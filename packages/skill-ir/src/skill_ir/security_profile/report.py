"""Chinese records of annotations; no risk or necessity judgments."""
from __future__ import annotations

import json

from skill_ir.runtime_contract import (
    execution_model_binding, validate_execution_model_binding,
)

STATUS_LABELS = {"complete": "标注记录完整", "semantic_failure": "无法完成语义标注",
                 "input_error": "输入错误", "invalid_response": "响应无效",
                 "execution_error": "调用执行错误", "interrupted": "已中断"}


def _cell(value):
    return str(value).replace("|", "\\|").replace("\r", "").replace("\n", "<br>")


def _effect_steps(profile, partial=False):
    steps = "<br>".join(
        f"{index + 1}. {effect}" + ("（上下文写入）" if effect == "context_write" else "")
        for index, effect in enumerate(profile["effects"])
    ) or "[]（无已记录效果；不等于空操作，请结合动作与绑定）"
    return ("部分顺序；按因果约束保留候选安排。<br>" if partial else "") + steps


def render_report(result, material=None):
    binding = result.get("execution_model")
    if binding is not None:
        binding = validate_execution_model_binding(binding)
    if material is not None and "execution_model" in material:
        material_binding = execution_model_binding(material["execution_model"])
        if binding is not None and binding != material_binding:
            raise ValueError("report abstract runtime contract binding differs from material")
        binding = material_binding
    contract_line = (
        f"统一抽象运行时契约：`{binding['version']}`；摘要：`{binding['sha256']}`。"
        if binding is not None else "本报告未提供契约身份，不能据此确认所用执行假设。"
    )
    lines = [f"# 安全语义标注：{result['run_id']}", "",
             f"状态：**{STATUS_LABELS.get(result['status'], result['status'])}**（`{result['status']}`）", "",
             "本页记录统一契约下的静态可能性，不是执行轨迹。默认读取与观察不表示真实运行必然如此；明确局部获取、返回或隔离机制约束默认范围。", "",
             contract_line, "",
             result["reason"], "", result["notice"], "",
             f"图摘要：`{result['graph_sha256']}`", "",
             "[四字段标注](profiles.json) · [位置声明](locations.json) · [位置证据表](audit/location-evidences.json) · [符号传播说明](transfer-specs.json) · [Sink 边界](sink-boundaries.json) · [校验记录](validation.json) · [完整结果](result.json)", "",
             "## 执行问题与能力边界", ""]
    if result.get("error_kind"):
        lines.append(f"错误类别：`{result['error_kind']}`。")
    request = result.get("request_validation")
    if request is not None:
        lines.extend(["", "请求身份核验（不表示标注语义正确）：", "",
                      "```json", json.dumps(request, ensure_ascii=False, indent=2), "```", ""])
    for error in result.get("validation", {}).get("errors", []):
        lines.append("- " + error)
    if not result.get("validation", {}).get("errors"):
        lines.append("没有记录执行问题；不等于模型标注已经人工确认。"
                     if result["status"] == "complete" else result["reason"])
    lines.extend(["", "## Sink 边界与固定等级", "",
                  "类型和等级由程序按位置属性和具体交付／写入操作生成；等级仅表达边界访问及留存，不表示敏感度、危险程度、任务必要性或 DOE 结论。标注阶段关联符号操作，传播后由同一操作关联实际数据版本。", "",
                  "| IR / 事件 / 操作 | 边界 | 类型 | 等级 | 访问范围 / 留存 | 作用域 |",
                  "|---|---|---|---|---|---|"])
    for sink in result.get("sink_boundaries", []):
        location = result.get("locations", {}).get(sink["target"], {})
        event = str(sink["event_index"])
        if sink.get("body_event_index") is not None:
            event += "." + str(sink["body_event_index"])
        values = [f"{sink['instruction_id']} / {event} / {sink['op_index']}",
                  f"{sink['target']} · {location.get('kind', '')} / {location.get('name', '')}",
                  sink["sink_type"], str(sink["exposure_level"]),
                  f"{location.get('access_scope', '')} / {location.get('retention')}", sink.get("scope") or "—"]
        lines.append("| " + " | ".join(_cell(x) for x in values) + " |")
    if not result.get("sink_boundaries"):
        lines.append("| — | 没有程序收集的 Sink 边界 | — | — | — | — |")
    lines.extend(["", "任务内部且任务期限内的流动仍保留在传播说明中，等级 0 不进入 Sink 清单；删除绑定不交付旧内容。未进入清单不等于已证明没有数据风险。", "",
                  "## 按块查看", ""])
    if material is not None:
        for block_id, block in material["cfg"]["blocks"].items():
            lines.extend([f"### {block_id} · {_cell(block['block_name'])}", "",
                          "| IR | 动作 | 执行主体（operator） | roles | effects |",
                          "|---|---|---|---|---|"])
            for instruction in block["instructions"]:
                profile = result["profiles"].get(instruction["id"])
                partial = result.get("transfer_specs", {}).get(instruction["id"], {}).get("order") == "partial"
                values = ([", ".join(profile[key]) or "[]" for key in ("operator", "roles")]
                          + [_effect_steps(profile, partial)]) if profile else ["未接受"] * 3
                lines.append("| " + " | ".join(_cell(x) for x in [instruction["id"], instruction["opcode"], *values]) + " |")
            lines.append("")
    lines.extend(["## 符号传播说明", "",
                  "以下为程序编译后的符号操作。处理段来自模型标注，model_observe 由程序依据处理方式与运行时契约生成；编译不证明处理方式的语义判断正确。尚未执行数据传播，符号引用不是 Data ID。", "",
                  "[原始处理段](audit/raw-annotation.json) · [编译后完整响应](audit/compiled-response.json) · [编译位置映射](audit/compilation-map.json)", ""])
    for location_id, location in result.get("locations", {}).items():
        lines.append(f"- 位置 `{location_id}`：`{location['kind']}` / `{location['name']}`；访问范围 `{location['access_scope']}`，留存 `{location['retention']}`。位置依据见独立审计表，默认属性不冒充真实运行事实。")
    for ir_id, spec in result.get("transfer_specs", {}).items():
        lines.extend(["", f"### {ir_id} · 事件与公开结果", "", f"次序：`{spec['order']}`；编译因果约束：{len(spec['precedence'])} 项。", ""])
        def describe_event(event, position):
            effect_index = event["effect_index"]
            label = "无安全标签的数据关系" if effect_index is None else f"效果索引 {effect_index}"
            lines.append(f"- 事件 {position}：{label}。")
            for op_index, operation in enumerate(event["atomic_ops"]):
                body = {key: value for key, value in operation.items() if key != "evidences"}
                lines.append(f"  - 操作 {op_index}：`{_cell(json.dumps(body, ensure_ascii=False))}`")
        for event_index, event in enumerate(spec["events"]):
            if event.get("kind") == "for_each":
                lines.append(f"- 逐元素作用域 {event_index}：集合 `{_cell(json.dumps(event['collection'], ensure_ascii=False))}`，元素绑定 `{_cell(event['item'])}`。同一元素的字段保持配对；不表示真实集合长度或实际调用次数。")
                for body_index, child in enumerate(event["body"]):
                    describe_event(child, f"{event_index}.{body_index}")
            else:
                describe_event(event, event_index)
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
            basis_note = "（契约依据，非实测；结合适用对象和明确例外理解）" if item["basis"] == "execution_model" else ""
            lines.extend([f"- `{item['field']}`{step} / `{value}`；依据 `{item['basis']}`{basis_note}，位置 `{item['ref_id']}`。",
                          f"  理由：{item['reason']}", ""])
            lines.extend("> " + line for line in item["quote"].splitlines())
            lines.append("")
    lines.extend(["## 分析边界", "",
                  "这里只列举动作属性并声明符号传播操作。未执行 Skill，没有实际数据传播、敏感数据集合、风险评分或必要性判断。",
                  "宽读取与模型回传是统一抽象运行时契约中的保守默认。工具内部读取、工具返回和进入模型请求是不同边界；引文匹配只核验证据存在，不证明推断成立。",
                  "effects 保留逐次效果位置；order=partial 时，按约束计算可能安排，数组不是唯一执行次序。程序不证明模型推断正确。",
                  "context_write 表示后续可读的运行时上下文内容或绑定发生修改；它不自动等于 transform、fs_write 或 model_observe，普通 IR 结果绑定也不自动构成上下文写入。",
                  "空 effects 不等于空操作，也不能推出入口与出口状态相同；无法形成必要关系时明确记录任务失败。",
                  "未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。", ""])
    return "\n".join(lines)
