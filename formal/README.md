# Skill-IR 形式化工程：结构规则与受控事实保持

当前工程包含两个独立证明域：本页介绍的结构核心 `WF/check`，以及保留全部显式记录的
`RichGraph` 受控文本打印/解析。完整事实域与实际文本往返保证见
[CONTROLLED_RETELLING.md](CONTROLLED_RETELLING.md)。2026-09-13 的
[结构验收记录](VERIFICATION.md) 保留其历史日期和数字；新版 F01 实测见
[受控回述验收](../experiments/graph/audit/runs/controlled-v2-f01-20260914T142804Z/acceptance.md)。

本目录给出静态分析 IR 的声明式结构条件 `WF`、可运行参考检查器、Lean 内核检查的证明，以及生产 Python 校验器与参考检查器的差分工具。规范见 [Skill-IR 结构规范与验证边界](../docs/graph/Skill-IR结构规范与验证边界.md)，实施范围见 [第一步实施方案](../docs/history/skill-ir/Plan1.md)。

这一步回答“图是否符合约定的结构和引用规则”，不回答“原文是否全部提取”“操作是否正确执行”或“所有路径是否安全”。Lean 是研究验收工具，不是生产 Python 包的依赖。这里不执行 Skill，不调用模型 API，也不修改冻结的输入、标注、CFG 或图片。

## 文件与证明范围

| 文件 | 职责 |
| --- | --- |
| `SkillIR/Core.lean` | 核心数据类型、声明式 `WF`、可判定实例、`check` 及其健全性/完备性 |
| `SkillIR/RenameDefs.lean` | 三个结构 ID 命名空间的同步重命名及注入辅助引理 |
| `SkillIR/RenameReach.lean` | 有限可达闭包、可达关系和根集合与重命名的相容性 |
| `SkillIR/Rename.lean` | 各项结构条件和全图 `WF` 的重命名不变性 |
| `Main.lean` | 接收核心图 JSONL、输出布尔检查结果的离线 CLI |
| `SkillIR/Controlled.lean`、`SkillIR/ControlledGraph.lean` | 完整事实域、唯一受控打印/解析器、恢复与事实保持定理 |
| `ControlledMain.lean` | 实际受控文本 JSONL 打印/解析入口 |
| `ProofAudit.lean` | 打印五个结构主定理及十一个受控回述主定理的公理依赖 |
| `tools/bridge.py` | 字段 Schema 入域、规则相关信息的保真投影、调用生产 Python 校验 |
| `tools/cases.py` | 规则正反例、30 个固定原始 CFG、生成式和拓扑案例、变形与破坏规则的案例 |
| `tools/differential.py` | 运行两套检查器、绑定摘要、统计分歧、缩减与回放 |
| `fixtures/review30.json` | 固定 30 份原始分析的编号、轮次、仓库相对路径和 SHA-256；不含 CFG 副本或事实标注 |

规范 W01–W12 到生产实现、测试和证明范围的对应关系在规范文档中。Lean 核心的标识使用三个独立的自然数命名空间；生产字符串的非空、格式及字段互斥等要求属于 Schema 层。

核心定理如下，均由 `lake build` 编译并由 Lean 内核检查：

```lean
SkillIR.check_iff_wf   -- check g = true ↔ WF g
SkillIR.check_sound   -- check g = true → WF g
SkillIR.check_complete -- WF g → check g = true
SkillIR.wf_rename_iff  -- WF (renameGraph ρ g) ↔ WF g
SkillIR.check_rename   -- check (renameGraph ρ g) = check g
```

后两个定理要求块、指令、结果的三种映射分别单射。合法双射是特例；定义、引用、边端点和入口同步改名，上下文键、资源标识、业务文字及条件不改名。映射回生产字符串时仍须满足 Schema 命名规则。

`WF` 先独立写成逻辑条件，再以 `check g := decide (WF g)` 得到可执行参考检查器。检查器正确性在这里是有限命题的反射证明，不是一套另行手写、优化过的算法的正确性证明。重命名证明另外覆盖各项条件、定义引用关系以及可达闭包的保持。

`Reach` 使用 `blocks.length` 轮有限闭包，条件文字不参与真假判断。证明包含每轮闭包的逻辑刻画和重命名保持；本轮没有另行证明它与某个无界路径定义、Python 遍历算法或实际执行轨迹等价。循环仍然允许，闭包轮数不是循环执行次数限制。

## 复现环境

- Python 3.10 或更高版本；安装本仓库 `skillflow` 及 `pytest`。实际验收所用的 Python、Pydantic、pydantic-core 版本保存在差分报告中。
- Lean 固定为 `leanprover/lean4:v4.33.1`，见 `lean-toolchain`。仅使用随该工具链提供的标准库，没有 Mathlib 或外部 Lean 包。
- 本次实际使用的 Lean 提交：`819816b2e0a3bf405af45ae5c7af2491d8f5bee6`。

已有 elan 时，在 `formal/` 中运行 `lake build` 会选择固定版本。也可使用 [Lean 官方 4.33.1 发布包](https://github.com/leanprover/lean4/releases/tag/v4.33.1)。本次 Windows 便携包为 `lean-4.33.1-windows.tar.zst`，583,557,483 字节，SHA-256：

```text
f63029c0e1e6daed0f4807481b6fcd8f8b77fbce6d63f205c7f9191072387a7a
```

工具链压缩包与解压目录不是源码交付内容。当前工作区放在被忽略的 `tmp/toolchains/`；`.lake/` 同样被忽略，不需要把本机编译缓存加入版本控制。

如尚未安装 Python 依赖，从仓库根目录执行：

```powershell
python -m pip install -e . pytest
```

## 构建与公理审计

从仓库根目录进入本目录。下面的 `PATH` 设置仅用于本次会话的便携工具链；使用 elan 时省略该行。

```powershell
$env:PATH = (Resolve-Path 'tmp/toolchains/lean-4.33.1-windows/bin').Path + ';' + $env:PATH
Set-Location formal
lake build
lake env lean ProofAudit.lean
```

默认构建包含 `SkillIR` 证明库、结构检查器 `skill_ir_check` 和受控打印/解析器
`skill_ir_retell`，避免只构建 CLI 而遗漏证明。Windows 可执行文件位于
`.lake/build/bin/`，扩展名为 `.exe`；其他平台没有此扩展名。

五个结构主定理的审计输出均为标准依赖 `[propext, Quot.sound]`；受控文本定理中的
部分证明另依赖 `Classical.choice`，详见受控回述说明。它们是明确列出的 Lean 标准公理，
不应描述成“完全不依赖公理”。工程不使用 `sorry`、`admit`、自定义公理或跳过内核检查的方法。

## 测试与完整差分

以下命令均从仓库根目录执行：

```powershell
python -B -X utf8 -m pytest tests -q -p no:cacheprovider
python -B -X utf8 -m formal.tools.differential --checker formal/.lake/build/bin/skill_ir_check.exe --output tmp/skill-ir-formal/differential
python -B -X utf8 -m tools.graph.baseline.export_review_set --check
```

默认差分使用仓库内的 `fixtures/review30.json`，不依赖某台机器的临时绘图文件或绝对路径。001–006 对应 N01–N06，007–012 对应 Q01–Q06，013–018 对应 F01–F06，019–024 对应 D01–D06，025–030 对应 R01–R06。015/F03 固定第 3 轮，其余固定第 1 轮。实际输入从逐一校验摘要的原始 `analysis.json["cfg"]` 读取。

需要保留冻结实验记录才能重现这 30 图。若只想验证生成案例，可显式传 `--without-review`，但这不满足含 30 图回归的完整验收。不要用绘图时带默认空字段的 `model_dump` 替换原始分析，也不要为通过验证而重写冻结记录。

默认生成参数为 `--seed 20260913 --random-count 160 --max-blocks 3`。包括 57 个规则 fixtures、30 个原始图、1,060 个拓扑案例、160 个固定种子案例、80 个合法改名案例、80 个块与边存储次序案例和 284 个规则 mutation，共 1,751 个输入。拓扑枚举覆盖至多 3 个块的所有有向边子集（含自环），并检查两种特定指令布局；它不是对所有可能的 3 块 IR 内容的穷举。

这批改名案例还同步修改 `context_key` 与其声明，额外检验上下文名称的一致替换；这一额外范围由差分测试覆盖，不属于当前仅重命名块、指令、结果 ID 的 Lean 定理。存储次序案例同时反转块字典和边列表，不改变块内指令次序。

差分报告分别统计 Schema 拒绝和进入 Lean 核心的输入。Schema 非法案例没有 Lean 判断，不能计为双方共同拒绝。`--prepare-only` 只生成材料，状态明确为 `prepared-not-checked`；缺失或损坏的指定检查器会报错，不会隐式通过。

普通 Python 测试在没有 Lean 时只跳过一项显式的 CLI 集成测试，其余生产和桥接测试仍能运行。完整研究验收必须另行完成真实构建、公理审计及差分运行，不能凭跳过后的测试成功宣称全部完成。

## 证据与反例回放

`--output` 目录包含：

- `report.json`：每例输入、投影、Python/Lean 判断、分组统计、版本、命令与源码/检查器摘要。
- `attestation.json`：报告文件摘要、案例集合摘要以及相同的版本绑定。
- `cases/`、`projections/`：可单独检查和回放的实际输入与核心投影。
- `counterexamples/`：仅出现分歧时生成原例关联和经删除缩减的反例。

版本绑定包含 IR Python 源码、桥接/生成/差分工具、Lean 证明源文件、`lakefile.toml` 与 `lean-toolchain`。每个原始案例另外绑定固定清单和原始分析文件摘要。本次验收概要及证据定位见 [VERIFICATION.md](VERIFICATION.md)。

缩减默认最多尝试 120 次删除，保留同方向的 Python/Lean 分歧，并记录是否耗尽预算。只声称指定删除策略下的结果，不声称获得全局最小反例。对报告中的案例文件或缩减反例执行：

```powershell
python -B -X utf8 -m formal.tools.differential --checker formal/.lake/build/bin/skill_ir_check.exe --replay <案例JSON路径> --output tmp/skill-ir-formal/replay
```

所有证据放在正式输入和 PNG 目录之外。不同运行的时间戳、绝对输出路径和本机构建产物摘要可能不同；案例内容、原始输入摘要、生成参数和判断结果才是跨机器复现的主要比较对象。

## 输入协议和信任边界

CLI 从标准输入读取 JSONL，每个非空行是一张核心图，输出一行 `{"accept":true}` 或 `{"accept":false}`。JSON 解析失败输出 `{"error":"..."}`，它不等同于结构规则拒绝。最小输入例子：

```json
{"entry":0,"blocks":[{"key":0,"id":0,"source":"none","instructions":[{"id":0,"opcode":"return","inputs":[],"outputs":[]}]}],"edges":[],"contexts":[]}
```

核心 `opcode` 只有 `business`、`dispatch`、`return` 三个结构类别；生产业务名称仍是开放字符串。输入/输出操作数形如 `{"kind":"result","id":0}`、`{"kind":"context","id":"request"}`、`{"kind":"external","id":"path"}` 或 `{"kind":"literal"}`。边条件为字符串或 `null`，仅参与“是否有条件”和边身份的判断。

原图的说明、约束、业务名称、literal 内容和脚本正文仍保存在原 IR；核心投影只保留本阶段规则用到的信息。桥接不会执行这些内容，也不会把 Python 已经算好的可达性或规则结论送给 Lean。重复项、悬空引用、列表顺序和块键/ID 不一致等必须保留，不能投影时清理。

Lean 证明覆盖核心数学对象及参考检查器。JSON 解析、Python Schema、模型快照、投影、Python 执行以及本机编译器/运行时并没有端到端机器证明；回归与差分是在已记录版本和有限输入上的一致性证据。定理的信任基础包括 Lean 内核及列明的标准公理；运行 CLI 还依赖实际构建和运行环境。

例如，只有快速分支定义 `fast_result`，而合流块引用它，只要存在从定义到使用的控制路径就可能满足本阶段规则。备用分支是否也会无条件读取它，需要后续数据可用性与操作语义分析。`x > 0` 后再经过 `x < 0` 的控制路径也可以在图结构上合法，条件是否矛盾属于另一个问题。无定义引用、重复定义、同块先读后定义等已规定的结构错误则必须拒绝。

受控语义回述与完整源文核对的 v2 原型当时验收范围是 F01 原图及四个受控反例，
对应记录保留其历史身份。现行流程已包含联合标注、观察编译和确定性传播，布局与
当前验收见[架构与迁移验收](../docs/architecture/SkillFlow-架构与迁移验收.md)。
这些工程实现不扩大本页结构证明或受控文本事实保持定理的范围；任务相关的 DOE
判断仍为下一阶段。
