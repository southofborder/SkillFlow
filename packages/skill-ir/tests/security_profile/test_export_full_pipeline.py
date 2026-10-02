"""Offline provenance checks for the new staged delivery; never call a model."""
from copy import deepcopy
import hashlib
import importlib.util
from pathlib import Path
import struct
import zlib
import zipfile

import pytest

from skill_ir.experiments.report import ArtifactWriter
from skill_ir.inputs.snapshot import freeze_input, read_snapshot
from skill_ir.recording import canonical_sha256, sha_file
from skill_ir.security_profile.runner import prepare_run, run_annotation, compilation_certificate
from skill_ir.security_profile.evidence import prepare_material
from skill_ir.security_profile.services import to_payload, compile_response
from skill_ir.semantic_contract import contract_binding
from security_profile.helpers import graph, FakeClient

SCRIPT = Path(__file__).resolve().parents[2] / "experiments/security_profile/tools/export_full_pipeline.py"


@pytest.fixture(scope="module")
def exporter():
    spec = importlib.util.spec_from_file_location("test_new_pipeline_exporter", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def case(tmp_path, exporter):
    package = tmp_path / "package"
    package.mkdir()
    (package / "SKILL.md").write_bytes("---\nname: local-config\n---\n读取配置并本地选择字段后返回。\n".encode())
    (package / "data.bin").write_bytes(b"\xff\x00original")
    inventory = {p.name: {"bytes": p.stat().st_size, "sha256": sha_file(p)} for p in package.iterdir()}
    directory = tmp_path / "run"
    root = directory / "cases/001"
    feedback_dir = root / "feedback"
    freeze_input(package, feedback_dir, ArtifactWriter(()))
    _, source, snapshot = read_snapshot(feedback_dir)
    cfg = graph()
    digest = canonical_sha256(cfg)
    row = {"revision": 0, "status": "audit_error", "graph_sha256": digest,
           "structural": {"status": "passed"}, "audit": None}
    feedback = {"status": "audit_error", "reason": "当前响应无效，不代表语义通过。", "last_valid_cfg": cfg,
                "source_sha256": source["source_sha256"], "rounds": [row]}
    selection = {"policy": "last_valid_cfg_from_current_feedback_only", "revision": 0,
                 "graph_sha256": digest, "source_sha256": source["source_sha256"],
                 "feedback_status": "audit_error", "auditor_passed": False, **contract_binding()}
    exporter.write_json(root / "selected-analysis.json", {"cfg": cfg})
    exporter.write_json(root / "selection.json", selection)
    prepare_run(feedback_dir / "inputs/package", root / "selected-analysis.json", run_dir=root / "annotation")
    material = prepare_material(source, cfg)
    annotation = run_annotation(root / "annotation", client=FakeClient())
    assert annotation["status"] == "complete"
    binding = {"status": "passed", "source_sha256": source["source_sha256"],
               "package_bytes_sha256": snapshot["package_bytes_sha256"], "file_count": len(snapshot["files"]),
               "checked_fields": ["path", "size", "raw_sha256", "decoded_sha256", "kind"]}
    item = {"case_id": "001", "sample_id": "N01", "basename": "001-local-config", "run_dir": "cases/001",
            "source_inventory": inventory, "source_inventory_sha256": canonical_sha256(inventory)}
    result = {"feedback": feedback, "selection": selection, "source_binding": binding, "annotation": annotation}
    skills = tmp_path / "skills"
    skills.mkdir()
    zip_path = skills / "001-local-config.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        for p in package.iterdir():
            archive.writestr(p.name, p.read_bytes())
    value = {"run_dir": directory, "root": root, "item": item, "result": result, "skills": skills,
             "zip": zip_path, "source": source, "material": material}
    commit(exporter, value)
    return value


def commit(exporter, case):
    root, result = case["root"], case["result"]
    exporter.write_json(root / "result.json", result)
    exporter.write_json(root / "feedback/result.json", result["feedback"])
    exporter.write_json(root / "annotation/result.json", result["annotation"])
    exporter.write_json(root / "source-binding.json", result["source_binding"])
    for row in result["feedback"].get("rounds", []):
        if row.get("graph_sha256") == canonical_sha256(result["feedback"]["last_valid_cfg"]):
            exporter.write_json(root / "feedback/rounds" / f"r{row['revision']:03}" / "cfg.json", result["feedback"]["last_valid_cfg"])


def load(exporter, case):
    return exporter.load_case(case["run_dir"], case["item"], case["result"], case["skills"])


def test_location_audit_is_bound_and_separate_from_business_payload(exporter, case):
    row = load(exporter, case)
    assert "location_evidences" not in row
    assert "location_evidences" not in case["result"]["annotation"]
    assert row["annotation_audit"]["sha256"] == case["result"]["annotation"]["location_evidences_sha256"]
    assert all(set(location) == {"kind", "name", "operand_refs", "access_scope", "retention"} for location in row["locations"].values())
    assert row["sink_boundaries"] == case["result"]["annotation"]["sink_boundaries"]


def test_export_rejects_modified_separate_location_audit(exporter, case):
    path = case["root"] / "annotation/audit/location-evidences.json"
    audit = exporter.read_json(path)
    next(iter(audit.values()))[0]["quote"] = "changed"
    exporter.write_json(path, audit)
    with pytest.raises(ValueError, match="payload or location evidence differs from the accepted response"):
        load(exporter, case)


def test_export_revalidates_audit_refs_after_digest_change(exporter, case):
    path = case["root"] / "annotation/audit/location-evidences.json"
    audit = exporter.read_json(path)
    next(iter(audit.values()))[0]["ref_id"] = "missing_reference"
    exporter.write_json(path, audit)
    case["result"]["annotation"]["location_evidences_sha256"] = canonical_sha256(audit)
    commit(exporter, case)
    with pytest.raises(ValueError):
        load(exporter, case)


@pytest.fixture
def display_lineage(exporter, tmp_path):
    directory = tmp_path / "child-display"
    cases = [{"case_id": f"{i:03}", "sample_id": sample, "basename": f"{i:03}-skill"}
             for i, sample in enumerate(exporter.SAMPLE_IDS, 1)]
    manifest = {"schema_version": 10, "profile_schema_version": "security-profile-v10", "identity": exporter.IDENTITY, **contract_binding(),
                "cases": cases, "renderer": {"path": "unused-renderer"}}
    exporter.write_json(directory / "manifest.json", manifest)
    value = {"schema_version": 4, "identity": "skill-ir-explicit-failed-case-rerun-v4",
             "child_run": {"path": str(directory), "run_id": directory.name},
             "parent_run": {"path": str(tmp_path / "parent-display"), "run_id": "parent-display",
                            "manifest_sha256": sha_file(directory / "manifest.json")},
             "rerun_cases": ["008", "009"] + [f"{i:03}" for i in range(18, 31)],
             "reused_cases": [f"{i:03}" for i in range(1, 18) if i not in (8, 9)]}
    seal_display_lineage(exporter, directory, value)
    return directory, cases, value


def seal_display_lineage(exporter, directory, value):
    value["provenance_sha256"] = canonical_sha256({k: v for k, v in value.items() if k != "provenance_sha256"})
    exporter.write_json(directory / "rerun-provenance.json", value)


def test_execution_origin_marks_fifteen_reused_without_reading_calls(exporter, display_lineage, monkeypatch):
    directory, cases, _ = display_lineage
    original = exporter.read_json
    def read(path):
        assert path.name == "rerun-provenance.json"  # Display binding never reads live case/call data.
        return original(path)
    monkeypatch.setattr(exporter, "read_json", read)
    origins = exporter.execution_origins(directory, cases)
    assert len(origins) == 30
    assert sum(item["kind"] == "reused" for item in origins.values()) == 15
    assert origins["001"]["source_run_id"] == "parent-display"
    assert origins["008"]["source_run_id"] == "child-display"
    assert origins["030"]["kind"] == "rerun"


@pytest.mark.parametrize("change", ["seal", "child_name", "child_path", "parent_name", "manifest", "overlap", "missing", "duplicate", "swapped"])
def test_execution_origin_rejects_bad_binding_or_partition(exporter, display_lineage, change):
    directory, cases, value = display_lineage
    if change == "seal":
        value["provenance_sha256"] = "0" * 64
    elif change == "child_name":
        value["child_run"]["run_id"] = "different"
    elif change == "child_path":
        value["child_run"]["path"] = str(directory / "different")
    elif change == "parent_name":
        value["parent_run"]["run_id"] = "different"
    elif change == "manifest":
        value["parent_run"]["manifest_sha256"] = "0" * 64
    elif change == "overlap":
        value["reused_cases"].append("008")
    elif change == "missing":
        value["reused_cases"].remove("001")
    elif change == "duplicate":
        value["rerun_cases"].append("008")
    else:
        value["rerun_cases"][0], value["reused_cases"][0] = "001", "008"
    if change == "seal":
        exporter.write_json(directory / "rerun-provenance.json", value)
    else:
        seal_display_lineage(exporter, directory, value)
    with pytest.raises(ValueError, match="Execution origin"):
        exporter.execution_origins(directory, cases)


def test_origin_is_display_only_and_plain_runs_remain_unchanged(exporter, case, display_lineage, monkeypatch):
    directory, cases, _ = display_lineage
    row = load(exporter, case)
    assert exporter.execution_origins(case["run_dir"], []) == {}
    assert "execution_origin" not in row and "执行来源：" not in exporter.suggestions(row)
    before = exporter.render_samples({"cases": [row]})
    origins = exporter.execution_origins(directory, cases)
    reused = {**row, "execution_origin": origins["001"]}
    rerun = {**row, "execution_origin": origins["008"]}
    assert "复用父运行记录（本次未重新调用模型）" in exporter.suggestions(reused)
    assert "本次重新执行" in exporter.suggestions(rerun)
    assert "parent-display" in exporter.suggestions(reused)
    assert exporter.render_samples({"cases": [reused]}) == before
    assert exporter.render_samples({"cases": [rerun]}) == before
    result = {"schema_version": 10, "profile_schema_version": "security-profile-v10", "identity": exporter.IDENTITY, **contract_binding(),
              "cases": {c["case_id"]: {} for c in cases}}
    exporter.write_json(directory / "experiment-result.json", result)
    monkeypatch.setattr(exporter._png, "check_inventory", lambda *_: None)
    monkeypatch.setattr(exporter, "load_case", lambda *_, **__: deepcopy(row))
    monkeypatch.setattr(exporter, "_assistant_review", lambda *_, **__: {})
    plan = exporter.build_export_plan(directory, case["skills"])
    assert [item["execution_origin"] for item in plan["cases"]] == [origins[c["case_id"]] for c in cases]


def test_valid_profile_bound_to_actual_latest_graph_and_source(exporter, case):
    row = load(exporter, case)
    assert row["kind"] == "cfg" and row["selected_revision"] == 0
    assert row["feedback_status"] == "audit_error" and row["annotation_status"] == "complete"
    assert row["audit"] is None  # Never borrow earlier/historical valid findings.
    assert row["profiles"] == case["result"]["annotation"]["profiles"]
    assert row["annotation_evidence_index"]["instruction_index"] == case["material"]["instruction_index"]
    assert "没有合法的完整语义核对记录" in exporter.suggestions(row)
    assert "不是助手或人工确认" in exporter.suggestions(row)


@pytest.mark.parametrize("change", ["manifest", "profile_version", "actor"])
def test_export_refuses_legacy_annotation_even_with_valid_digest(exporter, case, change):
    if change == "manifest":
        path = case["root"] / "annotation/manifest.json"
        manifest = exporter.read_json(path)
        manifest.update(identity="skill-ir-security-profile-v2", schema_version=2,
                        profile_schema_version="security-profile-v2")
        manifest["manifest_sha256"] = canonical_sha256({key: value for key, value in manifest.items()
                                                      if key != "manifest_sha256"})
        exporter.write_json(path, manifest)
    elif change == "profile_version":
        case["result"]["annotation"]["profile_schema_version"] = "security-profile-v2"
        commit(exporter, case)
    else:
        profile = case["result"]["annotation"]["profiles"]["ir_read"]
        profile["actor"] = profile.pop("operator")
        commit(exporter, case)
    with pytest.raises(ValueError):
        load(exporter, case)


@pytest.mark.parametrize("change", ["zip", "graph", "profile_digest", "profile_ir", "evidence", "source_binding"])
def test_corrupted_provenance_or_profile_is_rejected(exporter, case, change):
    result = case["result"]
    if change == "zip":
        with zipfile.ZipFile(case["zip"], "a") as archive:
            archive.writestr("facts.json", '{"expected":"do not leak annotations"}')
    elif change == "graph":
        result["feedback"]["last_valid_cfg"]["blocks"]["entry"]["instructions"][0]["opcode"] = "changed"
    elif change == "profile_digest":
        result["annotation"]["graph_sha256"] = "0" * 64
    elif change == "profile_ir":
        result["annotation"]["profiles"]["invented_ir"] = result["annotation"]["profiles"].pop("ir_read")
    elif change == "evidence":
        result["annotation"]["profiles"]["ir_read"]["evidences"][0]["quote"] = "not an actual quote"
    else:
        result["source_binding"]["package_bytes_sha256"] = "0" * 64
    commit(exporter, case)
    with pytest.raises(ValueError):
        load(exporter, case)


def test_last_valid_graph_survives_later_extraction_failure(exporter, case):
    result = case["result"]
    result["feedback"].update(status="extraction_error", reason="下一轮结构失败")
    result["feedback"]["rounds"].append({"revision": 1, "graph_sha256": None, "structural": None})
    result["selection"]["feedback_status"] = "extraction_error"
    exporter.write_json(case["root"] / "selection.json", result["selection"])
    commit(exporter, case)
    row = load(exporter, case)
    assert row["selected_revision"] == 0
    assert row["feedback_status"] == "extraction_error"


def test_duplicate_graph_selection_uses_latest_matching_round(exporter, case):
    result = case["result"]
    newer = {**result["feedback"]["rounds"][0], "revision": 1}
    result["feedback"]["rounds"].append(newer)
    commit(exporter, case)
    with pytest.raises(ValueError, match="Selection differs"):
        load(exporter, case)
    result["feedback"]["rounds"][0]["audit"] = {"marker": "previous audit must never be substituted"}
    result["selection"]["revision"] = 1
    exporter.write_json(case["root"] / "selection.json", result["selection"])
    commit(exporter, case)
    assert load(exporter, case)["audit"] is None


def test_legacy_unresolved_cannot_hide_in_current_compilation(exporter, case):
    directory = case["root"] / "annotation"
    raw = exporter.read_json(directory / "audit/raw-annotation.json")
    raw["unresolved"] = [{"instruction_id": "ir_read", "field": "effects", "reason": "未确定"}]
    with pytest.raises(ValueError):
        compile_response(raw, case["material"])


def test_failed_annotation_never_exports_profiles(exporter, case):
    case["result"]["annotation"]["status"] = "invalid_response"
    commit(exporter, case)
    with pytest.raises(ValueError, match="must not export"):
        load(exporter, case)
    case["result"]["annotation"]["profiles"] = {}
    case["result"]["annotation"]["locations"] = {}
    case["result"]["annotation"]["transfer_specs"] = {}
    commit(exporter, case)
    assert load(exporter, case)["profiles"] == {}


def test_no_cfg_has_failure_card_and_no_fake_graph(exporter, case, tmp_path):
    directory = tmp_path / "unstarted"
    root = directory / "cases/001"
    result = {"feedback": {"status": "not_run", "reason": "批次中断，未开始"}, "selection": None,
              "source_binding": None, "annotation": {"status": "not_run", "reason": "没有新图", "profiles": {}, "locations": {}, "transfer_specs": {}, "sink_boundaries": []}}
    exporter.write_json(root / "result.json", result)
    row = exporter.load_case(directory, case["item"], result, case["skills"])
    sample = exporter.render_samples({"cases": [row]})["samples"][0]
    assert row["cfg"] is None and row["graph_sha256"] is None and row["profiles"] == {}
    assert sample["cfg"] is None and sample["failure"]["reason"] == "批次中断，未开始"
    assert "没有借用旧图" in exporter.suggestions(row)


def test_numbering_and_complete_batch_required(exporter, case, monkeypatch):
    manifest = {"schema_version": 10, "profile_schema_version": "security-profile-v10", "identity": exporter.IDENTITY, **contract_binding(),
                "renderer": {"path": "unused"}, "cases": [case["item"]]}
    result = {"schema_version": 10, "profile_schema_version": "security-profile-v10", "identity": exporter.IDENTITY, **contract_binding(), "cases": {"001": case["result"]}}
    exporter.write_json(case["run_dir"] / "manifest.json", manifest)
    exporter.write_json(case["run_dir"] / "experiment-result.json", result)
    with pytest.raises(ValueError, match="thirty-case"):
        exporter.build_export_plan(case["run_dir"], case["skills"])
    manifest["cases"] = [{**case["item"], "case_id": f"{index:03}", "sample_id": sample,
                           "basename": f"{index:03}-local-config"}
                          for index, sample in enumerate(exporter.SAMPLE_IDS, 1)]
    result["cases"] = {f"{index:03}": {} for index in range(1, 31)}
    manifest["cases"][9]["sample_id"] = "N01"
    exporter.write_json(case["run_dir"] / "manifest.json", manifest)
    exporter.write_json(case["run_dir"] / "experiment-result.json", result)
    with pytest.raises(ValueError, match="Fixed numbering"):
        exporter.build_export_plan(case["run_dir"], case["skills"])


def test_staging_refuses_final_deliveries_or_existing_data(exporter, case, tmp_path):
    for path in (exporter.REPOSITORY_ROOT / "result", case["run_dir"] / "staging", case["skills"]):
        with pytest.raises(ValueError, match="overlap"):
            exporter._staging_directory(path, case["run_dir"], case["skills"])
    path = tmp_path / "occupied"
    path.mkdir()
    (path / "keep.txt").write_text("existing")
    with pytest.raises(ValueError, match="empty directory"):
        exporter._staging_directory(path, case["run_dir"], case["skills"])
    assert (path / "keep.txt").read_text() == "existing"


def _tiny_png(rgb=b"\xff\xff\xff"):
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(b"\0" + rgb)) + chunk(b"IEND", b"")


def test_export_stages_exact_pairs_and_binds_actual_png_bytes(exporter, case, tmp_path, monkeypatch):
    row = load(exporter, case)
    plan = {"schema_version": 5, "profile_schema_version": "security-profile-v10", "cases": [row], "run_id": "run", "manifest_sha256": "m", "experiment_result_sha256": "r"}
    monkeypatch.setattr(exporter, "build_export_plan", lambda *args, **kwargs: deepcopy(plan))
    def render(command, **kwargs):
        args = dict(zip(command[2::2], command[3::2]))
        output = Path(args["--output-dir"])
        output.mkdir(parents=True)
        svg_dir = Path(args["--svg-output-dir"])
        raw = _tiny_png()
        svg = '<svg xmlns="http://www.w3.org/2000/svg"></svg>'
        (output / (row["basename"] + ".png")).write_bytes(raw)
        (svg_dir / (row["basename"] + ".svg")).write_text(svg, encoding="utf-8")
        entry = {"basename": row["basename"], "kind": "cfg", "counts": exporter._png.graph_counts(row["cfg"]),
                 "width": 1, "height": 1, "png_sha256": hashlib.sha256(raw).hexdigest(),
                 "svg_sha256": hashlib.sha256(svg.encode()).hexdigest(),
                 **{key: True for key in ("counts_checks_passed", "text_checks_passed", "bounds_checks_passed",
                                          "identity_checks_passed", "png_dimensions_checked")}}
        exporter.write_json(Path(args["--audit"]), {"status": "passed", "samples": [entry],
            "input_sha256": sha_file(Path(args["--input"]))})
    monkeypatch.setattr(exporter.subprocess, "run", render)
    staging = tmp_path / "staging"
    before = sha_file(case["zip"])
    manifest = exporter.export(case["run_dir"], staging, skills_dir=case["skills"], node_modules=tmp_path)
    assert manifest["published"] is False and manifest["visual_review"] == "pending"
    assert manifest["schema_version"] == 5 and manifest["profile_schema_version"] == "security-profile-v10"
    assert sha_file(case["zip"]) == before
    assert exporter.validate_staging(plan, staging)[0]["kind"] == "cfg"
    png = staging / row["png_file"]
    assert exporter._png.inspect_png(png)["source"] == row["provenance"]
    # Even a valid PNG with correct metadata cannot replace the renderer's pixels.
    png.write_bytes(_tiny_png(b"\0\0\0"))
    exporter._png.bind_png_source(png, row["provenance"])
    with pytest.raises(ValueError, match="PNG image bytes differ"):
        exporter.validate_staging(plan, staging)


def test_strict_json_rejects_duplicate_keys_and_nonfinite_numbers(exporter, tmp_path):
    path = tmp_path / "bad.json"
    for text in ('{"x":1,"x":2}', '{"x":NaN}'):
        path.write_text(text)
        with pytest.raises(ValueError):
            exporter.read_json(path)


def test_graph_cannot_claim_audit_passed_without_current_valid_audit(exporter, case):
    case["result"]["feedback"]["status"] = "audit_passed"
    case["result"]["selection"].update(feedback_status="audit_passed", auditor_passed=True)
    exporter.write_json(case["root"] / "selection.json", case["result"]["selection"])
    commit(exporter, case)
    with pytest.raises(ValueError, match="lacks a current valid passing audit"):
        load(exporter, case)


def test_snapshot_bytes_must_still_match_frozen_source(exporter, case):
    path = case["root"] / "feedback/inputs/package/data.bin"
    path.write_bytes(b"changed")
    with pytest.raises(ValueError):
        load(exporter, case)


def test_assistant_review_is_graph_bound_and_separate_from_model_judgment(exporter, case, tmp_path):
    row = load(exporter, case)
    path = tmp_path / "assistant/001.json"
    value = {"run_id": case["run_dir"].name, "case_id": "001", "reviews": [{
        "revision": 0, "graph_sha256": row["graph_sha256"], "assessment": "助手复核：保留标注争议。",
        "observations": ["仅工具调度不支持 model_observe。"]}]}
    exporter.write_json(path, value)
    review = exporter._assistant_review(path.parent, case["run_dir"], case["item"], case["result"], row)
    assert review["human_confirmed"] is False and review["reviews"][0]["matches_selected_graph"] is True
    text = exporter.suggestions({**row, "assistant_review": review})
    assert "未经人工确认" in text and "当前所选图" in text and value["reviews"][0]["assessment"] in text
    prior = {**row, "selected_revision": 1}
    old = exporter._assistant_review(path.parent, case["run_dir"], case["item"], case["result"], prior)
    assert old["reviews"][0]["matches_selected_graph"] is False
    assert "历史轮次，不能作为当前图结论" in exporter.suggestions({**prior, "assistant_review": old})
    value["reviews"][0]["graph_sha256"] = "f" * 64
    exporter.write_json(path, value)
    with pytest.raises(ValueError, match="does not belong"):
        exporter._assistant_review(path.parent, case["run_dir"], case["item"], case["result"], row)


def test_execution_only_review_requires_no_actual_graph(exporter, case, tmp_path):
    row = load(exporter, case)
    path = tmp_path / "assistant/001.json"
    value = {"run_id": case["run_dir"].name, "case_id": "001", "reviews": [{
        "revision": None, "graph_sha256": None, "assessment": "调用失败，未得到可用图。",
        "observations": ["仅说明执行记录边界，不能判断图语义或安全标注正确性。"]}]}
    exporter.write_json(path, value)
    with pytest.raises(ValueError, match="Execution-only review requires no selected or valid graph"):
        exporter._assistant_review(path.parent, case["run_dir"], case["item"], case["result"], row)
    empty_row = {**row, "cfg": None, "selected_revision": None, "graph_sha256": None, "audit": None, "profiles": {}}
    empty_result = {"feedback": {"status": "extraction_error"}, "selection": None}
    review = exporter._assistant_review(path.parent, case["run_dir"], case["item"], empty_result, empty_row)
    assert review["status"] == "execution_only" and review["human_confirmed"] is False
    assert review["reviews"][0]["scope"] == "execution_only"
    assert review["reviews"][0]["matches_selected_graph"] is False
    text = exporter.suggestions({**empty_row, "assistant_review": review})
    assert "仅执行记录复核，无可用图" in text and "不计作语义复核成功" in text
    value["reviews"].append(deepcopy(value["reviews"][0]))
    exporter.write_json(path, value)
    with pytest.raises(ValueError, match="Duplicate or mixed execution-only"):
        exporter._assistant_review(path.parent, case["run_dir"], case["item"], empty_result, empty_row)


@pytest.mark.parametrize("revision,digest", [(None, "f" * 64), (0, None), (False, None)])
def test_partial_null_or_noninteger_review_is_invalid(exporter, case, tmp_path, revision, digest):
    row = load(exporter, case)
    value = {"run_id": case["run_dir"].name, "case_id": "001", "reviews": [{
        "revision": revision, "graph_sha256": digest, "assessment": "不得混合图与执行身份", "observations": []}]}
    exporter.write_json(tmp_path / "reviews/001.json", value)
    with pytest.raises(ValueError):
        exporter._assistant_review(tmp_path / "reviews", case["run_dir"], case["item"], case["result"], row)


def test_long_execution_diagnostics_are_summarized_without_touching_evidence(exporter, case):
    errors = [f"findings.{index}.controlled_refs.0\n  Input should be a valid dictionary or instance of ControlledRef "
              f"[type=model_type, input_value='fact_{index:04}', input_type=str]\n"
              "    For further information visit https://errors.pydantic.dev/2/v/model_type"
              for index in range(159)]
    reason = "159 validation errors for AuditResult\n" + "\n".join(errors)
    case["result"]["feedback"]["reason"] = reason
    commit(exporter, case)
    row = load(exporter, case)
    assert row["feedback_reason"] == reason  # Complete original diagnostics for the page.
    summary = row["feedback_reason_summary"]
    assert len(summary) <= 600 and summary.startswith("159 validation errors for AuditResult")
    assert "findings.0.controlled_refs.0" in summary
    assert "Input should be a valid dictionary or instance of ControlledRef" in summary
    assert "findings.158" not in summary
    text = exporter.suggestions(row)
    assert summary in text and "findings.158" not in text
    assert "原始运行记录" in text and "审查页也可展开全文" in text
    assert row["cfg"] == case["result"]["feedback"]["last_valid_cfg"]
    assert row["source"]["files"] == case["source"]["files"]
    assert row["profiles"] == case["result"]["annotation"]["profiles"]
    failure = exporter.render_samples({"cases": [{**row, "cfg": None}]})["samples"][0]["failure"]
    assert failure["reason"] == summary  # Failure cards are readable, not diagnostic dumps.


def test_summary_retains_distinct_representative_errors_and_short_reason(exporter):
    raw = ("2 validation errors for AuditResult\nfindings.0.controlled_refs.0\n"
           "  Input should be a valid dictionary [type=model_type, input_value='x', input_type=str]\n"
           "findings.0.reason\n  Field required [type=missing, input_value={}, input_type=dict]\n")
    summary = exporter.reason_summary(raw)
    assert "Input should be a valid dictionary" in summary and "Field required" in summary
    assert "findings.0.reason" in summary
    assert exporter.reason_summary("核对响应未完整返回。") == "核对响应未完整返回。"
    assert len(exporter.reason_summary("a" * 10000)) <= 600
