# Sink 边界：工程验收与三例复核

这是统一抽象运行时契约下的静态可能行为，不是执行日志。边界暴露等级不表示数据敏感度、任务必要性或 DOE 结论。

本轮代码、规范与离线验收已完成；三例真实标注得到 2 份可用 DOE 文件和 1 份格式失败记录。助手意见旁置保存，没有修改模型输出，也没有启动标注修复或 CFG 重提取。

| 样例 | 最新状态 | 已生成 sink | 审查入口 |
| --- | --- | --- | --- |
| 001 / N01 | 标注和传播完成；有网络分类问题 | model_observe × 4、network_send × 1、storage_write × 1 | [数据与边界审查](cases/001/propagation/report.html) · [DOE 原始事实](cases/001/propagation/doe-input.json) · [编译 sink 清单](cases/001/annotation/sink-boundaries.json) · [助手复核](cases/001/assistant-review.md) · [既有 CFG](cases/001/selected-analysis.json) · [标注状态与边界依据](cases/001/annotation/report.md) · [原始模型响应](cases/001/annotation/calls/annotation/a001/response.json) |
| 010 / Q04 | 标注和传播完成；有参数精度问题 | model_observe × 8、external_tool × 1、storage_write × 1 | [数据与边界审查](cases/010/propagation/report.html) · [DOE 原始事实](cases/010/propagation/doe-input.json) · [编译 sink 清单](cases/010/annotation/sink-boundaries.json) · [助手复核](cases/010/assistant-review.md) · [既有 CFG](cases/010/selected-analysis.json) · [标注状态与边界依据](cases/010/annotation/report.md) · [原始模型响应](cases/010/annotation/calls/annotation/a001/response.json) |
| 013 / F01 | 完整响应格式失败；未生成 DOE | 未生成；不能解释为无 sink | [助手复核](cases/013/assistant-review.md) · [既有 CFG](cases/013/selected-analysis.json) · [标注状态与边界依据](cases/013/annotation/report.md) · [原始模型响应](cases/013/annotation/calls/annotation/a001/response.json) |

## 助手复核：实际改善与保留问题

### 001

读取、筛选、字段准备与计数采用 default；编译得到 4 处可能模型观察。同一元素的 recipient 与 summary 通过 select_part 保持配对，count.txt 持久写入等级 1。唯一实质问题是 notify.send 仅由调用描述被标成网络发送，没有部署依据；应为可能的外部工具交付，等级仍为 2。

### 010

工具请求、取得响应和响应后的模型观察分开；index.search 为 tool/recipient/null，没有凭名称增加网络效果。来源整体及响应 total/items 原字段保持。但 ir_007 将可选参数原值与存在性旗标合成 opaque 结果，deliver 与 receive 的输入表达也不一致，不能据此作精确参数级必要性判断。

### 013

HTTP 200、SSE 完整结束、finish_reason=stop；响应末尾多余一个 }，解析报 Extra data。实际只调用一次，未修剪文本或质量补跑。来源范围、模型观察、首次/重试/回退身份、禁传和 status.txt 边界本轮未验收。0 个已解析 sink 不表示没有 sink。

## 工程与保护验收

- LocationSpec 统一保存 access_scope 与 retention；存储和上下文 retention 必填，未知接收方留存期限允许 null。Profile 保持四字段。
- 程序从 deliver/write 及编译观察生成六类 sink，不根据 roles 筛选；等级由范围与留存决定。等级 0 和删除不进入 sink 清单，但保留传播关系。
- 请求交付、工具返回、模型观察与本次保存载荷保持各自版本。sink 清单只引用已有坐标和目标，Data ID 从实际操作记录读取，不另存一份载荷。
- 运行时契约 v4、表示契约 v2、联合标注 v9、标注运行 v10、编译器 v3、传播记录 v8、DOE 输入 v6、传播运行 v9；Data 仍为 v4。旧格式明确拒绝。
- 2,426 项离线回归全部通过，覆盖固定分级、内部/持久/共享/公开边界、删除与追加、零参数工具、重复阶段、逐元素配对、清单篡改、一次修复服务及原流程回归。
- 三例在禁止网络及在线客户端创建的进程中完成零 API 重放；001/010 的 DOE 摘要不变，013 的同一失败状态重现。重放没有再次持久保存一份最终 Data。
- 旧加载器在升级前核验并冻结三例。11,319 个历史/交付文件及额外 36 个生产提取、IR、Data、核对和反馈源码检查均保持摘要一致。

浏览器自动检查因本地 file:// 策略被拒绝，未执行浏览器视觉验证。已完成离线链接、UTF-8、内容与转义检查；审查 HTML 可作为人工审计入口。

[测试记录](tests.junit.xml) · [工程验收摘要](verification.json) · [零 API 重放凭据](replay-verification.json) · [历史保护检查](preservation.json) · [调用和状态](summary.json)
