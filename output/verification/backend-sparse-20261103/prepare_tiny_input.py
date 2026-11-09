"""Prepare an English synthetic harness input; never evaluate a Skill or model."""
import hashlib
import json
from pathlib import Path

from skillflow.common.source_evidence import _digest
from skillflow.propagation.contracts.task import validate_task_candidate
from skillflow.propagation.material import prepare_material
from skillflow.document_guided.annotation_wire import compile_flat_response
from skillflow.propagation.annotation.services import to_payload


text = "Build a record with a Boolean flag and return that record.\n"
source = {"files": [{"path": "SKILL.md", "content": text, "sha256": hashlib.sha256(text.encode()).hexdigest()}]}
source["source_sha256"] = _digest([{key: item[key] for key in ("path", "sha256")} for item in source["files"]])
evidence = {"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
            "reason": "The synthetic source states the complete small harness operation."}
task = validate_task_candidate({"purpose": {"text": "Return the stated record.", "evidences": [evidence]},
    "requirements": [{"id": "R", "text": "Return a record with a Boolean flag.", "evidences": [evidence]}],
    "issues": []}, source_files={"skill/SKILL.md": text}, source_sha256=source["source_sha256"])
cfg = {"entry_block_id": "main", "blocks": {"main": {"block_id": "main", "block_name": "Small fixture",
    "instructions": [{"id": "ir_build", "opcode": "build_flag", "inputs": [],
                      "outputs": [{"type": "result", "identifier": "row"}]},
                     {"id": "ir_return", "opcode": "return", "inputs": [{"type": "result", "identifier": "row"}],
                      "outputs": []}]}}, "edges": []}
material = prepare_material(source, cfg, task_baseline=task)
wire = {"outcome": "completed", "realizations": [{"requirement_id": "R", "gaps": [{
    "reason": "The harness fixture does not claim a complete preservation-demand mapping.", "evidences": [evidence]}]}], "demands": [], "expressions": [],
    "locations": {}, "ir_semantics": {
        "ir_build": {"evidences": [evidence], "segments": [{"mode": "local", "returns": [], "ops": [
            {"op": "build", "container": "object", "parts": [{"path": ["flag"],
                "value": {"kind": "literal", "value": True}}], "output": "row"}]}],
            "output_bindings": [{"output_index": 0, "value": {"kind": "local", "name": "row"}}]},
        "ir_return": {"evidences": [evidence], "segments": [], "output_bindings": []}}}
saved, raw, compiled, mapping = compile_flat_response(wire, material)
value = {"material": material, "raw_annotation": raw, "wire_annotation": saved,
         "compiled_annotation": compiled, "mapping": mapping, "payload": to_payload(compiled),
         "task": material["task"], "source_metadata": {}}
path = Path(__file__).resolve().parent / "tiny-fixed-input.json"
if path.exists():
    raise ValueError("tiny input already exists")
path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"output": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "instructions": 2}))
