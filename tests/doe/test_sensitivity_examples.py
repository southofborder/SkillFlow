"""Pinned authoring recipes never become production sensitivity heuristics."""
import json

import pytest

from skillflow.common.paths import project_root
from tests.doe.fixtures.sensitivity_examples import VERIFIED_BASELINE, authored_sensitivity_candidate
from tests.doe.fixtures.rebuild_field_fixtures import canonical_demand

def check_preserved_demand(before, after):
    if canonical_demand(before) != canonical_demand(after):
        raise ValueError("changed existing demand relations")
from tests.doe.fixtures.rebuild_field_fixtures import rebuild_raw_annotation
from skillflow.doe.sensitivity_results import resolve_data_review


def bundle(case):
    path = project_root() / VERIFIED_BASELINE / f"{case}.json"
    if not path.is_file():
        pytest.skip("Pre-upgrade experiment receipt is not part of the source distribution")
    value = json.loads(path.read_bytes())
    value["annotation"]["raw_annotation"] = rebuild_raw_annotation(
        value["annotation"]["raw_annotation"], value["annotation"]["material"], task=value["task"])
    return value


@pytest.mark.parametrize("case,ir,local,path", [
    ("001", "ir_001", "events_content", [{"kind": "each"}, "access_token"]),
    ("013", "ir_003", "environment_content", ["FAST_KEY"]),
])
def test_explicit_original_source_range_and_evidence(case, ir, local, path):
    values = bundle(case)
    candidate = authored_sensitivity_candidate(case, values["input"]["cfg"],
        values["annotation"]["raw_annotation"], values["annotation"]["task_source_files"])
    assert len(candidate["scopes"]) == 1
    scope = candidate["scopes"][0]
    assert scope["instruction_id"] == ir and scope["scope_path"] == []
    declaration = scope["declarations"][0]
    assert declaration["value"] == {"kind": "local", "name": local}
    assert declaration["path"] == path and declaration["property"] == "value"
    assert declaration["label"] == "authentication credential"
    assert all("quote" not in evidence for evidence in declaration["evidences"])


def test_010_does_not_invent_sensitive_unknown_fields():
    values = bundle("010")
    candidate = authored_sensitivity_candidate("010", values["input"]["cfg"],
        values["annotation"]["raw_annotation"], values["annotation"]["task_source_files"])
    assert candidate["scopes"] == []


def test_example_rejects_changed_source_operation():
    values = bundle("001")
    raw = values["annotation"]["raw_annotation"]
    raw["ir_semantics"]["ir_001"]["events"][0]["events"][0]["atomic_ops"][0]["output"] = "different"
    with pytest.raises(ValueError, match="Pinned sensitivity source"):
        authored_sensitivity_candidate("001", values["input"]["cfg"], raw, values["annotation"]["task_source_files"])


def test_demand_comparison_allows_only_goal_listing_order():
    from copy import deepcopy
    original = bundle("001")["demand_result"]
    reordered = deepcopy(original)
    reordered["goals"].reverse()
    check_preserved_demand(original, reordered)
    reordered["sinks"][0]["actual_payload"][0]["inputs"].append(["different"])
    with pytest.raises(ValueError, match="changed existing"):
        check_preserved_demand(original, reordered)


def test_013_received_response_refinement_preserves_possible_credential_influence(tmp_path):
    from copy import deepcopy
    from skillflow.common.recording import sha_file
    from skillflow.doe.sensitivity_material import prepare_sensitivity_review
    from tests.doe.helpers import fact_fixture
    from tests.doe.fixtures.task_examples import authored_candidate, BASELINE
    from tests.doe.fixtures.demand_examples import authored_demand_candidate
    from skillflow.doe.task_material import prepare_task_review
    from skillflow.propagation.contracts.joint import joint_source_files
    receipt = project_root() / BASELINE / "013/propagation/doe-input.json"
    before = sha_file(receipt)
    facts = fact_fixture(receipt)
    original = deepcopy(facts)
    annotation = facts.annotation
    task = prepare_task_review(facts, authored_candidate("013", facts.cfg)).task
    requested = authored_demand_candidate("013",facts.cfg,annotation["raw_annotation"],task.model_dump(mode="json"))
    candidate = authored_sensitivity_candidate("013",facts.cfg,annotation["raw_annotation"],joint_source_files(annotation["material"]))
    result = prepare_sensitivity_review(facts,task,annotation,requested,candidate).to_dict()
    credential_ids = {data["id"] for data in facts.data if data["origin"]["path"] == ["FAST_KEY"]}
    responses = {data["id"] for data in facts.data
        if data["content"]["form"] == "known_parts" and not data["content"]["parts_complete"]
        and data["origin"]["acquired_from"] and any(
            dependency["data"] in credential_ids and dependency["relation"] == "possible"
            for dependency in data["origin"]["dependencies"])}
    assert len(responses) == 2  # Distinct initial and retry response identities.
    observed = [row for sink in result["sinks"] if sink["boundary"]["sink_type"] == "model_observe"
                for saved in sink["data_reviews"]
                for row in [resolve_data_review(saved, sink, result["derivations"]["sensitivity"])] if row["data_id"] in responses]
    assert {row["data_id"] for row in observed} == responses
    assert all(row["relation"] == "possible" and row["conclusion"] != "excess_supported" for row in observed)
    assert facts == original and sha_file(receipt) == before
