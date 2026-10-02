# 安全语义标注：annotation

状态：**标注记录完整**（`complete`）

标注记录完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`795fd2d72a4bd9f13c5eb79fc8c9ef99ed8d8b8437dc48ac38903d39e84e5968`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

没有记录未决项或执行问题；不等于模型标注已经人工确认。

## 按块查看

### block_001 · Read the user-provided manifest.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_manifest_file | agent_runtime | source | fs_read |
| ir_002 | dispatch | llm | [] | [] |

### block_002 · Extract document paths from the manifest paths list

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | extract_document_paths_from_manifest_paths_list | agent_runtime | transformer | transform |
| ir_004 | dispatch | llm | [] | [] |

### block_003 · Read output_dir and delivery_path from the request

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | read_output_dir_and_delivery_path_from_request | agent_runtime | source | context_read |
| ir_006 | dispatch | llm | [] | [] |

### block_004 · Convert each document with scripts/convert.py and capture stdout

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | run_convert_script_for_each_document_and_capture_stdout | tool, agent_runtime, llm | source, sink | fs_read, fs_write, model_observe |
| ir_008 | dispatch | llm | [] | [] |

### block_005 · Package converted artifacts into bundle.zip using the reference command

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | run_package_script | tool, agent_runtime | source, sink, transformer | fs_read, fs_write, transform |
| ir_010 | dispatch | llm | [] | [] |

### block_006 · Deliver bundle.zip to the requested delivery_path

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | deliver_bundle_zip | agent_runtime | sink | fs_write |
| ir_012 | dispatch | llm | [] | [] |

### block_007 · Write the converted artifact path list to local receipt.txt

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_013 | write_receipt_file | agent_runtime | sink | fs_write |
| ir_014 | return | agent_runtime | [] | [] |

## 标注依据

### ir_001

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：读取外部 manifest 文件是本地 I/O 动作，由代理运行时执行。

> read_manifest_file

- `roles` / `source`；依据 `cfg`，位置 `g_0009`。
  理由：该动作将 manifest.json 内容引入当前过程。

> manifest.json

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0009`。
  理由：opcode 表明读取 manifest 文件内容。

> read_manifest_file

### ir_002

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：调度动作由 LLM 参与选择下一执行块。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制转交，未向过程引入数据、未使内容到达接收或存储、未处理内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制操作，未记录读取、写入、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_003

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：本地提取/筛选 manifest 中的 paths 列表，由代理运行时处理。

> extract_document_paths_from_manifest_paths_list

- `roles` / `transformer`；依据 `execution_model`，位置 `EM04`。
  理由：从 manifest 内容中选取 paths 列表生成文档路径，属于处理/变换。

> 本地字段筛选

- `effects` / `transform`；依据 `execution_model`，位置 `EM04`。
  理由：对已有内容进行字段筛选/组合，标注 transform。

> 本地字段筛选

### ir_004

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：调度动作由 LLM 参与选择下一执行块。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制转交，未向过程引入数据、未使内容到达接收或存储、未处理内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制操作，未记录读取、写入、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_005

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0021`。
  理由：从运行时上下文/请求读取配置，由代理运行时执行。

> read_output_dir_and_delivery_path_from_request

- `roles` / `source`；依据 `cfg`，位置 `g_0021`。
  理由：将请求上下文中的 output_dir 和 delivery_path 引入当前过程。

> output_dir

- `effects` / `context_read`；依据 `cfg`，位置 `g_0021`。
  理由：读取运行时上下文/调用者输入。

> context_key

### ir_006

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：调度动作由 LLM 参与选择下一执行块。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制转交，未向过程引入数据、未使内容到达接收或存储、未处理内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制操作，未记录读取、写入、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_007

- `actor` / `tool`；依据 `cfg`，位置 `g_0027`。
  理由：具体脚本作为工具执行转换。

> scripts/convert.py

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0027`。
  理由：本地运行时逐个调用脚本并捕获标准输出。

> run_convert_script_for_each_document_and_capture_stdout

- `actor` / `llm`；依据 `execution_model`，位置 `EM02`。
  理由：脚本标准输出作为工具结果默认回传 LLM 上下文，模型参与观察。

> 默认进入 LLM 上下文

- `roles` / `source`；依据 `cfg`，位置 `g_0027`。
  理由：脚本读取源文档内容，向当前过程引入文档数据。

> source.read_text

- `roles` / `sink`；依据 `cfg`，位置 `g_0027`。
  理由：脚本创建/写入转换产物文件，使内容到达存储位置。

> output.write_text

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0027`。
  理由：脚本读取源文档内容。

> source.read_text

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0027`。
  理由：脚本写入转换产物文件。

> output.write_text

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：捕获的标准输出作为工具结果默认进入 LLM 上下文，模型观察输出路径。

> 默认进入 LLM 上下文

### ir_008

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：调度动作由 LLM 参与选择下一执行块。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制转交，未向过程引入数据、未使内容到达接收或存储、未处理内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制操作，未记录读取、写入、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_009

- `actor` / `tool`；依据 `cfg`，位置 `g_0033`。
  理由：具体脚本作为工具执行打包。

> scripts/package.py

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0033`。
  理由：本地运行时调用打包脚本。

> run_package_script

- `roles` / `source`；依据 `cfg`，位置 `g_0033`。
  理由：读取指定产物文件内容以写入压缩包。

> archive.write

- `roles` / `sink`；依据 `cfg`，位置 `g_0033`。
  理由：创建/写入 bundle.zip，使内容到达存储位置。

> bundle.zip

- `roles` / `transformer`；依据 `cfg`，位置 `g_0033`。
  理由：将多个产物组合/压缩为 ZIP，改变表示。

> archive.write

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0033`。
  理由：脚本读取每个产物文件内容。

> archive.write

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0033`。
  理由：脚本创建/写入 ZIP 文件。

> bundle.zip

- `effects` / `transform`；依据 `cfg`，位置 `g_0033`。
  理由：打包/压缩/组合多个文件为 ZIP，属于变换。

> archive.write

### ir_010

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：调度动作由 LLM 参与选择下一执行块。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制转交，未向过程引入数据、未使内容到达接收或存储、未处理内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制操作，未记录读取、写入、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_011

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0039`。
  理由：将 bundle.zip 交付到目标路径，属于本地运行时文件操作。

> deliver_bundle_zip

- `roles` / `sink`；依据 `cfg`，位置 `g_0039`。
  理由：使 bundle 内容到达 delivery_path 存储位置。

> request_delivery_path

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0039`。
  理由：在目标位置写入/放置 bundle.zip 文件。

> deliver_bundle_zip

### ir_012

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：调度动作由 LLM 参与选择下一执行块。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：纯控制转交，未向过程引入数据、未使内容到达接收或存储、未处理内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：纯控制操作，未记录读取、写入、网络、模型观察、用户输出或变换效果。

> dispatch

### ir_013

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0045`。
  理由：写入本地 receipt.txt，由代理运行时执行。

> write_receipt_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0045`。
  理由：使转换产物路径列表到达本地文件存储。

> receipt.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0045`。
  理由：创建/写入 receipt.txt 文件内容。

> write_receipt_file

### ir_014

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0046`。
  理由：返回/结束流程由本地代理运行时执行控制转移。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0046`。
  理由：纯控制返回，未向过程引入数据、未使内容到达接收或存储、未处理内容。

> return

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：return 未记录读取、写入、网络、模型观察或用户输出等效果。

> 普通 return 不能单独证明面向用户输出

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
