# 执行中复核笔记（不是最终验收结论）

仅查看已完成且不再改写的阶段产物；最终意见必须核对最后选中图及对应标注。

## 001 / N01

已阅读完整原文与 r000/cfg.json：用户 events.json 来源和七字段声明保留；opted_out 必须非真且 urgent 或 value>=100 的筛选规则位于实际 evaluate 操作约束；循环只为选中记录调用 notify.send，recipient/summary 各有结果引用，未补造摘要或遮蔽；access_token 禁传是声明；处理后计数写 count.txt。不将处理条数强行解释为已发送条数。初轮核对器 8 项业务保留，暂无关键漏转证据。安全标注尚未完成，不能先判正确。

## 002 / N02

r000 finding_2 指出记录模式中未显式记录 record_id，触发 r001。该字段虽不参与 body，但属于源文给定容器结构，保留它可用于未来二次传播的输入边界；这不是证明 record_id 已暴露。

## 003 / N03

r000 finding_2 的用户来源和记录字段模式遗漏有实际依据。finding_5 仅因 opcode notify_send 与 notify.send 的拼写不同判 internal_conflict，疑似过度严格的命名误报：block_003 名称为 Send one notify.send call for each selected record；ir_005 资源为 notify，同操作约束明确逐条调用 notify.send、recipient 和 summary 参数绑定。开放 opcode 允许合理抽象，不应仅凭点号/下划线判矛盾。这个问题影响反馈可信度及额外重提取成本，未证明业务行为存在冲突。原始模型判断必须保留，复核独立记载。
