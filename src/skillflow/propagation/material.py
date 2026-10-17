"""Frozen source, graph, optional user request and one runtime contract."""
from __future__ import annotations
from copy import deepcopy
import json
from typing import Any
from pydantic import TypeAdapter
from skillflow.common.source_evidence import _checked_source, _digest, extract_source_lines, source_lines
from skillflow.common.validation import structural_error
from skillflow.graph.validation import checked_cfg
from skillflow.propagation.contracts.runtime_contract import runtime_contract, validate_runtime_contract
from skillflow.propagation.contracts.profiles import SCHEMA_VERSION
from skillflow.propagation.contracts.references import cfg_instructions, resolve_cfg_target


def prepare_material(source, cfg, *, task_baseline, user_request=None):
    if user_request is not None and (type(user_request) is not str or not user_request.strip()):
        raise ValueError("user_request must be nonempty text or null")
    source = _checked_source(deepcopy(source))
    from skillflow.propagation.contracts.task import checked_task, task_source_files
    task = checked_task(task_baseline, source_files=task_source_files(source, user_request=user_request),
                        source_sha256=source["source_sha256"])
    cfg = checked_cfg(cfg)
    if not cfg_instructions(cfg):
        raise ValueError("annotation requires at least one actual instruction")
    return {"version": SCHEMA_VERSION, "source": source, "cfg": cfg,
            "runtime_contract": runtime_contract(), "user_request": user_request,
            "task": task.model_dump(mode="json") if hasattr(task, "model_dump") else task}


def checked_material(material):
    if type(material) is not dict or set(material) != {"version", "source", "cfg", "runtime_contract", "user_request", "task"}:
        raise ValueError("material must contain the exact current input fields")
    validate_runtime_contract(material["runtime_contract"])
    prepared = prepare_material(material["source"], material["cfg"], task_baseline=material["task"], user_request=material["user_request"])
    if _digest(prepared) != _digest(material):
        raise ValueError("prepared material schema or runtime rules differ")
    return prepared


def evidence_reference(evidence, material):
    """Validate one direct location and extract original content, never model quotes."""
    from skillflow.propagation.contracts.evidence import SpecEvidence
    from skillflow.propagation.contracts.joint import joint_source_files
    if hasattr(evidence, "model_dump"):
        evidence = evidence.model_dump(mode="json")
    evidence = {key: value for key, value in evidence.items() if key != "value"}
    typed = TypeAdapter(SpecEvidence).validate_python(evidence)
    if hasattr(typed, "file"):
        files = joint_source_files(material)
        if typed.file not in files:
            raise structural_error("evidence_file", "/file", "evidence file is not in the frozen source table")
        try:
            text = extract_source_lines(files[typed.file], typed.start_line, typed.end_line)
        except ValueError as error:
            raise structural_error("evidence_span", "", str(error)) from error
        return {"kind": "source", "file": typed.file, "start_line": typed.start_line,
                "end_line": typed.end_line, "text": text}
    if hasattr(typed, "target"):
        try:
            resolved = resolve_cfg_target(typed.target, material["cfg"])
        except ValueError as error:
            raise structural_error("evidence_target", "/target", str(error)) from error
        return {**resolved, "target_kind": resolved["kind"], "kind": "cfg",
                "text": json.dumps(resolved["value"], ensure_ascii=False, separators=(",", ":"), allow_nan=False)}
    rules = {rule["id"]: rule["text"] for rule in material["runtime_contract"]["rules"]}
    if typed.rule_id not in rules:
        raise structural_error("evidence_rule", "/rule_id", "runtime rule does not exist: " + typed.rule_id)
    return {"kind": "runtime_contract", "rule_id": typed.rule_id, "text": rules[typed.rule_id]}


def check_evidence(evidence, material):
    evidence_reference(evidence, material)


def model_material(material):
    """One graph and readable source; no persisted or transmitted CFG target table."""
    from skillflow.propagation.contracts.joint import joint_source_files
    prepared = checked_material(material)
    return {"source": {"files": [{"file": path, "lines": source_lines(text)}
                                  for path, text in joint_source_files(prepared).items() if path.startswith("skill/")]},
            "cfg": prepared["cfg"], "runtime_contract": prepared["runtime_contract"],
            "user_request": prepared["user_request"], "task": prepared["task"]}


def compact_schema(schema):
    """Remove display-only schema titles without weakening validation keywords."""
    schema_maps = {"properties", "patternProperties", "$defs", "definitions", "dependentSchemas"}
    def visit(value, *, schema_object=True):
        if isinstance(value, list):
            return [visit(item) for item in value]
        if isinstance(value, dict):
            result = {}
            for key, child in value.items():
                if schema_object and key == "title":
                    continue
                # Property names (including a real field called 'title') are
                # mapping keys, not removable schema annotations.
                if schema_object and key in schema_maps:
                    result[key] = {name: visit(item) for name, item in child.items()}
                elif schema_object and key in {"const", "enum", "default", "examples"}:
                    result[key] = deepcopy(child)
                else:
                    result[key] = visit(child)
            return result
        return value
    return visit(schema)
