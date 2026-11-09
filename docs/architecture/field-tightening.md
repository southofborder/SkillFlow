# 原文任务基准与需求转译的字段职责

当前 Task 只从完整冻结 Skill 提取并封存，以其声明用途为目的依据。外部任务入口、固定依据标签和逐行填表已删除；真实 Skill 内的运行输入仍保留。历史运行不迁移，原始文件保持不变。

```text
Task 提取输入：source
Task v5：purpose / requirements / issues / 来源及版本身份
标注输入：source / cfg / runtime_contract / 已封存 Task
当前模型 wire：realizations（补充对应、限制和 gaps）/ demands / expressions /
               IR → segments → ops / locations（内联证据）
程序展开的原始规格：task_revision_id / realizations / demands / expressions /
                    ir_semantics / locations / location_evidences
canonical 编译标注：task_ref / realizations / 归一化 demands、expressions /
                    ir_semantics / locations / sink_boundaries / location_evidences
编译映射：events / goals（raw_pointer → goal_id / requirement_id / target）
当前统一审查：findings（domain / target_ids / source_refs / explanation / suggestion）
需求推导：seed_goal_id / requirement_id / node / property / path / parents / rules
```

Task 是唯一任务释义，requirements 不含 CFG bindings。realizations 对每项要求恰好一条，区分 expressed、partial、retained_only、unmapped，缺口引用源文。正向 preserve 仅 value、presence、cardinality、shape、truth、action；登记禁止事项不制造读取或交付禁用数据的需求。

当前 wire 不填写 realization status、Task hash、operator、operator_evidences 或 empty_effect_evidences；状态、版本与 effect 层由程序展开。需求声明及其目标提供普通对应，模型只补额外 binding 和缺口。证据就近继承，源文新判断仍须真实引用。旧独立审查的 requirement_checks/declaration_checks/reviewed_ir_ids 属于兼容接口，不用于当前七调用源文审查。

Task 修订输入仅允许旧 Task、原始材料及有限类别/source_spans/requirement_ids；不接收审查自由解释、CFG、旧 demands 或 DOE。Task 改动后旧标注失效，完整重建。每条需求推导属于一个 seed，父推导不得跨 seed；报告可以汇总但保留来源。

程序检查真实物理行引用、审查发现、Task 版本、编译映射、推导和保存链；不要求模型重复登记每行源文。完整原文仍交给独立审查，遗漏通过具体 finding 报告。引用有效不证明自然语言完整性、需求不可替代性、路径可行性或禁止事项实际满足。教学样例与效果评测分开。

当前版本：document-guided run v8、step/annotation v7，fragment/wire v3，fragment review v2；内层 annotation run/profile v21，runtime v10，processing compiler/mapping v12，Data v6，propagation records v15，propagation run/format v20，DOE run/format v7。Task v5、Task extraction v3 和已有 CFG 的联合 pipeline v9 保留各自身份。显式循环摘要、类型化接口与嵌套 each 需求路径只用于新产物，不迁移或重新标记旧产物。

现行完整规范见 [Task evidence](../doe/task-evidence.md)、[反向需求](../doe/backward-demand.md)、[分析链](../doe/joint-pipeline.md)。
