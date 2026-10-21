"""Prospective source-only long/complex selection; never a final cohort seal.

Only frozen queue/rules, source screening inventories, retained source and source
reviews are read. No method output, DOE reference, human approval or performance
input is accepted. All diagnostic and report prose is English.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import random
import re

from . import selection as old
from .protocol import canonical_hash, sha256, write_json

SCHEMA = "skillflow-prospective-long-selection-v2"
CODE_SUFFIXES = {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".sh", ".ps1", ".go", ".rs", ".rb", ".sql"}


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _inside(root, value):
    if not isinstance(value, str) or "\\" in value:
        raise ValueError("Source evidence requires an exact portable relative path")
    path = old._inside(Path(root), value)
    if path.is_symlink():
        raise ValueError("Source evidence must not follow a symlink")
    return path


def _frozen_inputs(proposal_dir, corpus_root):
    proposal, corpus = Path(proposal_dir).resolve(), Path(corpus_root).resolve()
    freeze = read(proposal / "rules-freeze.json")
    for relative, expected in freeze["files"].items():
        if sha256(_inside(proposal, relative)) != expected:
            raise ValueError("A frozen prospective rule or queue file changed: " + relative)
    rules, queue = read(proposal / "rules.json"), read(proposal / "candidate-queue.json")
    bound = []
    for item in rules["evidence_inputs"]:
        path = Path(item["path"]).resolve()
        if not path.is_relative_to(corpus) or sha256(path) != item["sha256"]:
            raise ValueError("A frozen source-only evidence input changed or escaped its corpus")
        bound.append({"path": str(path), "sha256": item["sha256"]})
    screening_paths = [Path(i["path"]) for i in bound if Path(i["path"]).name == "screening-report.json"]
    if len(screening_paths) != 1:
        raise ValueError("Exactly one frozen source-screening report must be bound")
    screening = read(screening_paths[0])
    rows = {r["canonical_id"]: r for r in screening["entries"]}
    gate = rules["candidate_gate"]
    eligible = sorted((r for r in rows.values() if r.get("eligible") is True
        and gate["minimum_reference_tokens_inclusive"] <= r["reference_tokens"] <= gate["maximum_reference_tokens_inclusive"]
        and r["bundle_bytes"] <= gate["maximum_numbered_bundle_bytes_inclusive"]), key=lambda r: r["canonical_id"])
    random.Random(rules["seed"]).shuffle(eligible)
    candidates = queue["candidates"]
    if (len(candidates) != queue["candidate_count"] or len(candidates) != len(eligible)
            or [c["canonical_id"] for c in candidates] != [r["canonical_id"] for r in eligible]
            or [c["queue_index"] for c in candidates] != list(range(1, len(candidates) + 1))):
        raise ValueError("The frozen candidate queue differs from the preregistered source-only length-gate order")
    identities = ("version", "rank", "source_dir", "source_view_path", "source_sha256", "source_tree_sha256",
                  "bundle_sha256", "reference_tokens", "bundle_bytes", "source_cluster", "near_fork_group")
    for candidate in candidates:
        original = rows[candidate["canonical_id"]]
        if any(candidate.get(key) != original.get(key) for key in identities):
            raise ValueError("A frozen queue identity differs from the frozen screening report: " + candidate["canonical_id"])
        path = _inside(corpus, candidate["source_dir"])
        if candidate.get("source_dir_absolute") and path.resolve() != Path(candidate["source_dir_absolute"]).resolve():
            raise ValueError("The frozen absolute and relative source identities differ")
    return proposal, corpus, rules, candidates, bound


def _review_batches(proposal):
    batches = {}
    for path in sorted((proposal / "reviews").glob("*.json")):
        document = read(path)
        records = document if isinstance(document, list) else document.get("reviews")
        if not isinstance(records, list):
            raise ValueError("A review batch must be a list or contain a reviews list: " + path.name)
        batches[path.name] = {"path": path, "sha256": sha256(path), "document": document, "records": records}
    supersessions, declarations = [], []
    for name, batch in batches.items():
        document = batch["document"]
        if not isinstance(document, dict):
            continue
        prior = document.get("recounts_prior_review") or document.get("supersedes")
        if prior:
            expected = document.get("recounts_prior_review_sha256") or document.get("supersedes_sha256")
            if isinstance(prior, dict):
                expected, prior = prior.get("sha256"), prior.get("path")
            declaration = {"superseded_path": prior, "superseded_sha256": expected,
                "replacement_path": name, "replacement_sha256": batch["sha256"]}
            declarations.append(declaration)
            if expected is not None:
                supersessions.append(declaration)
    manifest = proposal / "review-supersessions.json"
    if manifest.exists():
        document = read(manifest)
        if (document.get("rules_sha256") != sha256(proposal / "rules.json")
                or document.get("candidate_queue_sha256") != sha256(proposal / "candidate-queue.json")):
            raise ValueError("The review supersession manifest is bound to different frozen rules or queue")
        for item in document.get("records", document.get("supersessions", [])):
            supersessions.append({"superseded_path": item.get("superseded_path", item.get("predecessor_path")),
                "superseded_sha256": item.get("superseded_sha256", item.get("predecessor_sha256")),
                "replacement_path": item["replacement_path"], "replacement_sha256": item["replacement_sha256"]})
    for declaration in declarations:
        if not any(Path(s["superseded_path"]).name == Path(declaration["superseded_path"]).name
                and Path(s["replacement_path"]).name == Path(declaration["replacement_path"]).name for s in supersessions):
            raise ValueError("Review supersession requires exact predecessor and replacement hashes")
    successors = {}
    for item in supersessions:
        for value in (item["superseded_path"], item["replacement_path"]):
            if not isinstance(value, str) or value not in {Path(value).name, "reviews/" + Path(value).name}:
                raise ValueError("A review supersession path escapes the review directory")
        before, after = Path(item["superseded_path"]).name, Path(item["replacement_path"]).name
        if before not in batches or after not in batches or before == after:
            raise ValueError("A declared review supersession lacks its exact predecessor/replacement")
        if (item.get("superseded_sha256") != batches[before]["sha256"]
                or item.get("replacement_sha256") != batches[after]["sha256"]):
            raise ValueError("Review supersession requires exact predecessor and replacement hashes")
        if before in successors and successors[before] != after:
            raise ValueError("A review batch has competing superseding versions")
        successors[before] = after
    for name in successors:
        seen, cursor = set(), name
        while cursor in successors:
            if cursor in seen:
                raise ValueError("Review supersession contains a cycle")
            seen.add(cursor)
            cursor = successors[cursor]
    by_index = {}
    for name, batch in batches.items():
        present = set()
        for record in batch["records"]:
            index = record.get("queue_index")
            if type(index) is not int or index in present:
                raise ValueError("A review batch has a missing or duplicate queue identity")
            present.add(index)
            by_index.setdefault(index, []).append((name, record))
    effective, histories = {}, {}
    for index, versions in by_index.items():
        names = {name for name, _ in versions}
        active = []
        for name, record in versions:
            cursor, replaced = name, False
            while cursor in successors:
                cursor = successors[cursor]
                if cursor in names:
                    replaced = True
            if not replaced:
                active.append((name, record))
        if len(active) != 1:
            raise ValueError("Contradictory review records lack explicit hash-bound supersession at queue index " + str(index))
        effective[index] = active[0]
        histories[index] = [{"path": "reviews/" + name, "sha256": batches[name]["sha256"],
                             "effective": name == active[0][0]} for name, _ in versions]
    return batches, effective, histories


def _nested_quotes(value, texts, location="review"):
    count = 0
    if isinstance(value, dict):
        if "quote" in value:
            if not {"path", "start_line", "end_line", "quote"} <= value.keys():
                raise ValueError("A nested source quote lacks its exact source coordinates: " + location)
            if (not isinstance(value["path"], str) or "\\" in value["path"]
                    or old._relative(value["path"]) != value["path"]
                    or type(value["start_line"]) is not int or type(value["end_line"]) is not int):
                raise ValueError("A nested source quote has noncanonical physical source coordinates")
            old.validate_evidence(texts, [value])
            count += 1
        for key, child in value.items():
            count += _nested_quotes(child, texts, location + "." + key)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            count += _nested_quotes(child, texts, location + "[" + str(index) + "]")
    return count


def conservative_lines(text, path):
    """Return physical nonblank own-code/content rows after mechanical exclusions.

    This does not establish that a source span is operative. Reviewers provide
    that semantic scope; this function rejects count inflation within the scope.
    Python docstrings are identified as actual first-body string expressions,
    preserving assigned or returned strings and output/value definitions.
    """
    lines = text.splitlines()
    suffix = PurePosixPath(path).suffix.casefold()
    excluded = {}
    docstrings = set()
    if suffix == ".py":
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.body:
                first = node.body[0]
                if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                    docstrings.update(range(first.lineno, first.end_lineno + 1))
    code = suffix in CODE_SUFFIXES
    block_comment, quote = False, None
    retained = []
    for number, line in enumerate(lines, 1):
        if number in docstrings:
            excluded[number] = "python_docstring"
            continue
        if not line.strip():
            excluded[number] = "blank"
            continue
        if not code:
            stripped = line.strip()
            if (re.fullmatch(r"[#]+\s.*|`{3,}.*|~{3,}.*", stripped)
                    or re.fullmatch(r"[\s|:+*_=\-]+", stripped)):
                excluded[number] = "formatting"
            elif stripped.startswith("<!--") and stripped.endswith("-->"):
                excluded[number] = "standalone_comment"
            else:
                retained.append(number)
            continue
        visible, cursor = [], 0
        while cursor < len(line):
            if block_comment:
                close = line.find("*/", cursor)
                if close < 0:
                    break
                block_comment, cursor = False, close + 2
                continue
            ch = line[cursor]
            if quote:
                visible.append(ch)
                if ch == "\\" and cursor + 1 < len(line):
                    visible.append(line[cursor + 1]); cursor += 2; continue
                if line.startswith(quote, cursor):
                    visible.extend(line[cursor + 1:cursor + len(quote)])
                    cursor += len(quote); quote = None; continue
                cursor += 1
                continue
            if suffix == ".py" and ch == "#":
                break
            if suffix in {".sh", ".ps1", ".rb"} and ch == "#":
                break
            if suffix not in {".py", ".sh", ".ps1", ".rb"} and line.startswith("//", cursor):
                break
            if suffix not in {".py", ".sh", ".ps1", ".rb"} and line.startswith("/*", cursor):
                block_comment, cursor = True, cursor + 2
                continue
            if ch in "\"'`":
                quote = ch * 3 if suffix == ".py" and line.startswith(ch * 3, cursor) else ch
                visible.extend(quote); cursor += len(quote); continue
            visible.append(ch); cursor += 1
        content = "".join(visible).strip()
        if not content:
            excluded[number] = "standalone_comment"
        elif re.fullmatch(r"[\s()\[\]{},;:.\\'\"`]+", content):
            excluded[number] = "syntax_only_punctuation"
        else:
            retained.append(number)
        # Single quotes and double quotes cannot span ordinary JS/Python lines.
        if quote in {"'", '"'}:
            quote = None
    return set(retained), excluded


def _span_numbers(span, lines):
    start, end = span.get("start_line"), span.get("end_line")
    if type(start) is not int or type(end) is not int or not 1 <= start <= end <= len(lines):
        raise ValueError("An operative proof span has invalid physical line bounds")
    return set(range(start, end + 1))


def _count_proof(basis, texts):
    spans, total, normalized, discrepancies = basis.get("counted_spans", []), set(), [], []
    for span in spans:
        path = old._relative(span["path"])
        if path != span["path"] or "\\" in span["path"]:
            raise ValueError("A counted proof requires an exact portable physical source path")
        if path not in texts:
            raise ValueError("A counted proof refers to excluded or absent source")
        text = texts[path]
        numbers = _span_numbers(span, text.splitlines())
        allowed, excluded = conservative_lines(text, path)
        explicit = span.get("counted_physical_line_numbers")
        if explicit is not None:
            if (not isinstance(explicit, list) or any(type(n) is not int for n in explicit)
                    or len(set(explicit)) != len(explicit) or not set(explicit) <= numbers):
                raise ValueError("Explicit counted physical line identities are invalid or duplicate")
            nominated = set(explicit)
        else:
            if "excluded_all_blank_lines" not in span:
                raise ValueError("An implicit operative count lacks explicit exclusion policy")
            nominated = {n for n in numbers if text.splitlines()[n - 1].strip()}
            for excluded_span in span.get("excluded_docstring_spans", []):
                nominated -= _span_numbers(excluded_span, text.splitlines())
            nominated -= set(span.get("excluded_comment_line_numbers", []))
            for n in span.get("excluded_comment_line_numbers", []):
                if n not in numbers or excluded.get(n) != "standalone_comment":
                    raise ValueError("A declared comment exclusion does not identify a standalone comment")
        valid = nominated & allowed
        rejected = [{"line": n, "reason": excluded.get(n, "outside_scope")} for n in sorted(nominated - allowed)]
        stated = span.get("operative_nonempty_lines")
        if type(stated) is not int or stated != len(valid) or (explicit is not None and rejected):
            discrepancies.append({"path": path, "span": [span["start_line"], span["end_line"]],
                "declared": stated, "mechanically_confirmed": len(valid), "rejected_nominated_lines": rejected,
                "action": "The source author must explicitly correct or supersede the proof; the selector does not rewrite eligibility."})
        identities = {(path, n) for n in valid}
        if identities & total:
            raise ValueError("Operative line proof double-counts overlapping physical lines")
        total |= identities
        normalized.append({"path": path, "start_line": span["start_line"], "end_line": span["end_line"],
            "operative_nonempty_lines": len(valid), "counted_physical_line_numbers": sorted(valid)})
    stated_total = basis.get("nonempty_lines", basis.get("operative_nonempty_lines"))
    if spans and stated_total != len(total):
        discrepancies.append({"declared_total": stated_total, "mechanically_confirmed_total": len(total),
            "action": "Require explicit source-review correction; no silent eligibility change."})
    return {"confirmed_operative_nonempty_lines": len(total), "counted_spans": normalized,
            "count_discrepancies": discrepancies, "threshold_met": bool(spans) and len(total) >= 600 and not discrepancies}


def _edge_target_supported(source, target, evidence, actual_paths=()):
    parent = PurePosixPath(source).parent
    literals = []
    for item in evidence:
        if item["path"] != source:
            return False
        quote = item["quote"]
        if target in quote:
            return True
        basename = PurePosixPath(target).name
        if basename in quote and sum(PurePosixPath(p).name == basename for p in actual_paths) == 1:
            return True
        if (target == str(parent / "package.json") and isinstance(actual_paths, dict)
                and target in actual_paths):
            # A bare command can only connect a co-located manifest. Its script
            # name does not establish identity for another package in the bundle.
            commands = [match[1] for line in quote.splitlines()
                        if (match := re.fullmatch(r"\s*npm\s+run\s+([A-Za-z0-9:_.-]+)\s*", line))]
            try:
                scripts = json.loads(actual_paths[target]).get("scripts", {})
            except (ValueError, AttributeError):
                scripts = {}
            if (commands and isinstance(scripts, dict)
                    and all(isinstance(scripts.get(command), str) and scripts[command].strip()
                            for command in commands)):
                return True
        for literal in re.findall(r"[\w./<>*{}-]+\.(?:md|py|tsx?|m?js|ya?ml|json|sh)", quote):
            literals.append(literal)
        module = str(PurePosixPath(target).with_suffix("")).replace("/", ".")
        if re.search(r"\b(?:from|import)\s+[.\w]*" + re.escape(module.rsplit(".", 1)[-1]) + r"\b", quote):
            return True
    for literal in literals:
        for candidate in (literal, str(parent / literal)):
            normalized = str(PurePosixPath(candidate)).removeprefix("./")
            normalized = re.sub(r"\.js$", ".ts", normalized) if target.endswith(".ts") else normalized
            pattern = re.escape(normalized)
            pattern = re.sub(r"<[^>]+>|\\\{[^}]+\\\}", "[^/]+", pattern).replace(r"\*", "[^/]*")
            if re.fullmatch(pattern, target):
                return True
    return False


def _file_proof(basis, inventory):
    paths = basis.get("operative_files", [])
    if not paths:
        return {"connected_operative_files": [], "reference_edges": [], "threshold_met": False}
    if len(paths) != len(set(paths)) or "SKILL.md" not in inventory["texts"]:
        raise ValueError("An eight-file proof needs an actual entry and unique operative files")
    kinds = {f["path"]: f["kind"] for f in inventory["files"]}
    for path in paths:
        old._relative(path)
        if (path not in inventory["texts"] or kinds[path] == "non_operational_support"
                or PurePosixPath(path).name in {"package.json", "pyproject.toml", "Cargo.toml"}):
            raise ValueError("The operative file proof includes missing, metadata, test or support-only source")
        if kinds[path] == "text_asset":
            content_proof = any(e.get("path") == path for e in basis.get("operative_content_evidence", []))
            if not content_proof:
                raise ValueError("A named text asset lacks explicit operative input/output-template content evidence")
    edges = []
    for edge in basis.get("local_reference_edges", basis.get("reference_edges", [])):
        source, target = edge.get("source", edge.get("path")), edge.get("target")
        evidence = edge.get("evidence", [edge] if "quote" in edge else [])
        if (source not in inventory["texts"] or target not in inventory["texts"] or not evidence
                or not _edge_target_supported(source, target, evidence, inventory["texts"])):
            raise ValueError("A claimed operative file connection lacks a source-supported local target")
        edges.append({"source": source, "target": target, "evidence": evidence})
    reached = {"SKILL.md"}
    while True:
        expanded = reached | {e["target"] for e in edges if e["source"] in reached}
        if expanded == reached:
            break
        reached = expanded
    declared = basis.get("count", basis.get("confirmed_file_count"))
    if declared != len(paths) or not set(paths) <= reached:
        raise ValueError("The eight-file proof has a wrong count or disconnected operative members")
    return {"root": "SKILL.md", "connected_operative_files": sorted(paths),
            "supporting_connectors_without_operative_credit": sorted(reached - set(paths)),
            "reference_edges": edges, "threshold_met": len(paths) >= 8}


def _inventory(corpus, candidate):
    source = _inside(corpus, candidate["source_dir"])
    source_view = read(_inside(corpus, candidate["source_view_path"]))
    inventory = old.source_inventory(source, source_view)
    if any(f["kind"] == "unresolved_source_provenance" for f in inventory["files"]):
        raise ValueError("Source provenance remains unresolved; metadata cannot be silently excluded")
    bundle = old.render_numbered_bundle(inventory["texts"], inventory["files"])
    if (inventory["source_tree_sha256"] != candidate["source_tree_sha256"]
            or old.native_source_sha256(inventory["texts"]) != candidate["source_sha256"]
            or hashlib.sha256(bundle.encode("utf-8")).hexdigest() != candidate["bundle_sha256"]
            or len(bundle.encode("utf-8")) != candidate["bundle_bytes"]):
        raise ValueError("Retained source bytes, tree, decoded source or complete numbered bundle changed")
    if len(old.reference_tokenizer()[0].encode(bundle, disallowed_special=())) != candidate["reference_tokens"]:
        raise ValueError("The complete retained source bundle reference token count changed")
    return inventory


def _validate_record(candidate, record, inventory, rules_sha256):
    if record.get("canonical_id") != candidate["canonical_id"]:
        raise ValueError("The source review canonical identity differs from its queue index")
    for key in ("version", "rank", "source_sha256", "source_tree_sha256", "reference_tokens", "bundle_bytes"):
        if key in record and record[key] != candidate[key]:
            raise ValueError("The source review identity differs: " + key)
    if record.get("rules_sha256", rules_sha256) != rules_sha256:
        raise ValueError("The source review is bound to different prospective rules")
    if record.get("decision") not in {"include", "exclude", "reject", "unresolved"} or not record.get("reason"):
        raise ValueError("A completed source review requires include/exclude/unresolved and a reason")
    texts = inventory["texts"]
    quote_count = _nested_quotes(record, texts)
    members = {f["path"]: f for f in inventory["files"]}
    for file in record.get("reviewed_files", []):
        path = file["path"]
        old._relative(path)
        if path not in members or file.get("sha256") != members[path]["sha256"]:
            raise ValueError("A reviewed physical source file hash differs or is missing: " + path)
    if not record.get("reviewed_files"):
        raise ValueError("A completed source review must bind its reviewed physical files")
    return quote_count


def validate_reviews(proposal_dir, corpus_root, *, write=True):
    proposal, corpus, rules, candidates, inputs = _frozen_inputs(proposal_dir, corpus_root)
    batches, effective, histories = _review_batches(proposal)
    normalized, errors = [], []
    indexed = {c["queue_index"]: c for c in candidates}
    for index in sorted(effective):
        candidate = indexed.get(index)
        if candidate is None:
            raise ValueError("A review contains an identity outside the frozen candidate queue")
        batch_name, record = effective[index]
        row = {"queue_index": index, "canonical_id": candidate["canonical_id"],
            "review_decision": record.get("decision"), "effective_review_file": "reviews/" + batch_name,
            "normalized_decision": "exclude" if record.get("decision") == "reject" else record.get("decision"),
            "review_versions": histories[index], "errors": [], "count_discrepancies": [], "eligible": False}
        try:
            inventory = _inventory(corpus, candidate)
            # Every archived version's quotes and identity remain auditable.
            quote_count = 0
            for name, batch in batches.items():
                for version in batch["records"]:
                    if version["queue_index"] == index:
                        quote_count += _validate_record(candidate, version, inventory, sha256(proposal / "rules.json"))
            for name, batch in batches.items():
                document = batch["document"]
                if isinstance(document, dict) and any(r["queue_index"] == index for r in batch["records"]):
                    if document.get("rules_sha256", sha256(proposal / "rules.json")) != sha256(proposal / "rules.json"):
                        raise ValueError("A source-review batch is bound to different prospective rules")
            basis = record.get("complexity_basis", record.get("basis", {}))
            member_kinds = {f["path"]: f["kind"] for f in inventory["files"]}
            for span in basis.get("counted_spans", []):
                path = span.get("path", "")
                if (member_kinds.get(path) == "non_operational_support"
                        or any(part.casefold() in {"vendor", "node_modules", "site-packages", ".venv", "third_party"}
                               for part in PurePosixPath(path).parts)):
                    raise ValueError("An operative line proof counts support, tests or dependency/vendor source")
            feature_names = []
            for feature in record.get("features", []):
                if feature.get("feature") not in rules["feature_criterion"]["allowed_features"] or not feature.get("reason") or not feature.get("evidence"):
                    raise ValueError("A source-confirmed feature lacks an allowed identity, reason or exact evidence")
                feature_names.append(feature["feature"])
            if len(feature_names) != len(set(feature_names)):
                raise ValueError("A review repeats one feature as distinct source complexity")
            count = _count_proof(basis, inventory["texts"])
            files = _file_proof(basis, inventory)
            row.update(quote_count=quote_count, confirmed_features=sorted(feature_names), line_proof=count, file_proof=files,
                source_files=inventory["files"], review_reason=record["reason"],
                count_discrepancies=count["count_discrepancies"], source_review_proof=record)
            if count["count_discrepancies"]:
                raise ValueError("Operative physical-line count differs from the declared source proof; explicit author correction is required")
            if record["decision"] == "include":
                if record.get("source_closure", {}).get("status") not in {"complete_for_static_audit", "complete_for_static_source_audit"}:
                    raise ValueError("An included source review lacks complete static source closure")
                if len(feature_names) < rules["feature_criterion"]["minimum_source_confirmed_distinct_features"]:
                    raise ValueError("An included review has fewer than three distinct source-confirmed features")
                if not count["threshold_met"] and not files["threshold_met"]:
                    raise ValueError("The new positive 600-line or connected-eight-file operative proof is missing")
                row["eligible"] = True
        except (ValueError, KeyError, SyntaxError, OSError) as error:
            row["errors"].append(f"{type(error).__name__}: {error}")
            errors.append({"queue_index": index, "canonical_id": candidate["canonical_id"], "errors": row["errors"],
                           "count_discrepancies": row["count_discrepancies"]})
        normalized.append(row)
    result = {"schema": SCHEMA, "status": "needs_review_correction" if errors else "validated_available_reviews",
        "rules_sha256": sha256(proposal / "rules.json"), "candidate_queue_sha256": sha256(proposal / "candidate-queue.json"),
        "frozen_source_inputs": inputs, "review_batches": [{"path": "reviews/" + n, "sha256": b["sha256"]} for n, b in batches.items()],
        "review_supersessions_sha256": sha256(proposal / "review-supersessions.json") if (proposal / "review-supersessions.json").exists() else None,
        "candidate_count": len(candidates), "completed_review_count": len(normalized), "reviews": normalized, "errors": errors,
        "scope": "Source-only engineering validation; quote/hash/count checks are not independent semantic adjudication.",
        "formal_target_calls": 0, "human_reference_confirmations_created": 0, "final_seal": False}
    if write:
        write_json(proposal / "output/validation-assessments" / (canonical_hash(result) + ".json"), result, immutable=True)
        write_json(proposal / "output/review-validation.json", result)
    return result


def select_long_cases(proposal_dir, corpus_root, *, write=True):
    proposal, _, rules, candidates, inputs = _frozen_inputs(proposal_dir, corpus_root)
    validation = validate_reviews(proposal_dir, corpus_root, write=write)
    reviews = {r["queue_index"]: r for r in validation["reviews"]}
    plan = rules["selection_plan"]
    accepted, decisions, forks, clusters = [], [], Counter(), Counter()
    needed = plan["requested_cases"] + plan["requested_reserves"]
    status, blocked_index = "insufficient_eligible_candidates", None
    for candidate in candidates:
        index = candidate["queue_index"]
        if len(accepted) >= needed:
            status = "selection_complete_pending_human_reference"
            break
        if index not in reviews:
            status, blocked_index = "needs_more_review", index
            break
        review = reviews[index]
        if review["errors"]:
            status, blocked_index = "needs_review_correction", index
            decisions.append({"queue_index": index, "canonical_id": candidate["canonical_id"],
                              "decision": "review_correction_required", "errors": review["errors"]})
            break
        reason = review["normalized_decision"]
        if not review["eligible"]:
            decisions.append({"queue_index": index, "canonical_id": candidate["canonical_id"], "decision": reason,
                              "reason": review["review_reason"]})
            continue
        if forks[candidate["near_fork_group"]] >= plan["max_per_near_fork_group"]:
            reason = "near_fork_group_cap"
        elif clusters[candidate["source_cluster"]] >= plan["max_per_source_cluster"]:
            reason = "source_cluster_cap"
        else:
            reason = "accepted"
            forks[candidate["near_fork_group"]] += 1
            clusters[candidate["source_cluster"]] += 1
            accepted.append({**candidate, "source_review_file": review["effective_review_file"],
                "source_review_versions": review["review_versions"], "source_files": review["source_files"],
                "stronger_source_proof": {"features": review["confirmed_features"], "line_proof": review["line_proof"],
                    "file_proof": review["file_proof"], "review_reason": review["review_reason"]}})
        decisions.append({"queue_index": index, "canonical_id": candidate["canonical_id"], "decision": reason})
    if len(accepted) == needed:
        status = "selection_complete_pending_human_reference"
    selected, reserves = accepted[:plan["requested_cases"]], accepted[plan["requested_cases"]:]
    selected_cluster_count = len({r["source_cluster"] for r in selected})
    if len(accepted) == needed and selected_cluster_count < plan["minimum_selected_source_clusters"]:
        status = "insufficient_selected_source_clusters"
    result = {"schema": SCHEMA, "status": status, "final_seal": False, "root_audit_required": True,
        "selection_state": "proposed_pending_root_audit", "human_reference_status": "pending_two_actual_humans_per_case_and_reserve",
        "rules_sha256": validation["rules_sha256"], "candidate_queue_sha256": validation["candidate_queue_sha256"],
        "review_validation_sha256": canonical_hash(validation), "frozen_source_inputs": inputs,
        "selected": selected, "reserves": reserves, "accepted_count": len(accepted),
        "required_count": needed, "shortfall": max(0, needed - len(accepted)),
        "selected_source_clusters": selected_cluster_count, "prefix_decisions": decisions,
        "last_consumed_queue_index": decisions[-1]["queue_index"] if decisions else 0,
        "first_blocked_queue_index": blocked_index, "available_review_count": validation["completed_review_count"],
        "group_caps_scope": "Selected plus reserves together", "thresholds_relaxed": False,
        "order_reshuffled": False, "source_bytes_modified": False, "formal_target_calls": 0,
        "interpretation": "A prospective source-only proposal. Unresolved source gates are not failures proved by an old lower-bound count. Source reviews and this selection are not human DOE references or performance evidence."}
    if write:
        write_json(proposal / "output/selection-proposals" / (canonical_hash(result) + ".json"), result, immutable=True)
        write_json(proposal / "output/selection-proposal.json", result)
        lines = ["# Prospective long/complex source selection", "", "Status: `" + status + "`.", "",
            f"Accepted {len(accepted)} of {needed}: {len(selected)} selected and {len(reserves)} reserves. Selected source clusters: {selected_cluster_count}.", "",
            "The frozen queue is consumed in order. Group caps apply to selected and reserve candidates together. No threshold was relaxed, no source was changed, and no formal target request or human confirmation was created.", "",
            "Root audit is required. No final cohort seal has been written.", "", "| Role | Queue | Source | Version | Reference tokens |", "|---|---:|---|---|---:|"]
        for role, records in (("Selected", selected), ("Reserve", reserves)):
            lines.extend(f"| {role} | {r['queue_index']} | {r['canonical_id']} | {r['version']} | {r['reference_tokens']} |" for r in records)
        if blocked_index:
            lines.extend(["", f"The prefix stops at queue index {blocked_index}; later reviewed candidates are not silently substituted."])
        (proposal / "output/selection-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "select"))
    parser.add_argument("--proposal-dir", required=True)
    parser.add_argument("--corpus-root", required=True)
    args = parser.parse_args(argv)
    result = (validate_reviews if args.command == "validate" else select_long_cases)(args.proposal_dir, args.corpus_root)
    print(json.dumps({key: value for key, value in result.items() if key not in {"reviews", "selected", "reserves", "prefix_decisions"}}, ensure_ascii=True))


if __name__ == "__main__":
    main()
