"""Independent zero-call review of the prospective direct-only boundaries."""
import pytest

from tools.doe.real_comparison import direct_continuation_v2 as epoch
from tools.doe.real_comparison import exploratory_cli as base
from tools.doe.real_comparison.protocol import write_json


def test_dependency_injection_preserves_frozen_code_and_original_globals():
    assert epoch.run_workflow.__code__ is base.run_workflow.__code__
    assert epoch.run_workflow.__globals__ is not base.run_workflow.__globals__
    assert epoch.run_workflow.__globals__["verify_run"] is epoch.verify
    assert epoch.run_workflow.__globals__["ExploratoryClient"] is epoch.RemainingClient
    assert base.run_workflow.__globals__["verify_run"] is base.verify_run
    assert base.run_workflow.__globals__["ExploratoryClient"] is base.ExploratoryClient
    complete = epoch.RemainingClient.complete
    assert complete.__code__ is base.ExploratoryClient.complete.__code__
    assert complete.__globals__ is not base.ExploratoryClient.complete.__globals__
    assert complete.__globals__["verify_run"] is epoch.verify
    assert complete.__globals__["cli"] is epoch.transport
    assert base.ExploratoryClient.complete.__globals__["cli"] is base.cli


def test_direct_main_and_fixed_r1_review_never_reach_native_pipeline(tmp_path, monkeypatch):
    main = {"workflow_id": "synthetic_audit_r1", "case_id": "synthetic",
            "kind": "main", "method": "audit", "repeat": 1, "source_sha256": "synthetic-source"}
    review = {**main, "workflow_id": "synthetic_audit_r1_review", "kind": "review",
              "original_workflow_id": main["workflow_id"]}
    write_json(tmp_path / "schedule.json", {"main": [main], "reviews": [review]})
    write_json(tmp_path / "plan.json", {"created_at": "2026-10-24T00:00:00+00:00"})
    source = tmp_path / "cases/synthetic/source-bundle.txt"
    source.parent.mkdir(parents=True)
    source.write_text("Synthetic source only.", encoding="utf-8")
    prompts = tmp_path / "prompts"
    prompts.mkdir()
    (prompts / "audit.txt").write_text("Declared Skill purpose\n{source_bundle}", encoding="utf-8")
    (prompts / "review.txt").write_text("{original_task}\n{original_answer}", encoding="utf-8")
    monkeypatch.setitem(epoch.run_workflow.__globals__, "verify_run", lambda *a, **kw: {})
    monkeypatch.setattr(base.native, "_native_pipeline",
                        lambda *a, **kw: pytest.fail("A direct workflow reached native execution"))
    calls = []
    def synthetic_complete(self, core):
        calls.append((self.workflow_id, core))
        return "Synthetic first answer." if self.item["kind"] == "main" else "Synthetic checked answer."
    monkeypatch.setattr(epoch.RemainingClient, "complete", synthetic_complete)
    assert epoch.run_workflow(tmp_path, main["workflow_id"])["status"] == "complete"
    assert epoch.run_workflow(tmp_path, review["workflow_id"])["status"] == "complete"
    assert len(calls) == 2 and "Synthetic first answer." in calls[1][1]
    assert epoch.read(tmp_path / "workflows" / review["workflow_id"] / "original.json")[
        "original_workflow_id"] == main["workflow_id"]
    with pytest.raises(base.native.ExecutionStop, match="cannot be retried"):
        epoch.run_workflow(tmp_path, main["workflow_id"])
    assert len(calls) == 2
    assert not list(tmp_path.rglob("dispatch.json"))


def test_batch_guard_rejects_imported_or_skillflow_identities(tmp_path, monkeypatch):
    write_json(tmp_path / "remaining-output-lineage.json", {"new_workflow_ids": ["new", "sf"]})
    monkeypatch.setattr(epoch, "verify", lambda *a, **kw: {})
    methods = {"new": "audit", "sf": "skillflow"}
    monkeypatch.setattr(base, "planned", lambda run, wid: {"method": methods.get(wid, "audit")})
    calls = []
    monkeypatch.setattr(epoch, "run_workflow", lambda run, wid: calls.append(wid))
    original_injected = epoch.injected
    def instrument(function, **dependencies):
        if function is not base.run_batch:
            return original_injected(function, **dependencies)
        def fake_engine(run, *, workers, runner):
            assert workers == 6
            for forbidden in ("imported", "sf"):
                with pytest.raises(ValueError, match="previously unlaunched direct"):
                    runner(run, forbidden)
            runner(run, "new")
            return {"target_calls": 0}
        return fake_engine
    monkeypatch.setattr(epoch, "injected", instrument)
    assert epoch.run_batch(tmp_path) == {"target_calls": 0}
    assert calls == ["new"]
