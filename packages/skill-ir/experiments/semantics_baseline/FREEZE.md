# 已共同确认的实验基线冻结

用户于 2026-09-10 明确确认二次复核修订和此前待确认部分，并要求进入后续步骤。本目录的 `approval.json` 按标注 SHA-256、全部事实 ID 和原文未知范围记录这次确认。它表示检查依据已获共同确认，不表示尚未产生的模型输出已经语义通过。

`frozen/` 是真实字节副本，不依赖当前工作区源文件继续保持不变：

| 路径 | 冻结内容 |
| --- | --- |
| `frozen/corpus/` | 已审语料全树，包括 30 个独立 Skill 输入、297 条外置事实、来源、覆盖矩阵及首阶段构建器 |
| `frozen/production/` | 引入约束契约之前的 29 个生产 Python 文件和 `pyproject.toml`；包含 Prompt、候选模型、IR、编译器、加载器、提取流程与 HTTP 客户端 |
| `frozen/original_contract/` | 原候选 JSON Schema、原 Prompt 前缀、30 份原始完整 Prompt，以及生成用 Python/Pydantic 版本 |
| `frozen/review/` | 已审的 126 页主册、99 页原文附册、构建摘要、视觉检查记录及共同复核方案 |
| `freeze_manifest.json` | 206 个冻结文件的字节数及 SHA-256、整体摘要、确认记录摘要、22/8 划分和 3 次重复协议 |
| `approval.json` | 包外共同确认记录；完整保留已接受的不确定范围 |

原 `semantics_review` 目录完全不改。冻结标注继续保存初次生成时的“待共同复核”字符串，避免修改已审 PDF 的源字节；有效确认状态由外置 `approval.json` 赋予。N 组计数口径、D 组原顺序要求的范围、Netlify 发布优先级冲突和 Transcribe 包外 API 结果等，接受为已记录的源文不确定性，不捏造单一答案。互不相关的独立行为组件仍是本批未覆盖范围。

生产契约的后续修改必须与此原版分开记录。`frozen/original_contract/prompts/` 是历史参照：正式比较应当让基线与后续 Prompt 版本采用相同的约束契约，不能把新加字段的收益计为 Prompt 优化。保留查询参数整组及 Linear、Transcribe 的 8 份验证样例；它们不用于本轮编写 Prompt 示例或反复调参。每版本全量固定 30 × 3 = 90 次提取，结构修复与 HTTP 重试另外记录。

离线校验命令（仓库根目录执行）：

```powershell
python packages/skill-ir/experiments/semantics_baseline/tools/freeze.py
python -m pytest packages/skill-ir/tests/experiments/test_semantics_freeze.py -q
```

向新目录导出可复核副本：

```powershell
python packages/skill-ir/experiments/semantics_baseline/tools/freeze.py --export tmp/approved-semantics-export
python packages/skill-ir/experiments/semantics_baseline/tools/freeze.py --base tmp/approved-semantics-export
```

导出只复制封存字节，不重新采集当前已可能变化的生产源码；目标已存在时拒绝覆盖。校验器只需标准库，不调用模型、不执行样例脚本。文件摘要用于检测陈旧或意外修改，不构成外部签名或防止恶意重写锁文件的证明。

实验 runner 可导入 `tools/freeze.py`，使用 `verify_freeze(base=...)` 验证后读取 `corpus_root(base)/corpus.json`。**只能把单条 `samples[].package_path` 所指向的目录交给加载器**，不得加载 `frozen/`、`frozen/corpus/` 或 `inputs/` 父目录。`production_root(base)` 返回原版 `frozen/production/src/skill_ir`，用于审查契约差异。冻结文件清单包含所有输入目录成员；即使新增文件伪装为 `__pycache__` 下的标注，也会使校验失败。

在创建任何线上实验输出之前，这些原始源码、事实和 Prompt 已封存。冻结本身未发起线上调用；具体实验执行状态在后续运行产物中记录。
