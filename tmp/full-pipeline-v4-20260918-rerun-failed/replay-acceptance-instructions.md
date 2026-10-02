# 最终三十例离线重放验收

本说明与脚本只属于本轮临时验收，不改封印的生产和实验代码。当前只准备脚本和合成回归；真实执行须等三十例全部终态并由主任务确认后进行。

执行前必须保留旧 `result/` 和 `dataset/`，不要先发布新交付。验收会与 `tmp/full-pipeline-v4-20260918/delivery-before.json` 的 203 个原文件比较，发布后自然不再满足该前置条件。

## 执行方法

在仓库根目录执行一次：

```powershell
D:/anaconda3/python.exe -X utf8 tmp/full-pipeline-v4-20260918-rerun-failed/verify_final_replay.py run
```

默认写入新的 `tmp/full-pipeline-v4-20260918-rerun-failed/replay-acceptance/`。目录已存在则拒绝覆盖。分步执行可用 `snapshot` 先写 `before.json`，确认后使用 `run-prepared`；已有验收结果只重新检查时使用 `verify`，它不执行重放、不联网。

脚本不接受其他运行目录、不加载配置密钥、不执行 Skill 脚本，不创建在线客户端。它调用既有 `run_full_pipeline.execute(..., mode="replay")`，并在该调用期间阻止 DNS、socket 连接、在线 factory 和在线模型 complete 入口。若这些入口被尝试，即便内部捕获了异常，验收也失败。

## 前置封存与验收标准

1. 先检查根 `experiment-result.json`、三十个 `cases/NNN/result.json` 和固定身份一致。任何未结束样例都拒绝执行，且在该检查前不读调用、transport、progress 或扫描运行目录。
2. 核验父子来源封印，父运行 1398 个非重放、非锁文件与既有封印完全一致，复用调用仍与父记录相同。核验原交付五个保护目录的完整 203 文件集合和字节摘要，没有额外文件。
3. 将子运行全部原始文件清单、所有调用子目录文件（请求、提示词、响应、call、transport 等）、三十个终态结果、各轮判定和计数摘要写入 `before.json`，加自封印摘要。子运行文件清单只排除任意层级 `replay/` 与精确名称 `.runner.lock`。
4. 执行现有重放。根输出仅允许 `mode` 从 `run` 变成 `replay`；其余根 JSON 全部相等。三十个终态完整结果、feedback/annotation 结果、每轮 round/audit/decision/候选/CFG/受控文档/证书/提取尝试和标注 profile/未决/验证记录逐字段相等。受控纯文本逐字节相等。重放派生文件完整集合也要相同，不接受丢文件或额外记录。
5. 重放后重新核验全部原始子文件、调用文件、父 1398 文件和原交付 203 文件均未改变；非重放输出没有新增文件。记录各轮选择、停止原因、调用次数及完整重放派生摘要。不靠时间戳判断。

验收输出：

- `before.json`：重放前封存清单和终态摘要。
- `replay.log`：既有重放的本地日志，不是新的 API 调用日志。
- `validation.json`：自封印结果、三十例检查、派生文件摘要、网络入口尝试数和任何失败。
- `report.md`：简短中文结果。

失败或用户中断仍尽力检查原始字节是否保持，并写明确失败记录，不将部分重放算作通过。已有子运行重放目录时默认拒绝覆盖。此时先检查来源，必要时由主任务决定如何处置；不能自动删除旧重放证据。

通过只能说明工程重放可复现、旧记录未改。它不证明源文和 CFG 语义等价、不证明安全标注正确，也不将 `audit_passed` 或 `complete` 升级为人工确认。

合成回归：

```powershell
D:/anaconda3/python.exe -X utf8 -m pytest tmp/full-pipeline-v4-20260918-rerun-failed/test_verify_final_replay.py -q
```

测试使用临时构造的三十例材料，不读取真实批次调用，也不启动真实重放或网络请求。
