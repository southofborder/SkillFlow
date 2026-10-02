# 安全语义标注：024

状态：**标注记录完整**（`complete`）

标注记录完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`d312dc2a42929c3683570e48518c6f84203e14e843da08edf1e7cee4a9244609`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

没有记录未决项或执行问题；不等于模型标注已经人工确认。

## 按块查看

### block_001 · Read the user-provided manifest.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_manifest_file | agent_runtime | source | fs_read |
| ir_002 | dispatch | llm | [] | [] |

### block_002 · Read output_dir and delivery_path from the request

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | read_output_dir_and_delivery_path_from_request | agent_runtime | source | context_read |
| ir_004 | dispatch | llm | [] | [] |

### block_003 · Extract document paths from the manifest paths list

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | extract_document_paths_from_manifest | agent_runtime | transformer | transform |
| ir_006 | dispatch | llm | [] | [] |

### block_004 · Convert each document and collect its output path

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | execute_convert_script_for_each_document | tool | source, transformer, sink | fs_read, fs_write, transform, model_observe |
| ir_008 | dispatch | llm | [] | [] |

### block_005 · Package converted artifacts into bundle.zip

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | execute_package_script | tool | source, transformer, sink | fs_read, fs_write, transform |
| ir_010 | dispatch | llm | [] | [] |

### block_006 · Read archive_path from the request

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | read_archive_path_from_request | agent_runtime | source | context_read |
| ir_012 | dispatch | llm | [] | [] |

### block_007 · Deliver bundle.zip to the requested archive_path

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_013 | deliver_bundle_zip | agent_runtime | sink | fs_write |
| ir_014 | dispatch | llm | [] | [] |

### block_008 · Write converted artifact paths to receipt.txt

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_015 | write_converted_paths_to_receipt | agent_runtime | sink | fs_write |
| ir_016 | return | agent_runtime | [] | [] |

## 标注依据

### ir_001

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：该 IR 读取 manifest 文件，由本地代理运行时执行文件读取。

> read_manifest_file

- `roles` / `source`；依据 `cfg`，位置 `g_0009`。
  理由：读取外部 manifest 文件，将 manifest 内容引入当前过程，承担 source 角色。

> read_manifest_file

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0009`。
  理由：读取文件内容，产生 fs_read。

> read_manifest_file

### ir_002

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：执行模型表明 LLM 参与调度，dispatch 为调度动作。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯调度控制，不引入、变换或存储内容，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制操作，无词表匹配效果。

> dispatch

### ir_003

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：该 IR 从请求中读取上下文键，由本地代理运行时执行。

> read_output_dir_and_delivery_path_from_request

- `roles` / `source`；依据 `cfg`，位置 `g_0015`。
  理由：从请求读取 output_dir 和 delivery_path，将调用者输入引入当前过程，承担 source 角色。

> read_output_dir_and_delivery_path_from_request

- `effects` / `context_read`；依据 `cfg`，位置 `g_0015`。
  理由：从请求/运行时上下文读取 output_dir 和 delivery_path，产生 context_read。

> read_output_dir_and_delivery_path_from_request

### ir_004

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：执行模型表明 LLM 参与调度，dispatch 为调度动作。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯调度控制，不引入、变换或存储内容，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制操作，无词表匹配效果。

> dispatch

### ir_005

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0021`。
  理由：该 IR 从 manifest 内容中提取路径，由本地代理运行时执行本地处理。

> extract_document_paths_from_manifest

- `roles` / `transformer`；依据 `cfg`，位置 `g_0021`。
  理由：对 manifest 内容进行选择/提取，输出 document_paths，承担 transformer 角色。

> extract_document_paths_from_manifest

- `effects` / `transform`；依据 `cfg`，位置 `g_0021`。
  理由：从 manifest 内容中提取路径列表，属于选择/变换。

> extract_document_paths_from_manifest

### ir_006

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：执行模型表明 LLM 参与调度，dispatch 为调度动作。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯调度控制，不引入、变换或存储内容，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制操作，无词表匹配效果。

> dispatch

### ir_007

- `actor` / `tool`；依据 `cfg`，位置 `g_0027`。
  理由：该 IR 执行转换脚本，脚本作为工具执行动作。

> execute_convert_script_for_each_document

- `roles` / `source`；依据 `cfg`，位置 `g_0027`。
  理由：脚本读取输入文档，将文档内容引入处理过程，承担 source 角色。

> execute_convert_script_for_each_document

- `roles` / `transformer`；依据 `source`，位置 `src_007`。
  理由：脚本读取源文档并写入新的 .txt 文件，改变表示/格式，承担 transformer 角色。

> output = output_dir / (source.stem + ".txt")

- `roles` / `sink`；依据 `source`，位置 `src_007`。
  理由：脚本写入转换产物文件，使内容到达存储位置，承担 sink 角色。

> output.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

- `effects` / `fs_read`；依据 `source`，位置 `src_007`。
  理由：脚本读取源文档内容，产生 fs_read。

> source.read_text(encoding="utf-8")

- `effects` / `fs_write`；依据 `source`，位置 `src_007`。
  理由：脚本写入输出文件，产生 fs_write。

> output.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

- `effects` / `transform`；依据 `source`，位置 `src_007`。
  理由：脚本将源文档转换为 .txt 输出路径并写入，改变表示，产生 transform。

> output = output_dir / (source.stem + ".txt")

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：脚本执行结果 converted_artifact_paths 默认回传 LLM 上下文，产生 model_observe。

> 工具执行返回的内容默认进入 LLM 上下文

### ir_008

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：执行模型表明 LLM 参与调度，dispatch 为调度动作。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯调度控制，不引入、变换或存储内容，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制操作，无词表匹配效果。

> dispatch

### ir_009

- `actor` / `tool`；依据 `cfg`，位置 `g_0033`。
  理由：该 IR 执行打包脚本，脚本作为工具执行动作。

> execute_package_script

- `roles` / `source`；依据 `source`，位置 `src_009`。
  理由：脚本读取传入的转换产物路径，将文件内容引入打包过程，承担 source 角色。

> for filename in args.paths:

- `roles` / `transformer`；依据 `source`，位置 `src_009`。
  理由：脚本将多个文件组合进 ZIP，改变表示，承担 transformer 角色。

> archive.write(path, arcname=path.name)

- `roles` / `sink`；依据 `source`，位置 `src_009`。
  理由：脚本创建并写入 bundle.zip，使内容到达存储位置，承担 sink 角色。

> with ZipFile(args.output, "w") as archive:

- `effects` / `fs_read`；依据 `source`，位置 `src_009`。
  理由：脚本读取 path 对应文件以写入 ZIP，产生 fs_read。

> archive.write(path, arcname=path.name)

- `effects` / `fs_write`；依据 `source`，位置 `src_009`。
  理由：脚本写入 bundle.zip，产生 fs_write。

> with ZipFile(args.output, "w") as archive:

- `effects` / `transform`；依据 `source`，位置 `src_009`。
  理由：将多个文件打包成 ZIP，组合并改变表示，产生 transform。

> archive.write(path, arcname=path.name)

### ir_010

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：执行模型表明 LLM 参与调度，dispatch 为调度动作。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯调度控制，不引入、变换或存储内容，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制操作，无词表匹配效果。

> dispatch

### ir_011

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0039`。
  理由：该 IR 从请求中读取 archive_path，由本地代理运行时执行。

> read_archive_path_from_request

- `roles` / `source`；依据 `cfg`，位置 `g_0039`。
  理由：从请求读取 archive_path，将调用者输入引入当前过程，承担 source 角色。

> read_archive_path_from_request

- `effects` / `context_read`；依据 `cfg`，位置 `g_0039`。
  理由：从请求/运行时上下文读取 archive_path，产生 context_read。

> read_archive_path_from_request

### ir_012

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：执行模型表明 LLM 参与调度，dispatch 为调度动作。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：纯调度控制，不引入、变换或存储内容，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：纯控制操作，无词表匹配效果。

> dispatch

### ir_013

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0045`。
  理由：该 IR 将 bundle.zip 交付到本地 archive_path，由本地代理运行时执行文件交付。

> deliver_bundle_zip

- `roles` / `sink`；依据 `cfg`，位置 `g_0045`。
  理由：将 bundle.zip 交付到 archive_path，使内容到达存储位置，承担 sink 角色。

> deliver_bundle_zip

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0045`。
  理由：交付到 archive_path 涉及写入目标位置，产生 fs_write。

> deliver_bundle_zip

### ir_014

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：执行模型表明 LLM 参与调度，dispatch 为调度动作。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0046`。
  理由：纯调度控制，不引入、变换或存储内容，无 source/sink/transformer 角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0046`。
  理由：纯控制操作，无词表匹配效果。

> dispatch

### ir_015

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0051`。
  理由：该 IR 将路径列表写入本地 receipt.txt，由本地代理运行时执行文件写入。

> write_converted_paths_to_receipt

- `roles` / `sink`；依据 `cfg`，位置 `g_0051`。
  理由：将转换产物路径列表写入 receipt.txt，使内容到达存储位置，承担 sink 角色。

> write_converted_paths_to_receipt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0051`。
  理由：写入本地 receipt.txt，产生 fs_write。

> write_converted_paths_to_receipt

### ir_016

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0052`。
  理由：return 为控制流动作，由本地代理运行时执行控制转移。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0052`。
  理由：纯控制返回，不引入、变换或存储内容，无 source/sink/transformer 角色。

> return

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：return 为控制流，不能据此推断 user_output 或其他效果。

> 普通 return 不能单独证明面向用户输出

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
