"""Prepare exact review inputs and compiler-derived observations, without Data.

The reviewer sees original annotations once. Target indexes contain positions,
not another rendering of their contents. Observations are extracted directly
from the verified compiler mapping, never inferred from operation names.
"""

from __future__ import annotations
from skillflow.propagation.contracts.references import cfg_instructions

from copy import deepcopy
from typing import Any

from skillflow.common.source_evidence import json_pointer, nonempty_source_lines
from skillflow.common.source_evidence import resolve_pointer
from skillflow.common.recording import canonical_sha256
from skillflow.propagation.material import checked_material as checked_annotation_material
from skillflow.propagation.annotation.services import compile_response
from skillflow.propagation.contracts.paths import semantics_path

from skillflow.propagation.review.models import SCHEMA_VERSION

REVIEW_FIELDS = {"schema_version", "raw_annotation", "observations", "target_index", "declaration_index", "source_line_universe"}


def _target_index(raw: dict, instruction_ids: set[str]) -> list[dict]:
    targets: list[dict] = []

    def visit(value, path: list, ir_ids: list[str]) -> None:
        if not isinstance(value, (dict, list)):
            return
        # Evidence bodies remain readable in the original response. Their
        # containing claim, rather than each quote string, is the review target.
        targets.append({"id": f"ann_{len(targets) + 1:04d}", "kind": "annotation",
                        "pointer": json_pointer(*path), "instruction_ids": ir_ids})
        if path and path[-1] in ("evidences", "location_evidences", "operator_evidences", "empty_effect_evidences"):
            return
        items = sorted(value.items()) if isinstance(value, dict) else enumerate(value)
        for key, child in items:
            child_ir_ids = ir_ids
            if len(path) == 1 and path[0] == "ir_semantics":
                child_ir_ids = [key]
            elif len(path) == 1 and path[0] == "locations":
                child_ir_ids = sorted({item["instruction_id"] for item in child["operand_refs"]})
            if not set(child_ir_ids) <= instruction_ids:
                raise ValueError("review target has unknown instruction context")
            visit(child, [*path, key], child_ir_ids)

    visit(raw, [], [])
    return targets


def _compiled_observation_paths(compiled: dict) -> set[str]:
    paths: set[str] = set()
    for ir_id, spec in compiled["ir_semantics"].items():
        def events(values, path):
            for index, event in enumerate(values):
                current = [*path, index]
                if event.get("kind") == "for_each":
                    events(event["body"], [*current, "body"])
                else:
                    if event["effect"] == "model_observe":
                        paths.add(json_pointer(*current))
        events(spec["events"], semantics_path(ir_id, "events"))
    return paths


def _observations(raw: dict, compiled: dict, mapping: dict, targets: list[dict]) -> list[dict]:
    by_pointer = {item["pointer"]: item for item in targets}
    expected = _compiled_observation_paths(compiled)
    seen: set[str] = set()
    observations: list[dict] = []
    for item in mapping["events"]:
        if item["kind"] != "observation":
            continue
        pointer = json_pointer(*item["compiled_path"])
        if pointer not in expected or pointer in seen:
            raise ValueError("compiler observation mapping has duplicate or unexpected observation")
        seen.add(pointer)
        event = resolve_pointer(compiled, pointer)
        if len(event["atomic_ops"]) != 1 or event["atomic_ops"][0]["op"] != "deliver":
            raise ValueError("compiled observation does not contain one delivery")
        operation = event["atomic_ops"][0]
        boundary = compiled["locations"][operation["target"]]
        if boundary["kind"] != "model_context":
            raise ValueError("compiled observation is not directed to model context")
        raw_pointer = json_pointer(*item["raw_path"])
        if raw_pointer not in by_pointer:
            raise ValueError("compiler observation has no original annotation target")
        ancestors = [(item["raw_path"][:size], resolve_pointer(raw, json_pointer(*item["raw_path"][:size])))
                     for size in range(1, len(item["raw_path"]) + 1)]
        processing = [(path, value) for path, value in ancestors
                      if isinstance(value, dict) and value.get("kind") == "processing"]
        if len(processing) != 1 or processing[0][1]["mode"] != item["mode"]:
            raise ValueError("compiler observation processing segment is inconsistent")
        scopes = [by_pointer[json_pointer(*path)]["id"] for path, value in ancestors
                  if isinstance(value, dict) and value.get("kind") == "for_each"]
        observations.append({
            "id": f"obs_{len(observations) + 1:04d}",
            "instruction_id": item["instruction_id"],
            "mode": item["mode"],
            "values": deepcopy(operation["inputs"]),
            "target": {"kind": boundary["kind"], "name": boundary["name"]},
            "raw_target_id": by_pointer[raw_pointer]["id"],
            "processing_target_id": by_pointer[json_pointer(*processing[0][0])]["id"],
            "scope_target_ids": scopes,
            **({"when": deepcopy(operation["when"])} if operation.get("when") is not None else {}),
        })
    if seen != expected:
        raise ValueError("compiler observation list is incomplete")
    return observations


def prepare_review_material(material: dict[str, Any], raw_annotation: dict[str, Any]) -> dict[str, Any]:
    """Validate and compile original inputs, then construct the one review view."""
    annotation_material = checked_annotation_material(material)
    raw, compiled, mapping = compile_response(raw_annotation, annotation_material)
    targets = _target_index(raw, set(cfg_instructions(annotation_material["cfg"])))
    # The sealed Task is a separate object, never inserted into the annotation.
    def task_targets(value, path):
        if not isinstance(value, (dict, list)):
            return
        targets.append({"id": f"task_{len(targets) + 1:04d}", "kind": "task",
                        "pointer": json_pointer(*path), "instruction_ids": []})
        if path and path[-1] == "evidences":
            return
        items = sorted(value.items()) if isinstance(value, dict) else enumerate(value)
        for key, child in items:
            task_targets(child, [*path, key])
    task_targets(annotation_material["task"], [])
    observations = _observations(raw, compiled, mapping, targets)
    targets.extend({"id": item["id"], "kind": "observation", "pointer": json_pointer(index),
                    "instruction_ids": [item["instruction_id"]]}
                   for index, item in enumerate(observations))
    from skillflow.propagation.contracts.joint import joint_source_files
    universe = [{"file": file, "line": line}
                for file, line in sorted(nonempty_source_lines(joint_source_files(annotation_material)))]
    return {"schema_version": SCHEMA_VERSION, **deepcopy(annotation_material),
            "raw_annotation": raw, "observations": observations, "target_index": targets,
            "declaration_index": _declaration_index(annotation_material["cfg"], raw, compiled, mapping),
            "source_line_universe": universe}


def _declaration_index(cfg, raw, compiled, mapping):
    """Account for every demand and restriction without deriving execution facts."""
    from skillflow.propagation.contracts.demand_index import build_demand_target_index
    from skillflow.propagation.contracts.references import target_key
    targets = build_demand_target_index(cfg, raw)
    goals = {goal["id"]: goal for goal in compiled["demands"]}
    seen = set()
    result = []
    for item in mapping["goals"]:
        pointer, goal_id = item["raw_pointer"], item["goal_id"]
        if pointer in seen or goal_id not in goals:
            raise ValueError("compiler goal mapping has duplicate or unknown seed")
        seen.add(pointer)
        original, goal = resolve_pointer(raw, pointer), goals[goal_id]
        if original["requirement_id"] != goal["requirement_id"] or item["requirement_id"] != goal["requirement_id"]:
            raise ValueError("compiler goal mapping requirement differs")
        if item["target"] != goal["target"]:
            raise ValueError("compiler goal mapping target differs")
        target = targets[target_key(goal["target"])]
        resolved = {key: deepcopy(target[key]) for key in (
            "domain", "kind", "instruction_id", "pointer", "slot", "ref", "role", "when",
            "member_index", "scope_path", "operation_raw_path", "available_locals") if key in target}
        if target["domain"] == "cfg":
            resolved["value"] = deepcopy(target["value"])
        elif target["kind"] == "operation":
            resolved["op"] = target["value"]["op"]
            resolved["declared_refs"] = deepcopy(target.get("declared_refs", []))
            if "output" in target["value"]:
                resolved["output"] = target["value"]["output"]
        result.append({"kind": "demand", **deepcopy(item), "goal": deepcopy(goal), "resolved_target": resolved})
    if {item["goal_id"] for item in result} != set(goals) or len(result) != len(goals):
        raise ValueError("compiler goal mapping is incomplete")
    expected = {
        json_pointer("realizations", row_index, "constraints", constraint_index): row["requirement_id"]
        for row_index, row in enumerate(raw["realizations"])
        for constraint_index, _ in enumerate(row.get("constraints", []))
    }
    constraint_ids = set()
    constraint_pointers = set()
    for item in mapping["constraints"]:
        pointer = item["raw_pointer"]
        if pointer not in expected or pointer in constraint_pointers or item["constraint_id"] in constraint_ids:
            raise ValueError("compiler constraint mapping has duplicate or unknown declaration")
        if item["requirement_id"] != expected[pointer]:
            raise ValueError("compiler constraint mapping requirement differs")
        constraint_ids.add(item["constraint_id"])
        constraint_pointers.add(pointer)
        # The declaration is already present once in raw_annotation; only its
        # checked coordinate/identity belongs in this accounting index.
        result.append({"kind": "constraint", **deepcopy(item)})
    if constraint_pointers != set(expected):
        raise ValueError("compiler constraint mapping is incomplete")
    return result


def checked_review_material(material: dict[str, Any]) -> dict[str, Any]:
    if type(material) is not dict or material.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported annotation review material version")
    annotation_material = {key: deepcopy(value) for key, value in material.items()
                           if key not in REVIEW_FIELDS}
    reconstructed = prepare_review_material(annotation_material, material["raw_annotation"])
    if canonical_sha256(reconstructed) != canonical_sha256(material):
        raise ValueError("review material indexes or compiled observations differ")
    return reconstructed


def resolve_targets(target_ids: list[str], material: dict[str, Any]) -> list[dict]:
    """Resolve model-selected IDs; pointers and values are always program owned."""
    indexes = {item["id"]: item for item in material["target_index"]}
    resolved = []
    for target_id in target_ids:
        if target_id not in indexes:
            raise ValueError(f"review target does not exist: {target_id}")
        item = deepcopy(indexes[target_id])
        collection = {"annotation": material["raw_annotation"], "task": material["task"],
                      "observation": material["observations"]}[item["kind"]]
        item["value"] = deepcopy(resolve_pointer(collection, item["pointer"]))
        resolved.append(item)
    return resolved
