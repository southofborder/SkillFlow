# 001 / N01 助手复核记录

本记录是助手对本轮产物的只读复核，**不是人工确认、不是安全判定，也不是 DOE 判定**。复核没有调用模型、执行 Skill 或修改代码及既有产物；唯一新增文件为本记录。

结论：本例能够作为“整份文件来源 → 当前记录 → 显式字段选择 → 通知参数，以及计数写本地文件”的数据传播基线。未发现把未知整体自动缩成已知字段、把禁止泄漏声明当作删除操作、或把依赖关系当作完整明文包含的行为。需要保留两个边界：其一，标注把读文件和若干处理直接归为本地 runtime，但源文并未证明模型不可见；其二，循环和分支记录是合并后的候选抽象，不能当作一次实际运行的先后状态或发送次数。`complete`、空 `unresolved` 和空 `diagnostics` 均不消除这些边界。

复核材料为本目录的 `propagation/doe-input.json`、`propagation/audit/annotation.json`、`propagation/audit/initial-data.json`、`initial-state.json`、`data-identities.json`、`stats.json`、`accepted-call/call.json`、`annotation/inputs/material.json`、`annotation/inputs/cfg.json`、`annotation/inputs/package/SKILL.md`、`annotation/result.json` 和验证记录；另只读查看传播求解器的 CFG 连接与状态合并实现以确认分支近似。主文件内完整源文与本轮输入 `SKILL.md` 逐字一致，主文件 CFG 与本轮输入 CFG 一致；审计中的 profiles、locations、transfer_specs、unresolved 与本轮 annotation/result 的对应业务字段一致。

本轮记录为 12 / 12 IR processed，7 个 Data、3 个位置；`status=complete`、`unresolved=[]`、`diagnostics=[]`。标注结构验证通过，覆盖 12 profiles、12 transfer specs、9 atomic ops。以上是记录完整性事实，不证明每条语义推断正确。

报告短名沿用本轮 `propagation/report.md` 的排序，完整 ID 如下。

| 短名 | 完整 Data ID | 当前语义与绑定 |
|---|---|---|
| D001 | `data_5701747f0fab6fb817d644bfdd0a5dbcd7a26ff4246c5fbd13d58c5745bb5361` | 当前记录的 `recipient` 部分；`result_005` |
| D002 | `data_776994f403cc8368782c2872ec3d88f8bd76ca0ac20c97e0db9de4ad2bf55fa6` | `ir_003` 的当前记录；`result_002` |
| D003 | `data_93645e26b72f968e33f76514d8dff81fab4b2b3ff9b2c1744195076accc35446` | 当前记录的 `summary` 部分；`result_006` |
| D004 | `data_a869db224db06ba689293820f7f5978298524307873be02e06d612c68f728ec3` | `ir_010` 的处理条数；`result_007`，随后写入 `count.txt` |
| D005 | `data_d05515013b087ce86a19349812e8fe0ffbf819387b2ac5fd384c3651af5d23f4` | `storage:events.json` 的原始整体；`ir_001` 读取后绑定 `result_001` |
| D006 | `data_d269123004656fdac3dbc7ed8f145887b2d9d1b15fa6c62cce298b2d3b291c8b` | `ir_003` 的 `has_more_records`；`result_003` |
| D007 | `data_db18990088d0614d26d31f890687439fc33afcdf782dfe8a4585402568dd8c5e` | `ir_005` 的 `is_selected`；`result_004` |

## 实际发现与逐项核对

1. **源头范围保留正确。** `ir_001` 的 `read(loc_events_json)` 获得 D005，文件位置和 `result_001` 保持同一 Data 身份。D005 为 `opaque`，没有因后续只用 recipient / summary 而变成仅含这两项的完整对象。源文第 1 条明确声明每条记录还包含 `record_id`、`value`、`urgent`、`opted_out`、`access_token`；这些未生成独立 Data 不等于已被删除或不存在。此处未知范围是相关 `events.json` 整体，不应扩大为整个运行环境。

2. **当前记录的未知余部仍在。** `ir_003` 用 `compute` 从 D005 生成 D002 / D006，依赖均为 `derived`。动态“下一条记录”没有可证明的固定数字索引，未编造 `select_part([0])` 是合理处理。D002 最终是 `known_parts`，只显式列出 `recipient→D001` 和 `summary→D003`，但 `parts_complete=false`；这表示已知部分的增补，不能读取成 D002 仅剩两个字段。D002 的身份仍是 `ir_003` 计算结果，未被本轮细化另造为“清洗后的当前记录”。

3. **真正缩小通知输入的是显式选择。** `ir_007` 两个 `select_part` 的路径分别为 `["recipient"]`、`["summary"]`，分别产出 D001 / D003；原文第 4、5、8 条及 CFG `g_0027` 支持字段原值提取，没有摘要生成或改写。`ir_008` 只将这两个实际输入提交到 `loc_notify_send`，没有直接提交 D002 / D005。这里没有 `exclude_parts(access_token)`，也不应为了禁止声明补造该操作。可以确认外送实参来自所选字段；不能由此证明 summary 的实际字符串从不含与 token 相同或有关的内容，因为没有实际 events 数据。

4. **派生值与前序内容没有被混为同一版本。** `ir_005` 从 D002 生成选择判定 D007；`ir_010` 从 D005 生成计数 D004；D006 / D007 / D004 均为独立 `opaque` 派生结果，没有当作原始事件的别名。它们的 `derived` 记录只支持计算依赖，不能据此声称布尔值或计数包含原始整份文件、summary 或 access_token 的明文。本例实际没有 `possible` 依赖；其他场景中的 `possible` 同样只能表示未排除的影响，不能当作完整明文包含。

5. **模型可见性是标注推断尚未建立的边界。** 全部 12 个 IR 没有 `model_observe`，没有 `model_context` 位置。`ir_001` 的依据为 `read_events_json` 以及“未出现具名工具”“没有证据表明读取结果进入模型上下文”；`ir_003/005/007/010/011` 也主要通过操作名称及未出现具名工具推断本地 runtime。源文确实没有模型读取、模型摘要或模型改写的正面证据，因此不能机械补上观察；但源文也没有明确 local-only、模型不可见、句柄或隔离机制，操作名称本身不能证明执行主体及内容可见性。此项应作为后续 DOE 输入的未确定执行边界，不能把当前“未标观察”升级为“已证明模型没有见到 D005 / D002 / D001 / D003”。标注 `unresolved=[]` 未记录这一推断边界，属于标注层面的证据不足，传播引擎只是忠实传播了现有标注。

6. **逐条套用固定执行模型后，不能认定存在确定漏标观察。** `EM01` 支持相关文件整体读取，没有说每次文件读都自动进入模型。`EM02` 默认覆盖 agent tool 的返回内容，而本例唯一明确标成 `tool` 的 `ir_008` 在 CFG 中没有输出、源文没有声明通知工具返回内容，故不能凭工具调用凭空创建返回 Data 或观察事件。`ir_001` 也未明确为 agent tool 调用，不能把 EM02 条件当作已满足。`EM03` 支持 `ir_002/004/006/009` 的纯 dispatch 不因调度而观察；`EM04` 要求实际模型读取处理的证据，本例没有。`ir_012` 普通 return 没有 user output，与 EM06 一致；`ir_011` 文件写未自动加 context_write，与 EM07 一致。结论是“观察边界尚未证明”，不是“所有 runtime 操作都肯定漏标”。

7. **通知边界的值已分清，接收方身份仍是动态值。** `ir_008` 的 `net_send / deliver` 两组输入是 D001（接收对象参数）和 D003（body 原值），target 为 `remote:notify.send`。源文有向选中记录 recipient 发送通知的通信行为，不只是孤立工具名。此位置表示通知调用边界，不能当作已经解析出具体用户、域名、服务部署位置，或证明接收人可见 recipient 参数本身。通知工具没有返回数据记录；本轮没有依据推断发送完成回执及其观察。

8. **分支条件在 CFG 保留，但传播不证明条件求值或调用次数。** `ir_005` 的约束同时保留 `opted_out != true`、`urgent == true 或 value >= 100` 以及 urgent 不豁免 opted_out。CFG `block_003→block_004` 为 `is_selected is true`，false 回循环；`block_002` 的 has_more true / false 边也都在。求解器连接图使用 source/target，合并前驱状态，不按 `condition_text` 求值。因此所有可达 IR processed、`ir_008` 有发送事件，不代表所有事件记录都发送，也不能证明 opted_out 记录真的不会发送或每个选中记录恰好一次。这里属于传播近似，不能伪报为源 CFG 漏掉条件。

9. **循环合并解释了入口已有后续结果。** `ir_003.entry_state` 已含 `result_002` / D002、`result_003` / D006、`result_004` / D007、`result_005` / D001 和 `result_006` / D003，入口出口可显示没有变化；`ir_010` 入口也保留这些符号绑定。这是循环回边及候选状态合并的结果，不是证明首次进入循环前就已提取字段，也不是“本次未选中仍拿上一条记录发送”的实证。相同 `ir_003` 站点及相同抽象输入得到同一 D002，未为每个实际事件记录展开版本；当前产物无法逐条核验 recipient 与 summary 的跨迭代对应、处理条数或精确次数。

10. **本地计数写存在次级边界，尚不能当确定错误。** `ir_011` 把 D004 写入 `storage:count.txt`；审计 spec 用 `mode=replace`，理由是“无追加语义证据，按 replace 写入表示”，传播产生 `before=[]`、`after=[D004]`、`update=strong`。原文和 `g_0035` 确认本地写入，但未明确覆盖或追加；缺追加证据本身不构成明确覆盖证据。当前种子也未提供 count.txt 旧内容，因此 `before=[]` 是未绑定，不能解释为真实文件此前为空。可保留“结果按覆盖约定表示”的限制，不足以判定本例真实写错或实际丢失旧文件内容。

## 源 CFG 已有边界与本轮新增推断的区分

源文没有提供实际 events 数据；源 CFG 中迭代游标、实际迭代次数、notify 返回值、文件覆盖模式、执行主体与模型可见边界都没有具体化。`ir_010` 直接以整份 `result_001` 计算 `processed_count`，没有单独的成功通知计数器；源文只说“处理条数”，未定义为发送成功条数，因此不能据此认定 CFG 计数错误，也不能将 D004解释成成功发送数。这些是既有源文 / CFG 的表达边界。

本轮标注具体增加的是 runtime / tool 的主体推断、`notify.send` 的通信边界、字段选择、计算依赖及 count.txt 的 replace 约定。字段选择与依赖有直接源文 / CFG 依据；runtime 是否同时涉及模型内容观察、覆盖模式是否已确定则缺进一步证据。传播层的实际近似是路径不敏感的状态合并、循环站点复用及共享 Data 描述的细化。三类边界不应合并成“传播程序丢字段”。

后续可据此检查 D005 整体读、D002 保留未知余部、D001 / D003 的实际外送、D004 的本地写，并继续把模型观察可见性、循环 / 分支候选和文件写模式作为限制保留。没有证据支持宣称 access_token 已外泄，也没有证据支持宣称其从整份已读内容中被删除或从未对模型可见。
