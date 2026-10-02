"""Capture successful stages, then recompute propagation after a report-only fix.

This is neither a migration nor an annotation run. The original failed run and
its accepted calls remain immutable. A capture is made with the original code;
recovery permits exactly one source change, propagation/report.py.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from copy import deepcopy
import json
from pathlib import Path
import socket
import sys

PACKAGE = Path(__file__).resolve().parents[3]
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE / "src"))

from skill_ir import recording
from skill_ir.data import DataRegistry
from skill_ir.experiments.report import ArtifactWriter
from skill_ir.experiments.resumable import _exclusive_run
from skill_ir.feedback.runner import replay_run as replay_feedback
from skill_ir.inputs.snapshot import read_snapshot
from skill_ir.propagation.handoff import build_doe_input, load_doe_input
from skill_ir.propagation.models import FlowState
from skill_ir.propagation.runner import load_propagation_run, replay_propagation, save_propagation_run
from skill_ir.propagation.solver import propagate
from skill_ir.recording import SavedResponseClient, canonical_sha256, implementation_provenance, now, read_json, sha_file, verify_request_identity
from skill_ir.security_profile.evidence import checked_material
from skill_ir.security_profile.runner import replay_run as replay_annotation, verify_prepared
from skill_ir.security_profile.services import to_payload, compile_response
from skill_ir.security_profile.runner import compilation_certificate
from skill_ir.security_profile.runner import IDENTITY as ANNOTATION_IDENTITY, FORMAT_VERSION as ANNOTATION_FORMAT_VERSION
from skill_ir.security_profile.models import SCHEMA_VERSION as PROFILE_VERSION

IDENTITY = "skill-ir-source-boundaries-offline-recovery-v3"
FORMAT_VERSION = 3
PILOT_IDENTITY = "skill-ir-source-boundaries-pilot3-v4"
PILOT_FORMAT_VERSION = 4
REPORT_SOURCE = "packages/skill-ir/src/skill_ir/propagation/report.py"
WRITER = ArtifactWriter(())


@contextmanager
def network_guard():
    """Fail closed before any socket connection or online factory construction."""
    attempts = []
    saved = (socket.socket.connect, socket.socket.connect_ex, socket.create_connection, recording.streaming_factory)
    def denied(name):
        def fail(*args, **kwargs):
            attempts.append(name)
            raise RuntimeError("offline recovery forbids network/client creation: " + name)
        return fail
    socket.socket.connect = denied("socket.connect")
    socket.socket.connect_ex = denied("socket.connect_ex")
    socket.create_connection = denied("socket.create_connection")
    recording.streaming_factory = denied("recording.streaming_factory")
    try:
        yield attempts
    finally:
        socket.socket.connect, socket.socket.connect_ex, socket.create_connection, recording.streaming_factory = saved


def guard_record(attempts):
    return {"status": "passed" if not attempts else "failed", "network_attempts": len(attempts),
            "attempts": list(attempts), "blocked_surfaces": ["socket.connect", "socket.connect_ex",
                                                             "socket.create_connection", "recording.streaming_factory"]}


def _seal(value):
    return {**value, "receipt_sha256": canonical_sha256(value)}


def _read_receipt(directory):
    value = read_json(Path(directory) / "receipt.json")
    unsigned = {key: val for key, val in value.items() if key != "receipt_sha256"}
    if (value.get("identity") != IDENTITY or value.get("schema_version") != FORMAT_VERSION
            or canonical_sha256(unsigned) != value.get("receipt_sha256")):
        raise ValueError("unsupported or altered offline capture receipt")
    if value.get("tool_sha256") != sha_file(Path(__file__)):
        raise ValueError("offline recovery tool changed after capture")
    if value.get("network_guard", {}).get("status") != "passed" or value["network_guard"].get("network_attempts") != 0:
        raise ValueError("capture did not pass the offline network guard")
    return value


def source_change(before, after):
    if set(before) != set(after) or before.get("python") != after.get("python"):
        raise ValueError("recovery implementation environment differs")
    if set(before["files"]) != set(after["files"]):
        raise ValueError("recovery source inventory differs")
    changed = [name for name, digest in before["files"].items() if after["files"][name] != digest]
    if changed != [REPORT_SOURCE]:
        raise ValueError("recovery permits exactly propagation/report.py to change")
    return {REPORT_SOURCE: {"before": before["files"][REPORT_SOURCE], "after": after["files"][REPORT_SOURCE]}}


def material_hashes(case_dir):
    """Only durable inputs/results; later assistant reviews and replay outputs are separate."""
    case_dir = Path(case_dir).resolve()
    root = case_dir.parents[1]
    paths = [root / "manifest.json"]
    for name in ("result.json", "selection.json", "selected-analysis.json", "source-binding.json",
                 "execution-boundary.json", "driver-error.json"):
        if (case_dir / name).is_file():
            paths.append(case_dir / name)
    for name in ("source", "feedback", "annotation", "propagation"):
        directory = case_dir / name
        if directory.exists():
            paths += [p for p in directory.rglob("*") if p.is_file()
                      and "replay" not in p.relative_to(directory).parts and p.name != ".runner.lock"]
    return {path.relative_to(root).as_posix(): sha_file(path) for path in sorted(paths)}


def unchanged(receipt):
    if material_hashes(receipt["case_dir"]) != receipt["original_materials"]:
        raise ValueError("original captured inputs, responses, selection or failed outputs changed")


def accepted_material(case_dir, *, check_current_implementation):
    """Validate frozen source, exact accepted prompt/response, and both projections."""
    directory = Path(case_dir) / "annotation"
    manifest = read_json(directory / "manifest.json")
    if (manifest.get("identity") != ANNOTATION_IDENTITY or manifest.get("schema_version") != ANNOTATION_FORMAT_VERSION
            or manifest.get("profile_schema_version") != PROFILE_VERSION
            or canonical_sha256({k: v for k, v in manifest.items() if k != "manifest_sha256"}) != manifest.get("manifest_sha256")):
        raise ValueError("unsupported or altered original annotation manifest")
    if check_current_implementation:
        if verify_prepared(directory, replay=True) != manifest:
            raise ValueError("annotation verification changed manifest")
    files = {p.relative_to(directory).as_posix(): sha_file(p) for p in sorted((directory / "inputs").rglob("*")) if p.is_file()}
    if files != manifest["files"] or manifest["preparation_status"] != "ready":
        raise ValueError("annotation frozen input identity differs")
    material = checked_material(read_json(directory / "inputs/material.json"))
    _, source, metadata = read_snapshot(directory)
    from skill_ir.security_profile.loading import load_annotation_run
    prompt = load_annotation_run(directory)["prompt"]
    if (source != material["source"] or material["cfg"] != read_json(directory / "inputs/cfg.json")
            or canonical_sha256(material) != manifest["material_sha256"]
            or canonical_sha256(prompt) != manifest["prompt_sha256"]
            or prompt != (directory / "inputs/prompt.txt").read_bytes().decode("utf-8")
            or source["source_sha256"] != manifest["source_sha256"]
            or canonical_sha256(material["cfg"]) != manifest["graph_sha256"]):
        raise ValueError("source/CFG/material/exact prompt identity differs")
    result = read_json(directory / "result.json")
    if (result.get("identity") != manifest["identity"] or result.get("schema_version") != ANNOTATION_FORMAT_VERSION
            or result.get("profile_schema_version") != PROFILE_VERSION
            or result.get("status") not in {"complete"}
            or result.get("validation", {}).get("status") != "passed"
            or result.get("source_sha256") != manifest["source_sha256"]
            or result.get("graph_sha256") != manifest["graph_sha256"]):
        raise ValueError("recovery requires a completed, valid original annotation")
    # Do not turn an interrupted or uncertain call into a recovered annotation.
    call_dir = directory / "calls/annotation/a001"
    if read_json(call_dir / "call.json").get("status") != "complete":
        raise ValueError("annotation call was not durably accepted")
    accepted = SavedResponseClient(call_dir, WRITER).complete(prompt)
    if result.get("request_validation") != verify_request_identity(call_dir, manifest["config"], prompt=prompt):
        raise ValueError("annotation request identity differs")
    raw, response, mapping = compile_response(accepted, material)
    if (read_json(directory / "audit/raw-annotation.json") != raw
            or read_json(directory / "audit/compiled-response.json") != response
            or read_json(directory / "audit/compilation-map.json") != mapping
            or result.get("compilation") != compilation_certificate(raw, response, mapping)):
        raise ValueError("accepted compilation material differs")
    payload = to_payload(response)
    if payload != {key: result[key] for key in ("profiles", "locations", "transfer_specs", "sink_boundaries")}:
        raise ValueError("saved annotation differs from accepted response")
    evidence = read_json(directory / "audit/location-evidences.json")
    if (evidence != response["location_evidences"] or canonical_sha256(evidence) != result["location_evidences_sha256"]):
        raise ValueError("annotation evidence differs")
    calls = {name: read_json(call_dir / name) for name in ("call.json", "transport.json")}
    return manifest, material, metadata, result, payload, evidence, calls, accepted


def capture(case_dir, receipt_dir):
    case_dir, receipt_dir = Path(case_dir).resolve(), Path(receipt_dir).resolve()
    root = case_dir.parents[1]
    if not receipt_dir.is_relative_to(root / "offline-recovery"):
        raise ValueError("capture receipts must use this pilot's new offline-recovery directory")
    if receipt_dir.exists() and any(receipt_dir.iterdir()):
        raise ValueError("capture requires a new or empty receipt directory")
    with network_guard() as attempts, _exclusive_run(root):
        pilot = read_json(root / "manifest.json")
        current = implementation_provenance()
        if (pilot.get("identity") != PILOT_IDENTITY or pilot.get("schema_version") != PILOT_FORMAT_VERSION
                or pilot.get("profile_schema_version") != PROFILE_VERSION
                or pilot["implementation"] != current):
            raise ValueError("capture requires the original pilot version and exact original source identity")
        for relative, field in (("experiments/propagation/tools/run_pilot.py", "driver_sha256"),
                                ("experiments/security_profile/tools/run_full_pipeline.py", "shared_case_driver_sha256")):
            if sha_file(PACKAGE / relative) != pilot[field]:
                raise ValueError("original pilot driver changed")
        before = material_hashes(case_dir)
        stages = read_json(case_dir / "result.json")
        if (stages["feedback"]["status"] in {"not_run", "interrupted"}
                or stages["annotation"]["status"] not in {"complete"}):
            raise ValueError("only finished cases with valid annotations are eligible for recovery")
        renderer = read_json(case_dir / "feedback/manifest.json")["renderer"]["path"]
        fb = replay_feedback(case_dir / "feedback", renderer=renderer)
        ann = replay_annotation(case_dir / "annotation")
        if fb != stages["feedback"] or ann != stages["annotation"]:
            raise ValueError("original stage replay differs from accepted case results")
        selected = read_json(case_dir / "selected-analysis.json")["cfg"]
        selection = read_json(case_dir / "selection.json")
        if (selected != fb["last_valid_cfg"] or canonical_sha256(selected) != selection["graph_sha256"]
                or selection != stages["selection"] or selection["auditor_passed"] != (fb["status"] == "audit_passed")):
            raise ValueError("selected graph is not the original current-feedback selection")
        manifest, material, metadata, result, payload, evidence, calls, accepted = accepted_material(
            case_dir, check_current_implementation=True)
        if selected != material["cfg"]:
            raise ValueError("annotation uses a different selected graph")
        pinned = [item for item in pilot["cases"] if item["case_id"] == case_dir.name]
        if len(pinned) != 1:
            raise ValueError("original case is not uniquely pinned in this pilot")
        _, source, seed_metadata = read_snapshot(case_dir / "source")
        _, feedback_source, feedback_metadata = read_snapshot(case_dir / "feedback")
        inventory = {item["path"]: {"bytes": item["size"], "sha256": item["raw_sha256"]} for item in metadata["files"]}
        binding = read_json(case_dir / "source-binding.json")
        if (source != material["source"] or feedback_source != source
                or seed_metadata["files"] != metadata["files"] or feedback_metadata["files"] != metadata["files"]
                or source["source_sha256"] != pinned[0]["source_sha256"]
                or metadata["package_bytes_sha256"] != pinned[0]["package_bytes_sha256"]
                or inventory != pinned[0]["source_inventory"]
                or binding != stages["source_binding"] or binding["status"] != "passed"
                or binding["source_sha256"] != source["source_sha256"]
                or binding["package_bytes_sha256"] != metadata["package_bytes_sha256"]):
            raise ValueError("source/feedback/annotation snapshots differ from the original pinned package")
        old_dir = case_dir / "propagation"
        old = load_doe_input(old_dir / "doe-input.json") if (old_dir / "doe-input.json").is_file() else None
        committed = (old_dir / "manifest.json").is_file()
        if committed and load_propagation_run(old_dir) != old:
            raise ValueError("committed original propagation differs")
        seed_path, state_path = old_dir / "audit/requested-data.json", old_dir / "audit/requested-state.json"
        seed, state = read_json(seed_path) if seed_path.exists() else None, read_json(state_path) if state_path.exists() else None
        after = material_hashes(case_dir)
        if before != after:
            raise ValueError("capture mutated original durable inputs or results")
        receipt = {"schema_version": FORMAT_VERSION, "identity": IDENTITY, "captured_at": now(), "case_dir": str(case_dir),
                   "case_id": case_dir.name, "original_run_identity": PILOT_IDENTITY,
                   "capture_implementation": current, "tool_sha256": sha_file(Path(__file__)),
                   "original_materials": before, "original_materials_sha256": canonical_sha256(before),
                   "stage_replay": {"feedback_equal": True, "annotation_equal": True,
                                    "feedback_status": fb["status"], "annotation_status": ann["status"]},
                   "selected_graph_sha256": selection["graph_sha256"], "source_sha256": manifest["source_sha256"],
                   "accepted_response_sha256": canonical_sha256(accepted), "prompt_sha256": manifest["prompt_sha256"],
                   "original_propagation": {"committed": committed, "business_status": old["status"] if old else None,
                                            "doe_input_sha256": canonical_sha256(old) if old else None,
                                            "driver_error": read_json(case_dir / "driver-error.json") if (case_dir / "driver-error.json").exists() else None},
                   "requested_data": seed, "requested_state": state, "model_calls": 0,
                   "network_guard": guard_record(attempts)}
        WRITER.json(receipt_dir / "receipt.json", _seal(receipt))
    return _read_receipt(receipt_dir)


def recover(receipt_dir, run_dir):
    receipt, directory = _read_receipt(receipt_dir), Path(run_dir).resolve()
    case_dir = Path(receipt["case_dir"])
    if not directory.is_relative_to(case_dir.parents[1] / "offline-recovery"):
        raise ValueError("recovery must use this pilot's new offline-recovery directory")
    if directory.exists() and any(directory.iterdir()):
        raise ValueError("recovery requires a new or empty propagation directory")
    current = implementation_provenance()
    changes = source_change(receipt["capture_implementation"], current)
    with network_guard() as attempts, _exclusive_run(case_dir.parents[1]):
        unchanged(receipt)
        manifest, material, metadata, result, payload, evidence, calls, accepted = accepted_material(
            case_dir, check_current_implementation=False)
        if (canonical_sha256(accepted) != receipt["accepted_response_sha256"]
                or manifest["prompt_sha256"] != receipt["prompt_sha256"]
                or manifest["graph_sha256"] != receipt["selected_graph_sha256"]
                or manifest["source_sha256"] != receipt["source_sha256"]):
            raise ValueError("captured annotation identities changed")
        seed, state = receipt["requested_data"], receipt["requested_state"]
        solved = propagate(material["cfg"], payload,
                           initial_registry=DataRegistry.from_dict(seed) if seed is not None else None,
                           initial_state=FlowState.model_validate(state) if state is not None else None)
        business = build_doe_input(material["source"], material["cfg"], payload, solved, source_metadata=metadata,
                                   execution_model=material["execution_model"])
        old_hash = receipt["original_propagation"]["doe_input_sha256"]
        if old_hash is not None and canonical_sha256(business) != old_hash:
            raise ValueError("report-only recovery changed the original DOE business facts")
        origin = case_dir / "annotation"
        original_files = ("manifest.json", "result.json", "audit/location-evidences.json",
                          "calls/annotation/a001/call.json", "calls/annotation/a001/transport.json")
        provenance = {"kind": "model_annotation", "annotation_path": str(origin), "annotation_manifest": manifest,
                      "original_sha256": {name: sha_file(origin / name) for name in original_files},
                      "accepted_response_sha256": canonical_sha256(accepted),
                      "request_validation": result["request_validation"],
                      "recovery": {"identity": IDENTITY, "capture_receipt": receipt,
                                   "current_implementation_sha256": current["sha256"], "changed_source": changes,
                                   "original_run_repaired": False, "new_model_calls": 0}}
        raw, compiled, mapping = compile_response(accepted, material)
        written = save_propagation_run(directory, material=material, source_metadata=metadata, annotation=payload,
                                      location_evidences=evidence, solved=solved, requested_data=seed, requested_state=state,
                                      raw_annotation=raw, compilation_map=mapping,
                                      provenance=provenance, accepted_files=deepcopy(calls), before_commit=lambda: unchanged(receipt))
        if written != business or load_doe_input(directory / "doe-input.json") != business or load_propagation_run(directory) != business:
            raise ValueError("recovered business or complete-run loading differs")
        if replay_propagation(directory) != business:
            raise ValueError("recovered propagation offline replay differs")
        unchanged(receipt)
        check = {"schema_version": FORMAT_VERSION, "identity": IDENTITY, "status": "matched", "model_calls": 0,
                 "capture_receipt_sha256": receipt["receipt_sha256"], "changed_source": changes,
                 "original_propagation_committed": receipt["original_propagation"]["committed"],
                 "original_doe_equal": True if old_hash is not None else None,
                 "doe_input_sha256": canonical_sha256(business), "standalone_load": "passed",
                 "complete_run_load": "passed", "offline_replay": "matched", "network_guard": guard_record(attempts)}
        WRITER.json(directory / "recovery-check.json", check)
    return check


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    first = commands.add_parser("capture")
    first.add_argument("--case-dir", type=Path, required=True)
    first.add_argument("--receipt-dir", type=Path, required=True)
    second = commands.add_parser("recover")
    second.add_argument("--receipt-dir", type=Path, required=True)
    second.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    result = capture(args.case_dir, args.receipt_dir) if args.command == "capture" else recover(args.receipt_dir, args.run_dir)
    print(json.dumps({key: result[key] for key in ("identity", "model_calls", "network_guard")}, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
