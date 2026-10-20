## Description:

Search and analyze your own session logs (older/parent conversations) using jq.

This skill is ready for commercial/non-commercial use.

## Publisher:

[guogang1024](https://clawhub.ai/user/guogang1024)

### License/Terms of Use:


## Use Case:

Agents use this skill when a user authorizes review of prior or parent conversations, so they can locate, extract, and summarize relevant session log content with jq and rg.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Broad searches across saved conversation logs can expose unrelated private messages, secrets, tool outputs, or content from other contexts.

Mitigation: Ask the user to specify the exact session, date, or phrase they authorize and prefer narrow, text-only queries before expanding scope.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/guogang1024/skills/session-logs)
- [Publisher profile](https://clawhub.ai/user/guogang1024)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, guidance]

**Output Format:** [Markdown with inline bash code blocks and concise analysis text]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires local jq and rg; reads user-authorized local session JSONL files.]

## Skill Version(s):

1.0.0 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
