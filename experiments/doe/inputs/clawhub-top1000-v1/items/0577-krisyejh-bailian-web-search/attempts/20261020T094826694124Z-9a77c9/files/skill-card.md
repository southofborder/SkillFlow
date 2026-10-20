## Description:

Bailian Web Search provides AI-optimized web search through the Bailian (Alibaba ModelStudio) API and returns concise, multisourced results for LLMs.

This skill is ready for commercial/non-commercial use.

## Publisher:

[krisyejh](https://clawhub.ai/user/krisyejh)

### License/Terms of Use:


## Use Case:

Developers and agent builders use this skill to run web searches through Alibaba DashScope/Bailian and return concise web results for LLM workflows.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Search queries are sent to Alibaba DashScope using the user's API key.

Mitigation: Avoid sensitive secrets or private text in search queries, and use the skill only where DashScope data handling is acceptable.

Risk: The DashScope API key is available to the script runtime.

Mitigation: Provide DASHSCOPE_API_KEY through a scoped environment secret and rotate it if the runtime environment may have exposed it.

Risk: The result-count maximum is documented, while the script validates only that count is numeric.

Mitigation: Enforce the documented maximum of 20 in the calling environment when quota, cost, or response-size control matters.

## Reference(s):

- [ClawHub Skill Page](https://clawhub.ai/krisyejh/skills/bailian-web-search)
- [Bailian WebSearch MCP Marketplace](https://bailian.console.aliyun.com/cn-beijing?tab=app#/mcp-market/detail/WebSearch)
- [DashScope WebSearch MCP Endpoint](https://dashscope.aliyuncs.com/api/v1/mcps/WebSearch/mcp)

## Skill Output:

**Output Type(s):** [text, JSON, shell commands, configuration]

**Output Format:** [Terminal stdout containing status text and JSON-formatted MCP responses.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires DASHSCOPE_API_KEY and local bash, curl, and jq; result count defaults to 5 and is documented with a maximum of 20.]

## Skill Version(s):

1.0.4 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
