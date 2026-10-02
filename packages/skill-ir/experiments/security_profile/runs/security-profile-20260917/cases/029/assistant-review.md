# 029 · R05 Security Profile 助手复核

实际执行状态：`invalid_response`。

完整原始响应因源文引文定位错误而被拒收，接受的 profiles 仍为 0。已逐条阅读未接受候选；以下额外语义观察仅作失败诊断，不作为已接受标注或正确率统计。

本记录是助手复核，尚未由用户确认；不计算标注正确率。

## 已检查内容

- 完整阅读 Linear Skill、MCP transport 配置、许可证及 SVG 文本，核对 62 条 IR 的全分支。
- 明确 streamable_http 远端 MCP；list/get/search 也发送查询，create/update 也返回结果，结果回传模型的隐含观察。
- 配置服务地址不等于已经传出业务数据；用户澄清、结果汇总与普通内部控制分别核对。

## 发现与建议

### 1. 记录失败 · 整例调用 · execution

evidence quote does not match source location src_047；没有经过严格校验接受的整图标注，不能把空 profiles 当作语义漏标，也不能评价该例标注是否正确。

建议：保留本次 invalid_response 与原始完整响应，不手工修引用、不补造已接受 profile，不重发或补跑择优；具体定位错误见后续条目。

```json
{
  "source_evidence": {
    "reviewed_files": [
      "LICENSE.txt",
      "SKILL.md",
      "agents/openai.yaml",
      "assets/linear-small.svg"
    ],
    "source_sha256": "d85f4fc3338e0d31e63343701ac25b3bcaad012ff1ce7534a5feacd7368794c2"
  },
  "graph_evidence": {
    "instruction_count": 62,
    "graph_sha256": "7a3d418576071d8fc03384dc7efd65c49a9024f8ef47b7b4764c5e47e91030a4"
  },
  "profile_evidence": {
    "status": "invalid_response",
    "validation": {
      "status": "failed",
      "instruction_count": 62,
      "profile_count": 0,
      "evidence_count": 0,
      "errors": [
        "evidence quote does not match source location src_047"
      ]
    },
    "counts": {
      "logical_calls": 1,
      "http_attempts": 1,
      "http_retries": 0,
      "http_attempts_observed": true,
      "returned_models": [
        "deepseek-flash"
      ],
      "known_token_usage": {
        "input_tokens": 20450,
        "output_tokens": 53196,
        "total_tokens": 73646
      },
      "record_integrity_errors": []
    },
    "attempts": [
      {
        "attempt": 1,
        "status": "complete",
        "http_status": 200,
        "error_type": null,
        "error": null,
        "done_received": true,
        "finish_reason": "stop",
        "received_bytes": 16717511,
        "partial_content_chars": 42645
      }
    ]
  }
}
```

### 2. 证据不足 · ir_017 · evidences

本条仅诊断未接受的原始响应：完整 JSON 覆盖 62 个 IR，但 12 个写调用将 Execute Linear MCP tool calls 错指 src_047。该单元是 SKILL.md 43–44 行 Step 2 的选择工作流/确认标识，所引文字实际位于第 47 行 Step 3。并非该句话不在源文，而是精确定位不匹配，严格拒收有据。

建议：保持整例 invalid_response 和 0 份接受标注；不手工替换 src_047，不把已有 JSON 覆盖全部 IR 当作可接受结果。

```json
{
  "source_evidence": [
    {
      "file": "SKILL.md",
      "start_line": 47,
      "end_line": 47,
      "quote": "Execute Linear MCP tool calls in logical batches:"
    }
  ],
  "graph_evidence": [
    {
      "instruction_id": "ir_017",
      "location": "g_0049",
      "pointer": "/blocks/block_007/instructions/1"
    }
  ],
  "profile_evidence": {
    "accepted": false,
    "raw_profile_count": 62,
    "source_quote_mismatches": [
      {
        "instruction_id": "ir_017",
        "evidence": {
          "field": "effects",
          "value": "net_send",
          "basis": "source",
          "location": "src_047",
          "quote": "Execute Linear MCP tool calls",
          "reason": "该动作是 Linear MCP 工具调用，请求发往远端。"
        },
        "actual_unit": {
          "id": "src_047",
          "file": "SKILL.md",
          "start_line": 43,
          "end_line": 44
        },
        "actual_unit_text": "### Step 2\nSelect the appropriate workflow (see Practical Workflows below) and identify the Linear MCP tools you will need. Confirm required identifiers (issue ID, project ID, team key) before calling tools."
      },
      {
        "instruction_id": "ir_018",
        "evidence": {
          "field": "effects",
          "value": "net_send",
          "basis": "source",
          "location": "src_047",
          "quote": "Execute Linear MCP tool calls",
          "reason": "该动作是 Linear MCP 工具调用，请求发往远端。"
        },
        "actual_unit": {
          "id": "src_047",
          "file": "SKILL.md",
          "start_line": 43,
          "end_line": 44
        },
        "actual_unit_text": "### Step 2\nSelect the appropriate workflow (see Practical Workflows below) and identify the Linear MCP tools you will need. Confirm required identifiers (issue ID, project ID, team key) before calling tools."
      },
      {
        "instruction_id": "ir_023",
        "evidence": {
          "field": "effects",
          "value": "net_send",
          "basis": "source",
          "location": "src_047",
          "quote": "Execute Linear MCP tool calls",
          "reason": "该动作是 Linear MCP 工具调用，请求发往远端。"
        },
        "actual_unit": {
          "id": "src_047",
          "file": "SKILL.md",
          "start_line": 43,
          "end_line": 44
        },
        "actual_unit_text": "### Step 2\nSelect the appropriate workflow (see Practical Workflows below) and identify the Linear MCP tools you will need. Confirm required identifiers (issue ID, project ID, team key) before calling tools."
      },
      {
        "instruction_id": "ir_028",
        "evidence": {
          "field": "effects",
          "value": "net_send",
          "basis": "source",
          "location": "src_047",
          "quote": "Execute Linear MCP tool calls",
          "reason": "该动作是 Linear MCP 工具调用，请求发往远端。"
        },
        "actual_unit": {
          "id": "src_047",
          "file": "SKILL.md",
          "start_line": 43,
          "end_line": 44
        },
        "actual_unit_text": "### Step 2\nSelect the appropriate workflow (see Practical Workflows below) and identify the Linear MCP tools you will need. Confirm required identifiers (issue ID, project ID, team key) before calling tools."
      },
      {
        "instruction_id": "ir_036",
        "evidence": {
          "field": "effects",
          "value": "net_send",
          "basis": "source",
          "location": "src_047",
          "quote": "Execute Linear MCP tool calls",
          "reason": "该动作是 Linear MCP 工具调用，请求发往远端。"
        },
        "actual_unit": {
          "id": "src_047",
          "file": "SKILL.md",
          "start_line": 43,
          "end_line": 44
        },
        "actual_unit_text": "### Step 2\nSelect the appropriate workflow (see Practical Workflows below) and identify the Linear MCP tools you will need. Confirm required identifiers (issue ID, project ID, team key) before calling tools."
      },
      {
        "instruction_id": "ir_037",
        "evidence": {
          "field": "effects",
          "value": "net_send",
          "basis": "source",
          "location": "src_047",
          "quote": "Execute Linear MCP tool calls",
          "reason": "该动作是 Linear MCP 工具调用，请求发往远端。"
        },
        "actual_unit": {
          "id": "src_047",
          "file": "SKILL.md",
          "start_line": 43,
          "end_line": 44
        },
        "actual_unit_text": "### Step 2\nSelect the appropriate workflow (see Practical Workflows below) and identify the Linear MCP tools you will need. Confirm required identifiers (issue ID, project ID, team key) before calling tools."
      },
      {
        "instruction_id": "ir_038",
        "evidence": {
          "field": "effects",
          "value": "net_send",
          "basis": "source",
          "location": "src_047",
          "quote": "Execute Linear MCP tool calls",
          "reason": "该动作是 Linear MCP 工具调用，请求发往远端。"
        },
        "actual_unit": {
          "id": "src_047",
          "file": "SKILL.md",
          "start_line": 43,
          "end_line": 44
        },
        "actual_unit_text": "### Step 2\nSelect the appropriate workflow (see Practical Workflows below) and identify the Linear MCP tools you will need. Confirm required identifiers (issue ID, project ID, team key) before calling tools."
      },
      {
        "instruction_id": "ir_043",
        "evidence": {
          "field": "effects",
          "value": "net_send",
          "basis": "source",
          "location": "src_047",
          "quote": "Execute Linear MCP tool calls",
          "reason": "该动作是 Linear MCP 工具调用，请求发往远端。"
        },
        "actual_unit": {
          "id": "src_047",
          "file": "SKILL.md",
          "start_line": 43,
          "end_line": 44
        },
        "actual_unit_text": "### Step 2\nSelect the appropriate workflow (see Practical Workflows below) and identify the Linear MCP tools you will need. Confirm required identifiers (issue ID, project ID, team key) before calling tools."
      },
      {
        "instruction_id": "ir_048",
        "evidence": {
          "field": "effects",
          "value": "net_send",
          "basis": "source",
          "location": "src_047",
          "quote": "Execute Linear MCP tool calls",
          "reason": "该动作是 Linear MCP 工具调用，请求发往远端。"
        },
        "actual_unit": {
          "id": "src_047",
          "file": "SKILL.md",
          "start_line": 43,
          "end_line": 44
        },
        "actual_unit_text": "### Step 2\nSelect the appropriate workflow (see Practical Workflows below) and identify the Linear MCP tools you will need. Confirm required identifiers (issue ID, project ID, team key) before calling tools."
      },
      {
        "instruction_id": "ir_053",
        "evidence": {
          "field": "effects",
          "value": "net_send",
          "basis": "source",
          "location": "src_047",
          "quote": "Execute Linear MCP tool calls",
          "reason": "该动作是 Linear MCP 工具调用，请求发往远端。"
        },
        "actual_unit": {
          "id": "src_047",
          "file": "SKILL.md",
          "start_line": 43,
          "end_line": 44
        },
        "actual_unit_text": "### Step 2\nSelect the appropriate workflow (see Practical Workflows below) and identify the Linear MCP tools you will need. Confirm required identifiers (issue ID, project ID, team key) before calling tools."
      },
      {
        "instruction_id": "ir_054",
        "evidence": {
          "field": "effects",
          "value": "net_send",
          "basis": "source",
          "location": "src_047",
          "quote": "Execute Linear MCP tool calls",
          "reason": "该动作是 Linear MCP 工具调用，请求发往远端。"
        },
        "actual_unit": {
          "id": "src_047",
          "file": "SKILL.md",
          "start_line": 43,
          "end_line": 44
        },
        "actual_unit_text": "### Step 2\nSelect the appropriate workflow (see Practical Workflows below) and identify the Linear MCP tools you will need. Confirm required identifiers (issue ID, project ID, team key) before calling tools."
      },
      {
        "instruction_id": "ir_059",
        "evidence": {
          "field": "effects",
          "value": "net_send",
          "basis": "source",
          "location": "src_047",
          "quote": "Execute Linear MCP tool calls",
          "reason": "该动作是 Linear MCP 工具调用，请求发往远端。"
        },
        "actual_unit": {
          "id": "src_047",
          "file": "SKILL.md",
          "start_line": 43,
          "end_line": 44
        },
        "actual_unit_text": "### Step 2\nSelect the appropriate workflow (see Practical Workflows below) and identify the Linear MCP tools you will need. Confirm required identifiers (issue ID, project ID, team key) before calling tools."
      }
    ]
  }
}
```

### 3. 漏标 · ir_014 · roles

本条仅诊断未接受的原始响应：查询动作仅列 source，创建动作仅列 sink，虽然 effects 已承认请求发送和响应接收。例如 ir_014 把 confirmed_identifiers 发到远端并引入问题列表，ir_017 发送创建参数并引入 created cycle；按本轮中性数据边界定义，两类动作都有引入与到达边界的一面，不能仅按业务读/写给单一角色。

建议：后续独立标注按具体请求/返回内容复核多 roles，至少为示例查询补充 sink、创建响应补充 source；不要用 net_send 标签机械映射角色，仍需检查实际输入输出。

```json
{
  "source_evidence": [
    {
      "file": "SKILL.md",
      "start_line": 48,
      "end_line": 48,
      "quote": "Read first (list/get/search) to build context."
    },
    {
      "file": "SKILL.md",
      "start_line": 49,
      "end_line": 49,
      "quote": "Create or update next (issues, projects, labels, comments) with all required fields."
    }
  ],
  "graph_evidence": [
    {
      "instruction_id": "ir_014",
      "location": "g_0042",
      "pointer": "/blocks/block_006/instructions/0"
    },
    {
      "instruction_id": "ir_017",
      "location": "g_0049",
      "pointer": "/blocks/block_007/instructions/1"
    }
  ],
  "profile_evidence": {
    "accepted": false,
    "raw_profiles": {
      "ir_014": {
        "actor": [
          "llm",
          "tool"
        ],
        "roles": [
          "source"
        ],
        "effects": [
          "net_send",
          "net_receive",
          "model_observe"
        ],
        "evidences": [
          {
            "field": "actor",
            "value": "llm",
            "basis": "source",
            "location": "src_048",
            "quote": "Read first (list/get/search) to build context.",
            "reason": "技能要求模型先执行读取工具调用。"
          },
          {
            "field": "actor",
            "value": "tool",
            "basis": "cfg",
            "location": "g_0042",
            "quote": "list_open_issues_for_team",
            "reason": "Linear MCP 工具执行列表动作。"
          },
          {
            "field": "roles",
            "value": "source",
            "basis": "cfg",
            "location": "g_0042",
            "quote": "open issues for target team",
            "reason": "问题数据被引入当前过程。"
          },
          {
            "field": "effects",
            "value": "net_send",
            "basis": "cfg",
            "location": "g_0042",
            "quote": "linear_mcp_server",
            "reason": "向远端 Linear MCP 服务器发送列表请求。"
          },
          {
            "field": "effects",
            "value": "net_receive",
            "basis": "cfg",
            "location": "g_0042",
            "quote": "open issues for target team",
            "reason": "接收远端返回的问题内容。"
          },
          {
            "field": "effects",
            "value": "model_observe",
            "basis": "execution_model",
            "location": "EM02",
            "quote": "Agent 工具执行返回的内容默认进入 LLM 上下文",
            "reason": "工具结果进入模型上下文。"
          }
        ]
      },
      "ir_017": {
        "actor": [
          "llm",
          "tool"
        ],
        "roles": [
          "sink"
        ],
        "effects": [
          "net_send",
          "net_receive",
          "model_observe"
        ],
        "evidences": [
          {
            "field": "actor",
            "value": "llm",
            "basis": "source",
            "location": "src_048",
            "quote": "Create or update next",
            "reason": "技能要求模型执行创建或更新工具调用。"
          },
          {
            "field": "actor",
            "value": "tool",
            "basis": "cfg",
            "location": "g_0049",
            "quote": "create_linear_cycle",
            "reason": "Linear MCP 工具执行创建周期。"
          },
          {
            "field": "roles",
            "value": "sink",
            "basis": "cfg",
            "location": "g_0049",
            "quote": "create_linear_cycle",
            "reason": "创建周期写入 Linear 存储或可见边界。"
          },
          {
            "field": "effects",
            "value": "net_send",
            "basis": "source",
            "location": "src_047",
            "quote": "Execute Linear MCP tool calls",
            "reason": "该动作是 Linear MCP 工具调用，请求发往远端。"
          },
          {
            "field": "effects",
            "value": "net_receive",
            "basis": "cfg",
            "location": "g_0049",
            "quote": "created cycle",
            "reason": "接收创建结果对象。"
          },
          {
            "field": "effects",
            "value": "model_observe",
            "basis": "execution_model",
            "location": "EM02",
            "quote": "Agent 工具执行返回的内容默认进入 LLM 上下文",
            "reason": "工具创建结果进入模型上下文。"
          }
        ]
      }
    }
  }
}
```

### 4. 未决合理 · ir_034 · effects/roles/actor

本条仅诊断未接受的原始响应：suggest_or_apply_redistributions 既可能提出方案，也可能实施变更，原始响应将是否实际网络写入保留未决合理。不过该不确定性还可能影响 tool actor 与 sink role，目前只记在 effects，需要避免把其余字段误看成已完全确定。

建议：后续独立实验保留行为分支未决，并检查其对 actor、roles 的影响；本次保持拒收状态。

```json
{
  "source_evidence": [
    {
      "file": "SKILL.md",
      "start_line": 68,
      "end_line": 68,
      "quote": "suggest or apply redistributions"
    }
  ],
  "graph_evidence": [
    {
      "instruction_id": "ir_034",
      "location": "g_0090",
      "pointer": "/blocks/block_013/instructions/2"
    }
  ],
  "profile_evidence": {
    "accepted": false,
    "raw_profile": {
      "actor": [
        "llm"
      ],
      "roles": [
        "transformer"
      ],
      "effects": [
        "transform",
        "model_observe"
      ],
      "evidences": [
        {
          "field": "actor",
          "value": "llm",
          "basis": "source",
          "location": "src_055",
          "quote": "suggest or apply redistributions",
          "reason": "Team Workload Balance 要求模型生成或应用再分配方案。"
        },
        {
          "field": "roles",
          "value": "transformer",
          "basis": "cfg",
          "location": "g_0090",
          "quote": "suggest_or_apply_redistributions",
          "reason": "基于负载信息生成或应用再分配方案，属于处理与选择。"
        },
        {
          "field": "effects",
          "value": "transform",
          "basis": "cfg",
          "location": "g_0090",
          "quote": "suggest_or_apply_redistributions",
          "reason": "生成或应用再分配结果，属于组合、选择或计算。"
        },
        {
          "field": "effects",
          "value": "model_observe",
          "basis": "execution_model",
          "location": "EM04",
          "quote": "模型实际读取内容并处理时还标注 model_observe",
          "reason": "模型读取负载信息并处理。"
        }
      ]
    },
    "raw_unresolved": [
      {
        "instruction_id": "ir_034",
        "field": "effects",
        "reason": "opcode 为 suggest_or_apply，无法确定本轮是否实际应用到 Linear 存储，故无法确定是否另有 net_send/sink 效果。"
      }
    ]
  }
}
```
