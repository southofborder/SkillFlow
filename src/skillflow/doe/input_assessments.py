"""Complete input inventory and actionable demand-complement assessments."""
from __future__ import annotations

from collections import defaultdict, deque
from copy import deepcopy
from typing import Literal

from pydantic import Field

from skillflow.common.recording import canonical_sha256
from skillflow.propagation.contracts.values import StrictSpec, Text, Index
from skillflow.propagation.contracts.demand import EachDemandStep
from skillflow.propagation.data.models import PathStep
from skillflow.propagation.contracts.limitations import diagnostic_applies
from .material import _id
from .input_contracts import prefix, overlaps, covers
from .input_locations import AssessmentLocation, InputModification, RetrievalProjection, InputLocationBuilder
from .source_input_findings import NormalizedSourceInputFinding

AssessmentPath = list[PathStep | EachDemandStep]


class AssessedRange(StrictSpec):
    status: Literal["required", "deletable", "unresolved"]
    property: Literal["value", "presence", "cardinality", "shape", "truth"]
    path: AssessmentPath
    excluded_paths: list[AssessmentPath]
    demand_refs: list[Text]
    diagnostic_refs: list[Text]
    contract_refs: list[Text]
    reason: Text
    modification: InputModification | None
    modification_limit: Text | None


class InputAssessment(StrictSpec):
    id: Text
    node_kind: Literal["ir_input", "op_input", "acquisition_output"]
    instruction_id: Text
    operation_id: Text | None
    input_index: Index
    data_ids: list[Text]
    coverage: Text
    ranges: list[AssessedRange]
    location: AssessmentLocation
    retrieval_projection: RetrievalProjection | None


class InputSemanticFinding(StrictSpec):
    id: Text
    kind: Literal["excessive_input", "wrong_input", "missing_input"]
    instruction_id: Text
    operation_id: Text | None
    input_index: Index | None
    path: AssessmentPath
    excluded_paths: list[AssessmentPath]
    assessment_refs: list[Text]
    diagnostic_refs: list[Text]
    reason: Text
    origin: Literal["demand_analysis", "source_review"]
    source_review_refs: list[Text]
    source_finding: NormalizedSourceInputFinding | None


def derivation_problem_refs(engine):
    """Follow actual derivation ancestry, not all fields in a shared IR."""
    refs, children = {}, defaultdict(set)
    for key, row in engine.derivations.items():
        refs[key] = {rule.split(":", 1)[1] for rule in row["rules"]
                     if rule.startswith(("input_contract_gap:", "unavailable_dependency:"))}
        for parent in row["parents"]:
            children[parent].add(key)
    queue = deque(key for key in sorted(refs) if refs[key])
    queued = set(queue)
    while queue:
        key = queue.popleft()
        queued.discard(key)
        for child in sorted(children[key]):
            added = refs[key] - refs[child]
            if added:
                refs[child].update(added)
                if child not in queued:
                    queue.append(child)
                    queued.add(child)
    return refs


def applicable_contract_diagnostics(derivations, ids):
    from types import SimpleNamespace
    refs = derivation_problem_refs(SimpleNamespace(derivations=derivations))
    return set().union(*(refs[key] for key in ids)) if ids else set()


def _range(row):
    marker = [{"kind": "each"}] if row.get("each") else []
    return {"property": row["property"], "path": marker + row["path"],
            "excluded_paths": [marker + p for p in row["excluded_paths"]]}


def _known_paths(data, ids):
    paths = {}
    seen = set()
    def add(identity, base):
        if (identity, canonical_sha256(base)) in seen or len(base) > 32:
            return
        seen.add((identity, canonical_sha256(base)))
        content = data.get(identity, {}).get("content", {})
        if content.get("form") in {"known_parts", "constructed"}:
            for part in content.get("parts", []):
                path = base + part["path"]
                paths[canonical_sha256(path)] = path
                children = [part["data"]] if "data" in part else part.get("data_ids", [])
                for child in children:
                    add(child, path)
        for path in content.get("excluded_paths", []):
            full = base + path
            paths[canonical_sha256(full)] = full
    for identity in ids:
        add(identity, [])
    return list(paths.values())


def _reference_index(engine):
    """Resolve existing lexical bindings without creating nodes or diagnostics."""
    nodes = {(row["kind"], row["instruction_id"], row["operation_id"], row["slot"]): key
             for key, row in engine.nodes.items()}
    contexts = defaultdict(set)
    segments = defaultdict(set)
    for info in engine.ops.values():
        ir, scope = info["position"]["instruction_id"], info["scope"]
        contexts[ir].add(scope)
        if scope is not None:
            segments[(ir, tuple(info["segment"][:2]))].add(scope)

    def references(ref, ir, scope=None):
        kind = ref["kind"]
        if kind == "alternatives":
            return set().union(*(references(value, ir, scope) for value in ref["items"]))
        if kind == "input":
            node = nodes.get(("ir_input", ir, None, ref["index"]))
        elif kind == "local":
            key = (ir, scope, ref["name"])
            node = (engine.elements.get(key) or engine.locals.get(key)
                    or engine.locals.get((ir, None, ref["name"])))
        else:
            node = None
        return {node} if node is not None else set()

    def scopes(ir, path):
        return sorted(segments.get((ir, tuple(path)), ())) if path else [None]

    return nodes, references, scopes, contexts


def _declared_paths(engine, references, scopes):
    """Use named source paths only on their exact recorded Data versions."""
    from .sensitivity_engine import range_presence
    from skillflow.propagation.contracts.sensitivity import extract_sensitivity_candidate
    paths = defaultdict(dict)

    def add(ir, scope_path, ref, path):
        if not path:
            return
        for scope in scopes(ir, scope_path):
            for node_id in references(ref, ir, scope):
                for data_id in engine.nodes[node_id]["data_ids"]:
                    if range_presence(engine.index.data, data_id, path) not in {"absent", "invalid", "empty"}:
                        paths[data_id][canonical_sha256(path)] = deepcopy(path)

    for scope in extract_sensitivity_candidate(engine.raw)["scopes"]:
        for row in scope["declarations"]:
            add(scope["instruction_id"], scope["scope_path"], row["value"], row["path"])
    for realization in engine.realizations.values():
        for row in realization.get("constraints", []):
            if row["kind"] == "forbid_information":
                source = row["source"]
                add(source["instruction_id"], source["scope_path"], source["value"], row.get("path", []))
    return paths


def _consumer_index(engine, nodes, references):
    """Follow only explicit value aliases, never global equal-Data uses."""
    consumers, aliases = defaultdict(list), defaultdict(set)
    for key, info in engine.ops.items():
        ir = info["position"]["instruction_id"]
        for slot, (ref, _) in engine.slots(key).items():
            for source in references(ref, ir, info["scope"]):
                consumers[source].append((key, slot, tuple(info["record"]["inputs"][slot])))
    for ir, spec in engine.compiled["ir_semantics"].items():
        for binding in spec["output_bindings"]:
            target = nodes.get(("ir_output", ir, None, binding["output_index"]))
            if target is not None:
                for source in references(binding["value"], ir):
                    aliases[source].add(target)
    for ir, instruction in engine.index.instructions.items():
        for slot, operand in enumerate(instruction["inputs"]):
            if operand["type"] == "result" and operand["identifier"] in engine.definitions:
                producer, output = engine.definitions[operand["identifier"]]
                source = nodes.get(("ir_output", producer, None, output))
                target = nodes.get(("ir_input", ir, None, slot))
                if source is not None and target is not None:
                    aliases[source].add(target)
    cache = {}

    def uses(source):
        if source not in cache:
            seen, pending, found = set(), [source], set()
            while pending:
                current = pending.pop()
                if current in seen:
                    continue
                seen.add(current)
                found.update(consumers.get(current, ()))
                pending.extend(aliases.get(current, ()))
            cache[source] = (sorted(found), seen)
        return cache[source]

    return uses


def _closed_remainder(data, ids, excluded):
    """A fully described object's listed members can exhaust its remainder."""
    return bool(ids) and all(
        (content := data[identity]["content"]).get("form") == "known_parts"
        and content.get("parts_complete") is True
        and all(any(covers(path, part["path"]) for path in excluded) for part in content["parts"])
        for identity in ids)


class InputReviewBarrierIndex:
    """Read-only actual-use lookup shared by generation and result validation."""
    def __init__(self, engine):
        from .review_barriers import ReviewValidationBarriers
        self.engine = engine
        self.barriers = ReviewValidationBarriers(getattr(getattr(engine, "contracts", None), "receipt", None))
        self.nodes, references, _, _ = _reference_index(engine)
        self.consumers = _consumer_index(engine, self.nodes, references) if self.barriers.barriers else None

    def for_node(self, node):
        rows = {row["id"]: row for row in self.barriers.global_barriers}

        def collect(operation):
            info = self.engine.ops[operation]
            rows.update((row["id"], row) for row in self.barriers.for_operation(
                info["position"]["instruction_id"], info["raw_op"]))

        if node["operation_id"] is not None:
            collect(node["operation_id"])
        # Follow actual lexical aliases, never global equality of Data values.
        if self.consumers is not None and node["kind"] in {"ir_input", "op_output"}:
            identity = self.nodes[(node["kind"], node["instruction_id"], node["operation_id"], node["slot"])]
            uses, _ = self.consumers(identity)
            for operation, _, _ in uses:
                collect(operation)
        return [deepcopy(rows[key]) for key in sorted(rows)]

    def for_assessment(self, assessment):
        kind = "op_output" if assessment["node_kind"] == "acquisition_output" else assessment["node_kind"]
        key = (kind, assessment["instruction_id"], assessment["operation_id"], assessment["input_index"])
        if key not in self.nodes:
            raise ValueError("Input review assessment has no actual operand node")
        return self.for_node(self.engine.nodes[self.nodes[key]])


def build_input_assessments(engine):
    from .sensitivity_engine import demand_overlap
    from .constraint_preservation import ConstraintAnalysis
    by_node = defaultdict(list)
    for identity, row in engine.derivations.items():
        node = row["node"]
        by_node[(node["kind"], node["instruction_id"], node["operation_id"], node["slot"])].append((identity, row))
    problem_refs = derivation_problem_refs(engine)
    constraint_analysis = ConstraintAnalysis(engine)
    node_index, references, scopes, contexts = _reference_index(engine)
    declared_paths = _declared_paths(engine, references, scopes)
    from .review_barriers import barrier_diagnostic, barrier_reason
    review_barriers = InputReviewBarrierIndex(engine)
    consumer_uses = (_consumer_index(engine, node_index, references) if constraint_analysis.checks else None)
    builder = InputLocationBuilder(engine)
    results, findings = [], []

    # Pure constraints are not positive seeds. Nevertheless, an output used
    # directly by a constraint expression cannot be removed on a zero-use
    # assumption merely because that expression has no recorded atomic input.
    condition_uses = defaultdict(list)
    if constraint_analysis.checks:
        from .sensitivity_engine import _expression_uses
        for identity, declaration in constraint_analysis.checker.constraints.items():
            check = constraint_analysis.checks[identity]
            if check["structural"] and constraint_analysis.checker.complete_scope(identity):
                continue
            for field in ("condition", "success"):
                target = declaration.get(field)
                located = constraint_analysis.checker.booleans.location(target) if target else None
                if located is None:
                    continue
                expression, owner, _ = located
                for scope in contexts.get(owner, {None}) | {None}:
                    for ref, wanted in _expression_uses(expression):
                        for source in references(ref, owner, scope):
                            condition_uses[source].append((check["raw_pointer"], field, wanted["path"]))

    def preservation(node, path):
        if not constraint_analysis.checks:
            return True, []
        uses = []
        failures = set()
        if node["kind"] == "op_input":
            uses = [(node["operation_id"], node["slot"], node["data_ids"])]
        elif node["kind"] in {"ir_input", "op_output"}:
            node_id = node_index[(node["kind"], node["instruction_id"], node["operation_id"], node["slot"])]
            uses, aliases = consumer_uses(node_id)
            for alias in aliases:
                for pointer, field, required_path in condition_uses.get(alias, ()):
                    if overlaps(path, required_path):
                        failures.add(f"Removing {path} from {node['instruction_id']}/{node['kind']}/{node['slot']} "
                            f"can change {pointer}/{field}, which directly reads {required_path}. "
                            "The recorded consumer-input checks do not establish preservation of this direct output/operand expression.")
        # Acquisition output is an information-use assessment, not an assertion
        # that the external interface supports a narrower retrieval request.
        for key, slot, ids in uses:
            for data_id in ids:
                references, preserved = constraint_analysis.evaluate(key, slot, data_id, path)
                if not preserved:
                    failures.update(constraint_analysis.preservation[ref]["reason"] for ref in references
                                    if not constraint_analysis.preservation[ref]["preserved"])
        return not failures, sorted(failures)

    for node in list(engine.nodes.values()):
        kind = node["kind"]
        if kind not in {"ir_input", "op_input", "op_output"}:
            continue
        if kind == "op_output" and engine.ops[node["operation_id"]]["spec"]["op"] not in {"read", "receive"}:
            continue
        ir, operation, slot = node["instruction_id"], node["operation_id"], node["slot"]
        state = engine.index.coverage[ir]
        assessment = {"node_kind": "acquisition_output" if kind == "op_output" else kind,
            "instruction_id": ir, "operation_id": operation, "input_index": slot,
            "data_ids": deepcopy(node["data_ids"]), "coverage": state, "ranges": []}
        assessment["id"] = _id("input_assessment_", {k: v for k, v in assessment.items() if k != "ranges"})
        if state == "infeasible":
            results.append(assessment)
            continue
        demands = sorted(by_node.get((kind, ir, operation, slot), []))
        limits = [d["id"] for d in engine.diagnostics.values() if d["blocking"]
            and not d["code"].startswith("input_contract_") and diagnostic_applies(d, {ir})]
        contracts = engine.contracts.references(operation) if operation else []
        ranges = assessment["ranges"]
        barriers = review_barriers.for_node(node)
        if (kind == "ir_input" and not demands
                and not barriers
                and engine.index.instructions[ir]["inputs"][slot]["type"] in {"literal", "external_resource"}
                and not builder.location(assessment)["raw_annotation_sites"]):
            ranges.append({"status": "unresolved", "property": "value", "path": [], "excluded_paths": [],
                "demand_refs": [], "diagnostic_refs": [], "contract_refs": [],
                "reason": "The CFG operand at " + builder.location(assessment)["cfg_pointer"]
                    + " has no recorded processing value use under /ir_semantics/" + ir
                    + ". Its role may have been compiled into operation metadata, but no demand-transfer binding to that metadata is established. "
                      "Supply the exact operand-to-location/path/selector relation or a reviewed independent-input relation to assess this operand; absence of a value use does not authorize argument removal."})
            results.append(assessment)
            continue
        for identity, row in demands:
            refs = sorted(problem_refs[identity])
            unavailable = any(engine.diagnostics[ref]["code"] == "unavailable_required_action" for ref in refs)
            ranges.append({**_range(row), "status": "unresolved" if row["conservative"] else "required",
                "demand_refs": [identity], "diagnostic_refs": refs, "contract_refs": contracts,
                "reason": ("The declared dependencies of a required but unestablished action retain this range: " if unavailable
                           else "The recorded transfer retains this range conservatively: " if row["conservative"]
                           else "This information preserves the task goal through ") + ", ".join(sorted(row["rules"])) + "."})
        if barriers:
            refs = sorted({barrier_diagnostic(engine, barrier, ir, operation) for barrier in barriers})
            ranges.append({"status": "unresolved", "property": "value", "path": [], "excluded_paths": [],
                "demand_refs": [], "diagnostic_refs": refs, "contract_refs": contracts,
                "reason": " ".join(barrier_reason(barrier) for barrier in barriers)})
            results.append(assessment)
            continue
        if limits or state != "processed":
            ranges.append({"status": "unresolved", "property": "value", "path": [], "excluded_paths": [],
                "demand_refs": [], "diagnostic_refs": sorted(limits), "contract_refs": contracts,
                "reason": "Input coverage is blocked by the referenced material diagnostics; coverage state: " + state + "."})
            results.append(assessment)
            continue
        # Explicit exclusions, observed member paths and the complement of all
        # retained ranges provide finite candidates without inventing fields.
        retained = {_id("path_", _range(row)["path"]): _range(row)["path"] for _, row in demands}
        candidates = {canonical_sha256([]): []}
        for path in _known_paths(engine.index.data, node["data_ids"]):
            candidates[canonical_sha256(path)] = path
        for data_id in node["data_ids"]:
            candidates.update(declared_paths.get(data_id, {}))
        for _, row in demands:
            for path in _range(row)["excluded_paths"]:
                candidates[canonical_sha256(path)] = path
        for path in candidates.values():
            signal = {"property": "value", "path": path, "excluded_paths": []}
            if any(demand_overlap(signal, row) != "none" for _, row in demands):
                continue
            preserved, preservation_reasons = preservation(node, path)
            if not preserved:
                ranges.append({"status": "unresolved", **signal, "demand_refs": [], "diagnostic_refs": [],
                    "contract_refs": contracts, "reason": " ".join(preservation_reasons)})
                continue
            ranges.append({"status": "deletable", **signal, "demand_refs": [], "diagnostic_refs": [],
                "contract_refs": contracts, "reason": "No task-preservation demand covers this range; applicable declared constraints are preserved."
                + (" This is an acquired-result use assessment; the interface has not established support for narrower retrieval."
                   if kind == "op_output" else "")})
        if demands and [] not in retained.values():
            excluded = [retained[key] for key in sorted(retained)]
            # A complement can be represented even when an opaque record does
            # not enumerate its unrelated fields. Check concrete exclusions on
            # demand; constraints require explicit path-level witnesses.
            preserved, preservation_reasons = preservation(node, [])
            if preserved:
                ranges.append({"status": "deletable", "property": "value", "path": [], "excluded_paths": excluded,
                    "demand_refs": [], "diagnostic_refs": [], "contract_refs": contracts,
                    "reason": "The remainder outside every retained information range has no task demand; constraints permit the broader input-content reduction."
                    + (" This does not establish that the acquisition interface supports field projection."
                       if kind == "op_output" else "")})
            else:
                accounted = excluded + [row["path"] for row in ranges if row["path"] and not row["excluded_paths"]]
                accounted = [value for _, value in sorted({canonical_sha256(p): p for p in accounted}.items())]
                if not _closed_remainder(engine.index.data, node["data_ids"], accounted):
                    ranges.append({"status": "unresolved", "property": "value", "path": [], "excluded_paths": accounted,
                        "demand_refs": [], "diagnostic_refs": [], "contract_refs": contracts,
                        "reason": "The unenumerated remainder has no collective constraint-preservation rule. Concrete field checks remain separate. "
                                  + " ".join(preservation_reasons)})
        results.append(assessment)
        if kind != "op_output":
            for row in ranges:
                if row["status"] == "deletable":
                    value = {"kind": "excessive_input", "instruction_id": ir, "operation_id": operation,
                        "input_index": slot, "path": row["path"], "excluded_paths": row["excluded_paths"], "assessment_refs": [assessment["id"]],
                        "diagnostic_refs": [], "reason": row["reason"]}
                    findings.append({"id": _id("input_finding_", [value, row["excluded_paths"]]), **value})
    for diagnostic in engine.diagnostics.values():
        if diagnostic["code"] in {"expected_relation_mismatch", "expected_relation_projection", "excluded_requirement", "input_contract_missing_input", "input_contract_wrong_input"}:
            value = {"kind": "missing_input" if diagnostic["code"] in {"excluded_requirement", "input_contract_missing_input"} else "wrong_input",
                "instruction_id": diagnostic["instruction_id"], "operation_id": diagnostic["operation_id"],
                "input_index": None, "path": [], "excluded_paths": [], "assessment_refs": [],
                "diagnostic_refs": [diagnostic["id"]], "reason": diagnostic["reason"]}
            findings.append({"id": _id("input_finding_", value), **value})
    for finding in findings:
        finding.update(origin="demand_analysis", source_review_refs=[], source_finding=None)
    findings.extend(source_input_semantic_findings(engine, results))
    engine.input_location_builder = builder
    builder.enrich(results)
    return sorted(results, key=lambda r: r["id"]), sorted(findings, key=lambda r: r["id"])


def source_input_semantic_findings(engine, assessments):
    """Known source errors survive even when the missing slot has no node."""
    index = getattr(engine, "source_input_mismatches", None)
    if index is None:
        from .source_input_findings import SourceInputMismatchIndex
        index = SourceInputMismatchIndex(engine.contracts.receipt)
    results = []
    for source in index.findings:
        placements = {(p["instruction_id"], tuple(p["raw_path"])) for p in source["operation_refs"]}
        actual_ops = {key for key, info in engine.ops.items()
                      if (info["position"]["instruction_id"], info["raw_op"]) in placements}
        actual = source["actual"]
        slot = actual.get("input_index")
        from .input_locations import use_suffix, record_use_suffix
        def same_use(assessment):
            if slot is None or assessment["operation_id"] not in actual_ops or assessment["node_kind"] != "op_input":
                return False
            info = engine.ops[assessment["operation_id"]]
            return use_suffix(info["spec"], slot) == record_use_suffix(info["spec"], info["record"], assessment["input_index"])
        refs = sorted(a["id"] for a in assessments if a["operation_id"] in actual_ops
                      and same_use(a))
        diagnostics = sorted(d["id"] for d in engine.diagnostics.values()
                             if d["code"].startswith("input_contract_source_") and source["id"] in d["reason"])
        results.append({"id": source["id"], "kind": "wrong_input" if source["kind"] == "wrong_field" else "missing_input",
            "instruction_id": source["operation_refs"][0]["instruction_id"], "operation_id": None,
            "input_index": slot, "path": deepcopy(actual.get("path", [])), "excluded_paths": [],
            "assessment_refs": refs, "diagnostic_refs": diagnostics, "reason": source["reason"],
            "origin": "source_review", "source_review_refs": [source["id"]], "source_finding": deepcopy(source)})
    return results


def deletable_reduction(result, operation_id, input_index, data_id, path):
    """Locate an explicit completed assessment for this exact operation use."""
    refs = []
    whole = False
    for item in result.get("input_assessments", []):
        if (item["node_kind"] != "op_input" or item["operation_id"] != operation_id
            or item["input_index"] != input_index or data_id not in item["data_ids"] or item["coverage"] != "processed"):
            continue
        for row in item["ranges"]:
            if row["status"] != "deletable" or not covers(row["path"], path):
                continue
            if any(overlaps(excluded, path) for excluded in row["excluded_paths"]):
                continue
            refs.append(item["id"])
            whole = whole or not row["path"] and not row["excluded_paths"]
    if not refs:
        return None, []
    if not whole and (not path or type(path[-1]) is not str):
        # Removing an array member can reindex a later demanded member. The
        # information assessment does not supply that structural rewrite.
        return None, []
    return ({"kind": "remove_input"} if whole else {"kind": "exclude_field", "path": deepcopy(path)}), sorted(set(refs))
