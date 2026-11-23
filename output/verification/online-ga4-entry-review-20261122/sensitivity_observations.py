"""Count declared sites with recorded ingress data, independently of DOE comparisons."""
from collections import Counter, defaultdict
from pydantic import TypeAdapter
from skillflow.common.source_evidence import json_pointer
from skillflow.document_guided.sensitivity_entries import entry_catalogue
from skillflow.propagation.contracts.specs import AtomicOp
from skillflow.propagation.contracts.uses import value_uses


def operand_slots(op, saved, adapter):
    if saved.get("skipped_case_inputs"):
        return
    if op["op"] == "build":
        for spec, observed in zip(op["parts"], saved["members"], strict=True):
            for field, index in (("when", "when_input_index"), ("value", "value_input_index")):
                if observed[index] is not None:
                    yield spec[field], saved["inputs"][observed[index]]
    elif op.get("when") is not None:
        control = saved["when_input_index"]
        yield op["when"], saved["inputs"][control]
        yield from zip(op["inputs"][:control], saved["inputs"][:control], strict=True)
    else:
        for use, ids in zip(value_uses(adapter.validate_python(op)), saved["inputs"]):
            yield use.value.model_dump(mode="json"), ids


def summarize(declared, cfg, processing, compiled, mapping, records, data):
    roots = {row["id"]: row["origin"].get("acquired_from") for row in data}
    sites = {}
    for label in declared:
        key = label["source_access_id"]
        sites.setdefault(key, label)
    accesses = {s["access_id"]: s for entry in entry_catalogue(cfg, processing).values() for s in entry["accesses"]}
    mapped_events = {tuple(row["compiled_path"]): row for row in mapping["events"]}
    local_reads = defaultdict(lambda: defaultdict(set))
    consumed_inputs = defaultdict(set)
    incoming_owners = {row["instruction_id"] for row in declared if row["value"]["kind"] == "input"}
    adapter = TypeAdapter(AtomicOp)
    for ir, record in records.items():
        specs = compiled["ir_semantics"][ir]["events"]
        for ei, event in enumerate(record["events"]):
            if event.get("kind") == "for_each":
                effects = ((specs[ei]["body"][bi], child, (ei, ii, bi))
                           for ii, instance in enumerate(event["instances"])
                           for bi, child in enumerate(instance["body"]))
            else:
                effects = [(specs[ei], event, (ei,))]
            for spec, observed, coordinate in effects:
                for oi, (op, saved) in enumerate(zip(spec["atomic_ops"], observed["atomic_ops"], strict=True)):
                    if ir in incoming_owners:
                        for ref, identities in operand_slots(op, saved, adapter):
                            if ref["kind"] == "input":
                                consumed_inputs[(ir, ref["index"])].update(identities)
                    if op["op"] in ("read", "call", "receive") and op.get("output"):
                        path = ("ir_semantics", ir, "events", ei)
                        if len(coordinate) == 3:
                            path += ("body", coordinate[2])
                        origin = mapped_events[path]
                        if origin["raw_atomic_range"] is None:
                            continue
                        raw = [*origin["raw_path"], "atomic_ops", origin["raw_atomic_range"][0] + oi]
                        wire = mapping["wire_paths"].get(json_pointer(*raw))
                        if wire is None:
                            continue
                        local_reads[wire][(*coordinate, oi)].update(
                            value for slot in saved["outputs"] for value in slot)

    seen_roots, witnessed, available, counts = set(), set(), set(), Counter()
    for site, label in sites.items():
        ir, source, ref = label["instruction_id"], label["source_entry_location"], label["value"]
        occurrences = {}
        if ir in records and ref["kind"] == "input":
            bindings = records[ir]["entry_state"]["bindings"]
            bound = {identity for row in bindings
                if row["location"]["kind"] + ":" + row["location"]["name"] == source for identity in row["data_ids"]}
            if any(roots.get(identity) == source for identity in bound):
                available.add(site)
            occurrences[(ir, "input", ref["index"])] = bound & consumed_inputs[(ir, ref["index"])]
        elif ref["kind"] == "local":
            coordinate = accesses[site]["operation_path"]
            occurrences = local_reads.get(json_pointer("ir_semantics", ir, *coordinate), {})
        for address, identities in occurrences.items():
            matching = {identity for identity in identities if roots.get(identity) == source}
            if matching:
                witnessed.add(site)
                counts[label["source_entry_origin"]] += 1
                seen_roots.update(matching)
    return {"classified_source_access_ids": len(sites), "witnessed_distinct_access_sites": len(witnessed),
            "incoming_operand_sites_available_at_entry": len(available),
            "witnessed_data_versions": len(seen_roots), "recorded_occurrences_by_origin": dict(counts),
            "unwitnessed_classified_sites": len(sites.keys() - witnessed),
            "basis": "Mapped read/call/receive outputs and named incoming argument slots explicitly consumed in static forward records, "
                     "matched to acquired_from. Multiple sensitive fields at one access are counted once. "
                     "These are modeled reads. No Skill was executed."}
