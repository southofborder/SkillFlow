## Description:

Token Optimizer helps OpenClaw users reduce AI spend with model routing, local heartbeat options, prompt caching, session management, and budget controls.

This skill is ready for commercial/non-commercial use.

## Publisher:

[smartpeopleconnected](https://clawhub.ai/user/smartpeopleconnected)

### License/Terms of Use:

MIT

## Use Case:

Developers and OpenClaw users use this skill to analyze token-cost drivers and apply reviewed configuration, prompt, heartbeat, caching, and budget changes for lower AI operating costs.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Persistent OpenClaw configuration and prompt changes can alter model routing, context loading, memory behavior, budgets, and cost-control behavior.

Mitigation: Run the default dry-run preview first, review the diff and generated files, keep the automatic backups, and use apply mode only for intended changes.

Risk: Prompt rules that suppress prior context or prefer cheaper models can reduce correctness for complex, security-sensitive, or high-stakes work.

Mitigation: Review SOUL.md and OPTIMIZATION-RULES.md before adding them to an agent prompt, and override the cheaper-model or reduced-context defaults when task risk requires it.

Risk: Heartbeat provider changes can affect local service expectations and notification behavior.

Mitigation: Review heartbeat provider settings before applying them and verify the resulting OpenClaw configuration after setup.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/smartpeopleconnected/skills/token-optimizer)
- [Publisher profile](https://clawhub.ai/user/smartpeopleconnected)
- [Declared project homepage](https://github.com/smartpeopleconnected/openclaw-token-optimizer)

## Skill Output:

**Output Type(s):** [Text, Markdown, Code, Shell commands, Configuration, Guidance]

**Output Format:** [Markdown guidance with Python CLI commands and JSON configuration templates]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Dry-run preview by default; writes under ~/.openclaw only when apply mode is used.]

## Skill Version(s):

1.0.18 (source: server release evidence, CHANGELOG, skill.json, src/__init__.py)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
