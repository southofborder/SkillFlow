# SkillFlow 基础传播算法与 IR 传递规格


## 当前处理段与字段关系

当前联合标注先生成 `model/local/default` 处理段，再由程序编译观察、最终效果及对应依据。
原始标注、编译结果和位置映射分开保存并绑定摘要；恢复与离线重放重新编译核对。
`local` 需要源文／CFG 机制依据与明确的回传列表；`model` 需要执行主体包含 llm。
程序不因观察接收方是模型就自动增加执行主体。新规则见
[字段关系与观察编译](SkillFlow-字段关系与观察编译.md)。

新增 `filter_items`、`subset_view` 和单层 `for_each`。逐元素作用域保留 collection/element 及
其 body，接收者与正文只在同一实例中绑定。已有 `select_part` 继续表达精确字段原值，
`compute` 表达运算或不透明关系，两者不能因为方便而替换。处理段是标注形式；编译后的
规格保留唯一 events 顺序，数据记录不再复制第二份模式表。


本规范描述独立的第二阶段：完整 Skill 与选定 CFG 在同一次安全标注调用中产生
统一 IR 语义、位置声明与任务／需求／敏感性声明；随后程序离线解释规格，计算 Data、逐 IR
入口／出口状态和效果记录。传播过程中不调用 LLM，不执行 Skill、工具或嵌入代码，
不判断风险、必要性或 DOE，也不修改原图。

采用前向 may 数据流分析。`complete` 表示当前有限分析范围内完成求解，不表示
CFG 与源文已证明等价，也不表示模型标注或数据暴露判断已被证明正确。

所有 Skill 共用[统一抽象运行时契约](SkillFlow-统一抽象运行时契约.md)。范围与观察默认只在该契约定义，联合标注生成其下的可能关系；传播不补充执行假设，不将结果当作真实执行日志。

## 1. 一次标注与单一阶段顺序

当前 profile v24 的已编译业务 `AnnotationPayload` 严格包含：

```text
task_ref / realizations      冻结 Task 引用及其在当前图中的对应关系
demands / expressions        需求起点与结构化计算语义
ir_semantics[ir_id]         执行主体、依据、事件、输出绑定、敏感声明与顺序
locations[location_id]     kind、name、operand_refs、address_kind、address_reason、access_scope、retention
sink_boundaries[]          编译操作位置、目标、类型和固定边界暴露等级
processing_gaps[]          具体局部缺口；空表可省略
input_contracts[]          编译后的输出—输入必要性关系；空表可省略
```

原始模型响应使用处理段；程序校验后编译为直接事件并生成 sink 清单。完整响应还带 outcome 和独立 location_evidences；后者必须精确覆盖位置。通过 `to_payload` 显式投影业务字段，求解器不静默删除额外字段。

事件直接保存 effect、非空效果的 evidences 和有序 atomic_ops。重复标签就是不同阶段，不再维护第二份 effects 或 effect_index。原子操作次序、中间值和部分顺序因果保持。没有非空效果的 IR 必须提供 empty_effect_evidences；有非空效果时禁止该字段。执行主体证据独立保留，不因观察目标是模型而自动增加 llm。

`output_bindings` 只绑定每个真实公开输出，不能藏入计算或上下文写入。无标签事件 effect=null 支持 possible compute 或工具交付／获取，不能隐藏已知网络或写入。空效果的原样传递和普通 return 仍可能改变状态或保留任务结果。

## 2. 符号值、位置与原子操作

### 符号值引用

| `kind` | 字段 | 含义 |
| --- | --- | --- |
| `input` | `index` | 当前 IR 的实际输入位置 |
| `local` | `name` | 当前 IR 已声明的内部阶段值 |
| `literal` | `value` | 明确的 JSON 字面值，保留 null／空对象／空列表区别 |
| `alternatives` | `items` | 这些引用中的候选值并集，不是内容拼接 |

`input` 在当前 IR 的入口状态解析并固定，包括上下文操作数；段内写入不能改变同一个
输入符号所指的数据版本。需要读取写入后的当前位置时，必须显式使用 `read`。公开
输出通过 `output_bindings` 引用 `input` 时，同样绑定入口值；循环依赖检查沿用这一规则。

本地名称只在一条 IR 内有效。不存在的名称、非法输入位置、重复定义、循环定义和
确定顺序下的先用后定义均拒绝。部分顺序的候选引用可以包含后续局部值，但必须保留
已经可用的候选，不能靠引用约束将“部分顺序”偷换成“保护必定在前”。

`locations` 使用 `kind`、`name` 和必填的 `operand_refs` 表达运行时上下文、存储、模型上下文、
远端、工具或用户边界。`(kind, name)` 确定位置身份，外层 location_id 用于规格引用；名称不是数据内容。
`operand_refs` 是 `{instruction_id, side, index}` 列表，不重复、必须引用真实操作数，也可为空。
同一操作数可关联多个可能位置；没有公开操作数的隐式边界不伪造关联。operand_refs 关联实际操作数值，不能将来源父容器冒充其目标字段。
位置身份依据只保存于独立审计表，不放回业务位置。程序核验引用和引文，不通过工具名称猜测网络。
位置属性 access_scope/retention 用于程序生成 sink 类型及固定等级；不改变原传播状态中 `(kind,name)` 的身份，也不自动读取或交付数据。具体默认和纳入范围见[Sink 边界主规范](SkillFlow-Sink边界与固定分级.md)。
`address_kind` 默认是 `identified`：名字表示稳定来源身份，内容未知不扩大别名。
已知调用参数、异常载荷、调用结果及成员值保留各自真实来源和 occurrence。
只有地址关系确实未知时使用 `unidentified`，同时提供具体 `address_reason` 和物理源文依据；
这类位置与同 kind 的明确或不明确位置保守别名，写入只能弱更新。名字本身不承担别名语法，
`symbolic:` 前缀没有特殊传播含义；旧前缀声明在新协议下必须明确填写地址策略。
程序验证类型、引用和证据位置；源文审查仍须判断该未知地址理由是否成立。

路径用字符串字段和整数下标的列表表达，`["0"]` 与 `[0]` 不相同。路径选择必须是
明确操作；发现一个字段或依赖中提到某字段，不自动缩小整体。

### 原子操作

| `op` | 主要参数 | 数据语义 |
| --- | --- | --- |
| `read` | `location`、`output` | 读取当前位置的全部候选，原样保留 Data 身份 |
| `receive` | `location`、`inputs`、`output` | 取得外部内容；保留来源和请求可能依赖 |
| `deliver` | `inputs`、`target` | 记录发送、观察或用户输出涉及的实际数据与边界 |
| `write` | `target`、`mode`、可选 `input` | replace／append／delete，更新后续可读取状态 |
| `select_part` | `input`、`path`、`output` | 明确选取部分，解析或登记稳定部分／子视图 |
| `exclude_parts` | `input`、`paths`、`output` | 原整体排除指定路径，未知剩余仍保留 |
| `update_fields` | `input`、`updates`、`output` | 覆盖明确字段，其余原整体内容保留 |
| `build` | `container`、`parts`、`output` | 明确构造 object／list，不将候选并集当作组合 |
| `compute` | `inputs`、`dependencies`、`output` | 不解释开放函数，保存 derived／possible 依赖 |
| `filter_items` | `input`、`predicate`、`output` | 保留选中成员原身份；不执行自然语言谓词 |
| `merge` | `incoming`、`output` | 按实际前驱选择对应值，保持前驱配对 |
| `member` | `collection`、`output` | 保留源集合成员及 occurrence；对象不充当数组 |
| `branch` | `input`、类型化谓词与目标 | 保留条件和控制边关系，不执行自由文本条件 |
| `append` | `collection`、`item` 或 `items`、`output` | 保留原集合、加入内容及有序成员关系 |

这 14 个原子操作，加上 flat `call` 和 `processing`、`for_each`、`cases` 三种结构，
组成运行时契约的 18 行有限清单。清单还覆盖全部 14 个结构化需求表达式操作符。
每行说明输入输出类型、身份／别名、信息属性、副作用，并共享失败范围和源文依据义务；
实际字段、引用、数量和边界仍由类型模式校验。完整清单随契约提供，不为每条 IR 再调用模型。
覆盖有限支持词汇不等于穷尽任意 Skill 行为或外部工具语义；源文关系不在支持域内时必须保留具体缺口。

操作和输出绑定使用 file/start_line/end_line/reason、target/reason 或 rule_id/reason。原文由程序提取；CFG target 使用真实 IR／块身份及相对路径，规则使用 EM 编号，不再维护别名注册表。效果分类与原子关系的依据职责均保留，位置依据单独保存；字段成员仍是所属操作参数。
`read.location`、`receive.location` 仍表示业务位置，不是证据编号。
`compute.dependencies` 与输入逐项对应；
`possible` 不导致停止或请求人工判定，也不意味着整份输入明文保留在结果中。
本版不执行开放运算，即使存在运算名，也不会运行代码来“算出结果”。

`update_fields` 对应 Data v4 的 `field_updates(base, updates)`。同一次更新不能包含
相同或交叠路径；有先后的覆盖拆成多个 atomic_ops。字段覆盖与敏感数据“已安全”
没有等价关系。`build` 的完整性只描述明确构造的组成，不能拿已知字段枚举代替原整体。
完整组成不再要求 Data 内有非空证据字符串；默认仍不完整，显式构造或调用方明确声明才可设为完整，
之后不能普通细化出额外字段或重新打开为不完整。操作的真实引文仍在规格层核验。

`write(delete)` 没有内容 input，不虚构读取被删除的内容；append 使用旧内容和追加
参数生成新结果，不把候选 ID 集合并集当作拼接值。发送或观察不自动写入模型／远端
状态；后续确实需要读取的位置由明确的写入规则管理。

## 3. 来源、Data 身份与状态更新

未提供完整初始状态时，程序在求解前一次性为需要读取的外部上下文和存储登记 opaque
来源，仅包括规格实际 read/append 的位置及值引用使用的上下文入口。未使用的上下文操作数不额外造独立叶子种子；种子、值解析与循环依赖检查共用位置解析。已有描述只细化它们，不把整体裁成当前已知字段。显式提供的初始状态是完整且
权威的，包括没有绑定的位置；读不到 Data 时不能在传播过程中重新造来源。

网络或工具返回在对应 receive 求值时登记，因为它可能依赖当前请求候选。receive 在 remote 边界必须关联 net_receive；在 tool 边界使用无标签事件，不断言网络。获取来源 acquired_from 与请求 inputs/possible 依赖同时保留，纯函数仍使用 compute。缺失 CFG result 永远
不会自动变成外部 source。读取暂时缺失的结果会等待后续求值；最终仍无候选则保留
`unresolved_binding`，不会形成一次“零内容观察”的假成功。

每个处理结果按静态操作位置及有序的实际输入候选元组登记。同一个元组重算复用 ID，
新增候选产生相应新结果。不能在一个已有结果 ID 上追加或改写 origin.inputs；也不能
将迭代号加入身份。原样传递直接复用 ID，重复参数仍保留其输入位置和次序。

Data 不再复制传播依据：origin 和 dependencies 没有 evidence_refs，描述细化也不接收该参数。
`annotations.evidences` 只存后续 DOE 敏感性判断的依据；传播保留调用方已有的显式标注，
不生成敏感性标签或依据，也不把删除的 `spec:` 字符串搬进去。origin.inputs、依赖与内容关系
是传播计算结果，继续保留并接受来源身份与次序冲突检查。

多候选逐组合处理，OUT 保存结果候选集合。组合可能包含路径不相关的候选，本版不求解
自然语言条件，不承诺每个组合实际可执行。依赖关系与 content 关系分开：未知运算
使用 opaque 加 possible；排除和覆盖使用相应的内容视图，不能通过依赖边直接认定明文包含。

状态为“分类位置 → 可能 Data ID 集合”。不同前驱／成员关联保留为独立关系行，
不能按位置各自取并集而丢失配对；当前结果定义和明确位置的确定覆盖写采用替换／强更新。
未知地址或顺序不明时采用弱更新并保留旧候选。删除
只移除位置绑定，不删除 Data 或历史观察事件。

Data 描述细化保持 ID，但会推进 registry.revision。求解器据此重新检查受影响的已处理
节点，避免仅比较 Data ID 导致漏传播。纯新增结果不推进描述版本。用户给定的注册表
和状态均复制到新运行；原始输入不被求解改写。

## 4. 前向求解、部分顺序与循环边界

入口沿用 CFG 的声明入口和无前驱块。块按工作队列处理，块内按 IR 次序执行；前驱
OUT 改变时重新处理后继，描述版本改变时重新检查已处理节点。队列耗尽后保存每条 IR
的最终静态记录，而不是把每次求解迭代追加成实际执行日志。

`order=partial` 时，枚举满足编译规格 `precedence`、同一 event 内原子次序和局部值可用关系的有限安排，每个原子操作
在每种安排中只执行一次；合并各安排的候选、事件和状态。显式 input 引用始终代表原
操作数，不能因为另一个步骤删除过字段就被偷偷替换成处理后版本。多版本可能性需要
用候选引用表达。编译器保留处理段内部顺序、必要观察因果和局部定义使用关系；不同处理段的原子操作可交错，不能默认先保护后观察。

新协议在循环内使用有限的静态定义与关系摘要，支持显式逐项、重试、分页、累计及其
常见嵌套。普通 Data 身份仍不可变；循环内部事实表与最终封存的 `loop_summary` 区分，
不再通过递归输入身份为每轮分配新版本，也不按“存在生成反馈”全局拒绝 CFG。
processing 的 `merge` 按真实前驱选值，`member` 保留源 occurrence，`branch` 根据有类型的
实际条件对应控制边；自然语言条件不参与执行。累计集合保留初始内容与贡献关系，
未展开结构及未知重复明确保留精度限制。详见 [通用循环设计](../doe/general-loop-analysis.md)。

已知空成员范围可以排除循环体；保存层重新核验有类型分支和实际操作数后判断允许
到达的区域，不仅相信一个 not_reached 标签。新的循环摘要进入正反向需求、敏感性和
DOE 对照；计算完成不证明路径可行、次数精确或需求最小。

候选组合或部分顺序安排超过资源限制时返回 `resource_limit`，不截断后报告 complete。
语义不明的普通 compute 并非数据反馈循环，因此仍可保守传播。

| 状态 | 含义 |
| --- | --- |
| `complete` | 在当前分析域内求解完成；partial 保留可计算候选关系 |
| `incomplete` | 存在未绑定、源文建模缺口或局部操作失败；独立已处理记录继续保留 |
| `unsupported_feedback` | 历史协议保留的生成反馈拒绝状态；新有限循环域不以存在反馈全局拒绝 |
| `resource_limit` | 组合／安排超限，未冒充成功 |
| `execution_error` | 有明确全局错误诊断的失败结果；不能把任意程序／完整性错误自动降级为局部缺口 |

非法输入和无效规格在进入求解前明确报错。单条 IR 的 coverage 区分 `processed`、
`execution_error`、`blocked`、`unmodeled`、`unresolved_binding`、`not_solved`、
`not_reached` 和 `infeasible`。只有经过实际 CFG／类型化条件核验的 `infeasible` 才表示路径排除；
未执行或未形成记录不能据此删除输入。

支持的局部类型／数据域错误保留原错误、IR／事件／操作位置和实际输入 Data 身份。
失败 IR 的试探更新回滚，已观察的前缀操作另存为失败证据，不伪造成功输出；缺口随实际数据、
状态和控制依赖传播，独立工作继续。只有可证明的有限汇合点才能解除未知分支控制。
对象／集合保护不放宽，未知引用、内部不变量错误和资源限制也不按同一种局部错误吞掉。

## 5. 运行、业务交付与审查

```powershell
python -m skillflow.propagation run --annotation-run path/to/current-annotation-run --run-dir path/to/new-propagation
python -m skillflow.propagation run --annotation-run path/to/current-annotation-run --run-dir path/to/new-propagation --seed-data data.json --seed-state state.json
python -m skillflow.propagation replay --run-dir path/to/new-propagation
python examples/propagation/propagation_demo.py
python examples/propagation/propagation_demo.py --records-only
python examples/propagation/propagation_demo.py --output path/to/new-authored-demo
```

Python 使用 `propagate(cfg, to_payload(validated_response), initial_registry=..., initial_state=...)`。求解入口不导入在线客户端。`--seed-state` 是完整状态，不是自动种子的局部覆盖；其中 Data ID 必须来自配套注册表。只给 Data 快照时，不按 description 或内容名称猜测位置。

正式传播只保存 data.json、records.json、sinks.json，状态、覆盖、诊断及摘要位于 manifest。源文、CFG、位置、执行主体及联合声明由 manifest.upstream 引用本次标注运行，规则全文只在上游保存；不再交付总包或再次复制输入。

原子 records 的 inputs/outputs 仍是按参数顺序排列的 Data 候选集合。事件和操作位置、字段处理、前后版本、原样传递、强弱更新和保守候选没有改变。程序按对应编译规格校验位置、类型、参数数量、输出形状及 sink 清单，原始引用通过编译映射回查。

公开 load_propagation_materials 返回经过完整验证的内存材料。反向需求使用对应原始和编译规格，不从已删除的符号副本反猜。运行只在 audit 保存原始种子、有效初始种子、最终身份和技术统计；重放比较阶段文件，不保存第二份最终 Data。报告 MD／HTML 共用展示模型。

现行接口、目录、版本和完整性规则见[传播记录规范](SkillFlow-传播记录结构与更新规则.md)及[字段收紧规范](../architecture/field-tightening.md)。历史响应、旧报告和固定交付物不迁移，不重算身份冒充新运行。

## 6. 验收边界

离线测试覆盖动作阶段的前后版本、字段选择／排除／覆盖、未知计算、构造、追加和删除，
分支候选、强弱更新、稳定循环与反馈拒绝、队列调度独立性、摘要隔离、缺失值不造源、
资源限制以及零 API 重放。综合示例的规格由作者提供并校验真实引文，不能冒充模型实测。

实际标注实验另存原始响应和复核报告，分别报告工程检查、模型遗漏／误绑定及保守近似。
测试通过不证明模型生成的规格与源文语义等价，也不构成 DOE 结论。

历史记录（v4 标注／v2 Data／v2 记录，不能替代当前版本验收）：2026-09-24 首轮实施验收完整回归 1,745 项通过；001、010、013 共三次联合标注均取得
合法响应，其中 010 保留四项未决，三例传播及零 API 重放完成。助手复核仍发现入口范围、
字段身份、网络性质和模型观察范围的标注问题，详见
[三例实测复核报告](../../experiments/propagation/runs/pilot3-v1-20260924/assistant-review.md)。
这份报告保留实际错误，不把工程完成替换为标注准确性结论。

## 可选对象成员与共享请求

构造成员使用 BuildMember，字段为 path、value 和可选 when。when 是 Boolean ValueRef，true 加入原值，false 省略且不消费原值，抽象布尔保留可能形状。同一符号条件共用决定。条件仅支持对象字段，不扩展 Data 或任意谓词语言。候选组合超出现有 100,000 上限时明确失败。

同一 IR、作用域和边界上的 deliver／receive 要求完全相同的有序请求引用才能唯一配对；解释器复用交付绑定而不是重新取得另一版本。不同 IR 的关系仍由 CFG 数据依赖表示；不按 opcode 或最近位置猜测。已知零参数交付与无请求获取继续保留。见[可选参数规范](SkillFlow-Sink标注收紧与可选参数.md)。
