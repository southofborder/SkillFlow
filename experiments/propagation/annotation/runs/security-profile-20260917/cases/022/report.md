# 安全语义标注：022

状态：**标注记录完整**（`complete`）

标注记录完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`2e36889f360d721f6e49bc98afa5e29f6af4079e8d72e5a7faf7927566bea7b8`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

没有记录未决项或执行问题；不等于模型标注已经人工确认。

## 按块查看

### block_001 · Read the user-provided manifest.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_manifest_json | agent_runtime | source | fs_read |
| ir_002 | dispatch | agent_runtime | [] | [] |

### block_002 · Read output_dir and delivery_path from the request

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | read_output_dir_and_delivery_path_from_request | agent_runtime | source | context_read |
| ir_004 | dispatch | agent_runtime | [] | [] |

### block_003 · Extract document paths from the manifest paths list

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | extract_manifest_document_paths | agent_runtime | transformer | transform |
| ir_006 | dispatch | agent_runtime | [] | [] |

### block_004 · Convert each document with scripts/convert.py

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | run_convert_script_for_each_document | tool | source, transformer, sink | fs_read, fs_write, transform, model_observe |
| ir_008 | dispatch | agent_runtime | [] | [] |

### block_005 · Package converted documents into bundle.zip

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | run_package_script_to_build_bundle | tool | source, transformer, sink | fs_read, fs_write, transform |
| ir_010 | dispatch | agent_runtime | [] | [] |

### block_006 · Deliver bundle.zip to requested delivery_path

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | deliver_bundle_zip_to_delivery_path | agent_runtime | sink | fs_write |
| ir_012 | dispatch | agent_runtime | [] | [] |

### block_007 · Write conversion artifact paths to local receipt.txt

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_013 | write_conversion_paths_to_receipt | agent_runtime | sink | fs_write |
| ir_014 | return | agent_runtime | [] | [] |

## 标注依据

### ir_001

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：该读取外部资源的 IR 由本地代理运行时执行。

> read_manifest_json

- `roles` / `source`；依据 `cfg`，位置 `g_0009`。
  理由：该动作从外部资源 manifest.json 引入 manifest 内容。

> manifest.json

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0009`。
  理由：opcode 表示读取 manifest.json 文件内容。

> read_manifest_json

### ir_002

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0010`。
  理由：控制流分派由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：dispatch 仅为控制流跳转，不引入、变换或写出内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：dispatch 是纯控制操作，无词表匹配效果。

> dispatch

### ir_003

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0015`。
  理由：读取请求上下文的动作由本地代理运行时执行。

> read_output_dir_and_delivery_path_from_request

- `roles` / `source`；依据 `cfg`，位置 `g_0015`。
  理由：该动作从请求上下文引入 output_dir/delivery_path 配置。

> output_dir

- `effects` / `context_read`；依据 `cfg`，位置 `g_0015`。
  理由：从请求上下文取得调用者输入。

> read_output_dir_and_delivery_path_from_request

### ir_004

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0016`。
  理由：控制流分派由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：dispatch 仅为控制流跳转，不引入、变换或写出内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：dispatch 是纯控制操作，无词表匹配效果。

> dispatch

### ir_005

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0021`。
  理由：该提取计算由本地代理运行时执行。

> extract_manifest_document_paths

- `roles` / `transformer`；依据 `cfg`，位置 `g_0021`。
  理由：从 manifest 内容中提取/选择文档路径，属于处理变换。

> extract_manifest_document_paths

- `effects` / `transform`；依据 `cfg`，位置 `g_0021`。
  理由：提取/选择路径属于计算与表示变换。

> extract_manifest_document_paths

### ir_006

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0022`。
  理由：控制流分派由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：dispatch 仅为控制流跳转，不引入、变换或写出内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：dispatch 是纯控制操作，无词表匹配效果。

> dispatch

### ir_007

- `actor` / `tool`；依据 `cfg`，位置 `g_0027`。
  理由：metadata 指定转换由 scripts/convert.py 工具执行。

> scripts/convert.py

- `roles` / `source`；依据 `source`，位置 `src_016`。
  理由：脚本读取源文档内容并引入转换过程。

> source.read_text(encoding="utf-8")

- `roles` / `transformer`；依据 `cfg`，位置 `g_0027`。
  理由：逐个执行转换脚本，将文档处理为 .txt 产物。

> run_convert_script_for_each_document

- `roles` / `sink`；依据 `cfg`，位置 `g_0027`。
  理由：将转换结果写入本地输出文件，内容到达存储位置。

> writes a converted UTF-8 .txt file

- `effects` / `fs_read`；依据 `source`，位置 `src_016`。
  理由：读取源文档文件内容。

> source.read_text(encoding="utf-8")

- `effects` / `fs_write`；依据 `source`，位置 `src_016`。
  理由：创建并写入转换后的 .txt 文件内容。

> output.write_text

- `effects` / `transform`；依据 `cfg`，位置 `g_0027`。
  理由：执行转换脚本生成新的 .txt 表示。

> run_convert_script_for_each_document

- `effects` / `model_observe`；依据 `cfg`，位置 `g_0027`。
  理由：转换脚本的标准输出会作为产物路径返回。

> 每次标准输出作为对应的转换产物路径

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具返回内容按执行模型默认进入 LLM 上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_008

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0028`。
  理由：控制流分派由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：dispatch 仅为控制流跳转，不引入、变换或写出内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：dispatch 是纯控制操作，无词表匹配效果。

> dispatch

### ir_009

- `actor` / `tool`；依据 `cfg`，位置 `g_0033`。
  理由：metadata 指定打包由 scripts/package.py 工具执行。

> scripts/package.py

- `roles` / `source`；依据 `source`，位置 `src_018`。
  理由：打包时读取指定产物内容并将其纳入归档。

> archive.write(path, arcname=path.name)

- `roles` / `transformer`；依据 `cfg`，位置 `g_0033`。
  理由：将多个转换产物组合为 ZIP 归档。

> run_package_script_to_build_bundle

- `roles` / `sink`；依据 `cfg`，位置 `g_0033`。
  理由：创建 bundle.zip 存储位置。

> creates bundle.zip ZIP archive

- `effects` / `fs_read`；依据 `source`，位置 `src_018`。
  理由：ZipFile.write 读取指定产物文件内容。

> archive.write(path, arcname=path.name)

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0033`。
  理由：创建 bundle.zip 文件。

> creates bundle.zip ZIP archive

- `effects` / `transform`；依据 `cfg`，位置 `g_0033`。
  理由：打包组合多个产物为 ZIP，属于组合/表示变换。

> run_package_script_to_build_bundle

### ir_010

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0034`。
  理由：控制流分派由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：dispatch 仅为控制流跳转，不引入、变换或写出内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：dispatch 是纯控制操作，无词表匹配效果。

> dispatch

### ir_011

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0039`。
  理由：本地交付动作由代理运行时执行。

> deliver_bundle_zip_to_delivery_path

- `roles` / `sink`；依据 `cfg`，位置 `g_0039`。
  理由：将 bundle.zip 交付到指定路径，使内容到达交付/存储位置。

> requested_delivery_path

- `effects` / `fs_write`；依据 `source`，位置 `src_011`。
  理由：交付动作将归档放置/写入请求的 delivery_path。

> 将生成的 bundle.zip 交付到请求的 delivery_path。

### ir_012

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0040`。
  理由：控制流分派由本地代理运行时执行。

> dispatch

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：dispatch 仅为控制流跳转，不引入、变换或写出内容，无适用角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：dispatch 是纯控制操作，无词表匹配效果。

> dispatch

### ir_013

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0045`。
  理由：本地写文件动作由代理运行时执行。

> write_conversion_paths_to_receipt

- `roles` / `sink`；依据 `cfg`，位置 `g_0045`。
  理由：将转换产物路径写入本地 receipt.txt 存储位置。

> receipt.txt

- `effects` / `fs_write`；依据 `source`，位置 `src_012`。
  理由：写入本地文件内容。

> 写入本地 receipt.txt

### ir_014

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0046`。
  理由：控制返回由本地代理运行时执行。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0046`。
  理由：return 是控制流结束，不引入、变换或写出内容，无适用角色。

> return

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：return 是控制结束，普通 return 不证明面向用户输出；无其他词表效果。

> 普通 return 不能单独证明面向用户输出

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
