"""Read-only verification of completed annotation runs.

Reading is deliberately different from resuming a producer: the saved producer
identity is retained, while its material, request and compilation are checked
with the current supported contracts. This never creates a lock or writes files.
"""
from __future__ import annotations

import json
from pathlib import Path

from skill_ir.experiments.report import ArtifactWriter
from skill_ir.inputs.snapshot import read_snapshot
from skill_ir.propagation.specs import iter_effect_events, iter_spec_evidence
from skill_ir.recording import SavedResponseClient, canonical_sha256, sha_file, verify_request_identity
from skill_ir.runtime_contract import execution_model_binding, validate_execution_model_binding
from .evidence import checked_material, prepare_material
from .models import AnnotationResponse, SCHEMA_VERSION
from .prompts import build_prompt
from .requests import validate_repair_context
from skill_ir.representation_contract import binding as representation_binding
from .runner import (CALL_PATH, FORMAT_VERSION, IDENTITY, RunIdentityError, _config,
                     _counts, _files, _unseal, _verify_saved_projection)
from .services import compile_response, to_payload


_RESULT_FILES = (
    "manifest.json", "result.json", "profiles.json", "locations.json", "transfer-specs.json",
    "validation.json", "sink-boundaries.json", "audit/location-evidences.json",
    "audit/raw-annotation.json", "audit/compiled-response.json", "audit/compilation-map.json",
    *(f"{CALL_PATH}/{name}" for name in ("call.json", "transport.json", "prompt.txt", "response.json")),
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

    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=pairs, parse_constant=invalid)


def _inventory(directory):
    paths = {name: directory / name for name in _RESULT_FILES}
    paths.update({path.relative_to(directory).as_posix(): path
                  for path in (directory / "inputs").rglob("*") if path.is_file()})
    return {name: sha_file(path) for name, path in sorted(paths.items())}


def load_annotation_run(run_dir):
    """Verify a v11 complete annotation without producer-source matching.

    Returns frozen material, the genuine accepted raw annotation, reconstructed
    compiled annotation and mapping, plus their producer identity. It does not
    follow or revalidate mutable original source paths. Frozen bytes remain the
    authority. A changed rule, prompt or compiler that cannot reconstruct the
    saved materials is rejected, as are incomplete executions and old formats.
    """
    directory = Path(run_dir).resolve()
    try:
        identity = _read(directory / "manifest.json")
        if (identity.get("identity") != IDENTITY or identity.get("schema_version") != FORMAT_VERSION
                or identity.get("profile_schema_version") != SCHEMA_VERSION):
            raise RunIdentityError("Unsupported security-profile run version")
        before = _inventory(directory)
        # Skill-owned *.json files are text inputs, not our record format: their
        # contents can legitimately be an example fragment or malformed sample.
        record_names = [name for name in _RESULT_FILES if name.endswith(".json")]
        record_names += ["inputs/material.json", "inputs/cfg.json", "inputs/repair-context.json"]
        values = {name: _read(directory / name) for name in record_names}
        manifest = values["manifest.json"]
        if (manifest.get("identity") != IDENTITY or manifest.get("schema_version") != FORMAT_VERSION
                or manifest.get("profile_schema_version") != SCHEMA_VERSION):
            raise RunIdentityError("Unsupported security-profile run version")
        _unseal(manifest)
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
        _, source, source_metadata = read_snapshot(directory)
        material = checked_material(values["inputs/material.json"])
        cfg = values["inputs/cfg.json"]
        if (material != prepare_material(source, cfg)
                or manifest.get("source_sha256") != source["source_sha256"]
                or manifest.get("graph_sha256") != canonical_sha256(cfg)
                or manifest.get("material_sha256") != canonical_sha256(material)
                or manifest.get("boundaries") != source_metadata["boundaries"]):
            raise ValueError("Annotation source, CFG, material or boundary identity differs")
        validate_execution_model_binding(manifest.get("execution_model"))
        if manifest["execution_model"] != execution_model_binding(material["execution_model"]):
            raise ValueError("Annotation execution model identity differs")
        repair_context = values["inputs/repair-context.json"]
        validate_repair_context(material, repair_context)
        if (manifest.get("repair_context_sha256") != canonical_sha256(repair_context)
                or manifest.get("request_kind") != ("base" if repair_context is None else "repair")
                or manifest.get("representation_contract") != representation_binding()):
            raise ValueError("Saved annotation request or representation contract differs")
        prompt = build_prompt(material, repair_context)
        if (prompt != (directory / "inputs/prompt.txt").read_bytes().decode("utf-8")
                or manifest.get("prompt_sha256") != canonical_sha256(prompt)
                or prompt != (directory / CALL_PATH / "prompt.txt").read_bytes().decode("utf-8")):
            raise ValueError("Annotation prompt identity differs")

        result = values["result.json"]
        if (result.get("status") not in {"complete"}
                or result.get("validation", {}).get("status") != "passed"
                or result.get("source_sha256") != manifest["source_sha256"]
                or result.get("graph_sha256") != manifest["graph_sha256"]
                or result.get("boundaries") != manifest["boundaries"]
                or result.get("run_id") != manifest["run_id"]
                or result.get("error_kind") is not None):
            raise ValueError("Read-only loading requires a validated completed annotation")
        accepted = SavedResponseClient(directory / CALL_PATH, ArtifactWriter(())).complete(prompt)
        if accepted != values[f"{CALL_PATH}/response.json"]:
            raise ValueError("Saved response export differs from the accepted response")
        request = verify_request_identity(directory / CALL_PATH, manifest["config"], prompt=prompt)
        raw, compiled, mapping = compile_response(accepted, material)
        payload = to_payload(compiled)
        _verify_saved_projection(directory, payload, compiled["location_evidences"],
                                 manifest["execution_model"], (raw, compiled, mapping), request)
        for filename, key in (("profiles.json", "profiles"), ("locations.json", "locations"),
                              ("transfer-specs.json", "transfer_specs"),
                              ("sink-boundaries.json", "sink_boundaries"),
                              ("validation.json", "validation")):
            if values[filename] != result[key]:
                raise ValueError("Saved annotation projection differs: " + filename)
        typed = AnnotationResponse.model_validate(compiled)
        location_count = sum(map(len, compiled["location_evidences"].values()))
        expected_validation = {
            "status": "passed", "instruction_count": len(material["instruction_index"]),
            "profile_count": len(compiled["profiles"]), "location_count": len(compiled["locations"]),
            "transfer_spec_count": len(compiled["transfer_specs"]),
            "sink_boundary_count": len(compiled["sink_boundaries"]),
            "atomic_op_count": sum(len(event.atomic_ops) for spec in typed.transfer_specs.values()
                                   for event in iter_effect_events(spec)),
            "evidence_count": (sum(len(p["evidences"]) for p in compiled["profiles"].values())
                               + sum(1 for _ in iter_spec_evidence(typed)) + location_count),
            "location_evidence_count": location_count, "errors": [],
        }
        if result["validation"] != expected_validation or result.get("counts") != _counts(directory):
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
            "compilation": result["compilation"], "request_validation": request,
            "files": before,
        }
        return {"manifest": manifest, "material": material, "prompt": prompt, "repair_context": repair_context,
                "raw_annotation": raw, "compiled_annotation": compiled, "mapping": mapping,
                "result": result, "request_validation": request, "source_metadata": source_metadata,
                "upstream_identity": identity}
    except RunIdentityError:
        raise
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
        raise RunIdentityError("Read-only annotation verification failed: " + str(error)) from error
