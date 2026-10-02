# 010 catalog-query｜面向新 DOE 的简评

样例：**Q04**；所选轮次：**第 1 次**。[原语义评审](D:/projects/SkillFlow/result/suggestions/010-catalog-query.md) · [ZIP](D:/projects/SkillFlow/dataset/skills/010-catalog-query.zip) · [PNG](D:/projects/SkillFlow/result/ir-IPP/010-catalog-query.png)。

核心链：读取 request.json，`block_002` 按两个可选字段的存在性四选一，经 `ir_010/ir_016/ir_022/ir_026` 中对应的一次搜索，再写本次 total、返回本次 items。[workflow 第 7 行](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q04/references/workflow.md:7)要求单次调用；[query.yaml](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/Q04/query.yaml:1)仅规定缺失实参省略。

未发现已证实的关键过程缺口。新 DOE 应沿互斥路径理解实际服务调用与结果来源：四个节点不代表同次任务调用四次，各分支输出也不能串成同时存在的载荷。

- 保留存在参数原值传递、缺失参数省略，以及同一路响应分别用于文件和返回；静态配置不是新增运行时外发。
- 分支展开数量、工具名与日期验证细节降级，不强求统一汇合或新字段。继承 index.delete 禁令，fuzzy 能力说明不变成实际处理；默认参数及异常值规则不由 DOE 补造。

本页为 Codex 外置意见。静态可能不等于真实泄露；通用双向语义回溯仍核对原文与 IR 的一般保真。

