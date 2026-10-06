"""Shared abstract Boolean and operation-consumption helpers.

No opcode, evidence text or sensitivity is interpreted here. Conditions use
literal Boolean values or unresolved opaque Boolean candidates; control slots
remain operation inputs but are never silently treated as delivered payloads.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping

from skillflow.propagation.data import DataRegistry


def _plain(value):
    return value.model_dump(mode="python") if hasattr(value, "model_dump") else value


def _data_index(data):
    if isinstance(data, DataRegistry):
        return {entry["data"]["id"]: entry["data"] for entry in data.to_dict()["records"]}
    if isinstance(data, Mapping):
        if "records" in data:
            return {entry["data"]["id"]: entry["data"] for entry in data["records"]}
        return {key: _plain(value) for key, value in data.items()}
    return {item["id"]: item for value in data for item in [_plain(value)]}


def guard_truths(data: DataRegistry | Iterable | Mapping, data_ids) -> frozenset[bool]:
    """Return may-truths, refusing ordinary language truthiness conversions."""
    index = None if isinstance(data, DataRegistry) else _data_index(data)
    if not data_ids:
        raise ValueError("condition has no Data candidate")
    truths = set()
    for data_id in data_ids:
        if index is not None and data_id not in index:
            raise ValueError(f"condition references unknown Data: {data_id}")
        content = _plain(data.get(data_id) if index is None else index[data_id])["content"]
        form = content["form"]
        if form == "opaque":
            truths.update((False, True))
        elif form == "literal" and type(content["value"]) is bool:
            truths.add(content["value"])
        else:
            raise ValueError("condition must be Boolean or an opaque abstract Boolean")
    return frozenset(truths)


def payload_input_indices(operation_record) -> tuple[int, ...]:
    """Separate effect payload from control without changing parameter order."""
    record = _plain(operation_record)
    control = record.get("when_input_index")
    if record["op"] == "build":
        return tuple(member["value_input_index"] for member in record.get("members", [])
                     if member["value_input_index"] is not None)
    return tuple(index for index in range(len(record["inputs"])) if index != control)


def payload_inputs(operation_record):
    record = _plain(operation_record)
    return [record["inputs"][index] for index in payload_input_indices(record)]


def record_consumption_shape(operation_record):
    """Template shape invariant across candidates, including skipped members.

    Candidate truth affects consumed slot count. It does not change the member
    declarations or add a different operation to a for_each scope template.
    """
    record = _plain(operation_record)
    if record["op"] == "build":
        return ("build", tuple((tuple(member["path"]), member["when_input_index"] is not None)
                               for member in record["members"]))
    if record.get("when_input_index") is not None:
        return (record["op"], "conditional")
    return (record["op"], len(record["inputs"]))


def validate_record_consumption(operation_record, data=None) -> None:
    """Check explicit slot mappings; full records additionally check their specs."""
    record = _plain(operation_record)
    inputs = record["inputs"]
    members = record.get("members")
    condition = record.get("when_input_index")
    if members is not None and record["op"] != "build":
        raise ValueError("members belongs only to build records")
    if record["op"] == "build" and members is None:
        raise ValueError("build record requires member consumption mapping")
    if condition is not None and record["op"] != "deliver":
        raise ValueError("when_input_index belongs only to conditional delivery")

    def check(index):
        if type(index) is not int or not 0 <= index < len(inputs):
            raise ValueError("consumption index does not refer to an input slot")

    if members is not None:
        used, paths = [], []
        for member in members:
            if member["path"] in paths:
                raise ValueError("duplicate build member path")
            path = member["path"]
            if not path or type(path[0]) is not str:
                # Conditional construction supports object members. Legacy
                # unconditional list builds are checked against their specs.
                if member["when_input_index"] is not None:
                    raise ValueError("conditional member requires an object field")
            if any(path[:len(prior)] == prior or prior[:len(path)] == path for prior in paths):
                raise ValueError("overlapping build member paths")
            paths.append(member["path"])
            value, guard = member["value_input_index"], member["when_input_index"]
            if value is None and guard is None:
                raise ValueError("an unconditional build member requires its value input")
            for index in (guard, value):
                if index is not None:
                    check(index)
                    used.append(index)
            if data is not None and guard is not None:
                truth = guard_truths(data, inputs[guard])
                if (value is None) != (True not in truth):
                    raise ValueError("build member presence disagrees with its condition")
        if used != list(range(len(inputs))):
            raise ValueError("build member consumption must cover slots once in semantic order")
    if condition is not None:
        check(condition)
        if condition != len(inputs) - 1:
            raise ValueError("conditional delivery control must be the final input slot")
        if data is not None:
            truths = guard_truths(data, inputs[condition])
            payload = payload_input_indices(record)
            if True not in truths and payload:
                raise ValueError("false conditional delivery must not resolve payload")
            if True in truths and not payload:
                raise ValueError("possibly active model observation requires payload")
