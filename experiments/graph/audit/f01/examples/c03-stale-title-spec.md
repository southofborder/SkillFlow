# c03 人工回述规格示例

**这是人工撰写的预期表达示例，不是模型输出或实验结果。它专门说明残留标题与真实指令的区别，不作为模型输入。**这里只展示受变体影响的片段，不能冒充完整图回述。

archive 失败的条件边进入失败终态块。该块仍以“Append failure status and return the archive.fetch error”命名，但其实际指令列表现在只有 return；return 的输入引用 archive 调用产生的 error。这个块的列表中没有 status.txt 追加指令。

图级约束仍记录“Before returning from every success or failure path, append the final status to local status.txt.”。因此，图同时保留了要求追加的文字与一个没有追加动作的失败终态结构。回述应分别呈现这两项证据，不能因为标题和约束仍在就描述成“失败时先追加 failure 再返回”。

实际可定位证据是 `/blocks/block_014/instructions`、`/blocks/block_014/block_name`、`/blocks/block_014/instructions/0/inputs/0`、`/constraints/1` 及通向该块的失败条件边。此处没有引用原 Skill；是否遗漏源文要求，应由另一个 source_to_graph 核对步骤判断。

如果某份实际文本明确把标题标为标题、把约束标为声明，保留这些原文并非错误。只有它把残留文字提升为仍存在的追加指令，才构成待 graph_to_text 核对的错转或无依据新增。是否命中仍须结合真实 text_refs 与解释人工复核，不能预先给尚不存在的模型回述评分。
