# 013 / F01 助手复核

**调用在DNS解析阶段失败；无可接受profile、无部分模型内容，无法评价安全标注漏标或误标。**

此记录是助手事后复核，未冒充用户确认。源文和图已读完；标注质量因没有有效响应而不可评价。

- 状态：`execution_error`；校验：`not_run`。
- 逻辑调用：1；HTTP尝试：3；HTTP重试：2。
- HTTP 200：无；响应头：无；接收字节：0；部分响应：无；实际返回模型名及用量：未获得。
- 原因：`LLM SSE network failure: <urlopen error [Errno 11002] getaddrinfo failed>`。

## 已阅读的输入与核查重点

- 已读 F01 完整源文与28条IR：ir_001/003分别读取请求和环境，ir_007/015/021为首次、重试和archive工具调用。
- 工具结果回传可按EM02讨论模型观察，工具名称不证明net_send/net_receive；读取环境也不能自行列举其他密钥或传播集合。
- ir_011/019/025/027有实际status.txt追加；密钥禁传只是约束，不能当成已执行脱敏。ir_012/020/026/028为普通return，纯dispatch与存在性/成功性计算需区分。

## 判定边界

本例的 `profiles: {}` 表示调用未获得标注，不是每条IR被判断为没有actor、roles或effects。没有模型响应可以用来裁决漏标、误标、网络双向效果、隐含模型观察或保护操作分类；上述重点只是已阅读输入后确定的复核位置。

未执行Skill或脚本，未计算传播结果，未判断风险、泄露或必要性，未补跑。

证据：[结果](result.json) · [原始调用](calls/annotation/a001/call.json) · [传输记录](calls/annotation/a001/transport.json) · [完整源文](inputs/source.json) · [实际图](inputs/cfg.json)
