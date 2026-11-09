# Basic data propagation records

**These records describe static possible behavior under the shared abstract runtime contract, not execution logs. complete means only that solving finished under the contract, not that the model actually observed this content. Default observations and explicit exceptions jointly constrain analysis. Fixed ordering or absence of a contract citation does not establish an observed runtime fact.**

Shared contract: `skillflow-abstract-runtime-v8`; SHA-256: `e2c37499e5d575975c528bd8f30169616eeb98a41e85dae7b2e8a9b7e34a49a6`.

Solver status: `incomplete`.

IR record coverage: 5 / 8.

[Local visual review](report.html) · [Data](../data.json) · [Operation records](../records.json) · [Sink list](../sinks.json)

D labels are report-local short names. Input/output indexes refer to atomic-operation arguments, not original IR operands. Control slots determine inclusion or observation and are not delivered payload. Candidate sets do not imply simultaneous occurrence; possible does not imply complete plaintext inclusion. This stage makes no risk, necessity or DOE judgment. Read scope, model observation, explicit selection and actual arguments are reviewed separately; a tool boundary does not imply networking.

[Frozen runtime contract text](../../source/inputs/runtime-contract.json) (runtime_contract); Expand the audit section below for individual evidence.

## Receiving and storage boundaries

Included positions: 1 operation positions; per-element candidate groups show arguments separately, using existing scope coordinates.

Levels describe boundary properties only: 0 task-local temporary, 1 task-local persistent, 2 another principal/shared, 3 public. They do not measure sensitivity, necessity or final risk. Coverage identifies unevaluated operations; empty arguments do not establish absence of unmodeled content.

| IR / step | Included | Type / level | Target, access / retention | Actual arguments by slot | Rationale and property evidence |
|---|---|---|---|---|---|
| ir_007 / 1.1 | Included | model_observe / 2 | __compiled_model_context__ · model_context: Current model processing context · recipient / Retention period not modeled | 0: D003 | Another recipient or cross-principal sharing; EM10, EM12 |

<details><summary>Complete source</summary>

<pre>{
  &quot;files&quot;: [
    {
      &quot;content&quot;: &quot;# Scoped static fixture\nRead the local configuration.\nOne branch updates cache with an unsupported mechanism, then reads and publishes cache.\nAn independent branch asks a model for the document body and returns that body.\nConfiguration and cache token fields are confidential.\n&quot;,
      &quot;path&quot;: &quot;SKILL.md&quot;,
      &quot;sha256&quot;: &quot;462dc62b0996f43be32b20f9826e3f212ffea50ba0c11d79d90dd5f008e1eec2&quot;
    }
  ],
  &quot;source_sha256&quot;: &quot;3cc30e5168980680b741e66a0cf8c3c550e1add1d94ed8fb0486e5c4df99488c&quot;
}</pre>

</details>

<details><summary>Coverage and diagnostics</summary>

<pre>{
  &quot;boundary_coverage&quot;: [
    {
      &quot;boundary&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;exposure_level&quot;: 2,
        &quot;instruction_id&quot;: &quot;ir_005&quot;,
        &quot;op_index&quot;: 0,
        &quot;scope&quot;: null,
        &quot;sink_type&quot;: &quot;user_output&quot;,
        &quot;target&quot;: &quot;user&quot;
      },
      &quot;reason&quot;: &quot;No evaluated instruction record resolves this declared boundary; this is not an empty or safe payload.&quot;,
      &quot;status&quot;: &quot;unresolved&quot;
    },
    {
      &quot;boundary&quot;: {
        &quot;body_event_index&quot;: null,
        &quot;event_index&quot;: 0,
        &quot;exposure_level&quot;: 2,
        &quot;instruction_id&quot;: &quot;ir_007&quot;,
        &quot;op_index&quot;: 0,
        &quot;scope&quot;: null,
        &quot;sink_type&quot;: &quot;model_observe&quot;,
        &quot;target&quot;: &quot;__compiled_model_context__&quot;
      },
      &quot;reason&quot;: &quot;An actual static operation record resolves this boundary.&quot;,
      &quot;status&quot;: &quot;resolved&quot;
    }
  ],
  &quot;coverage&quot;: {
    &quot;ir_001&quot;: &quot;processed&quot;,
    &quot;ir_002&quot;: &quot;processed&quot;,
    &quot;ir_003&quot;: &quot;unmodeled&quot;,
    &quot;ir_004&quot;: &quot;blocked&quot;,
    &quot;ir_005&quot;: &quot;blocked&quot;,
    &quot;ir_006&quot;: &quot;processed&quot;,
    &quot;ir_007&quot;: &quot;processed&quot;,
    &quot;ir_008&quot;: &quot;processed&quot;
  },
  &quot;diagnostics&quot;: [
    {
      &quot;code&quot;: &quot;unmodeled_processing&quot;,
      &quot;instruction_id&quot;: &quot;ir_003&quot;,
      &quot;reason&quot;: &quot;Explicitly unmodeled processing stops this block before evaluation and OUT publication; prior records remain available.&quot;
    }
  ],
  &quot;processing_gaps&quot;: [
    {
      &quot;control&quot;: false,
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 3,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The synthetic source explicitly identifies the cache branch and its stated mechanism.&quot;,
          &quot;start_line&quot;: 3
        }
      ],
      &quot;instruction_id&quot;: &quot;ir_003&quot;,
      &quot;locations&quot;: [
        &quot;cache&quot;
      ],
      &quot;origin&quot;: &quot;source&quot;,
      &quot;outputs&quot;: [
        0
      ],
      &quot;reason&quot;: &quot;The source mechanism has an unsupported relation.&quot;,
      &quot;unmodeled&quot;: true,
      &quot;validation_errors&quot;: []
    }
  ]
}</pre>

</details>

## ir_001 · read_local_config

Block: block_001; Operator: unknown.

IR inputs: 0: config.json

IR outputs: 0: result_001

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| 1.1 | fs_read | read | — | storage: ir_read_boundary_0 | 0: D002 |

Entry/exit changes: 

- `result: result_001`: Unbound → D002

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_ae5eae31c3d0f6200b629e6b46224378b4415565ba6e7e0dddc32c4a30c5fc45&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;cache&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6da41c6c56e4ba57e2dc42f4afc22ec7a9c5aa3ac7d45c9e2b0010f47d3c09c5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;ir_read_boundary_0&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_6da41c6c56e4ba57e2dc42f4afc22ec7a9c5aa3ac7d45c9e2b0010f47d3c09c5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ae5eae31c3d0f6200b629e6b46224378b4415565ba6e7e0dddc32c4a30c5fc45&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;cache&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6da41c6c56e4ba57e2dc42f4afc22ec7a9c5aa3ac7d45c9e2b0010f47d3c09c5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;ir_read_boundary_0&quot;
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
                &quot;reason&quot;: &quot;Explicit engineering fixture; location validity is not semantic proof.&quot;,
                &quot;target&quot;: {
                  &quot;instruction_id&quot;: &quot;ir_001&quot;,
                  &quot;path&quot;: []
                }
              }
            ],
            &quot;location&quot;: &quot;ir_read_boundary_0&quot;,
            &quot;op&quot;: &quot;read&quot;,
            &quot;output&quot;: &quot;stage_0&quot;
          }
        ],
        &quot;effect&quot;: &quot;fs_read&quot;,
        &quot;evidences&quot;: [
          {
            &quot;reason&quot;: &quot;Explicit engineering fixture; location validity is not semantic proof.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_001&quot;,
              &quot;path&quot;: []
            }
          }
        ]
      }
    ],
    &quot;operator&quot;: null,
    &quot;operator_evidences&quot;: [],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [
      {
        &quot;evidences&quot;: [
          {
            &quot;reason&quot;: &quot;Explicit engineering fixture; location validity is not semantic proof.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_001&quot;,
              &quot;path&quot;: []
            }
          }
        ],
        &quot;output_index&quot;: 0,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;stage_0&quot;
        }
      }
    ],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;reason&quot;: &quot;Explicit engineering fixture; location validity is not semantic proof.&quot;,
          &quot;target&quot;: {
            &quot;instruction_id&quot;: &quot;ir_001&quot;,
            &quot;path&quot;: []
          }
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;stage_0&quot;
      }
    }
  ],
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;reason&quot;: &quot;Explicit engineering fixture; location validity is not semantic proof.&quot;,
          &quot;target&quot;: {
            &quot;instruction_id&quot;: &quot;ir_001&quot;,
            &quot;path&quot;: []
          }
        }
      ],
      &quot;location&quot;: &quot;ir_read_boundary_0&quot;,
      &quot;op&quot;: &quot;read&quot;,
      &quot;output&quot;: &quot;stage_0&quot;
    }
  ]
}</pre>

</details>

## ir_002 · dispatch

Block: block_001; Operator: unknown.

IR inputs: 0: true

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
          &quot;data_6da41c6c56e4ba57e2dc42f4afc22ec7a9c5aa3ac7d45c9e2b0010f47d3c09c5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ae5eae31c3d0f6200b629e6b46224378b4415565ba6e7e0dddc32c4a30c5fc45&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;cache&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6da41c6c56e4ba57e2dc42f4afc22ec7a9c5aa3ac7d45c9e2b0010f47d3c09c5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;ir_read_boundary_0&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_6da41c6c56e4ba57e2dc42f4afc22ec7a9c5aa3ac7d45c9e2b0010f47d3c09c5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ae5eae31c3d0f6200b629e6b46224378b4415565ba6e7e0dddc32c4a30c5fc45&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;cache&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6da41c6c56e4ba57e2dc42f4afc22ec7a9c5aa3ac7d45c9e2b0010f47d3c09c5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;ir_read_boundary_0&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [],
    &quot;operator&quot;: null,
    &quot;operator_evidences&quot;: [],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [],
  &quot;steps&quot;: []
}</pre>

</details>

## ir_006 · operation

Block: block_003; Operator: unknown.

IR inputs: []

IR outputs: 0: result_004

<details><summary>Order and required precedence</summary>

<pre>{
  &quot;order&quot;: &quot;fixed&quot;,
  &quot;precedence&quot;: []
}</pre>

</details>

| Position | Effect | op | Actual input Data | Interaction boundary | Output or state change |
|---|---|---|---|---|---|
| 1.1 | context_read | read | — | runtime_context: cache | 0: D003 |

Entry/exit changes: 

- `result: result_004`: Unbound → D003

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_6da41c6c56e4ba57e2dc42f4afc22ec7a9c5aa3ac7d45c9e2b0010f47d3c09c5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ae5eae31c3d0f6200b629e6b46224378b4415565ba6e7e0dddc32c4a30c5fc45&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;cache&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6da41c6c56e4ba57e2dc42f4afc22ec7a9c5aa3ac7d45c9e2b0010f47d3c09c5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;ir_read_boundary_0&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_6da41c6c56e4ba57e2dc42f4afc22ec7a9c5aa3ac7d45c9e2b0010f47d3c09c5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ae5eae31c3d0f6200b629e6b46224378b4415565ba6e7e0dddc32c4a30c5fc45&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ae5eae31c3d0f6200b629e6b46224378b4415565ba6e7e0dddc32c4a30c5fc45&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;cache&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6da41c6c56e4ba57e2dc42f4afc22ec7a9c5aa3ac7d45c9e2b0010f47d3c09c5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;ir_read_boundary_0&quot;
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
                &quot;end_line&quot;: 4,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The fixture declares the read or delivery explicitly.&quot;,
                &quot;start_line&quot;: 3
              }
            ],
            &quot;location&quot;: &quot;cache&quot;,
            &quot;op&quot;: &quot;read&quot;,
            &quot;output&quot;: &quot;cached&quot;
          }
        ],
        &quot;effect&quot;: &quot;context_read&quot;,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 4,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The fixture declares the read or delivery explicitly.&quot;,
            &quot;start_line&quot;: 3
          }
        ]
      }
    ],
    &quot;operator&quot;: null,
    &quot;operator_evidences&quot;: [],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 4,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The source requires the independent document body.&quot;,
            &quot;start_line&quot;: 4
          }
        ],
        &quot;output_index&quot;: 0,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;cached&quot;
        }
      }
    ],
    &quot;precedence&quot;: [],
    &quot;sensitivity&quot;: []
  },
  &quot;output_bindings&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 4,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The source requires the independent document body.&quot;,
          &quot;start_line&quot;: 4
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;cached&quot;
      }
    }
  ],
  &quot;steps&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;end_line&quot;: 4,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The fixture declares the read or delivery explicitly.&quot;,
          &quot;start_line&quot;: 3
        }
      ],
      &quot;location&quot;: &quot;cache&quot;,
      &quot;op&quot;: &quot;read&quot;,
      &quot;output&quot;: &quot;cached&quot;
    }
  ]
}</pre>

</details>

## ir_007 · select_fields_locally

Block: block_003; Operator: llm.

IR inputs: 0: result_004

IR outputs: 0: result_005

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
| 1.1 | model_observe (program-generated, statically possible) | deliver | 0: D003 | model_context: Current model processing context | — |
| 2.1 | transform | select_part | 0: D003 | — | 0: D001 |

Entry/exit changes: 

- `result: result_005`: Unbound → D001

<details><summary>Complete entry and exit states</summary>

<pre>{
  &quot;entry_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_6da41c6c56e4ba57e2dc42f4afc22ec7a9c5aa3ac7d45c9e2b0010f47d3c09c5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ae5eae31c3d0f6200b629e6b46224378b4415565ba6e7e0dddc32c4a30c5fc45&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ae5eae31c3d0f6200b629e6b46224378b4415565ba6e7e0dddc32c4a30c5fc45&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;cache&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6da41c6c56e4ba57e2dc42f4afc22ec7a9c5aa3ac7d45c9e2b0010f47d3c09c5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;ir_read_boundary_0&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_6da41c6c56e4ba57e2dc42f4afc22ec7a9c5aa3ac7d45c9e2b0010f47d3c09c5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ae5eae31c3d0f6200b629e6b46224378b4415565ba6e7e0dddc32c4a30c5fc45&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3fec0f3299fed759b1dc13e92a9e50368b182da92d8c4cacfe365c010ae0a9b6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ae5eae31c3d0f6200b629e6b46224378b4415565ba6e7e0dddc32c4a30c5fc45&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;cache&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6da41c6c56e4ba57e2dc42f4afc22ec7a9c5aa3ac7d45c9e2b0010f47d3c09c5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;ir_read_boundary_0&quot;
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
                &quot;reason&quot;: &quot;Explicit engineering fixture; location validity is not semantic proof.&quot;,
                &quot;target&quot;: {
                  &quot;instruction_id&quot;: &quot;ir_007&quot;,
                  &quot;path&quot;: []
                }
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
            &quot;reason&quot;: &quot;Explicit engineering fixture; location validity is not semantic proof.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_007&quot;,
              &quot;path&quot;: []
            }
          }
        ]
      },
      {
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 4,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The source requires the independent document body.&quot;,
                &quot;start_line&quot;: 4
              }
            ],
            &quot;input&quot;: {
              &quot;index&quot;: 0,
              &quot;kind&quot;: &quot;input&quot;
            },
            &quot;op&quot;: &quot;select_part&quot;,
            &quot;output&quot;: &quot;body&quot;,
            &quot;path&quot;: [
              &quot;body&quot;
            ]
          }
        ],
        &quot;effect&quot;: &quot;transform&quot;,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 4,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The source requires the independent document body.&quot;,
            &quot;start_line&quot;: 4
          }
        ]
      }
    ],
    &quot;operator&quot;: [
      &quot;llm&quot;
    ],
    &quot;operator_evidences&quot;: [
      {
        &quot;reason&quot;: &quot;Explicit engineering fixture; location validity is not semantic proof.&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_007&quot;,
          &quot;path&quot;: []
        },
        &quot;value&quot;: &quot;llm&quot;
      }
    ],
    &quot;order&quot;: &quot;fixed&quot;,
    &quot;output_bindings&quot;: [
      {
        &quot;evidences&quot;: [
          {
            &quot;reason&quot;: &quot;Explicit engineering fixture; location validity is not semantic proof.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_007&quot;,
              &quot;path&quot;: []
            }
          }
        ],
        &quot;output_index&quot;: 0,
        &quot;value&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;body&quot;
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
    &quot;sensitivity&quot;: [
      {
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 5,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The source declares token confidentiality.&quot;,
            &quot;start_line&quot;: 5
          }
        ],
        &quot;label&quot;: &quot;credential&quot;,
        &quot;path&quot;: [
          &quot;token&quot;
        ],
        &quot;property&quot;: &quot;value&quot;,
        &quot;value&quot;: {
          &quot;index&quot;: 0,
          &quot;kind&quot;: &quot;input&quot;
        }
      }
    ]
  },
  &quot;output_bindings&quot;: [
    {
      &quot;evidences&quot;: [
        {
          &quot;reason&quot;: &quot;Explicit engineering fixture; location validity is not semantic proof.&quot;,
          &quot;target&quot;: {
            &quot;instruction_id&quot;: &quot;ir_007&quot;,
            &quot;path&quot;: []
          }
        }
      ],
      &quot;output_index&quot;: 0,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;body&quot;
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
          &quot;reason&quot;: &quot;Explicit engineering fixture; location validity is not semantic proof.&quot;,
          &quot;target&quot;: {
            &quot;instruction_id&quot;: &quot;ir_007&quot;,
            &quot;path&quot;: []
          }
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
          &quot;end_line&quot;: 4,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The source requires the independent document body.&quot;,
          &quot;start_line&quot;: 4
        }
      ],
      &quot;input&quot;: {
        &quot;index&quot;: 0,
        &quot;kind&quot;: &quot;input&quot;
      },
      &quot;op&quot;: &quot;select_part&quot;,
      &quot;output&quot;: &quot;body&quot;,
      &quot;path&quot;: [
        &quot;body&quot;
      ]
    }
  ]
}</pre>

</details>

## ir_008 · return

Block: block_003; Operator: unknown.

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
          &quot;data_6da41c6c56e4ba57e2dc42f4afc22ec7a9c5aa3ac7d45c9e2b0010f47d3c09c5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ae5eae31c3d0f6200b629e6b46224378b4415565ba6e7e0dddc32c4a30c5fc45&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3fec0f3299fed759b1dc13e92a9e50368b182da92d8c4cacfe365c010ae0a9b6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ae5eae31c3d0f6200b629e6b46224378b4415565ba6e7e0dddc32c4a30c5fc45&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;cache&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6da41c6c56e4ba57e2dc42f4afc22ec7a9c5aa3ac7d45c9e2b0010f47d3c09c5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;ir_read_boundary_0&quot;
        }
      }
    ]
  },
  &quot;exit_state&quot;: {
    &quot;bindings&quot;: [
      {
        &quot;data_ids&quot;: [
          &quot;data_6da41c6c56e4ba57e2dc42f4afc22ec7a9c5aa3ac7d45c9e2b0010f47d3c09c5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_001&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ae5eae31c3d0f6200b629e6b46224378b4415565ba6e7e0dddc32c4a30c5fc45&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_004&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_3fec0f3299fed759b1dc13e92a9e50368b182da92d8c4cacfe365c010ae0a9b6&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;result&quot;,
          &quot;name&quot;: &quot;result_005&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_ae5eae31c3d0f6200b629e6b46224378b4415565ba6e7e0dddc32c4a30c5fc45&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;runtime_context&quot;,
          &quot;name&quot;: &quot;cache&quot;
        }
      },
      {
        &quot;data_ids&quot;: [
          &quot;data_6da41c6c56e4ba57e2dc42f4afc22ec7a9c5aa3ac7d45c9e2b0010f47d3c09c5&quot;
        ],
        &quot;location&quot;: {
          &quot;kind&quot;: &quot;storage&quot;,
          &quot;name&quot;: &quot;ir_read_boundary_0&quot;
        }
      }
    ]
  }
}</pre>

</details>

<details><summary>Original annotation audit: IR semantics, step arguments, output bindings and evidence</summary>

<pre>{
  &quot;ir_semantics&quot;: {
    &quot;events&quot;: [],
    &quot;operator&quot;: null,
    &quot;operator_evidences&quot;: [],
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
| D001 | data_3fec0f3299fed759b1dc13e92a9e50368b182da92d8c4cacfe365c010ae0a9b6 | opaque |
| D002 | data_6da41c6c56e4ba57e2dc42f4afc22ec7a9c5aa3ac7d45c9e2b0010f47d3c09c5 | opaque |
| D003 | data_ae5eae31c3d0f6200b629e6b46224378b4415565ba6e7e0dddc32c4a30c5fc45 | known_parts |

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
  &quot;id&quot;: &quot;data_3fec0f3299fed759b1dc13e92a9e50368b182da92d8c4cacfe365c010ae0a9b6&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: null,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
    &quot;part_of&quot;: &quot;data_ae5eae31c3d0f6200b629e6b46224378b4415565ba6e7e0dddc32c4a30c5fc45&quot;,
    &quot;path&quot;: [
      &quot;body&quot;
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
  &quot;id&quot;: &quot;data_6da41c6c56e4ba57e2dc42f4afc22ec7a9c5aa3ac7d45c9e2b0010f47d3c09c5&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;storage:ir_read_boundary_0&quot;,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
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
    &quot;form&quot;: &quot;known_parts&quot;,
    &quot;parts&quot;: [
      {
        &quot;data&quot;: &quot;data_3fec0f3299fed759b1dc13e92a9e50368b182da92d8c4cacfe365c010ae0a9b6&quot;,
        &quot;path&quot;: [
          &quot;body&quot;
        ]
      }
    ],
    &quot;parts_complete&quot;: false
  },
  &quot;id&quot;: &quot;data_ae5eae31c3d0f6200b629e6b46224378b4415565ba6e7e0dddc32c4a30c5fc45&quot;,
  &quot;origin&quot;: {
    &quot;acquired_from&quot;: &quot;runtime_context:cache&quot;,
    &quot;at&quot;: null,
    &quot;dependencies&quot;: [],
    &quot;inputs&quot;: [],
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
    &quot;cache&quot;: [
      {
        &quot;end_line&quot;: 3,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The synthetic source explicitly identifies the cache branch and its stated mechanism.&quot;,
        &quot;start_line&quot;: 3
      }
    ],
    &quot;ir_read_boundary_0&quot;: [
      {
        &quot;reason&quot;: &quot;Explicit engineering fixture; location validity is not semantic proof.&quot;,
        &quot;target&quot;: {
          &quot;instruction_id&quot;: &quot;ir_001&quot;,
          &quot;path&quot;: []
        }
      }
    ],
    &quot;user&quot;: [
      {
        &quot;end_line&quot;: 4,
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;reason&quot;: &quot;The source requires the independent document body.&quot;,
        &quot;start_line&quot;: 4
      }
    ]
  },
  &quot;stats&quot;: {
    &quot;block_evaluations&quot;: 6,
    &quot;data_count&quot;: 3,
    &quot;description_revision&quot;: 1,
    &quot;record_count&quot;: 5
  }
}</pre>

</details>

<details><summary>Compilation audit: original model processing segments and program-generated location mapping</summary>

<pre>{
  &quot;compilation_map&quot;: {
    &quot;compiled_sha256&quot;: &quot;dd4d23e8effb3ab2a5e7f7aff8765e7bff1b464317c708fa9425ce806bbc518d&quot;,
    &quot;compiler_version&quot;: &quot;skillflow-processing-compiler-v11&quot;,
    &quot;constraints&quot;: [],
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
        &quot;mode&quot;: &quot;local&quot;,
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
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_001/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_004&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_004&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
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
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_004/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_005&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_005&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
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
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_005/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_006&quot;,
          &quot;events&quot;,
          0
        ],
        &quot;instruction_id&quot;: &quot;ir_006&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;local&quot;,
        &quot;raw_atomic_range&quot;: [
          0,
          1
        ],
        &quot;raw_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_006&quot;,
          &quot;events&quot;,
          0,
          &quot;events&quot;,
          0
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_006/segments/0/ops/0&quot;
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
        &quot;mode&quot;: &quot;model&quot;,
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
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/0&quot;
      },
      {
        &quot;compiled_path&quot;: [
          &quot;ir_semantics&quot;,
          &quot;ir_007&quot;,
          &quot;events&quot;,
          1
        ],
        &quot;instruction_id&quot;: &quot;ir_007&quot;,
        &quot;kind&quot;: &quot;retained&quot;,
        &quot;mode&quot;: &quot;model&quot;,
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
        ],
        &quot;wire_path&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/0&quot;
      }
    ],
    &quot;fragment_origins&quot;: {
      &quot;/demands&quot;: &quot;task-correspondence&quot;,
      &quot;/expressions&quot;: &quot;processing&quot;,
      &quot;/ir_semantics&quot;: &quot;processing&quot;,
      &quot;/ir_semantics/ir_001/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_002/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_004/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_005/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_006/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_007/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_007/sensitivity/0&quot;: &quot;sensitivity&quot;,
      &quot;/ir_semantics/ir_008/sensitivity&quot;: &quot;sensitivity&quot;,
      &quot;/locations&quot;: &quot;processing&quot;,
      &quot;/processing_gaps&quot;: &quot;processing&quot;,
      &quot;/realizations&quot;: &quot;task-correspondence&quot;
    },
    &quot;fragment_paths&quot;: {
      &quot;/demands&quot;: {
        &quot;fragment&quot;: &quot;task-correspondence&quot;,
        &quot;path&quot;: &quot;/demands&quot;
      },
      &quot;/expressions&quot;: {
        &quot;fragment&quot;: &quot;processing&quot;,
        &quot;path&quot;: &quot;/expressions&quot;
      },
      &quot;/ir_semantics&quot;: {
        &quot;fragment&quot;: &quot;processing&quot;,
        &quot;path&quot;: &quot;/ir_semantics&quot;
      },
      &quot;/ir_semantics/ir_001/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_002/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_004/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_005/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_006/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_007/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/ir_semantics/ir_007/sensitivity/0&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations/0&quot;
      },
      &quot;/ir_semantics/ir_008/sensitivity&quot;: {
        &quot;fragment&quot;: &quot;sensitivity&quot;,
        &quot;path&quot;: &quot;/declarations&quot;
      },
      &quot;/locations&quot;: {
        &quot;fragment&quot;: &quot;processing&quot;,
        &quot;path&quot;: &quot;/locations&quot;
      },
      &quot;/processing_gaps&quot;: {
        &quot;fragment&quot;: &quot;processing&quot;,
        &quot;path&quot;: &quot;/processing_gaps&quot;
      },
      &quot;/realizations&quot;: {
        &quot;fragment&quot;: &quot;task-correspondence&quot;,
        &quot;path&quot;: &quot;/realizations&quot;
      }
    },
    &quot;goals&quot;: [
      {
        &quot;goal_id&quot;: &quot;goal_e0c7e2c7f8ab73558ea6&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/0&quot;,
        &quot;requirement_id&quot;: &quot;R&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 0,
          &quot;instruction_id&quot;: &quot;ir_008&quot;,
          &quot;side&quot;: &quot;input&quot;
        },
        &quot;wire_pointer&quot;: &quot;/demands/0&quot;
      }
    ],
    &quot;processing_gaps&quot;: [
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 3,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The synthetic source explicitly identifies the cache branch and its stated mechanism.&quot;,
            &quot;start_line&quot;: 3
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_003&quot;,
        &quot;locations&quot;: [
          &quot;cache&quot;
        ],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [
          0
        ],
        &quot;reason&quot;: &quot;The source mechanism has an unsupported relation.&quot;,
        &quot;unmodeled&quot;: true,
        &quot;validation_errors&quot;: []
      }
    ],
    &quot;raw_sha256&quot;: &quot;200e7f25f460db2dd59e2da4eaad85544f520349ed8fdde8a71f968b5c3cfcae&quot;,
    &quot;runtime_contract&quot;: {
      &quot;sha256&quot;: &quot;e2c37499e5d575975c528bd8f30169616eeb98a41e85dae7b2e8a9b7e34a49a6&quot;,
      &quot;version&quot;: &quot;skillflow-abstract-runtime-v8&quot;
    },
    &quot;schema_version&quot;: &quot;skillflow-processing-compilation-v11&quot;,
    &quot;wire_paths&quot;: {
      &quot;/ir_semantics/ir_001&quot;: &quot;/ir_semantics/ir_001&quot;,
      &quot;/ir_semantics/ir_001/events/0&quot;: &quot;/ir_semantics/ir_001/segments/0&quot;,
      &quot;/ir_semantics/ir_001/events/0/events/0&quot;: &quot;/ir_semantics/ir_001/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_001/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_001/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_001/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_001/segments/0/ops/0/evidences&quot;,
      &quot;/ir_semantics/ir_001/events/0/evidences&quot;: &quot;/ir_semantics/ir_001/segments/0/evidences&quot;,
      &quot;/ir_semantics/ir_001/output_bindings/0&quot;: &quot;/ir_semantics/ir_001/output_bindings/0&quot;,
      &quot;/ir_semantics/ir_001/output_bindings/0/evidences&quot;: &quot;/ir_semantics/ir_001/output_bindings/0/evidences&quot;,
      &quot;/ir_semantics/ir_002&quot;: &quot;/ir_semantics/ir_002&quot;,
      &quot;/ir_semantics/ir_004&quot;: &quot;/ir_semantics/ir_004&quot;,
      &quot;/ir_semantics/ir_004/events/0&quot;: &quot;/ir_semantics/ir_004/segments/0&quot;,
      &quot;/ir_semantics/ir_004/events/0/events/0&quot;: &quot;/ir_semantics/ir_004/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_004/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_004/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_004/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_004/segments/0/ops/0/evidences&quot;,
      &quot;/ir_semantics/ir_004/events/0/evidences&quot;: &quot;/ir_semantics/ir_004/segments/0/evidences&quot;,
      &quot;/ir_semantics/ir_004/output_bindings/0&quot;: &quot;/ir_semantics/ir_004/output_bindings/0&quot;,
      &quot;/ir_semantics/ir_004/output_bindings/0/evidences&quot;: &quot;/ir_semantics/ir_004/output_bindings/0/evidences&quot;,
      &quot;/ir_semantics/ir_005&quot;: &quot;/ir_semantics/ir_005&quot;,
      &quot;/ir_semantics/ir_005/events/0&quot;: &quot;/ir_semantics/ir_005/segments/0&quot;,
      &quot;/ir_semantics/ir_005/events/0/events/0&quot;: &quot;/ir_semantics/ir_005/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_005/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_005/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_005/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_005/segments/0/ops/0/evidences&quot;,
      &quot;/ir_semantics/ir_005/events/0/evidences&quot;: &quot;/ir_semantics/ir_005/segments/0/evidences&quot;,
      &quot;/ir_semantics/ir_006&quot;: &quot;/ir_semantics/ir_006&quot;,
      &quot;/ir_semantics/ir_006/events/0&quot;: &quot;/ir_semantics/ir_006/segments/0&quot;,
      &quot;/ir_semantics/ir_006/events/0/events/0&quot;: &quot;/ir_semantics/ir_006/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_006/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_006/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_006/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_006/segments/0/ops/0/evidences&quot;,
      &quot;/ir_semantics/ir_006/events/0/evidences&quot;: &quot;/ir_semantics/ir_006/segments/0/evidences&quot;,
      &quot;/ir_semantics/ir_006/output_bindings/0&quot;: &quot;/ir_semantics/ir_006/output_bindings/0&quot;,
      &quot;/ir_semantics/ir_006/output_bindings/0/evidences&quot;: &quot;/ir_semantics/ir_006/output_bindings/0/evidences&quot;,
      &quot;/ir_semantics/ir_007&quot;: &quot;/ir_semantics/ir_007&quot;,
      &quot;/ir_semantics/ir_007/events/0&quot;: &quot;/ir_semantics/ir_007/segments/0&quot;,
      &quot;/ir_semantics/ir_007/events/0/events/0&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_007/events/0/events/0/atomic_ops/0&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/0&quot;,
      &quot;/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/evidences&quot;: &quot;/ir_semantics/ir_007/segments/0/ops/0/evidences&quot;,
      &quot;/ir_semantics/ir_007/events/0/evidences&quot;: &quot;/ir_semantics/ir_007/segments/0/evidences&quot;,
      &quot;/ir_semantics/ir_007/output_bindings/0&quot;: &quot;/ir_semantics/ir_007/output_bindings/0&quot;,
      &quot;/ir_semantics/ir_007/output_bindings/0/evidences&quot;: &quot;/ir_semantics/ir_007/output_bindings/0/evidences&quot;,
      &quot;/ir_semantics/ir_008&quot;: &quot;/ir_semantics/ir_008&quot;,
      &quot;/location_evidences/cache&quot;: &quot;/locations/cache/evidences&quot;,
      &quot;/location_evidences/ir_read_boundary_0&quot;: &quot;/locations/ir_read_boundary_0/evidences&quot;,
      &quot;/location_evidences/user&quot;: &quot;/locations/user/evidences&quot;,
      &quot;/locations/cache&quot;: &quot;/locations/cache&quot;,
      &quot;/locations/ir_read_boundary_0&quot;: &quot;/locations/ir_read_boundary_0&quot;,
      &quot;/locations/user&quot;: &quot;/locations/user&quot;,
      &quot;/realizations/0&quot;: &quot;/realizations/0&quot;
    },
    &quot;wire_sha256&quot;: &quot;ce9f2bf95becf7945e4a82cbfd66e738fd1d02b6f92f94c1aedba9b32729c0ce&quot;,
    &quot;wire_version&quot;: &quot;skillflow-flat-annotation-v1&quot;
  },
  &quot;raw_annotation&quot;: {
    &quot;demands&quot;: [
      {
        &quot;expected&quot;: null,
        &quot;expected_path&quot;: [],
        &quot;path&quot;: [],
        &quot;preserve&quot;: &quot;value&quot;,
        &quot;reason&quot;: &quot;Keep the explicitly required body.&quot;,
        &quot;requirement_id&quot;: &quot;R&quot;,
        &quot;target&quot;: {
          &quot;index&quot;: 0,
          &quot;instruction_id&quot;: &quot;ir_008&quot;,
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
                        &quot;reason&quot;: &quot;Explicit engineering fixture; location validity is not semantic proof.&quot;,
                        &quot;target&quot;: {
                          &quot;instruction_id&quot;: &quot;ir_001&quot;,
                          &quot;path&quot;: []
                        }
                      }
                    ],
                    &quot;location&quot;: &quot;ir_read_boundary_0&quot;,
                    &quot;op&quot;: &quot;read&quot;,
                    &quot;output&quot;: &quot;stage_0&quot;
                  }
                ],
                &quot;effect&quot;: &quot;fs_read&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;reason&quot;: &quot;Explicit engineering fixture; location validity is not semantic proof.&quot;,
                    &quot;target&quot;: {
                      &quot;instruction_id&quot;: &quot;ir_001&quot;,
                      &quot;path&quot;: []
                    }
                  }
                ]
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;reason&quot;: &quot;Explicit engineering fixture; location validity is not semantic proof.&quot;,
                &quot;target&quot;: {
                  &quot;instruction_id&quot;: &quot;ir_001&quot;,
                  &quot;path&quot;: []
                }
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;local&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;reason&quot;: &quot;Explicit engineering fixture; location validity is not semantic proof.&quot;,
                &quot;target&quot;: {
                  &quot;instruction_id&quot;: &quot;ir_001&quot;,
                  &quot;path&quot;: []
                }
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;stage_0&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_002&quot;: {
        &quot;events&quot;: [],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
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
                        &quot;end_line&quot;: 4,
                        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                        &quot;reason&quot;: &quot;The fixture declares the read or delivery explicitly.&quot;,
                        &quot;start_line&quot;: 3
                      }
                    ],
                    &quot;location&quot;: &quot;cache&quot;,
                    &quot;op&quot;: &quot;read&quot;,
                    &quot;output&quot;: &quot;old&quot;
                  }
                ],
                &quot;effect&quot;: &quot;context_read&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 4,
                    &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                    &quot;reason&quot;: &quot;The fixture declares the read or delivery explicitly.&quot;,
                    &quot;start_line&quot;: 3
                  }
                ]
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 4,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The fixture declares the read or delivery explicitly.&quot;,
                &quot;start_line&quot;: 3
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;local&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 4,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The source requires the independent document body.&quot;,
                &quot;start_line&quot;: 4
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;old&quot;
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
                        &quot;end_line&quot;: 4,
                        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                        &quot;reason&quot;: &quot;The fixture declares the read or delivery explicitly.&quot;,
                        &quot;start_line&quot;: 3
                      }
                    ],
                    &quot;inputs&quot;: [
                      {
                        &quot;index&quot;: 0,
                        &quot;kind&quot;: &quot;input&quot;
                      }
                    ],
                    &quot;op&quot;: &quot;deliver&quot;,
                    &quot;target&quot;: &quot;user&quot;
                  }
                ],
                &quot;effect&quot;: &quot;user_output&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 4,
                    &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                    &quot;reason&quot;: &quot;The fixture declares the read or delivery explicitly.&quot;,
                    &quot;start_line&quot;: 3
                  }
                ]
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 4,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The fixture declares the read or delivery explicitly.&quot;,
                &quot;start_line&quot;: 3
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;local&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_006&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 4,
                        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                        &quot;reason&quot;: &quot;The fixture declares the read or delivery explicitly.&quot;,
                        &quot;start_line&quot;: 3
                      }
                    ],
                    &quot;location&quot;: &quot;cache&quot;,
                    &quot;op&quot;: &quot;read&quot;,
                    &quot;output&quot;: &quot;cached&quot;
                  }
                ],
                &quot;effect&quot;: &quot;context_read&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 4,
                    &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                    &quot;reason&quot;: &quot;The fixture declares the read or delivery explicitly.&quot;,
                    &quot;start_line&quot;: 3
                  }
                ]
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 4,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The fixture declares the read or delivery explicitly.&quot;,
                &quot;start_line&quot;: 3
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;local&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 4,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The source requires the independent document body.&quot;,
                &quot;start_line&quot;: 4
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;cached&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: []
      },
      &quot;ir_007&quot;: {
        &quot;events&quot;: [
          {
            &quot;events&quot;: [
              {
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;end_line&quot;: 4,
                        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                        &quot;reason&quot;: &quot;The source requires the independent document body.&quot;,
                        &quot;start_line&quot;: 4
                      }
                    ],
                    &quot;input&quot;: {
                      &quot;index&quot;: 0,
                      &quot;kind&quot;: &quot;input&quot;
                    },
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;output&quot;: &quot;body&quot;,
                    &quot;path&quot;: [
                      &quot;body&quot;
                    ]
                  }
                ],
                &quot;effect&quot;: &quot;transform&quot;,
                &quot;evidences&quot;: [
                  {
                    &quot;end_line&quot;: 4,
                    &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                    &quot;reason&quot;: &quot;The source requires the independent document body.&quot;,
                    &quot;start_line&quot;: 4
                  }
                ]
              }
            ],
            &quot;evidences&quot;: [
              {
                &quot;reason&quot;: &quot;Explicit engineering fixture; location validity is not semantic proof.&quot;,
                &quot;target&quot;: {
                  &quot;instruction_id&quot;: &quot;ir_007&quot;,
                  &quot;path&quot;: []
                }
              }
            ],
            &quot;kind&quot;: &quot;processing&quot;,
            &quot;mode&quot;: &quot;model&quot;,
            &quot;returns&quot;: []
          }
        ],
        &quot;operator&quot;: [
          &quot;llm&quot;
        ],
        &quot;operator_evidences&quot;: [
          {
            &quot;reason&quot;: &quot;Explicit engineering fixture; location validity is not semantic proof.&quot;,
            &quot;target&quot;: {
              &quot;instruction_id&quot;: &quot;ir_007&quot;,
              &quot;path&quot;: []
            },
            &quot;value&quot;: &quot;llm&quot;
          }
        ],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;reason&quot;: &quot;Explicit engineering fixture; location validity is not semantic proof.&quot;,
                &quot;target&quot;: {
                  &quot;instruction_id&quot;: &quot;ir_007&quot;,
                  &quot;path&quot;: []
                }
              }
            ],
            &quot;output_index&quot;: 0,
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;body&quot;
            }
          }
        ],
        &quot;sensitivity&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;end_line&quot;: 5,
                &quot;file&quot;: &quot;skill/SKILL.md&quot;,
                &quot;reason&quot;: &quot;The source declares token confidentiality.&quot;,
                &quot;start_line&quot;: 5
              }
            ],
            &quot;label&quot;: &quot;credential&quot;,
            &quot;path&quot;: [
              &quot;token&quot;
            ],
            &quot;property&quot;: &quot;value&quot;,
            &quot;value&quot;: {
              &quot;index&quot;: 0,
              &quot;kind&quot;: &quot;input&quot;
            }
          }
        ]
      },
      &quot;ir_008&quot;: {
        &quot;events&quot;: [],
        &quot;operator&quot;: null,
        &quot;operator_evidences&quot;: [],
        &quot;order&quot;: &quot;fixed&quot;,
        &quot;output_bindings&quot;: [],
        &quot;sensitivity&quot;: []
      }
    },
    &quot;location_evidences&quot;: {
      &quot;cache&quot;: [
        {
          &quot;end_line&quot;: 3,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The synthetic source explicitly identifies the cache branch and its stated mechanism.&quot;,
          &quot;start_line&quot;: 3
        }
      ],
      &quot;ir_read_boundary_0&quot;: [
        {
          &quot;reason&quot;: &quot;Explicit engineering fixture; location validity is not semantic proof.&quot;,
          &quot;target&quot;: {
            &quot;instruction_id&quot;: &quot;ir_001&quot;,
            &quot;path&quot;: []
          }
        }
      ],
      &quot;user&quot;: [
        {
          &quot;end_line&quot;: 4,
          &quot;file&quot;: &quot;skill/SKILL.md&quot;,
          &quot;reason&quot;: &quot;The source requires the independent document body.&quot;,
          &quot;start_line&quot;: 4
        }
      ]
    },
    &quot;locations&quot;: {
      &quot;cache&quot;: {
        &quot;access_scope&quot;: &quot;task&quot;,
        &quot;kind&quot;: &quot;runtime_context&quot;,
        &quot;name&quot;: &quot;cache&quot;,
        &quot;operand_refs&quot;: [],
        &quot;retention&quot;: &quot;task&quot;
      },
      &quot;ir_read_boundary_0&quot;: {
        &quot;access_scope&quot;: &quot;task&quot;,
        &quot;kind&quot;: &quot;storage&quot;,
        &quot;name&quot;: &quot;ir_read_boundary_0&quot;,
        &quot;operand_refs&quot;: [
          {
            &quot;index&quot;: 0,
            &quot;instruction_id&quot;: &quot;ir_001&quot;,
            &quot;side&quot;: &quot;input&quot;
          }
        ],
        &quot;retention&quot;: &quot;persistent&quot;
      },
      &quot;user&quot;: {
        &quot;access_scope&quot;: &quot;recipient&quot;,
        &quot;kind&quot;: &quot;user&quot;,
        &quot;name&quot;: &quot;user&quot;,
        &quot;operand_refs&quot;: [],
        &quot;retention&quot;: null
      }
    },
    &quot;outcome&quot;: &quot;completed&quot;,
    &quot;processing_gaps&quot;: [
      {
        &quot;control&quot;: false,
        &quot;evidences&quot;: [
          {
            &quot;end_line&quot;: 3,
            &quot;file&quot;: &quot;skill/SKILL.md&quot;,
            &quot;reason&quot;: &quot;The synthetic source explicitly identifies the cache branch and its stated mechanism.&quot;,
            &quot;start_line&quot;: 3
          }
        ],
        &quot;instruction_id&quot;: &quot;ir_003&quot;,
        &quot;locations&quot;: [
          &quot;cache&quot;
        ],
        &quot;origin&quot;: &quot;source&quot;,
        &quot;outputs&quot;: [
          0
        ],
        &quot;reason&quot;: &quot;The source mechanism has an unsupported relation.&quot;,
        &quot;unmodeled&quot;: true,
        &quot;validation_errors&quot;: []
      }
    ],
    &quot;realizations&quot;: [
      {
        &quot;bindings&quot;: [],
        &quot;gaps&quot;: [],
        &quot;requirement_id&quot;: &quot;R&quot;,
        &quot;status&quot;: &quot;expressed&quot;
      }
    ],
    &quot;task_revision_id&quot;: &quot;901ff8f9c8af07e1a126c9af3ba4cd021a8bb1b058046ed568579396458c63dc&quot;
  }
}</pre>

</details>

