# 来源范围、工具返回与模型观察的通用修正（v6 阶段历史说明）

本页记录来源修正阶段的设计、三例重建及当时的离线恢复流程。其联合标注 v6、旧运行身份和以下命令说明属于历史上下文，不是当前入口的兼容承诺；历史实际报告及材料不改写。现行版本、模式编译和 JSON Output 说明见[安全标注规范](Skill-IR安全语义标注规范.md)、[字段关系与观察编译](SkillFlow-字段关系与观察编译.md)及[表示契约与一次标注修复](SkillFlow-表示契约与一次标注修复.md)。

来源范围修正将“内容来源、读取范围、模型观察、明确取值和实际交付”分开表达，共用既有 CFG、四字段 profile、位置表、九种原子操作与 Data v3。当前默认执行规则已集中至[统一抽象运行时契约](SkillFlow-统一抽象运行时契约.md)，本页保留来源／工具获取的表示方式及原三例重建流程；不再独立定义宽读取与回传默认。

## 1. 两阶段各自保留什么

CFG 提取保留源文明示的来源与目标，不把执行假设写成源文步骤。例如“从请求取得 city”应能从现有操作数及操作文字认出 request 来源和 city 目标；入口标识不是实际读取范围的证明。原文只有一次获取动作时不补造独立的整包读取步骤；原文明确分为先读取、再选取时保留该次序。明确的局部接口、隔离措施和黑盒边界也照实保留。原 IR 没有新增字段。

共享语义解释契约升级为 `skill-ir-semantic-contract-v3`。核对仍独立比较完整源文与经 Lean 保真检查的受控回述，不读取安全标注、传播结果或旧判断。它检查来源、取得目标、结果身份及后续参数绑定；不能把逻辑来源标识误判成新增全环境读取，也不能用“保守依赖”掩盖明确来源的遗漏。核对与反馈响应结构仍为 v4。

联合标注在一次整图调用中区分：

| 问题 | 规格如何表达 |
|---|---|
| 内容来自哪里 | 位置声明，以及 `read` 或 `receive` |
| 读取了多少 | 整体来源或有依据的局部入口，不由目标字段名称自动决定 |
| 模型看到什么 | `model_observe` 下的 `deliver` 引用当时数据版本 |
| 最后取出什么 | 明确 `select_part` 等处理，以及公开 `output_bindings` |
| 实际传给谁 | 发送、写入、观察、用户输出各自的边界与参数 |

标注提示词指令保持英文，理由及未决说明使用中文；源文和引文保留原语言。执行主体叫 `agent_runtime` 或工具，并不能单独证明内容对模型不可见；LLM 仅调度也不能单独证明内容已进入模型。

## 2. 默认规则的统一来源

读取范围、工具返回、模型可见边界、明确局部机制及保守推断，统一按[运行时契约 EM01–EM06、EM08](SkillFlow-统一抽象运行时契约.md) 应用。它们表达契约下的静态可能行为，不能把来源整体存在写成整体观察，也不能把工具内部扫描整体直接写成模型观察整体。

本页的表示方式保持：整体可用 opaque 或未完整展开的 known_parts；明确取值以 select_part 连到公开结果；观察和交付各自引用实际数据版本。源文只要求某字段，不等于已经明确提供 getter。实际模型是否遵循规则由实测记录与复核说明，不由结构校验代替。

## 3. 工具返回不是只有网络返回

新增位置类别 `tool`，表示工具交互边界，不断言网络、不等于 profile.operator。`receive` 保持原有字段，统一表达本次调用从声明边界取得的内容：

| 情形 | 原子操作 | 效果及边界 |
|---|---|---|
| 已明确远程返回 | `receive` | `net_receive` + `remote` |
| 明确取得工具内容，网络未知或明确本地 | `receive` | `effect_index=null` + `tool` |
| 已有值的纯函数或不透明运算 | `compute` | 原有变换规则；未知影响保留 possible |
| 读取上下文／文件 | `read` | `context_read`／`fs_read` |

无标签事件仅允许既有 possible 计算，以及新增的工具 receive；不能隐藏明确网络、观察或写入。工具返回的 Data 同时保存 `acquired_from`、有序实际 `origin.inputs` 和 possible 依赖。查询参数影响返回内容，不代表返回内容全部来自参数；反过来，纯计算工具不应被一律标成独立外部来源。

操作、效果与位置类别的相容性校验由规格、紧凑记录及独立 DOE 加载复用。程序检查结构，不按工具名字或证据理由中的关键词推断业务语义。

`operand_refs` 继续表达实际操作数值与位置的关联，不能将父容器冒充已取出的字段。没有直接对应公开操作数的父容器可用空列表，随后以 read/local/select_part/output_bindings 连起关系。只有规格实际读取、追加的位置，以及真正被值引用使用的上下文入口才建立默认种子，避免额外生成无父容器的叶子来源。实际输入解析和循环依赖检查共用同一位置解析规则。

## 4. 版本、运行与审计

| 对象 | 当时的版本 |
|---|---|
| 联合标注／独立运行 | `security-profile-v6`／`skill-ir-security-profile-v6`，格式 6 |
| 固定执行模型 | `skillflow-abstract-runtime-v1` |
| 共享语义解释契约 | `skill-ir-semantic-contract-v3` |
| Data | `skillflow-data-v3`，保持不变 |
| 紧凑传播记录 | `skillflow-propagation-record-v5` |
| 唯一 DOE 业务文件 | `skillflow-doe-input-v3` |
| 传播运行 | `skill-ir-propagation-v5` |
| 三例调度 | `skill-ir-source-boundaries-pilot3-v1` |

旧运行不迁移、不重解释。DOE 主文件仍仅包含原始事实，模型证据留在 audit 中。本轮没有风险分数、必要性或 DOE 结论。

以下 `run_pilot.py` 是原来源范围修正的重建诊断流程，其已生成运行维持原版本和身份。统一契约本轮复测改用 `run_runtime_pilot.py`，复用 `source-boundaries-v1-20260928-112118` 中已经选定的三张图，不重新建图，至多三次联合标注；命令和验证见[统一契约规范](SkillFlow-统一抽象运行时契约.md)。

原三例工具从已固定的 001/N01、010/Q04、013/F01 源包重新建图。历史图仅作摘要绑定的对照，不进入初轮模型输入；运行先离线冻结 source，再调用已有反馈单例服务，最多 3 次语义修复、每轮最多 3 次结构修复。随后选择本次末次结构有效图，只联合标注一次，再离线传播。

```powershell
python packages/skill-ir/experiments/propagation/tools/run_pilot.py prepare --run-dir packages/skill-ir/experiments/propagation/runs/source-boundaries-v1-<时间戳>
python packages/skill-ir/experiments/propagation/tools/run_pilot.py run --run-dir <同一目录> --env-file <已有配置>
python packages/skill-ir/experiments/propagation/tools/run_pilot.py replay --run-dir <同一目录>
python packages/skill-ir/experiments/propagation/tools/verify_pilot.py --run-dir <同一目录>
```

可显式提供 `--renderer`。prepare/replay 不读凭据或创建在线客户端。run 顺序运行三例，单例错误保留并继续其他例；用户中断不启动后续调用。核对未通过可使用当前末次结构有效图继续诊断，但保留反馈停止状态，不称为通过图。无有效图不回退历史图；合法标注才进入传播。

每例最多 16 次提取、4 个核对逻辑单元、1 次联合标注；三例最多 63 次计划内逻辑调用。每个核对逻辑单元对明确暂态执行失败最多另试 2 次，最多 87 次执行尝试；底层 HTTP 尝试另计。完整响应的格式、语义或传播质量不触发择优补跑；恢复优先消费接受响应，不自动重发不确定请求。

```text
source-boundaries-v1-<时间戳>/
├─ manifest.json / summary.json / index.html / report.md
├─ verification/                 保护摘要、离线网络阻断与回归证据
└─ cases/001、010、013/
   ├─ source/                    本轮冻结原始源包
   ├─ feedback/                  建图、受控文本、逐轮核对及接受调用
   ├─ selection.json             末次有效图、轮次和核对停止状态
   ├─ selected-analysis.json      本轮实际 CFG
   ├─ annotation/                唯一联合标注及完整接受响应
   ├─ propagation/
   │  ├─ doe-input.json          唯一最终业务事实文件
   │  ├─ audit/                  证据、来源和恢复身份
   │  └─ report.html / report.md
   └─ assistant-review.md         助手复核，不冒充人工确认
```

总览优先展示五个问题。对比旧图按源文动作和数据关系核对，不沿用旧 IR 编号推断相同动作。反馈、标注和传播各自离线重放，验证器比较阶段结果、选择、源包绑定及传播回执；网络阻断检查单独保存 `verification/network-guard.json`，`status=passed` 且 `network_attempts=0` 才可声称零网络验收。实际模型返回名称原样保存，不凭请求名猜测服务映射。

## 5. 验收与保证边界

离线回归成对检查默认容器与明确局部接口、模型处理与本地处理、先观察后删减与先本地删减后观察、整体观察与精简参数、工具检索与纯计算、明确网络与未知网络、内容未知与地址未知，以及同一来源取得多个字段。保持原有有序效果、重复参数、返回绑定、禁传、字段更新、强弱写入、受支持循环及引用／证据检查。

三例新实测必须分别报告工程状态和实际语义表现：新增了哪些来源／观察，是否误扩大局部机制，是否将整个容器误当调用参数，是否破坏返回及禁传约束。测试通过与传播 complete 不证明模型判断正确；端到端改善也不能全部归因于单一 Prompt 修改。历史 30 例、三例旧 DOE 输入及冻结源包保持原样。

## 6. 报告保存失败时的离线恢复

如果模型响应已经接受、传播事实已经求出，而报告渲染失败导致传播 manifest 尚未提交，原运行仍标记为未提交，不能在原目录补造成功标记。来源修正当轮提供的 `experiments/propagation/tools/recover_reports_offline.py` 当时只处理 source-boundaries v1 / 联合标注 v6 的报告错误，不迁移旧契约，不新增模型调用。下文是那一轮的恢复记录；当前同路径工具已随契约升级，不能用它继续旧 v6 记录，也不能把旧恢复回执冒充当前 v8 标注的验证材料。

恢复分两步，必须等在线三例全部停止后执行：

1. **修复源码前 capture**：在原源码身份下对该例反馈和标注执行离线重放，验证实际选图、三个源快照、精确 Prompt、接受响应、证据及原传播事实。回执绑定原始材料的字节摘要和源码摘要；不改变原阶段结果，重放输出使用已有 replay 子目录。
2. **报告修复后 recover**：仅允许源码变化为 `propagation/report.py`。再次确认原材料未变，通过 `SavedResponseClient` 精确匹配 Prompt 并验证原接受响应，使用既有传播与保存服务在全新目录重算。原有 DOE 文件存在时，新旧业务文件必须逐字段一致，否则拒绝保存。新运行保留原始 call/transport、模型名及用量，并在审计 provenance 中绑定捕获回执和旧／新源码身份。

```powershell
python packages/skill-ir/experiments/propagation/tools/recover_reports_offline.py capture --case-dir <原运行>/cases/001 --receipt-dir <原运行>/offline-recovery/cases/001/capture
# capture 完成后才能修复 propagation/report.py；原清单不改写。
python packages/skill-ir/experiments/propagation/tools/recover_reports_offline.py recover --receipt-dir <原运行>/offline-recovery/cases/001/capture --run-dir <原运行>/offline-recovery/cases/001/propagation
```

两个命令都内置 socket 和在线客户端创建阻断。中断、未接受或无效的标注不得恢复；有效但未决的标注仍保留未决。工具检查独立 DOE 加载、完整运行加载以及修复后源码身份下的零 API 重放，结果保存在新传播目录的 `recovery-check.json`。原三例调度的报告保存失败仍保留，恢复成功只表示新建的离线传播运行通过检查，不追溯改写原端到端状态。

## 7. 本轮实际结果（2026-09-28）

新运行是 `source-boundaries-v1-20260928-112118`。三例共 14 次逻辑调用、15 次 HTTP 尝试，联合标注各一次。请求模型为 `deepseek-v4-flash`，服务实际返回名均为 `deepseek-flash`。三个核对状态均为 `audit_passed`，标注均为 `complete`，但这些状态不代表方法验收通过。

- 001 补上文件整体的模型观察；逐记录 summary 原值和 recipient 配对却退化成不透明派生与符号边界。处理条数的反馈修改存在解释歧义，来源核对也有跨轮不一致。
- 010 补上请求整体观察和工具返回新来源；可选参数省略关系比旧图退步，存在标记进入获取输入，核对器假定了未定义的可选参数机制。
- 013 的 CFG 已保留 environment，但标注无依据地把它解释为显式按键获取，只读 environment.FAST_KEY，环境整体及其模型观察仍缺失。请求整体观察及工具返回来源有所改善，重试、回退参数、返回身份和状态追加保持。

001 还暴露了报告展示错误：合法 literal 的 `identifier:null` 被误当字符串拼接。修复只按操作数类型选择真实 JSON 字面值；原未提交目录保留，三例使用同一批接受响应在 `offline-recovery` 新目录零网络重算、保存及重放。旧新 DOE 业务事实逐字段相等，模型的上述错误没有被人工改写。

审查入口：[完整交付总览](../packages/skill-ir/experiments/propagation/runs/source-boundaries-v1-20260928-112118/offline-recovery/index.html)、[中文主报告](../packages/skill-ir/experiments/propagation/runs/source-boundaries-v1-20260928-112118/offline-recovery/report.md)。本轮工程可复核，核心方法目标尚未全部达到；不能以未决数量为零或传播完成作为源头范围完整的证据。
