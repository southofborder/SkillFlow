# 已验证材料复用：离线实施与验收

本轮在 GA4、001、010、013 的线上运行、各自唯一一次零调用重放和结果交付结束后实施。目标是减少普通读取、保存及逐条声明投影中的重复工作。正常七调用、两个 worker、Task／任务对应／sensitivity 隔离及传播语义保持。

**实现与离线验收已完成：去重后 1,274 个测试通过，没有未解决的测试失败。**最终记录见 [acceptance.json](../../output/verification/material-reuse-20261102/acceptance.json)。当前实现 SHA 为 `65e9060aa090ed51519310317dabd78a9aef2278bba5ee3bfdfcd73cfcfb9367`。这是多轮检查与针对性修复后的结果，不是一次全仓无失败执行，也不是一次新的 GA4 线上运行。

## 改动范围

1. **普通读取复用已保存的材料。**guided step 读取已选定的规范化值；annotation 读取已保存的 raw、compiled 和 compilation map。保留输入、依赖、终态、引用及产物字节身份检查，停止在普通读取时重新验证整条回答链、重新组装整份 annotation。显式 `recompute=True` 仍执行原来的重建，用于需要完整重算的检查。
2. **保存复用刚刚算出的结果。**guided 传播只加载一次 annotation，将已检查的编译结果带入计算和保存；保存时为现有传播材料附加最终 manifest。DOE 同样复用已检查的传播材料和刚生成的 review，不再为发布同一结果反复加载、重建。提交前仍检查输入没有变化。
3. **一次展开供多条声明使用。**processing 的 case aliases 和 member scopes 在一次校验／组装内共享；sensitivity 的每条声明不再触发整份 processing 展开。最终组合仍执行一次编译与对应检查。
4. **定位索引直接构建并复用。**CFG 索引沿已知位置生成相同条目，不再为每个条目重新扫描所有 IR；敏感性结果校验中的 demand target index 从三次构建合并为一次。外部路径解析仍检查真实路径与规范地址。

这是一次调用或计算内的普通对象复用，没有通用持久缓存、失效服务、新协议或额外模型阶段。独立的 legacy annotation loader 保留原有重建路径；本轮没有把历史入口一并翻新。

## 已完成的组件测量

| 对象 | 修改前 | 修改后 | 核对范围 |
|---|---:|---:|---|
| GA4 已保存的 420 IR CFG 定位索引 | 中位 1.44985 秒 | 中位 0.28439 秒 | 三次交替测量；9,843 个条目及整体 hash 一致 |
| 两条 IR、13 条敏感性声明的合成组装 | 18 次完整展开；中位 0.8685 秒 | 3 次完整展开；中位 0.2537 秒 | 三次测量；wire、raw、compiled、mapping 一致 |
| 合成 annotation 的三次普通读取 | 3 次组装、15 次回答链重建；单次中位 1.64965 秒 | 0 次组装、0 次回答链重建；单次中位 0.94164 秒 | 完整返回材料 hash 与夹具原始字节一致 |
| 合成 DOE 发布 | 4 次传播材料加载、3 次 review 重建；5.575 秒 | 1 次加载、0 次 review 重建；2.350 秒 | 单次测量；结果、索引及需求支持一致；两边均求解一次需求 |
| 合成 sensitivity 结果校验 | 3 次索引构建；0.109 秒 | 1 次索引构建；0.049 秒 | 单次测量；结果 hash 一致 |

测量使用本轮修改前备份与修改后的组件，其他依赖相同。时间会受本机调度影响；调用次数和输出一致性是更直接的证据。GA4 测量仅从保存的 JSON 构建定位索引，未加载其历史分析后端、重做传播或添加重放。

原始记录：[索引](../../output/verification/material-reuse-20261102/reference-index-benchmark.json)、[片段组装](../../output/verification/material-reuse-20261102/fragment-benchmark.json)、[普通读取](../../output/verification/material-reuse-20261102/saved-annotation-benchmark.json)、[DOE 发布](../../output/verification/material-reuse-20261102/doe-publication-benchmark.json)、[敏感性索引](../../output/verification/material-reuse-20261102/doe-index-benchmark.json)。

## 验收与发现的回归

专项检查覆盖输出一致、输入变更检测、原始材料工厂仍编译、部分结果保留、定位索引独立副本、成员／候选／接收方与局部返回、循环和集合需求，以及 fresh fake-client 七调用与零新增调用重放。综合回归覆盖相关 document-guided、annotation、传播和 DOE 测试。重叠执行不累加为不同测试；1,274 项来自汇总记录中的去重身份。

综合进程在 legacy 保存检查修复前已经导入旧模块，其原始结果为 **1,190 通过、6 失败，1,636.15 秒**。六项全部是下述已定位的字节变化检测问题；没有额外失败。最终代码下，受影响的整个传播 runner 模块 **54 项全部通过，299.08 秒**；专项八项复测也已通过。初始综合回执与最终复测分别保存在 [integration-tests.xml](../../output/verification/material-reuse-20261102/integration-tests.xml) 和 [integration-runner-recheck.xml](../../output/verification/material-reuse-20261102/integration-runner-recheck.xml)，没有覆盖失败记录。

独立审查及回归发现并修复了两处兼容问题：

- 合法的部分 task-correspondence 结果可以把缺口保存在 realization 中，同时有空的 `validation_gaps`。新读取路径已经允许这种情况，保留其部分状态与缺口。
- legacy 保存期间，即使上游文件只增加空白、JSON 值相同，也应保持原先的字节变化检测。现已复用已经加载的完整上游身份进行比较，没有增加加载或重算。

初始失败记录保留。还保留了开发期间的测试夹具、断言及临时接口未接通问题，并与上述产品回归区分。不能把多轮检查及纠正重跑描述为一次全仓无失败执行。[独立审查](../../output/verification/material-reuse-20261102/independent-review.md)记录了九个生产文件和后续补充审查。

最终九个生产文件的哈希全部匹配独立审查记录。另对四轮线上报告引用的 **82 个不同历史证据文件、109 条哈希断言**进行只读核查，全部一致；这项核查没有加载分析器或重放历史运行，也不声称检查了历史目录中的每个文件。

## 对线上结论的影响

本轮没有新增真实模型调用、执行 Skill 或重跑历史实验。字段、prompts、模型阶段数和语义修复预算没有改变，因此没有新的实际 token 节省结论。

四轮线上报告中的覆盖缺口仍然成立：GA4 的 29/420 IR 处理范围不会因为读取更快而扩大；三个小 Skill 的分支接口、写入语义及处理对应问题也未在这次改动中修复。它们的完整性、准确性和有用 DOE 结论以[已交付报告](../../output/verification/general-loops-v8-online-20261101/assessment.en.md)为准。

后续若授权全新运行，应分别观察模型生成耗时、局部计算／保存耗时和实际语义覆盖。当前证据支持“重复重建已经减少且已测组件输出保持一致”，不支持宣称整轮 GA4 已加速、完整 DOE 已恢复或优于直接 GPT。

英文实现说明：[Reusing validated analysis material](material-reuse.md)。
