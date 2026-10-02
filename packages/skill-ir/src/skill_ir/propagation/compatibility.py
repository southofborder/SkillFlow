"""One structural operation/effect/boundary contract for specs and facts.

This module never infers labels from opcodes, tool names or evidence prose.
It checks only explicitly supplied abstract operations and boundary categories.
"""

INTERACTION_EFFECTS = {
    "read": {"context_read", "fs_read"},
    "receive": {"net_receive"},
    "deliver": {"net_send", "model_observe", "user_output"},
    "write": {"context_write", "fs_write"},
}
EFFECT_BOUNDARIES = {
    "context_read": {"runtime_context"}, "context_write": {"runtime_context"},
    "fs_read": {"storage"}, "fs_write": {"storage"},
    "net_send": {"remote"}, "net_receive": {"remote"},
    "model_observe": {"model_context"}, "user_output": {"user"},
}
TRANSFORM_OPERATIONS = {"select_part", "exclude_parts", "update_fields", "build", "compute", "filter_items"}


def validate_event_operations(effect: str | None, operations: list[str]) -> None:
    if not operations:
        raise ValueError("effect event must contain an atomic operation")
    primary = next((op for op, effects in INTERACTION_EFFECTS.items() if effect in effects), None)
    if primary is not None and primary not in operations:
        raise ValueError(f"effect event lacks its primary operation: {effect}/{primary}")
    if effect == "transform" and not TRANSFORM_OPERATIONS.intersection(operations):
        raise ValueError("transform event lacks a data transformation")


def validate_operation_boundary(
    operation: str, effect: str | None, boundary_kind: str | None,
    *, dependencies: list[str] | None = None, input_count: int | None = None,
) -> None:
    """Check one operation; resolved records omit symbolic dependency lists.

    The symbolic specification additionally supplies compute dependency kinds.
    The standalone fact file still checks the same operation/boundary combination.
    """
    if effect is None:
        if operation == "compute":
            if dependencies is not None and any(value != "possible" for value in dependencies):
                raise ValueError("effect-free compute only permits possible dependencies")
        elif not (operation in {"receive", "deliver"} and boundary_kind == "tool"):
            raise ValueError("effect-free event only permits possible compute or receive/deliver with tool")
    elif operation in INTERACTION_EFFECTS and effect not in INTERACTION_EFFECTS[operation]:
        raise ValueError(f"atomic operation/effect mismatch: {operation}/{effect}")

    if operation in INTERACTION_EFFECTS:
        allowed = {"tool"} if effect is None else EFFECT_BOUNDARIES.get(effect, set())
        if boundary_kind not in allowed:
            raise ValueError(f"effect location kind mismatch: {operation}/{effect}/{boundary_kind}")
        if operation == "deliver" and input_count == 0 and not (effect is None and boundary_kind == "tool"):
            raise ValueError("empty delivery inputs are allowed only for an effect-free tool request")
    elif boundary_kind is not None:
        raise ValueError("non-interaction operation must not declare a boundary")
