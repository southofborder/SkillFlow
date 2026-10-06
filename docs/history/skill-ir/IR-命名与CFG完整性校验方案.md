# skill-ir 命名统一与第一阶段 CFG 校验

本文件替代此前方案中将可用性传播与审计候选接入第一遍编译的安排。
实施范围仅为 `packages/skill-ir`、其测试和示例展示；不迁就旧 SFG/DOE 格式。

## 阶段边界

第一遍建立 CFG，并验证结构、编号、读入形状和结果引用连通性。
语义回溯、effect 建模、沿路径累积数据处理历史及审计属于后续工作。
图结构自洽不等于行为覆盖完整，不证明所有路径可执行或最终返回。

## 已采用的接口

- `BasicBlock.instructions`、`data_source_kind`；`DataSourceKind` 类型。
- `declared_context_keys`；连边使用 `condition_text`。
- `produced_result_ids()`、`cross_block_result_ids()`、`read_context_keys()`、`result_semantic_names()`。
- 保留 `Operand`，使用 `identifier`、`semantic_name`、`literal_value`。
- 操作数类型为 `result`、`context_key`、`external_resource`、`literal`。
- 结果编号为 `result_004`，保留 `IRInstruction.id` 和 `ir_007` 格式。
- 指令使用 `metadata`、`draft_instruction_id`，`opcode` 保持语义字符串。

## Opcode 和 Prompt

删除 Opcode 枚举。业务操作没有白名单，不按 http_get/read_db 等拼写进行专有检查。
Prompt 固定 dispatch / return 的终结写法，校验其位置、输入与出边约束。
数据来源由块类别和操作数结构判断；read_context 仅是推荐语义名。
不新增 BasicBlock.terminator，也不拆分输入和输出模型。

## 校验与可用性辅助模块

`ir/validation.py` 负责第一阶段；`ControlFlowGraph.validate_integrity()` 是对外入口。
先收集全图产出，再逐条检查引用；跨块以产出块缓存可达性，不做结果集合传播。
支持单分支合流、回边引用、多入口；拒绝悬空关系、重复标识和不可达孤立环。
不分析 condition_text 的真假，不补边，局部先读后产出即使有回边仍拒绝。

已有集合分析独立放入 `availability.py`，入口 `analyze_availability()`，结果
`AvailabilityAnalysis`。保留独立测试，但第一阶段和图渲染不依赖它。
移除按 opcode 推断暴露候选的代码及旧 propagate 公共入口。

## 配套与验收

Prompt、完整示例、Schema、序列化、错误信息、公开导出、README 和测试同步更新。
错误信息保留编号和原语义名；图示优先显示语义名，再显示编号。
新增隔离测试，禁止导入 availability 后仍能编译、保存、读取、渲染。
三份示例只离线转换字段和引用编号，核对块、边和原响应没有改变。
该轮历史产物位置为 `results/ir/phase1/`；后续交付目录已调整为仓库直属的
`dataset/skills/` 与 `result/ir-IPP/`，冻结实验原始记录仍在实验源目录。
不将离线回归当作在线验证。

Candidate→Draft、CLI 参数和分析状态改名不属于本轮范围。

## 后续结构形式化

本方案记录第一阶段的工程边界。完整字段重验、结构规则矩阵与形式核心证明以
[Skill-IR结构规范与验证边界](Skill-IR结构规范与验证边界.md) 为当前补充规范。
形式核心不把业务操作名收紧为白名单，不解释条件真假，也不引入暴露审计。
