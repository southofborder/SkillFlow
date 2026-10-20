## Description:

Feishu File Sender uploads local files through Feishu OpenAPI and sends them as file messages so OpenClaw agents can deliver generated files back to chat.

This skill is ready for commercial/non-commercial use.

## Publisher:

[ziwenwang28](https://clawhub.ai/user/ziwenwang28)

### License/Terms of Use:

MIT

## Use Case:

Developers and OpenClaw operators use this skill to send agent-generated local files into Feishu chats or to specific Feishu users as downloadable file messages.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Agents can upload any readable local file through Feishu using configured app credentials.

Mitigation: Restrict allowed file paths to generated workspace outputs and require confirmation before sending files outside expected directories.

Risk: Caller-chosen recipients can cause files to be sent to unintended chats or users.

Mitigation: Prefer current-chat delivery and enforce recipient allowlists before broad deployment.

Risk: Feishu app credentials may be too broadly scoped for the intended file-sending workflow.

Mitigation: Verify credential scope before installation and rotate or narrow credentials when they exceed the required permissions.

Risk: Workspace matching can select an unintended agent account if workspace paths overlap.

Mitigation: Fix or review workspace matching before enabling the skill across many agents.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/ziwenwang28/skills/feishu-file-sender)
- [Feishu tenant access token API endpoint](https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal)
- [Feishu file upload API endpoint](https://open.feishu.cn/open-apis/im/v1/files)
- [Feishu message send API endpoint](https://open.feishu.cn/open-apis/im/v1/messages)

## Skill Output:

**Output Type(s):** [Shell commands, Configuration, Guidance]

**Output Format:** [Markdown with shell commands and configuration notes]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May upload a local file and send it as a Feishu file message when executed.]

## Skill Version(s):

1.0.9 (source: server release metadata, skill frontmatter, clawdis.yaml)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
