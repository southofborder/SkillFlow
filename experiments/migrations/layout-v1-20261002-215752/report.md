# SkillFlow 架构迁移验收报告

迁移主线已完成：生产代码按 `graph / propagation / common` 组织，根安装入口为 `skillflow`，证明、测试、工具、示例及实验材料分开存放。完整 Python 回归已完成：2509 项通过，无失败、错误或跳过。

[可视化总览](index.html) · [架构、入口和保证边界](../../../docs/architecture/SkillFlow-架构与迁移验收.md) · [文档导航](../../../docs/README.md)

## 交付位置和入口

- `src/skillflow/graph`：原 IR、候选编译、结构校验、受控核对与 CFG 反馈。
- `src/skillflow/propagation`：联合标注、聚焦审查和一次修复、观察编译、Data 与确定性传播。
- `src/skillflow/common`：源包、HTTP/SSE、记录保存及精确地址解析；没有对业务阶段的反向依赖。
- `formal/`、`tests/`、`tools/`、`examples/`：研究证明、回归、仓库工具及可运行示例。
- `experiments/{graph,propagation,corpus}`：各阶段冻结材料和运行；配置与数据集在 `experiments/configs` 和 `experiments/datasets`。

```powershell
python -m pip install -e . pytest
python -m skillflow --help
python -m skillflow.graph.audit --help
python -m skillflow.graph.feedback --help
python -m skillflow.propagation.annotation --help
python -m skillflow.propagation.review --help
python -m skillflow.propagation --help
```

生产入口安装后可从其他工作目录使用。仓库工具从项目根执行 `python -m tools.*`，不随生产包安装。旧 `packages/skill-ir` 活跃目录已清除，没有 `skill_ir` 兼容包；已核验的旧缓存隔离在忽略的 `tmp/layout-migration/retired-cache`，不作为源码或入口。独立的 Skill 相似性工具保持自己的实现。

## 内容与历史身份保护

本次改变目录和代码依赖，不改变 IR、Data 或联合标注等业务版本，也没有重新调用模型、执行 Skill 或生成 PDF。

| 核验对象 | 结果 | 原始证据 |
| --- | --- | --- |
| 历史文件 | 11,963 个大小／摘要保持 | [独立审计](verification/independent-audit.json) |
| 受保护交付物 | 239 个摘要保持 | 同上 |
| 证明文件 | 13 个摘要保持 | 同上 |
| 3 个建图 Skill 示例 | 迁移到 examples/graph，字节保持 | [补充地址清单](../layout-v1-20261002-215752-examples/manifest.json) |
| 目录／文件地址 | 精确登记旧相对、旧绝对、新地址和摘要 | [主地址清单](manifest.json)、[搬迁记录](moved-units.json) |

历史响应、Prompt、报告及生产者摘要没有改写。历史字面路径由精确清单解析；不存在后缀搜索或猜测性替代。清单解析成功不等于允许旧运行续跑。

只读加载检查材料真实性、接受响应和可重建编译一致性；旧 `run/resume/replay` 继续严格核验完整实现身份，迁移后实现变化仍被拒绝。没有关闭检查、更新旧摘要或将旧记录冒充新生产者。

## 已完成的工程验收

1. **形式工程：**Lean 构建通过，16 个主定理完成公理审计；30 个固定图及 4 个变体完成实际受控文本往返。依赖为日志列明的 Lean 标准公理，不宣称无公理依赖。[形式验收](verification/formal/receipt.json)、[构建](verification/formal/build.log)、[公理](verification/formal/axioms.log)。
2. **原三例只读核验：**源文、CFG、实际 Prompt、原始与编译响应、编译映射、DOE 全字段和 SHA 一致；旧标注及传播的直接重放因实现身份改变被拒绝。[三例记录](verification/three-case-facts.json)。
3. **新布局恢复和重放：**建立独立新身份，注入每例一份真实已接受响应，恢复时不重发，并进行标注和传播离线重放；三例与原 DOE 字节相同。总远程模型调用为 0，HTTP 参数、用量和实际返回模型在注入记录中不可观测，不能当作新的 DeepSeek 实测。[新布局记录](verification/new-layout/receipt.json)。
4. **安装与依赖：**轮包源码比较、包外工作目录入口、系统临时目录轮包安装、阶段单向依赖及无固定父目录／临时 sys.path 已核验。[独立审计](verification/independent-audit.json)、[独立安装](verification/isolated-install.json)。
5. **导航与工具：**文档与 HTML 本地链接、片内锚点、UTF-8、示例及帮助入口以更新后的[导航记录](verification/navigation.json)为准。此次只有结构检查，不声称完成浏览器视觉验证。
6. **专项记录：**[保护验收](verification/preservation.json)、[依赖验收](verification/dependencies.json)及[测试保留](verification/test-retention.json)分别记录历史、分层和回归保护；[JavaScript 测试](verification/javascript.json)24 项通过。

**最终完整回归已通过：2509 项，0 失败／错误／跳过，759.39 秒，退出码 0。** 原有 2494 项保留，本轮新增 15 项；详见[最终测试记录](verification/python-tests.json)与[JUnit](verification/tests.xml)。该结果说明工程回归通过，不代替模型标注语义正确性的结论。

## 三例 DOE 原始事实与审查页

| 样例 | 静态传播状态 | IR 记录 | Data | 新布局 DOE | 审查报告 | 零 API 重放 |
| --- | --- | --- | --- | --- | --- | --- |
| 001 / N01 | complete | 10 | 6 | [原始 JSON](verification/new-layout/cases/001/propagation/doe-input.json) | [HTML](verification/new-layout/cases/001/propagation/report.html) | [摘要](verification/new-layout/cases/001/propagation/replay/summary.json) |
| 010 / Q04 | complete | 12 | 22 | [原始 JSON](verification/new-layout/cases/010/propagation/doe-input.json) | [HTML](verification/new-layout/cases/010/propagation/report.html) | [摘要](verification/new-layout/cases/010/propagation/replay/summary.json) |
| 013 / F01 | complete | 26 | 20 | [原始 JSON](verification/new-layout/cases/013/propagation/doe-input.json) | [HTML](verification/new-layout/cases/013/propagation/report.html) | [摘要](verification/new-layout/cases/013/propagation/replay/summary.json) |

原始模型实验位于[已封存的 sink-tightening 总览](../../propagation/runs/sink-tightening-v1-20261002-205045/index.html)。此次不重新评价其模型表现，也不将 `complete` 解释为已经证明标注正确。新文件保留来源范围、处理关系、可能观察及实际参数绑定；DOE 阶段尚未计算。

## 后续阶段边界

迁移验收确认现有代码组织、内容身份、有限输入上的恢复与输出一致性。它不证明原自然语言与 CFG 完全等价，不证明标注模型的所有判断，不把契约可能观察变成真实执行事实。

DOE 下一阶段应消费自己的事实输入和 Sink 范围，另存回溯、敏感性、必要性和非必要暴露结论。现有传播事实、人工材料及历史身份不能被后续结果回写。

后续 DOE 实现归入 `src/skillflow/doe/`；本轮不创建空模块或假入口。

## 封存历史阶段导航

下列迁移目标来自主清单的精确 `new_relative`；链接已核对存在及摘要。旧报告中的原绝对链接保持原字节，历史日期及旧协议不因总览链接变成当前结果。

### 建图 baseline

- [CONTRACT.md](../../graph/baseline/CONTRACT.md)
- [DEEPSEEK.md](../../graph/baseline/DEEPSEEK.md)
- [FREEZE.md](../../graph/baseline/FREEZE.md)
- [RESULTS.md](../../graph/baseline/RESULTS.md)
- [RUNNER_REVIEW.md](../../graph/baseline/RUNNER_REVIEW.md)
- [RUNNING.md](../../graph/baseline/RUNNING.md)
- [STATUS.md](../../graph/baseline/STATUS.md)

### 源文核对 audit

- [runs/controlled-v2-f01-20260914T142804Z/README.md](../../graph/audit/runs/controlled-v2-f01-20260914T142804Z/README.md)
- [runs/controlled-v2-f01-20260914T142804Z/report.md](../../graph/audit/runs/controlled-v2-f01-20260914T142804Z/report.md)
- [runs/controlled-v3-seven-20260918/README.md](../../graph/audit/runs/controlled-v3-seven-20260918/README.md)
- [runs/controlled-v3-seven-20260918/report.md](../../graph/audit/runs/controlled-v3-seven-20260918/report.md)
- [runs/controlled-v4-seven-20260918/README.md](../../graph/audit/runs/controlled-v4-seven-20260918/README.md)
- [runs/controlled-v4-seven-20260918/report.md](../../graph/audit/runs/controlled-v4-seven-20260918/report.md)
- [runs/f01-deepseek-v4-flash-max-20260914/README.md](../../graph/audit/runs/f01-deepseek-v4-flash-max-20260914/README.md)
- [runs/f01-deepseek-v4-flash-max-20260914/report.md](../../graph/audit/runs/f01-deepseek-v4-flash-max-20260914/report.md)

### CFG 反馈 feedback

- [runs/f01-feedback-20260915/report.md](../../graph/feedback/runs/f01-feedback-20260915/report.md)

### 联合标注 annotation

- [runs/full-pipeline-v4-20260918-rerun-failed/acceptance-report.md](../../propagation/annotation/runs/full-pipeline-v4-20260918-rerun-failed/acceptance-report.md)
- [runs/full-pipeline-v4-20260918-rerun-failed/lineage-report.md](../../propagation/annotation/runs/full-pipeline-v4-20260918-rerun-failed/lineage-report.md)
- [runs/full-pipeline-v4-20260918-rerun-failed/report.md](../../propagation/annotation/runs/full-pipeline-v4-20260918-rerun-failed/report.md)
- [runs/full-pipeline-v4-20260918/report.md](../../propagation/annotation/runs/full-pipeline-v4-20260918/report.md)
- [runs/security-profile-20260917/report.md](../../propagation/annotation/runs/security-profile-20260917/report.md)

### 聚焦审查 review

- [runs/focused-v1-20260929-121534/index.html](../../propagation/review/runs/focused-v1-20260929-121534/index.html)
- [runs/focused-v1-20260929-121534/report.md](../../propagation/review/runs/focused-v1-20260929-121534/report.md)
- [runs/repair-once-v1-20260929-132248/index.html](../../propagation/review/runs/repair-once-v1-20260929-132248/index.html)
- [runs/repair-once-v1-20260929-132248/report.md](../../propagation/review/runs/repair-once-v1-20260929-132248/report.md)

### 确定性传播

- [abstract-runtime-v1-20260928-143306/index.html](../../propagation/runs/abstract-runtime-v1-20260928-143306/index.html)
- [abstract-runtime-v1-20260928-143306/report.md](../../propagation/runs/abstract-runtime-v1-20260928-143306/report.md)
- [doe-input-v1-20260924-193407/index.html](../../propagation/runs/doe-input-v1-20260924-193407/index.html)
- [doe-input-v1-20260924-193407/report.md](../../propagation/runs/doe-input-v1-20260924-193407/report.md)
- [pilot3-v1-20260924/index.html](../../propagation/runs/pilot3-v1-20260924/index.html)
- [pilot3-v1-20260924/report.md](../../propagation/runs/pilot3-v1-20260924/report.md)
- [processing-v1-20260928-204710/index.html](../../propagation/runs/processing-v1-20260928-204710/index.html)
- [processing-v1-20260928-204710/report.md](../../propagation/runs/processing-v1-20260928-204710/report.md)
- [sink-boundaries-v1-20261002-185934/index.html](../../propagation/runs/sink-boundaries-v1-20261002-185934/index.html)
- [sink-boundaries-v1-20261002-185934/report.md](../../propagation/runs/sink-boundaries-v1-20261002-185934/report.md)
- [sink-tightening-v1-20261002-201445/index.html](../../propagation/runs/sink-tightening-v1-20261002-201445/index.html)
- [sink-tightening-v1-20261002-201445/report.md](../../propagation/runs/sink-tightening-v1-20261002-201445/report.md)
- [sink-tightening-v1-20261002-203802/index.html](../../propagation/runs/sink-tightening-v1-20261002-203802/index.html)
- [sink-tightening-v1-20261002-203802/report.md](../../propagation/runs/sink-tightening-v1-20261002-203802/report.md)
- [sink-tightening-v1-20261002-205045/index.html](../../propagation/runs/sink-tightening-v1-20261002-205045/index.html)
- [sink-tightening-v1-20261002-205045/report.md](../../propagation/runs/sink-tightening-v1-20261002-205045/report.md)
- [source-boundaries-v1-20260928-112118/index.html](../../propagation/runs/source-boundaries-v1-20260928-112118/index.html)
- [source-boundaries-v1-20260928-112118/report.md](../../propagation/runs/source-boundaries-v1-20260928-112118/report.md)

### 语义评测语料

- [corpus.json](../../corpus/semantics_review/corpus.json)
- [coverage_matrix.md](../../corpus/semantics_review/coverage_matrix.md)
- [provenance/README.md](../../corpus/semantics_review/provenance/README.md)

### 原位置保留的 legacy

- [旧 SFG/FCG 与 DOE 实验](../../legacy_sfg_doe/README.md)
- [旧设计文档](../../../docs/history/legacy-sfg-doe/README.md)
