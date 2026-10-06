# DOE 前收尾检查与阶段交接

检查日期：2026-09-29。

本轮完成最后一轮代码收紧、离线回归和现有输入核验。在本次检查范围内，没有发现阻挡进入 DOE 阶段的遗留实现问题。DOE 的敏感性、任务必要性和非必要暴露判断尚未实现；下一阶段从当前传播事实开始，不把核对通过或传播完成解释为语义正确性的证明。

## 1. 本轮实际收紧

| 部位 | 修改 | 保留的约束 |
|---|---|---|
| CFG 反馈快照 | 删除只有转口作用的 `feedback/snapshot.py`，直接复用 `inputs.snapshot` | 字节与文本摘要、快照隔离、恢复核验不变 |
| 核对类型与依赖 | 删除未使用类型、重复版本常量、无用导入和转口；CLI 直接使用公共调用工厂 | 公共输入类型、严格引用和执行记录仍由原有模块管理 |
| 核对依据 | 删除没有独立定义或处理逻辑的 `FindingBasis.insufficient`，同步提示词并增加拒绝测试 | 合法遗漏仍用真实源文与图事实支持；确实无法判断走 `cannot_assess` |
| 标注审查 | `suggestion` 直接定义为必填非空文本，删除旧的条件必填逻辑；提示词与实际 Schema 一致 | 正常空 findings 合法，但无效响应不能形成审查通过 |
| 配置与契约 | 公共请求配置字段、审查版本统一取自已有权威定义；删除未使用的契约文本辅助函数 | 凭据、未知参数仍被拒绝，契约正文和版本不变 |
| 传播与导出 | 复用 `load_annotation_run()`，合并重复的接受响应、请求身份、投影及编译核验 | 提交前材料摘要、新计算的实现身份校验、保存边界的独立验证保留 |
| 使用文档 | 根 README、包说明和文档导航更新为实际流程；旧实验说明标明历史身份 | 历史响应、实验报告、摘要及交付物不改写 |

传播提交前现在检查共用加载器核验过的完整文件清单。相应测试覆盖在提交期间篡改 `profiles.json`、`transfer-specs.json`、`validation.json`、`response.json` 时拒绝提交；没有用合并代码的方式放松材料一致性检查。

## 2. 明确保留的内容

下列内容有独立职责，不属于应继续删除的泛化未决或重复证据：

- `partial` 顺序、候选集合及 `possible` 依赖：承载可计算的可能关系，避免无依据选择保护后的数据版本。
- 实际绑定错误、能力限制及 `semantic_failure`：说明为什么不能完成计算或必要判断，不能把它们改为空问题清单。
- HTTP 请求状态不确定及已接受响应保护：防止中断恢复自动重复收费调用，和业务语义中的“未决”无关。
- 规格中的效果索引、因果次序和诊断位置：用于证据关联、编译及求值定位，没有重新复制进精简后的业务操作记录。
- 原始响应、编译映射、位置审计证据、初始种子及身份恢复材料：分别验证不同阶段；DOE 主文件仍不复制这些模型证据链。
- 内容关系、实际输入和派生／可能依赖：三者不能合并成“包含了哪些敏感数据”。

没有修改 IR、Data 契约、生产提取 Prompt 或 Lean 实现，也没有增加新的模型调用阶段。

## 3. 本轮验证结果

| 验证 | 结果 |
|---|---|
| 核对、反馈、审查、一次修复、标注、观察编译、传播、导出及记录相关统一回归 | **705 项通过** |
| 最后删除 `insufficient` 后的核对服务、显式失败和反馈契约回归 | **136 项通过**；与上一批部分重叠，不累加为独立测试数 |
| 既有七份 DOE 文件独立读取 | 全部通过严格结构、引用和覆盖检查 |
| 七份传播运行完整只读加载 | 全部通过接受响应、审计材料、编译和业务投影一致性核验 |
| 三个基线与源文核对的图身份、标注审查状态及传播覆盖 | 一致；均无传播诊断 |
| 冻结输入、既有运行和交付物，以及受保护的 IR、Data、形式化和提取材料 | **11,320 个文件摘要未变** |
| 本轮远程模型调用 | **0 次**；现有输入核验还显式阻断了网络连接 |

本轮只读核验旧实验，没有将其改成新生产者身份，也没有在源码变化后重放或续跑旧实验。回归测试覆盖新准备运行的恢复与零 API 重放；旧实验的只读加载仍重新核验实际材料与编译关系。重新求解和续跑要求实现身份一致的规则没有放松。

本地验证回执：[统一回归](../tmp/doe-handoff-cleanup/regression.xml)、[最后定向回归](../tmp/doe-handoff-cleanup/final-basis.xml)、[输入与保护文件核验](../tmp/doe-handoff-cleanup/input-validation.json)。这些是检查产物，不是 DOE 输入的新字段。

## 4. 下一阶段使用的三个基线

使用 `repair-once-v1-20260929-132248` 中的三个真实基线。它们的既有 CFG 核对均为 `audit_passed`，标注初审均为 `review_passed`，未触发标注修复；传播均为 `complete`。这些状态说明相应步骤完成，不保证模型判断无误。

| 基线 | 完整 IR 记录数 | Data 数 | 唯一业务输入 | 人审页 |
|---|---:|---:|---|---|
| 001 / N01 | 10 | 6 | [doe-input.json](../packages/skill-ir/experiments/annotation_review/runs/repair-once-v1-20260929-132248/cases/001-base/propagation/doe-input.json) | [HTML](../packages/skill-ir/experiments/annotation_review/runs/repair-once-v1-20260929-132248/cases/001-base/propagation/report.html) |
| 010 / Q04 | 12 | 9 | [doe-input.json](../packages/skill-ir/experiments/annotation_review/runs/repair-once-v1-20260929-132248/cases/010-base/propagation/doe-input.json) | [HTML](../packages/skill-ir/experiments/annotation_review/runs/repair-once-v1-20260929-132248/cases/010-base/propagation/report.html) |
| 013 / F01 | 26 | 20 | [doe-input.json](../packages/skill-ir/experiments/annotation_review/runs/repair-once-v1-20260929-132248/cases/013-base/propagation/doe-input.json) | [HTML](../packages/skill-ir/experiments/annotation_review/runs/repair-once-v1-20260929-132248/cases/013-base/propagation/report.html) |

以上均为 `skillflow-doe-input-v5`，实际文件 SHA-256 保存在本轮输入核验回执中。后续 DOE 读取单份业务文件；需要检查上游推断依据时另读旁置审计材料。

四个受控缺陷案例用于检验审查和修复方法，不当成另外四个真实 Skill。尤其 `010-source` 的初审已经发现问题，但修复流中断，因此闭环状态仍为 `execution_error`。它的原始缺陷候选虽可完成诊断性传播，却没有被修好，不能进入正常 DOE 基线。正常的 `010-base` 不受这次受控实验失败影响。

[七例原实验总览](../packages/skill-ir/experiments/annotation_review/runs/repair-once-v1-20260929-132248/index.html)与[助手复核](../packages/skill-ir/experiments/annotation_review/runs/repair-once-v1-20260929-132248/assistant-review.md)继续保留原样。

## 5. DOE 阶段的交接边界

下一阶段围绕“必要动作中的非必要敏感数据暴露”设计判断，利用现有任务原文、数据来源与内容关系、处理前后版本、CFG 条件及交付边界。当前实现不求解自然语言路径条件，也不把 may 候选自动当成可同时发生的事实；DOE 不能默默强化这些结论。

建议先用上述三个基线固定敏感性判断、任务相关的必要范围、实际可能观察／交付范围与最终问题表达。DOE 结果另存，不回写上游 `doe-input.json`，也不为获得预期结论反向修改传播事实。本轮交接没有预先定义新的 DOE 大型 Schema 或判定算法。
