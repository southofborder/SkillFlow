# Basic data propagation records

**These records describe static possible behavior under the shared abstract runtime contract, not execution logs. complete means only that solving finished under the contract, not that the model actually observed this content. Default observations and explicit exceptions jointly constrain analysis. Fixed ordering or absence of a contract citation does not establish an observed runtime fact.**

Shared contract: `skillflow-abstract-runtime-v7`; SHA-256: `32abb3320d5d1b1e9c18c37622c0d523317faaa0f69027de15b7ce76c61b3eda`.

Solver status: `complete`.

IR record coverage: 26 / 26.

[Local visual review](report.html) · [Data](data.json) · [Operation records](records.json) · [Sink list](sinks.json)

D labels are report-local short names. Input/output indexes refer to atomic-operation arguments, not original IR operands. Control slots determine inclusion or observation and are not delivered payload. Candidate sets do not imply simultaneous occurrence; possible does not imply complete plaintext inclusion. This stage makes no risk, necessity or DOE judgment. Read scope, model observation, explicit selection and actual arguments are reviewed separately; a tool boundary does not imply networking.

[Frozen runtime contract text](../inputs/runtime-contract.json) (runtime_contract); Expand the audit section below for individual evidence.

## Receiving and storage boundaries

Included positions: 16 operation positions; per-element candidate groups show arguments separately, using existing scope coordinates.

Levels describe boundary properties only: 0 task-local temporary, 1 task-local persistent, 2 another principal/shared, 3 public. They do not measure sensitivity, necessity or final risk. Coverage identifies unevaluated operations; empty arguments do not establish absence of unmodeled content.

| IR / step | Included | Type / level | Target, access / retention | Actual arguments by slot | Rationale and property evidence |
|---|---|---|---|---|---|
| ir_001 / 2.1 | Included | model_observe / 2 | __compiled_model_context__ · model_context: Current model processing context · recipient / Retention period not modeled | 0: D001 | Another recipient or cross-principal sharing; EM10, EM12 |
| ir_003 / 2.1 | Included | model_observe / 2 | __compiled_model_context__ · model_context: Current model processing context · recipient / Retention period not modeled | 0: D014 | Another recipient or cross-principal sharing; EM10, EM12 |
| ir_005 / 1.1 | Included | model_observe / 2 | __compiled_model_context__ · model_context: Current model processing context · recipient / Retention period not modeled | 0: D011 | Another recipient or cross-principal sharing; EM10, EM12 |
| ir_007 / 1.1 | Included | external_tool / 2 | fast_fetch · tool: fast.fetch · recipient / Retention period not modeled | 0: D019; 1: D011 | Another recipient or cross-principal sharing; skill/SKILL.md:9-10 |
| ir_007 / 2.1 | Included | model_observe / 2 | __compiled_model_context__ · model_context: Current model processing context · recipient / Retention period not modeled | 0: D020 | Another recipient or cross-principal sharing; EM10, EM12 |
| ir_009 / 1.1 | Included | model_observe / 2 | __compiled_model_context__ · model_context: Current model processing context · recipient / Retention period not modeled | 0: D020 | Another recipient or cross-principal sharing; EM10, EM12 |
| ir_011 / 1.1 | Included | external_tool / 2 | fast_fetch · tool: fast.fetch · recipient / Retention period not modeled | 0: D019; 1: D011 | Another recipient or cross-principal sharing; skill/SKILL.md:9-10 |
| ir_011 / 2.1 | Included | model_observe / 2 | __compiled_model_context__ · model_context: Current model processing context · recipient / Retention period not modeled | 0: D017 | Another recipient or cross-principal sharing; EM10, EM12 |
| ir_013 / 1.1 | Included | model_observe / 2 | __compiled_model_context__ · model_context: Current model processing context · recipient / Retention period not modeled | 0: D017 | Another recipient or cross-principal sharing; EM10, EM12 |
| ir_015 / 1.1 | Included | external_tool / 2 | archive_fetch · tool: archive.fetch · recipient / Retention period not modeled | 0: D019 | Another recipient or cross-principal sharing; skill/SKILL.md:11-12 |
| ir_015 / 2.1 | Included | model_observe / 2 | __compiled_model_context__ · model_context: Current model processing context · recipient / Retention period not modeled | 0: D009 | Another recipient or cross-principal sharing; EM10, EM12 |
| ir_017 / 1.1 | Included | model_observe / 2 | __compiled_model_context__ · model_context: Current model processing context · recipient / Retention period not modeled | 0: D009 | Another recipient or cross-principal sharing; EM10, EM12 |
| ir_019 / 1.1 | Included | storage_write / 1 | status_file · storage: status.txt · task / persistent | 0: D018 | Task-internal, retained across tasks; skill/SKILL.md:16-16 |
| ir_021 / 1.1 | Included | storage_write / 1 | status_file · storage: status.txt · task / persistent | 0: D012 | Task-internal, retained across tasks; skill/SKILL.md:16-16 |
| ir_023 / 1.1 | Included | storage_write / 1 | status_file · storage: status.txt · task / persistent | 0: D003 | Task-internal, retained across tasks; skill/SKILL.md:16-16 |
| ir_025 / 1.1 | Included | storage_write / 1 | status_file · storage: status.txt · task / persistent | 0: D003 | Task-internal, retained across tasks; skill/SKILL.md:16-16 |

<details><summary>Complete source</summary>

<pre>{
  &quot;files&quot;: [
    {
      &quot;content&quot;: &quot;---\nname: source-fetch-with-fallback\ndescription: Fetch one source using a credential-gated preferred tool and a bounded archive fallback.\n---\n\n# Source Fetch With Fallback\n\n1. Read source_id from the user&#x27;s request and read FAST_KEY from the environment.\n2. If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch.\n3. Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure.\n4. After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id.\n5. Call archive.fetch at most once and pass source_id as its only argument.\n6. On either tool&#x27;s success, return that successful response&#x27;s body value unchanged and make no further fetch calls.\n7. If archive.fetch fails, stop and return its error; do not retry archive.fetch.\n8. Never pass FAST_KEY to archive.fetch or diagnostic output anywhere in this workflow.\n9. Before returning from every success or failure path, append the final status to local status.txt.\n&quot;,
      &quot;path&quot;: &quot;SKILL.md&quot;,
      &quot;sha256&quot;: &quot;90cc786cd8bb72c6881c2d27a95157d4bad8363bd533f2383d02ee8678c61495&quot;
    }
  ],
  &quot;source_sha256&quot;: &quot;fd57bfb1f4c45a3d6d22f015bfcf9cf9f86f812c01d523c996918540bef606da&quot;
}</pre>

</details>

<details><summary>Coverage and diagnostics</summary>

<pre>{
  &quot;coverage&quot;: {
    &quot;ir_001&quot;: &quot;processed&quot;,
    &quot;ir_002&quot;: &quot;processed&quot;,
    &quot;ir_003&quot;: &quot;processed&quot;,
    &quot;ir_004&quot;: &quot;processed&quot;,
    &quot;ir_005&quot;: &quot;processed&quot;,
    &quot;ir_006&quot;: &quot;processed&quot;,
    &quot;ir_007&quot;: &quot;processed&quot;,
    &quot;ir_008&quot;: &quot;processed&quot;,
    &quot;ir_009&quot;: &quot;processed&quot;,
    &quot;ir_010&quot;: &quot;processed&quot;,
    &quot;ir_011&quot;: &quot;processed&quot;,
    &quot;ir_012&quot;: &quot;processed&quot;,
    &quot;ir_013&quot;: &quot;processed&quot;,
    &quot;ir_014&quot;: &quot;processed&quot;,
    &quot;ir_015&quot;: &quot;processed&quot;,
    &quot;ir_016&quot;: &quot;processed&quot;,
    &quot;ir_017&quot;: &quot;processed&quot;,
    &quot;ir_018&quot;: &quot;processed&quot;,
    &quot;ir_019&quot;: &quot;processed&quot;,
    &quot;ir_020&quot;: &quot;processed&quot;,
    &quot;ir_021&quot;: &quot;processed&quot;,
    &quot;ir_022&quot;: &quot;processed&quot;,
    &quot;ir_023&quot;: &quot;processed&quot;,
    &quot;ir_024&quot;: &quot;processed&quot;,
    &quot;ir_025&quot;: &quot;processed&quot;,
    &quot;ir_026&quot;: &quot;processed&quot;
  },
  &quot;diagnostics&quot;: []
}</pre>

</details>

## ir_001 · read_source_id_from_user_request

Block: block_001; Operator: agent_runtime.

IR inputs: 0: user_request

IR outputs: 0: result_001

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: [
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 2,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 2,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 0
      }
    }
  ]
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| 1.1 | context_read | read | — | runtime_context: user_request | 0: D001 |
| 2.1 | model_observe (program-generated, statically possible) | deliver | 0: D001 | model_context: Current model processing context | — |
| 3.1 | transform | select_part | 0: D001 | — | 0: D019 |

Entry/exit changes: 

- `result: result_001`: Unbound → D019

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 8,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;Read the user request context.&quot;,
                &quot;start_line&quot;: 8
              }
            ],
            &quot;location&quot;: &quot;user_request&quot;,
            &quot;op&quot;: &quot;read&quot;,
            &quot;output&quot;: &quot;user_request_snapshot&quot;
          }
        ],
        &quot;effect&quot;: &quot;context_read&quot;,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 8,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The user_request context is read.&quot;,
            &quot;start_line&quot;: 8
          }
        ]
      },
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
                &quot;rule_id&quot;: &quot;EM10&quot;
              },
              {
                &quot;end_line&quot;: 8,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The first workflow step reads source_id from the user request.&quot;,
                &quot;start_line&quot;: 8
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;kind&quot;: &quot;local&quot;,
                &quot;name&quot;: &quot;user_request_snapshot&quot;
              }
            ],
            &quot;op&quot;: &quot;deliver&quot;,
            &quot;target&quot;: &quot;__compiled_model_context__&quot;
          }
        ],
        &quot;effect&quot;: &quot;model_observe&quot;,
        &quot;evidences&quot;: [
          {
            &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
            &quot;rule_id&quot;: &quot;EM10&quot;
          },
          {
            &quot;end_line&quot;: 8,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The first workflow step reads source_id from the user request.&quot;,
            &quot;start_line&quot;: 8
          }
        ]
      },
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 8,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The step requires reading source_id from the user request.&quot;,
                &quot;start_line&quot;: 8
              }
            ],
            &quot;input&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;user_request_snapshot&quot;
            },
            &quot;op&quot;: &quot;select_part&quot;,
            &quot;output&quot;: &quot;source_id&quot;,
            &quot;path&quot;: [
              &quot;source_id&quot;
            ]
          }
        ],
        &quot;effect&quot;: &quot;transform&quot;,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 8,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;Select source_id from the read user request.&quot;,
            &quot;start_line&quot;: 8
          }
        ]
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 8,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The agent runtime reads source_id from the user request.&quot;,
        &quot;start_line&quot;: 8,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 8,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The instruction output is source_id.&quot;,
            &quot;start_line&quot;: 8
          }
        ],
        &quot;output_index&quot;: 0,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;source_id&quot;
        }
      }
    ],
    &quot;precedence&quot;: [
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 1,
          &quot;op_index&quot;: 0
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 0,
          &quot;op_index&quot;: 0
        }
      },
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 2,
          &quot;op_index&quot;: 0
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 0,
          &quot;op_index&quot;: 0
        }
      },
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 2,
          &quot;op_index&quot;: 0
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 1,
          &quot;op_index&quot;: 0
        }
      }
    ],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 8,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The instruction output is source_id.&quot;,
          &quot;start_line&quot;: 8
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;source_id&quot;
      }
    }
  ],
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 8,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;Read the user request context.&quot;,
          &quot;start_line&quot;: 8
        }
      ],
      &quot;location&quot;: &quot;user_request&quot;,
      &quot;op&quot;: &quot;read&quot;,
      &quot;output&quot;: &quot;user_request_snapshot&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
          &quot;rule_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;end_line&quot;: 8,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The first workflow step reads source_id from the user request.&quot;,
          &quot;start_line&quot;: 8
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;user_request_snapshot&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;__compiled_model_context__&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 8,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The step requires reading source_id from the user request.&quot;,
          &quot;start_line&quot;: 8
        }
      ],
      &quot;input&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;user_request_snapshot&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;source_id&quot;,
      &quot;path&quot;: [
        &quot;source_id&quot;
      ]
    }
  ]
}</pre>

</details>

## ir_002 · dispatch

Block: block_001; Operator: agent_runtime.

IR inputs: []

IR outputs: []

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| — | No effect event | — | — | — | Entry/exit states and result bindings remain available |

Entry/exit changes: 

- Location bindings are unchanged; this does not imply absence of observation or sending.

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;empty_effect_evidences&quot;: [
      {
        &quot;end_line&quot;: 8,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;This dispatch controls the next step without content processing.&quot;,
        &quot;start_line&quot;: 8
      }
    ],
    &quot;events&quot;: [],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 8,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The workflow dispatches to reading FAST_KEY after source_id.&quot;,
        &quot;start_line&quot;: 8,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [],
  &quot;steps&quot;: []
}</pre>

</details>

## ir_003 · read_fast_key_from_environment

Block: block_002; Operator: agent_runtime.

IR inputs: 0: environment

IR outputs: 0: result_002

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: [
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 2,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 2,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 0
      }
    }
  ]
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| 1.1 | context_read | read | — | runtime_context: environment | 0: D014 |
| 2.1 | model_observe (program-generated, statically possible) | deliver | 0: D014 | model_context: Current model processing context | — |
| 3.1 | transform | select_part | 0: D014 | — | 0: D011 |

Entry/exit changes: 

- `result: result_002`: Unbound → D011

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 8,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;Read the environment context.&quot;,
                &quot;start_line&quot;: 8
              }
            ],
            &quot;location&quot;: &quot;environment&quot;,
            &quot;op&quot;: &quot;read&quot;,
            &quot;output&quot;: &quot;environment_snapshot&quot;
          }
        ],
        &quot;effect&quot;: &quot;context_read&quot;,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 8,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The environment context is read.&quot;,
            &quot;start_line&quot;: 8
          }
        ]
      },
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
                &quot;rule_id&quot;: &quot;EM10&quot;
              },
              {
                &quot;end_line&quot;: 8,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The first workflow step reads FAST_KEY from the environment.&quot;,
                &quot;start_line&quot;: 8
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;kind&quot;: &quot;local&quot;,
                &quot;name&quot;: &quot;environment_snapshot&quot;
              }
            ],
            &quot;op&quot;: &quot;deliver&quot;,
            &quot;target&quot;: &quot;__compiled_model_context__&quot;
          }
        ],
        &quot;effect&quot;: &quot;model_observe&quot;,
        &quot;evidences&quot;: [
          {
            &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
            &quot;rule_id&quot;: &quot;EM10&quot;
          },
          {
            &quot;end_line&quot;: 8,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The first workflow step reads FAST_KEY from the environment.&quot;,
            &quot;start_line&quot;: 8
          }
        ]
      },
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 8,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The step requires reading FAST_KEY from the environment.&quot;,
                &quot;start_line&quot;: 8
              }
            ],
            &quot;input&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;environment_snapshot&quot;
            },
            &quot;op&quot;: &quot;select_part&quot;,
            &quot;output&quot;: &quot;fast_key&quot;,
            &quot;path&quot;: [
              &quot;FAST_KEY&quot;
            ]
          }
        ],
        &quot;effect&quot;: &quot;transform&quot;,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 8,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;Select FAST_KEY from the read environment.&quot;,
            &quot;start_line&quot;: 8
          }
        ]
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 8,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The agent runtime reads FAST_KEY from the environment.&quot;,
        &quot;start_line&quot;: 8,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 8,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The instruction output is FAST_KEY.&quot;,
            &quot;start_line&quot;: 8
          }
        ],
        &quot;output_index&quot;: 0,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;fast_key&quot;
        }
      }
    ],
    &quot;precedence&quot;: [
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 1,
          &quot;op_index&quot;: 0
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 0,
          &quot;op_index&quot;: 0
        }
      },
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 2,
          &quot;op_index&quot;: 0
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 0,
          &quot;op_index&quot;: 0
        }
      },
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 2,
          &quot;op_index&quot;: 0
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 1,
          &quot;op_index&quot;: 0
        }
      }
    ],
    &quot;sensitivity&quot;: [
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 3,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The skill description describes the preferred tool as credential-gated.&quot;,
            &quot;start_line&quot;: 3
          },
          {
            &quot;end_line&quot;: 8,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;FAST_KEY is read from the environment.&quot;,
            &quot;start_line&quot;: 8
          },
          {
            &quot;end_line&quot;: 15,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;FAST_KEY is prohibited from archive.fetch and diagnostic output, indicating that this environment member is credential information.&quot;,
            &quot;start_line&quot;: 15
          }
        ],
        &quot;label&quot;: &quot;credential&quot;,
        &quot;path&quot;: [
          &quot;FAST_KEY&quot;
        ],
        &quot;property&quot;: &quot;value&quot;,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;environment_snapshot&quot;
        }
      },
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 3,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The skill description describes the preferred tool as credential-gated.&quot;,
            &quot;start_line&quot;: 3
          },
          {
            &quot;end_line&quot;: 15,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;FAST_KEY is prohibited from archive.fetch and diagnostic output, indicating it is a credential.&quot;,
            &quot;start_line&quot;: 15
          }
        ],
        &quot;label&quot;: &quot;credential&quot;,
        &quot;path&quot;: [],
        &quot;property&quot;: &quot;value&quot;,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;fast_key&quot;
        }
      }
    ]
  },
  &quot;output_bindings&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 8,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The instruction output is FAST_KEY.&quot;,
          &quot;start_line&quot;: 8
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;fast_key&quot;
      }
    }
  ],
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 8,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;Read the environment context.&quot;,
          &quot;start_line&quot;: 8
        }
      ],
      &quot;location&quot;: &quot;environment&quot;,
      &quot;op&quot;: &quot;read&quot;,
      &quot;output&quot;: &quot;environment_snapshot&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
          &quot;rule_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;end_line&quot;: 8,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The first workflow step reads FAST_KEY from the environment.&quot;,
          &quot;start_line&quot;: 8
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;environment_snapshot&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;__compiled_model_context__&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 8,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The step requires reading FAST_KEY from the environment.&quot;,
          &quot;start_line&quot;: 8
        }
      ],
      &quot;input&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;environment_snapshot&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;fast_key&quot;,
      &quot;path&quot;: [
        &quot;FAST_KEY&quot;
      ]
    }
  ]
}</pre>

</details>

## ir_004 · dispatch

Block: block_002; Operator: agent_runtime.

IR inputs: []

IR outputs: []

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| — | No effect event | — | — | — | Entry/exit states and result bindings remain available |

Entry/exit changes: 

- Location bindings are unchanged; this does not imply absence of observation or sending.

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;empty_effect_evidences&quot;: [
      {
        &quot;end_line&quot;: 9,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;This dispatch controls the next step without content processing.&quot;,
        &quot;start_line&quot;: 8
      }
    ],
    &quot;events&quot;: [],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 9,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The workflow dispatches to the FAST_KEY presence check.&quot;,
        &quot;start_line&quot;: 8,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [],
  &quot;steps&quot;: []
}</pre>

</details>

## ir_005 · check_fast_key_presence

Block: block_003; Operator: agent_runtime.

IR inputs: 0: result_002

IR outputs: 0: result_003

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: [
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 0
      }
    }
  ]
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| 1.1 | model_observe (program-generated, statically possible) | deliver | 0: D011 | model_context: Current model processing context | — |
| 2.1 | transform | compute | 0: D011 | — | 0: D007 |

Entry/exit changes: 

- `result: result_003`: Unbound → D007

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
                &quot;rule_id&quot;: &quot;EM10&quot;
              },
              {
                &quot;end_line&quot;: 9,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The workflow checks FAST_KEY presence.&quot;,
                &quot;start_line&quot;: 9
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;index&quot;: 0,
                &quot;kind&quot;: &quot;input&quot;
              }
            ],
            &quot;op&quot;: &quot;deliver&quot;,
            &quot;target&quot;: &quot;__compiled_model_context__&quot;
          }
        ],
        &quot;effect&quot;: &quot;model_observe&quot;,
        &quot;evidences&quot;: [
          {
            &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
            &quot;rule_id&quot;: &quot;EM10&quot;
          },
          {
            &quot;end_line&quot;: 9,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The workflow checks FAST_KEY presence.&quot;,
            &quot;start_line&quot;: 9
          }
        ]
      },
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;dependencies&quot;: [
              &quot;derived&quot;
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 9,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;Check FAST_KEY presence.&quot;,
                &quot;start_line&quot;: 9
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;index&quot;: 0,
                &quot;kind&quot;: &quot;input&quot;
              }
            ],
            &quot;op&quot;: &quot;compute&quot;,
            &quot;output&quot;: &quot;fast_key_present&quot;
          }
        ],
        &quot;effect&quot;: &quot;transform&quot;,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 9,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;Compute the presence condition for FAST_KEY.&quot;,
            &quot;start_line&quot;: 9
          }
        ]
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 9,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The agent runtime checks whether FAST_KEY is present.&quot;,
        &quot;start_line&quot;: 9,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 9,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The instruction output is the FAST_KEY presence result.&quot;,
            &quot;start_line&quot;: 9
          }
        ],
        &quot;output_index&quot;: 0,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;fast_key_present&quot;
        }
      }
    ],
    &quot;precedence&quot;: [
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 1,
          &quot;op_index&quot;: 0
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 0,
          &quot;op_index&quot;: 0
        }
      }
    ],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 9,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The instruction output is the FAST_KEY presence result.&quot;,
          &quot;start_line&quot;: 9
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;fast_key_present&quot;
      }
    }
  ],
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
          &quot;rule_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;end_line&quot;: 9,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The workflow checks FAST_KEY presence.&quot;,
          &quot;start_line&quot;: 9
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;__compiled_model_context__&quot;
    },
    {
      &quot;dependencies&quot;: [
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 9,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;Check FAST_KEY presence.&quot;,
          &quot;start_line&quot;: 9
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;fast_key_present&quot;
    }
  ]
}</pre>

</details>

## ir_006 · dispatch

Block: block_003; Operator: agent_runtime.

IR inputs: 0: result_003

IR outputs: []

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| — | No effect event | — | — | — | Entry/exit states and result bindings remain available |

Entry/exit changes: 

- Location bindings are unchanged; this does not imply absence of observation or sending.

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;empty_effect_evidences&quot;: [
      {
        &quot;end_line&quot;: 9,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;This dispatch controls the fetch path without content processing.&quot;,
        &quot;start_line&quot;: 9
      }
    ],
    &quot;events&quot;: [],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 9,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The workflow dispatches according to FAST_KEY presence.&quot;,
        &quot;start_line&quot;: 9,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [],
  &quot;steps&quot;: []
}</pre>

</details>

## ir_007 · fast.fetch

Block: block_004; Operator: agent_runtime.

IR inputs: 0: fast.fetch, 1: result_001, 2: result_002

IR outputs: 0: result_004

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: [
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 1
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 1
      }
    }
  ]
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| 1.1 | Unlabeled data operation | deliver | 0: D019; 1: D011 | tool: fast.fetch | — |
| 1.2 | Unlabeled data operation | receive | 0: D019; 1: D011 | tool: fast.fetch | 0: D020 |
| 2.1 | model_observe (program-generated, statically possible) | deliver | 0: D020 | model_context: Current model processing context | — |

Entry/exit changes: 

- `result: result_004`: Unbound → D020

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 9,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;fast.fetch is called with source_id and FAST_KEY.&quot;,
                &quot;start_line&quot;: 9
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;index&quot;: 1,
                &quot;kind&quot;: &quot;input&quot;
              },
              {
                &quot;index&quot;: 2,
                &quot;kind&quot;: &quot;input&quot;
              }
            ],
            &quot;op&quot;: &quot;deliver&quot;,
            &quot;target&quot;: &quot;fast_fetch&quot;
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 9,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;Acquire the first fast.fetch response.&quot;,
                &quot;start_line&quot;: 9
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;index&quot;: 1,
                &quot;kind&quot;: &quot;input&quot;
              },
              {
                &quot;index&quot;: 2,
                &quot;kind&quot;: &quot;input&quot;
              }
            ],
            &quot;location&quot;: &quot;fast_fetch&quot;,
            &quot;op&quot;: &quot;receive&quot;,
            &quot;output&quot;: &quot;fast_fetch_first_response&quot;
          }
        ],
        &quot;effect&quot;: null
      },
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
                &quot;rule_id&quot;: &quot;EM10&quot;
              },
              {
                &quot;end_line&quot;: 9,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The first fast.fetch attempt is made only when FAST_KEY is present.&quot;,
                &quot;start_line&quot;: 9
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;kind&quot;: &quot;local&quot;,
                &quot;name&quot;: &quot;fast_fetch_first_response&quot;
              }
            ],
            &quot;op&quot;: &quot;deliver&quot;,
            &quot;target&quot;: &quot;__compiled_model_context__&quot;
          }
        ],
        &quot;effect&quot;: &quot;model_observe&quot;,
        &quot;evidences&quot;: [
          {
            &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
            &quot;rule_id&quot;: &quot;EM10&quot;
          },
          {
            &quot;end_line&quot;: 9,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The first fast.fetch attempt is made only when FAST_KEY is present.&quot;,
            &quot;start_line&quot;: 9
          }
        ]
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 9,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The agent runtime tries fast.fetch first with source_id and FAST_KEY.&quot;,
        &quot;start_line&quot;: 9,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 9,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The instruction output is the first fast.fetch response.&quot;,
            &quot;start_line&quot;: 9
          }
        ],
        &quot;output_index&quot;: 0,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;fast_fetch_first_response&quot;
        }
      }
    ],
    &quot;precedence&quot;: [
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 0,
          &quot;op_index&quot;: 1
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 0,
          &quot;op_index&quot;: 0
        }
      },
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 1,
          &quot;op_index&quot;: 0
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 0,
          &quot;op_index&quot;: 1
        }
      }
    ],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 9,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The instruction output is the first fast.fetch response.&quot;,
          &quot;start_line&quot;: 9
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;fast_fetch_first_response&quot;
      }
    }
  ],
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 9,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;fast.fetch is called with source_id and FAST_KEY.&quot;,
          &quot;start_line&quot;: 9
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 1,
          &quot;kind&quot;: &quot;input&quot;
        },
        {
          &quot;index&quot;: 2,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;fast_fetch&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 9,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;Acquire the first fast.fetch response.&quot;,
          &quot;start_line&quot;: 9
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 1,
          &quot;kind&quot;: &quot;input&quot;
        },
        {
          &quot;index&quot;: 2,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;location&quot;: &quot;fast_fetch&quot;,
      &quot;op&quot;: &quot;receive&quot;,
      &quot;output&quot;: &quot;fast_fetch_first_response&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
          &quot;rule_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;end_line&quot;: 9,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The first fast.fetch attempt is made only when FAST_KEY is present.&quot;,
          &quot;start_line&quot;: 9
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;fast_fetch_first_response&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;__compiled_model_context__&quot;
    }
  ]
}</pre>

</details>

## ir_008 · dispatch

Block: block_004; Operator: agent_runtime.

IR inputs: []

IR outputs: []

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| — | No effect event | — | — | — | Entry/exit states and result bindings remain available |

Entry/exit changes: 

- Location bindings are unchanged; this does not imply absence of observation or sending.

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;empty_effect_evidences&quot;: [
      {
        &quot;end_line&quot;: 10,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;This dispatch controls the next step without content processing.&quot;,
        &quot;start_line&quot;: 9
      }
    ],
    &quot;events&quot;: [],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 10,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The workflow dispatches to inspect the first fast.fetch result.&quot;,
        &quot;start_line&quot;: 9,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [],
  &quot;steps&quot;: []
}</pre>

</details>

## ir_009 · classify_fast_fetch_outcome

Block: block_005; Operator: agent_runtime.

IR inputs: 0: result_004

IR outputs: 0: result_005, 1: result_006

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: [
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 1
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 2
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 1
      }
    }
  ]
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| 1.1 | model_observe (program-generated, statically possible) | deliver | 0: D020 | model_context: Current model processing context | — |
| 2.1 | transform | compute | 0: D020 | — | 0: D018 |
| 2.2 | transform | compute | 0: D018 | — | 0: D002 |
| 2.3 | transform | select_part | 0: D020 | — | 0: D005 |

Entry/exit changes: 

- `result: result_005`: Unbound → D018
- `result: result_006`: Unbound → D005

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
                &quot;rule_id&quot;: &quot;EM10&quot;
              },
              {
                &quot;end_line&quot;: 10,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The first fast.fetch attempt is classified as success, transient failure, or non-transient failure.&quot;,
                &quot;start_line&quot;: 10
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;index&quot;: 0,
                &quot;kind&quot;: &quot;input&quot;
              }
            ],
            &quot;op&quot;: &quot;deliver&quot;,
            &quot;target&quot;: &quot;__compiled_model_context__&quot;
          }
        ],
        &quot;effect&quot;: &quot;model_observe&quot;,
        &quot;evidences&quot;: [
          {
            &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
            &quot;rule_id&quot;: &quot;EM10&quot;
          },
          {
            &quot;end_line&quot;: 10,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The first fast.fetch attempt is classified as success, transient failure, or non-transient failure.&quot;,
            &quot;start_line&quot;: 10
          }
        ]
      },
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;dependencies&quot;: [
              &quot;possible&quot;
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 10,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;Classify the first fast.fetch outcome.&quot;,
                &quot;start_line&quot;: 10
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;index&quot;: 0,
                &quot;kind&quot;: &quot;input&quot;
              }
            ],
            &quot;op&quot;: &quot;compute&quot;,
            &quot;output&quot;: &quot;fast_fetch_first_outcome&quot;
          },
          {
            &quot;dependencies&quot;: [
              &quot;derived&quot;
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 10,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The retry condition is a transient first failure.&quot;,
                &quot;start_line&quot;: 10
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;kind&quot;: &quot;local&quot;,
                &quot;name&quot;: &quot;fast_fetch_first_outcome&quot;
              }
            ],
            &quot;op&quot;: &quot;compute&quot;,
            &quot;output&quot;: &quot;fast_fetch_first_transient&quot;
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 13,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The successful response has a body value to return unchanged.&quot;,
                &quot;start_line&quot;: 13
              }
            ],
            &quot;input&quot;: {
              &quot;index&quot;: 0,
              &quot;kind&quot;: &quot;input&quot;
            },
            &quot;op&quot;: &quot;select_part&quot;,
            &quot;output&quot;: &quot;fast_fetch_first_body&quot;,
            &quot;path&quot;: [
              &quot;body&quot;
            ]
          }
        ],
        &quot;effect&quot;: &quot;transform&quot;,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 10,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;Classify the first fast.fetch response and extract its body.&quot;,
            &quot;start_line&quot;: 10
          }
        ]
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 10,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The agent runtime classifies the first fast.fetch attempt outcome.&quot;,
        &quot;start_line&quot;: 10,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 10,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The instruction classifies the first fast.fetch outcome.&quot;,
            &quot;start_line&quot;: 10
          }
        ],
        &quot;output_index&quot;: 0,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;fast_fetch_first_outcome&quot;
        }
      },
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 13,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The instruction extracts the response body.&quot;,
            &quot;start_line&quot;: 13
          }
        ],
        &quot;output_index&quot;: 1,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;fast_fetch_first_body&quot;
        }
      }
    ],
    &quot;precedence&quot;: [
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 1,
          &quot;op_index&quot;: 0
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 0,
          &quot;op_index&quot;: 0
        }
      },
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 1,
          &quot;op_index&quot;: 1
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 1,
          &quot;op_index&quot;: 0
        }
      },
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 1,
          &quot;op_index&quot;: 2
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 1,
          &quot;op_index&quot;: 1
        }
      }
    ],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 10,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The instruction classifies the first fast.fetch outcome.&quot;,
          &quot;start_line&quot;: 10
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;fast_fetch_first_outcome&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 13,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The instruction extracts the response body.&quot;,
          &quot;start_line&quot;: 13
        }
      ],
      &quot;output_index&quot;: 1,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;fast_fetch_first_body&quot;
      }
    }
  ],
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
          &quot;rule_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;end_line&quot;: 10,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The first fast.fetch attempt is classified as success, transient failure, or non-transient failure.&quot;,
          &quot;start_line&quot;: 10
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;__compiled_model_context__&quot;
    },
    {
      &quot;dependencies&quot;: [
        &quot;possible&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 10,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;Classify the first fast.fetch outcome.&quot;,
          &quot;start_line&quot;: 10
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;fast_fetch_first_outcome&quot;
    },
    {
      &quot;dependencies&quot;: [
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 10,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The retry condition is a transient first failure.&quot;,
          &quot;start_line&quot;: 10
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;fast_fetch_first_outcome&quot;
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;fast_fetch_first_transient&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 13,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The successful response has a body value to return unchanged.&quot;,
          &quot;start_line&quot;: 13
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;fast_fetch_first_body&quot;,
      &quot;path&quot;: [
        &quot;body&quot;
      ]
    }
  ]
}</pre>

</details>

## ir_010 · dispatch

Block: block_005; Operator: agent_runtime.

IR inputs: 0: result_005

IR outputs: []

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| — | No effect event | — | — | — | Entry/exit states and result bindings remain available |

Entry/exit changes: 

- Location bindings are unchanged; this does not imply absence of observation or sending.

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;empty_effect_evidences&quot;: [
      {
        &quot;end_line&quot;: 10,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;This dispatch controls the next step without content processing.&quot;,
        &quot;start_line&quot;: 10
      }
    ],
    &quot;events&quot;: [],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 10,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The workflow dispatches according to the first fast.fetch outcome.&quot;,
        &quot;start_line&quot;: 10,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [],
  &quot;steps&quot;: []
}</pre>

</details>

## ir_011 · fast.fetch

Block: block_006; Operator: agent_runtime.

IR inputs: 0: fast.fetch, 1: result_001, 2: result_002

IR outputs: 0: result_007

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: [
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 1
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 1
      }
    }
  ]
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| 1.1 | Unlabeled data operation | deliver | 0: D019; 1: D011 | tool: fast.fetch | — |
| 1.2 | Unlabeled data operation | receive | 0: D019; 1: D011 | tool: fast.fetch | 0: D017 |
| 2.1 | model_observe (program-generated, statically possible) | deliver | 0: D017 | model_context: Current model processing context | — |

Entry/exit changes: 

- `result: result_007`: Unbound → D017

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 10,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;fast.fetch is retried with source_id and FAST_KEY.&quot;,
                &quot;start_line&quot;: 10
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;index&quot;: 1,
                &quot;kind&quot;: &quot;input&quot;
              },
              {
                &quot;index&quot;: 2,
                &quot;kind&quot;: &quot;input&quot;
              }
            ],
            &quot;op&quot;: &quot;deliver&quot;,
            &quot;target&quot;: &quot;fast_fetch&quot;
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 10,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;Acquire the fast.fetch retry response.&quot;,
                &quot;start_line&quot;: 10
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;index&quot;: 1,
                &quot;kind&quot;: &quot;input&quot;
              },
              {
                &quot;index&quot;: 2,
                &quot;kind&quot;: &quot;input&quot;
              }
            ],
            &quot;location&quot;: &quot;fast_fetch&quot;,
            &quot;op&quot;: &quot;receive&quot;,
            &quot;output&quot;: &quot;fast_fetch_retry_response&quot;
          }
        ],
        &quot;effect&quot;: null
      },
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
                &quot;rule_id&quot;: &quot;EM10&quot;
              },
              {
                &quot;end_line&quot;: 10,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The single retry of fast.fetch occurs only on a transient first failure.&quot;,
                &quot;start_line&quot;: 10
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;kind&quot;: &quot;local&quot;,
                &quot;name&quot;: &quot;fast_fetch_retry_response&quot;
              }
            ],
            &quot;op&quot;: &quot;deliver&quot;,
            &quot;target&quot;: &quot;__compiled_model_context__&quot;
          }
        ],
        &quot;effect&quot;: &quot;model_observe&quot;,
        &quot;evidences&quot;: [
          {
            &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
            &quot;rule_id&quot;: &quot;EM10&quot;
          },
          {
            &quot;end_line&quot;: 10,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The single retry of fast.fetch occurs only on a transient first failure.&quot;,
            &quot;start_line&quot;: 10
          }
        ]
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 10,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The agent runtime retries fast.fetch once on a transient first failure.&quot;,
        &quot;start_line&quot;: 10,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 10,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The instruction output is the fast.fetch retry response.&quot;,
            &quot;start_line&quot;: 10
          }
        ],
        &quot;output_index&quot;: 0,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;fast_fetch_retry_response&quot;
        }
      }
    ],
    &quot;precedence&quot;: [
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 0,
          &quot;op_index&quot;: 1
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 0,
          &quot;op_index&quot;: 0
        }
      },
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 1,
          &quot;op_index&quot;: 0
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 0,
          &quot;op_index&quot;: 1
        }
      }
    ],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 10,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The instruction output is the fast.fetch retry response.&quot;,
          &quot;start_line&quot;: 10
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;fast_fetch_retry_response&quot;
      }
    }
  ],
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 10,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;fast.fetch is retried with source_id and FAST_KEY.&quot;,
          &quot;start_line&quot;: 10
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 1,
          &quot;kind&quot;: &quot;input&quot;
        },
        {
          &quot;index&quot;: 2,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;fast_fetch&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 10,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;Acquire the fast.fetch retry response.&quot;,
          &quot;start_line&quot;: 10
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 1,
          &quot;kind&quot;: &quot;input&quot;
        },
        {
          &quot;index&quot;: 2,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;location&quot;: &quot;fast_fetch&quot;,
      &quot;op&quot;: &quot;receive&quot;,
      &quot;output&quot;: &quot;fast_fetch_retry_response&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
          &quot;rule_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;end_line&quot;: 10,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The single retry of fast.fetch occurs only on a transient first failure.&quot;,
          &quot;start_line&quot;: 10
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;fast_fetch_retry_response&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;__compiled_model_context__&quot;
    }
  ]
}</pre>

</details>

## ir_012 · dispatch

Block: block_006; Operator: agent_runtime.

IR inputs: []

IR outputs: []

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| — | No effect event | — | — | — | Entry/exit states and result bindings remain available |

Entry/exit changes: 

- Location bindings are unchanged; this does not imply absence of observation or sending.

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;empty_effect_evidences&quot;: [
      {
        &quot;end_line&quot;: 10,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;This dispatch controls the next step without content processing.&quot;,
        &quot;start_line&quot;: 10
      }
    ],
    &quot;events&quot;: [],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 10,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The workflow dispatches to inspect the fast.fetch retry result.&quot;,
        &quot;start_line&quot;: 10,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [],
  &quot;steps&quot;: []
}</pre>

</details>

## ir_013 · classify_fast_fetch_outcome

Block: block_007; Operator: agent_runtime.

IR inputs: 0: result_007

IR outputs: 0: result_008, 1: result_009

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: [
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 1
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 0
      }
    }
  ]
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| 1.1 | model_observe (program-generated, statically possible) | deliver | 0: D017 | model_context: Current model processing context | — |
| 2.1 | transform | compute | 0: D017 | — | 0: D012 |
| 2.2 | transform | select_part | 0: D017 | — | 0: D015 |

Entry/exit changes: 

- `result: result_008`: Unbound → D012
- `result: result_009`: Unbound → D015

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8506fe4405e816156ca9a758c93cf271a381e091a43360428b426dec7720adce&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a0a78e85803d69c6f4f9f0a5adf2c329feab79987fc4458c9d26a9cfdc6edcdf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
                &quot;rule_id&quot;: &quot;EM10&quot;
              },
              {
                &quot;end_line&quot;: 11,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The retry response is classified and its body is extracted.&quot;,
                &quot;start_line&quot;: 10
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;index&quot;: 0,
                &quot;kind&quot;: &quot;input&quot;
              }
            ],
            &quot;op&quot;: &quot;deliver&quot;,
            &quot;target&quot;: &quot;__compiled_model_context__&quot;
          }
        ],
        &quot;effect&quot;: &quot;model_observe&quot;,
        &quot;evidences&quot;: [
          {
            &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
            &quot;rule_id&quot;: &quot;EM10&quot;
          },
          {
            &quot;end_line&quot;: 11,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The retry response is classified and its body is extracted.&quot;,
            &quot;start_line&quot;: 10
          }
        ]
      },
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;dependencies&quot;: [
              &quot;possible&quot;
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 11,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;Classify the fast.fetch retry outcome.&quot;,
                &quot;start_line&quot;: 10
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;index&quot;: 0,
                &quot;kind&quot;: &quot;input&quot;
              }
            ],
            &quot;op&quot;: &quot;compute&quot;,
            &quot;output&quot;: &quot;fast_fetch_retry_outcome&quot;
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 13,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The successful retry response has a body value to return unchanged.&quot;,
                &quot;start_line&quot;: 13
              }
            ],
            &quot;input&quot;: {
              &quot;index&quot;: 0,
              &quot;kind&quot;: &quot;input&quot;
            },
            &quot;op&quot;: &quot;select_part&quot;,
            &quot;output&quot;: &quot;fast_fetch_retry_body&quot;,
            &quot;path&quot;: [
              &quot;body&quot;
            ]
          }
        ],
        &quot;effect&quot;: &quot;transform&quot;,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 11,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;Classify the fast.fetch retry response and extract its body.&quot;,
            &quot;start_line&quot;: 10
          }
        ]
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 11,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The agent runtime classifies the fast.fetch retry outcome.&quot;,
        &quot;start_line&quot;: 10,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 11,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The instruction classifies the fast.fetch retry outcome.&quot;,
            &quot;start_line&quot;: 10
          }
        ],
        &quot;output_index&quot;: 0,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;fast_fetch_retry_outcome&quot;
        }
      },
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 13,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The instruction extracts the retry response body.&quot;,
            &quot;start_line&quot;: 13
          }
        ],
        &quot;output_index&quot;: 1,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;fast_fetch_retry_body&quot;
        }
      }
    ],
    &quot;precedence&quot;: [
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 1,
          &quot;op_index&quot;: 0
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 0,
          &quot;op_index&quot;: 0
        }
      },
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 1,
          &quot;op_index&quot;: 1
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 1,
          &quot;op_index&quot;: 0
        }
      }
    ],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 11,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The instruction classifies the fast.fetch retry outcome.&quot;,
          &quot;start_line&quot;: 10
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;fast_fetch_retry_outcome&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 13,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The instruction extracts the retry response body.&quot;,
          &quot;start_line&quot;: 13
        }
      ],
      &quot;output_index&quot;: 1,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;fast_fetch_retry_body&quot;
      }
    }
  ],
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
          &quot;rule_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;end_line&quot;: 11,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The retry response is classified and its body is extracted.&quot;,
          &quot;start_line&quot;: 10
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;__compiled_model_context__&quot;
    },
    {
      &quot;dependencies&quot;: [
        &quot;possible&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 11,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;Classify the fast.fetch retry outcome.&quot;,
          &quot;start_line&quot;: 10
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;fast_fetch_retry_outcome&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 13,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The successful retry response has a body value to return unchanged.&quot;,
          &quot;start_line&quot;: 13
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;fast_fetch_retry_body&quot;,
      &quot;path&quot;: [
        &quot;body&quot;
      ]
    }
  ]
}</pre>

</details>

## ir_014 · dispatch

Block: block_007; Operator: agent_runtime.

IR inputs: 0: result_008

IR outputs: []

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| — | No effect event | — | — | — | Entry/exit states and result bindings remain available |

Entry/exit changes: 

- Location bindings are unchanged; this does not imply absence of observation or sending.

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8506fe4405e816156ca9a758c93cf271a381e091a43360428b426dec7720adce&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a0a78e85803d69c6f4f9f0a5adf2c329feab79987fc4458c9d26a9cfdc6edcdf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8506fe4405e816156ca9a758c93cf271a381e091a43360428b426dec7720adce&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a0a78e85803d69c6f4f9f0a5adf2c329feab79987fc4458c9d26a9cfdc6edcdf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;empty_effect_evidences&quot;: [
      {
        &quot;end_line&quot;: 11,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;This dispatch controls the next step without content processing.&quot;,
        &quot;start_line&quot;: 11
      }
    ],
    &quot;events&quot;: [],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 11,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The workflow dispatches to archive.fetch after fast.fetch failures.&quot;,
        &quot;start_line&quot;: 11,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [],
  &quot;steps&quot;: []
}</pre>

</details>

## ir_015 · archive.fetch

Block: block_008; Operator: agent_runtime.

IR inputs: 0: archive.fetch, 1: result_001

IR outputs: 0: result_010

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: [
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 1
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 1
      }
    }
  ]
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| 1.1 | Unlabeled data operation | deliver | 0: D019 | tool: archive.fetch | — |
| 1.2 | Unlabeled data operation | receive | 0: D019 | tool: archive.fetch | 0: D009 |
| 2.1 | model_observe (program-generated, statically possible) | deliver | 0: D009 | model_context: Current model processing context | — |

Entry/exit changes: 

- `result: result_010`: Unbound → D009

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8506fe4405e816156ca9a758c93cf271a381e091a43360428b426dec7720adce&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a0a78e85803d69c6f4f9f0a5adf2c329feab79987fc4458c9d26a9cfdc6edcdf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8506fe4405e816156ca9a758c93cf271a381e091a43360428b426dec7720adce&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a0a78e85803d69c6f4f9f0a5adf2c329feab79987fc4458c9d26a9cfdc6edcdf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_480afd2db542978c3e68e2d66334c9c896e41164743179224dc2eabc438ee797&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 12,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;archive.fetch is called with source_id only.&quot;,
                &quot;start_line&quot;: 11
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;index&quot;: 1,
                &quot;kind&quot;: &quot;input&quot;
              }
            ],
            &quot;op&quot;: &quot;deliver&quot;,
            &quot;target&quot;: &quot;archive_fetch&quot;
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 12,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;Acquire the archive.fetch response.&quot;,
                &quot;start_line&quot;: 11
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;index&quot;: 1,
                &quot;kind&quot;: &quot;input&quot;
              }
            ],
            &quot;location&quot;: &quot;archive_fetch&quot;,
            &quot;op&quot;: &quot;receive&quot;,
            &quot;output&quot;: &quot;archive_fetch_response&quot;
          }
        ],
        &quot;effect&quot;: null
      },
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
                &quot;rule_id&quot;: &quot;EM10&quot;
              },
              {
                &quot;end_line&quot;: 12,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;archive.fetch is called at most once with source_id as its only argument.&quot;,
                &quot;start_line&quot;: 11
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;kind&quot;: &quot;local&quot;,
                &quot;name&quot;: &quot;archive_fetch_response&quot;
              }
            ],
            &quot;op&quot;: &quot;deliver&quot;,
            &quot;target&quot;: &quot;__compiled_model_context__&quot;
          }
        ],
        &quot;effect&quot;: &quot;model_observe&quot;,
        &quot;evidences&quot;: [
          {
            &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
            &quot;rule_id&quot;: &quot;EM10&quot;
          },
          {
            &quot;end_line&quot;: 12,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;archive.fetch is called at most once with source_id as its only argument.&quot;,
            &quot;start_line&quot;: 11
          }
        ]
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 12,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The agent runtime calls archive.fetch with source_id only.&quot;,
        &quot;start_line&quot;: 11,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 12,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The instruction output is the archive.fetch response.&quot;,
            &quot;start_line&quot;: 11
          }
        ],
        &quot;output_index&quot;: 0,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;archive_fetch_response&quot;
        }
      }
    ],
    &quot;precedence&quot;: [
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 0,
          &quot;op_index&quot;: 1
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 0,
          &quot;op_index&quot;: 0
        }
      },
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 1,
          &quot;op_index&quot;: 0
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 0,
          &quot;op_index&quot;: 1
        }
      }
    ],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 12,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The instruction output is the archive.fetch response.&quot;,
          &quot;start_line&quot;: 11
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;archive_fetch_response&quot;
      }
    }
  ],
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 12,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;archive.fetch is called with source_id only.&quot;,
          &quot;start_line&quot;: 11
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 1,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;archive_fetch&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 12,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;Acquire the archive.fetch response.&quot;,
          &quot;start_line&quot;: 11
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 1,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;location&quot;: &quot;archive_fetch&quot;,
      &quot;op&quot;: &quot;receive&quot;,
      &quot;output&quot;: &quot;archive_fetch_response&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
          &quot;rule_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;end_line&quot;: 12,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;archive.fetch is called at most once with source_id as its only argument.&quot;,
          &quot;start_line&quot;: 11
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;archive_fetch_response&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;__compiled_model_context__&quot;
    }
  ]
}</pre>

</details>

## ir_016 · dispatch

Block: block_008; Operator: agent_runtime.

IR inputs: []

IR outputs: []

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| — | No effect event | — | — | — | Entry/exit states and result bindings remain available |

Entry/exit changes: 

- Location bindings are unchanged; this does not imply absence of observation or sending.

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8506fe4405e816156ca9a758c93cf271a381e091a43360428b426dec7720adce&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a0a78e85803d69c6f4f9f0a5adf2c329feab79987fc4458c9d26a9cfdc6edcdf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_480afd2db542978c3e68e2d66334c9c896e41164743179224dc2eabc438ee797&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8506fe4405e816156ca9a758c93cf271a381e091a43360428b426dec7720adce&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a0a78e85803d69c6f4f9f0a5adf2c329feab79987fc4458c9d26a9cfdc6edcdf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_480afd2db542978c3e68e2d66334c9c896e41164743179224dc2eabc438ee797&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;empty_effect_evidences&quot;: [
      {
        &quot;end_line&quot;: 12,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;This dispatch controls the next step without content processing.&quot;,
        &quot;start_line&quot;: 11
      }
    ],
    &quot;events&quot;: [],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 12,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The workflow dispatches to inspect the archive.fetch result.&quot;,
        &quot;start_line&quot;: 11,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [],
  &quot;steps&quot;: []
}</pre>

</details>

## ir_017 · classify_fetch_outcome

Block: block_009; Operator: agent_runtime.

IR inputs: 0: result_010

IR outputs: 0: result_011, 1: result_012, 2: result_013

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: [
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 1
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 2
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 1
      }
    }
  ]
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| 1.1 | model_observe (program-generated, statically possible) | deliver | 0: D009 | model_context: Current model processing context | — |
| 2.1 | transform | compute | 0: D009 | — | 0: D003 |
| 2.2 | transform | select_part | 0: D009 | — | 0: D004 |
| 2.3 | transform | select_part | 0: D009 | — | 0: D006 |

Entry/exit changes: 

- `result: result_011`: Unbound → D003
- `result: result_012`: Unbound → D004
- `result: result_013`: Unbound → D006

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8506fe4405e816156ca9a758c93cf271a381e091a43360428b426dec7720adce&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a0a78e85803d69c6f4f9f0a5adf2c329feab79987fc4458c9d26a9cfdc6edcdf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_480afd2db542978c3e68e2d66334c9c896e41164743179224dc2eabc438ee797&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8506fe4405e816156ca9a758c93cf271a381e091a43360428b426dec7720adce&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a0a78e85803d69c6f4f9f0a5adf2c329feab79987fc4458c9d26a9cfdc6edcdf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_480afd2db542978c3e68e2d66334c9c896e41164743179224dc2eabc438ee797&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0771a4eee1aff7b98e695d99229320db7ec7772c7dbc887a4cb4e39e448769d0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0e4b6ae7e7dbc77b14dbcb9824ec27a3ddb6797f2772edb7b746cf51ec933b97&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_229ecf9b1be5d6d01b845d620bbfa58ed40c6c250050e8a7ad35af3651bf379e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
                &quot;rule_id&quot;: &quot;EM10&quot;
              },
              {
                &quot;end_line&quot;: 14,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The archive.fetch response is classified and its body or error is extracted.&quot;,
                &quot;start_line&quot;: 13
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;index&quot;: 0,
                &quot;kind&quot;: &quot;input&quot;
              }
            ],
            &quot;op&quot;: &quot;deliver&quot;,
            &quot;target&quot;: &quot;__compiled_model_context__&quot;
          }
        ],
        &quot;effect&quot;: &quot;model_observe&quot;,
        &quot;evidences&quot;: [
          {
            &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
            &quot;rule_id&quot;: &quot;EM10&quot;
          },
          {
            &quot;end_line&quot;: 14,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The archive.fetch response is classified and its body or error is extracted.&quot;,
            &quot;start_line&quot;: 13
          }
        ]
      },
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;dependencies&quot;: [
              &quot;possible&quot;
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 14,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;Classify the archive.fetch outcome.&quot;,
                &quot;start_line&quot;: 13
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;index&quot;: 0,
                &quot;kind&quot;: &quot;input&quot;
              }
            ],
            &quot;op&quot;: &quot;compute&quot;,
            &quot;output&quot;: &quot;archive_fetch_outcome&quot;
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 13,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The successful archive.fetch response has a body value to return unchanged.&quot;,
                &quot;start_line&quot;: 13
              }
            ],
            &quot;input&quot;: {
              &quot;index&quot;: 0,
              &quot;kind&quot;: &quot;input&quot;
            },
            &quot;op&quot;: &quot;select_part&quot;,
            &quot;output&quot;: &quot;archive_fetch_body&quot;,
            &quot;path&quot;: [
              &quot;body&quot;
            ]
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 14,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;A failed archive.fetch response has an error value to return.&quot;,
                &quot;start_line&quot;: 14
              }
            ],
            &quot;input&quot;: {
              &quot;index&quot;: 0,
              &quot;kind&quot;: &quot;input&quot;
            },
            &quot;op&quot;: &quot;select_part&quot;,
            &quot;output&quot;: &quot;archive_fetch_error&quot;,
            &quot;path&quot;: [
              &quot;error&quot;
            ]
          }
        ],
        &quot;effect&quot;: &quot;transform&quot;,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 14,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;Classify the archive.fetch result and extract body or error.&quot;,
            &quot;start_line&quot;: 13
          }
        ]
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 13,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The agent runtime classifies the archive.fetch result.&quot;,
        &quot;start_line&quot;: 13,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 14,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The instruction classifies the archive.fetch outcome.&quot;,
            &quot;start_line&quot;: 13
          }
        ],
        &quot;output_index&quot;: 0,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;archive_fetch_outcome&quot;
        }
      },
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 13,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The instruction extracts the archive.fetch body.&quot;,
            &quot;start_line&quot;: 13
          }
        ],
        &quot;output_index&quot;: 1,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;archive_fetch_body&quot;
        }
      },
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 14,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The instruction extracts the archive.fetch error.&quot;,
            &quot;start_line&quot;: 14
          }
        ],
        &quot;output_index&quot;: 2,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;archive_fetch_error&quot;
        }
      }
    ],
    &quot;precedence&quot;: [
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 1,
          &quot;op_index&quot;: 0
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 0,
          &quot;op_index&quot;: 0
        }
      },
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 1,
          &quot;op_index&quot;: 1
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 1,
          &quot;op_index&quot;: 0
        }
      },
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 1,
          &quot;op_index&quot;: 2
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 1,
          &quot;op_index&quot;: 1
        }
      }
    ],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 14,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The instruction classifies the archive.fetch outcome.&quot;,
          &quot;start_line&quot;: 13
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;archive_fetch_outcome&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 13,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The instruction extracts the archive.fetch body.&quot;,
          &quot;start_line&quot;: 13
        }
      ],
      &quot;output_index&quot;: 1,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;archive_fetch_body&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 14,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The instruction extracts the archive.fetch error.&quot;,
          &quot;start_line&quot;: 14
        }
      ],
      &quot;output_index&quot;: 2,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;archive_fetch_error&quot;
      }
    }
  ],
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
          &quot;rule_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;end_line&quot;: 14,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The archive.fetch response is classified and its body or error is extracted.&quot;,
          &quot;start_line&quot;: 13
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;__compiled_model_context__&quot;
    },
    {
      &quot;dependencies&quot;: [
        &quot;possible&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 14,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;Classify the archive.fetch outcome.&quot;,
          &quot;start_line&quot;: 13
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;archive_fetch_outcome&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 13,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The successful archive.fetch response has a body value to return unchanged.&quot;,
          &quot;start_line&quot;: 13
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;archive_fetch_body&quot;,
      &quot;path&quot;: [
        &quot;body&quot;
      ]
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 14,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;A failed archive.fetch response has an error value to return.&quot;,
          &quot;start_line&quot;: 14
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;archive_fetch_error&quot;,
      &quot;path&quot;: [
        &quot;error&quot;
      ]
    }
  ]
}</pre>

</details>

## ir_018 · dispatch

Block: block_009; Operator: agent_runtime.

IR inputs: 0: result_011

IR outputs: []

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| — | No effect event | — | — | — | Entry/exit states and result bindings remain available |

Entry/exit changes: 

- Location bindings are unchanged; this does not imply absence of observation or sending.

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8506fe4405e816156ca9a758c93cf271a381e091a43360428b426dec7720adce&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a0a78e85803d69c6f4f9f0a5adf2c329feab79987fc4458c9d26a9cfdc6edcdf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_480afd2db542978c3e68e2d66334c9c896e41164743179224dc2eabc438ee797&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0771a4eee1aff7b98e695d99229320db7ec7772c7dbc887a4cb4e39e448769d0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0e4b6ae7e7dbc77b14dbcb9824ec27a3ddb6797f2772edb7b746cf51ec933b97&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_229ecf9b1be5d6d01b845d620bbfa58ed40c6c250050e8a7ad35af3651bf379e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8506fe4405e816156ca9a758c93cf271a381e091a43360428b426dec7720adce&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a0a78e85803d69c6f4f9f0a5adf2c329feab79987fc4458c9d26a9cfdc6edcdf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_480afd2db542978c3e68e2d66334c9c896e41164743179224dc2eabc438ee797&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0771a4eee1aff7b98e695d99229320db7ec7772c7dbc887a4cb4e39e448769d0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0e4b6ae7e7dbc77b14dbcb9824ec27a3ddb6797f2772edb7b746cf51ec933b97&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_229ecf9b1be5d6d01b845d620bbfa58ed40c6c250050e8a7ad35af3651bf379e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;empty_effect_evidences&quot;: [
      {
        &quot;end_line&quot;: 14,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;This dispatch controls the next step without content processing.&quot;,
        &quot;start_line&quot;: 13
      }
    ],
    &quot;events&quot;: [],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 14,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The workflow dispatches according to the archive.fetch outcome.&quot;,
        &quot;start_line&quot;: 13,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [],
  &quot;steps&quot;: []
}</pre>

</details>

## ir_019 · append_final_status_to_local_status_file

Block: block_010; Operator: agent_runtime.

IR inputs: 0: status.txt, 1: result_005

IR outputs: []

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | 0: D018 | storage: status.txt | storage: status.txt: D010 → D008 (strong) |

Entry/exit changes: 

- `storage: status.txt`: D010 → D008

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_34a889821dc06724cfa32c6223be343388d1927a56a60f60b67783130c40bd13&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 16,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;Append the final status to local status.txt on this return path.&quot;,
                &quot;start_line&quot;: 16
              }
            ],
            &quot;input&quot;: {
              &quot;index&quot;: 1,
              &quot;kind&quot;: &quot;input&quot;
            },
            &quot;mode&quot;: &quot;append&quot;,
            &quot;op&quot;: &quot;write&quot;,
            &quot;target&quot;: &quot;status_file&quot;
          }
        ],
        &quot;effect&quot;: &quot;fs_write&quot;,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 16,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;Append the final status to local status.txt.&quot;,
            &quot;start_line&quot;: 16
          }
        ]
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 16,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The agent runtime appends the first fast.fetch outcome to status.txt.&quot;,
        &quot;start_line&quot;: 16,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [],
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 16,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;Append the final status to local status.txt on this return path.&quot;,
          &quot;start_line&quot;: 16
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 1,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;mode&quot;: &quot;append&quot;,
      &quot;op&quot;: &quot;write&quot;,
      &quot;target&quot;: &quot;status_file&quot;
    }
  ]
}</pre>

</details>

## ir_020 · return

Block: block_010; Operator: agent_runtime.

IR inputs: 0: result_006

IR outputs: []

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| — | No effect event | — | — | — | Entry/exit states and result bindings remain available |

Entry/exit changes: 

- Location bindings are unchanged; this does not imply absence of observation or sending.

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_34a889821dc06724cfa32c6223be343388d1927a56a60f60b67783130c40bd13&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_34a889821dc06724cfa32c6223be343388d1927a56a60f60b67783130c40bd13&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;empty_effect_evidences&quot;: [
      {
        &quot;end_line&quot;: 13,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The return itself has no content effect; it returns the existing body value.&quot;,
        &quot;start_line&quot;: 13
      }
    ],
    &quot;events&quot;: [],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 13,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The workflow returns the first fast.fetch body.&quot;,
        &quot;start_line&quot;: 13,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [],
  &quot;steps&quot;: []
}</pre>

</details>

## ir_021 · append_final_status_to_local_status_file

Block: block_011; Operator: agent_runtime.

IR inputs: 0: status.txt, 1: result_008

IR outputs: []

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | 0: D012 | storage: status.txt | storage: status.txt: D010 → D021 (strong) |

Entry/exit changes: 

- `storage: status.txt`: D010 → D021

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8506fe4405e816156ca9a758c93cf271a381e091a43360428b426dec7720adce&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a0a78e85803d69c6f4f9f0a5adf2c329feab79987fc4458c9d26a9cfdc6edcdf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8506fe4405e816156ca9a758c93cf271a381e091a43360428b426dec7720adce&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a0a78e85803d69c6f4f9f0a5adf2c329feab79987fc4458c9d26a9cfdc6edcdf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f3904fe7f69f74662ba26214afdc8579d3fe5ff2f53af7a6cc5860746184d24b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 16,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;Append the final status to local status.txt on this return path.&quot;,
                &quot;start_line&quot;: 16
              }
            ],
            &quot;input&quot;: {
              &quot;index&quot;: 1,
              &quot;kind&quot;: &quot;input&quot;
            },
            &quot;mode&quot;: &quot;append&quot;,
            &quot;op&quot;: &quot;write&quot;,
            &quot;target&quot;: &quot;status_file&quot;
          }
        ],
        &quot;effect&quot;: &quot;fs_write&quot;,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 16,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;Append the final status to local status.txt.&quot;,
            &quot;start_line&quot;: 16
          }
        ]
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 16,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The agent runtime appends the fast.fetch retry outcome to status.txt.&quot;,
        &quot;start_line&quot;: 16,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [],
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 16,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;Append the final status to local status.txt on this return path.&quot;,
          &quot;start_line&quot;: 16
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 1,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;mode&quot;: &quot;append&quot;,
      &quot;op&quot;: &quot;write&quot;,
      &quot;target&quot;: &quot;status_file&quot;
    }
  ]
}</pre>

</details>

## ir_022 · return

Block: block_011; Operator: agent_runtime.

IR inputs: 0: result_009

IR outputs: []

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| — | No effect event | — | — | — | Entry/exit states and result bindings remain available |

Entry/exit changes: 

- Location bindings are unchanged; this does not imply absence of observation or sending.

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8506fe4405e816156ca9a758c93cf271a381e091a43360428b426dec7720adce&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a0a78e85803d69c6f4f9f0a5adf2c329feab79987fc4458c9d26a9cfdc6edcdf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f3904fe7f69f74662ba26214afdc8579d3fe5ff2f53af7a6cc5860746184d24b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8506fe4405e816156ca9a758c93cf271a381e091a43360428b426dec7720adce&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a0a78e85803d69c6f4f9f0a5adf2c329feab79987fc4458c9d26a9cfdc6edcdf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_f3904fe7f69f74662ba26214afdc8579d3fe5ff2f53af7a6cc5860746184d24b&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;empty_effect_evidences&quot;: [
      {
        &quot;end_line&quot;: 13,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The return itself has no content effect; it returns the existing body value.&quot;,
        &quot;start_line&quot;: 13
      }
    ],
    &quot;events&quot;: [],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 13,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The workflow returns the fast.fetch retry body.&quot;,
        &quot;start_line&quot;: 13,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [],
  &quot;steps&quot;: []
}</pre>

</details>

## ir_023 · append_final_status_to_local_status_file

Block: block_012; Operator: agent_runtime.

IR inputs: 0: status.txt, 1: result_011

IR outputs: []

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | 0: D003 | storage: status.txt | storage: status.txt: D010 → D013 (strong) |

Entry/exit changes: 

- `storage: status.txt`: D010 → D013

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8506fe4405e816156ca9a758c93cf271a381e091a43360428b426dec7720adce&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a0a78e85803d69c6f4f9f0a5adf2c329feab79987fc4458c9d26a9cfdc6edcdf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_480afd2db542978c3e68e2d66334c9c896e41164743179224dc2eabc438ee797&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0771a4eee1aff7b98e695d99229320db7ec7772c7dbc887a4cb4e39e448769d0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0e4b6ae7e7dbc77b14dbcb9824ec27a3ddb6797f2772edb7b746cf51ec933b97&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_229ecf9b1be5d6d01b845d620bbfa58ed40c6c250050e8a7ad35af3651bf379e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8506fe4405e816156ca9a758c93cf271a381e091a43360428b426dec7720adce&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a0a78e85803d69c6f4f9f0a5adf2c329feab79987fc4458c9d26a9cfdc6edcdf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_480afd2db542978c3e68e2d66334c9c896e41164743179224dc2eabc438ee797&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0771a4eee1aff7b98e695d99229320db7ec7772c7dbc887a4cb4e39e448769d0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0e4b6ae7e7dbc77b14dbcb9824ec27a3ddb6797f2772edb7b746cf51ec933b97&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_229ecf9b1be5d6d01b845d620bbfa58ed40c6c250050e8a7ad35af3651bf379e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8f385af1aea8d4b31ae086e17be72d6763bff848469d23226bf7299399ab729e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 16,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;Append the final status to local status.txt on this return path.&quot;,
                &quot;start_line&quot;: 16
              }
            ],
            &quot;input&quot;: {
              &quot;index&quot;: 1,
              &quot;kind&quot;: &quot;input&quot;
            },
            &quot;mode&quot;: &quot;append&quot;,
            &quot;op&quot;: &quot;write&quot;,
            &quot;target&quot;: &quot;status_file&quot;
          }
        ],
        &quot;effect&quot;: &quot;fs_write&quot;,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 16,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;Append the final status to local status.txt.&quot;,
            &quot;start_line&quot;: 16
          }
        ]
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 16,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The agent runtime appends the archive.fetch outcome to status.txt.&quot;,
        &quot;start_line&quot;: 16,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [],
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 16,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;Append the final status to local status.txt on this return path.&quot;,
          &quot;start_line&quot;: 16
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 1,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;mode&quot;: &quot;append&quot;,
      &quot;op&quot;: &quot;write&quot;,
      &quot;target&quot;: &quot;status_file&quot;
    }
  ]
}</pre>

</details>

## ir_024 · return

Block: block_012; Operator: agent_runtime.

IR inputs: 0: result_012

IR outputs: []

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| — | No effect event | — | — | — | Entry/exit states and result bindings remain available |

Entry/exit changes: 

- Location bindings are unchanged; this does not imply absence of observation or sending.

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8506fe4405e816156ca9a758c93cf271a381e091a43360428b426dec7720adce&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a0a78e85803d69c6f4f9f0a5adf2c329feab79987fc4458c9d26a9cfdc6edcdf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_480afd2db542978c3e68e2d66334c9c896e41164743179224dc2eabc438ee797&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0771a4eee1aff7b98e695d99229320db7ec7772c7dbc887a4cb4e39e448769d0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0e4b6ae7e7dbc77b14dbcb9824ec27a3ddb6797f2772edb7b746cf51ec933b97&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_229ecf9b1be5d6d01b845d620bbfa58ed40c6c250050e8a7ad35af3651bf379e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8f385af1aea8d4b31ae086e17be72d6763bff848469d23226bf7299399ab729e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8506fe4405e816156ca9a758c93cf271a381e091a43360428b426dec7720adce&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a0a78e85803d69c6f4f9f0a5adf2c329feab79987fc4458c9d26a9cfdc6edcdf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_480afd2db542978c3e68e2d66334c9c896e41164743179224dc2eabc438ee797&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0771a4eee1aff7b98e695d99229320db7ec7772c7dbc887a4cb4e39e448769d0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0e4b6ae7e7dbc77b14dbcb9824ec27a3ddb6797f2772edb7b746cf51ec933b97&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_229ecf9b1be5d6d01b845d620bbfa58ed40c6c250050e8a7ad35af3651bf379e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8f385af1aea8d4b31ae086e17be72d6763bff848469d23226bf7299399ab729e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;empty_effect_evidences&quot;: [
      {
        &quot;end_line&quot;: 13,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The return itself has no content effect; it returns the existing body value.&quot;,
        &quot;start_line&quot;: 13
      }
    ],
    &quot;events&quot;: [],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 13,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The workflow returns the archive.fetch body.&quot;,
        &quot;start_line&quot;: 13,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [],
  &quot;steps&quot;: []
}</pre>

</details>

## ir_025 · append_final_status_to_local_status_file

Block: block_013; Operator: agent_runtime.

IR inputs: 0: status.txt, 1: result_011

IR outputs: []

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | 0: D003 | storage: status.txt | storage: status.txt: D010 → D016 (strong) |

Entry/exit changes: 

- `storage: status.txt`: D010 → D016

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8506fe4405e816156ca9a758c93cf271a381e091a43360428b426dec7720adce&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a0a78e85803d69c6f4f9f0a5adf2c329feab79987fc4458c9d26a9cfdc6edcdf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_480afd2db542978c3e68e2d66334c9c896e41164743179224dc2eabc438ee797&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0771a4eee1aff7b98e695d99229320db7ec7772c7dbc887a4cb4e39e448769d0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0e4b6ae7e7dbc77b14dbcb9824ec27a3ddb6797f2772edb7b746cf51ec933b97&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_229ecf9b1be5d6d01b845d620bbfa58ed40c6c250050e8a7ad35af3651bf379e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8506fe4405e816156ca9a758c93cf271a381e091a43360428b426dec7720adce&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a0a78e85803d69c6f4f9f0a5adf2c329feab79987fc4458c9d26a9cfdc6edcdf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_480afd2db542978c3e68e2d66334c9c896e41164743179224dc2eabc438ee797&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0771a4eee1aff7b98e695d99229320db7ec7772c7dbc887a4cb4e39e448769d0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0e4b6ae7e7dbc77b14dbcb9824ec27a3ddb6797f2772edb7b746cf51ec933b97&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_229ecf9b1be5d6d01b845d620bbfa58ed40c6c250050e8a7ad35af3651bf379e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_aa1d5992f26391970bc8025270cfa77b526fcfd7af0f1ee515c67769321d91b8&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 16,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;Append the final status to local status.txt on this return path.&quot;,
                &quot;start_line&quot;: 16
              }
            ],
            &quot;input&quot;: {
              &quot;index&quot;: 1,
              &quot;kind&quot;: &quot;input&quot;
            },
            &quot;mode&quot;: &quot;append&quot;,
            &quot;op&quot;: &quot;write&quot;,
            &quot;target&quot;: &quot;status_file&quot;
          }
        ],
        &quot;effect&quot;: &quot;fs_write&quot;,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 16,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;Append the final status to local status.txt.&quot;,
            &quot;start_line&quot;: 16
          }
        ]
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 16,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The agent runtime appends the archive.fetch failure outcome to status.txt.&quot;,
        &quot;start_line&quot;: 16,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [],
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 16,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;Append the final status to local status.txt on this return path.&quot;,
          &quot;start_line&quot;: 16
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 1,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;mode&quot;: &quot;append&quot;,
      &quot;op&quot;: &quot;write&quot;,
      &quot;target&quot;: &quot;status_file&quot;
    }
  ]
}</pre>

</details>

## ir_026 · return

Block: block_013; Operator: agent_runtime.

IR inputs: 0: result_013

IR outputs: []

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| — | No effect event | — | — | — | Entry/exit states and result bindings remain available |

Entry/exit changes: 

- Location bindings are unchanged; this does not imply absence of observation or sending.

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8506fe4405e816156ca9a758c93cf271a381e091a43360428b426dec7720adce&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a0a78e85803d69c6f4f9f0a5adf2c329feab79987fc4458c9d26a9cfdc6edcdf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_480afd2db542978c3e68e2d66334c9c896e41164743179224dc2eabc438ee797&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0771a4eee1aff7b98e695d99229320db7ec7772c7dbc887a4cb4e39e448769d0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0e4b6ae7e7dbc77b14dbcb9824ec27a3ddb6797f2772edb7b746cf51ec933b97&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_229ecf9b1be5d6d01b845d620bbfa58ed40c6c250050e8a7ad35af3651bf379e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_aa1d5992f26391970bc8025270cfa77b526fcfd7af0f1ee515c67769321d91b8&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8506fe4405e816156ca9a758c93cf271a381e091a43360428b426dec7720adce&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_a0a78e85803d69c6f4f9f0a5adf2c329feab79987fc4458c9d26a9cfdc6edcdf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_480afd2db542978c3e68e2d66334c9c896e41164743179224dc2eabc438ee797&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_010&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0771a4eee1aff7b98e695d99229320db7ec7772c7dbc887a4cb4e39e448769d0&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_011&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_0e4b6ae7e7dbc77b14dbcb9824ec27a3ddb6797f2772edb7b746cf51ec933b97&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_012&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_229ecf9b1be5d6d01b845d620bbfa58ed40c6c250050e8a7ad35af3651bf379e&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_013&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;environment&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;user_request&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_aa1d5992f26391970bc8025270cfa77b526fcfd7af0f1ee515c67769321d91b8&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;status.txt&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;empty_effect_evidences&quot;: [
      {
        &quot;end_line&quot;: 14,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The return itself has no content effect; it returns the existing error value.&quot;,
        &quot;start_line&quot;: 14
      }
    ],
    &quot;events&quot;: [],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 14,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The workflow returns the archive.fetch error.&quot;,
        &quot;start_line&quot;: 14,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [],
  &quot;steps&quot;: []
}</pre>

</details>

## Data index

| Short name | Complete ID | Content form |
|---|---|---|
| D001 | data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c | known_parts |
| D002 | data_034fb865892d9f2d686b34c98ccc1a07d34601bf1cd1a760b5efc5599c5496b6 | opaque |
| D003 | data_0771a4eee1aff7b98e695d99229320db7ec7772c7dbc887a4cb4e39e448769d0 | opaque |
| D004 | data_0e4b6ae7e7dbc77b14dbcb9824ec27a3ddb6797f2772edb7b746cf51ec933b97 | opaque |
| D005 | data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c | opaque |
| D006 | data_229ecf9b1be5d6d01b845d620bbfa58ed40c6c250050e8a7ad35af3651bf379e | opaque |
| D007 | data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9 | opaque |
| D008 | data_34a889821dc06724cfa32c6223be343388d1927a56a60f60b67783130c40bd13 | opaque |
| D009 | data_480afd2db542978c3e68e2d66334c9c896e41164743179224dc2eabc438ee797 | known_parts |
| D010 | data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15 | opaque |
| D011 | data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d | opaque |
| D012 | data_8506fe4405e816156ca9a758c93cf271a381e091a43360428b426dec7720adce | opaque |
| D013 | data_8f385af1aea8d4b31ae086e17be72d6763bff848469d23226bf7299399ab729e | opaque |
| D014 | data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800 | known_parts |
| D015 | data_a0a78e85803d69c6f4f9f0a5adf2c329feab79987fc4458c9d26a9cfdc6edcdf | opaque |
| D016 | data_aa1d5992f26391970bc8025270cfa77b526fcfd7af0f1ee515c67769321d91b8 | opaque |
| D017 | data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0 | known_parts |
| D018 | data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0 | opaque |
| D019 | data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0 | opaque |
| D020 | data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2 | known_parts |
| D021 | data_f3904fe7f69f74662ba26214afdc8579d3fe5ff2f53af7a6cc5860746184d24b | opaque |

<details><summary>D001: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;,
        &quot;path&quot;: [
          &quot;source_id&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;runtime_context:user_request&quot;,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D002: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_034fb865892d9f2d686b34c98ccc1a07d34601bf1cd1a760b5efc5599c5496b6&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_009&#x27;, 1, 1]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D003: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_0771a4eee1aff7b98e695d99229320db7ec7772c7dbc887a4cb4e39e448769d0&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_017&#x27;, 1, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_480afd2db542978c3e68e2d66334c9c896e41164743179224dc2eabc438ee797&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_480afd2db542978c3e68e2d66334c9c896e41164743179224dc2eabc438ee797&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D004: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_0e4b6ae7e7dbc77b14dbcb9824ec27a3ddb6797f2772edb7b746cf51ec933b97&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_480afd2db542978c3e68e2d66334c9c896e41164743179224dc2eabc438ee797&quot;,
    &quot;path&quot;: [
      &quot;body&quot;
    ]
  }
}</pre>

</details>

<details><summary>D005: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;,
    &quot;path&quot;: [
      &quot;body&quot;
    ]
  }
}</pre>

</details>

<details><summary>D006: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_229ecf9b1be5d6d01b845d620bbfa58ed40c6c250050e8a7ad35af3651bf379e&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_480afd2db542978c3e68e2d66334c9c896e41164743179224dc2eabc438ee797&quot;,
    &quot;path&quot;: [
      &quot;error&quot;
    ]
  }
}</pre>

</details>

<details><summary>D007: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_283399c8b1075acd57cf8872a8cd2f58d0f31588bfe08acda63e3dd084397ba9&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_005&#x27;, 1, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D008: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_34a889821dc06724cfa32c6223be343388d1927a56a60f60b67783130c40bd13&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[&#x27;ir_019&#x27;, 0, 0], &#x27;append&#x27;, &#x27;storage&#x27;, &#x27;status.txt&#x27;]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;,
      &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D009: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_0e4b6ae7e7dbc77b14dbcb9824ec27a3ddb6797f2772edb7b746cf51ec933b97&quot;,
        &quot;path&quot;: [
          &quot;body&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_229ecf9b1be5d6d01b845d620bbfa58ed40c6c250050e8a7ad35af3651bf379e&quot;,
        &quot;path&quot;: [
          &quot;error&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_480afd2db542978c3e68e2d66334c9c896e41164743179224dc2eabc438ee797&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;tool:archive.fetch&quot;,
    &quot;at&quot;: &quot;[&#x27;ir_015&#x27;, 0, 1]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D010: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;storage:status.txt&quot;,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D011: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;,
    &quot;path&quot;: [
      &quot;FAST_KEY&quot;
    ]
  }
}</pre>

</details>

<details><summary>D012: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_8506fe4405e816156ca9a758c93cf271a381e091a43360428b426dec7720adce&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_013&#x27;, 1, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D013: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_8f385af1aea8d4b31ae086e17be72d6763bff848469d23226bf7299399ab729e&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[&#x27;ir_023&#x27;, 0, 0], &#x27;append&#x27;, &#x27;storage&#x27;, &#x27;status.txt&#x27;]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_0771a4eee1aff7b98e695d99229320db7ec7772c7dbc887a4cb4e39e448769d0&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;,
      &quot;data_0771a4eee1aff7b98e695d99229320db7ec7772c7dbc887a4cb4e39e448769d0&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D014: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;,
        &quot;path&quot;: [
          &quot;FAST_KEY&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_950db711eed983e675be53420c63c219681802c8213862d4b621d1213c71e800&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;runtime_context:environment&quot;,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D015: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_a0a78e85803d69c6f4f9f0a5adf2c329feab79987fc4458c9d26a9cfdc6edcdf&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;,
    &quot;path&quot;: [
      &quot;body&quot;
    ]
  }
}</pre>

</details>

<details><summary>D016: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_aa1d5992f26391970bc8025270cfa77b526fcfd7af0f1ee515c67769321d91b8&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[&#x27;ir_025&#x27;, 0, 0], &#x27;append&#x27;, &#x27;storage&#x27;, &#x27;status.txt&#x27;]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_0771a4eee1aff7b98e695d99229320db7ec7772c7dbc887a4cb4e39e448769d0&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;,
      &quot;data_0771a4eee1aff7b98e695d99229320db7ec7772c7dbc887a4cb4e39e448769d0&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D017: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_a0a78e85803d69c6f4f9f0a5adf2c329feab79987fc4458c9d26a9cfdc6edcdf&quot;,
        &quot;path&quot;: [
          &quot;body&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_abeef00b6d0c13e0c76c652e6e6577980f24ec536c420f3441222c086c409be0&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;tool:fast.fetch&quot;,
    &quot;at&quot;: &quot;[&#x27;ir_011&#x27;, 0, 1]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      },
      {
        &quot;data&quot;: &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;,
      &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D018: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_b817d04ba10113cac0612984091788c0635d6eb316d1283252e89a10df8dccb0&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_009&#x27;, 1, 0]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D019: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_010f3f049d453712eca179cc679eee74d8d11a507e318c70b71e57aa9e3f4e9c&quot;,
    &quot;path&quot;: [
      &quot;source_id&quot;
    ]
  }
}</pre>

</details>

<details><summary>D020: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_0f6ef9b6736527aa0c77386993638b5cc20d35f9cacb43acb353d5f262b2233c&quot;,
        &quot;path&quot;: [
          &quot;body&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_ca175754c0b6278ab7864bf2e76c87b9faf628a74492c7ee8bb8f1acd7245dc2&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;tool:fast.fetch&quot;,
    &quot;at&quot;: &quot;[&#x27;ir_007&#x27;, 0, 1]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      },
      {
        &quot;data&quot;: &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_bd4edf268dd24ad15c08c7834a93e9574b8d07464e31d239e65e80c824dadaf0&quot;,
      &quot;data_5a4fc515bcaf3cdfe750b5f871eba0ada15ce4706bbdc84dea67cb4ddeba476d&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>

<details><summary>D021: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_f3904fe7f69f74662ba26214afdc8579d3fe5ff2f53af7a6cc5860746184d24b&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[&#x27;ir_021&#x27;, 0, 0], &#x27;append&#x27;, &#x27;storage&#x27;, &#x27;status.txt&#x27;]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_8506fe4405e816156ca9a758c93cf271a381e091a43360428b426dec7720adce&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_4ba556a9556414c3bf21749208ada88c63a9f303f53b56fd9fe68090df44cb15&quot;,
      &quot;data_8506fe4405e816156ca9a758c93cf271a381e091a43360428b426dec7720adce&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
  }
}</pre>

</details>


<details><summary>Separate audit materials: location evidence and solver statistics</summary>

<pre>{
  &quot;location_evidences&quot;: {
    &quot;__compiled_model_context__&quot;: [
      {
        &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
        &quot;rule_id&quot;: &quot;EM10&quot;
      },
      {
        &quot;reason&quot;: &quot;The program-generated model boundary uses recipient; unmodeled retention stays null and does not assert that the service retains nothing.&quot;,
        &quot;rule_id&quot;: &quot;EM12&quot;
      }
    ],
    &quot;archive_fetch&quot;: [
      {
        &quot;end_line&quot;: 12,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;archive.fetch is the bounded fallback called with source_id only.&quot;,
        &quot;start_line&quot;: 11
      }
    ],
    &quot;environment&quot;: [
      {
        &quot;end_line&quot;: 8,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;FAST_KEY is read from the environment.&quot;,
        &quot;start_line&quot;: 8
      }
    ],
    &quot;fast_fetch&quot;: [
      {
        &quot;end_line&quot;: 10,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;fast.fetch is the preferred credential-gated tool called first and retried once.&quot;,
        &quot;start_line&quot;: 9
      }
    ],
    &quot;status_file&quot;: [
      {
        &quot;end_line&quot;: 16,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The final status is appended to local status.txt on every return path.&quot;,
        &quot;start_line&quot;: 16
      }
    ],
    &quot;user_request&quot;: [
      {
        &quot;end_line&quot;: 8,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;source_id is read from the user&#x27;s request.&quot;,
        &quot;start_line&quot;: 8
      }
    ]
  },
  &quot;stats&quot;: {
    &quot;block_evaluations&quot;: 35,
    &quot;data_count&quot;: 21,
    &quot;description_revision&quot;: 6,
    &quot;record_count&quot;: 26
  }
}</pre>

</details>

<details><summary>Compilation audit: original model processing segments and program-generated location mapping</summary>

<pre>{
  &quot;compilation_map&quot;: {
    &quot;compiled_sha256&quot;: &quot;738c1c8ca183905dbb042b8e3d9bf761aadb340919693dfac60ade191aaddf49&quot;,
    &quot;compiler_version&quot;: &quot;skillflow-processing-compiler-v9&quot;,
    &quot;constraints&quot;: [
      {
        &quot;constraint_id&quot;: &quot;constraint_1b7c5783e6231f705c43&quot;,
        &quot;raw_pointer&quot;: &quot;/realizations/2/constraints/0&quot;,
        &quot;requirement_id&quot;: &quot;R3&quot;
      },
      {
        &quot;constraint_id&quot;: &quot;constraint_66cbca1f9f0a4ce1c16d&quot;,
        &quot;raw_pointer&quot;: &quot;/realizations/3/constraints/0&quot;,
        &quot;requirement_id&quot;: &quot;R4&quot;
      },
      {
        &quot;constraint_id&quot;: &quot;constraint_a8b104b4038cf4cbc6ad&quot;,
        &quot;raw_pointer&quot;: &quot;/realizations/4/constraints/0&quot;,
        &quot;requirement_id&quot;: &quot;R5&quot;
      },
      {
        &quot;constraint_id&quot;: &quot;constraint_9f020b53b4e158b9669f&quot;,
        &quot;raw_pointer&quot;: &quot;/realizations/4/constraints/1&quot;,
        &quot;requirement_id&quot;: &quot;R5&quot;
      },
      {
        &quot;constraint_id&quot;: &quot;constraint_a37723a5cd62afd22ada&quot;,
        &quot;raw_pointer&quot;: &quot;/realizations/5/constraints/0&quot;,
        &quot;requirement_id&quot;: &quot;R6&quot;
      },
      {
        &quot;constraint_id&quot;: &quot;constraint_c513ca74cfaeefaf1cc3&quot;,
        &quot;raw_pointer&quot;: &quot;/realizations/7/constraints/0&quot;,
        &quot;requirement_id&quot;: &quot;R8&quot;
      },
      {
        &quot;constraint_id&quot;: &quot;constraint_2b913793dbcaf7a01836&quot;,
        &quot;raw_pointer&quot;: &quot;/realizations/10/constraints/0&quot;,
        &quot;requirement_id&quot;: &quot;R11&quot;
      },
      {
        &quot;constraint_id&quot;: &quot;constraint_71073f9ea8ec714d0454&quot;,
        &quot;raw_pointer&quot;: &quot;/realizations/10/constraints/1&quot;,
        &quot;requirement_id&quot;: &quot;R11&quot;
      },
      {
        &quot;constraint_id&quot;: &quot;constraint_d815395f81b3dc192bbf&quot;,
        &quot;raw_pointer&quot;: &quot;/realizations/10/constraints/2&quot;,
        &quot;requirement_id&quot;: &quot;R11&quot;
      },
      {
        &quot;constraint_id&quot;: &quot;constraint_b2e1364a394954033e2c&quot;,
        &quot;raw_pointer&quot;: &quot;/realizations/12/constraints/0&quot;,
        &quot;requirement_id&quot;: &quot;R13&quot;
      },
      {
        &quot;constraint_id&quot;: &quot;constraint_77a32f9f420b5b5e458a&quot;,
        &quot;raw_pointer&quot;: &quot;/realizations/13/constraints/0&quot;,
        &quot;requirement_id&quot;: &quot;R14&quot;
      },
      {
        &quot;constraint_id&quot;: &quot;constraint_b0a4ced734ab0cbf2849&quot;,
        &quot;raw_pointer&quot;: &quot;/realizations/14/constraints/0&quot;,
        &quot;requirement_id&quot;: &quot;R15&quot;
      },
      {
        &quot;constraint_id&quot;: &quot;constraint_2fcde5b35cd07b608d0f&quot;,
        &quot;raw_pointer&quot;: &quot;/realizations/15/constraints/0&quot;,
        &quot;requirement_id&quot;: &quot;R16&quot;
      },
      {
        &quot;constraint_id&quot;: &quot;constraint_24d8c02c945f3c0f7990&quot;,
        &quot;raw_pointer&quot;: &quot;/realizations/15/constraints/1&quot;,
        &quot;requirement_id&quot;: &quot;R16&quot;
      },
      {
        &quot;constraint_id&quot;: &quot;constraint_84c8dde9c7076665a166&quot;,
        &quot;raw_pointer&quot;: &quot;/realizations/15/constraints/2&quot;,
        &quot;requirement_id&quot;: &quot;R16&quot;
      },
      {
        &quot;constraint_id&quot;: &quot;constraint_0f1284eaa47a8a793d1e&quot;,
        &quot;raw_pointer&quot;: &quot;/realizations/15/constraints/3&quot;,
        &quot;requirement_id&quot;: &quot;R16&quot;
      }
    ],
    &quot;events&quot;: [
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_001&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_001&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_001&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_001&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_001&quot;,
        &quot;kind&quot;: &quot;observation&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_001&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_001&quot;,
          &quot;events&quot;,
          2
        ],
        &quot;instruction_id&quot;: &quot;ir_001&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_001&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          1
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_003&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_003&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_003&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_003&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_003&quot;,
        &quot;kind&quot;: &quot;observation&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_003&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_003&quot;,
          &quot;events&quot;,
          2
        ],
        &quot;instruction_id&quot;: &quot;ir_003&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_003&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          1
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_005&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_005&quot;,
        &quot;kind&quot;: &quot;observation&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_005&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_005&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_005&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_005&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_007&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_007&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          2
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_007&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_007&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_007&quot;,
        &quot;kind&quot;: &quot;observation&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          1,
          2
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_007&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_009&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_009&quot;,
        &quot;kind&quot;: &quot;observation&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_009&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_009&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_009&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          3
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_009&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_011&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_011&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          2
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_011&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_011&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_011&quot;,
        &quot;kind&quot;: &quot;observation&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          1,
          2
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_011&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_013&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_013&quot;,
        &quot;kind&quot;: &quot;observation&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_013&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_013&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_013&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          2
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_013&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_015&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_015&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          2
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_015&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_015&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_015&quot;,
        &quot;kind&quot;: &quot;observation&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          1,
          2
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_015&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_017&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_017&quot;,
        &quot;kind&quot;: &quot;observation&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_017&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_017&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_017&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          3
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_017&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_019&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_019&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_019&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_021&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_021&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_021&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_023&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_023&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_023&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_025&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_025&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_025&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      }
    ],
    &quot;goals&quot;: [
      {
        &quot;goal_id&quot;: &quot;goal_d93049b68b0aee6a8642&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/0&quot;,
        &quot;requirement_id&quot;: &quot;R10&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 0,
          &quot;instruction_id&quot;: &quot;ir_020&quot;,
          &quot;side&quot;: &quot;input&quot;
        }
      },
      {
        &quot;goal_id&quot;: &quot;goal_9f03413bc5487ca4b779&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/1&quot;,
        &quot;requirement_id&quot;: &quot;R10&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 0,
          &quot;instruction_id&quot;: &quot;ir_022&quot;,
          &quot;side&quot;: &quot;input&quot;
        }
      },
      {
        &quot;goal_id&quot;: &quot;goal_e1d07e741cb504a0ac41&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/2&quot;,
        &quot;requirement_id&quot;: &quot;R10&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 0,
          &quot;instruction_id&quot;: &quot;ir_024&quot;,
          &quot;side&quot;: &quot;input&quot;
        }
      },
      {
        &quot;goal_id&quot;: &quot;goal_6eee0f7a3828e67b679a&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/3&quot;,
        &quot;requirement_id&quot;: &quot;R12&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 0,
          &quot;instruction_id&quot;: &quot;ir_026&quot;,
          &quot;side&quot;: &quot;input&quot;
        }
      },
      {
        &quot;goal_id&quot;: &quot;goal_a261f0fd5f8da40022a7&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_001/events/0/events/1/atomic_ops/0/demands/0&quot;,
        &quot;requirement_id&quot;: &quot;R1&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_001&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            1,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;kind&quot;: &quot;self&quot;
          }
        }
      },
      {
        &quot;goal_id&quot;: &quot;goal_d30d3a4a1e1841d46fe6&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_003/events/0/events/1/atomic_ops/0/demands/0&quot;,
        &quot;requirement_id&quot;: &quot;R2&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_003&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            1,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;kind&quot;: &quot;self&quot;
          }
        }
      },
      {
        &quot;goal_id&quot;: &quot;goal_2a9825475f80aaa968ad&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_005/events/0/events/0/atomic_ops/0/demands/0&quot;,
        &quot;requirement_id&quot;: &quot;R3&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_005&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;kind&quot;: &quot;self&quot;
          }
        }
      },
      {
        &quot;goal_id&quot;: &quot;goal_6e4e685b49d46bb16bf4&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/0&quot;,
        &quot;requirement_id&quot;: &quot;R3&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_007&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;kind&quot;: &quot;self&quot;
          }
        }
      },
      {
        &quot;goal_id&quot;: &quot;goal_a5f6c9837a8185ed2842&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/1&quot;,
        &quot;requirement_id&quot;: &quot;R3&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_007&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;index&quot;: 0,
            &quot;kind&quot;: &quot;input&quot;
          }
        }
      },
      {
        &quot;goal_id&quot;: &quot;goal_2ba7d40cc0fcd7e52de6&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/2&quot;,
        &quot;requirement_id&quot;: &quot;R3&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_007&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;index&quot;: 1,
            &quot;kind&quot;: &quot;input&quot;
          }
        }
      },
      {
        &quot;goal_id&quot;: &quot;goal_6b5988f5263a79d34337&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_009/events/0/events/0/atomic_ops/1/demands/0&quot;,
        &quot;requirement_id&quot;: &quot;R5&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_009&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            1
          ],
          &quot;slot&quot;: {
            &quot;kind&quot;: &quot;self&quot;
          }
        }
      },
      {
        &quot;goal_id&quot;: &quot;goal_a90b9011370a95405c6d&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_011/events/0/events/0/atomic_ops/0/demands/0&quot;,
        &quot;requirement_id&quot;: &quot;R5&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_011&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;kind&quot;: &quot;self&quot;
          }
        }
      },
      {
        &quot;goal_id&quot;: &quot;goal_96270f451e2273da9604&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_011/events/0/events/0/atomic_ops/0/demands/1&quot;,
        &quot;requirement_id&quot;: &quot;R5&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_011&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;index&quot;: 0,
            &quot;kind&quot;: &quot;input&quot;
          }
        }
      },
      {
        &quot;goal_id&quot;: &quot;goal_a852d40a2988d53d8768&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_011/events/0/events/0/atomic_ops/0/demands/2&quot;,
        &quot;requirement_id&quot;: &quot;R5&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_011&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;index&quot;: 1,
            &quot;kind&quot;: &quot;input&quot;
          }
        }
      },
      {
        &quot;goal_id&quot;: &quot;goal_d787e8db6e7691331844&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_015/events/0/events/0/atomic_ops/0/demands/0&quot;,
        &quot;requirement_id&quot;: &quot;R7&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_015&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;kind&quot;: &quot;self&quot;
          }
        }
      },
      {
        &quot;goal_id&quot;: &quot;goal_675ec0f7a54d9d424017&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_015/events/0/events/0/atomic_ops/0/demands/1&quot;,
        &quot;requirement_id&quot;: &quot;R9&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_015&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;index&quot;: 0,
            &quot;kind&quot;: &quot;input&quot;
          }
        }
      },
      {
        &quot;goal_id&quot;: &quot;goal_c47884c5742ed8ccf272&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_019/events/0/events/0/atomic_ops/0/demands/0&quot;,
        &quot;requirement_id&quot;: &quot;R16&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_019&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;kind&quot;: &quot;self&quot;
          }
        }
      },
      {
        &quot;goal_id&quot;: &quot;goal_ab5998e1d2c9fb6bfc3b&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_019/events/0/events/0/atomic_ops/0/demands/1&quot;,
        &quot;requirement_id&quot;: &quot;R16&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_019&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;index&quot;: 0,
            &quot;kind&quot;: &quot;input&quot;
          }
        }
      },
      {
        &quot;goal_id&quot;: &quot;goal_22399659989102b4bccd&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_021/events/0/events/0/atomic_ops/0/demands/0&quot;,
        &quot;requirement_id&quot;: &quot;R16&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_021&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;kind&quot;: &quot;self&quot;
          }
        }
      },
      {
        &quot;goal_id&quot;: &quot;goal_96dc9eea7ab05d4949bd&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_021/events/0/events/0/atomic_ops/0/demands/1&quot;,
        &quot;requirement_id&quot;: &quot;R16&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_021&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;index&quot;: 0,
            &quot;kind&quot;: &quot;input&quot;
          }
        }
      },
      {
        &quot;goal_id&quot;: &quot;goal_439b9439a0e53de21020&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_023/events/0/events/0/atomic_ops/0/demands/0&quot;,
        &quot;requirement_id&quot;: &quot;R16&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_023&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;kind&quot;: &quot;self&quot;
          }
        }
      },
      {
        &quot;goal_id&quot;: &quot;goal_09766dec5e6c505297e2&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_023/events/0/events/0/atomic_ops/0/demands/1&quot;,
        &quot;requirement_id&quot;: &quot;R16&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_023&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;index&quot;: 0,
            &quot;kind&quot;: &quot;input&quot;
          }
        }
      },
      {
        &quot;goal_id&quot;: &quot;goal_4881a7316e21c9fe13ac&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_025/events/0/events/0/atomic_ops/0/demands/0&quot;,
        &quot;requirement_id&quot;: &quot;R16&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_025&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;kind&quot;: &quot;self&quot;
          }
        }
      },
      {
        &quot;goal_id&quot;: &quot;goal_204d92e17659496cbcd3&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_025/events/0/events/0/atomic_ops/0/demands/1&quot;,
        &quot;requirement_id&quot;: &quot;R16&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_025&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            0,
            &quot;atomic_ops&quot;,
            0
          ],
          &quot;slot&quot;: {
            &quot;index&quot;: 0,
            &quot;kind&quot;: &quot;input&quot;
          }
        }
      }
    ],
    &quot;raw_sha256&quot;: &quot;290d7e850b287cab92f7a9c66f276edb3bfbf50424b5815a2dca292bfa48aa3d&quot;,
    &quot;runtime_contract&quot;: {
      &quot;sha256&quot;: &quot;32abb3320d5d1b1e9c18c37622c0d523317faaa0f69027de15b7ce76c61b3eda&quot;,
      &quot;version&quot;: &quot;skillflow-abstract-runtime-v7&quot;
    },
    &quot;schema_version&quot;: &quot;skillflow-processing-compilation-v9&quot;
  },
  &quot;raw_annotation&quot;: {
    &quot;demands&quot;: [
      {
        &quot;expected&quot;: null,
        &quot;expected_path&quot;: [],
        &quot;path&quot;: [],
        &quot;preserve&quot;: &quot;value&quot;,
        &quot;reason&quot;: &quot;Return the first fast.fetch response body unchanged.&quot;,
        &quot;requirement_id&quot;: &quot;R10&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 0,
          &quot;instruction_id&quot;: &quot;ir_020&quot;,
          &quot;side&quot;: &quot;input&quot;
        }
      },
      {
        &quot;expected&quot;: null,
        &quot;expected_path&quot;: [],
        &quot;path&quot;: [],
        &quot;preserve&quot;: &quot;value&quot;,
        &quot;reason&quot;: &quot;Return the fast.fetch retry response body unchanged.&quot;,
        &quot;requirement_id&quot;: &quot;R10&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 0,
          &quot;instruction_id&quot;: &quot;ir_022&quot;,
          &quot;side&quot;: &quot;input&quot;
        }
      },
      {
        &quot;expected&quot;: null,
        &quot;expected_path&quot;: [],
        &quot;path&quot;: [],
        &quot;preserve&quot;: &quot;value&quot;,
        &quot;reason&quot;: &quot;Return the archive.fetch response body unchanged.&quot;,
        &quot;requirement_id&quot;: &quot;R10&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 0,
          &quot;instruction_id&quot;: &quot;ir_024&quot;,
          &quot;side&quot;: &quot;input&quot;
        }
      },
      {
        &quot;expected&quot;: null,
        &quot;expected_path&quot;: [],
        &quot;path&quot;: [],
        &quot;preserve&quot;: &quot;value&quot;,
        &quot;reason&quot;: &quot;Return the archive.fetch error unchanged when archive.fetch fails.&quot;,
        &quot;requirement_id&quot;: &quot;R12&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 0,
          &quot;instruction_id&quot;: &quot;ir_026&quot;,
          &quot;side&quot;: &quot;input&quot;
        }
      }
    ],
    &quot;expressions&quot;: [],
    &quot;ir_semantics&quot;: {
      &quot;ir_001&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 8,
                        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                        &quot;reason&quot;: &quot;Read the user request context.&quot;,
                        &quot;start_line&quot;: 8
                      }
                    ],
                    &quot;location&quot;: &quot;user_request&quot;,
                    &quot;op&quot;: &quot;read&quot;,
                    &quot;output&quot;: &quot;user_request_snapshot&quot;
                  }
                ],
                &quot;effect&quot;: &quot;context_read&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 8,
                    &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                    &quot;reason&quot;: &quot;The user_request context is read.&quot;,
                    &quot;start_line&quot;: 8
                  }
                ]
              },
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;demands&quot;: [
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [],
                        &quot;preserve&quot;: &quot;value&quot;,
                        &quot;reason&quot;: &quot;Preserve the source_id selected from the user request.&quot;,
                        &quot;requirement_id&quot;: &quot;R1&quot;,
                        &quot;target&quot;: {
                          &quot;kind&quot;: &quot;self&quot;
                        }
                      }
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 8,
                        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                        &quot;reason&quot;: &quot;The step requires reading source_id from the user request.&quot;,
                        &quot;start_line&quot;: 8
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;kind&quot;: &quot;local&quot;,
                      &quot;name&quot;: &quot;user_request_snapshot&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;source_id&quot;,
                    &quot;path&quot;: [
                      &quot;source_id&quot;
                    ]
                  }
                ],
                &quot;effect&quot;: &quot;transform&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 8,
                    &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                    &quot;reason&quot;: &quot;Select source_id from the read user request.&quot;,
                    &quot;start_line&quot;: 8
                  }
                ]
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 8,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The first workflow step reads source_id from the user request.&quot;,
                &quot;start_line&quot;: 8
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;default&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;end_line&quot;: 8,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The agent runtime reads source_id from the user request.&quot;,
            &quot;start_line&quot;: 8,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 8,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The instruction output is source_id.&quot;,
                &quot;start_line&quot;: 8
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;source_id&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_002&quot;: {
        &quot;empty_effect_evidences&quot;: [
          {
            &quot;end_line&quot;: 8,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;This dispatch controls the next step without content processing.&quot;,
            &quot;start_line&quot;: 8
          }
        ],
        &quot;events&quot;: [],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;end_line&quot;: 8,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The workflow dispatches to reading FAST_KEY after source_id.&quot;,
            &quot;start_line&quot;: 8,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_003&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 8,
                        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                        &quot;reason&quot;: &quot;Read the environment context.&quot;,
                        &quot;start_line&quot;: 8
                      }
                    ],
                    &quot;location&quot;: &quot;environment&quot;,
                    &quot;op&quot;: &quot;read&quot;,
                    &quot;output&quot;: &quot;environment_snapshot&quot;
                  }
                ],
                &quot;effect&quot;: &quot;context_read&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 8,
                    &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                    &quot;reason&quot;: &quot;The environment context is read.&quot;,
                    &quot;start_line&quot;: 8
                  }
                ]
              },
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;demands&quot;: [
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [],
                        &quot;preserve&quot;: &quot;value&quot;,
                        &quot;reason&quot;: &quot;Preserve the FAST_KEY selected from the environment.&quot;,
                        &quot;requirement_id&quot;: &quot;R2&quot;,
                        &quot;target&quot;: {
                          &quot;kind&quot;: &quot;self&quot;
                        }
                      }
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 8,
                        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                        &quot;reason&quot;: &quot;The step requires reading FAST_KEY from the environment.&quot;,
                        &quot;start_line&quot;: 8
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;kind&quot;: &quot;local&quot;,
                      &quot;name&quot;: &quot;environment_snapshot&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;fast_key&quot;,
                    &quot;path&quot;: [
                      &quot;FAST_KEY&quot;
                    ]
                  }
                ],
                &quot;effect&quot;: &quot;transform&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 8,
                    &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                    &quot;reason&quot;: &quot;Select FAST_KEY from the read environment.&quot;,
                    &quot;start_line&quot;: 8
                  }
                ]
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 8,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The first workflow step reads FAST_KEY from the environment.&quot;,
                &quot;start_line&quot;: 8
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;default&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;end_line&quot;: 8,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The agent runtime reads FAST_KEY from the environment.&quot;,
            &quot;start_line&quot;: 8,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 8,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The instruction output is FAST_KEY.&quot;,
                &quot;start_line&quot;: 8
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;fast_key&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 3,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The skill description describes the preferred tool as credential-gated.&quot;,
                &quot;start_line&quot;: 3
              },
              {
                &quot;end_line&quot;: 8,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;FAST_KEY is read from the environment.&quot;,
                &quot;start_line&quot;: 8
              },
              {
                &quot;end_line&quot;: 15,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;FAST_KEY is prohibited from archive.fetch and diagnostic output, indicating that this environment member is credential information.&quot;,
                &quot;start_line&quot;: 15
              }
            ],
            &quot;label&quot;: &quot;credential&quot;,
            &quot;path&quot;: [
              &quot;FAST_KEY&quot;
            ],
            &quot;property&quot;: &quot;value&quot;,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;environment_snapshot&quot;
            }
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 3,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The skill description describes the preferred tool as credential-gated.&quot;,
                &quot;start_line&quot;: 3
              },
              {
                &quot;end_line&quot;: 15,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;FAST_KEY is prohibited from archive.fetch and diagnostic output, indicating it is a credential.&quot;,
                &quot;start_line&quot;: 15
              }
            ],
            &quot;label&quot;: &quot;credential&quot;,
            &quot;path&quot;: [],
            &quot;property&quot;: &quot;value&quot;,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;fast_key&quot;
            }
          }
        ]
      },
      &quot;ir_004&quot;: {
        &quot;empty_effect_evidences&quot;: [
          {
            &quot;end_line&quot;: 9,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;This dispatch controls the next step without content processing.&quot;,
            &quot;start_line&quot;: 8
          }
        ],
        &quot;events&quot;: [],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;end_line&quot;: 9,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The workflow dispatches to the FAST_KEY presence check.&quot;,
            &quot;start_line&quot;: 8,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_005&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;demands&quot;: [
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [],
                        &quot;preserve&quot;: &quot;truth&quot;,
                        &quot;reason&quot;: &quot;Preserve whether FAST_KEY is present to choose the fast.fetch path.&quot;,
                        &quot;requirement_id&quot;: &quot;R3&quot;,
                        &quot;target&quot;: {
                          &quot;kind&quot;: &quot;self&quot;
                        }
                      }
                    ],
                    &quot;dependencies&quot;: [
                      &quot;derived&quot;
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 9,
                        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                        &quot;reason&quot;: &quot;Check FAST_KEY presence.&quot;,
                        &quot;start_line&quot;: 9
                      }
                    ],
                    &quot;expression&quot;: {
                      &quot;evidences&quot;: [
                        {
                          &quot;end_line&quot;: 9,
                          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                          &quot;reason&quot;: &quot;The condition is whether FAST_KEY is present.&quot;,
                          &quot;start_line&quot;: 9
                        }
                      ],
                      &quot;expression&quot;: {
                        &quot;arg&quot;: {
                          &quot;op&quot;: &quot;ref&quot;,
                          &quot;value&quot;: {
                            &quot;index&quot;: 0,
                            &quot;kind&quot;: &quot;input&quot;
                          }
                        },
                        &quot;op&quot;: &quot;present&quot;
                      }
                    },
                    &quot;inputs&quot;: [
                      {
                        &quot;index&quot;: 0,
                        &quot;kind&quot;: &quot;input&quot;
                      }
                    ],
                    &quot;op&quot;: &quot;compute&quot;,
                    &quot;output&quot;: &quot;fast_key_present&quot;
                  }
                ],
                &quot;effect&quot;: &quot;transform&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 9,
                    &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                    &quot;reason&quot;: &quot;Compute the presence condition for FAST_KEY.&quot;,
                    &quot;start_line&quot;: 9
                  }
                ]
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 9,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The workflow checks FAST_KEY presence.&quot;,
                &quot;start_line&quot;: 9
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;default&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;end_line&quot;: 9,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The agent runtime checks whether FAST_KEY is present.&quot;,
            &quot;start_line&quot;: 9,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 9,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The instruction output is the FAST_KEY presence result.&quot;,
                &quot;start_line&quot;: 9
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;fast_key_present&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_006&quot;: {
        &quot;empty_effect_evidences&quot;: [
          {
            &quot;end_line&quot;: 9,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;This dispatch controls the fetch path without content processing.&quot;,
            &quot;start_line&quot;: 9
          }
        ],
        &quot;events&quot;: [],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;end_line&quot;: 9,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The workflow dispatches according to FAST_KEY presence.&quot;,
            &quot;start_line&quot;: 9,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_007&quot;: {
        &quot;empty_effect_evidences&quot;: [
          {
            &quot;end_line&quot;: 9,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The tool request and response are modeled with null effects because no network or filesystem mechanism is established.&quot;,
            &quot;start_line&quot;: 9
          }
        ],
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;demands&quot;: [
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [],
                        &quot;preserve&quot;: &quot;action&quot;,
                        &quot;reason&quot;: &quot;Try fast.fetch first on the FAST_KEY present path.&quot;,
                        &quot;requirement_id&quot;: &quot;R3&quot;,
                        &quot;target&quot;: {
                          &quot;kind&quot;: &quot;self&quot;
                        }
                      },
                      {
                        &quot;expected&quot;: {
                          &quot;index&quot;: 1,
                          &quot;kind&quot;: &quot;input&quot;
                        },
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [],
                        &quot;preserve&quot;: &quot;value&quot;,
                        &quot;reason&quot;: &quot;Pass the original source_id to fast.fetch.&quot;,
                        &quot;requirement_id&quot;: &quot;R3&quot;,
                        &quot;target&quot;: {
                          &quot;index&quot;: 0,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      },
                      {
                        &quot;expected&quot;: {
                          &quot;index&quot;: 2,
                          &quot;kind&quot;: &quot;input&quot;
                        },
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [],
                        &quot;preserve&quot;: &quot;value&quot;,
                        &quot;reason&quot;: &quot;Pass the original FAST_KEY to fast.fetch.&quot;,
                        &quot;requirement_id&quot;: &quot;R3&quot;,
                        &quot;target&quot;: {
                          &quot;index&quot;: 1,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      }
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 9,
                        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                        &quot;reason&quot;: &quot;fast.fetch is called with source_id and FAST_KEY.&quot;,
                        &quot;start_line&quot;: 9
                      }
                    ],
                    &quot;inputs&quot;: [
                      {
                        &quot;index&quot;: 1,
                        &quot;kind&quot;: &quot;input&quot;
                      },
                      {
                        &quot;index&quot;: 2,
                        &quot;kind&quot;: &quot;input&quot;
                      }
                    ],
                    &quot;op&quot;: &quot;deliver&quot;,
                    &quot;target&quot;: &quot;fast_fetch&quot;
                  },
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 9,
                        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                        &quot;reason&quot;: &quot;Acquire the first fast.fetch response.&quot;,
                        &quot;start_line&quot;: 9
                      }
                    ],
                    &quot;inputs&quot;: [
                      {
                        &quot;index&quot;: 1,
                        &quot;kind&quot;: &quot;input&quot;
                      },
                      {
                        &quot;index&quot;: 2,
                        &quot;kind&quot;: &quot;input&quot;
                      }
                    ],
                    &quot;location&quot;: &quot;fast_fetch&quot;,
                    &quot;op&quot;: &quot;receive&quot;,
                    &quot;output&quot;: &quot;fast_fetch_first_response&quot;
                  }
                ],
                &quot;effect&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 9,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The first fast.fetch attempt is made only when FAST_KEY is present.&quot;,
                &quot;start_line&quot;: 9
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;default&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;end_line&quot;: 9,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The agent runtime tries fast.fetch first with source_id and FAST_KEY.&quot;,
            &quot;start_line&quot;: 9,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 9,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The instruction output is the first fast.fetch response.&quot;,
                &quot;start_line&quot;: 9
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;fast_fetch_first_response&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_008&quot;: {
        &quot;empty_effect_evidences&quot;: [
          {
            &quot;end_line&quot;: 10,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;This dispatch controls the next step without content processing.&quot;,
            &quot;start_line&quot;: 9
          }
        ],
        &quot;events&quot;: [],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;end_line&quot;: 10,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The workflow dispatches to inspect the first fast.fetch result.&quot;,
            &quot;start_line&quot;: 9,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_009&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;dependencies&quot;: [
                      &quot;possible&quot;
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 10,
                        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                        &quot;reason&quot;: &quot;Classify the first fast.fetch outcome.&quot;,
                        &quot;start_line&quot;: 10
                      }
                    ],
                    &quot;inputs&quot;: [
                      {
                        &quot;index&quot;: 0,
                        &quot;kind&quot;: &quot;input&quot;
                      }
                    ],
                    &quot;op&quot;: &quot;compute&quot;,
                    &quot;output&quot;: &quot;fast_fetch_first_outcome&quot;
                  },
                  {
                    &quot;demands&quot;: [
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [],
                        &quot;preserve&quot;: &quot;truth&quot;,
                        &quot;reason&quot;: &quot;Preserve whether the first fast.fetch attempt failed with a transient error to gate the retry.&quot;,
                        &quot;requirement_id&quot;: &quot;R5&quot;,
                        &quot;target&quot;: {
                          &quot;kind&quot;: &quot;self&quot;
                        }
                      }
                    ],
                    &quot;dependencies&quot;: [
                      &quot;derived&quot;
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 10,
                        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                        &quot;reason&quot;: &quot;The retry condition is a transient first failure.&quot;,
                        &quot;start_line&quot;: 10
                      }
                    ],
                    &quot;expression&quot;: {
                      &quot;evidences&quot;: [
                        {
                          &quot;end_line&quot;: 10,
                          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                          &quot;reason&quot;: &quot;The retry condition is whether the first fast.fetch outcome classification marks the failure as transient.&quot;,
                          &quot;start_line&quot;: 10
                        }
                      ],
                      &quot;expression&quot;: {
                        &quot;left&quot;: {
                          &quot;arg&quot;: {
                            &quot;op&quot;: &quot;ref&quot;,
                            &quot;value&quot;: {
                              &quot;kind&quot;: &quot;local&quot;,
                              &quot;name&quot;: &quot;fast_fetch_first_outcome&quot;
                            }
                          },
                          &quot;op&quot;: &quot;field&quot;,
                          &quot;path&quot;: [
                            &quot;transient&quot;
                          ]
                        },
                        &quot;op&quot;: &quot;eq&quot;,
                        &quot;right&quot;: {
                          &quot;op&quot;: &quot;literal&quot;,
                          &quot;value&quot;: true
                        }
                      }
                    },
                    &quot;inputs&quot;: [
                      {
                        &quot;kind&quot;: &quot;local&quot;,
                        &quot;name&quot;: &quot;fast_fetch_first_outcome&quot;
                      }
                    ],
                    &quot;op&quot;: &quot;compute&quot;,
                    &quot;output&quot;: &quot;fast_fetch_first_transient&quot;
                  },
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 13,
                        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                        &quot;reason&quot;: &quot;The successful response has a body value to return unchanged.&quot;,
                        &quot;start_line&quot;: 13
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;fast_fetch_first_body&quot;,
                    &quot;path&quot;: [
                      &quot;body&quot;
                    ]
                  }
                ],
                &quot;effect&quot;: &quot;transform&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 10,
                    &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                    &quot;reason&quot;: &quot;Classify the first fast.fetch response and extract its body.&quot;,
                    &quot;start_line&quot;: 10
                  }
                ]
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 10,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The first fast.fetch attempt is classified as success, transient failure, or non-transient failure.&quot;,
                &quot;start_line&quot;: 10
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;default&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;end_line&quot;: 10,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The agent runtime classifies the first fast.fetch attempt outcome.&quot;,
            &quot;start_line&quot;: 10,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 10,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The instruction classifies the first fast.fetch outcome.&quot;,
                &quot;start_line&quot;: 10
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;fast_fetch_first_outcome&quot;
            }
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 13,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The instruction extracts the response body.&quot;,
                &quot;start_line&quot;: 13
              }
            ],
            &quot;output_index&quot;: 1,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;fast_fetch_first_body&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_010&quot;: {
        &quot;empty_effect_evidences&quot;: [
          {
            &quot;end_line&quot;: 10,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;This dispatch controls the next step without content processing.&quot;,
            &quot;start_line&quot;: 10
          }
        ],
        &quot;events&quot;: [],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;end_line&quot;: 10,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The workflow dispatches according to the first fast.fetch outcome.&quot;,
            &quot;start_line&quot;: 10,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_011&quot;: {
        &quot;empty_effect_evidences&quot;: [
          {
            &quot;end_line&quot;: 10,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The tool request and response are modeled with null effects because no network or filesystem mechanism is established.&quot;,
            &quot;start_line&quot;: 10
          }
        ],
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;demands&quot;: [
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [],
                        &quot;preserve&quot;: &quot;action&quot;,
                        &quot;reason&quot;: &quot;Retry fast.fetch exactly once on a transient first failure.&quot;,
                        &quot;requirement_id&quot;: &quot;R5&quot;,
                        &quot;target&quot;: {
                          &quot;kind&quot;: &quot;self&quot;
                        }
                      },
                      {
                        &quot;expected&quot;: {
                          &quot;index&quot;: 1,
                          &quot;kind&quot;: &quot;input&quot;
                        },
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [],
                        &quot;preserve&quot;: &quot;value&quot;,
                        &quot;reason&quot;: &quot;Pass the original source_id on retry.&quot;,
                        &quot;requirement_id&quot;: &quot;R5&quot;,
                        &quot;target&quot;: {
                          &quot;index&quot;: 0,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      },
                      {
                        &quot;expected&quot;: {
                          &quot;index&quot;: 2,
                          &quot;kind&quot;: &quot;input&quot;
                        },
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [],
                        &quot;preserve&quot;: &quot;value&quot;,
                        &quot;reason&quot;: &quot;Pass the original FAST_KEY on retry.&quot;,
                        &quot;requirement_id&quot;: &quot;R5&quot;,
                        &quot;target&quot;: {
                          &quot;index&quot;: 1,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      }
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 10,
                        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                        &quot;reason&quot;: &quot;fast.fetch is retried with source_id and FAST_KEY.&quot;,
                        &quot;start_line&quot;: 10
                      }
                    ],
                    &quot;inputs&quot;: [
                      {
                        &quot;index&quot;: 1,
                        &quot;kind&quot;: &quot;input&quot;
                      },
                      {
                        &quot;index&quot;: 2,
                        &quot;kind&quot;: &quot;input&quot;
                      }
                    ],
                    &quot;op&quot;: &quot;deliver&quot;,
                    &quot;target&quot;: &quot;fast_fetch&quot;
                  },
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 10,
                        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                        &quot;reason&quot;: &quot;Acquire the fast.fetch retry response.&quot;,
                        &quot;start_line&quot;: 10
                      }
                    ],
                    &quot;inputs&quot;: [
                      {
                        &quot;index&quot;: 1,
                        &quot;kind&quot;: &quot;input&quot;
                      },
                      {
                        &quot;index&quot;: 2,
                        &quot;kind&quot;: &quot;input&quot;
                      }
                    ],
                    &quot;location&quot;: &quot;fast_fetch&quot;,
                    &quot;op&quot;: &quot;receive&quot;,
                    &quot;output&quot;: &quot;fast_fetch_retry_response&quot;
                  }
                ],
                &quot;effect&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 10,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The single retry of fast.fetch occurs only on a transient first failure.&quot;,
                &quot;start_line&quot;: 10
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;default&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;end_line&quot;: 10,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The agent runtime retries fast.fetch once on a transient first failure.&quot;,
            &quot;start_line&quot;: 10,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 10,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The instruction output is the fast.fetch retry response.&quot;,
                &quot;start_line&quot;: 10
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;fast_fetch_retry_response&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_012&quot;: {
        &quot;empty_effect_evidences&quot;: [
          {
            &quot;end_line&quot;: 10,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;This dispatch controls the next step without content processing.&quot;,
            &quot;start_line&quot;: 10
          }
        ],
        &quot;events&quot;: [],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;end_line&quot;: 10,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The workflow dispatches to inspect the fast.fetch retry result.&quot;,
            &quot;start_line&quot;: 10,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_013&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;dependencies&quot;: [
                      &quot;possible&quot;
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 11,
                        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                        &quot;reason&quot;: &quot;Classify the fast.fetch retry outcome.&quot;,
                        &quot;start_line&quot;: 10
                      }
                    ],
                    &quot;inputs&quot;: [
                      {
                        &quot;index&quot;: 0,
                        &quot;kind&quot;: &quot;input&quot;
                      }
                    ],
                    &quot;op&quot;: &quot;compute&quot;,
                    &quot;output&quot;: &quot;fast_fetch_retry_outcome&quot;
                  },
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 13,
                        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                        &quot;reason&quot;: &quot;The successful retry response has a body value to return unchanged.&quot;,
                        &quot;start_line&quot;: 13
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;fast_fetch_retry_body&quot;,
                    &quot;path&quot;: [
                      &quot;body&quot;
                    ]
                  }
                ],
                &quot;effect&quot;: &quot;transform&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 11,
                    &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                    &quot;reason&quot;: &quot;Classify the fast.fetch retry response and extract its body.&quot;,
                    &quot;start_line&quot;: 10
                  }
                ]
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 11,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The retry response is classified and its body is extracted.&quot;,
                &quot;start_line&quot;: 10
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;default&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;end_line&quot;: 11,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The agent runtime classifies the fast.fetch retry outcome.&quot;,
            &quot;start_line&quot;: 10,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 11,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The instruction classifies the fast.fetch retry outcome.&quot;,
                &quot;start_line&quot;: 10
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;fast_fetch_retry_outcome&quot;
            }
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 13,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The instruction extracts the retry response body.&quot;,
                &quot;start_line&quot;: 13
              }
            ],
            &quot;output_index&quot;: 1,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;fast_fetch_retry_body&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_014&quot;: {
        &quot;empty_effect_evidences&quot;: [
          {
            &quot;end_line&quot;: 11,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;This dispatch controls the next step without content processing.&quot;,
            &quot;start_line&quot;: 11
          }
        ],
        &quot;events&quot;: [],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;end_line&quot;: 11,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The workflow dispatches to archive.fetch after fast.fetch failures.&quot;,
            &quot;start_line&quot;: 11,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_015&quot;: {
        &quot;empty_effect_evidences&quot;: [
          {
            &quot;end_line&quot;: 12,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The tool request and response are modeled with null effects because no network or filesystem mechanism is established.&quot;,
            &quot;start_line&quot;: 11
          }
        ],
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;demands&quot;: [
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [],
                        &quot;preserve&quot;: &quot;action&quot;,
                        &quot;reason&quot;: &quot;Call archive.fetch after a non-transient first failure or a failed retry.&quot;,
                        &quot;requirement_id&quot;: &quot;R7&quot;,
                        &quot;target&quot;: {
                          &quot;kind&quot;: &quot;self&quot;
                        }
                      },
                      {
                        &quot;expected&quot;: {
                          &quot;index&quot;: 1,
                          &quot;kind&quot;: &quot;input&quot;
                        },
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [],
                        &quot;preserve&quot;: &quot;value&quot;,
                        &quot;reason&quot;: &quot;Pass source_id as archive.fetch&#x27;s only argument.&quot;,
                        &quot;requirement_id&quot;: &quot;R9&quot;,
                        &quot;target&quot;: {
                          &quot;index&quot;: 0,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      }
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 12,
                        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                        &quot;reason&quot;: &quot;archive.fetch is called with source_id only.&quot;,
                        &quot;start_line&quot;: 11
                      }
                    ],
                    &quot;inputs&quot;: [
                      {
                        &quot;index&quot;: 1,
                        &quot;kind&quot;: &quot;input&quot;
                      }
                    ],
                    &quot;op&quot;: &quot;deliver&quot;,
                    &quot;target&quot;: &quot;archive_fetch&quot;
                  },
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 12,
                        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                        &quot;reason&quot;: &quot;Acquire the archive.fetch response.&quot;,
                        &quot;start_line&quot;: 11
                      }
                    ],
                    &quot;inputs&quot;: [
                      {
                        &quot;index&quot;: 1,
                        &quot;kind&quot;: &quot;input&quot;
                      }
                    ],
                    &quot;location&quot;: &quot;archive_fetch&quot;,
                    &quot;op&quot;: &quot;receive&quot;,
                    &quot;output&quot;: &quot;archive_fetch_response&quot;
                  }
                ],
                &quot;effect&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 12,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;archive.fetch is called at most once with source_id as its only argument.&quot;,
                &quot;start_line&quot;: 11
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;default&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;end_line&quot;: 12,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The agent runtime calls archive.fetch with source_id only.&quot;,
            &quot;start_line&quot;: 11,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 12,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The instruction output is the archive.fetch response.&quot;,
                &quot;start_line&quot;: 11
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;archive_fetch_response&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_016&quot;: {
        &quot;empty_effect_evidences&quot;: [
          {
            &quot;end_line&quot;: 12,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;This dispatch controls the next step without content processing.&quot;,
            &quot;start_line&quot;: 11
          }
        ],
        &quot;events&quot;: [],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;end_line&quot;: 12,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The workflow dispatches to inspect the archive.fetch result.&quot;,
            &quot;start_line&quot;: 11,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_017&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;dependencies&quot;: [
                      &quot;possible&quot;
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 14,
                        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                        &quot;reason&quot;: &quot;Classify the archive.fetch outcome.&quot;,
                        &quot;start_line&quot;: 13
                      }
                    ],
                    &quot;inputs&quot;: [
                      {
                        &quot;index&quot;: 0,
                        &quot;kind&quot;: &quot;input&quot;
                      }
                    ],
                    &quot;op&quot;: &quot;compute&quot;,
                    &quot;output&quot;: &quot;archive_fetch_outcome&quot;
                  },
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 13,
                        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                        &quot;reason&quot;: &quot;The successful archive.fetch response has a body value to return unchanged.&quot;,
                        &quot;start_line&quot;: 13
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;archive_fetch_body&quot;,
                    &quot;path&quot;: [
                      &quot;body&quot;
                    ]
                  },
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 14,
                        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                        &quot;reason&quot;: &quot;A failed archive.fetch response has an error value to return.&quot;,
                        &quot;start_line&quot;: 14
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;archive_fetch_error&quot;,
                    &quot;path&quot;: [
                      &quot;error&quot;
                    ]
                  }
                ],
                &quot;effect&quot;: &quot;transform&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 14,
                    &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                    &quot;reason&quot;: &quot;Classify the archive.fetch result and extract body or error.&quot;,
                    &quot;start_line&quot;: 13
                  }
                ]
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 14,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The archive.fetch response is classified and its body or error is extracted.&quot;,
                &quot;start_line&quot;: 13
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;default&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;end_line&quot;: 13,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The agent runtime classifies the archive.fetch result.&quot;,
            &quot;start_line&quot;: 13,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 14,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The instruction classifies the archive.fetch outcome.&quot;,
                &quot;start_line&quot;: 13
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;archive_fetch_outcome&quot;
            }
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 13,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The instruction extracts the archive.fetch body.&quot;,
                &quot;start_line&quot;: 13
              }
            ],
            &quot;output_index&quot;: 1,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;archive_fetch_body&quot;
            }
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 14,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The instruction extracts the archive.fetch error.&quot;,
                &quot;start_line&quot;: 14
              }
            ],
            &quot;output_index&quot;: 2,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;archive_fetch_error&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_018&quot;: {
        &quot;empty_effect_evidences&quot;: [
          {
            &quot;end_line&quot;: 14,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;This dispatch controls the next step without content processing.&quot;,
            &quot;start_line&quot;: 13
          }
        ],
        &quot;events&quot;: [],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;end_line&quot;: 14,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The workflow dispatches according to the archive.fetch outcome.&quot;,
            &quot;start_line&quot;: 13,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_019&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;demands&quot;: [
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [],
                        &quot;preserve&quot;: &quot;action&quot;,
                        &quot;reason&quot;: &quot;Append the final status before returning.&quot;,
                        &quot;requirement_id&quot;: &quot;R16&quot;,
                        &quot;target&quot;: {
                          &quot;kind&quot;: &quot;self&quot;
                        }
                      },
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [],
                        &quot;preserve&quot;: &quot;value&quot;,
                        &quot;reason&quot;: &quot;Append this path&#x27;s final outcome status.&quot;,
                        &quot;requirement_id&quot;: &quot;R16&quot;,
                        &quot;target&quot;: {
                          &quot;index&quot;: 0,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      }
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 16,
                        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                        &quot;reason&quot;: &quot;Append the final status to local status.txt on this return path.&quot;,
                        &quot;start_line&quot;: 16
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 1,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;mode&quot;: &quot;append&quot;,
                    &quot;op&quot;: &quot;write&quot;,
                    &quot;target&quot;: &quot;status_file&quot;
                  }
                ],
                &quot;effect&quot;: &quot;fs_write&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 16,
                    &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                    &quot;reason&quot;: &quot;Append the final status to local status.txt.&quot;,
                    &quot;start_line&quot;: 16
                  }
                ]
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 16,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The final status is appended before returning the first fast.fetch body.&quot;,
                &quot;start_line&quot;: 16
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;default&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;end_line&quot;: 16,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The agent runtime appends the first fast.fetch outcome to status.txt.&quot;,
            &quot;start_line&quot;: 16,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_020&quot;: {
        &quot;empty_effect_evidences&quot;: [
          {
            &quot;end_line&quot;: 13,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The return itself has no content effect; it returns the existing body value.&quot;,
            &quot;start_line&quot;: 13
          }
        ],
        &quot;events&quot;: [],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;end_line&quot;: 13,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The workflow returns the first fast.fetch body.&quot;,
            &quot;start_line&quot;: 13,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_021&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;demands&quot;: [
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [],
                        &quot;preserve&quot;: &quot;action&quot;,
                        &quot;reason&quot;: &quot;Append the final status before returning.&quot;,
                        &quot;requirement_id&quot;: &quot;R16&quot;,
                        &quot;target&quot;: {
                          &quot;kind&quot;: &quot;self&quot;
                        }
                      },
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [],
                        &quot;preserve&quot;: &quot;value&quot;,
                        &quot;reason&quot;: &quot;Append this path&#x27;s final outcome status.&quot;,
                        &quot;requirement_id&quot;: &quot;R16&quot;,
                        &quot;target&quot;: {
                          &quot;index&quot;: 0,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      }
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 16,
                        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                        &quot;reason&quot;: &quot;Append the final status to local status.txt on this return path.&quot;,
                        &quot;start_line&quot;: 16
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 1,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;mode&quot;: &quot;append&quot;,
                    &quot;op&quot;: &quot;write&quot;,
                    &quot;target&quot;: &quot;status_file&quot;
                  }
                ],
                &quot;effect&quot;: &quot;fs_write&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 16,
                    &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                    &quot;reason&quot;: &quot;Append the final status to local status.txt.&quot;,
                    &quot;start_line&quot;: 16
                  }
                ]
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 16,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The final status is appended before returning the fast.fetch retry body.&quot;,
                &quot;start_line&quot;: 16
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;default&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;end_line&quot;: 16,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The agent runtime appends the fast.fetch retry outcome to status.txt.&quot;,
            &quot;start_line&quot;: 16,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_022&quot;: {
        &quot;empty_effect_evidences&quot;: [
          {
            &quot;end_line&quot;: 13,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The return itself has no content effect; it returns the existing body value.&quot;,
            &quot;start_line&quot;: 13
          }
        ],
        &quot;events&quot;: [],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;end_line&quot;: 13,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The workflow returns the fast.fetch retry body.&quot;,
            &quot;start_line&quot;: 13,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_023&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;demands&quot;: [
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [],
                        &quot;preserve&quot;: &quot;action&quot;,
                        &quot;reason&quot;: &quot;Append the final status before returning.&quot;,
                        &quot;requirement_id&quot;: &quot;R16&quot;,
                        &quot;target&quot;: {
                          &quot;kind&quot;: &quot;self&quot;
                        }
                      },
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [],
                        &quot;preserve&quot;: &quot;value&quot;,
                        &quot;reason&quot;: &quot;Append this path&#x27;s final outcome status.&quot;,
                        &quot;requirement_id&quot;: &quot;R16&quot;,
                        &quot;target&quot;: {
                          &quot;index&quot;: 0,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      }
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 16,
                        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                        &quot;reason&quot;: &quot;Append the final status to local status.txt on this return path.&quot;,
                        &quot;start_line&quot;: 16
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 1,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;mode&quot;: &quot;append&quot;,
                    &quot;op&quot;: &quot;write&quot;,
                    &quot;target&quot;: &quot;status_file&quot;
                  }
                ],
                &quot;effect&quot;: &quot;fs_write&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 16,
                    &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                    &quot;reason&quot;: &quot;Append the final status to local status.txt.&quot;,
                    &quot;start_line&quot;: 16
                  }
                ]
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 16,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The final status is appended before returning the archive.fetch body.&quot;,
                &quot;start_line&quot;: 16
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;default&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;end_line&quot;: 16,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The agent runtime appends the archive.fetch outcome to status.txt.&quot;,
            &quot;start_line&quot;: 16,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_024&quot;: {
        &quot;empty_effect_evidences&quot;: [
          {
            &quot;end_line&quot;: 13,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The return itself has no content effect; it returns the existing body value.&quot;,
            &quot;start_line&quot;: 13
          }
        ],
        &quot;events&quot;: [],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;end_line&quot;: 13,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The workflow returns the archive.fetch body.&quot;,
            &quot;start_line&quot;: 13,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_025&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;demands&quot;: [
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [],
                        &quot;preserve&quot;: &quot;action&quot;,
                        &quot;reason&quot;: &quot;Append the final status before returning.&quot;,
                        &quot;requirement_id&quot;: &quot;R16&quot;,
                        &quot;target&quot;: {
                          &quot;kind&quot;: &quot;self&quot;
                        }
                      },
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [],
                        &quot;preserve&quot;: &quot;value&quot;,
                        &quot;reason&quot;: &quot;Append this path&#x27;s final outcome status.&quot;,
                        &quot;requirement_id&quot;: &quot;R16&quot;,
                        &quot;target&quot;: {
                          &quot;index&quot;: 0,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      }
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 16,
                        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                        &quot;reason&quot;: &quot;Append the final status to local status.txt on this return path.&quot;,
                        &quot;start_line&quot;: 16
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 1,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;mode&quot;: &quot;append&quot;,
                    &quot;op&quot;: &quot;write&quot;,
                    &quot;target&quot;: &quot;status_file&quot;
                  }
                ],
                &quot;effect&quot;: &quot;fs_write&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 16,
                    &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                    &quot;reason&quot;: &quot;Append the final status to local status.txt.&quot;,
                    &quot;start_line&quot;: 16
                  }
                ]
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 16,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The final status is appended before returning the archive.fetch error.&quot;,
                &quot;start_line&quot;: 16
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;default&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;end_line&quot;: 16,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The agent runtime appends the archive.fetch failure outcome to status.txt.&quot;,
            &quot;start_line&quot;: 16,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_026&quot;: {
        &quot;empty_effect_evidences&quot;: [
          {
            &quot;end_line&quot;: 14,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The return itself has no content effect; it returns the existing error value.&quot;,
            &quot;start_line&quot;: 14
          }
        ],
        &quot;events&quot;: [],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;end_line&quot;: 14,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The workflow returns the archive.fetch error.&quot;,
            &quot;start_line&quot;: 14,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      }
    },
    &quot;location_evidences&quot;: {
      &quot;archive_fetch&quot;: [
        {
          &quot;end_line&quot;: 12,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;archive.fetch is the bounded fallback called with source_id only.&quot;,
          &quot;start_line&quot;: 11
        }
      ],
      &quot;environment&quot;: [
        {
          &quot;end_line&quot;: 8,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;FAST_KEY is read from the environment.&quot;,
          &quot;start_line&quot;: 8
        }
      ],
      &quot;fast_fetch&quot;: [
        {
          &quot;end_line&quot;: 10,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;fast.fetch is the preferred credential-gated tool called first and retried once.&quot;,
          &quot;start_line&quot;: 9
        }
      ],
      &quot;status_file&quot;: [
        {
          &quot;end_line&quot;: 16,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The final status is appended to local status.txt on every return path.&quot;,
          &quot;start_line&quot;: 16
        }
      ],
      &quot;user_request&quot;: [
        {
          &quot;end_line&quot;: 8,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;source_id is read from the user&#x27;s request.&quot;,
          &quot;start_line&quot;: 8
        }
      ]
    },
    &quot;locations&quot;: {
      &quot;archive_fetch&quot;: {
        &quot;access_scope&quot;: &quot;recipient&quot;,
        &quot;kind&quot;: &quot;tool&quot;,
        &quot;name&quot;: &quot;archive.fetch&quot;,
        &quot;operand_refs&quot;: [
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_015&quot;,
            &quot;side&quot;: &quot;input&quot;
          }
        ],
        &quot;retention&quot;: null
      },
      &quot;environment&quot;: {
        &quot;access_scope&quot;: &quot;task&quot;,
        &quot;kind&quot;: &quot;runtime_context&quot;,
        &quot;name&quot;: &quot;environment&quot;,
        &quot;operand_refs&quot;: [
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_003&quot;,
            &quot;side&quot;: &quot;input&quot;
          }
        ],
        &quot;retention&quot;: &quot;task&quot;
      },
      &quot;fast_fetch&quot;: {
        &quot;access_scope&quot;: &quot;recipient&quot;,
        &quot;kind&quot;: &quot;tool&quot;,
        &quot;name&quot;: &quot;fast.fetch&quot;,
        &quot;operand_refs&quot;: [
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_007&quot;,
            &quot;side&quot;: &quot;input&quot;
          },
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_011&quot;,
            &quot;side&quot;: &quot;input&quot;
          }
        ],
        &quot;retention&quot;: null
      },
      &quot;status_file&quot;: {
        &quot;access_scope&quot;: &quot;task&quot;,
        &quot;kind&quot;: &quot;storage&quot;,
        &quot;name&quot;: &quot;status.txt&quot;,
        &quot;operand_refs&quot;: [
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_019&quot;,
            &quot;side&quot;: &quot;input&quot;
          },
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_021&quot;,
            &quot;side&quot;: &quot;input&quot;
          },
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_023&quot;,
            &quot;side&quot;: &quot;input&quot;
          },
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_025&quot;,
            &quot;side&quot;: &quot;input&quot;
          }
        ],
        &quot;retention&quot;: &quot;persistent&quot;
      },
      &quot;user_request&quot;: {
        &quot;access_scope&quot;: &quot;task&quot;,
        &quot;kind&quot;: &quot;runtime_context&quot;,
        &quot;name&quot;: &quot;user_request&quot;,
        &quot;operand_refs&quot;: [
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_001&quot;,
            &quot;side&quot;: &quot;input&quot;
          }
        ],
        &quot;retention&quot;: &quot;task&quot;
      }
    },
    &quot;outcome&quot;: &quot;completed&quot;,
    &quot;realizations&quot;: [
      {
        &quot;bindings&quot;: [
          {
            &quot;reason&quot;: &quot;ir_001 reads the user_request context and selects source_id.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_001&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;block_001 contains the source_id acquisition step.&quot;,
            &quot;target&quot;: {
              &quot;block_id&quot;: &quot;block_001&quot;,
              &quot;path&quot;: []
            }
          }
        ],
        &quot;gaps&quot;: [],
        &quot;requirement_id&quot;: &quot;R1&quot;,
        &quot;status&quot;: &quot;expressed&quot;
      },
      {
        &quot;bindings&quot;: [
          {
            &quot;reason&quot;: &quot;ir_003 reads the environment context and selects FAST_KEY.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_003&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;block_002 contains the FAST_KEY acquisition step.&quot;,
            &quot;target&quot;: {
              &quot;block_id&quot;: &quot;block_002&quot;,
              &quot;path&quot;: []
            }
          }
        ],
        &quot;gaps&quot;: [],
        &quot;requirement_id&quot;: &quot;R2&quot;,
        &quot;status&quot;: &quot;expressed&quot;
      },
      {
        &quot;bindings&quot;: [
          {
            &quot;reason&quot;: &quot;The FAST_KEY present edge routes to the first fast.fetch call.&quot;,
            &quot;target&quot;: {
              &quot;block_id&quot;: &quot;block_003&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;ir_005 computes whether FAST_KEY is present.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_005&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;ir_007 is the first fast.fetch call with source_id and FAST_KEY on the present path.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_007&quot;,
              &quot;path&quot;: []
            }
          }
        ],
        &quot;constraints&quot;: [
          {
            &quot;condition&quot;: {
              &quot;instruction_id&quot;: &quot;ir_005&quot;,
              &quot;operation_path&quot;: [
                &quot;events&quot;,
                0,
                &quot;events&quot;,
                0,
                &quot;atomic_ops&quot;,
                0
              ],
              &quot;slot&quot;: {
                &quot;kind&quot;: &quot;self&quot;
              }
            },
            &quot;events&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_007&quot;,
                &quot;operation_path&quot;: [
                  &quot;events&quot;,
                  0,
                  &quot;events&quot;,
                  0,
                  &quot;atomic_ops&quot;,
                  0
                ],
                &quot;slot&quot;: {
                  &quot;kind&quot;: &quot;self&quot;
                }
              }
            ],
            &quot;kind&quot;: &quot;only_if&quot;,
            &quot;scope&quot;: {
              &quot;kind&quot;: &quot;task&quot;
            }
          }
        ],
        &quot;gaps&quot;: [],
        &quot;requirement_id&quot;: &quot;R3&quot;,
        &quot;status&quot;: &quot;expressed&quot;
      },
      {
        &quot;bindings&quot;: [
          {
            &quot;reason&quot;: &quot;The FAST_KEY absent edge from block_003 routes directly to block_008.&quot;,
            &quot;target&quot;: {
              &quot;block_id&quot;: &quot;block_003&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;block_008 is the archive.fetch path reached when FAST_KEY is absent, without entering block_004.&quot;,
            &quot;target&quot;: {
              &quot;block_id&quot;: &quot;block_008&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;ir_015 is the archive.fetch call used on the absent path.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_015&quot;,
              &quot;path&quot;: []
            }
          }
        ],
        &quot;constraints&quot;: [
          {
            &quot;condition&quot;: {
              &quot;instruction_id&quot;: &quot;ir_005&quot;,
              &quot;operation_path&quot;: [
                &quot;events&quot;,
                0,
                &quot;events&quot;,
                0,
                &quot;atomic_ops&quot;,
                0
              ],
              &quot;slot&quot;: {
                &quot;kind&quot;: &quot;self&quot;
              }
            },
            &quot;events&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_007&quot;,
                &quot;operation_path&quot;: [
                  &quot;events&quot;,
                  0,
                  &quot;events&quot;,
                  0,
                  &quot;atomic_ops&quot;,
                  0
                ],
                &quot;slot&quot;: {
                  &quot;kind&quot;: &quot;self&quot;
                }
              }
            ],
            &quot;kind&quot;: &quot;only_if&quot;,
            &quot;scope&quot;: {
              &quot;kind&quot;: &quot;task&quot;
            }
          }
        ],
        &quot;gaps&quot;: [],
        &quot;requirement_id&quot;: &quot;R4&quot;,
        &quot;status&quot;: &quot;expressed&quot;
      },
      {
        &quot;bindings&quot;: [
          {
            &quot;reason&quot;: &quot;block_005 classifies the first fast.fetch attempt and routes transient failures to retry.&quot;,
            &quot;target&quot;: {
              &quot;block_id&quot;: &quot;block_005&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;block_006 contains the single fast.fetch retry.&quot;,
            &quot;target&quot;: {
              &quot;block_id&quot;: &quot;block_006&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;ir_009 computes the first outcome and an explicit transient classification used to gate the retry.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_009&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;ir_011 performs the fast.fetch retry with source_id and FAST_KEY.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_011&quot;,
              &quot;path&quot;: []
            }
          }
        ],
        &quot;constraints&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_011&quot;,
                &quot;operation_path&quot;: [
                  &quot;events&quot;,
                  0,
                  &quot;events&quot;,
                  0,
                  &quot;atomic_ops&quot;,
                  0
                ],
                &quot;slot&quot;: {
                  &quot;kind&quot;: &quot;self&quot;
                }
              }
            ],
            &quot;kind&quot;: &quot;at_most&quot;,
            &quot;limit&quot;: 1,
            &quot;scope&quot;: {
              &quot;kind&quot;: &quot;task&quot;
            },
            &quot;success&quot;: null,
            &quot;unit&quot;: &quot;attempt&quot;
          },
          {
            &quot;condition&quot;: {
              &quot;instruction_id&quot;: &quot;ir_009&quot;,
              &quot;operation_path&quot;: [
                &quot;events&quot;,
                0,
                &quot;events&quot;,
                0,
                &quot;atomic_ops&quot;,
                1
              ],
              &quot;slot&quot;: {
                &quot;kind&quot;: &quot;self&quot;
              }
            },
            &quot;events&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_011&quot;,
                &quot;operation_path&quot;: [
                  &quot;events&quot;,
                  0,
                  &quot;events&quot;,
                  0,
                  &quot;atomic_ops&quot;,
                  0
                ],
                &quot;slot&quot;: {
                  &quot;kind&quot;: &quot;self&quot;
                }
              }
            ],
            &quot;kind&quot;: &quot;only_if&quot;,
            &quot;scope&quot;: {
              &quot;kind&quot;: &quot;task&quot;
            }
          }
        ],
        &quot;gaps&quot;: [],
        &quot;requirement_id&quot;: &quot;R5&quot;,
        &quot;status&quot;: &quot;expressed&quot;
      },
      {
        &quot;bindings&quot;: [
          {
            &quot;reason&quot;: &quot;block_005 routes a non-transient first failure directly to block_008, skipping the retry.&quot;,
            &quot;target&quot;: {
              &quot;block_id&quot;: &quot;block_005&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;block_008 is the fallback reached after a non-transient first failure.&quot;,
            &quot;target&quot;: {
              &quot;block_id&quot;: &quot;block_008&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;ir_009 computes the first outcome and an explicit transient classification used to distinguish non-transient failures.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_009&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;ir_011 is the retry that must not occur for a non-transient first failure.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_011&quot;,
              &quot;path&quot;: []
            }
          }
        ],
        &quot;constraints&quot;: [
          {
            &quot;condition&quot;: {
              &quot;instruction_id&quot;: &quot;ir_009&quot;,
              &quot;operation_path&quot;: [
                &quot;events&quot;,
                0,
                &quot;events&quot;,
                0,
                &quot;atomic_ops&quot;,
                1
              ],
              &quot;slot&quot;: {
                &quot;kind&quot;: &quot;self&quot;
              }
            },
            &quot;events&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_011&quot;,
                &quot;operation_path&quot;: [
                  &quot;events&quot;,
                  0,
                  &quot;events&quot;,
                  0,
                  &quot;atomic_ops&quot;,
                  0
                ],
                &quot;slot&quot;: {
                  &quot;kind&quot;: &quot;self&quot;
                }
              }
            ],
            &quot;kind&quot;: &quot;only_if&quot;,
            &quot;scope&quot;: {
              &quot;kind&quot;: &quot;task&quot;
            }
          }
        ],
        &quot;gaps&quot;: [],
        &quot;requirement_id&quot;: &quot;R6&quot;,
        &quot;status&quot;: &quot;expressed&quot;
      },
      {
        &quot;bindings&quot;: [
          {
            &quot;reason&quot;: &quot;The non-transient first failure edge routes to block_008.&quot;,
            &quot;target&quot;: {
              &quot;block_id&quot;: &quot;block_005&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;The failed retry edge routes to block_008.&quot;,
            &quot;target&quot;: {
              &quot;block_id&quot;: &quot;block_007&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;block_008 contains the archive.fetch fallback.&quot;,
            &quot;target&quot;: {
              &quot;block_id&quot;: &quot;block_008&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;ir_015 is the archive.fetch call with source_id as its only argument.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_015&quot;,
              &quot;path&quot;: []
            }
          }
        ],
        &quot;gaps&quot;: [],
        &quot;requirement_id&quot;: &quot;R7&quot;,
        &quot;status&quot;: &quot;expressed&quot;
      },
      {
        &quot;bindings&quot;: [
          {
            &quot;reason&quot;: &quot;ir_015 is the archive.fetch call.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_015&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;block_008 contains the only archive.fetch call path.&quot;,
            &quot;target&quot;: {
              &quot;block_id&quot;: &quot;block_008&quot;,
              &quot;path&quot;: []
            }
          }
        ],
        &quot;constraints&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_015&quot;,
                &quot;operation_path&quot;: [
                  &quot;events&quot;,
                  0,
                  &quot;events&quot;,
                  0,
                  &quot;atomic_ops&quot;,
                  0
                ],
                &quot;slot&quot;: {
                  &quot;kind&quot;: &quot;self&quot;
                }
              }
            ],
            &quot;kind&quot;: &quot;at_most&quot;,
            &quot;limit&quot;: 1,
            &quot;scope&quot;: {
              &quot;kind&quot;: &quot;task&quot;
            },
            &quot;success&quot;: null,
            &quot;unit&quot;: &quot;attempt&quot;
          }
        ],
        &quot;gaps&quot;: [],
        &quot;requirement_id&quot;: &quot;R8&quot;,
        &quot;status&quot;: &quot;expressed&quot;
      },
      {
        &quot;bindings&quot;: [
          {
            &quot;reason&quot;: &quot;ir_015 delivers a request to archive.fetch with source_id as the single input.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_015&quot;,
              &quot;path&quot;: []
            }
          }
        ],
        &quot;gaps&quot;: [],
        &quot;requirement_id&quot;: &quot;R9&quot;,
        &quot;status&quot;: &quot;expressed&quot;
      },
      {
        &quot;bindings&quot;: [
          {
            &quot;reason&quot;: &quot;The first fast.fetch success edge routes to the return in block_010.&quot;,
            &quot;target&quot;: {
              &quot;block_id&quot;: &quot;block_005&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;The retry success edge routes to the return in block_011.&quot;,
            &quot;target&quot;: {
              &quot;block_id&quot;: &quot;block_007&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;The archive.fetch success edge routes to the return in block_012.&quot;,
            &quot;target&quot;: {
              &quot;block_id&quot;: &quot;block_009&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;ir_020 returns the first fast.fetch body.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_020&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;ir_022 returns the fast.fetch retry body.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_022&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;ir_024 returns the archive.fetch body.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_024&quot;,
              &quot;path&quot;: []
            }
          }
        ],
        &quot;gaps&quot;: [],
        &quot;requirement_id&quot;: &quot;R10&quot;,
        &quot;status&quot;: &quot;expressed&quot;
      },
      {
        &quot;bindings&quot;: [
          {
            &quot;reason&quot;: &quot;The first fast.fetch success edge terminates at block_010.&quot;,
            &quot;target&quot;: {
              &quot;block_id&quot;: &quot;block_005&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;The retry success edge terminates at block_011.&quot;,
            &quot;target&quot;: {
              &quot;block_id&quot;: &quot;block_007&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;The archive.fetch success edge terminates at block_012.&quot;,
            &quot;target&quot;: {
              &quot;block_id&quot;: &quot;block_009&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;ir_020 is the first fast.fetch success return.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_020&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;ir_022 is the retry success return.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_022&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;ir_024 is the archive.fetch success return.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_024&quot;,
              &quot;path&quot;: []
            }
          }
        ],
        &quot;constraints&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_007&quot;,
                &quot;operation_path&quot;: [
                  &quot;events&quot;,
                  0,
                  &quot;events&quot;,
                  0,
                  &quot;atomic_ops&quot;,
                  0
                ],
                &quot;slot&quot;: {
                  &quot;kind&quot;: &quot;self&quot;
                }
              },
              {
                &quot;instruction_id&quot;: &quot;ir_011&quot;,
                &quot;operation_path&quot;: [
                  &quot;events&quot;,
                  0,
                  &quot;events&quot;,
                  0,
                  &quot;atomic_ops&quot;,
                  0
                ],
                &quot;slot&quot;: {
                  &quot;kind&quot;: &quot;self&quot;
                }
              },
              {
                &quot;instruction_id&quot;: &quot;ir_015&quot;,
                &quot;operation_path&quot;: [
                  &quot;events&quot;,
                  0,
                  &quot;events&quot;,
                  0,
                  &quot;atomic_ops&quot;,
                  0
                ],
                &quot;slot&quot;: {
                  &quot;kind&quot;: &quot;self&quot;
                }
              }
            ],
            &quot;kind&quot;: &quot;forbid_after&quot;,
            &quot;scope&quot;: {
              &quot;kind&quot;: &quot;task&quot;
            },
            &quot;triggers&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_020&quot;,
                &quot;path&quot;: []
              }
            ]
          },
          {
            &quot;events&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_007&quot;,
                &quot;operation_path&quot;: [
                  &quot;events&quot;,
                  0,
                  &quot;events&quot;,
                  0,
                  &quot;atomic_ops&quot;,
                  0
                ],
                &quot;slot&quot;: {
                  &quot;kind&quot;: &quot;self&quot;
                }
              },
              {
                &quot;instruction_id&quot;: &quot;ir_011&quot;,
                &quot;operation_path&quot;: [
                  &quot;events&quot;,
                  0,
                  &quot;events&quot;,
                  0,
                  &quot;atomic_ops&quot;,
                  0
                ],
                &quot;slot&quot;: {
                  &quot;kind&quot;: &quot;self&quot;
                }
              },
              {
                &quot;instruction_id&quot;: &quot;ir_015&quot;,
                &quot;operation_path&quot;: [
                  &quot;events&quot;,
                  0,
                  &quot;events&quot;,
                  0,
                  &quot;atomic_ops&quot;,
                  0
                ],
                &quot;slot&quot;: {
                  &quot;kind&quot;: &quot;self&quot;
                }
              }
            ],
            &quot;kind&quot;: &quot;forbid_after&quot;,
            &quot;scope&quot;: {
              &quot;kind&quot;: &quot;task&quot;
            },
            &quot;triggers&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_022&quot;,
                &quot;path&quot;: []
              }
            ]
          },
          {
            &quot;events&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_007&quot;,
                &quot;operation_path&quot;: [
                  &quot;events&quot;,
                  0,
                  &quot;events&quot;,
                  0,
                  &quot;atomic_ops&quot;,
                  0
                ],
                &quot;slot&quot;: {
                  &quot;kind&quot;: &quot;self&quot;
                }
              },
              {
                &quot;instruction_id&quot;: &quot;ir_011&quot;,
                &quot;operation_path&quot;: [
                  &quot;events&quot;,
                  0,
                  &quot;events&quot;,
                  0,
                  &quot;atomic_ops&quot;,
                  0
                ],
                &quot;slot&quot;: {
                  &quot;kind&quot;: &quot;self&quot;
                }
              },
              {
                &quot;instruction_id&quot;: &quot;ir_015&quot;,
                &quot;operation_path&quot;: [
                  &quot;events&quot;,
                  0,
                  &quot;events&quot;,
                  0,
                  &quot;atomic_ops&quot;,
                  0
                ],
                &quot;slot&quot;: {
                  &quot;kind&quot;: &quot;self&quot;
                }
              }
            ],
            &quot;kind&quot;: &quot;forbid_after&quot;,
            &quot;scope&quot;: {
              &quot;kind&quot;: &quot;task&quot;
            },
            &quot;triggers&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_024&quot;,
                &quot;path&quot;: []
              }
            ]
          }
        ],
        &quot;gaps&quot;: [],
        &quot;requirement_id&quot;: &quot;R11&quot;,
        &quot;status&quot;: &quot;expressed&quot;
      },
      {
        &quot;bindings&quot;: [
          {
            &quot;reason&quot;: &quot;The archive.fetch failure edge routes to block_013.&quot;,
            &quot;target&quot;: {
              &quot;block_id&quot;: &quot;block_009&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;block_013 returns the archive.fetch error and is terminal.&quot;,
            &quot;target&quot;: {
              &quot;block_id&quot;: &quot;block_013&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;ir_017 classifies the archive.fetch result and exposes the error.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_017&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;ir_026 returns the archive.fetch error.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_026&quot;,
              &quot;path&quot;: []
            }
          }
        ],
        &quot;gaps&quot;: [],
        &quot;requirement_id&quot;: &quot;R12&quot;,
        &quot;status&quot;: &quot;expressed&quot;
      },
      {
        &quot;bindings&quot;: [
          {
            &quot;reason&quot;: &quot;ir_015 is the single archive.fetch call.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_015&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;ir_017 classifies the archive.fetch result before any further step.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_017&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;The archive.fetch failure path is terminal and does not loop back to another fetch.&quot;,
            &quot;target&quot;: {
              &quot;block_id&quot;: &quot;block_013&quot;,
              &quot;path&quot;: []
            }
          }
        ],
        &quot;constraints&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_015&quot;,
                &quot;operation_path&quot;: [
                  &quot;events&quot;,
                  0,
                  &quot;events&quot;,
                  0,
                  &quot;atomic_ops&quot;,
                  0
                ],
                &quot;slot&quot;: {
                  &quot;kind&quot;: &quot;self&quot;
                }
              }
            ],
            &quot;kind&quot;: &quot;forbid_after&quot;,
            &quot;scope&quot;: {
              &quot;kind&quot;: &quot;task&quot;
            },
            &quot;triggers&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_017&quot;,
                &quot;path&quot;: []
              }
            ]
          }
        ],
        &quot;gaps&quot;: [],
        &quot;requirement_id&quot;: &quot;R13&quot;,
        &quot;status&quot;: &quot;expressed&quot;
      },
      {
        &quot;bindings&quot;: [
          {
            &quot;reason&quot;: &quot;ir_003 defines the FAST_KEY value.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_003&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;ir_015 is the archive.fetch call that must not receive FAST_KEY.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_015&quot;,
              &quot;path&quot;: []
            }
          }
        ],
        &quot;constraints&quot;: [
          {
            &quot;events&quot;: null,
            &quot;kind&quot;: &quot;forbid_information&quot;,
            &quot;path&quot;: [],
            &quot;receivers&quot;: {
              &quot;ids&quot;: [
                &quot;archive_fetch&quot;
              ],
              &quot;kind&quot;: &quot;locations&quot;
            },
            &quot;scope&quot;: {
              &quot;kind&quot;: &quot;task&quot;
            },
            &quot;source&quot;: {
              &quot;instruction_id&quot;: &quot;ir_003&quot;,
              &quot;scope_path&quot;: [],
              &quot;value&quot;: {
                &quot;kind&quot;: &quot;local&quot;,
                &quot;name&quot;: &quot;fast_key&quot;
              }
            }
          }
        ],
        &quot;gaps&quot;: [],
        &quot;requirement_id&quot;: &quot;R14&quot;,
        &quot;status&quot;: &quot;expressed&quot;
      },
      {
        &quot;bindings&quot;: [
          {
            &quot;reason&quot;: &quot;ir_003 defines the FAST_KEY value.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_003&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;The local status output is status.txt via the append in block_010.&quot;,
            &quot;target&quot;: {
              &quot;block_id&quot;: &quot;block_010&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;The local status output is status.txt via the append in block_011.&quot;,
            &quot;target&quot;: {
              &quot;block_id&quot;: &quot;block_011&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;The local status output is status.txt via the append in block_012.&quot;,
            &quot;target&quot;: {
              &quot;block_id&quot;: &quot;block_012&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;The local status output is status.txt via the append in block_013.&quot;,
            &quot;target&quot;: {
              &quot;block_id&quot;: &quot;block_013&quot;,
              &quot;path&quot;: []
            }
          }
        ],
        &quot;constraints&quot;: [
          {
            &quot;events&quot;: null,
            &quot;kind&quot;: &quot;forbid_information&quot;,
            &quot;path&quot;: [],
            &quot;receivers&quot;: {
              &quot;ids&quot;: [
                &quot;status_file&quot;
              ],
              &quot;kind&quot;: &quot;locations&quot;
            },
            &quot;scope&quot;: {
              &quot;kind&quot;: &quot;task&quot;
            },
            &quot;source&quot;: {
              &quot;instruction_id&quot;: &quot;ir_003&quot;,
              &quot;scope_path&quot;: [],
              &quot;value&quot;: {
                &quot;kind&quot;: &quot;local&quot;,
                &quot;name&quot;: &quot;fast_key&quot;
              }
            }
          }
        ],
        &quot;gaps&quot;: [],
        &quot;requirement_id&quot;: &quot;R15&quot;,
        &quot;status&quot;: &quot;expressed&quot;
      },
      {
        &quot;bindings&quot;: [
          {
            &quot;reason&quot;: &quot;block_010 appends status before returning the first fast.fetch body.&quot;,
            &quot;target&quot;: {
              &quot;block_id&quot;: &quot;block_010&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;block_011 appends status before returning the retry body.&quot;,
            &quot;target&quot;: {
              &quot;block_id&quot;: &quot;block_011&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;block_012 appends status before returning the archive.fetch body.&quot;,
            &quot;target&quot;: {
              &quot;block_id&quot;: &quot;block_012&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;block_013 appends status before returning the archive.fetch error.&quot;,
            &quot;target&quot;: {
              &quot;block_id&quot;: &quot;block_013&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;ir_019 appends the first fast.fetch outcome.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_019&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;ir_020 is the return after the first append.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_020&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;ir_021 appends the fast.fetch retry outcome.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_021&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;ir_022 is the return after the retry append.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_022&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;ir_023 appends the archive.fetch outcome.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_023&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;ir_024 is the return after the archive success append.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_024&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;ir_025 appends the archive.fetch outcome on failure.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_025&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;ir_026 is the return after the archive failure append.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_026&quot;,
              &quot;path&quot;: []
            }
          }
        ],
        &quot;constraints&quot;: [
          {
            &quot;after&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_020&quot;,
                &quot;path&quot;: []
              }
            ],
            &quot;before&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_019&quot;,
                &quot;operation_path&quot;: [
                  &quot;events&quot;,
                  0,
                  &quot;events&quot;,
                  0,
                  &quot;atomic_ops&quot;,
                  0
                ],
                &quot;slot&quot;: {
                  &quot;kind&quot;: &quot;self&quot;
                }
              }
            ],
            &quot;kind&quot;: &quot;requires_prior&quot;,
            &quot;matching&quot;: &quot;scope&quot;,
            &quot;scope&quot;: {
              &quot;kind&quot;: &quot;task&quot;
            }
          },
          {
            &quot;after&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_022&quot;,
                &quot;path&quot;: []
              }
            ],
            &quot;before&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_021&quot;,
                &quot;operation_path&quot;: [
                  &quot;events&quot;,
                  0,
                  &quot;events&quot;,
                  0,
                  &quot;atomic_ops&quot;,
                  0
                ],
                &quot;slot&quot;: {
                  &quot;kind&quot;: &quot;self&quot;
                }
              }
            ],
            &quot;kind&quot;: &quot;requires_prior&quot;,
            &quot;matching&quot;: &quot;scope&quot;,
            &quot;scope&quot;: {
              &quot;kind&quot;: &quot;task&quot;
            }
          },
          {
            &quot;after&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_024&quot;,
                &quot;path&quot;: []
              }
            ],
            &quot;before&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_023&quot;,
                &quot;operation_path&quot;: [
                  &quot;events&quot;,
                  0,
                  &quot;events&quot;,
                  0,
                  &quot;atomic_ops&quot;,
                  0
                ],
                &quot;slot&quot;: {
                  &quot;kind&quot;: &quot;self&quot;
                }
              }
            ],
            &quot;kind&quot;: &quot;requires_prior&quot;,
            &quot;matching&quot;: &quot;scope&quot;,
            &quot;scope&quot;: {
              &quot;kind&quot;: &quot;task&quot;
            }
          },
          {
            &quot;after&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_026&quot;,
                &quot;path&quot;: []
              }
            ],
            &quot;before&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_025&quot;,
                &quot;operation_path&quot;: [
                  &quot;events&quot;,
                  0,
                  &quot;events&quot;,
                  0,
                  &quot;atomic_ops&quot;,
                  0
                ],
                &quot;slot&quot;: {
                  &quot;kind&quot;: &quot;self&quot;
                }
              }
            ],
            &quot;kind&quot;: &quot;requires_prior&quot;,
            &quot;matching&quot;: &quot;scope&quot;,
            &quot;scope&quot;: {
              &quot;kind&quot;: &quot;task&quot;
            }
          }
        ],
        &quot;gaps&quot;: [],
        &quot;requirement_id&quot;: &quot;R16&quot;,
        &quot;status&quot;: &quot;expressed&quot;
      }
    ],
    &quot;task_revision_id&quot;: &quot;5795dc07441e3a322e4d09d174e9478c9d396acbadaf4314048fc565d815f4f9&quot;
  }
}</pre>

</details>

