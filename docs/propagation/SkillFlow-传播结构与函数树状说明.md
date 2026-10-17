# SkillFlow 传播结构与函数：按审计顺序展开


## 当前处理段与字段关系

当前联合标注先生成 `model/local/default` 处理段，再由程序编译观察、最终效果及证据索引。
原始标注、编译结果和位置映射分开保存并绑定摘要；恢复与离线重放重新编译核对。
`local` 需要源文／CFG 机制依据与明确的回传列表；`model` 需要执行主体包含 llm。
程序不因观察接收方是模型就自动增加执行主体。新规则见
[字段关系与观察编译](SkillFlow-字段关系与观察编译.md)。

新增 `filter_items`、`subset_view` 和单层 `for_each`。逐元素作用域保留 collection/element 及
其 body，接收者与正文只在同一实例中绑定。已有 `select_part` 继续表达精确字段原值，
`compute` 表达运算或不透明关系，两者不能因为方便而替换。处理段是标注形式；编译后的
规格保留唯一 events 顺序，数据记录不再复制第二份模式表。


依据当前代码整理；现行版本见[字段收紧规范](../architecture/field-tightening.md)。本说明解释当前结构，不修改算法，不调用模型。

前面的呈现把模型声明、程序计算和文件存档混在一起，确实增加了审计负担。这里把它们分开。先读整体关系和编号，再看字段，最后查函数。

```text
一次传播分析
├─ 输入一：完整 Skill                         原始文件内容，供模型理解和引用
├─ 输入二：CFG                               第一阶段产生的原图
│  └─ IRInstruction                          图中的一条动作及其操作数
├─ 模型产物：RawAnnotationResponse           一次联合标注的原始响应
│  ├─ task / demands / expressions           全局要求与独立需求、计算语义
│  ├─ locations[位置别名]                     位置身份、访问范围、留存及操作数关联
│  ├─ ir_semantics[IR ID]                    谁执行，以及怎样取得、处理、交付数据
│  │  ├─ events[].processing / for_each      唯一处理顺序；段内使用符号 atomic_ops
│  │  └─ output_bindings[]                   把已有值登记为原 IR 的公开结果
│  └─ location_evidences[位置别名]           位置依据审计表，校验后独立保存
├─ 程序编译：sink_boundaries[]               交付／保存点的类型、等级及真实操作坐标
├─ 程序转换：to_payload(response)            显式取六项业务字段为 AnnotationPayload
│                                            这是传播输入，不含位置依据审计表
├─ 程序管理的数据：DataRegistry
│  └─ Data                                  一份数据的身份、内容关系、来源与说明
├─ 程序计算的状态：FlowState
│  └─ 位置 → 可能的 Data ID 集合              某个程序位置上，哪些值可能放在哪里
└─ 程序产物：PropagationResult
   ├─ registry                              求解后的全部 Data
   ├─ records[IR ID]                         每条 IR 的最终静态记录
   │  ├─ entry_state                        执行该 IR 之前的完整状态
   │  ├─ events[].atomic_ops[]               符号已解析成实际 Data ID
   │  └─ exit_state                         执行该 IR 之后的完整状态
   ├─ coverage                              哪些 IR 已处理、未处理或缺少绑定
   └─ diagnostics                           实际绑定错误、算法范围限制
```

其中 RawAnnotationResponse 是模型生成的业务候选；AnnotationResponse 是程序校验并编译后的投影。Data、状态和传播记录由程序生成。CFG 来自前一阶段。清单、摘要和调用次数用于复现与校验，放在最后解释。

**1．先分清编号，以及几个重复出现的词**

| 写法 | 它指什么 | 它不直接表示什么 |
| --- | --- | --- |
| `ir_007` | 一条原 IR 动作 | 某份数据 |
| `result_005` | 原图里的公开结果名称／位置 | Data 的内容身份 |
| `input[0]` | 当前 IR 第一个输入操作数 | 整个入口状态中的第一份数据 |
| `clean` | 当前 IR 内部的一个局部值名字 | 自动跨 IR 可见的变量 |
| `data_…` | DataRegistry 管理的数据身份 | 显示顺序或风险级别 |
| 页面 `D006` | 当前报告给某个完整 Data ID 起的短名 | 跨样例通用的 Data ID |
| `loc_model` | locations 表里的位置别名，由规格引用 | Data ID 或原文证据编号 |
| `(model_context, assistant)` | 实际位置的类别与名称，共同确定身份 | 存在于该位置的具体内容 |
| `g_0004`、源文单元编号、`EM02` | 图、源文、执行规则的证据定位 | 文件／模型／网络的交互位置 |
| `effect` | 该事件直接关联的安全效果 | 风险判断或另一份效果数组的索引 |
| `atomic_ops[0]` | 当前事件内第一个原子操作；顺序由数组位置确定 | 额外存储的 op_index 字段 |

`kind`、`form`、`op` 都是“选择具体类型”的标记，所处结构不同：ValueRef.kind 选择引用方式，FlowLocation.kind 选择位置类别，Data.content.form 选择内容形态，AtomicOp.op 选择固定操作。

`Data.annotations` 是数据本身的描述／已有敏感性标记；传播里的 `annotation` 是六项业务载荷 AnnotationPayload。原始模型响应没有 sink 清单；程序编译后的完整 AnnotationResponse 还包含 completed 状态和位置审计表，不直接传给求解器。

下面 `T[]` 表示列表；`?` 表示允许 null；`{D_A,D_B}` 表示候选集合。索引全部从 0 开始，源文行号从 1 开始。能为空的字段不一定能省略；每段会说明默认值。

**2．原图给传播器提供什么**

这部分是现有 IR，没有加入新的传播字段。

```text
ControlFlowGraph
├─ entry_block_id: str                     声明的入口块
├─ constraints: str[]                     全图约束声明；不是已执行的保护动作
├─ declared_context_keys: str[]            原图声明可取得的运行时键
├─ blocks: dict[块 ID, BasicBlock]
│  └─ BasicBlock
│     ├─ block_id: str                    块身份，与外层键对应
│     ├─ block_name: str                  人可读名称，名称不自动产生操作
│     ├─ data_source_kind: context/external/null
│     │                                  第一阶段的来源块分类
│     ├─ constraints: str[]               当前块的约束声明
│     └─ instructions: IRInstruction[]    该块中按执行顺序排列的 IR
│        └─ IRInstruction
│           ├─ id: str                   动作身份，如 ir_007
│           ├─ opcode: str               原图记录的开放动作名称
│           ├─ inputs: Operand[]         有序输入操作数；重复使用也保留位置
│           ├─ outputs: Operand[]        该动作定义的公开结果
│           ├─ constraints: str[]        当前动作的约束声明
│           ├─ metadata: dict            原有补充内容；传播器不执行其中代码
│           └─ draft_instruction_id: str? 提取草稿身份，便于追溯
└─ edges: CFGEdge[]
   ├─ source_block_id: str                从哪个块出发
   ├─ target_block_id: str                到哪个块
   └─ condition_text: str?                条件原文；本版不求解自然语言条件

Operand
├─ type                                  操作数属于哪种类型
│  ├─ literal                            明确的字面值
│  ├─ context_key                        运行时输入键
│  ├─ result                             某条 IR 已定义的结果
│  └─ external_resource                  文件／工具／服务等资源标识
├─ identifier: str?                      非 literal 的实际标识
├─ literal_value                         只有 literal 拥有的值
└─ semantic_name: str?                   原有语义名称，帮助理解 result_005 等编号
```

列表和 metadata 默认空，`data_source_kind`、`draft_instruction_id`、条件默认 null。非 literal 操作数不能填写 literal_value。原 IR 的 output 只能是 result；dispatch 和 return 不产生公开 output。因此普通 return 的 inputs 里可以有返回值，而 outputs 仍为空。

**3．Data：一份数据到底如何描述**

```text
Data
├─ id: str                               程序登记的稳定身份
│                                        内容改变产生新 Data；补充描述可保持 ID
├─ content: Content                      内容关系；下面五种形态选一种
├─ origin: Origin                        数据如何取得、属于谁、由什么产生
└─ annotations: Annotations              人可读描述、已有敏感性标签及其依据

Content（按 form 选择，不能同时填五套字段）
├─ OpaqueContent
│  └─ form = opaque                      有数据，但内部内容尚未展开；不是空值
├─ KnownPartsContent
│  ├─ form = known_parts
│  ├─ parts: DataPart[]                  已识别的可能组成，默认 []
│  │  ├─ path: Path                      这个组成在整体的哪个位置
│  │  └─ data: str                       对应另一份 Data 的 ID
│  └─ parts_complete: bool               默认 false：没有列出的部分仍可能存在
│                                        true 是调用方显式完整构造声明
├─ WholeExceptContent
│  ├─ form = whole_except
│  ├─ base: str                          被删减之前的整体 Data ID
│  └─ excluded_parts: Path[]             明确排除的路径，至少一个
│                                        其余内容继续保留，包括未知剩余
├─ FieldUpdatesContent
│  ├─ form = field_updates
│  ├─ base: str                          被更新之前的整体 Data ID
│  └─ updates: DataPart[]                至少一个路径—新 Data 对应关系
│     ├─ path: Path                      哪个位置要被替换／新增
│     └─ data: str                       替换为哪份 Data
│                                        未提及位置继续来自 base
└─ LiteralContent
   ├─ form = literal
   └─ value: JSON 值                     明确的字符串、数值、布尔、null、对象或数组
                                          null、{}、[] 三者不同

Path = 非空的 [PathStep, ...]
└─ PathStep
   ├─ str                               对象字段名，如 "user"、"0"
   └─ 非负 int                          列表下标，如 0；不是字符串 "0"

Origin（各项默认 null 或 []，按适用情况填写）
├─ at: str?                            哪个获取／处理位置产生它
├─ acquired_from: str?                 外部获取来源，如 storage:config.json
├─ part_of: str?                       若本 Data 是登记出的组成部分，它属于哪个整体
├─ path: Path?                         与 part_of 同时填写，指出部分位置
├─ inputs: Data ID[]                   实际参与此次操作的输入，保留次序与重复
└─ dependencies: Dependency[]          输入与结果之间的依赖关系
   ├─ data: str                        依赖哪份 Data
   └─ relation                         derived：声明有明确派生关系
                                       possible：保留未被排除的影响可能性

Annotations（各项默认 null 或 []）
├─ description: str?                   对这份数据的说明
├─ sensitivity: str[]                  已有敏感性标签，当前不固定标签词表
└─ evidences: str[]                    只用于后续 DOE 敏感性判断的依据，默认 []
```

Data 的 id、content 必填；origin、annotations 可省略，程序使用空描述。各 content.form 有对应默认值，但使用联合类型解析时仍应显式提供 form 来选择形态。

Data 不保存来源／依赖的证据链；`annotations.evidences` 不承接传播依据，传播不自动填写。完整组成的业务依据留在规格／构造边界，Data 只检查显式声明和结构冲突。不能重新打开完整组成、添加其未列出的部分，或改写同一身份的来源、输入和依赖关系。

四个必须分开的关系：

```text
content.parts:     C.owner → D_OWNER    表示 C 的这个位置明确保留 D_OWNER
origin.part_of:    D_OWNER 属于 A      表示这个部分的登记来源是 A
origin.inputs:    [B]                 表示生成当前结果时使用了 B
dependencies:     B / possible        表示仍可能受 B 影响，不等于含有 B 全部明文
```

把 A.owner 放进新对象 C，不会把 D_OWNER 的来源改写成 C。内容关系可以复用 Data；来源记录不应随着引用者变化而被改写。

`origin.part_of` 与 `path` 必须同时填写。登记为部分的来源不能同时填写 `at`、`acquired_from`、非空 `inputs` 或 `dependencies`；这些处理来源字段属于产生新结果的情况。

已知 parts 不保证同时存在；parts_complete=false 不代表空、错误或必须人工补全。WholeExcept 始终保留 base 的未知剩余。一次 field_updates 的路径不能相同或互为前缀；先改父字段再改子字段要写成两个操作，产生两份数据版本。

**4．联合语义：一条 IR 只有一份语义记录**

```text
RawAnnotationResponse
├─ outcome = completed
├─ task                                全局目的、要求、依据及 CFG 对应
├─ demands / expressions        真实 CFG 目标；模型不填 goal ID
├─ ir_semantics[IR ID]
│  ├─ operator[]                       执行主体；不重复，排列无时序意义
│  ├─ operator_evidences[]              定位与 reason，加 value 指明主体
│  ├─ empty_effect_evidences[]          仅无非空效果时必填；其他情况省略
│  ├─ order                            fixed / partial
│  ├─ events[]                         processing 或单层 for_each
│  │  └─ processing.events[]
│  │     ├─ effect                     当前阶段标签，或 null
│  │     ├─ evidences[]                 非空效果的分类与阶段依据
│  │     └─ atomic_ops[]                当前阶段的有序数据操作
│  ├─ output_bindings[]                真实公开结果绑定
│  └─ sensitivity[]                    已有符号值及信息范围的敏感声明
├─ locations                           位置身份与边界属性
└─ location_evidences                   位置 ID → 非空依据列表

AnnotationResponse（编译结果）
├─ outcome = completed
├─ task / demands / expressions        单一任务与规范化需求；goal ID 由程序生成
├─ ir_semantics[IR ID]                  同一 IR 记录，events 已展开观察
│  └─ precedence[]                     程序生成的必要先后关系
├─ locations / location_evidences
└─ sink_boundaries[]                   程序生成
   ├─ instruction_id
   ├─ event_index / op_index
   ├─ body_event_index / scope          逐元素位置及作用域
   ├─ target                           已声明边界 ID
   ├─ sink_type                        固定六类边界
   └─ exposure_level                   固定 1/2/3 级；0 级仍传播但不入清单

SourceEvidence                         CFGEvidence                RuleEvidence
├─ file                                ├─ target: CFGTarget       ├─ rule_id
├─ start_line / end_line                └─ reason                  └─ reason
└─ reason
```

不再维护 `profiles`、`roles`、平行 effects 数组或 effect_index。效果随事件出现，重复阶段各保留独立依据。主体仍为 llm、agent_runtime、tool、human。编译观察不机械增加 llm。效果词表不变；model_observe 只由编译器生成。

证据用文件行范围、直接 CFG target 或 EM rule_id 区分，原文按真实文件行提取，模型不再抄 quote、basis 或摘要。operator_evidences 只额外填写 value；空主体使用 null。null 效果没有效果依据，但数据操作依据仍必需。无非空效果的 IR 仍须解释，不等于 NOP 或 IN/OUT 相同。

传播业务 `AnnotationPayload` 严格只含 task、demands、expressions、ir_semantics、locations、sink_boundaries；完整响应的 outcome 与位置证据通过显式投影剥离，不能由求解器静默忽略。Task bindings 保留图中对应关系，不自动成为需求起点。真实源文可支持错误解释；引用通过不等于语义正确。

**5．位置声明与符号引用：传播前先把“哪里”和“哪个值”说清楚**

```text
LocationSpec
├─ kind: runtime_context/storage/model_context/remote/tool/user
│                                        边界类别，同名跨类别不会合并
├─ name: str                            稳定位置名称，如 config.json
│                                        symbolic: 前缀表示具体身份未确定
├─ operand_refs: OperandRef[]            必填，可为 []；关联实际 IR 操作数
│  ├─ instruction_id: str               原图哪条 IR
│  ├─ side: input/output                该 IR 的输入侧还是输出侧
│  └─ index: 非负 int                   该侧第几个操作数
├─ access_scope: task/recipient/shared/public
│                                        任务内部、另一接收主体、共享或公开
└─ retention: task/persistent/null       存储／上下文必非空；其他边界未建模留存可 null

ValueRef（按 kind 四选一；此时没有实际 Data ID）
├─ InputRef
│  ├─ kind = input
│  └─ index: 非负 int                    当前 IR.inputs 的位置
├─ LocalRef
│  ├─ kind = local
│  └─ name: str                          本 IR 内前序操作定义的局部名，如 clean
├─ LiteralRef
│  ├─ kind = literal
│  └─ value: JSON 值                     原文／图中明确给出的字面值
└─ AlternativesRef
   ├─ kind = alternatives
   └─ items: ValueRef[]                  至少一个候选引用，取可能值并集
```

位置声明不会自动读取或写入，operand_refs 也不是数据传输操作。`locations["loc_cfg"]` 的别名用于规格查表，实际状态位置使用其中的 `(kind,name)`。同一精确位置不能用不同别名重复登记；同一位置也不能重复关联同一操作数。

operand_refs 是业务映射：解释 context_key 输入时，它决定该操作数关联哪个上下文位置；实际值引用使用未关联的 context_key 时才以其名称解析位置；未被值引用使用的上下文入口不额外建立叶子种子。无法关联具体操作数的边界可以写空列表，但仍须在独立 location_evidences 表中提供依据。旧 anchors、SourceAnchor 与位置内 evidences 均已移除。

访问和留存属性不改变 `(kind,name)` 身份，也不自动把数据送到该位置。模型识别这些属性，程序按固定表生成等级；工具未知部署保留外部接收可能性，但不制造网络效果。任务内部临时写入继续传播而不单列 sink，删除不交付旧值。完整默认及六类边界见[Sink 边界规范](SkillFlow-Sink边界与固定分级.md)。

input 索引必须存在，不能把 external_resource 操作数当内容值引用；读取资源内容要用 read。若资源名称本身确为载荷，可以用有依据的 literal。local 只在当前 IR 内有效。alternatives(A,B) 是“可能 A，也可能 B”，不是构造一个包含 A 与 B 的对象。

通常 local 由前序操作定义。order=partial 时，当前实现还允许 alternatives 中包含后续定义的 local，但必须同时保留已可用候选，且定义关系不能形成循环；不能仅引用一个尚不存在的后续结果，从而遗漏此前可能使用原数据的情况。

**6．IR 事件：唯一的操作顺序**

```text
IRSemantics（编译后的 IR 语义，动作字段见上一节）
├─ order: fixed / partial
├─ precedence[]                        程序生成的因果约束
├─ events[]                            EffectSpec 或单层 ForEachSpec
│  └─ EffectSpec
│     ├─ effect: Effect/null           该次效果；不通过另一份列表索引
│     ├─ evidences: SpecEvidence[]     非空效果必填；null 效果规范化后省略
│     └─ atomic_ops: AtomicOp[]        非空；保留参数和操作次序
└─ output_bindings[]
   ├─ output_index                     原 IR.outputs 下标
   ├─ value                            已有 ValueRef，不是一次隐藏计算
   └─ evidences                        对应关系的依据
```

无标签事件只支持 possible compute 或 tool 边界的 receive/deliver，不能隐藏已知效果。RawIRSemantics 在 events 中保存处理段；编译后的 events 可以比原事件更多，因此编译映射保留 raw_path、raw_atomic_range、compiled_path 和处理模式，不能用相同数组下标代替。

**原子数据操作 的所有字段如下。每一类都必须有 `evidences: SpecEvidence[]`，至少一条；以下树中逐项保留它，便于对照。**

```text
ReadOp                                  从已有位置取得当前内容
├─ op = read
├─ location: str                        locations 表的别名
├─ output: str                          新定义的局部值名，如 raw
└─ evidences: SpecEvidence[]
    求值：位置 → 当前候选 Data；不复制已有 Data，也不自动添加模型观察。

ReceiveOp                               取得外部响应
├─ op = receive                        取得工具／远端内容，不局限于网络
├─ location: str                        远端或工具位置别名
├─ inputs: ValueRef[]                    相关请求输入；可为空，保留参数顺序
├─ output: str                          响应的局部名
└─ evidences: SpecEvidence[]
    求值：生成 opaque Data，记录外部来源与请求的 possible 依赖。

DeliverOp                               交付／观察当时的数据版本
├─ op = deliver
├─ inputs: ValueRef[]                    实际交付值，不能默认为整个 IN；零参数 tool 可为空
├─ target: str                          接收边界的位置别名
├─ when: ValueRef/null                  仅编译观察：消费条件；原始 DeliverOp 禁止该字段
└─ evidences: SpecEvidence[]
    求值：记录数据与边界；不改变内容，不自动写出可读取的远端状态。

WriteOp                                 改变以后能读到的位置绑定
├─ op = write
├─ target: str                          上下文或存储位置别名
├─ mode: replace/append/delete
│  ├─ replace                           目标改为输入值
│  ├─ append                            旧内容与追加值产生新内容
│  └─ delete                            解除绑定，不自动读取旧内容
├─ input: ValueRef/null                 默认 null；replace/append 必填，delete 不得填值
└─ evidences: SpecEvidence[]
    求值：改变状态。没有局部 output；新文件 Data 从记录 changes.after 查。

SelectPartOp                            明确选取一个部分
├─ op = select_part
├─ input: ValueRef                      原整体
├─ path: Path                           要选取的字段／下标路径
├─ output: str                          选取值的局部名
└─ evidences: SpecEvidence[]
    求值：解析或登记部分，可复用已有 Data ID。知道字段存在不自动执行此操作。

ExcludePartsOp                          明确删除若干部分
├─ op = exclude_parts
├─ input: ValueRef                      原整体
├─ paths: Path[]                        至少一条排除路径，不重复
├─ output: str                          删除后结果的局部名
└─ evidences: SpecEvidence[]
    求值：生成 whole_except Data；不把剩余内容重写成当前已知字段列表。

UpdateFieldsOp                          覆盖／新增字段，其余内容保留
├─ op = update_fields
├─ input: ValueRef                      原整体
├─ updates: FieldValue[]                至少一项，路径不能重复或交叠
│  ├─ path: Path                        修改的位置
│  └─ value: ValueRef                   新值从哪里取得
├─ output: str                          更新后整体的局部名
└─ evidences: SpecEvidence[]
    求值：FieldValue.value 解析成 Data ID，存入 field_updates.updates[].data。

BuildOp                                 明确构造新对象／列表
├─ op = build
├─ container: object/list               容器形态
├─ parts: BuildMember[]                 完整构造规则；可为空，表示明确空容器
│  ├─ path: Path                        组成在新容器中的位置
│  ├─ value: ValueRef                   放进来的原值
│  └─ when: ValueRef/null               可选布尔控制；只允许条件对象字段
├─ output: str                          新容器的局部名
└─ evidences: SpecEvidence[]
    求值：非空构造保存为完整 known_parts；空构造保存 literal {} 或 []。
    构造列表的下标须从 0 连续；同一层不能同时当对象字段与列表下标。

ComputeOp                               已知派生或不透明处理，不执行真实函数
├─ op = compute
├─ inputs: ValueRef[]                    实际参与处理的输入，允许重复
├─ dependencies: [derived/possible,...] 与 inputs 一一对应，同长度、同次序
├─ output: str                          结果局部名
└─ evidences: SpecEvidence[]
    求值：生成 opaque Data 和依赖关系，不实际执行 sum、加密或任意源码。
    合法的零输入结果可用两个空列表，不能因此伪造外部来源。
```

`FieldValue` 是传播前的“路径 → 符号值”；`DataPart` 是传播后的“路径 → Data ID”。两者不是两份需要人工维护的相同数据，而是求值前后两个阶段。

安全 effect 与 op 也不相同。例如同一个 deliver，在 net_send 事件中表示发送，在 model_observe 事件中表示模型观察。一个 effect 可包含多个 op；read／receive／deliver／write 等必要边界操作不能被一个 compute 代替。

**7．状态和记录：程序到底算出了什么**

先把三种小类型读成一张表：

```text
FlowState                               一张“位置 → 可能值”表
└─ bindings: StateBinding[]             JSON 中的行；默认空，内存保存为 tuple
   ├─ location: FlowLocation            这一行的位置
   │  ├─ kind                           位置类别
   │  └─ name: str                      类别内的名字
   └─ data_ids: frozenset[Data ID]      这个位置当前可能对应哪些 Data，非空

示例表
├─ (result, result_001) → {D_B}         公开结果 result_001 代表 B
├─ (storage, status.txt) → {D_OLD,D_NEW} 文件在不同路径可能是两个版本之一
└─ (runtime_context, cache) → {D_B}     cache 目前可能保存 B
```

FlowLocation 不是另一份入口状态，StateBinding 不是另一份 Data：它们分别是表的键和表的一行。IR 的 entry_state／exit_state 才是这张表在两个程序位置的快照。

FlowLocation.kind 支持 `result、runtime_context、storage、model_context、remote、tool、user、intermediate`。位置声明的 LocationSpec 只支持六种外部／交互位置，没有 result 和 intermediate。公开结果由 output_bindings 登记；当前解释器的 local 值放在 IR 内部字典，不会强制为每个 local 增加一行 intermediate 状态。

frozenset 内只有 ID 字符串，不放可变 Data 对象。一个位置的候选集合不能为空；没有绑定就不写这一行。整个 FlowState 可以为空，表示没有已登记绑定，不表示“无数据”“不可达”或“全都安全”。

```text
IRFlowRecord                            一条 IR 的最终静态记录
├─ entry_state: FlowState               当前动作之前的完整状态
├─ events: EffectEvent[]                按原规格位置排列
│  └─ EffectEvent
│     ├─ effect: Effect/null            当前标签；无标签保守计算或工具获取为 null
│     └─ atomic_ops: AtomicOpRecord[]   与规格逐项对应，顺序由数组表达
│        ├─ op: 固定操作名              read、compute、deliver 等十选一
│        ├─ inputs: frozenset[Data ID][] 原子操作的实际输入，保留参数次序和重复
│        ├─ outputs: frozenset[Data ID][]阶段结果，保留输出位置
│        ├─ endpoints: FlowLocation[]   来源／接收边界
│        ├─ changes: StateChange[]      该步骤产生的位置绑定更新
│        ├─ members[]                   仅 build：字段到 inputs 的映射，不复制 Data ID
│        │  ├─ path                    字段路径
│        │  ├─ value_input_index       值输入槽位；确定省略为 null
│        │  └─ when_input_index        控制输入槽位；无条件为 null
│        └─ when_input_index           仅编译条件观察：不属于观察载荷
└─ exit_state: FlowState                当前动作之后的完整状态

输入／输出的 JSON 示例
└─ [["D_A", "D_B"], ["D_A"]]
   ├─ 第一个参数可能为 D_A 或 D_B，不表示两者拼接
   └─ 第二个参数再次使用 D_A，不能与第一个参数合并

StateChange
├─ location: FlowLocation               更新哪个位置
├─ before: frozenset[Data ID]           更新前的候选，可为空
├─ after: frozenset[Data ID]            更新后的候选，可为空
└─ update: strong/weak/delete
   ├─ strong                            确定目标：用新绑定替换旧绑定
   ├─ weak                              目标／时序不确定：旧候选与新候选都保留
   └─ delete                            确定解除绑定，after 为空
```

当前事件层已经没有额外的 inputs／outputs 副本，它们只在 atomic_ops 下。一般字段路径和依据仍在对应的规格中；build 额外保留成员路径及输入索引，条件观察保留控制索引，不复制证据；通过 `IR ID → event 列表位置 → atomic_ops 列表位置` 对应查回。记录不保存 ref、op_index、effect_index 或逐步骤 notes；order/precedence 和动态诊断分别保存。

read 的输入来自位置，所以记录 inputs 可以为空，来源放 endpoints，读到的数据放 outputs。write 的 inputs 只记录本次写入参数；append 所用旧文件在 changes.before 和新 Data.origin.inputs 中。write 没有局部 output，因此它生成的新文件版本见 changes.after。deliver 通常不改变状态，所以它的 IN／OUT 可以相同，但观察或发送仍然确实记录在事件中。

**8．同一个例子，把上述结构连起来**

教学用 D_B、D_CLEAN 是短写，不是生产 ID。假设原图中的一条动作明确先让模型观察 B，再删掉 api_key，再观察删减结果。

```text
原 IR
├─ id = ir_filter
├─ inputs[0]  = result_B
└─ outputs[0] = result_clean

profile
└─ effects = [model_observe, transform, model_observe]

ir_semantics[ir_filter]
├─ events[0]：effect=model_observe
│  └─ deliver(input[0], target=loc_model)
├─ events[1]：effect=transform
│  └─ exclude_parts(input[0], paths=[["api_key"]], output="clean")
├─ events[2]：effect=model_observe
│  └─ deliver(local("clean"), target=loc_model)
└─ output_bindings[0]
   ├─ output_index = 0
   └─ value = local("clean")

求值时的对应关系
├─ 入口状态：result_B → {D_B}
├─ 第一次 deliver：input[0] → {D_B}      观察原数据
├─ exclude_parts：生成 D_CLEAN
│  ├─ content = whole_except(base=D_B, excluded_parts=[["api_key"]])
│  ├─ origin.inputs = [D_B]              处理用到了 B
│  └─ local 字典：clean → {D_CLEAN}
├─ 第二次 deliver：local("clean") → {D_CLEAN}
└─ 公开输出登记：result_clean → {D_CLEAN}  不再生成另一份 Data

records[ir_filter]
├─ entry_state：result_B → {D_B}
├─ events：分别记录 D_B、D_B→D_CLEAN、D_CLEAN
└─ exit_state
   ├─ result_B → {D_B}                  原数据身份仍保留
   └─ result_clean → {D_CLEAN}          新结果有了公开位置
```

因此 `origin.inputs=[D_B]` 与 `whole_except(base=D_B,...)` 并不矛盾：前者说“用什么生成”，后者说“结果保留什么”。第一次观察也不会被后面的 D_CLEAN 改写。

**9．主要函数：按运行顺序读，不按文件名猜**

```text
annotate_skill(source, cfg, *, client)
├─ prepare_material(source, cfg)         核验源文与图，冻结唯一运行时规则，直接校验已有 CFG 引用
├─ build_prompt(material)               拼出英文指令、类型契约和完整输入
├─ client.complete(prompt)              一次模型调用
└─ validate_response(raw, material)      解析 JSON、检查引用、覆盖、证据与规格
    ├─ AnnotationResponse 校验          completed 分支结构、位置审计表覆盖及枚举合法
    ├─ validate_specs(cfg, annotation)   效果位置、操作数、local、输出覆盖等合法
    └─ check_evidence(...)              引文确实存在于所指源文／图／执行规则

to_payload(checked_response)            显式生成 AnnotationPayload 六项业务载荷
                                       不自行复核引文，也不把位置审计表送入求解器

propagate(cfg, annotation, *, initial_registry=None, initial_state=None,
          schedule="fifo", max_variants=100000)
├─ 检查 CFG、AnnotationPayload 与规格     不接收完整响应，不在这里调用模型修复
├─ 复制 initial_registry                隔离调用者已有数据
├─ _seed_state(...)                     运行前登记必要初始来源；明确传空状态就保持空
├─ _graph(...)                          建前驱、后继、入口与可到达块关系
├─ _generation_feedback(...)            检查本版不能支持的生成数据反馈
├─ 工作队列                              FIFO 或 LIFO，状态变化后重新处理相关块
│  ├─ join_states(...)                  按位置合并前驱候选集合
│  └─ TransferInterpreter.evaluate(...) 求值一条完整 IR
│     ├─ resolve(...)                   把 input/local/literal/alternatives 解析到 ID
│     ├─ execute(...)                   执行一个固定抽象操作
│     │  ├─ 调用 DataRegistry            复用已有身份或登记新结果／部分
│     │  └─ 构造 AtomicOpRecord         保存阶段值、边界和位置变化
│     └─ bind_outputs(...)              将 local／已有值登记到公开 result 位置
├─ PropagationRecords.put(...)          提交每条 IR 的最终整份记录
└─ 返回 PropagationResult               数据、记录、覆盖、诊断和统计
```

`initial_state=None` 才会自动准备相关读取来源。显式空 FlowState 是调用者提供的完整空状态，不会在读不到值时偷偷重建来源。`max_variants` 限制候选组合或部分顺序的枚举；超限返回资源限制，不宣称已经收敛。它不是循环执行次数。

普通未知 compute 仍会传播。缺少实际 result 候选则等待；该块未完成时不发布出口，也不跳过写入继续执行后面的读。最终仍未绑定，记录 incomplete。每次重新求值替换静态记录，不追加成一长串运行日志。

**10．阶段产物与运行引用**

```text
PropagationResult（内存）
├─ status / coverage / diagnostics
├─ registry / records                  最终 Data 与逐 IR 记录
├─ stats                               技术统计，不是真实执行次数
└─ initial_data / initial_state        求解使用的初始描述版本

传播目录
├─ data.json                           Data[]，每份最终内容一份
├─ records.json                        IR ID → IRFlowRecord，保留原操作/候选/条件
├─ sinks.json                          实际边界坐标及类型/等级，不复制载荷
├─ manifest.json                       上游地址与身份、状态、覆盖、诊断、文件摘要
├─ audit/
│  ├─ requested-data.json / requested-state.json
│  ├─ initial-data.json / initial-state.json
│  ├─ data-identities.json
│  └─ stats.json
├─ report.md / report.html
└─ replay/summary.json                 重算比较，不保存另一份最终 Data
```

上游 `manifest.upstream={path,manifest_sha256}` 引用真正的联合标注运行；source、CFG、runtime_contract、原响应及编译映射不再复制。没有 `doe-input.json` 替代总包。共享材料由严格加载器按显式地址取得，丢失或篡改时拒绝，不从同名目录猜测。

**11．公开调用顺序**

```text
联合标注与审查
├─ prepare_material(source, cfg, user_request=None)
│  └─ 冻结 source/cfg/runtime_contract/user_request；不生成持久地址表
├─ annotate_skill(..., client)
│  └─ raw Task/demands/expressions/IR语义 → 校验 → 编译观察、需求与sink
├─ to_payload(response)                task/demands/expressions/ir_semantics/locations/sinks
├─ review_annotation / refine_annotation
│  └─ 旁置初审，按需一次语义修复及独立复审；机械结构纠正不设次数上限
└─ load_annotation_run                 完整请求链、候选、编译、材料身份核验

传播与下游
├─ propagate(cfg, annotation, initial_registry=None, initial_state=None, ...)
│  └─ 同一正向传递与工作队列；不执行真实工具或代码
├─ run_propagation(annotation_run, run_dir=...)
│  └─ 只保存本阶段 Data、records、sinks 和必要审计
├─ load_propagation_materials(run_dir) → PropagationMaterials
│  └─ 校验事实与上游；内存组件，不提供总包JSON序列化
├─ replay_propagation(run_dir)          零 API 重新求解并比较
└─ run_doe(propagation_run, run_dir=...)
   └─ 对应标注的 Task/需求/敏感性 → 确定性需求及暴露对照
```

`PropagationRecords.records_dict()` 返回隔离的记录映射。`from_records(..., cfg, annotation, data_registry, initial_data, initial_state)` 显式接收对应材料并严格检查；旧摘要封套及隐式恢复入口已删除。调用记录保留原始响应，受限 JSON 修整另存回执，不能改写原响应冒充模型直接生成。

`DataRegistry` 继续提供 register_source、register_part、create_result、get、refine、resolve_part、validate、to_dict/to_json 和 from_dict/from_json。描述细化沿用旧 ID，内容处理创建新 ID；敏感性依据仅留在 Data.annotations.evidences。完整 Data 契约见 [Data 规范](SkillFlow-Data数据结构与更新规则.md)。

`PropagationRecords` 提供 put/get/validate、effect_order_known、records_dict() 与 from_records(...)。records_dict() 只导出 IR 到记录的映射；from_records(...) 要求显式提供对应 CFG、编译标注及 DataRegistry 等材料。材料身份由运行清单验证，记录不再内嵌材料或摘要封套。effect_order_known 只检查 order 是否为 fixed，不证明真实执行顺序。

原先没有实际调用的 intermediate_key、symbolic_endpoint 与对应私有辅助已移除；身份统一由实际求值位置和 DataRegistry 接口产生。旧 propagation_record_demo.py 入口已删除，主示例 `--records-only` 保留只查看记录的用途，不再维护第二个程序入口。

**12．怎样看结果**

1. 先看传播 manifest 的 status、coverage、diagnostics，以及 records.json 每条记录的 order/precedence；传播完成不等于语义已证明。
2. 在 HTML 中按 IR 查看原输入输出、执行主体、按数组顺序保留的效果与实际 Data 候选。
3. 点击 D 短名核对 content、origin、排除和字段覆盖关系；Data 依赖不自动等同于明文包含。
4. 需要追查字段路径、local 名称或判断依据时，展开原标注审计；程序按记录位置读取原规格，不复制第二套参数。
5. 源文和 CFG 由上游冻结材料唯一保存，Data、操作记录与 sink 清单由传播阶段保存；加载器沿清单引用重建关联，审查页面不要求手工拼接。复现、引文审计和成本统计使用对应阶段的 audit 与调用记录。

报告里的 D001 等仅为显示别名，实际 Data ID 不改写。传递步骤在 JSON 中用数组次序表达，报告的 1.1、1.2 是位置标签，不是再次储存的 op_index。输出数组的第 0 项是该抽象操作产生的第一个值，不保证对应 IR.outputs[0]；公开输出联系仍由原规格 output_bindings 解释，并体现在出口 result 位置。

当前实现提供静态候选关系和顺序记录；没有证明模型解释正确，也没有将这些记录视为 DOE 裁决结果。

当前可选参数以[Sink 标注收紧与可选参数规范](SkillFlow-Sink标注收紧与可选参数.md)为准。when 属于操作消费条件，不修改 Data，也不成为任意路径条件语言。


联合标注自身也按所有权保存：原始 package＋snapshot 冻结源文件，cfg/runtime-contract/user-request 分片各保存一次，内存 material 不另落盘。annotation/result.json 仅为状态、验证、计数、请求链及编译证书；六项业务事实只在 audit/compiled-response.json 中。加载器验证后重建业务结果，单独的 ir-semantics/locations/sink-boundaries 导出已删除。审查与修复通过显式上游引用读取这些事实，只保存本阶段拥有的显式候选、定位、观察、实际请求及结论；修复 context 根据已有所有者和初审重建并检查清单摘要，不再落盘复制。
