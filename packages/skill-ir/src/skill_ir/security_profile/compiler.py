"""Compile declared processing modes into ordered model-visibility events.

No opcode, predicate or inference prose is interpreted. This establishes the
implications of supplied typed modes, not their semantic correctness.
"""
from __future__ import annotations

from copy import deepcopy

from skill_ir.propagation.compatibility import TRANSFORM_OPERATIONS, INTERACTION_EFFECTS
from skill_ir.propagation.specs import (
    ProcessingSpec, ReadOp, ReceiveOp, LocalRef, AlternativesRef,
    _validate_ref, IRTransferSpec, structural_precedence, position_value,
)
from skill_ir.propagation.uses import value_uses, request_precedence
from skill_ir.recording import canonical_sha256
from skill_ir.runtime_contract import execution_model_binding
from .evidence import checked_material
from .models import RawAnnotationResponse
from .boundaries import derive_sink_boundaries

COMPILER_VERSION = "skillflow-processing-compiler-v4"


def compile_response(raw, material):
    """Return (validated raw response, compiled response, deterministic mapping)."""
    from .services import validate_raw_response, validate_compiled_response
    material = checked_material(material)
    raw = validate_raw_response(raw, material)
    parsed = RawAnnotationResponse.model_validate(raw)
    compiled = deepcopy(raw)
    compiled["transfer_specs"] = {}
    mapping = {"schema_version": "skillflow-processing-compilation-v4",
               "compiler_version": COMPILER_VERSION,
               "execution_model": execution_model_binding(material["execution_model"]),
               "events": []}
    rules = {rule["id"]: rule["text"] for rule in material["execution_model"]["rules"]}
    mechanism = {"basis": "execution_model", "ref_id": "EM10", "quote": rules["EM10"],
                 "reason": "程序按已声明处理模式及实际符号引用编译观察；不证明模式判断正确或真实执行已发生。"}
    boundary_evidence = {"basis": "execution_model", "ref_id": "EM12", "quote": rules["EM12"],
                         "reason": "程序生成的模型接收边界使用 recipient；未建模保存期限保持 null，不声明服务端不保存。"}
    model_location = None

    def context_location():
        nonlocal model_location
        if model_location is not None:
            return model_location
        identities = [(key, location) for key, location in compiled["locations"].items()
                      if location["kind"] == "model_context" and location["name"] == "当前模型处理上下文"]
        if identities:
            model_location = identities[0][0]
            existing = identities[0][1]
            if existing["access_scope"] != "recipient" or existing["retention"] is not None:
                raise ValueError("compiled model location boundary attributes conflict with recipient/null")
        else:
            model_location = "__compiled_model_context__"
            if model_location in compiled["locations"]:
                raise ValueError("reserved compiled model location conflicts with a supplied location")
            compiled["locations"][model_location] = {
                "kind": "model_context", "name": "当前模型处理上下文", "operand_refs": [],
                "access_scope": "recipient", "retention": None}
            compiled["location_evidences"][model_location] = [deepcopy(mechanism), deepcopy(boundary_evidence)]
        return model_location

    instructions = {ir["id"]: ir for block in material["cfg"]["blocks"].values() for ir in block["instructions"]}
    for ir_id, spec in parsed.transfer_specs.items():
        original = raw["profiles"][ir_id]
        profile = compiled["profiles"][ir_id]
        profile["effects"] = []
        profile["evidences"] = [deepcopy(item) for item in original["evidences"] if item["field"] != "effects"]
        output_events = []
        known = {}
        causal_edges = set()

        def emit(target, event_path, ops, effect, original_index, raw_path, operation_range,
                 kind, mode, additional_evidence=None):
            index = None if effect is None else len(profile["effects"])
            target.append({"effect_index": index, "atomic_ops": deepcopy(ops)})
            mapping["events"].append({"instruction_id": ir_id, "raw_path": raw_path,
                                      "raw_atomic_range": operation_range,
                                      "compiled_path": event_path + [len(target) - 1],
                                      "kind": kind, "mode": mode})
            if effect is None:
                return
            profile["effects"].append(effect)
            if additional_evidence is not None:
                evidences = additional_evidence
            elif original_index is not None and effect == original["effects"][original_index]:
                evidences = [item for item in original["evidences"]
                             if item["field"] == "effects" and item["effect_index"] == original_index]
            else:
                evidences = [item for op in ops for item in op["evidences"]]
            for item in evidences:
                profile["evidences"].append({key: deepcopy(item[key]) for key in ("basis", "ref_id", "quote", "reason")}
                | {"field": "effects", "value": effect, "effect_index": index})

        def processing(segment, target, event_path, raw_path, available):
            if segment.mode == "model" and "llm" not in original["operator"]:
                raise ValueError(f"model processing requires llm operator: {ir_id}")
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
                old_effect = None if event.effect_index is None else original["effects"][event.effect_index]
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
                    emit(target, event_path, pending, effect, event.effect_index, path, [start, end],
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
                    pending.append(op.model_dump(mode="json"))
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
            is_body = len(event_path) > 3
            outer = event_path[3] if is_body else None
            positions = [(outer if is_body else e, e if is_body else None, o)
                         for e in range(segment_start, len(target))
                         for o in range(len(target[e]["atomic_ops"]))]
            causal_edges.update(zip(positions, positions[1:]))

        for position, event in enumerate(spec.events):
            raw_path = ["transfer_specs", ir_id, "events", position]
            if isinstance(event, ProcessingSpec):
                processing(event, output_events, ["transfer_specs", ir_id, "events"], raw_path, known)
            else:
                body = []
                body_known = {**known, event.item: -1}
                index = len(output_events)
                for body_position, segment in enumerate(event.body):
                    processing(segment, body, ["transfer_specs", ir_id, "events", index, "body"],
                               raw_path + ["body", body_position], body_known)
                output_events.append({"kind": "for_each", "collection": event.collection.model_dump(mode="json"),
                                      "item": event.item, "body": body,
                                      "evidences": [item.model_dump(mode="json") for item in event.evidences]})
        if not profile["effects"]:
            profile["evidences"].extend(deepcopy(item) for item in original["evidences"] if item["field"] == "effects")
        result_spec = {"order": spec.order, "precedence": [],
            "events": output_events, "output_bindings": [item.model_dump(mode="json") for item in spec.output_bindings]}
        typed = IRTransferSpec.model_validate(result_spec)
        causal_edges |= structural_precedence(typed)
        causal_edges |= request_precedence(typed)
        def coordinate(key):
            return (key[0], -1 if key[1] is None else key[1], key[2])
        result_spec["precedence"] = [{"before": position_value(before), "after": position_value(after)}
            for before, after in sorted(causal_edges, key=lambda pair: (coordinate(pair[0]), coordinate(pair[1])))]
        compiled["transfer_specs"][ir_id] = result_spec
    compiled["sink_boundaries"] = [boundary.model_dump(mode="json") for boundary in
        derive_sink_boundaries(compiled["locations"], compiled["transfer_specs"], compiled["profiles"])]
    compiled = validate_compiled_response(compiled, material)
    mapping["raw_sha256"] = canonical_sha256(raw)
    mapping["compiled_sha256"] = canonical_sha256(compiled)
    return raw, compiled, mapping
