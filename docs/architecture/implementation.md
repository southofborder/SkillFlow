# SkillFlow 实现与使用说明

读取多文档 Skill，提取指令、基本块和连边，由确定性编译器分配编号并检查 CFG
结构与引用。工具不执行 Skill 本身，也不将结构检查通过视为原文语义已被完整覆盖。

## 安装与统一入口

在仓库根目录安装开发版本：

```powershell
python -m pip install -e .
skillflow --help
```

安装后可从任意目录使用 `skillflow`，或等价的 `python -m skillflow`，不再依赖
手动设置 PYTHONPATH。实验工具须在仓库根目录使用 `python -m tools.*`；它们不随生产包安装。旧的 `skill-ir-analyze`、`skill-ir-flowchart` 和
`run_online_examples.py` 已移除；旧模块路径不提供转发。

```powershell
skillflow analyze --input examples/graph/simple_skill --output analysis.json
skillflow analyze --input examples/graph/simple_skill --candidate candidate.json --output offline.json
skillflow render --input analysis.json --output graph.mmd
skillflow experiment --config experiments/configs/sol_max.json --output-dir results/skill-ir
```

`--env-file` 可放在子命令前或后，指定配置文件。从仓库外运行时，使用输入、实验配置
与环境文件的绝对路径。未提供 `--env-file` 时保留最近 `.env` 的发现规则。
`analyze --candidate` 不调用模型，不要求 API 密钥；`render` 也不调用模型。

退出码：0 表示成功；1 表示分析 degraded 或实验包含失败；2 表示输入、配置或执行错误；
130 表示用户中断。实验单项失败会继续后续任务，完整结果保留在报告中。

## 代码目录与依赖

```text
src/skillflow/
  graph/          原 IR、提取、结构校验、受控核对 audit、反馈与建图实验
  propagation/    联合标注 annotation、聚焦审查 review、Data、规格与离线求解
    contracts/    安全 profile、运行时／表示契约与固定 sink 边界规则
  common/         输入、LLM／SSE、调用记录、文件保存、实验保存与历史地址解析
  cli.py          skillflow 的 analyze / render / experiment 统一入口
formal/           Lean 事实保持与结构证明
experiments/configs/ 实验配置；只声明模型与输入，不保存凭据
experiments/datasets/ 生产实验的数据集定义
tools/
  graph/          baseline / audit / feedback 实验工具
  propagation/    annotation / review 与传播实验工具
  corpus/         冻结评测集及 PDF 生成工具
experiments/
  graph/          baseline / audit / feedback 历史材料与新运行
  propagation/    标注、审查与传播运行材料
  corpus/         语料、包外标注与来源锁
  migrations/     物理搬迁与历史字节身份清单
```

命令入口调用实验管理或提取流程；提取流程依赖输入加载、模型客户端与 IR 编译校验。
IR 不依赖 LLM、实验管理或命令行。结果输出模块消费已有分析结果。
测试按相同职责分组，手工演示 CFG 位于 `tests/fixtures`。

安全标注独立运行，不改变建图或反馈入口。其模型输入为完整可读 Skill、选定的完整
CFG JSON 及固定执行模型；输出每条 IR 的 `operator`、`roles`、`effects`、`evidences`，
以及图外的 `locations`、`transfer_specs`。当前安全标注为 v10：`operator` 是参与动作执行的主体，允许 `llm`、`agent_runtime`、
`tool`、`human` 多值，仍与 roles 一样去重；旧字段 `actor` 不作为兼容别名。
`effects` 按有依据的发生阶段排列，允许重复；证据以零起始 `effect_index` 对应每次出现。
新增 `context_write` 表示创建、更新或删除共享运行时、会话或环境条目，普通结果定义不自动算上下文写入，
模型实际接收内容仍使用 `model_observe`。纯控制或原样传递等没有适用效果时可有依据地
保留空数组；确实无法完成必要判断时记录 semantic_failure。空效果不等于 nop 或入口／出口状态相同；删除上下文绑定
也不自动表示读取旧内容。部分顺序用 order=partial 与程序生成的 precedence 计算，不能默认先保护后观察。
固定执行模型为 `skillflow-abstract-runtime-v5`，所有 Skill 共用一份规则；独立运行使用 `skill-ir-security-profile-v11` / schema 11，业务标注为 v10。默认可能行为、明确机制和适用边界统一见[抽象运行时契约](../propagation/SkillFlow-统一抽象运行时契约.md)；
位置声明保留 `kind/name/operand_refs/access_scope/retention`，状态位置仍使用 `kind/name`；安全标注与传播规格的证据编号统一为 `ref_id`。
模型响应另带 `location_evidences`，校验后独立保存为 `audit/location-evidences.json`；业务结果和传播快照不复制该表。
旧运行和旧标注均明确拒绝，不自动迁移或重新解释。
联合标注本身不执行传播、风险评分或必要性判断；合法编译结果交给独立传播入口求值。使用方法见
[标注规范](../propagation/Skill-IR安全语义标注规范.md) 与
[30 图首次实验的历史记录](../../experiments/propagation/annotation/README.md)。历史标注保持原版本；当前入口不重解释或续跑旧记录。

模型声明接收方、访问范围和留存性质，程序生成六类 sink 及固定 `exposure_level`，不让模型自由数字打分。编译业务材料为 profiles、locations、transfer_specs、sink_boundaries 四项；profile 仍四字段。纯任务内部工具和临时状态继续传播但不进入暴露清单，删除不交付旧内容。网络未知的工具参数用 null-effect 的 deliver → tool，不能以工具响应依赖代替请求交付。等级只表示边界范围和留存，具体数据敏感性和任务必要性留给 DOE。详见[Sink 边界与固定分级](../propagation/SkillFlow-Sink边界与固定分级.md)。

联合标注之后可独立执行[三任务聚焦审查](../propagation/SkillFlow-联合标注三任务聚焦审查.md)：
检查无依据收窄、数据关系和观察／交付绑定。审查只读加载合法标注，每图一次调用，
不修改历史原结果。`python -m skillflow.propagation.review` 提供 `prepare/run/replay`，以及 `refine`：初审有明确问题才完整修复一次，再独立复审，最多三次调用。语义任务失败不冒充空问题清单；复审无问题不代表已经证明语义正确。
职责及失败边界见[表示契约与一次标注修复](../propagation/SkillFlow-表示契约与一次标注修复.md)。

提取、语义核对及标注的提示词指令统一使用英文，模型解释及审查报告继续使用中文；
源文件、代码和证据引文保留原语言。提取时必须拆开先后或中间数据版本有意义的
多个明确动作，同一原子调用仍可具有多个 effects，黑盒内部不会凭空展开。更新和
早期改动见 [操作粒度与有序效果的 v2 历史记录](../history/skill-ir/Skill-IR操作粒度与有序效果更新.md)，
当前变更及离线验收见 [上下文写入与执行主体更新](../history/skill-ir/Skill-IR上下文写入与执行主体更新.md)。

```powershell
python -m skillflow.propagation.annotation prepare --input path/to/skill --analysis analysis.json --run-dir path/to/new-run
python -m skillflow.propagation.annotation run --run-dir path/to/new-run --env-file .env
python -m skillflow.propagation.annotation replay --run-dir path/to/new-run
```

独立的 `skillflow.propagation.data` 使用唯一 `Data` 表示来源、部分与处理结果，由 `DataRegistry`
管理稳定身份、描述细化、排除／字段覆盖关系及 v4 JSON 快照。`resolve_part` 确定性解析
字面值、未知部分和经过覆盖／排除的子视图，`revision` 记录已有描述变化。描述细化保持整体身份，内容变化产生
新结果；可能依赖不等于输出包含输入明文。模块不读取 CFG 以猜测操作语义，不调用
LLM，也不实现传播、观察记录或 DOE 判定。契约见
[Data 数据结构与更新规则](../propagation/SkillFlow-Data数据结构与更新规则.md)。

安装包后，从仓库根目录运行综合示例和聚焦测试：

```powershell
python examples/propagation/data_model_demo.py
python -m pytest tests/propagation/data -q
```

示例只向标准输出打印注册表 JSON，并核对导出恢复一致性，不执行 Skill、不读取真实
敏感数据，也不写产物。`build_demo()` 可供其他 Python 示例直接调用。

独立的 `skillflow.propagation` 离线解释 v9 联合标注经观察编译后的 IR 传递规格，执行前向 may 求解。
单一 `events → atomic_ops` 序列描述效果内的读取、接收、传递、写入、选择、排除、覆盖、
构造和计算；`output_bindings` 只登记公开结果别名。未知函数保留 possible 依赖，原样
读取不因已知字段而自动缩小，不执行 Skill 或在传播中调用模型。

`PropagationRecords` 在图外保存完整入口／出口状态与实际 Data 绑定，记录外壳升级为
`skillflow-propagation-record-v9`。原子操作 inputs/outputs 直接保存有序的 Data 候选集合列表，不再复制 ref、位置索引或逐步骤 notes。紧凑快照只保留记录及材料摘要，恢复时必须显式提供原 CFG、四项业务标注、注册表和初始状态。
工作队列重新求值替换静态记录，不增加实际运行次数；partial 候选次序及必要因果继续保留，已有观察不会被
后续删减撤销。支持基本分支和稳定输入的重试；生成数据反馈明确停止为 unsupported_feedback，
不以迭代上限冒充收敛。详见[算法与 IR 传递规格](../propagation/SkillFlow-传播算法与IR传递规格.md)
和[传播记录规范](../propagation/SkillFlow-传播记录结构与更新规则.md)。

```powershell
python examples/propagation/propagation_demo.py
python examples/propagation/propagation_demo.py --records-only
python examples/propagation/propagation_demo.py --output path/to/new-authored-demo
python -m skillflow.propagation run --annotation-run path/to/current-annotation-run --run-dir path/to/new-propagation
python -m skillflow.propagation replay --run-dir path/to/new-propagation
python -m pytest tests/propagation -q
```

示例构造合成材料和手写规格，离线校验引文后实际求解；默认打印唯一业务结果，
`--records-only` 只打印 IR 记录，`--output` 与正式运行共用保存流程。旧 `propagation_record_demo.py` 已删除。
新运行仅以 `doe-input.json` 作为后续 DOE 的业务输入，内含完整源文、CFG、位置属性、sink 清单、执行主体／角色、扁平 Data 和紧凑记录；
标注长文、身份键、证据及求解统计保存在 `audit/`。不再并行导出 `result.json`、`data.json` 或 `records.json`。
离线重放写入 `replay/summary.json` 与报告，链接原主文件；不复制第二份业务结果。报告 MD／HTML 复用同一视图模型。
Python `propagate` 可注入 DataRegistry 和完整初始 FlowState；CLI 可配套提供 `--seed-data`
与 `--seed-state`。显式初始状态包含缺失绑定的含义，不会在后续读取时重新自动造来源。

包顶层 API 保持可用：

```python
from skillflow import analyze_skill, render_mermaid, serialize_analysis_result, run_experiment

result = analyze_skill("path/to/skill")
payload = serialize_analysis_result(result)
run = run_experiment("path/to/experiment.json", env_file="path/to/settings.env")
print(run.status, run.run_directory)
```

`run_experiment()` 在所有配置、输入与凭据通过前置检查后才调用模型；前置错误抛异常。
执行结果提供 `run_directory`、`status`、`report`。Python 调用还可传入 `environ` 映射，
跳过自动环境文件发现，方便嵌入其他工具或测试。离线候选与在线结果均继续使用原有
分析 JSON 格式；`attempts=0` 明确表示离线编译。

## 统一运行时契约与三例复测

当前联合标注 v10 区分逻辑来源、实际读取、模型观察和明确取值；`receive` 可以在 `tool` 边界取得网络未知或本地的工具返回，不再强制等同于网络接收。它保留获取来源与请求依赖，纯计算仍使用 `compute`。标注运行为 `skill-ir-security-profile-v11`（格式 11），Data 为 v4，唯一业务交付为 `skillflow-doe-input-v7`，传播运行为 `skill-ir-propagation-v10`（格式 10）。表示契约为 v3、编译器为 v4；共享语义解释契约仍为 v4，核对和反馈仍为 v5。DOE 顶层 execution_model 只保存冻结契约 version/sha256；完整规则和推断证据在已有审计材料中。

来源整体不能被目标字段名称自动替代；明确局部接口、隔离机制和本地处理仍须尊重。整体观察不意味着调用参数也是整体。位置种子按实际 read/append 与值引用建立，不为未使用的上下文操作数额外制造叶子来源。详见[来源范围与工具返回通用修正](../history/skill-ir/SkillFlow-来源范围与工具返回通用修正.md)。

```powershell
python -m tools.propagation.run_runtime_pilot prepare --run-dir path/to/new-processing-run
python -m tools.propagation.run_runtime_pilot run --run-dir path/to/new-processing-run --env-file path/to/settings.env
python -m tools.propagation.run_runtime_pilot replay --run-dir path/to/new-processing-run
```

三例调度固定复用 `source-boundaries-v1-20260928-112118` 的冻结源包与 selected-analysis，核验 source、selection、原轮次图和字节摘要，不重新建图或语义反馈。三例至多三次计划内联合标注调用，接受响应后不自动重发或择优补跑；HTTP 暂态传输尝试另计。prepare/replay 零 API；用户中断不启动后续调用。旧 run_pilot.py 的重建诊断流程及其历史运行保持独立身份。上面的通用 prepare 命令使用新目录；`processing-v1-20260928-204710` 的原位替换属于当时单独授权的历史实验，不是后续运行的默认行为。最新一次审查修复实验另存于 `experiments/propagation/review/runs/repair-once-v1-20260929-132248`，没有覆盖上述三例和 30 例交付物；观察属于契约下的静态可能行为，不是执行日志。

## 模型与服务配置

当前项目 `.env` 按用户要求使用 DeepSeek 官方服务
`https://api.deepseek.com/chat/completions`、`deepseek-v4-flash` 和请求推理档 `max`。
这些是本地配置，不改变下表中的代码默认值，也不限制实验工具可使用的模型。
首次提取和后续修复共用同一配置，不自动切换模型、服务或降低推理强度。

语义复核的新模型批次使用 `experiments/graph/baseline/deepseek-v4-flash.json`。
旧 `sol-max` 配置及记录保留原模型身份，不能通过更换 `.env` 把两种模型的结果拼成同一批次。
2026-09-10 官方接口接受了请求名 `deepseek-v4-flash`，实际响应的 `model` 为
`deepseek-flash`；预检记录同时保存两者，后续以每次响应元数据为准。

| 环境变量 | 含义 | 默认值 |
| --- | --- | --- |
| LLM_API_KEY | 与服务配套的密钥 | 必填，仅在线运行需要 |
| LLM_ENDPOINT | Chat Completions 完整地址 | https://api.openai.com/v1/chat/completions |
| LLM_MODEL | 服务接受的模型标识 | gpt-5.6-sol |
| LLM_REASONING_EFFORT | none / low / medium / high / xhigh / max | max |
| LLM_TIMEOUT | 连接及阻塞读取超时，毫秒；不是流式生成总时限 | 600000 |
| LLM_MAX_RETRIES | 临时网络错误的额外重试次数 | 2 |
| LLM_RETRY_BASE_MS | 初始重试间隔，毫秒 | 500 |
| LLM_RETRY_MAX_BACKOFF_MS | 最大重试间隔，毫秒 | 8000 |

进程环境优先于环境文件；实验变体显式填写的非密钥字段又优先于这些默认值。
每次实验开始时一次性解析全部配置。不同变体通过 `api_key_env` 引用不同环境变量，
而不是在实验文件中写密钥。`OPENAI_*` 不参与此包的配置。模板见 [.env.example](engine-env.example)。
显式环境文件不存在时直接报错，不回退到其他文件。配置读取不修改进程环境。

请求使用 `reasoning_effort`，不携带 `temperature=0`。第三方服务是否实际遵循
该参数，取决于服务实现；报告记录请求值，不将其视为服务内部执行方式的证明。

## 实验定义

数据集只包含待分析对象；增加或删除案例只修改 JSON，不修改 Python。
输入可以是目录或 ZIP，不强制存在 SKILL.md。所有相对路径以声明它的 JSON 文件
所在目录为基准，不以进程工作目录为基准。

数据集示例：

```json
{
  "cases": [
    {"id": "case-a", "input": "../skills/a"},
    {"id": "case-b", "input": "../skills/b.zip"}
  ]
}
```

实验示例：

```json
{
  "name": "reasoning-comparison",
  "dataset": "../datasets/smoke.json",
  "repetitions": 2,
  "variants": [
    {"id": "max", "model": "gpt-5.6-sol", "reasoning_effort": "max", "max_repair_rounds": 3},
    {"id": "high", "model": "gpt-5.6-sol", "reasoning_effort": "high", "max_repair_rounds": 3}
  ]
}
```

实验名、案例 ID、变体 ID 使用 1–64 位英文字母、数字、下划线或连字符，首位为字母
或数字，避开 Windows 保留文件名；同一类别的 ID 忽略大小写后必须唯一。
变体可覆盖 `model`、`endpoint`、`reasoning_effort`、`timeout_ms`、`max_retries`、
`retry_base_ms`、`retry_max_backoff_ms`；另有 `api_key_env`（默认 LLM_API_KEY）和
`max_repair_rounds`（默认 3）。未写参数沿用环境默认值，未知字段直接报错。

执行顺序固定为案例 → 变体 → 重复序号，串行执行。案例、变体列表不能为空；
重复次数至少 1，超时与间隔必须为正整数，重试与修复次数可为 0。
同一实验固定当前 Prompt 构建逻辑，输入包在前置检查时读入内存，后续各任务复用，
避免执行期间文件变化干扰对照。本轮没有 Prompt 模板切换、语义评分、自动排名或断点续跑。

## 产物与评测指标

默认输出根目录为启动目录下的 `results/skill-ir`，可用 `--output-dir` 覆盖。
每次新建时间戳加随机后缀的运行目录；历史结果不会覆盖。

```text
<输出根目录>/<实验名>/<运行ID>/
  experiment.json       解析后的配置快照，不含密钥
  dataset.json          输入位置、文件信息与内容摘要
  report.json           持续更新的进度与总体/分变体汇总
  summary.csv           每次任务一行，便于人工对照
  trials/<案例ID>/<变体ID>/<重复序号>/
    analysis.json       原格式分析结果
    candidate.json      存在候选时生成
    graph.mmd           有通过检查的 CFG 时生成
    trace.json          首次提取与各轮修复的 Prompt、响应和 HTTP 尝试
```

目录摘要是加载后提取输入（文件路径、类别、大小、可读文本）的 SHA-256，另外保存
每个可读文件的文本摘要；它不是未读取二进制内容的摘要，也不能取代原始数据备份。

任务状态为 not_run / running / complete / degraded / error / interrupted。
前置检查失败不会创建运行目录或调用模型；执行开始后单项失败会记录错误并继续。
中断时保存活动任务与此前调用，后续任务保持 not_run；不在下次启动时自动续跑。
报告及跟踪文件通过临时文件替换写入，避免读取到写了一半的 JSON。

报告分别统计逻辑生成尝试、修复尝试、HTTP 尝试和额外 HTTP 重试。结构通过率与首次
通过率以已结束或已中断的实际执行任务为分母，不含 running 和 not_run。
首次通过要求第一次逻辑生成即通过结构检查，HTTP 重试不视为模型修复。

记录耗时、诊断、块数、边数、已知 token 用量及有用量信息的响应数。服务未返回的
模型标识、请求 ID 或用量记为缺失，不当作 0；部分响应有用量时只汇总已知部分，
通过响应数判断覆盖情况。原始服务用量字段同时保存在 trace 中，不内置价格或估算账单。
块数与边数仅用于描述，不能据此判断语义质量。

`LlmClient(record_calls=True)` 启用 `call_records`；可提供 `on_record` 进行增量保存。
默认不记录，`complete()` 仍返回助手消息内容。实验记录会移除所有本次配置密钥，
包括服务意外回显到错误、响应或 Prompt 中的密钥，返回的实验报告同样脱敏。

## 指令和操作数

`IRInstruction.id` 和 `ir_007` 格式保留。`opcode` 是 LLM 给出的语义字符串，
没有独立的 `Opcode` 枚举或业务操作白名单；附加信息保存在 `metadata`，
原候选指令标识保存在 `draft_instruction_id`。

| `Operand.type` | 标识或内容 | 用途 |
| --- | --- | --- |
| `result` | `identifier="result_004"` | 指令结果；在输入中使用，在输出中产出 |
| `context_key` | `identifier="user_request"` | 上下文条目 |
| `external_resource` | `identifier="weather_api"` | 文件、服务、工具或 API 标识 |
| `literal` | `literal_value="sunny"` | 直接写出的常量 |

```json
{"type": "result", "identifier": "result_004", "semantic_name": "weather_type"}
```

结果编号全图唯一。候选结果先登记再解析引用，因此候选块排列不必与执行顺序相同。
`semantic_name` 保留 LLM 给出的语义名；给结果编号不删除该含义。
非 literal 操作数不能附带 `literal_value`，包括显式 null。旧字段不作为别名接受。

## 基本块、来源与连边

基本块使用 `instructions`、`data_source_kind`。上下文条目由
`declared_context_keys` 声明；该声明不能替代实际读取。

- 读入块包含一条获取指令和一条终结指令，并至少产出一个结果。
- `data_source_kind="context"` 的获取指令使用非空、仅由 `context_key` 构成的输入。
  其他位置不能使用原始上下文条目。操作名优先说明读取什么，例如 `read_city_from_request`；来源由结构确定。
- `data_source_kind="external"` 的获取指令至少使用一个外部资源或已有结果。
  普通计算和不读入返回数据的副作用可使用 `data_source_kind=null`。
- `http_get`、`read_db` 等名字不触发专有业务检查；不按操作名称自动补来源或 effect。
- 有后续跳转的块以 `dispatch` 结束，结束执行的块以 `return` 结束。
  两者不能产出结果，之后不能再放指令。
- `dispatch.inputs` 记录分支使用的数据。连边的 `condition_text` 保存条件文字，
  不替代结果引用，程序也不解释该文字来证明条件覆盖或可行性。

连边来自候选。程序不补边，不恢复逐块转交声明。

Prompt 对操作名和结束块还有两项提取偏好：

- 操作名表达具体动作及对象；原文明确给出的函数或工具名称照原名保留。
  同一行为可以在不同分支使用同一名称，不为命名增加原文没有的处理步骤或 effect。
- 行为之后直接结束时，可在该行为块末尾使用 `return`；独立分支可以只有 `return`。
  直接返回原文给定的常量或已有结果时，不额外创建准备、赋值或包装结果的指令。
  保留真实的分支、合流和独立行为边界，不以减少纯 `return` 块为目标。

这些是 Prompt 的提取指导，不是新的校验硬限制；编译器不会自动合并块、改边或重命名操作。

## CFG 完整性检查

`ControlFlowGraph.validate_integrity()` 对调用时的实际对象完整重验，先检查字段规则，
再检查结构与引用。通过时返回 True，失败时抛出带定位信息的 `CFGIntegrityError`。
构造时的字段归一化不代表图已通过完整性检查；修改后的对象不会在重验时被静默修复。
`ir/validation.py` 检查结构、全局标识、声明与引用，并按产出块缓存图可达性。
它不计算每个块的完整可用结果集合，不累积处理历史。

检查涵盖：入口及边端点、重复边/指令/结果标识、终结位置和出边、读入形状、
缺失产出、块内先读后产出，以及没有路径支持的跨块读取。
`RESULT_NOT_DEFINED`、`DUPLICATE_RESULT_IDENTIFIER`、`RESULT_READ_BEFORE_DEFINITION`、
`RESULT_PATH_NOT_FOUND` 分别标识缺失、重复、局部顺序和跨块路径问题。
诊断保留块名称、结果语义名、指令编号与输入位置，供定位和模型修复使用。

单分支产出在合流后被引用、跨块结果经回边到达，允许通过引用连通性检查。
这不证明结果在所有路径或首次迭代中都可用。声明入口和无前驱块作为入口，
支持独立行为片段，拒绝不可达孤立环；不要求所有路径结束，也不证明终止。
仅凭图不能发现原文中被整体遗漏的行为，这属于后续语义回溯的工作。

字段重验使用实际值和字段显式设置情况的快照，保留默认空值与显式非法字段的区别；
不会先通过 JSON 导出删除字段，也不会改动待验证对象。新增 `CFG_SCHEMA_INVALID`
诊断说明字段非法或内存状态必须被归一化/重建才能接受，原结构错误码继续保留。

完整规则、证明对象及未保证的性质见
[结构规范与验证边界](../graph/Skill-IR结构规范与验证边界.md)。
[独立形式核心](../../formal/README.md) 提供 Lean 参考检查器、机器检查证明和差分验收入口；
生产编译与渲染不依赖 Lean。形式证明覆盖核心模型，Python/JSON 桥接的一致性由测试验证，
不宣称自然语言到 IR 或生产 Python 实现已被端到端证明。

## 可选分析与后续阶段

`skillflow.graph.analysis.availability.analyze_availability(cfg)` 提供可能/保证结果集合、
回边与必经块等辅助信息。编译、完整性检查、绘图及实验管理均不自动导入它，
包顶层也不导出它。这不是 effect 传播或审计实现。

独立的 `python -m skillflow.graph.audit` 提供受控语义回述与完整源文核对（v5）：
Lean 打印/解析受控文本，程序核验完整字段与定位，模型每案例只做一次原文—受控文本核对。
核对与反馈共用版本化 IR 解释契约。v5 将七类检查点保留为阅读提示，由模型合理组织语义核对项；保守依赖说明仅在适用时填写，不将其余保留项自动称为精确。保守只允许依赖精度损失，不能掩盖明确错误。原图 IR 不增加字段。详见 [解释契约与逐项核对规范](../graph/Skill-IR解释契约与逐项语义核对规范.md)。`--suite semantics-v5-seven` 可运行 F01 五例与暂停批次001、010第0轮图的独立七例诊断。
它需要单独构建形式化打印器，不改变生产提取接口。使用方式与保证边界见
[受控回述实验](../../experiments/graph/audit/README.md)。旧回溯运行代码已清理，历史产物保留。

独立的 `python -m skillflow.graph.feedback` 在现有提取与核对外增加有界反馈：有明确差异时，
向下一轮提取请求追加当前图、已核验的引文和定向建议，重新生成完整候选；每轮独立核对
同一完整源文与新图的受控文本。默认最多 3 次语义修复，与每轮最多 3 次结构修复分别计数。
必要判断确实无法完成时以 `semantic_failure` 停止；契约默认和保守候选不因缺少实现细节自动失败。只有有效业务项全部为 `represented` 且其余检查通过时，才称“核对器通过”。

```powershell
python -m skillflow.graph.feedback run --input path/to/skill --run-dir path/to/new-run
python -m skillflow.graph.feedback run --input path/to/skill.zip --initial-analysis path/to/analysis.json --run-dir path/to/seeded-run --max-semantic-revisions 3 --max-structural-repairs 3
python -m skillflow.graph.feedback replay --run-dir path/to/seeded-run
```

`run` 可传 `--env-file`，两个命令均支持 `--renderer`。Python 服务
`skillflow.graph.feedback.refine_skill` 可分别注入提取与核对客户端。恢复优先使用已接受响应，
不自动重发不确定请求；`replay` 不创建在线客户端。详见
[反馈闭环规范](../graph/CFG构建语义反馈闭环.md) 与
[F01 首次反馈实验](../../experiments/graph/feedback/README.md)。

反馈运行 v5 保留 `--max-audit-execution-retries 2`（默认 2，允许 0–5），与独立核对共用 `audit_execution`：仅核对发生明确的暂态传输失败时，使用同一 Prompt 创建独立记录的新尝试，默认退避 5 秒、10 秒。首个完整响应后停止，坏 JSON、证据错误、语义失败或语义差异不会触发通信重试。核对轮次、执行尝试、HTTP 尝试与两类修复分别计数；旧版运行不迁移，使用新目录。配置默认等待时间为 10 分钟，历史实验显式配置保持原样。合法保守项可通过且不触发修图，但结果与选择记录保留 `representation_summary`（保留项及其保守子集），不能当作严格语义等价或必定传递。

独立 Security Profile 已提供动作标注与图外传递规格，Data 和 propagation 已提供基础
传播求解及静态记录；一般数据反馈循环、必要性和 DOE 暴露判断仍属后续工作。模型核对
结果和传播 complete 均不是形式化语义等价证明。

## 验证与历史结果

```powershell
python -m pip install -e .
python -m pytest tests -q
```

默认测试使用离线候选、模拟 HTTP 和临时目录，不产生 API 用量。
仓库外运行验收使用已安装包，故运行测试前需完成开发安装。
生产 Prompt 示例也会被编译检查；历史候选可通过新 analyze 命令离线重编译。

旧方案曾使用 `results/ir/` 保存实验；当前已冻结的语义评测实验在
`experiments/graph/baseline/`，交付输入和 CFG 图片分别在仓库直属的
`dataset/skills/`、`result/ir-IPP/`。测试中的离线重编译不代表新一轮在线验证。

## 处理段、字段关系与观察编译（标注 v10／编译 v4）

一次联合标注输出处理段，编译器生成最终观察事件。`filter_items` 保留原集合成员，
单层 `for_each` 保留同一元素的字段配对；不执行真实集合，不改变已有 CFG。
参见[主规范](../propagation/SkillFlow-字段关系与观察编译.md)。
业务标注 v10、标注运行 v11（格式 11）、Data v4、记录 v9、DOE v7、传播运行 v10（格式 10）；不迁移历史结果。
原始处理段、编译响应及映射均在 audit 中，DOE 主文件只保留事实。

当前 sink 三例验证使用 `tools/propagation/run_sink_pilot.py prepare/run/replay/summarize`；复用已核验最新三个 base 的冻结源包与 CFG，不重新提取或反馈，每例一次标注。新目录前缀为 `sink-boundaries-v1-`，已有实验保留原版本身份。

三例工具仍使用 `tools/propagation/run_runtime_pilot.py prepare/run/replay`，
通用新目录前缀为 `processing-v1-`，只复用固定三图，不触发提取或反馈；历史结果不覆盖；本轮七例修复工具见 `experiments/propagation/review/README.md`。

## Sink 收紧与可选参数

部署未说明的工具保留 tool/recipient/null，不凭发送动词补 net_send。build 的成员新增可选 Boolean when，原值与存在条件分开；编译观察共用条件，控制不成为请求载荷。deliver 与 receive 复用唯一配对的请求绑定。DOE 主文件只增加成员／观察的输入索引，不新增证据区，Data 保持 v4。详见[主规范](../propagation/SkillFlow-Sink标注收紧与可选参数.md)。
