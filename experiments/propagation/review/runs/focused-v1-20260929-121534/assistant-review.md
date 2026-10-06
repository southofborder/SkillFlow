# 七例聚焦审查：助手复核与方法结论

本轮已完成七次计划内逻辑调用：**6 份有效审查响应，1 次传输失败**。未重新标注、提取或传播，未自动修复，也没有按质量补跑。请求模型为 deepseek-v4-flash，成功响应记录的返回模型名为 deepseek-flash。

**三个可评估的受控缺陷均被助手确认命中；“无依据局部隔离”因传输失败，尚不能评估。**原始三例并非零问题标准答案。审查器还两次提出同一类普通 return 交付问题，助手认为部分成立但结论过强，不能把它们算成两个新的实质缺陷。

## 逐例结果

| 案例 | 执行结果 | 模型问题数 | 助手复核 |
|---|---|---:|---|
| [001 原标注](cases/001-base/report.html) | complete | 0 | 当前未确认关键数据关系错误；网络边界分类的依据仍有表示限制，不把空清单当作正确性证明。 |
| [010 原标注](cases/010-base/report.html) | complete | 1 | 理由把 CFG 承载关系说成 transfer_specs 承载，确有不一致；但据此断言普通 return 丢失交付，结论过强。 |
| [013 原标注](cases/013-base/report.html) | complete | 0 | 来源整体、各次工具响应、body 原值、返回身份和回退实参均保持；没有因 error 未给物理接口 schema 而机械报错。 |
| [013 无依据局部隔离](cases/013-local/report.html) | execution_error | — | IncompleteRead(0 bytes read)，没有完整响应；方法不可评估，不能记为漏检或通过。 |
| [013 字段关系降精度](cases/013-field/report.html) | complete | 1 | **命中**：compute + possible 不能代替明示的 body 原字段值。 |
| [010 获取来源丢失](cases/010-source/report.html) | complete | 2 | **命中**：请求输入的依赖不能代替工具 receive；另一个 return 发现属于与原 010 相同的过强判断。 |
| [001 通知正文扩大](cases/001-version/report.html) | complete | 1 | **命中**：接收者配对正确，但 body 从 summary 值扩大为整条当前记录。 |

以上“命中”来自助手对具体差异、源文依据、编译观察及建议适用性的复核，不是仅按目标位置自动打分，更不是用户已人工确认。所有原始模型 issue、理由和建议保持原样。

## 三个确认命中的关系

**字段原值。**013-field 的 `f_ir009_body_identity_lost` 精确识别首次响应 body 的 select_part 被替换为 compute(possible)。恢复同一响应的 body 选取是有效建议。其辅助比较中对其他 opcode 的说法略宽，但核心判断由源文和 EM11 独立支持。

**获取来源。**010-source 的 `f_ir007_missing_receive` 明确指出：响应受 query/from_date/limit 影响，不等于响应是这些值计算出来的全部内容。应以工具 receive 恢复获取边界，保留实际请求输入；实施时是替换错误 compute，不能追加同名局部值，也不能补造网络标签。

**实际交付范围。**001-version 的 `f_ir005_deliver_body_argument` 区分了同元素配对与正文身份：recipient 仍正确，body 却绑定整个 record。建议改回已定义的 summary_value 合法，不需要新操作。这里说的是静态参数范围，未执行 Skill 或证实真实敏感数据暴露。

## 为什么不采纳普通 return 的强结论

010 的理由确实声称转发关系已在 transfer_specs 中保留，而 events/output_bindings 为空；承载位置的说明不准确，应承认这一点。

但该 IR 没有公开 outputs，当前规则要求 output_bindings 精确覆盖实际 outputs；不能创建虚构输出。当前事件也没有普通 caller 交付类型，无标签事件不允许任意 deliver。普通 return 不能被机械变成 user_output、net_send 或 model_observe。

返回值及“unchanged”约束仍在完整 CFG 的 return 输入中，上游字段选取和入口状态保留对应 Data 身份。DOE 事实包含 CFG，因此不能把“传递规格没有重复这个事实”说成“所有材料都丢掉了返回关系”。修正理由即可避免承载层混淆；是否将通用调用方边界单独建模属于另一个契约问题。

本轮把两条同类发现标为**部分成立、结论过强**。原始 issue 不改判、不删除；它们不计为确认的实质数据关系缺陷。逐例说明见 [010-base 助手复核](cases/010-base/assistant-review.md) 与 [010-source 助手复核](cases/010-source/assistant-review.md)。

## 工程结果与限制

- 已实现独立 annotation_review 服务及 prepare/run/replay，原标注只读加载，原有续跑源码身份限制未放松。
- 模型输入由源文、CFG、冻结契约、原始标注和确定性编译观察组成；不含传播 Data、DOE、助手意见或外置预期。
- 七份记录全部零 API 重放，恢复相同结果；包括那份传输失败。逻辑调用和 HTTP 尝试均为 7，没有额外逻辑请求。
- 旧材料保护核验覆盖 10,538 个文件，未发现变化；对照旧生产者的 94 个已有源码文件，仅安全标注包新增只读加载导出的入口发生允许的变化。未修改提取、核对、反馈、Data、运行时契约、观察编译或传播算法。
- 集中离线结果见 [工程校验](verification/offline.json)、[重放一致性](verification/replay.json) 和 [旧源码差异](verification/producer-source-diff.json)。

本轮没有给“局部隔离”这类错误取得有效方法结果；也没有证明对无内部矛盾提示的任意错误同样有效。例如 010-source 的 profile 仍声称已有 receive，审查利用了与实际操作的矛盾，这是该具体实验的条件。七例不能提供泛化或统计显著性结论。

下一步应优先给审查器补充精简的现行表示契约解释，明确哪些事实由 CFG 承载、哪些必须在传递规格展开、哪些边界尚未建模，避免 return 这类过度推断。局部隔离变体可在另一个明确记录的新运行中单独补测；本轮没有自动重发，也不接入多轮修复。

## 审计入口

[总览](index.html) · [原始执行统计](summary.json) · [外置预期](evaluation/expectations.json) · [自动位置候选匹配](evaluation/locator-matching.json) · [助手逐项评测](evaluation/assistant-assessment.json)

每例目录包含原始调用、真实返回、程序定位及助手意见。这里所有助手评测均独立于模型输入；它们不回写原标注、传播记录或 DOE 文件。
