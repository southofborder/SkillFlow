# DeepSeek 完整结果册：构建与视觉复验

最终结果册共 **730 页**，对应 30 个样例、90 条终态记录、85 份结构有效 CFG 和 891 项外置事实判断。PDF SHA256：

`d7e800a17608180900afc0f2cded045c2738e6d514ac89a2eb21313155f126ed`

这份记录确认产物与来源一致、排版可以复核；模型结果及初审理由仍待用户共同确认。结构有效不等于语义通过。第一阶段已确认的复核主册、完整原文附册、语料和事实标注保持冻结。

## 阅读定位

- 第 1–168 页：运行身份、服务与模型变更来源、30 个样例的三轮对照及逐事实初审。
- 第 169–172 页：全部 90 次试验的操作明细索引。
- 第 173–730 页：实际 CFG、完整控制边与条件、操作数和约束，以及五条失败的明确边界。
- 开发集重点意见：N04 第 22 页、D04 第 116 页、R03 第 143 页、R04 第 149 页、R05 第 156 页。保留集 R06 第 162 页只作为固定基线观察。

## 已完成的验证

在相同来源及字体环境下连续构建两次，PDF 字节和来源摘要清单完全一致。`build_manifest.json` 保留字体、生成器及全部输入来源摘要；`content_qa.json` 记录两次构建一致性、730 个页码、30 个样例目录和全部 90 次明细页眉检查。

内容校验逐次绑定实际输出，核对 854 个块、915 条边、1,760 条操作、2,906 项输入/输出操作数、1,227 条约束。所有页面都有正文，中文可搜索，没有 Unicode 替换字符；PDF 文本中本地 API 密钥精确匹配数为 0。

使用 Poppler 将最终 **730 页全部以 110 dpi 渲染**，生成 122 张六页联系表。初版 728 页已分四段逐张视觉检查，并放大检查中文、密集事实表、长字段、脚本摘要、CFG、失败页和最终页。最终版有 704 页在仅屏蔽右下角页码数字后与已检查的初版像素完全相同；另外 26 页全部按原尺寸重新检查。没有把未检查的差异页直接沿用为已通过。

最终变化页为：2–5、170–172、342–346、426–427、614–616、650–656、717–718。图像比较保留页眉、正文、页脚说明和页脚线；页码另行对所有最终页面检查。完整对应关系、分段观察和变化页记录均内嵌在 `visual_qa.json`，不依赖临时联系表作为唯一证据。

已修复来源记录跨页造成的三行孤尾、目录继承错误页眉，以及块首短 return 将 `draft_instruction_id` 孤立到续页的问题。最终第 427 页完整显示 F05/R2 的最后返回块及全部字段。稀疏但包含完整操作的末页予以保留；较长操作允许连续分页，字段内容没有省略。脚本字符串摘要与数组等 JSON 序列化值摘要分别标明计算依据。

最后全包离线测试为 **514 passed in 64.74s**。随后仅调整 PDF 短终结操作分页，其聚焦回归为 **29 passed in 1.22s**；两者不相加，也不声称最后排版修改后又运行了全包。测试、视觉检查及用户共同语义确认是不同层面的证据。

## 离线复现

在仓库根目录执行；使用安装了 ReportLab 4.4.9、pypdf 6.10 的 Python 3.12，字体以生成清单列出的文件和摘要为准。以下命令不调用 API，也不执行 Skill 脚本：

```powershell
$deepseekRun = 'packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910'
python -X utf8 packages/skill-ir/experiments/semantics_baseline/tools/review_results.py --run-dir $deepseekRun --check
python -X utf8 packages/skill-ir/experiments/semantics_baseline/tools/build_results_pdf.py --run-dir $deepseekRun --variant deepseek-v4-flash-max --output output/pdf/skill-ir-semantics-baseline-deepseek/skill-ir-baseline-results.pdf
New-Item -ItemType Directory -Force -Path tmp/pdfs/deepseek-reproduce
pdftoppm -r 110 -png output/pdf/skill-ir-semantics-baseline-deepseek/skill-ir-baseline-results.pdf tmp/pdfs/deepseek-reproduce/page
```

本次重建实际使用的 bundled Python 位于 `C:/Users/24831/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`。重新生成或更改来源、工具、字体后，应重新检查渲染；此处完成的视觉结论只绑定上述 PDF 摘要。
