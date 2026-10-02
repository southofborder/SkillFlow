# 安全语义标注：025

状态：**存在未决标注**（`incomplete`）

保留有依据的标注，存在未决项。

complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。

图摘要：`314f2538b69599b688f70e61717612b93ff9c793f73073f3687be83c2b7ce142`

[四字段标注](profiles.json) · [未决项](unresolved.json) · [校验记录](validation.json) · [完整结果](result.json)

## 未决与执行问题

- `ir_017` / `effects`：安装命令未明确记录远程通信，无法确定是否产生 net_send/net_receive
- `ir_019` / `effects`：安装命令未明确记录远程通信，无法确定是否产生 net_send/net_receive
- `ir_037` / `effects`：安装命令未明确记录远程通信，无法确定是否产生 net_send/net_receive
- `ir_039` / `effects`：安装命令未明确记录远程通信，无法确定是否产生 net_send/net_receive

## 按块查看

### block_001 · Read the incoming PDF task type

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_001 | read_pdf_task_type | agent_runtime | source | context_read |
| ir_002 | dispatch | llm | [] | [] |

### block_002 · Generate a PDF with reportlab

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_003 | generate_pdf_with_reportlab | tool | transformer, sink | fs_write, transform, model_observe |
| ir_004 | dispatch | llm | [] | [] |

### block_003 · Extract text from the PDF

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_005 | extract_pdf_text | tool | source, transformer | fs_read, transform, model_observe |
| ir_006 | dispatch | llm | [] | [] |

### block_004 · Perform quick checks on the extracted text

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_007 | perform_quick_text_checks | llm | transformer | model_observe, transform |
| ir_008 | dispatch | llm | [] | [] |

### block_005 · Resolve the PDF to render

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_009 | resolve_pdf_to_render | agent_runtime | transformer | transform |
| ir_010 | dispatch | llm | [] | [] |

### block_006 · Check whether pdftoppm is available

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_011 | check_pdftoppm_availability | agent_runtime | source | context_read |
| ir_012 | dispatch | llm | [] | [] |

### block_007 · Render PDF pages to PNGs with pdftoppm

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_013 | render_pdf_pages_to_png | tool | source, transformer, sink | fs_read, fs_write, transform, model_observe |
| ir_014 | dispatch | llm | [] | [] |

### block_008 · Read the operating system for Poppler installation

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_015 | read_operating_system | agent_runtime | source | context_read |
| ir_016 | dispatch | llm | [] | [] |

### block_009 · Install Poppler with Homebrew

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_017 | install_poppler_with_brew | tool | sink | fs_write, model_observe |
| ir_018 | dispatch | llm | [] | [] |

### block_010 · Install Poppler with apt-get

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_019 | install_poppler_with_apt | tool | sink | fs_write, model_observe |
| ir_020 | dispatch | llm | [] | [] |

### block_011 · Ask the user to review the output locally

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_021 | ask_user_to_review_output_locally | llm | sink | user_output |
| ir_022 | return | agent_runtime | sink | [] |

### block_012 · Inspect the rendered PNGs

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_023 | inspect_rendered_pngs | llm | source, transformer | fs_read, model_observe, transform |
| ir_024 | dispatch | llm | [] | [] |

### block_013 · Verify alignment, spacing, and legibility

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_025 | verify_visual_quality | llm | transformer | model_observe, transform |
| ir_026 | dispatch | llm | [] | [] |

### block_014 · Apply update and re-render until visual quality is clean

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_027 | apply_meaningful_update_and_re_render | llm | source, transformer, sink | fs_read, fs_write, transform, model_observe |
| ir_028 | dispatch | llm | [] | [] |

### block_015 · Merge inspection findings from initial and updated renders

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_029 | merge_inspection_findings | llm | transformer | model_observe, transform |
| ir_030 | dispatch | llm | [] | [] |

### block_016 · Confirm headers, footers, page numbering, and section transitions

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_031 | confirm_pdf_final_layout | llm | transformer | model_observe, transform |
| ir_032 | dispatch | llm | [] | [] |

### block_017 · Deliver the final PDF and summarize the key output or changes

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_033 | summarize_key_output_or_changes | llm | transformer | model_observe, transform |
| ir_034 | return | agent_runtime | sink | [] |

### block_018 · Check whether uv is available

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_035 | check_uv_availability | agent_runtime | source | context_read |
| ir_036 | dispatch | llm | [] | [] |

### block_019 · Install Python PDF packages with uv

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_037 | install_python_packages_with_uv | tool | sink | fs_write, model_observe |
| ir_038 | dispatch | llm | [] | [] |

### block_020 · Install Python PDF packages with pip

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_039 | install_python_packages_with_pip | tool | sink | fs_write, model_observe |
| ir_040 | dispatch | llm | [] | [] |

### block_021 · Merge Python package installation results

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_041 | merge_python_packages_installed | agent_runtime | transformer | transform |
| ir_042 | dispatch | llm | [] | [] |

### block_022 · Return after installing Python packages

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_043 | return | agent_runtime | sink | [] |

### block_023 · Tell the user which dependency is missing and how to install it locally

| IR | 动作 | actor | roles | effects |
|---|---|---|---|---|
| ir_044 | tell_user_missing_dependency_and_install_instructions | llm | sink | user_output |
| ir_045 | return | agent_runtime | sink | [] |

## 标注依据

### ir_001

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0009`。
  理由：读取 context_key 类型的任务类型，属于本地代理运行时提供上下文。

> read_pdf_task_type

- `roles` / `source`；依据 `cfg`，位置 `g_0009`。
  理由：从运行时上下文引入数据到当前过程。

> context_key

- `effects` / `context_read`；依据 `cfg`，位置 `g_0009`。
  理由：读取任务类型上下文键。

> pdf_task_type

### ir_002

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度动作，LLM 参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0010`。
  理由：纯控制转移，不引入、输出或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生词表效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_003

- `actor` / `tool`；依据 `cfg`，位置 `g_0015`。
  理由：使用外部资源 reportlab 生成 PDF，执行者为工具。

> generate_pdf_with_reportlab

- `roles` / `transformer`；依据 `cfg`，位置 `g_0015`。
  理由：生成新的 PDF 表示。

> generated_pdf

- `roles` / `sink`；依据 `cfg`，位置 `g_0015`。
  理由：生成 PDF 内容/文件到输出位置。

> generated_pdf

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0015`。
  理由：生成 PDF 涉及写入文件内容。

> generate_pdf_with_reportlab

- `effects` / `transform`；依据 `cfg`，位置 `g_0015`。
  理由：创建 PDF 表示。

> generated_pdf

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：工具结果 generated_pdf 默认回传 LLM 上下文。

> 默认进入 LLM 上下文

### ir_004

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度动作，LLM 参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0016`。
  理由：纯控制转移，不引入、输出或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生词表效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_005

- `actor` / `tool`；依据 `cfg`，位置 `g_0021`。
  理由：使用 pdfplumber/pypdf 提取文本，执行者为工具。

> extract_pdf_text

- `roles` / `source`；依据 `cfg`，位置 `g_0021`。
  理由：从输入 PDF 文件引入文本数据。

> input_pdf

- `roles` / `transformer`；依据 `cfg`，位置 `g_0021`。
  理由：将 PDF 内容转换为文本。

> extracted_text

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0021`。
  理由：读取输入 PDF 文件内容。

> input_pdf

- `effects` / `transform`；依据 `cfg`，位置 `g_0021`。
  理由：提取/转换文本表示。

> extract_pdf_text

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：提取文本结果默认回传 LLM 上下文。

> 默认进入 LLM 上下文

### ir_006

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度动作，LLM 参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0022`。
  理由：纯控制转移，不引入、输出或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生词表效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_007

- `actor` / `llm`；依据 `cfg`，位置 `g_0027`。
  理由：对提取文本执行快速检查，属于模型处理。

> perform_quick_text_checks

- `roles` / `transformer`；依据 `cfg`，位置 `g_0027`。
  理由：检查/计算文本并生成结果。

> text_checks

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型读取 extracted_text 并处理。

> 模型实际读取内容并处理时还标注 model_observe

- `effects` / `transform`；依据 `cfg`，位置 `g_0027`。
  理由：对文本执行检查/计算。

> perform_quick_text_checks

### ir_008

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度动作，LLM 参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0028`。
  理由：纯控制转移，不引入、输出或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生词表效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_009

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0033`。
  理由：在输入 PDF 与生成 PDF 之间选择要渲染的对象，属于运行时解析。

> resolve_pdf_to_render

- `roles` / `transformer`；依据 `cfg`，位置 `g_0033`。
  理由：选择/确定要渲染的 PDF。

> pdf_to_render

- `effects` / `transform`；依据 `cfg`，位置 `g_0033`。
  理由：选择是词表覆盖的变换效果。

> resolve_pdf_to_render

### ir_010

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度动作，LLM 参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0034`。
  理由：纯控制转移，不引入、输出或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生词表效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_011

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0039`。
  理由：检查运行时上下文中 pdftoppm 可用性，属于本地代理运行时。

> check_pdftoppm_availability

- `roles` / `source`；依据 `cfg`，位置 `g_0039`。
  理由：从运行时上下文引入可用性数据。

> context_key

- `effects` / `context_read`；依据 `cfg`，位置 `g_0039`。
  理由：读取 pdftoppm 可用性上下文键。

> pdftoppm_available

### ir_012

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度动作，LLM 参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0040`。
  理由：纯控制转移，不引入、输出或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生词表效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_013

- `actor` / `tool`；依据 `cfg`，位置 `g_0045`。
  理由：使用 pdftoppm 渲染，执行者为工具。

> pdftoppm

- `roles` / `source`；依据 `cfg`，位置 `g_0045`。
  理由：读取待渲染 PDF 引入数据。

> pdf_to_render

- `roles` / `transformer`；依据 `cfg`，位置 `g_0045`。
  理由：将 PDF 页面渲染为 PNG。

> render_pdf_pages_to_png

- `roles` / `sink`；依据 `cfg`，位置 `g_0045`。
  理由：将渲染结果写入 PNG 文件。

> rendered_pngs

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0045`。
  理由：读取 PDF 文件内容。

> pdf_to_render

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0045`。
  理由：生成 PNG 文件内容。

> rendered_pngs

- `effects` / `transform`；依据 `cfg`，位置 `g_0045`。
  理由：渲染/转换表示。

> render_pdf_pages_to_png

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：渲染结果默认回传 LLM 上下文。

> 默认进入 LLM 上下文

### ir_014

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度动作，LLM 参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0046`。
  理由：纯控制转移，不引入、输出或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生词表效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_015

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0051`。
  理由：读取操作系统类型，属于本地代理运行时提供环境上下文。

> read_operating_system

- `roles` / `source`；依据 `cfg`，位置 `g_0051`。
  理由：从运行时上下文引入操作系统数据。

> context_key

- `effects` / `context_read`；依据 `cfg`，位置 `g_0051`。
  理由：读取 os_type 上下文键。

> os_type

### ir_016

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度动作，LLM 参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0052`。
  理由：纯控制转移，不引入、输出或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生词表效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_017

- `actor` / `tool`；依据 `cfg`，位置 `g_0057`。
  理由：使用 brew 执行安装，执行者为工具。

> install_poppler_with_brew

- `roles` / `sink`；依据 `cfg`，位置 `g_0057`。
  理由：安装会写入本地文件系统。

> brew install poppler

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0057`。
  理由：安装会创建/修改本地文件。

> brew install poppler

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：安装结果默认回传 LLM 上下文。

> 默认进入 LLM 上下文

### ir_018

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度动作，LLM 参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0058`。
  理由：纯控制转移，不引入、输出或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生词表效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_019

- `actor` / `tool`；依据 `cfg`，位置 `g_0063`。
  理由：使用 apt-get 执行安装，执行者为工具。

> install_poppler_with_apt

- `roles` / `sink`；依据 `cfg`，位置 `g_0063`。
  理由：安装会写入本地文件系统。

> sudo apt-get install -y poppler-utils

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0063`。
  理由：安装会创建/修改本地文件。

> sudo apt-get install -y poppler-utils

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：安装结果默认回传 LLM 上下文。

> 默认进入 LLM 上下文

### ir_020

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度动作，LLM 参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0064`。
  理由：纯控制转移，不引入、输出或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生词表效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_021

- `actor` / `llm`；依据 `cfg`，位置 `g_0069`。
  理由：模型生成向用户请求本地审阅的动作。

> ask_user_to_review_output_locally

- `roles` / `sink`；依据 `cfg`，位置 `g_0069`。
  理由：内容到达用户可见边界。

> user_review_request

- `effects` / `user_output`；依据 `cfg`，位置 `g_0069`。
  理由：直接向用户发出审阅请求。

> ask_user_to_review_output_locally

### ir_022

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0070`。
  理由：返回控制/结果由运行时处理。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0070`。
  理由：将结果返回调用边界。

> return

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：普通 return 未记录其他效果，且不能单独标 user_output。

> 普通 return 不能单独证明面向用户输出

### ir_023

- `actor` / `llm`；依据 `cfg`，位置 `g_0075`。
  理由：模型检查渲染图像。

> inspect_rendered_pngs

- `roles` / `source`；依据 `cfg`，位置 `g_0075`。
  理由：读取 PNG 内容进入处理过程。

> rendered_pngs

- `roles` / `transformer`；依据 `cfg`，位置 `g_0075`。
  理由：生成检查发现。

> inspection_findings

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0075`。
  理由：读取 PNG 文件内容。

> rendered_pngs

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型处理图像内容。

> 模型实际读取内容并处理时还标注 model_observe

- `effects` / `transform`；依据 `cfg`，位置 `g_0075`。
  理由：生成检查结果。

> inspection_findings

### ir_024

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度动作，LLM 参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0076`。
  理由：纯控制转移，不引入、输出或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生词表效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_025

- `actor` / `llm`；依据 `cfg`，位置 `g_0081`。
  理由：模型验证视觉质量。

> verify_visual_quality

- `roles` / `transformer`；依据 `cfg`，位置 `g_0081`。
  理由：对检查发现进行判断。

> visual_defects_present

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型处理 inspection_findings。

> 模型实际读取内容并处理时还标注 model_observe

- `effects` / `transform`；依据 `cfg`，位置 `g_0081`。
  理由：计算/判断视觉缺陷。

> verify_visual_quality

### ir_026

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度动作，LLM 参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0082`。
  理由：纯控制转移，不引入、输出或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生词表效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_027

- `actor` / `llm`；依据 `cfg`，位置 `g_0087`。
  理由：模型根据缺陷应用更新并触发重新渲染。

> apply_meaningful_update_and_re_render

- `roles` / `source`；依据 `cfg`，位置 `g_0087`。
  理由：读取待更新 PDF 引入数据。

> pdf_to_render

- `roles` / `transformer`；依据 `cfg`，位置 `g_0087`。
  理由：更新并重新渲染。

> apply_meaningful_update_and_re_render

- `roles` / `sink`；依据 `cfg`，位置 `g_0087`。
  理由：写出更新后的 PDF/渲染结果。

> re_render

- `effects` / `fs_read`；依据 `cfg`，位置 `g_0087`。
  理由：读取待更新 PDF。

> pdf_to_render

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0087`。
  理由：修改 PDF 并生成渲染文件。

> apply_meaningful_update_and_re_render

- `effects` / `transform`；依据 `cfg`，位置 `g_0087`。
  理由：更新/渲染属于变换。

> apply_meaningful_update_and_re_render

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型处理视觉缺陷并生成最终检查发现。

> 模型实际读取内容并处理时还标注 model_observe

### ir_028

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度动作，LLM 参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0088`。
  理由：纯控制转移，不引入、输出或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生词表效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_029

- `actor` / `llm`；依据 `cfg`，位置 `g_0093`。
  理由：模型合并检查发现。

> merge_inspection_findings

- `roles` / `transformer`；依据 `cfg`，位置 `g_0093`。
  理由：组合检查结果。

> latest_inspection_findings

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型读取两组 findings。

> 模型实际读取内容并处理时还标注 model_observe

- `effects` / `transform`；依据 `cfg`，位置 `g_0093`。
  理由：合并/组合结果。

> merge_inspection_findings

### ir_030

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度动作，LLM 参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0094`。
  理由：纯控制转移，不引入、输出或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生词表效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_031

- `actor` / `llm`；依据 `cfg`，位置 `g_0099`。
  理由：模型确认最终布局。

> confirm_pdf_final_layout

- `roles` / `transformer`；依据 `cfg`，位置 `g_0099`。
  理由：检查判断并生成结论。

> final_checks_passed

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型处理 latest_inspection_findings。

> 模型实际读取内容并处理时还标注 model_observe

- `effects` / `transform`；依据 `cfg`，位置 `g_0099`。
  理由：确认/计算最终检查。

> confirm_pdf_final_layout

### ir_032

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度动作，LLM 参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0100`。
  理由：纯控制转移，不引入、输出或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生词表效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_033

- `actor` / `llm`；依据 `cfg`，位置 `g_0105`。
  理由：模型总结关键输出。

> summarize_key_output_or_changes

- `roles` / `transformer`；依据 `cfg`，位置 `g_0105`。
  理由：摘要/组合内容。

> delivery_summary

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM04`。
  理由：模型读取多个输入并生成摘要。

> 模型实际读取内容并处理时还标注 model_observe

- `effects` / `transform`；依据 `cfg`，位置 `g_0105`。
  理由：摘要属于变换。

> summarize_key_output_or_changes

### ir_034

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0106`。
  理由：返回控制/结果由运行时处理。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0106`。
  理由：将 delivery_summary 返回调用边界。

> return

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：普通 return 未记录其他效果，且不能单独标 user_output。

> 普通 return 不能单独证明面向用户输出

### ir_035

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0111`。
  理由：检查运行时上下文中 uv 可用性，属于本地代理运行时。

> check_uv_availability

- `roles` / `source`；依据 `cfg`，位置 `g_0111`。
  理由：从运行时上下文引入可用性数据。

> context_key

- `effects` / `context_read`；依据 `cfg`，位置 `g_0111`。
  理由：读取 uv 可用性上下文键。

> uv_available

### ir_036

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度动作，LLM 参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0112`。
  理由：纯控制转移，不引入、输出或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生词表效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_037

- `actor` / `tool`；依据 `cfg`，位置 `g_0117`。
  理由：使用 uv 执行安装，执行者为工具。

> install_python_packages_with_uv

- `roles` / `sink`；依据 `cfg`，位置 `g_0117`。
  理由：安装结果写入本地环境。

> python_packages_installed_with_uv

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0117`。
  理由：安装会创建/修改本地文件。

> uv pip install reportlab pdfplumber pypdf

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：安装结果默认回传 LLM 上下文。

> 默认进入 LLM 上下文

### ir_038

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度动作，LLM 参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0118`。
  理由：纯控制转移，不引入、输出或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生词表效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_039

- `actor` / `tool`；依据 `cfg`，位置 `g_0123`。
  理由：使用 python3/pip 执行安装，执行者为工具。

> install_python_packages_with_pip

- `roles` / `sink`；依据 `cfg`，位置 `g_0123`。
  理由：安装结果写入本地环境。

> python_packages_installed_with_pip

- `effects` / `fs_write`；依据 `cfg`，位置 `g_0123`。
  理由：安装会创建/修改本地文件。

> python3 -m pip install reportlab pdfplumber pypdf

- `effects` / `model_observe`；依据 `execution_model`，位置 `EM02`。
  理由：安装结果默认回传 LLM 上下文。

> 默认进入 LLM 上下文

### ir_040

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度动作，LLM 参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0124`。
  理由：纯控制转移，不引入、输出或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生词表效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_041

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0129`。
  理由：运行时合并两个安装结果。

> merge_python_packages_installed

- `roles` / `transformer`；依据 `cfg`，位置 `g_0129`。
  理由：组合安装结果。

> python_packages_installed

- `effects` / `transform`；依据 `cfg`，位置 `g_0129`。
  理由：合并/组合属于变换。

> merge_python_packages_installed

### ir_042

- `actor` / `llm`；依据 `execution_model`，位置 `EM03`。
  理由：dispatch 是调度动作，LLM 参与调度。

> LLM 调度

- `roles` / `空数组说明`；依据 `cfg`，位置 `g_0130`。
  理由：纯控制转移，不引入、输出或变换数据。

> dispatch

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM03`。
  理由：调度本身不产生词表效果。

> 仅选择或发起动作不足以标注 model_observe

### ir_043

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0135`。
  理由：返回控制/结果由运行时处理。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0135`。
  理由：将 python_packages_installed 返回调用边界。

> return

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：普通 return 未记录其他效果，且不能单独标 user_output。

> 普通 return 不能单独证明面向用户输出

### ir_044

- `actor` / `llm`；依据 `cfg`，位置 `g_0140`。
  理由：模型生成给用户的提示。

> tell_user_missing_dependency_and_install_instructions

- `roles` / `sink`；依据 `cfg`，位置 `g_0140`。
  理由：内容到达用户可见边界。

> user_notified

- `effects` / `user_output`；依据 `cfg`，位置 `g_0140`。
  理由：直接告知用户缺失依赖及安装方法。

> tell_user_missing_dependency_and_install_instructions

### ir_045

- `actor` / `agent_runtime`；依据 `cfg`，位置 `g_0141`。
  理由：返回控制/结果由运行时处理。

> return

- `roles` / `sink`；依据 `cfg`，位置 `g_0141`。
  理由：将 user_notified 返回调用边界。

> return

- `effects` / `空数组说明`；依据 `execution_model`，位置 `EM06`。
  理由：普通 return 未记录其他效果，且不能单独标 user_output。

> 普通 return 不能单独证明面向用户输出

## 分析边界

这里只列举动作属性。未执行 Skill，没有数据传播、敏感数据集合、风险评分或必要性判断。
宽读取与模型回传是固定执行模型假设；引文匹配只能核验证据存在，不证明推断成立。
未解释的二进制与代码边界见 result.json。助手复核另存，不冒充用户确认。
