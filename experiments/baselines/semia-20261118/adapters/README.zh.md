# Semia 完整源输入适配

`complete_source.py` 是单独命名的 `semia-379bc25f-complete-source-v1` 实验适配。固定官方源码仍未修改。本适配只在调用官方 prepare 的短暂期间，从 `_SKIP_FILES_ALWAYS` 中移除已固定输入清单所需的 `package.json`、`package-lock.json`，随后恢复原集合。官方渲染、语义单元抽取、合成提示、SDL、校验和候选选择均保持原样。

四包输入共21文件已完成离线验证；10项检查通过、无失败或跳过，360个官方源码文件与原归档哈希一致。见 [机器回执](../analysis/full-source-preflight/manifest.json) 和 [检查日志](../analysis/full-source-preflight/validation.txt)。本适配验证过程未调用模型，也未执行 Skill。

| case | 最终纳入文件 | prepared字节 | 初始合成prompt字节 | 语义单元 |
|---|---:|---:|---:|---:|
| 001 | 1/1 | 1116 | 9166 | 12 |
| 010 | 3/3 | 1443 | 9492 | 23 |
| 013 | 1/1 | 1115 | 9165 | 12 |
| ga4 | 16/16 | 155964 | 164013 | 3155 |

前三包的 `prepared_skill.md` 与上游默认prepare逐字节相同。GA4原版14文件产生66215字节、623个语义单元；补入两份JSON后增加89749字节（含上游包装）和2532个语义单元。这改变了实际输入规模、覆盖率分母和可能的模型成本，不能将适配版称为原版默认，也不能把两个分母下的覆盖分数直接对比。

验证不仅检查文件目录：它核验输入清单及字节哈希、逐个源文件的正文行及原行号、prepare产物和语义单元的来源映射一致性，并调用固定上游 `_prompt` 确认完整prepared正文确实位于最终合成请求的敌意输入围栏中。若出现额外或缺失文件、哈希变化、排除项、正文改写、来源映射重复或丢失、prompt缺少正文，就在模型请求前抛错。输出目录非空时拒绝覆盖。

上游本身将源文按行重组为LF，并去除末尾空白。本次固定四包的末尾仅有终止换行，因此适配验证允许该既有标准化，并验证每一条正文行不变。原始字节哈希和标准化后的正文哈希分别记录，不声称最终prompt字节与原始目录逐字节相同。未来遇到会被 `.rstrip()` 删除的非换行尾空白时，本适配直接拒绝，不静默扩大保证。

在新的独立runner中接入（调用者需先加载固定Semia源码）：

```python
from complete_source import make_complete_source_preparer
from semia_cli import core_adapter

core_adapter.prepare = make_complete_source_preparer(case_id)
# 此后仍调用官方 scan；prepare成功返回前已验证完整源输入。
```

也可离线调用 `prepare_complete_source(input_root, new_output_directory, case_id)`；需要复核现有产物时用 `verify_prepared(input_root, output_directory, case_id)`。输入目录可以重定位，但内容必须与既有input-manifest对应case完全一致。helper依赖当前固定Semia的私有prepare/prompt接口，必须在单独的实验进程中使用；它不会自动适配未来上游版本。

`validate_complete_source.py` 是本次离线验证入口，默认拒绝覆盖已经完成的prepared输出。完整检查包括输入额外文件、输入篡改、即使更新元数据哈希仍能发现的正文改写、最终prompt遗漏、异常后恢复上游过滤集合和原产物防覆盖。其日志不代表任何在线合成、检测精度或DOE结果。
