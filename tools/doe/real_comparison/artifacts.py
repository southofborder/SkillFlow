"""Deterministic candidate views and byte seals, without model rewriting."""
from __future__ import annotations

import json
from pathlib import Path

from .protocol import SCHEMA, sha256, write_json


def seal_candidate(run_dir, workflow_id, *, artifact_root=None):
    run = Path(run_dir).resolve()
    workflow = (run / "workflows" / workflow_id).resolve()
    if not workflow.is_relative_to((run / "workflows").resolve()):
        raise ValueError("Candidate workflow path escapes its experiment")
    files = []
    if artifact_root is None:
        answer = workflow / "answer.txt"
        if answer.is_file():
            files.append(answer)
        visible = files[:]
    else:
        native = (run / artifact_root).resolve()
        if not native.is_relative_to(workflow / "attempts"):
            raise ValueError("Native candidate path escapes its workflow attempts")
        # All output files are sealed. Inputs, call recordings and intermediate
        # outputs remain auditable in the archive; the reading view contains
        # original native reports and terminal stage result documents.
        files = sorted(p for p in native.rglob("*") if p.is_file()
                       and p.name != "worker-result.json")
        reports = [p for p in files if p.name == "report.md"
                   and not {"inputs", "calls", "replay"}.intersection(p.relative_to(native).parts)]
        results = [p for p in files if p.suffix == ".json"
                   and p.name not in {"manifest.json", "transport.json", "execution-boundary.json"}
                   and not {"inputs", "calls", "replay"}.intersection(p.relative_to(native).parts)]
        visible = reports + [p for p in results if p not in reports]
    if not files:
        return {"artifact_manifest_sha256": None, "candidate_view_sha256": None}
    for path in files:
        if path.is_symlink() or not path.resolve().is_relative_to(run):
            raise ValueError("A candidate output contains a symlink or external path")
    manifest = {"schema_version": SCHEMA,
                "files": {p.relative_to(run).as_posix(): sha256(p) for p in files},
                "reading_view_files": [p.relative_to(run).as_posix() for p in visible],
                "rendering": "Concatenated original reports and terminal result documents; no semantic edits or model polish.",
                "blinding_limit": "Artifact structure and original native labels may reveal the method."}
    path = workflow / "candidate-manifest.json"
    write_json(path, manifest, immutable=True)
    if artifact_root is None:
        text = visible[0].read_text(encoding="utf-8")
    else:
        text = "\n\n".join("=== " + p.relative_to(native).as_posix() + " ===\n"
                             + p.read_text(encoding="utf-8") for p in visible)
    view = workflow / "candidate-view.txt"
    if view.exists() and view.read_bytes() != text.encode("utf-8"):
        raise ValueError("The sealed candidate reading view changed")
    view.write_bytes(text.encode("utf-8"))
    return {"artifact_manifest_sha256": sha256(path), "candidate_view_sha256": sha256(view)}


def verify_candidate(run_dir, workflow_id, result):
    run = Path(run_dir).resolve()
    workflow = run / "workflows" / workflow_id
    manifest = workflow / "candidate-manifest.json"
    if not result.get("artifact_manifest_sha256") or sha256(manifest) != result["artifact_manifest_sha256"]:
        raise ValueError("The candidate manifest is absent or changed")
    for relative, expected in json.loads(manifest.read_text(encoding="utf-8"))["files"].items():
        path = (run / relative).resolve()
        if not path.is_relative_to(run) or sha256(path) != expected:
            raise ValueError("A sealed candidate artifact changed")
    if sha256(workflow / "candidate-view.txt") != result.get("candidate_view_sha256"):
        raise ValueError("The candidate reading view changed")
    return True
