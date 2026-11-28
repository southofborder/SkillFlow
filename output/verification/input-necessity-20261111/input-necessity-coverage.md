# Input necessity acceptance coverage / 输入必要性验收覆盖

Exact test mapping to acceptance points using available completed receipts. Production audit was read-only; final frozen-suite aggregation and online experiments are outside this matrix.

按现有完整收据，将精确测试映射到验收点。生产审计仅只读；最终冻结套件汇总与在线实验不属于本矩阵结论。

**Status / 状态:** Offline acceptance completed separately in [offline-acceptance.json](offline-acceptance.json); no real-model performance claim. / 离线汇总已通过，详见独立验收收据；本矩阵不作真实模型性能结论。

| Point | Requirement / 验收点 | Scope / 覆盖范围 | Remaining assertion / 待补断言 |
|---|---|---|---|
| A1 | Three claimed inputs reduce to the two required fields while actual observations remain.<br>三个声称输入中仅两个字段必要，真实读取与观察保持。 | direct_regressions | None identified in this mapping / 本映射未识别 |
| A2 | Partial object fields and whole unused inputs have distinct reductions, including nonsensitive inputs.<br>对象部分字段和整槽删除采用不同类型，并覆盖非敏感输入。 | direct_regressions | None identified in this mapping / 本映射未识别 |
| A3 | Output selectors remain distinct and multiple requested output components take a union.<br>不同输出字段分别回传需求，多个输出组件需求取并集。 | direct_regressions | None identified in this mapping / 本映射未识别 |
| A4 | Other consumers, controls, cardinality, presence and member pairing prevent unsafe deletion.<br>其他消费、控制、数量、存在性和成员配对防止误删。 | direct_and_composed_regressions | None identified in this mapping / 本映射未识别 |
| A5 | Required tool parameters remain; extra fields are removable; explicit whole requirements remain whole.<br>工具必要参数保留、额外字段可删、明确整值要求保持。 | direct_and_composed_regressions | None identified in this mapping / 本映射未识别 |
| A6 | Wrong or missing required inputs are semantic findings, without synthesizing replacement data.<br>错用或缺失必要输入作为语义错误报告，不虚构替代数据。 | direct_and_composed_regressions | None identified in this mapping / 本映射未识别 |
| A7 | Deletion influence and constraint preservation use the reviewed dependency relation.<br>删除影响与限制保持使用同一核验依赖关系。 | direct_regressions | None identified in this mapping / 本映射未识别 |
| A8 | Unresolved cases need specific evidence and propagate only through affected ranges.<br>未决必须有具体依据，并沿实际影响范围传播。 | direct_regressions | None identified in this mapping / 本映射未识别 |
| A9 | Missing contract rows, bad citations and stale selected-material identities are rejected.<br>契约漏行、错引用和旧材料身份被拒绝。 | direct_regressions | None identified in this mapping / 本映射未识别 |
| A10 | FIFO/LIFO agree and injected responses complete the seven-request path with existing repair closure.<br>FIFO/LIFO 一致，注入答复走通七次正常请求及既有修复闭包。 | direct_regressions | None identified in this mapping / 本映射未识别 |
| A11 | Acquisition-result ranges are reported separately from interface projection capability.<br>获取结果需求范围与接口是否支持裁剪分别说明。 | direct_regressions | None identified in this mapping / 本映射未识别 |

## A1 — Three claimed inputs reduce to the two required fields while actual observations remain.

Direct new-contract regression checks slots 0/a and 1/b, whole slot 2 deletion, unchanged forward input records, and independent change propagation.

新契约测试直接断言槽 0/a、1/b 必需，槽 2 可整槽删除，正向输入记录不变，无关修改不影响输出。

- `tests/doe/test_reviewed_input_necessity.py::test_three_claimed_inputs_only_two_required_and_actual_observations_remain`; latest available receipt: `optional-runtime-and-binding.xml` (passed, 1 case(s))
- `tests/document_guided/test_input_requirement_contracts.py::test_compute_contract_compiles_without_erasing_extra_input_or_observation`; latest available receipt: `optional-input-schema.xml` (passed, 1 case(s))
- `tests/doe/test_input_contract_preservation.py::test_reviewed_independent_field_stops_forward_change_without_erasing_actual_observation`; latest available receipt: `optional-runtime-and-binding.xml` (passed, 1 case(s))

## A2 — Partial object fields and whole unused inputs have distinct reductions, including nonsensitive inputs.

Direct tests assert exclude_field versus remove_input, retained source exposure, complete report inventory without sensitivity labels, and refusal to authorize array reindexing.

直接检查 exclude_field 与 remove_input、原暴露事实保留、零敏感声明仍有输入清单，以及不将成员删除冒充数组重排。

- `tests/doe/test_reviewed_input_necessity.py::test_object_remainder_is_deletable_but_required_field_and_whole_slot_are_not`; latest available receipt: `optional-runtime-and-binding.xml` (passed, 1 case(s))
- `tests/doe/test_input_contract_preservation.py::test_no_demand_after_review_supports_whole_input_removal_and_keeps_original_exposure`; latest available receipt: `optional-runtime-and-binding.xml` (passed, 1 case(s))
- `tests/doe/test_input_contract_preservation.py::test_report_includes_full_input_audit_without_any_sensitive_declarations`; latest available receipt: `optional-runtime-and-binding.xml` (passed, 1 case(s))
- `tests/doe/test_input_contract_preservation.py::test_information_only_member_removal_is_not_an_array_reindex_instruction`; latest available receipt: `optional-runtime-and-binding.xml` (passed, 3 case(s))

## A3 — Output selectors remain distinct and multiple requested output components take a union.

Exact x/z and closed whole-output regressions check selective demands, union, and refusal to reuse a whole-output rule for an unspecified subfield.

x/z 与封闭整体输出测试检查选择性需求、并集，以及整体规则不能充当未指定子字段的精确规则。

- `tests/doe/test_reviewed_input_necessity.py::test_output_field_rules_do_not_promote_unrequested_siblings`; latest available receipt: `optional-runtime-and-binding.xml` (passed, 1 case(s))
- `tests/doe/test_reviewed_input_necessity.py::test_whole_output_rule_is_not_a_narrow_output_rule`; latest available receipt: `optional-runtime-and-binding.xml` (passed, 1 case(s))
- `tests/doe/test_input_contract_preservation.py::test_complete_output_decomposition_limits_change_to_the_affected_output_field`; latest available receipt: `optional-runtime-and-binding.xml` (passed, 1 case(s))
- `tests/document_guided/test_input_requirement_contracts.py::test_closed_output_decomposition_requires_an_explicit_complete_part_inventory`; latest available receipt: `optional-input-schema.xml` (passed, 1 case(s))

## A4 — Other consumers, controls, cardinality, presence and member pairing prevent unsafe deletion.

New contract tests cover another consumer and optional presence/value. Existing deterministic regressions cover control, count/shape/presence properties and pairing; this is composed coverage, not a new blackbox-contract fixture for every property.

新契约直接覆盖另一消费位置和可选字段存在性/值；既有确定性测试覆盖控制、数量/结构/存在性与配对。这是组合覆盖，并非每种属性都新增了黑盒契约整链样例。

- `tests/doe/test_reviewed_input_necessity.py::test_another_needed_consumer_retains_same_ir_input`; latest available receipt: `optional-runtime-and-binding.xml` (passed, 1 case(s))
- `tests/doe/test_reviewed_input_necessity.py::test_optional_input_preserves_presence_and_only_existing_value`; latest available receipt: `optional-runtime-and-binding.xml` (passed, 2 case(s))
- `tests/doe/test_demand_engine.py::test_build_keeps_only_requested_member_and_its_control`; latest available receipt: `demand-core-final.xml` (passed, 1 case(s))
- `tests/doe/test_demand_engine.py::test_model_filter_retains_predicate_field_while_count_needs_structure`; latest available receipt: `demand-core-final.xml` (passed, 2 case(s))
- `tests/doe/test_demand_engine.py::test_built_member_properties_flow_into_actual_member_value`; latest available receipt: `demand-core-final.xml` (passed, 3 case(s))
- `tests/doe/test_loop_summary_relations.py::test_request_pairing_rejects_swapped_occurrences_even_with_equal_aggregate_inputs`; latest available receipt: `integrated-initial.xml` (passed, 1 case(s))
- `tests/doe/test_sensitivity_engine.py::test_repeated_parameters_keep_receiver_slot_specific_demands`; latest available receipt: `constraint-sensitivity-final-v3.xml` (passed, 1 case(s))

## A5 — Required tool parameters remain; extra fields are removable; explicit whole requirements remain whole.

New tests check request/response contract binding, optional parameters, extra-field independence, missing-contract action retention, and a reviewed whole-value tool parameter retaining every present field.

新测试直接检查请求/响应契约绑定、可选参数、额外字段无关性、缺少接口契约时动作输入保留，以及已核验整值工具参数保留全部实际字段。

- `tests/document_guided/test_input_requirement_contracts.py::test_tool_interface_fields_copy_to_request_response_and_keep_extra_payload`; latest available receipt: `optional-input-schema.xml` (passed, 2 case(s))
- `tests/doe/test_input_contract_preservation.py::test_tool_interface_extra_field_does_not_change_paired_response`; latest available receipt: `optional-runtime-and-binding.xml` (passed, 1 case(s))
- `tests/doe/test_input_necessity_review_regressions.py::test_action_only_tool_call_without_interface_contract_retains_unknown_inputs`; latest available receipt: `optional-runtime-and-binding.xml` (passed, 1 case(s))
- `tests/doe/test_sink_payload_seeds.py::test_true_whole_value_requirement_remains_legal_and_precise`; latest available receipt: `fixture-compatibility-initial.xml` (passed, 1 case(s))
- `tests/doe/test_input_necessity_additional_acceptance.py::test_reviewed_tool_whole_value_requirement_retains_every_present_field`; latest available receipt: `additional-acceptance.xml` (passed, 1 case(s))

## A6 — Wrong or missing required inputs are semantic findings, without synthesizing replacement data.

New-contract regressions directly assert missing_input, invalid-type wrong_input, and unchanged forward Data/records. Existing expected-relation regressions detect wrong source/field projection. Intended replacements require an explicit semantic relation.

新契约直接断言 missing_input、类型不匹配的 wrong_input、正向 Data/记录不变；既有 expected 关系测试检测来源/字段投影不匹配。应替换字段仍须明确语义关系。

- `tests/doe/test_input_necessity_review_regressions.py::test_known_absent_required_field_is_a_missing_input_not_an_invented_value`; latest available receipt: `optional-runtime-and-binding.xml` (passed, 1 case(s))
- `tests/doe/test_demand_partial.py::test_expected_relation_on_real_return_operand_is_checked`; latest available receipt: `demand-core-final.xml` (passed, 1 case(s))
- `tests/doe/test_demand_partial.py::test_actual_whole_argument_does_not_become_the_required_original_field`; latest available receipt: `demand-core-final.xml` (passed, 1 case(s))
- `tests/doe/test_demand_engine.py::test_removed_required_field_is_diagnostic_not_recovered_from_parent`; latest available receipt: `demand-core-final.xml` (passed, 1 case(s))
- `tests/doe/test_input_necessity_additional_acceptance.py::test_invalid_required_field_selector_reports_wrong_input_without_repairing_data`; latest available receipt: `additional-acceptance.xml` (passed, 1 case(s))

## A7 — Deletion influence and constraint preservation use the reviewed dependency relation.

Tests retain baseline violations, preserve an independent removal, identify affected operations/constraint pointers for blocked reductions, and avoid vacuous acquisition-output proofs.

测试保留基线违规，支持无关字段删除，阻止影响限制的修改并给出操作/限制指针，避免获取输出零消费者时的空洞保持结论。

- `tests/doe/test_input_contract_preservation.py::test_independent_model_input_removal_preserves_ban_and_keeps_original_violation`; latest available receipt: `optional-runtime-and-binding.xml` (passed, 1 case(s))
- `tests/doe/test_input_contract_preservation.py::test_constraint_named_field_remains_actionable_but_unknown_complement_has_exact_witness`; latest available receipt: `optional-runtime-and-binding.xml` (passed, 1 case(s))
- `tests/doe/test_input_contract_preservation.py::test_acquired_output_checks_actual_consumers_before_claiming_constraint_preservation`; latest available receipt: `optional-runtime-and-binding.xml` (passed, 1 case(s))
- `tests/doe/test_input_contract_preservation.py::test_acquired_output_direct_control_expression_is_not_vacuously_preserved`; latest available receipt: `optional-runtime-and-binding.xml` (passed, 1 case(s))
- `tests/doe/test_constraint_preservation.py::test_same_data_other_receiver_is_not_changed_and_original_violation_remains`; latest available receipt: `constraint-sensitivity-final-v3.xml` (passed, 1 case(s))
- `tests/doe/test_constraint_preservation.py::test_structural_count_proof_does_not_seed_control_or_payload_demands`; latest available receipt: `constraint-sensitivity-final-v3.xml` (passed, 1 case(s))

## A8 — Unresolved cases need specific evidence and propagate only through affected ranges.

Generic opaque reasons are structurally rejected; source-backed local gaps remain local across other inputs/sinks and cyclic derivations. Source-review judgment still decides semantic adequacy.

泛化黑盒理由被结构检查拒绝；源文支持的局部缺口不会污染其他输入/接收端，循环推导祖先按不动点计算。理由在语义上是否成立仍由源文审查判断。

- `tests/document_guided/test_input_requirement_contracts.py::test_unresolved_remainder_requires_a_specific_source_backed_gap`; latest available receipt: `optional-input-schema.xml` (passed, 1 case(s))
- `tests/doe/test_reviewed_input_necessity.py::test_concrete_uncertainty_does_not_block_independent_other_input`; latest available receipt: `optional-runtime-and-binding.xml` (passed, 1 case(s))
- `tests/doe/test_reviewed_input_necessity.py::test_unrelated_partial_review_does_not_erase_accepted_contract`; latest available receipt: `optional-runtime-and-binding.xml` (passed, 1 case(s))
- `tests/doe/test_input_contract_preservation.py::test_unrelated_same_ir_contract_gap_does_not_contaminate_an_independent_sink`; latest available receipt: `optional-runtime-and-binding.xml` (passed, 1 case(s))
- `tests/doe/test_input_necessity_review_regressions.py::test_contract_gap_ancestry_is_a_fixed_point_across_parent_cycles`; latest available receipt: `optional-runtime-and-binding.xml` (passed, 1 case(s))

## A9 — Missing contract rows, bad citations and stale selected-material identities are rejected.

Tests bind source, CFG, Task, raw/compiled annotation, mapping and review coverage; typed runtime receipt equality is also enforced when sensitivity validates a demand result.

测试绑定 source、CFG、Task、原始/编译标注、映射和审查覆盖；敏感性校验需求结果时还检查运行时审查凭据身份一致。

- `tests/document_guided/test_input_requirement_contracts.py::test_invalid_compute_contract_is_rejected_at_its_original_location`; latest available receipt: `optional-input-schema.xml` (passed, 5 case(s))
- `tests/doe/test_input_contract_review.py::test_checks_need_exact_contract_coverage_and_real_source_evidence`; latest available receipt: `review-optional-final.xml` (passed, 1 case(s))
- `tests/doe/test_input_contract_review.py::test_explicit_accepted_receipt_binds_all_selected_materials`; latest available receipt: `review-optional-final.xml` (passed, 1 case(s))
- `tests/doe/test_input_contract_review.py::test_completion_cannot_be_changed_independently_of_bound_review_coverage`; latest available receipt: `review-optional-final.xml` (passed, 1 case(s))
- `tests/doe/test_input_contract_review.py::test_accepted_contract_cannot_overlap_known_representation_finding`; latest available receipt: `review-optional-final.xml` (passed, 4 case(s))
- `tests/doe/test_formal_runner.py::test_tampered_artifacts_are_rejected`; latest available receipt: `optional-runtime-and-binding.xml` (passed, 6 case(s))
- `tests/doe/test_input_necessity_additional_acceptance.py::test_sensitivity_loader_rejects_a_demand_bound_to_another_review_receipt`; latest available receipt: `additional-acceptance.xml` (passed, 2 case(s))

## A10 — FIFO/LIFO agree and injected responses complete the seven-request path with existing repair closure.

Shared reviewed-fixture solve helper compares FIFO/LIFO. Injected flow asserts seven normal calls, four repair-closure requests for a rejected contract, selected revised receipt and zero additional calls on replay.

新契约 solve 辅助函数比较 FIFO/LIFO；注入流程检查七次正常调用、拒绝契约后的四个既有闭包修复请求、选中修订凭据，以及回放无新增调用。

- `tests/doe/test_reviewed_input_necessity.py::test_three_claimed_inputs_only_two_required_and_actual_observations_remain`; latest available receipt: `optional-runtime-and-binding.xml` (passed, 1 case(s))
- `tests/doe/test_reviewed_input_necessity.py::test_output_field_rules_do_not_promote_unrequested_siblings`; latest available receipt: `optional-runtime-and-binding.xml` (passed, 1 case(s))
- `tests/doe/test_input_contract_preservation.py::test_reviewed_independent_field_stops_forward_change_without_erasing_actual_observation`; latest available receipt: `optional-runtime-and-binding.xml` (passed, 1 case(s))
- `tests/document_guided/test_parallel_runner.py::test_seven_calls_dependency_parallelism_true_backend_and_zero_call_replay`; latest available receipt: `integrated-initial.xml` (passed, 1 case(s))
- `tests/document_guided/test_input_contract_review_flow.py::test_rejected_contract_repairs_processing_and_seals_selected_review`; latest available receipt: `audit-formal-final.xml` (passed, 1 case(s))

## A11 — Acquisition-result ranges are reported separately from interface projection capability.

Candidates come from exact Data versions and real nested parts. Reports explicitly state that a deletable acquired-result range does not establish support for narrower retrieval.

候选字段来自精确 Data 版本及真实嵌套部件；报告明确可删的获取结果字段不证明接口支持更窄请求。

- `tests/doe/test_input_contract_preservation.py::test_declared_opaque_field_candidates_are_exact_to_the_recorded_data_version`; latest available receipt: `optional-runtime-and-binding.xml` (passed, 1 case(s))
- `tests/doe/test_input_contract_preservation.py::test_nested_known_parts_use_the_recorded_child_data_identity`; latest available receipt: `optional-runtime-and-binding.xml` (passed, 1 case(s))
- `tests/doe/test_input_contract_preservation.py::test_acquired_output_checks_actual_consumers_before_claiming_constraint_preservation`; latest available receipt: `optional-runtime-and-binding.xml` (passed, 1 case(s))

## Read-only audit / 只读审计

No material defect was identified in the optional-field assessment, receipt binding, or full-input report paths. This is a focused code review, not proof of absence of defects.

本次聚焦审计未发现可选字段评估、审查凭据绑定或全输入报告链路的实质缺陷；这不是无缺陷证明。

The additional acceptance file ran independently of the frozen broad suite: four cases passed in `additional-acceptance.xml`; production source was unchanged.

新增验收文件独立于冻结广测运行：`additional-acceptance.xml` 四个用例通过，生产源码未修改。

## Explicit limits / 明确限制

- **L1** Static schema/reference validation and source-review acceptance do not prove natural-language semantic equivalence or a universally minimal implementation. / 结构/引用校验与源文审查通过不证明自然语言语义等价或所有实现中的全局最小需求。
- **L2** Wrong-input detection needs an expressible source-backed expected relation, invalid selector, or known missing field. It does not infer the intended replacement field without that relation. / 错用输入检测须有可表达且有源文依据的 expected 关系、无效选择器或已知缺失字段；没有该关系时不推测应替换字段。
- **L3** The implementation reports locations and reductions; it does not rewrite or execute the analyzed Skill. / 本实现报告修改位置与删除类型，不自动改写或执行被分析 Skill。
- **L4** Acquired-result nonnecessity is not an assertion that a tool supports server-side projection or accepts fewer request parameters. / 获取结果字段非必要不等于工具支持获取端字段投影或允许减少接口必要参数。
- **L5** Field reductions require a concrete final field name; array/member removals are not issued as reindexing transformations. / 字段排除要求末步为具体字段名；不会将数组/成员删除解释为重排变换。
- **L6** When individual fields are proven removable but an unenumerated complement lacks a collective constraint-preservation rule, only that remainder is unresolved with the actual constraint witness. / 单独字段可证明删除，而未枚举补集缺少整体限制保持规则时，仅该剩余范围带具体限制依据列为未决。
- **L7** Receipt-local tests and injected semantic answers do not measure real-model precision, recall, semantic completeness, or GA4 operational coverage. Those require the separately authorized fresh runs. / 局部测试和注入语义答复不衡量真实模型准确率、召回率、语义完整性或 GA4 实际覆盖；这些须由另外授权的新运行报告。

The JSON preserves exact receipt case names and timestamps. Existing initial failures and corrective receipts remain untouched.

JSON 保留精确收据用例名及时间戳。既有初次失败和修正复验收据未改写。
