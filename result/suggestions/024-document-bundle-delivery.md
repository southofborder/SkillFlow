# 024-document-bundle-delivery · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：D06；运行：full-pipeline-v4-20260918-rerun-failed；选图轮次：2
- 执行来源：本次重新执行；父运行：`full-pipeline-v4-20260918`；实际执行运行：`full-pipeline-v4-20260918-rerun-failed`
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

### 修复轮次 0 · 历史轮次，不能作为当前图结论

图 SHA-256：0849131f764f741befc57395be60b21c1bb81d3e1b0155befbc7c157f7457bde

助手复核初轮差异与未决项：paths 和打包命令参数说明不够显式，保序备注的作用域确有解释空间；archive_path 交付目标已经保留。非人工确认。

- r0 finding_5/7 分别要求补 manifest.paths 与完整参考命令/--output bundle.zip 绑定；原图确实只在提取操作中使用 manifest_data，打包只列 bundle.zip 和‘采用下方参考步骤’约束而未记录该命令正文。反馈增加的是原文已有绑定，不是新的业务功能。
- r0 finding_12=unknown 针对‘必要时保留原顺序’只放转换/打包两个块。实际 r0 的两个块确有这条约束，原文备注未明确限定对象；该问题是作用域解释未定，不是完全丢失备注。与明确差异同时存在时继续修复符合既定停止策略，但不能把后续通过自动当成原歧义已经被证实消除。
- r0 交付已通过 archive_path 独立请求读取结果连接，没有误用第一条中读取的 delivery_path；后续完整重提取也应保持这一点。

### 修复轮次 1 · 历史轮次，不能作为当前图结论

图 SHA-256：a25c7074cb0cc6967a762e02034c4ba8995ed880d1c280777e2582fadb8cd6b4

助手复核 r1 的实际新问题：paths 与参考命令已补，但保序备注被整体删去；核对发现了这个回归，同时要求更明确的逐次 stdout 绑定。非人工确认。

- r1 finding_13=omitted 有实际依据：图级、块级及操作级均没有 r0 曾记录的‘必要时保留原顺序’。这不是只检查旧差异就通过，完整复核确实发现重提取造成的新遗漏。
- r1 finding_5 指向 ir_007 聚合输出 result_005 converted_paths：动作名包含 for_each_document，但只保留脚本中的 print(output)，尚未写出该 stdout 与各文档产物结果的对应关系。r2 增加 stdout_binding/correspondence 与操作约束后仍维持单个脚本黑盒抽象。
- r1 finding_13 的建议把模糊备注具体应用到 paths 提取、转换、打包和回执。这是与数据列表有关的合理解释，却仍是对原文作用域的选择；应保留解释身份，不把建议当成源文额外明确给出的范围。

### 修复轮次 2 · 当前所选图

图 SHA-256：336a0da9c49b0d3dd63a151f4d71959759b1fd4f6ee580772a271ca55545a93e

助手已复核完整三文件源包、三轮关键变化、末图全部业务项及 16 条安全标注，并查看实际 PNG 全图与原尺寸细节。archive_path 目标、逐次 stdout、脚本边界和回执均保留；保序作用域仍是解释性选择，部分 actor/transform 标注依据有待收紧。非人工确认。

- r2 finding_4/7 与 actual CFG 一致：ir_005 仍读取原文第1条的 output_dir、delivery_path，result_004 delivery_path_value 保留但未被交付使用；ir_011 另从请求 archive_path 生成 result_006，ir_013 交付使用 result_006。没有为了统一常见工作流把 archive_path 改回 delivery_path；‘请求的 archive_path’足以支持实际上下文读取，不需要虚构额外参数来源。
- r2 finding_3/5/6/8 对应实际绑定：manifest.paths 为显式 literal，转换读取 result_002/003、输出 result_005；metadata 的 stdout_binding 与 correspondence 逐项说明每文档和产物路径关系，约束保留每次 stdout 用作产物路径；打包保留完整 python scripts/package.py --paths ... --output bundle.zip 命令及 flags；receipt 独立写同一 result_005，而非原始路径或 bundle.zip。没有把单次脚本内部读取/写入又展开执行一遍。
- 保序备注目前原文文字‘必要时保留原顺序’分别挂在 ir_003、ir_007、ir_009、ir_015，保留条件模态，没有变成无条件等待/排序动作。这个应用范围与路径列表链条相容，但仍未从源文证明它只限这些操作；r0 的 scope unknown 最终变为模型接受的合理范围选择，不应宣传为歧义得到客观证明消除。
- 标题限制只挂转换 ir_007，未错误限制汇总标题；两条禁止改输入/上传外部服务仍是全局声明。正文脚本完整保留，文件成功写入、输入与输出路径不重合、禁止上传在执行时得到保证均不由声明或核对器通过证明。
- 最终 ir_009.outputs=[]、ir_013 读取 external_resource bundle.zip，原来的 bundle 路径 result 链被文件资源表示取代。源文交付目标与顺序没有因此丢失，但后续传播应根据打包命令写入的实际 bundle.zip 建立文件状态依赖；不能将 external_resource 解释为远端或独立外源，也不能声称现有图已经给出该文件的 result 定义链接。
- 16 个 IR 均恰有四字段 profile。ir_007 的 fs_read/fs_write 来自脚本正文，model_observe 依据明确 stdout 与 EM02，只支持产物路径回传，不支持整文档进入模型。该条没有 transformer/transform，而脚本会计算 source.stem + '.txt' 输出路径并将每次 stdout 汇成路径列表；按本轮计算/组合的固定定义存在变换依据，且与同脚本的021/023标注不一致，属于需检查的漏标或粒度分歧。没有因此认定文本被净化。
- 7个 dispatch 的 actor=llm 理由为‘LLM 可参与调度’，可能性并不能证明本次动作执行者；EM03只限制观察推断。其余 read/extract/context/deliver 的 agent_runtime 标签也多由‘IR未记录工具/模型’反推，未充分区分缺证据与确定本地执行。当前 unresolved=[] 不能证明这些主体推断已确定；纯控制 roles/effects 为空本身合理。
- ir_009 打包的三 roles 与 fs_read/fs_write/transform 有 archive.write/ZipFile 依据；ir_013 archive 交付、ir_015 receipt 写入各自保持 sink/fs_write，未凭工具名或资源类型增加网络；交付具体实现仍是本地落盘解释，不能据此推论网络或用户正文输出。
- 已查看 1260×5838 实际 PNG 全图及标题、转换/打包、archive读取/交付/回执原分辨率细节：024/D06/r2、8块、7边、16IR，中文约束、flags、result标识和末尾return清晰，未见节点裁切或箭头遮挡。PNG SHA-256=e99f149ac01cfdf574865f1ee80121404218f267a76fafcbea1ec1e22fc39083；视觉绑定详见 visual-review-024.json。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
