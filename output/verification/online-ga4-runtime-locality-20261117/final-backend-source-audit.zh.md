# 主分析终态：后端与源文边界审计

对象为唯一运行 `document-guided-ga4-runtime-locality-high-20261117-205158`。本报告只读取本轮保存的 JSON、完整源文和冻结代码，没有执行校验器、传播、DOE、测试、模型、Skill 或重放。唯一重放与进程退出由 controller 负责，root 另行报告。

主分析结果为 **partial**。graph 修复没有返回完整答案，依赖它的 processing、mapping、sensitivity 和 re-review 均跳过。最终保留原始 **49 条需求 Task、继承的 489IR CFG、原 annotation 及对应初始审查**；已经完成的 60 条需求修订 Task 没有被选用。原来的 44 条审查发现全部保留，没有被标成修复完成。

## 传播与真实源文位置的记录

传播为 incomplete：**470 processed、4 unmodeled、15 blocked**，保存 470 份 IR 记录和 1033 个 Data。实际遇到的 unmodeled 为 ir001、289、295、436；blocked 为 ir002–013、290、296、437。另有源文声明 unmodeled 的 ir011 位于已被阻断的初始化后续，因此没有以实际遇到的 unmodeled 计数重复统计。

本轮 **operation_execution_error 为 0**，所以新实现的类型错误局部隔离路径仍主要由离线证据支持，本轮没有触发该路径的线上样例。ir148、151 均已处理，但不能把与上轮的差异完全归因于运行时修复：本轮 annotation 也改变了，ir151 目前通过不透明工具调用描述 normalizeUrls，没有再次执行上轮那个内部集合操作。

16 个源文件均与冻结快照哈希匹配。物理源文点与继承 CFG 一一对应，且已有边界记录：

| 物理源文点 | 总数 | 对应已处理边界记录 |
|---|---:|---:|
| 远程 SDK 调用 | 13 | 13 |
| saveResult 调用 | 25 | 25 |
| 存储工具内文件系统调用 | 7 | 7 |

这仅是**抽象边界记录到达数**，不是 Skill 执行或源文正确率。六个远程点有显式 CFG client 输入，但该 client 的入口 Data 没有直接出现在 remote inputs，call 实际只用 request；另七个 realtime/metadata 点虽获取 local ga，整个 IR 没有使用这个局部值。服务名称存在仍不能证明 receiver/authentication 依赖。25 个逻辑写入也不能证明 operation、extra、文件地址的来源正确；七个文件系统记录仍包括审查指出的“目录路径被当成写入内容”。F010 的 19 处错误返回绑定全部也被标成 processed，直接说明到达数不能替代语义忠实性。

## 两条 missing_part 的准确含义

ir457、459 都有成功记录，coverage 仍是 processed。前者从读取结果 result242 选择 value，后者从解析结果 result243 选择 value。报错 Data 均是完整的失败包装 `{fulfilled:false, exception:…}`；成功包装则有 `{fulfilled:true, value:…}`。

源文 `skill/scripts/src/core/storage.ts:103–114` 在 try 中读取并解析，异常进入 catch 返回 null。CFG ir456、458 在选择 value 前已经读取 fulfilled 并分支。保存的 branch alternatives 能区分字面 true/false，但成功消费者的 entry_state 仍同时带着成功、失败两种原包装。因此 select 能从成功包装得到结果，同时对尚未排除的失败包装报告 value 缺失。

这不是未知地址别名污染，也不是成功结果真的缺字段，更不能简单归罪为模型选错了源文字段。冻结代码 `solver.py:69–116` 只在 local guard 同时是该 IR 的公开 output binding 时定位对应状态；这两个 dispatch 没有 outputs，分支 binding 又为空，所以没有把判别字段与原包装版本关联并收窄。`interpreter.py:677–691` 对实际传入的失败候选报告 missing_part 是有效的，剩余问题是组合关系的精度。

需求侧各保留一条 IR 局部 upstream_diagnostic；两个 IR 合计 10 条 assessment、10 条 unresolved 范围。它们没有造成那 15 个 blocked，也没有使整份传播退出。后续方案应为受支持的判别字段选择维护原包装版本关联，覆盖 true/false 和独立状态的离线回归；不能反推任意不透明计算，也不能放宽缺字段检查。本轮冻结期间没有实施该方案。

## 审查绑定、需求与 DOE

需求结果引用的 receipt 哈希与所选审查完全一致：`9cd2b0d3b6f34b71f59b2f0eb99d2233872a3dc5d41b19c0829333635956d8b9`。review_status 为 complete，528 checks 中 **503 accepted、25 rejected**，1735 scopes 中 **1625 accepted、110 rejected**，没有结构性 validation barrier。但审查输入仍是 partial，因此 `source_review_complete=false`；初始审查仍为 diagnostic_only，44 条发现未解决。完整审查清单不等于语义全部通过。

需求结果 partial，共 **2004 assessments**：1091 个 operation input、590 个 CFG input、323 个 acquisition output；coverage 为 1989 processed、13 blocked、2 unmodeled。实际范围条目为：

| 状态 | 数量 |
|---|---:|
| required | 497 |
| unresolved | 3078 |
| deletable | **0** |

**可执行修改类型记录为 0。** 这些是跨用途、需求和信息属性重复出现的范围条目，不是不同字段的数量。497 条 required 仍以当前表示为前提，不能忽略未解决的源文发现。

共 **250 条 blocking 诊断：70 全局、180 IR 局部**。全局部分是 40 条 requirement_expression_gap、27 条 unbound_requirement、3 条 task_source_issue；49 条 realization 分为 27 retained_only、13 partial、9 expressed。局部部分为 108 条契约拒绝、22 条输出选择器缺口、20 条 processing gap、19 条 coverage、6 条 upstream diagnostic、5 条 expected_relation_mismatch。最后五条产生 wrong_input findings，位于 ir145、153、160、258、270，不是找出了五个多余字段。

**22 条输出选择器缺口涉及 13 个 IR**，包括 11 条 value、10 条 truth、1 条 shape，12 条路径非空，并非全是子字段。实际例子包括 ir167 的 rowLimit/startRow/save/dimensions、ir034 的 clientEmail/privateKey、ir440 的 resultsDir、ir150 的成员值与 shape、ir030.valid 的 truth。这证实整体 value 契约不足以支撑本轮部分实际字段/属性需求；应在有明确源文结构时补逐输出规则或用既有确定性构造操作，不能直接放宽整体契约的适用范围。

DOE 为 partial：**123 个 sink 均有记录 payload，295 个比较全部为 no_excess_established**。两个约束检查都是 not_established，未生成保持或删除方案。这不代表已证明不存在过度获取。

先前“必需动作没有成功记录时上游需求可能丢失”的静态风险，本轮既未复现也未排除。实际发布的删除为零，且 70 条全局阻碍使本轮无法单独验证这个风险；仍应作为后续离线回归，而非已发生错删或已消除风险的结论。

证据 `final-backend-source-audit.json`，SHA256 **`d3dd1b37fe8574e7672033ccbb29fedae56bb229d830d0e6249a95e4297d3eb0`**。其中保存源文点、操作、Data 和两条 missing_part 的精确证据以及终态统计。本轮没有自动改写 Skill 或追加实验。
