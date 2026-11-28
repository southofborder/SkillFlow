# 字段必要性补全：源文错误与删除位置验收

本说明记录 2026-11-11 四个真实分析及各自唯一重放关闭之后的离线补全。没有启动新的模型、Skill 或历史重放。原四次运行的材料与结论保持原样；本文件不是对这些旧运行的重新判定。

## 已实现的结果接口

`source_input_findings` 将源文已经证明的 `missing_argument`、`missing_field`、`wrong_field` 独立于材料表示错误和未决关系。缺失整个参数使用 `absent_argument`，没有虚构的输入槽、Data、值或节点；字段问题只能定位真实操作的实际输入。预期接口参数／源文角色与实际 CFG 输入分别表示。要求依据和实际发生位置分别引用冻结源文；所有坐标和证据范围均由程序核对。

同一调用中的请求动作和返回字段由既有调用配对映射到实际 deliver／receive。一个源文错误保留一个标识，可以有多个实际操作位置。它只影响被需求的相应动作／输出范围，不创建任务需求。若普通 processing／CFG finding 同时声称该实际操作表示不忠实，程序拒绝把它再确认为源文错误；契约关系或获取端投影关系的修正不自动构成这种冲突。

每条 `input_assessment` 增加真实 CFG 指针、原始标注位置、可映射的 wire 位置、已有元数据绑定位置、真正提供的源文行范围和作用域。未提供源文证据的情况明确标为 `annotation_only`，不会补造源文列号。条件构造的输入位置根据传播记录中的成员／控制槽映射，不能把未执行成员造成的槽位变化当作同一个输入。

可删范围分别给出 `remove_input`、`exclude_field` 或保留所列信息要求的 `keep_ranges`。数量、结构、存在性等需求保留在范围方案内。终端数组索引／成员选择器没有默认成员删除或重排方案。生成的模型观察仍保留原事实；修改说明定位的是其上下文供给关系。获取结果的 `omit_result_range_at_use` 与获取动作分开。

获取端能力只采用可选且已审查的真实请求—响应关系：实际请求输入槽、选择参数路径、精确返回范围以及理由和证据。报告保留接受、拒绝、未决决定；只有接受的精确范围可以成为支持的选择范围。整个返回值的能力不能自动推导任意子字段能力，不合成服务器查询、参数值或联合选择掩码。缺少关系表示“材料未建立”，不是证明接口不支持。

CFG 中的资源或字段名常量如果没有实际消费或元数据需求绑定，不会仅因无正向需求而报告可删。确切 `operand_refs` 可保留必需的位置身份；缺少绑定时仅该输入范围未决，并列出 CFG／标注位置、缺少的关系和补齐方式。

## 离线证据

下列均为各自范围的测试收据，重叠用例不能相加。集成验证由主代理另行记录。

| 收据 | 结果 | 范围 |
|---|---:|---|
| `constraints-report-focused.xml` | 125 通过、1 失败 | 初次扩展回归；一个当前测试样例仍声明 demand-v8，失败原样保存 |
| `constraints-report-focused-final.xml` | 126 通过 | 更新该当前样例为 demand-v9 后的需求、敏感性、约束、报告和新接口回归 |
| `input-locations-source-errors-final.xml` | 46 通过 | 源文错误、位置／修改方案、获取能力及原约束保持和补充验收 |
| `typed-input-report-final.xml` | 45 通过 | 最终类型、位置、源文错误和范围化未决标记验证 |

关键新增测试包括：

- `test_known_source_defect_preserves_actual_inputs_and_reports_without_invented_slot`：整个参数缺失、字段缺失、错用字段分别报告，实际输入及观察记录保持不变。
- `test_flat_call_one_source_defect_projects_exact_request_action_and_response_output`：真实调用配对与统一错误身份。
- `test_known_source_error_is_not_a_demand_seed_and_disjoint_output_stays_exact`：源文错误不自行产生需求，不污染独立输出。
- `test_saved_edit_recipes_and_locations_are_rederived_from_bound_material`：拒绝篡改 CFG、源文、wire 或修改方案。
- `test_conditional_member_locations_follow_recorded_slot_mapping`：条件成员和控制槽位定位。
- `test_acquisition_projection_requires_exact_reviewed_pair_range_and_real_request_operand`：无能力记录、精确能力及不支持的子字段推断。
- `test_field_name_literal_without_metadata_binding_is_local_unresolved_not_deletable`、`test_read_resource_identity_is_retained_only_through_exact_location_binding`：元数据参数不误删。
- `test_bounded_information_requires_scoped_review_origin_and_exact_ancestry`：范围化未决必须保持 conservative，绑定审查收据，沿允许的规则追溯到局部语义缺口；拒绝无依据循环和泛化处理，允许合并已有确定性父关系。

范围化标记 `information_bound` 默认不出现，仅在有审查依据的明确属性范围使用。它区分“此属性是否必要仍未决”与“不知道影响范围”。程序核对结构和证据关系；语义理由是否成立仍属于源文审查职责。这些注入答复的离线测试不构成真实模型准确率、语义等价或全局最小性证明。

本轮没有自动修改 Skill，不猜测没有源文依据的正确输入，不给未证实的获取端裁剪能力生成调用，也没有复跑已封存的真实实验。

## 同一接收位置的局部限制补充

后续只读审查发现一个已复现的局部性问题：`body` 必需、`y` 的关系未决、`token` 明确无关时，输入评估已支持删除 `token`，但敏感性比较仍复制整个接收位置的限制，导致三种 `y` 属性（值、存在性、数量）全部误阻断 `token` 的结论。失败收据 `scoped-sensitivity-repro.xml` 保留 3 个失败。

修正后，敏感性结果 v8 的每条比较保存 `limitation_refs`。泛化材料限制继续保留；输入契约限制只沿与该敏感范围重叠的实际需求祖先适用。接收位置的整体限制表、全部需求引用和全局 partial 状态不减少。加载验证重新计算每条比较的限制，拒绝加入不相关限制或删去相关限制。显示层分别呈现比较范围与边界整体限制。

`scoped-sensitivity-final.xml` 中 64 项通过，包括新增 6 项和既有敏感性、约束保持、报告、补充验收。新增用例同时验证：无关 `token` 可删、`y` 自身仍受阻、一般分析限制仍阻断、限制引用篡改被拒绝以及报告没有把整份部分结果显示成完全结论。此收据仍为限定范围回归，不代替主代理的集成验收。
