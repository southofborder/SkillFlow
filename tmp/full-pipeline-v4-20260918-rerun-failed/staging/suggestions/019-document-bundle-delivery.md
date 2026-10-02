# 019-document-bundle-delivery · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：D01；运行：full-pipeline-v4-20260918-rerun-failed；选图轮次：1
- 执行来源：本次重新执行；父运行：`full-pipeline-v4-20260918`；实际执行运行：`full-pipeline-v4-20260918-rerun-failed`
- 反馈停止：audit_passed；原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。
- 安全标注：complete；原因：标注记录完整；结构、操作覆盖与证据定位校验通过。
- 图 SHA-256：795fd2d72a4bd9f13c5eb79fc8c9ef99ed8d8b8437dc48ac38903d39e84e5968；源文 SHA-256：269e7a58c4369571ecc332f6668d6aa2f1f85af4570312feb552bda87e917ed3

未填写保守说明不代表精确保留；覆盖记录不证明语义完整。

反馈完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/019/feedback/result.json>)；本地审查页也可展开全文。

安全标注完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/019/annotation/result.json>)；本地审查页也可展开全文。

## finding_1 · context · represented

原文要求：源文顶部 frontmatter 的名称/描述、一级标题“# 多文档处理与交付”和“## 参考步骤”标题属于背景/标签，不构成可执行业务步骤。

当前表示：受控回述以 fact:/entry 作为入口，以块名称和 metadata/reference_command 组织流程；没有把名称、描述或 Markdown 标题当作额外业务动作。

比较理由：这些内容属于前言、名称和标题等上下文/表示辅助信息，按契约可作为 context 处理，不要求成为独立操作；受控未据此新增业务流程。

源文 `src_001` · `SKILL.md:1-4`：

> ---
> name: document-bundle-delivery
> description: 转换清单中的文档、打包转换产物并交付到用户指定位置。
> ---

源文 `src_002` · `SKILL.md:6-6`：

> # 多文档处理与交付

源文 `src_004` · `SKILL.md:19-19`：

> ## 参考步骤

图位置："/entry_block_id"

图位置："/blocks/block_001/block_name"

图位置："/blocks/block_005/instructions/0/metadata"

## finding_2 · semantic · represented

原文要求：第1步前半：读取用户提供的 manifest.json，并按其中 paths 列表获取文档路径。

当前表示：block_001 ir_001 read_manifest_file 以 external_resource manifest.json 为输入，输出 result_001 manifest_content；block_002 ir_003 extract_document_paths_from_manifest_paths_list 以 result_001 和字面量 "paths" 为输入，输出 result_002 document_paths，并声明约束“按其中 paths 列表获取文档路径。”；link 将 result_001 绑定到该提取输入。

比较理由：读取对象、路径键、提取动作和结果绑定均保留；external_resource 不推断远端或上传。

源文 `src_003` · `SKILL.md:8-8`：

> 1. 读取用户提供的 manifest.json，按其中 paths 列表获取文档路径，并从请求中读取 output_dir 和 delivery_path。

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

## finding_3 · semantic · represented

原文要求：第1步后半：从请求中读取 output_dir 和 delivery_path。

当前表示：fact:/contexts 声明 output_dir 与 delivery_path；block_003 ir_005 read_output_dir_and_delivery_path_from_request 以 context_key output_dir/delivery_path 为输入，输出 result_003 request_output_dir、result_004 request_delivery_path；块 source 标为 context。

比较理由：两个请求变量的读取动作、来源和作用域保留，没有多读其他键。

源文 `src_003` · `SKILL.md:8-8`：

> 并从请求中读取 output_dir 和 delivery_path。

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

## finding_4a · semantic · represented

原文要求：第2步：逐个执行 python scripts/convert.py <文档路径> <output_dir>，把每次标准输出作为对应的转换产物路径。

当前表示：block_004 ir_007 run_convert_script_for_each_document_and_capture_stdout 输入 scripts/convert.py、result_002 document_paths、result_003 request_output_dir，输出 result_005 converted_artifact_paths；约束2记录“把每次标准输出作为对应的转换产物路径。”；metadata command_template 记录 python scripts/convert.py <文档路径> <output_dir>。

比较理由：逐个执行、脚本与两个业务参数、stdout 对应产物路径的语义有记录；per-item 绑定由 opcode 和约束表达，未展开脚本内部处理。

源文 `src_003` · `SKILL.md:9-9`：

> 2. 逐个执行 python scripts/convert.py <文档路径> <output_dir>，把每次标准输出作为对应的转换产物路径。

图位置："/blocks/block_004/block_id"

图位置："/blocks/block_004/block_name"

图位置："/blocks/block_004/data_source_kind"

图位置："/blocks/block_004/instructions"

图位置："/blocks/block_004/instructions/0"

图位置："/blocks/block_004/instructions/0/inputs/0"

图位置："/blocks/block_004/instructions/0/inputs/1"

图位置："/blocks/block_004/instructions/0/inputs/2"

图位置："/blocks/block_004/instructions/0/outputs/0"

图位置："/blocks/block_004/instructions/0/constraints/2"

图位置："/blocks/block_004/instructions/0/metadata"

图位置："/blocks/block_004/instructions/1"

图位置："/blocks/block_004/instructions/1/metadata"

## finding_4b · semantic · represented

原文要求：第3步：转换期间保留原文标题；该要求仅限转换，不限制汇总标题。

当前表示：操作级约束 fact:/blocks/3/instructions/0/constraints/0 逐字记录转换期间保留原文标题，并限定仅转换、不限制汇总标题。

比较理由：要求性质为转换期约束，作用域明确，未扩展到汇总标题。

源文 `src_003` · `SKILL.md:10-10`：

> 3. 转换期间保留原文标题；该要求仅限转换，不限制汇总标题。

图位置："/blocks/block_004/instructions/0/constraints/0"

## finding_4c · semantic · represented

原文要求：第4步：转换通过 scripts/convert.py 完成；主流程只使用脚本输出路径，不重复执行脚本内部的处理。

当前表示：操作级约束 fact:/blocks/3/instructions/0/constraints/1 记录转换通过 scripts/convert.py 完成，主流程只使用脚本输出路径，不重复脚本内部处理。

比较理由：与 metadata 嵌入脚本不矛盾；嵌入源码仅保存内容，未作为主流程额外操作。

源文 `src_003` · `SKILL.md:11-11`：

> 4. 转换通过 scripts/convert.py 完成；主流程只使用脚本输出路径，不重复执行脚本内部的处理。

图位置："/blocks/block_004/instructions/0/constraints/1"

## finding_4d · semantic · represented

原文要求：第10步备注：必要时保留原顺序。

当前表示：受控将“必要时保留原顺序。”分别作为转换、打包、写 receipt 的操作级约束：fact:/blocks/3/instructions/0/constraints/3、fact:/blocks/4/instructions/0/constraints/1、fact:/blocks/6/instructions/0/constraints/0；未记录为图级约束。

比较理由：源文备注未指定操作范围；受控把同一文字挂在会传递路径列表顺序的三个操作上，属于具体化，未新增其他动作或改变次数/终止。

源文 `src_003` · `SKILL.md:17-17`：

> 10. 备注：必要时保留原顺序。

图位置："/blocks/block_004/instructions/0/constraints/3"

图位置："/blocks/block_005/instructions/0/constraints/1"

图位置："/blocks/block_007/instructions/0/constraints/0"

## finding_5 · semantic · represented

原文要求：第5步：打包时必须采用参考步骤命令，并将转换产物路径列表传给 --paths。

当前表示：block_005 ir_009 run_package_script 输入 scripts/package.py、result_005 converted_artifact_paths、字面量 "bundle.zip"，输出 result_006 bundle_zip_path；约束0要求采用参考步骤并将列表传给 --paths；metadata reference_command 记录 python scripts/package.py --paths <转换产物路径列表> --output bundle.zip，script_content 保存 package.py。

比较理由：打包命令、--paths 绑定、bundle.zip 输出与脚本身份均保留；metadata 作为显式接口/嵌入内容，不声称运行成功。

源文 `src_003` · `SKILL.md:12-12`：

> 5. 打包时必须采用下方“参考步骤”的命令，并将转换产物路径列表传给 --paths。

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

图位置："/blocks/block_005/instructions/0/outputs/0"

图位置："/blocks/block_005/instructions/0/constraints/0"

图位置："/blocks/block_005/instructions/0/metadata"

图位置："/blocks/block_005/instructions/1"

图位置："/blocks/block_005/instructions/1/metadata"

## finding_6 · semantic · represented

原文要求：第6步：将生成的 bundle.zip 交付到请求的 delivery_path。

当前表示：block_006 ir_011 deliver_bundle_zip 输入 result_006 bundle_zip_path 与 result_004 request_delivery_path；无输出。

比较理由：交付对象和目的路径按结果身份绑定；没有记录上传外部服务或额外接收者。

源文 `src_003` · `SKILL.md:13-13`：

> 6. 将生成的 bundle.zip 交付到请求的 delivery_path。

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

## finding_7 · semantic · represented

原文要求：第7步：另外，将转换产物路径列表写入本地 receipt.txt。

当前表示：block_007 ir_013 write_receipt_file 输入 result_005 converted_artifact_paths 与 external_resource receipt.txt；无输出；块名称含 local receipt.txt；操作级约束“必要时保留原顺序。”

比较理由：写入对象、数据来源和本地文件身份保留；external_resource 不推断远端。

源文 `src_003` · `SKILL.md:14-14`：

> 7. 另外，将转换产物路径列表写入本地 receipt.txt。

图位置："/blocks/block_007/block_id"

图位置："/blocks/block_007/block_name"

图位置："/blocks/block_007/data_source_kind"

图位置："/blocks/block_007/instructions"

图位置："/blocks/block_007/instructions/0"

图位置："/blocks/block_007/instructions/0/inputs/0"

图位置："/blocks/block_007/instructions/0/inputs/1"

图位置："/blocks/block_007/instructions/0/constraints/0"

图位置："/blocks/block_007/instructions/0/metadata"

图位置："/blocks/block_007/instructions/1"

图位置："/blocks/block_007/instructions/1/metadata"

## finding_8 · semantic · represented

原文要求：第8步整份流程不得修改输入原文文件；第9步整份流程禁止把文档上传到外部服务。

当前表示：fact:/constraints/0 与 fact:/constraints/1 逐字记录这两条图级声明约束。

比较理由：作用域为整份流程，禁止/不得语义保留；受控图中没有显式上传操作，external_resource 标记不等于远端发送。

源文 `src_003` · `SKILL.md:15-15`：

> 8. 整份流程不得修改输入原文文件。

源文 `src_003` · `SKILL.md:16-16`：

> 9. 整份流程禁止把文档上传到外部服务。

图位置："/constraints/0"

图位置："/constraints/1"

## finding_9 · semantic · represented

原文要求：源文以编号步骤1-7要求顺序执行；无分支、失败回退或条件终止。

当前表示：受控以 dispatch/return 固定控制终结操作和 edges/0-5 顺序连接 block_001→block_002→block_003→block_004→block_005→block_006→block_007；各边 condition 未记录；return 无返回值。

比较理由：dispatch/return 是 IR 固定控制，不因源文未写这些术语视为新增；边无条件和顺序与步骤一致。

源文 `src_003` · `SKILL.md:8-8`：

> 1. 读取用户提供的 manifest.json，按其中 paths 列表获取文档路径，并从请求中读取 output_dir 和 delivery_path。

源文 `src_003` · `SKILL.md:9-9`：

> 2. 逐个执行 python scripts/convert.py <文档路径> <output_dir>，把每次标准输出作为对应的转换产物路径。

源文 `src_003` · `SKILL.md:12-12`：

> 5. 打包时必须采用下方“参考步骤”的命令，并将转换产物路径列表传给 --paths。

源文 `src_003` · `SKILL.md:13-13`：

> 6. 将生成的 bundle.zip 交付到请求的 delivery_path。

源文 `src_003` · `SKILL.md:14-14`：

> 7. 另外，将转换产物路径列表写入本地 receipt.txt。

图位置："/edges/0"

图位置："/edges/1"

图位置："/edges/2"

图位置："/edges/3"

图位置："/edges/4"

图位置："/edges/5"

图位置："/blocks/block_001/instructions/1"

图位置："/blocks/block_002/instructions/1"

图位置："/blocks/block_003/instructions/1"

图位置："/blocks/block_004/instructions/1"

图位置："/blocks/block_005/instructions/1"

图位置："/blocks/block_006/instructions/1"

图位置："/blocks/block_007/instructions/1"

## finding_10 · semantic · represented

原文要求：scripts/convert.py 的具体内容（UTF-8 文本转换并 print 输出路径）和 scripts/package.py 的具体内容（用 --paths/--output 构造 ZIP）作为嵌入脚本资源存在；主流程按黑盒方式调用它们。

当前表示：ir_007 metadata script_content 保存 convert.py 源码，包含 docstring、argv 处理、mkdir、.txt 输出、read_text/write_text、print(output)；ir_009 metadata script_content 保存 package.py 源码，包含 argparse --paths nargs+ required、--output required、ZipFile 写入 arcname=path.name。

比较理由：按 IR-OPAQUE，嵌入源码完整保存不等于内部行为被显式建模或执行；但作为嵌入内容和显式接口，源脚本内容有保留。

源文 `src_006` · `scripts/convert.py:1-3`：

> """Convert one UTF-8 text document and print the output path."""
> from pathlib import Path
> import sys

源文 `src_007` · `scripts/convert.py:5-10`：

> source = Path(sys.argv[1])
> output_dir = Path(sys.argv[2])
> output_dir.mkdir(parents=True, exist_ok=True)
> output = output_dir / (source.stem + ".txt")
> output.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
> print(output)

源文 `src_008` · `scripts/package.py:1-4`：

> """Build the explicitly requested ZIP from supplied output paths."""
> import argparse
> from pathlib import Path
> from zipfile import ZipFile

源文 `src_009` · `scripts/package.py:6-13`：

> parser = argparse.ArgumentParser()
> parser.add_argument("--paths", nargs="+", required=True)
> parser.add_argument("--output", required=True)
> args = parser.parse_args()
> with ZipFile(args.output, "w") as archive:
>     for filename in args.paths:
>         path = Path(filename)
>         archive.write(path, arcname=path.name)

图位置："/blocks/block_004/instructions/0/metadata"

图位置："/blocks/block_005/instructions/0/metadata"

## finding_11 · semantic · represented

原文要求：参考步骤代码块要求命令 python scripts/package.py --paths <转换产物路径列表> --output bundle.zip。

当前表示：metadata reference_command 逐字记录 python scripts/package.py --paths <转换产物路径列表> --output bundle.zip；约束0要求采用参考步骤并将列表传给 --paths；ir_009 输入 result_005 和字面量 bundle.zip，输出 result_006。

比较理由：参考步骤标题作为上下文，命令文本与参数绑定保留；未新增其他打包命令。

源文 `src_004` · `SKILL.md:19-19`：

> ## 参考步骤

源文 `src_005` · `SKILL.md:22-22`：

> python scripts/package.py --paths <转换产物路径列表> --output bundle.zip

图位置："/blocks/block_005/instructions/0/constraints/0"

图位置："/blocks/block_005/instructions/0/metadata"

图位置："/blocks/block_005/instructions/0/inputs/1"

图位置："/blocks/block_005/instructions/0/inputs/2"

图位置："/blocks/block_005/instructions/0/outputs/0"

## 助手事后复核

此部分独立于模型核对记录，未经人工确认，不追溯修改模型判定。

### 修复轮次 1 · 当前所选图

图 SHA-256：795fd2d72a4bd9f13c5eb79fc8c9ef99ed8d8b8437dc48ac38903d39e84e5968

paths字段与逐文档stdout绑定已按原文补全，主要流程未见明显漏转；保留顺序的作用域仍有具体化风险。标注complete中仍存在交付fs_write和执行主体/模型观察依据不足，需与同义020区别如实呈现，不能视为安全语义已确认。

- 助手复核冻结 D01 全部可读源文及两个脚本、r0和r1关键核对结果、最终7块/6边/14 IR，以及全部14份profile的52条证据。本次最终 r1/795fd2d7... 与标注摘要一致；6次逻辑调用分别为3次提取、2次核对、1次标注，包含1次语义修复和1次结构修复。核对器通过、标注complete均为模型/工程状态，不是人工确认或正确性证明。
- r0核对指出的paths字段绑定和逐文档stdout对应确有表示依据不足：原图只有从manifest提取document_paths的开放动作、脚本输出路径结果和嵌入print源码，缺少显式paths字段与每次stdout对应关系。r1 ir_003补入literal paths及字段约束，ir_007动作明确capture_stdout并保留“把每次标准输出作为对应的转换产物路径”。这两处修改有原文直接依据，未见额外业务步骤或错误参数。
- r0完全漏掉“必要时保留原顺序”而把范围不明放入提取diagnostics；r1将原话分别挂到转换、打包、receipt操作。文字和条件性已恢复，没有增加排序操作或宣称无条件排序；但为何恰好是三个范围、何时必要仍非源文确定事实。r1 finding_4d 将此当成可接受具体化，存在过度指定作用域的风险；宜保留源文范围未决，不能把修复后核对通过解读为唯一正确的约束范围。
- r1第一次候选只因两个literal操作数携带不允许的semantic_name失败；第二次去除字段后结构通过。该次结构修复解决的是候选Schema问题，不证明paths选择、顺序语义或脚本行为正确，也不是额外语义核对轮次。
- 最终关键数据链保留：manifest result_001→paths result_002；请求output_dir/result_003和delivery_path/result_004；转换输出列表result_005同时送打包和receipt；打包result_006/bundle_zip_path送交付并与result_004组合。打包命令--paths/--output bundle.zip及转换调用模板完整保留；两份metadata脚本与冻结源码逐字相同，主流程没有重复拆执行脚本内部处理。开放逐文档动作聚合记录不等于循环或stdout成功采集已经运行证明。
- 标题保留仅绑定转换；不得改输入和不得上传保持图级声明，没有补造遮蔽、隔离或过滤动作。convert.py没有输出路径与输入路径别名防护，声明保留不能证明实际永不改写输入。r1 finding_3中的“没有多读其他键”也只能理解为图未显式增加键，不表示执行中保证仅读取这两个键，更不能排除后续宽读取传播。
- 明确的标注证据不足：ir_011仅凭deliver_bundle_zip及request_delivery_path就标agent_runtime/fs_write，并称为本地文件操作。源文未限定delivery_path机制，图也未补充本地复制、远端发送或面向用户交付；禁止上传声明不能替代机制证据。同义新020对此保留effects未决更谨慎，本例complete不消除该不确定性；建议把交付机制外置为未决，而非将fs_write当成已确认事实。
- 模型观察存在实现假设不一致：ir_001仅凭read_manifest_file便标runtime/fs_read、不标model_observe；ir_003同样被断定本地提取，而新020同义动作分别推断tool回传和LLM处理。原文没有给本地隔离或执行者，因此不能把019的缺失model_observe当成manifest不会进入模型。六个dispatch仅引用EM03片段“LLM调度”来确定actor=llm，EM03原意是调度不足以证明观察，并未规定所有dispatch由LLM执行。
- ir_007的fs_read/fs_write有具体脚本调用依据，model_observe明确依据EM02且理由只覆盖stdout输出路径；不得扩张成源文档全文必然被模型观察。其actor把tool/runtime/llm一并列出时，EM02支持内容进入LLM，不单独证明LLM执行转换脚本。该动作未标transform/transformer，而同义020有标注，属于复合动作粒度需统一的边界，不能只按convert名称认定正文已被改变。
- ir_009读取产物并生成ZIP支持source/sink/transformer与fs_read/fs_write/transform；源码ZipFile默认未请求压缩，证据理由中“压缩”不宜视为已确认算法行为，但组合成ZIP仍支持transform。ir_013本地receipt写入有fs_write依据，最终return无值而不标user_output合理。本轮无unresolved只表示模型未记录未决，不代表以上实现边界已被消除。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
