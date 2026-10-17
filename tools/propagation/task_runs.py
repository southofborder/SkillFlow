"""Explicit independent Task owners for historical experiment drivers.

These drivers never invent a Task or reinterpret an old accepted annotation.
Use the main skillflow pipeline when extraction and review should be orchestrated.
"""
from pathlib import Path

from skillflow.common.recording import read_json
from skillflow.common.upstream import checked_run_path, make_run_reference, resolve_run_reference
from skillflow.task.runner import load_task_run


def _checked_baseline(path, case):
    task = load_task_run(path)["task"]
    if task["basis"] != "declared_skill":
        raise ValueError("These corpus drivers require a declared-Skill Task baseline; use the main analysis pipeline for an independent user task")
    expected = case.get("source_sha256")
    address = case.get("package_path", case.get("input"))
    if expected is None and address is not None:
        from skillflow.common.inputs.snapshot import inspect_input
        from skillflow.common.paths import resolve_material_path
        expected = inspect_input(resolve_material_path(address))[1]["source_sha256"]
    if expected is not None and task["source_sha256"] != expected:
        raise ValueError("Independent Task source differs from case " + case["case_id"])
    return task


def read_task_runs(path):
    if path is None:
        return None
    path = checked_run_path(path)
    value = read_json(path)
    if type(value) is not dict or any(type(k) is not str or type(v) is not str for k, v in value.items()):
        raise ValueError("--task-runs-json must map case IDs to completed independent Task run paths")
    return {key: str(checked_run_path(path.parent / address)) for key, address in value.items()}


def bind_task_runs(directory, cases, supplied=None):
    """Bind exact completed Task owners before creating any model client."""
    directory = Path(directory).resolve()
    expected = {case["case_id"] for case in cases}
    path = directory / "manifest.json"
    if supplied is None:
        saved = read_json(path) if path.is_file() else {}
        references = saved.get("task_runs")
        if type(references) is not dict:
            raise ValueError("Independent Task runs are required: supply --task-runs-json (case ID -> completed source-only Task run), or use skillflow pipeline for new extraction and review. Historical annotation runs are not upgraded.")
        if set(references) != expected:
            raise ValueError("Independent Task run case inventory differs")
        for case in cases:
            _checked_baseline(resolve_run_reference(directory, references[case["case_id"]]), case)
        return references
    if type(supplied) is not dict or set(supplied) != expected:
        raise ValueError("Supply exactly one independent Task run for every case ID")
    references = {}
    indexed = {case["case_id"]: case for case in cases}
    for identity in sorted(expected):
        _checked_baseline(supplied[identity], indexed[identity])
        references[identity] = make_run_reference(directory, supplied[identity])
    return references


def task_owner(directory, manifest, case_id):
    return resolve_run_reference(directory, manifest["task_runs"][case_id])
