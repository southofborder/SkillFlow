# 真实 Skill 的来源与复现

六个包来自 [openai/skills 的固定提交](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431)，提交号为 `49f948faa9258a0c61caceaf225e179651397431`。所有包均取自该提交的 `skills/.curated/`，没有使用分支、标签或最新版本。

| 样例 | 包 | 划分 | 文件数 | 原始字节数 | 可读取文件数 | 可读取行数 |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| R01 | pdf | development | 4 | 14824 | 3 | 273 |
| R02 | playwright | development | 9 | 22850 | 8 | 607 |
| R03 | gh-fix-ci | development | 6 | 32642 | 5 | 788 |
| R04 | netlify-deploy | development | 8 | 33655 | 7 | 1189 |
| R05 | linear | held_out | 5 | 24803 | 4 | 308 |
| R06 | transcribe | held_out | 7 | 25203 | 6 | 575 |
| 合计 |  |  | 39 | 153977 | 33 | 3740 |

`upstream-lock.json` 从固定提交的 GitHub recursive tree 响应记录六个目录的完整文件集合、Git blob ID、Git 文件模式及长度，同时记录仓库根 `README.md` 的 blob。GitHub 返回 `truncated: false`。快照保存每个包内全部原始文件字节，包括图标、脚本、许可证、NOTICE 和 agent 配置；没有为样例编号或解释改写包内文本。

每包 `R01.json` 至 `R06.json` 记录来源 URL、提交、上游目录和本地输入目录。`files` 记录相对路径、字节数、SHA-256、Git blob SHA-1、Git 模式、加载器可读性和可读行数。Git blob 摘要使用 `SHA1("blob " + byte_length + NUL + raw_bytes)` 校验，不是普通文件 SHA-1。

读取边界与当前生产加载器一致：含 NUL 或不能按 UTF-8-sig 解码的文件不作为文本输入；其余文件完整解码。六个 PNG 保留在原包中但不进入可读文本；SVG 可以解码，所以作为完整源文本进入原文附册，不被误判成不可读图片。行号以解码文本的 `splitlines()` 计算，从 1 开始。原始文件没有经过换行符转换。

外链仅做清单记录。`external_links` 是源文本中出现的 HTTP(S) 字面量及其文件和行号，包括文档链接、示例 URL、XML namespace、API endpoint 等；所有条目均标记 `provided_as_input: false` 和 `not_fetched`。该清单不把这些不同用途的 URL 视为需要执行的操作，也不下载其指向内容。包内跨文件引用已经随完整包提供；未附带的第三方库、工具服务、音频、用户仓库及外部文档不作为隐藏输入。

全部语义标注、样例编号、来源记录均在包外。复现程序不会加载标注到包中，不执行上游脚本、安装其依赖、建立 MCP 连接或调用部署及转录服务。

## 离线验证

在仓库根目录使用 Python 3.10 或更新版本运行（只需标准库）：

```powershell
python packages/skill-ir/experiments/semantics_review/tools/vendor_upstream.py
```

默认模式不访问网络，逐个验证 Git blob、文件大小、完整文件集合、无符号链接及重建的 provenance 内容。多出标注或任何其他包内文件都会使验证失败。

## 从固定来源恢复及重建清单

```powershell
python packages/skill-ir/experiments/semantics_review/tools/vendor_upstream.py --fetch --write-manifests
```

`--fetch` 只请求锁文件列出的 `raw.githubusercontent.com/openai/skills/<固定提交>/<路径>`。写入前校验 Git blob ID 和原始长度；不会跟随包内外链，亦不会刷新到更新提交。`--write-manifests` 根据已经验证的字节重建六份来源 manifest 与 `upstream_samples.json`；不重写事实标注。恢复前后运行默认模式可得到相同摘要。上游不可访问时，版本库内已经保存的原始文件可完全离线使用与校验。

## 许可证与版权

该提交的仓库根目录没有 LICENSE 文件；根 `README.md` 明确说明每份 Skill 的许可证位于自身 `LICENSE.txt`。原始根 README 按原字节另存为 `upstream-README.md`，只作为来源记录，不插入任何输入包。六份包内 `LICENSE.txt` 均完整保留，playwright 的 `NOTICE.txt` 亦完整保留；版权和授权条款以这些原始文件为准。来源 manifest 的 `license.package_files` 列出各包适用的许可及声明文件。

引用上游文本与脚本仅用于文档语义复核。语料本身保留原文提出的行为（包括有条件要求提升网络权限），这些内容是待分析的数据，不能改变本仓库执行权限或本阶段边界。
