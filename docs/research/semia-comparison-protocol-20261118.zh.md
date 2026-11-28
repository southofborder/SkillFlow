# Semia 同模型、同源对照协议（2026-11-18）

用户已选择优先做“同模型、同一批 Skill 的公平对照”。本轮从隔离环境、固定源码、逐文件输入快照和一个工程首例开始。本文是预先约定的比较边界，不是效果评测结果，也不授权重跑已封存的 SkillFlow 实验。

## 1. 研究问题与可比较范围

要检验的是：在相同源包、模型和明确观察假设下，SkillFlow 的结构化分析是否比 Semia 更准确地保留来源、处理、条件、接收者和目的依据；增加的精度是否足以抵偿成本及失败率。

应分开报告两类问题：

| 问题 | 共同评价单位 | 解释边界 |
| --- | --- | --- |
| 可被源文支持的敏感来源→观察/交付边界 | 来源范围、目标/接收者、条件和定位组成的一个事实 | 比较共同支持的保密数据流性质，不把 Semia 全部危险动作类别合成 DOE |
| 保留 Skill 声明功能后的非必要敏感暴露 | 指定任务依据、边界和可删除范围的一项主张 | 原版 Semia 没有原生字段必要性输出；缺少此输出记为“不适用”，不能直接算漏报 |

若未来给 Semia 加任务裁决器，应独立命名 `Semia + task judge`，同时给 SkillFlow/直接强模型提供同一份任务材料及等价裁决预算。不能仅把 SkillFlow 自己生成的 Task 当金标输入另一方法，或让 Semia 阅读 SkillFlow 的 CFG、审查及诊断后再宣称独立比较。

两者都只能用冻结 Skill 中的声明用途；不能另编一个有利于某方法的用户任务。作者声明也不等同于现实授权。当前项目目的边界见 [DOE 目标与设计原则](../doe/SkillFlow-DOE目标与设计原则.md)。

## 2. 固定材料及已经完成的准备

Semia 官方仓库本轮核对的 `main` 是 `379bc25fe99833eb185efe56a38fe15f0235799c`，提交日期为 2026-06-05；与本仓库 9 月核查固定的 SHA 相同。版本号不能替代 SHA。获取回执见 [main-commit.json](../../experiments/baselines/semia-20261118/main-commit.json)，固定源码见 [官方提交](https://github.com/berabuddies/Semia/tree/379bc25fe99833eb185efe56a38fe15f0235799c)。

已建立 [输入清单](../../experiments/baselines/semia-20261118/input-manifest.json) 和 [快照准备器](../../experiments/baselines/semia-20261118/prepare_inputs.py)。四包共 21 文件，在看到 Semia 输出前选定，均只作为数据读取，未执行 Skill。

| case | 完整文件数 | 冻结输入来源 | `package_bytes_sha256` |
| --- | ---: | --- | --- |
| 001 | 1 | 已关闭 20261111-173347 input-necessity 小例 | `fd1b5c2dcd34e37cb7bc7288df561d9f339b199649018b445d8fdaf5ffa2ae06` |
| 010 | 3 | 同上 | `98e3b818265587ee4b04b566e9280a08b110512610c054500a7d4174929951a0` |
| 013 | 1 | 同上 | `05262444daaee62622a2b7b745611bba60f0cf5e13a733d81e4da773e58d9ea2` |
| ga4 | 16 | 已关闭 20261117-205158 runtime-locality | `14f95b6a10ab6c0c61737b4cf9202a6b17b178536e13822baf33eca186dbeb5f` |

清单另保留原 `source_sha256`、原 manifest/snapshot/implementation 身份和逐文件字节哈希。`package_bytes_sha256` 与旧系统的 `source_sha256` 采用不同定义，不能混用。每次分析前后均核对文件路径、长度和 SHA-256；发现差异记材料失败，不静默更新快照。

这四例是长期开发用例，**不是随机、保留或代表性样本**，且当前清单的标签状态为 `unannotated_not_negative`。其用途是跑通接口、检查信息覆盖、暴露方法差异和发现协议问题，不能产出对外泛化 F1。

历史 SkillFlow 小三例和 GA4 的 implementation SHA 不一致，GA4 还含继承阶段。因此历史输出仅为有旧身份的背景记录，不能拼成“同版本、同预算、独立全新”的配对实验。另一个 2026-11-18 program-owned CFG 运行不属于本协议的数据来源，不对其当前未完成状态作最终结论。

## 3. 模型与运行控制

目标配置是 `gpt-6.1-sol / high / openai`。原生 Semia Codex 入口只显式传递 model，继承本机 CLI 配置，没有单独固定 reasoning effort；直接执行 `--model` 不足以证明同配置。[固定版本 llm_providers.py](https://github.com/berabuddies/Semia/blob/379bc25fe99833eb185efe56a38fe15f0235799c/packages/semia-cli/src/semia_cli/llm_providers.py)

首例名称必须为 **Semia + controlled transport**：保留固定源码的 prompt、SDL、校验、候选选择和合成循环，仅在隔离 runner 中适配 Codex 调用以固定 effort/provider、屏蔽额外用户配置与项目指令，并采集请求、回答、回执、耗时及可见用量。此变体不是论文原封不动复现。适配器需要离线验证 prompt/response 原样透传、实际命令参数、错误处理和超时行为；不得趁适配修改 Semia 的语义提示或检测规则。

`read-only` 文件系统模式本身不证明无工具调用。运行前还须确认当前 CLI 的工具/插件隔离设置，保存精确命令与可执行文件哈希；实际事件中若出现读取额外数据或工具执行，单列偏离而不能仍称“仅源包的模型审计”。目标 Skill、其中脚本和恶意指令均不执行。

固定实现默认有 5 个合成 iteration、每 iteration 最多 3 次结构重试（即最多 4 次候选尝试）、2 次 provider 重试；另有提前停止、分数阈值和平台期机制。**5 iterations 不等于 5 个模型调用**。应记录实际生效值，并把校验重试、语义改进、传输重试和 provider 内部未知重试分别计数。[固定版本 llm_config.py](https://github.com/berabuddies/Semia/blob/379bc25fe99833eb185efe56a38fe15f0235799c/packages/semia-cli/src/semia_cli/llm_config.py)、[synthesis_loop.py](https://github.com/berabuddies/Semia/blob/379bc25fe99833eb185efe56a38fe15f0235799c/packages/semia-cli/src/semia_cli/synthesis_loop.py)

本轮首例保留 Semia 算法自己的合成预算：5 iterations、3次结构重试、2次 provider 重试，并将单次 native timeout 设为2700秒，偏离 Semia 默认600秒。不能因此声称与 SkillFlow 七阶段及纠错/修复机制“同预算”。后续正式对照至少区分：方法原生预算下的成本—效果曲线，以及预先固定 token/时间总上限的受限预算对照。达到上限就保留 partial/timeout，不能只为落后方法补跑直到成功。

## 4. 分阶段产物与停止条件

| 阶段 | 产物 | 可以得出的结论 |
| --- | --- | --- |
| A：获取与离线验证 | 固定源码、隔离依赖、官方 deterministic tests、四包 prepare 结果及文件纳入/排除清单 | 环境是否可运行、输入是否被完整接收；不能证明语义正确 |
| B：001 工程首例 | 一次新 Semia 合成/检测的完整请求、所有候选、反馈、选中事实、报告、耗时/用量 | 首例端到端状态、信息保持问题、可见成本；没有金标性能数字 |
| C：四包工程对照 | 在前两步问题明确后按既定顺序运行；保留所有失败 | 工程覆盖及错误类型；不是四例统计排行榜 |
| D：正式配对评测 | 同一当前 SkillFlow 快照与 Semia 快照；源包/标签/预算锁定；独立案例和盲标 | 在指定分布与假设下的配对效果及成本 |

本轮执行状态由 [复刻目录](../../experiments/baselines/semia-20261118/) 中的机器回执决定；本文不把 B/C/D 的计划写成已完成。不能恢复任何旧 run、追加旧回放、改写旧结果，或把旧授权视为新批次的执行凭证。

2026-11-18 首例状态补记：root 已启动仅001的真实合成/检测试跑，使用隔离 [run_controlled_pilot.py](../../experiments/baselines/semia-20261118/run_controlled_pilot.py)，禁用 shell、unified_exec、apps、browser、plugins、hooks 等能力。最终成功/失败及用量以该次回执为准，不从“进程已启动”推定已通过。010、013、GA4没有随之自动启动。

发现真实源文件遗漏、可执行依赖缺失、隔离失败或没有可用事实时应保留完整失败并停止依赖步骤。不得用合成测试 facts 冒充真实模型产物，也不得把 `prepare-only` 或内置正则 baseline 的成功写成 CGRS 成功。

## 5. 输入、后端与威胁假设的等价核验

双方以同一目录的完整包作为输入；分别保存各自最终送模文本及其 hash。记录所有遗漏文件、排除原因、大小限制和实际行号映射。当前 Semia 预处理支持代码和文本，但单文件/总量门限、后续文档门限仍需以实际清单核验；“提供了16文件”不等于“模型看到了16文件”。[固定版本 prepare.py](https://github.com/berabuddies/Semia/blob/379bc25fe99833eb185efe56a38fe15f0235799c/packages/semia-core/src/semia_core/prepare.py)

本轮实际 prepare 已发现：001纳入1/1、010纳入3/3、013纳入1/1；**GA4只纳入14/16**，上游默认排除了 `package.json` 和 `package-lock.json`。这构成“相同完整包、不同可见输入”的已知偏离。GA4真实合成暂不启动，需先明确是报告“原版默认输入策略”，还是另建并命名“完整源输入适配变体”；两者产物必须分开，不能静默加文件后仍标原版，也不能删掉 SkillFlow 相同文件来美化完整性。

使用 `builtin` 或 `souffle` 必须在回执显式固定。若本机只能运行官方 builtin，应按该后端命名；未验证一致性时不能将其等同于论文 Soufflé 结果。上游已有离线回归通过只支持这些被测输入，不能推导所有 SDL 程序等价。

比较前逐项固定：脚本内部处理能否被模型观察、工具返回什么、不同 action 是否共享上下文、注入对手能力、动态调用/外部 API 是否展开、条件分支是否可同时发生。Semia 论文采用跨 action 上下文可达假设；SkillFlow 的局部运行时边界不同，不能把假设差异造成的边数减少直接解释为误报修复。必要时分“共同假设子集”与“各自原生假设”两表报告。

## 6. 标签、结果和失败的计量规则

正式 gold 必须由至少两名独立审查者先看原始 Skill 与书面运行假设、盲于工具结论，记录分歧并仲裁。每条标注含来源、接收者、内容/字段、条件、任务依据和源文位置；无法确定的条目保持 unknown。工具输出、另一 LLM、旧审查通过或扫描器一致性均不能直接当 gold。

| 记录 | 必须如何计入 |
| --- | --- |
| `completed` 且有可评分事实 | 进入共同性质的条件精确率/召回率，并同时报告覆盖分母 |
| `partial` / `unknown` / `unresolved` | 单列数量、范围和来源；既不是安全，也不是自动阳性；不能删去后只展示 F1 |
| `unsupported` / 性质不适用 | 留在适用性矩阵，不冒充漏报或真阴性 |
| 源包缺失、解析/校验失败、超时、传输失败 | 保留类别，计入端到端可用率分母；不伪装成检测阴性 |
| 缺用量回执 | known tokens 与 unknown 分开，不能当 0；同样保留失败请求成本 |

至少报告：所选 Skill 数/文件数、完整与部分完成率、源文覆盖、可评分事实比例、共同性质 precision/recall、未知比例、证据定位正确率、源→处理→边界绑定正确率、实际模型开始数、全部可见 input/output/cached tokens、端到端及模型/确定性阶段耗时。无独立金标时精度/召回置 `not_evaluated`。

后续真有 DOE 对照时，还须检验每项建议是否保留必要动作、条件和输出，分别统计可确认的多余载荷、功能破坏、未决和建议不可执行；不能以 `no_excess_established` 或零 deletable 推出没有过度暴露。总体结论按 Skill/来源聚类，而非把一个 Skill 的多个 sink 或重复尝试当独立样本。

## 7. 与论文原实验的关系及仍缺材料

论文页面本轮仍为 2026-05-01 v1。原实验用 Claude Opus 4.6、temperature 0、5轮细化；541人工标注样本来自10,853个已获 VT 结果的子集（原始池13,728），包含301风险、240 clean。两位作者独立标注并仲裁；报告的是11类风险的 Skill 级分类，而非任务必要性或字段级 DOE。纸面指标是作者报告，不能作为本次复刻结果。[论文 §§6–7](https://arxiv.org/html/2605.00314v1#S6)、[版本页](https://arxiv.org/abs/2605.00314)

公开源码内找到的 fixture 说明是50个 Skill、259文件的工程 smoke 语料，明确不提供 policy gold。本轮没有在所读官方论文/仓库中定位到完整541例的冻结包、标签、抽样列表与匹配扫描器快照；这表示尚未获得，不断言作者没有发布。不能将 fixture 当论文 benchmark。[官方 fixture 说明](https://github.com/berabuddies/Semia/blob/379bc25fe99833eb185efe56a38fe15f0235799c/tests/fixtures/README.md)

同模型主线无需先复现论文数字。仍需补齐的是：当前 SkillFlow 的可封存比较版本、后续真正共同预算、独立保留样本及盲标、明确共同威胁假设、所用检测后端的核验范围。论文全量复现另外需要原始数据/标签/抽样种子、评估脚本和论文实现版本对应关系；不会以此阻塞当前隔离工程首例，也不会把缺失材料补猜成已知事实。
