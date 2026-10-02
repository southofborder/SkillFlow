# Skill Similarity Analyzer

`skill-similarity-analyzer` downloads and groups OpenClaw Skill zip packages for independent corpus sampling. Grouping reads only each package's `SKILL.md` and optional `README.md`, then writes folders containing copies of the original zip packages. Selected packages can be analyzed individually with `skill-ir`.

This optional sampling utility is separate from the current Skill-IR analysis and controlled semantic review workflow. Its similarity scores are sampling aids, not semantic fidelity or security judgments.

## Requirements

- Node.js `>=18`
- npm

Install dependencies:

```bash
npm install
```

Run tests:

```bash
npm test
```

## CLI Usage

```bash
node src/index.js group <zip-or-dir...> --output <dir> [--semantic-llm] [--threshold <n>] [--top-k <n>]
```

Example:

```bash
node src/index.js group "D:\datasets\skill-zips" --output "D:\datasets\skill-groups"
```

You can pass one or more zip files and/or directories:

```bash
node src/index.js group skill-a.zip skill-b.zip "D:\datasets\more-zips" --output grouped-skills
```

Show help:

```bash
node src/index.js --help
```

## Options

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| `--output <dir>` | Yes | none | Output directory for `grouping.json`, `grouping.md`, grouped zip folders, and ungrouped zips. |
| `--threshold <n>` | No | `0.68` | Similarity threshold in `[0, 1]`. A pair with `similarity_score >= threshold` becomes an edge in the grouping graph. Lower values create larger/noisier groups; higher values create smaller/stricter groups. |
| `--top-k <n>` | No | `20` | Per-skill number of highest rule-score candidate pairs kept for reporting and optional semantic LLM refinement. |
| `--semantic-llm` | No | off | Enables model-based refinement for Top-K candidate pairs. Requires `LLM_API_KEY`; if unavailable or a call fails, rule scores are kept and the issue is recorded in `errors`. |
| `--help`, `-h` | No | off | Prints CLI usage. |

## Inputs

Each input can be:

- A `.zip` Skill package.
- A directory containing `.zip` Skill packages. Directories are scanned recursively.

The analyzer reads the shallowest matching files inside each zip:

- `SKILL.md` is required.
- `README.md` is optional.

If `SKILL.md` is missing, the zip is skipped and recorded in `errors`. If `README.md` is missing, the Skill still participates in grouping and is marked with `readme_missing: true`.

The directory scan skips common generated or output folders such as `node_modules`, `.git`, `groups`, and `ungrouped`.

## Outputs

The output directory has this structure:

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

Machine-readable full result. Main fields:

- `meta`: analyzer version, threshold, Top-K, semantic LLM flag, output directory.
- `skills`: parsed Skill metadata and extracted document profile.
- `similarity_pairs`: reported pair scores and score components.
- `groups`: generated groups, representative Skill, average similarity, and members.
- `ungrouped`: valid Skills that did not connect to any group.
- `statistics`: counts for zips, valid Skills, invalid Skills, pairs, groups, and ungrouped Skills.
- `errors`: invalid inputs, missing `SKILL.md`, or LLM fallback records.

### `grouping.md`

Human-readable summary of groups, members, ungrouped Skills, and errors.

### `groups/group_*/group_manifest.json`

Per-group manifest. It records:

- group id
- representative Skill
- average similarity
- copied zip names
- original zip paths
- `SKILL.md` and `README.md` entry paths inside each zip
- pairwise similarity evidence inside the group

## Analyze a Selected Package With `skill-ir`

Install the current analyzer from the repository root:

```powershell
python -m pip install -e packages/skill-ir
```

Choose one of the copied zip packages and pass that package to the analyzer:

```powershell
python -m skill_ir analyze --input "D:\datasets\skill-groups\groups\group_001\skill-a.zip" --output "D:\datasets\skill-analysis\skill-a.json"
```

This command performs model-based extraction and uses the configured API credentials. The `--input` value is a single Skill zip or unpacked Skill package, not the grouping output root or `grouping.json`. Grouping and downloading do not invoke `skill-ir` automatically. See the [Skill-IR usage and review documentation](../skill-ir/README.md) for offline candidates, rendering, and controlled semantic review.

## ClawHub Top Skills Automation

Download the top ClawHub Skills by popularity and group them in one run:

```powershell
npm run clawhub-top -- --semantic-llm
```

Recommended repo-root `.env`:

```dotenv
LLM_API_KEY=your_api_key
LLM_PROVIDER=openai
LLM_ENDPOINT=https://xiaomuai.cn/v1/chat/completions
LLM_MODEL=gpt-5.5
LLM_TIMEOUT=30000
```

Defaults:

- `--k <n>` / `-k <n>` controls how many top skills to process; `--limit <n>` is also supported.
- `--limit 10000`
- `--root D:\projects\SkillFlow\results\clawhub-top10000`
- `--sort downloads`
- `--top-k 5`
- `--download-concurrency 8`
- `--llm-concurrency 2`
- `--phase all`

Output layout:

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

Useful staged runs:

```powershell
npm run clawhub-top -- --k 500 --phase list
npm run clawhub-top -- --k 500 --phase download
npm run clawhub-top -- --k 500 --phase group --semantic-llm
```

The downloader resumes from `manifests/downloads.jsonl` and skips already valid zip files. Similarity LLM calls are cached in `similarity/semantic-cache.jsonl`.

## How Similarity Works

The analyzer builds a document profile for every valid Skill package. The profile is derived from:

- front matter fields from `SKILL.md`, especially `name` and `description`
- `SKILL.md` body
- optional `README.md` body
- Markdown headings
- functional action tags
- platform/tool tags
- input/output object tags
- frequent domain terms
- polarity claims such as allow, require, deny, avoid, and only constraints

It then computes rule-based pair scores. TF-IDF and tag overlap are used as a recall layer; polarity conflicts can reduce the score when two documents talk about the same action/object but express opposite constraints.

| Component | Weight | Meaning |
| --- | ---: | --- |
| TF-IDF cosine | `0.50` | Text-level semantic distance over tokenized Skill and README content. |
| Title/description Jaccard | `0.20` | Overlap in Skill name, description, and headings. |
| Functional action Jaccard | `0.15` | Overlap in actions such as analyze, generate, query, visualize, test, design, extract, compare, execute, and write. |
| Platform/tool Jaccard | `0.10` | Overlap in platform or tool tags such as database, browser, GitHub, OpenAI, DashScope, spreadsheet, image, audio, finance, and dotted tool namespaces. |
| Input/output object Jaccard | `0.05` | Overlap in data object tags such as file, URL, text, image, table, database, report, credential, user info, and code. |

The base rule score is the weighted sum:

```text
base_rule_score =
  0.50 * tfidf_cosine +
  0.20 * title_description +
  0.15 * action_tags +
  0.10 * platform_tags +
  0.05 * io_objects
```

The final rule score applies a contradiction penalty:

```text
rule_score = max(0, base_rule_score - contradiction_penalty)
```

The contradiction layer detects cases such as:

- `send files to an external API` vs `do not send files externally`
- `read credentials` vs `never read credentials`
- `I like watching TV` vs `I do not like watching TV`

Penalty levels:

| Penalty | Meaning |
| ---: | --- |
| `0.15` | Soft constraint conflict, such as broad `only` versus broader allow. |
| `0.35` | Clear allow/require versus deny conflict on the same action or object. |
| `0.50` | High-risk conflict involving external sending, execution, credentials, secrets, user information, or similar sensitive objects. |

The semantic distance is:

```text
semantic_distance = 1 - similarity_score
```

Pair outputs include `components.contradiction_penalty` and `components.polarity_conflicts` so the grouping decision can be inspected.

## Grouping Algorithm

1. Compute similarity for all Skill pairs.
2. Keep edges where `similarity_score >= threshold`.
3. Build an undirected graph from those edges.
4. Use connected components as groups.
5. Components with a single Skill are written to `ungrouped/`.
6. Each multi-Skill component becomes `groups/group_XXX/`.

This means transitive similarity can place multiple related Skills in the same group even when not every pair in the group is above threshold.

## Optional Semantic LLM Refinement

By default, the analyzer is fully offline and deterministic.

When this package's `--semantic-llm` is enabled:

1. Rule scores are computed first.
2. For each Skill, only its Top-K rule candidates are selected.
3. The model receives structured summaries only, not full raw documents.
4. The model returns JSON with `similarity`, `reason`, `has_contradiction`, and `contradiction_reason`.
5. The final score first blends rule and LLM scores:

```text
similarity_score = 0.75 * rule_score + 0.25 * llm_score
```

If `has_contradiction=true`, an additional `0.35` LLM contradiction penalty is applied after blending. This prevents textually similar but semantically opposite Skills from forming a group.

If the API key is missing, the request fails, or the model returns invalid JSON, the analyzer keeps the rule score and records the fallback in `errors`.

LLM environment variables:

| Variable | Default | Description |
| --- | --- | --- |
| `LLM_API_KEY` | none | Required when `--semantic-llm` is enabled. |
| `LLM_PROVIDER` | `openai` | Provider selector. Use `openai` for XiaoMuAI/OpenAI-compatible gateways, or `dashscope` for DashScope-compatible endpoints. |
| `LLM_MODEL` | `gpt-5.5` | Default chat model. Switch to `deepseek-v4-pro` if gateway validation fails. |
| `LLM_ENDPOINT` | `https://xiaomuai.cn/v1/chat/completions` | Explicit OpenAI-compatible chat completions endpoint. |
| `LLM_TIMEOUT` | `30000` | Request timeout in milliseconds. |
| `DASHSCOPE_ENDPOINT` | DashScope compatible endpoint | Optional DashScope endpoint override. |

Example:

```powershell
$env:LLM_API_KEY = "your_api_key"
$env:LLM_PROVIDER = "openai"
$env:LLM_ENDPOINT = "https://xiaomuai.cn/v1/chat/completions"
$env:LLM_MODEL = "deepseek-v4-pro"
node src/index.js group "D:\datasets\skill-zips" --output "D:\datasets\skill-groups" --semantic-llm
```

## Boundaries

- Only zip packages are analyzed. A raw unpacked Skill directory is not treated as a Skill input unless it contains zip packages to scan.
- Only `SKILL.md` and optional `README.md` are read from each zip.
- The analyzer does not execute package code.
- The analyzer does not construct CFGs or invoke `skill-ir`.
- The analyzer does not detect over-exposure, data leakage, or risk paths.
- Similarity groups support corpus selection independently of the main analysis and review workflow.
