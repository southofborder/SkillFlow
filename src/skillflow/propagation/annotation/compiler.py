"""Compile declared processing modes into ordered model-visibility events.

No opcode, predicate or inference prose is interpreted. This establishes the
implications of supplied typed modes, not their semantic correctness.
"""
from __future__ import annotations

from copy import deepcopy
from contextlib import contextmanager

from pydantic import ValidationError

from skillflow.common.validation import StructuralValidationError, structural_error
from skillflow.common.source_evidence import json_pointer

from skillflow.propagation.contracts.compatibility import TRANSFORM_OPERATIONS
from skillflow.propagation.contracts.compatibility import INTERACTION_EFFECTS
from skillflow.propagation.contracts.specs import ProcessingSpec
from skillflow.propagation.contracts.specs import ReadOp
from skillflow.propagation.contracts.specs import ReceiveOp
from skillflow.propagation.contracts.specs import LocalRef
from skillflow.propagation.contracts.specs import AlternativesRef
from skillflow.propagation.contracts.specs import _validate_ref
from skillflow.propagation.contracts.specs import IRTransferSpec, IRSemantics, _has_effect
from skillflow.propagation.contracts.paths import semantics_path, split_semantics_path
from skillflow.propagation.contracts.specs import structural_precedence
from skillflow.propagation.contracts.specs import position_value
from skillflow.propagation.contracts.specs import compiled_operation
from skillflow.propagation.contracts.joint import normalize_joint_semantics, goal_mapping
from skillflow.propagation.contracts.uses import value_uses
from skillflow.propagation.contracts.uses import request_precedence
from skillflow.common.recording import canonical_sha256
from skillflow.propagation.contracts.runtime_contract import runtime_contract_binding
from skillflow.propagation.material import checked_material
from skillflow.propagation.contracts.profiles import RawAnnotationResponse
from skillflow.propagation.contracts.boundaries import derive_sink_boundaries

COMPILER_VERSION = "skillflow-processing-compiler-v8"


class InternalCompilationError(RuntimeError):
    """A generated artifact violated an invariant after candidate validation."""


@contextmanager
def _generated_artifact(stage):
    """Generated invariant failures must never request another model response."""
    try:
        yield
    except (StructuralValidationError, ValidationError) as error:
        raise InternalCompilationError(f"Generated {stage} failed validation: {error}") from error


def compile_response(raw, material):
    """Return (validated raw response, compiled response, deterministic mapping)."""
    from skillflow.propagation.annotation.services import validate_raw_response
    from skillflow.propagation.annotation.services import validate_compiled_response
    material = checked_material(material)
    raw = validate_raw_response(raw, material)
    parsed = RawAnnotationResponse.model_validate(raw)
    compiled = deepcopy(raw)
    normalized = normalize_joint_semantics(raw, material)
    compiled.pop("task_revision_id")
    compiled.update(normalized)
    compiled["ir_semantics"] = {}
    mapping = {"schema_version": "skillflow-processing-compilation-v8",
               "compiler_version": COMPILER_VERSION,
               "runtime_contract": runtime_contract_binding(material["runtime_contract"]),
               "events": [], "goals": goal_mapping(raw, normalized)}
    rules = {rule["id"]: rule["text"] for rule in material["runtime_contract"]["rules"]}
    mechanism = {"rule_id": "EM10",
                 "reason": "The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred."}
    boundary_evidence = {"rule_id": "EM12",
                         "reason": "The program-generated model boundary uses recipient; unmodeled retention stays null and does not assert that the service retains nothing."}
    model_location = None

    def context_location():
        nonlocal model_location
        if model_location is not None:
            return model_location
        identities = [(key, location) for key, location in compiled["locations"].items()
                      if location["kind"] == "model_context" and location["name"] == "Current model processing context"]
        if identities:
            model_location = identities[0][0]
            existing = identities[0][1]
            if existing["access_scope"] != "recipient" or existing["retention"] is not None:
                raise structural_error("compiled_location_conflict", json_pointer("locations", model_location),
                                       "compiled model location boundary attributes conflict with recipient/null")
        else:
            model_location = "__compiled_model_context__"
            if model_location in compiled["locations"]:
                raise structural_error("reserved_location", json_pointer("locations", model_location),
                                       "reserved compiled model location conflicts with a supplied location")
            compiled["locations"][model_location] = {
                "kind": "model_context", "name": "Current model processing context", "operand_refs": [],
                "access_scope": "recipient", "retention": None}
            compiled["location_evidences"][model_location] = [deepcopy(mechanism), deepcopy(boundary_evidence)]
        return model_location

    instructions = {ir["id"]: ir for block in material["cfg"]["blocks"].values() for ir in block["instructions"]}
    for ir_id, spec in parsed.ir_semantics.items():
        original = raw["ir_semantics"][ir_id]
        output_events = []
        known = {}
        causal_edges = set()

        def emit(target, event_path, ops, effect, original_event, raw_path, operation_range,
                 kind, mode, additional_evidence=None):
            evidences = []
            if effect is not None:
                if additional_evidence is not None:
                    evidences = additional_evidence
                elif original_event is not None and effect == original_event.effect:
                    evidences = [item.model_dump(mode="json") for item in original_event.evidences]
                else:
                    evidences = [item for op in ops for item in op["evidences"]]
            event_value = {"effect": effect, "atomic_ops": deepcopy(ops)}
            if effect is not None:
                event_value["evidences"] = deepcopy(evidences)
            target.append(event_value)
            mapping["events"].append({"instruction_id": ir_id, "raw_path": raw_path,
                                      "raw_atomic_range": operation_range,
                                      "compiled_path": event_path + [len(target) - 1],
                                      "kind": kind, "mode": mode})

        def processing(segment, target, event_path, raw_path, available):
            if segment.mode == "model" and "llm" not in original["operator"]:
                raise structural_error("model_operator", json_pointer("ir_semantics", ir_id, "operator"),
                                       f"model processing requires llm operator: {ir_id}")
            segment_start = len(target)
            seen = set()
            local_defs = dict(available)
            produced_here = set()
            for event in segment.events:
                for op in event.atomic_ops:
                    name = getattr(op, "output", None)
                    if name is not None:
                        local_defs[name] = 0
                        produced_here.add(name)
            for ref in segment.returns:
                _validate_ref(ref, instructions[ir_id], local_defs, 1, uncertain=False)

            def observe(refs, path, bounds, when=None):
                values = []
                guard = (when.model_dump(mode="json") if hasattr(when, "model_dump") else when)
                guard_identity = None if guard is None else canonical_sha256(guard)
                for ref in refs:
                    value = ref.model_dump(mode="json") if hasattr(ref, "model_dump") else ref
                    identity = canonical_sha256(value)
                    pair = (identity, guard_identity)
                    # A conditional observation cannot erase a later
                    # unconditional one. An earlier unconditional observation
                    # already retains the value across all guard outcomes.
                    if (identity, None) not in seen and pair not in seen:
                        seen.add(pair)
                        values.append(deepcopy(value))
                if not values:
                    return
                evidence = [deepcopy(mechanism), *(item.model_dump(mode="json") for item in segment.evidences)]
                operation = {"op": "deliver", "inputs": values, "target": context_location(), "evidences": evidence}
                if guard is not None:
                    operation["when"] = deepcopy(guard)
                emit(target, event_path, [operation], "model_observe", None, path, bounds,
                     "observation", segment.mode, evidence)

            def external_reference(ref):
                # Intermediate values generated within this one processing
                # segment are not additional external model inputs. Actual
                # acquisitions are observed separately after read/receive.
                if isinstance(ref, LocalRef) and ref.name in produced_here:
                    return None
                if isinstance(ref, AlternativesRef):
                    items = [value for item in ref.items if (value := external_reference(item)) is not None]
                    return AlternativesRef(kind="alternatives", items=items) if items else None
                return ref

            for event_index, event in enumerate(segment.events):
                old_effect = event.effect
                path = raw_path + ["events", event_index]
                pending = []
                start = 0
                def flush(end):
                    nonlocal pending, start
                    if not pending:
                        return
                    whole = start == 0 and end == len(event.atomic_ops)
                    has_primary = any(op["op"] in INTERACTION_EFFECTS for op in pending)
                    effect = old_effect if whole or has_primary or old_effect is None else "transform"
                    emit(target, event_path, pending, effect, event, path, [start, end],
                         "retained" if whole else "slice", segment.mode)
                    pending = []
                for position, op in enumerate(event.atomic_ops):
                    should_observe = segment.mode == "model" or (
                        segment.mode == "default" and op.op in TRANSFORM_OPERATIONS)
                    if should_observe and not isinstance(op, (ReadOp, ReceiveOp)):
                        groups = {}
                        for use in value_uses(op):
                            value = external_reference(use.value)
                            if value is None:
                                continue
                            guard = use.when
                            guard_identity = None if guard is None else canonical_sha256(guard.model_dump(mode="json"))
                            identity = canonical_sha256(value.model_dump(mode="json"))
                            if (identity, None) in seen or (identity, guard_identity) in seen:
                                continue
                            group = groups.setdefault(guard_identity, (guard, []))
                            group[1].append(value)
                        if groups:
                            flush(position)
                            for guard, fresh in groups.values():
                                observe(fresh, path, [position, position + 1], when=guard)
                    if not pending:
                        start = position
                    pending.append(compiled_operation(op))
                    if segment.mode != "local" and isinstance(op, (ReadOp, ReceiveOp)):
                        flush(position + 1)
                        observe([{"kind": "local", "name": op.output}], path, [position, position + 1])
                flush(len(event.atomic_ops))
            if segment.mode == "local" and segment.returns:
                observe(segment.returns, raw_path + ["returns"], None)
            for event in segment.events:
                for op in event.atomic_ops:
                    output = getattr(op, "output", None)
                    if output is not None:
                        available[output] = -1
            # Preserve declared within-segment ordering and generated causal
            # edges at primitive-operation granularity. Different segments may
            # still interleave in partial-order evaluation.
            _, relative_path = split_semantics_path(event_path)
            is_body = len(relative_path) == 3 and relative_path[2] == "body"
            outer = relative_path[1] if is_body else None
            positions = [(outer if is_body else e, e if is_body else None, o)
                         for e in range(segment_start, len(target))
                         for o in range(len(target[e]["atomic_ops"]))]
            causal_edges.update(zip(positions, positions[1:]))

        for position, event in enumerate(spec.events):
            raw_path = semantics_path(ir_id, "events", position)
            if isinstance(event, ProcessingSpec):
                processing(event, output_events, semantics_path(ir_id, "events"), raw_path, known)
            else:
                body = []
                body_known = {**known, event.item: -1}
                index = len(output_events)
                for body_position, segment in enumerate(event.body):
                    processing(segment, body, semantics_path(ir_id, "events", index, "body"),
                               raw_path + ["body", body_position], body_known)
                output_events.append({"kind": "for_each", "collection": event.collection.model_dump(mode="json"),
                                      "item": event.item, "body": body,
                                      "sensitivity": [item.model_dump(mode="json") for item in event.sensitivity],
                                      "evidences": [item.model_dump(mode="json") for item in event.evidences]})
        result_spec = {"order": spec.order, "precedence": [],
            "sensitivity": [item.model_dump(mode="json") for item in spec.sensitivity],
            "events": output_events, "output_bindings": [item.model_dump(mode="json") for item in spec.output_bindings]}
        with _generated_artifact(f"transfer structure for {ir_id}"):
            typed = IRTransferSpec.model_validate(result_spec)
            causal_edges |= structural_precedence(typed)
            causal_edges |= request_precedence(typed)
        def coordinate(key):
            return (key[0], -1 if key[1] is None else key[1], key[2])
        result_spec["precedence"] = [{"before": position_value(before), "after": position_value(after)}
            for before, after in sorted(causal_edges, key=lambda pair: (coordinate(pair[0]), coordinate(pair[1])))]
        result_spec.update(operator=deepcopy(original["operator"]),
                           operator_evidences=deepcopy(original["operator_evidences"]))
        if not _has_effect(typed.events):
            result_spec["empty_effect_evidences"] = deepcopy(original["empty_effect_evidences"])
        with _generated_artifact(f"IR semantics for {ir_id}"):
            compiled["ir_semantics"][ir_id] = IRSemantics.model_validate(result_spec).model_dump(mode="json")
    with _generated_artifact("sink boundaries and final compiled response"):
        compiled["sink_boundaries"] = [boundary.model_dump(mode="json") for boundary in
            derive_sink_boundaries(compiled["locations"], compiled["ir_semantics"])]
        compiled = validate_compiled_response(compiled, material)
    mapping["raw_sha256"] = canonical_sha256(raw)
    mapping["compiled_sha256"] = canonical_sha256(compiled)
    return raw, compiled, mapping
