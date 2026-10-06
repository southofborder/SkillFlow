# 026 · R02 Security Profile 助手复核

实际执行状态：`incomplete`。

已逐条复核 22 条标注及 2 项未决。网络效果未决与未知子命令相符；快照、捕获产物及 wrapper 返回处理未见明确相反证据。这不是通用正确性证明。

本记录是助手复核，尚未由用户确认；不计算标注正确率。

## 已检查内容

- 完整阅读 Skill、CLI/workflows 引用、playwright_cli.sh、代理说明、NOTICE、许可证及 SVG 文本，核对 22 条 IR。
- 浏览器 open/交互是否实际联网、snapshot/工具 stdout 的模型可见性、截图/trace 写入与路径返回分别核对。
- wrapper 的参数/环境读取与 npx 执行，不把所有 wrapper 命令机械认定为同一种网络效果。

## 发现与建议

### 1. 未决合理 · ir_013 · effects

interact_with_element_refs 没有指定具体 click/fill/导航行为，wrapper 的 cli_args 也未固定子命令；模型将是否实际远程通信列为未决，并保留 snapshot 的模型观察、捕获产物的文件写入及 wrapper 返回内容的模型观察，没有把所有浏览器动作都强行标成网络发送。

建议：保留网络效果未决，后续传播不能把 effects 空列表理解成无副作用；具体子命令/URL 类型/工具契约明确后再收窄。模型观察目前只说明返回的 CLI 结果可见，不自动证明其引用的所有网页或截图内容可见。

```json
{
  "source_evidence": [
    {
      "file": "SKILL.md",
      "start_line": 67,
      "end_line": 67,
      "quote": "Interact using refs from the latest snapshot."
    },
    {
      "file": "scripts/playwright_cli.sh",
      "start_line": 23,
      "end_line": 23,
      "quote": "cmd+=(\"$@\")"
    }
  ],
  "graph_evidence": [
    {
      "instruction_id": "ir_013",
      "location": "g_0045",
      "pointer": "/blocks/block_007/instructions/0"
    },
    {
      "instruction_id": "ir_021",
      "location": "g_0069",
      "pointer": "/blocks/block_011/instructions/0"
    },
    {
      "instruction_id": "ir_022",
      "location": "g_0070",
      "pointer": "/blocks/block_011/instructions/1"
    }
  ],
  "profile_evidence": {
    "unresolved": [
      {
        "instruction_id": "ir_013",
        "field": "effects",
        "reason": "未给出具体交互命令、输入数据或是否提交/导航，无法确定是否触发远端网络发送或接收。"
      },
      {
        "instruction_id": "ir_021",
        "field": "effects",
        "reason": "cli_args 未指定具体子命令，npx 也可能使用缓存，无法确定是否触发远端网络发送或接收。"
      }
    ],
    "wrapper_return": {
      "actor": [
        "agent_runtime"
      ],
      "roles": [
        "sink"
      ],
      "effects": [
        "model_observe"
      ],
      "evidences": [
        {
          "field": "actor",
          "value": "agent_runtime",
          "basis": "cfg",
          "location": "g_0070",
          "quote": "return",
          "reason": "本地运行时执行 wrapper 返回控制。"
        },
        {
          "field": "roles",
          "value": "sink",
          "basis": "cfg",
          "location": "g_0070",
          "quote": "cli_output",
          "reason": "返回 cli_output，使内容到达调用方或模型边界。"
        },
        {
          "field": "effects",
          "value": "model_observe",
          "basis": "execution_model",
          "location": "EM02",
          "quote": "Agent 工具执行返回的内容默认进入 LLM 上下文",
          "reason": "wrapper 返回的 cli_output 默认进入模型处理上下文。"
        }
      ]
    }
  }
}
```
