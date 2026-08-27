# SkillFlow Project Overview

> Purpose: give collaborators the "what are we building, how far along, and at what granularity" picture, to align on scope and writing detail.
> Maintenance: this file describes the state as of 2026-08. Code under `packages/` is the source of truth. Chinese version: `PROJECT-OVERVIEW-CH.md`.
> Engine status: **SFG (Skill Flow Graph) is now Python** (`packages/skill-sfg`), **DOE (Data Over-Exposure) is still JS** (`packages/skill-doe-analyzer`), and the orchestrator `scripts/skillflow-pipeline.js` dispatches to both.

---

## 1. One-line positioning

SkillFlow is a static-analysis pipeline for **Data Over-Exposure (DOE)** in **Agent Skills** (downloadable skill packages on ClawHub). The core question it answers:

> When a skill performs the task it claims to perform, does it send **sensitive data beyond what the task actually needs** across a trust boundary (to an external LLM, an external service, persistent storage, etc.)?

It is not simply "did sensitive data flow out," but **"was this outflow necessary to complete the claimed task."** Necessary exposure is not DOE; only unnecessary exposure is. This is the key difference from ordinary taint analysis.

> **Two orthogonal axes**: a boundary crossing has both an **exposure** (how dangerous this egress is in itself) and a **necessity** (how necessary this egress is for the claimed task). A DOE positive = **real egress ∧ not necessary**; real egress (model_provider / external network / third party / persistent storage) is non-exemptable, and feeding an LLM only lowers necessity, never exposure. This orthogonality is the foundation of the structural necessity redesign (see §4).

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
| **DOE score** | `clamp(exposure × (1 - necessity) + baseline_adjustment)` — higher means more over-exposed |
| **potential_doe** | boolean `boundary_crossed ∧ necessity < 0.7` (exposed ∧ not necessary, `DEFAULT_NECESSITY_THRESHOLD=0.7`) |

Exposure (`exposure-scorer.js`): `exposure = boundary_crossed ? clamp(0.6·label_sensitivity + 0.4·boundary_risk) : 0`. `label_sensitivity` comes from a category lookup in `CATEGORY_EXPOSURE` (credentials/secret 1.0, financial/health 0.9, pii 0.8 … generic 0.3); `boundary_risk` is layered by trust/receiver/retention. **All real egress is uniformly tagged `high_sensitivity_egress` tier — no sub-tiers, non-exemptable**; only stopping at `user_visible` (returned to the user, no other egress signal) is `local`.

Necessity is composed of **3 components**; DOE necessity is the **minimum** of the three (the weakest link decides; `COMPONENT_KEYS` in `necessity-baseline.js`). **The key names carry over from the old design, but the internals were redesigned from bag-of-words to structural criteria** (bag-of-words survives only as a weak floor-raising signal):

- **`action_input_need`**: does this action's **input** really require this label (local). Primary criteria = ① the sink applies a real transform to the label (`transform_sig≠none`, weight 0.9) ② the label is in the sink's **declared input schema** (`schemaMember==1`, weight 0.95) ③ op-type baseline (`model_inference`/`external_egress`, etc.). **Structural negative**: a declared schema that does not contain the label and no transform → capped at 0.25.
- **`receiver_semantic_need`**: grounded in a **receiver × label-category compatibility matrix** (`RECEIVER_CATEGORY_COMPAT`, by `model_provider`/`third_party`/`first_party`/`local_runtime`); a reduction before egress lifts it to ≤0.6 (**still below the 0.70 threshold**); a `user_visible` source + single receiver lifts it to 0.6.
- **`task_need`**: `min(flow_path declaration coverage, boundary_node declaration signal)`. The higher the fraction of path nodes declared/synthesized by the task, the more necessary; a generic sink (webhook/analytics/telemetry/log not named by the task) is capped at 0.12. Both sub-signals are still surfaced under `flow_path_signal`/`boundary_node_signal` for debugging.

> **Group baseline is a separate additive term** (`group-baseline.js`): `baseline_adjustment ∈ {-0.08, +0.08, +0.12, 0}`, **added to the final DOE score, not folded into necessity**; without a groupBaseline it is always 0 (the default).

---

## 3. Three-stage pipeline (end to end)

Entry point: `scripts/skillflow-pipeline.js` (JS orchestrator), default `all` flow. It dispatches the SFG stage to Python (`python -m skill_sfg.batch`, cwd=`packages/skill-sfg`) and the DOE stage to JS (`node scripts/doe-batch.js`, cwd=`packages/skill-doe-analyzer`). Config in `skillflow-pipeline.config.cjs`; two pipeline READMEs (`README-PIPELINE.md` / `README-PIPELINE-CH.md`).

```text
                    ┌─────────────┐   ┌──────────────────┐   ┌─────────────────────┐
ClawHub top-k  ───▶ │ 1. Download │──▶│ 2. SFG flow graph │──▶│ 3. DOE exposure verdict│
   (by downloads)   └─────────────┘   └──────────────────┘   └─────────────────────┘
                          │                   │                        │
                    zips/ downloads     fcg/skills/*-sfg.json     doe/skills/*-doe.json
                                        + flow.md / flow.mmd      + doe-summary.{json,md}
```

> **Naming note**: the graph brand was renamed (FCG→**SFG**), but the runtime **keeps** the internal selectors and directories to avoid breaking contracts: the `--phase fcg`/`--phase doe` selectors, output dirs `fcg/`/`doe/`, summary files `fcg-summary.*`/`doe-summary.*`, and the join-contract CLI (`--fcg`/`--fcg-root`) are all unchanged; on the SFG side the per-skill file suffix is now `-sfg.json` and the env-var prefix `SFG_*`, while the DOE side keeps its original `-doe.json` suffix, `DOE_*` prefix, and `skill-doe-analyzer` package.

Optional **similarity grouping** is off by default; it runs only with `--with-similarity` (or `--phase download-group`).

### Stage 1 — Download (reuses `packages/skill-similarity-analyzer`)

Fetches the top-k ClawHub skill zips sorted by `downloads`. Concurrent, with retry and timeout.

### Stage 2 — SFG (Skill Flow Graph, `packages/skill-sfg`, **Python**)

> SFG is the largest component in the chain and the sole input source for DOE. **This stage was rewritten wholesale from JS to Python**: package `skill-sfg`, entry `python -m skill_sfg.batch`, batch CLI `skill-sfg analyze`; modules layered `parser/ → analyzer/ → classifier/ → security/ + flood/ → output/`.
> This section is laid out as "orchestration → output schema → LLM touch points" to align the input contract with DOE.

#### 2.1 What it does

Parses a skill package (`SKILL.md` + README + scripts + other docs) into a **directed flow graph**, then overlays a layer of **security semantic profile (security_profile)**.

- Graph (`nodes` / `edges`): who passes data to whom.
- Security profile (`security_profile`): what sensitive data (label) each node handles, along what path data flows (label_flow), and where it crosses a trust boundary (observation).

The DOE stage **reads only `meta` / `nodes` / `documentation_context` / `security_profile`** (within security_profile it uses observations / label_flows / node_profiles / provenance_graph / label_dictionary / flow_states). The graph's edges and nodes are mainly for human-readable reports and debugging. This is the interface boundary between the two stages.

> **Extraction granularity: block classification + strategy dispatch (rewritten July 2026)**. Extraction is no longer "run keywords line by line"; it **first classifies the file type, then the content-block type, then dispatches the matching strategy**:
>
> - **File type**: instruction docs (SKILL.md/README) vs non-instruction docs (changelog/license/notice/contributing, blocked by `_NON_INSTRUCTION_MD` in `parser/document_context.py` and producing no action nodes) vs scripts (js/py/sh).
> - **Content-block type**: code / table / list / prose / disclaimer. Shell code blocks and shell commands inside scripts **share `parser/shell_command_classifier.py`** (a deterministic whitelist: egress/exec/read/write + URL/host/redirect detection) and emit a sink per command (`curl`/`wget` egress is the strongest sink evidence, previously the whole block was dropped); negations and disclaimers in prose ("does not send…", "What this skill does NOT do") are detected and demoted to `guard`/`context` instead of being flipped into an egress action; a table's condition is kept as an edge-connection criterion.
> - **List-block structure (`segment_markdown_blocks`, July 2026)**: prose/lists are segmented into blocks before extraction. A **multi-line bullet** (continuation indented past the marker column) is folded into one item instead of stray fragment nodes; a **list block inherits its lead-in disclaimer scope** — bullets under `**What this skill does NOT do:**` become context even without repeating a negation word; **reverse protection**: an explicit imperative instruction in a soft negation section (e.g. `## Limitations`) is not suppressed (keeps weather's `- PNG: curl … -o` sink alive). Prose stays line-oriented (real "paragraphs" are usually one multi-sentence line, so line ≈ paragraph); no cross-line prose merging.
> - **Script calls**: classified by role (sink/source/sanitizer/noise). Language builtins (`push`/`map`/`console.log`/`Array.isArray`, etc.) are dropped as noise, while **unknown user functions are kept** (never guessed as noise), preventing script-node explosion.
> - This layer is **rule-first, LLM only for ambiguity**, preserving the default zero-LLM token cost. See the semantic gate in §2.5.
>
> **Two forces on edge connection (recall vs precision)**: `analyzer/type_analyzer.py` uses **exhaustive candidates + type/signature compatibility** to ensure edges that should connect do (recall — cross-block/cross-section data flows rely on this); the routing layer (`flood/router.py`) uses **condition/guard semantics** to keep edges that should not connect from carrying a label (precision). Extracted `formal_semantics.conditions` (`when/if/unless/without`…) are surfaced onto the profile by `security/node_profiler.py` and fed into `build_route_text`; an explicit negative condition ("unless redacted", "only if not") **downgrades** an otherwise-definite sink route to `may_route` (no edge deletion, no hard block, unchanged when no condition is present — so recall is untouched).

#### 2.2 Orchestration (the phases in `analyzer/pipeline.py`)

Entry `run_pipeline(skill_root_dir, options)` (ported from the old JS `SkillFCGAnalyzer.analyze`), returning `{graph, tools, semantic_gate_usage, mode, cycle_expand, skill_data, readme_data, documentation_context}`. **JSON/security_profile generation is not here**; after `run_pipeline` returns, `batch.py` calls `output/json_generator.py::build_fcg_json`:

| Phase | Step | Module | Output |
| --- | --- | --- | --- |
| 1 | Unzip / locate skill root | `batch.py` | skill_root_dir |
| 2 | Parse skill files + README + executable list + doc plan | `parser/skill_parser.py`, `parser/document_context.py` (`parse_skill` / `parse_readme` / `find_executable_files` / `build_documentation_plan`) | skill_data / readme_data / documentation_context |
| 3a | Extract tool calls | `parser/tool_extractor.py` (`extract_tool_calls`) | tool nodes |
| 3b | Extract script data flow (JS/PY/…): calls classified by role (sink/source/sanitizer/noise), builtin noise dropped, unknown user functions kept; shell commands go through the shared classifier | `parser/script_flow_extractor.py` (`extract_script_flow`), `parser/shell_command_classifier.py` | script flow nodes+edges |
| 3c | Extract doc data flow: **first classify the file type (instruction md vs non-instruction docs like changelog/license), then classify the block (code/table/list/prose/disclaimer) and dispatch the matching extraction strategy**; list-block structure (multi-line bullet folding, lead-in disclaimer-scope inheritance); shell code blocks emit a sink per command, negations/disclaimers demote to guard/context; sequence edges are same-section by default (`SFG_SEQUENCE_EDGE_SCOPE=global` to revert) | `parser/doc_flow_extractor.py` (largest, `extract_document_flow` / `resolve_pending_constraints`), `parser/document_context.py`, `parser/shell_command_classifier.py` | doc flow nodes+edges |
| 3d | Inject implicit `user.query` source + `llm.inference` edges; call-site mediation (`build_call_site_mediation`) | `classifier/source_sink.py` (`create_user_query_source`), `analyzer/callsite_expander.py` | activation flows / skill-content→global-LLM edges |
| 4 | Sparse type-compatibility analysis (candidate dependency edges) + structural dependency edges (user.query→llm.inference, skill-content→global-LLM) | `analyzer/type_analyzer.py` (`analyze_type_compatibility`) | dependency candidates |
| 5 | Dependency-edge validation: `full` runs `high_value`-strategy LLM validation (`validation_method=dependency_llm_high_value`), `quick` maps candidates directly, `deep` additionally adds control_flow ordering edges (`build_deep_mode_edges`) | `analyzer/llm_validator.py` | validated edges |
| 6 | Build graph + dedup edges | `analyzer/fcg_builder.py` (`build_fcg` / `remove_duplicate_edges`) | graph (nodes/edges) |
| 6b | Cycles: when `cycle_expand`, `detect_and_tag_cycles` tags feedback edges (no deletion), else `remove_cycles`; then `classify_feedback_edges` (feedback-edge plausibility) → `break_only_fake` | `analyzer/cycle_remover.py`, `analyzer/feedback_edge_classifier.py` | de-cycled / tagged graph |
| 6c | **Single-crossing split** (deterministic, post-edge; each node crosses ≤1 boundary; children inherit parent edges, synthetic builtins exempt) | `analyzer/node_splitter.py` (`split_graph_nodes`) | split graph |
| — | Emit v6 JSON + **security_profile** + flowchart (outside `run_pipeline`, called by `batch.py`) | `output/json_generator.py` (`build_fcg_json`), `output/flowchart_generator.py`, `security/` + `flood/` | `*-sfg.json` / `.flow.md` / `.flow.mmd` |

> `mode`: `quick` (skip Phase 5 LLM dependency validation) / `full` (default) / `deep` (adds structured control_flow ordering edges). The old JS Phase 7 path extraction (`path-extractor`, `O(V!)` and debug-only) was **not ported to Python** — the v6 output has no `paths`.

#### 2.3 Security profile generation (inside `build_fcg_json`, the `security/` + `flood/` subsystems)

`output/json_generator.py::build_fcg_json` → `security/transfer_analysis.py::build_transfer_security_profile` (a thin wrapper: first builds node profiles over the active edge set) → delegates to `flood/public.py::build_transfer_security_profile_v6`. The old JS flat four-step chain (node-profiler → graph-transfer-analyzer → observation-analyzer → provenance-extractor) is **split in Python into `security/` for profiling and `flood/` for propagation**:

1. `security/node_profiler.py` (`build_node_profiles` / `build_node_profiles_with_options`) — profiles each node with a **label** (category.subtype + sensitivity), operation_type, data_surface, receiver_scope, trust_boundary, etc. Optional `security/label_llm_assistant.py` assists low-confidence labels via LLM.
2. `flood/analyzer.py::analyze_graph_transfers` — propagates **labels** over the graph, producing `label_flows` (with `node_path`/`node_names`/`edge_path`), `flow_states`, and events (route/filter/merge).
3. `flood/observations.py::build_observations` — folds boundary-crossing events into **observations**.
4. `flood/public.py::_build_provenance_graph_v6` — builds `provenance_graph` (real transform/filter events only), recording data lineage; labels are deduped into the top-level `label_dictionary`, and label_flows/flow_states are compacted to their public form. **v6 dropped `provenance_store`** (origins/path_classes/representative_paths no longer persisted).

#### 2.4 Output schema (`*-sfg.json`, the contract with DOE)

Top-level fields (assembled by `output/json_generator.py::build_fcg_json`, `analyzer_version: "6.0.0"`). **The v6 envelope is leaner than the old JS**: the debug-only `source_sink` / `paths` / `risks` blocks were **removed** (no verdict depends on them, and `run_pipeline` no longer computes them):

```text
{
  meta:                { skill_name, skill_version, analysis_timestamp,
                         analyzer_version="6.0.0", input_source, analysis_mode }
  nodes:               [ ... ]           ← graph nodes (below)
  edges:               [ ... ]           ← graph edges (below, faithfully preserving SFG graph shape)
  statistics:          { total_nodes, total_edges, ..., feedback_edge_count,
                         semantic_gate_llm_usage? }
  documentation_context:{ ... }
  security_profile:    { ... }           ← ★ the part DOE actually consumes (v6.0)
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

**Key security_profile fields (★ DOE input)** (`flood/public.py::build_transfer_security_profile_v6`, current `version: "6.0"`):

| Field | Meaning | DOE use |
| --- | --- | --- |
| `node_profiles[]` | Per-node security profile (label/operation/data_surface/receiver_scope/trust_boundary) | local necessity |
| `label_flows[]` | Label flow (public compacted form): `{ label_flow_id, label_id or inline label, current_node, node_path, node_names, edge_path, flow_mode, confidence, origin_ids, parent_label_flow_ids[], ... }` | global necessity, path evidence |
| `label_dictionary` | Top-level deduped label table; `label_flows[].label_id` references it | dereference to a label |
| `observations[]` | Boundary observation: `{ observation_id, node_id, operation_type, boundary{trust_boundary,receiver_scope}, label_flow_ids[], ... }` | the observation side of an assessment unit |
| `flow_states[]` | Aggregated label-flow state (slimmed in v6, only decision-needed fields kept) | aggregate evidence, reduction contract |
| `provenance_graph` | Data-propagation lineage (events, real transform/filter events only) | filter/storage evidence |
| `statistics` | `observation_count` / `label_flow_count` / `label_dictionary_count` / `node_flow_set_count` / ... | scale and logging |

> **Alignment point 1**: DOE's smallest decision unit `(observation × label_flow)` comes directly from here — `observations[].label_flow_ids` expand into a Cartesian set of assessment units. If SFG is replaced/changed, DOE needs no change as long as these `security_profile` array-field contracts hold.
>
> **Alignment point 2 (node_path contract)**: label_flow now **carries its own `node_path`/`node_names`/`edge_path`** (previously DOE rebuilt these from the parent chain). `edge_path` obeys the **positional contract** `len(edge_path) == len(node_path) - 1` (edge[i] connects node[i]→node[i+1]). Only the plural `parent_label_flow_ids` is kept; each flow is **single-flow** (≤1 parent); the parent pointer is for **traceback** (so a `source_introduction` extract/summarize step is not mistaken for an origin), not for recording merges. GNN/sequence models can consume node_path directly, no rebuild needed.
>
> **Alignment point 3 (label_dictionary)**: labels are deduped into the top-level `label_dictionary` and flows reference them by `label_id`. DOE dereferences once (inline first, else look up the dictionary; a dangling id explicitly raises a `label_dictionary.miss` warning); everything downstream is unchanged. **This only saves SFG disk / parse latency, not LLM tokens.**
>
> **Alignment point 4 (v6 slimming)**: vs v5.1, v6 dropped `provenance_store` (origins/path_classes/representative_paths) and the `node_flow_sets` detail (only the statistics count is kept), slimmed dead fields out of `flow_states`, and reduced `provenance_graph` to real transform/filter events only. DOE reads just 4 fields from `flow_states`.

#### 2.5 The 3 LLM touch points in SFG (all toggleable, all cached)

SFG is not "one big LLM call" but 3 **independent, separately toggleable** LLM touch points:

1. **Markdown semantic gate (on by default, strong gate)** — `parser/doc_flow_extractor.py` + `parser/script_flow_extractor.py`. Rules only produce candidate nodes; the **LLM decides each candidate's actionability/classification/operation_type**, written into the node's `semantic_gate`. Missing `LLM_API_KEY` fails the SFG preflight. This is the main source of both SFG precision and latency. Cache: `<root>/fcg/semantic-gate-cache.jsonl` (`SFG_SEMANTIC_GATE_CACHE` tunable, persists across runs/CI).
2. **Dependency-edge validation (default `high_value` strategy)** — Phase 5 `analyzer/llm_validator.py`. LLM-confirms only high-value candidate dependency pairs, producing `validation_method=dependency_llm_high_value` edges. Skipped in `quick` mode. Tunable via `SFG_DEPENDENCY_*`.
3. **Label LLM assist (off by default)** — `security/label_llm_assistant.py`. Generates weak-evidence candidate labels only for generic/low-evidence labels, marked `mode=llm_assisted`, `requires_review=true`, so DOE can tell strong from weak evidence.

> Key property: an LLM cache hit returns the exact same verdict as before — **extraction quality is identical, only latency drops**. This is the "harden robustness without lowering accuracy" constraint on the SFG side.

### Stage 3 — DOE (`packages/skill-doe-analyzer`, **JS**)

Consumes the SFG JSON and produces a DOE verdict per assessment unit. See §4.

---

## 4. Inside the DOE analyzer (the project's core, finest granularity)

Source: `packages/skill-doe-analyzer/src/` (DOE is still **JS**; internal identifiers and filenames keep their `doe-*` names, only the brand and package directory changed)

| File | Responsibility |
| --- | --- |
| `doe-analyzer.js` | Main orchestration: rule-only scoring → pick units to send to LLM → call LLM judge → blend |
| `exposure-scorer.js` | Exposure scoring (boundary crossed?, boundary risk, sensitivity) |
| `necessity-baseline.js` | Rule-based necessity scoring (3-component baseline, `COMPONENT_KEYS = ['action_input_need','receiver_semantic_need','task_need']`) |
| `necessity-text-utils.js` | Helpers to extract necessity text signals |
| `group-baseline.js` | Same-group skill baseline adjustment |
| `label-resolver.js` | `resolveLabel` / `buildLabelDictionary`: compat for inline label and `label_id` references |
| `flow-path-utils.js` | label_flow path resolution (fast path when node_path is present, else rebuild from parent chain) |
| `evidence-pack.js` | Pack one unit into a **flow-centric** evidence pack + aggregate shared task_memory |
| `evidence-budget.js` | Tiered compression of the evidence pack (guard against context overflow / timeout) |
| `llm-judge.js` | LLM judge: prompt packing, batching, voting, escalation review, caching, fault tolerance |
| `path-report.js` | Human-readable report generation |

### 4.1 Two-layer scoring: rules + LLM blend

1. **Rule layer (rule-only, deterministic, free, offline)**: every unit first gets an exposure and a 3-component necessity baseline. The rule scorer consumes the SFG object and `flow_states` summary directly and **does not read the evidence pack**, so pack rewrites do not change rule scores.
2. **LLM gate (sensitivity-driven, not a boundary_risk threshold)**: `shouldJudgeAssessmentWithLlm` admits `boundary_crossed && (highSensitive || (mediumSensitive && potential_doe))` — high sensitivity is always judged (reason `high_sensitivity_backstop`), medium sensitivity only when also `potential_doe` (= crossed and necessity<0.7) (reason `medium_sensitivity_potential_doe`). `boundary_risk` is still returned for transparency but **no longer gates**. Before judging, units are deduped by `(observation | label | transform_seq | origin_class)`, collapsing thousands of crossing units into representatives whose verdict members reuse.
3. **LLM judge**: for admitted units, the LLM scores the 3 components from the evidence pack (PROMPT_VERSION `doe-llm-judge-v6-reduction-antichain`).
4. **Blend**: `component = llmWeight·llm + (1-llmWeight)·rule` (default `llmWeight=0.7`); necessity is the minimum of the 3 components, then the DOE score is computed.

### 4.2 Voting and escalation (accuracy-oriented)

- First round is **1 vote** per unit (guarantees every unit is seen by the LLM at least once).
- High-risk / uncertain / split-vote units **escalate to 3 votes, median taken** (`risk_or_uncertain` policy).
- Goal: spend LLM calls on the genuinely uncertain verdicts.

### 4.3 Evidence pack: flow-centric structure (rewritten flow-centric 2026-06-30, now v7 with structural signals)

`buildEvidencePack` assembles one per unit (= one complete flow of a label from source to sink). The **old 5-section structure was fully replaced**, no toggle. The current v7 pack:

- `unit_id` / `observation_id` / `label_flow_id` — decision-unit identifiers
- `question` — the embedded verdict prompt (local necessity: does the sink's action input and receiver semantics need this label; global `task_need`: does the whole source→sink path belong to the data/control flow the claimed task needs, and is the sink required by that path)
- `label` — `{ category, subtype, sensitivity, field_name, field_path }` (pure semantics, no internal ids; `requires_review` / `mode` flags when relevant)
- `sink_boundary` — the data boundary the sink crosses: `{ node_name, operation_type, data_surface, receiver_scope, retention_scope, trust_boundary, operation_tags }`, plus **N5 structural signals**: `exposure_tier` (all real egress uniformly `high_sensitivity_egress`), `reduction_before_egress` (the set of maximal mutually-incomparable reduction types actually applied before crossing = the reduction antichain; empty array = raw data egress). (**node_roles removed** — redundant with the `capabilities` of the flow's role=sink node; **sink_surface moved to the sink flow node**; the single-crossing invariant keeps each unit's sink unique, so sink_boundary stays top-level)
- `flow[]` — per node: `{ node_name, role(source/transform/sink/source_sink), action, operations?, capabilities?, transform?/transforms?, sink_surface?[] }`, plus **N5 structural signals**: sink/source_sink nodes carry `schema_declares_input` (whether the label is in the sink's declared input schema — the hard basis for `action_input_need`), source/source_sink nodes carry `origin_trust` (the trust boundary of the data introduction point — the hard basis for receiver-compat). `sink_surface` is present only on role=sink/source_sink nodes: the concrete output channel/medium tags (`webhook_post`/`api_call`/`file_write`/`database_write`/`shell_exec`, etc.) that are finer than `sink_boundary`'s coarse fields
- `leak_type` / `leak_severity` / `cycle_handling` — attached only when the flow passes a real cycle (periodic leak / collapse exit), so the judge can weight repeated leaks
- `task_memory_evidence_ids` — pointers into the skill-level shared `task_memory` for task nodes related to this flow

> **Key design points**:
>
> - **No per-unit `evidence[]` index**: grounding no longer carries a separate flat evidence index — the `label` / `sink_boundary` / `flow[].node.{i}` already in the structure are the reference anchors; only the skill-level shared `task_memory` keeps an `evidence[]` (referenced by `task_memory_evidence_ids`).
> - **role ≠ capability**: `role` is the node's **positional role on this one label flow** (first=source, last=sink, first==last=source_sink, else=transform); a source→sink unit has **exactly one sink** (the endpoint). `capabilities` is the node's global ability (node_roles). Once we wrongly used global node_roles as `role`, making one flow sprout 8 sinks; fixed.
> - **transform comes from filter_events** (redact_drop/summarization/pseudonymize/unknown_may_flow, etc.) and is a core necessity signal, so it is kept; identical transforms on one node are deduped, carrying `count` when >1 (none when single, to avoid count:1 noise). Cross-node order/count is carried by the dedup key's `transform_seq`, which **display-layer dedup does not touch**.
> - **shared task_memory**: the global task declaration (skill identity + docs + all skill task nodes) is aggregated **once** by `buildSharedTaskMemory(fcg)` from SFG and shared at skill level, no longer parasitic on each pack.
> - **information fidelity**: after the rewrite, core semantic token coverage is 98.7%; what is lost is all JSON key-name / event_id noise plus deliberately dropped fields. Single-pack size ~500k chars → ~1.4k (skill_0001).

---

## 5. Robustness / engineering hardening

To run large-scale skills against a **real, unstable, quota-limited** remote API, one hardening pass was done under the constraint that **semantic extraction and DOE verdict accuracy must not drop**. Landed (213 tests green: SFG 135 pytest + DOE 58 + similarity 20):

1. **SFG semantic-gate cache** persisted at `<root>/fcg/semantic-gate-cache.jsonl` (output dir name `fcg/` kept unchanged; survives runs/CI). A hit = the same extraction result, only lower latency.
2. **DOE tiered evidence budget** (`evidence-budget.js`):
   - Tier 0 (default): packs within the cap (default 100k chars) are sent **byte-for-byte**, verdicts identical to no compression.
   - Tier 2 (fallback): only over-cap packs are compressed (otherwise they overflow/time out and drop the whole skill). Lossless cleanup → flow-path node windowing (keep boundary + endpoints) → text/array trimming → drop aggregate evidence → provenance truncation → hard-cap fallback. All evidence_ids kept; compressed units flagged `requires_review`.
3. **Adaptive timeout**: request timeout scales with payload size (default cap 4×).
4. **Per-unit graceful degradation**: a single pack that keeps failing transiently → that unit falls back to rule-only + `requires_review`, **no longer crashing the whole skill** (see `statistics.llm_fallback_count` / `llm_fallback_units`).
5. **Transport-layer retry**: DOE side `shared/llm-utils.cjs`, SFG side `skill_sfg/llm/transport.py` — 429/5xx/network/timeout retried with exponential backoff + jitter, honoring `Retry-After`; auth/4xx/schema errors fail fast.
6. **Config wiring**: `doe.evidence*`, `fcg.semanticGateCache`, etc. (config keys keep their `fcg`/`doe` names) are tunable all the way from config → pipeline → batch CLI; both pipeline READMEs are kept in sync.

---

## 6. Cost status (a known open problem)

For very large skills (e.g. `skill_0001 self-improving-agent`, SFG hundreds of MB, thousands of eligible units), one DOE run with gpt-5.5 is still expensive.

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
| `results/clawhub-top-k10000/` | Download/group/SFG artifacts for a 10k-skill run (largest-scale real run) |
| `results/sample-skill1/` | SFG of a single very large skill (skill_0001), for stress testing |
| `results/ab-sample/` | A/B of DOE budget on/off (verifying "compression does not lower accuracy") |
| `results/debug-k20-c8/` | Small-batch debugging |
| `results/run-logs/` | Logs from real runs (SFG/DOE timing, quota errors) |
| `paper/` | Paper draft (sections / tables / figures) |

---

## 8. Current-state summary (for collaborator alignment)

- **Done and stable**: the three-stage pipeline, SFG semantic gate + cache, DOE two-layer scoring + vote escalation, flow-centric evidence pack/budget, transport robustness. Both a 10k-skill run and a single very large skill have been run for real.
- **Known constraints / open**: LLM call cost (especially for large skills); the test API account has limited quota, so very large skills cannot be fully run.
- **Granularity to align on**:
  - When writing/reporting, **assessment unit = (observation × label_flow)** is the finest decision granularity; the DOE score formula and the **3-component** necessity are the core contributions.
  - Keep **exposure (dangerousness)** and **necessity** distinct — the novelty is the LLM judgment of necessity, not exposure detection itself.
  - SFG and DOE are **two independently replaceable stages**: SFG owns "how the flow graph is built," DOE owns "was the exposure necessary." Split work along the `security_profile` contract (§2.4).

---

## 9. Reproduction entry points

```powershell
# Full pipeline (needs LLM_API_KEY in .env)
node scripts\skillflow-pipeline.js --k 100

# A single stage
node scripts\skillflow-pipeline.js --k 100 --phase fcg
node scripts\skillflow-pipeline.js --k 100 --phase doe

# Tests (213 green total)
# SFG is Python now (135 pytest):
python -m pytest packages/skill-sfg/tests
# DOE + similarity stay JS (58 + 20):
node --test "packages/skill-doe-analyzer/test/**/*.test.js" "packages/skill-similarity-analyzer/test/**/*.test.js"
```

See `README-PIPELINE.md` and `skillflow-pipeline.config.cjs` for detailed parameters.
