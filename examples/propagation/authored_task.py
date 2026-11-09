"""Source-only hand-authored baselines for demonstrations, never model results."""
from skillflow.propagation.contracts.task import task_source_files, validate_task_candidate


def authored_baseline(source, *, purpose, requirements):
    files = task_source_files(source)
    primary = next(iter(files))
    evidence = {"file": primary, "start_line": 1, "end_line": len(files[primary].splitlines()),
                "reason": "Hand-authored teaching claim with source evidence, not a model evaluation."}
    candidate = {"purpose": {"text": purpose, "evidences": [evidence]},
        "requirements": [{"id": f"R{number}", "text": text, "evidences": [evidence]}
                         for number, text in enumerate(requirements, 1)],
        "issues": []}
    return validate_task_candidate(candidate, source_files=files, source_sha256=source["source_sha256"])


def unseeded_realizations(task):
    return [{"requirement_id": row.id, "status": "unmapped", "bindings": [], "gaps": [
        {"reason": "This example checks propagation; it does not declare a demand seed for this obligation.", "evidences": [e.model_dump(mode="json") for e in row.evidences]}]}
        for row in task.requirements]
