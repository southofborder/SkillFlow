<!-- Current entry: CFG/processing alignment v9; seven calls and program assembly. -->

# 文档引导式分析：七调用与程序组装

更新：2026-11-02。当前入口使用 run v9、step/annotation v8 和运行时契约 v11，保持七调用与材料复用。CFG 和三个语义片段在初次生成及重建时都接收完整冻结源文。通过本轮离线验收后，用户授权 GA4、001、010、013 各一次全新 High 运行；四例沿用各自上一轮逐字相同的源包，按顺序串行运行。历史运行和失败保持原样。具体改动见 [CFG／processing 对齐](cfg-processing-alignment.zh.md)。

## 1. 七次语义请求

| 次序 | 阶段 | 输入与所有权 |
|---|---|---|
| 1 | Task | 完整冻结 Skill；独立提取目的、要求及冲突，与 flow 并行 |
| 2 | flow | 简短入口、来源、版本、条件、接收及未决关系说明 |
| 3 | CFG | 源文及 flow；不等待 Task |
| 4 | processing | CFG、flow、源文及运行时契约；提交处理片段 |
| 5 | task-correspondence | Task、CFG、processing、源文；提交需求与限制片段 |
| 6 | sensitivity | CFG、processing、源文；不接收 Task 或任务对应 |
| — | 程序组装 | 按显式引用合并三个片段，展开并编译；不调用模型 |
| 7 | source review | 完整源文与实际 Task、CFG、annotation；仅输出具体问题 |

两个 worker 仅写各自阶段目录；主线程更新根状态和选用组合。任务对应与敏感性并行。正常七调用不包含实际发生的结构纠正、共享修复或网络重试；这些全部单独计数。没有 relationships、独立图审查、环境确认或模型监控请求。

Task 只依据 Skill 声明用途，作者声明不等于真实用户授权。原文真实交互与运行参数保留。Task 修订仅接收源文、旧 Task、有限问题类别与源范围，不接收 CFG、敏感性或自由审查意见。

## 2. 模型片段与程序职责

三个片段直接使用短的带类型记录，程序生成可读视图，不再让第七个模型重新解释文档并填写整份 annotation。

| 片段 | 所有字段 |
|---|---|
| processing | ir_semantics、locations、expressions、processing_gaps；操作、顺序、模式、局部名称和输出绑定 |
| task-correspondence | realizations、demands、operation_demands；约束在 realizations 内 |
| sensitivity | declarations；只引用已声明的处理值和成员范围 |

processing 不得包含 Task demands 或敏感性；任务对应不得改写处理；敏感性不得改写 Task 或处理。程序验证真实引用，不根据邻近、同参、名称或 FIFO 猜测关联。每个内部位置保留片段来源和原位置，审查及纠正可以定位原始所有者。

程序生成内部编号、Task 版本引用、effect 层、call 请求/响应配对、确定默认、编译坐标、引用摘录和 realization status。模型仍选择真实来源、输出身份、条件、顺序、接收方及语义关系。不设逐项通过表，不自动产生 accepted 结论。

敏感性及表达式显式证据仅允许源文。省略时，从最近适用父级已有源文引用继承；不能把 CFG/rule 引用转换成敏感性证据。具体新判断可覆盖父级引用，程序继承不证明语义支持。

段数组默认声明 fixed 顺序；非固定顺序显式填写 partial。local 要求显式 returns，空 returns 与缺字段不同。yield 本身不是模型观察。

CFG 保留来源获取的真实 resource/result 输入和 dispatch 分支输入；程序只生成 bookkeeping，不补资源、边或生产者。源文复制使用明确物理范围，保留原语言及换行。

公开参数用 context acquisition 获取；内部调用在实际调用点保留输入、返回和副作用，函数名、metadata 参数表与独立函数体不代替值绑定。遍历使用 has_member 判断后进入 member 块；多路判断拆成已有二路判断，新 guided dispatch 超过两个后继时给出早期结构诊断。零参调用和真实无输入表达式仍可使用。

普通未说明更新方式的保存／写入采用公开的 replace 默认；源文明示 append 或 delete 时优先保留。模型侧可省略 mode，程序展开为明确模式，后端仍要求明确模式。序列化精度未说明本身不删除实际保存值、接收位置及后续计算。

审查发现若需要改变块、边、输入、公共输出或生产位置，使用 cfg 问题域；固定 CFG 内可修正的事实使用 processing 所有者。原有一轮依赖重建处理这些问题，不新增路由字段或自然语言归属推断。

### 统一抽象粒度

flow、CFG、processing、运行时契约与审查共享同一份边界粒度规则。纯局部计算可以不透明；改变获取、交付、保存、返回或状态版本的条件必须表达，普通条件优先使用已有 CFG 分支。代码不再强制保持整体黑箱，也不要求逐行展开或恢复内部调用栈。未知运行参数和 API 内容不等于行为无法建模。

模块接口取得与相关初始化分开，保留初始化前后状态的真实来源。调用摘要保留来源支持的替代结果和具名局部状态可能变化，不能将原状态改名当成新状态。审查需要质疑能用既有原语、合理边界拆分或受支持摘要表达的未建模声明；真正缺失的来源关系仍定位为局部限制。

## 3. 结构纠正与局部保留

每阶段首次回答加最多一次结构纠正。格式与实际类型同源；可识别子对象的证据、顺序、路径、local returns、外部获取和 dispatch 问题提前汇总，诊断给出具体记录与字段位置。

完整片段包括所有当前 CFG 指令，含 dispatch 和 return；程序提供必需 IR 身份清单。语义修复提交当前对象版本的完整替换，局部审查坐标不是输出子集。只有结构纠正使用指定记录替换；新 CFG 不默认拼接旧坐标。各可解析记录独立检查，已知类型错误不应遮住其他记录的引用与作用域问题。

片段纠正只支持已有记录的完整替换，不支持通用增删移动 patch。未替换记录保持；顶层不可解析、无法识别记录时才重交该片段。原始回复、合并候选和校验记录分别保存，响应链绑定实际候选。恢复和回放不重置预算，不重新生成已有答案。

同一替换机制用于新入口的 Task purpose／requirements／issues、CFG blocks／edges 和 review findings；旧独立入口保持原纠正规则。能够定位的语义记录不要求重抄整份 Task、CFG 或审查。所有替换仍通过原有全对象引用与语义结构校验，不自动修补其他连接。

纠正后仍无效的独立记录保留原始诊断；只有实际可识别、可独立验证的记录可以参与局部保留。程序生成的 validation-origin 缺口与模型 source-origin 缺口分开；前者不伪造源文证据。全部不可用时不创建空 annotation 冒充完成。

需求路径支持字段前缀和重复 each，如 pages → each → rows → each → keys，逐层保留成员对应。显式 CFG 的循环与嵌套使用有限摘要；不要求模型添加循环管理字段。基数不扩大为成员内容，不能移动 each、删除字段前缀或虚构 select_part。详见 [通用循环与契约精简](general-loop-analysis.md)。

## 4. 局部未建模与覆盖

真实计算的内部关系未知时，可使用已有 opaque、possible、alternatives 和 partial order；来源、实际动作、输出和效果仍需明确。Opaque 内容不代表可以省略来源或副作用。

processing_gap 锚定真实 instruction_id，可指明 outputs、locations、control，附具体原因和源文。unmodeled=false 仅限制已有完整 may 事实上的精度，不能隐藏实际缺失写入；unmodeled=true 表示该 IR 没有可执行语义，覆盖中明确保留。

程序沿结果消费、location 写读及控制关系计算影响范围。未给范围时扩大至该 IR 的控制可达后续。不能仅凭现有 slice 看不到某关系就断言无影响；同位置的跨分支读取也要考虑。

遇到未建模 IR，保留已计算前缀，不发布该块的新 OUT，让独立分支继续。不能简单跳过未知写入后继续使用旧状态。不构造假 compute、空事件、透传或未知输出值执行器。

已声明但没有实际传播记录的边界单列为“已声明、载荷或可达性未解析”，不冒充 sink record，也不显示成空载荷或不存在。受影响结论为未建立，不等于安全。Task 的真实全局用途冲突与未表达要求仍保持现有全局限制，本轮不增加 Task 范围求解器。

单层映射集合保留逐项 read/receive/call、yield/output、重复 occurrence、空/未知集合、候选版本及源成员配对。调用 cases 要求所属 IR 使用 fixed 顺序、至少保留一个返回候选；始终抛出的行为用真实 CFG 终止路径表达。cases 是不可递归的替代路径，保留正常、请求前失败、请求后失败及有依据的本地失败，错误来自调用异常结果，不从 URL 计算。

同一成员的多个 yield 是替代结果，不增加集合成员数，也不枚举整个数组的笛卡尔积。逐项 catch 后继续与未捕获失败必须分开；后者只在正常完成路径产生完整集合及后续保存，失败前可能已发生的交付仍保留。

具名 task-local runtime_context 允许有显式标记的 may 状态效果摘要。保留旧 handle、null 和可能新建 handle 的来源与创建时凭据，不能证明一定覆盖、命中次数或跨成员精确顺序。循环内不执行逐成员共享状态更新，空集合不产生成员初始化作用；源码明确 reset 继续用普通写入表示。该有限摘要不扩展为通用缓存、异常或任意未知值执行器。

## 5. 一轮语义修复

| 问题所有者 | 重建语义请求；其后程序重新组装并独立复审 |
|---|---|
| sensitivity | sensitivity |
| task-correspondence | task-correspondence |
| processing | processing、任务对应、sensitivity |
| Task | 隔离修订 Task、任务对应 |
| CFG | CFG、processing、任务对应、sensitivity |

多域取依赖闭包；全流程最多一轮。旧审查坐标绑定旧组合。新 Task/CFG/processing 引用一致、组装成功后整体选用；修复失败保留原合法组合和实际问题。源文审查只报告 cfg/task/annotation 具体问题，annotation 问题按程序来源路由；不生成逐项通过登记。

片段语义修复仅接收自己的旧记录、需复查的目标和原文范围，不转发统一审查的自由解释或建议；避免把 Task／敏感性等其他层的判断带入隔离角色。Task 的有限类别及源范围投影保持原有规则。

最终运行区分 complete、partial、failed、interrupted。partial 提供已知分析和未决覆盖；failed 对应无法形成可用组合或工程失败。新模型格式没有 whole-run cannot_assess 分支；真实网络失败和输入错误也不能伪装成 partial 成功。

### 通用精简与生成自查

新运行的 compact-v1 审查模型视图不发送展开的 target_index 与 annotation._fragment_origins；完整目录与归属关系仍保存于本地，供引用校验及修复路由使用。其余源文、Task、CFG、语义对象、观察、运行时契约及缺口保持。target_ids 沿用现有路径语法；错误定位只返回错误目标和最近有效父对象，不回传整个目录，也不自动改写目标。

规则适用于任意 Skill，不设置 GA4、文件名、节点数或 IR 数特例。不同版本、条件、接收方和 occurrence 不因长度合并；不把真实语义截断称为精简。各生成阶段针对已提供材料及自身职责在提交前自查并直接修正，复用现有 Task 自查，不输出检查过程、通过表或隐藏推理；初次生成与语义重建均适用。Task 与 sensitivity 的输入隔离不变，自查不是额外模型调用或准确性证明。

新运行的审查请求因输入超限或已确认结束且无完整答案而失败时，保存 request_failure、review=null、原始错误身份及调用定位。已有合法候选继续传播和 DOE，总结果 partial/diagnostic_only、审查 incomplete，不伪造空 findings。没有有效 findings 不触发语义修复；修复后复审失败保留原问题为未确认。材料损坏、归属不一致、编译失败、保存失败及用户中断不由此降级或隐藏。

## 6. 入口、监控与验收边界

```text
python -m tools.doe.document_guided_pilot prepare --input <Skill> --run-dir <new-directory>
python -m tools.doe.document_guided_pilot run --run-dir <prepared-directory>
python -m tools.doe.document_guided_pilot replay --run-dir <recorded-directory>
```

prepare 可选 --effort {max,high}，默认 max。配置封存在新运行；run/replay 不改档。正式入口没有 confirm/preflight、profile、harness hash 或 usage 验收门槛。

监控只读本地文件、进程和公开输出。自然附带 usage 被动统计，缺失或统计异常不阻止分析。已退出、无完整答案的暂态网络错误最多追加两次传输尝试；已有完整答案本地复用，空尾不能覆盖它。未知活跃状态不自动重启。

客户端在 CLI 启动前检查含包装的完整文本是否超过已知 turn/start 上限 1,048,576 字符；这不是模型 token 容量。超限保留完整输入和本地诊断，不裁剪、不重发、不计为模型启动。已有完整答案优先本地复用。未完成的上游材料明确阻断其依赖；若只有审查交付失败，可计算合法候选但保持未审状态。本轮不增加自动切片。原始异常类型在新运行现场及重放一致，根终态不得留下虚假的运行中阶段。

原始回答、三个片段、程序组装、校验、缺口、审查及选用组合保留；历史实验不迁移、不改写、不用新协议续跑。格式、传播和离线测试通过不证明自然语言语义等价、最小需求或优于直接 GPT。

工程验收、真实速度与准确性分别报告。研究比较统一看正确性、复杂 Skill 有用覆盖、重复稳定性及完整 tokens/耗时/实际复核工作量，不能只统计成功子集或把更多字段当作优势。
