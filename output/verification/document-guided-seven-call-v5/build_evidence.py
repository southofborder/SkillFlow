"""Offline evidence only: fixed fake answers, no client transport or Skill execution."""
from pathlib import Path
import json
import os
import subprocess
import sys

from skillflow.common.recording import implementation_provenance
from skillflow.document_guided import runner
from skillflow.document_guided.fragments import fragment_adapter
from skillflow.document_guided.online import read
from tests.document_guided.test_seven_call_partial import fixture

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent


def write(name, value):
    path = ROOT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    producer = implementation_provenance()
    write("implementation.json", producer)
    for kind in ("processing", "task-correspondence", "sensitivity"):
        write("formats/" + kind + ".schema.json", fragment_adapter(kind).json_schema())
    # This verification isolates the changed semantic pipeline. Existing graph
    # compilation runs normally; the unchanged external certificate renderer is
    # stubbed explicitly rather than counted as a semantic model call.
    runner._certificate = lambda *args, **kwargs: None
    cases = []
    for name, shared in (("independent-excess", False), ("shared-location-unresolved", True)):
        source, graph, task, fragments, identities = fixture(shared)
        package, directory = ROOT / "fixtures" / name / "package", ROOT / "fixtures" / name / "run"
        package.mkdir(parents=True, exist_ok=True)
        for row in source["files"]:
            path = package / row["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(row["content"].encode("utf-8"))
        if not (directory / "manifest.json").exists():
            runner.prepare(package, run_dir=directory, config={"reasoning_effort": "high"})
        calls = []

        class FixtureClient:
            def __init__(self, stage):
                self.stage = stage

            def complete(self, prompt):
                calls.append(self.stage)
                if self.stage == "flow":
                    return "# Flow\nPreserve independent body return and unresolved cache write. skill/SKILL.md:1-5"
                answer = task if self.stage == "task" else graph if self.stage == "graph" else (
                    {"outcome": "completed", "findings": []} if self.stage == "review" else fragments[self.stage])
                return json.dumps(answer, ensure_ascii=False)

        result = runner.run(directory, client_factory=lambda stage, owner: FixtureClient(stage))
        assert result["status"] == "partial", result
        assert result["counts"]["logical_calls"] == 7
        assert result["counts"]["structural_corrections"] == 0
        assert runner.replay(directory) == result
        code = ("import json; from skillflow.document_guided import runner; "
                "runner._certificate=lambda *a,**k:None; "
                "value=runner.replay(" + repr(str(directory)) + "); "
                "print(json.dumps({'status':value['status'],'calls':value['counts']['logical_calls']}))")
        replay = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
            encoding="utf-8", check=True, timeout=180, env={**os.environ, "PYTHONHASHSEED": "891"})
        checked = json.loads(replay.stdout)
        assert checked == {"status": "partial", "calls": 7}
        conclusions = []
        unresolved = []
        for path in (directory / "doe").rglob("*.json"):
            document = read(path)
            if document.get("coverage", {}).get("unresolved_boundaries"):
                unresolved = document["coverage"]["unresolved_boundaries"]
            for sink in document.get("sinks", []):
                if sink.get("boundary", {}).get("instruction_id") == identities["ir_filter"]:
                    conclusions += [row["conclusion"] for row in sink.get("data_reviews", [])]
        assert ("excess_supported" in conclusions) is (not shared)
        assert unresolved
        cases.append({"name": name, "run": str(directory.relative_to(ROOT)), "status": result["status"],
            "logical_calls": 7, "new_fixture_completions": len(calls),
            "independent_conclusions": sorted(set(conclusions)), "unresolved_boundary_count": len(unresolved),
            "same_process_replay": "matched", "fresh_process_replay": "matched",
            "target_model_calls": 0, "target_tokens": None})
    assert producer == implementation_provenance(), "Implementation changed while evidence was produced"
    evidence = {"verification_date": "2026-10-28", "status": "passed", "target_model_calls": 0,
        "target_tokens": None, "currency": None, "skill_execution": False,
        "implementation_sha256": producer["sha256"], "cases": cases,
        "renderer": "External graph certificate renderer stubbed; CFG compilation, propagation, DOE, save/load and replay are real.",
        "semantic_scope": "Synthetic engineering fixtures; no GA4 target run or empirical advantage claim."}
    write("offline-evidence.json", evidence)
    print(json.dumps({"status": evidence["status"], "cases": len(cases), "target_model_calls": 0,
                      "implementation_sha256": producer["sha256"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
