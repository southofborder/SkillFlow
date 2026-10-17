"""Explicit test-only reconstruction; historical receipts are never rewritten."""
import json
from pathlib import Path
from skillflow.propagation.material import prepare_material
from skillflow.propagation.contracts.task import validate_task_candidate, task_source_files, task_reference
from skillflow.common.source_evidence import source_lines
from copy import deepcopy
from skillflow.propagation.annotation.compiler import compile_response
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.solver import propagate
from skillflow.propagation.loading import materials_from_result
from tests.doe.components import mutable_components
from tests.doe.fixtures.rebuild_field_fixtures import rebuild_raw_annotation


def source_task(source, candidate=None, *, user_request=None):
    """Explicit test baseline, never a model response or extraction algorithm."""
    files = task_source_files(source, user_request=user_request)
    if candidate is None:
        file = "task/user-request.txt" if user_request is not None else next(iter(files))
        number = next(i for i, line in enumerate(source_lines(files[file]), 1) if line.strip())
        evidence = {"file": file, "start_line": number, "end_line": number,
                    "reason": "独立算法测试显式给定的来源；不主张语义等价或完备。"}
        candidate = {"purpose": {"text": "保留算法测试指定的结果。", "evidences": [evidence]},
            "requirements": [{"id": "R", "text": "保留算法测试显式指定的结果。", "evidences": [evidence]}],
            "source_accounting": [{"file": name, "start_line": i, "end_line": i,
                "disposition": "requirement" if name == file and i == number else "supporting_context",
                "requirement_ids": ["R"] if name == file and i == number else [], "issue_ids": [],
                "reason": "离线算法样例物理行登记；不是源文语义评测基准。"}
                for name, text in files.items() for i, line in enumerate(source_lines(text), 1) if line.strip()],
            "issues": []}
    return validate_task_candidate(candidate, source_files=files,
        basis="user_request" if user_request is not None else "declared_skill",
        source_sha256=source["source_sha256"])


def annotation_fixture(directory, *, task=None):
    directory = Path(directory)
    old = json.loads((directory / "audit/raw-annotation.json").read_bytes())
    old_material = json.loads((directory / "inputs/material.json").read_bytes())
    from tests.doe.fixtures.task_examples import authored_candidate, authored_bindings
    case = directory.parent.name
    task = source_task(old_material["source"], task or authored_candidate(case, old_material["cfg"]))
    raw = rebuild_raw_annotation(old, old_material)
    raw["task_revision_id"] = task.task_sha256
    bindings = authored_bindings(case, old_material["cfg"])
    raw["realizations"] = [{"requirement_id": r.id, "status": "retained_only",
        "bindings": bindings[r.id], "gaps": [{"reason": "历史离线样例尚未编写正向保持目标。", "evidences": [e.model_dump(mode="json") for e in r.evidences]}]}
        for r in task.requirements]
    return raw


def fact_fixture(path):
    path = Path(path)
    upstream = path.parent.parent / "annotation"
    old = json.loads((upstream / "inputs/material.json").read_bytes())
    from tests.doe.fixtures.task_examples import authored_candidate
    task = source_task(old["source"], authored_candidate(path.parent.parent.name, old["cfg"]))
    material = prepare_material(old["source"], old["cfg"], task_baseline=task)
    raw = annotation_fixture(upstream)
    checked, compiled, mapping = compile_response(raw, material)
    solved = propagate(material["cfg"], to_payload(compiled))
    return mutable_components(materials_from_result(solved, material=material, raw_annotation=checked,
        compiled_annotation=compiled, mapping=mapping))
