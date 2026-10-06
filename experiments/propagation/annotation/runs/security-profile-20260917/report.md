# 30 图 Security Profile 首次标注

输入采用已冻结的 30 个 Skill 和既有选定 CFG：29 个第 1 轮，F03 第 3 轮。每例一次独立逻辑标注调用。

标注只描述动作的 actor、roles、effects 和 evidences；本轮不传播数据，不判断风险、必要性或 DOE。

## 执行概况

模式：run；案例数：30；状态分布：{'complete': 6, 'execution_error': 19, 'incomplete': 3, 'invalid_response': 2}。

有效保存的 profile 数：170；未决记录：7；已知调用计数：{'logical_calls': 30, 'http_attempts': 62, 'http_retries': 32}。

计数只汇总已保存的观测值；缺少调用计数的案例不按零调用认定：无。

## 逐例结果

| 编号／样例 | 原轮次 | 状态 | profile／IR | 未决 | 原因 |
|---|---:|---|---:|---:|---|
| [001 · N01 · 001-conditional-notification ](cases/001/report.md) | 1 | 标注记录完整 | 13/13 | 0 | 标注记录完整；结构、操作覆盖与证据定位校验通过。 |
| [002 · N02 · 002-conditional-notification ](cases/002/report.md) | 1 | 执行错误 | 0/13 | 0 | LLM SSE network failure: [WinError 5] 拒绝访问。: 'D:\\projects\\SkillFlow\\packages\\skill-ir\\experiments\\security_profile\\runs\\security-profile-20260917\\cases\\002\\calls\\annotation\\a001\\.transport.json.32abc823de49429cba7ef16c9e845037.tmp' -> 'D:\\projects\\SkillFlow\\packages\\skill-ir\\experiments\\security_profile\\runs\\security-profile-20260917\\cases\\002\\calls\\annotation\\a001\\transport.json' |
| [003 · N03 · 003-conditional-notification ](cases/003/report.md) | 1 | 标注记录完整 | 12/12 | 0 | 标注记录完整；结构、操作覆盖与证据定位校验通过。 |
| [004 · N04 · 004-conditional-notification ](cases/004/report.md) | 1 | 执行错误 | 0/16 | 0 | IncompleteRead(0 bytes read) |
| [005 · N05 · 005-conditional-notification ](cases/005/report.md) | 1 | 执行错误 | 0/11 | 0 | IncompleteRead(0 bytes read) |
| [006 · N06 · 006-conditional-notification ](cases/006/report.md) | 1 | 执行错误 | 0/12 | 0 | IncompleteRead(0 bytes read) |
| [007 · Q01 · 007-catalog-query ](cases/007/report.md) | 1 | 执行错误 | 0/12 | 0 | LLM SSE network failure: <urlopen error [Errno 11001] getaddrinfo failed> |
| [008 · Q02 · 008-catalog-query ](cases/008/report.md) | 1 | 执行错误 | 0/16 | 0 | LLM SSE network failure: <urlopen error [Errno 11001] getaddrinfo failed> |
| [009 · Q03 · 009-catalog-query ](cases/009/report.md) | 1 | 执行错误 | 0/17 | 0 | LLM SSE network failure: <urlopen error [Errno 11001] getaddrinfo failed> |
| [010 · Q04 · 010-catalog-query ](cases/010/report.md) | 1 | 执行错误 | 0/29 | 0 | LLM SSE network failure: <urlopen error [Errno 11001] getaddrinfo failed> |
| [011 · Q05 · 011-catalog-query ](cases/011/report.md) | 1 | 执行错误 | 0/17 | 0 | LLM SSE network failure: <urlopen error [Errno 11001] getaddrinfo failed> |
| [012 · Q06 · 012-catalog-query ](cases/012/report.md) | 1 | 执行错误 | 0/22 | 0 | LLM SSE network failure: <urlopen error [Errno 11002] getaddrinfo failed> |
| [013 · F01 · 013-source-fetch-with-fallback ](cases/013/report.md) | 1 | 执行错误 | 0/28 | 0 | LLM SSE network failure: <urlopen error [Errno 11002] getaddrinfo failed> |
| [014 · F02 · 014-source-fetch-with-fallback ](cases/014/report.md) | 1 | 执行错误 | 0/20 | 0 | LLM SSE network failure: <urlopen error [Errno 11001] getaddrinfo failed> |
| [015 · F03 · 015-source-fetch-with-fallback ](cases/015/report.md) | 3 | 执行错误 | 0/22 | 0 | LLM SSE network failure: <urlopen error [Errno 11001] getaddrinfo failed> |
| [016 · F04 · 016-source-fetch-with-fallback ](cases/016/report.md) | 1 | 执行错误 | 0/18 | 0 | LLM SSE network failure: <urlopen error [Errno 11001] getaddrinfo failed> |
| [017 · F05 · 017-source-fetch-with-fallback ](cases/017/report.md) | 1 | 执行错误 | 0/16 | 0 | LLM SSE network failure: <urlopen error [Errno 11001] getaddrinfo failed> |
| [018 · F06 · 018-source-fetch-with-fallback ](cases/018/report.md) | 1 | 执行错误 | 0/20 | 0 | LLM SSE network failure: <urlopen error [Errno 11001] getaddrinfo failed> |
| [019 · D01 · 019-document-bundle-delivery ](cases/019/report.md) | 1 | 执行错误 | 0/14 | 0 | LLM SSE network failure: <urlopen error [Errno 11001] getaddrinfo failed> |
| [020 · D02 · 020-document-bundle-delivery ](cases/020/report.md) | 1 | 标注记录完整 | 14/14 | 0 | 标注记录完整；结构、操作覆盖与证据定位校验通过。 |
| [021 · D03 · 021-document-bundle-delivery ](cases/021/report.md) | 1 | 执行错误 | 0/14 | 0 | IncompleteRead(0 bytes read) |
| [022 · D04 · 022-document-bundle-delivery ](cases/022/report.md) | 1 | 标注记录完整 | 14/14 | 0 | 标注记录完整；结构、操作覆盖与证据定位校验通过。 |
| [023 · D05 · 023-document-bundle-delivery ](cases/023/report.md) | 1 | 标注记录完整 | 12/12 | 0 | 标注记录完整；结构、操作覆盖与证据定位校验通过。 |
| [024 · D06 · 024-document-bundle-delivery ](cases/024/report.md) | 1 | 标注记录完整 | 16/16 | 0 | 标注记录完整；结构、操作覆盖与证据定位校验通过。 |
| [025 · R01 · 025-pdf ](cases/025/report.md) | 1 | 存在未决 | 45/45 | 4 | 保留有依据的标注，存在未决项。 |
| [026 · R02 · 026-playwright ](cases/026/report.md) | 1 | 存在未决 | 22/22 | 2 | 保留有依据的标注，存在未决项。 |
| [027 · R03 · 027-gh-fix-ci ](cases/027/report.md) | 1 | 执行错误 | 0/28 | 0 | IncompleteRead(0 bytes read) |
| [028 · R04 · 028-netlify-deploy ](cases/028/report.md) | 1 | 响应无效 | 0/40 | 0 | evidence quote does not match source location src_062 |
| [029 · R05 · 029-linear ](cases/029/report.md) | 1 | 响应无效 | 0/62 | 0 | evidence quote does not match source location src_047 |
| [030 · R06 · 030-transcribe ](cases/030/report.md) | 1 | 存在未决 | 22/22 | 1 | 保留有依据的标注，存在未决项。 |

## 效果分布

一条 IR 可具有多个 effects；以下为各标签对应的 IR 数，不是数据量或风险分数。

| effect | IR 数 |
|---|---:|
| context_read | 17 |
| fs_read | 20 |
| fs_write | 27 |
| net_send | 5 |
| net_receive | 3 |
| model_observe | 32 |
| user_output | 7 |
| transform | 41 |

## 复核边界

程序只验证四字段契约、ID 覆盖、定位和引文。complete 表示标注记录完整，不保证模型的分类或推断正确。

助手已完成 30 例源图与运行记录复核，其中 9 例存在可接受标注。意见单独保存于 [assistant-review.md](assistant-review.md)，实施验收见 [acceptance.md](acceptance.md)。模型输出保持原样，尚未由用户确认。

源包内的可读代码只作为文本提供，没有执行。二进制及未解释内容边界见逐例记录。
