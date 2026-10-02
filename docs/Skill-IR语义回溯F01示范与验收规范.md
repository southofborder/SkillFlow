# Skill-IR 语义回溯：F01 示范与验收规范

> 历史 v1 规格。以下记录旧实验设计，已由[受控语义回述与源文核对规范 v2](Skill-IR受控语义回述与源文核对规范.md)取代，不是当前执行说明。旧输入、响应和报告保留；按用户选择，旧运行与重放代码删除，当前入口不支持这些历史记录。

本轮建立一个可离线准备、可分别审阅两种回述的 F01 示范，并在离线检查通过后进行首次固定配置实测。目标是核对源文要求、IR 显式内容和实际回述之间的关系，验证错误能否被定位，不以结构通过、回述流畅或整体相似度代替语义核对。本轮不新增 Lean 证明，不执行 Skill，也不重新提取原图。

## 1. 固定输入与材料范围

基线固定为 `packages/skill-ir/formal/fixtures/review30.json` 中编号 **013 / F01 / 第 1 轮**。图只读取该条目指定的原始 `analysis.json["cfg"]`，先核对整个 analysis 文件的 SHA-256。源文固定为 `packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/F01/` 下的原始文件，并逐文件核对摘要和清单。不得用 render-input、model_dump 中间材料或人工修过的图代替原输入。

本轮新增材料位于 `packages/skill-ir/experiments/semantic_backtrace/`。manifest 只记录仓库相对路径和来源摘要；oracle 只供评测读取；人工回述示例明确标识为规格示例。旧 frozen、原 analysis、已有标注和已有实验结果均不修改。

文件摘要对原始字节计算。图和其他 JSON 对象的摘要统一为：先以 UTF-8 编码 `json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)`，再计算 SHA-256。字典键排序，列表次序和重复项保留。源包摘要对按 `path` 排序的 `[{"path": ..., "sha256": ...}]` 使用同一 JSON 算法计算；文件 `content` 保留 UTF-8 解码后的原始换行，不先改写再计算文件摘要。

## 2. 两个核对方向与两种回述

`source_to_graph` 核对源文要求是否进入图，包括来源绑定、条件、返回值、作用域、禁止事项和附加行为。`graph_to_text` 核对实际交付的回述是否准确表达图中记录的内容。一个图可以不符合源文，而它的回述仍然忠实；这时前者应发现问题，后者不能因为图有问题就自动判回述错误。

结构化回述由确定性程序遍历实际字段生成，保留入口、块内次序、operand 类别、定义与使用绑定、边条件、三级约束及内嵌内容。叙事回述由模型只根据同一图证据生成。两种回述都附可解析的 graph_refs，不把只有摘要或隐藏 JSON 的文件称为可审阅回述。开放 opcode、自然语言条件和约束文字是证据内容；不通过内置 F01 专用解释器将它们提升为已执行的事实。

源要求提取器只看源文。回述器只看图及其保留内容，不看源 Skill、人工要求、oracle、变体名或错误答案。源到图核对器看源文、独立提取的要求和图；图到文本核对器只看图与待审阅的实际文本。oracle 及人工示例不得进入上述模型 payload，case_id 和 oracle_key 也不应混入图内容。

## 3. 四组人工源要求

人工 gold 的分组用于验收，不是模型必须复用的需求编号。模型可将要求拆成更多条；匹配需根据源文位置和内容判断，不按两个系统各自产生的 ID 求交集。

| 组 | 必须保留的要求 | 源证据 |
| --- | --- | --- |
| 输入、优先工具与重试 | 从请求读 source_id，从环境读 FAST_KEY；有 key 才优先 fast.fetch，输入二者；无 key 直接 archive；仅首次暂时性失败可重试一次；首次非暂时性失败不得重试，也不得出现第三次 fast 尝试 | SKILL.md 8–10 行 |
| 回退、参数与返回 | 无 key、首次非暂时性失败或重试失败进入 archive；archive 最多一次，仅传 source_id；首次 fast、重试 fast 和 archive 各自成功时，返回各自同一成功响应的 body，保持不变并停止后续 fetch；archive 失败时返回其自身错误，不重试 | SKILL.md 9、11–14 行 |
| 凭据禁止传播 | 全流程不得将 FAST_KEY 传给 archive 或诊断输出；不仅检查局部调用，还保留全图作用域；声明禁令不等于证明开放操作内部绝无外泄 | SKILL.md 15 行 |
| 所有终态追加 | 首次 fast 成功、重试成功、archive 成功及 archive 失败，都应在对应 return 前向本地 status.txt 追加最终状态；源文没有要求状态必须是完整响应对象，success/failure 字符串可作为状态表示 | SKILL.md 16 行 |

完整 statement、分解条款和逐字引用保存在新 `f01/oracle.json`。不得因控制流已覆盖，就省掉同一次响应的返回绑定、archive 的唯一参数、禁止诊断输出或失败终态追加等要求。

下表固定基线原图中的审阅证据和允许的解释边界。这里的块号是该原件的证据位置，不是实现中的 F01 专用检测规则；模型生成的结论仍应引用它实际审阅的内容。

| 组 | 原图证据位置 | 允许的等价表达与人工解释边界 |
| --- | --- | --- |
| 输入、优先工具与重试 | `/blocks/block_001/instructions/0`、`/blocks/block_002/instructions/0` 的获取；`/blocks/block_004/instructions/0` 与 `/blocks/block_008/instructions/0` 的 fast 输入；`/blocks/block_007/instructions/0` 的失败类型检查；`/edges/2`、`/edges/3`、`/edges/7`、`/edges/8`、`/edges/10`、`/edges/11` 的分支 | 首次尝试与重试可拆节点，也可用明确有界重试表达；不能增加第三次尝试。请求/环境来源可由图中操作文字说明，但不将其当作外部环境已核实。presence 与 transient 的具体实现保留未知。 |
| 回退、参数与返回 | `/blocks/block_011/instructions/0/inputs` 的 archive 参数；`/blocks/block_006/instructions/1/inputs/0`、`/blocks/block_010/instructions/1/inputs/0`、`/blocks/block_013/instructions/1/inputs/0`、`/blocks/block_014/instructions/1/inputs/0` 的四类返回绑定；`/edges` 的回退与终态连接 | 不同回退原因可共用一次 archive 调用；不能把工具资源 operand 本身误当业务参数，也不能只凭相似 semantic_name 判断返回来源。同一 result 的直接返回是显式绑定证据，不能顺带证明开放操作内部未修改数据。 |
| 凭据禁止传播 | `/constraints/0` 的全图禁令；`/blocks/block_002/instructions/0/outputs/0` 的 FAST_KEY 定义；`/blocks/block_011/instructions/0/inputs` 的 archive 实际输入 | 凭据可以经不同合法结构 ID 重命名，核对仍沿定义与引用进行。未列出诊断动作不构成必须补一个动作的理由，也不证明黑盒内绝无诊断外发；禁令与实参冲突应分别列证据。 |
| 所有终态追加 | `/constraints/1`；`/blocks/block_006/instructions/0`、`/blocks/block_010/instructions/0`、`/blocks/block_013/instructions/0`、`/blocks/block_014/instructions/0` 的四处 status.txt 追加，以及其后的 return | 可以在每条终态分支追加，也可共用一个保持路径和状态依赖的出口；success/failure literal 状态串可接受。标题和约束不能替代缺失指令，追加动作的存在也不保证文件 IO 成功。 |

## 4. 五个保持结构有效的案例

| case_id | 输入差异 | 源到图需关注的问题 |
| --- | --- | --- |
| c01 | 原始基线，无修改 | 已记录的控制路径、绑定和动作；同时保留未决边界 |
| c02 | archive 输入增加读取 FAST_KEY 所产生的 result | 明确参数绑定违反仅 source_id 的要求，并与保留的全图禁令冲突 |
| c03 | 删除 archive 失败终态中的 status.txt 追加指令；保留原块标题和全图约束 | 不能把标题中的“Append”或全图要求当成实际仍存在的指令 |
| c04 | 重试成功 return 改读首次 fast 的 body，operand 标识和 semantic_name 同步指向首次定义，标题也如实更新 | 结果有定义且路径可达，仍不等于来自本次成功响应 |
| c05 | 在首次失败类型检查之后、dispatch 之前增加 wait_for_seconds，literal 为 2，指令约束明确为 `Wait for 2 seconds before continuing.` | 新增了源文没有要求的延迟；判断由实际操作、literal 和明确约束共同支持 |

每个案例从基线深拷贝，按资源、操作及数据定义关系定位修改位置。构造器不把错误类型写入 metadata，不以固定节点 ID 充当语义判定器；新指令 ID 必须唯一。全部五图都须通过现有 `ControlFlowGraph` 构造和 `validate_integrity()`。这组案例专门说明结构有效与语义忠实是不同问题。

## 5. 记录契约与未决边界

finding 的 status 统一为 `represented`、`omitted`、`mistranslated`、`unsupported_addition`、`internal_conflict` 或 `unknown`。每条结论保留说明、证据 basis、graph_refs，并按核对方向附 source_refs 或实际 text_refs。`unknown` 必须说明缺失什么依据。引用成功解析只证明位置存在，不证明结论正确。

基线至少保留下列边界：全局禁令和列出的输入不能证明开放 opcode 内部没有诊断外发；追加指令不能证明文件可写或 IO 实际成功；条件文字不能证明 FAST_KEY presence 或 transient 分类的具体实现；图中的返回绑定不等于黑盒操作实现已被验证。上述未决事项不能当作模型漏检，也不能靠叙事文字消除。

oracle 对四个变体记录期望问题和可接受的状态差异，例如 c02 可合理报告为 `mistranslated` 或 `internal_conflict`。图到文本的结论必须等实际文本产生后再判：忠实叙述错误参数是正确回述；把残留标题提升为实际追加动作才是回述错误。不得事先给尚不存在的叙事结果标注“通过”。

## 6. 默认调用与验收流程

默认完整运行预算固定为 **21 次逻辑模型调用**：一次独立源要求提取；五个案例各一次叙事回述、一次源到图核对、一次结构化回述的图到文本核对、一次叙事回述的图到文本核对。结构化回述和离线证据构建不调用模型。用户已授权首次实测使用官方 DeepSeek 接口、`deepseek-v4-flash`、`max` 推理配置；离线检查通过后由真实运行入口执行该固定实验。实现与离线单元测试不消耗这 21 次调用；底层受限连接重试与逻辑任务数分别记录，已接受响应不能自动重发冒充首次结果。

验收顺序如下：

1. 核对 manifest、源文件清单、原 analysis 摘要，准备五图并验证结构有效。
2. 检查模型输入隔离，特别是回述器不能看到源文，任何模型都不能看到 oracle。
3. 保存两种实际回述、模型原始响应、解析状态和两方向核对结果，分别记录失败、未完成或 unknown。
4. 用 oracle 的状态和实际证据位置筛选“可能检测到预期问题”的候选，再由人复核解释是否真正识别目标问题。自动命中不是语义正确率。
5. 检查完整四组源要求是否覆盖、四个错误是否可定位、c03 是否受残留标题误导，以及两种回述是否在相同图事实处产生不同理解。

不可将超时、坏 JSON、缺引用或中断算作成功，也不因重试后得到不同判断而隐藏先前输出。F01 及其变体是开发示范，不是独立留出集；这五例的结果不支持泛化准确率或模型优劣结论。这里的两个人工文本只是规格示例，不能伪装成模型运行结果。

## 7. 本轮证明承诺

本轮实施确定性遍历、引用检查、夹具、离线测试和首次 21 次逻辑调用的固定配置实测，并保存可重放的响应、评测和人工复核材料。实际完成情况以运行目录中的状态和结果为准，不能由规格文字预先认定。没有新增“回述语义正确”的 Lean 定理，也不把既有 `check(G) = true ↔ WF(G)` 扩展解释成源文或回述正确。

未来受控回述证明的目标固定为以下三项，作为后续工作的验收边界：

- **输入域：**通过现有完整结构校验且可以无损表示为 JSON 的 CFG。开放 opcode、条件、约束、metadata 及内嵌内容作为未解释的值保留，不在域定义中假定其行为正确，也不借 JSON 序列化修复非法内存对象。
- **显式事实集合：**至少包含入口、块内指令顺序、开放操作原文、类型化操作数及定义—使用绑定、带条件文字的有向边、图/块/指令三级约束，以及 opaque 字段的原始内容。事实表示需保留影响含义的位置、作用域和重复出现，不能只有节点 ID 或摘要。
- **保持命题：**拟证明 `parseControlled(printControlled(G))` 成功，并且解析后受控表达的 `facts` 与 `facts(G)` 相等。若作合法结构 ID 重命名，则按同一命名空间映射对齐定义和引用；若仅重排无语义意义的块/边存储次序，则按相应事实对应比较。不能把实际块内指令顺序、operand 位置、约束作用域或不同结果绑定当作可以丢弃的存储差异。打印器和解析器应针对实际展示的文本，解析不能读取原图或旁置答案来补全事实。

当前结构化输出尚不是一个已证明正确的受控 AST 打印器，叙事回述也没有获得这种定理。上述未来命题只覆盖 IR 到受控文本的显式事实保持；开放内容的行为解释，以及源 Skill 到 IR 的忠实性，需要独立前提与证据。只保存隐藏图 JSON 或证明节点 ID 对得上不足以完成该目标。
