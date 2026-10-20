# Joint semantic annotation: annotation

Status: **Annotation record complete** (`complete`)

These are static possibilities under the contract, not an execution trace. Defaults do not establish actual reads or observations; explicit local acquisition, return or isolation mechanisms constrain their scope.

Abstract runtime contract: `skillflow-abstract-runtime-v7`; digest: `32abb3320d5d1b1e9c18c37622c0d523317faaa0f69027de15b7ce76c61b3eda`.

Joint annotation and symbolic transfer specifications are complete; structure, operation coverage and evidence references passed validation.

Complete means a complete annotation record, not a safety conclusion or proof of model semantics.

Calls, JSON normalizations and model corrections are counted separately:

```json
{
  "logical_calls": 2,
  "stage_calls": 1,
  "structural_corrections": 1,
  "json_normalizations": 0,
  "http_attempts": 2,
  "http_retries": 0,
  "http_attempts_observed": true,
  "returned_models": [
    "deepseek-flash"
  ],
  "known_token_usage": {
    "input_tokens": 43068,
    "output_tokens": 88384,
    "total_tokens": 131452
  },
  "record_integrity_errors": []
}
```

Graph digest: `cdce0c44bb6531ac4058788c2510029e079e628fec77e691e7b54d24d2e59144`

[Compiled semantics, locations and sinks](audit/compiled-response.json) · [Location evidence](audit/location-evidences.json) · [Validation record](validation.json) · [Run result](result.json)

## Execution issues and capability boundaries


[Recorded response chain](../calls/annotation/chain.json). Raw responses are retained unchanged. A normalized request has a normalization.json receipt beside its validation.json; validation binds both the raw response and the candidate. Parsed specifications are not raw model text.

- `calls/annotation/a001`: [raw response](../calls/annotation/a001/response.json) · [candidate validation](../calls/annotation/a001/validation.json)
- `calls/annotation/a002`: [raw response](../calls/annotation/a002/response.json) · [candidate validation](../calls/annotation/a002/validation.json)

Request identity validation (not a semantic correctness proof):

```json
{
  "schema_version": "skill-ir-request-validation-v1",
  "config_sha256": "73ed56afcaa421a1448e0cd0058ab5192403256fe534ef248351578383426cb0",
  "prompt_sha256": "fa025a75cd01742f39254ac5cde82bce01ef5c1361dee6feee92be2a837633ca",
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
      "request_body_sha256": "fcf4ea393b717073171976561eaef1db767820d050c552918a827cbcf8debb4c"
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
| ir_003 / 0 / 0 | __compiled_model_context__ · model_context / Current model processing context | model_observe | 2 | recipient / None | — |
| ir_004 / 0 / 0 | __compiled_model_context__ · model_context / Current model processing context | model_observe | 2 | recipient / None | — |
| ir_005 / 0 / 0 | __compiled_model_context__ · model_context / Current model processing context | model_observe | 2 | recipient / None | — |
| ir_007 / 0 / 0 | __compiled_model_context__ · model_context / Current model processing context | model_observe | 2 | recipient / None | — |
| ir_007 / 1 / 0 | __compiled_model_context__ · model_context / Current model processing context | model_observe | 2 | recipient / None | — |
| ir_007 / 2 / 0 | __compiled_model_context__ · model_context / Current model processing context | model_observe | 2 | recipient / None | — |
| ir_007 / 4 / 0 | index_search · tool / index.search | external_tool | 2 | recipient / None | — |
| ir_007 / 5 / 0 | __compiled_model_context__ · model_context / Current model processing context | model_observe | 2 | recipient / None | — |
| ir_009 / 0 / 0 | __compiled_model_context__ · model_context / Current model processing context | model_observe | 2 | recipient / None | — |
| ir_010 / 0 / 0 | count_file · storage / count.txt | storage_write | 1 | task / persistent | — |
| ir_011 / 0 / 0 | __compiled_model_context__ · model_context / Current model processing context | model_observe | 2 | recipient / None | — |

Task-internal temporary flow remains represented; level 0 is excluded from the sink list. Deleting a binding does not deliver its old contents. Exclusion from this list is not a data-safety guarantee.

## IR semantics by block

### block_001 · Read the user-supplied request.json

| IR | Action | Executing subjects (operator) | effects |
|---|---|---|---|
| ir_001 | read_request_json | agent_runtime | 1. fs_read<br>2. model_observe |
| ir_002 | dispatch | agent_runtime | [] (no recorded effects; not a no-op; inspect the action and bindings) |

### block_002 · Extract request.term and optional from_date and limit

| IR | Action | Executing subjects (operator) | effects |
|---|---|---|---|
| ir_003 | extract_query_term | agent_runtime | 1. model_observe<br>2. transform |
| ir_004 | extract_optional_from_date | agent_runtime | 1. model_observe<br>2. transform |
| ir_005 | extract_optional_limit | agent_runtime | 1. model_observe<br>2. transform |
| ir_006 | dispatch | agent_runtime | [] (no recorded effects; not a no-op; inspect the action and bindings) |

### block_003 · Call index.search once with the request term and optional arguments

| IR | Action | Executing subjects (operator) | effects |
|---|---|---|---|
| ir_007 | index.search | agent_runtime, tool | 1. model_observe<br>2. model_observe<br>3. model_observe<br>4. transform<br>5. model_observe |
| ir_008 | dispatch | agent_runtime | [] (no recorded effects; not a no-op; inspect the action and bindings) |

### block_004 · Write the response total to count.txt and return the response items

| IR | Action | Executing subjects (operator) | effects |
|---|---|---|---|
| ir_009 | extract_response_total | agent_runtime | 1. model_observe<br>2. transform |
| ir_010 | write_count_file | agent_runtime | 1. fs_write |
| ir_011 | extract_response_items | agent_runtime | 1. model_observe<br>2. transform |
| ir_012 | return | agent_runtime | [] (no recorded effects; not a no-op; inspect the action and bindings) |

## Independent Task basis and demand realization

Purpose basis: `declared_skill`; Task revision: `b7d5394817bf20305abb5bd7a18bf975e5bf784a93eea05091a51969895675cb`.

Query an index once using a supplied request and preserve optional-parameter semantics.

Task requirements: 9; Positive preservation goals: 10; Expressions: 2.

Task comes from the independent source stage; annotation references that revision only. Expression states below do not prove requirements are satisfied, demands are minimal or semantics are complete.

| Requirement | Expression status | Remaining limitations |
| --- | --- | --- |
| R1 | expressed |  |
| R2 | expressed |  |
| R3 | expressed |  |
| R4 | expressed |  |
| R5 | expressed |  |
| R6 | expressed |  |
| R7 | retained_only | The workflow prohibits invoking index.delete anywhere. No index.delete operation exists in the CFG, and the available realization constraint forms cannot attach an arbitrary action prohibition to a non-existent event; the restriction is therefore retained rather than declared as an executable constraint. |
| R8 | expressed |  |
| R9 | expressed |  |

## Symbolic transfer specifications

These are compiler-generated symbolic operations. The model declares processing segments; the compiler derives model_observe from their modes and the runtime contract. Compilation does not prove that these semantic claims are correct. Data propagation has not run here; symbolic references are not Data IDs.

[Validated raw specification (parsed candidate)](audit/raw-annotation.json) · [Compiled response](audit/compiled-response.json) · [Compilation mapping](audit/compilation-map.json)

- Location `request_file`: `storage` / `request.json`; access `task`, retention `persistent`. Evidence remains in its audit table; default properties are not measured execution facts.
- Location `index_search`: `tool` / `index.search`; access `recipient`, retention `None`. Evidence remains in its audit table; default properties are not measured execution facts.
- Location `count_file`: `storage` / `count.txt`; access `task`, retention `persistent`. Evidence remains in its audit table; default properties are not measured execution facts.
- Location `__compiled_model_context__`: `model_context` / `Current model processing context`; access `recipient`, retention `None`. Evidence remains in its audit table; default properties are not measured execution facts.

### ir_001 · Events and public results

Order: `fixed`; compiled causal constraints: 1.

- Event 0: fs_read.
  - Operation 0: `{"op": "read", "location": "request_file", "output": "request_data"}`
- Event 1: model_observe.
  - Operation 0: `{"op": "deliver", "inputs": [{"kind": "local", "name": "request_data"}], "target": "__compiled_model_context__"}`
- output[0] ← `{"kind": "local", "name": "request_data"}`

### ir_002 · Events and public results

Order: `fixed`; compiled causal constraints: 0.

- No events; the following result bindings still apply.

### ir_003 · Events and public results

Order: `fixed`; compiled causal constraints: 1.

- Event 0: model_observe.
  - Operation 0: `{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- Event 1: transform.
  - Operation 0: `{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["term"], "output": "query_term"}`
- output[0] ← `{"kind": "local", "name": "query_term"}`

### ir_004 · Events and public results

Order: `fixed`; compiled causal constraints: 2.

- Event 0: model_observe.
  - Operation 0: `{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- Event 1: transform.
  - Operation 0: `{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["from_date"], "output": "from_date_value"}`
  - Operation 1: `{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "from_date_present"}`
- output[0] ← `{"kind": "local", "name": "from_date_value"}`
- output[1] ← `{"kind": "local", "name": "from_date_present"}`

### ir_005 · Events and public results

Order: `fixed`; compiled causal constraints: 2.

- Event 0: model_observe.
  - Operation 0: `{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- Event 1: transform.
  - Operation 0: `{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["limit"], "output": "limit_value"}`
  - Operation 1: `{"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["derived"], "output": "limit_present"}`
- output[0] ← `{"kind": "local", "name": "limit_value"}`
- output[1] ← `{"kind": "local", "name": "limit_present"}`

### ir_006 · Events and public results

Order: `fixed`; compiled causal constraints: 0.

- No events; the following result bindings still apply.

### ir_007 · Events and public results

Order: `fixed`; compiled causal constraints: 7.

- Event 0: model_observe.
  - Operation 0: `{"op": "deliver", "inputs": [{"kind": "input", "index": 1}, {"kind": "input", "index": 3}, {"kind": "input", "index": 5}], "target": "__compiled_model_context__"}`
- Event 1: model_observe.
  - Operation 0: `{"op": "deliver", "inputs": [{"kind": "input", "index": 2}], "target": "__compiled_model_context__", "when": {"kind": "input", "index": 3}}`
- Event 2: model_observe.
  - Operation 0: `{"op": "deliver", "inputs": [{"kind": "input", "index": 4}], "target": "__compiled_model_context__", "when": {"kind": "input", "index": 5}}`
- Event 3: transform.
  - Operation 0: `{"op": "build", "parts": [{"path": ["query"], "value": {"kind": "input", "index": 1}, "when": null}, {"path": ["from_date"], "value": {"kind": "input", "index": 2}, "when": {"kind": "input", "index": 3}}, {"path": ["limit"], "value": {"kind": "input", "index": 4}, "when": {"kind": "input", "index": 5}}], "output": "search_request", "container": "object"}`
- Event 4: Data relationship without a security label.
  - Operation 0: `{"op": "deliver", "inputs": [{"kind": "local", "name": "search_request"}], "target": "index_search"}`
  - Operation 1: `{"op": "receive", "location": "index_search", "inputs": [{"kind": "local", "name": "search_request"}], "output": "search_response"}`
- Event 5: model_observe.
  - Operation 0: `{"op": "deliver", "inputs": [{"kind": "local", "name": "search_response"}], "target": "__compiled_model_context__"}`
- output[0] ← `{"kind": "local", "name": "search_response"}`

### ir_008 · Events and public results

Order: `fixed`; compiled causal constraints: 0.

- No events; the following result bindings still apply.

### ir_009 · Events and public results

Order: `fixed`; compiled causal constraints: 1.

- Event 0: model_observe.
  - Operation 0: `{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- Event 1: transform.
  - Operation 0: `{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["total"], "output": "response_total"}`
- output[0] ← `{"kind": "local", "name": "response_total"}`

### ir_010 · Events and public results

Order: `fixed`; compiled causal constraints: 0.

- Event 0: fs_write.
  - Operation 0: `{"op": "write", "target": "count_file", "mode": "replace", "input": {"kind": "input", "index": 1}}`

### ir_011 · Events and public results

Order: `fixed`; compiled causal constraints: 1.

- Event 0: model_observe.
  - Operation 0: `{"op": "deliver", "inputs": [{"kind": "input", "index": 0}], "target": "__compiled_model_context__"}`
- Event 1: transform.
  - Operation 0: `{"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["items"], "output": "response_items"}`
- output[0] ← `{"kind": "local", "name": "response_items"}`

### ir_012 · Events and public results

Order: `fixed`; compiled causal constraints: 0.

- No events; the following result bindings still apply.

## Evidence by claim

### ir_001

- operator=agent_runtime · `skill/references/workflow.md:5-5`: The workflow instructs the skill runtime to read the supplied request.json; no external tool is named for this read.

> Read the user-supplied request.json, which contains term and may contain from_date and limit.

- Event 0: fs_read · `skill/references/workflow.md:5-5`: Reading the supplied request file is the specified data acquisition.

> Read the user-supplied request.json, which contains term and may contain from_date and limit.

- Event 1: model_observe · `EM10`: The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator; retain the independently evidenced executors. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- Event 1: model_observe · `skill/references/workflow.md:5-5`: This line requires reading the user-supplied request.json.

> Read the user-supplied request.json, which contains term and may contain from_date and limit.

### ir_002

- operator=agent_runtime · `{"instruction_id": "ir_002", "path": []}`: The CFG dispatch is an internal workflow control step with no explicit tool or human executor.

> {"id":"ir_002","opcode":"dispatch","inputs":[],"outputs":[],"constraints":[],"metadata":{},"draft_instruction_id":"go_extract_params"}

- No applicable effect · `{"instruction_id": "ir_002", "path": []}`: This dispatch performs only CFG control transfer and has no external effect.

> {"id":"ir_002","opcode":"dispatch","inputs":[],"outputs":[],"constraints":[],"metadata":{},"draft_instruction_id":"go_extract_params"}

### ir_003

- operator=agent_runtime · `skill/references/workflow.md:7-7`: The workflow directs the skill runtime to use request.term as the search query; orchestration of that extraction is an agent-runtime step.

> Call index.search exactly once, using request.term unchanged as its query argument.

- Event 0: model_observe · `EM10`: The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator; retain the independently evidenced executors. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- Event 0: model_observe · `skill/references/workflow.md:7-7`: This line requires using request.term unchanged as the query argument.

> Call index.search exactly once, using request.term unchanged as its query argument.

- Event 1: transform · `skill/references/workflow.md:7-7`: The request term is selected unchanged for the search call.

> Call index.search exactly once, using request.term unchanged as its query argument.

### ir_004

- operator=agent_runtime · `skill/references/workflow.md:10-11`: The workflow directs extracting and conditionally using the optional from_date field; this orchestration is performed by the skill runtime.

>   - When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.
>   - When from_date is missing, omit the from_date argument.

- Event 0: model_observe · `EM10`: The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator; retain the independently evidenced executors. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- Event 0: model_observe · `skill/references/workflow.md:10-11`: These lines define presence-dependent handling of from_date.

>   - When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.
>   - When from_date is missing, omit the from_date argument.

- Event 1: transform · `skill/references/workflow.md:10-11`: The optional from_date value and its presence are extracted for conditional construction.

>   - When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.
>   - When from_date is missing, omit the from_date argument.

### ir_005

- operator=agent_runtime · `skill/references/workflow.md:12-13`: The workflow directs extracting and conditionally using the optional limit field; this orchestration is performed by the skill runtime.

>   - When limit is present, pass its value unchanged as the limit argument.
>   - When limit is missing, omit the limit argument.

- Event 0: model_observe · `EM10`: The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator; retain the independently evidenced executors. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- Event 0: model_observe · `skill/references/workflow.md:12-13`: These lines define presence-dependent handling of limit.

>   - When limit is present, pass its value unchanged as the limit argument.
>   - When limit is missing, omit the limit argument.

- Event 1: transform · `skill/references/workflow.md:12-13`: The optional limit value and its presence are extracted for conditional construction.

>   - When limit is present, pass its value unchanged as the limit argument.
>   - When limit is missing, omit the limit argument.

### ir_006

- operator=agent_runtime · `{"instruction_id": "ir_006", "path": []}`: The CFG dispatch is an internal workflow control step with no explicit tool or human executor.

> {"id":"ir_006","opcode":"dispatch","inputs":[],"outputs":[],"constraints":[],"metadata":{},"draft_instruction_id":"go_search"}

- No applicable effect · `{"instruction_id": "ir_006", "path": []}`: This dispatch performs only CFG control transfer and has no external effect.

> {"id":"ir_006","opcode":"dispatch","inputs":[],"outputs":[],"constraints":[],"metadata":{},"draft_instruction_id":"go_search"}

### ir_007

- operator=agent_runtime · `skill/references/workflow.md:7-7`: The workflow directs the skill runtime to construct the index.search arguments from the request fields.

> Call index.search exactly once, using request.term unchanged as its query argument.

- operator=tool · `{"instruction_id": "ir_007", "side": "input", "index": 0}`: The CFG records index.search as an external_resource argument, independently evidencing a tool interface.

> {"type":"external_resource","identifier":"index.search","semantic_name":"index.search"}

- Event 0: model_observe · `EM10`: The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator; retain the independently evidenced executors. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- Event 0: model_observe · `skill/references/workflow.md:7-7`: This line requires one index.search call with the request term and optional arguments.

> Call index.search exactly once, using request.term unchanged as its query argument.

- Event 1: model_observe · `EM10`: The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator; retain the independently evidenced executors. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- Event 1: model_observe · `skill/references/workflow.md:7-7`: This line requires one index.search call with the request term and optional arguments.

> Call index.search exactly once, using request.term unchanged as its query argument.

- Event 2: model_observe · `EM10`: The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator; retain the independently evidenced executors. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- Event 2: model_observe · `skill/references/workflow.md:7-7`: This line requires one index.search call with the request term and optional arguments.

> Call index.search exactly once, using request.term unchanged as its query argument.

- Event 3: transform · `skill/references/workflow.md:7-15`: The workflow specifies the query argument and conditional from_date and limit members for the same call.

> Call index.search exactly once, using request.term unchanged as its query argument.
> 
> - Call argument requirements:
>   - When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.
>   - When from_date is missing, omit the from_date argument.
>   - When limit is present, pass its value unchanged as the limit argument.
>   - When limit is missing, omit the limit argument.
> 
> Apply the missing-argument settings in [query configuration](../query.yaml) to this same call.

- Event 5: model_observe · `EM10`: The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator; retain the independently evidenced executors. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- Event 5: model_observe · `skill/references/workflow.md:7-7`: This line requires one index.search call with the request term and optional arguments.

> Call index.search exactly once, using request.term unchanged as its query argument.

### ir_008

- operator=agent_runtime · `{"instruction_id": "ir_008", "path": []}`: The CFG dispatch is an internal workflow control step with no explicit tool or human executor.

> {"id":"ir_008","opcode":"dispatch","inputs":[],"outputs":[],"constraints":[],"metadata":{},"draft_instruction_id":"go_post_search"}

- No applicable effect · `{"instruction_id": "ir_008", "path": []}`: This dispatch performs only CFG control transfer and has no external effect.

> {"id":"ir_008","opcode":"dispatch","inputs":[],"outputs":[],"constraints":[],"metadata":{},"draft_instruction_id":"go_post_search"}

### ir_009

- operator=agent_runtime · `skill/references/workflow.md:21-21`: The workflow directs the skill runtime to obtain the search response total for the local file write.

> After the search, write the response's total value to local count.txt.

- Event 0: model_observe · `EM10`: The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator; retain the independently evidenced executors. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- Event 0: model_observe · `skill/references/workflow.md:21-21`: This line requires using the response total after the search.

> After the search, write the response's total value to local count.txt.

- Event 1: transform · `skill/references/workflow.md:21-21`: The response total is selected from the search response for writing.

> After the search, write the response's total value to local count.txt.

### ir_010

- operator=agent_runtime · `skill/references/workflow.md:21-21`: The workflow directs the skill runtime to write the local count.txt file.

> After the search, write the response's total value to local count.txt.

- Event 0: fs_write · `skill/references/workflow.md:21-21`: Writing to the local count.txt file is the specified file effect.

> After the search, write the response's total value to local count.txt.

### ir_011

- operator=agent_runtime · `skill/references/workflow.md:23-23`: The workflow directs the skill runtime to obtain the search response items for returning.

> Return the search response's items value unchanged.

- Event 0: model_observe · `EM10`: The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.

> Deterministic processing compilation: model mode declares model processing and requires llm among participating operators. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator; retain the independently evidenced executors. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure.

- Event 0: model_observe · `skill/references/workflow.md:23-23`: This line requires returning the response items value unchanged.

> Return the search response's items value unchanged.

- Event 1: transform · `skill/references/workflow.md:23-23`: The response items are selected unchanged from the search response.

> Return the search response's items value unchanged.

### ir_012

- operator=agent_runtime · `skill/references/workflow.md:23-23`: The workflow directs the skill runtime to return the selected response items.

> Return the search response's items value unchanged.

- No applicable effect · `skill/references/workflow.md:23-23`: The final instruction is an ordinary return of the selected items value; it has no external effect event.

> Return the search response's items value unchanged.

## Analysis boundaries

This stage declares Task requirements, supported demand semantics, sensitivity, action properties and symbolic operations. It does not execute the Skill or compute final sensitive exposure, risk or indispensability.
Broad reads and model returns are conservative contract defaults. Tool-internal reads, tool returns and model inputs are distinct boundaries. Evidence matching validates references, not semantic support.
Effects preserve occurrence positions. With order=partial, constraints determine possible arrangements; the array is not the unique execution order. Model inference is not proven correct.
context_write changes runtime content or bindings readable by later actions. It is not automatically transform, fs_write or model_observe; ordinary IR output binding does not imply a context write.
Empty effects are not a no-op and cannot establish equal entry and exit states. Failure to represent required relationships is recorded explicitly.
Uninterpreted binary and code boundaries remain in result.json. Assistant review is separate and does not imply user confirmation.
