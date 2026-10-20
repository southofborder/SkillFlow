## Description:

OpenClaw skill for designing Telegram Bot API workflows and command-driven conversations using direct HTTPS requests (no SDKs).

This skill is ready for commercial/non-commercial use.

## Publisher:

[codedao12](https://clawhub.ai/user/codedao12)

### License/Terms of Use:


## Use Case:

Developers and bot builders use this skill to design command-first Telegram Bot API workflows, plan webhook or polling update flows, and produce operational checklists for direct HTTPS integrations.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Bot tokens or webhook secrets could be exposed if included in logs, prompts, or committed files.

Mitigation: Provide real secrets only when the agent needs them, avoid logging or committing secret values, and use Telegram webhook secret token headers when possible.

## Reference(s):

- [ClawHub Skill Page](https://clawhub.ai/codedao12/skills/telegram)
- [Telegram Bot API Field Notes](references/telegram-bot-api.md)
- [Telegram Command Playbook](references/telegram-commands-playbook.md)
- [Telegram Request Templates](references/telegram-request-templates.md)
- [Telegram Update Routing](references/telegram-update-routing.md)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Telegram Bots FAQ](https://core.telegram.org/bots/faq)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance with JSON and HTTP request examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May include Telegram Bot API endpoint plans, command routing, update handling checklists, and secret-handling reminders.]

## Skill Version(s):

1.0.1 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
