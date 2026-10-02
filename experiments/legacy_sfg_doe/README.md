# 旧 SFG/FCG 与 DOE 实验记录

本目录只保存已退役实现的历史非代码产物，不参与当前 Skill-IR 的输入、测试或运行，
不提供旧实现、旧入口或重放兼容代码。

`records/` 保存从旧包的临时实验目录中迁出的 JSON、日志与结果，保留原始字节。
目录名 `m4tmp`、`m4gate`、`necessity-probe` 对应旧包中的同名隐藏目录。
旧测试专用 fixture、依赖缓存、脚本与评分实现已删除，没有作为另一套代码归档。

[cleanup-manifest.json](cleanup-manifest.json) 记录原路径、现路径、SHA-256、
清理范围和受保护文件数量。旧设计文档位于
[docs/history/legacy-sfg-doe](../../docs/history/legacy-sfg-doe/README.md)。

当前能力与验证结果见 [当前状态](../../docs/当前状态与旧代码清理-2026-09-15.md)。
历史评分和标签不作为新 DOE 的判定标准。
