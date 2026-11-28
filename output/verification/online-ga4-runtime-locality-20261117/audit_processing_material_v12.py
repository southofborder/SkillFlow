"""Passive saved-byte audit only; no project imports, model or stage execution."""
import ast
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
VERIFY = Path(__file__).resolve().parent
RUN = ROOT / "experiments/doe/runs/document-guided-ga4-runtime-locality-high-20261117-205158"


def sha(value):
    return hashlib.sha256(value).hexdigest()


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON member in saved material: " + key)
        result[key] = value
    return result


def read(path):
    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def expand(display):
    """Decode only the saved input presentation; never validate stage semantics."""
    assert display["format"] == "skillflow-review-display-v1"
    columns, definitions = display["record_columns"], display["shared_values"]
    cache, visiting = {}, set()

    def visit(value):
        if isinstance(value, list):
            return [visit(child) for child in value]
        if not isinstance(value, dict):
            return value
        markers = {"$ref", "$rows", "$literal_object"} & value.keys()
        if not markers:
            return {key: visit(child) for key, child in value.items()}
        assert len(value) == len(markers) == 1
        marker = next(iter(markers))
        body = value[marker]
        if marker == "$ref":
            assert body in definitions and body not in visiting
            if body not in cache:
                visiting.add(body)
                cache[body] = visit(definitions[body])
                visiting.remove(body)
            return deepcopy(cache[body])
        body = visit(body)
        if marker == "$literal_object":
            return unique(body)
        result = []
        for row in body:
            shape = columns[row[0]]
            assert len(row) == len(shape) + 1
            result.append(unique(zip(shape, row[1:])))
        return result

    for name in definitions:
        visit({"$ref": name})
    return visit(display["payload"])


def main():
    step = RUN / "steps/processing"
    prompt_bytes = (step / "prompt.txt").read_bytes()
    prompt = prompt_bytes.decode("utf-8")
    marker = "\nPROCESSING_INPUT_JSON\n"
    start = prompt.index(marker) + len(marker)
    envelope, length = json.JSONDecoder(object_pairs_hook=unique).raw_decode(prompt[start:])
    logical = expand(envelope["display"])
    logical_text = compact(logical)
    assert sha(logical_text.encode()) == envelope["logical_sha256"]
    assert envelope["format"] == "skillflow-processing-input-display-v1"
    snapshot = read(RUN / "source/inputs/snapshot.json")
    rows, segments, source_texts = [], [], []
    for item in snapshot["files"]:
        data = (RUN / "source/inputs/package" / item["path"]).read_bytes()
        text = data.decode("utf-8")
        assert sha(data) == item["raw_sha256"]
        assert sha(text.encode()) == item["decoded_sha256"]
        lines = text.splitlines(keepends=True)
        name = "skill/" + item["path"]
        segment = f"\nSOURCE {name}:1-{len(lines)}\n" + "".join(
            f"{index}: {line}" for index, line in enumerate(lines, 1))
        rows.append({"file": name, "physical_lines": len(lines), "chars": len(text),
                     "sha256": sha(data), "rendered_segment_count": prompt.count(segment)})
        source_texts.append(text)
        segments.append(segment)
    expected_source = "\n".join(["File navigation (not proof of semantic coverage):", *[
        f"- {row['file']} ({row['physical_lines']} physical lines)" for row in rows], *segments])
    actual_source = prompt.split("RELATED SOURCE\n", 1)[1].split("\n\nOUTPUT REQUIREMENTS\n", 1)[0]
    assert actual_source == expected_source
    graph_artifact = read(RUN / "graph/initial.json")
    cfg = graph_artifact.get("cfg", graph_artifact)
    displayed_cfg = deepcopy(cfg)
    omitted = 0
    for block in displayed_cfg["blocks"].values():
        for ir in block["instructions"]:
            metadata = ir.get("metadata", {})
            code = metadata.get("script_content")
            if isinstance(code, str) and code and any(code in text for text in source_texts):
                metadata.pop("script_content")
                omitted += 1
    assert logical["cfg"] == displayed_cfg
    tree = ast.parse((ROOT / "src/skillflow/propagation/contracts/runtime_contract.py").read_bytes())
    abstraction = ast.parse((ROOT / "src/skillflow/common/abstraction.py").read_bytes())
    boundary = next(ast.literal_eval(node.value) for node in abstraction.body
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "BOUNDARY_GRANULARITY" for target in node.targets))

    class ConstantReference(ast.NodeTransformer):
        def visit_Name(self, node):
            if node.id == "BOUNDARY_GRANULARITY":
                return ast.Constant(value=boundary)
            return node

    tree = ConstantReference().visit(tree)
    constants = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in {"CONTRACT_VERSION", "_RULES", "_OPERATION_CONTRACT"}:
                    constants[target.id] = ast.literal_eval(node.value)
    expected_contract = {"version": constants["CONTRACT_VERSION"],
        "rules": [{"id": identity, "text": text} for identity, text in constants["_RULES"]],
        "operation_contract": constants["_OPERATION_CONTRACT"]}
    contract = logical["runtime_contract"]
    assert contract == expected_contract
    inventory = contract["operation_contract"]
    prefix = prompt[:prompt.index("RELATED SOURCE\n")]
    output_instructions = prompt.split("\n\nOUTPUT REQUIREMENTS\n", 1)[1]
    call = read(step / "calls/a001/call.json")
    comparison = len(prompt) - length + len(logical_text)
    report = {
        "audit": "passive_processing_input_v12", "created_at": datetime.now(timezone.utc).isoformat(),
        "run_directory": RUN.relative_to(ROOT).as_posix(), "stage": "initial_processing",
        "method": "Saved bytes, strict JSON pair parsing, input-display expansion and AST literal comparison only; no project import, semantic validation, compiler, backend, model, Skill or replay execution.",
        "bindings": {"prompt_sha256": sha(prompt_bytes), "step_manifest_sha256": sha((step / "manifest.json").read_bytes()),
            "cfg_sha256": sha((RUN / "graph/initial.json").read_bytes()), "logical_sha256": envelope["logical_sha256"]},
        "input": {"stage_prompt_chars": len(prompt), "stage_prompt_utf8_bytes": len(prompt_bytes),
            "display_envelope_chars": length, "logical_payload_chars": len(logical_text),
            "same_material_prompt_with_literal_payload_chars": comparison,
            "display_only_saving_chars": comparison - len(prompt),
            "display_only_saving_percent": round(100 * (comparison - len(prompt)) / comparison, 4),
            "logical_fields": list(logical), "documents_fields": list(logical["documents"]),
            "source_chars": sum(row["chars"] for row in rows), "rendered_source_chars": len(actual_source),
            "full_source_exact": actual_source == expected_source, "source_files": rows,
            "source_complete_file_count": len(rows), "script_content_duplicate_copies_removed": omitted,
            "cfg_equals_exact_source_deduplicated_original": logical["cfg"] == displayed_cfg,
            "cfg_blocks": len(cfg["blocks"]), "cfg_ir": sum(len(block["instructions"]) for block in cfg["blocks"].values()),
            "task_object_absent": "task" not in logical and "task" not in logical["documents"],
            "sealed_task_marker_absent": "SEALED_TASK\n" not in prefix + output_instructions},
        "runtime": {"version": contract["version"], "exact_current_frozen_contract": contract == expected_contract,
            "rule_ids": [row["id"] for row in contract["rules"]], "operation_rows": inventory["rows"],
            "operation_count": len(inventory["rows"]),
            "expression_inventory": inventory["expression_operators"],
            "inventory_keys": list(inventory), "address_guidance": [row for row in contract["rules"] if row["id"] == "EM08"],
            "output_schema_has_address_kind": "address_kind" in output_instructions,
            "output_schema_has_address_reason": "address_reason" in output_instructions},
        "snapshot_status": {"initial_call_status": call.get("status"), "response_saved": (step / "calls/a001/response.json").exists(),
            "validation_saved": (step / "calls/a001/validation.json").exists(), "stage_result_saved": (step / "result.json").exists()},
        "limits": ["This establishes delivered material identity and completeness, not model comprehension, source-faithful annotations or accepted review.",
            "The payload equality comparison includes the pre-existing exact-source script_content deduplication; it is not raw CFG artifact equality.",
            "The character comparison changes only the actual input presentation; it is not historical latency, output-compression or cost evidence.",
            "The stage prompt is separate from any transport delivery wrapper."]}
    path = VERIFY / "processing-input-v12-audit.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(compact({"report": str(path), "input": {k: v for k, v in report["input"].items() if k != "source_files"},
        "runtime_version": contract["version"], "operation_count": len(inventory["rows"]), "inventory_keys": list(inventory),
        "snapshot_status": report["snapshot_status"]}))


if __name__ == "__main__":
    main()
