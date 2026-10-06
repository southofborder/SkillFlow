"""Protected provenance, deliberate graph mutations and evaluation isolation."""

from skillflow.common.paths import project_root, resolve_material_path

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil

import pytest

from skillflow.graph.audit import fixtures
from skillflow.graph.audit.evidence import canonical_graph_sha256
from skillflow.graph.audit.evidence import normalize_cfg
from skillflow.graph.ir.cfg import ControlFlowGraph


def isolated_repository(tmp_path):
    root = project_root()
    manifest = json.loads((root / fixtures.MANIFEST_PATH).read_bytes())
    relative_paths = [
        fixtures.MANIFEST_PATH,
        Path(manifest["selection"]["manifest_path"]),
        Path(manifest["analysis"]["path"]),
        *[Path(manifest["source"]["root"]) / row["path"] for row in manifest["source"]["files"]],
    ]
    for relative in relative_paths:
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(resolve_material_path(relative, base=root), destination)
    return manifest


def test_canonical_hash_contract_is_shared_and_rejects_nan():
    value = {"z": [1, "中文"], "a": None}
    exact = '{"a":null,"z":[1,"中文"]}'
    assert fixtures.canonical_json(value) == exact
    assert fixtures.canonical_sha256(value) == hashlib.sha256(exact.encode("utf-8")).hexdigest()
    assert fixtures.canonical_sha256(value) == fixtures.canonical_sha256({"a": None, "z": [1, "中文"]})
    assert fixtures.canonical_sha256([1, 2]) != fixtures.canonical_sha256([2, 1])
    with pytest.raises(ValueError):
        fixtures.canonical_sha256(float("nan"))


def test_five_graphs_validate_without_changing_protected_inputs_or_cfgs(tmp_path, monkeypatch):
    manifest = json.loads((project_root() / fixtures.MANIFEST_PATH).read_bytes())
    protected = [
        resolve_material_path(manifest["analysis"]["path"]),
        *[resolve_material_path(manifest["source"]["root"]) / row["path"] for row in manifest["source"]["files"]],
    ]
    before = {path: path.read_bytes() for path in protected}
    monkeypatch.chdir(tmp_path)
    result = fixtures.prepare_cases()
    assert [case["case_id"] for case in result["cases"]] == ["c01", "c02", "c03", "c04", "c05"]
    original = json.loads(before[protected[0]])["cfg"]
    assert result["cases"][0]["cfg"] == original
    for case in result["cases"]:
        untouched = deepcopy(case["cfg"])
        graph = ControlFlowGraph.model_validate(case["cfg"])
        assert graph.validate_integrity()
        assert canonical_graph_sha256(normalize_cfg(graph)) == case["graph_sha256"]
        assert case["cfg"] == untouched
    assert before == {path: path.read_bytes() for path in protected}
    assert len({case["graph_sha256"] for case in result["cases"]}) == 5


@pytest.mark.parametrize("target", ["source", "analysis", "review_selection"])
def test_bound_input_tampering_is_rejected(tmp_path, target):
    manifest = isolated_repository(tmp_path)
    relative = {
        "source": Path(manifest["source"]["root"]) / manifest["source"]["files"][0]["path"],
        "analysis": Path(manifest["analysis"]["path"]),
        "review_selection": Path(manifest["selection"]["manifest_path"]),
    }[target]
    path = tmp_path / relative
    path.write_bytes(path.read_bytes() + b"\nchanged")
    with pytest.raises(fixtures.FixtureIntegrityError, match="SHA-256 mismatch"):
        fixtures.prepare_cases(repository_root=tmp_path)


def test_source_inventory_change_is_rejected(tmp_path):
    manifest = isolated_repository(tmp_path)
    (tmp_path / manifest["source"]["root"] / "extra.md").write_text("unexpected", encoding="utf-8")
    with pytest.raises(fixtures.FixtureIntegrityError, match="inventory"):
        fixtures.prepare_cases(repository_root=tmp_path)


def test_oracle_is_not_read_and_cases_are_independent(monkeypatch):
    read_bytes = Path.read_bytes

    def forbid_oracle(path):
        assert path.name != "oracle.json", "Fixture preparation must not load evaluation answers"
        return read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", forbid_oracle)
    result = fixtures.prepare_cases()
    assert result["provenance"]["oracle_loaded"] is False
    for case in result["cases"]:
        assert "oracle_key" not in fixtures.canonical_json(case["cfg"])
        assert "oracle_finding_id" not in fixtures.canonical_json(case["cfg"])
        assert "case_id" not in fixtures.canonical_json(case["cfg"])
    baseline = deepcopy(result["cases"][0]["cfg"])
    result["cases"][1]["cfg"]["constraints"].append("changed by caller")
    assert result["cases"][0]["cfg"] == baseline
    assert fixtures.prepare_cases()["cases"][1]["graph_sha256"] != fixtures.canonical_sha256(result["cases"][1]["cfg"])


def test_variants_preserve_the_intended_semantic_traps():
    cases = {case["case_id"]: case["cfg"] for case in fixtures.prepare_cases()["cases"]}
    baseline = cases["c01"]
    base = fixtures._anchors(baseline)
    archive_inputs = fixtures._anchors(cases["c02"])["archive"][2]["inputs"]
    assert archive_inputs[-1] == base["key_result"]
    failure_block = base["archive_failure_return"][0]
    assert [i["opcode"] for i in cases["c03"]["blocks"][failure_block]["instructions"]] == ["return"]
    assert cases["c03"]["blocks"][failure_block]["block_name"] == baseline["blocks"][failure_block]["block_name"]
    assert cases["c03"]["constraints"] == baseline["constraints"]
    retry_return_block = base["retry_success_return"][0]
    wrong_return = cases["c04"]["blocks"][retry_return_block]["instructions"][-1]
    assert wrong_return["inputs"] == [fixtures._result_output(base["first"][2], "response_body")]
    check_block, position, _ = base["failure_check"]
    sequence = cases["c05"]["blocks"][check_block]["instructions"]
    inserted = sequence[position + 1]
    assert inserted["opcode"] == "wait_for_seconds"
    assert inserted["inputs"][0]["literal_value"] == 2
    assert inserted["constraints"] == ["Wait for 2 seconds before continuing."]
    assert sequence[-1]["opcode"] == "dispatch"


def test_oracle_hashes_and_graph_references_match_actual_cases():
    root = project_root()
    oracle = json.loads(resolve_material_path("packages/skill-ir/experiments/semantic_backtrace/f01/oracle.json").read_bytes())
    prepared = fixtures.prepare_cases()
    assert oracle["source_sha256"] == prepared["source"]["source_sha256"]
    assert len(oracle["source_requirements"]) == 4
    for case in prepared["cases"]:
        expected = oracle["cases"][case["oracle_key"]]
        assert expected["graph_sha256"] == case["graph_sha256"]
        for finding in expected["expected_findings"]:
            for pointer in finding["graph_refs"]:
                value = case["cfg"]
                for raw in pointer.split("/")[1:]:
                    part = raw.replace("~1", "/").replace("~0", "~")
                    value = value[int(part)] if isinstance(value, list) else value[part]
        for check in expected["graph_to_text_checks"].values():
            assert check["actual_text_status"] == "not_yet_generated"
            assert check["preassigned_findings"] is False


def test_new_instruction_identifier_is_chosen_without_collision():
    cfg = fixtures.prepare_cases()["cases"][0]["cfg"]
    first = next(iter(cfg["blocks"].values()))["instructions"][0]
    first["id"] = "ir_wait_1"
    fixtures._mutate(cfg, "c05")
    identifiers = [instruction["id"] for _, _, instruction in fixtures._instructions(cfg)]
    assert "ir_wait_2" in identifiers
    assert len(identifiers) == len(set(identifiers))
    assert ControlFlowGraph.model_validate(cfg).validate_integrity()
