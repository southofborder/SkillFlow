from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.annotation_wire import compile_flat_response
from skillflow.document_guided.fragment_revision import merge_sensitivity_revision, sensitivity_scope
from skillflow.document_guided.fragments import assemble_fragments, split_fragments
from skillflow.document_guided.online import validate_step
from skillflow.document_guided.sensitivity_entries import entry_catalogue, resolve_labels, retain_valid_entries
from skillflow.document_guided.source_review import prepare_review_material, validate_source_review
from skillflow.doe.sensitivity_engine import equivalent_entry_declarations
from skillflow.doe.sensitivity_results import SensitivityResult
from skillflow.propagation.contracts.task import task_source_files
from tests.document_guided.test_annotation_wire import sample
from tests.doe.input_review_helpers import source_review_response


def materials():
    material, wire = sample()
    p = split_fragments(wire)
    cfg, files = material["cfg"], task_source_files(material["source"])
    catalogue = entry_catalogue(cfg, p["processing"])
    key, = catalogue
    label = {"entry_id": key, "origin": "tool_response", "applicability": "source_field", "property": "value", "path": ["private"],
             "label": "Customer identifier", "evidences": p["processing"]["ir_semantics"]["ir_call"]["evidences"]}
    return material, p, cfg, files, catalogue, label


def test_model_can_label_real_tool_response_only_including_local_repair():
    m, p, cfg, files, c, label = materials()
    ctx = {"cfg": cfg, "source": m["source"], "files": files, "processing": p["processing"]}
    value = validate_step("sensitivity_fragment", {"declarations": [label]}, context=ctx)
    record, = value["declarations"]
    assert record["value"] == {"kind": "local", "name": "reply"}
    assert record["source_entry_location"] == "tool:Service"
    with pytest.raises(StructuralValidationError):
        validate_step("sensitivity_fragment", {"declarations": [record]}, context=ctx)
    invalid = {**label, "entry_id": "result_returned_by_compute"}
    with pytest.raises(StructuralValidationError, match="catalogue"):
        validate_step("sensitivity_fragment", {"declarations": [invalid]}, context=ctx)
    f = {"owner": "sensitivity", "domain": "annotation", "target_ids": ["fragment:sensitivity:/declarations/0"]}
    scope = sensitivity_scope(cfg, cfg, p["processing"], p["processing"], [f], value)
    assert set(scope["slots"]) == {"ir_call"}
    assert scope["entry_catalogue"] == c
    assert scope["slots"]["ir_call"]["prior_entry_labels"] == [label]
    assert merge_sensitivity_revision(value, scope,
        {"slots": [{"instruction_id": "ir_call", "declarations": [label]}]}, files=files) == value


def test_missing_source_entry_is_a_reviewable_gap_without_a_sensitive_seed():
    m, p, cfg, files, _, label = materials()
    gap = {"instruction_id": "ir_call", "missing_from": "processing", "missing_entry": "Service reply field",
           "reason": "The declared response remains opaque; the missing reply field cannot be located.",
           "evidences": label["evidences"]}
    ctx = {"cfg": cfg, "source": m["source"], "files": files, "processing": p["processing"]}
    value = validate_step("sensitivity_fragment", {"entry_gaps": [gap], "declarations": []}, context=ctx)
    wire, raw, compiled, mapping = assemble_fragments(p["processing"], p["task-correspondence"], value, m)
    assert mapping["sensitivity_entry_gaps"] == [gap]
    assert compile_flat_response(wire, m)[3]["sensitivity_entry_gaps"] == [gap]
    review = prepare_review_material(files=files, cfg=cfg, task=m["task"], annotation=wire,
        raw_annotation=raw, compiled=compiled, mapping=mapping, generation="fragment-v1")
    result = validate_source_review(source_review_response(review, []), review)
    assert any(f.get("owner") == "processing" and "annotation:/ir_semantics/ir_call" in f["target_ids"]
               for f in result["findings"])
    assert not raw["ir_semantics"]["ir_call"]["sensitivity"]


def test_legacy_lexical_seed_cannot_bypass_ingress_validation_in_salvage():
    _, p, cfg, files, _, label = materials()
    legacy = {"instruction_id": "ir_return", "value": {"kind": "input", "index": 0},
              "label": "Downstream copy", "evidences": label["evidences"]}
    value, gaps = retain_valid_entries({"declarations": [label, legacy]}, cfg, p["processing"], files)
    assert [g["instruction_id"] for g in gaps] == ["ir_return"]
    assert [r["label"] for r in value["declarations"]] == [label["label"]]


def test_one_normal_correction_names_all_missing_entry_fields_and_keeps_other_labels():
    from skillflow.document_guided.fragments import fragment_correction_strategy
    from skillflow.document_guided.prompts import build_fragment_prompt
    m, fragments, cfg, files, _, label = materials()
    ctx = {"cfg": cfg, "source": m["source"], "files": files, "processing": fragments["processing"]}
    base = build_fragment_prompt("sensitivity", files=files, documents={"processing": fragments["processing"]},
                                 cfg=cfg, global_requirements="Preserve the source.")
    prior = {**label, "path": ["other"], "label": "Other sensitive field"}
    candidate = {"declarations": [prior, {k: v for k, v in label.items() if k not in {"origin", "applicability"}}]}
    with pytest.raises(StructuralValidationError) as error:
        validate_step("sensitivity_fragment", candidate, context=ctx)
    assert {d["path"] for d in error.value.diagnostics} == {"/declarations/1/origin", "/declarations/1/applicability"}
    strategy = fragment_correction_strategy("sensitivity")
    prompt = strategy.build_prompt(base, candidate, error.value.diagnostics)
    assert "applicability" in prompt and "origin" in prompt
    result = strategy.merge(candidate, {"replacements": [{"record_id": "/declarations/1", "value": label}]})
    assert result["declarations"][0] == prior
    assert len(validate_step("sensitivity_fragment", result, context=ctx)["declarations"]) == 2


def test_classification_can_share_a_fixed_location_but_ambiguous_addresses_have_distinct_entries():
    _, p, cfg, _, _, _ = materials()
    processing = p["processing"]
    slot = processing["ir_semantics"]["ir_call"]["segments"][0]["ops"]
    for name in ("env", "uncertain"):
        processing["locations"][name] = {"kind": "runtime_context", "name": name}
        for i in range(2):
            slot.append({"op": "read", "location": name, "output": name + str(i)})
    processing["locations"]["uncertain"].update(address_kind="unidentified", address_reason="Address unavailable")
    catalogue = entry_catalogue(cfg, processing)
    assert [len(e["accesses"]) for e in catalogue.values() if e["source"] == "env"] == [2]
    assert [len(e["accesses"]) for e in catalogue.values() if e["source"] == "uncertain"] == [1, 1]


def test_context_argument_uses_real_operand_anchor_and_rejects_overlapping_access_labels():
    _, fragments, cfg, files, _, sample_label = materials()
    from skillflow.propagation.contracts.references import cfg_instructions
    ir = cfg_instructions(cfg)["ir_call"]
    ir["inputs"].append({"type": "context_key", "identifier": "external_context"})
    slot = len(ir["inputs"]) - 1
    fragments["processing"]["locations"]["user_file"] = {"kind": "storage", "name": "request.json",
        "operand_refs": [{"instruction_id": "ir_call", "side": "input", "index": slot}]}
    catalogue = entry_catalogue(cfg, fragments["processing"])
    key, entry = next((k, row) for k, row in catalogue.items() if row["source"] == "external_context")
    label = {**sample_label, "entry_id": key, "origin": "file"}
    bound, = resolve_labels({"declarations": [label]}, catalogue, {"ir_call"}, files)["declarations"]
    assert bound["source_entry_location"] == "storage:request.json" and entry["origins"] == ["file"]
    with pytest.raises(StructuralValidationError, match="already covers"):
        resolve_labels({"declarations": [label, {**label, "applicability": "access",
                       "access_ids": [bound["source_access_id"]]}]}, catalogue, {"ir_call"}, files)


def test_resolved_seed_aliases_preserve_source_version_context_members_and_coverage():
    _, _, _, files, catalogue, label = materials()
    bound = resolve_labels({"declarations": [label]}, catalogue, {"ir_call"}, files)["declarations"][0]
    decl = {k: v for k, v in bound.items() if k != "instruction_id"}
    bucket = {"a": {"instruction_id": "ir", "scope_path": [], "declaration": decl},
              "b": {"instruction_id": "ir", "scope_path": [], "declaration": deepcopy(decl)}}
    reg = {"data1": {"origin": {"acquired_from": "tool:Service", "at": None}}}
    engine = SimpleNamespace(index=SimpleNamespace(data=reg, coverage={"ir": "processed"}),
                             nodes={"n": {"data_ids": ["data1"]}}, resolve=lambda *a: ["n"])
    assert equivalent_entry_declarations(engine, bucket) == {"a": ["a", "b"]}
    bucket["b"]["declaration"]["source_entry_context"] = "a" * 64
    assert equivalent_entry_declarations(engine, bucket) == {"a": ["a", "b"]}
    for row in bucket.values():
        row["declaration"]["source_entry_applicability"] = "access"
    assert equivalent_entry_declarations(engine, bucket) == {}
    bucket["b"]["declaration"] = deepcopy(decl)
    bucket["b"]["scope_path"] = ["events", 1]
    assert equivalent_entry_declarations(engine, bucket) == {}
    bucket["b"]["scope_path"] = []
    reg["data1"]["origin"]["at"] = "response_version"
    assert equivalent_entry_declarations(engine, bucket) == {}


def test_one_intrinsic_field_at_fifty_case_accesses_preserves_all_declaration_provenance():
    m, p, cfg, files, _, example_label = materials()
    proc = p["processing"]
    proc["locations"]["env"] = {"kind": "runtime_context", "name": "Environment"}
    cases = [{"name": str(i), "segments": [{"ops": [{"op": "read", "location": "env",
              "output": "env"}]}]} for i in range(50)]
    proc["ir_semantics"]["ir_call"]["segments"] = [{"kind": "cases", "cases": cases}]
    catalogue = entry_catalogue(cfg, proc)
    entry, = catalogue
    label = {**example_label, "entry_id": entry, "origin": "environment", "label": "private key"}
    engine = SimpleNamespace(index=SimpleNamespace(data={"root": {"origin": {
        "acquired_from": "runtime_context:Environment", "at": None}}}, coverage={"ir_call": "processed"}),
        nodes={"ref": {"data_ids": ["root"]}}, resolve=lambda *a: ["ref"])
    def classification(label):
        rows = resolve_labels({"declarations": [label]}, catalogue, {"ir_call"}, files)["declarations"]
        index = {f"d{i:02d}": {"declaration": {k: v for k, v in row.items() if k not in
                 {"instruction_id", "scope_path", "case_path"}}, "instruction_id": "ir_call", "scope_path": []}
                 for i, row in enumerate(rows)}
        return rows, equivalent_entry_declarations(engine, index)
    rows, aliases = classification(label)
    assert len(rows) == len({r["source_entry_context"] for r in rows}) == len({r["source_access_id"] for r in rows}) == 50
    assert aliases == {"d00": [f"d{i:02d}" for i in range(50)]}
    only = [rows[0]["source_access_id"], rows[-1]["source_access_id"]]
    limited, aliases = classification({**label, "applicability": "access", "access_ids": only})
    assert len(limited) == 2 and not aliases
    with pytest.raises(StructuralValidationError, match="access_ids"):
        classification({**label, "access_ids": only})


def test_distinct_straight_line_blocks_share_context_and_conditional_edges_do_not():
    from skillflow.document_guided.sensitivity_entries import _straight_line_contexts
    cfg = {"entry_block_id": "a", "blocks": {x: {} for x in "abcde"}, "edges": [
        {"source_block_id": x, "target_block_id": y, "condition_text": c}
        for x, y, c in (("a", "b", None), ("b", "c", "yes"), ("b", "d", "no"),
                        ("c", "e", None), ("d", "e", None))]}
    regions = _straight_line_contexts(cfg)
    assert regions["a"] == regions["b"]
    assert len({regions[k] for k in "bcde"}) == 4


def test_archived_v10_fixture_has_exact_shape_and_v11_requires_the_alias_table():
    old = json.loads((Path(__file__).parents[1] / "doe/fixtures/sensitivity-v10-result.json").read_bytes())
    assert SensitivityResult.model_validate(old).model_dump(mode="json") == old
    with pytest.raises(ValueError, match="declaration_aliases"):
        SensitivityResult.model_validate({**old, "declaration_aliases": {}})
    with pytest.raises(ValueError, match="declaration_aliases"):
        SensitivityResult.model_validate({**old, "schema_version": "skillflow-sensitivity-review-v11"})
    tampered = deepcopy(old)
    tampered["derivations"]["demand"]["forged"] = {"selector_ref": None}
    with pytest.raises(ValueError, match="selector_ref"):
        SensitivityResult.model_validate(tampered)
