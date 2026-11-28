"""Validate the provenance of each protected outcome without executing it."""

from skillflow.common.recording import canonical_sha256
from skillflow.propagation.data.summary import content_options
from skillflow.propagation.loop_domain import key as producer_key
from skillflow.propagation.models import FlowLocation
from skillflow.propagation.selectors import selector_outcomes


def validate_route_evidence(instruction, record, specs, records=None):
    dispatch = instruction.get("metadata", {}).get("outcome_dispatch")
    if bool(record.outcome_routes) != (dispatch is not None):
        raise ValueError("route evidence must belong to its typed outcome dispatch")
    if dispatch is None:
        return
    producer = dispatch["producer"]
    groups = specs.get(producer, {}).get("outcome_bindings", [])
    targets = {(group["group"], case["case_id"]): dispatch["on_" + case["disposition"]]
               for group in groups for case in group["cases"]}
    observed = {(row.group, row.case_id): row.target for row in record.outcome_routes}
    if len(observed) != len(record.outcome_routes) or any(targets.get(key) != target for key, target in observed.items()):
        raise ValueError("selected case route differs from its declared protected continuation")
    if records is not None:
        origin = records.get(producer)
        feasible = {(row.group, row.case_id) for row in origin.outcomes} if origin is not None else set()
        if set(observed) != feasible:
            raise ValueError("outcome dispatch evidence differs from its producer's feasible case records")


def _literal_matches(data, identity, value):
    options = content_options(data, identity)
    expected = canonical_sha256(value)
    return bool(options) and all(row["form"] == "literal" and canonical_sha256(row["value"]) == expected
                                 for row in options)


def _bound_version(data, identity, accepted, seen=frozenset()):
    """Accept recorded roots and their exact, nonprojecting context views."""
    if accepted(identity):
        return True
    if identity in seen:
        return False
    content = data.get(identity).content
    options = ([part.content for part in content.variants] if content.form == "loop_summary" else [content])
    return bool(options) and all(option.form == "selection" and not option.path and
        _bound_version(data, option.base, accepted, seen | {identity}) for option in options)


def _outcome_occurrence(data, identity, position):
    value = data.get(identity)
    source = value.origin.at
    bindings, prefix = (), str(position)[:-1] + ", "
    if value.content.form == "loop_summary":
        if source != value.content.producer:
            return None
        bindings = tuple(sorted(value.content.bindings.items()))
        prefix = producer_key(position)[:-1] + ","
    return (source.removeprefix(prefix), bindings) if source and source.startswith(prefix) else None


def _matches_versions(data, identity, roots, aliases):
    return _bound_version(data, identity, roots.__contains__) if aliases else identity in roots


def _input_value(ir, index, record, data, identity, aliases=False):
    operand = ir["inputs"][index]
    kind, name = operand["type"], operand.get("identifier")
    if kind == "literal":
        return _literal_matches(data, identity, operand.get("literal_value"))
    if kind == "result":
        roots = record.entry_state.get(FlowLocation(kind="result", name=name)) or frozenset()
        return _matches_versions(data, identity, roots, aliases)
    # The imported state does not retain the resolved optional/addressee snapshot.
    return None if kind == "context_key" else False


def _local_versions(events, records, pair, name):
    values = set()
    for event, record in zip(events, records):
        case = event.get("case")
        if case and (case["group"], case["id"]) != pair:
            continue
        if event.get("kind") == "for_each":
            if event.get("output") == name:
                values.update(record.outputs)
        else:
            for operation, observed in zip(event["atomic_ops"], record.atomic_ops):
                if operation.get("output") == name:
                    values.update(identity for slot in observed.outputs for identity in slot)
    return values


def validate_outcome_evidence(ir, spec, record, data, row, declaration):
    pair = row.group, row.case_id
    labels = [event["case"] for event in spec["events"] if event.get("case")
              and (event["case"]["group"], event["case"]["id"]) == pair]
    guard = labels[0].get("guard") if labels else None
    if bool(row.selectors) != (guard is not None):
        raise ValueError("outcome selectors differ from the declared case guard")
    if guard is not None and any(
            _input_value(ir, guard["input_index"], record, data, identity) is False
            or guard["outcome"] not in selector_outcomes(data, identity, guard) for identity in row.selectors):
        raise ValueError("outcome selector is not a feasible version of its declared entry operand")
    position = [ir["id"], *pair]
    completions = {_outcome_occurrence(data, identity, [*position, "completion"]) for identity in row.completion}
    if None in completions:
        raise ValueError("completion version belongs to another protected outcome")
    def matches(ref, identity, aliases=False):
        kind = ref["kind"]
        if kind == "literal":
            return _literal_matches(data, identity, ref["value"])
        if kind == "input":
            index = ref["index"]
            return (_matches_versions(data, identity, row.selectors, aliases)
                    if guard and index == guard["input_index"] else _input_value(ir, index, record, data, identity, aliases))
        if kind == "alternatives":
            return any(matches(item, identity, aliases or bool(ref.get("guard"))) is not False for item in ref["items"])
        if ref["name"] == "__raised__":
            options = content_options(data, identity)
            occurrence = _outcome_occurrence(data, identity, [*position, "raised"])
            return (occurrence is not None and (not completions or occurrence in completions)
                    and bool(options) and all(value["form"] == "opaque" and value.get("python_exception_type")
                        == ir.get("metadata", {}).get("python_raised_class") for value in options))
        roots = _local_versions(spec["events"], record.events, pair, ref["name"])
        return _matches_versions(data, identity, roots, aliases)

    if row.values and any(matches(declaration["value"], identity) is False for identity in row.values):
        raise ValueError("public value does not bind to its declared protected outcome source")
