# 基线执行状态 PDF 检查记录

检查日期：2026-09-10。最终交付仅为执行状态报告，不是完成了 90 次提取的语义结果复核册。

- 文件：`skill-ir-baseline-execution-status.pdf`
- 页数：6 页。
- SHA256：`863d6aac9078e4f59ecc82e5ca6495b5e5e26bab31b7335de2ce6cfcb826f1b1`
- 实际生成两次，PDF 字节摘要完全一致。
- 渲染：Poppler `pdftoppm -r 110 -png`，6 页全部生成 PNG。
- 页面图：`tmp/pdfs/skill-ir-baseline-execution-status/page-1.png` 至 `page-6.png`。

PDF 代理与根代理分别实际查看全部 6 页。中文字符、标题、页眉页脚、1-6 页码、30 行状态矩阵、样例编号、HTTP 长错误 JSON 与换行均清楚；未见缺字、裁切、重叠、空白页或不可读表格。表格保留 8.7 pt 字号；不通过缩小字号强塞内容。

内容核对：90 次计划仍为 22 个开发样例和 8 个保留样例，各重复 3 次。4 个受影响试验为 N01 第 1、2、3 次和 N02 第 1 次，状态 uncertain；其余 86 次 not_run。4 个生成会话记录了 12 次 HTTP 尝试：3 次 HTTP 524、5 次网络读取超时、4 次中断时仍在进行且远端结果未知。未收到生成结果，没有已接受 CFG；结构修复为 0，用量记录不可用（null），不能写成消耗为零。报告明确区分 HTTP 尝试与生成次数，也未虚构精确 Ctrl-C 时刻。

`execution_build_manifest.json` 记录生成器、复用排版工具、正式初审校验 helper、冻结材料、report/record/trace 与独立 reconciliation 审计来源摘要，以及字体与 PDF 摘要。生成时确认来源未变化，并核对全部 30 个样例编号和全部页脚页号。

复现命令（仓库根目录，需 PDF 依赖和所记录的字体）：

```powershell
& 'C:/Users/24831/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' packages/skill-ir/experiments/semantics_baseline/tools/build_results_pdf.py --execution-status-only
pdftoppm -r 110 -png output/pdf/skill-ir-semantics-baseline/skill-ir-baseline-execution-status.pdf tmp/pdfs/skill-ir-baseline-execution-status/page
```

正常结果模式保留在同一生成器中，已接入 `review_results.validate_review`；当前没有运行该正式结果模式，也没有创建 891 个空白或伪造的事实判定。`--allow-partial` 的排版自检仅保留于临时目录，未作为最终交付。
