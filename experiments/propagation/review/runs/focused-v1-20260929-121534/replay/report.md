# 联合标注三任务聚焦审查：七例验证

每例一次旁置审查，不改标注、不启动传播或自动修复。空问题清单不证明语义正确，IR 覆盖仅表示模型声明检查过。

| 案例 | 执行状态 | 审查摘要 | 问题 / 未决 | 逻辑调用 | 材料 |
|---|---|---|---:|---:|---|
| 001-base | complete | 未发现实质问题 | 0 / 0 | 1 | [问题与依据](../cases/001-base/report.html) · [Markdown](../cases/001-base/report.md) · [原始审查结果](../cases/001-base/result.json) · [材料与定位索引](../cases/001-base/inputs/material.json) |
| 010-base | complete | 有明确问题 | 1 / 0 | 1 | [问题与依据](../cases/010-base/report.html) · [Markdown](../cases/010-base/report.md) · [原始审查结果](../cases/010-base/result.json) · [材料与定位索引](../cases/010-base/inputs/material.json) |
| 013-base | complete | 未发现实质问题 | 0 / 0 | 1 | [问题与依据](../cases/013-base/report.html) · [Markdown](../cases/013-base/report.md) · [原始审查结果](../cases/013-base/result.json) · [材料与定位索引](../cases/013-base/inputs/material.json) |
| 013-local | execution_error | — | 0 / 0 | 1 | [问题与依据](../cases/013-local/report.html) · [Markdown](../cases/013-local/report.md) · [原始审查结果](../cases/013-local/result.json) · [材料与定位索引](../cases/013-local/inputs/material.json) |
| 013-field | complete | 有明确问题 | 1 / 0 | 1 | [问题与依据](../cases/013-field/report.html) · [Markdown](../cases/013-field/report.md) · [原始审查结果](../cases/013-field/result.json) · [材料与定位索引](../cases/013-field/inputs/material.json) |
| 010-source | complete | 有明确问题 | 2 / 0 | 1 | [问题与依据](../cases/010-source/report.html) · [Markdown](../cases/010-source/report.md) · [原始审查结果](../cases/010-source/result.json) · [材料与定位索引](../cases/010-source/inputs/material.json) |
| 001-version | complete | 有明确问题 | 1 / 0 | 1 | [问题与依据](../cases/001-version/report.html) · [Markdown](../cases/001-version/report.md) · [原始审查结果](../cases/001-version/result.json) · [材料与定位索引](../cases/001-version/inputs/material.json) |

001-base：聚焦审查响应的格式、定位、引文和声明覆盖校验通过。
010-base：聚焦审查响应的格式、定位、引文和声明覆盖校验通过。
013-base：聚焦审查响应的格式、定位、引文和声明覆盖校验通过。
013-local：IncompleteRead(0 bytes read)
013-field：聚焦审查响应的格式、定位、引文和声明覆盖校验通过。
010-source：聚焦审查响应的格式、定位、引文和声明覆盖校验通过。
001-version：聚焦审查响应的格式、定位、引文和声明覆盖校验通过。

三类关注点：无依据缩小；关系丢失或虚构；观察和交付的数据版本、参数、边界与逐元素配对。

[外置预期](../evaluation/expectations.json) · [定位候选匹配](evaluation/locator-matching.json) · [助手方法复核](../assistant-review.md)

定位候选匹配不能代替语义评测。三个原结果不预设零问题；额外发现由助手复核，不能自动记为误报。
