# Sensitivity and sink-demand comparisons

Sensitivity coverage is limited to explicit declarations. Undeclared content is not proven non-sensitive. Comparisons apply to the recorded processing and task-demand rules, not to all possible implementations. A possible dependency is not evidence that sensitive plaintext is present.

**Status:** partial

**Candidate origin:** model\_annotation

Offline preparation; zero API calls.

**Declaration source:** accepted\_joint\_annotation

## Coverage

<pre>{
  &quot;declared_scopes&quot;: 0,
  &quot;declarations&quot;: 0,
  &quot;resolved_declarations&quot;: 0,
  &quot;sinks&quot;: 12,
  &quot;expected_sinks&quot;: 12,
  &quot;sensitivity_basis&quot;: &quot;declared_ranges_only&quot;,
  &quot;demand_status&quot;: &quot;partial&quot;
}</pre>

## Range comparisons

<pre>{
  &quot;excess_supported&quot;: 0,
  &quot;possible_excess&quot;: 0,
  &quot;no_excess_established&quot;: 0
}</pre>

These counts concern declared ranges, not unique leaks or measured events.

## Forward constraint checks

Constraints do not change actual propagation or create positive demands. Baseline findings remain visible independently of any local reduction. Satisfaction is limited to the supported static model.

<pre>{
  &quot;constraint_9009e15876bcfc82d8ad&quot;: {
    &quot;requirement_id&quot;: &quot;R2&quot;,
    &quot;raw_pointer&quot;: &quot;/realizations/1/constraints/0&quot;,
    &quot;kind&quot;: &quot;at_most&quot;,
    &quot;status&quot;: &quot;satisfied&quot;,
    &quot;operations&quot;: [
      &quot;op_ir_007:e0:a0&quot;,
      &quot;op_ir_007:e1:a0&quot;,
      &quot;op_ir_007:e2:a0&quot;,
      &quot;op_ir_007:e3:a0&quot;,
      &quot;op_ir_007:e4:a0&quot;,
      &quot;op_ir_007:e4:a1&quot;,
      &quot;op_ir_007:e5:a0&quot;
    ],
    &quot;reasons&quot;: [
      &quot;All supported task-entry behaviors satisfy this constraint within the declared static model.&quot;
    ],
    &quot;witness&quot;: [],
    &quot;structural&quot;: true
  },
  &quot;constraint_35e3a6a8eec50bad5a08&quot;: {
    &quot;requirement_id&quot;: &quot;R8&quot;,
    &quot;raw_pointer&quot;: &quot;/realizations/7/constraints/0&quot;,
    &quot;kind&quot;: &quot;requires_prior&quot;,
    &quot;status&quot;: &quot;satisfied&quot;,
    &quot;operations&quot;: [
      &quot;op_ir_007:e0:a0&quot;,
      &quot;op_ir_007:e1:a0&quot;,
      &quot;op_ir_007:e2:a0&quot;,
      &quot;op_ir_007:e3:a0&quot;,
      &quot;op_ir_007:e4:a0&quot;,
      &quot;op_ir_007:e4:a1&quot;,
      &quot;op_ir_007:e5:a0&quot;,
      &quot;op_ir_010:e0:a0&quot;
    ],
    &quot;reasons&quot;: [
      &quot;All supported task-entry behaviors satisfy this constraint within the declared static model.&quot;
    ],
    &quot;witness&quot;: [],
    &quot;structural&quot;: true
  }
}</pre>

## Task and demand basis

These front-end requirements drive preservation demands. Reference checks do not prove semantic support or completeness; current payload use is not a necessity argument.

### Task provenance

<pre>{
  &quot;kind&quot;: &quot;independent_task_run&quot;,
  &quot;task_sha256&quot;: &quot;b7d5394817bf20305abb5bd7a18bf975e5bf784a93eea05091a51969895675cb&quot;
}</pre>

Annotation acceptance and Task provenance are recorded separately; an assistant-authored fixture is not evidence of independent Task extraction performance.

<pre>{
  &quot;purpose&quot;: {
    &quot;text&quot;: &quot;Query an index once using a supplied request and preserve optional-parameter semantics.&quot;,
    &quot;evidences&quot;: [
      {
        &quot;file&quot;: &quot;skill/SKILL.md&quot;,
        &quot;start_line&quot;: 3,
        &quot;end_line&quot;: 3,
        &quot;reason&quot;: &quot;Declares the skill purpose: a one-time index query using a supplied request with preserved optional-parameter semantics.&quot;
      }
    ]
  },
  &quot;requirements&quot;: [
    {
      &quot;id&quot;: &quot;R1&quot;,
      &quot;text&quot;: &quot;Read the user-supplied request.json; it contains term and may contain from_date and limit.&quot;,
      &quot;evidences&quot;: [
        {
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;start_line&quot;: 5,
          &quot;end_line&quot;: 5,
          &quot;reason&quot;: &quot;Imperatively directs reading the supplied request and identifies the request fields that govern the search call.&quot;
        }
      ]
    },
    {
      &quot;id&quot;: &quot;R2&quot;,
      &quot;text&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
      &quot;evidences&quot;: [
        {
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;start_line&quot;: 7,
          &quot;end_line&quot;: 7,
          &quot;reason&quot;: &quot;States the exact call count, operation, and unchanged term argument in one sentence.&quot;
        }
      ]
    },
    {
      &quot;id&quot;: &quot;R3&quot;,
      &quot;text&quot;: &quot;When from_date is present in the request, pass its value unchanged as the from_date argument; the accepted format is YYYY-MM-DD.&quot;,
      &quot;evidences&quot;: [
        {
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;start_line&quot;: 10,
          &quot;end_line&quot;: 10,
          &quot;reason&quot;: &quot;Specifies the conditional from_date argument, its unchanged value, and accepted format.&quot;
        }
      ]
    },
    {
      &quot;id&quot;: &quot;R4&quot;,
      &quot;text&quot;: &quot;When from_date is missing from the request, omit the from_date argument from this same index.search call, applying query.yaml&#x27;s missing-argument setting.&quot;,
      &quot;evidences&quot;: [
        {
          &quot;file&quot;: &quot;skill/query.yaml&quot;,
          &quot;start_line&quot;: 2,
          &quot;end_line&quot;: 2,
          &quot;reason&quot;: &quot;Declares the missing from_date setting as omit.&quot;
        },
        {
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;start_line&quot;: 11,
          &quot;end_line&quot;: 11,
          &quot;reason&quot;: &quot;Requires omitting from_date when it is missing.&quot;
        },
        {
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;start_line&quot;: 15,
          &quot;end_line&quot;: 15,
          &quot;reason&quot;: &quot;Requires applying query.yaml missing-argument settings to the same search call.&quot;
        }
      ]
    },
    {
      &quot;id&quot;: &quot;R5&quot;,
      &quot;text&quot;: &quot;When limit is present in the request, pass its value unchanged as the limit argument.&quot;,
      &quot;evidences&quot;: [
        {
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;start_line&quot;: 12,
          &quot;end_line&quot;: 12,
          &quot;reason&quot;: &quot;Specifies the conditional limit argument and its unchanged value.&quot;
        }
      ]
    },
    {
      &quot;id&quot;: &quot;R6&quot;,
      &quot;text&quot;: &quot;When limit is missing from the request, omit the limit argument from this same index.search call, applying query.yaml&#x27;s missing-argument setting.&quot;,
      &quot;evidences&quot;: [
        {
          &quot;file&quot;: &quot;skill/query.yaml&quot;,
          &quot;start_line&quot;: 3,
          &quot;end_line&quot;: 3,
          &quot;reason&quot;: &quot;Declares the missing limit setting as omit.&quot;
        },
        {
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;start_line&quot;: 13,
          &quot;end_line&quot;: 13,
          &quot;reason&quot;: &quot;Requires omitting limit when it is missing.&quot;
        },
        {
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;start_line&quot;: 15,
          &quot;end_line&quot;: 15,
          &quot;reason&quot;: &quot;Requires applying query.yaml missing-argument settings to the same search call.&quot;
        }
      ]
    },
    {
      &quot;id&quot;: &quot;R7&quot;,
      &quot;text&quot;: &quot;Do not invoke index.delete anywhere in this workflow.&quot;,
      &quot;evidences&quot;: [
        {
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;start_line&quot;: 17,
          &quot;end_line&quot;: 17,
          &quot;reason&quot;: &quot;Explicitly prohibits invoking index.delete anywhere in the workflow.&quot;
        }
      ]
    },
    {
      &quot;id&quot;: &quot;R8&quot;,
      &quot;text&quot;: &quot;After the search, write the response&#x27;s total value to local count.txt.&quot;,
      &quot;evidences&quot;: [
        {
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;start_line&quot;: 21,
          &quot;end_line&quot;: 21,
          &quot;reason&quot;: &quot;Requires the post-search write of the response total to the specified local file.&quot;
        }
      ]
    },
    {
      &quot;id&quot;: &quot;R9&quot;,
      &quot;text&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
      &quot;evidences&quot;: [
        {
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;start_line&quot;: 23,
          &quot;end_line&quot;: 23,
          &quot;reason&quot;: &quot;Requires returning the response items value without change.&quot;
        }
      ]
    }
  ],
  &quot;source_accounting&quot;: [
    {
      &quot;file&quot;: &quot;skill/SKILL.md&quot;,
      &quot;start_line&quot;: 1,
      &quot;end_line&quot;: 1,
      &quot;disposition&quot;: &quot;not_applicable&quot;,
      &quot;requirement_ids&quot;: [],
      &quot;issue_ids&quot;: [],
      &quot;reason&quot;: &quot;Frontmatter opening delimiter; no task obligation.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/SKILL.md&quot;,
      &quot;start_line&quot;: 2,
      &quot;end_line&quot;: 2,
      &quot;disposition&quot;: &quot;supporting_context&quot;,
      &quot;requirement_ids&quot;: [],
      &quot;issue_ids&quot;: [],
      &quot;reason&quot;: &quot;Declares the skill name catalog-query; it identifies the workflow but adds no separate operational duty.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/SKILL.md&quot;,
      &quot;start_line&quot;: 3,
      &quot;end_line&quot;: 3,
      &quot;disposition&quot;: &quot;supporting_context&quot;,
      &quot;requirement_ids&quot;: [],
      &quot;issue_ids&quot;: [],
      &quot;reason&quot;: &quot;Supplies the declared purpose used for this task.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/SKILL.md&quot;,
      &quot;start_line&quot;: 4,
      &quot;end_line&quot;: 4,
      &quot;disposition&quot;: &quot;not_applicable&quot;,
      &quot;requirement_ids&quot;: [],
      &quot;issue_ids&quot;: [],
      &quot;reason&quot;: &quot;Frontmatter closing delimiter; no task obligation.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/SKILL.md&quot;,
      &quot;start_line&quot;: 6,
      &quot;end_line&quot;: 6,
      &quot;disposition&quot;: &quot;supporting_context&quot;,
      &quot;requirement_ids&quot;: [],
      &quot;issue_ids&quot;: [],
      &quot;reason&quot;: &quot;Document title for the catalog query workflow.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/SKILL.md&quot;,
      &quot;start_line&quot;: 8,
      &quot;end_line&quot;: 8,
      &quot;disposition&quot;: &quot;supporting_context&quot;,
      &quot;requirement_ids&quot;: [],
      &quot;issue_ids&quot;: [],
      &quot;reason&quot;: &quot;Incorporates the referenced workflow instructions; the concrete duties are extracted from that file.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/query.yaml&quot;,
      &quot;start_line&quot;: 1,
      &quot;end_line&quot;: 1,
      &quot;disposition&quot;: &quot;supporting_context&quot;,
      &quot;requirement_ids&quot;: [],
      &quot;issue_ids&quot;: [],
      &quot;reason&quot;: &quot;Section heading for missing-argument settings.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/query.yaml&quot;,
      &quot;start_line&quot;: 2,
      &quot;end_line&quot;: 2,
      &quot;disposition&quot;: &quot;requirement&quot;,
      &quot;requirement_ids&quot;: [
        &quot;R4&quot;
      ],
      &quot;issue_ids&quot;: [],
      &quot;reason&quot;: &quot;Provides the omit setting for a missing from_date argument.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/query.yaml&quot;,
      &quot;start_line&quot;: 3,
      &quot;end_line&quot;: 3,
      &quot;disposition&quot;: &quot;requirement&quot;,
      &quot;requirement_ids&quot;: [
        &quot;R6&quot;
      ],
      &quot;issue_ids&quot;: [],
      &quot;reason&quot;: &quot;Provides the omit setting for a missing limit argument.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 1,
      &quot;end_line&quot;: 1,
      &quot;disposition&quot;: &quot;supporting_context&quot;,
      &quot;requirement_ids&quot;: [],
      &quot;issue_ids&quot;: [],
      &quot;reason&quot;: &quot;Heading for the query workflow; no separate obligation.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 3,
      &quot;end_line&quot;: 3,
      &quot;disposition&quot;: &quot;capability&quot;,
      &quot;requirement_ids&quot;: [],
      &quot;issue_ids&quot;: [],
      &quot;reason&quot;: &quot;States an index.search capability while explicitly not requesting fuzzy expansion in this workflow.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 5,
      &quot;end_line&quot;: 5,
      &quot;disposition&quot;: &quot;requirement&quot;,
      &quot;requirement_ids&quot;: [
        &quot;R1&quot;
      ],
      &quot;issue_ids&quot;: [],
      &quot;reason&quot;: &quot;Requires reading the supplied request and identifies its fields.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 7,
      &quot;end_line&quot;: 7,
      &quot;disposition&quot;: &quot;requirement&quot;,
      &quot;requirement_ids&quot;: [
        &quot;R2&quot;
      ],
      &quot;issue_ids&quot;: [],
      &quot;reason&quot;: &quot;Requires exactly one index.search call with the unchanged request term.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 9,
      &quot;end_line&quot;: 9,
      &quot;disposition&quot;: &quot;supporting_context&quot;,
      &quot;requirement_ids&quot;: [
        &quot;R3&quot;,
        &quot;R4&quot;,
        &quot;R5&quot;,
        &quot;R6&quot;
      ],
      &quot;issue_ids&quot;: [],
      &quot;reason&quot;: &quot;Introduces the call-argument requirement bullets.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 10,
      &quot;end_line&quot;: 10,
      &quot;disposition&quot;: &quot;requirement&quot;,
      &quot;requirement_ids&quot;: [
        &quot;R3&quot;
      ],
      &quot;issue_ids&quot;: [],
      &quot;reason&quot;: &quot;Requires unchanged passthrough of a present from_date and states its accepted format.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 11,
      &quot;end_line&quot;: 11,
      &quot;disposition&quot;: &quot;requirement&quot;,
      &quot;requirement_ids&quot;: [
        &quot;R4&quot;
      ],
      &quot;issue_ids&quot;: [],
      &quot;reason&quot;: &quot;Requires omitting the from_date argument when from_date is missing.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 12,
      &quot;end_line&quot;: 12,
      &quot;disposition&quot;: &quot;requirement&quot;,
      &quot;requirement_ids&quot;: [
        &quot;R5&quot;
      ],
      &quot;issue_ids&quot;: [],
      &quot;reason&quot;: &quot;Requires unchanged passthrough of a present limit value.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 13,
      &quot;end_line&quot;: 13,
      &quot;disposition&quot;: &quot;requirement&quot;,
      &quot;requirement_ids&quot;: [
        &quot;R6&quot;
      ],
      &quot;issue_ids&quot;: [],
      &quot;reason&quot;: &quot;Requires omitting the limit argument when limit is missing.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 15,
      &quot;end_line&quot;: 15,
      &quot;disposition&quot;: &quot;requirement&quot;,
      &quot;requirement_ids&quot;: [
        &quot;R4&quot;,
        &quot;R6&quot;
      ],
      &quot;issue_ids&quot;: [],
      &quot;reason&quot;: &quot;Requires applying query.yaml missing-argument settings to the same search call; reflected in the two omission requirements.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 17,
      &quot;end_line&quot;: 17,
      &quot;disposition&quot;: &quot;requirement&quot;,
      &quot;requirement_ids&quot;: [
        &quot;R7&quot;
      ],
      &quot;issue_ids&quot;: [],
      &quot;reason&quot;: &quot;Explicitly prohibits invoking index.delete in the workflow.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 19,
      &quot;end_line&quot;: 19,
      &quot;disposition&quot;: &quot;supporting_context&quot;,
      &quot;requirement_ids&quot;: [
        &quot;R3&quot;,
        &quot;R4&quot;,
        &quot;R5&quot;,
        &quot;R6&quot;
      ],
      &quot;issue_ids&quot;: [],
      &quot;reason&quot;: &quot;Clarifies that parameter descriptions are call requirements and do not add pre-call validation or normalization requirements.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 21,
      &quot;end_line&quot;: 21,
      &quot;disposition&quot;: &quot;requirement&quot;,
      &quot;requirement_ids&quot;: [
        &quot;R8&quot;
      ],
      &quot;issue_ids&quot;: [],
      &quot;reason&quot;: &quot;Requires writing the response total to local count.txt after the search.&quot;
    },
    {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 23,
      &quot;end_line&quot;: 23,
      &quot;disposition&quot;: &quot;requirement&quot;,
      &quot;requirement_ids&quot;: [
        &quot;R9&quot;
      ],
      &quot;issue_ids&quot;: [],
      &quot;reason&quot;: &quot;Requires returning the response items value unchanged.&quot;
    }
  ],
  &quot;issues&quot;: [],
  &quot;schema_version&quot;: &quot;skillflow-task-v3&quot;,
  &quot;basis&quot;: &quot;declared_skill&quot;,
  &quot;source_sha256&quot;: &quot;66bc23209ed1dccd2232511bd2933a076c2bb101e0b180737668b78f6dad618c&quot;,
  &quot;user_request_sha256&quot;: null,
  &quot;task_sha256&quot;: &quot;b7d5394817bf20305abb5bd7a18bf975e5bf784a93eea05091a51969895675cb&quot;
}</pre>

<details><summary>Task source evidence</summary><pre>[
  {
    &quot;owner&quot;: &quot;purpose&quot;,
    &quot;reference&quot;: {
      &quot;file&quot;: &quot;skill/SKILL.md&quot;,
      &quot;start_line&quot;: 3,
      &quot;end_line&quot;: 3,
      &quot;reason&quot;: &quot;Declares the skill purpose: a one-time index query using a supplied request with preserved optional-parameter semantics.&quot;
    },
    &quot;quote&quot;: &quot;description: Query an index once using a supplied request and preserve optional-parameter semantics.\n&quot;
  },
  {
    &quot;owner&quot;: &quot;R1&quot;,
    &quot;reference&quot;: {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 5,
      &quot;end_line&quot;: 5,
      &quot;reason&quot;: &quot;Imperatively directs reading the supplied request and identifies the request fields that govern the search call.&quot;
    },
    &quot;quote&quot;: &quot;Read the user-supplied request.json, which contains term and may contain from_date and limit.\n&quot;
  },
  {
    &quot;owner&quot;: &quot;R2&quot;,
    &quot;reference&quot;: {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 7,
      &quot;end_line&quot;: 7,
      &quot;reason&quot;: &quot;States the exact call count, operation, and unchanged term argument in one sentence.&quot;
    },
    &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.\n&quot;
  },
  {
    &quot;owner&quot;: &quot;R3&quot;,
    &quot;reference&quot;: {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 10,
      &quot;end_line&quot;: 10,
      &quot;reason&quot;: &quot;Specifies the conditional from_date argument, its unchanged value, and accepted format.&quot;
    },
    &quot;quote&quot;: &quot;  - When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.\n&quot;
  },
  {
    &quot;owner&quot;: &quot;R4&quot;,
    &quot;reference&quot;: {
      &quot;file&quot;: &quot;skill/query.yaml&quot;,
      &quot;start_line&quot;: 2,
      &quot;end_line&quot;: 2,
      &quot;reason&quot;: &quot;Declares the missing from_date setting as omit.&quot;
    },
    &quot;quote&quot;: &quot;  from_date: omit\n&quot;
  },
  {
    &quot;owner&quot;: &quot;R4&quot;,
    &quot;reference&quot;: {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 11,
      &quot;end_line&quot;: 11,
      &quot;reason&quot;: &quot;Requires omitting from_date when it is missing.&quot;
    },
    &quot;quote&quot;: &quot;  - When from_date is missing, omit the from_date argument.\n&quot;
  },
  {
    &quot;owner&quot;: &quot;R4&quot;,
    &quot;reference&quot;: {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 15,
      &quot;end_line&quot;: 15,
      &quot;reason&quot;: &quot;Requires applying query.yaml missing-argument settings to the same search call.&quot;
    },
    &quot;quote&quot;: &quot;Apply the missing-argument settings in [query configuration](../query.yaml) to this same call.\n&quot;
  },
  {
    &quot;owner&quot;: &quot;R5&quot;,
    &quot;reference&quot;: {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 12,
      &quot;end_line&quot;: 12,
      &quot;reason&quot;: &quot;Specifies the conditional limit argument and its unchanged value.&quot;
    },
    &quot;quote&quot;: &quot;  - When limit is present, pass its value unchanged as the limit argument.\n&quot;
  },
  {
    &quot;owner&quot;: &quot;R6&quot;,
    &quot;reference&quot;: {
      &quot;file&quot;: &quot;skill/query.yaml&quot;,
      &quot;start_line&quot;: 3,
      &quot;end_line&quot;: 3,
      &quot;reason&quot;: &quot;Declares the missing limit setting as omit.&quot;
    },
    &quot;quote&quot;: &quot;  limit: omit\n&quot;
  },
  {
    &quot;owner&quot;: &quot;R6&quot;,
    &quot;reference&quot;: {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 13,
      &quot;end_line&quot;: 13,
      &quot;reason&quot;: &quot;Requires omitting limit when it is missing.&quot;
    },
    &quot;quote&quot;: &quot;  - When limit is missing, omit the limit argument.\n&quot;
  },
  {
    &quot;owner&quot;: &quot;R6&quot;,
    &quot;reference&quot;: {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 15,
      &quot;end_line&quot;: 15,
      &quot;reason&quot;: &quot;Requires applying query.yaml missing-argument settings to the same search call.&quot;
    },
    &quot;quote&quot;: &quot;Apply the missing-argument settings in [query configuration](../query.yaml) to this same call.\n&quot;
  },
  {
    &quot;owner&quot;: &quot;R7&quot;,
    &quot;reference&quot;: {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 17,
      &quot;end_line&quot;: 17,
      &quot;reason&quot;: &quot;Explicitly prohibits invoking index.delete anywhere in the workflow.&quot;
    },
    &quot;quote&quot;: &quot;Do not invoke index.delete anywhere in this workflow.\n&quot;
  },
  {
    &quot;owner&quot;: &quot;R8&quot;,
    &quot;reference&quot;: {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 21,
      &quot;end_line&quot;: 21,
      &quot;reason&quot;: &quot;Requires the post-search write of the response total to the specified local file.&quot;
    },
    &quot;quote&quot;: &quot;After the search, write the response&#x27;s total value to local count.txt.\n&quot;
  },
  {
    &quot;owner&quot;: &quot;R9&quot;,
    &quot;reference&quot;: {
      &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
      &quot;start_line&quot;: 23,
      &quot;end_line&quot;: 23,
      &quot;reason&quot;: &quot;Requires returning the response items value without change.&quot;
    },
    &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.\n&quot;
  }
]</pre></details>

## Source → Task → demands correspondence

Links are program-generated; accounting coverage and completed computation do not prove semantic completeness. Each entry retains source evidence, expression gaps, raw demand positions, compiled goals, per-seed derivations and receiving boundaries.

<pre>[
  {
    &quot;requirement_id&quot;: &quot;R1&quot;,
    &quot;source_accounting_indices&quot;: [
      11
    ],
    &quot;seeds&quot;: [
      {
        &quot;goal_id&quot;: &quot;goal_bad3975a1c33c86da8bc&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_001/events/0/events/0/atomic_ops/0/demands/0&quot;,
        &quot;derivation_ids&quot;: [
          &quot;demand_98dbcb2fddf9fb77a93e&quot;
        ],
        &quot;compiled_goal&quot;: {
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
          },
          &quot;preserve&quot;: &quot;action&quot;,
          &quot;path&quot;: [],
          &quot;expected&quot;: null,
          &quot;expected_path&quot;: [],
          &quot;reason&quot;: &quot;Preserve the required read of the supplied request.json.&quot;,
          &quot;id&quot;: &quot;goal_bad3975a1c33c86da8bc&quot;
        },
        &quot;sink_ids&quot;: []
      }
    ],
    &quot;requirement&quot;: {
      &quot;id&quot;: &quot;R1&quot;,
      &quot;text&quot;: &quot;Read the user-supplied request.json; it contains term and may contain from_date and limit.&quot;,
      &quot;evidences&quot;: [
        {
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;start_line&quot;: 5,
          &quot;end_line&quot;: 5,
          &quot;reason&quot;: &quot;Imperatively directs reading the supplied request and identifies the request fields that govern the search call.&quot;
        }
      ]
    },
    &quot;source_accounting&quot;: [
      {
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;start_line&quot;: 5,
        &quot;end_line&quot;: 5,
        &quot;disposition&quot;: &quot;requirement&quot;,
        &quot;requirement_ids&quot;: [
          &quot;R1&quot;
        ],
        &quot;issue_ids&quot;: [],
        &quot;reason&quot;: &quot;Requires reading the supplied request and identifies its fields.&quot;,
        &quot;quote&quot;: &quot;Read the user-supplied request.json, which contains term and may contain from_date and limit.\n&quot;
      }
    ],
    &quot;realization&quot;: {
      &quot;requirement_id&quot;: &quot;R1&quot;,
      &quot;status&quot;: &quot;expressed&quot;,
      &quot;bindings&quot;: [
        {
          &quot;target&quot;: {
            &quot;instruction_id&quot;: &quot;ir_001&quot;,
            &quot;path&quot;: []
          },
          &quot;reason&quot;: &quot;The read_request_json instruction acquires the supplied request.json; term, from_date, and limit are subsequently extracted from that request by the CFG.&quot;
        }
      ],
      &quot;gaps&quot;: [],
      &quot;goal_ids&quot;: [
        &quot;goal_bad3975a1c33c86da8bc&quot;
      ],
      &quot;constraint_ids&quot;: [],
      &quot;has_applicable_goal&quot;: true
    }
  },
  {
    &quot;requirement_id&quot;: &quot;R2&quot;,
    &quot;source_accounting_indices&quot;: [
      12
    ],
    &quot;seeds&quot;: [
      {
        &quot;goal_id&quot;: &quot;goal_06ba52e6366aa3d27778&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_007/events/0/events/1/atomic_ops/0/demands/0&quot;,
        &quot;derivation_ids&quot;: [
          &quot;demand_7d75a0a4c56874385a11&quot;
        ],
        &quot;compiled_goal&quot;: {
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
          },
          &quot;preserve&quot;: &quot;action&quot;,
          &quot;path&quot;: [],
          &quot;expected&quot;: null,
          &quot;expected_path&quot;: [],
          &quot;reason&quot;: &quot;Preserve the single index.search invocation; together with the at-most constraint this covers the exactly-once requirement.&quot;,
          &quot;id&quot;: &quot;goal_06ba52e6366aa3d27778&quot;
        },
        &quot;sink_ids&quot;: [
          &quot;sink_f5e30d631911b0c8db08&quot;
        ]
      },
      {
        &quot;goal_id&quot;: &quot;goal_b9704dcab72933209f08&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_007/events/0/events/1/atomic_ops/0/demands/1&quot;,
        &quot;derivation_ids&quot;: [
          &quot;demand_1cf2bd3a1b6cefaeebf0&quot;,
          &quot;demand_2011f2f9df4b0a803756&quot;,
          &quot;demand_24a23be128f53091c993&quot;,
          &quot;demand_28e08f4f663b7011f1d7&quot;,
          &quot;demand_37154e374f14a5f3224e&quot;,
          &quot;demand_5a2713c90c7e1f1c406d&quot;,
          &quot;demand_5d9944aca9d0f5b3af9e&quot;,
          &quot;demand_7af4ef8e87c64e9c7ff1&quot;,
          &quot;demand_9bb97c53e9fd4ea8bcc4&quot;,
          &quot;demand_b8c556f810395df679cc&quot;,
          &quot;demand_c7277a7ef37dfc348362&quot;,
          &quot;demand_e17da6f4e6d06628fbd1&quot;,
          &quot;demand_ef7bc36a49ee5facb86d&quot;
        ],
        &quot;compiled_goal&quot;: {
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
              &quot;kind&quot;: &quot;input&quot;,
              &quot;index&quot;: 0
            }
          },
          &quot;preserve&quot;: &quot;value&quot;,
          &quot;path&quot;: [
            &quot;query&quot;
          ],
          &quot;expected&quot;: {
            &quot;kind&quot;: &quot;input&quot;,
            &quot;index&quot;: 1
          },
          &quot;expected_path&quot;: [],
          &quot;reason&quot;: &quot;Preserve request.term unchanged as the query argument.&quot;,
          &quot;id&quot;: &quot;goal_b9704dcab72933209f08&quot;
        },
        &quot;sink_ids&quot;: [
          &quot;sink_6982d6acfff5c4808d1f&quot;,
          &quot;sink_8632d255f8657b506825&quot;,
          &quot;sink_c2397cb75735b4bbf5ed&quot;,
          &quot;sink_f5e30d631911b0c8db08&quot;
        ]
      }
    ],
    &quot;requirement&quot;: {
      &quot;id&quot;: &quot;R2&quot;,
      &quot;text&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.&quot;,
      &quot;evidences&quot;: [
        {
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;start_line&quot;: 7,
          &quot;end_line&quot;: 7,
          &quot;reason&quot;: &quot;States the exact call count, operation, and unchanged term argument in one sentence.&quot;
        }
      ]
    },
    &quot;source_accounting&quot;: [
      {
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;start_line&quot;: 7,
        &quot;end_line&quot;: 7,
        &quot;disposition&quot;: &quot;requirement&quot;,
        &quot;requirement_ids&quot;: [
          &quot;R2&quot;
        ],
        &quot;issue_ids&quot;: [],
        &quot;reason&quot;: &quot;Requires exactly one index.search call with the unchanged request term.&quot;,
        &quot;quote&quot;: &quot;Call index.search exactly once, using request.term unchanged as its query argument.\n&quot;
      }
    ],
    &quot;realization&quot;: {
      &quot;requirement_id&quot;: &quot;R2&quot;,
      &quot;status&quot;: &quot;expressed&quot;,
      &quot;bindings&quot;: [
        {
          &quot;target&quot;: {
            &quot;instruction_id&quot;: &quot;ir_003&quot;,
            &quot;path&quot;: []
          },
          &quot;reason&quot;: &quot;The request.term value is selected unchanged from the supplied request for the search call.&quot;
        },
        {
          &quot;target&quot;: {
            &quot;instruction_id&quot;: &quot;ir_007&quot;,
            &quot;path&quot;: []
          },
          &quot;reason&quot;: &quot;The CFG has a single index.search instruction; its build and deliver operations pass the selected term and optional arguments, and the at-most constraint caps the call count at one.&quot;
        }
      ],
      &quot;gaps&quot;: [],
      &quot;goal_ids&quot;: [
        &quot;goal_06ba52e6366aa3d27778&quot;,
        &quot;goal_b9704dcab72933209f08&quot;
      ],
      &quot;constraint_ids&quot;: [
        &quot;constraint_9009e15876bcfc82d8ad&quot;
      ],
      &quot;has_applicable_goal&quot;: true
    }
  },
  {
    &quot;requirement_id&quot;: &quot;R3&quot;,
    &quot;source_accounting_indices&quot;: [
      13,
      14,
      20
    ],
    &quot;seeds&quot;: [
      {
        &quot;goal_id&quot;: &quot;goal_c25263b0b7055126cef1&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_007/events/0/events/1/atomic_ops/0/demands/2&quot;,
        &quot;derivation_ids&quot;: [
          &quot;demand_040c46ea630a77b3f3a9&quot;,
          &quot;demand_11c1292b507a99d484a9&quot;,
          &quot;demand_21fc99a5f39f0a12bb33&quot;,
          &quot;demand_3519cd325fa94f564a75&quot;,
          &quot;demand_42fbb489f1bd4560a46f&quot;,
          &quot;demand_4a3a715927c9f2ef6981&quot;,
          &quot;demand_590b42ebda7587a7fd51&quot;,
          &quot;demand_5d35b238051495dcce71&quot;,
          &quot;demand_643508f65ade2ed6cb53&quot;,
          &quot;demand_6805e845273c09774a25&quot;,
          &quot;demand_6c004b1a228348f6d572&quot;,
          &quot;demand_762481587d1dd195647d&quot;,
          &quot;demand_826a46cc7dab97aadc12&quot;,
          &quot;demand_84232f84eead295c9298&quot;,
          &quot;demand_8bac55342e62890a8849&quot;,
          &quot;demand_90a8c8faaa43e558ed32&quot;,
          &quot;demand_a8c4d482172c4e5b600b&quot;,
          &quot;demand_a9cb292e347f99bd49e2&quot;,
          &quot;demand_bf8055ea0bc0dea4bc17&quot;,
          &quot;demand_cdb9b6806ba2be68aa2a&quot;,
          &quot;demand_d382514978f76839919b&quot;,
          &quot;demand_e124af09ea1ff36bf62d&quot;,
          &quot;demand_e5b4ea3e00aaa215f221&quot;,
          &quot;demand_ee03d6918aa2bfde483d&quot;,
          &quot;demand_f0f265b2497e30deb0da&quot;
        ],
        &quot;compiled_goal&quot;: {
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
              &quot;kind&quot;: &quot;input&quot;,
              &quot;index&quot;: 0
            }
          },
          &quot;preserve&quot;: &quot;value&quot;,
          &quot;path&quot;: [
            &quot;from_date&quot;
          ],
          &quot;expected&quot;: {
            &quot;kind&quot;: &quot;input&quot;,
            &quot;index&quot;: 2
          },
          &quot;expected_path&quot;: [],
          &quot;reason&quot;: &quot;When from_date is present, preserve its value unchanged in the from_date argument.&quot;,
          &quot;id&quot;: &quot;goal_c25263b0b7055126cef1&quot;
        },
        &quot;sink_ids&quot;: [
          &quot;sink_431a0c1fa101e978cc88&quot;,
          &quot;sink_5298b9fc4b95bf5e34ac&quot;,
          &quot;sink_6982d6acfff5c4808d1f&quot;,
          &quot;sink_c2397cb75735b4bbf5ed&quot;,
          &quot;sink_f5e30d631911b0c8db08&quot;
        ]
      }
    ],
    &quot;requirement&quot;: {
      &quot;id&quot;: &quot;R3&quot;,
      &quot;text&quot;: &quot;When from_date is present in the request, pass its value unchanged as the from_date argument; the accepted format is YYYY-MM-DD.&quot;,
      &quot;evidences&quot;: [
        {
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;start_line&quot;: 10,
          &quot;end_line&quot;: 10,
          &quot;reason&quot;: &quot;Specifies the conditional from_date argument, its unchanged value, and accepted format.&quot;
        }
      ]
    },
    &quot;source_accounting&quot;: [
      {
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;start_line&quot;: 9,
        &quot;end_line&quot;: 9,
        &quot;disposition&quot;: &quot;supporting_context&quot;,
        &quot;requirement_ids&quot;: [
          &quot;R3&quot;,
          &quot;R4&quot;,
          &quot;R5&quot;,
          &quot;R6&quot;
        ],
        &quot;issue_ids&quot;: [],
        &quot;reason&quot;: &quot;Introduces the call-argument requirement bullets.&quot;,
        &quot;quote&quot;: &quot;- Call argument requirements:\n&quot;
      },
      {
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;start_line&quot;: 10,
        &quot;end_line&quot;: 10,
        &quot;disposition&quot;: &quot;requirement&quot;,
        &quot;requirement_ids&quot;: [
          &quot;R3&quot;
        ],
        &quot;issue_ids&quot;: [],
        &quot;reason&quot;: &quot;Requires unchanged passthrough of a present from_date and states its accepted format.&quot;,
        &quot;quote&quot;: &quot;  - When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.\n&quot;
      },
      {
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;start_line&quot;: 19,
        &quot;end_line&quot;: 19,
        &quot;disposition&quot;: &quot;supporting_context&quot;,
        &quot;requirement_ids&quot;: [
          &quot;R3&quot;,
          &quot;R4&quot;,
          &quot;R5&quot;,
          &quot;R6&quot;
        ],
        &quot;issue_ids&quot;: [],
        &quot;reason&quot;: &quot;Clarifies that parameter descriptions are call requirements and do not add pre-call validation or normalization requirements.&quot;,
        &quot;quote&quot;: &quot;Parameter descriptions are call requirements and do not instruct pre-call validation or normalization.\n&quot;
      }
    ],
    &quot;realization&quot;: {
      &quot;requirement_id&quot;: &quot;R3&quot;,
      &quot;status&quot;: &quot;expressed&quot;,
      &quot;bindings&quot;: [
        {
          &quot;target&quot;: {
            &quot;instruction_id&quot;: &quot;ir_004&quot;,
            &quot;path&quot;: []
          },
          &quot;reason&quot;: &quot;The optional from_date value is selected from the request and its presence is computed separately.&quot;
        },
        {
          &quot;target&quot;: {
            &quot;instruction_id&quot;: &quot;ir_007&quot;,
            &quot;path&quot;: []
          },
          &quot;reason&quot;: &quot;The search request from_date member uses the selected value unchanged when the presence flag is true.&quot;
        }
      ],
      &quot;gaps&quot;: [],
      &quot;goal_ids&quot;: [
        &quot;goal_c25263b0b7055126cef1&quot;
      ],
      &quot;constraint_ids&quot;: [],
      &quot;has_applicable_goal&quot;: true
    }
  },
  {
    &quot;requirement_id&quot;: &quot;R4&quot;,
    &quot;source_accounting_indices&quot;: [
      7,
      13,
      15,
      18,
      20
    ],
    &quot;seeds&quot;: [
      {
        &quot;goal_id&quot;: &quot;goal_852714501b1884f87090&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/0&quot;,
        &quot;derivation_ids&quot;: [
          &quot;demand_124ab7fabe6068059b38&quot;,
          &quot;demand_337fb1297ba54ad5da66&quot;,
          &quot;demand_3d3d7ae1418b74d696f7&quot;,
          &quot;demand_41850aec0160ef422854&quot;,
          &quot;demand_4cb095dcbfa2c33d77ee&quot;,
          &quot;demand_6d99652a86943741c3eb&quot;,
          &quot;demand_85e7a4931aa93fb6b1e6&quot;,
          &quot;demand_90c2453cf4e8850e2f87&quot;,
          &quot;demand_a0b33a9eda68b1403808&quot;,
          &quot;demand_bd9a60659f9187892e00&quot;,
          &quot;demand_c5bceddd5ea42bd4f55c&quot;,
          &quot;demand_dd861db390d4a4006f4d&quot;
        ],
        &quot;compiled_goal&quot;: {
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
          },
          &quot;preserve&quot;: &quot;presence&quot;,
          &quot;path&quot;: [
            &quot;from_date&quot;
          ],
          &quot;expected&quot;: null,
          &quot;expected_path&quot;: [],
          &quot;reason&quot;: &quot;The built search request conditionally includes from_date only when the request field is present, so a missing from_date omits this member and applies query.yaml&#x27;s omit setting to the same call.&quot;,
          &quot;id&quot;: &quot;goal_852714501b1884f87090&quot;
        },
        &quot;sink_ids&quot;: [
          &quot;sink_5298b9fc4b95bf5e34ac&quot;,
          &quot;sink_6982d6acfff5c4808d1f&quot;,
          &quot;sink_c2397cb75735b4bbf5ed&quot;
        ]
      }
    ],
    &quot;requirement&quot;: {
      &quot;id&quot;: &quot;R4&quot;,
      &quot;text&quot;: &quot;When from_date is missing from the request, omit the from_date argument from this same index.search call, applying query.yaml&#x27;s missing-argument setting.&quot;,
      &quot;evidences&quot;: [
        {
          &quot;file&quot;: &quot;skill/query.yaml&quot;,
          &quot;start_line&quot;: 2,
          &quot;end_line&quot;: 2,
          &quot;reason&quot;: &quot;Declares the missing from_date setting as omit.&quot;
        },
        {
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;start_line&quot;: 11,
          &quot;end_line&quot;: 11,
          &quot;reason&quot;: &quot;Requires omitting from_date when it is missing.&quot;
        },
        {
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;start_line&quot;: 15,
          &quot;end_line&quot;: 15,
          &quot;reason&quot;: &quot;Requires applying query.yaml missing-argument settings to the same search call.&quot;
        }
      ]
    },
    &quot;source_accounting&quot;: [
      {
        &quot;file&quot;: &quot;skill/query.yaml&quot;,
        &quot;start_line&quot;: 2,
        &quot;end_line&quot;: 2,
        &quot;disposition&quot;: &quot;requirement&quot;,
        &quot;requirement_ids&quot;: [
          &quot;R4&quot;
        ],
        &quot;issue_ids&quot;: [],
        &quot;reason&quot;: &quot;Provides the omit setting for a missing from_date argument.&quot;,
        &quot;quote&quot;: &quot;  from_date: omit\n&quot;
      },
      {
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;start_line&quot;: 9,
        &quot;end_line&quot;: 9,
        &quot;disposition&quot;: &quot;supporting_context&quot;,
        &quot;requirement_ids&quot;: [
          &quot;R3&quot;,
          &quot;R4&quot;,
          &quot;R5&quot;,
          &quot;R6&quot;
        ],
        &quot;issue_ids&quot;: [],
        &quot;reason&quot;: &quot;Introduces the call-argument requirement bullets.&quot;,
        &quot;quote&quot;: &quot;- Call argument requirements:\n&quot;
      },
      {
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;start_line&quot;: 11,
        &quot;end_line&quot;: 11,
        &quot;disposition&quot;: &quot;requirement&quot;,
        &quot;requirement_ids&quot;: [
          &quot;R4&quot;
        ],
        &quot;issue_ids&quot;: [],
        &quot;reason&quot;: &quot;Requires omitting the from_date argument when from_date is missing.&quot;,
        &quot;quote&quot;: &quot;  - When from_date is missing, omit the from_date argument.\n&quot;
      },
      {
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;start_line&quot;: 15,
        &quot;end_line&quot;: 15,
        &quot;disposition&quot;: &quot;requirement&quot;,
        &quot;requirement_ids&quot;: [
          &quot;R4&quot;,
          &quot;R6&quot;
        ],
        &quot;issue_ids&quot;: [],
        &quot;reason&quot;: &quot;Requires applying query.yaml missing-argument settings to the same search call; reflected in the two omission requirements.&quot;,
        &quot;quote&quot;: &quot;Apply the missing-argument settings in [query configuration](../query.yaml) to this same call.\n&quot;
      },
      {
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;start_line&quot;: 19,
        &quot;end_line&quot;: 19,
        &quot;disposition&quot;: &quot;supporting_context&quot;,
        &quot;requirement_ids&quot;: [
          &quot;R3&quot;,
          &quot;R4&quot;,
          &quot;R5&quot;,
          &quot;R6&quot;
        ],
        &quot;issue_ids&quot;: [],
        &quot;reason&quot;: &quot;Clarifies that parameter descriptions are call requirements and do not add pre-call validation or normalization requirements.&quot;,
        &quot;quote&quot;: &quot;Parameter descriptions are call requirements and do not instruct pre-call validation or normalization.\n&quot;
      }
    ],
    &quot;realization&quot;: {
      &quot;requirement_id&quot;: &quot;R4&quot;,
      &quot;status&quot;: &quot;expressed&quot;,
      &quot;bindings&quot;: [
        {
          &quot;target&quot;: {
            &quot;instruction_id&quot;: &quot;ir_007&quot;,
            &quot;path&quot;: []
          },
          &quot;reason&quot;: &quot;The build member for from_date has a when control tied to from_date presence, so a missing from_date omits the member and applies the omit setting in query.yaml to this same call.&quot;
        }
      ],
      &quot;gaps&quot;: [],
      &quot;goal_ids&quot;: [
        &quot;goal_852714501b1884f87090&quot;
      ],
      &quot;constraint_ids&quot;: [],
      &quot;has_applicable_goal&quot;: true
    }
  },
  {
    &quot;requirement_id&quot;: &quot;R5&quot;,
    &quot;source_accounting_indices&quot;: [
      13,
      16,
      20
    ],
    &quot;seeds&quot;: [
      {
        &quot;goal_id&quot;: &quot;goal_99915fbe3f62e1af0426&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_007/events/0/events/1/atomic_ops/0/demands/3&quot;,
        &quot;derivation_ids&quot;: [
          &quot;demand_0ef30ddf1912010b5241&quot;,
          &quot;demand_0f342157a8515367497a&quot;,
          &quot;demand_10bd0a708d3f8dc5425f&quot;,
          &quot;demand_2265116b7cfa70e7b4fd&quot;,
          &quot;demand_516ebbbcda4dd4401481&quot;,
          &quot;demand_664f3d164665ceccc236&quot;,
          &quot;demand_80b80e5e32bb4975cf54&quot;,
          &quot;demand_818be2d98b4452eeedc4&quot;,
          &quot;demand_826c56400b72b19032dd&quot;,
          &quot;demand_84f9c21c73468e5a9f36&quot;,
          &quot;demand_8908050761768483aa42&quot;,
          &quot;demand_8c1a0244385b7a40c8d7&quot;,
          &quot;demand_8cec444e21f59eae5821&quot;,
          &quot;demand_a0f746440856254f3e55&quot;,
          &quot;demand_bde9043c98c874071f96&quot;,
          &quot;demand_c517668c72349b7793ae&quot;,
          &quot;demand_c8563fb46c01ac50aa1a&quot;,
          &quot;demand_d33e6a25921fbd47190c&quot;,
          &quot;demand_d5f140ab698f1c07550f&quot;,
          &quot;demand_e988c039d89c1763ac21&quot;,
          &quot;demand_ed053d38c1c3c958466c&quot;,
          &quot;demand_f2bb42d64236e7f67d4a&quot;,
          &quot;demand_f39fdd98d6d3cb57415c&quot;,
          &quot;demand_fb3898ec36137409560d&quot;,
          &quot;demand_fdaa28ea47863a88b661&quot;
        ],
        &quot;compiled_goal&quot;: {
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
              &quot;kind&quot;: &quot;input&quot;,
              &quot;index&quot;: 0
            }
          },
          &quot;preserve&quot;: &quot;value&quot;,
          &quot;path&quot;: [
            &quot;limit&quot;
          ],
          &quot;expected&quot;: {
            &quot;kind&quot;: &quot;input&quot;,
            &quot;index&quot;: 4
          },
          &quot;expected_path&quot;: [],
          &quot;reason&quot;: &quot;When limit is present, preserve its value unchanged in the limit argument.&quot;,
          &quot;id&quot;: &quot;goal_99915fbe3f62e1af0426&quot;
        },
        &quot;sink_ids&quot;: [
          &quot;sink_6982d6acfff5c4808d1f&quot;,
          &quot;sink_836d6bb37efb1eefe31e&quot;,
          &quot;sink_c2397cb75735b4bbf5ed&quot;,
          &quot;sink_ce54588f3e0fbdcec0e6&quot;,
          &quot;sink_f5e30d631911b0c8db08&quot;
        ]
      }
    ],
    &quot;requirement&quot;: {
      &quot;id&quot;: &quot;R5&quot;,
      &quot;text&quot;: &quot;When limit is present in the request, pass its value unchanged as the limit argument.&quot;,
      &quot;evidences&quot;: [
        {
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;start_line&quot;: 12,
          &quot;end_line&quot;: 12,
          &quot;reason&quot;: &quot;Specifies the conditional limit argument and its unchanged value.&quot;
        }
      ]
    },
    &quot;source_accounting&quot;: [
      {
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;start_line&quot;: 9,
        &quot;end_line&quot;: 9,
        &quot;disposition&quot;: &quot;supporting_context&quot;,
        &quot;requirement_ids&quot;: [
          &quot;R3&quot;,
          &quot;R4&quot;,
          &quot;R5&quot;,
          &quot;R6&quot;
        ],
        &quot;issue_ids&quot;: [],
        &quot;reason&quot;: &quot;Introduces the call-argument requirement bullets.&quot;,
        &quot;quote&quot;: &quot;- Call argument requirements:\n&quot;
      },
      {
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;start_line&quot;: 12,
        &quot;end_line&quot;: 12,
        &quot;disposition&quot;: &quot;requirement&quot;,
        &quot;requirement_ids&quot;: [
          &quot;R5&quot;
        ],
        &quot;issue_ids&quot;: [],
        &quot;reason&quot;: &quot;Requires unchanged passthrough of a present limit value.&quot;,
        &quot;quote&quot;: &quot;  - When limit is present, pass its value unchanged as the limit argument.\n&quot;
      },
      {
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;start_line&quot;: 19,
        &quot;end_line&quot;: 19,
        &quot;disposition&quot;: &quot;supporting_context&quot;,
        &quot;requirement_ids&quot;: [
          &quot;R3&quot;,
          &quot;R4&quot;,
          &quot;R5&quot;,
          &quot;R6&quot;
        ],
        &quot;issue_ids&quot;: [],
        &quot;reason&quot;: &quot;Clarifies that parameter descriptions are call requirements and do not add pre-call validation or normalization requirements.&quot;,
        &quot;quote&quot;: &quot;Parameter descriptions are call requirements and do not instruct pre-call validation or normalization.\n&quot;
      }
    ],
    &quot;realization&quot;: {
      &quot;requirement_id&quot;: &quot;R5&quot;,
      &quot;status&quot;: &quot;expressed&quot;,
      &quot;bindings&quot;: [
        {
          &quot;target&quot;: {
            &quot;instruction_id&quot;: &quot;ir_005&quot;,
            &quot;path&quot;: []
          },
          &quot;reason&quot;: &quot;The optional limit value is selected from the request and its presence is computed separately.&quot;
        },
        {
          &quot;target&quot;: {
            &quot;instruction_id&quot;: &quot;ir_007&quot;,
            &quot;path&quot;: []
          },
          &quot;reason&quot;: &quot;The search request limit member uses the selected value unchanged when the presence flag is true.&quot;
        }
      ],
      &quot;gaps&quot;: [],
      &quot;goal_ids&quot;: [
        &quot;goal_99915fbe3f62e1af0426&quot;
      ],
      &quot;constraint_ids&quot;: [],
      &quot;has_applicable_goal&quot;: true
    }
  },
  {
    &quot;requirement_id&quot;: &quot;R6&quot;,
    &quot;source_accounting_indices&quot;: [
      8,
      13,
      17,
      18,
      20
    ],
    &quot;seeds&quot;: [
      {
        &quot;goal_id&quot;: &quot;goal_da9ae22c3399787be23d&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/1&quot;,
        &quot;derivation_ids&quot;: [
          &quot;demand_2a5b1271ff711c27cab6&quot;,
          &quot;demand_4e840f919403be10342a&quot;,
          &quot;demand_4f0d6479a3f258902fd9&quot;,
          &quot;demand_5ef46ac2ca6212387e6e&quot;,
          &quot;demand_7e08c07d87242c733f11&quot;,
          &quot;demand_99ce68074d56ea71cb5e&quot;,
          &quot;demand_ad7a3c380dd29a60d6eb&quot;,
          &quot;demand_bf1cab20b360f6dd5dd1&quot;,
          &quot;demand_c73b1e4863ac33e110b4&quot;,
          &quot;demand_d7ec078f0532d17ef79e&quot;,
          &quot;demand_ef44a9bba39f75fb78a5&quot;,
          &quot;demand_f9881e439c26f60c118b&quot;
        ],
        &quot;compiled_goal&quot;: {
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
          },
          &quot;preserve&quot;: &quot;presence&quot;,
          &quot;path&quot;: [
            &quot;limit&quot;
          ],
          &quot;expected&quot;: null,
          &quot;expected_path&quot;: [],
          &quot;reason&quot;: &quot;The built search request conditionally includes limit only when the request field is present, so a missing limit omits this member and applies query.yaml&#x27;s omit setting to the same call.&quot;,
          &quot;id&quot;: &quot;goal_da9ae22c3399787be23d&quot;
        },
        &quot;sink_ids&quot;: [
          &quot;sink_6982d6acfff5c4808d1f&quot;,
          &quot;sink_836d6bb37efb1eefe31e&quot;,
          &quot;sink_c2397cb75735b4bbf5ed&quot;
        ]
      }
    ],
    &quot;requirement&quot;: {
      &quot;id&quot;: &quot;R6&quot;,
      &quot;text&quot;: &quot;When limit is missing from the request, omit the limit argument from this same index.search call, applying query.yaml&#x27;s missing-argument setting.&quot;,
      &quot;evidences&quot;: [
        {
          &quot;file&quot;: &quot;skill/query.yaml&quot;,
          &quot;start_line&quot;: 3,
          &quot;end_line&quot;: 3,
          &quot;reason&quot;: &quot;Declares the missing limit setting as omit.&quot;
        },
        {
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;start_line&quot;: 13,
          &quot;end_line&quot;: 13,
          &quot;reason&quot;: &quot;Requires omitting limit when it is missing.&quot;
        },
        {
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;start_line&quot;: 15,
          &quot;end_line&quot;: 15,
          &quot;reason&quot;: &quot;Requires applying query.yaml missing-argument settings to the same search call.&quot;
        }
      ]
    },
    &quot;source_accounting&quot;: [
      {
        &quot;file&quot;: &quot;skill/query.yaml&quot;,
        &quot;start_line&quot;: 3,
        &quot;end_line&quot;: 3,
        &quot;disposition&quot;: &quot;requirement&quot;,
        &quot;requirement_ids&quot;: [
          &quot;R6&quot;
        ],
        &quot;issue_ids&quot;: [],
        &quot;reason&quot;: &quot;Provides the omit setting for a missing limit argument.&quot;,
        &quot;quote&quot;: &quot;  limit: omit\n&quot;
      },
      {
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;start_line&quot;: 9,
        &quot;end_line&quot;: 9,
        &quot;disposition&quot;: &quot;supporting_context&quot;,
        &quot;requirement_ids&quot;: [
          &quot;R3&quot;,
          &quot;R4&quot;,
          &quot;R5&quot;,
          &quot;R6&quot;
        ],
        &quot;issue_ids&quot;: [],
        &quot;reason&quot;: &quot;Introduces the call-argument requirement bullets.&quot;,
        &quot;quote&quot;: &quot;- Call argument requirements:\n&quot;
      },
      {
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;start_line&quot;: 13,
        &quot;end_line&quot;: 13,
        &quot;disposition&quot;: &quot;requirement&quot;,
        &quot;requirement_ids&quot;: [
          &quot;R6&quot;
        ],
        &quot;issue_ids&quot;: [],
        &quot;reason&quot;: &quot;Requires omitting the limit argument when limit is missing.&quot;,
        &quot;quote&quot;: &quot;  - When limit is missing, omit the limit argument.\n&quot;
      },
      {
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;start_line&quot;: 15,
        &quot;end_line&quot;: 15,
        &quot;disposition&quot;: &quot;requirement&quot;,
        &quot;requirement_ids&quot;: [
          &quot;R4&quot;,
          &quot;R6&quot;
        ],
        &quot;issue_ids&quot;: [],
        &quot;reason&quot;: &quot;Requires applying query.yaml missing-argument settings to the same search call; reflected in the two omission requirements.&quot;,
        &quot;quote&quot;: &quot;Apply the missing-argument settings in [query configuration](../query.yaml) to this same call.\n&quot;
      },
      {
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;start_line&quot;: 19,
        &quot;end_line&quot;: 19,
        &quot;disposition&quot;: &quot;supporting_context&quot;,
        &quot;requirement_ids&quot;: [
          &quot;R3&quot;,
          &quot;R4&quot;,
          &quot;R5&quot;,
          &quot;R6&quot;
        ],
        &quot;issue_ids&quot;: [],
        &quot;reason&quot;: &quot;Clarifies that parameter descriptions are call requirements and do not add pre-call validation or normalization requirements.&quot;,
        &quot;quote&quot;: &quot;Parameter descriptions are call requirements and do not instruct pre-call validation or normalization.\n&quot;
      }
    ],
    &quot;realization&quot;: {
      &quot;requirement_id&quot;: &quot;R6&quot;,
      &quot;status&quot;: &quot;expressed&quot;,
      &quot;bindings&quot;: [
        {
          &quot;target&quot;: {
            &quot;instruction_id&quot;: &quot;ir_007&quot;,
            &quot;path&quot;: []
          },
          &quot;reason&quot;: &quot;The build member for limit has a when control tied to limit presence, so a missing limit omits the member and applies the omit setting in query.yaml to this same call.&quot;
        }
      ],
      &quot;gaps&quot;: [],
      &quot;goal_ids&quot;: [
        &quot;goal_da9ae22c3399787be23d&quot;
      ],
      &quot;constraint_ids&quot;: [],
      &quot;has_applicable_goal&quot;: true
    }
  },
  {
    &quot;requirement_id&quot;: &quot;R7&quot;,
    &quot;source_accounting_indices&quot;: [
      19
    ],
    &quot;seeds&quot;: [],
    &quot;requirement&quot;: {
      &quot;id&quot;: &quot;R7&quot;,
      &quot;text&quot;: &quot;Do not invoke index.delete anywhere in this workflow.&quot;,
      &quot;evidences&quot;: [
        {
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;start_line&quot;: 17,
          &quot;end_line&quot;: 17,
          &quot;reason&quot;: &quot;Explicitly prohibits invoking index.delete anywhere in the workflow.&quot;
        }
      ]
    },
    &quot;source_accounting&quot;: [
      {
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;start_line&quot;: 17,
        &quot;end_line&quot;: 17,
        &quot;disposition&quot;: &quot;requirement&quot;,
        &quot;requirement_ids&quot;: [
          &quot;R7&quot;
        ],
        &quot;issue_ids&quot;: [],
        &quot;reason&quot;: &quot;Explicitly prohibits invoking index.delete in the workflow.&quot;,
        &quot;quote&quot;: &quot;Do not invoke index.delete anywhere in this workflow.\n&quot;
      }
    ],
    &quot;realization&quot;: {
      &quot;requirement_id&quot;: &quot;R7&quot;,
      &quot;status&quot;: &quot;retained_only&quot;,
      &quot;bindings&quot;: [
        {
          &quot;target&quot;: {
            &quot;path&quot;: [
              &quot;constraints&quot;,
              1
            ]
          },
          &quot;reason&quot;: &quot;The supplied CFG retains the exact prohibition against invoking index.delete as a graph-level constraint, but there is no index.delete instruction or operation event to target with an executable typed constraint.&quot;
        }
      ],
      &quot;gaps&quot;: [
        {
          &quot;reason&quot;: &quot;The workflow prohibits invoking index.delete anywhere. No index.delete operation exists in the CFG, and the available realization constraint forms cannot attach an arbitrary action prohibition to a non-existent event; the restriction is therefore retained rather than declared as an executable constraint.&quot;,
          &quot;evidences&quot;: [
            {
              &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
              &quot;start_line&quot;: 17,
              &quot;end_line&quot;: 17,
              &quot;reason&quot;: &quot;This line explicitly prohibits invoking index.delete anywhere in the workflow.&quot;
            }
          ]
        }
      ],
      &quot;goal_ids&quot;: [],
      &quot;constraint_ids&quot;: [],
      &quot;has_applicable_goal&quot;: false
    }
  },
  {
    &quot;requirement_id&quot;: &quot;R8&quot;,
    &quot;source_accounting_indices&quot;: [
      21
    ],
    &quot;seeds&quot;: [
      {
        &quot;goal_id&quot;: &quot;goal_a68e938e61f1884d7598&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_010/events/0/events/0/atomic_ops/0/demands/0&quot;,
        &quot;derivation_ids&quot;: [
          &quot;demand_1630af8d3d8cd57edf6e&quot;
        ],
        &quot;compiled_goal&quot;: {
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
          },
          &quot;preserve&quot;: &quot;action&quot;,
          &quot;path&quot;: [],
          &quot;expected&quot;: null,
          &quot;expected_path&quot;: [],
          &quot;reason&quot;: &quot;Preserve the required write to local count.txt.&quot;,
          &quot;id&quot;: &quot;goal_a68e938e61f1884d7598&quot;
        },
        &quot;sink_ids&quot;: [
          &quot;sink_d73d96f2b39e63cdaaad&quot;
        ]
      },
      {
        &quot;goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
        &quot;raw_pointer&quot;: &quot;/ir_semantics/ir_010/events/0/events/0/atomic_ops/0/demands/1&quot;,
        &quot;derivation_ids&quot;: [
          &quot;demand_027879ee0798a76e382e&quot;,
          &quot;demand_03981620e2e6f3f13b08&quot;,
          &quot;demand_0f95adba03c8b5c7d0df&quot;,
          &quot;demand_0fb904054ffe8db7cff2&quot;,
          &quot;demand_1267e5b11b3f8394cebb&quot;,
          &quot;demand_148d47ecfc12a07d92c2&quot;,
          &quot;demand_1527693ead3389526798&quot;,
          &quot;demand_15e672d7fd8cfc39f9d5&quot;,
          &quot;demand_19163dc921148efcdf63&quot;,
          &quot;demand_19841bb9b807fdf32007&quot;,
          &quot;demand_2309bafb3909dcb19085&quot;,
          &quot;demand_2abfedbf464a993f7ea4&quot;,
          &quot;demand_319add76d3ac8f50fbe0&quot;,
          &quot;demand_347ce93969decf74ea86&quot;,
          &quot;demand_3ceb0f49c62a078f8a55&quot;,
          &quot;demand_3d08c880775f9f9ac1e7&quot;,
          &quot;demand_3e6cde98406f7453901b&quot;,
          &quot;demand_3f72c371567eb238315b&quot;,
          &quot;demand_3fdb35f17666f0d05802&quot;,
          &quot;demand_4531a752719eb527730a&quot;,
          &quot;demand_4dffd6199cd64056c3ae&quot;,
          &quot;demand_5e7715447833486ec098&quot;,
          &quot;demand_60fe8bfc7dbac9467679&quot;,
          &quot;demand_64278c426083d32e40eb&quot;,
          &quot;demand_66673f4cc0a1000c3364&quot;,
          &quot;demand_6b0d0ba67ed22c85c0b5&quot;,
          &quot;demand_6be9b2f5b849c10264a6&quot;,
          &quot;demand_70b2fa7b5c54a135467d&quot;,
          &quot;demand_72b9b88f0ac48b29155e&quot;,
          &quot;demand_74e011a283e3c2a7c497&quot;,
          &quot;demand_7eb0b5fdd5480d183860&quot;,
          &quot;demand_7f7f0145ff463e904092&quot;,
          &quot;demand_7ffb8ab6e5d4601295c9&quot;,
          &quot;demand_8d2a0ae336cd56890d75&quot;,
          &quot;demand_91fc1268f9aa69097200&quot;,
          &quot;demand_92f978725a6f48f73a92&quot;,
          &quot;demand_987ba4c1faeea4293fbb&quot;,
          &quot;demand_9a1e97e18f570f55846c&quot;,
          &quot;demand_9ce5af8a561b9c24b4a4&quot;,
          &quot;demand_a121999a238e2b343db5&quot;,
          &quot;demand_a7619d995eea12ea7ec0&quot;,
          &quot;demand_a830ab582af19c9ae211&quot;,
          &quot;demand_ac951b8bf04df1b81904&quot;,
          &quot;demand_b35a9011f4975e024454&quot;,
          &quot;demand_b39c68a83b1ada0552a5&quot;,
          &quot;demand_baf6040bb485b47d9e9a&quot;,
          &quot;demand_bfa79c9e2a33df5825eb&quot;,
          &quot;demand_c2f9f7d0546d1d204694&quot;,
          &quot;demand_c4aaa01e135b1d3c60fc&quot;,
          &quot;demand_cc1e7ca6c02583fb1fa1&quot;,
          &quot;demand_cde82ff41056af9b1987&quot;,
          &quot;demand_d75f7c02084be857e77c&quot;,
          &quot;demand_de974e2b6cdb2ec6815d&quot;,
          &quot;demand_dede86295c1db9f772b2&quot;,
          &quot;demand_e26dc8f02b4659d06e86&quot;,
          &quot;demand_e2b8a5b34dee8e4abd0e&quot;,
          &quot;demand_e480ec35cc1b8733e075&quot;,
          &quot;demand_eb8c53fc958b1eeaeb7f&quot;,
          &quot;demand_ebfc76d70055a0204f1b&quot;,
          &quot;demand_ecf094d1f91d32a49a29&quot;,
          &quot;demand_ef34de16517bcc0ba0dc&quot;,
          &quot;demand_f54f30d8eb9442c92ff5&quot;,
          &quot;demand_f7ebe9090e7e8e852b0e&quot;,
          &quot;demand_fa0d743285ad8d862d11&quot;,
          &quot;demand_fb0fb70eb3d7b7b5b6a8&quot;,
          &quot;demand_fb2050d056b0101a52c6&quot;,
          &quot;demand_fbddddbc2453964e4624&quot;,
          &quot;demand_fcda4d95d9313530c05b&quot;,
          &quot;demand_fcf417f85ceb391d20a2&quot;,
          &quot;demand_fcfb3c9f3b78737b0e31&quot;,
          &quot;demand_fe314a23bc872fb4b635&quot;
        ],
        &quot;compiled_goal&quot;: {
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
              &quot;kind&quot;: &quot;input&quot;,
              &quot;index&quot;: 0
            }
          },
          &quot;preserve&quot;: &quot;value&quot;,
          &quot;path&quot;: [],
          &quot;expected&quot;: {
            &quot;kind&quot;: &quot;input&quot;,
            &quot;index&quot;: 1
          },
          &quot;expected_path&quot;: [],
          &quot;reason&quot;: &quot;The write payload must be the response total value from the CFG total result.&quot;,
          &quot;id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;
        },
        &quot;sink_ids&quot;: [
          &quot;sink_3d32c2d913765f8ec8b1&quot;,
          &quot;sink_431a0c1fa101e978cc88&quot;,
          &quot;sink_5298b9fc4b95bf5e34ac&quot;,
          &quot;sink_6982d6acfff5c4808d1f&quot;,
          &quot;sink_836d6bb37efb1eefe31e&quot;,
          &quot;sink_8632d255f8657b506825&quot;,
          &quot;sink_9a3c4449a80a0bfeb411&quot;,
          &quot;sink_c2397cb75735b4bbf5ed&quot;,
          &quot;sink_ce54588f3e0fbdcec0e6&quot;,
          &quot;sink_d73d96f2b39e63cdaaad&quot;,
          &quot;sink_f5e30d631911b0c8db08&quot;
        ]
      }
    ],
    &quot;requirement&quot;: {
      &quot;id&quot;: &quot;R8&quot;,
      &quot;text&quot;: &quot;After the search, write the response&#x27;s total value to local count.txt.&quot;,
      &quot;evidences&quot;: [
        {
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;start_line&quot;: 21,
          &quot;end_line&quot;: 21,
          &quot;reason&quot;: &quot;Requires the post-search write of the response total to the specified local file.&quot;
        }
      ]
    },
    &quot;source_accounting&quot;: [
      {
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;start_line&quot;: 21,
        &quot;end_line&quot;: 21,
        &quot;disposition&quot;: &quot;requirement&quot;,
        &quot;requirement_ids&quot;: [
          &quot;R8&quot;
        ],
        &quot;issue_ids&quot;: [],
        &quot;reason&quot;: &quot;Requires writing the response total to local count.txt after the search.&quot;,
        &quot;quote&quot;: &quot;After the search, write the response&#x27;s total value to local count.txt.\n&quot;
      }
    ],
    &quot;realization&quot;: {
      &quot;requirement_id&quot;: &quot;R8&quot;,
      &quot;status&quot;: &quot;expressed&quot;,
      &quot;bindings&quot;: [
        {
          &quot;target&quot;: {
            &quot;instruction_id&quot;: &quot;ir_009&quot;,
            &quot;path&quot;: []
          },
          &quot;reason&quot;: &quot;The response total is selected from the search response before the write.&quot;
        },
        {
          &quot;target&quot;: {
            &quot;instruction_id&quot;: &quot;ir_010&quot;,
            &quot;path&quot;: []
          },
          &quot;reason&quot;: &quot;The local count.txt write consumes the extracted response total, and the requires-prior constraint preserves the after-search order.&quot;
        }
      ],
      &quot;gaps&quot;: [],
      &quot;goal_ids&quot;: [
        &quot;goal_a68e938e61f1884d7598&quot;,
        &quot;goal_b9a86bc8698a176813fb&quot;
      ],
      &quot;constraint_ids&quot;: [
        &quot;constraint_35e3a6a8eec50bad5a08&quot;
      ],
      &quot;has_applicable_goal&quot;: true
    }
  },
  {
    &quot;requirement_id&quot;: &quot;R9&quot;,
    &quot;source_accounting_indices&quot;: [
      22
    ],
    &quot;seeds&quot;: [
      {
        &quot;goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
        &quot;raw_pointer&quot;: &quot;/demands/0&quot;,
        &quot;derivation_ids&quot;: [
          &quot;demand_011b75f91d326ee990db&quot;,
          &quot;demand_01b3b70894daf5f7ee4a&quot;,
          &quot;demand_060d059caea61b0856a0&quot;,
          &quot;demand_12a7bcc23754ebcae14b&quot;,
          &quot;demand_17152c60a6ae1d21b8de&quot;,
          &quot;demand_1ce9c7d3a9f371fab647&quot;,
          &quot;demand_210e7a5f9f813242d2a2&quot;,
          &quot;demand_226185ce3ae84e4a5551&quot;,
          &quot;demand_26557e406502932fbfec&quot;,
          &quot;demand_2ec2c86f2aec01f55f79&quot;,
          &quot;demand_2f3a701de8654081301e&quot;,
          &quot;demand_2f867e60ea7f9050757c&quot;,
          &quot;demand_375081c2e3bbc0ee0d77&quot;,
          &quot;demand_38008f50db63e3e59448&quot;,
          &quot;demand_3f2f1eee3c0f48917732&quot;,
          &quot;demand_477b6ab435de27de43c7&quot;,
          &quot;demand_5d5dea924b3d86941903&quot;,
          &quot;demand_61409dc5b007f9f16793&quot;,
          &quot;demand_61b23ba86b050f08f580&quot;,
          &quot;demand_6b68b76e3b74e7967bfa&quot;,
          &quot;demand_6c0528f82772a7fe8746&quot;,
          &quot;demand_73141ae109e6fb35cff1&quot;,
          &quot;demand_7493dde427fb4d2ef69a&quot;,
          &quot;demand_750834fe82201bbad0cc&quot;,
          &quot;demand_7b3a35330b12e8ba140b&quot;,
          &quot;demand_7b570e9c2f7e78cca284&quot;,
          &quot;demand_7d177a9a7565bddaea4f&quot;,
          &quot;demand_82c47223cb8495272a52&quot;,
          &quot;demand_8619e9761ff560faf655&quot;,
          &quot;demand_8b2b878cce0eaf2a51fe&quot;,
          &quot;demand_8c7c2e131b5181c9f257&quot;,
          &quot;demand_90cd1510cfe0663a2e57&quot;,
          &quot;demand_941c77f8f1ee40589119&quot;,
          &quot;demand_95fdaabbc06279c05636&quot;,
          &quot;demand_9b45307c579d6df84415&quot;,
          &quot;demand_a0200b367a9ee1cac92c&quot;,
          &quot;demand_a250ebc33e7210d80f67&quot;,
          &quot;demand_a8f2037aae808da9a583&quot;,
          &quot;demand_aa3ec9d16d7ca210e3bc&quot;,
          &quot;demand_ad7929f80ff7dd7547bb&quot;,
          &quot;demand_ada22b605a53a043a5c3&quot;,
          &quot;demand_adb35267dcc6986504be&quot;,
          &quot;demand_aea05ec71fbabb48bf35&quot;,
          &quot;demand_affde27b049c81080bfa&quot;,
          &quot;demand_b21450a98657d0faa15e&quot;,
          &quot;demand_b4acd6d8777d40b09cb6&quot;,
          &quot;demand_b93c9007bb675892fdef&quot;,
          &quot;demand_bd3300adbbbdd1805a29&quot;,
          &quot;demand_bdf78099635501633b42&quot;,
          &quot;demand_c1770df052c38c03b8d8&quot;,
          &quot;demand_c247c6618cffff5b721e&quot;,
          &quot;demand_c296e5b640c7b725f18b&quot;,
          &quot;demand_c58a57d27f2007c8e1e6&quot;,
          &quot;demand_d1131151dfb681ad1a1f&quot;,
          &quot;demand_d378b0df310d8e750810&quot;,
          &quot;demand_d3d6b54aead7cea69e58&quot;,
          &quot;demand_d52b25361812e6b5276e&quot;,
          &quot;demand_d6f1b29ca884fc09ba2f&quot;,
          &quot;demand_d81c094ea22be28c9a11&quot;,
          &quot;demand_d8e4a9da93b2e2d39b35&quot;,
          &quot;demand_d9e2820869128653c624&quot;,
          &quot;demand_dfed630e0a047cd37ba5&quot;,
          &quot;demand_e040a0805294f39b8a2b&quot;,
          &quot;demand_e89d369b316e5ed308f9&quot;,
          &quot;demand_eaa1740ae1512b5396c9&quot;,
          &quot;demand_f0b30b8b6fb7dd22cd2a&quot;,
          &quot;demand_f23311e087bb37baeef9&quot;,
          &quot;demand_f85c7bec526edab12a40&quot;,
          &quot;demand_fdb88a29a419e92159ef&quot;,
          &quot;demand_ffb8870545afc91e7312&quot;
        ],
        &quot;compiled_goal&quot;: {
          &quot;requirement_id&quot;: &quot;R9&quot;,
          &quot;target&quot;: {
            &quot;instruction_id&quot;: &quot;ir_012&quot;,
            &quot;side&quot;: &quot;input&quot;,
            &quot;index&quot;: 0
          },
          &quot;preserve&quot;: &quot;value&quot;,
          &quot;path&quot;: [],
          &quot;expected&quot;: null,
          &quot;expected_path&quot;: [],
          &quot;reason&quot;: &quot;Preserve the search response items value unchanged at the return input.&quot;,
          &quot;id&quot;: &quot;goal_6e5ca31142833529f175&quot;
        },
        &quot;sink_ids&quot;: [
          &quot;sink_3d32c2d913765f8ec8b1&quot;,
          &quot;sink_431a0c1fa101e978cc88&quot;,
          &quot;sink_4c227ba36482bf5e5a54&quot;,
          &quot;sink_5298b9fc4b95bf5e34ac&quot;,
          &quot;sink_6982d6acfff5c4808d1f&quot;,
          &quot;sink_836d6bb37efb1eefe31e&quot;,
          &quot;sink_8632d255f8657b506825&quot;,
          &quot;sink_c2397cb75735b4bbf5ed&quot;,
          &quot;sink_ce54588f3e0fbdcec0e6&quot;,
          &quot;sink_f5e30d631911b0c8db08&quot;
        ]
      }
    ],
    &quot;requirement&quot;: {
      &quot;id&quot;: &quot;R9&quot;,
      &quot;text&quot;: &quot;Return the search response&#x27;s items value unchanged.&quot;,
      &quot;evidences&quot;: [
        {
          &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
          &quot;start_line&quot;: 23,
          &quot;end_line&quot;: 23,
          &quot;reason&quot;: &quot;Requires returning the response items value without change.&quot;
        }
      ]
    },
    &quot;source_accounting&quot;: [
      {
        &quot;file&quot;: &quot;skill/references/workflow.md&quot;,
        &quot;start_line&quot;: 23,
        &quot;end_line&quot;: 23,
        &quot;disposition&quot;: &quot;requirement&quot;,
        &quot;requirement_ids&quot;: [
          &quot;R9&quot;
        ],
        &quot;issue_ids&quot;: [],
        &quot;reason&quot;: &quot;Requires returning the response items value unchanged.&quot;,
        &quot;quote&quot;: &quot;Return the search response&#x27;s items value unchanged.\n&quot;
      }
    ],
    &quot;realization&quot;: {
      &quot;requirement_id&quot;: &quot;R9&quot;,
      &quot;status&quot;: &quot;expressed&quot;,
      &quot;bindings&quot;: [
        {
          &quot;target&quot;: {
            &quot;instruction_id&quot;: &quot;ir_011&quot;,
            &quot;path&quot;: []
          },
          &quot;reason&quot;: &quot;The response items are selected unchanged from the search response.&quot;
        },
        {
          &quot;target&quot;: {
            &quot;instruction_id&quot;: &quot;ir_012&quot;,
            &quot;path&quot;: []
          },
          &quot;reason&quot;: &quot;The CFG return instruction returns the selected response items input.&quot;
        }
      ],
      &quot;gaps&quot;: [],
      &quot;goal_ids&quot;: [
        &quot;goal_6e5ca31142833529f175&quot;
      ],
      &quot;constraint_ids&quot;: [],
      &quot;has_applicable_goal&quot;: true
    }
  }
]</pre>

## Sink comparisons

<a id="sink-79ee11ce30e6fae4e907"></a>

### sink\_3d32c2d913765f8ec8b1

<details><summary>Boundary and actual payload</summary><pre>{
  &quot;boundary&quot;: {
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;event_index&quot;: 5,
    &quot;op_index&quot;: 0,
    &quot;body_event_index&quot;: null,
    &quot;scope&quot;: null,
    &quot;target&quot;: &quot;__compiled_model_context__&quot;,
    &quot;sink_type&quot;: &quot;model_observe&quot;,
    &quot;exposure_level&quot;: 2
  },
  &quot;actual_payload&quot;: [
    {
      &quot;operation_id&quot;: &quot;op_ir_007:e5:a0&quot;,
      &quot;position&quot;: {
        &quot;instruction_id&quot;: &quot;ir_007&quot;,
        &quot;event_index&quot;: 5,
        &quot;op_index&quot;: 0,
        &quot;body_event_index&quot;: null,
        &quot;instance_index&quot;: null
      },
      &quot;inputs&quot;: [
        [
          &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
          &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
          &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
          &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;
        ]
      ]
    }
  ]
}</pre></details>

#### Demand-driving requirements

- **R8:** After the search, write the response's total value to local count\.txt\.

- **R9:** Return the search response's items value unchanged\.

<details><summary>Full boundary-specific preservation demand</summary><p>Unestablished demand is not a deletion certificate; all conservative retention and relevant limitations constrain a reduction.</p><pre>{
  &quot;demanded_information&quot;: [
    &quot;demand_1527693ead3389526798&quot;,
    &quot;demand_3f2f1eee3c0f48917732&quot;
  ],
  &quot;conservative_retention&quot;: [],
  &quot;unestablished_ranges&quot;: [
    {
      &quot;operation_id&quot;: &quot;op_ir_007:e5:a0&quot;,
      &quot;input_index&quot;: 0,
      &quot;data_ids&quot;: [
        &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
        &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
        &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
        &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;
      ],
      &quot;description&quot;: &quot;Requirements constrain only the listed information properties. Preserve structure and all listed demands; no replacement execution was verified.&quot;,
      &quot;scope&quot;: &quot;outside_listed_properties&quot;
    }
  ],
  &quot;limitations&quot;: [
    &quot;diagnostic_0d29a666fd3a446e29e4&quot;,
    &quot;diagnostic_23efa867ad6a3e638305&quot;
  ]
}</pre></details>

No declared sensitive range reaches this sink in the supported relationships. This is not a non-sensitive or no-DOE certificate.

#### Sink limitations

<pre>[
  {
    &quot;id&quot;: &quot;diagnostic_0d29a666fd3a446e29e4&quot;,
    &quot;code&quot;: &quot;unbound_requirement&quot;,
    &quot;reason&quot;: &quot;No applicable demand goal is available; this does not mean the requirement can be omitted.&quot;,
    &quot;instruction_id&quot;: null,
    &quot;operation_id&quot;: null,
    &quot;blocking&quot;: true
  },
  {
    &quot;id&quot;: &quot;diagnostic_23efa867ad6a3e638305&quot;,
    &quot;code&quot;: &quot;requirement_expression_gap&quot;,
    &quot;reason&quot;: &quot;This requirement is not fully expressed as positive demands and supported constraints. No program-verifiable local impact boundary is available; retain it as a global limitation.&quot;,
    &quot;instruction_id&quot;: null,
    &quot;operation_id&quot;: null,
    &quot;blocking&quot;: true
  }
]</pre>

<a id="sink-60f5a561ec8b8893c53a"></a>

### sink\_431a0c1fa101e978cc88

<details><summary>Boundary and actual payload</summary><pre>{
  &quot;boundary&quot;: {
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;event_index&quot;: 1,
    &quot;op_index&quot;: 0,
    &quot;body_event_index&quot;: null,
    &quot;scope&quot;: null,
    &quot;target&quot;: &quot;__compiled_model_context__&quot;,
    &quot;sink_type&quot;: &quot;model_observe&quot;,
    &quot;exposure_level&quot;: 2
  },
  &quot;actual_payload&quot;: [
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
          &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
        ]
      ]
    }
  ]
}</pre></details>

#### Demand-driving requirements

- **R3:** When from\_date is present in the request, pass its value unchanged as the from\_date argument; the accepted format is YYYY\-MM\-DD\.

- **R8:** After the search, write the response's total value to local count\.txt\.

- **R9:** Return the search response's items value unchanged\.

<details><summary>Full boundary-specific preservation demand</summary><p>Unestablished demand is not a deletion certificate; all conservative retention and relevant limitations constrain a reduction.</p><pre>{
  &quot;demanded_information&quot;: [
    &quot;demand_21fc99a5f39f0a12bb33&quot;,
    &quot;demand_826a46cc7dab97aadc12&quot;
  ],
  &quot;conservative_retention&quot;: [
    &quot;demand_01b3b70894daf5f7ee4a&quot;,
    &quot;demand_38008f50db63e3e59448&quot;,
    &quot;demand_f7ebe9090e7e8e852b0e&quot;,
    &quot;demand_fa0d743285ad8d862d11&quot;
  ],
  &quot;unestablished_ranges&quot;: [],
  &quot;limitations&quot;: [
    &quot;diagnostic_0d29a666fd3a446e29e4&quot;,
    &quot;diagnostic_23efa867ad6a3e638305&quot;
  ]
}</pre></details>

No declared sensitive range reaches this sink in the supported relationships. This is not a non-sensitive or no-DOE certificate.

#### Sink limitations

<pre>[
  {
    &quot;id&quot;: &quot;diagnostic_0d29a666fd3a446e29e4&quot;,
    &quot;code&quot;: &quot;unbound_requirement&quot;,
    &quot;reason&quot;: &quot;No applicable demand goal is available; this does not mean the requirement can be omitted.&quot;,
    &quot;instruction_id&quot;: null,
    &quot;operation_id&quot;: null,
    &quot;blocking&quot;: true
  },
  {
    &quot;id&quot;: &quot;diagnostic_23efa867ad6a3e638305&quot;,
    &quot;code&quot;: &quot;requirement_expression_gap&quot;,
    &quot;reason&quot;: &quot;This requirement is not fully expressed as positive demands and supported constraints. No program-verifiable local impact boundary is available; retain it as a global limitation.&quot;,
    &quot;instruction_id&quot;: null,
    &quot;operation_id&quot;: null,
    &quot;blocking&quot;: true
  }
]</pre>

<a id="sink-0a941bb39e637a7d4d5b"></a>

### sink\_4c227ba36482bf5e5a54

<details><summary>Boundary and actual payload</summary><pre>{
  &quot;boundary&quot;: {
    &quot;instruction_id&quot;: &quot;ir_011&quot;,
    &quot;event_index&quot;: 0,
    &quot;op_index&quot;: 0,
    &quot;body_event_index&quot;: null,
    &quot;scope&quot;: null,
    &quot;target&quot;: &quot;__compiled_model_context__&quot;,
    &quot;sink_type&quot;: &quot;model_observe&quot;,
    &quot;exposure_level&quot;: 2
  },
  &quot;actual_payload&quot;: [
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
          &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
          &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
          &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
          &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;
        ]
      ]
    }
  ]
}</pre></details>

#### Demand-driving requirements

- **R9:** Return the search response's items value unchanged\.

<details><summary>Full boundary-specific preservation demand</summary><p>Unestablished demand is not a deletion certificate; all conservative retention and relevant limitations constrain a reduction.</p><pre>{
  &quot;demanded_information&quot;: [
    &quot;demand_aea05ec71fbabb48bf35&quot;
  ],
  &quot;conservative_retention&quot;: [],
  &quot;unestablished_ranges&quot;: [
    {
      &quot;operation_id&quot;: &quot;op_ir_011:e0:a0&quot;,
      &quot;input_index&quot;: 0,
      &quot;data_ids&quot;: [
        &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
        &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
        &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
        &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;
      ],
      &quot;description&quot;: &quot;Requirements constrain only the listed information properties. Preserve structure and all listed demands; no replacement execution was verified.&quot;,
      &quot;scope&quot;: &quot;outside_listed_properties&quot;
    }
  ],
  &quot;limitations&quot;: [
    &quot;diagnostic_0d29a666fd3a446e29e4&quot;,
    &quot;diagnostic_23efa867ad6a3e638305&quot;
  ]
}</pre></details>

No declared sensitive range reaches this sink in the supported relationships. This is not a non-sensitive or no-DOE certificate.

#### Sink limitations

<pre>[
  {
    &quot;id&quot;: &quot;diagnostic_0d29a666fd3a446e29e4&quot;,
    &quot;code&quot;: &quot;unbound_requirement&quot;,
    &quot;reason&quot;: &quot;No applicable demand goal is available; this does not mean the requirement can be omitted.&quot;,
    &quot;instruction_id&quot;: null,
    &quot;operation_id&quot;: null,
    &quot;blocking&quot;: true
  },
  {
    &quot;id&quot;: &quot;diagnostic_23efa867ad6a3e638305&quot;,
    &quot;code&quot;: &quot;requirement_expression_gap&quot;,
    &quot;reason&quot;: &quot;This requirement is not fully expressed as positive demands and supported constraints. No program-verifiable local impact boundary is available; retain it as a global limitation.&quot;,
    &quot;instruction_id&quot;: null,
    &quot;operation_id&quot;: null,
    &quot;blocking&quot;: true
  }
]</pre>

<a id="sink-cdfe6e71766a768ad128"></a>

### sink\_5298b9fc4b95bf5e34ac

<details><summary>Boundary and actual payload</summary><pre>{
  &quot;boundary&quot;: {
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;event_index&quot;: 0,
    &quot;op_index&quot;: 0,
    &quot;body_event_index&quot;: null,
    &quot;scope&quot;: null,
    &quot;target&quot;: &quot;__compiled_model_context__&quot;,
    &quot;sink_type&quot;: &quot;model_observe&quot;,
    &quot;exposure_level&quot;: 2
  },
  &quot;actual_payload&quot;: [
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
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ]
      ]
    }
  ]
}</pre></details>

#### Demand-driving requirements

- **R3:** When from\_date is present in the request, pass its value unchanged as the from\_date argument; the accepted format is YYYY\-MM\-DD\.

- **R4:** When from\_date is missing from the request, omit the from\_date argument from this same index\.search call, applying query\.yaml's missing\-argument setting\.

- **R8:** After the search, write the response's total value to local count\.txt\.

- **R9:** Return the search response's items value unchanged\.

<details><summary>Full boundary-specific preservation demand</summary><p>Unestablished demand is not a deletion certificate; all conservative retention and relevant limitations constrain a reduction.</p><pre>{
  &quot;demanded_information&quot;: [
    &quot;demand_040c46ea630a77b3f3a9&quot;,
    &quot;demand_8bac55342e62890a8849&quot;,
    &quot;demand_90c2453cf4e8850e2f87&quot;
  ],
  &quot;conservative_retention&quot;: [
    &quot;demand_148d47ecfc12a07d92c2&quot;,
    &quot;demand_82c47223cb8495272a52&quot;,
    &quot;demand_d81c094ea22be28c9a11&quot;,
    &quot;demand_ebfc76d70055a0204f1b&quot;
  ],
  &quot;unestablished_ranges&quot;: [
    {
      &quot;operation_id&quot;: &quot;op_ir_004:e0:a0&quot;,
      &quot;input_index&quot;: 0,
      &quot;data_ids&quot;: [
        &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
      ],
      &quot;description&quot;: &quot;Requirements constrain only the listed information properties. Preserve structure and all listed demands; no replacement execution was verified.&quot;,
      &quot;scope&quot;: &quot;outside_listed_properties&quot;
    }
  ],
  &quot;limitations&quot;: [
    &quot;diagnostic_0d29a666fd3a446e29e4&quot;,
    &quot;diagnostic_23efa867ad6a3e638305&quot;
  ]
}</pre></details>

No declared sensitive range reaches this sink in the supported relationships. This is not a non-sensitive or no-DOE certificate.

#### Sink limitations

<pre>[
  {
    &quot;id&quot;: &quot;diagnostic_0d29a666fd3a446e29e4&quot;,
    &quot;code&quot;: &quot;unbound_requirement&quot;,
    &quot;reason&quot;: &quot;No applicable demand goal is available; this does not mean the requirement can be omitted.&quot;,
    &quot;instruction_id&quot;: null,
    &quot;operation_id&quot;: null,
    &quot;blocking&quot;: true
  },
  {
    &quot;id&quot;: &quot;diagnostic_23efa867ad6a3e638305&quot;,
    &quot;code&quot;: &quot;requirement_expression_gap&quot;,
    &quot;reason&quot;: &quot;This requirement is not fully expressed as positive demands and supported constraints. No program-verifiable local impact boundary is available; retain it as a global limitation.&quot;,
    &quot;instruction_id&quot;: null,
    &quot;operation_id&quot;: null,
    &quot;blocking&quot;: true
  }
]</pre>

<a id="sink-4e5a6e646e28bd1de2cb"></a>

### sink\_6982d6acfff5c4808d1f

<details><summary>Boundary and actual payload</summary><pre>{
  &quot;boundary&quot;: {
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;event_index&quot;: 0,
    &quot;op_index&quot;: 0,
    &quot;body_event_index&quot;: null,
    &quot;scope&quot;: null,
    &quot;target&quot;: &quot;__compiled_model_context__&quot;,
    &quot;sink_type&quot;: &quot;model_observe&quot;,
    &quot;exposure_level&quot;: 2
  },
  &quot;actual_payload&quot;: [
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
          &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
        ],
        [
          &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
        ],
        [
          &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
        ]
      ]
    }
  ]
}</pre></details>

#### Demand-driving requirements

- **R2:** Call index\.search exactly once, using request\.term unchanged as its query argument\.

- **R3:** When from\_date is present in the request, pass its value unchanged as the from\_date argument; the accepted format is YYYY\-MM\-DD\.

- **R4:** When from\_date is missing from the request, omit the from\_date argument from this same index\.search call, applying query\.yaml's missing\-argument setting\.

- **R5:** When limit is present in the request, pass its value unchanged as the limit argument\.

- **R6:** When limit is missing from the request, omit the limit argument from this same index\.search call, applying query\.yaml's missing\-argument setting\.

- **R8:** After the search, write the response's total value to local count\.txt\.

- **R9:** Return the search response's items value unchanged\.

<details><summary>Full boundary-specific preservation demand</summary><p>Unestablished demand is not a deletion certificate; all conservative retention and relevant limitations constrain a reduction.</p><pre>{
  &quot;demanded_information&quot;: [
    &quot;demand_0f342157a8515367497a&quot;,
    &quot;demand_11c1292b507a99d484a9&quot;,
    &quot;demand_1cf2bd3a1b6cefaeebf0&quot;,
    &quot;demand_4cb095dcbfa2c33d77ee&quot;,
    &quot;demand_bf1cab20b360f6dd5dd1&quot;
  ],
  &quot;conservative_retention&quot;: [
    &quot;demand_4531a752719eb527730a&quot;,
    &quot;demand_7b570e9c2f7e78cca284&quot;,
    &quot;demand_a250ebc33e7210d80f67&quot;,
    &quot;demand_f85c7bec526edab12a40&quot;,
    &quot;demand_fb0fb70eb3d7b7b5b6a8&quot;,
    &quot;demand_fb2050d056b0101a52c6&quot;
  ],
  &quot;unestablished_ranges&quot;: [
    {
      &quot;operation_id&quot;: &quot;op_ir_007:e0:a0&quot;,
      &quot;input_index&quot;: 1,
      &quot;data_ids&quot;: [
        &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
      ],
      &quot;description&quot;: &quot;Requirements constrain only the listed information properties. Preserve structure and all listed demands; no replacement execution was verified.&quot;,
      &quot;scope&quot;: &quot;outside_listed_properties&quot;
    },
    {
      &quot;operation_id&quot;: &quot;op_ir_007:e0:a0&quot;,
      &quot;input_index&quot;: 2,
      &quot;data_ids&quot;: [
        &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
      ],
      &quot;description&quot;: &quot;Requirements constrain only the listed information properties. Preserve structure and all listed demands; no replacement execution was verified.&quot;,
      &quot;scope&quot;: &quot;outside_listed_properties&quot;
    }
  ],
  &quot;limitations&quot;: [
    &quot;diagnostic_0d29a666fd3a446e29e4&quot;,
    &quot;diagnostic_23efa867ad6a3e638305&quot;
  ]
}</pre></details>

No declared sensitive range reaches this sink in the supported relationships. This is not a non-sensitive or no-DOE certificate.

#### Sink limitations

<pre>[
  {
    &quot;id&quot;: &quot;diagnostic_0d29a666fd3a446e29e4&quot;,
    &quot;code&quot;: &quot;unbound_requirement&quot;,
    &quot;reason&quot;: &quot;No applicable demand goal is available; this does not mean the requirement can be omitted.&quot;,
    &quot;instruction_id&quot;: null,
    &quot;operation_id&quot;: null,
    &quot;blocking&quot;: true
  },
  {
    &quot;id&quot;: &quot;diagnostic_23efa867ad6a3e638305&quot;,
    &quot;code&quot;: &quot;requirement_expression_gap&quot;,
    &quot;reason&quot;: &quot;This requirement is not fully expressed as positive demands and supported constraints. No program-verifiable local impact boundary is available; retain it as a global limitation.&quot;,
    &quot;instruction_id&quot;: null,
    &quot;operation_id&quot;: null,
    &quot;blocking&quot;: true
  }
]</pre>

<a id="sink-3ba586042e58c59af3ef"></a>

### sink\_836d6bb37efb1eefe31e

<details><summary>Boundary and actual payload</summary><pre>{
  &quot;boundary&quot;: {
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;event_index&quot;: 0,
    &quot;op_index&quot;: 0,
    &quot;body_event_index&quot;: null,
    &quot;scope&quot;: null,
    &quot;target&quot;: &quot;__compiled_model_context__&quot;,
    &quot;sink_type&quot;: &quot;model_observe&quot;,
    &quot;exposure_level&quot;: 2
  },
  &quot;actual_payload&quot;: [
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
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ]
      ]
    }
  ]
}</pre></details>

#### Demand-driving requirements

- **R5:** When limit is present in the request, pass its value unchanged as the limit argument\.

- **R6:** When limit is missing from the request, omit the limit argument from this same index\.search call, applying query\.yaml's missing\-argument setting\.

- **R8:** After the search, write the response's total value to local count\.txt\.

- **R9:** Return the search response's items value unchanged\.

<details><summary>Full boundary-specific preservation demand</summary><p>Unestablished demand is not a deletion certificate; all conservative retention and relevant limitations constrain a reduction.</p><pre>{
  &quot;demanded_information&quot;: [
    &quot;demand_c517668c72349b7793ae&quot;,
    &quot;demand_d7ec078f0532d17ef79e&quot;,
    &quot;demand_ed053d38c1c3c958466c&quot;
  ],
  &quot;conservative_retention&quot;: [
    &quot;demand_9a1e97e18f570f55846c&quot;,
    &quot;demand_d3d6b54aead7cea69e58&quot;,
    &quot;demand_f23311e087bb37baeef9&quot;,
    &quot;demand_fe314a23bc872fb4b635&quot;
  ],
  &quot;unestablished_ranges&quot;: [
    {
      &quot;operation_id&quot;: &quot;op_ir_005:e0:a0&quot;,
      &quot;input_index&quot;: 0,
      &quot;data_ids&quot;: [
        &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
      ],
      &quot;description&quot;: &quot;Requirements constrain only the listed information properties. Preserve structure and all listed demands; no replacement execution was verified.&quot;,
      &quot;scope&quot;: &quot;outside_listed_properties&quot;
    }
  ],
  &quot;limitations&quot;: [
    &quot;diagnostic_0d29a666fd3a446e29e4&quot;,
    &quot;diagnostic_23efa867ad6a3e638305&quot;
  ]
}</pre></details>

No declared sensitive range reaches this sink in the supported relationships. This is not a non-sensitive or no-DOE certificate.

#### Sink limitations

<pre>[
  {
    &quot;id&quot;: &quot;diagnostic_0d29a666fd3a446e29e4&quot;,
    &quot;code&quot;: &quot;unbound_requirement&quot;,
    &quot;reason&quot;: &quot;No applicable demand goal is available; this does not mean the requirement can be omitted.&quot;,
    &quot;instruction_id&quot;: null,
    &quot;operation_id&quot;: null,
    &quot;blocking&quot;: true
  },
  {
    &quot;id&quot;: &quot;diagnostic_23efa867ad6a3e638305&quot;,
    &quot;code&quot;: &quot;requirement_expression_gap&quot;,
    &quot;reason&quot;: &quot;This requirement is not fully expressed as positive demands and supported constraints. No program-verifiable local impact boundary is available; retain it as a global limitation.&quot;,
    &quot;instruction_id&quot;: null,
    &quot;operation_id&quot;: null,
    &quot;blocking&quot;: true
  }
]</pre>

<a id="sink-9244162a65f1dab10c01"></a>

### sink\_8632d255f8657b506825

<details><summary>Boundary and actual payload</summary><pre>{
  &quot;boundary&quot;: {
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;event_index&quot;: 0,
    &quot;op_index&quot;: 0,
    &quot;body_event_index&quot;: null,
    &quot;scope&quot;: null,
    &quot;target&quot;: &quot;__compiled_model_context__&quot;,
    &quot;sink_type&quot;: &quot;model_observe&quot;,
    &quot;exposure_level&quot;: 2
  },
  &quot;actual_payload&quot;: [
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
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ]
      ]
    }
  ]
}</pre></details>

#### Demand-driving requirements

- **R2:** Call index\.search exactly once, using request\.term unchanged as its query argument\.

- **R8:** After the search, write the response's total value to local count\.txt\.

- **R9:** Return the search response's items value unchanged\.

<details><summary>Full boundary-specific preservation demand</summary><p>Unestablished demand is not a deletion certificate; all conservative retention and relevant limitations constrain a reduction.</p><pre>{
  &quot;demanded_information&quot;: [
    &quot;demand_5d9944aca9d0f5b3af9e&quot;
  ],
  &quot;conservative_retention&quot;: [
    &quot;demand_3e6cde98406f7453901b&quot;,
    &quot;demand_c296e5b640c7b725f18b&quot;
  ],
  &quot;unestablished_ranges&quot;: [
    {
      &quot;operation_id&quot;: &quot;op_ir_003:e0:a0&quot;,
      &quot;input_index&quot;: 0,
      &quot;data_ids&quot;: [
        &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
      ],
      &quot;description&quot;: &quot;Requirements constrain only the listed information properties. Preserve structure and all listed demands; no replacement execution was verified.&quot;,
      &quot;scope&quot;: &quot;outside_listed_properties&quot;
    }
  ],
  &quot;limitations&quot;: [
    &quot;diagnostic_0d29a666fd3a446e29e4&quot;,
    &quot;diagnostic_23efa867ad6a3e638305&quot;
  ]
}</pre></details>

No declared sensitive range reaches this sink in the supported relationships. This is not a non-sensitive or no-DOE certificate.

#### Sink limitations

<pre>[
  {
    &quot;id&quot;: &quot;diagnostic_0d29a666fd3a446e29e4&quot;,
    &quot;code&quot;: &quot;unbound_requirement&quot;,
    &quot;reason&quot;: &quot;No applicable demand goal is available; this does not mean the requirement can be omitted.&quot;,
    &quot;instruction_id&quot;: null,
    &quot;operation_id&quot;: null,
    &quot;blocking&quot;: true
  },
  {
    &quot;id&quot;: &quot;diagnostic_23efa867ad6a3e638305&quot;,
    &quot;code&quot;: &quot;requirement_expression_gap&quot;,
    &quot;reason&quot;: &quot;This requirement is not fully expressed as positive demands and supported constraints. No program-verifiable local impact boundary is available; retain it as a global limitation.&quot;,
    &quot;instruction_id&quot;: null,
    &quot;operation_id&quot;: null,
    &quot;blocking&quot;: true
  }
]</pre>

<a id="sink-e769559260c304bdb061"></a>

### sink\_9a3c4449a80a0bfeb411

<details><summary>Boundary and actual payload</summary><pre>{
  &quot;boundary&quot;: {
    &quot;instruction_id&quot;: &quot;ir_009&quot;,
    &quot;event_index&quot;: 0,
    &quot;op_index&quot;: 0,
    &quot;body_event_index&quot;: null,
    &quot;scope&quot;: null,
    &quot;target&quot;: &quot;__compiled_model_context__&quot;,
    &quot;sink_type&quot;: &quot;model_observe&quot;,
    &quot;exposure_level&quot;: 2
  },
  &quot;actual_payload&quot;: [
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
          &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
          &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
          &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
          &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;
        ]
      ]
    }
  ]
}</pre></details>

#### Demand-driving requirements

- **R8:** After the search, write the response's total value to local count\.txt\.

<details><summary>Full boundary-specific preservation demand</summary><p>Unestablished demand is not a deletion certificate; all conservative retention and relevant limitations constrain a reduction.</p><pre>{
  &quot;demanded_information&quot;: [
    &quot;demand_3fdb35f17666f0d05802&quot;
  ],
  &quot;conservative_retention&quot;: [],
  &quot;unestablished_ranges&quot;: [
    {
      &quot;operation_id&quot;: &quot;op_ir_009:e0:a0&quot;,
      &quot;input_index&quot;: 0,
      &quot;data_ids&quot;: [
        &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
        &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
        &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
        &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;
      ],
      &quot;description&quot;: &quot;Requirements constrain only the listed information properties. Preserve structure and all listed demands; no replacement execution was verified.&quot;,
      &quot;scope&quot;: &quot;outside_listed_properties&quot;
    }
  ],
  &quot;limitations&quot;: [
    &quot;diagnostic_0d29a666fd3a446e29e4&quot;,
    &quot;diagnostic_23efa867ad6a3e638305&quot;
  ]
}</pre></details>

No declared sensitive range reaches this sink in the supported relationships. This is not a non-sensitive or no-DOE certificate.

#### Sink limitations

<pre>[
  {
    &quot;id&quot;: &quot;diagnostic_0d29a666fd3a446e29e4&quot;,
    &quot;code&quot;: &quot;unbound_requirement&quot;,
    &quot;reason&quot;: &quot;No applicable demand goal is available; this does not mean the requirement can be omitted.&quot;,
    &quot;instruction_id&quot;: null,
    &quot;operation_id&quot;: null,
    &quot;blocking&quot;: true
  },
  {
    &quot;id&quot;: &quot;diagnostic_23efa867ad6a3e638305&quot;,
    &quot;code&quot;: &quot;requirement_expression_gap&quot;,
    &quot;reason&quot;: &quot;This requirement is not fully expressed as positive demands and supported constraints. No program-verifiable local impact boundary is available; retain it as a global limitation.&quot;,
    &quot;instruction_id&quot;: null,
    &quot;operation_id&quot;: null,
    &quot;blocking&quot;: true
  }
]</pre>

<a id="sink-6c8495df7975f7014a02"></a>

### sink\_c2397cb75735b4bbf5ed

<details><summary>Boundary and actual payload</summary><pre>{
  &quot;boundary&quot;: {
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;event_index&quot;: 1,
    &quot;op_index&quot;: 0,
    &quot;body_event_index&quot;: null,
    &quot;scope&quot;: null,
    &quot;target&quot;: &quot;__compiled_model_context__&quot;,
    &quot;sink_type&quot;: &quot;model_observe&quot;,
    &quot;exposure_level&quot;: 2
  },
  &quot;actual_payload&quot;: [
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
          &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
        ]
      ]
    }
  ]
}</pre></details>

#### Demand-driving requirements

- **R2:** Call index\.search exactly once, using request\.term unchanged as its query argument\.

- **R3:** When from\_date is present in the request, pass its value unchanged as the from\_date argument; the accepted format is YYYY\-MM\-DD\.

- **R4:** When from\_date is missing from the request, omit the from\_date argument from this same index\.search call, applying query\.yaml's missing\-argument setting\.

- **R5:** When limit is present in the request, pass its value unchanged as the limit argument\.

- **R6:** When limit is missing from the request, omit the limit argument from this same index\.search call, applying query\.yaml's missing\-argument setting\.

- **R8:** After the search, write the response's total value to local count\.txt\.

- **R9:** Return the search response's items value unchanged\.

<details><summary>Full boundary-specific preservation demand</summary><p>Unestablished demand is not a deletion certificate; all conservative retention and relevant limitations constrain a reduction.</p><pre>{
  &quot;demanded_information&quot;: [
    &quot;demand_124ab7fabe6068059b38&quot;,
    &quot;demand_24a23be128f53091c993&quot;,
    &quot;demand_818be2d98b4452eeedc4&quot;,
    &quot;demand_ad7a3c380dd29a60d6eb&quot;,
    &quot;demand_c8563fb46c01ac50aa1a&quot;,
    &quot;demand_cdb9b6806ba2be68aa2a&quot;,
    &quot;demand_ee03d6918aa2bfde483d&quot;
  ],
  &quot;conservative_retention&quot;: [
    &quot;demand_0fb904054ffe8db7cff2&quot;,
    &quot;demand_2309bafb3909dcb19085&quot;,
    &quot;demand_4dffd6199cd64056c3ae&quot;,
    &quot;demand_66673f4cc0a1000c3364&quot;,
    &quot;demand_6b68b76e3b74e7967bfa&quot;,
    &quot;demand_7493dde427fb4d2ef69a&quot;,
    &quot;demand_90cd1510cfe0663a2e57&quot;,
    &quot;demand_987ba4c1faeea4293fbb&quot;,
    &quot;demand_d9e2820869128653c624&quot;,
    &quot;demand_e89d369b316e5ed308f9&quot;
  ],
  &quot;unestablished_ranges&quot;: [
    {
      &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
      &quot;input_index&quot;: 0,
      &quot;data_ids&quot;: [
        &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
      ],
      &quot;description&quot;: &quot;Requirements constrain only the listed information properties. Preserve structure and all listed demands; no replacement execution was verified.&quot;,
      &quot;scope&quot;: &quot;outside_listed_properties&quot;
    }
  ],
  &quot;limitations&quot;: [
    &quot;diagnostic_0d29a666fd3a446e29e4&quot;,
    &quot;diagnostic_23efa867ad6a3e638305&quot;
  ]
}</pre></details>

No declared sensitive range reaches this sink in the supported relationships. This is not a non-sensitive or no-DOE certificate.

#### Sink limitations

<pre>[
  {
    &quot;id&quot;: &quot;diagnostic_0d29a666fd3a446e29e4&quot;,
    &quot;code&quot;: &quot;unbound_requirement&quot;,
    &quot;reason&quot;: &quot;No applicable demand goal is available; this does not mean the requirement can be omitted.&quot;,
    &quot;instruction_id&quot;: null,
    &quot;operation_id&quot;: null,
    &quot;blocking&quot;: true
  },
  {
    &quot;id&quot;: &quot;diagnostic_23efa867ad6a3e638305&quot;,
    &quot;code&quot;: &quot;requirement_expression_gap&quot;,
    &quot;reason&quot;: &quot;This requirement is not fully expressed as positive demands and supported constraints. No program-verifiable local impact boundary is available; retain it as a global limitation.&quot;,
    &quot;instruction_id&quot;: null,
    &quot;operation_id&quot;: null,
    &quot;blocking&quot;: true
  }
]</pre>

<a id="sink-24bbf7ef75e8a7d9b932"></a>

### sink\_ce54588f3e0fbdcec0e6

<details><summary>Boundary and actual payload</summary><pre>{
  &quot;boundary&quot;: {
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;event_index&quot;: 2,
    &quot;op_index&quot;: 0,
    &quot;body_event_index&quot;: null,
    &quot;scope&quot;: null,
    &quot;target&quot;: &quot;__compiled_model_context__&quot;,
    &quot;sink_type&quot;: &quot;model_observe&quot;,
    &quot;exposure_level&quot;: 2
  },
  &quot;actual_payload&quot;: [
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
          &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
        ]
      ]
    }
  ]
}</pre></details>

#### Demand-driving requirements

- **R5:** When limit is present in the request, pass its value unchanged as the limit argument\.

- **R8:** After the search, write the response's total value to local count\.txt\.

- **R9:** Return the search response's items value unchanged\.

<details><summary>Full boundary-specific preservation demand</summary><p>Unestablished demand is not a deletion certificate; all conservative retention and relevant limitations constrain a reduction.</p><pre>{
  &quot;demanded_information&quot;: [
    &quot;demand_2265116b7cfa70e7b4fd&quot;,
    &quot;demand_8cec444e21f59eae5821&quot;
  ],
  &quot;conservative_retention&quot;: [
    &quot;demand_011b75f91d326ee990db&quot;,
    &quot;demand_9ce5af8a561b9c24b4a4&quot;,
    &quot;demand_c58a57d27f2007c8e1e6&quot;,
    &quot;demand_de974e2b6cdb2ec6815d&quot;
  ],
  &quot;unestablished_ranges&quot;: [],
  &quot;limitations&quot;: [
    &quot;diagnostic_0d29a666fd3a446e29e4&quot;,
    &quot;diagnostic_23efa867ad6a3e638305&quot;
  ]
}</pre></details>

No declared sensitive range reaches this sink in the supported relationships. This is not a non-sensitive or no-DOE certificate.

#### Sink limitations

<pre>[
  {
    &quot;id&quot;: &quot;diagnostic_0d29a666fd3a446e29e4&quot;,
    &quot;code&quot;: &quot;unbound_requirement&quot;,
    &quot;reason&quot;: &quot;No applicable demand goal is available; this does not mean the requirement can be omitted.&quot;,
    &quot;instruction_id&quot;: null,
    &quot;operation_id&quot;: null,
    &quot;blocking&quot;: true
  },
  {
    &quot;id&quot;: &quot;diagnostic_23efa867ad6a3e638305&quot;,
    &quot;code&quot;: &quot;requirement_expression_gap&quot;,
    &quot;reason&quot;: &quot;This requirement is not fully expressed as positive demands and supported constraints. No program-verifiable local impact boundary is available; retain it as a global limitation.&quot;,
    &quot;instruction_id&quot;: null,
    &quot;operation_id&quot;: null,
    &quot;blocking&quot;: true
  }
]</pre>

<a id="sink-10e9215b4dfcde073ab6"></a>

### sink\_d73d96f2b39e63cdaaad

<details><summary>Boundary and actual payload</summary><pre>{
  &quot;boundary&quot;: {
    &quot;instruction_id&quot;: &quot;ir_010&quot;,
    &quot;event_index&quot;: 0,
    &quot;op_index&quot;: 0,
    &quot;body_event_index&quot;: null,
    &quot;scope&quot;: null,
    &quot;target&quot;: &quot;count_file&quot;,
    &quot;sink_type&quot;: &quot;storage_write&quot;,
    &quot;exposure_level&quot;: 1
  },
  &quot;actual_payload&quot;: [
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
          &quot;data_009b07c5001af2da1d8acba3076888f2a7aa49ea2d80afafcc10b34e1bd1a4bd&quot;,
          &quot;data_048f3f047d3cfd508d82af1052f822b8a36daad60f870bd2320e27d348514221&quot;,
          &quot;data_bd1ba59ec1f944c468c881a67676f62b0095ddc2e9217a2e133cf178abcb2ec9&quot;,
          &quot;data_dc7b982531c6520469643cfd7a66716bad24aaa6ba24f305c1d6b60f15a4af79&quot;
        ]
      ]
    }
  ]
}</pre></details>

#### Demand-driving requirements

- **R8:** After the search, write the response's total value to local count\.txt\.

<details><summary>Full boundary-specific preservation demand</summary><p>Unestablished demand is not a deletion certificate; all conservative retention and relevant limitations constrain a reduction.</p><pre>{
  &quot;demanded_information&quot;: [
    &quot;demand_1630af8d3d8cd57edf6e&quot;,
    &quot;demand_64278c426083d32e40eb&quot;
  ],
  &quot;conservative_retention&quot;: [],
  &quot;unestablished_ranges&quot;: [],
  &quot;limitations&quot;: [
    &quot;diagnostic_0d29a666fd3a446e29e4&quot;,
    &quot;diagnostic_23efa867ad6a3e638305&quot;
  ]
}</pre></details>

No declared sensitive range reaches this sink in the supported relationships. This is not a non-sensitive or no-DOE certificate.

#### Sink limitations

<pre>[
  {
    &quot;id&quot;: &quot;diagnostic_0d29a666fd3a446e29e4&quot;,
    &quot;code&quot;: &quot;unbound_requirement&quot;,
    &quot;reason&quot;: &quot;No applicable demand goal is available; this does not mean the requirement can be omitted.&quot;,
    &quot;instruction_id&quot;: null,
    &quot;operation_id&quot;: null,
    &quot;blocking&quot;: true
  },
  {
    &quot;id&quot;: &quot;diagnostic_23efa867ad6a3e638305&quot;,
    &quot;code&quot;: &quot;requirement_expression_gap&quot;,
    &quot;reason&quot;: &quot;This requirement is not fully expressed as positive demands and supported constraints. No program-verifiable local impact boundary is available; retain it as a global limitation.&quot;,
    &quot;instruction_id&quot;: null,
    &quot;operation_id&quot;: null,
    &quot;blocking&quot;: true
  }
]</pre>

<a id="sink-c6372774cf98e8e7681e"></a>

### sink\_f5e30d631911b0c8db08

<details><summary>Boundary and actual payload</summary><pre>{
  &quot;boundary&quot;: {
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;event_index&quot;: 4,
    &quot;op_index&quot;: 0,
    &quot;body_event_index&quot;: null,
    &quot;scope&quot;: null,
    &quot;target&quot;: &quot;index_search&quot;,
    &quot;sink_type&quot;: &quot;external_tool&quot;,
    &quot;exposure_level&quot;: 2
  },
  &quot;actual_payload&quot;: [
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
          &quot;data_0a2883229a9be18ff5d5eb083414c0b4e16345aa9fa51e195e00917d906fe248&quot;,
          &quot;data_6eb33a1fba325169baaeb5a263cfb1ca3f88b1ca955288acf76ebbf3d574204a&quot;,
          &quot;data_d0564fb629786752de47645d70df9e2654757eed8e265baafae2fdc61d57ca77&quot;,
          &quot;data_fd34f589b9e429b928ab67c129121af92307b50527970b5a8546d4982c76e0ce&quot;
        ]
      ]
    }
  ]
}</pre></details>

#### Demand-driving requirements

- **R2:** Call index\.search exactly once, using request\.term unchanged as its query argument\.

- **R3:** When from\_date is present in the request, pass its value unchanged as the from\_date argument; the accepted format is YYYY\-MM\-DD\.

- **R5:** When limit is present in the request, pass its value unchanged as the limit argument\.

- **R8:** After the search, write the response's total value to local count\.txt\.

- **R9:** Return the search response's items value unchanged\.

<details><summary>Full boundary-specific preservation demand</summary><p>Unestablished demand is not a deletion certificate; all conservative retention and relevant limitations constrain a reduction.</p><pre>{
  &quot;demanded_information&quot;: [
    &quot;demand_590b42ebda7587a7fd51&quot;,
    &quot;demand_7d75a0a4c56874385a11&quot;,
    &quot;demand_b8c556f810395df679cc&quot;,
    &quot;demand_baf6040bb485b47d9e9a&quot;,
    &quot;demand_d33e6a25921fbd47190c&quot;,
    &quot;demand_d6f1b29ca884fc09ba2f&quot;
  ],
  &quot;conservative_retention&quot;: [
    &quot;demand_7eb0b5fdd5480d183860&quot;,
    &quot;demand_e040a0805294f39b8a2b&quot;
  ],
  &quot;unestablished_ranges&quot;: [],
  &quot;limitations&quot;: [
    &quot;diagnostic_0d29a666fd3a446e29e4&quot;,
    &quot;diagnostic_23efa867ad6a3e638305&quot;
  ]
}</pre></details>

No declared sensitive range reaches this sink in the supported relationships. This is not a non-sensitive or no-DOE certificate.

#### Sink limitations

<pre>[
  {
    &quot;id&quot;: &quot;diagnostic_0d29a666fd3a446e29e4&quot;,
    &quot;code&quot;: &quot;unbound_requirement&quot;,
    &quot;reason&quot;: &quot;No applicable demand goal is available; this does not mean the requirement can be omitted.&quot;,
    &quot;instruction_id&quot;: null,
    &quot;operation_id&quot;: null,
    &quot;blocking&quot;: true
  },
  {
    &quot;id&quot;: &quot;diagnostic_23efa867ad6a3e638305&quot;,
    &quot;code&quot;: &quot;requirement_expression_gap&quot;,
    &quot;reason&quot;: &quot;This requirement is not fully expressed as positive demands and supported constraints. No program-verifiable local impact boundary is available; retain it as a global limitation.&quot;,
    &quot;instruction_id&quot;: null,
    &quot;operation_id&quot;: null,
    &quot;blocking&quot;: true
  }
]</pre>

## Shared declarations and source evidence

Evidence locates the claim; a real excerpt does not prove the sensitivity interpretation.

No explicit sensitivity declarations. Unknown source remainder is retained in facts, but is not assigned invented sensitive fields or labels.

## Shared derivations

<a id="demand-65bab95b32d508b85685"></a>

### demand · demand\_011b75f91d326ee990db

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e2:a0&quot;,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;conditional_observation&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_c58a57d27f2007c8e1e6&quot;
  ]
}</pre>

<a id="demand-c68c98c22cf00b628d75"></a>

### demand · demand\_01b3b70894daf5f7ee4a

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_bd3300adbbbdd1805a29&quot;
  ]
}</pre>

<a id="demand-61582d607ebdf8346002"></a>

### demand · demand\_027879ee0798a76e382e

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_66673f4cc0a1000c3364&quot;,
    &quot;demand_dede86295c1db9f772b2&quot;
  ]
}</pre>

<a id="demand-420dc860b45d16db28dc"></a>

### demand · demand\_03981620e2e6f3f13b08

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_5e7715447833486ec098&quot;
  ]
}</pre>

<a id="demand-34cff007780d5debd106"></a>

### demand · demand\_040c46ea630a77b3f3a9

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R3&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_c25263b0b7055126cef1&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_42fbb489f1bd4560a46f&quot;
  ]
}</pre>

<a id="demand-1c9cf3402511d2106361"></a>

### demand · demand\_060d059caea61b0856a0

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e1:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;expression_reference&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_61409dc5b007f9f16793&quot;
  ]
}</pre>

<a id="demand-2a27fd85fa309bcfaeaa"></a>

### demand · demand\_0ef30ddf1912010b5241

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R5&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_99915fbe3f62e1af0426&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_e988c039d89c1763ac21&quot;
  ]
}</pre>

<a id="demand-6a0c71fac0db9d4c8dc0"></a>

### demand · demand\_0f342157a8515367497a

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e0:a0&quot;,
    &quot;slot&quot;: 2,
    &quot;data_ids&quot;: [
      &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R5&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_99915fbe3f62e1af0426&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_f39fdd98d6d3cb57415c&quot;
  ]
}</pre>

<a id="demand-7f2b6ea8af6d2f219ac4"></a>

### demand · demand\_0f95adba03c8b5c7d0df

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e1:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;expression_reference&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_91fc1268f9aa69097200&quot;
  ]
}</pre>

<a id="demand-86a902459720da799d04"></a>

### demand · demand\_0fb904054ffe8db7cff2

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_7f7f0145ff463e904092&quot;
  ]
}</pre>

<a id="demand-398a424e05bb3ce4b66b"></a>

### demand · demand\_10bd0a708d3f8dc5425f

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e1:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R5&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_99915fbe3f62e1af0426&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;expression_reference&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_8c1a0244385b7a40c8d7&quot;
  ]
}</pre>

<a id="demand-fc5c1878737facbda425"></a>

### demand · demand\_11c1292b507a99d484a9

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e0:a0&quot;,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R3&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_c25263b0b7055126cef1&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_a8c4d482172c4e5b600b&quot;
  ]
}</pre>

<a id="demand-f9ec7ab88690622e75d1"></a>

### demand · demand\_124ab7fabe6068059b38

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R4&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_852714501b1884f87090&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_bd9a60659f9187892e00&quot;
  ]
}</pre>

<a id="demand-fc5de4fab17c22c49011"></a>

### demand · demand\_1267e5b11b3f8394cebb

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_3e6cde98406f7453901b&quot;,
    &quot;demand_fcf417f85ceb391d20a2&quot;
  ]
}</pre>

<a id="demand-e0f50af88983d2a1b997"></a>

### demand · demand\_12a7bcc23754ebcae14b

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_d9e2820869128653c624&quot;,
    &quot;demand_ffb8870545afc91e7312&quot;
  ]
}</pre>

<a id="demand-4ea6ddf784a460d66dd1"></a>

### demand · demand\_148d47ecfc12a07d92c2

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_6be9b2f5b849c10264a6&quot;
  ]
}</pre>

<a id="demand-2734f5ee88712392cb98"></a>

### demand · demand\_1527693ead3389526798

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e5:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
      &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
      &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
      &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;total&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_fbddddbc2453964e4624&quot;
  ]
}</pre>

<a id="demand-b572c9b8b6081031221b"></a>

### demand · demand\_15e672d7fd8cfc39f9d5

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_92f978725a6f48f73a92&quot;
  ]
}</pre>

<a id="demand-715e92a6b4e951be8b5f"></a>

### demand · demand\_1630af8d3d8cd57edf6e

<pre>{
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
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_a68e938e61f1884d7598&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;task_action&quot;
  ],
  &quot;parents&quot;: []
}</pre>

<a id="demand-4baf0b5dbfcb21d100c3"></a>

### demand · demand\_17152c60a6ae1d21b8de

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e1:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;expression_reference&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_375081c2e3bbc0ee0d77&quot;
  ]
}</pre>

<a id="demand-78555686a92e3e3c781c"></a>

### demand · demand\_19163dc921148efcdf63

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_3f72c371567eb238315b&quot;,
    &quot;demand_fb0fb70eb3d7b7b5b6a8&quot;
  ]
}</pre>

<a id="demand-82f2c7ded990d09914f7"></a>

### demand · demand\_19841bb9b807fdf32007

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_eb8c53fc958b1eeaeb7f&quot;
  ]
}</pre>

<a id="demand-777a8fc6fa938961eae9"></a>

### demand · demand\_1ce9c7d3a9f371fab647

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_c247c6618cffff5b721e&quot;
  ]
}</pre>

<a id="demand-e7aa1fe431c6cbccf751"></a>

### demand · demand\_1cf2bd3a1b6cefaeebf0

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R2&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9704dcab72933209f08&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_5a2713c90c7e1f1c406d&quot;
  ]
}</pre>

<a id="demand-184d145382741a263fa4"></a>

### demand · demand\_2011f2f9df4b0a803756

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R2&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9704dcab72933209f08&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_24a23be128f53091c993&quot;,
    &quot;demand_7af4ef8e87c64e9c7ff1&quot;
  ]
}</pre>

<a id="demand-5cea8768bf860838436c"></a>

### demand · demand\_210e7a5f9f813242d2a2

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;member_presence&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_8c7c2e131b5181c9f257&quot;
  ]
}</pre>

<a id="demand-127706e66ccf749040e5"></a>

### demand · demand\_21fc99a5f39f0a12bb33

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R3&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_c25263b0b7055126cef1&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_e5b4ea3e00aaa215f221&quot;
  ]
}</pre>

<a id="demand-54731e229119122a7c62"></a>

### demand · demand\_226185ce3ae84e4a5551

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;constructed_member&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_8c7c2e131b5181c9f257&quot;
  ]
}</pre>

<a id="demand-c9d3a08f96bf18c3293e"></a>

### demand · demand\_2265116b7cfa70e7b4fd

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e2:a0&quot;,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R5&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_99915fbe3f62e1af0426&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;conditional_observation&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_8cec444e21f59eae5821&quot;
  ]
}</pre>

<a id="demand-e7137a5d1c53705106f0"></a>

### demand · demand\_2309bafb3909dcb19085

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_72b9b88f0ac48b29155e&quot;
  ]
}</pre>

<a id="demand-7be946ad6fe639e6ed8f"></a>

### demand · demand\_24a23be128f53091c993

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R2&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9704dcab72933209f08&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_2011f2f9df4b0a803756&quot;
  ]
}</pre>

<a id="demand-de01eb32d73bdb756158"></a>

### demand · demand\_26557e406502932fbfec

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_8b2b878cce0eaf2a51fe&quot;,
    &quot;demand_d3d6b54aead7cea69e58&quot;
  ]
}</pre>

<a id="demand-a563375c26dda20f78e3"></a>

### demand · demand\_28e08f4f663b7011f1d7

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R2&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9704dcab72933209f08&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;selected_path&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_ef7bc36a49ee5facb86d&quot;
  ]
}</pre>

<a id="demand-66192653ac1e1f012a61"></a>

### demand · demand\_2a5b1271ff711c27cab6

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 5,
    &quot;data_ids&quot;: [
      &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R6&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_da9ae22c3399787be23d&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_bf1cab20b360f6dd5dd1&quot;,
    &quot;demand_ef44a9bba39f75fb78a5&quot;
  ]
}</pre>

<a id="demand-97d49273d439e3638c43"></a>

### demand · demand\_2abfedbf464a993f7ea4

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_009&quot;,
    &quot;operation_id&quot;: &quot;op_ir_009:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_009b07c5001af2da1d8acba3076888f2a7aa49ea2d80afafcc10b34e1bd1a4bd&quot;,
      &quot;data_048f3f047d3cfd508d82af1052f822b8a36daad60f870bd2320e27d348514221&quot;,
      &quot;data_bd1ba59ec1f944c468c881a67676f62b0095ddc2e9217a2e133cf178abcb2ec9&quot;,
      &quot;data_dc7b982531c6520469643cfd7a66716bad24aaa6ba24f305c1d6b60f15a4af79&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_319add76d3ac8f50fbe0&quot;
  ]
}</pre>

<a id="demand-ad1e7cfeb8d71220642f"></a>

### demand · demand\_2ec2c86f2aec01f55f79

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;selected_path&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_b4acd6d8777d40b09cb6&quot;
  ]
}</pre>

<a id="demand-956ed74b9422c444d8dd"></a>

### demand · demand\_2f3a701de8654081301e

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_26557e406502932fbfec&quot;
  ]
}</pre>

<a id="demand-a4a7edd707919cd1f051"></a>

### demand · demand\_2f867e60ea7f9050757c

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_011&quot;,
    &quot;operation_id&quot;: &quot;op_ir_011:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
      &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
      &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
      &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;items&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;selected_path&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_fdb88a29a419e92159ef&quot;
  ]
}</pre>

<a id="demand-2a793639052b0a713c7a"></a>

### demand · demand\_319add76d3ac8f50fbe0

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_009&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_009b07c5001af2da1d8acba3076888f2a7aa49ea2d80afafcc10b34e1bd1a4bd&quot;,
      &quot;data_048f3f047d3cfd508d82af1052f822b8a36daad60f870bd2320e27d348514221&quot;,
      &quot;data_bd1ba59ec1f944c468c881a67676f62b0095ddc2e9217a2e133cf178abcb2ec9&quot;,
      &quot;data_dc7b982531c6520469643cfd7a66716bad24aaa6ba24f305c1d6b60f15a4af79&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_7ffb8ab6e5d4601295c9&quot;
  ]
}</pre>

<a id="demand-38fe52ce1ec9b5419665"></a>

### demand · demand\_337fb1297ba54ad5da66

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R4&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_852714501b1884f87090&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;member_presence&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_85e7a4931aa93fb6b1e6&quot;
  ]
}</pre>

<a id="demand-8ce1e1fdd85503fa7cfc"></a>

### demand · demand\_347ce93969decf74ea86

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_0a2883229a9be18ff5d5eb083414c0b4e16345aa9fa51e195e00917d906fe248&quot;,
      &quot;data_6eb33a1fba325169baaeb5a263cfb1ca3f88b1ca955288acf76ebbf3d574204a&quot;,
      &quot;data_d0564fb629786752de47645d70df9e2654757eed8e265baafae2fdc61d57ca77&quot;,
      &quot;data_fd34f589b9e429b928ab67c129121af92307b50527970b5a8546d4982c76e0ce&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_7eb0b5fdd5480d183860&quot;,
    &quot;demand_8d2a0ae336cd56890d75&quot;
  ]
}</pre>

<a id="demand-4e14bae707b532164015"></a>

### demand · demand\_3519cd325fa94f564a75

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R3&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_c25263b0b7055126cef1&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_a9cb292e347f99bd49e2&quot;,
    &quot;demand_cdb9b6806ba2be68aa2a&quot;
  ]
}</pre>

<a id="demand-c58d3febe5b26df2c834"></a>

### demand · demand\_37154e374f14a5f3224e

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R2&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9704dcab72933209f08&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;required_original_value&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_1cf2bd3a1b6cefaeebf0&quot;,
    &quot;demand_5a2713c90c7e1f1c406d&quot;
  ]
}</pre>

<a id="demand-197ae1562e89c55b804f"></a>

### demand · demand\_375081c2e3bbc0ee0d77

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e1:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_61b23ba86b050f08f580&quot;
  ]
}</pre>

<a id="demand-05be178a7bbf369eeac3"></a>

### demand · demand\_38008f50db63e3e59448

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e1:a0&quot;,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;conditional_observation&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_01b3b70894daf5f7ee4a&quot;
  ]
}</pre>

<a id="demand-5d9ab84080f8c37875a5"></a>

### demand · demand\_3ceb0f49c62a078f8a55

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_b39c68a83b1ada0552a5&quot;
  ]
}</pre>

<a id="demand-47f883846b7df0e961ad"></a>

### demand · demand\_3d08c880775f9f9ac1e7

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_009&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
      &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
      &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
      &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;total&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_3fdb35f17666f0d05802&quot;,
    &quot;demand_e480ec35cc1b8733e075&quot;
  ]
}</pre>

<a id="demand-01a579eb5154bd73159f"></a>

### demand · demand\_3d3d7ae1418b74d696f7

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R4&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_852714501b1884f87090&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_41850aec0160ef422854&quot;
  ]
}</pre>

<a id="demand-84bef79a5a0e89247fbc"></a>

### demand · demand\_3e6cde98406f7453901b

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_fcf417f85ceb391d20a2&quot;
  ]
}</pre>

<a id="demand-7f5f0afeb54a4d7e5533"></a>

### demand · demand\_3f2f1eee3c0f48917732

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e5:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
      &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
      &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
      &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;items&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_d52b25361812e6b5276e&quot;
  ]
}</pre>

<a id="demand-5b68ef6e506bb8501960"></a>

### demand · demand\_3f72c371567eb238315b

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;constructed_member&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_347ce93969decf74ea86&quot;
  ]
}</pre>

<a id="demand-93744d2dd6a26d648b31"></a>

### demand · demand\_3fdb35f17666f0d05802

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_009&quot;,
    &quot;operation_id&quot;: &quot;op_ir_009:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
      &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
      &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
      &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;total&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_e480ec35cc1b8733e075&quot;
  ]
}</pre>

<a id="demand-82952ccd1e495dce5f8a"></a>

### demand · demand\_41850aec0160ef422854

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 3,
    &quot;data_ids&quot;: [
      &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R4&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_852714501b1884f87090&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_337fb1297ba54ad5da66&quot;,
    &quot;demand_4cb095dcbfa2c33d77ee&quot;
  ]
}</pre>

<a id="demand-14f9717b9360d9dfcd7b"></a>

### demand · demand\_42fbb489f1bd4560a46f

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R3&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_c25263b0b7055126cef1&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;selected_path&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_5d35b238051495dcce71&quot;
  ]
}</pre>

<a id="demand-24a15c530cf1e163ce2b"></a>

### demand · demand\_4531a752719eb527730a

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e0:a0&quot;,
    &quot;slot&quot;: 2,
    &quot;data_ids&quot;: [
      &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_a7619d995eea12ea7ec0&quot;
  ]
}</pre>

<a id="demand-3881eea6e0b40d166129"></a>

### demand · demand\_477b6ab435de27de43c7

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 2,
    &quot;data_ids&quot;: [
      &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_01b3b70894daf5f7ee4a&quot;,
    &quot;demand_bd3300adbbbdd1805a29&quot;
  ]
}</pre>

<a id="demand-9d2f93e9a051f054879b"></a>

### demand · demand\_4a3a715927c9f2ef6981

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R3&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_c25263b0b7055126cef1&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_762481587d1dd195647d&quot;
  ]
}</pre>

<a id="demand-03f864c8bc8b67355598"></a>

### demand · demand\_4cb095dcbfa2c33d77ee

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e0:a0&quot;,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R4&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_852714501b1884f87090&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_337fb1297ba54ad5da66&quot;
  ]
}</pre>

<a id="demand-3fcc5bd58fb8931ecc6b"></a>

### demand · demand\_4dffd6199cd64056c3ae

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_d75f7c02084be857e77c&quot;
  ]
}</pre>

<a id="demand-ee4a0b7d130f70a19ee2"></a>

### demand · demand\_4e840f919403be10342a

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R6&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_da9ae22c3399787be23d&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_2a5b1271ff711c27cab6&quot;
  ]
}</pre>

<a id="demand-e0b91c19f77858a3c1da"></a>

### demand · demand\_4f0d6479a3f258902fd9

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R6&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_da9ae22c3399787be23d&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_99ce68074d56ea71cb5e&quot;,
    &quot;demand_ad7a3c380dd29a60d6eb&quot;
  ]
}</pre>

<a id="demand-ea38fbb3526dc29e9a66"></a>

### demand · demand\_516ebbbcda4dd4401481

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R5&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_99915fbe3f62e1af0426&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_fb3898ec36137409560d&quot;
  ]
}</pre>

<a id="demand-3ab564e313e1c28db4dd"></a>

### demand · demand\_590b42ebda7587a7fd51

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e4:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_0a2883229a9be18ff5d5eb083414c0b4e16345aa9fa51e195e00917d906fe248&quot;,
      &quot;data_6eb33a1fba325169baaeb5a263cfb1ca3f88b1ca955288acf76ebbf3d574204a&quot;,
      &quot;data_d0564fb629786752de47645d70df9e2654757eed8e265baafae2fdc61d57ca77&quot;,
      &quot;data_fd34f589b9e429b928ab67c129121af92307b50527970b5a8546d4982c76e0ce&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R3&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_c25263b0b7055126cef1&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;task_expected_relation&quot;
  ],
  &quot;parents&quot;: []
}</pre>

<a id="demand-a2189a4598144dc49eb1"></a>

### demand · demand\_5a2713c90c7e1f1c406d

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R2&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9704dcab72933209f08&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;constructed_member&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_c7277a7ef37dfc348362&quot;
  ]
}</pre>

<a id="demand-9584c38534b8fa613912"></a>

### demand · demand\_5d35b238051495dcce71

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R3&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_c25263b0b7055126cef1&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_90a8c8faaa43e558ed32&quot;
  ]
}</pre>

<a id="demand-9995fd4b8a92d5a421db"></a>

### demand · demand\_5d5dea924b3d86941903

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 4,
    &quot;data_ids&quot;: [
      &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;constructed_member&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_8c7c2e131b5181c9f257&quot;
  ]
}</pre>

<a id="demand-8facf33549155ed96dc7"></a>

### demand · demand\_5d9944aca9d0f5b3af9e

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R2&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9704dcab72933209f08&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_28e08f4f663b7011f1d7&quot;
  ]
}</pre>

<a id="demand-965027f7b6ddf7991e0e"></a>

### demand · demand\_5e7715447833486ec098

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 3,
    &quot;data_ids&quot;: [
      &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_a121999a238e2b343db5&quot;,
    &quot;demand_fa0d743285ad8d862d11&quot;,
    &quot;demand_fb2050d056b0101a52c6&quot;
  ]
}</pre>

<a id="demand-f256f6beba8fc713de8f"></a>

### demand · demand\_5ef46ac2ca6212387e6e

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e1:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R6&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_da9ae22c3399787be23d&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_4e840f919403be10342a&quot;
  ]
}</pre>

<a id="demand-705f790a1dc40988e372"></a>

### demand · demand\_60fe8bfc7dbac9467679

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_ef34de16517bcc0ba0dc&quot;
  ]
}</pre>

<a id="demand-5e07bc0e5f2cbbf72d6c"></a>

### demand · demand\_61409dc5b007f9f16793

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e1:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_ada22b605a53a043a5c3&quot;
  ]
}</pre>

<a id="demand-bee7a079ad2a220b2b2b"></a>

### demand · demand\_61b23ba86b050f08f580

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_6c0528f82772a7fe8746&quot;
  ]
}</pre>

<a id="demand-c52e925057e2ededd06f"></a>

### demand · demand\_64278c426083d32e40eb

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_010&quot;,
    &quot;operation_id&quot;: &quot;op_ir_010:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_009b07c5001af2da1d8acba3076888f2a7aa49ea2d80afafcc10b34e1bd1a4bd&quot;,
      &quot;data_048f3f047d3cfd508d82af1052f822b8a36daad60f870bd2320e27d348514221&quot;,
      &quot;data_bd1ba59ec1f944c468c881a67676f62b0095ddc2e9217a2e133cf178abcb2ec9&quot;,
      &quot;data_dc7b982531c6520469643cfd7a66716bad24aaa6ba24f305c1d6b60f15a4af79&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;task_expected_relation&quot;
  ],
  &quot;parents&quot;: []
}</pre>

<a id="demand-5a673a8a5dcc8de4b3a0"></a>

### demand · demand\_643508f65ade2ed6cb53

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R3&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_c25263b0b7055126cef1&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_8bac55342e62890a8849&quot;,
    &quot;demand_d382514978f76839919b&quot;
  ]
}</pre>

<a id="demand-8aa336aaddf9e8a408fd"></a>

### demand · demand\_664f3d164665ceccc236

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R5&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_99915fbe3f62e1af0426&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_8908050761768483aa42&quot;
  ]
}</pre>

<a id="demand-3225d59574ea84a72914"></a>

### demand · demand\_66673f4cc0a1000c3364

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_027879ee0798a76e382e&quot;
  ]
}</pre>

<a id="demand-831ef18154b7f034cc63"></a>

### demand · demand\_6805e845273c09774a25

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R3&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_c25263b0b7055126cef1&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_6c004b1a228348f6d572&quot;
  ]
}</pre>

<a id="demand-81a3d117777bc3edc7d9"></a>

### demand · demand\_6b0d0ba67ed22c85c0b5

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;selected_path&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_fcfb3c9f3b78737b0e31&quot;
  ]
}</pre>

<a id="demand-573998def05eb439bd08"></a>

### demand · demand\_6b68b76e3b74e7967bfa

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_d378b0df310d8e750810&quot;
  ]
}</pre>

<a id="demand-72b96d234a1d81cce6bf"></a>

### demand · demand\_6be9b2f5b849c10264a6

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;selected_path&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_cde82ff41056af9b1987&quot;
  ]
}</pre>

<a id="demand-5effa7fa78a528686019"></a>

### demand · demand\_6c004b1a228348f6d572

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R3&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_c25263b0b7055126cef1&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_040c46ea630a77b3f3a9&quot;,
    &quot;demand_42fbb489f1bd4560a46f&quot;
  ]
}</pre>

<a id="demand-38297a0f9ab6cb8e8099"></a>

### demand · demand\_6c0528f82772a7fe8746

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 3,
    &quot;data_ids&quot;: [
      &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_210e7a5f9f813242d2a2&quot;,
    &quot;demand_38008f50db63e3e59448&quot;,
    &quot;demand_7b570e9c2f7e78cca284&quot;
  ]
}</pre>

<a id="demand-44960e0ab8c6c81dc4f7"></a>

### demand · demand\_6d99652a86943741c3eb

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R4&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_852714501b1884f87090&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_90c2453cf4e8850e2f87&quot;,
    &quot;demand_a0b33a9eda68b1403808&quot;
  ]
}</pre>

<a id="demand-291e3904908118e07bf5"></a>

### demand · demand\_70b2fa7b5c54a135467d

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 2,
    &quot;data_ids&quot;: [
      &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;constructed_member&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_347ce93969decf74ea86&quot;
  ]
}</pre>

<a id="demand-aeb293d9571c783af20f"></a>

### demand · demand\_72b9b88f0ac48b29155e

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_2309bafb3909dcb19085&quot;,
    &quot;demand_3ceb0f49c62a078f8a55&quot;
  ]
}</pre>

<a id="demand-184e7b979d334d497043"></a>

### demand · demand\_73141ae109e6fb35cff1

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_2f3a701de8654081301e&quot;,
    &quot;demand_e89d369b316e5ed308f9&quot;
  ]
}</pre>

<a id="demand-fb440071aaef13df87c8"></a>

### demand · demand\_7493dde427fb4d2ef69a

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_bdf78099635501633b42&quot;
  ]
}</pre>

<a id="demand-98e5a24368c88171d48c"></a>

### demand · demand\_74e011a283e3c2a7c497

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_ecf094d1f91d32a49a29&quot;
  ]
}</pre>

<a id="demand-d5c66c0518134a4a2e40"></a>

### demand · demand\_750834fe82201bbad0cc

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_17152c60a6ae1d21b8de&quot;,
    &quot;demand_d81c094ea22be28c9a11&quot;
  ]
}</pre>

<a id="demand-f286161411781ece914d"></a>

### demand · demand\_762481587d1dd195647d

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 3,
    &quot;data_ids&quot;: [
      &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R3&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_c25263b0b7055126cef1&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_11c1292b507a99d484a9&quot;,
    &quot;demand_826a46cc7dab97aadc12&quot;,
    &quot;demand_a8c4d482172c4e5b600b&quot;
  ]
}</pre>

<a id="demand-3d84bc38ded876f9dcd1"></a>

### demand · demand\_7af4ef8e87c64e9c7ff1

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R2&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9704dcab72933209f08&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_e17da6f4e6d06628fbd1&quot;
  ]
}</pre>

<a id="demand-9891bdf7a3da66b51898"></a>

### demand · demand\_7b3a35330b12e8ba140b

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_1ce9c7d3a9f371fab647&quot;
  ]
}</pre>

<a id="demand-f5978fb26240906b5924"></a>

### demand · demand\_7b570e9c2f7e78cca284

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e0:a0&quot;,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_210e7a5f9f813242d2a2&quot;
  ]
}</pre>

<a id="demand-9c1ca2f0fbe3f5af1648"></a>

### demand · demand\_7d177a9a7565bddaea4f

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 3,
    &quot;data_ids&quot;: [
      &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;member_presence&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_8c7c2e131b5181c9f257&quot;
  ]
}</pre>

<a id="demand-a3d90e4ab813052ff39a"></a>

### demand · demand\_7d75a0a4c56874385a11

<pre>{
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
  &quot;requirement_id&quot;: &quot;R2&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_06ba52e6366aa3d27778&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;task_action&quot;
  ],
  &quot;parents&quot;: []
}</pre>

<a id="demand-b543fa20fa5ec61198cc"></a>

### demand · demand\_7e08c07d87242c733f11

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e1:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R6&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_da9ae22c3399787be23d&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;expression_reference&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_5ef46ac2ca6212387e6e&quot;
  ]
}</pre>

<a id="demand-3f4e1a54d65dc48266d2"></a>

### demand · demand\_7eb0b5fdd5480d183860

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e4:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_0a2883229a9be18ff5d5eb083414c0b4e16345aa9fa51e195e00917d906fe248&quot;,
      &quot;data_6eb33a1fba325169baaeb5a263cfb1ca3f88b1ca955288acf76ebbf3d574204a&quot;,
      &quot;data_d0564fb629786752de47645d70df9e2654757eed8e265baafae2fdc61d57ca77&quot;,
      &quot;data_fd34f589b9e429b928ab67c129121af92307b50527970b5a8546d4982c76e0ce&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;external_request_retained&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_fbddddbc2453964e4624&quot;
  ]
}</pre>

<a id="demand-4394e7bc8ab1de4adee1"></a>

### demand · demand\_7f7f0145ff463e904092

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_0fb904054ffe8db7cff2&quot;,
    &quot;demand_e26dc8f02b4659d06e86&quot;
  ]
}</pre>

<a id="demand-7153b0fdef2e5c6214e6"></a>

### demand · demand\_7ffb8ab6e5d4601295c9

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_010&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_009b07c5001af2da1d8acba3076888f2a7aa49ea2d80afafcc10b34e1bd1a4bd&quot;,
      &quot;data_048f3f047d3cfd508d82af1052f822b8a36daad60f870bd2320e27d348514221&quot;,
      &quot;data_bd1ba59ec1f944c468c881a67676f62b0095ddc2e9217a2e133cf178abcb2ec9&quot;,
      &quot;data_dc7b982531c6520469643cfd7a66716bad24aaa6ba24f305c1d6b60f15a4af79&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;required_original_value&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_64278c426083d32e40eb&quot;
  ]
}</pre>

<a id="demand-7f6711d6d451e4f559f1"></a>

### demand · demand\_80b80e5e32bb4975cf54

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R5&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_99915fbe3f62e1af0426&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_10bd0a708d3f8dc5425f&quot;,
    &quot;demand_ed053d38c1c3c958466c&quot;
  ]
}</pre>

<a id="demand-57e7899f7359ec2e5d43"></a>

### demand · demand\_818be2d98b4452eeedc4

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R5&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_99915fbe3f62e1af0426&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_d5f140ab698f1c07550f&quot;
  ]
}</pre>

<a id="demand-10ee7f679d4d9d606a22"></a>

### demand · demand\_826a46cc7dab97aadc12

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e1:a0&quot;,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R3&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_c25263b0b7055126cef1&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;conditional_observation&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_21fc99a5f39f0a12bb33&quot;
  ]
}</pre>

<a id="demand-395b1ae7d07a5e1a01b7"></a>

### demand · demand\_826c56400b72b19032dd

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R5&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_99915fbe3f62e1af0426&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;selected_path&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_fdaa28ea47863a88b661&quot;
  ]
}</pre>

<a id="demand-1fe7fc2698bc81d0fa86"></a>

### demand · demand\_82c47223cb8495272a52

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_2ec2c86f2aec01f55f79&quot;
  ]
}</pre>

<a id="demand-fd38f12556af8943aefd"></a>

### demand · demand\_84232f84eead295c9298

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_0a2883229a9be18ff5d5eb083414c0b4e16345aa9fa51e195e00917d906fe248&quot;,
      &quot;data_6eb33a1fba325169baaeb5a263cfb1ca3f88b1ca955288acf76ebbf3d574204a&quot;,
      &quot;data_d0564fb629786752de47645d70df9e2654757eed8e265baafae2fdc61d57ca77&quot;,
      &quot;data_fd34f589b9e429b928ab67c129121af92307b50527970b5a8546d4982c76e0ce&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R3&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_c25263b0b7055126cef1&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_590b42ebda7587a7fd51&quot;
  ]
}</pre>

<a id="demand-2f7e023e369d4c080287"></a>

### demand · demand\_84f9c21c73468e5a9f36

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 4,
    &quot;data_ids&quot;: [
      &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R5&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_99915fbe3f62e1af0426&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;constructed_member&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_a0f746440856254f3e55&quot;
  ]
}</pre>

<a id="demand-c671144e72bbd38a5b8d"></a>

### demand · demand\_85e7a4931aa93fb6b1e6

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_0a2883229a9be18ff5d5eb083414c0b4e16345aa9fa51e195e00917d906fe248&quot;,
      &quot;data_6eb33a1fba325169baaeb5a263cfb1ca3f88b1ca955288acf76ebbf3d574204a&quot;,
      &quot;data_d0564fb629786752de47645d70df9e2654757eed8e265baafae2fdc61d57ca77&quot;,
      &quot;data_fd34f589b9e429b928ab67c129121af92307b50527970b5a8546d4982c76e0ce&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R4&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_852714501b1884f87090&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;task_value&quot;
  ],
  &quot;parents&quot;: []
}</pre>

<a id="demand-ec9af6de8105637feeee"></a>

### demand · demand\_8619e9761ff560faf655

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 5,
    &quot;data_ids&quot;: [
      &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_011b75f91d326ee990db&quot;,
    &quot;demand_7d177a9a7565bddaea4f&quot;,
    &quot;demand_a250ebc33e7210d80f67&quot;
  ]
}</pre>

<a id="demand-a8501c52ae7072ce9ae4"></a>

### demand · demand\_8908050761768483aa42

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R5&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_99915fbe3f62e1af0426&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_826c56400b72b19032dd&quot;,
    &quot;demand_c517668c72349b7793ae&quot;
  ]
}</pre>

<a id="demand-b4356e0602182fb3803c"></a>

### demand · demand\_8b2b878cce0eaf2a51fe

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;selected_path&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_7b3a35330b12e8ba140b&quot;
  ]
}</pre>

<a id="demand-9d0aa609e3171998ad66"></a>

### demand · demand\_8bac55342e62890a8849

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R3&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_c25263b0b7055126cef1&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_d382514978f76839919b&quot;
  ]
}</pre>

<a id="demand-ae973043d96e7b49e1ed"></a>

### demand · demand\_8c1a0244385b7a40c8d7

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e1:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R5&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_99915fbe3f62e1af0426&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_0ef30ddf1912010b5241&quot;
  ]
}</pre>

<a id="demand-863ce019792ba5f3cbdc"></a>

### demand · demand\_8c7c2e131b5181c9f257

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_0a2883229a9be18ff5d5eb083414c0b4e16345aa9fa51e195e00917d906fe248&quot;,
      &quot;data_6eb33a1fba325169baaeb5a263cfb1ca3f88b1ca955288acf76ebbf3d574204a&quot;,
      &quot;data_d0564fb629786752de47645d70df9e2654757eed8e265baafae2fdc61d57ca77&quot;,
      &quot;data_fd34f589b9e429b928ab67c129121af92307b50527970b5a8546d4982c76e0ce&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_c1770df052c38c03b8d8&quot;,
    &quot;demand_e040a0805294f39b8a2b&quot;
  ]
}</pre>

<a id="demand-35506b357f2345562f4e"></a>

### demand · demand\_8cec444e21f59eae5821

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e2:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R5&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_99915fbe3f62e1af0426&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_84f9c21c73468e5a9f36&quot;
  ]
}</pre>

<a id="demand-5dbbffebb566067e09bf"></a>

### demand · demand\_8d2a0ae336cd56890d75

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e4:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_0a2883229a9be18ff5d5eb083414c0b4e16345aa9fa51e195e00917d906fe248&quot;,
      &quot;data_6eb33a1fba325169baaeb5a263cfb1ca3f88b1ca955288acf76ebbf3d574204a&quot;,
      &quot;data_d0564fb629786752de47645d70df9e2654757eed8e265baafae2fdc61d57ca77&quot;,
      &quot;data_fd34f589b9e429b928ab67c129121af92307b50527970b5a8546d4982c76e0ce&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;external_request_retained&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_fbddddbc2453964e4624&quot;
  ]
}</pre>

<a id="demand-780530b22f5ffce9991a"></a>

### demand · demand\_90a8c8faaa43e558ed32

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R3&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_c25263b0b7055126cef1&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_f0f265b2497e30deb0da&quot;
  ]
}</pre>

<a id="demand-986bb8576f3a11a0a8f8"></a>

### demand · demand\_90c2453cf4e8850e2f87

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R4&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_852714501b1884f87090&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_a0b33a9eda68b1403808&quot;
  ]
}</pre>

<a id="demand-fd33a5e1e35aff88d6e1"></a>

### demand · demand\_90cd1510cfe0663a2e57

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_a8f2037aae808da9a583&quot;
  ]
}</pre>

<a id="demand-dc976c86158046726ddf"></a>

### demand · demand\_91fc1268f9aa69097200

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e1:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_03981620e2e6f3f13b08&quot;
  ]
}</pre>

<a id="demand-9592b8a4ba16e0075773"></a>

### demand · demand\_92f978725a6f48f73a92

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_ac951b8bf04df1b81904&quot;,
    &quot;demand_fe314a23bc872fb4b635&quot;
  ]
}</pre>

<a id="demand-fe64cc186657aeba64b2"></a>

### demand · demand\_941c77f8f1ee40589119

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_011&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_41579c3d03f6f282e27032d6d90b1f0b803d643172579ecd01a36d619a4e97ab&quot;,
      &quot;data_65a79b1fbed9a71475acf516876593e476ab10fe2ad3c2ed599a5717e0edcfb7&quot;,
      &quot;data_a3fbf7f05105730eaa540813bac298a6a0f9e9e9c905244b323c4262bfa51eb7&quot;,
      &quot;data_ed5a774645da77bcd5c8de30cc27cf7137b52e0eb86af26412a0169bec42bcc8&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_d1131151dfb681ad1a1f&quot;
  ]
}</pre>

<a id="demand-6bd8aa7693a2ea14abe9"></a>

### demand · demand\_95fdaabbc06279c05636

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_d8e4a9da93b2e2d39b35&quot;
  ]
}</pre>

<a id="demand-df00aad209c73e269e38"></a>

### demand · demand\_987ba4c1faeea4293fbb

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_bfa79c9e2a33df5825eb&quot;
  ]
}</pre>

<a id="demand-9b018a5d1ad883dcc1fe"></a>

### demand · demand\_98dbcb2fddf9fb77a93e

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;action&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: null,
    &quot;data_ids&quot;: []
  },
  &quot;property&quot;: &quot;action&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R1&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_bad3975a1c33c86da8bc&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;task_action&quot;
  ],
  &quot;parents&quot;: []
}</pre>

<a id="demand-dd1a957219df254c5145"></a>

### demand · demand\_99ce68074d56ea71cb5e

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R6&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_da9ae22c3399787be23d&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_f9881e439c26f60c118b&quot;
  ]
}</pre>

<a id="demand-5422dd5b484079483d27"></a>

### demand · demand\_9a1e97e18f570f55846c

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_6b0d0ba67ed22c85c0b5&quot;
  ]
}</pre>

<a id="demand-174e6523d9521897554e"></a>

### demand · demand\_9b45307c579d6df84415

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_2ec2c86f2aec01f55f79&quot;,
    &quot;demand_82c47223cb8495272a52&quot;
  ]
}</pre>

<a id="demand-96ac03245dd84f62aac2"></a>

### demand · demand\_9bb97c53e9fd4ea8bcc4

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R2&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9704dcab72933209f08&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_37154e374f14a5f3224e&quot;
  ]
}</pre>

<a id="demand-f9c1992a6e62ac5cc548"></a>

### demand · demand\_9ce5af8a561b9c24b4a4

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e2:a0&quot;,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;conditional_observation&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_de974e2b6cdb2ec6815d&quot;
  ]
}</pre>

<a id="demand-ea265aa03d780ca2055d"></a>

### demand · demand\_a0200b367a9ee1cac92c

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_b21450a98657d0faa15e&quot;
  ]
}</pre>

<a id="demand-b4d9573f5ab48be695e4"></a>

### demand · demand\_a0b33a9eda68b1403808

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e1:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R4&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_852714501b1884f87090&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;expression_reference&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_c5bceddd5ea42bd4f55c&quot;
  ]
}</pre>

<a id="demand-ae5a3095ea0fea860b5f"></a>

### demand · demand\_a0f746440856254f3e55

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_0a2883229a9be18ff5d5eb083414c0b4e16345aa9fa51e195e00917d906fe248&quot;,
      &quot;data_6eb33a1fba325169baaeb5a263cfb1ca3f88b1ca955288acf76ebbf3d574204a&quot;,
      &quot;data_d0564fb629786752de47645d70df9e2654757eed8e265baafae2fdc61d57ca77&quot;,
      &quot;data_fd34f589b9e429b928ab67c129121af92307b50527970b5a8546d4982c76e0ce&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R5&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_99915fbe3f62e1af0426&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_d33e6a25921fbd47190c&quot;
  ]
}</pre>

<a id="demand-de40b7b58a2a5e26e237"></a>

### demand · demand\_a121999a238e2b343db5

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;member_presence&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_347ce93969decf74ea86&quot;
  ]
}</pre>

<a id="demand-0190e40515064014a172"></a>

### demand · demand\_a250ebc33e7210d80f67

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e0:a0&quot;,
    &quot;slot&quot;: 2,
    &quot;data_ids&quot;: [
      &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_7d177a9a7565bddaea4f&quot;
  ]
}</pre>

<a id="demand-e39f2d2b0e5e11dfdc13"></a>

### demand · demand\_a7619d995eea12ea7ec0

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 3,
    &quot;data_ids&quot;: [
      &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;member_presence&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_347ce93969decf74ea86&quot;
  ]
}</pre>

<a id="demand-7d4b99b6a1b3c4fa532c"></a>

### demand · demand\_a830ab582af19c9ae211

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_cc1e7ca6c02583fb1fa1&quot;
  ]
}</pre>

<a id="demand-572fe425a7923abc4807"></a>

### demand · demand\_a8c4d482172c4e5b600b

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R3&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_c25263b0b7055126cef1&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;member_presence&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_84232f84eead295c9298&quot;
  ]
}</pre>

<a id="demand-51c64af6cd3de4c2335b"></a>

### demand · demand\_a8f2037aae808da9a583

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_90cd1510cfe0663a2e57&quot;,
    &quot;demand_ad7929f80ff7dd7547bb&quot;
  ]
}</pre>

<a id="demand-6d2d24efb0e39b57bee9"></a>

### demand · demand\_a9cb292e347f99bd49e2

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R3&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_c25263b0b7055126cef1&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_643508f65ade2ed6cb53&quot;
  ]
}</pre>

<a id="demand-217e409cd4a3f9ef882a"></a>

### demand · demand\_aa3ec9d16d7ca210e3bc

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
      &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
      &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
      &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;items&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_dfed630e0a047cd37ba5&quot;
  ]
}</pre>

<a id="demand-0f7ccbbc33e44749160b"></a>

### demand · demand\_ac951b8bf04df1b81904

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e1:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;expression_reference&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_f54f30d8eb9442c92ff5&quot;
  ]
}</pre>

<a id="demand-1dfaffe262b65d1b59ed"></a>

### demand · demand\_ad7929f80ff7dd7547bb

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_750834fe82201bbad0cc&quot;
  ]
}</pre>

<a id="demand-3785dfd38d55ed70dfca"></a>

### demand · demand\_ad7a3c380dd29a60d6eb

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R6&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_da9ae22c3399787be23d&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_4f0d6479a3f258902fd9&quot;
  ]
}</pre>

<a id="demand-1797a790b20d49f9592f"></a>

### demand · demand\_ada22b605a53a043a5c3

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_8619e9761ff560faf655&quot;
  ]
}</pre>

<a id="demand-96aa5bdd45b548448c88"></a>

### demand · demand\_adb35267dcc6986504be

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_b93c9007bb675892fdef&quot;,
    &quot;demand_c296e5b640c7b725f18b&quot;
  ]
}</pre>

<a id="demand-756e94194a4cca463d8d"></a>

### demand · demand\_aea05ec71fbabb48bf35

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_011&quot;,
    &quot;operation_id&quot;: &quot;op_ir_011:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
      &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
      &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
      &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;items&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_2f867e60ea7f9050757c&quot;
  ]
}</pre>

<a id="demand-4def17d9e1901154bb9f"></a>

### demand · demand\_affde27b049c81080bfa

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_a0200b367a9ee1cac92c&quot;
  ]
}</pre>

<a id="demand-92f354b1c2e9c54e1613"></a>

### demand · demand\_b21450a98657d0faa15e

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_226185ce3ae84e4a5551&quot;,
    &quot;demand_f85c7bec526edab12a40&quot;
  ]
}</pre>

<a id="demand-e3636e60256c05956781"></a>

### demand · demand\_b35a9011f4975e024454

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_c2f9f7d0546d1d204694&quot;
  ]
}</pre>

<a id="demand-3bb1dfa603cfe04a999d"></a>

### demand · demand\_b39c68a83b1ada0552a5

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_0f95adba03c8b5c7d0df&quot;,
    &quot;demand_ebfc76d70055a0204f1b&quot;
  ]
}</pre>

<a id="demand-fc79b39a49c87d9ce19a"></a>

### demand · demand\_b4acd6d8777d40b09cb6

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_f0b30b8b6fb7dd22cd2a&quot;
  ]
}</pre>

<a id="demand-249a04b0be6065b3e74b"></a>

### demand · demand\_b8c556f810395df679cc

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e4:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_0a2883229a9be18ff5d5eb083414c0b4e16345aa9fa51e195e00917d906fe248&quot;,
      &quot;data_6eb33a1fba325169baaeb5a263cfb1ca3f88b1ca955288acf76ebbf3d574204a&quot;,
      &quot;data_d0564fb629786752de47645d70df9e2654757eed8e265baafae2fdc61d57ca77&quot;,
      &quot;data_fd34f589b9e429b928ab67c129121af92307b50527970b5a8546d4982c76e0ce&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;query&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R2&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9704dcab72933209f08&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;task_expected_relation&quot;
  ],
  &quot;parents&quot;: []
}</pre>

<a id="demand-ce85231b14e923ee5150"></a>

### demand · demand\_b93c9007bb675892fdef

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;selected_path&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_affde27b049c81080bfa&quot;
  ]
}</pre>

<a id="demand-7f9da6515adde0ca3e0e"></a>

### demand · demand\_baf6040bb485b47d9e9a

<pre>{
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
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;required_acquisition&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_fbddddbc2453964e4624&quot;
  ]
}</pre>

<a id="demand-32d9448c6520e3dae5ed"></a>

### demand · demand\_bd3300adbbbdd1805a29

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 2,
    &quot;data_ids&quot;: [
      &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;constructed_member&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_8c7c2e131b5181c9f257&quot;
  ]
}</pre>

<a id="demand-64a1458728f096402303"></a>

### demand · demand\_bd9a60659f9187892e00

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R4&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_852714501b1884f87090&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_124ab7fabe6068059b38&quot;,
    &quot;demand_dd861db390d4a4006f4d&quot;
  ]
}</pre>

<a id="demand-fb77494aa58c0b930c75"></a>

### demand · demand\_bde9043c98c874071f96

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R5&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_99915fbe3f62e1af0426&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_664f3d164665ceccc236&quot;,
    &quot;demand_c8563fb46c01ac50aa1a&quot;
  ]
}</pre>

<a id="demand-584b0914d28c4a8c001c"></a>

### demand · demand\_bdf78099635501633b42

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_7493dde427fb4d2ef69a&quot;,
    &quot;demand_95fdaabbc06279c05636&quot;
  ]
}</pre>

<a id="demand-f19118d5040427301fb9"></a>

### demand · demand\_bf1cab20b360f6dd5dd1

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e0:a0&quot;,
    &quot;slot&quot;: 2,
    &quot;data_ids&quot;: [
      &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R6&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_da9ae22c3399787be23d&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_ef44a9bba39f75fb78a5&quot;
  ]
}</pre>

<a id="demand-91830a848ebbb6dc1231"></a>

### demand · demand\_bf8055ea0bc0dea4bc17

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R3&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_c25263b0b7055126cef1&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_6805e845273c09774a25&quot;,
    &quot;demand_ee03d6918aa2bfde483d&quot;
  ]
}</pre>

<a id="demand-06ffe5eed7ea0033b2a8"></a>

### demand · demand\_bfa79c9e2a33df5825eb

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_15e672d7fd8cfc39f9d5&quot;,
    &quot;demand_987ba4c1faeea4293fbb&quot;
  ]
}</pre>

<a id="demand-1e483aff160a15b099df"></a>

### demand · demand\_c1770df052c38c03b8d8

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e4:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_0a2883229a9be18ff5d5eb083414c0b4e16345aa9fa51e195e00917d906fe248&quot;,
      &quot;data_6eb33a1fba325169baaeb5a263cfb1ca3f88b1ca955288acf76ebbf3d574204a&quot;,
      &quot;data_d0564fb629786752de47645d70df9e2654757eed8e265baafae2fdc61d57ca77&quot;,
      &quot;data_fd34f589b9e429b928ab67c129121af92307b50527970b5a8546d4982c76e0ce&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;external_request_retained&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_d52b25361812e6b5276e&quot;
  ]
}</pre>

<a id="demand-cb87b51b6ff510d464bc"></a>

### demand · demand\_c247c6618cffff5b721e

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 4,
    &quot;data_ids&quot;: [
      &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_5d5dea924b3d86941903&quot;,
    &quot;demand_c58a57d27f2007c8e1e6&quot;
  ]
}</pre>

<a id="demand-8b45c7e95c5e1fcfaba1"></a>

### demand · demand\_c296e5b640c7b725f18b

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_b93c9007bb675892fdef&quot;
  ]
}</pre>

<a id="demand-a74066fecbc3bf0d05dc"></a>

### demand · demand\_c2f9f7d0546d1d204694

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_6b0d0ba67ed22c85c0b5&quot;,
    &quot;demand_9a1e97e18f570f55846c&quot;
  ]
}</pre>

<a id="demand-274650c9d6132ef34f28"></a>

### demand · demand\_c4aaa01e135b1d3c60fc

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 4,
    &quot;data_ids&quot;: [
      &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;constructed_member&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_347ce93969decf74ea86&quot;
  ]
}</pre>

<a id="demand-4b9ef7c15caa7dcaa561"></a>

### demand · demand\_c517668c72349b7793ae

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R5&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_99915fbe3f62e1af0426&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_826c56400b72b19032dd&quot;
  ]
}</pre>

<a id="demand-0ea4968bf8e0349ae726"></a>

### demand · demand\_c58a57d27f2007c8e1e6

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e2:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_5d5dea924b3d86941903&quot;
  ]
}</pre>

<a id="demand-22d3cf99fe715b9a7dde"></a>

### demand · demand\_c5bceddd5ea42bd4f55c

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e1:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R4&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_852714501b1884f87090&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_3d3d7ae1418b74d696f7&quot;
  ]
}</pre>

<a id="demand-70f0edd1b7f157dc8432"></a>

### demand · demand\_c7277a7ef37dfc348362

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_0a2883229a9be18ff5d5eb083414c0b4e16345aa9fa51e195e00917d906fe248&quot;,
      &quot;data_6eb33a1fba325169baaeb5a263cfb1ca3f88b1ca955288acf76ebbf3d574204a&quot;,
      &quot;data_d0564fb629786752de47645d70df9e2654757eed8e265baafae2fdc61d57ca77&quot;,
      &quot;data_fd34f589b9e429b928ab67c129121af92307b50527970b5a8546d4982c76e0ce&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;query&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R2&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9704dcab72933209f08&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_b8c556f810395df679cc&quot;
  ]
}</pre>

<a id="demand-bc595d6c46da1b18f061"></a>

### demand · demand\_c73b1e4863ac33e110b4

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_0a2883229a9be18ff5d5eb083414c0b4e16345aa9fa51e195e00917d906fe248&quot;,
      &quot;data_6eb33a1fba325169baaeb5a263cfb1ca3f88b1ca955288acf76ebbf3d574204a&quot;,
      &quot;data_d0564fb629786752de47645d70df9e2654757eed8e265baafae2fdc61d57ca77&quot;,
      &quot;data_fd34f589b9e429b928ab67c129121af92307b50527970b5a8546d4982c76e0ce&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R6&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_da9ae22c3399787be23d&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;task_value&quot;
  ],
  &quot;parents&quot;: []
}</pre>

<a id="demand-a31b87840f1bf4552127"></a>

### demand · demand\_c8563fb46c01ac50aa1a

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R5&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_99915fbe3f62e1af0426&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_bde9043c98c874071f96&quot;
  ]
}</pre>

<a id="demand-faf1f4e86d63aa81fe71"></a>

### demand · demand\_cc1e7ca6c02583fb1fa1

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 5,
    &quot;data_ids&quot;: [
      &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_4531a752719eb527730a&quot;,
    &quot;demand_9ce5af8a561b9c24b4a4&quot;,
    &quot;demand_a7619d995eea12ea7ec0&quot;
  ]
}</pre>

<a id="demand-6150fc23a0492e040309"></a>

### demand · demand\_cdb9b6806ba2be68aa2a

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R3&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_c25263b0b7055126cef1&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_3519cd325fa94f564a75&quot;
  ]
}</pre>

<a id="demand-9078f5c49e264c60eef4"></a>

### demand · demand\_cde82ff41056af9b1987

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_19841bb9b807fdf32007&quot;
  ]
}</pre>

<a id="demand-6eba7c065208d27c1c9a"></a>

### demand · demand\_d1131151dfb681ad1a1f

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_012&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_41579c3d03f6f282e27032d6d90b1f0b803d643172579ecd01a36d619a4e97ab&quot;,
      &quot;data_65a79b1fbed9a71475acf516876593e476ab10fe2ad3c2ed599a5717e0edcfb7&quot;,
      &quot;data_a3fbf7f05105730eaa540813bac298a6a0f9e9e9c905244b323c4262bfa51eb7&quot;,
      &quot;data_ed5a774645da77bcd5c8de30cc27cf7137b52e0eb86af26412a0169bec42bcc8&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;task_operand&quot;
  ],
  &quot;parents&quot;: []
}</pre>

<a id="demand-902d5ffab968d1446d16"></a>

### demand · demand\_d33e6a25921fbd47190c

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e4:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_0a2883229a9be18ff5d5eb083414c0b4e16345aa9fa51e195e00917d906fe248&quot;,
      &quot;data_6eb33a1fba325169baaeb5a263cfb1ca3f88b1ca955288acf76ebbf3d574204a&quot;,
      &quot;data_d0564fb629786752de47645d70df9e2654757eed8e265baafae2fdc61d57ca77&quot;,
      &quot;data_fd34f589b9e429b928ab67c129121af92307b50527970b5a8546d4982c76e0ce&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R5&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_99915fbe3f62e1af0426&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;task_expected_relation&quot;
  ],
  &quot;parents&quot;: []
}</pre>

<a id="demand-96fe89f7f7727af8ef9a"></a>

### demand · demand\_d378b0df310d8e750810

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_6b68b76e3b74e7967bfa&quot;,
    &quot;demand_eaa1740ae1512b5396c9&quot;
  ]
}</pre>

<a id="demand-d2200c5eaaf82454d3e9"></a>

### demand · demand\_d382514978f76839919b

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e1:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R3&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_c25263b0b7055126cef1&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;expression_reference&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_e124af09ea1ff36bf62d&quot;
  ]
}</pre>

<a id="demand-0a60c51e883998e0aa66"></a>

### demand · demand\_d3d6b54aead7cea69e58

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_8b2b878cce0eaf2a51fe&quot;
  ]
}</pre>

<a id="demand-581896e8af98480293ef"></a>

### demand · demand\_d52b25361812e6b5276e

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e4:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
      &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
      &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
      &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;items&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_3f2f1eee3c0f48917732&quot;,
    &quot;demand_aa3ec9d16d7ca210e3bc&quot;
  ]
}</pre>

<a id="demand-6f9dc726be0033e88e2c"></a>

### demand · demand\_d5f140ab698f1c07550f

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R5&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_99915fbe3f62e1af0426&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_818be2d98b4452eeedc4&quot;,
    &quot;demand_f2bb42d64236e7f67d4a&quot;
  ]
}</pre>

<a id="demand-1b03504e57128b7141f3"></a>

### demand · demand\_d6f1b29ca884fc09ba2f

<pre>{
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
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;required_acquisition&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_d52b25361812e6b5276e&quot;
  ]
}</pre>

<a id="demand-eeaa4832e4aa5dc16e87"></a>

### demand · demand\_d75f7c02084be857e77c

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_4dffd6199cd64056c3ae&quot;,
    &quot;demand_b35a9011f4975e024454&quot;
  ]
}</pre>

<a id="demand-ee36f4dfcaec2443345c"></a>

### demand · demand\_d7ec078f0532d17ef79e

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R6&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_da9ae22c3399787be23d&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_7e08c07d87242c733f11&quot;
  ]
}</pre>

<a id="demand-ec5feaaae4b4368e0d3e"></a>

### demand · demand\_d81c094ea22be28c9a11

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_17152c60a6ae1d21b8de&quot;
  ]
}</pre>

<a id="demand-9221da252b7cbf8b4189"></a>

### demand · demand\_d8e4a9da93b2e2d39b35

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_060d059caea61b0856a0&quot;,
    &quot;demand_f23311e087bb37baeef9&quot;
  ]
}</pre>

<a id="demand-8bc93f78c60b95f39363"></a>

### demand · demand\_d9e2820869128653c624

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_12a7bcc23754ebcae14b&quot;
  ]
}</pre>

<a id="demand-9236ab204d31be5b2866"></a>

### demand · demand\_dd861db390d4a4006f4d

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R4&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_852714501b1884f87090&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_6d99652a86943741c3eb&quot;
  ]
}</pre>

<a id="demand-e923acbbf8e9e92a0454"></a>

### demand · demand\_de974e2b6cdb2ec6815d

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e2:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_c4aaa01e135b1d3c60fc&quot;
  ]
}</pre>

<a id="demand-440878b4b5e673566b6c"></a>

### demand · demand\_dede86295c1db9f772b2

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_1267e5b11b3f8394cebb&quot;
  ]
}</pre>

<a id="demand-832dbc67642fc7b09996"></a>

### demand · demand\_dfed630e0a047cd37ba5

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_011&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
      &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
      &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
      &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;items&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_2f867e60ea7f9050757c&quot;,
    &quot;demand_aea05ec71fbabb48bf35&quot;
  ]
}</pre>

<a id="demand-3eedc0ca29d40b701a68"></a>

### demand · demand\_e040a0805294f39b8a2b

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e4:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_0a2883229a9be18ff5d5eb083414c0b4e16345aa9fa51e195e00917d906fe248&quot;,
      &quot;data_6eb33a1fba325169baaeb5a263cfb1ca3f88b1ca955288acf76ebbf3d574204a&quot;,
      &quot;data_d0564fb629786752de47645d70df9e2654757eed8e265baafae2fdc61d57ca77&quot;,
      &quot;data_fd34f589b9e429b928ab67c129121af92307b50527970b5a8546d4982c76e0ce&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;external_request_retained&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_d52b25361812e6b5276e&quot;
  ]
}</pre>

<a id="demand-e63c076b1a6f5cd4c617"></a>

### demand · demand\_e124af09ea1ff36bf62d

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e1:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R3&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_c25263b0b7055126cef1&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_4a3a715927c9f2ef6981&quot;
  ]
}</pre>

<a id="demand-5e687a53ea63ff75a7a7"></a>

### demand · demand\_e17da6f4e6d06628fbd1

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R2&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9704dcab72933209f08&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_28e08f4f663b7011f1d7&quot;,
    &quot;demand_5d9944aca9d0f5b3af9e&quot;
  ]
}</pre>

<a id="demand-dfabad58078748ba0674"></a>

### demand · demand\_e26dc8f02b4659d06e86

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_e2b8a5b34dee8e4abd0e&quot;
  ]
}</pre>

<a id="demand-921b3bd633dafb311cb1"></a>

### demand · demand\_e2b8a5b34dee8e4abd0e

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_148d47ecfc12a07d92c2&quot;,
    &quot;demand_6be9b2f5b849c10264a6&quot;
  ]
}</pre>

<a id="demand-0f6dc2cc86679d5afd43"></a>

### demand · demand\_e480ec35cc1b8733e075

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_009&quot;,
    &quot;operation_id&quot;: &quot;op_ir_009:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
      &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
      &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
      &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;total&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;selected_path&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_2abfedbf464a993f7ea4&quot;
  ]
}</pre>

<a id="demand-adb886b6943340e6e8d2"></a>

### demand · demand\_e5b4ea3e00aaa215f221

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 2,
    &quot;data_ids&quot;: [
      &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R3&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_c25263b0b7055126cef1&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;constructed_member&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_84232f84eead295c9298&quot;
  ]
}</pre>

<a id="demand-03f48d9095d89aa82a7c"></a>

### demand · demand\_e89d369b316e5ed308f9

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_73141ae109e6fb35cff1&quot;
  ]
}</pre>

<a id="demand-c80b979982a3790c7e4f"></a>

### demand · demand\_e988c039d89c1763ac21

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 5,
    &quot;data_ids&quot;: [
      &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R5&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_99915fbe3f62e1af0426&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_0f342157a8515367497a&quot;,
    &quot;demand_2265116b7cfa70e7b4fd&quot;,
    &quot;demand_f39fdd98d6d3cb57415c&quot;
  ]
}</pre>

<a id="demand-f1a2b94792c9eac748a1"></a>

### demand · demand\_eaa1740ae1512b5396c9

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_9b45307c579d6df84415&quot;
  ]
}</pre>

<a id="demand-32927936326fd660dc26"></a>

### demand · demand\_eb8c53fc958b1eeaeb7f

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 2,
    &quot;data_ids&quot;: [
      &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_70b2fa7b5c54a135467d&quot;,
    &quot;demand_f7ebe9090e7e8e852b0e&quot;
  ]
}</pre>

<a id="demand-202b05e6e475f5c1be5f"></a>

### demand · demand\_ebfc76d70055a0204f1b

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: &quot;op_ir_004:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_0f95adba03c8b5c7d0df&quot;
  ]
}</pre>

<a id="demand-bef8c8389684547fdfa0"></a>

### demand · demand\_ecf094d1f91d32a49a29

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_19163dc921148efcdf63&quot;
  ]
}</pre>

<a id="demand-4a6e724c834c99581083"></a>

### demand · demand\_ed053d38c1c3c958466c

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R5&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_99915fbe3f62e1af0426&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_10bd0a708d3f8dc5425f&quot;
  ]
}</pre>

<a id="demand-972e7653581144295f37"></a>

### demand · demand\_ee03d6918aa2bfde483d

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: &quot;op_ir_001:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;from_date&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R3&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_c25263b0b7055126cef1&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_bf8055ea0bc0dea4bc17&quot;
  ]
}</pre>

<a id="demand-78d25758d5c5ff1f4798"></a>

### demand · demand\_ef34de16517bcc0ba0dc

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 4,
    &quot;data_ids&quot;: [
      &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_c4aaa01e135b1d3c60fc&quot;,
    &quot;demand_de974e2b6cdb2ec6815d&quot;
  ]
}</pre>

<a id="demand-22d6d94eba12d689a6ae"></a>

### demand · demand\_ef44a9bba39f75fb78a5

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 3,
    &quot;data_ids&quot;: [
      &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R6&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_da9ae22c3399787be23d&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;member_presence&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_c73b1e4863ac33e110b4&quot;
  ]
}</pre>

<a id="demand-e0ae1c8a14a77d8333d8"></a>

### demand · demand\_ef7bc36a49ee5facb86d

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R2&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9704dcab72933209f08&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_9bb97c53e9fd4ea8bcc4&quot;
  ]
}</pre>

<a id="demand-d6169d05cb23f96c5283"></a>

### demand · demand\_f0b30b8b6fb7dd22cd2a

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_004&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_477b6ab435de27de43c7&quot;
  ]
}</pre>

<a id="demand-d4ef29862d571a8197e4"></a>

### demand · demand\_f0f265b2497e30deb0da

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 2,
    &quot;data_ids&quot;: [
      &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R3&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_c25263b0b7055126cef1&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;required_original_value&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_21fc99a5f39f0a12bb33&quot;,
    &quot;demand_e5b4ea3e00aaa215f221&quot;
  ]
}</pre>

<a id="demand-f26990822abf77f9a6cd"></a>

### demand · demand\_f23311e087bb37baeef9

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_060d059caea61b0856a0&quot;
  ]
}</pre>

<a id="demand-1a587340a582537773f4"></a>

### demand · demand\_f2bb42d64236e7f67d4a

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R5&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_99915fbe3f62e1af0426&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_80b80e5e32bb4975cf54&quot;
  ]
}</pre>

<a id="demand-863b887dfecb9560cd13"></a>

### demand · demand\_f39fdd98d6d3cb57415c

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e3:a0&quot;,
    &quot;slot&quot;: 3,
    &quot;data_ids&quot;: [
      &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R5&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_99915fbe3f62e1af0426&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;member_presence&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_a0f746440856254f3e55&quot;
  ]
}</pre>

<a id="demand-667d40765221e8b7b130"></a>

### demand · demand\_f54f30d8eb9442c92ff5

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e1:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_114096bf95c05c2a53a52fa5de6a19045b7cfecaa8e6b68d97e03813870eb7bf&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_a830ab582af19c9ae211&quot;
  ]
}</pre>

<a id="demand-604e19d979ec701a034c"></a>

### demand · demand\_f7ebe9090e7e8e852b0e

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_8f4af431e0b026293d9b0044252f478573499cbb76e33baf5428032281444341&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_70b2fa7b5c54a135467d&quot;
  ]
}</pre>

<a id="demand-634a1fcc89a758565cc8"></a>

### demand · demand\_f85c7bec526edab12a40

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_226185ce3ae84e4a5551&quot;
  ]
}</pre>

<a id="demand-b56a13827e22bea96ef2"></a>

### demand · demand\_f9881e439c26f60c118b

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R6&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_da9ae22c3399787be23d&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_7e08c07d87242c733f11&quot;,
    &quot;demand_d7ec078f0532d17ef79e&quot;
  ]
}</pre>

<a id="demand-bfc6add67177e3c9a484"></a>

### demand · demand\_fa0d743285ad8d862d11

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e1:a0&quot;,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;conditional_observation&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_f7ebe9090e7e8e852b0e&quot;
  ]
}</pre>

<a id="demand-2830d862ced946a8db67"></a>

### demand · demand\_fb0fb70eb3d7b7b5b6a8

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_4cc5a97ab0c28d7dbf58026cdee76d13b976dd99b091bff3557a62b78071c33d&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_3f72c371567eb238315b&quot;
  ]
}</pre>

<a id="demand-21c7c35a2f1f08a924b3"></a>

### demand · demand\_fb2050d056b0101a52c6

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e0:a0&quot;,
    &quot;slot&quot;: 1,
    &quot;data_ids&quot;: [
      &quot;data_12e34c464a8267b27600f3a61bb5babb4650f38431c98669af52f635a522cfba&quot;
    ]
  },
  &quot;property&quot;: &quot;truth&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_a121999a238e2b343db5&quot;
  ]
}</pre>

<a id="demand-2ce9239533742e0b8257"></a>

### demand · demand\_fb3898ec36137409560d

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 4,
    &quot;data_ids&quot;: [
      &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R5&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_99915fbe3f62e1af0426&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;required_original_value&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_84f9c21c73468e5a9f36&quot;,
    &quot;demand_8cec444e21f59eae5821&quot;
  ]
}</pre>

<a id="demand-b878b93e9bfdeb3848f7"></a>

### demand · demand\_fbddddbc2453964e4624

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: &quot;op_ir_007:e4:a1&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
      &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
      &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
      &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;total&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;actual_operand&quot;,
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_1527693ead3389526798&quot;,
    &quot;demand_fcda4d95d9313530c05b&quot;
  ]
}</pre>

<a id="demand-87377a35a40c8d3729df"></a>

### demand · demand\_fcda4d95d9313530c05b

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_007&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_1ad20aea1ad7f32abc950606396ba5759aa2e2cdb9aee3b9838bb416fc304690&quot;,
      &quot;data_47bc986c8fc90b7bdc4b1eb88308652cf6dd1d0963b38d7ac85a543dc48357a5&quot;,
      &quot;data_532758a66c9c9321eb7997c43c753e74e616dce610d7c3f825d512bd4fcd5850&quot;,
      &quot;data_66e7798e4b968768401b463b2eccf1076b9066ff34005e5099d01ff4940b5de1&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;total&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_3d08c880775f9f9ac1e7&quot;
  ]
}</pre>

<a id="demand-8b9819f04348f6f1844c"></a>

### demand · demand\_fcf417f85ceb391d20a2

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_003&quot;,
    &quot;operation_id&quot;: &quot;op_ir_003:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;selected_path&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_74e011a283e3c2a7c497&quot;
  ]
}</pre>

<a id="demand-7a4ad65ef0f7282016d7"></a>

### demand · demand\_fcfb3c9f3b78737b0e31

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_60fe8bfc7dbac9467679&quot;
  ]
}</pre>

<a id="demand-18726b1f30a85dfe573e"></a>

### demand · demand\_fdaa28ea47863a88b661

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_63df6aae8b097f6c061ffd51c2d99211459d1e575a757eec56c52f52bb62d2d1&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R5&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_99915fbe3f62e1af0426&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_516ebbbcda4dd4401481&quot;
  ]
}</pre>

<a id="demand-2f3d09e2de7e3a55ef73"></a>

### demand · demand\_fdb88a29a419e92159ef

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_011&quot;,
    &quot;operation_id&quot;: &quot;op_ir_011:e1:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_41579c3d03f6f282e27032d6d90b1f0b803d643172579ecd01a36d619a4e97ab&quot;,
      &quot;data_65a79b1fbed9a71475acf516876593e476ab10fe2ad3c2ed599a5717e0edcfb7&quot;,
      &quot;data_a3fbf7f05105730eaa540813bac298a6a0f9e9e9c905244b323c4262bfa51eb7&quot;,
      &quot;data_ed5a774645da77bcd5c8de30cc27cf7137b52e0eb86af26412a0169bec42bcc8&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: false,
  &quot;rules&quot;: [
    &quot;public_result&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_941c77f8f1ee40589119&quot;
  ]
}</pre>

<a id="demand-775d38df890879122bea"></a>

### demand · demand\_fe314a23bc872fb4b635

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;op_input&quot;,
    &quot;instruction_id&quot;: &quot;ir_005&quot;,
    &quot;operation_id&quot;: &quot;op_ir_005:e0:a0&quot;,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;presence&quot;,
  &quot;path&quot;: [
    &quot;limit&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R8&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_b9a86bc8698a176813fb&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;processing_boundary&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_ac951b8bf04df1b81904&quot;
  ]
}</pre>

<a id="demand-56a1330f282953a3d2bc"></a>

### demand · demand\_ffb8870545afc91e7312

<pre>{
  &quot;node&quot;: {
    &quot;kind&quot;: &quot;ir_output&quot;,
    &quot;instruction_id&quot;: &quot;ir_001&quot;,
    &quot;operation_id&quot;: null,
    &quot;slot&quot;: 0,
    &quot;data_ids&quot;: [
      &quot;data_b3d729a455434e5c963d6b3c41890d110e5a871ff805abb24968f6cb595c54e6&quot;
    ]
  },
  &quot;property&quot;: &quot;value&quot;,
  &quot;path&quot;: [
    &quot;term&quot;
  ],
  &quot;each&quot;: false,
  &quot;excluded_paths&quot;: [],
  &quot;requirement_id&quot;: &quot;R9&quot;,
  &quot;seed_goal_id&quot;: &quot;goal_6e5ca31142833529f175&quot;,
  &quot;conservative&quot;: true,
  &quot;rules&quot;: [
    &quot;cfg_result_use&quot;
  ],
  &quot;parents&quot;: [
    &quot;demand_adb35267dcc6986504be&quot;
  ]
}</pre>

## Diagnostics and limitations

<pre>[
  {
    &quot;id&quot;: &quot;diagnostic_0d29a666fd3a446e29e4&quot;,
    &quot;code&quot;: &quot;unbound_requirement&quot;,
    &quot;reason&quot;: &quot;No applicable demand goal is available; this does not mean the requirement can be omitted.&quot;,
    &quot;instruction_id&quot;: null,
    &quot;operation_id&quot;: null,
    &quot;blocking&quot;: true
  },
  {
    &quot;id&quot;: &quot;diagnostic_23efa867ad6a3e638305&quot;,
    &quot;code&quot;: &quot;requirement_expression_gap&quot;,
    &quot;reason&quot;: &quot;This requirement is not fully expressed as positive demands and supported constraints. No program-verifiable local impact boundary is available; retain it as a global limitation.&quot;,
    &quot;instruction_id&quot;: null,
    &quot;operation_id&quot;: null,
    &quot;blocking&quot;: true
  }
]</pre>
