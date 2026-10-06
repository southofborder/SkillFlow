# 013 / F01 助手复核

本文件为 **助手复核，非人工确认**。范围仅为本轮 `doe-input-v1-20260924-193407/cases/013` 的完整源文、当前 CFG、`propagation/doe-input.json`、`propagation/audit/annotation.json`、`propagation/audit/material.json` 中的 `wide-read-agent-v5` 执行模型，以及本轮来源、位置和初始数据审计材料。未修改代码、标注或历史结果，未调用远程模型。

结论：传播完成，18/18 个 IR 均已处理；新标注仍为 `incomplete`，四个 return 的接收方未决项完整保留，不能据此给出无条件 DOE 结论。工具请求实参、三次独立响应版本、整体工具结果进入模型的假设，以及四条返回路径前的状态追加均可追踪。主要待补证点是实际网络边界和最初读取的执行者／可见范围；本例没有把外部响应仅写成请求派生值的来源缺口。

## 1. 来源范围与最初可见性

- `ir_001` 从 `runtime_context:source_id` 读取 D018 并原样绑定 `result_001`；`ir_003` 从 `runtime_context:FAST_KEY` 读取 D008 并原样绑定 `result_002`，再由 D008 派生存在性结果 D006（`result_003`）。D018 和 D008 是两个独立的 opaque 来源，没有把 source_id 与密钥混为一个来源，也没有把整个运行时环境虚构为已读取。
- 源文第 1 步提供“用户请求”和“环境”来源，但当前 CFG 从已命名的 `context_key` 开始。D018 不是已建模的完整用户请求，D008 不是已建模的整个环境；其 `part_of/path` 均为空。这里能够确认的是两个值的来源与传递，不能把 CFG 的字段粒度反推为上游一定只见过这两个值。
- 标注将 `ir_001/ir_003` 判为 `agent_runtime`，理由是本地读取的 opcode；完整源文没有额外给出本地解析器、模型不可见凭据代理或隔离实现。`annotation/execution-boundary.json` 的 `kind: none` 也不提供这种保证。因此“这些内容确定未被模型观察”缺乏足够依据；同样不能仅因为由 LLM 调度就自动增加 model_observe（EM03）。若 DOE 涉及请求整体或原始密钥对模型的可见性，应保留此边界问题，不能仅靠这两个无观察事件的 read 得出否定结论。
- EM01 要求在没有明确范围限制或隔离时保留相关容器，且禁止由此推断整个运行时环境已被读取。复核建议保留“当前表示仅到命名值，相关请求容器及读取实现未建模”这一限制，不擅自添加请求字段、其他环境变量或具体敏感内容，也不默认缩小模型实际已接收的容器。

## 2. 实参隔离成立于当前调用边界；网络性质需要补证

| IR | 当前 deliver 的数据 | 当前接收位置 | 核对结果 |
| --- | --- | --- | --- |
| `ir_005` fast 首次调用 | D018 source_id、D008 FAST_KEY | `remote:fast.fetch` | 与源文第 2 步及 CFG 实参一致 |
| `ir_007` fast 重试 | D018 source_id、D008 FAST_KEY | `remote:fast.fetch` | 复用两个输入值，不混入首次响应或错误 |
| `ir_009` archive 调用 | 仅 D018 source_id | `remote:archive.fetch` | CFG 与 transfer 都排除 D008，满足“only argument”的实参要求 |

`ir_009` 入口的候选状态仍可能包含 D008 以及 fast 的响应版本；这不等于 archive 接收了它们。实际 deliver 明确只引用 `input[1]`，不是整个 entry_state。源文禁止向 archive 传密钥这一点由调用实参得到支持，而不是依赖禁止性声明自动执行清洗。

**网络分类待补证：** `loc_remote_fast_fetch/loc_remote_archive_fetch` 的位置依据只引用 `fast.fetch`、`archive.fetch` 名称及“调用该工具／发送实参”文字。完整源文没有 URL、HTTP、远程服务、网络协议或工具实现。当前 `net_send/net_receive` 与 `remote` 是标注已经作出的更强推断；EM06 明确规定仅工具名不足以证明远程网络通信。工具接收实参与工具返回内容的交互成立，但是否跨网络、具体接收者是谁不能视为已证实。该问题影响 DOE 的接收方和跨界判断，不应通过删除工具响应来源来处理。

## 3. 三份响应来源和模型观察保留正确

| 调用 | 整体响应 | body / error / status | 模型实际被交付的符号内容 |
| --- | --- | --- | --- |
| `ir_005` 首次 fast | D010 | D009 / D005 / D016 | D010 整体 |
| `ir_007` 重试 fast | D002 | D003 / D020 / D011 | D002 整体 |
| `ir_009` archive | D015 | D014 / D004 / D012 | D015 整体 |

三个 receive 均新建独立来源：D010 和 D002 的 `acquired_from` 为 `remote:fast.fetch`，D015 为 `remote:archive.fetch`；其输入依赖分别为 `{D018,D008}`、`{D018,D008}`、`{D018}`，关系均为 `possible`。body/error/status 随后才由各自完整响应 `derived`。这保留了外部新增内容来源，不能误写成“响应只是请求数据的计算结果”。网络位置分类的证据问题与新增内容来源是否存在是两个问题。

`ir_005/007/009` 的 model_observe 各自交付完整响应 D010/D002/D015，没有因为成功只 return body、失败只 return error 就把更早的工具观察缩成最终返回字段。依据是 EM02 的工具返回默认进入模型上下文假设，源文没有 local-only、句柄、隔离存储或模型不可见结果的例外。该观察是执行模型假设，不是本轮真实抓取轨迹。三个调用的 `llm` operator 由此获得依据，而不是仅由“LLM 发起调用”获得依据。

所有响应及派生输出均为 opaque，没有已知字段集或敏感数据集合。fast 响应对 D008 的 possible 依赖必须保留，但它不证明 FAST_KEY 明文回显，更不证明整个响应、body、error、status 都完整包含密钥。D006 的 derived 也不等于布尔值包含密钥字节。反向同样不能把 derived 或状态名称当作清洗证明。

## 4. 返回版本、状态追加与未知接收方

| 终止路径 | 返回前写入 | status.txt 新版本 | return 输入 |
| --- | --- | --- | --- |
| fast 首次成功 | `ir_011` 写 D016 | D013，由旧 D019 与 D016 派生 | `ir_012`：`result_004` / D009 |
| fast 重试成功 | `ir_013` 写 D011 | D017，由旧 D019 与 D011 派生 | `ir_014`：`result_007` / D003 |
| archive 成功 | `ir_015` 写 D012 | D007，由旧 D019 与 D012 派生 | `ir_016`：`result_010` / D014 |
| archive 失败 | `ir_017` 写 D012 | D001，由旧 D019 与 D012 派生 | `ir_018`：`result_011` / D004 |

四个终止块的指令顺序均为 append 后 return；没有成功后继续 fetch 的出边。标注的 write mode 均为 `append`。传播记录显示 `update: strong` 是当前位置绑定换成追加后的新版本，并非删除旧内容：每个新 Data 的 origin 仍包含 D019 和相应状态依赖。不能将 strong 更新误报为覆盖 status.txt，也不能将对旧内容的版本依赖误报为模型读取旧文件。

三个成功 return 都引用对应成功调用的 body，没有引用旧尝试 body、整体响应或 status；archive 失败引用自己的 error，未替换成先前 fast error。CFG 从相应 body/error 结果到 return 没有另一个内容变换步骤，因此“原样返回”的结构得到保留。由于返回没有已知接收位置，四个 return 的事件均为空，且明确保留 effects 未决项；不能把空事件解释为没有对外交付，也不能自动标为 user_output 或追加另一次 model_observe。

状态追加显式输入中没有 D008，满足“没有直接把密钥作为诊断参数写出”的窄结论。但 D016/D011 都从对 D008 有 possible 依赖的整体 fast 响应派生，且未建模明确清洗。故不能将源文“Never pass FAST_KEY … diagnostic output”直接当作“诊断内容已无密钥”的证明；也不能从 possible 链断言发生了密钥泄露。source_id 实参自身是否含有任何特定内容亦未知。

## 5. 分支、未知和求解近似

- CFG 将 retry 展开为单独 `block_004/ir_007`，没有回边。只有首次 transient failure 到达该块；首次 non-transient failure 或任何 retry failure 到 archive；凭据 absent 直接到 archive。archive 只有一个调用节点，失败即终止，没有 archive retry。这里没有循环近似需要展开成任意重试次数。
- 传播是所有 CFG 可能路径的合并表示，条件文字仍在 CFG 中，记录本身不是某次实际执行。archive 入口出现首次及重试结果候选不表示凭据缺失路径也执行了这些调用；body/error 同时有符号版本也不表示同一次调用同时成功和失败。D007 与 D001 是成功和失败两个不同写点的备选状态版本，不是先成功追加再失败追加。
- 四个 return 接收方 unknown 已显式保留；所有 20 个 Data 均 opaque。没有实际响应内容、工具契约、字段 schema、状态文本格式、实际状态值或模型可见性轨迹。body/error/status 的不同 Data 表明输出版本分离，`derived` 未建立精确字段路径，也不支持自行推断互斥字段的敏感性。
- `complete` 只表示当前标注与 CFG 下传播求解完成。实际网络接收边界、最初读取的执行者和可见范围、return 接收方尚不能由本结果补全。DOE 可使用上述已定位的值与交互，但需保留这些限制；不能将没有明确泄漏证据等同于已证明隔离或安全。

## 数据定位

上述 D 短名已与本例 `propagation/report.md` 的 Data 索引及 `doe-input.json` 核对。便于独立定位的关键完整 ID 如下：

| 短名 | 含义 | 完整 Data ID |
| --- | --- | --- |
| D018 | source_id | `data_dfaa5949e8b4ebcb0b50cc48cc1d9189722c22f579a26a59450ffaa4a70318be` |
| D008 | FAST_KEY | `data_927eeac282ee11acaedd9f3eaababf6ccccb07526c7605d5e507344e60895ad1` |
| D010 | 首次 fast 整体响应 | `data_988b518678387cc6e3b44363c746833a8aebcb49cb1d9ee2890fca51ab37b4aa` |
| D002 | 重试 fast 整体响应 | `data_181ff046a21b73458d9fbbf631f1d8cadb61dd11c5b6cd0be1159887051030e3` |
| D015 | archive 整体响应 | `data_c3f6c68cb7dae022811d9793485e5b954db4d38959afefa0cfe6d1aba431f1fd` |
| D019 | status.txt 原版本 | `data_e9b84936119238acb4c19fe88d341fc9fac10aeff3726badf22d9cc6ef72bacd` |
