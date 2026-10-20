# Source → Task → declarations whole-chain review

**Material issues found** · Execution status: `complete`

Review structure, references, evidence and declared coverage passed validation\.

This semantic review does not rewrite the sealed Task, annotation or propagation facts. Accounting coverage of source, Task, demand/constraint declarations and IR does not prove semantic completeness; no reported issue does not prove correct interpretation, minimal demands or absence of DOE.

## Per-requirement semantic correspondence

Expression status and review acceptance do not prove requirement satisfaction. Full source excerpts, remaining gaps and resolved declarations appear in the audit records below.

| Source span | Task requirement | Expression status | Raw demand / constraint | Review record |
| --- | --- | --- | --- | --- |
| skill/SKILL\.md:8\-8 | R1: Read source\_id from the user's request\. | expressed | /ir\_semantics/ir\_001/events/0/events/1/atomic\_ops/0/demands/0 → goal\_a261f0fd5f8da40022a7 | accepted |
| skill/SKILL\.md:8\-8 | R2: Read FAST\_KEY from the environment\. | expressed | /ir\_semantics/ir\_003/events/0/events/1/atomic\_ops/0/demands/0 → goal\_d30d3a4a1e1841d46fe6 | accepted |
| skill/SKILL\.md:9\-9 | R3: If FAST\_KEY is present, try fast\.fetch first with source\_id and FAST\_KEY\. | expressed | /ir\_semantics/ir\_005/events/0/events/0/atomic\_ops/0/demands/0 → goal\_2a9825475f80aaa968ad; /ir\_semantics/ir\_007/events/0/events/0/atomic\_ops/0/demands/0 → goal\_6e4e685b49d46bb16bf4; /ir\_semantics/ir\_007/events/0/events/0/atomic\_ops/0/demands/1 → goal\_a5f6c9837a8185ed2842; /ir\_semantics/ir\_007/events/0/events/0/atomic\_ops/0/demands/2 → goal\_2ba7d40cc0fcd7e52de6; /realizations/2/constraints/0 → constraint\_1b7c5783e6231f705c43 | accepted |
| skill/SKILL\.md:9\-9 | R4: If FAST\_KEY is absent, go directly to archive\.fetch without calling fast\.fetch\. | expressed | /realizations/3/constraints/0 → constraint\_66cbca1f9f0a4ce1c16d | accepted |
| skill/SKILL\.md:10\-10 | R5: Retry fast\.fetch exactly once only when its first attempt fails with a transient error\. | expressed | /ir\_semantics/ir\_009/events/0/events/0/atomic\_ops/1/demands/0 → goal\_6b5988f5263a79d34337; /ir\_semantics/ir\_011/events/0/events/0/atomic\_ops/0/demands/0 → goal\_a90b9011370a95405c6d; /ir\_semantics/ir\_011/events/0/events/0/atomic\_ops/0/demands/1 → goal\_96270f451e2273da9604; /ir\_semantics/ir\_011/events/0/events/0/atomic\_ops/0/demands/2 → goal\_a852d40a2988d53d8768; /realizations/4/constraints/0 → constraint\_a8b104b4038cf4cbc6ad; /realizations/4/constraints/1 → constraint\_9f020b53b4e158b9669f | accepted |
| skill/SKILL\.md:10\-10 | R6: Do not retry a non\-transient first failure of fast\.fetch\. | expressed | /realizations/5/constraints/0 → constraint\_a37723a5cd62afd22ada | accepted |
| skill/SKILL\.md:11\-11 | R7: After a non\-transient first failure of fast\.fetch or any failed retry of fast\.fetch, call archive\.fetch with source\_id\. | expressed | /ir\_semantics/ir\_015/events/0/events/0/atomic\_ops/0/demands/0 → goal\_d787e8db6e7691331844 | accepted |
| skill/SKILL\.md:12\-12 | R8: Call archive\.fetch at most once\. | expressed | /realizations/7/constraints/0 → constraint\_c513ca74cfaeefaf1cc3 | accepted |
| skill/SKILL\.md:12\-12 | R9: Pass source\_id as archive\.fetch's only argument\. | expressed | /ir\_semantics/ir\_015/events/0/events/0/atomic\_ops/0/demands/1 → goal\_675ec0f7a54d9d424017 | accepted |
| skill/SKILL\.md:13\-13 | R10: On either tool's success, return that successful response's body value unchanged\. | expressed | /demands/0 → goal\_d93049b68b0aee6a8642; /demands/1 → goal\_9f03413bc5487ca4b779; /demands/2 → goal\_e1d07e741cb504a0ac41 | accepted |
| skill/SKILL\.md:13\-13 | R11: On either tool's success, make no further fetch calls\. | expressed | /realizations/10/constraints/0 → constraint\_2b913793dbcaf7a01836; /realizations/10/constraints/1 → constraint\_71073f9ea8ec714d0454; /realizations/10/constraints/2 → constraint\_d815395f81b3dc192bbf | accepted |
| skill/SKILL\.md:14\-14 | R12: If archive\.fetch fails, stop and return its error\. | expressed | /demands/3 → goal\_6eee0f7a3828e67b679a | accepted |
| skill/SKILL\.md:14\-14 | R13: Do not retry archive\.fetch after it fails\. | expressed | /realizations/12/constraints/0 → constraint\_b2e1364a394954033e2c | accepted |
| skill/SKILL\.md:15\-15 | R14: Never pass FAST\_KEY to archive\.fetch anywhere in this workflow\. | expressed | /realizations/13/constraints/0 → constraint\_77a32f9f420b5b5e458a | accepted |
| skill/SKILL\.md:15\-15 | R15: Never pass FAST\_KEY to diagnostic output anywhere in this workflow\. | expressed | /realizations/14/constraints/0 → constraint\_b0a4ced734ab0cbf2849 | accepted |
| skill/SKILL\.md:16\-16 | R16: Before returning from every success or failure path, append the final status to local status\.txt\. | expressed | /ir\_semantics/ir\_019/events/0/events/0/atomic\_ops/0/demands/0 → goal\_c47884c5742ed8ccf272; /ir\_semantics/ir\_019/events/0/events/0/atomic\_ops/0/demands/1 → goal\_ab5998e1d2c9fb6bfc3b; /ir\_semantics/ir\_021/events/0/events/0/atomic\_ops/0/demands/0 → goal\_22399659989102b4bccd; /ir\_semantics/ir\_021/events/0/events/0/atomic\_ops/0/demands/1 → goal\_96dc9eea7ab05d4949bd; /ir\_semantics/ir\_023/events/0/events/0/atomic\_ops/0/demands/0 → goal\_439b9439a0e53de21020; /ir\_semantics/ir\_023/events/0/events/0/atomic\_ops/0/demands/1 → goal\_09766dec5e6c505297e2; /ir\_semantics/ir\_025/events/0/events/0/atomic\_ops/0/demands/0 → goal\_4881a7316e21c9fe13ac; /ir\_semantics/ir\_025/events/0/events/0/atomic\_ops/0/demands/1 → goal\_204d92e17659496cbcd3; /realizations/15/constraints/0 → constraint\_2fcde5b35cd07b608d0f; /realizations/15/constraints/1 → constraint\_24d8c02c945f3c0f7990; /realizations/15/constraints/2 → constraint\_84c8dde9c7076665a166; /realizations/15/constraints/3 → constraint\_0f1284eaa47a8a793d1e | issue |

## F001 · annotation

All four status\-append write operations reference IR input index 1, but each enclosing instruction has a single input at index 0\. The corresponding input demands resolve to the same nonexistent input index 1, so the required final\-status payload is not linked to the actual outcome value on any return path\. This leaves R16 only partially represented despite the otherwise correct append action and ordering\.

Related targets: ann\_0414, ann\_0420, ann\_0446, ann\_0452, ann\_0478, ann\_0484, ann\_0510, ann\_0516

Suggested change: Keep the four append operations, their status\_file target, action demands, and requires\_prior constraints\. Change each write atomic op input ValueRef from \{"kind":"input","index":1\} to \{"kind":"input","index":0\} in ir\_019, ir\_021, ir\_023, and ir\_025, so the existing operation\-slot\-0 input demands resolve to the actual outcome value\. Do not change the CFG input lists; recompile any status\-write observations after correcting the payload references\.

- skill/SKILL\.md:16\-16: 9\. Before returning from every success or failure path, append the final status to local status\.txt\.

  Evidence rationale: The source requires the final status to be appended to local status\.txt before every return path\.
- \{"instruction\_id": "ir\_019", "path": \[\]\}: \{"id":"ir\_019","opcode":"append\_final\_status\_to\_local\_status\_file","inputs":\[\{"type":"external\_resource","identifier":"status\.txt","semantic\_name":"status\.txt"\},\{"type":"result","identifier":"result\_005","semantic\_name":"fast\_fetch\_first\_outcome"\}\],"outputs":\[\],"constraints":\["Before returning from every success or failure path, append the final status to local status\.txt\."\],"metadata":\{\},"draft\_instruction\_id":"append\_fast\_fetch\_first\_status"\}
  Evidence rationale: The IR instruction exposes a single input operand at index 0\.
- \{"instruction\_id": "ir\_021", "path": \[\]\}: \{"id":"ir\_021","opcode":"append\_final\_status\_to\_local\_status\_file","inputs":\[\{"type":"external\_resource","identifier":"status\.txt","semantic\_name":"status\.txt"\},\{"type":"result","identifier":"result\_008","semantic\_name":"fast\_fetch\_retry\_outcome"\}\],"outputs":\[\],"constraints":\["Before returning from every success or failure path, append the final status to local status\.txt\."\],"metadata":\{\},"draft\_instruction\_id":"append\_fast\_fetch\_retry\_status"\}
  Evidence rationale: The IR instruction exposes a single input operand at index 0\.
- \{"instruction\_id": "ir\_023", "path": \[\]\}: \{"id":"ir\_023","opcode":"append\_final\_status\_to\_local\_status\_file","inputs":\[\{"type":"external\_resource","identifier":"status\.txt","semantic\_name":"status\.txt"\},\{"type":"result","identifier":"result\_011","semantic\_name":"archive\_fetch\_outcome"\}\],"outputs":\[\],"constraints":\["Before returning from every success or failure path, append the final status to local status\.txt\."\],"metadata":\{\},"draft\_instruction\_id":"append\_archive\_fetch\_success\_status"\}
  Evidence rationale: The IR instruction exposes a single input operand at index 0\.
- \{"instruction\_id": "ir\_025", "path": \[\]\}: \{"id":"ir\_025","opcode":"append\_final\_status\_to\_local\_status\_file","inputs":\[\{"type":"external\_resource","identifier":"status\.txt","semantic\_name":"status\.txt"\},\{"type":"result","identifier":"result\_011","semantic\_name":"archive\_fetch\_outcome"\}\],"outputs":\[\],"constraints":\["Before returning from every success or failure path, append the final status to local status\.txt\."\],"metadata":\{\},"draft\_instruction\_id":"append\_archive\_fetch\_failure\_status"\}
  Evidence rationale: The IR instruction exposes a single input operand at index 0\.

## Audit materials

IR declared reviewed: ir\_001, ir\_002, ir\_003, ir\_004, ir\_005, ir\_006, ir\_007, ir\_008, ir\_009, ir\_010, ir\_011, ir\_012, ir\_013, ir\_014, ir\_015, ir\_016, ir\_017, ir\_018, ir\_019, ir\_020, ir\_021, ir\_022, ir\_023, ir\_024, ir\_025, ir\_026

Request, JSON normalization and structural correction counts: \{
  "logical\_calls": 1,
  "stage\_calls": 1,
  "structural\_corrections": 0,
  "json\_normalizations": 0,
  "http\_attempts": 1,
  "http\_retries": 0,
  "http\_attempts\_observed": true,
  "returned\_models": \[
    "deepseek\-flash"
  \],
  "known\_token\_usage": \{
    "input\_tokens": 69604,
    "output\_tokens": 63242,
    "total\_tokens": 132846
  \},
  "record\_integrity\_errors": \[\]
\}

Request chain: [chain.json](../calls/review/chain.json); Targets: [targets.json](../inputs/targets.json); Observations: [observations.json](../inputs/observations.json).

### Four-axis records and program-resolved targets

```json
{
  "Source_Task_declarations_correspondence": [
    {
      "requirement_id": "R1",
      "text": "Read source_id from the user's request.",
      "source_evidence": [
        {
          "reference": "skill/SKILL.md:8-8",
          "excerpt": "1. Read source_id from the user's request and read FAST_KEY from the environment.\n",
          "reason": "The first workflow step requires reading source_id from the user's request."
        }
      ],
      "realization": {
        "requirement_id": "R1",
        "status": "expressed",
        "bindings": [
          {
            "target": {
              "instruction_id": "ir_001",
              "path": []
            },
            "reason": "ir_001 reads the user_request context and selects source_id."
          },
          {
            "target": {
              "block_id": "block_001",
              "path": []
            },
            "reason": "block_001 contains the source_id acquisition step."
          }
        ],
        "gaps": []
      },
      "declarations": [
        {
          "kind": "demand",
          "raw_pointer": "/ir_semantics/ir_001/events/0/events/1/atomic_ops/0/demands/0",
          "goal_id": "goal_a261f0fd5f8da40022a7",
          "requirement_id": "R1",
          "target": {
            "instruction_id": "ir_001",
            "operation_path": [
              "events",
              0,
              "events",
              1,
              "atomic_ops",
              0
            ],
            "slot": {
              "kind": "self"
            }
          },
          "goal": {
            "requirement_id": "R1",
            "target": {
              "instruction_id": "ir_001",
              "operation_path": [
                "events",
                0,
                "events",
                1,
                "atomic_ops",
                0
              ],
              "slot": {
                "kind": "self"
              }
            },
            "preserve": "value",
            "path": [],
            "expected": null,
            "expected_path": [],
            "reason": "Preserve the source_id selected from the user request.",
            "id": "goal_a261f0fd5f8da40022a7"
          },
          "resolved_target": {
            "domain": "transfer",
            "kind": "operation",
            "instruction_id": "ir_001",
            "pointer": "/ir_semantics/ir_001/events/0/events/1/atomic_ops/0",
            "scope_path": null,
            "operation_raw_path": [
              "events",
              0,
              "events",
              1,
              "atomic_ops",
              0
            ],
            "available_locals": [
              "user_request_snapshot"
            ],
            "op": "select_part",
            "declared_refs": [
              {
                "kind": "local",
                "name": "user_request_snapshot"
              }
            ],
            "output": "source_id"
          }
        }
      ],
      "review_check": {
        "status": "accepted",
        "reason": "ir_001 reads user_request and selects source_id; the realization and demand preserve the selected value.",
        "finding_ids": [],
        "requirement_id": "R1"
      }
    },
    {
      "requirement_id": "R2",
      "text": "Read FAST_KEY from the environment.",
      "source_evidence": [
        {
          "reference": "skill/SKILL.md:8-8",
          "excerpt": "1. Read source_id from the user's request and read FAST_KEY from the environment.\n",
          "reason": "The first workflow step requires reading FAST_KEY from the environment."
        }
      ],
      "realization": {
        "requirement_id": "R2",
        "status": "expressed",
        "bindings": [
          {
            "target": {
              "instruction_id": "ir_003",
              "path": []
            },
            "reason": "ir_003 reads the environment context and selects FAST_KEY."
          },
          {
            "target": {
              "block_id": "block_002",
              "path": []
            },
            "reason": "block_002 contains the FAST_KEY acquisition step."
          }
        ],
        "gaps": []
      },
      "declarations": [
        {
          "kind": "demand",
          "raw_pointer": "/ir_semantics/ir_003/events/0/events/1/atomic_ops/0/demands/0",
          "goal_id": "goal_d30d3a4a1e1841d46fe6",
          "requirement_id": "R2",
          "target": {
            "instruction_id": "ir_003",
            "operation_path": [
              "events",
              0,
              "events",
              1,
              "atomic_ops",
              0
            ],
            "slot": {
              "kind": "self"
            }
          },
          "goal": {
            "requirement_id": "R2",
            "target": {
              "instruction_id": "ir_003",
              "operation_path": [
                "events",
                0,
                "events",
                1,
                "atomic_ops",
                0
              ],
              "slot": {
                "kind": "self"
              }
            },
            "preserve": "value",
            "path": [],
            "expected": null,
            "expected_path": [],
            "reason": "Preserve the FAST_KEY selected from the environment.",
            "id": "goal_d30d3a4a1e1841d46fe6"
          },
          "resolved_target": {
            "domain": "transfer",
            "kind": "operation",
            "instruction_id": "ir_003",
            "pointer": "/ir_semantics/ir_003/events/0/events/1/atomic_ops/0",
            "scope_path": null,
            "operation_raw_path": [
              "events",
              0,
              "events",
              1,
              "atomic_ops",
              0
            ],
            "available_locals": [
              "environment_snapshot"
            ],
            "op": "select_part",
            "declared_refs": [
              {
                "kind": "local",
                "name": "environment_snapshot"
              }
            ],
            "output": "fast_key"
          }
        }
      ],
      "review_check": {
        "status": "accepted",
        "reason": "ir_003 reads environment and selects FAST_KEY; the realization, demand, and credential sensitivity support the requirement.",
        "finding_ids": [],
        "requirement_id": "R2"
      }
    },
    {
      "requirement_id": "R3",
      "text": "If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY.",
      "source_evidence": [
        {
          "reference": "skill/SKILL.md:9-9",
          "excerpt": "2. If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch.\n",
          "reason": "This line states the preferred-tool path conditioned on FAST_KEY being present."
        }
      ],
      "realization": {
        "requirement_id": "R3",
        "status": "expressed",
        "bindings": [
          {
            "target": {
              "block_id": "block_003",
              "path": []
            },
            "reason": "The FAST_KEY present edge routes to the first fast.fetch call."
          },
          {
            "target": {
              "instruction_id": "ir_005",
              "path": []
            },
            "reason": "ir_005 computes whether FAST_KEY is present."
          },
          {
            "target": {
              "instruction_id": "ir_007",
              "path": []
            },
            "reason": "ir_007 is the first fast.fetch call with source_id and FAST_KEY on the present path."
          }
        ],
        "gaps": [],
        "constraints": [
          {
            "scope": {
              "kind": "task"
            },
            "kind": "only_if",
            "events": [
              {
                "instruction_id": "ir_007",
                "operation_path": [
                  "events",
                  0,
                  "events",
                  0,
                  "atomic_ops",
                  0
                ],
                "slot": {
                  "kind": "self"
                }
              }
            ],
            "condition": {
              "instruction_id": "ir_005",
              "operation_path": [
                "events",
                0,
                "events",
                0,
                "atomic_ops",
                0
              ],
              "slot": {
                "kind": "self"
              }
            }
          }
        ]
      },
      "declarations": [
        {
          "kind": "demand",
          "raw_pointer": "/ir_semantics/ir_005/events/0/events/0/atomic_ops/0/demands/0",
          "goal_id": "goal_2a9825475f80aaa968ad",
          "requirement_id": "R3",
          "target": {
            "instruction_id": "ir_005",
            "operation_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "slot": {
              "kind": "self"
            }
          },
          "goal": {
            "requirement_id": "R3",
            "target": {
              "instruction_id": "ir_005",
              "operation_path": [
                "events",
                0,
                "events",
                0,
                "atomic_ops",
                0
              ],
              "slot": {
                "kind": "self"
              }
            },
            "preserve": "truth",
            "path": [],
            "expected": null,
            "expected_path": [],
            "reason": "Preserve whether FAST_KEY is present to choose the fast.fetch path.",
            "id": "goal_2a9825475f80aaa968ad"
          },
          "resolved_target": {
            "domain": "transfer",
            "kind": "operation",
            "instruction_id": "ir_005",
            "pointer": "/ir_semantics/ir_005/events/0/events/0/atomic_ops/0",
            "scope_path": null,
            "operation_raw_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "available_locals": [],
            "op": "compute",
            "declared_refs": [
              {
                "kind": "input",
                "index": 0
              }
            ],
            "output": "fast_key_present"
          }
        },
        {
          "kind": "demand",
          "raw_pointer": "/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/0",
          "goal_id": "goal_6e4e685b49d46bb16bf4",
          "requirement_id": "R3",
          "target": {
            "instruction_id": "ir_007",
            "operation_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "slot": {
              "kind": "self"
            }
          },
          "goal": {
            "requirement_id": "R3",
            "target": {
              "instruction_id": "ir_007",
              "operation_path": [
                "events",
                0,
                "events",
                0,
                "atomic_ops",
                0
              ],
              "slot": {
                "kind": "self"
              }
            },
            "preserve": "action",
            "path": [],
            "expected": null,
            "expected_path": [],
            "reason": "Try fast.fetch first on the FAST_KEY present path.",
            "id": "goal_6e4e685b49d46bb16bf4"
          },
          "resolved_target": {
            "domain": "transfer",
            "kind": "operation",
            "instruction_id": "ir_007",
            "pointer": "/ir_semantics/ir_007/events/0/events/0/atomic_ops/0",
            "scope_path": null,
            "operation_raw_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "available_locals": [],
            "op": "deliver",
            "declared_refs": [
              {
                "kind": "input",
                "index": 1
              },
              {
                "kind": "input",
                "index": 2
              }
            ]
          }
        },
        {
          "kind": "demand",
          "raw_pointer": "/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/1",
          "goal_id": "goal_a5f6c9837a8185ed2842",
          "requirement_id": "R3",
          "target": {
            "instruction_id": "ir_007",
            "operation_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "slot": {
              "kind": "input",
              "index": 0
            }
          },
          "goal": {
            "requirement_id": "R3",
            "target": {
              "instruction_id": "ir_007",
              "operation_path": [
                "events",
                0,
                "events",
                0,
                "atomic_ops",
                0
              ],
              "slot": {
                "kind": "input",
                "index": 0
              }
            },
            "preserve": "value",
            "path": [],
            "expected": {
              "kind": "input",
              "index": 1
            },
            "expected_path": [],
            "reason": "Pass the original source_id to fast.fetch.",
            "id": "goal_a5f6c9837a8185ed2842"
          },
          "resolved_target": {
            "domain": "transfer",
            "kind": "input_use",
            "instruction_id": "ir_007",
            "pointer": "/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/uses/0",
            "slot": 0,
            "ref": {
              "kind": "input",
              "index": 1
            },
            "role": "value",
            "when": null,
            "member_index": null,
            "scope_path": null,
            "operation_raw_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "available_locals": []
          }
        },
        {
          "kind": "demand",
          "raw_pointer": "/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/2",
          "goal_id": "goal_2ba7d40cc0fcd7e52de6",
          "requirement_id": "R3",
          "target": {
            "instruction_id": "ir_007",
            "operation_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "slot": {
              "kind": "input",
              "index": 1
            }
          },
          "goal": {
            "requirement_id": "R3",
            "target": {
              "instruction_id": "ir_007",
              "operation_path": [
                "events",
                0,
                "events",
                0,
                "atomic_ops",
                0
              ],
              "slot": {
                "kind": "input",
                "index": 1
              }
            },
            "preserve": "value",
            "path": [],
            "expected": {
              "kind": "input",
              "index": 2
            },
            "expected_path": [],
            "reason": "Pass the original FAST_KEY to fast.fetch.",
            "id": "goal_2ba7d40cc0fcd7e52de6"
          },
          "resolved_target": {
            "domain": "transfer",
            "kind": "input_use",
            "instruction_id": "ir_007",
            "pointer": "/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/uses/1",
            "slot": 1,
            "ref": {
              "kind": "input",
              "index": 2
            },
            "role": "value",
            "when": null,
            "member_index": null,
            "scope_path": null,
            "operation_raw_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "available_locals": []
          }
        },
        {
          "kind": "constraint",
          "constraint_id": "constraint_1b7c5783e6231f705c43",
          "requirement_id": "R3",
          "raw_pointer": "/realizations/2/constraints/0"
        }
      ],
      "review_check": {
        "status": "accepted",
        "reason": "The FAST_KEY-present condition gates ir_007, and both source_id and FAST_KEY inputs are preserved for the first fast.fetch call.",
        "finding_ids": [],
        "requirement_id": "R3"
      }
    },
    {
      "requirement_id": "R4",
      "text": "If FAST_KEY is absent, go directly to archive.fetch without calling fast.fetch.",
      "source_evidence": [
        {
          "reference": "skill/SKILL.md:9-9",
          "excerpt": "2. If FAST_KEY is present, try fast.fetch first with source_id and FAST_KEY; if it is absent, go directly to archive.fetch without calling fast.fetch.\n",
          "reason": "This line states the archive-only path when FAST_KEY is absent."
        }
      ],
      "realization": {
        "requirement_id": "R4",
        "status": "expressed",
        "bindings": [
          {
            "target": {
              "block_id": "block_003",
              "path": []
            },
            "reason": "The FAST_KEY absent edge from block_003 routes directly to block_008."
          },
          {
            "target": {
              "block_id": "block_008",
              "path": []
            },
            "reason": "block_008 is the archive.fetch path reached when FAST_KEY is absent, without entering block_004."
          },
          {
            "target": {
              "instruction_id": "ir_015",
              "path": []
            },
            "reason": "ir_015 is the archive.fetch call used on the absent path."
          }
        ],
        "gaps": [],
        "constraints": [
          {
            "scope": {
              "kind": "task"
            },
            "kind": "only_if",
            "events": [
              {
                "instruction_id": "ir_007",
                "operation_path": [
                  "events",
                  0,
                  "events",
                  0,
                  "atomic_ops",
                  0
                ],
                "slot": {
                  "kind": "self"
                }
              }
            ],
            "condition": {
              "instruction_id": "ir_005",
              "operation_path": [
                "events",
                0,
                "events",
                0,
                "atomic_ops",
                0
              ],
              "slot": {
                "kind": "self"
              }
            }
          }
        ]
      },
      "declarations": [
        {
          "kind": "constraint",
          "constraint_id": "constraint_66cbca1f9f0a4ce1c16d",
          "requirement_id": "R4",
          "raw_pointer": "/realizations/3/constraints/0"
        }
      ],
      "review_check": {
        "status": "accepted",
        "reason": "The absent-FAST_KEY edge routes directly to archive.fetch, and the present-only gate prevents fast.fetch on that path.",
        "finding_ids": [],
        "requirement_id": "R4"
      }
    },
    {
      "requirement_id": "R5",
      "text": "Retry fast.fetch exactly once only when its first attempt fails with a transient error.",
      "source_evidence": [
        {
          "reference": "skill/SKILL.md:10-10",
          "excerpt": "3. Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure.\n",
          "reason": "This line defines the single transient-error retry obligation."
        }
      ],
      "realization": {
        "requirement_id": "R5",
        "status": "expressed",
        "bindings": [
          {
            "target": {
              "block_id": "block_005",
              "path": []
            },
            "reason": "block_005 classifies the first fast.fetch attempt and routes transient failures to retry."
          },
          {
            "target": {
              "block_id": "block_006",
              "path": []
            },
            "reason": "block_006 contains the single fast.fetch retry."
          },
          {
            "target": {
              "instruction_id": "ir_009",
              "path": []
            },
            "reason": "ir_009 computes the first outcome and an explicit transient classification used to gate the retry."
          },
          {
            "target": {
              "instruction_id": "ir_011",
              "path": []
            },
            "reason": "ir_011 performs the fast.fetch retry with source_id and FAST_KEY."
          }
        ],
        "gaps": [],
        "constraints": [
          {
            "scope": {
              "kind": "task"
            },
            "kind": "at_most",
            "events": [
              {
                "instruction_id": "ir_011",
                "operation_path": [
                  "events",
                  0,
                  "events",
                  0,
                  "atomic_ops",
                  0
                ],
                "slot": {
                  "kind": "self"
                }
              }
            ],
            "limit": 1,
            "unit": "attempt",
            "success": null
          },
          {
            "scope": {
              "kind": "task"
            },
            "kind": "only_if",
            "events": [
              {
                "instruction_id": "ir_011",
                "operation_path": [
                  "events",
                  0,
                  "events",
                  0,
                  "atomic_ops",
                  0
                ],
                "slot": {
                  "kind": "self"
                }
              }
            ],
            "condition": {
              "instruction_id": "ir_009",
              "operation_path": [
                "events",
                0,
                "events",
                0,
                "atomic_ops",
                1
              ],
              "slot": {
                "kind": "self"
              }
            }
          }
        ]
      },
      "declarations": [
        {
          "kind": "demand",
          "raw_pointer": "/ir_semantics/ir_009/events/0/events/0/atomic_ops/1/demands/0",
          "goal_id": "goal_6b5988f5263a79d34337",
          "requirement_id": "R5",
          "target": {
            "instruction_id": "ir_009",
            "operation_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              1
            ],
            "slot": {
              "kind": "self"
            }
          },
          "goal": {
            "requirement_id": "R5",
            "target": {
              "instruction_id": "ir_009",
              "operation_path": [
                "events",
                0,
                "events",
                0,
                "atomic_ops",
                1
              ],
              "slot": {
                "kind": "self"
              }
            },
            "preserve": "truth",
            "path": [],
            "expected": null,
            "expected_path": [],
            "reason": "Preserve whether the first fast.fetch attempt failed with a transient error to gate the retry.",
            "id": "goal_6b5988f5263a79d34337"
          },
          "resolved_target": {
            "domain": "transfer",
            "kind": "operation",
            "instruction_id": "ir_009",
            "pointer": "/ir_semantics/ir_009/events/0/events/0/atomic_ops/1",
            "scope_path": null,
            "operation_raw_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              1
            ],
            "available_locals": [
              "fast_fetch_first_outcome"
            ],
            "op": "compute",
            "declared_refs": [
              {
                "kind": "local",
                "name": "fast_fetch_first_outcome"
              }
            ],
            "output": "fast_fetch_first_transient"
          }
        },
        {
          "kind": "demand",
          "raw_pointer": "/ir_semantics/ir_011/events/0/events/0/atomic_ops/0/demands/0",
          "goal_id": "goal_a90b9011370a95405c6d",
          "requirement_id": "R5",
          "target": {
            "instruction_id": "ir_011",
            "operation_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "slot": {
              "kind": "self"
            }
          },
          "goal": {
            "requirement_id": "R5",
            "target": {
              "instruction_id": "ir_011",
              "operation_path": [
                "events",
                0,
                "events",
                0,
                "atomic_ops",
                0
              ],
              "slot": {
                "kind": "self"
              }
            },
            "preserve": "action",
            "path": [],
            "expected": null,
            "expected_path": [],
            "reason": "Retry fast.fetch exactly once on a transient first failure.",
            "id": "goal_a90b9011370a95405c6d"
          },
          "resolved_target": {
            "domain": "transfer",
            "kind": "operation",
            "instruction_id": "ir_011",
            "pointer": "/ir_semantics/ir_011/events/0/events/0/atomic_ops/0",
            "scope_path": null,
            "operation_raw_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "available_locals": [],
            "op": "deliver",
            "declared_refs": [
              {
                "kind": "input",
                "index": 1
              },
              {
                "kind": "input",
                "index": 2
              }
            ]
          }
        },
        {
          "kind": "demand",
          "raw_pointer": "/ir_semantics/ir_011/events/0/events/0/atomic_ops/0/demands/1",
          "goal_id": "goal_96270f451e2273da9604",
          "requirement_id": "R5",
          "target": {
            "instruction_id": "ir_011",
            "operation_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "slot": {
              "kind": "input",
              "index": 0
            }
          },
          "goal": {
            "requirement_id": "R5",
            "target": {
              "instruction_id": "ir_011",
              "operation_path": [
                "events",
                0,
                "events",
                0,
                "atomic_ops",
                0
              ],
              "slot": {
                "kind": "input",
                "index": 0
              }
            },
            "preserve": "value",
            "path": [],
            "expected": {
              "kind": "input",
              "index": 1
            },
            "expected_path": [],
            "reason": "Pass the original source_id on retry.",
            "id": "goal_96270f451e2273da9604"
          },
          "resolved_target": {
            "domain": "transfer",
            "kind": "input_use",
            "instruction_id": "ir_011",
            "pointer": "/ir_semantics/ir_011/events/0/events/0/atomic_ops/0/uses/0",
            "slot": 0,
            "ref": {
              "kind": "input",
              "index": 1
            },
            "role": "value",
            "when": null,
            "member_index": null,
            "scope_path": null,
            "operation_raw_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "available_locals": []
          }
        },
        {
          "kind": "demand",
          "raw_pointer": "/ir_semantics/ir_011/events/0/events/0/atomic_ops/0/demands/2",
          "goal_id": "goal_a852d40a2988d53d8768",
          "requirement_id": "R5",
          "target": {
            "instruction_id": "ir_011",
            "operation_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "slot": {
              "kind": "input",
              "index": 1
            }
          },
          "goal": {
            "requirement_id": "R5",
            "target": {
              "instruction_id": "ir_011",
              "operation_path": [
                "events",
                0,
                "events",
                0,
                "atomic_ops",
                0
              ],
              "slot": {
                "kind": "input",
                "index": 1
              }
            },
            "preserve": "value",
            "path": [],
            "expected": {
              "kind": "input",
              "index": 2
            },
            "expected_path": [],
            "reason": "Pass the original FAST_KEY on retry.",
            "id": "goal_a852d40a2988d53d8768"
          },
          "resolved_target": {
            "domain": "transfer",
            "kind": "input_use",
            "instruction_id": "ir_011",
            "pointer": "/ir_semantics/ir_011/events/0/events/0/atomic_ops/0/uses/1",
            "slot": 1,
            "ref": {
              "kind": "input",
              "index": 2
            },
            "role": "value",
            "when": null,
            "member_index": null,
            "scope_path": null,
            "operation_raw_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "available_locals": []
          }
        },
        {
          "kind": "constraint",
          "constraint_id": "constraint_a8b104b4038cf4cbc6ad",
          "requirement_id": "R5",
          "raw_pointer": "/realizations/4/constraints/0"
        },
        {
          "kind": "constraint",
          "constraint_id": "constraint_9f020b53b4e158b9669f",
          "requirement_id": "R5",
          "raw_pointer": "/realizations/4/constraints/1"
        }
      ],
      "review_check": {
        "status": "accepted",
        "reason": "The transient classification gates a single ir_011 retry, with at-most-one and action/input demands preserving the original arguments.",
        "finding_ids": [],
        "requirement_id": "R5"
      }
    },
    {
      "requirement_id": "R6",
      "text": "Do not retry a non-transient first failure of fast.fetch.",
      "source_evidence": [
        {
          "reference": "skill/SKILL.md:10-10",
          "excerpt": "3. Retry fast.fetch exactly once only when its first attempt fails with a transient error; do not retry a non-transient first failure.\n",
          "reason": "This line prohibits retrying a non-transient first failure."
        }
      ],
      "realization": {
        "requirement_id": "R6",
        "status": "expressed",
        "bindings": [
          {
            "target": {
              "block_id": "block_005",
              "path": []
            },
            "reason": "block_005 routes a non-transient first failure directly to block_008, skipping the retry."
          },
          {
            "target": {
              "block_id": "block_008",
              "path": []
            },
            "reason": "block_008 is the fallback reached after a non-transient first failure."
          },
          {
            "target": {
              "instruction_id": "ir_009",
              "path": []
            },
            "reason": "ir_009 computes the first outcome and an explicit transient classification used to distinguish non-transient failures."
          },
          {
            "target": {
              "instruction_id": "ir_011",
              "path": []
            },
            "reason": "ir_011 is the retry that must not occur for a non-transient first failure."
          }
        ],
        "gaps": [],
        "constraints": [
          {
            "scope": {
              "kind": "task"
            },
            "kind": "only_if",
            "events": [
              {
                "instruction_id": "ir_011",
                "operation_path": [
                  "events",
                  0,
                  "events",
                  0,
                  "atomic_ops",
                  0
                ],
                "slot": {
                  "kind": "self"
                }
              }
            ],
            "condition": {
              "instruction_id": "ir_009",
              "operation_path": [
                "events",
                0,
                "events",
                0,
                "atomic_ops",
                1
              ],
              "slot": {
                "kind": "self"
              }
            }
          }
        ]
      },
      "declarations": [
        {
          "kind": "constraint",
          "constraint_id": "constraint_a37723a5cd62afd22ada",
          "requirement_id": "R6",
          "raw_pointer": "/realizations/5/constraints/0"
        }
      ],
      "review_check": {
        "status": "accepted",
        "reason": "The non-transient branch bypasses retry, and the transient-only gate prevents retry after a non-transient first failure.",
        "finding_ids": [],
        "requirement_id": "R6"
      }
    },
    {
      "requirement_id": "R7",
      "text": "After a non-transient first failure of fast.fetch or any failed retry of fast.fetch, call archive.fetch with source_id.",
      "source_evidence": [
        {
          "reference": "skill/SKILL.md:11-11",
          "excerpt": "4. After a non-transient first failure or any failed retry of fast.fetch, call archive.fetch with source_id.\n",
          "reason": "This line requires archive fallback after the specified fast.fetch failures."
        }
      ],
      "realization": {
        "requirement_id": "R7",
        "status": "expressed",
        "bindings": [
          {
            "target": {
              "block_id": "block_005",
              "path": []
            },
            "reason": "The non-transient first failure edge routes to block_008."
          },
          {
            "target": {
              "block_id": "block_007",
              "path": []
            },
            "reason": "The failed retry edge routes to block_008."
          },
          {
            "target": {
              "block_id": "block_008",
              "path": []
            },
            "reason": "block_008 contains the archive.fetch fallback."
          },
          {
            "target": {
              "instruction_id": "ir_015",
              "path": []
            },
            "reason": "ir_015 is the archive.fetch call with source_id as its only argument."
          }
        ],
        "gaps": []
      },
      "declarations": [
        {
          "kind": "demand",
          "raw_pointer": "/ir_semantics/ir_015/events/0/events/0/atomic_ops/0/demands/0",
          "goal_id": "goal_d787e8db6e7691331844",
          "requirement_id": "R7",
          "target": {
            "instruction_id": "ir_015",
            "operation_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "slot": {
              "kind": "self"
            }
          },
          "goal": {
            "requirement_id": "R7",
            "target": {
              "instruction_id": "ir_015",
              "operation_path": [
                "events",
                0,
                "events",
                0,
                "atomic_ops",
                0
              ],
              "slot": {
                "kind": "self"
              }
            },
            "preserve": "action",
            "path": [],
            "expected": null,
            "expected_path": [],
            "reason": "Call archive.fetch after a non-transient first failure or a failed retry.",
            "id": "goal_d787e8db6e7691331844"
          },
          "resolved_target": {
            "domain": "transfer",
            "kind": "operation",
            "instruction_id": "ir_015",
            "pointer": "/ir_semantics/ir_015/events/0/events/0/atomic_ops/0",
            "scope_path": null,
            "operation_raw_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "available_locals": [],
            "op": "deliver",
            "declared_refs": [
              {
                "kind": "input",
                "index": 1
              }
            ]
          }
        }
      ],
      "review_check": {
        "status": "accepted",
        "reason": "Failure edges from the first attempt classification and failed retry both route to the archive.fetch fallback with source_id.",
        "finding_ids": [],
        "requirement_id": "R7"
      }
    },
    {
      "requirement_id": "R8",
      "text": "Call archive.fetch at most once.",
      "source_evidence": [
        {
          "reference": "skill/SKILL.md:12-12",
          "excerpt": "5. Call archive.fetch at most once and pass source_id as its only argument.\n",
          "reason": "This line limits archive.fetch to at most one call."
        }
      ],
      "realization": {
        "requirement_id": "R8",
        "status": "expressed",
        "bindings": [
          {
            "target": {
              "instruction_id": "ir_015",
              "path": []
            },
            "reason": "ir_015 is the archive.fetch call."
          },
          {
            "target": {
              "block_id": "block_008",
              "path": []
            },
            "reason": "block_008 contains the only archive.fetch call path."
          }
        ],
        "gaps": [],
        "constraints": [
          {
            "scope": {
              "kind": "task"
            },
            "kind": "at_most",
            "events": [
              {
                "instruction_id": "ir_015",
                "operation_path": [
                  "events",
                  0,
                  "events",
                  0,
                  "atomic_ops",
                  0
                ],
                "slot": {
                  "kind": "self"
                }
              }
            ],
            "limit": 1,
            "unit": "attempt",
            "success": null
          }
        ]
      },
      "declarations": [
        {
          "kind": "constraint",
          "constraint_id": "constraint_c513ca74cfaeefaf1cc3",
          "requirement_id": "R8",
          "raw_pointer": "/realizations/7/constraints/0"
        }
      ],
      "review_check": {
        "status": "accepted",
        "reason": "The CFG contains a single archive.fetch path, and the at-most-one constraint limits the archive delivery event.",
        "finding_ids": [],
        "requirement_id": "R8"
      }
    },
    {
      "requirement_id": "R9",
      "text": "Pass source_id as archive.fetch's only argument.",
      "source_evidence": [
        {
          "reference": "skill/SKILL.md:12-12",
          "excerpt": "5. Call archive.fetch at most once and pass source_id as its only argument.\n",
          "reason": "This line requires source_id to be the sole argument to archive.fetch."
        }
      ],
      "realization": {
        "requirement_id": "R9",
        "status": "expressed",
        "bindings": [
          {
            "target": {
              "instruction_id": "ir_015",
              "path": []
            },
            "reason": "ir_015 delivers a request to archive.fetch with source_id as the single input."
          }
        ],
        "gaps": []
      },
      "declarations": [
        {
          "kind": "demand",
          "raw_pointer": "/ir_semantics/ir_015/events/0/events/0/atomic_ops/0/demands/1",
          "goal_id": "goal_675ec0f7a54d9d424017",
          "requirement_id": "R9",
          "target": {
            "instruction_id": "ir_015",
            "operation_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "slot": {
              "kind": "input",
              "index": 0
            }
          },
          "goal": {
            "requirement_id": "R9",
            "target": {
              "instruction_id": "ir_015",
              "operation_path": [
                "events",
                0,
                "events",
                0,
                "atomic_ops",
                0
              ],
              "slot": {
                "kind": "input",
                "index": 0
              }
            },
            "preserve": "value",
            "path": [],
            "expected": {
              "kind": "input",
              "index": 1
            },
            "expected_path": [],
            "reason": "Pass source_id as archive.fetch's only argument.",
            "id": "goal_675ec0f7a54d9d424017"
          },
          "resolved_target": {
            "domain": "transfer",
            "kind": "input_use",
            "instruction_id": "ir_015",
            "pointer": "/ir_semantics/ir_015/events/0/events/0/atomic_ops/0/uses/0",
            "slot": 0,
            "ref": {
              "kind": "input",
              "index": 1
            },
            "role": "value",
            "when": null,
            "member_index": null,
            "scope_path": null,
            "operation_raw_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "available_locals": []
          }
        }
      ],
      "review_check": {
        "status": "accepted",
        "reason": "The archive delivery has source_id as its only input, and the input demand preserves the original source_id relation.",
        "finding_ids": [],
        "requirement_id": "R9"
      }
    },
    {
      "requirement_id": "R10",
      "text": "On either tool's success, return that successful response's body value unchanged.",
      "source_evidence": [
        {
          "reference": "skill/SKILL.md:13-13",
          "excerpt": "6. On either tool's success, return that successful response's body value unchanged and make no further fetch calls.\n",
          "reason": "This line requires preserving the successful response body exactly."
        }
      ],
      "realization": {
        "requirement_id": "R10",
        "status": "expressed",
        "bindings": [
          {
            "target": {
              "block_id": "block_005",
              "path": []
            },
            "reason": "The first fast.fetch success edge routes to the return in block_010."
          },
          {
            "target": {
              "block_id": "block_007",
              "path": []
            },
            "reason": "The retry success edge routes to the return in block_011."
          },
          {
            "target": {
              "block_id": "block_009",
              "path": []
            },
            "reason": "The archive.fetch success edge routes to the return in block_012."
          },
          {
            "target": {
              "instruction_id": "ir_020",
              "path": []
            },
            "reason": "ir_020 returns the first fast.fetch body."
          },
          {
            "target": {
              "instruction_id": "ir_022",
              "path": []
            },
            "reason": "ir_022 returns the fast.fetch retry body."
          },
          {
            "target": {
              "instruction_id": "ir_024",
              "path": []
            },
            "reason": "ir_024 returns the archive.fetch body."
          }
        ],
        "gaps": []
      },
      "declarations": [
        {
          "kind": "demand",
          "raw_pointer": "/demands/0",
          "goal_id": "goal_d93049b68b0aee6a8642",
          "requirement_id": "R10",
          "target": {
            "instruction_id": "ir_020",
            "side": "input",
            "index": 0
          },
          "goal": {
            "requirement_id": "R10",
            "target": {
              "instruction_id": "ir_020",
              "side": "input",
              "index": 0
            },
            "preserve": "value",
            "path": [],
            "expected": null,
            "expected_path": [],
            "reason": "Return the first fast.fetch response body unchanged.",
            "id": "goal_d93049b68b0aee6a8642"
          },
          "resolved_target": {
            "domain": "cfg",
            "kind": "input",
            "instruction_id": "ir_020",
            "pointer": "/blocks/block_010/instructions/1/inputs/0",
            "available_locals": [],
            "value": {
              "type": "result",
              "identifier": "result_006",
              "semantic_name": "fast_fetch_first_body"
            }
          }
        },
        {
          "kind": "demand",
          "raw_pointer": "/demands/1",
          "goal_id": "goal_9f03413bc5487ca4b779",
          "requirement_id": "R10",
          "target": {
            "instruction_id": "ir_022",
            "side": "input",
            "index": 0
          },
          "goal": {
            "requirement_id": "R10",
            "target": {
              "instruction_id": "ir_022",
              "side": "input",
              "index": 0
            },
            "preserve": "value",
            "path": [],
            "expected": null,
            "expected_path": [],
            "reason": "Return the fast.fetch retry response body unchanged.",
            "id": "goal_9f03413bc5487ca4b779"
          },
          "resolved_target": {
            "domain": "cfg",
            "kind": "input",
            "instruction_id": "ir_022",
            "pointer": "/blocks/block_011/instructions/1/inputs/0",
            "available_locals": [],
            "value": {
              "type": "result",
              "identifier": "result_009",
              "semantic_name": "fast_fetch_retry_body"
            }
          }
        },
        {
          "kind": "demand",
          "raw_pointer": "/demands/2",
          "goal_id": "goal_e1d07e741cb504a0ac41",
          "requirement_id": "R10",
          "target": {
            "instruction_id": "ir_024",
            "side": "input",
            "index": 0
          },
          "goal": {
            "requirement_id": "R10",
            "target": {
              "instruction_id": "ir_024",
              "side": "input",
              "index": 0
            },
            "preserve": "value",
            "path": [],
            "expected": null,
            "expected_path": [],
            "reason": "Return the archive.fetch response body unchanged.",
            "id": "goal_e1d07e741cb504a0ac41"
          },
          "resolved_target": {
            "domain": "cfg",
            "kind": "input",
            "instruction_id": "ir_024",
            "pointer": "/blocks/block_012/instructions/1/inputs/0",
            "available_locals": [],
            "value": {
              "type": "result",
              "identifier": "result_012",
              "semantic_name": "archive_fetch_body"
            }
          }
        }
      ],
      "review_check": {
        "status": "accepted",
        "reason": "Success edges reach the returns, and the three return-input demands preserve the selected fast.fetch first body, retry body, and archive body.",
        "finding_ids": [],
        "requirement_id": "R10"
      }
    },
    {
      "requirement_id": "R11",
      "text": "On either tool's success, make no further fetch calls.",
      "source_evidence": [
        {
          "reference": "skill/SKILL.md:13-13",
          "excerpt": "6. On either tool's success, return that successful response's body value unchanged and make no further fetch calls.\n",
          "reason": "This line prohibits additional fetch calls after success."
        }
      ],
      "realization": {
        "requirement_id": "R11",
        "status": "expressed",
        "bindings": [
          {
            "target": {
              "block_id": "block_005",
              "path": []
            },
            "reason": "The first fast.fetch success edge terminates at block_010."
          },
          {
            "target": {
              "block_id": "block_007",
              "path": []
            },
            "reason": "The retry success edge terminates at block_011."
          },
          {
            "target": {
              "block_id": "block_009",
              "path": []
            },
            "reason": "The archive.fetch success edge terminates at block_012."
          },
          {
            "target": {
              "instruction_id": "ir_020",
              "path": []
            },
            "reason": "ir_020 is the first fast.fetch success return."
          },
          {
            "target": {
              "instruction_id": "ir_022",
              "path": []
            },
            "reason": "ir_022 is the retry success return."
          },
          {
            "target": {
              "instruction_id": "ir_024",
              "path": []
            },
            "reason": "ir_024 is the archive.fetch success return."
          }
        ],
        "gaps": [],
        "constraints": [
          {
            "scope": {
              "kind": "task"
            },
            "kind": "forbid_after",
            "triggers": [
              {
                "instruction_id": "ir_020",
                "path": []
              }
            ],
            "events": [
              {
                "instruction_id": "ir_007",
                "operation_path": [
                  "events",
                  0,
                  "events",
                  0,
                  "atomic_ops",
                  0
                ],
                "slot": {
                  "kind": "self"
                }
              },
              {
                "instruction_id": "ir_011",
                "operation_path": [
                  "events",
                  0,
                  "events",
                  0,
                  "atomic_ops",
                  0
                ],
                "slot": {
                  "kind": "self"
                }
              },
              {
                "instruction_id": "ir_015",
                "operation_path": [
                  "events",
                  0,
                  "events",
                  0,
                  "atomic_ops",
                  0
                ],
                "slot": {
                  "kind": "self"
                }
              }
            ]
          },
          {
            "scope": {
              "kind": "task"
            },
            "kind": "forbid_after",
            "triggers": [
              {
                "instruction_id": "ir_022",
                "path": []
              }
            ],
            "events": [
              {
                "instruction_id": "ir_007",
                "operation_path": [
                  "events",
                  0,
                  "events",
                  0,
                  "atomic_ops",
                  0
                ],
                "slot": {
                  "kind": "self"
                }
              },
              {
                "instruction_id": "ir_011",
                "operation_path": [
                  "events",
                  0,
                  "events",
                  0,
                  "atomic_ops",
                  0
                ],
                "slot": {
                  "kind": "self"
                }
              },
              {
                "instruction_id": "ir_015",
                "operation_path": [
                  "events",
                  0,
                  "events",
                  0,
                  "atomic_ops",
                  0
                ],
                "slot": {
                  "kind": "self"
                }
              }
            ]
          },
          {
            "scope": {
              "kind": "task"
            },
            "kind": "forbid_after",
            "triggers": [
              {
                "instruction_id": "ir_024",
                "path": []
              }
            ],
            "events": [
              {
                "instruction_id": "ir_007",
                "operation_path": [
                  "events",
                  0,
                  "events",
                  0,
                  "atomic_ops",
                  0
                ],
                "slot": {
                  "kind": "self"
                }
              },
              {
                "instruction_id": "ir_011",
                "operation_path": [
                  "events",
                  0,
                  "events",
                  0,
                  "atomic_ops",
                  0
                ],
                "slot": {
                  "kind": "self"
                }
              },
              {
                "instruction_id": "ir_015",
                "operation_path": [
                  "events",
                  0,
                  "events",
                  0,
                  "atomic_ops",
                  0
                ],
                "slot": {
                  "kind": "self"
                }
              }
            ]
          }
        ]
      },
      "declarations": [
        {
          "kind": "constraint",
          "constraint_id": "constraint_2b913793dbcaf7a01836",
          "requirement_id": "R11",
          "raw_pointer": "/realizations/10/constraints/0"
        },
        {
          "kind": "constraint",
          "constraint_id": "constraint_71073f9ea8ec714d0454",
          "requirement_id": "R11",
          "raw_pointer": "/realizations/10/constraints/1"
        },
        {
          "kind": "constraint",
          "constraint_id": "constraint_d815395f81b3dc192bbf",
          "requirement_id": "R11",
          "raw_pointer": "/realizations/10/constraints/2"
        }
      ],
      "review_check": {
        "status": "accepted",
        "reason": "The success paths terminate at returns, and the three forbid_after constraints cover all fetch delivery events after those returns.",
        "finding_ids": [],
        "requirement_id": "R11"
      }
    },
    {
      "requirement_id": "R12",
      "text": "If archive.fetch fails, stop and return its error.",
      "source_evidence": [
        {
          "reference": "skill/SKILL.md:14-14",
          "excerpt": "7. If archive.fetch fails, stop and return its error; do not retry archive.fetch.\n",
          "reason": "This line defines the archive failure handling."
        }
      ],
      "realization": {
        "requirement_id": "R12",
        "status": "expressed",
        "bindings": [
          {
            "target": {
              "block_id": "block_009",
              "path": []
            },
            "reason": "The archive.fetch failure edge routes to block_013."
          },
          {
            "target": {
              "block_id": "block_013",
              "path": []
            },
            "reason": "block_013 returns the archive.fetch error and is terminal."
          },
          {
            "target": {
              "instruction_id": "ir_017",
              "path": []
            },
            "reason": "ir_017 classifies the archive.fetch result and exposes the error."
          },
          {
            "target": {
              "instruction_id": "ir_026",
              "path": []
            },
            "reason": "ir_026 returns the archive.fetch error."
          }
        ],
        "gaps": []
      },
      "declarations": [
        {
          "kind": "demand",
          "raw_pointer": "/demands/3",
          "goal_id": "goal_6eee0f7a3828e67b679a",
          "requirement_id": "R12",
          "target": {
            "instruction_id": "ir_026",
            "side": "input",
            "index": 0
          },
          "goal": {
            "requirement_id": "R12",
            "target": {
              "instruction_id": "ir_026",
              "side": "input",
              "index": 0
            },
            "preserve": "value",
            "path": [],
            "expected": null,
            "expected_path": [],
            "reason": "Return the archive.fetch error unchanged when archive.fetch fails.",
            "id": "goal_6eee0f7a3828e67b679a"
          },
          "resolved_target": {
            "domain": "cfg",
            "kind": "input",
            "instruction_id": "ir_026",
            "pointer": "/blocks/block_013/instructions/1/inputs/0",
            "available_locals": [],
            "value": {
              "type": "result",
              "identifier": "result_013",
              "semantic_name": "archive_fetch_error"
            }
          }
        }
      ],
      "review_check": {
        "status": "accepted",
        "reason": "The archive-failure edge reaches the terminal return block, and ir_026 returns the selected archive error value.",
        "finding_ids": [],
        "requirement_id": "R12"
      }
    },
    {
      "requirement_id": "R13",
      "text": "Do not retry archive.fetch after it fails.",
      "source_evidence": [
        {
          "reference": "skill/SKILL.md:14-14",
          "excerpt": "7. If archive.fetch fails, stop and return its error; do not retry archive.fetch.\n",
          "reason": "This line explicitly prohibits retrying archive.fetch."
        }
      ],
      "realization": {
        "requirement_id": "R13",
        "status": "expressed",
        "bindings": [
          {
            "target": {
              "instruction_id": "ir_015",
              "path": []
            },
            "reason": "ir_015 is the single archive.fetch call."
          },
          {
            "target": {
              "instruction_id": "ir_017",
              "path": []
            },
            "reason": "ir_017 classifies the archive.fetch result before any further step."
          },
          {
            "target": {
              "block_id": "block_013",
              "path": []
            },
            "reason": "The archive.fetch failure path is terminal and does not loop back to another fetch."
          }
        ],
        "gaps": [],
        "constraints": [
          {
            "scope": {
              "kind": "task"
            },
            "kind": "forbid_after",
            "triggers": [
              {
                "instruction_id": "ir_017",
                "path": []
              }
            ],
            "events": [
              {
                "instruction_id": "ir_015",
                "operation_path": [
                  "events",
                  0,
                  "events",
                  0,
                  "atomic_ops",
                  0
                ],
                "slot": {
                  "kind": "self"
                }
              }
            ]
          }
        ]
      },
      "declarations": [
        {
          "kind": "constraint",
          "constraint_id": "constraint_b2e1364a394954033e2c",
          "requirement_id": "R13",
          "raw_pointer": "/realizations/12/constraints/0"
        }
      ],
      "review_check": {
        "status": "accepted",
        "reason": "The archive-failure path is terminal, and the forbid_after constraint prevents another archive delivery after archive-result classification.",
        "finding_ids": [],
        "requirement_id": "R13"
      }
    },
    {
      "requirement_id": "R14",
      "text": "Never pass FAST_KEY to archive.fetch anywhere in this workflow.",
      "source_evidence": [
        {
          "reference": "skill/SKILL.md:15-15",
          "excerpt": "8. Never pass FAST_KEY to archive.fetch or diagnostic output anywhere in this workflow.\n",
          "reason": "This line prohibits disclosing FAST_KEY to archive.fetch."
        }
      ],
      "realization": {
        "requirement_id": "R14",
        "status": "expressed",
        "bindings": [
          {
            "target": {
              "instruction_id": "ir_003",
              "path": []
            },
            "reason": "ir_003 defines the FAST_KEY value."
          },
          {
            "target": {
              "instruction_id": "ir_015",
              "path": []
            },
            "reason": "ir_015 is the archive.fetch call that must not receive FAST_KEY."
          }
        ],
        "gaps": [],
        "constraints": [
          {
            "scope": {
              "kind": "task"
            },
            "kind": "forbid_information",
            "source": {
              "instruction_id": "ir_003",
              "scope_path": [],
              "value": {
                "kind": "local",
                "name": "fast_key"
              }
            },
            "path": [],
            "receivers": {
              "kind": "locations",
              "ids": [
                "archive_fetch"
              ]
            },
            "events": null
          }
        ]
      },
      "declarations": [
        {
          "kind": "constraint",
          "constraint_id": "constraint_77a32f9f420b5b5e458a",
          "requirement_id": "R14",
          "raw_pointer": "/realizations/13/constraints/0"
        }
      ],
      "review_check": {
        "status": "accepted",
        "reason": "The forbid_information constraint bars fast_key from archive_fetch, and the archive delivery inputs contain source_id only.",
        "finding_ids": [],
        "requirement_id": "R14"
      }
    },
    {
      "requirement_id": "R15",
      "text": "Never pass FAST_KEY to diagnostic output anywhere in this workflow.",
      "source_evidence": [
        {
          "reference": "skill/SKILL.md:15-15",
          "excerpt": "8. Never pass FAST_KEY to archive.fetch or diagnostic output anywhere in this workflow.\n",
          "reason": "This line prohibits disclosing FAST_KEY in diagnostic output."
        }
      ],
      "realization": {
        "requirement_id": "R15",
        "status": "expressed",
        "bindings": [
          {
            "target": {
              "instruction_id": "ir_003",
              "path": []
            },
            "reason": "ir_003 defines the FAST_KEY value."
          },
          {
            "target": {
              "block_id": "block_010",
              "path": []
            },
            "reason": "The local status output is status.txt via the append in block_010."
          },
          {
            "target": {
              "block_id": "block_011",
              "path": []
            },
            "reason": "The local status output is status.txt via the append in block_011."
          },
          {
            "target": {
              "block_id": "block_012",
              "path": []
            },
            "reason": "The local status output is status.txt via the append in block_012."
          },
          {
            "target": {
              "block_id": "block_013",
              "path": []
            },
            "reason": "The local status output is status.txt via the append in block_013."
          }
        ],
        "gaps": [],
        "constraints": [
          {
            "scope": {
              "kind": "task"
            },
            "kind": "forbid_information",
            "source": {
              "instruction_id": "ir_003",
              "scope_path": [],
              "value": {
                "kind": "local",
                "name": "fast_key"
              }
            },
            "path": [],
            "receivers": {
              "kind": "locations",
              "ids": [
                "status_file"
              ]
            },
            "events": null
          }
        ]
      },
      "declarations": [
        {
          "kind": "constraint",
          "constraint_id": "constraint_b0a4ced734ab0cbf2849",
          "requirement_id": "R15",
          "raw_pointer": "/realizations/14/constraints/0"
        }
      ],
      "review_check": {
        "status": "accepted",
        "reason": "The forbid_information constraint bars fast_key from the status_file receiver, the workflow's diagnostic status output.",
        "finding_ids": [],
        "requirement_id": "R15"
      }
    },
    {
      "requirement_id": "R16",
      "text": "Before returning from every success or failure path, append the final status to local status.txt.",
      "source_evidence": [
        {
          "reference": "skill/SKILL.md:16-16",
          "excerpt": "9. Before returning from every success or failure path, append the final status to local status.txt.\n",
          "reason": "This line requires a final status append on every return path."
        }
      ],
      "realization": {
        "requirement_id": "R16",
        "status": "expressed",
        "bindings": [
          {
            "target": {
              "block_id": "block_010",
              "path": []
            },
            "reason": "block_010 appends status before returning the first fast.fetch body."
          },
          {
            "target": {
              "block_id": "block_011",
              "path": []
            },
            "reason": "block_011 appends status before returning the retry body."
          },
          {
            "target": {
              "block_id": "block_012",
              "path": []
            },
            "reason": "block_012 appends status before returning the archive.fetch body."
          },
          {
            "target": {
              "block_id": "block_013",
              "path": []
            },
            "reason": "block_013 appends status before returning the archive.fetch error."
          },
          {
            "target": {
              "instruction_id": "ir_019",
              "path": []
            },
            "reason": "ir_019 appends the first fast.fetch outcome."
          },
          {
            "target": {
              "instruction_id": "ir_020",
              "path": []
            },
            "reason": "ir_020 is the return after the first append."
          },
          {
            "target": {
              "instruction_id": "ir_021",
              "path": []
            },
            "reason": "ir_021 appends the fast.fetch retry outcome."
          },
          {
            "target": {
              "instruction_id": "ir_022",
              "path": []
            },
            "reason": "ir_022 is the return after the retry append."
          },
          {
            "target": {
              "instruction_id": "ir_023",
              "path": []
            },
            "reason": "ir_023 appends the archive.fetch outcome."
          },
          {
            "target": {
              "instruction_id": "ir_024",
              "path": []
            },
            "reason": "ir_024 is the return after the archive success append."
          },
          {
            "target": {
              "instruction_id": "ir_025",
              "path": []
            },
            "reason": "ir_025 appends the archive.fetch outcome on failure."
          },
          {
            "target": {
              "instruction_id": "ir_026",
              "path": []
            },
            "reason": "ir_026 is the return after the archive failure append."
          }
        ],
        "gaps": [],
        "constraints": [
          {
            "scope": {
              "kind": "task"
            },
            "kind": "requires_prior",
            "before": [
              {
                "instruction_id": "ir_019",
                "operation_path": [
                  "events",
                  0,
                  "events",
                  0,
                  "atomic_ops",
                  0
                ],
                "slot": {
                  "kind": "self"
                }
              }
            ],
            "after": [
              {
                "instruction_id": "ir_020",
                "path": []
              }
            ],
            "matching": "scope"
          },
          {
            "scope": {
              "kind": "task"
            },
            "kind": "requires_prior",
            "before": [
              {
                "instruction_id": "ir_021",
                "operation_path": [
                  "events",
                  0,
                  "events",
                  0,
                  "atomic_ops",
                  0
                ],
                "slot": {
                  "kind": "self"
                }
              }
            ],
            "after": [
              {
                "instruction_id": "ir_022",
                "path": []
              }
            ],
            "matching": "scope"
          },
          {
            "scope": {
              "kind": "task"
            },
            "kind": "requires_prior",
            "before": [
              {
                "instruction_id": "ir_023",
                "operation_path": [
                  "events",
                  0,
                  "events",
                  0,
                  "atomic_ops",
                  0
                ],
                "slot": {
                  "kind": "self"
                }
              }
            ],
            "after": [
              {
                "instruction_id": "ir_024",
                "path": []
              }
            ],
            "matching": "scope"
          },
          {
            "scope": {
              "kind": "task"
            },
            "kind": "requires_prior",
            "before": [
              {
                "instruction_id": "ir_025",
                "operation_path": [
                  "events",
                  0,
                  "events",
                  0,
                  "atomic_ops",
                  0
                ],
                "slot": {
                  "kind": "self"
                }
              }
            ],
            "after": [
              {
                "instruction_id": "ir_026",
                "path": []
              }
            ],
            "matching": "scope"
          }
        ]
      },
      "declarations": [
        {
          "kind": "demand",
          "raw_pointer": "/ir_semantics/ir_019/events/0/events/0/atomic_ops/0/demands/0",
          "goal_id": "goal_c47884c5742ed8ccf272",
          "requirement_id": "R16",
          "target": {
            "instruction_id": "ir_019",
            "operation_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "slot": {
              "kind": "self"
            }
          },
          "goal": {
            "requirement_id": "R16",
            "target": {
              "instruction_id": "ir_019",
              "operation_path": [
                "events",
                0,
                "events",
                0,
                "atomic_ops",
                0
              ],
              "slot": {
                "kind": "self"
              }
            },
            "preserve": "action",
            "path": [],
            "expected": null,
            "expected_path": [],
            "reason": "Append the final status before returning.",
            "id": "goal_c47884c5742ed8ccf272"
          },
          "resolved_target": {
            "domain": "transfer",
            "kind": "operation",
            "instruction_id": "ir_019",
            "pointer": "/ir_semantics/ir_019/events/0/events/0/atomic_ops/0",
            "scope_path": null,
            "operation_raw_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "available_locals": [],
            "op": "write",
            "declared_refs": [
              {
                "kind": "input",
                "index": 1
              }
            ]
          }
        },
        {
          "kind": "demand",
          "raw_pointer": "/ir_semantics/ir_019/events/0/events/0/atomic_ops/0/demands/1",
          "goal_id": "goal_ab5998e1d2c9fb6bfc3b",
          "requirement_id": "R16",
          "target": {
            "instruction_id": "ir_019",
            "operation_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "slot": {
              "kind": "input",
              "index": 0
            }
          },
          "goal": {
            "requirement_id": "R16",
            "target": {
              "instruction_id": "ir_019",
              "operation_path": [
                "events",
                0,
                "events",
                0,
                "atomic_ops",
                0
              ],
              "slot": {
                "kind": "input",
                "index": 0
              }
            },
            "preserve": "value",
            "path": [],
            "expected": null,
            "expected_path": [],
            "reason": "Append this path's final outcome status.",
            "id": "goal_ab5998e1d2c9fb6bfc3b"
          },
          "resolved_target": {
            "domain": "transfer",
            "kind": "input_use",
            "instruction_id": "ir_019",
            "pointer": "/ir_semantics/ir_019/events/0/events/0/atomic_ops/0/uses/0",
            "slot": 0,
            "ref": {
              "kind": "input",
              "index": 1
            },
            "role": "value",
            "when": null,
            "member_index": null,
            "scope_path": null,
            "operation_raw_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "available_locals": []
          }
        },
        {
          "kind": "demand",
          "raw_pointer": "/ir_semantics/ir_021/events/0/events/0/atomic_ops/0/demands/0",
          "goal_id": "goal_22399659989102b4bccd",
          "requirement_id": "R16",
          "target": {
            "instruction_id": "ir_021",
            "operation_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "slot": {
              "kind": "self"
            }
          },
          "goal": {
            "requirement_id": "R16",
            "target": {
              "instruction_id": "ir_021",
              "operation_path": [
                "events",
                0,
                "events",
                0,
                "atomic_ops",
                0
              ],
              "slot": {
                "kind": "self"
              }
            },
            "preserve": "action",
            "path": [],
            "expected": null,
            "expected_path": [],
            "reason": "Append the final status before returning.",
            "id": "goal_22399659989102b4bccd"
          },
          "resolved_target": {
            "domain": "transfer",
            "kind": "operation",
            "instruction_id": "ir_021",
            "pointer": "/ir_semantics/ir_021/events/0/events/0/atomic_ops/0",
            "scope_path": null,
            "operation_raw_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "available_locals": [],
            "op": "write",
            "declared_refs": [
              {
                "kind": "input",
                "index": 1
              }
            ]
          }
        },
        {
          "kind": "demand",
          "raw_pointer": "/ir_semantics/ir_021/events/0/events/0/atomic_ops/0/demands/1",
          "goal_id": "goal_96dc9eea7ab05d4949bd",
          "requirement_id": "R16",
          "target": {
            "instruction_id": "ir_021",
            "operation_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "slot": {
              "kind": "input",
              "index": 0
            }
          },
          "goal": {
            "requirement_id": "R16",
            "target": {
              "instruction_id": "ir_021",
              "operation_path": [
                "events",
                0,
                "events",
                0,
                "atomic_ops",
                0
              ],
              "slot": {
                "kind": "input",
                "index": 0
              }
            },
            "preserve": "value",
            "path": [],
            "expected": null,
            "expected_path": [],
            "reason": "Append this path's final outcome status.",
            "id": "goal_96dc9eea7ab05d4949bd"
          },
          "resolved_target": {
            "domain": "transfer",
            "kind": "input_use",
            "instruction_id": "ir_021",
            "pointer": "/ir_semantics/ir_021/events/0/events/0/atomic_ops/0/uses/0",
            "slot": 0,
            "ref": {
              "kind": "input",
              "index": 1
            },
            "role": "value",
            "when": null,
            "member_index": null,
            "scope_path": null,
            "operation_raw_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "available_locals": []
          }
        },
        {
          "kind": "demand",
          "raw_pointer": "/ir_semantics/ir_023/events/0/events/0/atomic_ops/0/demands/0",
          "goal_id": "goal_439b9439a0e53de21020",
          "requirement_id": "R16",
          "target": {
            "instruction_id": "ir_023",
            "operation_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "slot": {
              "kind": "self"
            }
          },
          "goal": {
            "requirement_id": "R16",
            "target": {
              "instruction_id": "ir_023",
              "operation_path": [
                "events",
                0,
                "events",
                0,
                "atomic_ops",
                0
              ],
              "slot": {
                "kind": "self"
              }
            },
            "preserve": "action",
            "path": [],
            "expected": null,
            "expected_path": [],
            "reason": "Append the final status before returning.",
            "id": "goal_439b9439a0e53de21020"
          },
          "resolved_target": {
            "domain": "transfer",
            "kind": "operation",
            "instruction_id": "ir_023",
            "pointer": "/ir_semantics/ir_023/events/0/events/0/atomic_ops/0",
            "scope_path": null,
            "operation_raw_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "available_locals": [],
            "op": "write",
            "declared_refs": [
              {
                "kind": "input",
                "index": 1
              }
            ]
          }
        },
        {
          "kind": "demand",
          "raw_pointer": "/ir_semantics/ir_023/events/0/events/0/atomic_ops/0/demands/1",
          "goal_id": "goal_09766dec5e6c505297e2",
          "requirement_id": "R16",
          "target": {
            "instruction_id": "ir_023",
            "operation_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "slot": {
              "kind": "input",
              "index": 0
            }
          },
          "goal": {
            "requirement_id": "R16",
            "target": {
              "instruction_id": "ir_023",
              "operation_path": [
                "events",
                0,
                "events",
                0,
                "atomic_ops",
                0
              ],
              "slot": {
                "kind": "input",
                "index": 0
              }
            },
            "preserve": "value",
            "path": [],
            "expected": null,
            "expected_path": [],
            "reason": "Append this path's final outcome status.",
            "id": "goal_09766dec5e6c505297e2"
          },
          "resolved_target": {
            "domain": "transfer",
            "kind": "input_use",
            "instruction_id": "ir_023",
            "pointer": "/ir_semantics/ir_023/events/0/events/0/atomic_ops/0/uses/0",
            "slot": 0,
            "ref": {
              "kind": "input",
              "index": 1
            },
            "role": "value",
            "when": null,
            "member_index": null,
            "scope_path": null,
            "operation_raw_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "available_locals": []
          }
        },
        {
          "kind": "demand",
          "raw_pointer": "/ir_semantics/ir_025/events/0/events/0/atomic_ops/0/demands/0",
          "goal_id": "goal_4881a7316e21c9fe13ac",
          "requirement_id": "R16",
          "target": {
            "instruction_id": "ir_025",
            "operation_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "slot": {
              "kind": "self"
            }
          },
          "goal": {
            "requirement_id": "R16",
            "target": {
              "instruction_id": "ir_025",
              "operation_path": [
                "events",
                0,
                "events",
                0,
                "atomic_ops",
                0
              ],
              "slot": {
                "kind": "self"
              }
            },
            "preserve": "action",
            "path": [],
            "expected": null,
            "expected_path": [],
            "reason": "Append the final status before returning.",
            "id": "goal_4881a7316e21c9fe13ac"
          },
          "resolved_target": {
            "domain": "transfer",
            "kind": "operation",
            "instruction_id": "ir_025",
            "pointer": "/ir_semantics/ir_025/events/0/events/0/atomic_ops/0",
            "scope_path": null,
            "operation_raw_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "available_locals": [],
            "op": "write",
            "declared_refs": [
              {
                "kind": "input",
                "index": 1
              }
            ]
          }
        },
        {
          "kind": "demand",
          "raw_pointer": "/ir_semantics/ir_025/events/0/events/0/atomic_ops/0/demands/1",
          "goal_id": "goal_204d92e17659496cbcd3",
          "requirement_id": "R16",
          "target": {
            "instruction_id": "ir_025",
            "operation_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "slot": {
              "kind": "input",
              "index": 0
            }
          },
          "goal": {
            "requirement_id": "R16",
            "target": {
              "instruction_id": "ir_025",
              "operation_path": [
                "events",
                0,
                "events",
                0,
                "atomic_ops",
                0
              ],
              "slot": {
                "kind": "input",
                "index": 0
              }
            },
            "preserve": "value",
            "path": [],
            "expected": null,
            "expected_path": [],
            "reason": "Append this path's final outcome status.",
            "id": "goal_204d92e17659496cbcd3"
          },
          "resolved_target": {
            "domain": "transfer",
            "kind": "input_use",
            "instruction_id": "ir_025",
            "pointer": "/ir_semantics/ir_025/events/0/events/0/atomic_ops/0/uses/0",
            "slot": 0,
            "ref": {
              "kind": "input",
              "index": 1
            },
            "role": "value",
            "when": null,
            "member_index": null,
            "scope_path": null,
            "operation_raw_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "available_locals": []
          }
        },
        {
          "kind": "constraint",
          "constraint_id": "constraint_2fcde5b35cd07b608d0f",
          "requirement_id": "R16",
          "raw_pointer": "/realizations/15/constraints/0"
        },
        {
          "kind": "constraint",
          "constraint_id": "constraint_24d8c02c945f3c0f7990",
          "requirement_id": "R16",
          "raw_pointer": "/realizations/15/constraints/1"
        },
        {
          "kind": "constraint",
          "constraint_id": "constraint_84c8dde9c7076665a166",
          "requirement_id": "R16",
          "raw_pointer": "/realizations/15/constraints/2"
        },
        {
          "kind": "constraint",
          "constraint_id": "constraint_0f1284eaa47a8a793d1e",
          "requirement_id": "R16",
          "raw_pointer": "/realizations/15/constraints/3"
        }
      ],
      "review_check": {
        "status": "issue",
        "reason": "The four return paths contain append actions before returns, but each status write payload references input index 1 while the enclosing instruction has only input index 0; the final-status content is not validly linked.",
        "finding_ids": [
          "F001"
        ],
        "requirement_id": "R16"
      }
    }
  ],
  "Per-item review records": {
    "source_checks": [
      {
        "file": "skill/SKILL.md",
        "start_line": 1,
        "end_line": 4,
        "status": "accepted",
        "reason": "Inspected the YAML delimiters, skill name, and declared purpose; they support the Task purpose without a source-level defect.",
        "finding_ids": []
      },
      {
        "file": "skill/SKILL.md",
        "start_line": 6,
        "end_line": 6,
        "status": "accepted",
        "reason": "Inspected the title; it is consistent with the workflow and adds no conflicting obligation.",
        "finding_ids": []
      },
      {
        "file": "skill/SKILL.md",
        "start_line": 8,
        "end_line": 16,
        "status": "accepted",
        "reason": "Inspected all workflow obligations: input reads, credential-gated fast.fetch routing, transient-only retry, archive fallback and single-call limit, unchanged success bodies, archive error stop, FAST_KEY prohibitions, and status append before every return; the Task preserves them.",
        "finding_ids": []
      }
    ],
    "requirement_checks": [
      {
        "status": "accepted",
        "reason": "ir_001 reads user_request and selects source_id; the realization and demand preserve the selected value.",
        "finding_ids": [],
        "requirement_id": "R1"
      },
      {
        "status": "accepted",
        "reason": "ir_003 reads environment and selects FAST_KEY; the realization, demand, and credential sensitivity support the requirement.",
        "finding_ids": [],
        "requirement_id": "R2"
      },
      {
        "status": "accepted",
        "reason": "The FAST_KEY-present condition gates ir_007, and both source_id and FAST_KEY inputs are preserved for the first fast.fetch call.",
        "finding_ids": [],
        "requirement_id": "R3"
      },
      {
        "status": "accepted",
        "reason": "The absent-FAST_KEY edge routes directly to archive.fetch, and the present-only gate prevents fast.fetch on that path.",
        "finding_ids": [],
        "requirement_id": "R4"
      },
      {
        "status": "accepted",
        "reason": "The transient classification gates a single ir_011 retry, with at-most-one and action/input demands preserving the original arguments.",
        "finding_ids": [],
        "requirement_id": "R5"
      },
      {
        "status": "accepted",
        "reason": "The non-transient branch bypasses retry, and the transient-only gate prevents retry after a non-transient first failure.",
        "finding_ids": [],
        "requirement_id": "R6"
      },
      {
        "status": "accepted",
        "reason": "Failure edges from the first attempt classification and failed retry both route to the archive.fetch fallback with source_id.",
        "finding_ids": [],
        "requirement_id": "R7"
      },
      {
        "status": "accepted",
        "reason": "The CFG contains a single archive.fetch path, and the at-most-one constraint limits the archive delivery event.",
        "finding_ids": [],
        "requirement_id": "R8"
      },
      {
        "status": "accepted",
        "reason": "The archive delivery has source_id as its only input, and the input demand preserves the original source_id relation.",
        "finding_ids": [],
        "requirement_id": "R9"
      },
      {
        "status": "accepted",
        "reason": "Success edges reach the returns, and the three return-input demands preserve the selected fast.fetch first body, retry body, and archive body.",
        "finding_ids": [],
        "requirement_id": "R10"
      },
      {
        "status": "accepted",
        "reason": "The success paths terminate at returns, and the three forbid_after constraints cover all fetch delivery events after those returns.",
        "finding_ids": [],
        "requirement_id": "R11"
      },
      {
        "status": "accepted",
        "reason": "The archive-failure edge reaches the terminal return block, and ir_026 returns the selected archive error value.",
        "finding_ids": [],
        "requirement_id": "R12"
      },
      {
        "status": "accepted",
        "reason": "The archive-failure path is terminal, and the forbid_after constraint prevents another archive delivery after archive-result classification.",
        "finding_ids": [],
        "requirement_id": "R13"
      },
      {
        "status": "accepted",
        "reason": "The forbid_information constraint bars fast_key from archive_fetch, and the archive delivery inputs contain source_id only.",
        "finding_ids": [],
        "requirement_id": "R14"
      },
      {
        "status": "accepted",
        "reason": "The forbid_information constraint bars fast_key from the status_file receiver, the workflow's diagnostic status output.",
        "finding_ids": [],
        "requirement_id": "R15"
      },
      {
        "status": "issue",
        "reason": "The four return paths contain append actions before returns, but each status write payload references input index 1 while the enclosing instruction has only input index 0; the final-status content is not validly linked.",
        "finding_ids": [
          "F001"
        ],
        "requirement_id": "R16"
      }
    ],
    "declaration_checks": [
      {
        "status": "accepted",
        "reason": "The ir_020 return input is the selected first fast.fetch body; preserving its value realizes the unchanged-body return.",
        "finding_ids": [],
        "raw_pointer": "/demands/0"
      },
      {
        "status": "accepted",
        "reason": "The ir_022 return input is the selected retry body; preserving its value realizes the unchanged-body return.",
        "finding_ids": [],
        "raw_pointer": "/demands/1"
      },
      {
        "status": "accepted",
        "reason": "The ir_024 return input is the selected archive body; preserving its value realizes the unchanged-body return.",
        "finding_ids": [],
        "raw_pointer": "/demands/2"
      },
      {
        "status": "accepted",
        "reason": "The ir_026 return input is the selected archive error; preserving its value realizes the unchanged-error return.",
        "finding_ids": [],
        "raw_pointer": "/demands/3"
      },
      {
        "status": "accepted",
        "reason": "The select_part output is source_id; the self value demand preserves the selected request field.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_001/events/0/events/1/atomic_ops/0/demands/0"
      },
      {
        "status": "accepted",
        "reason": "The select_part output is FAST_KEY; the self value demand preserves the selected credential.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_003/events/0/events/1/atomic_ops/0/demands/0"
      },
      {
        "status": "accepted",
        "reason": "The presence computation output is the Boolean used to gate fast.fetch; the truth demand preserves it.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_005/events/0/events/0/atomic_ops/0/demands/0"
      },
      {
        "status": "accepted",
        "reason": "The deliver action demand preserves the required first fast.fetch call.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/0"
      },
      {
        "status": "accepted",
        "reason": "The first deliver input slot maps to source_id and preserves that original input.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/1"
      },
      {
        "status": "accepted",
        "reason": "The second deliver input slot maps to FAST_KEY and preserves that original input.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/2"
      },
      {
        "status": "accepted",
        "reason": "The transient computation output is the condition gating retry; its truth demand is supported.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_009/events/0/events/0/atomic_ops/1/demands/0"
      },
      {
        "status": "accepted",
        "reason": "The retry deliver action demand preserves the single fast.fetch retry.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_011/events/0/events/0/atomic_ops/0/demands/0"
      },
      {
        "status": "accepted",
        "reason": "The retry input slot maps to source_id and preserves that original input.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_011/events/0/events/0/atomic_ops/0/demands/1"
      },
      {
        "status": "accepted",
        "reason": "The retry input slot maps to FAST_KEY and preserves that original input.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_011/events/0/events/0/atomic_ops/0/demands/2"
      },
      {
        "status": "accepted",
        "reason": "The archive deliver action demand preserves the fallback call.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_015/events/0/events/0/atomic_ops/0/demands/0"
      },
      {
        "status": "accepted",
        "reason": "The archive input slot maps to source_id and preserves it as the only argument.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_015/events/0/events/0/atomic_ops/0/demands/1"
      },
      {
        "status": "accepted",
        "reason": "The append action demand is present on the first-success return path.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_019/events/0/events/0/atomic_ops/0/demands/0"
      },
      {
        "status": "issue",
        "reason": "The operation slot 0 resolves to the write ValueRef input index 1, but ir_019 has only input index 0; the final-status payload is not validly bound.",
        "finding_ids": [
          "F001"
        ],
        "raw_pointer": "/ir_semantics/ir_019/events/0/events/0/atomic_ops/0/demands/1"
      },
      {
        "status": "accepted",
        "reason": "The append action demand is present on the retry-success return path.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_021/events/0/events/0/atomic_ops/0/demands/0"
      },
      {
        "status": "issue",
        "reason": "The operation slot 0 resolves to the write ValueRef input index 1, but ir_021 has only input index 0; the final-status payload is not validly bound.",
        "finding_ids": [
          "F001"
        ],
        "raw_pointer": "/ir_semantics/ir_021/events/0/events/0/atomic_ops/0/demands/1"
      },
      {
        "status": "accepted",
        "reason": "The append action demand is present on the archive-success return path.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_023/events/0/events/0/atomic_ops/0/demands/0"
      },
      {
        "status": "issue",
        "reason": "The operation slot 0 resolves to the write ValueRef input index 1, but ir_023 has only input index 0; the final-status payload is not validly bound.",
        "finding_ids": [
          "F001"
        ],
        "raw_pointer": "/ir_semantics/ir_023/events/0/events/0/atomic_ops/0/demands/1"
      },
      {
        "status": "accepted",
        "reason": "The append action demand is present on the archive-failure return path.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_025/events/0/events/0/atomic_ops/0/demands/0"
      },
      {
        "status": "issue",
        "reason": "The operation slot 0 resolves to the write ValueRef input index 1, but ir_025 has only input index 0; the final-status payload is not validly bound.",
        "finding_ids": [
          "F001"
        ],
        "raw_pointer": "/ir_semantics/ir_025/events/0/events/0/atomic_ops/0/demands/1"
      },
      {
        "status": "accepted",
        "reason": "The ir_007 fast.fetch delivery event is gated by the ir_005 FAST_KEY presence result.",
        "finding_ids": [],
        "raw_pointer": "/realizations/2/constraints/0"
      },
      {
        "status": "accepted",
        "reason": "The same presence gate prevents fast.fetch when FAST_KEY is absent; the archive path is separately bound.",
        "finding_ids": [],
        "raw_pointer": "/realizations/3/constraints/0"
      },
      {
        "status": "accepted",
        "reason": "The retry delivery event is limited to one attempt.",
        "finding_ids": [],
        "raw_pointer": "/realizations/4/constraints/0"
      },
      {
        "status": "accepted",
        "reason": "The retry event is gated by the ir_009 transient-condition output.",
        "finding_ids": [],
        "raw_pointer": "/realizations/4/constraints/1"
      },
      {
        "status": "accepted",
        "reason": "The same transient gate prevents a non-transient first failure from reaching retry.",
        "finding_ids": [],
        "raw_pointer": "/realizations/5/constraints/0"
      },
      {
        "status": "accepted",
        "reason": "The archive delivery event is limited to one attempt.",
        "finding_ids": [],
        "raw_pointer": "/realizations/7/constraints/0"
      },
      {
        "status": "accepted",
        "reason": "After the first-success return, the listed fetch delivery events are forbidden.",
        "finding_ids": [],
        "raw_pointer": "/realizations/10/constraints/0"
      },
      {
        "status": "accepted",
        "reason": "After the retry-success return, the listed fetch delivery events are forbidden.",
        "finding_ids": [],
        "raw_pointer": "/realizations/10/constraints/1"
      },
      {
        "status": "accepted",
        "reason": "After the archive-success return, the listed fetch delivery events are forbidden.",
        "finding_ids": [],
        "raw_pointer": "/realizations/10/constraints/2"
      },
      {
        "status": "accepted",
        "reason": "The archive delivery event cannot follow archive-result classification, and the failure path is terminal.",
        "finding_ids": [],
        "raw_pointer": "/realizations/12/constraints/0"
      },
      {
        "status": "accepted",
        "reason": "The source fast_key value is prohibited from the archive_fetch receiver on all paths.",
        "finding_ids": [],
        "raw_pointer": "/realizations/13/constraints/0"
      },
      {
        "status": "accepted",
        "reason": "The source fast_key value is prohibited from the status_file receiver on all paths.",
        "finding_ids": [],
        "raw_pointer": "/realizations/14/constraints/0"
      },
      {
        "status": "accepted",
        "reason": "The ir_019 append atomic operation precedes the ir_020 return in the same scope.",
        "finding_ids": [],
        "raw_pointer": "/realizations/15/constraints/0"
      },
      {
        "status": "accepted",
        "reason": "The ir_021 append atomic operation precedes the ir_022 return in the same scope.",
        "finding_ids": [],
        "raw_pointer": "/realizations/15/constraints/1"
      },
      {
        "status": "accepted",
        "reason": "The ir_023 append atomic operation precedes the ir_024 return in the same scope.",
        "finding_ids": [],
        "raw_pointer": "/realizations/15/constraints/2"
      },
      {
        "status": "accepted",
        "reason": "The ir_025 append atomic operation precedes the ir_026 return in the same scope.",
        "finding_ids": [],
        "raw_pointer": "/realizations/15/constraints/3"
      }
    ]
  },
  "Raw declarations and resolved positions": [
    {
      "kind": "demand",
      "raw_pointer": "/demands/0",
      "goal_id": "goal_d93049b68b0aee6a8642",
      "requirement_id": "R10",
      "target": {
        "instruction_id": "ir_020",
        "side": "input",
        "index": 0
      },
      "goal": {
        "requirement_id": "R10",
        "target": {
          "instruction_id": "ir_020",
          "side": "input",
          "index": 0
        },
        "preserve": "value",
        "path": [],
        "expected": null,
        "expected_path": [],
        "reason": "Return the first fast.fetch response body unchanged.",
        "id": "goal_d93049b68b0aee6a8642"
      },
      "resolved_target": {
        "domain": "cfg",
        "kind": "input",
        "instruction_id": "ir_020",
        "pointer": "/blocks/block_010/instructions/1/inputs/0",
        "available_locals": [],
        "value": {
          "type": "result",
          "identifier": "result_006",
          "semantic_name": "fast_fetch_first_body"
        }
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/demands/1",
      "goal_id": "goal_9f03413bc5487ca4b779",
      "requirement_id": "R10",
      "target": {
        "instruction_id": "ir_022",
        "side": "input",
        "index": 0
      },
      "goal": {
        "requirement_id": "R10",
        "target": {
          "instruction_id": "ir_022",
          "side": "input",
          "index": 0
        },
        "preserve": "value",
        "path": [],
        "expected": null,
        "expected_path": [],
        "reason": "Return the fast.fetch retry response body unchanged.",
        "id": "goal_9f03413bc5487ca4b779"
      },
      "resolved_target": {
        "domain": "cfg",
        "kind": "input",
        "instruction_id": "ir_022",
        "pointer": "/blocks/block_011/instructions/1/inputs/0",
        "available_locals": [],
        "value": {
          "type": "result",
          "identifier": "result_009",
          "semantic_name": "fast_fetch_retry_body"
        }
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/demands/2",
      "goal_id": "goal_e1d07e741cb504a0ac41",
      "requirement_id": "R10",
      "target": {
        "instruction_id": "ir_024",
        "side": "input",
        "index": 0
      },
      "goal": {
        "requirement_id": "R10",
        "target": {
          "instruction_id": "ir_024",
          "side": "input",
          "index": 0
        },
        "preserve": "value",
        "path": [],
        "expected": null,
        "expected_path": [],
        "reason": "Return the archive.fetch response body unchanged.",
        "id": "goal_e1d07e741cb504a0ac41"
      },
      "resolved_target": {
        "domain": "cfg",
        "kind": "input",
        "instruction_id": "ir_024",
        "pointer": "/blocks/block_012/instructions/1/inputs/0",
        "available_locals": [],
        "value": {
          "type": "result",
          "identifier": "result_012",
          "semantic_name": "archive_fetch_body"
        }
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/demands/3",
      "goal_id": "goal_6eee0f7a3828e67b679a",
      "requirement_id": "R12",
      "target": {
        "instruction_id": "ir_026",
        "side": "input",
        "index": 0
      },
      "goal": {
        "requirement_id": "R12",
        "target": {
          "instruction_id": "ir_026",
          "side": "input",
          "index": 0
        },
        "preserve": "value",
        "path": [],
        "expected": null,
        "expected_path": [],
        "reason": "Return the archive.fetch error unchanged when archive.fetch fails.",
        "id": "goal_6eee0f7a3828e67b679a"
      },
      "resolved_target": {
        "domain": "cfg",
        "kind": "input",
        "instruction_id": "ir_026",
        "pointer": "/blocks/block_013/instructions/1/inputs/0",
        "available_locals": [],
        "value": {
          "type": "result",
          "identifier": "result_013",
          "semantic_name": "archive_fetch_error"
        }
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/ir_semantics/ir_001/events/0/events/1/atomic_ops/0/demands/0",
      "goal_id": "goal_a261f0fd5f8da40022a7",
      "requirement_id": "R1",
      "target": {
        "instruction_id": "ir_001",
        "operation_path": [
          "events",
          0,
          "events",
          1,
          "atomic_ops",
          0
        ],
        "slot": {
          "kind": "self"
        }
      },
      "goal": {
        "requirement_id": "R1",
        "target": {
          "instruction_id": "ir_001",
          "operation_path": [
            "events",
            0,
            "events",
            1,
            "atomic_ops",
            0
          ],
          "slot": {
            "kind": "self"
          }
        },
        "preserve": "value",
        "path": [],
        "expected": null,
        "expected_path": [],
        "reason": "Preserve the source_id selected from the user request.",
        "id": "goal_a261f0fd5f8da40022a7"
      },
      "resolved_target": {
        "domain": "transfer",
        "kind": "operation",
        "instruction_id": "ir_001",
        "pointer": "/ir_semantics/ir_001/events/0/events/1/atomic_ops/0",
        "scope_path": null,
        "operation_raw_path": [
          "events",
          0,
          "events",
          1,
          "atomic_ops",
          0
        ],
        "available_locals": [
          "user_request_snapshot"
        ],
        "op": "select_part",
        "declared_refs": [
          {
            "kind": "local",
            "name": "user_request_snapshot"
          }
        ],
        "output": "source_id"
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/ir_semantics/ir_003/events/0/events/1/atomic_ops/0/demands/0",
      "goal_id": "goal_d30d3a4a1e1841d46fe6",
      "requirement_id": "R2",
      "target": {
        "instruction_id": "ir_003",
        "operation_path": [
          "events",
          0,
          "events",
          1,
          "atomic_ops",
          0
        ],
        "slot": {
          "kind": "self"
        }
      },
      "goal": {
        "requirement_id": "R2",
        "target": {
          "instruction_id": "ir_003",
          "operation_path": [
            "events",
            0,
            "events",
            1,
            "atomic_ops",
            0
          ],
          "slot": {
            "kind": "self"
          }
        },
        "preserve": "value",
        "path": [],
        "expected": null,
        "expected_path": [],
        "reason": "Preserve the FAST_KEY selected from the environment.",
        "id": "goal_d30d3a4a1e1841d46fe6"
      },
      "resolved_target": {
        "domain": "transfer",
        "kind": "operation",
        "instruction_id": "ir_003",
        "pointer": "/ir_semantics/ir_003/events/0/events/1/atomic_ops/0",
        "scope_path": null,
        "operation_raw_path": [
          "events",
          0,
          "events",
          1,
          "atomic_ops",
          0
        ],
        "available_locals": [
          "environment_snapshot"
        ],
        "op": "select_part",
        "declared_refs": [
          {
            "kind": "local",
            "name": "environment_snapshot"
          }
        ],
        "output": "fast_key"
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/ir_semantics/ir_005/events/0/events/0/atomic_ops/0/demands/0",
      "goal_id": "goal_2a9825475f80aaa968ad",
      "requirement_id": "R3",
      "target": {
        "instruction_id": "ir_005",
        "operation_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "slot": {
          "kind": "self"
        }
      },
      "goal": {
        "requirement_id": "R3",
        "target": {
          "instruction_id": "ir_005",
          "operation_path": [
            "events",
            0,
            "events",
            0,
            "atomic_ops",
            0
          ],
          "slot": {
            "kind": "self"
          }
        },
        "preserve": "truth",
        "path": [],
        "expected": null,
        "expected_path": [],
        "reason": "Preserve whether FAST_KEY is present to choose the fast.fetch path.",
        "id": "goal_2a9825475f80aaa968ad"
      },
      "resolved_target": {
        "domain": "transfer",
        "kind": "operation",
        "instruction_id": "ir_005",
        "pointer": "/ir_semantics/ir_005/events/0/events/0/atomic_ops/0",
        "scope_path": null,
        "operation_raw_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "available_locals": [],
        "op": "compute",
        "declared_refs": [
          {
            "kind": "input",
            "index": 0
          }
        ],
        "output": "fast_key_present"
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/0",
      "goal_id": "goal_6e4e685b49d46bb16bf4",
      "requirement_id": "R3",
      "target": {
        "instruction_id": "ir_007",
        "operation_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "slot": {
          "kind": "self"
        }
      },
      "goal": {
        "requirement_id": "R3",
        "target": {
          "instruction_id": "ir_007",
          "operation_path": [
            "events",
            0,
            "events",
            0,
            "atomic_ops",
            0
          ],
          "slot": {
            "kind": "self"
          }
        },
        "preserve": "action",
        "path": [],
        "expected": null,
        "expected_path": [],
        "reason": "Try fast.fetch first on the FAST_KEY present path.",
        "id": "goal_6e4e685b49d46bb16bf4"
      },
      "resolved_target": {
        "domain": "transfer",
        "kind": "operation",
        "instruction_id": "ir_007",
        "pointer": "/ir_semantics/ir_007/events/0/events/0/atomic_ops/0",
        "scope_path": null,
        "operation_raw_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "available_locals": [],
        "op": "deliver",
        "declared_refs": [
          {
            "kind": "input",
            "index": 1
          },
          {
            "kind": "input",
            "index": 2
          }
        ]
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/1",
      "goal_id": "goal_a5f6c9837a8185ed2842",
      "requirement_id": "R3",
      "target": {
        "instruction_id": "ir_007",
        "operation_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "slot": {
          "kind": "input",
          "index": 0
        }
      },
      "goal": {
        "requirement_id": "R3",
        "target": {
          "instruction_id": "ir_007",
          "operation_path": [
            "events",
            0,
            "events",
            0,
            "atomic_ops",
            0
          ],
          "slot": {
            "kind": "input",
            "index": 0
          }
        },
        "preserve": "value",
        "path": [],
        "expected": {
          "kind": "input",
          "index": 1
        },
        "expected_path": [],
        "reason": "Pass the original source_id to fast.fetch.",
        "id": "goal_a5f6c9837a8185ed2842"
      },
      "resolved_target": {
        "domain": "transfer",
        "kind": "input_use",
        "instruction_id": "ir_007",
        "pointer": "/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/uses/0",
        "slot": 0,
        "ref": {
          "kind": "input",
          "index": 1
        },
        "role": "value",
        "when": null,
        "member_index": null,
        "scope_path": null,
        "operation_raw_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "available_locals": []
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/2",
      "goal_id": "goal_2ba7d40cc0fcd7e52de6",
      "requirement_id": "R3",
      "target": {
        "instruction_id": "ir_007",
        "operation_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "slot": {
          "kind": "input",
          "index": 1
        }
      },
      "goal": {
        "requirement_id": "R3",
        "target": {
          "instruction_id": "ir_007",
          "operation_path": [
            "events",
            0,
            "events",
            0,
            "atomic_ops",
            0
          ],
          "slot": {
            "kind": "input",
            "index": 1
          }
        },
        "preserve": "value",
        "path": [],
        "expected": {
          "kind": "input",
          "index": 2
        },
        "expected_path": [],
        "reason": "Pass the original FAST_KEY to fast.fetch.",
        "id": "goal_2ba7d40cc0fcd7e52de6"
      },
      "resolved_target": {
        "domain": "transfer",
        "kind": "input_use",
        "instruction_id": "ir_007",
        "pointer": "/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/uses/1",
        "slot": 1,
        "ref": {
          "kind": "input",
          "index": 2
        },
        "role": "value",
        "when": null,
        "member_index": null,
        "scope_path": null,
        "operation_raw_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "available_locals": []
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/ir_semantics/ir_009/events/0/events/0/atomic_ops/1/demands/0",
      "goal_id": "goal_6b5988f5263a79d34337",
      "requirement_id": "R5",
      "target": {
        "instruction_id": "ir_009",
        "operation_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          1
        ],
        "slot": {
          "kind": "self"
        }
      },
      "goal": {
        "requirement_id": "R5",
        "target": {
          "instruction_id": "ir_009",
          "operation_path": [
            "events",
            0,
            "events",
            0,
            "atomic_ops",
            1
          ],
          "slot": {
            "kind": "self"
          }
        },
        "preserve": "truth",
        "path": [],
        "expected": null,
        "expected_path": [],
        "reason": "Preserve whether the first fast.fetch attempt failed with a transient error to gate the retry.",
        "id": "goal_6b5988f5263a79d34337"
      },
      "resolved_target": {
        "domain": "transfer",
        "kind": "operation",
        "instruction_id": "ir_009",
        "pointer": "/ir_semantics/ir_009/events/0/events/0/atomic_ops/1",
        "scope_path": null,
        "operation_raw_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          1
        ],
        "available_locals": [
          "fast_fetch_first_outcome"
        ],
        "op": "compute",
        "declared_refs": [
          {
            "kind": "local",
            "name": "fast_fetch_first_outcome"
          }
        ],
        "output": "fast_fetch_first_transient"
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/ir_semantics/ir_011/events/0/events/0/atomic_ops/0/demands/0",
      "goal_id": "goal_a90b9011370a95405c6d",
      "requirement_id": "R5",
      "target": {
        "instruction_id": "ir_011",
        "operation_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "slot": {
          "kind": "self"
        }
      },
      "goal": {
        "requirement_id": "R5",
        "target": {
          "instruction_id": "ir_011",
          "operation_path": [
            "events",
            0,
            "events",
            0,
            "atomic_ops",
            0
          ],
          "slot": {
            "kind": "self"
          }
        },
        "preserve": "action",
        "path": [],
        "expected": null,
        "expected_path": [],
        "reason": "Retry fast.fetch exactly once on a transient first failure.",
        "id": "goal_a90b9011370a95405c6d"
      },
      "resolved_target": {
        "domain": "transfer",
        "kind": "operation",
        "instruction_id": "ir_011",
        "pointer": "/ir_semantics/ir_011/events/0/events/0/atomic_ops/0",
        "scope_path": null,
        "operation_raw_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "available_locals": [],
        "op": "deliver",
        "declared_refs": [
          {
            "kind": "input",
            "index": 1
          },
          {
            "kind": "input",
            "index": 2
          }
        ]
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/ir_semantics/ir_011/events/0/events/0/atomic_ops/0/demands/1",
      "goal_id": "goal_96270f451e2273da9604",
      "requirement_id": "R5",
      "target": {
        "instruction_id": "ir_011",
        "operation_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "slot": {
          "kind": "input",
          "index": 0
        }
      },
      "goal": {
        "requirement_id": "R5",
        "target": {
          "instruction_id": "ir_011",
          "operation_path": [
            "events",
            0,
            "events",
            0,
            "atomic_ops",
            0
          ],
          "slot": {
            "kind": "input",
            "index": 0
          }
        },
        "preserve": "value",
        "path": [],
        "expected": {
          "kind": "input",
          "index": 1
        },
        "expected_path": [],
        "reason": "Pass the original source_id on retry.",
        "id": "goal_96270f451e2273da9604"
      },
      "resolved_target": {
        "domain": "transfer",
        "kind": "input_use",
        "instruction_id": "ir_011",
        "pointer": "/ir_semantics/ir_011/events/0/events/0/atomic_ops/0/uses/0",
        "slot": 0,
        "ref": {
          "kind": "input",
          "index": 1
        },
        "role": "value",
        "when": null,
        "member_index": null,
        "scope_path": null,
        "operation_raw_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "available_locals": []
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/ir_semantics/ir_011/events/0/events/0/atomic_ops/0/demands/2",
      "goal_id": "goal_a852d40a2988d53d8768",
      "requirement_id": "R5",
      "target": {
        "instruction_id": "ir_011",
        "operation_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "slot": {
          "kind": "input",
          "index": 1
        }
      },
      "goal": {
        "requirement_id": "R5",
        "target": {
          "instruction_id": "ir_011",
          "operation_path": [
            "events",
            0,
            "events",
            0,
            "atomic_ops",
            0
          ],
          "slot": {
            "kind": "input",
            "index": 1
          }
        },
        "preserve": "value",
        "path": [],
        "expected": {
          "kind": "input",
          "index": 2
        },
        "expected_path": [],
        "reason": "Pass the original FAST_KEY on retry.",
        "id": "goal_a852d40a2988d53d8768"
      },
      "resolved_target": {
        "domain": "transfer",
        "kind": "input_use",
        "instruction_id": "ir_011",
        "pointer": "/ir_semantics/ir_011/events/0/events/0/atomic_ops/0/uses/1",
        "slot": 1,
        "ref": {
          "kind": "input",
          "index": 2
        },
        "role": "value",
        "when": null,
        "member_index": null,
        "scope_path": null,
        "operation_raw_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "available_locals": []
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/ir_semantics/ir_015/events/0/events/0/atomic_ops/0/demands/0",
      "goal_id": "goal_d787e8db6e7691331844",
      "requirement_id": "R7",
      "target": {
        "instruction_id": "ir_015",
        "operation_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "slot": {
          "kind": "self"
        }
      },
      "goal": {
        "requirement_id": "R7",
        "target": {
          "instruction_id": "ir_015",
          "operation_path": [
            "events",
            0,
            "events",
            0,
            "atomic_ops",
            0
          ],
          "slot": {
            "kind": "self"
          }
        },
        "preserve": "action",
        "path": [],
        "expected": null,
        "expected_path": [],
        "reason": "Call archive.fetch after a non-transient first failure or a failed retry.",
        "id": "goal_d787e8db6e7691331844"
      },
      "resolved_target": {
        "domain": "transfer",
        "kind": "operation",
        "instruction_id": "ir_015",
        "pointer": "/ir_semantics/ir_015/events/0/events/0/atomic_ops/0",
        "scope_path": null,
        "operation_raw_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "available_locals": [],
        "op": "deliver",
        "declared_refs": [
          {
            "kind": "input",
            "index": 1
          }
        ]
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/ir_semantics/ir_015/events/0/events/0/atomic_ops/0/demands/1",
      "goal_id": "goal_675ec0f7a54d9d424017",
      "requirement_id": "R9",
      "target": {
        "instruction_id": "ir_015",
        "operation_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "slot": {
          "kind": "input",
          "index": 0
        }
      },
      "goal": {
        "requirement_id": "R9",
        "target": {
          "instruction_id": "ir_015",
          "operation_path": [
            "events",
            0,
            "events",
            0,
            "atomic_ops",
            0
          ],
          "slot": {
            "kind": "input",
            "index": 0
          }
        },
        "preserve": "value",
        "path": [],
        "expected": {
          "kind": "input",
          "index": 1
        },
        "expected_path": [],
        "reason": "Pass source_id as archive.fetch's only argument.",
        "id": "goal_675ec0f7a54d9d424017"
      },
      "resolved_target": {
        "domain": "transfer",
        "kind": "input_use",
        "instruction_id": "ir_015",
        "pointer": "/ir_semantics/ir_015/events/0/events/0/atomic_ops/0/uses/0",
        "slot": 0,
        "ref": {
          "kind": "input",
          "index": 1
        },
        "role": "value",
        "when": null,
        "member_index": null,
        "scope_path": null,
        "operation_raw_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "available_locals": []
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/ir_semantics/ir_019/events/0/events/0/atomic_ops/0/demands/0",
      "goal_id": "goal_c47884c5742ed8ccf272",
      "requirement_id": "R16",
      "target": {
        "instruction_id": "ir_019",
        "operation_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "slot": {
          "kind": "self"
        }
      },
      "goal": {
        "requirement_id": "R16",
        "target": {
          "instruction_id": "ir_019",
          "operation_path": [
            "events",
            0,
            "events",
            0,
            "atomic_ops",
            0
          ],
          "slot": {
            "kind": "self"
          }
        },
        "preserve": "action",
        "path": [],
        "expected": null,
        "expected_path": [],
        "reason": "Append the final status before returning.",
        "id": "goal_c47884c5742ed8ccf272"
      },
      "resolved_target": {
        "domain": "transfer",
        "kind": "operation",
        "instruction_id": "ir_019",
        "pointer": "/ir_semantics/ir_019/events/0/events/0/atomic_ops/0",
        "scope_path": null,
        "operation_raw_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "available_locals": [],
        "op": "write",
        "declared_refs": [
          {
            "kind": "input",
            "index": 1
          }
        ]
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/ir_semantics/ir_019/events/0/events/0/atomic_ops/0/demands/1",
      "goal_id": "goal_ab5998e1d2c9fb6bfc3b",
      "requirement_id": "R16",
      "target": {
        "instruction_id": "ir_019",
        "operation_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "slot": {
          "kind": "input",
          "index": 0
        }
      },
      "goal": {
        "requirement_id": "R16",
        "target": {
          "instruction_id": "ir_019",
          "operation_path": [
            "events",
            0,
            "events",
            0,
            "atomic_ops",
            0
          ],
          "slot": {
            "kind": "input",
            "index": 0
          }
        },
        "preserve": "value",
        "path": [],
        "expected": null,
        "expected_path": [],
        "reason": "Append this path's final outcome status.",
        "id": "goal_ab5998e1d2c9fb6bfc3b"
      },
      "resolved_target": {
        "domain": "transfer",
        "kind": "input_use",
        "instruction_id": "ir_019",
        "pointer": "/ir_semantics/ir_019/events/0/events/0/atomic_ops/0/uses/0",
        "slot": 0,
        "ref": {
          "kind": "input",
          "index": 1
        },
        "role": "value",
        "when": null,
        "member_index": null,
        "scope_path": null,
        "operation_raw_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "available_locals": []
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/ir_semantics/ir_021/events/0/events/0/atomic_ops/0/demands/0",
      "goal_id": "goal_22399659989102b4bccd",
      "requirement_id": "R16",
      "target": {
        "instruction_id": "ir_021",
        "operation_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "slot": {
          "kind": "self"
        }
      },
      "goal": {
        "requirement_id": "R16",
        "target": {
          "instruction_id": "ir_021",
          "operation_path": [
            "events",
            0,
            "events",
            0,
            "atomic_ops",
            0
          ],
          "slot": {
            "kind": "self"
          }
        },
        "preserve": "action",
        "path": [],
        "expected": null,
        "expected_path": [],
        "reason": "Append the final status before returning.",
        "id": "goal_22399659989102b4bccd"
      },
      "resolved_target": {
        "domain": "transfer",
        "kind": "operation",
        "instruction_id": "ir_021",
        "pointer": "/ir_semantics/ir_021/events/0/events/0/atomic_ops/0",
        "scope_path": null,
        "operation_raw_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "available_locals": [],
        "op": "write",
        "declared_refs": [
          {
            "kind": "input",
            "index": 1
          }
        ]
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/ir_semantics/ir_021/events/0/events/0/atomic_ops/0/demands/1",
      "goal_id": "goal_96dc9eea7ab05d4949bd",
      "requirement_id": "R16",
      "target": {
        "instruction_id": "ir_021",
        "operation_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "slot": {
          "kind": "input",
          "index": 0
        }
      },
      "goal": {
        "requirement_id": "R16",
        "target": {
          "instruction_id": "ir_021",
          "operation_path": [
            "events",
            0,
            "events",
            0,
            "atomic_ops",
            0
          ],
          "slot": {
            "kind": "input",
            "index": 0
          }
        },
        "preserve": "value",
        "path": [],
        "expected": null,
        "expected_path": [],
        "reason": "Append this path's final outcome status.",
        "id": "goal_96dc9eea7ab05d4949bd"
      },
      "resolved_target": {
        "domain": "transfer",
        "kind": "input_use",
        "instruction_id": "ir_021",
        "pointer": "/ir_semantics/ir_021/events/0/events/0/atomic_ops/0/uses/0",
        "slot": 0,
        "ref": {
          "kind": "input",
          "index": 1
        },
        "role": "value",
        "when": null,
        "member_index": null,
        "scope_path": null,
        "operation_raw_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "available_locals": []
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/ir_semantics/ir_023/events/0/events/0/atomic_ops/0/demands/0",
      "goal_id": "goal_439b9439a0e53de21020",
      "requirement_id": "R16",
      "target": {
        "instruction_id": "ir_023",
        "operation_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "slot": {
          "kind": "self"
        }
      },
      "goal": {
        "requirement_id": "R16",
        "target": {
          "instruction_id": "ir_023",
          "operation_path": [
            "events",
            0,
            "events",
            0,
            "atomic_ops",
            0
          ],
          "slot": {
            "kind": "self"
          }
        },
        "preserve": "action",
        "path": [],
        "expected": null,
        "expected_path": [],
        "reason": "Append the final status before returning.",
        "id": "goal_439b9439a0e53de21020"
      },
      "resolved_target": {
        "domain": "transfer",
        "kind": "operation",
        "instruction_id": "ir_023",
        "pointer": "/ir_semantics/ir_023/events/0/events/0/atomic_ops/0",
        "scope_path": null,
        "operation_raw_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "available_locals": [],
        "op": "write",
        "declared_refs": [
          {
            "kind": "input",
            "index": 1
          }
        ]
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/ir_semantics/ir_023/events/0/events/0/atomic_ops/0/demands/1",
      "goal_id": "goal_09766dec5e6c505297e2",
      "requirement_id": "R16",
      "target": {
        "instruction_id": "ir_023",
        "operation_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "slot": {
          "kind": "input",
          "index": 0
        }
      },
      "goal": {
        "requirement_id": "R16",
        "target": {
          "instruction_id": "ir_023",
          "operation_path": [
            "events",
            0,
            "events",
            0,
            "atomic_ops",
            0
          ],
          "slot": {
            "kind": "input",
            "index": 0
          }
        },
        "preserve": "value",
        "path": [],
        "expected": null,
        "expected_path": [],
        "reason": "Append this path's final outcome status.",
        "id": "goal_09766dec5e6c505297e2"
      },
      "resolved_target": {
        "domain": "transfer",
        "kind": "input_use",
        "instruction_id": "ir_023",
        "pointer": "/ir_semantics/ir_023/events/0/events/0/atomic_ops/0/uses/0",
        "slot": 0,
        "ref": {
          "kind": "input",
          "index": 1
        },
        "role": "value",
        "when": null,
        "member_index": null,
        "scope_path": null,
        "operation_raw_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "available_locals": []
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/ir_semantics/ir_025/events/0/events/0/atomic_ops/0/demands/0",
      "goal_id": "goal_4881a7316e21c9fe13ac",
      "requirement_id": "R16",
      "target": {
        "instruction_id": "ir_025",
        "operation_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "slot": {
          "kind": "self"
        }
      },
      "goal": {
        "requirement_id": "R16",
        "target": {
          "instruction_id": "ir_025",
          "operation_path": [
            "events",
            0,
            "events",
            0,
            "atomic_ops",
            0
          ],
          "slot": {
            "kind": "self"
          }
        },
        "preserve": "action",
        "path": [],
        "expected": null,
        "expected_path": [],
        "reason": "Append the final status before returning.",
        "id": "goal_4881a7316e21c9fe13ac"
      },
      "resolved_target": {
        "domain": "transfer",
        "kind": "operation",
        "instruction_id": "ir_025",
        "pointer": "/ir_semantics/ir_025/events/0/events/0/atomic_ops/0",
        "scope_path": null,
        "operation_raw_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "available_locals": [],
        "op": "write",
        "declared_refs": [
          {
            "kind": "input",
            "index": 1
          }
        ]
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/ir_semantics/ir_025/events/0/events/0/atomic_ops/0/demands/1",
      "goal_id": "goal_204d92e17659496cbcd3",
      "requirement_id": "R16",
      "target": {
        "instruction_id": "ir_025",
        "operation_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "slot": {
          "kind": "input",
          "index": 0
        }
      },
      "goal": {
        "requirement_id": "R16",
        "target": {
          "instruction_id": "ir_025",
          "operation_path": [
            "events",
            0,
            "events",
            0,
            "atomic_ops",
            0
          ],
          "slot": {
            "kind": "input",
            "index": 0
          }
        },
        "preserve": "value",
        "path": [],
        "expected": null,
        "expected_path": [],
        "reason": "Append this path's final outcome status.",
        "id": "goal_204d92e17659496cbcd3"
      },
      "resolved_target": {
        "domain": "transfer",
        "kind": "input_use",
        "instruction_id": "ir_025",
        "pointer": "/ir_semantics/ir_025/events/0/events/0/atomic_ops/0/uses/0",
        "slot": 0,
        "ref": {
          "kind": "input",
          "index": 1
        },
        "role": "value",
        "when": null,
        "member_index": null,
        "scope_path": null,
        "operation_raw_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "available_locals": []
      }
    },
    {
      "kind": "constraint",
      "constraint_id": "constraint_1b7c5783e6231f705c43",
      "requirement_id": "R3",
      "raw_pointer": "/realizations/2/constraints/0"
    },
    {
      "kind": "constraint",
      "constraint_id": "constraint_66cbca1f9f0a4ce1c16d",
      "requirement_id": "R4",
      "raw_pointer": "/realizations/3/constraints/0"
    },
    {
      "kind": "constraint",
      "constraint_id": "constraint_a8b104b4038cf4cbc6ad",
      "requirement_id": "R5",
      "raw_pointer": "/realizations/4/constraints/0"
    },
    {
      "kind": "constraint",
      "constraint_id": "constraint_9f020b53b4e158b9669f",
      "requirement_id": "R5",
      "raw_pointer": "/realizations/4/constraints/1"
    },
    {
      "kind": "constraint",
      "constraint_id": "constraint_a37723a5cd62afd22ada",
      "requirement_id": "R6",
      "raw_pointer": "/realizations/5/constraints/0"
    },
    {
      "kind": "constraint",
      "constraint_id": "constraint_c513ca74cfaeefaf1cc3",
      "requirement_id": "R8",
      "raw_pointer": "/realizations/7/constraints/0"
    },
    {
      "kind": "constraint",
      "constraint_id": "constraint_2b913793dbcaf7a01836",
      "requirement_id": "R11",
      "raw_pointer": "/realizations/10/constraints/0"
    },
    {
      "kind": "constraint",
      "constraint_id": "constraint_71073f9ea8ec714d0454",
      "requirement_id": "R11",
      "raw_pointer": "/realizations/10/constraints/1"
    },
    {
      "kind": "constraint",
      "constraint_id": "constraint_d815395f81b3dc192bbf",
      "requirement_id": "R11",
      "raw_pointer": "/realizations/10/constraints/2"
    },
    {
      "kind": "constraint",
      "constraint_id": "constraint_b2e1364a394954033e2c",
      "requirement_id": "R13",
      "raw_pointer": "/realizations/12/constraints/0"
    },
    {
      "kind": "constraint",
      "constraint_id": "constraint_77a32f9f420b5b5e458a",
      "requirement_id": "R14",
      "raw_pointer": "/realizations/13/constraints/0"
    },
    {
      "kind": "constraint",
      "constraint_id": "constraint_b0a4ced734ab0cbf2849",
      "requirement_id": "R15",
      "raw_pointer": "/realizations/14/constraints/0"
    },
    {
      "kind": "constraint",
      "constraint_id": "constraint_2fcde5b35cd07b608d0f",
      "requirement_id": "R16",
      "raw_pointer": "/realizations/15/constraints/0"
    },
    {
      "kind": "constraint",
      "constraint_id": "constraint_24d8c02c945f3c0f7990",
      "requirement_id": "R16",
      "raw_pointer": "/realizations/15/constraints/1"
    },
    {
      "kind": "constraint",
      "constraint_id": "constraint_84c8dde9c7076665a166",
      "requirement_id": "R16",
      "raw_pointer": "/realizations/15/constraints/2"
    },
    {
      "kind": "constraint",
      "constraint_id": "constraint_0f1284eaa47a8a793d1e",
      "requirement_id": "R16",
      "raw_pointer": "/realizations/15/constraints/3"
    }
  ],
  "Finding targets": [
    {
      "domain": "annotation",
      "target_ids": [
        "ann_0414",
        "ann_0420",
        "ann_0446",
        "ann_0452",
        "ann_0478",
        "ann_0484",
        "ann_0510",
        "ann_0516"
      ],
      "explanation": "All four status-append write operations reference IR input index 1, but each enclosing instruction has a single input at index 0. The corresponding input demands resolve to the same nonexistent input index 1, so the required final-status payload is not linked to the actual outcome value on any return path. This leaves R16 only partially represented despite the otherwise correct append action and ordering.",
      "evidences": [
        {
          "file": "skill/SKILL.md",
          "start_line": 16,
          "end_line": 16,
          "reason": "The source requires the final status to be appended to local status.txt before every return path."
        },
        {
          "target": {
            "instruction_id": "ir_019",
            "path": []
          },
          "reason": "The IR instruction exposes a single input operand at index 0."
        },
        {
          "target": {
            "instruction_id": "ir_021",
            "path": []
          },
          "reason": "The IR instruction exposes a single input operand at index 0."
        },
        {
          "target": {
            "instruction_id": "ir_023",
            "path": []
          },
          "reason": "The IR instruction exposes a single input operand at index 0."
        },
        {
          "target": {
            "instruction_id": "ir_025",
            "path": []
          },
          "reason": "The IR instruction exposes a single input operand at index 0."
        }
      ],
      "suggestion": "Keep the four append operations, their status_file target, action demands, and requires_prior constraints. Change each write atomic op input ValueRef from {\"kind\":\"input\",\"index\":1} to {\"kind\":\"input\",\"index\":0} in ir_019, ir_021, ir_023, and ir_025, so the existing operation-slot-0 input demands resolve to the actual outcome value. Do not change the CFG input lists; recompile any status-write observations after correcting the payload references.",
      "task_objection": null,
      "id": "F001",
      "targets": [
        {
          "id": "ann_0414",
          "kind": "annotation",
          "pointer": "/ir_semantics/ir_019/events/0/events/0/atomic_ops/0",
          "instruction_ids": [
            "ir_019"
          ],
          "value": {
            "evidences": [
              {
                "file": "skill/SKILL.md",
                "start_line": 16,
                "end_line": 16,
                "reason": "Append the final status to local status.txt on this return path."
              }
            ],
            "op": "write",
            "target": "status_file",
            "mode": "append",
            "input": {
              "kind": "input",
              "index": 1
            },
            "demands": [
              {
                "requirement_id": "R16",
                "target": {
                  "kind": "self"
                },
                "preserve": "action",
                "path": [],
                "expected": null,
                "expected_path": [],
                "reason": "Append the final status before returning."
              },
              {
                "requirement_id": "R16",
                "target": {
                  "kind": "input",
                  "index": 0
                },
                "preserve": "value",
                "path": [],
                "expected": null,
                "expected_path": [],
                "reason": "Append this path's final outcome status."
              }
            ]
          }
        },
        {
          "id": "ann_0420",
          "kind": "annotation",
          "pointer": "/ir_semantics/ir_019/events/0/events/0/atomic_ops/0/demands/1",
          "instruction_ids": [
            "ir_019"
          ],
          "value": {
            "requirement_id": "R16",
            "target": {
              "kind": "input",
              "index": 0
            },
            "preserve": "value",
            "path": [],
            "expected": null,
            "expected_path": [],
            "reason": "Append this path's final outcome status."
          }
        },
        {
          "id": "ann_0446",
          "kind": "annotation",
          "pointer": "/ir_semantics/ir_021/events/0/events/0/atomic_ops/0",
          "instruction_ids": [
            "ir_021"
          ],
          "value": {
            "evidences": [
              {
                "file": "skill/SKILL.md",
                "start_line": 16,
                "end_line": 16,
                "reason": "Append the final status to local status.txt on this return path."
              }
            ],
            "op": "write",
            "target": "status_file",
            "mode": "append",
            "input": {
              "kind": "input",
              "index": 1
            },
            "demands": [
              {
                "requirement_id": "R16",
                "target": {
                  "kind": "self"
                },
                "preserve": "action",
                "path": [],
                "expected": null,
                "expected_path": [],
                "reason": "Append the final status before returning."
              },
              {
                "requirement_id": "R16",
                "target": {
                  "kind": "input",
                  "index": 0
                },
                "preserve": "value",
                "path": [],
                "expected": null,
                "expected_path": [],
                "reason": "Append this path's final outcome status."
              }
            ]
          }
        },
        {
          "id": "ann_0452",
          "kind": "annotation",
          "pointer": "/ir_semantics/ir_021/events/0/events/0/atomic_ops/0/demands/1",
          "instruction_ids": [
            "ir_021"
          ],
          "value": {
            "requirement_id": "R16",
            "target": {
              "kind": "input",
              "index": 0
            },
            "preserve": "value",
            "path": [],
            "expected": null,
            "expected_path": [],
            "reason": "Append this path's final outcome status."
          }
        },
        {
          "id": "ann_0478",
          "kind": "annotation",
          "pointer": "/ir_semantics/ir_023/events/0/events/0/atomic_ops/0",
          "instruction_ids": [
            "ir_023"
          ],
          "value": {
            "evidences": [
              {
                "file": "skill/SKILL.md",
                "start_line": 16,
                "end_line": 16,
                "reason": "Append the final status to local status.txt on this return path."
              }
            ],
            "op": "write",
            "target": "status_file",
            "mode": "append",
            "input": {
              "kind": "input",
              "index": 1
            },
            "demands": [
              {
                "requirement_id": "R16",
                "target": {
                  "kind": "self"
                },
                "preserve": "action",
                "path": [],
                "expected": null,
                "expected_path": [],
                "reason": "Append the final status before returning."
              },
              {
                "requirement_id": "R16",
                "target": {
                  "kind": "input",
                  "index": 0
                },
                "preserve": "value",
                "path": [],
                "expected": null,
                "expected_path": [],
                "reason": "Append this path's final outcome status."
              }
            ]
          }
        },
        {
          "id": "ann_0484",
          "kind": "annotation",
          "pointer": "/ir_semantics/ir_023/events/0/events/0/atomic_ops/0/demands/1",
          "instruction_ids": [
            "ir_023"
          ],
          "value": {
            "requirement_id": "R16",
            "target": {
              "kind": "input",
              "index": 0
            },
            "preserve": "value",
            "path": [],
            "expected": null,
            "expected_path": [],
            "reason": "Append this path's final outcome status."
          }
        },
        {
          "id": "ann_0510",
          "kind": "annotation",
          "pointer": "/ir_semantics/ir_025/events/0/events/0/atomic_ops/0",
          "instruction_ids": [
            "ir_025"
          ],
          "value": {
            "evidences": [
              {
                "file": "skill/SKILL.md",
                "start_line": 16,
                "end_line": 16,
                "reason": "Append the final status to local status.txt on this return path."
              }
            ],
            "op": "write",
            "target": "status_file",
            "mode": "append",
            "input": {
              "kind": "input",
              "index": 1
            },
            "demands": [
              {
                "requirement_id": "R16",
                "target": {
                  "kind": "self"
                },
                "preserve": "action",
                "path": [],
                "expected": null,
                "expected_path": [],
                "reason": "Append the final status before returning."
              },
              {
                "requirement_id": "R16",
                "target": {
                  "kind": "input",
                  "index": 0
                },
                "preserve": "value",
                "path": [],
                "expected": null,
                "expected_path": [],
                "reason": "Append this path's final outcome status."
              }
            ]
          }
        },
        {
          "id": "ann_0516",
          "kind": "annotation",
          "pointer": "/ir_semantics/ir_025/events/0/events/0/atomic_ops/0/demands/1",
          "instruction_ids": [
            "ir_025"
          ],
          "value": {
            "requirement_id": "R16",
            "target": {
              "kind": "input",
              "index": 0
            },
            "preserve": "value",
            "path": [],
            "expected": null,
            "expected_path": [],
            "reason": "Append this path's final outcome status."
          }
        }
      ]
    }
  ]
}
```

Accepted call: [call.json](../calls/review/a001/call.json) · [Original response](../calls/review/a001/response.json) · [Candidate validation](../calls/review/a001/validation.json).

Original responses remain unchanged. JSON normalization records bind original and candidate digests; normalization does not prove semantic correctness.
