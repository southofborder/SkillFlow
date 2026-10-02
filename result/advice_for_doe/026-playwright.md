# 026-playwright｜压缩评审

样例：**R02**；选定轮次：**第 1 次**。

[Skill ZIP](D:/projects/SkillFlow/dataset/skills/026-playwright.zip) · [CFG PNG](D:/projects/SkillFlow/result/ir-IPP/026-playwright.png) · [完整评审](D:/projects/SkillFlow/result/suggestions/026-playwright.md) · [选定 CFG 原记录](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910/trials/R02/deepseek-v4-flash-max/1/analysis.json)

**关键过程：**npx 前提检查 → wrapper 打开任务目标页面 → snapshot 取得 refs → 浏览器交互与产物捕获。示例网址和表单数据没有被固定为当前任务值。

- **判断前需要任务实例。** `ir_013` 的高层交互需与当前站点、会话、待填写/上传数据及接收对象关联。Skill 没有给出的真实表单值不能补造；浏览器快照、元素引用、上传正文属于不同对象，不能把“可读取页面”直接判为“已向网站发送页面内容”。

- **配置来源属于条件核查。** [references/workflows.md:74](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/playwright/references/workflows.md:74) 的默认配置与 --config 覆盖未完整保留。应记录这个来源缺口；只有证据表明配置改变会话、访问对象或数据流时，才据此调整暴露判断，不能把示例窗口尺寸升级为安全要求。

- **通用回溯继续检查恢复语义。** 新 refs 未继续消费、ref 失败后的重拍重试关系仍需核对。独立 wrapper 片段不自动构成漏调用；不为接通主入口而重复执行。恢复问题是否影响提交对象或重复发送，需由具体交互语义判断。

本页为外置评审意见，按[新版 DOE 需求草案](D:/projects/SkillFlow/result/advice_for_doe/README.md)整理；不作为标准答案，不替代通用语义回溯。
