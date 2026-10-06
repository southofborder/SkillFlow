# 联合标注聚焦审查实验

使用已经完成的联合标注作为只读输入，每图一次独立审查，检查范围、数据关系与观察／交付绑定。显式 `refine` 编排在初审发现具体问题时最多完整修复一次，再独立复审。历史标注、传播和 DOE 文件不修改。

当前通用入口为 `python -m skillflow.propagation.review prepare/run/replay/refine`，读取当前 v10 标注及编译清单，审查边界属性、数据关系和观察版本；最多一次修复后独立复审，原标注不回写。sink 的类型和 exposure_level 由程序固定生成，审查模型检查属性依据而不重新自由打分。

下面 `tools/propagation/review/run_repair_once.py` 与 `tools/propagation/review/repair_candidates.py` 固定三份原候选和四个受控变体，属于 2026-09-29 的七例实验。它们从当时已冻结且通过旧加载器核验的材料显式重建，不是新版位置属性的通用迁移入口；旧候选不能在缺少新边界依据时补字段后冒充新版标注。
旧 `run_focused.py` 和其专属 fixtures 已移除，历史 focused-v1 运行及实际响应保留，不另保留可执行旧流程。

七例每例最多初审、完整修复、复审三次调用，另对三个既有 CFG 各核对一次，计划上限 24 次。新版源文核对不重新提取、不修复 CFG；所有真实调用使用 JSON Output。外置来源说明、人工预期、历史助手意见不进入审查输入。

```powershell
python -m tools.propagation.review.run_repair_once prepare --run-dir <已冻结本轮上游材料的目录>
python -m tools.propagation.review.run_repair_once run --run-dir <同目录> --env-file .env
python -m tools.propagation.review.run_repair_once replay --run-dir <同目录>
```

`prepare` 不会重新创建已准备目录，`run` 恢复已接受响应、不自动重发；`replay` 零 API。原候选的诊断传播明确标为重建材料，修复候选使用真实接受响应。未提交传播文件不冒充成功，单例失败保留原因并继续其他案例。

运行方式和结果边界见[主规范](../../../docs/propagation/SkillFlow-联合标注三任务聚焦审查.md)。`runs/` 只新增运行，不覆盖历史材料。`complete` 是审查执行与格式检查完成，不意味着待审标注语义正确。
