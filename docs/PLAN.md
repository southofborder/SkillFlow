# Skill → IR/CFG 独立分析器 v1

## 当前进度

截至 2026-09-07，`packages/skill-ir` 已实现显式来源、真实产出绑定和逐块转交规范。当前包测试为 115 个，全部通过。

已完成：

- 基础 `BasicBlock`、`IRInstruction`、`ControlFlowGraph` 模型和确定性校验；
- 开放字符串 Opcode；
- 必填语义字段 `BasicBlock.block_name`；
- 目录/ZIP Skill 包加载；
- Whole-Skill Prompt；
- Candidate Schema 和 Candidate → canonical IR/CFG 编译器；
- LLM 请求、解析、有限修复和 `complete/degraded` 降级；
- 离线固定候选 CLI、最小样例和测试覆盖。
- 上下文/外部数据 source 块、局部输出到上下文的绑定、逐块显式转交，以及对应的流程图展示。

本实现不导入、不修改、不接入旧 `skill-sfg`、DOE 或现有 pipeline。

## 目标流程

```text
Skill 包目录/ZIP
  ↓
完整无损读取可读文件
  ↓
Whole-Skill Prompt
  ↓
LLM 阅读完整包并识别行为单元
  ↓
Candidate IR + CFG
  ↓
确定性编译、SSA 规范化和 CFG 校验
  ↓
BasicBlock + ControlFlowGraph JSON
```

## 数据模型

### Skill 包

```python
class SkillPackage(BaseModel):
    root_name: str
    files: list[SkillFile]
```

```python
class SkillFile(BaseModel):
    path: str
    kind: Literal["markdown", "code", "text", "binary"]
    content: str | None
    size: int
```

目录和 ZIP 输入都会统一为正斜杠相对路径并稳定排序。ZIP 拒绝绝对路径、路径穿越和符号链接；单一顶层包装目录会被剥离。可读文件完整保留，二进制文件只保留大小和类型，不执行任何 Skill 代码。

### LLM Candidate

Candidate 是 LLM 的不可信中间结果，不直接作为最终 CFG：

```python
class CandidateInstruction(BaseModel):
    instruction_ref: str
    opcode: str
    inputs: list[Operand]
    outputs: list[Operand]
    meta: dict[str, Any]
```

```python
class CandidateBlock(BaseModel):
    block_ref: str
    block_name: str
    source_kind: Literal["context", "external"] | None
    context_exports: dict[str, str]
    context_passthrough: list[str]
    instructions: list[CandidateInstruction]
```

```python
class CandidateEdge(BaseModel):
    source_block_ref: str
    target_block_ref: str
    guard: str | None
```

```python
class IRAnalysisCandidate(BaseModel):
    entry_block_ref: str
    initial_context_keys: list[str]
    blocks: list[CandidateBlock]
    edges: list[CandidateEdge]
    diagnostics: list[str]
```

`block_ref` 和 `instruction_ref` 只用于 LLM 候选内部引用。`CandidateBlock.block_name` 是 LLM 提供的非空语义名称，编译后原样保存到最终 `BasicBlock.block_name`，不回退、不根据 `block_ref` 猜测。

最终 `block_id` 按候选顺序生成为 `block_001`、`block_002`；最终指令 ID 按块和指令的全局顺序生成为 `ir_001`、`ir_002`。局部 SSA 值按定义顺序规范化为 `value_001`、`value_002`。指令保留 LLM 的 `instruction_ref` 作为 `llm_ref` 调试字段。

`context_exports` 绑定“上下文名称 → 本块实际局部输出”，编译时与 SSA 名称同步改写。`context_passthrough` 明确列出本块接收后原样转交的键，不产生新值；同一个键不能同时导出和原样转交。

候选不再独立声明 `context_requires/context_provides`。最终 `BasicBlock` 保留这两个摘要：需求由实际 `context_ref` 消费和转交推导，提供由导出和转交推导；读取保存的 CFG 时会验证摘要与真实操作一致。

`source_kind="context"` 块以 `read_context` 读取 `initial_context_keys` 中声明的原始输入，再通过实际输出和导出绑定将其引入 CFG。初始键声明不能直接满足普通块的消费。`source_kind="external"` 表示实际读取文件、配置或外部返回数据；每个 source 块只含一次读入动作和终结指令，可产生多个值。`http_get/read_db` 必须是外部 source 的读入操作，其他开放 opcode 的读入分类由 prompt 约束。

本 v1 不包含 `EvidenceRef`、`evidence`、`source_refs`、上下文证据映射或文件行号审计契约。

## Prompt 与语义规则

`build_whole_skill_prompt(package)` 会完整展示所有可读文件，并使用明确的 `<skill-file>` 边界；二进制只展示元数据。Prompt 要求 LLM：

1. 阅读完整 Skill 包后再分析；
2. 文本和代码默认独立推断；
3. 只有文本明确指代代码时才联合解释；
4. 从动作句、步骤、条件和工具描述中提取行为；
5. 将代码文件或代码块视为黑盒，不拆解内部循环、局部变量或内部控制流；
6. 对代码行为尽可能在 `meta.script_content` 中保留原始代码正文；
7. 为每个行为单元生成 `block_name`、候选指令和控制流边；
8. 区分实际读入、计算产出和原样转交，按实际读入动作建立 source 块，条件读入留在对应路径；
9. 对 A→B→C 中的 B 明确列出后续仍需的 `context_passthrough`，即使 B 自己不消费；
10. 把实际分支条件依赖列入 `dispatch.inputs`，guard 文本仅作说明；
11. 严格只返回符合 Candidate Schema 的 JSON。Prompt 包含可直接编译的直线和分支完整示例。

非执行性许可证、历史记录、普通说明和示例不生成执行指令，除非上下文明确表示运行行为。

## 编译和降级

`compile_candidate(candidate, package)` 只做确定性结构处理：

- 校验 Candidate Schema、块引用、入口和指令引用；
- 生成稳定 block/instruction/SSA ID；
- 规范化同一块内的 `LOCAL_DEP`；
- 校验 source 形状、原始输入声明及真实导出绑定，并同步规范化绑定中的 SSA 名称；
- 拒绝跨块或前向局部依赖；
- 校验 `DISPATCH` 必须有出边、`RETURN` 不得有出边；
- 校验边的源/目标存在、重复边和基本块终结符；
- 校验每个合流块的上下文需求由所有直接前驱提供；
- 拒绝漏传、自行转交未接收值、初始声明绕过 source、依赖后续循环迭代的首次输入；
- 保留独立行为组件，以主入口和无前驱块作为空上下文起点，拒绝这些起点均无法到达的孤立循环；
- 生成 `ControlFlowGraph`，不执行 Skill 代码，也不猜测缺失语义。

`analyze_skill()` 首次请求 LLM 后，最多进行 3 轮修复。每次修复都会把上一次原始响应、Candidate JSON 和确定性校验错误反馈给 LLM。最终结果为：

```python
class SkillAnalysisResult(BaseModel):
    status: Literal["complete", "degraded"]
    cfg: ControlFlowGraph | None
    raw_candidate: dict
    diagnostics: list[str]
    requires_review: bool
    prompt: str
    raw_response: str | None
    attempts: int
```

解析失败、Schema 错误或 CFG 校验超限会返回 `degraded`、`cfg=None`、`requires_review=True`，并保留最后一次原始响应和候选内容；不会生成伪造的可信 CFG。

`complete` 只说明显式结构和数据依赖通过校验，不证明开放 opcode、guard 文本或黑盒代码被正确理解。语义回溯、多文档相似度阈值及 DOE 接入留待后续处理。

## 流程图与兼容性

source 是参与控制流的真实块，流程图标识上下文/外部读入，展示 `产出 city ← value_001` 和 `接收 message → 原样转交 message`。服务、API 和路径等 `external_res` 仍是资源标识节点，纯发送操作无需虚构一次服务读入。

旧候选和缺少显式 source/export/passthrough 字段的保存结果需要重新生成；绘图器不补造来源。新格式中无害的旧版非字面操作数 `value: null` 仍会被规范化。

回归样例输入位于 `examples/echo_skill`、`examples/alert_skill` 和 `examples/simple_skill`。新分析和图保存到 `results/skill-ir-flowcharts/explicit-sources/`，原目录的旧结果保留用于对照。

2026-09-07 实测：Echo、Alert 均由新 prompt 在线生成，候选第 1 次通过。天气样例在线请求及单独重试遇到断连/连接重置，当前交付为明确标注的离线固定候选回归，在线生成验证仍未完成。结果目录的 README 与 index 记录生成方式及完整对照。

## CLI 和验证

安装包后可运行：

```powershell
python -m pip install -e packages/skill-ir
python -m skill_ir.analyze `
  --input examples/simple_skill `
  --output results/simple_skill-ir.json
```

无网络调试可使用固定候选：

```powershell
python -m skill_ir.analyze `
  --input examples/simple_skill `
  --candidate candidate.json `
  --output results/simple_skill-ir.json
```

LLM 客户端读取既有环境变量：`LLM_API_KEY`、`LLM_ENDPOINT`、`LLM_MODEL`、`LLM_TIMEOUT`；网络请求使用 OpenAI-compatible `chat/completions`，对超时、网络错误、429 和 5xx 做有限重试。

测试覆盖目录/ZIP、完整 Prompt、文本/代码独立行为、黑盒代码、开放 Opcode、`block_name` 保留、稳定 ID/SSA、局部依赖、CFG 结构、上下文合流、修复循环、降级结果、LLM 传输和离线 CLI。缺少完整 LLM 配置时只跳过网络请求测试，不影响固定候选测试。
