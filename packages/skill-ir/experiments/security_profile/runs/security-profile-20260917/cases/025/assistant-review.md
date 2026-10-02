# 025 · R01 Security Profile 助手复核

实际执行状态：`incomplete`。

已逐条复核 45 条标注与 4 项未决。安装网络效果未决合理；复合动作执行主体有遗漏，最终交付的效果解释仍需补充。

本记录是助手复核，尚未由用户确认；不计算标注正确率。

## 已检查内容

- 完整阅读 PDF Skill、代理说明和许可证，核对 45 条 IR、条件、约束与嵌入命令；二进制图标仅核验边界。
- PDF 渲染/文本抽取涉及读取与变换，输出 PNG/文档涉及写入；视觉检查的模型观察与本地生成文件分开。
- 安装依赖、普通返回、面向用户的缺依赖说明，以及选择文件句柄与读取文件内容的区别。

## 发现与建议

### 1. 漏标 · ir_027 · actor

该复合动作既根据缺陷修改文档又重新渲染，profile 已承认 fs_read、fs_write 和渲染效果，却只列 llm。源文渲染路径明确使用 pdftoppm/Poppler，实际文件读写与重新渲染还需要工具或运行时参与；只列 LLM 会把执行职责缩成模型调度。

建议：对复合 IR 保留模型处理及工具/运行时执行主体，依据当前渲染路径补充相应 actor；不要让 fs_write 被误解为 LLM 本身直接执行。

```json
{
  "source_evidence": [
    {
      "file": "SKILL.md",
      "start_line": 20,
      "end_line": 20,
      "quote": "After each meaningful update, re-render pages and verify alignment, spacing, and legibility."
    },
    {
      "file": "SKILL.md",
      "start_line": 54,
      "end_line": 54,
      "quote": "pdftoppm -png $INPUT_PDF $OUTPUT_PREFIX"
    }
  ],
  "graph_evidence": [
    {
      "instruction_id": "ir_013",
      "location": "g_0045",
      "pointer": "/blocks/block_007/instructions/0"
    },
    {
      "instruction_id": "ir_027",
      "location": "g_0087",
      "pointer": "/blocks/block_014/instructions/0"
    }
  ],
  "profile_evidence": {
    "actor": [
      "llm"
    ],
    "roles": [
      "source",
      "transformer",
      "sink"
    ],
    "effects": [
      "fs_read",
      "fs_write",
      "transform",
      "model_observe"
    ],
    "evidences": [
      {
        "field": "actor",
        "value": "llm",
        "basis": "cfg",
        "location": "g_0087",
        "quote": "apply_meaningful_update_and_re_render",
        "reason": "模型根据缺陷应用更新并触发重新渲染。"
      },
      {
        "field": "roles",
        "value": "source",
        "basis": "cfg",
        "location": "g_0087",
        "quote": "pdf_to_render",
        "reason": "读取待更新 PDF 引入数据。"
      },
      {
        "field": "roles",
        "value": "transformer",
        "basis": "cfg",
        "location": "g_0087",
        "quote": "apply_meaningful_update_and_re_render",
        "reason": "更新并重新渲染。"
      },
      {
        "field": "roles",
        "value": "sink",
        "basis": "cfg",
        "location": "g_0087",
        "quote": "re_render",
        "reason": "写出更新后的 PDF/渲染结果。"
      },
      {
        "field": "effects",
        "value": "fs_read",
        "basis": "cfg",
        "location": "g_0087",
        "quote": "pdf_to_render",
        "reason": "读取待更新 PDF。"
      },
      {
        "field": "effects",
        "value": "fs_write",
        "basis": "cfg",
        "location": "g_0087",
        "quote": "apply_meaningful_update_and_re_render",
        "reason": "修改 PDF 并生成渲染文件。"
      },
      {
        "field": "effects",
        "value": "transform",
        "basis": "cfg",
        "location": "g_0087",
        "quote": "apply_meaningful_update_and_re_render",
        "reason": "更新/渲染属于变换。"
      },
      {
        "field": "effects",
        "value": "model_observe",
        "basis": "execution_model",
        "location": "EM04",
        "quote": "模型实际读取内容并处理时还标注 model_observe",
        "reason": "模型处理视觉缺陷并生成最终检查发现。"
      }
    ]
  }
}
```

### 2. 未决合理 · ir_017 · effects

四个安装动作保留本地写入及结果回传，将 net_send/net_receive 外置为未决。原图没有网络仓库、缓存状态或安装工具通信契约，不能仅据安装命令断言每次都发生网络通信。

建议：保留未决；后续工具契约可描述可能联网与缓存分支，但不得把目前未标网络效果当作确定无网络。

```json
{
  "source_evidence": [
    {
      "file": "SKILL.md",
      "start_line": 41,
      "end_line": 41,
      "quote": "brew install poppler"
    },
    {
      "file": "SKILL.md",
      "start_line": 32,
      "end_line": 32,
      "quote": "uv pip install reportlab pdfplumber pypdf"
    }
  ],
  "graph_evidence": [
    {
      "instruction_id": "ir_017",
      "location": "g_0057",
      "pointer": "/blocks/block_009/instructions/0"
    },
    {
      "instruction_id": "ir_019",
      "location": "g_0063",
      "pointer": "/blocks/block_010/instructions/0"
    },
    {
      "instruction_id": "ir_037",
      "location": "g_0117",
      "pointer": "/blocks/block_019/instructions/0"
    },
    {
      "instruction_id": "ir_039",
      "location": "g_0123",
      "pointer": "/blocks/block_020/instructions/0"
    }
  ],
  "profile_evidence": {
    "unresolved": [
      {
        "instruction_id": "ir_017",
        "field": "effects",
        "reason": "安装命令未明确记录远程通信，无法确定是否产生 net_send/net_receive"
      },
      {
        "instruction_id": "ir_019",
        "field": "effects",
        "reason": "安装命令未明确记录远程通信，无法确定是否产生 net_send/net_receive"
      },
      {
        "instruction_id": "ir_037",
        "field": "effects",
        "reason": "安装命令未明确记录远程通信，无法确定是否产生 net_send/net_receive"
      },
      {
        "instruction_id": "ir_039",
        "field": "effects",
        "reason": "安装命令未明确记录远程通信，无法确定是否产生 net_send/net_receive"
      }
    ]
  }
}
```

### 3. 证据不足 · ir_034 · effects

最终 delivery_summary 返回被直接套用普通 return 规则清空 effects。EM06 只排除仅凭 opcode 推断用户输出，不能替代检查整个交付上下文。当前原文有交付与总结要求，块也组织了最终交付，至少应解释接收方是否已明确；现有证据只引用 return，没有处理该上下文。

建议：结合原文交付上下文判断最终输出边界；若接收方仍未确定则明确未决，不能仅用 EM06 把所有 return 都当成无用户输出。

```json
{
  "source_evidence": [
    {
      "file": "SKILL.md",
      "start_line": 65,
      "end_line": 65,
      "quote": "Do not deliver until the latest PNG inspection shows zero visual or formatting defects."
    },
    {
      "file": "agents/openai.yaml",
      "start_line": 5,
      "end_line": 5,
      "quote": "Create, edit, or review this PDF and summarize the key output or changes."
    }
  ],
  "graph_evidence": [
    {
      "instruction_id": "ir_033",
      "location": "g_0105",
      "pointer": "/blocks/block_017/instructions/0"
    },
    {
      "instruction_id": "ir_034",
      "location": "g_0106",
      "pointer": "/blocks/block_017/instructions/1"
    }
  ],
  "profile_evidence": {
    "actor": [
      "agent_runtime"
    ],
    "roles": [
      "sink"
    ],
    "effects": [],
    "evidences": [
      {
        "field": "actor",
        "value": "agent_runtime",
        "basis": "cfg",
        "location": "g_0106",
        "quote": "return",
        "reason": "返回控制/结果由运行时处理。"
      },
      {
        "field": "roles",
        "value": "sink",
        "basis": "cfg",
        "location": "g_0106",
        "quote": "return",
        "reason": "将 delivery_summary 返回调用边界。"
      },
      {
        "field": "effects",
        "value": null,
        "basis": "execution_model",
        "location": "EM06",
        "quote": "普通 return 不能单独证明面向用户输出",
        "reason": "普通 return 未记录其他效果，且不能单独标 user_output。"
      }
    ]
  }
}
```
