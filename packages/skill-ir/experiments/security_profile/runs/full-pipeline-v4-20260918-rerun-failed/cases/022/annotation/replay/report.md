# 安全语义标注：annotation

状态：**存在未决标注**（`incomplete`）

保留有依据的标注，存在未决项。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`9b773ace215334006228669ceaca7490a43fa156c5935de313555fa3bc05bdef`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- `ir_011` / `effects`：无法确定交付动作是否通过复制读取 bundle.zip 内容而包含 fs_read，还是仅写入或移动目标路径；未据此添加 fs_read。

## 按块查看

### block_001 · Read the user-provided manifest.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_manifest_file | agent_runtime | source | fs_read |
| ir_002 | dispatch | llm | [] | [] |

### block_002 · Extract document paths from the manifest paths list

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | extract_document_paths_from_manifest | llm | transformer | model_observe, transform |
| ir_004 | dispatch | llm | [] | [] |

### block_003 · Read output_dir and delivery_path from the request

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | read_output_dir_and_delivery_path_from_request | llm | source | context_read, model_observe |
| ir_006 | dispatch | llm | [] | [] |

### block_004 · Convert each document with scripts/convert.py and collect output paths

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | run_convert_script_for_each_document | agent_runtime, tool | source, transformer, sink | fs_read, fs_write, transform, model_observe |
| ir_008 | dispatch | llm | [] | [] |

### block_005 · Package converted artifacts into bundle.zip with scripts/package.py

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | run_package_script | agent_runtime, tool | source, transformer, sink | fs_read, fs_write, transform |
| ir_010 | dispatch | llm | [] | [] |

### block_006 · Deliver generated bundle.zip to requested delivery_path

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | deliver_bundle_to_requested_path | agent_runtime | sink | fs_write |
| ir_012 | dispatch | llm | [] | [] |

### block_007 · Write converted artifact paths to local receipt.txt and finish

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_013 | write_converted_paths_to_receipt | agent_runtime | sink | fs_write |
| ir_014 | return | agent_runtime | [] | [] |

## 标注依据

### ir_001

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：该 IR 为文件读取动作，由本地代理运行时执行。

> read_manifest_file

- `roles` / `source`；依据 `source`，位置 `src_005`。
  理由：该动作把外部清单内容引入当前流程。

> 读取用户提供的 manifest.json

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0009`。
  理由：opcode 表明读取 manifest 文件内容。

> read_manifest_file

### ir_002

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 表示由 LLM 选择或发起后续动作。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯调度不引入、变换或送达内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生读取、写入、观察等效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_003

- `actor` / `llm`；依据 `cfg`，位置 `g_0015`。
  理由：该提取未绑定脚本，由模型处理清单内容并选择路径。

> extract_document_paths_from_manifest

- `roles` / `transformer`；依据 `cfg`，位置 `g_0015`。
  理由：按 paths 选择或提取路径属于对内容的变换。

> paths

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型读取 manifest_content 并提取路径。

> 模型实际读取内容并处理时还标注 model_observe

- `effects` / `transform`；依据 `cfg`，位置 `g_0015`。
  理由：提取或选择路径是计算与选择表示的变换。

> extract_document_paths_from_manifest

### ir_004

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 表示由 LLM 选择或发起后续动作。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯调度不引入、变换或送达内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生读取、写入、观察等效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_005

- `actor` / `llm`；依据 `cfg`，位置 `g_0021`。
  理由：该请求上下文读取由执行流程的模型完成。

> read_output_dir_and_delivery_path_from_request

- `roles` / `source`；依据 `cfg`，位置 `g_0021`。
  理由：读取请求上下文将 output_dir 和 delivery_path 引入流程。

> output_dir

- `effects` / `context_read`；依据 `cfg`，位置 `g_0021`。
  理由：输入类型为 context_key，表示取得调用者或运行时上下文。

> context_key

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型读取请求上下文中的路径值。

> 模型实际读取内容并处理时还标注 model_observe

### ir_006

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 表示由 LLM 选择或发起后续动作。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯调度不引入、变换或送达内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生读取、写入、观察等效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_007

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0027`。
  理由：本地代理运行时发起该转换命令。

> python scripts/convert.py

- `actor` / `tool`；依据 `cfg`，位置 `g_0027`。
  理由：metadata.script_path 指明执行的脚本工具。

> scripts/convert.py

- `roles` / `source`；依据 `source`，位置 `src_016`。
  理由：脚本读取输入文档内容，将其引入处理。

> source.read_text

- `roles` / `transformer`；依据 `cfg`，位置 `g_0027`。
  理由：转换脚本将输入文档处理为转换产物。

> run_convert_script_for_each_document

- `roles` / `sink`；依据 `source`，位置 `src_016`。
  理由：写入转换产物文件，使内容到达存储位置。

> output.write_text

- `effects` / `fs_read`；依据 `source`，位置 `src_016`。
  理由：读取源文档内容。

> source.read_text

- `effects` / `fs_write`；依据 `source`，位置 `src_016`。
  理由：创建或写入转换产物文件内容。

> output.write_text

- `effects` / `transform`；依据 `cfg`，位置 `g_0027`。
  理由：转换或另存处理改变内容表示。

> run_convert_script_for_each_document

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：脚本标准输出路径作为工具结果回传模型。

> 默认进入 LLM 上下文

### ir_008

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 表示由 LLM 选择或发起后续动作。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯调度不引入、变换或送达内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生读取、写入、观察等效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_009

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0033`。
  理由：本地代理运行时发起该打包命令。

> python scripts/package.py

- `actor` / `tool`；依据 `cfg`，位置 `g_0033`。
  理由：metadata.script_path 指明执行的打包脚本工具。

> scripts/package.py

- `roles` / `source`；依据 `source`，位置 `src_018`。
  理由：打包脚本读取转换产物文件内容加入归档。

> archive.write(path

- `roles` / `transformer`；依据 `cfg`，位置 `g_0033`。
  理由：打包或压缩改变内容表示。

> run_package_script

- `roles` / `sink`；依据 `source`，位置 `src_018`。
  理由：写入 bundle.zip 存储位置。

> ZipFile(args.output

- `effects` / `fs_read`；依据 `source`，位置 `src_018`。
  理由：读取待打包文件内容。

> archive.write(path

- `effects` / `fs_write`；依据 `source`，位置 `src_018`。
  理由：创建或写入 zip 文件内容。

> ZipFile(args.output

- `effects` / `transform`；依据 `cfg`，位置 `g_0033`。
  理由：打包或压缩属于变换。

> run_package_script

### ir_010

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 表示由 LLM 选择或发起后续动作。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯调度不引入、变换或送达内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生读取、写入、观察等效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_011

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0039`。
  理由：本地交付或写入目标路径由代理运行时执行。

> deliver_bundle_to_requested_path

- `roles` / `sink`；依据 `source`，位置 `src_011`。
  理由：使 bundle 到达目标存储位置。

> 交付到请求的 delivery_path

- `effects` / `fs_write`；依据 `source`，位置 `src_011`。
  理由：在 delivery_path 创建或放置文件内容。

> 交付到请求的 delivery_path

### ir_012

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 表示由 LLM 选择或发起后续动作。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：纯调度不引入、变换或送达内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生读取、写入、观察等效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_013

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0045`。
  理由：本地写文件动作由代理运行时执行。

> write_converted_paths_to_receipt

- `roles` / `sink`；依据 `source`，位置 `src_012`。
  理由：写入本地文件使内容到达存储位置。

> 写入本地 receipt.txt

- `effects` / `fs_write`；依据 `source`，位置 `src_012`。
  理由：创建或写入 receipt.txt 文件内容。

> 写入本地 receipt.txt

### ir_014

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0046`。
  理由：控制流返回由本地代理运行时执行。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0046`。
  理由：返回为纯控制，不引入、变换或送达内容。

> return

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：无其他效果依据，且 return 不证明用户输出。

> 普通 return 不能单独证明面向用户输出

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
