# 表示契约与一次标注修复

格式职责由 [`format_instructions.py`](../../src/skillflow/propagation/contracts/format_instructions.py) 和严格 Schema 共用维护，标注、审查及修复 Prompt 引用同一函数。本轮取消独立表示契约材料及其摘要；读取、观察等保守默认仍由唯一的 `runtime_contract` 决定。现行字段和分阶段保存方式见[字段收紧规范](../architecture/field-tightening.md)。

## 各层职责

| 关系 | 权威材料 | 不能由此推导的结论 |
|---|---|---|
| 动作、操作数、结果定义、次序、控制边、条件、约束 | CFG | 约束声明不替代缺失动作 |
| 普通 return 返回哪个值 | return 的实际输入 | 没有公开输出，不因此添加 output_bindings 或 user_output |
| 获取范围、字段、筛选、计算依赖、共享状态、交付参数 | 传递规格 | 结果名称不能替代明确字段关系 |
| 模型观察的数据版本 | 原始处理段及程序编译观察 | 可能观察不是实际执行测量 |
| 普通调用者内部状态、未说明网络、执行成功 | 当前能力边界 | 没有建模这些边界不自动构成漏标 |

空 effects、空 events 和空 output_bindings 可以合法存在，尤其普通 return。
审查仍检查 CFG 的返回身份，不能将空效果等同于 NOP 或入口、出口相同。
工具获取使用工具边界，不因网络机制未明确而抹掉来源。
明确的字段关系必须使用现有选取能力，不能以 CFG 有结果名称为由接受 opaque compute。

## 正常判断、部分顺序和任务失败

CFG 核对正常判定仅有 represented、omitted、mistranslated、unsupported_addition、internal_conflict。
标注审查正常 findings 只含具体 issue，可以为空。旧 unknown、unknown_reason、uncertain、unresolved 不作为新版正常响应字段。

正常响应使用 `outcome=completed`。确实缺少必要材料、存在无法消解的源文冲突或必要关系超出表示能力时，使用 `outcome=cannot_assess` 和具有真实原文范围／CFG目标／规则定位的 failure；运行状态为 semantic_failure。
失败不是空问题结果，也不会触发没有纠错依据的修复。程序检查格式和定位，不证明失败理由成立。

未知容器内容、默认可能观察、普通不透明计算、possible 依赖、候选来源及没有运行成功承诺，均不是单独失败理由。
它们按已有契约正常计算。原始规格必填 `order=fixed|partial`；编译器生成 precedence，不让模型维护第二份顺序表。
partial 保留可能次序、局部定义使用、作用域与观察因果，不等待人工决定，也不等于 incomplete。
绑定错误、不可求解回路等具体诊断继续保留。

## 一次修复

```text
冻结候选 → 独立初审
              ├─ 无问题：结束
              ├─ 具体问题：完整修复一次 → 校验与编译 → 独立复审 → 结束
              └─ 语义任务失败、无效响应或执行失败：结束
```

初审、语义修复和复审最多三个语义阶段；每个阶段的机械结构纠正次数不限，不应称为总调用最多三次。修复返回完整原始标注，不返回 JSON Patch，也不修改 CFG。
修复输入绑定同一源文、CFG、运行时规则和共享格式说明、上一份实际标注、经过验证的初审和程序解析的目标位置。
源文和契约优先于建议，禁止为了满足误报而虚构用户输出、局部隔离、字段或网络效果。
复审重新建立索引和观察清单，不接收初审、修复指令或外置预期。

复审无问题称为“本轮审查未发现实质问题”；仍有问题为 repair_limit。修复或复审失败明确保存原因。
合法修复候选可以诊断性传播，但不会因传播完成而变成语义正确。
修复失败时原候选仍是最后结构有效材料，不冒充已修复结果。

`python -m skillflow.propagation.review refine --annotation-run <目录> --run-dir <新目录>`
执行闭环；`replay --run-dir <目录>` 使用接受响应重建决定，零 API。
修复请求类型与上下文冻结，由标注加载、传播加载和重放共同重建；不通过客户端临时追加文字。
已接受响应恢复不重发，完整无效响应仅按机械诊断进入结构纠正，不增加语义修复轮。

## 版本与实验边界

Task v2；联合标注 v13／运行 v16；运行时 v7；编译器 v7；审查业务 v5／运行 v9；一次修复运行 v8。完整版本表见[字段收紧规范](../architecture/field-tightening.md)。Data v4、原 IR 与 Lean 事实保持语义未改变。

The following seven-candidate experiment describes its historical execution, not a new run under the current format.
旧记录不自动迁移。七例试验先用旧入口核验并冻结材料，再显式重建三份原候选与四个缺陷变体，记录每项变更；它们不是新版模型接受响应。
新实验最多 21 次审查／修复调用，加三个既有 CFG 各一次源文核对，共最多 24 次。
不重新提取或修复 CFG，不对完整返回按质量补跑。
历史材料保持原样，受控缺陷真正修复与否由助手另外复核，不以复审空清单替代评测。
