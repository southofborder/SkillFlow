"""Shared typed value uses and unambiguous request/response association.

This module does not evaluate data, parse evidence prose or identify calls by
tool names. A guard controls use of a value, never becomes a request parameter.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from skillflow.common.recording import canonical_sha256


@dataclass(frozen=True)
class ValueUse:
    value: Any
    when: Any | None = None
    role: Literal["value", "control"] = "value"
    member_index: int | None = None


def value_uses(operation) -> list[ValueUse]:
    """Preserve original operands; conditional members visit guard then value."""
    from skillflow.propagation.contracts.specs import BuildOp
    from skillflow.propagation.contracts.specs import ReceiveOp
    from skillflow.propagation.contracts.specs import DeliverOp
    from skillflow.propagation.contracts.specs import RawDeliverOp
    from skillflow.propagation.contracts.specs import ComputeOp
    from skillflow.propagation.contracts.specs import WriteOp
    from skillflow.propagation.contracts.specs import SelectPartOp
    from skillflow.propagation.contracts.specs import ExcludePartsOp
    from skillflow.propagation.contracts.specs import FilterItemsOp
    from skillflow.propagation.contracts.specs import UpdateFieldsOp
    if isinstance(operation, BuildOp):
        uses = []
        for index, member in enumerate(operation.parts):
            if member.when is not None:
                uses.append(ValueUse(member.when, role="control", member_index=index))
            uses.append(ValueUse(member.value, when=member.when, member_index=index))
        return uses
    if isinstance(operation, (ReceiveOp, DeliverOp, RawDeliverOp, ComputeOp)):
        guard = getattr(operation, "when", None)
        uses = [ValueUse(ref, when=guard) for ref in operation.inputs]
        if guard is not None:
            uses.append(ValueUse(guard, role="control"))
        return uses
    if isinstance(operation, WriteOp):
        return [] if operation.input is None else [ValueUse(operation.input)]
    if isinstance(operation, (SelectPartOp, ExcludePartsOp, FilterItemsOp)):
        return [ValueUse(operation.input)]
    if isinstance(operation, UpdateFieldsOp):
        return [ValueUse(operation.input), *(ValueUse(item.value) for item in operation.updates)]
    return []


def iter_value_uses(operation):
    yield from value_uses(operation)


def static_condition(ref, instruction=None):
    """Only explicit Boolean literals determine a static truth value."""
    from skillflow.propagation.contracts.specs import LiteralRef
    from skillflow.propagation.contracts.specs import InputRef
    from skillflow.propagation.contracts.specs import AlternativesRef
    if isinstance(ref, LiteralRef):
        if type(ref.value) is not bool:
            raise ValueError("condition must be Boolean, not Python truthiness")
        return ref.value
    if isinstance(ref, InputRef) and instruction is not None:
        operand = instruction.get("inputs", [])[ref.index]
        if operand["type"] == "literal":
            value = operand.get("literal_value")
            if type(value) is not bool:
                raise ValueError("condition input must be Boolean")
            return value
    if isinstance(ref, AlternativesRef):
        values = [static_condition(child, instruction) for child in ref.items]
        if values and all(value is True for value in values):
            return True
        if values and all(value is False for value in values):
            return False
    return None


def active_value_uses(operation, instruction=None):
    """A definitely false member has no value use; its control use remains."""
    return [use for use in value_uses(operation)
            if use.role == "control" or use.when is None
            or static_condition(use.when, instruction) is not False]


def _identity(operation):
    target = getattr(operation, "target", getattr(operation, "location", None))
    return target, canonical_sha256([ref.model_dump(mode="json") for ref in operation.inputs])


def request_pairs(spec) -> dict[tuple[int, int | None, int], tuple[int, int | None, int]]:
    """Associate each declared response with one request in the same scope.

    Fixed serial calls consume requests once. Partial orders must determine a
    unique association; no FIFO/nearest-call inference or implicit call ID.
    Empty-input acquisitions need not have a request at all.
    """
    from skillflow.propagation.contracts.specs import operation_items
    from skillflow.propagation.contracts.specs import structural_precedence
    from skillflow.propagation.contracts.specs import operation_key
    operations = operation_items(spec)
    scopes = {}
    for key, operation in operations.items():
        if operation.op not in {"deliver", "receive"} or getattr(operation, "when", None) is not None:
            continue
        scope = None if key[1] is None else key[0]
        scopes.setdefault(scope, []).append((key, operation))
    result = {}
    if spec.order == "fixed":
        for entries in scopes.values():
            available = []
            declared_targets = {op.target for _, op in entries if op.op == "deliver"}
            for key, operation in entries:
                if operation.op == "deliver":
                    available.append((key, operation))
                    continue
                candidates = [(prior, request) for prior, request in available if _identity(request) == _identity(operation)]
                if len(candidates) > 1:
                    raise ValueError("ambiguous request/receive association")
                if candidates:
                    prior, _ = candidates[0]
                    result[key] = prior
                    available = [(p, request) for p, request in available if p != prior]
                elif operation.location in declared_targets:
                    raise ValueError("receive request inputs do not match an unconsumed delivery")
        return result
    edges = structural_precedence(spec) | {
        (operation_key(item.before), operation_key(item.after)) for item in spec.precedence}
    following = {key: set() for key in operations}
    for before, after in edges:
        following[before].add(after)
    changed = True
    while changed:
        changed = False
        for key in following:
            expanded = following[key] | set().union(*(following[child] for child in following[key]))
            if expanded != following[key]:
                following[key] = expanded
                changed = True
    for entries in scopes.values():
        requests = {key: op for key, op in entries if op.op == "deliver"}
        pending = {key: op for key, op in entries if op.op == "receive"}
        consumed = set()
        while pending:
            progressed = False
            for key, operation in list(pending.items()):
                if not any(request.target == operation.location for request in requests.values()):
                    del pending[key]
                    progressed = True
                    continue
                # A later mandatory response cannot consume a request before
                # an earlier unresolved response has established its pairing.
                if any(key in following[other] for other in pending if other != key):
                    continue
                matches = [prior for prior, request in requests.items()
                           if prior not in consumed and prior not in following[key]
                           and _identity(request) == _identity(operation)]
                if len(matches) != 1:
                    continue
                prior = matches[0]
                rivals = [other for other, candidate in pending.items() if other != key
                          and other not in following[key] and key not in following[other]
                          and _identity(candidate) == _identity(operation) and prior not in following[other]]
                if rivals:
                    continue
                result[key] = prior
                consumed.add(prior)
                del pending[key]
                progressed = True
            if not progressed:
                raise ValueError("ambiguous or missing request/receive association in partial order")
    return result


def request_precedence(spec):
    return {(request, response) for response, request in request_pairs(spec).items()}
