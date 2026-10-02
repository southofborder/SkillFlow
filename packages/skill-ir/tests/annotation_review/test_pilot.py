"""Historical reconstruction is preserved and rejected by the current contract."""
import importlib.util
from pathlib import Path

import pytest

from skill_ir.recording import read_json, sha_file


@pytest.fixture
def pilot():
    path = Path(__file__).resolve().parents[2] / "experiments/annotation_review/tools/run_repair_once.py"
    spec = importlib.util.spec_from_file_location("repair_once_pilot_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def frozen(pilot):
    pointer = pilot.ROOT / "tmp/annotation-refinement-verification/run-path.txt"
    if not pointer.exists():
        pytest.skip("explicit pre-change local verification is not present")
    return Path(pointer.read_text(encoding="utf-8"))


def test_seven_historical_candidates_are_not_silently_promoted_to_current_boundaries(pilot, frozen):
    receipt = pilot.verify_prechange(frozen)
    before = {name: sha_file(frozen / name) for name in receipt["files"]}
    candidates = read_json(frozen / "upstream/candidates-v1.json")
    assert [item["case_id"] for item in candidates] == list(pilot.CASE_IDS)
    assert sum(item["expectation"] is not None for item in candidates) == 4
    # The old helper may remove its originally authorized empty field and fix
    # order, but it cannot invent the new receiving-scope/retention judgments.
    # A preserved pre-change receipt is not current producer authorization.
    with pytest.raises(ValueError, match="access_scope|retention"):
        pilot.reconstruct(frozen)
    assert before == {name: sha_file(frozen / name) for name in receipt["files"]}


def test_all_four_preserved_historical_defects_keep_their_original_relations(pilot, frozen):
    receipt = pilot.verify_prechange(frozen)
    before = {name: sha_file(frozen / name) for name in receipt["files"]}
    candidates = {c["case_id"]: c for c in read_json(frozen / "upstream/candidates-v1.json")}
    segment = candidates["013-local"]["raw_annotation"]["transfer_specs"]["ir_003"]["events"][0]
    assert segment["mode"] == "local" and segment["returns"] == [{"kind": "local", "name": "fast_key"}]
    field = candidates["013-field"]["raw_annotation"]["transfer_specs"]["ir_009"]["events"][0]["events"][0]["atomic_ops"][1]
    assert field["op"] == "compute" and field["dependencies"] == ["possible"]
    source = candidates["010-source"]["raw_annotation"]["transfer_specs"]["ir_007"]["events"][0]["events"][0]["atomic_ops"][0]
    assert source["op"] == "compute" and "location" not in source
    scope = candidates["001-version"]["raw_annotation"]["transfer_specs"]["ir_005"]["events"][0]
    delivery = next(op for op in scope["body"][0]["events"][0]["atomic_ops"] if op["op"] == "deliver")
    assert delivery["inputs"] == [{"kind": "local", "name": "recipient_value"}, {"kind": "local", "name": "record"}]
    assert before == {name: sha_file(frozen / name) for name in receipt["files"]}


def test_policy_and_output_paths(pilot, tmp_path):
    assert pilot.public_config()["response_format"] == "json_object"
    assert pilot.POLICY["max_logical_calls"] == 24
    assert pilot.POLICY["annotation_repairs_per_case"] == 1
    assert pilot.POLICY["cfg_extractions"] == pilot.POLICY["cfg_repairs"] == 0
    with pytest.raises(ValueError):
        pilot.checked_run(tmp_path / "repair-once-v1-test")
    with pytest.raises(ValueError):
        pilot.checked_run(pilot.ROOT / "result" / "repair-once-v1-test")


def test_driver_continues_error_stops_interrupt_without_cfg(pilot, tmp_path, monkeypatch):
    run = tmp_path / "run"
    monkeypatch.setattr(pilot, "checked_run", lambda path: path)
    monkeypatch.setattr(pilot, "manifest", lambda _: {"config": pilot.public_config()})
    monkeypatch.setattr(pilot, "summarize", lambda _: {})
    monkeypatch.setattr(pilot, "refine_skill", lambda *a, **k: pytest.fail("no CFG call after interruption"))
    calls = []
    def refine(path, **kwargs):
        calls.append(path.parent.name)
        if len(calls) == 1:
            raise ValueError("local error")
        return {"status": "interrupted", "selected": "original"}
    monkeypatch.setattr(pilot, "run_refinement", refine)
    pilot.run(run)
    assert calls == ["001-base", "010-base"]
    assert read_json(run / "cases/001-base/pilot-status.json")["status"] == "driver_error"


def test_replay_never_constructs_online_factories(pilot, tmp_path, monkeypatch):
    run = tmp_path / "run"
    monkeypatch.setattr(pilot, "checked_run", lambda path: path)
    monkeypatch.setattr(pilot, "manifest", lambda _: {"config": pilot.public_config()})
    monkeypatch.setattr(pilot, "summarize", lambda _: {})
    monkeypatch.setattr(pilot, "streaming_factory", lambda *a, **k: pytest.fail("online factory"))
    monkeypatch.setattr(pilot, "run_refinement", lambda *a, **k: pytest.fail("online refine"))
    calls, cfg = [], []
    monkeypatch.setattr(pilot, "replay_refinement", lambda path: calls.append(path.parent.name) or {"status": "review_passed", "selected": "original"})
    monkeypatch.setattr(pilot, "replay_cfg", lambda path: cfg.append(path.name) or {})
    pilot.run(run, replay=True)
    assert calls == list(pilot.CASE_IDS)
    assert cfg == ["001", "010", "013"]


def test_summary_does_not_promote_or_abort_uncommitted_propagation(pilot, tmp_path, monkeypatch):
    import json
    case = tmp_path / "cases/001-base/propagation"
    case.mkdir(parents=True)
    (case / "doe-input.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(pilot, "load_propagation_run", lambda *a: pytest.fail("uncommitted material must not load"))
    summary = pilot.summarize(tmp_path)
    assert summary["cases"][0]["propagation"] == "uncommitted"
    assert summary["cases"][0]["initial_issues"] is None
    assert len(summary["cases"]) == 7


def test_selected_propagation_rejects_different_candidate(pilot, tmp_path, monkeypatch):
    import json
    case = tmp_path / "cases/001-base"
    for path, content in (("propagation/manifest.json", {}), ("propagation/audit/raw-annotation.json", {"other": True}),
                          ("refinement/inputs/candidate.json", {})):
        target = case / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(content), encoding="utf-8")
    monkeypatch.setattr(pilot, "load_propagation_run", lambda *a: {})
    monkeypatch.setattr(pilot, "replay_propagation", lambda *a: pytest.fail("must reject before replay"))
    with pytest.raises(ValueError, match="selected current candidate"):
        pilot._selected_propagation(tmp_path, "001-base", {"selected": "original"})
