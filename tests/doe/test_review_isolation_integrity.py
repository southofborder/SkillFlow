"""Partial review receipts retain exact targets and raw record identities."""
from copy import deepcopy

import pytest

from skillflow.common.recording import canonical_sha256
from skillflow.doe.input_contract_review import build_input_contract_review, checked_input_contract_review
from skillflow.doe.input_contract_scopes import reviewed_contract_scopes
from skillflow.document_guided.annotation_wire import compile_flat_response
from skillflow.document_guided.fragments import split_fragments
from skillflow.document_guided.source_review import isolate_source_review, prepare_review_material
from skillflow.propagation.contracts.joint import joint_source_files
from skillflow.propagation.annotation.binding_examples import evidence
from tests.document_guided.test_input_contract_completeness import call_sample
from tests.doe.input_review_helpers import checks_for_inventory


@pytest.fixture(scope="module")
def selected():
    material, wire = call_sample()
    wire, raw, compiled, mapping = compile_flat_response(wire, material)
    annotation = {"task": material["task"], "raw_annotation": raw,
        "compiled_annotation": compiled, "mapping": mapping, "wire_annotation": wire}
    files, cfg = joint_source_files(material), material["cfg"]
    fragments = {"processing": {"outcome": "completed", **split_fragments(wire)["processing"]}}
    review_material = prepare_review_material(files=files, cfg=cfg, task=annotation["task"],
        annotation=wire, raw_annotation=raw, compiled=compiled, mapping=mapping,
        generation="fragment-v1", fragments=fragments)
    candidate = {"outcome": "completed", "findings": [], "source_input_findings": [],
        "input_projection_checks": [], "input_contract_checks":
            checks_for_inventory(review_material["input_contract_inventory"], [evidence()])}
    return files, cfg, annotation, review_material, candidate


def representation_finding():
    return {"domain": "annotation", "target_ids": [
        "fragment:processing:/ir_semantics/ir_call/segments/0/ops/0"],
        "explanation": "The actual receiver relationship is not represented at this invocation.",
        "source_refs": [{k: evidence()[k] for k in ("file", "start_line", "end_line")}],
        "suggestion": "Retain the source-supported actual receiver relation before accepting this call."}


def source_finding():
    return {"kind": "missing_argument",
        "target_id": "annotation:/ir_semantics/ir_call/segments/0/ops/0",
        "actual": {"kind": "absent_argument"},
        "expected": {"parameter": {"kind": "source_role", "description": "The separately required label"},
            "information": {"property": "value"}, "source_value": None,
            "description": "The independently specified action needs the omitted label argument."},
        "impacts": [{"kind": "action"}], "requirement_evidences": [evidence()],
        "occurrence_evidences": [evidence()], "reason": "The invocation omits the source-required label."}


def partial_receipt(selected):
    files, cfg, annotation, material, original = selected
    candidate = deepcopy(original)
    candidate["findings"] = [representation_finding()]
    isolated = isolate_source_review(candidate, material)
    assert isolated["validation"]["diagnostics"]
    receipt = build_input_contract_review(files=files, cfg=cfg, annotation=annotation,
        review={"status": "partial", "availability": material["availability"], **isolated},
        review_material=material)
    return receipt


def test_fragment_alias_receipt_roundtrips_and_cannot_hide_current_call_conflict(selected):
    files, cfg, annotation, material, _ = selected
    receipt = partial_receipt(selected)
    core = receipt["review_core"]
    assert core["isolation_context"]["fragments"] == material["fragments"]
    assert core["findings"][0]["target_ids"] == representation_finding()["target_ids"]
    expected = {row["id"] for row in material["input_contract_inventory"]["obligations"]}
    assert set(core["blocked_obligation_ids"]) == expected
    assert not receipt["source_review_complete"]
    for row in core["inventory"]["contracts"]:
        assert not reviewed_contract_scopes(receipt, row["contract_id"])["available"]
    assert checked_input_contract_review(receipt, files=files, cfg=cfg, annotation=annotation) == receipt


@pytest.mark.parametrize("change", ["list_view", "dict_view", "unknown_null_fragment_key",
                                    "list_failures", "string_failures", "boolean_failures"])
def test_malformed_or_forged_context_is_a_typed_receipt_failure(selected, change):
    files, cfg, annotation, _, _ = selected
    receipt = partial_receipt(selected)
    context = receipt["review_core"]["isolation_context"]
    if change == "list_view":
        context["annotation_view"] = []
    elif change == "dict_view":
        context["annotation_view"] = {}
    elif change == "unknown_null_fragment_key":
        context["fragments"]["processing"]["invented_field"] = None
    else:
        context["stage_failures"] = {"list_failures": [], "string_failures": "", "boolean_failures": False}[change]
    receipt["review_sha256"] = canonical_sha256(receipt["review_core"])
    receipt["receipt_sha256"] = canonical_sha256({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    with pytest.raises(ValueError, match="isolated review|Isolated review"):
        checked_input_contract_review(receipt, files=files, cfg=cfg, annotation=annotation)


@pytest.mark.parametrize("mode", ["duplicate", "source_conflict"])
def test_duplicate_and_conflict_record_digests_identify_raw_candidate(selected, mode):
    _, _, _, material, original = selected
    candidate = deepcopy(original)
    finding = representation_finding()
    if mode == "duplicate":
        candidate["findings"] = [finding, deepcopy(finding)]
        paths = ["/findings/0", "/findings/1"]
        expected_status = "duplicate"
    else:
        candidate["findings"] = [finding]
        candidate["source_input_findings"] = [source_finding()]
        paths = ["/source_input_findings/0"]
        expected_status = "conflict"
    isolated = isolate_source_review(candidate, material)
    records = {row["path"]: row for row in isolated["validation"]["records"]}
    for path in paths:
        _, table, index = path.split("/")
        assert records[path]["status"] == expected_status
        assert records[path]["record_sha256"] == canonical_sha256(candidate[table][int(index)])
    assert isolated["validation"]["candidate"] == candidate


def test_deterministic_malformed_review_json_yields_record_diagnostics(selected):
    _, _, _, material, original = selected
    variants = []
    for table in ("findings", "input_contract_checks", "input_projection_checks", "source_input_findings"):
        for bad in (None, False, 0, "bad", {}, [None], [[{}]], [{"unknown": []}]):
            candidate = deepcopy(original)
            candidate[table] = deepcopy(bad)
            variants.append((table + ":" + repr(bad), candidate))
    for bad in (None, [], {}, [None], {"nested": []}, 0, False):
        candidate = deepcopy(original)
        candidate["input_contract_checks"][0]["obligation_id"] = deepcopy(bad)
        variants.append(("obligation_id:" + repr(bad), candidate))
        candidate = deepcopy(original)
        candidate["findings"] = [{**representation_finding(), "target_ids": [deepcopy(bad)]}]
        variants.append(("target_ids:" + repr(bad), candidate))
        candidate = deepcopy(original)
        candidate["source_input_findings"] = [{**source_finding(), "kind": deepcopy(bad)}]
        variants.append(("source_kind:" + repr(bad), candidate))
        candidate = deepcopy(original)
        candidate["input_projection_checks"] = [{"scope_ids": [deepcopy(bad)]}]
        variants.append(("projection_scope:" + repr(bad), candidate))
    before = deepcopy(material)
    for name, candidate in variants:
        isolated = isolate_source_review(candidate, material)
        assert isolated["validation"]["diagnostics"], name
        assert isolated["validation"]["candidate"] == candidate, name
        assert isolated["validation"]["candidate_sha256"] == canonical_sha256(candidate), name
    assert len(variants) == 60
    assert material == before
