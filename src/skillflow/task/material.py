"""Exact source-only material and a closed, nontextual revision interface."""
from __future__ import annotations

from copy import deepcopy
from pydantic import BaseModel, ConfigDict, Field

from skillflow.common.source_evidence import _checked_source, extract_source_lines, source_lines
from skillflow.propagation.contracts.task import (
    Task, TaskRepairObjection, checked_task, task_source_files,
)

MATERIAL_VERSION = "skillflow-task-material-v3"


class TaskRevision(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    previous_task: Task
    objections: list[TaskRepairObjection] = Field(min_length=1)


def prepare_task_material(source):
    source = _checked_source(deepcopy(source))
    task_source_files(source)
    return {"version": MATERIAL_VERSION, "source": source}


def checked_task_material(material):
    if type(material) is not dict or set(material) != {"version", "source"}:
        raise ValueError("Task material only accepts exact source-only fields")
    prepared = prepare_task_material(material["source"])
    if prepared != material:
        raise ValueError("Task material identity differs")
    return prepared


def validate_revision(revision, material):
    if revision is None:
        return None
    value = revision.model_dump(mode="json") if isinstance(revision, TaskRevision) else revision
    parsed = TaskRevision.model_validate(value)
    files = task_source_files(material["source"])
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
    files = task_source_files(material["source"])
    return {"source_files": [
        {"file": file, "lines": source_lines(text)} for file, text in files.items()]}
