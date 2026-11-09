"""Versioned source-only reference workspaces; no model or target dispatch route.

Human imports require explicit files supplied by actual people. A JSON assertion
does not independently establish personhood or semantic completeness.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
import json
from pathlib import Path

from . import assessment
from .long_preparation import COPIED_RULES, verify_preparation
from .protocol import canonical_hash, sha256, utc_now, write_json
from .selection import verify_reference_packets
from .selection_readiness import inspect_current_selection, verify_saved_binding

SCHEMA = "skillflow-source-reference-epoch-v1"
SOURCE_ONLY_CONFIRMATION = (
    "I personally checked this exact source reference against the complete frozen source and "
    "declared-purpose rules, without target method outputs or registry safety summaries."
)
FORBIDDEN = ("protocol.json", "cli-protocol.json", "protocol-freeze.json", "formal-protocol.json",
             "formal-gate.json", "gate.json", "calibration.json", "calibration-plan.json",
             "output-freeze.json", "materials-freeze.json")
INHERITED = ("selection.json", "source-selection.json", "source-selection-seal.json",
             "human-roster.template.json", *COPIED_RULES)


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _inside(root, relative):
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError("Reference epoch members require relative workspace paths")
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Reference epoch path escapes its workspace")
    return path


def _copy(source, target):
    raw = source.read_bytes()
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.read_bytes() != raw:
        raise ValueError("An immutable reference-epoch member differs: " + str(target))
    if not target.exists():
        target.write_bytes(raw)


def _no_dispatch(epoch):
    if any((epoch / name).exists() for name in FORBIDDEN):
        raise ValueError("A source-only reference epoch cannot contain a protocol or execution gate")
    if any(p.is_file() for folder in ("mailbox", "workflows", "authorization") for p in (epoch / folder).rglob("*")):
        raise ValueError("A source-only reference epoch cannot contain target requests or outputs")


def _identity(reference, case):
    for field, wanted in (("case_id", case["case_id"]), ("canonical_id", case["canonical_id"]),
                          ("source_sha256", case["source_sha256"]),
                          ("source_bundle_sha256", case["bundle_sha256"])):
        if reference.get(field) != wanted:
            raise ValueError("Reference changes the fixed case/source/bundle identity: " + field)


def _pending(reference):
    slots = reference.get("human_verifications", [])
    if (reference.get("human_verified") is not False or not isinstance(slots, list)
            or any(not isinstance(slot, dict) or slot.get("status") != "pending"
                   or slot.get("reviewer_id") is not None or slot.get("confirmed_at") is not None
                   or slot.get("reference_sha256") is not None
                   or slot.get("source_only_attestation") not in (None, False)
                   or slot.get("per_item_checks") not in (None, []) for slot in slots)
            or reference.get("state") in {"approved", "human_verified", "verified"}
            or reference.get("reference_status") in {"approved", "human_verified", "verified"}):
        raise ValueError("A source-draft revision cannot manufacture human approval")


def _history_files(epoch, records, label, checked=None):
    for item in records:
        if checked is not None and item["path"] in checked:
            if checked[item["path"]] != item["sha256"]:
                raise ValueError(label + " has inconsistent preserved hashes: " + item["path"])
            continue
        path = _inside(epoch, item["path"])
        if not path.is_file() or sha256(path) != item["sha256"]:
            raise ValueError(label + " changed: " + item["path"])
        if checked is not None:
            checked[item["path"]] = item["sha256"]


def _preserve_manifest(epoch, kind, value):
    """Retain every exact manifest version, including before invalidation."""
    relative = f"import-manifest-history/{kind}/{canonical_hash(value)}.json"
    write_json(epoch / relative, value, immutable=True)
    return {"path": relative, "sha256": sha256(epoch / relative)}


def _import_history(epoch):
    path = epoch / "human-import-history.json"
    return read(path) if path.exists() else {"schema_version": SCHEMA, "events": []}


def _record_import_event(epoch, *, kind, before, after, submission=None):
    history = _import_history(epoch)
    history["events"].append({"sequence": len(history["events"]), "kind": kind,
                              "before": _preserve_manifest(epoch, "before", before),
                              "after": _preserve_manifest(epoch, "after", after),
                              "submission": submission, "recorded_at": utc_now()})
    write_json(epoch / "human-import-history.json", history)


def _verify_import_history(epoch):
    history = _import_history(epoch)
    current = {"records": []}
    checked = {}
    for sequence, event in enumerate(history["events"]):
        if event.get("sequence") != sequence or event.get("kind") not in {"confirmation_import", "case_invalidation"}:
            raise ValueError("Human import history is incomplete")
        _history_files(epoch, [event["before"], event["after"]], "Preserved human import manifest", checked)
        before, after = read(epoch / event["before"]["path"]), read(epoch / event["after"]["path"])
        if before != current:
            raise ValueError("Human import manifests no longer form the preserved event history")
        current = after
        _history_files(epoch, before["records"] + after["records"], "Preserved human confirmation", checked)
        if event.get("submission"):
            _history_files(epoch, [event["submission"]], "Original human submission", checked)
    if _active_imports(epoch) != current:
        raise ValueError("Active human imports changed outside the versioned importer")
    provenance_path = epoch / "human-import-provenance.json"
    provenance = read(provenance_path).get("records", []) if provenance_path.exists() else []
    imported = [event["submission"] for event in history["events"] if event["kind"] == "confirmation_import"]
    if len(imported) != len(provenance):
        raise ValueError("Human import provenance no longer covers every original submission")
    for submission, record in zip(imported, provenance):
        if (submission["path"] != record["preserved_path"]
                or submission["sha256"] != record["actual_submission_sha256"]):
            raise ValueError("Original human submission provenance changed")
        _history_files(epoch, [{"path": record["imported_path"], "sha256": record["imported_sha256"]}],
                       "Preserved imported human confirmation", checked)
    expected = {
        "human-submission-history": {item["path"] for item in imported},
        "approvals/submissions": {item["imported_path"] for item in provenance},
        "import-manifest-history": {event[side]["path"] for event in history["events"] for side in ("before", "after")},
    }
    for folder, paths in expected.items():
        actual = {path.relative_to(epoch).as_posix() for path in (epoch / folder).rglob("*") if path.is_file()}
        if actual != paths:
            raise ValueError("Human submission/import-manifest history has missing or unindexed preserved members")


def _cases(epoch):
    selection = read(epoch / "selection.json")
    selected, reserves = selection.get("selected", []), selection.get("reserves", [])
    cases = selected + reserves
    if (len(selected) != 24 or len(reserves) != 6 or len({c["canonical_id"] for c in cases}) != 30
            or [c["case_id"] for c in cases] != [f"real-{i:03d}" for i in range(1, 31)]):
        raise ValueError("A reference epoch requires the exact ordered 24 selected and six reserve identities")
    for case in cases:
        manifest = read(epoch / "cases" / case["case_id"] / "source-manifest.json")
        if (manifest.get("case_id") != case["case_id"]
                or manifest.get("source_sha256") != case["source_sha256"]
                or manifest.get("canonical_id") != case["canonical_id"]
                or manifest.get("source_bundle_sha256") != case["bundle_sha256"]
                or manifest.get("source_tree_sha256") != case["source_tree_sha256"]
                or sha256(epoch / "cases" / case["case_id"] / "source-bundle.txt") != case["bundle_sha256"]):
            raise ValueError("Reference epoch case/source/bundle identity differs: " + case["case_id"])
    return cases


def _integrity(epoch):
    epoch = Path(epoch).resolve()
    _no_dispatch(epoch)
    origin = read(epoch / "reference-epoch-origin.json")
    if origin.get("schema_version") != SCHEMA or origin.get("execution_enabled") is not False:
        raise ValueError("Reference epoch lacks its source-only origin contract")
    for relative, digest in origin["protected_files"].items():
        path = _inside(epoch, relative)
        if not path.is_file() or sha256(path) != digest:
            raise ValueError("Inherited reference-epoch bytes changed: " + relative)
    parent = Path(origin["parent_preparation"])
    if sha256(parent / "preparation-freeze.json") != origin["parent_preparation_freeze_sha256"]:
        raise ValueError("Parent preparation identity changed")
    verification = verify_preparation(parent, origin["corpus_root"])
    if verification["status"] != "passed":
        raise ValueError("Parent source preparation no longer verifies")
    cases = _cases(epoch)
    packets = verify_reference_packets(origin["corpus_root"], epoch / "cases")
    if not packets["verified"] or packets["packet_count"] != 30:
        raise ValueError("Reference epoch requires 30 verified complete source packets")
    revisions = read(epoch / "reference-revisions.json")
    if set(revisions["cases"]) != {c["case_id"] for c in cases}:
        raise ValueError("Reference revision index must cover all 30 fixed cases")
    indexed_history = {item["path"] for entry in revisions["cases"].values() for item in entry["history"]}
    actual_history = {path.relative_to(epoch).as_posix() for path in (epoch / "reference-history").rglob("*") if path.is_file()}
    if indexed_history != actual_history:
        raise ValueError("Reference revision history has missing or unindexed preserved members")
    for case in cases:
        entry = revisions["cases"][case["case_id"]]
        history = entry["history"]
        if (not history or entry["active_version"] != history[-1]["version"]
                or entry["active_sha256"] != history[-1]["sha256"]):
            raise ValueError("Active reference revision lacks its exact history binding")
        for index, item in enumerate(history):
            if item["version"] != index or not item.get("reason"):
                raise ValueError("Reference revision history is incomplete")
            path = _inside(epoch, item["path"])
            if not path.is_file() or sha256(path) != item["sha256"]:
                raise ValueError("Preserved reference revision changed")
            _identity(read(path), case)
            _pending(read(path))
            invalidation = item.get("confirmation_invalidation")
            if invalidation:
                for relative, digest in invalidation["preserved_files"].items():
                    _history_files(epoch, [{"path": relative, "sha256": digest}], "Archived confirmation history")
        if sha256(epoch / "references" / (case["case_id"] + ".json")) != entry["active_sha256"]:
            raise ValueError("Active draft changed outside the versioned reference importer")
    _verify_import_history(epoch)
    if (epoch / "human-roster.json").exists() != (epoch / "roster-import.json").exists():
        raise ValueError("Actual human roster requires its explicit preserved import record")
    if (epoch / "roster-import.json").exists():
        record = read(epoch / "roster-import.json")
        if (record.get("import_source") != "human_user_submission"
                or record.get("source_sha256") != record.get("copied_sha256")
                or sha256(epoch / "human-roster.json") != record.get("copied_sha256")):
            raise ValueError("Actual human roster differs from its preserved import")
        _people(read(epoch / "human-roster.json"))
    if (epoch / "reference-epoch-freeze.json").exists():
        seal = read(epoch / "reference-epoch-freeze.json")
        for relative, digest in seal["files"].items():
            if sha256(_inside(epoch, relative)) != digest:
                raise ValueError("Sealed reference epoch bytes changed: " + relative)
    return epoch, origin, cases, revisions


def _open(epoch):
    if any((epoch / name).exists() for name in ("reference-freeze.json", "references.json", "reference-epoch-freeze.json")):
        raise ValueError("This reference version is sealed; use an explicit separate corrigendum for later errors")


def validate_current_selection(epoch_dir, proposal_dir):
    """Bind a fresh maintained-selector replay; never inherit a historical pass."""
    epoch, origin, _, _ = _integrity(epoch_dir)
    _open(epoch)
    binding = inspect_current_selection(proposal_dir, origin["corpus_root"], read(epoch / "source-selection.json"))
    write_json(epoch / "current-selection-validation.json", binding, immutable=True)
    return binding


def current_selection_binding(epoch_dir):
    epoch = Path(epoch_dir).resolve()
    path = epoch / "current-selection-validation.json"
    if not path.exists():
        raise ValueError("Current source selection validation is pending; historical hash seals do not establish readiness")
    binding = verify_saved_binding(read(path), read(epoch / "source-selection.json"))
    if Path(binding["corpus_root"]).resolve() != Path(read(epoch / "reference-epoch-origin.json")["corpus_root"]).resolve():
        raise ValueError("Current source selection binding differs from the reference epoch corpus")
    return binding


def prepare_reference_epoch(epoch_dir, *, preparation_run, corpus_root):
    """Copy a verified preparation into a new sibling; create no people or approvals."""
    epoch, parent = Path(epoch_dir).resolve(), Path(preparation_run).resolve()
    if epoch == parent or epoch.parent != parent.parent:
        raise ValueError("Use a new sibling reference epoch, never a child of the sealed preparation")
    if epoch.exists():
        raise ValueError("Use a new reference-epoch directory")
    verification = verify_preparation(parent, corpus_root)
    if verification["status"] != "passed" or verification["packet_count"] != 30:
        raise ValueError("Reference epoch preparation requires the verified 30-packet long cohort")
    epoch.mkdir(parents=True)
    protected = {}
    for name in INHERITED:
        _copy(parent / name, epoch / name)
        protected[name] = sha256(epoch / name)
    for path in sorted((parent / "cases").rglob("*")):
        if path.is_file():
            relative = path.relative_to(parent).as_posix()
            if not path.resolve().is_relative_to(parent):
                raise ValueError("A source packet escapes the parent preparation")
            _copy(path, epoch / relative)
            protected[relative] = sha256(epoch / relative)
    for name in ("preparation-freeze.json", "preparation-state.json", "preparation-verification.json"):
        relative = "inherited-preparation/" + name
        _copy(parent / name, epoch / relative)
        protected[relative] = sha256(epoch / relative)
    cases = _cases(epoch)
    revisions = {"schema_version": SCHEMA, "cases": {}}
    for case in cases:
        case_id = case["case_id"]
        original = parent / "references" / (case_id + ".json")
        history_path = f"reference-history/{case_id}/v0000.json"
        _copy(original, epoch / history_path)
        _copy(original, epoch / "references" / (case_id + ".json"))
        digest = sha256(original)
        protected[history_path] = digest
        revisions["cases"][case_id] = {"active_version": 0, "active_sha256": digest, "history": [
            {"version": 0, "path": history_path, "sha256": digest,
             "reason": "Initial partial source facts copied byte for byte from the sealed preparation."}]}
    write_json(epoch / "reference-revisions.json", revisions, immutable=True)
    origin = {"schema_version": SCHEMA, "created_at": utc_now(), "state": "source_only_reference_epoch",
              "parent_preparation": str(parent), "corpus_root": str(Path(corpus_root).resolve()),
              "parent_preparation_freeze_sha256": sha256(parent / "preparation-freeze.json"),
              "protected_files": protected, "execution_enabled": False, "human_approvals_at_creation": 0,
              "source_selection_readiness_at_creation": "pending_current_selector_validation",
              "human_identity_limit": "Only explicit files submitted by actual humans may be imported. Software does not establish personhood or semantic completeness."}
    write_json(epoch / "reference-epoch-origin.json", origin, immutable=True)
    _integrity(epoch)
    return {"schema_version": SCHEMA, "state": "partial_source_drafts_pending_actual_humans",
            "cases": 30, "actual_human_confirmations": 0, "execution_enabled": False, "model_calls": 0,
            "source_selection_readiness": "pending_current_selector_validation"}


def _facts(reference):
    result = set()
    for group in assessment.REFERENCE_FIELDS:
        for fact in reference[group]:
            if not isinstance(fact, dict):
                raise ValueError("Every reference fact requires a distinct group/id for personal item checks")
            identity = fact.get("id")
            if not isinstance(identity, str) or not identity.strip() or (group, identity) in result:
                raise ValueError("Every reference fact requires a distinct group/id for personal item checks")
            result.add((group, identity))
    return result


def _archive_confirmations(epoch, case_id, version, manifest, reason):
    relative = f"confirmation-history/{case_id}/before-v{version:04d}"
    saved = {}
    paths = ["approvals/import-manifest.json", *(item["path"] for item in manifest["records"])]
    if (epoch / "human-import-provenance.json").exists():
        paths.append("human-import-provenance.json")
    for name in paths:
        source = _inside(epoch, name)
        target = epoch / relative / name
        _copy(source, target)
        saved[target.relative_to(epoch).as_posix()] = sha256(target)
    invalidated = [item for item in manifest["records"] if item.get("case_id") == case_id]
    after = {**manifest, "records": [item for item in manifest["records"] if item.get("case_id") != case_id]}
    write_json(epoch / "approvals/import-manifest.json", after)
    _record_import_event(epoch, kind="case_invalidation", before=manifest, after=after)
    return {"reason": reason, "prior_import_manifest_sha256": saved[relative + "/approvals/import-manifest.json"],
            "invalidated_records": invalidated, "preserved_files": saved,
            "effect": "Only this case's active confirmations were invalidated. Both actual humans must confirm the new reference hash."}


def import_reference_revision(epoch_dir, submission_path, *, reason, invalidate_confirmations=False):
    epoch, _, cases, revisions = _integrity(epoch_dir)
    _open(epoch)
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("A source-grounded revision reason is required")
    submission_path = Path(submission_path).resolve()
    reference = read(submission_path)
    matches = [c for c in cases if c["case_id"] == reference.get("case_id")]
    if len(matches) != 1:
        raise ValueError("Revision must identify one exact frozen case")
    case = matches[0]
    _identity(reference, case)
    _pending(reference)
    assessment.validate_reference_evidence(epoch, reference)
    _facts(reference)
    imports = read(epoch / "approvals/import-manifest.json") if (epoch / "approvals/import-manifest.json").exists() else {"records": []}
    has_confirmations = any(item.get("case_id") == case["case_id"] for item in imports["records"])
    if has_confirmations and not invalidate_confirmations:
        raise ValueError("This case has personal confirmations; explicitly invalidate them for a versioned revision")
    entry = revisions["cases"][case["case_id"]]
    digest = sha256(submission_path)
    if digest == entry["active_sha256"]:
        raise ValueError("A revision must contain a new exact reference version")
    version = entry["active_version"] + 1
    relative = f"reference-history/{case['case_id']}/v{version:04d}.json"
    _copy(submission_path, epoch / relative)
    invalidation = _archive_confirmations(epoch, case["case_id"], version, imports, reason.strip()) if has_confirmations else None
    active = epoch / "references" / (case["case_id"] + ".json")
    active.write_bytes((epoch / relative).read_bytes())
    entry.update(active_version=version, active_sha256=digest)
    entry["history"].append({"version": version, "path": relative, "sha256": digest,
                             "reason": reason.strip(), "imported_at": utc_now(),
                             "confirmation_invalidation": invalidation})
    write_json(epoch / "reference-revisions.json", revisions)
    return {"case_id": case["case_id"], "version": version, "reference_sha256": digest,
            "human_approval_created": False, "model_calls": 0}


def _timestamp(value):
    if not isinstance(value, str):
        raise ValueError("Actual human declarations require explicit timestamp strings")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Actual human declarations require timezone-qualified timestamps")
    return parsed


def _people(roster):
    records = roster.get("reviewers", [])
    if (not isinstance(records, list) or any(not isinstance(p, dict) for p in records)
            or len({p.get("reviewer_id") for p in records}) != len(records)):
        raise ValueError("Actual human roster identities must be distinct")
    people = {p.get("reviewer_id"): p for p in records}
    for person in records:
        if person.get("human") is not True or person.get("role") not in {"reference_verifier", "timed_reviewer"}:
            raise ValueError("Import only actual human role declarations, never assistant or pending identities")
        _timestamp(person.get("declared_at"))
    if {key for key, p in people.items() if p["role"] == "reference_verifier"} != {"H1", "H2"}:
        raise ValueError("Map two actual reference verifiers to the prospectively assigned H1/H2 slots")
    timed = {key for key, p in people.items() if p["role"] == "timed_reviewer"}
    if timed and timed != {"R1", "R2", "R3"}:
        raise ValueError("Optional timed-review declarations must map three separate people to R1/R2/R3")
    return people


def import_actual_roster(epoch_dir, submission_path):
    """Copy an explicitly supplied actual-human roster; never synthesize people."""
    epoch, _, _, _ = _integrity(epoch_dir)
    _open(epoch)
    source = Path(submission_path).resolve()
    _people(read(source))
    target = epoch / "human-roster.json"
    if target.exists():
        raise ValueError("The actual roster is already imported; preserve it and start a new epoch to change people")
    _copy(source, target)
    record = {"source_path": str(source), "source_sha256": sha256(source),
              "copied_path": "human-roster.json", "copied_sha256": sha256(target),
              "import_source": "human_user_submission", "imported_at": utc_now(),
              "identity_limit": "An explicit personal declaration is not independent proof of personhood."}
    write_json(epoch / "roster-import.json", record, immutable=True)
    return {"actual_role_declarations_imported": len(read(target)["reviewers"]),
            "reference_confirmations_created": 0, "model_calls": 0}


def _checked_attestation(epoch, submission, cases, people):
    matched = [case for case in cases if case["case_id"] == submission.get("case_id")]
    if len(matched) != 1:
        raise ValueError("Personal confirmation must identify an exact case in this epoch")
    case = matched[0]
    reference_path = epoch / "references" / (case["case_id"] + ".json")
    reference = assessment.validate_reference_evidence(epoch, read(reference_path))
    _identity(reference, case)
    _pending(reference)
    wanted = _facts(reference)
    person = people.get(submission.get("reviewer_id"), {})
    if (person.get("role") != "reference_verifier" or person.get("human") is not True
            or submission.get("human") is not True or submission.get("approved") is not True
            or submission.get("role") != "reference_verifier"
            or submission.get("confirmation") != assessment.CONFIRMATION
            or submission.get("source_only_attestation") is not True
            or submission.get("source_only_confirmation") != SOURCE_ONLY_CONFIRMATION):
        raise ValueError("A registered actual person must explicitly attest to source-only verification")
    if (submission.get("source_sha256") != case["source_sha256"]
            or submission.get("reference_sha256") != sha256(reference_path)):
        raise ValueError("Personal item checks must bind the current exact source and reference hashes")
    if (not isinstance(submission.get("attestation_id"), str) or not submission["attestation_id"].strip()
            or _timestamp(submission.get("attested_at")) < _timestamp(person.get("declared_at"))):
        raise ValueError("Personal confirmation requires a new identity and a prior actual roster declaration")
    checks = submission.get("per_item_checks")
    if not isinstance(checks, list) or any(not isinstance(c, dict) for c in checks):
        raise ValueError("Actual per-item personal checks are required")
    identities = [(c.get("group"), c.get("id")) for c in checks]
    if (any(not isinstance(group, str) or not isinstance(identity, str) for group, identity in identities)
            or len(identities) != len(set(identities)) or set(identities) != wanted
            or any(c.get("checked") is not True for c in checks)):
        raise ValueError("Personally check every reference fact exactly once by group/id")
    return reference


def _active_imports(epoch):
    path = epoch / "approvals/import-manifest.json"
    return read(path) if path.exists() else {"records": []}


def import_actual_confirmation(epoch_dir, submission_path):
    epoch, _, cases, _ = _integrity(epoch_dir)
    _open(epoch)
    people = _people(read(epoch / "human-roster.json"))
    submission_path = Path(submission_path).resolve()
    submission = read(submission_path)
    _checked_attestation(epoch, submission, cases, people)
    before = _active_imports(epoch)
    existing = before["records"]
    if any(item["case_id"] == submission["case_id"] and item["reviewer_id"] == submission["reviewer_id"] for item in existing):
        raise ValueError("This person already confirmed the active case version")
    for event in _import_history(epoch)["events"]:
        if event["kind"] == "confirmation_import" and read(epoch / event["submission"]["path"])["attestation_id"] == submission["attestation_id"]:
            raise ValueError("Use a new personal attestation identity; prior submissions remain immutable")
    raw_digest = sha256(submission_path)
    original = epoch / "human-submission-history" / (raw_digest + ".json")
    _copy(submission_path, original)
    imported = assessment.import_human_attestation(epoch, original)
    provenance = read(epoch / "human-import-provenance.json") if (epoch / "human-import-provenance.json").exists() else {"records": []}
    provenance["records"].append({"actual_source_path": str(submission_path), "actual_submission_sha256": raw_digest,
                                  "preserved_path": original.relative_to(epoch).as_posix(),
                                  "imported_path": imported["path"], "imported_sha256": imported["sha256"]})
    write_json(epoch / "human-import-provenance.json", provenance)
    _record_import_event(epoch, kind="confirmation_import", before=before, after=_active_imports(epoch),
                         submission={"path": original.relative_to(epoch).as_posix(), "sha256": raw_digest})
    return {"case_id": imported["case_id"], "reviewer_id": imported["reviewer_id"],
            "actual_confirmation_imported": True, "model_calls": 0}


def _all_confirmations(epoch, cases):
    roster_import = read(epoch / "roster-import.json")
    if (roster_import.get("import_source") != "human_user_submission"
            or sha256(epoch / "human-roster.json") != roster_import.get("copied_sha256")):
        raise ValueError("Actual human roster differs from its preserved import")
    people = _people(read(epoch / "human-roster.json"))
    records = _active_imports(epoch)["records"]
    if len(records) != 60 or Counter(item.get("case_id") for item in records) != Counter({c["case_id"]: 2 for c in cases}):
        raise ValueError("All 30 exact references require two actual personal confirmations each")
    seen, attestation_ids = set(), set()
    provenance = read(epoch / "human-import-provenance.json")["records"]
    for item in records:
        path = _inside(epoch, item["path"])
        if (not path.is_relative_to((epoch / "approvals/submissions").resolve())
                or item.get("import_source") != "human_user_submission" or sha256(path) != item["sha256"]):
            raise ValueError("An active personal submission changed or lacks actual human import provenance")
        attestation = read(path)
        _checked_attestation(epoch, attestation, cases, people)
        if (attestation.get("case_id") != item["case_id"] or attestation.get("reviewer_id") != item["reviewer_id"]
                or (item["case_id"], item["reviewer_id"]) in seen
                or attestation["attestation_id"] in attestation_ids):
            raise ValueError("Active personal confirmation identities are duplicated or mismatched")
        seen.add((item["case_id"], item["reviewer_id"]))
        attestation_ids.add(attestation["attestation_id"])
        sources = [p for p in provenance if p["imported_path"] == item["path"] and p["imported_sha256"] == item["sha256"]]
        if len(sources) != 1 or sha256(_inside(epoch, sources[0]["preserved_path"])) != sources[0]["actual_submission_sha256"]:
            raise ValueError("The exact originally submitted human payload is not preserved")
    return records


def freeze_reference_epoch(epoch_dir):
    epoch, origin, cases, _ = _integrity(epoch_dir)
    _open(epoch)
    selection_binding = current_selection_binding(epoch)
    _all_confirmations(epoch, cases)
    for case in cases:
        assessment.validate_reference_evidence(epoch, read(epoch / "references" / (case["case_id"] + ".json")))
    assessment.finalize_human_references(epoch, cases)
    assessment.verify_human_reference_freeze(epoch)
    approved = [{"case_id": c["case_id"], "canonical_id": c["canonical_id"],
                 "source_sha256": c["source_sha256"], "source_tree_sha256": c["source_tree_sha256"],
                 "source_bundle_sha256": c["bundle_sha256"],
                 "reference_sha256": sha256(epoch / "references" / (c["case_id"] + ".json"))} for c in cases]
    write_json(epoch / "approved-source-set.json", {"schema_version": SCHEMA, "cases": approved,
               "parent_preparation_freeze_sha256": origin["parent_preparation_freeze_sha256"],
               "current_selection_binding_sha256": canonical_hash(selection_binding)}, immutable=True)
    files = {p.relative_to(epoch).as_posix(): sha256(p) for p in sorted(epoch.rglob("*")) if p.is_file()}
    seal = {"schema_version": SCHEMA, "state": "human_submissions_sealed_source_only",
            "files": files, "cases": 30, "personal_confirmations": 60, "execution_enabled": False,
            "semantic_limit": "Actual per-item personal attestations are preserved study evidence, not software proof of semantic completeness or personhood."}
    write_json(epoch / "reference-epoch-freeze.json", seal, immutable=True)
    return {"state": seal["state"], "cases": 30, "personal_confirmations": 60,
            "execution_enabled": False, "model_calls": 0}


def verify_reference_epoch(epoch_dir):
    epoch, _, cases, revisions = _integrity(epoch_dir)
    complete = 0
    for case in cases:
        try:
            assessment.validate_reference_evidence(epoch, read(epoch / "references" / (case["case_id"] + ".json")))
            complete += 1
        except ValueError:
            pass
    sealed = (epoch / "reference-epoch-freeze.json").exists()
    readiness = (current_selection_binding(epoch)["state"] if (epoch / "current-selection-validation.json").exists()
                 else "pending_current_selector_validation")
    if sealed:
        current_selection_binding(epoch)
        _all_confirmations(epoch, cases)
        assessment.verify_human_reference_freeze(epoch)
    return {"schema_version": SCHEMA, "integrity": "verified", "cases": len(cases),
            "complete_draft_schema_and_quotes": complete, "reference_epoch_sealed": sealed,
            "actual_active_confirmations": len(_active_imports(epoch)["records"]),
            "actual_roster_imported": (epoch / "roster-import.json").exists(),
            "source_selection_readiness": readiness,
            "execution_enabled": False, "model_calls": 0}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "verify", "validate-selection", "import-reference", "import-roster", "import-human", "freeze-references"))
    parser.add_argument("--epoch-dir", required=True)
    parser.add_argument("--preparation-run")
    parser.add_argument("--corpus-root")
    parser.add_argument("--selection-proposal-dir")
    parser.add_argument("--submission")
    parser.add_argument("--reason")
    parser.add_argument("--invalidate-case-confirmations", action="store_true")
    parser.add_argument("--actual-human-submission", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "prepare":
        if not args.preparation_run or not args.corpus_root:
            parser.error("prepare requires --preparation-run and --corpus-root")
        result = prepare_reference_epoch(args.epoch_dir, preparation_run=args.preparation_run, corpus_root=args.corpus_root)
    elif args.command == "verify":
        result = verify_reference_epoch(args.epoch_dir)
    elif args.command == "freeze-references":
        result = freeze_reference_epoch(args.epoch_dir)
    elif args.command == "validate-selection":
        if not args.selection_proposal_dir:
            parser.error("validate-selection requires --selection-proposal-dir")
        result = validate_current_selection(args.epoch_dir, args.selection_proposal_dir)
    elif args.command == "import-reference":
        if not args.submission or not args.reason:
            parser.error("import-reference requires --submission and a source-grounded --reason")
        result = import_reference_revision(args.epoch_dir, args.submission, reason=args.reason,
                                          invalidate_confirmations=args.invalidate_case_confirmations)
    else:
        if not args.submission or not args.actual_human_submission:
            parser.error("Human import requires an explicitly supplied --submission and --actual-human-submission")
        result = (import_actual_roster if args.command == "import-roster" else import_actual_confirmation)(args.epoch_dir, args.submission)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
