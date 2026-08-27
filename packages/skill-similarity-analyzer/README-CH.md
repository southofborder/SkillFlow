# Skill Similarity Analyzer 中文说明

`skill-similarity-analyzer` 用于按照功能相似度对 OpenClaw Skill 压缩包分组。它只读取每个 zip 包中的 `SKILL.md` 和可选 `README.md`，然后输出可直接交给 SFG 引擎(`skill-sfg`)继续做技能流图(Skill Flow Graph)分析的分组目录。

本模块不做过暴露判断、不做风险分析、不扫描代码，也不构建 SFG。

## 环境要求

- Node.js `>=18`
- npm

安装依赖：

```bash
npm install
```

运行测试：

```bash
npm test
```

## CLI 使用

```bash
node src/index.js group <zip-or-dir...> --output <dir> [--semantic-llm] [--threshold <n>] [--top-k <n>]
```

示例：

```bash
node src/index.js group "D:\datasets\skill-zips" --output "D:\datasets\skill-groups"
```

也可以同时传入多个 zip 文件或目录：

```bash
node src/index.js group skill-a.zip skill-b.zip "D:\datasets\more-zips" --output grouped-skills
```

查看帮助：

```bash
node src/index.js --help
```

## 参数开关

| 参数 | 必需 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `--output <dir>` | 是 | 无 | 输出目录，用于保存 `grouping.json`、`grouping.md`、分组后的 zip 目录和未分组 zip。 |
| `--threshold <n>` | 否 | `0.68` | 相似度阈值，范围为 `[0, 1]`。当一对 Skill 的 `similarity_score >= threshold` 时，会在分组图中建立一条边。阈值越低，分组越大但噪声可能越多；阈值越高，分组越严格。 |
| `--top-k <n>` | 否 | `20` | 对每个 Skill 保留规则相似度最高的 Top-K 候选 pair，用于结果报告和可选的语义 LLM 复核。 |
| `--semantic-llm` | 否 | 关闭 | 启用模型语义复核。需要设置 `LLM_API_KEY`；如果没有 key、调用失败或返回非法 JSON，会保留规则分数并把问题记录到 `errors`。 |
| `--help`、`-h` | 否 | 关闭 | 打印 CLI 使用说明。 |

## 输入规则

每个输入可以是：

- 一个 `.zip` Skill 压缩包。
- 一个包含 `.zip` Skill 压缩包的目录。目录会被递归扫描。

分析器会读取 zip 内最浅层匹配的文件：

- `SKILL.md` 是必需文件。
- `README.md` 是可选文件。

如果缺失 `SKILL.md`，该 zip 会被跳过并记录到 `errors`。如果缺失 `README.md`，该 Skill 仍然参与分组，并在结果中标记 `readme_missing: true`。

目录扫描会跳过常见生成目录或输出目录，例如 `node_modules`、`.git`、`groups`、`ungrouped`。

## 输出结构

输出目录结构如下：

```text
output/
  grouping.json
  grouping.md
  groups/
    group_001/
      skill-a.zip
      skill-b.zip
      group_manifest.json
    group_002/
      skill-c.zip
      skill-d.zip
      group_manifest.json
  ungrouped/
    skill-x.zip
```

### `grouping.json`

完整的机器可读结果，主要字段包括：

- `meta`：分析器版本、阈值、Top-K、是否启用语义 LLM、输出目录。
- `skills`：解析到的 Skill 元数据和文档画像。
- `similarity_pairs`：输出的 pair 相似度分数和分数组件。
- `groups`：生成的分组、代表 Skill、平均相似度和成员。
- `ungrouped`：没有进入任何分组的合法 Skill。
- `statistics`：zip 数、合法 Skill 数、非法 Skill 数、pair 数、分组数、未分组数等统计。
- `errors`：非法输入、缺失 `SKILL.md`、LLM fallback 等记录。

### `grouping.md`

面向人工阅读的分组摘要，包括每组成员、未分组 Skill 和错误信息。

### `groups/group_*/group_manifest.json`

每个分组自己的 manifest，包含：

- group id
- 代表 Skill
- 组内平均相似度
- 复制后的 zip 文件名
- 原始 zip 路径
- 每个 zip 内 `SKILL.md` 和 `README.md` 的入口路径
- 组内 pair 相似度证据

## 与 `skill-sfg` 衔接

分组完成后，对运行根目录跑 SFG 分析。SFG 批处理会从 `similarity/grouping.json`(或 `<root>/zips`)发现待分析 skill，因此把它指向相似度阶段写入的同一个运行根目录：

```powershell
cd packages\skill-sfg
python -m skill_sfg.batch --root D:\projects\SkillFlow\results\clawhub-top-k100
```

若只想直接分析单个 skill 目录或 zip，用 CLI 入口：

```powershell
python -m skill_sfg.cli analyze "D:\datasets\skill-groups\groups\group_001\skill-a.zip" --output skill-a-sfg.json
```

分组目录中复制的是原始 zip 包，因此同一个运行根目录可直接喂给 SFG 批处理。

## ClawHub 热门 Skills 自动化

一条命令抓取 ClawHub 热门 Skills、下载 zip，并进行相似度分组：

```powershell
npm run clawhub-top -- --k 500 --semantic-llm
```

推荐在仓库根目录使用 `.env`：

```dotenv
LLM_API_KEY=your_api_key
LLM_PROVIDER=openai
LLM_ENDPOINT=https://xiaomuai.cn/v1/chat/completions
LLM_MODEL=gpt-5.5
LLM_TIMEOUT=30000
```

常用参数：

- `--k <n>` / `-k <n>`：处理下载量最高的前 n 个 Skills。
- `--limit <n>`：兼容旧参数，等价于 `--k <n>`。
- `--root <dir>`：输出根目录，默认 `D:\projects\SkillFlow\results\clawhub-top10000`。
- `--sort downloads|stars|installs`：热度排序口径，默认 `downloads`。
- `--top-k <n>`：每个 Skill 进入 LLM 复核的候选 pair 数，默认 `5`。
- `--download-concurrency <n>`：下载并发数，默认 `8`。
- `--llm-concurrency <n>`：LLM 复核并发数，默认 `2`。
- `--phase list|download|group|all`：只跑指定阶段或跑全流程，默认 `all`。
- `--non-suspicious-only`：只抓 ClawHub 标记为非可疑的 Skills。

输出结构：

```text
results/clawhub-top10000/
  zips/
  manifests/
    top-skills.json
    downloads.jsonl
    download-summary.json
  similarity/
    grouping.json
    grouping.md
    semantic-cache.jsonl
    groups/
    ungrouped/
```

分阶段运行示例：

```powershell
npm run clawhub-top -- --k 500 --phase list
npm run clawhub-top -- --k 500 --phase download
npm run clawhub-top -- --k 500 --phase group --semantic-llm
```

下载阶段会根据 `manifests/downloads.jsonl` 断点续跑，并跳过已经存在且合法的 zip。LLM 复核结果会缓存到 `similarity/semantic-cache.jsonl`，续跑时不会重复调用同一个 pair。

## 相似度实现原理

分析器会为每个合法 Skill 构建一个文档画像。画像来源包括：

- `SKILL.md` front matter，尤其是 `name` 和 `description`
- `SKILL.md` 正文
- 可选 `README.md` 正文
- Markdown 标题
- 功能动作标签
- 平台/工具标签
- 输入输出对象标签
- 高频领域词
- 极性声明，例如 allow、require、deny、avoid、only 等约束

随后对所有 Skill pair 计算规则相似度。TF-IDF 和标签重合主要负责召回；如果两个文档围绕同一动作/对象表达了相反约束，极性冲突层会降低分数。

| 组件 | 权重 | 含义 |
| --- | ---: | --- |
| TF-IDF cosine | `0.50` | 基于分词后的 Skill/README 文本计算文本级相似度。 |
| 标题/描述 Jaccard | `0.20` | Skill 名称、description 和标题的重合度。 |
| 功能动作 Jaccard | `0.15` | analyze、generate、query、visualize、test、design、extract、compare、execute、write 等动作标签的重合度。 |
| 平台/工具 Jaccard | `0.10` | database、browser、GitHub、OpenAI、DashScope、spreadsheet、image、audio、finance 以及 dotted tool namespace 等标签重合度。 |
| 输入输出对象 Jaccard | `0.05` | file、URL、text、image、table、database、report、credential、user info、code 等对象标签重合度。 |

基础规则分数公式：

```text
base_rule_score =
  0.50 * tfidf_cosine +
  0.20 * title_description +
  0.15 * action_tags +
  0.10 * platform_tags +
  0.05 * io_objects
```

最终规则分数会扣除语义冲突惩罚：

```text
rule_score = max(0, base_rule_score - contradiction_penalty)
```

极性冲突层会识别这类情况：

- `send files to an external API` vs `do not send files externally`
- `read credentials` vs `never read credentials`
- `I like watching TV` vs `I do not like watching TV`
- `读取用户凭据` vs `禁止读取用户凭据`

惩罚等级：

| 惩罚 | 含义 |
| ---: | --- |
| `0.15` | 轻微约束冲突，例如较宽泛的 allow 与 only 限定不一致。 |
| `0.35` | 明确的 allow/require 与 deny 冲突，且作用在相同动作或对象上。 |
| `0.50` | 高风险冲突，涉及外发、执行、凭据、密钥、用户信息等敏感对象或动作。 |

语义距离定义为：

```text
semantic_distance = 1 - similarity_score
```

pair 输出中会包含 `components.contradiction_penalty` 和 `components.polarity_conflicts`，便于人工检查为什么相似度被下调。

## 分组算法

1. 计算所有 Skill pair 的相似度。
2. 保留 `similarity_score >= threshold` 的边。
3. 用这些边构建无向图。
4. 用连通分量生成分组。
5. 只有一个 Skill 的连通分量进入 `ungrouped/`。
6. 至少两个 Skill 的连通分量进入 `groups/group_XXX/`。

这意味着分组具有传递性：即使组内不是每一对 Skill 都超过阈值，只要它们通过相似边连通，就会进入同一组。

## 可选语义 LLM 复核

默认情况下，分析器完全离线、规则可复现。

启用本包的 `--semantic-llm` 后：

1. 先计算规则相似度。
2. 对每个 Skill 只选择 Top-K 规则候选 pair。
3. 发送给模型的是结构化摘要，不是完整原始文档。
4. 模型返回包含 `similarity`、`reason`、`has_contradiction`、`contradiction_reason` 的 JSON。
5. 先融合规则分数和 LLM 分数：

```text
similarity_score = 0.75 * rule_score + 0.25 * llm_score
```

如果 `has_contradiction=true`，融合后会额外扣除 `0.35` 的 LLM 冲突惩罚，避免文本相似但语义目标相反的 Skill 进入同一组。

如果 API key 缺失、请求失败或模型返回非法 JSON，分析器会保留规则分数，并将 fallback 信息记录到 `errors`。

LLM 环境变量：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `LLM_API_KEY` | 无 | 启用 `--semantic-llm` 时必需。 |
| `LLM_PROVIDER` | `openai` | Provider 选择。接 XiaoMuAI 这类 OpenAI-compatible 网关时用 `openai`；只有接 DashScope compatible endpoint 时才需要 `dashscope`。 |
| `LLM_MODEL` | `gpt-5.5` | 默认 chat model。若网关稳定性验证失败，批准的回退模型是 `deepseek-v4-pro`。 |
| `LLM_ENDPOINT` | `https://xiaomuai.cn/v1/chat/completions` | 显式指定 OpenAI-compatible chat completions endpoint。 |
| `LLM_TIMEOUT` | `30000` | 请求超时，单位毫秒。 |
| `DASHSCOPE_ENDPOINT` | DashScope compatible endpoint | 可选 DashScope endpoint 覆盖。 |

示例：

```powershell
$env:LLM_API_KEY = "your_api_key"
$env:LLM_PROVIDER = "openai"
$env:LLM_ENDPOINT = "https://xiaomuai.cn/v1/chat/completions"
$env:LLM_MODEL = "deepseek-v4-pro"
node src/index.js group "D:\datasets\skill-zips" --output "D:\datasets\skill-groups" --semantic-llm
```

## 边界说明

- 只分析 zip 包。裸 Skill 目录不会被当作单个 Skill 输入，除非该目录中包含可扫描的 zip 包。
- 每个 zip 中只读取 `SKILL.md` 和可选 `README.md`。
- 不执行 Skill 包中的代码。
- 不调用 SFG 引擎(`skill-sfg`)。
- 不检测过暴露、数据泄露或风险路径。
- 极性冲突只用于降低相似度，不等价于完整的自然语言推理。
- 本模块的输出定位是后续 SFG 分析的预处理分组结果。

