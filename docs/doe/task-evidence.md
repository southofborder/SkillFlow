# 独立 Task 与原文依据 v5

当前 Task 只依据完整冻结的 Skill 源包建立。它解释 Skill 声明的用途和要求，不引入独立用户请求，也不把 Skill 声明视为真实用户授权。来源固定，因此不再保存 `basis` 字段。

## 模型声明与来源隔离

Task 提取和隔离修订不接收 CFG、当前载荷、标注、传播或 DOE。模型只返回：

```text
CandidateTask
├─ purpose: text / evidences[]
├─ requirements[]: id / text / evidences[]
└─ issues[]: id / kind / evidences[] / requirement_ids[] / resolution / reason
```

要求按可分别遗漏或放宽的义务组织，同时保留原值、条件、范围、次数、顺序、质量、副作用、禁止事项及同元素关系。能力说明、示例和当前实现事实不自动成为要求；实现步骤中的精确义务也不能被忽略。必要动作不豁免其全部载荷，真实整值要求也不能为了缩减结果而被缩小。

源包内部的冲突保留双方证据、受影响要求和处理理由，未解决问题保留在 `issues`。Task 不含图绑定、demands 或敏感性声明。

## 原文引用

证据使用 `file / start_line / end_line / reason`。文件必须来自冻结的 `skill/<实际相对路径>`；行范围从 1 开始，包含两端。程序用同一物理行定义校验和提取原文，保留 LF、CRLF、无末尾换行及原语言。跨文件依据分别引用，不复制引文、段落 ID 或逐项摘要。

不要求逐行登记。未引用的背景可以保留，未引用范围也不直接证明遗漏。模型仍须检查完整源文，审查可以用具体 finding 报告遗漏条件、禁止事项或错误解释。

## 封存与接口

程序为 CandidateTask 添加 `schema_version / source_sha256 / task_sha256`。源文摘要绑定冻结输入，Task 摘要绑定除自身外的完整 Task；下游通过 `TaskReference` 引用该精确版本。没有用户请求正文、请求摘要或替代目的标志。

| 材料 | 当前身份 |
|---|---|
| Task | `skillflow-task-v5` |
| TaskReference | `skillflow-task-reference-v3` |
| Task 输入材料 | `skillflow-task-material-v3` |
| Task 提取／修订运行 | `skillflow-task-extraction-v3`，格式 3 |

`skillflow.task` 提供 `prepare_task_material(source)`、`extract_task(source, client=...)`、隔离修订，以及 `prepare_task_run / run_task / load_task_run / replay_task`。正式流程入口见[完整分析链](joint-pipeline.md)。旧字段、旧版本和已移除的输入参数直接拒绝；历史实验不迁移或回写。

固定 Task 交给后续标注。模型响应只返回 `task_revision_id`，不重写 Task；编译响应保存 `task_ref`。图中对应、正向 demands 和受支持限制放在后续标注及 `realizations` 中。Task 由独立运行持有，下游引用其 owner；展示副本不是第二份可编辑任务基准。

## 隔离修订

Task 问题只通过有限 `code`、原文 `source_spans` 和已有 `requirement_ids` 传给修订器。修订器读取完整源文和旧 Task，不接收审查自由文本、建议、CFG、操作、sink、载荷、demands 或 DOE。它须独立核查并返回完整替换 Task。

Task 改变后，依赖它的标注和需求必须重新生成，不能机械迁移旧绑定。原版本和审查记录保留，继续遵守正式流程的语义修复预算。

## 保证边界

程序校验结构、精确来源、引用、封存身份、恢复和零调用重放。它不证明解释正确、要求穷尽、不可替代性、最小信息范围或不存在 DOE。真实 Skill 仍可能混合用途与实现；独立提取能隔离下游分析结果，不能消除原文自身的语义偏差。

已保留的离线回归包括跨文件及多语言证据、同一行多项要求、冲突引用、旧字段和版本拒绝、篡改拒绝、接受后无重发恢复，以及只读加载与重放。模型语义效果须另外评估，不能由结构检查通过代替。
