"""Small explicit fixtures for security-profile engineering contracts."""

from copy import deepcopy
import hashlib
import json

from skillflow.propagation.material import prepare_material as _prepare_material
from skillflow.propagation.contracts.references import cfg_instructions
from skillflow.common.source_evidence import _digest


def source_bundle(content=None):
    content = content if content is not None else (
        "# 配置处理\n\n读取配置文件 config.json，仅在本地筛选字段。\n"
        "禁止泄露密钥。返回内部结果，不直接向用户展示。\n"
    )
    files = [{"path": "SKILL.md", "content": content,
              "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest()}]
    return {"files": files, "source_sha256": _digest([
        {key: item[key] for key in ("path", "sha256")} for item in files
    ])}


def graph():
    return {
        "entry_block_id": "entry",
        "constraints": ["禁止泄露密钥。"],
        "blocks": {"entry": {
            "block_id": "entry", "block_name": "配置处理",
            "instructions": [
                {"id": "ir_read", "opcode": "read_local_config",
                 "inputs": [{"type": "external_resource", "identifier": "config.json"}],
                 "outputs": [{"type": "result", "identifier": "result_config"}],
                 "constraints": [], "metadata": {"local": True, "nested": [None, {}, [], 1, 1.5]}},
                {"id": "ir_filter", "opcode": "select_fields_locally",
                 "inputs": [{"type": "result", "identifier": "result_config"}],
                 "outputs": [{"type": "result", "identifier": "result_selected"}],
                 "constraints": [], "metadata": {}},
                {"id": "ir_return", "opcode": "return",
                 "inputs": [{"type": "result", "identifier": "result_selected"}],
                 "outputs": [], "constraints": [], "metadata": {}},
            ],
            "constraints": [], "data_source_kind": None,
        }},
        "edges": [], "declared_context_keys": [],
    }


def semantics(material, instruction_id, *, operator=(), effects=()):
    """Explicit complete IR fixture, including its only ordered effect list."""
    ir = cfg_instructions(material["cfg"])[instruction_id]
    evidence = {"target": {"instruction_id": instruction_id, "path": []}, "reason": "Explicit engineering fixture; location validity is not semantic proof."}
    latest = {"kind": "input", "index": 0} if ir.get("inputs") else {"kind": "literal", "value": None}
    if ir.get("inputs") and ir["inputs"][0]["type"] == "external_resource":
        latest = {"kind": "literal", "value": ir["inputs"][0]["identifier"]}
    events = []
    for index, effect in enumerate(effects):
        location, output = f"{instruction_id}_boundary_{index}", f"stage_{index}"
        if effect in {"context_read", "fs_read"}:
            operation = {"op": "read", "location": location, "output": output}
            latest = {"kind": "local", "name": output}
        elif effect == "net_receive":
            operation = {"op": "receive", "location": location, "inputs": [deepcopy(latest)], "output": output}
            latest = {"kind": "local", "name": output}
        elif effect in {"net_send", "model_observe", "user_output"}:
            operation = {"op": "deliver", "inputs": [deepcopy(latest)], "target": location}
        elif effect in {"context_write", "fs_write"}:
            operation = {"op": "write", "target": location, "mode": "replace", "input": deepcopy(latest)}
        else:
            operation = {"op": "compute", "inputs": [deepcopy(latest)], "dependencies": ["derived"], "output": output}
            latest = {"kind": "local", "name": output}
        operation["evidences"] = [deepcopy(evidence)]
        events.append({"effect": effect, "evidences": [deepcopy(evidence)], "atomic_ops": [operation]})
    result = {"operator": list(operator),
              "operator_evidences": [{**evidence, "value": value} for value in list(operator) or [None]],
              "order": "fixed", "precedence": [], "events": events, "sensitivity": [],
              "output_bindings": [{"output_index": index, "value": deepcopy(latest), "evidences": [deepcopy(evidence)]}
                                  for index, _ in enumerate(ir.get("outputs", []))]}
    if not effects:
        result["empty_effect_evidences"] = [deepcopy(evidence)]
    return result


def effects_of(spec):
    """Read effect occurrences from the actual timeline, including scope bodies."""
    values = []
    def visit(events):
        for event in events:
            if event.get("kind") == "for_each": visit(event["body"])
            elif event.get("kind") == "processing": visit(event["events"])
            elif event["effect"] is not None: values.append(event["effect"])
    visit(spec["events"])
    return values


def valid_response(material):
    """Compiled fixture for final structure/evidence tests, not a model response."""
    specs = {
        "ir_read": {"operator": ["agent_runtime"], "effects": ["fs_read"]},
        "ir_filter": {"operator": ["agent_runtime"], "effects": ["transform"]},
        "ir_return": {"operator": ["agent_runtime"], "effects": []},
    }
    return with_specs(material, {"ir_semantics": {
        instruction_id: semantics(material, instruction_id, **specs.get(instruction_id, {}))
        for instruction_id in cfg_instructions(material["cfg"])
    }, "outcome": "completed"})


def valid_raw_response(material):
    """Explicit local fixture for the model protocol; compiled observations absent.

    This fixture describes the supplied configuration-read/local-filter graph.
    It is not a migration or an inference from arbitrary effect labels.
    """
    response = valid_response(material)
    response.pop("sink_boundaries")
    response.pop("task_ref")
    response["task_revision_id"] = material["task"]["task_sha256"]
    response["demands"] = []
    response["expressions"] = []
    for spec in response["ir_semantics"].values():
        spec.pop("precedence")
    for ir_id in ("ir_read", "ir_filter"):
        if ir_id not in response["ir_semantics"]:
            continue
        spec = response["ir_semantics"][ir_id]
        events = spec["events"]
        spec["events"] = [{"kind": "processing", "mode": "local", "returns": [],
                           "events": events,
                           "evidences": deepcopy(events[0]["atomic_ops"][0]["evidences"])}]
    return response


def authored_task(source, *, user_request=None):
    """Explicit synthetic declaration for engineering fixtures, not model extraction."""
    from skillflow.propagation.contracts.task import task_source_files, validate_task_candidate
    files = task_source_files(source, user_request=user_request)
    primary = "task/user-request.txt" if user_request is not None else next(iter(files))
    evidence = {"file": primary, "start_line": 1, "end_line": len(files[primary].splitlines()),
                "reason": "此人工工程样例声明保持原文结果；不作为真实模型语义表现。"}
    candidate = {"purpose": {"text": "Preserve the stated fixture result.", "evidences": [evidence]},
        "requirements": [{"id": "R001", "text": "Preserve the stated fixture result and limitations.", "evidences": [evidence]}],
        "source_accounting": [{"file": name, "start_line": 1, "end_line": len(text.splitlines()),
            "disposition": "requirement", "requirement_ids": ["R001"], "issue_ids": [],
            "reason": "完整人工样例源文登记，不声称语义完备。"} for name,text in files.items() if text.strip()], "issues": []}
    return validate_task_candidate(candidate, source_files=files, source_sha256=source["source_sha256"],
                                   basis="user_request" if user_request is not None else "declared_skill")


def prepared_material(source, cfg, *, user_request=None, task_baseline=None, **kwargs):
    return _prepare_material(source, cfg, user_request=user_request,
        task_baseline=task_baseline or authored_task(source, user_request=user_request), **kwargs)


prepare_material = prepared_material


def with_task_semantics(material, response, *, raw=False):
    """Complete explicit engineering metadata, never a production parser."""
    from skillflow.propagation.contracts.task import task_reference
    if raw:
        response.setdefault("task_revision_id", material["task"]["task_sha256"])
    else:
        response.setdefault("task_ref", task_reference(material["task"]))
    response.setdefault("realizations", [{"requirement_id": row["id"], "status": "unmapped", "bindings": [],
        "gaps": [{"reason": "人工工程样例未声明需求起点。", "evidences": row["evidences"]}]}
        for row in material["task"]["requirements"]])
    response.setdefault("demands", [])
    response.setdefault("expressions", [])
    for spec in response["ir_semantics"].values():
        spec.setdefault("sensitivity", [])
        for event in spec["events"]:
            if event.get("kind") == "for_each":
                event.setdefault("sensitivity", [])
    return response


def with_specs(material, response):
    """Complete explicit fixture boundary declarations; never parse old schemas."""
    raw_semantics = "task_revision_id" in response
    response["outcome"] = "completed"
    response["locations"] = {}
    response["location_evidences"] = {}
    kinds = {"context_read": "runtime_context", "context_write": "runtime_context",
             "fs_read": "storage", "fs_write": "storage", "net_send": "remote",
             "net_receive": "remote", "model_observe": "model_context", "user_output": "user"}
    for ir_id, spec in response["ir_semantics"].items():
        if ir_id not in cfg_instructions(material["cfg"]):
            continue
        ir = cfg_instructions(material["cfg"])[ir_id]
        for event in spec["events"]:
            for operation in event.get("atomic_ops", []):
                location = operation.get("target", operation.get("location"))
                if location is None: continue
                kind = kinds[event["effect"]]
                response["locations"][location] = {"kind": kind, "name": location,
                    "operand_refs": [{"instruction_id": ir_id, "side": "input", "index": 0}] if ir.get("inputs") else [],
                    "access_scope": "task" if kind in {"runtime_context", "storage"} else "recipient",
                    "retention": "persistent" if kind == "storage" else "task" if kind == "runtime_context" else None}
                response["location_evidences"][location] = deepcopy(operation["evidences"])
    from skillflow.propagation.contracts.boundaries import derive_sink_boundaries
    response["sink_boundaries"] = [item.model_dump(mode="json") for item in
        derive_sink_boundaries(response["locations"], response["ir_semantics"])]
    return with_task_semantics(material, response, raw=raw_semantics)


def material_from_prompt(prompt):
    """Reconstruct fixture inputs from the exact compact request reading view."""
    payload = json.JSONDecoder().raw_decode(prompt.split("\nINPUT_JSON\n", 1)[1])[0]
    return material_from_model_payload(payload)


def material_from_model_payload(payload):
    """Rebuild checked fixture material, not a production wire compatibility path."""
    source, task = [], payload["user_request"]
    for entry in payload["source"]["files"]:
        path, content = entry["file"], "".join(entry["lines"])
        if path.startswith("skill/"):
            source.append({"path": path[6:], "content": content,
                           "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest()})
    bundle = {"files": source, "source_sha256": _digest([
        {key: item[key] for key in ("path", "sha256")} for item in source])}
    return prepare_material(bundle, payload["cfg"], user_request=task, task_baseline=payload["task"])


class FakeClient:
    def __init__(self, response=None):
        self.response = response
        self.prompts = []

    def complete(self, prompt):
        self.prompts.append(prompt)
        if "COMPLETE_ORIGINAL_SOURCE\n\n" in prompt:
            # Explicitly authored test output, not a model-quality measurement.
            view = json.JSONDecoder().raw_decode(prompt.split("COMPLETE_ORIGINAL_SOURCE\n\n", 1)[1])[0]
            source_rows, user_request = [], None
            for entry in view["source_files"]:
                text = "".join(entry["lines"])
                if entry["file"] == "task/user-request.txt":
                    user_request = text
                else:
                    source_rows.append({"path": entry["file"][6:], "content": text,
                        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()})
            bundle = {"files": source_rows, "source_sha256": _digest([
                {key: row[key] for key in ("path", "sha256")} for row in source_rows])}
            task = authored_task(bundle, user_request=user_request).model_dump(mode="json")
            from skillflow.propagation.contracts.task import CandidateTask
            return {name: task[name] for name in CandidateTask.model_fields}
        material = material_from_prompt(prompt)
        return deepcopy(self.response if self.response is not None else valid_raw_response(material))


def material():
    return prepare_material(source_bundle(), graph())


def authored_task_run(source, *, run_dir, user_request=None):
    """Record one explicitly authored engineering baseline, without a remote model."""
    from pathlib import Path
    from skillflow.common.inputs.skill_package import load_skill_package
    from skillflow.task.runner import prepare_task_run, run_task
    if not isinstance(source, dict):
        package = load_skill_package(source)
        rows = [{"path": item.path, "content": item.content,
                 "sha256": hashlib.sha256(item.content.encode("utf-8")).hexdigest()}
                for item in package.readable_files()]
        source = {"files": rows, "source_sha256": _digest([
            {key: row[key] for key in ("path", "sha256")} for row in rows])}
    baseline = authored_task(source, user_request=user_request).model_dump(mode="json")
    from skillflow.propagation.contracts.task import CandidateTask
    declaration = {name: baseline[name] for name in CandidateTask.model_fields}
    class AuthoredClient:
        def complete(self, prompt):
            return deepcopy(declaration)
    prepare_task_run(run_dir, source, user_request=user_request)
    result = run_task(run_dir, client=AuthoredClient())
    assert result["status"] == "complete", result
    return Path(run_dir)


def authored_prepare_run(input, analysis, *, run_dir, task_run=None, **kwargs):
    """Test-only baseline injection; production callers must supply their Task owner."""
    from pathlib import Path
    from skillflow.propagation.annotation.runner import prepare_run as prepare
    source_path = None if input is None else Path(input).resolve()
    if source_path is not None and source_path.is_dir() and Path(run_dir).resolve().is_relative_to(source_path):
        raise ValueError("run directory must not be nested inside the Skill input")
    if task_run is None:
        task_run = Path(run_dir).with_name(Path(run_dir).name + "-task")
        if not task_run.exists():
            task_run = authored_task_run(input, run_dir=task_run, user_request=kwargs.get("user_request"))
    return prepare(input, analysis, run_dir=run_dir, task_run=task_run, **kwargs)
