"""Exact source-only material and a closed, nontextual revision interface."""
from __future__ import annotations

from copy import deepcopy
from pydantic import BaseModel, ConfigDict, Field

from skillflow.common.source_evidence import _checked_source, extract_source_lines, source_lines
from skillflow.propagation.contracts.task import (
    Task, TaskRepairObjection, checked_task, task_source_files,
)

MATERIAL_VERSION = "skillflow-task-material-v1"


class TaskRevision(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    previous_task: Task
    objections: list[TaskRepairObjection] = Field(min_length=1)


def prepare_task_material(source, *, user_request=None):
    source = _checked_source(deepcopy(source))
    files = task_source_files(source, user_request=user_request)
    return {"version": MATERIAL_VERSION, "source": source, "user_request": user_request,
            "basis": "user_request" if "task/user-request.txt" in files else "declared_skill"}


def checked_task_material(material):
    if type(material) is not dict or set(material) != {"version", "source", "user_request", "basis"}:
        raise ValueError("Task material only accepts exact source-only fields")
    prepared = prepare_task_material(material["source"], user_request=material["user_request"])
    if prepared != material:
        raise ValueError("Task material identity or purpose basis differs")
    return prepared


def validate_revision(revision, material):
    if revision is None:
        return None
    value = revision.model_dump(mode="json") if isinstance(revision, TaskRevision) else revision
    parsed = TaskRevision.model_validate(value)
    files = task_source_files(material["source"], user_request=material["user_request"])
    old = checked_task(parsed.previous_task, source_files=files,
                       source_sha256=material["source"]["source_sha256"])
    ids = {x.id for x in old.requirements}
    for objection in parsed.objections:
        if not set(objection.requirement_ids) <= ids:
            raise ValueError("Task revision refers to unknown requirement")
        for span in objection.source_spans:
            if span.file not in files:
                raise ValueError("Task revision refers to unknown source")
            extract_source_lines(files[span.file], span.start_line, span.end_line)
    return parsed.model_dump(mode="json")


def model_task_material(material):
    material = checked_task_material(material)
    files = task_source_files(material["source"], user_request=material["user_request"])
    return {"basis": material["basis"], "source_files": [
        {"file": file, "lines": source_lines(text)} for file, text in files.items()]}
