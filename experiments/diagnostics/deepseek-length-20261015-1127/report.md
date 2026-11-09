# DeepSeek 短／长输入对照：2026-10-15

本轮是用户明确要求的独立连接重试，不是正式标注实验。没有改动生产配置、源码或三例历史运行。

## 测试条件

两个请求并行发出，使用相同官方接口、密钥、`deepseek-v4-flash`、`reasoning_effort=max`、JSON Output 与 SSE。均只要求输出 `{"ok":true}`；长输入增加约 10 万字符的合成无业务意义数据，以分离输入规模与业务分析复杂度。合成数据不等于真实 SkillFlow Prompt，字符数也不是 token 数。

| 输入 | 字符数 | HTTP 头 | 首个推理／正文事件 | 实际观察时长 | 收到内容 |
|---|---:|---|---|---:|---|
| 短 | 101 | 200，1.485 秒 | 无 | 121.766 秒 | 10 条 keep-alive，0 个数据事件 |
| 长 | 100,163 | 200，1.922 秒 | 无 | 122.047 秒 | 10 条 keep-alive，0 个数据事件 |

诊断窗口设为 120 秒，在收到下一条保活后关闭连接，实际约 122 秒。这是本地诊断停止，不是服务端超时，也不是生产请求的新增上限。两个请求都没有正文、推理内容、finish_reason、DONE 或 usage。

## 原因证据

[官方故障事件](https://status.deepseek.com/incidents/7116348214287)公布：2026-10-15 00:11 UTC（北京 08:11）起网页/API 部分中断；01:08 UTC（北京 09:08）更新为已定位原因、正在修复。本次查询仍为 Identified，Flash 与 Pro API 均受影响。先前三例北京时间 10:23–10:54 和本次对照均在该已公布故障窗口内。

这为先前 503、900 秒内未开始处理以及当前长短输入均只有保活提供了直接的服务状态证据。不能将本次失败归因于长输入、JSON 校验或项目语义，也不能由此证明长输入永远没有延迟或预算问题。

官方仍接受旧模型别名；`max` 和 JSON Output 均为受支持请求参数。没有实际模型事件，因此实际返回模型身份未知。

## 调用和后续

本轮 2 次逻辑生成请求、2 次 HTTP 尝试、0 次自动重试。两次 usage 都缺失，token 消耗未知，不记为零。

服务恢复后，先确认短请求能返回完整结果，再进行同参数长输入对照；若只有长输入失败，再分别检查输入长度、输出预算和业务复杂度。当前不重跑完整三例，也不放宽项目校验。

[统计 JSON](summary.json) · [短请求记录](short/result.json) · [长请求记录](long/result.json)

官方参考：[状态页](https://status.deepseek.com/)、[模型与别名](https://api-docs.deepseek.com/quick_start/pricing/)、[请求参数](https://api-docs.deepseek.com/api/create-chat-completion/)、[保活机制](https://api-docs.deepseek.com/quick_start/rate_limit/)
