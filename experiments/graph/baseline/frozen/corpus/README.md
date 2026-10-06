# Skill-IR 首阶段语义复核语料

本目录实现 [共同复核方案](../../../../docs/Skill文档理解数据集与PDF共同复核方案.md) 的第一阶段。全部事实均为 **待共同复核**，没有预填语义通过结论，没有模型输出，也没有在线提取调用。生产 `src/skill_ir` 未因本语料修改；特别是 Prompt、IR 模型和提取流程不在本次变更范围内。

## 目录与输入隔离

| 路径 | 用途 | 可否作为一个 Skill 输入 |
| --- | --- | --- |
| `inputs/controlled/<ID>/` | 单份控制 Skill 的原始文件 | 是，仅限单个包目录 |
| `inputs/upstream/<name>/` | 单份固定上游 Skill 的原始字节 | 是，仅限单个包目录 |
| `annotations/<ID>.json` | 包外事实、证据、约束归属、争议、最小差分 | 否 |
| `provenance/` | 固定提交、Git blob/SHA-256、许可证来源、未下载链接 | 否 |
| `corpus.json` | 30 份样例的唯一清单与划分 | 否 |
| `coverage_matrix.json/.csv/.md` | 覆盖目标到事实和源文件行号的索引 | 否 |
| `tools/` | 离线构建、来源校验与 PDF 生成器 | 否 |

当前生产加载器递归读取目录中的全部可解码文件，包括 JSON/YAML 和 SVG。因此，**只能将 `corpus.json` 中某一条 `samples[].package_path` 交给加载器**；不能把本目录、`inputs/` 或其 `controlled/`、`upstream/` 父目录整体输入。样例 ID 来自外部清单及包目录名，不把答案或标注元数据写入 `SKILL.md`。来源 README 位于包外，各包原有 LICENSE/NOTICE 保留在原位置、保持字节不变。

## 固定组成

| 编号 | 场景 / 原包 | 语言 | 划分 |
| --- | --- | --- | --- |
| N01-N06 | 条件通知与数据发送 | 中文 | 开发集 |
| Q01-Q06 | 查询调用与参数使用 | 英文 | 保留验证集 |
| F01-F06 | 工具选择与失败回退 | 英文 | 开发集 |
| D01-D06 | 多文档处理与交付 | 中文 | 开发集 |
| R01-R04 | pdf、playwright、gh-fix-ci、netlify-deploy | 原文英文 | 开发集 |
| R05-R06 | linear、transcribe | 原文英文 | 保留验证集 |

控制组 01/02/03/04 分别是编号步骤、连贯段落、表格、跨文件混合表达；同组事实语义一致。05 与 01 相比只改一句话的用途，06 与 01 相比只改一句实质条件或数据要求；其他输入字节保持一致。开发集 22 份、保留集 8 份，按整组划分。已有三个独立回归示例不计入这 30 份。

真实包来自 [openai/skills 固定提交](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431)，提交 SHA 为 `49f948faa9258a0c61caceaf225e179651397431`。共 39 个包内文件，153,977 字节；生产加载器可读取 33 个文件、3,740 行。六张 PNG 属于不可读取输入，SVG 是可读取的 XML 文本。未做 OCR，未执行原包脚本、工具指令或部署，包外链接未被下载成隐含输入。

## 事实标注契约

`annotations/<ID>.json` 使用 `schema_version: 1`。事实的 `kind` 仅供人工复核组织：`behavior`、`condition`、`data_flow`、`constraint`、`must_not_infer`，不作为生产 IR 的新增分类。

- 每个事实具有唯一 `id`、自然语言 `statement`、`scope`、`evidence`、`coverage_tags` 及 `status: "待共同复核"`。
- `scope.level` 为 `skill`、`block`、`operation` 或 `unresolved`；`target` 是语义归属说明，不是固定块编号。`unresolved` 留待共同确认，不提升为全局约束。
- `evidence` 的 `file` 是包内相对路径，`start_line` / `end_line` 是从 1 开始、含两端的行号，`quote` 与解码原文逐行一致。表格事实附必要表头；跨文件事实附入口引用。
- `coverage_targets` 是各事实 `coverage_tags` 的并集。矩阵把每一个目标关联到具体事实及证据行号，避免只列“覆盖了某格式”的无来源勾选。
- `minimal_pair` 明确 `base_id`、一句话改动、`changed_fact_ids` 与 `unchanged_fact_ids`。相同事实在同组各版本保留相同 ID 后缀。
- `acceptable_variants` 不要求唯一 opcode、结果编号或 CFG；`open_questions` 记录有歧义的范围和源文分歧。

约束拟议采用“原文 + 所在层级”，即相应层级的 `constraints: list[str]`；**本次仅记录复核契约，不修改生产数据模型**。数据读取、运算和传递仍需在后续提取中表示为操作数及控制流，不能只藏在约束文字里。能力说明不制造调用，调用要求不凭空制造校验或转换。引用、示例和代码依当前流程是否明确采用而判定。可疑但确有原文要求的行为需如实保留，不执行，也不增添攻击分类、effect 或审计结论。

### 二次复核明确的边界

- N04/Q04/F04 包中的 JSON/YAML 是已提供的固定规范，与正文重复表达同一规则。仅引用这些声明不意味着执行流程必须新增一次运行时配置文件读取；真正要求读取的请求、环境变量、文档和 API 响应仍需保留数据来源。
- 黑盒只是不拆解内部变量、循环和控制流；调用可观察到的输入文件读取、目录/产物写入、返回值及标准输出仍须保留。D 组事实同时引用文字调用和实际脚本接口。
- `additional_behavior` 覆盖计数、状态和收据等附加写入，它们依赖主流程结果。原 `independent_behavior` 标签已改名，**本批未覆盖互不相关的独立行为组件及“不凭空连边”能力**，不能用本批测试通过来宣称该能力已验证。补足它应另行添加并复核样例，不改写已共同阅读的 24 个输入。
- 真实包的事实是具有来源的复核检查点，不是对所有可选工作流逐条穷举。未列为事实的行为，不能仅因“不在检查表”就判断为无依据新增；仍须返回原文判断。
- 用户已复核初版；本次复核意见和修改见 [SECOND_REVIEW.md](SECOND_REVIEW.md)。事实中的“待共同复核”保留为初始标注状态，不把测试成功等同于人工语义批准。

## 可复现构建

在仓库根目录执行。控制语料、清单与来源校验只需 Python 3.10+ 标准库：

```powershell
python packages/skill-ir/experiments/semantics_review/tools/generate_controlled.py
python packages/skill-ir/experiments/semantics_review/tools/vendor_upstream.py
python packages/skill-ir/experiments/semantics_review/tools/build_catalog.py
python packages/skill-ir/experiments/semantics_review/tools/build_catalog.py --check
```

`generate_controlled.py --output <目录>` 可在独立位置重建输入和标注并比较字节。`vendor_upstream.py` 默认**离线**核对完整清单、原始字节、许可证及外置 manifest。只有显式添加 `--fetch` 才会从锁定提交恢复原包；`--write-manifests` 从已核对的字节重建来源记录。上游注释为外置人工事实，不从模型输出生成。

PDF 使用独立环境，依赖锁定在 `requirements-pdf.txt`，不会修改生产包依赖：

```powershell
python -m venv .venv-review
.venv-review/Scripts/python -m pip install -r packages/skill-ir/experiments/semantics_review/requirements-pdf.txt
.venv-review/Scripts/python packages/skill-ir/experiments/semantics_review/tools/build_pdfs.py
.venv-review/Scripts/python packages/skill-ir/experiments/semantics_review/tools/verify_pdfs.py
```

Windows 默认读取系统 SimHei、Consolas 及可用的 Segoe 符号字体，**不复制或再分发系统字体文件**。其他系统通过 `--cjk-font` / `--mono-font` 提供带 TrueType 轮廓的中文与等宽字体；额外缺失字符使用可重复的 `--fallback-font` 参数。也可设置 `SKILL_REVIEW_CJK_FONT` / `SKILL_REVIEW_MONO_FONT`。生成器逐字符检查字体覆盖，缺字直接失败，不静默输出方框。使用相同源文件、依赖版本和字体字节，PDF 禁用时间变化，可重建相同 PDF 字节；`build_manifest.json` 记录源文件、字体及 PDF SHA-256 和实际页码索引。换字体可能改变分页，应重新渲染并检查。

最终输出默认在仓库 `output/pdf/skill-ir-semantics-review/`：

- `skill-ir-semantics-review.pdf`：判定规范、目录、划分、覆盖索引、24 份完整控制样例、6 份真实包证据摘录及全部外置事实检查表。
- `skill-ir-full-source-appendix.pdf`：6 份真实包的全部可读文本，包括许可证、配置、代码、SVG、参考材料；逐文件起页、原始行号、连续页码、样例编号。
- `build_manifest.json`：输入 / 字体 / 输出摘要和实际页码索引。

附册代码固定 9 pt，不缩字塞入页面；过长原始行分为带 `>` 标记的续行，制表符按 4 列展开。主册将控制样例的 Markdown 表格排为可换页表格，重复表头；附册保留 Markdown 原始管道、表头、分隔行与正文，便于追查。PDF 是可检索文本，原始文件字节仍为核对依据。

`verify_pdfs.py` 需要 Poppler `pdftoppm` 位于 PATH，或通过 `--pdftoppm <路径>` 指定。它会：

1. 先核对当前语料、标注、生成器和生产加载器与构建 manifest 的摘要，拒绝陈旧 PDF；再验证页数、页码、中文可检索性、全部事实 ID 与样例页码索引。
2. 从附册实际 PDF 的源码文字层读取所有 9 pt 文本运行，核对其与生产加载器的全部可读内容严格一致（仅按规定展开制表符、移除物理换行），确认无省略或换序。
3. 将**每页**渲染到 `tmp/pdfs/skill-ir-semantics-review/`，生成六页一组的索引图与 `verification.json`。该 JSON 的结构检查不会自动宣布视觉通过；须人工查看全部索引图和代表性整页，包括中文、表格、代码续页及编号。

可用 `--check-only` 只做文本/页码核对，用 `--output-dir` 或 `--pdf-dir` / `--render-dir` 指定独立位置。中间 PNG/索引图不作为 Skill 输入，不需要纳入版本控制。

## 测试与后续使用

```powershell
python -m pytest packages/skill-ir/tests/experiments/test_semantics_review_corpus.py -q
```

聚焦测试核对样例组成、22/8 划分、语义等价组、单行最小差分、原文证据、覆盖矩阵和上游文件摘要；使用**真实生产加载器与 Prompt 构建器**分别加载全部 30 个目录及带单层 wrapper 的 ZIP，并通过包外 canary 证明标注不会进入输入。测试不调用 LLM，也不执行包内脚本。

本轮验收是资料齐全、输入隔离、证据可追溯、PDF 可读。所有语义判断仍待共同复核。确认后才冻结语料和 Prompt，再单独处理约束契约，并在同一契约下每份每版本重复 3 次（30 × 3 = 90 次）；结构修复和 HTTP 重试分别记录。保留集不用于编写 Prompt 示例或当前轮反复调参。
