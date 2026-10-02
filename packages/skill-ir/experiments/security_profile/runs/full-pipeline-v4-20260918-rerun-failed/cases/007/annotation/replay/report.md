# 安全语义标注：annotation

状态：**存在未决标注**（`incomplete`）

保留有依据的标注，存在未决项。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`97ee7d272d3c4269f245db6a9beb86d4b054b1c05e18d8c1d58b3dfdf940b117`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- `ir_003` / `effects`：index.search 的工具名称和调用记录未提供远程通信依据，无法确定是否发生 net_send/net_receive。
- `ir_008` / `effects`：return 的接收方未明确，普通 return 不能单独证明 user_output；也无法确定是否进入模型上下文，因此效果无法确定。

## 按块查看

### block_001 · Read the user-supplied request.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_request_json | agent_runtime | source | fs_read |
| ir_002 | dispatch | llm | [] | [] |

### block_002 · Call index.search with the supplied request parameters

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | index.search | tool | source, transformer | transform, model_observe |
| ir_004 | dispatch | llm | [] | [] |

### block_003 · Write the response total to count.txt and return the response items

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | extract_total_from_search_response | agent_runtime | transformer | transform |
| ir_006 | write_total_to_count_txt | agent_runtime | sink | fs_write |
| ir_007 | extract_items_from_search_response | agent_runtime | transformer | transform |
| ir_008 | return | agent_runtime | sink | [] |

## 标注依据

### ir_001

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：该IR为本地读取 request.json 的动作，由代理运行时执行。

> read_request_json

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：该动作从外部请求文件引入数据到当前过程。

> Read the user-supplied request.json

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0009`。
  理由：该动作读取 request.json 文件内容。

> request.json

### ir_002

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度动作，LLM 可参与调度；该规则说明调度本身不证明内容可见。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制转移，不向过程引入、变换或送达内容，无角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：仅控制流跳转，不执行读取、写入、网络、模型处理或输出等效果。

> dispatch

### ir_003

- `actor` / `tool`；依据 `cfg`，位置 `g_0015`。
  理由：IR 调用 index.search 工具，动作由该工具执行。

> index.search

- `roles` / `source`；依据 `cfg`，位置 `g_0015`。
  理由：工具输出 search_response，将搜索结果引入当前过程。

> search_response

- `roles` / `transformer`；依据 `cfg`，位置 `g_0015`。
  理由：搜索动作根据查询参数产生结果，承担变换角色。

> index.search

- `effects` / `transform`；依据 `cfg`，位置 `g_0015`。
  理由：以 request.term 作为查询参数并产生搜索响应，属于选择/计算变换。

> request.term

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：index.search 返回的 search_response 默认进入 LLM 上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_004

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度动作，LLM 可参与调度；该规则说明调度本身不证明内容可见。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制转移，不向过程引入、变换或送达内容，无角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：仅控制流跳转，不执行读取、写入、网络、模型处理或输出等效果。

> dispatch

### ir_005

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0021`。
  理由：该IR为本地字段提取操作，由代理运行时执行。

> extract_total_from_search_response

- `roles` / `transformer`；依据 `cfg`，位置 `g_0021`。
  理由：从搜索结果中提取 total 字段，承担变换角色。

> extract_total_from_search_response

- `effects` / `transform`；依据 `cfg`，位置 `g_0021`。
  理由：输出为从 search_response 选出的 total 值，属于选择/变换。

> response.total

### ir_006

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0022`。
  理由：本地文件写入动作由代理运行时执行。

> write_total_to_count_txt

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：该动作将 total 写入本地 count.txt，使内容到达存储位置。

> write the response's total value to local count.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0022`。
  理由：该动作创建/写入本地 count.txt 文件内容。

> write_total_to_count_txt

### ir_007

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0023`。
  理由：该IR为本地字段提取操作，由代理运行时执行。

> extract_items_from_search_response

- `roles` / `transformer`；依据 `cfg`，位置 `g_0023`。
  理由：从搜索结果中提取 items 字段，承担变换角色。

> extract_items_from_search_response

- `effects` / `transform`；依据 `cfg`，位置 `g_0023`。
  理由：输出为从 search_response 选出的 items 值，属于选择/变换。

> response.items

### ir_008

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0024`。
  理由：返回动作由代理运行时执行，将值交给调用方。

> return

- `roles` / `sink`；依据 `source`，位置 `src_003`。
  理由：该动作将 items 交给调用方，使内容到达接收边界。

> Return the search response's items value unchanged.

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
