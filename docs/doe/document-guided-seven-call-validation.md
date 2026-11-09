# 七调用与程序组装：离线实施验收

日期：2026-10-28。实现与离线验收完成。**本轮真实目标模型调用为 0，没有执行 Skill，没有续跑或改写任何历史实验。**

## 1. 实际交付

正常语义请求固定为 Task、flow、CFG、processing、task-correspondence、sensitivity、统一源文审查，共七次。annotation 由程序组装三个隔离片段并编译，不存在 annotation 模型请求。Task 与 flow 并行；CFG 不等待 Task；任务对应与 sensitivity 并行；最多两个 worker。

processing 只写处理、来源、版本、位置、输出及局部缺口；任务对应只写固定 Task 的需求、限制和对应；sensitivity 只标已有值的敏感范围。程序生成内部格式、版本引用、call 配对、编译坐标和状态，不推断实际资源、分支输入或接收者。语义修复仅传自身旧记录、目标与源范围，避免转发其他层的自由审查判断。

新入口没有整份 cannot_assess 模型分支。源文处理缺口与程序验证缺口分开。不能执行的 IR 保留显式覆盖，不制造空事件或假值；截止当前 block OUT，保留前缀，让独立分支继续。真实 Task 全局缺口仍保持原有规则。

格式检查提前汇总证据继承、顺序、local returns、each 路径、外部源和 dispatch 输入问题。每阶段最多一次结构纠正；P/M/S、Task、CFG 和 review 的可定位记录均使用同一套完整记录替换，不提供通用 patch。纯整图错误缺少结构化坐标时仍回退整份纠正，不解析错误文本猜关联。

完整 annotation 不可用时，统一审查仍看到真实存在的片段和失败阶段目标，availability.annotation 保持 false，不创建空标注。源文支持的具体问题可使用一次共享语义修复；格式失败本身不触发择优采样。新组合一致后统一选用，失败则保留原合法组合及问题。

维护样例已刷新为七份实际模板、三个片段及 schema、程序组装 wire/backend/compiled/mapping。真实 GA4 开发笔记保留历史标签；没有生成 GA4 答案或改动其冻结源文、Task。

## 2. 当前版本与可复核证据

当前实现 SHA-256：

`27c96eafa74c9c1f957df4116369198981f72833dd69d28b18ded84bf4c835d8`

该值由实际 implementation_provenance 产生，覆盖 177 个实现与形式化文件。release 证据生成前后及交付前重核一致。

| 接口 | 当前版本 |
|---|---|
| document-guided run / step / annotation | 5 |
| semantic fragments | 1 |
| 新统一 source review | fragment-v1 |
| security profile | 19 |
| processing compiler / compilation map | 11 |
| propagation records / propagation | 13 / 19 |
| demand / sensitivity review | 7 / 6 |
| Data | 5，未改变 |

- [release 机器证据](../../output/verification/document-guided-seven-call-v5/release/offline-evidence.json)
- [当前实现文件哈希](../../output/verification/document-guided-seven-call-v5/release/implementation.json)
- [最终集成测试 XML](../../output/verification/document-guided-seven-call-v5/release-integration-tests.xml)
- [英文片段格式](document-guided-fragments-format.md)、[中文设计](document-guided-analysis.md)、[维护样例](../../examples/document-guided/index.html)

## 3. 两条真实后端离线贯穿案例

这些是明确编写的合成工程夹具，回答由 fake client 提供 JSON 文本；它们不是 GPT 的真实分析成绩，也不是 GA4 参考答案。

| 案例 | 已知行为与预期 | 实际结果 |
|---|---|---|
| independent-excess | 一个分支存在不可建模缓存写入；独立分支将含 token 的配置交给模型，只要求正文 | 未知分支停止发布 OUT；独立分支得到 excess_supported |
| shared-location-unresolved | 将上述分支改为读取相同未知共享位置 | 相关结论未建立，无缩减建议；未将旧值当作写入后的新值 |

两条案例均完成七次 fake 语义交付、零结构纠正、程序组装、实际 CFG 编译、传播、DOE、保存和加载；最终 status 都为 partial，并保留一个未解析声明边界。两条均通过同进程以及不同 PYTHONHASHSEED 的全新 Python 进程重放，新增目标模型调用为 0。

为隔离本轮变化，工程夹具替换了未改变的外部图证书 renderer；CFG 编译、传播、DOE、材料验证和重放均使用实际实现。不能把这个夹具写成新完成了外部形式化验证或真实模型运行。

第二条内部枚举兼容 no_excess_established，但理由与展示为 Unresolved；它不表示安全、必要或已经证明无 DOE。尚未形成实际 sink record 的边界单列，不能作为空载荷或不存在。

## 4. 验证结果与复验记录

下列测试集合有重叠，不相加为独立样本或语义准确率。

| 检查 | 结果与范围 |
|---|---|
| 最后冻结后的集成批次 | **111 passed / 583.14 秒**；七调用、Max/High 配置、各修复闭包、部分材料审查、真实 JSON 文本纠正、有限预算、中断恢复、未知覆盖及重放 |
| 后端核心回归 | **425 passed**；循环、映射集合、版本、条件、需求、约束、敏感性与局部未知；新增局部限制用例 13 个包含在内 |
| 纯 facts 接缝 | **36 passed**；没有 compiled annotation 的低层测试视图不伪造配对，正式加载仍要求完整材料 |
| 相同参数及零参数 call | **2 passed**；显式配对、成员 occurrence 和响应身份保持；没有放宽网络请求规则 |
| 持久化／后端完整批次 | **281 passed + 1 次 producer 变更失败**；完全冻结后该精确用例复验 **1 passed**，不能表述为同一批 282 passed |
| 维护样例与格式回归 | **60 passed**；实际组装等于保存输出，断网且禁止 Client 构造的逐文件重生一致 |
| 最后 Task／CFG／review 记录纠正批次 | **72 passed**；包含 9 条真实 JSON 文本纠正、未改记录保持、预算及重放用例 |
| 静态检查 | 对涉及路径执行 diff --check 与 Python compileall，通过 |

完整前端开发批次曾为 281 passed、2 failed，分别是 expression 所有者与被动 usage 的旧测试假设；相应断言已按实际协议修正。后续隔离修复改为仅传目标与源范围，相应 owner 断言也加强并复验。原始失败 XML 与复验 XML 均保留，没有把失败文件替换成通过记录。最终 111 项集成批次在全部源码冻结后执行并通过。

补齐的实质问题包括：source-only 证据继承定位、分层校验遮蔽、真实 CLI 字符串的记录合并、跨进程缺口顺序、正常回答不能被注入伪验证缺口、运行时 literal 不能被当作源文件引用，以及部分材料的审查目标与修复路由。

## 5. 保留边界与研究结论

Task 的真实全局语义缺口仍可能限制多个边界；不可表示的输出之后，本轮采用截止策略，没有增加未知值执行器、共享缓存执行器或通用异常机制。不能用引用合法、格式通过或确定性计算完成证明自然语言语义完整。

原八调用 GA4 High 运行仍是其原来的失败：18 次 native 请求、1,525,001 已报告 tokens、约 66 分钟，没有 DOE。本轮没有重跑它，不能据七调用或离线测试推算真实加速比例、tokens 降幅、实际账单或准确性提升。没有目标调用，所以新目标 tokens、货币金额和人工复核分钟均无可报告测量。

本轮证明的是工程行为：模型不再重填完整 annotation，程序能够组装并校验隔离片段，局部未知不会自动抹去独立分支的分析。**是否在复杂真实 Skill 上优于直接 GPT，仍需新运行及同模型对照，当前没有新的实证结论。**
