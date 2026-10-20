"""Paired review subsets use durable calls without weakening historical guards."""
from copy import deepcopy
import json
from pathlib import Path
import shutil

import pytest

from skillflow.common.recording import ResponseIntegrityError, sha_file
from tools.doe.endpoint_validation import (
    IDENTITY, LEGACY_IDENTITY, load_validation, prepare_validation,
    replay_validation, run_validation,
)
from tools.doe.prompt_screen import _seal


CASES = ("review_custody_release", "review_voucher_delivery")
CONFIG = {"endpoint": "https://example.invalid/v1/chat/completions",
    "model": "endpoint-subset-test", "reasoning_effort": "max",
    "timeout_ms": 1000, "max_retries": 0, "retry_base_ms": 1,
    "retry_max_backoff_ms": 1, "response_format": "json_object"}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def manifest_body(directory):
    value = read(directory / "manifest.json")
    value.pop("manifest_sha256")
    return value


@pytest.fixture(scope="module")
def materials(tmp_path_factory):
    root = tmp_path_factory.mktemp("endpoint-subset")
    sources = Path(__file__).resolve().parents[2] / "src"
    baseline = root / "baseline"
    receipt = {}
    for source in sorted((sources / "skillflow").rglob("*.py")):
        target = baseline / "src" / source.relative_to(sources)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
        receipt[target.relative_to(baseline).as_posix()] = sha_file(target)
    (baseline / "files.json").write_text(json.dumps(receipt), encoding="utf-8")
    prepare_validation(root / "subset", baseline_dir=baseline, config=CONFIG,
                       case_names=list(CASES))
    prepare_validation(root / "full", baseline_dir=baseline, config=CONFIG)
    return root


@pytest.fixture
def subset(tmp_path, materials):
    return Path(shutil.copytree(materials / "subset", tmp_path / "subset"))


class Client:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.prompts = []

    def complete(self, prompt):
        index = len(self.prompts)
        self.prompts.append(prompt)
        assert index < len(self.responses), "Unexpected additional request"
        return deepcopy(self.responses[index])


def clients(directory):
    return {(case, arm): Client(read(directory / f"audit/fixtures/{case}.json")["reference_response"])
            for case in CASES for arm in ("baseline", "latest")}


def test_review_subset_has_four_counterbalanced_first_responses_and_zero_api_replay(subset):
    manifest = load_validation(subset)
    assert manifest["identity"] == IDENTITY
    assert [case["name"] for case in manifest["cases"]] == list(CASES)
    assert manifest["schedule"] == [
        {"case": CASES[0], "stage": "review", "arm": "baseline"},
        {"case": CASES[0], "stage": "review", "arm": "latest"},
        {"case": CASES[1], "stage": "review", "arm": "latest"},
        {"case": CASES[1], "stage": "review", "arm": "baseline"}]
    assert read(subset / "audit/preregistration.json")["initial_chains"] == 4
    assert {path.stem for path in (subset / "audit/fixtures").glob("*.json")} == set(CASES)
    live = clients(subset)
    result = run_validation(subset, clients=live)
    assert result["status"] == "complete" and len(result["results"]) == 4
    assert all(row["first_response_valid"] is True
               and row["metrics"]["structural_corrections"] == 0
               for row in result["results"])
    assert all(len(client.prompts) == 1 for client in live.values())
    assert {arm: row["initial_chains"] for arm, row in read(subset / "metrics.json")["arms"].items()} == {"baseline": 2, "latest": 2}
    assert "4 initial chains are scheduled" in (subset / "report.md").read_text(encoding="utf-8")
    assert replay_validation(subset)["api_calls"] == 0
    run_validation(subset, clients=live)
    assert all(len(client.prompts) == 1 for client in live.values())


def test_subset_correction_preserves_initial_failure_and_replays(subset):
    live = clients(subset)
    key = (CASES[1], "latest")
    valid = live[key].responses[0]
    invalid = {**deepcopy(valid), "unrecognized_field": "Do not silently discard this field."}
    live[key] = Client(invalid, valid)
    result = run_validation(subset, clients=live)
    row = next(row for row in result["results"] if (row["case"], row["arm"]) == key)
    assert row["first_response_valid"] is False
    assert row["metrics"]["structural_corrections"] == 1
    assert row["metrics"]["logical_calls"] == 2
    assert row["accepted_call"].endswith("/a002")
    assert read(subset / f"cases/{key[0]}/{key[1]}/calls/review/a001/call.json")["response"] == invalid
    assert replay_validation(subset)["api_calls"] == 0
    assert len(live[key].prompts) == 2


@pytest.mark.parametrize("selection", [[], [CASES[0], CASES[0]], ["not_a_case"], "review_custody_release", [None]])
def test_bad_case_selections_are_rejected(tmp_path, materials, selection):
    with pytest.raises(ValueError, match="distinct supported case names"):
        prepare_validation(tmp_path / "bad", baseline_dir=materials / "baseline",
                           config=CONFIG, case_names=selection)


@pytest.mark.parametrize("mutation", ["duplicate", "stage", "reorder", "missing"])
def test_changed_subset_schedule_is_rejected_even_if_resealed(subset, mutation):
    manifest = manifest_body(subset)
    if mutation == "duplicate":
        manifest["schedule"][1] = deepcopy(manifest["schedule"][0])
    elif mutation == "stage":
        manifest["schedule"][0]["stage"] = "annotation"
    elif mutation == "reorder":
        manifest["schedule"].reverse()
    else:
        manifest["schedule"].pop()
    (subset / "manifest.json").write_text(json.dumps(_seal(manifest)), encoding="utf-8")
    with pytest.raises(ResponseIntegrityError, match="schedule changed"):
        load_validation(subset)


def test_legacy_identity_cannot_reinterpret_a_subset(subset):
    manifest = manifest_body(subset)
    manifest["identity"] = LEGACY_IDENTITY
    (subset / "manifest.json").write_text(json.dumps(_seal(manifest)), encoding="utf-8")
    with pytest.raises(ResponseIntegrityError, match="original four cases"):
        load_validation(subset)


def test_legacy_full_read_only_loading_keeps_content_and_implementation_guards(tmp_path, materials):
    directory = Path(shutil.copytree(materials / "full", tmp_path / "legacy"))
    manifest = manifest_body(directory)
    manifest["identity"] = LEGACY_IDENTITY
    manifest["implementation"] = {"production": {"historical": "different producer"}, "tools": {}}
    (directory / "manifest.json").write_text(json.dumps(_seal(manifest)), encoding="utf-8")
    assert load_validation(directory)["identity"] == LEGACY_IDENTITY
    with pytest.raises(ResponseIntegrityError, match="implementation changed"):
        load_validation(directory, check_implementation=True)
    path = directory / next(iter(manifest["files"]))
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(ResponseIntegrityError, match="Frozen validation material changed"):
        load_validation(directory)
