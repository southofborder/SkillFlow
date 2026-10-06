# 023 · D05 Security Profile 助手复核

实际执行状态：`complete`。

已逐条复核完整标注。脚本读写、路径回传与控制操作处理有据；执行者分配和交付媒介存在证据不足，complete 不代表语义正确。

本记录是助手复核，尚未由用户确认；不计算标注正确率。

## 已检查内容

- 完整阅读三份可读源文件和 12 条 IR；历史 receipt 示例明确不执行，当前图也没有 receipt 写操作。
- 转换脚本 stdout 是路径；打包脚本实际读文件并写 ZIP，不能把 handle 当内容。
- 交付媒介、隐含模型观察、空 return 与隐私声明/实际动作的区别。

## 发现与建议

### 1. 证据不足 · ir_003 · actor/effects

通用 manifest 路径提取没有给出执行实现，却被依据 opcode 直接确定为 ['llm']。相同业务步骤在 022/023/024 中分别被定为 runtime/LLM/runtime，model_observe 也随之改变；原文差异是 receipt 是否执行或交付参数改名，没有提供这种执行者差异。没有记录未决，不能据此认定模型是否实际观察 manifest。

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
      "instruction_id": "ir_003",
      "location": "g_0015",
      "pointer": "/blocks/block_002/instructions/0"
    }
  ],
  "profile_evidence": {
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
        "basis": "cfg",
        "location": "g_0015",
        "quote": "extract_paths_from_manifest",
        "reason": "从 manifest 数据中提取路径属于 LLM 推理处理。"
      },
      {
        "field": "roles",
        "value": "transformer",
        "basis": "cfg",
        "location": "g_0015",
        "quote": "extract_paths_from_manifest",
        "reason": "选择/提取文档路径，处理输入数据。"
      },
      {
        "field": "effects",
        "value": "transform",
        "basis": "cfg",
        "location": "g_0015",
        "quote": "extract_paths_from_manifest",
        "reason": "从 manifest 中选择并组合出文档路径。"
      },
      {
        "field": "effects",
        "value": "model_observe",
        "basis": "cfg",
        "location": "g_0015",
        "quote": "manifest_data",
        "reason": "输入 manifest_data 进入模型处理上下文以提取路径。"
      }
    ]
  }
}
```

### 2. 证据不足 · ir_011 · effects

交付到 delivery_path 不足以证明目的地属于本地文件系统，profile 的 fs_write 和本地运行时解释缺少路径类型/交付工具依据；禁止外传声明不构成其执行保证。

建议：保留 sink，并将具体交付效果列为未决；获得媒介/工具依据后再确定 fs_write、net_send 或 user_output。

```json
{
  "source_evidence": [
    {
      "file": "SKILL.md",
      "start_line": 13,
      "end_line": 13,
      "quote": "将生成的 bundle.zip 交付到请求的 delivery_path。"
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
        "quote": "deliver_bundle_zip_to_path",
        "reason": "按路径交付文件属于本地运行时文件操作。"
      },
      {
        "field": "roles",
        "value": "sink",
        "basis": "cfg",
        "location": "g_0039",
        "quote": "requested_delivery_path",
        "reason": "使 bundle 内容到达指定交付路径/存储位置。"
      },
      {
        "field": "effects",
        "value": "fs_write",
        "basis": "source",
        "location": "src_003",
        "quote": "交付到请求的 delivery_path",
        "reason": "将 bundle.zip 写入/交付到目标路径。"
      }
    ]
  }
}
```
