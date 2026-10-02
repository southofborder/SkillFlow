# 022 · D04 Security Profile 助手复核

实际执行状态：`complete`。

已逐条复核完整标注。脚本读写、路径回传与控制操作处理有据；执行者分配和交付媒介存在证据不足，complete 不代表语义正确。

本记录是助手复核，尚未由用户确认；不计算标注正确率。

## 已检查内容

- 完整读取 SKILL.md 引用的 references/workflow.md 与两个脚本，逐条复核 14 条实际 profile 和全部证据。
- ir_007 正确列出 fs_read/fs_write/transform，并依据 stdout 与 EM02 标 model_observe；该观察只支持产物路径，不证明读取整份文档。
- ir_009 正确依据 ZipFile.write 标读取、组合、写入；ir_013 receipt 为 fs_write；禁止外传声明未被变成额外过滤操作。
- dispatch 及无值 return 未硬贴 transform/user_output；未在没有远程依据时补造 net_send。

## 发现与建议

### 1. 证据不足 · ir_001 · actor/effects

读取 manifest 与后续字段提取没有明确声明由隔离本地程序完成。profile 仅凭 read_manifest_json 名称把执行者确定为 agent_runtime，未说明是否通过工具回传模型，也未记录该分配的不确定性。该假设会影响后续是否建立模型观察边界，不能把没有 model_observe 当作已证明模型不可见。相同执行者推断还出现在 ir_003、ir_005。

建议：明确通用读取/字段提取操作的执行分配规则，或将 actor 及相关模型观察记为未决；若采用工具结果默认回传，应为模型观察给出该操作与 EM02 的联合依据。不要根据 opcode 假设本地隔离。

```json
{
  "source_evidence": [
    {
      "file": "references/workflow.md",
      "start_line": 3,
      "end_line": 3,
      "quote": "读取用户提供的 manifest.json，按其中 paths 列表获取文档路径，并从请求中读取 output_dir 和 delivery_path。"
    }
  ],
  "graph_evidence": [
    {
      "instruction_id": "ir_001",
      "location": "g_0009",
      "pointer": "/blocks/block_001/instructions/0"
    },
    {
      "instruction_id": "ir_003",
      "location": "g_0015",
      "pointer": "/blocks/block_002/instructions/0"
    },
    {
      "instruction_id": "ir_005",
      "location": "g_0021",
      "pointer": "/blocks/block_003/instructions/0"
    }
  ],
  "profile_evidence": {
    "ir_001": {
      "actor": [
        "agent_runtime"
      ],
      "roles": [
        "source"
      ],
      "effects": [
        "fs_read"
      ],
      "evidences": [
        {
          "field": "actor",
          "value": "agent_runtime",
          "basis": "cfg",
          "location": "g_0009",
          "quote": "read_manifest_json",
          "reason": "该读取外部资源的 IR 由本地代理运行时执行。"
        },
        {
          "field": "roles",
          "value": "source",
          "basis": "cfg",
          "location": "g_0009",
          "quote": "manifest.json",
          "reason": "该动作从外部资源 manifest.json 引入 manifest 内容。"
        },
        {
          "field": "effects",
          "value": "fs_read",
          "basis": "cfg",
          "location": "g_0009",
          "quote": "read_manifest_json",
          "reason": "opcode 表示读取 manifest.json 文件内容。"
        }
      ]
    },
    "ir_003": {
      "actor": [
        "agent_runtime"
      ],
      "roles": [
        "source"
      ],
      "effects": [
        "context_read"
      ],
      "evidences": [
        {
          "field": "actor",
          "value": "agent_runtime",
          "basis": "cfg",
          "location": "g_0015",
          "quote": "read_output_dir_and_delivery_path_from_request",
          "reason": "读取请求上下文的动作由本地代理运行时执行。"
        },
        {
          "field": "roles",
          "value": "source",
          "basis": "cfg",
          "location": "g_0015",
          "quote": "output_dir",
          "reason": "该动作从请求上下文引入 output_dir/delivery_path 配置。"
        },
        {
          "field": "effects",
          "value": "context_read",
          "basis": "cfg",
          "location": "g_0015",
          "quote": "read_output_dir_and_delivery_path_from_request",
          "reason": "从请求上下文取得调用者输入。"
        }
      ]
    },
    "ir_005": {
      "actor": [
        "agent_runtime"
      ],
      "roles": [
        "transformer"
      ],
      "effects": [
        "transform"
      ],
      "evidences": [
        {
          "field": "actor",
          "value": "agent_runtime",
          "basis": "cfg",
          "location": "g_0021",
          "quote": "extract_manifest_document_paths",
          "reason": "该提取计算由本地代理运行时执行。"
        },
        {
          "field": "roles",
          "value": "transformer",
          "basis": "cfg",
          "location": "g_0021",
          "quote": "extract_manifest_document_paths",
          "reason": "从 manifest 内容中提取/选择文档路径，属于处理变换。"
        },
        {
          "field": "effects",
          "value": "transform",
          "basis": "cfg",
          "location": "g_0021",
          "quote": "extract_manifest_document_paths",
          "reason": "提取/选择路径属于计算与表示变换。"
        }
      ]
    }
  }
}
```

### 2. 证据不足 · ir_011 · effects

delivery_path 的传输媒介和实现没有给出，原文只要求交付到请求的位置。标签 fs_write 以该句为依据，进一步解释为本地放置/写入，超过了文本明确说明的范围。禁止上传声明也不能证明执行机制必然是本地文件系统。sink 角色有依据，但具体效果应保留未知。

建议：保留交付 sink，外置记录交付媒介未决；只有在路径类型或工具契约明确后才确定 fs_write/net_send/user_output，不用约束声明补成实现保证。

```json
{
  "source_evidence": [
    {
      "file": "references/workflow.md",
      "start_line": 19,
      "end_line": 19,
      "quote": "将生成的 bundle.zip 交付到请求的 delivery_path。"
    },
    {
      "file": "references/workflow.md",
      "start_line": 25,
      "end_line": 25,
      "quote": "整份流程禁止把文档上传到外部服务。"
    }
  ],
  "graph_evidence": [
    {
      "instruction_id": "ir_011",
      "location": "g_0039",
      "pointer": "/blocks/block_006/instructions/0"
    }
  ],
  "profile_evidence": {
    "actor": [
      "agent_runtime"
    ],
    "roles": [
      "sink"
    ],
    "effects": [
      "fs_write"
    ],
    "evidences": [
      {
        "field": "actor",
        "value": "agent_runtime",
        "basis": "cfg",
        "location": "g_0039",
        "quote": "deliver_bundle_zip_to_delivery_path",
        "reason": "本地交付动作由代理运行时执行。"
      },
      {
        "field": "roles",
        "value": "sink",
        "basis": "cfg",
        "location": "g_0039",
        "quote": "requested_delivery_path",
        "reason": "将 bundle.zip 交付到指定路径，使内容到达交付/存储位置。"
      },
      {
        "field": "effects",
        "value": "fs_write",
        "basis": "source",
        "location": "src_011",
        "quote": "将生成的 bundle.zip 交付到请求的 delivery_path。",
        "reason": "交付动作将归档放置/写入请求的 delivery_path。"
      }
    ]
  }
}
```
