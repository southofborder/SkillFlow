# SkillFlow 字段关系与观察编译

这轮调整解决两类不同的问题：**从一份记录中取出的字段应当保持原值与配对；标注已经说明模型处理时，程序应当可靠地产生观察记录。**它不把一个名叫 summary 的字段自动解释为模型摘要，也不把处理模式判断变成已经证明的执行事实。

CFG 保持原样。原文支持的“逐记录发送字段”可以在同一条批量 IR 的传播规格中展开为逐元素作用域；它不是新增 CFG 循环。需要中间数据版本的多个源文业务动作仍受现有提取粒度规则约束，本轮不另改第一阶段。

## 1. 先看完整层次

```text
模型原始标注（正常 outcome=completed）
├─ profiles[IR]                    主体、角色、非观察效果、证据
├─ locations                       交互位置、操作数关联及 access_scope/retention
├─ transfer_specs[IR]
│  ├─ order                       fixed / partial
│  ├─ events[]
│  │  ├─ processing                一段有明确处理方式的数据操作
│  │  │  ├─ mode                   model / local / default
│  │  │  ├─ events[]               原有有序效果与 atomic_ops
│  │  │  ├─ returns[]              仅 local：这段向模型返回什么
│  │  │  └─ evidences[]            处理方式的依据
│  │  └─ for_each                  按集合元素保持字段配对
│  │     ├─ collection             从哪个符号值取得集合
│  │     ├─ item                   当前元素的局部名字
│  │     ├─ body[]                 对当前元素执行的 processing 段
│  │     └─ evidences[]            逐元素关系的依据
│  └─ output_bindings[]            IR 公开结果对应哪个符号值
└─ location_evidences               独立位置证据
                  ↓ 程序编译
编译标注
├─ outcome / profiles / locations / transfer_specs / location_evidences
├─ sink_boundaries[]                程序派生的类型、等级、目标和操作位置
├─ transfer_specs[IR].order / precedence（程序生成约束）
└─ transfer_specs[IR].events[]
   ├─ EffectSpec                   effect_index + atomic_ops
   └─ ForEachSpec                  collection + item + body[EffectSpec]
                  ↓ 确定性传播
DOE 事实
├─ data                            实际数据身份和内容关系
├─ records[IR]                     IN、有序事件及 OUT
└─ sink_boundaries[]                只关联已经求值形成记录的边界操作
```

模型不写 model_observe；编译后的 profile 仍只有 operator、roles、effects、evidences 四个字段。ProcessingSpec 是标注／编译输入，不向 CFG 或 Data 添加处理模式字段。观察映射、证据和编译摘要保存在审计目录，不塞进 DOE 的逐条业务事件。

当前编译器 v4 同时为生成的模型位置填写 recipient/null 属性，并沿用 EM12 的真实规则依据。模型不得手写 sink_boundaries；编译后的观察、交付和非删除保存由程序生成六类 sink 与固定等级，清单位置按真实编译数组定位。既有接收方位置属性冲突不能通过覆盖定义消除。详见[Sink 边界规范](SkillFlow-Sink边界与固定分级.md)。

## 2. 三种处理模式

| mode | 标注方负责说明 | 编译器确定做什么 |
|---|---|---|
| model | 这段实际使用模型处理；IR 的 operator 须已有 llm | 在首次使用前观察段外实际输入；read/receive 后观察取得值；同段中间计算值不自动形成额外模型输入 |
| local | 有依据的本地隔离及显式 returns（可空） | 内部读和变换不观察；只在段末观察 returns 引用的版本 |
| default | 未指定隔离，按统一契约分析 | read/receive 后保留取得值的可能观察；非隔离变换的段外输入在使用前可能被观察 |

local 必须有 source/CFG 证据，不能只引用默认规则；其引文是否足以支持隔离仍是语义判断。model/default 的 returns 必须为空，避免存在被程序忽略的“局部返回”声明。

标注按机制决定模式，次序固定为：先确认实际使用的内容及源文／代码／接口规定的执行和回传机制；明确由模型处理时用 `model`；明确本地执行且明确内容可见边界时才用 `local`；其余使用 `default`。多个明确阶段继续分段，可计算的部分顺序使用 order=partial。必要判断无法完成时返回独立 cannot_assess/failure；缺少实现细节但契约已有默认时正常处理。

“可以写成一个本地程序”不能推出“此处已经规定本地隔离”。筛选条件、计算简单、opcode、主体标签、未提到 LLM，以及普通结果绑定，都不能单独支持 local。沿用现有 evidences 的中文理由，解释引文具体规定了什么机制和哪些回传内容；`returns=[]` 也需要明确无内容回传的依据，不能从 CFG 没有公开输出直接推出。

| 对照源文 | 模式与关系 |
|---|---|
| 仅要求保留启用记录 | default + filter_items |
| 明确在隔离的本地 worker 中筛选，只有筛选结果回传 Agent | local + filter_items；returns 为筛选结果 |
| 仅要求统计条数 | default + compute |
| 明确本地 worker 内部计数，只有整数结果回传，输入记录不回传 | local + compute；returns 为计数结果 |

这些示例锁定规则及编译后的数据版本，不声称离线测试能证明模型在真实输入上必然选对模式。权威运行时契约为 v5，统一规定默认、处理段和部分顺序的边界。

同段相同外部符号引用及其消费条件共同去重；条件观察不能吞掉后续无条件观察。不同处理段、不同取得／返回版本分别保留。中间结果不是额外外部输入：例如模型段 `A → compute → T → build → C`，观察 A 不意味着程序要虚构对 T、C 的两次新模型调用。若下一段再接收 C，则按下一段边界重新记录。

receive 的请求输入与响应不同。默认观察其返回值，不因为请求参与获取就自动观察请求参数。局部扫描整个文件、只返回匹配行时，内部扫描的整体与模型接收的行也不同。

自动增加 model_observe 不机械增加 operator=llm 或 roles=sink。执行主体和角色保留模型原来的有据标注；model 模式要求 llm 是对显式模式的结构条件。

## 3. 选取字段不是生成摘要

```json
{
  "op": "select_part",
  "input": {"kind": "local", "name": "row"},
  "path": ["summary"],
  "output": "body",
  "evidences": ["示意占位：正式规格必须是真实证据对象"]
}
```

这表达 **body 就是当前 row 的 summary 部分**。如果改成 compute，只能得到“某个新结果依赖 row”，无法保证仍是原字段，也不能保证它与另一个独立计算的 recipient 属于同一记录。

每个输出分别选择已有表示能力：

| 原文明示关系 | 表示 |
|---|---|
| 整份值原样转交 | 直接引用已有值，通过 output_bindings 绑定 |
| 已有字段或下标 | select_part，路径须有明确依据 |
| 筛选成员但不改变成员内容 | filter_items |
| 删除、替换、组合 | exclude_parts、update_fields、build |
| 分类、计数、生成摘要等实际计算 | compute，保留有据依赖 |
| 内部值关系确实未知 | compute，保留相关 possible 依赖 |

同一 IR 可以 `compute(response) → classification`，同时 `select_part(response,["payload"]) → payload`。不能因为其中一个输出需要计算，就把明确要求原样取得的另一个字段也降为 opaque。字段名叫 summary 不代表摘要生成；反之，只描述不透明处理时也不能根据结果名称发明字段路径。程序没有按 opcode 或理由关键词替模型选择关系的规则。

标注中的字段路径使用 `SpecPath`，只允许字符串字段名和严格非负整数下标。Data 在传播后使用的符号元素步骤由程序生成，不能由模型在 select_part、exclude_parts、update_fields 或 build 的路径中直接填写或伪造作用域。

filter_items 表达筛选记录且保留元素身份：

```text
集合 records
    → filter_items(predicate="只保留 enabled=true 的记录")
    → 可能被保留的原元素集合
```

程序记录条件，不执行自然语言、不宣称所有元素实际通过。筛选不生成一批与原记录无关的新内容。读取明确字段与过滤集合各自保留路径／谓词；不因为后面只需某字段就自动缩小此前观察的整体。

## 4. 同一元素的字段与参数必须在一起

下面是结构示意，省略正式非空证据对象：

```python
{
    "kind": "for_each",
    "collection": {"kind": "input", "index": 0},
    "item": "row",
    "body": [{
        "kind": "processing",
        "mode": "default",
        "returns": [],
        "events": [
            {"effect_index": 0, "atomic_ops": [
                {"op": "select_part", "input": {"kind": "local", "name": "row"},
                 "path": ["recipient"], "output": "recipient"},
                {"op": "select_part", "input": {"kind": "local", "name": "row"},
                 "path": ["summary"], "output": "body"},
            ]},
            {"effect_index": 1, "atomic_ops": [
                {"op": "deliver", "inputs": [
                    {"kind": "local", "name": "recipient"},
                    {"kind": "local", "name": "body"},
                ], "target": "notification_service"},
            ]},
        ],
    }],
}
```

原始 effects 对应 transform、net_send；默认处理可能插入对 row 的观察。每个实例的两个字段都从**同一个 row** 选出。不能分别形成所有收件人集合和所有正文集合后任意笛卡尔组合。

本轮仅支持一层作用域。collection 可来自当前 IR 的结果输入、字面值或已定义的外层 local。body 可使用 item、较早外层 local 和稳定输入，但不能 read、receive、write 或直接引用 context_key 输入；这些获取须在作用域外完成。body 的 local 不逃逸、不覆盖外层 local；不能被 IR output_bindings 引用。不同作用域可以分别使用相同的局部名字。

已知有限列表逐元素形成实例；未知集合使用稳定的符号元素，不编造长度或无穷展开。过滤之后的元素保留与原集合的关系。没有求值的谓词和分支相关性仍是保守边界。

## 5. 编译只维护一条时间线

顺序是 `IR → 顶层段／作用域 → 效果事件 → atomic_ops`。程序插入观察后重新编号 effects，每个非空位置仍恰好对应一个事件。for_each body 的效果也参与同一遍历顺序。

若原事件中包含 `read → select_part`，默认观察须插入 read 之后；编译可以切成：

```text
fs_read          read → whole
model_observe    deliver whole → 模型上下文
transform        select_part whole → field
```

切片保留原子操作顺序和真实交互。不是每个原子操作都强制新建效果；无需切片时原事件整体保留。真实 read/receive/deliver/write 保留其相应效果，纯数据切片按固定数据操作类型标 transform，原无标签 possible compute 保持无标签。新增 transform 引用具体操作依据，不能复制 net_send 标签当作变换依据。

原始 IRTransferSpec 必填 order=fixed/partial。编译器产生 precedence，before/after 均为 event_index、op_index 和可空的 body_event_index；模型不填第二份顺序表。编译保留段内原子顺序、直接定义使用以及观察因果：模型输入先观察再处理，获取后才能观察返回，本地全部处理后才观察 returns。partial 的不同段可在原子步骤间交错，不把整段当不可分割的动作。作用域仍保持同一元素配对；需要跨作用域共享状态交错的规格明确拒绝。编译映射把每个编译事件定位回原始事件和操作范围，观察项注明模式与规则来源。

## 6. 编译身份与 API

`compile_response(raw, material)` 返回 `(validated_raw, compiled, mapping)`。原始响应禁止 model_observe；编译响应允许它。`validate_compiled_response` 只检查结构和引文，不能凭一个可解析的 JSON 证明它来自正确编译。

完整运行还须保存原始接受响应、原始规范化标注、实际编译响应和映射；证书绑定编译器版本及这三份材料的摘要。恢复和重放重新编译后逐项比较，发现篡改拒绝继续。四项业务 payload 为 profiles/locations/transfer_specs/sink_boundaries；outcome 和位置证据留在完整响应中，证书在旁置审计材料中。

| 对象 | 当前版本 |
|---|---|
| 运行时契约 | skillflow-abstract-runtime-v5 |
| 联合标注及运行 | security-profile-v10 / skill-ir-security-profile-v11 |
| 观察编译器 | skillflow-processing-compiler-v4 |
| 编译映射 | skillflow-processing-compilation-v4 |
| Data | skillflow-data-v4 |
| 传播记录 | skillflow-propagation-record-v9 |
| DOE 输入 | skillflow-doe-input-v7 |
| 传播运行 | skill-ir-propagation-v10 |

旧记录不自动迁移或重解释。CFG、生产提取和语义核对契约不因本轮增加字段。

## 7. 本轮能保证什么

程序可以保证已接受类型、实际引用和规则之间的一致性：该观察按哪个模式生成、使用哪个数据版本、逐元素参数是否维持同一元素作用域，以及审计材料是否重编译一致。

程序不能保证模型选择的模式真实、局部隔离充分、source/CFG 证据足以证明关系、自然语言谓词已经成立，也不能证明任意 Skill 与图完全等价。真实实验需单列助手复核，不能把结构通过称为人工确认或语义证明。

离线验收集中覆盖获取与请求、先观察后处理与本地处理后返回、段内中间结果、跨段重复、逐元素原字段配对、部分顺序及观察因果、原始／编译格式拒绝、摘要篡改及零 API 重放。只有这些测试和实测完成后才报告实际结果；本规范不预写成功结论。

上一轮三例试验复用 `run_runtime_pilot.py`，按明确批准的范围原位替换 `processing-v1-20260928-204710` 内三例的标注、传播与生成审查材料。冻结源包和选定 CFG 先校验，其他历史目录及 30 例交付物不变。新失败不能继续展示被替换轮次的成功 DOE 文件；运行时间及新身份由新清单记录。当时每例一次联合标注，不重新提取、不自动语义修复，也不把旧版响应迁移成新结果。

该轮先收紧联合标注提示词并启用 API JSON Output，尚未增加独立的标注语义审查调用。JSON Output 只约束输出语法，仍须通过严格 JSON、引用、证据和编译校验；已完整返回的错误内容不截断修补或质量重试。现有 SSE、超时及暂态传输重试保持。工程测试与助手复核分别报告。

目前已增加[聚焦审查及最多一次修复](SkillFlow-表示契约与一次标注修复.md)。最新七例审查与三份 CFG 核对单独保存于 [repair-once-v1 实验](../packages/skill-ir/experiments/annotation_review/runs/repair-once-v1-20260929-132248/assistant-review.md)，没有覆盖上述历史材料；当前契约及命令以对应规范为准。

## 记录中的空集合与开放集合

```text
ForEachRecord
├─ kind = for_each
├─ collections             实际待遍历的集合候选，包括明确空集合
└─ instances[]
   ├─ collection           当前候选来自哪个集合
   ├─ element              同一个成员的稳定身份
   └─ body[]               该成员的有序事件与操作
```

`collections` 使空集合仍可追溯来源。没有 instance 只适用于明确空列表及其子集视图；
未知整体不能被当成空。开放集合里已经识别的整数成员与未知符号成员同时保留，不宣称它们互斥。
字段 origin 的路径规范化到同一个原整体，例如 `[ElementStep, "recipient"]` 与
`[ElementStep, "summary"]` 共享前缀；不要求 part_of 总是直接指向中间元素。

独立 DOE 加载校验结构、引用、成员关系和已声明空集合；不在缺少原规格时证明候选实例绝无遗漏。
完整运行摘要及重新传播负责发现删除一个形状仍合法的实例等篡改。

离线示例：`python packages/skill-ir/examples/processing_demo.py --output <新目录>`。
它使用人工编写的处理段，执行真实编译、传播、DOE 保存及报告生成，不能冒充模型实测。

## 条件构造与观察

`BuildMember(path,value,when)` 在 build 的 parts 中表达可选对象字段；when 省略或 null 时无条件。控制本身与字段内容分开观察，成员值的编译观察复用相同条件。条件为 false 时不解析或观察被省略值；可能为 true 时仍检查值绑定。中间局部值不会自动变成新的外部输入。原始标注不得手写 DeliverOp.when 或 model_observe。

公开结果、局部值与处理模式保持原契约。交付和对应获取引用同一 request local；编译器保存必要的先后约束，解释器直接复用交付数据。详见[可选参数主规范](SkillFlow-Sink标注收紧与可选参数.md)。
