"""Source-only hand-authored baselines for demonstrations, never model results."""
from skillflow.propagation.contracts.task import task_source_files, validate_task_candidate


def authored_baseline(source, *, purpose, requirements):
    files = task_source_files(source)
    primary = next(iter(files))
    evidence = {"file": primary, "start_line": 1, "end_line": len(files[primary].splitlines()),
                "reason": "人工教学声明及原文定位；不是模型语义实测。"}
    candidate = {"purpose": {"text": purpose, "evidences": [evidence]},
        "requirements": [{"id": f"R{number}", "text": text, "evidences": [evidence]}
                         for number, text in enumerate(requirements, 1)],
        "source_accounting": [{"file": name, "start_line": 1, "end_line": len(text.splitlines()),
            "disposition": "requirement", "requirement_ids": [f"R{i}" for i in range(1, len(requirements)+1)],
            "issue_ids": [], "reason": "人工教学样例的完整原文处置登记。"}
            for name, text in files.items() if text.strip()], "issues": []}
    return validate_task_candidate(candidate, source_files=files, source_sha256=source["source_sha256"], basis="declared_skill")


def unseeded_realizations(task):
    return [{"requirement_id": row.id, "status": "unmapped", "bindings": [], "gaps": [
        {"reason": "本示例验证传播关系；未声明该义务的需求起点。", "evidences": [e.model_dump(mode="json") for e in row.evidences]}]}
        for row in task.requirements]
