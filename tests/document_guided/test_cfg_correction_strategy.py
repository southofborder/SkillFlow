"""Existing-record correction keeps complete context and strict whole checks."""
from copy import deepcopy
import json

import pytest

from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.fragments import fragment_correction_strategy
from skillflow.graph.extraction.compiler import compile_candidate
from tests.document_guided.test_cfg_correction_scope import diagnostics_for
from tests.graph.extraction.test_compiler_causal_diagnostics import loop_candidate


def _two_loops():
    candidate, second = loop_candidate("first"), loop_candidate("second")
    candidate["blocks"].extend(second["blocks"])
    candidate["edges"].extend(second["edges"])
    return candidate


def _four_replacements(candidate):
    replacements = []
    for prefix, head_index, body_index in [("first", 1, 2), ("second", 6, 7)]:
        head, body = (deepcopy(candidate["blocks"][index]) for index in (head_index, body_index))
        head["instructions"][0]["inputs"][1]["identifier"] = prefix + "_retained"
        body["instructions"].insert(1, {"instruction_ref": prefix + "_retain", "opcode": "retain",
            "inputs": [{"type": "result", "identifier": prefix + "_current"}],
            "outputs": [{"type": "result", "identifier": prefix + "_retained"}]})
        replacements.extend([{"record_id": f"/blocks/{head_index}", "value": head},
                             {"record_id": f"/blocks/{body_index}", "value": body}])
    return {"replacements": replacements}


def test_complete_candidate_and_source_remain_once_while_only_four_blocks_change():
    candidate = _two_loops()
    candidate["blocks"][9]["instructions"][0]["metadata"] = {"source": "UNSELECTED_SOURCE_RELATION"}
    original = deepcopy(candidate)
    diagnostics = diagnostics_for(candidate)
    strategy = fragment_correction_strategy("cfg")
    base = "FORMAT AND FULL SOURCE\nSOURCE_START\n完整源文\nSOURCE_END\n"
    prompt = strategy.build_prompt(base, candidate, diagnostics)
    assert prompt.startswith(base) and prompt.count("UNSELECTED_SOURCE_RELATION") == 1
    context = json.loads(prompt.rsplit("\n", 1)[1])
    assert context["candidate"] == candidate
    assert context["diagnostics"] == diagnostics
    assert set(context["allowed_record_ids"]) == {f"/blocks/{bi}" for bi in (0, 1, 2, 3, 5, 6, 7, 8)}
    merged = strategy.merge(candidate, _four_replacements(candidate))
    assert compile_candidate(merged).ok
    assert [bi for bi, (old, new) in enumerate(zip(candidate["blocks"], merged["blocks"])) if old != new] == [1, 2, 6, 7]
    assert merged["edges"] == candidate["edges"] and merged["entry_block_ref"] == candidate["entry_block_ref"]
    assert candidate == original


@pytest.mark.parametrize("mutation", ["candidate", "diagnostics", "scope", "selected"])
def test_scope_identity_is_rechecked_before_merge(mutation):
    candidate = _two_loops()
    strategy = fragment_correction_strategy("cfg")
    strategy.build_prompt("FULL SOURCE", candidate, diagnostics_for(candidate))
    if mutation == "candidate":
        candidate["blocks"][9]["block_name"] = "changed unselected context"
    elif mutation == "diagnostics":
        strategy.cfg_diagnostics[0]["context"]["cfg_correction_candidate_sha256"] = "0" * 64
    elif mutation == "scope":
        strategy.cfg_scope["evidence"]["dependencies"].pop()
    else:
        strategy.selected["/blocks/1"]["block_name"] = "changed permission"
    with pytest.raises(StructuralValidationError) as error:
        strategy.merge(candidate, _four_replacements(candidate))
    assert error.value.diagnostics[0]["code"] == "cfg_correction_identity"


@pytest.mark.parametrize("mutation", ["block_ref", "edge", "entry", "new_block", "unselected_block", "duplicate"])
def test_dependency_replacement_cannot_change_topology_or_unlisted_records(mutation):
    candidate = _two_loops()
    strategy = fragment_correction_strategy("cfg")
    strategy.build_prompt("FULL SOURCE", candidate, diagnostics_for(candidate))
    replacement = _four_replacements(candidate)
    if mutation == "block_ref":
        replacement["replacements"][0]["value"]["block_ref"] = "new_head"
    elif mutation == "edge":
        replacement["replacements"].append({"record_id": "/edges/0", "value": candidate["edges"][0]})
    elif mutation == "entry":
        replacement["replacements"].append({"record_id": "/entry_block_ref", "value": "first_head"})
    elif mutation == "new_block":
        replacement["replacements"].append({"record_id": "/blocks/10", "value": candidate["blocks"][0]})
    elif mutation == "unselected_block":
        replacement["replacements"].append({"record_id": "/blocks/9", "value": candidate["blocks"][9]})
    else:
        replacement["replacements"].append(deepcopy(replacement["replacements"][0]))
    with pytest.raises(StructuralValidationError) as error:
        strategy.merge(candidate, replacement)
    assert error.value.diagnostics[0]["code"] in {"record_identity", "cfg_correction_topology"}


def test_head_only_edit_does_not_make_unproduced_carry_valid():
    candidate = _two_loops()
    strategy = fragment_correction_strategy("cfg")
    strategy.build_prompt("FULL SOURCE", candidate, diagnostics_for(candidate))
    correction = _four_replacements(candidate)
    correction["replacements"] = correction["replacements"][::2]
    merged = strategy.merge(candidate, correction)
    result = compile_candidate(merged)
    assert not result.ok and result.cfg is None
    assert sum(row.code == "RESULT_NOT_DEFINED" for row in result.diagnostics) >= 2


def test_actual_missing_endpoint_keeps_full_candidate_correction():
    candidate = loop_candidate()
    candidate["edges"][2]["target_block_ref"] = "missing"
    strategy = fragment_correction_strategy("cfg")
    prompt = strategy.build_prompt("FULL SOURCE", candidate, diagnostics_for(candidate))
    assert strategy.cfg_scope["mode"] == "whole" and strategy.selected == {}
    assert '"candidate":' in prompt and '"missing"' in prompt
    assert "MECHANICAL OUTPUT CORRECTION" in prompt
