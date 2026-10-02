# 008-catalog-query · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：Q02；运行：full-pipeline-v4-20260918；选图轮次：0
- 反馈停止：audit_error；原因：159 validation errors for AuditResult；代表错误：findings.1.controlled_refs.0：Input should be a valid dictionary or instance of ControlledRef；完整诊断保留于原始运行记录及审查页展开区。
- 安全标注：incomplete；原因：保留有依据的标注，存在未决项。
- 图 SHA-256：ac4801c39e5d80d8c6ab91c27dcb53d21bc612b79d4469f14e4a1f6df0516dd7；源文 SHA-256：d96ebca9513a94331237527adb4ed3a0c55f032f11c71b4d8682f8ccdb305d04

未填写保守说明不代表精确保留；覆盖记录不证明语义完整。

反馈完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918/cases/008/feedback/result.json>)；本地审查页也可展开全文。

安全标注完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918/cases/008/annotation/result.json>)；本地审查页也可展开全文。

当前所选图没有合法的完整语义核对记录。不能由结构有效或其他轮次的发现推定通过。

## 安全标注未决

- {"instruction_id": "ir_012", "field": "effects", "reason": "无法确定 index.search 是否为远端网络服务；工具名和外部资源标识不足以证明 net_send/net_receive。"}
- {"instruction_id": "ir_017", "field": "effects", "reason": "普通 return 不能单独证明面向用户输出，无法确定是否产生 user_output。"}

## 助手事后复核

此部分独立于模型核对记录，未经人工确认，不追溯修改模型判定。

### 修复轮次 0 · 当前所选图

图 SHA-256：ac4801c39e5d80d8c6ab91c27dcb53d21bc612b79d4469f14e4a1f6df0516dd7

助手独立复核：查询主过程及参数省略声明可定位，但本轮核对因响应格式非法仍为 audit_error；标注的两项未决有实质依据，执行主体推断仍需收紧。

- 本次复核绑定 r000 实际图，已读冻结 Q02 全文、全部 17 条 IR 及控制边/约束、全部 profile 证据与两项 unresolved。反馈收到完整响应但 159 处 controlled_refs 使用字符串而非 ControlledRef 对象，结果为 audit_error，没有合法 audit/findings 或保守解释。该错误不是语义不通过，也不是网络超时；助手独立检查不把无效响应改判为通过，原始完整诊断保留。
- ir_001 读取 request.json；ir_003 提取 term；ir_004/ir_008 分别检查 from_date/limit 是否存在，存在分支才执行 ir_006/ir_010 取值，缺失路径跳过对应取值；各路径合流至唯一 ir_012 index.search，没有重试或第二次 search。查询约束保留 term 原值、from_date 原值与 YYYY-MM-DD、limit 原值、缺失分别省略参数。存在性判断是支持省略语义所需控制，不是源文未要求的格式校验或规范化。
- 实际 ir_012 的输入同时列 result_004/from_date 和 result_006/limit，这两个结果只在各自存在分支定义。按 IR-PATH，不能仅据某路径无定义就判结构/语义错误；图也没有显式可选操作数或四组独立调用实参列表，省略行为主要由操作约束承载。因此只能确认存在性分支、参数来源和省略声明可定位，不能据此证明运行时省略机制已实现，也不能把依赖列表直接读成缺失时仍同时传参。本轮没有合法核对结果，不能替模型补写 DEP-MERGE 后声称通过。
- ir_014 从 result_007/search_response 提取 total=result_008，ir_015 写本地 count.txt；随后 ir_016 从同一响应取 items=result_009，ir_017 原值返回该 items。没有错把 total 当返回值或 items 当计数。图级约束保留不调用 index.delete、不要求 fuzzy 扩展、参数描述不要求预校验/规范化；实际没有这些额外动作。
- 标注明确保留 ir_012.effects 的网络边界未决：index.search 名称和 external_resource 不足以确定 net_send/net_receive；这符合 EM06，不能为了减少 incomplete 强行补网络标签。该动作 tool、多 roles source/sink/transformer、transform 与 EM02 下工具结果 model_observe 有相应接口和执行规则依据。ir_017.effects 未决是否 user_output 也合理：return 返回 items 不能证明最终展示给用户。
- 其余读取、提取、存在性计算及写文件的 fs_read/transform/fs_write 可由实际动作支持；但将 ir_001、ir_003/004/006/008/010/014/016 一律确定为本地 agent_runtime，仅有 opcode，没有执行位置或模型隔离证据。各 dispatch 的 llm actor 又从 EM03“承认存在LLM调度”推为本节点执行者，规则不足以支持这种必然化；这些执行主体不确定性没有列入原两项 unresolved。
- 未把 index.delete 禁止或不要求 fuzzy 扩展解释成实际保护动作，未从普通 return 自动补用户输出，也没有按“查询工具”猜网络双向传输。总体业务检查与标签疑点均为助手意见而非核对器通过/人工确认；17 profiles 的 incomplete 状态和 audit_error 原样保留。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
