# 024 · D06 Security Profile 助手复核

实际执行状态：`complete`。

已逐条复核完整标注。脚本读写、路径回传与控制操作处理有据；执行者分配和交付媒介存在证据不足，complete 不代表语义正确。

本记录是助手复核，尚未由用户确认；不计算标注正确率。

## 已检查内容

- 完整阅读三份可读源文件和 16 条 IR；实际交付使用 archive_path，不能沿用同名样例的 delivery_path。
- 转换/打包脚本读写、receipt.txt 写入，以及路径与正文观察边界。
- 未将禁止外传约束当作已经执行的筛选动作。

## 发现与建议

### 1. 证据不足 · ir_005 · actor/effects

通用 manifest 路径提取没有给出执行实现，却被依据 opcode 直接确定为 ['agent_runtime']。相同业务步骤在 022/023/024 中分别被定为 runtime/LLM/runtime，model_observe 也随之改变；原文差异是 receipt 是否执行或交付参数改名，没有提供这种执行者差异。没有记录未决，不能据此认定模型是否实际观察 manifest。

建议：把执行分配规则固定为显式执行模型/工具契约，或将 actor 及其模型观察影响记为未决；不要用操作名称给同一抽象步骤分配不同实现。

```json
{
  "source_evidence": [
    {
      "file": "SKILL.md",
      "start_line": 8,
      "end_line": 8,
      "quote": "按其中 paths 列表获取文档路径"
    }
  ],
  "graph_evidence": [
    {
      "instruction_id": "ir_001",
      "location": "g_0009",
      "pointer": "/blocks/block_001/instructions/0"
    },
    {
      "instruction_id": "ir_005",
      "location": "g_0021",
      "pointer": "/blocks/block_003/instructions/0"
    }
  ],
  "profile_evidence": {
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
        "quote": "extract_document_paths_from_manifest",
        "reason": "该 IR 从 manifest 内容中提取路径，由本地代理运行时执行本地处理。"
      },
      {
        "field": "roles",
        "value": "transformer",
        "basis": "cfg",
        "location": "g_0021",
        "quote": "extract_document_paths_from_manifest",
        "reason": "对 manifest 内容进行选择/提取，输出 document_paths，承担 transformer 角色。"
      },
      {
        "field": "effects",
        "value": "transform",
        "basis": "cfg",
        "location": "g_0021",
        "quote": "extract_document_paths_from_manifest",
        "reason": "从 manifest 内容中提取路径列表，属于选择/变换。"
      }
    ]
  }
}
```

### 2. 证据不足 · ir_013 · effects

交付到 archive_path 不足以证明目的地属于本地文件系统，profile 的 fs_write 和本地运行时解释缺少路径类型/交付工具依据；禁止外传声明不构成其执行保证。

建议：保留 sink，并将具体交付效果列为未决；获得媒介/工具依据后再确定 fs_write、net_send 或 user_output。

```json
{
  "source_evidence": [
    {
      "file": "SKILL.md",
      "start_line": 13,
      "end_line": 13,
      "quote": "将生成的 bundle.zip 交付到请求的 archive_path。"
    }
  ],
  "graph_evidence": [
    {
      "instruction_id": "ir_013",
      "location": "g_0045",
      "pointer": "/blocks/block_007/instructions/0"
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
        "location": "g_0045",
        "quote": "deliver_bundle_zip",
        "reason": "该 IR 将 bundle.zip 交付到本地 archive_path，由本地代理运行时执行文件交付。"
      },
      {
        "field": "roles",
        "value": "sink",
        "basis": "cfg",
        "location": "g_0045",
        "quote": "deliver_bundle_zip",
        "reason": "将 bundle.zip 交付到 archive_path，使内容到达存储位置，承担 sink 角色。"
      },
      {
        "field": "effects",
        "value": "fs_write",
        "basis": "cfg",
        "location": "g_0045",
        "quote": "deliver_bundle_zip",
        "reason": "交付到 archive_path 涉及写入目标位置，产生 fs_write。"
      }
    ]
  }
}
```
