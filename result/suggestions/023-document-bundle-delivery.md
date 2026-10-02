# 023-document-bundle-delivery · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：D05；运行：full-pipeline-v4-20260918-rerun-failed；选图轮次：1
- 执行来源：本次重新执行；父运行：`full-pipeline-v4-20260918`；实际执行运行：`full-pipeline-v4-20260918-rerun-failed`
- 反馈停止：audit_passed；原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。
- 安全标注：complete；原因：标注记录完整；结构、操作覆盖与证据定位校验通过。
- 图 SHA-256：2df124accc140ea99d8d8820e6c13d3eccc70f715b31937e9ba852afe134a4bb；源文 SHA-256：98fbb0b1d1685da75f5d5cef1eae3cd59747d0613d142c459f9fab65b26efa9a

未填写保守说明不代表精确保留；覆盖记录不证明语义完整。

反馈完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/023/feedback/result.json>)；本地审查页也可展开全文。

安全标注完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/023/annotation/result.json>)；本地审查页也可展开全文。

## finding_context_metadata · context · represented

原文要求：源文前置元数据和标题为背景信息：name 为 document-bundle-delivery，description 为转换清单中的文档、打包转换产物并交付到用户指定位置，标题为“多文档处理与交付”；它们不是可执行流程要求。

当前表示：受控回述以声明入口块和块图记录流程，没有重复记录 Skill 名称、description 或标题；这些内容作为上下文不改变业务步骤。

比较理由：按 REVIEW-MODALITY 与 context 规则，名称、描述、标题属于背景而非业务动作；受控回述的入口和图记录足以承载流程上下文。

源文 `src_001` · `SKILL.md:2-2`：

> name: document-bundle-delivery

源文 `src_002` · `SKILL.md:6-6`：

> # 多文档处理与交付

图位置："/entry_block_id"

## finding_graph_constraints · semantic · represented

原文要求：第8项要求整份流程不得修改输入原文文件；第9项禁止把文档上传到外部服务；第10项备注必要时保留原顺序。

当前表示：fact:/constraints/0、fact:/constraints/1、fact:/constraints/2 分别记录三条图级声明约束，文字与源文对应，作用域标为图级/整份流程。

比较理由：三条约束的文字、禁止或条件模态和整份流程作用域均保留；备注未被扩成无条件动作，也未发现新增业务行为。

源文 `src_003` · `SKILL.md:15-15`：

> 8. 整份流程不得修改输入原文文件。

源文 `src_003` · `SKILL.md:16-16`：

> 9. 整份流程禁止把文档上传到外部服务。

源文 `src_003` · `SKILL.md:17-17`：

> 10. 备注：必要时保留原顺序。

图位置："/constraints/0"

图位置："/constraints/1"

图位置："/constraints/2"

## finding_read_manifest · semantic · represented

原文要求：第1项要求读取用户提供的 manifest.json。

当前表示：block_001 记录 ir_001 read_manifest_file，以 external_resource manifest.json 为输入，输出 result_001 manifest_content；ir_002 dispatch 结束该块。

比较理由：实际读取动作和对象 manifest.json 已记录；用户提供以外部资源和块名标签承载，名称标签不补造额外步骤。

源文 `src_003` · `SKILL.md:8-8`：

> 读取用户提供的 manifest.json

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

## finding_extract_paths · semantic · represented

原文要求：第1项要求按 manifest 中的 paths 列表获取文档路径。

当前表示：block_002 ir_003 extract_document_paths_from_manifest 输入 result_001 与 literal "paths"，输出 result_002 document_paths；link 将 result_001 绑定到 block_001 的输出定义。

比较理由：读取 manifest 后以其 paths 列表提取文档路径的动作、输入来源、字面量键名和输出标识均被记录。

源文 `src_003` · `SKILL.md:8-8`：

> 按其中 paths 列表获取文档路径

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

## finding_request_settings_contexts · semantic · represented

原文要求：第1项要求从请求中读取 output_dir 和 delivery_path。

当前表示：fact:/entry 声明入口；fact:/contexts 声明 output_dir、delivery_path 为上下文键且不是读取操作；block_003 ir_005 read_request_delivery_settings 以两个 context_key 为输入，输出 result_003 request_output_dir 与 result_004 request_delivery_path。

比较理由：两个请求上下文键的声明、实际读取动作、输入和输出身份均被记录；声明与读取操作分开。

源文 `src_003` · `SKILL.md:8-8`：

> 并从请求中读取 output_dir 和 delivery_path。

图位置："/entry_block_id"

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

## finding_convert_flow · semantic · represented

原文要求：第2项要求逐个执行 python scripts/convert.py <文档路径> <output_dir>，并把每次标准输出作为对应转换产物路径；第3项要求转换期间保留原文标题且仅限转换；第4项要求通过 scripts/convert.py 完成且主流程不重复脚本内部处理；第10项要求必要时保留原顺序。

当前表示：block_004 ir_007 convert_documents_one_by_one_with_convert_script 输入 scripts/convert.py、result_002 document_paths、result_003 request_output_dir，输出 result_005 conversion_artifact_paths；约束0记录 python 调用，约束1记录按输入顺序逐个调用并把每次 stdout 绑定到对应转换产物路径，约束2记录标题保留及仅限转换，约束3记录脚本完成和不重复内部处理；图级约束2记录保留原顺序。links 绑定 result_002、result_003。

比较理由：逐个执行、脚本参数、stdout 到对应产物的绑定、标题保留作用域、脚本黑盒边界和顺序条件均有独立记录，未发现对象、次数或次序错转。

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

图位置："/blocks/block_004/instructions/1"

图位置："/blocks/block_004/instructions/1/metadata"

## finding_convert_script · semantic · represented

原文要求：scripts/convert.py 的嵌入内容应被完整保留：读取 argv[1] 文档和 argv[2] 输出目录，创建输出目录，写出 source.stem + .txt，并打印输出路径。

当前表示：fact:/blocks/3/instructions/0/metadata_json 的 script_content 与 scripts/convert.py 原文一致，invocation_template 为 python scripts/convert.py <文档路径> <output_dir>。

比较理由：嵌入脚本内容逐项覆盖源文件中的参数读取、输出目录创建、输出文件名和打印行为；按 IR-OPAQUE，metadata 保留不等于主流程重复展开内部处理。

源文 `src_006` · `scripts/convert.py:2-2`：

> from pathlib import Path

源文 `src_006` · `scripts/convert.py:3-3`：

> import sys

源文 `src_007` · `scripts/convert.py:5-5`：

> source = Path(sys.argv[1])

源文 `src_007` · `scripts/convert.py:8-8`：

> output = output_dir / (source.stem + ".txt")

源文 `src_007` · `scripts/convert.py:10-10`：

> print(output)

图位置："/blocks/block_004/instructions/0/metadata"

## finding_package_command · semantic · represented

原文要求：第5项要求打包时必须采用参考步骤命令，并将转换产物路径列表传给 --paths。

当前表示：block_005 ir_009 package_conversion_artifacts_with_package_script 输入 scripts/package.py、result_005 conversion_artifact_paths 和 literal "bundle.zip"；操作级约束0-1记录必须采用参考步骤命令及完整命令 python scripts/package.py --paths <转换产物路径列表> --output bundle.zip；metadata reference_step_command 同命令。

比较理由：参考步骤命令、--paths 传递、--output bundle.zip 和脚本资源均被记录；操作输入与约束共同覆盖命令绑定，未发现遗漏。

源文 `src_003` · `SKILL.md:12-12`：

> 5. 打包时必须采用下方“参考步骤”的命令，并将转换产物路径列表传给 --paths。

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

图位置："/blocks/block_005/instructions/0/constraints/0"

图位置："/blocks/block_005/instructions/0/constraints/1"

图位置："/blocks/block_005/instructions/0/metadata"

图位置："/blocks/block_005/instructions/1"

图位置："/blocks/block_005/instructions/1/metadata"

## finding_package_script · semantic · represented

原文要求：scripts/package.py 的嵌入内容应被完整保留：解析 --paths 与 --output，按每个路径写 ZIP，arcname 为文件名。

当前表示：fact:/blocks/4/instructions/0/metadata_json 的 script_content 与 scripts/package.py 原文一致，reference_step_command 为 python scripts/package.py --paths <转换产物路径列表> --output bundle.zip。

比较理由：嵌入脚本内容覆盖参数声明、路径迭代和写入 ZIP 的行为；没有把脚本内部步骤改写成主流程业务步骤。

源文 `src_008` · `scripts/package.py:2-2`：

> import argparse

源文 `src_009` · `scripts/package.py:7-7`：

> parser.add_argument("--paths", nargs="+", required=True)

源文 `src_009` · `scripts/package.py:8-8`：

> parser.add_argument("--output", required=True)

源文 `src_009` · `scripts/package.py:13-13`：

>         archive.write(path, arcname=path.name)

图位置："/blocks/block_005/instructions/0/metadata"

## finding_bundle_delivery · semantic · represented

原文要求：第5-6项要求打包命令以 --output bundle.zip 生成 bundle.zip，并把生成的 bundle.zip 交付到请求的 delivery_path。

当前表示：block_004 ir_009 的约束1记录 --output bundle.zip，inputs/2 记录 literal "bundle.zip"；edge/3 连接 block_004→block_005；block_006 ir_011 输入 external_resource bundle.zip 和 result_004 request_delivery_path，link 将 result_004 绑定到 block_003 输出。

比较理由：bundle.zip 按本地文件资源记录；按 IR-RESOURCE，external_resource 不等于远端或网络上传。生成路径由打包命令约束和 literal 记录，生成到交付的顺序由 edge/3 保持，交付目标由 result_004 绑定；未发现遗漏或错转。

源文 `src_003` · `SKILL.md:12-12`：

> 5. 打包时必须采用下方“参考步骤”的命令，并将转换产物路径列表传给 --paths。

源文 `src_003` · `SKILL.md:13-13`：

> 6. 将生成的 bundle.zip 交付到请求的 delivery_path。

图位置："/blocks/block_005/instructions/0"

图位置："/blocks/block_005/instructions/0/inputs/2"

图位置："/blocks/block_005/instructions/0/constraints/1"

图位置："/edges/3"

图位置："/blocks/block_006/block_id"

图位置："/blocks/block_006/block_name"

图位置："/blocks/block_006/data_source_kind"

图位置："/blocks/block_006/instructions"

图位置："/blocks/block_006/instructions/0"

图位置："/blocks/block_006/instructions/0/inputs/0"

图位置："/blocks/block_006/instructions/0/inputs/1"

图位置："/blocks/block_006/instructions/0/metadata"

## finding_control_order · semantic · represented

原文要求：源文第1-6项按编号给出执行顺序：读取 manifest 与请求设置、转换、打包、交付。

当前表示：fact:/edges/0 至 fact:/edges/4 依次连接 block_001 到 block_006；各块以 dispatch 结束，block_006 以 return 结束，dispatch/return 的 inputs 为空。

比较理由：控制边保留源文步骤先后；dispatch 和 return 是固定控制终结操作，不因源文未写这些 IR 术语而视为新增。源文无显式分支条件，未记录条件不等于恒真，return 无返回值也不表示缺少展示。

源文 `src_003` · `SKILL.md:8-13`：

> 1. 读取用户提供的 manifest.json，按其中 paths 列表获取文档路径，并从请求中读取 output_dir 和 delivery_path。
> 2. 逐个执行 python scripts/convert.py <文档路径> <output_dir>，把每次标准输出作为对应的转换产物路径。
> 3. 转换期间保留原文标题；该要求仅限转换，不限制汇总标题。
> 4. 转换通过 scripts/convert.py 完成；主流程只使用脚本输出路径，不重复执行脚本内部的处理。
> 5. 打包时必须采用下方“参考步骤”的命令，并将转换产物路径列表传给 --paths。
> 6. 将生成的 bundle.zip 交付到请求的 delivery_path。

图位置："/edges/0"

图位置："/edges/1"

图位置："/edges/2"

图位置："/edges/3"

图位置："/edges/4"

图位置："/blocks/block_001/instructions/1"

图位置："/blocks/block_001/instructions/1/metadata"

图位置："/blocks/block_002/instructions/1"

图位置："/blocks/block_002/instructions/1/metadata"

图位置："/blocks/block_003/instructions/1"

图位置："/blocks/block_003/instructions/1/metadata"

图位置："/blocks/block_004/instructions/1"

图位置："/blocks/block_004/instructions/1/metadata"

图位置："/blocks/block_005/instructions/1"

图位置："/blocks/block_005/instructions/1/metadata"

图位置："/blocks/block_006/instructions/1"

图位置："/blocks/block_006/instructions/1/metadata"

## finding_history_receipt · semantic · represented

原文要求：第7项说明历史示例当前流程不执行：另外，将转换产物路径列表写入本地 receipt.txt。

当前表示：受控回述块0-5的完整操作ID清单与操作列表均未记录 receipt.txt 写入操作或相关结果。

比较理由：源文本身将 receipt.txt 标为历史示例且当前不执行，受控不执行该动作是保留而非遗漏；没有为历史示例新增步骤。

源文 `src_003` · `SKILL.md:14-14`：

> 7. 历史示例（当前流程不执行）：另外，将转换产物路径列表写入本地 receipt.txt。

图位置："/blocks/block_001/instructions"

图位置："/blocks/block_002/instructions"

图位置："/blocks/block_003/instructions"

图位置："/blocks/block_004/instructions"

图位置："/blocks/block_005/instructions"

图位置："/blocks/block_006/instructions"

## 助手事后复核

此部分独立于模型核对记录，未经人工确认，不追溯修改模型判定。

### 修复轮次 0 · 历史轮次，不能作为当前图结论

图 SHA-256：353a50e4da4d20735bcbc4d4e13f83abfdaf96f357c89ac1404f24c9aca2244b

助手复核初轮定向反馈，paths 字段和逐次 stdout 绑定的明确化有实际定位；同时建议加入无条件保序的部分强于原文备注，需与修复效果分开记录，非人工确认。

- r0 finding_4 针对 manifest_content 到 paths 的绑定，r0 finding_6 针对逐个执行与 stdout 对应关系；两者都给出实际操作定位，r1 将 literal paths 与逐项调用约束补入，没有新增 receipt 写入或重复脚本内部处理。
- r0 finding_6 的建议额外写‘且保持输入顺序’，而原文仅写‘逐个执行’及‘必要时保留原顺序’。r1 采用了‘按输入顺序分别调用’；这是潜在的约束强化，不能把反馈建议本身当作新的源文要求。

### 修复轮次 1 · 当前所选图

图 SHA-256：2df124accc140ea99d8d8820e6c13d3eccc70f715b31937e9ba852afe134a4bb

助手已复核完整三文件源包、全部核对项、最终 12 个 IR 及其安全标注，并查看实际 PNG 全图和细节。历史 receipt 未被误转为当前动作；关键流程保留，但发现核对理由中的错误块/边定位、轻度约束强化与 actor 证据不足，不能将 audit_passed/complete 当作全面正确性证明。非人工确认。

- finding_history_receipt 与完整操作清单一致：最终仅读取清单、提取 paths、读取请求、转换、打包、交付，末尾 ir_012 return；没有 receipt.txt 操作、结果或写入标注。源文第7条‘历史示例（当前流程不执行）’得到保留，没有因通常文档工作流而补回回执。
- finding_extract_paths、finding_convert_flow、finding_package_command 的核心绑定成立：ir_003 使用 literal paths，ir_007 读取 result_002/003 并产出 result_005；逐个脚本调用和每次 stdout 对应产物路径保留在操作名及约束，转换标题限制只挂 ir_007；打包接收同一 result_005 并保留 --paths/--output bundle.zip。两份脚本全文在 metadata 中保留，没有在主流程重复展开内部步骤。
- finding_convert_flow 未指出 ir_007.constraints[1] 将‘必要时保留原顺序’强化为‘按输入顺序分别调用’；图级仍有原条件说明，但局部声明是无条件的。这不丢失转换/交付关键过程，却是反馈引入局部更强限制后再次被 represented 接受的实际例子，应保留而非宣称毫无差异。
- finding_bundle_delivery 的结论有实际图支持，但解释与证据局部错位：ir_009 实在 block_005，模型文字写 block_004；打包到交付是 /edges/4（block_005→block_006），该项却引用 /edges/3 并称它保证生成到交付。完整图和 finding_control_order 包含正确边，因此这属于核对理由/证据使用错误，不是图缺交付边。合法 fact ID 不等于该事实能支持所写推断。
- 最终打包 ir_009.outputs 为空，交付 ir_011 以 external_resource bundle.zip 指代先前写出的本地文件；这不是远程来源，也不是新增网络上传。与 r0 的 result 链不同，后续传播需通过实际文件写入/读取位置建立 bundle.zip 的存储依赖，不能把同名 external_resource 当全新无来源数据或冒称已有 result 定义链接。
- 12 条 profile 一一覆盖实际 IR。转换 ir_007 与打包 ir_009 的 source/sink/transformer、fs_read/fs_write/transform 均有 read_text/write_text/archive.write 依据；只有转换明确 print(output)，其 model_observe 同时引用脚本和 EM02，正确地没有据此补 actor=llm。这里进入模型的证据对象是输出路径，不能扩成整个输入文档或 ZIP 内容。没有凭资源类型推断网络，也没有把禁止上传转成实际净化。
- 5 个 dispatch 的 actor=llm 都只援引 EM03‘LLM 调度不等于内容可见’；该规则限制观察推断，并未规定每个 dispatch 必由 LLM 执行，因此主体证据不足。相对地 read/extract/context/deliver 均被推为 agent_runtime，也缺少统一的具体执行实现约定；这类不确定性在本例 unresolved=[] 中未呈现。纯 dispatch/return 没有被硬贴数据 effect，这一点合理。
- ir_011 的 fs_write 来自‘交付到 delivery_path’这一可行本地解释，源文没有进一步指定传送机制；不能据标签反推上传、面向用户正文输出或文档被模型观察。全局禁止修改原文与禁止外部上传只是声明；脚本写入成功及输出路径不覆盖输入未经证明。
- 已查看 1260×4646 PNG 全图与标题、转换、打包/交付原分辨率细节：023/D05/r1、中文约束、12IR、6块、5边、末尾 return 均可见，长操作名完整换行且无裁切，箭头与 null 条件框未遮挡。PNG SHA-256=b9c774bc5c93bb51a073b1426a03ec68a9f913b4f6cd7916a997af9fe10b07d2；视觉绑定详见同级 visual-review-023.json。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
