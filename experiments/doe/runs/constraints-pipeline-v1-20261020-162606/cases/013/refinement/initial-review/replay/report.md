# Source → Task → declarations whole-chain review

**Material issues found** · Execution status: `complete`

Review structure, references, evidence and declared coverage passed validation\.

This semantic review does not rewrite the sealed Task, annotation or propagation facts. Accounting coverage of source, Task, demand/constraint declarations and IR does not prove semantic completeness; no reported issue does not prove correct interpretation, minimal demands or absence of DOE.

## Per-requirement semantic correspondence

Expression status and review acceptance do not prove requirement satisfaction. Full source excerpts, remaining gaps and resolved declarations appear in the audit records below.

| Source span | Task requirement | Expression status | Raw demand / constraint | Review record |
| --- | --- | --- | --- | --- |
| skill/SKILL\.md:8\-8 | R1: Read source\_id from the user's request\. | expressed | /ir\_semantics/ir\_001/events/0/events/1/atomic\_ops/0/demands/0 → goal\_a261f0fd5f8da40022a7 | accepted |
| skill/SKILL\.md:8\-8 | R2: Read FAST\_KEY from the environment\. | expressed | /ir\_semantics/ir\_003/events/0/events/1/atomic\_ops/0/demands/0 → goal\_d30d3a4a1e1841d46fe6 | issue |
| skill/SKILL\.md:9\-9 | R3: If FAST\_KEY is present, try fast\.fetch first with source\_id and FAST\_KEY\. | expressed | /ir\_semantics/ir\_005/events/0/events/0/atomic\_ops/0/demands/0 → goal\_2a9825475f80aaa968ad; /ir\_semantics/ir\_007/events/0/events/0/atomic\_ops/0/demands/0 → goal\_6e4e685b49d46bb16bf4; /ir\_semantics/ir\_007/events/0/events/0/atomic\_ops/0/demands/1 → goal\_a5f6c9837a8185ed2842; /ir\_semantics/ir\_007/events/0/events/0/atomic\_ops/0/demands/2 → goal\_2ba7d40cc0fcd7e52de6; /realizations/2/constraints/0 → constraint\_1b7c5783e6231f705c43 | accepted |
| skill/SKILL\.md:9\-9 | R4: If FAST\_KEY is absent, go directly to archive\.fetch without calling fast\.fetch\. | expressed | /realizations/3/constraints/0 → constraint\_66cbca1f9f0a4ce1c16d | accepted |
| skill/SKILL\.md:10\-10 | R5: Retry fast\.fetch exactly once only when its first attempt fails with a transient error\. | expressed | /ir\_semantics/ir\_009/events/0/events/0/atomic\_ops/1/demands/0 → goal\_6b5988f5263a79d34337; /ir\_semantics/ir\_011/events/0/events/0/atomic\_ops/0/demands/0 → goal\_a90b9011370a95405c6d; /ir\_semantics/ir\_011/events/0/events/0/atomic\_ops/0/demands/1 → goal\_96270f451e2273da9604; /ir\_semantics/ir\_011/events/0/events/0/atomic\_ops/0/demands/2 → goal\_a852d40a2988d53d8768; /realizations/4/constraints/0 → constraint\_a8b104b4038cf4cbc6ad; /realizations/4/constraints/1 → constraint\_9f020b53b4e158b9669f | issue |
| skill/SKILL\.md:10\-10 | R6: Do not retry a non\-transient first failure of fast\.fetch\. | expressed | /realizations/5/constraints/0 → constraint\_a37723a5cd62afd22ada | issue |
| skill/SKILL\.md:11\-11 | R7: After a non\-transient first failure of fast\.fetch or any failed retry of fast\.fetch, call archive\.fetch with source\_id\. | expressed | /ir\_semantics/ir\_015/events/0/events/0/atomic\_ops/0/demands/0 → goal\_d787e8db6e7691331844 | accepted |
| skill/SKILL\.md:12\-12 | R8: Call archive\.fetch at most once\. | expressed | /realizations/7/constraints/0 → constraint\_c513ca74cfaeefaf1cc3 | accepted |
| skill/SKILL\.md:12\-12 | R9: Pass source\_id as archive\.fetch's only argument\. | expressed | /ir\_semantics/ir\_015/events/0/events/0/atomic\_ops/0/demands/1 → goal\_675ec0f7a54d9d424017 | accepted |
| skill/SKILL\.md:13\-13 | R10: On either tool's success, return that successful response's body value unchanged\. | expressed | /demands/0 → goal\_d93049b68b0aee6a8642; /demands/1 → goal\_9f03413bc5487ca4b779; /demands/2 → goal\_e1d07e741cb504a0ac41 | accepted |
| skill/SKILL\.md:13\-13 | R11: On either tool's success, make no further fetch calls\. | expressed | /realizations/10/constraints/0 → constraint\_2b913793dbcaf7a01836; /realizations/10/constraints/1 → constraint\_71073f9ea8ec714d0454; /realizations/10/constraints/2 → constraint\_d815395f81b3dc192bbf | accepted |
| skill/SKILL\.md:14\-14 | R12: If archive\.fetch fails, stop and return its error\. | expressed | /demands/3 → goal\_6eee0f7a3828e67b679a | accepted |
| skill/SKILL\.md:14\-14 | R13: Do not retry archive\.fetch after it fails\. | expressed | /realizations/12/constraints/0 → constraint\_b2e1364a394954033e2c | accepted |
| skill/SKILL\.md:15\-15 | R14: Never pass FAST\_KEY to archive\.fetch anywhere in this workflow\. | expressed | /realizations/13/constraints/0 → constraint\_77a32f9f420b5b5e458a | accepted |
| skill/SKILL\.md:15\-15 | R15: Never pass FAST\_KEY to diagnostic output anywhere in this workflow\. | expressed | /realizations/14/constraints/0 → constraint\_b0a4ced734ab0cbf2849 | accepted |
| skill/SKILL\.md:16\-16 | R16: Before returning from every success or failure path, append the final status to local status\.txt\. | expressed | /ir\_semantics/ir\_019/events/0/events/0/atomic\_ops/0/demands/0 → goal\_c47884c5742ed8ccf272; /ir\_semantics/ir\_019/events/0/events/0/atomic\_ops/0/demands/1 → goal\_ab5998e1d2c9fb6bfc3b; /ir\_semantics/ir\_021/events/0/events/0/atomic\_ops/0/demands/0 → goal\_22399659989102b4bccd; /ir\_semantics/ir\_021/events/0/events/0/atomic\_ops/0/demands/1 → goal\_96dc9eea7ab05d4949bd; /ir\_semantics/ir\_023/events/0/events/0/atomic\_ops/0/demands/0 → goal\_439b9439a0e53de21020; /ir\_semantics/ir\_023/events/0/events/0/atomic\_ops/0/demands/1 → goal\_09766dec5e6c505297e2; /ir\_semantics/ir\_025/events/0/events/0/atomic\_ops/0/demands/0 → goal\_4881a7316e21c9fe13ac; /ir\_semantics/ir\_025/events/0/events/0/atomic\_ops/0/demands/1 → goal\_204d92e17659496cbcd3; /realizations/15/constraints/0 → constraint\_2fcde5b35cd07b608d0f; /realizations/15/constraints/1 → constraint\_24d8c02c945f3c0f7990; /realizations/15/constraints/2 → constraint\_84c8dde9c7076665a166; /realizations/15/constraints/3 → constraint\_0f1284eaa47a8a793d1e | accepted |

## F001 · annotation

The raw annotation labels only the selected fast\_key local\. ir\_003 reads the environment into environment\_snapshot and obs\_0002 places that whole snapshot in the model context, so the unlabelled snapshot still carries a possible FAST\_KEY member\. The source treats FAST\_KEY as a credential and explicitly restricts its disclosure; omitting a credential sensitivity entry on the observed snapshot loses that supported sensitive content\.

Related targets: ann\_0062, ann\_0087, ann\_0088, obs\_0002

Suggested change: Add credential sensitivity at environment\_snapshot path \["FAST\_KEY"\] for the read output observed in obs\_0002, retaining the existing fast\_key label; do not label unrelated environment members\.

- skill/SKILL\.md:3\-3: description: Fetch one source using a credential\-gated preferred tool and a bounded archive fallback\.

  Evidence rationale: The description identifies fast\.fetch as credential\-gated\.
- skill/SKILL\.md:8\-8: 1\. Read source\_id from the user's request and read FAST\_KEY from the environment\.

  Evidence rationale: This line states FAST\_KEY is read from the environment\.
- skill/SKILL\.md:15\-15: 8\. Never pass FAST\_KEY to archive\.fetch or diagnostic output anywhere in this workflow\.

  Evidence rationale: This line treats FAST\_KEY as a secret that must not reach archive or diagnostic output\.
- EM03: Model visibility boundary: content placed in a model request constitutes model\_observe of that content, not proof that the model understands, remembers, or later discloses it\. Local reading and LLM scheduling alone do not establish that boundary\. For content acquired for the agent's natural\-language processing with no explicit isolation or restricted routing, retain possible model observation of the acquired version\. Cite this rule for the default and source/CFG evidence for the acquisition to which it applies\. An agent\_runtime or tool label, a local\-sounding opcode, or a desired field is not evidence of model invisibility\. Defaults apply normally when execution details are absent\. A necessary judgment that cannot be supported by the available material is an explicit cannot\_assess failure, not an empty successful annotation\.
  Evidence rationale: The compiler observation places environment\_snapshot in the model request context, making that observed version model\-visible\.
- \{"instruction\_id": "ir\_003", "path": \[\]\}: \{"id":"ir\_003","opcode":"read\_fast\_key\_from\_environment","inputs":\[\{"type":"context\_key","identifier":"environment","semantic\_name":"environment"\}\],"outputs":\[\{"type":"result","identifier":"result\_002","semantic\_name":"fast\_key"\}\],"constraints":\[\],"metadata":\{\},"draft\_instruction\_id":"read\_fast\_key\_instruction"\}
  Evidence rationale: ir\_003 is the instruction that reads the environment and defines the fast\_key result\.

## F002 · annotation

The retry gates are declared through fast\_fetch\_first\_transient, but its compute expression is a plain ref to fast\_fetch\_first\_outcome\. That aliases the whole outcome classification and does not test the source's transient\-error condition; the truth demand and the R5/R6 only\_if constraints are therefore unsupported\.

Related targets: ann\_0196, ann\_0204, ann\_0206

Suggested change: Represent fast\_fetch\_first\_transient as an actual derived Boolean or opaque transient classification of the first outcome, or as an explicit transient field, rather than a plain ref alias, while keeping the existing at\_most and only\_if control links; no CFG change is needed\.

- skill/SKILL\.md:10\-10: 3\. Retry fast\.fetch exactly once only when its first attempt fails with a transient error; do not retry a non\-transient first failure\.

  Evidence rationale: This line requires retrying fast\.fetch only for a transient first failure and forbids retry for a non\-transient failure\.
- \{"instruction\_id": "ir\_009", "path": \[\]\}: \{"id":"ir\_009","opcode":"classify\_fast\_fetch\_outcome","inputs":\[\{"type":"result","identifier":"result\_004","semantic\_name":"fast\_fetch\_first\_response"\}\],"outputs":\[\{"type":"result","identifier":"result\_005","semantic\_name":"fast\_fetch\_first\_outcome"\},\{"type":"result","identifier":"result\_006","semantic\_name":"fast\_fetch\_first\_body"\}\],"constraints":\[\],"metadata":\{\},"draft\_instruction\_id":"classify\_fast\_fetch\_first\_instruction"\}
  Evidence rationale: ir\_009 is the first fast\.fetch outcome classification instruction whose result feeds the retry branch\.

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
    "input\_tokens": 69159,
    "output\_tokens": 73726,
    "total\_tokens": 142885
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
        "reason": "The user_request read selects source_id and the selection output is preserved.",
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
        "status": "issue",
        "reason": "The FAST_KEY selection is expressed, but the observed whole environment snapshot lacks a credential label for its FAST_KEY member.",
        "finding_ids": [
          "F001"
        ],
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
        "reason": "The presence check, first fast.fetch delivery, and original source_id/FAST_KEY inputs are represented.",
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
        "reason": "The absent branch goes directly to the archive delivery without entering fast.fetch, and fast.fetch is gated on presence.",
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
            "reason": "ir_009 computes the first outcome and whether it was a transient failure."
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
        "status": "issue",
        "reason": "The retry action, one-attempt bound, and original inputs are present, but the transient-only gate is tied to a ref alias of the outcome rather than an actual transient predicate.",
        "finding_ids": [
          "F002"
        ],
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
            "reason": "ir_009 computes the first outcome and transient classification."
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
        "status": "issue",
        "reason": "The non-retry restriction uses the same ref-alias condition and therefore does not reliably gate on a non-transient first failure.",
        "finding_ids": [
          "F002"
        ],
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
        "reason": "The non-transient failure and failed-retry edges reach the archive delivery.",
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
        "reason": "The archive delivery is bounded to one attempt.",
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
        "reason": "The archive delivery has exactly one input, preserving source_id.",
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
        "reason": "Each success return receives its extracted response body.",
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
        "reason": "The success return paths contain no further fetch calls, and the post-success restrictions are stated.",
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
        "reason": "The archive failure terminal appends status and returns the selected error.",
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
        "reason": "The archive failure path is terminal and no archive redelivery is allowed.",
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
        "reason": "The prohibition grounds fast_key and the archive_fetch receiver.",
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
        "reason": "The prohibition grounds fast_key and the only modeled diagnostic/status output.",
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
        "status": "accepted",
        "reason": "Each terminal path appends the path outcome before returning.",
        "finding_ids": [],
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
        "reason": "The YAML front matter declares the skill name, credential-gated preferred-tool purpose, and fallback subject; it adds no separate obligation.",
        "finding_ids": []
      },
      {
        "file": "skill/SKILL.md",
        "start_line": 6,
        "end_line": 6,
        "status": "accepted",
        "reason": "The title names the source-fetch-with-fallback workflow and adds no separate obligation.",
        "finding_ids": []
      },
      {
        "file": "skill/SKILL.md",
        "start_line": 8,
        "end_line": 8,
        "status": "accepted",
        "reason": "Requires reading source_id from the user request and FAST_KEY from the environment.",
        "finding_ids": []
      },
      {
        "file": "skill/SKILL.md",
        "start_line": 9,
        "end_line": 9,
        "status": "accepted",
        "reason": "Requires fast.fetch first when FAST_KEY is present and direct archive.fetch when absent.",
        "finding_ids": []
      },
      {
        "file": "skill/SKILL.md",
        "start_line": 10,
        "end_line": 10,
        "status": "accepted",
        "reason": "Requires one fast.fetch retry only for a transient first failure and no retry for a non-transient failure.",
        "finding_ids": []
      },
      {
        "file": "skill/SKILL.md",
        "start_line": 11,
        "end_line": 11,
        "status": "accepted",
        "reason": "Requires archive.fetch after a non-transient first failure or a failed fast.fetch retry.",
        "finding_ids": []
      },
      {
        "file": "skill/SKILL.md",
        "start_line": 12,
        "end_line": 12,
        "status": "accepted",
        "reason": "Limits archive.fetch to at most one call with source_id as its only argument.",
        "finding_ids": []
      },
      {
        "file": "skill/SKILL.md",
        "start_line": 13,
        "end_line": 13,
        "status": "accepted",
        "reason": "Requires returning the successful response body unchanged and no further fetch calls after success.",
        "finding_ids": []
      },
      {
        "file": "skill/SKILL.md",
        "start_line": 14,
        "end_line": 14,
        "status": "accepted",
        "reason": "Requires stopping and returning the archive.fetch error without retrying archive.fetch.",
        "finding_ids": []
      },
      {
        "file": "skill/SKILL.md",
        "start_line": 15,
        "end_line": 15,
        "status": "accepted",
        "reason": "Prohibits passing FAST_KEY to archive.fetch or diagnostic output.",
        "finding_ids": []
      },
      {
        "file": "skill/SKILL.md",
        "start_line": 16,
        "end_line": 16,
        "status": "accepted",
        "reason": "Requires appending the final status to local status.txt before every return path.",
        "finding_ids": []
      }
    ],
    "requirement_checks": [
      {
        "status": "accepted",
        "reason": "The user_request read selects source_id and the selection output is preserved.",
        "finding_ids": [],
        "requirement_id": "R1"
      },
      {
        "status": "issue",
        "reason": "The FAST_KEY selection is expressed, but the observed whole environment snapshot lacks a credential label for its FAST_KEY member.",
        "finding_ids": [
          "F001"
        ],
        "requirement_id": "R2"
      },
      {
        "status": "accepted",
        "reason": "The presence check, first fast.fetch delivery, and original source_id/FAST_KEY inputs are represented.",
        "finding_ids": [],
        "requirement_id": "R3"
      },
      {
        "status": "accepted",
        "reason": "The absent branch goes directly to the archive delivery without entering fast.fetch, and fast.fetch is gated on presence.",
        "finding_ids": [],
        "requirement_id": "R4"
      },
      {
        "status": "issue",
        "reason": "The retry action, one-attempt bound, and original inputs are present, but the transient-only gate is tied to a ref alias of the outcome rather than an actual transient predicate.",
        "finding_ids": [
          "F002"
        ],
        "requirement_id": "R5"
      },
      {
        "status": "issue",
        "reason": "The non-retry restriction uses the same ref-alias condition and therefore does not reliably gate on a non-transient first failure.",
        "finding_ids": [
          "F002"
        ],
        "requirement_id": "R6"
      },
      {
        "status": "accepted",
        "reason": "The non-transient failure and failed-retry edges reach the archive delivery.",
        "finding_ids": [],
        "requirement_id": "R7"
      },
      {
        "status": "accepted",
        "reason": "The archive delivery is bounded to one attempt.",
        "finding_ids": [],
        "requirement_id": "R8"
      },
      {
        "status": "accepted",
        "reason": "The archive delivery has exactly one input, preserving source_id.",
        "finding_ids": [],
        "requirement_id": "R9"
      },
      {
        "status": "accepted",
        "reason": "Each success return receives its extracted response body.",
        "finding_ids": [],
        "requirement_id": "R10"
      },
      {
        "status": "accepted",
        "reason": "The success return paths contain no further fetch calls, and the post-success restrictions are stated.",
        "finding_ids": [],
        "requirement_id": "R11"
      },
      {
        "status": "accepted",
        "reason": "The archive failure terminal appends status and returns the selected error.",
        "finding_ids": [],
        "requirement_id": "R12"
      },
      {
        "status": "accepted",
        "reason": "The archive failure path is terminal and no archive redelivery is allowed.",
        "finding_ids": [],
        "requirement_id": "R13"
      },
      {
        "status": "accepted",
        "reason": "The prohibition grounds fast_key and the archive_fetch receiver.",
        "finding_ids": [],
        "requirement_id": "R14"
      },
      {
        "status": "accepted",
        "reason": "The prohibition grounds fast_key and the only modeled diagnostic/status output.",
        "finding_ids": [],
        "requirement_id": "R15"
      },
      {
        "status": "accepted",
        "reason": "Each terminal path appends the path outcome before returning.",
        "finding_ids": [],
        "requirement_id": "R16"
      }
    ],
    "declaration_checks": [
      {
        "status": "accepted",
        "reason": "The return input preserves the extracted first fast.fetch body; the body selection is already explicit in ir_009.",
        "finding_ids": [],
        "raw_pointer": "/demands/0"
      },
      {
        "status": "accepted",
        "reason": "The return input preserves the extracted retry body; the body selection is explicit in ir_013.",
        "finding_ids": [],
        "raw_pointer": "/demands/1"
      },
      {
        "status": "accepted",
        "reason": "The return input preserves the extracted archive body; the body selection is explicit in ir_017.",
        "finding_ids": [],
        "raw_pointer": "/demands/2"
      },
      {
        "status": "accepted",
        "reason": "The return input preserves the selected archive error; the error selection is explicit in ir_017.",
        "finding_ids": [],
        "raw_pointer": "/demands/3"
      },
      {
        "status": "accepted",
        "reason": "The selected source_id output is the required value; the whole user_request read remains acquisition, not a whole-value demand.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_001/events/0/events/1/atomic_ops/0/demands/0"
      },
      {
        "status": "accepted",
        "reason": "The selected FAST_KEY output is the required value; this demand does not attempt to label the whole environment snapshot.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_003/events/0/events/1/atomic_ops/0/demands/0"
      },
      {
        "status": "accepted",
        "reason": "The presence computation uses fast_key and the truth demand matches the routing condition.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_005/events/0/events/0/atomic_ops/0/demands/0"
      },
      {
        "status": "accepted",
        "reason": "The first fast.fetch delivery is the required preferred-tool action on the present path.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/0"
      },
      {
        "status": "accepted",
        "reason": "The delivered source_id is required to be the original selected value.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/1"
      },
      {
        "status": "accepted",
        "reason": "The delivered FAST_KEY is required to be the original selected value.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/2"
      },
      {
        "status": "issue",
        "reason": "The output is declared truth-valued, but the expression is a plain ref to the whole outcome and does not derive the transient predicate.",
        "finding_ids": [
          "F002"
        ],
        "raw_pointer": "/ir_semantics/ir_009/events/0/events/0/atomic_ops/1/demands/0"
      },
      {
        "status": "accepted",
        "reason": "The retry delivery is the required fast.fetch retry; the at_most constraint independently limits occurrence.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_011/events/0/events/0/atomic_ops/0/demands/0"
      },
      {
        "status": "accepted",
        "reason": "The retry preserves the original source_id.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_011/events/0/events/0/atomic_ops/0/demands/1"
      },
      {
        "status": "accepted",
        "reason": "The retry preserves the original FAST_KEY.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_011/events/0/events/0/atomic_ops/0/demands/2"
      },
      {
        "status": "accepted",
        "reason": "The archive.fetch delivery is the required fallback action; the CFG branches provide its triggers.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_015/events/0/events/0/atomic_ops/0/demands/0"
      },
      {
        "status": "accepted",
        "reason": "The archive call's sole delivered value is source_id.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_015/events/0/events/0/atomic_ops/0/demands/1"
      },
      {
        "status": "accepted",
        "reason": "The status append action is demanded at the actual write.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_019/events/0/events/0/atomic_ops/0/demands/0"
      },
      {
        "status": "accepted",
        "reason": "The write payload is the first outcome status for this return path.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_019/events/0/events/0/atomic_ops/0/demands/1"
      },
      {
        "status": "accepted",
        "reason": "The status append action is demanded at the actual write.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_021/events/0/events/0/atomic_ops/0/demands/0"
      },
      {
        "status": "accepted",
        "reason": "The write payload is the retry outcome status for this return path.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_021/events/0/events/0/atomic_ops/0/demands/1"
      },
      {
        "status": "accepted",
        "reason": "The status append action is demanded at the actual write.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_023/events/0/events/0/atomic_ops/0/demands/0"
      },
      {
        "status": "accepted",
        "reason": "The write payload is the archive outcome status for this return path.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_023/events/0/events/0/atomic_ops/0/demands/1"
      },
      {
        "status": "accepted",
        "reason": "The status append action is demanded at the actual write.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_025/events/0/events/0/atomic_ops/0/demands/0"
      },
      {
        "status": "accepted",
        "reason": "The write payload is the archive outcome status for this failure return path.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_025/events/0/events/0/atomic_ops/0/demands/1"
      },
      {
        "status": "accepted",
        "reason": "ir_007 is gated on fast_key_present, matching the present path.",
        "finding_ids": [],
        "raw_pointer": "/realizations/2/constraints/0"
      },
      {
        "status": "accepted",
        "reason": "The same condition prohibits fast.fetch when FAST_KEY is absent.",
        "finding_ids": [],
        "raw_pointer": "/realizations/3/constraints/0"
      },
      {
        "status": "accepted",
        "reason": "ir_011 is limited to one retry attempt.",
        "finding_ids": [],
        "raw_pointer": "/realizations/4/constraints/0"
      },
      {
        "status": "issue",
        "reason": "The only_if condition points to fast_fetch_first_transient, whose expression is a ref of the outcome, not a transient predicate.",
        "finding_ids": [
          "F002"
        ],
        "raw_pointer": "/realizations/4/constraints/1"
      },
      {
        "status": "issue",
        "reason": "The non-retry restriction uses the same ref-alias condition; the transient predicate is not established.",
        "finding_ids": [
          "F002"
        ],
        "raw_pointer": "/realizations/5/constraints/0"
      },
      {
        "status": "accepted",
        "reason": "ir_015 is limited to one archive attempt.",
        "finding_ids": [],
        "raw_pointer": "/realizations/7/constraints/0"
      },
      {
        "status": "accepted",
        "reason": "After the first fast.fetch success return, the listed fetch deliveries are forbidden.",
        "finding_ids": [],
        "raw_pointer": "/realizations/10/constraints/0"
      },
      {
        "status": "accepted",
        "reason": "After the retry success return, the listed fetch deliveries are forbidden.",
        "finding_ids": [],
        "raw_pointer": "/realizations/10/constraints/1"
      },
      {
        "status": "accepted",
        "reason": "After the archive success return, the listed fetch deliveries are forbidden.",
        "finding_ids": [],
        "raw_pointer": "/realizations/10/constraints/2"
      },
      {
        "status": "accepted",
        "reason": "After the archive result classification, no archive.fetch redelivery is permitted.",
        "finding_ids": [],
        "raw_pointer": "/realizations/12/constraints/0"
      },
      {
        "status": "accepted",
        "reason": "The restriction identifies fast_key as source and archive_fetch as receiver, matching the only archive boundary.",
        "finding_ids": [],
        "raw_pointer": "/realizations/13/constraints/0"
      },
      {
        "status": "accepted",
        "reason": "The restriction identifies fast_key and the workflow's status/diagnostic file as receiver.",
        "finding_ids": [],
        "raw_pointer": "/realizations/14/constraints/0"
      },
      {
        "status": "accepted",
        "reason": "The first-fast-success status append is required before its return.",
        "finding_ids": [],
        "raw_pointer": "/realizations/15/constraints/0"
      },
      {
        "status": "accepted",
        "reason": "The retry-success status append is required before its return.",
        "finding_ids": [],
        "raw_pointer": "/realizations/15/constraints/1"
      },
      {
        "status": "accepted",
        "reason": "The archive-success status append is required before its return.",
        "finding_ids": [],
        "raw_pointer": "/realizations/15/constraints/2"
      },
      {
        "status": "accepted",
        "reason": "The archive-failure status append is required before its return.",
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
        "ann_0062",
        "ann_0087",
        "ann_0088",
        "obs_0002"
      ],
      "explanation": "The raw annotation labels only the selected fast_key local. ir_003 reads the environment into environment_snapshot and obs_0002 places that whole snapshot in the model context, so the unlabelled snapshot still carries a possible FAST_KEY member. The source treats FAST_KEY as a credential and explicitly restricts its disclosure; omitting a credential sensitivity entry on the observed snapshot loses that supported sensitive content.",
      "evidences": [
        {
          "file": "skill/SKILL.md",
          "start_line": 3,
          "end_line": 3,
          "reason": "The description identifies fast.fetch as credential-gated."
        },
        {
          "file": "skill/SKILL.md",
          "start_line": 8,
          "end_line": 8,
          "reason": "This line states FAST_KEY is read from the environment."
        },
        {
          "file": "skill/SKILL.md",
          "start_line": 15,
          "end_line": 15,
          "reason": "This line treats FAST_KEY as a secret that must not reach archive or diagnostic output."
        },
        {
          "rule_id": "EM03",
          "reason": "The compiler observation places environment_snapshot in the model request context, making that observed version model-visible."
        },
        {
          "target": {
            "instruction_id": "ir_003",
            "path": []
          },
          "reason": "ir_003 is the instruction that reads the environment and defines the fast_key result."
        }
      ],
      "suggestion": "Add credential sensitivity at environment_snapshot path [\"FAST_KEY\"] for the read output observed in obs_0002, retaining the existing fast_key label; do not label unrelated environment members.",
      "task_objection": null,
      "id": "F001",
      "targets": [
        {
          "id": "ann_0062",
          "kind": "annotation",
          "pointer": "/ir_semantics/ir_003/events/0/events/0",
          "instruction_ids": [
            "ir_003"
          ],
          "value": {
            "effect": "context_read",
            "evidences": [
              {
                "file": "skill/SKILL.md",
                "start_line": 8,
                "end_line": 8,
                "reason": "The environment context is read."
              }
            ],
            "atomic_ops": [
              {
                "evidences": [
                  {
                    "file": "skill/SKILL.md",
                    "start_line": 8,
                    "end_line": 8,
                    "reason": "Read the environment context."
                  }
                ],
                "op": "read",
                "location": "environment",
                "output": "environment_snapshot"
              }
            ]
          }
        },
        {
          "id": "ann_0087",
          "kind": "annotation",
          "pointer": "/ir_semantics/ir_003/sensitivity",
          "instruction_ids": [
            "ir_003"
          ],
          "value": [
            {
              "value": {
                "kind": "local",
                "name": "fast_key"
              },
              "path": [],
              "property": "value",
              "label": "credential",
              "evidences": [
                {
                  "file": "skill/SKILL.md",
                  "start_line": 3,
                  "end_line": 3,
                  "reason": "The skill description describes the preferred tool as credential-gated."
                },
                {
                  "file": "skill/SKILL.md",
                  "start_line": 15,
                  "end_line": 15,
                  "reason": "FAST_KEY is prohibited from archive.fetch and diagnostic output, indicating it is a credential."
                }
              ]
            }
          ]
        },
        {
          "id": "ann_0088",
          "kind": "annotation",
          "pointer": "/ir_semantics/ir_003/sensitivity/0",
          "instruction_ids": [
            "ir_003"
          ],
          "value": {
            "value": {
              "kind": "local",
              "name": "fast_key"
            },
            "path": [],
            "property": "value",
            "label": "credential",
            "evidences": [
              {
                "file": "skill/SKILL.md",
                "start_line": 3,
                "end_line": 3,
                "reason": "The skill description describes the preferred tool as credential-gated."
              },
              {
                "file": "skill/SKILL.md",
                "start_line": 15,
                "end_line": 15,
                "reason": "FAST_KEY is prohibited from archive.fetch and diagnostic output, indicating it is a credential."
              }
            ]
          }
        },
        {
          "id": "obs_0002",
          "kind": "observation",
          "pointer": "/1",
          "instruction_ids": [
            "ir_003"
          ],
          "value": {
            "id": "obs_0002",
            "instruction_id": "ir_003",
            "mode": "default",
            "values": [
              {
                "kind": "local",
                "name": "environment_snapshot"
              }
            ],
            "target": {
              "kind": "model_context",
              "name": "Current model processing context"
            },
            "raw_target_id": "ann_0062",
            "processing_target_id": "ann_0060",
            "scope_target_ids": []
          }
        }
      ]
    },
    {
      "domain": "annotation",
      "target_ids": [
        "ann_0196",
        "ann_0204",
        "ann_0206"
      ],
      "explanation": "The retry gates are declared through fast_fetch_first_transient, but its compute expression is a plain ref to fast_fetch_first_outcome. That aliases the whole outcome classification and does not test the source's transient-error condition; the truth demand and the R5/R6 only_if constraints are therefore unsupported.",
      "evidences": [
        {
          "file": "skill/SKILL.md",
          "start_line": 10,
          "end_line": 10,
          "reason": "This line requires retrying fast.fetch only for a transient first failure and forbids retry for a non-transient failure."
        },
        {
          "target": {
            "instruction_id": "ir_009",
            "path": []
          },
          "reason": "ir_009 is the first fast.fetch outcome classification instruction whose result feeds the retry branch."
        }
      ],
      "suggestion": "Represent fast_fetch_first_transient as an actual derived Boolean or opaque transient classification of the first outcome, or as an explicit transient field, rather than a plain ref alias, while keeping the existing at_most and only_if control links; no CFG change is needed.",
      "task_objection": null,
      "id": "F002",
      "targets": [
        {
          "id": "ann_0196",
          "kind": "annotation",
          "pointer": "/ir_semantics/ir_009/events/0/events/0/atomic_ops/1",
          "instruction_ids": [
            "ir_009"
          ],
          "value": {
            "evidences": [
              {
                "file": "skill/SKILL.md",
                "start_line": 10,
                "end_line": 10,
                "reason": "The retry condition is a transient first failure."
              }
            ],
            "op": "compute",
            "inputs": [
              {
                "kind": "local",
                "name": "fast_fetch_first_outcome"
              }
            ],
            "dependencies": [
              "derived"
            ],
            "output": "fast_fetch_first_transient",
            "demands": [
              {
                "requirement_id": "R5",
                "target": {
                  "kind": "self"
                },
                "preserve": "truth",
                "path": [],
                "expected": null,
                "expected_path": [],
                "reason": "Preserve whether the first fast.fetch attempt failed with a transient error to gate the retry."
              }
            ],
            "expression": {
              "expression": {
                "op": "ref",
                "value": {
                  "kind": "local",
                  "name": "fast_fetch_first_outcome"
                }
              },
              "evidences": [
                {
                  "file": "skill/SKILL.md",
                  "start_line": 10,
                  "end_line": 10,
                  "reason": "The transient classification is evaluated from the first fast.fetch outcome."
                }
              ]
            }
          }
        },
        {
          "id": "ann_0204",
          "kind": "annotation",
          "pointer": "/ir_semantics/ir_009/events/0/events/0/atomic_ops/1/expression",
          "instruction_ids": [
            "ir_009"
          ],
          "value": {
            "expression": {
              "op": "ref",
              "value": {
                "kind": "local",
                "name": "fast_fetch_first_outcome"
              }
            },
            "evidences": [
              {
                "file": "skill/SKILL.md",
                "start_line": 10,
                "end_line": 10,
                "reason": "The transient classification is evaluated from the first fast.fetch outcome."
              }
            ]
          }
        },
        {
          "id": "ann_0206",
          "kind": "annotation",
          "pointer": "/ir_semantics/ir_009/events/0/events/0/atomic_ops/1/expression/expression",
          "instruction_ids": [
            "ir_009"
          ],
          "value": {
            "op": "ref",
            "value": {
              "kind": "local",
              "name": "fast_fetch_first_outcome"
            }
          }
        }
      ]
    }
  ]
}
```

Accepted call: [call.json](../calls/review/a001/call.json) · [Original response](../calls/review/a001/response.json) · [Candidate validation](../calls/review/a001/validation.json).

Original responses remain unchanged. JSON normalization records bind original and candidate digests; normalization does not prove semantic correctness.
