"""Light scheduler summaries reference the one verified annotation owner.

References are relative to the case directory identified by the scheduler
manifest, including when the summary is embedded in a batch or replay file.
"""
from copy import deepcopy
from pathlib import Path

from skillflow.common.recording import sha_file

from skillflow.common.upstream import make_run_reference, resolve_run_reference
from skillflow.propagation.annotation.loading import load_annotation_attempt


FIELDS = ("status", "reason", "counts", "identity", "schema_version", "profile_schema_version",
          "source_sha256", "graph_sha256", "error_kind", "accepted_call")


def support_identity():
    directory = Path(__file__).resolve().parent
    return {name: sha_file(directory / name) for name in ("summaries.py", "pinned_inputs.py", "task_runs.py")}


def annotation_summary(value, *, owner, annotation_run):
    reference = make_run_reference(owner, annotation_run) if (annotation_run / "manifest.json").is_file() else None
    return {**{key: deepcopy(value[key]) for key in FIELDS if key in value},
            "run": reference,
            "ir_semantics_count": len(value.get("ir_semantics", {})),
            "partial_order_ir_count": sum(spec.get("order") == "partial" for spec in value.get("ir_semantics", {}).values())}


def restore_annotation(value, *, owner):
    if value.get("run") is None:
        return {**deepcopy(value), "ir_semantics": {}, "locations": {}, "sink_boundaries": [],
                "task_ref": None, "realizations": [], "demands": [], "expressions": []}
    directory = resolve_run_reference(owner, value["run"])
    result = load_annotation_attempt(directory)["result"]
    if annotation_summary(result, owner=owner, annotation_run=directory) != value:
        raise ValueError("Scheduler annotation summary differs from its verified owner")
    return result


def case_summary(value, *, owner, annotation_run):
    return {**deepcopy(value), "annotation": annotation_summary(value["annotation"], owner=owner, annotation_run=annotation_run)}
