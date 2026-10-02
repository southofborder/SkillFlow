# 024-document-bundle-delivery｜压缩评审

样例：**D06**；选定轮次：**第 1 次**。

[Skill ZIP](D:/projects/SkillFlow/dataset/skills/024-document-bundle-delivery.zip) · [CFG PNG](D:/projects/SkillFlow/result/ir-IPP/024-document-bundle-delivery.png) · [完整评审](D:/projects/SkillFlow/result/suggestions/024-document-bundle-delivery.md) · [选定 CFG 原记录](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910/trials/D06/deepseek-v4-flash-max/1/analysis.json)

**关键过程：**manifest.paths → 逐文档转换 → stdout 产物路径集合 → bundle.zip → 请求中的 archive_path。另将转换产物路径列表写入 receipt.txt。不得改输入原文、不得上传外部服务的全局限制，以及转换阶段保留标题的局部限制均保留。

- **主要判断：未确认遗漏整段关键数据处理或交付过程。** `ir_007` 的逐项转换与集合输出可作为高层操作；不要求显式循环。后续分析需保留“每个源文件内容→对应转换文件→入包内容”的来源关系，不能把路径字符串直接等同文件正文，也不能因为图不展开脚本就认定正文未处理。

- **目标差异必须保留。** `ir_011` 使用 `archive_path`，符合 [SKILL.md:13](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D06/SKILL.md:13)；此前读取 `delivery_path` 不代表它也被交付使用。不得为消除未使用值而换回旧目标。具体路径是否跨越信任边界，要由任务和运行环境补充，不能仅凭变量名判断。

- **通用回溯继续保留的问题：** [SKILL.md:17](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/controlled/D06/SKILL.md:17) 的“必要时保留原顺序”被列为全局限制，但适用对象仍不明。应保留这种不确定性；现无证据表明它改变载荷、接收方或访问范围，暂不据此阻塞 DOE 需求设计。

本页为外置评审意见，按[新版 DOE 需求草案](D:/projects/SkillFlow/result/advice_for_doe/README.md)整理；不作为标准答案，不替代通用语义回溯。
