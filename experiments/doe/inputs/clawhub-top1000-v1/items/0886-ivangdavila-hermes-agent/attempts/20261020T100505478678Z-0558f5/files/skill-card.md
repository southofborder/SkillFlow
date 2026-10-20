## Description:

Turn OpenClaw into a learning-loop agent with seeded workspace rules, skill promotion, reflective memory, and proactive maintenance.

This skill is ready for commercial/non-commercial use.

## Publisher:

[ivangdavila](https://clawhub.ai/user/ivangdavila)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and OpenClaw users use this skill to add a local learning loop that retrieves durable operational memory, reflects after significant work, and promotes repeated workflows into stable rules or future skills.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill maintains durable local memory under ~/hermes-agent/, which can accumulate sensitive operational details if used carelessly.

Mitigation: Review ~/hermes-agent/ periodically, avoid storing sensitive details, and use the documented preference options to limit when Hermes behavior is active.

Risk: Workspace seed blocks can change how OpenClaw retrieves memory and reflects after work.

Mitigation: Apply only additive, smallest-section patches after user confirmation, and avoid replacing AGENTS.md, SOUL.md, HEARTBEAT.md, or user persona content.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/ivangdavila/skills/hermes-agent)
- [Skill homepage](https://clawic.com/skills/hermes-agent)
- [Setup guide](artifact/setup.md)
- [Hermes loop](artifact/loop.md)
- [Memory template](artifact/memory-template.md)
- [OpenClaw seed blocks](artifact/openclaw-seed.md)
- [Promotion rules](artifact/promotion.md)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance with inline shell commands and file templates]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Creates and maintains local files under ~/hermes-agent/ and may propose additive workspace seed blocks when the user confirms.]

## Skill Version(s):

1.0.0 (source: frontmatter and server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
