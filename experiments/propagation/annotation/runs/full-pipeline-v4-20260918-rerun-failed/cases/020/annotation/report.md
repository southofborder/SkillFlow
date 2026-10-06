# 安全语义标注：annotation

状态：**存在未决标注**（`incomplete`）

保留有依据的标注，存在未决项。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`574547ff095741ab123aa95b75e0bdb9b7e34734fee4d025d9d2f545012eeec1`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- `ir_011` / `effects`：IR 仅记录交付到 delivery_path，未记录本地写入、远端发送或用户直接可见等机制；无法确定应标 fs_write、net_send 还是 user_output，故不猜测。

## 按块查看

### block_001 · Read the user-provided manifest.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_manifest_file | tool | source | fs_read, model_observe |
| ir_002 | dispatch | agent_runtime | [] | [] |

### block_002 · Extract document paths from the manifest paths list

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | extract_document_paths_from_manifest | llm | transformer | model_observe, transform |
| ir_004 | dispatch | agent_runtime | [] | [] |

### block_003 · Read output_dir and delivery_path from the request

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | read_output_and_delivery_from_request | agent_runtime | source | context_read |
| ir_006 | dispatch | agent_runtime | [] | [] |

### block_004 · Convert each document with scripts/convert.py and capture output paths

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | run_convert_script_for_each_document | tool | source, sink, transformer | fs_read, fs_write, transform, model_observe |
| ir_008 | dispatch | agent_runtime | [] | [] |

### block_005 · Package converted documents into bundle.zip with scripts/package.py

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | package_converted_documents_with_script | tool | source, sink, transformer | fs_read, fs_write, transform |
| ir_010 | dispatch | agent_runtime | [] | [] |

### block_006 · Deliver bundle.zip to the requested delivery path

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | deliver_bundle_to_delivery_path | tool | sink | [] |
| ir_012 | dispatch | agent_runtime | [] | [] |

### block_007 · Write converted paths to local receipt.txt and finish

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_013 | write_converted_paths_to_receipt | tool | sink | fs_write |
| ir_014 | return | agent_runtime | [] | [] |

## 标注依据

### ir_001

- `actor` / `tool`；依据 `cfg`，位置 `g_0009`。
  理由：该 opcode 表示读取外部 manifest 文件，由文件读取工具执行。

> read_manifest_file

- `roles` / `source`；依据 `cfg`，位置 `g_0009`。
  理由：该动作将外部 manifest.json 内容引入当前流程，起 source 作用。

> manifest.json

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0009`。
  理由：动作读取 manifest 文件内容。

> read_manifest_file

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：读取结果 result_001 是工具返回内容且无隔离标记，默认进入 LLM 上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_002

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0010`。
  理由：dispatch 是 CFG 控制流跳转，由本地运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：仅控制流跳转，不引入、变换或输出内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：仅控制流跳转，不读取、写入、发送、接收、展示或变换内容，无适用效果。

> dispatch

### ir_003

- `actor` / `llm`；依据 `cfg`，位置 `g_0015`。
  理由：该指令对已回传模型的 manifest 内容做语义提取，不是文件或网络工具，由 LLM 处理。

> extract_document_paths_from_manifest

- `roles` / `transformer`；依据 `cfg`，位置 `g_0015`。
  理由：从 manifest 内容选择并提取文档路径，改变数据表示，起 transformer 作用。

> extract_document_paths_from_manifest

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：输入 manifest_content 是上一步工具返回内容，已按假设进入 LLM 上下文，当前动作继续由模型处理该内容。

> Agent 工具执行返回的内容默认进入 LLM 上下文

- `effects` / `transform`；依据 `cfg`，位置 `g_0015`。
  理由：解析 manifest 并提取 paths 列表，生成文档路径集合，属于 transform。

> extract_document_paths_from_manifest

### ir_004

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：dispatch 是 CFG 控制流跳转，由本地运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：仅控制流跳转，不引入、变换或输出内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：仅控制流跳转，不读取、写入、发送、接收、展示或变换内容，无适用效果。

> dispatch

### ir_005

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0021`。
  理由：读取声明为 context_key 的运行时上下文键，由本地代理运行时取得调用者输入。

> read_output_and_delivery_from_request

- `roles` / `source`；依据 `cfg`，位置 `g_0021`。
  理由：该动作将请求中的 output_dir 和 delivery_path 引入当前流程，起 source 作用。

> output_dir

- `effects` / `context_read`；依据 `cfg`，位置 `g_0021`。
  理由：动作读取运行时上下文/调用者输入中的 output_dir 与 delivery_path。

> read_output_and_delivery_from_request

### ir_006

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0022`。
  理由：dispatch 是 CFG 控制流跳转，由本地运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：仅控制流跳转，不引入、变换或输出内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：仅控制流跳转，不读取、写入、发送、接收、展示或变换内容，无适用效果。

> dispatch

### ir_007

- `actor` / `tool`；依据 `cfg`，位置 `g_0027`。
  理由：该指令执行外部转换脚本，由脚本执行工具完成。

> run_convert_script_for_each_document

- `roles` / `source`；依据 `cfg`，位置 `g_0027`。
  理由：脚本读取源文档内容，将其引入转换过程，起 source 作用。

> source.read_text

- `roles` / `sink`；依据 `cfg`，位置 `g_0027`。
  理由：脚本将转换产物写入 output_dir，使内容到达存储位置，起 sink 作用。

> writes each converted UTF-8 text document to output_dir

- `roles` / `transformer`；依据 `cfg`，位置 `g_0027`。
  理由：动作执行文档转换，起 transformer 作用。

> Convert one UTF-8 text document

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0027`。
  理由：脚本读取源文档文件内容。

> source.read_text

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0027`。
  理由：脚本写入转换后的文件内容。

> output.write_text

- `effects` / `transform`；依据 `cfg`，位置 `g_0027`。
  理由：约束与动作表明对文档执行转换处理。

> 转换期间保留原文标题

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：脚本标准输出 result_005 是工具返回内容，默认进入 LLM 上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_008

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0028`。
  理由：dispatch 是 CFG 控制流跳转，由本地运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：仅控制流跳转，不引入、变换或输出内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：仅控制流跳转，不读取、写入、发送、接收、展示或变换内容，无适用效果。

> dispatch

### ir_009

- `actor` / `tool`；依据 `cfg`，位置 `g_0033`。
  理由：该指令执行外部打包脚本，由脚本执行工具完成。

> package_converted_documents_with_script

- `roles` / `source`；依据 `cfg`，位置 `g_0033`。
  理由：脚本将传入路径的文件读入 ZIP，起 source 作用。

> archive.write(path, arcname=path.name)

- `roles` / `sink`；依据 `cfg`，位置 `g_0033`。
  理由：脚本写入 bundle.zip，使内容到达存储位置，起 sink 作用。

> writes the ZIP archive to bundle.zip

- `roles` / `transformer`；依据 `cfg`，位置 `g_0033`。
  理由：动作将多个输入文件组合为 ZIP，起 transformer 作用。

> Build the explicitly requested ZIP from supplied output paths.

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0033`。
  理由：ZipFile.write 读取所提供文件内容。

> archive.write(path, arcname=path.name)

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0033`。
  理由：脚本创建并写入 ZIP 文件。

> writes the ZIP archive to bundle.zip

- `effects` / `transform`；依据 `cfg`，位置 `g_0033`。
  理由：将输入文件组合成 ZIP 归档，改变表示。

> Build the explicitly requested ZIP from supplied output paths.

### ir_010

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0034`。
  理由：dispatch 是 CFG 控制流跳转，由本地运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：仅控制流跳转，不引入、变换或输出内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：仅控制流跳转，不读取、写入、发送、接收、展示或变换内容，无适用效果。

> dispatch

### ir_011

- `actor` / `tool`；依据 `cfg`，位置 `g_0039`。
  理由：该交付动作由执行工具完成。

> deliver_bundle_to_delivery_path

- `roles` / `sink`；依据 `cfg`，位置 `g_0039`。
  理由：动作使 bundle.zip 到达请求的 delivery_path，起 sink 作用。

> delivers bundle.zip to the requested delivery_path

### ir_012

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0040`。
  理由：dispatch 是 CFG 控制流跳转，由本地运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：仅控制流跳转，不引入、变换或输出内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：仅控制流跳转，不读取、写入、发送、接收、展示或变换内容，无适用效果。

> dispatch

### ir_013

- `actor` / `tool`；依据 `cfg`，位置 `g_0045`。
  理由：该写本地文件动作由文件写入工具执行。

> write_converted_paths_to_receipt

- `roles` / `sink`；依据 `cfg`，位置 `g_0045`。
  理由：动作将数据写入本地 receipt.txt，使内容到达存储位置，起 sink 作用。

> receipt.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0045`。
  理由：动作创建并写入本地 receipt.txt 文件内容。

> writes the converted file path list to local receipt.txt

### ir_014

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0046`。
  理由：return 是 CFG 结束控制操作，由本地运行时执行。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0046`。
  理由：仅结束流程，不引入、变换或输出内容，无适用角色。

> return

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0046`。
  理由：仅控制返回，不产生词表所列效果。

> return

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
