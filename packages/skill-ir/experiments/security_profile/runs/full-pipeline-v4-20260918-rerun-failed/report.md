# 30 个 Skill 重新提取、语义反馈与安全语义标注

本轮从冻结 Skill 源包重新提取，不采用历史 CFG。每例最多 3 次语义修复，每轮最多 3 次结构修复，随后对本轮末次结构有效图标注一次。

核对遇到可识别的暂态传输失败时，最多额外重试 2 次；语义核对轮次、执行尝试与 HTTP 尝试分别计数。完整响应、无效语义核对 JSON、未决、用户中断或状态不确定的请求不因本策略自动重发。远程阻塞读取超时为 600 秒。

核对器通过仅记为 audit_passed；其他停止状态仍明确保留。标注记录完整不保证分类正确。本轮没有进行数据传播、风险、必要性或 DOE 判断。

模式：run；反馈状态：{'audit_passed': 25, 'audit_error': 5}；标注状态：{'complete': 14, 'incomplete': 14, 'invalid_response': 1, 'execution_error': 1}。

有效保存 483 份 profile，54 条标注未决。调用计数：{'extraction_logical_calls': 66, 'audit_logical_calls': 53, 'audit_execution_calls': 54, 'audit_execution_retries': 1, 'annotation_logical_calls': 30, 'semantic_revisions': 23, 'structural_repairs': 13, 'http_attempts': 151, 'http_retries': 1, 'total_logical_calls': 149, 'total_execution_calls': 150}。

计数仅汇总已观测值，计数不完整的案例：无。未知不视为零。

| 编号／样例 | 反馈停止状态 | 选图轮次 | 标注状态 | profile 数 | 未决数 | 原因 |
|---|---|---:|---|---:|---:|---|
| 001 · N01 · 001-conditional-notification | [audit_passed](cases/001/feedback/report.md) | 0 | [complete](cases/001/annotation/report.md) | 12 | 0 | 标注记录完整；结构、操作覆盖与证据定位校验通过。 |
| 002 · N02 · 002-conditional-notification | [audit_passed](cases/002/feedback/report.md) | 1 | [complete](cases/002/annotation/report.md) | 13 | 0 | 标注记录完整；结构、操作覆盖与证据定位校验通过。 |
| 003 · N03 · 003-conditional-notification | [audit_passed](cases/003/feedback/report.md) | 1 | [complete](cases/003/annotation/report.md) | 10 | 0 | 标注记录完整；结构、操作覆盖与证据定位校验通过。 |
| 004 · N04 · 004-conditional-notification | [audit_passed](cases/004/feedback/report.md) | 2 | [complete](cases/004/annotation/report.md) | 15 | 0 | 标注记录完整；结构、操作覆盖与证据定位校验通过。 |
| 005 · N05 · 005-conditional-notification | [audit_passed](cases/005/feedback/report.md) | 1 | [complete](cases/005/annotation/report.md) | 10 | 0 | 标注记录完整；结构、操作覆盖与证据定位校验通过。 |
| 006 · N06 · 006-conditional-notification | [audit_passed](cases/006/feedback/report.md) | 1 | [complete](cases/006/annotation/report.md) | 10 | 0 | 标注记录完整；结构、操作覆盖与证据定位校验通过。 |
| 007 · Q01 · 007-catalog-query | [audit_passed](cases/007/feedback/report.md) | 1 | [incomplete](cases/007/annotation/report.md) | 8 | 2 | 保留有依据的标注，存在未决项。 |
| 008 · Q02 · 008-catalog-query | [audit_passed](cases/008/feedback/report.md) | 0 | [incomplete](cases/008/annotation/report.md) | 6 | 2 | 保留有依据的标注，存在未决项。 |
| 009 · Q03 · 009-catalog-query | [audit_passed](cases/009/feedback/report.md) | 0 | [incomplete](cases/009/annotation/report.md) | 37 | 8 | 保留有依据的标注，存在未决项。 |
| 010 · Q04 · 010-catalog-query | [audit_passed](cases/010/feedback/report.md) | 1 | [incomplete](cases/010/annotation/report.md) | 18 | 8 | 保留有依据的标注，存在未决项。 |
| 011 · Q05 · 011-catalog-query | [audit_passed](cases/011/feedback/report.md) | 0 | [incomplete](cases/011/annotation/report.md) | 12 | 5 | 保留有依据的标注，存在未决项。 |
| 012 · Q06 · 012-catalog-query | [audit_passed](cases/012/feedback/report.md) | 0 | [incomplete](cases/012/annotation/report.md) | 21 | 8 | 保留有依据的标注，存在未决项。 |
| 013 · F01 · 013-source-fetch-with-fallback | [audit_passed](cases/013/feedback/report.md) | 0 | [incomplete](cases/013/annotation/report.md) | 18 | 7 | 保留有依据的标注，存在未决项。 |
| 014 · F02 · 014-source-fetch-with-fallback | [audit_passed](cases/014/feedback/report.md) | 0 | [complete](cases/014/annotation/report.md) | 20 | 0 | 标注记录完整；结构、操作覆盖与证据定位校验通过。 |
| 015 · F03 · 015-source-fetch-with-fallback | [audit_passed](cases/015/feedback/report.md) | 0 | [incomplete](cases/015/annotation/report.md) | 20 | 3 | 保留有依据的标注，存在未决项。 |
| 016 · F04 · 016-source-fetch-with-fallback | [audit_passed](cases/016/feedback/report.md) | 0 | [complete](cases/016/annotation/report.md) | 18 | 0 | 标注记录完整；结构、操作覆盖与证据定位校验通过。 |
| 017 · F05 · 017-source-fetch-with-fallback | [audit_passed](cases/017/feedback/report.md) | 0 | [incomplete](cases/017/annotation/report.md) | 16 | 4 | 保留有依据的标注，存在未决项。 |
| 018 · F06 · 018-source-fetch-with-fallback | [audit_passed](cases/018/feedback/report.md) | 0 | [incomplete](cases/018/annotation/report.md) | 23 | 3 | 保留有依据的标注，存在未决项。 |
| 019 · D01 · 019-document-bundle-delivery | [audit_passed](cases/019/feedback/report.md) | 1 | [complete](cases/019/annotation/report.md) | 14 | 0 | 标注记录完整；结构、操作覆盖与证据定位校验通过。 |
| 020 · D02 · 020-document-bundle-delivery | [audit_passed](cases/020/feedback/report.md) | 0 | [incomplete](cases/020/annotation/report.md) | 14 | 1 | 保留有依据的标注，存在未决项。 |
| 021 · D03 · 021-document-bundle-delivery | [audit_passed](cases/021/feedback/report.md) | 1 | [complete](cases/021/annotation/report.md) | 14 | 0 | 标注记录完整；结构、操作覆盖与证据定位校验通过。 |
| 022 · D04 · 022-document-bundle-delivery | [audit_passed](cases/022/feedback/report.md) | 3 | [incomplete](cases/022/annotation/report.md) | 14 | 1 | 保留有依据的标注，存在未决项。 |
| 023 · D05 · 023-document-bundle-delivery | [audit_passed](cases/023/feedback/report.md) | 1 | [complete](cases/023/annotation/report.md) | 12 | 0 | 标注记录完整；结构、操作覆盖与证据定位校验通过。 |
| 024 · D06 · 024-document-bundle-delivery | [audit_passed](cases/024/feedback/report.md) | 2 | [complete](cases/024/annotation/report.md) | 16 | 0 | 标注记录完整；结构、操作覆盖与证据定位校验通过。 |
| 025 · R01 · 025-pdf | [audit_passed](cases/025/feedback/report.md) | 1 | [complete](cases/025/annotation/report.md) | 29 | 0 | 标注记录完整；结构、操作覆盖与证据定位校验通过。 |
| 026 · R02 · 026-playwright | [audit_error](cases/026/feedback/report.md) | 1 | [incomplete](cases/026/annotation/report.md) | 27 | 1 | 保留有依据的标注，存在未决项。 |
| 027 · R03 · 027-gh-fix-ci | [audit_error](cases/027/feedback/report.md) | 3 | [complete](cases/027/annotation/report.md) | 29 | 0 | 标注记录完整；结构、操作覆盖与证据定位校验通过。 |
| 028 · R04 · 028-netlify-deploy | [audit_error](cases/028/feedback/report.md) | 0 | [invalid_response](cases/028/annotation/report.md) | 0 | 0 | evidence quote does not match cfg location g_0070 |
| 029 · R05 · 029-linear | [audit_error](cases/029/feedback/report.md) | 1 | [execution_error](cases/029/annotation/report.md) | 0 | 0 | IncompleteRead(0 bytes read) |
| 030 · R06 · 030-transcribe | [audit_error](cases/030/feedback/report.md) | 1 | [incomplete](cases/030/annotation/report.md) | 27 | 1 | 保留有依据的标注，存在未决项。 |

每例 selection.json 记录当前末次有效图的轮次、摘要与反馈停止状态；source-binding.json 校验两个阶段的文件字节与解码文本一致。

没有有效图的案例不进行标注，不回退历史基线图。来源、配置、源码、打印器及各次响应均保留；恢复先消费已保存响应。只对已经明确以暂态传输失败结束的核对调用创建有界的新尝试，失败与重试决定分别留存。

助手逐例复核另存；本自动报告不能替代复核，不将运行或格式校验通过当成语义正确性结论。
