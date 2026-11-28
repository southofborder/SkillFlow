"""Passive presentation audit of the sole current GA4; no stage/backend replay.

Reads saved JSON/text and calls only the two lossless presentation codecs.
It neither constructs a client nor imports stage validators or controllers.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from skillflow.document_guided.fragment_wire import expand_processing_response, PROCESSING_WIRE_IDENTITY
from skillflow.document_guided.processing_display import expand_processing_material, INPUT_MARKER


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RUN = ROOT / "experiments/doe/runs/document-guided-ga4-processing-shared-high-20261116-225414"


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def unique_object(pairs):
    value = {}
    for key, child in pairs:
        if key in value:
            raise ValueError("duplicate JSON member: " + key)
        value[key] = child
    return value


def read(path):
    return json.loads(path.read_bytes().decode("utf-8"))


def digest(value):
    return hashlib.sha256(value).hexdigest()


def frozen_source():
    snapshot = read(RUN / "source/inputs/snapshot.json")
    files, rows = {}, []
    for row in snapshot["files"]:
        raw = (RUN / "source/inputs/package" / row["path"]).read_bytes()
        content = raw.decode("utf-8")
        files["skill/" + row["path"]] = content
        rows.append({"path": row["path"], "bytes": len(raw), "raw_sha256_matches": digest(raw) == row["raw_sha256"],
                     "physical_lines": len(content.splitlines(keepends=True))})
    parts = ["File navigation (not proof of semantic coverage):"]
    parts.extend(f"- {name} ({len(content.splitlines(keepends=True))} physical lines)" for name, content in files.items())
    for name, content in files.items():
        lines = content.splitlines(keepends=True)
        if lines:
            parts.append(f"\nSOURCE {name}:1-{len(lines)}\n" + "".join(f"{index}: {line}" for index, line in enumerate(lines, 1)))
    rendered = "\n".join(parts)
    return rendered, {"source_sha256": snapshot["source_sha256"], "files": rows,
                      "total_bytes": sum(row["bytes"] for row in rows), "rendered_chars": len(rendered),
                      "rendered_sha256": digest(rendered.encode("utf-8"))}


def count_contracts(value):
    counts = Counter()
    def visit(item):
        if isinstance(item, dict):
            for key, child in item.items():
                if key in {"demand_transfer", "input_contract"}:
                    counts[key] += 1
                visit(child)
        elif isinstance(item, list):
            for child in item:
                visit(child)
    visit(value)
    return dict(counts)


def audit_call(path, rendered_source):
    row = {"call": path.relative_to(RUN).as_posix()}
    prompt_file = path / "prompt.txt"
    if not prompt_file.is_file():
        row["status"] = "prompt_not_published"
        return row
    prompt = prompt_file.read_bytes().decode("utf-8")
    row["prompt_chars"] = len(prompt)
    source_marker = "\n\nRELATED SOURCE\n"
    if source_marker in prompt:
        start = prompt.index(source_marker) + len(source_marker)
        row["complete_source_exact_match"] = prompt[start:start+len(rendered_source)] == rendered_source
    else:
        row["complete_source_exact_match"] = False
    logical = None
    if INPUT_MARKER in prompt:
        encoded, _ = json.JSONDecoder().raw_decode(prompt[prompt.index(INPUT_MARKER)+len(INPUT_MARKER):])
        logical = expand_processing_material(encoded)
        blocks = logical.get("cfg", {}).get("blocks", {})
        current_ids = [ir["id"] for block in (blocks.values() if isinstance(blocks, dict) else blocks)
                       for ir in block.get("instructions", [])]
        row["input"] = {"format": encoded["format"], "encoded_chars": len(compact(encoded)),
                        "expanded_chars": len(compact(logical)), "logical_sha256": encoded["logical_sha256"],
                        "top_level_keys": list(logical), "document_keys": list(logical.get("documents", {})),
                        "cfg_ir_count": len(current_ids), "cfg_distinct_ir_count": len(set(current_ids)),
                        "field_chars": {key: len(compact(value)) for key, value in logical.items()}}
        repair = logical.get("repair_context") or {}
        if repair:
            row["input"]["previous_fragment_contracts"] = count_contracts(repair.get("previous_fragment"))
            row["input"]["source_recheck_count"] = len(repair.get("source_rechecks", []))
        if "correction" in logical:
            correction = logical["correction"]
            row["input"]["correction"] = {"keys": list(correction),
                "diagnostic_count": len(correction.get("diagnostics", [])),
                "complete_candidate_chars": len(compact(correction["candidate"])) if "candidate" in correction else None,
                "selected_record_count": len(correction["records"]) if "records" in correction else None}
    response_file = path / "response.json"
    if not response_file.is_file():
        row["response"] = {"status": "no_saved_complete_response"}
    else:
        raw = read(response_file)
        raw_chars = len(raw) if isinstance(raw, str) else len(compact(raw))
        output = {"raw_response_chars": raw_chars, "saved_response_file_bytes": response_file.stat().st_size}
        try:
            # An invalid response has no canonical compact or expanded size.
            # Preserve its raw text and fail before any last-wins projection.
            parsed = json.loads(raw, object_pairs_hook=unique_object) if isinstance(raw, str) else raw
            output["compact_response_chars"] = len(compact(parsed))
            output["format_choice"] = "shared" if isinstance(parsed, dict) and parsed.get("format") == PROCESSING_WIRE_IDENTITY else "plain"
            expanded = expand_processing_response(raw)
            output["expanded_chars"] = len(compact(expanded))
            output["shared_definition_count"] = len(parsed.get("shared_values", {})) if output["format_choice"] == "shared" else 0
            output["response_form"] = "replacements" if "replacements" in expanded else "complete_fragment"
            output["contract_occurrences"] = count_contracts(expanded)
            candidate = expanded
            if (path / "merged-candidate.json").is_file():
                candidate = read(path / "merged-candidate.json")
                output["candidate_origin"] = "program_saved_merged_candidate"
            else:
                output["candidate_origin"] = "decoded_saved_response"
            modeled = candidate.get("ir_semantics", {})
            gaps = candidate.get("processing_gaps", [])
            output["candidate_modeled_ir_count"] = len(modeled) if isinstance(modeled, dict) else None
            output["candidate_gap_count"] = len(gaps) if isinstance(gaps, list) else None
            output["candidate_contract_occurrences"] = count_contracts(candidate)
            if logical is not None and isinstance(modeled, dict) and isinstance(gaps, list):
                unmodeled = {gap.get("instruction_id") for gap in gaps if isinstance(gap, dict) and gap.get("unmodeled")}
                output["inventory_only_missing_current_ids"] = sorted(set(current_ids) - set(modeled) - unmodeled)
                output["inventory_only_extra_modeled_ids"] = sorted(set(modeled) - set(current_ids))
        except (ValueError, TypeError, KeyError) as error:
            output["codec_error"] = {"type": type(error).__name__, "message": str(error)}
        row["response"] = output
    for name in ("validation.json", "normalization.json"):
        if (path / name).is_file():
            value = read(path / name)
            if name == "validation.json":
                diagnostics = value.get("diagnostics", [])
                row["saved_validation"] = {"status": value.get("status"), "diagnostic_count": len(diagnostics),
                    "diagnostic_codes": dict(Counter(item.get("code", "unknown") for item in diagnostics))}
            else:
                row["saved_normalization"] = value
    return row


def main():
    rendered, source = frozen_source()
    result = {"observed_at": datetime.now(timezone.utc).isoformat(), "run": RUN.relative_to(ROOT).as_posix(),
              "method": "Passive JSON/text parsing and exact presentation-codec expansion only; no stage validation, model call, backend run or replay.",
              "limits": "Character and inventory statistics are not token savings, semantic correctness, reached coverage or pure generation time.",
              "source": source, "processing_calls": []}
    for name in ("processing", "revision-processing"):
        for path in sorted((RUN / "steps" / name / "calls").glob("a*")):
            if path.is_dir():
                result["processing_calls"].append(audit_call(path, rendered))
    target = OUT / "presentation-audit" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + ".json")
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(compact({"report": target.relative_to(ROOT).as_posix(), "processing_calls": len(result["processing_calls"]),
                   "source_files": len(source["files"]), "source_bytes": source["total_bytes"]}))


if __name__ == "__main__":
    main()
