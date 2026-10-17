"""Validated offline preparation of declared sensitivity and sink comparisons."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass

from skillflow.common.recording import canonical_sha256
from .material import _id, _Index
from .task_material import _read_object
from .demand_material import checked_demand_material, validate_demand_result
from .demand_index import build_demand_target_index
from .sensitivity_results import SensitivityResult, resolve_data_review


@dataclass(frozen=True)
class SensitivityReview:
    _result: dict
    _index: dict
    _demand: dict | None = None

    def to_dict(self):
        return deepcopy(self._result)

    def index_dict(self):
        return deepcopy(self._index)

    def demand_dict(self):
        """Expose the already computed demand for durable audit, not a re-solve."""
        if self._demand is None:
            raise ValueError("This sensitivity review has no computed demand material")
        return deepcopy(self._demand)


def _json(value):
    return value.model_dump(mode="json") if hasattr(value, "model_dump") else _read_object(value)


def joint_demands(annotation):
    """An internal solver argument, not another persisted model response."""
    compiled = annotation["compiled_annotation"]
    return {"goals": compiled["demands"], "expressions": compiled["expressions"]}


def build_sensitivity_index(annotation, sensitivity_candidate):
    """Deterministic candidate coordinates, separate from model acceptance."""
    from skillflow.propagation.contracts.sensitivity import SensitivityCandidate
    candidate = SensitivityCandidate.model_validate(_json(sensitivity_candidate)).model_dump(mode="json")
    result = {}
    for scope in candidate["scopes"]:
        for index, declaration in enumerate(scope["declarations"]):
            location = {"instruction_id": scope["instruction_id"],
                        "scope_path": deepcopy(scope["scope_path"]), "declaration_index": index}
            identity = _id("declaration_", location)
            if identity in result:
                raise ValueError("Duplicate sensitivity declaration coordinate")
            result[identity] = {**location, "declaration": deepcopy(declaration)}
    return {"declarations": result}


def prepare_sensitivity_review(facts, task=None, annotation=None, demand_candidate=None,
                               sensitivity_candidate=None, *, queue_order="fifo"):
    """Apply one deterministic engine to joint or explicit offline declarations.

    An independent candidate is a separately authored, validated input. It is
    never relabelled as the accepted model response. With omitted candidates,
    the current compiled joint semantics supply Task, demand and sensitivity.
    """
    from skillflow.propagation.contracts.demand import validate_demand_candidate
    from skillflow.propagation.contracts.sensitivity import validate_sensitivity_candidate, extract_sensitivity_candidate
    from skillflow.propagation.contracts.joint import joint_source_files
    from .demand_engine import DemandEngine
    from .sensitivity_engine import SensitivityEngine
    if annotation is None:
        raise ValueError("Sensitivity review requires checked annotation and compilation materials")
    if task is None:
        task = annotation["task"]
    if demand_candidate is None:
        demand_candidate = joint_demands(annotation)
    if sensitivity_candidate is None:
        sensitivity_candidate = extract_sensitivity_candidate(annotation["raw_annotation"])
    facts, task, annotation, files = checked_demand_material(facts, task, annotation)
    targets = build_demand_target_index(facts.cfg, annotation["raw_annotation"])
    demands = validate_demand_candidate(_json(demand_candidate), task=task, source_files=files, targets=targets)
    sensitivity = validate_sensitivity_candidate(_json(sensitivity_candidate), cfg=facts.cfg,
        raw=annotation["raw_annotation"], source_files=files)
    sensitivity = _json(sensitivity)
    index = build_sensitivity_index(annotation, sensitivity)
    engine = DemandEngine(facts, task, annotation, demands.model_dump(mode="json"), targets)
    demand_result = engine.solve(queue_order=queue_order)
    validate_demand_result(demand_result)
    result = SensitivityEngine(engine, demand_result, index["declarations"]).solve()
    validate_sensitivity_result(result, facts, task, annotation, demands, sensitivity, demand_result=demand_result)
    return SensitivityReview(deepcopy(result), index, deepcopy(demand_result))


def prepare_joint_sensitivity_review(facts, annotation, *, queue_order="fifo"):
    return prepare_sensitivity_review(facts, annotation=annotation, queue_order=queue_order)


def validate_sensitivity_result(result, facts=None, task=None, annotation=None,
                                demand_candidate=None, sensitivity_candidate=None, *, demand_result=None):
    """Strict stored-result and reference checks; this does not re-run inference."""
    from skillflow.propagation.conditions import payload_input_indices
    from skillflow.propagation.contracts.sensitivity import validate_sensitivity_candidate
    from skillflow.propagation.contracts.joint import joint_source_files
    from skillflow.propagation.contracts.demand import validate_demand_candidate
    from skillflow.propagation.contracts.task import Task, task_source_files
    value = SensitivityResult.model_validate(result).model_dump(mode="json")
    if facts is not None and demand_result is None:
        raise ValueError("Verified demand result is required for sensitivity material validation")
    expected_demand = validate_demand_result(demand_result) if demand_result is not None else None
    if expected_demand is not None and facts is not None and annotation is not None:
        from .demand_results import validate_result_references
        validate_result_references(expected_demand, facts,
            build_demand_target_index(facts.cfg, annotation["raw_annotation"]))
    expected_comparisons = {sink["id"]: sink for sink in expected_demand["sinks"]} if expected_demand is not None else None
    sensitivity = value["derivations"]["sensitivity"]
    demand = value["derivations"]["demand"]
    diagnostics = {d["id"]: d for d in value["diagnostics"]}
    if len(diagnostics) != len(value["diagnostics"]):
        raise ValueError("Duplicate sensitivity diagnostic")
    for records in (sensitivity, demand):
        for identity, row in records.items():
            if not set(row["parents"]) <= records.keys() or identity in row["parents"]:
                raise ValueError("Invalid sensitivity review derivation reference")
    for identity, row in sensitivity.items():
        signal = {k: row[k] for k in ("declaration_id", "label", "property", "path", "excluded_paths", "relation")}
        if identity != _id("sensitivity_", [row["data_id"], signal]):
            raise ValueError("Sensitivity derivation identity differs")
    index = _Index(facts) if facts is not None else None
    if facts is not None and annotation is not None and sensitivity_candidate is not None:
        source_files = joint_source_files(annotation["material"])
        validate_sensitivity_candidate(_json(sensitivity_candidate), facts.cfg, annotation["raw_annotation"], source_files)
        if task is not None and demand_candidate is not None:
            task = task if isinstance(task, Task) else Task.model_validate(task)
            task_files = source_files
            parsed_demand = validate_demand_candidate(_json(demand_candidate), task=task, source_files=task_files,
                targets=build_demand_target_index(facts.cfg, annotation["raw_annotation"]))
            if expected_demand is not None and expected_demand["goals"] != parsed_demand.model_dump(mode="json")["goals"]:
                raise ValueError("Verified demand result goals differ from candidate")
            requirements = {row.id for row in task.requirements}
            if any(d["requirement_id"] not in requirements for d in demand.values()):
                raise ValueError("Sensitivity demand refers to an absent task requirement")
    declarations = build_sensitivity_index(annotation, sensitivity_candidate)["declarations"] if sensitivity_candidate is not None else None
    if declarations is not None:
        if value["coverage"]["declarations"] != len(declarations):
            raise ValueError("Sensitivity declaration coverage differs")
        if any(d["declaration_id"] not in declarations for d in sensitivity.values()):
            raise ValueError("Unknown sensitivity declaration")
        scopes = {canonical_sha256([row["instruction_id"], row["scope_path"]]) for row in declarations.values()}
        if value["coverage"]["declared_scopes"] != len(scopes):
            raise ValueError("Sensitivity scope coverage differs")
        for row in sensitivity.values():
            declaration = declarations[row["declaration_id"]]["declaration"]
            if row["label"] != declaration["label"] or row["property"] != declaration.get("property", "value"):
                raise ValueError("Sensitivity derivation changes the declared property or label")
            if index is not None and row["data_id"] not in index.data:
                raise ValueError("Sensitivity derivation references absent Data")
    sink_ids, review_ids, expected_review_ids, required_demands = set(), set(), set(), set()
    expected = {_id("sink_", b): b for b in facts.sinks} if facts is not None else None
    for sink in value["sinks"]:
        if sink["id"] in sink_ids:
            raise ValueError("Duplicate sensitivity sink")
        sink_ids.add(sink["id"])
        if not set(sink["limitations"]) <= diagnostics.keys():
            raise ValueError("Unknown sink sensitivity limitation")
        if expected is not None and expected.get(sink["id"]) != sink["boundary"]:
            raise ValueError("Sensitivity boundary differs from frozen facts")
        base = expected_comparisons.get(sink["id"]) if expected_comparisons is not None else None
        if expected_comparisons is not None:
            if base is None or any(sink[k] != base[k] for k in ("boundary", "actual_payload", "related_requirements")):
                raise ValueError("Sensitivity sink differs from verified demand comparison")
            if not set(base["limitations"]) <= set(sink["limitations"]):
                raise ValueError("Sensitivity sink drops a verified demand limitation")
        operations = {p["operation_id"] for p in sink["actual_payload"]}
        if index is not None and operations != set(index.sink_operations(sink["boundary"])):
            raise ValueError("Sensitivity sink instance coverage differs")
        if index is not None and base is not None:
            sliced = index.slice(sink["boundary"])
            relevant = set(sliced["usage_context"]["instructions"])
            relevant.update(index.operations[key]["position"]["instruction_id"] for key in sliced["backward_slice"]["operations"])
            limits = sorted(set(base["limitations"]) | {identity for identity, diagnostic in diagnostics.items()
                if diagnostic["blocking"] and (diagnostic["instruction_id"] is None or diagnostic["instruction_id"] in relevant)})
            if sink["limitations"] != limits:
                raise ValueError("Sensitivity sink changes relevant saved analysis limitations")
        if index is not None:
            from skillflow.propagation.conditions import payload_inputs
            for payload in sink["actual_payload"]:
                operation = index.operations[payload["operation_id"]]
                if payload["position"] != operation["position"] or payload["inputs"] != payload_inputs(operation["record"]):
                    raise ValueError("Sensitivity actual payload differs from frozen facts")
                from .sensitivity_engine import dominates
                for slot in payload_input_indices(operation["record"]):
                    for data_id in operation["record"]["inputs"][slot]:
                        candidates = {identity: row for identity, row in sensitivity.items() if row["data_id"] == data_id}
                        for identity, row in candidates.items():
                            if any(other != identity and dominates(other_row, row)
                                   and (not dominates(row, other_row) or other < identity)
                                   for other, other_row in candidates.items()):
                                continue
                            expected_review_ids.add(_id("data_review_", [sink["id"], payload["operation_id"], slot, identity]))
        for compact_review in sink["data_reviews"]:
            review = resolve_data_review(compact_review, sink, sensitivity)
            if review["id"] in review_ids:
                raise ValueError("Duplicate sensitivity data review")
            review_ids.add(review["id"])
            if review["id"] != _id("data_review_", [sink["id"], review["operation_id"], review["input_index"], review["derivation_id"]]):
                raise ValueError("Sensitivity review identity differs")
            if review["derivation_id"] not in sensitivity or not set(review["demand_refs"]) <= demand.keys():
                raise ValueError("Dangling sensitivity review derivation")
            row = sensitivity[review["derivation_id"]]
            if base is not None:
                required = sorted(identity for identity in [*base["demanded_information"], *base["conservative_retention"]]
                    if expected_demand["derivations"][identity]["node"]["kind"] == "op_input"
                    and expected_demand["derivations"][identity]["node"]["operation_id"] == review["operation_id"]
                    and expected_demand["derivations"][identity]["node"]["slot"] == review["input_index"])
                if review["demand_refs"] != required:
                    raise ValueError("Sensitivity review omits or changes its complete verified demand set")
                required_demands.update(required)
            if review["operation_id"] not in operations:
                raise ValueError("Sensitivity review operation differs from sink")
            if index is not None:
                record = index.operations[review["operation_id"]]["record"]
                slot = review["input_index"]
                if slot not in payload_input_indices(record) or review["data_id"] not in record["inputs"][slot]:
                    raise ValueError("Sensitivity data is not a payload candidate at this slot")
                if any(demand[k]["node"]["operation_id"] != review["operation_id"]
                       or demand[k]["node"]["slot"] != slot for k in review["demand_refs"]):
                    raise ValueError("Sensitivity demand belongs to another receiver or parameter")
            from .sensitivity_engine import SensitivityEngine
            expected_conclusion = SensitivityEngine._compare(row,
                [(identity, demand[identity]) for identity in review["demand_refs"]], review["limitations"])[0]
            if review["conclusion"] != expected_conclusion:
                raise ValueError("Sensitivity conclusion differs from the supported comparison rule")
            if review["conclusion"] == "excess_supported":
                if review["relation"] != "direct" or review["property"] != "value" or not review["path"] or review["excluded_paths"] or review["limitations"] or not review["demand_refs"]:
                    raise ValueError("Unsupported excess conclusion lacks a direct, constrained field range")
                from .sensitivity_engine import demand_overlap
                if any(demand_overlap(row, demand[k]) != "none" for k in review["demand_refs"]):
                    raise ValueError("Supported excess overlaps a preservation demand")
                if type(review["path"][-1]) is not str or review["reduction"] != {"kind": "exclude_field", "path": review["path"]}:
                    raise ValueError("Supported excess lacks its precise field reduction")
            elif review["reduction"] is not None:
                raise ValueError("A non-supported conclusion cannot propose a certified reduction")
    if expected is not None and sink_ids != expected.keys():
        raise ValueError("Sensitivity review does not cover every actual sink")
    if index is not None and review_ids != expected_review_ids:
        raise ValueError("Sensitivity review omits or adds a tracked payload range")
    if expected_demand is not None:
        if sink_ids != expected_comparisons.keys():
            raise ValueError("Sensitivity sink coverage differs from verified demand result")
        pending = list(required_demands)
        while pending:
            for parent in expected_demand["derivations"][pending.pop()]["parents"]:
                if parent not in required_demands:
                    required_demands.add(parent)
                    pending.append(parent)
        if demand != {identity: expected_demand["derivations"][identity] for identity in sorted(required_demands)}:
            raise ValueError("Sensitivity demand derivation closure differs from verified demand result")
        for diagnostic in expected_demand["diagnostics"]:
            projection = {k: diagnostic[k] for k in ("id", "code", "reason", "instruction_id", "operation_id", "blocking")}
            if diagnostics.get(diagnostic["id"]) != projection:
                raise ValueError("Sensitivity result drops or changes a verified demand diagnostic")
        if value["coverage"]["demand_status"] != expected_demand["status"]:
            raise ValueError("Sensitivity demand status differs from verified result")
    coverage = value["coverage"]
    if coverage["sinks"] != len(sink_ids) or coverage["resolved_declarations"] > coverage["declarations"]:
        raise ValueError("Invalid sensitivity coverage")
    if coverage["expected_sinks"] != len(sink_ids):
        raise ValueError("Sensitivity sink count differs")
    if value["status"] == "complete" and (coverage["demand_status"] != "complete" or
        coverage["resolved_declarations"] != coverage["declarations"] or any(d["blocking"] for d in diagnostics.values())):
        raise ValueError("Incomplete sensitivity material cannot be complete")
    return deepcopy(value)
