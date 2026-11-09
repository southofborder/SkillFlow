# GA4 v9：具体失败的独立离线回归

这组回归不读取或修改旧模型答案，不调用模型，不执行 Skill 代码，也没有重放旧运行。新增夹具引用从 v8 冻结包逐字复制的十份源码；完整十六文件线上材料由主线程独立准备。源码副本的 SHA-256 随夹具保存，每次加载均核对。

新增实现位置为 `tests/document_guided/ga4_alignment_v9_cases.py`、`tests/document_guided/test_ga4_alignment_v9.py` 与 `tests/fixtures/ga4_alignment_v9/`。这些是人工编写的边界候选与程序回归，不是完整 GA4 的新答案，也不能证明模型会自行生成正确标注。

## 已验证的关系

- 公共 URL 参数经真正的 context acquisition 进入调用，normalizeUrls 保持重复 occurrence 和来源顺序；其字符串变换可以不透明，不能因此截断整个集合。
- 非空路径先生成实际 URL filter，再读取 client，调用取得新响应；保存和后续读取绑定该响应，不能误绑定请求参数。空集合必须在 client、远程请求及保存之前返回。
- URL inspection 的请求保留 `requestBody.inspectionUrl/siteUrl` 层级；结果字段来自真实响应投影。源码的 `undefined` 使用不透明表达式，绝不换成 `null`。字段默认和内部精确表达式仍可保留精度限制。
- dotenv 的零参返回与 environment state 分离；可能 post-state 保留 prior 和新增候选。getSettings 从当前环境的五个具体字段及独立 cwd 来源构造设置，不把 config 返回值当环境。
- indexing cache 的读取和可能写入使用同一位置；既存 handle、新 handle 和创建时凭据来源不混同。时钟是独立来源，只进入源码支持的 fallback 候选。
- 使用已有源码 cases 夹具检查批次正常返回、逐项捕获后继续，以及 URL／结果配对。异常从受保护调用的真实异常边界获取，不能从成功响应或 URL 计算；同 occurrence 的候选不增加成员数。
- compareDateRanges 的两个实际 helper 响应分别进入 period1/period2；saveResult 的 data 参数绑定 comparison，再与真实 metadata 字段一起写入；返回 filepath 与保存内容是不同值。
- `rows → each → dimensionValues/metricValues → each → value` 路径可在现有需求引擎中解析。字段消费者和完整原始结果保存分别拥有需求，不因为一处要求完整保存就扩大其他接收方需求。
- discovery 的 apiName/uiName/description 与完整 metadata 要求分别保留。已知多余敏感字段阳性和完整必要用法阴性使用**单独声明的合成敏感变体**，不宣称原始 GA4 metadata 含凭据。

## 回归发现的真实后端缺口

空 URL 列表经 mapped for_each 后得到明确的空 mapped collection，但旧 `nonempty` 判断仍让非空边可达。修正后的独立测试要求 client、API、save 均为 `not_reached`。主线程对已有 `loop_guards.py` 做了局部内容判断修复；本代理未修改生产代码，也没有通过改变源码条件掩盖失败。

## 检查记录

初次 20 项执行有 19 项失败、1 项通过；主要是新测试编写时的错误：acquisition block 形状、源文行号、源文件排序、未登记正向需求、测试使用错误的记录字段／API。第二次为 9 失败、11 通过。第三次直接检查为 2 失败、12 通过、6 未选择，其中一项仍是测试访问错误，另一项是上面的真实 mapped 空集合问题。详见 `initial-checks.json`，没有把这些首次失败抹除。

后续完整 20 项通过，耗时 102.06 秒；再新增 comparison／保存 wrapper 回归后，针对 comparison、公参绑定及空集合的 4 项通过，耗时 21.02 秒。最终 **22 项全部通过，耗时 119.33 秒**，包含七种正式保存／DOE 路径，无未解决测试失败。执行记录位于同目录 `final-tests.log` 和 `final-tests.xml`。这些是本模块的验收结果，不是整个仓库一次全绿。

## 不扩大结论

测试能证明这些边界候选能够使用现有接口编译、传播、保存并形成 DOE 输入／结果；不能替代新线上四例的覆盖及正确性审计。库内部更新优先级、精确 cache 次数、文件名／JSON 字节序列化、源码条件的完整可行性仍保持未知。已知 empty pruning 使用实际集合关系，未知集合不能被当成空或长度一。

索引批次保留源 occurrence 的位置与完整输出数组 value demand。现有接口没有独立 `preserve=order` 属性，本回归不增加它；仅要求顺序而不要求全部内容的独立限制，不能被偷偷扩大成整份值需求。记录序列按身份规范化不代表运行时数组顺序，实际顺序关系由 base／selector 保留。

行字段消费者与 privateToken 是明确区分的合成验证材料，均不进入目标模型上下文。每种 source projection 的范围及未覆盖条件在夹具 README 中列明。
