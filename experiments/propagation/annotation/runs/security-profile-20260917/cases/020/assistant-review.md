# 020 / D02 助手复核

**14条IR标注记录完整；关键脚本效果与回传路径边界表达合理，但有3处模型观察对应sink角色漏标，以及1处LLM执行者依据不足。不能把complete当成标注语义全部正确。**

本记录是助手事后复核，未冒充用户确认；原始模型响应和profiles未修改。

工程记录：`complete`，14/14条IR，56条证据，`unresolved=[]`。一次逻辑调用、3次HTTP尝试；前两次DNS失败，第三次HTTP 200并收到完整SSE结束标记及stop。实际返回模型名为`deepseek-flash`。

## 关键发现

### 1. ir_001 / roles：漏标

在当前profile保留model_observe的前提下，动作已经被解释为使内容到达LLM可见边界；按本轮sink定义，应同时记录sink角色。当前只记录数据引入或变换，角色与效果不一致。该意见不判断任何数据是否敏感或是否泄露。

- 源文依据：SKILL.md / src_003：读取用户提供的 manifest.json；执行规则EM02/EM04的模型观察说明。
- 图位置：`/blocks/block_001/instructions/0：ir_001`
- 当前标注：{"actor": ["agent_runtime"], "roles": ["source"], "effects": ["fs_read", "model_observe"]}
- 建议：先确认该动作的模型观察依据；若保留model_observe，补sink及对应证据；若实际执行主体/回传方式未定，则将相关事项保留未决，不将现有标签直接作为已核实事实。

### 2. ir_003 / roles：漏标

在当前profile保留model_observe的前提下，动作已经被解释为使内容到达LLM可见边界；按本轮sink定义，应同时记录sink角色。当前只记录数据引入或变换，角色与效果不一致。该意见不判断任何数据是否敏感或是否泄露。

- 源文依据：SKILL.md / src_003：按其中 paths 列表获取文档路径；执行规则EM02/EM04的模型观察说明。
- 图位置：`/blocks/block_002/instructions/0：ir_003`
- 当前标注：{"actor": ["llm"], "roles": ["transformer"], "effects": ["transform", "model_observe"]}
- 建议：先确认该动作的模型观察依据；若保留model_observe，补sink及对应证据；若实际执行主体/回传方式未定，则将相关事项保留未决，不将现有标签直接作为已核实事实。

### 3. ir_005 / roles：漏标

在当前profile保留model_observe的前提下，动作已经被解释为使内容到达LLM可见边界；按本轮sink定义，应同时记录sink角色。当前只记录数据引入或变换，角色与效果不一致。该意见不判断任何数据是否敏感或是否泄露。

- 源文依据：SKILL.md / src_003：从请求中读取 output_dir 和 delivery_path；执行规则EM02/EM04的模型观察说明。
- 图位置：`/blocks/block_003/instructions/0：ir_005`
- 当前标注：{"actor": ["llm"], "roles": ["source"], "effects": ["context_read", "model_observe"]}
- 建议：先确认该动作的模型观察依据；若保留model_observe，补sink及对应证据；若实际执行主体/回传方式未定，则将相关事项保留未决，不将现有标签直接作为已核实事实。

### 4. ir_003 / actor：证据不足

源文只要求从manifest的paths字段获取路径，图只记录字段提取，未规定必须由LLM完成；模型理由却写“该提取动作需模型”。EM04说明模型实际处理时应加观察效果，是条件规则，不能反过来证明这个提取动作一定交给模型。运行时JSON取字段也符合当前业务描述。

- 源文依据：SKILL.md / src_003：“按其中 paths 列表获取文档路径”；EM04：“本地处理与模型处理分开”。
- 图位置：`/blocks/block_002/instructions/0：ir_003 extract_document_paths_from_manifest；metadata为空，无执行者或工具映射。`
- 当前标注：actor=["llm"]；actor证据reason="该提取动作需模型从manifest内容中读取并选择路径，由LLM参与执行。"；effects含model_observe且unresolved为空。
- 建议：后续规则修订时明确开放字段提取操作的执行映射；在没有该映射时保留actor及其派生观察效果的未决，不用条件性执行规则替代具体动作依据。此次实验原响应保持不变。

## 其余核查与边界

- 完整阅读SKILL.md、scripts/convert.py、scripts/package.py以及全部14条IR、metadata、边和56条profile证据。
- 隐含模型观察：ir_001/003/005/007均有model_observe；ir_007理由明确只讨论脚本stdout产物路径，没有扩张成文档全文观察。ir_009脚本无stdout且图无结果，没有强加观察效果。
- 多主体/多角色：ir_007/009的actor为agent_runtime+tool，roles为source+transformer+sink；已检查其文件读取、处理和写入依据。ir_001/003/005的模型观察与sink角色不一致，列为发现。
- 网络双向：本图没有明确网络调用，未出现net_send/net_receive；这不证明实际运行没有网络副作用，只是本次标注没有据工具名虚构网络。
- 保护声明与transform：ir_007/009依据脚本读写及打包行为标transform，没有把“不得修改原文”“禁止上传”当成脱敏或隔离操作。
- 纯控制/return：全部dispatch的roles/effects为空且有解释；ir_014为无值return，没有user_output。
- ir_011按文件路径交付解释为fs_write，源文未给实际delivery_path值；本次不推断具体接收者或传输范围。

未执行脚本，未计算数据传播或敏感数据集合，未作风险或必要性判断。当前发现属于动作标注一致性和执行主体依据，不是实际泄露结论。

证据：[原始标注](profiles.json) · [源文](inputs/source.json) · [实际图](inputs/cfg.json) · [运行结果](result.json)
