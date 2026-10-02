# SkillFlow 一键 Pipeline 中文说明

在仓库根目录运行当前 SkillFlow pipeline。

默认 `all` 流程：

1. 列出并下载 ClawHub 下载量前 `k` 个 skill zip。
2. 对下载的 zip 运行 SFG 分析(Python,`python -m skill_sfg.batch`)。
3. 对生成的 SFG JSON 运行 DOE 分析(JS)。

Similarity grouping 默认不运行；只有传入 `--with-similarity` 或 `--phase download-group` 时才运行。

> **命名说明**:图引擎品牌层已更名(FCG→**SFG**),但运行时**保留**了内部选择器与目录:`--phase fcg`/`--phase doe` 选择器、输出目录 `fcg/`/`doe/`、汇总文件 `fcg-summary.*`/`doe-summary.*` 均不变;SFG 侧单 skill 文件后缀为 `-sfg.json`、环境变量前缀 `SFG_*`,DOE 侧保持 `-doe.json` 后缀。SFG 是 Python(`packages/skill-sfg`),DOE 仍是 JS(`packages/skill-doe-analyzer`)。

## 快速开始

先在仓库根目录创建 `.env`。SFG Markdown 语义门控和 DOE LLM judge 默认运行，因此正常 `all` 流程需要 `LLM_API_KEY`。

```dotenv
LLM_API_KEY=<your-key>
LLM_PROVIDER=openai
LLM_ENDPOINT=https://xiaomuai.cn/v1/chat/completions
LLM_MODEL=gpt-5.5
LLM_TIMEOUT=180000
```

> `LLM_TIMEOUT` 默认 180000(3 分钟)。DOE 的 judge 单次真实延迟约 50–100s(gpt-5.5),过低的超时(如旧默认 30s)会在重试循环里静默卡死整批。

运行：

```powershell
cd D:\projects\SkillFlow
node scripts\skillflow-pipeline.js --k 100
```

PowerShell 包装脚本：

```powershell
.\run-skillflow-pipeline.ps1 -K 100
```

Dry run 只打印解析后的命令，不需要 LLM key：

```powershell
node scripts\skillflow-pipeline.js --k 100 --dry-run
```

## 输出

配置里的 root 前缀是：

```text
D:\projects\SkillFlow\results\clawhub-top
```

实际输出目录会包含 `k`：

```text
D:\projects\SkillFlow\results\clawhub-top-k100
```

主要输出：

```text
<root>\zips\
<root>\fcg\skills\
<root>\fcg\fcg-summary.json
<root>\fcg\fcg-summary.md
<root>\doe\skills\
<root>\doe\doe-summary.json
<root>\doe\doe-summary.md
```

## 配置

高级参数位于：

```text
skillflow-pipeline.config.cjs
```

常用 CLI 参数：

- `--root <dir>`：输出 root 前缀或显式 `-k` root。
- `--phase download|fcg|doe|all|download-group`：只运行某个阶段。默认 `all` 表示 download、SFG、DOE 三阶段。（阶段选择器 `fcg`/`doe` 是保留的内部标识,分别对应 SFG/DOE 阶段。）
- `--with-similarity`：在下载阶段运行 similarity grouping。`download-group` 是兼容别名。
- `--semantic-llm`：只启用 similarity grouping 阶段的 semantic LLM。
- `--dry-run`：只打印解析后的配置和子命令。

SFG 提取(现为 Python,`packages/skill-sfg`)会先判文件类型（指令文档 vs changelog/license 等非指令文档）与内容块类型（代码块/表格/列点/散文/免责声明），再派发对应的规则策略——shell 代码块经共享 `shell-command-classifier` 逐命令建 sink，脚本调用按角色分类（丢内建、保留未知用户函数），否定/免责声明降为 guard/context，列表切块处理（多行 bullet 合并、继承 lead-in 免责作用域）。文档步骤间的顺序边默认**同节内**连;设 `SFG_SEQUENCE_EDGE_SCOPE=global` 可恢复旧的全文连接。在此之上，Markdown 语义抽取默认由 LLM 强门控：规则只生成候选，缺少 `LLM_API_KEY` 时 SFG/pipeline 预检失败。默认会尽量复核全部文档候选；`SFG_MAX_DOC_FLOW_NODES` 未设置或设为 `0` 表示 unlimited，只有设为正整数时才作为显式安全上限。吞吐和缓存可用 `SFG_SEMANTIC_GATE_BATCH_SIZE`、`SFG_SEMANTIC_GATE_MAX_BATCH_CHARS` 和 `SFG_SEMANTIC_GATE_CACHE` 调整。（Python 端逐批**顺序**执行语义门控,因此没有并发旋钮——旧的 `FCG_SEMANTIC_GATE_CONCURRENCY` 已不存在。）

语义门控缓存现在固定在 `<root>/fcg/semantic-gate-cache.jsonl`（沿用内部 `fcg/` 目录名,不再放在全局临时目录），使重跑及其他机器/CI 能复用此前的语义判定、对未变文档跳过远程模型调用。可用 `fcg.semanticGateCache`（保留的内部配置键,或 `--semantic-gate-cache`）覆盖路径，设为 `0`/`false` 可禁用。语义抽取逻辑本身不变——缓存命中返回的是当初模型对该节点给出的同一判定，抽取质量完全一致，只是降低了耗时。

DOE LLM judge（仍为 JS,`packages/skill-doe-analyzer`）默认开启，除非在配置或 DOE batch 命令中显式关闭，否则也需要 `LLM_API_KEY`。judge 的送审是**敏感度驱动**的：只有跨边界、且（高敏感度兜底 || 中敏感度且 `potential_doe`）的 unit 才送 LLM,其中 `potential_doe` = `暴露 ∧ 必要性 < 0.7`（`DEFAULT_NECESSITY_THRESHOLD=0.7`）。每个入选 assessment 先做 1 票 LLM 判断；只有高风险、不确定或需要复核的 unit 才追加 3 票 median 复判。可在 `skillflow-pipeline.config.cjs` 中调整 `doe.llmConcurrency`、`doe.llmEscalationVotes`、`doe.llmEscalationPolicy` 和 `doe.llmMaxBatchChars`（`doe.*` 是保留的内部配置键前缀）。

为避免大证据导致的上下文超长/超时，DOE 对每个 evidence pack 采用分层、且不损失准确性的尺寸控制：

- 字符数在 `doe.evidenceMaxPackChars`（默认 100000）以内的 pack 原样发送、携带完整证据，与不做尺寸控制时逐字节一致，判定结果不变。
- 偏大但仍可发送的 pack 会按体积放大请求超时（上限为 `doe.adaptiveTimeoutMaxMs`，默认 4 倍基础超时），让它以完整内容完成判定，而不是被裁剪。
- 只有仍超过上限的 pack——这些在当前实现下会超长、超时并导致整个 skill 的 DOE 结果丢失——才会被裁剪：先做无损精简，再对中间 flow 路径节点做首尾窗口保留（`doe.evidencePathNodeWindow`，默认 4），并始终保留边界节点与路径首尾节点，最后再施加文本/数组上限（`doe.evidenceMaxTextChars`、`doe.evidenceMaxArrayItems`）。这类 unit 会被标记 `requires_review` 并计入 `llm_fallback_count`。由于这只会影响当前本就会完全丢失的 pack，因此相对现状准确性绝不会下降。

如果某次 LLM 调用在裁剪和重试后仍失败（例如持续超时），该单个 unit 会降级为 rule-only 评分并标记 `requires_review=true`，而不会让整个 skill 崩溃——见 `statistics.llm_fallback_count` / `llm_fallback_units`。

瞬时传输失败（请求超时、网络 reset/DNS、HTTP 429、HTTP 5xx）会以有界指数退避 + 抖动重试，并遵守 `Retry-After`。鉴权/4xx（429 除外）和 schema 错误不重试、快速失败。两个引擎共用同一套传输重试逻辑——DOE 侧在 `shared/llm-utils.cjs`,SFG 侧在 `skill_sfg/llm/transport.py`。可用 `LLM_MAX_RETRIES`（默认 2）、`LLM_RETRY_BASE_MS`（默认 500）、`LLM_RETRY_MAX_BACKOFF_MS`（默认 8000）调整。

如果 OpenAI-compatible endpoint 的 DNS 不稳定，或较大的 HTTP/1.1 请求会被 reset，可以在运行 DOE 或完整 pipeline 前设置 `LLM_HTTP2=1`；必要时再设置 `LLM_ENDPOINT_RESOLVED_IP=<ip>` 固定连接 IP。

## 示例

只下载 zip：

```powershell
node scripts\skillflow-pipeline.js --k 100 --phase download
```

下载并按 similarity 分组，然后在 FCG 前停止：

```powershell
node scripts\skillflow-pipeline.js --k 100 --phase download-group
```

对已有 `<root>\zips` 或 similarity 输出运行 SFG（阶段选择器仍为 `fcg`）：

```powershell
node scripts\skillflow-pipeline.js --k 100 --phase fcg
```

对已有 `<root>\fcg\skills` 运行 DOE（阶段选择器仍为 `doe`）：

```powershell
node scripts\skillflow-pipeline.js --k 100 --phase doe
```

运行完整 pipeline，并启用可选 similarity grouping：

```powershell
node scripts\skillflow-pipeline.js --k 100 --with-similarity
```

直接运行 SFG batch（Python）：

```powershell
cd packages\skill-sfg
python -m skill_sfg.batch --root ..\..\results\clawhub-top-k100
```

直接运行 DOE batch（JS,脚本内部名仍为 `doe-batch.js`）：

```powershell
node packages\skill-doe-analyzer\scripts\doe-batch.js --root results\clawhub-top-k100
```

## 测试

全绿共 213 测试。SFG 现为 Python(135 pytest)：

```powershell
python -m pytest packages/skill-sfg/tests
```

DOE 与 similarity 仍为 JS(58 + 20)：

```powershell
node --test "packages/skill-doe-analyzer/test/**/*.test.js" "packages/skill-similarity-analyzer/test/**/*.test.js"
```

仓库根 `test/` 只放 pipeline/env 传输层测试:

```powershell
node --test "test/**/*.test.js"
```
