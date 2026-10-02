"""Collect explicit post-run assistant assessments, never model judgments."""
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
read = lambda name: json.loads((HERE / name).read_text(encoding="utf-8"))
notes = read("case-reviews.json")
for case in ("c02", "c04", "c05", "c06", "c07"):
    record = read(f"review-{case}.json")
    if case == "c05":
        record["diagnostic_details"] = record["observations"]
        record["observations"] = [
            "完整响应有 15 条 finding。finding_5 引用 fact:/blocks/5/instructions/0/outputs/0；该位置实际对应 block_006 的 ir_011 状态追加操作，其 outputs=[]。扫描发现 1 个唯一非法 fact ID，出现 1 次，整例按协议拒绝。",
            "原始 finding_7 将 wait_for_seconds、literal 2 及明确秒单位判为 unsupported_addition，说明源文未要求等待。实际 block_007 顺序为 check_transient_error → wait_for_seconds → dispatch，等待影响瞬态与非瞬态两条后继。该目标描述合理，但不计有效命中。",
            "finding_7 的事实编号和建议目标存在；finding_6/7 的自由文字却把实际 block_007 写为 block_006，属于额外定位文字缺陷。不能用有效的局部证据挽救整份无效响应，也未补造状态追加的输出。",
            "原始建议删除等待操作及其字面量和约束只保留供诊断，未进入有效反馈或修改流程。其余原始语义项没有作为合法结果逐项验收。",
            "v3 此例有合法核对并命中等待，本轮是完整响应后的证据校验失败；结果没有改善。没有因完整响应失败而额外调用 API，也没有更改历史判断。",
        ]
    notes[case] = record
(HERE / "case-reviews.json").write_text(json.dumps(notes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
incidents = read("runtime-incidents.json")
incidents["c05"] = {
    "stage": "response_evidence_validation",
    "observed_error": "controlled unit does not exist: fact:/blocks/5/instructions/0/outputs/0",
    "classification": "ResponseValidationError",
    "automatic_retry": False,
    "complete_response_available": True,
    "semantic_result_available": False,
    "method_boundary": "Preserve complete response for diagnosis, do not repair evidence IDs or count a valid semantic hit.",
}
(HERE / "runtime-incidents.json").write_text(json.dumps(incidents, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"reviewed_cases": sorted(notes)}, ensure_ascii=False))
