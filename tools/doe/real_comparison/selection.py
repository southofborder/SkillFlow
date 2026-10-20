"""Source-only screening, deterministic selection and pending human references.

No skill is executed. Machine evidence nominations never establish semantic
eligibility. Source reviewers must confirm features with exact source citations;
two real humans must separately confirm the reference before target trials.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path, PurePosixPath
import random
import re
from functools import lru_cache
from typing import Any, Iterable
import uuid
from urllib.parse import urlsplit

SCHEMA = "skillflow-real-comparison-selection-v1"
SEED = 20261020
MAX_BUNDLE_BYTES = 256 * 1024
MAX_REFERENCE_TOKENS = 64000
TOKENIZER_VERSION = "0.12.0"
FEATURES = (
    "cross_file_dataflow", "conditions_or_retries", "versions_or_transformations",
    "element_or_recipient_pairing", "multiple_receiving_boundaries", "persistence_or_cross_session",
)
FEATURE_PATTERNS = {
    "cross_file_dataflow": r"(?:scripts|references|config)/[^\s`<>]+|\b(?:import|require\(|source\s)\b",
    "conditions_or_retries": r"\b(?:if|unless|retry|retries|fallback|otherwise|when|elif)\b",
    "versions_or_transformations": r"\b(?:redact|sanitize|transform|convert|filter|extract|parse|summari[sz]|encrypt|mask|normalize)\w*\b",
    "element_or_recipient_pairing": r"\b(?:for each|per[- ](?:item|record|recipient|user)|recipients?|iterate|loop)\b",
    "multiple_receiving_boundaries": r"\b(?:https?://|upload|post|send|publish|webhook|api|email|write|store|save)\b",
    "persistence_or_cross_session": r"\b(?:persist|memory|database|cache|write|save|session|sqlite|storage)\w*\b",
}
TEXT_SUFFIXES = {
    ".md", ".txt", ".rst", ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx",
    ".json", ".jsonl", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".sh",
    ".ps1", ".bat", ".cmd", ".rb", ".go", ".rs", ".sql", ".xml", ".html", ".css",
    ".csv", ".tsv", ".env", ".example", ".curl", ".graphql", ".proto", ".r",
}
NON_OPERATIONAL_NAMES = {
    "license", "license.txt", "license.md", "licence", "licence.txt", "copying", "notice",
    "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "uv.lock", "poetry.lock",
    "changelog.md", "history.md", "contributing.md", "code_of_conduct.md",
}
REGISTRY_METADATA_NAMES = {".clawhub/origin.json"}


def normalize_repository(value: str) -> str | None:
    """Normalize explicitly declared repository identities, never arbitrary links."""
    if not isinstance(value, str) or not value.strip() or re.search(r"\s", value):
        return None
    value = value.strip().removeprefix("git+")
    if value.startswith("github:"):
        value = "https://github.com/" + value[7:]
    if re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?", value):
        value = "https://github.com/" + value
    ssh = re.fullmatch(r"(?:[^/@:]+@)?([^/:]+):([^?#]+)", value)
    if ssh and "://" not in value:
        value = "https://" + ssh[1] + "/" + ssh[2]
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https", "ssh", "git"} or not parsed.hostname:
        return None
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) < 2 or any(part in {".", ".."} for part in parts):
        return None
    if parsed.hostname.casefold() in {"github.com", "bitbucket.org"}:
        parts = parts[:2]
    path = "/".join(parts).casefold().removesuffix(".git")
    return parsed.hostname.casefold() + "/" + path


def repository_origins(texts: dict[str, str], record: dict, review: dict | None = None) -> list[dict]:
    """Collect source-evidenced upstreams from own root metadata and reviewed facts."""
    origins = []
    for field in ("repo", "repository", "source_repository"):
        raw = record.get(field)
        repository = normalize_repository(raw)
        if repository:
            origins.append({"repository": repository, "basis": "official_acquisition_descriptor",
                            "field": field, "declared_value": raw})
    # Only explicit fields inside the root entry's frontmatter qualify here.
    # Body links, deep documentation URLs and arbitrary dependency links do not.
    entry_lines = texts.get("SKILL.md", "").splitlines()
    if entry_lines and entry_lines[0].strip() == "---":
        closing = next((i for i in range(1, len(entry_lines)) if entry_lines[i].strip() in {"---", "..."}), None)
        if closing is not None:
            declarations = []
            for i, line in enumerate(entry_lines[1:closing], 2):
                match = re.fullmatch(r"(repository|source|homepage)\s*:\s*(.+?)\s*", line)
                if match:
                    value = match[2].strip()
                    if len(value) > 1 and value[0] == value[-1] and value[0] in {"'", '"'}:
                        value = value[1:-1]
                    declarations.append((match[1], value, i, line))
                metadata = re.fullmatch(r"metadata\s*:\s*(\{.*\})\s*", line)
                if metadata:
                    try:
                        value = json.loads(metadata[1])
                    except ValueError:
                        continue
                    def walk_fields(item: Any, prefix: str) -> None:
                        if not isinstance(item, dict):
                            return
                        for key, val in item.items():
                            field = prefix + "." + key
                            if key in {"repository", "source", "homepage"} and isinstance(val, str):
                                declarations.append((field, val, i, line))
                            elif isinstance(val, dict):
                                walk_fields(val, field)
                    walk_fields(value, "metadata")
            for field, value, i, line in declarations:
                candidate = value.removeprefix("git+")
                if candidate.startswith("github:"):
                    candidate = "https://github.com/" + candidate[7:]
                if re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?(?:#readme)?", candidate, re.I):
                    candidate = "https://github.com/" + candidate
                parsed = urlsplit(candidate)
                parts = [part for part in parsed.path.strip("/").split("/") if part]
                if (parsed.hostname or "").casefold() != "github.com" or len(parts) != 2 or parsed.query or parsed.fragment.casefold() not in {"", "readme"}:
                    continue
                repository = normalize_repository(candidate)
                if repository:
                    origins.append({"repository": repository, "basis": "author_declared_root_frontmatter",
                                    "field": field, "declared_value": value,
                                    "evidence": [{"path": "SKILL.md", "start_line": i, "end_line": i, "quote": line}]})
    for path, field_path in (("package.json", ("repository",)),
                             ("distribution-manifest.json", ("source", "repository"))):
        if path not in texts:
            continue
        try:
            value = json.loads(texts[path])
            for key in field_path:
                value = value[key]
            if path == "package.json" and isinstance(value, dict):
                value = value.get("url")
        except (ValueError, KeyError, TypeError):
            continue
        repository = normalize_repository(value)
        if not repository:
            continue
        encoded = json.dumps(value, ensure_ascii=False)[1:-1]
        evidence = [{"path": path, "start_line": i, "end_line": i, "quote": line}
                    for i, line in enumerate(texts[path].splitlines(), 1) if encoded in line or value in line]
        if not evidence:
            continue
        origins.append({"repository": repository, "basis": "explicit_own_root_metadata",
                        "field": ".".join(field_path) + (".url" if path == "package.json" and isinstance(json.loads(texts[path]).get("repository"), dict) else ""),
                        "declared_value": value, "evidence": evidence[:1]})
    for origin in (review or {}).get("upstream_repositories", []):
        repository = normalize_repository(origin.get("repository"))
        if not repository or not origin.get("reason"):
            raise ValueError("Reviewed upstream repositories require an explicit repository and source-based reason")
        validate_evidence(texts, origin.get("evidence", []))
        origins.append({"repository": repository, "basis": "explicit_source_review",
                        "declared_value": origin["repository"], "reason": origin["reason"], "evidence": origin["evidence"]})
    return sorted(origins, key=lambda origin: (origin["repository"], origin["basis"], origin.get("field", "")))


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json(data: Any) -> bytes:
    return (json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    temporary.write_bytes(_json(data))
    os.replace(temporary, path)


def _immutable(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f"Frozen artifact differs: {path}")
        return
    with path.open("xb") as stream:
        stream.write(data)


def _relative(value: str) -> str:
    value = value.replace("\\", "/")
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or ":" in value or any(p in {"", ".", ".."} for p in path.parts):
        raise ValueError("Source path must be a safe relative path")
    return path.as_posix()


def _inside(root: Path, relative: str) -> Path:
    path = root.joinpath(*PurePosixPath(_relative(relative)).parts)
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Source path escapes the package")
    return path


def canonical_identity(owner: str, slug: str) -> str:
    if any(not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", s) for s in (owner, slug)):
        raise ValueError("Invalid owner or slug")
    return f"{owner.casefold()}/{slug.casefold()}"


@lru_cache(maxsize=1)
def reference_tokenizer() -> tuple[Any, dict]:
    """Pin the reference tokenizer; it is not the target model tokenizer."""
    import tiktoken
    actual = importlib.metadata.version("tiktoken")
    if actual != TOKENIZER_VERSION:
        raise ValueError(f"Reference tokenizer must be tiktoken {TOKENIZER_VERSION}; found {actual}")
    encoding = tiktoken.get_encoding("o200k_base")
    rank_bytes = b"".join(len(k).to_bytes(4, "big") + k + v.to_bytes(4, "big")
                          for k, v in sorted(encoding._mergeable_ranks.items(), key=lambda row: row[1]))
    return encoding, {"library": "tiktoken", "version": actual, "encoding": "o200k_base",
                      "mergeable_ranks_sha256": _sha(rank_bytes), "is_target_tokenizer": False}


def classify_source(relative: str, raw: bytes) -> tuple[str, str | None]:
    """Preserve arbitrary UTF-8 source, including original language and quotes."""
    rel = _relative(relative)
    lower = rel.casefold()
    if lower in REGISTRY_METADATA_NAMES or lower.startswith(".clawhub/"):
        return "registry_generated_metadata", None
    if b"\x00" in raw:
        return "binary", None
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return "non_utf8_binary_or_text", None
    if lower in {"_meta.json", "_skillhub_meta.json"}:
        try:
            metadata = json.loads(text)
        except (ValueError, TypeError):
            metadata = None
        if (lower == "_meta.json" and isinstance(metadata, dict)
                and {"ownerId", "slug", "version", "publishedAt"} <= metadata.keys()):
            return "registry_generated_metadata", None
        if (isinstance(metadata, dict) and metadata.get("source") == "marketplace"
                and "installedAt" in metadata and "skillId" in metadata):
            return "registry_generated_metadata", None
    # Text assets remain visible, but never count toward operational complexity.
    name = PurePosixPath(lower).name
    suffix = PurePosixPath(lower).suffix
    if name in NON_OPERATIONAL_NAMES or name.startswith(("license.", "licence.")):
        return "non_operational_support", text
    if re.search(r"(?:^|/)(?:tests?|__tests__)/|(?:^|/)(?:test_[^/]+|[^/]+\.(?:test|spec)\.[^/]+)$", lower) or lower == "agents/openai.yaml":
        return "non_operational_support", text
    if suffix in {".svg", ".map"} or "assets" in PurePosixPath(lower).parts:
        return "text_asset", text
    if suffix in TEXT_SUFFIXES or not suffix or name.startswith(".env"):
        operational = suffix not in {".json", ".jsonl", ".csv", ".tsv", ".xml", ".css"}
        return "operational_text" if operational else "supporting_text", text
    return "other_utf8_text", text


def source_inventory(package_dir: Path | str, source_view: dict | None = None) -> dict:
    root = Path(package_dir)
    files, texts, operational = [], {}, {}
    view_by_path = {item["path"]: item for item in (source_view or {}).get("files", [])}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("Source inventory does not follow symbolic links")
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        raw = path.read_bytes()
        kind, text = classify_source(relative, raw)
        view = view_by_path.get(relative)
        if source_view is not None and view is None:
            raise ValueError(f"Source member is absent from the acquisition view: {relative}")
        if view and ((view.get("sha256") and view["sha256"] != _sha(raw)) or
                     (view.get("size") is not None and view["size"] != len(raw))):
            raise ValueError(f"Source member differs from the acquisition view: {relative}")
        if view and (not view.get("include_in_source", False) or view.get("provenance") != "source"):
            kind, text = "registry_generated_metadata" if view.get("provenance") == "registry_generated" else "unresolved_source_provenance", None
        entry = {"path": relative, "sha256": _sha(raw), "bytes": len(raw), "kind": kind,
                 "nonempty_lines": sum(bool(line.strip()) for line in text.splitlines()) if text is not None else None}
        if relative.casefold() == "_skillhub_meta.json" and kind == "registry_generated_metadata":
            metadata = json.loads(raw.decode("utf-8-sig"))
            entry["derived_view_exclusion"] = {
                "rule": "explicit_marketplace_installation_metadata",
                "reason": "The object declares installation metadata from another marketplace. Its installation state and teaching examples are outside the operational source view; original acquisition bytes and provenance remain unchanged.",
                "evidence": {key: metadata[key] for key in ("source", "installedAt", "skillId")},
                "original_file_sha256": _sha(raw),
            }
        files.append(entry)
        if text is not None:
            texts[relative] = text
            if kind == "operational_text":
                operational[relative] = text
    if source_view is not None and {file["path"] for file in files} != set(view_by_path):
        raise ValueError("Source member set differs from the acquisition view")
    for file in files:
        if file["path"].casefold() != "_meta.json" or file["kind"] != "registry_generated_metadata":
            continue
        view = view_by_path.get(file["path"], {})
        readers = sorted(path for path, text in operational.items() if "_meta.json" in text)
        if view.get("provenance") == "source" and view.get("include_in_source") and readers:
            raw = _inside(root, file["path"]).read_bytes()
            metadata = json.loads(raw.decode("utf-8-sig"))
            if set(metadata) == {"ownerId", "slug", "version", "publishedAt"}:
                text = raw.decode("utf-8-sig")
                texts[file["path"]] = text
                file.update(kind="supporting_text", nonempty_lines=sum(bool(line.strip()) for line in text.splitlines()),
                            derived_view_inclusion={"rule": "verified_original_metadata_is_operational_input",
                                                    "reason": "Own operational source references this verified publisher member; it contains only identity/version/time values, with no rating, scan verdict or generated summary.",
                                                    "referenced_by": readers})
            else:
                file.update(kind="unresolved_source_provenance", derived_view_exclusion={
                    "rule": "referenced_original_metadata_contains_extra_fields",
                    "reason": "A verified original metadata member is referenced by own source but mixes registry identity with additional fields. Required-source closure and interpretation provenance need explicit review before inclusion.",
                    "referenced_by": readers, "original_file_sha256": _sha(raw)})
    return {"files": files, "texts": texts, "operational": operational,
            "original_member_tree_sha256": _sha(_json([{k: f[k] for k in ("path", "sha256")} for f in files])),
            "source_tree_sha256": _sha(_json([{k: f[k] for k in ("path", "sha256")} for f in files
                                                if f["kind"] not in {"registry_generated_metadata", "unresolved_source_provenance"}]))}


def render_numbered_bundle(texts: dict[str, str], files: Iterable[dict] | None = None) -> str:
    """Number physical source lines without rewriting the original line content."""
    blocks = ["FILE " + path + "\n" + "\n".join(f"{i}: {line}" for i, line in enumerate(text.splitlines(), 1))
              for path, text in sorted(texts.items())]
    binaries = sorted((file for file in (files or []) if file["kind"] in {"binary", "non_utf8_binary_or_text"}), key=lambda file: file["path"])
    if binaries:
        blocks.append("BINARY SOURCE INVENTORY\n" + "\n".join(
            f"FILE {file['path']} | kind=binary | size={file['bytes']} bytes | [binary content omitted]" for file in binaries))
    return "\n\n".join(blocks) + "\n"


def native_source_sha256(texts: dict[str, str]) -> str:
    """Use the production decoded-source digest, distinct from raw/bundle hashes."""
    from skillflow.common.source_evidence import _digest
    return _digest([{"path": path, "sha256": _sha(text.encode("utf-8"))} for path, text in sorted(texts.items())])


def ranked_review_queue(screening: dict | Path | str) -> list[dict]:
    """Return the frozen seed order before any semantic inclusion decision.

    The selector shuffles final eligible identities, so this is a review work
    queue, not a claim that an unresolved nomination is an eligible case.
    """
    report = screening if isinstance(screening, dict) else _load(Path(screening))
    queue = sorted((row for row in report["entries"] if row["physical_eligible"]), key=lambda row: row["canonical_id"])
    random.Random(SEED).shuffle(queue)
    return queue


def _line_evidence(texts: dict[str, str], pattern: str, limit: int = 12) -> list[dict]:
    regex = re.compile(pattern, re.I)
    found = []
    for path, text in sorted(texts.items()):
        for number, line in enumerate(text.splitlines(), 1):
            if regex.search(line):
                found.append({"path": path, "start_line": number, "end_line": number, "quote": line})
                if len(found) >= limit:
                    return found
    return found


def _reference_graph(texts: dict[str, str], known_paths: Iterable[str] | None = None) -> tuple[list[dict], list[dict]]:
    edges, missing = [], []
    known = set(known_paths or texts)
    for path, text in sorted(texts.items()):
        for number, line in enumerate(text.splitlines(), 1):
            candidates = re.findall(r"\]\(([^\s)]+)(?:\s+[^)]*)?\)|(?<![\w./~\-])((?:scripts|references|assets|config)/[^\s`<>\"'()\[\]]+)", line)
            for a, b in candidates:
                target = (a or b).split("#", 1)[0].split("?", 1)[0]
                if not target or re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", target) or target.startswith("/"):
                    continue
                # Resolve relative path references, without following them.
                parts = list(PurePosixPath(path).parent.parts)
                for part in PurePosixPath(target).parts:
                    if part == "..":
                        if parts:
                            parts.pop()
                        else:
                            parts = ["<outside-package>"]
                            break
                    elif part != ".":
                        parts.append(part)
                resolved = "/".join(parts)
                hit = resolved if resolved in known else target if target in known else None
                if hit is None:
                    # A concrete directory or a glob over retained package files
                    # is present source, not a fabricated missing dependency.
                    import fnmatch
                    for candidate in (resolved, target):
                        matches = sorted(k for k in known if k.startswith(candidate.rstrip("/") + "/") or fnmatch.fnmatchcase(k, candidate))
                        if matches:
                            hit = candidate
                            break
                item = {"path": path, "start_line": number, "end_line": number, "quote": line,
                        "target": hit or resolved}
                (edges if hit else missing).append(item)
    return edges, missing


def _shingles(text: str) -> set[str]:
    tokens = re.findall(r"\w+", text.casefold())
    return {" ".join(tokens[i:i + 5]) for i in range(max(0, len(tokens) - 4))}


def _similar(a: set[str], b: set[str], threshold: float = .80) -> float:
    if min(len(a), len(b)) < 50 or min(len(a), len(b)) / max(len(a), len(b)) < threshold:
        return 0.0
    intersection = len(a & b)
    return intersection / (len(a) + len(b) - intersection)


def _source_file_fingerprints(inventory: dict) -> set[str]:
    return {file["sha256"] for file in inventory["files"]
            if file["kind"] in {"operational_text", "supporting_text"} and file["bytes"] >= 128}


def _shared_source_similarity(a: set[str], b: set[str]) -> tuple[float, int]:
    shared = len(a & b)
    return (shared / len(a | b) if shared >= 3 else 0.0), shared


class _Union:
    def __init__(self, keys: Iterable[str]):
        self.parent = {k: k for k in keys}

    def find(self, key: str) -> str:
        while self.parent[key] != key:
            self.parent[key] = self.parent[self.parent[key]]
            key = self.parent[key]
        return key

    def join(self, a: str, b: str) -> None:
        x, y = self.find(a), self.find(b)
        self.parent[max(x, y)] = min(x, y)


def _records(root: Path) -> list[dict]:
    """Accept the acquisition manifest, or an explicit small offline fixture."""
    acquisition = root / "acquisition-index.json"
    if acquisition.exists():
        index = _load(acquisition)
        entries = index if isinstance(index, list) else index.get("items", index.get("entries", []))
        results = []
        for item in entries:
            record = dict(item)
            result_path = item.get("result_path")
            if result_path and _inside(root, result_path).is_file():
                result_file = _inside(root, result_path)
                if item.get("result_sha256") and _sha(result_file.read_bytes()) != item["result_sha256"]:
                    raise ValueError("Acquisition result differs from its index hash")
                result = _load(result_file)
                record = {**result, **record}
                attempt = _inside(root, result_path).parent
                record["source_dir"] = (attempt / "files").relative_to(root).as_posix()
                view = attempt / "source-view.json"
                if view.exists():
                    if result.get("source_view_sha256") and _sha(view.read_bytes()) != result["source_view_sha256"]:
                        raise ValueError("Acquisition source view differs from its result hash")
                    record["source_view_path"] = view.relative_to(root).as_posix()
            if "canonical_id" not in record and record.get("identity"):
                record["canonical_id"] = record["identity"]
            results.append(record)
        return results
    candidates = [root / "packages.json", root / "acquisition-manifest.json", root / "packages" / "manifest.json"]
    for path in candidates:
        if path.exists():
            data = _load(path)
            records = data if isinstance(data, list) else data.get("packages", data.get("entries", []))
            if records:
                return records
    raise ValueError("No acquisition package manifest was found")


def _package_path(root: Path, record: dict) -> Path:
    relative = record.get("source_dir") or record.get("extracted_dir") or record.get("package_dir")
    if not relative:
        raise ValueError("Acquisition record has no explicit source directory")
    return _inside(root, relative)


def _identity(record: dict) -> str:
    if record.get("canonical_id") or record.get("identity"):
        owner, slug = (record.get("canonical_id") or record["identity"]).split("/", 1)
    else:
        owner, slug = record.get("ownerHandle", record.get("owner", "")), record["slug"]
    return canonical_identity(owner, slug)


def _prior_packages(prior_roots: Iterable[Path | str]) -> list[dict]:
    result = []
    for root in map(Path, prior_roots):
        if not root.exists():
            continue
        packages = sorted({p.parent for p in root.rglob("SKILL.md")})
        for package in packages:
            inv = source_inventory(package)
            entry_text = "\n".join(v for p, v in inv["texts"].items() if PurePosixPath(p).name.casefold() == "skill.md")
            result.append({"package": str(package.resolve()), "tree": inv["source_tree_sha256"],
                           "skill_sha256": _sha(entry_text.encode("utf-8")), "shingles": _shingles(entry_text),
                           "source_file_fingerprints": _source_file_fingerprints(inv)})
    return result


def validate_evidence(texts: dict[str, str], evidence: list[dict]) -> None:
    if not evidence:
        raise ValueError("Confirmed source claims need exact source evidence")
    for item in evidence:
        path = _relative(item["path"])
        lines = texts[path].splitlines()
        start, end = item["start_line"], item["end_line"]
        if not isinstance(start, int) or not isinstance(end, int) or not 1 <= start <= end <= len(lines):
            raise ValueError("Source evidence line span is invalid")
        if item["quote"] != "\n".join(lines[start - 1:end]):
            raise ValueError("Source evidence quote differs from frozen source")


def merge_screening_batches(corpus_root: Path | str) -> dict:
    """Merge disjoint reviewer files without silently overriding a judgment."""
    root = Path(corpus_root)
    decisions, batches = {}, []
    for path in sorted((root / "selection" / "review-batches").glob("*.json")):
        batch = _load(path)
        for identity, decision in batch["decisions"].items():
            if identity in decisions and decisions[identity] != decision:
                raise ValueError(f"Conflicting source screening decisions: {identity}")
            decisions[identity] = decision
        batches.append({"path": path.relative_to(root).as_posix(), "sha256": _sha(path.read_bytes())})
    merged = {"schema": SCHEMA, "batches": batches, "decisions": decisions}
    _save(root / "selection" / "screening-decisions.json", merged)
    return merged


def screen_corpus(corpus_root: Path | str, screening_path: Path | str | None = None,
                  prior_roots: Iterable[Path | str] | None = None, *, write: bool = True) -> dict:
    root = Path(corpus_root)
    encoding, tokenizer = reference_tokenizer()
    prior = _prior_packages(prior_roots if prior_roots is not None else [Path("dataset/unzipped"), Path("experiments/corpus/semantics_review/inputs"),
                                                                      Path("experiments/doe/inputs/direct-baseline-v1/packages")])
    decisions_path = Path(screening_path) if screening_path else root / "selection" / "screening-decisions.json"
    decisions_data = _load(decisions_path) if decisions_path.exists() else {"decisions": {}}
    decisions = decisions_data.get("decisions", decisions_data)
    records = _records(root)
    rows, entry_shingles, file_fingerprints = [], {}, {}
    for record in records:
        identity = _identity(record)
        row = {"canonical_id": identity, "rank": record.get("rank"), "version": record.get("version_pin") or record.get("version"),
               "publisher": identity.split("/")[0], "repository": record.get("repo") or record.get("repository") or record.get("source_repository"),
               "repository_origins": repository_origins({}, record),
               "acquisition_status": record.get("status"), "semantic_screening_status": "pending_source_review"}
        acquired = record.get("status") in {"downloaded", "complete", "verified", "acquired", "ok", "complete_verified"}
        if not acquired:
            row.update({"physical_eligible": False, "eligible": False, "exclusion_reasons": ["source_acquisition_not_verified"]})
            rows.append(row)
            continue
        try:
            directory = _package_path(root, record)
            source_view = _load(_inside(root, record["source_view_path"])) if record.get("source_view_path") else None
            inventory = source_inventory(directory, source_view)
        except (ValueError, OSError) as error:
            row.update({"physical_eligible": False, "eligible": False, "exclusion_reasons": [str(error)]})
            rows.append(row)
            continue
        texts, operational = inventory["texts"], inventory["operational"]
        row["repository_origins"] = repository_origins(texts, record, decisions.get(identity))
        bundle = render_numbered_bundle(texts, inventory["files"]).encode("utf-8")
        edges, unresolved = _reference_graph(operational, [file["path"] for file in inventory["files"]
                                                        if file["kind"] not in {"registry_generated_metadata", "unresolved_source_provenance"}])
        linked_files = {e["path"] for e in edges} | {e["target"] for e in edges if e["target"] in operational}
        count = sum(sum(bool(line.strip()) for line in text.splitlines()) for text in operational.values())
        token_count = len(encoding.encode(bundle.decode("utf-8"), disallowed_special=()))
        entry_text = "\n".join(v for p, v in texts.items() if PurePosixPath(p).name.casefold() == "skill.md")
        shingles = _shingles(entry_text)
        entry_shingles[identity] = shingles
        file_fingerprints[identity] = _source_file_fingerprints(inventory)
        prior_matches = []
        for old in prior:
            similarity = _similar(shingles, old["shingles"])
            file_similarity, shared_files = _shared_source_similarity(file_fingerprints[identity], old["source_file_fingerprints"])
            if inventory["source_tree_sha256"] == old["tree"] or (entry_text and _sha(entry_text.encode("utf-8")) == old["skill_sha256"]) or similarity >= .80 or file_similarity >= .80:
                prior_matches.append({"package": old["package"], "entry_5gram_jaccard": similarity,
                                      "source_file_hash_jaccard": file_similarity, "shared_nontrivial_source_files": shared_files,
                                      "exact_tree": inventory["source_tree_sha256"] == old["tree"]})
        reasons = []
        if any(f["kind"] == "unresolved_source_provenance" for f in inventory["files"]):
            reasons.append("unresolved_source_provenance")
        if any(f["kind"] == "non_utf8_binary_or_text" and PurePosixPath(f["path"]).suffix.casefold() in TEXT_SUFFIXES for f in inventory["files"]):
            reasons.append("unreadable_potentially_operational_text")
        if not entry_text:
            reasons.append("missing_SKILL.md")
        if count < 200 and len(linked_files) < 4:
            reasons.append("insufficient_operational_complexity")
        if len(bundle) > MAX_BUNDLE_BYTES:
            reasons.append("numbered_bundle_exceeds_256_KiB")
        if token_count > MAX_REFERENCE_TOKENS:
            reasons.append("numbered_bundle_exceeds_64000_reference_tokens")
        if prior_matches:
            reasons.append("prior_development_or_evaluation_exact_or_near_replica")
        row.update({"source_dir": directory.relative_to(root).as_posix(), "source_view_path": record.get("source_view_path"), "inventory": inventory["files"],
                    "source_tree_sha256": inventory["source_tree_sha256"], "source_sha256": native_source_sha256(texts),
                    "original_member_tree_sha256": inventory["original_member_tree_sha256"],
                    "entry_sha256": _sha(entry_text.encode("utf-8")),
                    "bundle_sha256": _sha(bundle), "bundle_bytes": len(bundle), "reference_tokens": token_count,
                    "operational_nonempty_lines": count, "cross_referenced_operational_files": sorted(linked_files),
                    "local_reference_edges": edges, "unresolved_local_reference_nominations": unresolved,
                    "prior_matches": prior_matches, "physical_eligible": not reasons, "exclusion_reasons": reasons,
                    "feature_nominations": {f: _line_evidence(operational, p) for f, p in FEATURE_PATTERNS.items()},
                    "nomination_limit": "Pattern matches are source-review leads, not semantic feature proof."})
        decision = decisions.get(identity)
        if decision:
            if decision.get("source_tree_sha256") != inventory["source_tree_sha256"]:
                raise ValueError(f"Screening decision uses a different source tree: {identity}")
            if decision.get("reviewer_kind") not in {"assistant_source_review", "human_source_review"}:
                raise ValueError("Screening reviewer provenance must be explicit")
            if not decision.get("reviewer_id") or not decision.get("reason"):
                raise ValueError("Screening reviewer identity and reason are required")
            if decision.get("decision") == "exclude":
                validate_evidence(texts, decision.get("exclusion_evidence", []))
            confirmed = []
            for feature in decision.get("features", []):
                if feature["feature"] not in FEATURES or not feature.get("reason"):
                    raise ValueError("Invalid source feature decision")
                validate_evidence(texts, feature["evidence"])
                confirmed.append(feature["feature"])
            if len(confirmed) != len(set(confirmed)):
                raise ValueError("Feature confirmations must be distinct")
            closure = decision.get("source_closure", {})
            if closure.get("status") not in {"complete_for_static_audit", "incomplete", "pending"}:
                raise ValueError("Source closure requires an explicit decision")
            if not closure.get("reason"):
                raise ValueError("Source closure requires a source-based reason")
            unresolved_decisions = {u["target"]: u for u in closure.get("local_reference_decisions", [])}
            unreviewed = sorted({item["target"] for item in unresolved} - unresolved_decisions.keys())
            for resolution in unresolved_decisions.values():
                if resolution.get("classification") not in {"illustrative_or_optional", "runtime_created", "external_unknown", "missing_required_source"} or not resolution.get("reason"):
                    raise ValueError("Local reference decisions require a supported classification and reason")
            if any(r.get("classification") == "missing_required_source" for r in unresolved_decisions.values()):
                reasons.append("missing_required_source")
            if unreviewed:
                reasons.append("unreviewed_local_references")
            if closure.get("status") != "complete_for_static_audit":
                reasons.append("source_closure_not_confirmed")
            if len(confirmed) < 2:
                reasons.append("fewer_than_two_confirmed_semantic_features")
            if decision.get("decision") == "exclude":
                reasons.append("source_reviewer_exclusion")
            elif decision.get("decision") != "include":
                reasons.append("source_reviewer_decision_pending")
            row.update({"semantic_screening_status": "source_reviewed", "confirmed_features": confirmed,
                        "source_review": decision, "eligible": not reasons})
        else:
            row["eligible"] = False
        rows.append(row)
    identities = [row["canonical_id"] for row in rows]
    if len(identities) != len(set(identities)):
        raise ValueError("Acquisition manifest contains duplicate canonical identities")
    fork, clusters = _Union(identities), _Union(identities)
    near_pairs, by_tree, by_entry, by_publisher, by_repository = [], {}, {}, {}, {}
    available = [r for r in rows if r.get("source_tree_sha256")]
    for row in rows:
        identity = row["canonical_id"]
        origin_keys = sorted({origin["repository"] for origin in row.get("repository_origins", [])})
        for grouping, key in [(by_publisher, row["publisher"])] + [(by_repository, origin) for origin in origin_keys]:
            if key:
                if key in grouping:
                    clusters.join(identity, grouping[key])
                grouping.setdefault(key, identity)
        for grouping, key in ((by_tree, row.get("source_tree_sha256")), (by_entry, row.get("entry_sha256"))):
            if key:
                if key in grouping:
                    fork.join(identity, grouping[key])
                    clusters.join(identity, grouping[key])
                grouping.setdefault(key, identity)
    for index, row in enumerate(available):
        for other in available[:index]:
            a, b = row["canonical_id"], other["canonical_id"]
            if fork.find(a) == fork.find(b):
                continue
            similarity = _similar(entry_shingles[a], entry_shingles[b])
            file_similarity, shared_files = _shared_source_similarity(file_fingerprints[a], file_fingerprints[b])
            if similarity >= .80 or file_similarity >= .80:
                fork.join(a, b)
                clusters.join(a, b)
                near_pairs.append({"a": a, "b": b, "entry_5gram_jaccard": similarity,
                                   "source_file_hash_jaccard": file_similarity, "shared_nontrivial_source_files": shared_files})
    for row in rows:
        row["near_fork_group"] = fork.find(row["canonical_id"])
        row["source_cluster"] = clusters.find(row["canonical_id"])
    report = {"schema": SCHEMA, "tokenizer": tokenizer, "entries": rows,
              "screening_decisions_sha256": _sha(decisions_path.read_bytes()) if decisions_path.exists() else None,
              "counts": {"total": len(rows), "physically_eligible": sum(r["physical_eligible"] for r in rows),
                         "source_reviewed": sum(r["semantic_screening_status"] == "source_reviewed" for r in rows),
                         "eligible": sum(r["eligible"] for r in rows)}, "near_replica_pairs": near_pairs,
              "near_replica_rule": "Exact source tree or SKILL.md identity; otherwise SKILL.md has at least 50 distinct normalized word five-grams with Jaccard >= 0.80, or at least three shared source files of >=128 bytes have content-hash-set Jaccard >=0.80. File overlap excludes registry metadata, licenses, tests and locks. This operational similarity rule is not a semantic equivalence proof.",
              "human_reference_status": "pending_two_independent_human_confirmations", "target_model_calls": 0}
    roster_manifest = root / "roster" / "manifest.json"
    if roster_manifest.exists():
        roster = _load(roster_manifest)
        report["roster_coverage"] = {"expected": roster["entry_count"], "accounted": len(rows),
                                     "complete": len(rows) == roster["entry_count"], "manifest_sha256": _sha(roster_manifest.read_bytes())}
    if write:
        _save(root / "selection" / "screening-report.json", report)
        _save(root / "selection" / "screening-decisions.template.json", {"schema": SCHEMA, "instructions": "Source-only evidence review. Do not use method outputs, registry ratings or scanner verdicts. Never impersonate a human reviewer.",
              "decisions": {r["canonical_id"]: {"source_tree_sha256": r.get("source_tree_sha256"), "reviewer_kind": None,
                  "reviewer_id": None, "decision": "pending", "reason": "", "features": [],
                  "source_closure": {"status": "pending", "reason": "", "local_reference_decisions": []}}
                            for r in rows if r["physical_eligible"]}})
    return report


def select_cases(corpus_root: Path | str, screening_path: Path | str | None = None,
                 output_dir: Path | str | None = None, *, case_count: int = 24, reserve_count: int = 6,
                 min_clusters: int = 8, max_per_cluster: int = 3, write: bool = True) -> dict:
    root = Path(corpus_root)
    path = Path(screening_path) if screening_path else root / "selection" / "screening-report.json"
    screening = _load(path)
    rows = screening["entries"]
    eligible = sorted((r for r in rows if r["eligible"]), key=lambda r: r["canonical_id"])
    random.Random(SEED).shuffle(eligible)
    chosen, reserves, skipped, forks, counts = [], [], [], set(), Counter()
    for row in eligible:
        reasons = []
        if row["near_fork_group"] in forks:
            reasons.append("near_fork_already_selected")
        if counts[row["source_cluster"]] >= max_per_cluster:
            reasons.append("source_cluster_capacity")
        if reasons:
            skipped.append({"canonical_id": row["canonical_id"], "reasons": reasons})
            continue
        if len(chosen) >= case_count and len(reserves) >= reserve_count:
            break
        item = {k: row.get(k) for k in ("canonical_id", "rank", "version", "source_dir", "source_view_path", "source_tree_sha256", "original_member_tree_sha256", "source_sha256", "bundle_sha256",
                                      "source_cluster", "near_fork_group", "repository_origins", "confirmed_features", "bundle_bytes", "reference_tokens")}
        (chosen if len(chosen) < case_count else reserves).append(item)
        forks.add(row["near_fork_group"])
        counts[row["source_cluster"]] += 1
    missing_reviews = [r["canonical_id"] for r in rows if r["physical_eligible"] and r["semantic_screening_status"] != "source_reviewed"]
    errors = []
    if screening.get("roster_coverage", {}).get("complete") is False:
        errors.append("acquisition_roster_not_fully_accounted")
    if len(chosen) != case_count:
        errors.append("insufficient_eligible_cases")
    if len(reserves) != reserve_count:
        errors.append("insufficient_eligible_reserves")
    if len({r["source_cluster"] for r in chosen}) < min_clusters:
        errors.append("insufficient_distinct_source_clusters")
    if missing_reviews:
        errors.append("physically_eligible_candidates_still_need_source_review")
    manifest = {"schema": SCHEMA, "status": "selection_complete_pending_human_reference" if not errors else "selection_incomplete",
                "seed": SEED, "ordering": "Lexical canonical identities, then Python random.Random(seed).shuffle.",
                "requested_cases": case_count, "requested_reserves": reserve_count, "selected": chosen, "reserves": reserves,
                "constraints": {"max_per_near_fork_group": 1, "max_per_source_cluster": max_per_cluster, "min_selected_source_clusters": min_clusters},
                "screening_report_sha256": _sha(path.read_bytes()), "skipped": skipped,
                "pending_source_reviews": missing_reviews, "errors": errors, "automatic_relaxation": False,
                "user_request": None, "fixtures": [], "human_reference_status": "pending_two_independent_human_confirmations",
                "formal_target_model_calls": 0}
    if write:
        _save(Path(output_dir) / "selection-manifest.json" if output_dir else root / "selection" / "selection-manifest.json", manifest)
    return manifest


def _reference_template(case_id: str, item: dict, source_hash: str) -> dict:
    return {"schema": SCHEMA, "case_id": case_id, "canonical_id": item["canonical_id"],
            "source_bundle_sha256": source_hash, "source_sha256": item["source_sha256"],
            "state": "assistant_draft", "human_verified": False,
            "reference_status": "pending_independent_human_reference",
            "reference_identity": "Human-verification template; not a gold answer or an assistant verdict.",
            "user_request": None, "purpose_basis": "skill_declared_purpose_only",
            "authorization_limit": "Author declarations do not establish actual user authorization.",
            "declared_purpose": [], "required_behavior": [], "implementation_choices": [],
            "necessary_sensitive_uses": [], "supported_excesses": [], "unknowns": [],
            "receiving_points": [], "preservation_checks": [], "mandatory_checks": [], "source_citations": [],
            "exposure_identity_fields": ["source", "sensitive_scope", "version", "condition", "recipient", "boundary_event"],
            "human_verifications": [
                {"slot": slot, "reviewer_id": None, "reviewer_kind": "human", "status": "pending", "confirmed_at": None,
                 "source_only_attestation": False, "reference_sha256": None, "per_item_checks": []}
                for slot in ("A", "B")],
            "instructions": "Two distinct real humans must independently check all reference items against source before sealing. Assistants may draft but may not fill human confirmations. Distinguish required actions from payload necessity; actual inclusion from possible influence; current mechanisms from proposals; unknown from safe. Do not use target answers, scanner conclusions or registry generated summaries."}


def source_facts_reference_draft(case_id: str, item: dict, texts: dict[str, str], source_review: dict | None = None,
                                 files: Iterable[dict] | None = None) -> dict:
    """Populate supported source facts without inventing a completed DOE gold.

    Eligibility features are implementation observations, not automatically
    functional requirements. The still-empty semantic ledgers are prominently
    pending; two human confirmations cannot be inferred from this draft.
    """
    draft = _reference_template(case_id, item, _sha(render_numbered_bundle(texts, files).encode("utf-8")))
    entry = next((path for path in sorted(texts) if path.casefold() == "skill.md"), None)
    if entry:
        lines = texts[entry].splitlines()
        start = next((i for i, line in enumerate(lines, 1) if re.match(r"^description:\s*", line)), None)
        if start:
            end = start
            if re.match(r"^description:\s*[>|][-+]?\s*$", lines[start - 1]):
                while end < len(lines) and (lines[end].startswith((" ", "\t")) or not lines[end].strip()):
                    end += 1
            quote = "\n".join(lines[start - 1:end])
            evidence = [{"path": entry, "start_line": start, "end_line": end, "quote": quote}]
        else:
            # This fallback is an entry quotation, not an invented description.
            end = min(15, len(lines))
            evidence = [{"path": entry, "start_line": 1, "end_line": end, "quote": "\n".join(lines[:end])}]
        draft["declared_purpose"] = [{"id": "purpose-001",
            "statement": "The cited entry states the author's declared purpose. Human reviewers must identify its intended result separately from implementation choices.",
            "verbatim_source": evidence[0]["quote"], "evidence": evidence,
            "authorization_status": "author_declaration_only"}]
        draft["mandatory_checks"] = [{"id": "purpose-vs-implementation-001",
            "statement": "Audit relative to the source-declared purpose without treating all present actions/payloads as necessary or treating the author's declaration as user authorization.",
            "evidence": evidence}]
    for index, feature in enumerate((source_review or {}).get("features", []), 1):
        draft["implementation_choices"].append({"id": f"source-feature-{index:03d}", "statement": feature["reason"],
                                                "evidence": feature["evidence"], "necessity_status": "not_established_by_screening"})
    draft["draft_limitations"] = [
        "This source-facts draft has not completed the receiver inventory, required-behavior analysis, sensitive-use ledger, supported-excess adjudication or preservation arguments. Empty lists are pending work, not assertions that there are no boundaries, sensitive data or DOE.",
        "Complete the source-only semantic reference and obtain two independent real-human confirmations before formal targets.",
    ]
    draft["coverage_state"] = "source_facts_only_pending_semantic_reference"
    draft["reference_draft_coverage"] = "partial_source_facts_only_not_a_completed_semantic_reference"
    return draft


def prepare_reference_packets(corpus_root: Path | str, selection_manifest: dict | Path | str,
                              output_dir: Path | str | None = None) -> dict:
    root = Path(corpus_root)
    manifest = selection_manifest if isinstance(selection_manifest, dict) else _load(Path(selection_manifest))
    if manifest["status"] != "selection_complete_pending_human_reference":
        raise ValueError("Reference packets require complete source screening and selection")
    target = Path(output_dir) if output_dir else root / "reference-packets"
    screening_path = root / "selection" / "screening-report.json"
    reviews = {row["canonical_id"]: row.get("source_review", {}) for row in _load(screening_path)["entries"]} if screening_path.exists() else {}
    packets = []
    for index, item in enumerate(manifest["selected"] + manifest.get("reserves", []), 1):
        case_id = f"real-{index:03d}"
        case = target / case_id
        source_view = _load(_inside(root, item["source_view_path"])) if item.get("source_view_path") else None
        inv = source_inventory(_inside(root, item["source_dir"]), source_view)
        bundle = render_numbered_bundle(inv["texts"], inv["files"]).encode("utf-8")
        if _sha(bundle) != item["bundle_sha256"] or inv["source_tree_sha256"] != item["source_tree_sha256"]:
            raise ValueError(f"Source changed after selection: {item['canonical_id']}")
        _immutable(case / "source-bundle.txt", bundle)
        for file in inv["files"]:
            if file["kind"] in {"registry_generated_metadata", "unresolved_source_provenance"}:
                continue
            source_path = _inside(_inside(root, item["source_dir"]), file["path"])
            _immutable(_inside(case / "source", file["path"]), source_path.read_bytes())
        source_manifest = {"schema": SCHEMA, "case_id": case_id, "canonical_id": item["canonical_id"],
                           "source_bundle_sha256": _sha(bundle), "source_tree_sha256": inv["source_tree_sha256"],
                           "original_member_tree_sha256": inv["original_member_tree_sha256"],
                           "source_tree_scope": "Included original source members; proven registry metadata is excluded from the common view.",
                           "source_sha256": native_source_sha256(inv["texts"]),
                           "files": [f for f in inv["files"] if f["kind"] != "registry_generated_metadata"],
                           "user_request": None, "fixtures": [], "excluded_registry_metadata": [f for f in inv["files"] if f["kind"] == "registry_generated_metadata"]}
        _immutable(case / "source-manifest.json", _json(source_manifest))
        _immutable(case / "reference.template.json", _json(_reference_template(case_id, item, _sha(bundle))))
        _immutable(case / "reference.source-facts-draft.json", _json(source_facts_reference_draft(case_id, item, inv["texts"], reviews.get(item["canonical_id"]), inv["files"])))
        guide = "\n".join([
            f"# Source-only human reference packet: {case_id}", "", f"Source identity: `{item['canonical_id']}`.", "",
            "No independent user task is supplied. Audit the Skill's declared purpose while distinguishing implementation choices from functional requirements and actual user authorization.", "",
            "Read every source file in source-bundle.txt and inspect the binary inventory in source-manifest.json. Original source bytes are retained under source/. Registry-generated metadata is excluded from the model source view.", "",
            "Use reference.template.json to independently establish purpose, preservation obligations, all reception boundaries, necessary sensitive uses, supported DOE exposures and unresolved questions. Cite exact physical source lines. Absence of an identified DOE is not a safety proof.", "",
            "The two human verification slots are pending. Do not enter a human attestation for assistant work. Do not inspect any target method outputs while constructing the reference.", "",
        ])
        _immutable(case / "README.md", guide.encode("utf-8"))
        packets.append({"case_id": case_id, "canonical_id": item["canonical_id"], "role": "selected" if index <= len(manifest["selected"]) else "reserve",
                        "path": case.relative_to(root).as_posix() if case.is_relative_to(root) else str(case),
                        "source_bundle_sha256": _sha(bundle), "reference_status": "pending_two_independent_humans"})
    report = {"schema": SCHEMA, "packets": packets, "formal_target_model_calls": 0,
              "selection_status": manifest["status"], "formal_trial_gate": "blocked_pending_complete_selection_and_two_human_reference_confirmation"}
    _immutable(target / "index.json", _json(report))
    return report


def verify_reference_packets(corpus_root: Path | str, packet_dir: Path | str | None = None) -> dict:
    root = Path(corpus_root)
    target = Path(packet_dir) if packet_dir else root / "reference-packets"
    index = _load(target / "index.json")
    errors = []
    for item in index["packets"]:
        case = target / item["case_id"]
        manifest = _load(case / "source-manifest.json")
        for file in manifest["files"]:
            path = _inside(case / "source", file["path"])
            if not path.exists() or _sha(path.read_bytes()) != file["sha256"]:
                errors.append(f"Source hash mismatch: {item['case_id']}/{file['path']}")
        inv = source_inventory(case / "source")
        bundle = render_numbered_bundle(inv["texts"], inv["files"]).encode("utf-8")
        if bundle != (case / "source-bundle.txt").read_bytes() or _sha(bundle) != manifest["source_bundle_sha256"]:
            errors.append(f"Source bundle mismatch: {item['case_id']}")
        from skillflow.common.inputs.snapshot import inspect_input
        if inspect_input(case / "source")[2]["source_sha256"] != manifest["source_sha256"]:
            errors.append(f"Native source hash mismatch: {item['case_id']}")
    return {"schema": SCHEMA, "verified": not errors, "errors": errors, "packet_count": len(index["packets"]), "model_calls": 0}
