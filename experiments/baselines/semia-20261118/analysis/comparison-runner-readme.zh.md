# 后续样本受控入口

`run_comparison.py` 已完成离线核验，尚未由本实现任务启动模型。它只写新的 `comparison/010`、`comparison/013`、`comparison/ga4`；输出目录已存在就拒绝启动。原首例适配器、运行目录和官方源码保持原样。

默认只读预检：

```powershell
& .\.venv\Scripts\python.exe .\run_comparison.py --case 010 --dry-run
```

正式入口增加 `--run`，仅由 root 在首例结束、结果分析完成后调用。必须存在 `pilot/001/finished.json` 和 `analysis/001-closeout.json`；后者至少包含：

```json
{
  "status": "complete",
  "pilot_finished_sha256": "首例完成回执的实际SHA256",
  "input_manifest_sha256": "input-manifest.json的实际SHA256",
  "source_commit": "379bc25fe99833eb185efe56a38fe15f0235799c"
}
```

`status=complete` 表示分析完成，不要求首例扫描成功。首例 exit 2 等失败可以作为合法对照证据，不能为了通过此入口修改失败回执。

模型固定 `gpt-6.1-sol / high / openai`，CLI 路径与哈希绑定首例 runtime。360 个官方源文件必须与 source-manifest 和首例固定清单同时相符，额外源码文件、哈希漂移、从其他位置导入的 Semia 模块均拒绝。输入清单也绑定首例哈希，文件数量、路径、字节和长度均核验。完整输入 helper 从明确文件路径加载，其哈希必须等于已通过离线验证的 `analysis/full-source-preflight/manifest.json`。

版本名称为 `semia-379bc25f-controlled-complete-source-v1`。文件纳入适配只补充官方默认过滤的两个已固定 GA4 metadata 文件；保留官方提示词、SDL、checker、合成循环、检测与推荐。每次发起原生请求前，还会检查实际发送的 source fence 内确实包含完整 prepared 正文，并绑定 prepare receipt。推荐提示自带的额外终止换行不改变内容。

算法预算为 5 iterations、每轮 3 次结构重试、每请求 2 次 provider error retry，原生每次 deadline 2700 秒。scan 默认还包含一次最终 recommendation。因此限制为 CGRS 最多 60 次原生开始、recommendation 最多 3 次，总计 63；按两个阶段分别记账。上游 retry 捕获所有 `LlmSynthesisError`（配置错误除外），不能只称为网络重试。首例已冻结的硬限制为60；是否实际受影响必须按原始回执判断。

`transport/call-NNN` 保存实际 argv、prompt、response、公开 stdout/stderr、用量及错误。未知用量保留 null；超时尝试清理本次子进程树，未能确认进程退出时以不重试的配置错误结束。`validations/check-NNN` 保存实际提交 facts、详细检查文件、返回 payload 和调用状态；若 checker 异常，明确指出共享检查文件可能来自之前一次，而不是当作本次新诊断。

推荐失败在上游是非致命状态，最终 exit 0 也不能单独证明推荐成功；读取 `finished.json` 的 `recommendation_completed`、各阶段启动数、完整性和工具事件计数，以及 `console-stderr.txt`。没有独立 gold 标签，精确率/召回率保持未评估。

验证记录：[comparison-runner-check.json](comparison-runner-check.json) 为13项 mock检查全部通过，覆盖成功透传、实际payload缺行拒绝、prepared篡改拒绝、非零退出、缺响应、启动失败、timeout清理和未退出拒绝重试、未知用量、工具活动拒绝、推荐阶段预算、首例失败+绑定分析标记，以及源文件漂移/本地重新固定拒绝。此处超时测试使用伪进程，未执行真实模型或真实杀进程。一次测试代码插入位置导致的 NameError 保留在 `comparison-runner-tests-20261118T083453849470Z.log`；随后修复，最终回执通过。

三例预检结果见 [comparison-preflight.json](comparison-preflight.json)。当前没有新比较模型调用；实际启动状态以后续目录机器回执为准。
