"""Read-only current-selector validation for an unchanged prospective cohort.

Historical source seals retain their original meaning. This helper recomputes
the maintained selector and binds the exact input closure without writing a new
proposal, selecting replacements, changing rules or creating human approval.
"""
from __future__ import annotations

import importlib.metadata
import json
from pathlib import Path
import sys

from . import long_selection
from .protocol import canonical_hash, sha256

SCHEMA = "skillflow-current-source-selection-binding-v1"
ROOT = Path(__file__).resolve().parents[3]
IMPLEMENTATION = ("tools/doe/real_comparison/selection_readiness.py",
                  "tools/doe/real_comparison/long_selection.py",
                  "tools/doe/real_comparison/selection.py",
                  "tools/doe/real_comparison/protocol.py",
                  "src/skillflow/common/source_evidence.py")
IDENTITY_FIELDS = ("canonical_id", "version", "source_sha256", "source_tree_sha256", "bundle_sha256")


def _read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _files(root):
    root = Path(root).resolve()
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError("Current source selection inputs cannot contain symlinks")
        if path.is_file():
            result[path.relative_to(root).as_posix()] = sha256(path)
    return result


def _identities(selection):
    selected, reserves = selection.get("selected", []), selection.get("reserves", [])
    if (len(selected) != 24 or len(reserves) != 6
            or len({item.get("canonical_id") for item in selected + reserves}) != 30):
        raise ValueError("Current source readiness requires the exact 24 selected and six reserve identities")
    rows = []
    for item in selected + reserves:
        if any(not isinstance(item.get(field), str) or not item[field].strip() for field in IDENTITY_FIELDS):
            raise ValueError("Current source readiness requires canonical, version, source, tree and bundle identities")
        rows.append({field: item[field] for field in IDENTITY_FIELDS})
    return rows


def _dependency_snapshot(proposal, corpus):
    freeze = _read(proposal / "rules-freeze.json")
    inputs = {str((proposal / "rules-freeze.json").resolve()): sha256(proposal / "rules-freeze.json")}
    for relative, digest in freeze["files"].items():
        path = (proposal / relative).resolve()
        if not path.is_relative_to(proposal) or sha256(path) != digest:
            raise ValueError("Current source selection frozen input changed or escaped its proposal")
        inputs[str(path)] = digest
    for item in _read(proposal / "rules.json")["evidence_inputs"]:
        path = Path(item["path"]).resolve()
        if not path.is_relative_to(corpus) or sha256(path) != item["sha256"]:
            raise ValueError("Current source selection source-only evidence changed")
        inputs[str(path)] = item["sha256"]
    trees = {str((proposal / "reviews").resolve()): _files(proposal / "reviews"),
             str((proposal / "review-history").resolve()): _files(proposal / "review-history")}
    supersessions = proposal / "review-supersessions.json"
    inputs[str(supersessions.resolve())] = sha256(supersessions) if supersessions.exists() else None
    for candidate in _read(proposal / "candidate-queue.json")["candidates"]:
        source = (corpus / candidate["source_dir"]).resolve()
        view = (corpus / candidate["source_view_path"]).resolve()
        if not source.is_relative_to(corpus) or not view.is_relative_to(corpus):
            raise ValueError("Current source selection candidate source escapes its corpus")
        trees[str(source)] = _files(source)
        inputs[str(view)] = sha256(view)
    return inputs, trees


def _validation_snapshot(proposal, corpus):
    inputs, trees = _dependency_snapshot(proposal, corpus)
    return {"input_files": inputs, "input_trees": trees,
            "implementation_files": {path: sha256(ROOT / path) for path in IMPLEMENTATION},
            "python_version": sys.version,
            "tokenizer_package_version": importlib.metadata.version("tiktoken")}


def inspect_current_selection(proposal_dir, corpus_root, expected_selection):
    """Recompute current proof checks; return a dependency binding, with no writes."""
    proposal, corpus = Path(proposal_dir).resolve(), Path(corpus_root).resolve()
    expected = _read(expected_selection) if isinstance(expected_selection, (str, Path)) else expected_selection
    expected_digest = canonical_hash(expected)
    expected_rows = _identities(expected)
    before = _validation_snapshot(proposal, corpus)
    current = long_selection.select_long_cases(proposal, corpus, write=False)
    after = _validation_snapshot(proposal, corpus)
    expected_after = _read(expected_selection) if isinstance(expected_selection, (str, Path)) else expected_selection
    if before != after or canonical_hash(expected_after) != expected_digest:
        raise ValueError("Current source selection dependencies changed during validation; no readiness binding was created")
    if (current.get("status") != "selection_complete_pending_human_reference"
            or current.get("accepted_count") != 30 or current.get("shortfall") != 0
            or current.get("thresholds_relaxed") is not False or current.get("order_reshuffled") is not False
            or _identities(current) != expected_rows):
        raise ValueError("Current source selection proof is incomplete or differs from the fixed ordered cohort")
    for field in ("rules_sha256", "candidate_queue_sha256"):
        if current.get(field) != expected.get(field) or not current.get(field):
            raise ValueError("Current source selection differs from the frozen rules or queue: " + field)
    return {"schema_version": SCHEMA, "state": "validated_current_selector",
            "proposal_dir": str(proposal), "corpus_root": str(corpus),
            "expected_case_identities": expected_rows, "selection_result_sha256": canonical_hash(current),
            "rules_sha256": current["rules_sha256"], "candidate_queue_sha256": current["candidate_queue_sha256"],
            **before,
            "model_calls": 0, "human_confirmations_created": 0, "source_bytes_modified": False}


def verify_saved_binding(binding, expected_selection):
    """Recheck the complete saved closure without repeating tokenization/proofs."""
    expected = _read(expected_selection) if isinstance(expected_selection, (str, Path)) else expected_selection
    if (binding.get("schema_version") != SCHEMA or binding.get("state") != "validated_current_selector"
            or binding.get("expected_case_identities") != _identities(expected)
            or binding.get("rules_sha256") != expected.get("rules_sha256")
            or binding.get("candidate_queue_sha256") != expected.get("candidate_queue_sha256")
            or set(binding.get("implementation_files", {})) != set(IMPLEMENTATION)):
        raise ValueError("Current source selection binding does not describe the fixed cohort")
    for relative, digest in binding["implementation_files"].items():
        if sha256(ROOT / relative) != digest:
            raise ValueError("Current source selector implementation changed; revalidation is required")
    inputs, trees = _dependency_snapshot(Path(binding["proposal_dir"]), Path(binding["corpus_root"]))
    if inputs != binding.get("input_files") or trees != binding.get("input_trees"):
        raise ValueError("Current source selection dependency closure changed; revalidation is required")
    if sys.version != binding.get("python_version"):
        raise ValueError("Current source selector Python runtime changed; revalidation is required")
    if importlib.metadata.version("tiktoken") != binding["tokenizer_package_version"]:
        raise ValueError("Current source selector tokenizer changed; revalidation is required")
    return binding
