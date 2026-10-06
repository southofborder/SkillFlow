# 安全语义标注：023

状态：**标注记录完整**（`complete`）

标注记录完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`34d9ecead15a748c687a9c6fcae7b948d2f2114aee02cc49e2a2c090748168dc`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

没有记录未决项或执行问题；不等于模型标注已经人工确认。

## 按块查看

### block_001 · Read the user-provided manifest.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_manifest_json | agent_runtime | source | fs_read |
| ir_002 | dispatch | llm | [] | [] |

### block_002 · Extract document paths from the manifest

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | extract_paths_from_manifest | llm | transformer | transform, model_observe |
| ir_004 | dispatch | llm | [] | [] |

### block_003 · Read output_dir and delivery_path from the request

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | read_output_dir_and_delivery_path_from_request | agent_runtime | source | context_read |
| ir_006 | dispatch | llm | [] | [] |

### block_004 · Convert each document with scripts/convert.py and collect stdout paths

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | run_convert_script_for_each_document | tool | source, transformer, sink | fs_read, fs_write, transform, model_observe |
| ir_008 | dispatch | llm | [] | [] |

### block_005 · Package converted artifacts with scripts/package.py

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | run_package_script | tool | source, transformer, sink | fs_read, fs_write, transform |
| ir_010 | dispatch | llm | [] | [] |

### block_006 · Deliver bundle.zip to the requested delivery_path

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | deliver_bundle_zip_to_path | agent_runtime | sink | fs_write |
| ir_012 | return | agent_runtime | [] | [] |

## 标注依据

### ir_001

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：读取外部 manifest 文件属于本地代理运行时的文件访问动作。

> read_manifest_json

- `roles` / `source`；依据 `cfg`，位置 `g_0009`。
  理由：输出 manifest 内容，向当前流程引入数据。

> manifest contents

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0009`。
  理由：动作读取 manifest.json 文件内容。

> read_manifest_json

### ir_002

- `actor` / `llm`；依据 `cfg`，位置 `g_0010`。
  理由：dispatch 为控制流调度，由 LLM 参与决定下一动作。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制转移，不引入、变换或沉淀内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制操作，无读取、写入、网络或模型观察效果。

> dispatch

### ir_003

- `actor` / `llm`；依据 `cfg`，位置 `g_0015`。
  理由：从 manifest 数据中提取路径属于 LLM 推理处理。

> extract_paths_from_manifest

- `roles` / `transformer`；依据 `cfg`，位置 `g_0015`。
  理由：选择/提取文档路径，处理输入数据。

> extract_paths_from_manifest

- `effects` / `transform`；依据 `cfg`，位置 `g_0015`。
  理由：从 manifest 中选择并组合出文档路径。

> extract_paths_from_manifest

- `effects` / `model_observe`；依据 `cfg`，位置 `g_0015`。
  理由：输入 manifest_data 进入模型处理上下文以提取路径。

> manifest_data

### ir_004

- `actor` / `llm`；依据 `cfg`，位置 `g_0016`。
  理由：dispatch 为控制流调度，由 LLM 参与决定下一动作。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制转移，不引入、变换或沉淀内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制操作，无读取、写入、网络或模型观察效果。

> dispatch

### ir_005

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0021`。
  理由：读取请求上下文键由本地代理运行时执行。

> read_output_dir_and_delivery_path_from_request

- `roles` / `source`；依据 `cfg`，位置 `g_0021`。
  理由：取得请求设置并引入当前流程。

> requested output_dir

- `effects` / `context_read`；依据 `cfg`，位置 `g_0021`。
  理由：输入类型为 context_key，取得运行时/调用者上下文。

> context_key

### ir_006

- `actor` / `llm`；依据 `cfg`，位置 `g_0022`。
  理由：dispatch 为控制流调度，由 LLM 参与决定下一动作。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制转移，不引入、变换或沉淀内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制操作，无读取、写入、网络或模型观察效果。

> dispatch

### ir_007

- `actor` / `tool`；依据 `cfg`，位置 `g_0027`。
  理由：动作执行指定转换脚本，脚本作为工具执行。

> scripts/convert.py

- `roles` / `source`；依据 `source`，位置 `src_007`。
  理由：脚本读取源文档内容进入本地转换过程。

> source.read_text(encoding="utf-8")

- `roles` / `transformer`；依据 `cfg`，位置 `g_0027`。
  理由：脚本生成转换后的文档产物。

> writes the converted document to output_dir/<source_stem>.txt

- `roles` / `sink`；依据 `cfg`，位置 `g_0027`。
  理由：将转换产物写入 output_dir 存储位置。

> writes the converted document to output_dir/<source_stem>.txt

- `effects` / `fs_read`；依据 `source`，位置 `src_007`。
  理由：读取源文档文件内容。

> source.read_text(encoding="utf-8")

- `effects` / `fs_write`；依据 `source`，位置 `src_007`。
  理由：写入转换后的输出文件。

> output.write_text

- `effects` / `transform`；依据 `cfg`，位置 `g_0027`。
  理由：生成转换文档，属于表示/产物变换。

> writes the converted document to output_dir/<source_stem>.txt

- `effects` / `model_observe`；依据 `cfg`，位置 `g_0027`。
  理由：脚本将输出路径打印到 stdout，成为工具结果。

> prints the converted output path to stdout

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具结果默认回传 LLM 上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_008

- `actor` / `llm`；依据 `cfg`，位置 `g_0028`。
  理由：dispatch 为控制流调度，由 LLM 参与决定下一动作。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制转移，不引入、变换或沉淀内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制操作，无读取、写入、网络或模型观察效果。

> dispatch

### ir_009

- `actor` / `tool`；依据 `cfg`，位置 `g_0033`。
  理由：动作执行指定打包脚本，脚本作为工具执行。

> scripts/package.py

- `roles` / `source`；依据 `source`，位置 `src_009`。
  理由：打包时读取转换产物文件内容进入归档过程。

> archive.write(path, arcname=path.name)

- `roles` / `transformer`；依据 `cfg`，位置 `g_0033`。
  理由：将多个产物组合为 ZIP 归档。

> run_package_script

- `roles` / `sink`；依据 `cfg`，位置 `g_0033`。
  理由：将归档写入 bundle.zip 存储位置。

> writes the ZIP archive to bundle.zip

- `effects` / `fs_read`；依据 `source`，位置 `src_009`。
  理由：归档写入每个路径时读取对应文件内容。

> archive.write(path, arcname=path.name)

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0033`。
  理由：写入 ZIP 文件到 bundle.zip。

> writes the ZIP archive to bundle.zip

- `effects` / `transform`；依据 `source`，位置 `src_008`。
  理由：脚本构建 ZIP 归档，组合多个产物。

> Build the explicitly requested ZIP

### ir_010

- `actor` / `llm`；依据 `cfg`，位置 `g_0034`。
  理由：dispatch 为控制流调度，由 LLM 参与决定下一动作。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制转移，不引入、变换或沉淀内容。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制操作，无读取、写入、网络或模型观察效果。

> dispatch

### ir_011

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0039`。
  理由：按路径交付文件属于本地运行时文件操作。

> deliver_bundle_zip_to_path

- `roles` / `sink`；依据 `cfg`，位置 `g_0039`。
  理由：使 bundle 内容到达指定交付路径/存储位置。

> requested_delivery_path

- `effects` / `fs_write`；依据 `source`，位置 `src_003`。
  理由：将 bundle.zip 写入/交付到目标路径。

> 交付到请求的 delivery_path

### ir_012

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0040`。
  理由：return 为运行时控制返回动作。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：纯控制结束，不引入、变换或沉淀内容。

> return

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：普通 return 无内容效果，也不证明用户输出。

> return

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
