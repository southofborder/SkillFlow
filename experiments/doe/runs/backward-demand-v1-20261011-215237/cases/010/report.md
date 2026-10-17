# Task-driven Backward Demand

Backward demand describes information retained under the recorded processing relationships. It does not prove irreplaceability, global minimality, sensitivity, or absence of data over-exposure.

**Status:** complete

**Candidate origin:** assistant\_authored\_offline

Offline preparation; no model calls.

## Coverage

<pre>{
  &quot;requirements&quot;: {
    &quot;R001&quot;: &quot;bound&quot;,
    &quot;R002&quot;: &quot;bound&quot;,
    &quot;R003&quot;: &quot;bound&quot;,
    &quot;R004&quot;: &quot;bound&quot;,
    &quot;R005&quot;: &quot;bound&quot;,
    &quot;R006&quot;: &quot;bound&quot;,
    &quot;R007&quot;: &quot;bound&quot;,
    &quot;R008&quot;: &quot;bound&quot;
  },
  &quot;sinks&quot;: 12,
  &quot;expected_sinks&quot;: 12,
  &quot;upstream&quot;: {
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
  }
}</pre>

## Task preservation goals

A required action does not exempt all of its current payload.

<a id="goal-dd31ffb1f533a2fabe0b"></a>

### G001

Use the user\-supplied request\.json, including term and any present from\_date and limit values\.

<pre>{
  &quot;id&quot;: &quot;G001&quot;,
  &quot;requirement_id&quot;: &quot;R001&quot;,
  &quot;target_id&quot;: &quot;target_6afff9c218ebc2a39759&quot;,
  &quot;property&quot;: &quot;constraint&quot;,
  &quot;path&quot;: [],
  &quot;expected&quot;: null,
  &quot;expected_path&quot;: [],
  &quot;reason&quot;: &quot;Keep the named request origin without turning the entire request into a required payload.&quot;
}</pre>

<details><summary>Existing Task evidence and binding</summary><pre>{
  &quot;id&quot;: &quot;R001&quot;,
  &quot;text&quot;: &quot;Use the user-supplied request.json, including term and any present from_date and limit values.&quot;,
  &quot;evidences&quot;: [
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 5,
      &quot;end_line&quot;: 5,
      &quot;reason&quot;: &quot;The workflow names the source and distinguishes the optional fields.&quot;
    }
  ],
  &quot;bindings&quot;: [
    {
      &quot;target_id&quot;: &quot;target_6afff9c218ebc2a39759&quot;,
      &quot;reason&quot;: &quot;This binds the request source, not a requirement to transmit the whole request.&quot;
    }
  ]
}</pre></details>

<a id="goal-b4b3d2c42b6f00cdb0ba"></a>

### G002

Call index\.search exactly once, passing request\.term unchanged as query\.

<pre>{
  &quot;id&quot;: &quot;G002&quot;,
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;target_id&quot;: &quot;demand_target_450c34e4f0db7a8c6802&quot;,
  &quot;property&quot;: &quot;action&quot;,
  &quot;path&quot;: [],
  &quot;expected&quot;: null,
  &quot;expected_path&quot;: [],
  &quot;reason&quot;: &quot;Keep the one required search request.&quot;
}</pre>

<details><summary>Existing Task evidence and binding</summary><pre>{
  &quot;id&quot;: &quot;R002&quot;,
  &quot;text&quot;: &quot;Call index.search exactly once, passing request.term unchanged as query.&quot;,
  &quot;evidences&quot;: [
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 7,
      &quot;end_line&quot;: 7,
      &quot;reason&quot;: &quot;The source specifies both call multiplicity and the original query value.&quot;
    }
  ],
  &quot;bindings&quot;: [
    {
      &quot;target_id&quot;: &quot;target_74256b1796dc113828cc&quot;,
      &quot;reason&quot;: &quot;This preserves the global single-call restriction.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_70c96dfd296c8130066b&quot;,
      &quot;reason&quot;: &quot;This is the query value rather than the full request.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_aeb48f99c87b5433380d&quot;,
      &quot;reason&quot;: &quot;The parameter must preserve the original term.&quot;
    }
  ]
}</pre></details>

<a id="goal-a5b641574ba521ba97b3"></a>

### G003

Call index\.search exactly once, passing request\.term unchanged as query\.

<pre>{
  &quot;id&quot;: &quot;G003&quot;,
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;target_id&quot;: &quot;demand_target_eb630a83282c75fd652c&quot;,
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;query&quot;
  ],
  &quot;expected&quot;: {
    &quot;kind&quot;: &quot;input&quot;,
    &quot;index&quot;: 1
  },
  &quot;expected_path&quot;: [],
  &quot;reason&quot;: &quot;The query member is the unchanged term value.&quot;
}</pre>

<details><summary>Existing Task evidence and binding</summary><pre>{
  &quot;id&quot;: &quot;R002&quot;,
  &quot;text&quot;: &quot;Call index.search exactly once, passing request.term unchanged as query.&quot;,
  &quot;evidences&quot;: [
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 7,
      &quot;end_line&quot;: 7,
      &quot;reason&quot;: &quot;The source specifies both call multiplicity and the original query value.&quot;
    }
  ],
  &quot;bindings&quot;: [
    {
      &quot;target_id&quot;: &quot;target_74256b1796dc113828cc&quot;,
      &quot;reason&quot;: &quot;This preserves the global single-call restriction.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_70c96dfd296c8130066b&quot;,
      &quot;reason&quot;: &quot;This is the query value rather than the full request.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_aeb48f99c87b5433380d&quot;,
      &quot;reason&quot;: &quot;The parameter must preserve the original term.&quot;
    }
  ]
}</pre></details>

<a id="goal-ee29196b43aae6ee7ca2"></a>

### G004

Call index\.search exactly once, passing request\.term unchanged as query\.

<pre>{
  &quot;id&quot;: &quot;G004&quot;,
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;target_id&quot;: &quot;target_aeb48f99c87b5433380d&quot;,
  &quot;property&quot;: &quot;constraint&quot;,
  &quot;path&quot;: [],
  &quot;expected&quot;: null,
  &quot;expected_path&quot;: [],
  &quot;reason&quot;: &quot;Preserve the existing single-call and original-query restriction.&quot;
}</pre>

<details><summary>Existing Task evidence and binding</summary><pre>{
  &quot;id&quot;: &quot;R002&quot;,
  &quot;text&quot;: &quot;Call index.search exactly once, passing request.term unchanged as query.&quot;,
  &quot;evidences&quot;: [
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 7,
      &quot;end_line&quot;: 7,
      &quot;reason&quot;: &quot;The source specifies both call multiplicity and the original query value.&quot;
    }
  ],
  &quot;bindings&quot;: [
    {
      &quot;target_id&quot;: &quot;target_74256b1796dc113828cc&quot;,
      &quot;reason&quot;: &quot;This preserves the global single-call restriction.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_70c96dfd296c8130066b&quot;,
      &quot;reason&quot;: &quot;This is the query value rather than the full request.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_aeb48f99c87b5433380d&quot;,
      &quot;reason&quot;: &quot;The parameter must preserve the original term.&quot;
    }
  ]
}</pre></details>

<a id="goal-24b13b18dd5591e8a48f"></a>

### G005

Pass from\_date unchanged only when present; omit the argument when absent\. Its stated accepted format does not request a preprocessing step\.

<pre>{
  &quot;id&quot;: &quot;G005&quot;,
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;target_id&quot;: &quot;demand_target_eb630a83282c75fd652c&quot;,
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;expected&quot;: {
    &quot;kind&quot;: &quot;input&quot;,
    &quot;index&quot;: 2
  },
  &quot;expected_path&quot;: [],
  &quot;reason&quot;: &quot;When included, from_date is the original optional value.&quot;
}</pre>

<details><summary>Existing Task evidence and binding</summary><pre>{
  &quot;id&quot;: &quot;R003&quot;,
  &quot;text&quot;: &quot;Pass from_date unchanged only when present; omit the argument when absent. Its stated accepted format does not request a preprocessing step.&quot;,
  &quot;evidences&quot;: [
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 10,
      &quot;end_line&quot;: 11,
      &quot;reason&quot;: &quot;The argument carries its original value when present and is absent otherwise.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 15,
      &quot;end_line&quot;: 15,
      &quot;reason&quot;: &quot;The separate configuration applies to the same call.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/query.yaml&quot;,
      &quot;start_line&quot;: 1,
      &quot;end_line&quot;: 2,
      &quot;reason&quot;: &quot;The configuration explicitly sets the missing from_date behavior to omit.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 19,
      &quot;end_line&quot;: 19,
      &quot;reason&quot;: &quot;The format description does not require validation or normalization.&quot;
    }
  ],
  &quot;bindings&quot;: [
    {
      &quot;target_id&quot;: &quot;target_d49b7dd46f8209dbe334&quot;,
      &quot;reason&quot;: &quot;This is the optional business value.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_77b9604eaae52b5abbc6&quot;,
      &quot;reason&quot;: &quot;This is an existence control value, not an extra request member.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_2a168b4a5f91acde4f8e&quot;,
      &quot;reason&quot;: &quot;This preserves the present-value requirement.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_8fe35635386dff487a10&quot;,
      &quot;reason&quot;: &quot;This preserves omission when absent.&quot;
    }
  ]
}</pre></details>

<a id="goal-2d673be02770278c0b36"></a>

### G006

Pass from\_date unchanged only when present; omit the argument when absent\. Its stated accepted format does not request a preprocessing step\.

<pre>{
  &quot;id&quot;: &quot;G006&quot;,
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;target_id&quot;: &quot;demand_target_eb630a83282c75fd652c&quot;,
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;expected&quot;: null,
  &quot;expected_path&quot;: [],
  &quot;reason&quot;: &quot;Preserve from_date inclusion versus omission; absence is not null substitution.&quot;
}</pre>

<details><summary>Existing Task evidence and binding</summary><pre>{
  &quot;id&quot;: &quot;R003&quot;,
  &quot;text&quot;: &quot;Pass from_date unchanged only when present; omit the argument when absent. Its stated accepted format does not request a preprocessing step.&quot;,
  &quot;evidences&quot;: [
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 10,
      &quot;end_line&quot;: 11,
      &quot;reason&quot;: &quot;The argument carries its original value when present and is absent otherwise.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 15,
      &quot;end_line&quot;: 15,
      &quot;reason&quot;: &quot;The separate configuration applies to the same call.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/query.yaml&quot;,
      &quot;start_line&quot;: 1,
      &quot;end_line&quot;: 2,
      &quot;reason&quot;: &quot;The configuration explicitly sets the missing from_date behavior to omit.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 19,
      &quot;end_line&quot;: 19,
      &quot;reason&quot;: &quot;The format description does not require validation or normalization.&quot;
    }
  ],
  &quot;bindings&quot;: [
    {
      &quot;target_id&quot;: &quot;target_d49b7dd46f8209dbe334&quot;,
      &quot;reason&quot;: &quot;This is the optional business value.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_77b9604eaae52b5abbc6&quot;,
      &quot;reason&quot;: &quot;This is an existence control value, not an extra request member.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_2a168b4a5f91acde4f8e&quot;,
      &quot;reason&quot;: &quot;This preserves the present-value requirement.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_8fe35635386dff487a10&quot;,
      &quot;reason&quot;: &quot;This preserves omission when absent.&quot;
    }
  ]
}</pre></details>

<a id="goal-4b08eebd441e38772d93"></a>

### G007

Pass limit unchanged only when present; omit the argument when absent\.

<pre>{
  &quot;id&quot;: &quot;G007&quot;,
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;target_id&quot;: &quot;demand_target_eb630a83282c75fd652c&quot;,
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;expected&quot;: {
    &quot;kind&quot;: &quot;input&quot;,
    &quot;index&quot;: 4
  },
  &quot;expected_path&quot;: [],
  &quot;reason&quot;: &quot;When included, limit is the original optional value.&quot;
}</pre>

<details><summary>Existing Task evidence and binding</summary><pre>{
  &quot;id&quot;: &quot;R004&quot;,
  &quot;text&quot;: &quot;Pass limit unchanged only when present; omit the argument when absent.&quot;,
  &quot;evidences&quot;: [
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 12,
      &quot;end_line&quot;: 13,
      &quot;reason&quot;: &quot;The two cases specify original value versus argument omission.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 15,
      &quot;end_line&quot;: 15,
      &quot;reason&quot;: &quot;The configuration applies to the same search call.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/query.yaml&quot;,
      &quot;start_line&quot;: 1,
      &quot;end_line&quot;: 3,
      &quot;reason&quot;: &quot;The missing-argument configuration includes limit: omit.&quot;
    }
  ],
  &quot;bindings&quot;: [
    {
      &quot;target_id&quot;: &quot;target_c171aff2761c13f2d18a&quot;,
      &quot;reason&quot;: &quot;This is the optional limit value.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_6389bd8eefc49bff667a&quot;,
      &quot;reason&quot;: &quot;This is the existence control, not part of the request payload.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_a5a1aecc877f545de2a1&quot;,
      &quot;reason&quot;: &quot;This retains the original present value.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_f105e162947fa55e18de&quot;,
      &quot;reason&quot;: &quot;This retains omission when absent.&quot;
    }
  ]
}</pre></details>

<a id="goal-291a9e34e596971dc478"></a>

### G008

Pass limit unchanged only when present; omit the argument when absent\.

<pre>{
  &quot;id&quot;: &quot;G008&quot;,
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;target_id&quot;: &quot;demand_target_eb630a83282c75fd652c&quot;,
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;expected&quot;: null,
  &quot;expected_path&quot;: [],
  &quot;reason&quot;: &quot;Preserve limit inclusion versus omission; absence is not null substitution.&quot;
}</pre>

<details><summary>Existing Task evidence and binding</summary><pre>{
  &quot;id&quot;: &quot;R004&quot;,
  &quot;text&quot;: &quot;Pass limit unchanged only when present; omit the argument when absent.&quot;,
  &quot;evidences&quot;: [
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 12,
      &quot;end_line&quot;: 13,
      &quot;reason&quot;: &quot;The two cases specify original value versus argument omission.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 15,
      &quot;end_line&quot;: 15,
      &quot;reason&quot;: &quot;The configuration applies to the same search call.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/query.yaml&quot;,
      &quot;start_line&quot;: 1,
      &quot;end_line&quot;: 3,
      &quot;reason&quot;: &quot;The missing-argument configuration includes limit: omit.&quot;
    }
  ],
  &quot;bindings&quot;: [
    {
      &quot;target_id&quot;: &quot;target_c171aff2761c13f2d18a&quot;,
      &quot;reason&quot;: &quot;This is the optional limit value.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_6389bd8eefc49bff667a&quot;,
      &quot;reason&quot;: &quot;This is the existence control, not part of the request payload.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_a5a1aecc877f545de2a1&quot;,
      &quot;reason&quot;: &quot;This retains the original present value.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_f105e162947fa55e18de&quot;,
      &quot;reason&quot;: &quot;This retains omission when absent.&quot;
    }
  ]
}</pre></details>

<a id="goal-53390a422ba1a1ffae9b"></a>

### G009

Do not invoke index\.delete anywhere in this workflow\.

<pre>{
  &quot;id&quot;: &quot;G009&quot;,
  &quot;requirement_id&quot;: &quot;R005&quot;,
  &quot;target_id&quot;: &quot;target_6624934ada448fce25c5&quot;,
  &quot;property&quot;: &quot;prohibit&quot;,
  &quot;path&quot;: [],
  &quot;expected&quot;: null,
  &quot;expected_path&quot;: [],
  &quot;reason&quot;: &quot;Keep the global delete prohibition without creating a required delete operation.&quot;
}</pre>

<details><summary>Existing Task evidence and binding</summary><pre>{
  &quot;id&quot;: &quot;R005&quot;,
  &quot;text&quot;: &quot;Do not invoke index.delete anywhere in this workflow.&quot;,
  &quot;evidences&quot;: [
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 17,
      &quot;end_line&quot;: 17,
      &quot;reason&quot;: &quot;This explicitly prohibits deletion throughout the workflow.&quot;
    }
  ],
  &quot;bindings&quot;: [
    {
      &quot;target_id&quot;: &quot;target_6624934ada448fce25c5&quot;,
      &quot;reason&quot;: &quot;The global restriction is meaningful without an existing delete operation.&quot;
    }
  ]
}</pre></details>

<a id="goal-ca4a3f6911afb92edb12"></a>

### G010

Do not introduce fuzzy expansion, pre\-call validation, or normalization from capability or parameter descriptions\.

<pre>{
  &quot;id&quot;: &quot;G010&quot;,
  &quot;requirement_id&quot;: &quot;R006&quot;,
  &quot;target_id&quot;: &quot;target_46b557f1d7527b4a10dc&quot;,
  &quot;property&quot;: &quot;prohibit&quot;,
  &quot;path&quot;: [],
  &quot;expected&quot;: null,
  &quot;expected_path&quot;: [],
  &quot;reason&quot;: &quot;Keep the restriction against inferred fuzzy expansion, validation, and normalization.&quot;
}</pre>

<details><summary>Existing Task evidence and binding</summary><pre>{
  &quot;id&quot;: &quot;R006&quot;,
  &quot;text&quot;: &quot;Do not introduce fuzzy expansion, pre-call validation, or normalization from capability or parameter descriptions.&quot;,
  &quot;evidences&quot;: [
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 3,
      &quot;end_line&quot;: 3,
      &quot;reason&quot;: &quot;Fuzzy matching is described as capability, explicitly not requested behavior.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 19,
      &quot;end_line&quot;: 19,
      &quot;reason&quot;: &quot;The argument descriptions do not instruct validation or normalization.&quot;
    }
  ],
  &quot;bindings&quot;: [
    {
      &quot;target_id&quot;: &quot;target_46b557f1d7527b4a10dc&quot;,
      &quot;reason&quot;: &quot;This preserves the no-preprocessing distinction.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_14e045481779376a48d6&quot;,
      &quot;reason&quot;: &quot;This keeps the capability note from becoming an additional task.&quot;
    }
  ]
}</pre></details>

<a id="goal-12ff945ce0aeacac1892"></a>

### G011

Do not introduce fuzzy expansion, pre\-call validation, or normalization from capability or parameter descriptions\.

<pre>{
  &quot;id&quot;: &quot;G011&quot;,
  &quot;requirement_id&quot;: &quot;R006&quot;,
  &quot;target_id&quot;: &quot;target_14e045481779376a48d6&quot;,
  &quot;property&quot;: &quot;prohibit&quot;,
  &quot;path&quot;: [],
  &quot;expected&quot;: null,
  &quot;expected_path&quot;: [],
  &quot;reason&quot;: &quot;Keep the restriction against inferred fuzzy expansion, validation, and normalization.&quot;
}</pre>

<details><summary>Existing Task evidence and binding</summary><pre>{
  &quot;id&quot;: &quot;R006&quot;,
  &quot;text&quot;: &quot;Do not introduce fuzzy expansion, pre-call validation, or normalization from capability or parameter descriptions.&quot;,
  &quot;evidences&quot;: [
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 3,
      &quot;end_line&quot;: 3,
      &quot;reason&quot;: &quot;Fuzzy matching is described as capability, explicitly not requested behavior.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 19,
      &quot;end_line&quot;: 19,
      &quot;reason&quot;: &quot;The argument descriptions do not instruct validation or normalization.&quot;
    }
  ],
  &quot;bindings&quot;: [
    {
      &quot;target_id&quot;: &quot;target_46b557f1d7527b4a10dc&quot;,
      &quot;reason&quot;: &quot;This preserves the no-preprocessing distinction.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_14e045481779376a48d6&quot;,
      &quot;reason&quot;: &quot;This keeps the capability note from becoming an additional task.&quot;
    }
  ]
}</pre></details>

<a id="goal-4682439fc6236c2c33e8"></a>

### G012

After the search, write that response's total value to local count\.txt\.

<pre>{
  &quot;id&quot;: &quot;G012&quot;,
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;target_id&quot;: &quot;demand_target_935679a9c6cf862ce45a&quot;,
  &quot;property&quot;: &quot;action&quot;,
  &quot;path&quot;: [],
  &quot;expected&quot;: null,
  &quot;expected_path&quot;: [],
  &quot;reason&quot;: &quot;Keep the explicitly required persistence of response.total.&quot;
}</pre>

<details><summary>Existing Task evidence and binding</summary><pre>{
  &quot;id&quot;: &quot;R007&quot;,
  &quot;text&quot;: &quot;After the search, write that response&#x27;s total value to local count.txt.&quot;,
  &quot;evidences&quot;: [
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 21,
      &quot;end_line&quot;: 21,
      &quot;reason&quot;: &quot;The side effect names a specific response field and destination.&quot;
    }
  ],
  &quot;bindings&quot;: [
    {
      &quot;target_id&quot;: &quot;target_0338c293f4218e102429&quot;,
      &quot;reason&quot;: &quot;This is the extracted total from the search response.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_7059117d893e83168a4a&quot;,
      &quot;reason&quot;: &quot;This is the actual saved value; extra response content is not made required.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_ce5dc739e4eaf2527fce&quot;,
      &quot;reason&quot;: &quot;This is the required count-file destination.&quot;
    }
  ]
}</pre></details>

<a id="goal-70d856f3693d402f52b2"></a>

### G013

After the search, write that response's total value to local count\.txt\.

<pre>{
  &quot;id&quot;: &quot;G013&quot;,
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;target_id&quot;: &quot;demand_target_cb3eb1f9d9b790aeb342&quot;,
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;expected&quot;: {
    &quot;kind&quot;: &quot;input&quot;,
    &quot;index&quot;: 1
  },
  &quot;expected_path&quot;: [],
  &quot;reason&quot;: &quot;Preserve only the specified saved total value.&quot;
}</pre>

<details><summary>Existing Task evidence and binding</summary><pre>{
  &quot;id&quot;: &quot;R007&quot;,
  &quot;text&quot;: &quot;After the search, write that response&#x27;s total value to local count.txt.&quot;,
  &quot;evidences&quot;: [
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 21,
      &quot;end_line&quot;: 21,
      &quot;reason&quot;: &quot;The side effect names a specific response field and destination.&quot;
    }
  ],
  &quot;bindings&quot;: [
    {
      &quot;target_id&quot;: &quot;target_0338c293f4218e102429&quot;,
      &quot;reason&quot;: &quot;This is the extracted total from the search response.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_7059117d893e83168a4a&quot;,
      &quot;reason&quot;: &quot;This is the actual saved value; extra response content is not made required.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_ce5dc739e4eaf2527fce&quot;,
      &quot;reason&quot;: &quot;This is the required count-file destination.&quot;
    }
  ]
}</pre></details>

<a id="goal-3fc4dee2a249e8085f2e"></a>

### G014

Return that search response's items value unchanged\.

<pre>{
  &quot;id&quot;: &quot;G014&quot;,
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;target_id&quot;: &quot;target_33cc6c103c883f7b96d1&quot;,
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;expected&quot;: null,
  &quot;expected_path&quot;: [],
  &quot;reason&quot;: &quot;Ordinary return preserves this search response&#x27;s items identity without a fabricated delivery event.&quot;
}</pre>

<details><summary>Existing Task evidence and binding</summary><pre>{
  &quot;id&quot;: &quot;R008&quot;,
  &quot;text&quot;: &quot;Return that search response&#x27;s items value unchanged.&quot;,
  &quot;evidences&quot;: [
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 23,
      &quot;end_line&quot;: 23,
      &quot;reason&quot;: &quot;The requirement is the items field, not the complete response.&quot;
    }
  ],
  &quot;bindings&quot;: [
    {
      &quot;target_id&quot;: &quot;target_a312bfa5142fb9403867&quot;,
      &quot;reason&quot;: &quot;This binds the items extraction result.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_33cc6c103c883f7b96d1&quot;,
      &quot;reason&quot;: &quot;Ordinary return is represented by its actual input; no public output or user-delivery event is invented.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_6227194f4845b13f8abb&quot;,
      &quot;reason&quot;: &quot;The return must preserve the original items value.&quot;
    }
  ]
}</pre></details>

<a id="restrictions"></a>

## Retained task restrictions

Retained review context; not executable or verified predicates. These task restrictions remain available for review across sink comparisons. Their listing does not establish a per-sink scope or that a restriction was satisfied.

- [G001](#goal-dd31ffb1f533a2fabe0b): Use the user\-supplied request\.json, including term and any present from\_date and limit values\.
- [G004](#goal-ee29196b43aae6ee7ca2): Call index\.search exactly once, passing request\.term unchanged as query\.
- [G009](#goal-53390a422ba1a1ffae9b): Do not invoke index\.delete anywhere in this workflow\.
- [G010](#goal-ca4a3f6911afb92edb12): Do not introduce fuzzy expansion, pre\-call validation, or normalization from capability or parameter descriptions\.
- [G011](#goal-12ff945ce0aeacac1892): Do not introduce fuzzy expansion, pre\-call validation, or normalization from capability or parameter descriptions\.

## Sink comparisons

Payload slots retain parameter order and candidate identity. No established demand does not automatically authorize deletion.

<a id="sink-a68b00a635d36793a644"></a>

### sink\_14b0b8b7ce7067b325c4

[Shared retained task restrictions](#restrictions)

#### Current boundary

<pre>{
  &quot;instruction_id&quot;: &quot;ir_007&quot;,
  &quot;event_index&quot;: 6,
  &quot;op_index&quot;: 0,
  &quot;body_event_index&quot;: null,
  &quot;scope&quot;: null,
  &quot;target&quot;: &quot;__compiled_model_context__&quot;,
  &quot;sink_type&quot;: &quot;model_observe&quot;,
  &quot;exposure_level&quot;: 2
}</pre>

#### Actual payload

<pre>[
  {
    &quot;operation_id&quot;: &quot;op_ir_007:e6:a0&quot;,
    &quot;position&quot;: {
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;event_index&quot;: 6,
      &quot;op_index&quot;: 0,
      &quot;body_event_index&quot;: null,
      &quot;instance_index&quot;: null
    },
    &quot;inputs&quot;: [
      [
        &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
        &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
        &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
        &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;
      ]
    ]
  }
]</pre>

#### Demand-driving requirements

- **R007:** After the search, write that response's total value to local count\.txt\.

- **R008:** Return that search response's items value unchanged\.

#### Rule-supported demand

| Task | Information to preserve | Use position | Rule and derivation |
| --- | --- | --- | --- |
| R007 | Value at \["total"\] | ir\_007 / op\_input / slot 0 | processing\_boundary [demand\_2f172ee7a4e2e697a4cd](#derivation-a214c9ea0f16bff8c3ce) |
| R008 | Value at \["items"\] | ir\_007 / op\_input / slot 0 | processing\_boundary [demand\_bff860b7dc91334e5042](#derivation-12080433b444da4861a3) |

#### Conservative retention

No entries in this category.

#### Payload ranges without established demand

<pre>[
  {
    &quot;operation_id&quot;: &quot;op_ir_007:e6:a0&quot;,
    &quot;input_index&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
      &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
      &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
      &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;
    ],
    &quot;description&quot;: &quot;Requirements constrain only the listed information properties. Preserve structure and all listed demands; no replacement execution was verified.&quot;,
    &quot;scope&quot;: &quot;outside_listed_properties&quot;
  }
]</pre>

#### Analysis limitations

<pre>[]</pre>

<a id="sink-60f5a561ec8b8893c53a"></a>

### sink\_431a0c1fa101e978cc88

[Shared retained task restrictions](#restrictions)

#### Current boundary

<pre>{
  &quot;instruction_id&quot;: &quot;ir_007&quot;,
  &quot;event_index&quot;: 1,
  &quot;op_index&quot;: 0,
  &quot;body_event_index&quot;: null,
  &quot;scope&quot;: null,
  &quot;target&quot;: &quot;__compiled_model_context__&quot;,
  &quot;sink_type&quot;: &quot;model_observe&quot;,
  &quot;exposure_level&quot;: 2
}</pre>

#### Actual payload

<pre>[
  {
    &quot;operation_id&quot;: &quot;op_ir_007:e1:a0&quot;,
    &quot;position&quot;: {
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;event_index&quot;: 1,
      &quot;op_index&quot;: 0,
      &quot;body_event_index&quot;: null,
      &quot;instance_index&quot;: null
    },
    &quot;inputs&quot;: [
      [
        &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
      ]
    ]
  }
]</pre>

#### Demand-driving requirements

- **R003:** Pass from\_date unchanged only when present; omit the argument when absent\. Its stated accepted format does not request a preprocessing step\.

- **R007:** After the search, write that response's total value to local count\.txt\.

- **R008:** Return that search response's items value unchanged\.

#### Rule-supported demand

| Task | Information to preserve | Use position | Rule and derivation |
| --- | --- | --- | --- |
| R003 | Condition outcome \(whole referenced value\) | ir\_007 / op\_input / slot 1 | conditional\_observation [demand\_09d6ec65d99b55ebf769](#derivation-4f3b54af69bfc8e0ad9e) |
| R003 | Value \(whole referenced value\) | ir\_007 / op\_input / slot 0 | processing\_boundary [demand\_d3b5044605c1160166e0](#derivation-b8b93cbbdb9866f6665e) |

#### Conservative retention

| Task | Information to preserve | Use position | Rule and derivation |
| --- | --- | --- | --- |
| R008 | Value \(whole referenced value\) | ir\_007 / op\_input / slot 0 | processing\_boundary [demand\_4d366363de94f81993ac](#derivation-cfc00dba175008ec7fdb) |
| R007 | Value \(whole referenced value\) | ir\_007 / op\_input / slot 0 | processing\_boundary [demand\_5e84bcfe3e0c4316cf23](#derivation-4a6054856d978a349d46) |
| R008 | Condition outcome \(whole referenced value\) | ir\_007 / op\_input / slot 1 | conditional\_observation [demand\_73a52b5ebb8866e71559](#derivation-8260aaf28a5c82a27da2) |
| R007 | Condition outcome \(whole referenced value\) | ir\_007 / op\_input / slot 1 | conditional\_observation [demand\_f504c504335f0e95ec33](#derivation-720f29bdd8e5448ac8bd) |

#### Payload ranges without established demand

<pre>[]</pre>

#### Analysis limitations

<pre>[]</pre>

<a id="sink-0a941bb39e637a7d4d5b"></a>

### sink\_4c227ba36482bf5e5a54

[Shared retained task restrictions](#restrictions)

#### Current boundary

<pre>{
  &quot;instruction_id&quot;: &quot;ir_011&quot;,
  &quot;event_index&quot;: 0,
  &quot;op_index&quot;: 0,
  &quot;body_event_index&quot;: null,
  &quot;scope&quot;: null,
  &quot;target&quot;: &quot;__compiled_model_context__&quot;,
  &quot;sink_type&quot;: &quot;model_observe&quot;,
  &quot;exposure_level&quot;: 2
}</pre>

#### Actual payload

<pre>[
  {
    &quot;operation_id&quot;: &quot;op_ir_011:e0:a0&quot;,
    &quot;position&quot;: {
      &quot;instruction_id&quot;: &quot;ir_011&quot;,
      &quot;event_index&quot;: 0,
      &quot;op_index&quot;: 0,
      &quot;body_event_index&quot;: null,
      &quot;instance_index&quot;: null
    },
    &quot;inputs&quot;: [
      [
        &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
        &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
        &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
        &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;
      ]
    ]
  }
]</pre>

#### Demand-driving requirements

- **R008:** Return that search response's items value unchanged\.

#### Rule-supported demand

| Task | Information to preserve | Use position | Rule and derivation |
| --- | --- | --- | --- |
| R008 | Value at \["items"\] | ir\_011 / op\_input / slot 0 | processing\_boundary [demand\_e1c12628e1cf671d68dd](#derivation-751e684bda909c2b2029) |

#### Conservative retention

No entries in this category.

#### Payload ranges without established demand

<pre>[
  {
    &quot;operation_id&quot;: &quot;op_ir_011:e0:a0&quot;,
    &quot;input_index&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
      &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
      &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
      &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;
    ],
    &quot;description&quot;: &quot;Requirements constrain only the listed information properties. Preserve structure and all listed demands; no replacement execution was verified.&quot;,
    &quot;scope&quot;: &quot;outside_listed_properties&quot;
  }
]</pre>

#### Analysis limitations

<pre>[]</pre>

<a id="sink-cdfe6e71766a768ad128"></a>

### sink\_5298b9fc4b95bf5e34ac

[Shared retained task restrictions](#restrictions)

#### Current boundary

<pre>{
  &quot;instruction_id&quot;: &quot;ir_004&quot;,
  &quot;event_index&quot;: 0,
  &quot;op_index&quot;: 0,
  &quot;body_event_index&quot;: null,
  &quot;scope&quot;: null,
  &quot;target&quot;: &quot;__compiled_model_context__&quot;,
  &quot;sink_type&quot;: &quot;model_observe&quot;,
  &quot;exposure_level&quot;: 2
}</pre>

#### Actual payload

<pre>[
  {
    &quot;operation_id&quot;: &quot;op_ir_004:e0:a0&quot;,
    &quot;position&quot;: {
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;event_index&quot;: 0,
      &quot;op_index&quot;: 0,
      &quot;body_event_index&quot;: null,
      &quot;instance_index&quot;: null
    },
    &quot;inputs&quot;: [
      [
        &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
      ]
    ]
  }
]</pre>

#### Demand-driving requirements

- **R003:** Pass from\_date unchanged only when present; omit the argument when absent\. Its stated accepted format does not request a preprocessing step\.

- **R007:** After the search, write that response's total value to local count\.txt\.

- **R008:** Return that search response's items value unchanged\.

#### Rule-supported demand

| Task | Information to preserve | Use position | Rule and derivation |
| --- | --- | --- | --- |
| R003 | Presence at \["from\_date"\] | ir\_004 / op\_input / slot 0 | processing\_boundary [demand\_49809e00993fd3298c90](#derivation-6f2f2cb7ac3df78a08a0) |
| R003 | Value at \["from\_date"\] | ir\_004 / op\_input / slot 0 | processing\_boundary [demand\_a99abaf590a5bc6642ba](#derivation-80cf3274b11467d8b27c) |

#### Conservative retention

| Task | Information to preserve | Use position | Rule and derivation |
| --- | --- | --- | --- |
| R007 | Value at \["from\_date"\] | ir\_004 / op\_input / slot 0 | processing\_boundary [demand\_2f662c212c5a996b9a93](#derivation-fa5a59325dd6974fc3f5) |
| R007 | Presence at \["from\_date"\] | ir\_004 / op\_input / slot 0 | processing\_boundary [demand\_778cb0387e39f0c9f5a2](#derivation-59a933033b79f0f43347) |
| R008 | Presence at \["from\_date"\] | ir\_004 / op\_input / slot 0 | processing\_boundary [demand\_c311dd9af991af51f870](#derivation-6bba669ac1ae951639d2) |
| R008 | Value at \["from\_date"\] | ir\_004 / op\_input / slot 0 | processing\_boundary [demand\_e8047654aa6bff17f62f](#derivation-0ee4483550b2a603bbb5) |

#### Payload ranges without established demand

<pre>[
  {
    &quot;operation_id&quot;: &quot;op_ir_004:e0:a0&quot;,
    &quot;input_index&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ],
    &quot;description&quot;: &quot;Requirements constrain only the listed information properties. Preserve structure and all listed demands; no replacement execution was verified.&quot;,
    &quot;scope&quot;: &quot;outside_listed_properties&quot;
  }
]</pre>

#### Analysis limitations

<pre>[]</pre>

<a id="sink-6cefc8af8351d0961713"></a>

### sink\_5b7883aa5bd512f9c0b3

[Shared retained task restrictions](#restrictions)

#### Current boundary

<pre>{
  &quot;instruction_id&quot;: &quot;ir_007&quot;,
  &quot;event_index&quot;: 4,
  &quot;op_index&quot;: 0,
  &quot;body_event_index&quot;: null,
  &quot;scope&quot;: null,
  &quot;target&quot;: &quot;loc_index_search&quot;,
  &quot;sink_type&quot;: &quot;external_tool&quot;,
  &quot;exposure_level&quot;: 2
}</pre>

#### Actual payload

<pre>[
  {
    &quot;operation_id&quot;: &quot;op_ir_007:e4:a0&quot;,
    &quot;position&quot;: {
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;event_index&quot;: 4,
      &quot;op_index&quot;: 0,
      &quot;body_event_index&quot;: null,
      &quot;instance_index&quot;: null
    },
    &quot;inputs&quot;: [
      [
        &quot;data_04977d052e12894e8e9c0a137fd39df74fb642c40353e8fa497f9efb4135badb&quot;,
        &quot;data_8276fb1f277efeb717aae1eb89fad8dc9851725a894ffffdbbdd00e6f260e56c&quot;,
        &quot;data_94cfb94a16886ab61be49175ee8bddb2882c306a6969a0769d12f3a2ad7be9c2&quot;,
        &quot;data_c151aa225e154341fe56b24f3f7e3b657a75ec1230aab5c985ba811572e96383&quot;
      ]
    ]
  }
]</pre>

#### Demand-driving requirements

- **R002:** Call index\.search exactly once, passing request\.term unchanged as query\.

- **R003:** Pass from\_date unchanged only when present; omit the argument when absent\. Its stated accepted format does not request a preprocessing step\.

- **R004:** Pass limit unchanged only when present; omit the argument when absent\.

- **R007:** After the search, write that response's total value to local count\.txt\.

- **R008:** Return that search response's items value unchanged\.

#### Rule-supported demand

| Task | Information to preserve | Use position | Rule and derivation |
| --- | --- | --- | --- |
| R003 | Presence at \["from\_date"\] | ir\_007 / op\_input / slot 0 | task\_value [demand\_3d98da9857708568385e](#derivation-b91902998d2498636e33) |
| R002 | Value at \["query"\] | ir\_007 / op\_input / slot 0 | task\_expected\_relation [demand\_7152da4555f1e0b354f7](#derivation-afcae62f4c76114757c5) |
| R002 | Required behavior \(whole referenced value\) | ir\_007 / action | task\_action [demand\_76a95debf4852e739d4e](#derivation-378a0fe72a8fac3360ce) |
| R003 | Value at \["from\_date"\] | ir\_007 / op\_input / slot 0 | task\_expected\_relation [demand\_770f8357df9eea9bcbd1](#derivation-2c936773892d338bd20f) |
| R008 | Required behavior \(whole referenced value\) | ir\_007 / action | required\_acquisition [demand\_7c0060421bcacf0320c4](#derivation-cd537109fd785dac5dec) |
| R004 | Presence at \["limit"\] | ir\_007 / op\_input / slot 0 | task\_value [demand\_b4e3f1504bb12bf3c101](#derivation-93ace520e1cfb34eec70) |
| R004 | Value at \["limit"\] | ir\_007 / op\_input / slot 0 | task\_expected\_relation [demand\_b80fcaba1d3cb69a64ec](#derivation-0e7f5ea4524e4c04aa56) |
| R007 | Required behavior \(whole referenced value\) | ir\_007 / action | required\_acquisition [demand\_bfc939197c77ad301f6e](#derivation-715e18d9b8dfa1a15cd4) |

#### Conservative retention

| Task | Information to preserve | Use position | Rule and derivation |
| --- | --- | --- | --- |
| R008 | Value \(whole referenced value\) | ir\_007 / op\_input / slot 0 | external\_request\_retained [demand\_0d21c9e8ece1c99119bb](#derivation-bcc5713c43c4c7dd184c) |
| R007 | Value \(whole referenced value\) | ir\_007 / op\_input / slot 0 | external\_request\_retained [demand\_ba9ad30c0f71261d761c](#derivation-c0a379b75688e3e6016b) |

#### Payload ranges without established demand

<pre>[]</pre>

#### Analysis limitations

<pre>[]</pre>

<a id="sink-4e5a6e646e28bd1de2cb"></a>

### sink\_6982d6acfff5c4808d1f

[Shared retained task restrictions](#restrictions)

#### Current boundary

<pre>{
  &quot;instruction_id&quot;: &quot;ir_007&quot;,
  &quot;event_index&quot;: 0,
  &quot;op_index&quot;: 0,
  &quot;body_event_index&quot;: null,
  &quot;scope&quot;: null,
  &quot;target&quot;: &quot;__compiled_model_context__&quot;,
  &quot;sink_type&quot;: &quot;model_observe&quot;,
  &quot;exposure_level&quot;: 2
}</pre>

#### Actual payload

<pre>[
  {
    &quot;operation_id&quot;: &quot;op_ir_007:e0:a0&quot;,
    &quot;position&quot;: {
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;event_index&quot;: 0,
      &quot;op_index&quot;: 0,
      &quot;body_event_index&quot;: null,
      &quot;instance_index&quot;: null
    },
    &quot;inputs&quot;: [
      [
        &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
      ],
      [
        &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
      ],
      [
        &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
      ]
    ]
  }
]</pre>

#### Demand-driving requirements

- **R002:** Call index\.search exactly once, passing request\.term unchanged as query\.

- **R003:** Pass from\_date unchanged only when present; omit the argument when absent\. Its stated accepted format does not request a preprocessing step\.

- **R004:** Pass limit unchanged only when present; omit the argument when absent\.

- **R007:** After the search, write that response's total value to local count\.txt\.

- **R008:** Return that search response's items value unchanged\.

#### Rule-supported demand

| Task | Information to preserve | Use position | Rule and derivation |
| --- | --- | --- | --- |
| R003 | Condition outcome \(whole referenced value\) | ir\_007 / op\_input / slot 1 | processing\_boundary [demand\_31b579606595406d5703](#derivation-f7e07220adc8182b2b55) |
| R002 | Value \(whole referenced value\) | ir\_007 / op\_input / slot 0 | processing\_boundary [demand\_b5ec715878877301c884](#derivation-ee082435232ff1e8e022) |
| R004 | Condition outcome \(whole referenced value\) | ir\_007 / op\_input / slot 2 | processing\_boundary [demand\_e3f1e82a9022edf7445b](#derivation-90a0212d9bf8ab3da6ac) |

#### Conservative retention

| Task | Information to preserve | Use position | Rule and derivation |
| --- | --- | --- | --- |
| R008 | Value \(whole referenced value\) | ir\_007 / op\_input / slot 0 | processing\_boundary [demand\_3378fb51950f65e5be8a](#derivation-8dfd3af70af19d841320) |
| R007 | Condition outcome \(whole referenced value\) | ir\_007 / op\_input / slot 2 | processing\_boundary [demand\_588b7f1db144c74a771a](#derivation-94cedfa8f1d8ca0101cf) |
| R008 | Condition outcome \(whole referenced value\) | ir\_007 / op\_input / slot 1 | processing\_boundary [demand\_5d93a00a900eaa207c71](#derivation-11c40a1cf4f8511e525a) |
| R007 | Value \(whole referenced value\) | ir\_007 / op\_input / slot 0 | processing\_boundary [demand\_73ae1d77566a9696778f](#derivation-1608f50b2898161ee53e) |
| R008 | Condition outcome \(whole referenced value\) | ir\_007 / op\_input / slot 2 | processing\_boundary [demand\_8c77ea65ddfd5264b67d](#derivation-8b096482a9f2204ecf19) |
| R007 | Condition outcome \(whole referenced value\) | ir\_007 / op\_input / slot 1 | processing\_boundary [demand\_c33596ff7a7281694f4f](#derivation-80a2a7e7b59d40e2a00a) |

#### Payload ranges without established demand

<pre>[
  {
    &quot;operation_id&quot;: &quot;op_ir_007:e0:a0&quot;,
    &quot;input_index&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
    ],
    &quot;description&quot;: &quot;Requirements constrain only the listed information properties. Preserve structure and all listed demands; no replacement execution was verified.&quot;,
    &quot;scope&quot;: &quot;outside_listed_properties&quot;
  },
  {
    &quot;operation_id&quot;: &quot;op_ir_007:e0:a0&quot;,
    &quot;input_index&quot;: 2,
    &quot;data_ids&quot;: [
      &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
    ],
    &quot;description&quot;: &quot;Requirements constrain only the listed information properties. Preserve structure and all listed demands; no replacement execution was verified.&quot;,
    &quot;scope&quot;: &quot;outside_listed_properties&quot;
  }
]</pre>

#### Analysis limitations

<pre>[]</pre>

<a id="sink-3ba586042e58c59af3ef"></a>

### sink\_836d6bb37efb1eefe31e

[Shared retained task restrictions](#restrictions)

#### Current boundary

<pre>{
  &quot;instruction_id&quot;: &quot;ir_005&quot;,
  &quot;event_index&quot;: 0,
  &quot;op_index&quot;: 0,
  &quot;body_event_index&quot;: null,
  &quot;scope&quot;: null,
  &quot;target&quot;: &quot;__compiled_model_context__&quot;,
  &quot;sink_type&quot;: &quot;model_observe&quot;,
  &quot;exposure_level&quot;: 2
}</pre>

#### Actual payload

<pre>[
  {
    &quot;operation_id&quot;: &quot;op_ir_005:e0:a0&quot;,
    &quot;position&quot;: {
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;event_index&quot;: 0,
      &quot;op_index&quot;: 0,
      &quot;body_event_index&quot;: null,
      &quot;instance_index&quot;: null
    },
    &quot;inputs&quot;: [
      [
        &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
      ]
    ]
  }
]</pre>

#### Demand-driving requirements

- **R004:** Pass limit unchanged only when present; omit the argument when absent\.

- **R007:** After the search, write that response's total value to local count\.txt\.

- **R008:** Return that search response's items value unchanged\.

#### Rule-supported demand

| Task | Information to preserve | Use position | Rule and derivation |
| --- | --- | --- | --- |
| R004 | Presence at \["limit"\] | ir\_005 / op\_input / slot 0 | processing\_boundary [demand\_30647d87deec5e8c9872](#derivation-fec57f730ccb2b2c76b3) |
| R004 | Value at \["limit"\] | ir\_005 / op\_input / slot 0 | processing\_boundary [demand\_bbcc0f5a6503524e10e8](#derivation-c66c2e6e619ee3684438) |

#### Conservative retention

| Task | Information to preserve | Use position | Rule and derivation |
| --- | --- | --- | --- |
| R007 | Presence at \["limit"\] | ir\_005 / op\_input / slot 0 | processing\_boundary [demand\_b286f779d7abe4ebe3c6](#derivation-7aa0259b7e7b224d743a) |
| R008 | Value at \["limit"\] | ir\_005 / op\_input / slot 0 | processing\_boundary [demand\_b53391f0f7d5f71e91fe](#derivation-726ac26561cd7d977030) |
| R008 | Presence at \["limit"\] | ir\_005 / op\_input / slot 0 | processing\_boundary [demand\_c406707838ff2b9369d5](#derivation-535230253f21625ba152) |
| R007 | Value at \["limit"\] | ir\_005 / op\_input / slot 0 | processing\_boundary [demand\_f4e464ac72de50af9767](#derivation-99c99979addc22a0048a) |

#### Payload ranges without established demand

<pre>[
  {
    &quot;operation_id&quot;: &quot;op_ir_005:e0:a0&quot;,
    &quot;input_index&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ],
    &quot;description&quot;: &quot;Requirements constrain only the listed information properties. Preserve structure and all listed demands; no replacement execution was verified.&quot;,
    &quot;scope&quot;: &quot;outside_listed_properties&quot;
  }
]</pre>

#### Analysis limitations

<pre>[]</pre>

<a id="sink-9244162a65f1dab10c01"></a>

### sink\_8632d255f8657b506825

[Shared retained task restrictions](#restrictions)

#### Current boundary

<pre>{
  &quot;instruction_id&quot;: &quot;ir_003&quot;,
  &quot;event_index&quot;: 0,
  &quot;op_index&quot;: 0,
  &quot;body_event_index&quot;: null,
  &quot;scope&quot;: null,
  &quot;target&quot;: &quot;__compiled_model_context__&quot;,
  &quot;sink_type&quot;: &quot;model_observe&quot;,
  &quot;exposure_level&quot;: 2
}</pre>

#### Actual payload

<pre>[
  {
    &quot;operation_id&quot;: &quot;op_ir_003:e0:a0&quot;,
    &quot;position&quot;: {
      &quot;instruction_id&quot;: &quot;ir_003&quot;,
      &quot;event_index&quot;: 0,
      &quot;op_index&quot;: 0,
      &quot;body_event_index&quot;: null,
      &quot;instance_index&quot;: null
    },
    &quot;inputs&quot;: [
      [
        &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
      ]
    ]
  }
]</pre>

#### Demand-driving requirements

- **R002:** Call index\.search exactly once, passing request\.term unchanged as query\.

- **R007:** After the search, write that response's total value to local count\.txt\.

- **R008:** Return that search response's items value unchanged\.

#### Rule-supported demand

| Task | Information to preserve | Use position | Rule and derivation |
| --- | --- | --- | --- |
| R002 | Value at \["term"\] | ir\_003 / op\_input / slot 0 | processing\_boundary [demand\_8223fe328a0a4a78bb8f](#derivation-6ac43f8e59fb9b763b90) |

#### Conservative retention

| Task | Information to preserve | Use position | Rule and derivation |
| --- | --- | --- | --- |
| R008 | Value at \["term"\] | ir\_003 / op\_input / slot 0 | processing\_boundary [demand\_db127be777f1a636a74b](#derivation-e00cedb6dbd758b75e86) |
| R007 | Value at \["term"\] | ir\_003 / op\_input / slot 0 | processing\_boundary [demand\_e3c98c7288aa69a5864b](#derivation-487c3bc68fc5f1141110) |

#### Payload ranges without established demand

<pre>[
  {
    &quot;operation_id&quot;: &quot;op_ir_003:e0:a0&quot;,
    &quot;input_index&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ],
    &quot;description&quot;: &quot;Requirements constrain only the listed information properties. Preserve structure and all listed demands; no replacement execution was verified.&quot;,
    &quot;scope&quot;: &quot;outside_listed_properties&quot;
  }
]</pre>

#### Analysis limitations

<pre>[]</pre>

<a id="sink-e769559260c304bdb061"></a>

### sink\_9a3c4449a80a0bfeb411

[Shared retained task restrictions](#restrictions)

#### Current boundary

<pre>{
  &quot;instruction_id&quot;: &quot;ir_009&quot;,
  &quot;event_index&quot;: 0,
  &quot;op_index&quot;: 0,
  &quot;body_event_index&quot;: null,
  &quot;scope&quot;: null,
  &quot;target&quot;: &quot;__compiled_model_context__&quot;,
  &quot;sink_type&quot;: &quot;model_observe&quot;,
  &quot;exposure_level&quot;: 2
}</pre>

#### Actual payload

<pre>[
  {
    &quot;operation_id&quot;: &quot;op_ir_009:e0:a0&quot;,
    &quot;position&quot;: {
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;event_index&quot;: 0,
      &quot;op_index&quot;: 0,
      &quot;body_event_index&quot;: null,
      &quot;instance_index&quot;: null
    },
    &quot;inputs&quot;: [
      [
        &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
        &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
        &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
        &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;
      ]
    ]
  }
]</pre>

#### Demand-driving requirements

- **R007:** After the search, write that response's total value to local count\.txt\.

#### Rule-supported demand

| Task | Information to preserve | Use position | Rule and derivation |
| --- | --- | --- | --- |
| R007 | Value at \["total"\] | ir\_009 / op\_input / slot 0 | processing\_boundary [demand\_bad4aba5fc5149222095](#derivation-e11750a84758c846c0c1) |

#### Conservative retention

No entries in this category.

#### Payload ranges without established demand

<pre>[
  {
    &quot;operation_id&quot;: &quot;op_ir_009:e0:a0&quot;,
    &quot;input_index&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
      &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
      &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
      &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;
    ],
    &quot;description&quot;: &quot;Requirements constrain only the listed information properties. Preserve structure and all listed demands; no replacement execution was verified.&quot;,
    &quot;scope&quot;: &quot;outside_listed_properties&quot;
  }
]</pre>

#### Analysis limitations

<pre>[]</pre>

<a id="sink-1be37cbabd2315fd8a87"></a>

### sink\_b49311cac3371bac7f82

[Shared retained task restrictions](#restrictions)

#### Current boundary

<pre>{
  &quot;instruction_id&quot;: &quot;ir_010&quot;,
  &quot;event_index&quot;: 0,
  &quot;op_index&quot;: 0,
  &quot;body_event_index&quot;: null,
  &quot;scope&quot;: null,
  &quot;target&quot;: &quot;loc_count_txt&quot;,
  &quot;sink_type&quot;: &quot;storage_write&quot;,
  &quot;exposure_level&quot;: 1
}</pre>

#### Actual payload

<pre>[
  {
    &quot;operation_id&quot;: &quot;op_ir_010:e0:a0&quot;,
    &quot;position&quot;: {
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;event_index&quot;: 0,
      &quot;op_index&quot;: 0,
      &quot;body_event_index&quot;: null,
      &quot;instance_index&quot;: null
    },
    &quot;inputs&quot;: [
      [
        &quot;data_3c59631c7c944a1e5dc7bdb966c272cd355ff20dcdeb6d07906e4547746e1169&quot;,
        &quot;data_5bd0761d4780c33b8f014a0a65282b7460a295319cf205b06a923dd49f8d2594&quot;,
        &quot;data_5d32e16a7f2d66a941ff4ff820ed14a18a1b0ca5bbb2e568b6a33171729a62e9&quot;,
        &quot;data_b82b2e7fc2d1815522bc8e967ffc709aae6daf50b6b234c9b176a1bf6d4b246a&quot;
      ]
    ]
  }
]</pre>

#### Demand-driving requirements

- **R007:** After the search, write that response's total value to local count\.txt\.

#### Rule-supported demand

| Task | Information to preserve | Use position | Rule and derivation |
| --- | --- | --- | --- |
| R007 | Required behavior \(whole referenced value\) | ir\_010 / action | task\_action [demand\_9a8f570e3c654eb1ee42](#derivation-de985751879569efb1fe) |
| R007 | Value \(whole referenced value\) | ir\_010 / op\_input / slot 0 | task\_expected\_relation [demand\_b307a49044f63b65253d](#derivation-0b46ed13fd4cab9fdf76) |

#### Conservative retention

No entries in this category.

#### Payload ranges without established demand

<pre>[]</pre>

#### Analysis limitations

<pre>[]</pre>

<a id="sink-6c8495df7975f7014a02"></a>

### sink\_c2397cb75735b4bbf5ed

[Shared retained task restrictions](#restrictions)

#### Current boundary

<pre>{
  &quot;instruction_id&quot;: &quot;ir_001&quot;,
  &quot;event_index&quot;: 1,
  &quot;op_index&quot;: 0,
  &quot;body_event_index&quot;: null,
  &quot;scope&quot;: null,
  &quot;target&quot;: &quot;__compiled_model_context__&quot;,
  &quot;sink_type&quot;: &quot;model_observe&quot;,
  &quot;exposure_level&quot;: 2
}</pre>

#### Actual payload

<pre>[
  {
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;position&quot;: {
      &quot;instruction_id&quot;: &quot;ir_001&quot;,
      &quot;event_index&quot;: 1,
      &quot;op_index&quot;: 0,
      &quot;body_event_index&quot;: null,
      &quot;instance_index&quot;: null
    },
    &quot;inputs&quot;: [
      [
        &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
      ]
    ]
  }
]</pre>

#### Demand-driving requirements

- **R002:** Call index\.search exactly once, passing request\.term unchanged as query\.

- **R003:** Pass from\_date unchanged only when present; omit the argument when absent\. Its stated accepted format does not request a preprocessing step\.

- **R004:** Pass limit unchanged only when present; omit the argument when absent\.

- **R007:** After the search, write that response's total value to local count\.txt\.

- **R008:** Return that search response's items value unchanged\.

#### Rule-supported demand

| Task | Information to preserve | Use position | Rule and derivation |
| --- | --- | --- | --- |
| R003 | Presence at \["from\_date"\] | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_568ad54ffa69d22b3e96](#derivation-6bcfa2868227db02975a) |
| R002 | Value at \["term"\] | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_6d310e1a296e12fe6082](#derivation-bcf083a3d2f5480568dd) |
| R004 | Value at \["limit"\] | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_b7ec1e84454c1a18f384](#derivation-ba50e08ada050126ef8d) |
| R004 | Presence at \["limit"\] | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_dcd59f59ba5ecf26f0b2](#derivation-be16e8d8f6ba9b815a2d) |
| R003 | Value at \["from\_date"\] | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_fce49c40b6a6c62be83f](#derivation-8d05633bc06d880eb515) |

#### Conservative retention

| Task | Information to preserve | Use position | Rule and derivation |
| --- | --- | --- | --- |
| R008 | Value at \["term"\] | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_4548d148e701318d8376](#derivation-c8862a0382ce8eef96bd) |
| R008 | Presence at \["from\_date"\] | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_5011bdb0839eb1db8f5f](#derivation-4ca67f31b011cd2f3afe) |
| R007 | Value at \["from\_date"\] | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_94a26ae9bddbfb8eca23](#derivation-0e52dad3fd9278e38666) |
| R007 | Value at \["limit"\] | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_9dc47e97a4fa6ca40d85](#derivation-37f5b689da1f5beb088b) |
| R008 | Value at \["from\_date"\] | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_bc79b3add08ddaf4dd01](#derivation-4e3fed4139a277b7a43d) |
| R007 | Value at \["term"\] | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_bf666375e380c823c702](#derivation-97f09b783ed3c9b2c7f8) |
| R007 | Presence at \["from\_date"\] | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_cbb989e7a266e3f66a0e](#derivation-315fa10b285d89f2fde3) |
| R008 | Value at \["limit"\] | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_df6c35a9003c5782def0](#derivation-101b1685a8ffde1fce60) |
| R008 | Presence at \["limit"\] | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_ebec4ea2896736a03704](#derivation-201667d65099cbad2600) |
| R007 | Presence at \["limit"\] | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_ed52af0fd937f879f815](#derivation-d1c83461572dfb17763d) |

#### Payload ranges without established demand

<pre>[
  {
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;input_index&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ],
    &quot;description&quot;: &quot;Requirements constrain only the listed information properties. Preserve structure and all listed demands; no replacement execution was verified.&quot;,
    &quot;scope&quot;: &quot;outside_listed_properties&quot;
  }
]</pre>

#### Analysis limitations

<pre>[]</pre>

<a id="sink-24bbf7ef75e8a7d9b932"></a>

### sink\_ce54588f3e0fbdcec0e6

[Shared retained task restrictions](#restrictions)

#### Current boundary

<pre>{
  &quot;instruction_id&quot;: &quot;ir_007&quot;,
  &quot;event_index&quot;: 2,
  &quot;op_index&quot;: 0,
  &quot;body_event_index&quot;: null,
  &quot;scope&quot;: null,
  &quot;target&quot;: &quot;__compiled_model_context__&quot;,
  &quot;sink_type&quot;: &quot;model_observe&quot;,
  &quot;exposure_level&quot;: 2
}</pre>

#### Actual payload

<pre>[
  {
    &quot;operation_id&quot;: &quot;op_ir_007:e2:a0&quot;,
    &quot;position&quot;: {
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;event_index&quot;: 2,
      &quot;op_index&quot;: 0,
      &quot;body_event_index&quot;: null,
      &quot;instance_index&quot;: null
    },
    &quot;inputs&quot;: [
      [
        &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
      ]
    ]
  }
]</pre>

#### Demand-driving requirements

- **R004:** Pass limit unchanged only when present; omit the argument when absent\.

- **R007:** After the search, write that response's total value to local count\.txt\.

- **R008:** Return that search response's items value unchanged\.

#### Rule-supported demand

| Task | Information to preserve | Use position | Rule and derivation |
| --- | --- | --- | --- |
| R004 | Condition outcome \(whole referenced value\) | ir\_007 / op\_input / slot 1 | conditional\_observation [demand\_8f6c9eaabc5af2d49c37](#derivation-bb7d8ec5bdcbf7eb4c7b) |
| R004 | Value \(whole referenced value\) | ir\_007 / op\_input / slot 0 | processing\_boundary [demand\_d1a9f5a027f71cf5f37f](#derivation-2f39f266436f75ab4e93) |

#### Conservative retention

| Task | Information to preserve | Use position | Rule and derivation |
| --- | --- | --- | --- |
| R008 | Value \(whole referenced value\) | ir\_007 / op\_input / slot 0 | processing\_boundary [demand\_1571b282b1cc3480be38](#derivation-41babb1667753378607c) |
| R008 | Condition outcome \(whole referenced value\) | ir\_007 / op\_input / slot 1 | conditional\_observation [demand\_5cb3c1ed63a29acc81e0](#derivation-a58daef5239c94a216cf) |
| R007 | Value \(whole referenced value\) | ir\_007 / op\_input / slot 0 | processing\_boundary [demand\_acaf0ec94c39315f5609](#derivation-f2d5cf95d800d776ad9a) |
| R007 | Condition outcome \(whole referenced value\) | ir\_007 / op\_input / slot 1 | conditional\_observation [demand\_b5b4a1eb3efaa1668424](#derivation-a9408af52c1b22cc0f37) |

#### Payload ranges without established demand

<pre>[]</pre>

#### Analysis limitations

<pre>[]</pre>

## Shared rule derivations

<a id="derivation-e8f2ed9fe0176870303d"></a>

### demand\_0001aeda76e11b764441

<pre>{
  &quot;id&quot;: &quot;demand_0001aeda76e11b764441&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 4,
    &quot;data_ids&quot;: [
      &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;constructed_member&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_fd5c1eb70a6a723c58ad&quot;
  ]
}</pre>

<a id="derivation-dcf0cb6db7e8bb827de6"></a>

### demand\_004b4892406001232339

<pre>{
  &quot;id&quot;: &quot;demand_004b4892406001232339&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e1:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_9216db2340931460b1aa&quot;
  ]
}</pre>

<a id="derivation-d2ee186915a4bf17e574"></a>

### demand\_0088834c70240599d9ce

<pre>{
  &quot;id&quot;: &quot;demand_0088834c70240599d9ce&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_81f1915086c8d574aa16&quot;
  ]
}</pre>

<a id="derivation-4923d4ca7902d357b1f1"></a>

### demand\_011277f3c08d6481b14c

<pre>{
  &quot;id&quot;: &quot;demand_011277f3c08d6481b14c&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_8794b79aca4871a54aea&quot;,
    &quot;demand_94a26ae9bddbfb8eca23&quot;
  ]
}</pre>

<a id="derivation-f0b7358688d52fb19b5f"></a>

### demand\_0141adb0d4592b3adc67

<pre>{
  &quot;id&quot;: &quot;demand_0141adb0d4592b3adc67&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_011&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_12ea329cebb7fb4155ba190a559188e76a986f0a1eb020754003e824f22535a5&quot;,
      &quot;data_31a9dc19c5483e1464b99e4bdd6547c1519117d64e70291a2ad78d0c544160ce&quot;,
      &quot;data_ddcfc654bd05b26d018d1c712cca288a2caceba2b37bc24d3d49faa952553e6a&quot;,
      &quot;data_f04c7c46dcfdf4406afbda7f422fb9b62daa512e862b76f925c8f9c76f0d37e4&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_16ec473131e32492173a&quot;
  ]
}</pre>

<a id="derivation-2cafbe17c044ed8321ac"></a>

### demand\_0310df466313b6d76981

<pre>{
  &quot;id&quot;: &quot;demand_0310df466313b6d76981&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_c7fb0ddc14cc53bedd4a&quot;
  ]
}</pre>

<a id="derivation-631f6b1ecc3179088c1b"></a>

### demand\_037418f9eb471de7b119

<pre>{
  &quot;id&quot;: &quot;demand_037418f9eb471de7b119&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 5,
    &quot;data_ids&quot;: [
      &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_8f6c9eaabc5af2d49c37&quot;,
    &quot;demand_b713cd5cb0285deba88f&quot;,
    &quot;demand_e3f1e82a9022edf7445b&quot;
  ]
}</pre>

<a id="derivation-82cf12f6bfe401112616"></a>

### demand\_0985269a53c1c5a484dc

<pre>{
  &quot;id&quot;: &quot;demand_0985269a53c1c5a484dc&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_b95265387a64bed01a1c&quot;,
    &quot;demand_bc79b3add08ddaf4dd01&quot;
  ]
}</pre>

<a id="derivation-4f3b54af69bfc8e0ad9e"></a>

### demand\_09d6ec65d99b55ebf769

<pre>{
  &quot;id&quot;: &quot;demand_09d6ec65d99b55ebf769&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e1:a0&quot;,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;conditional_observation&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_d3b5044605c1160166e0&quot;
  ]
}</pre>

<a id="derivation-915c7c6e694e215ca550"></a>

### demand\_09daef85513bd2245b89

<pre>{
  &quot;id&quot;: &quot;demand_09daef85513bd2245b89&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_3c31d44c792cca9aca27&quot;,
    &quot;demand_ebec4ea2896736a03704&quot;
  ]
}</pre>

<a id="derivation-7bdab13f29cdd3f02b37"></a>

### demand\_0c572562cca375fcb81c

<pre>{
  &quot;id&quot;: &quot;demand_0c572562cca375fcb81c&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 5,
    &quot;data_ids&quot;: [
      &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_588b7f1db144c74a771a&quot;,
    &quot;demand_962ab148bd3f76131e70&quot;,
    &quot;demand_b5b4a1eb3efaa1668424&quot;
  ]
}</pre>

<a id="derivation-bcc5713c43c4c7dd184c"></a>

### demand\_0d21c9e8ece1c99119bb

<pre>{
  &quot;id&quot;: &quot;demand_0d21c9e8ece1c99119bb&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e4:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_04977d052e12894e8e9c0a137fd39df74fb642c40353e8fa497f9efb4135badb&quot;,
      &quot;data_8276fb1f277efeb717aae1eb89fad8dc9851725a894ffffdbbdd00e6f260e56c&quot;,
      &quot;data_94cfb94a16886ab61be49175ee8bddb2882c306a6969a0769d12f3a2ad7be9c2&quot;,
      &quot;data_c151aa225e154341fe56b24f3f7e3b657a75ec1230aab5c985ba811572e96383&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;external_request_retained&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_ec49381ac390295bdf73&quot;
  ]
}</pre>

<a id="derivation-246f2d8ee81630229649"></a>

### demand\_0ed25450465605d8bdee

<pre>{
  &quot;id&quot;: &quot;demand_0ed25450465605d8bdee&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e5:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_04977d052e12894e8e9c0a137fd39df74fb642c40353e8fa497f9efb4135badb&quot;,
      &quot;data_8276fb1f277efeb717aae1eb89fad8dc9851725a894ffffdbbdd00e6f260e56c&quot;,
      &quot;data_94cfb94a16886ab61be49175ee8bddb2882c306a6969a0769d12f3a2ad7be9c2&quot;,
      &quot;data_c151aa225e154341fe56b24f3f7e3b657a75ec1230aab5c985ba811572e96383&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;external_request_retained&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_ec49381ac390295bdf73&quot;
  ]
}</pre>

<a id="derivation-e62de1a2bd5d9f612754"></a>

### demand\_114a4d4ea6d305d9eade

<pre>{
  &quot;id&quot;: &quot;demand_114a4d4ea6d305d9eade&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_49809e00993fd3298c90&quot;,
    &quot;demand_7abbaea7cb5d29f28d60&quot;
  ]
}</pre>

<a id="derivation-48af6e32d49723bbaf2b"></a>

### demand\_12e579c8e4ba4e2ad8c5

<pre>{
  &quot;id&quot;: &quot;demand_12e579c8e4ba4e2ad8c5&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_e9838adbf3a93290628a&quot;
  ]
}</pre>

<a id="derivation-d58164b0e45d0f6727a9"></a>

### demand\_12ff67812f331399a73c

<pre>{
  &quot;id&quot;: &quot;demand_12ff67812f331399a73c&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_bc1d10125a7b0297df28&quot;
  ]
}</pre>

<a id="derivation-41babb1667753378607c"></a>

### demand\_1571b282b1cc3480be38

<pre>{
  &quot;id&quot;: &quot;demand_1571b282b1cc3480be38&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e2:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_0001aeda76e11b764441&quot;
  ]
}</pre>

<a id="derivation-4449a0d02b512ecf3f0e"></a>

### demand\_16ec473131e32492173a

<pre>{
  &quot;id&quot;: &quot;demand_16ec473131e32492173a&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_012&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_12ea329cebb7fb4155ba190a559188e76a986f0a1eb020754003e824f22535a5&quot;,
      &quot;data_31a9dc19c5483e1464b99e4bdd6547c1519117d64e70291a2ad78d0c544160ce&quot;,
      &quot;data_ddcfc654bd05b26d018d1c712cca288a2caceba2b37bc24d3d49faa952553e6a&quot;,
      &quot;data_f04c7c46dcfdf4406afbda7f422fb9b62daa512e862b76f925c8f9c76f0d37e4&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;task_operand&quot;
  ],
  &quot;parents&quot;: []
}</pre>

<a id="derivation-229dec784d77cb0d749a"></a>

### demand\_17dd7ca30d951bb87f63

<pre>{
  &quot;id&quot;: &quot;demand_17dd7ca30d951bb87f63&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_a99abaf590a5bc6642ba&quot;,
    &quot;demand_d7f0c68b978bf9a2a057&quot;
  ]
}</pre>

<a id="derivation-26888a2069b7ab910ac6"></a>

### demand\_1a321dc33bd0eb3a2915

<pre>{
  &quot;id&quot;: &quot;demand_1a321dc33bd0eb3a2915&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_1a3b2c0384f5e207e0cd&quot;
  ]
}</pre>

<a id="derivation-a533fb71fa4db9873ae9"></a>

### demand\_1a3b2c0384f5e207e0cd

<pre>{
  &quot;id&quot;: &quot;demand_1a3b2c0384f5e207e0cd&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_30647d87deec5e8c9872&quot;,
    &quot;demand_bc4f0460d4e45aa1af15&quot;
  ]
}</pre>

<a id="derivation-766f4d58b71616ff6484"></a>

### demand\_1e311538e0891a4b28db

<pre>{
  &quot;id&quot;: &quot;demand_1e311538e0891a4b28db&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_2b1ce18df1fb9d005e2f&quot;,
    &quot;demand_778cb0387e39f0c9f5a2&quot;
  ]
}</pre>

<a id="derivation-5f343acb87775065cc39"></a>

### demand\_20350eab3a8b9219263c

<pre>{
  &quot;id&quot;: &quot;demand_20350eab3a8b9219263c&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_1e311538e0891a4b28db&quot;
  ]
}</pre>

<a id="derivation-7feb0e7a7818cab0a27a"></a>

### demand\_2454d8dfe06c811c1b8d

<pre>{
  &quot;id&quot;: &quot;demand_2454d8dfe06c811c1b8d&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_562bbddda249bd58cba5&quot;
  ]
}</pre>

<a id="derivation-9463482c99ddc4f63002"></a>

### demand\_24bccf3c0fd1c71d8670

<pre>{
  &quot;id&quot;: &quot;demand_24bccf3c0fd1c71d8670&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_6d310e1a296e12fe6082&quot;,
    &quot;demand_81436ab38ab1ad441869&quot;
  ]
}</pre>

<a id="derivation-ab7af98291d5bd250156"></a>

### demand\_272b1e058e7c58d988ed

<pre>{
  &quot;id&quot;: &quot;demand_272b1e058e7c58d988ed&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_011&quot;,
    &quot;operation_id&quot;: &quot;op_ir_011:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
      &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
      &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
      &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;items&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;selected_path&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_ba84e42bbdcd9356a9be&quot;
  ]
}</pre>

<a id="derivation-92c2bdddf75a449f7ef5"></a>

### demand\_291d056f6077282bc046

<pre>{
  &quot;id&quot;: &quot;demand_291d056f6077282bc046&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_a49e8fd7c34794d32d06&quot;
  ]
}</pre>

<a id="derivation-4cec8229aa09233266f8"></a>

### demand\_2b1ce18df1fb9d005e2f

<pre>{
  &quot;id&quot;: &quot;demand_2b1ce18df1fb9d005e2f&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e1:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;expression_reference&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_e7b2800b9cfb8182d939&quot;
  ]
}</pre>

<a id="derivation-90ccf45a580353ad5fba"></a>

### demand\_2b5fbd0c41efbf0c72b8

<pre>{
  &quot;id&quot;: &quot;demand_2b5fbd0c41efbf0c72b8&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_568ad54ffa69d22b3e96&quot;,
    &quot;demand_d63b24117139b2274350&quot;
  ]
}</pre>

<a id="derivation-a214c9ea0f16bff8c3ce"></a>

### demand\_2f172ee7a4e2e697a4cd

<pre>{
  &quot;id&quot;: &quot;demand_2f172ee7a4e2e697a4cd&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e6:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
      &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
      &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
      &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;total&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_f5e167bcdf4f9006cb97&quot;
  ]
}</pre>

<a id="derivation-fa5a59325dd6974fc3f5"></a>

### demand\_2f662c212c5a996b9a93

<pre>{
  &quot;id&quot;: &quot;demand_2f662c212c5a996b9a93&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_5fc6900a28b4207e9a7a&quot;
  ]
}</pre>

<a id="derivation-fec57f730ccb2b2c76b3"></a>

### demand\_30647d87deec5e8c9872

<pre>{
  &quot;id&quot;: &quot;demand_30647d87deec5e8c9872&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_bc4f0460d4e45aa1af15&quot;
  ]
}</pre>

<a id="derivation-88549bd4650e41426427"></a>

### demand\_3130c6d9fa81d0d715ba

<pre>{
  &quot;id&quot;: &quot;demand_3130c6d9fa81d0d715ba&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 2,
    &quot;data_ids&quot;: [
      &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_4d366363de94f81993ac&quot;,
    &quot;demand_fea45467f7f250a1026a&quot;
  ]
}</pre>

<a id="derivation-436f39fb5a2326a4d17d"></a>

### demand\_31620240295ce24ad7a1

<pre>{
  &quot;id&quot;: &quot;demand_31620240295ce24ad7a1&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 4,
    &quot;data_ids&quot;: [
      &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;required_original_value&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_39bf9abd0a9d713d5923&quot;,
    &quot;demand_d1a9f5a027f71cf5f37f&quot;
  ]
}</pre>

<a id="derivation-f7e07220adc8182b2b55"></a>

### demand\_31b579606595406d5703

<pre>{
  &quot;id&quot;: &quot;demand_31b579606595406d5703&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e0:a0&quot;,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_3d2a4f6cfeb2936ca3a7&quot;
  ]
}</pre>

<a id="derivation-8dfd3af70af19d841320"></a>

### demand\_3378fb51950f65e5be8a

<pre>{
  &quot;id&quot;: &quot;demand_3378fb51950f65e5be8a&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_8ae7508a094c84bb53f2&quot;
  ]
}</pre>

<a id="derivation-4fcee911c6fad612afb1"></a>

### demand\_34adffe576b442f72a3d

<pre>{
  &quot;id&quot;: &quot;demand_34adffe576b442f72a3d&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;required_original_value&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_73d463a7529f0667f3df&quot;,
    &quot;demand_b5ec715878877301c884&quot;
  ]
}</pre>

<a id="derivation-59c2ebc7c7e4b827e394"></a>

### demand\_34ba5d5a8d609182c024

<pre>{
  &quot;id&quot;: &quot;demand_34ba5d5a8d609182c024&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_6ba592badeb517669f07&quot;
  ]
}</pre>

<a id="derivation-e80d74b229f2283bc1d2"></a>

### demand\_36a423f29e613db958f6

<pre>{
  &quot;id&quot;: &quot;demand_36a423f29e613db958f6&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_4548d148e701318d8376&quot;,
    &quot;demand_6d505434e12189832332&quot;
  ]
}</pre>

<a id="derivation-50718880f9d872de97c3"></a>

### demand\_36ab9bc1351b9a94eced

<pre>{
  &quot;id&quot;: &quot;demand_36ab9bc1351b9a94eced&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_009&quot;,
    &quot;operation_id&quot;: &quot;op_ir_009:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_3c59631c7c944a1e5dc7bdb966c272cd355ff20dcdeb6d07906e4547746e1169&quot;,
      &quot;data_5bd0761d4780c33b8f014a0a65282b7460a295319cf205b06a923dd49f8d2594&quot;,
      &quot;data_5d32e16a7f2d66a941ff4ff820ed14a18a1b0ca5bbb2e568b6a33171729a62e9&quot;,
      &quot;data_b82b2e7fc2d1815522bc8e967ffc709aae6daf50b6b234c9b176a1bf6d4b246a&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_ad84c6971fb53fc6eb12&quot;
  ]
}</pre>

<a id="derivation-64b7d6cb0ead3ee05705"></a>

### demand\_36cb4c7986aa6a55abf4

<pre>{
  &quot;id&quot;: &quot;demand_36cb4c7986aa6a55abf4&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;member_presence&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_fd5c1eb70a6a723c58ad&quot;
  ]
}</pre>

<a id="derivation-26d3dba56b348d1b50ce"></a>

### demand\_3739e3f0e708a91f8ffe

<pre>{
  &quot;id&quot;: &quot;demand_3739e3f0e708a91f8ffe&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 3,
    &quot;data_ids&quot;: [
      &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;member_presence&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_fd5c1eb70a6a723c58ad&quot;
  ]
}</pre>

<a id="derivation-dfa96560ec0f04a532ed"></a>

### demand\_39bf9abd0a9d713d5923

<pre>{
  &quot;id&quot;: &quot;demand_39bf9abd0a9d713d5923&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 4,
    &quot;data_ids&quot;: [
      &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;constructed_member&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_acd6698ca3e534e587ca&quot;
  ]
}</pre>

<a id="derivation-b2312644f2cb4831813f"></a>

### demand\_3c31d44c792cca9aca27

<pre>{
  &quot;id&quot;: &quot;demand_3c31d44c792cca9aca27&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_9a90203532af8f15edab&quot;
  ]
}</pre>

<a id="derivation-84324287924d3b697634"></a>

### demand\_3d15661988b19a6b4b7e

<pre>{
  &quot;id&quot;: &quot;demand_3d15661988b19a6b4b7e&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_04977d052e12894e8e9c0a137fd39df74fb642c40353e8fa497f9efb4135badb&quot;,
      &quot;data_8276fb1f277efeb717aae1eb89fad8dc9851725a894ffffdbbdd00e6f260e56c&quot;,
      &quot;data_94cfb94a16886ab61be49175ee8bddb2882c306a6969a0769d12f3a2ad7be9c2&quot;,
      &quot;data_c151aa225e154341fe56b24f3f7e3b657a75ec1230aab5c985ba811572e96383&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_770f8357df9eea9bcbd1&quot;
  ]
}</pre>

<a id="derivation-b0cf30e42f1e1277d908"></a>

### demand\_3d2a4f6cfeb2936ca3a7

<pre>{
  &quot;id&quot;: &quot;demand_3d2a4f6cfeb2936ca3a7&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;member_presence&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_3d15661988b19a6b4b7e&quot;,
    &quot;demand_457b5d22e0e02b6037bd&quot;
  ]
}</pre>

<a id="derivation-b91902998d2498636e33"></a>

### demand\_3d98da9857708568385e

<pre>{
  &quot;id&quot;: &quot;demand_3d98da9857708568385e&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e4:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_04977d052e12894e8e9c0a137fd39df74fb642c40353e8fa497f9efb4135badb&quot;,
      &quot;data_8276fb1f277efeb717aae1eb89fad8dc9851725a894ffffdbbdd00e6f260e56c&quot;,
      &quot;data_94cfb94a16886ab61be49175ee8bddb2882c306a6969a0769d12f3a2ad7be9c2&quot;,
      &quot;data_c151aa225e154341fe56b24f3f7e3b657a75ec1230aab5c985ba811572e96383&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;task_value&quot;
  ],
  &quot;parents&quot;: []
}</pre>

<a id="derivation-291a18527ccfadba46ff"></a>

### demand\_4139f169a7a440a36c48

<pre>{
  &quot;id&quot;: &quot;demand_4139f169a7a440a36c48&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e1:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;expression_reference&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_004b4892406001232339&quot;
  ]
}</pre>

<a id="derivation-17e32e40030be2ef3c21"></a>

### demand\_41d795bc4e3527fa9ff2

<pre>{
  &quot;id&quot;: &quot;demand_41d795bc4e3527fa9ff2&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_31620240295ce24ad7a1&quot;
  ]
}</pre>

<a id="derivation-cd280c16a00664acdbe9"></a>

### demand\_42501761a360ca263efd

<pre>{
  &quot;id&quot;: &quot;demand_42501761a360ca263efd&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_434667e05ca41f976143&quot;,
    &quot;demand_df6c35a9003c5782def0&quot;
  ]
}</pre>

<a id="derivation-f7b9941b66e7e50f35b5"></a>

### demand\_4253e0798df43afe8a74

<pre>{
  &quot;id&quot;: &quot;demand_4253e0798df43afe8a74&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_2454d8dfe06c811c1b8d&quot;,
    &quot;demand_9dc47e97a4fa6ca40d85&quot;
  ]
}</pre>

<a id="derivation-8c5bb637c264e2db5066"></a>

### demand\_434667e05ca41f976143

<pre>{
  &quot;id&quot;: &quot;demand_434667e05ca41f976143&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_4c9fa9a6ccede6dfc85c&quot;
  ]
}</pre>

<a id="derivation-c8862a0382ce8eef96bd"></a>

### demand\_4548d148e701318d8376

<pre>{
  &quot;id&quot;: &quot;demand_4548d148e701318d8376&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_36a423f29e613db958f6&quot;
  ]
}</pre>

<a id="derivation-f9982ef93e69f3ecdce9"></a>

### demand\_457b5d22e0e02b6037bd

<pre>{
  &quot;id&quot;: &quot;demand_457b5d22e0e02b6037bd&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_04977d052e12894e8e9c0a137fd39df74fb642c40353e8fa497f9efb4135badb&quot;,
      &quot;data_8276fb1f277efeb717aae1eb89fad8dc9851725a894ffffdbbdd00e6f260e56c&quot;,
      &quot;data_94cfb94a16886ab61be49175ee8bddb2882c306a6969a0769d12f3a2ad7be9c2&quot;,
      &quot;data_c151aa225e154341fe56b24f3f7e3b657a75ec1230aab5c985ba811572e96383&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_3d98da9857708568385e&quot;
  ]
}</pre>

<a id="derivation-347b19f991fd6762e092"></a>

### demand\_46c9deb547b2922b60b7

<pre>{
  &quot;id&quot;: &quot;demand_46c9deb547b2922b60b7&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 2,
    &quot;data_ids&quot;: [
      &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_4ea7e281c6d43004a421&quot;,
    &quot;demand_5e84bcfe3e0c4316cf23&quot;
  ]
}</pre>

<a id="derivation-30f5fd8c5da651fdad5e"></a>

### demand\_47bf0e3566721de713c3

<pre>{
  &quot;id&quot;: &quot;demand_47bf0e3566721de713c3&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e5:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_04977d052e12894e8e9c0a137fd39df74fb642c40353e8fa497f9efb4135badb&quot;,
      &quot;data_8276fb1f277efeb717aae1eb89fad8dc9851725a894ffffdbbdd00e6f260e56c&quot;,
      &quot;data_94cfb94a16886ab61be49175ee8bddb2882c306a6969a0769d12f3a2ad7be9c2&quot;,
      &quot;data_c151aa225e154341fe56b24f3f7e3b657a75ec1230aab5c985ba811572e96383&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;external_request_retained&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_f5e167bcdf4f9006cb97&quot;
  ]
}</pre>

<a id="derivation-22c11e4401d9911af448"></a>

### demand\_48085dfa392def0ce20a

<pre>{
  &quot;id&quot;: &quot;demand_48085dfa392def0ce20a&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_04977d052e12894e8e9c0a137fd39df74fb642c40353e8fa497f9efb4135badb&quot;,
      &quot;data_8276fb1f277efeb717aae1eb89fad8dc9851725a894ffffdbbdd00e6f260e56c&quot;,
      &quot;data_94cfb94a16886ab61be49175ee8bddb2882c306a6969a0769d12f3a2ad7be9c2&quot;,
      &quot;data_c151aa225e154341fe56b24f3f7e3b657a75ec1230aab5c985ba811572e96383&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;query&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_7152da4555f1e0b354f7&quot;
  ]
}</pre>

<a id="derivation-de37443647a153400b8d"></a>

### demand\_48dab746b2aa866df933

<pre>{
  &quot;id&quot;: &quot;demand_48dab746b2aa866df933&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_46c9deb547b2922b60b7&quot;
  ]
}</pre>

<a id="derivation-6f2f2cb7ac3df78a08a0"></a>

### demand\_49809e00993fd3298c90

<pre>{
  &quot;id&quot;: &quot;demand_49809e00993fd3298c90&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_7abbaea7cb5d29f28d60&quot;
  ]
}</pre>

<a id="derivation-ff389390d9fe2fb89ad1"></a>

### demand\_4c9fa9a6ccede6dfc85c

<pre>{
  &quot;id&quot;: &quot;demand_4c9fa9a6ccede6dfc85c&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_611e49809880b096832e&quot;,
    &quot;demand_b53391f0f7d5f71e91fe&quot;
  ]
}</pre>

<a id="derivation-b9d6f42d600f91b46ac2"></a>

### demand\_4cc30f3714d17ae8b8aa

<pre>{
  &quot;id&quot;: &quot;demand_4cc30f3714d17ae8b8aa&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 4,
    &quot;data_ids&quot;: [
      &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;constructed_member&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_8ceca2514b143c12c3ec&quot;
  ]
}</pre>

<a id="derivation-cfc00dba175008ec7fdb"></a>

### demand\_4d366363de94f81993ac

<pre>{
  &quot;id&quot;: &quot;demand_4d366363de94f81993ac&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_fea45467f7f250a1026a&quot;
  ]
}</pre>

<a id="derivation-d0f26790bc02f275795f"></a>

### demand\_4e5e65007e5d5bfbb24c

<pre>{
  &quot;id&quot;: &quot;demand_4e5e65007e5d5bfbb24c&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_04977d052e12894e8e9c0a137fd39df74fb642c40353e8fa497f9efb4135badb&quot;,
      &quot;data_8276fb1f277efeb717aae1eb89fad8dc9851725a894ffffdbbdd00e6f260e56c&quot;,
      &quot;data_94cfb94a16886ab61be49175ee8bddb2882c306a6969a0769d12f3a2ad7be9c2&quot;,
      &quot;data_c151aa225e154341fe56b24f3f7e3b657a75ec1230aab5c985ba811572e96383&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_b4e3f1504bb12bf3c101&quot;
  ]
}</pre>

<a id="derivation-7ee595db40c18ab84365"></a>

### demand\_4ea7e281c6d43004a421

<pre>{
  &quot;id&quot;: &quot;demand_4ea7e281c6d43004a421&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 2,
    &quot;data_ids&quot;: [
      &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;constructed_member&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_8ceca2514b143c12c3ec&quot;
  ]
}</pre>

<a id="derivation-c6e2c14c3746d7bf167e"></a>

### demand\_4ef50416138bb581b28f

<pre>{
  &quot;id&quot;: &quot;demand_4ef50416138bb581b28f&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_d08365eada36586f59d0&quot;,
    &quot;demand_fce49c40b6a6c62be83f&quot;
  ]
}</pre>

<a id="derivation-4ca67f31b011cd2f3afe"></a>

### demand\_5011bdb0839eb1db8f5f

<pre>{
  &quot;id&quot;: &quot;demand_5011bdb0839eb1db8f5f&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_5557e331811b40c74c9f&quot;
  ]
}</pre>

<a id="derivation-da18a38846725622d3eb"></a>

### demand\_50c4239ed411c9ab4a93

<pre>{
  &quot;id&quot;: &quot;demand_50c4239ed411c9ab4a93&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_72d71816d574fb4dd9b5&quot;,
    &quot;demand_e3c98c7288aa69a5864b&quot;
  ]
}</pre>

<a id="derivation-21b850993b43a1eab77b"></a>

### demand\_51ac4ebbabda35f15857

<pre>{
  &quot;id&quot;: &quot;demand_51ac4ebbabda35f15857&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_3130c6d9fa81d0d715ba&quot;
  ]
}</pre>

<a id="derivation-2f27202ee8cd14f03550"></a>

### demand\_5557e331811b40c74c9f

<pre>{
  &quot;id&quot;: &quot;demand_5557e331811b40c74c9f&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_5011bdb0839eb1db8f5f&quot;,
    &quot;demand_9c612dff83479d2876a7&quot;
  ]
}</pre>

<a id="derivation-1dccc075796cf98a7b46"></a>

### demand\_555a31782d301a8b7e66

<pre>{
  &quot;id&quot;: &quot;demand_555a31782d301a8b7e66&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_1a321dc33bd0eb3a2915&quot;,
    &quot;demand_dcd59f59ba5ecf26f0b2&quot;
  ]
}</pre>

<a id="derivation-ca948ea29f0eee3e7519"></a>

### demand\_562bbddda249bd58cba5

<pre>{
  &quot;id&quot;: &quot;demand_562bbddda249bd58cba5&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_cd85273821c7bf906f0e&quot;,
    &quot;demand_f4e464ac72de50af9767&quot;
  ]
}</pre>

<a id="derivation-6bcfa2868227db02975a"></a>

### demand\_568ad54ffa69d22b3e96

<pre>{
  &quot;id&quot;: &quot;demand_568ad54ffa69d22b3e96&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_2b5fbd0c41efbf0c72b8&quot;
  ]
}</pre>

<a id="derivation-19ccd224608ab88e2aa7"></a>

### demand\_5752edcb6ff7273367d5

<pre>{
  &quot;id&quot;: &quot;demand_5752edcb6ff7273367d5&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e1:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;expression_reference&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_97c2ca65557814fe480c&quot;
  ]
}</pre>

<a id="derivation-94cedfa8f1d8ca0101cf"></a>

### demand\_588b7f1db144c74a771a

<pre>{
  &quot;id&quot;: &quot;demand_588b7f1db144c74a771a&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e0:a0&quot;,
    &quot;slot&quot;: 2,
    &quot;data_ids&quot;: [
      &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_962ab148bd3f76131e70&quot;
  ]
}</pre>

<a id="derivation-a58daef5239c94a216cf"></a>

### demand\_5cb3c1ed63a29acc81e0

<pre>{
  &quot;id&quot;: &quot;demand_5cb3c1ed63a29acc81e0&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e2:a0&quot;,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;conditional_observation&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_1571b282b1cc3480be38&quot;
  ]
}</pre>

<a id="derivation-c94c79720a1013844d6c"></a>

### demand\_5d27dda2bc039df4f42e

<pre>{
  &quot;id&quot;: &quot;demand_5d27dda2bc039df4f42e&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
      &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
      &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
      &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;total&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_ee26768410095adc582d&quot;
  ]
}</pre>

<a id="derivation-8116c92db1dca0f584b6"></a>

### demand\_5d40478cb03f05b4ec79

<pre>{
  &quot;id&quot;: &quot;demand_5d40478cb03f05b4ec79&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_48dab746b2aa866df933&quot;
  ]
}</pre>

<a id="derivation-11c40a1cf4f8511e525a"></a>

### demand\_5d93a00a900eaa207c71

<pre>{
  &quot;id&quot;: &quot;demand_5d93a00a900eaa207c71&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e0:a0&quot;,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_36cb4c7986aa6a55abf4&quot;
  ]
}</pre>

<a id="derivation-4a6054856d978a349d46"></a>

### demand\_5e84bcfe3e0c4316cf23

<pre>{
  &quot;id&quot;: &quot;demand_5e84bcfe3e0c4316cf23&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_4ea7e281c6d43004a421&quot;
  ]
}</pre>

<a id="derivation-d8da006a89b2de089593"></a>

### demand\_5fc6900a28b4207e9a7a

<pre>{
  &quot;id&quot;: &quot;demand_5fc6900a28b4207e9a7a&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;selected_path&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_5d40478cb03f05b4ec79&quot;
  ]
}</pre>

<a id="derivation-13db82e98bd201283df6"></a>

### demand\_611e49809880b096832e

<pre>{
  &quot;id&quot;: &quot;demand_611e49809880b096832e&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;selected_path&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_0310df466313b6d76981&quot;
  ]
}</pre>

<a id="derivation-b79eb2e3834d679589d6"></a>

### demand\_61fe0838d6fe0dc3bd81

<pre>{
  &quot;id&quot;: &quot;demand_61fe0838d6fe0dc3bd81&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_b286f779d7abe4ebe3c6&quot;,
    &quot;demand_f9c9c6d5f47e51e30859&quot;
  ]
}</pre>

<a id="derivation-3ed93eabbc176fd2c700"></a>

### demand\_68902d1f94e48fcef73f

<pre>{
  &quot;id&quot;: &quot;demand_68902d1f94e48fcef73f&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_df6cc1f7f3ab12db4e43&quot;
  ]
}</pre>

<a id="derivation-7dafe4b889126465d0c9"></a>

### demand\_6ae3f4fa8d9ad3f5251e

<pre>{
  &quot;id&quot;: &quot;demand_6ae3f4fa8d9ad3f5251e&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_bf666375e380c823c702&quot;,
    &quot;demand_efcce88b04206bdcea3b&quot;
  ]
}</pre>

<a id="derivation-a384508f073a2d948cdd"></a>

### demand\_6ba592badeb517669f07

<pre>{
  &quot;id&quot;: &quot;demand_6ba592badeb517669f07&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 3,
    &quot;data_ids&quot;: [
      &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_c33596ff7a7281694f4f&quot;,
    &quot;demand_ddf3e29062f750ca385f&quot;,
    &quot;demand_f504c504335f0e95ec33&quot;
  ]
}</pre>

<a id="derivation-73f6ad8aa14ec3f51876"></a>

### demand\_6cd3c1759d0a385ebd76

<pre>{
  &quot;id&quot;: &quot;demand_6cd3c1759d0a385ebd76&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_b513d4a1213497ee53f4&quot;
  ]
}</pre>

<a id="derivation-bcf083a3d2f5480568dd"></a>

### demand\_6d310e1a296e12fe6082

<pre>{
  &quot;id&quot;: &quot;demand_6d310e1a296e12fe6082&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_24bccf3c0fd1c71d8670&quot;
  ]
}</pre>

<a id="derivation-14e75292a630f1b6e7ad"></a>

### demand\_6d505434e12189832332

<pre>{
  &quot;id&quot;: &quot;demand_6d505434e12189832332&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_857b523d1a37eb7cd36f&quot;
  ]
}</pre>

<a id="derivation-afcae62f4c76114757c5"></a>

### demand\_7152da4555f1e0b354f7

<pre>{
  &quot;id&quot;: &quot;demand_7152da4555f1e0b354f7&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e4:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_04977d052e12894e8e9c0a137fd39df74fb642c40353e8fa497f9efb4135badb&quot;,
      &quot;data_8276fb1f277efeb717aae1eb89fad8dc9851725a894ffffdbbdd00e6f260e56c&quot;,
      &quot;data_94cfb94a16886ab61be49175ee8bddb2882c306a6969a0769d12f3a2ad7be9c2&quot;,
      &quot;data_c151aa225e154341fe56b24f3f7e3b657a75ec1230aab5c985ba811572e96383&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;query&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;task_expected_relation&quot;
  ],
  &quot;parents&quot;: []
}</pre>

<a id="derivation-0c5bb66f6e6f2926572e"></a>

### demand\_71911dc6014a8c24b1fc

<pre>{
  &quot;id&quot;: &quot;demand_71911dc6014a8c24b1fc&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e1:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_e46a47898c247d6466d1&quot;
  ]
}</pre>

<a id="derivation-ab1e939996f332b6aab3"></a>

### demand\_72d71816d574fb4dd9b5

<pre>{
  &quot;id&quot;: &quot;demand_72d71816d574fb4dd9b5&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;selected_path&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_9d2610407f82d449ad56&quot;
  ]
}</pre>

<a id="derivation-8260aaf28a5c82a27da2"></a>

### demand\_73a52b5ebb8866e71559

<pre>{
  &quot;id&quot;: &quot;demand_73a52b5ebb8866e71559&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e1:a0&quot;,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;conditional_observation&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_4d366363de94f81993ac&quot;
  ]
}</pre>

<a id="derivation-1608f50b2898161ee53e"></a>

### demand\_73ae1d77566a9696778f

<pre>{
  &quot;id&quot;: &quot;demand_73ae1d77566a9696778f&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_c246e8ec45842e762ed8&quot;
  ]
}</pre>

<a id="derivation-615e3d456fecb928017f"></a>

### demand\_73b7af8c4c657be0f328

<pre>{
  &quot;id&quot;: &quot;demand_73b7af8c4c657be0f328&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_2f662c212c5a996b9a93&quot;,
    &quot;demand_5fc6900a28b4207e9a7a&quot;
  ]
}</pre>

<a id="derivation-511d919cab46d46c83ce"></a>

### demand\_73d463a7529f0667f3df

<pre>{
  &quot;id&quot;: &quot;demand_73d463a7529f0667f3df&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;constructed_member&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_48085dfa392def0ce20a&quot;
  ]
}</pre>

<a id="derivation-3467734cafcaa2728a84"></a>

### demand\_741bbfb83d8659783e18

<pre>{
  &quot;id&quot;: &quot;demand_741bbfb83d8659783e18&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_009&quot;,
    &quot;operation_id&quot;: &quot;op_ir_009:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
      &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
      &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
      &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;total&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;selected_path&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_36ab9bc1351b9a94eced&quot;
  ]
}</pre>

<a id="derivation-378a0fe72a8fac3360ce"></a>

### demand\_76a95debf4852e739d4e

<pre>{
  &quot;id&quot;: &quot;demand_76a95debf4852e739d4e&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;action&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e4:a0&quot;,
    &quot;slot&quot;: null,
    &quot;data_ids&quot;: []
  },
  &quot;property&quot;: &quot;action&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;task_action&quot;
  ],
  &quot;parents&quot;: []
}</pre>

<a id="derivation-2dec417113e8465cf4f0"></a>

### demand\_76c502d20b285019bd43

<pre>{
  &quot;id&quot;: &quot;demand_76c502d20b285019bd43&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 5,
    &quot;data_ids&quot;: [
      &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_3739e3f0e708a91f8ffe&quot;,
    &quot;demand_5cb3c1ed63a29acc81e0&quot;,
    &quot;demand_8c77ea65ddfd5264b67d&quot;
  ]
}</pre>

<a id="derivation-2c936773892d338bd20f"></a>

### demand\_770f8357df9eea9bcbd1

<pre>{
  &quot;id&quot;: &quot;demand_770f8357df9eea9bcbd1&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e4:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_04977d052e12894e8e9c0a137fd39df74fb642c40353e8fa497f9efb4135badb&quot;,
      &quot;data_8276fb1f277efeb717aae1eb89fad8dc9851725a894ffffdbbdd00e6f260e56c&quot;,
      &quot;data_94cfb94a16886ab61be49175ee8bddb2882c306a6969a0769d12f3a2ad7be9c2&quot;,
      &quot;data_c151aa225e154341fe56b24f3f7e3b657a75ec1230aab5c985ba811572e96383&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;task_expected_relation&quot;
  ],
  &quot;parents&quot;: []
}</pre>

<a id="derivation-59a933033b79f0f43347"></a>

### demand\_778cb0387e39f0c9f5a2

<pre>{
  &quot;id&quot;: &quot;demand_778cb0387e39f0c9f5a2&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_2b1ce18df1fb9d005e2f&quot;
  ]
}</pre>

<a id="derivation-94b5141660bb7972c0f1"></a>

### demand\_78363bdef55f1542017d

<pre>{
  &quot;id&quot;: &quot;demand_78363bdef55f1542017d&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_010&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_3c59631c7c944a1e5dc7bdb966c272cd355ff20dcdeb6d07906e4547746e1169&quot;,
      &quot;data_5bd0761d4780c33b8f014a0a65282b7460a295319cf205b06a923dd49f8d2594&quot;,
      &quot;data_5d32e16a7f2d66a941ff4ff820ed14a18a1b0ca5bbb2e568b6a33171729a62e9&quot;,
      &quot;data_b82b2e7fc2d1815522bc8e967ffc709aae6daf50b6b234c9b176a1bf6d4b246a&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;required_original_value&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_b307a49044f63b65253d&quot;
  ]
}</pre>

<a id="derivation-48084816832a5024dba9"></a>

### demand\_7abbaea7cb5d29f28d60

<pre>{
  &quot;id&quot;: &quot;demand_7abbaea7cb5d29f28d60&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e1:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;expression_reference&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_93316229a7c91d48dd81&quot;
  ]
}</pre>

<a id="derivation-cd537109fd785dac5dec"></a>

### demand\_7c0060421bcacf0320c4

<pre>{
  &quot;id&quot;: &quot;demand_7c0060421bcacf0320c4&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;action&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e4:a0&quot;,
    &quot;slot&quot;: null,
    &quot;data_ids&quot;: []
  },
  &quot;property&quot;: &quot;action&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;required_acquisition&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_ec49381ac390295bdf73&quot;
  ]
}</pre>

<a id="derivation-0170459dd910316afd98"></a>

### demand\_7e577145599289c69121

<pre>{
  &quot;id&quot;: &quot;demand_7e577145599289c69121&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_ba9b7f4a31116525c2d0&quot;
  ]
}</pre>

<a id="derivation-6df5366e6427282a64a1"></a>

### demand\_81436ab38ab1ad441869

<pre>{
  &quot;id&quot;: &quot;demand_81436ab38ab1ad441869&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_f9042fb247ef932628d0&quot;
  ]
}</pre>

<a id="derivation-d58f52802ec82c5cd910"></a>

### demand\_81f1915086c8d574aa16

<pre>{
  &quot;id&quot;: &quot;demand_81f1915086c8d574aa16&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_a70581e50e1c2baef086&quot;
  ]
}</pre>

<a id="derivation-6ac43f8e59fb9b763b90"></a>

### demand\_8223fe328a0a4a78bb8f

<pre>{
  &quot;id&quot;: &quot;demand_8223fe328a0a4a78bb8f&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_d6b1e40b8b2fbeaa74e5&quot;
  ]
}</pre>

<a id="derivation-c54b430b9e701ecec54f"></a>

### demand\_82ad1b48e34ddf11c067

<pre>{
  &quot;id&quot;: &quot;demand_82ad1b48e34ddf11c067&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e1:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_986d6c1b0c695e4487a7&quot;
  ]
}</pre>

<a id="derivation-55e3285040cec234e63d"></a>

### demand\_857b523d1a37eb7cd36f

<pre>{
  &quot;id&quot;: &quot;demand_857b523d1a37eb7cd36f&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_a02e66d0b48f56cec96e&quot;,
    &quot;demand_db127be777f1a636a74b&quot;
  ]
}</pre>

<a id="derivation-81360db03057813c9bbb"></a>

### demand\_859820ff51196a26d078

<pre>{
  &quot;id&quot;: &quot;demand_859820ff51196a26d078&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;selected_path&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_a6fbaa34d6e660359985&quot;
  ]
}</pre>

<a id="derivation-56e15f6af0c1ae29911a"></a>

### demand\_8794b79aca4871a54aea

<pre>{
  &quot;id&quot;: &quot;demand_8794b79aca4871a54aea&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_73b7af8c4c657be0f328&quot;
  ]
}</pre>

<a id="derivation-4ea285c27d2e2c5ee3e4"></a>

### demand\_8ae7508a094c84bb53f2

<pre>{
  &quot;id&quot;: &quot;demand_8ae7508a094c84bb53f2&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;constructed_member&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_fd5c1eb70a6a723c58ad&quot;
  ]
}</pre>

<a id="derivation-8b096482a9f2204ecf19"></a>

### demand\_8c77ea65ddfd5264b67d

<pre>{
  &quot;id&quot;: &quot;demand_8c77ea65ddfd5264b67d&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e0:a0&quot;,
    &quot;slot&quot;: 2,
    &quot;data_ids&quot;: [
      &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_3739e3f0e708a91f8ffe&quot;
  ]
}</pre>

<a id="derivation-7798f5d8b063f8aa26cc"></a>

### demand\_8ceca2514b143c12c3ec

<pre>{
  &quot;id&quot;: &quot;demand_8ceca2514b143c12c3ec&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_04977d052e12894e8e9c0a137fd39df74fb642c40353e8fa497f9efb4135badb&quot;,
      &quot;data_8276fb1f277efeb717aae1eb89fad8dc9851725a894ffffdbbdd00e6f260e56c&quot;,
      &quot;data_94cfb94a16886ab61be49175ee8bddb2882c306a6969a0769d12f3a2ad7be9c2&quot;,
      &quot;data_c151aa225e154341fe56b24f3f7e3b657a75ec1230aab5c985ba811572e96383&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_47bf0e3566721de713c3&quot;,
    &quot;demand_ba9ad30c0f71261d761c&quot;
  ]
}</pre>

<a id="derivation-bb7d8ec5bdcbf7eb4c7b"></a>

### demand\_8f6c9eaabc5af2d49c37

<pre>{
  &quot;id&quot;: &quot;demand_8f6c9eaabc5af2d49c37&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e2:a0&quot;,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;conditional_observation&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_d1a9f5a027f71cf5f37f&quot;
  ]
}</pre>

<a id="derivation-1dc5f49ab3caf4f913fb"></a>

### demand\_9216db2340931460b1aa

<pre>{
  &quot;id&quot;: &quot;demand_9216db2340931460b1aa&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_76c502d20b285019bd43&quot;
  ]
}</pre>

<a id="derivation-f5dfe475f157e8876c76"></a>

### demand\_93316229a7c91d48dd81

<pre>{
  &quot;id&quot;: &quot;demand_93316229a7c91d48dd81&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e1:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_9a3e1f907ffaa3531744&quot;
  ]
}</pre>

<a id="derivation-b2b2785d30b6641c6576"></a>

### demand\_93bb0378b437546e0d4e

<pre>{
  &quot;id&quot;: &quot;demand_93bb0378b437546e0d4e&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_61fe0838d6fe0dc3bd81&quot;
  ]
}</pre>

<a id="derivation-0e52dad3fd9278e38666"></a>

### demand\_94a26ae9bddbfb8eca23

<pre>{
  &quot;id&quot;: &quot;demand_94a26ae9bddbfb8eca23&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_011277f3c08d6481b14c&quot;
  ]
}</pre>

<a id="derivation-669bb2cd5dbd8be1e070"></a>

### demand\_95caf89c6420d824792c

<pre>{
  &quot;id&quot;: &quot;demand_95caf89c6420d824792c&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_51ac4ebbabda35f15857&quot;
  ]
}</pre>

<a id="derivation-f42a28988c5a8918ed0b"></a>

### demand\_962ab148bd3f76131e70

<pre>{
  &quot;id&quot;: &quot;demand_962ab148bd3f76131e70&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 3,
    &quot;data_ids&quot;: [
      &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;member_presence&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_8ceca2514b143c12c3ec&quot;
  ]
}</pre>

<a id="derivation-00759c7c58b2d9230c3b"></a>

### demand\_97c2ca65557814fe480c

<pre>{
  &quot;id&quot;: &quot;demand_97c2ca65557814fe480c&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e1:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_7e577145599289c69121&quot;
  ]
}</pre>

<a id="derivation-a5a35ae775fa6db5bcd4"></a>

### demand\_986d6c1b0c695e4487a7

<pre>{
  &quot;id&quot;: &quot;demand_986d6c1b0c695e4487a7&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_037418f9eb471de7b119&quot;
  ]
}</pre>

<a id="derivation-e9a9b4a96a722d943e47"></a>

### demand\_9a3e1f907ffaa3531744

<pre>{
  &quot;id&quot;: &quot;demand_9a3e1f907ffaa3531744&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_c1a76913b8cad56da419&quot;
  ]
}</pre>

<a id="derivation-de985751879569efb1fe"></a>

### demand\_9a8f570e3c654eb1ee42

<pre>{
  &quot;id&quot;: &quot;demand_9a8f570e3c654eb1ee42&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;action&quot;,
    &quot;instruction_id&quot;: &quot;ir_010&quot;,
    &quot;operation_id&quot;: &quot;op_ir_010:e0:a0&quot;,
    &quot;slot&quot;: null,
    &quot;data_ids&quot;: []
  },
  &quot;property&quot;: &quot;action&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;task_action&quot;
  ],
  &quot;parents&quot;: []
}</pre>

<a id="derivation-1e07c73e107f20f596c4"></a>

### demand\_9a90203532af8f15edab

<pre>{
  &quot;id&quot;: &quot;demand_9a90203532af8f15edab&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_4139f169a7a440a36c48&quot;,
    &quot;demand_c406707838ff2b9369d5&quot;
  ]
}</pre>

<a id="derivation-5a049206b27e8fb330be"></a>

### demand\_9c612dff83479d2876a7

<pre>{
  &quot;id&quot;: &quot;demand_9c612dff83479d2876a7&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_bc20046888a093b8e7d2&quot;
  ]
}</pre>

<a id="derivation-cebf2f8d7d99efde4b7e"></a>

### demand\_9d2610407f82d449ad56

<pre>{
  &quot;id&quot;: &quot;demand_9d2610407f82d449ad56&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_12e579c8e4ba4e2ad8c5&quot;
  ]
}</pre>

<a id="derivation-37f5b689da1f5beb088b"></a>

### demand\_9dc47e97a4fa6ca40d85

<pre>{
  &quot;id&quot;: &quot;demand_9dc47e97a4fa6ca40d85&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_4253e0798df43afe8a74&quot;
  ]
}</pre>

<a id="derivation-56fa25645561b6b90245"></a>

### demand\_9f11d0b7a2cac71b1f0f

<pre>{
  &quot;id&quot;: &quot;demand_9f11d0b7a2cac71b1f0f&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 4,
    &quot;data_ids&quot;: [
      &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_4cc30f3714d17ae8b8aa&quot;,
    &quot;demand_acaf0ec94c39315f5609&quot;
  ]
}</pre>

<a id="derivation-113100ca16a0f851db2f"></a>

### demand\_a02e66d0b48f56cec96e

<pre>{
  &quot;id&quot;: &quot;demand_a02e66d0b48f56cec96e&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;selected_path&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_da78ba1f5674bfc6a96f&quot;
  ]
}</pre>

<a id="derivation-5fe05b899966b7455a46"></a>

### demand\_a49e8fd7c34794d32d06

<pre>{
  &quot;id&quot;: &quot;demand_a49e8fd7c34794d32d06&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_859820ff51196a26d078&quot;,
    &quot;demand_bbcc0f5a6503524e10e8&quot;
  ]
}</pre>

<a id="derivation-c6c5769bafd35c48f1ce"></a>

### demand\_a6fbaa34d6e660359985

<pre>{
  &quot;id&quot;: &quot;demand_a6fbaa34d6e660359985&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_41d795bc4e3527fa9ff2&quot;
  ]
}</pre>

<a id="derivation-d873e5f3e89b26bfcef9"></a>

### demand\_a70581e50e1c2baef086

<pre>{
  &quot;id&quot;: &quot;demand_a70581e50e1c2baef086&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 2,
    &quot;data_ids&quot;: [
      &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;required_original_value&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_c5938053dafdfb56ceca&quot;,
    &quot;demand_d3b5044605c1160166e0&quot;
  ]
}</pre>

<a id="derivation-80cf3274b11467d8b27c"></a>

### demand\_a99abaf590a5bc6642ba

<pre>{
  &quot;id&quot;: &quot;demand_a99abaf590a5bc6642ba&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_d7f0c68b978bf9a2a057&quot;
  ]
}</pre>

<a id="derivation-5c1121d5a86bf8ff18b1"></a>

### demand\_ab1562c691e4a29ee345

<pre>{
  &quot;id&quot;: &quot;demand_ab1562c691e4a29ee345&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_93bb0378b437546e0d4e&quot;,
    &quot;demand_ed52af0fd937f879f815&quot;
  ]
}</pre>

<a id="derivation-f2d5cf95d800d776ad9a"></a>

### demand\_acaf0ec94c39315f5609

<pre>{
  &quot;id&quot;: &quot;demand_acaf0ec94c39315f5609&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e2:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_4cc30f3714d17ae8b8aa&quot;
  ]
}</pre>

<a id="derivation-730d94acb1f72f654e38"></a>

### demand\_acd6698ca3e534e587ca

<pre>{
  &quot;id&quot;: &quot;demand_acd6698ca3e534e587ca&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_04977d052e12894e8e9c0a137fd39df74fb642c40353e8fa497f9efb4135badb&quot;,
      &quot;data_8276fb1f277efeb717aae1eb89fad8dc9851725a894ffffdbbdd00e6f260e56c&quot;,
      &quot;data_94cfb94a16886ab61be49175ee8bddb2882c306a6969a0769d12f3a2ad7be9c2&quot;,
      &quot;data_c151aa225e154341fe56b24f3f7e3b657a75ec1230aab5c985ba811572e96383&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_b80fcaba1d3cb69a64ec&quot;
  ]
}</pre>

<a id="derivation-7355aa053145eed0fc9d"></a>

### demand\_ad84c6971fb53fc6eb12

<pre>{
  &quot;id&quot;: &quot;demand_ad84c6971fb53fc6eb12&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_009&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_3c59631c7c944a1e5dc7bdb966c272cd355ff20dcdeb6d07906e4547746e1169&quot;,
      &quot;data_5bd0761d4780c33b8f014a0a65282b7460a295319cf205b06a923dd49f8d2594&quot;,
      &quot;data_5d32e16a7f2d66a941ff4ff820ed14a18a1b0ca5bbb2e568b6a33171729a62e9&quot;,
      &quot;data_b82b2e7fc2d1815522bc8e967ffc709aae6daf50b6b234c9b176a1bf6d4b246a&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_78363bdef55f1542017d&quot;
  ]
}</pre>

<a id="derivation-7aa0259b7e7b224d743a"></a>

### demand\_b286f779d7abe4ebe3c6

<pre>{
  &quot;id&quot;: &quot;demand_b286f779d7abe4ebe3c6&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_f9c9c6d5f47e51e30859&quot;
  ]
}</pre>

<a id="derivation-0b46ed13fd4cab9fdf76"></a>

### demand\_b307a49044f63b65253d

<pre>{
  &quot;id&quot;: &quot;demand_b307a49044f63b65253d&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_010&quot;,
    &quot;operation_id&quot;: &quot;op_ir_010:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_3c59631c7c944a1e5dc7bdb966c272cd355ff20dcdeb6d07906e4547746e1169&quot;,
      &quot;data_5bd0761d4780c33b8f014a0a65282b7460a295319cf205b06a923dd49f8d2594&quot;,
      &quot;data_5d32e16a7f2d66a941ff4ff820ed14a18a1b0ca5bbb2e568b6a33171729a62e9&quot;,
      &quot;data_b82b2e7fc2d1815522bc8e967ffc709aae6daf50b6b234c9b176a1bf6d4b246a&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;task_expected_relation&quot;
  ],
  &quot;parents&quot;: []
}</pre>

<a id="derivation-93ace520e1cfb34eec70"></a>

### demand\_b4e3f1504bb12bf3c101

<pre>{
  &quot;id&quot;: &quot;demand_b4e3f1504bb12bf3c101&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e4:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_04977d052e12894e8e9c0a137fd39df74fb642c40353e8fa497f9efb4135badb&quot;,
      &quot;data_8276fb1f277efeb717aae1eb89fad8dc9851725a894ffffdbbdd00e6f260e56c&quot;,
      &quot;data_94cfb94a16886ab61be49175ee8bddb2882c306a6969a0769d12f3a2ad7be9c2&quot;,
      &quot;data_c151aa225e154341fe56b24f3f7e3b657a75ec1230aab5c985ba811572e96383&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;task_value&quot;
  ],
  &quot;parents&quot;: []
}</pre>

<a id="derivation-b305d599463419f3f2ef"></a>

### demand\_b513d4a1213497ee53f4

<pre>{
  &quot;id&quot;: &quot;demand_b513d4a1213497ee53f4&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_3378fb51950f65e5be8a&quot;,
    &quot;demand_8ae7508a094c84bb53f2&quot;
  ]
}</pre>

<a id="derivation-726ac26561cd7d977030"></a>

### demand\_b53391f0f7d5f71e91fe

<pre>{
  &quot;id&quot;: &quot;demand_b53391f0f7d5f71e91fe&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_611e49809880b096832e&quot;
  ]
}</pre>

<a id="derivation-47cfa8c6fa09237e3dbc"></a>

### demand\_b57377a0246c23824760

<pre>{
  &quot;id&quot;: &quot;demand_b57377a0246c23824760&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_011&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
      &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
      &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
      &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;items&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_272b1e058e7c58d988ed&quot;,
    &quot;demand_e1c12628e1cf671d68dd&quot;
  ]
}</pre>

<a id="derivation-a9408af52c1b22cc0f37"></a>

### demand\_b5b4a1eb3efaa1668424

<pre>{
  &quot;id&quot;: &quot;demand_b5b4a1eb3efaa1668424&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e2:a0&quot;,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;conditional_observation&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_acaf0ec94c39315f5609&quot;
  ]
}</pre>

<a id="derivation-ee082435232ff1e8e022"></a>

### demand\_b5ec715878877301c884

<pre>{
  &quot;id&quot;: &quot;demand_b5ec715878877301c884&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_73d463a7529f0667f3df&quot;
  ]
}</pre>

<a id="derivation-b6a4f1d3139cc819649b"></a>

### demand\_b713cd5cb0285deba88f

<pre>{
  &quot;id&quot;: &quot;demand_b713cd5cb0285deba88f&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 3,
    &quot;data_ids&quot;: [
      &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;member_presence&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_4e5e65007e5d5bfbb24c&quot;,
    &quot;demand_acd6698ca3e534e587ca&quot;
  ]
}</pre>

<a id="derivation-ba50e08ada050126ef8d"></a>

### demand\_b7ec1e84454c1a18f384

<pre>{
  &quot;id&quot;: &quot;demand_b7ec1e84454c1a18f384&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_e1e9d3ae018195f100c5&quot;
  ]
}</pre>

<a id="derivation-0e7f5ea4524e4c04aa56"></a>

### demand\_b80fcaba1d3cb69a64ec

<pre>{
  &quot;id&quot;: &quot;demand_b80fcaba1d3cb69a64ec&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e4:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_04977d052e12894e8e9c0a137fd39df74fb642c40353e8fa497f9efb4135badb&quot;,
      &quot;data_8276fb1f277efeb717aae1eb89fad8dc9851725a894ffffdbbdd00e6f260e56c&quot;,
      &quot;data_94cfb94a16886ab61be49175ee8bddb2882c306a6969a0769d12f3a2ad7be9c2&quot;,
      &quot;data_c151aa225e154341fe56b24f3f7e3b657a75ec1230aab5c985ba811572e96383&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;task_expected_relation&quot;
  ],
  &quot;parents&quot;: []
}</pre>

<a id="derivation-ccebd2d919f15ccbace7"></a>

### demand\_b95265387a64bed01a1c

<pre>{
  &quot;id&quot;: &quot;demand_b95265387a64bed01a1c&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_b962d5a298a25048ede4&quot;
  ]
}</pre>

<a id="derivation-02d4df4ad655ea9b4a81"></a>

### demand\_b962d5a298a25048ede4

<pre>{
  &quot;id&quot;: &quot;demand_b962d5a298a25048ede4&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_c25c4be315aa1cb2ddbd&quot;,
    &quot;demand_e8047654aa6bff17f62f&quot;
  ]
}</pre>

<a id="derivation-fcddd26dfac31f68bd68"></a>

### demand\_ba84e42bbdcd9356a9be

<pre>{
  &quot;id&quot;: &quot;demand_ba84e42bbdcd9356a9be&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_011&quot;,
    &quot;operation_id&quot;: &quot;op_ir_011:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_12ea329cebb7fb4155ba190a559188e76a986f0a1eb020754003e824f22535a5&quot;,
      &quot;data_31a9dc19c5483e1464b99e4bdd6547c1519117d64e70291a2ad78d0c544160ce&quot;,
      &quot;data_ddcfc654bd05b26d018d1c712cca288a2caceba2b37bc24d3d49faa952553e6a&quot;,
      &quot;data_f04c7c46dcfdf4406afbda7f422fb9b62daa512e862b76f925c8f9c76f0d37e4&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_0141adb0d4592b3adc67&quot;
  ]
}</pre>

<a id="derivation-c0a379b75688e3e6016b"></a>

### demand\_ba9ad30c0f71261d761c

<pre>{
  &quot;id&quot;: &quot;demand_ba9ad30c0f71261d761c&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e4:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_04977d052e12894e8e9c0a137fd39df74fb642c40353e8fa497f9efb4135badb&quot;,
      &quot;data_8276fb1f277efeb717aae1eb89fad8dc9851725a894ffffdbbdd00e6f260e56c&quot;,
      &quot;data_94cfb94a16886ab61be49175ee8bddb2882c306a6969a0769d12f3a2ad7be9c2&quot;,
      &quot;data_c151aa225e154341fe56b24f3f7e3b657a75ec1230aab5c985ba811572e96383&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;external_request_retained&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_f5e167bcdf4f9006cb97&quot;
  ]
}</pre>

<a id="derivation-bb590fb6968c06b83627"></a>

### demand\_ba9b7f4a31116525c2d0

<pre>{
  &quot;id&quot;: &quot;demand_ba9b7f4a31116525c2d0&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 3,
    &quot;data_ids&quot;: [
      &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_36cb4c7986aa6a55abf4&quot;,
    &quot;demand_5d93a00a900eaa207c71&quot;,
    &quot;demand_73a52b5ebb8866e71559&quot;
  ]
}</pre>

<a id="derivation-e11750a84758c846c0c1"></a>

### demand\_bad4aba5fc5149222095

<pre>{
  &quot;id&quot;: &quot;demand_bad4aba5fc5149222095&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_009&quot;,
    &quot;operation_id&quot;: &quot;op_ir_009:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
      &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
      &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
      &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;total&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_741bbfb83d8659783e18&quot;
  ]
}</pre>

<a id="derivation-c66c2e6e619ee3684438"></a>

### demand\_bbcc0f5a6503524e10e8

<pre>{
  &quot;id&quot;: &quot;demand_bbcc0f5a6503524e10e8&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_859820ff51196a26d078&quot;
  ]
}</pre>

<a id="derivation-9397f445f1d54dba66ac"></a>

### demand\_bc1d10125a7b0297df28

<pre>{
  &quot;id&quot;: &quot;demand_bc1d10125a7b0297df28&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_9f11d0b7a2cac71b1f0f&quot;
  ]
}</pre>

<a id="derivation-e70c9533841b508e700f"></a>

### demand\_bc20046888a093b8e7d2

<pre>{
  &quot;id&quot;: &quot;demand_bc20046888a093b8e7d2&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_5752edcb6ff7273367d5&quot;,
    &quot;demand_c311dd9af991af51f870&quot;
  ]
}</pre>

<a id="derivation-3ba5aa35888415fa0e61"></a>

### demand\_bc4f0460d4e45aa1af15

<pre>{
  &quot;id&quot;: &quot;demand_bc4f0460d4e45aa1af15&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e1:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;expression_reference&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_82ad1b48e34ddf11c067&quot;
  ]
}</pre>

<a id="derivation-4e3fed4139a277b7a43d"></a>

### demand\_bc79b3add08ddaf4dd01

<pre>{
  &quot;id&quot;: &quot;demand_bc79b3add08ddaf4dd01&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_0985269a53c1c5a484dc&quot;
  ]
}</pre>

<a id="derivation-f1583cc07bb02ea23b74"></a>

### demand\_be7a78d11a57332cf9cb

<pre>{
  &quot;id&quot;: &quot;demand_be7a78d11a57332cf9cb&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
      &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
      &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
      &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;items&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_b57377a0246c23824760&quot;
  ]
}</pre>

<a id="derivation-97f09b783ed3c9b2c7f8"></a>

### demand\_bf666375e380c823c702

<pre>{
  &quot;id&quot;: &quot;demand_bf666375e380c823c702&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_6ae3f4fa8d9ad3f5251e&quot;
  ]
}</pre>

<a id="derivation-715e18d9b8dfa1a15cd4"></a>

### demand\_bfc939197c77ad301f6e

<pre>{
  &quot;id&quot;: &quot;demand_bfc939197c77ad301f6e&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;action&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e4:a0&quot;,
    &quot;slot&quot;: null,
    &quot;data_ids&quot;: []
  },
  &quot;property&quot;: &quot;action&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;required_acquisition&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_f5e167bcdf4f9006cb97&quot;
  ]
}</pre>

<a id="derivation-12080433b444da4861a3"></a>

### demand\_bff860b7dc91334e5042

<pre>{
  &quot;id&quot;: &quot;demand_bff860b7dc91334e5042&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e6:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
      &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
      &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
      &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;items&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_ec49381ac390295bdf73&quot;
  ]
}</pre>

<a id="derivation-3252672d795cc0dc012a"></a>

### demand\_c1a76913b8cad56da419

<pre>{
  &quot;id&quot;: &quot;demand_c1a76913b8cad56da419&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 3,
    &quot;data_ids&quot;: [
      &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_09d6ec65d99b55ebf769&quot;,
    &quot;demand_31b579606595406d5703&quot;,
    &quot;demand_3d2a4f6cfeb2936ca3a7&quot;
  ]
}</pre>

<a id="derivation-4419aaa80d95cbcbb432"></a>

### demand\_c246e8ec45842e762ed8

<pre>{
  &quot;id&quot;: &quot;demand_c246e8ec45842e762ed8&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;constructed_member&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_8ceca2514b143c12c3ec&quot;
  ]
}</pre>

<a id="derivation-6a298fee400ab59c8a84"></a>

### demand\_c25c4be315aa1cb2ddbd

<pre>{
  &quot;id&quot;: &quot;demand_c25c4be315aa1cb2ddbd&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;selected_path&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_95caf89c6420d824792c&quot;
  ]
}</pre>

<a id="derivation-6bba669ac1ae951639d2"></a>

### demand\_c311dd9af991af51f870

<pre>{
  &quot;id&quot;: &quot;demand_c311dd9af991af51f870&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_5752edcb6ff7273367d5&quot;
  ]
}</pre>

<a id="derivation-80a2a7e7b59d40e2a00a"></a>

### demand\_c33596ff7a7281694f4f

<pre>{
  &quot;id&quot;: &quot;demand_c33596ff7a7281694f4f&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e0:a0&quot;,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_ddf3e29062f750ca385f&quot;
  ]
}</pre>

<a id="derivation-535230253f21625ba152"></a>

### demand\_c406707838ff2b9369d5

<pre>{
  &quot;id&quot;: &quot;demand_c406707838ff2b9369d5&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_4139f169a7a440a36c48&quot;
  ]
}</pre>

<a id="derivation-285c7c7ef0e289d8b040"></a>

### demand\_c5938053dafdfb56ceca

<pre>{
  &quot;id&quot;: &quot;demand_c5938053dafdfb56ceca&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 2,
    &quot;data_ids&quot;: [
      &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;constructed_member&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_3d15661988b19a6b4b7e&quot;
  ]
}</pre>

<a id="derivation-334c166c5c84f2cc2797"></a>

### demand\_c7fb0ddc14cc53bedd4a

<pre>{
  &quot;id&quot;: &quot;demand_c7fb0ddc14cc53bedd4a&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_d1932f0a64b79c23dec5&quot;
  ]
}</pre>

<a id="derivation-315fa10b285d89f2fde3"></a>

### demand\_cbb989e7a266e3f66a0e

<pre>{
  &quot;id&quot;: &quot;demand_cbb989e7a266e3f66a0e&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_f7f0676a25c6bbf1a3e8&quot;
  ]
}</pre>

<a id="derivation-93cea5028333633ffe85"></a>

### demand\_cd85273821c7bf906f0e

<pre>{
  &quot;id&quot;: &quot;demand_cd85273821c7bf906f0e&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;selected_path&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_12ff67812f331399a73c&quot;
  ]
}</pre>

<a id="derivation-edadb6e4d3ffb280201c"></a>

### demand\_d08365eada36586f59d0

<pre>{
  &quot;id&quot;: &quot;demand_d08365eada36586f59d0&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_17dd7ca30d951bb87f63&quot;
  ]
}</pre>

<a id="derivation-d1d9d0739f0b679055cc"></a>

### demand\_d1932f0a64b79c23dec5

<pre>{
  &quot;id&quot;: &quot;demand_d1932f0a64b79c23dec5&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 4,
    &quot;data_ids&quot;: [
      &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_0001aeda76e11b764441&quot;,
    &quot;demand_1571b282b1cc3480be38&quot;
  ]
}</pre>

<a id="derivation-2f39f266436f75ab4e93"></a>

### demand\_d1a9f5a027f71cf5f37f

<pre>{
  &quot;id&quot;: &quot;demand_d1a9f5a027f71cf5f37f&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e2:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_45301469e2dd60b3fdcb7738c37b7d4b0b5f6eb2e74b42f572722bdf6c75e54f&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_39bf9abd0a9d713d5923&quot;
  ]
}</pre>

<a id="derivation-b8b93cbbdb9866f6665e"></a>

### demand\_d3b5044605c1160166e0

<pre>{
  &quot;id&quot;: &quot;demand_d3b5044605c1160166e0&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_c5938053dafdfb56ceca&quot;
  ]
}</pre>

<a id="derivation-c95abca464b48c1a2670"></a>

### demand\_d63b24117139b2274350

<pre>{
  &quot;id&quot;: &quot;demand_d63b24117139b2274350&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_114a4d4ea6d305d9eade&quot;
  ]
}</pre>

<a id="derivation-d7f631a9515180e8bca8"></a>

### demand\_d6b1e40b8b2fbeaa74e5

<pre>{
  &quot;id&quot;: &quot;demand_d6b1e40b8b2fbeaa74e5&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;selected_path&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_68902d1f94e48fcef73f&quot;
  ]
}</pre>

<a id="derivation-429e2c0daa1c1ad62ec3"></a>

### demand\_d7f0c68b978bf9a2a057

<pre>{
  &quot;id&quot;: &quot;demand_d7f0c68b978bf9a2a057&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;selected_path&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_0088834c70240599d9ce&quot;
  ]
}</pre>

<a id="derivation-ad522521b4c00451b345"></a>

### demand\_da78ba1f5674bfc6a96f

<pre>{
  &quot;id&quot;: &quot;demand_da78ba1f5674bfc6a96f&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_6cd3c1759d0a385ebd76&quot;
  ]
}</pre>

<a id="derivation-e00cedb6dbd758b75e86"></a>

### demand\_db127be777f1a636a74b

<pre>{
  &quot;id&quot;: &quot;demand_db127be777f1a636a74b&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_a02e66d0b48f56cec96e&quot;
  ]
}</pre>

<a id="derivation-be16e8d8f6ba9b815a2d"></a>

### demand\_dcd59f59ba5ecf26f0b2

<pre>{
  &quot;id&quot;: &quot;demand_dcd59f59ba5ecf26f0b2&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_555a31782d301a8b7e66&quot;
  ]
}</pre>

<a id="derivation-0378ceafd1ba0e3a6b12"></a>

### demand\_ddf3e29062f750ca385f

<pre>{
  &quot;id&quot;: &quot;demand_ddf3e29062f750ca385f&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;member_presence&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_8ceca2514b143c12c3ec&quot;
  ]
}</pre>

<a id="derivation-101b1685a8ffde1fce60"></a>

### demand\_df6c35a9003c5782def0

<pre>{
  &quot;id&quot;: &quot;demand_df6c35a9003c5782def0&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_42501761a360ca263efd&quot;
  ]
}</pre>

<a id="derivation-7fcdd439e3ce3490ee45"></a>

### demand\_df6cc1f7f3ab12db4e43

<pre>{
  &quot;id&quot;: &quot;demand_df6cc1f7f3ab12db4e43&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_34adffe576b442f72a3d&quot;
  ]
}</pre>

<a id="derivation-751e684bda909c2b2029"></a>

### demand\_e1c12628e1cf671d68dd

<pre>{
  &quot;id&quot;: &quot;demand_e1c12628e1cf671d68dd&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_011&quot;,
    &quot;operation_id&quot;: &quot;op_ir_011:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
      &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
      &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
      &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;items&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_272b1e058e7c58d988ed&quot;
  ]
}</pre>

<a id="derivation-ca34d7675e71100eba0d"></a>

### demand\_e1e9d3ae018195f100c5

<pre>{
  &quot;id&quot;: &quot;demand_e1e9d3ae018195f100c5&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_291d056f6077282bc046&quot;,
    &quot;demand_b7ec1e84454c1a18f384&quot;
  ]
}</pre>

<a id="derivation-487c3bc68fc5f1141110"></a>

### demand\_e3c98c7288aa69a5864b

<pre>{
  &quot;id&quot;: &quot;demand_e3c98c7288aa69a5864b&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_72d71816d574fb4dd9b5&quot;
  ]
}</pre>

<a id="derivation-90a0212d9bf8ab3da6ac"></a>

### demand\_e3f1e82a9022edf7445b

<pre>{
  &quot;id&quot;: &quot;demand_e3f1e82a9022edf7445b&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e0:a0&quot;,
    &quot;slot&quot;: 2,
    &quot;data_ids&quot;: [
      &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_b713cd5cb0285deba88f&quot;
  ]
}</pre>

<a id="derivation-71220b94aae1035c3598"></a>

### demand\_e46a47898c247d6466d1

<pre>{
  &quot;id&quot;: &quot;demand_e46a47898c247d6466d1&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_56fe23ccb6a2ce54ddf0df27d745453130e6023a145b61742452ac7c10cad5e4&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_0c572562cca375fcb81c&quot;
  ]
}</pre>

<a id="derivation-c89b8372557f43486242"></a>

### demand\_e7b2800b9cfb8182d939

<pre>{
  &quot;id&quot;: &quot;demand_e7b2800b9cfb8182d939&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e1:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_34ba5d5a8d609182c024&quot;
  ]
}</pre>

<a id="derivation-0ee4483550b2a603bbb5"></a>

### demand\_e8047654aa6bff17f62f

<pre>{
  &quot;id&quot;: &quot;demand_e8047654aa6bff17f62f&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_c25c4be315aa1cb2ddbd&quot;
  ]
}</pre>

<a id="derivation-2df29f3ca5a1ae60396e"></a>

### demand\_e9838adbf3a93290628a

<pre>{
  &quot;id&quot;: &quot;demand_e9838adbf3a93290628a&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_645d0dcf737729ce3ddc7bd92368ad4a79bf2a4acfb97f4497044ebfde75022f&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_73ae1d77566a9696778f&quot;,
    &quot;demand_c246e8ec45842e762ed8&quot;
  ]
}</pre>

<a id="derivation-201667d65099cbad2600"></a>

### demand\_ebec4ea2896736a03704

<pre>{
  &quot;id&quot;: &quot;demand_ebec4ea2896736a03704&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_09daef85513bd2245b89&quot;
  ]
}</pre>

<a id="derivation-1b5f3f04ef47a65f8563"></a>

### demand\_ec49381ac390295bdf73

<pre>{
  &quot;id&quot;: &quot;demand_ec49381ac390295bdf73&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e5:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
      &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
      &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
      &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;items&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_be7a78d11a57332cf9cb&quot;,
    &quot;demand_bff860b7dc91334e5042&quot;
  ]
}</pre>

<a id="derivation-d1c83461572dfb17763d"></a>

### demand\_ed52af0fd937f879f815

<pre>{
  &quot;id&quot;: &quot;demand_ed52af0fd937f879f815&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_ab1562c691e4a29ee345&quot;
  ]
}</pre>

<a id="derivation-458b74820f196580e264"></a>

### demand\_ee26768410095adc582d

<pre>{
  &quot;id&quot;: &quot;demand_ee26768410095adc582d&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_009&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
      &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
      &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
      &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;total&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_741bbfb83d8659783e18&quot;,
    &quot;demand_bad4aba5fc5149222095&quot;
  ]
}</pre>

<a id="derivation-6909918c693f1f7d1062"></a>

### demand\_efcce88b04206bdcea3b

<pre>{
  &quot;id&quot;: &quot;demand_efcce88b04206bdcea3b&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_50c4239ed411c9ab4a93&quot;
  ]
}</pre>

<a id="derivation-99c99979addc22a0048a"></a>

### demand\_f4e464ac72de50af9767

<pre>{
  &quot;id&quot;: &quot;demand_f4e464ac72de50af9767&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_cd85273821c7bf906f0e&quot;
  ]
}</pre>

<a id="derivation-720f29bdd8e5448ac8bd"></a>

### demand\_f504c504335f0e95ec33

<pre>{
  &quot;id&quot;: &quot;demand_f504c504335f0e95ec33&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e1:a0&quot;,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_ab5d6d9a2f6f7763d7e2a0810ef911317a6232502e2da5145ffa04608ff6bc2d&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;conditional_observation&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_5e84bcfe3e0c4316cf23&quot;
  ]
}</pre>

<a id="derivation-5c6688e491c503cf4518"></a>

### demand\_f5e167bcdf4f9006cb97

<pre>{
  &quot;id&quot;: &quot;demand_f5e167bcdf4f9006cb97&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e5:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_2eb63a1ab15756fe6994b40aeafa4cea6583a56479b5f81a63566dd43e727cc7&quot;,
      &quot;data_cb9b02f478da3ccfd17db533252ab707ef339880d6a0e3de05cbe95078ec8a9d&quot;,
      &quot;data_d739df60dd3db16d6061fca21dc7029175bc2eaa1f4a855b38b22d45a33ebe50&quot;,
      &quot;data_df81cda97aac5677b957c70e3f9b20b4da96f1f793bf9c6bab14e7b07a2d660b&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;total&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_2f172ee7a4e2e697a4cd&quot;,
    &quot;demand_5d27dda2bc039df4f42e&quot;
  ]
}</pre>

<a id="derivation-776dbc9bc5b1348be8f8"></a>

### demand\_f7f0676a25c6bbf1a3e8

<pre>{
  &quot;id&quot;: &quot;demand_f7f0676a25c6bbf1a3e8&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_20350eab3a8b9219263c&quot;,
    &quot;demand_cbb989e7a266e3f66a0e&quot;
  ]
}</pre>

<a id="derivation-efbc98f247eedbd9cf3d"></a>

### demand\_f9042fb247ef932628d0

<pre>{
  &quot;id&quot;: &quot;demand_f9042fb247ef932628d0&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_8223fe328a0a4a78bb8f&quot;,
    &quot;demand_d6b1e40b8b2fbeaa74e5&quot;
  ]
}</pre>

<a id="derivation-106e91cc0230543a6a3e"></a>

### demand\_f9c9c6d5f47e51e30859

<pre>{
  &quot;id&quot;: &quot;demand_f9c9c6d5f47e51e30859&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e1:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;expression_reference&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_71911dc6014a8c24b1fc&quot;
  ]
}</pre>

<a id="derivation-8d05633bc06d880eb515"></a>

### demand\_fce49c40b6a6c62be83f

<pre>{
  &quot;id&quot;: &quot;demand_fce49c40b6a6c62be83f&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_a3c50049aa08eca57cb3898bf5901dca60aa49facf7700822371ff974a1cdff7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_4ef50416138bb581b28f&quot;
  ]
}</pre>

<a id="derivation-76b5b14bbc0e749fc83a"></a>

### demand\_fd5c1eb70a6a723c58ad

<pre>{
  &quot;id&quot;: &quot;demand_fd5c1eb70a6a723c58ad&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_04977d052e12894e8e9c0a137fd39df74fb642c40353e8fa497f9efb4135badb&quot;,
      &quot;data_8276fb1f277efeb717aae1eb89fad8dc9851725a894ffffdbbdd00e6f260e56c&quot;,
      &quot;data_94cfb94a16886ab61be49175ee8bddb2882c306a6969a0769d12f3a2ad7be9c2&quot;,
      &quot;data_c151aa225e154341fe56b24f3f7e3b657a75ec1230aab5c985ba811572e96383&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_0d21c9e8ece1c99119bb&quot;,
    &quot;demand_0ed25450465605d8bdee&quot;
  ]
}</pre>

<a id="derivation-bf0d53bad2cae23ffb1d"></a>

### demand\_fea45467f7f250a1026a

<pre>{
  &quot;id&quot;: &quot;demand_fea45467f7f250a1026a&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 2,
    &quot;data_ids&quot;: [
      &quot;data_0b0b29f64fdd39fa6bc14820dd97f2f3ca1559b504f46706b5504356a33ca7a6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R008&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;constructed_member&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_fd5c1eb70a6a723c58ad&quot;
  ]
}</pre>

## Limitations and diagnostics

<pre>[]</pre>

No additional semantic approval is implied by preparation or replay\.

<details><summary>Reference index</summary><pre>{
  &quot;targets&quot;: {
    &quot;target_e3b0c44298fc1c149afb&quot;: {
      &quot;pointer&quot;: &quot;&quot;,
      &quot;kind&quot;: &quot;graph&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [],
      &quot;value&quot;: {
        &quot;entry_block_id&quot;: &quot;block_001&quot;,
        &quot;constraints&quot;: [
          &quot;Call index.search exactly once.&quot;,
          &quot;Do not invoke index.delete anywhere in this workflow.&quot;,
          &quot;Parameter descriptions are call requirements and do not instruct pre-call validation or normalization.&quot;,
          &quot;Capability note: index.search supports fuzzy matching; this note does not request fuzzy expansion in this workflow.&quot;
        ],
        &quot;blocks&quot;: {
          &quot;block_001&quot;: {
            &quot;block_id&quot;: &quot;block_001&quot;,
            &quot;block_name&quot;: &quot;Read the user-supplied request.json&quot;,
            &quot;instructions&quot;: [
              {
                &quot;id&quot;: &quot;ir_001&quot;,
                &quot;opcode&quot;: &quot;read_request_json&quot;,
                &quot;inputs&quot;: [
                  {
                    &quot;type&quot;: &quot;external_resource&quot;,
                    &quot;identifier&quot;: &quot;request.json&quot;,
                    &quot;semantic_name&quot;: &quot;request.json&quot;
                  }
                ],
                &quot;outputs&quot;: [
                  {
                    &quot;type&quot;: &quot;result&quot;,
                    &quot;identifier&quot;: &quot;result_001&quot;,
                    &quot;semantic_name&quot;: &quot;request.json contents&quot;
                  }
                ],
                &quot;constraints&quot;: [],
                &quot;metadata&quot;: {},
                &quot;draft_instruction_id&quot;: &quot;read_request_json&quot;
              },
              {
                &quot;id&quot;: &quot;ir_002&quot;,
                &quot;opcode&quot;: &quot;dispatch&quot;,
                &quot;inputs&quot;: [],
                &quot;outputs&quot;: [],
                &quot;constraints&quot;: [],
                &quot;metadata&quot;: {},
                &quot;draft_instruction_id&quot;: &quot;go_extract_params&quot;
              }
            ],
            &quot;constraints&quot;: [],
            &quot;data_source_kind&quot;: &quot;external&quot;
          },
          &quot;block_002&quot;: {
            &quot;block_id&quot;: &quot;block_002&quot;,
            &quot;block_name&quot;: &quot;Extract request.term and optional from_date and limit&quot;,
            &quot;instructions&quot;: [
              {
                &quot;id&quot;: &quot;ir_003&quot;,
                &quot;opcode&quot;: &quot;extract_query_term&quot;,
                &quot;inputs&quot;: [
                  {
                    &quot;type&quot;: &quot;result&quot;,
                    &quot;identifier&quot;: &quot;result_001&quot;,
                    &quot;semantic_name&quot;: &quot;request_data&quot;
                  }
                ],
                &quot;outputs&quot;: [
                  {
                    &quot;type&quot;: &quot;result&quot;,
                    &quot;identifier&quot;: &quot;result_002&quot;,
                    &quot;semantic_name&quot;: &quot;request.term&quot;
                  }
                ],
                &quot;constraints&quot;: [],
                &quot;metadata&quot;: {},
                &quot;draft_instruction_id&quot;: &quot;extract_query_term&quot;
              },
              {
                &quot;id&quot;: &quot;ir_004&quot;,
                &quot;opcode&quot;: &quot;extract_optional_from_date&quot;,
                &quot;inputs&quot;: [
                  {
                    &quot;type&quot;: &quot;result&quot;,
                    &quot;identifier&quot;: &quot;result_001&quot;,
                    &quot;semantic_name&quot;: &quot;request_data&quot;
                  }
                ],
                &quot;outputs&quot;: [
                  {
                    &quot;type&quot;: &quot;result&quot;,
                    &quot;identifier&quot;: &quot;result_003&quot;,
                    &quot;semantic_name&quot;: &quot;request.from_date&quot;
                  },
                  {
                    &quot;type&quot;: &quot;result&quot;,
                    &quot;identifier&quot;: &quot;result_004&quot;,
                    &quot;semantic_name&quot;: &quot;whether request.from_date is present&quot;
                  }
                ],
                &quot;constraints&quot;: [],
                &quot;metadata&quot;: {},
                &quot;draft_instruction_id&quot;: &quot;extract_optional_from_date&quot;
              },
              {
                &quot;id&quot;: &quot;ir_005&quot;,
                &quot;opcode&quot;: &quot;extract_optional_limit&quot;,
                &quot;inputs&quot;: [
                  {
                    &quot;type&quot;: &quot;result&quot;,
                    &quot;identifier&quot;: &quot;result_001&quot;,
                    &quot;semantic_name&quot;: &quot;request_data&quot;
                  }
                ],
                &quot;outputs&quot;: [
                  {
                    &quot;type&quot;: &quot;result&quot;,
                    &quot;identifier&quot;: &quot;result_005&quot;,
                    &quot;semantic_name&quot;: &quot;request.limit&quot;
                  },
                  {
                    &quot;type&quot;: &quot;result&quot;,
                    &quot;identifier&quot;: &quot;result_006&quot;,
                    &quot;semantic_name&quot;: &quot;whether request.limit is present&quot;
                  }
                ],
                &quot;constraints&quot;: [],
                &quot;metadata&quot;: {},
                &quot;draft_instruction_id&quot;: &quot;extract_optional_limit&quot;
              },
              {
                &quot;id&quot;: &quot;ir_006&quot;,
                &quot;opcode&quot;: &quot;dispatch&quot;,
                &quot;inputs&quot;: [],
                &quot;outputs&quot;: [],
                &quot;constraints&quot;: [],
                &quot;metadata&quot;: {},
                &quot;draft_instruction_id&quot;: &quot;go_search&quot;
              }
            ],
            &quot;constraints&quot;: [],
            &quot;data_source_kind&quot;: null
          },
          &quot;block_003&quot;: {
            &quot;block_id&quot;: &quot;block_003&quot;,
            &quot;block_name&quot;: &quot;Call index.search once with the request term and optional arguments&quot;,
            &quot;instructions&quot;: [
              {
                &quot;id&quot;: &quot;ir_007&quot;,
                &quot;opcode&quot;: &quot;index.search&quot;,
                &quot;inputs&quot;: [
                  {
                    &quot;type&quot;: &quot;external_resource&quot;,
                    &quot;identifier&quot;: &quot;index.search&quot;,
                    &quot;semantic_name&quot;: &quot;index.search&quot;
                  },
                  {
                    &quot;type&quot;: &quot;result&quot;,
                    &quot;identifier&quot;: &quot;result_002&quot;,
                    &quot;semantic_name&quot;: &quot;query_term&quot;
                  },
                  {
                    &quot;type&quot;: &quot;result&quot;,
                    &quot;identifier&quot;: &quot;result_003&quot;,
                    &quot;semantic_name&quot;: &quot;from_date_value&quot;
                  },
                  {
                    &quot;type&quot;: &quot;result&quot;,
                    &quot;identifier&quot;: &quot;result_004&quot;,
                    &quot;semantic_name&quot;: &quot;from_date_present&quot;
                  },
                  {
                    &quot;type&quot;: &quot;result&quot;,
                    &quot;identifier&quot;: &quot;result_005&quot;,
                    &quot;semantic_name&quot;: &quot;limit_value&quot;
                  },
                  {
                    &quot;type&quot;: &quot;result&quot;,
                    &quot;identifier&quot;: &quot;result_006&quot;,
                    &quot;semantic_name&quot;: &quot;limit_present&quot;
                  }
                ],
                &quot;outputs&quot;: [
                  {
                    &quot;type&quot;: &quot;result&quot;,
                    &quot;identifier&quot;: &quot;result_007&quot;,
                    &quot;semantic_name&quot;: &quot;index.search response&quot;
                  }
                ],
                &quot;constraints&quot;: [
                  &quot;Use request.term unchanged as its query argument.&quot;,
                  &quot;When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.&quot;,
                  &quot;When from_date is missing, omit the from_date argument.&quot;,
                  &quot;When limit is present, pass its value unchanged as the limit argument.&quot;,
                  &quot;When limit is missing, omit the limit argument.&quot;,
                  &quot;Apply the missing-argument settings in query configuration to this same call: missing_arguments.from_date = omit, missing_arguments.limit = omit.&quot;
                ],
                &quot;metadata&quot;: {},
                &quot;draft_instruction_id&quot;: &quot;call_index_search&quot;
              },
              {
                &quot;id&quot;: &quot;ir_008&quot;,
                &quot;opcode&quot;: &quot;dispatch&quot;,
                &quot;inputs&quot;: [],
                &quot;outputs&quot;: [],
                &quot;constraints&quot;: [],
                &quot;metadata&quot;: {},
                &quot;draft_instruction_id&quot;: &quot;go_post_search&quot;
              }
            ],
            &quot;constraints&quot;: [],
            &quot;data_source_kind&quot;: &quot;external&quot;
          },
          &quot;block_004&quot;: {
            &quot;block_id&quot;: &quot;block_004&quot;,
            &quot;block_name&quot;: &quot;Write the response total to count.txt and return the response items&quot;,
            &quot;instructions&quot;: [
              {
                &quot;id&quot;: &quot;ir_009&quot;,
                &quot;opcode&quot;: &quot;extract_response_total&quot;,
                &quot;inputs&quot;: [
                  {
                    &quot;type&quot;: &quot;result&quot;,
                    &quot;identifier&quot;: &quot;result_007&quot;,
                    &quot;semantic_name&quot;: &quot;search_response&quot;
                  }
                ],
                &quot;outputs&quot;: [
                  {
                    &quot;type&quot;: &quot;result&quot;,
                    &quot;identifier&quot;: &quot;result_008&quot;,
                    &quot;semantic_name&quot;: &quot;search response total&quot;
                  }
                ],
                &quot;constraints&quot;: [],
                &quot;metadata&quot;: {},
                &quot;draft_instruction_id&quot;: &quot;extract_response_total&quot;
              },
              {
                &quot;id&quot;: &quot;ir_010&quot;,
                &quot;opcode&quot;: &quot;write_count_file&quot;,
                &quot;inputs&quot;: [
                  {
                    &quot;type&quot;: &quot;external_resource&quot;,
                    &quot;identifier&quot;: &quot;count.txt&quot;,
                    &quot;semantic_name&quot;: &quot;count.txt&quot;
                  },
                  {
                    &quot;type&quot;: &quot;result&quot;,
                    &quot;identifier&quot;: &quot;result_008&quot;,
                    &quot;semantic_name&quot;: &quot;response_total&quot;
                  }
                ],
                &quot;outputs&quot;: [],
                &quot;constraints&quot;: [
                  &quot;After the search, write the response&#x27;s total value to local count.txt.&quot;
                ],
                &quot;metadata&quot;: {},
                &quot;draft_instruction_id&quot;: &quot;write_count_file&quot;
              },
              {
                &quot;id&quot;: &quot;ir_011&quot;,
                &quot;opcode&quot;: &quot;extract_response_items&quot;,
                &quot;inputs&quot;: [
                  {
                    &quot;type&quot;: &quot;result&quot;,
                    &quot;identifier&quot;: &quot;result_007&quot;,
                    &quot;semantic_name&quot;: &quot;search_response&quot;
                  }
                ],
                &quot;outputs&quot;: [
                  {
                    &quot;type&quot;: &quot;result&quot;,
                    &quot;identifier&quot;: &quot;result_009&quot;,
                    &quot;semantic_name&quot;: &quot;search response items&quot;
                  }
                ],
                &quot;constraints&quot;: [],
                &quot;metadata&quot;: {},
                &quot;draft_instruction_id&quot;: &quot;extract_response_items&quot;
              },
              {
                &quot;id&quot;: &quot;ir_012&quot;,
                &quot;opcode&quot;: &quot;return&quot;,
                &quot;inputs&quot;: [
                  {
                    &quot;type&quot;: &quot;result&quot;,
                    &quot;identifier&quot;: &quot;result_009&quot;,
                    &quot;semantic_name&quot;: &quot;response_items&quot;
                  }
                ],
                &quot;outputs&quot;: [],
                &quot;constraints&quot;: [
                  &quot;Return the search response&#x27;s items value unchanged.&quot;
                ],
                &quot;metadata&quot;: {},
                &quot;draft_instruction_id&quot;: &quot;return_items&quot;
              }
            ],
            &quot;constraints&quot;: [],
            &quot;data_source_kind&quot;: null
          }
        },
        &quot;edges&quot;: [
          {
            &quot;source_block_id&quot;: &quot;block_001&quot;,
            &quot;target_block_id&quot;: &quot;block_002&quot;,
            &quot;condition_text&quot;: null
          },
          {
            &quot;source_block_id&quot;: &quot;block_002&quot;,
            &quot;target_block_id&quot;: &quot;block_003&quot;,
            &quot;condition_text&quot;: null
          },
          {
            &quot;source_block_id&quot;: &quot;block_003&quot;,
            &quot;target_block_id&quot;: &quot;block_004&quot;,
            &quot;condition_text&quot;: null
          }
        ],
        &quot;declared_context_keys&quot;: []
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_da5059015847e5be0de6&quot;: {
      &quot;pointer&quot;: &quot;/blocks&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;
      ],
      &quot;value&quot;: {
        &quot;block_001&quot;: {
          &quot;block_id&quot;: &quot;block_001&quot;,
          &quot;block_name&quot;: &quot;Read the user-supplied request.json&quot;,
          &quot;instructions&quot;: [
            {
              &quot;id&quot;: &quot;ir_001&quot;,
              &quot;opcode&quot;: &quot;read_request_json&quot;,
              &quot;inputs&quot;: [
                {
                  &quot;type&quot;: &quot;external_resource&quot;,
                  &quot;identifier&quot;: &quot;request.json&quot;,
                  &quot;semantic_name&quot;: &quot;request.json&quot;
                }
              ],
              &quot;outputs&quot;: [
                {
                  &quot;type&quot;: &quot;result&quot;,
                  &quot;identifier&quot;: &quot;result_001&quot;,
                  &quot;semantic_name&quot;: &quot;request.json contents&quot;
                }
              ],
              &quot;constraints&quot;: [],
              &quot;metadata&quot;: {},
              &quot;draft_instruction_id&quot;: &quot;read_request_json&quot;
            },
            {
              &quot;id&quot;: &quot;ir_002&quot;,
              &quot;opcode&quot;: &quot;dispatch&quot;,
              &quot;inputs&quot;: [],
              &quot;outputs&quot;: [],
              &quot;constraints&quot;: [],
              &quot;metadata&quot;: {},
              &quot;draft_instruction_id&quot;: &quot;go_extract_params&quot;
            }
          ],
          &quot;constraints&quot;: [],
          &quot;data_source_kind&quot;: &quot;external&quot;
        },
        &quot;block_002&quot;: {
          &quot;block_id&quot;: &quot;block_002&quot;,
          &quot;block_name&quot;: &quot;Extract request.term and optional from_date and limit&quot;,
          &quot;instructions&quot;: [
            {
              &quot;id&quot;: &quot;ir_003&quot;,
              &quot;opcode&quot;: &quot;extract_query_term&quot;,
              &quot;inputs&quot;: [
                {
                  &quot;type&quot;: &quot;result&quot;,
                  &quot;identifier&quot;: &quot;result_001&quot;,
                  &quot;semantic_name&quot;: &quot;request_data&quot;
                }
              ],
              &quot;outputs&quot;: [
                {
                  &quot;type&quot;: &quot;result&quot;,
                  &quot;identifier&quot;: &quot;result_002&quot;,
                  &quot;semantic_name&quot;: &quot;request.term&quot;
                }
              ],
              &quot;constraints&quot;: [],
              &quot;metadata&quot;: {},
              &quot;draft_instruction_id&quot;: &quot;extract_query_term&quot;
            },
            {
              &quot;id&quot;: &quot;ir_004&quot;,
              &quot;opcode&quot;: &quot;extract_optional_from_date&quot;,
              &quot;inputs&quot;: [
                {
                  &quot;type&quot;: &quot;result&quot;,
                  &quot;identifier&quot;: &quot;result_001&quot;,
                  &quot;semantic_name&quot;: &quot;request_data&quot;
                }
              ],
              &quot;outputs&quot;: [
                {
                  &quot;type&quot;: &quot;result&quot;,
                  &quot;identifier&quot;: &quot;result_003&quot;,
                  &quot;semantic_name&quot;: &quot;request.from_date&quot;
                },
                {
                  &quot;type&quot;: &quot;result&quot;,
                  &quot;identifier&quot;: &quot;result_004&quot;,
                  &quot;semantic_name&quot;: &quot;whether request.from_date is present&quot;
                }
              ],
              &quot;constraints&quot;: [],
              &quot;metadata&quot;: {},
              &quot;draft_instruction_id&quot;: &quot;extract_optional_from_date&quot;
            },
            {
              &quot;id&quot;: &quot;ir_005&quot;,
              &quot;opcode&quot;: &quot;extract_optional_limit&quot;,
              &quot;inputs&quot;: [
                {
                  &quot;type&quot;: &quot;result&quot;,
                  &quot;identifier&quot;: &quot;result_001&quot;,
                  &quot;semantic_name&quot;: &quot;request_data&quot;
                }
              ],
              &quot;outputs&quot;: [
                {
                  &quot;type&quot;: &quot;result&quot;,
                  &quot;identifier&quot;: &quot;result_005&quot;,
                  &quot;semantic_name&quot;: &quot;request.limit&quot;
                },
                {
                  &quot;type&quot;: &quot;result&quot;,
                  &quot;identifier&quot;: &quot;result_006&quot;,
                  &quot;semantic_name&quot;: &quot;whether request.limit is present&quot;
                }
              ],
              &quot;constraints&quot;: [],
              &quot;metadata&quot;: {},
              &quot;draft_instruction_id&quot;: &quot;extract_optional_limit&quot;
            },
            {
              &quot;id&quot;: &quot;ir_006&quot;,
              &quot;opcode&quot;: &quot;dispatch&quot;,
              &quot;inputs&quot;: [],
              &quot;outputs&quot;: [],
              &quot;constraints&quot;: [],
              &quot;metadata&quot;: {},
              &quot;draft_instruction_id&quot;: &quot;go_search&quot;
            }
          ],
          &quot;constraints&quot;: [],
          &quot;data_source_kind&quot;: null
        },
        &quot;block_003&quot;: {
          &quot;block_id&quot;: &quot;block_003&quot;,
          &quot;block_name&quot;: &quot;Call index.search once with the request term and optional arguments&quot;,
          &quot;instructions&quot;: [
            {
              &quot;id&quot;: &quot;ir_007&quot;,
              &quot;opcode&quot;: &quot;index.search&quot;,
              &quot;inputs&quot;: [
                {
                  &quot;type&quot;: &quot;external_resource&quot;,
                  &quot;identifier&quot;: &quot;index.search&quot;,
                  &quot;semantic_name&quot;: &quot;index.search&quot;
                },
                {
                  &quot;type&quot;: &quot;result&quot;,
                  &quot;identifier&quot;: &quot;result_002&quot;,
                  &quot;semantic_name&quot;: &quot;query_term&quot;
                },
                {
                  &quot;type&quot;: &quot;result&quot;,
                  &quot;identifier&quot;: &quot;result_003&quot;,
                  &quot;semantic_name&quot;: &quot;from_date_value&quot;
                },
                {
                  &quot;type&quot;: &quot;result&quot;,
                  &quot;identifier&quot;: &quot;result_004&quot;,
                  &quot;semantic_name&quot;: &quot;from_date_present&quot;
                },
                {
                  &quot;type&quot;: &quot;result&quot;,
                  &quot;identifier&quot;: &quot;result_005&quot;,
                  &quot;semantic_name&quot;: &quot;limit_value&quot;
                },
                {
                  &quot;type&quot;: &quot;result&quot;,
                  &quot;identifier&quot;: &quot;result_006&quot;,
                  &quot;semantic_name&quot;: &quot;limit_present&quot;
                }
              ],
              &quot;outputs&quot;: [
                {
                  &quot;type&quot;: &quot;result&quot;,
                  &quot;identifier&quot;: &quot;result_007&quot;,
                  &quot;semantic_name&quot;: &quot;index.search response&quot;
                }
              ],
              &quot;constraints&quot;: [
                &quot;Use request.term unchanged as its query argument.&quot;,
                &quot;When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.&quot;,
                &quot;When from_date is missing, omit the from_date argument.&quot;,
                &quot;When limit is present, pass its value unchanged as the limit argument.&quot;,
                &quot;When limit is missing, omit the limit argument.&quot;,
                &quot;Apply the missing-argument settings in query configuration to this same call: missing_arguments.from_date = omit, missing_arguments.limit = omit.&quot;
              ],
              &quot;metadata&quot;: {},
              &quot;draft_instruction_id&quot;: &quot;call_index_search&quot;
            },
            {
              &quot;id&quot;: &quot;ir_008&quot;,
              &quot;opcode&quot;: &quot;dispatch&quot;,
              &quot;inputs&quot;: [],
              &quot;outputs&quot;: [],
              &quot;constraints&quot;: [],
              &quot;metadata&quot;: {},
              &quot;draft_instruction_id&quot;: &quot;go_post_search&quot;
            }
          ],
          &quot;constraints&quot;: [],
          &quot;data_source_kind&quot;: &quot;external&quot;
        },
        &quot;block_004&quot;: {
          &quot;block_id&quot;: &quot;block_004&quot;,
          &quot;block_name&quot;: &quot;Write the response total to count.txt and return the response items&quot;,
          &quot;instructions&quot;: [
            {
              &quot;id&quot;: &quot;ir_009&quot;,
              &quot;opcode&quot;: &quot;extract_response_total&quot;,
              &quot;inputs&quot;: [
                {
                  &quot;type&quot;: &quot;result&quot;,
                  &quot;identifier&quot;: &quot;result_007&quot;,
                  &quot;semantic_name&quot;: &quot;search_response&quot;
                }
              ],
              &quot;outputs&quot;: [
                {
                  &quot;type&quot;: &quot;result&quot;,
                  &quot;identifier&quot;: &quot;result_008&quot;,
                  &quot;semantic_name&quot;: &quot;search response total&quot;
                }
              ],
              &quot;constraints&quot;: [],
              &quot;metadata&quot;: {},
              &quot;draft_instruction_id&quot;: &quot;extract_response_total&quot;
            },
            {
              &quot;id&quot;: &quot;ir_010&quot;,
              &quot;opcode&quot;: &quot;write_count_file&quot;,
              &quot;inputs&quot;: [
                {
                  &quot;type&quot;: &quot;external_resource&quot;,
                  &quot;identifier&quot;: &quot;count.txt&quot;,
                  &quot;semantic_name&quot;: &quot;count.txt&quot;
                },
                {
                  &quot;type&quot;: &quot;result&quot;,
                  &quot;identifier&quot;: &quot;result_008&quot;,
                  &quot;semantic_name&quot;: &quot;response_total&quot;
                }
              ],
              &quot;outputs&quot;: [],
              &quot;constraints&quot;: [
                &quot;After the search, write the response&#x27;s total value to local count.txt.&quot;
              ],
              &quot;metadata&quot;: {},
              &quot;draft_instruction_id&quot;: &quot;write_count_file&quot;
            },
            {
              &quot;id&quot;: &quot;ir_011&quot;,
              &quot;opcode&quot;: &quot;extract_response_items&quot;,
              &quot;inputs&quot;: [
                {
                  &quot;type&quot;: &quot;result&quot;,
                  &quot;identifier&quot;: &quot;result_007&quot;,
                  &quot;semantic_name&quot;: &quot;search_response&quot;
                }
              ],
              &quot;outputs&quot;: [
                {
                  &quot;type&quot;: &quot;result&quot;,
                  &quot;identifier&quot;: &quot;result_009&quot;,
                  &quot;semantic_name&quot;: &quot;search response items&quot;
                }
              ],
              &quot;constraints&quot;: [],
              &quot;metadata&quot;: {},
              &quot;draft_instruction_id&quot;: &quot;extract_response_items&quot;
            },
            {
              &quot;id&quot;: &quot;ir_012&quot;,
              &quot;opcode&quot;: &quot;return&quot;,
              &quot;inputs&quot;: [
                {
                  &quot;type&quot;: &quot;result&quot;,
                  &quot;identifier&quot;: &quot;result_009&quot;,
                  &quot;semantic_name&quot;: &quot;response_items&quot;
                }
              ],
              &quot;outputs&quot;: [],
              &quot;constraints&quot;: [
                &quot;Return the search response&#x27;s items value unchanged.&quot;
              ],
              &quot;metadata&quot;: {},
              &quot;draft_instruction_id&quot;: &quot;return_items&quot;
            }
          ],
          &quot;constraints&quot;: [],
          &quot;data_source_kind&quot;: null
        }
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_1e4bea09f0d4266b3d20&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001&quot;,
      &quot;kind&quot;: &quot;block&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;
      ],
      &quot;value&quot;: {
        &quot;block_id&quot;: &quot;block_001&quot;,
        &quot;block_name&quot;: &quot;Read the user-supplied request.json&quot;,
        &quot;instructions&quot;: [
          {
            &quot;id&quot;: &quot;ir_001&quot;,
            &quot;opcode&quot;: &quot;read_request_json&quot;,
            &quot;inputs&quot;: [
              {
                &quot;type&quot;: &quot;external_resource&quot;,
                &quot;identifier&quot;: &quot;request.json&quot;,
                &quot;semantic_name&quot;: &quot;request.json&quot;
              }
            ],
            &quot;outputs&quot;: [
              {
                &quot;type&quot;: &quot;result&quot;,
                &quot;identifier&quot;: &quot;result_001&quot;,
                &quot;semantic_name&quot;: &quot;request.json contents&quot;
              }
            ],
            &quot;constraints&quot;: [],
            &quot;metadata&quot;: {},
            &quot;draft_instruction_id&quot;: &quot;read_request_json&quot;
          },
          {
            &quot;id&quot;: &quot;ir_002&quot;,
            &quot;opcode&quot;: &quot;dispatch&quot;,
            &quot;inputs&quot;: [],
            &quot;outputs&quot;: [],
            &quot;constraints&quot;: [],
            &quot;metadata&quot;: {},
            &quot;draft_instruction_id&quot;: &quot;go_extract_params&quot;
          }
        ],
        &quot;constraints&quot;: [],
        &quot;data_source_kind&quot;: &quot;external&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_95d32c00f41cba3ad713&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001/block_id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;,
        &quot;block_id&quot;
      ],
      &quot;value&quot;: &quot;block_001&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_11e9e64a7ad216822c4b&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001/block_name&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;,
        &quot;block_name&quot;
      ],
      &quot;value&quot;: &quot;Read the user-supplied request.json&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_fff2f261ee3ed9e131d6&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001/constraints&quot;,
      &quot;kind&quot;: &quot;constraints&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;,
        &quot;constraints&quot;
      ],
      &quot;value&quot;: [],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_d6363ce758fcc68a7413&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001/data_source_kind&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;,
        &quot;data_source_kind&quot;
      ],
      &quot;value&quot;: &quot;external&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_ff91fb104a9de4dbef80&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001/instructions&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;,
        &quot;instructions&quot;
      ],
      &quot;value&quot;: [
        {
          &quot;id&quot;: &quot;ir_001&quot;,
          &quot;opcode&quot;: &quot;read_request_json&quot;,
          &quot;inputs&quot;: [
            {
              &quot;type&quot;: &quot;external_resource&quot;,
              &quot;identifier&quot;: &quot;request.json&quot;,
              &quot;semantic_name&quot;: &quot;request.json&quot;
            }
          ],
          &quot;outputs&quot;: [
            {
              &quot;type&quot;: &quot;result&quot;,
              &quot;identifier&quot;: &quot;result_001&quot;,
              &quot;semantic_name&quot;: &quot;request.json contents&quot;
            }
          ],
          &quot;constraints&quot;: [],
          &quot;metadata&quot;: {},
          &quot;draft_instruction_id&quot;: &quot;read_request_json&quot;
        },
        {
          &quot;id&quot;: &quot;ir_002&quot;,
          &quot;opcode&quot;: &quot;dispatch&quot;,
          &quot;inputs&quot;: [],
          &quot;outputs&quot;: [],
          &quot;constraints&quot;: [],
          &quot;metadata&quot;: {},
          &quot;draft_instruction_id&quot;: &quot;go_extract_params&quot;
        }
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_c4a2ea86b75b76c41697&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001/instructions/0&quot;,
      &quot;kind&quot;: &quot;instruction&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;instruction_id&quot;: &quot;ir_001&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;,
        &quot;instructions&quot;,
        0
      ],
      &quot;value&quot;: {
        &quot;id&quot;: &quot;ir_001&quot;,
        &quot;opcode&quot;: &quot;read_request_json&quot;,
        &quot;inputs&quot;: [
          {
            &quot;type&quot;: &quot;external_resource&quot;,
            &quot;identifier&quot;: &quot;request.json&quot;,
            &quot;semantic_name&quot;: &quot;request.json&quot;
          }
        ],
        &quot;outputs&quot;: [
          {
            &quot;type&quot;: &quot;result&quot;,
            &quot;identifier&quot;: &quot;result_001&quot;,
            &quot;semantic_name&quot;: &quot;request.json contents&quot;
          }
        ],
        &quot;constraints&quot;: [],
        &quot;metadata&quot;: {},
        &quot;draft_instruction_id&quot;: &quot;read_request_json&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_fbf90c38d7f60f9ad64e&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001/instructions/0/constraints&quot;,
      &quot;kind&quot;: &quot;constraints&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;instruction_id&quot;: &quot;ir_001&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;,
        &quot;instructions&quot;,
        0,
        &quot;constraints&quot;
      ],
      &quot;value&quot;: [],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_7ef51b5327eccf65c25e&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001/instructions/0/draft_instruction_id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;instruction_id&quot;: &quot;ir_001&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;,
        &quot;instructions&quot;,
        0,
        &quot;draft_instruction_id&quot;
      ],
      &quot;value&quot;: &quot;read_request_json&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_8c98b00646f87106be18&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001/instructions/0/id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;instruction_id&quot;: &quot;ir_001&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;,
        &quot;instructions&quot;,
        0,
        &quot;id&quot;
      ],
      &quot;value&quot;: &quot;ir_001&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_c2d919b890dc94adf052&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001/instructions/0/inputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;instruction_id&quot;: &quot;ir_001&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;
      ],
      &quot;value&quot;: [
        {
          &quot;type&quot;: &quot;external_resource&quot;,
          &quot;identifier&quot;: &quot;request.json&quot;,
          &quot;semantic_name&quot;: &quot;request.json&quot;
        }
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_6afff9c218ebc2a39759&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001/instructions/0/inputs/0&quot;,
      &quot;kind&quot;: &quot;input&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;instruction_id&quot;: &quot;ir_001&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        0
      ],
      &quot;value&quot;: {
        &quot;type&quot;: &quot;external_resource&quot;,
        &quot;identifier&quot;: &quot;request.json&quot;,
        &quot;semantic_name&quot;: &quot;request.json&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_2f93607eae5aa7a036c9&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001/instructions/0/inputs/0/identifier&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;instruction_id&quot;: &quot;ir_001&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        0,
        &quot;identifier&quot;
      ],
      &quot;value&quot;: &quot;request.json&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_a1fa4cb5843177224a08&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001/instructions/0/inputs/0/semantic_name&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;instruction_id&quot;: &quot;ir_001&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        0,
        &quot;semantic_name&quot;
      ],
      &quot;value&quot;: &quot;request.json&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_9571f81637caef877ae7&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001/instructions/0/inputs/0/type&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;instruction_id&quot;: &quot;ir_001&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        0,
        &quot;type&quot;
      ],
      &quot;value&quot;: &quot;external_resource&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_abd06bd79c910e0bd602&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001/instructions/0/metadata&quot;,
      &quot;kind&quot;: &quot;metadata&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;instruction_id&quot;: &quot;ir_001&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;,
        &quot;instructions&quot;,
        0,
        &quot;metadata&quot;
      ],
      &quot;value&quot;: {},
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_358f58bded6bc936326a&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001/instructions/0/opcode&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;instruction_id&quot;: &quot;ir_001&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;,
        &quot;instructions&quot;,
        0,
        &quot;opcode&quot;
      ],
      &quot;value&quot;: &quot;read_request_json&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_eab2ef47f449ff3779b4&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001/instructions/0/outputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;instruction_id&quot;: &quot;ir_001&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;,
        &quot;instructions&quot;,
        0,
        &quot;outputs&quot;
      ],
      &quot;value&quot;: [
        {
          &quot;type&quot;: &quot;result&quot;,
          &quot;identifier&quot;: &quot;result_001&quot;,
          &quot;semantic_name&quot;: &quot;request.json contents&quot;
        }
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_f5d19a7fcef97798a846&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001/instructions/0/outputs/0&quot;,
      &quot;kind&quot;: &quot;output&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;instruction_id&quot;: &quot;ir_001&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;,
        &quot;instructions&quot;,
        0,
        &quot;outputs&quot;,
        0
      ],
      &quot;value&quot;: {
        &quot;type&quot;: &quot;result&quot;,
        &quot;identifier&quot;: &quot;result_001&quot;,
        &quot;semantic_name&quot;: &quot;request.json contents&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_a51ceffbb69cddc0003e&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001/instructions/0/outputs/0/identifier&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;instruction_id&quot;: &quot;ir_001&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;,
        &quot;instructions&quot;,
        0,
        &quot;outputs&quot;,
        0,
        &quot;identifier&quot;
      ],
      &quot;value&quot;: &quot;result_001&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_623936167bd8325fb585&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001/instructions/0/outputs/0/semantic_name&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;instruction_id&quot;: &quot;ir_001&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;,
        &quot;instructions&quot;,
        0,
        &quot;outputs&quot;,
        0,
        &quot;semantic_name&quot;
      ],
      &quot;value&quot;: &quot;request.json contents&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_5c3b0dbbd30e2aafd68c&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001/instructions/0/outputs/0/type&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;instruction_id&quot;: &quot;ir_001&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;,
        &quot;instructions&quot;,
        0,
        &quot;outputs&quot;,
        0,
        &quot;type&quot;
      ],
      &quot;value&quot;: &quot;result&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_4fc5ea2978d09b9eb5c5&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001/instructions/1&quot;,
      &quot;kind&quot;: &quot;instruction&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;instruction_id&quot;: &quot;ir_002&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;,
        &quot;instructions&quot;,
        1
      ],
      &quot;value&quot;: {
        &quot;id&quot;: &quot;ir_002&quot;,
        &quot;opcode&quot;: &quot;dispatch&quot;,
        &quot;inputs&quot;: [],
        &quot;outputs&quot;: [],
        &quot;constraints&quot;: [],
        &quot;metadata&quot;: {},
        &quot;draft_instruction_id&quot;: &quot;go_extract_params&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: true,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_c0724382d1b23603e76a&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001/instructions/1/constraints&quot;,
      &quot;kind&quot;: &quot;constraints&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;instruction_id&quot;: &quot;ir_002&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;,
        &quot;instructions&quot;,
        1,
        &quot;constraints&quot;
      ],
      &quot;value&quot;: [],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_38bd035b51e2a8ddd60e&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001/instructions/1/draft_instruction_id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;instruction_id&quot;: &quot;ir_002&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;,
        &quot;instructions&quot;,
        1,
        &quot;draft_instruction_id&quot;
      ],
      &quot;value&quot;: &quot;go_extract_params&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_f6322c9089ed36d067bd&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001/instructions/1/id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;instruction_id&quot;: &quot;ir_002&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;,
        &quot;instructions&quot;,
        1,
        &quot;id&quot;
      ],
      &quot;value&quot;: &quot;ir_002&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_3fe131b55efdbbf96b0b&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001/instructions/1/inputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;instruction_id&quot;: &quot;ir_002&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;,
        &quot;instructions&quot;,
        1,
        &quot;inputs&quot;
      ],
      &quot;value&quot;: [],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_0a08656ceb8f92b64c3e&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001/instructions/1/metadata&quot;,
      &quot;kind&quot;: &quot;metadata&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;instruction_id&quot;: &quot;ir_002&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;,
        &quot;instructions&quot;,
        1,
        &quot;metadata&quot;
      ],
      &quot;value&quot;: {},
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_e10decb40c7a584bac02&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001/instructions/1/opcode&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;instruction_id&quot;: &quot;ir_002&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;,
        &quot;instructions&quot;,
        1,
        &quot;opcode&quot;
      ],
      &quot;value&quot;: &quot;dispatch&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_3e69e68a174b26915359&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001/instructions/1/outputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;instruction_id&quot;: &quot;ir_002&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;,
        &quot;instructions&quot;,
        1,
        &quot;outputs&quot;
      ],
      &quot;value&quot;: [],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_bf73f50b0f2ff485e3f6&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002&quot;,
      &quot;kind&quot;: &quot;block&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;
      ],
      &quot;value&quot;: {
        &quot;block_id&quot;: &quot;block_002&quot;,
        &quot;block_name&quot;: &quot;Extract request.term and optional from_date and limit&quot;,
        &quot;instructions&quot;: [
          {
            &quot;id&quot;: &quot;ir_003&quot;,
            &quot;opcode&quot;: &quot;extract_query_term&quot;,
            &quot;inputs&quot;: [
              {
                &quot;type&quot;: &quot;result&quot;,
                &quot;identifier&quot;: &quot;result_001&quot;,
                &quot;semantic_name&quot;: &quot;request_data&quot;
              }
            ],
            &quot;outputs&quot;: [
              {
                &quot;type&quot;: &quot;result&quot;,
                &quot;identifier&quot;: &quot;result_002&quot;,
                &quot;semantic_name&quot;: &quot;request.term&quot;
              }
            ],
            &quot;constraints&quot;: [],
            &quot;metadata&quot;: {},
            &quot;draft_instruction_id&quot;: &quot;extract_query_term&quot;
          },
          {
            &quot;id&quot;: &quot;ir_004&quot;,
            &quot;opcode&quot;: &quot;extract_optional_from_date&quot;,
            &quot;inputs&quot;: [
              {
                &quot;type&quot;: &quot;result&quot;,
                &quot;identifier&quot;: &quot;result_001&quot;,
                &quot;semantic_name&quot;: &quot;request_data&quot;
              }
            ],
            &quot;outputs&quot;: [
              {
                &quot;type&quot;: &quot;result&quot;,
                &quot;identifier&quot;: &quot;result_003&quot;,
                &quot;semantic_name&quot;: &quot;request.from_date&quot;
              },
              {
                &quot;type&quot;: &quot;result&quot;,
                &quot;identifier&quot;: &quot;result_004&quot;,
                &quot;semantic_name&quot;: &quot;whether request.from_date is present&quot;
              }
            ],
            &quot;constraints&quot;: [],
            &quot;metadata&quot;: {},
            &quot;draft_instruction_id&quot;: &quot;extract_optional_from_date&quot;
          },
          {
            &quot;id&quot;: &quot;ir_005&quot;,
            &quot;opcode&quot;: &quot;extract_optional_limit&quot;,
            &quot;inputs&quot;: [
              {
                &quot;type&quot;: &quot;result&quot;,
                &quot;identifier&quot;: &quot;result_001&quot;,
                &quot;semantic_name&quot;: &quot;request_data&quot;
              }
            ],
            &quot;outputs&quot;: [
              {
                &quot;type&quot;: &quot;result&quot;,
                &quot;identifier&quot;: &quot;result_005&quot;,
                &quot;semantic_name&quot;: &quot;request.limit&quot;
              },
              {
                &quot;type&quot;: &quot;result&quot;,
                &quot;identifier&quot;: &quot;result_006&quot;,
                &quot;semantic_name&quot;: &quot;whether request.limit is present&quot;
              }
            ],
            &quot;constraints&quot;: [],
            &quot;metadata&quot;: {},
            &quot;draft_instruction_id&quot;: &quot;extract_optional_limit&quot;
          },
          {
            &quot;id&quot;: &quot;ir_006&quot;,
            &quot;opcode&quot;: &quot;dispatch&quot;,
            &quot;inputs&quot;: [],
            &quot;outputs&quot;: [],
            &quot;constraints&quot;: [],
            &quot;metadata&quot;: {},
            &quot;draft_instruction_id&quot;: &quot;go_search&quot;
          }
        ],
        &quot;constraints&quot;: [],
        &quot;data_source_kind&quot;: null
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_8f7ce8e55f205e500729&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/block_id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;block_id&quot;
      ],
      &quot;value&quot;: &quot;block_002&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_1ebdae7d64d926adb236&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/block_name&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;block_name&quot;
      ],
      &quot;value&quot;: &quot;Extract request.term and optional from_date and limit&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_8ec950a61b79d12f2c35&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/constraints&quot;,
      &quot;kind&quot;: &quot;constraints&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;constraints&quot;
      ],
      &quot;value&quot;: [],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_6db7a20519a5c32dcd69&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/data_source_kind&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;data_source_kind&quot;
      ],
      &quot;value&quot;: null,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_1ac8e74cc918cc73514f&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;
      ],
      &quot;value&quot;: [
        {
          &quot;id&quot;: &quot;ir_003&quot;,
          &quot;opcode&quot;: &quot;extract_query_term&quot;,
          &quot;inputs&quot;: [
            {
              &quot;type&quot;: &quot;result&quot;,
              &quot;identifier&quot;: &quot;result_001&quot;,
              &quot;semantic_name&quot;: &quot;request_data&quot;
            }
          ],
          &quot;outputs&quot;: [
            {
              &quot;type&quot;: &quot;result&quot;,
              &quot;identifier&quot;: &quot;result_002&quot;,
              &quot;semantic_name&quot;: &quot;request.term&quot;
            }
          ],
          &quot;constraints&quot;: [],
          &quot;metadata&quot;: {},
          &quot;draft_instruction_id&quot;: &quot;extract_query_term&quot;
        },
        {
          &quot;id&quot;: &quot;ir_004&quot;,
          &quot;opcode&quot;: &quot;extract_optional_from_date&quot;,
          &quot;inputs&quot;: [
            {
              &quot;type&quot;: &quot;result&quot;,
              &quot;identifier&quot;: &quot;result_001&quot;,
              &quot;semantic_name&quot;: &quot;request_data&quot;
            }
          ],
          &quot;outputs&quot;: [
            {
              &quot;type&quot;: &quot;result&quot;,
              &quot;identifier&quot;: &quot;result_003&quot;,
              &quot;semantic_name&quot;: &quot;request.from_date&quot;
            },
            {
              &quot;type&quot;: &quot;result&quot;,
              &quot;identifier&quot;: &quot;result_004&quot;,
              &quot;semantic_name&quot;: &quot;whether request.from_date is present&quot;
            }
          ],
          &quot;constraints&quot;: [],
          &quot;metadata&quot;: {},
          &quot;draft_instruction_id&quot;: &quot;extract_optional_from_date&quot;
        },
        {
          &quot;id&quot;: &quot;ir_005&quot;,
          &quot;opcode&quot;: &quot;extract_optional_limit&quot;,
          &quot;inputs&quot;: [
            {
              &quot;type&quot;: &quot;result&quot;,
              &quot;identifier&quot;: &quot;result_001&quot;,
              &quot;semantic_name&quot;: &quot;request_data&quot;
            }
          ],
          &quot;outputs&quot;: [
            {
              &quot;type&quot;: &quot;result&quot;,
              &quot;identifier&quot;: &quot;result_005&quot;,
              &quot;semantic_name&quot;: &quot;request.limit&quot;
            },
            {
              &quot;type&quot;: &quot;result&quot;,
              &quot;identifier&quot;: &quot;result_006&quot;,
              &quot;semantic_name&quot;: &quot;whether request.limit is present&quot;
            }
          ],
          &quot;constraints&quot;: [],
          &quot;metadata&quot;: {},
          &quot;draft_instruction_id&quot;: &quot;extract_optional_limit&quot;
        },
        {
          &quot;id&quot;: &quot;ir_006&quot;,
          &quot;opcode&quot;: &quot;dispatch&quot;,
          &quot;inputs&quot;: [],
          &quot;outputs&quot;: [],
          &quot;constraints&quot;: [],
          &quot;metadata&quot;: {},
          &quot;draft_instruction_id&quot;: &quot;go_search&quot;
        }
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_53c834a8f6a78ed63ce1&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/0&quot;,
      &quot;kind&quot;: &quot;instruction&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_003&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        0
      ],
      &quot;value&quot;: {
        &quot;id&quot;: &quot;ir_003&quot;,
        &quot;opcode&quot;: &quot;extract_query_term&quot;,
        &quot;inputs&quot;: [
          {
            &quot;type&quot;: &quot;result&quot;,
            &quot;identifier&quot;: &quot;result_001&quot;,
            &quot;semantic_name&quot;: &quot;request_data&quot;
          }
        ],
        &quot;outputs&quot;: [
          {
            &quot;type&quot;: &quot;result&quot;,
            &quot;identifier&quot;: &quot;result_002&quot;,
            &quot;semantic_name&quot;: &quot;request.term&quot;
          }
        ],
        &quot;constraints&quot;: [],
        &quot;metadata&quot;: {},
        &quot;draft_instruction_id&quot;: &quot;extract_query_term&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_1dabfa5e6de517f1d5bb&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/0/constraints&quot;,
      &quot;kind&quot;: &quot;constraints&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_003&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        0,
        &quot;constraints&quot;
      ],
      &quot;value&quot;: [],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_8d520edd9bc4dbcbbb2a&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/0/draft_instruction_id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_003&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        0,
        &quot;draft_instruction_id&quot;
      ],
      &quot;value&quot;: &quot;extract_query_term&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_e1877ecb434e782c1ca4&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/0/id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_003&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        0,
        &quot;id&quot;
      ],
      &quot;value&quot;: &quot;ir_003&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_f6d5b01d181c50e7dd02&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/0/inputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_003&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;
      ],
      &quot;value&quot;: [
        {
          &quot;type&quot;: &quot;result&quot;,
          &quot;identifier&quot;: &quot;result_001&quot;,
          &quot;semantic_name&quot;: &quot;request_data&quot;
        }
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_babedf937ff083c9cca5&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/0/inputs/0&quot;,
      &quot;kind&quot;: &quot;input&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_003&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        0
      ],
      &quot;value&quot;: {
        &quot;type&quot;: &quot;result&quot;,
        &quot;identifier&quot;: &quot;result_001&quot;,
        &quot;semantic_name&quot;: &quot;request_data&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_10bdd66250cac30d1a44&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/0/inputs/0/identifier&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_003&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        0,
        &quot;identifier&quot;
      ],
      &quot;value&quot;: &quot;result_001&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_68beabd5bd3d222a32b5&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/0/inputs/0/semantic_name&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_003&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        0,
        &quot;semantic_name&quot;
      ],
      &quot;value&quot;: &quot;request_data&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_eea9641918b195b13fd7&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/0/inputs/0/type&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_003&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        0,
        &quot;type&quot;
      ],
      &quot;value&quot;: &quot;result&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_30e53b4148c3df21182a&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/0/metadata&quot;,
      &quot;kind&quot;: &quot;metadata&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_003&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        0,
        &quot;metadata&quot;
      ],
      &quot;value&quot;: {},
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_983234f7e3be164db63f&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/0/opcode&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_003&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        0,
        &quot;opcode&quot;
      ],
      &quot;value&quot;: &quot;extract_query_term&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_542f87e9eaf3cb6e7ee3&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/0/outputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_003&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        0,
        &quot;outputs&quot;
      ],
      &quot;value&quot;: [
        {
          &quot;type&quot;: &quot;result&quot;,
          &quot;identifier&quot;: &quot;result_002&quot;,
          &quot;semantic_name&quot;: &quot;request.term&quot;
        }
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_0c1491125c133aecbdd7&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/0/outputs/0&quot;,
      &quot;kind&quot;: &quot;output&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_003&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        0,
        &quot;outputs&quot;,
        0
      ],
      &quot;value&quot;: {
        &quot;type&quot;: &quot;result&quot;,
        &quot;identifier&quot;: &quot;result_002&quot;,
        &quot;semantic_name&quot;: &quot;request.term&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_5bb617bf0fb5b1891679&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/0/outputs/0/identifier&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_003&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        0,
        &quot;outputs&quot;,
        0,
        &quot;identifier&quot;
      ],
      &quot;value&quot;: &quot;result_002&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_4bc1bb2a76d79324f6c2&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/0/outputs/0/semantic_name&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_003&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        0,
        &quot;outputs&quot;,
        0,
        &quot;semantic_name&quot;
      ],
      &quot;value&quot;: &quot;request.term&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_178d1813bd03e091a8b3&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/0/outputs/0/type&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_003&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        0,
        &quot;outputs&quot;,
        0,
        &quot;type&quot;
      ],
      &quot;value&quot;: &quot;result&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_1939028382132efd27e5&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/1&quot;,
      &quot;kind&quot;: &quot;instruction&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        1
      ],
      &quot;value&quot;: {
        &quot;id&quot;: &quot;ir_004&quot;,
        &quot;opcode&quot;: &quot;extract_optional_from_date&quot;,
        &quot;inputs&quot;: [
          {
            &quot;type&quot;: &quot;result&quot;,
            &quot;identifier&quot;: &quot;result_001&quot;,
            &quot;semantic_name&quot;: &quot;request_data&quot;
          }
        ],
        &quot;outputs&quot;: [
          {
            &quot;type&quot;: &quot;result&quot;,
            &quot;identifier&quot;: &quot;result_003&quot;,
            &quot;semantic_name&quot;: &quot;request.from_date&quot;
          },
          {
            &quot;type&quot;: &quot;result&quot;,
            &quot;identifier&quot;: &quot;result_004&quot;,
            &quot;semantic_name&quot;: &quot;whether request.from_date is present&quot;
          }
        ],
        &quot;constraints&quot;: [],
        &quot;metadata&quot;: {},
        &quot;draft_instruction_id&quot;: &quot;extract_optional_from_date&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_15c2b87d7bc7d5e14163&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/1/constraints&quot;,
      &quot;kind&quot;: &quot;constraints&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        1,
        &quot;constraints&quot;
      ],
      &quot;value&quot;: [],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_09afd813b248e3c5f81c&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/1/draft_instruction_id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        1,
        &quot;draft_instruction_id&quot;
      ],
      &quot;value&quot;: &quot;extract_optional_from_date&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_caf34e7027a6a1b4bdc0&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/1/id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        1,
        &quot;id&quot;
      ],
      &quot;value&quot;: &quot;ir_004&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_15a923bb2f6798789608&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/1/inputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        1,
        &quot;inputs&quot;
      ],
      &quot;value&quot;: [
        {
          &quot;type&quot;: &quot;result&quot;,
          &quot;identifier&quot;: &quot;result_001&quot;,
          &quot;semantic_name&quot;: &quot;request_data&quot;
        }
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_9041b6bfe31cd13becb5&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/1/inputs/0&quot;,
      &quot;kind&quot;: &quot;input&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        1,
        &quot;inputs&quot;,
        0
      ],
      &quot;value&quot;: {
        &quot;type&quot;: &quot;result&quot;,
        &quot;identifier&quot;: &quot;result_001&quot;,
        &quot;semantic_name&quot;: &quot;request_data&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_999325421c5ec7bfd982&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/1/inputs/0/identifier&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        1,
        &quot;inputs&quot;,
        0,
        &quot;identifier&quot;
      ],
      &quot;value&quot;: &quot;result_001&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_22522d6265f433c6f079&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/1/inputs/0/semantic_name&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        1,
        &quot;inputs&quot;,
        0,
        &quot;semantic_name&quot;
      ],
      &quot;value&quot;: &quot;request_data&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_78642ae4989fc7428443&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/1/inputs/0/type&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        1,
        &quot;inputs&quot;,
        0,
        &quot;type&quot;
      ],
      &quot;value&quot;: &quot;result&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_a9d45dac5844f43af2cd&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/1/metadata&quot;,
      &quot;kind&quot;: &quot;metadata&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        1,
        &quot;metadata&quot;
      ],
      &quot;value&quot;: {},
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_da713dd7d60299ae5c93&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/1/opcode&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        1,
        &quot;opcode&quot;
      ],
      &quot;value&quot;: &quot;extract_optional_from_date&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_de21dd0d67dade14c011&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/1/outputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        1,
        &quot;outputs&quot;
      ],
      &quot;value&quot;: [
        {
          &quot;type&quot;: &quot;result&quot;,
          &quot;identifier&quot;: &quot;result_003&quot;,
          &quot;semantic_name&quot;: &quot;request.from_date&quot;
        },
        {
          &quot;type&quot;: &quot;result&quot;,
          &quot;identifier&quot;: &quot;result_004&quot;,
          &quot;semantic_name&quot;: &quot;whether request.from_date is present&quot;
        }
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_4d4fcffda7569d099934&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/1/outputs/0&quot;,
      &quot;kind&quot;: &quot;output&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        1,
        &quot;outputs&quot;,
        0
      ],
      &quot;value&quot;: {
        &quot;type&quot;: &quot;result&quot;,
        &quot;identifier&quot;: &quot;result_003&quot;,
        &quot;semantic_name&quot;: &quot;request.from_date&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_d75fcb0b0d949557fc79&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/1/outputs/0/identifier&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        1,
        &quot;outputs&quot;,
        0,
        &quot;identifier&quot;
      ],
      &quot;value&quot;: &quot;result_003&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_949cf68f1a3158c506a4&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/1/outputs/0/semantic_name&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        1,
        &quot;outputs&quot;,
        0,
        &quot;semantic_name&quot;
      ],
      &quot;value&quot;: &quot;request.from_date&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_8d44dd01c50786aa88eb&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/1/outputs/0/type&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        1,
        &quot;outputs&quot;,
        0,
        &quot;type&quot;
      ],
      &quot;value&quot;: &quot;result&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_222bc62b34e23c680614&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/1/outputs/1&quot;,
      &quot;kind&quot;: &quot;output&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        1,
        &quot;outputs&quot;,
        1
      ],
      &quot;value&quot;: {
        &quot;type&quot;: &quot;result&quot;,
        &quot;identifier&quot;: &quot;result_004&quot;,
        &quot;semantic_name&quot;: &quot;whether request.from_date is present&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_934a19d841cc616723d1&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/1/outputs/1/identifier&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        1,
        &quot;outputs&quot;,
        1,
        &quot;identifier&quot;
      ],
      &quot;value&quot;: &quot;result_004&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_968a9e14ba3949fcdc5d&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/1/outputs/1/semantic_name&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        1,
        &quot;outputs&quot;,
        1,
        &quot;semantic_name&quot;
      ],
      &quot;value&quot;: &quot;whether request.from_date is present&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_3f47818e2e55e05ad25e&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/1/outputs/1/type&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        1,
        &quot;outputs&quot;,
        1,
        &quot;type&quot;
      ],
      &quot;value&quot;: &quot;result&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_ede8bb9e7023d7d2bf7c&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/2&quot;,
      &quot;kind&quot;: &quot;instruction&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        2
      ],
      &quot;value&quot;: {
        &quot;id&quot;: &quot;ir_005&quot;,
        &quot;opcode&quot;: &quot;extract_optional_limit&quot;,
        &quot;inputs&quot;: [
          {
            &quot;type&quot;: &quot;result&quot;,
            &quot;identifier&quot;: &quot;result_001&quot;,
            &quot;semantic_name&quot;: &quot;request_data&quot;
          }
        ],
        &quot;outputs&quot;: [
          {
            &quot;type&quot;: &quot;result&quot;,
            &quot;identifier&quot;: &quot;result_005&quot;,
            &quot;semantic_name&quot;: &quot;request.limit&quot;
          },
          {
            &quot;type&quot;: &quot;result&quot;,
            &quot;identifier&quot;: &quot;result_006&quot;,
            &quot;semantic_name&quot;: &quot;whether request.limit is present&quot;
          }
        ],
        &quot;constraints&quot;: [],
        &quot;metadata&quot;: {},
        &quot;draft_instruction_id&quot;: &quot;extract_optional_limit&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_f310fb36897dbed9e0a5&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/2/constraints&quot;,
      &quot;kind&quot;: &quot;constraints&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        2,
        &quot;constraints&quot;
      ],
      &quot;value&quot;: [],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_6a397573351c2e0937a4&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/2/draft_instruction_id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        2,
        &quot;draft_instruction_id&quot;
      ],
      &quot;value&quot;: &quot;extract_optional_limit&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_7c865647d6fd2c67860a&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/2/id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        2,
        &quot;id&quot;
      ],
      &quot;value&quot;: &quot;ir_005&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_53875a6990b86e09b263&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/2/inputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        2,
        &quot;inputs&quot;
      ],
      &quot;value&quot;: [
        {
          &quot;type&quot;: &quot;result&quot;,
          &quot;identifier&quot;: &quot;result_001&quot;,
          &quot;semantic_name&quot;: &quot;request_data&quot;
        }
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_83347bdb3ec562fe5a0b&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/2/inputs/0&quot;,
      &quot;kind&quot;: &quot;input&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        2,
        &quot;inputs&quot;,
        0
      ],
      &quot;value&quot;: {
        &quot;type&quot;: &quot;result&quot;,
        &quot;identifier&quot;: &quot;result_001&quot;,
        &quot;semantic_name&quot;: &quot;request_data&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_443097f611de5cc1e382&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/2/inputs/0/identifier&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        2,
        &quot;inputs&quot;,
        0,
        &quot;identifier&quot;
      ],
      &quot;value&quot;: &quot;result_001&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_d382dd064fd9b1a733d6&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/2/inputs/0/semantic_name&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        2,
        &quot;inputs&quot;,
        0,
        &quot;semantic_name&quot;
      ],
      &quot;value&quot;: &quot;request_data&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_d5feb752b06e8980845d&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/2/inputs/0/type&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        2,
        &quot;inputs&quot;,
        0,
        &quot;type&quot;
      ],
      &quot;value&quot;: &quot;result&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_87555b2889fd5ce5989d&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/2/metadata&quot;,
      &quot;kind&quot;: &quot;metadata&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        2,
        &quot;metadata&quot;
      ],
      &quot;value&quot;: {},
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_a3ebc09201b7c54dcc51&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/2/opcode&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        2,
        &quot;opcode&quot;
      ],
      &quot;value&quot;: &quot;extract_optional_limit&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_2c08216d70710cd67bf8&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/2/outputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        2,
        &quot;outputs&quot;
      ],
      &quot;value&quot;: [
        {
          &quot;type&quot;: &quot;result&quot;,
          &quot;identifier&quot;: &quot;result_005&quot;,
          &quot;semantic_name&quot;: &quot;request.limit&quot;
        },
        {
          &quot;type&quot;: &quot;result&quot;,
          &quot;identifier&quot;: &quot;result_006&quot;,
          &quot;semantic_name&quot;: &quot;whether request.limit is present&quot;
        }
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_005630f76d2a2e75e9b3&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/2/outputs/0&quot;,
      &quot;kind&quot;: &quot;output&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        2,
        &quot;outputs&quot;,
        0
      ],
      &quot;value&quot;: {
        &quot;type&quot;: &quot;result&quot;,
        &quot;identifier&quot;: &quot;result_005&quot;,
        &quot;semantic_name&quot;: &quot;request.limit&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_4be0e4d84fad99206d3d&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/2/outputs/0/identifier&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        2,
        &quot;outputs&quot;,
        0,
        &quot;identifier&quot;
      ],
      &quot;value&quot;: &quot;result_005&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_da9a00d3ba153ff11171&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/2/outputs/0/semantic_name&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        2,
        &quot;outputs&quot;,
        0,
        &quot;semantic_name&quot;
      ],
      &quot;value&quot;: &quot;request.limit&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_d211f8af0aa730a1be5c&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/2/outputs/0/type&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        2,
        &quot;outputs&quot;,
        0,
        &quot;type&quot;
      ],
      &quot;value&quot;: &quot;result&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_aeeeab5815bd257a0254&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/2/outputs/1&quot;,
      &quot;kind&quot;: &quot;output&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        2,
        &quot;outputs&quot;,
        1
      ],
      &quot;value&quot;: {
        &quot;type&quot;: &quot;result&quot;,
        &quot;identifier&quot;: &quot;result_006&quot;,
        &quot;semantic_name&quot;: &quot;whether request.limit is present&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_a550afb4e8c371702819&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/2/outputs/1/identifier&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        2,
        &quot;outputs&quot;,
        1,
        &quot;identifier&quot;
      ],
      &quot;value&quot;: &quot;result_006&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_bcbbf5c1fe7f99a1973c&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/2/outputs/1/semantic_name&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        2,
        &quot;outputs&quot;,
        1,
        &quot;semantic_name&quot;
      ],
      &quot;value&quot;: &quot;whether request.limit is present&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_9776b0b8f34e1b2a4612&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/2/outputs/1/type&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        2,
        &quot;outputs&quot;,
        1,
        &quot;type&quot;
      ],
      &quot;value&quot;: &quot;result&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_134fd71783e4aad34356&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/3&quot;,
      &quot;kind&quot;: &quot;instruction&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_006&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        3
      ],
      &quot;value&quot;: {
        &quot;id&quot;: &quot;ir_006&quot;,
        &quot;opcode&quot;: &quot;dispatch&quot;,
        &quot;inputs&quot;: [],
        &quot;outputs&quot;: [],
        &quot;constraints&quot;: [],
        &quot;metadata&quot;: {},
        &quot;draft_instruction_id&quot;: &quot;go_search&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: true,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_3fec90935dd2d5bb229c&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/3/constraints&quot;,
      &quot;kind&quot;: &quot;constraints&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_006&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        3,
        &quot;constraints&quot;
      ],
      &quot;value&quot;: [],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_8eb3522c20b7d3f20f32&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/3/draft_instruction_id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_006&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        3,
        &quot;draft_instruction_id&quot;
      ],
      &quot;value&quot;: &quot;go_search&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_cc2b872f8362352f661c&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/3/id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_006&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        3,
        &quot;id&quot;
      ],
      &quot;value&quot;: &quot;ir_006&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_83fc9b38926e6a60185d&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/3/inputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_006&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        3,
        &quot;inputs&quot;
      ],
      &quot;value&quot;: [],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_1516b1aa4c3bb34aabe3&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/3/metadata&quot;,
      &quot;kind&quot;: &quot;metadata&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_006&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        3,
        &quot;metadata&quot;
      ],
      &quot;value&quot;: {},
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_7e415887341d77c30bf8&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/3/opcode&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_006&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        3,
        &quot;opcode&quot;
      ],
      &quot;value&quot;: &quot;dispatch&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_83157cdf9633ad80c4ee&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/3/outputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_006&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        3,
        &quot;outputs&quot;
      ],
      &quot;value&quot;: [],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_69cd323c3771f3afe971&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003&quot;,
      &quot;kind&quot;: &quot;block&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;
      ],
      &quot;value&quot;: {
        &quot;block_id&quot;: &quot;block_003&quot;,
        &quot;block_name&quot;: &quot;Call index.search once with the request term and optional arguments&quot;,
        &quot;instructions&quot;: [
          {
            &quot;id&quot;: &quot;ir_007&quot;,
            &quot;opcode&quot;: &quot;index.search&quot;,
            &quot;inputs&quot;: [
              {
                &quot;type&quot;: &quot;external_resource&quot;,
                &quot;identifier&quot;: &quot;index.search&quot;,
                &quot;semantic_name&quot;: &quot;index.search&quot;
              },
              {
                &quot;type&quot;: &quot;result&quot;,
                &quot;identifier&quot;: &quot;result_002&quot;,
                &quot;semantic_name&quot;: &quot;query_term&quot;
              },
              {
                &quot;type&quot;: &quot;result&quot;,
                &quot;identifier&quot;: &quot;result_003&quot;,
                &quot;semantic_name&quot;: &quot;from_date_value&quot;
              },
              {
                &quot;type&quot;: &quot;result&quot;,
                &quot;identifier&quot;: &quot;result_004&quot;,
                &quot;semantic_name&quot;: &quot;from_date_present&quot;
              },
              {
                &quot;type&quot;: &quot;result&quot;,
                &quot;identifier&quot;: &quot;result_005&quot;,
                &quot;semantic_name&quot;: &quot;limit_value&quot;
              },
              {
                &quot;type&quot;: &quot;result&quot;,
                &quot;identifier&quot;: &quot;result_006&quot;,
                &quot;semantic_name&quot;: &quot;limit_present&quot;
              }
            ],
            &quot;outputs&quot;: [
              {
                &quot;type&quot;: &quot;result&quot;,
                &quot;identifier&quot;: &quot;result_007&quot;,
                &quot;semantic_name&quot;: &quot;index.search response&quot;
              }
            ],
            &quot;constraints&quot;: [
              &quot;Use request.term unchanged as its query argument.&quot;,
              &quot;When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.&quot;,
              &quot;When from_date is missing, omit the from_date argument.&quot;,
              &quot;When limit is present, pass its value unchanged as the limit argument.&quot;,
              &quot;When limit is missing, omit the limit argument.&quot;,
              &quot;Apply the missing-argument settings in query configuration to this same call: missing_arguments.from_date = omit, missing_arguments.limit = omit.&quot;
            ],
            &quot;metadata&quot;: {},
            &quot;draft_instruction_id&quot;: &quot;call_index_search&quot;
          },
          {
            &quot;id&quot;: &quot;ir_008&quot;,
            &quot;opcode&quot;: &quot;dispatch&quot;,
            &quot;inputs&quot;: [],
            &quot;outputs&quot;: [],
            &quot;constraints&quot;: [],
            &quot;metadata&quot;: {},
            &quot;draft_instruction_id&quot;: &quot;go_post_search&quot;
          }
        ],
        &quot;constraints&quot;: [],
        &quot;data_source_kind&quot;: &quot;external&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_36a7554f2d63f10a66f7&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/block_id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;block_id&quot;
      ],
      &quot;value&quot;: &quot;block_003&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_33022a65bda7710cd2fb&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/block_name&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;block_name&quot;
      ],
      &quot;value&quot;: &quot;Call index.search once with the request term and optional arguments&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_62d0979eccdab863b119&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/constraints&quot;,
      &quot;kind&quot;: &quot;constraints&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;constraints&quot;
      ],
      &quot;value&quot;: [],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_40eff9c26161317ec5a0&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/data_source_kind&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;data_source_kind&quot;
      ],
      &quot;value&quot;: &quot;external&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_c75f2c23923f067e0772&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;
      ],
      &quot;value&quot;: [
        {
          &quot;id&quot;: &quot;ir_007&quot;,
          &quot;opcode&quot;: &quot;index.search&quot;,
          &quot;inputs&quot;: [
            {
              &quot;type&quot;: &quot;external_resource&quot;,
              &quot;identifier&quot;: &quot;index.search&quot;,
              &quot;semantic_name&quot;: &quot;index.search&quot;
            },
            {
              &quot;type&quot;: &quot;result&quot;,
              &quot;identifier&quot;: &quot;result_002&quot;,
              &quot;semantic_name&quot;: &quot;query_term&quot;
            },
            {
              &quot;type&quot;: &quot;result&quot;,
              &quot;identifier&quot;: &quot;result_003&quot;,
              &quot;semantic_name&quot;: &quot;from_date_value&quot;
            },
            {
              &quot;type&quot;: &quot;result&quot;,
              &quot;identifier&quot;: &quot;result_004&quot;,
              &quot;semantic_name&quot;: &quot;from_date_present&quot;
            },
            {
              &quot;type&quot;: &quot;result&quot;,
              &quot;identifier&quot;: &quot;result_005&quot;,
              &quot;semantic_name&quot;: &quot;limit_value&quot;
            },
            {
              &quot;type&quot;: &quot;result&quot;,
              &quot;identifier&quot;: &quot;result_006&quot;,
              &quot;semantic_name&quot;: &quot;limit_present&quot;
            }
          ],
          &quot;outputs&quot;: [
            {
              &quot;type&quot;: &quot;result&quot;,
              &quot;identifier&quot;: &quot;result_007&quot;,
              &quot;semantic_name&quot;: &quot;index.search response&quot;
            }
          ],
          &quot;constraints&quot;: [
            &quot;Use request.term unchanged as its query argument.&quot;,
            &quot;When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.&quot;,
            &quot;When from_date is missing, omit the from_date argument.&quot;,
            &quot;When limit is present, pass its value unchanged as the limit argument.&quot;,
            &quot;When limit is missing, omit the limit argument.&quot;,
            &quot;Apply the missing-argument settings in query configuration to this same call: missing_arguments.from_date = omit, missing_arguments.limit = omit.&quot;
          ],
          &quot;metadata&quot;: {},
          &quot;draft_instruction_id&quot;: &quot;call_index_search&quot;
        },
        {
          &quot;id&quot;: &quot;ir_008&quot;,
          &quot;opcode&quot;: &quot;dispatch&quot;,
          &quot;inputs&quot;: [],
          &quot;outputs&quot;: [],
          &quot;constraints&quot;: [],
          &quot;metadata&quot;: {},
          &quot;draft_instruction_id&quot;: &quot;go_post_search&quot;
        }
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_4249450d80896db9f16c&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0&quot;,
      &quot;kind&quot;: &quot;instruction&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0
      ],
      &quot;value&quot;: {
        &quot;id&quot;: &quot;ir_007&quot;,
        &quot;opcode&quot;: &quot;index.search&quot;,
        &quot;inputs&quot;: [
          {
            &quot;type&quot;: &quot;external_resource&quot;,
            &quot;identifier&quot;: &quot;index.search&quot;,
            &quot;semantic_name&quot;: &quot;index.search&quot;
          },
          {
            &quot;type&quot;: &quot;result&quot;,
            &quot;identifier&quot;: &quot;result_002&quot;,
            &quot;semantic_name&quot;: &quot;query_term&quot;
          },
          {
            &quot;type&quot;: &quot;result&quot;,
            &quot;identifier&quot;: &quot;result_003&quot;,
            &quot;semantic_name&quot;: &quot;from_date_value&quot;
          },
          {
            &quot;type&quot;: &quot;result&quot;,
            &quot;identifier&quot;: &quot;result_004&quot;,
            &quot;semantic_name&quot;: &quot;from_date_present&quot;
          },
          {
            &quot;type&quot;: &quot;result&quot;,
            &quot;identifier&quot;: &quot;result_005&quot;,
            &quot;semantic_name&quot;: &quot;limit_value&quot;
          },
          {
            &quot;type&quot;: &quot;result&quot;,
            &quot;identifier&quot;: &quot;result_006&quot;,
            &quot;semantic_name&quot;: &quot;limit_present&quot;
          }
        ],
        &quot;outputs&quot;: [
          {
            &quot;type&quot;: &quot;result&quot;,
            &quot;identifier&quot;: &quot;result_007&quot;,
            &quot;semantic_name&quot;: &quot;index.search response&quot;
          }
        ],
        &quot;constraints&quot;: [
          &quot;Use request.term unchanged as its query argument.&quot;,
          &quot;When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.&quot;,
          &quot;When from_date is missing, omit the from_date argument.&quot;,
          &quot;When limit is present, pass its value unchanged as the limit argument.&quot;,
          &quot;When limit is missing, omit the limit argument.&quot;,
          &quot;Apply the missing-argument settings in query configuration to this same call: missing_arguments.from_date = omit, missing_arguments.limit = omit.&quot;
        ],
        &quot;metadata&quot;: {},
        &quot;draft_instruction_id&quot;: &quot;call_index_search&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_87dafedba9a1d78f1675&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/constraints&quot;,
      &quot;kind&quot;: &quot;constraints&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;constraints&quot;
      ],
      &quot;value&quot;: [
        &quot;Use request.term unchanged as its query argument.&quot;,
        &quot;When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.&quot;,
        &quot;When from_date is missing, omit the from_date argument.&quot;,
        &quot;When limit is present, pass its value unchanged as the limit argument.&quot;,
        &quot;When limit is missing, omit the limit argument.&quot;,
        &quot;Apply the missing-argument settings in query configuration to this same call: missing_arguments.from_date = omit, missing_arguments.limit = omit.&quot;
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_aeb48f99c87b5433380d&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/constraints/0&quot;,
      &quot;kind&quot;: &quot;constraint&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;constraints&quot;,
        0
      ],
      &quot;value&quot;: &quot;Use request.term unchanged as its query argument.&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_2a168b4a5f91acde4f8e&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/constraints/1&quot;,
      &quot;kind&quot;: &quot;constraint&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;constraints&quot;,
        1
      ],
      &quot;value&quot;: &quot;When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_8fe35635386dff487a10&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/constraints/2&quot;,
      &quot;kind&quot;: &quot;constraint&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;constraints&quot;,
        2
      ],
      &quot;value&quot;: &quot;When from_date is missing, omit the from_date argument.&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_a5a1aecc877f545de2a1&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/constraints/3&quot;,
      &quot;kind&quot;: &quot;constraint&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;constraints&quot;,
        3
      ],
      &quot;value&quot;: &quot;When limit is present, pass its value unchanged as the limit argument.&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_f105e162947fa55e18de&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/constraints/4&quot;,
      &quot;kind&quot;: &quot;constraint&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;constraints&quot;,
        4
      ],
      &quot;value&quot;: &quot;When limit is missing, omit the limit argument.&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_42dc0e936fde6af51a36&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/constraints/5&quot;,
      &quot;kind&quot;: &quot;constraint&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;constraints&quot;,
        5
      ],
      &quot;value&quot;: &quot;Apply the missing-argument settings in query configuration to this same call: missing_arguments.from_date = omit, missing_arguments.limit = omit.&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_19141a1b733b451ee90a&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/draft_instruction_id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;draft_instruction_id&quot;
      ],
      &quot;value&quot;: &quot;call_index_search&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_472ee958be2d1a82d1f9&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;id&quot;
      ],
      &quot;value&quot;: &quot;ir_007&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_cea4e4ee9a491bac6ef2&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;
      ],
      &quot;value&quot;: [
        {
          &quot;type&quot;: &quot;external_resource&quot;,
          &quot;identifier&quot;: &quot;index.search&quot;,
          &quot;semantic_name&quot;: &quot;index.search&quot;
        },
        {
          &quot;type&quot;: &quot;result&quot;,
          &quot;identifier&quot;: &quot;result_002&quot;,
          &quot;semantic_name&quot;: &quot;query_term&quot;
        },
        {
          &quot;type&quot;: &quot;result&quot;,
          &quot;identifier&quot;: &quot;result_003&quot;,
          &quot;semantic_name&quot;: &quot;from_date_value&quot;
        },
        {
          &quot;type&quot;: &quot;result&quot;,
          &quot;identifier&quot;: &quot;result_004&quot;,
          &quot;semantic_name&quot;: &quot;from_date_present&quot;
        },
        {
          &quot;type&quot;: &quot;result&quot;,
          &quot;identifier&quot;: &quot;result_005&quot;,
          &quot;semantic_name&quot;: &quot;limit_value&quot;
        },
        {
          &quot;type&quot;: &quot;result&quot;,
          &quot;identifier&quot;: &quot;result_006&quot;,
          &quot;semantic_name&quot;: &quot;limit_present&quot;
        }
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_4b7cacd582eecfb84195&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/0&quot;,
      &quot;kind&quot;: &quot;input&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        0
      ],
      &quot;value&quot;: {
        &quot;type&quot;: &quot;external_resource&quot;,
        &quot;identifier&quot;: &quot;index.search&quot;,
        &quot;semantic_name&quot;: &quot;index.search&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_81b13a64b9385b6d8b83&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/0/identifier&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        0,
        &quot;identifier&quot;
      ],
      &quot;value&quot;: &quot;index.search&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_9b9e8992bb86b517ee65&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/0/semantic_name&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        0,
        &quot;semantic_name&quot;
      ],
      &quot;value&quot;: &quot;index.search&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_67ca50f0790e15c71f64&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/0/type&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        0,
        &quot;type&quot;
      ],
      &quot;value&quot;: &quot;external_resource&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_70c96dfd296c8130066b&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/1&quot;,
      &quot;kind&quot;: &quot;input&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        1
      ],
      &quot;value&quot;: {
        &quot;type&quot;: &quot;result&quot;,
        &quot;identifier&quot;: &quot;result_002&quot;,
        &quot;semantic_name&quot;: &quot;query_term&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_49c48d0f59a29b3e8e8a&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/1/identifier&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        1,
        &quot;identifier&quot;
      ],
      &quot;value&quot;: &quot;result_002&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_96d296de488397c7ca70&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/1/semantic_name&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        1,
        &quot;semantic_name&quot;
      ],
      &quot;value&quot;: &quot;query_term&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_6db0fa07cb50eee0f651&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/1/type&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        1,
        &quot;type&quot;
      ],
      &quot;value&quot;: &quot;result&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_d49b7dd46f8209dbe334&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/2&quot;,
      &quot;kind&quot;: &quot;input&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        2
      ],
      &quot;value&quot;: {
        &quot;type&quot;: &quot;result&quot;,
        &quot;identifier&quot;: &quot;result_003&quot;,
        &quot;semantic_name&quot;: &quot;from_date_value&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_b21b1f4eac5dc2d155a6&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/2/identifier&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        2,
        &quot;identifier&quot;
      ],
      &quot;value&quot;: &quot;result_003&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_5aaaf0b10a3340e203dd&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/2/semantic_name&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        2,
        &quot;semantic_name&quot;
      ],
      &quot;value&quot;: &quot;from_date_value&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_336e221dd239eb5cdb28&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/2/type&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        2,
        &quot;type&quot;
      ],
      &quot;value&quot;: &quot;result&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_77b9604eaae52b5abbc6&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/3&quot;,
      &quot;kind&quot;: &quot;input&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        3
      ],
      &quot;value&quot;: {
        &quot;type&quot;: &quot;result&quot;,
        &quot;identifier&quot;: &quot;result_004&quot;,
        &quot;semantic_name&quot;: &quot;from_date_present&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_fe41be4473bb8bb98158&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/3/identifier&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        3,
        &quot;identifier&quot;
      ],
      &quot;value&quot;: &quot;result_004&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_1fa24c249dc65c742fd2&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/3/semantic_name&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        3,
        &quot;semantic_name&quot;
      ],
      &quot;value&quot;: &quot;from_date_present&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_f039e2534f3fb445070d&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/3/type&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        3,
        &quot;type&quot;
      ],
      &quot;value&quot;: &quot;result&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_c171aff2761c13f2d18a&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/4&quot;,
      &quot;kind&quot;: &quot;input&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        4
      ],
      &quot;value&quot;: {
        &quot;type&quot;: &quot;result&quot;,
        &quot;identifier&quot;: &quot;result_005&quot;,
        &quot;semantic_name&quot;: &quot;limit_value&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_c117f8310523d975ebe4&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/4/identifier&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        4,
        &quot;identifier&quot;
      ],
      &quot;value&quot;: &quot;result_005&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_5d8a137ecab4e2121b74&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/4/semantic_name&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        4,
        &quot;semantic_name&quot;
      ],
      &quot;value&quot;: &quot;limit_value&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_d7e6d6055ffe07e06429&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/4/type&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        4,
        &quot;type&quot;
      ],
      &quot;value&quot;: &quot;result&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_6389bd8eefc49bff667a&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/5&quot;,
      &quot;kind&quot;: &quot;input&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        5
      ],
      &quot;value&quot;: {
        &quot;type&quot;: &quot;result&quot;,
        &quot;identifier&quot;: &quot;result_006&quot;,
        &quot;semantic_name&quot;: &quot;limit_present&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_81839156ba3bb74eab37&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/5/identifier&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        5,
        &quot;identifier&quot;
      ],
      &quot;value&quot;: &quot;result_006&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_99faa33da6ded5653534&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/5/semantic_name&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        5,
        &quot;semantic_name&quot;
      ],
      &quot;value&quot;: &quot;limit_present&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_44d51338f72fbc002d6b&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/5/type&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        5,
        &quot;type&quot;
      ],
      &quot;value&quot;: &quot;result&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_486661a1fe0c92f7d5c4&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/metadata&quot;,
      &quot;kind&quot;: &quot;metadata&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;metadata&quot;
      ],
      &quot;value&quot;: {},
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_4d692262bdef4fa1e046&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/opcode&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;opcode&quot;
      ],
      &quot;value&quot;: &quot;index.search&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_75937558dfb0670c42f8&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/outputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;outputs&quot;
      ],
      &quot;value&quot;: [
        {
          &quot;type&quot;: &quot;result&quot;,
          &quot;identifier&quot;: &quot;result_007&quot;,
          &quot;semantic_name&quot;: &quot;index.search response&quot;
        }
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_626fa18cc47f361727c6&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/outputs/0&quot;,
      &quot;kind&quot;: &quot;output&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;outputs&quot;,
        0
      ],
      &quot;value&quot;: {
        &quot;type&quot;: &quot;result&quot;,
        &quot;identifier&quot;: &quot;result_007&quot;,
        &quot;semantic_name&quot;: &quot;index.search response&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_b02f8748f20e0b8ae4d3&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/outputs/0/identifier&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;outputs&quot;,
        0,
        &quot;identifier&quot;
      ],
      &quot;value&quot;: &quot;result_007&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_a0a72e7db1b44b17663d&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/outputs/0/semantic_name&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;outputs&quot;,
        0,
        &quot;semantic_name&quot;
      ],
      &quot;value&quot;: &quot;index.search response&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_f97e93fd4c5e5937a55a&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/outputs/0/type&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;outputs&quot;,
        0,
        &quot;type&quot;
      ],
      &quot;value&quot;: &quot;result&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_6d2995384fed34945dbc&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/1&quot;,
      &quot;kind&quot;: &quot;instruction&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_008&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        1
      ],
      &quot;value&quot;: {
        &quot;id&quot;: &quot;ir_008&quot;,
        &quot;opcode&quot;: &quot;dispatch&quot;,
        &quot;inputs&quot;: [],
        &quot;outputs&quot;: [],
        &quot;constraints&quot;: [],
        &quot;metadata&quot;: {},
        &quot;draft_instruction_id&quot;: &quot;go_post_search&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: true,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_9d2b7cd2925034e82389&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/1/constraints&quot;,
      &quot;kind&quot;: &quot;constraints&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_008&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        1,
        &quot;constraints&quot;
      ],
      &quot;value&quot;: [],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_3c7d817c46995694fee3&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/1/draft_instruction_id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_008&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        1,
        &quot;draft_instruction_id&quot;
      ],
      &quot;value&quot;: &quot;go_post_search&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_5308c02687c86a14b0b4&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/1/id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_008&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        1,
        &quot;id&quot;
      ],
      &quot;value&quot;: &quot;ir_008&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_9861ab4393d0c37562f1&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/1/inputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_008&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        1,
        &quot;inputs&quot;
      ],
      &quot;value&quot;: [],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_5f5eff608e65f01e591d&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/1/metadata&quot;,
      &quot;kind&quot;: &quot;metadata&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_008&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        1,
        &quot;metadata&quot;
      ],
      &quot;value&quot;: {},
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_e270e586b23307a9c3d0&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/1/opcode&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_008&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        1,
        &quot;opcode&quot;
      ],
      &quot;value&quot;: &quot;dispatch&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_b56662dbec35783d8a3e&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/1/outputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_008&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        1,
        &quot;outputs&quot;
      ],
      &quot;value&quot;: [],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_39d586b5402de1204c93&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004&quot;,
      &quot;kind&quot;: &quot;block&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;
      ],
      &quot;value&quot;: {
        &quot;block_id&quot;: &quot;block_004&quot;,
        &quot;block_name&quot;: &quot;Write the response total to count.txt and return the response items&quot;,
        &quot;instructions&quot;: [
          {
            &quot;id&quot;: &quot;ir_009&quot;,
            &quot;opcode&quot;: &quot;extract_response_total&quot;,
            &quot;inputs&quot;: [
              {
                &quot;type&quot;: &quot;result&quot;,
                &quot;identifier&quot;: &quot;result_007&quot;,
                &quot;semantic_name&quot;: &quot;search_response&quot;
              }
            ],
            &quot;outputs&quot;: [
              {
                &quot;type&quot;: &quot;result&quot;,
                &quot;identifier&quot;: &quot;result_008&quot;,
                &quot;semantic_name&quot;: &quot;search response total&quot;
              }
            ],
            &quot;constraints&quot;: [],
            &quot;metadata&quot;: {},
            &quot;draft_instruction_id&quot;: &quot;extract_response_total&quot;
          },
          {
            &quot;id&quot;: &quot;ir_010&quot;,
            &quot;opcode&quot;: &quot;write_count_file&quot;,
            &quot;inputs&quot;: [
              {
                &quot;type&quot;: &quot;external_resource&quot;,
                &quot;identifier&quot;: &quot;count.txt&quot;,
                &quot;semantic_name&quot;: &quot;count.txt&quot;
              },
              {
                &quot;type&quot;: &quot;result&quot;,
                &quot;identifier&quot;: &quot;result_008&quot;,
                &quot;semantic_name&quot;: &quot;response_total&quot;
              }
            ],
            &quot;outputs&quot;: [],
            &quot;constraints&quot;: [
              &quot;After the search, write the response&#x27;s total value to local count.txt.&quot;
            ],
            &quot;metadata&quot;: {},
            &quot;draft_instruction_id&quot;: &quot;write_count_file&quot;
          },
          {
            &quot;id&quot;: &quot;ir_011&quot;,
            &quot;opcode&quot;: &quot;extract_response_items&quot;,
            &quot;inputs&quot;: [
              {
                &quot;type&quot;: &quot;result&quot;,
                &quot;identifier&quot;: &quot;result_007&quot;,
                &quot;semantic_name&quot;: &quot;search_response&quot;
              }
            ],
            &quot;outputs&quot;: [
              {
                &quot;type&quot;: &quot;result&quot;,
                &quot;identifier&quot;: &quot;result_009&quot;,
                &quot;semantic_name&quot;: &quot;search response items&quot;
              }
            ],
            &quot;constraints&quot;: [],
            &quot;metadata&quot;: {},
            &quot;draft_instruction_id&quot;: &quot;extract_response_items&quot;
          },
          {
            &quot;id&quot;: &quot;ir_012&quot;,
            &quot;opcode&quot;: &quot;return&quot;,
            &quot;inputs&quot;: [
              {
                &quot;type&quot;: &quot;result&quot;,
                &quot;identifier&quot;: &quot;result_009&quot;,
                &quot;semantic_name&quot;: &quot;response_items&quot;
              }
            ],
            &quot;outputs&quot;: [],
            &quot;constraints&quot;: [
              &quot;Return the search response&#x27;s items value unchanged.&quot;
            ],
            &quot;metadata&quot;: {},
            &quot;draft_instruction_id&quot;: &quot;return_items&quot;
          }
        ],
        &quot;constraints&quot;: [],
        &quot;data_source_kind&quot;: null
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_7f3849d38f9fd2240f26&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/block_id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;block_id&quot;
      ],
      &quot;value&quot;: &quot;block_004&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_b199e293b4a85fd4f332&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/block_name&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;block_name&quot;
      ],
      &quot;value&quot;: &quot;Write the response total to count.txt and return the response items&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_d2668eed894694cd5ecd&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/constraints&quot;,
      &quot;kind&quot;: &quot;constraints&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;constraints&quot;
      ],
      &quot;value&quot;: [],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_afdce17faa78abb32389&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/data_source_kind&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;data_source_kind&quot;
      ],
      &quot;value&quot;: null,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_f3c5fd1ca023e2517c7f&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;
      ],
      &quot;value&quot;: [
        {
          &quot;id&quot;: &quot;ir_009&quot;,
          &quot;opcode&quot;: &quot;extract_response_total&quot;,
          &quot;inputs&quot;: [
            {
              &quot;type&quot;: &quot;result&quot;,
              &quot;identifier&quot;: &quot;result_007&quot;,
              &quot;semantic_name&quot;: &quot;search_response&quot;
            }
          ],
          &quot;outputs&quot;: [
            {
              &quot;type&quot;: &quot;result&quot;,
              &quot;identifier&quot;: &quot;result_008&quot;,
              &quot;semantic_name&quot;: &quot;search response total&quot;
            }
          ],
          &quot;constraints&quot;: [],
          &quot;metadata&quot;: {},
          &quot;draft_instruction_id&quot;: &quot;extract_response_total&quot;
        },
        {
          &quot;id&quot;: &quot;ir_010&quot;,
          &quot;opcode&quot;: &quot;write_count_file&quot;,
          &quot;inputs&quot;: [
            {
              &quot;type&quot;: &quot;external_resource&quot;,
              &quot;identifier&quot;: &quot;count.txt&quot;,
              &quot;semantic_name&quot;: &quot;count.txt&quot;
            },
            {
              &quot;type&quot;: &quot;result&quot;,
              &quot;identifier&quot;: &quot;result_008&quot;,
              &quot;semantic_name&quot;: &quot;response_total&quot;
            }
          ],
          &quot;outputs&quot;: [],
          &quot;constraints&quot;: [
            &quot;After the search, write the response&#x27;s total value to local count.txt.&quot;
          ],
          &quot;metadata&quot;: {},
          &quot;draft_instruction_id&quot;: &quot;write_count_file&quot;
        },
        {
          &quot;id&quot;: &quot;ir_011&quot;,
          &quot;opcode&quot;: &quot;extract_response_items&quot;,
          &quot;inputs&quot;: [
            {
              &quot;type&quot;: &quot;result&quot;,
              &quot;identifier&quot;: &quot;result_007&quot;,
              &quot;semantic_name&quot;: &quot;search_response&quot;
            }
          ],
          &quot;outputs&quot;: [
            {
              &quot;type&quot;: &quot;result&quot;,
              &quot;identifier&quot;: &quot;result_009&quot;,
              &quot;semantic_name&quot;: &quot;search response items&quot;
            }
          ],
          &quot;constraints&quot;: [],
          &quot;metadata&quot;: {},
          &quot;draft_instruction_id&quot;: &quot;extract_response_items&quot;
        },
        {
          &quot;id&quot;: &quot;ir_012&quot;,
          &quot;opcode&quot;: &quot;return&quot;,
          &quot;inputs&quot;: [
            {
              &quot;type&quot;: &quot;result&quot;,
              &quot;identifier&quot;: &quot;result_009&quot;,
              &quot;semantic_name&quot;: &quot;response_items&quot;
            }
          ],
          &quot;outputs&quot;: [],
          &quot;constraints&quot;: [
            &quot;Return the search response&#x27;s items value unchanged.&quot;
          ],
          &quot;metadata&quot;: {},
          &quot;draft_instruction_id&quot;: &quot;return_items&quot;
        }
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_51025447e69b6ad057fd&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/0&quot;,
      &quot;kind&quot;: &quot;instruction&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        0
      ],
      &quot;value&quot;: {
        &quot;id&quot;: &quot;ir_009&quot;,
        &quot;opcode&quot;: &quot;extract_response_total&quot;,
        &quot;inputs&quot;: [
          {
            &quot;type&quot;: &quot;result&quot;,
            &quot;identifier&quot;: &quot;result_007&quot;,
            &quot;semantic_name&quot;: &quot;search_response&quot;
          }
        ],
        &quot;outputs&quot;: [
          {
            &quot;type&quot;: &quot;result&quot;,
            &quot;identifier&quot;: &quot;result_008&quot;,
            &quot;semantic_name&quot;: &quot;search response total&quot;
          }
        ],
        &quot;constraints&quot;: [],
        &quot;metadata&quot;: {},
        &quot;draft_instruction_id&quot;: &quot;extract_response_total&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_67cd52f69e9265ee2d88&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/0/constraints&quot;,
      &quot;kind&quot;: &quot;constraints&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        0,
        &quot;constraints&quot;
      ],
      &quot;value&quot;: [],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_cd991c082b756a62bff6&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/0/draft_instruction_id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        0,
        &quot;draft_instruction_id&quot;
      ],
      &quot;value&quot;: &quot;extract_response_total&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_e77c25c85218ab286eae&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/0/id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        0,
        &quot;id&quot;
      ],
      &quot;value&quot;: &quot;ir_009&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_38c270bdf3a6852e75ed&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/0/inputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;
      ],
      &quot;value&quot;: [
        {
          &quot;type&quot;: &quot;result&quot;,
          &quot;identifier&quot;: &quot;result_007&quot;,
          &quot;semantic_name&quot;: &quot;search_response&quot;
        }
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_f47896a324af5c5037f6&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/0/inputs/0&quot;,
      &quot;kind&quot;: &quot;input&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        0
      ],
      &quot;value&quot;: {
        &quot;type&quot;: &quot;result&quot;,
        &quot;identifier&quot;: &quot;result_007&quot;,
        &quot;semantic_name&quot;: &quot;search_response&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_56c6a831065c5bb01d4f&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/0/inputs/0/identifier&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        0,
        &quot;identifier&quot;
      ],
      &quot;value&quot;: &quot;result_007&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_125006a11de07a73b9c0&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/0/inputs/0/semantic_name&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        0,
        &quot;semantic_name&quot;
      ],
      &quot;value&quot;: &quot;search_response&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_3e2691ec7b1a5b47adc3&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/0/inputs/0/type&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        0,
        &quot;type&quot;
      ],
      &quot;value&quot;: &quot;result&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_7410ecf76b5f50835de3&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/0/metadata&quot;,
      &quot;kind&quot;: &quot;metadata&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        0,
        &quot;metadata&quot;
      ],
      &quot;value&quot;: {},
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_234c2dfbe82c789dbb38&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/0/opcode&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        0,
        &quot;opcode&quot;
      ],
      &quot;value&quot;: &quot;extract_response_total&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_f9dcfda4d6d3d41b2457&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/0/outputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        0,
        &quot;outputs&quot;
      ],
      &quot;value&quot;: [
        {
          &quot;type&quot;: &quot;result&quot;,
          &quot;identifier&quot;: &quot;result_008&quot;,
          &quot;semantic_name&quot;: &quot;search response total&quot;
        }
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_0338c293f4218e102429&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/0/outputs/0&quot;,
      &quot;kind&quot;: &quot;output&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        0,
        &quot;outputs&quot;,
        0
      ],
      &quot;value&quot;: {
        &quot;type&quot;: &quot;result&quot;,
        &quot;identifier&quot;: &quot;result_008&quot;,
        &quot;semantic_name&quot;: &quot;search response total&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_937b28c5990d32818eef&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/0/outputs/0/identifier&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        0,
        &quot;outputs&quot;,
        0,
        &quot;identifier&quot;
      ],
      &quot;value&quot;: &quot;result_008&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_309db752895f50993d12&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/0/outputs/0/semantic_name&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        0,
        &quot;outputs&quot;,
        0,
        &quot;semantic_name&quot;
      ],
      &quot;value&quot;: &quot;search response total&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_7540f01d50b35e11f600&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/0/outputs/0/type&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        0,
        &quot;outputs&quot;,
        0,
        &quot;type&quot;
      ],
      &quot;value&quot;: &quot;result&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_8a496a9373a7ecdb9f03&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/1&quot;,
      &quot;kind&quot;: &quot;instruction&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        1
      ],
      &quot;value&quot;: {
        &quot;id&quot;: &quot;ir_010&quot;,
        &quot;opcode&quot;: &quot;write_count_file&quot;,
        &quot;inputs&quot;: [
          {
            &quot;type&quot;: &quot;external_resource&quot;,
            &quot;identifier&quot;: &quot;count.txt&quot;,
            &quot;semantic_name&quot;: &quot;count.txt&quot;
          },
          {
            &quot;type&quot;: &quot;result&quot;,
            &quot;identifier&quot;: &quot;result_008&quot;,
            &quot;semantic_name&quot;: &quot;response_total&quot;
          }
        ],
        &quot;outputs&quot;: [],
        &quot;constraints&quot;: [
          &quot;After the search, write the response&#x27;s total value to local count.txt.&quot;
        ],
        &quot;metadata&quot;: {},
        &quot;draft_instruction_id&quot;: &quot;write_count_file&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 2,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_36fb20851e6bb54fec07&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/1/constraints&quot;,
      &quot;kind&quot;: &quot;constraints&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        1,
        &quot;constraints&quot;
      ],
      &quot;value&quot;: [
        &quot;After the search, write the response&#x27;s total value to local count.txt.&quot;
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 2,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_85d02f3e566a3accbd54&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/1/constraints/0&quot;,
      &quot;kind&quot;: &quot;constraint&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        1,
        &quot;constraints&quot;,
        0
      ],
      &quot;value&quot;: &quot;After the search, write the response&#x27;s total value to local count.txt.&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 2,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_26deb537ff49d78d397f&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/1/draft_instruction_id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        1,
        &quot;draft_instruction_id&quot;
      ],
      &quot;value&quot;: &quot;write_count_file&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 2,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_b8ab99b21c96288902de&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/1/id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        1,
        &quot;id&quot;
      ],
      &quot;value&quot;: &quot;ir_010&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 2,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_3de614466f0c8ef33a19&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/1/inputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        1,
        &quot;inputs&quot;
      ],
      &quot;value&quot;: [
        {
          &quot;type&quot;: &quot;external_resource&quot;,
          &quot;identifier&quot;: &quot;count.txt&quot;,
          &quot;semantic_name&quot;: &quot;count.txt&quot;
        },
        {
          &quot;type&quot;: &quot;result&quot;,
          &quot;identifier&quot;: &quot;result_008&quot;,
          &quot;semantic_name&quot;: &quot;response_total&quot;
        }
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 2,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_ce5dc739e4eaf2527fce&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/1/inputs/0&quot;,
      &quot;kind&quot;: &quot;input&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        1,
        &quot;inputs&quot;,
        0
      ],
      &quot;value&quot;: {
        &quot;type&quot;: &quot;external_resource&quot;,
        &quot;identifier&quot;: &quot;count.txt&quot;,
        &quot;semantic_name&quot;: &quot;count.txt&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 2,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_0391beb19037408759db&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/1/inputs/0/identifier&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        1,
        &quot;inputs&quot;,
        0,
        &quot;identifier&quot;
      ],
      &quot;value&quot;: &quot;count.txt&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 2,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_430c65ade2ef630aa3e3&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/1/inputs/0/semantic_name&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        1,
        &quot;inputs&quot;,
        0,
        &quot;semantic_name&quot;
      ],
      &quot;value&quot;: &quot;count.txt&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 2,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_128d6e2364ba2871e9e3&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/1/inputs/0/type&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        1,
        &quot;inputs&quot;,
        0,
        &quot;type&quot;
      ],
      &quot;value&quot;: &quot;external_resource&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 2,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_7059117d893e83168a4a&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/1/inputs/1&quot;,
      &quot;kind&quot;: &quot;input&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        1,
        &quot;inputs&quot;,
        1
      ],
      &quot;value&quot;: {
        &quot;type&quot;: &quot;result&quot;,
        &quot;identifier&quot;: &quot;result_008&quot;,
        &quot;semantic_name&quot;: &quot;response_total&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 2,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_cdc0cf8eccd0befe656e&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/1/inputs/1/identifier&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        1,
        &quot;inputs&quot;,
        1,
        &quot;identifier&quot;
      ],
      &quot;value&quot;: &quot;result_008&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 2,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_3109b2168d3010b43adf&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/1/inputs/1/semantic_name&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        1,
        &quot;inputs&quot;,
        1,
        &quot;semantic_name&quot;
      ],
      &quot;value&quot;: &quot;response_total&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 2,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_64ea4e4f92e93c865673&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/1/inputs/1/type&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        1,
        &quot;inputs&quot;,
        1,
        &quot;type&quot;
      ],
      &quot;value&quot;: &quot;result&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 2,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_092295b777adf7b9880f&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/1/metadata&quot;,
      &quot;kind&quot;: &quot;metadata&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        1,
        &quot;metadata&quot;
      ],
      &quot;value&quot;: {},
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 2,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_ad7879b2e2895bc93a40&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/1/opcode&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        1,
        &quot;opcode&quot;
      ],
      &quot;value&quot;: &quot;write_count_file&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 2,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_e0d557e6c127f93627b5&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/1/outputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        1,
        &quot;outputs&quot;
      ],
      &quot;value&quot;: [],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 2,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_edafb33936cb6d656c88&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/2&quot;,
      &quot;kind&quot;: &quot;instruction&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_011&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        2
      ],
      &quot;value&quot;: {
        &quot;id&quot;: &quot;ir_011&quot;,
        &quot;opcode&quot;: &quot;extract_response_items&quot;,
        &quot;inputs&quot;: [
          {
            &quot;type&quot;: &quot;result&quot;,
            &quot;identifier&quot;: &quot;result_007&quot;,
            &quot;semantic_name&quot;: &quot;search_response&quot;
          }
        ],
        &quot;outputs&quot;: [
          {
            &quot;type&quot;: &quot;result&quot;,
            &quot;identifier&quot;: &quot;result_009&quot;,
            &quot;semantic_name&quot;: &quot;search response items&quot;
          }
        ],
        &quot;constraints&quot;: [],
        &quot;metadata&quot;: {},
        &quot;draft_instruction_id&quot;: &quot;extract_response_items&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_fa7f285430e0855a3bb0&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/2/constraints&quot;,
      &quot;kind&quot;: &quot;constraints&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_011&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        2,
        &quot;constraints&quot;
      ],
      &quot;value&quot;: [],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_32a2845316753096927a&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/2/draft_instruction_id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_011&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        2,
        &quot;draft_instruction_id&quot;
      ],
      &quot;value&quot;: &quot;extract_response_items&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_e7ffa72410feb4752c7d&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/2/id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_011&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        2,
        &quot;id&quot;
      ],
      &quot;value&quot;: &quot;ir_011&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_fcaf1f641e04342ccc47&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/2/inputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_011&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        2,
        &quot;inputs&quot;
      ],
      &quot;value&quot;: [
        {
          &quot;type&quot;: &quot;result&quot;,
          &quot;identifier&quot;: &quot;result_007&quot;,
          &quot;semantic_name&quot;: &quot;search_response&quot;
        }
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_d441ff179a8073433e11&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/2/inputs/0&quot;,
      &quot;kind&quot;: &quot;input&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_011&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        2,
        &quot;inputs&quot;,
        0
      ],
      &quot;value&quot;: {
        &quot;type&quot;: &quot;result&quot;,
        &quot;identifier&quot;: &quot;result_007&quot;,
        &quot;semantic_name&quot;: &quot;search_response&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_ad31635106cdce68b03e&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/2/inputs/0/identifier&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_011&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        2,
        &quot;inputs&quot;,
        0,
        &quot;identifier&quot;
      ],
      &quot;value&quot;: &quot;result_007&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_8010332758ada1b22529&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/2/inputs/0/semantic_name&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_011&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        2,
        &quot;inputs&quot;,
        0,
        &quot;semantic_name&quot;
      ],
      &quot;value&quot;: &quot;search_response&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_580a32610a2e7131108b&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/2/inputs/0/type&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_011&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        2,
        &quot;inputs&quot;,
        0,
        &quot;type&quot;
      ],
      &quot;value&quot;: &quot;result&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_24cf3c68dd8f6e2b7d62&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/2/metadata&quot;,
      &quot;kind&quot;: &quot;metadata&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_011&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        2,
        &quot;metadata&quot;
      ],
      &quot;value&quot;: {},
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_ade97240b777d49eb683&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/2/opcode&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_011&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        2,
        &quot;opcode&quot;
      ],
      &quot;value&quot;: &quot;extract_response_items&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_0680a9a1f124322211c8&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/2/outputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_011&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        2,
        &quot;outputs&quot;
      ],
      &quot;value&quot;: [
        {
          &quot;type&quot;: &quot;result&quot;,
          &quot;identifier&quot;: &quot;result_009&quot;,
          &quot;semantic_name&quot;: &quot;search response items&quot;
        }
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_a312bfa5142fb9403867&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/2/outputs/0&quot;,
      &quot;kind&quot;: &quot;output&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_011&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        2,
        &quot;outputs&quot;,
        0
      ],
      &quot;value&quot;: {
        &quot;type&quot;: &quot;result&quot;,
        &quot;identifier&quot;: &quot;result_009&quot;,
        &quot;semantic_name&quot;: &quot;search response items&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_892a206011d19831e765&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/2/outputs/0/identifier&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_011&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        2,
        &quot;outputs&quot;,
        0,
        &quot;identifier&quot;
      ],
      &quot;value&quot;: &quot;result_009&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_ea4eb78e38a3f10b0983&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/2/outputs/0/semantic_name&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_011&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        2,
        &quot;outputs&quot;,
        0,
        &quot;semantic_name&quot;
      ],
      &quot;value&quot;: &quot;search response items&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_33396bda2d54a0529ff2&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/2/outputs/0/type&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_011&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        2,
        &quot;outputs&quot;,
        0,
        &quot;type&quot;
      ],
      &quot;value&quot;: &quot;result&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_7b8f1bd028dad0498897&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/3&quot;,
      &quot;kind&quot;: &quot;instruction&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_012&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        3
      ],
      &quot;value&quot;: {
        &quot;id&quot;: &quot;ir_012&quot;,
        &quot;opcode&quot;: &quot;return&quot;,
        &quot;inputs&quot;: [
          {
            &quot;type&quot;: &quot;result&quot;,
            &quot;identifier&quot;: &quot;result_009&quot;,
            &quot;semantic_name&quot;: &quot;response_items&quot;
          }
        ],
        &quot;outputs&quot;: [],
        &quot;constraints&quot;: [
          &quot;Return the search response&#x27;s items value unchanged.&quot;
        ],
        &quot;metadata&quot;: {},
        &quot;draft_instruction_id&quot;: &quot;return_items&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_cc1424f6065a319bbb3b&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/3/constraints&quot;,
      &quot;kind&quot;: &quot;constraints&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_012&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        3,
        &quot;constraints&quot;
      ],
      &quot;value&quot;: [
        &quot;Return the search response&#x27;s items value unchanged.&quot;
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_6227194f4845b13f8abb&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/3/constraints/0&quot;,
      &quot;kind&quot;: &quot;constraint&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_012&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        3,
        &quot;constraints&quot;,
        0
      ],
      &quot;value&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_a7cf517e21279693b697&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/3/draft_instruction_id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_012&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        3,
        &quot;draft_instruction_id&quot;
      ],
      &quot;value&quot;: &quot;return_items&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_d53340028300f6aae986&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/3/id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_012&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        3,
        &quot;id&quot;
      ],
      &quot;value&quot;: &quot;ir_012&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_2342fe412bea5a4c4091&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/3/inputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_012&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        3,
        &quot;inputs&quot;
      ],
      &quot;value&quot;: [
        {
          &quot;type&quot;: &quot;result&quot;,
          &quot;identifier&quot;: &quot;result_009&quot;,
          &quot;semantic_name&quot;: &quot;response_items&quot;
        }
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_33cc6c103c883f7b96d1&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/3/inputs/0&quot;,
      &quot;kind&quot;: &quot;input&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_012&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        3,
        &quot;inputs&quot;,
        0
      ],
      &quot;value&quot;: {
        &quot;type&quot;: &quot;result&quot;,
        &quot;identifier&quot;: &quot;result_009&quot;,
        &quot;semantic_name&quot;: &quot;response_items&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_a9e6fddc498b4f6ac792&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/3/inputs/0/identifier&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_012&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        3,
        &quot;inputs&quot;,
        0,
        &quot;identifier&quot;
      ],
      &quot;value&quot;: &quot;result_009&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_08c8779e404911196406&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/3/inputs/0/semantic_name&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_012&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        3,
        &quot;inputs&quot;,
        0,
        &quot;semantic_name&quot;
      ],
      &quot;value&quot;: &quot;response_items&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_d0af1a65ab3e5778b221&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/3/inputs/0/type&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_012&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        3,
        &quot;inputs&quot;,
        0,
        &quot;type&quot;
      ],
      &quot;value&quot;: &quot;result&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_f2a278d7002c39c463f1&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/3/metadata&quot;,
      &quot;kind&quot;: &quot;metadata&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_012&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        3,
        &quot;metadata&quot;
      ],
      &quot;value&quot;: {},
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_e15a1478eca9c24d16b2&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/3/opcode&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_012&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        3,
        &quot;opcode&quot;
      ],
      &quot;value&quot;: &quot;return&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_51d501b7e85434d822fb&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/3/outputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_012&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        3,
        &quot;outputs&quot;
      ],
      &quot;value&quot;: [],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_a7022b2025864a4aee8e&quot;: {
      &quot;pointer&quot;: &quot;/constraints&quot;,
      &quot;kind&quot;: &quot;constraints&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;constraints&quot;
      ],
      &quot;value&quot;: [
        &quot;Call index.search exactly once.&quot;,
        &quot;Do not invoke index.delete anywhere in this workflow.&quot;,
        &quot;Parameter descriptions are call requirements and do not instruct pre-call validation or normalization.&quot;,
        &quot;Capability note: index.search supports fuzzy matching; this note does not request fuzzy expansion in this workflow.&quot;
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_74256b1796dc113828cc&quot;: {
      &quot;pointer&quot;: &quot;/constraints/0&quot;,
      &quot;kind&quot;: &quot;constraint&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;constraints&quot;,
        0
      ],
      &quot;value&quot;: &quot;Call index.search exactly once.&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_6624934ada448fce25c5&quot;: {
      &quot;pointer&quot;: &quot;/constraints/1&quot;,
      &quot;kind&quot;: &quot;constraint&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;constraints&quot;,
        1
      ],
      &quot;value&quot;: &quot;Do not invoke index.delete anywhere in this workflow.&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_46b557f1d7527b4a10dc&quot;: {
      &quot;pointer&quot;: &quot;/constraints/2&quot;,
      &quot;kind&quot;: &quot;constraint&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;constraints&quot;,
        2
      ],
      &quot;value&quot;: &quot;Parameter descriptions are call requirements and do not instruct pre-call validation or normalization.&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_14e045481779376a48d6&quot;: {
      &quot;pointer&quot;: &quot;/constraints/3&quot;,
      &quot;kind&quot;: &quot;constraint&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;constraints&quot;,
        3
      ],
      &quot;value&quot;: &quot;Capability note: index.search supports fuzzy matching; this note does not request fuzzy expansion in this workflow.&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_b41b0539d00f9c7f9544&quot;: {
      &quot;pointer&quot;: &quot;/declared_context_keys&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;declared_context_keys&quot;
      ],
      &quot;value&quot;: [],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_617d412c248879458d4c&quot;: {
      &quot;pointer&quot;: &quot;/edges&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;edges&quot;
      ],
      &quot;value&quot;: [
        {
          &quot;source_block_id&quot;: &quot;block_001&quot;,
          &quot;target_block_id&quot;: &quot;block_002&quot;,
          &quot;condition_text&quot;: null
        },
        {
          &quot;source_block_id&quot;: &quot;block_002&quot;,
          &quot;target_block_id&quot;: &quot;block_003&quot;,
          &quot;condition_text&quot;: null
        },
        {
          &quot;source_block_id&quot;: &quot;block_003&quot;,
          &quot;target_block_id&quot;: &quot;block_004&quot;,
          &quot;condition_text&quot;: null
        }
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_5faac0806b42f79e3384&quot;: {
      &quot;pointer&quot;: &quot;/edges/0&quot;,
      &quot;kind&quot;: &quot;edge&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;edges&quot;,
        0
      ],
      &quot;value&quot;: {
        &quot;source_block_id&quot;: &quot;block_001&quot;,
        &quot;target_block_id&quot;: &quot;block_002&quot;,
        &quot;condition_text&quot;: null
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: true,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;instruction_id&quot;: &quot;ir_002&quot;
    },
    &quot;target_0305b37337374dc86f9d&quot;: {
      &quot;pointer&quot;: &quot;/edges/0/condition_text&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;edges&quot;,
        0,
        &quot;condition_text&quot;
      ],
      &quot;value&quot;: null,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: true,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;instruction_id&quot;: &quot;ir_002&quot;
    },
    &quot;target_6e31557a85255fb0e28e&quot;: {
      &quot;pointer&quot;: &quot;/edges/0/source_block_id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;edges&quot;,
        0,
        &quot;source_block_id&quot;
      ],
      &quot;value&quot;: &quot;block_001&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;instruction_id&quot;: &quot;ir_002&quot;
    },
    &quot;target_ed43ae3256fb61dda415&quot;: {
      &quot;pointer&quot;: &quot;/edges/0/target_block_id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;edges&quot;,
        0,
        &quot;target_block_id&quot;
      ],
      &quot;value&quot;: &quot;block_002&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;instruction_id&quot;: &quot;ir_002&quot;
    },
    &quot;target_08ae339fac34d840b865&quot;: {
      &quot;pointer&quot;: &quot;/edges/1&quot;,
      &quot;kind&quot;: &quot;edge&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;edges&quot;,
        1
      ],
      &quot;value&quot;: {
        &quot;source_block_id&quot;: &quot;block_002&quot;,
        &quot;target_block_id&quot;: &quot;block_003&quot;,
        &quot;condition_text&quot;: null
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: true,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;instruction_id&quot;: &quot;ir_006&quot;
    },
    &quot;target_4752555e3fbea6a94726&quot;: {
      &quot;pointer&quot;: &quot;/edges/1/condition_text&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;edges&quot;,
        1,
        &quot;condition_text&quot;
      ],
      &quot;value&quot;: null,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: true,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;instruction_id&quot;: &quot;ir_006&quot;
    },
    &quot;target_00bd4c2ed7f301442de5&quot;: {
      &quot;pointer&quot;: &quot;/edges/1/source_block_id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;edges&quot;,
        1,
        &quot;source_block_id&quot;
      ],
      &quot;value&quot;: &quot;block_002&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;instruction_id&quot;: &quot;ir_006&quot;
    },
    &quot;target_39e9a4c53eb85128e3f1&quot;: {
      &quot;pointer&quot;: &quot;/edges/1/target_block_id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;edges&quot;,
        1,
        &quot;target_block_id&quot;
      ],
      &quot;value&quot;: &quot;block_003&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;instruction_id&quot;: &quot;ir_006&quot;
    },
    &quot;target_8495517429dc04aa4790&quot;: {
      &quot;pointer&quot;: &quot;/edges/2&quot;,
      &quot;kind&quot;: &quot;edge&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;edges&quot;,
        2
      ],
      &quot;value&quot;: {
        &quot;source_block_id&quot;: &quot;block_003&quot;,
        &quot;target_block_id&quot;: &quot;block_004&quot;,
        &quot;condition_text&quot;: null
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: true,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;instruction_id&quot;: &quot;ir_008&quot;
    },
    &quot;target_c6c7a12847c88f82bcaa&quot;: {
      &quot;pointer&quot;: &quot;/edges/2/condition_text&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;edges&quot;,
        2,
        &quot;condition_text&quot;
      ],
      &quot;value&quot;: null,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: true,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;instruction_id&quot;: &quot;ir_008&quot;
    },
    &quot;target_6f053941c32e7f14d0c7&quot;: {
      &quot;pointer&quot;: &quot;/edges/2/source_block_id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;edges&quot;,
        2,
        &quot;source_block_id&quot;
      ],
      &quot;value&quot;: &quot;block_003&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;instruction_id&quot;: &quot;ir_008&quot;
    },
    &quot;target_185131a7a3d0e37cfa8a&quot;: {
      &quot;pointer&quot;: &quot;/edges/2/target_block_id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;edges&quot;,
        2,
        &quot;target_block_id&quot;
      ],
      &quot;value&quot;: &quot;block_004&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;instruction_id&quot;: &quot;ir_008&quot;
    },
    &quot;target_c3451c12dafbab510d96&quot;: {
      &quot;pointer&quot;: &quot;/entry_block_id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;entry_block_id&quot;
      ],
      &quot;value&quot;: &quot;block_001&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;demand_target_8549692ca39a8390ee37&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;processing&quot;,
      &quot;instruction_id&quot;: &quot;ir_001&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_001/events/0&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;processing&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;events&quot;: [
          {
            &quot;effect_index&quot;: 0,
            &quot;atomic_ops&quot;: [
              {
                &quot;evidences&quot;: [
                  {
                    &quot;basis&quot;: &quot;source&quot;,
                    &quot;ref_id&quot;: &quot;src_007&quot;,
                    &quot;quote&quot;: &quot;Read the user-supplied request.json, which contains term and may contain from_date and limit.&quot;,
                    &quot;reason&quot;: &quot;读取 request.json 当前内容到局部值 request_content。&quot;
                  },
                  {
                    &quot;basis&quot;: &quot;execution_model&quot;,
                    &quot;ref_id&quot;: &quot;EM01&quot;,
                    &quot;quote&quot;: &quot;Preserve the related source whole as a possible acquisition scope unless an explicit interface or mechanism restricts the read or returned content.&quot;,
                    &quot;reason&quot;: &quot;没有显式 key-only 读取机制，保留整个文件作为可能获取范围。&quot;
                  }
                ],
                &quot;op&quot;: &quot;read&quot;,
                &quot;location&quot;: &quot;loc_request_json&quot;,
                &quot;output&quot;: &quot;request_content&quot;
              }
            ]
          }
        ],
        &quot;returns&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;ref_id&quot;: &quot;EM10&quot;,
            &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
            &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，按默认模式分析读取输出。&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;ref_id&quot;: &quot;src_007&quot;,
            &quot;quote&quot;: &quot;Read the user-supplied request.json, which contains term and may contain from_date and limit.&quot;,
            &quot;reason&quot;: &quot;源文只要求读取文件，未说明本地或模型处理边界。&quot;
          }
        ]
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_f9d06d6fafac4dfd3c92&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;effect&quot;,
      &quot;instruction_id&quot;: &quot;ir_001&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_001/events/0/events/0&quot;,
      &quot;value&quot;: {
        &quot;effect_index&quot;: 0,
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;ref_id&quot;: &quot;src_007&quot;,
                &quot;quote&quot;: &quot;Read the user-supplied request.json, which contains term and may contain from_date and limit.&quot;,
                &quot;reason&quot;: &quot;读取 request.json 当前内容到局部值 request_content。&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;ref_id&quot;: &quot;EM01&quot;,
                &quot;quote&quot;: &quot;Preserve the related source whole as a possible acquisition scope unless an explicit interface or mechanism restricts the read or returned content.&quot;,
                &quot;reason&quot;: &quot;没有显式 key-only 读取机制，保留整个文件作为可能获取范围。&quot;
              }
            ],
            &quot;op&quot;: &quot;read&quot;,
            &quot;location&quot;: &quot;loc_request_json&quot;,
            &quot;output&quot;: &quot;request_content&quot;
          }
        ]
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_d3bfc95682d44b33f657&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;operation&quot;,
      &quot;instruction_id&quot;: &quot;ir_001&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_001/events/0/events/0/atomic_ops/0&quot;,
      &quot;value&quot;: {
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;ref_id&quot;: &quot;src_007&quot;,
            &quot;quote&quot;: &quot;Read the user-supplied request.json, which contains term and may contain from_date and limit.&quot;,
            &quot;reason&quot;: &quot;读取 request.json 当前内容到局部值 request_content。&quot;
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;ref_id&quot;: &quot;EM01&quot;,
            &quot;quote&quot;: &quot;Preserve the related source whole as a possible acquisition scope unless an explicit interface or mechanism restricts the read or returned content.&quot;,
            &quot;reason&quot;: &quot;没有显式 key-only 读取机制，保留整个文件作为可能获取范围。&quot;
          }
        ],
        &quot;op&quot;: &quot;read&quot;,
        &quot;location&quot;: &quot;loc_request_json&quot;,
        &quot;output&quot;: &quot;request_content&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;declared_refs&quot;: [],
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_fed701af8decdad78917&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;local_output&quot;,
      &quot;instruction_id&quot;: &quot;ir_001&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0,
        &quot;output&quot;
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_001/events/0/events/0/atomic_ops/0/output&quot;,
      &quot;value&quot;: &quot;request_content&quot;,
      &quot;available_locals&quot;: [
        &quot;request_content&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;request_content&quot;
      },
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_b46331c829d20ac23307&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;output_binding&quot;,
      &quot;instruction_id&quot;: &quot;ir_001&quot;,
      &quot;raw_path&quot;: [
        &quot;output_bindings&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_001/output_bindings/0&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;request_content&quot;
      },
      &quot;available_locals&quot;: [
        &quot;request_content&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;output_index&quot;: 0,
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;request_content&quot;
      },
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_4c38474a1420991dbcb7&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;processing&quot;,
      &quot;instruction_id&quot;: &quot;ir_003&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_003/events/0&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;processing&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;events&quot;: [
          {
            &quot;effect_index&quot;: 0,
            &quot;atomic_ops&quot;: [
              {
                &quot;evidences&quot;: [
                  {
                    &quot;basis&quot;: &quot;source&quot;,
                    &quot;ref_id&quot;: &quot;src_008&quot;,
                    &quot;quote&quot;: &quot;using request.term unchanged as its query argument&quot;,
                    &quot;reason&quot;: &quot;明确从输入选择 request.term 字段并保持原值。&quot;
                  }
                ],
                &quot;op&quot;: &quot;select_part&quot;,
                &quot;input&quot;: {
                  &quot;kind&quot;: &quot;input&quot;,
                  &quot;index&quot;: 0
                },
                &quot;path&quot;: [
                  &quot;term&quot;
                ],
                &quot;output&quot;: &quot;term&quot;
              }
            ]
          }
        ],
        &quot;returns&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;ref_id&quot;: &quot;EM10&quot;,
            &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
            &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，字段提取按默认模式分析。&quot;
          }
        ]
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_9d1854ee7470b44c9c62&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;effect&quot;,
      &quot;instruction_id&quot;: &quot;ir_003&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_003/events/0/events/0&quot;,
      &quot;value&quot;: {
        &quot;effect_index&quot;: 0,
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;ref_id&quot;: &quot;src_008&quot;,
                &quot;quote&quot;: &quot;using request.term unchanged as its query argument&quot;,
                &quot;reason&quot;: &quot;明确从输入选择 request.term 字段并保持原值。&quot;
              }
            ],
            &quot;op&quot;: &quot;select_part&quot;,
            &quot;input&quot;: {
              &quot;kind&quot;: &quot;input&quot;,
              &quot;index&quot;: 0
            },
            &quot;path&quot;: [
              &quot;term&quot;
            ],
            &quot;output&quot;: &quot;term&quot;
          }
        ]
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_db473f8638997a7d068a&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;operation&quot;,
      &quot;instruction_id&quot;: &quot;ir_003&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_003/events/0/events/0/atomic_ops/0&quot;,
      &quot;value&quot;: {
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;ref_id&quot;: &quot;src_008&quot;,
            &quot;quote&quot;: &quot;using request.term unchanged as its query argument&quot;,
            &quot;reason&quot;: &quot;明确从输入选择 request.term 字段并保持原值。&quot;
          }
        ],
        &quot;op&quot;: &quot;select_part&quot;,
        &quot;input&quot;: {
          &quot;kind&quot;: &quot;input&quot;,
          &quot;index&quot;: 0
        },
        &quot;path&quot;: [
          &quot;term&quot;
        ],
        &quot;output&quot;: &quot;term&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;declared_refs&quot;: [
        {
          &quot;kind&quot;: &quot;input&quot;,
          &quot;index&quot;: 0
        }
      ],
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_f9f57018a278480e8c0f&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;input_use&quot;,
      &quot;instruction_id&quot;: &quot;ir_003&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0,
        &quot;uses&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_003/events/0/events/0/atomic_ops/0/uses/0&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;input&quot;,
        &quot;index&quot;: 0
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;slot&quot;: 0,
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;input&quot;,
        &quot;index&quot;: 0
      },
      &quot;role&quot;: &quot;value&quot;,
      &quot;when&quot;: null,
      &quot;member_index&quot;: null,
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_bcb7362cc7a165322864&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;local_output&quot;,
      &quot;instruction_id&quot;: &quot;ir_003&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0,
        &quot;output&quot;
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_003/events/0/events/0/atomic_ops/0/output&quot;,
      &quot;value&quot;: &quot;term&quot;,
      &quot;available_locals&quot;: [
        &quot;term&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;term&quot;
      },
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_0b704127b53ff4e063cb&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;output_binding&quot;,
      &quot;instruction_id&quot;: &quot;ir_003&quot;,
      &quot;raw_path&quot;: [
        &quot;output_bindings&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_003/output_bindings/0&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;term&quot;
      },
      &quot;available_locals&quot;: [
        &quot;term&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;output_index&quot;: 0,
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;term&quot;
      },
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_6a69ec925443b688f129&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;processing&quot;,
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_004/events/0&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;processing&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;events&quot;: [
          {
            &quot;effect_index&quot;: 0,
            &quot;atomic_ops&quot;: [
              {
                &quot;evidences&quot;: [
                  {
                    &quot;basis&quot;: &quot;source&quot;,
                    &quot;ref_id&quot;: &quot;src_009&quot;,
                    &quot;quote&quot;: &quot;When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.&quot;,
                    &quot;reason&quot;: &quot;存在时保留 from_date 原值。&quot;
                  }
                ],
                &quot;op&quot;: &quot;select_part&quot;,
                &quot;input&quot;: {
                  &quot;kind&quot;: &quot;input&quot;,
                  &quot;index&quot;: 0
                },
                &quot;path&quot;: [
                  &quot;from_date&quot;
                ],
                &quot;output&quot;: &quot;from_date_value&quot;
              },
              {
                &quot;evidences&quot;: [
                  {
                    &quot;basis&quot;: &quot;source&quot;,
                    &quot;ref_id&quot;: &quot;src_009&quot;,
                    &quot;quote&quot;: &quot;When from_date is missing, omit the from_date argument.&quot;,
                    &quot;reason&quot;: &quot;需要判断 from_date 是否存在以决定是否传递；存在性由输入计算，单独于原值。&quot;
                  },
                  {
                    &quot;basis&quot;: &quot;execution_model&quot;,
                    &quot;ref_id&quot;: &quot;EM14&quot;,
                    &quot;quote&quot;: &quot;build members may have a Boolean when reference: true includes the original value, false omits the member without consuming its value, and an abstract Boolean retains both possibilities.&quot;,
                    &quot;reason&quot;: &quot;存在性布尔作为后续可选成员的 when 控制，而不是作为参数值。&quot;
                  }
                ],
                &quot;op&quot;: &quot;compute&quot;,
                &quot;inputs&quot;: [
                  {
                    &quot;kind&quot;: &quot;input&quot;,
                    &quot;index&quot;: 0
                  }
                ],
                &quot;dependencies&quot;: [
                  &quot;derived&quot;
                ],
                &quot;output&quot;: &quot;from_date_present&quot;
              }
            ]
          }
        ],
        &quot;returns&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;ref_id&quot;: &quot;EM10&quot;,
            &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
            &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，可选字段提取按默认模式分析。&quot;
          }
        ]
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_92612a0ce291a8d74cba&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;effect&quot;,
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_004/events/0/events/0&quot;,
      &quot;value&quot;: {
        &quot;effect_index&quot;: 0,
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;ref_id&quot;: &quot;src_009&quot;,
                &quot;quote&quot;: &quot;When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.&quot;,
                &quot;reason&quot;: &quot;存在时保留 from_date 原值。&quot;
              }
            ],
            &quot;op&quot;: &quot;select_part&quot;,
            &quot;input&quot;: {
              &quot;kind&quot;: &quot;input&quot;,
              &quot;index&quot;: 0
            },
            &quot;path&quot;: [
              &quot;from_date&quot;
            ],
            &quot;output&quot;: &quot;from_date_value&quot;
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;ref_id&quot;: &quot;src_009&quot;,
                &quot;quote&quot;: &quot;When from_date is missing, omit the from_date argument.&quot;,
                &quot;reason&quot;: &quot;需要判断 from_date 是否存在以决定是否传递；存在性由输入计算，单独于原值。&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;ref_id&quot;: &quot;EM14&quot;,
                &quot;quote&quot;: &quot;build members may have a Boolean when reference: true includes the original value, false omits the member without consuming its value, and an abstract Boolean retains both possibilities.&quot;,
                &quot;reason&quot;: &quot;存在性布尔作为后续可选成员的 when 控制，而不是作为参数值。&quot;
              }
            ],
            &quot;op&quot;: &quot;compute&quot;,
            &quot;inputs&quot;: [
              {
                &quot;kind&quot;: &quot;input&quot;,
                &quot;index&quot;: 0
              }
            ],
            &quot;dependencies&quot;: [
              &quot;derived&quot;
            ],
            &quot;output&quot;: &quot;from_date_present&quot;
          }
        ]
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_07c37ee2ca00ec51146e&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;operation&quot;,
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_004/events/0/events/0/atomic_ops/0&quot;,
      &quot;value&quot;: {
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;ref_id&quot;: &quot;src_009&quot;,
            &quot;quote&quot;: &quot;When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.&quot;,
            &quot;reason&quot;: &quot;存在时保留 from_date 原值。&quot;
          }
        ],
        &quot;op&quot;: &quot;select_part&quot;,
        &quot;input&quot;: {
          &quot;kind&quot;: &quot;input&quot;,
          &quot;index&quot;: 0
        },
        &quot;path&quot;: [
          &quot;from_date&quot;
        ],
        &quot;output&quot;: &quot;from_date_value&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;declared_refs&quot;: [
        {
          &quot;kind&quot;: &quot;input&quot;,
          &quot;index&quot;: 0
        }
      ],
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_67fc3187b59cfc2f90d7&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;input_use&quot;,
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0,
        &quot;uses&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_004/events/0/events/0/atomic_ops/0/uses/0&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;input&quot;,
        &quot;index&quot;: 0
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;slot&quot;: 0,
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;input&quot;,
        &quot;index&quot;: 0
      },
      &quot;role&quot;: &quot;value&quot;,
      &quot;when&quot;: null,
      &quot;member_index&quot;: null,
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_9cd33d01da9200bdc10e&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;local_output&quot;,
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0,
        &quot;output&quot;
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_004/events/0/events/0/atomic_ops/0/output&quot;,
      &quot;value&quot;: &quot;from_date_value&quot;,
      &quot;available_locals&quot;: [
        &quot;from_date_value&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;from_date_value&quot;
      },
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_9ae77e3a8dcfcd52788c&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;operation&quot;,
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        1
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_004/events/0/events/0/atomic_ops/1&quot;,
      &quot;value&quot;: {
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;ref_id&quot;: &quot;src_009&quot;,
            &quot;quote&quot;: &quot;When from_date is missing, omit the from_date argument.&quot;,
            &quot;reason&quot;: &quot;需要判断 from_date 是否存在以决定是否传递；存在性由输入计算，单独于原值。&quot;
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;ref_id&quot;: &quot;EM14&quot;,
            &quot;quote&quot;: &quot;build members may have a Boolean when reference: true includes the original value, false omits the member without consuming its value, and an abstract Boolean retains both possibilities.&quot;,
            &quot;reason&quot;: &quot;存在性布尔作为后续可选成员的 when 控制，而不是作为参数值。&quot;
          }
        ],
        &quot;op&quot;: &quot;compute&quot;,
        &quot;inputs&quot;: [
          {
            &quot;kind&quot;: &quot;input&quot;,
            &quot;index&quot;: 0
          }
        ],
        &quot;dependencies&quot;: [
          &quot;derived&quot;
        ],
        &quot;output&quot;: &quot;from_date_present&quot;
      },
      &quot;available_locals&quot;: [
        &quot;from_date_value&quot;
      ],
      &quot;supports_expression&quot;: true,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;declared_refs&quot;: [
        {
          &quot;kind&quot;: &quot;input&quot;,
          &quot;index&quot;: 0
        }
      ],
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        1
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_733bbb5171bc60ad454e&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;input_use&quot;,
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        1,
        &quot;uses&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_004/events/0/events/0/atomic_ops/1/uses/0&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;input&quot;,
        &quot;index&quot;: 0
      },
      &quot;available_locals&quot;: [
        &quot;from_date_value&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;slot&quot;: 0,
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;input&quot;,
        &quot;index&quot;: 0
      },
      &quot;role&quot;: &quot;value&quot;,
      &quot;when&quot;: null,
      &quot;member_index&quot;: null,
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        1
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_b1f6082deef217cc997a&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;local_output&quot;,
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        1,
        &quot;output&quot;
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_004/events/0/events/0/atomic_ops/1/output&quot;,
      &quot;value&quot;: &quot;from_date_present&quot;,
      &quot;available_locals&quot;: [
        &quot;from_date_present&quot;,
        &quot;from_date_value&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;from_date_present&quot;
      },
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        1
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_b1947399edb7640311b5&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;output_binding&quot;,
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;raw_path&quot;: [
        &quot;output_bindings&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_004/output_bindings/0&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;from_date_value&quot;
      },
      &quot;available_locals&quot;: [
        &quot;from_date_present&quot;,
        &quot;from_date_value&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;output_index&quot;: 0,
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;from_date_value&quot;
      },
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_b15cd131bc069d39dcc6&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;output_binding&quot;,
      &quot;instruction_id&quot;: &quot;ir_004&quot;,
      &quot;raw_path&quot;: [
        &quot;output_bindings&quot;,
        1
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_004/output_bindings/1&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;from_date_present&quot;
      },
      &quot;available_locals&quot;: [
        &quot;from_date_present&quot;,
        &quot;from_date_value&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;output_index&quot;: 1,
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;from_date_present&quot;
      },
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_9a2d9bbed999b0627aa5&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;processing&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_005/events/0&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;processing&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;events&quot;: [
          {
            &quot;effect_index&quot;: 0,
            &quot;atomic_ops&quot;: [
              {
                &quot;evidences&quot;: [
                  {
                    &quot;basis&quot;: &quot;source&quot;,
                    &quot;ref_id&quot;: &quot;src_009&quot;,
                    &quot;quote&quot;: &quot;When limit is present, pass its value unchanged as the limit argument.&quot;,
                    &quot;reason&quot;: &quot;存在时保留 limit 原值。&quot;
                  }
                ],
                &quot;op&quot;: &quot;select_part&quot;,
                &quot;input&quot;: {
                  &quot;kind&quot;: &quot;input&quot;,
                  &quot;index&quot;: 0
                },
                &quot;path&quot;: [
                  &quot;limit&quot;
                ],
                &quot;output&quot;: &quot;limit_value&quot;
              },
              {
                &quot;evidences&quot;: [
                  {
                    &quot;basis&quot;: &quot;source&quot;,
                    &quot;ref_id&quot;: &quot;src_009&quot;,
                    &quot;quote&quot;: &quot;When limit is missing, omit the limit argument.&quot;,
                    &quot;reason&quot;: &quot;需要判断 limit 是否存在以决定是否传递；存在性由输入计算，单独于原值。&quot;
                  },
                  {
                    &quot;basis&quot;: &quot;execution_model&quot;,
                    &quot;ref_id&quot;: &quot;EM14&quot;,
                    &quot;quote&quot;: &quot;build members may have a Boolean when reference: true includes the original value, false omits the member without consuming its value, and an abstract Boolean retains both possibilities.&quot;,
                    &quot;reason&quot;: &quot;存在性布尔作为后续可选成员的 when 控制，而不是作为参数值。&quot;
                  }
                ],
                &quot;op&quot;: &quot;compute&quot;,
                &quot;inputs&quot;: [
                  {
                    &quot;kind&quot;: &quot;input&quot;,
                    &quot;index&quot;: 0
                  }
                ],
                &quot;dependencies&quot;: [
                  &quot;derived&quot;
                ],
                &quot;output&quot;: &quot;limit_present&quot;
              }
            ]
          }
        ],
        &quot;returns&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;ref_id&quot;: &quot;EM10&quot;,
            &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
            &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，可选字段提取按默认模式分析。&quot;
          }
        ]
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_b25f4a46ea5418411722&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;effect&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_005/events/0/events/0&quot;,
      &quot;value&quot;: {
        &quot;effect_index&quot;: 0,
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;ref_id&quot;: &quot;src_009&quot;,
                &quot;quote&quot;: &quot;When limit is present, pass its value unchanged as the limit argument.&quot;,
                &quot;reason&quot;: &quot;存在时保留 limit 原值。&quot;
              }
            ],
            &quot;op&quot;: &quot;select_part&quot;,
            &quot;input&quot;: {
              &quot;kind&quot;: &quot;input&quot;,
              &quot;index&quot;: 0
            },
            &quot;path&quot;: [
              &quot;limit&quot;
            ],
            &quot;output&quot;: &quot;limit_value&quot;
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;ref_id&quot;: &quot;src_009&quot;,
                &quot;quote&quot;: &quot;When limit is missing, omit the limit argument.&quot;,
                &quot;reason&quot;: &quot;需要判断 limit 是否存在以决定是否传递；存在性由输入计算，单独于原值。&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;ref_id&quot;: &quot;EM14&quot;,
                &quot;quote&quot;: &quot;build members may have a Boolean when reference: true includes the original value, false omits the member without consuming its value, and an abstract Boolean retains both possibilities.&quot;,
                &quot;reason&quot;: &quot;存在性布尔作为后续可选成员的 when 控制，而不是作为参数值。&quot;
              }
            ],
            &quot;op&quot;: &quot;compute&quot;,
            &quot;inputs&quot;: [
              {
                &quot;kind&quot;: &quot;input&quot;,
                &quot;index&quot;: 0
              }
            ],
            &quot;dependencies&quot;: [
              &quot;derived&quot;
            ],
            &quot;output&quot;: &quot;limit_present&quot;
          }
        ]
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_badf9aba04923baca25f&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;operation&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_005/events/0/events/0/atomic_ops/0&quot;,
      &quot;value&quot;: {
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;ref_id&quot;: &quot;src_009&quot;,
            &quot;quote&quot;: &quot;When limit is present, pass its value unchanged as the limit argument.&quot;,
            &quot;reason&quot;: &quot;存在时保留 limit 原值。&quot;
          }
        ],
        &quot;op&quot;: &quot;select_part&quot;,
        &quot;input&quot;: {
          &quot;kind&quot;: &quot;input&quot;,
          &quot;index&quot;: 0
        },
        &quot;path&quot;: [
          &quot;limit&quot;
        ],
        &quot;output&quot;: &quot;limit_value&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;declared_refs&quot;: [
        {
          &quot;kind&quot;: &quot;input&quot;,
          &quot;index&quot;: 0
        }
      ],
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_35794fee45926702aa0a&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;input_use&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0,
        &quot;uses&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_005/events/0/events/0/atomic_ops/0/uses/0&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;input&quot;,
        &quot;index&quot;: 0
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;slot&quot;: 0,
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;input&quot;,
        &quot;index&quot;: 0
      },
      &quot;role&quot;: &quot;value&quot;,
      &quot;when&quot;: null,
      &quot;member_index&quot;: null,
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_f7c5c6d6c61edc38bbad&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;local_output&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0,
        &quot;output&quot;
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_005/events/0/events/0/atomic_ops/0/output&quot;,
      &quot;value&quot;: &quot;limit_value&quot;,
      &quot;available_locals&quot;: [
        &quot;limit_value&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;limit_value&quot;
      },
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_bc07f7377292754afc22&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;operation&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        1
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_005/events/0/events/0/atomic_ops/1&quot;,
      &quot;value&quot;: {
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;ref_id&quot;: &quot;src_009&quot;,
            &quot;quote&quot;: &quot;When limit is missing, omit the limit argument.&quot;,
            &quot;reason&quot;: &quot;需要判断 limit 是否存在以决定是否传递；存在性由输入计算，单独于原值。&quot;
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;ref_id&quot;: &quot;EM14&quot;,
            &quot;quote&quot;: &quot;build members may have a Boolean when reference: true includes the original value, false omits the member without consuming its value, and an abstract Boolean retains both possibilities.&quot;,
            &quot;reason&quot;: &quot;存在性布尔作为后续可选成员的 when 控制，而不是作为参数值。&quot;
          }
        ],
        &quot;op&quot;: &quot;compute&quot;,
        &quot;inputs&quot;: [
          {
            &quot;kind&quot;: &quot;input&quot;,
            &quot;index&quot;: 0
          }
        ],
        &quot;dependencies&quot;: [
          &quot;derived&quot;
        ],
        &quot;output&quot;: &quot;limit_present&quot;
      },
      &quot;available_locals&quot;: [
        &quot;limit_value&quot;
      ],
      &quot;supports_expression&quot;: true,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;declared_refs&quot;: [
        {
          &quot;kind&quot;: &quot;input&quot;,
          &quot;index&quot;: 0
        }
      ],
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        1
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_ed03c04b7f7952cf9324&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;input_use&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        1,
        &quot;uses&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_005/events/0/events/0/atomic_ops/1/uses/0&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;input&quot;,
        &quot;index&quot;: 0
      },
      &quot;available_locals&quot;: [
        &quot;limit_value&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;slot&quot;: 0,
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;input&quot;,
        &quot;index&quot;: 0
      },
      &quot;role&quot;: &quot;value&quot;,
      &quot;when&quot;: null,
      &quot;member_index&quot;: null,
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        1
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_9d412af77fe6616dc95a&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;local_output&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        1,
        &quot;output&quot;
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_005/events/0/events/0/atomic_ops/1/output&quot;,
      &quot;value&quot;: &quot;limit_present&quot;,
      &quot;available_locals&quot;: [
        &quot;limit_present&quot;,
        &quot;limit_value&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;limit_present&quot;
      },
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        1
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_786d4cfa6d1bcce995d0&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;output_binding&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;raw_path&quot;: [
        &quot;output_bindings&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_005/output_bindings/0&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;limit_value&quot;
      },
      &quot;available_locals&quot;: [
        &quot;limit_present&quot;,
        &quot;limit_value&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;output_index&quot;: 0,
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;limit_value&quot;
      },
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_b81373c5c1dd0668d58a&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;output_binding&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;raw_path&quot;: [
        &quot;output_bindings&quot;,
        1
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_005/output_bindings/1&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;limit_present&quot;
      },
      &quot;available_locals&quot;: [
        &quot;limit_present&quot;,
        &quot;limit_value&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;output_index&quot;: 1,
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;limit_present&quot;
      },
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_aa3f6e9ed6b0c285d52a&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;processing&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_007/events/0&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;processing&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;events&quot;: [
          {
            &quot;effect_index&quot;: 0,
            &quot;atomic_ops&quot;: [
              {
                &quot;evidences&quot;: [
                  {
                    &quot;basis&quot;: &quot;source&quot;,
                    &quot;ref_id&quot;: &quot;src_008&quot;,
                    &quot;quote&quot;: &quot;using request.term unchanged as its query argument&quot;,
                    &quot;reason&quot;: &quot;query 成员来自当前 IR 的查询词输入，保持原值。&quot;
                  },
                  {
                    &quot;basis&quot;: &quot;source&quot;,
                    &quot;ref_id&quot;: &quot;src_009&quot;,
                    &quot;quote&quot;: &quot;When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.&quot;,
                    &quot;reason&quot;: &quot;from_date 成员在存在时包含原值，并由存在性布尔控制。&quot;
                  },
                  {
                    &quot;basis&quot;: &quot;source&quot;,
                    &quot;ref_id&quot;: &quot;src_009&quot;,
                    &quot;quote&quot;: &quot;When limit is present, pass its value unchanged as the limit argument.&quot;,
                    &quot;reason&quot;: &quot;limit 成员在存在时包含原值，并由存在性布尔控制。&quot;
                  },
                  {
                    &quot;basis&quot;: &quot;execution_model&quot;,
                    &quot;ref_id&quot;: &quot;EM14&quot;,
                    &quot;quote&quot;: &quot;build members may have a Boolean when reference: true includes the original value, false omits the member without consuming its value, and an abstract Boolean retains both possibilities.&quot;,
                    &quot;reason&quot;: &quot;from_date 与 limit 用各自存在性布尔作为 when；存在性标志不作为 payload。&quot;
                  }
                ],
                &quot;op&quot;: &quot;build&quot;,
                &quot;parts&quot;: [
                  {
                    &quot;path&quot;: [
                      &quot;query&quot;
                    ],
                    &quot;value&quot;: {
                      &quot;kind&quot;: &quot;input&quot;,
                      &quot;index&quot;: 1
                    },
                    &quot;when&quot;: null
                  },
                  {
                    &quot;path&quot;: [
                      &quot;from_date&quot;
                    ],
                    &quot;value&quot;: {
                      &quot;kind&quot;: &quot;input&quot;,
                      &quot;index&quot;: 2
                    },
                    &quot;when&quot;: {
                      &quot;kind&quot;: &quot;input&quot;,
                      &quot;index&quot;: 3
                    }
                  },
                  {
                    &quot;path&quot;: [
                      &quot;limit&quot;
                    ],
                    &quot;value&quot;: {
                      &quot;kind&quot;: &quot;input&quot;,
                      &quot;index&quot;: 4
                    },
                    &quot;when&quot;: {
                      &quot;kind&quot;: &quot;input&quot;,
                      &quot;index&quot;: 5
                    }
                  }
                ],
                &quot;output&quot;: &quot;request&quot;,
                &quot;container&quot;: &quot;object&quot;
              }
            ]
          },
          {
            &quot;effect_index&quot;: null,
            &quot;atomic_ops&quot;: [
              {
                &quot;evidences&quot;: [
                  {
                    &quot;basis&quot;: &quot;execution_model&quot;,
                    &quot;ref_id&quot;: &quot;EM13&quot;,
                    &quot;quote&quot;: &quot;A tool delivery with no established network effect is a null-effect deliver to a tool location, including an explicit empty argument list for a known zero-argument request.&quot;,
                    &quot;reason&quot;: &quot;未发现实际网络机制，将实际请求参数投递到 index.search 工具边界，记为 null-effect deliver。&quot;
                  },
                  {
                    &quot;basis&quot;: &quot;source&quot;,
                    &quot;ref_id&quot;: &quot;src_008&quot;,
                    &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
                    &quot;reason&quot;: &quot;该指令确实把构造的参数对象交给 index.search。&quot;
                  }
                ],
                &quot;op&quot;: &quot;deliver&quot;,
                &quot;inputs&quot;: [
                  {
                    &quot;kind&quot;: &quot;local&quot;,
                    &quot;name&quot;: &quot;request&quot;
                  }
                ],
                &quot;target&quot;: &quot;loc_index_search&quot;
              }
            ]
          },
          {
            &quot;effect_index&quot;: null,
            &quot;atomic_ops&quot;: [
              {
                &quot;evidences&quot;: [
                  {
                    &quot;basis&quot;: &quot;execution_model&quot;,
                    &quot;ref_id&quot;: &quot;EM09&quot;,
                    &quot;quote&quot;: &quot;known tool acquisition without established networking uses receive at a tool location in a null-effect event.&quot;,
                    &quot;reason&quot;: &quot;index.search 返回内容有获取边界，但未建立网络传输，故在工具位置用 null-effect receive 获取。&quot;
                  },
                  {
                    &quot;basis&quot;: &quot;source&quot;,
                    &quot;ref_id&quot;: &quot;src_008&quot;,
                    &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
                    &quot;reason&quot;: &quot;响应来自这次实际调用；请求依赖为同一 request 对象。&quot;
                  }
                ],
                &quot;op&quot;: &quot;receive&quot;,
                &quot;location&quot;: &quot;loc_index_search&quot;,
                &quot;inputs&quot;: [
                  {
                    &quot;kind&quot;: &quot;local&quot;,
                    &quot;name&quot;: &quot;request&quot;
                  }
                ],
                &quot;output&quot;: &quot;response&quot;
              }
            ]
          }
        ],
        &quot;returns&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;ref_id&quot;: &quot;EM10&quot;,
            &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
            &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，参数构造与工具获取按默认模式分析。&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;ref_id&quot;: &quot;src_008&quot;,
            &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
            &quot;reason&quot;: &quot;源文要求一次实际工具调用，未说明本地 worker 或模型执行边界。&quot;
          }
        ]
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_3e0cc1b09fd9c2df68ac&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;effect&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_007/events/0/events/0&quot;,
      &quot;value&quot;: {
        &quot;effect_index&quot;: 0,
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;ref_id&quot;: &quot;src_008&quot;,
                &quot;quote&quot;: &quot;using request.term unchanged as its query argument&quot;,
                &quot;reason&quot;: &quot;query 成员来自当前 IR 的查询词输入，保持原值。&quot;
              },
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;ref_id&quot;: &quot;src_009&quot;,
                &quot;quote&quot;: &quot;When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.&quot;,
                &quot;reason&quot;: &quot;from_date 成员在存在时包含原值，并由存在性布尔控制。&quot;
              },
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;ref_id&quot;: &quot;src_009&quot;,
                &quot;quote&quot;: &quot;When limit is present, pass its value unchanged as the limit argument.&quot;,
                &quot;reason&quot;: &quot;limit 成员在存在时包含原值，并由存在性布尔控制。&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;ref_id&quot;: &quot;EM14&quot;,
                &quot;quote&quot;: &quot;build members may have a Boolean when reference: true includes the original value, false omits the member without consuming its value, and an abstract Boolean retains both possibilities.&quot;,
                &quot;reason&quot;: &quot;from_date 与 limit 用各自存在性布尔作为 when；存在性标志不作为 payload。&quot;
              }
            ],
            &quot;op&quot;: &quot;build&quot;,
            &quot;parts&quot;: [
              {
                &quot;path&quot;: [
                  &quot;query&quot;
                ],
                &quot;value&quot;: {
                  &quot;kind&quot;: &quot;input&quot;,
                  &quot;index&quot;: 1
                },
                &quot;when&quot;: null
              },
              {
                &quot;path&quot;: [
                  &quot;from_date&quot;
                ],
                &quot;value&quot;: {
                  &quot;kind&quot;: &quot;input&quot;,
                  &quot;index&quot;: 2
                },
                &quot;when&quot;: {
                  &quot;kind&quot;: &quot;input&quot;,
                  &quot;index&quot;: 3
                }
              },
              {
                &quot;path&quot;: [
                  &quot;limit&quot;
                ],
                &quot;value&quot;: {
                  &quot;kind&quot;: &quot;input&quot;,
                  &quot;index&quot;: 4
                },
                &quot;when&quot;: {
                  &quot;kind&quot;: &quot;input&quot;,
                  &quot;index&quot;: 5
                }
              }
            ],
            &quot;output&quot;: &quot;request&quot;,
            &quot;container&quot;: &quot;object&quot;
          }
        ]
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_12b03164f44793667ef7&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;operation&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_007/events/0/events/0/atomic_ops/0&quot;,
      &quot;value&quot;: {
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;ref_id&quot;: &quot;src_008&quot;,
            &quot;quote&quot;: &quot;using request.term unchanged as its query argument&quot;,
            &quot;reason&quot;: &quot;query 成员来自当前 IR 的查询词输入，保持原值。&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;ref_id&quot;: &quot;src_009&quot;,
            &quot;quote&quot;: &quot;When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.&quot;,
            &quot;reason&quot;: &quot;from_date 成员在存在时包含原值，并由存在性布尔控制。&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;ref_id&quot;: &quot;src_009&quot;,
            &quot;quote&quot;: &quot;When limit is present, pass its value unchanged as the limit argument.&quot;,
            &quot;reason&quot;: &quot;limit 成员在存在时包含原值，并由存在性布尔控制。&quot;
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;ref_id&quot;: &quot;EM14&quot;,
            &quot;quote&quot;: &quot;build members may have a Boolean when reference: true includes the original value, false omits the member without consuming its value, and an abstract Boolean retains both possibilities.&quot;,
            &quot;reason&quot;: &quot;from_date 与 limit 用各自存在性布尔作为 when；存在性标志不作为 payload。&quot;
          }
        ],
        &quot;op&quot;: &quot;build&quot;,
        &quot;parts&quot;: [
          {
            &quot;path&quot;: [
              &quot;query&quot;
            ],
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;input&quot;,
              &quot;index&quot;: 1
            },
            &quot;when&quot;: null
          },
          {
            &quot;path&quot;: [
              &quot;from_date&quot;
            ],
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;input&quot;,
              &quot;index&quot;: 2
            },
            &quot;when&quot;: {
              &quot;kind&quot;: &quot;input&quot;,
              &quot;index&quot;: 3
            }
          },
          {
            &quot;path&quot;: [
              &quot;limit&quot;
            ],
            &quot;value&quot;: {
              &quot;kind&quot;: &quot;input&quot;,
              &quot;index&quot;: 4
            },
            &quot;when&quot;: {
              &quot;kind&quot;: &quot;input&quot;,
              &quot;index&quot;: 5
            }
          }
        ],
        &quot;output&quot;: &quot;request&quot;,
        &quot;container&quot;: &quot;object&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;declared_refs&quot;: [
        {
          &quot;kind&quot;: &quot;input&quot;,
          &quot;index&quot;: 1
        },
        {
          &quot;kind&quot;: &quot;input&quot;,
          &quot;index&quot;: 3
        },
        {
          &quot;kind&quot;: &quot;input&quot;,
          &quot;index&quot;: 2
        },
        {
          &quot;kind&quot;: &quot;input&quot;,
          &quot;index&quot;: 5
        },
        {
          &quot;kind&quot;: &quot;input&quot;,
          &quot;index&quot;: 4
        }
      ],
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_1bbd665d2f962e75961e&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;input_use&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0,
        &quot;uses&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_007/events/0/events/0/atomic_ops/0/uses/0&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;input&quot;,
        &quot;index&quot;: 1
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;slot&quot;: 0,
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;input&quot;,
        &quot;index&quot;: 1
      },
      &quot;role&quot;: &quot;value&quot;,
      &quot;when&quot;: null,
      &quot;member_index&quot;: 0,
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_73ec942a6ebbb7271db9&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;input_use&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0,
        &quot;uses&quot;,
        1
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_007/events/0/events/0/atomic_ops/0/uses/1&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;input&quot;,
        &quot;index&quot;: 3
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;slot&quot;: 1,
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;input&quot;,
        &quot;index&quot;: 3
      },
      &quot;role&quot;: &quot;control&quot;,
      &quot;when&quot;: null,
      &quot;member_index&quot;: 1,
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_b1e6fdb5132bfbe855d7&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;input_use&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0,
        &quot;uses&quot;,
        2
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_007/events/0/events/0/atomic_ops/0/uses/2&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;input&quot;,
        &quot;index&quot;: 2
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;slot&quot;: 2,
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;input&quot;,
        &quot;index&quot;: 2
      },
      &quot;role&quot;: &quot;value&quot;,
      &quot;when&quot;: {
        &quot;kind&quot;: &quot;input&quot;,
        &quot;index&quot;: 3
      },
      &quot;member_index&quot;: 1,
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_d8f0072ac063e86498fa&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;input_use&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0,
        &quot;uses&quot;,
        3
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_007/events/0/events/0/atomic_ops/0/uses/3&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;input&quot;,
        &quot;index&quot;: 5
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;slot&quot;: 3,
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;input&quot;,
        &quot;index&quot;: 5
      },
      &quot;role&quot;: &quot;control&quot;,
      &quot;when&quot;: null,
      &quot;member_index&quot;: 2,
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_80e369f6ba14b32a5d2e&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;input_use&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0,
        &quot;uses&quot;,
        4
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_007/events/0/events/0/atomic_ops/0/uses/4&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;input&quot;,
        &quot;index&quot;: 4
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;slot&quot;: 4,
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;input&quot;,
        &quot;index&quot;: 4
      },
      &quot;role&quot;: &quot;value&quot;,
      &quot;when&quot;: {
        &quot;kind&quot;: &quot;input&quot;,
        &quot;index&quot;: 5
      },
      &quot;member_index&quot;: 2,
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_c1c69e7212e066def972&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;local_output&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0,
        &quot;output&quot;
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_007/events/0/events/0/atomic_ops/0/output&quot;,
      &quot;value&quot;: &quot;request&quot;,
      &quot;available_locals&quot;: [
        &quot;request&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;request&quot;
      },
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_724f3c8bda9b0db0144f&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;effect&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        1
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_007/events/0/events/1&quot;,
      &quot;value&quot;: {
        &quot;effect_index&quot;: null,
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;ref_id&quot;: &quot;EM13&quot;,
                &quot;quote&quot;: &quot;A tool delivery with no established network effect is a null-effect deliver to a tool location, including an explicit empty argument list for a known zero-argument request.&quot;,
                &quot;reason&quot;: &quot;未发现实际网络机制，将实际请求参数投递到 index.search 工具边界，记为 null-effect deliver。&quot;
              },
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;ref_id&quot;: &quot;src_008&quot;,
                &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
                &quot;reason&quot;: &quot;该指令确实把构造的参数对象交给 index.search。&quot;
              }
            ],
            &quot;op&quot;: &quot;deliver&quot;,
            &quot;inputs&quot;: [
              {
                &quot;kind&quot;: &quot;local&quot;,
                &quot;name&quot;: &quot;request&quot;
              }
            ],
            &quot;target&quot;: &quot;loc_index_search&quot;
          }
        ]
      },
      &quot;available_locals&quot;: [
        &quot;request&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_450c34e4f0db7a8c6802&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;operation&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        1,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_007/events/0/events/1/atomic_ops/0&quot;,
      &quot;value&quot;: {
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;ref_id&quot;: &quot;EM13&quot;,
            &quot;quote&quot;: &quot;A tool delivery with no established network effect is a null-effect deliver to a tool location, including an explicit empty argument list for a known zero-argument request.&quot;,
            &quot;reason&quot;: &quot;未发现实际网络机制，将实际请求参数投递到 index.search 工具边界，记为 null-effect deliver。&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;ref_id&quot;: &quot;src_008&quot;,
            &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
            &quot;reason&quot;: &quot;该指令确实把构造的参数对象交给 index.search。&quot;
          }
        ],
        &quot;op&quot;: &quot;deliver&quot;,
        &quot;inputs&quot;: [
          {
            &quot;kind&quot;: &quot;local&quot;,
            &quot;name&quot;: &quot;request&quot;
          }
        ],
        &quot;target&quot;: &quot;loc_index_search&quot;
      },
      &quot;available_locals&quot;: [
        &quot;request&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;declared_refs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;request&quot;
        }
      ],
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        1,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_eb630a83282c75fd652c&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;input_use&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        1,
        &quot;atomic_ops&quot;,
        0,
        &quot;uses&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_007/events/0/events/1/atomic_ops/0/uses/0&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;request&quot;
      },
      &quot;available_locals&quot;: [
        &quot;request&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;slot&quot;: 0,
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;request&quot;
      },
      &quot;role&quot;: &quot;value&quot;,
      &quot;when&quot;: null,
      &quot;member_index&quot;: null,
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        1,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_75410d9218c7f5c43912&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;effect&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        2
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_007/events/0/events/2&quot;,
      &quot;value&quot;: {
        &quot;effect_index&quot;: null,
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;ref_id&quot;: &quot;EM09&quot;,
                &quot;quote&quot;: &quot;known tool acquisition without established networking uses receive at a tool location in a null-effect event.&quot;,
                &quot;reason&quot;: &quot;index.search 返回内容有获取边界，但未建立网络传输，故在工具位置用 null-effect receive 获取。&quot;
              },
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;ref_id&quot;: &quot;src_008&quot;,
                &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
                &quot;reason&quot;: &quot;响应来自这次实际调用；请求依赖为同一 request 对象。&quot;
              }
            ],
            &quot;op&quot;: &quot;receive&quot;,
            &quot;location&quot;: &quot;loc_index_search&quot;,
            &quot;inputs&quot;: [
              {
                &quot;kind&quot;: &quot;local&quot;,
                &quot;name&quot;: &quot;request&quot;
              }
            ],
            &quot;output&quot;: &quot;response&quot;
          }
        ]
      },
      &quot;available_locals&quot;: [
        &quot;request&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_33b0a2a68c0f8a5c5112&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;operation&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        2,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_007/events/0/events/2/atomic_ops/0&quot;,
      &quot;value&quot;: {
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;ref_id&quot;: &quot;EM09&quot;,
            &quot;quote&quot;: &quot;known tool acquisition without established networking uses receive at a tool location in a null-effect event.&quot;,
            &quot;reason&quot;: &quot;index.search 返回内容有获取边界，但未建立网络传输，故在工具位置用 null-effect receive 获取。&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;ref_id&quot;: &quot;src_008&quot;,
            &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
            &quot;reason&quot;: &quot;响应来自这次实际调用；请求依赖为同一 request 对象。&quot;
          }
        ],
        &quot;op&quot;: &quot;receive&quot;,
        &quot;location&quot;: &quot;loc_index_search&quot;,
        &quot;inputs&quot;: [
          {
            &quot;kind&quot;: &quot;local&quot;,
            &quot;name&quot;: &quot;request&quot;
          }
        ],
        &quot;output&quot;: &quot;response&quot;
      },
      &quot;available_locals&quot;: [
        &quot;request&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;declared_refs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;request&quot;
        }
      ],
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        2,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_11a5ab7695be56a805cb&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;input_use&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        2,
        &quot;atomic_ops&quot;,
        0,
        &quot;uses&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_007/events/0/events/2/atomic_ops/0/uses/0&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;request&quot;
      },
      &quot;available_locals&quot;: [
        &quot;request&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;slot&quot;: 0,
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;request&quot;
      },
      &quot;role&quot;: &quot;value&quot;,
      &quot;when&quot;: null,
      &quot;member_index&quot;: null,
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        2,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_08214f177451e8c59481&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;local_output&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        2,
        &quot;atomic_ops&quot;,
        0,
        &quot;output&quot;
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_007/events/0/events/2/atomic_ops/0/output&quot;,
      &quot;value&quot;: &quot;response&quot;,
      &quot;available_locals&quot;: [
        &quot;request&quot;,
        &quot;response&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;response&quot;
      },
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        2,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_635d0b90c709bb3d91b7&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;output_binding&quot;,
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;raw_path&quot;: [
        &quot;output_bindings&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_007/output_bindings/0&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;response&quot;
      },
      &quot;available_locals&quot;: [
        &quot;request&quot;,
        &quot;response&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 6,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;output_index&quot;: 0,
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;response&quot;
      },
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_11b9943abda3d0791dbd&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;processing&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_009/events/0&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;processing&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;events&quot;: [
          {
            &quot;effect_index&quot;: 0,
            &quot;atomic_ops&quot;: [
              {
                &quot;evidences&quot;: [
                  {
                    &quot;basis&quot;: &quot;source&quot;,
                    &quot;ref_id&quot;: &quot;src_013&quot;,
                    &quot;quote&quot;: &quot;After the search, write the response&#x27;s total value to local count.txt.&quot;,
                    &quot;reason&quot;: &quot;明确从搜索响应选择 total 原值。&quot;
                  }
                ],
                &quot;op&quot;: &quot;select_part&quot;,
                &quot;input&quot;: {
                  &quot;kind&quot;: &quot;input&quot;,
                  &quot;index&quot;: 0
                },
                &quot;path&quot;: [
                  &quot;total&quot;
                ],
                &quot;output&quot;: &quot;total&quot;
              }
            ]
          }
        ],
        &quot;returns&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;ref_id&quot;: &quot;EM10&quot;,
            &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
            &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，响应字段提取按默认模式分析。&quot;
          }
        ]
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_98919856cc221d2b6fb2&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;effect&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_009/events/0/events/0&quot;,
      &quot;value&quot;: {
        &quot;effect_index&quot;: 0,
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;ref_id&quot;: &quot;src_013&quot;,
                &quot;quote&quot;: &quot;After the search, write the response&#x27;s total value to local count.txt.&quot;,
                &quot;reason&quot;: &quot;明确从搜索响应选择 total 原值。&quot;
              }
            ],
            &quot;op&quot;: &quot;select_part&quot;,
            &quot;input&quot;: {
              &quot;kind&quot;: &quot;input&quot;,
              &quot;index&quot;: 0
            },
            &quot;path&quot;: [
              &quot;total&quot;
            ],
            &quot;output&quot;: &quot;total&quot;
          }
        ]
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_b715f7a9008aba5e4b20&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;operation&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_009/events/0/events/0/atomic_ops/0&quot;,
      &quot;value&quot;: {
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;ref_id&quot;: &quot;src_013&quot;,
            &quot;quote&quot;: &quot;After the search, write the response&#x27;s total value to local count.txt.&quot;,
            &quot;reason&quot;: &quot;明确从搜索响应选择 total 原值。&quot;
          }
        ],
        &quot;op&quot;: &quot;select_part&quot;,
        &quot;input&quot;: {
          &quot;kind&quot;: &quot;input&quot;,
          &quot;index&quot;: 0
        },
        &quot;path&quot;: [
          &quot;total&quot;
        ],
        &quot;output&quot;: &quot;total&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;declared_refs&quot;: [
        {
          &quot;kind&quot;: &quot;input&quot;,
          &quot;index&quot;: 0
        }
      ],
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_1e6198f794b8c0f3080c&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;input_use&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0,
        &quot;uses&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_009/events/0/events/0/atomic_ops/0/uses/0&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;input&quot;,
        &quot;index&quot;: 0
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;slot&quot;: 0,
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;input&quot;,
        &quot;index&quot;: 0
      },
      &quot;role&quot;: &quot;value&quot;,
      &quot;when&quot;: null,
      &quot;member_index&quot;: null,
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_b5393faae48f51bf3aa6&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;local_output&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0,
        &quot;output&quot;
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_009/events/0/events/0/atomic_ops/0/output&quot;,
      &quot;value&quot;: &quot;total&quot;,
      &quot;available_locals&quot;: [
        &quot;total&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;total&quot;
      },
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_b4f8c07d5b3ff2b670f8&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;output_binding&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;raw_path&quot;: [
        &quot;output_bindings&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_009/output_bindings/0&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;total&quot;
      },
      &quot;available_locals&quot;: [
        &quot;total&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;output_index&quot;: 0,
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;total&quot;
      },
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_a01e9463dca7c2f68632&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;processing&quot;,
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_010/events/0&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;processing&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;events&quot;: [
          {
            &quot;effect_index&quot;: 0,
            &quot;atomic_ops&quot;: [
              {
                &quot;evidences&quot;: [
                  {
                    &quot;basis&quot;: &quot;source&quot;,
                    &quot;ref_id&quot;: &quot;src_013&quot;,
                    &quot;quote&quot;: &quot;After the search, write the response&#x27;s total value to local count.txt.&quot;,
                    &quot;reason&quot;: &quot;将当前 IR 输入中的 total 值写入 count.txt；未说明追加，按 replace 表示写文件内容。&quot;
                  }
                ],
                &quot;op&quot;: &quot;write&quot;,
                &quot;target&quot;: &quot;loc_count_txt&quot;,
                &quot;mode&quot;: &quot;replace&quot;,
                &quot;input&quot;: {
                  &quot;kind&quot;: &quot;input&quot;,
                  &quot;index&quot;: 1
                }
              }
            ]
          }
        ],
        &quot;returns&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;ref_id&quot;: &quot;EM10&quot;,
            &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
            &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，文件写入按默认模式分析。&quot;
          }
        ]
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 2,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_d230ae95799327ab8a84&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;effect&quot;,
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_010/events/0/events/0&quot;,
      &quot;value&quot;: {
        &quot;effect_index&quot;: 0,
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;ref_id&quot;: &quot;src_013&quot;,
                &quot;quote&quot;: &quot;After the search, write the response&#x27;s total value to local count.txt.&quot;,
                &quot;reason&quot;: &quot;将当前 IR 输入中的 total 值写入 count.txt；未说明追加，按 replace 表示写文件内容。&quot;
              }
            ],
            &quot;op&quot;: &quot;write&quot;,
            &quot;target&quot;: &quot;loc_count_txt&quot;,
            &quot;mode&quot;: &quot;replace&quot;,
            &quot;input&quot;: {
              &quot;kind&quot;: &quot;input&quot;,
              &quot;index&quot;: 1
            }
          }
        ]
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 2,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_935679a9c6cf862ce45a&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;operation&quot;,
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_010/events/0/events/0/atomic_ops/0&quot;,
      &quot;value&quot;: {
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;ref_id&quot;: &quot;src_013&quot;,
            &quot;quote&quot;: &quot;After the search, write the response&#x27;s total value to local count.txt.&quot;,
            &quot;reason&quot;: &quot;将当前 IR 输入中的 total 值写入 count.txt；未说明追加，按 replace 表示写文件内容。&quot;
          }
        ],
        &quot;op&quot;: &quot;write&quot;,
        &quot;target&quot;: &quot;loc_count_txt&quot;,
        &quot;mode&quot;: &quot;replace&quot;,
        &quot;input&quot;: {
          &quot;kind&quot;: &quot;input&quot;,
          &quot;index&quot;: 1
        }
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 2,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;declared_refs&quot;: [
        {
          &quot;kind&quot;: &quot;input&quot;,
          &quot;index&quot;: 1
        }
      ],
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_cb3eb1f9d9b790aeb342&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;input_use&quot;,
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0,
        &quot;uses&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_010/events/0/events/0/atomic_ops/0/uses/0&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;input&quot;,
        &quot;index&quot;: 1
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 2,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;slot&quot;: 0,
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;input&quot;,
        &quot;index&quot;: 1
      },
      &quot;role&quot;: &quot;value&quot;,
      &quot;when&quot;: null,
      &quot;member_index&quot;: null,
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_3c7de76f62828f0259b5&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;processing&quot;,
      &quot;instruction_id&quot;: &quot;ir_011&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_011/events/0&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;processing&quot;,
        &quot;mode&quot;: &quot;default&quot;,
        &quot;events&quot;: [
          {
            &quot;effect_index&quot;: 0,
            &quot;atomic_ops&quot;: [
              {
                &quot;evidences&quot;: [
                  {
                    &quot;basis&quot;: &quot;source&quot;,
                    &quot;ref_id&quot;: &quot;src_014&quot;,
                    &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
                    &quot;reason&quot;: &quot;明确从搜索响应选择 items 原值。&quot;
                  }
                ],
                &quot;op&quot;: &quot;select_part&quot;,
                &quot;input&quot;: {
                  &quot;kind&quot;: &quot;input&quot;,
                  &quot;index&quot;: 0
                },
                &quot;path&quot;: [
                  &quot;items&quot;
                ],
                &quot;output&quot;: &quot;items&quot;
              }
            ]
          }
        ],
        &quot;returns&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;ref_id&quot;: &quot;EM10&quot;,
            &quot;quote&quot;: &quot;Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired.&quot;,
            &quot;reason&quot;: &quot;没有显式本地隔离或模型处理证据，响应字段提取按默认模式分析。&quot;
          }
        ]
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_cfea1e8d28c454dc55e2&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;effect&quot;,
      &quot;instruction_id&quot;: &quot;ir_011&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_011/events/0/events/0&quot;,
      &quot;value&quot;: {
        &quot;effect_index&quot;: 0,
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;ref_id&quot;: &quot;src_014&quot;,
                &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
                &quot;reason&quot;: &quot;明确从搜索响应选择 items 原值。&quot;
              }
            ],
            &quot;op&quot;: &quot;select_part&quot;,
            &quot;input&quot;: {
              &quot;kind&quot;: &quot;input&quot;,
              &quot;index&quot;: 0
            },
            &quot;path&quot;: [
              &quot;items&quot;
            ],
            &quot;output&quot;: &quot;items&quot;
          }
        ]
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_d41913d2fb4e566e2d12&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;operation&quot;,
      &quot;instruction_id&quot;: &quot;ir_011&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_011/events/0/events/0/atomic_ops/0&quot;,
      &quot;value&quot;: {
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;ref_id&quot;: &quot;src_014&quot;,
            &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
            &quot;reason&quot;: &quot;明确从搜索响应选择 items 原值。&quot;
          }
        ],
        &quot;op&quot;: &quot;select_part&quot;,
        &quot;input&quot;: {
          &quot;kind&quot;: &quot;input&quot;,
          &quot;index&quot;: 0
        },
        &quot;path&quot;: [
          &quot;items&quot;
        ],
        &quot;output&quot;: &quot;items&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;declared_refs&quot;: [
        {
          &quot;kind&quot;: &quot;input&quot;,
          &quot;index&quot;: 0
        }
      ],
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_2793334bb797f0fdd069&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;input_use&quot;,
      &quot;instruction_id&quot;: &quot;ir_011&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0,
        &quot;uses&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_011/events/0/events/0/atomic_ops/0/uses/0&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;input&quot;,
        &quot;index&quot;: 0
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;slot&quot;: 0,
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;input&quot;,
        &quot;index&quot;: 0
      },
      &quot;role&quot;: &quot;value&quot;,
      &quot;when&quot;: null,
      &quot;member_index&quot;: null,
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_2b0b461dad90160e07e1&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;local_output&quot;,
      &quot;instruction_id&quot;: &quot;ir_011&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0,
        &quot;output&quot;
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_011/events/0/events/0/atomic_ops/0/output&quot;,
      &quot;value&quot;: &quot;items&quot;,
      &quot;available_locals&quot;: [
        &quot;items&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;items&quot;
      },
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_2479f9ec6439ed10a8eb&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;output_binding&quot;,
      &quot;instruction_id&quot;: &quot;ir_011&quot;,
      &quot;raw_path&quot;: [
        &quot;output_bindings&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_011/output_bindings/0&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;items&quot;
      },
      &quot;available_locals&quot;: [
        &quot;items&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;output_index&quot;: 0,
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;items&quot;
      },
      &quot;scope_path&quot;: null
    }
  }
}</pre></details>
