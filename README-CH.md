# SkillFlow

针对 Agent Skill(ClawHub 上的可下载 skill 包)的**数据过度暴露(Data Over-Exposure, DOE)**静态分析流水线。

核心问题:一个 skill 在完成它声称的任务时,是否把**超出任务必要范围的敏感数据**送过了信任边界(外部 LLM、外部服务、持久化存储)?必要的暴露不算发现,不必要的才算——这是 SkillFlow 区别于普通污点分析(taint analysis)的关键。

> **命名说明**:图引擎品牌层已更名(FCG→**SFG**),但运行时**保留**了内部选择器与目录以免破坏契约——`--phase fcg`/`--phase doe` 选择器、输出目录 `fcg/`/`doe/`、连接契约 CLI(`--fcg`/`--fcg-root`)均不变;SFG 侧单 skill 文件后缀为 `-sfg.json`、环境变量前缀 `SFG_*`,DOE 侧保持 `-doe.json` 后缀与 `DOE_*` 前缀。package 布局:SFG 现在是 **Python**(`packages/skill-sfg`,用 `python -m skill_sfg.batch` 运行),DOE 仍是 **JS**(`packages/skill-doe-analyzer`)。
>
> 英文版见 [`README.md`](README.md)。

## 流水线概览

```text
ClawHub top-k  ──▶  1. 下载  ──▶  2. SFG 流图分析  ──▶  3. DOE 过度暴露评分
   (按下载量)        zips/         fcg/skills/*-sfg.json  doe/skills/*-doe.json
```

- **下载** — 抓取 ClawHub 下载量前 k 个 skill zip(复用 `packages/skill-similarity-analyzer`)。
- **SFG(Skill Flow Graph)** — 把每个 skill 解析成有向流图,叠加 `security_profile`(标签、标签流、边界观测)。提取时先判文件类型与内容块(代码块/表格/列点/散文/免责声明)再派发对应策略,规则优先、LLM 只兜底歧义。连边兼顾 recall(穷举类型兼容候选)与 precision(条件/guard 路由)。这是 DOE 的唯一输入。见 `packages/skill-sfg`(Python)。
- **DOE(Data Over-Exposure)** — 对每个 `(observation × label_flow)` 评估单元,以规则 + LLM 两层设计算 `exposure × (1 - necessity)`。见 `packages/skill-doe-analyzer`(JS)。

可选的 similarity grouping(`packages/skill-similarity-analyzer`)默认关闭。

## 快速开始

先在仓库根目录创建 `.env`(SFG 语义门控与 DOE LLM judge 默认运行,故需要 `LLM_API_KEY`):

```dotenv
LLM_API_KEY=<your-key>
LLM_PROVIDER=openai
LLM_ENDPOINT=https://xiaomuai.cn/v1/chat/completions
LLM_MODEL=gpt-5.5
LLM_TIMEOUT=30000
```

运行完整 pipeline:

```powershell
node scripts\skillflow-pipeline.js --k 100
```

或只跑某个阶段:

```powershell
node scripts\skillflow-pipeline.js --k 100 --phase fcg
node scripts\skillflow-pipeline.js --k 100 --phase doe
```

Dry run(只打印解析后的命令,不需要 LLM key):

```powershell
node scripts\skillflow-pipeline.js --k 100 --dry-run
```

## 各 package

| Package | 职责 |
| --- | --- |
| `packages/skill-sfg`(Python) | 建流图 + `security_profile`(阶段 2,DOE 唯一输入) |
| `packages/skill-doe-analyzer`(JS) | 逐评估单元给数据过度暴露打分(阶段 3,项目核心) |
| `packages/skill-similarity-analyzer`(JS) | 下载 ClawHub zip;可选的 README/SKILL 相似度分组 |

## 文档

- [`PROJECT-OVERVIEW-CH.md`](PROJECT-OVERVIEW-CH.md) — 完整项目总览:核心概念、三阶段流水线、SFG↔DOE 的 `security_profile` 契约、DOE 内部结构、鲁棒性、成本。(英文:[`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md)。)
- [`README-PIPELINE-CH.md`](README-PIPELINE-CH.md) — 一键 pipeline 参考:参数、阶段、环境变量、evidence 预算。(英文:[`README-PIPELINE.md`](README-PIPELINE.md)。)
- `skillflow-pipeline.config.cjs` — 高级配置。

## 测试

```powershell
# SFG 已是 Python(135 pytest):
python -m pytest packages/skill-sfg/tests
# DOE + similarity 仍是 JS(58 + 20):
node --test "packages/skill-doe-analyzer/test/**/*.test.js" "packages/skill-similarity-analyzer/test/**/*.test.js"
```

213 测试全绿(SFG 135 + DOE 58 + similarity 20)。仓库根 `test/` 只放 pipeline/env 传输层测试;核心用例在各 package 下。
