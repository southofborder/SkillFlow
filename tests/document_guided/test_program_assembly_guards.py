"""Typed source selection and program provenance do not reinterpret payloads."""
from copy import deepcopy
import json
import os
import subprocess
import sys

import pytest

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.fragments import split_fragments, validate_fragment
from skillflow.document_guided.online import load_step, prepare_step, read, run_step
from skillflow.document_guided.prompts import build_fragment_prompt
from skillflow.document_guided.source import select_fragment_source
from tests.document_guided.test_annotation_wire import sample
from tests.document_guided.test_online import Client
from tests.document_guided.test_whole_steps import source_owner


def test_runtime_literals_do_not_request_source_files_and_typed_spans_stay_exact():
    files = {"skill/SKILL.md": "Declared purpose.\n", "skill/code.py": "one\ntwo\nthree\nfour\n"}
    p = {"ir_semantics": {"ir_call": {"evidences": [{"file": "skill/code.py", "start_line": 2, "end_line": 2}],
        "segments": [{"ops": [{"op": "call", "location": "api", "inputs": [{"kind": "literal",
            "value": {"path": "skill/runtime-input.json", "evidences": [{"file": "skill/also-data.txt", "start_line": 1, "end_line": 1}]}}],
            "output": "reply"}]}]}}}
    packet = select_fragment_source(files, p)
    assert [(span["file"], span["start_line"], span["end_line"]) for span in packet["ranges"]] == [
        ("skill/SKILL.md", 1, 1), ("skill/code.py", 2, 2)]
    material, _ = sample()
    prompt = build_fragment_prompt("sensitivity", files=files, documents={"processing": p},
        cfg=material["cfg"], global_requirements="Keep source-supported relationships.")
    assert "skill/runtime-input.json" in prompt and "SOURCE skill/runtime-input.json" not in prompt
    # Typed evidence keeps its exact citation; the current phase also receives
    # the whole frozen source independently of that citation's range.
    assert "SOURCE skill/code.py:1-4" in prompt
    assert "SOURCE skill/code.py:2-2" not in prompt


def test_fragment_semantic_repair_receives_locations_without_cross_layer_review_prose():
    from skillflow.document_guided.runner import _fragment_repair_findings
    span = {"file": "skill/SKILL.md", "start_line": 1, "end_line": 1}
    review = {"findings": [{"domain": "annotation", "owner": owner,
        "target_ids": ["annotation:/realizations" if owner == "task-correspondence" else "annotation:/ir_semantics/ir_call/sensitivity"],
        "source_refs": [span], "explanation": "OTHER_LAYER_INTERPRETATION_CANARY",
        "suggestion": "Do not send this independent review judgment into a different semantic role."}
        for owner in ("task-correspondence", "sensitivity")]}
    for owner in ("task-correspondence", "sensitivity"):
        value = _fragment_repair_findings(review, owner)
        assert len(value) == 1 and value[0]["source_refs"] == [span]
        assert set(value[0]) == {"target_ids", "source_refs"}
        assert "OTHER_LAYER_INTERPRETATION_CANARY" not in str(value)


def test_mapping_source_selection_retains_task_only_evidence_without_sensitivity_leak():
    material, wire = sample()
    fragments = split_fragments(wire)
    task = deepcopy(material["task"])
    task["purpose"]["evidences"] = [{"file": "skill/requirements.md", "start_line": 2, "end_line": 2,
                                    "reason": "The declared purpose is specified here."}]
    files = {"skill/SKILL.md": "Source.\n", "skill/requirements.md": "one\nTwo.\nthree\n"}
    # A Task citation must not limit the complete current source view. This is
    # an input-isolation check, not a new semantic target response.
    p = {"ir_semantics": {}, "locations": {}}
    prompt = build_fragment_prompt("task-correspondence", files=files, documents={"processing": p},
        cfg=material["cfg"], task=task, global_requirements="Preserve requirements.")
    assert "SOURCE skill/requirements.md:1-3" in prompt
    assert "SOURCE skill/requirements.md:2-2" not in prompt
    assert "SENSITIVITY" not in prompt


def test_inherited_duplicate_source_is_a_local_structural_error_not_execution_error():
    material, wire = sample()
    p = split_fragments(wire)["processing"]
    citation = deepcopy(p["ir_semantics"]["ir_call"]["evidences"][0])
    p["ir_semantics"]["ir_call"]["evidences"] = [citation, deepcopy(citation)]
    value = {"declarations": [{"instruction_id": "ir_call", "value": {"kind": "local", "name": "reply"},
                               "label": "Confidential response"}]}
    with pytest.raises(StructuralValidationError) as error:
        validate_fragment("sensitivity", value, material, p)
    assert any(row["path"].startswith("/declarations/0") for row in error.value.diagnostics)


def test_empty_sensitivity_scope_can_route_an_omission_without_rebuilding_processing():
    from skillflow.document_guided.fragments import assemble_fragments
    from skillflow.document_guided.source_review import prepare_review_material, _annotation_owner
    material, wire = sample()
    fragments = split_fragments(wire)
    assembled, _, compiled, mapping = assemble_fragments(fragments["processing"],
        fragments["task-correspondence"], {"declarations": []}, material)
    files = {"skill/" + row["path"]: row["content"] for row in material["source"]["files"]}
    reviewed = prepare_review_material(files=files, task=material["task"], cfg=material["cfg"],
        annotation=assembled, compiled=compiled, mapping=mapping, generation="fragment-v1")
    target = next(row for row in reviewed["target_index"]
                  if row["id"] == "annotation:/ir_semantics/ir_call/sensitivity")
    assert target["owner"] == "sensitivity"
    assert assembled["ir_semantics"]["ir_call"]["sensitivity"] == []
    assert _annotation_owner("/expressions/0", {}) == "processing"


def test_accepted_fragment_cannot_acquire_unproven_program_validation_gaps(tmp_path):
    material, wire = sample()
    package_source = source_owner(tmp_path, {row["path"]: row["content"] for row in material["source"]["files"]})
    cfg = tmp_path / "cfg.json"
    ArtifactWriter(()).json(cfg, material["cfg"])
    owner = tmp_path / "processing"
    prepare_step(owner, "Return the processing fragment.", kind="processing_fragment",
                 context={"source_owner": package_source, "cfg_path": cfg}, max_corrections=1)
    fragment = split_fragments(wire)["processing"]
    client = Client(fragment)
    assert run_step(owner, client=client) == load_step(owner) == fragment
    result = read(owner / "result.json")
    result["validation_gaps"] = []
    ArtifactWriter(()).json(owner / "result.json", result)
    with pytest.raises(ValueError, match="validation coverage"):
        load_step(owner)
    assert client.calls == 1


def test_multiple_missing_ir_salvage_is_identical_across_fresh_hash_seeds():
    code = """import json
from tests.document_guided.test_fragments import fixture
from skillflow.document_guided.fragments import salvage_fragment
m,w,f=fixture()
p=f['processing']
key=next(iter(p['ir_semantics']))
p['ir_semantics']={key:p['ir_semantics'][key]}
m={'source':m['source'],'cfg':m['cfg']}
block=next(iter(m['cfg']['blocks'].values()))
for i in range(3):
    block['instructions'].insert(-1,{'id':'ir_missing_'+str(i),'opcode':'operation','inputs':[], 'outputs':[], 'constraints':[], 'metadata':{}})
value,gaps=salvage_fragment('processing',json.dumps(p),m)
assert len(gaps)>=3
print(json.dumps(gaps,sort_keys=True,separators=(',',':')))
"""
    outputs = []
    for seed in ("7", "83", "891"):
        environment = {**os.environ, "PYTHONHASHSEED": seed}
        result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                                encoding="utf-8", env=environment, check=True, timeout=45)
        outputs.append(result.stdout)
    assert outputs[0] == outputs[1] == outputs[2]
