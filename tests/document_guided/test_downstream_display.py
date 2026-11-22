"""Downstream prompt encoding preserves full source, scope and owner boundaries."""
from copy import deepcopy
import json

import pytest

from skillflow.common.prompt_format import compact_json
from skillflow.common.structural_correction import correction_prompt, _current_diagnostics, VERSION
from skillflow.document_guided.annotation_wire import expression_reference_view
from skillflow.document_guided.fragment_display import (
    INPUT_MARKER, compact_fragment_correction, expand_fragment_material,
    fragment_prompt_parts, pack_fragment_material, render_fragment_material,
)
from skillflow.document_guided.fragments import fragment_correction_strategy
from skillflow.document_guided.prompts import (
    build_correspondence_revision_prompt, build_fragment_prompt, build_graph_updates_prompt,
    build_processing_revision_prompt, build_sensitivity_revision_prompt,
)
from skillflow.document_guided.source import prompt_cfg, render_source, source_packet
from tests.document_guided.test_boundary_prompt_alignment import material_inputs


def inputs():
    material, fragments, files = material_inputs()
    files = {**files, "skill/unused.txt": "中文 source\r\nFRAGMENT_INPUT_JSON\n$ref is literal. 😀"}
    return material, fragments, files


def assert_source(prompt, files):
    source = "RELATED SOURCE\n" + render_source(source_packet(files)) + "\n\nOUTPUT REQUIREMENTS\n"
    assert source in prompt
    assert prompt.count(source) == 1


def repetitive_payload(owner="sensitivity"):
    evidence = {"file": "skill/example.ts", "start_line": 1, "end_line": 2,
                "reason": "Retain this source-supported relationship in this exact occurrence. " * 12}
    return {"owner": owner, "documents": {"processing": {"ir_semantics": {
        f"ir_{index}": {"evidences": [evidence], "output_bindings": [
            {"output_index": 0, "value": {"kind": "input", "index": 0}}]}
        for index in range(40)}}}, "cfg": {"blocks": []}}


def test_generic_codec_is_smaller_exact_and_independent_at_every_occurrence():
    value = repetitive_payload()
    value["literals"] = [{"$ref": "plain", "value": False}, {"$rows": [], "value": 0},
                         {"$literal_object": [["x", 1]], "value": 0.0}, {"value": None}]
    before = compact_json(value)
    packed = pack_fragment_material(value)
    assert len(compact_json(packed)) < len(before)
    assert pack_fragment_material(value) == packed
    assert compact_json(expand_fragment_material(packed)) == before
    expanded = expand_fragment_material(packed)
    expanded["documents"]["processing"]["ir_semantics"]["ir_0"]["evidences"][0]["reason"] = "changed"
    assert expanded["documents"]["processing"]["ir_semantics"]["ir_1"]["evidences"][0]["reason"] != "changed"
    assert compact_json(value) == before
    altered = deepcopy(packed)
    altered["logical_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="logical identity"):
        expand_fragment_material(altered)
    with pytest.raises(ValueError, match="owner"):
        pack_fragment_material({"owner": "task", "documents": {}})


@pytest.mark.parametrize("owner", ["sensitivity", "task-correspondence"])
@pytest.mark.parametrize("repair", [False, True])
def test_normal_and_full_revision_keep_every_input_and_complete_source(owner, repair):
    material, fragments, files = inputs()
    previous = {"previous_fragment": fragments[owner], "source_rechecks": [
        {"target_id": "ir_call", "source_refs": [{"file": "skill/unused.txt", "start_line": 1, "end_line": 1}]}]}
    kwargs = {"task": material["task"]} if owner == "task-correspondence" else {}
    prompt = build_fragment_prompt(owner, files=files, documents={"processing": fragments["processing"]},
        cfg=material["cfg"], global_requirements="Keep every source obligation.",
        repair_context=previous if repair else None, **kwargs)
    _, value, suffix = fragment_prompt_parts(prompt)
    assert value["owner"] == owner
    assert value["documents"]["processing"] == fragments["processing"]
    assert value["cfg"] == prompt_cfg(material["cfg"], packet=source_packet(files))
    if repair:
        assert value["repair_context"] == previous
        assert "not an implicit merge" in prompt
    else:
        assert "repair_context" not in value
    if owner == "task-correspondence":
        assert value["task"] == material["task"]
        assert value["expression_references"] == expression_reference_view(fragments["processing"])
    else:
        assert not {"task", "expression_references", "runtime_contract"} & value.keys()
        assert compact_json(material["task"]) not in prompt
    assert_source(prompt, files)
    assert suffix.startswith("\n\nGLOBAL REQUIREMENTS AND LIMITATIONS\n")


@pytest.mark.parametrize("owner", ["sensitivity", "task-correspondence"])
@pytest.mark.parametrize("finite", [False, True])
def test_corrections_share_all_original_inputs_and_exact_context(owner, finite):
    value = repetitive_payload(owner)
    base = ("STEP RESPONSIBILITY\nAnalyze.\n\nPREVIOUS WORK\n" +
            render_fragment_material(owner, {key: item for key, item in value.items() if key != "owner"}) +
            "\n\nGLOBAL REQUIREMENTS AND LIMITATIONS\nKeep source.\n\nRELATED SOURCE\n" +
            "1: FRAGMENT_INPUT_JSON\n2: original source\n\nOUTPUT REQUIREMENTS\nUse strict JSON.")
    candidate = {"declarations": list(value["documents"]["processing"]["ir_semantics"].values())}
    diagnostics = [{"code": "schema", "path": "/declarations/0/value", "message": "Correct this field."}]
    if finite:
        context = {"records": {"/declarations/0": candidate["declarations"][0]}, "diagnostics": diagnostics}
        fallback = base + "\nMECHANICAL RECORD CORRECTION\nReplace the selected record.\n" + compact_json(context)
    else:
        current, examples = _current_diagnostics(diagnostics)
        context = {"protocol": VERSION, "candidate": candidate, "diagnostics": current, "format_examples": examples}
        fallback = correction_prompt(base, candidate, diagnostics)
    result = compact_fragment_correction(base, fallback, context)
    assert len(result) < len(fallback)
    _, merged, suffix = fragment_prompt_parts(result)
    assert {key: item for key, item in merged.items() if key != "correction"} == value
    assert merged["correction"] == context
    assert suffix == fragment_prompt_parts(base)[2]
    if finite:
        assert "Replace the selected record." in result
    else:
        assert "Return one complete replacement response" in result


@pytest.mark.parametrize("owner", ["sensitivity", "task-correspondence"])
@pytest.mark.parametrize("malformed", [False, True])
def test_real_strategy_uses_exact_finite_or_whole_correction_material(owner, malformed):
    material, fragments, files = inputs()
    candidate = deepcopy(fragments[owner])
    key = "declarations" if owner == "sensitivity" else "realizations"
    if not candidate[key]:
        candidate[key] = [{"instruction_id": "ir_call", "label": "Credential",
                           "value": {"kind": "local", "name": "reply"}}]
    repair = {"previous_fragment": candidate, "source_rechecks": []}
    kwargs = {"task": material["task"]} if owner == "task-correspondence" else {}
    base = build_fragment_prompt(owner, files=files, documents={"processing": fragments["processing"]},
        cfg=material["cfg"], global_requirements="Keep source.", repair_context=repair, **kwargs)
    diagnostic = {"code": "schema", "path": "" if malformed else f"/{key}/0",
                  "message": "Correct the declared representation."}
    strategy = fragment_correction_strategy(owner)
    supplied = '{"duplicate":1,"duplicate":2}' if malformed else candidate
    result = strategy.build_prompt(base, supplied, [diagnostic])
    assert_source(result, files)
    parsed = fragment_prompt_parts(result)
    assert parsed is not None
    logical = parsed[1]
    assert logical["repair_context"] == repair
    if "correction" in logical:
        context = logical["correction"]
    else:
        # A tiny correction can remain a complete suffix to the encoded base.
        context = json.loads(result.rsplit("\n", 1)[1])
    if malformed:
        assert context["candidate"] == supplied
    else:
        assert context["records"] == {f"/{key}/0": candidate[key][0]}
    assert context["diagnostics"] == [diagnostic]
    if not malformed:
        replacement = deepcopy(candidate[key][0])
        replacement["instruction_id" if owner == "sensitivity" else "requirement_id"] = "corrected_identity"
        merged = strategy.merge(candidate, {"replacements": [{"record_id": f"/{key}/0", "value": replacement}]})
        expected = deepcopy(candidate)
        expected[key][0] = replacement
        assert merged == expected


@pytest.mark.parametrize("owner", ["processing", "sensitivity", "task-correspondence", "cfg"])
def test_scoped_revision_preserves_full_scope_and_owner_context(owner):
    material, fragments, files = inputs()
    scope = {"slots": {f"slot_{i}": {"processing": fragments["processing"], "keepable": i % 2 == 0}
                       for i in range(12)}, "unresolved_targets": ["evidenced-target"]}
    if owner == "processing":
        contract = {"rules": ["one strict supported runtime"]}
        prompt = build_processing_revision_prompt(files=files, flow="Complete flow.",
            runtime_contract=contract, scope=scope, global_requirements="Keep source.")
    elif owner == "sensitivity":
        prompt = build_sensitivity_revision_prompt(files=files, scope=scope, global_requirements="Keep source.")
    elif owner == "task-correspondence":
        prompt = build_correspondence_revision_prompt(files=files, scope=scope, cfg=material["cfg"],
            processing=fragments["processing"], global_requirements="Keep source.")
    else:
        prompt = build_graph_updates_prompt(files=files, plan=scope)
    _, payload, _ = fragment_prompt_parts(prompt)
    assert payload["owner"] == owner
    assert payload["scope"] == scope
    if owner == "task-correspondence":
        assert payload["processing"] == fragments["processing"]
        assert payload["expression_references"] == expression_reference_view(fragments["processing"])
    elif owner == "processing":
        assert payload["documents"] == {"flow": "Complete flow."}
        assert payload["runtime_contract"] == contract
        assert "task" not in payload
    elif owner == "sensitivity":
        assert set(payload) == {"owner", "scope"}
    assert_source(prompt, files)


def test_custom_prompt_or_untrusted_marker_keeps_complete_correction():
    base = "Custom source text\nLOSSLESS FRAGMENT INPUT\nFRAGMENT_INPUT_JSON\n{}"
    context = {"candidate": '{"duplicate":1,"duplicate":2}', "diagnostics": []}
    fallback = base + "\nCorrect the entire response.\n" + compact_json(context)
    assert fragment_prompt_parts(base) is None
    assert compact_fragment_correction(base, fallback, context) == fallback
