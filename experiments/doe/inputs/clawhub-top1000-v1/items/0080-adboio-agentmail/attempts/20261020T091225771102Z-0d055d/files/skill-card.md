## Description:

AgentMail helps agents create and manage dedicated email inboxes, send and receive messages programmatically, and handle email workflows with webhooks and real-time events.

This skill is ready for commercial/non-commercial use.

## Publisher:

[adboio](https://clawhub.ai/user/adboio)

### License/Terms of Use:


## Use Case:

Developers and agent builders use this skill to give agents email identities, send and receive AgentMail messages, and configure webhook-driven email workflows.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Webhook examples and the test server can expose sensitive email contents, sender identities, or attachments when used with real mail or public tunnels.

Mitigation: Use test inboxes first, keep webhook endpoints private or signature-verified, avoid public tunnels for real mail, and redact email content before sending it to external services.

Risk: Incoming email webhooks can deliver untrusted instructions to an agent.

Mitigation: Use trusted-sender allowlists or route untrusted email to an isolated review session before allowing agent action.

## Reference(s):

- [AgentMail on ClawHub](https://clawhub.ai/adboio/skills/agentmail)
- [AgentMail API Reference](references/API.md)
- [AgentMail Webhooks Guide](references/WEBHOOKS.md)
- [AgentMail Usage Examples](references/EXAMPLES.md)
- [AgentMail Console](https://console.agentmail.to)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance]

**Output Format:** [Markdown with Python snippets, JSON configuration examples, and shell commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May include AgentMail API usage and helper-script commands that require AGENTMAIL_API_KEY.]

## Skill Version(s):

1.1.1 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
