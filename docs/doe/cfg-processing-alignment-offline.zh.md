# CFG／processing 对齐 v9：离线验收报告

**离线验收已完成：可按测试身份核对的 XML 回执联合覆盖 971 个当前案例，纠正复查后全部通过，未解决失败为 0。**首次流程集成的四项旧预期失败继续保留，这不是一次全绿的全仓执行。离线结果证明修正候选可以使用现有接口编译、传播、保存并生成 DOE；模型能否在完整 GA4 上自行生成正确候选，将由获授权的新线上验证回答。

本报告对应 [v9 设计与验收口径](cfg-processing-alignment.zh.md)。稳定生产候选 SHA-256 为：

`e5c8d5ffce9f94b02f103b284a2b366c32d9bd386727bfad8b78d6df79842154`

验收封存于 2026-11-02 21:44（中国时间），详见 [offline-acceptance.json](../../output/verification/cfg-processing-alignment-v9-20261102/offline-acceptance.json)。**验收时**尚未准备或启动新运行，实际模型启动数为 0；没有执行 Skill、恢复旧控制器或重放历史运行。随后运行的最新状态见 [continuation-state.json](../../output/verification/cfg-processing-alignment-v9-20261102/continuation-state.json)。

## 1. 保持的流程与完成的修复

正常流程仍为 **七次语义请求、最多两个 worker、程序组装 annotation**。Task 仍只读取完整源文；任务对应可读取 Task、CFG 和 processing；sensitivity 不接收 Task 或任务对应。已有已验证材料、编译结果和定位索引复用继续保留。

| 修复 | 实际行为与验证范围 |
|---|---|
| 完整源文交付 | CFG、processing、任务对应和 sensitivity 的首次生成及语义重建使用完整冻结源文。flow 或上游片段的引用不再裁定下游可见行。完全重复的嵌入代码及机械定位信息仍由程序处理。 |
| CFG 与 processing 的共同形状 | 公共输入通过 context acquisition 取得；内部调用保留实际参数、返回版本和边界。循环使用 `has_member` 判断后取得单个 `member`；多路条件拆成二路判断。零参调用、常量和实际不透明表达式仍合法。 |
| 多后继早期诊断及纠正 | guided dispatch 超过两个不同后继时输出 `binary_dispatch` 及真实位置。由于拆分需要新增块、改边，该项诊断在原有一次结构纠正内要求完整 CFG；其他可定位问题仍使用记录替换。没有增加预算或新的 patch 协议。 |
| 普通保存默认覆盖 | 仅模型侧 `write.mode` 可省略，程序展开为显式 `replace`。后端 `WriteOp` 的必填模式及输入校验保持；明确 append／delete 不受覆盖默认影响。运行时 v11 的 EM18 明示这是分析约定，不能声称源文明示覆盖。未知序列化本身不再成为删除实际写入关系的理由。 |
| 修复归属 | 需要修改块、边、输入、公共输出或生产位置的问题归 `cfg`；固定 CFG 内可修正的处理事实才归 processing。审查仍由模型选择有源文依据的域，程序沿现有依赖闭包重建，不从建议文字猜归属。 |
| 确定空集合的判断 | 回归发现过滤／映射后的已知空集合曾被当作未知。局部修复沿有限内容关系识别确定空的来源，不执行过滤谓词，不把未知集合的空记录误当作实际空集合，也不重建整个 DataRegistry。 |
| 未激活路径需求 | 已验证为 `not_reached` 的目标保留需求声明与追踪，产生非阻断 `inactive_goal`，不再为不存在的执行记录寻找 producer。该分支不被算作已满足要求；全部需求都未激活的 requirement 仍可得到 `unbound_requirement`。blocked／unmodeled／未解析绑定继续保持未决。 |

当前 guided run 身份为 v9，步骤／组装身份为 v8，运行时契约为 v11；源包格式未变。没有引入通用调用栈、异常执行器、缓存机制、额外模型阶段或新的监控模型请求。

## 2. GA4：已验证具体关系，未把局部夹具当作完整分析

[GA4 专项验收](../../output/verification/cfg-processing-alignment-v9-20261102/ga4-regressions/assessment.zh.md) 使用从 v8 冻结包逐字复制的十份相关源码构造独立候选，共 **22 项测试通过，119.33 秒**，其中七种路径实际经过编译、传播、正式保存和 DOE。完整线上输入仍是原有十六文件源包；这组离线候选不是完整 GA4 的新 CFG 或新模型答案。

已覆盖的具体行为包括：

- 公共 URL 参数有真实 context 获取；normalizeUrls 保留重复 occurrence 和来源顺序，局部字符串变换可保持不透明。实际 URL filter、client 获取、请求、新响应以及保存之间有可追踪的数据关系。空 URL 集合在 client、远程请求及保存之前返回。
- URL inspection 保留 `requestBody.inspectionUrl/siteUrl` 层级；返回字段来自实际响应。源码中的 `undefined` 使用不透明表达式，没有替换成 `null`。
- dotenv 返回与环境状态分离；可能更新后的环境保留已有值与新增候选。getSettings 使用当前环境的五个字段及独立 cwd 来源。indexing cache 的读写位置对应，旧 handle、新 handle 及创建时凭据来源保持区别；clock 是独立来源，只进入有源码支持的 fallback 候选。
- 批次正常完成、逐项 catch 后继续、URL 与对应检查结果配对均使用已有 cases／集合关系。错误从受保护调用的异常来源取得，同一 occurrence 的成功／错误候选没有被算成额外成员。
- compareDateRanges 的两个 helper 响应分别进入 period1／period2；saveResult 保存 comparison 及实际 metadata，而不是请求参数。返回 filepath 与保存内容保持为不同值。
- `rows → each → dimensionValues/metricValues → each → value` 可解析；字段消费者、完整原始结果保存和完整 metadata 要求分别保留，未因某接收方需要完整对象就扩大其他接收方需求。此前遗漏的 getAvailableFields／indexing 源文也纳入完整交付契约。

已知多余敏感字段的阳性与必要敏感使用的反例使用**单独声明的合成敏感变体**。这些变体不证明原始 GA4 metadata 含凭据，不进入新线上目标上下文。

本组初次测试曾暴露 acquisition 形状、源文件排序、引用行号、缺少正向需求及测试使用错误记录 API 等夹具错误，也发现真实 mapped 空集合判断缺口。所有初次失败和修正记录均保存在 [initial-checks.json](../../output/verification/cfg-processing-alignment-v9-20261102/ga4-regressions/initial-checks.json)，最终结果见 [final-checks.json](../../output/verification/cfg-processing-alignment-v9-20261102/ga4-regressions/final-checks.json)。

## 3. 三个小 Skill：实际传播与 DOE 结果

三个小 Skill 的五份源文件均逐字复制并保存来源哈希，详见 [源包 provenance](../../tests/fixtures/cfg_processing_alignment_v9/provenance.json)。新增 **23 个独立测试**在记录的纠正运行中全部通过，完整说明见 [small-regressions.en.md](../../output/verification/cfg-processing-alignment-v9-20261102/small-regressions.en.md)。

| 案例 | 离线实际结果 | 仍保留的解释边界 |
|---|---|---|
| **001 conditional-notification** | guard／member 分离后的图完整传播并保存；三个 occurrence，包括两个完全相同的记录，保持各自 recipient／原始 summary 配对。已知空过滤集合不产生 member／通知作用，仍到达计数和保存。旧 Boolean＋member 双输出形状作为独立非法候选保留。 | `filter_items` 是保留真实谓词的 may 子集，不是执行源码条件。`processed records` 的口径歧义独立归入 `R_COUNT`；因此传播完整，DOE 保持明确的 partial，不能将计数口径写成已确定。 |
| **010 catalog-query** | 四种可选参数组合均完成编译、传播、保存与 DOE。缺失参数实际省略，没有变成 null 或附加存在标记；保存值是对应响应的 total，返回值是同一响应的原始 items。普通保存默认 replace 与明确 append 分别通过。 | 原始源文没有支持敏感类别，零敏感比较是允许结果，不被解释成已证明安全。未知编码不阻断真实写入。 |
| **013 source-fetch-with-fallback** | 六种固定输入／结果场景覆盖四类终态及 key 缺失时的 archive 成败。首轮成功、重试成功、archive 成功及 archive 失败均有正确二路路由、不同响应／异常身份、终态追加顺序；archive 参数不包含 FAST_KEY。传播和 DOE 均完成。 | 固定场景是独立测试条件，不是对真实工具结果的预测。已确定不激活的路径保留 `inactive_goal`，没有凭空产生结果。旧 status 内容未知；正常生产初始状态已有获取逻辑，不需要补造源码读取。 |

013 另有一次真实编排回归：初始合法 CFG 漏掉 transient／non-transient 判断，源文审查将其归为 `cfg`，随后重建 CFG、processing、任务对应、sensitivity 并复审，复用 Task 与 flow。**12 个注入响应**完成了保存后的传播和 DOE；这包含现有共享语义修复，不改变正常七调用预算。

独立 DOE 能力变体为另一个诊断接收方明确声明敏感字段和参数要求：不必要的 private note 得到 `excess_supported`，明确要求该敏感参数时不产生该过量结论。它与原始 010 的源包和线上输入分开。最初将额外字段加入不透明 API 请求时，下游响应需求保守保留了该输入影响，不能据此断言多余；该初次失败及改用独立接收方的原因均保留在 [small-regressions-attempts.json](../../output/verification/cfg-processing-alignment-v9-20261102/small-regressions-attempts.json)。

## 4. 完整源文与提示成本

离线输入长度检查只说明**本次渲染的材料**能否经过当前 CLI 文本接口，不能推导模型 token 窗口，也不能保证任意 Skill 或未来更长修复材料都能提交。

使用旧 v8 存储材料进行只读渲染、采用新版完整源文规则时，GA4 十六文件源文视图为 **154,973 个 Unicode 字符**。八个被检查的首次／修复视图使用相同完整源文哈希；以下长度包含传输包装：

| 阶段 | 首次生成字符数 | 修复视图字符数 |
|---|---:|---:|
| CFG | 212,580 | 431,976 |
| processing | 477,424 | 638,846 |
| 任务对应 | 608,186 | 608,628 |
| sensitivity | 570,327 | 570,769 |

这些视图均低于当前 **1,048,576 字符**上限。但修复试算中的 findings 为空，会低估实际修复输入；新线上答案也可能更大。完整材料仍按实际提交文本检查，超限会明确记录，没有自动切片、静默截断或删除语义材料。此检查没有重新分析、重放旧答案，也不把旧材料导入新目标，见 [full-source-input-size-check.json](../../output/verification/cfg-processing-alignment-v9-20261102/full-source-input-size-check.json)。

连接例子使 CFG 示例从 **641 增至 6,766 字符**，processing 示例从 **2,474 增至 7,631 字符**；任务对应和 sensitivity 示例仍分别为 **1,298／705 字符**。同一小型测量夹具中，当前完整输出说明分别为 CFG **15,588**、processing **35,674**、任务对应 **16,756**、sensitivity **8,395 字符**。这些是字符计数，既不是实测 tokens，也不是 GA4 各阶段总输入。详见 [prompt-example-size.json](../../output/verification/cfg-processing-alignment-v9-20261102/prompt-example-size.json)。

本轮选择增加少量经过编译／传播的组合例子，以减少接口误解；尚无证据证明新增说明可由更少纠正请求抵消。后续真实运行需要报告全部正常、纠正、修复与传输尝试的实际成本。

## 5. 集成、独立审查和历史保留

以下是当前已取得的回执，集合有重叠，**不可直接相加为去重测试总数**：

| 范围 | 当前结果 | 证据 |
|---|---|---|
| 后端集成 | **599 passed，602.61 秒** | [backend-integration.xml](../../output/verification/cfg-processing-alignment-v9-20261102/backend-integration.xml) |
| 文档引导流程集成 | 首次 **366 passed、4 failed，992.42 秒**；四项旧预期纠正后全部复查通过 | [guided-integration.log](../../output/verification/cfg-processing-alignment-v9-20261102/guided-integration.log) |
| GA4 专项 | **22 passed，119.33 秒** | [final-tests.xml](../../output/verification/cfg-processing-alignment-v9-20261102/ga4-regressions/final-tests.xml) |
| 小 Skill／默认写入新增专项 | **23 个当前独立案例通过**，由分组纠正运行组成 | [small-regressions-attempts.json](../../output/verification/cfg-processing-alignment-v9-20261102/small-regressions-attempts.json) |
| 现有 flat／fragment／运行时相关模块 | **144 passed，11.97 秒** | [write-default-existing-regressions-corrected.txt](../../output/verification/cfg-processing-alignment-v9-20261102/write-default-existing-regressions-corrected.txt) |
| 最终本地观察／编排检查 | **3 passed，21.93 秒** | [final-controller-observation.xml](../../output/verification/cfg-processing-alignment-v9-20261102/final-controller-observation.xml) |
| 当前 XML 回执去重联合 | **971 passed，0 skipped，0 未解决失败**；文本专项回执作为额外证据，不重复加入该数 | [offline-acceptance.json](../../output/verification/cfg-processing-alignment-v9-20261102/offline-acceptance.json) |

集成时两个旧测试仍要求按引用行切片源码，与当前明确批准的完整源文契约冲突；原始失败保存在 [source-contract-old-expectations.xml](../../output/verification/cfg-processing-alignment-v9-20261102/source-contract-old-expectations.xml)。更新为完整源文预期后，整个受影响模块 **7 项通过，14.25 秒**，见 [source-contract-recheck.xml](../../output/verification/cfg-processing-alignment-v9-20261102/source-contract-recheck.xml)。这不是删除隔离检查：真实源文保留与 Task／敏感性隔离仍分别检查。

另有 `test_recorded_review_request_failure_keeps_compiled_doe_and_replays` 的两个参数化案例仍期待旧 v8 manifest 身份，复现为 v8／v9 的精确身份差异；原始失败保存在 [review-failure-reproduction.xml](../../output/verification/cfg-processing-alignment-v9-20261102/review-failure-reproduction.xml)。单一预期已更新为 v9，两个案例 **2 passed，54.07 秒**，见 [review-failure-recheck.xml](../../output/verification/cfg-processing-alignment-v9-20261102/review-failure-recheck.xml)，生产 SHA 未变化。四项首次失败均有明确旧预期原因，仍保留原始回执，**不表述成一次全绿集成执行**。

[独立工程审查](../../output/verification/cfg-processing-alignment-v9-20261102/independent-review.md) 当前没有未解决工程阻断。它复核了拓扑纠正、未激活需求、append 夹具真实性以及新四例队列的早期中断处理。审查最初将观察回调抛错推断成主分析必然终止，该推断过宽，已撤回并保留原回执；最终真实 fake-client 编排验证了普通观察 I/O 失败不改变七调用分析，而用户中断仍有不同终态。另有 **8 个独立假子进程队列场景**检查顺序、普通失败继续、缺少完成标记／中断停止，以及错误顺序、已有控制器标记、CLI 变化不启动目标。这些是工程情景检查，不是八次真实模型运行。

历史保留检查逐项核对了旧四例的 **82 个指定关键产物**，哈希均未变化；这项记录只覆盖列出的文件，不冒称扫描了旧运行全部文件。详见 [history-preservation.json](../../output/verification/cfg-processing-alignment-v9-20261102/history-preservation.json)。旧 v8 四例仍为 partial；GA4 旧结果仍是 **29／420 IR 已处理、13 个远程 API 点和 25 个 saveResult 点均未到达**，不得用本轮离线夹具替换或重命名该结果。

## 6. 当前限制与下一步验收

局部函数内部精度、条件完整可行性、精确缓存命中／创建次数、动态文件名归属和序列化仍受现有抽象能力限制。来源明确且关系不透明不等于整个 IR 必须停止；真实缺失的来源、作用或控制关系仍不能由假 compute、空事件或相似名称补造。

现有接口没有独立 `preserve=order` 属性。本轮保留源集合、occurrence 和 selector 对应，真实完整数组 value 需求可以保留相关关系；只要求顺序而不要求全部内容的独立限制仍须说明，不能悄悄扩大成整个数组必需。

所有离线修正候选均为明确编写的测试输入，独立助手审计不是人工金标准。此次结果不支持一般准确率／召回率、优于直接 GPT 或实际加速的结论。

离线验收通过，下一步按授权新建 **GA4 → 001 → 010 → 013** 各一次真实运行，使用 `gpt-6.1-sol / high / openai`、相同冻结实现与提示词、各自逐字相同的旧冻结源包，重新生成全部答案。每例仅一个控制器、一次零模型调用重放；不恢复旧实验或追加择优采样。正式报告须先回答传播是否完整、DOE 是否有用，再分开列出生成 IR 覆盖、源码边界覆盖、支持／矛盾／未决关系和完整可得调用、tokens、阶段及总耗时。
