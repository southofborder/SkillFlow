# SkillFlow 相关研究与会议进展：2026-11-24

接续 [11 月 18 日记录](related-work-update-20261118.zh.md)，截至 **2026 年 11 月 24 日（Asia/Shanghai）**，本轮定向核查安全、软件工程／程序语言、AI／NLP 会议及最新预印本。**确有新增的高度相似研究：SkillPrivus 最直接触及正常 Skill 的超任务隐私使用，SkillCFI 紧邻 Skill 到执行契约的编译。** 旧稿 ToolMinimize 也必须补入字段必要性对照。

下面严格区分首次提交、版本更新、旧稿补漏和会议身份确认。“本轮确认录用”不表示会议本周才宣布。arXiv 日期默认 UTC；完整来源与证据等级见 [来源记录](related-work-update-20261124.sources.json)。所有外部效果数字均为作者报告，本轮没有复现这些结果。

## 上次检索之后的新稿与版本更新

上次版本记录抓取于 11 月 18 日约 08:11 UTC。SkillCFI 虽与上次报告同日，首次提交晚于该时间，因此列为边界新增。

| 工作 | 首发／更新及身份 | 核心问题与对 SkillFlow 的关系 |
| --- | --- | --- |
| **[SkillPrivus: Uncovering PRIVacy of USe Harms in Agentic Skills](https://arxiv.org/abs/2611.26747)** | **11-19 19:43 UTC v1**，北京时间 11-20；预印本，未确认会议 | 安装前静态审计正常功能中的过度使用、敏感推断、保留与意外接收方。抽取有源文依据的 data moves，以情境完整性属性和模型判断审查用途适当性。**最直接的新增定位竞争者**：不能再以“正常 Skill 也会超任务使用数据”或“有源文依据的隐私审查”作为独有贡献。 |
| **[SkillCFI / Guarding the Kingdom of Skill-Based Agents in the AI Dynasty of Computation](https://arxiv.org/abs/2611.24185)** | **11-18 10:26 UTC v1**；作者列为预印本 | 将 Skill 同时编译成 Agent 指令与可执行契约，确定性运行时守卫检查步骤、工具调用和结果证据。对无可观察证据的强制义务采取拒绝策略。**源文到契约、控制顺序、结果绑定都很接近**；其执行环境约束与我们的静态诊断需要分别评价。 |
| **[SkillPlumber / Evolve Where It Matters: Coverage-Guided Self-Evolution of Agent Skills](https://arxiv.org/abs/2611.25429)** | **11-19 03:11 UTC v1**；预印本 | 按指令记录已遵循、未遵循、未覆盖，以持续根因分析推动 Skill 修订。适合比较失败定位与修订依据，尚不能直接充当隐私必要性判定基线。 |
| **[Carried-Over and Agent-Native Threats in the Supply Chain of LLM Agent Skills](https://arxiv.org/abs/2611.30932)** | **11-23 16:20 UTC v1**，北京时间 **11-24**；预印本 | 从依赖、源码、安装说明和凭据输出追踪供应链风险，结合静态筛查、人工核查与抽样运行。重点是区分漏洞存在、输入可达与真实 Agent 利用；支持我们把边界覆盖和实际风险分开报告。 |
| **[SNOOP / Actions Speak Louder than Words](https://arxiv.org/abs/2611.27046)** | **11-20 03:17 UTC v1**；预印本 | 通过页面／链接选择及访问顺序推断 Agent 私密上下文，研究有状态行为隐蔽信道。提示仅检查出站敏感字段并不足以覆盖控制行为泄露；不能据此声称 SkillFlow 已覆盖隐式流。 |
| [Privacy Protection in Self-Evolving Personal Agents: Persistent Memory and Cross-Carrier Transfer](https://arxiv.org/abs/2611.26983) | **11-20 02:03 UTC v1**；预印本综述 | 讨论记忆准入、维护、释放与跨载体转移。作为持久化／生命周期边界补充；本轮仅核实摘要，不列直接算法对照。 |
| **[EvoSkill Injection](https://arxiv.org/abs/2608.30429)** | **11-19 v2**；首版 08-31，属于旧稿更新 | 已由 [ACL Anthology](https://aclanthology.org/2026.emnlp-main.353/)确认 **EMNLP 2026 主会**，研究 Skill 生成、演化与持久污染。不是本周首次发表，也不是 Findings。 |

对前两篇，需要保留以下评测边界：

- **SkillPrivus**：726 个收集样本中，118 个被筛除、45 个未完成，563 个完成隐私相关审计；其中 307 个被标记潜在危害，不能写成“54.5% 已证实发生泄露”。其人工分析的 83.2% 是标注者两两一致率，κ 约 0.346，不能称为检测准确率。作者明确把独立的抽取忠实度审计列为后续工作。[正文](https://arxiv.org/html/2611.26747v1)
- **SkillCFI**：作者的 53 个公开 Skill 没有一个原样接纳，7 个经适配后接纳；评测另含 8 个自建 Skill。论文承诺录用后发布代码，本轮不能将其列为已可直接复刻的完整实现。[正文](https://arxiv.org/html/2611.24185v1)、[作者页面](https://profile.wohin.me/publications.html)

## 各会议目前可核实的相关研究

这些大多是旧稿的会议确认或本轮补漏，**不计入本周新稿数量**。表中没有写明轨道的，不推定为研究主会长文。

| 会议／轨道 | 相关工作及官方证据 | 与本项目的关系 |
| --- | --- | --- |
| **CCS 2026** | [官方接收列表](https://www.sigsac.org/ccs/CCS2026/program/accepted-papers.html)列有 **SkillScope（Wu 等，arXiv 2605.05868）**、**SkillCODER** | 前者是任务条件下细粒度最小权限的重要对照；后者研究 SkillIR、版权审计与归因，不能当作 DOE 检测基线。 |
| **USENIX Security 2026** | [“Do Not Mention This to the User”](https://www.usenix.org/conference/usenixsecurity26/presentation/liu-yi)；[AttriGuard](https://www.usenix.org/conference/usenixsecurity26/presentation/he-yu) | 分别是野外恶意 Skill 测量，以及工具调用的因果归因防护。后者关注调用来自用户意图还是不可信观测，不等于静态字段必要性证明。 |
| **IEEE S&P 2026** | [Towards Automating Data Access Permissions in AI Agents](https://sp2026.ieee-security.org/program.html) | 根据用户及上下文推断数据访问权限；用户偏好与任务功能必要性需要分开。 |
| **NDSS 2026** | [SAGA: A Security Architecture for Governing AI Agentic Systems](https://www.ndss-symposium.org/ndss2026/accepted-papers/) | Agent 生命周期、通信授权与能力令牌的架构背景。 |
| **ASE 2026 Research Papers** | [MalSkills 官方日程](https://conf.researchr.org/program/ase-2026/program-ase-2026/)；[ProvenanceGuard](https://conf.researchr.org/details/ase-2026/ase-2026-research-track/239/Safeguarding-LLM-Agents-from-Misalignment-through-Provenance-Analysis)；[How Your Credentials Are Leaked by LLM Agent Skills](https://conf.researchr.org/details/ase-2026/ase-2026-research-track/43/How-Your-Credentials-Are-Leaked-by-LLM-Agent-Skills-An-Empirical-Study) | MalSkills 的正式研究轨道已确认；ProvenanceGuard 在执行前检查工具调用的上下文证据支持；凭据论文补充真实生态测量。 |
| **ASE 2026 Tools and Datasets** | [AgentOS](https://conf.researchr.org/details/ase-2026/ase-2026-tools-and-data-sets/45/Introducing-Safe-LLM-Agent-Execution-via-Typed-Tool-Mediation-and-World-Effect-Evalua) | 类型化工具中介、能力／标签检查与真实世界效果评估；**不是研究长文轨道**。 |
| **FSE 2026** | [AgentBound，Research Papers](https://conf.researchr.org/details/fse-2026/fse-2026-research-papers/14/AgentBound-Securing-Execution-Boundaries-of-AI-Agents)；[GrantBox，IVR](https://conf.researchr.org/details/fse-2026/fse-2026-ideas-visions-and-reflections/3/Evaluating-Privilege-Usage-of-Agents-on-Real-World-Tools) | 源码权限推断／执行隔离与真实工具权限使用；两者轨道不同，不能合并标为研究长文。 |
| **ISSTA 2026 Research Papers** | [ToolLeak](https://conf.researchr.org/details/issta-2026/issta-2026-research-papers/176/Red-Teaming-Coding-Agents-from-a-Tool-Invocation-Perspective-An-Empirical-Security-A)；[AgentBreaker 官方日程](https://conf.researchr.org/program/splash-issta-2026/program-splash-issta-2026/) | 工具参数生成中的上下文泄漏、Web Agent 间接提示注入；属于动态安全评测近邻。 |
| **NeurIPS 2026 Evaluations & Datasets** | **Skill-Inject**、**No More, No Less: Task Alignment in Terminal Agents（TAB）**；[官方目录](https://neurips.cc/Downloads/2026)、[作者明确的轨道记录](https://s-abdelnabi.github.io/publications/) | Skill 文件攻击，以及完成任务同时避免多余动作的评测。TAB 与 Task 必要性非常相关，但不是字段级静态最小化。 |
| **NeurIPS 2026，具体轨道未核实** | **Fides / Securing AI Agents with Information-Flow Control**，有[微软官方论文页](https://www.microsoft.com/en-us/research/publication/securing-ai-agents-with-information-flow-control/)；**Seeing Is Not Screening**，有[作者记录](https://yebof.github.io/publications/)；两者均见[官方目录](https://neurips.cc/Downloads/2026) | 分别是确定性信息流控制、跨模态 Skill 扫描攻击及防护。Fides 旧 OpenReview 的 ICML 投稿状态不能用来标注 ICML 录用。 |
| **EMNLP 2026 Main Conference** | [EvoSkill Injection](https://aclanthology.org/2026.emnlp-main.353/) | 主会身份已由正式论文集确认；本轮增量是 arXiv v2。 |

2027 年会议需要单独区分“题目公布”“作者称录用”和“正式目录核验”：

| 会议 | 截至 11-24 的证据 | 应如何解读 |
| --- | --- | --- |
| **ICSE 2027 Industry Challenge** | 官方题目 **What Skills Claim and What Skills Do: Detecting Intent-Behavior Misalignment in Agent Skill Ecosystems**；解决方案通知日为 **12-18**。[官方页](https://conf.researchr.org/track/icse-2027/icse-2027-industry-challenge) | 与我们的任务／源文行为对应高度相关，但目前确认的是**被接纳的挑战题目，不是已录用的解题论文**。 |
| **MSR 2027 Mining Challenge** | **GitSkills** 被用作官方挑战数据集；作者注明 MSR ’27 to appear。[官方页](https://conf.researchr.org/track/msr-2027/msr-2027-mining-challenge)、[论文](https://arxiv.org/abs/2608.10906) | 旧稿，适合扩展样本来源；大规模收集不是安全或必要性金标。 |
| **S&P 2027** | **Janus** 在[作者页面](https://gracebrigham.github.io/)标为 S&P 2027；[论文](https://arxiv.org/abs/2607.01510)与[代码](https://github.com/GraceBrigham/Janus)可见；本轮官方接收页面未返回可核查的单篇正文 | 记为**作者确认 forthcoming，官方单篇条目未独立复核**。用户参与的权限管理与任务必要性判定有交集，但不相同。 |
| **PoPETs 2027 Issue 2** | **GapLeak: When Privacy-Preserving LLM-based Web Agents Become a Privacy Risk** 的 [arXiv](https://arxiv.org/abs/2611.22223)注释称已录用；首版 11-17 | 旧稿补漏；**作者声明录用，官方单篇目录未独立核实**。缺失任务字段可能诱导 Agent 获取更敏感的未授权来源，是输入不足／扩权边界的重要近邻。 |
| **ICLR 2027** | [RuntimeTickets](https://arxiv.org/abs/2611.03772)注明 submitted / under review | 仍按**在审**记录，不能写为录用。 |
| **USENIX Security 2027 / NDSS 2027** | USENIX 首轮通知 **12-03**；NDSS 秋季轮通知 **12-02**。[USENIX CFP](https://www.usenix.org/conference/usenixsecurity27/call-for-papers)、[NDSS CFP](https://www.ndss-symposium.org/ndss2027/submissions/call-for-papers/) | 这些轮次截至本日尚未到通知时间；NDSS 还有更早的夏季轮，不能据此断言 2027 年完全没有已接收论文。 |
| **SAIS 2027** | USENIX 新会议 Secure Agentic-AI Systems，明确征集隐私、最小权限、能力控制、形式保证和可复现评估；投稿截止 **2027-02-04 AoE**。[官方 CFP](https://www.usenix.org/conference/sais27/call-for-papers) | 值得关注的新会议信号，当前是征稿，**不是论文接收列表**。 |

本轮对 ACL、ICML、POPL 及其余 2027 年会议作了有限检索，没有取得更多“本周首次公开的直接竞争论文”的可靠证据；这不等于这些会议没有相关工作。FSE／ISSTA 2027 仍有后续评审周期；不能把一个尚未完整公布的目录当作全年结论。

## 必须补入的旧工作与材料更正

**ToolMinimize 与“字段粒度更细”的定位直接相撞。** [ToolMinimize: Auditing and Rewriting LLM Agent Tool Calls to Minimize Privacy Exposure](https://arxiv.org/abs/2608.24957) 首版为 08-25。它在工具调用边界按 schema 与任务判断内容必要性，执行删除、泛化、替换或截断；包括必需自由文本内部的可选任务相关审查。正文首页称为 **PST 2026 接收作者版**，本轮没有独立找到官方单篇／Xplore 条目，应保留该证据等级。其“参数仍符合 schema”不等于端到端功能保持：作者 mock 测试 20 例中 16 例等价，4 个地图案例因删去必要地址且缺少 minimum_necessary 元数据失败。[正文](https://arxiv.org/html/2608.24957v1)

**SCS 的代码状态需要补正。** 11 月 18 日写的是未核实作者实现；现在已从[论文附录 B](https://arxiv.org/html/2610.33489v1)找到作者给出的[匿名制品地址](https://anonymous.4open.science/r/scs-F00A)。本轮未能读取仓库内容，因此准确表述为“已找到作者声明的代码／数据／配置入口，完整性与可运行性未核验”，不能写成没有代码，也不能说本周新开源。

**Semia 的已固定版本未发现前进。** [论文](https://arxiv.org/abs/2605.00314)仍是 05-01 v1；通过 GitHub 连接器比较固定提交 `379bc25fe99833eb185efe56a38fe15f0235799c` 与 main，结果 identical、ahead 0、behind 0。[比较入口](https://github.com/berabuddies/Semia/compare/379bc25fe99833eb185efe56a38fe15f0235799c...main) 本轮没有新增代码版本依据来改变既有复刻结论；四例证据仍见 [11 月 19 日结果](semia-cohort-results-20261119.zh.md)。

复刻材料还应避免两个误认：Fides [公开仓库](https://github.com/microsoft/fides)主要提供教程 notebook，不能直接称为完整论文评测包；ASE ProvenanceGuard 的[正确仓库是 cmu-soda/ProvenanceGuard](https://github.com/cmu-soda/ProvenanceGuard)，不要与同名 RAG／MCP 项目混淆。另有 [Skill or Threat?](https://conf.researchr.org/details/ase-2026/jaws-2-2026-papers/13/Skill-or-Threat-Risks-and-Scanner-Gaps-in-the-LLM-Skill-Ecosystem) 属于 ASE JAWs2 workshop 的短 pitch，不是 ASE 主会研究长文。

## 对 SkillFlow 定位与后续对照的判断

以下是根据上述论文作出的研究判断，不是已有实验结论：

1. **优先精读／映射 SkillPrivus、SkillCFI、ToolMinimize 和 SCS。** 四者分别覆盖用途适当性、源文编译契约、字段最小化、静态依赖图安全分析；它们压缩了只凭问题定义或框架组合宣称新颖性的空间。
2. **候选差异必须落到可验证的任务语义。** 可以研究在明确支持的操作范围内，将源文依据、接收方／数据对象绑定、分支义务和字段必要性联系起来；但“更细 IR”“有源行”“确定性传播”本身都不证明分析正确。未建模、地址未知和取值未知应各自报告。
3. **评测要同时覆盖必要使用与多余暴露。** 对每个“可删／可缩减”结论，分别核实源文支持、敏感对象／接收方、Task 要求与功能保持。ToolMinimize 的失败案例和 TAB 的多余操作任务可帮助设计评判维度，不能直接替代独立金标。
4. **先对齐范围，再比较成绩。** SkillPrivus 的潜在隐私危害、SkillCFI 的运行时契约拒绝、MalSkills 的恶意分类、Semia 的安全查询、SkillFlow 的 DOE，不是同一种标签。模型、实际输入、预算、适配量、前端失败和 unknown 都需要单列。
5. **不要把现有局部证据扩展成胜负结论。** Semia 四个工程样本的结构失败不证明总体劣势；SkillFlow 历史边界到达数也不证明语义正确或最小化有效。供应链新研究同样提醒：静态发现、可达性和实际利用应分层报告。

本轮产出是研究记录与证据索引。核查深度以版本／摘要／官方会议条目为主，对 SkillPrivus、SkillCFI、ToolMinimize 及 SCS 的相关正文作了重点阅读；未验证各篇全部附录和实验。可用代码入口不等于可复现，作者录用声明不等于已独立核对官方目录。建议下一次重点复核 ICSE 挑战解决方案及上述 12 月通知后的正式条目。

