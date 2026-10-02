# 024-document-bundle-delivery · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：D06；运行：full-pipeline-v4-20260918-rerun-failed；选图轮次：2
- 反馈停止：audit_passed；原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。
- 安全标注：complete；原因：标注记录完整；结构、操作覆盖与证据定位校验通过。
- 图 SHA-256：336a0da9c49b0d3dd63a151f4d71959759b1fd4f6ee580772a271ca55545a93e；源文 SHA-256：05f63b466fbf17f6160ce7a2dc53727916cba5e0a9281c95e0fca16e76cb2f43

未填写保守说明不代表精确保留；覆盖记录不证明语义完整。

反馈完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/024/feedback/result.json>)；本地审查页也可展开全文。

安全标注完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/024/annotation/result.json>)；本地审查页也可展开全文。

## finding_1 · context · represented

原文要求：源文 frontmatter 提供技能名 document-bundle-delivery、描述“转换清单中的文档、打包转换产物并交付到用户指定位置”，标题为“多文档处理与交付”；这些是背景/命名信息，不是业务步骤。

当前表示：受控回述以 Skill-IR 图结构记录入口、上下文和块；没有单独的技能名称/描述字段，但流程块名称和记录覆盖了主要业务范围。

比较理由：按统一契约，名称、标题、描述属于 context，不要求成为业务操作或数据绑定；受控记录未用这些背景文字补造业务步骤。

源文 `src_001` · `SKILL.md:2-2`：

> name: document-bundle-delivery

源文 `src_001` · `SKILL.md:3-3`：

> description: 转换清单中的文档、打包转换产物并交付到用户指定位置。

源文 `src_002` · `SKILL.md:6-6`：

> # 多文档处理与交付

图位置："/entry_block_id"

## finding_2 · semantic · represented

原文要求：源文要求：从请求读取 output_dir、delivery_path（第8行）和 archive_path（第13行）；整份流程不得修改输入原文文件，且禁止把文档上传到外部服务（第15-16行）。

当前表示：受控图声明入口块和 contexts（output_dir、delivery_path、archive_path）；图级 constraints/0 禁止修改输入原文文件，constraints/1 禁止把文档上传到外部服务。

比较理由：请求上下文键和两条全局禁止/不得约束逐字保留，作用域为整份流程；未把资源类型推成网络发送或额外参数。

源文 `src_003` · `SKILL.md:8-8`：

> 1. 读取用户提供的 manifest.json，按其中 paths 列表获取文档路径，并从请求中读取 output_dir 和 delivery_path。

源文 `src_003` · `SKILL.md:13-13`：

> 6. 将生成的 bundle.zip 交付到请求的 archive_path。

源文 `src_003` · `SKILL.md:15-15`：

> 8. 整份流程不得修改输入原文文件。

源文 `src_003` · `SKILL.md:16-16`：

> 9. 整份流程禁止把文档上传到外部服务。

图位置："/entry_block_id"

图位置："/declared_context_keys"

图位置："/constraints/0"

图位置："/constraints/1"

## finding_3 · semantic · represented

原文要求：第8行要求读取用户提供的 manifest.json，并按其中 paths 列表获取文档路径；第17行备注必要时保留原顺序。

当前表示：block_001 记录 read_manifest_json，输入 external_resource manifest.json，输出 result_001 manifest_data，然后 dispatch；block_002 记录 extract_document_paths_from_manifest_paths，输入 result_001 和 literal "paths"，输出 result_002 document_paths，并有操作级约束“必要时保留原顺序”，然后 dispatch。链接 fact:/blocks/1/instructions/0/inputs/0:link 确认 result_001 来自 block_001。

比较理由：读取对象、paths 字段、输出文档路径列表和顺序约束均被记录；manifest.json 作为文件资源处理，不推断远端上传。

源文 `src_003` · `SKILL.md:8-8`：

> 1. 读取用户提供的 manifest.json，按其中 paths 列表获取文档路径，并从请求中读取 output_dir 和 delivery_path。

源文 `src_003` · `SKILL.md:17-17`：

> 10. 备注：必要时保留原顺序。

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

图位置："/blocks/block_002/instructions/0/constraints/0"

图位置："/blocks/block_002/instructions/0/metadata"

图位置："/blocks/block_002/instructions/1"

图位置："/blocks/block_002/instructions/1/metadata"

## finding_4 · semantic · represented

原文要求：第8行要求从请求中读取 output_dir 和 delivery_path。

当前表示：block_003 记录 read_output_dir_and_delivery_path_from_request，输入 context_key output_dir 和 delivery_path，输出 result_003 output_dir_value、result_004 delivery_path_value，source 标记为 context，然后 dispatch。

比较理由：动作、两个请求上下文键和输出绑定均对应源文；delivery_path 在源文后续未被使用，回述也未额外使用它。

源文 `src_003` · `SKILL.md:8-8`：

> 1. 读取用户提供的 manifest.json，按其中 paths 列表获取文档路径，并从请求中读取 output_dir 和 delivery_path。

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

原文要求：第9-11行要求逐个执行 python scripts/convert.py <文档路径> <output_dir>，把每次标准输出作为对应转换产物路径；转换期间保留原文标题且仅限转换；转换通过 scripts/convert.py 完成，主流程只使用脚本输出路径，不重复脚本内部处理；第17行备注必要时保留原顺序。

当前表示：block_004 记录 run_convert_script_per_document_and_read_stdout，输入 external_resource scripts/convert.py、result_002 document_paths、result_003 output_dir_value，输出 result_005 converted_artifact_paths_from_stdout；constraints/0-3 分别记录保留原文标题、转换通过 scripts/convert.py 且不重复内部处理、每次 stdout 作为对应产物路径、必要时保留原顺序；metadata_json 嵌入 convert.py 和 stdout_binding。链接 fact:/blocks/3/instructions/0/inputs/1:link 与 fact:/blocks/3/instructions/0/inputs/2:link 确认 result_002/003 来源。

比较理由：逐个转换、脚本对象、文档路径和输出目录绑定、stdout 到产物路径映射、标题与顺序约束均保留；脚本内部处理仅在 metadata 中保留，未作为主流程重复操作。

源文 `src_003` · `SKILL.md:9-9`：

> 2. 逐个执行 python scripts/convert.py <文档路径> <output_dir>，把每次标准输出作为对应的转换产物路径。

源文 `src_003` · `SKILL.md:10-10`：

> 3. 转换期间保留原文标题；该要求仅限转换，不限制汇总标题。

源文 `src_003` · `SKILL.md:11-11`：

> 4. 转换通过 scripts/convert.py 完成；主流程只使用脚本输出路径，不重复执行脚本内部的处理。

源文 `src_003` · `SKILL.md:17-17`：

> 10. 备注：必要时保留原顺序。

图位置："/blocks/block_004/block_id"

图位置："/blocks/block_004/block_name"

图位置："/blocks/block_004/data_source_kind"

图位置："/blocks/block_004/instructions"

图位置："/blocks/block_004/instructions/0"

图位置："/blocks/block_004/instructions/0/inputs/0"

图位置："/blocks/block_004/instructions/0/inputs/1"

图位置："/blocks/block_004/instructions/0/inputs/2"

图位置："/blocks/block_004/instructions/0/outputs/0"

图位置："/blocks/block_004/instructions/0/constraints/0"

图位置："/blocks/block_004/instructions/0/constraints/1"

图位置："/blocks/block_004/instructions/0/constraints/2"

图位置："/blocks/block_004/instructions/0/constraints/3"

图位置："/blocks/block_004/instructions/0/metadata"

图位置："/blocks/block_004/instructions/1"

图位置："/blocks/block_004/instructions/1/metadata"

## finding_6 · semantic · represented

原文要求：第12行要求打包时必须采用参考步骤命令，并将转换产物路径列表传给 --paths；参考步骤代码块给出 python scripts/package.py --paths <转换产物路径列表> --output bundle.zip；第17行备注必要时保留原顺序。

当前表示：block_005 记录 run_package_script，输入 external_resource scripts/package.py、result_005 converted_artifact_paths、literal --paths、--output、bundle.zip；constraints/0-2 记录必须采用参考步骤命令、完整命令、必要时保留原顺序；metadata_json 嵌入 package.py。链接 fact:/blocks/4/instructions/0/inputs/1:link 确认 result_005 来源。

比较理由：打包命令、--paths 绑定、bundle.zip 输出参数和顺序约束均有记录；约束/1 显式保留源文命令顺序，操作记录未引入额外业务参数。

源文 `src_003` · `SKILL.md:12-12`：

> 5. 打包时必须采用下方“参考步骤”的命令，并将转换产物路径列表传给 --paths。

源文 `src_003` · `SKILL.md:17-17`：

> 10. 备注：必要时保留原顺序。

源文 `src_004` · `SKILL.md:19-19`：

> ## 参考步骤

源文 `src_005` · `SKILL.md:22-22`：

> python scripts/package.py --paths <转换产物路径列表> --output bundle.zip

图位置："/blocks/block_005/block_id"

图位置："/blocks/block_005/block_name"

图位置："/blocks/block_005/data_source_kind"

图位置："/blocks/block_005/instructions"

图位置："/blocks/block_005/instructions/0"

图位置："/blocks/block_005/instructions/0/inputs/0"

图位置："/blocks/block_005/instructions/0/inputs/1"

图位置："/blocks/block_005/instructions/0/inputs/2"

图位置："/blocks/block_005/instructions/0/inputs/3"

图位置："/blocks/block_005/instructions/0/inputs/4"

图位置："/blocks/block_005/instructions/0/constraints/0"

图位置："/blocks/block_005/instructions/0/constraints/1"

图位置："/blocks/block_005/instructions/0/constraints/2"

图位置："/blocks/block_005/instructions/0/metadata"

图位置："/blocks/block_005/instructions/1"

图位置："/blocks/block_005/instructions/1/metadata"

## finding_7 · semantic · represented

原文要求：第13行要求将生成的 bundle.zip 交付到请求的 archive_path。

当前表示：block_006 记录 read_archive_path_from_request，输入 context_key archive_path，输出 result_006 archive_path_value；block_007 记录 deliver_bundle_zip_to_archive_path，输入 external_resource bundle.zip 和 result_006。链接 fact:/blocks/6/instructions/0/inputs/1:link 确认 result_006 来源。

比较理由：读取请求中的 archive_path 是“请求的 archive_path”的数据绑定；bundle.zip 与打包操作的输出参数同名，交付顺序在打包之后，符合生成后交付。

源文 `src_003` · `SKILL.md:13-13`：

> 6. 将生成的 bundle.zip 交付到请求的 archive_path。

图位置："/blocks/block_006/block_id"

图位置："/blocks/block_006/block_name"

图位置："/blocks/block_006/data_source_kind"

图位置："/blocks/block_006/instructions"

图位置："/blocks/block_006/instructions/0"

图位置："/blocks/block_006/instructions/0/inputs/0"

图位置："/blocks/block_006/instructions/0/outputs/0"

图位置："/blocks/block_006/instructions/0/metadata"

图位置："/blocks/block_006/instructions/1"

图位置："/blocks/block_006/instructions/1/metadata"

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

## finding_8 · semantic · represented

原文要求：第14行要求另外将转换产物路径列表写入本地 receipt.txt；第17行备注必要时保留原顺序。

当前表示：block_008 记录 write_converted_paths_to_receipt，输入 result_005 converted_artifact_paths 和 external_resource receipt.txt，并有操作级约束“必要时保留原顺序”；随后 return 结束路径。链接 fact:/blocks/7/instructions/0/inputs/0:link 确认 result_005 来源。

比较理由：写入对象、数据来源、本地文件标识和顺序约束均保留；receipt.txt 作为本地文件资源记录，不推断网络发送。

源文 `src_003` · `SKILL.md:14-14`：

> 7. 另外，将转换产物路径列表写入本地 receipt.txt。

源文 `src_003` · `SKILL.md:17-17`：

> 10. 备注：必要时保留原顺序。

图位置："/blocks/block_008/block_id"

图位置："/blocks/block_008/block_name"

图位置："/blocks/block_008/data_source_kind"

图位置："/blocks/block_008/instructions"

图位置："/blocks/block_008/instructions/0"

图位置："/blocks/block_008/instructions/0/inputs/0"

图位置："/blocks/block_008/instructions/0/inputs/1"

图位置："/blocks/block_008/instructions/0/constraints/0"

图位置："/blocks/block_008/instructions/0/metadata"

图位置："/blocks/block_008/instructions/1"

图位置："/blocks/block_008/instructions/1/metadata"

## finding_9 · semantic · represented

原文要求：源文步骤顺序：读取清单并提取路径、读取 output_dir/delivery_path、逐个转换、打包、交付到 archive_path、写入 receipt；源文未给出分支条件。

当前表示：edges/0-6 依次连接 block_001→block_002→block_003→block_004→block_005→block_006→block_007→block_008；各块内 dispatch 控制终结到后继，block_008 内 return 结束。

比较理由：控制边顺序与源文编号步骤一致；所有边条件未记录，源文也未给出条件；dispatch/return 为固定控制操作，不新增业务步骤。

源文 `src_003` · `SKILL.md:8-8`：

> 1. 读取用户提供的 manifest.json，按其中 paths 列表获取文档路径，并从请求中读取 output_dir 和 delivery_path。

源文 `src_003` · `SKILL.md:14-14`：

> 7. 另外，将转换产物路径列表写入本地 receipt.txt。

图位置："/edges/0"

图位置："/edges/1"

图位置："/edges/2"

图位置："/edges/3"

图位置："/edges/4"

图位置："/edges/5"

图位置："/edges/6"

## finding_10 · semantic · represented

原文要求：源文件 scripts/convert.py 和 scripts/package.py 给出转换和打包脚本实现；源 Skill 要求转换/打包通过这两个脚本完成，主流程不重复脚本内部处理。

当前表示：block_004 和 block_005 的 metadata_json 完整嵌入 convert.py 与 package.py 的源码和脚本路径；操作只调用脚本，不展开其内部步骤。

比较理由：按 IR-OPAQUE，嵌入源码不等于内部行为已作为主流程步骤执行；回述保留脚本内容且未把内部处理重复建模，符合源文。

源文 `src_006` · `scripts/convert.py:1-1`：

> """Convert one UTF-8 text document and print the output path."""

源文 `src_007` · `scripts/convert.py:5-5`：

> source = Path(sys.argv[1])

源文 `src_008` · `scripts/package.py:1-1`：

> """Build the explicitly requested ZIP from supplied output paths."""

源文 `src_009` · `scripts/package.py:7-7`：

> parser.add_argument("--paths", nargs="+", required=True)

图位置："/blocks/block_004/instructions/0/metadata"

图位置："/blocks/block_005/instructions/0/metadata"

## 助手事后复核

此部分独立于模型核对记录，未经人工确认，不追溯修改模型判定。

尚无已保存的助手逐例复核。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
