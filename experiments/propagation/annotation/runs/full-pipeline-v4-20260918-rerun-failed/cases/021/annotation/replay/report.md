# 安全语义标注：annotation

状态：**标注记录完整**（`complete`）

标注记录完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`70a314c9753929e7642b1622b13ef8e52a6b2267b54a0489d7513f1c52025925`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

没有记录未决项或执行问题；不等于模型标注已经人工确认。

## 按块查看

### block_001 · Read user-provided manifest.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_manifest_file | agent_runtime | source | fs_read |
| ir_002 | dispatch | agent_runtime | [] | [] |

### block_002 · Extract document paths from manifest paths list

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | extract_document_paths_from_manifest | agent_runtime | transformer | transform |
| ir_004 | dispatch | agent_runtime | [] | [] |

### block_003 · Read output_dir and delivery_path from the request

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | read_output_dir_and_delivery_path_from_request | agent_runtime | source | context_read |
| ir_006 | dispatch | agent_runtime | [] | [] |

### block_004 · Convert each document with scripts/convert.py and collect stdout paths

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | convert_documents_individually_with_convert_script | tool, llm | source, transformer, sink | fs_read, fs_write, transform, model_observe |
| ir_008 | dispatch | agent_runtime | [] | [] |

### block_005 · Package converted artifacts with scripts/package.py

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | package_converted_artifacts_with_package_script | tool | source, transformer, sink | fs_read, fs_write, transform |
| ir_010 | dispatch | agent_runtime | [] | [] |

### block_006 · Deliver bundle.zip to requested delivery_path

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | deliver_bundle_to_delivery_path | agent_runtime | sink | fs_write |
| ir_012 | dispatch | agent_runtime | [] | [] |

### block_007 · Write receipt.txt and finish

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_013 | write_receipt_file | agent_runtime | sink | fs_write |
| ir_014 | return | agent_runtime | [] | [] |

## 标注依据

### ir_001

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：该IR执行读取manifest.json的本地文件操作，由代理运行时执行。

> read_manifest_file

- `roles` / `source`；依据 `cfg`，位置 `g_0009`。
  理由：读取外部文件内容并向流程引入数据，扮演source。

> manifest.json

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0009`。
  理由：opcode表明读取manifest文件内容。

> read_manifest_file

### ir_002

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0010`。
  理由：dispatch为控制转移指令，由代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制转移，不引入、变换或送达内容，无适用角色标签。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制操作，词表无匹配效果标签。

> dispatch

### ir_003

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：该IR在本地从清单内容中提取路径，由代理运行时执行。

> extract_document_paths_from_manifest

- `roles` / `transformer`；依据 `cfg`，位置 `g_0015`。
  理由：对输入清单内容进行提取/选择，处理内容。

> extract_document_paths_from_manifest

- `effects` / `transform`；依据 `cfg`，位置 `g_0015`。
  理由：提取路径列表属于计算/选择/改变表示。

> extract_document_paths_from_manifest

### ir_004

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：dispatch为控制转移指令，由代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制转移，不引入、变换或送达内容，无适用角色标签。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制操作，词表无匹配效果标签。

> dispatch

### ir_005

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0021`。
  理由：从请求上下文读取路径，由代理运行时执行。

> read_output_dir_and_delivery_path_from_request

- `roles` / `source`；依据 `cfg`，位置 `g_0021`。
  理由：从调用者输入/运行时上下文引入数据，扮演source。

> context_key

- `effects` / `context_read`；依据 `cfg`，位置 `g_0021`。
  理由：取得运行时上下文/调用者输入中的output_dir与delivery_path。

> read_output_dir_and_delivery_path_from_request

### ir_006

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0022`。
  理由：dispatch为控制转移指令，由代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制转移，不引入、变换或送达内容，无适用角色标签。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制操作，词表无匹配效果标签。

> dispatch

### ir_007

- `actor` / `tool`；依据 `cfg`，位置 `g_0027`。
  理由：转换动作由scripts/convert.py工具执行。

> scripts/convert.py

- `actor` / `llm`；依据 `execution_model`，位置 `EM02`。
  理由：转换脚本stdout作为工具结果默认进入模型上下文，模型参与接收。

> 返回的内容默认进入 LLM 上下文

- `roles` / `source`；依据 `cfg`，位置 `g_0027`。
  理由：脚本读取源文档内容，向转换过程引入数据。

> source.read_text

- `roles` / `transformer`；依据 `cfg`，位置 `g_0027`。
  理由：转换文档并生成转换产物，处理/改变表示。

> convert_documents_individually_with_convert_script

- `roles` / `sink`；依据 `cfg`，位置 `g_0027`。
  理由：写出转换产物到输出目录，使内容到达存储位置。

> output.write_text

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0027`。
  理由：脚本读取源文档内容。

> source.read_text

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0027`。
  理由：脚本创建/写入转换产物文件。

> output.write_text

- `effects` / `transform`；依据 `cfg`，位置 `g_0027`。
  理由：执行文档转换，改变表示/生成产物。

> convert_documents_individually_with_convert_script

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：脚本stdout作为工具结果默认进入模型上下文。

> 返回的内容默认进入 LLM 上下文

### ir_008

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0028`。
  理由：dispatch为控制转移指令，由代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制转移，不引入、变换或送达内容，无适用角色标签。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制操作，词表无匹配效果标签。

> dispatch

### ir_009

- `actor` / `tool`；依据 `cfg`，位置 `g_0033`。
  理由：打包动作由scripts/package.py工具执行。

> scripts/package.py

- `roles` / `source`；依据 `cfg`，位置 `g_0033`。
  理由：读取传入文件内容并写入归档，引入数据。

> archive.write

- `roles` / `transformer`；依据 `cfg`，位置 `g_0033`。
  理由：将多个转换产物组合为ZIP包，处理/组合内容。

> package_converted_artifacts_with_package_script

- `roles` / `sink`；依据 `cfg`，位置 `g_0033`。
  理由：创建指定的ZIP输出文件，使内容到达存储位置。

> args.output

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0033`。
  理由：archive.write读取输入文件内容以加入归档。

> archive.write

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0033`。
  理由：将归档写入--output指定的文件。

> args.output

- `effects` / `transform`；依据 `cfg`，位置 `g_0033`。
  理由：打包组合多个文件为ZIP，属于组合/改变表示。

> package_converted_artifacts_with_package_script

### ir_010

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0034`。
  理由：dispatch为控制转移指令，由代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制转移，不引入、变换或送达内容，无适用角色标签。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制操作，词表无匹配效果标签。

> dispatch

### ir_011

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0039`。
  理由：交付动作由代理运行时执行。

> deliver_bundle_to_delivery_path

- `roles` / `sink`；依据 `cfg`，位置 `g_0039`。
  理由：将bundle交付到目标路径，使内容到达存储/接收边界。

> requested_delivery_path

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0039`。
  理由：将bundle写入/放置到delivery_path，涉及目标位置文件内容写入。

> deliver_bundle_to_delivery_path

### ir_012

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0040`。
  理由：dispatch为控制转移指令，由代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：纯控制转移，不引入、变换或送达内容，无适用角色标签。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：纯控制操作，词表无匹配效果标签。

> dispatch

### ir_013

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0045`。
  理由：写receipt文件由代理运行时执行。

> write_receipt_file

- `roles` / `sink`；依据 `cfg`，位置 `g_0045`。
  理由：将内容写入本地receipt.txt，使内容到达存储位置。

> receipt.txt

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0045`。
  理由：opcode表明创建/写入receipt.txt文件。

> write_receipt_file

### ir_014

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0046`。
  理由：return为控制结束指令，由代理运行时执行。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0046`。
  理由：纯控制结束，不引入、变换或送达内容，无适用角色标签。

> return

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0046`。
  理由：普通return不必然面向用户输出，词表无匹配效果标签。

> return

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
