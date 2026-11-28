# google-search 操作结果绑定与双向计算验证

## 改动

受保护操作可以用 `cases.outcome` 指定已有 CFG 的完成状态、正常返回和异常输出槽。每个 case 只发布实际产生的值。抛出异常的 case 可以用 `raise` 引用已有值，或引用本次调用产生的原始异常。分支选择使用同一次调用的完成状态、数据版本和写入后的状态，循环沿用原有成员绑定。请求发送前失败与发送后失败保留各自已经发生的效果；终止动作归属执行退出的指令。

`compute.expression` 使用已有操作数引用。对于字段投影，前向计算保留来源版本，反向计算把需求送回该版本的对应字段。对于 `count`，反向保留数量信息。无法还原内容的计算继续保留有依据的影响关系；原始异常的身份可以确定，其文本内容需要单独的证据。

## 完整源包自动审计

本轮从 946 字节的 `SKILL.md` 和 1099 字节的 `scripts/search.py` 重新开始。Task 与流程提取完成。CFG 草稿为 helper 的前驱增加了 `helper.return_scope`，并按入口填入 `cli` 或 `public`，但该项没有对应的正式参数输出与实参输入。结构纠正未消除错误，共享修订又改变了用于定位调用的源文位置。最终没有选定 CFG 或标注，传播和 DOE 未运行。模型新启动 7 次，记录到 195,783 个 token，耗时 538.0 秒。[运行报告](../../../experiments/doe/runs/document-guided-google-search-outcomes-high-20261125-190529/report.md) · [原始结构诊断](../../../experiments/doe/runs/document-guided-google-search-outcomes-high-20261125-190529/steps/graph/calls/a001/validation.json) · [修订诊断](../../../experiments/doe/runs/document-guided-google-search-outcomes-high-20261125-190529/steps/revision-graph/calls/a001/validation.json)

该轮使用的实现摘要为 `e6446245af558dfbd0935d462821afd716a960eb9fdab68d5336545a4740b8ec`。之后完成的版本配对校验、已排除分支的依赖隔离及表达式位置校验均以离线结果为准。[启动记录](dispatch.json) · [最终源码摘要](final-implementation.json)

对草稿副本的离线检查进一步定位了阻断原因。命令行调用和独立函数入口共用一个函数体；草稿用额外的 `helper.return_scope` 决定正常返回或异常发生后应回到哪个调用方。将这项从四参数表中去掉能消除局部实参诊断，但两个出口仍引用它。本轮修订允许修改的块不足以重建两个调用位置各自的返回与异常路径，因此未接受该草稿。[修订范围与两个出口的核对](graph-diagnosis/diagnosis.json)

## 在原 65 条 IR 上逐条验收

沿用先前已选定的完整 CFG 和对应 Task，在新的离线目录补写标注。38 个基本块、42 条控制边、65 条指令的顺序与操作数均保持一致。复用的 46 条语义中，44 条原样保留，两处 GET 补充了正常与失败结果。另补写 19 条缺失语义，并将 3 处退出动作归还给紧随打印操作的终结指令。原始实验文件均按摘要核对。[来源、范围和条目清单](full-source-witness/summary.json) · [完整标注](full-source-witness/authored-wire-annotation.json)

| 验收位置 | 传播与需求结果 |
| --- | --- |
| CLI 请求 `ir_036 → ir_037` | 记录发送前失败、已发送后失败以及正常返回。完成状态进入分派，返回值和异常分别沿对应路径传递。发送时的 `params.key` 可回溯到 CLI 凭据，R9 要求保留该字段。继承的检查条件还保留了一个凭据为空的候选。 |
| 独立函数请求 `ir_056 → ir_057` | 使用本次函数调用的凭据、响应和异常版本。两处请求合计得到 6 条与具体发送位置、参数槽及版本匹配的密钥比较，均有 R9 保留依据。 |
| CLI 错误输出 `ir_050` | stdout 可达，记录 5 个诊断消息版本。R12 要求打印完整异常字符串并以状态码 1 退出。当前证据未建立密钥值进入诊断文本的关系，也没有支持删除或脱敏的结论。 |

65 条 IR 均被访问。64 条为 `processed`，模块初始化 `ir_004` 沿用已有占位语义。前向整体为 `incomplete`，反向与 DOE 均为 `partial`。全部 20 条 DOE 比较为 `no_excess_established`。验证从公开编译、求解入口运行，使用合成输入，任务依据与实际记录的数据版本经独立脚本核对。[指令级证据](full-source-witness/named-ir-evidence.json) · [逐边界验收](full-source-witness/task-evidence-verification.json) · [完整前向事实](full-source-witness/propagation.json)

## 本轮新 Task 的独立切片

为单独检查后端，验证使用原样的两份源码和本轮自动提取的 Task，人工提供 3 个基本块、11 条 IR 的 CFG 和标注。切片从凭据与请求参数进入 Google 请求出发，在 GET 已返回响应的条件下，检查 `raise_for_status()` 的正常与抛出两条路径。11 条 IR 全部完成前向传播，反向和 DOE 因完整 Task 的切片外义务及异常格式化的证据缺口而为 `partial`。[切片范围与复现入口](source-witness/README.md) · [校验结果](source-witness/summary.json)

| 边界 | 边界可达 | 密钥内容 | 字段需求与删减 |
| --- | --- | --- | --- |
| Google 请求的 `params.key` | 可达 | 与环境变量的密钥为同一来源版本 | 本轮 R10 要求使用该值进行请求认证，保留 |
| 失败分支 stdout | 状态检查抛出的异常经格式化到达 stdout | 未建立异常文本含有密钥的字段或文本关系 | 本轮 R13 要求输出完整异常文本，当前证据不支持删除该输入或其中的密钥 |

两处结果来自公共编译、传播与 DOE 入口对人工标注的检验。整个过程使用静态源码与示例输入，没有访问 Google 或执行 Skill。

## 离线回归

在最终实现上运行了 149 个测试文件，共 2,539 项通过、1 项跳过、0 项失败。跳过项依赖本机缺少的一份可选历史实验材料。测试覆盖完整传播测试目录，以及与本次改动相关的语义前端和 DOE 用例，包含同值循环成员的独立异常、异常前后的状态与请求效果、字段投影与基数需求、旧标注格式兼容和错误版本配对。[独立计数及 JUnit 清单](offline-final.json)
