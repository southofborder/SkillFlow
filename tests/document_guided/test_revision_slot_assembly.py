"""Real completed text and independent-owner revisions through their strict validators."""
import hashlib
import json
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import pytest

from skillflow.common.revision_slots import decode_revision_slots, read_revision_object
from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.fragment_revision import processing_scope
from skillflow.document_guided.fragment_wire import expand_revision_rows
from skillflow.document_guided.graph_slots import _edit_components
from skillflow.document_guided.revision_assembly import assemble_revision
from tests.document_guided.test_processing_finite_slots import inputs


def decode(text, names=("a", "b", "c")):
    return decode_revision_slots(text, field="coverage_slots", owner="instruction_id", authorized=names,
                                 shared=expand_revision_rows)


def test_ga4_134_revision_slots_and_73_definitions_survive_unique_closer_repair():
    raw = (Path(__file__).parents[1]/"fixtures/ga4_entry_occurrences/revision-processing-response.txt").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == "29dd484943c931fa9ab8b84fa174ffd5ba9892b0ade531fac9e965f90ba6f81f"
    obj = read_revision_object(raw.decode())
    assert len(obj.value["shared_values"]) == 73
    assert [(r["offset"], r["character"]) for r in obj.repairs] == [(51867, "}")]
    names = ("011 015 017 018 019 020 037 038 039 040 042 049 050 051 060 061 062 071 072 073 080 082 083 091 092 093 "
           "102 103 104 105 114 115 124 125 132 133 144 147 149 152 165 168 170 173 195 199 203 207 211 215 218 219 "
           "220 221 222 229 239 257 261 265 269 272 273 276 290 291 292 294 298 300 319 323 327 331 335 338 339 340 "
           "341 343 354 373 374 376 378 385 386 388 390 397 398 399 401 404 405 406 411 412 424 429 430 451 462 466 "
           "467 468 469 472 483 485 488 491 494 497 511 515 524 528 537 541 546 550 563 564 570 571 573 579 599 600 "
           "607 614 617 625").split()
    result = decode(obj, {"ir_" + n for n in names})
    assert not result.diagnostics and len(result.rows) == 134
    assert result.rows["ir_195"]["keep"] == "modeled"
    assert result.rows["ir_229"]["modeled"] and result.rows["ir_617"]["modeled"]


def test_named_bad_line_does_not_invalidate_its_neighbors_or_hide_duplicate():
    source = '''{"coverage_slots":[
{"instruction_id":"a","keep":"modeled"},
{"instruction_id":"b","keep":???},
{"instruction_id":"b","keep":"modeled"},
{"instruction_id":"c","keep":"modeled"}
]}'''
    result = decode(source)
    assert set(result.rows) == {"a", "c"}
    assert {d["code"] for d in result.diagnostics} == {"revision_record_json", "revision_slot_duplicate"}
    assert all(d["context"]["instruction_id"] == "b" for d in result.diagnostics)


def test_shared_reference_fault_and_duplicate_definition_are_scoped_to_their_users():
    source = '''{"format":"skillflow-processing-json-v1","shared_values":{
"v0":"modeled",
"v1":broken,
"v2":{"$ref":"v1"}
},"payload":{"coverage_slots":[
{"instruction_id":"a","keep":{"$ref":"v0"}},
{"instruction_id":"b","keep":{"$ref":"v2"}},
{"instruction_id":"c","keep":{"$ref":"v0"}}
]}}'''
    for bad in (source, source.replace('"v1":broken,', '"v1":"a",\n"v1":"b",')):
        result = decode(bad)
        assert set(result.rows) == {"a", "c"}
        assert all(row["keep"] == "modeled" for row in result.rows.values())
        assert any(d["code"] == "revision_shared_reference" and d["context"]["instruction_id"] == "b"
                   for d in result.diagnostics)


def test_ordinary_pretty_json_is_supported_and_ambiguous_truncation_rejects_outer_object():
    obj = {"coverage_slots": [{"instruction_id": k, "label": "literal } ] fake owner"} for k in ("b", "c", "a")]}
    assert set(decode(json.dumps(obj, indent=3)).rows) == {"a", "b", "c"}
    with pytest.raises(StructuralValidationError):
        decode('{"coverage_slots":[{"instruction_id":"a","label":"unfinished')
    with pytest.raises(StructuralValidationError):
        decode('{"coverage_slots":[],"coverage_slots":[]}')


def test_valid_scoped_fix_survives_unrelated_invalid_row_and_retained_prior_is_validated():
    material, prior, _ = inputs()
    cfg = material["cfg"]
    targets = ["ir_call", "ir_other_call"]
    scope = processing_scope(cfg, cfg, [{"target_ids": ["annotation:/ir_semantics/" + i for i in targets]}], prior)
    old = prior["ir_semantics"]["ir_other_call"]
    valid = deepcopy(old)
    valid["segments"][0]["ops"][0]["output"] = "specific_reply"
    valid["output_bindings"][0]["value"]["name"] = "specific_reply"
    rows = {"coverage_slots": [{"instruction_id": "ir_call", "modeled": {"segments": "bad"}},
                            {"instruction_id": "ir_other_call", "modeled": valid}]}
    context = {"processing_revision": {"scope": scope, "previous": prior}}
    result, gaps, receipt = assemble_revision("processing", rows, context, material)
    assert result["ir_semantics"]["ir_call"] == prior["ir_semantics"]["ir_call"]
    assert result["ir_semantics"]["ir_other_call"] == valid
    assert receipt["retained_prior"] == ["ir_call"] and receipt["accepted"] == ["ir_other_call"]


def test_cfg_groups_mutually_required_edits_separately_from_unrelated_invalid_block():
    def block(ref, inputs, outputs):
        return {"ref": ref, "operations": [{"inputs": inputs, "outputs": outputs}], "exit": {"kind": "return", "values": []}}
    blocks = [block("maker", [], ["old"]), block("user", [{"result": "old"}], []), block("other", [], [])]
    edits = [(0, {"kind": "field", "path": ["blocks", 0, "operations", 0, "outputs"]}, ["new"]),
           (1, {"kind": "field", "path": ["blocks", 1, "operations", 0, "inputs"]}, [{"result": "new"}]),
           (2, {"kind": "field", "path": ["blocks", 2, "operations", 0, "inputs"]}, [{"result": "absent"}])]
    groups = _edit_components(SimpleNamespace(facts={"blocks": blocks}), edits)
    assert [[i for i, _, _ in group] for group in groups] == [[0, 1], [2]]


def test_full_processing_revision_quarantines_one_malformed_ir_on_its_current_cfg():
    from skillflow.document_guided.revision_assembly import full_revision
    material, previous, _ = inputs()
    lines = [json.dumps(name) + ":" + json.dumps(op) for name, op in previous["ir_semantics"].items()]
    encoded = "{" + ",\n".join(json.dumps(k) + ":" + json.dumps(v) for k, v in previous.items() if k != "ir_semantics")
    encoded+=',"ir_semantics":{\n' + ",\n".join(
        line if not line.startswith('"ir_other_call":') else '"ir_other_call":{"bad":???}' for line in lines) + '\n}}'
    result, gaps, receipt = full_revision("processing", encoded, {}, material)
    assert "ir_other_call" not in result["ir_semantics"]
    assert result["ir_semantics"]["ir_call"] == previous["ir_semantics"]["ir_call"]
    assert {g["instruction_id"] for g in gaps} == {"ir_other_call"}
    assert receipt["diagnostics"][0]["path"] == "/ir_semantics/ir_other_call"


def test_correspondence_invalid_slot_retains_only_its_still_valid_prior_goals():
    from skillflow.document_guided.fragment_revision import correspondence_scope
    from tests.document_guided.test_correspondence_fragment_revision import inputs as make_case
    material, processing, prior = make_case()
    cfg, task = material["cfg"], material["task"]
    target = "annotation:/ir_semantics/ir_call/segments/0/ops/0/demands/"
    findings = [{"domain": "annotation", "owner": "task-correspondence", "target_ids": [target + "0", target + "1"]}]
    scope = correspondence_scope(cfg, cfg, processing, processing, task, task, findings, prior)
    assert len(scope["slots"]) == 2
    good, bad = sorted(scope["slots"])
    rows = {"slots": [{"requirement_id": good, "keep": True}, {"requirement_id": bad, "keep": "invalid"}]}
    context = {"processing": processing, "correspondence_revision": {"scope": scope, "previous": prior}}
    value, _, receipt = assemble_revision("task-correspondence", rows, context, material)
    assert value == prior
    assert receipt["accepted"] == [good] and receipt["retained_prior"] == [bad]


def test_sensitivity_empty_answer_of_an_authorized_owner_is_distinct_from_missing_row():
    from skillflow.document_guided.fragment_revision import sensitivity_scope
    material, processing, _ = inputs()
    cfg = material["cfg"]
    name = "ir_call"
    prior = {"declarations": []}
    changed = deepcopy(processing)
    changed["ir_semantics"][name]["segments"][0]["ops"][0]["output"] = "revised"
    changed["ir_semantics"][name]["output_bindings"][0]["value"]["name"] = "revised"
    scope = sensitivity_scope(cfg, cfg, processing, changed, [], prior)
    assert len(scope["slots"]) >= 2 and name in scope["slots"]
    context = {"processing": changed, "sensitivity_revision": {"scope": scope, "previous": prior}}
    value, gaps, receipt = assemble_revision("sensitivity", {"slots": [{"instruction_id": name, "declarations": []}]}, context, material)
    assert value == prior and receipt["accepted"] == [name]
    assert {g["instruction_id"] for g in gaps} == scope["slots"].keys() - {name}


def test_recorded_partial_scoped_revision_replays_from_immutable_response(tmp_path):
    from skillflow.common.artifacts import ArtifactWriter
    from skillflow.common.recording import injected_factory
    from skillflow.common.structural_correction import ResponseChain
    from skillflow.document_guided.online import CONFIG, _run_candidate, validate_step
    material, prior, _ = inputs()
    targets = ["ir_call", "ir_other_call"]
    scope = processing_scope(material["cfg"], material["cfg"], [
        {"target_ids": ["annotation:/ir_semantics/" + ir for ir in targets]}], prior)
    raw = ('{"coverage_slots":[\n{"instruction_id":"ir_call","keep":"modeled"},\n'
           '{"instruction_id":"ir_other_call","keep":???}\n]}')
    context = {"slot_revisions": True, "processing_revision": {"scope": scope, "previous": prior},
               "cfg": material["cfg"], "source": material["source"]}
    class Client:
        calls = 0
        def complete(self, prompt):
            self.calls += 1
            return raw
    client = Client()
    def run(replay):
        ctx = deepcopy(context)
        chain = ResponseChain(tmp_path, prefix="calls", base_prompt="Repair the two bound owners.",
            request_kind="document_guided_processing_fragment", config=CONFIG, writer=ArtifactWriter(()),
            validate=lambda reply: validate_step("processing_fragment", reply, context=ctx), max_corrections=0,
            validation_evidence=lambda candidate: ctx.get("revision_slots"),
            client_factory=None if replay else injected_factory(client), replay=replay)
        value, gaps = _run_candidate(chain, "processing_fragment", ctx)
        return value, gaps, ctx["revision_slots"]
    first = run(False)
    assert client.calls == 1 and first[0] == prior and first[2]["retained_prior"] == ["ir_other_call"]
    assert json.loads((tmp_path / "calls/a001/response.json").read_bytes()) == raw
    assert run(True) == first and client.calls == 1
    from skillflow.common.recording import canonical_sha256, sha_file
    from skillflow.document_guided.online import _saved_step_value, STEP_IDENTITY
    chain = json.loads((tmp_path / "calls/chain.json").read_bytes())
    (tmp_path / "value.json").write_text(json.dumps(first[0]), encoding="utf-8")
    saved = {"identity": STEP_IDENTITY, "value_file": "value.json", "value_sha256": sha_file(tmp_path / "value.json"),
             "response_chain_sha256": canonical_sha256(chain), "accepted_call": None, "status": "partial",
             "revision_slots": first[2], "validation_gaps": first[1]}
    (tmp_path / "result.json").write_text(json.dumps(saved), encoding="utf-8")
    manifest = {"kind": "processing_fragment"}
    # The saved-step reader also binds its normal stage request kind.
    assert _saved_step_value(tmp_path, manifest) == first[0]
    saved["revision_slots"]["diagnostics"] = []
    (tmp_path / "result.json").write_text(json.dumps(saved), encoding="utf-8")
    with pytest.raises(ValueError, match="slot assembly"):
        _saved_step_value(tmp_path, manifest)


def test_revised_review_preserves_strict_json_receipt_and_replays(tmp_path):
    from skillflow.document_guided.source_review import run_source_review, replay_saved_review
    from tests.document_guided.test_source_review import Client, fixture
    from tests.doe.input_review_helpers import source_review_response
    from skillflow.document_guided.source_review import prepare_review_material
    files, task, cfg = fixture()
    opts = dict(files=files, task=task, cfg=cfg, generation="fragment-v1", partial=True, prompt_view="shared-v2")
    material = prepare_review_material(**opts)
    normal = source_review_response(material, [])
    assert not normal["findings"]
    # Invalid finding with an independently readable identity stays available to
    # the normal isolation/objection logic; the envelope and neighbors are intact.
    source = json.dumps(normal).replace('"findings": []', '"findings": [\n{"domain":"cfg","target_ids":["stage:graph"],"explanation":???}\n]')
    client = Client(source)
    directory = tmp_path / "revision/review"
    result = run_source_review(directory, client=client, max_corrections=0, **opts)
    assert result["status"] in {"partial", "structural_failure"}
    assert result["revision_slots"][0]["diagnostics"][0]["path"] == "/findings/0"
    assert replay_saved_review(directory) == result and len(client.prompts) == 1
