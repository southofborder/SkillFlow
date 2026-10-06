# Security Profile 批次工具与历史标注实验

当前工具在 CFG 构建之后，单次标注整图动作的 `operator`、`roles`、有序 `effects`、`evidences`，并生成位置和 IR 传递规格。
每条 IR 对应一份严格四字段 profile，操作 ID 保存在外层索引中。标注模型读取完整可读 Skill、完整实际 CFG 及固定执行模型。

当前为 `security-profile-v10` / `skill-ir-security-profile-v11`（运行格式 11），执行模型为 `skillflow-abstract-runtime-v5`。
正常模型响应为 `outcome=completed`，含 profiles、locations、transfer_specs 和 location_evidences；业务输出只保留前三项，
位置证据另存 `audit/location-evidences.json` 并绑定摘要。位置声明为 kind/name/operand_refs，证据编号统一使用 ref_id。
旧 actor、位置 key/anchors、证据 location 及旧运行均拒绝，没有兼容别名或自动迁移。

标注工具本身不执行数据传播，不预测数据集合，不判断风险、必要性或 DOE，不执行 Skill 中的脚本或工具，不修改原图。

## 固定来源

使用与现有 ZIP/PNG 交付相同的 `review_set_source.build_export_plan` 核验输入原始字节、来源和历史分析摘要。编号为 001–030，对应 N01–N06、Q01–Q06、F01–F06、D01–D06、R01–R06；29 例使用历史第 1 轮，F03 使用第 3 轮。

选择源为 `experiments/graph/baseline/runs/baseline-deepseek-v4-flash-max-20260910`。不改用后续反馈修复图，不读取外置人工事实、旧评审或答案作为模型输入。这里的“结构有效”不代表原图已经得到独立的语义核对通过结论。

## 命令

在仓库根目录运行：

```powershell
python -B -X utf8 -m tools.propagation.annotation.run_review_set prepare --run-dir experiments/propagation/annotation/runs/<new-id>
python -B -X utf8 -m tools.propagation.annotation.run_review_set run --run-dir experiments/propagation/annotation/runs/<new-id> --env-file .env
python -B -X utf8 -m tools.propagation.annotation.run_review_set replay --run-dir experiments/propagation/annotation/runs/<new-id>
```

`run` 可以直接用于新目录，也可以接着已准备的同一目录运行。`prepare` 不读取密钥、不创建模型客户端；`replay` 不读取环境文件、不创建在线客户端，仅使用已保存响应。批次和逐例清单绑定输入、配置、源码、词表及执行规则身份，变更后不得沿用旧记录续跑。

线上配置固定为已有官方 DeepSeek 配置文件中的 `deepseek-v4-flash`，不把密钥写入清单。实际模型返回名称、用量、HTTP 尝试与不完整响应照实保存在调用记录中。每例至多一次计划内逻辑调用，共 30 次；HTTP 传输重试另计。没有自动修复响应、逐节点补问或择优补跑。

默认最多 3 个案例并行，可在首次 `prepare` 或 `run` 中用 `--workers 1` 至 `--workers 8` 指定；并发度写入清单，恢复时必须一致。调度只提交当前可运行的有限案例，完成后再补位，不预先排队 30 次调用。每例客户端和上下文独立。单例失败继续其他例；中断后不再启动新调用，已经开始的调用保存记录。离线重放会处理全部已开始案例，包括中断时仍在执行的其他案例。

## 新产物

```text
runs/<run-id>/
  manifest.json              30 图来源、源码与调度配置
  cases/001/                 单例冻结输入、三项业务材料、证据校验与完整调用记录
    audit/location-evidences.json  独立位置身份依据
  cases/.../
  progress.json              已保存的逐例进度
  experiment-result.json     批次结果与描述性计数
  report.md                  中文批次报告
  assistant-review.md        执行后逐例助手复核，单独标注
  replay/                    离线重放批次报告
```

逐例 `report.md` 按块列出动作及四字段。批次报告展示有效 profile／真实 IR 数、部分顺序 IR 数、失败、九类 effects 分布及逻辑调用计数。
效果保留顺序与重复，覆盖计数仍按具有该效果的 IR 数计算；效果数不是风险分数或数据量。

`complete` 只表示标注记录完整；`order=partial` 是按约束求解的候选顺序，不形成未完成状态。`outcome=cannot_assess` 的有效失败记录为 `semantic_failure`，不形成有效业务结果。程序核验编号和引文不等于已经证明标注语义正确。自动报告不会伪造助手或用户确认。助手实际检查全部 30 例后，在独立复核文件保留漏标、误标和证据不足。

完整标注定义见仓库 `docs/propagation/Skill-IR安全语义标注规范.md`。任意 Skill 的通用入口是 `python -m skillflow.propagation.annotation`，固定 30 图调度器不作为通用接口。

## 从源包重新提取、反馈及标注

`tools/propagation/annotation/run_full_pipeline.py` 是另一项独立实验：从相同 30 个冻结 Skill 源包重新提取 CFG，经受控回述保真检查和完整源文核对，最多进行 3 次语义修复；每轮最多 3 次结构修复。它不将历史 CFG 当初始图，也不回退旧图。

```powershell
python -B -X utf8 -m tools.propagation.annotation.run_full_pipeline run --run-dir experiments/propagation/annotation/runs/<new-full-id> --env-file .env --workers 3
python -B -X utf8 -m tools.propagation.annotation.run_full_pipeline replay --run-dir experiments/propagation/annotation/runs/<new-full-id>
```

每例反馈停止后，对该次运行的 `last_valid_cfg` 标注一次；无结构有效图则不标注。反馈仅有 `audit_passed` 才记作核对器通过，语义失败、次数耗尽或执行错误不会被改写成通过。选择末次有效图时保存真实轮次、图摘要和反馈停止原因；即使后续轮次提取失败，也如实绑定最后一张成功建成的图。用户中断后不启动后续标注。

单例目录包含 `feedback/`、`annotation/` 两个独立阶段，另有只包含本次 CFG 的 `selected-analysis.json`、选图依据 `selection.json` 与源包字节／解码文本一致性证明记录 `source-binding.json`。标注输入读取 feedback 已冻结的源包，模型不会收到反馈意见、旧判断、人工答案或基线图。

当前 full-pipeline-v10 从源包开始每例上界为 16 次提取、4 轮核对和 1 次标注，共 21 个逻辑调用单元；30 例上界为 630。核对遇到明确的暂态传输失败时最多额外重试 2 次，因此每例核对执行尝试上限 12，总执行模型调用上限 29，30 例最多 870。HTTP 层重试另计。这些都是预算上界，实际会因通过、语义失败或错误提前停止。

新批次的连接/阻塞读取超时为 600000 毫秒（10 分钟），独立写入清单；历史基线的配置文件不改写。完整响应、坏 JSON/引文/覆盖、语义失败或明确差异均不触发传输重试；用户中断和仍为 running 的不确定请求不自动重发。核对每次执行尝试保存独立记录，恢复先消费已保存响应，首个完整响应之后不再尝试。离线重放重新执行解析、编译、回述、核对、选图和标注解析，并验证停止结果和来源相同；不创建在线客户端。

新实验必须使用新目录，不能复用下面首次标注批次目录，也不迁移任何旧版全流程运行。旧响应、图和报告保持原样；新入口遇到旧版本明确拒绝，旧运行没有自动恢复。生产提取 Prompt、IR、结构规则和安全标注实现保持不变。

## 2026-09-17 首次结果

[实施与验收报告](runs/security-profile-20260917/acceptance.md)：30 次逻辑调用得到 6 例完整记录、3 例含未决记录、2 例引文错误拒收、19 例执行失败。共接受 170 条 profile，保留 7 项模型未决；没有补跑。全 30 例离线重放与原结果一致，逐例助手复核单独保存。此批次没有获得 30 份均可用标注，也不构成标注语义正确性或数据安全结论。
