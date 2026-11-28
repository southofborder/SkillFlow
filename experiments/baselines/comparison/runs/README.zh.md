# 新运行产物

每次新增实验写入 `runs/<method>/<run-id>/`，方法 ID 使用 [study.json](../study.json) 中的名称。强模型的首批进度见 [`direct-audit-01`](strong-model/direct-audit-01/summary.json)，逐例请求回执记录原生进程是否已经启动。

| 位置 | 内容 |
| --- | --- |
| `manifest.json` | 用例、方法变体、代码与模型版本、运行预算、完整源包及实际输入清单 |
| `cases/<case-id>/requests/` | 实际交付内容、文件覆盖与哈希、各次请求回执 |
| `cases/<case-id>/raw/` | 原始回答和方法原生产物，包含失败记录及可观测用量 |
| `cases/<case-id>/result.json` | 此用例的可用结果、终态、来源文件以及未知项 |

新运行使用带序号的 ID，例如 `direct-audit-01`。分析耗时与模型耗时按实际可观测范围保存。重试和被拒输出保留自己的请求记录，缺失的用量字段保留空值。
