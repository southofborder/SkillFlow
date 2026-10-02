"""Write the post-experiment assistant assessment, separate from model artifacts."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
directory = Path((root / "tmp/controlled-backtrace-v2/current-run.txt").read_text().strip())
report = json.loads((directory / "report.json").read_text(encoding="utf-8"))
assert report["execution_status"] == "complete" and report["recorded_logical_calls"] == 5


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


case_notes = {
    "c01": {
        "description": "F01 原图",
        "assessment": "four_key_groups_represented_with_local_explanation_error",
        "target_hits": [],
        "observed_target_misses": [],
        "observed_additional_business_false_positives": [],
        "explanation_issues": [{
            "finding_id": "finding_18",
            "category": "evidence_description_location_error",
            "model_text": "例如 result_002 来自 block_001/instructions/0",
            "correction": "result_002 由 block_002 的 ir_003 读取环境 FAST_KEY 后产生；rich 位置 /blocks/1/instructions/0/outputs/0，公共图位置 /blocks/block_002/instructions/0/outputs/0。",
            "basis": "finding_4 对来源描述正确；finding_18 引用的三个 result_002 派生链接也均指向正确定义。",
            "material_binding_misunderstanding_observed": False,
        }],
        "review": "四组关键要求均有实际对应核对，没有观察到关键语义漏报或业务缺陷误报；不能将局部证据说明错误省略为完全正确。",
    },
    "c02": {
        "description": "archive 额外接收密钥",
        "assessment": "target_defect_detected",
        "target_hits": [{"oracle_finding_id": "archive-receives-credential", "finding_ids": ["finding_6", "finding_7"], "distinct_defects": 1}],
        "observed_target_misses": [],
        "observed_additional_business_false_positives": [],
        "explanation_issues": [],
        "review": "错转与内部冲突是同一额外密钥输入的两方面，计一个目标缺陷。模型正确区分 archive.fetch 资源定位符与 source_id/FAST_KEY 业务输入。",
        "action_clarification": "建议修改 /blocks/block_011/instructions/0/inputs/2 对应的额外 result_002 输入；删除实际输入后重新生成受控文本及派生链接，不手工编辑 :link。保留 archive.fetch 资源定位符。",
    },
    "c03": {
        "description": "失败返回前缺少状态追加",
        "assessment": "target_defect_detected",
        "target_hits": [{"oracle_finding_id": "failure-status-append-missing", "finding_ids": ["finding_10"], "distinct_defects": 1}],
        "observed_target_misses": [],
        "observed_additional_business_false_positives": [],
        "explanation_issues": [],
        "review": "模型依据完整操作清单识别 block_014 只剩 ir_028 return，并明确标题及全局声明不能补回 append；其他失败返回语义分别判定保留。",
        "action_clarification": "在 /blocks/block_014/instructions/0 的现有 return 前添加状态追加操作。failure 只是可采用的状态值示例，源文未限定唯一存储格式。",
    },
    "c04": {
        "description": "重试成功返回首次 body",
        "assessment": "target_defect_detected_with_source_order_overstatement",
        "target_hits": [{"oracle_finding_id": "retry-returns-first-body", "finding_ids": ["finding_7b"], "distinct_defects": 1}],
        "observed_target_misses": [],
        "observed_additional_business_false_positives": [],
        "explanation_issues": [{
            "finding_id": "finding_2",
            "category": "source_order_overstatement",
            "model_text": "源文要求先读 request 中的 source_id，再读环境中的 FAST_KEY",
            "correction": "源文要求两项读取，用 and 连接，未指定它们必须先后执行；图将其记录为先读取 source_id，再读取 FAST_KEY。",
            "effect": "未产生额外缺陷误报，但解释文字扩大了源文的顺序要求。",
        }],
        "review": "返回输入实际为 result_004，链接到首次调用 body；重试结果为 result_008。判断引用实际输入、定义链接与成功边，具有不依赖块名的证据；本次响应仍不能证明模型内部不借助名称提示。",
        "action_clarification": "修改 /blocks/block_010/instructions/1/inputs/0 的完整结果引用：identifier=result_008，并同步 semantic_name=retry_fast_fetch_response_body；相应更新块名后再生成受控文本。单改名称不能修复绑定。",
    },
    "c05": {
        "description": "无依据增加两秒等待",
        "assessment": "target_defect_detected",
        "target_hits": [{"oracle_finding_id": "added-two-second-wait", "finding_ids": ["finding_5"], "distinct_defects": 1}],
        "observed_target_misses": [],
        "observed_additional_business_false_positives": [],
        "explanation_issues": [{
            "finding_id": "finding_7",
            "category": "evidence_description_location_error",
            "model_text": "fact:/blocks/5 检查并返回首次 fast.fetch body result_004；fact:/blocks/9 检查并返回 retry body result_008",
            "correction": "两个位置实际是追加状态和返回块；成功检查分别位于 fact:/blocks/4/instructions/0 和 fact:/blocks/8/instructions/0。返回在 fact:/blocks/5/instructions/1 和 fact:/blocks/9/instructions/1。",
            "basis": "正式证据列表覆盖正确的检查与返回位置，且 result_004/result_008 的返回绑定正确；自由说明合并相邻步骤导致定位不严谨。",
            "material_binding_misunderstanding_observed": False,
        }, {
            "finding_id": "finding_8",
            "category": "insufficient_cited_support_for_operation_claim",
            "model_text": "archive.fetch 操作输入为 archive.fetch 资源定位符和 result_001 source_id，未包含 result_002 FAST_KEY；图中没有诊断输出操作。",
            "correction": "本条正式引用只有 fact:/constraints/0，足以支持禁止声明被保留，但不足以单独支持所有操作层说明；应同时引用 archive 输入与实际 key 使用/定义链接。",
            "effect": "操作层说明与当前图相符，未观察到业务误报；证据引用范围仍需补足。",
        }],
        "review": "模型识别实际 wait_for_seconds、literal 2 和明确 seconds 约束，并定位到 transient 检查后、dispatch 前；不是仅凭不透明名称猜测等待。源文未给出该新增动作依据。",
        "action_clarification": "删除 /blocks/block_007/instructions/1 的 ir_wait_1 记录及其附属输入/约束，保留原有检查和 dispatch，之后重新生成操作清单。两条后续分支前记录了等待，并不构成已观察到运行延迟的证明。",
    },
}

for case_id, case in case_notes.items():
    stage = report["stages"][case_id]
    case.update(
        status=stage["status"],
        semantic_counts=dict(Counter(f["status"] for f in stage["result"]["findings"] if f["kind"] == "semantic")),
        context_count=sum(f["kind"] == "context" for f in stage["result"]["findings"]),
        parsed_sha256=digest(directory / f"parsed/{case_id}.json"),
        controlled_sha256=digest(directory / f"inputs/{case_id}/controlled.txt"),
        input_graph_sha256=digest(directory / f"inputs/{case_id}/cfg.json"),
        evidence=[f"parsed/{case_id}.json", f"inputs/{case_id}/controlled.txt", f"inputs/{case_id}/cfg.json", "inputs/source.json"],
    )

method = {
    "schema_version": 2,
    "run_id": directory.name,
    "assessment_identity": "assistant_posthoc_review_not_user_confirmation",
    "created_at": datetime.now(timezone.utc).isoformat(),
    "review_protocol": "先检查模型判定及原文/当前受控证据和图定位，再对照外置预期。原始模型响应、parsed 和 report 均不修改。",
    "human_confirmed": False,
    "model_response_sha256_binding": digest(directory / "report.json"),
    "cases": case_notes,
    "summary": {
        "distinct_injected_defects": 4,
        "assistant_assessed_hits": 4,
        "observed_target_misses": 0,
        "observed_additional_business_false_positives": 0,
        "local_explanation_inaccuracies": 3,
        "evidence_support_issues": 1,
        "posthoc_findings_total": 4,
        "model_reported_unknowns": 0,
        "execution_errors": 0,
        "is_general_accuracy_estimate": False,
    },
    "boundaries": [
        "四个命中仅针对预先固定的开发反例；单次 F01 示范不支持统计显著性或泛化保证。",
        "程序验证引用确实存在及引文一致，不证明自由说明准确或证据足够支持结论；c01/c04/c05 已出现相关问题。",
        "没有模型 unknown 条目不意味着 I/O 成功、隐含副作用、条件实现或开放操作语义已获验证。",
        "声明与动作分开保留；represented 仅为模型认为源要求在显式记录中有所对应。",
        "受控语言冗长；本轮没有证明其在成本或模型理解准确性上优于直接读图。",
        "所有修改建议待后续审查；本轮未编辑原图、重跑提取或补跑模型。",
    ],
}
(directory / "method_review.json").write_text(json.dumps(method, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

usage = {name: sum(c["usage"][name] for c in report["calls"]) for name in ("prompt_tokens", "completion_tokens", "total_tokens")}
reasoning = sum(c["usage"]["completion_tokens_details"]["reasoning_tokens"] for c in report["calls"])
review_lines = ["# 五案例助手事后复核", "", "本文件是助手复核意见，尚未经用户确认，不改写任何模型原始响应或有效判定。", ""]
for case_id, case in case_notes.items():
    review_lines += [f"## {case_id} · {case['description']}", "", case["review"], ""]
    if "action_clarification" in case:
        review_lines += ["建议的具体含义：" + case["action_clarification"], ""]
    for issue in case["explanation_issues"]:
        review_lines += [f"**解释文字问题：{issue['finding_id']} / {issue['category']}**", "",
                         "模型写法：“" + issue["model_text"] + "”。", "", "复核意见：" + issue["correction"], ""]
    review_lines += [f"依据：[模型结果](parsed/{case_id}.json)、[实际受控文本](inputs/{case_id}/controlled.txt)、[当前图](inputs/{case_id}/cfg.json)、[原始修改建议](suggestions/{case_id}.md)。", ""]
review_lines += ["## 统一边界", ""] + ["- " + item for item in method["boundaries"]] + [""]
(directory / "assistant_review.md").write_text("\n".join(review_lines), encoding="utf-8")

acceptance = f"""# 受控语义回述 v2：工程、证明与首次方法验收

本轮已完成重构、实际文本保真检查、五次官方 DeepSeek 核对及离线重放。唯一模型任务是**完整原文与受控文本核对**。本报告中的方法复核由助手完成，尚未经用户确认。

运行编号：`{directory.name}`。先阅读本页；需要证据时再打开[逐项助手复核](assistant_review.md)、[原始模型报告](report.md)或[完整运行 JSON](report.json)。本轮没有生成 PDF。

## 首次实测差异

| 案例 | 固定输入 | 模型实际结果 | 助手事后复核 |
| --- | --- | --- | --- |
| c01 | F01 原图，013/第 1 轮 | 17 项业务保留，无业务差异或未决 | 四组关键要求已核对；finding_18 有一处块编号说明错误。 |
| c02 | archive 额外接收 FAST_KEY | finding_6 错转；finding_7 内部冲突 | 同一密钥输入缺陷的两个方面，计 1 个目标命中。 |
| c03 | 删除失败出口状态追加 | finding_10 遗漏 | 正确区分残留标题/约束与实际操作清单；建议补在现有 return 前。 |
| c04 | 重试成功返回首次 body | finding_7b 错转 | 正确识别 result_004 与 result_008；finding_2 另有读取顺序的过度解读。 |
| c05 | 额外等待 2 秒 | finding_5 无依据新增 | 正确识别等待；另有检查/返回位置描述不严谨及操作层引证不足。 |

在本次助手复核范围内，四个预设缺陷均命中，未观察到目标漏报或额外业务缺陷误报；模型没有给出 unknown，执行错误为 0。**这不是方法正确率估计**，也不说明核对文本完全正确：三处解释不准确和一处操作层引证不足完整记录在 [assistant_review.md](assistant_review.md) 与 [method_review.json](method_review.json)。自动评测只生成证据区域匹配候选，助手复核也不冒充用户确认。

逐条原始修改建议：[c01](suggestions/c01.md)、[c02](suggestions/c02.md)、[c03](suggestions/c03.md)、[c04](suggestions/c04.md)、[c05](suggestions/c05.md)。建议只存档，没有自动改图。派生链接及操作清单应在 CFG 修改后重新生成，不能单独修改；c04 的修复需要更改实际 identifier 及相应语义标签，不能只改块名。

## 工程与证明结果

| 验收项 | 实际结果 | 记录 |
| --- | --- | --- |
| Lean 构建 | 成功；唯一实际打印器和解析器参与转换 | [证明说明](../../../../formal/CONTROLLED_RETELLING.md) |
| 公理审计 | 16 个主定理，其中新增 11 个；没有 sorry、占位公理或绕过内核检查 | [审计输出](verification/proof-audit.txt) |
| 固定图离线转换 | 30 原图 + F01 四反例，34 个不同输入全部通过实际文本解析与逐字段恢复比较 | [30 图清单](verification/review30.json)、inputs/c01–c05 |
| 回归测试 | 860 项通过，退出码 0 | [完整输出](verification/pytest-full.txt) |
| 模型输入绑定 | 五份实际正文摘要均与转换证书一致，输入允许字段固定 | [输入隔离检查](verification/payload-isolation.json) |
| 真实调用 | 5 个独立逻辑调用，5 次 HTTP 请求，每案例一次；没有修复或补跑 | calls/ 及 report.json |
| 离线重放 | 0 客户端创建、0 凭据读取、0 网络尝试；核对、评测与调用汇总一致 | [重放验收](verification/replay.json) |
| 已有材料保护 | 对 1,616 个保护文件逐文件验摘要，变化 0；新运行无配置凭据内容 | [最终保护检查](verification/protected-final.json) |

生产 Prompt、IR 字段、提取 pipeline、结构校验、冻结输入、ZIP、PNG、既有评审和历史实验记录未变。旧要求提取、自由回译、多方向模型核对、旧分阶段调度、Python 回述打印器及专属诊断工具均已移除。v1 历史记录保留，v2 入口明确拒绝将其运行或重放。

## 证明具体保证什么

形式化输入是完整的 RichGraph：不仅包含控制结构，也保留实际 opcode、所有操作数、标识、语义标签、字面值、draft ID、三级约束、上下文、顺序、完整 metadata 和控制边。literal/metadata 以规范 JSON 字符串保持，未解释嵌入源码行为。

已证明的核心关系为 `parseGraph(renderGraph(g)) = some g`：只读取真正打印出来的受控文本，即可恢复原来的富记录图。相关定理同时保持分类、作用域、位置、记录顺序和结果定义链接。正式解析入口还核对整份规范重印文本，不能只保留一个隐藏载荷却允许可见事实被篡改。

Python 每次都调用该 Lean 实现，从实际文本恢复规范 CFG，与输入逐字段比较，并绑定原图、正文、证据单元、链接、源码和可执行文件摘要。模型收到的就是已核验的原文本体；恢复失败或摘要不符时禁止该案例调用模型，不回退旧实现。

证明的公理基础明确包括 Lean 标准的 `propext`、`Quot.sound`，部分文本定理还使用 `Classical.choice`，不是“完全无公理”。Python Schema、JSON 规范化、JSONL 进程传输、编译器/可执行文件及模型请求封装仍属工程信任边界；本轮以实际往返、哈希绑定与回归测试验证这些边界，没有给出它们的全链路形式证明。

这不证明源文到图正确、模型说明正确、条件实现正确、所有路径可执行、文件写入成功、开放操作无隐藏副作用或自由中文的理解正确。没有 unknown 条目也不能消除这些未证明事项。

## 实际调用记录与效率边界

请求配置为官方 `deepseek-v4-flash`，API 实际返回名称均为 `deepseek-flash`；二者分别存档，没有强行改写成同一个名称。API 报告总用量：输入 {usage['prompt_tokens']:,} tokens，完成 {usage['completion_tokens']:,} tokens，总计 {usage['total_tokens']:,} tokens，其中 reasoning 为 {reasoning:,} tokens（属于完成用量）。没有估算费用。

当前受控文本强调完整记录、固定标签、块内清单与证据定位；F01 单份正文约 6.4–6.7 万字符，实际请求约 3.5–3.6 万输入 tokens。它是严格受控的结构化记录语言，仍然冗长。本轮没有做与直接读图的对照，不能宣称已证明降低认知负担、成本或提高泛化准确率。

## 复现与入口

使用固定 Lean 工具链在 `packages/skill-ir/formal` 下执行 `lake build` 和 `lake env lean ProofAudit.lean`。在仓库根目录创建新的运行目录，然后分别执行：

```powershell
python -m skill_ir.backtrace prepare --run-dir <新运行目录>
python -m skill_ir.backtrace run --run-dir <新运行目录>
python -m skill_ir.backtrace replay --run-dir <已有v2运行目录>
```

prepare 和 replay 不调用 API；run 按案例调用一次。已有接受的响应不会自动重发。完整使用说明见[实验 README](../../README.md)，当前流程规格见[受控语义回述与源文核对规范](../../../../../../docs/Skill-IR受控语义回述与源文核对规范.md)。
"""
(directory / "acceptance.md").write_text(acceptance, encoding="utf-8")
print(json.dumps({"written": ["method_review.json", "assistant_review.md", "acceptance.md"], "usage": usage}, ensure_ascii=False))
