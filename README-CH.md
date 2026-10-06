# SkillFlow

SkillFlow 面向 Agent Skills 开展任务相关的静态数据最小化分析。当前 **Skill-IR**
已实现建图、受控回述与源文核对、有界反馈、安全与传播语义标注、聚焦审查及一次标注修复、确定性数据传播。

**下一阶段是敏感性、任务必要性与 Data Over-Exposure（DOE）的综合判断。**
当前传播交付完整事实文件 `doe-input.json`，尚不产生 DOE 结论。
2026-09-15 已删除旧 SFG/FCG 引擎、旧 DOE 评分器及其流水线，不保留兼容转发。

[表示契约与一次修复](docs/propagation/SkillFlow-表示契约与一次标注修复.md) · [文档导航](docs/README.md) · [English](README.md)

当前布局与历史身份边界见[架构与迁移验收](docs/architecture/SkillFlow-架构与迁移验收.md)；[迁移总览](experiments/migrations/layout-v1-20261002-215752/index.html)直接链接三例保持一致的 DOE 文件及新布局离线验收。最终完整回归已通过：2509 项，无失败、错误或跳过，详见[测试记录](experiments/migrations/layout-v1-20261002-215752/verification/python-tests.json)。

## 当前主流程

```text
Skill 目录 / ZIP
  → 模型提取候选，程序编译 CFG
  → 结构与引用校验
  → Lean 生成受控回述，程序检查实际文本往返
  → 模型比较完整源文与受控回述
  → 有明确差异时进行有界 CFG 反馈
  → 一次安全与传播语义标注，编译模型观察
  → 聚焦审查；有明确问题时完整修复标注一次并独立复审
  → 确定性传播，生成 doe-input.json 与审查报告
  → DOE 判断（下一阶段）
```

结构通过不等于源文语义完整；受控回述证明保持图中明确记录的事实，不证明原文提取、
模型判断或操作执行正确。CFG 反馈重新完整提取；标注修复只生成新候选，不改写冻结图或历史结果。

既有一次验证包括七例标注初审及按需一次修复，以及 001、010、013 三份既有 CFG 的单次核对。
详情见[助手复核报告](experiments/propagation/review/runs/repair-once-v1-20260929-132248/assistant-review.md)。
已有 30 例及更早实验保留各自协议和模型身份，不能自动视为通过了最新流程。

## 使用入口

在仓库根目录使用 Python 3.10 或更高版本：

```powershell
python -m pip install -e . pytest
python -m skillflow --help
python -m skillflow.graph.audit --help
python -m skillflow.graph.feedback --help
python -m skillflow.propagation.annotation --help
python -m skillflow.propagation.review --help
python -m skillflow.propagation --help
python -m skillflow analyze --input examples/graph/simple_skill --output tmp/analysis.json
python -m skillflow render --input tmp/analysis.json --output tmp/graph.mmd
```

`analyze` 默认调用模型；提供 `--candidate` 时离线编译。`render` 不调用模型。
凭据配置模板为 [.env.example](.env.example)。当前项目使用官方 DeepSeek 服务，请求
模型为 `deepseek-v4-flash`；实际响应模型名单独记录。
完整说明见 [Skill-IR 使用说明](docs/architecture/implementation.md)。

独立回述实验需要先构建固定版本的 Lean 打印器：

```powershell
# 在 formal 中，使用 lean-toolchain 固定的工具链：
lake build
lake env lean ProofAudit.lean
# 回到仓库根目录；prepare 不调用 API：
python -m skillflow.graph.audit prepare --run-dir tmp/backtrace-review
```

`run` 对 F01 原图与四个反例执行五次模型核对；`replay` 离线重放已保存的新版响应。
早期实测可阅读 [F01 历史验收报告](experiments/graph/audit/runs/controlled-v2-f01-20260914T142804Z/acceptance.md)，
不需要为查看结果重新调用 API。

## 目录与离线检查

| 路径 | 当前用途 |
| --- | --- |
| `src/skillflow/` | graph、propagation、common 三个职责区域 |
| `formal/`、`tests/`、`tools/` | 证明、回归与仓库实验工具 |
| `dataset/skills/` | 30 份冻结的 Skill 语义评测输入 ZIP |
| `result/ir-IPP/` | 对应的 30 张 CFG PNG；是模型转换结果，不是标准答案 |
| `result/suggestions/`、`result/advice_for_doe/` | 逐样例评审及先前压缩意见；历史目录名不代表已有新 DOE 实现 |
| `packages/skill-similarity-analyzer/` | 独立 ClawHub 下载与相似度分组工具，不参与当前语义核对 |
| `shared/`、`test/` | 该辅助工具仍使用的 JavaScript 支持代码与测试 |
| `docs/`、`experiments/legacy_sfg_doe/` | 当前规范与保留的历史材料 |

冻结 Skill、外置标注和原始模型调用位于 `experiments/`；当前 PDF 工具位于 `tools/corpus/`。
标注不进入 Skill 输入。既有 ZIP、PNG、评审、PDF 及历史记录没有因清理被重写。

以下检查不调用远程模型，也不执行 Skill 中的脚本：

```powershell
python -B -X utf8 -m pytest tests -q -p no:cacheprovider
python -B -X utf8 -m tools.graph.baseline.export_review_set --check
node --test "test/*.test.js" "packages/skill-similarity-analyzer/test/*.test.js"
```

更多内容见 [文档导航](docs/README.md)、[形式化工程](formal/README.md)
和 [实际受控文本保证](formal/CONTROLLED_RETELLING.md)。
旧流水线文档已作为 [历史材料](docs/history/legacy-sfg-doe/README.md) 保留。

安装后的生产命令可从其他工作目录使用。仓库实验工具从项目根使用 `python -m tools.<职责>.<工具名>`，不把它们安装成生产接口。历史字节与旧地址映射由 `experiments/migrations/` 清单核验，旧 `skill_ir` 模块没有兼容转发。
