# Skill-IR 安全与传播联合标注规范（v9）

当前流程是：**完整 Skill + 选定 CFG + 统一契约 → 一次原始标注 → 程序编译观察与 sink 清单 → 离线传播**。本阶段不改 CFG，不执行 Skill，不判断风险、必要性或 DOE。模型标注动作标签、字段关系、处理模式及接收边界性质；程序产生观察记录、sink 类型和固定边界等级。原始响应与编译响应分开保存，不能把二者混同。

唯一运行时规则来自 [`runtime_contract.py`](../../src/skillflow/propagation/contracts/runtime_contract.py)，版本 `skillflow-abstract-runtime-v5`。中文解释见[统一抽象运行时契约](SkillFlow-统一抽象运行时契约.md)，处理结构和编译规则见[字段关系与观察编译](SkillFlow-字段关系与观察编译.md)。提示词正文英文，解释及失败理由中文；源文、代码与引文保留原语言。正式类型生成完整响应 JSON Schema。

## 1. 输入与四字段 profile

模型读取完整可读源文、实际完整 CFG、程序生成的源文／图索引和统一契约。二进制及未解释内容列为边界；代码仅作为文本。旧候选、人工答案、历史评审、实际传播 Data 和 DOE 判断不进入输入。

每条真实 IR，包括 dispatch 和 return，恰好一份 profile：

```text
profiles[ir_id]
├─ operator[]    参与动作的执行主体，去重；不是接收方，也不是 opcode
├─ roles[]       数据引入／到达边界／变换角色，去重
├─ effects[]     按发生阶段排列，可重复；原始与编译形式见下表
└─ evidences[]   标签及每次效果的引文、定位和理由
```

operator 允许 `llm、agent_runtime、tool、human`；roles 允许 `source、sink、transformer`。主体与角色的排列不表示执行顺序；工具名称单独保留在 IR 与证据中。模型接收内容不自动意味着它是原动作执行主体，编译器不会机械增加 llm 或 sink。

| 效果 | 含义 | 原始模型响应 |
|---|---|---|
| context_read | 取得运行时、环境、调用者内容 | 可标注 |
| context_write | 改变后续动作能读取的共享上下文内容／绑定 | 可标注 |
| fs_read | 读取文件内容 | 可标注 |
| fs_write | 创建、追加或修改文件内容 | 可标注 |
| net_send | 向远端发送请求、参数或内容 | 可标注 |
| net_receive | 从远端接收内容 | 可标注 |
| model_observe | 内容进入模型处理边界；具体版本由事件引用确定 | **禁止手写，由编译器产生** |
| user_output | 内容直接提供给用户 | 可标注 |
| transform | 选择、过滤、计算、组合或改变表示 | 可标注 |

网络请求可以同时发送和接收；网络未知的工具内容获取不补造网络标签。普通 return 不自动成为用户输出。共享上下文写入、IR 结果绑定、文件写入和模型观察各自独立。删除绑定不自动读取旧值；原样保存不自动变换。隐私声明不自动产生保护操作，transform 不证明脱敏。

空 effects 有合法依据时允许，不等于 NOP 或入口／出口相同。确实无法完成必要判断时使用独立 cannot_assess 分支，不能以空列表伪装无效果。次序存在候选时使用 order=partial；程序保存并求解必要先后约束。

## 2. 原始响应与编译响应

模型只输出 `RawAnnotationResponse`：

```text
RawAnnotationResponse
├─ outcome                  completed
├─ profiles                 四字段 profile；没有 model_observe
├─ locations                kind / name / operand_refs / access_scope / retention
├─ transfer_specs[ir_id]
│  ├─ order                 fixed / partial
│  ├─ events[]              ProcessingSpec 或单层 RawForEachSpec
│  └─ output_bindings[]     公开输出到符号值的绑定
└─ location_evidences       位置 ID → 非空 SpecEvidence 列表
```

ProcessingSpec 显式选择 model、local 或 default；包含原来的效果事件。local 必须提供源文／CFG 机制证据和 returns（可为空）；另外两种模式的 returns 为空。model 要求该 IR 的 operator 已包含 llm。不能只靠动作名称证明局部隔离，也不能因为字段名叫 summary 就宣称在做模型摘要。

模式按机制顺序判断：先寻找源文、代码或接口规定的执行和回传边界；明确模型参与时用 model；明确本地执行及内容可见边界时才用 local；其余用 default。筛选条件、简单计算、执行主体、opcode、没有提到 LLM，都不能把“能够本地实现”升级成“已经明确本地隔离”。local 的现有证据理由需解释机制与回传内容，空 returns 也需有据的无内容回传说明。契约已有默认时，不因实现未指定就进入失败分支。

操作选择保留最明确的已知值关系：原样转交直接绑定；明确字段／下标用 select_part；成员内容不变的筛选用 filter_items；明确删改组合用对应操作；实际计算或确实不透明的关系才用 compute。同一 IR 的分类计算和字段原值输出须分别表达，不能整体降成 opaque；也不能凭结果名称发明字段路径。详见[模式及值关系对照](SkillFlow-字段关系与观察编译.md)。

for_each 使用同一 item 绑定选择当前元素的 recipient、summary 等字段，保持实际参数配对。它是单层分析作用域，不改 CFG；内部禁止 read、receive、write、context_key 输入依赖，局部结果不逃逸。`filter_items` 保留集合筛选的元素身份及条件文本；不执行自然语言条件。

编译后的 `AnnotationResponse` 在原始五项基础上增加程序生成的 `sink_boundaries`，profile 仍四字段。effects 已含程序插入的 model_observe，transfer_specs.events 已变成直接 EffectSpec 或 ForEachSpec，并附程序生成的 precedence。没有旧格式自动兼容。`to_payload` 将经过检查的编译响应显式投影为传播使用的四项业务材料，位置证据另存。模型不得填写程序派生的 sink 清单、类型或等级。

位置身份由 `(kind,name)` 确定，外层位置 ID 用于符号引用。kind 允许 runtime_context、storage、model_context、remote、tool、user。operand_refs 为真实 `{instruction_id,side,index}` 列表，可空、不能重复；来源容器不能仅因包含目标字段就冒充该目标值的位置。位置证据表必须与 locations 完全同键且每项非空。

位置新增必填 `access_scope` 和 `retention`，同一位置只标一次。访问范围为 task/recipient/shared/public；存储和上下文留存为 task/persistent，其他接收边界可 null。依据继续放 location_evidences。默认、例外、六种 sink 和固定 0–3 级见[Sink 边界主规范](SkillFlow-Sink边界与固定分级.md)。程序收集具体交付和非删除写入，0 级操作保留传播但不进入清单；不从 roles 或 opcode 推断交付。

网络未知的工具请求用 null-effect 的 deliver → tool，获取用 receive → tool，回传观察由处理模式编译；三者不能互相代替。工具明确纯本地、任务内部时仍保留参数交付，但不单列 DOE sink。普通 return 不产生虚构公开输出、调用者位置或用户输出。

## 3. 证据、引用和严格校验

profile Evidence 保留 `field、value、basis、ref_id、quote、reason` 及可选 effect_index。basis 为 source、cfg、execution_model；ref_id 必须指向对应索引，quote 必须为该定位的真实引文。每个非空效果位置至少一条证据，effect_index 为零起始整数（布尔值不合法），标签须和该位置一致。operator／roles 去重；effects 不排序、不去重。

空标签字段用 value=null 说明无适用项；确实无法支持必要判断时返回有真实证据的 cannot_assess，不与正常 profiles 混合。覆盖、编号和引文校验仅证明记录一致，不证明推断正确。

处理段、逐元素作用域、原子操作与公开输出绑定使用 SpecEvidence：`basis、ref_id、quote、reason`。位置证据只放独立表。程序检查模式、值引用、局部定义、索引、作用域、操作／效果／边界相容性和输出覆盖。对 source/CFG 引文的真实性检查不等于证明它确实支持局部隔离。

原始八种非观察效果的索引按顶层处理段及 for_each body 顺序连续排列。编译器重排索引并为新增观察附 EM10 和处理段证据；必须分割混合操作事件时，数据切片使用具体原子操作证据，不能把原 net_send 证据冒充 transform 依据。完整映射留在审计材料。

ValueRef、十种固定原子操作和 output_bindings 的执行语义由[传播主规范](SkillFlow-传播算法与IR传递规格.md)及[编译规范](SkillFlow-字段关系与观察编译.md)共同定义。内容获取与 compute 的依赖关系不混同；参数次序、重复输入和候选替代保持。没有按 opcode 或理由关键词自动推断业务关系的规则。

## 4. 服务、保存与重放

服务职责明确区分：

| 入口 | 用途 |
|---|---|
| `annotate_skill(source,cfg,client=...)` | 一次调用，接受原始响应，校验并返回编译响应 |
| `validate_raw_response(raw,material)` | 原始类型及引文检查，不生成观察 |
| `compile_response(raw,material)` | 返回已校验原始响应、编译响应、编译映射 |
| `validate_response(raw,material)` | 对原始输入编译并返回完整编译响应 |
| `validate_compiled_response(compiled,material)` | 检查最终结构与证据；**单独调用不证明编译来源** |
| `to_payload(compiled)` | 显式生成四项业务投影，不替代引文核验 |

命令形式保持 prepare/run/replay。prepare 冻结源文、CFG、契约及索引；run 每图一次计划内调用，不逐节点补问、不自动修复坏响应、不择优；replay 使用接受响应重新校验和编译，零 API。超时、暂态传输重试、脱敏、互斥锁和中断规则沿用既有记录组件；已接受响应不重发，不确定请求不自动重发。

联合标注从基础客户端配置派生专用配置，启用 `response_format={"type":"json_object"}`；普通提取及语义核对的默认请求不因此改变。提示词包含一份独立、完整、可通过 Schema 的格式示例，明确禁止把示例编号及引文复制到真实材料。JSON Output 只减少语法错误，不能替代结构、引用或语义校验。

实际非敏感请求参数及请求体摘要与冻结配置一致绑定，注入客户端没有可观测 HTTP 参数时如实标记。服务拒绝 JSON Output 不移除参数降级重发；完整返回中的额外括号、重复键和坏 JSON 仍为 invalid_response，不自动修复。输出截断不能被当成完整接受响应；传输未完成、格式、结构／引文错误分开记录。离线重放核验原始响应、实际请求配置和编译材料，不调用 API。独立聚焦审查与一次修复见[表示契约与一次标注修复](SkillFlow-表示契约与一次标注修复.md)。

成功产物包含 profiles、locations、transfer-specs、validation、report 和 result。审计材料独立保存：

```text
audit/
├─ raw-annotation.json       经过严格解析的原始模式规格
├─ compiled-response.json    实际编译响应（含位置证据）
├─ compilation-map.json      原始位置到编译事件位置的映射
└─ location-evidences.json   编译后完整位置证据表
```

result.compilation 保存编译器版本及原始、编译、映射摘要。清单绑定输入、当前契约及源码。完整加载和重放重新编译接受响应，与业务投影、位置证据、映射及证书逐项比较，不能仅重算摘要后继续。审计文件先持久保存，最后提交成功 result；保存失败不形成成功记录。

运行版本为 `skill-ir-security-profile-v11`，schema_version=11，profile_schema_version=`security-profile-v10`。运行同时绑定表示契约 v3、编译器 v4、基础／修复请求种类和修复上下文摘要。旧运行、旧模型直接写观察或 sink 清单的响应和旧事件结构明确拒绝，不自动迁移。

## 5. 状态和验收含义

complete 表示标注／编译记录合法；partial 不导致 incomplete。semantic_failure 表示已校验的 cannot_assess 任务失败。input_error、invalid_response、execution_error、interrupted 分别保留输入、响应、执行和中断问题。它们不判定风险，也不证明模型理解正确。

中文报告按原始处理段、编译效果和数据关系展示，部分顺序及其先后约束单独注明。效果覆盖仍统计具有该效果的 IR 数，不因重复阶段虚增。审查时区分：模型提出的模式／关系、程序确定生成的观察、传播后的实际 Data 关系。

集中测试检查本地返回与原始数据版本、工具返回与请求参数、段内中间值、逐元素参数配对、作用域、过滤身份、结构／引文／映射篡改、一次逻辑调用和零 API 重放。编译通过不证明 local 真的隔离、model 判断正确、filter 谓词成立或源文完整。

最早 30 图、v6 来源边界试验和 abstract-runtime-v1 试验均保留历史身份；本次不回写其响应及结论。processing-v1-20260928-204710 是前轮历史材料，本轮不覆盖；新七例明确重建于独立修复实验目录。工程验证和模型表现分开报告。

当前表示职责使用唯一[表示契约](SkillFlow-表示契约与一次标注修复.md)。原始响应可改为 `outcome=cannot_assess, failure={reason,instruction_ids,evidences}`，不能同时包含正常五项。正常响应不得保留旧 unresolved 字段。

## 网络机制与可选参数

明确通信机制才支持 remote/net_send/net_receive；工具、发送动词或接收对象本身不构成机制。部署未说明保持 tool/recipient/null。原值与存在性旗标分别表示，build 成员的可选 when 是 Boolean ValueRef，控制不作为请求字段。交付与返回获取必须使用相同 request local。原始 Schema 禁止模型手写条件观察；程序按成员条件编译。详见[可选参数规范](SkillFlow-Sink标注收紧与可选参数.md)。

唯一 JSON 对象要求增加完整括号／字符串／逗号／唯一键自查；程序仍严格拒绝多余括号、截断和完整无效响应，不截掉多余文本，不质量补跑。
