# 当前源文审查输入与 Task 字段需求

这是初次源文审查尚未返回时的只读快照。实际阶段提示词为 897,543 字符、897,772 字节；686,494 字符的共享 JSON 精确展开为 1,188,576 字符的逻辑 payload。仅换回同一完整逻辑输入，提示词会达到 1,399,625 字符。这说明实际展示节省，不证明答复成功或生成提速；传输包装另计。

完整源文段包含全部 16 文件、180,825 字符，文件表与展示内容均和本轮冻结源码一致。完整 annotation、观察、Task、v12 契约、阶段状态、缺口和审查清单都能精确还原。CFG 的展示规范化和重复 fragment-origin 信息去除沿用现有规则，不能混称为原始 CFG 文件逐字相等。契约正文仍完整保留在 annotation 中。

审查收到 528 个契约义务、1,735 个范围：439 个工具物理操作义务、89 个 compute 义务；范围由 439 个接口、865 个 required、342 个 remainder、89 个规则范围组成。全部义务身份、契约身份、目标及范围描述符与保存的完整清单一致。清单中没有缺失附件；获取端投影能力声明为 0，表示尚无已声明、已审查的裁剪能力，不等于工具不支持裁剪。此时尚未接受任何审查结论。

当前装配为 partial：484 条 modeled IR，19 个源文声明缺口加 1 个校验缺口。49 个 Task realization 编译为 27 个 retained_only、13 个 partial、9 个 expressed。这些是映射状态，不是源文审查已经确认任务完成。需求有 33 条 IR demand（11 条非空字段路径）和 32 条操作 demand（25 条非空字段路径），涉及 value、action、truth、cardinality。

具体字段需求包括 GA4 行内维度值和指标值的嵌套 each、Search Console 行的 keys/clicks/impressions/ctr/position、空批量结果的 rows/rowCount、逐成员 url/indexed。因此任务所需子字段已经出现，而 89 份 compute 契约仍只有整体输出规则；这些契约能否支持对应子范围，仍要由审查与后续确定性推导检验。

映射把源码没有传递 filters、orderBy 的现状保留为缺口，没有补造请求参数。已保存分析的总结义务也保留了两项缺口：无法绑定具体调用与所存文件，以及没有实现 Markdown 后续。这些是待独立审查的映射声明，还不是字段可删除结论。

ir_001 的隔离事实没有消失：完整 CFG 仍有该 IR，processing_gaps 和 annotation._validation_gaps 都带有准确错误。实际目标 `cfg:/blocks/block_001/instructions/0` 可用；被删去的 annotation 记录没有虚构目标。processing 为 partial，按协议不产生 stage:processing 失败目标。审查仍可读取真实 CFG、源文和缺口，不会把隔离记录当成成功的空操作。

证据见 `source-review-input-v12-audit.json`。审计仅比较已保存字节、展开展示编码并核对确定性展示投影，没有执行项目阶段、语义校验、编译、传播、DOE、模型、Skill 或重放。最终选择、审查通过范围、修复与实际后端覆盖仍待后续记录。
