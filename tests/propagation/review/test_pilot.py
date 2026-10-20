"""The one-off seven-case reconstruction is history, not a production runner."""
from skillflow.common.paths import project_root, resolve_material_path
from skillflow.common.recording import read_json, sha_file
import pytest


def test_fixed_reconstruction_scripts_are_retired():
    root = project_root() / "tools/propagation/review"
    assert not (root / "repair_candidates.py").exists()
    assert not (root / "run_repair_once.py").exists()
    from skillflow.propagation.review import refinement
    assert callable(refinement.run_refinement)
    assert callable(refinement.replay_refinement)


def test_preserved_historical_candidates_are_only_read_as_frozen_fixture():
    pointer = project_root() / "tmp/annotation-refinement-verification/run-path.txt"
    if not pointer.exists():
        pytest.skip("optional historical experiment fixture is not installed")
    frozen = resolve_material_path(pointer.read_text(encoding="utf-8").strip())
    path = frozen / "upstream/candidates-v1.json"
    before = sha_file(path)
    candidates = {c["case_id"]: c for c in read_json(path)}
    assert len(candidates) == 7
    assert sum(c["expectation"] is not None for c in candidates.values()) == 4
    segment = candidates["013-local"]["raw_annotation"]["transfer_specs"]["ir_003"]["events"][0]
    assert segment["mode"] == "local" and segment["returns"] == [{"kind": "local", "name": "fast_key"}]
    field = candidates["013-field"]["raw_annotation"]["transfer_specs"]["ir_009"]["events"][0]["events"][0]["atomic_ops"][1]
    assert field["op"] == "compute" and field["dependencies"] == ["possible"]
    source = candidates["010-source"]["raw_annotation"]["transfer_specs"]["ir_007"]["events"][0]["events"][0]["atomic_ops"][0]
    assert source["op"] == "compute" and "location" not in source
    scope = candidates["001-version"]["raw_annotation"]["transfer_specs"]["ir_005"]["events"][0]
    delivery = next(op for op in scope["body"][0]["events"][0]["atomic_ops"] if op["op"] == "deliver")
    assert delivery["inputs"] == [{"kind": "local", "name": "recipient_value"}, {"kind": "local", "name": "record"}]
    assert before == sha_file(path)
