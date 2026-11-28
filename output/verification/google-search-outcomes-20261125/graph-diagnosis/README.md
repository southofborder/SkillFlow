# 190529 CFG correction：新副本离线诊断

本目录只读取实际 a001 草稿和完整两文件源码，将新副本送入既有 `assemble_graph_facts`、`plan_graph_repair`、`apply_graph_updates`。不改生产或运行产物，不调用模型，不做历史 replay，不接受修复后的 CFG。

`diagnose.py` 的断言全部通过，结果见 `diagnosis.json`：

1. 原草稿复现 `call_return_binding`。`helper.prepare_values.metadata.predecessor_bindings` 给四个 Python 参数绑定之外又加入 `helper.return_scope: {literal: public/cli}`。现有校验要求对应值为实际结果版本字符串。
2. 既有程序生成的 `cfg_calls_40fed56c8366a7140098b383` 只授权两个块：`cli.invoke_helper` 的参数动作/entry exit，以及 `helper.prepare` 的 formal 动作。
3. 新副本只删除两个非参数的非法 literal 表项，保持所有物理 spans、source_actions、输入、输出与控制边不变。直接 call-site 检查不再报参数错误；但同一改动经现有 patch compiler 被拒为 `cfg_region_boundary`：要求保留 physical invocation/parameter evidence。
4. 原因是父动作 source span 为 6–13 行，原有三个子动作 spans 是 6、7、8–13；当前 changed-formal 校验要求各子 span 都等于父 span。后续另一独立 gate 又要求非 source 元数据完全不变，连该错误恰需修改的 `predecessor_bindings` 也不能改。

因此，错误 pointer/guidance 更精确仍无法让这个保留证据的局部参数表改动通过当前 contract。这是 edit gate 的表达能力问题，不只是模型没理解提示。

**但修好这两个 gate 也不足以宣称本案源码忠实修复完成。** `helper.return_scope` 后续同时被正常 `helper.return_dispatch` 和异常 `helper.merge_exception` 消费，以区分独立 public 调用与 CLI 调用。删掉其非法参数表项，并没有建立它的合法来源。四个参数的值本身不能标识调用者；不能将它别名为 query/key，也不能把 public/CLI 或正常/异常路径合并来通过编译。当前 slot 不授权这两个后续 exit，且不允许添加/复制 callee blocks，因此没有在本测试中建立完整的调用上下文修复。

本诊断只证明局部参数检查与 patch gate 的冲突。完整修复仍需明确处理调用上下文/continuation，例如经支持并校验的程序控制关联，或源码忠实地分离 callee 上下文；不能以 metadata 删除后的结构通过代替语义正确性。本目录没有生成或接受“修复成功”的 CFG。

精确代码位置：`call_region.py:117–120`（参数表值）；`:317–328`（既有块/动作限制）；`:361–365`（子动作 span）；`:369–381`（metadata 不可变）。实际在线 a002 还改了 caller 的无关 metadata，revision 又改了物理证据；这些失败保留在原运行文件中，本目录不重写它们。
