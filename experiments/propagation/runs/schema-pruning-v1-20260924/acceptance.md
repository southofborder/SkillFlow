# 结构收紧的离线验收

日期：2026-09-24。本目录是 Data／位置／证据收紧的离线交付，不是新的真实标注实验。

- 全套命令 `python -X utf8 -m pytest packages/skill-ir/tests -q`：**1,811 passed in 741.87s**。
- 全套启动后新增的多位置操作数测试，在后续传播专项中一起验收：**109 passed in 20.16s**。
- Data 子集 168 项、标注核心 204 项、消费工具六文件 148 项通过；审查页追加浏览器回归后 35 项通过。子集之间有交叉，不相加。
- [离线示例](offline-demo/report.html)：13 条 IR、5 个位置、传播 complete、模型调用 0；重复生成内容一致。
- [Data 示例](data-demo.json)：16 份 Data，格式 `skillflow-data-v3`。
- [原文件摘要复核](protected-check.json)：9,220 个原文件未变化，没有缺失。

主说明与精简字段树见 [结构收紧验收与后续冗余审查](../../../../../../docs/SkillFlow-结构收紧验收与后续冗余审查.md)。

业务输入在 `offline-demo/inputs/annotation.json`，仅包含 profiles、locations、transfer_specs、unresolved。
位置证据单独保存在 `offline-demo/audit/location-evidences.json`；主页面将其放在折叠审计区。
示例由作者提供规格并核验引文，没有执行 Skill 或远程模型。

工具的本地 URL 策略阻止直接打开这份新 HTML；没有绕过，未宣称完成其手工截图审查。
自动审查页浏览器测试验证了新字段、独立审计区、默认折叠和注入文本转义。

“complete”和测试通过仅是工程结果，不证明模型语义判断正确，也不产生 DOE 结论。
