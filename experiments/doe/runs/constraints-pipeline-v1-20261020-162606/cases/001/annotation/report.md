# Joint semantic annotation: annotation

Status: **Call execution error** (`execution_error`)

These are static possibilities under the contract, not an execution trace. Defaults do not establish actual reads or observations; explicit local acquisition, return or isolation mechanisms constrain their scope.

Abstract runtime contract: `skillflow-abstract-runtime-v7`; digest: `32abb3320d5d1b1e9c18c37622c0d523317faaa0f69027de15b7ce76c61b3eda`.

IncompleteRead(0 bytes read)

Complete means a complete annotation record, not a safety conclusion or proof of model semantics.

Calls, JSON normalizations and model corrections are counted separately:

```json
{
  "logical_calls": 4,
  "stage_calls": 1,
  "structural_corrections": 3,
  "json_normalizations": 0,
  "http_attempts": 4,
  "http_retries": 0,
  "http_attempts_observed": true,
  "returned_models": [
    "deepseek-flash"
  ],
  "known_token_usage": {
    "input_tokens": 60393,
    "output_tokens": 120049,
    "total_tokens": 180442
  },
  "record_integrity_errors": []
}
```

Graph digest: `7761a958a0ef72d0b78165cb2ebf6a9ca06f92e5c2a975f6c5d6e2bf1626f4dd`

[Compiled semantics, locations and sinks](audit/compiled-response.json) · [Location evidence](audit/location-evidences.json) · [Validation record](validation.json) · [Run result](result.json)

## Execution issues and capability boundaries

Error category: `execution`.

[Recorded response chain](calls/annotation/chain.json). Raw responses are retained unchanged. A normalized request has a normalization.json receipt beside its validation.json; validation binds both the raw response and the candidate. Parsed specifications are not raw model text.

- `calls/annotation/a001`: [raw response](calls/annotation/a001/response.json) · [candidate validation](calls/annotation/a001/validation.json)
- `calls/annotation/a002`: [raw response](calls/annotation/a002/response.json) · [candidate validation](calls/annotation/a002/validation.json)
- `calls/annotation/a003`: [raw response](calls/annotation/a003/response.json) · [candidate validation](calls/annotation/a003/validation.json)

Request identity validation (not a semantic correctness proof):

```json
{
  "schema_version": "skill-ir-request-validation-v1",
  "config_sha256": "73ed56afcaa421a1448e0cd0058ab5192403256fe534ef248351578383426cb0",
  "prompt_sha256": "55939f3d67391e8274eb52088f834a1d798742681c1f26c67a2adbeb83d63aba",
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
      "request_body_sha256": "befca314177be1df1bf437cb8586f1a68245b5c3a6ca3d10f3ab2091b8949135"
    }
  ],
  "transport": "http"
}
```

- IncompleteRead(0 bytes read)

## Sink boundaries and fixed levels

The program derives types and levels from location properties and delivery/write operations. Levels describe access and retention, not sensitivity, danger, task necessity or DOE conclusions. Symbolic operations will bind actual data versions during propagation.

| IR / event / operation | Boundary | Type | Level | Access / retention | Scope |
|---|---|---|---|---|
| — | No compiler-collected sink boundary | — | — | — | — |

Task-internal temporary flow remains represented; level 0 is excluded from the sink list. Deleting a binding does not deliver its old contents. Exclusion from this list is not a data-safety guarantee.

## IR semantics by block

### block_001 · Read the user-provided events.json

| IR | Action | Executing subjects (operator) | effects |
|---|---|---|---|
| ir_001 | read_file | Not accepted | Not accepted |
| ir_002 | dispatch | Not accepted | Not accepted |

### block_002 · Select records using the opted_out, urgent, and value conditions

| IR | Action | Executing subjects (operator) | effects |
|---|---|---|---|
| ir_003 | select_notifiable_events | Not accepted | Not accepted |
| ir_004 | dispatch | Not accepted | Not accepted |

### block_003 · Call notify.send for each selected record

| IR | Action | Executing subjects (operator) | effects |
|---|---|---|---|
| ir_005 | notify.send | Not accepted | Not accepted |
| ir_006 | dispatch | Not accepted | Not accepted |

### block_004 · Count processed records

| IR | Action | Executing subjects (operator) | effects |
|---|---|---|---|
| ir_007 | count_processed_records | Not accepted | Not accepted |
| ir_008 | dispatch | Not accepted | Not accepted |

### block_005 · Write the processed-record count to the local count.txt

| IR | Action | Executing subjects (operator) | effects |
|---|---|---|---|
| ir_009 | write_file | Not accepted | Not accepted |
| ir_010 | return | Not accepted | Not accepted |

## Independent Task basis and demand realization

Purpose basis: `declared_skill`; Task revision: `1de777ff1138c698d31d75e9a17d3fdd63f073453fcce88faea8ac57e918d574`.

Send conditionally selected event notifications, without transmitting access tokens, and write the number of processed records to local count.txt.

Task requirements: 8; Positive preservation goals: 0; Expressions: 0.

Task comes from the independent source stage; annotation references that revision only. Expression states below do not prove requirements are satisfied, demands are minimal or semantics are complete.

| Requirement | Expression status | Remaining limitations |
| --- | --- | --- |

## Symbolic transfer specifications

These are compiler-generated symbolic operations. The model declares processing segments; the compiler derives model_observe from their modes and the runtime contract. Compilation does not prove that these semantic claims are correct. Data propagation has not run here; symbolic references are not Data IDs.

[Validated raw specification (parsed candidate)](audit/raw-annotation.json) · [Compiled response](audit/compiled-response.json) · [Compilation mapping](audit/compilation-map.json)


## Evidence by claim

## Analysis boundaries

This stage declares Task requirements, supported demand semantics, sensitivity, action properties and symbolic operations. It does not execute the Skill or compute final sensitive exposure, risk or indispensability.
Broad reads and model returns are conservative contract defaults. Tool-internal reads, tool returns and model inputs are distinct boundaries. Evidence matching validates references, not semantic support.
Effects preserve occurrence positions. With order=partial, constraints determine possible arrangements; the array is not the unique execution order. Model inference is not proven correct.
context_write changes runtime content or bindings readable by later actions. It is not automatically transform, fs_write or model_observe; ordinary IR output binding does not imply a context write.
Empty effects are not a no-op and cannot establish equal entry and exit states. Failure to represent required relationships is recorded explicitly.
Uninterpreted binary and code boundaries remain in result.json. Assistant review is separate and does not imply user confirmation.
