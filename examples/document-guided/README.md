# 同一分析的分步 Prompt：离线样张

请从[中文入口](index.html)开始。七次请求是独立 Task、流程文档、完整 CFG wire、processing 片段、任务对应片段、敏感性片段和统一 source review。程序从三份实际类型化片段组装 annotation，没有 annotation 模型调用；不按业务分组拼接 CFG 或标注批次。

GA4 部分保留历史文字开发笔记，明确不是当前 typed fragment target，也不是接受的模型响应；synthetic/ 是独立设备校准 fixture 的作者合成片段、schemas、程序组装与七份实际模板。assembled-annotation.json 与兼容文件 flat-annotation.json 都是程序组装，annotation.json/backend-annotation.json 是程序展开；空 findings 是格式演示，不是审查通过。源文与历史 Task 保持原字节，原文样张范围保持；旧生成批次文件已从当前样张中移除，历史实验未修改。

规模使用字符和 UTF-8 字节，不预测 token 或成本。复现命令为 `python -m tools.doe.prepare_document_guided_sample --source-root <frozen-package> --legacy-task <historical-task.json> --output examples/document-guided --refresh`，可附 `--audit-run <saved-graph-audit>` 只读比较逻辑 Prompt 规模。生成器不构造模型客户端。
