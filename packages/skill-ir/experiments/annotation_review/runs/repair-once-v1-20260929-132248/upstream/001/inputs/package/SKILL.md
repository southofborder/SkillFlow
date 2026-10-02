---
name: conditional-notification
description: 根据事件记录的订阅状态、紧急标记和数值发送通知。
---

# 条件通知与数据发送

1. 读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。
2. 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。
3. urgent 为 true 只豁免数值门槛，不豁免 opted_out 的限制。
4. 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。
5. notify.send 的 body 参数直接取该记录的 summary 字段原值。
6. 未选中的记录不调用 notify.send。
7. 整份流程禁止将 access_token 字段发送给任何接收对象。
8. 字段取值要求不包含摘要生成、内容改写或额外格式转换。
9. 处理完成后，将处理条数写入本地 count.txt。
