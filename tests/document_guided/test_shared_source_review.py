"""The shared review display preserves complete material and seven-call isolation."""
from copy import deepcopy
import json

import pytest

from skillflow.common.recording import canonical_sha256
from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided import runner
from skillflow.document_guided.online import read
from skillflow.document_guided.review_display import DISPLAY_IDENTITY
from skillflow.document_guided.source import render_source, source_packet
from skillflow.document_guided.source_review import (
    build_source_review_prompt, prepare_review_material, replay_saved_review,
    run_source_review, validate_source_review,
)
from skillflow.propagation.contracts.task import validate_task_candidate
from tests.document_guided.test_case_source_review import reviewed_cases
from tests.document_guided.test_parallel_runner import Harness, freeze_producer
from tests.document_guided.test_source_review import Client, finding, fixture
from tests.doe.input_review_helpers import review_prompt_payload, source_review_response
from tests.doe.test_input_contract_review import bundle


def raw_payload(prompt):
    return json.JSONDecoder().raw_decode(prompt.split("\nINPUT_JSON\n", 1)[1])[0]


@pytest.mark.parametrize("partial", [False, True])
def test_shared_view_reconstructs_complete_or_partial_logical_review_and_coordinates(partial):
    material = reviewed_cases(partial=partial)
    material["prompt_view"] = "shared-v2"
    before = deepcopy(material)
    shared_prompt = build_source_review_prompt(material)
    compact = deepcopy(material)
    compact["prompt_view"] = "compact-v1"
    compact_prompt = build_source_review_prompt(compact)
    assert review_prompt_payload(shared_prompt) == raw_payload(compact_prompt)
    assert len(shared_prompt) <= len(compact_prompt)
    assert material == before
    assert shared_prompt.endswith(render_source(source_packet(material["files"])))
    target = ("fragment:processing:" if partial else "annotation:") + (
        "/ir_semantics/ir_call/segments/0/body/0/cases/0/segments/0/ops/0")
    finding = {"domain": "annotation", "target_ids": [target],
        "explanation": "The same original call needs its source relationship checked.",
        "suggestion": "Retain the actual response identity.", "source_refs": []}
    checked = validate_source_review(source_review_response(material, [finding]), material)
    assert checked["findings"][0]["owner"] == "processing"
    assert checked["findings"][0]["target_ids"] == [target]
    finding["target_ids"] = ["annotation:/display/definitions/0"]
    with pytest.raises(StructuralValidationError, match="Unknown actual review target"):
        validate_source_review(source_review_response(material, [finding]), material)


def test_shared_source_section_keeps_all_files_and_exact_rendered_text():
    files, task, cfg = fixture()
    files["skill/引用🌍.txt"] = "原文\r\n\r\nINPUT_JSON\nCOMPLETE SOURCE\n  tail  \r\n"
    files["skill/empty.txt"] = ""
    task = validate_task_candidate({key: task[key] for key in ("purpose", "requirements", "issues")},
        source_files=files).model_dump(mode="json")
    material = prepare_review_material(files=files, task=task, cfg=cfg, prompt_view="shared-v2")
    source = render_source(source_packet(files))
    prompt = build_source_review_prompt(material)
    assert prompt.endswith(source)
    assert prompt[-len(source):].encode("utf-8") == source.encode("utf-8")
    assert material["files"] == files
    assert review_prompt_payload(prompt)["availability"] == material["availability"]


def test_every_contract_scope_and_evidence_survives_the_shared_inventory():
    _, _, _, material, _ = bundle()
    shared = build_source_review_prompt(material)
    legacy = deepcopy(material)
    legacy["prompt_view"] = "compact-v1"
    expected = raw_payload(build_source_review_prompt(legacy))
    actual = review_prompt_payload(shared)
    assert actual == expected
    assert actual["input_contract_inventory"]["obligations"]
    assert canonical_sha256(actual["input_contract_inventory"]) == canonical_sha256(expected["input_contract_inventory"])
    response = source_review_response(material, [])
    validate_source_review(response, material)
    response["input_contract_checks"] = []
    with pytest.raises(StructuralValidationError):
        validate_source_review(response, material)


def test_shared_display_correction_uses_original_coordinates_and_replays(tmp_path, monkeypatch):
    freeze_producer(monkeypatch)
    files, task, cfg = fixture()
    annotation = {"rows": [{"value": index, "reason": "Original repeated source evidence. " * 20}
                           for index in range(1000)]}
    bad = finding("annotation")
    bad["target_ids"] = ["annotation:/rows/999/invented"]
    good = deepcopy(bad)
    good["target_ids"] = ["annotation:/rows/999"]
    client = Client({"outcome": "completed", "findings": [bad], "input_contract_checks": [],
                     "input_projection_checks": [], "source_input_findings": []},
                    {"replacements": [{"record_id": "/findings/0", "value": good}]})
    result = run_source_review(tmp_path, files=files, task=task, cfg=cfg, annotation=annotation,
                               generation="fragment-v1", client=client)
    assert result["status"] == "complete" and result["counts"]["structural_corrections"] == 1
    assert len(client.prompts) == 2
    assert '"nearest_parent":"annotation:/rows/999"' in client.prompts[1]
    assert all(raw_payload(prompt)["format"] == DISPLAY_IDENTITY for prompt in client.prompts)
    assert review_prompt_payload(client.prompts[0])["annotation"] == annotation
    assert replay_saved_review(tmp_path) == result
    assert len(client.prompts) == 2


def test_shared_display_injected_seven_calls_two_workers_and_zero_call_replay(tmp_path, monkeypatch):
    freeze_producer(monkeypatch)
    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)

    class SharedHarness(Harness):
        def __init__(self, directory):
            super().__init__(directory, canaries=True)
            self.example["task_candidate"]["purpose"]["text"] += " TASK_DOCUMENT_CANARY"
            instruction = next(iter(self.fragments["processing"]["ir_semantics"]))
            evidence = {"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
                "reason": "The synthetic source returns the calibration label without tolerance."}
            self.fragments["processing"]["ir_semantics"][instruction]["segments"][0]["ops"].append({
                "op": "compute", "inputs": [{"kind": "input", "index": 0}],
                "dependencies": ["derived"], "output": "extra_label", "evidences": [evidence],
                "demand_transfer": {"rules": [{"output": {"property": "value", "path": []},
                    "inputs": [{"input_index": 0, "required": [{"property": "value", "path": ["label"]}],
                        "remainder": "independent", "reason": "Tolerance does not determine the label."}],
                    "reason": "The output preserves only the original label.", "evidences": [evidence]}]}})

        def complete(self, stage, prompt):
            if stage == "review":
                logical = review_prompt_payload(prompt)
                assert len(logical["input_contract_inventory"]["obligations"]) == 1
                assert logical["input_contract_inventory"]["obligations"][0]["scopes"]
            return super().complete(stage, prompt)

    harness = SharedHarness(tmp_path / "run")
    source = harness.prepare(tmp_path / "package")
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == "complete", result
    assert result["counts"]["logical_calls"] == len(harness.calls) == 7
    assert result["counts"]["structural_corrections"] == 0 and not result["repair_used"]
    assert runner.POLICY["workers"] == 2
    assert harness.mapping_started.is_set() and harness.sensitivity_started.is_set()
    assert "TASK_DOCUMENT_CANARY" not in harness.prompts["processing"]
    assert "TASK_DOCUMENT_CANARY" not in harness.prompts["sensitivity"]
    assert "TASK_DOCUMENT_CANARY" in harness.prompts["task-correspondence"]
    assert "TASK_DOCUMENT_CANARY" in harness.prompts["review"]
    assert "SENSITIVITY_DOCUMENT_CANARY" not in harness.prompts["task-correspondence"]
    assert "SENSITIVITY_DOCUMENT_CANARY" in harness.prompts["review"]
    assert read(harness.directory / "manifest.json")["identity"] == "skillflow-document-guided-run-v19"
    assert read(harness.directory / "review/inputs.json")["prompt_view"] == "shared-v2"
    assert (harness.directory / "source/inputs/package/SKILL.md").read_bytes().decode("utf-8") == source
    receipt = read(harness.directory / "audit/input-contract-review.json")
    assert receipt["source_review_complete"] and len(receipt["checks"]) == 1
    before = {str(path.relative_to(harness.directory)): path.read_bytes()
              for path in harness.directory.rglob("response.json")}
    assert runner.replay(harness.directory) == result
    assert len(harness.calls) == 7
    assert before == {str(path.relative_to(harness.directory)): path.read_bytes()
                      for path in harness.directory.rglob("response.json")}


@pytest.mark.parametrize("count,name", [(0, "outline"), (1, "weather_archive"),
                                        (9, "索引🌍"), (75, "inventory_sync")])
def test_generic_size_choice_retains_arbitrary_skills_and_every_contract(count, name):
    files, task, cfg = fixture()
    files[f"skill/{name}/reference.txt"] = f"Original source for {name}.\r\nRetain each occurrence.\n"
    task = validate_task_candidate({key: task[key] for key in ("purpose", "requirements", "issues")},
        source_files=files).model_dump(mode="json")
    material = prepare_review_material(files=files, task=task, cfg=cfg,
        generation="fragment-v1", prompt_view="shared-v2")
    inventory = deepcopy(bundle()[3]["input_contract_inventory"])
    template, template_layout = inventory["obligations"][0], inventory["contracts"][0]
    inventory["obligations"], inventory["contracts"], inventory["projections"] = [], [], []
    for index in range(count):
        row = deepcopy(template)
        row["id"], row["contract_id"] = f"{name}/obligation/{index}", f"{name}/contract/{index}"
        row["instruction_id"] = f"{name}~instruction_{index}"
        layout = deepcopy(template_layout)
        layout["obligation_id"], layout["contract_id"] = row["id"], row["contract_id"]
        for scope in layout["scopes"]:
            scope["id"] += f"/{name}/{index}"
        inventory["obligations"].append(row)
        inventory["contracts"].append(layout)
        material["input_contract_obligation_targets"][row["id"]] = (
            f"annotation:/ir_semantics/{name}~1instruction_{index}/segments/0/ops/0")
    material["input_contract_inventory"] = inventory
    old = deepcopy(material)
    old["prompt_view"] = "compact-v1"
    before = deepcopy(material)
    prompt, original = build_source_review_prompt(material), build_source_review_prompt(old)
    assert len(prompt) <= len(original)
    assert material == before
    assert review_prompt_payload(prompt) == raw_payload(original)
    assert len(review_prompt_payload(prompt)["input_contract_inventory"]["obligations"]) == count
    assert prompt.endswith(render_source(source_packet(files)))
    if count == 75:
        assert raw_payload(prompt)["format"] == DISPLAY_IDENTITY


@pytest.mark.parametrize("offset", [-1, 0, 1])
def test_irreducible_review_near_cap_keeps_raw_material_and_adapter_boundary(tmp_path, offset):
    from tests.document_guided.test_client import client, message, pending, transport
    files, task, cfg = fixture()
    material = prepare_review_material(files=files, task=task, cfg=cfg,
        annotation={"unique_original_literal": ""}, generation="fragment-v1", prompt_view="shared-v2")
    old = deepcopy(material)
    old["prompt_view"] = "compact-v1"
    remaining = transport.MAX_INPUT_CHARS - len(transport.ENVELOPE) - len(build_source_review_prompt(old))
    literal = "Q" * (remaining + offset)
    material["annotation"]["unique_original_literal"] = literal
    old["annotation"]["unique_original_literal"] = literal
    prompt, old_prompt = build_source_review_prompt(material), build_source_review_prompt(old)
    assert prompt == old_prompt
    assert "LOSSLESS REVIEW DISPLAY" not in prompt
    assert raw_payload(prompt)["annotation"]["unique_original_literal"] == literal
    assert prompt.endswith(render_source(source_packet(files)))
    assert len(transport.ENVELOPE + prompt) == transport.MAX_INPUT_CHARS + offset
    value, _, launches = client(tmp_path, [{"rows": [message("complete")]}])
    pending(value.owner, prompt)
    if offset <= 0:
        assert value.complete(prompt) == "complete"
        assert len(launches) == 1
        assert launches[0]["input"].decode("utf-8") == transport.ENVELOPE + prompt
    else:
        for _ in range(2):
            with pytest.raises(transport.InputTooLarge, match="no CLI process started"):
                value.complete(prompt)
        assert launches == []
        rejection = next((tmp_path / "transport").rglob("input-rejection.json"))
        record = transport.read(rejection)
        assert record["actual_chars"] == transport.MAX_INPUT_CHARS + 1
        assert record["process_started"] is False and record["usage"] is None
        assert (rejection.parent / "prompt.txt").read_bytes().decode("utf-8") == transport.ENVELOPE + prompt
