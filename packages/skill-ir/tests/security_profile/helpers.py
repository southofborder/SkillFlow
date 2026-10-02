"""Small explicit fixtures for security-profile engineering contracts."""

from copy import deepcopy
import hashlib
import json

from skill_ir.security_profile.evidence import prepare_material
from skill_ir.source_evidence import _digest


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


def profile(material, instruction_id, *, operator=(), roles=(), effects=()):
    entry = material["instruction_index"][instruction_id]
    instruction = material["cfg"]["blocks"][entry["block_id"]]["instructions"][entry["position"]]
    result = {"operator": list(operator), "roles": list(roles), "effects": list(effects), "evidences": []}
    for field in ("operator", "roles", "effects"):
        for index, value in enumerate(result[field] or [None]):
            result["evidences"].append({
                "field": field, "value": value, "basis": "cfg", "ref_id": entry["ref_id"],
                "quote": instruction["opcode"], "reason": "依据当前动作进行局部分类；无标签时明确不适用。",
                "effect_index": index if field == "effects" and value is not None else None,
            })
    return result


def valid_response(material):
    """Compiled fixture for final structure/evidence tests, not a model response."""
    specs = {
        "ir_read": {"operator": ["agent_runtime"], "roles": ["source"], "effects": ["fs_read"]},
        "ir_filter": {"operator": ["agent_runtime"], "roles": ["transformer"], "effects": ["transform"]},
        "ir_return": {"operator": ["agent_runtime"], "roles": [], "effects": []},
    }
    return with_specs(material, {"profiles": {
        instruction_id: profile(material, instruction_id, **specs.get(instruction_id, {}))
        for instruction_id in material["instruction_index"]
    }, "outcome": "completed"})


def valid_raw_response(material):
    """Explicit local fixture for the model protocol; compiled observations absent.

    This fixture describes the supplied configuration-read/local-filter graph.
    It is not a migration or an inference from arbitrary effect labels.
    """
    response = valid_response(material)
    response.pop("sink_boundaries")
    for spec in response["transfer_specs"].values():
        spec.pop("precedence")
    for ir_id in ("ir_read", "ir_filter"):
        if ir_id not in response["transfer_specs"]:
            continue
        spec = response["transfer_specs"][ir_id]
        events = spec["events"]
        spec["events"] = [{"kind": "processing", "mode": "local", "returns": [],
                           "events": events,
                           "evidences": deepcopy(events[0]["atomic_ops"][0]["evidences"])}]
    return response


def with_specs(material, response):
    """Explicit test-only symbolic fixtures, never a production migration.

    Labels in these engineering fixtures are deliberate inputs, not an oracle
    or an implementation of deriving operations from arbitrary effect labels.
    """
    response["outcome"] = "completed"
    response["locations"] = {}
    response["location_evidences"] = {}
    response["transfer_specs"] = {}
    kinds = {"context_read": "runtime_context", "context_write": "runtime_context",
             "fs_read": "storage", "fs_write": "storage", "net_send": "remote",
             "net_receive": "remote", "model_observe": "model_context", "user_output": "user"}
    for ir_id, item in response["profiles"].items():
        if ir_id not in material["instruction_index"]:
            continue
        entry = material["instruction_index"][ir_id]
        ir = material["cfg"]["blocks"][entry["block_id"]]["instructions"][entry["position"]]
        evidence = {"basis": "cfg", "ref_id": entry["ref_id"], "quote": ir["opcode"],
                    "reason": "离线注入的符号传播说明，仅验证工程契约。"}
        latest = {"kind": "input", "index": 0} if ir.get("inputs") else {"kind": "literal", "value": None}
        if ir.get("inputs") and ir["inputs"][0]["type"] == "external_resource":
            latest = {"kind": "literal", "value": ir["inputs"][0]["identifier"]}
        events = []
        for index, effect in enumerate(item["effects"]):
            if effect in kinds:
                location = f"{ir_id}_boundary_{index}"
                operand_refs = ([{"instruction_id": ir_id, "side": "input", "index": 0}]
                                if ir.get("inputs") else [])
                response["locations"][location] = {"kind": kinds[effect], "name": location,
                                                    "operand_refs": operand_refs,
                                                    "access_scope": "task" if kinds[effect] in {"runtime_context", "storage"} else "recipient",
                                                    "retention": "persistent" if kinds[effect] == "storage" else "task" if kinds[effect] == "runtime_context" else None}
                response["location_evidences"][location] = [deepcopy(evidence)]
            output = f"stage_{index}"
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
            events.append({"effect_index": index, "atomic_ops": [operation]})
        response["transfer_specs"][ir_id] = {
            "order": "fixed", "precedence": [],
            "events": events,
            "output_bindings": [{"output_index": index, "value": deepcopy(latest), "evidences": [deepcopy(evidence)]}
                                for index, _ in enumerate(ir.get("outputs", []))],
        }
    from skill_ir.security_profile.boundaries import derive_sink_boundaries
    response["sink_boundaries"] = [item.model_dump(mode="json") for item in
        derive_sink_boundaries(response["locations"], response["transfer_specs"], response["profiles"])]
    return response


class FakeClient:
    def __init__(self, response=None):
        self.response = response
        self.prompts = []

    def complete(self, prompt):
        self.prompts.append(prompt)
        material = json.loads(prompt.split("\nINPUT_JSON\n", 1)[1])
        return deepcopy(self.response if self.response is not None else valid_raw_response(material))


def material():
    return prepare_material(source_bundle(), graph())
