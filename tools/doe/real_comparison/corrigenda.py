"""Versioned human reference corrections and complete, closed grading epochs.

Every workspace is another grading view of the same frozen target cohort.
Original references, scores and target bytes are never rewritten. Human
confirmation and regrading are explicit submissions, never synthesized here.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import shutil

from .protocol import SCHEMA, canonical_hash, sha256, utc_now, write_json


def _read(path, default=None):
    path = Path(path)
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def _safe_name(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", value):
        raise ValueError("Unsafe reference correction identity")
    return value


def _inside(root, relative):
    root = Path(root).resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError("A reference correction artifact escapes its grading workspace")
    return path


def _copy_file(source, target):
    source, target = Path(source), Path(target)
    if not source.is_file() or source.is_symlink():
        raise ValueError("Reference corrections require original regular files")
    if target.exists():
        if target.read_bytes() != source.read_bytes():
            raise ValueError("An immutable grading-epoch copy differs")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)  # Never hardlink: child edits cannot alter history.


def _root(run_dir):
    run = Path(run_dir).resolve()
    epoch = _read(run / "grading-epoch.json")
    return Path(epoch["logical_study_root"]).resolve() if epoch else run


def resolve_grading_run(run_dir):
    """Resolve active grading only; callers must keep target generation at root."""
    run = Path(run_dir).resolve()
    if (run / "grading-epoch.json").exists():
        return run
    pointer = _read(run / "active-grading-epoch.json")
    if pointer is None:
        return run
    activation = _inside(run, pointer["activation_record"])
    if sha256(activation) != pointer.get("activation_sha256"):
        raise ValueError("The active grading epoch activation changed")
    record = _read(activation)
    workspace = _inside(run, record["workspace"])
    marker = _read(workspace / "grading-epoch.json")
    if (pointer.get("epoch_id") != record.get("epoch_id") or marker.get("epoch_id") != record.get("epoch_id")
            or marker.get("logical_study_root") != str(run)
            or sha256(run / "output-freeze.json") != record.get("target_output_freeze_sha256")
            or sha256(workspace / "output-freeze.json") != record.get("target_output_freeze_sha256")):
        raise ValueError("A grading epoch does not belong to the same closed target cohort")
    return workspace


def assert_active_grading_epoch(run_dir):
    """Reject writes to a prepared or superseded grading archive."""
    run = Path(run_dir).resolve()
    marker = _read(run / "grading-epoch.json")
    if marker and resolve_grading_run(Path(marker["logical_study_root"])) != run:
        raise ValueError("Only the activated current grading epoch may accept fresh human scores or adjudications")
    return marker


def _verify_workspace(directory):
    completion = _read(directory / "preparation-complete.json")
    if completion is None:
        raise ValueError("Reference correction preparation is incomplete; original records remain preserved")
    if (completion["request_sha256"] != sha256(directory / "request.json")
            or completion["workspace_base_freeze_sha256"] != sha256(directory / "workspace-base-freeze.json")):
        raise ValueError("A reference correction preparation seal changed")
    for relative, expected in _read(directory / "workspace-base-freeze.json")["files"].items():
        path = _inside(directory / "workspace", relative)
        if not path.is_file() or sha256(path) != expected:
            raise ValueError("A copied target, source or proposed reference changed in its grading epoch")


def _target_inventory(run):
    from .results import verify_output_freeze
    freeze = verify_output_freeze(run)
    files = dict(freeze["files"])
    files["output-freeze.json"] = sha256(run / "output-freeze.json")
    for relative in list(files):
        if Path(relative).name == "candidate-manifest.json":
            for name, expected in _read(_inside(run, relative))["files"].items():
                path = _inside(run, name)
                if sha256(path) != expected:
                    raise ValueError("A frozen native target artifact changed before reference correction")
                files[name] = expected
    return files


def _grading_configuration(run):
    """Keep the applicable anti-downgrade contract and supplemental rules."""
    run = Path(run)
    names = {"grading-contract.json"}
    names.update(p.relative_to(run).as_posix() for p in run.glob("evaluation-rules*") if p.is_file())
    return sorted(name for name in names if (run / name).is_file())


def _protected_inventory(parent):
    files = _target_inventory(parent)
    for folder in ("references", "approvals", "grades", "cases", "review/adjudications"):
        for path in sorted((parent / folder).rglob("*")):
            if path.is_file():
                files[path.relative_to(parent).as_posix()] = sha256(path)
    for name in ("references.json", "reference-freeze.json", "scores.json", "selection.json", "schedule.json", "human-roster.json"):
        if (parent / name).exists():
            files[name] = sha256(parent / name)
    for name in _grading_configuration(parent):
        files[name] = sha256(parent / name)
    # Timed submissions are immutable. Their manifest may append later first-read
    # submissions; an immutable snapshot of that earlier manifest is retained.
    for path in sorted((parent / "review/submissions").glob("*.json")):
        files[path.relative_to(parent).as_posix()] = sha256(path)
    return files


def _verify_protected(request):
    parent = Path(request["parent_grading_run"])
    for relative, expected in request["preserved_parent_files"].items():
        path = _inside(parent, relative)
        if not path.is_file() or sha256(path) != expected:
            raise ValueError("Original reference, score, source or target bytes changed after correction preparation: " + relative)


def _correction(root, correction_id):
    directory = root / "corrigenda" / _safe_name(correction_id)
    request = _read(directory / "request.json")
    if request is None or request.get("corrigendum_id") != correction_id:
        raise ValueError("Unknown prepared reference correction")
    return directory, request


def _copy_confirmations(parent, workspace, affected_case):
    original = _read(parent / "approvals/import-manifest.json", {"records": []})
    kept = []
    for entry in original["records"]:
        path = _inside(parent, entry["path"])
        if sha256(path) != entry["sha256"] or entry.get("import_source") != "human_user_submission":
            raise ValueError("An inherited human reference confirmation changed")
        if entry.get("case_id") != affected_case:
            _copy_file(path, _inside(workspace, entry["path"]))
            kept.append(entry)
    write_json(workspace / "approvals/import-manifest.json", {"schema_version": SCHEMA, "records": kept}, immutable=True)


def sync_timed_submissions(run_dir, correction_id=None):
    """Append original first-read records; never rerun or modify practical reviews."""
    root = _root(run_dir)
    if correction_id is None:
        workspace = resolve_grading_run(root)
        if workspace == root:
            return {"copied_submissions": 0, "new_timed_reviews": 0}
    else:
        directory, request = _correction(root, correction_id)
        workspace = directory / "workspace"
    original = _read(root / "review/import-manifest.json", {"records": []})
    current_path = workspace / "review/import-manifest.json"
    current = _read(current_path, {"records": []})
    people = {p["reviewer_id"]: p for p in _read(root / "human-roster.json")["reviewers"]}
    existing = {r["assignment_id"]: r for r in current["records"]}
    added = 0
    for entry in original["records"]:
        path = _inside(root, entry["path"])
        record = _read(path)
        person = people.get(entry.get("reviewer_id"), {})
        if (not path.is_relative_to((root / "review/submissions").resolve()) or sha256(path) != entry.get("sha256")
                or entry.get("import_source") != "human_user_submission" or person.get("human") is not True
                or person.get("role") != "timed_reviewer" or record.get("reviewer_id") != entry.get("reviewer_id")
                or record.get("assignment_id") != entry.get("assignment_id")):
            raise ValueError("A shared timed-review record lacks unchanged original human evidence")
        prior = existing.get(entry["assignment_id"])
        if prior and prior != entry:
            raise ValueError("A practical review cannot be replaced or repeated in another grading epoch")
        _copy_file(path, _inside(workspace, entry["path"]))
        if not prior:
            current["records"].append(entry)
            added += 1
    write_json(current_path, current)
    return {"copied_submissions": added, "shared_original_submissions": len(current["records"]), "new_timed_reviews": 0}


def prepare_corrigendum(run_dir, *, case_id, new_reference_path, reason):
    from .assessment import validate_reference_evidence, verify_human_reference_freeze
    root = _root(run_dir)
    parent = resolve_grading_run(root)
    case_id = _safe_name(case_id)
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("A source-grounded reference correction reason is required")
    targets = _target_inventory(parent)
    verify_human_reference_freeze(parent)
    selection = _read(parent / "selection.json")
    cases = selection["selected"] + selection.get("reserves", [])
    matched = [c for c in cases if c["case_id"] == case_id]
    if len(matched) != 1:
        raise ValueError("A correction must identify one frozen case or reserve")
    old_path, new_path = parent / "references" / (case_id + ".json"), Path(new_reference_path)
    proposed = validate_reference_evidence(parent, _read(new_path))
    if proposed.get("case_id") != case_id or proposed.get("source_sha256") != matched[0]["source_sha256"]:
        raise ValueError("A reference correction cannot change the frozen case or source identity")
    old_hash, new_hash = sha256(old_path), sha256(new_path)
    if old_hash == new_hash:
        raise ValueError("A reference correction requires a different reference version")
    identity = {"case_id": case_id, "reason": reason.strip(), "old_reference_sha256": old_hash,
                "new_reference_sha256": new_hash, "parent_grading_run": str(parent),
                "target_output_freeze_sha256": sha256(parent / "output-freeze.json")}
    correction_id = "corr-" + canonical_hash(identity)[:20]
    directory = root / "corrigenda" / correction_id
    if (directory / "request.json").exists():
        request = _read(directory / "request.json")
        _verify_protected(request)
        _verify_workspace(directory)
        return request
    directory.mkdir(parents=True, exist_ok=False)
    workspace = directory / "workspace"
    workspace.mkdir()
    protected = _protected_inventory(parent)
    for relative in targets:
        _copy_file(_inside(parent, relative), _inside(workspace, relative))
    for folder in ("cases", "references", "mailbox"):
        for path in sorted((parent / folder).rglob("*")):
            if path.is_file() and not (folder == "references" and path == old_path):
                _copy_file(path, _inside(workspace, path.relative_to(parent).as_posix()))
    _copy_file(new_path, workspace / "references" / (case_id + ".json"))
    _copy_file(new_path, directory / "new-reference.json")
    for relative in ("selection.json", "schedule.json", "protocol.json", "rubric.md", "protocol-freeze.json", "human-roster.json",
                     "review/private-scoring-map.json", "review/scoring-assignments.json", "review/private-assignment-map.json", "review/assignments.json", *_grading_configuration(parent)):
        if (parent / relative).exists():
            _copy_file(parent / relative, workspace / relative)
    for relative in ("references.json", "reference-freeze.json", "scores.json", "grades/import-manifest.json", "review/adjudications/import-manifest.json", "review/import-manifest.json"):
        if (parent / relative).exists():
            _copy_file(parent / relative, directory / "history" / relative)
    _copy_confirmations(parent, workspace, case_id)
    write_json(workspace / "grades/import-manifest.json", {"records": []}, immutable=True)
    write_json(workspace / "review/adjudications/import-manifest.json", {"records": []}, immutable=True)
    epoch_id = correction_id
    request = {"schema_version": SCHEMA, "corrigendum_id": correction_id, "epoch_id": epoch_id,
               **identity, "source_sha256": matched[0]["source_sha256"], "created_at": utc_now(),
               "workspace": workspace.relative_to(root).as_posix(), "logical_study_root": str(root),
               "preserved_parent_files": protected, "regrading_results": 264,
               "state": "prepared_pending_two_actual_human_confirmations", "target_generation": "closed",
               "timed_review_policy": "Original first-read submissions are shared unchanged; quality adjudication resets for every assignment. No new practical timed review is requested."}
    write_json(directory / "request.json", request, immutable=True)
    write_json(workspace / "grading-epoch.json", {k: request[k] for k in ("schema_version", "corrigendum_id", "epoch_id", "logical_study_root", "parent_grading_run", "created_at", "target_output_freeze_sha256", "regrading_results", "target_generation", "timed_review_policy")}, immutable=True)
    sync_timed_submissions(root, correction_id)
    frozen_files = {}
    for path in sorted(workspace.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(workspace).as_posix()
        if (relative.startswith(("approvals/", "grades/", "review/submissions/", "review/adjudications/"))
                or relative == "review/import-manifest.json"):
            continue
        frozen_files[relative] = sha256(path)
    write_json(directory / "workspace-base-freeze.json", {"schema_version": SCHEMA, "files": frozen_files}, immutable=True)
    write_json(directory / "preparation-complete.json", {"request_sha256": sha256(directory / "request.json"),
               "workspace_base_freeze_sha256": sha256(directory / "workspace-base-freeze.json")}, immutable=True)
    _verify_protected(request)
    return request


def import_corrigendum_confirmation(run_dir, correction_id, submission_path):
    from .assessment import import_human_attestation
    root = _root(run_dir)
    directory, request = _correction(root, correction_id)
    _verify_protected(request)
    _verify_workspace(directory)
    submission = _read(submission_path)
    if (submission.get("case_id") != request["case_id"] or submission.get("reference_sha256") != request["new_reference_sha256"]
            or submission.get("source_sha256") != request["source_sha256"]):
        raise ValueError("The correction confirmation must bind the affected case and exact new source-reference version")
    return import_human_attestation(directory / "workspace", submission_path)


def activate_corrigendum(run_dir, correction_id):
    from .assessment import finalize_human_references, verify_human_reference_freeze
    from .results import aggregate_scores, verify_output_freeze
    root = _root(run_dir)
    directory, request = _correction(root, correction_id)
    workspace = directory / "workspace"
    _verify_protected(request)
    _verify_workspace(directory)
    if sha256(directory / "new-reference.json") != request["new_reference_sha256"] or sha256(workspace / "references" / (request["case_id"] + ".json")) != request["new_reference_sha256"]:
        raise ValueError("The proposed corrected reference changed before human-confirmed activation")
    active = resolve_grading_run(root)
    if active == workspace:
        return _read(directory / "activation.json")
    if active != Path(request["parent_grading_run"]):
        raise ValueError("The reference correction is stale; its parent is no longer the current grading epoch")
    verify_output_freeze(workspace)
    if sha256(workspace / "output-freeze.json") != sha256(root / "output-freeze.json"):
        raise ValueError("A reference correction cannot replace or regenerate target outputs")
    selection = _read(workspace / "selection.json")
    finalize_human_references(workspace, selection["selected"] + selection.get("reserves", []))
    verify_human_reference_freeze(workspace)
    sync_timed_submissions(root, correction_id)
    summary = aggregate_scores(workspace)
    if summary["planned_results"] != 264 or summary["complete"] or any("satisfies_reference" in group for group in summary["groups"].values()):
        raise ValueError("A corrected grading epoch must begin with all 264 results pending fresh adjudication")
    activation = {"schema_version": SCHEMA, "epoch_id": request["epoch_id"], "corrigendum_id": correction_id,
                  "case_id": request["case_id"], "reason": request["reason"], "old_reference_sha256": request["old_reference_sha256"],
                  "new_reference_sha256": request["new_reference_sha256"], "source_sha256": request["source_sha256"],
                  "parent_grading_run": request["parent_grading_run"], "workspace": request["workspace"],
                  "target_output_freeze_sha256": request["target_output_freeze_sha256"],
                  "reference_freeze_sha256": sha256(workspace / "reference-freeze.json"), "activated_at": utc_now(),
                  "grading_state": "all_264_pending_uniform_regrading", "new_target_requests": 0, "new_timed_reviews": 0}
    write_json(directory / "activation.json", activation, immutable=True)
    pointer = {"schema_version": SCHEMA, "epoch_id": request["epoch_id"],
               "activation_record": (directory / "activation.json").relative_to(root).as_posix(),
               "activation_sha256": sha256(directory / "activation.json")}
    write_json(root / "active-grading-epoch.json", pointer)
    _verify_protected(request)
    return activation


def grading_epoch_lineage(run_dir):
    root = _root(run_dir)
    current = resolve_grading_run(root)
    closed = (root / "output-freeze.json").is_file()
    runs, seen = [], set()
    cursor = current
    while cursor != root:
        if cursor in seen:
            raise ValueError("Cyclic reference correction grading lineage")
        seen.add(cursor)
        marker = _read(cursor / "grading-epoch.json")
        if marker.get("logical_study_root") != str(root):
            raise ValueError("A grading lineage belongs to another logical study")
        correction_dir, request = _correction(root, marker["corrigendum_id"])
        _verify_protected(request)
        _verify_workspace(correction_dir)
        runs.append({"epoch_id": marker["epoch_id"], "run_dir": str(cursor), "target_generation": "closed"})
        cursor = Path(marker["parent_grading_run"]).resolve()
        if not cursor.is_relative_to(root):
            raise ValueError("A grading lineage escaped its logical study")
    runs.append({"epoch_id": "original", "run_dir": str(root), "target_generation": "closed" if closed else "not_closed"})
    runs.reverse()
    return {"logical_study_root": str(root), "current_epoch_id": runs[-1]["epoch_id"], "epochs": runs,
            "target_generation": "closed" if closed else "not_closed",
            "target_output_freeze_sha256": sha256(root / "output-freeze.json") if closed else None,
            "target_cost_policy": "Every epoch grades the same target response IDs; never sum duplicated target ledgers across workspaces.",
            "human_cost_policy": "Count newly submitted confirmation/scoring/adjudication work; deduplicate copied human records by exact submitted bytes and identity.",
            "new_target_requests": 0}


def lineage_human_cost(run_dir):
    """Observed incremental human work only; copied confirmations/timing count once."""
    lineage = grading_epoch_lineage(run_dir)
    groups = {"source_reference_work": "approvals/import-manifest.json", "scoring": "grades/import-manifest.json",
              "practical_timed_review": "review/import-manifest.json", "timed_quality_adjudication": "review/adjudications/import-manifest.json"}
    unique = {group: {} for group in groups}
    epochs = []
    for epoch in lineage["epochs"]:
        run = Path(epoch["run_dir"])
        from .metrics import human_cost_summary
        human_cost_summary(run)  # Verify actual roles, bindings and imported hashes first.
        added, copied = {}, {}
        for group, relative in groups.items():
            fresh, repeated = [], 0
            for entry in _read(run / relative, {"records": []})["records"]:
                path = _inside(run, entry["path"])
                if sha256(path) != entry["sha256"] or entry.get("import_source") != "human_user_submission":
                    raise ValueError("A grading lineage human import changed")
                record = _read(path)
                identity = (record.get("reviewer_id"), record.get("attestation_id") or record.get("submission_id") or record.get("assignment_id"), entry["sha256"])
                if identity in unique[group]:
                    repeated += 1
                else:
                    from .metrics import _active_seconds
                    seconds = _active_seconds(record)
                    unique[group][identity] = seconds
                    fresh.append(seconds)
            known = [v for v in fresh if v is not None]
            added[group] = {"new_records": len(fresh), "reported_duration_records": len(known),
                            "unknown_duration_records": len(fresh) - len(known),
                            "observed_active_seconds_subtotal": sum(known) if known else None}
            copied[group] = repeated
        epochs.append({**epoch, "incremental_human_work": added, "copied_records_not_counted_again": copied})
    totals = {}
    for group, values in unique.items():
        known = [v for v in values.values() if v is not None]
        totals[group] = {"unique_records": len(values), "reported_duration_records": len(known),
                         "unknown_duration_records": len(values) - len(known),
                         "observed_active_seconds_subtotal": sum(known) if known else None,
                         "complete_historical_work_time_seconds": None}
    return {**lineage, "epochs": epochs, "unique_observed_human_work": totals, "currency": None,
            "scope_limit": "Submitted active-time subtotals only. Unreported work is unknown; original timed reading is not repeated after a correction.", "model_calls": 0}
