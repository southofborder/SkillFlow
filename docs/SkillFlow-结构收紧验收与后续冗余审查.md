# Data、位置与证据结构收紧：验收与后续审查

> 本文是上一阶段的验收记录。文中可删除／可合并候选已在[DOE 输入收紧与三例复核](SkillFlow-DOE输入收紧与三例复核.md)中实施；应保留项继续保留。下文原阶段测试与实验记录保持历史含义。

本轮只收紧结构、名称与保存边界，不改传播规则、效果顺序或数据版本关系。没有调用远程模型，
没有重新提取 CFG，也没有重写三例试验和 30 例交付物。下面先给出可直接人审的字段树，
详细类型与函数仍以[完整树状说明](SkillFlow-传播结构与函数树状说明.md)为准。

## 1. 当前业务字段树

```text
Data
├─ id                         稳定数据身份；由注册表登记键确定
├─ content                    内容关系，五种形式之一
│  ├─ opaque                  尚未展开，不是空数据
│  ├─ known_parts             已知组成：parts + parts_complete
│  ├─ whole_except            原整体 base 排除 excluded_parts
│  ├─ literal                 明确 JSON 值，区分 null、空对象和空列表
│  └─ field_updates           原整体 base 的指定字段使用新 Data，其余保留
├─ origin                     获取与派生关系，不重复保存标注证据
│  ├─ at                      获取／处理发生的位置标识
│  ├─ acquired_from           外部获取来源；结果不自动成为新外部来源
│  ├─ part_of / path          若为组成部分，指出所属整体和字段路径
│  ├─ inputs[]                实际输入的 Data ID，保留顺序和重复
│  └─ dependencies[]          影响关系，不等于明文包含
│     ├─ data                 被依赖的 Data ID
│     └─ relation             derived 或 possible
└─ annotations
   ├─ description             描述
   ├─ sensitivity[]           已有敏感性标注；传播本身不生成
   └─ evidences[]             仅供后续 DOE 敏感性判断的依据字符串

LocationSpec                  声明一个可读写位置或交互边界
├─ kind                       类别：上下文、存储、模型、远端或用户
├─ name                       此类别中的稳定名称，不是数据内容
└─ operand_refs[]             必填、可为空；指出相关 IR 操作数
   ├─ instruction_id          IR ID
   ├─ side                    input 或 output
   └─ index                   零起始操作数位置

FlowLocation                  实际状态或事件使用的位置身份
├─ kind
└─ name

SpecEvidence                  规格判断依据；位置依据另存
├─ basis                      source / cfg / execution_model
├─ ref_id                     已有证据单元编号
├─ quote                      该单元中的原引文
└─ reason                     中文推断理由

Profile Evidence              标签及某次效果的依据
├─ field / value              支持的标注字段与标签
├─ basis / ref_id / quote / reason
└─ effect_index               若支持具体效果，定位它在 effects 中的出现
```

`origin.inputs`、`dependencies` 和 `content` 分别描述实际输入、影响关系和内容关系，
三者没有合并。它们不是重复的判断证据。例如计算依赖 B，不表示结果中包含 B 的全部明文。

`(kind, name)` 决定位置身份；外层位置 ID 用于规格引用。同一个操作数可对应多个可能位置。
`DataRegistry` 的 `key` 是数据登记身份，不是位置名称，仍保留原名。

`read.location`、`receive.location` 和状态条目的 `location` 仍表示业务位置。
证据编号和 `instruction_index` 的证据指针都使用 `ref_id`，不再与业务位置混用。

## 2. 完整响应与传播材料的关系

```text
同一次模型调用返回 AnnotationResponse
├─ profiles                   每条 IR 的 operator / roles / effects / evidences
├─ locations                  三字段 LocationSpec
├─ transfer_specs             events / atomic_ops / output_bindings
├─ unresolved                 外置未决
└─ location_evidences          位置 ID → 非空 SpecEvidence[]
             │
             │ validate_response：校验完整响应与真实引文
             │
             ├─ to_payload：显式取四部分业务材料
             │       └─ AnnotationPayload → propagate / PropagationRecords
             │
             └─ 独立审计表 → audit/location-evidences.json
```

五部分响应直接传给传播器或记录容器会失败，不自动丢弃多余字段。空位置表对应空证据表；
有位置时，证据表必须恰好覆盖每个位置。业务 JSON 不夹带该表，主页面默认展示数据与操作，
位置证据放在单独的折叠审计区。

保存和恢复还核验两份投影与完整已接受响应的一致性。单独修改业务材料、独立表或引文，
包括修改后重算摘要，都不能替换已接受响应。标注成功记录在独立审计表写入后提交；
保存中断可以复用已接受响应，不因此再发一次模型请求。

本轮版本为 Data v3、联合标注 v5、标注运行 v5、执行模型 v5、传播记录 v3、传播运行 v2。
不提供旧字段别名、不迁移历史记录；Data ID 受新版本身份规则影响，不能跨版本强行对齐 ID。

## 3. 离线交付与验证

- [新的传播审查示例](../packages/skill-ir/experiments/propagation/runs/schema-pruning-v1-20260924/offline-demo/report.html)：13 条 IR、5 个位置，0 次模型调用，计算状态 complete。
- [精简 Data 示例](../packages/skill-ir/experiments/propagation/runs/schema-pruning-v1-20260924/data-demo.json)：16 份 Data，可查看新增字段、派生、排除、覆盖与敏感性依据的独立用途。
- [独立位置审计表](../packages/skill-ir/experiments/propagation/runs/schema-pruning-v1-20260924/offline-demo/audit/location-evidences.json)：不放回业务 locations，也不进入 Data。
- [受保护文件检查](../packages/skill-ir/experiments/propagation/runs/schema-pruning-v1-20260924/protected-check.json)：9,220 个原文件逐字节 SHA-256 一致，缺失 0、变更 0。

示例由作者提供规格，校验真实引文后运行确定性解释器；它是工程示例，不是模型实测。
浏览器工具的本地 URL 策略阻止直接打开这份新 HTML，没有绕过；不宣称已完成新示例的手工截图审查。
审查模板的自动浏览器回归另外验证字段展示、折叠审计和文本转义。

专项离线结果（各子集可能交叉，不能将行数直接相加）：

| 范围 | 结果 |
| --- | --- |
| 整个 `packages/skill-ir/tests` 回归 | 1,811 项通过，741.87 秒 |
| Data 模型与注册表 | 168 项通过 |
| 标注契约、传递规格、上下文写入、报告与标注运行核心 | 204 项通过 |
| 批次、全流程、导出及审查工具六文件 | 148 项通过 |
| 追加新版审计交互后的审查页回归 | 35 项通过，含本地 Edge 测试 |
| 传播求解、记录与运行 | 109 项通过 |
| 文档检查 | 4 份现行文档、21 个本地链接有效，代码围栏成对 |

全套启动后另补的一项“同一操作数关联多个命名位置”测试，已包含在后续 109 项传播专项中通过；
不将尚未重新收集该测试的全套命令报告为 1,812 项。全套覆盖既有提取、语义核对、反馈、
受控回述、记录、Data、安全标注和传播回归。完整运行命令为：

```powershell
python -X utf8 -m pytest packages/skill-ir/tests -q
python -X utf8 -m pytest packages/skill-ir/tests/propagation -q
```

测试覆盖五部分／四部分边界、独立表篡改与摘要、
旧字段拒绝、数据版本、候选分支、强弱更新、受支持循环、客户端调用次数和零 API 重放。
工程测试不证明模型对位置或传播语义的判断正确。

## 4. 下一轮冗余候选：本轮只读，不继续修改

| 分类 | 候选与代码依据 | 影响与建议 |
| --- | --- | --- |
| 可以无损删除（仓库内部） | `propagation/records.py` 的 `intermediate_key`、`symbolic_endpoint` 只有定义及 `__init__.py` 导出，当前源码、测试、示例、活跃工具无调用；实际求解使用 `interpreter.static_key` 和已声明位置 | 删去不会改变仓库内当前求值；它们是公开导出，删除前仍应确认是否有仓库外调用，并更新函数树。不能把“内部无调用”当成对外兼容保证。 |
| 可以合并实现 | `propagation/report.py` 的 `render_markdown` 与 `render_html` 分别遍历 profile、IR 操作和 Data；已共用 `_labels`、`_changes` 等，但表格内容组织仍重复 | 可建立一份纯展示行模型供两个渲染器使用；保留 HTML 转义与 Markdown 专用处理，不合并不同证据语义。 |
| 可以合并实现 | `examples/propagation_record_demo.py` 仅通过 runpy 委托主示例，再取 records | 可统一示例入口；应保留明确的“整轮结果”和“仅记录”输出选择。当前没有两套传播算法。 |
| 需要另行改变保存契约 | `runner._save` 同时保存 result.registry、result.records.data、data.json；result.records 与 records.json 也重复 | 可讨论一个权威 Data 文件加摘要引用，但会改变自包含快照、移走原目录后的重放、报告输入和验证边界，不能本轮随手删文件。 |
| 需要另行改变标注契约 | `OutputBinding.output_index` 的合法取值和操作数数量由 CFG 决定，但它绑定哪个 input/local/literal 仍需规格说明 | 可讨论用键索引表达输出位置，不能删除 output_bindings：CFG 并不唯一说明处理前／后哪个 Data 是输出。位置的 operand_refs 同样不能按名字自动推断。 |

优先建议先合并展示层的实现，再讨论自包含快照的保存方式。ValueRef、九种原子操作、
output_bindings，以及原始／处理后 Data 的区分有各自职责，本轮没有依据继续合并这些业务概念。
