# 传播离线示例与三例实验工具

主规范见仓库 `docs/SkillFlow-传播算法与IR传递规格.md`。这里仅组织实验，不维护另一套传播算法。

本轮 sink 三例入口为 `tools/run_sink_pilot.py prepare/run/replay/summarize`，复用旧加载器已核验并冻结的 001-base、010-base、013-base 源包与选定 CFG。它只做一次联合标注、离线传播和零 API 重放，生成新的 sink-boundaries-v1 目录，不调用旧建图调度器，不覆盖历史材料。

当前工具绑定联合标注 v10、Data v4、传播记录 v9、DOE 输入 v7 与传播运行 v10。
契约与源码变化后，新入口拒绝旧运行；历史输出不迁移、不重新解释、不覆盖。

`tools/run_runtime_pilot.py` 使用已绑定来源的 001/N01、010/Q04、013/F01 既有 CFG 和源包，只运行联合标注和离线传播，不重新提取。
`tools/run_pilot.py` 是来源范围实验调度器：从冻结源包重新建图并进入反馈，随后选择末次结构有效图、标注和传播。它不回退旧图。
两种调度身份分别为 `skill-ir-processing-pilot3-v4` 与 `skill-ir-source-boundaries-pilot3-v4`，不可混用。

在 `packages/skill-ir` 下执行：

```powershell
python experiments/propagation/tools/run_runtime_pilot.py prepare --run-dir experiments/propagation/runs/<new-id>
python experiments/propagation/tools/run_runtime_pilot.py run --run-dir experiments/propagation/runs/<new-id>
python experiments/propagation/tools/run_runtime_pilot.py replay --run-dir experiments/propagation/runs/<new-id>
```

正式实验使用新的空运行目录；现有运行只允许在身份一致时消费已保存响应。请求固定为官方 DeepSeek 的 `deepseek-v4-flash`，每例一次联合标注；HTTP 尝试与逻辑调用分别记录。完整但无效的模型响应不按质量重发；`replay` 不创建在线客户端。

每例 `annotation/` 保存实际提示词、响应、请求身份、模型名、用量、证据校验与处理编译材料。合法 `completed` 分支才进入离线传播。`cannot_assess` 保存为 `semantic_failure`，格式错误、执行错误和中断分别保留，均不伪造 DOE 文件。

原始模型响应包含 outcome、profiles、locations、transfer_specs 和 location_evidences。编译后的完整响应新增程序生成的 sink_boundaries；业务投影为 profiles、locations、transfer_specs、sink_boundaries 四项。位置属性包含 access_scope/retention，类型和等级由程序生成，不让模型自由打分。位置依据独立保存，编译前后规格分别绑定摘要。传播运行复核接受响应、编译和证据，不接受人工改写冒充模型结果。

边界和默认见[Sink 主规范](../../../../docs/SkillFlow-Sink边界与固定分级.md)。任务内部工具及临时状态保持传播关系，但不进入暴露清单；删除不交付旧值。DOE 清单关联已形成记录的操作，覆盖缺口不被清单为空掩盖。当前三例 sink 验证使用新的独立目录，仅复用已冻结源包和 CFG，不重新提取或反馈。

传播交付 `propagation/doe-input.json` 是唯一权威业务事实文件，Data 只保存一次。旁置 audit 保存原始材料、恢复身份及证据；HTML 和 Markdown 供人审。总览链接可用结果和失败原因，助手意见与程序检查分开。

`order=partial` 是可计算的候选顺序；必要先后约束与因果关系继续保留。生成型反馈、缺失绑定与保守候选如实报告，传播完成不表示实际执行发生过，也不等于无数据暴露。

`examples/propagation_demo.py` 是手工规格驱动的离线示例，不是模型实测。生成 HTML、业务文件与审计材料：

```powershell
python experiments/propagation/tools/render_demo.py --output experiments/propagation/runs/<new-demo-id>
```

手工示例记录零模型调用，不修改历史实验。`runs/pilot3-v1-20260924`、`runs/schema-pruning-v1-20260924` 等目录保留其原始版本身份。

## Sink 收紧三例调度

`tools/run_tightening_pilot.py` 使用独立身份 `skill-ir-sink-tightening-pilot3-v1`，提供 prepare/run/replay，复用已核验冻结的 001、010、013 源文与 CFG。新版仅联合标注、观察编译和离线传播，不重新提取，不启动反馈或真实一次修复；计划三次逻辑调用。每例交付 DOE 输入、变化对照和助手复核，格式失败不显示旧成功结果。运行另存于 `runs/sink-tightening-v1-<时间戳>/`，本轮已执行结果见[三例总览](runs/sink-tightening-v1-20261002-205045/index.html)。模型遵循与工程一致性分别验收，规则见[可选参数主规范](../../../../docs/SkillFlow-Sink标注收紧与可选参数.md)。
