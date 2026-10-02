# 021-document-bundle-delivery · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：D03；运行：full-pipeline-v4-20260918-rerun-failed；选图轮次：1
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

尚无已保存的助手逐例复核。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
