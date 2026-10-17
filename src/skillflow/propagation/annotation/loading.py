"""Read-only verification of completed annotation runs.

Reading is deliberately different from resuming a producer: the saved producer
identity is retained, while its material, request and compilation are checked
with the current supported contracts. This never creates a lock or writes files.
"""
from __future__ import annotations
from skillflow.propagation.contracts.references import cfg_instructions

import json
from pathlib import Path

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.upstream import checked_run_path
from skillflow.common.structural_correction import ResponseChain, response_chain_files
from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.propagation.contracts.specs import iter_effect_events
from skillflow.propagation.contracts.specs import iter_spec_evidence
from skillflow.common.recording import SavedResponseClient
from skillflow.common.recording import canonical_sha256
from skillflow.common.recording import sha_file
from skillflow.common.recording import verify_request_identity
from skillflow.propagation.contracts.runtime_contract import runtime_contract_binding
from skillflow.propagation.contracts.runtime_contract import validate_runtime_contract_binding
from skillflow.propagation.material import checked_material
from skillflow.propagation.material import prepare_material
from skillflow.propagation.contracts.profiles import AnnotationResponse
from skillflow.propagation.contracts.profiles import SCHEMA_VERSION
from skillflow.propagation.annotation.prompts import build_prompt
from skillflow.propagation.annotation.requests import load_repair_context
from skillflow.propagation.annotation.runner import CALL_PATH
from skillflow.propagation.annotation.runner import CALL_PREFIX
from skillflow.propagation.annotation.runner import FORMAT_VERSION
from skillflow.propagation.annotation.runner import IDENTITY
from skillflow.propagation.annotation.runner import POLICY
from skillflow.propagation.annotation.runner import RunIdentityError
from skillflow.propagation.annotation.runner import _config
from skillflow.propagation.annotation.runner import _counts
from skillflow.propagation.annotation.runner import _files
from skillflow.propagation.annotation.runner import _unseal, _check_result_snapshot, result_snapshot
from skillflow.propagation.annotation.runner import _verify_saved_projection
from skillflow.propagation.annotation.services import compile_response
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.annotation.inputs import load_prepared_material, resolve_material_owner


_RESULT_FILES = (
    "manifest.json", "result.json", "validation.json", "audit/location-evidences.json",
    "audit/raw-annotation.json", "audit/compiled-response.json", "audit/compilation-map.json",
)


def _read(path):
    """Reject duplicate keys even in records read by legacy JSON helpers later."""
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    def invalid(value):
        raise ValueError(f"Non-JSON number: {value}")

    return json.loads(checked_run_path(path).read_text(encoding="utf-8"), object_pairs_hook=pairs, parse_constant=invalid)


def _inventory(directory):
    paths = {name: directory / name for name in _RESULT_FILES}
    paths.update({name: directory / name for name in response_chain_files(directory, CALL_PREFIX)})
    paths.update({path.relative_to(directory).as_posix(): path
                  for path in (directory / "inputs").rglob("*") if path.is_file()})
    return {name: sha_file(checked_run_path(path)) for name, path in sorted(paths.items())}


def load_annotation_run(run_dir):
    """Verify a v16 complete annotation and its complete mechanical request chain.

    Returns frozen material, the genuine accepted raw annotation, reconstructed
    compiled annotation and mapping, plus their producer identity. It does not
    follow or revalidate mutable original source paths. Frozen bytes remain the
    authority. A changed rule, prompt or compiler that cannot reconstruct the
    saved materials is rejected, as are incomplete executions and old formats.
    """
    directory = checked_run_path(run_dir)
    try:
        identity = _read(directory / "manifest.json")
        if (identity.get("identity") != IDENTITY or identity.get("schema_version") != FORMAT_VERSION
                or identity.get("profile_schema_version") != SCHEMA_VERSION):
            raise RunIdentityError("Unsupported security-profile run version")
        before = _inventory(directory)
        # Skill-owned *.json files are text inputs, not our record format: their
        # contents can legitimately be an example fragment or malformed sample.
        record_names = [name for name in before if name.endswith(".json") and not name.startswith("inputs/")]
        values = {name: _read(directory / name) for name in record_names}
        manifest = values["manifest.json"]
        if (manifest.get("identity") != IDENTITY or manifest.get("schema_version") != FORMAT_VERSION
                or manifest.get("profile_schema_version") != SCHEMA_VERSION):
            raise RunIdentityError("Unsupported security-profile run version")
        _unseal(manifest)
        if manifest.get("policy") != POLICY:
            raise ValueError("Saved annotation structural-correction policy changed")
        if manifest.get("preparation_status") != "ready":
            raise ValueError("Annotation preparation did not complete")
        producer = manifest.get("implementation", {})
        if (not isinstance(producer.get("files"), dict) or not producer["files"]
                or canonical_sha256(producer["files"]) != producer.get("sha256")):
            raise ValueError("Saved annotation producer identity is invalid")
        if manifest.get("config") != _config(manifest.get("config")):
            raise ValueError("Saved annotation configuration is not normalized")
        if manifest.get("files") != _files(directory):
            raise ValueError("Frozen annotation input inventory or bytes changed")
        material = load_prepared_material(directory)
        _, source, source_metadata = read_snapshot(resolve_material_owner(directory))
        cfg = material["cfg"]
        if (material != prepare_material(source, cfg, task_baseline=material["task"], user_request=material["user_request"])
                or manifest.get("source_sha256") != source["source_sha256"]
                or manifest.get("graph_sha256") != canonical_sha256(cfg)
                or manifest.get("material_sha256") != canonical_sha256(material)
                or manifest.get("boundaries") != source_metadata["boundaries"]):
            raise ValueError("Annotation source, CFG, material or boundary identity differs")
        validate_runtime_contract_binding(manifest.get("runtime_contract"))
        if manifest["runtime_contract"] != runtime_contract_binding(material["runtime_contract"]):
            raise ValueError("Annotation execution model identity differs")
        repair_context = load_repair_context(directory, material=material, manifest=manifest)
        if (manifest.get("repair_context_sha256") != canonical_sha256(repair_context)
                or manifest.get("request_kind") != ("base" if repair_context is None else "repair")):
            raise ValueError("Saved annotation request identity differs")
        prompt = build_prompt(material, repair_context)
        if (prompt != (directory / "inputs/prompt.txt").read_bytes().decode("utf-8")
                or manifest.get("prompt_sha256") != canonical_sha256(prompt)):
            raise ValueError("Annotation prompt identity differs")

        result = _check_result_snapshot(values["result.json"], manifest)
        if (result.get("status") not in {"complete"}
                or result.get("validation", {}).get("status") != "passed"
                or result.get("source_sha256") != manifest["source_sha256"]
                or result.get("graph_sha256") != manifest["graph_sha256"]
                or result.get("boundaries") != manifest["boundaries"]
                or result.get("run_id") != manifest["run_id"]
                or result.get("error_kind") is not None):
            raise ValueError("Read-only loading requires a validated completed annotation")
        chain = ResponseChain(directory, prefix=CALL_PREFIX, base_prompt=prompt,
            request_kind=manifest["request_kind"], config=manifest["config"], writer=ArtifactWriter(()),
            validate=lambda response: compile_response(response, material), replay=True, read_only=True)
        raw, compiled, mapping = chain.run()
        if (canonical_sha256(chain.snapshot()) != canonical_sha256(result.get("response_chain")) or chain.accepted_call != result.get("accepted_call")
                or not chain.accepted_call):
            raise ValueError("Saved annotation final call or structural response chain differs")
        accepted, request = chain.response, chain.request_validation
        payload = to_payload(compiled)
        result = {**result, **payload}
        _verify_saved_projection(directory, payload, compiled["location_evidences"],
                                 manifest["runtime_contract"], (raw, compiled, mapping), request)
        if canonical_sha256(values["validation.json"]) != canonical_sha256(result["validation"]):
            raise ValueError("Saved annotation validation projection differs")
        typed = AnnotationResponse.model_validate(compiled)
        location_count = sum(map(len, compiled["location_evidences"].values()))
        expected_validation = {
            "status": "passed", "instruction_count": len(cfg_instructions(material["cfg"])),
            "ir_semantics_count": len(compiled["ir_semantics"]), "location_count": len(compiled["locations"]),
            "sink_boundary_count": len(compiled["sink_boundaries"]),
            "atomic_op_count": sum(len(event.atomic_ops) for spec in typed.ir_semantics.values()
                                   for event in iter_effect_events(spec)),
            "evidence_count": (sum(1 for _ in iter_spec_evidence(typed)) + location_count),
            "location_evidence_count": location_count, "errors": [],
        }
        if (canonical_sha256(result["validation"]) != canonical_sha256(expected_validation)
                or canonical_sha256(result.get("counts")) != canonical_sha256(_counts(directory))):
            raise ValueError("Annotation validation or call summary differs from reconstructed records")
        if _inventory(directory) != before:
            raise ValueError("Annotation files changed during read-only verification")
        identity = {
            "identity": IDENTITY, "schema_version": FORMAT_VERSION,
            "profile_schema_version": SCHEMA_VERSION,
            "manifest_sha256": manifest["manifest_sha256"], "implementation": producer,
            "source_sha256": manifest["source_sha256"], "graph_sha256": manifest["graph_sha256"],
            "material_sha256": canonical_sha256(material), "prompt_sha256": canonical_sha256(prompt),
            "accepted_response_sha256": canonical_sha256(accepted),
            "response_chain_sha256": canonical_sha256(chain.snapshot()), "accepted_call": chain.accepted_call,
            "compilation": result["compilation"], "request_validation": request,
            "files": before,
        }
        return {"manifest": manifest, "material": material, "prompt": prompt, "repair_context": repair_context,
                "response_chain": chain.snapshot(), "accepted_call": chain.accepted_call,
                "accepted_prompt": chain.prompt, "accepted_response": accepted,
                "raw_annotation": raw, "compiled_annotation": compiled, "mapping": mapping,
                "result": result, "request_validation": request, "source_metadata": source_metadata, "task": material["task"],
                "upstream_identity": identity}
    except RunIdentityError:
        raise
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
        raise RunIdentityError("Read-only annotation verification failed: " + str(error)) from error


def load_annotation_attempt(run_dir):
    """Verify a saved successful or failed attempt without resuming its producer.

    Failure classification is reconstructed by the same saved-response path as
    replay. The private read-only branch neither writes reports nor weakens the
    public runner's strict implementation check.
    """
    from skillflow.propagation.annotation.runner import _run_annotation
    directory = checked_run_path(run_dir)
    saved = _read(directory / "result.json")
    if saved.get("status") == "complete":
        return load_annotation_run(directory)

    def inventory():
        return {p.relative_to(directory).as_posix(): sha_file(p)
                for p in sorted(directory.rglob("*")) if p.is_file()
                and p.relative_to(directory).parts[0] != "replay"
                and p.relative_to(directory).as_posix() not in {"report.html", "report.md", ".runner.lock"}}

    before = inventory()
    manifest = _read(directory / "manifest.json")
    producer = manifest.get("implementation", {})
    if (not producer.get("files") or canonical_sha256(producer["files"]) != producer.get("sha256")):
        raise RunIdentityError("Saved annotation producer identity is invalid")
    result = _run_annotation(directory, replay=True, read_only=True)
    if canonical_sha256(result_snapshot(result)) != canonical_sha256(saved):
        raise RunIdentityError("Saved annotation failure differs from its accepted response or execution boundary")
    if inventory() != before:
        raise RunIdentityError("Annotation attempt changed during read-only verification")
    return {"manifest": manifest, "result": result,
            "material": load_prepared_material(directory) if manifest.get("preparation_status") == "ready" else None,
            "upstream_identity": {"identity": IDENTITY, "schema_version": FORMAT_VERSION,
                                  "implementation": producer, "files": before}}
