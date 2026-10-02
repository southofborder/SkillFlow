# 30 个 Skill 重新提取、语义反馈与安全语义标注

本轮从冻结 Skill 源包重新提取，不采用历史 CFG。每例最多 3 次语义修复，每轮最多 3 次结构修复，随后对本轮末次结构有效图标注一次。

核对遇到可识别的暂态传输失败时，最多额外重试 2 次；语义核对轮次、执行尝试与 HTTP 尝试分别计数。完整响应、无效语义核对 JSON、未决、用户中断或状态不确定的请求不因本策略自动重发。远程阻塞读取超时为 600 秒。

核对器通过仅记为 audit_passed；其他停止状态仍明确保留。标注记录完整不保证分类正确。本轮没有进行数据传播、风险、必要性或 DOE 判断。

模式：replay；反馈状态：{'audit_passed': 15, 'audit_error': 4, 'extraction_error': 11}；标注状态：{'complete': 8, 'incomplete': 9, 'execution_error': 3, 'not_run': 10}。

有效保存 267 份 profile，47 条标注未决。调用计数：{'extraction_logical_calls': 40, 'audit_logical_calls': 29, 'audit_execution_calls': 33, 'audit_execution_retries': 4, 'annotation_logical_calls': 20, 'semantic_revisions': 10, 'structural_repairs': 0, 'http_attempts': 128, 'http_retries': 35, 'total_logical_calls': 89, 'total_execution_calls': 93}。

计数仅汇总已观测值，计数不完整的案例：无。未知不视为零。

| 编号／样例 | 反馈停止状态 | 选图轮次 | 标注状态 | profile 数 | 未决数 | 原因 |
|---|---|---:|---|---:|---:|---|
| 001 · N01 · 001-conditional-notification | [audit_passed](../cases/001/feedback/replay/report.md) | 0 | [complete](../cases/001/annotation/replay/report.md) | 12 | 0 | 标注记录完整；结构、操作覆盖与证据定位校验通过。 |
| 002 · N02 · 002-conditional-notification | [audit_passed](../cases/002/feedback/replay/report.md) | 1 | [complete](../cases/002/annotation/replay/report.md) | 13 | 0 | 标注记录完整；结构、操作覆盖与证据定位校验通过。 |
| 003 · N03 · 003-conditional-notification | [audit_passed](../cases/003/feedback/replay/report.md) | 1 | [complete](../cases/003/annotation/replay/report.md) | 10 | 0 | 标注记录完整；结构、操作覆盖与证据定位校验通过。 |
| 004 · N04 · 004-conditional-notification | [audit_passed](../cases/004/feedback/replay/report.md) | 2 | [complete](../cases/004/annotation/replay/report.md) | 15 | 0 | 标注记录完整；结构、操作覆盖与证据定位校验通过。 |
| 005 · N05 · 005-conditional-notification | [audit_passed](../cases/005/feedback/replay/report.md) | 1 | [complete](../cases/005/annotation/replay/report.md) | 10 | 0 | 标注记录完整；结构、操作覆盖与证据定位校验通过。 |
| 006 · N06 · 006-conditional-notification | [audit_passed](../cases/006/feedback/replay/report.md) | 1 | [complete](../cases/006/annotation/replay/report.md) | 10 | 0 | 标注记录完整；结构、操作覆盖与证据定位校验通过。 |
| 007 · Q01 · 007-catalog-query | [audit_passed](../cases/007/feedback/replay/report.md) | 1 | [incomplete](../cases/007/annotation/replay/report.md) | 8 | 2 | 保留有依据的标注，存在未决项。 |
| 008 · Q02 · 008-catalog-query | [audit_error](../cases/008/feedback/replay/report.md) | 0 | [incomplete](../cases/008/annotation/replay/report.md) | 17 | 2 | 保留有依据的标注，存在未决项。 |
| 009 · Q03 · 009-catalog-query | [audit_error](../cases/009/feedback/replay/report.md) | 1 | [incomplete](../cases/009/annotation/replay/report.md) | 29 | 8 | 保留有依据的标注，存在未决项。 |
| 010 · Q04 · 010-catalog-query | [audit_passed](../cases/010/feedback/replay/report.md) | 1 | [incomplete](../cases/010/annotation/replay/report.md) | 18 | 8 | 保留有依据的标注，存在未决项。 |
| 011 · Q05 · 011-catalog-query | [audit_passed](../cases/011/feedback/replay/report.md) | 0 | [incomplete](../cases/011/annotation/replay/report.md) | 12 | 5 | 保留有依据的标注，存在未决项。 |
| 012 · Q06 · 012-catalog-query | [audit_passed](../cases/012/feedback/replay/report.md) | 0 | [incomplete](../cases/012/annotation/replay/report.md) | 21 | 8 | 保留有依据的标注，存在未决项。 |
| 013 · F01 · 013-source-fetch-with-fallback | [audit_passed](../cases/013/feedback/replay/report.md) | 0 | [incomplete](../cases/013/annotation/replay/report.md) | 18 | 7 | 保留有依据的标注，存在未决项。 |
| 014 · F02 · 014-source-fetch-with-fallback | [audit_passed](../cases/014/feedback/replay/report.md) | 0 | [complete](../cases/014/annotation/replay/report.md) | 20 | 0 | 标注记录完整；结构、操作覆盖与证据定位校验通过。 |
| 015 · F03 · 015-source-fetch-with-fallback | [audit_passed](../cases/015/feedback/replay/report.md) | 0 | [incomplete](../cases/015/annotation/replay/report.md) | 20 | 3 | 保留有依据的标注，存在未决项。 |
| 016 · F04 · 016-source-fetch-with-fallback | [audit_passed](../cases/016/feedback/replay/report.md) | 0 | [complete](../cases/016/annotation/replay/report.md) | 18 | 0 | 标注记录完整；结构、操作覆盖与证据定位校验通过。 |
| 017 · F05 · 017-source-fetch-with-fallback | [audit_passed](../cases/017/feedback/replay/report.md) | 0 | [incomplete](../cases/017/annotation/replay/report.md) | 16 | 4 | 保留有依据的标注，存在未决项。 |
| 018 · F06 · 018-source-fetch-with-fallback | [extraction_error](../cases/018/feedback/replay/report.md) | 0 | [execution_error](../cases/018/annotation/replay/report.md) | 0 | 0 | LLM SSE network failure: <urlopen error [Errno 11001] getaddrinfo failed> |
| 019 · D01 · 019-document-bundle-delivery | [audit_error](../cases/019/feedback/replay/report.md) | 0 | [execution_error](../cases/019/annotation/replay/report.md) | 0 | 0 | LLM SSE network failure: <urlopen error [Errno 11001] getaddrinfo failed> |
| 020 · D02 · 020-document-bundle-delivery | [audit_error](../cases/020/feedback/replay/report.md) | 0 | [execution_error](../cases/020/annotation/replay/report.md) | 0 | 0 | LLM SSE network failure: <urlopen error [Errno 11001] getaddrinfo failed> |
| 021 · D03 · 021-document-bundle-delivery | [extraction_error](../cases/021/feedback/replay/report.md) | 无 | not_run | 0 | 0 | 本次反馈流程没有结构有效图；不回退历史 CFG |
| 022 · D04 · 022-document-bundle-delivery | [extraction_error](../cases/022/feedback/replay/report.md) | 无 | not_run | 0 | 0 | 本次反馈流程没有结构有效图；不回退历史 CFG |
| 023 · D05 · 023-document-bundle-delivery | [extraction_error](../cases/023/feedback/replay/report.md) | 无 | not_run | 0 | 0 | 本次反馈流程没有结构有效图；不回退历史 CFG |
| 024 · D06 · 024-document-bundle-delivery | [extraction_error](../cases/024/feedback/replay/report.md) | 无 | not_run | 0 | 0 | 本次反馈流程没有结构有效图；不回退历史 CFG |
| 025 · R01 · 025-pdf | [extraction_error](../cases/025/feedback/replay/report.md) | 无 | not_run | 0 | 0 | 本次反馈流程没有结构有效图；不回退历史 CFG |
| 026 · R02 · 026-playwright | [extraction_error](../cases/026/feedback/replay/report.md) | 无 | not_run | 0 | 0 | 本次反馈流程没有结构有效图；不回退历史 CFG |
| 027 · R03 · 027-gh-fix-ci | [extraction_error](../cases/027/feedback/replay/report.md) | 无 | not_run | 0 | 0 | 本次反馈流程没有结构有效图；不回退历史 CFG |
| 028 · R04 · 028-netlify-deploy | [extraction_error](../cases/028/feedback/replay/report.md) | 无 | not_run | 0 | 0 | 本次反馈流程没有结构有效图；不回退历史 CFG |
| 029 · R05 · 029-linear | [extraction_error](../cases/029/feedback/replay/report.md) | 无 | not_run | 0 | 0 | 本次反馈流程没有结构有效图；不回退历史 CFG |
| 030 · R06 · 030-transcribe | [extraction_error](../cases/030/feedback/replay/report.md) | 无 | not_run | 0 | 0 | 本次反馈流程没有结构有效图；不回退历史 CFG |

每例 selection.json 记录当前末次有效图的轮次、摘要与反馈停止状态；source-binding.json 校验两个阶段的文件字节与解码文本一致。

没有有效图的案例不进行标注，不回退历史基线图。来源、配置、源码、打印器及各次响应均保留；恢复先消费已保存响应。只对已经明确以暂态传输失败结束的核对调用创建有界的新尝试，失败与重试决定分别留存。

助手逐例复核另存；本自动报告不能替代复核，不将运行或格式校验通过当成语义正确性结论。
