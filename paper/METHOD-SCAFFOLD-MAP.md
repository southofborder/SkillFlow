# SkillFlow 论文 — Method 骨料映射(内部写作清单,非论文正文)

> 目的:保证 method 章**完整**——把我们真实踩过的难点/解法/创新点逐条钉到 method 小节,写作时不漏。
> 用户硬要求:method 完整,不能只挑别人没有的讲;自己的难点(困难→解法→创新)详细讲;与别人不同的部分**更**重点突出。
> 占位名:系统=SkillFlow,图=SFG(Skill Flow Graph,替旧 FCG),判定=CoDE(Coalitional Data Exposure,替旧 DOE)。
> 每条标注:【差异】=竞品没有/我们独特;【硬工程】=真实工程墙的挑战→解法;【方法】=方法学创新;【契约】=系统内部一致性设计。

---

## M1. 系统总览(three-stage)
- Download → SFG(语义图+安全档案)→ CoDE(逐单元判定)。入口 `scripts/skillflow-pipeline.js`。
- 【差异】纯静态、免执行、免沙箱、免 replay——对比 AgentRaft(运行时执行 agent 抓 taint)、SkillScope(双 run replay 消融)、凭证study(动态沙箱)。这是能上 marketplace 规模的根因。
- 素材:PROJECT-OVERVIEW §1-3。

## M2. SFG 构建(图 + 安全档案)
### M2.1 提取粒度:块分类 + 策略派发
- 【硬工程+方法】不再逐行关键词,先分文件类型→内容块类型(code/table/list/prose/disclaimer)→派发策略。
- 记忆:[[fcg-extraction-granularity-findings]](四缺陷:代码块丢弃/否定误判/脚本爆炸/非指令文档,已修)、[[fcg-list-block-and-edge-precision]](多行bullet合并/列表免责作用域/conditions→router降级)、[[node-profiler-metadata-pollution-fix]](name/gate/action_evidence JSON喂检测→伪造sink子节点,分离nodeActionText+doc-slug排除)。
### M2.2 语义门(LLM,承重)
- 【方法】规则只产候选,**LLM 判每个候选的 actionability/classification/operation_type**,写入 node.semantic_gate。真 gpt-5.5。
- 记忆:[[fcg-semantic-reason-role-pollution-fix]](边的 semantic_reason 散文误推节点 role→改 role 由 node_roles 定)。缓存内容寻址 [[skillflow-llm-resilience-work]]。
### M2.3 边连接的两股力(recall vs precision)
- 【方法】type-analyzer 穷举候选+类型相容(recall)vs router 用 condition/guard 语义(precision)。
- 记忆:[[negation-constraint-edge-closure]](否定句分免责/约束,ordering建control_flow约束边、guard标conditions;端点全局作用域匹配+词干化+LLM兜底)、[[fcg-list-block-and-edge-precision]]。
### M2.4 单跨界拆分不变量
- 【契约】连边后确定性拆分,每节点≤1跨界步,observation↔sink-node 1:1,child继承父边省 O(n²) 配对。
- 记忆:[[node-split-single-crossing-invariant]]。

## M3. 环感知(**核心差异**,竞品全剪环)
- 【差异+方法】AgentRaft "explicitly prune cyclic trajectories"、SkillScope 前向DAG——我们认真处理环。
- 记忆链:[[self-loop-cycle-representation-plan]](removeCycles静默删环丢自优化语义)→[[feedback-edge-cycle-representation]](方案A:标记is_feedback_edge不删;下游三处过滤activeEdges;零回归)→[[feedback-edge-plausibility-classifier]](不判真假环改判"回边合理性",粗规则宽进+LLM复核;15skill实测92.8%plausible/7.2%implausible)→[[cycle-expansion-in-transfer-layer]](真环带进标签传递层绕一轮;periodic/collapse)→[[cycle-label-closure-model]](出环闭包:细化型specializing成员复用外部derive多流;判据按category非mode;label_id字典化)。
- 【差异】实测 prevalence 可做(92.8/7.2)——反驳"环是corner case"。

## M4. 标签泛洪引擎(判定驱动重写,内存墙)
### M4.1 判定驱动的设计哲学
- 【方法】FCG产出**服务DOE判定**而非忠实复现全路径(数据最小化+删除-替代测试法)。
- 记忆:[[fcg-python-judgment-driven-rewrite]]、[[m3-flood-python-rewrite-progress]]、plan 文件 peaceful-spinning-willow.md。
### M4.2 内存墙 → 去路径化状态
- 【硬工程】每条流spread-copy整路径致GC撞墙;改为携带O(真变换)摘要+origin+词集,不物化路径。
- 记忆:[[flood-key-origin-node-explosion-fix]](flood dedup key用origin_node过度分区→改origin_class对齐DOE)、[[flood-transform-sig-dekey]](transform_sig移出去重键治空间爆炸)、[[reduction-antichain-key-component]](reduction_applied 1bit→反链值)。
### M4.3 存储合并 O(W²) 时间/内存墙(**未完全解**)
- 【硬工程】applyMergeEventToFlows 每writer O(W) filter × W flows;beast skill致JS heap OOM。
- 记忆:[[storage-merge-ow2-incremental-fix]](三处塌成O(1)增量:set去重+event索引+指纹集;134绿+A/B逐字节等价)、[[two-distinct-perf-walls]](无普适墙;线性体量vs存储合并O(W²)唯一超线性140x)、[[admapix-js-oom-beast-confirmed]](00011真574节点6GB仍OOM)、[[fcg51-nodepath-contract-verified]]。
- 【诚实】Python已修O(1)增量,JS未回港;beast走Python引擎。eval的scalability节要如实讲。

## M5. CoDE 判定(exposure ⊥ necessity 两轴)
### M5.1 两轴正交
- 【方法】exposure(危险度)与necessity(必要度)正交;真外泄不可豁免,DOE=外泄∧不必要;喂LLM不降暴露只由必要性定。
- 记忆:[[exposure-necessity-orthogonality]]、[[n5-structural-evidence-and-egress-tier]](真外泄统一high_sensitivity_egress;结构信号schema_declares_input/origin_trust)。
### M5.2 必要性重设计(词袋→结构判据)
- 【方法】三分量词袋→结构判据;N0探针定位action_input是裁决主宰+522词袋假地板;N1(op语义+transform参与+schema归属)N2(receiver×category相容矩阵)N3(task_need声明覆盖)。
- 记忆:[[necessity-redesign]]、[[doe-necessity-3component-optimization]](4→3取min)、[[score-not-gate-guards]](修判别靠打分/阈值不靠gate特化;necessity阈值0.7落在clr/pd簇间隙)。
### M5.3 flow-centric 证据包
- 【契约+硬工程】pack大换血为label/sink_boundary/flow结构;task_memory改吃FCG;信息保真98.7%,单包500k→1.4k。
- 记忆:[[doe-flow-centric-evidence-pack]]、[[doe-evidence-index-cleanup]]、[[v6-flowstate-slimming-and-reduction-fix]]、[[doe-sink-confidence-dedup-submission]](同签名多路径只送最高置信度代表省75%)。
### M5.4 溯源裁剪 + control_flow 链接
- 记忆:[[doe-p1-origin-trim-p2-controlflow-link]](溯源截到origin_node;control_flow分纯顺序/数据)。

## M6. 【新·大卖点】聚合泄露 CoDE(**待核实回填**)
- 【差异+方法】Sweeney QI集命中:多流汇聚同一sink,label集合命中准标识符组合→聚合泄露。判定单元单流→同sink多流label集合。"聚合∧不必要"。
- 记忆:[[aggregation-exposure-qi-pivot]]。**占位——两agent核实(代码可行性+文献查新)回来才填实。**
- 竞品盲区证据:[[same-group-deepread-gaps]](两系统逐单元裁决,单动作消融构造性漏聚合)。

## M7. 鲁棒性 / 工程硬化(不降精度前提)
- 语义门缓存、分层证据预算(Tier0逐字节/Tier2仅超包压缩)、自适应超时、逐单元优雅降级、传输重试。
- 记忆:[[skillflow-llm-resilience-work]]、[[doe-llm-timeout-too-low-blocker]](30s<真实judge 50-100s致静默卡死,提到150-180s)、[[doe-prompt-caching-and-usage-tracking]](endpoint缓存95.6%命中)、[[fcg-py-subprocess-utf8-encoding-bug]]、[[node-append-handle-stale-size-windows]]。

## M8. 契约/工程一致性(system 章或 method 附)
- 【契约】FCG↔DOE 沿 security_profile 契约切分;v5.0→5.1→v6演进。
- 记忆:[[fcg-doe-parent-field-and-nodepath-contract]]、[[m4-doe-refactor-and-perf]]。

---

## 竞品对照(每个 method 点要不要点名差异)
见 [[competitor-narrative-map]] [[same-group-deepread-gaps]]。禁用话术:first large-scale/prevalence/taxonomy/supply chain/bidirectional dataflow。改名 DOE/FCG→CoDE/SFG。
