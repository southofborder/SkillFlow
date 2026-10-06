"""Prepare exact review inputs and compiler-derived observations, without Data.

The reviewer sees original annotations once. Target indexes contain positions,
not another rendering of their contents. Observations are extracted directly
from the verified compiler mapping, never inferred from operation names.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from skillflow.common.source_evidence import json_pointer
from skillflow.common.source_evidence import resolve_pointer
from skillflow.common.recording import canonical_sha256
from skillflow.propagation.material import checked_material as checked_annotation_material
from skillflow.propagation.annotation.services import compile_response

from skillflow.propagation.review.models import SCHEMA_VERSION


def _target_index(raw: dict, instruction_ids: set[str]) -> list[dict]:
    targets: list[dict] = []

    def visit(value, path: list, ir_ids: list[str]) -> None:
        if not isinstance(value, (dict, list)):
            return
        # Evidence bodies remain readable in the original response. Their
        # containing claim, rather than each quote string, is the review target.
        targets.append({"id": f"ann_{len(targets) + 1:04d}", "kind": "annotation",
                        "pointer": json_pointer(*path), "instruction_ids": ir_ids})
        if path and path[-1] in ("evidences", "location_evidences"):
            return
        items = sorted(value.items()) if isinstance(value, dict) else enumerate(value)
        for key, child in items:
            child_ir_ids = ir_ids
            if len(path) == 1 and path[0] in ("profiles", "transfer_specs"):
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
    for ir_id, spec in compiled["transfer_specs"].items():
        def events(values, path):
            for index, event in enumerate(values):
                current = [*path, index]
                if event.get("kind") == "for_each":
                    events(event["body"], [*current, "body"])
                else:
                    effect_index = event["effect_index"]
                    if effect_index is not None and compiled["profiles"][ir_id]["effects"][effect_index] == "model_observe":
                        paths.add(json_pointer(*current))
        events(spec["events"], ["transfer_specs", ir_id, "events"])
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
        })
    if seen != expected:
        raise ValueError("compiler observation list is incomplete")
    return observations


def prepare_review_material(material: dict[str, Any], raw_annotation: dict[str, Any]) -> dict[str, Any]:
    """Validate and compile original inputs, then construct the one review view."""
    annotation_material = checked_annotation_material(material)
    raw, compiled, mapping = compile_response(raw_annotation, annotation_material)
    targets = _target_index(raw, set(annotation_material["instruction_index"]))
    observations = _observations(raw, compiled, mapping, targets)
    targets.extend({"id": item["id"], "kind": "observation", "pointer": json_pointer(index),
                    "instruction_ids": [item["instruction_id"]]}
                   for index, item in enumerate(observations))
    return {"schema_version": SCHEMA_VERSION, **deepcopy(annotation_material),
            "raw_annotation": raw, "observations": observations, "target_index": targets}


def checked_review_material(material: dict[str, Any]) -> dict[str, Any]:
    if type(material) is not dict or material.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported annotation review material version")
    annotation_material = {key: deepcopy(value) for key, value in material.items()
                           if key not in ("schema_version", "raw_annotation", "observations", "target_index")}
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
        collection = material["raw_annotation"] if item["kind"] == "annotation" else material["observations"]
        item["value"] = deepcopy(resolve_pointer(collection, item["pointer"]))
        resolved.append(item)
    return resolved
