# 001 通知正文扩大候选：助手复核

**确认真实命中。**唯一发现 `f_ir005_deliver_body_argument` 的 ann_0120 精确定位到 deliver.inputs[1]：它引用整个当前元素 record，而不是前面已经选出的 summary_value。

接收者和正文仍在同一个 for_each 元素作用域，配对没有破坏。错误在正文的数据身份和范围：从该记录的 summary 原值扩大成整条记录。这与源文明示的实际参数及禁止发送 access_token 的限制不一致。

审查建议引用现有 summary_value，保留 recipient_value，当前定义次序与作用域均支持这一修改，不需要新增操作或猜测字段。本轮没有执行修复。

关于 access_token 的说明限于候选标注的静态内容范围；没有执行 Skill、没有读取真实记录，也没有证明真实泄露发生。本例没有额外独立发现。
