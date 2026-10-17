# 原文任务基准与需求转译的字段职责

当前版本将 Task 从联合标注模型移至独立 source-only 提取阶段。下列协议替换此前联合响应中的 Task 正文与 constraint/prohibit 正向 goal。历史运行不迁移，原始文件保持不变。

```text
Task 提取输入：source / user_request / 程序选定 basis
Task v3：purpose / requirements / source_accounting / issues / 源与任务摘要
标注输入：source / cfg / runtime_contract / user_request / 已封存 Task
原始标注：task_revision_id / realizations / demands / expressions /
          ir_semantics / locations / location_evidences
canonical 编译标注：task_ref / realizations / 归一化 demands、expressions /
                    ir_semantics / locations / sink_boundaries / location_evidences
编译映射：events / goals（raw_pointer → goal_id / requirement_id / target）
审查：source_checks / requirement_checks / goal_checks / reviewed_ir_ids / findings
需求推导：seed_goal_id / requirement_id / node / property / path / parents / rules
```

Task 是唯一任务释义，requirements 不含 CFG bindings。realizations 对每项要求恰好一条，区分 expressed、partial、retained_only、unmapped，缺口引用源文。正向 preserve 仅 value、presence、cardinality、shape、truth、action；登记禁止事项不制造读取或交付禁用数据的需求。

Task 修订输入仅允许旧 Task、原始材料及有限类别/source_spans/requirement_ids；不接收审查自由解释、CFG、旧 demands 或 DOE。Task 改动后旧标注失效，完整重建。每条需求推导属于一个 seed，父推导不得跨 seed；报告可以汇总但保留来源。

程序检查真实引用、源文物理行登记、逐项审查记录、Task 版本、编译映射、推导和保存链；它不证明自然语言完整性、需求不可替代性、路径可行性或禁止事项实际满足。教学样例与效果评测分开。

现行完整规范见 [Task evidence](../doe/task-evidence.md)、[反向需求](../doe/backward-demand.md)、[分析链](../doe/joint-pipeline.md)。
