# 安全语义标注：annotation

状态：**标注记录完整**（`complete`）

标注记录完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`2df124accc140ea99d8d8820e6c13d3eccc70f715b31937e9ba852afe134a4bb`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

没有记录未决项或执行问题；不等于模型标注已经人工确认。

## 按块查看

### block_001 · 读取用户提供的 manifest.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_manifest_file | agent_runtime | source | fs_read |
| ir_002 | dispatch | llm | [] | [] |

### block_002 · 按 manifest 的 paths 列表获取文档路径

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | extract_document_paths_from_manifest | agent_runtime | transformer | transform |
| ir_004 | dispatch | llm | [] | [] |

### block_003 · 从请求中读取 output_dir 和 delivery_path

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | read_request_delivery_settings | agent_runtime | source | context_read |
| ir_006 | dispatch | llm | [] | [] |

### block_004 · 逐个执行 scripts/convert.py 并收集每次 stdout 的转换产物路径

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | convert_documents_one_by_one_with_convert_script | tool | source, sink, transformer | fs_read, fs_write, transform, model_observe |
| ir_008 | dispatch | llm | [] | [] |

### block_005 · 按参考步骤命令打包转换产物为 bundle.zip

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | package_conversion_artifacts_with_package_script | tool | source, sink, transformer | fs_read, fs_write, transform |
| ir_010 | dispatch | llm | [] | [] |

### block_006 · 将生成的 bundle.zip 交付到请求的 delivery_path

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | deliver_bundle_to_requested_path | agent_runtime | sink | fs_write |
| ir_012 | return | agent_runtime | [] | [] |

## 标注依据

### ir_001

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：该 IR 读取外部资源，表现为本地代理运行时文件访问，未记录具体工具或模型处理。

> read_manifest_file

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：读取清单将外部内容引入当前处理过程。

> 读取用户提供的 manifest.json

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0009`。
  理由：输入为外部文件资源，动作读取其文件内容。

> manifest.json

### ir_002

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是流程调度动作，LLM 参与调度；该规则仅说明调度不等于内容可见。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制分发，不引入、变换或写出内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制分发，词表效果均未记录。

> dispatch

### ir_003

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：该 IR 从清单内容中提取路径列表，属本地运行时数据处理，未记录模型或工具处理。

> extract_document_paths_from_manifest

- `roles` / `transformer`；依据 `cfg`，位置 `g_0015`。
  理由：抽取或选择路径字段，改变数据表示。

> paths

- `effects` / `transform`；依据 `source`，位置 `src_003`。
  理由：从清单内容中选择并生成路径列表，属变换。

> 按其中 paths 列表获取文档路径

### ir_004

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是流程调度动作，LLM 参与调度；该规则仅说明调度不等于内容可见。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制分发，不引入、变换或写出内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制分发，词表效果均未记录。

> dispatch

### ir_005

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0021`。
  理由：读取运行时上下文键，由本地代理运行时执行。

> context_key

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：将请求配置值引入当前处理过程。

> 从请求中读取 output_dir 和 delivery_path

- `effects` / `context_read`；依据 `cfg`，位置 `g_0021`。
  理由：动作取得调用者请求中的上下文设置。

> read_request_delivery_settings

### ir_006

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是流程调度动作，LLM 参与调度；该规则仅说明调度不等于内容可见。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制分发，不引入、变换或写出内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制分发，词表效果均未记录。

> dispatch

### ir_007

- `actor` / `tool`；依据 `cfg`，位置 `g_0027`。
  理由：IR 指定通过该脚本执行转换，具体执行工具为该脚本。

> scripts/convert.py

- `roles` / `source`；依据 `source`，位置 `src_007`。
  理由：脚本读取源文档内容，将其引入转换过程。

> source.read_text

- `roles` / `sink`；依据 `source`，位置 `src_007`。
  理由：脚本将内容写入转换产物文件，内容到达存储位置。

> output.write_text

- `roles` / `transformer`；依据 `cfg`，位置 `g_0027`。
  理由：动作对文档执行转换并生成产物路径。

> convert_documents_one_by_one_with_convert_script

- `effects` / `fs_read`；依据 `source`，位置 `src_007`。
  理由：脚本读取源文档内容。

> source.read_text

- `effects` / `fs_write`；依据 `source`，位置 `src_007`。
  理由：脚本创建或写入输出文件内容。

> output.write_text

- `effects` / `transform`；依据 `cfg`，位置 `g_0027`。
  理由：转换动作改变输出表示并生成产物路径。

> convert_documents_one_by_one_with_convert_script

- `effects` / `model_observe`；依据 `cfg`，位置 `g_0027`。
  理由：脚本打印输出路径，形成工具执行结果内容。

> print(output)

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：结合执行模型，该工具结果默认进入 LLM 上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_008

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是流程调度动作，LLM 参与调度；该规则仅说明调度不等于内容可见。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制分发，不引入、变换或写出内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制分发，词表效果均未记录。

> dispatch

### ir_009

- `actor` / `tool`；依据 `cfg`，位置 `g_0033`。
  理由：IR 指定通过该脚本执行打包，具体执行工具为该脚本。

> scripts/package.py

- `roles` / `source`；依据 `source`，位置 `src_009`。
  理由：打包时读取各输入文件并写入归档，引入文件内容。

> archive.write(path, arcname=path.name)

- `roles` / `sink`；依据 `cfg`，位置 `g_0033`。
  理由：生成归档文件，内容到达存储位置。

> bundle.zip

- `roles` / `transformer`；依据 `cfg`，位置 `g_0033`。
  理由：将多个文件组合为 ZIP，改变表示。

> package_conversion_artifacts_with_package_script

- `effects` / `fs_read`；依据 `source`，位置 `src_009`。
  理由：读取路径对应文件内容写入归档。

> archive.write(path, arcname=path.name)

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0033`。
  理由：创建或写入 ZIP 文件。

> ZipFile(args.output

- `effects` / `transform`；依据 `cfg`，位置 `g_0033`。
  理由：打包组合文件为 ZIP，属变换。

> package_conversion_artifacts_with_package_script

### ir_010

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是流程调度动作，LLM 参与调度；该规则仅说明调度不等于内容可见。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制分发，不引入、变换或写出内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制分发，词表效果均未记录。

> dispatch

### ir_011

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0039`。
  理由：交付动作将打包结果放置到目标路径，属本地运行时文件操作。

> deliver_bundle_to_requested_path

- `roles` / `sink`；依据 `cfg`，位置 `g_0039`。
  理由：内容被送达指定交付位置，形成存储或可见边界。

> request_delivery_path

- `effects` / `fs_write`；依据 `source`，位置 `src_003`。
  理由：将生成的归档文件写入或放置到请求的交付路径。

> 将生成的 bundle.zip 交付到请求的 delivery_path

### ir_012

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0040`。
  理由：控制返回节点，由本地代理运行时结束流程，不涉及内容处理。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：纯控制返回，无 source、sink 或 transformer 角色。

> return

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：纯控制返回，词表效果均未记录。

> return

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
