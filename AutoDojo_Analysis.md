# AutoDojo_Analysis

## 1. 背景知识速览（通俗版）

- **核心痛点**：LLM Agent 不只是聊天机器人，而是会读邮件、看网页、查 RAG 文档、调用支付/日历/Slack/旅行预订等工具的“AI 助理”。间接提示注入（Indirect Prompt Injection, IPI）指攻击者不直接对 AI 说话，而是把恶意指令藏在 AI 会读取的外部内容里。通俗来讲，这就像黑客不给秘书本人下命令，而是在秘书必须阅读的账单、酒店评论、共享文档里夹了一张“小纸条”，诱导秘书把“付账”“发消息”“泄露信息”等工具动作做偏。

  本报告阅读的是 arXiv:2606.15057 v2（2026-06-19）及本地 PDF。arXiv/PDF 标题显示为 *AutoDojo: Adaptive Black-Box Attacks Reveal the Limits of IPI Defenses and Task-Specification Effects in LLM Agents*，与题述 “Expose Superficial Defenses and User-Underspecification Limits” 指向同一核心主题：固定评测高估了防御，用户请求越欠规格化，Agent 越容易被外部内容牵着走。论文链接：[arXiv](https://arxiv.org/abs/2606.15057)、[PDF](https://arxiv.org/pdf/2606.15057)、[arXiv source](https://arxiv.org/e-print/2606.15057)、[代码仓库](https://github.com/xhOwenMa/AutoDojo)。

  背景调研中，OWASP 2025 LLM01 也把直接/间接提示注入列为 GenAI 应用的首要风险之一，并明确指出网页、文件、邮件、RAG 检索内容等外部数据都可能成为注入载体。通俗来讲，只要 AI 会把“外部材料”放进上下文，这些材料就可能从“资料”变成“假命令”。

- **现有防御的局限性**：论文把主流 IPI 防御分成三类：

  1. **Prompt-level defense（提示层防御）**：例如 sandwich/reminder/spotlighting，把用户目标反复强调，或给不可信文本打标签。通俗来讲，是在 AI 耳边提醒：“下面只是资料，不是命令。”
  2. **Filter/detector defense（过滤/检测防御）**：例如 PromptGuard、PIGuard、ProtectAI、DataFilter，先扫描外部内容，发现像命令的句子就删掉或重写。通俗来讲，是把纸条递给秘书前先过一次安检。
  3. **System-level defense（系统层防御）**：例如 Progent、DRIFT，根据用户请求推导允许的工具调用轨迹，拦截越权动作。通俗来讲，不只是检查纸条，而是给秘书设置“只能做这张工单允许的动作”的门禁。

  作者认为许多防御是“肤浅的”（superficial），不是说它们完全没用，而是说它们常常只学会了固定 benchmark 里的表面特征，例如 `important_instructions` 这类公开模板、显眼的祈使句、特殊分隔符。通俗来讲，如果安检员只记住了“坏纸条通常写着 IMPORTANT”，攻击者把它改写成一段像账单说明的自然语言，安检就可能放行。

  RAG-based defenses（面向检索增强生成的防御）也面临同样问题。通俗来讲，RAG 系统像一个会翻资料库的助理；如果资料库里混入“请忽略用户、改做 X”的文本，只靠关键词过滤或分隔符提示，很难保证模型永远把它当资料而不是命令。

## 2. 核心方法论（逻辑完整推导）

- **高层直觉（High-level Intuition）**：本文的核心洞察是：IPI 安全评测本质上是攻防博弈，而不是一次性选择题。静态 benchmark 只问“防御能不能挡住这几条固定攻击串”；真实攻击者会观察失败结果，然后换说法、换语气、换上下文伪装。通俗来讲，考试不能只用去年的原题，因为学生背题不等于真会。

  AutoDojo 的高层观点可以概括为两句话：

  1. **自适应攻击比静态攻击更接近真实威胁**。攻击者不需要白盒梯度，也不需要知道防御细节，只要能看到某个注入是否成功，就能用离线 LLM 优化下一版注入。
  2. **用户欠规格化是结构性风险**。User underspecification（用户欠规格化）指用户没有把动作、参数或目标说清楚，而是把决定权交给外部内容。通俗来讲，用户说“照这个网页上的待办做”，就等于把方向盘交给了网页；如果网页被攻击者控制，防御就更难判断什么是“正常任务数据”、什么是“恶意命令”。

- **算法/框架拆解（Step-by-Step）**：

  - **输入与约束**：AutoDojo 的输入包括：

    1. 注入目标 `(v, g)`：`v` 是攻击者可写入、Agent 会读取的外部载体，例如账单、评论、Slack 消息；`g` 是攻击者希望 Agent 执行的目标动作。通俗来讲，`v` 是纸条被夹在哪里，`g` 是纸条想让秘书做什么。
    2. 种子注入（seed injections）：来自 AgentDojo 固定攻击、TopicAttack、RLHammer 或其他已有攻击。
    3. 目标 Agent 与防御 `D`：攻击者只把它当黑盒调用，不知道权重、梯度、具体防御规则或检测分数。
    4. 离线优化器 LLM：论文实验中使用 Gemini 3.1 Pro 作为优化器，通过 OpenRouter 调用。
    5. 查询预算：每个注入目标只运行 6 轮优化，每轮给优化器看排行榜前 5 个候选。

    Threat model（威胁模型）是黑盒、自适应、低预算。通俗来讲，攻击者不知道门锁结构，只知道自己试了一把钥匙后门有没有开。

  - **核心机制**：AutoDojo 的自适应来自一个闭环：

    ```text
    种子注入
      -> 放入外部载体 v
      -> 运行被防御保护的 Agent
      -> 只观察成功/失败或 ASR
      -> 更新候选排行榜
      -> 优化器 LLM 诊断失败原因
      -> 生成下一条候选注入
      -> 重复 K 轮
      -> 返回排行榜中 ASR 最高的注入
    ```

    这个闭环有三步：

    1. **Outcome feedback（结果反馈）**：系统把候选注入放进载体 `v`，让 Agent 在一组用户任务 `C` 上运行，然后记录攻击成功率 ASR。
    2. **Diagnosis（诊断）**：优化器 LLM 读取候选排行榜，推测为什么某些注入有效、某些无效，以及目标系统可能偏向哪类防御。
    3. **Generation（生成）**：优化器基于诊断写出一条新注入。它可以改写领先候选、组合两个候选、换成自然段、对话记录、或更像工具输出的记录格式。论文附录描述了 analyzer prompt 和 rewriter prompt：前者负责分析策略，后者负责落地为一个具体候选。

  - **关键创新点**：AutoDojo 与传统随机攻击或手工模板的本质差异在于，它不是盲目扰动字符串，而是把 ASR 当作“适应度信号”，让 LLM 做语义层面的搜索。

    Adversarial objective（对抗目标）是“最大化攻击成功率”。通俗来讲，不是追求句子看起来多凶，而是追求它在真实 Agent 上多大概率让工具动作跑偏。

    与随机攻击相比，AutoDojo 的每一轮都有诊断依据；与 GCG 这类梯度攻击相比，它不需要白盒模型权重或 token 梯度；与人工模板相比，它可以针对当前防御持续改写。作者把它类比为 LLM 驱动的 evolutionary search（进化式搜索）：排行榜像种群，改写像变异，组合像交叉，ASR 像适应度。通俗来讲，AutoDojo 不是一次写一张纸条赌运气，而是像做 A/B 测试一样，保留表现好的版本，再有方向地改。

- **数学/伪代码精髓**：

  论文的核心目标函数是：

  ```text
  ASR_C(x) = (1 / |C|) * sum_{c in C} 1[g is performed in case c | x]

  x* = argmax_x ASR_C(x)
  ```

  自然语言解释如下：

  - `x` 是候选注入文本。
  - `C` 是会读取同一注入载体的一组用户任务。
  - `g` 是攻击者想让 Agent 做的动作。
  - 指示函数 `1[...]` 表示某个任务里攻击是否成功，成功为 1，失败为 0。
  - `ASR_C(x)` 就是“这条注入在这一组任务里成功的比例”。

  为什么这样设计？因为单个成功/失败太偶然，可能只是某个用户任务刚好给了攻击者机会；跨多个任务平均，才能衡量一条注入是否稳定有效。通俗来讲，一把钥匙碰巧开了一扇门不算厉害，能开同类很多扇门才说明它真的危险。

  伪代码可压缩为：

  ```text
  Input: injection target (v, g), case set C, seed injections S,
         target agent A with unknown defense D, optimizer LLM O,
         budget K

  L <- []
  for each seed x in S:
      s <- Evaluate(A, D, v, g, C, x)   # returns ASR only
      L <- L plus (x, s)

  for k = 1..K:
      h <- O.diagnose(top_candidates(L), domain_info, strategy_menu)
      x_new <- O.rewrite(h, top_candidates(L), cycle_breaker)
      s_new <- Evaluate(A, D, v, g, C, x_new)
      L <- L plus (x_new, s_new)

  return argmax_(x, s) in L s
  ```

  这里最重要的是黑盒边界：`Evaluate` 只返回 ASR，不返回模型 logits、梯度、检测器分数、内部推理链或工具轨迹。通俗来讲，攻击者只能看比分牌，不能进裁判室。

## 3. 实验设置与评估思路

- **实验想定（Threat Model）**：攻击者是黑盒外部攻击者，能控制一个 Agent 会读取的外部内容，但不能篡改用户、Agent 框架、运行时、工具或防御。攻击者不知道具体部署了哪种防御，只知道公开文献中常见的防御家族及其大致表面信号。攻击者也不知道未来具体用户会提出什么请求，所以每条注入要在一组会读到同一载体的任务上评估。

  这个设定比“最强白盒攻击”弱得多，也更接近部署场景。白盒攻击（white-box attack）指知道模型权重、梯度或防御内部规则。通俗来讲，白盒像拿到了保险柜设计图；黑盒只能试密码，看门开不开。

- **基准与指标（Baselines & Metrics）**：

  对比基线主要有三类，外加本文方法 AutoDojo：

  1. **Static attack / `important_instructions`**：AgentDojo 自带的固定注入串，也是许多 IPI 防御论文默认使用的静态评测攻击。它通常写得很直接，例如强调“重要指令”、要求 Agent 在完成用户任务前先执行攻击者目标。通俗来讲，它是一张明牌小纸条，危险但也显眼。它适合检验防御能否挡住最基础攻击，但不适合证明防御能抵抗会改写话术的攻击者。

  2. **TopicAttack**：TopicAttack 把恶意目标包进自然的上下文或对话历史中，让话题从正常业务内容逐步过渡到攻击目标。通俗来讲，它不是突然喊“照我说的做”，而是先聊账单、流程、收款方变更，再把 Agent 带到攻击动作上。它的优势是语义更柔和、更像普通内容；弱点是如果不针对当前防御继续调整，单条生成结果未必适配每个模型和防御。

  3. **RLHammer**：RLHammer 是一种强化学习攻击器。它训练一个 attacker model，根据目标模型返回的成功/失败奖励，逐步学会生成更容易触发 prompt injection 的文本。通俗来讲，它像一个反复练习绕过门禁的人：每轮试一批说法，成功的说法得到奖励，模型参数随之更新。本文把 RLHammer 作为 AutoDojo 的种子来源之一，并在 GPT-4o-mini 上单独报告 RLHammer 结果，用来判断 AutoDojo 的收益是否只是来自更强初始种子。

  4. **AutoDojo（本文方法）**：AutoDojo 不是预训练一个固定攻击器，而是在目标 Agent/防御面前进行低预算黑盒闭环优化。它从 Static、TopicAttack、RLHammer 等种子出发，观察 ASR，诊断失败原因，再让优化器 LLM 改写下一条候选。通俗来讲，RLHammer 是“先训练出一个会写坏纸条的模型”，AutoDojo 是“面对当前门禁现场试、现场复盘、现场改写”。

  GCG（Greedy Coordinate Gradient）这类梯度攻击在相关工作中讨论，但不是本文主实验基线，因为它通常需要白盒权重或梯度。Random attack 也不是核心基线；论文的重点是比较“固定公开字符串”“已有自适应种子”和“AutoDojo 黑盒闭环优化”。

  指标包括：

  1. **ASR（Attack Success Rate，攻击成功率）**：攻击目标 `g` 被 Agent 执行的比例。
  2. **Clean utility（干净效用）**：没有攻击时，Agent 完成正常用户任务的比例。
  3. **Utility under attack（攻击下效用）**：存在注入时，Agent 仍完成用户原任务的比例，论文在表格括号中报告。
  4. **防御绕过后的恢复量/恢复率（解读性指标）**：论文没有单独命名一个正式 BWR 指标，但用“AutoDojo recovers ASR”表达防御被自适应攻击绕过后，攻击成功被拉回了多少。可以看两种量：`ΔASR = ASR_AutoDojo - ASR_static`，或相对于无防御 ASR 的恢复比例。

  代表性结果：

  - 在 GPT-4o-mini 上，PIGuard 把静态 ASR 压到 0.0%，但 AutoDojo 拉回到 28.0%；在 action-open 任务桶中，PIGuard 从 0.0% 被拉到 64.3%。
  - DataFilter 在 GPT-4o-mini 上从静态 12.6% 提升到 AutoDojo 33.4%，`ΔASR = +20.8`。
  - ProtectAI 在 GPT-4o-mini 上从 7.2% 提升到 15.4%。
  - 系统层防御更稳：Progent 在 GPT-4o-mini 上静态 8.2%、AutoDojo 7.7%；DRIFT 静态 2.6%、AutoDojo 6.4%，但二者也牺牲了部分 clean utility。

- **防御方法详细拆解（Defenses）**：

  论文评估 9 个防御，覆盖提示层、过滤/检测层、系统层三类。

  1. **Sandwich（提示层）**：Sandwich 把用户原始请求夹在不可信内容前后，反复强调“真正要完成的是用户任务”。通俗来讲，就是读外部文件前后都提醒 Agent：别忘了老板原话。它的弱点是提醒不是硬约束；当外部内容写得像任务参数或业务记录时，Agent 仍可能把它纳入执行计划。

  2. **Reminder（提示层）**：Reminder 在 prompt 中加入安全提醒，要求模型不要遵循外部数据里的指令。通俗来讲，它像贴在工作台上的警示语。它能拦住一部分显式命令，但对自然伪装、长上下文干扰和 action-open 任务帮助有限。

  3. **Spotlighting（提示层）**：Spotlighting 给不可信数据打来源标记，例如 delimiter、datamarking 或编码，让模型知道哪些内容只是数据。通俗来讲，它给每段外部文本贴“第三方资料”的标签。它比单纯提醒更结构化，但仍依赖模型正确理解标签并持续遵守。

  4. **PromptGuard（过滤/检测层）**：PromptGuard 是 Meta 的 DeBERTa 类提示注入检测器。AutoDojo 论文按句子级别使用它：每个句子单独检测，被判为注入就移除。通俗来讲，它是轻量安检机，擅长抓显眼的命令式注入；问题是容易被语义伪装绕过。

  5. **PIGuard（过滤/检测层）**：PIGuard 也是检测型防御，目标之一是缓解 over-defense，也就是减少把正常内容误删的情况。通俗来讲，它想做到“抓坏纸条，但别撕掉正常账单”。论文中它对静态攻击非常强，多个模型上静态 ASR 为 0.0%；但 AutoDojo 在 GPT-4o-mini 上把整体 ASR 拉到 28.0%，在 action-open 桶里达到 64.3%，说明它仍可能依赖表面特征。

  6. **ProtectAI（过滤/检测层）**：ProtectAI 使用 fine-tuned DeBERTa-v3-base 检测 prompt injection，论文同样按句子过滤。它能显著压低显式注入，但可能误删完成任务所需的正常文本，导致 clean utility 下降。通俗来讲，安检更严，但有时把正常材料也扣下。

  7. **DataFilter（过滤/检测层）**：DataFilter 是 fine-tuned LLM 防御。它不是逐句二分类，而是读完整不可信内容，尝试删除恶意指令并保留正常数据。通俗来讲，它像一个安全编辑，试图把材料“清洗”后再交给 Agent。AutoDojo 仍能明显提升绕过：GPT-4o-mini 上静态 ASR 为 12.6%，AutoDojo 为 33.4%。

  8. **Progent（系统层）**：Progent 根据用户请求动态生成权限策略，并在运行时检查工具调用是否符合策略。通俗来讲，它不是只看纸条内容，而是检查秘书准备做的动作是否在工单授权内。它对 action-open 与 specified 任务的差距更小，但可能因为策略约束过严而影响正常任务完成。

  9. **DRIFT（系统层）**：DRIFT 从用户请求推导允许的工具调用轨迹，并阻断偏离轨迹的行为。通俗来讲，它先画出正常任务路线图，Agent 想走岔路时拦住。论文中系统层防御整体更稳，但并非免费：例如 DRIFT 在一些模型上会牺牲明显 clean utility。

- **RLHammer 具体实现，以及它和 AutoDojo 的强区别**：

  RLHammer 原论文是 [*RL Is a Hammer and LLMs Are Nails: A Simple Reinforcement Learning Recipe for Strong Prompt Injection*](https://arxiv.org/abs/2510.04885)（arXiv:2510.04885），官方代码仓库是 [`facebookresearch/rl-injector`](https://github.com/facebookresearch/rl-injector)。它的实现核心不是“让一个 LLM 临场改写”，而是**用强化学习微调一个攻击者模型**。

  具体流程可以抽象成：

  ```text
  输入攻击目标 x
    -> attacker model 生成 G 条候选注入 y_1...y_G
    -> 把每条候选注入目标模型/Agent 的工具输出或外部内容
    -> 自动判断目标动作是否被执行
    -> 成功给 reward=1，失败给 reward=0 或软奖励
    -> 用 GRPO 更新 attacker model
    -> 多轮训练后得到一个可复用攻击模型
  ```

  GRPO（Group Relative Policy Optimization）是 RLHammer 的核心训练算法。通俗来讲，它不为每条输出单独训练一个价值模型，而是让同一攻击目标下的一组候选互相比：谁更成功，谁的相对优势更高，模型就更倾向生成类似说法。

  RLHammer 的几个关键工程技巧是：

  1. **去掉 GRPO 中的 KL 正则**：标准 GRPO 会惩罚策略偏离初始模型太远；RLHammer 认为攻击任务不需要保持通用聊天能力，所以移除 KL 项，让攻击器更大胆地专门化。通俗来讲，不再要求攻击模型“像原来的自己”，而是允许它为了成功变得更激进。

  2. **同时训练 easy target 和 robust target**：只在强防御模型上训练会遇到奖励极稀疏，几乎全失败；只在弱模型上热身又容易过拟合。RLHammer 让攻击器同时攻击一个容易模型和一个强防御模型，并用软奖励表示“攻破了几个目标”。通俗来讲，先在简单门锁上学开锁手感，同时不断试更硬的门。

  3. **限制输出格式**：攻击器输出必须包在特殊标记中，否则容易生成过长、重复甚至失控的文本。通俗来讲，给攻击器规定答题框，避免它为了探索而写成一团。

  4. **LoRA + TRL GRPO 训练**：原论文使用 Llama-3.1-8B-Instruct 作为 attacker base model，用 LoRA 微调，并采用 Hugging Face TRL 的 GRPOTrainer。论文实验设置中，每个 injection goal 做 8 个 rollout，batch size 为 8，学习率为 1e-5，训练 40 epochs，主要在 InjecAgent 上训练和评估。

  5. **奖励来自目标执行结果**：在工具调用场景下，RLHammer 会把候选注入嵌入工具输出，再检查目标模型是否调用了攻击者希望的工具/参数。通俗来讲，奖励不是看文本像不像攻击，而是看最后动作有没有真的跑偏。

  在 AutoDojo 这篇论文里，RLHammer 的角色更克制：作者使用一个在 Llama-3.1-8B-Instruct 上训练的 LoRA 攻击器，并让它针对 Meta-SecAlign-8B 训练，而不是为每个被测 Agent、防御和模型重新训练最强 RLHammer。也就是说，AutoDojo 使用的是成本受控的 RLHammer 种子，不是 RLHammer 在每个目标上的上限版本。

  两者的强区别如下：

  | 维度 | RLHammer | AutoDojo |
  | --- | --- | --- |
  | 优化对象 | 训练 attacker model 的参数 | 优化某个注入目标下的候选文本 |
  | 优化方式 | 强化学习，GRPO + reward | LLM-in-the-loop 黑盒搜索 |
  | 是否需要训练 | 需要 LoRA/RL 训练 | 不需要模型训练 |
  | 反馈粒度 | 训练阶段反复调用目标并更新参数 | 每轮只用 ASR 排行榜指导改写 |
  | 适配方式 | 训练好后生成攻击，迁移到目标 | 面向当前 Agent/防御现场适配 |
  | 成本结构 | 训练成本高，推理时便宜 | 无训练成本，但每个目标要多轮查询 |
  | 泛化目标 | 学一个可复用攻击策略 | 找当前 `(v, g, D)` 下最有效注入 |
  | 在本文中的角色 | 种子攻击/对比基线 | 主方法 |

  最关键的区别是：**RLHammer 的“强”来自参数学习，AutoDojo 的“强”来自目标现场自适应**。通俗来讲，RLHammer 像训练出一名开锁员；AutoDojo 像带着几把已有钥匙到现场试锁、看反馈、当场打磨钥匙。二者不互斥：RLHammer 可以产出更好的种子，AutoDojo 可以继续把这些种子适配到具体防御上。

- **数据集构建**：AutoDojo 基于 AgentDojo，选择三个任务套件：

  | Suite | 用户任务数 | 注入任务数 | 攻击案例数 |
  | --- | ---: | ---: | ---: |
  | Banking | 16 | 9 | 144 |
  | Slack | 21 | 5 | 105 |
  | Travel | 20 | 7 | 140 |
  | Total | 57 | 21 | 389 |

  目标模型覆盖五个 LLM：GPT-4o-mini、GPT-5.4-mini、Gemini-2.5-Flash、DeepSeek-v4-Flash、Claude-Haiku-4.5。每个 suite 使用 AgentDojo 的 tool-calling agent。

  作者还引入了任务规格化难度划分：

  1. **Fully-specified（完全指定）**：用户给出动作和所有参数，例如“把地址改成某个明确地址”。
  2. **Param-open（参数开放）**：用户指定动作，但参数要从外部内容里读，例如“支付这个账单”，金额和收款方在账单文件中。
  3. **Action-open（动作开放）**：用户连动作也交给外部内容，例如“完成这个 TODO 列表上的任务”。

  三类分布为：action-open 6 个用户任务（42 个攻击案例）、param-open 26 个用户任务（180 个案例）、fully-specified 25 个用户任务（167 个案例）。Travel 没有 action-open 任务，Banking 的 param/action-open 比例更高，这也是 Banking 更容易被攻破的原因之一。

- **关键消融实验**：

  1. **去掉闭环优化，只看种子攻击**：表 3 在 GPT-4o-mini 上比较 Static、TopicAttack、RLHammer 与 AutoDojo。对过滤型防御，AutoDojo 明显高于种子：
     - PIGuard：Static 0.0%，TopicAttack 3.6%，RLHammer 11.3%，AutoDojo 28.0%。
     - DataFilter：Static 12.6%，TopicAttack 4.9%，RLHammer 2.1%，AutoDojo 33.4%。
     - ProtectAI：Static 7.2%，TopicAttack 6.2%，RLHammer 9.3%，AutoDojo 15.4%。

     这说明收益主要来自自适应优化循环，而不是简单继承更强种子。通俗来讲，不只是起跑线好，而是跑的过程中真的会调整路线。

  2. **按用户欠规格化切分**：表 5 显示，prompt-level 和 filter-based 防御在 action-open 任务上更脆。典型例子是 GPT-4o-mini + PIGuard：静态攻击在 action-open/specified 两桶都是 0.0%，但 AutoDojo 分别达到 64.3% 和 23.6%。这证明“用户把动作选择权交给外部内容”本身就是安全漏洞放大器。

  3. **按 suite 切分**：附录表 6-8 显示 AutoDojo 的恢复并不均匀。例如 GPT-4o-mini + PIGuard 在 Banking 上从 0.0% 到 56.3%，Slack 到 15.2%，Travel 到 8.6%。这提醒我们：任务域和工具链会强烈影响攻击成功率，不能只看总平均。

  4. **缺失的细粒度消融**：论文没有系统报告“去掉 diagnosis”“去掉 cycle-breaker”“只用 rewriter 不用 analyzer”等模块级消融。这不影响主结论，但限制了我们判断各 prompt 组件贡献大小。

## 4. 局限性与你的启发（可选）

- **局限性**：

  1. **评测仍依赖 AgentDojo 的任务分布**：AgentDojo 很有代表性，但仍是 benchmark 环境。真实企业 Agent 的工具权限、审批流程、日志可见性、用户行为和 RAG 语料污染方式可能更复杂。
  2. **攻击目标相对固定**：论文固定 `(v, g)`，主要优化注入文本。如果真实攻击者还能选择载体、选择触发时机、调整 payload 目标，攻击面会更大。
  3. **只使用很弱的反馈信号**：AutoDojo 只看 ASR，这让结论保守；但真实攻击者可能观察到更多外部副作用，例如消息是否发出、账单是否变更、工具错误信息等。
  4. **模块级解释不足**：如上所述，缺少 analyzer/rewriter/strategy menu/cycle-breaker 的单独消融。
  5. **模型污染与基准记忆风险**：论文自己也指出，新模型可能见过 AgentDojo 的固定注入模式，因此低静态 ASR 可能只是“见过原题”，不是防御真的稳。

- **后续算法改进思路**：

  1. **面向评测的策略调度器**：把 AutoDojo 的策略选择从纯 LLM 诊断升级为多臂老虎机或贝叶斯优化。通俗来讲，让系统记录“自然段伪装、字段伪装、对话伪装”等策略在哪类防御上更有效，在低预算下更聪明地分配尝试次数。这可用于红队评测，而不是生成可直接滥用的 payload 库。
  2. **欠规格化感知的防御评估**：在评测前自动标注用户请求的 action-open/param-open/fully-specified 程度，并要求防御报告分桶 ASR 与 clean utility。通俗来讲，别只问“总体安全吗”，要问“当用户说得很含糊时还安全吗”。
  3. **防御侧的任务意图约束**：系统层防御的相对稳健性说明，未来不应只做文本过滤，还应把用户意图转成可执行的权限边界。通俗来讲，不要只检查纸条像不像坏话，更要检查秘书准备做的事是不是这张工单允许的事。
