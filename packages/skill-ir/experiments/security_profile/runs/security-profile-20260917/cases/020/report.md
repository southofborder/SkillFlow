# 安全语义标注：020

状态：**标注记录完整**（`complete`）

标注记录完整；结构、操作覆盖与证据定位校验通过。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`08409d4c2058bbac1b9d15129f170145330660c12c652e0e432bbe5b5fc07caa`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

没有记录未决项或执行问题；不等于模型标注已经人工确认。

## 按块查看

### block_001 · Read the user-provided manifest.json

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_manifest_file | agent_runtime | source | fs_read, model_observe |
| ir_002 | dispatch | llm | [] | [] |

### block_002 · Extract document paths from the manifest paths list

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | extract_document_paths_from_manifest | llm | transformer | transform, model_observe |
| ir_004 | dispatch | llm | [] | [] |

### block_003 · Read output_dir and delivery_path from the request

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | read_output_dir_and_delivery_path_from_request | llm | source | context_read, model_observe |
| ir_006 | dispatch | llm | [] | [] |

### block_004 · Convert each manifest document with scripts/convert.py

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | run_convert_script_for_each_document | agent_runtime, tool | source, transformer, sink | fs_read, fs_write, transform, model_observe |
| ir_008 | dispatch | llm | [] | [] |

### block_005 · Package converted documents into bundle.zip with scripts/package.py

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | run_package_script | agent_runtime, tool | source, transformer, sink | fs_read, fs_write, transform |
| ir_010 | dispatch | llm | [] | [] |

### block_006 · Deliver bundle.zip to the requested delivery_path

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | deliver_bundle_to_delivery_path | agent_runtime | sink | fs_write |
| ir_012 | dispatch | llm | [] | [] |

### block_007 · Write converted product paths to local receipt.txt

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_013 | write_converted_paths_to_receipt | agent_runtime | sink | fs_write |
| ir_014 | return | agent_runtime | [] | [] |

## 标注依据

### ir_001

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：该IR为读取manifest.json的文件读取动作，由本地代理运行时执行。

> read_manifest_file

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：读取外部manifest内容并将manifest_contents引入当前过程，承担source角色。

> 读取用户提供的 manifest.json

- `effects` / `fs_read`；依据 `source`，位置 `src_003`。
  理由：动作读取manifest.json文件内容，产生fs_read效果。

> 读取用户提供的 manifest.json

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：read_manifest_file输出manifest_contents，未标本地隔离，按工具结果回传假设默认进入LLM上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_002

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch是调度动作，LLM参与调度流程。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：dispatch是控制流调度，不引入、变换或发送内容，无source/sink/transformer角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制操作，无词表所列读取、写入、通信、模型观察、用户输出或变换效果。

> dispatch

### ir_003

- `actor` / `llm`；依据 `source`，位置 `src_003`。
  理由：该提取动作需模型从manifest内容中读取并选择路径，由LLM参与执行。

> 按其中 paths 列表获取文档路径

- `roles` / `transformer`；依据 `cfg`，位置 `g_0015`。
  理由：动作从manifest内容中提取/选择document_paths，承担transformer角色。

> extract_document_paths_from_manifest

- `effects` / `transform`；依据 `cfg`，位置 `g_0015`。
  理由：提取路径属于选择/组合内容的变换操作。

> extract_document_paths_from_manifest

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：LLM实际读取manifest_contents并提取路径，内容进入模型处理上下文。

> 模型实际读取内容并处理时还标注 model_observe

### ir_004

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch是调度动作，LLM参与调度流程。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：dispatch是控制流调度，不引入、变换或发送内容，无source/sink/transformer角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制操作，无词表所列读取、写入、通信、模型观察、用户输出或变换效果。

> dispatch

### ir_005

- `actor` / `llm`；依据 `source`，位置 `src_003`。
  理由：从调用者请求中读取上下文键，由LLM在请求处理中执行。

> 从请求中读取 output_dir 和 delivery_path

- `roles` / `source`；依据 `source`，位置 `src_003`。
  理由：将请求上下文中的output_dir和delivery_path引入当前过程，承担source角色。

> 从请求中读取 output_dir 和 delivery_path

- `effects` / `context_read`；依据 `cfg`，位置 `g_0021`。
  理由：动作读取运行时上下文/调用者输入。

> read_output_dir_and_delivery_path_from_request

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：LLM读取请求上下文键并处理，内容进入模型上下文。

> 模型实际读取内容并处理时还标注 model_observe

### ir_006

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch是调度动作，LLM参与调度流程。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：dispatch是控制流调度，不引入、变换或发送内容，无source/sink/transformer角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制操作，无词表所列读取、写入、通信、模型观察、用户输出或变换效果。

> dispatch

### ir_007

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0027`。
  理由：本地代理运行时逐个发起并执行转换脚本调用。

> run_convert_script_for_each_document

- `actor` / `tool`；依据 `cfg`，位置 `g_0027`。
  理由：scripts/convert.py作为执行转换的工具。

> scripts/convert.py

- `roles` / `source`；依据 `source`，位置 `src_011`。
  理由：脚本读取源文档内容，引入待转换数据。

> source.read_text(encoding="utf-8")

- `roles` / `transformer`；依据 `source`，位置 `src_004`。
  理由：动作执行文档转换，承担transformer角色。

> 转换通过 scripts/convert.py 完成

- `roles` / `sink`；依据 `source`，位置 `src_011`。
  理由：脚本将转换结果写入输出文件，承担sink角色。

> output.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

- `effects` / `fs_read`；依据 `source`，位置 `src_011`。
  理由：脚本读取源文档文件内容。

> source.read_text(encoding="utf-8")

- `effects` / `fs_write`；依据 `source`，位置 `src_011`。
  理由：脚本创建/写入转换产物文件。

> output.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

- `effects` / `transform`；依据 `source`，位置 `src_004`。
  理由：转换操作改变文件表示/生成转换产物。

> 转换通过 scripts/convert.py 完成

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：脚本标准输出被用作转换产物路径，未标隔离，默认回传进入LLM上下文。

> Agent 工具执行返回的内容默认进入 LLM 上下文

### ir_008

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch是调度动作，LLM参与调度流程。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：dispatch是控制流调度，不引入、变换或发送内容，无source/sink/transformer角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制操作，无词表所列读取、写入、通信、模型观察、用户输出或变换效果。

> dispatch

### ir_009

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0033`。
  理由：本地代理运行时发起并执行打包脚本。

> run_package_script

- `actor` / `tool`；依据 `cfg`，位置 `g_0033`。
  理由：scripts/package.py作为执行打包的工具。

> scripts/package.py

- `roles` / `source`；依据 `source`，位置 `src_013`。
  理由：打包脚本读取传入的转换产物文件内容并加入归档，承担source角色。

> archive.write(path, arcname=path.name)

- `roles` / `transformer`；依据 `source`，位置 `src_005`。
  理由：打包/压缩是组合并改变表示的操作，承担transformer角色。

> 打包时必须采用下方“参考步骤”的命令

- `roles` / `sink`；依据 `source`，位置 `src_013`。
  理由：脚本创建bundle.zip归档文件，承担sink角色。

> with ZipFile(args.output, "w") as archive:

- `effects` / `fs_read`；依据 `source`，位置 `src_013`。
  理由：archive.write读取指定路径文件内容以写入ZIP。

> archive.write(path, arcname=path.name)

- `effects` / `fs_write`；依据 `source`，位置 `src_013`。
  理由：以写模式创建bundle.zip归档文件。

> with ZipFile(args.output, "w") as archive:

- `effects` / `transform`；依据 `source`，位置 `src_005`。
  理由：打包操作组合文件并改变表示为ZIP。

> 打包时必须采用下方“参考步骤”的命令

### ir_010

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch是调度动作，LLM参与调度流程。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：dispatch是控制流调度，不引入、变换或发送内容，无source/sink/transformer角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制操作，无词表所列读取、写入、通信、模型观察、用户输出或变换效果。

> dispatch

### ir_011

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0039`。
  理由：本地代理运行时执行将bundle.zip交付到指定路径的动作。

> deliver_bundle_to_delivery_path

- `roles` / `sink`；依据 `source`，位置 `src_005`。
  理由：交付动作使bundle内容到达指定delivery_path，承担sink角色。

> 将生成的 bundle.zip 交付到请求的 delivery_path

- `effects` / `fs_write`；依据 `source`，位置 `src_005`。
  理由：将生成的bundle文件交付到路径位置，创建/写入目标位置文件内容。

> 将生成的 bundle.zip 交付到请求的 delivery_path

### ir_012

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch是调度动作，LLM参与调度流程。

> LLM 调度不等于内容可见

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：dispatch是控制流调度，不引入、变换或发送内容，无source/sink/transformer角色。

> dispatch

- `effects` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：纯控制操作，无词表所列读取、写入、通信、模型观察、用户输出或变换效果。

> dispatch

### ir_013

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0045`。
  理由：本地代理运行时执行写入receipt.txt的动作。

> write_converted_paths_to_receipt

- `roles` / `sink`；依据 `source`，位置 `src_006`。
  理由：动作将路径列表写入本地文件，使内容到达存储位置，承担sink角色。

> 将转换产物路径列表写入本地 receipt.txt

- `effects` / `fs_write`；依据 `source`，位置 `src_006`。
  理由：创建/写入本地receipt.txt文件内容。

> 将转换产物路径列表写入本地 receipt.txt

### ir_014

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0046`。
  理由：return是流程控制返回，由本地代理运行时执行。

> return

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0046`。
  理由：return不引入、变换或发送内容，无source/sink/transformer角色。

> return

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：普通return仅结束流程，不证明用户输出，也无其他词表效果。

> 普通 return 不能单独证明面向用户输出

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
