"""Chinese records of annotations; no risk or necessity judgments."""
from __future__ import annotations

import json

STATUS_LABELS = {"complete": "标注记录完整", "incomplete": "存在未决标注",
                 "input_error": "输入错误", "invalid_response": "响应无效",
                 "execution_error": "调用执行错误", "interrupted": "已中断"}


def _cell(value):
    return str(value).replace("|", "\\|").replace("\r", "").replace("\n", "<br>")


def _effect_steps(profile, uncertain=False):
    steps = "<br>".join(
        f"{index + 1}. {effect}" + ("（上下文写入）" if effect == "context_write" else "")
        for index, effect in enumerate(profile["effects"])
    ) or "[]（无已记录效果；不等于空操作，请结合证据与未决项）"
    return ("顺序未确定；编号仅供证据定位。<br>" if uncertain else "") + steps


def render_report(result, material=None):
    lines = [f"# 安全语义标注：{result['run_id']}", "",
             f"状态：**{STATUS_LABELS.get(result['status'], result['status'])}**（`{result['status']}`）", "",
             result["reason"], "", result["notice"], "",
             f"图摘要：`{result['graph_sha256']}`", "",
             "[四字段标注](profiles.json) · [位置声明](locations.json) · [位置证据表](audit/location-evidences.json) · [符号传播说明](transfer-specs.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)", "",
             "## 未决与执行问题", ""]
    for item in result.get("unresolved", []):
        lines.append(f"- `{item['instruction_id']}` / `{item['field']}`：{item['reason']}")
    for error in result.get("validation", {}).get("errors", []):
        lines.append("- " + error)
    if not result.get("unresolved") and not result.get("validation", {}).get("errors"):
        lines.append("没有记录未决项或执行问题；不等于模型标注已经人工确认。"
                     if result["status"] == "complete" else result["reason"])
    lines.extend(["", "## 按块查看", ""])
    if material is not None:
        for block_id, block in material["cfg"]["blocks"].items():
            lines.extend([f"### {block_id} · {_cell(block['block_name'])}", "",
                          "| IR | 动作 | 执行主体（operator） | roles | effects |",
                          "|---|---|---|---|---|"])
            for instruction in block["instructions"]:
                profile = result["profiles"].get(instruction["id"])
                uncertain = any(item["instruction_id"] == instruction["id"] and item["field"] == "effects"
                                for item in result.get("unresolved", []))
                values = ([", ".join(profile[key]) or "[]" for key in ("operator", "roles")]
                          + [_effect_steps(profile, uncertain)]) if profile else ["未接受"] * 3
                lines.append("| " + " | ".join(_cell(x) for x in [instruction["id"], instruction["opcode"], *values]) + " |")
            lines.append("")
    lines.extend(["## 符号传播说明", "",
                  "以下为同一次模型调用声明的符号操作。尚未执行数据传播，符号引用不是 Data ID；事件与效果位置保持唯一顺序。", ""])
    for location_id, location in result.get("locations", {}).items():
        lines.append(f"- 位置 `{location_id}`：`{location['kind']}` / `{location['name']}`。")
    for ir_id, spec in result.get("transfer_specs", {}).items():
        lines.extend(["", f"### {ir_id} · 事件与公开结果", ""])
        for event_index, event in enumerate(spec["events"]):
            effect_index = event["effect_index"]
            label = "无匹配效果的保守计算" if effect_index is None else f"效果索引 {effect_index}"
            lines.append(f"- 事件 {event_index}：{label}。")
            for position, operation in enumerate(event["atomic_ops"]):
                body = {key: value for key, value in operation.items() if key != "evidences"}
                lines.append(f"  - 操作 {position}：`{_cell(json.dumps(body, ensure_ascii=False))}`")
        if not spec["events"]:
            lines.append("- 事件为空；仍须保留下面的结果绑定。")
        for binding in spec["output_bindings"]:
            lines.append(f"- output[{binding['output_index']}] ← `{_cell(json.dumps(binding['value'], ensure_ascii=False))}`")
    lines.extend(["", "## 标注依据", ""])
    for ir_id, profile in result.get("profiles", {}).items():
        lines.extend([f"### {ir_id}", ""])
        for item in profile["evidences"]:
            value = item["value"] if item["value"] is not None else "空数组说明"
            step = f" / 步骤 {item['effect_index'] + 1}（索引 {item['effect_index']}）" if item.get("effect_index") is not None else ""
            lines.extend([f"- `{item['field']}`{step} / `{value}`；依据 `{item['basis']}`，位置 `{item['ref_id']}`。",
                          f"  理由：{item['reason']}", ""])
            lines.extend("> " + line for line in item["quote"].splitlines())
            lines.append("")
    lines.extend(["## 分析边界", "",
                  "这里只列举动作属性并声明符号传播操作。未执行 Skill，没有实际数据传播、敏感数据集合、风险评分或必要性判断。",
                  "宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。",
                  "effects 保留逐次效果及顺序；存在 effects 未决时，编号仅用于定位，不能视为已确认执行链。程序不证明模型推断的顺序正确。",
                  "context_write 表示后续可读的运行时上下文内容或绑定发生修改；它不自动等于 transform、fs_write 或 model_observe，普通 IR 结果绑定也不自动构成上下文写入。",
                  "空 effects 不等于空操作，也不能推出入口与出口状态相同；未知效果记录在 unresolved 中。",
                  "未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。", ""])
    return "\n".join(lines)
