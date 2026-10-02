# 022-document-bundle-delivery · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：D04；运行：full-pipeline-v4-20260918-rerun-failed；选图轮次：3
- 反馈停止：audit_passed；原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。
- 安全标注：incomplete；原因：保留有依据的标注，存在未决项。
- 图 SHA-256：9b773ace215334006228669ceaca7490a43fa156c5935de313555fa3bc05bdef；源文 SHA-256：277ef0b935d5afad71bc83471e55f8e85a71f3d0c800642e08def9335e27aaca

未填写保守说明不代表精确保留；覆盖记录不证明语义完整。

反馈完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/022/feedback/result.json>)；本地审查页也可展开全文。

安全标注完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/022/annotation/result.json>)；本地审查页也可展开全文。

## finding_1 · context · represented

原文要求：SKILL.md 的 frontmatter 名称/描述、SKILL 标题、workflow.md 标题及“参考步骤”节名属于背景或结构上下文，不是业务动作要求。

当前表示：受控回述用 entry、各块名称以及打包约束中对“参考步骤”的引用和 metadata 命令承载这些上下文；未把标题或节名扩写成额外业务步骤。

比较理由：这些源单元是标题、元数据或节名，不是可执行业务要求；受控回述没有据其新增动作，相关业务流程在后续 findings 中按操作与约束核对。

源文 `src_001` · `SKILL.md:2-2`：

> name: document-bundle-delivery

源文 `src_002` · `SKILL.md:6-6`：

> # 多文档处理与交付

源文 `src_004` · `references/workflow.md:1-1`：

> # 文档流程

源文 `src_009` · `references/workflow.md:13-13`：

> ## 参考步骤

图位置："/entry_block_id"

图位置："/blocks/block_001/block_name"

图位置："/blocks/block_002/block_name"

图位置："/blocks/block_003/block_name"

图位置："/blocks/block_004/block_name"

图位置："/blocks/block_005/block_name"

图位置："/blocks/block_006/block_name"

图位置："/blocks/block_007/block_name"

图位置："/blocks/block_005/instructions/0/constraints/0"

## finding_2 · semantic · represented

原文要求：必须执行 references/workflow.md 中的要求且该文件属于流程；整份流程不得修改输入原文文件；整份流程禁止把文档上传到外部服务；必要时保留原顺序。

当前表示：图级 constraints/0、constraints/1、constraints/2、constraints/3 分别记录上述四项，作用域为整图或图级声明；文本与源文一致。

比较理由：源文要求分别属于流程执行约束、禁止修改、禁止上传和条件性顺序备注；受控回述以声明约束保留，未记录上传或修改输入原文的操作，且 external_resource 类型不被当作网络发送证据。

源文 `src_003` · `SKILL.md:8-8`：

> 必须执行 [流程说明](references/workflow.md) 中的要求；该文件是当前流程的组成部分。

源文 `src_013` · `references/workflow.md:23-23`：

> 整份流程不得修改输入原文文件。

源文 `src_013` · `references/workflow.md:25-25`：

> 整份流程禁止把文档上传到外部服务。

源文 `src_014` · `references/workflow.md:27-27`：

> 备注：必要时保留原顺序。

图位置："/constraints/0"

图位置："/constraints/1"

图位置："/constraints/2"

图位置："/constraints/3"

## finding_3 · semantic · represented

原文要求：读取用户提供的 manifest.json，并按其中 paths 列表获取文档路径。

当前表示：block_001 的 ir_001 read_manifest_file 以 external_resource manifest.json 为输入，输出 result_001 manifest_content；block_002 的 ir_003 extract_document_paths_from_manifest 以 result_001 和 literal paths 为输入，输出 result_002 document_paths；两块均以 dispatch 终结。

比较理由：manifest 文件身份、paths 键和文档路径结果均有对应操作数与输出语义；用户提供属性由块名和外部资源输入共同承载，未把 external_resource 误解释为网络服务。

源文 `src_005` · `references/workflow.md:3-3`：

> 读取用户提供的 manifest.json，按其中 paths 列表获取文档路径，并从请求中读取 output_dir 和 delivery_path。

图位置："/blocks/block_001/block_id"

图位置："/blocks/block_001/block_name"

图位置："/blocks/block_001/data_source_kind"

图位置："/blocks/block_001/instructions"

图位置："/blocks/block_001/instructions/0"

图位置："/blocks/block_001/instructions/0/inputs/0"

图位置："/blocks/block_001/instructions/0/outputs/0"

图位置："/blocks/block_001/instructions/0/metadata"

图位置："/blocks/block_001/instructions/1"

图位置："/blocks/block_001/instructions/1/metadata"

图位置："/blocks/block_002/block_id"

图位置："/blocks/block_002/block_name"

图位置："/blocks/block_002/data_source_kind"

图位置："/blocks/block_002/instructions"

图位置："/blocks/block_002/instructions/0"

图位置："/blocks/block_002/instructions/0/inputs/0"

图位置："/blocks/block_002/instructions/0/inputs/1"

图位置："/blocks/block_002/instructions/0/outputs/0"

图位置："/blocks/block_002/instructions/0/metadata"

图位置："/blocks/block_002/instructions/1"

图位置："/blocks/block_002/instructions/1/metadata"

## finding_4 · semantic · represented

原文要求：从请求中读取 output_dir 和 delivery_path。

当前表示：contexts 声明 output_dir 与 delivery_path；block_003 的 ir_005 read_output_dir_and_delivery_path_from_request 使用两个 context_key 输入，输出 result_003 request_output_dir 与 result_004 request_delivery_path，随后 dispatch。

比较理由：两个请求键的身份、来源语义和两个独立结果均保留；受控文本也明确声明 context 声明本身不是读取操作。

源文 `src_005` · `references/workflow.md:3-3`：

> 读取用户提供的 manifest.json，按其中 paths 列表获取文档路径，并从请求中读取 output_dir 和 delivery_path。

图位置："/declared_context_keys"

图位置："/blocks/block_003/block_id"

图位置："/blocks/block_003/block_name"

图位置："/blocks/block_003/data_source_kind"

图位置："/blocks/block_003/instructions"

图位置："/blocks/block_003/instructions/0"

图位置："/blocks/block_003/instructions/0/inputs/0"

图位置："/blocks/block_003/instructions/0/inputs/1"

图位置："/blocks/block_003/instructions/0/outputs/0"

图位置："/blocks/block_003/instructions/0/outputs/1"

图位置："/blocks/block_003/instructions/0/metadata"

图位置："/blocks/block_003/instructions/1"

图位置："/blocks/block_003/instructions/1/metadata"

## finding_5 · semantic · represented

原文要求：转换阶段逐个执行 python scripts/convert.py <文档路径> <output_dir>，把每次标准输出作为对应的转换产物路径。

当前表示：block_004 的 ir_007 run_convert_script_for_each_document 以 scripts/convert.py、result_002 document_paths、result_003 request_output_dir 为输入，输出 result_005 converted_artifact_paths；块名和 opcode 表示逐文档执行，metadata command 记录脚本与参数，metadata script_content 中的 print(output) 及后续约束“只使用脚本输出路径”支持脚本输出路径来源；ir_008 dispatch 终结。

比较理由：逐文档次数、脚本对象、文档路径集合、output_dir 和转换产物路径结果均有图内事实；result_005 作为聚合列表承载本次流程后续需要的转换产物路径，未把脚本内部处理展开为主流程步骤。

源文 `src_006` · `references/workflow.md:6-6`：

> 逐个执行 python scripts/convert.py <文档路径> <output_dir>，把每次标准输出作为对应的转换产物路径。

图位置："/blocks/block_004/block_id"

图位置："/blocks/block_004/block_name"

图位置："/blocks/block_004/data_source_kind"

图位置："/blocks/block_004/instructions"

图位置："/blocks/block_004/instructions/0"

图位置："/blocks/block_004/instructions/0/inputs/0"

图位置："/blocks/block_004/instructions/0/inputs/1"

图位置："/blocks/block_004/instructions/0/inputs/2"

图位置："/blocks/block_004/instructions/0/outputs/0"

图位置："/blocks/block_004/instructions/0/metadata"

图位置："/blocks/block_004/instructions/1"

图位置："/blocks/block_004/instructions/1/metadata"

## finding_6 · semantic · represented

原文要求：转换期间保留原文标题，且该要求仅限转换、不限制汇总标题；转换通过 scripts/convert.py 完成，主流程只使用脚本输出路径，不重复执行脚本内部处理。

当前表示：block_004 操作级 constraints/0 与 constraints/1 记录这两项要求；constraints/0 保留“仅限转换，不限制汇总标题”的作用域，constraints/1 保留脚本完成转换和主流程不重复内部处理的约束。

比较理由：标题保留的作用域、脚本使用边界和不重复内部处理的要求均以操作级声明保留；声明不表示已实现，但源文该项本身也是约束性要求。

源文 `src_006` · `references/workflow.md:7-7`：

> 转换期间保留原文标题；该要求仅限转换，不限制汇总标题。

源文 `src_007` · `references/workflow.md:9-9`：

> 转换通过 scripts/convert.py 完成；主流程只使用脚本输出路径，不重复执行脚本内部的处理。

图位置："/blocks/block_004/instructions/0/constraints/0"

图位置："/blocks/block_004/instructions/0/constraints/1"

## finding_7 · semantic · represented

原文要求：打包必须采用参考步骤命令 python scripts/package.py --paths <转换产物路径列表> --output bundle.zip，并将转换产物路径列表传给 --paths。

当前表示：block_005 的 ir_009 run_package_script 以 scripts/package.py、result_005 converted_artifact_paths、literal bundle.zip 为输入，输出 result_006 bundle.zip；操作级 constraint/0 要求采用参考步骤命令并把路径列表传给 --paths；metadata command 完整记录 --paths 与 --output bundle.zip；ir_010 dispatch 终结。

比较理由：脚本、路径列表到 --paths、bundle.zip 到 --output 以及输出结果均有图、约束或 metadata 依据；未新增其他打包参数或打包对象。

源文 `src_008` · `references/workflow.md:11-11`：

> 打包时必须采用下方“参考步骤”的命令，并将转换产物路径列表传给 --paths。

源文 `src_010` · `references/workflow.md:16-16`：

> python scripts/package.py --paths <转换产物路径列表> --output bundle.zip

图位置："/blocks/block_005/block_id"

图位置："/blocks/block_005/block_name"

图位置："/blocks/block_005/data_source_kind"

图位置："/blocks/block_005/instructions"

图位置："/blocks/block_005/instructions/0"

图位置："/blocks/block_005/instructions/0/inputs/0"

图位置："/blocks/block_005/instructions/0/inputs/1"

图位置："/blocks/block_005/instructions/0/inputs/2"

图位置："/blocks/block_005/instructions/0/outputs/0"

图位置："/blocks/block_005/instructions/0/constraints/0"

图位置："/blocks/block_005/instructions/0/metadata"

图位置："/blocks/block_005/instructions/1"

图位置："/blocks/block_005/instructions/1/metadata"

## finding_8 · semantic · represented

原文要求：将生成的 bundle.zip 交付到请求的 delivery_path。

当前表示：block_006 的 ir_011 deliver_bundle_to_requested_path 以 result_006 bundle.zip 和 result_004 request_delivery_path 为输入，无输出，随后 ir_012 dispatch。

比较理由：交付对象是打包结果 result_006，目标是请求读取得到的 result_004；动作与两个输入身份均匹配，交付无返回值符合源文未要求返回内容。

源文 `src_011` · `references/workflow.md:19-19`：

> 将生成的 bundle.zip 交付到请求的 delivery_path。

图位置："/blocks/block_006/block_id"

图位置："/blocks/block_006/block_name"

图位置："/blocks/block_006/data_source_kind"

图位置："/blocks/block_006/instructions"

图位置："/blocks/block_006/instructions/0"

图位置："/blocks/block_006/instructions/0/inputs/0"

图位置："/blocks/block_006/instructions/0/inputs/1"

图位置："/blocks/block_006/instructions/0/metadata"

图位置："/blocks/block_006/instructions/1"

图位置："/blocks/block_006/instructions/1/metadata"

## finding_9 · semantic · represented

原文要求：另外，将转换产物路径列表写入本地 receipt.txt。

当前表示：block_007 的 ir_013 write_converted_paths_to_receipt 以 external_resource receipt.txt 和 result_005 converted_artifact_paths 为输入，无输出；块名标明 local；ir_014 return 终结路径。

比较理由：receipt.txt 的本地文件身份、写入内容和无返回值均与源文一致；return 是固定控制终结操作，不表示额外发送或展示内容。

源文 `src_012` · `references/workflow.md:21-21`：

> 另外，将转换产物路径列表写入本地 receipt.txt。

图位置："/blocks/block_007/block_id"

图位置："/blocks/block_007/block_name"

图位置："/blocks/block_007/data_source_kind"

图位置："/blocks/block_007/instructions"

图位置："/blocks/block_007/instructions/0"

图位置："/blocks/block_007/instructions/0/inputs/0"

图位置："/blocks/block_007/instructions/0/inputs/1"

图位置："/blocks/block_007/instructions/0/metadata"

图位置："/blocks/block_007/instructions/1"

图位置："/blocks/block_007/instructions/1/metadata"

## finding_10 · semantic · represented

原文要求：结果在不同步骤间按实际身份传递：manifest 内容用于提取文档路径；文档路径与 output_dir 用于转换；转换产物路径列表用于打包和 receipt；bundle.zip 与 delivery_path 用于交付。

当前表示：links 记录 result_001 到 path extraction，result_002 与 result_003 到 convert，result_005 到 package 与 receipt，result_006 与 result_004 到 delivery。

比较理由：逐条按 identifier 定位，未按 semantic_name 合并；未发现错绑、漏绑或多绑。result_005 同时用于打包和 receipt，符合源文转换产物路径列表的两个用途。

源文 `src_005` · `references/workflow.md:3-3`：

> 读取用户提供的 manifest.json，按其中 paths 列表获取文档路径，并从请求中读取 output_dir 和 delivery_path。

源文 `src_006` · `references/workflow.md:6-6`：

> 逐个执行 python scripts/convert.py <文档路径> <output_dir>，把每次标准输出作为对应的转换产物路径。

源文 `src_008` · `references/workflow.md:11-11`：

> 打包时必须采用下方“参考步骤”的命令，并将转换产物路径列表传给 --paths。

源文 `src_011` · `references/workflow.md:19-19`：

> 将生成的 bundle.zip 交付到请求的 delivery_path。

源文 `src_012` · `references/workflow.md:21-21`：

> 另外，将转换产物路径列表写入本地 receipt.txt。

图位置："/blocks/block_002/instructions/0/inputs/0"

图位置："/blocks/block_004/instructions/0/inputs/1"

图位置："/blocks/block_004/instructions/0/inputs/2"

图位置："/blocks/block_005/instructions/0/inputs/1"

图位置："/blocks/block_006/instructions/0/inputs/0"

图位置："/blocks/block_006/instructions/0/inputs/1"

图位置："/blocks/block_007/instructions/0/inputs/1"

## finding_11 · semantic · represented

原文要求：源文按读取 manifest/paths、读取请求路径、转换、打包、交付、写 receipt 的顺序叙述；必要时保留原顺序。

当前表示：edges/0 至 edges/5 将 block_001→block_002→block_003→block_004→block_005→block_006→block_007 顺序连接，条件未记录；最终 return 终止。

比较理由：控制边顺序与源文列出的阶段顺序一致；源文没有需要分支条件的例外，“必要时保留原顺序”已在图级约束中记录。dispatch/return 是固定控制终结，不新增业务动作。

源文 `src_005` · `references/workflow.md:3-3`：

> 读取用户提供的 manifest.json，按其中 paths 列表获取文档路径，并从请求中读取 output_dir 和 delivery_path。

源文 `src_006` · `references/workflow.md:6-6`：

> 逐个执行 python scripts/convert.py <文档路径> <output_dir>，把每次标准输出作为对应的转换产物路径。

源文 `src_008` · `references/workflow.md:11-11`：

> 打包时必须采用下方“参考步骤”的命令，并将转换产物路径列表传给 --paths。

源文 `src_011` · `references/workflow.md:19-19`：

> 将生成的 bundle.zip 交付到请求的 delivery_path。

源文 `src_012` · `references/workflow.md:21-21`：

> 另外，将转换产物路径列表写入本地 receipt.txt。

源文 `src_014` · `references/workflow.md:27-27`：

> 备注：必要时保留原顺序。

图位置："/edges/0"

图位置："/edges/1"

图位置："/edges/2"

图位置："/edges/3"

图位置："/edges/4"

图位置："/edges/5"

## finding_12 · semantic · represented

原文要求：scripts/convert.py 定义逐文档 UTF-8 文本转换，创建 output_dir、写入目标 txt 并打印输出路径。

当前表示：block_004 ir_007 的 metadata_json 完整嵌入 convert 脚本的 command、script_content 和 script_path；内部行为未展开为主流程操作。

比较理由：源脚本内容可在 embedded_content 中核对，包含创建 output_dir 与 print(output) 等行为；主流程不重复执行内部处理的约束另见 finding_6。

源文 `src_015` · `scripts/convert.py:1-1`：

> """Convert one UTF-8 text document and print the output path."""

源文 `src_016` · `scripts/convert.py:7-7`：

> output_dir.mkdir(parents=True, exist_ok=True)

源文 `src_016` · `scripts/convert.py:10-10`：

> print(output)

图位置："/blocks/block_004/instructions/0/metadata"

## finding_13 · semantic · represented

原文要求：scripts/package.py 定义通过 --paths 和 --output 构建 ZIP，并逐个 archive.write。

当前表示：block_005 ir_009 的 metadata_json 完整嵌入 package 脚本的 command、script_content 和 script_path；内部行为未展开为主流程操作。

比较理由：源脚本内容可在 embedded_content 中核对，包含 --paths、--output 与 archive.write 等行为；打包命令要求另见 finding_7。

源文 `src_017` · `scripts/package.py:1-1`：

> """Build the explicitly requested ZIP from supplied output paths."""

源文 `src_018` · `scripts/package.py:7-7`：

> parser.add_argument("--paths", nargs="+", required=True)

源文 `src_018` · `scripts/package.py:13-13`：

> archive.write(path, arcname=path.name)

图位置："/blocks/block_005/instructions/0/metadata"

## 安全标注未决

- {"instruction_id": "ir_011", "field": "effects", "reason": "无法确定交付动作是否通过复制读取 bundle.zip 内容而包含 fs_read，还是仅写入或移动目标路径；未据此添加 fs_read。"}

## 助手事后复核

此部分独立于模型核对记录，未经人工确认，不追溯修改模型判定。

尚无已保存的助手逐例复核。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
