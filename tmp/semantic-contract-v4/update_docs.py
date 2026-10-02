"""Update current usage docs only; historical run records are immutable."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
changes = {
    "docs/Skill-IR受控语义回述与源文核对规范.md": [
        ("（v3）", "（v4）"), ("核对协议为 v3", "核对协议为 v4"),
        ("业务项按七类义务拆分为可独立判错的要求或关系：要求性质与作用域、动作与对象、数据来源与绑定、条件与例外、顺序与依赖、次数与终止、反向依据与一致性。`dimension_reviews` 必须恰好覆盖七类，关联具体条目或说明不适用理由。一个段落的编号已覆盖，不表示其中多个关系均已核对。",
         "七类检查点仅作为阅读提示：要求性质与作用域、动作与对象、数据来源与绑定、条件与例外、顺序与依赖、次数与终止、反向依据与一致性。取消强制类别、逐类表格和原子拆分；允许关联要求合并，但有局部差异不能将整项判为保留。模型在同一次调用中检查自身结论与证据及其他发现的一致性。一个段落的编号已覆盖，不表示其中多个关系均已核对。"),
        ("`represented` 的业务项必须标明 `precision=precise/conservative`。保守只接受依赖精度问题，附固定规则、已有候选事实编号、理由和精度损失，不因该精度不足记为未决，也不引发重新提取。",
         "`represented` 不再强制选择精度类别；明确采用保守依赖规则时附可选 `conservative` 说明，包括固定规则、已有候选事实编号、理由和精度损失。没有该说明不代表精确。保守只接受依赖精度问题，不因该精度不足记为未决，也不引发重新提取。"),
        ("程序校验定位、记录和精度标签，不证明模型拆分完整或候选判断正确。", "程序校验定位、记录及已填写的保守候选，不证明模型语义判断正确。`unknown_reason` 仅在未决时必填，其他状态可以省略；不要求原因枚举。所有核对记录都在图外，原图 IR 不增加字段。"),
        ("semantics-v3-seven", "semantics-v4-seven"), ("runs/controlled-v3-seven", "runs/controlled-v4-seven"),
        ("七类和精度契约", "可组合语义项、可选说明和证据契约"),
    ],
    "docs/CFG构建语义反馈闭环.md": [
        ("当前版本为 **v3**", "当前版本为 **v4**"),
        ("七类义务分别核对，依赖区分精确与保守表示。", "七类检查点仅作阅读提示，核对项可组合关联要求；保守依赖说明仅在适用时填写，不将未说明者自动称为精确。"),
        ("v1/v2 的历史响应", "v1/v2/v3 的历史响应"),
        ("项及其类别、引文", "项及其引文"),
        ("JSON、编号、引文、七类检查记录、精度字段及完整源文／受控单元覆盖有效", "JSON、编号、引文、适用的可选说明及完整源文／受控单元覆盖有效"),
        ("须区分 `precise` 和 `conservative`。", "不再强制标记精度；明确使用保守依赖规则时填写 `conservative`。"),
        ("七类记录不证明模型找全所有要求。", "编号覆盖不证明模型找全所有要求。程序仅报告保留总数及其中明确记录保守依赖的数量。"),
        ("历史单次核对及 v1/v2 反馈记录不被解释为 v3 运行。", "历史单次核对及 v1/v2/v3 反馈记录不被解释为 v4 运行。"),
    ],
    "docs/README.md": [
        ("核对 v3 允许带证据的保守依赖表示", "核对 v4 将七类检查点作为阅读提示，允许带证据的保守依赖说明"),
        ("七类核对义务、精确／保守依赖、反馈门槛和保证边界。", "模型语义判断与程序证据检查的分工、可选保守依赖说明、反馈门槛和保证边界。"),
        ("v3 契约绑定", "v4 契约绑定"),
        ("[v3 七例实施验收]", "[v3 七例历史验收]"),
        ("不能替代 v3 实测", "不能替代当前版本实测"),
        ("当前流程以 v3 核对规范为准", "当前流程以 v4 核对规范为准"),
    ],
    "packages/skill-ir/README.md": [
        ("核对与反馈共用版本化 IR 解释契约，七类业务关系逐项记录，保留项区分精确和保守依赖；保守只允许依赖精度损失，不能掩盖明确错误。", "核对与反馈共用版本化 IR 解释契约。v4 将七类检查点保留为阅读提示，由模型合理组织语义核对项；保守依赖说明仅在适用时填写，不将其余保留项自动称为精确。保守只允许依赖精度损失，不能掩盖明确错误。原图 IR 不增加字段。"),
        ("--suite semantics-v3-seven", "--suite semantics-v4-seven"),
    ],
}
for relative, replacements in changes.items():
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    for before, after in replacements:
        if before not in text:
            raise RuntimeError(f"Missing documentation text in {relative}: {before}")
        text = text.replace(before, after)
    path.write_text(text, encoding="utf-8")

path = ROOT / "packages/skill-ir/experiments/semantic_backtrace/README.md"
text = path.read_text(encoding="utf-8")
text = text.replace("（v3）", "（v4）")
text = text.replace("v3 按 [统一解释契约与七类义务]", "v4 按 [统一解释契约与阅读检查点]")
text = text.replace("逐项核对，保留项区分精确表示和合法的保守依赖。", "核对语义，由模型组织相关要求；取消强制类别与精度分类，仅在适用时记录保守依赖说明。未填写该说明不代表精确。")
text = text.replace("semantics-v3-seven", "semantics-v4-seven")
# Preserve links to the historical v3 run.
text = text.replace("runs/controlled-v3-seven --", "runs/controlled-v4-seven --")
text = text.replace("runs/controlled-v3-seven\n", "runs/controlled-v4-seven\n")
text = text.replace("不能作为 v3 实测", "不能作为 v4 实测")
text = text.replace("本轮 v3 七例结果见", "历史 v3 七例结果见")
path.write_text(text, encoding="utf-8")
print("Updated current documentation; historical experiment reports unchanged")
