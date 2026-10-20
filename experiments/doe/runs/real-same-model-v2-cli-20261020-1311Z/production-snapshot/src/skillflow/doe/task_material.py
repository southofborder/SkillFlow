"""Prepare exact task evidence and graph correspondences without model calls."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from skillflow.common.source_evidence import _json_object, _require_json, source_lines, _checked_source
from skillflow.propagation.contracts.task import (
    CandidateTask, Task, task_source_files, validate_task_candidate, checked_task,
)
from skillflow.propagation.loading import PropagationMaterials
from skillflow.propagation.contracts.references import resolve_cfg_target, target_key


@dataclass(frozen=True)
class TaskReview:
    """Isolated review objects; no claim of semantic support or completeness."""

    task: Task
    files: dict[str, str]
    targets: dict[str, dict[str, Any]]
    cfg: dict[str, Any]
    boundaries: dict[str, Any]
    realizations: tuple = ()

    def index_dict(self) -> dict[str, Any]:
        return {
            "files": [{"file": name,
                       "original_path": name[len("skill/"):] if name.startswith("skill/") else None,
                       "origin": "skill" if name.startswith("skill/") else "user_request",
                       "line_count": len(source_lines(text))}
                      for name, text in sorted(self.files.items())],
            "targets": deepcopy(self.targets),
        }


def _read_object(value: Any) -> dict[str, Any]:
    if isinstance(value, Path):
        value = value.read_bytes().decode("utf-8")
    elif isinstance(value, str) and not value.lstrip().startswith("{"):
        value = Path(value).read_bytes().decode("utf-8")
    if isinstance(value, dict):
        _require_json(value, "")
    return _json_object(value)


def prepare_task_review(facts, task_annotation) -> TaskReview:
    """Inspect Task claims against the same verified propagation components."""
    if not isinstance(facts, PropagationMaterials):
        raise TypeError("Task review requires verified propagation materials")
    candidate = task_annotation if isinstance(task_annotation, CandidateTask) else _read_object(task_annotation)
    user_request = facts.material["user_request"]
    files = task_source_files(_checked_source(facts.source), user_request=user_request)
    if isinstance(task_annotation, Task) or isinstance(candidate, dict) and "task_sha256" in candidate:
        task = checked_task(task_annotation, source_files=files,
                            source_sha256=facts.source["source_sha256"])
    else:
        task = validate_task_candidate(candidate, source_files=files,
            basis="user_request" if user_request is not None else "declared_skill",
            source_sha256=facts.source["source_sha256"])
    realizations = tuple(deepcopy(facts.annotation["compiled_annotation"]["realizations"]))
    targets = {target_key(binding["target"]): resolve_cfg_target(binding["target"], facts.cfg)
               for realization in realizations for binding in realization["bindings"]}
    return TaskReview(task=task, files=deepcopy(files), targets=deepcopy(targets),
                      cfg=deepcopy(facts.cfg), boundaries=deepcopy(facts.source_metadata), realizations=realizations)
