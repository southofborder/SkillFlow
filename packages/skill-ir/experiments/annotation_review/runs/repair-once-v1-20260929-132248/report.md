# 一次标注修复与 CFG 核对

新实验保留七份重建候选及各次真实响应；未执行 Skill，不作 DOE 判断。

已记录逻辑调用：17 / 24。

| 案例 | 闭环状态 | 初审问题 | 复审问题 | 选定候选 | 传播 | 调用 |
|---|---|---:|---:|---|---|---:|
| [001-base](cases/001-base/refinement/report.md) | review_passed | 0 | None | original | complete | 1 |
| [010-base](cases/010-base/refinement/report.md) | review_passed | 0 | None | original | complete | 1 |
| [013-base](cases/013-base/refinement/report.md) | review_passed | 0 | None | original | complete | 1 |
| [013-local](cases/013-local/refinement/report.md) | review_passed | 1 | 0 | repair | complete | 3 |
| [013-field](cases/013-field/refinement/report.md) | review_passed | 1 | 0 | repair | complete | 3 |
| [010-source](cases/010-source/refinement/report.md) | execution_error | 1 | None | original | complete | 2 |
| [001-version](cases/001-version/refinement/report.md) | review_passed | 1 | 0 | repair | complete | 3 |

## CFG 单次核对

- 001：audit_passed，1 次调用。
- 010：audit_passed，1 次调用。
- 013：audit_passed，1 次调用。

## 各例停止原因

- 001-base：初审未发现实质问题；未调用修复。；传播诊断：无
- 010-base：初审未发现实质问题；未调用修复。；传播诊断：无
- 013-base：初审未发现实质问题；未调用修复。；传播诊断：无
- 013-local：一次修复后独立复审未发现实质问题。；传播诊断：无
- 013-field：一次修复后独立复审未发现实质问题。；传播诊断：无
- 010-source：IncompleteRead(0 bytes read)；传播诊断：无
- 001-version：一次修复后独立复审未发现实质问题。；传播诊断：无

复审无问题仅表示核对器未提出实质问题。受控缺陷修复、误改及漏检由 assistant-review.md 另行复核。
