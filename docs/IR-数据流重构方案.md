> 本文为历史方案。当前阶段边界与命名以 [IR-命名与CFG完整性校验方案](IR-命名与CFG完整性校验方案.md) 为准；整图可用性和暴露候选不再属于第一遍编译。

# IR 数据流重构方案

状态：待定稿。本文只描述设计与改动范围，尚未动任何代码。

## 0. 一句话

把跨块数据引用从「共享上下文键 + 逐块原样转交」改成「SSA 值引用 + 可达/支配判定」。
每块的可用集照旧存在、照旧显式，但由规则算出而非由 LLM 声明。

## 1. 现状机制

LLM 在候选里给出块、边、guard，以及每块的 `context_exports`（键 → 本块 SSA 输出）
和 `context_passthrough`（收到并原样转交的键）。
`derived_context_contract`（[basic_block_ir.py:230-253](../packages/skill-ir/skill_ir/basic_block_ir.py#L230-L253)）
按下式推出契约：

```
requires = use_ctx[B]（扫 CONTEXT_REF 输入得到）  ∪  passthrough[B]
provides = exports[B]                            ∪  passthrough[B]
```

`_global_dataflow_errors`（[cfg.py:218-243](../packages/skill-ir/skill_ir/cfg.py#L218-L243)）
再要求：每个 required key 必须被**所有**直接前驱 `provides`，往上游找到生产者明确不算数。

这里有个容易记错的事实：`context_requires` / `context_provides` **本来就是规则填的**,
候选层没有这两个字段。编译期走的是「不在 `model_fields_set` 就直接赋推导值」那一支
（[basic_block_ir.py:214-228](../packages/skill-ir/skill_ir/basic_block_ir.py#L214-L228)），
不存在任何比对；比对只在反序列化既有 CFG 时触发。
所以要改的不是这两个字段，而是流进它们的 `passthrough` 那一项，以及产生它的那层键索引。

## 2. 三个问题

**失败方向是反的。** 漏一条 passthrough，若下游也没人消费它（LLM 通常整条流一起漏，
不会只漏中间一跳），校验零报错、`complete` 照发。这是静默召回损失，
而规则在「丢弃」方向本该高精度。三份真实产物印证了这个形态：
echo 3 块 0 条 passthrough、alert 4 块 1 条、simple_skill 8 块 1 条；
simple_skill 每块恰好只提供下一块要的那一个键，`user_request` 在 block_002 之后
从图上消失，而运行时它显然还在。block_004 那次外部调用带不带出去，
正是暴露面要问的问题，IR 里已经没有它了。

**记账量是乘出来的。** 义务规模 O(块 × 活跃键)，且块自己不碰这个值也得写。
错误非局部：block_017 少写一条，报错点落在 block_025。
叠加 [analyze.py:113-130](../packages/skill-ir/skill_ir/analyze.py#L113-L130)
修复提示的全量重拼（原 prompt + 上次响应 + 上次候选 + 诊断），三轮 token 平方增长，
每轮 LLM 重排一遍全局记账，修 A 碰坏 B。

**语义 gate 覆盖不到它。** 回译校验对整篇相似度灵敏，对单条细粒度记账缺失近乎零灵敏：
200 条里漏 1 条，回译文本几乎不变，阈值不动，放行。反过来若真把它回译成句子
（「第 9 步把 x 交给第 10 步」），原文里没有对应物，只会拉低相似度——
等于往把关的度量里灌噪声。

更硬的证据在 IR 内部：`context_exports` 的每个值必须绑定本块已定义的 SSA 输出，
写错当场报 `CONTEXT_EXPORT_NOT_DEFINED`；`context_passthrough` 是裸字符串列表，
块内没有任何指令读它、没有任何 SSA 名指向它。**它没有 referent**，
所以既无从校验，也回译不出来。

## 3. 划分判据

> 一个字段该问 LLM，当且仅当它有原文对应物、能被回译成句子、因此能被语义 gate 覆盖。
> 否则该由规则算。

于是字段分三类：

- **LLM 产、gate 覆盖**：块切分、`block_name`、指令与 opcode、边与 guard、
  `source_kind`、块局部 use/def。这些在 Skill 原文里都有对应句子——
  「接着执行」「如果……否则」「调用天气 API」——错了能指着那句话说错在哪。
- **规则算、由构造保证**：稳定 id、SSA 重命名、前驱后继、roots、可达性、可用集。
  这类不需要 gate，确定性且可重放。
- **两者都不覆盖**：LLM 产、gate 看不见、构造也不保证。目前只有
  `context_passthrough` 落在这里，而它恰好是体量最大、随活跃键数乘出来的那一项。

第三类是唯一的真洞。把它搬到第二类，洞闭合，同时剩下的每条 LLM 断言都被回译覆盖。
这也顺手定了 kill 的归属：覆盖赋值（同名值被重定义）规则自己看得出来，不必问；
「作用域结束 / 明确丢弃」在原文里几乎没有对应句子，回译不出来、gate 覆盖不了，
那就不问，默认存活。漏 kill 的后果是多带一个值多判一次，方向是保守的。

## 4. 目标机制：SSA 值引用取代键索引

差别在 referent：

- `context_ref: "city"` 引的是**共享命名空间里的一个名字**。名字要跨块可见，
  就得有人一路端着——`passthrough` 不是设计失误，是键索引的必然推论。
- `local_dep: value_001` 引的是**定义点本身**。中间块不需要参与，
  可用性变成一句图上查询：`def(value_001)` 是否支配这个 use。
  删掉 passthrough 不留窟窿，因为从来不靠它建立引用。

代码其实已经站在这一步上。[compiler.py:116](../packages/skill-ir/skill_ir/compiler.py#L116)
的 `next_value_number` 在块循环外初始化、183-184 行在块内递增，`value_00N` 已经是
全 CFG 唯一；而 [compiler.py:121](../packages/skill-ir/skill_ir/compiler.py#L121)
的 `local_values` 每块重置，所以 144-157 行跨块引用报 `LOCAL_DEP_NOT_DEFINED`。
**名字空间已经是全局的，只有解析作用域是块局部的。**
这个改动是把解析域放宽到与名字空间一致，不是引入新概念。

比 passthrough 更重要的收获是可变槽消失。现在 prompt 教的是「要更新 x，
就读 `context_ref:x`、算个新本地值、把 x 导出到它」，于是 block_005 的 `x`
和 block_012 的 `x` 是两份不同的数据共用一个名字，各自来源与沿途处理都不同。
审计要追的恰恰是数据的同一性，键索引把它抹掉了：看到 block_017 读 `x`，
无法确定读的是哪一份、被重写过几次。SSA 里 `value_047 = normalize(value_001)`
把派生关系写在指令里，来源无歧义，「更新」自然成为一次显式派生事件——
那正是审计要的 per-hop 事实。所以这一刀同时解决表示问题和审计信息量问题。

## 5. 合流处：不强求 phi

`value_012`（then 分支产）和 `value_031`（else 分支产）语义上是「同一个槽」，
SSA 里是两个值。键索引在这一点上确实提供了一个「不管从哪条路来」的名字。
但对我们的目的倾向**不统一**：两份数据来源不同、沿途处理不同，审计本来就该分开跟。

所以合流处的判定改成：

- use 引的 def **支配**它 → must，正常；
- 只在某条入边上可达 → **may，标记但不拒收**；
- 要表达「两者之一」→ 指令列多个输入，IR 本来就允许多输入，语义天然是 may。

注意这里极性反了一次：现行「所有直接前驱都得 provide」在合流处只有一条路带这个值时
是**报错**。LLM 为了不报错，最省事的做法就是别 require——流就这么没了。
对召回敏感的分析，这条规则的方向是错的，应当保守地当「可能有」。

phi 若需要，由传播那一遍在报告层合成，不进抽取契约。

## 6. 传播那一遍

两个方程，遍历 CFG 求解：

```
avail_in[B]  = ∪_{P ∈ pred(B)} avail_out[P]
avail_out[B] = (avail_in[B] \ kill[B]) ∪ def[B]
roots 初值    = ∅（加上 initial_context_keys 引入的值）
```

集合本身即去重，收敛靠单调增长 + 值域有限。直线图一趟走完。
环上才真正需要迭代：回边 B→A 时 `avail_in[A]` 依赖 `avail_out[B]`，后者又依赖前者，
从 ∅ 起迭代到不变即停。这里顺带解决现行的一处硬伤——回边也是直接前驱，
按「所有前驱都得 provide」，循环携带的值等于要求 LLM 手写这个递归方程的自洽解。
不是难，是不该问它。

**`avail` 与 `live` 是反方向的两个分析，别混。** 暴露面要 `avail`（值此刻在场），
不要 `live`（值以后还会被用）——一个值就算再没人用，它在场就可能被带出去。
两个都算，用途分开。

产物：

- 每块 `avail_in` / `avail_out`：你要的「每点转发信息」一条不少，只是来源变了。
  `passthrough[B] = avail_in[B] \ (B 重定义的值 ∪ kill[B])`，仍可作为输出字段保留。
- 每个 egress 指令点 × `avail_in` = **暴露候选集**，审计层的直接输入。
- 支配边界 → must/may 标注。

### 审计单元的去重（上一层）

审计层传播的不是单个 value_id，而是带路径事实的记录
`(value_id, origin, 沿途变换事件, 减量, …)`。路径数随分支指数增长、遇环无界，
所以必须投影到一个**有界去重键**：两条路径若在键上一致，下游判定结果相同，留一条即可。
键有界 → 每节点记录集有界 → 带环也终止。

这与 §6 开头那层是两个不同的收敛论证：可用集靠有限格 + 单调；
流记录靠投影到有界键。别把后者的说法套到前者，那里不需要。

审计单元由这一遍统一产出——一次遍历全图覆盖，每个 (值, 节点) 对都有着落；
逐块声明只在 LLM 恰好写了的地方有，覆盖率不可控。

## 7. 改动清单

### 7.1 操作数层（[basic_block_ir.py](../packages/skill-ir/skill_ir/basic_block_ir.py)）

- `OperandType.LOCAL_DEP` → `VALUE_REF`。它不再 local，名字里编码的不变量
  正是要放弃的那条。`OUTPUT_NOT_LOCAL_DEP` / `LOCAL_DEP_NOT_DEFINED`
  等诊断码随之更名。
- `Operand` 新增 `llm_name: str | None`，保留 LLM 原始值名。
  现在 `_copy_operand(operand, name=canonical_name)` 把它丢了；
  指令有 `llm_ref`（[compiler.py:196](../packages/skill-ir/skill_ir/compiler.py#L196)）
  留着，操作数没有。**回译 gate 要靠这些名字造句子，`value_047` 造不出来**，
  所以这条是 gate 的前置依赖，不是附赠。
- `CONTEXT_REF` 保留枚举值但不再用于跨块引用（见 7.5）。

### 7.2 块层

- 删 `context_passthrough` 字段与其 validator。
- `derived_context_contract()`：删掉 `requires.extend(self.context_passthrough)`
  与 provides 里的 passthrough 项。requires 退化为纯 `use_ctx[B]`，
  正好是数据流方程里的 `use[B]`。
- `_dataflow_errors()` 中「SSA 定义先于使用」的作用域从块内放宽到支配判据，
  实际实现移到 CFG 层（块层看不到图）。
- 源块形状检查（恰好一条获取指令 + 终结符）、`read_context` 只许在 context 源、
  `http_get`/`read_db` 只许在 external 源，**全部保留**。

### 7.3 CFG 层（[cfg.py](../packages/skill-ir/skill_ir/cfg.py)）

- `_global_dataflow_errors` 里「所有直接前驱都得 provide」整段删除，
  换成调用传播结果做支配/可达判定（§5）。
- 「根块不能 require 未引入的值」「回边不能替首次进入供值」
  （[cfg.py:191-206](../packages/skill-ir/skill_ir/cfg.py#L191-L206)）不丢，
  变成不动点初值为 ∅——同一件事从声明比对改由算法保证，且不再需要 LLM 配合就成立。
- 结构检查全部保留：entry 存在、blocks 键与 `block_id` 一致、重复边、
  RETURN 无出边、DISPATCH 有出边、分支 dispatch 必须把条件依赖写进 `inputs`
  （[cfg.py:158-166](../packages/skill-ir/skill_ir/cfg.py#L158-L166)）、
  无根环不可达拒收。

### 7.4 新增 `propagate.py`

`avail_in`/`avail_out` 不动点、回边识别（DFS 树 back edge）、支配关系与支配边界、
must/may 标注、egress × avail 的暴露候选集。纯函数，输入 `ControlFlowGraph`，
无 LLM 依赖，可单测到逐位。

### 7.5 候选层与 prompt

- `CandidateBlock` 删 `context_passthrough`。
- 候选层值名要求**全图唯一**（现在两个块可以都叫 `result`，因为 `local_values`
  每块重置）。先例已有：`instruction_ref` 就是全局唯一，
  编译器报 `DUPLICATE_INSTRUCTION_REF`
  （[compiler.py:126-135](../packages/skill-ir/skill_ir/compiler.py#L126-L135)）。
- [prompt.py](../packages/skill-ir/skill_ir/prompt.py) 删整段
  FORWARDING EXISTING CONTEXT（76-92 行，含 A→B→C 那个例子），
  改为教「跨块引用直接写产出该值的那个值名」。
  这段是 prompt 里最长最绕的一节，删掉对块切分与连边质量应是净收益
  （这是假设，需 §9 A/B 验证）。
- 两个 `_EXAMPLES` 候选 JSON 同步改写。它们作为数据保存、测试会去编译，
  所以必须与新契约一致。

### 7.6 `context_exports` 的去留

若每个上下文条目都由源块 `read_context` 引入（现行显式源块契约已如此要求，
且其产出就是 SSA 输出），则**每份数据都有 def 点**，`CONTEXT_REF` 跨块用途归零，
`context_exports` / `context_requires` / `context_provides` 整层可一并塌掉，
[basic_block_ir.py:240-245](../packages/skill-ir/skill_ir/basic_block_ir.py#L240-L245)
跳过 position-0 的特例也不必留。

一个值得考虑的保留理由：`context_exports` 不作绑定机制、只作**标签**
（给值挂个可读名字），纯粹服务回译。这与 7.1 的 `llm_name` 是同一件事的两种做法，
**二选一**，建议选 `llm_name`——它覆盖所有值，而 exports 只覆盖被导出的那些。

## 8. 语义回溯 gate 的三个坑

这一节不属于本次改动范围，但设计相互依赖，记录在此。

1. **回译器必须看不到原文。** 否则它从原文重建措辞而非从 CFG 重建，
   相似度自证，度量失效。
2. **要双向。** 原文→CFG 的覆盖（漏抽）与 CFG→原文的落地（凭空造）
   是两类不同错误，单向相似度只抓一个。
3. **gate 对控制流敏感、对数据流弱。** 原文多是动作描述，
   很少有「把城市名传给天气 API」这种显式转交句。
   gate 最弱的地方正是审计最需要精度的地方——这本身就是把数据流可用性
   交给规则的独立理由。

另：阈值以上放行意味着以下拒收，误拒可见（有人看），误放行静默。
阈值定在哪取决于更怕哪一个。

新增一条现在没有、改动后才可能的检查：**每个 use 必须追到一个真实源**，
堵住 LLM 凭空造值。这比现行的记账自洽检查有价值。

## 9. 验证

- 三份真实产物（echo / alert / simple_skill）改造后重跑，人工核对
  `avail_out` 是否符合直觉。simple_skill 的判据很明确：
  `user_request` 必须在 block_004 的 `avail_in` 里出现。
- 115 项包内测试全绿；新增 propagate.py 的单测（直线、分支合流、环、多重环）。
- prompt A/B：同一批 skill 在删 FORWARDING 前后对比块数、边数、attempts、
  诊断数，验证 §7.5 那个「净收益」假设。
- 顺带修一个已观察到的产物瑕疵：simple_skill block_005 的 dispatch
  带了个 `('literal', None)` 输入。

## 10. 不做什么

- 不为 SFG / DOE 的现有格式做任何迁就，它们要重写。
- 不引入规则推导的边。跳转关系只能靠理解拿；若日后要加，只该往**加边**方向加
  （加边是过近似，最坏让下游多判几次；不加是漏，直接丢暴露面）。
  现在一条都不补，先保持。
- 不问 LLM 要 kill（§3）。
- 不在抽取契约里要求 phi（§5）。
