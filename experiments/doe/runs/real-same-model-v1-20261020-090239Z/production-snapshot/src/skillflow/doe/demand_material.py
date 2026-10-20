"""Offline task-driven demand preparation; not an irreplacability or DOE verdict."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass

from skillflow.common.recording import canonical_sha256
from skillflow.propagation.annotation.services import compile_response
from skillflow.propagation.contracts.task import Task, task_source_files, checked_task
from skillflow.propagation.loading import PropagationMaterials
from .task_material import _read_object


@dataclass(frozen=True)
class DemandReview:
    """Copies keep review clients from changing an already prepared result."""

    _result: dict
    _index: dict

    def to_dict(self):
        return deepcopy(self._result)

    def index_dict(self):
        return deepcopy(self._index)


def validate_record_spec_structure(facts, compiled):
    """Bind every resolved step to its compiled occurrence, including non-sinks.

    This checks recorded structure, not operation execution or demand semantics.
    Empty/partial propagation may lack an IR record, but a present IR record may
    not omit, insert or reorder effect stages or their abstract operations.
    """
    def effect_event(record, event, label):
        if record.get("kind") == "for_each":
            raise ValueError("Demand record event type differs from compiled specification: " + label)
        if record["effect"] != event["effect"]:
            raise ValueError("Demand record effect differs from compiled specification: " + label)
        if len(record["atomic_ops"]) != len(event["atomic_ops"]):
            raise ValueError("Demand record operation coverage differs from compiled specification: " + label)
        for actual, specification in zip(record["atomic_ops"], event["atomic_ops"]):
            if actual["op"] != specification["op"]:
                raise ValueError("Demand record operation kind differs from compiled specification: " + label)

    for ir, record in facts.records.items():
        spec = compiled["ir_semantics"][ir]
        if record["order"] != spec["order"] or record["precedence"] != spec["precedence"]:
            raise ValueError("Demand record order or precedence differs from compiled specification: " + ir)
        if len(record["events"]) != len(spec["events"]):
            raise ValueError("Demand record event coverage differs from compiled specification: " + ir)
        for index, (actual, event) in enumerate(zip(record["events"], spec["events"])):
            label = ir + "/events/" + str(index)
            if event.get("kind") != "for_each":
                effect_event(actual, event, label)
                continue
            if actual.get("kind") != "for_each":
                raise ValueError("Demand record event type differs from compiled specification: " + label)
            for instance_index, instance in enumerate(actual["instances"]):
                if len(instance["body"]) != len(event["body"]):
                    raise ValueError("Demand record foreach body coverage differs from compiled specification: " + label)
                for body_index, (body, body_spec) in enumerate(zip(instance["body"], event["body"])):
                    effect_event(body, body_spec,
                        label + "/instances/" + str(instance_index) + "/body/" + str(body_index))


def checked_demand_material(facts, task, annotation):
    """Validate components, source claims and compilation without a handoff JSON."""
    if not isinstance(facts, PropagationMaterials):
        raise TypeError("Demand analysis requires verified propagation materials")
    task_value = task.model_dump(mode="json") if isinstance(task, Task) else _read_object(task)
    parsed = Task.model_validate(task_value)
    from skillflow.propagation.contracts.joint import joint_source_files
    files = joint_source_files(annotation["material"])
    if ({k: v for k, v in files.items() if k.startswith("skill/")}
            != task_source_files(facts.source)):
        raise ValueError("Demand annotation source differs from frozen facts")
    material = annotation["material"]
    checked_task(task_value, source_files=files,
                 source_sha256=material["source"]["source_sha256"])
    if task_value != annotation["task"] or task_value != material["task"]:
        raise ValueError("Demand Task differs from its sealed annotation revision")
    if material != facts.annotation["material"]:
        raise ValueError("Demand annotation source, CFG, request or runtime contract differs")
    raw, compiled, mapping = compile_response(annotation["raw_annotation"], material)
    if compiled != annotation["compiled_annotation"] or mapping != annotation["mapping"]:
        raise ValueError("Demand annotation compilation or mapping differs")
    if annotation != facts.annotation:
        raise ValueError("Demand annotation differs from the verified propagation candidate")
    declared = {canonical_sha256(b) for b in compiled["sink_boundaries"]}
    if any(canonical_sha256(b) not in declared for b in facts.sinks):
        raise ValueError("Demand sink boundary differs from compiled annotation")
    validate_record_spec_structure(facts, compiled)
    return facts, parsed, {**annotation, "raw_annotation": raw, "compiled_annotation": compiled,
                           "mapping": mapping}, files


def prepare_demand_review(facts, task, annotation, candidate, *, queue_order="fifo") -> DemandReview:
    """Compute supported preservation demands, without API calls or input edits.

    queue_order is a deterministic verification hook, not a change in semantics.
    """
    from .demand_index import build_demand_target_index
    from skillflow.propagation.contracts.demand import validate_demand_candidate
    from .demand_engine import DemandEngine
    facts, task, annotation, files = checked_demand_material(facts, task, annotation)
    targets = build_demand_target_index(facts.cfg, annotation["raw_annotation"])
    candidate = candidate.model_dump(mode="json") if hasattr(candidate, "model_dump") else _read_object(candidate)
    parsed = validate_demand_candidate(candidate, task=task, source_files=files, targets=targets)
    engine = DemandEngine(facts, task, annotation, parsed.model_dump(mode="json"), targets)
    result = engine.solve(queue_order=queue_order)
    validate_demand_result(result)
    from .demand_results import validate_result_references
    validate_result_references(result, facts, targets)
    return DemandReview(deepcopy(result), {"targets": deepcopy(targets)})


def validate_demand_result(result):
    """Validate a stored business result; recomputation is the replay's job."""
    from .demand_results import validate_result_shape
    result = validate_result_shape(result)
    if set(result) != {"schema_version", "status", "goals", "derivations", "sinks", "diagnostics", "coverage", "traceability"}:
        raise ValueError("Demand result fields differ")
    if result["schema_version"] != "skillflow-demand-v4" or result["status"] not in {"complete", "partial"}:
        raise ValueError("Unsupported demand result version or status")
    if not isinstance(result["derivations"], dict) or not isinstance(result["sinks"], list):
        raise ValueError("Invalid demand collections")
    derivations = result["derivations"]
    for key, item in derivations.items():
        if not set(item.get("parents", [])) <= derivations.keys() or key in item.get("parents", []):
            raise ValueError("Invalid demand derivation reference")
    ids = [s["id"] for s in result["sinks"]]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate sink review")
    diagnostic_ids = {d["id"] for d in result["diagnostics"]}
    if len(diagnostic_ids) != len(result["diagnostics"]):
        raise ValueError("Duplicate demand diagnostic")
    for sink in result["sinks"]:
        for field in ("demanded_information", "conservative_retention"):
            if not set(sink[field]) <= derivations.keys():
                raise ValueError("Dangling sink demand")
        if not set(sink["limitations"]) <= diagnostic_ids:
            raise ValueError("Dangling sink limitation")
    return deepcopy(result)
