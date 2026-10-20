# Source → Task → declarations whole-chain review

**No material issue reported** · Execution status: `complete`

Review structure, references, evidence and declared coverage passed validation\.

This semantic review does not rewrite the sealed Task, annotation or propagation facts. Accounting coverage of source, Task, demand/constraint declarations and IR does not prove semantic completeness; no reported issue does not prove correct interpretation, minimal demands or absence of DOE.

## Per-requirement semantic correspondence

Expression status and review acceptance do not prove requirement satisfaction. Full source excerpts, remaining gaps and resolved declarations appear in the audit records below.

| Source span | Task requirement | Expression status | Raw demand / constraint | Review record |
| --- | --- | --- | --- | --- |
| skill/references/workflow\.md:5\-5 | R1: Read the user\-supplied request\.json; it contains term and may contain from\_date and limit\. | expressed | /ir\_semantics/ir\_001/events/0/events/0/atomic\_ops/0/demands/0 → goal\_bad3975a1c33c86da8bc | accepted |
| skill/references/workflow\.md:7\-7 | R2: Call index\.search exactly once, using request\.term unchanged as its query argument\. | expressed | /ir\_semantics/ir\_007/events/0/events/1/atomic\_ops/0/demands/0 → goal\_06ba52e6366aa3d27778; /ir\_semantics/ir\_007/events/0/events/1/atomic\_ops/0/demands/1 → goal\_b9704dcab72933209f08; /realizations/1/constraints/0 → constraint\_9009e15876bcfc82d8ad | accepted |
| skill/references/workflow\.md:10\-10 | R3: When from\_date is present in the request, pass its value unchanged as the from\_date argument; the accepted format is YYYY\-MM\-DD\. | expressed | /ir\_semantics/ir\_007/events/0/events/1/atomic\_ops/0/demands/2 → goal\_c25263b0b7055126cef1 | accepted |
| skill/query\.yaml:2\-2; skill/references/workflow\.md:11\-11; skill/references/workflow\.md:15\-15 | R4: When from\_date is missing from the request, omit the from\_date argument from this same index\.search call, applying query\.yaml's missing\-argument setting\. | expressed | /ir\_semantics/ir\_007/events/0/events/0/atomic\_ops/0/demands/0 → goal\_852714501b1884f87090 | accepted |
| skill/references/workflow\.md:12\-12 | R5: When limit is present in the request, pass its value unchanged as the limit argument\. | expressed | /ir\_semantics/ir\_007/events/0/events/1/atomic\_ops/0/demands/3 → goal\_99915fbe3f62e1af0426 | accepted |
| skill/query\.yaml:3\-3; skill/references/workflow\.md:13\-13; skill/references/workflow\.md:15\-15 | R6: When limit is missing from the request, omit the limit argument from this same index\.search call, applying query\.yaml's missing\-argument setting\. | expressed | /ir\_semantics/ir\_007/events/0/events/0/atomic\_ops/0/demands/1 → goal\_da9ae22c3399787be23d | accepted |
| skill/references/workflow\.md:17\-17 | R7: Do not invoke index\.delete anywhere in this workflow\. | retained\_only | No executable declaration | accepted |
| skill/references/workflow\.md:21\-21 | R8: After the search, write the response's total value to local count\.txt\. | expressed | /ir\_semantics/ir\_010/events/0/events/0/atomic\_ops/0/demands/0 → goal\_a68e938e61f1884d7598; /ir\_semantics/ir\_010/events/0/events/0/atomic\_ops/0/demands/1 → goal\_b9a86bc8698a176813fb; /realizations/7/constraints/0 → constraint\_35e3a6a8eec50bad5a08 | accepted |
| skill/references/workflow\.md:23\-23 | R9: Return the search response's items value unchanged\. | expressed | /demands/0 → goal\_6e5ca31142833529f175 | accepted |

This review reported no material issue.

## Audit materials

IR declared reviewed: ir\_001, ir\_002, ir\_003, ir\_004, ir\_005, ir\_006, ir\_007, ir\_008, ir\_009, ir\_010, ir\_011, ir\_012

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
    "input\_tokens": 43933,
    "output\_tokens": 46021,
    "total\_tokens": 89954
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
      "text": "Read the user-supplied request.json; it contains term and may contain from_date and limit.",
      "source_evidence": [
        {
          "reference": "skill/references/workflow.md:5-5",
          "excerpt": "Read the user-supplied request.json, which contains term and may contain from_date and limit.\n",
          "reason": "Imperatively directs reading the supplied request and identifies the request fields that govern the search call."
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
            "reason": "The read_request_json instruction acquires the supplied request.json; term, from_date, and limit are subsequently extracted from that request by the CFG."
          }
        ],
        "gaps": []
      },
      "declarations": [
        {
          "kind": "demand",
          "raw_pointer": "/ir_semantics/ir_001/events/0/events/0/atomic_ops/0/demands/0",
          "goal_id": "goal_bad3975a1c33c86da8bc",
          "requirement_id": "R1",
          "target": {
            "instruction_id": "ir_001",
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
            "requirement_id": "R1",
            "target": {
              "instruction_id": "ir_001",
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
            "reason": "Preserve the required read of the supplied request.json.",
            "id": "goal_bad3975a1c33c86da8bc"
          },
          "resolved_target": {
            "domain": "transfer",
            "kind": "operation",
            "instruction_id": "ir_001",
            "pointer": "/ir_semantics/ir_001/events/0/events/0/atomic_ops/0",
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
            "op": "read",
            "declared_refs": [],
            "output": "request_data"
          }
        }
      ],
      "review_check": {
        "status": "accepted",
        "reason": "The read_request_json instruction reads request_file and later instructions extract term and the optional fields. The whole request acquisition and observation remain actual facts, but no unsupported whole-value task demand is added.",
        "finding_ids": [],
        "requirement_id": "R1"
      }
    },
    {
      "requirement_id": "R2",
      "text": "Call index.search exactly once, using request.term unchanged as its query argument.",
      "source_evidence": [
        {
          "reference": "skill/references/workflow.md:7-7",
          "excerpt": "Call index.search exactly once, using request.term unchanged as its query argument.\n",
          "reason": "States the exact call count, operation, and unchanged term argument in one sentence."
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
            "reason": "The request.term value is selected unchanged from the supplied request for the search call."
          },
          {
            "target": {
              "instruction_id": "ir_007",
              "path": []
            },
            "reason": "The CFG has a single index.search instruction; its build and deliver operations pass the selected term and optional arguments, and the at-most constraint caps the call count at one."
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
                "instruction_id": "ir_007",
                "path": []
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
          "kind": "demand",
          "raw_pointer": "/ir_semantics/ir_007/events/0/events/1/atomic_ops/0/demands/0",
          "goal_id": "goal_06ba52e6366aa3d27778",
          "requirement_id": "R2",
          "target": {
            "instruction_id": "ir_007",
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
              "instruction_id": "ir_007",
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
            "preserve": "action",
            "path": [],
            "expected": null,
            "expected_path": [],
            "reason": "Preserve the single index.search invocation; together with the at-most constraint this covers the exactly-once requirement.",
            "id": "goal_06ba52e6366aa3d27778"
          },
          "resolved_target": {
            "domain": "transfer",
            "kind": "operation",
            "instruction_id": "ir_007",
            "pointer": "/ir_semantics/ir_007/events/0/events/1/atomic_ops/0",
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
              "search_request"
            ],
            "op": "deliver",
            "declared_refs": [
              {
                "kind": "local",
                "name": "search_request"
              }
            ]
          }
        },
        {
          "kind": "demand",
          "raw_pointer": "/ir_semantics/ir_007/events/0/events/1/atomic_ops/0/demands/1",
          "goal_id": "goal_b9704dcab72933209f08",
          "requirement_id": "R2",
          "target": {
            "instruction_id": "ir_007",
            "operation_path": [
              "events",
              0,
              "events",
              1,
              "atomic_ops",
              0
            ],
            "slot": {
              "kind": "input",
              "index": 0
            }
          },
          "goal": {
            "requirement_id": "R2",
            "target": {
              "instruction_id": "ir_007",
              "operation_path": [
                "events",
                0,
                "events",
                1,
                "atomic_ops",
                0
              ],
              "slot": {
                "kind": "input",
                "index": 0
              }
            },
            "preserve": "value",
            "path": [
              "query"
            ],
            "expected": {
              "kind": "input",
              "index": 1
            },
            "expected_path": [],
            "reason": "Preserve request.term unchanged as the query argument.",
            "id": "goal_b9704dcab72933209f08"
          },
          "resolved_target": {
            "domain": "transfer",
            "kind": "input_use",
            "instruction_id": "ir_007",
            "pointer": "/ir_semantics/ir_007/events/0/events/1/atomic_ops/0/uses/0",
            "slot": 0,
            "ref": {
              "kind": "local",
              "name": "search_request"
            },
            "role": "value",
            "when": null,
            "member_index": null,
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
              "search_request"
            ]
          }
        },
        {
          "kind": "constraint",
          "constraint_id": "constraint_9009e15876bcfc82d8ad",
          "requirement_id": "R2",
          "raw_pointer": "/realizations/1/constraints/0"
        }
      ],
      "review_check": {
        "status": "accepted",
        "reason": "The CFG contains one index.search instruction and one unconditional deliver, with query path preserving request.term via query_term; the at-most-one constraint caps further attempts.",
        "finding_ids": [],
        "requirement_id": "R2"
      }
    },
    {
      "requirement_id": "R3",
      "text": "When from_date is present in the request, pass its value unchanged as the from_date argument; the accepted format is YYYY-MM-DD.",
      "source_evidence": [
        {
          "reference": "skill/references/workflow.md:10-10",
          "excerpt": "  - When from_date is present, pass its value unchanged; the accepted format is YYYY-MM-DD.\n",
          "reason": "Specifies the conditional from_date argument, its unchanged value, and accepted format."
        }
      ],
      "realization": {
        "requirement_id": "R3",
        "status": "expressed",
        "bindings": [
          {
            "target": {
              "instruction_id": "ir_004",
              "path": []
            },
            "reason": "The optional from_date value is selected from the request and its presence is computed separately."
          },
          {
            "target": {
              "instruction_id": "ir_007",
              "path": []
            },
            "reason": "The search request from_date member uses the selected value unchanged when the presence flag is true."
          }
        ],
        "gaps": []
      },
      "declarations": [
        {
          "kind": "demand",
          "raw_pointer": "/ir_semantics/ir_007/events/0/events/1/atomic_ops/0/demands/2",
          "goal_id": "goal_c25263b0b7055126cef1",
          "requirement_id": "R3",
          "target": {
            "instruction_id": "ir_007",
            "operation_path": [
              "events",
              0,
              "events",
              1,
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
                1,
                "atomic_ops",
                0
              ],
              "slot": {
                "kind": "input",
                "index": 0
              }
            },
            "preserve": "value",
            "path": [
              "from_date"
            ],
            "expected": {
              "kind": "input",
              "index": 2
            },
            "expected_path": [],
            "reason": "When from_date is present, preserve its value unchanged in the from_date argument.",
            "id": "goal_c25263b0b7055126cef1"
          },
          "resolved_target": {
            "domain": "transfer",
            "kind": "input_use",
            "instruction_id": "ir_007",
            "pointer": "/ir_semantics/ir_007/events/0/events/1/atomic_ops/0/uses/0",
            "slot": 0,
            "ref": {
              "kind": "local",
              "name": "search_request"
            },
            "role": "value",
            "when": null,
            "member_index": null,
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
              "search_request"
            ]
          }
        }
      ],
      "review_check": {
        "status": "accepted",
        "reason": "from_date is selected unchanged and its presence computed separately; the build consumes the value only under the presence condition and the deliver demand preserves the original value relation.",
        "finding_ids": [],
        "requirement_id": "R3"
      }
    },
    {
      "requirement_id": "R4",
      "text": "When from_date is missing from the request, omit the from_date argument from this same index.search call, applying query.yaml's missing-argument setting.",
      "source_evidence": [
        {
          "reference": "skill/query.yaml:2-2",
          "excerpt": "  from_date: omit\n",
          "reason": "Declares the missing from_date setting as omit."
        },
        {
          "reference": "skill/references/workflow.md:11-11",
          "excerpt": "  - When from_date is missing, omit the from_date argument.\n",
          "reason": "Requires omitting from_date when it is missing."
        },
        {
          "reference": "skill/references/workflow.md:15-15",
          "excerpt": "Apply the missing-argument settings in [query configuration](../query.yaml) to this same call.\n",
          "reason": "Requires applying query.yaml missing-argument settings to the same search call."
        }
      ],
      "realization": {
        "requirement_id": "R4",
        "status": "expressed",
        "bindings": [
          {
            "target": {
              "instruction_id": "ir_007",
              "path": []
            },
            "reason": "The build member for from_date has a when control tied to from_date presence, so a missing from_date omits the member and applies the omit setting in query.yaml to this same call."
          }
        ],
        "gaps": []
      },
      "declarations": [
        {
          "kind": "demand",
          "raw_pointer": "/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/0",
          "goal_id": "goal_852714501b1884f87090",
          "requirement_id": "R4",
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
              "kind": "output"
            }
          },
          "goal": {
            "requirement_id": "R4",
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
                "kind": "output"
              }
            },
            "preserve": "presence",
            "path": [
              "from_date"
            ],
            "expected": null,
            "expected_path": [],
            "reason": "The built search request conditionally includes from_date only when the request field is present, so a missing from_date omits this member and applies query.yaml's omit setting to the same call.",
            "id": "goal_852714501b1884f87090"
          },
          "resolved_target": {
            "domain": "transfer",
            "kind": "local_output",
            "instruction_id": "ir_007",
            "pointer": "/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/output",
            "ref": {
              "kind": "local",
              "name": "search_request"
            },
            "scope_path": null,
            "operation_raw_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "available_locals": [
              "search_request"
            ]
          }
        }
      ],
      "review_check": {
        "status": "accepted",
        "reason": "A separate from_date presence Boolean controls the build member, so a missing field omits the argument without using null, and the query.yaml omit setting is applied to this same call.",
        "finding_ids": [],
        "requirement_id": "R4"
      }
    },
    {
      "requirement_id": "R5",
      "text": "When limit is present in the request, pass its value unchanged as the limit argument.",
      "source_evidence": [
        {
          "reference": "skill/references/workflow.md:12-12",
          "excerpt": "  - When limit is present, pass its value unchanged as the limit argument.\n",
          "reason": "Specifies the conditional limit argument and its unchanged value."
        }
      ],
      "realization": {
        "requirement_id": "R5",
        "status": "expressed",
        "bindings": [
          {
            "target": {
              "instruction_id": "ir_005",
              "path": []
            },
            "reason": "The optional limit value is selected from the request and its presence is computed separately."
          },
          {
            "target": {
              "instruction_id": "ir_007",
              "path": []
            },
            "reason": "The search request limit member uses the selected value unchanged when the presence flag is true."
          }
        ],
        "gaps": []
      },
      "declarations": [
        {
          "kind": "demand",
          "raw_pointer": "/ir_semantics/ir_007/events/0/events/1/atomic_ops/0/demands/3",
          "goal_id": "goal_99915fbe3f62e1af0426",
          "requirement_id": "R5",
          "target": {
            "instruction_id": "ir_007",
            "operation_path": [
              "events",
              0,
              "events",
              1,
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
              "instruction_id": "ir_007",
              "operation_path": [
                "events",
                0,
                "events",
                1,
                "atomic_ops",
                0
              ],
              "slot": {
                "kind": "input",
                "index": 0
              }
            },
            "preserve": "value",
            "path": [
              "limit"
            ],
            "expected": {
              "kind": "input",
              "index": 4
            },
            "expected_path": [],
            "reason": "When limit is present, preserve its value unchanged in the limit argument.",
            "id": "goal_99915fbe3f62e1af0426"
          },
          "resolved_target": {
            "domain": "transfer",
            "kind": "input_use",
            "instruction_id": "ir_007",
            "pointer": "/ir_semantics/ir_007/events/0/events/1/atomic_ops/0/uses/0",
            "slot": 0,
            "ref": {
              "kind": "local",
              "name": "search_request"
            },
            "role": "value",
            "when": null,
            "member_index": null,
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
              "search_request"
            ]
          }
        }
      ],
      "review_check": {
        "status": "accepted",
        "reason": "limit is selected unchanged with a separate presence Boolean; the build uses the value only when present, and the deliver demand preserves the original value relation.",
        "finding_ids": [],
        "requirement_id": "R5"
      }
    },
    {
      "requirement_id": "R6",
      "text": "When limit is missing from the request, omit the limit argument from this same index.search call, applying query.yaml's missing-argument setting.",
      "source_evidence": [
        {
          "reference": "skill/query.yaml:3-3",
          "excerpt": "  limit: omit\n",
          "reason": "Declares the missing limit setting as omit."
        },
        {
          "reference": "skill/references/workflow.md:13-13",
          "excerpt": "  - When limit is missing, omit the limit argument.\n",
          "reason": "Requires omitting limit when it is missing."
        },
        {
          "reference": "skill/references/workflow.md:15-15",
          "excerpt": "Apply the missing-argument settings in [query configuration](../query.yaml) to this same call.\n",
          "reason": "Requires applying query.yaml missing-argument settings to the same search call."
        }
      ],
      "realization": {
        "requirement_id": "R6",
        "status": "expressed",
        "bindings": [
          {
            "target": {
              "instruction_id": "ir_007",
              "path": []
            },
            "reason": "The build member for limit has a when control tied to limit presence, so a missing limit omits the member and applies the omit setting in query.yaml to this same call."
          }
        ],
        "gaps": []
      },
      "declarations": [
        {
          "kind": "demand",
          "raw_pointer": "/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/1",
          "goal_id": "goal_da9ae22c3399787be23d",
          "requirement_id": "R6",
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
              "kind": "output"
            }
          },
          "goal": {
            "requirement_id": "R6",
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
                "kind": "output"
              }
            },
            "preserve": "presence",
            "path": [
              "limit"
            ],
            "expected": null,
            "expected_path": [],
            "reason": "The built search request conditionally includes limit only when the request field is present, so a missing limit omits this member and applies query.yaml's omit setting to the same call.",
            "id": "goal_da9ae22c3399787be23d"
          },
          "resolved_target": {
            "domain": "transfer",
            "kind": "local_output",
            "instruction_id": "ir_007",
            "pointer": "/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/output",
            "ref": {
              "kind": "local",
              "name": "search_request"
            },
            "scope_path": null,
            "operation_raw_path": [
              "events",
              0,
              "events",
              0,
              "atomic_ops",
              0
            ],
            "available_locals": [
              "search_request"
            ]
          }
        }
      ],
      "review_check": {
        "status": "accepted",
        "reason": "The limit build member is controlled by the separate limit presence Boolean, so absence causes omission, and the query.yaml omit setting applies to the same search call.",
        "finding_ids": [],
        "requirement_id": "R6"
      }
    },
    {
      "requirement_id": "R7",
      "text": "Do not invoke index.delete anywhere in this workflow.",
      "source_evidence": [
        {
          "reference": "skill/references/workflow.md:17-17",
          "excerpt": "Do not invoke index.delete anywhere in this workflow.\n",
          "reason": "Explicitly prohibits invoking index.delete anywhere in the workflow."
        }
      ],
      "realization": {
        "requirement_id": "R7",
        "status": "retained_only",
        "bindings": [
          {
            "target": {
              "path": [
                "constraints",
                1
              ]
            },
            "reason": "The supplied CFG retains the exact prohibition against invoking index.delete as a graph-level constraint, but there is no index.delete instruction or operation event to target with an executable typed constraint."
          }
        ],
        "gaps": [
          {
            "reason": "The workflow prohibits invoking index.delete anywhere. No index.delete operation exists in the CFG, and the available realization constraint forms cannot attach an arbitrary action prohibition to a non-existent event; the restriction is therefore retained rather than declared as an executable constraint.",
            "evidences": [
              {
                "file": "skill/references/workflow.md",
                "start_line": 17,
                "end_line": 17,
                "reason": "This line explicitly prohibits invoking index.delete anywhere in the workflow."
              }
            ]
          }
        ]
      },
      "declarations": [],
      "review_check": {
        "status": "accepted",
        "reason": "The source prohibition is retained in Task R7 and in the CFG graph-level constraint. With no index.delete event, retained_only with a gap is an honest unsupported restriction rather than a fabricated delete action or demand.",
        "finding_ids": [],
        "requirement_id": "R7"
      }
    },
    {
      "requirement_id": "R8",
      "text": "After the search, write the response's total value to local count.txt.",
      "source_evidence": [
        {
          "reference": "skill/references/workflow.md:21-21",
          "excerpt": "After the search, write the response's total value to local count.txt.\n",
          "reason": "Requires the post-search write of the response total to the specified local file."
        }
      ],
      "realization": {
        "requirement_id": "R8",
        "status": "expressed",
        "bindings": [
          {
            "target": {
              "instruction_id": "ir_009",
              "path": []
            },
            "reason": "The response total is selected from the search response before the write."
          },
          {
            "target": {
              "instruction_id": "ir_010",
              "path": []
            },
            "reason": "The local count.txt write consumes the extracted response total, and the requires-prior constraint preserves the after-search order."
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
                "instruction_id": "ir_007",
                "path": []
              }
            ],
            "after": [
              {
                "instruction_id": "ir_010",
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
          "raw_pointer": "/ir_semantics/ir_010/events/0/events/0/atomic_ops/0/demands/0",
          "goal_id": "goal_a68e938e61f1884d7598",
          "requirement_id": "R8",
          "target": {
            "instruction_id": "ir_010",
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
            "requirement_id": "R8",
            "target": {
              "instruction_id": "ir_010",
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
            "reason": "Preserve the required write to local count.txt.",
            "id": "goal_a68e938e61f1884d7598"
          },
          "resolved_target": {
            "domain": "transfer",
            "kind": "operation",
            "instruction_id": "ir_010",
            "pointer": "/ir_semantics/ir_010/events/0/events/0/atomic_ops/0",
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
          "raw_pointer": "/ir_semantics/ir_010/events/0/events/0/atomic_ops/0/demands/1",
          "goal_id": "goal_b9a86bc8698a176813fb",
          "requirement_id": "R8",
          "target": {
            "instruction_id": "ir_010",
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
            "requirement_id": "R8",
            "target": {
              "instruction_id": "ir_010",
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
            "reason": "The write payload must be the response total value from the CFG total result.",
            "id": "goal_b9a86bc8698a176813fb"
          },
          "resolved_target": {
            "domain": "transfer",
            "kind": "input_use",
            "instruction_id": "ir_010",
            "pointer": "/ir_semantics/ir_010/events/0/events/0/atomic_ops/0/uses/0",
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
          "constraint_id": "constraint_35e3a6a8eec50bad5a08",
          "requirement_id": "R8",
          "raw_pointer": "/realizations/7/constraints/0"
        }
      ],
      "review_check": {
        "status": "accepted",
        "reason": "The response total is selected from search_response, the write consumes that selected total at its payload slot, and the requires-prior constraint places the search before the count.txt write.",
        "finding_ids": [],
        "requirement_id": "R8"
      }
    },
    {
      "requirement_id": "R9",
      "text": "Return the search response's items value unchanged.",
      "source_evidence": [
        {
          "reference": "skill/references/workflow.md:23-23",
          "excerpt": "Return the search response's items value unchanged.\n",
          "reason": "Requires returning the response items value without change."
        }
      ],
      "realization": {
        "requirement_id": "R9",
        "status": "expressed",
        "bindings": [
          {
            "target": {
              "instruction_id": "ir_011",
              "path": []
            },
            "reason": "The response items are selected unchanged from the search response."
          },
          {
            "target": {
              "instruction_id": "ir_012",
              "path": []
            },
            "reason": "The CFG return instruction returns the selected response items input."
          }
        ],
        "gaps": []
      },
      "declarations": [
        {
          "kind": "demand",
          "raw_pointer": "/demands/0",
          "goal_id": "goal_6e5ca31142833529f175",
          "requirement_id": "R9",
          "target": {
            "instruction_id": "ir_012",
            "side": "input",
            "index": 0
          },
          "goal": {
            "requirement_id": "R9",
            "target": {
              "instruction_id": "ir_012",
              "side": "input",
              "index": 0
            },
            "preserve": "value",
            "path": [],
            "expected": null,
            "expected_path": [],
            "reason": "Preserve the search response items value unchanged at the return input.",
            "id": "goal_6e5ca31142833529f175"
          },
          "resolved_target": {
            "domain": "cfg",
            "kind": "input",
            "instruction_id": "ir_012",
            "pointer": "/blocks/block_004/instructions/3/inputs/0",
            "available_locals": [],
            "value": {
              "type": "result",
              "identifier": "result_009",
              "semantic_name": "response_items"
            }
          }
        }
      ],
      "review_check": {
        "status": "accepted",
        "reason": "The response items are selected unchanged from search_response and the ordinary return input preserves that selected response_items value.",
        "finding_ids": [],
        "requirement_id": "R9"
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
        "reason": "The frontmatter supplies the skill name and the one-time catalog query purpose with optional-parameter semantics; it adds no separate operational duty.",
        "finding_ids": []
      },
      {
        "file": "skill/SKILL.md",
        "start_line": 6,
        "end_line": 8,
        "status": "accepted",
        "reason": "The title and the reference to workflow instructions correctly incorporate the referenced workflow; no independent workflow action is omitted.",
        "finding_ids": []
      },
      {
        "file": "skill/query.yaml",
        "start_line": 1,
        "end_line": 3,
        "status": "accepted",
        "reason": "The missing-argument settings require omission of absent from_date and limit arguments, consistent with R4 and R6 and the build conditions.",
        "finding_ids": []
      },
      {
        "file": "skill/references/workflow.md",
        "start_line": 1,
        "end_line": 3,
        "status": "accepted",
        "reason": "The workflow heading and capability note state that fuzzy matching exists but is not requested here; no fuzzy-expansion obligation is created.",
        "finding_ids": []
      },
      {
        "file": "skill/references/workflow.md",
        "start_line": 5,
        "end_line": 5,
        "status": "accepted",
        "reason": "This requires reading the supplied request and identifies term and optional from_date and limit fields, matching R1 and the request-field extraction.",
        "finding_ids": []
      },
      {
        "file": "skill/references/workflow.md",
        "start_line": 7,
        "end_line": 7,
        "status": "accepted",
        "reason": "This requires exactly one index.search call using the unchanged request term, matching R2 without introducing fuzzy expansion or delete actions.",
        "finding_ids": []
      },
      {
        "file": "skill/references/workflow.md",
        "start_line": 9,
        "end_line": 13,
        "status": "accepted",
        "reason": "These argument rules require unchanged present from_date and limit values and omission when missing, matching R3 through R6 and the conditional build.",
        "finding_ids": []
      },
      {
        "file": "skill/references/workflow.md",
        "start_line": 15,
        "end_line": 15,
        "status": "accepted",
        "reason": "This applies the query.yaml missing-argument settings to the same search call, which the build conditions and R4/R6 preserve.",
        "finding_ids": []
      },
      {
        "file": "skill/references/workflow.md",
        "start_line": 17,
        "end_line": 17,
        "status": "accepted",
        "reason": "This explicitly prohibits index.delete; R7 retains it, and the CFG keeps the graph-level prohibition without fabricating a delete event.",
        "finding_ids": []
      },
      {
        "file": "skill/references/workflow.md",
        "start_line": 19,
        "end_line": 19,
        "status": "accepted",
        "reason": "This clarifies that parameter descriptions do not add pre-call validation or normalization requirements; the annotation passes values through without adding such actions.",
        "finding_ids": []
      },
      {
        "file": "skill/references/workflow.md",
        "start_line": 21,
        "end_line": 21,
        "status": "accepted",
        "reason": "This requires writing the search response total to local count.txt after the search, matching R8 and the extracted total payload write.",
        "finding_ids": []
      },
      {
        "file": "skill/references/workflow.md",
        "start_line": 23,
        "end_line": 23,
        "status": "accepted",
        "reason": "This requires returning the search response items unchanged, matching R9 and the selected response_items return input.",
        "finding_ids": []
      }
    ],
    "requirement_checks": [
      {
        "status": "accepted",
        "reason": "The read_request_json instruction reads request_file and later instructions extract term and the optional fields. The whole request acquisition and observation remain actual facts, but no unsupported whole-value task demand is added.",
        "finding_ids": [],
        "requirement_id": "R1"
      },
      {
        "status": "accepted",
        "reason": "The CFG contains one index.search instruction and one unconditional deliver, with query path preserving request.term via query_term; the at-most-one constraint caps further attempts.",
        "finding_ids": [],
        "requirement_id": "R2"
      },
      {
        "status": "accepted",
        "reason": "from_date is selected unchanged and its presence computed separately; the build consumes the value only under the presence condition and the deliver demand preserves the original value relation.",
        "finding_ids": [],
        "requirement_id": "R3"
      },
      {
        "status": "accepted",
        "reason": "A separate from_date presence Boolean controls the build member, so a missing field omits the argument without using null, and the query.yaml omit setting is applied to this same call.",
        "finding_ids": [],
        "requirement_id": "R4"
      },
      {
        "status": "accepted",
        "reason": "limit is selected unchanged with a separate presence Boolean; the build uses the value only when present, and the deliver demand preserves the original value relation.",
        "finding_ids": [],
        "requirement_id": "R5"
      },
      {
        "status": "accepted",
        "reason": "The limit build member is controlled by the separate limit presence Boolean, so absence causes omission, and the query.yaml omit setting applies to the same search call.",
        "finding_ids": [],
        "requirement_id": "R6"
      },
      {
        "status": "accepted",
        "reason": "The source prohibition is retained in Task R7 and in the CFG graph-level constraint. With no index.delete event, retained_only with a gap is an honest unsupported restriction rather than a fabricated delete action or demand.",
        "finding_ids": [],
        "requirement_id": "R7"
      },
      {
        "status": "accepted",
        "reason": "The response total is selected from search_response, the write consumes that selected total at its payload slot, and the requires-prior constraint places the search before the count.txt write.",
        "finding_ids": [],
        "requirement_id": "R8"
      },
      {
        "status": "accepted",
        "reason": "The response items are selected unchanged from search_response and the ordinary return input preserves that selected response_items value.",
        "finding_ids": [],
        "requirement_id": "R9"
      }
    ],
    "declaration_checks": [
      {
        "status": "accepted",
        "reason": "The return input demand targets the actual response_items result selected from the search response and preserves it unchanged as required by R9.",
        "finding_ids": [],
        "raw_pointer": "/demands/0"
      },
      {
        "status": "accepted",
        "reason": "The self action demand on the read operation targets the actual request_file read and does not overstate acquisition as a whole-value content requirement.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_001/events/0/events/0/atomic_ops/0/demands/0"
      },
      {
        "status": "accepted",
        "reason": "The build output path from_date is controlled by the separate presence Boolean, so the member is conditionally present or omitted; this preserves the optional-member semantics without treating the flag as payload.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/0"
      },
      {
        "status": "accepted",
        "reason": "The build output path limit is controlled by the separate limit presence Boolean, preserving conditional inclusion and omission without adding a control member to the request object.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/1"
      },
      {
        "status": "accepted",
        "reason": "The self action demand targets the single deliver operation to index_search; together with the at-most-one constraint it preserves the required single search invocation.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_007/events/0/events/1/atomic_ops/0/demands/0"
      },
      {
        "status": "accepted",
        "reason": "The deliver slot resolves to the local search_request, and path query refers to the build value from query_term, which was selected unchanged from request.term; the expected relation is the original query term.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_007/events/0/events/1/atomic_ops/0/demands/1"
      },
      {
        "status": "accepted",
        "reason": "The deliver path from_date is conditionally consumed by the build when-control, and its expected relation is the unchanged selected from_date_value from the request.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_007/events/0/events/1/atomic_ops/0/demands/2"
      },
      {
        "status": "accepted",
        "reason": "The deliver path limit is conditionally consumed by the build when-control, and its expected relation is the unchanged selected limit_value from the request.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_007/events/0/events/1/atomic_ops/0/demands/3"
      },
      {
        "status": "accepted",
        "reason": "The self action demand targets the actual write operation to count_file, preserving the required count.txt write rather than only an upstream extraction.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_010/events/0/events/0/atomic_ops/0/demands/0"
      },
      {
        "status": "accepted",
        "reason": "The write payload slot resolves to the response_total result from the search response total selection; the expected relation preserves that value as the write payload.",
        "finding_ids": [],
        "raw_pointer": "/ir_semantics/ir_010/events/0/events/0/atomic_ops/0/demands/1"
      },
      {
        "status": "accepted",
        "reason": "The constraint limits the sole index.search instruction to at most one attempt; with the single unconditional deliver, it represents the required exactly-once call cap without inventing additional events.",
        "finding_ids": [],
        "raw_pointer": "/realizations/1/constraints/0"
      },
      {
        "status": "accepted",
        "reason": "The task-scoped requires-prior constraint places the ir_007 search before the ir_010 count.txt write, matching the required after-search write order.",
        "finding_ids": [],
        "raw_pointer": "/realizations/7/constraints/0"
      }
    ]
  },
  "Raw declarations and resolved positions": [
    {
      "kind": "demand",
      "raw_pointer": "/demands/0",
      "goal_id": "goal_6e5ca31142833529f175",
      "requirement_id": "R9",
      "target": {
        "instruction_id": "ir_012",
        "side": "input",
        "index": 0
      },
      "goal": {
        "requirement_id": "R9",
        "target": {
          "instruction_id": "ir_012",
          "side": "input",
          "index": 0
        },
        "preserve": "value",
        "path": [],
        "expected": null,
        "expected_path": [],
        "reason": "Preserve the search response items value unchanged at the return input.",
        "id": "goal_6e5ca31142833529f175"
      },
      "resolved_target": {
        "domain": "cfg",
        "kind": "input",
        "instruction_id": "ir_012",
        "pointer": "/blocks/block_004/instructions/3/inputs/0",
        "available_locals": [],
        "value": {
          "type": "result",
          "identifier": "result_009",
          "semantic_name": "response_items"
        }
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/ir_semantics/ir_001/events/0/events/0/atomic_ops/0/demands/0",
      "goal_id": "goal_bad3975a1c33c86da8bc",
      "requirement_id": "R1",
      "target": {
        "instruction_id": "ir_001",
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
        "requirement_id": "R1",
        "target": {
          "instruction_id": "ir_001",
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
        "reason": "Preserve the required read of the supplied request.json.",
        "id": "goal_bad3975a1c33c86da8bc"
      },
      "resolved_target": {
        "domain": "transfer",
        "kind": "operation",
        "instruction_id": "ir_001",
        "pointer": "/ir_semantics/ir_001/events/0/events/0/atomic_ops/0",
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
        "op": "read",
        "declared_refs": [],
        "output": "request_data"
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/0",
      "goal_id": "goal_852714501b1884f87090",
      "requirement_id": "R4",
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
          "kind": "output"
        }
      },
      "goal": {
        "requirement_id": "R4",
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
            "kind": "output"
          }
        },
        "preserve": "presence",
        "path": [
          "from_date"
        ],
        "expected": null,
        "expected_path": [],
        "reason": "The built search request conditionally includes from_date only when the request field is present, so a missing from_date omits this member and applies query.yaml's omit setting to the same call.",
        "id": "goal_852714501b1884f87090"
      },
      "resolved_target": {
        "domain": "transfer",
        "kind": "local_output",
        "instruction_id": "ir_007",
        "pointer": "/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/output",
        "ref": {
          "kind": "local",
          "name": "search_request"
        },
        "scope_path": null,
        "operation_raw_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "available_locals": [
          "search_request"
        ]
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/demands/1",
      "goal_id": "goal_da9ae22c3399787be23d",
      "requirement_id": "R6",
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
          "kind": "output"
        }
      },
      "goal": {
        "requirement_id": "R6",
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
            "kind": "output"
          }
        },
        "preserve": "presence",
        "path": [
          "limit"
        ],
        "expected": null,
        "expected_path": [],
        "reason": "The built search request conditionally includes limit only when the request field is present, so a missing limit omits this member and applies query.yaml's omit setting to the same call.",
        "id": "goal_da9ae22c3399787be23d"
      },
      "resolved_target": {
        "domain": "transfer",
        "kind": "local_output",
        "instruction_id": "ir_007",
        "pointer": "/ir_semantics/ir_007/events/0/events/0/atomic_ops/0/output",
        "ref": {
          "kind": "local",
          "name": "search_request"
        },
        "scope_path": null,
        "operation_raw_path": [
          "events",
          0,
          "events",
          0,
          "atomic_ops",
          0
        ],
        "available_locals": [
          "search_request"
        ]
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/ir_semantics/ir_007/events/0/events/1/atomic_ops/0/demands/0",
      "goal_id": "goal_06ba52e6366aa3d27778",
      "requirement_id": "R2",
      "target": {
        "instruction_id": "ir_007",
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
          "instruction_id": "ir_007",
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
        "preserve": "action",
        "path": [],
        "expected": null,
        "expected_path": [],
        "reason": "Preserve the single index.search invocation; together with the at-most constraint this covers the exactly-once requirement.",
        "id": "goal_06ba52e6366aa3d27778"
      },
      "resolved_target": {
        "domain": "transfer",
        "kind": "operation",
        "instruction_id": "ir_007",
        "pointer": "/ir_semantics/ir_007/events/0/events/1/atomic_ops/0",
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
          "search_request"
        ],
        "op": "deliver",
        "declared_refs": [
          {
            "kind": "local",
            "name": "search_request"
          }
        ]
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/ir_semantics/ir_007/events/0/events/1/atomic_ops/0/demands/1",
      "goal_id": "goal_b9704dcab72933209f08",
      "requirement_id": "R2",
      "target": {
        "instruction_id": "ir_007",
        "operation_path": [
          "events",
          0,
          "events",
          1,
          "atomic_ops",
          0
        ],
        "slot": {
          "kind": "input",
          "index": 0
        }
      },
      "goal": {
        "requirement_id": "R2",
        "target": {
          "instruction_id": "ir_007",
          "operation_path": [
            "events",
            0,
            "events",
            1,
            "atomic_ops",
            0
          ],
          "slot": {
            "kind": "input",
            "index": 0
          }
        },
        "preserve": "value",
        "path": [
          "query"
        ],
        "expected": {
          "kind": "input",
          "index": 1
        },
        "expected_path": [],
        "reason": "Preserve request.term unchanged as the query argument.",
        "id": "goal_b9704dcab72933209f08"
      },
      "resolved_target": {
        "domain": "transfer",
        "kind": "input_use",
        "instruction_id": "ir_007",
        "pointer": "/ir_semantics/ir_007/events/0/events/1/atomic_ops/0/uses/0",
        "slot": 0,
        "ref": {
          "kind": "local",
          "name": "search_request"
        },
        "role": "value",
        "when": null,
        "member_index": null,
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
          "search_request"
        ]
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/ir_semantics/ir_007/events/0/events/1/atomic_ops/0/demands/2",
      "goal_id": "goal_c25263b0b7055126cef1",
      "requirement_id": "R3",
      "target": {
        "instruction_id": "ir_007",
        "operation_path": [
          "events",
          0,
          "events",
          1,
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
            1,
            "atomic_ops",
            0
          ],
          "slot": {
            "kind": "input",
            "index": 0
          }
        },
        "preserve": "value",
        "path": [
          "from_date"
        ],
        "expected": {
          "kind": "input",
          "index": 2
        },
        "expected_path": [],
        "reason": "When from_date is present, preserve its value unchanged in the from_date argument.",
        "id": "goal_c25263b0b7055126cef1"
      },
      "resolved_target": {
        "domain": "transfer",
        "kind": "input_use",
        "instruction_id": "ir_007",
        "pointer": "/ir_semantics/ir_007/events/0/events/1/atomic_ops/0/uses/0",
        "slot": 0,
        "ref": {
          "kind": "local",
          "name": "search_request"
        },
        "role": "value",
        "when": null,
        "member_index": null,
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
          "search_request"
        ]
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/ir_semantics/ir_007/events/0/events/1/atomic_ops/0/demands/3",
      "goal_id": "goal_99915fbe3f62e1af0426",
      "requirement_id": "R5",
      "target": {
        "instruction_id": "ir_007",
        "operation_path": [
          "events",
          0,
          "events",
          1,
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
          "instruction_id": "ir_007",
          "operation_path": [
            "events",
            0,
            "events",
            1,
            "atomic_ops",
            0
          ],
          "slot": {
            "kind": "input",
            "index": 0
          }
        },
        "preserve": "value",
        "path": [
          "limit"
        ],
        "expected": {
          "kind": "input",
          "index": 4
        },
        "expected_path": [],
        "reason": "When limit is present, preserve its value unchanged in the limit argument.",
        "id": "goal_99915fbe3f62e1af0426"
      },
      "resolved_target": {
        "domain": "transfer",
        "kind": "input_use",
        "instruction_id": "ir_007",
        "pointer": "/ir_semantics/ir_007/events/0/events/1/atomic_ops/0/uses/0",
        "slot": 0,
        "ref": {
          "kind": "local",
          "name": "search_request"
        },
        "role": "value",
        "when": null,
        "member_index": null,
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
          "search_request"
        ]
      }
    },
    {
      "kind": "demand",
      "raw_pointer": "/ir_semantics/ir_010/events/0/events/0/atomic_ops/0/demands/0",
      "goal_id": "goal_a68e938e61f1884d7598",
      "requirement_id": "R8",
      "target": {
        "instruction_id": "ir_010",
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
        "requirement_id": "R8",
        "target": {
          "instruction_id": "ir_010",
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
        "reason": "Preserve the required write to local count.txt.",
        "id": "goal_a68e938e61f1884d7598"
      },
      "resolved_target": {
        "domain": "transfer",
        "kind": "operation",
        "instruction_id": "ir_010",
        "pointer": "/ir_semantics/ir_010/events/0/events/0/atomic_ops/0",
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
      "raw_pointer": "/ir_semantics/ir_010/events/0/events/0/atomic_ops/0/demands/1",
      "goal_id": "goal_b9a86bc8698a176813fb",
      "requirement_id": "R8",
      "target": {
        "instruction_id": "ir_010",
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
        "requirement_id": "R8",
        "target": {
          "instruction_id": "ir_010",
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
        "reason": "The write payload must be the response total value from the CFG total result.",
        "id": "goal_b9a86bc8698a176813fb"
      },
      "resolved_target": {
        "domain": "transfer",
        "kind": "input_use",
        "instruction_id": "ir_010",
        "pointer": "/ir_semantics/ir_010/events/0/events/0/atomic_ops/0/uses/0",
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
      "constraint_id": "constraint_9009e15876bcfc82d8ad",
      "requirement_id": "R2",
      "raw_pointer": "/realizations/1/constraints/0"
    },
    {
      "kind": "constraint",
      "constraint_id": "constraint_35e3a6a8eec50bad5a08",
      "requirement_id": "R8",
      "raw_pointer": "/realizations/7/constraints/0"
    }
  ],
  "Finding targets": []
}
```

Accepted call: [call.json](../calls/review/a001/call.json) · [Original response](../calls/review/a001/response.json) · [Candidate validation](../calls/review/a001/validation.json).

Original responses remain unchanged. JSON normalization records bind original and candidate digests; normalization does not prove semantic correctness.
