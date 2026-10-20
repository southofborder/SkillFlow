# Basic data propagation records

**These records describe static possible behavior under the shared abstract runtime contract, not execution logs. complete means only that solving finished under the contract, not that the model actually observed this content. Default observations and explicit exceptions jointly constrain analysis. Fixed ordering or absence of a contract citation does not establish an observed runtime fact.**

Shared contract: `skillflow-abstract-runtime-v7`; SHA-256: `32abb3320d5d1b1e9c18c37622c0d523317faaa0f69027de15b7ce76c61b3eda`.

Solver status: `complete`.

IR record coverage: 12 / 12.

[Local visual review](report.html) · [Data](data.json) · [Operation records](records.json) · [Sink list](sinks.json)

D labels are report-local short names. Input/output indexes refer to atomic-operation arguments, not original IR operands. Control slots determine inclusion or observation and are not delivered payload. Candidate sets do not imply simultaneous occurrence; possible does not imply complete plaintext inclusion. This stage makes no risk, necessity or DOE judgment. Read scope, model observation, explicit selection and actual arguments are reviewed separately; a tool boundary does not imply networking.

[Frozen runtime contract text](../inputs/runtime-contract.json) (runtime_contract); Expand the audit section below for individual evidence.

## Receiving and storage boundaries

Included positions: 12 operation positions; per-element candidate groups show arguments separately, using existing scope coordinates.

Levels describe boundary properties only: 0 task-local temporary, 1 task-local persistent, 2 another principal/shared, 3 public. They do not measure sensitivity, necessity or final risk. Coverage identifies unevaluated operations; empty arguments do not establish absence of unmodeled content.

| IR / step | Included | Type / level | Target, access / retention | Actual arguments by slot | Rationale and property evidence |
|---|---|---|---|---|---|
| ir_001 / 2.1 | Included | model_observe / 2 | __compiled_model_context__ · model_context: Current model processing context · recipient / Retention period not modeled | 0: D017 | Another recipient or cross-principal sharing; EM10, EM12 |
| ir_003 / 1.1 | Included | model_observe / 2 | __compiled_model_context__ · model_context: Current model processing context · recipient / Retention period not modeled | 0: D017 | Another recipient or cross-principal sharing; EM10, EM12 |
| ir_004 / 1.1 | Included | model_observe / 2 | __compiled_model_context__ · model_context: Current model processing context · recipient / Retention period not modeled | 0: D017 | Another recipient or cross-principal sharing; EM10, EM12 |
| ir_005 / 1.1 | Included | model_observe / 2 | __compiled_model_context__ · model_context: Current model processing context · recipient / Retention period not modeled | 0: D017 | Another recipient or cross-principal sharing; EM10, EM12 |
| ir_007 / 1.1 | Included | model_observe / 2 | __compiled_model_context__ · model_context: Current model processing context · recipient / Retention period not modeled | 0: D009; 1: D005; 2: D004 | Another recipient or cross-principal sharing; EM10, EM12 |
| ir_007 / 2.1 | Included | model_observe / 2 | __compiled_model_context__ · model_context: Current model processing context · recipient / Retention period not modeled | 0: D015 | Another recipient or cross-principal sharing; EM10, EM12 |
| ir_007 / 3.1 | Included | model_observe / 2 | __compiled_model_context__ · model_context: Current model processing context · recipient / Retention period not modeled | 0: D011 | Another recipient or cross-principal sharing; EM10, EM12 |
| ir_007 / 5.1 | Included | external_tool / 2 | index_search · tool: index.search · recipient / Retention period not modeled | 0: D003, D014, D019, D022 | Another recipient or cross-principal sharing; skill/references/workflow.md:7-7 |
| ir_007 / 6.1 | Included | model_observe / 2 | __compiled_model_context__ · model_context: Current model processing context · recipient / Retention period not modeled | 0: D006, D008, D010, D013 | Another recipient or cross-principal sharing; EM10, EM12 |
| ir_009 / 1.1 | Included | model_observe / 2 | __compiled_model_context__ · model_context: Current model processing context · recipient / Retention period not modeled | 0: D006, D008, D010, D013 | Another recipient or cross-principal sharing; EM10, EM12 |
| ir_010 / 1.1 | Included | storage_write / 1 | count_file · storage: count.txt · task / persistent | 0: D001, D002, D018, D020 | Task-internal, retained across tasks; skill/references/workflow.md:21-21 |
| ir_011 / 1.1 | Included | model_observe / 2 | __compiled_model_context__ · model_context: Current model processing context · recipient / Retention period not modeled | 0: D006, D008, D010, D013 | Another recipient or cross-principal sharing; EM10, EM12 |

<details><summary>Complete source</summary>

<pre>{
  &quot;files&quot;: [
    {
      &quot;content&quot;: &quot;---\nname: catalog-query\ndescription: Query an index once using a supplied request and preserve optional-parameter semantics.\n---\n\n# Catalog Query\n\nFollow the requirements in [workflow instructions](references/workflow.md); this file is part of the current workflow.\n&quot;,
      &quot;path&quot;: &quot;SKILL.md&quot;,
      &quot;sha256&quot;: &quot;60ab6f65755b224fc8f3b0b267f1e8f2e149b5fee87699d45e76842258ee7181&quot;
    },
    {
      &quot;content&quot;: &quot;missing_arguments:\n  from_date: omit\n  limit: omit\n&quot;,
      &quot;path&quot;: &quot;query.yaml&quot;,
      &quot;sha256&quot;: &quot;a8a3256dda0c39c5738829e27d79563ff50938a15ed5bae4389bcf481e477d42&quot;
    },
    {
      &quot;content&quot;: &quot;# Query workflow\n\n&gt; Capability note: index.search supports fuzzy matching; this note does not request fuzzy expansion in this workflow.\n\nRead the user-supplied request.json, which contains term and may contain from_date and limit.\n\nCall index.search exactly once, using request.term unchanged as its query argument.\n\n- Call argument requirements:\n  - When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.\n  - When from_date is missing, omit the from_date argument.\n  - When limit is present, pass its value unchanged as the limit argument.\n  - When limit is missing, omit the limit argument.\n\nApply the missing-argument settings in [query configuration](../query.yaml) to this same call.\n\nDo not invoke index.delete anywhere in this workflow.\n\nParameter descriptions are call requirements and do not instruct pre-call validation or normalization.\n\nAfter the search, write the response&#x27;s total value to local count.txt.\n\nReturn the search response&#x27;s items value unchanged.\n&quot;,
      &quot;path&quot;: &quot;references/workflow.md&quot;,
      &quot;sha256&quot;: &quot;923dc4fb2a2ca28fdbe2caa9b2f348573e4af50dad5c51b930f0c672d180a7e2&quot;
    }
  ],
  &quot;source_sha256&quot;: &quot;66bc23209ed1dccd2232511bd2933a076c2bb101e0b180737668b78f6dad618c&quot;
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
    &quot;ir_012&quot;: &quot;processed&quot;
  },
  &quot;diagnostics&quot;: []
}</pre>

</details>

## ir_001 · read_request_json

Block: block_001; Operator: agent_runtime.

IR inputs: 0: request.json

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
    }
  ]
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| 1.1 | fs_read | read | — | storage: request.json | 0: D017 |
| 2.1 | model_observe (program-generated, statically possible) | deliver | 0: D017 | model_context: Current model processing context | — |

Entry/exit changes: 

- `result: result_001`: Unbound → D017

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
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
                &quot;end_line&quot;: 5,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;This line directs reading the supplied request.json.&quot;,
                &quot;start_line&quot;: 5
              }
            ],
            &quot;location&quot;: &quot;request_file&quot;,
            &quot;op&quot;: &quot;read&quot;,
            &quot;output&quot;: &quot;request_data&quot;
          }
        ],
        &quot;effect&quot;: &quot;fs_read&quot;,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 5,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;Reading the supplied request file is the specified data acquisition.&quot;,
            &quot;start_line&quot;: 5
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
                &quot;end_line&quot;: 5,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;This line requires reading the user-supplied request.json.&quot;,
                &quot;start_line&quot;: 5
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;kind&quot;: &quot;local&quot;,
                &quot;name&quot;: &quot;request_data&quot;
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
            &quot;end_line&quot;: 5,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;This line requires reading the user-supplied request.json.&quot;,
            &quot;start_line&quot;: 5
          }
        ]
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 5,
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;reason&quot;: &quot;The workflow instructs the skill runtime to read the supplied request.json; no external tool is named for this read.&quot;,
        &quot;start_line&quot;: 5,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 5,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;The requested request.json contents are bound to the CFG read result.&quot;,
            &quot;start_line&quot;: 5
          }
        ],
        &quot;output_index&quot;: 0,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;request_data&quot;
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
          &quot;end_line&quot;: 5,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;The requested request.json contents are bound to the CFG read result.&quot;,
          &quot;start_line&quot;: 5
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;request_data&quot;
      }
    }
  ],
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 5,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;This line directs reading the supplied request.json.&quot;,
          &quot;start_line&quot;: 5
        }
      ],
      &quot;location&quot;: &quot;request_file&quot;,
      &quot;op&quot;: &quot;read&quot;,
      &quot;output&quot;: &quot;request_data&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
          &quot;rule_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;end_line&quot;: 5,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;This line requires reading the user-supplied request.json.&quot;,
          &quot;start_line&quot;: 5
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;request_data&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;__compiled_model_context__&quot;
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
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
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
        &quot;reason&quot;: &quot;This dispatch performs only CFG control transfer and has no external effect.&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_002&quot;,
          &quot;path&quot;: []
        }
      }
    ],
    &quot;events&quot;: [],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;reason&quot;: &quot;The CFG dispatch is an internal workflow control step with no explicit tool or human executor.&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_002&quot;,
          &quot;path&quot;: []
        },
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

## ir_003 · extract_query_term

Block: block_002; Operator: agent_runtime.

IR inputs: 0: result_001

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
    }
  ]
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| 1.1 | model_observe (program-generated, statically possible) | deliver | 0: D017 | model_context: Current model processing context | — |
| 2.1 | transform | select_part | 0: D017 | — | 0: D009 |

Entry/exit changes: 

- `result: result_002`: Unbound → D009

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
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
                &quot;end_line&quot;: 7,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;This line requires using request.term unchanged as the query argument.&quot;,
                &quot;start_line&quot;: 7
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
            &quot;end_line&quot;: 7,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;This line requires using request.term unchanged as the query argument.&quot;,
            &quot;start_line&quot;: 7
          }
        ]
      },
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 7,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;This line identifies request.term as the query value to preserve.&quot;,
                &quot;start_line&quot;: 7
              }
            ],
            &quot;input&quot;: {
              &quot;index&quot;: 0,
              &quot;kind&quot;: &quot;input&quot;
            },
            &quot;op&quot;: &quot;select_part&quot;,
            &quot;output&quot;: &quot;query_term&quot;,
            &quot;path&quot;: [
              &quot;term&quot;
            ]
          }
        ],
        &quot;effect&quot;: &quot;transform&quot;,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 7,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;The request term is selected unchanged for the search call.&quot;,
            &quot;start_line&quot;: 7
          }
        ]
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 7,
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;reason&quot;: &quot;The workflow directs the skill runtime to use request.term as the search query; orchestration of that extraction is an agent-runtime step.&quot;,
        &quot;start_line&quot;: 7,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 7,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;The extracted request.term value is bound to the CFG extraction result.&quot;,
            &quot;start_line&quot;: 7
          }
        ],
        &quot;output_index&quot;: 0,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;query_term&quot;
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
          &quot;end_line&quot;: 7,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;The extracted request.term value is bound to the CFG extraction result.&quot;,
          &quot;start_line&quot;: 7
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;query_term&quot;
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
          &quot;end_line&quot;: 7,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;This line requires using request.term unchanged as the query argument.&quot;,
          &quot;start_line&quot;: 7
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
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 7,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;This line identifies request.term as the query value to preserve.&quot;,
          &quot;start_line&quot;: 7
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;query_term&quot;,
      &quot;path&quot;: [
        &quot;term&quot;
      ]
    }
  ]
}</pre>

</details>

## ir_004 · extract_optional_from_date

Block: block_002; Operator: agent_runtime.

IR inputs: 0: result_001

IR outputs: 0: result_003, 1: result_004

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
| 2.1 | transform | select_part | 0: D017 | — | 0: D015 |
| 2.2 | transform | compute | 0: D017 | — | 0: D005 |

Entry/exit changes: 

- `result: result_003`: Unbound → D015
- `result: result_004`: Unbound → D005

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
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
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;These lines define presence-dependent handling of from_date.&quot;,
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
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;These lines define presence-dependent handling of from_date.&quot;,
            &quot;start_line&quot;: 10
          }
        ]
      },
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 10,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;This line requires passing a present from_date value unchanged.&quot;,
                &quot;start_line&quot;: 10
              }
            ],
            &quot;input&quot;: {
              &quot;index&quot;: 0,
              &quot;kind&quot;: &quot;input&quot;
            },
            &quot;op&quot;: &quot;select_part&quot;,
            &quot;output&quot;: &quot;from_date_value&quot;,
            &quot;path&quot;: [
              &quot;from_date&quot;
            ]
          },
          {
            &quot;dependencies&quot;: [
              &quot;derived&quot;
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 11,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;These lines distinguish a present from_date from a missing from_date.&quot;,
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
            &quot;output&quot;: &quot;from_date_present&quot;
          }
        ],
        &quot;effect&quot;: &quot;transform&quot;,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 11,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;The optional from_date value and its presence are extracted for conditional construction.&quot;,
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
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;reason&quot;: &quot;The workflow directs extracting and conditionally using the optional from_date field; this orchestration is performed by the skill runtime.&quot;,
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
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;A present from_date value is bound to the CFG optional-value result.&quot;,
            &quot;start_line&quot;: 10
          }
        ],
        &quot;output_index&quot;: 0,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;from_date_value&quot;
        }
      },
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 11,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;The presence of from_date is bound to the CFG presence result.&quot;,
            &quot;start_line&quot;: 10
          }
        ],
        &quot;output_index&quot;: 1,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;from_date_present&quot;
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
          &quot;end_line&quot;: 10,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;A present from_date value is bound to the CFG optional-value result.&quot;,
          &quot;start_line&quot;: 10
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;from_date_value&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 11,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;The presence of from_date is bound to the CFG presence result.&quot;,
          &quot;start_line&quot;: 10
        }
      ],
      &quot;output_index&quot;: 1,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;from_date_present&quot;
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
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;These lines define presence-dependent handling of from_date.&quot;,
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
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 10,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;This line requires passing a present from_date value unchanged.&quot;,
          &quot;start_line&quot;: 10
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;from_date_value&quot;,
      &quot;path&quot;: [
        &quot;from_date&quot;
      ]
    },
    {
      &quot;dependencies&quot;: [
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 11,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;These lines distinguish a present from_date from a missing from_date.&quot;,
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
      &quot;output&quot;: &quot;from_date_present&quot;
    }
  ]
}</pre>

</details>

## ir_005 · extract_optional_limit

Block: block_002; Operator: agent_runtime.

IR inputs: 0: result_001

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
    }
  ]
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| 1.1 | model_observe (program-generated, statically possible) | deliver | 0: D017 | model_context: Current model processing context | — |
| 2.1 | transform | select_part | 0: D017 | — | 0: D011 |
| 2.2 | transform | compute | 0: D017 | — | 0: D004 |

Entry/exit changes: 

- `result: result_005`: Unbound → D011
- `result: result_006`: Unbound → D004

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
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
                &quot;end_line&quot;: 13,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;These lines define presence-dependent handling of limit.&quot;,
                &quot;start_line&quot;: 12
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
            &quot;end_line&quot;: 13,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;These lines define presence-dependent handling of limit.&quot;,
            &quot;start_line&quot;: 12
          }
        ]
      },
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 12,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;This line requires passing a present limit value unchanged.&quot;,
                &quot;start_line&quot;: 12
              }
            ],
            &quot;input&quot;: {
              &quot;index&quot;: 0,
              &quot;kind&quot;: &quot;input&quot;
            },
            &quot;op&quot;: &quot;select_part&quot;,
            &quot;output&quot;: &quot;limit_value&quot;,
            &quot;path&quot;: [
              &quot;limit&quot;
            ]
          },
          {
            &quot;dependencies&quot;: [
              &quot;derived&quot;
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 13,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;These lines distinguish a present limit from a missing limit.&quot;,
                &quot;start_line&quot;: 12
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;index&quot;: 0,
                &quot;kind&quot;: &quot;input&quot;
              }
            ],
            &quot;op&quot;: &quot;compute&quot;,
            &quot;output&quot;: &quot;limit_present&quot;
          }
        ],
        &quot;effect&quot;: &quot;transform&quot;,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 13,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;The optional limit value and its presence are extracted for conditional construction.&quot;,
            &quot;start_line&quot;: 12
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
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;reason&quot;: &quot;The workflow directs extracting and conditionally using the optional limit field; this orchestration is performed by the skill runtime.&quot;,
        &quot;start_line&quot;: 12,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 12,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;A present limit value is bound to the CFG optional-value result.&quot;,
            &quot;start_line&quot;: 12
          }
        ],
        &quot;output_index&quot;: 0,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;limit_value&quot;
        }
      },
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 13,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;The presence of limit is bound to the CFG presence result.&quot;,
            &quot;start_line&quot;: 12
          }
        ],
        &quot;output_index&quot;: 1,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;limit_present&quot;
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
          &quot;end_line&quot;: 12,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;A present limit value is bound to the CFG optional-value result.&quot;,
          &quot;start_line&quot;: 12
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;limit_value&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 13,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;The presence of limit is bound to the CFG presence result.&quot;,
          &quot;start_line&quot;: 12
        }
      ],
      &quot;output_index&quot;: 1,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;limit_present&quot;
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
          &quot;end_line&quot;: 13,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;These lines define presence-dependent handling of limit.&quot;,
          &quot;start_line&quot;: 12
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
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 12,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;This line requires passing a present limit value unchanged.&quot;,
          &quot;start_line&quot;: 12
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;limit_value&quot;,
      &quot;path&quot;: [
        &quot;limit&quot;
      ]
    },
    {
      &quot;dependencies&quot;: [
        &quot;derived&quot;
      ],
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 13,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;These lines distinguish a present limit from a missing limit.&quot;,
          &quot;start_line&quot;: 12
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;compute&quot;,
      &quot;output&quot;: &quot;limit_present&quot;
    }
  ]
}</pre>

</details>

## ir_006 · dispatch

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
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
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
        &quot;reason&quot;: &quot;This dispatch performs only CFG control transfer and has no external effect.&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_006&quot;,
          &quot;path&quot;: []
        }
      }
    ],
    &quot;events&quot;: [],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;reason&quot;: &quot;The CFG dispatch is an internal workflow control step with no explicit tool or human executor.&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_006&quot;,
          &quot;path&quot;: []
        },
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

## ir_007 · index.search

Block: block_003; Operator: agent_runtime, tool.

IR inputs: 0: index.search, 1: result_002, 2: result_003, 3: result_004, 4: result_005, 5: result_006

IR outputs: 0: result_007

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
        &quot;event_index&quot;: 1,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 3,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 2,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 4,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 3,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 4,
        &quot;op_index&quot;: 1
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 3,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 4,
        &quot;op_index&quot;: 1
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 4,
        &quot;op_index&quot;: 0
      }
    },
    {
      &quot;after&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 5,
        &quot;op_index&quot;: 0
      },
      &quot;before&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 4,
        &quot;op_index&quot;: 1
      }
    }
  ]
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| 1.1 | model_observe (program-generated, statically possible) | deliver | 0: D009; 1: D005; 2: D004 | model_context: Current model processing context | — |
| 2.1 | model_observe (program-generated, statically possible) | deliver | 0: D015; 1 (control): D005; Condition: Retain both inclusion and omission possibilities | model_context: Current model processing context | — |
| 3.1 | model_observe (program-generated, statically possible) | deliver | 0: D011; 1 (control): D004; Condition: Retain both inclusion and omission possibilities | model_context: Current model processing context | — |
| 4.1 | transform | build | 0: D009; 1 (control): D005; 2: D015; 3 (control): D004; 4: D011 | — | 0: D003, D014, D019, D022 |
| 4.1 · Member | — | [   &quot;query&quot; ] | Original-value slot 0; Condition slot None | — | Include original value |
| 4.1 · Member | — | [   &quot;from_date&quot; ] | Original-value slot 2; Condition slot 1 | — | Inclusion / omission candidates |
| 4.1 · Member | — | [   &quot;limit&quot; ] | Original-value slot 4; Condition slot 3 | — | Inclusion / omission candidates |
| 5.1 | Unlabeled data operation | deliver | 0: D003, D014, D019, D022 | tool: index.search | — |
| 5.2 | Unlabeled data operation | receive | 0: D003, D014, D019, D022 | tool: index.search | 0: D006, D008, D010, D013 |
| 6.1 | model_observe (program-generated, statically possible) | deliver | 0: D006, D008, D010, D013 | model_context: Current model processing context | — |

Entry/exit changes: 

- `result: result_007`: Unbound → D006, D008, D010, D013

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
          &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
          &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
          &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
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
                &quot;end_line&quot;: 7,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;This line requires one index.search call with the request term and optional arguments.&quot;,
                &quot;start_line&quot;: 7
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;index&quot;: 1,
                &quot;kind&quot;: &quot;input&quot;
              },
              {
                &quot;index&quot;: 3,
                &quot;kind&quot;: &quot;input&quot;
              },
              {
                &quot;index&quot;: 5,
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
            &quot;end_line&quot;: 7,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;This line requires one index.search call with the request term and optional arguments.&quot;,
            &quot;start_line&quot;: 7
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
                &quot;end_line&quot;: 7,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;This line requires one index.search call with the request term and optional arguments.&quot;,
                &quot;start_line&quot;: 7
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;index&quot;: 2,
                &quot;kind&quot;: &quot;input&quot;
              }
            ],
            &quot;op&quot;: &quot;deliver&quot;,
            &quot;target&quot;: &quot;__compiled_model_context__&quot;,
            &quot;when&quot;: {
              &quot;index&quot;: 3,
              &quot;kind&quot;: &quot;input&quot;
            }
          }
        ],
        &quot;effect&quot;: &quot;model_observe&quot;,
        &quot;evidences&quot;: [
          {
            &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
            &quot;rule_id&quot;: &quot;EM10&quot;
          },
          {
            &quot;end_line&quot;: 7,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;This line requires one index.search call with the request term and optional arguments.&quot;,
            &quot;start_line&quot;: 7
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
                &quot;end_line&quot;: 7,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;This line requires one index.search call with the request term and optional arguments.&quot;,
                &quot;start_line&quot;: 7
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;index&quot;: 4,
                &quot;kind&quot;: &quot;input&quot;
              }
            ],
            &quot;op&quot;: &quot;deliver&quot;,
            &quot;target&quot;: &quot;__compiled_model_context__&quot;,
            &quot;when&quot;: {
              &quot;index&quot;: 5,
              &quot;kind&quot;: &quot;input&quot;
            }
          }
        ],
        &quot;effect&quot;: &quot;model_observe&quot;,
        &quot;evidences&quot;: [
          {
            &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
            &quot;rule_id&quot;: &quot;EM10&quot;
          },
          {
            &quot;end_line&quot;: 7,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;This line requires one index.search call with the request term and optional arguments.&quot;,
            &quot;start_line&quot;: 7
          }
        ]
      },
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;container&quot;: &quot;object&quot;,
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 7,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;The query argument uses request.term unchanged.&quot;,
                &quot;start_line&quot;: 7
              },
              {
                &quot;end_line&quot;: 13,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;These lines specify inclusion and omission of the optional arguments based on presence.&quot;,
                &quot;start_line&quot;: 10
              },
              {
                &quot;end_line&quot;: 3,
                &quot;file&quot;: &quot;skill/query.yaml&quot;,
                &quot;reason&quot;: &quot;The configuration sets missing from_date and limit arguments to omit.&quot;,
                &quot;start_line&quot;: 2
              }
            ],
            &quot;op&quot;: &quot;build&quot;,
            &quot;output&quot;: &quot;search_request&quot;,
            &quot;parts&quot;: [
              {
                &quot;path&quot;: [
                  &quot;query&quot;
                ],
                &quot;value&quot;: {
                  &quot;index&quot;: 1,
                  &quot;kind&quot;: &quot;input&quot;
                },
                &quot;when&quot;: null
              },
              {
                &quot;path&quot;: [
                  &quot;from_date&quot;
                ],
                &quot;value&quot;: {
                  &quot;index&quot;: 2,
                  &quot;kind&quot;: &quot;input&quot;
                },
                &quot;when&quot;: {
                  &quot;index&quot;: 3,
                  &quot;kind&quot;: &quot;input&quot;
                }
              },
              {
                &quot;path&quot;: [
                  &quot;limit&quot;
                ],
                &quot;value&quot;: {
                  &quot;index&quot;: 4,
                  &quot;kind&quot;: &quot;input&quot;
                },
                &quot;when&quot;: {
                  &quot;index&quot;: 5,
                  &quot;kind&quot;: &quot;input&quot;
                }
              }
            ]
          }
        ],
        &quot;effect&quot;: &quot;transform&quot;,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 15,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;The workflow specifies the query argument and conditional from_date and limit members for the same call.&quot;,
            &quot;start_line&quot;: 7
          }
        ]
      },
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 7,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;The workflow requires calling index.search.&quot;,
                &quot;start_line&quot;: 7
              },
              {
                &quot;end_line&quot;: 13,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;These lines define the argument content and conditional inclusion requirements for that call.&quot;,
                &quot;start_line&quot;: 10
              },
              {
                &quot;end_line&quot;: 15,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;The missing-argument settings apply to this same call.&quot;,
                &quot;start_line&quot;: 15
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;kind&quot;: &quot;local&quot;,
                &quot;name&quot;: &quot;search_request&quot;
              }
            ],
            &quot;op&quot;: &quot;deliver&quot;,
            &quot;target&quot;: &quot;index_search&quot;
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 7,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;The same index.search call yields the search response used by later steps.&quot;,
                &quot;start_line&quot;: 7
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;kind&quot;: &quot;local&quot;,
                &quot;name&quot;: &quot;search_request&quot;
              }
            ],
            &quot;location&quot;: &quot;index_search&quot;,
            &quot;op&quot;: &quot;receive&quot;,
            &quot;output&quot;: &quot;search_response&quot;
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
                &quot;end_line&quot;: 7,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;This line requires one index.search call with the request term and optional arguments.&quot;,
                &quot;start_line&quot;: 7
              }
            ],
            &quot;inputs&quot;: [
              {
                &quot;kind&quot;: &quot;local&quot;,
                &quot;name&quot;: &quot;search_response&quot;
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
            &quot;end_line&quot;: 7,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;This line requires one index.search call with the request term and optional arguments.&quot;,
            &quot;start_line&quot;: 7
          }
        ]
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;,
      &quot;tool&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 7,
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;reason&quot;: &quot;The workflow directs the skill runtime to construct the index.search arguments from the request fields.&quot;,
        &quot;start_line&quot;: 7,
        &quot;value&quot;: &quot;agent_runtime&quot;
      },
      {
        &quot;reason&quot;: &quot;The CFG records index.search as an external_resource argument, independently evidencing a tool interface.&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 0,
          &quot;instruction_id&quot;: &quot;ir_007&quot;,
          &quot;side&quot;: &quot;input&quot;
        },
        &quot;value&quot;: &quot;tool&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 7,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;The search response is the output of the single index.search call.&quot;,
            &quot;start_line&quot;: 7
          }
        ],
        &quot;output_index&quot;: 0,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;search_response&quot;
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
          &quot;event_index&quot;: 1,
          &quot;op_index&quot;: 0
        }
      },
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 3,
          &quot;op_index&quot;: 0
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 2,
          &quot;op_index&quot;: 0
        }
      },
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 4,
          &quot;op_index&quot;: 0
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 3,
          &quot;op_index&quot;: 0
        }
      },
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 4,
          &quot;op_index&quot;: 1
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 3,
          &quot;op_index&quot;: 0
        }
      },
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 4,
          &quot;op_index&quot;: 1
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 4,
          &quot;op_index&quot;: 0
        }
      },
      {
        &quot;after&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 5,
          &quot;op_index&quot;: 0
        },
        &quot;before&quot;: {
          &quot;body_event_index&quot;: null,
          &quot;event_index&quot;: 4,
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
          &quot;end_line&quot;: 7,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;The search response is the output of the single index.search call.&quot;,
          &quot;start_line&quot;: 7
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;search_response&quot;
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
          &quot;end_line&quot;: 7,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;This line requires one index.search call with the request term and optional arguments.&quot;,
          &quot;start_line&quot;: 7
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 1,
          &quot;kind&quot;: &quot;input&quot;
        },
        {
          &quot;index&quot;: 3,
          &quot;kind&quot;: &quot;input&quot;
        },
        {
          &quot;index&quot;: 5,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;__compiled_model_context__&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
          &quot;rule_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;end_line&quot;: 7,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;This line requires one index.search call with the request term and optional arguments.&quot;,
          &quot;start_line&quot;: 7
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 2,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;__compiled_model_context__&quot;,
      &quot;when&quot;: {
        &quot;index&quot;: 3,
        &quot;kind&quot;: &quot;input&quot;
      }
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
          &quot;rule_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;end_line&quot;: 7,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;This line requires one index.search call with the request term and optional arguments.&quot;,
          &quot;start_line&quot;: 7
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;index&quot;: 4,
          &quot;kind&quot;: &quot;input&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;__compiled_model_context__&quot;,
      &quot;when&quot;: {
        &quot;index&quot;: 5,
        &quot;kind&quot;: &quot;input&quot;
      }
    },
    {
      &quot;container&quot;: &quot;object&quot;,
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 7,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;The query argument uses request.term unchanged.&quot;,
          &quot;start_line&quot;: 7
        },
        {
          &quot;end_line&quot;: 13,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;These lines specify inclusion and omission of the optional arguments based on presence.&quot;,
          &quot;start_line&quot;: 10
        },
        {
          &quot;end_line&quot;: 3,
          &quot;file&quot;: &quot;skill/query.yaml&quot;,
          &quot;reason&quot;: &quot;The configuration sets missing from_date and limit arguments to omit.&quot;,
          &quot;start_line&quot;: 2
        }
      ],
      &quot;op&quot;: &quot;build&quot;,
      &quot;output&quot;: &quot;search_request&quot;,
      &quot;parts&quot;: [
        {
          &quot;path&quot;: [
            &quot;query&quot;
          ],
          &quot;value&quot;: {
            &quot;index&quot;: 1,
            &quot;kind&quot;: &quot;input&quot;
          },
          &quot;when&quot;: null
        },
        {
          &quot;path&quot;: [
            &quot;from_date&quot;
          ],
          &quot;value&quot;: {
            &quot;index&quot;: 2,
            &quot;kind&quot;: &quot;input&quot;
          },
          &quot;when&quot;: {
            &quot;index&quot;: 3,
            &quot;kind&quot;: &quot;input&quot;
          }
        },
        {
          &quot;path&quot;: [
            &quot;limit&quot;
          ],
          &quot;value&quot;: {
            &quot;index&quot;: 4,
            &quot;kind&quot;: &quot;input&quot;
          },
          &quot;when&quot;: {
            &quot;index&quot;: 5,
            &quot;kind&quot;: &quot;input&quot;
          }
        }
      ]
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 7,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;The workflow requires calling index.search.&quot;,
          &quot;start_line&quot;: 7
        },
        {
          &quot;end_line&quot;: 13,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;These lines define the argument content and conditional inclusion requirements for that call.&quot;,
          &quot;start_line&quot;: 10
        },
        {
          &quot;end_line&quot;: 15,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;The missing-argument settings apply to this same call.&quot;,
          &quot;start_line&quot;: 15
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;search_request&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;index_search&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 7,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;The same index.search call yields the search response used by later steps.&quot;,
          &quot;start_line&quot;: 7
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;search_request&quot;
        }
      ],
      &quot;location&quot;: &quot;index_search&quot;,
      &quot;op&quot;: &quot;receive&quot;,
      &quot;output&quot;: &quot;search_response&quot;
    },
    {
      &quot;evidences&quot;: [
        {
          &quot;reason&quot;: &quot;The program compiles observations from declared processing modes and actual symbolic references; this does not prove the mode classification or that execution occurred.&quot;,
          &quot;rule_id&quot;: &quot;EM10&quot;
        },
        {
          &quot;end_line&quot;: 7,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;This line requires one index.search call with the request term and optional arguments.&quot;,
          &quot;start_line&quot;: 7
        }
      ],
      &quot;inputs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;search_response&quot;
        }
      ],
      &quot;op&quot;: &quot;deliver&quot;,
      &quot;target&quot;: &quot;__compiled_model_context__&quot;
    }
  ]
}</pre>

</details>

## ir_008 · dispatch

Block: block_003; Operator: agent_runtime.

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
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
          &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
          &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
          &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
          &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
          &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
          &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
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
        &quot;reason&quot;: &quot;This dispatch performs only CFG control transfer and has no external effect.&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_008&quot;,
          &quot;path&quot;: []
        }
      }
    ],
    &quot;events&quot;: [],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;reason&quot;: &quot;The CFG dispatch is an internal workflow control step with no explicit tool or human executor.&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_008&quot;,
          &quot;path&quot;: []
        },
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

## ir_009 · extract_response_total

Block: block_004; Operator: agent_runtime.

IR inputs: 0: result_007

IR outputs: 0: result_008

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
| 1.1 | model_observe (program-generated, statically possible) | deliver | 0: D006, D008, D010, D013 | model_context: Current model processing context | — |
| 2.1 | transform | select_part | 0: D006, D008, D010, D013 | — | 0: D001, D002, D018, D020 |

Entry/exit changes: 

- `result: result_008`: Unbound → D001, D002, D018, D020

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
          &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
          &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
          &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
          &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
          &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
          &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_009b07c5001af2da1d8acba3076888f2a7aa49ea2d80afafcc10b34e1bd1a4bd&quot;,
          &quot;data_048f3f047d3cfd508d82af1052f822b8a36daad60f870bd2320e27d348514221&quot;,
          &quot;data_bd1ba59ec1f944c468c881a67676f62b0095ddc2e9217a2e133cf178abcb2ec9&quot;,
          &quot;data_dc7b982531c6520469643cfd7a66716bad24aaa6ba24f305c1d6b60f15a4af79&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
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
                &quot;end_line&quot;: 21,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;This line requires using the response total after the search.&quot;,
                &quot;start_line&quot;: 21
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
            &quot;end_line&quot;: 21,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;This line requires using the response total after the search.&quot;,
            &quot;start_line&quot;: 21
          }
        ]
      },
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 21,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;This line identifies the response total as the value to write.&quot;,
                &quot;start_line&quot;: 21
              }
            ],
            &quot;input&quot;: {
              &quot;index&quot;: 0,
              &quot;kind&quot;: &quot;input&quot;
            },
            &quot;op&quot;: &quot;select_part&quot;,
            &quot;output&quot;: &quot;response_total&quot;,
            &quot;path&quot;: [
              &quot;total&quot;
            ]
          }
        ],
        &quot;effect&quot;: &quot;transform&quot;,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 21,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;The response total is selected from the search response for writing.&quot;,
            &quot;start_line&quot;: 21
          }
        ]
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 21,
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;reason&quot;: &quot;The workflow directs the skill runtime to obtain the search response total for the local file write.&quot;,
        &quot;start_line&quot;: 21,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 21,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;The selected response total is bound to the CFG total result.&quot;,
            &quot;start_line&quot;: 21
          }
        ],
        &quot;output_index&quot;: 0,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;response_total&quot;
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
          &quot;end_line&quot;: 21,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;The selected response total is bound to the CFG total result.&quot;,
          &quot;start_line&quot;: 21
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;response_total&quot;
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
          &quot;end_line&quot;: 21,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;This line requires using the response total after the search.&quot;,
          &quot;start_line&quot;: 21
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
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 21,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;This line identifies the response total as the value to write.&quot;,
          &quot;start_line&quot;: 21
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;response_total&quot;,
      &quot;path&quot;: [
        &quot;total&quot;
      ]
    }
  ]
}</pre>

</details>

## ir_010 · write_count_file

Block: block_004; Operator: agent_runtime.

IR inputs: 0: count.txt, 1: result_008

IR outputs: []

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| 1.1 | fs_write | write | 0: D001, D002, D018, D020 | storage: count.txt | storage: count.txt: Unbound → D001, D002, D018, D020 (strong) |

Entry/exit changes: 

- `storage: count.txt`: Unbound → D001, D002, D018, D020

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
          &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
          &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
          &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_009b07c5001af2da1d8acba3076888f2a7aa49ea2d80afafcc10b34e1bd1a4bd&quot;,
          &quot;data_048f3f047d3cfd508d82af1052f822b8a36daad60f870bd2320e27d348514221&quot;,
          &quot;data_bd1ba59ec1f944c468c881a67676f62b0095ddc2e9217a2e133cf178abcb2ec9&quot;,
          &quot;data_dc7b982531c6520469643cfd7a66716bad24aaa6ba24f305c1d6b60f15a4af79&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
          &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
          &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
          &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_009b07c5001af2da1d8acba3076888f2a7aa49ea2d80afafcc10b34e1bd1a4bd&quot;,
          &quot;data_048f3f047d3cfd508d82af1052f822b8a36daad60f870bd2320e27d348514221&quot;,
          &quot;data_bd1ba59ec1f944c468c881a67676f62b0095ddc2e9217a2e133cf178abcb2ec9&quot;,
          &quot;data_dc7b982531c6520469643cfd7a66716bad24aaa6ba24f305c1d6b60f15a4af79&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_009b07c5001af2da1d8acba3076888f2a7aa49ea2d80afafcc10b34e1bd1a4bd&quot;,
          &quot;data_048f3f047d3cfd508d82af1052f822b8a36daad60f870bd2320e27d348514221&quot;,
          &quot;data_bd1ba59ec1f944c468c881a67676f62b0095ddc2e9217a2e133cf178abcb2ec9&quot;,
          &quot;data_dc7b982531c6520469643cfd7a66716bad24aaa6ba24f305c1d6b60f15a4af79&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
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
                &quot;end_line&quot;: 21,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;This line requires writing the response total to local count.txt.&quot;,
                &quot;start_line&quot;: 21
              }
            ],
            &quot;input&quot;: {
              &quot;index&quot;: 1,
              &quot;kind&quot;: &quot;input&quot;
            },
            &quot;mode&quot;: &quot;replace&quot;,
            &quot;op&quot;: &quot;write&quot;,
            &quot;target&quot;: &quot;count_file&quot;
          }
        ],
        &quot;effect&quot;: &quot;fs_write&quot;,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 21,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;Writing to the local count.txt file is the specified file effect.&quot;,
            &quot;start_line&quot;: 21
          }
        ]
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 21,
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;reason&quot;: &quot;The workflow directs the skill runtime to write the local count.txt file.&quot;,
        &quot;start_line&quot;: 21,
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
          &quot;end_line&quot;: 21,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;This line requires writing the response total to local count.txt.&quot;,
          &quot;start_line&quot;: 21
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 1,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;mode&quot;: &quot;replace&quot;,
      &quot;op&quot;: &quot;write&quot;,
      &quot;target&quot;: &quot;count_file&quot;
    }
  ]
}</pre>

</details>

## ir_011 · extract_response_items

Block: block_004; Operator: agent_runtime.

IR inputs: 0: result_007

IR outputs: 0: result_009

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
| 1.1 | model_observe (program-generated, statically possible) | deliver | 0: D006, D008, D010, D013 | model_context: Current model processing context | — |
| 2.1 | transform | select_part | 0: D006, D008, D010, D013 | — | 0: D007, D012, D016, D021 |

Entry/exit changes: 

- `result: result_009`: Unbound → D007, D012, D016, D021

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
          &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
          &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
          &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_009b07c5001af2da1d8acba3076888f2a7aa49ea2d80afafcc10b34e1bd1a4bd&quot;,
          &quot;data_048f3f047d3cfd508d82af1052f822b8a36daad60f870bd2320e27d348514221&quot;,
          &quot;data_bd1ba59ec1f944c468c881a67676f62b0095ddc2e9217a2e133cf178abcb2ec9&quot;,
          &quot;data_dc7b982531c6520469643cfd7a66716bad24aaa6ba24f305c1d6b60f15a4af79&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_009b07c5001af2da1d8acba3076888f2a7aa49ea2d80afafcc10b34e1bd1a4bd&quot;,
          &quot;data_048f3f047d3cfd508d82af1052f822b8a36daad60f870bd2320e27d348514221&quot;,
          &quot;data_bd1ba59ec1f944c468c881a67676f62b0095ddc2e9217a2e133cf178abcb2ec9&quot;,
          &quot;data_dc7b982531c6520469643cfd7a66716bad24aaa6ba24f305c1d6b60f15a4af79&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
          &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
          &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
          &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_009b07c5001af2da1d8acba3076888f2a7aa49ea2d80afafcc10b34e1bd1a4bd&quot;,
          &quot;data_048f3f047d3cfd508d82af1052f822b8a36daad60f870bd2320e27d348514221&quot;,
          &quot;data_bd1ba59ec1f944c468c881a67676f62b0095ddc2e9217a2e133cf178abcb2ec9&quot;,
          &quot;data_dc7b982531c6520469643cfd7a66716bad24aaa6ba24f305c1d6b60f15a4af79&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_41579c3d03f6f282e27032d6d90b1f0b803d643172579ecd01a36d619a4e97ab&quot;,
          &quot;data_65a79b1fbed9a71475acf516876593e476ab10fe2ad3c2ed599a5717e0edcfb7&quot;,
          &quot;data_a3fbf7f05105730eaa540813bac298a6a0f9e9e9c905244b323c4262bfa51eb7&quot;,
          &quot;data_ed5a774645da77bcd5c8de30cc27cf7137b52e0eb86af26412a0169bec42bcc8&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_009b07c5001af2da1d8acba3076888f2a7aa49ea2d80afafcc10b34e1bd1a4bd&quot;,
          &quot;data_048f3f047d3cfd508d82af1052f822b8a36daad60f870bd2320e27d348514221&quot;,
          &quot;data_bd1ba59ec1f944c468c881a67676f62b0095ddc2e9217a2e133cf178abcb2ec9&quot;,
          &quot;data_dc7b982531c6520469643cfd7a66716bad24aaa6ba24f305c1d6b60f15a4af79&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
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
                &quot;end_line&quot;: 23,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;This line requires returning the response items value unchanged.&quot;,
                &quot;start_line&quot;: 23
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
            &quot;end_line&quot;: 23,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;This line requires returning the response items value unchanged.&quot;,
            &quot;start_line&quot;: 23
          }
        ]
      },
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 23,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;This line identifies the response items as the value to return unchanged.&quot;,
                &quot;start_line&quot;: 23
              }
            ],
            &quot;input&quot;: {
              &quot;index&quot;: 0,
              &quot;kind&quot;: &quot;input&quot;
            },
            &quot;op&quot;: &quot;select_part&quot;,
            &quot;output&quot;: &quot;response_items&quot;,
            &quot;path&quot;: [
              &quot;items&quot;
            ]
          }
        ],
        &quot;effect&quot;: &quot;transform&quot;,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 23,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;The response items are selected unchanged from the search response.&quot;,
            &quot;start_line&quot;: 23
          }
        ]
      }
    ],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 23,
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;reason&quot;: &quot;The workflow directs the skill runtime to obtain the search response items for returning.&quot;,
        &quot;start_line&quot;: 23,
        &quot;value&quot;: &quot;agent_runtime&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 23,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;The selected response items are bound to the CFG items result.&quot;,
            &quot;start_line&quot;: 23
          }
        ],
        &quot;output_index&quot;: 0,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;response_items&quot;
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
          &quot;end_line&quot;: 23,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;The selected response items are bound to the CFG items result.&quot;,
          &quot;start_line&quot;: 23
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;response_items&quot;
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
          &quot;end_line&quot;: 23,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;This line requires returning the response items value unchanged.&quot;,
          &quot;start_line&quot;: 23
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
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 23,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;This line identifies the response items as the value to return unchanged.&quot;,
          &quot;start_line&quot;: 23
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;response_items&quot;,
      &quot;path&quot;: [
        &quot;items&quot;
      ]
    }
  ]
}</pre>

</details>

## ir_012 · return

Block: block_004; Operator: agent_runtime.

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
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
          &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
          &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
          &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_009b07c5001af2da1d8acba3076888f2a7aa49ea2d80afafcc10b34e1bd1a4bd&quot;,
          &quot;data_048f3f047d3cfd508d82af1052f822b8a36daad60f870bd2320e27d348514221&quot;,
          &quot;data_bd1ba59ec1f944c468c881a67676f62b0095ddc2e9217a2e133cf178abcb2ec9&quot;,
          &quot;data_dc7b982531c6520469643cfd7a66716bad24aaa6ba24f305c1d6b60f15a4af79&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_41579c3d03f6f282e27032d6d90b1f0b803d643172579ecd01a36d619a4e97ab&quot;,
          &quot;data_65a79b1fbed9a71475acf516876593e476ab10fe2ad3c2ed599a5717e0edcfb7&quot;,
          &quot;data_a3fbf7f05105730eaa540813bac298a6a0f9e9e9c905244b323c4262bfa51eb7&quot;,
          &quot;data_ed5a774645da77bcd5c8de30cc27cf7137b52e0eb86af26412a0169bec42bcc8&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_009b07c5001af2da1d8acba3076888f2a7aa49ea2d80afafcc10b34e1bd1a4bd&quot;,
          &quot;data_048f3f047d3cfd508d82af1052f822b8a36daad60f870bd2320e27d348514221&quot;,
          &quot;data_bd1ba59ec1f944c468c881a67676f62b0095ddc2e9217a2e133cf178abcb2ec9&quot;,
          &quot;data_dc7b982531c6520469643cfd7a66716bad24aaa6ba24f305c1d6b60f15a4af79&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_002&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_003&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_006&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
          &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
          &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
          &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_007&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_009b07c5001af2da1d8acba3076888f2a7aa49ea2d80afafcc10b34e1bd1a4bd&quot;,
          &quot;data_048f3f047d3cfd508d82af1052f822b8a36daad60f870bd2320e27d348514221&quot;,
          &quot;data_bd1ba59ec1f944c468c881a67676f62b0095ddc2e9217a2e133cf178abcb2ec9&quot;,
          &quot;data_dc7b982531c6520469643cfd7a66716bad24aaa6ba24f305c1d6b60f15a4af79&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_008&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_41579c3d03f6f282e27032d6d90b1f0b803d643172579ecd01a36d619a4e97ab&quot;,
          &quot;data_65a79b1fbed9a71475acf516876593e476ab10fe2ad3c2ed599a5717e0edcfb7&quot;,
          &quot;data_a3fbf7f05105730eaa540813bac298a6a0f9e9e9c905244b323c4262bfa51eb7&quot;,
          &quot;data_ed5a774645da77bcd5c8de30cc27cf7137b52e0eb86af26412a0169bec42bcc8&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_009&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_009b07c5001af2da1d8acba3076888f2a7aa49ea2d80afafcc10b34e1bd1a4bd&quot;,
          &quot;data_048f3f047d3cfd508d82af1052f822b8a36daad60f870bd2320e27d348514221&quot;,
          &quot;data_bd1ba59ec1f944c468c881a67676f62b0095ddc2e9217a2e133cf178abcb2ec9&quot;,
          &quot;data_dc7b982531c6520469643cfd7a66716bad24aaa6ba24f305c1d6b60f15a4af79&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;count.txt&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;request.json&quot;
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
        &quot;end_line&quot;: 23,
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;reason&quot;: &quot;The final instruction is an ordinary return of the selected items value; it has no external effect event.&quot;,
        &quot;start_line&quot;: 23
      }
    ],
    &quot;events&quot;: [],
    &quot;operator&quot;: [
      &quot;agent_runtime&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;end_line&quot;: 23,
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;reason&quot;: &quot;The workflow directs the skill runtime to return the selected response items.&quot;,
        &quot;start_line&quot;: 23,
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
| D001 | data_009b07c5001af2da1d8acba3076888f2a7aa49ea2d80afafcc10b34e1bd1a4bd | opaque |
| D002 | data_048f3f047d3cfd508d82af1052f822b8a36daad60f870bd2320e27d348514221 | opaque |
| D003 | data_0a2883229a9be18ff5d5eb083414c0b4e16345aa9fa51e195e00917d906fe248 | known_parts |
| D004 | data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf | opaque |
| D005 | data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba | opaque |
| D006 | data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690 | known_parts |
| D007 | data_41579c3d03f6f282e27032d6d90b1f0b803d643172579ecd01a36d619a4e97ab | opaque |
| D008 | data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5 | known_parts |
| D009 | data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d | opaque |
| D010 | data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850 | known_parts |
| D011 | data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1 | opaque |
| D012 | data_65a79b1fbed9a71475acf516876593e476ab10fe2ad3c2ed599a5717e0edcfb7 | opaque |
| D013 | data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1 | known_parts |
| D014 | data_6eb33a1fba325169baaeb5a263cfb1ca3f88b1ca955288acf76ebbf3d574204a | known_parts |
| D015 | data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341 | opaque |
| D016 | data_a3fbf7f05105730eaa540813bac298a6a0f9e9e9c905244b323c4262bfa51eb7 | opaque |
| D017 | data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6 | known_parts |
| D018 | data_bd1ba59ec1f944c468c881a67676f62b0095ddc2e9217a2e133cf178abcb2ec9 | opaque |
| D019 | data_d0564fb629786752de47645d70df9e2654757eed8e265baafae2fdc61d57ca77 | known_parts |
| D020 | data_dc7b982531c6520469643cfd7a66716bad24aaa6ba24f305c1d6b60f15a4af79 | opaque |
| D021 | data_ed5a774645da77bcd5c8de30cc27cf7137b52e0eb86af26412a0169bec42bcc8 | opaque |
| D022 | data_fd34f589b9e429b928ab67c129121af92307b50527970b5a8546d4982c76e0ce | known_parts |

<details><summary>D001: Complete Data content, origin and dependencies</summary>

<pre>{
  &quot;annotations&quot;: {
    &quot;description&quot;: null,
    &quot;evidences&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;content&quot;: {
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_009b07c5001af2da1d8acba3076888f2a7aa49ea2d80afafcc10b34e1bd1a4bd&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
    &quot;path&quot;: [
      &quot;total&quot;
    ]
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
  &quot;id&quot;: &quot;data_048f3f047d3cfd508d82af1052f822b8a36daad60f870bd2320e27d348514221&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
    &quot;path&quot;: [
      &quot;total&quot;
    ]
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
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;,
        &quot;path&quot;: [
          &quot;query&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: true
  },
  &quot;id&quot;: &quot;data_0a2883229a9be18ff5d5eb083414c0b4e16345aa9fa51e195e00917d906fe248&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[&#x27;ir_007&#x27;, 3, 0], &#x27;members&#x27;, [[&#x27;query&#x27;]]]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;,
      &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;,
      &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
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
  &quot;id&quot;: &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_005&#x27;, 1, 1]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
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
  &quot;id&quot;: &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[&#x27;ir_004&#x27;, 1, 1]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
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
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_bd1ba59ec1f944c468c881a67676f62b0095ddc2e9217a2e133cf178abcb2ec9&quot;,
        &quot;path&quot;: [
          &quot;total&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_ed5a774645da77bcd5c8de30cc27cf7137b52e0eb86af26412a0169bec42bcc8&quot;,
        &quot;path&quot;: [
          &quot;items&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;tool:index.search&quot;,
    &quot;at&quot;: &quot;[&#x27;ir_007&#x27;, 4, 1]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_d0564fb629786752de47645d70df9e2654757eed8e265baafae2fdc61d57ca77&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_d0564fb629786752de47645d70df9e2654757eed8e265baafae2fdc61d57ca77&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
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
  &quot;id&quot;: &quot;data_41579c3d03f6f282e27032d6d90b1f0b803d643172579ecd01a36d619a4e97ab&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
    &quot;path&quot;: [
      &quot;items&quot;
    ]
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
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_009b07c5001af2da1d8acba3076888f2a7aa49ea2d80afafcc10b34e1bd1a4bd&quot;,
        &quot;path&quot;: [
          &quot;total&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_41579c3d03f6f282e27032d6d90b1f0b803d643172579ecd01a36d619a4e97ab&quot;,
        &quot;path&quot;: [
          &quot;items&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;tool:index.search&quot;,
    &quot;at&quot;: &quot;[&#x27;ir_007&#x27;, 4, 1]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_0a2883229a9be18ff5d5eb083414c0b4e16345aa9fa51e195e00917d906fe248&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_0a2883229a9be18ff5d5eb083414c0b4e16345aa9fa51e195e00917d906fe248&quot;
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
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;,
    &quot;path&quot;: [
      &quot;term&quot;
    ]
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
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_048f3f047d3cfd508d82af1052f822b8a36daad60f870bd2320e27d348514221&quot;,
        &quot;path&quot;: [
          &quot;total&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_65a79b1fbed9a71475acf516876593e476ab10fe2ad3c2ed599a5717e0edcfb7&quot;,
        &quot;path&quot;: [
          &quot;items&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;tool:index.search&quot;,
    &quot;at&quot;: &quot;[&#x27;ir_007&#x27;, 4, 1]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_fd34f589b9e429b928ab67c129121af92307b50527970b5a8546d4982c76e0ce&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_fd34f589b9e429b928ab67c129121af92307b50527970b5a8546d4982c76e0ce&quot;
    ],
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
  &quot;id&quot;: &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;,
    &quot;path&quot;: [
      &quot;limit&quot;
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
  &quot;id&quot;: &quot;data_65a79b1fbed9a71475acf516876593e476ab10fe2ad3c2ed599a5717e0edcfb7&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
    &quot;path&quot;: [
      &quot;items&quot;
    ]
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
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_dc7b982531c6520469643cfd7a66716bad24aaa6ba24f305c1d6b60f15a4af79&quot;,
        &quot;path&quot;: [
          &quot;total&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_a3fbf7f05105730eaa540813bac298a6a0f9e9e9c905244b323c4262bfa51eb7&quot;,
        &quot;path&quot;: [
          &quot;items&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;tool:index.search&quot;,
    &quot;at&quot;: &quot;[&#x27;ir_007&#x27;, 4, 1]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_6eb33a1fba325169baaeb5a263cfb1ca3f88b1ca955288acf76ebbf3d574204a&quot;,
        &quot;relation&quot;: &quot;possible&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_6eb33a1fba325169baaeb5a263cfb1ca3f88b1ca955288acf76ebbf3d574204a&quot;
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
        &quot;data&quot;: &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;,
        &quot;path&quot;: [
          &quot;query&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;,
        &quot;path&quot;: [
          &quot;from_date&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: true
  },
  &quot;id&quot;: &quot;data_6eb33a1fba325169baaeb5a263cfb1ca3f88b1ca955288acf76ebbf3d574204a&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[&#x27;ir_007&#x27;, 3, 0], &#x27;members&#x27;, [[&#x27;query&#x27;], [&#x27;from_date&#x27;]]]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;,
      &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;,
      &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;,
      &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
    ],
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
  &quot;id&quot;: &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;,
    &quot;path&quot;: [
      &quot;from_date&quot;
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
  &quot;id&quot;: &quot;data_a3fbf7f05105730eaa540813bac298a6a0f9e9e9c905244b323c4262bfa51eb7&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;,
    &quot;path&quot;: [
      &quot;items&quot;
    ]
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
        &quot;data&quot;: &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;,
        &quot;path&quot;: [
          &quot;term&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;,
        &quot;path&quot;: [
          &quot;from_date&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;,
        &quot;path&quot;: [
          &quot;limit&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;storage:request.json&quot;,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
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
  &quot;id&quot;: &quot;data_bd1ba59ec1f944c468c881a67676f62b0095ddc2e9217a2e133cf178abcb2ec9&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
    &quot;path&quot;: [
      &quot;total&quot;
    ]
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
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;,
        &quot;path&quot;: [
          &quot;query&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;,
        &quot;path&quot;: [
          &quot;from_date&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;,
        &quot;path&quot;: [
          &quot;limit&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: true
  },
  &quot;id&quot;: &quot;data_d0564fb629786752de47645d70df9e2654757eed8e265baafae2fdc61d57ca77&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[&#x27;ir_007&#x27;, 3, 0], &#x27;members&#x27;, [[&#x27;query&#x27;], [&#x27;from_date&#x27;], [&#x27;limit&#x27;]]]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;,
      &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;,
      &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;,
      &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;,
      &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
    ],
    &quot;part_of&quot;: null,
    &quot;path&quot;: null
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
    &quot;form&quot;: &quot;opaque&quot;
  },
  &quot;id&quot;: &quot;data_dc7b982531c6520469643cfd7a66716bad24aaa6ba24f305c1d6b60f15a4af79&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;,
    &quot;path&quot;: [
      &quot;total&quot;
    ]
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
  &quot;id&quot;: &quot;data_ed5a774645da77bcd5c8de30cc27cf7137b52e0eb86af26412a0169bec42bcc8&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
    &quot;path&quot;: [
      &quot;items&quot;
    ]
  }
}</pre>

</details>

<details><summary>D022: Complete Data content, origin and dependencies</summary>

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
        &quot;data&quot;: &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;,
        &quot;path&quot;: [
          &quot;query&quot;
        ]
      },
      {
        &quot;data&quot;: &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;,
        &quot;path&quot;: [
          &quot;limit&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: true
  },
  &quot;id&quot;: &quot;data_fd34f589b9e429b928ab67c129121af92307b50527970b5a8546d4982c76e0ce&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: &quot;[[&#x27;ir_007&#x27;, 3, 0], &#x27;members&#x27;, [[&#x27;query&#x27;], [&#x27;limit&#x27;]]]&quot;,
    &quot;dependencies&quot;: [
      {
        &quot;data&quot;: &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      },
      {
        &quot;data&quot;: &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;,
        &quot;relation&quot;: &quot;derived&quot;
      }
    ],
    &quot;inputs&quot;: [
      &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;,
      &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;,
      &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;,
      &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
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
    &quot;count_file&quot;: [
      {
        &quot;end_line&quot;: 21,
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;reason&quot;: &quot;The workflow names local count.txt as the write destination.&quot;,
        &quot;start_line&quot;: 21
      }
    ],
    &quot;index_search&quot;: [
      {
        &quot;end_line&quot;: 7,
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;reason&quot;: &quot;The workflow names index.search as the interface to call.&quot;,
        &quot;start_line&quot;: 7
      }
    ],
    &quot;request_file&quot;: [
      {
        &quot;end_line&quot;: 5,
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;reason&quot;: &quot;The workflow identifies the supplied request.json as the input to read.&quot;,
        &quot;start_line&quot;: 5
      }
    ]
  },
  &quot;stats&quot;: {
    &quot;block_evaluations&quot;: 10,
    &quot;data_count&quot;: 22,
    &quot;description_revision&quot;: 11,
    &quot;record_count&quot;: 12
  }
}</pre>

</details>

<details><summary>Compilation audit: original model processing segments and program-generated location mapping</summary>

<pre>{
  &quot;compilation_map&quot;: {
    &quot;compiled_sha256&quot;: &quot;8ecd627294a7c18286fcea934a7b519ab01b07e903c96dfd3d771d4cd7fd9d88&quot;,
    &quot;compiler_version&quot;: &quot;skillflow-processing-compiler-v9&quot;,
    &quot;constraints&quot;: [
      {
        &quot;constraint_id&quot;: &quot;constraint_9009e15876bcfc82d8ad&quot;,
        &quot;raw_pointer&quot;: &quot;/realizations/1/constraints/0&quot;,
        &quot;requirement_id&quot;: &quot;R2&quot;
      },
      {
        &quot;constraint_id&quot;: &quot;constraint_35e3a6a8eec50bad5a08&quot;,
        &quot;raw_pointer&quot;: &quot;/realizations/7/constraints/0&quot;,
        &quot;requirement_id&quot;: &quot;R8&quot;
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
          &quot;ir_003&quot;,
          &quot;events&quot;,
          0
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
          1
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
          &quot;ir_004&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_004&quot;,
        &quot;kind&quot;: &quot;observation&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_004&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_004&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_004&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          2
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_004&quot;,
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
          2
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
        &quot;kind&quot;: &quot;observation&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
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
          0,
          1
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
          2
        ],
        &quot;instruction_id&quot;: &quot;ir_007&quot;,
        &quot;kind&quot;: &quot;observation&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
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
          3
        ],
        &quot;instruction_id&quot;: &quot;ir_007&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
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
          4
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
          1
        ]
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_007&quot;,
          &quot;events&quot;,
          5
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
          1
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
          &quot;ir_010&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_010&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_010&quot;,
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
        &quot;kind&quot;: &quot;observation&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
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
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_011&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ]
      }
    ],
    &quot;goals&quot;: [
      {
        &quot;goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/0&quot;,
        &quot;requirement_id&quot;: &quot;R9&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 0,
          &quot;instruction_id&quot;: &quot;ir_012&quot;,
          &quot;side&quot;: &quot;input&quot;
        }
      },
      {
        &quot;goal_id&quot;: &quot;goal_bad3975a1c33c86da8bc&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_001/events/0/events/0/atomic_ops/0/demands/0&quot;,
        &quot;requirement_id&quot;: &quot;R1&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_001&quot;,
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
        &quot;goal_id&quot;: &quot;goal_852714501b1884f87090&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/0&quot;,
        &quot;requirement_id&quot;: &quot;R4&quot;,
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
            &quot;kind&quot;: &quot;output&quot;
          }
        }
      },
      {
        &quot;goal_id&quot;: &quot;goal_da9ae22c3399787be23d&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/1&quot;,
        &quot;requirement_id&quot;: &quot;R6&quot;,
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
            &quot;kind&quot;: &quot;output&quot;
          }
        }
      },
      {
        &quot;goal_id&quot;: &quot;goal_06ba52e6366aa3d27778&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_007/events/0/events/1/atomic_ops/0/demands/0&quot;,
        &quot;requirement_id&quot;: &quot;R2&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_007&quot;,
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
        &quot;goal_id&quot;: &quot;goal_b9704dcab72933209f08&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_007/events/0/events/1/atomic_ops/0/demands/1&quot;,
        &quot;requirement_id&quot;: &quot;R2&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_007&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            1,
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
        &quot;goal_id&quot;: &quot;goal_c25263b0b7055126cef1&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_007/events/0/events/1/atomic_ops/0/demands/2&quot;,
        &quot;requirement_id&quot;: &quot;R3&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_007&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            1,
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
        &quot;goal_id&quot;: &quot;goal_99915fbe3f62e1af0426&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_007/events/0/events/1/atomic_ops/0/demands/3&quot;,
        &quot;requirement_id&quot;: &quot;R5&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_007&quot;,
          &quot;operation_path&quot;: [
            &quot;events&quot;,
            0,
            &quot;events&quot;,
            1,
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
        &quot;goal_id&quot;: &quot;goal_a68e938e61f1884d7598&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_010/events/0/events/0/atomic_ops/0/demands/0&quot;,
        &quot;requirement_id&quot;: &quot;R8&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_010&quot;,
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
        &quot;goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_010/events/0/events/0/atomic_ops/0/demands/1&quot;,
        &quot;requirement_id&quot;: &quot;R8&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_010&quot;,
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
    &quot;raw_sha256&quot;: &quot;46fce4da15bdc91579e39b020ea8353b9e069db96ca9f8e6369c5a025f22ba05&quot;,
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
        &quot;reason&quot;: &quot;Preserve the search response items value unchanged at the return input.&quot;,
        &quot;requirement_id&quot;: &quot;R9&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 0,
          &quot;instruction_id&quot;: &quot;ir_012&quot;,
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
                    &quot;demands&quot;: [
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [],
                        &quot;preserve&quot;: &quot;action&quot;,
                        &quot;reason&quot;: &quot;Preserve the required read of the supplied request.json.&quot;,
                        &quot;requirement_id&quot;: &quot;R1&quot;,
                        &quot;target&quot;: {
                          &quot;kind&quot;: &quot;self&quot;
                        }
                      }
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 5,
                        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                        &quot;reason&quot;: &quot;This line directs reading the supplied request.json.&quot;,
                        &quot;start_line&quot;: 5
                      }
                    ],
                    &quot;location&quot;: &quot;request_file&quot;,
                    &quot;op&quot;: &quot;read&quot;,
                    &quot;output&quot;: &quot;request_data&quot;
                  }
                ],
                &quot;effect&quot;: &quot;fs_read&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 5,
                    &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                    &quot;reason&quot;: &quot;Reading the supplied request file is the specified data acquisition.&quot;,
                    &quot;start_line&quot;: 5
                  }
                ]
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 5,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;This line requires reading the user-supplied request.json.&quot;,
                &quot;start_line&quot;: 5
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
            &quot;end_line&quot;: 5,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;The workflow instructs the skill runtime to read the supplied request.json; no external tool is named for this read.&quot;,
            &quot;start_line&quot;: 5,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 5,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;The requested request.json contents are bound to the CFG read result.&quot;,
                &quot;start_line&quot;: 5
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;request_data&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_002&quot;: {
        &quot;empty_effect_evidences&quot;: [
          {
            &quot;reason&quot;: &quot;This dispatch performs only CFG control transfer and has no external effect.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_002&quot;,
              &quot;path&quot;: []
            }
          }
        ],
        &quot;events&quot;: [],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;reason&quot;: &quot;The CFG dispatch is an internal workflow control step with no explicit tool or human executor.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_002&quot;,
              &quot;path&quot;: []
            },
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
                        &quot;end_line&quot;: 7,
                        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                        &quot;reason&quot;: &quot;This line identifies request.term as the query value to preserve.&quot;,
                        &quot;start_line&quot;: 7
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;query_term&quot;,
                    &quot;path&quot;: [
                      &quot;term&quot;
                    ]
                  }
                ],
                &quot;effect&quot;: &quot;transform&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 7,
                    &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                    &quot;reason&quot;: &quot;The request term is selected unchanged for the search call.&quot;,
                    &quot;start_line&quot;: 7
                  }
                ]
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 7,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;This line requires using request.term unchanged as the query argument.&quot;,
                &quot;start_line&quot;: 7
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
            &quot;end_line&quot;: 7,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;The workflow directs the skill runtime to use request.term as the search query; orchestration of that extraction is an agent-runtime step.&quot;,
            &quot;start_line&quot;: 7,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 7,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;The extracted request.term value is bound to the CFG extraction result.&quot;,
                &quot;start_line&quot;: 7
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;query_term&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_004&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 10,
                        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                        &quot;reason&quot;: &quot;This line requires passing a present from_date value unchanged.&quot;,
                        &quot;start_line&quot;: 10
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;from_date_value&quot;,
                    &quot;path&quot;: [
                      &quot;from_date&quot;
                    ]
                  },
                  {
                    &quot;dependencies&quot;: [
                      &quot;derived&quot;
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 11,
                        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                        &quot;reason&quot;: &quot;These lines distinguish a present from_date from a missing from_date.&quot;,
                        &quot;start_line&quot;: 10
                      }
                    ],
                    &quot;expression&quot;: {
                      &quot;evidences&quot;: [
                        {
                          &quot;end_line&quot;: 11,
                          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                          &quot;reason&quot;: &quot;The workflow conditions from_date use on whether that request field is present.&quot;,
                          &quot;start_line&quot;: 10
                        }
                      ],
                      &quot;expression&quot;: {
                        &quot;arg&quot;: {
                          &quot;arg&quot;: {
                            &quot;op&quot;: &quot;ref&quot;,
                            &quot;value&quot;: {
                              &quot;index&quot;: 0,
                              &quot;kind&quot;: &quot;input&quot;
                            }
                          },
                          &quot;op&quot;: &quot;field&quot;,
                          &quot;path&quot;: [
                            &quot;from_date&quot;
                          ]
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
                    &quot;output&quot;: &quot;from_date_present&quot;
                  }
                ],
                &quot;effect&quot;: &quot;transform&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 11,
                    &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                    &quot;reason&quot;: &quot;The optional from_date value and its presence are extracted for conditional construction.&quot;,
                    &quot;start_line&quot;: 10
                  }
                ]
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 11,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;These lines define presence-dependent handling of from_date.&quot;,
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
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;The workflow directs extracting and conditionally using the optional from_date field; this orchestration is performed by the skill runtime.&quot;,
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
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;A present from_date value is bound to the CFG optional-value result.&quot;,
                &quot;start_line&quot;: 10
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;from_date_value&quot;
            }
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 11,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;The presence of from_date is bound to the CFG presence result.&quot;,
                &quot;start_line&quot;: 10
              }
            ],
            &quot;output_index&quot;: 1,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;from_date_present&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_005&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 12,
                        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                        &quot;reason&quot;: &quot;This line requires passing a present limit value unchanged.&quot;,
                        &quot;start_line&quot;: 12
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;limit_value&quot;,
                    &quot;path&quot;: [
                      &quot;limit&quot;
                    ]
                  },
                  {
                    &quot;dependencies&quot;: [
                      &quot;derived&quot;
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 13,
                        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                        &quot;reason&quot;: &quot;These lines distinguish a present limit from a missing limit.&quot;,
                        &quot;start_line&quot;: 12
                      }
                    ],
                    &quot;expression&quot;: {
                      &quot;evidences&quot;: [
                        {
                          &quot;end_line&quot;: 13,
                          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                          &quot;reason&quot;: &quot;The workflow conditions limit use on whether that request field is present.&quot;,
                          &quot;start_line&quot;: 12
                        }
                      ],
                      &quot;expression&quot;: {
                        &quot;arg&quot;: {
                          &quot;arg&quot;: {
                            &quot;op&quot;: &quot;ref&quot;,
                            &quot;value&quot;: {
                              &quot;index&quot;: 0,
                              &quot;kind&quot;: &quot;input&quot;
                            }
                          },
                          &quot;op&quot;: &quot;field&quot;,
                          &quot;path&quot;: [
                            &quot;limit&quot;
                          ]
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
                    &quot;output&quot;: &quot;limit_present&quot;
                  }
                ],
                &quot;effect&quot;: &quot;transform&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 13,
                    &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                    &quot;reason&quot;: &quot;The optional limit value and its presence are extracted for conditional construction.&quot;,
                    &quot;start_line&quot;: 12
                  }
                ]
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 13,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;These lines define presence-dependent handling of limit.&quot;,
                &quot;start_line&quot;: 12
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
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;The workflow directs extracting and conditionally using the optional limit field; this orchestration is performed by the skill runtime.&quot;,
            &quot;start_line&quot;: 12,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 12,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;A present limit value is bound to the CFG optional-value result.&quot;,
                &quot;start_line&quot;: 12
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;limit_value&quot;
            }
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 13,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;The presence of limit is bound to the CFG presence result.&quot;,
                &quot;start_line&quot;: 12
              }
            ],
            &quot;output_index&quot;: 1,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;limit_present&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_006&quot;: {
        &quot;empty_effect_evidences&quot;: [
          {
            &quot;reason&quot;: &quot;This dispatch performs only CFG control transfer and has no external effect.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_006&quot;,
              &quot;path&quot;: []
            }
          }
        ],
        &quot;events&quot;: [],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;reason&quot;: &quot;The CFG dispatch is an internal workflow control step with no explicit tool or human executor.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_006&quot;,
              &quot;path&quot;: []
            },
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_007&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;container&quot;: &quot;object&quot;,
                    &quot;demands&quot;: [
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [
                          &quot;from_date&quot;
                        ],
                        &quot;preserve&quot;: &quot;presence&quot;,
                        &quot;reason&quot;: &quot;The built search request conditionally includes from_date only when the request field is present, so a missing from_date omits this member and applies query.yaml&#x27;s omit setting to the same call.&quot;,
                        &quot;requirement_id&quot;: &quot;R4&quot;,
                        &quot;target&quot;: {
                          &quot;kind&quot;: &quot;output&quot;
                        }
                      },
                      {
                        &quot;expected&quot;: null,
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [
                          &quot;limit&quot;
                        ],
                        &quot;preserve&quot;: &quot;presence&quot;,
                        &quot;reason&quot;: &quot;The built search request conditionally includes limit only when the request field is present, so a missing limit omits this member and applies query.yaml&#x27;s omit setting to the same call.&quot;,
                        &quot;requirement_id&quot;: &quot;R6&quot;,
                        &quot;target&quot;: {
                          &quot;kind&quot;: &quot;output&quot;
                        }
                      }
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 7,
                        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                        &quot;reason&quot;: &quot;The query argument uses request.term unchanged.&quot;,
                        &quot;start_line&quot;: 7
                      },
                      {
                        &quot;end_line&quot;: 13,
                        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                        &quot;reason&quot;: &quot;These lines specify inclusion and omission of the optional arguments based on presence.&quot;,
                        &quot;start_line&quot;: 10
                      },
                      {
                        &quot;end_line&quot;: 3,
                        &quot;file&quot;: &quot;skill/query.yaml&quot;,
                        &quot;reason&quot;: &quot;The configuration sets missing from_date and limit arguments to omit.&quot;,
                        &quot;start_line&quot;: 2
                      }
                    ],
                    &quot;op&quot;: &quot;build&quot;,
                    &quot;output&quot;: &quot;search_request&quot;,
                    &quot;parts&quot;: [
                      {
                        &quot;path&quot;: [
                          &quot;query&quot;
                        ],
                        &quot;value&quot;: {
                          &quot;index&quot;: 1,
                          &quot;kind&quot;: &quot;input&quot;
                        },
                        &quot;when&quot;: null
                      },
                      {
                        &quot;path&quot;: [
                          &quot;from_date&quot;
                        ],
                        &quot;value&quot;: {
                          &quot;index&quot;: 2,
                          &quot;kind&quot;: &quot;input&quot;
                        },
                        &quot;when&quot;: {
                          &quot;index&quot;: 3,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      },
                      {
                        &quot;path&quot;: [
                          &quot;limit&quot;
                        ],
                        &quot;value&quot;: {
                          &quot;index&quot;: 4,
                          &quot;kind&quot;: &quot;input&quot;
                        },
                        &quot;when&quot;: {
                          &quot;index&quot;: 5,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      }
                    ]
                  }
                ],
                &quot;effect&quot;: &quot;transform&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 15,
                    &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                    &quot;reason&quot;: &quot;The workflow specifies the query argument and conditional from_date and limit members for the same call.&quot;,
                    &quot;start_line&quot;: 7
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
                        &quot;preserve&quot;: &quot;action&quot;,
                        &quot;reason&quot;: &quot;Preserve the single index.search invocation; together with the at-most constraint this covers the exactly-once requirement.&quot;,
                        &quot;requirement_id&quot;: &quot;R2&quot;,
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
                        &quot;path&quot;: [
                          &quot;query&quot;
                        ],
                        &quot;preserve&quot;: &quot;value&quot;,
                        &quot;reason&quot;: &quot;Preserve request.term unchanged as the query argument.&quot;,
                        &quot;requirement_id&quot;: &quot;R2&quot;,
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
                        &quot;path&quot;: [
                          &quot;from_date&quot;
                        ],
                        &quot;preserve&quot;: &quot;value&quot;,
                        &quot;reason&quot;: &quot;When from_date is present, preserve its value unchanged in the from_date argument.&quot;,
                        &quot;requirement_id&quot;: &quot;R3&quot;,
                        &quot;target&quot;: {
                          &quot;index&quot;: 0,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      },
                      {
                        &quot;expected&quot;: {
                          &quot;index&quot;: 4,
                          &quot;kind&quot;: &quot;input&quot;
                        },
                        &quot;expected_path&quot;: [],
                        &quot;path&quot;: [
                          &quot;limit&quot;
                        ],
                        &quot;preserve&quot;: &quot;value&quot;,
                        &quot;reason&quot;: &quot;When limit is present, preserve its value unchanged in the limit argument.&quot;,
                        &quot;requirement_id&quot;: &quot;R5&quot;,
                        &quot;target&quot;: {
                          &quot;index&quot;: 0,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      }
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 7,
                        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                        &quot;reason&quot;: &quot;The workflow requires calling index.search.&quot;,
                        &quot;start_line&quot;: 7
                      },
                      {
                        &quot;end_line&quot;: 13,
                        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                        &quot;reason&quot;: &quot;These lines define the argument content and conditional inclusion requirements for that call.&quot;,
                        &quot;start_line&quot;: 10
                      },
                      {
                        &quot;end_line&quot;: 15,
                        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                        &quot;reason&quot;: &quot;The missing-argument settings apply to this same call.&quot;,
                        &quot;start_line&quot;: 15
                      }
                    ],
                    &quot;inputs&quot;: [
                      {
                        &quot;kind&quot;: &quot;local&quot;,
                        &quot;name&quot;: &quot;search_request&quot;
                      }
                    ],
                    &quot;op&quot;: &quot;deliver&quot;,
                    &quot;target&quot;: &quot;index_search&quot;
                  },
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 7,
                        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                        &quot;reason&quot;: &quot;The same index.search call yields the search response used by later steps.&quot;,
                        &quot;start_line&quot;: 7
                      }
                    ],
                    &quot;inputs&quot;: [
                      {
                        &quot;kind&quot;: &quot;local&quot;,
                        &quot;name&quot;: &quot;search_request&quot;
                      }
                    ],
                    &quot;location&quot;: &quot;index_search&quot;,
                    &quot;op&quot;: &quot;receive&quot;,
                    &quot;output&quot;: &quot;search_response&quot;
                  }
                ],
                &quot;effect&quot;: null
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 7,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;This line requires one index.search call with the request term and optional arguments.&quot;,
                &quot;start_line&quot;: 7
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;default&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;,
          &quot;tool&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;end_line&quot;: 7,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;The workflow directs the skill runtime to construct the index.search arguments from the request fields.&quot;,
            &quot;start_line&quot;: 7,
            &quot;value&quot;: &quot;agent_runtime&quot;
          },
          {
            &quot;reason&quot;: &quot;The CFG records index.search as an external_resource argument, independently evidencing a tool interface.&quot;,
            &quot;target&quot;: {
              &quot;index&quot;: 0,
              &quot;instruction_id&quot;: &quot;ir_007&quot;,
              &quot;side&quot;: &quot;input&quot;
            },
            &quot;value&quot;: &quot;tool&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 7,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;The search response is the output of the single index.search call.&quot;,
                &quot;start_line&quot;: 7
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;search_response&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_008&quot;: {
        &quot;empty_effect_evidences&quot;: [
          {
            &quot;reason&quot;: &quot;This dispatch performs only CFG control transfer and has no external effect.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_008&quot;,
              &quot;path&quot;: []
            }
          }
        ],
        &quot;events&quot;: [],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;reason&quot;: &quot;The CFG dispatch is an internal workflow control step with no explicit tool or human executor.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_008&quot;,
              &quot;path&quot;: []
            },
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
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 21,
                        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                        &quot;reason&quot;: &quot;This line identifies the response total as the value to write.&quot;,
                        &quot;start_line&quot;: 21
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;response_total&quot;,
                    &quot;path&quot;: [
                      &quot;total&quot;
                    ]
                  }
                ],
                &quot;effect&quot;: &quot;transform&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 21,
                    &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                    &quot;reason&quot;: &quot;The response total is selected from the search response for writing.&quot;,
                    &quot;start_line&quot;: 21
                  }
                ]
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 21,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;This line requires using the response total after the search.&quot;,
                &quot;start_line&quot;: 21
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
            &quot;end_line&quot;: 21,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;The workflow directs the skill runtime to obtain the search response total for the local file write.&quot;,
            &quot;start_line&quot;: 21,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 21,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;The selected response total is bound to the CFG total result.&quot;,
                &quot;start_line&quot;: 21
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;response_total&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_010&quot;: {
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
                        &quot;reason&quot;: &quot;Preserve the required write to local count.txt.&quot;,
                        &quot;requirement_id&quot;: &quot;R8&quot;,
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
                        &quot;reason&quot;: &quot;The write payload must be the response total value from the CFG total result.&quot;,
                        &quot;requirement_id&quot;: &quot;R8&quot;,
                        &quot;target&quot;: {
                          &quot;index&quot;: 0,
                          &quot;kind&quot;: &quot;input&quot;
                        }
                      }
                    ],
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 21,
                        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                        &quot;reason&quot;: &quot;This line requires writing the response total to local count.txt.&quot;,
                        &quot;start_line&quot;: 21
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 1,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;mode&quot;: &quot;replace&quot;,
                    &quot;op&quot;: &quot;write&quot;,
                    &quot;target&quot;: &quot;count_file&quot;
                  }
                ],
                &quot;effect&quot;: &quot;fs_write&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 21,
                    &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                    &quot;reason&quot;: &quot;Writing to the local count.txt file is the specified file effect.&quot;,
                    &quot;start_line&quot;: 21
                  }
                ]
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 21,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;This line requires writing the search response total to local count.txt after the search.&quot;,
                &quot;start_line&quot;: 21
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
            &quot;end_line&quot;: 21,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;The workflow directs the skill runtime to write the local count.txt file.&quot;,
            &quot;start_line&quot;: 21,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_011&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 23,
                        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                        &quot;reason&quot;: &quot;This line identifies the response items as the value to return unchanged.&quot;,
                        &quot;start_line&quot;: 23
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;response_items&quot;,
                    &quot;path&quot;: [
                      &quot;items&quot;
                    ]
                  }
                ],
                &quot;effect&quot;: &quot;transform&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 23,
                    &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                    &quot;reason&quot;: &quot;The response items are selected unchanged from the search response.&quot;,
                    &quot;start_line&quot;: 23
                  }
                ]
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 23,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;This line requires returning the response items value unchanged.&quot;,
                &quot;start_line&quot;: 23
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
            &quot;end_line&quot;: 23,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;The workflow directs the skill runtime to obtain the search response items for returning.&quot;,
            &quot;start_line&quot;: 23,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 23,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;The selected response items are bound to the CFG items result.&quot;,
                &quot;start_line&quot;: 23
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;response_items&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_012&quot;: {
        &quot;empty_effect_evidences&quot;: [
          {
            &quot;end_line&quot;: 23,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;The final instruction is an ordinary return of the selected items value; it has no external effect event.&quot;,
            &quot;start_line&quot;: 23
          }
        ],
        &quot;events&quot;: [],
        &quot;operator&quot;: [
          &quot;agent_runtime&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;end_line&quot;: 23,
            &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
            &quot;reason&quot;: &quot;The workflow directs the skill runtime to return the selected response items.&quot;,
            &quot;start_line&quot;: 23,
            &quot;value&quot;: &quot;agent_runtime&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      }
    },
    &quot;location_evidences&quot;: {
      &quot;count_file&quot;: [
        {
          &quot;end_line&quot;: 21,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;The workflow names local count.txt as the write destination.&quot;,
          &quot;start_line&quot;: 21
        }
      ],
      &quot;index_search&quot;: [
        {
          &quot;end_line&quot;: 7,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;The workflow names index.search as the interface to call.&quot;,
          &quot;start_line&quot;: 7
        }
      ],
      &quot;request_file&quot;: [
        {
          &quot;end_line&quot;: 5,
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;reason&quot;: &quot;The workflow identifies the supplied request.json as the input to read.&quot;,
          &quot;start_line&quot;: 5
        }
      ]
    },
    &quot;locations&quot;: {
      &quot;count_file&quot;: {
        &quot;access_scope&quot;: &quot;task&quot;,
        &quot;kind&quot;: &quot;storage&quot;,
        &quot;name&quot;: &quot;count.txt&quot;,
        &quot;operand_refs&quot;: [
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_010&quot;,
            &quot;side&quot;: &quot;input&quot;
          }
        ],
        &quot;retention&quot;: &quot;persistent&quot;
      },
      &quot;index_search&quot;: {
        &quot;access_scope&quot;: &quot;recipient&quot;,
        &quot;kind&quot;: &quot;tool&quot;,
        &quot;name&quot;: &quot;index.search&quot;,
        &quot;operand_refs&quot;: [
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_007&quot;,
            &quot;side&quot;: &quot;input&quot;
          }
        ],
        &quot;retention&quot;: null
      },
      &quot;request_file&quot;: {
        &quot;access_scope&quot;: &quot;task&quot;,
        &quot;kind&quot;: &quot;storage&quot;,
        &quot;name&quot;: &quot;request.json&quot;,
        &quot;operand_refs&quot;: [
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_001&quot;,
            &quot;side&quot;: &quot;input&quot;
          }
        ],
        &quot;retention&quot;: &quot;persistent&quot;
      }
    },
    &quot;outcome&quot;: &quot;completed&quot;,
    &quot;realizations&quot;: [
      {
        &quot;bindings&quot;: [
          {
            &quot;reason&quot;: &quot;The read_request_json instruction acquires the supplied request.json; term, from_date, and limit are subsequently extracted from that request by the CFG.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_001&quot;,
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
            &quot;reason&quot;: &quot;The request.term value is selected unchanged from the supplied request for the search call.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_003&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;The CFG has a single index.search instruction; its build and deliver operations pass the selected term and optional arguments, and the at-most constraint caps the call count at one.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_007&quot;,
              &quot;path&quot;: []
            }
          }
        ],
        &quot;constraints&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_007&quot;,
                &quot;path&quot;: []
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
        &quot;requirement_id&quot;: &quot;R2&quot;,
        &quot;status&quot;: &quot;expressed&quot;
      },
      {
        &quot;bindings&quot;: [
          {
            &quot;reason&quot;: &quot;The optional from_date value is selected from the request and its presence is computed separately.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_004&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;The search request from_date member uses the selected value unchanged when the presence flag is true.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_007&quot;,
              &quot;path&quot;: []
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
            &quot;reason&quot;: &quot;The build member for from_date has a when control tied to from_date presence, so a missing from_date omits the member and applies the omit setting in query.yaml to this same call.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_007&quot;,
              &quot;path&quot;: []
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
            &quot;reason&quot;: &quot;The optional limit value is selected from the request and its presence is computed separately.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_005&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;The search request limit member uses the selected value unchanged when the presence flag is true.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_007&quot;,
              &quot;path&quot;: []
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
            &quot;reason&quot;: &quot;The build member for limit has a when control tied to limit presence, so a missing limit omits the member and applies the omit setting in query.yaml to this same call.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_007&quot;,
              &quot;path&quot;: []
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
            &quot;reason&quot;: &quot;The supplied CFG retains the exact prohibition against invoking index.delete as a graph-level constraint, but there is no index.delete instruction or operation event to target with an executable typed constraint.&quot;,
            &quot;target&quot;: {
              &quot;path&quot;: [
                &quot;constraints&quot;,
                1
              ]
            }
          }
        ],
        &quot;gaps&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 17,
                &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
                &quot;reason&quot;: &quot;This line explicitly prohibits invoking index.delete anywhere in the workflow.&quot;,
                &quot;start_line&quot;: 17
              }
            ],
            &quot;reason&quot;: &quot;The workflow prohibits invoking index.delete anywhere. No index.delete operation exists in the CFG, and the available realization constraint forms cannot attach an arbitrary action prohibition to a non-existent event; the restriction is therefore retained rather than declared as an executable constraint.&quot;
          }
        ],
        &quot;requirement_id&quot;: &quot;R7&quot;,
        &quot;status&quot;: &quot;retained_only&quot;
      },
      {
        &quot;bindings&quot;: [
          {
            &quot;reason&quot;: &quot;The response total is selected from the search response before the write.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_009&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;The local count.txt write consumes the extracted response total, and the requires-prior constraint preserves the after-search order.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_010&quot;,
              &quot;path&quot;: []
            }
          }
        ],
        &quot;constraints&quot;: [
          {
            &quot;after&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_010&quot;,
                &quot;path&quot;: []
              }
            ],
            &quot;before&quot;: [
              {
                &quot;instruction_id&quot;: &quot;ir_007&quot;,
                &quot;path&quot;: []
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
        &quot;requirement_id&quot;: &quot;R8&quot;,
        &quot;status&quot;: &quot;expressed&quot;
      },
      {
        &quot;bindings&quot;: [
          {
            &quot;reason&quot;: &quot;The response items are selected unchanged from the search response.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_011&quot;,
              &quot;path&quot;: []
            }
          },
          {
            &quot;reason&quot;: &quot;The CFG return instruction returns the selected response items input.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_012&quot;,
              &quot;path&quot;: []
            }
          }
        ],
        &quot;gaps&quot;: [],
        &quot;requirement_id&quot;: &quot;R9&quot;,
        &quot;status&quot;: &quot;expressed&quot;
      }
    ],
    &quot;task_revision_id&quot;: &quot;b7d5394817bf20305abb5bd7a18bf975e5bf784a93eea05091a51969895675cb&quot;
  }
}</pre>

</details>

