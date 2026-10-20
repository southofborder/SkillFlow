## Description:

Store and retrieve memories using the SuperMemory API. Add content, search memories, and chat with your knowledge base.

This skill is ready for commercial/non-commercial use.

## Publisher:

[clawdbot51-oss](https://clawhub.ai/user/clawdbot51-oss)

### License/Terms of Use:


## Use Case:

External users and developers use this skill to store personal knowledge in SuperMemory, search saved memories, and retrieve relevant memory content through chat-like queries.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill includes an apparent real SuperMemory API key in its setup text.

Mitigation: Do not use the bundled credential; configure a freshly generated key through SUPERMEMORY_API_KEY and rotate any exposed key before release.

Risk: Stored memories and queries are sent to an external SuperMemory API.

Mitigation: Avoid storing passwords, API keys, private keys, regulated data, or confidential content unless the user explicitly intends to send that data to SuperMemory.

Risk: Shell scripts construct JSON payloads from user-provided content.

Mitigation: Review generated requests and prefer serializer-built JSON before using the skill with complex or sensitive input.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/clawdbot51-oss/skills/supermemory)
- [Publisher profile](https://clawhub.ai/user/clawdbot51-oss)
- [SuperMemory documents API endpoint](https://api.supermemory.ai/v3/documents)
- [SuperMemory search API endpoint](https://api.supermemory.ai/v3/search)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance with shell commands and API response text]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires SUPERMEMORY_API_KEY and sends memory content and queries to the SuperMemory API.]

## Skill Version(s):

1.0.0 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
