"""Offline result provenance checks; synthetic records are never corpus results."""

from skillflow.common.paths import project_root, resolve_material_path
from copy import deepcopy
import ast
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

BASE = project_root() / "experiments/graph/baseline"
SPEC = importlib.util.spec_from_file_location("semantics_result_integrity_test", project_root() / "tools/graph/baseline/result_integrity.py")
integrity = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(integrity)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def test_running_headers_and_footers_do_not_make_a_nonempty_body():
    from types import SimpleNamespace

    class Page:
        mediabox = SimpleNamespace(height=842)

        def __init__(self, body):
            self.body = body

        def extract_text(self, visitor_text):
            for text, y in [("Sample header", 820), ("27", 24), (self.body, 700)]:
                visitor_text(text, [1, 0, 0, 1, 0, y], [1, 0, 0, 1, 0, 0], None, 9)

    integrity.verify_page_bodies([Page("Actual result")])
    with pytest.raises(ValueError, match="no body content: 2"):
        integrity.verify_page_bodies([Page("Actual result"), Page("   ")])


@pytest.fixture
def trial(tmp_path):
    prompt = "SYNTHETIC PROVENANCE FIXTURE; not a model run"
    identity = {"prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest()}
    record = {
        "case": "N01", "variant": "sol-max", "repetition": 1,
        "split": "development", "status": "complete",
        "artifacts": "trials/N01/sol-max/1", **identity,
    }
    path = tmp_path / record["artifacts"]
    write(path / "analysis.json", {"synthetic_fixture": True})
    write(path / "trace.json", {
        **{key: record[key] for key in ("case", "variant", "repetition", "split")},
        "calls": [{"status": "complete", "prompt": prompt, "response": {"synthetic_fixture": True}}],
    })
    record["artifact_sha256"] = {name: integrity.sha(path / name) for name in ("analysis.json", "trace.json")}
    return path, record, identity


def test_valid_consistent_record_is_accepted_without_execution(trial):
    path, record, identity = trial
    integrity.verify_trial_record(record, deepcopy(record), path, identity)


def test_stale_report_cannot_override_persisted_trial(trial):
    path, record, identity = trial
    report = {**record, "status": "uncertain"}
    with pytest.raises(ValueError, match="report row disagree"):
        integrity.verify_trial_record(record, report, path, identity)


@pytest.mark.parametrize("mutation", ["unbound_analysis", "extra_file", "changed_file", "path_escape"])
def test_complete_artifact_inventory_is_required(trial, mutation):
    path, record, identity = trial
    if mutation == "unbound_analysis":
        record["artifact_sha256"].pop("analysis.json")
    elif mutation == "extra_file":
        write(path / "candidate.json", {"synthetic_fixture": True})
    elif mutation == "changed_file":
        write(path / "analysis.json", {"changed_after_commit": True})
    else:
        record["artifact_sha256"]["../analysis.json"] = "0" * 64
    with pytest.raises(ValueError, match="artifact"):
        integrity.verify_trial_record(record, deepcopy(record), path, identity)


@pytest.mark.parametrize("mutation", ["no_trace", "unfinished_call", "no_response", "wrong_prompt", "wrong_sample"])
def test_accepted_cfg_requires_trace_for_the_same_sample_and_prompt(trial, mutation):
    path, record, identity = trial
    trace_path = path / "trace.json"
    if mutation == "no_trace":
        trace_path.unlink()
        record["artifact_sha256"].pop("trace.json")
    else:
        trace = integrity.read(trace_path)
        if mutation == "unfinished_call":
            trace["calls"][0]["status"] = "running"
        elif mutation == "no_response":
            trace["calls"][0]["response"] = None
        elif mutation == "wrong_prompt":
            trace["calls"][0]["prompt"] += " another Skill"
        else:
            trace["case"] = "R06"
        write(trace_path, trace)
        record["artifact_sha256"]["trace.json"] = integrity.sha(trace_path)
    with pytest.raises(ValueError, match="trace|prompt"):
        integrity.verify_trial_record(record, deepcopy(record), path, identity)


def test_result_loading_verifies_the_freeze_first(monkeypatch, tmp_path):
    def reject(base):
        assert base == BASE
        raise ValueError("Frozen content changed: inputs/upstream/pdf/SKILL.md")
    monkeypatch.setattr(integrity.freeze, "verify_freeze", reject)
    with pytest.raises(ValueError, match="Frozen content changed"):
        integrity.verify_result_sources(BASE, tmp_path / "missing-run", "sol-max")


@pytest.mark.parametrize("mutation", ["freeze", "split", "dataset"])
def test_run_identity_must_match_approved_freeze(tmp_path, mutation):
    original = BASE / "runs/baseline-sol-max-v1"
    experiment = integrity.read(original / "experiment.json")
    dataset = integrity.read(original / "dataset.json")
    if mutation == "freeze":
        experiment["provenance"]["freeze_manifest_sha256"] = "0" * 64
    elif mutation == "split":
        experiment["cases"][0]["split"] = "held_out"
    else:
        dataset["cases"][0]["prompt_sha256"] = "0" * 64
    write(tmp_path / "experiment.json", experiment)
    write(tmp_path / "dataset.json", dataset)
    with pytest.raises(ValueError, match="freeze|split|identity"):
        integrity.verify_result_sources(BASE, tmp_path, "sol-max")


def test_transport_metadata_preserves_sse_stream_parameters():
    metadata = {"protocol": "chat-completions-sse-v1", "parameters": {
        "stream": True, "stream_options": {"include_usage": True},
    }}
    assert integrity.transport_metadata({"provenance": {"transport": metadata}}) == metadata


def test_legacy_transport_absence_is_not_inferred_as_streaming_or_nonstreaming():
    assert integrity.transport_metadata({"provenance": {}}) == {"protocol": None, "parameters": None}


def test_model_identity_keeps_exact_deepseek_request_and_return_names_separate():
    experiment = {"variants": [{"id": "deepseek-v4-flash-max", "model": "deepseek-v4-flash",
                               "endpoint": "https://api.deepseek.com/chat/completions",
                               "reasoning_effort": "max", "api_key": "SYNTHETIC-SECRET"}],
                  "provenance": {"provider_change": {
                      "provider_change_id": "synthetic-provider-change", "inherited_trials": 0,
                      "case_and_prompt_identity_equal": True, "production_source_identity_equal": True,
                      "requested_returned_model_note": "Names differ; do not infer model equivalence.",
                      "prior_runs": [{"directory": "runs/earlier", "report_sha256": "a" * 64}],
                      "secret": "SYNTHETIC-SECRET"}}}
    trials = [{"trace": {"calls": [
        {"generation": 1, "returned_model": "deepseek-flash", "http_attempts": [
            {"http_status": 524, "returned_model": None},
            {"http_status": 200, "returned_model": "deepseek-flash"}]},
        {"generation": 2, "returned_model": "deepseek-flash", "http_attempts": [
            {"http_status": 200, "returned_model": "deepseek-flash"}]},
    ]}}]
    metadata = integrity.model_identity_metadata(experiment, "deepseek-v4-flash-max", trials)
    assert metadata["requested"]["model"] == "deepseek-v4-flash"
    assert metadata["requested"]["endpoint"] == "https://api.deepseek.com/chat/completions"
    assert metadata["requested"]["reasoning_effort"] == "max"
    assert metadata["http_returned_model_counts"] == {"deepseek-flash": 2}
    assert metadata["http_attempts_without_returned_model"] == 1
    assert metadata["returned_names_differ_from_requested"] == ["deepseek-flash"]
    assert metadata["provider_change"]["inherited_trials"] == 0
    assert metadata["provider_change"]["prior_runs"][0]["report_sha256"] == "a" * 64
    assert "SYNTHETIC-SECRET" not in json.dumps(metadata)


def test_missing_returned_model_is_not_filled_from_request_or_generation_name():
    experiment = {"variants": [{"id": "custom", "model": "requested"}]}
    trace = {"calls": [{"generation": 1, "returned_model": "generation-name",
                         "http_attempts": [{"http_status": 200}]}]}
    observed = integrity.model_return_observations(trace)
    assert observed[0]["returned_model"] == "generation-name"
    assert observed[0]["http_attempts"][0]["returned_model"] is None
    metadata = integrity.model_identity_metadata(experiment, "custom", [{"trace": trace}])
    assert metadata["http_returned_model_counts"] == {}
    assert metadata["http_attempts_without_returned_model"] == 1
    assert metadata["provider_change"] is None


@pytest.mark.parametrize("variants", [[], [{"id": "other"}], [{"id": "duplicate"}, {"id": "duplicate"}]])
def test_model_metadata_rejects_ambiguous_or_missing_variant(variants):
    with pytest.raises(ValueError, match="exactly one"):
        integrity.model_identity_metadata({"variants": variants}, "duplicate", [])


def test_pdf_variant_default_uses_recorded_deepseek_identity_not_sol():
    experiment = {"variants": [{"id": "deepseek-v4-flash-max"}]}
    assert integrity.select_result_variant(experiment) == "deepseek-v4-flash-max"
    experiment["variants"].append({"id": "another-model"})
    with pytest.raises(ValueError, match="exactly one"):
        integrity.select_result_variant(experiment)
    assert integrity.select_result_variant(experiment, "deepseek-v4-flash-max") == "deepseek-v4-flash-max"


def test_pdf_script_summary_distinguishes_original_text_from_serialized_array():
    # Exercise the actual pure formatter without requiring reportlab in test Python.
    source = project_root() / "tools/graph/baseline/build_results_pdf.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    formatter = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                     and node.name == "script_content_summary")
    namespace = {"json": json, "hashlib": hashlib}
    exec(compile(ast.Module(body=[formatter], type_ignores=[]), str(source), "exec"), namespace)
    summarize = namespace["script_content_summary"]
    script = "print('中文')\nprint('done')"
    lines = script.splitlines()
    plain, structured = summarize(script), summarize(lines)
    text_sha = hashlib.sha256(script.encode("utf-8")).hexdigest()
    json_sha = hashlib.sha256(json.dumps(lines, ensure_ascii=False).encode("utf-8")).hexdigest()
    assert text_sha != json_sha
    assert text_sha in plain and "依据：原文 UTF-8" in plain
    assert json_sha in structured and "JSON 序列化值的 UTF-8（非原始脚本字节）" in structured
    assert text_sha not in structured and json_sha not in plain


def test_incomplete_http_200_stream_is_separate_from_local_error_and_known_failure():
    trace = {"calls": [{"generation": 2, "status": "error", "http_attempts": [
        {"status": "error", "http_status": 524},
        {"status": "error", "http_status": 200, "stream": {"outcome": "remote_outcome_unknown"}},
    ]}]}
    assert integrity.remote_unknown_attempts(trace) == [{"generation": 2, "http_attempt": 2, "http_status": 200}]
    assert integrity.remote_unknown_attempts(None) == []


def test_pdf_provider_change_starts_with_its_own_page_and_running_header():
    from types import SimpleNamespace

    source = project_root() / "tools/graph/baseline/build_results_pdf.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    builder = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                   and node.name == "model_identity_story")
    layout = SimpleNamespace(
        heading=lambda text, *args, **kwargs: SimpleNamespace(text=text, **kwargs),
        p=lambda text, *args: SimpleNamespace(text=text),
        table=lambda *args: SimpleNamespace(text="table"),
    )
    namespace = {"layout": layout, "PageBreak": lambda: SimpleNamespace(page_break=True),
                 "Spacer": lambda *args: SimpleNamespace(text="space"), "show": str}
    exec(compile(ast.Module(body=[builder], type_ignores=[]), str(source), "exec"), namespace)
    requested = dict.fromkeys(("id", "model", "endpoint", "reasoning_effort", "timeout_ms",
                               "max_retries", "max_repair_rounds"), "synthetic")
    change = dict.fromkeys(("provider_change_id", "authorized_on", "inherited_trials",
                           "case_and_prompt_identity_equal", "production_source_identity_equal",
                           "manifest_sha256", "config_sha256"), "synthetic")
    change["prior_runs"] = [{"directory": f"prior-{number}", "experiment_sha256": "a" * 64,
                             "report_sha256": "b" * 64} for number in range(3)]
    metadata = dict(requested=requested, provider_change=change, http_returned_model_counts={},
                    http_attempts_without_returned_model=0, returned_names_differ_from_requested=[])
    story = namespace["model_identity_story"](metadata)
    boundary = next(i for i, item in enumerate(story)
                    if getattr(item, "text", "") == "服务与模型变更来源")
    assert getattr(story[boundary - 1], "page_break", False)
    assert story[boundary].sample == "来源变更"
    assert all(any(f"prior-{number}" in getattr(item, "text", "") for item in story[boundary:])
               for number in range(3))
    metadata["provider_change"] = None
    assert sum(getattr(item, "page_break", False)
               for item in namespace["model_identity_story"](metadata)) == 1


def test_pdf_contents_resets_running_sample_without_extra_page_break():
    from types import SimpleNamespace

    source = project_root() / "tools/graph/baseline/build_results_pdf.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    builder = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                   and node.name == "results_toc")
    heading, index, trailing_break = SimpleNamespace(review_sample=None), object(), object()
    namespace = {"layout": SimpleNamespace(toc=lambda: [heading, index, trailing_break])}
    exec(compile(ast.Module(body=[builder], type_ignores=[]), str(source), "exec"), namespace)
    story = namespace["results_toc"]()
    assert story == [heading, index]
    assert heading.review_sample == "目录"


def test_pdf_first_short_terminator_keeps_final_draft_id_with_block():
    source = project_root() / "tools/graph/baseline/build_results_pdf.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    builder = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                   and node.name == "instruction_flowables")
    namespace = {"KeepTogether": lambda items: ("keep", items)}
    exec(compile(ast.Module(body=[builder], type_ignores=[]), str(source), "exec"), namespace)
    arrange = namespace["instruction_flowables"]
    intro = ["block title", "source", "block constraints"]
    short = ["ir return", "input", "outputs", "ir constraints", "draft_instruction_id"]
    for opcode in ("dispatch", "return"):
        assert arrange(intro, short, 0, opcode) == [("keep", intro + short)]
        assert arrange(intro, short, 1, opcode) == [("keep", short)]
    long = short + ["metadata", "long script digest"]
    assert arrange(intro, long, 0, "return") == [("keep", intro + long[:2]), *long[2:]]
    assert arrange(intro, long, 1, "transform") == long
