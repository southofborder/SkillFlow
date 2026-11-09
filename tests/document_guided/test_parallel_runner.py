"""Seven-call orchestration with injected fragments and the real offline backend."""
from copy import deepcopy
from threading import Event, Lock

import pytest

from skillflow.common.recording import implementation_provenance
from skillflow.document_guided import runner
from skillflow.document_guided.online import read
from skillflow.propagation.annotation.loading import load_annotation_run
from tests.document_guided.test_runner import _fixture


def _flat(raw):
    """Convert this existing synthetic fixture, never a production migration."""
    def segment(value):
        if value.get("kind") == "for_each":
            return {**{key: deepcopy(item) for key, item in value.items() if key != "body"},
                    "body": [segment(child) for child in value["body"]]}
        operations = []
        for event in value["events"]:
            for operation in event["atomic_ops"]:
                operation = deepcopy(operation)
                if operation["op"] == "compute":
                    operation["effect"] = event["effect"]
                operations.append(operation)
        return {"mode": value["mode"], "ops": operations, "returns": deepcopy(value.get("returns", [])),
                "evidences": deepcopy(value["evidences"])}
    result = {"outcome": "completed", "realizations": [
        {key: deepcopy(item) for key, item in row.items() if key != "status"}
        for row in raw["realizations"]], "demands": deepcopy(raw["demands"]),
        "expressions": deepcopy(raw["expressions"]), "locations": {}, "ir_semantics": {}}
    for name, location in raw["locations"].items():
        result["locations"][name] = {**deepcopy(location), "evidences": deepcopy(raw["location_evidences"][name])}
    for identity, spec in raw["ir_semantics"].items():
        evidence = [{key: deepcopy(value) for key, value in item.items() if key != "value"}
                    for item in spec["operator_evidences"]]
        result["ir_semantics"][identity] = {"order": spec["order"], "evidences": evidence,
            "segments": [segment(item) for item in spec["events"]],
            "output_bindings": deepcopy(spec["output_bindings"]), "sensitivity": deepcopy(spec.get("sensitivity", []))}
    return result


def _cfg_wire(candidate):
    wire = {key: deepcopy(value) for key, value in candidate.items() if key != "declared_context_keys"}
    for block in wire["blocks"]:
        for ir in block["instructions"]:
            ir.pop("instruction_ref")
            for side in ("inputs", "outputs"):
                ir[side] = [{key: value for key, value in operand.items()
                             if key in {"type", "identifier", "literal_value"}} for operand in ir[side]]
    return wire


def freeze_producer(monkeypatch):
    # These tests exercise orchestration, not producer-code mutation detection.
    # The real provenance shape is frozen to avoid unrelated concurrent edits.
    frozen = implementation_provenance()
    for module in ("skillflow.document_guided.runner", "skillflow.document_guided.online",
                   "skillflow.document_guided.source_review", "skillflow.task.runner",
                   "skillflow.propagation.runner", "skillflow.doe.formal_runner"):
        monkeypatch.setattr(module + ".implementation_provenance", lambda: deepcopy(frozen))


@pytest.fixture(autouse=True)
def independent_offline_producer(monkeypatch):
    freeze_producer(monkeypatch)
    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)


class Harness:
    def __init__(self, directory, *, domains=(), annotation_failure=False, canaries=False,
                 repair_failure=None, final_failure=False):
        self.directory = directory
        self.example, candidate = _fixture()
        self.graph = _cfg_wire(candidate)
        self.wire = _flat(self.example["annotation"])
        from skillflow.document_guided.fragments import split_fragments
        self.fragments = split_fragments(self.wire)
        if canaries and not self.fragments["sensitivity"]["declarations"]:
            ir = next(iter(self.wire["ir_semantics"]))
            self.fragments["sensitivity"]["declarations"].append({
                "instruction_id": ir, "value": {"kind": "local", "name": "label"},
                "label": "Synthetic input sensitivity", "evidences": [{"file": "skill/SKILL.md",
                    "start_line": 1, "end_line": 1,
                    "reason": "Synthetic sensitivity declaration checks input isolation; not an empirical source assessment."}]})
        self.domains, self.annotation_failure = domains, annotation_failure
        self.repair_failure, self.final_failure = repair_failure, final_failure
        self.canaries = canaries
        self.calls, self.prompts = [], {}
        self.attempts = {}
        self.lock = Lock()
        self.graph_started, self.mapping_started, self.sensitivity_started = Event(), Event(), Event()

    def factory(self, stage, owner):
        harness = self
        class Client:
            def complete(self, prompt):
                return harness.complete(stage, prompt)
        return Client()

    def complete(self, stage, prompt):
        with self.lock:
            self.attempts[stage] = self.attempts.get(stage, 0) + 1
            if self.attempts[stage] > 1:
                assert ((stage.startswith("revision") and self.repair_failure is not None)
                        or self.final_failure or self.annotation_failure), "Unexpected correction: " + stage
            self.calls.append(stage)
            self.prompts[stage] = prompt
        base = stage.removeprefix("revision-")
        if stage in {"task", "revision/task"}:
            if self.canaries and stage == "task":
                assert self.graph_started.wait(20), "CFG waited for independent Task"
            candidate = deepcopy(self.example["task_candidate"])
            if stage == "revision/task":
                candidate["purpose"]["text"] += " Preserve the source-supported original value."
            return candidate
        if base in {"flow", "processing", "task-correspondence", "sensitivity"}:
            if self.canaries and base == "task-correspondence":
                self.mapping_started.set()
                assert self.sensitivity_started.wait(20), "Mapping blocked independent sensitivity"
            if self.canaries and base == "sensitivity":
                self.sensitivity_started.set()
                assert self.mapping_started.wait(20), "Sensitivity blocked independent mapping"
            if base == "flow":
                return "# Working document\nPreserve the original field. skill/SKILL.md:1-1"
            if base == "processing" and (self.annotation_failure or
                    (self.repair_failure == "annotation" and stage.startswith("revision"))):
                # Malformed whole fragment cannot be passed off as an empty annotation.
                return {"outcome": "cannot_assess", "failure": {"reason": "Injected unsupported submission"}}
            fragment = deepcopy(self.fragments[base])
            if base == "sensitivity" and self.canaries and fragment.get("declarations"):
                fragment["declarations"][0]["label"] += " SENSITIVITY_DOCUMENT_CANARY"
            return fragment
        if base == "graph":
            self.graph_started.set()
            if self.repair_failure == "cfg" and stage.startswith("revision"):
                return {"outcome": "cannot_assess", "failure": {"reason": "Injected source representation barrier.",
                    "evidences": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1, "reason": "The source identifies the behavior."}]}}
            return deepcopy(self.graph)
        if base == "annotation":
            if self.annotation_failure or (self.repair_failure == "annotation" and stage.startswith("revision")):
                return {"outcome": "cannot_assess", "failure": {"reason": "Injected supported capability failure.",
                    "instruction_ids": ["ir_001"], "evidences": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
                        "reason": "The source identifies the unrepresented relationship."}]}}
            return deepcopy(self.wire)
        if stage in {"review", "revision/review"}:
            if self.final_failure and stage.startswith("revision"):
                return {"outcome": "cannot_assess", "failure": {"reason": "Injected incomplete review.",
                    "target_ids": ["annotation:"], "source_refs": []}}
            findings = []
            if stage == "review":
                for domain in self.domains:
                    item = {"domain": domain, "target_ids": [domain + ":"],
                        "explanation": "REVIEW_FREE_TEXT_CANARY: injected routing exercise, not semantic verification.",
                        "source_refs": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1}],
                        "suggestion": "Preserve the source-supported relationship."}
                    if domain == "task":
                        item["task_objection"] = {"code": "atomicity", "requirement_ids": ["R1"],
                            "source_spans": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1}]}
                    findings.append(item)
            return {"outcome": "completed", "findings": findings}
        raise AssertionError("Unexpected stage: " + stage)

    def prepare(self, package):
        package.mkdir()
        source = self.example["source"] + "\nOriginal source quotation: 保留原文，不翻译引文。\r\n"
        (package / "SKILL.md").write_bytes(source.encode("utf-8"))
        runner.prepare(package, run_dir=self.directory)
        return source


def test_seven_calls_dependency_parallelism_true_backend_and_zero_call_replay(tmp_path, monkeypatch):
    original_save = runner._save
    def checked_save(run, value, *, replay=False):
        if replay:
            stored = read(run / "result.json")
            differences = {key: (stored.get(key), item) for key, item in value.items()
                           if key != "counts" and stored.get(key) != item}
            assert not differences, differences
        return original_save(run, value, replay=replay)
    monkeypatch.setattr(runner, "_save", checked_save)
    harness = Harness(tmp_path / "run", canaries=True)
    source = harness.prepare(tmp_path / "package")
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == "complete", result
    assert len(harness.calls) == result["counts"]["logical_calls"] == 7
    assert not result["repair_used"]
    assert result["counts"]["structural_corrections"] == 0
    assert (harness.directory / "doe/doe-result.json").is_file()
    assert (harness.directory / "propagation/data.json").is_file()
    assert "relationships" not in harness.calls and "graph-review" not in harness.calls
    assert "SENSITIVITY_DOCUMENT_CANARY" not in harness.prompts["task-correspondence"]
    assert "annotation" not in harness.calls
    assert "SENSITIVITY_DOCUMENT_CANARY" in harness.prompts["review"]
    assert source in (harness.directory / "source/inputs/package/SKILL.md").read_bytes().decode("utf-8")
    accepted = load_annotation_run(harness.directory / "annotation")
    assert accepted["manifest"]["candidate_origin"] == "program_assembled_fragments"
    assert accepted["raw_annotation"]["ir_semantics"]
    assert "task_revision_id" not in accepted["wire_annotation"]
    assert accepted["raw_annotation"]["task_revision_id"] == accepted["task"]["task_sha256"]
    saved = {str(path.relative_to(harness.directory)): path.read_bytes() for path in harness.directory.rglob("response.json")}
    def forbidden(*args, **kwargs):
        raise AssertionError("Completed answers and replay must never create a client")
    assert runner.run(harness.directory, client_factory=forbidden) == result
    assert runner.replay(harness.directory) == result
    assert len(harness.calls) == 7
    assert saved == {str(path.relative_to(harness.directory)): path.read_bytes() for path in harness.directory.rglob("response.json")}


@pytest.mark.parametrize("domains,count,regenerated", [
    (("annotation",), 11, {"processing", "task-correspondence", "sensitivity"}),
    (("task",), 10, {"task", "task-correspondence"}),
    (("cfg",), 12, {"graph", "processing", "task-correspondence", "sensitivity"}),
    (("task", "cfg", "annotation"), 13, {"task", "graph", "processing", "task-correspondence", "sensitivity"}),
])
def test_one_shared_repair_regenerates_only_dependency_closure(tmp_path, domains, count, regenerated):
    harness = Harness(tmp_path / "run", domains=domains)
    harness.prepare(tmp_path / "package")
    def stop_at_backend(state):
        if state["stage"] == "propagation":
            raise KeyboardInterrupt("Focused repair routing stops at the independently tested backend")
    result = runner.run(harness.directory, client_factory=harness.factory, progress=stop_at_backend)
    assert result["status"] == "interrupted", result
    assert result["selected_annotation"] == "revision/annotation"
    assert result["repair_used"] and result["annotation_review"] == "review_passed"
    assert len(harness.calls) == result["counts"]["logical_calls"] == count
    expected = {"revision/task" if name == "task" else "revision-" + name for name in regenerated} | {"revision/review"}
    assert {name for name in harness.calls if name.startswith("revision")} == expected
    for name in ("processing", "sensitivity", "task-correspondence"):
        assert harness.calls.count(name) == 1
    if "task" in domains:
        assert "REVIEW_FREE_TEXT_CANARY" not in harness.prompts["revision/task"]
        assert "SENSITIVITY_DOCUMENT_CANARY" not in harness.prompts["revision/task"]
        assert "station-west" not in harness.prompts["revision/task"]
    for name in ("task-correspondence", "revision-task-correspondence"):
        if name in harness.prompts:
            assert "REVIEW_FREE_TEXT_CANARY" not in harness.prompts[name]
            assert "SENSITIVITY_DOCUMENT_CANARY" not in harness.prompts[name]
    assert "REVIEW_FREE_TEXT_CANARY" not in harness.prompts["revision/review"]


def test_legal_annotation_failure_still_has_partial_review_without_backend_or_retry(tmp_path):
    harness = Harness(tmp_path / "run", annotation_failure=True)
    harness.prepare(tmp_path / "package")
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == "failed", result
    assert result["selected_annotation"] is None and result["diagnostic_only"]
    assert "annotation" not in harness.calls and harness.calls.count("processing") == 2
    material = read(harness.directory / "review/inputs.json")
    assert material["annotation"] is None and not material["availability"]["annotation"]
    assert material["stage_failures"]["processing"]["status"] == "structural_failure"
    assert not (harness.directory / "propagation").exists()
    assert not (harness.directory / "doe").exists()
    assert runner.replay(harness.directory) == result


@pytest.mark.parametrize("domain", ["cfg", "annotation"])
def test_failed_shared_repair_keeps_original_consistent_bundle(tmp_path, domain):
    harness = Harness(tmp_path / "run", domains=("task", domain), repair_failure=domain)
    harness.prepare(tmp_path / "package")
    def stop_at_backend(state):
        if state["stage"] == "propagation":
            raise KeyboardInterrupt("Inspect consistent selection before deterministic backend")
    result = runner.run(harness.directory, client_factory=harness.factory, progress=stop_at_backend)
    assert result["status"] == "interrupted", result
    assert result["repair_used"] and result["selected_annotation"] == "annotation"
    selection = read(harness.directory / "selection.json")
    assert selection["task"]["path"] == "task/task.json"
    assert selection["cfg"]["path"] == "graph/initial.json"
    assert any("consistent new annotation" in text for text in result["limitations"])
    assert harness.calls.count("revision/task") == 1


def test_new_valid_bundle_survives_final_cannot_assess_with_diagnostic_status(tmp_path):
    harness = Harness(tmp_path / "run", domains=("annotation",), final_failure=True)
    harness.prepare(tmp_path / "package")
    def stop_at_backend(state):
        if state["stage"] == "propagation":
            raise KeyboardInterrupt("Inspect diagnostic selection")
    result = runner.run(harness.directory, client_factory=harness.factory, progress=stop_at_backend)
    assert result["status"] == "interrupted", result
    assert result["selected_annotation"] == "revision/annotation"
    assert result["diagnostic_only"] and result["annotation_review"] == "incomplete"
