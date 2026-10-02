# 本轮暂停与执行错误说明

用户要求暂停后，本地批处理进程已停止，未继续启动调用。暂停状态见 [pause-state.json](pause-state.json)。本说明只依据已保存记录，没有重新调用 API。

## 已确认的四例执行错误

这里的执行错误表示某个分析阶段未取得可用的完整模型响应，不表示执行 Skill 失败；实验没有执行 Skill 中的脚本或工具。具体状态中的 extraction/audit 表示失败发生在提取/语义核对阶段。

| 案例 | 出错阶段与状态 | 具体原因 | 已保存结果的边界 |
|---|---|---|---|
| 003 / N03 | 第 0 轮核对；audit_error | HTTP 200 后响应流未完整结束，IncompleteRead(0 bytes read) | 本次第 0 轮 CFG 结构及保真检查通过；没有完成语义核对；该图的安全标注随后 complete |
| 004 / N04 | 第 1 轮核对；audit_error | 3 次传输尝试均 getaddrinfo failed，未获得 HTTP 状态 | 第一轮修复 CFG 已生成，含一次成功的结构修复；尚未完成对修复图的语义复核；安全标注 complete |
| 005 / N05 | 第 1 轮重新提取；extraction_error | 3 次传输尝试均 getaddrinfo failed，未获得 HTTP 状态 | 修复图没有生成；标注使用本次第 0 轮图，已知差异仍保留；安全标注 complete |
| 006 / N06 | 第 1 轮重新提取；extraction_error | 3 次传输尝试均 getaddrinfo failed，未获得 HTTP 状态 | 修复图没有生成；标注使用本次第 0 轮图，已知差异仍保留；安全标注 complete |

003 的单次 HTTP 尝试已收到 1,204,055 字节、3,823 个 SSE 事件，但 done_received=false、finish_reason=null，没有完整核对答案。因此错误文字中的“0 bytes read”不等于整次请求零接收。记录保留接受后的失败，没有自动重新发送。

004–006 的失败集中在北京时间 2026-09-17 21:47:13 至 21:47:40。错误码包括 Windows 11002 和 11001，均发生在地址解析阶段；三例的失败尝试均无 HTTP 状态、接收零字节。随后重新检查时域名已能解析，三例的独立安全标注调用也最终完成。这支持间歇性解析/连接问题的判断，但不足以确定具体是本机 DNS、代理或上游网络导致。没有改变系统 DNS、代理或模型配置。

## 与其他状态的区别

- audit_passed：有效语义核对记录满足通过条件，不是语义等价证明。
- revise：核对已完成，发现明确差异，要求再提取；属于模型语义判断。
- unresolved：核对已完成，只剩不能裁决的项，按规则停止；不是网络错误。
- audit_error / extraction_error：相应阶段执行失败；本次四例具体是流读取或地址解析失败，未形成该阶段的有效判断/新图。
- 标注 complete / incomplete：四字段覆盖与证据格式校验通过，分别表示没有/存在标注未决；不能替代上游 CFG 语义核对结果。

## 暂停时的进度

已完整保存两个阶段终态的案例为 001–006、008，共 7 例，86 条合法 profile、1 项模型标注未决。007、009 在第 2 轮重新提取过程中暂停；010 在安全标注过程中暂停。三项未结束调用仍保留原始 running 记录，并由 pause-state.json 另外标记本地进程已停止、远端结果未知，没有把暂停改写成上述四例传输错误。011–030 尚未开始。

未修改原始调用记录、模型结果或已有历史产物。后续保持暂停，不自动重启或重发这些请求。

## 原始证据

- [003 调用记录](cases/003/feedback/calls/r000/audit/a001/call.json) · [传输记录](cases/003/feedback/calls/r000/audit/a001/transport.json)
- [004 调用记录](cases/004/feedback/calls/r001/audit/a001/call.json) · [传输记录](cases/004/feedback/calls/r001/audit/a001/transport.json)
- [005 调用记录](cases/005/feedback/calls/r001/extraction/a001/call.json) · [传输记录](cases/005/feedback/calls/r001/extraction/a001/transport.json)
- [006 调用记录](cases/006/feedback/calls/r001/extraction/a001/call.json) · [传输记录](cases/006/feedback/calls/r001/extraction/a001/transport.json)
