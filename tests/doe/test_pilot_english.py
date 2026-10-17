from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import shutil

import pytest

from tools.doe.pilot_english import prepare_english_inputs, verify_english_inputs
from tools.doe.run_joint_pipeline_pilot import verify_baseline


@pytest.fixture(scope="module")
def pinned():
    return verify_baseline()


def test_three_case_projection_is_english_and_preserves_history(tmp_path, pinned):
    records, hashes = pinned
    receipt = prepare_english_inputs(records, tmp_path)
    assert verify_english_inputs(records, tmp_path, receipt) == receipt
    for case in ("001", "010", "013"):
        translated = tmp_path / case
        audit = json.loads((translated / "projection.json").read_text(encoding="utf-8"))
        assert len(audit["cfg_changes"]) == (16 if case == "001" else 0)
        assert len(audit["source_changes"]) == (11 if case == "001" else 0)
        new_graph = json.loads((translated / "selected-analysis.json").read_text(encoding="utf-8"))
        original_graph = json.loads(Path(records[case]["analysis"]).read_text(encoding="utf-8"))
        assert not re.search(r"[\u3400-\u9fff]", json.dumps(new_graph, ensure_ascii=False))
        restored = deepcopy(new_graph)
        for change in audit["cfg_changes"]:
            obj = restored["cfg"]
            for part in change["path"][:-1]:
                obj = obj[part]
            assert obj[change["path"][-1]] == change["after"]
            obj[change["path"][-1]] = change["before"]
        assert restored == original_graph  # No added operations, edges, values, or scopes.
        for source in (translated / "package").rglob("*"):
            if not source.is_file():
                continue
            relative = source.relative_to(translated / "package")
            original = Path(records[case]["input"]) / relative
            actual = source.read_bytes()
            assert not re.search(r"[\u3400-\u9fff]", actual.decode("utf-8"))
            if case != "001":
                assert actual == original.read_bytes()
            else:
                old_lines = original.read_bytes().decode("utf-8").splitlines(keepends=True)
                new_lines = actual.decode("utf-8").splitlines(keepends=True)
                assert len(old_lines) == len(new_lines)
                assert [s[len(s.rstrip(chr(13) + chr(10))):] for s in old_lines] == [s[len(s.rstrip(chr(13) + chr(10))):] for s in new_lines]
    for name, expected in hashes.items():
        assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == expected


def test_preparation_recovers_missing_files_but_never_overwrites(tmp_path, pinned):
    records, _ = pinned
    receipt = prepare_english_inputs(records, tmp_path)
    missing = tmp_path / "010/projection.json"
    missing.unlink()
    with pytest.raises(ValueError, match="incomplete"):
        verify_english_inputs(records, tmp_path, receipt)
    assert prepare_english_inputs(records, tmp_path) == receipt
    target = tmp_path / "001/package/SKILL.md"
    target.write_text("unexpected edit", encoding="utf-8")
    with pytest.raises(ValueError, match="differs"):
        prepare_english_inputs(records, tmp_path)
    assert target.read_text() == "unexpected edit"


def test_extra_file_and_receipt_tampering_rejected(tmp_path, pinned):
    records, _ = pinned
    receipt = prepare_english_inputs(records, tmp_path)
    altered = deepcopy(receipt)
    altered["cases"]["001"]["analysis"] = "010/selected-analysis.json"
    with pytest.raises(ValueError, match="receipt"):
        verify_english_inputs(records, tmp_path, altered)
    (tmp_path / "unexpected.txt").write_text("extra")
    with pytest.raises(ValueError, match="differs"):
        verify_english_inputs(records, tmp_path, receipt)


@pytest.mark.parametrize("kind", ["source", "cfg"])
def test_unknown_source_or_graph_translation_is_not_guessed(tmp_path, pinned, kind):
    records = deepcopy(pinned[0])
    original = records["001"]
    package = tmp_path / "source"
    shutil.copytree(original["input"], package)
    analysis = tmp_path / "analysis.json"
    shutil.copyfile(original["analysis"], analysis)
    records["001"] = {**original, "input": str(package), "analysis": str(analysis)}
    if kind == "source":
        path = package / "SKILL.md"
        path.write_text(path.read_text(encoding="utf-8").replace("数值发送通知", "数值发送额外通知"), encoding="utf-8")
    else:
        value = json.loads(analysis.read_text(encoding="utf-8"))
        value["cfg"]["constraints"][0] += " A changed obligation."
        analysis.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(ValueError, match="differs"):
        prepare_english_inputs(records, tmp_path / "output")


def test_projection_refuses_overlap_with_historical_inputs(pinned):
    records = pinned[0]
    with pytest.raises(ValueError, match="overlap"):
        prepare_english_inputs(records, Path(records["001"]["input"]))
