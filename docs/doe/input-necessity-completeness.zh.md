# 输入必要性补全：批次后设计与离线验收

更新：2026-11-11。**实现及离线验收已完成：2531 项通过、2 项跳过、0 项未解决失败。** 本文记录原始四例真实批次关闭后的修正，与[首轮输入必要性实现](input-necessity.zh.md)分开计量。

| 最终验收项 | 当前状态 |
| --- | --- |
| 当前测试身份的最新范围收据 | **2531 通过、2 跳过、0 未解决失败；不是一次全仓全绿执行** |
| 最终冻结实现 SHA-256 | `796240619b140cbb2c521d1ef00fb1dcae81aa0eed7acc6b79f692c194e5f5fa` |
| 最终冻结后的保存／加载／身份检查 | **37/37 通过，实现文件清单前后一致** |
| 修正后的真实模型验证 | **未运行；没有新增批次或重放** |

完整[验收报告](../../output/verification/input-necessity-completeness-20261111/assessment.zh.md)与[机器收据](../../output/verification/input-necessity-completeness-20261111/offline-acceptance.json)保留初始失败、定向复验及 3 个旧测试身份的明确替代。工作状态及新收据位于 [input-necessity-completeness-20261111](../../output/verification/input-necessity-completeness-20261111/continuation-state.json)。首轮的 2810 项通过、2 项跳过属于先前版本，不能作为本轮修正后的总数。本文不改变任何原始运行的结果或身份。

## 原始真实批次证明了什么

唯一批次 `20261111-173347` 的四个控制器及各自唯一一次零调用重放均已关闭。原始材料、选定版本审计和成本记录先封存，随后才修改生产代码。

| 用例 | 原始保存结果 | 生成 IR 的传播 | 与本轮修正有关的发现 |
| --- | --- | --- | --- |
| GA4 | revision-processing 超时失败；没有传播或 DOE | 未运行 | 选定初始标注有 45 个计算契约、0 个工具契约；遗漏整份工具契约仍能通过原有处理校验。 |
| 001 | DOE partial | 17/17 | 通知字段有明确需求；计数对象存在局部歧义，但整份计算契约未决使已知独立的成员载荷也被保留。另有全局任务及约束表达缺口。 |
| 010 | DOE partial | 20/20 | 审查错误地认为 `if_present=true` 未保留存在性，拒绝两条配对契约；原后端实际上已实现该标记的存在性语义。另有禁止删除要求的全局表达缺口。 |
| 013 | DOE partial | 25/25 | 具体结果判别、瞬态错误分类关系仍未决；清楚的重试／回退义务与缺少执行判别细节的区别需要澄清。原标注还保留未由响应结构说明支持的 `error` 字段映射疑点。 |

GA4 的选定初始 CFG 为 535 IR，修订候选为 658 IR；修订 processing 没有完成，不能把二者拼成成功传播结果。13 个远端调用、25 个 `saveResult` 及 3 个 URL 循环的源位置映射，只证明所列位置在图中的表示。[GA4 最终审计](../../output/verification/online-input-necessity-20261111/source-audit/ga4-final-source-coverage-audit.en.md)

三个小例原始结果均没有已认证的删除示例。001、010、013 的范围记录分别为 `393 required / 58 unresolved / 0 deletable`、`340 / 201 / 0`、`318 / 1004 / 0`；这些是推导范围行数，不是唯一字段数、泄漏数或准确率分母。`no_excess_established` 不能解释为安全结论。[001 审计](../../output/verification/online-input-necessity-20261111/small-source-audit/001-final-audit.md)、[010 审计](../../output/verification/online-input-necessity-20261111/source-audit/010-final-source-coverage-audit.en.md)、[013 审计](../../output/verification/online-input-necessity-20261111/small-source-audit/013-final-audit.md)

批次实际有 **47 次原生启动**，其中 46 次有完整公开用量、1 次 GA4 失败请求用量未知；已知公开总量 **2,967,050 tokens**。四次唯一重放均匹配，新增启动均为 0。匹配也包含复现失败终态，不会使失败或 partial 变为成功。费用封存的 canonical SHA-256 为 `9aaad6c38a9027c0af8912e1584fa61e62e87fecd8c016c040679e46f58745cc`；未知用量及供应商账单仍未知。[封存记录](../../output/verification/online-input-necessity-20261111/four-case-closed-cost-provenance-seal.json)、[成本说明](../../output/verification/online-input-necessity-20261111/four-case-closed-cost-provenance-summary.en.md)

## 契约不能通过整份遗漏绕过检查

程序现在从实际选定的操作、边界类型、真实输入槽和已验证表达式，独立生成预期契约清单。它不读取 Task 需求或敏感性来决定哪些契约应存在。

- 当前 guided 入口中的每个工具／远端 `call`、`deliver`、`receive` 都需要 `input_contract`，包括零输入接口；零输入使用明确的 `inputs: []`、理由及源文证据。
- 没有针对该操作的精确表达式的 `compute` 必须提供 `demand_transfer`。相邻操作或整条 CFG 指令上的表达式不能替它免责。没有新增公共表达式语法。
- 检查覆盖正常路径、候选、循环及词法作用域。配对的请求／响应保留各自精确坐标及共同的程序生成配对身份，相同载荷不能合并调用。
- 漏契约是定位到 processing 的结构错误，进入原有修正预算。确实缺少源事实时，需要显式、有证据的局部缺口，不能自动填入独立性或把当前所有字段当作必要。

旧手工／独立 raw 入口仍允许缺少附件，但这不产生语义接受或独立性证明。契约存在不会自行制造动作需求；单独的载荷信息目标也不会自动变成调用动作目标。履约动作仍由 Task correspondence 与源文审查交代，真正没有用途的整次调用不会因接口契约而被保留。

## 局部疑点与独立字段分开保存

每个实际输入仍逐一有一行，但现在可以同时表达三种信息：

| 字段 | 含义 |
| --- | --- |
| `required` | 有明确依据的必需信息；选择器为属性与路径。 |
| `unresolved_ranges` | 可选的明确未决范围，每项为 `{information, gap}`。 |
| `remainder` | 上述必需及未决范围之外的补集，声明 `independent` 或 `unresolved`。 |

例如同一个实际对象含有 `x`、`y`、`z`：`x` 必需、只有 `y` 的依赖关系未知、其余独立，就可以只保留 `x` 和未决的 `y`，让无其他用途且满足适用约束的 `z` 得到可删除结论。前向对象、操作数、可能依赖及观察记录全部保留。

所有局部及余下范围的 gap 现在要求 `code`、`reason`、`missing`、`resolution`、`evidences`。`resolution` 明确说明补充哪条关系或事实才能解决问题；通用的“不透明”“查看源码”不够。关键词校验只是结构底线，是否确实缺少该事实仍需独立审查。同一信息属性下，`each` 与具体数组下标相交的范围也不能重复分配给必要和未决声明。

计数／成员选择存在歧义，不意味着成员的收件人、正文或令牌值都会影响计数。经审查确认信息边界的局部缺口可保存 `information_bound`：结论仍然是保守、未决，但不得丢掉其 `cardinality`、`presence` 等属性而扩大为整份载荷。该标记只沿受支持的精确传递继承，保存结果检查其源头及祖先链；普通不透明变换不能继承这份精度。

敏感性比较另存逐范围的 `limitation_refs`，只把与当前范围重叠的需求祖先中的契约缺口应用到该比较。边界层的完整限制列表仍保留；例如同一接收位置中 `y` 未决，不再阻止已经独立核验的 `token` 得到可删除和 DOE 结论。一般材料／Task 限制仍按原规则处理，不因此被忽略。

输出仍按属性和路径精确匹配。整值规则不自动覆盖子字段；`output_parts` 是独立审查的完整分解声明，不由若干已有规则自动推断。未通过完整性审查的分解不能成为“改变此输入不会影响输出”的证明。

## 审查范围、可选字段与原始源码错误

第七个源文审查现在同时核对预期义务清单和实际附件，回执绑定这两者。`input_contract_checks` 每项绑定 `obligation_id` 与 `contract_id`；缺少附件时后者为空，不能被接受。完整接受可以覆盖明确列出的有限范围；拒绝或未决必须通过 `scope_checks` 完整划分必要信息、局部缺口、补集、输出规则及完整分解等范围。

较大范围的审查障碍不会默认污染所有输入。其实际影响的输入范围通过 `affected_scope_ids` 指明，并具有各自非接受的决定；其他有依据的范围可继续使用。未决审查同样需要具体 gap 和证据。processing 自己的声明、有效行号、findings 为空以及哈希一致，都不等同于语义正确。

`if_present=true` 的含义保持为：**无条件保留该字段的存在性，并在存在时保留所声明的信息；确定缺席时不要求一个不存在的值。** 审查视图明确展示这层含义，不再要求重复添加 presence 行。原始 010 的拒绝意见及其 partial 结果不回写；修正后的提示是否能稳定避免模型误判，不能由离线格式测试证明。

`source_input_findings` 另行记录已经由源码／接口证据确立的 `missing_argument`、`missing_field`、`wrong_field`。它区分所需参数与真实出现位置的证据，绑定实际输入或“整个参数缺席”，再明确影响哪些原生动作／输出信息。程序不会补造不存在的输入槽、Data 或 Task 目标，也不会把拒绝契约直接解释为 Skill 写错。忠实描述实际依赖可以与明确的源码调用缺陷同时存在。

Task 保持 v5 及 source-only 输入。清楚的条件重试、回退或状态追加义务，可以按原文抽象保留；仅缺少响应字段、分类器实现或序列化细节，不自动生成全局 Task 歧义。若不同源文解释改变真实义务或输出内容，仍保留已有 Task issue 及其全局政策。

## 所有输入都有定位，获取能力单独说明

报告为敏感及非敏感输入统一补充 CFG、raw／wire 操作使用位置、源文范围、候选／成员作用域和实际下游使用位置。只找到继承证据或标注位置时会明确记录，不能虚构源码列号或直接补丁。

已建立的修改说明包括 `remove_input`、`exclude_field`、保留必要及未决信息的 `keep_ranges`，以及获取结果在后续使用处的 `omit_result_range_at_use`。结构、顺序、数量和成员身份要求仍需保留；数组删除或重编号没有依据时，不输出一个看似可执行的方案。生成的模型观察若只有处理上下文位置，也不会伪装为可直接删除的源参数。

可选的 `input_contract.acquisition_projections` 单独声明获取接口能力，字段为 `selection_input_index`、`selection_parameter_path`、值属性的 `returned_range`、`reason`、`evidences`。它必须绑定真实请求输入及精确配对响应，并由 `input_projection_checks` 单独审查。缺少声明表示能力未建立；整值能力不自动覆盖任意子字段，多行能力不自动证明任意组合掩码。报告只呈现已支持的能力及范围，不生成服务器查询、参数值或自动改写 Skill。

## 版本与已保存的离线证据

本轮使用 profile/raw v23、compiler v14、flat wire／fragments v5、guided run v11、step／annotation v10、source-review fragment v4、input-contract receipt v2、demand result v9、sensitivity result v8、formal DOE run/format v9。原始批次仍使用其原冻结身份；未迁移旧结果。七次正常语义请求、两个 worker、既有修正／修复预算及各阶段隔离保持不变。

以下是已经保存的范围收据示例，**相互有重叠，不能相加作为总数，也不替代最终冻结后的整合验收**：

| 收据 | 通过数 | 范围 |
| --- | ---: | --- |
| [schema-compiler-final.xml](../../output/verification/input-necessity-completeness-20261111/schema-compiler-final.xml) | 175 | 模式、编译、片段和兼容性检查。 |
| [schema-selector-overlap-corrected.xml](../../output/verification/input-necessity-completeness-20261111/schema-selector-overlap-corrected.xml) | 32 | 强制契约、精确表达式、局部范围及 each／下标交叠。 |
| [scoped-review-confirmed.xml](../../output/verification/input-necessity-completeness-20261111/scoped-review-confirmed.xml) | 62 | 预期义务、范围审查、配对能力及不可变回执。 |
| [scoped-backend-corrected.xml](../../output/verification/input-necessity-completeness-20261111/scoped-backend-corrected.xml) | 7 | 局部反向传递及影响范围回归。 |
| [constraints-report-focused-final.xml](../../output/verification/input-necessity-completeness-20261111/constraints-report-focused-final.xml) | 126 | 需求、敏感性、限制保持、定位及源码输入错误。 |
| [demand-record-information-bound.xml](../../output/verification/input-necessity-completeness-20261111/demand-record-information-bound.xml) | 19 | 局部信息边界的保存格式及祖先验证。 |
| [small-alignment-contracts-final.xml](../../output/verification/input-necessity-completeness-20261111/small-alignment-contracts-final.xml) | 23 | 原有小例语义断言，补齐当前合成候选契约。 |
| [case-contract-fixtures-final.xml](../../output/verification/input-necessity-completeness-20261111/case-contract-fixtures-final.xml) | 22 | 成员、正常／异常候选、原有状态和配对断言。 |

初始失败收据均保留：包括旧合成候选缺契约、旧版本断言、测试误用不存在的公共表达式入口，以及 `each` 输入路径未经 JSON 规范化引起的真实序列化缺陷。修正及定向重跑另存，不删除初始失败记录，也不放宽当前入口的契约覆盖要求。

这些证据验证有限表示和确定性行为，不证明自然语言语义完备、全局最小性、模型审查准确率或不存在 DOE。最终验收状态、当前测试身份总数、明确替代关系及冻结哈希见本文开头和完整验收报告。
