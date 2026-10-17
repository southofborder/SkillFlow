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
    &quot;R007&quot;: &quot;bound&quot;
  },
  &quot;sinks&quot;: 6,
  &quot;expected_sinks&quot;: 6,
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
    &quot;ir_010&quot;: &quot;processed&quot;
  }
}</pre>

## Task preservation goals

A required action does not exempt all of its current payload.

<a id="goal-dd31ffb1f533a2fabe0b"></a>

### G001

Use the user\-supplied events\.json as the event source; its listed fields describe the input, not permission to disclose them all\.

<pre>{
  &quot;id&quot;: &quot;G001&quot;,
  &quot;requirement_id&quot;: &quot;R001&quot;,
  &quot;target_id&quot;: &quot;target_6afff9c218ebc2a39759&quot;,
  &quot;property&quot;: &quot;constraint&quot;,
  &quot;path&quot;: [],
  &quot;expected&quot;: null,
  &quot;expected_path&quot;: [],
  &quot;reason&quot;: &quot;Keep the stated file origin; this does not demand every file field at each receiver.&quot;
}</pre>

<details><summary>Existing Task evidence and binding</summary><pre>{
  &quot;id&quot;: &quot;R001&quot;,
  &quot;text&quot;: &quot;Use the user-supplied events.json as the event source; its listed fields describe the input, not permission to disclose them all.&quot;,
  &quot;evidences&quot;: [
    {
      &quot;file&quot;: &quot;skill/SKILL.md&quot;,
      &quot;start_line&quot;: 8,
      &quot;end_line&quot;: 8,
      &quot;reason&quot;: &quot;The instruction identifies the source file and its record fields.&quot;
    }
  ],
  &quot;bindings&quot;: [
    {
      &quot;target_id&quot;: &quot;target_6afff9c218ebc2a39759&quot;,
      &quot;reason&quot;: &quot;This is the specified file source, not a claim that all its fields are required at every boundary.&quot;
    }
  ]
}</pre></details>

<a id="goal-b4b3d2c42b6f00cdb0ba"></a>

### G002

Select a record only if opted\_out is not true and either urgent is true or value is at least 100; urgency does not override opted\_out\.

<pre>{
  &quot;id&quot;: &quot;G002&quot;,
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;target_id&quot;: &quot;target_0c1491125c133aecbdd7&quot;,
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;expected&quot;: null,
  &quot;expected_path&quot;: [],
  &quot;reason&quot;: &quot;Preserve which members satisfy the subscription and urgency/value condition; member content is demanded separately.&quot;
}</pre>

<details><summary>Existing Task evidence and binding</summary><pre>{
  &quot;id&quot;: &quot;R002&quot;,
  &quot;text&quot;: &quot;Select a record only if opted_out is not true and either urgent is true or value is at least 100; urgency does not override opted_out.&quot;,
  &quot;evidences&quot;: [
    {
      &quot;file&quot;: &quot;skill/SKILL.md&quot;,
      &quot;start_line&quot;: 9,
      &quot;end_line&quot;: 10,
      &quot;reason&quot;: &quot;The selection condition and the explicit limitation on the urgency exception must be retained together.&quot;
    }
  ],
  &quot;bindings&quot;: [
    {
      &quot;target_id&quot;: &quot;target_81ff9a19868074649a51&quot;,
      &quot;reason&quot;: &quot;This constraint records the selection predicate.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_80cda75cb9ace38b3d87&quot;,
      &quot;reason&quot;: &quot;This constraint preserves the non-overridable subscription restriction.&quot;
    }
  ]
}</pre></details>

<a id="goal-a5b641574ba521ba97b3"></a>

### G003

Call notify\.send once for each selected record, and never for an unselected record\.

<pre>{
  &quot;id&quot;: &quot;G003&quot;,
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;target_id&quot;: &quot;target_8e519da0aef569df923b&quot;,
  &quot;property&quot;: &quot;constraint&quot;,
  &quot;path&quot;: [],
  &quot;expected&quot;: null,
  &quot;expected_path&quot;: [],
  &quot;reason&quot;: &quot;Preserve once-per-selected-element scope and the exclusion of unselected members.&quot;
}</pre>

<details><summary>Existing Task evidence and binding</summary><pre>{
  &quot;id&quot;: &quot;R003&quot;,
  &quot;text&quot;: &quot;Call notify.send once for each selected record, and never for an unselected record.&quot;,
  &quot;evidences&quot;: [
    {
      &quot;file&quot;: &quot;skill/SKILL.md&quot;,
      &quot;start_line&quot;: 11,
      &quot;end_line&quot;: 11,
      &quot;reason&quot;: &quot;The call is quantified over selected records and has per-record multiplicity one.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/SKILL.md&quot;,
      &quot;start_line&quot;: 13,
      &quot;end_line&quot;: 13,
      &quot;reason&quot;: &quot;Unselected records must not cause a notification call.&quot;
    }
  ],
  &quot;bindings&quot;: [
    {
      &quot;target_id&quot;: &quot;target_8e519da0aef569df923b&quot;,
      &quot;reason&quot;: &quot;The current graph records the per-record scope here; this does not certify all call arguments as necessary.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_aeb48f99c87b5433380d&quot;,
      &quot;reason&quot;: &quot;The call constraint retains the once-per-selected-record requirement.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_8fe35635386dff487a10&quot;,
      &quot;reason&quot;: &quot;This excludes notifications for unselected records.&quot;
    }
  ]
}</pre></details>

<a id="goal-ee29196b43aae6ee7ca2"></a>

### G004

Call notify\.send once for each selected record, and never for an unselected record\.

<pre>{
  &quot;id&quot;: &quot;G004&quot;,
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;target_id&quot;: &quot;target_aeb48f99c87b5433380d&quot;,
  &quot;property&quot;: &quot;constraint&quot;,
  &quot;path&quot;: [],
  &quot;expected&quot;: null,
  &quot;expected_path&quot;: [],
  &quot;reason&quot;: &quot;Preserve once-per-selected-element scope and the exclusion of unselected members.&quot;
}</pre>

<details><summary>Existing Task evidence and binding</summary><pre>{
  &quot;id&quot;: &quot;R003&quot;,
  &quot;text&quot;: &quot;Call notify.send once for each selected record, and never for an unselected record.&quot;,
  &quot;evidences&quot;: [
    {
      &quot;file&quot;: &quot;skill/SKILL.md&quot;,
      &quot;start_line&quot;: 11,
      &quot;end_line&quot;: 11,
      &quot;reason&quot;: &quot;The call is quantified over selected records and has per-record multiplicity one.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/SKILL.md&quot;,
      &quot;start_line&quot;: 13,
      &quot;end_line&quot;: 13,
      &quot;reason&quot;: &quot;Unselected records must not cause a notification call.&quot;
    }
  ],
  &quot;bindings&quot;: [
    {
      &quot;target_id&quot;: &quot;target_8e519da0aef569df923b&quot;,
      &quot;reason&quot;: &quot;The current graph records the per-record scope here; this does not certify all call arguments as necessary.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_aeb48f99c87b5433380d&quot;,
      &quot;reason&quot;: &quot;The call constraint retains the once-per-selected-record requirement.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_8fe35635386dff487a10&quot;,
      &quot;reason&quot;: &quot;This excludes notifications for unselected records.&quot;
    }
  ]
}</pre></details>

<a id="goal-24b13b18dd5591e8a48f"></a>

### G005

Call notify\.send once for each selected record, and never for an unselected record\.

<pre>{
  &quot;id&quot;: &quot;G005&quot;,
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;target_id&quot;: &quot;target_8fe35635386dff487a10&quot;,
  &quot;property&quot;: &quot;constraint&quot;,
  &quot;path&quot;: [],
  &quot;expected&quot;: null,
  &quot;expected_path&quot;: [],
  &quot;reason&quot;: &quot;Preserve once-per-selected-element scope and the exclusion of unselected members.&quot;
}</pre>

<details><summary>Existing Task evidence and binding</summary><pre>{
  &quot;id&quot;: &quot;R003&quot;,
  &quot;text&quot;: &quot;Call notify.send once for each selected record, and never for an unselected record.&quot;,
  &quot;evidences&quot;: [
    {
      &quot;file&quot;: &quot;skill/SKILL.md&quot;,
      &quot;start_line&quot;: 11,
      &quot;end_line&quot;: 11,
      &quot;reason&quot;: &quot;The call is quantified over selected records and has per-record multiplicity one.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/SKILL.md&quot;,
      &quot;start_line&quot;: 13,
      &quot;end_line&quot;: 13,
      &quot;reason&quot;: &quot;Unselected records must not cause a notification call.&quot;
    }
  ],
  &quot;bindings&quot;: [
    {
      &quot;target_id&quot;: &quot;target_8e519da0aef569df923b&quot;,
      &quot;reason&quot;: &quot;The current graph records the per-record scope here; this does not certify all call arguments as necessary.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_aeb48f99c87b5433380d&quot;,
      &quot;reason&quot;: &quot;The call constraint retains the once-per-selected-record requirement.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_8fe35635386dff487a10&quot;,
      &quot;reason&quot;: &quot;This excludes notifications for unselected records.&quot;
    }
  ]
}</pre></details>

<a id="goal-2d673be02770278c0b36"></a>

### G006

Call notify\.send once for each selected record, and never for an unselected record\.

<pre>{
  &quot;id&quot;: &quot;G006&quot;,
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;target_id&quot;: &quot;demand_target_69f18d1add9cc9406637&quot;,
  &quot;property&quot;: &quot;action&quot;,
  &quot;path&quot;: [],
  &quot;expected&quot;: null,
  &quot;expected_path&quot;: [],
  &quot;reason&quot;: &quot;Keep the required per-selected-record notification, without requiring all current payload fields.&quot;
}</pre>

<details><summary>Existing Task evidence and binding</summary><pre>{
  &quot;id&quot;: &quot;R003&quot;,
  &quot;text&quot;: &quot;Call notify.send once for each selected record, and never for an unselected record.&quot;,
  &quot;evidences&quot;: [
    {
      &quot;file&quot;: &quot;skill/SKILL.md&quot;,
      &quot;start_line&quot;: 11,
      &quot;end_line&quot;: 11,
      &quot;reason&quot;: &quot;The call is quantified over selected records and has per-record multiplicity one.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/SKILL.md&quot;,
      &quot;start_line&quot;: 13,
      &quot;end_line&quot;: 13,
      &quot;reason&quot;: &quot;Unselected records must not cause a notification call.&quot;
    }
  ],
  &quot;bindings&quot;: [
    {
      &quot;target_id&quot;: &quot;target_8e519da0aef569df923b&quot;,
      &quot;reason&quot;: &quot;The current graph records the per-record scope here; this does not certify all call arguments as necessary.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_aeb48f99c87b5433380d&quot;,
      &quot;reason&quot;: &quot;The call constraint retains the once-per-selected-record requirement.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_8fe35635386dff487a10&quot;,
      &quot;reason&quot;: &quot;This excludes notifications for unselected records.&quot;
    }
  ]
}</pre></details>

<a id="goal-4b08eebd441e38772d93"></a>

### G007

For each notification, take recipient and body from the same selected record's recipient and summary fields; preserve summary unchanged\.

<pre>{
  &quot;id&quot;: &quot;G007&quot;,
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;target_id&quot;: &quot;demand_target_0a40de71bf95206e00ec&quot;,
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;expected&quot;: {
    &quot;kind&quot;: &quot;local&quot;,
    &quot;name&quot;: &quot;event_record&quot;
  },
  &quot;expected_path&quot;: [
    &quot;recipient&quot;
  ],
  &quot;reason&quot;: &quot;The argument must preserve this same element&#x27;s recipient value, not the complete element.&quot;
}</pre>

<details><summary>Existing Task evidence and binding</summary><pre>{
  &quot;id&quot;: &quot;R004&quot;,
  &quot;text&quot;: &quot;For each notification, take recipient and body from the same selected record&#x27;s recipient and summary fields; preserve summary unchanged.&quot;,
  &quot;evidences&quot;: [
    {
      &quot;file&quot;: &quot;skill/SKILL.md&quot;,
      &quot;start_line&quot;: 11,
      &quot;end_line&quot;: 12,
      &quot;reason&quot;: &quot;The recipient and body requirements refer to that same record, and explicitly require the original summary value.&quot;
    }
  ],
  &quot;bindings&quot;: [
    {
      &quot;target_id&quot;: &quot;target_d49b7dd46f8209dbe334&quot;,
      &quot;reason&quot;: &quot;The recipient field selector is retained, not the whole record as a recipient.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_77b9604eaae52b5abbc6&quot;,
      &quot;reason&quot;: &quot;The body field selector denotes summary, not the complete record.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_2a168b4a5f91acde4f8e&quot;,
      &quot;reason&quot;: &quot;This preserves original-value body semantics.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_8e519da0aef569df923b&quot;,
      &quot;reason&quot;: &quot;The shared per-record scope ties both selected fields to one element.&quot;
    }
  ]
}</pre></details>

<a id="goal-291a9e34e596971dc478"></a>

### G008

For each notification, take recipient and body from the same selected record's recipient and summary fields; preserve summary unchanged\.

<pre>{
  &quot;id&quot;: &quot;G008&quot;,
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;target_id&quot;: &quot;demand_target_23fc3eb8e8393e5aead7&quot;,
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;expected&quot;: {
    &quot;kind&quot;: &quot;local&quot;,
    &quot;name&quot;: &quot;event_record&quot;
  },
  &quot;expected_path&quot;: [
    &quot;summary&quot;
  ],
  &quot;reason&quot;: &quot;The argument must preserve this same element&#x27;s summary value, not the complete element.&quot;
}</pre>

<details><summary>Existing Task evidence and binding</summary><pre>{
  &quot;id&quot;: &quot;R004&quot;,
  &quot;text&quot;: &quot;For each notification, take recipient and body from the same selected record&#x27;s recipient and summary fields; preserve summary unchanged.&quot;,
  &quot;evidences&quot;: [
    {
      &quot;file&quot;: &quot;skill/SKILL.md&quot;,
      &quot;start_line&quot;: 11,
      &quot;end_line&quot;: 12,
      &quot;reason&quot;: &quot;The recipient and body requirements refer to that same record, and explicitly require the original summary value.&quot;
    }
  ],
  &quot;bindings&quot;: [
    {
      &quot;target_id&quot;: &quot;target_d49b7dd46f8209dbe334&quot;,
      &quot;reason&quot;: &quot;The recipient field selector is retained, not the whole record as a recipient.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_77b9604eaae52b5abbc6&quot;,
      &quot;reason&quot;: &quot;The body field selector denotes summary, not the complete record.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_2a168b4a5f91acde4f8e&quot;,
      &quot;reason&quot;: &quot;This preserves original-value body semantics.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_8e519da0aef569df923b&quot;,
      &quot;reason&quot;: &quot;The shared per-record scope ties both selected fields to one element.&quot;
    }
  ]
}</pre></details>

<a id="goal-53390a422ba1a1ffae9b"></a>

### G009

Do not send access\_token to any recipient anywhere in this workflow\.

<pre>{
  &quot;id&quot;: &quot;G009&quot;,
  &quot;requirement_id&quot;: &quot;R005&quot;,
  &quot;target_id&quot;: &quot;target_74256b1796dc113828cc&quot;,
  &quot;property&quot;: &quot;prohibit&quot;,
  &quot;path&quot;: [],
  &quot;expected&quot;: null,
  &quot;expected_path&quot;: [],
  &quot;reason&quot;: &quot;Retain the workflow-wide access_token prohibition without creating an input demand.&quot;
}</pre>

<details><summary>Existing Task evidence and binding</summary><pre>{
  &quot;id&quot;: &quot;R005&quot;,
  &quot;text&quot;: &quot;Do not send access_token to any recipient anywhere in this workflow.&quot;,
  &quot;evidences&quot;: [
    {
      &quot;file&quot;: &quot;skill/SKILL.md&quot;,
      &quot;start_line&quot;: 14,
      &quot;end_line&quot;: 14,
      &quot;reason&quot;: &quot;This is a workflow-wide prohibition; it is not a demand to create or preserve a prohibited send.&quot;
    }
  ],
  &quot;bindings&quot;: [
    {
      &quot;target_id&quot;: &quot;target_74256b1796dc113828cc&quot;,
      &quot;reason&quot;: &quot;The global restriction applies even when the current graph contains no violating operation.&quot;
    }
  ]
}</pre></details>

<a id="goal-ca4a3f6911afb92edb12"></a>

### G010

Field retrieval must not introduce summary generation, content rewriting, or extra format conversion\.

<pre>{
  &quot;id&quot;: &quot;G010&quot;,
  &quot;requirement_id&quot;: &quot;R006&quot;,
  &quot;target_id&quot;: &quot;target_6624934ada448fce25c5&quot;,
  &quot;property&quot;: &quot;constraint&quot;,
  &quot;path&quot;: [],
  &quot;expected&quot;: null,
  &quot;expected_path&quot;: [],
  &quot;reason&quot;: &quot;Preserve original-field retrieval rather than inventing summarization or conversion.&quot;
}</pre>

<details><summary>Existing Task evidence and binding</summary><pre>{
  &quot;id&quot;: &quot;R006&quot;,
  &quot;text&quot;: &quot;Field retrieval must not introduce summary generation, content rewriting, or extra format conversion.&quot;,
  &quot;evidences&quot;: [
    {
      &quot;file&quot;: &quot;skill/SKILL.md&quot;,
      &quot;start_line&quot;: 15,
      &quot;end_line&quot;: 15,
      &quot;reason&quot;: &quot;The source distinguishes original field retrieval from new content processing.&quot;
    }
  ],
  &quot;bindings&quot;: [
    {
      &quot;target_id&quot;: &quot;target_6624934ada448fce25c5&quot;,
      &quot;reason&quot;: &quot;This constrains field-value handling rather than adding a transformation operation.&quot;
    }
  ]
}</pre></details>

<a id="goal-12ff945ce0aeacac1892"></a>

### G011

After processing, write the processed\-record count to local count\.txt without treating extra record content as a required file payload\.

<pre>{
  &quot;id&quot;: &quot;G011&quot;,
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;target_id&quot;: &quot;demand_target_b715f7a9008aba5e4b20&quot;,
  &quot;property&quot;: &quot;action&quot;,
  &quot;path&quot;: [],
  &quot;expected&quot;: null,
  &quot;expected_path&quot;: [],
  &quot;reason&quot;: &quot;Keep the final count-file write.&quot;
}</pre>

<details><summary>Existing Task evidence and binding</summary><pre>{
  &quot;id&quot;: &quot;R007&quot;,
  &quot;text&quot;: &quot;After processing, write the processed-record count to local count.txt without treating extra record content as a required file payload.&quot;,
  &quot;evidences&quot;: [
    {
      &quot;file&quot;: &quot;skill/SKILL.md&quot;,
      &quot;start_line&quot;: 16,
      &quot;end_line&quot;: 16,
      &quot;reason&quot;: &quot;The specified final side effect is saving the processed count.&quot;
    }
  ],
  &quot;bindings&quot;: [
    {
      &quot;target_id&quot;: &quot;target_0338c293f4218e102429&quot;,
      &quot;reason&quot;: &quot;This is the count result used by the implementation; the binding does not itself prove the counting interpretation.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_97b4dc7a239bae8e8e2a&quot;,
      &quot;reason&quot;: &quot;This is the value written to the file.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_fe0a60eb7dc3da061231&quot;,
      &quot;reason&quot;: &quot;This identifies the required local destination.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_e08b75a2cb7a3d042567&quot;,
      &quot;reason&quot;: &quot;The file write is required after processing.&quot;
    }
  ]
}</pre></details>

<a id="goal-4682439fc6236c2c33e8"></a>

### G012

After processing, write the processed\-record count to local count\.txt without treating extra record content as a required file payload\.

<pre>{
  &quot;id&quot;: &quot;G012&quot;,
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;target_id&quot;: &quot;demand_target_1e6198f794b8c0f3080c&quot;,
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;expected&quot;: {
    &quot;kind&quot;: &quot;input&quot;,
    &quot;index&quot;: 1
  },
  &quot;expected_path&quot;: [],
  &quot;reason&quot;: &quot;Preserve the processed-count value passed to the file.&quot;
}</pre>

<details><summary>Existing Task evidence and binding</summary><pre>{
  &quot;id&quot;: &quot;R007&quot;,
  &quot;text&quot;: &quot;After processing, write the processed-record count to local count.txt without treating extra record content as a required file payload.&quot;,
  &quot;evidences&quot;: [
    {
      &quot;file&quot;: &quot;skill/SKILL.md&quot;,
      &quot;start_line&quot;: 16,
      &quot;end_line&quot;: 16,
      &quot;reason&quot;: &quot;The specified final side effect is saving the processed count.&quot;
    }
  ],
  &quot;bindings&quot;: [
    {
      &quot;target_id&quot;: &quot;target_0338c293f4218e102429&quot;,
      &quot;reason&quot;: &quot;This is the count result used by the implementation; the binding does not itself prove the counting interpretation.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_97b4dc7a239bae8e8e2a&quot;,
      &quot;reason&quot;: &quot;This is the value written to the file.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_fe0a60eb7dc3da061231&quot;,
      &quot;reason&quot;: &quot;This identifies the required local destination.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_e08b75a2cb7a3d042567&quot;,
      &quot;reason&quot;: &quot;The file write is required after processing.&quot;
    }
  ]
}</pre></details>

<a id="goal-70d856f3693d402f52b2"></a>

### G013

After processing, write the processed\-record count to local count\.txt without treating extra record content as a required file payload\.

<pre>{
  &quot;id&quot;: &quot;G013&quot;,
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;target_id&quot;: &quot;target_0338c293f4218e102429&quot;,
  &quot;property&quot;: &quot;constraint&quot;,
  &quot;path&quot;: [],
  &quot;expected&quot;: null,
  &quot;expected_path&quot;: [],
  &quot;reason&quot;: &quot;Keep after-processing order. The current processed-count computation remains conservative; collection cardinality is not substituted.&quot;
}</pre>

<details><summary>Existing Task evidence and binding</summary><pre>{
  &quot;id&quot;: &quot;R007&quot;,
  &quot;text&quot;: &quot;After processing, write the processed-record count to local count.txt without treating extra record content as a required file payload.&quot;,
  &quot;evidences&quot;: [
    {
      &quot;file&quot;: &quot;skill/SKILL.md&quot;,
      &quot;start_line&quot;: 16,
      &quot;end_line&quot;: 16,
      &quot;reason&quot;: &quot;The specified final side effect is saving the processed count.&quot;
    }
  ],
  &quot;bindings&quot;: [
    {
      &quot;target_id&quot;: &quot;target_0338c293f4218e102429&quot;,
      &quot;reason&quot;: &quot;This is the count result used by the implementation; the binding does not itself prove the counting interpretation.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_97b4dc7a239bae8e8e2a&quot;,
      &quot;reason&quot;: &quot;This is the value written to the file.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_fe0a60eb7dc3da061231&quot;,
      &quot;reason&quot;: &quot;This identifies the required local destination.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_e08b75a2cb7a3d042567&quot;,
      &quot;reason&quot;: &quot;The file write is required after processing.&quot;
    }
  ]
}</pre></details>

<a id="goal-3fc4dee2a249e8085f2e"></a>

### G014

After processing, write the processed\-record count to local count\.txt without treating extra record content as a required file payload\.

<pre>{
  &quot;id&quot;: &quot;G014&quot;,
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;target_id&quot;: &quot;target_97b4dc7a239bae8e8e2a&quot;,
  &quot;property&quot;: &quot;constraint&quot;,
  &quot;path&quot;: [],
  &quot;expected&quot;: null,
  &quot;expected_path&quot;: [],
  &quot;reason&quot;: &quot;Keep after-processing order. The current processed-count computation remains conservative; collection cardinality is not substituted.&quot;
}</pre>

<details><summary>Existing Task evidence and binding</summary><pre>{
  &quot;id&quot;: &quot;R007&quot;,
  &quot;text&quot;: &quot;After processing, write the processed-record count to local count.txt without treating extra record content as a required file payload.&quot;,
  &quot;evidences&quot;: [
    {
      &quot;file&quot;: &quot;skill/SKILL.md&quot;,
      &quot;start_line&quot;: 16,
      &quot;end_line&quot;: 16,
      &quot;reason&quot;: &quot;The specified final side effect is saving the processed count.&quot;
    }
  ],
  &quot;bindings&quot;: [
    {
      &quot;target_id&quot;: &quot;target_0338c293f4218e102429&quot;,
      &quot;reason&quot;: &quot;This is the count result used by the implementation; the binding does not itself prove the counting interpretation.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_97b4dc7a239bae8e8e2a&quot;,
      &quot;reason&quot;: &quot;This is the value written to the file.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_fe0a60eb7dc3da061231&quot;,
      &quot;reason&quot;: &quot;This identifies the required local destination.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_e08b75a2cb7a3d042567&quot;,
      &quot;reason&quot;: &quot;The file write is required after processing.&quot;
    }
  ]
}</pre></details>

<a id="goal-9bcb9fbceed0f8cda0a5"></a>

### G015

After processing, write the processed\-record count to local count\.txt without treating extra record content as a required file payload\.

<pre>{
  &quot;id&quot;: &quot;G015&quot;,
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;target_id&quot;: &quot;target_fe0a60eb7dc3da061231&quot;,
  &quot;property&quot;: &quot;constraint&quot;,
  &quot;path&quot;: [],
  &quot;expected&quot;: null,
  &quot;expected_path&quot;: [],
  &quot;reason&quot;: &quot;Keep after-processing order. The current processed-count computation remains conservative; collection cardinality is not substituted.&quot;
}</pre>

<details><summary>Existing Task evidence and binding</summary><pre>{
  &quot;id&quot;: &quot;R007&quot;,
  &quot;text&quot;: &quot;After processing, write the processed-record count to local count.txt without treating extra record content as a required file payload.&quot;,
  &quot;evidences&quot;: [
    {
      &quot;file&quot;: &quot;skill/SKILL.md&quot;,
      &quot;start_line&quot;: 16,
      &quot;end_line&quot;: 16,
      &quot;reason&quot;: &quot;The specified final side effect is saving the processed count.&quot;
    }
  ],
  &quot;bindings&quot;: [
    {
      &quot;target_id&quot;: &quot;target_0338c293f4218e102429&quot;,
      &quot;reason&quot;: &quot;This is the count result used by the implementation; the binding does not itself prove the counting interpretation.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_97b4dc7a239bae8e8e2a&quot;,
      &quot;reason&quot;: &quot;This is the value written to the file.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_fe0a60eb7dc3da061231&quot;,
      &quot;reason&quot;: &quot;This identifies the required local destination.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_e08b75a2cb7a3d042567&quot;,
      &quot;reason&quot;: &quot;The file write is required after processing.&quot;
    }
  ]
}</pre></details>

<a id="goal-ec92126bb6c9d4f70ec7"></a>

### G016

After processing, write the processed\-record count to local count\.txt without treating extra record content as a required file payload\.

<pre>{
  &quot;id&quot;: &quot;G016&quot;,
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;target_id&quot;: &quot;target_e08b75a2cb7a3d042567&quot;,
  &quot;property&quot;: &quot;constraint&quot;,
  &quot;path&quot;: [],
  &quot;expected&quot;: null,
  &quot;expected_path&quot;: [],
  &quot;reason&quot;: &quot;Keep after-processing order. The current processed-count computation remains conservative; collection cardinality is not substituted.&quot;
}</pre>

<details><summary>Existing Task evidence and binding</summary><pre>{
  &quot;id&quot;: &quot;R007&quot;,
  &quot;text&quot;: &quot;After processing, write the processed-record count to local count.txt without treating extra record content as a required file payload.&quot;,
  &quot;evidences&quot;: [
    {
      &quot;file&quot;: &quot;skill/SKILL.md&quot;,
      &quot;start_line&quot;: 16,
      &quot;end_line&quot;: 16,
      &quot;reason&quot;: &quot;The specified final side effect is saving the processed count.&quot;
    }
  ],
  &quot;bindings&quot;: [
    {
      &quot;target_id&quot;: &quot;target_0338c293f4218e102429&quot;,
      &quot;reason&quot;: &quot;This is the count result used by the implementation; the binding does not itself prove the counting interpretation.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_97b4dc7a239bae8e8e2a&quot;,
      &quot;reason&quot;: &quot;This is the value written to the file.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_fe0a60eb7dc3da061231&quot;,
      &quot;reason&quot;: &quot;This identifies the required local destination.&quot;
    },
    {
      &quot;target_id&quot;: &quot;target_e08b75a2cb7a3d042567&quot;,
      &quot;reason&quot;: &quot;The file write is required after processing.&quot;
    }
  ]
}</pre></details>

<a id="restrictions"></a>

## Retained task restrictions

Retained review context; not executable or verified predicates. These task restrictions remain available for review across sink comparisons. Their listing does not establish a per-sink scope or that a restriction was satisfied.

- [G001](#goal-dd31ffb1f533a2fabe0b): Use the user\-supplied events\.json as the event source; its listed fields describe the input, not permission to disclose them all\.
- [G003](#goal-a5b641574ba521ba97b3): Call notify\.send once for each selected record, and never for an unselected record\.
- [G004](#goal-ee29196b43aae6ee7ca2): Call notify\.send once for each selected record, and never for an unselected record\.
- [G005](#goal-24b13b18dd5591e8a48f): Call notify\.send once for each selected record, and never for an unselected record\.
- [G009](#goal-53390a422ba1a1ffae9b): Do not send access\_token to any recipient anywhere in this workflow\.
- [G010](#goal-ca4a3f6911afb92edb12): Field retrieval must not introduce summary generation, content rewriting, or extra format conversion\.
- [G013](#goal-70d856f3693d402f52b2): After processing, write the processed\-record count to local count\.txt without treating extra record content as a required file payload\.
- [G014](#goal-3fc4dee2a249e8085f2e): After processing, write the processed\-record count to local count\.txt without treating extra record content as a required file payload\.
- [G015](#goal-9bcb9fbceed0f8cda0a5): After processing, write the processed\-record count to local count\.txt without treating extra record content as a required file payload\.
- [G016](#goal-ec92126bb6c9d4f70ec7): After processing, write the processed\-record count to local count\.txt without treating extra record content as a required file payload\.

## Sink comparisons

Payload slots retain parameter order and candidate identity. No established demand does not automatically authorize deletion.

<a id="sink-bb22bb6b2e2e3aabc3d6"></a>

### sink\_1ea1df94c056db64d320

[Shared retained task restrictions](#restrictions)

#### Current boundary

<pre>{
  &quot;instruction_id&quot;: &quot;ir_009&quot;,
  &quot;event_index&quot;: 0,
  &quot;op_index&quot;: 0,
  &quot;body_event_index&quot;: null,
  &quot;scope&quot;: null,
  &quot;target&quot;: &quot;loc_count_file&quot;,
  &quot;sink_type&quot;: &quot;storage_write&quot;,
  &quot;exposure_level&quot;: 1
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
        &quot;data_6769758ca6855624cf5c69aaefa1f22b15fe1b67a9c38a00a96fe27dc4ccb52d&quot;
      ]
    ]
  }
]</pre>

#### Demand-driving requirements

- **R007:** After processing, write the processed\-record count to local count\.txt without treating extra record content as a required file payload\.

#### Rule-supported demand

| Task | Information to preserve | Use position | Rule and derivation |
| --- | --- | --- | --- |
| R007 | Value \(whole referenced value\) | ir\_009 / op\_input / slot 0 | task\_expected\_relation [demand\_6eb0c66d2a057f298188](#derivation-7341694021b10ef8bab0) |
| R007 | Required behavior \(whole referenced value\) | ir\_009 / action | task\_action [demand\_b8ef03f1fb7151dcb622](#derivation-aaa2c3c827a382136e7e) |

#### Conservative retention

No entries in this category.

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
        &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
      ]
    ]
  }
]</pre>

#### Demand-driving requirements

- **R007:** After processing, write the processed\-record count to local count\.txt without treating extra record content as a required file payload\.

#### Rule-supported demand

No entries in this category.

#### Conservative retention

| Task | Information to preserve | Use position | Rule and derivation |
| --- | --- | --- | --- |
| R007 | Value \(whole referenced value\) | ir\_007 / op\_input / slot 0 | processing\_boundary [demand\_73ae1d77566a9696778f](#derivation-1608f50b2898161ee53e) |

#### Payload ranges without established demand

<pre>[]</pre>

#### Analysis limitations

<pre>[]</pre>

<a id="sink-33adc6fc634107e2bdee"></a>

### sink\_80fd796a4f5ad99767c4

[Shared retained task restrictions](#restrictions)

#### Current boundary

<pre>{
  &quot;instruction_id&quot;: &quot;ir_005&quot;,
  &quot;event_index&quot;: 0,
  &quot;op_index&quot;: 0,
  &quot;body_event_index&quot;: 2,
  &quot;scope&quot;: &quot;element&quot;,
  &quot;target&quot;: &quot;loc_notify_send&quot;,
  &quot;sink_type&quot;: &quot;external_tool&quot;,
  &quot;exposure_level&quot;: 2
}</pre>

#### Actual payload

<pre>[
  {
    &quot;operation_id&quot;: &quot;op_ir_005:e0:i0:b2:a0&quot;,
    &quot;position&quot;: {
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;event_index&quot;: 0,
      &quot;op_index&quot;: 0,
      &quot;body_event_index&quot;: 2,
      &quot;instance_index&quot;: 0
    },
    &quot;inputs&quot;: [
      [
        &quot;data_d750a7672e1d781d1a363df4e89026045b6962420bcdfd2961c8d5b9b7faae3c&quot;
      ],
      [
        &quot;data_935a590ca3f5fbfda0c156dbfd2219e481254cb1f0524ebde055f393d5ff121b&quot;
      ]
    ]
  }
]</pre>

#### Demand-driving requirements

- **R003:** Call notify\.send once for each selected record, and never for an unselected record\.

- **R004:** For each notification, take recipient and body from the same selected record's recipient and summary fields; preserve summary unchanged\.

#### Rule-supported demand

| Task | Information to preserve | Use position | Rule and derivation |
| --- | --- | --- | --- |
| R003 | Required behavior \(whole referenced value\) | ir\_005 / action | task\_action [demand\_5d07d52914a0acd9d7de](#derivation-29908998883c790a0883) |
| R004 | Value \(whole referenced value\) | ir\_005 / op\_input / slot 1 | task\_expected\_relation [demand\_8b7356084bb3e33c4183](#derivation-bcff973d733d93a759cd) |
| R004 | Value \(whole referenced value\) | ir\_005 / op\_input / slot 0 | task\_expected\_relation [demand\_d3d670b4c106375103cd](#derivation-5cbcd7af41c7b5029e64) |

#### Conservative retention

No entries in this category.

#### Payload ranges without established demand

<pre>[]</pre>

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
        &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
      ]
    ]
  }
]</pre>

#### Demand-driving requirements

- **R002:** Select a record only if opted\_out is not true and either urgent is true or value is at least 100; urgency does not override opted\_out\.

- **R003:** Call notify\.send once for each selected record, and never for an unselected record\.

- **R004:** For each notification, take recipient and body from the same selected record's recipient and summary fields; preserve summary unchanged\.

- **R007:** After processing, write the processed\-record count to local count\.txt without treating extra record content as a required file payload\.

#### Rule-supported demand

| Task | Information to preserve | Use position | Rule and derivation |
| --- | --- | --- | --- |
| R004 | Per element: Value at \["value"\] | ir\_003 / op\_input / slot 0 | processing\_boundary [demand\_0c7c56f52ec25b11a333](#derivation-28e6bd69b52fea3e1957) |
| R004 | Collection structure \(whole referenced value\) | ir\_003 / op\_input / slot 0 | processing\_boundary [demand\_1366bac463dd447da88a](#derivation-d98bce1a16153326c633) |
| R004 | Per element: Value at \["summary"\] | ir\_003 / op\_input / slot 0 | processing\_boundary [demand\_1bd96fdaac15d70f48c9](#derivation-c2d8866879223701fb63) |
| R003 | Collection structure \(whole referenced value\) | ir\_003 / op\_input / slot 0 | processing\_boundary [demand\_1c672530c034ddeeefa8](#derivation-1a51c6908c3e1c0bd1ea) |
| R002 | Per element: Value at \["value"\] | ir\_003 / op\_input / slot 0 | processing\_boundary [demand\_29ef9c16813372a5f655](#derivation-321a4c046eae1719b06a) |
| R003 | Per element: Value at \["urgent"\] | ir\_003 / op\_input / slot 0 | processing\_boundary [demand\_30e20514b9363527cb3a](#derivation-face87c6ae3a7769ec7b) |
| R003 | Per element: Value at \["value"\] | ir\_003 / op\_input / slot 0 | processing\_boundary [demand\_50f14355ec3fb7bb8ff8](#derivation-a68afef52dbe992de3c3) |
| R002 | Collection structure \(whole referenced value\) | ir\_003 / op\_input / slot 0 | processing\_boundary [demand\_8462dca99d4ca8b07723](#derivation-761afd2489e149e7ed6d) |
| R004 | Per element: Value at \["opted\_out"\] | ir\_003 / op\_input / slot 0 | processing\_boundary [demand\_9fa638f125c40fef2b79](#derivation-450d259cf281bc47759a) |
| R004 | Per element: Value at \["recipient"\] | ir\_003 / op\_input / slot 0 | processing\_boundary [demand\_a908577339740ee2f130](#derivation-fd43ed4cd5a72ccbcda3) |
| R002 | Per element: Value at \["urgent"\] | ir\_003 / op\_input / slot 0 | processing\_boundary [demand\_b35f3f8b13893d360d42](#derivation-214a24fec1e12d8c3437) |
| R002 | Per element: Value at \["opted\_out"\] | ir\_003 / op\_input / slot 0 | processing\_boundary [demand\_c396c2cfbb5f5a39eade](#derivation-8bcb3a9a4e6e9fc54c8d) |
| R003 | Per element: Value at \["opted\_out"\] | ir\_003 / op\_input / slot 0 | processing\_boundary [demand\_c7e8e2b6b501ffc499ca](#derivation-01f8182df29fd703b3fd) |
| R004 | Per element: Value at \["urgent"\] | ir\_003 / op\_input / slot 0 | processing\_boundary [demand\_da0045ff330114acb758](#derivation-a3fe8076f8e84fa7629a) |

#### Conservative retention

| Task | Information to preserve | Use position | Rule and derivation |
| --- | --- | --- | --- |
| R007 | Per element: Value at \["value"\] | ir\_003 / op\_input / slot 0 | processing\_boundary [demand\_059ab1bc165474d1ff99](#derivation-1824e7bf0527cb612969) |
| R007 | Collection structure \(whole referenced value\) | ir\_003 / op\_input / slot 0 | processing\_boundary [demand\_1f40653187e1716d39d7](#derivation-b5df1a6ebc14d853f39b) |
| R007 | Per element: Value at \["urgent"\] | ir\_003 / op\_input / slot 0 | processing\_boundary [demand\_3099fd072d0faee2ef50](#derivation-7d1f5c64f89907106da0) |
| R007 | Value \(whole referenced value\) | ir\_003 / op\_input / slot 0 | processing\_boundary [demand\_919b87f1c95c3bbb4d42](#derivation-93ab9a5799383795f60b) |
| R007 | Per element: Value at \["opted\_out"\] | ir\_003 / op\_input / slot 0 | processing\_boundary [demand\_b7a508322ba53561e68f](#derivation-b2c996b2707d10b3311f) |

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
        &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
      ]
    ]
  }
]</pre>

#### Demand-driving requirements

- **R002:** Select a record only if opted\_out is not true and either urgent is true or value is at least 100; urgency does not override opted\_out\.

- **R003:** Call notify\.send once for each selected record, and never for an unselected record\.

- **R004:** For each notification, take recipient and body from the same selected record's recipient and summary fields; preserve summary unchanged\.

- **R007:** After processing, write the processed\-record count to local count\.txt without treating extra record content as a required file payload\.

#### Rule-supported demand

| Task | Information to preserve | Use position | Rule and derivation |
| --- | --- | --- | --- |
| R002 | Collection structure \(whole referenced value\) | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_01a292afbf58b7b85766](#derivation-13eefb2372cf3cddf781) |
| R004 | Per element: Value at \["urgent"\] | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_27372e1edb15e4e3c92f](#derivation-7bfe9a0bd239a1214f2c) |
| R002 | Per element: Value at \["value"\] | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_358abb5b6baa5363d96d](#derivation-0c522d8f257c46becc44) |
| R004 | Per element: Value at \["recipient"\] | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_364f6a73c03f2ceb59fb](#derivation-b9e4356c560c35f469b3) |
| R003 | Per element: Value at \["urgent"\] | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_43a662bad1475035263a](#derivation-df44c7899d9d8793ea0a) |
| R004 | Per element: Value at \["summary"\] | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_4b614f1fabb71aa26717](#derivation-3907e46b3bcd9245453f) |
| R002 | Per element: Value at \["opted\_out"\] | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_6676657d1e09f7e2894c](#derivation-7ab285713e505fa0b607) |
| R003 | Per element: Value at \["opted\_out"\] | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_73a1fd49e5a2399a3637](#derivation-6b85d455472736e9b5eb) |
| R003 | Collection structure \(whole referenced value\) | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_8c079cdc009607f05d99](#derivation-d24d816acc7cdf7f59ee) |
| R004 | Collection structure \(whole referenced value\) | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_903cad7f3e1308b673eb](#derivation-1221aeec2793ba95684f) |
| R003 | Per element: Value at \["value"\] | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_c3e90da64b405af5988a](#derivation-cab9cefd0253dfc0735a) |
| R004 | Per element: Value at \["opted\_out"\] | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_d0b6f9eb6ed97a67a649](#derivation-31ae21ee621c09b594d2) |
| R004 | Per element: Value at \["value"\] | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_d64b4865ae554f8ca5a3](#derivation-d770f459b9962c003602) |
| R002 | Per element: Value at \["urgent"\] | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_d757cfeaca3cc614e4bd](#derivation-b3fc81d0a19d31a833be) |

#### Conservative retention

| Task | Information to preserve | Use position | Rule and derivation |
| --- | --- | --- | --- |
| R007 | Per element: Value at \["urgent"\] | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_77b8c45e41b782560600](#derivation-12745743da2a07bfc972) |
| R007 | Collection structure \(whole referenced value\) | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_94f389638afdd6929deb](#derivation-343753c5f9caa25eaa53) |
| R007 | Per element: Value at \["opted\_out"\] | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_c0bb53b9be08818a39e4](#derivation-d623eecf8ac4cb9682cf) |
| R007 | Per element: Value at \["value"\] | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_c58f80e9f07632e15741](#derivation-094c137dd11573390805) |
| R007 | Value \(whole referenced value\) | ir\_001 / op\_input / slot 0 | processing\_boundary [demand\_e7bf889160dead1a78a8](#derivation-7598d00641bbcb5e3caa) |

#### Payload ranges without established demand

<pre>[]</pre>

#### Analysis limitations

<pre>[]</pre>

<a id="sink-40257311e71fba76ff29"></a>

### sink\_cb57907a38ea01745209

[Shared retained task restrictions](#restrictions)

#### Current boundary

<pre>{
  &quot;instruction_id&quot;: &quot;ir_005&quot;,
  &quot;event_index&quot;: 0,
  &quot;op_index&quot;: 0,
  &quot;body_event_index&quot;: 0,
  &quot;scope&quot;: &quot;element&quot;,
  &quot;target&quot;: &quot;__compiled_model_context__&quot;,
  &quot;sink_type&quot;: &quot;model_observe&quot;,
  &quot;exposure_level&quot;: 2
}</pre>

#### Actual payload

<pre>[
  {
    &quot;operation_id&quot;: &quot;op_ir_005:e0:i0:b0:a0&quot;,
    &quot;position&quot;: {
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;event_index&quot;: 0,
      &quot;op_index&quot;: 0,
      &quot;body_event_index&quot;: 0,
      &quot;instance_index&quot;: 0
    },
    &quot;inputs&quot;: [
      [
        &quot;data_f07850d2a4ac450f42d8f002aae56e147b860228bb2bae0a856286e974a2b15a&quot;
      ]
    ]
  }
]</pre>

#### Demand-driving requirements

- **R004:** For each notification, take recipient and body from the same selected record's recipient and summary fields; preserve summary unchanged\.

#### Rule-supported demand

| Task | Information to preserve | Use position | Rule and derivation |
| --- | --- | --- | --- |
| R004 | Value at \["recipient"\] | ir\_005 / op\_input / slot 0 | processing\_boundary [demand\_111c204981035add8197](#derivation-17eec843e689ac7a1ffe) |
| R004 | Value at \["summary"\] | ir\_005 / op\_input / slot 0 | processing\_boundary [demand\_1cfd9016597cd36806fd](#derivation-61bec645f1b9e06e61ec) |

#### Conservative retention

No entries in this category.

#### Payload ranges without established demand

<pre>[
  {
    &quot;operation_id&quot;: &quot;op_ir_005:e0:i0:b0:a0&quot;,
    &quot;input_index&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_f07850d2a4ac450f42d8f002aae56e147b860228bb2bae0a856286e974a2b15a&quot;
    ],
    &quot;description&quot;: &quot;Requirements constrain only the listed information properties. Preserve structure and all listed demands; no replacement execution was verified.&quot;,
    &quot;scope&quot;: &quot;outside_listed_properties&quot;
  }
]</pre>

#### Analysis limitations

<pre>[]</pre>

## Shared rule derivations

<a id="derivation-13eefb2372cf3cddf781"></a>

### demand\_01a292afbf58b7b85766

<pre>{
  &quot;id&quot;: &quot;demand_01a292afbf58b7b85766&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_46ca0cca9f43b8598554&quot;
  ]
}</pre>

<a id="derivation-da1c5bd8200710e3c96d"></a>

### demand\_043c1d6dc5d58ea28fbd

<pre>{
  &quot;id&quot;: &quot;demand_043c1d6dc5d58ea28fbd&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e0:i0:b1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_f07850d2a4ac450f42d8f002aae56e147b860228bb2bae0a856286e974a2b15a&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;recipient&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;selected_path&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_9090c09af6255f28d730&quot;
  ]
}</pre>

<a id="derivation-ffa436ac57ab3e99e08b"></a>

### demand\_04e604c3b7998173ec5e

<pre>{
  &quot;id&quot;: &quot;demand_04e604c3b7998173ec5e&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;urgent&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;expression_reference&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_30e44cc93f8cc55d2347&quot;,
    &quot;demand_7f965c1425c9d9705732&quot;,
    &quot;demand_9776c01245b0406fd9ec&quot;
  ]
}</pre>

<a id="derivation-1824e7bf0527cb612969"></a>

### demand\_059ab1bc165474d1ff99

<pre>{
  &quot;id&quot;: &quot;demand_059ab1bc165474d1ff99&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;value&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_a06fc3eb88dfcd742e69&quot;
  ]
}</pre>

<a id="derivation-ba900e1682571281d148"></a>

### demand\_05da24f6af252dc7da48

<pre>{
  &quot;id&quot;: &quot;demand_05da24f6af252dc7da48&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;opted_out&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_9967c98f2bdae0477123&quot;
  ]
}</pre>

<a id="derivation-b252e555a46c5be8c7cc"></a>

### demand\_061e3e697458996cbe3a

<pre>{
  &quot;id&quot;: &quot;demand_061e3e697458996cbe3a&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;iteration_shape&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_a3a14254d26d0a02be20&quot;,
    &quot;demand_e64d4850fd51019a369d&quot;
  ]
}</pre>

<a id="derivation-e4670884b99f4666e317"></a>

### demand\_06b6b8bdce4956b4c04e

<pre>{
  &quot;id&quot;: &quot;demand_06b6b8bdce4956b4c04e&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;value&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_8a7b62080b7bad75aa78&quot;
  ]
}</pre>

<a id="derivation-08b50312dccccb8223bd"></a>

### demand\_092a3fcc5e4d2f746b9f

<pre>{
  &quot;id&quot;: &quot;demand_092a3fcc5e4d2f746b9f&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;urgent&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;expression_reference&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_9d2610407f82d449ad56&quot;
  ]
}</pre>

<a id="derivation-b1a690c983f3f99c3048"></a>

### demand\_0baefa9a756a6989ee69

<pre>{
  &quot;id&quot;: &quot;demand_0baefa9a756a6989ee69&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;recipient&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_a908577339740ee2f130&quot;,
    &quot;demand_c6ebbd64ce31ddac4c11&quot;
  ]
}</pre>

<a id="derivation-28e6bd69b52fea3e1957"></a>

### demand\_0c7c56f52ec25b11a333

<pre>{
  &quot;id&quot;: &quot;demand_0c7c56f52ec25b11a333&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;value&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_7cf685f04f7e740214ce&quot;
  ]
}</pre>

<a id="derivation-89e09b9c3b868cfce5b6"></a>

### demand\_1021243d4154c09a3fd9

<pre>{
  &quot;id&quot;: &quot;demand_1021243d4154c09a3fd9&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_6769758ca6855624cf5c69aaefa1f22b15fe1b67a9c38a00a96fe27dc4ccb52d&quot;
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
    &quot;demand_5785a3eb5a00f06ad7af&quot;
  ]
}</pre>

<a id="derivation-1d61d6f80bf1953c7f0b"></a>

### demand\_10647172e6d2b392b4bd

<pre>{
  &quot;id&quot;: &quot;demand_10647172e6d2b392b4bd&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;opted_out&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;expression_reference&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_30e44cc93f8cc55d2347&quot;,
    &quot;demand_7f965c1425c9d9705732&quot;,
    &quot;demand_9776c01245b0406fd9ec&quot;
  ]
}</pre>

<a id="derivation-17eec843e689ac7a1ffe"></a>

### demand\_111c204981035add8197

<pre>{
  &quot;id&quot;: &quot;demand_111c204981035add8197&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e0:i0:b0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_f07850d2a4ac450f42d8f002aae56e147b860228bb2bae0a856286e974a2b15a&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;recipient&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_043c1d6dc5d58ea28fbd&quot;
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
      &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
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
    &quot;demand_50a2d170fa8a7f82b976&quot;
  ]
}</pre>

<a id="derivation-d98bce1a16153326c633"></a>

### demand\_1366bac463dd447da88a

<pre>{
  &quot;id&quot;: &quot;demand_1366bac463dd447da88a&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_dd054ae2664b525ce1f8&quot;
  ]
}</pre>

<a id="derivation-13390829f0f63aa73229"></a>

### demand\_13e8c089e09f92ff76e4

<pre>{
  &quot;id&quot;: &quot;demand_13e8c089e09f92ff76e4&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;urgent&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_27372e1edb15e4e3c92f&quot;,
    &quot;demand_878fc59f7b87ebb96ce3&quot;
  ]
}</pre>

<a id="derivation-bc360aa683cc67f89b02"></a>

### demand\_18b2f582fd8aba703f5e

<pre>{
  &quot;id&quot;: &quot;demand_18b2f582fd8aba703f5e&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;opted_out&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_373c8ebd2c73635cec88&quot;,
    &quot;demand_c396c2cfbb5f5a39eade&quot;
  ]
}</pre>

<a id="derivation-d91bb841f958503539ba"></a>

### demand\_1a1a2039df086feb75e7

<pre>{
  &quot;id&quot;: &quot;demand_1a1a2039df086feb75e7&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;value&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_06b6b8bdce4956b4c04e&quot;,
    &quot;demand_c58f80e9f07632e15741&quot;
  ]
}</pre>

<a id="derivation-a6cdf8214823bcf75800"></a>

### demand\_1a919acc84fdc9fb8bf8

<pre>{
  &quot;id&quot;: &quot;demand_1a919acc84fdc9fb8bf8&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
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
    &quot;demand_f99f59b0696d76f5c20a&quot;
  ]
}</pre>

<a id="derivation-c2d8866879223701fb63"></a>

### demand\_1bd96fdaac15d70f48c9

<pre>{
  &quot;id&quot;: &quot;demand_1bd96fdaac15d70f48c9&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;summary&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_d1996c9b1cbd39c43631&quot;
  ]
}</pre>

<a id="derivation-1a51c6908c3e1c0bd1ea"></a>

### demand\_1c672530c034ddeeefa8

<pre>{
  &quot;id&quot;: &quot;demand_1c672530c034ddeeefa8&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_71b7eba3d3e1762ce048&quot;
  ]
}</pre>

<a id="derivation-61bec645f1b9e06e61ec"></a>

### demand\_1cfd9016597cd36806fd

<pre>{
  &quot;id&quot;: &quot;demand_1cfd9016597cd36806fd&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e0:i0:b0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_f07850d2a4ac450f42d8f002aae56e147b860228bb2bae0a856286e974a2b15a&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;summary&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_64b5fe288659831cb4d8&quot;
  ]
}</pre>

<a id="derivation-67095dbefce1c2835e2a"></a>

### demand\_1d55302031958c282cf6

<pre>{
  &quot;id&quot;: &quot;demand_1d55302031958c282cf6&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;opted_out&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_de08bfb400886f82bd33&quot;
  ]
}</pre>

<a id="derivation-b5df1a6ebc14d853f39b"></a>

### demand\_1f40653187e1716d39d7

<pre>{
  &quot;id&quot;: &quot;demand_1f40653187e1716d39d7&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_260c669f6ebed8beaa55&quot;
  ]
}</pre>

<a id="derivation-6fa7961533892a0bdb67"></a>

### demand\_21bc3fc9bfed62b5f448

<pre>{
  &quot;id&quot;: &quot;demand_21bc3fc9bfed62b5f448&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;opted_out&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_10647172e6d2b392b4bd&quot;,
    &quot;demand_9fa638f125c40fef2b79&quot;
  ]
}</pre>

<a id="derivation-5181d6024f936da01b48"></a>

### demand\_23026a0749a42ccfe57b

<pre>{
  &quot;id&quot;: &quot;demand_23026a0749a42ccfe57b&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;opted_out&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_18b2f582fd8aba703f5e&quot;
  ]
}</pre>

<a id="derivation-8dd3f189e2da0aca0128"></a>

### demand\_239d8386c7120386c978

<pre>{
  &quot;id&quot;: &quot;demand_239d8386c7120386c978&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;opted_out&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;expression_reference&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_9d2610407f82d449ad56&quot;
  ]
}</pre>

<a id="derivation-9959bce18adafd87c414"></a>

### demand\_242a341643c68f5ceac2

<pre>{
  &quot;id&quot;: &quot;demand_242a341643c68f5ceac2&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;summary&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_36077b6ca78e4fdec562&quot;
  ]
}</pre>

<a id="derivation-5419ec76954c9043b243"></a>

### demand\_260c669f6ebed8beaa55

<pre>{
  &quot;id&quot;: &quot;demand_260c669f6ebed8beaa55&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;filter_shape&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_9d2610407f82d449ad56&quot;
  ]
}</pre>

<a id="derivation-7bfe9a0bd239a1214f2c"></a>

### demand\_27372e1edb15e4e3c92f

<pre>{
  &quot;id&quot;: &quot;demand_27372e1edb15e4e3c92f&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;urgent&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_13e8c089e09f92ff76e4&quot;
  ]
}</pre>

<a id="derivation-9f4a1a512362cac1e234"></a>

### demand\_29e9585bec9aee2023a3

<pre>{
  &quot;id&quot;: &quot;demand_29e9585bec9aee2023a3&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;task_operand&quot;
  ],
  &quot;parents&quot;: []
}</pre>

<a id="derivation-321a4c046eae1719b06a"></a>

### demand\_29ef9c16813372a5f655

<pre>{
  &quot;id&quot;: &quot;demand_29ef9c16813372a5f655&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;value&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_88a8f0a26d425c2273d3&quot;
  ]
}</pre>

<a id="derivation-b3adb6f0fb07cb125d60"></a>

### demand\_307bfcf8aede153e71ae

<pre>{
  &quot;id&quot;: &quot;demand_307bfcf8aede153e71ae&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_8462dca99d4ca8b07723&quot;,
    &quot;demand_ed3b592513774eab0266&quot;
  ]
}</pre>

<a id="derivation-7d1f5c64f89907106da0"></a>

### demand\_3099fd072d0faee2ef50

<pre>{
  &quot;id&quot;: &quot;demand_3099fd072d0faee2ef50&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;urgent&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_092a3fcc5e4d2f746b9f&quot;
  ]
}</pre>

<a id="derivation-face87c6ae3a7769ec7b"></a>

### demand\_30e20514b9363527cb3a

<pre>{
  &quot;id&quot;: &quot;demand_30e20514b9363527cb3a&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;urgent&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_ff7cc261485f7883351a&quot;
  ]
}</pre>

<a id="derivation-1bbbefdaa016b68a80c5"></a>

### demand\_30e44cc93f8cc55d2347

<pre>{
  &quot;id&quot;: &quot;demand_30e44cc93f8cc55d2347&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;summary&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_242a341643c68f5ceac2&quot;
  ]
}</pre>

<a id="derivation-9a28345d8ef87065acc5"></a>

### demand\_32c6cb4c058fcbb1ab6b

<pre>{
  &quot;id&quot;: &quot;demand_32c6cb4c058fcbb1ab6b&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;opted_out&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_05da24f6af252dc7da48&quot;,
    &quot;demand_c0bb53b9be08818a39e4&quot;
  ]
}</pre>

<a id="derivation-0c522d8f257c46becc44"></a>

### demand\_358abb5b6baa5363d96d

<pre>{
  &quot;id&quot;: &quot;demand_358abb5b6baa5363d96d&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;value&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_f2a1a0c081ce2005c1ec&quot;
  ]
}</pre>

<a id="derivation-999553e879614766dc28"></a>

### demand\_35bb7cfe36290b362f07

<pre>{
  &quot;id&quot;: &quot;demand_35bb7cfe36290b362f07&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;urgent&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_cef6cb521caaf4021173&quot;,
    &quot;demand_d757cfeaca3cc614e4bd&quot;
  ]
}</pre>

<a id="derivation-a02fe345e04511688aaf"></a>

### demand\_35e37563fe662e2af051

<pre>{
  &quot;id&quot;: &quot;demand_35e37563fe662e2af051&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_6282f3ff69aa14ea1459&quot;,
    &quot;demand_8c079cdc009607f05d99&quot;
  ]
}</pre>

<a id="derivation-ac5b24717fc7e81eab13"></a>

### demand\_36077b6ca78e4fdec562

<pre>{
  &quot;id&quot;: &quot;demand_36077b6ca78e4fdec562&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;summary&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;same_element&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_a3a14254d26d0a02be20&quot;
  ]
}</pre>

<a id="derivation-b9e4356c560c35f469b3"></a>

### demand\_364f6a73c03f2ceb59fb

<pre>{
  &quot;id&quot;: &quot;demand_364f6a73c03f2ceb59fb&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;recipient&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_ba3a240043527f7ca1b0&quot;
  ]
}</pre>

<a id="derivation-3afaf77dd66455b03443"></a>

### demand\_373c8ebd2c73635cec88

<pre>{
  &quot;id&quot;: &quot;demand_373c8ebd2c73635cec88&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;opted_out&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;expression_reference&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_94f7186121fa33e462c2&quot;
  ]
}</pre>

<a id="derivation-bc20ab5b4ff3d89cfcb3"></a>

### demand\_382806e915724845a0d7

<pre>{
  &quot;id&quot;: &quot;demand_382806e915724845a0d7&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;opted_out&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_21bc3fc9bfed62b5f448&quot;
  ]
}</pre>

<a id="derivation-9fd4fc42db0125d9d756"></a>

### demand\_3aa3ebb242a2144bec43

<pre>{
  &quot;id&quot;: &quot;demand_3aa3ebb242a2144bec43&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_1c672530c034ddeeefa8&quot;,
    &quot;demand_71b7eba3d3e1762ce048&quot;
  ]
}</pre>

<a id="derivation-844c863cffc9599a0461"></a>

### demand\_3de3e6c0c18d6540e7ed

<pre>{
  &quot;id&quot;: &quot;demand_3de3e6c0c18d6540e7ed&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;recipient&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_420f87b634aa4bef0e4e&quot;
  ]
}</pre>

<a id="derivation-8f0a3217d1f43bcfae93"></a>

### demand\_3e3ab0f028ce1166b871

<pre>{
  &quot;id&quot;: &quot;demand_3e3ab0f028ce1166b871&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;value&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_c3e90da64b405af5988a&quot;,
    &quot;demand_e3aa7249fcbf08f078b0&quot;
  ]
}</pre>

<a id="derivation-1a8a37d0ba98f118e925"></a>

### demand\_420f87b634aa4bef0e4e

<pre>{
  &quot;id&quot;: &quot;demand_420f87b634aa4bef0e4e&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;recipient&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;same_element&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_e64d4850fd51019a369d&quot;
  ]
}</pre>

<a id="derivation-df44c7899d9d8793ea0a"></a>

### demand\_43a662bad1475035263a

<pre>{
  &quot;id&quot;: &quot;demand_43a662bad1475035263a&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;urgent&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_a54cca1b5324cea72e8d&quot;
  ]
}</pre>

<a id="derivation-3a7258cdea023fd5f652"></a>

### demand\_46ca0cca9f43b8598554

<pre>{
  &quot;id&quot;: &quot;demand_46ca0cca9f43b8598554&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_01a292afbf58b7b85766&quot;,
    &quot;demand_6c3762f38b8ef6efcab3&quot;
  ]
}</pre>

<a id="derivation-3907e46b3bcd9245453f"></a>

### demand\_4b614f1fabb71aa26717

<pre>{
  &quot;id&quot;: &quot;demand_4b614f1fabb71aa26717&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;summary&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_ec9f67f60d82455e90d2&quot;
  ]
}</pre>

<a id="derivation-7b23099fd3cb1b525a67"></a>

### demand\_4e683103d846f8eecde8

<pre>{
  &quot;id&quot;: &quot;demand_4e683103d846f8eecde8&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;recipient&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_0baefa9a756a6989ee69&quot;
  ]
}</pre>

<a id="derivation-3e5fe39299ae3001e183"></a>

### demand\_4f5dfe59fb83e9d2a333

<pre>{
  &quot;id&quot;: &quot;demand_4f5dfe59fb83e9d2a333&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;summary&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_5c47d7d5bfbcbe887505&quot;
  ]
}</pre>

<a id="derivation-fd1bafa65c7303aa5196"></a>

### demand\_50a2d170fa8a7f82b976

<pre>{
  &quot;id&quot;: &quot;demand_50a2d170fa8a7f82b976&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
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
    &quot;demand_5e84bcfe3e0c4316cf23&quot;,
    &quot;demand_73ae1d77566a9696778f&quot;
  ]
}</pre>

<a id="derivation-a68afef52dbe992de3c3"></a>

### demand\_50f14355ec3fb7bb8ff8

<pre>{
  &quot;id&quot;: &quot;demand_50f14355ec3fb7bb8ff8&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;value&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_757e96d1e251a70bba78&quot;
  ]
}</pre>

<a id="derivation-045c9697acbc06c80ad7"></a>

### demand\_52b4eb6d56df6626dc17

<pre>{
  &quot;id&quot;: &quot;demand_52b4eb6d56df6626dc17&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_ed2c6a452fa449926e2b&quot;
  ]
}</pre>

<a id="derivation-97b667d2609c5734a2ba"></a>

### demand\_5785a3eb5a00f06ad7af

<pre>{
  &quot;id&quot;: &quot;demand_5785a3eb5a00f06ad7af&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_6769758ca6855624cf5c69aaefa1f22b15fe1b67a9c38a00a96fe27dc4ccb52d&quot;
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
    &quot;demand_610d1405f445971ddf07&quot;
  ]
}</pre>

<a id="derivation-479ee97144f01b79fe41"></a>

### demand\_58515b9ea192b3d5a972

<pre>{
  &quot;id&quot;: &quot;demand_58515b9ea192b3d5a972&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_903cad7f3e1308b673eb&quot;,
    &quot;demand_eabfc8aaecc440fc62f7&quot;
  ]
}</pre>

<a id="derivation-520947a8334d7f2140b5"></a>

### demand\_5c42e06bba302d9dbb67

<pre>{
  &quot;id&quot;: &quot;demand_5c42e06bba302d9dbb67&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;required_iteration&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_5d07d52914a0acd9d7de&quot;
  ]
}</pre>

<a id="derivation-73ff0afb1ba6820e1304"></a>

### demand\_5c47d7d5bfbcbe887505

<pre>{
  &quot;id&quot;: &quot;demand_5c47d7d5bfbcbe887505&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;summary&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_1bd96fdaac15d70f48c9&quot;,
    &quot;demand_d1996c9b1cbd39c43631&quot;
  ]
}</pre>

<a id="derivation-36de989b51f8e62615d6"></a>

### demand\_5cfbfa31910a4de4bf87

<pre>{
  &quot;id&quot;: &quot;demand_5cfbfa31910a4de4bf87&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;urgent&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_30e20514b9363527cb3a&quot;,
    &quot;demand_ff7cc261485f7883351a&quot;
  ]
}</pre>

<a id="derivation-29908998883c790a0883"></a>

### demand\_5d07d52914a0acd9d7de

<pre>{
  &quot;id&quot;: &quot;demand_5d07d52914a0acd9d7de&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;action&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e0:i0:b2:a0&quot;,
    &quot;slot&quot;: null,
    &quot;data_ids&quot;: []
  },
  &quot;property&quot;: &quot;action&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;task_action&quot;
  ],
  &quot;parents&quot;: []
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
      &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;opaque_computation&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_1021243d4154c09a3fd9&quot;
  ]
}</pre>

<a id="derivation-487fd10a475f719e7aff"></a>

### demand\_610d1405f445971ddf07

<pre>{
  &quot;id&quot;: &quot;demand_610d1405f445971ddf07&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_009&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_6769758ca6855624cf5c69aaefa1f22b15fe1b67a9c38a00a96fe27dc4ccb52d&quot;
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
    &quot;demand_6eb0c66d2a057f298188&quot;
  ]
}</pre>

<a id="derivation-002adcabfbec0e68f8e5"></a>

### demand\_6282f3ff69aa14ea1459

<pre>{
  &quot;id&quot;: &quot;demand_6282f3ff69aa14ea1459&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_3aa3ebb242a2144bec43&quot;
  ]
}</pre>

<a id="derivation-cb643b625104a4ed2f1a"></a>

### demand\_64b5fe288659831cb4d8

<pre>{
  &quot;id&quot;: &quot;demand_64b5fe288659831cb4d8&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e0:i0:b1:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_f07850d2a4ac450f42d8f002aae56e147b860228bb2bae0a856286e974a2b15a&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;summary&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;selected_path&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_cfccb2054950afaf5035&quot;
  ]
}</pre>

<a id="derivation-3fd54223efa28eb7aa4d"></a>

### demand\_65c75520bf658ca61651

<pre>{
  &quot;id&quot;: &quot;demand_65c75520bf658ca61651&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;opted_out&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_382806e915724845a0d7&quot;,
    &quot;demand_d0b6f9eb6ed97a67a649&quot;
  ]
}</pre>

<a id="derivation-a00c3ce99310ebbc1d1a"></a>

### demand\_662c278094c765dd45e8

<pre>{
  &quot;id&quot;: &quot;demand_662c278094c765dd45e8&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_1366bac463dd447da88a&quot;,
    &quot;demand_dd054ae2664b525ce1f8&quot;
  ]
}</pre>

<a id="derivation-7ab285713e505fa0b607"></a>

### demand\_6676657d1e09f7e2894c

<pre>{
  &quot;id&quot;: &quot;demand_6676657d1e09f7e2894c&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;opted_out&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_c9b68432b2850f0fd385&quot;
  ]
}</pre>

<a id="derivation-7569f96764dcdb98f6fe"></a>

### demand\_6c3762f38b8ef6efcab3

<pre>{
  &quot;id&quot;: &quot;demand_6c3762f38b8ef6efcab3&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_307bfcf8aede153e71ae&quot;
  ]
}</pre>

<a id="derivation-0f2b72bb22b239639406"></a>

### demand\_6d9fa38170c0a22f6067

<pre>{
  &quot;id&quot;: &quot;demand_6d9fa38170c0a22f6067&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;value&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_0c7c56f52ec25b11a333&quot;,
    &quot;demand_7cf685f04f7e740214ce&quot;
  ]
}</pre>

<a id="derivation-7341694021b10ef8bab0"></a>

### demand\_6eb0c66d2a057f298188

<pre>{
  &quot;id&quot;: &quot;demand_6eb0c66d2a057f298188&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_009&quot;,
    &quot;operation_id&quot;: &quot;op_ir_009:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_6769758ca6855624cf5c69aaefa1f22b15fe1b67a9c38a00a96fe27dc4ccb52d&quot;
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

<a id="derivation-d68f8feb74b11c46fda0"></a>

### demand\_6f1f6a8d63dad82da326

<pre>{
  &quot;id&quot;: &quot;demand_6f1f6a8d63dad82da326&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;opted_out&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;expression_reference&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_a18ba7fa69136a17b324&quot;
  ]
}</pre>

<a id="derivation-ca88eb24eed39b08e5d7"></a>

### demand\_71b7eba3d3e1762ce048

<pre>{
  &quot;id&quot;: &quot;demand_71b7eba3d3e1762ce048&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;filter_shape&quot;,
    &quot;selected_members&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_a18ba7fa69136a17b324&quot;
  ]
}</pre>

<a id="derivation-6b85d455472736e9b5eb"></a>

### demand\_73a1fd49e5a2399a3637

<pre>{
  &quot;id&quot;: &quot;demand_73a1fd49e5a2399a3637&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;opted_out&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_f9df47fea2a8f940adb6&quot;
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
      &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
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
    &quot;demand_5e84bcfe3e0c4316cf23&quot;
  ]
}</pre>

<a id="derivation-834f380b35e3cc53f808"></a>

### demand\_757e96d1e251a70bba78

<pre>{
  &quot;id&quot;: &quot;demand_757e96d1e251a70bba78&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;value&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;expression_reference&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_a18ba7fa69136a17b324&quot;
  ]
}</pre>

<a id="derivation-12745743da2a07bfc972"></a>

### demand\_77b8c45e41b782560600

<pre>{
  &quot;id&quot;: &quot;demand_77b8c45e41b782560600&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;urgent&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_bbde3c24c272989caa5d&quot;
  ]
}</pre>

<a id="derivation-593b5d7371fa7ed30403"></a>

### demand\_7c76a4a707e5b939b2c0

<pre>{
  &quot;id&quot;: &quot;demand_7c76a4a707e5b939b2c0&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;value&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_6d9fa38170c0a22f6067&quot;
  ]
}</pre>

<a id="derivation-756471cd4b1c8a3c5557"></a>

### demand\_7cf685f04f7e740214ce

<pre>{
  &quot;id&quot;: &quot;demand_7cf685f04f7e740214ce&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;value&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;expression_reference&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_30e44cc93f8cc55d2347&quot;,
    &quot;demand_7f965c1425c9d9705732&quot;,
    &quot;demand_9776c01245b0406fd9ec&quot;
  ]
}</pre>

<a id="derivation-7fa990f4877811fa6522"></a>

### demand\_7d7f9dd758c81efa9670

<pre>{
  &quot;id&quot;: &quot;demand_7d7f9dd758c81efa9670&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;value&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_7c76a4a707e5b939b2c0&quot;,
    &quot;demand_d64b4865ae554f8ca5a3&quot;
  ]
}</pre>

<a id="derivation-60d6230689dcef8b31da"></a>

### demand\_7f965c1425c9d9705732

<pre>{
  &quot;id&quot;: &quot;demand_7f965c1425c9d9705732&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_e034113837a5e7ade065&quot;
  ]
}</pre>

<a id="derivation-c5691074ce36fbead2fa"></a>

### demand\_833f31e9d8d3ae5d7275

<pre>{
  &quot;id&quot;: &quot;demand_833f31e9d8d3ae5d7275&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;urgent&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;expression_reference&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_94f7186121fa33e462c2&quot;
  ]
}</pre>

<a id="derivation-761afd2489e149e7ed6d"></a>

### demand\_8462dca99d4ca8b07723

<pre>{
  &quot;id&quot;: &quot;demand_8462dca99d4ca8b07723&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_ed3b592513774eab0266&quot;
  ]
}</pre>

<a id="derivation-56e5a5fde50a87c1492c"></a>

### demand\_878fc59f7b87ebb96ce3

<pre>{
  &quot;id&quot;: &quot;demand_878fc59f7b87ebb96ce3&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;urgent&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_f0d6d543250fa820f8ca&quot;
  ]
}</pre>

<a id="derivation-62a9377482fc774dc154"></a>

### demand\_88a8f0a26d425c2273d3

<pre>{
  &quot;id&quot;: &quot;demand_88a8f0a26d425c2273d3&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;value&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;expression_reference&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_94f7186121fa33e462c2&quot;
  ]
}</pre>

<a id="derivation-89bcaef544313f150520"></a>

### demand\_8a7b62080b7bad75aa78

<pre>{
  &quot;id&quot;: &quot;demand_8a7b62080b7bad75aa78&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;value&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_059ab1bc165474d1ff99&quot;,
    &quot;demand_a06fc3eb88dfcd742e69&quot;
  ]
}</pre>

<a id="derivation-bcff973d733d93a759cd"></a>

### demand\_8b7356084bb3e33c4183

<pre>{
  &quot;id&quot;: &quot;demand_8b7356084bb3e33c4183&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e0:i0:b2:a0&quot;,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_935a590ca3f5fbfda0c156dbfd2219e481254cb1f0524ebde055f393d5ff121b&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;task_expected_relation&quot;
  ],
  &quot;parents&quot;: []
}</pre>

<a id="derivation-d24d816acc7cdf7f59ee"></a>

### demand\_8c079cdc009607f05d99

<pre>{
  &quot;id&quot;: &quot;demand_8c079cdc009607f05d99&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_35e37563fe662e2af051&quot;
  ]
}</pre>

<a id="derivation-356392475f221a4861aa"></a>

### demand\_8e1cb50147d6ac307225

<pre>{
  &quot;id&quot;: &quot;demand_8e1cb50147d6ac307225&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;selected_members&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_9d2610407f82d449ad56&quot;
  ]
}</pre>

<a id="derivation-1221aeec2793ba95684f"></a>

### demand\_903cad7f3e1308b673eb

<pre>{
  &quot;id&quot;: &quot;demand_903cad7f3e1308b673eb&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_58515b9ea192b3d5a972&quot;
  ]
}</pre>

<a id="derivation-ef74bde656a9167361d6"></a>

### demand\_9090c09af6255f28d730

<pre>{
  &quot;id&quot;: &quot;demand_9090c09af6255f28d730&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e0:i0:b1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_d750a7672e1d781d1a363df4e89026045b6962420bcdfd2961c8d5b9b7faae3c&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_d3d670b4c106375103cd&quot;
  ]
}</pre>

<a id="derivation-32e44c5e375acbc889fc"></a>

### demand\_90f6702f56953334402d

<pre>{
  &quot;id&quot;: &quot;demand_90f6702f56953334402d&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_5c42e06bba302d9dbb67&quot;
  ]
}</pre>

<a id="derivation-93ab9a5799383795f60b"></a>

### demand\_919b87f1c95c3bbb4d42

<pre>{
  &quot;id&quot;: &quot;demand_919b87f1c95c3bbb4d42&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
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
    &quot;demand_8e1cb50147d6ac307225&quot;
  ]
}</pre>

<a id="derivation-343753c5f9caa25eaa53"></a>

### demand\_94f389638afdd6929deb

<pre>{
  &quot;id&quot;: &quot;demand_94f389638afdd6929deb&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_b50c0e0f7fdb195fa4ed&quot;
  ]
}</pre>

<a id="derivation-abf5c06679eecb99c4d1"></a>

### demand\_94f7186121fa33e462c2

<pre>{
  &quot;id&quot;: &quot;demand_94f7186121fa33e462c2&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_29e9585bec9aee2023a3&quot;
  ]
}</pre>

<a id="derivation-8d240afff310abc9e9bb"></a>

### demand\_9776c01245b0406fd9ec

<pre>{
  &quot;id&quot;: &quot;demand_9776c01245b0406fd9ec&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;recipient&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_3de3e6c0c18d6540e7ed&quot;
  ]
}</pre>

<a id="derivation-75a59b2eaa300b0ebf41"></a>

### demand\_9967c98f2bdae0477123

<pre>{
  &quot;id&quot;: &quot;demand_9967c98f2bdae0477123&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;opted_out&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_239d8386c7120386c978&quot;,
    &quot;demand_b7a508322ba53561e68f&quot;
  ]
}</pre>

<a id="derivation-a512abc28544ad9deba0"></a>

### demand\_9bb9f57319ad670cd9f8

<pre>{
  &quot;id&quot;: &quot;demand_9bb9f57319ad670cd9f8&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;urgent&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_c145d414cca67982d5df&quot;
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
      &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
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

<a id="derivation-450d259cf281bc47759a"></a>

### demand\_9fa638f125c40fef2b79

<pre>{
  &quot;id&quot;: &quot;demand_9fa638f125c40fef2b79&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;opted_out&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_10647172e6d2b392b4bd&quot;
  ]
}</pre>

<a id="derivation-f7432e5a428847dbe38c"></a>

### demand\_a06fc3eb88dfcd742e69

<pre>{
  &quot;id&quot;: &quot;demand_a06fc3eb88dfcd742e69&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;value&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;expression_reference&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_9d2610407f82d449ad56&quot;
  ]
}</pre>

<a id="derivation-310fb39d4d15ef91e144"></a>

### demand\_a18ba7fa69136a17b324

<pre>{
  &quot;id&quot;: &quot;demand_a18ba7fa69136a17b324&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_90f6702f56953334402d&quot;
  ]
}</pre>

<a id="derivation-4e7e4bcf44b3f1de27d8"></a>

### demand\_a3a14254d26d0a02be20

<pre>{
  &quot;id&quot;: &quot;demand_a3a14254d26d0a02be20&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;element&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: null,
    &quot;scope&quot;: [
      0,
      0
    ],
    &quot;collection&quot;: &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;,
    &quot;reference&quot;: {
      &quot;kind&quot;: &quot;input&quot;,
      &quot;index&quot;: 1
    },
    &quot;data_ids&quot;: [
      &quot;data_f07850d2a4ac450f42d8f002aae56e147b860228bb2bae0a856286e974a2b15a&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;summary&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;required_original_value&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_1cfd9016597cd36806fd&quot;,
    &quot;demand_64b5fe288659831cb4d8&quot;
  ]
}</pre>

<a id="derivation-bd5f37a125bf3c3cb2db"></a>

### demand\_a54cca1b5324cea72e8d

<pre>{
  &quot;id&quot;: &quot;demand_a54cca1b5324cea72e8d&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;urgent&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_43a662bad1475035263a&quot;,
    &quot;demand_f3ba83a672ebd4ade9a4&quot;
  ]
}</pre>

<a id="derivation-fd43ed4cd5a72ccbcda3"></a>

### demand\_a908577339740ee2f130

<pre>{
  &quot;id&quot;: &quot;demand_a908577339740ee2f130&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;recipient&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_c6ebbd64ce31ddac4c11&quot;
  ]
}</pre>

<a id="derivation-214a24fec1e12d8c3437"></a>

### demand\_b35f3f8b13893d360d42

<pre>{
  &quot;id&quot;: &quot;demand_b35f3f8b13893d360d42&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;urgent&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_833f31e9d8d3ae5d7275&quot;
  ]
}</pre>

<a id="derivation-48d4628297c4b1d77912"></a>

### demand\_b50c0e0f7fdb195fa4ed

<pre>{
  &quot;id&quot;: &quot;demand_b50c0e0f7fdb195fa4ed&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_52b4eb6d56df6626dc17&quot;,
    &quot;demand_94f389638afdd6929deb&quot;
  ]
}</pre>

<a id="derivation-b2c996b2707d10b3311f"></a>

### demand\_b7a508322ba53561e68f

<pre>{
  &quot;id&quot;: &quot;demand_b7a508322ba53561e68f&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;opted_out&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_239d8386c7120386c978&quot;
  ]
}</pre>

<a id="derivation-aaa2c3c827a382136e7e"></a>

### demand\_b8ef03f1fb7151dcb622

<pre>{
  &quot;id&quot;: &quot;demand_b8ef03f1fb7151dcb622&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;action&quot;,
    &quot;instruction_id&quot;: &quot;ir_009&quot;,
    &quot;operation_id&quot;: &quot;op_ir_009:e0:a0&quot;,
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

<a id="derivation-5c3ced4c071153af50a5"></a>

### demand\_ba3a240043527f7ca1b0

<pre>{
  &quot;id&quot;: &quot;demand_ba3a240043527f7ca1b0&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;recipient&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_364f6a73c03f2ceb59fb&quot;,
    &quot;demand_4e683103d846f8eecde8&quot;
  ]
}</pre>

<a id="derivation-b8099acebe82bed8d4a3"></a>

### demand\_bbde3c24c272989caa5d

<pre>{
  &quot;id&quot;: &quot;demand_bbde3c24c272989caa5d&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;urgent&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_77b8c45e41b782560600&quot;,
    &quot;demand_9bb9f57319ad670cd9f8&quot;
  ]
}</pre>

<a id="derivation-d623eecf8ac4cb9682cf"></a>

### demand\_c0bb53b9be08818a39e4

<pre>{
  &quot;id&quot;: &quot;demand_c0bb53b9be08818a39e4&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;opted_out&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_32c6cb4c058fcbb1ab6b&quot;
  ]
}</pre>

<a id="derivation-86393fca27885446b6fc"></a>

### demand\_c145d414cca67982d5df

<pre>{
  &quot;id&quot;: &quot;demand_c145d414cca67982d5df&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;urgent&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_092a3fcc5e4d2f746b9f&quot;,
    &quot;demand_3099fd072d0faee2ef50&quot;
  ]
}</pre>

<a id="derivation-8bcb3a9a4e6e9fc54c8d"></a>

### demand\_c396c2cfbb5f5a39eade

<pre>{
  &quot;id&quot;: &quot;demand_c396c2cfbb5f5a39eade&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;opted_out&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_373c8ebd2c73635cec88&quot;
  ]
}</pre>

<a id="derivation-cab9cefd0253dfc0735a"></a>

### demand\_c3e90da64b405af5988a

<pre>{
  &quot;id&quot;: &quot;demand_c3e90da64b405af5988a&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;value&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_3e3ab0f028ce1166b871&quot;
  ]
}</pre>

<a id="derivation-094c137dd11573390805"></a>

### demand\_c58f80e9f07632e15741

<pre>{
  &quot;id&quot;: &quot;demand_c58f80e9f07632e15741&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;value&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_1a1a2039df086feb75e7&quot;
  ]
}</pre>

<a id="derivation-2f3bfdf3048c637533d1"></a>

### demand\_c6ebbd64ce31ddac4c11

<pre>{
  &quot;id&quot;: &quot;demand_c6ebbd64ce31ddac4c11&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;recipient&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;selected_members&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_9776c01245b0406fd9ec&quot;
  ]
}</pre>

<a id="derivation-01f8182df29fd703b3fd"></a>

### demand\_c7e8e2b6b501ffc499ca

<pre>{
  &quot;id&quot;: &quot;demand_c7e8e2b6b501ffc499ca&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;opted_out&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_6f1f6a8d63dad82da326&quot;
  ]
}</pre>

<a id="derivation-88ad9492c1ababf867bd"></a>

### demand\_c9b68432b2850f0fd385

<pre>{
  &quot;id&quot;: &quot;demand_c9b68432b2850f0fd385&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;opted_out&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_23026a0749a42ccfe57b&quot;,
    &quot;demand_6676657d1e09f7e2894c&quot;
  ]
}</pre>

<a id="derivation-5bef4734655d20d6201a"></a>

### demand\_cef6cb521caaf4021173

<pre>{
  &quot;id&quot;: &quot;demand_cef6cb521caaf4021173&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;urgent&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_d5d43d3ddeff69914688&quot;
  ]
}</pre>

<a id="derivation-4dc1e81ebe530e7b0bef"></a>

### demand\_cfccb2054950afaf5035

<pre>{
  &quot;id&quot;: &quot;demand_cfccb2054950afaf5035&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e0:i0:b1:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_935a590ca3f5fbfda0c156dbfd2219e481254cb1f0524ebde055f393d5ff121b&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_8b7356084bb3e33c4183&quot;
  ]
}</pre>

<a id="derivation-31ae21ee621c09b594d2"></a>

### demand\_d0b6f9eb6ed97a67a649

<pre>{
  &quot;id&quot;: &quot;demand_d0b6f9eb6ed97a67a649&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;opted_out&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_65c75520bf658ca61651&quot;
  ]
}</pre>

<a id="derivation-ef7c1fd5541be1309323"></a>

### demand\_d1996c9b1cbd39c43631

<pre>{
  &quot;id&quot;: &quot;demand_d1996c9b1cbd39c43631&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;summary&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;selected_members&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_30e44cc93f8cc55d2347&quot;
  ]
}</pre>

<a id="derivation-5cbcd7af41c7b5029e64"></a>

### demand\_d3d670b4c106375103cd

<pre>{
  &quot;id&quot;: &quot;demand_d3d670b4c106375103cd&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e0:i0:b2:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_d750a7672e1d781d1a363df4e89026045b6962420bcdfd2961c8d5b9b7faae3c&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;task_expected_relation&quot;
  ],
  &quot;parents&quot;: []
}</pre>

<a id="derivation-52d237449c7fb760841b"></a>

### demand\_d46462f18838d2941e78

<pre>{
  &quot;id&quot;: &quot;demand_d46462f18838d2941e78&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;value&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_29ef9c16813372a5f655&quot;,
    &quot;demand_88a8f0a26d425c2273d3&quot;
  ]
}</pre>

<a id="derivation-deb6565c018b0d57effe"></a>

### demand\_d5d43d3ddeff69914688

<pre>{
  &quot;id&quot;: &quot;demand_d5d43d3ddeff69914688&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;urgent&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_833f31e9d8d3ae5d7275&quot;,
    &quot;demand_b35f3f8b13893d360d42&quot;
  ]
}</pre>

<a id="derivation-d770f459b9962c003602"></a>

### demand\_d64b4865ae554f8ca5a3

<pre>{
  &quot;id&quot;: &quot;demand_d64b4865ae554f8ca5a3&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;value&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_7d7f9dd758c81efa9670&quot;
  ]
}</pre>

<a id="derivation-b3fc81d0a19d31a833be"></a>

### demand\_d757cfeaca3cc614e4bd

<pre>{
  &quot;id&quot;: &quot;demand_d757cfeaca3cc614e4bd&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;urgent&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_35bb7cfe36290b362f07&quot;
  ]
}</pre>

<a id="derivation-a3fe8076f8e84fa7629a"></a>

### demand\_da0045ff330114acb758

<pre>{
  &quot;id&quot;: &quot;demand_da0045ff330114acb758&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;urgent&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_04e604c3b7998173ec5e&quot;
  ]
}</pre>

<a id="derivation-a523df49833be4a581ce"></a>

### demand\_dd054ae2664b525ce1f8

<pre>{
  &quot;id&quot;: &quot;demand_dd054ae2664b525ce1f8&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;filter_shape&quot;,
    &quot;selected_members&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_30e44cc93f8cc55d2347&quot;,
    &quot;demand_7f965c1425c9d9705732&quot;,
    &quot;demand_9776c01245b0406fd9ec&quot;
  ]
}</pre>

<a id="derivation-1d75380d5c0dc93fbc85"></a>

### demand\_de08bfb400886f82bd33

<pre>{
  &quot;id&quot;: &quot;demand_de08bfb400886f82bd33&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;opted_out&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_6f1f6a8d63dad82da326&quot;,
    &quot;demand_c7e8e2b6b501ffc499ca&quot;
  ]
}</pre>

<a id="derivation-1fb22e558590d714a17f"></a>

### demand\_e034113837a5e7ade065

<pre>{
  &quot;id&quot;: &quot;demand_e034113837a5e7ade065&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_061e3e697458996cbe3a&quot;
  ]
}</pre>

<a id="derivation-697b69422af5ebb6bbb3"></a>

### demand\_e3aa7249fcbf08f078b0

<pre>{
  &quot;id&quot;: &quot;demand_e3aa7249fcbf08f078b0&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;value&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_f5b51121e7ce4de21d30&quot;
  ]
}</pre>

<a id="derivation-918a73ff4582eaa3be0d"></a>

### demand\_e64d4850fd51019a369d

<pre>{
  &quot;id&quot;: &quot;demand_e64d4850fd51019a369d&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;element&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: null,
    &quot;scope&quot;: [
      0,
      0
    ],
    &quot;collection&quot;: &quot;data_9e5996ab7c95f20b71536b0ca3fff59f3ff766fb00445805b5b505e1618a78fc&quot;,
    &quot;reference&quot;: {
      &quot;kind&quot;: &quot;input&quot;,
      &quot;index&quot;: 1
    },
    &quot;data_ids&quot;: [
      &quot;data_f07850d2a4ac450f42d8f002aae56e147b860228bb2bae0a856286e974a2b15a&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;recipient&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;required_original_value&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_043c1d6dc5d58ea28fbd&quot;,
    &quot;demand_111c204981035add8197&quot;
  ]
}</pre>

<a id="derivation-7598d00641bbcb5e3caa"></a>

### demand\_e7bf889160dead1a78a8

<pre>{
  &quot;id&quot;: &quot;demand_e7bf889160dead1a78a8&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
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
    &quot;demand_efcaee57015937045047&quot;
  ]
}</pre>

<a id="derivation-8cf92f4e38d90edf4c2d"></a>

### demand\_eabfc8aaecc440fc62f7

<pre>{
  &quot;id&quot;: &quot;demand_eabfc8aaecc440fc62f7&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_662c278094c765dd45e8&quot;
  ]
}</pre>

<a id="derivation-f261cfc7e770148f0905"></a>

### demand\_ec9f67f60d82455e90d2

<pre>{
  &quot;id&quot;: &quot;demand_ec9f67f60d82455e90d2&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;summary&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_4b614f1fabb71aa26717&quot;,
    &quot;demand_4f5dfe59fb83e9d2a333&quot;
  ]
}</pre>

<a id="derivation-c8818fca885d2d76b6d9"></a>

### demand\_ed2c6a452fa449926e2b

<pre>{
  &quot;id&quot;: &quot;demand_ed2c6a452fa449926e2b&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_1f40653187e1716d39d7&quot;,
    &quot;demand_260c669f6ebed8beaa55&quot;
  ]
}</pre>

<a id="derivation-d87a1bb9fb9611ca234f"></a>

### demand\_ed3b592513774eab0266

<pre>{
  &quot;id&quot;: &quot;demand_ed3b592513774eab0266&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;shape&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;filter_shape&quot;,
    &quot;selected_members&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_94f7186121fa33e462c2&quot;
  ]
}</pre>

<a id="derivation-b9e9874852bc6573e79a"></a>

### demand\_ee235cc2da4d47e8527c

<pre>{
  &quot;id&quot;: &quot;demand_ee235cc2da4d47e8527c&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;value&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_d46462f18838d2941e78&quot;
  ]
}</pre>

<a id="derivation-47c545227b21f149c30d"></a>

### demand\_efcaee57015937045047

<pre>{
  &quot;id&quot;: &quot;demand_efcaee57015937045047&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R007&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_1a919acc84fdc9fb8bf8&quot;,
    &quot;demand_e7bf889160dead1a78a8&quot;
  ]
}</pre>

<a id="derivation-b8fc2261d353ab8ddefa"></a>

### demand\_f0d6d543250fa820f8ca

<pre>{
  &quot;id&quot;: &quot;demand_f0d6d543250fa820f8ca&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;urgent&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R004&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_04e604c3b7998173ec5e&quot;,
    &quot;demand_da0045ff330114acb758&quot;
  ]
}</pre>

<a id="derivation-873579f0f39f09a5e48b"></a>

### demand\_f2a1a0c081ce2005c1ec

<pre>{
  &quot;id&quot;: &quot;demand_f2a1a0c081ce2005c1ec&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;value&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R002&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_358abb5b6baa5363d96d&quot;,
    &quot;demand_ee235cc2da4d47e8527c&quot;
  ]
}</pre>

<a id="derivation-76ba79bf0fc9896a4792"></a>

### demand\_f3ba83a672ebd4ade9a4

<pre>{
  &quot;id&quot;: &quot;demand_f3ba83a672ebd4ade9a4&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;urgent&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_5cfbfa31910a4de4bf87&quot;
  ]
}</pre>

<a id="derivation-3a5e0501e576462876a3"></a>

### demand\_f5b51121e7ce4de21d30

<pre>{
  &quot;id&quot;: &quot;demand_f5b51121e7ce4de21d30&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;value&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_50f14355ec3fb7bb8ff8&quot;,
    &quot;demand_757e96d1e251a70bba78&quot;
  ]
}</pre>

<a id="derivation-e1b92773d4d030cf25c7"></a>

### demand\_f99f59b0696d76f5c20a

<pre>{
  &quot;id&quot;: &quot;demand_f99f59b0696d76f5c20a&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
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
    &quot;demand_8e1cb50147d6ac307225&quot;,
    &quot;demand_919b87f1c95c3bbb4d42&quot;
  ]
}</pre>

<a id="derivation-3ab6cb30e779368da4a8"></a>

### demand\_f9df47fea2a8f940adb6

<pre>{
  &quot;id&quot;: &quot;demand_f9df47fea2a8f940adb6&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;opted_out&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_1d55302031958c282cf6&quot;,
    &quot;demand_73a1fd49e5a2399a3637&quot;
  ]
}</pre>

<a id="derivation-23cfcb5c1664f52b131d"></a>

### demand\_ff7cc261485f7883351a

<pre>{
  &quot;id&quot;: &quot;demand_ff7cc261485f7883351a&quot;,
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_7a785ac52903487cdfdfb48206d7809b94babde158da5ebfd616428ce762bac7&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;urgent&quot;
  ],
  &quot;each&quot;: true,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R003&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;expression_reference&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_a18ba7fa69136a17b324&quot;
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
          &quot;整份流程禁止将 access_token 字段发送给任何接收对象。&quot;,
          &quot;字段取值要求不包含摘要生成、内容改写或额外格式转换。&quot;
        ],
        &quot;blocks&quot;: {
          &quot;block_001&quot;: {
            &quot;block_id&quot;: &quot;block_001&quot;,
            &quot;block_name&quot;: &quot;读取用户提供的 events.json&quot;,
            &quot;instructions&quot;: [
              {
                &quot;id&quot;: &quot;ir_001&quot;,
                &quot;opcode&quot;: &quot;read_file&quot;,
                &quot;inputs&quot;: [
                  {
                    &quot;type&quot;: &quot;external_resource&quot;,
                    &quot;identifier&quot;: &quot;用户提供的 events.json&quot;,
                    &quot;semantic_name&quot;: &quot;用户提供的 events.json&quot;
                  }
                ],
                &quot;outputs&quot;: [
                  {
                    &quot;type&quot;: &quot;result&quot;,
                    &quot;identifier&quot;: &quot;result_001&quot;,
                    &quot;semantic_name&quot;: &quot;event_records&quot;
                  }
                ],
                &quot;constraints&quot;: [],
                &quot;metadata&quot;: {},
                &quot;draft_instruction_id&quot;: &quot;read_events_file&quot;
              },
              {
                &quot;id&quot;: &quot;ir_002&quot;,
                &quot;opcode&quot;: &quot;dispatch&quot;,
                &quot;inputs&quot;: [],
                &quot;outputs&quot;: [],
                &quot;constraints&quot;: [],
                &quot;metadata&quot;: {},
                &quot;draft_instruction_id&quot;: &quot;go_select&quot;
              }
            ],
            &quot;constraints&quot;: [
              &quot;读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。&quot;
            ],
            &quot;data_source_kind&quot;: &quot;external&quot;
          },
          &quot;block_002&quot;: {
            &quot;block_id&quot;: &quot;block_002&quot;,
            &quot;block_name&quot;: &quot;根据 opted_out、urgent 和 value 条件选中记录&quot;,
            &quot;instructions&quot;: [
              {
                &quot;id&quot;: &quot;ir_003&quot;,
                &quot;opcode&quot;: &quot;select_notifiable_events&quot;,
                &quot;inputs&quot;: [
                  {
                    &quot;type&quot;: &quot;result&quot;,
                    &quot;identifier&quot;: &quot;result_001&quot;,
                    &quot;semantic_name&quot;: &quot;event_records&quot;
                  }
                ],
                &quot;outputs&quot;: [
                  {
                    &quot;type&quot;: &quot;result&quot;,
                    &quot;identifier&quot;: &quot;result_002&quot;,
                    &quot;semantic_name&quot;: &quot;selected_records&quot;
                  }
                ],
                &quot;constraints&quot;: [
                  &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;,
                  &quot;urgent 为 true 只豁免数值门槛，不豁免 opted_out 的限制。&quot;
                ],
                &quot;metadata&quot;: {},
                &quot;draft_instruction_id&quot;: &quot;select_notifiable&quot;
              },
              {
                &quot;id&quot;: &quot;ir_004&quot;,
                &quot;opcode&quot;: &quot;dispatch&quot;,
                &quot;inputs&quot;: [],
                &quot;outputs&quot;: [],
                &quot;constraints&quot;: [],
                &quot;metadata&quot;: {},
                &quot;draft_instruction_id&quot;: &quot;go_send&quot;
              }
            ],
            &quot;constraints&quot;: [],
            &quot;data_source_kind&quot;: null
          },
          &quot;block_003&quot;: {
            &quot;block_id&quot;: &quot;block_003&quot;,
            &quot;block_name&quot;: &quot;对每条选中记录调用 notify.send&quot;,
            &quot;instructions&quot;: [
              {
                &quot;id&quot;: &quot;ir_005&quot;,
                &quot;opcode&quot;: &quot;notify.send&quot;,
                &quot;inputs&quot;: [
                  {
                    &quot;type&quot;: &quot;external_resource&quot;,
                    &quot;identifier&quot;: &quot;notify.send&quot;,
                    &quot;semantic_name&quot;: &quot;notify.send&quot;
                  },
                  {
                    &quot;type&quot;: &quot;result&quot;,
                    &quot;identifier&quot;: &quot;result_002&quot;,
                    &quot;semantic_name&quot;: &quot;selected_records&quot;
                  },
                  {
                    &quot;type&quot;: &quot;literal&quot;,
                    &quot;identifier&quot;: null,
                    &quot;literal_value&quot;: &quot;recipient&quot;
                  },
                  {
                    &quot;type&quot;: &quot;literal&quot;,
                    &quot;identifier&quot;: null,
                    &quot;literal_value&quot;: &quot;summary&quot;
                  }
                ],
                &quot;outputs&quot;: [],
                &quot;constraints&quot;: [
                  &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
                  &quot;notify.send 的 body 参数直接取该记录的 summary 字段原值。&quot;,
                  &quot;未选中的记录不调用 notify.send。&quot;
                ],
                &quot;metadata&quot;: {
                  &quot;per_record&quot;: true,
                  &quot;recipient_field&quot;: &quot;recipient&quot;,
                  &quot;body_field&quot;: &quot;summary&quot;
                },
                &quot;draft_instruction_id&quot;: &quot;send_notify&quot;
              },
              {
                &quot;id&quot;: &quot;ir_006&quot;,
                &quot;opcode&quot;: &quot;dispatch&quot;,
                &quot;inputs&quot;: [],
                &quot;outputs&quot;: [],
                &quot;constraints&quot;: [],
                &quot;metadata&quot;: {},
                &quot;draft_instruction_id&quot;: &quot;go_count&quot;
              }
            ],
            &quot;constraints&quot;: [],
            &quot;data_source_kind&quot;: null
          },
          &quot;block_004&quot;: {
            &quot;block_id&quot;: &quot;block_004&quot;,
            &quot;block_name&quot;: &quot;统计已处理条数&quot;,
            &quot;instructions&quot;: [
              {
                &quot;id&quot;: &quot;ir_007&quot;,
                &quot;opcode&quot;: &quot;count_processed_records&quot;,
                &quot;inputs&quot;: [
                  {
                    &quot;type&quot;: &quot;result&quot;,
                    &quot;identifier&quot;: &quot;result_002&quot;,
                    &quot;semantic_name&quot;: &quot;selected_records&quot;
                  }
                ],
                &quot;outputs&quot;: [
                  {
                    &quot;type&quot;: &quot;result&quot;,
                    &quot;identifier&quot;: &quot;result_003&quot;,
                    &quot;semantic_name&quot;: &quot;processed_count&quot;
                  }
                ],
                &quot;constraints&quot;: [],
                &quot;metadata&quot;: {},
                &quot;draft_instruction_id&quot;: &quot;count_processed_records&quot;
              },
              {
                &quot;id&quot;: &quot;ir_008&quot;,
                &quot;opcode&quot;: &quot;dispatch&quot;,
                &quot;inputs&quot;: [],
                &quot;outputs&quot;: [],
                &quot;constraints&quot;: [],
                &quot;metadata&quot;: {},
                &quot;draft_instruction_id&quot;: &quot;go_write&quot;
              }
            ],
            &quot;constraints&quot;: [],
            &quot;data_source_kind&quot;: null
          },
          &quot;block_005&quot;: {
            &quot;block_id&quot;: &quot;block_005&quot;,
            &quot;block_name&quot;: &quot;将处理条数写入本地 count.txt&quot;,
            &quot;instructions&quot;: [
              {
                &quot;id&quot;: &quot;ir_009&quot;,
                &quot;opcode&quot;: &quot;write_file&quot;,
                &quot;inputs&quot;: [
                  {
                    &quot;type&quot;: &quot;external_resource&quot;,
                    &quot;identifier&quot;: &quot;count.txt&quot;,
                    &quot;semantic_name&quot;: &quot;count.txt&quot;
                  },
                  {
                    &quot;type&quot;: &quot;result&quot;,
                    &quot;identifier&quot;: &quot;result_003&quot;,
                    &quot;semantic_name&quot;: &quot;processed_count&quot;
                  }
                ],
                &quot;outputs&quot;: [],
                &quot;constraints&quot;: [
                  &quot;处理完成后，将处理条数写入本地 count.txt。&quot;
                ],
                &quot;metadata&quot;: {},
                &quot;draft_instruction_id&quot;: &quot;write_count_file&quot;
              },
              {
                &quot;id&quot;: &quot;ir_010&quot;,
                &quot;opcode&quot;: &quot;return&quot;,
                &quot;inputs&quot;: [],
                &quot;outputs&quot;: [],
                &quot;constraints&quot;: [],
                &quot;metadata&quot;: {},
                &quot;draft_instruction_id&quot;: &quot;finish&quot;
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
          },
          {
            &quot;source_block_id&quot;: &quot;block_004&quot;,
            &quot;target_block_id&quot;: &quot;block_005&quot;,
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
          &quot;block_name&quot;: &quot;读取用户提供的 events.json&quot;,
          &quot;instructions&quot;: [
            {
              &quot;id&quot;: &quot;ir_001&quot;,
              &quot;opcode&quot;: &quot;read_file&quot;,
              &quot;inputs&quot;: [
                {
                  &quot;type&quot;: &quot;external_resource&quot;,
                  &quot;identifier&quot;: &quot;用户提供的 events.json&quot;,
                  &quot;semantic_name&quot;: &quot;用户提供的 events.json&quot;
                }
              ],
              &quot;outputs&quot;: [
                {
                  &quot;type&quot;: &quot;result&quot;,
                  &quot;identifier&quot;: &quot;result_001&quot;,
                  &quot;semantic_name&quot;: &quot;event_records&quot;
                }
              ],
              &quot;constraints&quot;: [],
              &quot;metadata&quot;: {},
              &quot;draft_instruction_id&quot;: &quot;read_events_file&quot;
            },
            {
              &quot;id&quot;: &quot;ir_002&quot;,
              &quot;opcode&quot;: &quot;dispatch&quot;,
              &quot;inputs&quot;: [],
              &quot;outputs&quot;: [],
              &quot;constraints&quot;: [],
              &quot;metadata&quot;: {},
              &quot;draft_instruction_id&quot;: &quot;go_select&quot;
            }
          ],
          &quot;constraints&quot;: [
            &quot;读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。&quot;
          ],
          &quot;data_source_kind&quot;: &quot;external&quot;
        },
        &quot;block_002&quot;: {
          &quot;block_id&quot;: &quot;block_002&quot;,
          &quot;block_name&quot;: &quot;根据 opted_out、urgent 和 value 条件选中记录&quot;,
          &quot;instructions&quot;: [
            {
              &quot;id&quot;: &quot;ir_003&quot;,
              &quot;opcode&quot;: &quot;select_notifiable_events&quot;,
              &quot;inputs&quot;: [
                {
                  &quot;type&quot;: &quot;result&quot;,
                  &quot;identifier&quot;: &quot;result_001&quot;,
                  &quot;semantic_name&quot;: &quot;event_records&quot;
                }
              ],
              &quot;outputs&quot;: [
                {
                  &quot;type&quot;: &quot;result&quot;,
                  &quot;identifier&quot;: &quot;result_002&quot;,
                  &quot;semantic_name&quot;: &quot;selected_records&quot;
                }
              ],
              &quot;constraints&quot;: [
                &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;,
                &quot;urgent 为 true 只豁免数值门槛，不豁免 opted_out 的限制。&quot;
              ],
              &quot;metadata&quot;: {},
              &quot;draft_instruction_id&quot;: &quot;select_notifiable&quot;
            },
            {
              &quot;id&quot;: &quot;ir_004&quot;,
              &quot;opcode&quot;: &quot;dispatch&quot;,
              &quot;inputs&quot;: [],
              &quot;outputs&quot;: [],
              &quot;constraints&quot;: [],
              &quot;metadata&quot;: {},
              &quot;draft_instruction_id&quot;: &quot;go_send&quot;
            }
          ],
          &quot;constraints&quot;: [],
          &quot;data_source_kind&quot;: null
        },
        &quot;block_003&quot;: {
          &quot;block_id&quot;: &quot;block_003&quot;,
          &quot;block_name&quot;: &quot;对每条选中记录调用 notify.send&quot;,
          &quot;instructions&quot;: [
            {
              &quot;id&quot;: &quot;ir_005&quot;,
              &quot;opcode&quot;: &quot;notify.send&quot;,
              &quot;inputs&quot;: [
                {
                  &quot;type&quot;: &quot;external_resource&quot;,
                  &quot;identifier&quot;: &quot;notify.send&quot;,
                  &quot;semantic_name&quot;: &quot;notify.send&quot;
                },
                {
                  &quot;type&quot;: &quot;result&quot;,
                  &quot;identifier&quot;: &quot;result_002&quot;,
                  &quot;semantic_name&quot;: &quot;selected_records&quot;
                },
                {
                  &quot;type&quot;: &quot;literal&quot;,
                  &quot;identifier&quot;: null,
                  &quot;literal_value&quot;: &quot;recipient&quot;
                },
                {
                  &quot;type&quot;: &quot;literal&quot;,
                  &quot;identifier&quot;: null,
                  &quot;literal_value&quot;: &quot;summary&quot;
                }
              ],
              &quot;outputs&quot;: [],
              &quot;constraints&quot;: [
                &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
                &quot;notify.send 的 body 参数直接取该记录的 summary 字段原值。&quot;,
                &quot;未选中的记录不调用 notify.send。&quot;
              ],
              &quot;metadata&quot;: {
                &quot;per_record&quot;: true,
                &quot;recipient_field&quot;: &quot;recipient&quot;,
                &quot;body_field&quot;: &quot;summary&quot;
              },
              &quot;draft_instruction_id&quot;: &quot;send_notify&quot;
            },
            {
              &quot;id&quot;: &quot;ir_006&quot;,
              &quot;opcode&quot;: &quot;dispatch&quot;,
              &quot;inputs&quot;: [],
              &quot;outputs&quot;: [],
              &quot;constraints&quot;: [],
              &quot;metadata&quot;: {},
              &quot;draft_instruction_id&quot;: &quot;go_count&quot;
            }
          ],
          &quot;constraints&quot;: [],
          &quot;data_source_kind&quot;: null
        },
        &quot;block_004&quot;: {
          &quot;block_id&quot;: &quot;block_004&quot;,
          &quot;block_name&quot;: &quot;统计已处理条数&quot;,
          &quot;instructions&quot;: [
            {
              &quot;id&quot;: &quot;ir_007&quot;,
              &quot;opcode&quot;: &quot;count_processed_records&quot;,
              &quot;inputs&quot;: [
                {
                  &quot;type&quot;: &quot;result&quot;,
                  &quot;identifier&quot;: &quot;result_002&quot;,
                  &quot;semantic_name&quot;: &quot;selected_records&quot;
                }
              ],
              &quot;outputs&quot;: [
                {
                  &quot;type&quot;: &quot;result&quot;,
                  &quot;identifier&quot;: &quot;result_003&quot;,
                  &quot;semantic_name&quot;: &quot;processed_count&quot;
                }
              ],
              &quot;constraints&quot;: [],
              &quot;metadata&quot;: {},
              &quot;draft_instruction_id&quot;: &quot;count_processed_records&quot;
            },
            {
              &quot;id&quot;: &quot;ir_008&quot;,
              &quot;opcode&quot;: &quot;dispatch&quot;,
              &quot;inputs&quot;: [],
              &quot;outputs&quot;: [],
              &quot;constraints&quot;: [],
              &quot;metadata&quot;: {},
              &quot;draft_instruction_id&quot;: &quot;go_write&quot;
            }
          ],
          &quot;constraints&quot;: [],
          &quot;data_source_kind&quot;: null
        },
        &quot;block_005&quot;: {
          &quot;block_id&quot;: &quot;block_005&quot;,
          &quot;block_name&quot;: &quot;将处理条数写入本地 count.txt&quot;,
          &quot;instructions&quot;: [
            {
              &quot;id&quot;: &quot;ir_009&quot;,
              &quot;opcode&quot;: &quot;write_file&quot;,
              &quot;inputs&quot;: [
                {
                  &quot;type&quot;: &quot;external_resource&quot;,
                  &quot;identifier&quot;: &quot;count.txt&quot;,
                  &quot;semantic_name&quot;: &quot;count.txt&quot;
                },
                {
                  &quot;type&quot;: &quot;result&quot;,
                  &quot;identifier&quot;: &quot;result_003&quot;,
                  &quot;semantic_name&quot;: &quot;processed_count&quot;
                }
              ],
              &quot;outputs&quot;: [],
              &quot;constraints&quot;: [
                &quot;处理完成后，将处理条数写入本地 count.txt。&quot;
              ],
              &quot;metadata&quot;: {},
              &quot;draft_instruction_id&quot;: &quot;write_count_file&quot;
            },
            {
              &quot;id&quot;: &quot;ir_010&quot;,
              &quot;opcode&quot;: &quot;return&quot;,
              &quot;inputs&quot;: [],
              &quot;outputs&quot;: [],
              &quot;constraints&quot;: [],
              &quot;metadata&quot;: {},
              &quot;draft_instruction_id&quot;: &quot;finish&quot;
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
        &quot;block_name&quot;: &quot;读取用户提供的 events.json&quot;,
        &quot;instructions&quot;: [
          {
            &quot;id&quot;: &quot;ir_001&quot;,
            &quot;opcode&quot;: &quot;read_file&quot;,
            &quot;inputs&quot;: [
              {
                &quot;type&quot;: &quot;external_resource&quot;,
                &quot;identifier&quot;: &quot;用户提供的 events.json&quot;,
                &quot;semantic_name&quot;: &quot;用户提供的 events.json&quot;
              }
            ],
            &quot;outputs&quot;: [
              {
                &quot;type&quot;: &quot;result&quot;,
                &quot;identifier&quot;: &quot;result_001&quot;,
                &quot;semantic_name&quot;: &quot;event_records&quot;
              }
            ],
            &quot;constraints&quot;: [],
            &quot;metadata&quot;: {},
            &quot;draft_instruction_id&quot;: &quot;read_events_file&quot;
          },
          {
            &quot;id&quot;: &quot;ir_002&quot;,
            &quot;opcode&quot;: &quot;dispatch&quot;,
            &quot;inputs&quot;: [],
            &quot;outputs&quot;: [],
            &quot;constraints&quot;: [],
            &quot;metadata&quot;: {},
            &quot;draft_instruction_id&quot;: &quot;go_select&quot;
          }
        ],
        &quot;constraints&quot;: [
          &quot;读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。&quot;
        ],
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
      &quot;value&quot;: &quot;读取用户提供的 events.json&quot;,
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
      &quot;value&quot;: [
        &quot;读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。&quot;
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_66f0785e9291c3fb5ee7&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_001/constraints/0&quot;,
      &quot;kind&quot;: &quot;constraint&quot;,
      &quot;block_id&quot;: &quot;block_001&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_001&quot;,
        &quot;constraints&quot;,
        0
      ],
      &quot;value&quot;: &quot;读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。&quot;,
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
          &quot;opcode&quot;: &quot;read_file&quot;,
          &quot;inputs&quot;: [
            {
              &quot;type&quot;: &quot;external_resource&quot;,
              &quot;identifier&quot;: &quot;用户提供的 events.json&quot;,
              &quot;semantic_name&quot;: &quot;用户提供的 events.json&quot;
            }
          ],
          &quot;outputs&quot;: [
            {
              &quot;type&quot;: &quot;result&quot;,
              &quot;identifier&quot;: &quot;result_001&quot;,
              &quot;semantic_name&quot;: &quot;event_records&quot;
            }
          ],
          &quot;constraints&quot;: [],
          &quot;metadata&quot;: {},
          &quot;draft_instruction_id&quot;: &quot;read_events_file&quot;
        },
        {
          &quot;id&quot;: &quot;ir_002&quot;,
          &quot;opcode&quot;: &quot;dispatch&quot;,
          &quot;inputs&quot;: [],
          &quot;outputs&quot;: [],
          &quot;constraints&quot;: [],
          &quot;metadata&quot;: {},
          &quot;draft_instruction_id&quot;: &quot;go_select&quot;
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
        &quot;opcode&quot;: &quot;read_file&quot;,
        &quot;inputs&quot;: [
          {
            &quot;type&quot;: &quot;external_resource&quot;,
            &quot;identifier&quot;: &quot;用户提供的 events.json&quot;,
            &quot;semantic_name&quot;: &quot;用户提供的 events.json&quot;
          }
        ],
        &quot;outputs&quot;: [
          {
            &quot;type&quot;: &quot;result&quot;,
            &quot;identifier&quot;: &quot;result_001&quot;,
            &quot;semantic_name&quot;: &quot;event_records&quot;
          }
        ],
        &quot;constraints&quot;: [],
        &quot;metadata&quot;: {},
        &quot;draft_instruction_id&quot;: &quot;read_events_file&quot;
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
      &quot;value&quot;: &quot;read_events_file&quot;,
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
          &quot;identifier&quot;: &quot;用户提供的 events.json&quot;,
          &quot;semantic_name&quot;: &quot;用户提供的 events.json&quot;
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
        &quot;identifier&quot;: &quot;用户提供的 events.json&quot;,
        &quot;semantic_name&quot;: &quot;用户提供的 events.json&quot;
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
      &quot;value&quot;: &quot;用户提供的 events.json&quot;,
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
      &quot;value&quot;: &quot;用户提供的 events.json&quot;,
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
      &quot;value&quot;: &quot;read_file&quot;,
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
          &quot;semantic_name&quot;: &quot;event_records&quot;
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
        &quot;semantic_name&quot;: &quot;event_records&quot;
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
      &quot;value&quot;: &quot;event_records&quot;,
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
        &quot;draft_instruction_id&quot;: &quot;go_select&quot;
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
      &quot;value&quot;: &quot;go_select&quot;,
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
        &quot;block_name&quot;: &quot;根据 opted_out、urgent 和 value 条件选中记录&quot;,
        &quot;instructions&quot;: [
          {
            &quot;id&quot;: &quot;ir_003&quot;,
            &quot;opcode&quot;: &quot;select_notifiable_events&quot;,
            &quot;inputs&quot;: [
              {
                &quot;type&quot;: &quot;result&quot;,
                &quot;identifier&quot;: &quot;result_001&quot;,
                &quot;semantic_name&quot;: &quot;event_records&quot;
              }
            ],
            &quot;outputs&quot;: [
              {
                &quot;type&quot;: &quot;result&quot;,
                &quot;identifier&quot;: &quot;result_002&quot;,
                &quot;semantic_name&quot;: &quot;selected_records&quot;
              }
            ],
            &quot;constraints&quot;: [
              &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;,
              &quot;urgent 为 true 只豁免数值门槛，不豁免 opted_out 的限制。&quot;
            ],
            &quot;metadata&quot;: {},
            &quot;draft_instruction_id&quot;: &quot;select_notifiable&quot;
          },
          {
            &quot;id&quot;: &quot;ir_004&quot;,
            &quot;opcode&quot;: &quot;dispatch&quot;,
            &quot;inputs&quot;: [],
            &quot;outputs&quot;: [],
            &quot;constraints&quot;: [],
            &quot;metadata&quot;: {},
            &quot;draft_instruction_id&quot;: &quot;go_send&quot;
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
      &quot;value&quot;: &quot;根据 opted_out、urgent 和 value 条件选中记录&quot;,
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
          &quot;opcode&quot;: &quot;select_notifiable_events&quot;,
          &quot;inputs&quot;: [
            {
              &quot;type&quot;: &quot;result&quot;,
              &quot;identifier&quot;: &quot;result_001&quot;,
              &quot;semantic_name&quot;: &quot;event_records&quot;
            }
          ],
          &quot;outputs&quot;: [
            {
              &quot;type&quot;: &quot;result&quot;,
              &quot;identifier&quot;: &quot;result_002&quot;,
              &quot;semantic_name&quot;: &quot;selected_records&quot;
            }
          ],
          &quot;constraints&quot;: [
            &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;,
            &quot;urgent 为 true 只豁免数值门槛，不豁免 opted_out 的限制。&quot;
          ],
          &quot;metadata&quot;: {},
          &quot;draft_instruction_id&quot;: &quot;select_notifiable&quot;
        },
        {
          &quot;id&quot;: &quot;ir_004&quot;,
          &quot;opcode&quot;: &quot;dispatch&quot;,
          &quot;inputs&quot;: [],
          &quot;outputs&quot;: [],
          &quot;constraints&quot;: [],
          &quot;metadata&quot;: {},
          &quot;draft_instruction_id&quot;: &quot;go_send&quot;
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
        &quot;opcode&quot;: &quot;select_notifiable_events&quot;,
        &quot;inputs&quot;: [
          {
            &quot;type&quot;: &quot;result&quot;,
            &quot;identifier&quot;: &quot;result_001&quot;,
            &quot;semantic_name&quot;: &quot;event_records&quot;
          }
        ],
        &quot;outputs&quot;: [
          {
            &quot;type&quot;: &quot;result&quot;,
            &quot;identifier&quot;: &quot;result_002&quot;,
            &quot;semantic_name&quot;: &quot;selected_records&quot;
          }
        ],
        &quot;constraints&quot;: [
          &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;,
          &quot;urgent 为 true 只豁免数值门槛，不豁免 opted_out 的限制。&quot;
        ],
        &quot;metadata&quot;: {},
        &quot;draft_instruction_id&quot;: &quot;select_notifiable&quot;
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
      &quot;value&quot;: [
        &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;,
        &quot;urgent 为 true 只豁免数值门槛，不豁免 opted_out 的限制。&quot;
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_81ff9a19868074649a51&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/0/constraints/0&quot;,
      &quot;kind&quot;: &quot;constraint&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_003&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        0,
        &quot;constraints&quot;,
        0
      ],
      &quot;value&quot;: &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_80cda75cb9ace38b3d87&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_002/instructions/0/constraints/1&quot;,
      &quot;kind&quot;: &quot;constraint&quot;,
      &quot;block_id&quot;: &quot;block_002&quot;,
      &quot;instruction_id&quot;: &quot;ir_003&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_002&quot;,
        &quot;instructions&quot;,
        0,
        &quot;constraints&quot;,
        1
      ],
      &quot;value&quot;: &quot;urgent 为 true 只豁免数值门槛，不豁免 opted_out 的限制。&quot;,
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
      &quot;value&quot;: &quot;select_notifiable&quot;,
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
          &quot;semantic_name&quot;: &quot;event_records&quot;
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
        &quot;semantic_name&quot;: &quot;event_records&quot;
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
      &quot;value&quot;: &quot;event_records&quot;,
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
      &quot;value&quot;: &quot;select_notifiable_events&quot;,
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
          &quot;semantic_name&quot;: &quot;selected_records&quot;
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
        &quot;semantic_name&quot;: &quot;selected_records&quot;
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
      &quot;value&quot;: &quot;selected_records&quot;,
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
        &quot;opcode&quot;: &quot;dispatch&quot;,
        &quot;inputs&quot;: [],
        &quot;outputs&quot;: [],
        &quot;constraints&quot;: [],
        &quot;metadata&quot;: {},
        &quot;draft_instruction_id&quot;: &quot;go_send&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: true,
      &quot;input_count&quot;: 0,
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
      &quot;input_count&quot;: 0,
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
      &quot;value&quot;: &quot;go_send&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
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
      &quot;input_count&quot;: 0,
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
      &quot;value&quot;: [],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
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
      &quot;input_count&quot;: 0,
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
      &quot;value&quot;: &quot;dispatch&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
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
        &quot;block_name&quot;: &quot;对每条选中记录调用 notify.send&quot;,
        &quot;instructions&quot;: [
          {
            &quot;id&quot;: &quot;ir_005&quot;,
            &quot;opcode&quot;: &quot;notify.send&quot;,
            &quot;inputs&quot;: [
              {
                &quot;type&quot;: &quot;external_resource&quot;,
                &quot;identifier&quot;: &quot;notify.send&quot;,
                &quot;semantic_name&quot;: &quot;notify.send&quot;
              },
              {
                &quot;type&quot;: &quot;result&quot;,
                &quot;identifier&quot;: &quot;result_002&quot;,
                &quot;semantic_name&quot;: &quot;selected_records&quot;
              },
              {
                &quot;type&quot;: &quot;literal&quot;,
                &quot;identifier&quot;: null,
                &quot;literal_value&quot;: &quot;recipient&quot;
              },
              {
                &quot;type&quot;: &quot;literal&quot;,
                &quot;identifier&quot;: null,
                &quot;literal_value&quot;: &quot;summary&quot;
              }
            ],
            &quot;outputs&quot;: [],
            &quot;constraints&quot;: [
              &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
              &quot;notify.send 的 body 参数直接取该记录的 summary 字段原值。&quot;,
              &quot;未选中的记录不调用 notify.send。&quot;
            ],
            &quot;metadata&quot;: {
              &quot;per_record&quot;: true,
              &quot;recipient_field&quot;: &quot;recipient&quot;,
              &quot;body_field&quot;: &quot;summary&quot;
            },
            &quot;draft_instruction_id&quot;: &quot;send_notify&quot;
          },
          {
            &quot;id&quot;: &quot;ir_006&quot;,
            &quot;opcode&quot;: &quot;dispatch&quot;,
            &quot;inputs&quot;: [],
            &quot;outputs&quot;: [],
            &quot;constraints&quot;: [],
            &quot;metadata&quot;: {},
            &quot;draft_instruction_id&quot;: &quot;go_count&quot;
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
      &quot;value&quot;: &quot;对每条选中记录调用 notify.send&quot;,
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
      &quot;value&quot;: null,
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
          &quot;id&quot;: &quot;ir_005&quot;,
          &quot;opcode&quot;: &quot;notify.send&quot;,
          &quot;inputs&quot;: [
            {
              &quot;type&quot;: &quot;external_resource&quot;,
              &quot;identifier&quot;: &quot;notify.send&quot;,
              &quot;semantic_name&quot;: &quot;notify.send&quot;
            },
            {
              &quot;type&quot;: &quot;result&quot;,
              &quot;identifier&quot;: &quot;result_002&quot;,
              &quot;semantic_name&quot;: &quot;selected_records&quot;
            },
            {
              &quot;type&quot;: &quot;literal&quot;,
              &quot;identifier&quot;: null,
              &quot;literal_value&quot;: &quot;recipient&quot;
            },
            {
              &quot;type&quot;: &quot;literal&quot;,
              &quot;identifier&quot;: null,
              &quot;literal_value&quot;: &quot;summary&quot;
            }
          ],
          &quot;outputs&quot;: [],
          &quot;constraints&quot;: [
            &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
            &quot;notify.send 的 body 参数直接取该记录的 summary 字段原值。&quot;,
            &quot;未选中的记录不调用 notify.send。&quot;
          ],
          &quot;metadata&quot;: {
            &quot;per_record&quot;: true,
            &quot;recipient_field&quot;: &quot;recipient&quot;,
            &quot;body_field&quot;: &quot;summary&quot;
          },
          &quot;draft_instruction_id&quot;: &quot;send_notify&quot;
        },
        {
          &quot;id&quot;: &quot;ir_006&quot;,
          &quot;opcode&quot;: &quot;dispatch&quot;,
          &quot;inputs&quot;: [],
          &quot;outputs&quot;: [],
          &quot;constraints&quot;: [],
          &quot;metadata&quot;: {},
          &quot;draft_instruction_id&quot;: &quot;go_count&quot;
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
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0
      ],
      &quot;value&quot;: {
        &quot;id&quot;: &quot;ir_005&quot;,
        &quot;opcode&quot;: &quot;notify.send&quot;,
        &quot;inputs&quot;: [
          {
            &quot;type&quot;: &quot;external_resource&quot;,
            &quot;identifier&quot;: &quot;notify.send&quot;,
            &quot;semantic_name&quot;: &quot;notify.send&quot;
          },
          {
            &quot;type&quot;: &quot;result&quot;,
            &quot;identifier&quot;: &quot;result_002&quot;,
            &quot;semantic_name&quot;: &quot;selected_records&quot;
          },
          {
            &quot;type&quot;: &quot;literal&quot;,
            &quot;identifier&quot;: null,
            &quot;literal_value&quot;: &quot;recipient&quot;
          },
          {
            &quot;type&quot;: &quot;literal&quot;,
            &quot;identifier&quot;: null,
            &quot;literal_value&quot;: &quot;summary&quot;
          }
        ],
        &quot;outputs&quot;: [],
        &quot;constraints&quot;: [
          &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
          &quot;notify.send 的 body 参数直接取该记录的 summary 字段原值。&quot;,
          &quot;未选中的记录不调用 notify.send。&quot;
        ],
        &quot;metadata&quot;: {
          &quot;per_record&quot;: true,
          &quot;recipient_field&quot;: &quot;recipient&quot;,
          &quot;body_field&quot;: &quot;summary&quot;
        },
        &quot;draft_instruction_id&quot;: &quot;send_notify&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_87dafedba9a1d78f1675&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/constraints&quot;,
      &quot;kind&quot;: &quot;constraints&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;constraints&quot;
      ],
      &quot;value&quot;: [
        &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
        &quot;notify.send 的 body 参数直接取该记录的 summary 字段原值。&quot;,
        &quot;未选中的记录不调用 notify.send。&quot;
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_aeb48f99c87b5433380d&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/constraints/0&quot;,
      &quot;kind&quot;: &quot;constraint&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;constraints&quot;,
        0
      ],
      &quot;value&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_2a168b4a5f91acde4f8e&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/constraints/1&quot;,
      &quot;kind&quot;: &quot;constraint&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;constraints&quot;,
        1
      ],
      &quot;value&quot;: &quot;notify.send 的 body 参数直接取该记录的 summary 字段原值。&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_8fe35635386dff487a10&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/constraints/2&quot;,
      &quot;kind&quot;: &quot;constraint&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;constraints&quot;,
        2
      ],
      &quot;value&quot;: &quot;未选中的记录不调用 notify.send。&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_19141a1b733b451ee90a&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/draft_instruction_id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;draft_instruction_id&quot;
      ],
      &quot;value&quot;: &quot;send_notify&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_472ee958be2d1a82d1f9&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;id&quot;
      ],
      &quot;value&quot;: &quot;ir_005&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_cea4e4ee9a491bac6ef2&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
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
          &quot;identifier&quot;: &quot;notify.send&quot;,
          &quot;semantic_name&quot;: &quot;notify.send&quot;
        },
        {
          &quot;type&quot;: &quot;result&quot;,
          &quot;identifier&quot;: &quot;result_002&quot;,
          &quot;semantic_name&quot;: &quot;selected_records&quot;
        },
        {
          &quot;type&quot;: &quot;literal&quot;,
          &quot;identifier&quot;: null,
          &quot;literal_value&quot;: &quot;recipient&quot;
        },
        {
          &quot;type&quot;: &quot;literal&quot;,
          &quot;identifier&quot;: null,
          &quot;literal_value&quot;: &quot;summary&quot;
        }
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_4b7cacd582eecfb84195&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/0&quot;,
      &quot;kind&quot;: &quot;input&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
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
        &quot;identifier&quot;: &quot;notify.send&quot;,
        &quot;semantic_name&quot;: &quot;notify.send&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_81b13a64b9385b6d8b83&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/0/identifier&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
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
      &quot;value&quot;: &quot;notify.send&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_9b9e8992bb86b517ee65&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/0/semantic_name&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
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
      &quot;value&quot;: &quot;notify.send&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_67ca50f0790e15c71f64&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/0/type&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
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
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_70c96dfd296c8130066b&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/1&quot;,
      &quot;kind&quot;: &quot;input&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
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
        &quot;semantic_name&quot;: &quot;selected_records&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_49c48d0f59a29b3e8e8a&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/1/identifier&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
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
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_96d296de488397c7ca70&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/1/semantic_name&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
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
      &quot;value&quot;: &quot;selected_records&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_6db0fa07cb50eee0f651&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/1/type&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
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
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_d49b7dd46f8209dbe334&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/2&quot;,
      &quot;kind&quot;: &quot;input&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
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
        &quot;type&quot;: &quot;literal&quot;,
        &quot;identifier&quot;: null,
        &quot;literal_value&quot;: &quot;recipient&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_b21b1f4eac5dc2d155a6&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/2/identifier&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
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
      &quot;value&quot;: null,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_ea363a1c4666a432a3cd&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/2/literal_value&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        2,
        &quot;literal_value&quot;
      ],
      &quot;value&quot;: &quot;recipient&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_336e221dd239eb5cdb28&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/2/type&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
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
      &quot;value&quot;: &quot;literal&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_77b9604eaae52b5abbc6&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/3&quot;,
      &quot;kind&quot;: &quot;input&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
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
        &quot;type&quot;: &quot;literal&quot;,
        &quot;identifier&quot;: null,
        &quot;literal_value&quot;: &quot;summary&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_fe41be4473bb8bb98158&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/3/identifier&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
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
      &quot;value&quot;: null,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_7e44eedd3eaaee34b102&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/3/literal_value&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        3,
        &quot;literal_value&quot;
      ],
      &quot;value&quot;: &quot;summary&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_f039e2534f3fb445070d&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/inputs/3/type&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
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
      &quot;value&quot;: &quot;literal&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_486661a1fe0c92f7d5c4&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/metadata&quot;,
      &quot;kind&quot;: &quot;metadata&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;metadata&quot;
      ],
      &quot;value&quot;: {
        &quot;per_record&quot;: true,
        &quot;recipient_field&quot;: &quot;recipient&quot;,
        &quot;body_field&quot;: &quot;summary&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_88dbc4a1510a1f34cb23&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/metadata/body_field&quot;,
      &quot;kind&quot;: &quot;metadata_value&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;metadata&quot;,
        &quot;body_field&quot;
      ],
      &quot;value&quot;: &quot;summary&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_8e519da0aef569df923b&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/metadata/per_record&quot;,
      &quot;kind&quot;: &quot;metadata_value&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;metadata&quot;,
        &quot;per_record&quot;
      ],
      &quot;value&quot;: true,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_d9d2de70b7b184ba76a0&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/metadata/recipient_field&quot;,
      &quot;kind&quot;: &quot;metadata_value&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;metadata&quot;,
        &quot;recipient_field&quot;
      ],
      &quot;value&quot;: &quot;recipient&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_4d692262bdef4fa1e046&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/opcode&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;opcode&quot;
      ],
      &quot;value&quot;: &quot;notify.send&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_75937558dfb0670c42f8&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/0/outputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        0,
        &quot;outputs&quot;
      ],
      &quot;value&quot;: [],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_6d2995384fed34945dbc&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_003/instructions/1&quot;,
      &quot;kind&quot;: &quot;instruction&quot;,
      &quot;block_id&quot;: &quot;block_003&quot;,
      &quot;instruction_id&quot;: &quot;ir_006&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        1
      ],
      &quot;value&quot;: {
        &quot;id&quot;: &quot;ir_006&quot;,
        &quot;opcode&quot;: &quot;dispatch&quot;,
        &quot;inputs&quot;: [],
        &quot;outputs&quot;: [],
        &quot;constraints&quot;: [],
        &quot;metadata&quot;: {},
        &quot;draft_instruction_id&quot;: &quot;go_count&quot;
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
      &quot;instruction_id&quot;: &quot;ir_006&quot;,
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
      &quot;instruction_id&quot;: &quot;ir_006&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        1,
        &quot;draft_instruction_id&quot;
      ],
      &quot;value&quot;: &quot;go_count&quot;,
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
      &quot;instruction_id&quot;: &quot;ir_006&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_003&quot;,
        &quot;instructions&quot;,
        1,
        &quot;id&quot;
      ],
      &quot;value&quot;: &quot;ir_006&quot;,
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
      &quot;instruction_id&quot;: &quot;ir_006&quot;,
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
      &quot;instruction_id&quot;: &quot;ir_006&quot;,
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
      &quot;instruction_id&quot;: &quot;ir_006&quot;,
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
      &quot;instruction_id&quot;: &quot;ir_006&quot;,
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
        &quot;block_name&quot;: &quot;统计已处理条数&quot;,
        &quot;instructions&quot;: [
          {
            &quot;id&quot;: &quot;ir_007&quot;,
            &quot;opcode&quot;: &quot;count_processed_records&quot;,
            &quot;inputs&quot;: [
              {
                &quot;type&quot;: &quot;result&quot;,
                &quot;identifier&quot;: &quot;result_002&quot;,
                &quot;semantic_name&quot;: &quot;selected_records&quot;
              }
            ],
            &quot;outputs&quot;: [
              {
                &quot;type&quot;: &quot;result&quot;,
                &quot;identifier&quot;: &quot;result_003&quot;,
                &quot;semantic_name&quot;: &quot;processed_count&quot;
              }
            ],
            &quot;constraints&quot;: [],
            &quot;metadata&quot;: {},
            &quot;draft_instruction_id&quot;: &quot;count_processed_records&quot;
          },
          {
            &quot;id&quot;: &quot;ir_008&quot;,
            &quot;opcode&quot;: &quot;dispatch&quot;,
            &quot;inputs&quot;: [],
            &quot;outputs&quot;: [],
            &quot;constraints&quot;: [],
            &quot;metadata&quot;: {},
            &quot;draft_instruction_id&quot;: &quot;go_write&quot;
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
      &quot;value&quot;: &quot;统计已处理条数&quot;,
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
          &quot;id&quot;: &quot;ir_007&quot;,
          &quot;opcode&quot;: &quot;count_processed_records&quot;,
          &quot;inputs&quot;: [
            {
              &quot;type&quot;: &quot;result&quot;,
              &quot;identifier&quot;: &quot;result_002&quot;,
              &quot;semantic_name&quot;: &quot;selected_records&quot;
            }
          ],
          &quot;outputs&quot;: [
            {
              &quot;type&quot;: &quot;result&quot;,
              &quot;identifier&quot;: &quot;result_003&quot;,
              &quot;semantic_name&quot;: &quot;processed_count&quot;
            }
          ],
          &quot;constraints&quot;: [],
          &quot;metadata&quot;: {},
          &quot;draft_instruction_id&quot;: &quot;count_processed_records&quot;
        },
        {
          &quot;id&quot;: &quot;ir_008&quot;,
          &quot;opcode&quot;: &quot;dispatch&quot;,
          &quot;inputs&quot;: [],
          &quot;outputs&quot;: [],
          &quot;constraints&quot;: [],
          &quot;metadata&quot;: {},
          &quot;draft_instruction_id&quot;: &quot;go_write&quot;
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
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        0
      ],
      &quot;value&quot;: {
        &quot;id&quot;: &quot;ir_007&quot;,
        &quot;opcode&quot;: &quot;count_processed_records&quot;,
        &quot;inputs&quot;: [
          {
            &quot;type&quot;: &quot;result&quot;,
            &quot;identifier&quot;: &quot;result_002&quot;,
            &quot;semantic_name&quot;: &quot;selected_records&quot;
          }
        ],
        &quot;outputs&quot;: [
          {
            &quot;type&quot;: &quot;result&quot;,
            &quot;identifier&quot;: &quot;result_003&quot;,
            &quot;semantic_name&quot;: &quot;processed_count&quot;
          }
        ],
        &quot;constraints&quot;: [],
        &quot;metadata&quot;: {},
        &quot;draft_instruction_id&quot;: &quot;count_processed_records&quot;
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
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
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
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        0,
        &quot;draft_instruction_id&quot;
      ],
      &quot;value&quot;: &quot;count_processed_records&quot;,
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
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        0,
        &quot;id&quot;
      ],
      &quot;value&quot;: &quot;ir_007&quot;,
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
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
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
          &quot;identifier&quot;: &quot;result_002&quot;,
          &quot;semantic_name&quot;: &quot;selected_records&quot;
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
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
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
        &quot;identifier&quot;: &quot;result_002&quot;,
        &quot;semantic_name&quot;: &quot;selected_records&quot;
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
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
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
      &quot;value&quot;: &quot;result_002&quot;,
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
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
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
      &quot;value&quot;: &quot;selected_records&quot;,
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
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
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
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
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
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        0,
        &quot;opcode&quot;
      ],
      &quot;value&quot;: &quot;count_processed_records&quot;,
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
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
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
          &quot;identifier&quot;: &quot;result_003&quot;,
          &quot;semantic_name&quot;: &quot;processed_count&quot;
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
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
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
        &quot;identifier&quot;: &quot;result_003&quot;,
        &quot;semantic_name&quot;: &quot;processed_count&quot;
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
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
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
      &quot;value&quot;: &quot;result_003&quot;,
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
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
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
      &quot;value&quot;: &quot;processed_count&quot;,
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
      &quot;instruction_id&quot;: &quot;ir_007&quot;,
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
      &quot;instruction_id&quot;: &quot;ir_008&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
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
        &quot;draft_instruction_id&quot;: &quot;go_write&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: true,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_36fb20851e6bb54fec07&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/1/constraints&quot;,
      &quot;kind&quot;: &quot;constraints&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_008&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
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
    &quot;target_26deb537ff49d78d397f&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/1/draft_instruction_id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_008&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
        &quot;instructions&quot;,
        1,
        &quot;draft_instruction_id&quot;
      ],
      &quot;value&quot;: &quot;go_write&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_b8ab99b21c96288902de&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/1/id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_008&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
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
    &quot;target_3de614466f0c8ef33a19&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/1/inputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_008&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
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
    &quot;target_092295b777adf7b9880f&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/1/metadata&quot;,
      &quot;kind&quot;: &quot;metadata&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_008&quot;,
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
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_ad7879b2e2895bc93a40&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/1/opcode&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_008&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_004&quot;,
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
    &quot;target_e0d557e6c127f93627b5&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_004/instructions/1/outputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_004&quot;,
      &quot;instruction_id&quot;: &quot;ir_008&quot;,
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
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_d0da5db1067ad87bc654&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005&quot;,
      &quot;kind&quot;: &quot;block&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;
      ],
      &quot;value&quot;: {
        &quot;block_id&quot;: &quot;block_005&quot;,
        &quot;block_name&quot;: &quot;将处理条数写入本地 count.txt&quot;,
        &quot;instructions&quot;: [
          {
            &quot;id&quot;: &quot;ir_009&quot;,
            &quot;opcode&quot;: &quot;write_file&quot;,
            &quot;inputs&quot;: [
              {
                &quot;type&quot;: &quot;external_resource&quot;,
                &quot;identifier&quot;: &quot;count.txt&quot;,
                &quot;semantic_name&quot;: &quot;count.txt&quot;
              },
              {
                &quot;type&quot;: &quot;result&quot;,
                &quot;identifier&quot;: &quot;result_003&quot;,
                &quot;semantic_name&quot;: &quot;processed_count&quot;
              }
            ],
            &quot;outputs&quot;: [],
            &quot;constraints&quot;: [
              &quot;处理完成后，将处理条数写入本地 count.txt。&quot;
            ],
            &quot;metadata&quot;: {},
            &quot;draft_instruction_id&quot;: &quot;write_count_file&quot;
          },
          {
            &quot;id&quot;: &quot;ir_010&quot;,
            &quot;opcode&quot;: &quot;return&quot;,
            &quot;inputs&quot;: [],
            &quot;outputs&quot;: [],
            &quot;constraints&quot;: [],
            &quot;metadata&quot;: {},
            &quot;draft_instruction_id&quot;: &quot;finish&quot;
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
    &quot;target_384d9f79acea3889b15d&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005/block_id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;,
        &quot;block_id&quot;
      ],
      &quot;value&quot;: &quot;block_005&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_e1e2453a78cbac2d158d&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005/block_name&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;,
        &quot;block_name&quot;
      ],
      &quot;value&quot;: &quot;将处理条数写入本地 count.txt&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_02cac622aac23d5faf38&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005/constraints&quot;,
      &quot;kind&quot;: &quot;constraints&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;,
        &quot;constraints&quot;
      ],
      &quot;value&quot;: [],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_3f6333777b9d11ed5154&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005/data_source_kind&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;,
        &quot;data_source_kind&quot;
      ],
      &quot;value&quot;: null,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_36603b3162a4fc13f8fe&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005/instructions&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;,
        &quot;instructions&quot;
      ],
      &quot;value&quot;: [
        {
          &quot;id&quot;: &quot;ir_009&quot;,
          &quot;opcode&quot;: &quot;write_file&quot;,
          &quot;inputs&quot;: [
            {
              &quot;type&quot;: &quot;external_resource&quot;,
              &quot;identifier&quot;: &quot;count.txt&quot;,
              &quot;semantic_name&quot;: &quot;count.txt&quot;
            },
            {
              &quot;type&quot;: &quot;result&quot;,
              &quot;identifier&quot;: &quot;result_003&quot;,
              &quot;semantic_name&quot;: &quot;processed_count&quot;
            }
          ],
          &quot;outputs&quot;: [],
          &quot;constraints&quot;: [
            &quot;处理完成后，将处理条数写入本地 count.txt。&quot;
          ],
          &quot;metadata&quot;: {},
          &quot;draft_instruction_id&quot;: &quot;write_count_file&quot;
        },
        {
          &quot;id&quot;: &quot;ir_010&quot;,
          &quot;opcode&quot;: &quot;return&quot;,
          &quot;inputs&quot;: [],
          &quot;outputs&quot;: [],
          &quot;constraints&quot;: [],
          &quot;metadata&quot;: {},
          &quot;draft_instruction_id&quot;: &quot;finish&quot;
        }
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_c1071833b6da68beaf27&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005/instructions/0&quot;,
      &quot;kind&quot;: &quot;instruction&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;,
        &quot;instructions&quot;,
        0
      ],
      &quot;value&quot;: {
        &quot;id&quot;: &quot;ir_009&quot;,
        &quot;opcode&quot;: &quot;write_file&quot;,
        &quot;inputs&quot;: [
          {
            &quot;type&quot;: &quot;external_resource&quot;,
            &quot;identifier&quot;: &quot;count.txt&quot;,
            &quot;semantic_name&quot;: &quot;count.txt&quot;
          },
          {
            &quot;type&quot;: &quot;result&quot;,
            &quot;identifier&quot;: &quot;result_003&quot;,
            &quot;semantic_name&quot;: &quot;processed_count&quot;
          }
        ],
        &quot;outputs&quot;: [],
        &quot;constraints&quot;: [
          &quot;处理完成后，将处理条数写入本地 count.txt。&quot;
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
    &quot;target_28fa3213df078ac4f772&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005/instructions/0/constraints&quot;,
      &quot;kind&quot;: &quot;constraints&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;,
        &quot;instructions&quot;,
        0,
        &quot;constraints&quot;
      ],
      &quot;value&quot;: [
        &quot;处理完成后，将处理条数写入本地 count.txt。&quot;
      ],
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 2,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_e08b75a2cb7a3d042567&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005/instructions/0/constraints/0&quot;,
      &quot;kind&quot;: &quot;constraint&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;,
        &quot;instructions&quot;,
        0,
        &quot;constraints&quot;,
        0
      ],
      &quot;value&quot;: &quot;处理完成后，将处理条数写入本地 count.txt。&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 2,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_03b2173e89226761961f&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005/instructions/0/draft_instruction_id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;,
        &quot;instructions&quot;,
        0,
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
    &quot;target_212c7326f378c7f0687d&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005/instructions/0/id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;,
        &quot;instructions&quot;,
        0,
        &quot;id&quot;
      ],
      &quot;value&quot;: &quot;ir_009&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 2,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_46638cf647c5644994f7&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005/instructions/0/inputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;,
        &quot;instructions&quot;,
        0,
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
          &quot;identifier&quot;: &quot;result_003&quot;,
          &quot;semantic_name&quot;: &quot;processed_count&quot;
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
    &quot;target_fe0a60eb7dc3da061231&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005/instructions/0/inputs/0&quot;,
      &quot;kind&quot;: &quot;input&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;,
        &quot;instructions&quot;,
        0,
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
    &quot;target_882ec1db31f5ae226793&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005/instructions/0/inputs/0/identifier&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;,
        &quot;instructions&quot;,
        0,
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
    &quot;target_b0f2d34dafab294c7dd9&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005/instructions/0/inputs/0/semantic_name&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;,
        &quot;instructions&quot;,
        0,
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
    &quot;target_eb45abe57234546a81e1&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005/instructions/0/inputs/0/type&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;,
        &quot;instructions&quot;,
        0,
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
    &quot;target_97b4dc7a239bae8e8e2a&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005/instructions/0/inputs/1&quot;,
      &quot;kind&quot;: &quot;input&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        1
      ],
      &quot;value&quot;: {
        &quot;type&quot;: &quot;result&quot;,
        &quot;identifier&quot;: &quot;result_003&quot;,
        &quot;semantic_name&quot;: &quot;processed_count&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 2,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_dab2a6857403a36ccb63&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005/instructions/0/inputs/1/identifier&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        1,
        &quot;identifier&quot;
      ],
      &quot;value&quot;: &quot;result_003&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 2,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_cf84592c2def4b32cebc&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005/instructions/0/inputs/1/semantic_name&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;,
        &quot;instructions&quot;,
        0,
        &quot;inputs&quot;,
        1,
        &quot;semantic_name&quot;
      ],
      &quot;value&quot;: &quot;processed_count&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 2,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_d75e8ee0c8ecec46895e&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005/instructions/0/inputs/1/type&quot;,
      &quot;kind&quot;: &quot;operand_field&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;,
        &quot;instructions&quot;,
        0,
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
    &quot;target_2f4d9369887edb044ea2&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005/instructions/0/metadata&quot;,
      &quot;kind&quot;: &quot;metadata&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;,
        &quot;instructions&quot;,
        0,
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
    &quot;target_53961a92734fbf0aa623&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005/instructions/0/opcode&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;,
        &quot;instructions&quot;,
        0,
        &quot;opcode&quot;
      ],
      &quot;value&quot;: &quot;write_file&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 2,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ]
    },
    &quot;target_45041b0e6b29a8b13277&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005/instructions/0/outputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;instruction_id&quot;: &quot;ir_009&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;,
        &quot;instructions&quot;,
        0,
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
    &quot;target_b82bec5e4beac6b36110&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005/instructions/1&quot;,
      &quot;kind&quot;: &quot;instruction&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;,
        &quot;instructions&quot;,
        1
      ],
      &quot;value&quot;: {
        &quot;id&quot;: &quot;ir_010&quot;,
        &quot;opcode&quot;: &quot;return&quot;,
        &quot;inputs&quot;: [],
        &quot;outputs&quot;: [],
        &quot;constraints&quot;: [],
        &quot;metadata&quot;: {},
        &quot;draft_instruction_id&quot;: &quot;finish&quot;
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_7bfa44aa9c7002279e0f&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005/instructions/1/constraints&quot;,
      &quot;kind&quot;: &quot;constraints&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;,
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
    &quot;target_be9a7a325c71903572d4&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005/instructions/1/draft_instruction_id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;,
        &quot;instructions&quot;,
        1,
        &quot;draft_instruction_id&quot;
      ],
      &quot;value&quot;: &quot;finish&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_6cce2b86629fdaf43a62&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005/instructions/1/id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;,
        &quot;instructions&quot;,
        1,
        &quot;id&quot;
      ],
      &quot;value&quot;: &quot;ir_010&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_b85d336e878a7997db0e&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005/instructions/1/inputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;,
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
    &quot;target_41c4a925b80b20ddbab5&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005/instructions/1/metadata&quot;,
      &quot;kind&quot;: &quot;metadata&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;,
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
    &quot;target_da911f66d018241d2018&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005/instructions/1/opcode&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;,
        &quot;instructions&quot;,
        1,
        &quot;opcode&quot;
      ],
      &quot;value&quot;: &quot;return&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: []
    },
    &quot;target_399d65c525701ef5cf51&quot;: {
      &quot;pointer&quot;: &quot;/blocks/block_005/instructions/1/outputs&quot;,
      &quot;kind&quot;: &quot;container&quot;,
      &quot;block_id&quot;: &quot;block_005&quot;,
      &quot;instruction_id&quot;: &quot;ir_010&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;blocks&quot;,
        &quot;block_005&quot;,
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
    &quot;target_a7022b2025864a4aee8e&quot;: {
      &quot;pointer&quot;: &quot;/constraints&quot;,
      &quot;kind&quot;: &quot;constraints&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;constraints&quot;
      ],
      &quot;value&quot;: [
        &quot;整份流程禁止将 access_token 字段发送给任何接收对象。&quot;,
        &quot;字段取值要求不包含摘要生成、内容改写或额外格式转换。&quot;
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
      &quot;value&quot;: &quot;整份流程禁止将 access_token 字段发送给任何接收对象。&quot;,
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
      &quot;value&quot;: &quot;字段取值要求不包含摘要生成、内容改写或额外格式转换。&quot;,
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
        },
        {
          &quot;source_block_id&quot;: &quot;block_004&quot;,
          &quot;target_block_id&quot;: &quot;block_005&quot;,
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
      &quot;instruction_id&quot;: &quot;ir_004&quot;
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
      &quot;instruction_id&quot;: &quot;ir_004&quot;
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
      &quot;instruction_id&quot;: &quot;ir_004&quot;
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
      &quot;instruction_id&quot;: &quot;ir_004&quot;
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
      &quot;instruction_id&quot;: &quot;ir_006&quot;
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
      &quot;instruction_id&quot;: &quot;ir_006&quot;
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
      &quot;instruction_id&quot;: &quot;ir_006&quot;
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
      &quot;instruction_id&quot;: &quot;ir_006&quot;
    },
    &quot;target_62a06507ca1cf66ff907&quot;: {
      &quot;pointer&quot;: &quot;/edges/3&quot;,
      &quot;kind&quot;: &quot;edge&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;edges&quot;,
        3
      ],
      &quot;value&quot;: {
        &quot;source_block_id&quot;: &quot;block_004&quot;,
        &quot;target_block_id&quot;: &quot;block_005&quot;,
        &quot;condition_text&quot;: null
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: true,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;instruction_id&quot;: &quot;ir_008&quot;
    },
    &quot;target_036ff2b4d34da3cdec9d&quot;: {
      &quot;pointer&quot;: &quot;/edges/3/condition_text&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;edges&quot;,
        3,
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
    &quot;target_fbe441da4c8333baff97&quot;: {
      &quot;pointer&quot;: &quot;/edges/3/source_block_id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;edges&quot;,
        3,
        &quot;source_block_id&quot;
      ],
      &quot;value&quot;: &quot;block_004&quot;,
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 0,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;instruction_id&quot;: &quot;ir_008&quot;
    },
    &quot;target_7047db27fbad811a8ead&quot;: {
      &quot;pointer&quot;: &quot;/edges/3/target_block_id&quot;,
      &quot;kind&quot;: &quot;field&quot;,
      &quot;domain&quot;: &quot;cfg&quot;,
      &quot;raw_path&quot;: [
        &quot;edges&quot;,
        3,
        &quot;target_block_id&quot;
      ],
      &quot;value&quot;: &quot;block_005&quot;,
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
                    &quot;ref_id&quot;: &quot;src_003&quot;,
                    &quot;quote&quot;: &quot;读取用户提供的 events.json&quot;,
                    &quot;reason&quot;: &quot;读取对象是源文指定的用户提供文件，目标值为其内容符号值。&quot;
                  },
                  {
                    &quot;basis&quot;: &quot;execution_model&quot;,
                    &quot;ref_id&quot;: &quot;EM01&quot;,
                    &quot;quote&quot;: &quot;Preserve the related source whole as a possible acquisition scope unless an explicit interface or mechanism restricts the read or returned content&quot;,
                    &quot;reason&quot;: &quot;没有显式接口或机制限制读取或返回内容，按 EM01 保留该文件整体为可能的获取范围，不假设键级读取。&quot;
                  }
                ],
                &quot;op&quot;: &quot;read&quot;,
                &quot;location&quot;: &quot;loc_events_file&quot;,
                &quot;output&quot;: &quot;events_content&quot;
              }
            ]
          }
        ],
        &quot;returns&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;quote&quot;: &quot;读取用户提供的 events.json&quot;,
            &quot;reason&quot;: &quot;源文只规定读取该文件；未规定模型处理，也未规定本地隔离执行及其限定回传边界，因此按默认模式声明该处理边界。&quot;
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;ref_id&quot;: &quot;EM05&quot;,
            &quot;quote&quot;: &quot;Contract defaults may supply possible analysis events for an existing action&quot;,
            &quot;reason&quot;: &quot;对已存在的读取动作，默认规则只提供可能的分析事件，不虚构额外的获取或保护动作；获取版本的后续观察由编译器按模式编译。&quot;
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
                &quot;ref_id&quot;: &quot;src_003&quot;,
                &quot;quote&quot;: &quot;读取用户提供的 events.json&quot;,
                &quot;reason&quot;: &quot;读取对象是源文指定的用户提供文件，目标值为其内容符号值。&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;ref_id&quot;: &quot;EM01&quot;,
                &quot;quote&quot;: &quot;Preserve the related source whole as a possible acquisition scope unless an explicit interface or mechanism restricts the read or returned content&quot;,
                &quot;reason&quot;: &quot;没有显式接口或机制限制读取或返回内容，按 EM01 保留该文件整体为可能的获取范围，不假设键级读取。&quot;
              }
            ],
            &quot;op&quot;: &quot;read&quot;,
            &quot;location&quot;: &quot;loc_events_file&quot;,
            &quot;output&quot;: &quot;events_content&quot;
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
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;quote&quot;: &quot;读取用户提供的 events.json&quot;,
            &quot;reason&quot;: &quot;读取对象是源文指定的用户提供文件，目标值为其内容符号值。&quot;
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;ref_id&quot;: &quot;EM01&quot;,
            &quot;quote&quot;: &quot;Preserve the related source whole as a possible acquisition scope unless an explicit interface or mechanism restricts the read or returned content&quot;,
            &quot;reason&quot;: &quot;没有显式接口或机制限制读取或返回内容，按 EM01 保留该文件整体为可能的获取范围，不假设键级读取。&quot;
          }
        ],
        &quot;op&quot;: &quot;read&quot;,
        &quot;location&quot;: &quot;loc_events_file&quot;,
        &quot;output&quot;: &quot;events_content&quot;
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
      &quot;value&quot;: &quot;events_content&quot;,
      &quot;available_locals&quot;: [
        &quot;events_content&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;events_content&quot;
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
        &quot;name&quot;: &quot;events_content&quot;
      },
      &quot;available_locals&quot;: [
        &quot;events_content&quot;
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
        &quot;name&quot;: &quot;events_content&quot;
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
                    &quot;ref_id&quot;: &quot;src_003&quot;,
                    &quot;quote&quot;: &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;,
                    &quot;reason&quot;: &quot;谓词取自源文条件；选中的记录元素保持原样，未选中的元素保持排除，未改写任何记录内容。&quot;
                  },
                  {
                    &quot;basis&quot;: &quot;source&quot;,
                    &quot;ref_id&quot;: &quot;src_003&quot;,
                    &quot;quote&quot;: &quot;urgent 为 true 只豁免数值门槛，不豁免 opted_out 的限制。&quot;,
                    &quot;reason&quot;: &quot;说明谓词中 opted_out 条件与 urgent/value 门槛的关系：urgent 不豁免 opted_out，条件保持合取。&quot;
                  },
                  {
                    &quot;basis&quot;: &quot;execution_model&quot;,
                    &quot;ref_id&quot;: &quot;EM11&quot;,
                    &quot;quote&quot;: &quot;filter_items preserves selected input elements unchanged under its recorded predicate&quot;,
                    &quot;reason&quot;: &quot;按 EM11 用 filter_items 表示元素筛选，静态分析只记录谓词而不执行它。&quot;
                  }
                ],
                &quot;op&quot;: &quot;filter_items&quot;,
                &quot;input&quot;: {
                  &quot;kind&quot;: &quot;input&quot;,
                  &quot;index&quot;: 0
                },
                &quot;predicate&quot;: &quot;opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100&quot;,
                &quot;output&quot;: &quot;selected_records&quot;
              }
            ]
          }
        ],
        &quot;returns&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;quote&quot;: &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;,
            &quot;reason&quot;: &quot;源文给出显式逐条筛选条件且不要求改写记录；未规定模型处理或本地隔离与限定回传，因此按默认模式。&quot;
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;ref_id&quot;: &quot;EM05&quot;,
            &quot;quote&quot;: &quot;Contract defaults may supply possible analysis events for an existing action&quot;,
            &quot;reason&quot;: &quot;默认规则只对已存在动作提供可能的分析事件，不把筛选谓词变成额外的保护动作。&quot;
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
                &quot;ref_id&quot;: &quot;src_003&quot;,
                &quot;quote&quot;: &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;,
                &quot;reason&quot;: &quot;谓词取自源文条件；选中的记录元素保持原样，未选中的元素保持排除，未改写任何记录内容。&quot;
              },
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;,
                &quot;quote&quot;: &quot;urgent 为 true 只豁免数值门槛，不豁免 opted_out 的限制。&quot;,
                &quot;reason&quot;: &quot;说明谓词中 opted_out 条件与 urgent/value 门槛的关系：urgent 不豁免 opted_out，条件保持合取。&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;ref_id&quot;: &quot;EM11&quot;,
                &quot;quote&quot;: &quot;filter_items preserves selected input elements unchanged under its recorded predicate&quot;,
                &quot;reason&quot;: &quot;按 EM11 用 filter_items 表示元素筛选，静态分析只记录谓词而不执行它。&quot;
              }
            ],
            &quot;op&quot;: &quot;filter_items&quot;,
            &quot;input&quot;: {
              &quot;kind&quot;: &quot;input&quot;,
              &quot;index&quot;: 0
            },
            &quot;predicate&quot;: &quot;opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100&quot;,
            &quot;output&quot;: &quot;selected_records&quot;
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
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;quote&quot;: &quot;仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。&quot;,
            &quot;reason&quot;: &quot;谓词取自源文条件；选中的记录元素保持原样，未选中的元素保持排除，未改写任何记录内容。&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;quote&quot;: &quot;urgent 为 true 只豁免数值门槛，不豁免 opted_out 的限制。&quot;,
            &quot;reason&quot;: &quot;说明谓词中 opted_out 条件与 urgent/value 门槛的关系：urgent 不豁免 opted_out，条件保持合取。&quot;
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;ref_id&quot;: &quot;EM11&quot;,
            &quot;quote&quot;: &quot;filter_items preserves selected input elements unchanged under its recorded predicate&quot;,
            &quot;reason&quot;: &quot;按 EM11 用 filter_items 表示元素筛选，静态分析只记录谓词而不执行它。&quot;
          }
        ],
        &quot;op&quot;: &quot;filter_items&quot;,
        &quot;input&quot;: {
          &quot;kind&quot;: &quot;input&quot;,
          &quot;index&quot;: 0
        },
        &quot;predicate&quot;: &quot;opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100&quot;,
        &quot;output&quot;: &quot;selected_records&quot;
      },
      &quot;available_locals&quot;: [],
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
      &quot;value&quot;: &quot;selected_records&quot;,
      &quot;available_locals&quot;: [
        &quot;selected_records&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;selected_records&quot;
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
        &quot;name&quot;: &quot;selected_records&quot;
      },
      &quot;available_locals&quot;: [
        &quot;selected_records&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;output_index&quot;: 0,
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;selected_records&quot;
      },
      &quot;scope_path&quot;: null
    },
    &quot;demand_target_9a2d9bbed999b0627aa5&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;for_each&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_005/events/0&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;for_each&quot;,
        &quot;collection&quot;: {
          &quot;kind&quot;: &quot;input&quot;,
          &quot;index&quot;: 1
        },
        &quot;item&quot;: &quot;event_record&quot;,
        &quot;body&quot;: [
          {
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
                        &quot;ref_id&quot;: &quot;src_003&quot;,
                        &quot;quote&quot;: &quot;接收对象取该记录的 recipient 字段&quot;,
                        &quot;reason&quot;: &quot;显式选出该记录的 recipient 字段并保持原值，作为接收对象参数。&quot;
                      }
                    ],
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;input&quot;: {
                      &quot;kind&quot;: &quot;local&quot;,
                      &quot;name&quot;: &quot;event_record&quot;
                    },
                    &quot;path&quot;: [
                      &quot;recipient&quot;
                    ],
                    &quot;output&quot;: &quot;recipient_value&quot;
                  },
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;,
                        &quot;quote&quot;: &quot;notify.send 的 body 参数直接取该记录的 summary 字段原值。&quot;,
                        &quot;reason&quot;: &quot;显式选出该记录的 summary 字段原值作为 body 参数，不做摘要或改写。&quot;
                      }
                    ],
                    &quot;op&quot;: &quot;select_part&quot;,
                    &quot;input&quot;: {
                      &quot;kind&quot;: &quot;local&quot;,
                      &quot;name&quot;: &quot;event_record&quot;
                    },
                    &quot;path&quot;: [
                      &quot;summary&quot;
                    ],
                    &quot;output&quot;: &quot;summary_value&quot;
                  }
                ]
              },
              {
                &quot;effect_index&quot;: null,
                &quot;atomic_ops&quot;: [
                  {
                    &quot;evidences&quot;: [
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;,
                        &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
                        &quot;reason&quot;: &quot;实际请求参数按同一记录的接收对象与正文顺序投递；选取结果先定义、投递再使用，支持固定先后顺序。&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;execution_model&quot;,
                        &quot;ref_id&quot;: &quot;EM13&quot;,
                        &quot;quote&quot;: &quot;A tool delivery with no established network effect is a null-effect deliver to a tool location&quot;,
                        &quot;reason&quot;: &quot;源文只有工具调用及参数，没有网络传输机制证据，因此不记 net_send，而以工具位置的零效应 deliver 表示实际请求参数投递。&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;source&quot;,
                        &quot;ref_id&quot;: &quot;src_003&quot;,
                        &quot;quote&quot;: &quot;整份流程禁止将 access_token 字段发送给任何接收对象。&quot;,
                        &quot;reason&quot;: &quot;投递输入严格为所选 recipient_value 与 summary_value 两个符号值，未把 access_token 字段纳入请求参数。&quot;
                      },
                      {
                        &quot;basis&quot;: &quot;execution_model&quot;,
                        &quot;ref_id&quot;: &quot;EM05&quot;,
                        &quot;quote&quot;: &quot;Preserve explicit restrictions without inventing protective actions to satisfy them&quot;,
                        &quot;reason&quot;: &quot;保留源文禁止性约束，但不因此虚构额外过滤或脱敏动作；投递参数即实际选取字段。&quot;
                      }
                    ],
                    &quot;op&quot;: &quot;deliver&quot;,
                    &quot;inputs&quot;: [
                      {
                        &quot;kind&quot;: &quot;local&quot;,
                        &quot;name&quot;: &quot;recipient_value&quot;
                      },
                      {
                        &quot;kind&quot;: &quot;local&quot;,
                        &quot;name&quot;: &quot;summary_value&quot;
                      }
                    ],
                    &quot;target&quot;: &quot;loc_notify_send&quot;
                  }
                ]
              }
            ],
            &quot;returns&quot;: [],
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;,
                &quot;quote&quot;: &quot;notify.send 的 body 参数直接取该记录的 summary 字段原值。&quot;,
                &quot;reason&quot;: &quot;逐条记录选取字段构造请求参数且保持原值，没有摘要生成或改写；源文未规定模型处理或本地隔离与限定回传，因此按默认模式。&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;ref_id&quot;: &quot;EM05&quot;,
                &quot;quote&quot;: &quot;Contract defaults may supply possible analysis events for an existing action&quot;,
                &quot;reason&quot;: &quot;默认规则只对已有工具调用动作提供可能的分析事件，不虚构新的外部来源或保护动作。&quot;
              }
            ]
          }
        ],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send&quot;,
            &quot;reason&quot;: &quot;源文规定对已选记录逐条调用一次，按逐元素作用域建模，并在每次处理中保持同一记录的元素身份。&quot;
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;ref_id&quot;: &quot;EM11&quot;,
            &quot;quote&quot;: &quot;for_each introduces one shared element binding per possible element so selections and delivery parameters retain that element&#x27;s identity&quot;,
            &quot;reason&quot;: &quot;用共享元素绑定保证接收对象与正文选择来自同一条记录；这是分析作用域，不是虚构的 CFG 循环或测量出的调用次数。&quot;
          }
        ]
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;scope_path&quot;: [
        &quot;events&quot;,
        0
      ]
    },
    &quot;demand_target_6de2bee99efb94b8e829&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;collection&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;collection&quot;
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_005/events/0/collection&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;input&quot;,
        &quot;index&quot;: 1
      },
      &quot;available_locals&quot;: [],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;input&quot;,
        &quot;index&quot;: 1
      },
      &quot;scope_path&quot;: [
        &quot;events&quot;,
        0
      ]
    },
    &quot;demand_target_4d34a59fd845f757de56&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;element&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;item&quot;
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_005/events/0/item&quot;,
      &quot;value&quot;: &quot;event_record&quot;,
      &quot;available_locals&quot;: [
        &quot;event_record&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;event_record&quot;
      },
      &quot;scope_path&quot;: [
        &quot;events&quot;,
        0
      ]
    },
    &quot;demand_target_0ae26fcc7d04ed6c3631&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;processing&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_005/events/0/body/0&quot;,
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
                    &quot;ref_id&quot;: &quot;src_003&quot;,
                    &quot;quote&quot;: &quot;接收对象取该记录的 recipient 字段&quot;,
                    &quot;reason&quot;: &quot;显式选出该记录的 recipient 字段并保持原值，作为接收对象参数。&quot;
                  }
                ],
                &quot;op&quot;: &quot;select_part&quot;,
                &quot;input&quot;: {
                  &quot;kind&quot;: &quot;local&quot;,
                  &quot;name&quot;: &quot;event_record&quot;
                },
                &quot;path&quot;: [
                  &quot;recipient&quot;
                ],
                &quot;output&quot;: &quot;recipient_value&quot;
              },
              {
                &quot;evidences&quot;: [
                  {
                    &quot;basis&quot;: &quot;source&quot;,
                    &quot;ref_id&quot;: &quot;src_003&quot;,
                    &quot;quote&quot;: &quot;notify.send 的 body 参数直接取该记录的 summary 字段原值。&quot;,
                    &quot;reason&quot;: &quot;显式选出该记录的 summary 字段原值作为 body 参数，不做摘要或改写。&quot;
                  }
                ],
                &quot;op&quot;: &quot;select_part&quot;,
                &quot;input&quot;: {
                  &quot;kind&quot;: &quot;local&quot;,
                  &quot;name&quot;: &quot;event_record&quot;
                },
                &quot;path&quot;: [
                  &quot;summary&quot;
                ],
                &quot;output&quot;: &quot;summary_value&quot;
              }
            ]
          },
          {
            &quot;effect_index&quot;: null,
            &quot;atomic_ops&quot;: [
              {
                &quot;evidences&quot;: [
                  {
                    &quot;basis&quot;: &quot;source&quot;,
                    &quot;ref_id&quot;: &quot;src_003&quot;,
                    &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
                    &quot;reason&quot;: &quot;实际请求参数按同一记录的接收对象与正文顺序投递；选取结果先定义、投递再使用，支持固定先后顺序。&quot;
                  },
                  {
                    &quot;basis&quot;: &quot;execution_model&quot;,
                    &quot;ref_id&quot;: &quot;EM13&quot;,
                    &quot;quote&quot;: &quot;A tool delivery with no established network effect is a null-effect deliver to a tool location&quot;,
                    &quot;reason&quot;: &quot;源文只有工具调用及参数，没有网络传输机制证据，因此不记 net_send，而以工具位置的零效应 deliver 表示实际请求参数投递。&quot;
                  },
                  {
                    &quot;basis&quot;: &quot;source&quot;,
                    &quot;ref_id&quot;: &quot;src_003&quot;,
                    &quot;quote&quot;: &quot;整份流程禁止将 access_token 字段发送给任何接收对象。&quot;,
                    &quot;reason&quot;: &quot;投递输入严格为所选 recipient_value 与 summary_value 两个符号值，未把 access_token 字段纳入请求参数。&quot;
                  },
                  {
                    &quot;basis&quot;: &quot;execution_model&quot;,
                    &quot;ref_id&quot;: &quot;EM05&quot;,
                    &quot;quote&quot;: &quot;Preserve explicit restrictions without inventing protective actions to satisfy them&quot;,
                    &quot;reason&quot;: &quot;保留源文禁止性约束，但不因此虚构额外过滤或脱敏动作；投递参数即实际选取字段。&quot;
                  }
                ],
                &quot;op&quot;: &quot;deliver&quot;,
                &quot;inputs&quot;: [
                  {
                    &quot;kind&quot;: &quot;local&quot;,
                    &quot;name&quot;: &quot;recipient_value&quot;
                  },
                  {
                    &quot;kind&quot;: &quot;local&quot;,
                    &quot;name&quot;: &quot;summary_value&quot;
                  }
                ],
                &quot;target&quot;: &quot;loc_notify_send&quot;
              }
            ]
          }
        ],
        &quot;returns&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;quote&quot;: &quot;notify.send 的 body 参数直接取该记录的 summary 字段原值。&quot;,
            &quot;reason&quot;: &quot;逐条记录选取字段构造请求参数且保持原值，没有摘要生成或改写；源文未规定模型处理或本地隔离与限定回传，因此按默认模式。&quot;
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;ref_id&quot;: &quot;EM05&quot;,
            &quot;quote&quot;: &quot;Contract defaults may supply possible analysis events for an existing action&quot;,
            &quot;reason&quot;: &quot;默认规则只对已有工具调用动作提供可能的分析事件，不虚构新的外部来源或保护动作。&quot;
          }
        ]
      },
      &quot;available_locals&quot;: [
        &quot;event_record&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0
      ],
      &quot;scope_path&quot;: [
        &quot;events&quot;,
        0
      ]
    },
    &quot;demand_target_2c85c9728db1954aac32&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;effect&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0,
        &quot;events&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_005/events/0/body/0/events/0&quot;,
      &quot;value&quot;: {
        &quot;effect_index&quot;: 0,
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;,
                &quot;quote&quot;: &quot;接收对象取该记录的 recipient 字段&quot;,
                &quot;reason&quot;: &quot;显式选出该记录的 recipient 字段并保持原值，作为接收对象参数。&quot;
              }
            ],
            &quot;op&quot;: &quot;select_part&quot;,
            &quot;input&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;event_record&quot;
            },
            &quot;path&quot;: [
              &quot;recipient&quot;
            ],
            &quot;output&quot;: &quot;recipient_value&quot;
          },
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;,
                &quot;quote&quot;: &quot;notify.send 的 body 参数直接取该记录的 summary 字段原值。&quot;,
                &quot;reason&quot;: &quot;显式选出该记录的 summary 字段原值作为 body 参数，不做摘要或改写。&quot;
              }
            ],
            &quot;op&quot;: &quot;select_part&quot;,
            &quot;input&quot;: {
              &quot;kind&quot;: &quot;local&quot;,
              &quot;name&quot;: &quot;event_record&quot;
            },
            &quot;path&quot;: [
              &quot;summary&quot;
            ],
            &quot;output&quot;: &quot;summary_value&quot;
          }
        ]
      },
      &quot;available_locals&quot;: [
        &quot;event_record&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0
      ],
      &quot;scope_path&quot;: [
        &quot;events&quot;,
        0
      ]
    },
    &quot;demand_target_a5ec6cd6372eb6847911&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;operation&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_005/events/0/body/0/events/0/atomic_ops/0&quot;,
      &quot;value&quot;: {
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;quote&quot;: &quot;接收对象取该记录的 recipient 字段&quot;,
            &quot;reason&quot;: &quot;显式选出该记录的 recipient 字段并保持原值，作为接收对象参数。&quot;
          }
        ],
        &quot;op&quot;: &quot;select_part&quot;,
        &quot;input&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;event_record&quot;
        },
        &quot;path&quot;: [
          &quot;recipient&quot;
        ],
        &quot;output&quot;: &quot;recipient_value&quot;
      },
      &quot;available_locals&quot;: [
        &quot;event_record&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;declared_refs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;event_record&quot;
        }
      ],
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0
      ],
      &quot;scope_path&quot;: [
        &quot;events&quot;,
        0
      ]
    },
    &quot;demand_target_2ad60ab1ca06130679ed&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;input_use&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0,
        &quot;uses&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_005/events/0/body/0/events/0/atomic_ops/0/uses/0&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;event_record&quot;
      },
      &quot;available_locals&quot;: [
        &quot;event_record&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;slot&quot;: 0,
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;event_record&quot;
      },
      &quot;role&quot;: &quot;value&quot;,
      &quot;when&quot;: null,
      &quot;member_index&quot;: null,
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0
      ],
      &quot;scope_path&quot;: [
        &quot;events&quot;,
        0
      ]
    },
    &quot;demand_target_302c45de373f6f9a0d6a&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;local_output&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0,
        &quot;output&quot;
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_005/events/0/body/0/events/0/atomic_ops/0/output&quot;,
      &quot;value&quot;: &quot;recipient_value&quot;,
      &quot;available_locals&quot;: [
        &quot;event_record&quot;,
        &quot;recipient_value&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;recipient_value&quot;
      },
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0
      ],
      &quot;scope_path&quot;: [
        &quot;events&quot;,
        0
      ]
    },
    &quot;demand_target_cdd7aba10fcb1cbef7f2&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;operation&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        1
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_005/events/0/body/0/events/0/atomic_ops/1&quot;,
      &quot;value&quot;: {
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;quote&quot;: &quot;notify.send 的 body 参数直接取该记录的 summary 字段原值。&quot;,
            &quot;reason&quot;: &quot;显式选出该记录的 summary 字段原值作为 body 参数，不做摘要或改写。&quot;
          }
        ],
        &quot;op&quot;: &quot;select_part&quot;,
        &quot;input&quot;: {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;event_record&quot;
        },
        &quot;path&quot;: [
          &quot;summary&quot;
        ],
        &quot;output&quot;: &quot;summary_value&quot;
      },
      &quot;available_locals&quot;: [
        &quot;event_record&quot;,
        &quot;recipient_value&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;declared_refs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;event_record&quot;
        }
      ],
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        1
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0
      ],
      &quot;scope_path&quot;: [
        &quot;events&quot;,
        0
      ]
    },
    &quot;demand_target_1687af35b79bf4a5579e&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;input_use&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        1,
        &quot;uses&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_005/events/0/body/0/events/0/atomic_ops/1/uses/0&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;event_record&quot;
      },
      &quot;available_locals&quot;: [
        &quot;event_record&quot;,
        &quot;recipient_value&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;slot&quot;: 0,
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;event_record&quot;
      },
      &quot;role&quot;: &quot;value&quot;,
      &quot;when&quot;: null,
      &quot;member_index&quot;: null,
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        1
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0
      ],
      &quot;scope_path&quot;: [
        &quot;events&quot;,
        0
      ]
    },
    &quot;demand_target_554abcc935b4cc8c98ca&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;local_output&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        1,
        &quot;output&quot;
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_005/events/0/body/0/events/0/atomic_ops/1/output&quot;,
      &quot;value&quot;: &quot;summary_value&quot;,
      &quot;available_locals&quot;: [
        &quot;event_record&quot;,
        &quot;recipient_value&quot;,
        &quot;summary_value&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;summary_value&quot;
      },
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0,
        &quot;events&quot;,
        0,
        &quot;atomic_ops&quot;,
        1
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0
      ],
      &quot;scope_path&quot;: [
        &quot;events&quot;,
        0
      ]
    },
    &quot;demand_target_e9ae4dadc14f9c780bb5&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;effect&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0,
        &quot;events&quot;,
        1
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_005/events/0/body/0/events/1&quot;,
      &quot;value&quot;: {
        &quot;effect_index&quot;: null,
        &quot;atomic_ops&quot;: [
          {
            &quot;evidences&quot;: [
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;,
                &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
                &quot;reason&quot;: &quot;实际请求参数按同一记录的接收对象与正文顺序投递；选取结果先定义、投递再使用，支持固定先后顺序。&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;ref_id&quot;: &quot;EM13&quot;,
                &quot;quote&quot;: &quot;A tool delivery with no established network effect is a null-effect deliver to a tool location&quot;,
                &quot;reason&quot;: &quot;源文只有工具调用及参数，没有网络传输机制证据，因此不记 net_send，而以工具位置的零效应 deliver 表示实际请求参数投递。&quot;
              },
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;,
                &quot;quote&quot;: &quot;整份流程禁止将 access_token 字段发送给任何接收对象。&quot;,
                &quot;reason&quot;: &quot;投递输入严格为所选 recipient_value 与 summary_value 两个符号值，未把 access_token 字段纳入请求参数。&quot;
              },
              {
                &quot;basis&quot;: &quot;execution_model&quot;,
                &quot;ref_id&quot;: &quot;EM05&quot;,
                &quot;quote&quot;: &quot;Preserve explicit restrictions without inventing protective actions to satisfy them&quot;,
                &quot;reason&quot;: &quot;保留源文禁止性约束，但不因此虚构额外过滤或脱敏动作；投递参数即实际选取字段。&quot;
              }
            ],
            &quot;op&quot;: &quot;deliver&quot;,
            &quot;inputs&quot;: [
              {
                &quot;kind&quot;: &quot;local&quot;,
                &quot;name&quot;: &quot;recipient_value&quot;
              },
              {
                &quot;kind&quot;: &quot;local&quot;,
                &quot;name&quot;: &quot;summary_value&quot;
              }
            ],
            &quot;target&quot;: &quot;loc_notify_send&quot;
          }
        ]
      },
      &quot;available_locals&quot;: [
        &quot;event_record&quot;,
        &quot;recipient_value&quot;,
        &quot;summary_value&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0
      ],
      &quot;scope_path&quot;: [
        &quot;events&quot;,
        0
      ]
    },
    &quot;demand_target_69f18d1add9cc9406637&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;operation&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0,
        &quot;events&quot;,
        1,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_005/events/0/body/0/events/1/atomic_ops/0&quot;,
      &quot;value&quot;: {
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;quote&quot;: &quot;对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。&quot;,
            &quot;reason&quot;: &quot;实际请求参数按同一记录的接收对象与正文顺序投递；选取结果先定义、投递再使用，支持固定先后顺序。&quot;
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;ref_id&quot;: &quot;EM13&quot;,
            &quot;quote&quot;: &quot;A tool delivery with no established network effect is a null-effect deliver to a tool location&quot;,
            &quot;reason&quot;: &quot;源文只有工具调用及参数，没有网络传输机制证据，因此不记 net_send，而以工具位置的零效应 deliver 表示实际请求参数投递。&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;quote&quot;: &quot;整份流程禁止将 access_token 字段发送给任何接收对象。&quot;,
            &quot;reason&quot;: &quot;投递输入严格为所选 recipient_value 与 summary_value 两个符号值，未把 access_token 字段纳入请求参数。&quot;
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;ref_id&quot;: &quot;EM05&quot;,
            &quot;quote&quot;: &quot;Preserve explicit restrictions without inventing protective actions to satisfy them&quot;,
            &quot;reason&quot;: &quot;保留源文禁止性约束，但不因此虚构额外过滤或脱敏动作；投递参数即实际选取字段。&quot;
          }
        ],
        &quot;op&quot;: &quot;deliver&quot;,
        &quot;inputs&quot;: [
          {
            &quot;kind&quot;: &quot;local&quot;,
            &quot;name&quot;: &quot;recipient_value&quot;
          },
          {
            &quot;kind&quot;: &quot;local&quot;,
            &quot;name&quot;: &quot;summary_value&quot;
          }
        ],
        &quot;target&quot;: &quot;loc_notify_send&quot;
      },
      &quot;available_locals&quot;: [
        &quot;event_record&quot;,
        &quot;recipient_value&quot;,
        &quot;summary_value&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;declared_refs&quot;: [
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;recipient_value&quot;
        },
        {
          &quot;kind&quot;: &quot;local&quot;,
          &quot;name&quot;: &quot;summary_value&quot;
        }
      ],
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0,
        &quot;events&quot;,
        1,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0
      ],
      &quot;scope_path&quot;: [
        &quot;events&quot;,
        0
      ]
    },
    &quot;demand_target_0a40de71bf95206e00ec&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;input_use&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0,
        &quot;events&quot;,
        1,
        &quot;atomic_ops&quot;,
        0,
        &quot;uses&quot;,
        0
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_005/events/0/body/0/events/1/atomic_ops/0/uses/0&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;recipient_value&quot;
      },
      &quot;available_locals&quot;: [
        &quot;event_record&quot;,
        &quot;recipient_value&quot;,
        &quot;summary_value&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;slot&quot;: 0,
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;recipient_value&quot;
      },
      &quot;role&quot;: &quot;value&quot;,
      &quot;when&quot;: null,
      &quot;member_index&quot;: null,
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0,
        &quot;events&quot;,
        1,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0
      ],
      &quot;scope_path&quot;: [
        &quot;events&quot;,
        0
      ]
    },
    &quot;demand_target_23fc3eb8e8393e5aead7&quot;: {
      &quot;domain&quot;: &quot;transfer&quot;,
      &quot;kind&quot;: &quot;input_use&quot;,
      &quot;instruction_id&quot;: &quot;ir_005&quot;,
      &quot;raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0,
        &quot;events&quot;,
        1,
        &quot;atomic_ops&quot;,
        0,
        &quot;uses&quot;,
        1
      ],
      &quot;pointer&quot;: &quot;/transfer_specs/ir_005/events/0/body/0/events/1/atomic_ops/0/uses/1&quot;,
      &quot;value&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;summary_value&quot;
      },
      &quot;available_locals&quot;: [
        &quot;event_record&quot;,
        &quot;recipient_value&quot;,
        &quot;summary_value&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 4,
      &quot;input_literals&quot;: {
        &quot;2&quot;: &quot;recipient&quot;,
        &quot;3&quot;: &quot;summary&quot;
      },
      &quot;resource_inputs&quot;: [
        0
      ],
      &quot;slot&quot;: 1,
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;summary_value&quot;
      },
      &quot;role&quot;: &quot;value&quot;,
      &quot;when&quot;: null,
      &quot;member_index&quot;: null,
      &quot;operation_raw_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0,
        &quot;events&quot;,
        1,
        &quot;atomic_ops&quot;,
        0
      ],
      &quot;segment_path&quot;: [
        &quot;events&quot;,
        0,
        &quot;body&quot;,
        0
      ],
      &quot;scope_path&quot;: [
        &quot;events&quot;,
        0
      ]
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
                    &quot;basis&quot;: &quot;cfg&quot;,
                    &quot;ref_id&quot;: &quot;g_0027&quot;,
                    &quot;quote&quot;: &quot;count_processed_records&quot;,
                    &quot;reason&quot;: &quot;指令对输入集合计数，结果由该集合派生；计数为不透明计算，只声明依赖。&quot;
                  },
                  {
                    &quot;basis&quot;: &quot;source&quot;,
                    &quot;ref_id&quot;: &quot;src_003&quot;,
                    &quot;quote&quot;: &quot;处理条数&quot;,
                    &quot;reason&quot;: &quot;源文要求得到处理条数，来源为该流程已选中并处理的记录集合。&quot;
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
                &quot;output&quot;: &quot;processed_count&quot;
              }
            ]
          }
        ],
        &quot;returns&quot;: [],
        &quot;evidences&quot;: [
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;quote&quot;: &quot;将处理条数写入本地 count.txt&quot;,
            &quot;reason&quot;: &quot;源文要求统计处理条数；未规定模型处理或本地隔离执行及限定回传，按默认模式。&quot;
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;ref_id&quot;: &quot;EM05&quot;,
            &quot;quote&quot;: &quot;Contract defaults may supply possible analysis events for an existing action&quot;,
            &quot;reason&quot;: &quot;默认规则只对已有计数动作给出可能的分析事件，不虚构额外外部来源。&quot;
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
                &quot;basis&quot;: &quot;cfg&quot;,
                &quot;ref_id&quot;: &quot;g_0027&quot;,
                &quot;quote&quot;: &quot;count_processed_records&quot;,
                &quot;reason&quot;: &quot;指令对输入集合计数，结果由该集合派生；计数为不透明计算，只声明依赖。&quot;
              },
              {
                &quot;basis&quot;: &quot;source&quot;,
                &quot;ref_id&quot;: &quot;src_003&quot;,
                &quot;quote&quot;: &quot;处理条数&quot;,
                &quot;reason&quot;: &quot;源文要求得到处理条数，来源为该流程已选中并处理的记录集合。&quot;
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
            &quot;output&quot;: &quot;processed_count&quot;
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
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;ref_id&quot;: &quot;g_0027&quot;,
            &quot;quote&quot;: &quot;count_processed_records&quot;,
            &quot;reason&quot;: &quot;指令对输入集合计数，结果由该集合派生；计数为不透明计算，只声明依赖。&quot;
          },
          {
            &quot;basis&quot;: &quot;source&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;quote&quot;: &quot;处理条数&quot;,
            &quot;reason&quot;: &quot;源文要求得到处理条数，来源为该流程已选中并处理的记录集合。&quot;
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
        &quot;output&quot;: &quot;processed_count&quot;
      },
      &quot;available_locals&quot;: [],
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
      &quot;value&quot;: &quot;processed_count&quot;,
      &quot;available_locals&quot;: [
        &quot;processed_count&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;processed_count&quot;
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
        &quot;name&quot;: &quot;processed_count&quot;
      },
      &quot;available_locals&quot;: [
        &quot;processed_count&quot;
      ],
      &quot;supports_expression&quot;: false,
      &quot;input_count&quot;: 1,
      &quot;input_literals&quot;: {},
      &quot;resource_inputs&quot;: [],
      &quot;output_index&quot;: 0,
      &quot;ref&quot;: {
        &quot;kind&quot;: &quot;local&quot;,
        &quot;name&quot;: &quot;processed_count&quot;
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
                    &quot;ref_id&quot;: &quot;src_003&quot;,
                    &quot;quote&quot;: &quot;将处理条数写入本地 count.txt&quot;,
                    &quot;reason&quot;: &quot;写入目标为本地 count.txt，写入内容为当前指令的条数操作数；源文未说明追加语义，按一次写入（替换）表示；文件写入不自动附加 context_write。&quot;
                  },
                  {
                    &quot;basis&quot;: &quot;cfg&quot;,
                    &quot;ref_id&quot;: &quot;g_0033&quot;,
                    &quot;quote&quot;: &quot;write_file&quot;,
                    &quot;reason&quot;: &quot;CFG 操作码为 write_file，与源文写入步骤一致。&quot;
                  }
                ],
                &quot;op&quot;: &quot;write&quot;,
                &quot;target&quot;: &quot;loc_count_file&quot;,
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
            &quot;basis&quot;: &quot;source&quot;,
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;quote&quot;: &quot;将处理条数写入本地 count.txt&quot;,
            &quot;reason&quot;: &quot;源文规定把条数写入本地文件；未规定模型处理或本地隔离执行及限定回传，按默认模式。&quot;
          },
          {
            &quot;basis&quot;: &quot;execution_model&quot;,
            &quot;ref_id&quot;: &quot;EM05&quot;,
            &quot;quote&quot;: &quot;Contract defaults may supply possible analysis events for an existing action&quot;,
            &quot;reason&quot;: &quot;默认规则只对已有写入动作提供可能的分析事件，不虚构额外保护动作。&quot;
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
                &quot;ref_id&quot;: &quot;src_003&quot;,
                &quot;quote&quot;: &quot;将处理条数写入本地 count.txt&quot;,
                &quot;reason&quot;: &quot;写入目标为本地 count.txt，写入内容为当前指令的条数操作数；源文未说明追加语义，按一次写入（替换）表示；文件写入不自动附加 context_write。&quot;
              },
              {
                &quot;basis&quot;: &quot;cfg&quot;,
                &quot;ref_id&quot;: &quot;g_0033&quot;,
                &quot;quote&quot;: &quot;write_file&quot;,
                &quot;reason&quot;: &quot;CFG 操作码为 write_file，与源文写入步骤一致。&quot;
              }
            ],
            &quot;op&quot;: &quot;write&quot;,
            &quot;target&quot;: &quot;loc_count_file&quot;,
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
            &quot;ref_id&quot;: &quot;src_003&quot;,
            &quot;quote&quot;: &quot;将处理条数写入本地 count.txt&quot;,
            &quot;reason&quot;: &quot;写入目标为本地 count.txt，写入内容为当前指令的条数操作数；源文未说明追加语义，按一次写入（替换）表示；文件写入不自动附加 context_write。&quot;
          },
          {
            &quot;basis&quot;: &quot;cfg&quot;,
            &quot;ref_id&quot;: &quot;g_0033&quot;,
            &quot;quote&quot;: &quot;write_file&quot;,
            &quot;reason&quot;: &quot;CFG 操作码为 write_file，与源文写入步骤一致。&quot;
          }
        ],
        &quot;op&quot;: &quot;write&quot;,
        &quot;target&quot;: &quot;loc_count_file&quot;,
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
    }
  }
}</pre></details>
