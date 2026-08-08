# SkillFlow Project Overview

> Purpose: give collaborators the "what are we building, how far along, and at what granularity" picture, to align on scope and writing detail.
> Maintenance: this file describes the state as of 2026-07. Code under `packages/` is the source of truth. Chinese version: `PROJECT-OVERVIEW-CH.md`.

---

## 1. One-line positioning

SkillFlow is a static-analysis pipeline for **Data Over-Exposure (DOE)** in **Agent Skills** (downloadable skill packages on ClawHub). The core question it answers:

> When a skill performs the task it claims to perform, does it send **sensitive data beyond what the task actually needs** across a trust boundary (to an external LLM, an external service, persistent storage, etc.)?

It is not simply "did sensitive data flow out," but **"was this outflow necessary to complete the claimed task."** Necessary exposure is not DOE; only unnecessary exposure is. This is the key difference from ordinary taint analysis.

---

## 2. Research question and core concepts

| Concept | Meaning |
| --- | --- |
| **boundary observation** | An event where data crosses a trust boundary at some node (handing data to an LLM, sending it to an external API, writing it to storage) |
| **label** | Data sensitivity classification: `category.subtype` + `sensitivity` (low/medium/high/critical) |
| **label_flow** | The full path a labeled datum travels through the graph (**single-flow**: each flow traces to one true origin, ≤1 parent) |
| **assessment unit** | `(observation × label_flow)`, the finest DOE decision granularity |
| **exposure** | How "dangerous" this boundary crossing is in itself (boundary type, receiver scope, sensitivity) |
| **necessity** | How "necessary" this exposure is for completing the skill's claimed task |
| **DOE score** | `exposure × (1 - necessity) + baseline_adjustment` — higher means more over-exposed |

Necessity is composed of **3 components**; DOE necessity is the **minimum** of the three (the weakest link decides; see `COMPONENT_KEYS` in `necessity-baseline.js`):

- **`action_input_need`**: does this action's **input** really require data of this label (local)
- **`receiver_semantic_need`**: does the **receiver's** semantics really require this label (local)
- **`task_need`**: does the whole label_flow path + boundary node belong to what the claimed task needs (global)

> **Granularity note (June 2026 optimization)**: `task_need` **merges** the old `flow_path_task_need` + `boundary_node_task_need` into a single global question. At the rule layer `task_need = min(flow_path signal, boundary_node signal)`; since `min(a,b,min(c,d)) ≡ min(a,b,c,d)`, the **rule-layer necessity_score is bit-for-bit unchanged**. Both sub-signals are still exposed under `global_necessity.{flow_path_signal, boundary_node_signal}` for debugging. The LLM asks it as **one** question, halving schema/output to cut cost and latency.

---

## 3. Three-stage pipeline (end to end)

Entry point: `scripts/skillflow-pipeline.js`, default `all` flow. Config in `skillflow-pipeline.config.cjs`; two pipeline READMEs (`README-PIPELINE.md` / `README-PIPELINE-CH.md`).

```text
                    ┌─────────────┐   ┌──────────────────┐   ┌─────────────────────┐
ClawHub top-k  ───▶ │ 1. Download │──▶│ 2. FCG flow graph │──▶│ 3. DOE exposure score│
   (by downloads)   └─────────────┘   └──────────────────┘   └─────────────────────┘
                          │                   │                        │
                    zips/ downloads     fcg/skills/*.json        doe/skills/*.json
                                        + flow.md / flow.mmd      + doe-summary.{json,md}
```

Optional **similarity grouping** is off by default; it runs only with `--with-similarity` (or `--phase download-group`).

### Stage 1 — Download (reuses `packages/skill-similarity-analyzer`)

Fetches the top-k ClawHub skill zips sorted by `downloads`. Concurrent, with retry and timeout.

### Stage 2 — FCG (Flow-Control Graph, `packages/skill-fcg-analyzer`)

> FCG is the largest component in the chain (`src/` ~15k lines) and the sole input source for DOE.
> This section is laid out as "orchestration → output schema → LLM touch points" to align the input contract with DOE.

#### 2.1 What it does

Parses a skill package (`SKILL.md` + README + scripts + other docs) into a **directed flow graph**, then overlays a layer of **security semantic profile (security_profile)**.

- Graph (`nodes` / `edges`): who passes data to whom.
- Security profile (`security_profile`): what sensitive data (label) each node handles, along what path data flows (label_flow), and where it crosses a trust boundary (observation).

The DOE stage **reads only `security_profile`** (observations / label_flows / node_profiles / provenance_store / provenance_graph / label_dictionary). The graph itself (nodes/edges/paths) is mainly for human-readable reports and debugging. This is the interface boundary between the two stages.

> **Extraction granularity: block classification + strategy dispatch (rewritten July 2026)**. Extraction is no longer "run keywords line by line"; it **first classifies the file type, then the content-block type, then dispatches the matching strategy**:
>
> - **File type**: instruction docs (SKILL.md/README) vs non-instruction docs (changelog/license/notice/contributing, blocked by `NON_INSTRUCTION_MD` in `document-context.js` and producing no action nodes) vs scripts (js/py/sh).
> - **Content-block type**: code / table / list / prose / disclaimer. Shell code blocks and shell commands inside scripts **share `shell-command-classifier.js`** (a deterministic whitelist: egress/exec/read/write + URL/host/redirect detection) and emit a sink per command (`curl`/`wget` egress is the strongest sink evidence, previously the whole block was dropped); negations and disclaimers in prose ("does not send…", "What this skill does NOT do") are detected and demoted to `guard`/`context` instead of being flipped into an egress action; a table's condition is kept as an edge-connection criterion.
> - **List-block structure (`segmentMarkdownBlocks`, July 2026)**: prose/lists are segmented into blocks before extraction. A **multi-line bullet** (continuation indented past the marker column) is folded into one item instead of stray fragment nodes; a **list block inherits its lead-in disclaimer scope** — bullets under `**What this skill does NOT do:**` become context even without repeating a negation word; **reverse protection**: an explicit imperative instruction in a soft negation section (e.g. `## Limitations`) is not suppressed (keeps weather's `- PNG: curl … -o` sink alive). Prose stays line-oriented (real "paragraphs" are usually one multi-sentence line, so line ≈ paragraph); no cross-line prose merging.
> - **Script calls**: classified by role (sink/source/sanitizer/noise). Language builtins (`push`/`map`/`console.log`/`Array.isArray`, etc.) are dropped as noise, while **unknown user functions are kept** (never guessed as noise), preventing script-node explosion.
> - This layer is **rule-first, LLM only for ambiguity**, preserving the default zero-LLM token cost. See the semantic gate in §2.5.
>
> **Two forces on edge connection (recall vs precision)**: type-analyzer uses **exhaustive candidates + type/signature compatibility** to ensure edges that should connect do (recall — cross-block/cross-section data flows rely on this); the routing layer (`flow-instance-router`) uses **condition/guard semantics** to keep edges that should not connect from carrying a label (precision). Extracted `formal_semantics.conditions` (`when/if/unless/without`…) are surfaced onto the profile by node-profiler and fed into `buildRouteText`; an explicit negative condition ("unless redacted", "only if not") **downgrades** an otherwise-definite sink route to `may_route` (no edge deletion, no hard block, unchanged when no condition is present — so recall is untouched).

#### 2.2 Orchestration (the phases in `src/index.js`)

Entry class `SkillFCGAnalyzer.analyze(inputPath)`; each `[ok] ...` in the log maps to a step:

| Phase | Step | Module | Output |
| --- | --- | --- | --- |
| 1 | Unzip / locate skill root | `index.js` | skillRootDir |
| 2 | Parse skill files + doc plan | `parser/skill-parser`, `parser/document-context` | skillData / readme / executable list |
| 3a | Extract tool calls | `parser/tool-extractor` | tool nodes |
| 3b | Extract script data flow (JS/PY/…): calls classified by role (sink/source/sanitizer/noise), builtin noise dropped, unknown user functions kept; shell commands go through the shared classifier | `parser/script-flow-extractor`, `parser/shell-command-classifier` | script flow nodes+edges |
| 3c | Extract doc data flow: **first classify the file type (instruction md vs non-instruction docs like changelog/license), then classify the block (code/table/list/prose/disclaimer) and dispatch the matching extraction strategy**; list-block structure (multi-line bullet folding, lead-in disclaimer-scope inheritance); shell code blocks emit a sink per command, negations/disclaimers demote to guard/context; sequence edges are same-section by default (`FCG_SEQUENCE_EDGE_SCOPE=global` to revert) | `parser/doc-flow-extractor` (largest), `parser/document-context`, `parser/shell-command-classifier` | doc flow nodes+edges |
| 3d | Inject implicit `user.query` source + `llm.inference` edges | `classifier/source-sink` | activation flows / skill-content→global-LLM edges |
| 4 | Sparse type-compatibility analysis (candidate dependency edges) | `parser/type-analyzer` | dependency candidates |
| 5 | LLM validation of high-value dependency edges | `analyzer/llm-validator` | validated edges |
| 6 | Build graph + dedup edges + break cycles | `analyzer/fcg-builder`, `analyzer/cycle-remover` | graph (nodes/edges) |
| 6b | **Single-crossing split** (deterministic, post-edge; each node crosses ≤1 boundary; children inherit parent edges, synthetic builtins exempt) | `analyzer/node-splitter` | split graph |
| 7 | Path extraction (debug only, cap 1500 paths / length 12) | `analyzer/path-extractor` | all_paths |
| 9 | Emit JSON + **security_profile** + flowchart | `output/json-generator`, `security/*` | `*-fcg.json` / `.flow.md` / `.flow.mmd` |

> `mode`: `quick` (skip Phase 5 LLM dependency validation) / `full` (default) / `deep` (adds structured control_flow ordering edges).

#### 2.3 Security profile generation (inside Phase 9, the `security/` subsystem)

`generateFCGJson(Async)` → `buildTransferSecurityProfile` runs, in order, over the built graph:

1. `node-profiler` — labels each node (category.subtype + sensitivity) plus operation_type, data_surface, receiver_scope, trust_boundary. Optional `label-llm-assistant` assists low-confidence labels via LLM.
2. `graph-transfer-analyzer` — propagates labels over the graph, producing `label_flows` (with `node_path`/`node_names`/`edge_path`), `flow_states`, `transitions`, and events (route/filter/merge/observation).
3. `observation-analyzer` — folds boundary-crossing events into **observations**.
4. `provenance-extractor` — builds `provenance_graph` / `provenance_store` (origins / path_classes / representative_paths), recording data lineage.

#### 2.4 Output schema (`*-fcg.json`, the contract with DOE)

Top-level fields (schema defined in `fcgSchema` in `output/json-generator.js`):

```text
{
  meta:                { skill_name, skill_version, analysis_timestamp,
                         analyzer_version, input_source, analysis_mode }
  nodes:               [ ... ]           ← graph nodes (below)
  edges:               [ ... ]           ← graph edges (below)
  source_sink:         { sources[], sinks[] }
  paths:               { all_paths[], source_to_sink_paths[],
                         path_clusters[], path_compression{} }   ← debug / human
  statistics:          { total_nodes, total_edges, source_count, sink_count, ... }
  risks:               [ ... ]           ← rule-based risk hints (not DOE verdicts)
  security_profile:    { ... }           ← ★ the part DOE actually consumes
  documentation_context:{ ... }
}
```

**Key node fields** (`buildNodeJson`):

| Field | Meaning |
| --- | --- |
| `id` / `name` | Node unique id / canonical name (e.g. `llm.inference`, `user.query`) |
| `type` | `tool_call` / `builtin_call` / `custom_func` |
| `category` | `Source` / `Sink` / `Intermediate` |
| `is_critical` | Whether it is a critical sink (data-exfil risk point) |
| `location` | `{ file, line, section }` traceback |
| `semanticKind` | `doc_step` / `doc_operation` / script nodes, etc. |
| `formal_semantics` | `{ operation_type, inputs[], outputs[], targets[], effects[], conditions[], evidence{} }` |
| `semantic_gate` | LLM semantic-gate verdict (see 2.5) |
| `instructionText` / `source_context` / `action_evidence` | Extracted source text and evidence |

**Key edge fields**: `{ id, source, target, type, confidence, validation_method, data_flow{from_param,to_param,data_type}, semantic_reason }`, where `type ∈ {data_dependency, control_flow, semantic, doc_instruction}` and `validation_method` marks whether it came from rules (`dependency_structural`/`dependency_rule`) or LLM validation (`dependency_llm`).

**Key security_profile fields (★ DOE input)** (`security/transfer-analysis.js`, current `version: 5.1`):

| Field | Meaning | DOE use |
| --- | --- | --- |
| `node_profiles[]` | Per-node security profile (label/operation/data_surface/receiver_scope/trust_boundary) | local necessity |
| `label_flows[]` | Label flow: `{ label_flow_id, label{...} or label_id, current_node, node_path, node_names, edge_path, flow_mode, confidence, origin_ids, parent_label_flow_ids[], path_class_ids, ... }` | global necessity, path evidence |
| `label_dictionary` | Top-level deduped label table (since v5.0); `label_flows[].label_id` references it | dereference to a label |
| `observations[]` | Boundary observation: `{ observation_id, node_id, operation_type, boundary{trust_boundary,receiver_scope}, label_flow_ids[], ... }` | the observation side of an assessment unit |
| `flow_states[]` | Aggregated label-flow state | aggregate evidence |
| `provenance_store` | `{ origins[], path_classes[], representative_paths[] }` | provenance evidence |
| `provenance_graph` | Data-propagation lineage (events) | filter/storage evidence |
| `statistics` | `observation_count` / `label_flow_count` / `label_dictionary_count` / ... | scale and logging |

> **Alignment point 1**: DOE's smallest decision unit `(observation × label_flow)` comes directly from here — `observations[].label_flow_ids` expand into a Cartesian set of assessment units. If FCG is replaced/changed, DOE needs no change as long as these `security_profile` array-field contracts hold.
>
> **Alignment point 2 (v5.1 contract)**: label_flow now **carries its own `node_path`/`node_names`/`edge_path`** (previously DOE rebuilt these from the parent chain). `edge_path` obeys the **positional contract** `len(edge_path) == len(node_path) - 1` (edge[i] connects node[i]→node[i+1]). The redundant singular `parent_label_flow_id` was removed; everything reads the plural `parent_label_flow_ids[0]`. Each flow is **single-flow** (≤1 parent); the parent pointer is for **traceback** (so a `source_introduction` extract/summarize step is not mistaken for an origin), not for recording merges. GNN/sequence models can consume node_path directly, no rebuild needed.
>
> **Alignment point 3 (label_dictionary, since v5.0)**: labels are deduped into the top-level `label_dictionary` and flows reference them by `label_id`. DOE dereferences once at the single boundary `labelFlowById` in `analyzeDoeRuleOnly` (inline first, else look up the dictionary; a dangling id explicitly raises a `label_dictionary.miss` warning); everything downstream is unchanged. **This only saves FCG disk / parse latency, not LLM tokens.**

#### 2.5 The 3 LLM touch points in FCG (all toggleable, all cached)

FCG is not "one big LLM call" but 3 **independent, separately toggleable** LLM touch points:

1. **Markdown semantic gate (on by default, strong gate)** — `doc-flow-extractor` + `script-flow-extractor`. Rules only produce candidate nodes; the **LLM decides each candidate's actionability/classification/operation_type**, written into the node's `semantic_gate`. Missing `LLM_API_KEY` fails the FCG preflight. This is the main source of both FCG precision and latency. Cache: `<root>/fcg/semantic-gate-cache.jsonl` (persists across runs/CI).
2. **Dependency-edge validation (default `high_value` strategy)** — Phase 5 `analyzer/llm-validator`. LLM-confirms only high-value candidate dependency pairs, producing `validation_method=dependency_llm` edges. Skipped in `quick` mode. Tunable via `FCG_DEPENDENCY_LLM_*`.
3. **Label LLM assist (off by default)** — `security/label-llm-assistant`. Generates weak-evidence candidate labels only for generic/low-evidence labels, marked `mode=llm_assisted`, `requires_review=true`, so DOE can tell strong from weak evidence.

> Key property: an LLM cache hit returns the exact same verdict as before — **extraction quality is identical, only latency drops**. This is the "harden robustness without lowering accuracy" constraint on the FCG side.

### Stage 3 — DOE (`packages/skill-doe-analyzer`)

Consumes the FCG JSON and produces a DOE verdict per assessment unit. See §4.

---

## 4. Inside the DOE analyzer (the project's core, finest granularity)

Source: `packages/skill-doe-analyzer/src/`

| File | Responsibility |
| --- | --- |
| `doe-analyzer.js` | Main orchestration: rule-only scoring → pick units to send to LLM → call LLM judge → blend |
| `exposure-scorer.js` | Exposure scoring (boundary crossed?, boundary risk, sensitivity) |
| `necessity-baseline.js` | Rule-based necessity scoring (3-component baseline, `COMPONENT_KEYS`) |
| `necessity-text-utils.js` | Helpers to extract necessity text signals |
| `group-baseline.js` | Same-group skill baseline adjustment |
| `label-resolver.js` | `resolveLabel` / `buildLabelDictionary`: compat for inline label and `label_id` references |
| `flow-path-utils.js` | label_flow path resolution (fast path when node_path is present, else rebuild from parent chain) |
| `evidence-pack.js` | Pack one unit into a **flow-centric** evidence pack + aggregate shared task_memory |
| `evidence-budget.js` | Tiered compression of the evidence pack (guard against context overflow / timeout) |
| `llm-judge.js` | LLM judge: prompt packing, batching, voting, escalation review, caching, fault tolerance |
| `path-report.js` | Human-readable report generation |

### 4.1 Two-layer scoring: rules + LLM blend

1. **Rule layer (rule-only, deterministic, free, offline)**: every unit first gets an exposure and a 3-component necessity baseline. The rule scorer consumes the FCG object directly and **does not read the evidence pack**, so pack rewrites do not change rule scores.
2. **LLM gate**: `shouldJudgeAssessmentWithLlm` only lets `boundary_crossed && sensitivity≥high && boundary_risk≥0.75` units go to the LLM. The rest use rule scores only.
3. **LLM judge**: for eligible units, the LLM scores the 3 components from the evidence pack (PROMPT_VERSION `doe-llm-judge-v4-merged-task-need`).
4. **Blend**: `component = llmWeight·llm + (1-llmWeight)·rule` (default `llmWeight=0.7`); necessity is the minimum of the 3 components, then the DOE score is computed.

### 4.2 Voting and escalation (accuracy-oriented)

- First round is **1 vote** per unit (guarantees every unit is seen by the LLM at least once).
- High-risk / uncertain / split-vote units **escalate to 3 votes, median taken** (`risk_or_uncertain` policy).
- Goal: spend LLM calls on the genuinely uncertain verdicts.

### 4.3 Evidence pack: flow-centric structure (rewritten 2026-06-30)

`buildEvidencePack` assembles one per unit (= one complete flow of a label from source to sink). The **old 5-section structure was fully replaced**, no toggle:

- `label` — `{ category, subtype, sensitivity, field_name, field_path }` (pure semantics, no internal ids)
- `sink_boundary` — the data boundary the sink crosses: `{ node_name, operation_type, data_surface, receiver_scope, retention_scope, trust_boundary, operation_tags }` (**node_roles removed** — redundant with the `capabilities` of the flow's role=sink node; **sink_surface moved to the sink flow node**; the single-crossing invariant keeps each unit's sink unique, so sink_boundary stays top-level)
- `flow[]` — per node: `{ node_name, role(source/transform/sink/source_sink), action, capabilities?, transform?{type,from_label,to_label,count?}, sink_surface?[] }` — `sink_surface` is present only on the role=sink/source_sink node: the concrete output channel/medium tags (e.g. `webhook_post`, `api_call`, `file_write`, `database_write`, `shell_exec`) that are finer than `sink_boundary`'s coarse fields
- `evidence[]` — flat reference index (`label.main` / `sink.boundary` / `flow.node.{i}`) for LLM grounding + trim-reconstruction
- `task_memory_evidence_ids` — pointers into the skill-level shared `task_memory` for task nodes related to this flow

> **Key design points**:
>
> - **role ≠ capability**: `role` is the node's **positional role on this one label flow** (first=source, last=sink, first==last=source_sink, else=transform); a source→sink unit has **exactly one sink** (the endpoint). `capabilities` is the node's global ability (node_roles). Once we wrongly used global node_roles as `role`, making one flow sprout 8 sinks; fixed.
> - **transform comes from filter_events** (redact_drop/summarization/pseudonymize/unknown_may_flow, etc.) and is a core necessity signal, so it is kept; identical transforms on one node are deduped, carrying `count` when >1 (none when single, to avoid count:1 noise). Cross-node order/count is carried by the dedup key's `transform_seq`, which **display-layer dedup does not touch**.
> - **shared task_memory**: the global task declaration (skill identity + docs + all skill task nodes) is aggregated **once** by `buildSharedTaskMemory(fcg)` and shared at skill level, no longer parasitic on each pack.
> - **information fidelity**: after the rewrite, core semantic token coverage is 98.7%; what is lost is all JSON key-name / event_id noise plus deliberately dropped fields. Single-pack size ~500k chars → ~1.4k (skill_0001).

---

## 5. Robustness / engineering hardening

To run large-scale skills against a **real, unstable, quota-limited** remote API, one hardening pass was done under the constraint that **semantic extraction and DOE verdict accuracy must not drop**. Landed (239 tests green):

1. **FCG semantic-gate cache** persisted at `<root>/fcg/semantic-gate-cache.jsonl` (survives runs/CI). A hit = the same extraction result, only lower latency.
2. **DOE tiered evidence budget** (`evidence-budget.js`):
   - Tier 0 (default): packs within the cap (default 100k chars) are sent **byte-for-byte**, verdicts identical to no compression.
   - Tier 2 (fallback): only over-cap packs are compressed (otherwise they overflow/time out and drop the whole skill). Lossless cleanup → flow-path node windowing (keep boundary + endpoints) → text/array trimming → drop aggregate evidence → provenance truncation → hard-cap fallback. All evidence_ids kept; compressed units flagged `requires_review`.
3. **Adaptive timeout**: request timeout scales with payload size (default cap 4×).
4. **Per-unit graceful degradation**: a single pack that keeps failing transiently → that unit falls back to rule-only + `requires_review`, **no longer crashing the whole skill** (see `statistics.llm_fallback_count` / `llm_fallback_units`).
5. **Transport-layer retry** (`shared/llm-utils.cjs`): 429/5xx/network/timeout retried with exponential backoff + jitter, honoring `Retry-After`; auth/4xx/schema errors fail fast.
6. **Config wiring**: `doe.evidence*`, `fcg.semanticGateCache`, etc. are tunable all the way from config → pipeline → batch CLI; both pipeline READMEs are kept in sync.

---

## 6. Cost status (a known open problem)

For very large skills (e.g. `skill_0001 self-improving-agent`, FCG hundreds of MB, thousands of eligible units), one DOE run with gpt-5.5 is still expensive.

**Lossless optimizations done** (measured via `scripts/measure-doe-cost.js`):

- Necessity 4→3 components, halving LLM output.
- flow-centric pack + shared task_memory aggregated once instead of parasitic per pack; self-repeating task_memory fields trimmed.
- Measured: `skill_0001` first-round estimate **$2,445 → $1,492** (input tokens 485M→296M, −39%, official gpt-5.5 pricing).

The **remaining bulk** has shifted to the evidence_packs themselves; further cuts are lossy and need A/B. The largest remaining non-code lever is **endpoint prompt caching** (shared_context is constant within a skill — a good cacheable prefix).

> Status: the advisor considers per-skill cost still high, so further optimization is **on hold**, but the root cause and directions are on record (prompt caching, larger batch amortization). Note the built-in placeholder price in `measure-doe-cost.js` may differ from official pricing; always unify the unit price when comparing costs across documents.

---

## 7. Data and artifacts

| Path | Contents |
| --- | --- |
| `results/clawhub-top-k10000/` | Download/group/FCG artifacts for a 10k-skill run (largest-scale real run) |
| `results/sample-skill1/` | FCG of a single very large skill (skill_0001), for stress testing |
| `results/ab-sample/` | A/B of DOE budget on/off (verifying "compression does not lower accuracy") |
| `results/debug-k20-c8/` | Small-batch debugging |
| `results/run-logs/` | Logs from real runs (FCG/DOE timing, quota errors) |
| `paper/` | Paper draft (sections / tables / figures) |

---

## 8. Current-state summary (for collaborator alignment)

- **Done and stable**: the three-stage pipeline, FCG semantic gate + cache, DOE two-layer scoring + vote escalation, flow-centric evidence pack/budget, transport robustness. Both a 10k-skill run and a single very large skill have been run for real.
- **Known constraints / open**: LLM call cost (especially for large skills); the test API account has limited quota, so very large skills cannot be fully run.
- **Granularity to align on**:
  - When writing/reporting, **assessment unit = (observation × label_flow)** is the finest decision granularity; the DOE score formula and the **3-component** necessity are the core contributions.
  - Keep **exposure (dangerousness)** and **necessity** distinct — the novelty is the LLM judgment of necessity, not exposure detection itself.
  - FCG and DOE are **two independently replaceable stages**: FCG owns "how the flow graph is built," DOE owns "was the exposure necessary." Split work along the `security_profile` contract (§2.4).

---

## 9. Reproduction entry points

```powershell
# Full pipeline (needs LLM_API_KEY in .env)
node scripts\skillflow-pipeline.js --k 100

# A single stage
node scripts\skillflow-pipeline.js --k 100 --phase fcg
node scripts\skillflow-pipeline.js --k 100 --phase doe

# Tests (239 green; core cases live under packages)
node --test "packages/*/test/**/*.test.js"
```

See `README-PIPELINE.md` and `skillflow-pipeline.config.cjs` for detailed parameters.
