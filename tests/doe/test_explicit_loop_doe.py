"""Real finite loop records feed demand and sensitive excess comparisons."""
from copy import deepcopy
import pytest

from examples.propagation.propagation_demo import instruction, operand
from skillflow.document_guided.annotation_wire import compile_flat_response
from skillflow.doe.sensitivity_material import prepare_joint_sensitivity_review
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.loading import materials_from_result
from skillflow.propagation.material import prepare_material
from skillflow.propagation.solver import propagate
from tests.doe.helpers import source_task
from tests.propagation.annotation.helpers import source_bundle
from tests.propagation.test_explicit_loops import explicit_loop_fixture


EACH = {"kind": "each"}


def loop_review(*, preserve="value", path=None, values=("same-url", "same-url"), count_limit=None):
    cfg, template = explicit_loop_fixture(values)
    cfg["blocks"]["exit"]["instructions"].insert(0, instruction("save", [operand("acc")]))
    text = ("Fetch each URL, retain its URL and full API response in an accumulated record, then save the batch.\n"
            "The required saved result contains each URL only. API response token fields are confidential.\n")
    if path == [] and preserve == "value":
        text = text.replace("each URL only", "the complete original metadata and URL records")
    elif preserve == "cardinality":
        text = text.replace("contains each URL only", "preserves only the number of records")
    source = source_bundle(text)
    citation = {"file": "skill/SKILL.md", "start_line": 1, "end_line": 2,
                "reason": "The authored fixture specifies the exact result requirement and confidential field."}
    task = source_task(source, {"purpose": {"text": "Produce the specified saved result.", "evidences": [citation]},
        "requirements": [{"id": "R", "text": text.splitlines()[1].split(". API")[0], "evidences": [citation]}],
        "issues": []})
    material = prepare_material(source, cfg, task_baseline=task)
    wire = {"outcome": "completed", "realizations": [{"requirement_id": "R"}], "ir_semantics": {},
        "locations": {
            "api": {"kind": "remote", "name": "api", "evidences": [citation]},
            "saved": {"kind": "storage", "name": "saved", "access_scope": "task", "retention": "persistent", "evidences": [citation]}},
        "demands": [], "expressions": []}
    if count_limit is not None:
        wire["realizations"][0]["constraints"] = [{"kind": "at_most", "scope": {"kind": "task"},
            "events": [{"instruction_id": "ir_fetch", "path": []}], "limit": count_limit, "unit": "attempt"}]
    for identity, spec in template["ir_semantics"].items():
        ops = [deepcopy(op) for event in spec["events"] for op in event["atomic_ops"]]
        if identity == "ir_fetch":
            ops = [{"op": "call", "location": "api", "inputs": [{"kind": "input", "index": 0}], "output": "reply"},
                   {"op": "build", "container": "object", "parts": [
                       {"path": ["url"], "value": {"kind": "input", "index": 0}},
                       {"path": ["response"], "value": {"kind": "local", "name": "reply"}}], "output": "record"}]
        wire["ir_semantics"][identity] = {"evidences": [citation],
            "segments": [{"mode": "local", "returns": [], "ops": ops}] if ops else [],
            "output_bindings": deepcopy(spec["output_bindings"])}
    fetch = wire["ir_semantics"]["ir_fetch"]
    fetch["output_bindings"][0]["value"] = {"kind": "local", "name": "record"}
    fetch["sensitivity"] = [{"value": {"kind": "local", "name": "reply"}, "path": ["token"],
                              "label": "credential", "evidences": [citation]}]
    wire["ir_semantics"]["ir_save"] = {"evidences": [citation], "segments": [{"mode": "local", "returns": [], "ops": [
        {"op": "write", "target": "saved", "input": {"kind": "input", "index": 0}, "mode": "replace", "demands": [
            {"requirement_id": "R", "target": {"kind": "input", "index": 0}, "preserve": preserve,
             "path": [EACH, "url"] if path is None else path,
             "reason": "Keep precisely the source-declared saved result."}]}]}], "output_bindings": []}
    saved, raw, compiled, mapping = compile_flat_response(wire, material)
    result = propagate(material["cfg"], to_payload(compiled))
    assert result.status == "complete", result.diagnostics
    facts = materials_from_result(result, material=material, raw_annotation=raw,
        compiled_annotation=compiled, mapping=mapping, wire_annotation=saved)
    review = prepare_joint_sensitivity_review(facts, facts.annotation)
    return result, review.to_dict(), review.demand_dict()


def test_loop_saved_extra_response_fields_are_excess_under_url_only_requirement():
    result, review, demand = loop_review()
    assert result.coverage["ir_save"] == "processed"
    saved = [s for s in review["sinks"] if s["boundary"]["sink_type"] == "storage_write"]
    comparisons = [r for sink in saved for r in sink["data_reviews"]]
    assert comparisons and {r["conclusion"] for r in comparisons} == {"excess_supported"}
    assert all(r["reduction"]["path"][-2:] == ["response", "token"] for r in comparisons)
    assert all(not (r["node"]["instruction_id"] == "ir_fetch" and r["node"]["kind"] == "op_output"
                    and r["node"]["operation_id"].endswith(":e1:a0")) for r in demand["derivations"].values())


def test_loop_genuine_complete_metadata_requirement_retains_sensitive_content():
    _, review, _ = loop_review(path=[])
    comparisons = [r for sink in review["sinks"] if sink["boundary"]["sink_type"] == "storage_write"
                   for r in sink["data_reviews"]]
    assert comparisons
    assert {r["conclusion"] for r in comparisons} == {"no_excess_established"}


def test_loop_cardinality_demand_does_not_require_response_payload():
    _, review, demand = loop_review(preserve="cardinality", path=[])
    assert not any(r["node"]["kind"] == "op_output" and r["node"]["instruction_id"] == "ir_fetch"
                   for r in demand["derivations"].values())
    assert any(r["property"] == "cardinality" for r in demand["derivations"].values())
    comparisons = [r for sink in review["sinks"] if sink["boundary"]["sink_type"] == "storage_write"
                   for r in sink["data_reviews"]]
    assert comparisons and {r["conclusion"] for r in comparisons} == {"excess_supported"}


def test_empty_explicit_loop_has_no_source_occurrence_or_invented_request_count():
    result, review, _ = loop_review(values=(), count_limit=0)
    assert result.coverage["ir_fetch"] == "not_reached"
    assert review["constraints"]["checks"]
    assert {row["status"] for row in review["constraints"]["checks"].values()} == {"satisfied"}
    assert not any(row["code"] == "unresolved_sensitivity_reference" for row in review["diagnostics"])


@pytest.mark.parametrize("guarded", [False, True])
def test_nested_explicit_pages_keep_each_recipient_and_excess_field_paired(guarded):
    from tests.propagation.test_explicit_loops import nested_loop_fixture
    from skillflow.propagation.data.summary import content_options
    cfg, template = nested_loop_fixture()
    pages = template["ir_semantics"]["ir_pages"]["output_bindings"][0]["value"]["value"]
    for page in pages:
        for row in page["rows"]:
            row["public"] = "public-" + row["secret"]
            if guarded:
                row["allowed"] = row["secret"] in {"a0", "b1"}
    spec = template["ir_semantics"]["ir_select"]
    spec["events"][0]["atomic_ops"] = spec["events"][0]["atomic_ops"][:1]
    spec["output_bindings"][1]["value"] = {"kind": "input", "index": 0}
    if guarded:
        row, select, send, back = cfg["blocks"]["item"]["instructions"]
        cfg["blocks"]["item"]["instructions"] = [row, select,
            instruction("allowed", [operand("row")], ["allowed"]),
            instruction("gate", [operand("allowed")], opcode="dispatch")]
        cfg["blocks"]["emit"] = {"block_id": "emit", "block_name": "emit", "instructions": [send, back]}
        cfg["edges"].extend([{"source_block_id": "item", "target_block_id": "emit"},
                             {"source_block_id": "emit", "target_block_id": "inner"}])
        template["ir_semantics"]["ir_allowed"] = {"events": [{"atomic_ops": [
            {"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["allowed"], "output": "flag"}]}],
            "output_bindings": [{"output_index": 0, "value": {"kind": "local", "name": "flag"}}]}
        template["ir_semantics"]["ir_gate"] = {"events": [{"atomic_ops": [
            {"op": "branch", "input": {"kind": "input", "index": 0}, "predicate": "truthy",
             "true_target": "emit", "false_target": "inner"}]}], "output_bindings": []}
    condition = " if its allowed flag is true" if guarded else ""
    source = source_bundle(f"For every page and row, deliver the full row to its indicated receiver{condition}.\n"
                           "Only the public row field is required by that receiver; secret fields are confidential.\n")
    citation = {"file": "skill/SKILL.md", "start_line": 1, "end_line": 2,
                "reason": "The authored nested fixture defines recipient pairing, public need and confidentiality."}
    task = source_task(source, {"purpose": {"text": "Deliver public rows to their receiver.", "evidences": [citation]},
        "requirements": [{"id": "R", "text": "Preserve each receiver and its public row field.", "evidences": [citation]}], "issues": []})
    material = prepare_material(source, cfg, task_baseline=task)
    wire = {"outcome": "completed", "realizations": [{"requirement_id": "R"}], "ir_semantics": {},
        "locations": {"api": {"kind": "remote", "name": "api", "evidences": [citation]}}, "demands": []}
    for identity, value in template["ir_semantics"].items():
        ops = [deepcopy(op) for event in value["events"] for op in event["atomic_ops"]]
        wire["ir_semantics"][identity] = {"evidences": [citation],
            "segments": [{"mode": "local", "returns": [], "ops": ops}] if ops else [],
            "output_bindings": deepcopy(value["output_bindings"])}
    wire["ir_semantics"]["ir_row"]["sensitivity"] = [{"value": {"kind": "local", "name": "row"},
        "path": ["secret"], "label": "confidential", "evidences": [citation]}]
    send = wire["ir_semantics"]["ir_send"]["segments"][0]["ops"][0]
    send["demands"] = [{"requirement_id": "R", "target": {"kind": "input", "index": index},
        "preserve": "value", "path": path, "reason": "Keep the original recipient and its required public field."}
        for index, path in ((0, []), (1, ["public"]))]
    saved, raw, compiled, mapping = compile_flat_response(wire, material)
    result = propagate(material["cfg"], to_payload(compiled))
    assert result.status == "complete", result.diagnostics
    facts = materials_from_result(result, material=material, raw_annotation=raw,
        compiled_annotation=compiled, mapping=mapping, wire_annotation=saved)
    review = prepare_joint_sensitivity_review(facts, facts.annotation)
    sink = next(row for row in review.to_dict()["sinks"] if row["boundary"]["instruction_id"] == "ir_send")
    assert sink["data_reviews"] and {row["conclusion"] for row in sink["data_reviews"]} == {"excess_supported"}
    assert all(row["input_index"] == 1 and row["reduction"]["path"] == ["secret"] for row in sink["data_reviews"])
    pairs = set()
    alternatives = sink["actual_payload"][0]["alternatives"]
    assert len(alternatives) == (2 if guarded else 4)
    for alternative in alternatives:
        receiver = content_options(result.registry, alternative["inputs"][0][0])
        payload = content_options(result.registry, alternative["inputs"][1][0])
        assert len(receiver) == len(payload) == 1
        assert receiver[0]["value"] == payload[0]["value"]["receiver"]
        pairs.add((receiver[0]["value"], payload[0]["value"]["secret"]))
    assert pairs == ({("A", "a0"), ("B", "b1")} if guarded
                     else {("A", "a0"), ("A", "a1"), ("B", "b0"), ("B", "b1")})
    if guarded:
        assert len(sink["data_reviews"]) == 2
    seed_demands = [row for row in review.demand_dict()["derivations"].values()
                    if row["node"]["kind"] == "ir_output" and row["node"]["instruction_id"] == "ir_pages"]
    assert any(row["each"] and row["path"] == ["rows", EACH, "public"] for row in seed_demands)
    assert not any("secret" in row["path"] for row in seed_demands)


def test_shared_handle_reuse_separates_creation_provenance_from_current_receiver():
    from tests.propagation.test_explicit_loops import cached_handle_loop_fixture, identity_bases
    from tests.doe.test_loop_summary_relations import _track
    from skillflow.propagation.data.summary import content_options
    cfg, template = cached_handle_loop_fixture()
    source = source_bundle(
        "Initialize a shared opaque handle, then for each member send the current cached handle to its receiver.\n"
        "After sending, acquire a new opaque handle from that member's credential and replace the shared cache.\n"
        "The receiver requires the selected handle identity. Credentials and the handles themselves are confidential.\n")
    citation = {"file": "skill/SKILL.md", "start_line": 1, "end_line": 3,
        "reason": "The authored fixture distinguishes handle creation, later reuse, required identity and confidential values."}
    task = source_task(source, {"purpose": {"text": "Send the selected shared handle to each receiver.", "evidences": [citation]},
        "requirements": [{"id": "R", "text": "Preserve the receiver and selected handle identity.", "evidences": [citation]}],
        "issues": []})
    material = prepare_material(source, cfg, task_baseline=task)
    wire = {"outcome": "completed", "realizations": [{"requirement_id": "R"}], "ir_semantics": {},
        "locations": {key: {**deepcopy(value), "evidences": [citation]} for key, value in template["locations"].items()},
        "demands": []}
    for identity, value in template["ir_semantics"].items():
        ops = [{key: deepcopy(item) for key, item in op.items() if key != "evidences"}
               for event in value["events"] for op in event["atomic_ops"]]
        bindings = [{key: deepcopy(item) for key, item in binding.items() if key != "evidences"}
                    for binding in value["output_bindings"]]
        wire["ir_semantics"][identity] = {"evidences": [citation],
            "segments": [{"mode": "local", "returns": [], "ops": ops}] if ops else [], "output_bindings": bindings}
    for identity, name, label in (("ir_select", "credential", "credential"), ("ir_fetch", "handle", "handle"),
                                  ("ir_initial_handle", "handle", "initial_handle")):
        wire["ir_semantics"][identity]["sensitivity"] = [{"value": {"kind": "local", "name": name},
            "path": [], "label": label, "evidences": [citation]}]
    wire["ir_semantics"]["ir_send"]["segments"][0]["ops"][0]["demands"] = [
        {"requirement_id": "R", "target": {"kind": "input", "index": slot}, "preserve": "value", "path": [],
         "reason": "The source requires this receiver and selected handle identity."} for slot in (0, 1)]
    saved, raw, compiled, mapping = compile_flat_response(wire, material)
    result = propagate(material["cfg"], to_payload(compiled))
    assert result.status == "complete", result.diagnostics
    facts = materials_from_result(result, material=material, raw_annotation=raw,
        compiled_annotation=compiled, mapping=mapping, wire_annotation=saved)
    review = prepare_joint_sensitivity_review(facts, facts.annotation).to_dict()
    sink = next(row for row in review["sinks"] if row["boundary"]["instruction_id"] == "ir_send")
    handles, credentials = {}, {}
    for identity in result.records.get("ir_fetch").events[0].atomic_ops[0].outputs[0]:
        credential = result.registry.get(identity).origin.inputs[0]
        name = content_options(result.registry, credential)[0]["value"]
        handles[name], credentials[name] = identity, credential
    original = next(iter(result.records.get("ir_initial_handle").events[0].atomic_ops[0].outputs[0]))
    assert len({original, *handles.values()}) == 3
    b_payloads = {identity for alternative in sink["actual_payload"][0]["alternatives"]
        if content_options(result.registry, alternative["inputs"][0][0]) == [{"form": "literal", "value": "B"}]
        for identity in alternative["inputs"][1]}
    assert b_payloads
    assert {original, *handles.values()} <= set().union(*(identity_bases(result.registry, identity) for identity in b_payloads))
    derivations = review["derivations"]["sensitivity"]
    signals = [derivations[row["derivation_id"]] for row in sink["data_reviews"] if row["input_index"] == 1
               and derivations[row["derivation_id"]]["data_id"] in b_payloads]
    assert any(row["label"] == "handle" and row["relation"] == "direct" for row in signals)
    pending = [row["derivation_id"] for row in sink["data_reviews"] if row["input_index"] == 1
               and derivations[row["derivation_id"]]["data_id"] in b_payloads
               and derivations[row["derivation_id"]]["label"] == "handle"]
    visited, declared_handles = set(), set()
    while pending:
        identity = pending.pop()
        if identity in visited:
            continue
        visited.add(identity)
        record = derivations[identity]
        if "explicit_declaration" in record["rules"]:
            declared_handles.add(record["data_id"])
        pending.extend(record["parents"])
    assert handles["credential-A"] in declared_handles
    credential_signals = [row for row in signals if row["label"] == "credential"]
    assert credential_signals and all(row["relation"] == "possible" for row in credential_signals)
    data = {row["data"]["id"]: row["data"] for row in result.registry.to_dict()["records"]}
    handle_a = _track(data, handles["credential-A"], [])
    assert any(row["data_id"] in b_payloads and row["relation"] == "direct" for row in handle_a.rows.values())
    assert not handle_a.by_data[handles["credential-B"]]
    credential_b = _track(data, credentials["credential-B"], [])
    assert not credential_b.by_data[handles["credential-A"]]
