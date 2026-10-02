"""Report-mode boundaries with synthetic bookkeeping, never model output."""
from copy import deepcopy
import importlib.util
from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parents[2] / "experiments/semantics_baseline"
SPEC = importlib.util.spec_from_file_location("semantics_result_reporting_test", BASE / "tools/result_integrity.py")
integrity = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(integrity)


def materials():
    catalog = integrity.read(BASE / "frozen/corpus/corpus.json")
    result = []
    for sample in catalog["samples"]:
        annotation = integrity.read(BASE / "frozen/corpus" / sample["annotation_path"])
        result.append({
            "sample": sample, "annotation": annotation,
            "trials": [{"repetition": repetition, "record": {"status": "complete"},
                        "analysis": {"status": "complete", "cfg": {"blocks": {"synthetic": {}}}}}
                       for repetition in (1, 2, 3)],
            "review": {"facts": [{"assessments": [{"synthetic_fixture": True}] * 3}
                                  for fact in annotation["facts"]]},
        })
    return result


def interim_materials():
    result = materials()
    for index, item in enumerate(result):
        if index == 1:
            item["trials"][2]["record"]["status"] = "not_run"
            item["trials"][2]["analysis"] = None
            item["review"] = None
        elif index > 1:
            item["review"] = None
            for trial in item["trials"]:
                trial["record"]["status"] = "not_run"
                trial["analysis"] = None
    return result


def test_full_report_requires_all_90_terminal_trials_and_891_assessments():
    source = materials()
    scope = integrity.result_report_scope(source, "final")
    assert len(scope["detail_trials"]) == 90 and scope["fact_assessments"] == 891
    source[0]["trials"][0]["record"]["status"] = "not_run"
    with pytest.raises(ValueError, match="all 90 terminal"):
        integrity.result_report_scope(source, "final")


def test_full_report_rejects_missing_plan_trial_or_fact_assessment():
    source = materials()
    source[0]["trials"].pop()
    with pytest.raises(ValueError, match="90-trial plan"):
        integrity.result_report_scope(source, "final")
    source = materials()
    source[0]["review"]["facts"][0]["assessments"].pop()
    with pytest.raises(ValueError, match="all 891"):
        integrity.result_report_scope(source, "final")


def test_interim_does_not_expand_unrun_trials_or_prefill_their_assessments():
    source = interim_materials()
    before = deepcopy(source)
    scope = integrity.result_report_scope(source, "interim")
    assert scope["sample_ids"] == ["N01", "N02"]
    assert scope["detail_trials"] == [("N01", 1), ("N01", 2), ("N01", 3), ("N02", 1), ("N02", 2)]
    assert scope["reviewed_sample_ids"] == ["N01"]
    assert scope["fact_assessments"] == 27 and source == before


def test_interim_requires_review_for_every_three_terminal_sample():
    source = interim_materials()
    source[0]["review"] = None
    with pytest.raises(ValueError, match="Three-terminal sample requires"):
        integrity.result_report_scope(source, "interim")


def test_interim_rejects_prefilled_review_for_incomplete_sample():
    source = interim_materials()
    source[1]["review"] = deepcopy(source[0]["review"])
    with pytest.raises(ValueError, match="Do not prefill"):
        integrity.result_report_scope(source, "interim")


@pytest.mark.parametrize("status", ["running", "interrupted", "pending"])
def test_interim_rejects_uncommitted_trials(status):
    source = interim_materials()
    source[1]["trials"][1]["record"]["status"] = status
    with pytest.raises(ValueError, match="stopped, committed"):
        integrity.result_report_scope(source, "interim")


@pytest.mark.parametrize("status", ["error", "degraded", "uncertain", "not_run"])
def test_unaccepted_cfg_is_never_counted_as_structural_acceptance(status):
    trial = materials()[0]["trials"][0]
    trial["record"]["status"] = status
    assert integrity.accepted_cfg_count([trial]) == 0
    assert "verdict" not in trial


def test_complete_status_alone_does_not_substitute_for_actual_cfg():
    trial = materials()[0]["trials"][0]
    trial["analysis"] = None
    assert integrity.accepted_cfg_count([trial]) == 0
