# 027-gh-fix-ci｜压缩评审

样例：**R03**；选定轮次：**第 1 次**。

[Skill ZIP](D:/projects/SkillFlow/dataset/skills/027-gh-fix-ci.zip) · [CFG PNG](D:/projects/SkillFlow/result/ir-IPP/027-gh-fix-ci.png) · [完整评审](D:/projects/SkillFlow/result/suggestions/027-gh-fix-ci.md) · [选定 CFG 原记录](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910/trials/R03/deepseek-v4-flash-max/1/analysis.json)

**关键过程：**仓库认证 → 选定 PR → 脚本或手工读取失败检查与 GitHub Actions 日志 → 摘要/修复计划 → 明确批准后实施。外部检查服务只报告 URL 的范围限制仍保留。

- **优先核对来源与读取范围。** 手工路径 `ir_011` 的缺省 PR、run/job 标识来源较弱，应能追溯到当前仓库与所选 PR，且遵守外部服务不调查的限制：[SKILL.md:33](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/gh-fix-ci/SKILL.md:33)、[SKILL.md:48](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/gh-fix-ci/SKILL.md:48)。脚本路径已有完整代码，不能把手工缺口扩大到两条路径。

- **修正原评审：合流不要求两支同时执行。** `ir_013/ir_015` 的两组输入可按可能来源理解；保留来源及分支条件即可，不强制 phi。失败摘要是否随计划展示给用户，需要看实际输出内容；图上没有单独“展示摘要”节点不足以证明全部日志外发。

- **批准门控是已保留的重要证据。** `ir_017/ir_018 → ir_020 → ir_022` 保留批准后实施，不应改写成未授权修改。字段降级、错误恢复等细节交由通用回溯；新 DOE 另需知道日志片段的实际载荷、接收方和任务所需范围，不能把修复批准解释为允许任意转发日志。

本页为外置评审意见，按[新版 DOE 需求草案](D:/projects/SkillFlow/result/advice_for_doe/README.md)整理；不作为标准答案，不替代通用语义回溯。
