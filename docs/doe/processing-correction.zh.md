# processing 格式诊断与 CFG 实际依赖范围纠错

本轮改动让既有的一次纠错获得充分、准确的材料：明确写出 processing 共享输出的完整语法；在严格解析失败后补充能够独立确定的格式错误；当 CFG 根级错误确实由局部块被拒绝引起时，按真实生产者、控制和前驱关系选择足够的既有记录进行纠错。原有验收条件和整图校验保留，不增加语义请求。

代码和离线材料位于 [processing-correction-20261117](../../output/verification/processing-correction-20261117/)。2026-11-17 最终验收为 2367 个不同用例最新通过、1 项 Windows 符号链接权限跳过、0 未解决失败；原始失败及依赖补齐后的复验均保留，不是一次全绿或全仓库执行。详见[最终验收说明](../../output/verification/processing-correction-20261117/offline-assessment.zh.md)及[不可变记录](../../output/verification/processing-correction-20261117/offline-acceptance.json)。离线验收不能证明线上超时已经解决。另见 [英文设计](processing-correction.md) 和 [触发本轮工作的已关闭实验评估](../../output/verification/online-ga4-processing-timeout-20261116/assessment.zh.md)。

上轮实际暴露了两类问题。processing 首答重复写了 `shared_values`，还使用了 codec 不接受的助记名称；严格 JSON 解析先发现重复键，因此后续独立格式问题未能一起进入纠错。CFG 中两处局部读早于定义使两个块被拒绝，引用这些块的边随后产生根级缺失端点错误。原流程无法归属这个根级错误，只能要求整份 CFG 重写；仅选两个错误循环头又不足以修复，因为真实修复还要在循环体增加保留累积值的指令。程序必须保留这些错误，准确解释因果关系，并给模型足够的可编辑范围。

共享输出继续采用原有 `skillflow-processing-json-v1`，普通完整 JSON 仍可提交。可选封套恰有 `format`、`payload` 和一个 `shared_values` 表。定义名称严格匹配 `v(?:0|[1-9][0-9]*)`：允许 `v0`、`v12`，不允许助记名称或 `v01`。所有 JSON 对象成员只能出现一次。精确的 `{"$ref":"v0"}` 表示一个已声明的完整 JSON 值；允许前向、嵌套引用，拒绝缺失引用、循环引用及未使用但格式错误的定义。普通对象含 `$ref` 或 `$literal_object` 键时，通过 `{"$literal_object":[["key",value],...]}` 转义，各键必须是不同字符串。这里没有模板、局部合并、跨运行引用或省略记录后的继承。

同一份完整语法用于初始 processing、修订 processing，以及完整响应和既有记录两种纠错路径；自定义简短基础提示也会获得语法说明。示例展示前向／嵌套引用和字面对象转义，其说明字段不替代 fragment schema。初始和修订响应展开后必须显式覆盖全部当前 IR 及所需契约。局部纠错只替换允许范围中实际需要改动的槽，每个替换值完整提供，其余槽由程序原样复用，合并后重新检查覆盖。展开边界保持为 16,777,216 个序列化字符、500,000 个节点和 128 层，并限制引用间接深度。每次出现均得到独立值副本，继续接受既有 schema、引用、证据、覆盖和语义检查。

新增原始响应扫描器只在权威 parser／codec 已拒绝字符串之后运行，首条原始错误保留不变。扫描器保留对象成员的顺序、重复出现次数和位置，可以同时报告重复键、非法定义名称和其他可独立确定的局部格式错误。它不选一张“正确”的共享表，不合并候选表，不解析引用关系，不展开 payload，不返回可接受候选，也不进行语义判断。只有唯一且受支持的 `format` 声明才启用共享格式规则；格式身份有歧义时不作解释。字面对象的键按数据处理，只检查其中的编码值。即使完整扫描没有补充发现，也不表示响应可接受：悬空引用、循环等仍由原 codec 判断。

扫描上限为 2,097,152 个原始字符、100,000 个节点和 96 层。完整扫描按规则记录准确数量，每组最多展示三个例子，另列未展示数量；全部例子的序列化规模合计最多 12,000 字符。证据绑定原始字符串 SHA-256，位置使用从零开始、右端不包含的 Unicode 码点范围；对象位置还记录成员序号和同名键的出现次数。这些是原始响应位置，不冒充展开后的 IR 路径。非字符串输入不通过重新序列化虚构原始身份。语法不完整、触及扫描边界或受处理的扫描资源失败会明确标记诊断覆盖不完整，保留原始拒绝和完整响应纠错。完整原始回答仍进入既有纠错上下文；限制诊断例子不会截断源文、契约或候选。补充诊断始终位于根级，因此歧义共享数据不能被当作局部替换或隔离后的有效 fragment。

CFG 编译器保留原有错误代码、路径、消息、顺序及验收结果。只有原有构造器已经失败后，才额外记录端点错误的因果归属；要求构造器实际给出的唯一根级值错误，与结构化的完整缺失端点问题集合严格一致。每个端点必须引用本次编译中确实被拒绝的块。证据包括拒绝诊断的原始序号和值、块序号／引用／规范 ID、原始边序号、端点角色和编译候选摘要。字段校验错误、入口缺失及其他独立结构错误不会获得这种解释。仅用于诊断的图投影不会作为可用 CFG 返回，也不参与放行。

适配层另外把诊断绑定到实际接受纠错的原始 CFG wire 摘要。源文复制和规范化会改变编译输入，因此编译摘要只记录该输入的来源，不能假装与原始 wire 相等。`select_cfg_correction(candidate, diagnostics)` 核对原始候选绑定、拒绝诊断的归属、全部相关端点及序号后，才生成既有记录权限；权限还绑定完整诊断集合的摘要。

对于局部“读早于定义”或完全解释的被拒块级联，纠错范围包含受影响块所在的控制流强连通分量、这些块实际使用结果的生产者，以及直接前驱和显式声明的 carry 前驱。这样循环体中需要新增保留值指令的位置也在范围内。声明的 carry 前驱必须与真实入边一致。跨范围的读写引用及相关控制边明确记录为保持不变的参考关系；不会自动把所有下游消费者和上游祖先全部纳入可编辑范围。选择依据是实际身份和图关系，不依赖描述中的词、固定块半径、字符大小或 GA4 专用规则。

CFG 纠错提示提供完整当前候选、该阶段的完整源文、全部诊断、允许的记录 ID 和范围证据。模型可对允许范围中实际需要修改的既有块提交完整替换值，也可以在这些块内部增加有源文依据的指令和新结果标识。依赖范围纠错不能增删块、改变 `block_ref`、改边或改变入口。合并前，策略根据原始候选和诊断重新推导权限；过期候选、上下文或权限不通过。未替换记录原样保留，随后整个合并 CFG 仍接受原有严格校验。只改循环头、却没有提供新 carry 值生产者的响应仍然失败。

存在无法解释的全局错误、过期／缺失因果证据、歧义或畸形身份、需要新拓扑的 binary dispatch、缺少真实生产者或 carry 前驱不一致时，使用既有完整响应纠错。原始候选真正缺失的边端点不会被重新归类成“被拒块的级联”。定位明确且能够安全替换既有记录的普通 schema、入口或边错误保留原有局部纠错行为；依赖修复还需要改变拓扑时回退完整响应。程序不自动修复源文语义，后续源文审查继续核验语义忠实性。

当前协议身份如下：

| 材料 | 身份 |
|---|---|
| guided run | `skillflow-document-guided-run-v15` |
| document step | `skillflow-document-step-v12` |
| 语义 fragments | `skillflow-document-fragments-v7` |
| CFG 纠错范围 | `skillflow-cfg-correction-scope-v1` |
| 被拒块因果证据 | `skillflow-cfg-rejected-block-cascade-v1` |
| 原始响应补充诊断 | `skillflow-processing-wire-diagnostics-v1` |
| processing 可选输出，未改语法 | `skillflow-processing-json-v1` |
| processing 输入显示，未改 | `skillflow-processing-input-display-v1` |
| 结构纠错链，未改 | `skillflow-structural-correction-v5` |
| 组装后的 annotation，未改 | `skillflow-document-annotation-v10` |

guided policy 新记录 `processing_wire_guidance=complete-grammar-v1`、`processing_format_diagnostics=bounded-raw-pairs-v1`、`cfg_correction_scope=causal-dependency-records-v1`。Task v5 隔离、源文审查职责、后端 demand／DOE 语义及前一版 fatal-frontier 协议保持不变。旧产物保留原身份和结论，不迁移，不补写历史修复。

七次正常语义请求、两个 worker、每阶段一次结构纠错、一次共享语义修订、2700 秒原生进程时限和既有两次额外合格瞬态原生重试预算保持原值。不增加逐 IR 调用、探针或重试。授权的新 GA4 仍只能由 root 在离线验收后准备和启动；完整源文、验收实现、提示、运输层和可执行文件需冻结到其唯一 controller 所属零调用回放结束。本文不触发或增加任何运行授权。

阶段性材料包括 [CFG 编译器／选择器审计](../../output/verification/processing-correction-20261117/cfg-scope-offline-audit.en.md)、[摘要绑定证据](../../output/verification/processing-correction-20261117/cfg-scope-offline-audit.json)、[CFG 聚焦回执](../../output/verification/processing-correction-20261117/cfg-scope-final.xml)、[CFG 集成回执](../../output/verification/processing-correction-20261117/root-cfg-integration-01.xml)、[原始扫描器实现说明](../../output/verification/processing-correction-20261117/raw-wire-implementation.en.md)、[扫描器回执](../../output/verification/processing-correction-20261117/raw-wire-diagnostics-final.xml) 及 [processing 集成回执](../../output/verification/processing-correction-20261117/root-processing-integration-01.xml)。它们覆盖独立合成的重复共享表错误、诊断边界、足够依赖范围内的四处实际循环头／体修复、缺少 carry 时严格失败、过期身份和拓扑越界拒绝、完整源文、注入七阶段分析及零调用回放。519 指令的规模回归使用独立合成候选，没有导入历史回答。各回执有重叠，不能相加；初次失败的断言及对应修正回执继续保留。最终验收还须单独汇总最新且去重的测试身份、未解决失败、实现摘要和生命周期检查，之后才能依据新线上结果评价是否改善了实际失败。
