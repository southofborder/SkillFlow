# ClawHub 隐私审计对比实验

当前批次在 100 个复杂 ClawHub Skill 上比较直接强模型、Semia 和 SkillPrivus。直接强模型先完成 100 例，随后启动其余两组在线运行。三组现均已达到终态。[三组对比报告](reports/audit-01/summary.md)

| 方法 | 当前入口 |
| --- | --- |
| 直接强模型 | [调用与产物说明](methods/strong-model/README.zh.md) · [本批次运行状态](runs/strong-model/direct-audit-01/summary.json) |
| Semia | [复刻入口](methods/semia/README.zh.md) · [本批次运行状态](runs/semia/semia-audit-01/summary.json) |
| SkillPrivus | [按论文方法复刻](methods/skillprivus/README.zh.md) · [本批次运行状态](runs/skillprivus/paper-based-controlled-01/summary.json) |

## 目录

- [study.json](study.json) 登记方法和当前阶段。
- [inputs/clawhub-complex.json](inputs/clawhub-complex.json) 固定 100 个 ClawHub 包的原始版本、来源回执、逐文件哈希和排序条件。按实现文件非空行数排序，筛选与文本送模兼容的完整包。源码来自已有的官方版本包下载缓存。
- [inputs/cohort.json](inputs/cohort.json) 保留 `001`、`010`、`013`、`ga4` 四例早期工程记录的输入索引。
- [runs/](runs/README.zh.md) 按方法和新运行 ID 保存实际输入、原始输出与回执。
- [reports/](reports/README.zh.md) 约定对齐后的事实、状态和汇总位置。

`study.json` 中的路径相对于本目录，样本清单中的路径相对于仓库根目录。

## 共同输入

三个方法从同一完整源码快照出发，以源码声明的用途为依据，记录实际送模的文件和内容。源码作为静态分析材料。结果按源包哈希对齐，模型、调用预算和观察假设按实际条件记录。

Semia 补跑范围为原批次受 CLI 传输故障影响的 94 例，使用原清单中的完整源码。三组更新汇总复用强模型、SkillPrivus 以及 Semia 其余 6 例的封存结果。[路由与超时诊断](reports/semia-transport-recovery/diagnosis.md) · [补跑状态](runs/semia/semia-recovery-01/summary.json)
