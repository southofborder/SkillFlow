# 020-document-bundle-delivery · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：D02；运行：full-pipeline-v4-20260918-rerun-failed；选图轮次：0
- 执行来源：本次重新执行；父运行：`full-pipeline-v4-20260918`；实际执行运行：`full-pipeline-v4-20260918-rerun-failed`
- 反馈停止：audit_passed；原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。
- 安全标注：incomplete；原因：保留有依据的标注，存在未决项。
- 图 SHA-256：574547ff095741ab123aa95b75e0bdb9b7e34734fee4d025d9d2f545012eeec1；源文 SHA-256：b1e51ead1f510ef5f4af1e44bea5951cad0a5fa9a355532a108304e6766cdba4

未填写保守说明不代表精确保留；覆盖记录不证明语义完整。

反馈完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/020/feedback/result.json>)；本地审查页也可展开全文。

安全标注完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/020/annotation/result.json>)；本地审查页也可展开全文。

## finding_1 · context · represented

原文要求：Skill 元数据、标题和参考步骤标题属于上下文：frontmatter 的名称与描述、一级标题、参考步骤标题，不构成读取、转换、打包、交付等业务动作要求。

当前表示：受控回述以受控回述标题、入口块、块标签和约束组织图；未把 frontmatter 名称、描述或 Markdown 标题复述为业务步骤。参考命令的实际内容在后续 metadata 与约束中保留。

比较理由：这些单元是标识和展示性上下文，不产生动作、对象、条件或返回要求；受控回述未将其转成额外操作。

源文 `src_001` · `SKILL.md:2-2`：

> name: document-bundle-delivery

源文 `src_001` · `SKILL.md:3-3`：

> description: 转换清单中的文档、打包转换产物并交付到用户指定位置。

源文 `src_002` · `SKILL.md:6-6`：

> # 多文档处理与交付

源文 `src_008` · `SKILL.md:18-18`：

> ## 参考步骤

图位置："/entry_block_id"

图位置："/blocks/block_005/instructions/0/metadata"

## finding_2 · semantic · represented

原文要求：读取用户提供的 manifest.json，并按其中 paths 列表获取文档路径。

当前表示：block_001 记录 read_manifest_file，输入 manifest.json，输出 result_001；block_002 记录 extract_document_paths_from_manifest，输入 result_001，输出 result_002；块级与操作级约束明确按 manifest 的 paths 列表获取文档路径。

比较理由：动作、对象、输入输出和 paths 列表约束均有定位；result_001 到提取操作的依赖由后续 link 记录，源文中的读取与提取关系未被合并成无依据的新步骤。

源文 `src_003` · `SKILL.md:8-8`：

> 读取用户提供的 manifest.json，按其中 paths 列表获取文档路径

图位置："/blocks/block_001/block_id"

图位置："/blocks/block_001/block_name"

图位置："/blocks/block_001/data_source_kind"

图位置："/blocks/block_001/instructions"

图位置："/blocks/block_001/instructions/0"

图位置："/blocks/block_001/instructions/0/inputs/0"

图位置："/blocks/block_001/instructions/0/outputs/0"

图位置："/blocks/block_001/instructions/0/metadata"

图位置："/blocks/block_002/block_id"

图位置："/blocks/block_002/block_name"

图位置："/blocks/block_002/data_source_kind"

图位置："/blocks/block_002/constraints/0"

图位置："/blocks/block_002/instructions"

图位置："/blocks/block_002/instructions/0"

图位置："/blocks/block_002/instructions/0/inputs/0"

图位置："/blocks/block_002/instructions/0/outputs/0"

图位置："/blocks/block_002/instructions/0/constraints/0"

图位置："/blocks/block_002/instructions/0/metadata"

## finding_3 · semantic · represented

原文要求：从请求中读取 output_dir 和 delivery_path。

当前表示：fact:/contexts 声明 output_dir 与 delivery_path；block_003 的 ir_005 read_output_and_delivery_from_request 以 context_key 读取这两个键，并分别输出 result_003 与 result_004。声明本身不是读取操作，但对应读取操作已记录。

比较理由：两个请求键的对象身份和读取动作均被保留，且没有把声明误当成实际读取来替代操作记录。

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

## finding_4 · semantic · represented

原文要求：逐个执行 python scripts/convert.py <文档路径> <output_dir>，把每次标准输出作为对应的转换产物路径；转换期间保留原文标题且该要求仅限转换；转换通过 scripts/convert.py 完成，主流程只使用脚本输出路径，不重复执行脚本内部处理。

当前表示：block_004 记录 run_convert_script_for_each_document，输入 scripts/convert.py、result_002 文档路径、result_003 output_dir，输出 result_005，其语义为来自 stdout 的转换产物路径；约束记录标题保留、stdout 对应产物路径与必要时保留原顺序；metadata 保留 convert.py 脚本内容、调用模板和 side effects；全局约束2记录脚本完成转换且不重复内部处理。

比较理由：转换动作、脚本、输入、输出身份、逐文档语义、标题约束和脚本黑盒边界均有记录；脚本内部处理只作为嵌入内容保留，没有被另建为主流程重复操作。

源文 `src_003` · `SKILL.md:8-8`：

> 逐个执行 python scripts/convert.py <文档路径> <output_dir>，把每次标准输出作为对应的转换产物路径。

源文 `src_004` · `SKILL.md:10-10`：

> 转换期间保留原文标题；该要求仅限转换，不限制汇总标题。 转换通过 scripts/convert.py 完成；主流程只使用脚本输出路径，不重复执行脚本内部的处理。

源文 `src_010` · `scripts/convert.py:2-2`：

> from pathlib import Path

源文 `src_011` · `scripts/convert.py:10-10`：

> print(output)

图位置："/constraints/2"

图位置："/blocks/block_004/block_id"

图位置："/blocks/block_004/block_name"

图位置："/blocks/block_004/data_source_kind"

图位置："/blocks/block_004/constraints/0"

图位置："/blocks/block_004/instructions"

图位置："/blocks/block_004/instructions/0"

图位置："/blocks/block_004/instructions/0/inputs/0"

图位置："/blocks/block_004/instructions/0/inputs/1"

图位置："/blocks/block_004/instructions/0/inputs/2"

图位置："/blocks/block_004/instructions/0/outputs/0"

图位置："/blocks/block_004/instructions/0/constraints/0"

图位置："/blocks/block_004/instructions/0/constraints/1"

图位置："/blocks/block_004/instructions/0/constraints/2"

图位置："/blocks/block_004/instructions/0/metadata"

## finding_5 · semantic · represented

原文要求：打包时必须采用参考步骤命令，并将转换产物路径列表传给 --paths；参考命令为 python scripts/package.py --paths <转换产物路径列表> --output bundle.zip；package.py 接口要求 --paths 与 --output。

当前表示：block_005 记录 package_converted_documents_with_script，输入 scripts/package.py、result_005 converted_file_paths、literal bundle.zip；块级与操作级约束重复必须采用参考步骤并把路径列表传给 --paths；metadata 保留参考命令、package.py 脚本内容和写 ZIP 到 bundle.zip 的 side effect。

比较理由：打包动作、脚本、路径列表、输出 bundle.zip 以及 --paths 与 --output 接口由操作数、约束和 metadata 共同保留；literal bundle.zip 对应命令中的 --output 值。

源文 `src_005` · `SKILL.md:12-12`：

> 打包时必须采用下方“参考步骤”的命令，并将转换产物路径列表传给 --paths。

源文 `src_009` · `SKILL.md:21-21`：

> python scripts/package.py --paths <转换产物路径列表> --output bundle.zip

源文 `src_012` · `scripts/package.py:2-2`：

> import argparse

源文 `src_013` · `scripts/package.py:11-11`：

>     for filename in args.paths:

图位置："/blocks/block_005/block_id"

图位置："/blocks/block_005/block_name"

图位置："/blocks/block_005/data_source_kind"

图位置："/blocks/block_005/constraints/0"

图位置："/blocks/block_005/instructions"

图位置："/blocks/block_005/instructions/0"

图位置："/blocks/block_005/instructions/0/inputs/0"

图位置："/blocks/block_005/instructions/0/inputs/1"

图位置："/blocks/block_005/instructions/0/inputs/2"

图位置："/blocks/block_005/instructions/0/constraints/0"

图位置："/blocks/block_005/instructions/0/metadata"

## finding_6 · semantic · represented

原文要求：将生成的 bundle.zip 交付到请求的 delivery_path。

当前表示：block_006 记录 deliver_bundle_to_delivery_path，输入 literal bundle.zip 与 result_004 requested_delivery_path；约束一致；metadata side effect 说明交付到请求的 delivery_path；前置 block_005 的 metadata 说明生成并写入 bundle.zip。

比较理由：交付动作、对象 bundle.zip、目标 result_004 和执行顺序均有记录；生成关系由 package 的 side effect 与前后边支持，未发现多用或漏用 delivery_path。

源文 `src_005` · `SKILL.md:12-12`：

> 将生成的 bundle.zip 交付到请求的 delivery_path。

图位置："/blocks/block_006/block_id"

图位置："/blocks/block_006/block_name"

图位置："/blocks/block_006/data_source_kind"

图位置："/blocks/block_006/constraints/0"

图位置："/blocks/block_006/instructions"

图位置："/blocks/block_006/instructions/0"

图位置："/blocks/block_006/instructions/0/inputs/0"

图位置："/blocks/block_006/instructions/0/inputs/1"

图位置："/blocks/block_006/instructions/0/constraints/0"

图位置："/blocks/block_006/instructions/0/metadata"

## finding_7 · semantic · represented

原文要求：将转换产物路径列表写入本地 receipt.txt，并在流程完成后终止。

当前表示：block_007 记录 write_converted_paths_to_receipt，输入 result_005 converted_file_paths 与 external_resource receipt.txt；块级与操作级约束一致；metadata side effect 说明写入本地 receipt.txt；随后 ir_014 return 无返回值结束当前路径。

比较理由：写入对象、目标本地文件、数据来源 result_005 和终止操作均有定位；return 本身不表示额外输出或向用户展示内容。

源文 `src_006` · `SKILL.md:14-14`：

> 另外，将转换产物路径列表写入本地 receipt.txt。

图位置："/blocks/block_007/block_id"

图位置："/blocks/block_007/block_name"

图位置："/blocks/block_007/data_source_kind"

图位置："/blocks/block_007/constraints/0"

图位置："/blocks/block_007/instructions"

图位置："/blocks/block_007/instructions/0"

图位置："/blocks/block_007/instructions/0/inputs/0"

图位置："/blocks/block_007/instructions/0/inputs/1"

图位置："/blocks/block_007/instructions/0/constraints/0"

图位置："/blocks/block_007/instructions/0/metadata"

图位置："/blocks/block_007/instructions/1"

图位置："/blocks/block_007/instructions/1/metadata"

## finding_8 · semantic · represented

原文要求：整份流程不得修改输入原文文件；整份流程禁止把文档上传到外部服务。

当前表示：全局约束 fact:/constraints/0 与 fact:/constraints/1 逐字记录这两项；图中未记录修改输入原文或上传文档到外部服务的业务操作。

比较理由：禁止项以图级约束保留，作用域为整份流程；已记录操作中未见违反，也未把 external_resource 类型本身推断为网络发送或额外参数。

源文 `src_006` · `SKILL.md:14-14`：

> 整份流程不得修改输入原文文件。

源文 `src_007` · `SKILL.md:16-16`：

> 整份流程禁止把文档上传到外部服务。

图位置："/constraints/0"

图位置："/constraints/1"

## finding_9 · semantic · represented

原文要求：备注：必要时保留原顺序。

当前表示：全局约束 fact:/constraints/3 记录该备注；转换操作 ir_007 的约束2也重复该备注。全局作用域仍保留，转换处的重复不缩小全局要求。

比较理由：备注文本、条件性和全局作用域被保留；转换处重复属于声明辅助，不新增业务动作或改变作用域。

源文 `src_007` · `SKILL.md:16-16`：

> 备注：必要时保留原顺序。

图位置："/constraints/3"

图位置："/blocks/block_004/instructions/0/constraints/2"

## finding_10 · semantic · represented

原文要求：流程次序为：读取 manifest、提取 paths、读取请求 output_dir 与 delivery_path、逐个转换、打包、交付、写 receipt、结束。

当前表示：edges/0 到 edges/5 依次连接 block_001 到 block_007；各前置块均记录 dispatch 指向后继块，末块以 return 结束。

比较理由：各步骤顺序和终结操作与源文叙述一致；dispatch 与 return 是固定控制操作，不产生额外业务输出，也未据此虚构条件或循环终止保证。

源文 `src_003` · `SKILL.md:8-8`：

> 读取用户提供的 manifest.json，按其中 paths 列表获取文档路径，并从请求中读取 output_dir 和 delivery_path。 逐个执行 python scripts/convert.py <文档路径> <output_dir>，把每次标准输出作为对应的转换产物路径。

源文 `src_005` · `SKILL.md:12-12`：

> 打包时必须采用下方“参考步骤”的命令，并将转换产物路径列表传给 --paths。 将生成的 bundle.zip 交付到请求的 delivery_path。

源文 `src_006` · `SKILL.md:14-14`：

> 另外，将转换产物路径列表写入本地 receipt.txt。 整份流程不得修改输入原文文件。

图位置："/entry_block_id"

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

图位置："/edges/0"

图位置："/edges/1"

图位置："/edges/2"

图位置："/edges/3"

图位置："/edges/4"

图位置："/edges/5"

## finding_11 · semantic · represented

原文要求：数据绑定：manifest 内容用于提取文档路径；文档路径和 output_dir 用于转换；转换输出路径列表用于打包并写入 receipt；delivery_path 用于交付生成的 bundle.zip。

当前表示：links 记录 result_001 到提取操作、result_002 与 result_003 到转换操作、result_005 到打包操作、result_004 到交付操作、result_005 到 receipt 写入操作，均按实际 identifier 关联定义与使用。

比较理由：各 result 的定义位置和实际使用位置被绑定；未把不同 result 混用，bundle.zip 作为 literal 路径与 package side effect 对齐，交付目标使用 result_004。

源文 `src_003` · `SKILL.md:8-8`：

> 读取用户提供的 manifest.json，按其中 paths 列表获取文档路径，并从请求中读取 output_dir 和 delivery_path。 逐个执行 python scripts/convert.py <文档路径> <output_dir>，把每次标准输出作为对应的转换产物路径。

源文 `src_005` · `SKILL.md:12-12`：

> 打包时必须采用下方“参考步骤”的命令，并将转换产物路径列表传给 --paths。 将生成的 bundle.zip 交付到请求的 delivery_path。

源文 `src_006` · `SKILL.md:14-14`：

> 另外，将转换产物路径列表写入本地 receipt.txt。 整份流程不得修改输入原文文件。

图位置："/blocks/block_002/instructions/0/inputs/0"

图位置："/blocks/block_004/instructions/0/inputs/1"

图位置："/blocks/block_004/instructions/0/inputs/2"

图位置："/blocks/block_005/instructions/0/inputs/1"

图位置："/blocks/block_006/instructions/0/inputs/1"

图位置："/blocks/block_007/instructions/0/inputs/0"

## 安全标注未决

- {"instruction_id": "ir_011", "field": "effects", "reason": "IR 仅记录交付到 delivery_path，未记录本地写入、远端发送或用户直接可见等机制；无法确定应标 fs_write、net_send 还是 user_output，故不猜测。"}

## 助手事后复核

此部分独立于模型核对记录，未经人工确认，不追溯修改模型判定。

### 修复轮次 0 · 当前所选图

图 SHA-256：574547ff095741ab123aa95b75e0bdb9b7e34734fee4d025d9d2f545012eeec1

核心转换、打包、交付和回执语义未见明显漏转，关键脚本与命令完整保留；1项交付边界未决合理。需保留模型/运行时 actor 推断、文件副作用传播和声明不等于运行保证的边界，不能把核对器通过与标注证据格式通过当作已证明执行安全。

- 本次助手逐项复核冻结 D02 的 SKILL.md、convert.py、package.py、7块/6边/14 IR、11条核对发现及全部14份安全 profile 的52条证据；图与标注摘要均绑定本次 r0，未沿用旧运行图或结论。模型判定 audit_passed，10条业务项 represented；annotation incomplete，1项交付效果未决。此记录不是人工确认或语义等价证明。
- 核心流程已记录：ir_001 读取 manifest.json→result_001；ir_003 按 paths 提取 result_002；ir_005 从请求取得 output_dir/result_003 与 delivery_path/result_004。ir_007 对每个文档调用转换脚本并把 stdout 路径收集为 result_005，ir_009 使用该路径列表与 bundle.zip 打包；ir_011 交付 bundle.zip 到 result_004；ir_013 将同一 result_005 写入本地 receipt.txt，随后无值 return。未见路径绑定错误或遗漏交付/回执步骤。
- 转换与打包完整脚本均逐字保留于 metadata，分别与冻结文件比较相同；转换调用模板、每次 stdout 对应产物路径及打包参考命令 python scripts/package.py --paths <转换产物路径列表> --output bundle.zip 均显式保留。主流程仅有聚合的逐文档脚本调用，没有复制脚本内部操作造成重复执行。逐文档语义记录在开放 opcode/约束中，没有展开逐次 CFG 循环；不能据此声称循环展开、次数或运行成功已被证明。
- 标题保留仅约束转换，未扩大为汇总标题；不修改输入、不上传外部服务与必要时保留顺序保留为全局声明。顺序备注的“必要时”仍由源文本身留白，图的逐字保留不等于给出了触发条件。核对器 finding_8 只能成立为声明已保留，不能理解为执行保证：convert.py 由 output_dir/source.stem 构造输出且未做路径别名检查，若输出恰好与输入重合，源码存在写入同一文件的可能；本轮没有加入防护动作，不能声称已证明不会改写原文。
- 为后续数据传播保留的边界：ir_009 没有 result 输出，bundle.zip 的生成写入在 metadata/副作用中表达，ir_011 以同一路径字面值引用该产物。原文关键对象可从文件名与前序动作对应，不能因缺少 result 连边就误判没有打包—交付的数据关系；也不能由同名路径直接证明运行时别名或成功写入。
- 文件与变换标签总体与显式行为对应：manifest 读取有 fs_read；转换脚本有 fs_read/fs_write、source/sink/transformer；打包从 archive.write/ZipFile 写入可支持 fs_read/fs_write/transform；receipt 写入有 sink/fs_write。六条 dispatch 和最终无值 return 采用空 roles/effects，证据明确为控制动作，不将 return 自动标成 user_output，也未从禁止上传声明补造遮蔽或隔离动作。
- 模型观察依据须保留范围：ir_001 的 manifest 内容、ir_007 的 stdout 产物路径按 EM02 工具回传假设标 model_observe；这不自动意味着转换脚本读取的全文、ZIP 内全部内容或整个环境已进入模型。ir_009 无显式输出且脚本无 print，本次没有盲目把所有工具操作都标为 model_observe；错误输出等未建模内容仍属于边界。
- actor/模型处理仍有推断边界：ir_003 以“不是文件或网络工具”便断定由 LLM 提取 paths，证据不足以排除本地 JSON 字段提取。此前 manifest 已依 EM02 可见，并不能单独证明下一步必须由模型执行；该 actor 与该步 model_observe 应保留为实现假设或未决，不能当成源文确定事实。ir_005 只标 agent_runtime/context_read 也不能倒推请求值被明确隔离于模型。
- 唯一正式 unresolved 是 ir_011 的 effects：delivery_path 未指明本地写入、远端传输或用户展示机制，外置保留未决而不猜 net_send/fs_write/user_output 是合理做法。其 actor=tool 同样是实现推断，源文只给交付动作，没有指定具体执行工具。未决不因 audit_passed 消失，不能据 incomplete 结果作已完成安全边界判断。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
