# 安全语义标注：annotation

状态：**标注记录完整**（`complete`）

标注记录完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`336a0da9c49b0d3dd63a151f4d71959759b1fd4f6ee580772a271ca55545a93e`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

没有记录未决项或执行问题；不等于模型标注已经人工确认。

## 按块查看

### block_001 · Read the user-provided manifest.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_manifest_json | agent_runtime | source | fs_read |
| ir_002 | dispatch | llm | [] | [] |

### block_002 · Extract document paths from the manifest paths list

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | extract_document_paths_from_manifest_paths | agent_runtime | transformer | transform |
| ir_004 | dispatch | llm | [] | [] |

### block_003 · Read output_dir and delivery_path from the request

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | read_output_dir_and_delivery_path_from_request | agent_runtime | source | context_read |
| ir_006 | dispatch | llm | [] | [] |

### block_004 · Convert each document via scripts/convert.py and read stdout

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | run_convert_script_per_document_and_read_stdout | agent_runtime, tool | source, sink | fs_read, fs_write, model_observe |
| ir_008 | dispatch | llm | [] | [] |

### block_005 · Package converted paths into bundle.zip

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | run_package_script | agent_runtime, tool | source, transformer, sink | fs_read, fs_write, transform |
| ir_010 | dispatch | llm | [] | [] |

### block_006 · Read archive_path from the request

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | read_archive_path_from_request | agent_runtime | source | context_read |
| ir_012 | dispatch | llm | [] | [] |

### block_007 · Deliver bundle.zip to archive_path

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_013 | deliver_bundle_zip_to_archive_path | agent_runtime | sink | fs_write |
| ir_014 | dispatch | llm | [] | [] |

### block_008 · Write converted paths to local receipt.txt

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_015 | write_converted_paths_to_receipt | agent_runtime | sink | fs_write |
| ir_016 | return | agent_runtime | [] | [] |

## 标注依据

### ir_001

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：该 IR 读取外部 manifest.json；IR 未记录具体工具，按本地代理运行时执行文件读取标注。

> read_manifest_json

- `roles` / `source`；依据 `cfg`，位置 `g_0009`。
  理由：读取外部资源并将 manifest 数据引入后续流程，充当 source。

> manifest.json

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0009`。
  理由：动作读取 manifest.json 文件内容，符合 fs_read。

> read_manifest_json

### ir_002

- `actor` / `llm`；依据 `cfg`，位置 `g_0010`。
  理由：dispatch 是调度/发起下一块的控制动作，LLM 可参与调度；按 EM03 调度本身不证明内容可见。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制流调度，不向当前过程引入、转换或写出内容，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：无词表所列数据处理效果，纯控制操作。

> dispatch

### ir_003

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：从已读取的 manifest 结果中按字段提取路径；IR 未记录模型或工具参与，归本地运行时处理。

> extract_document_paths_from_manifest_paths

- `roles` / `transformer`；依据 `cfg`，位置 `g_0015`。
  理由：按 paths 字段选择/提取文档路径，改变数据表示，属 transformer。

> paths

- `effects` / `transform`；依据 `cfg`，位置 `g_0015`。
  理由：从 manifest_data 中提取 paths 列表，属计算/选择。

> extract_document_paths_from_manifest_paths

### ir_004

- `actor` / `llm`；依据 `cfg`，位置 `g_0016`。
  理由：dispatch 是调度/发起下一块的控制动作，LLM 可参与调度；按 EM03 调度本身不证明内容可见。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制流调度，不向当前过程引入、转换或写出内容，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：无词表所列数据处理效果，纯控制操作。

> dispatch

### ir_005

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0021`。
  理由：读取请求上下文中的控制参数；IR 未记录模型或工具参与，归本地运行时处理。

> read_output_dir_and_delivery_path_from_request

- `roles` / `source`；依据 `cfg`，位置 `g_0021`。
  理由：从调用者请求中引入 output_dir 等上下文值，充当 source。

> output_dir

- `effects` / `context_read`；依据 `cfg`，位置 `g_0021`。
  理由：取得调用者输入/运行时上下文，符合 context_read。

> read_output_dir_and_delivery_path_from_request

### ir_006

- `actor` / `llm`；依据 `cfg`，位置 `g_0022`。
  理由：dispatch 是调度/发起下一块的控制动作，LLM 可参与调度；按 EM03 调度本身不证明内容可见。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制流调度，不向当前过程引入、转换或写出内容，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：无词表所列数据处理效果，纯控制操作。

> dispatch

### ir_007

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0027`。
  理由：本地运行时启动脚本并读取标准输出，参与该动作。

> run_convert_script_per_document_and_read_stdout

- `actor` / `tool`；依据 `cfg`，位置 `g_0027`。
  理由：具体转换由 scripts/convert.py 工具执行。

> scripts/convert.py

- `roles` / `source`；依据 `cfg`，位置 `g_0027`。
  理由：脚本读取源文档内容并引入转换流程，充当 source。

> source.read_text(encoding="utf-8")

- `roles` / `sink`；依据 `cfg`，位置 `g_0027`。
  理由：脚本写出转换产物并回传 stdout 路径，使内容到达存储/模型边界，充当 sink。

> output.write_text

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0027`。
  理由：脚本读取输入文档内容，符合 fs_read。

> source.read_text(encoding="utf-8")

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0027`。
  理由：脚本创建/写入输出文件，符合 fs_write。

> output.write_text

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：scripts/convert.py 的标准输出作为转换产物路径回传，按 EM02 默认进入 LLM 上下文。

> 工具执行返回的内容默认进入 LLM 上下文

### ir_008

- `actor` / `llm`；依据 `cfg`，位置 `g_0028`。
  理由：dispatch 是调度/发起下一块的控制动作，LLM 可参与调度；按 EM03 调度本身不证明内容可见。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制流调度，不向当前过程引入、转换或写出内容，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：无词表所列数据处理效果，纯控制操作。

> dispatch

### ir_009

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0033`。
  理由：本地运行时调用打包脚本，参与该动作。

> run_package_script

- `actor` / `tool`；依据 `cfg`，位置 `g_0033`。
  理由：打包由 scripts/package.py 工具执行。

> scripts/package.py

- `roles` / `source`；依据 `cfg`，位置 `g_0033`。
  理由：打包时读取传入路径对应文件内容，向打包过程引入数据，充当 source。

> archive.write(path, arcname=path.name)

- `roles` / `transformer`；依据 `cfg`，位置 `g_0033`。
  理由：将多个文件组合进 ZIP，属组合/改变容器表示，充当 transformer。

> archive.write(path, arcname=path.name)

- `roles` / `sink`；依据 `cfg`，位置 `g_0033`。
  理由：将内容写入 bundle.zip 存储位置，充当 sink。

> bundle.zip

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0033`。
  理由：ZipFile.write 读取输入文件内容，符合 fs_read。

> archive.write(path, arcname=path.name)

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0033`。
  理由：创建并写入 ZIP 输出文件，符合 fs_write。

> ZipFile(args.output, "w")

- `effects` / `transform`；依据 `cfg`，位置 `g_0033`。
  理由：将多文件组合为 ZIP 包，属组合/改变表示。

> archive.write(path, arcname=path.name)

### ir_010

- `actor` / `llm`；依据 `cfg`，位置 `g_0034`。
  理由：dispatch 是调度/发起下一块的控制动作，LLM 可参与调度；按 EM03 调度本身不证明内容可见。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制流调度，不向当前过程引入、转换或写出内容，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：无词表所列数据处理效果，纯控制操作。

> dispatch

### ir_011

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0039`。
  理由：读取请求上下文中的 archive_path；IR 未记录模型或工具参与，归本地运行时处理。

> read_archive_path_from_request

- `roles` / `source`；依据 `cfg`，位置 `g_0039`。
  理由：从调用者请求中引入 archive_path 值，充当 source。

> archive_path

- `effects` / `context_read`；依据 `cfg`，位置 `g_0039`。
  理由：取得调用者输入/运行时上下文，符合 context_read。

> read_archive_path_from_request

### ir_012

- `actor` / `llm`；依据 `cfg`，位置 `g_0040`。
  理由：dispatch 是调度/发起下一块的控制动作，LLM 可参与调度；按 EM03 调度本身不证明内容可见。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：纯控制流调度，不向当前过程引入、转换或写出内容，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：无词表所列数据处理效果，纯控制操作。

> dispatch

### ir_013

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0045`。
  理由：将 bundle.zip 交付到 archive_path 的本地动作；IR 未记录工具参与，归本地运行时执行。

> deliver_bundle_zip_to_archive_path

- `roles` / `sink`；依据 `cfg`，位置 `g_0045`。
  理由：使 bundle.zip 到达请求指定交付/存储位置，充当 sink。

> archive_path_value

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0045`。
  理由：将已有 bundle.zip 交付/写入 archive_path，创建或修改目标位置文件内容，符合 fs_write；IR 未记录远端通信依据，不标注 net_send。

> deliver_bundle_zip_to_archive_path

### ir_014

- `actor` / `llm`；依据 `cfg`，位置 `g_0046`。
  理由：dispatch 是调度/发起下一块的控制动作，LLM 可参与调度；按 EM03 调度本身不证明内容可见。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0046`。
  理由：纯控制流调度，不向当前过程引入、转换或写出内容，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0046`。
  理由：无词表所列数据处理效果，纯控制操作。

> dispatch

### ir_015

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0051`。
  理由：写入本地 receipt.txt；IR 未记录工具参与，归本地运行时执行。

> write_converted_paths_to_receipt

- `roles` / `sink`；依据 `cfg`，位置 `g_0051`。
  理由：将转换产物路径列表写入本地存储位置，充当 sink。

> receipt.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0051`。
  理由：创建/修改 receipt.txt 文件内容，符合 fs_write。

> write_converted_paths_to_receipt

### ir_016

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0052`。
  理由：return 是运行时控制流结束动作；无工具/模型参与证据。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0052`。
  理由：控制流返回，不引入、转换或写出内容，无 source/sink/transformer 角色。

> return

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0052`。
  理由：纯控制返回；按 EM06，普通 return 不证明面向用户输出，也无其他词表效果。

> return

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
