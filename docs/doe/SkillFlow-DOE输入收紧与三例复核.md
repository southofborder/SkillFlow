# 传播结果收紧与 DOE 原始输入

本页保留 2026-09-24 的 v1 精简实验及原始结果。当前业务文件已经更新为 DOE v6，位置增加 access_scope/retention，并以紧凑 sink_boundaries 关联已经形成记录的操作；最新字段树见[传播结构说明](../propagation/SkillFlow-传播结构与函数树状说明.md)，边界类型和固定等级见[Sink 主规范](../propagation/SkillFlow-Sink边界与固定分级.md)。下列历史结果不重写、不作为当前模型实测结论。

本轮的后续算法入口统一为 `doe-input.json`（`skillflow-doe-input-v1`）。它是传播事实文件，不包含必要性判断、风险等级或 DOE 结论。标注契约仍为 v5，Data 仍为 v3；记录快照为 v4，传播运行身份为 v3。

## 1. 人审时先看什么

先打开实验总览 `index.html`，进入某例的“传播审查”。页面默认展示动作、数据版本、交互边界和入口／出口变化；点击 `D001` 等报告短名查看对应 Data。短名仅用于展示，原文件保留完整真实 ID。

确认以下四件事，再按需展开审计材料：

1. 入口取到的是哪个整体，是否无依据缩成了某个字段。
2. 删除、选取、更新等操作使用哪个版本、生成哪个版本。
3. 模型观察、外发、写入使用的是处理前还是处理后的数据。
4. `unresolved`、`diagnostics` 和 `coverage` 是否保留尚未解决或未形成记录的部分。

## 2. 现在只交付一棵业务结构

```text
doe-input.json
├─ schema_version                 文件版本
├─ source                         完整可读 Skill 及其边界
│  ├─ files[]                     文件名、原文、文本摘要
│  ├─ source_sha256               源文整体摘要
│  ├─ index[]                     文本单元 ID、文件、起止行
│  ├─ inventory[]                 原始文件大小、类型与字节／文本摘要
│  └─ boundaries                  二进制与未解释代码清单
├─ cfg                            实际选用的原图，包括条件和约束
├─ locations[位置 ID]              kind、name、operand_refs
├─ actions[IR ID]                  operator、roles；覆盖全部 IR
├─ data[]                         每个 Data 实体只登记一次
│  ├─ id                          稳定身份
│  ├─ content                     组成、字面值、排除或覆盖关系
│  ├─ origin                      来源、实际输入与派生／可能依赖
│  └─ annotations                 描述和已有敏感性标注；传播不补写判断
├─ records[IR ID]                  仅包含求解形成的 IR 记录
│  ├─ entry_state                 当前动作之前的完整位置绑定
│  ├─ events[]                    按规格对应的效果阶段
│  │  ├─ effect                   实际效果标签，也可以为 null
│  │  └─ atomic_ops[]             本阶段的数据操作
│  │     ├─ op                    数据操作类型
│  │     ├─ inputs[][]            按参数位置排列的 Data 候选集合
│  │     ├─ outputs[][]           按局部输出位置排列的候选集合
│  │     ├─ endpoints[]           本步骤交互的声明边界
│  │     └─ changes[]             步骤内位置变化，含 before/after/update
│  └─ exit_state                  当前动作之后的完整位置绑定
├─ status                         程序求解状态
├─ coverage[IR ID]                哪些 IR 形成记录、哪些尚未形成
├─ unresolved[]                   标注仍未确定的内容
└─ diagnostics[]                  实际绑定问题、求解限制与动态诊断
```

`inputs = [[A, B], [A]]` 表示两个参数位置：第一个可能是 A 或 B，第二个再次使用 A。它既不是三个参数，也不是把 A、B 拼接成一份数据。

报告操作表的 `1.1` 表示第 1 个事件的第 1 项操作；查回 JSON 时对应 `events[0].atomic_ops[0]`。输入／输出行内的参数编号使用零起始。两者都是展示定位，不是新的传播字段。

## 3. 删除、合并与保留

| 处理 | 内容 | 原因 |
|---|---|---|
| 删除 | `intermediate_key`、`symbolic_endpoint` 及专用私有辅助 | 无生产调用，避免平行身份规则 |
| 合并 | 旧记录示例 → `propagation_demo.py --records-only` | 同一套示例与保存入口 |
| 删除 | 记录的 `op_index/effect_index` | 数组位置已有唯一对应；标注规格仍保留效果索引 |
| 删除 | `ResolvedBinding.ref` 与仅包装 `data_ids` 的一层对象 | 求解后直接保存实际 Data 候选，规格引用在审计区 |
| 删除 | 每个操作重复的固定 `notes` | 通用语义统一写在规范与报告中 |
| 转移 | 字段不存在、已排除等动态信息 | 进入带 IR／事件／操作位置和 Data ID 的 `diagnostics` |
| 合并 | Markdown 与 HTML 展示准备 | 共用 `build_view`，各自只负责格式和转义 |
| 合并 | 正式运行、示例、重放的组装与报告 | 共用业务投影和保存／渲染入口 |
| 删除 | 重复的最终 `result/data/records/resolved-seed.json` | 唯一业务结果为 `doe-input.json` |
| 分离 | 最终 Data 的 namespace 与身份键 | `audit/data-identities.json` 只保存身份，不复制实体 |
| 保留 | `StateChange.before/after/update` | 完整 IN／OUT 无法还原同一 IR 内多次写入 |
| 保留 | endpoints 与 changes.location | 声明目标与实际受影响的别名位置可能不同 |
| 保留 | 内容关系、origin.inputs、derived/possible | 明文内容、实际参数与影响依赖是不同事实 |
| 保留 | 初始 Data 与原始种子参数 | 初始描述可能不同于最终描述，不能从最终 Data 倒推 |
| 保留 | 原始响应、提示词及独立证据 | 用于核验模型实际输出，不写进业务文件 |

`ValueRef`、九种原子操作及 `output_bindings` 仍用于传播前的规格。没有增加按名称或 opcode 猜测字段选择、保护处理或结果绑定的规则。

## 4. 两级读取与离线重放

```python
from skillflow.propagation import load_doe_input, load_propagation_run

facts = load_doe_input("doe-input.json")        # 只需这一个文件
facts = load_propagation_run("propagation/")   # 再核验审计材料、接受响应和登记身份
```

普通读取不要求当前源码与生成时相同。离线重新求解要求源码身份匹配，并从保存的原始种子参数重算，比较业务结果、有效初始材料和身份索引。

```powershell
python -m skillflow.propagation replay --run-dir path/to/propagation
```

重放仅生成摘要、差异和报告，不再保存第二份最终 Data。清单最后提交；保存过程中断、缺少清单的目录不能被当成已提交运行。

## 5. 验证边界

精简前后的既有离线示例仍为 12 份 Data、13 条 IR、15 个事件与 15 个原子操作。Data 完整注册表、初始材料、覆盖、统计和数据版本关系完全相等；旧记录去掉冗余字段后与新记录逐字段相等。旧例中三条 notes 都是静态说明；真实动态缺失诊断另有专项回归。

程序检查严格字段、真实引用、材料身份、记录覆盖及重放一致性。这些检查不证明模型推断的安全／传播语义正确。实测案例的源头范围、处理前后版本和交互边界仍分别记录助手复核意见；后续 DOE 应读取事实和未决，不把 `complete` 当作隐私结论。

## 6. 本轮实际交付

新实验目录为 `experiments/propagation/runs/doe-input-v1-20260924-193407/`。

- [三例总览](../../experiments/propagation/runs/doe-input-v1-20260924-193407/index.html)
- [助手复核总览](../../experiments/propagation/runs/doe-input-v1-20260924-193407/assistant-review.md)
- [工程验证](../../experiments/propagation/runs/doe-input-v1-20260924-193407/verification/summary.json)

| 样例 | 标注状态 | 传播状态 | Data | 已记录 IR | 未决 |
|---|---|---|---:|---:|---:|
| 001 / N01 | complete | complete | 7 | 12 / 12 | 0 |
| 010 / Q04 | incomplete | complete | 18 | 18 / 18 | 5 |
| 013 / F01 | incomplete | complete | 20 | 18 / 18 | 4 |

实际完成三次逻辑调用与三次 HTTP 尝试，无重试、修复或择优。请求模型为 `deepseek-v4-flash`，返回标识为 `deepseek-flash`，按原记录分别保留。三例禁网离线重放一致。全套回归 1900 项通过；之后补充的验证工具测试 9 项通过，其中新增 5 项。9241 个受保护文件未变。

助手复核发现的主要边界是：001 的本地执行归因没有充分证明模型不可见；010 的检索响应新增来源未明确绑定，普通返回被推断为直接用户输出；013 只建立字段级来源，相关容器余部尚未建模，网络边界推断仍需依据。四个返回接收方未决保留在 013 原始结果中。没有为使结果“通过”改写标注或重跑模型。

三份实际 HTML／Markdown 已核对数据来源、IR 顺序、链接及重复生成的一致性；未做三例逐页截图验收。结构检查、助手语义复核和模型实际输出在验收记录中分别说明。
