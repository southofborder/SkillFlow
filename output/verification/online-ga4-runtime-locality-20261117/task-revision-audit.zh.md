# Task 修订的只读核对

修订 Task 首次答复通过结构及源文坐标校验，未使用纠错或正规化，仍为 `skillflow-task-v5`。这是 Task 阶段接受，不代表整链语义正确或执行完成。快照时修订 CFG 仍在运行，尚无新的任务对应结果。

需求由 **49 条变为 60 条**；issues 由 **10 条变为 12 条**，其中已解决 7→8，未解决 3→4。新增 13 个需求 ID、移除 2 个、共有 47 个；包含实时报告拆分、保存义务拆分和更名，不能把净增 11 条直接理解为新增 11 项业务义务。共有需求中，43 条文字、46 条完整记录发生变化。协议允许完整替换并复核其他内容；本次只读审计不证明所有改写均正确。

隔离保持：实际调用 prompt 与保存的输入 prompt 字节相同；源文输入只有 `source_files`，完整 16 文件可逐一还原为本轮源文件的相同字节，共 155,170 UTF-8 字节。修订数据只有 `previous_task` 和三条 `objections`。前者与本轮 `inherited/task/task.json` 完全相等；后者仅含有限代码、源文位置、需求 ID，与初始源文审查的三条 Task objection 投影一致。没有把审查解释、建议、CFG、processing、传播或 DOE 材料传给 Task。原 145 处和新 182 处证据引用均落在实际源文件有效行范围内；坐标有效不等于语义依据已经充分。

三项意见的处理分别是：

1. **`.env` 文件位置**：新增 `project_environment_file`，保留项目根目录建文件、运行时按工作目录加载及私钥换行转换。将项目根目录作为工作目录，是结合 `SKILL.md:16–24` 与 `settings.ts:5–9` 作出的协调解释，不能据此证明其他工作目录也可正常加载。
2. **独立接口遗漏**：新增 `build_bulk_path_filter`、`granular_api_access`、`entry_point_invocation`，并保留独立路径正规化。过滤器明确对已正规化路径生成 `pagePath` 不区分大小写的成员过滤，空列表返回 `null`；没有声称过滤器自己正规化或访问 GA4。依据为 `api-reference.md:317–339`、`bulk-lookup.ts:78–98`、`SKILL.md:39–51,100–102`。
3. **每个输入 URL 的输出覆盖**：保留 `bulk_page_metrics` 的逐页结果义务，新增未解决的 `bulk_path_result_coverage`。它指出文档“每个 URL”与实现直接返回 SDK 结果的差别，保留未匹配路径、重复输入和一条路径多个标题时应如何覆盖的歧义；没有虚构补零行、占位结果或输入顺序保证。依据是 `api-reference.md:341–352` 与 `bulk-lookup.ts:149–192`。

第三项通过**明确保留未解决输出义务**得到回应，不能记为已解决。原有排名、按查询的设备粒度、按页面的国家粒度三个未解决 issue 也都保留。新增 `configured_date_default` 则区分可配置默认值与 `30d` 出厂回退，被标为已解决。

`summarize_saved_analysis` 同样没有消失：分析并保存之后，仍须读取相关 JSON，在 `results/summaries/` 生成含表格、趋势和建议的 Markdown，继续引用 `SKILL.md:53–64,118–127`。新的任务对应尚未生成，不能提前说该输出已表达或完成。文档 filters/order 冲突的 Task 解释已解决，也不代表源码已经满足这些控制要求。

这四项未解决问题都有具体源文及需求范围，属于有依据的局部语义问题。**另一个问题是程序如何传播它们**：当前 `demand_engine.py:643–645` 将每个未解决 Task issue 生成无 IR 范围的 `task_source_issue`；`limitations.py:117` 与 `input_assessments.py:344–345` 将它作为全局阻碍，没有按 issue 的需求 ID 判断相关性。因此，若最终选用这份 Task，即使后续 realization 全部 expressed，这四项也会单独阻止所有输入的删除判断。这是独立的保守精度限制，不是所有字段都依赖这些歧义的证明。

详细记录、来源及哈希见 [task-revision-audit.json](task-revision-audit.json)，英文说明见 [task-revision-audit.en.md](task-revision-audit.en.md)。本次只读本轮新目录中的材料；未调用历史 Task 读取器、项目模块、校验器、测试、后端、模型、Skill 或重放，未修改冻结文件。
