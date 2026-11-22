"""Bound CFG editing permissions preserve source and full graph validation."""
from copy import deepcopy
import json

import pytest

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.recording import canonical_sha256, injected_factory, read_json
from skillflow.common.structural_correction import ResponseChain, StructuralCorrectionLimitReached
from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.fragments import fragment_correction_strategy
from skillflow.document_guided.online import CONFIG, validate_step
from tests.graph.extraction.test_compiler_causal_diagnostics import loop_candidate
from tests.document_guided.test_parallel_runner import _cfg_wire


SOURCE = "Original complete source. 保留每次读取、过滤和迭代结果。\n"


def two_loops():
    first, second = loop_candidate("left"), loop_candidate("right")
    first["blocks"].extend(second["blocks"])
    first["edges"].extend(second["edges"])
    return _cfg_wire(first)


def corrections(candidate, *, omit_carry=False):
    updates = []
    for prefix, head, body in (("left", 1, 2), ("right", 6, 7)):
        head_value, body_value = deepcopy(candidate["blocks"][head]), deepcopy(candidate["blocks"][body])
        head_value["instructions"][0]["inputs"][1]["identifier"] = prefix + "_retained"
        body_value["instructions"].insert(1, {"opcode": "retain", "inputs": [{"type": "result", "identifier": prefix + "_current"}],
            "outputs": [{"type": "result", "identifier": prefix + "_retained"}]})
        updates.append({"record_id": f"/blocks/{head}", "value": head_value})
        if not omit_carry:
            updates.append({"record_id": f"/blocks/{body}", "value": body_value})
    return {"replacements": updates}


def validate(value):
    return validate_step("cfg_wire_v5", value, context={"files": {"skill/SKILL.md": SOURCE}})


@pytest.mark.parametrize("omit_carry", [False, True])
def test_one_dependency_correction_and_zero_call_replay_revalidate_the_entire_graph(tmp_path, omit_carry):
    candidate = two_loops()
    reply = corrections(candidate, omit_carry=omit_carry)
    answers = [json.dumps(candidate, ensure_ascii=False), json.dumps(reply, ensure_ascii=False)]
    prompts = []

    class Client:
        def complete(self, prompt):
            prompts.append(prompt)
            if len(prompts) == 2:
                assert SOURCE in prompt and "MECHANICAL RECORD CORRECTION" in prompt
                payload = json.loads(prompt.rsplit("\n", 1)[1])
                assert payload["candidate"] == candidate
                assert set(payload["allowed_record_ids"]) == {f"/blocks/{i}" for i in (0, 1, 2, 3, 5, 6, 7, 8)}
                assert payload["correction_scope"]["candidate_sha256"] == canonical_sha256(candidate)
                assert len(payload["diagnostics"]) == 3
                assert payload["diagnostics"][-1]["code"] == "CFG_STRUCTURE_INVALID"
                assert payload["diagnostics"][-1]["context"]["cfg_rejected_block_cascade"]["complete"]
            return answers.pop(0)

    args = dict(prefix="calls", base_prompt="Generate the full source CFG.\n" + SOURCE,
        request_kind="cfg_wire_v5", config=CONFIG, writer=ArtifactWriter(()), validate=validate, max_corrections=1)
    chain = ResponseChain(tmp_path, **args, correction_strategy=fragment_correction_strategy("cfg"),
        client_factory=injected_factory(Client()))
    if omit_carry:
        with pytest.raises(StructuralCorrectionLimitReached):
            chain.run()
    else:
        assert chain.run()
    assert len(prompts) == 2 and not answers and not (tmp_path / "calls/a003").exists()
    merged = read_json(tmp_path / "calls/a002/merged-candidate.json")
    assert merged["edges"] == candidate["edges"] and merged["entry_block_ref"] == candidate["entry_block_ref"]
    changed = {int(row["record_id"].rsplit("/", 1)[1]) for row in reply["replacements"]}
    for i, block in enumerate(candidate["blocks"]):
        if i not in changed:
            assert merged["blocks"][i] == block
    saved = {str(path): path.read_bytes() for path in tmp_path.rglob("*.json")}
    replay = ResponseChain(tmp_path, **args, correction_strategy=fragment_correction_strategy("cfg"), replay=True)
    if omit_carry:
        with pytest.raises(StructuralCorrectionLimitReached):
            replay.run()
    else:
        assert replay.run() == chain.value
    assert replay.snapshot() == chain.snapshot() and len(prompts) == 2
    assert saved == {str(path): path.read_bytes() for path in tmp_path.rglob("*.json")}


def strategy_for(candidate):
    with pytest.raises(StructuralValidationError) as caught:
        validate(candidate)
    strategy = fragment_correction_strategy("cfg")
    strategy.build_prompt("Complete source.\n" + SOURCE, candidate, caught.value.diagnostics)
    return strategy


@pytest.mark.parametrize("mutation", ["candidate", "permissions", "diagnostics", "block_identity", "outside_record"])
def test_record_merge_rejects_stale_scope_or_topology_changes(mutation):
    candidate = two_loops()
    strategy = strategy_for(candidate)
    reply = corrections(candidate)
    if mutation == "candidate":
        candidate["constraints"] = ["Changed source requirement"]
    elif mutation == "permissions":
        strategy.selected["/blocks/4"] = candidate["blocks"][4]
    elif mutation == "diagnostics":
        strategy.cfg_diagnostics[0]["message"] += " altered"
    elif mutation == "block_identity":
        reply["replacements"][0]["value"]["block_ref"] = "new_topology"
    else:
        reply["replacements"].append({"record_id": "/edges/0", "value": candidate["edges"][0]})
    with pytest.raises(StructuralValidationError):
        strategy.merge(candidate, reply)


def test_true_missing_endpoint_retains_complete_fallback_evidence_and_all_raw_errors():
    candidate = two_loops()
    candidate["edges"][2]["target_block_ref"] = "absent"
    with pytest.raises(StructuralValidationError) as caught:
        validate(candidate)
    assert any(row["code"] == "EDGE_TARGET_NOT_FOUND" for row in caught.value.diagnostics)
    strategy = fragment_correction_strategy("cfg")
    prompt = strategy.build_prompt(SOURCE, candidate, caught.value.diagnostics)
    assert not strategy.selected and "MECHANICAL RECORD CORRECTION" not in prompt
    assert SOURCE in prompt and "CFG CORRECTION SCOPE" in prompt
    payload = json.loads(prompt.split("\nCURRENT_CANDIDATE_AND_DIAGNOSTICS\n", 1)[1])
    assert payload["candidate"] == candidate and len(payload["diagnostics"]) == len(caught.value.diagnostics)
    assert "EDGE_TARGET_NOT_FOUND" in prompt and "CFG_STRUCTURE_INVALID" in prompt
