# Joint semantic annotation: annotation

Status: **Annotation record complete** (`complete`)

These are static possibilities under the contract, not an execution trace. Defaults do not establish actual reads or observations; explicit local acquisition, return or isolation mechanisms constrain their scope.

Abstract runtime contract: `skillflow-abstract-runtime-v7`; digest: `32abb3320d5d1b1e9c18c37622c0d523317faaa0f69027de15b7ce76c61b3eda`.

Joint annotation and symbolic transfer specifications are complete; structure, operation coverage and evidence references passed validation.

Complete means a complete annotation record, not a safety conclusion or proof of model semantics.

Calls, JSON normalizations and model corrections are counted separately:

```json
{
  "logical_calls": 3,
  "stage_calls": 1,
  "structural_corrections": 2,
  "json_normalizations": 0,
  "http_attempts": 3,
  "http_retries": 0,
  "http_attempts_observed": true,
  "returned_models": [
    "deepseek-flash"
  ],
  "known_token_usage": {
    "input_tokens": 81600,
    "output_tokens": 135444,
    "total_tokens": 217044
  },
  "record_integrity_errors": []
}
```

Graph digest: `47c39ad7606ed9050aedf8b5322768a40b32a22abca1b762acdc7e4ea66a5244`

[Compiled semantics, locations and sinks](audit/compiled-response.json) · [Location evidence](audit/location-evidences.json) · [Validation record](validation.json) · [Run result](result.json)

## Execution issues and capability boundaries


[Recorded response chain](../calls/annotation/chain.json). Raw responses are retained unchanged. A normalized request has a normalization.json receipt beside its validation.json; validation binds both the raw response and the candidate. Parsed specifications are not raw model text.

- `calls/annotation/a001`: [raw response](../calls/annotation/a001/response.json) · [candidate validation](../calls/annotation/a001/validation.json)
- `calls/annotation/a002`: [raw response](../calls/annotation/a002/response.json) · [candidate validation](../calls/annotation/a002/validation.json)
- `calls/annotation/a003`: [raw response](../calls/annotation/a003/response.json) · [candidate validation](../calls/annotation/a003/validation.json)

Request identity validation (not a semantic correctness proof):

```json
{
  "schema_version": "skill-ir-request-validation-v1",
  "config_sha256": "73ed56afcaa421a1448e0cd0058ab5192403256fe534ef248351578383426cb0",
  "prompt_sha256": "1aeb38b53bd035d17c120bbe4da97dee1b06f02337c53a98a56096b92bac28e9",
  "observed": true,
  "requests": [
    {
      "request_parameters": {
        "model": "deepseek-v4-flash",
        "reasoning_effort": "max",
        "response_format": {
          "type": "json_object"
        },
        "stream": true,
        "stream_options": {
          "include_usage": true
        }
      },
      "request_body_sha256": "9a8eaf9dfc6ab01ed25d81607c34ca65d0c3e02fc27ec8b847a1800be9583cd5"
    }
  ],
  "transport": "http"
}
```

No execution issue was recorded; this is not human confirmation of the annotation.

## Sink boundaries and fixed levels

The program derives types and levels from location properties and delivery/write operations. Levels describe access and retention, not sensitivity, danger, task necessity or DOE conclusions. Symbolic operations will bind actual data versions during propagation.

| IR / event / operation | Boundary | Type | Level | Access / retention | Scope |
|---|---|---|---|---|
| ir_001 / 1 / 0 | __compiled_model_context__ · model_context / Current model processing context | model_observe | 2 | recipient / None | — |
| ir_003 / 1 / 0 | __compiled_model_context__ · model_context / Current model processing context | model_observe | 2 | recipient / None | — |
| ir_005 / 0 / 0 | __compiled_model_context__ · model_context / Current model processing context | model_observe | 2 | recipient / None | — |
| ir_007 / 0 / 0 | fast_fetch · tool / fast.fetch | external_tool | 2 | recipient / None | — |
| ir_007 / 1 / 0 | __compiled_model_context__ · model_context / Current model processing context | model_observe | 2 | recipient / None | — |
| ir_009 / 0 / 0 | __compiled_model_context__ · model_context / Current model processing context | model_observe | 2 | recipient / None | — |
| ir_011 / 0 / 0 | fast_fetch · tool / fast.fetch | external_tool | 2 | recipient / None | — |
| ir_011 / 1 / 0 | __compiled_model_context__ · model_context / Current model processing context | model_observe | 2 | recipient / None | — |
| ir_013 / 0 / 0 | __compiled_model_context__ · model_context / Current model processing context | model_observe | 2 | recipient / None | — |
| ir_015 / 0 / 0 | archive_fetch · tool / archive.fetch | external_tool | 2 | recipient / None | — |
| ir_015 / 1 / 0 | __compiled_model_context__ · model_context / Current model processing context | model_observe | 2 | recipient / None | — |
| ir_017 / 0 / 0 | __compiled_model_context__ · model_context / Current model processing context | model_observe | 2 | recipient / None | — |
| ir_019 / 0 / 0 | status_file · storage / status.txt | storage_write | 1 | task / persistent | — |
| ir_021 / 0 / 0 | status_file · storage / status.txt | storage_write | 1 | task / persistent | — |
| ir_023 / 0 / 0 | status_file · storage / status.txt | storage_write | 1 | task / persistent | — |
| ir_025 / 0 / 0 | status_file · storage / status.txt | storage_write | 1 | task / persistent | — |

Task-internal temporary flow remains represented; level 0 is excluded from the sink list. Deleting a binding does not deliver its old contents. Exclusion from this list is not a data-safety guarantee.

## IR semantics by block

### block_001 · Read source_id from the user's request

| IR | Action | Executing subjects (operator) | effects |
|---|---|---|---|
| ir_001 | read_source_id_from_user_request | agent_runtime | 1. context_read<br>2. model_observe<br>3. transform |
| ir_002 | dispatch | agent_runtime | [] (no recorded effects; not a no-op; inspect the action and bindings) |

### block_002 · Read FAST_KEY from the environment

| IR | Action | Executing subjects (operator) | effects |
|---|---|---|---|
| ir_003 | read_fast_key_from_environment | agent_runtime | 1. context_read<br>2. model_observe<br>3. transform |
| ir_004 | dispatch | agent_runtime | [] (no recorded effects; not a no-op; inspect the action and bindings) |

### block_003 · Check whether FAST_KEY is present

| IR | Action | Executing subjects (operator) | effects |
|---|---|---|---|
| ir_005 | check_fast_key_presence | agent_runtime | 1. model_observe<br>2. transform |
| ir_006 | dispatch | agent_runtime | [] (no recorded effects; not a no-op; inspect the action and bindings) |

### block_004 · Try fast.fetch first with source_id and FAST_KEY

| IR | Action | Executing subjects (operator) | effects |
|---|---|---|---|
| ir_007 | fast.fetch | agent_runtime | 1. model_observe |
| ir_008 | dispatch | agent_runtime | [] (no recorded effects; not a no-op; inspect the action and bindings) |

### block_005 · Classify the first fast.fetch attempt

| IR | Action | Executing subjects (operator) | effects |
|---|---|---|---|
| ir_009 | classify_fast_fetch_outcome | agent_runtime | 1. model_observe<br>2. transform |
| ir_010 | dispatch | agent_runtime | [] (no recorded effects; not a no-op; inspect the action and bindings) |

### block_006 · Retry fast.fetch once with source_id and FAST_KEY

| IR | Action | Executing subjects (operator) | effects |
|---|---|---|---|
| ir_011 | fast.fetch | agent_runtime | 1. model_observe |
| ir_012 | dispatch | agent_runtime | [] (no recorded effects; not a no-op; inspect the action and bindings) |

### block_007 · Classify the fast.fetch retry

| IR | Action | Executing subjects (operator) | effects |
|---|---|---|---|
| ir_013 | classify_fast_fetch_outcome | agent_runtime | 1. model_observe<br>2. transform |
| ir_014 | dispatch | agent_runtime | [] (no recorded effects; not a no-op; inspect the action and bindings) |

### block_008 · Call archive.fetch with source_id only

| IR | Action | Executing subjects (operator) | effects |
|---|---|---|---|
| ir_015 | archive.fetch | agent_runtime | 1. model_observe |
| ir_016 | dispatch | agent_runtime | [] (no recorded effects; not a no-op; inspect the action and bindings) |

### block_009 · Classify the archive.fetch result

| IR | Action | Executing subjects (operator) | effects |
|---|---|---|---|
| ir_017 | classify_fetch_outcome | agent_runtime | 1. model_observe<br>2. transform |
| ir_018 | dispatch | agent_runtime | [] (no recorded effects; not a no-op; inspect the action and bindings) |

### block_010 · Append status and return the first fast.fetch body

| IR | Action | Executing subjects (operator) | effects |
|---|---|---|---|
| ir_019 | append_final_status_to_local_status_file | agent_runtime | 1. fs_write |
| ir_020 | return | agent_runtime | [] (no recorded effects; not a no-op; inspect the action and bindings) |

### block_011 · Append status and return the fast.fetch retry body

| IR | Action | Executing subjects (operator) | effects |
|---|---|---|---|
| ir_021 | append_final_status_to_local_status_file | agent_runtime | 1. fs_write |
| ir_022 | return | agent_runtime | [] (no recorded effects; not a no-op; inspect the action and bindings) |

### block_012 · Append status and return the archive.fetch body

| IR | Action | Executing subjects (operator) | effects |
|---|---|---|---|
| ir_023 | append_final_status_to_local_status_file | agent_runtime | 1. fs_write |
| ir_024 | return | agent_runtime | [] (no recorded effects; not a no-op; inspect the action and bindings) |

### block_013 · Append status and return the archive.fetch error

| IR | Action | Executing subjects (operator) | effects |
|---|---|---|---|
| ir_025 | append_final_status_to_local_status_file | agent_runtime | 1. fs_write |
| ir_026 | return | agent_runtime | [] (no recorded effects; not a no-op; inspect the action and bindings) |

## Independent Task basis and demand realization

Purpose basis: `declared_skill`; Task revision: `5795dc07441e3a322e4d09d174e9478c9d396acbadaf4314048fc565d815f4f9`.

Fetch one source using a credential-gated preferred tool, with a bounded archive fallback.

Task requirements: 16; Positive preservation goals: 24; Expressions: 2.

Task comes from the independent source stage; annotation references that revision only. Expression states below do not prove requirements are satisfied, demands are minimal or semantics are complete.

| Requirement | Expression status | Remaining limitations |
| --- | --- | --- |
| R1 | expressed |  |
| R2 | expressed |  |
| R3 | expressed |  |
| R4 | expressed |  |
| R5 | expressed |  |
| R6 | expressed |  |
| R7 | expressed |  |
| R8 | expressed |  |
| R9 | expressed |  |
| R10 | expressed |  |
| R11 | expressed |  |
| R12 | expressed |  |
| R13 | expressed |  |
| R14 | expressed |  |
| R15 | expressed |  |
| R16 | expressed |  |

## Symbolic transfer specifications

These are compiler-generated symbolic operations. The model declares processing segments; the compiler derives model_observe from their modes and the runtime contract. Compilation does not prove that these semantic claims are correct. Data propagation has not run here; symbolic references are not Data IDs.

[Validated raw specification (parsed candidate)](audit/raw-annotation.json) · [Compiled response](audit/compiled-response.json) · [Compilation mapping](audit/compilation-map.json)

- Location `user_request`: `runtime_context` / `user_request`; access `task`, retention `task`. Evidence remains in its audit table; default properties are not measured execution facts.
- Location `environment`: `runtime_context` / `environment`; access `task`, retention `task`. Evidence remains in its audit table; default properties are not measured execution facts.
- Location `fast_fetch`: `tool` / `fast.fetch`; access `recipient`, retention `None`. Evidence remains in its audit table; default properties are not measured execution facts.
- Location `archive_fetch`: `tool` / `archive.fetch`; access `recipient`, retention `None`. Evidence remains in its audit table; default properties are not measured execution facts.
- Location `status_file`: `storage` / `status.txt`; access `task`, retention `persistent`. Evidence remains in its audit table; default properties are not measured execution facts.
- Location `__compiled_model_context__`: `model_context` / `Current model processing context`; access `recipient`, retention `None`. Evidence remains in its audit table; default properties are not measured execution facts.

### ir_001 · Events and public results

Order: `fixed`; compiled causal constraints: 3.

- Event 0: context_read.
  - Operation 0: `{"op": "read", "location": "user_request", "output": "user_request_snapshot"}`
- Event 1: model_observe.
  - Operation 0: `{"op": "deliver", "inputs": [{"kind": "local", "name": "user_request_snapshot"}], "target": "__compiled_model_context__"}`
- Event 2: transform.
  - Operation 0: `{"op": "select_part", "input": {"kind": "local", "name": "user_request_snapshot"}, "path": ["source_id"], "output": "source_id"}`
- output[0] ← `{"kind": "local", "name": "source_id"}`

### ir_002 · Events and public results

Order: `fixed`; compiled causal constraints: 0.

- No events; the following result bindings still apply.

### ir_003 · Events and public results

Order: `fixed`; compiled causal constraints: 3.

- Event 0: context_read.
  - Operation 0: `{"op": "read", "location": "environment", "output": "environment_snapshot"}`
- Event 1: model_observe.
  - Operation 0: `{"op": "deliver", "inputs": [{"kind": "local", "name": "environment_snapshot"}], "target": "__compiled_model_context__"}`
- Event 2: transform.
  - Operation 0: `{"op": "select_part", "input": {"kind": "local", "name": "environment_snapshot"}, "path": ["FAST_KEY"], "output": "fast_key"}`
- output[0] ← `{"kind": "local", "name": "fast_key"}`

### ir_004 · Events and public results

Order: `fixed`; compiled causal constraints: 0.

- No events; the following result bindings still apply.

### ir_005 · Events and public results

Order: `fixed`; compiled causal constraints: 1.

- Event 0: model_observe.
  - Operation 0: `{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- Event 1: transform.
  - Operation 0: `{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "fast_key_present"}`
- output[0] ← `{"kind": "local", "name": "fast_key_present"}`

### ir_006 · Events and public results

Order: `fixed`; compiled causal constraints: 0.

- No events; the following result bindings still apply.

### ir_007 · Events and public results

Order: `fixed`; compiled causal constraints: 2.

- Event 0: Data relationship without a security label.
  - Operation 0: `{"op": "deliver", "inputs": [{"kind": "input", "index": 1}, {"kind": "input", "index": 2}], "target": "fast_fetch"}`
  - Operation 1: `{"op": "receive", "location": "fast_fetch", "inputs": [{"kind": "input", "index": 1}, {"kind": "input", "index": 2}], "output": "fast_fetch_first_response"}`
- Event 1: model_observe.
  - Operation 0: `{"op": "deliver", "inputs": [{"kind": "local", "name": "fast_fetch_first_response"}], "target": "__compiled_model_context__"}`
- output[0] ← `{"kind": "local", "name": "fast_fetch_first_response"}`

### ir_008 · Events and public results

Order: `fixed`; compiled causal constraints: 0.

- No events; the following result bindings still apply.

### ir_009 · Events and public results

Order: `fixed`; compiled causal constraints: 3.

- Event 0: model_observe.
  - Operation 0: `{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- Event 1: transform.
  - Operation 0: `{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["possible"], "output": "fast_fetch_first_outcome"}`
  - Operation 1: `{"op": "compute", "inputs": [{"kind": "local", "name": "fast_fetch_first_outcome"}], "dependencies": ["derived"], "output": "fast_fetch_first_transient"}`
  - Operation 2: `{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["body"], "output": "fast_fetch_first_body"}`
- output[0] ← `{"kind": "local", "name": "fast_fetch_first_outcome"}`
- output[1] ← `{"kind": "local", "name": "fast_fetch_first_body"}`

### ir_010 · Events and public results

Order: `fixed`; compiled causal constraints: 0.

- No events; the following result bindings still apply.

### ir_011 · Events and public results

Order: `fixed`; compiled causal constraints: 2.

- Event 0: Data relationship without a security label.
  - Operation 0: `{"op": "deliver", "inputs": [{"kind": "input", "index": 1}, {"kind": "input", "index": 2}], "target": "fast_fetch"}`
  - Operation 1: `{"op": "receive", "location": "fast_fetch", "inputs": [{"kind": "input", "index": 1}, {"kind": "input", "index": 2}], "output": "fast_fetch_retry_response"}`
- Event 1: model_observe.
  - Operation 0: `{"op": "deliver", "inputs": [{"kind": "local", "name": "fast_fetch_retry_response"}], "target": "__compiled_model_context__"}`
- output[0] ← `{"kind": "local", "name": "fast_fetch_retry_response"}`

### ir_012 · Events and public results

Order: `fixed`; compiled causal constraints: 0.

- No events; the following result bindings still apply.

### ir_013 · Events and public results

Order: `fixed`; compiled causal constraints: 2.

- Event 0: model_observe.
  - Operation 0: `{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- Event 1: transform.
  - Operation 0: `{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["possible"], "output": "fast_fetch_retry_outcome"}`
  - Operation 1: `{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["body"], "output": "fast_fetch_retry_body"}`
- output[0] ← `{"kind": "local", "name": "fast_fetch_retry_outcome"}`
- output[1] ← `{"kind": "local", "name": "fast_fetch_retry_body"}`

### ir_014 · Events and public results

Order: `fixed`; compiled causal constraints: 0.

- No events; the following result bindings still apply.

### ir_015 · Events and public results

Order: `fixed`; compiled causal constraints: 2.

- Event 0: Data relationship without a security label.
  - Operation 0: `{"op": "deliver", "inputs": [{"kind": "input", "index": 1}], "target": "archive_fetch"}`
  - Operation 1: `{"op": "receive", "location": "archive_fetch", "inputs": [{"kind": "input", "index": 1}], "output": "archive_fetch_response"}`
- Event 1: model_observe.
  - Operation 0: `{"op": "deliver", "inputs": [{"kind": "local", "name": "archive_fetch_response"}], "target": "__compiled_model_context__"}`
- output[0] ← `{"kind": "local", "name": "archive_fetch_response"}`

### ir_016 · Events and public results

Order: `fixed`; compiled causal constraints: 0.

- No events; the following result bindings still apply.

### ir_017 · Events and public results

Order: `fixed`; compiled causal constraints: 3.

- Event 0: model_observe.
  - Operation 0: `{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- Event 1: transform.
  - Operation 0: `{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["possible"], "output": "archive_fetch_outcome"}`
  - Operation 1: `{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["body"], "output": "archive_fetch_body"}`
  - Operation 2: `{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["error"], "output": "archive_fetch_error"}`
- output[0] ← `{"kind": "local", "name": "archive_fetch_outcome"}`
- output[1] ← `{"kind": "local", "name": "archive_fetch_body"}`
- output[2] ← `{"kind": "local", "name": "archive_fetch_error"}`

### ir_018 · Events and public results

Order: `fixed`; compiled causal constraints: 0.

- No events; the following result bindings still apply.

### ir_019 · Events and public results

Order: `fixed`; compiled causal constraints: 0.

- Event 0: fs_write.
  - Operation 0: `{"op": "write", "target": "status_file", "mode": "append", "input": {"kind": "input", "index": 1}}`

### ir_020 · Events and public results

Order: `fixed`; compiled causal constraints: 0.

- No events; the following result bindings still apply.

### ir_021 · Events and public results

Order: `fixed`; compiled causal constraints: 0.

- Event 0: fs_write.
  - Operation 0: `{"op": "write", "target": "status_file", "mode": "append", "input": {"kind": "input", "index": 1}}`

### ir_022 · Events and public results

Order: `fixed`; compiled causal constraints: 0.

- No events; the following result bindings still apply.

### ir_023 · Events and public results

Order: `fixed`; compiled causal constraints: 0.

- Event 0: fs_write.
  - Operation 0: `{"op": "write", "target": "status_file", "mode": "append", "input": {"kind": "input", "index": 1}}`

### ir_024 · Events and public results

Order: `fixed`; compiled causal constraints: 0.

- No events; the following result bindings still apply.

### ir_025 · Events and public results

Order: `fixed`; compiled causal constraints: 0.

- Event 0: fs_write.
  - Operation 0: `{"op": "write", "target": "status_file", "mode": "append", "input": {"kind": "input", "index": 1}}`

### ir_026 · Events and public results

Order: `fixed`; compiled causal constraints: 0.

- No events; the following result bindings still apply.

## Evidence by claim

### ir_001

- operator=agent_runtime · `skill/SKILL.md:8-8`: The agent runtime reads source_id from the user request.

> 1. Read source_id from the user's request and read FAST_KEY from the environment.

- Event 0: context_read · `skill/SKILL.md:8-8`: The user_request context is read.

> 1. Read source_id from the user's request and read FAST_KEY from the environment.

- Event 1: model_observe · `EM10`: The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator; retain the independently evidenced executors. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- Event 1: model_observe · `skill/SKILL.md:8-8`: The first workflow step reads source_id from the user request.

> 1. Read source_id from the user's request and read FAST_KEY from the environment.

- Event 2: transform · `skill/SKILL.md:8-8`: Select source_id from the read user request.

> 1. Read source_id from the user's request and read FAST_KEY from the environment.

### ir_002

- operator=agent_runtime · `skill/SKILL.md:8-8`: The workflow dispatches to reading FAST_KEY after source_id.

> 1. Read source_id from the user's request and read FAST_KEY from the environment.

- No applicable effect · `skill/SKILL.md:8-8`: This dispatch controls the next step without content processing.

> 1. Read source_id from the user's request and read FAST_KEY from the environment.

### ir_003

- operator=agent_runtime · `skill/SKILL.md:8-8`: The agent runtime reads FAST_KEY from the environment.

> 1. Read source_id from the user's request and read FAST_KEY from the environment.

- Event 0: context_read · `skill/SKILL.md:8-8`: The environment context is read.

> 1. Read source_id from the user's request and read FAST_KEY from the environment.

- Event 1: model_observe · `EM10`: The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator; retain the independently evidenced executors. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- Event 1: model_observe · `skill/SKILL.md:8-8`: The first workflow step reads FAST_KEY from the environment.

> 1. Read source_id from the user's request and read FAST_KEY from the environment.

- Event 2: transform · `skill/SKILL.md:8-8`: Select FAST_KEY from the read environment.

> 1. Read source_id from the user's request and read FAST_KEY from the environment.

### ir_004

- operator=agent_runtime · `skill/SKILL.md:8-9`: The workflow dispatches to the FAST_KEY presence check.

> 1. Read source_id from the user's request and read FAST_KEY from the environment.
> 2. If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch.

- No applicable effect · `skill/SKILL.md:8-9`: This dispatch controls the next step without content processing.

> 1. Read source_id from the user's request and read FAST_KEY from the environment.
> 2. If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch.

### ir_005

- operator=agent_runtime · `skill/SKILL.md:9-9`: The agent runtime checks whether FAST_KEY is present.

> 2. If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch.

- Event 0: model_observe · `EM10`: The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator; retain the independently evidenced executors. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- Event 0: model_observe · `skill/SKILL.md:9-9`: The workflow checks FAST_KEY presence.

> 2. If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch.

- Event 1: transform · `skill/SKILL.md:9-9`: Compute the presence condition for FAST_KEY.

> 2. If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch.

### ir_006

- operator=agent_runtime · `skill/SKILL.md:9-9`: The workflow dispatches according to FAST_KEY presence.

> 2. If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch.

- No applicable effect · `skill/SKILL.md:9-9`: This dispatch controls the fetch path without content processing.

> 2. If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch.

### ir_007

- operator=agent_runtime · `skill/SKILL.md:9-9`: The agent runtime tries fast.fetch first with source_id and FAST_KEY.

> 2. If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch.

- Event 1: model_observe · `EM10`: The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator; retain the independently evidenced executors. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- Event 1: model_observe · `skill/SKILL.md:9-9`: The first fast.fetch attempt is made only when FAST_KEY is present.

> 2. If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch.

### ir_008

- operator=agent_runtime · `skill/SKILL.md:9-10`: The workflow dispatches to inspect the first fast.fetch result.

> 2. If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch.
> 3. Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure.

- No applicable effect · `skill/SKILL.md:9-10`: This dispatch controls the next step without content processing.

> 2. If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch.
> 3. Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure.

### ir_009

- operator=agent_runtime · `skill/SKILL.md:10-10`: The agent runtime classifies the first fast.fetch attempt outcome.

> 3. Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure.

- Event 0: model_observe · `EM10`: The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator; retain the independently evidenced executors. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- Event 0: model_observe · `skill/SKILL.md:10-10`: The first fast.fetch attempt is classified as success, transient failure, or non-transient failure.

> 3. Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure.

- Event 1: transform · `skill/SKILL.md:10-10`: Classify the first fast.fetch response and extract its body.

> 3. Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure.

### ir_010

- operator=agent_runtime · `skill/SKILL.md:10-10`: The workflow dispatches according to the first fast.fetch outcome.

> 3. Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure.

- No applicable effect · `skill/SKILL.md:10-10`: This dispatch controls the next step without content processing.

> 3. Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure.

### ir_011

- operator=agent_runtime · `skill/SKILL.md:10-10`: The agent runtime retries fast.fetch once on a transient first failure.

> 3. Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure.

- Event 1: model_observe · `EM10`: The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator; retain the independently evidenced executors. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- Event 1: model_observe · `skill/SKILL.md:10-10`: The single retry of fast.fetch occurs only on a transient first failure.

> 3. Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure.

### ir_012

- operator=agent_runtime · `skill/SKILL.md:10-10`: The workflow dispatches to inspect the fast.fetch retry result.

> 3. Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure.

- No applicable effect · `skill/SKILL.md:10-10`: This dispatch controls the next step without content processing.

> 3. Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure.

### ir_013

- operator=agent_runtime · `skill/SKILL.md:10-11`: The agent runtime classifies the fast.fetch retry outcome.

> 3. Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure.
> 4. After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id.

- Event 0: model_observe · `EM10`: The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator; retain the independently evidenced executors. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- Event 0: model_observe · `skill/SKILL.md:10-11`: The retry response is classified and its body is extracted.

> 3. Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure.
> 4. After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id.

- Event 1: transform · `skill/SKILL.md:10-11`: Classify the fast.fetch retry response and extract its body.

> 3. Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure.
> 4. After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id.

### ir_014

- operator=agent_runtime · `skill/SKILL.md:11-11`: The workflow dispatches to archive.fetch after fast.fetch failures.

> 4. After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id.

- No applicable effect · `skill/SKILL.md:11-11`: This dispatch controls the next step without content processing.

> 4. After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id.

### ir_015

- operator=agent_runtime · `skill/SKILL.md:11-12`: The agent runtime calls archive.fetch with source_id only.

> 4. After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id.
> 5. Call archive.fetch at most once and pass source_id as its only argument.

- Event 1: model_observe · `EM10`: The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator; retain the independently evidenced executors. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- Event 1: model_observe · `skill/SKILL.md:11-12`: archive.fetch is called at most once with source_id as its only argument.

> 4. After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id.
> 5. Call archive.fetch at most once and pass source_id as its only argument.

### ir_016

- operator=agent_runtime · `skill/SKILL.md:11-12`: The workflow dispatches to inspect the archive.fetch result.

> 4. After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id.
> 5. Call archive.fetch at most once and pass source_id as its only argument.

- No applicable effect · `skill/SKILL.md:11-12`: This dispatch controls the next step without content processing.

> 4. After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id.
> 5. Call archive.fetch at most once and pass source_id as its only argument.

### ir_017

- operator=agent_runtime · `skill/SKILL.md:13-13`: The agent runtime classifies the archive.fetch result.

> 6. On either tool's success, return that successful response's body value unchanged and make no further fetch calls.

- Event 0: model_observe · `EM10`: The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator; retain the independently evidenced executors. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- Event 0: model_observe · `skill/SKILL.md:13-14`: The archive.fetch response is classified and its body or error is extracted.

> 6. On either tool's success, return that successful response's body value unchanged and make no further fetch calls.
> 7. If archive.fetch fails, stop and return its error; do not retry archive.fetch.

- Event 1: transform · `skill/SKILL.md:13-14`: Classify the archive.fetch result and extract body or error.

> 6. On either tool's success, return that successful response's body value unchanged and make no further fetch calls.
> 7. If archive.fetch fails, stop and return its error; do not retry archive.fetch.

### ir_018

- operator=agent_runtime · `skill/SKILL.md:13-14`: The workflow dispatches according to the archive.fetch outcome.

> 6. On either tool's success, return that successful response's body value unchanged and make no further fetch calls.
> 7. If archive.fetch fails, stop and return its error; do not retry archive.fetch.

- No applicable effect · `skill/SKILL.md:13-14`: This dispatch controls the next step without content processing.

> 6. On either tool's success, return that successful response's body value unchanged and make no further fetch calls.
> 7. If archive.fetch fails, stop and return its error; do not retry archive.fetch.

### ir_019

- operator=agent_runtime · `skill/SKILL.md:16-16`: The agent runtime appends the first fast.fetch outcome to status.txt.

> 9. Before returning from every success or failure path, append the final status to local status.txt.

- Event 0: fs_write · `skill/SKILL.md:16-16`: Append the final status to local status.txt.

> 9. Before returning from every success or failure path, append the final status to local status.txt.

### ir_020

- operator=agent_runtime · `skill/SKILL.md:13-13`: The workflow returns the first fast.fetch body.

> 6. On either tool's success, return that successful response's body value unchanged and make no further fetch calls.

- No applicable effect · `skill/SKILL.md:13-13`: The return itself has no content effect; it returns the existing body value.

> 6. On either tool's success, return that successful response's body value unchanged and make no further fetch calls.

### ir_021

- operator=agent_runtime · `skill/SKILL.md:16-16`: The agent runtime appends the fast.fetch retry outcome to status.txt.

> 9. Before returning from every success or failure path, append the final status to local status.txt.

- Event 0: fs_write · `skill/SKILL.md:16-16`: Append the final status to local status.txt.

> 9. Before returning from every success or failure path, append the final status to local status.txt.

### ir_022

- operator=agent_runtime · `skill/SKILL.md:13-13`: The workflow returns the fast.fetch retry body.

> 6. On either tool's success, return that successful response's body value unchanged and make no further fetch calls.

- No applicable effect · `skill/SKILL.md:13-13`: The return itself has no content effect; it returns the existing body value.

> 6. On either tool's success, return that successful response's body value unchanged and make no further fetch calls.

### ir_023

- operator=agent_runtime · `skill/SKILL.md:16-16`: The agent runtime appends the archive.fetch outcome to status.txt.

> 9. Before returning from every success or failure path, append the final status to local status.txt.

- Event 0: fs_write · `skill/SKILL.md:16-16`: Append the final status to local status.txt.

> 9. Before returning from every success or failure path, append the final status to local status.txt.

### ir_024

- operator=agent_runtime · `skill/SKILL.md:13-13`: The workflow returns the archive.fetch body.

> 6. On either tool's success, return that successful response's body value unchanged and make no further fetch calls.

- No applicable effect · `skill/SKILL.md:13-13`: The return itself has no content effect; it returns the existing body value.

> 6. On either tool's success, return that successful response's body value unchanged and make no further fetch calls.

### ir_025

- operator=agent_runtime · `skill/SKILL.md:16-16`: The agent runtime appends the archive.fetch failure outcome to status.txt.

> 9. Before returning from every success or failure path, append the final status to local status.txt.

- Event 0: fs_write · `skill/SKILL.md:16-16`: Append the final status to local status.txt.

> 9. Before returning from every success or failure path, append the final status to local status.txt.

### ir_026

- operator=agent_runtime · `skill/SKILL.md:14-14`: The workflow returns the archive.fetch error.

> 7. If archive.fetch fails, stop and return its error; do not retry archive.fetch.

- No applicable effect · `skill/SKILL.md:14-14`: The return itself has no content effect; it returns the existing error value.

> 7. If archive.fetch fails, stop and return its error; do not retry archive.fetch.

## Analysis boundaries

This stage declares Task requirements, supported demand semantics, sensitivity, action properties and symbolic operations. It does not execute the Skill or compute final sensitive exposure, risk or indispensability.
Broad reads and model returns are conservative contract defaults. Tool-internal reads, tool returns and model inputs are distinct boundaries. Evidence matching validates references, not semantic support.
Effects preserve occurrence positions. With order=partial, constraints determine possible arrangements; the array is not the unique execution order. Model inference is not proven correct.
context_write changes runtime content or bindings readable by later actions. It is not automatically transform, fs_write or model_observe; ordinary IR output binding does not imply a context write.
Empty effects are not a no-op and cannot establish equal entry and exit states. Failure to represent required relationships is recorded explicitly.
Uninterpreted binary and code boundaries remain in result.json. Assistant review is separate and does not imply user confirmation.
