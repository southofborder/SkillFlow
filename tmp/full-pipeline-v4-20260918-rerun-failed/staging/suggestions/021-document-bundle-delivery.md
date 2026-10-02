# 021-document-bundle-delivery · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：D03；运行：full-pipeline-v4-20260918-rerun-failed；选图轮次：1
- 执行来源：本次重新执行；父运行：`full-pipeline-v4-20260918`；实际执行运行：`full-pipeline-v4-20260918-rerun-failed`
- 反馈停止：audit_passed；原因：所有业务项均为 represented，且没有明确差异或未决；未填写保守说明不代表精确保留。
- 安全标注：complete；原因：标注记录完整；结构、操作覆盖与证据定位校验通过。
- 图 SHA-256：70a314c9753929e7642b1622b13ef8e52a6b2267b54a0489d7513f1c52025925；源文 SHA-256：dfccfd64ec0b3a817dd8d408c627b30a96b7f4b3d61dbc9318267ff5d40b427a

未填写保守说明不代表精确保留；覆盖记录不证明语义完整。

反馈完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/021/feedback/result.json>)；本地审查页也可展开全文。

安全标注完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/021/annotation/result.json>)；本地审查页也可展开全文。

## finding_1 · context · represented

原文要求：源文 frontmatter 给出 skill 名称 document-bundle-delivery 和描述：转换清单中的文档、打包转换产物并交付到用户指定位置；H1 标题为“多文档处理与交付”。这些是背景/上下文，不是独立业务步骤。

当前表示：受控回述未把名称、描述、标题扩成业务操作；它以入口块和流程块记录实际图内容。

比较理由：按 REVIEW-MODALITY，名称、描述、标题属于背景，不应自动成为业务步骤；受控没有把它们新增为操作，也没有改变业务范围。

源文 `src_001` · `SKILL.md:2-2`：

> name: document-bundle-delivery

源文 `src_001` · `SKILL.md:3-3`：

> description: 转换清单中的文档、打包转换产物并交付到用户指定位置。

源文 `src_002` · `SKILL.md:6-6`：

> # 多文档处理与交付

图位置："/entry_block_id"

## finding_2 · semantic · represented

原文要求：读取用户提供的 manifest.json。

当前表示：block_001 记录 ir_001 read_manifest_file，输入 external_resource manifest.json，输出 result_001 manifest_content；块名称为 Read user-provided manifest.json。

比较理由：动作、对象、来源匹配：manifest.json 作为外部资源定位，读取结果作为后续提取输入；没有额外未支持步骤。

源文 `src_003` · `SKILL.md:10-10`：

> | 1 | input | 读取用户提供的 manifest.json，按其中 paths 列表获取文档路径，并从请求中读取 output_dir 和 delivery_path。 |

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

## finding_3 · semantic · represented

原文要求：按 manifest.json 中 paths 列表获取文档路径。

当前表示：block_002 记录 ir_003 extract_document_paths_from_manifest，输入 result_001（manifest_content）和 literal "paths"，输出 result_002 document_paths；link fact:/blocks/1/instructions/0/inputs/0:link 将 result_001 指向 block_001 定义。

比较理由：绑定正确：从 manifest 内容按 paths 提取 document_paths；无新增来源。

源文 `src_003` · `SKILL.md:10-10`：

> | 1 | input | 读取用户提供的 manifest.json，按其中 paths 列表获取文档路径，并从请求中读取 output_dir 和 delivery_path。 |

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

当前表示：fact:/contexts 声明 output_dir、delivery_path；block_003 记录 ir_005 read_output_dir_and_delivery_path_from_request，输入 context_key output_dir 和 context_key delivery_path，输出 result_003 requested_output_dir、result_004 requested_delivery_path。

比较理由：对象和来源匹配；context_key 表示从请求/上下文读取，两个键分别对应两个输出。

源文 `src_003` · `SKILL.md:10-10`：

> | 1 | input | 读取用户提供的 manifest.json，按其中 paths 列表获取文档路径，并从请求中读取 output_dir 和 delivery_path。 |

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

原文要求：逐个执行 python scripts/convert.py <文档路径> <output_dir>，把每次标准输出作为对应的转换产物路径。

当前表示：block_004 记录 ir_007 convert_documents_individually_with_convert_script，输入 result_002 document_paths、result_003 requested_output_dir、external_resource scripts/convert.py，输出 result_005 converted_artifact_paths；links 将 result_002、result_003 指向定义；metadata 记录 command_template、execution_mode=for_each_document_path、iteration_input、iteration_stdout_binding。

比较理由：动作、脚本对象、输入绑定、逐文档执行和 stdout 绑定均保留；result_002/003 链接正确。

源文 `src_003` · `SKILL.md:11-11`：

> | 2 | convert | 逐个执行 python scripts/convert.py <文档路径> <output_dir>，把每次标准输出作为对应的转换产物路径。 |

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

原文要求：转换期间保留原文标题；该要求仅限转换，不限制汇总标题。

当前表示：fact:/blocks/3/instructions/0/constraints/0 原文记录该约束，作用域挂在 ir_007 转换操作。

比较理由：约束文字和限定范围一致。

源文 `src_003` · `SKILL.md:12-12`：

> | 3 | local constraint | 转换期间保留原文标题；该要求仅限转换，不限制汇总标题。 |

图位置："/blocks/block_004/instructions/0/constraints/0"

## finding_7 · semantic · represented

原文要求：转换通过 scripts/convert.py 完成；主流程只使用脚本输出路径，不重复执行脚本内部的处理。

当前表示：fact:/blocks/3/instructions/0/constraints/1 原文记录；ir_007 使用 scripts/convert.py 并输出 result_005，metadata 保留脚本内容但标注未解释/未执行。

比较理由：黑盒约束保留；嵌入脚本正文不等于新增内部步骤。

源文 `src_003` · `SKILL.md:13-13`：

> | 4 | blackbox | 转换通过 scripts/convert.py 完成；主流程只使用脚本输出路径，不重复执行脚本内部的处理。 |

图位置："/blocks/block_004/instructions/0/constraints/1"

## finding_8 · semantic · represented

原文要求：打包时必须采用参考步骤的命令 python scripts/package.py --paths <转换产物路径列表> --output bundle.zip，并将转换产物路径列表传给 --paths。

当前表示：/blocks/4 记录 ir_009 package_converted_artifacts_with_package_script，输入 result_005 converted_artifact_paths、external_resource scripts/package.py、literal "bundle.zip"，输出 result_006 bundle_zip_path；constraint/0 原文记录必须采用参考步骤并传给 --paths；metadata command_template 与源文命令一致；link fact:/blocks/4/instructions/0/inputs/0:link 将 result_005 指向 convert 输出。

比较理由：命令、脚本、路径列表到 --paths 的绑定以及 --output bundle.zip 均在 constraint/metadata 中保留；result_005 链接正确。

源文 `src_003` · `SKILL.md:14-14`：

> | 5 | package | 打包时必须采用下方“参考步骤”的命令，并将转换产物路径列表传给 --paths。 |

源文 `src_004` · `SKILL.md:21-21`：

> ## 参考步骤

源文 `src_005` · `SKILL.md:24-24`：

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

## finding_9 · semantic · represented

原文要求：将生成的 bundle.zip 交付到请求的 delivery_path。

当前表示：/blocks/5 记录 ir_011 deliver_bundle_to_delivery_path，输入 result_006 bundle_zip_path、result_004 requested_delivery_path；links 将两者指向 package 输出和 request 输出。

比较理由：动作、对象和目的地匹配。

源文 `src_003` · `SKILL.md:15-15`：

> | 6 | deliver | 将生成的 bundle.zip 交付到请求的 delivery_path。 |

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

## finding_10 · semantic · represented

原文要求：另外，将转换产物路径列表写入本地 receipt.txt。

当前表示：/blocks/6 记录 ir_013 write_receipt_file，输入 result_005 converted_artifact_paths 和 literal "receipt.txt"；无输出；link 将 result_005 指向 convert 输出。

比较理由：写入对象 receipt.txt 与数据来源转换产物路径列表保留；opcode/write_receipt_file 和字面文件名体现本地文件写入，无外部上传资源或额外输出。

源文 `src_003` · `SKILL.md:16-16`：

> | 7 | receipt | 另外，将转换产物路径列表写入本地 receipt.txt。 |

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

## finding_11 · semantic · represented

原文要求：整份流程不得修改输入原文文件；整份流程禁止把文档上传到外部服务。

当前表示：fact:/constraints/0 和 fact:/constraints/1 原文记录两条图级声明约束。

比较理由：禁止内容和全局作用域一致；声明不等于已实现，但源文要求被保留为约束声明。

源文 `src_003` · `SKILL.md:17-17`：

> | 8 | global constraint | 整份流程不得修改输入原文文件。 |

源文 `src_003` · `SKILL.md:18-18`：

> | 9 | global constraint | 整份流程禁止把文档上传到外部服务。 |

图位置："/constraints/0"

图位置："/constraints/1"

## finding_12 · context · represented

原文要求：备注：必要时保留原顺序。

当前表示：受控边 fact:/edges/0..5 依次连接 block_001→002→003→004→005→006→007，保持表中业务步骤顺序；条件字段均未记录。

比较理由：源文是备注，不是新增分支或操作；受控顺序边与表中步骤顺序一致。‘必要时’未被建模为条件，但按 REVIEW-MODALITY 它是备注/上下文，不应扩成额外业务条件。

源文 `src_003` · `SKILL.md:19-19`：

> | 10 | note | 备注：必要时保留原顺序。 |

图位置："/edges/0"

图位置："/edges/1"

图位置："/edges/2"

图位置："/edges/3"

图位置："/edges/4"

图位置："/edges/5"

## finding_13 · semantic · represented

原文要求：scripts/convert.py 的完整脚本内容（UTF-8 转换并打印输出路径）。

当前表示：fact:/blocks/3/instructions/0/metadata_json 的 script_content 完整嵌入源脚本内容。

比较理由：嵌入内容与源文件逐行一致；metadata 标注未解释/未执行，符合黑盒建模，不新增内部步骤。

源文 `src_006` · `scripts/convert.py:1-1`：

> """Convert one UTF-8 text document and print the output path."""

源文 `src_007` · `scripts/convert.py:9-9`：

> output.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

图位置："/blocks/block_004/instructions/0/metadata"

## finding_14 · semantic · represented

原文要求：scripts/package.py 的完整脚本内容（从提供的输出路径构建 ZIP）。

当前表示：fact:/blocks/4/instructions/0/metadata_json 的 script_content 完整嵌入源脚本内容。

比较理由：嵌入内容与源文件逐行一致；metadata 标注未解释/未执行。

源文 `src_008` · `scripts/package.py:1-1`：

> """Build the explicitly requested ZIP from supplied output paths."""

源文 `src_009` · `scripts/package.py:7-7`：

> parser.add_argument("--paths", nargs="+", required=True)

图位置："/blocks/block_005/instructions/0/metadata"

## 助手事后复核

此部分独立于模型核对记录，未经人工确认，不追溯修改模型判定。

### 修复轮次 0 · 历史轮次，不能作为当前图结论

图 SHA-256：f0bd3f745f17ebd1052cc218160f90fe6d1d34fb2c6a27b602b6f1336fb29c5b

助手复核初轮的两条定向反馈及其对应原图，认为修复有助于明确字段与逐项绑定，但不能把两条初轮判断都当作已证实的业务遗漏；这不是人工确认。

- r0 finding_5 要求显式绑定 manifest.paths：ir_003 确实只有 manifest_content 操作数，但 block_002 标签已写 Extract document paths from manifest paths list。增加 literal paths 使表示更清晰；原判断把‘标签不能补造操作’进一步解释为‘已有提取操作不能借标签说明取哪个字段’，存在过度要求表示位置的空间，不能据此统计为无争议真实漏转。
- r0 finding_9 指出逐文档执行与 stdout 对应关系不够明确；原 block_004 已写 Convert each document，metadata 保留单文档命令、print(output) 脚本，块约束也写主流程只用输出路径。因此主要缺口是批量结果如何逐项绑定的显式程度，不是原图完全没有‘逐个转换’这一过程。r1 增补 iteration_stdout_binding 等 metadata 后没有引入第二份脚本执行。

### 修复轮次 1 · 当前所选图

图 SHA-256：70a314c9753929e7642b1622b13ef8e52a6b2267b54a0489d7513f1c52025925

助手已复核完整三文件源包、最终图、全部核对项及 14 条安全标注，并查看实际 PNG 全图与原分辨率细节。关键转换、打包、交付和回执流程未见明显漏转；执行者归属与交付机制仍有推断边界，标注 complete 不等于这些推断已证明。这不是人工确认。

- r1 finding_3/4/5 与实际 ir_003/005/007 对应：manifest.paths 显式 literal、请求 output_dir/delivery_path 的独立结果身份、按每文档执行的 opcode/metadata、每次 stdout 对应转换产物路径均保留。result_005 继续用于打包和 receipt；没有把原始文档路径误接为转换产物列表。
- r1 finding_6/7/8/9/10/11 与图一致：标题保留只挂转换 ir_007，黑盒脚本没有在主流程展开重复执行；package 命令与 --paths/--output bundle.zip 保留；新增 result_006 从实际打包操作流向交付 ir_011，目的地来自请求 result_004；ir_013 另写本地 receipt.txt，随后空 return。两条全局禁止声明保持全局作用域，没有补造遮蔽、上传或用户输出动作。
- 逐文档关系在本轮由开放操作名与完整 metadata 保留，CFG 本身仍是 7 块 6 条顺序边，没有显式循环边；这可视为批处理抽象，但不能声称已经证明每次调用执行或文件写入成功。后续传播若需要逐文件精度，需明确这类批处理事实的解释规则，不能从‘核对器通过’直接推导执行保证。
- 全部 14 个 IR 均有一份四字段标注，6 个 dispatch 与末尾 return 的 roles/effects 为空并附理由，未硬贴 transform/user_output。ir_007 与 ir_009 的 fs_read/fs_write/transform 及多 roles 有实际嵌入脚本 read_text/write_text/archive.write 依据；禁止上传声明没有被当作已实现的净化动作，也没有凭 external_resource 推断网络通信。
- ir_007 的 model_observe 依据 EM02 作用于 convert.py 明确 print(output) 返回的路径，证据没有证明整份文档或 ZIP 正文进入模型；后续传播必须保持这个对象边界。其 actor=llm 的理由仅是‘模型参与接收’，而 actor 契约区分执行者与接收者，故这个 actor 标签仍需谨慎解释，不能因 model_observe 自动推成模型执行转换。
- ir_001、ir_003、ir_005、ir_011、ir_013 直接推断 actor=agent_runtime，但源文和图未统一限定这些动作必须以纯本地运行时实现；尤其 ir_001 读取清单是否属于回传工具结果、ir_003 是否由模型处理，不能只凭 opcode 确定。当前无 unresolved，不代表这类主体/观察边界已经被源文解决。ir_011 的 fs_write 是交付到路径的合理本地解释，具体交付机制仍未写明；不应反过来据此声称发生网络发送。
- 全局‘不得修改输入原文文件’已作为声明保留。嵌入 convert.py 按 output_dir/source.stem.txt 写入，没有显式防止输出路径与输入路径相同的检查；这是源脚本及约束之间尚需执行前提约束的边界，不能把声明保留算成已证明不会覆盖输入。本轮没有擅自给图补防护。
- 已查看 1260×5017 的实际 PNG 全图及转换/打包与标题区原分辨率细节：中文正常，014 个 IR、7 块与 6 条有向边可见，条件 null 如实显示，约束换行留在节点内，末尾 return 未裁切；图标题绑定 021/D03/r1 与本记录图摘要。PNG SHA-256=d13908b16e53ec48cbe1a0fbcacf1628186df3e1f83dd33230ac3a7f5aa07e0a；静态预览位于 tmp/full-pipeline-v4-20260918-rerun-failed/preview-021。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
