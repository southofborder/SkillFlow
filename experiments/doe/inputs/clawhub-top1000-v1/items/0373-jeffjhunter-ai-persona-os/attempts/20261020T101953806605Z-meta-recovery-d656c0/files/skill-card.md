## Description:

AI Persona OS provides OpenClaw agents with a persistent persona and memory operating layer, including guided workspace setup, persona templates, heartbeat routines, memory files, channel-routing checks, security guidance, escalation patterns, and learning workflows.

This skill is ready for commercial/non-commercial use.

## Publisher:

[jeffjhunter](https://clawhub.ai/user/jeffjhunter)

### License/Terms of Use:

MIT-0

## Use Case:

External developers and OpenClaw users use this skill to set up and operate a structured AI persona workspace with persistent memory, reusable operating rules, persona selection, guided customization, and maintenance routines.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill asks the agent to use broad local execution and coding/full tools.

Mitigation: Use it only in workspaces where that tool access is appropriate, and review each proposed command before approving it.

Risk: The skill can propose edits to workspace paths, personalized files, and OpenClaw host configuration.

Mitigation: Inspect proposed file paths and config diffs carefully, especially changes to ~/.openclaw/openclaw.json and channel routing settings.

Risk: Persistent memory files can retain sensitive personal data or secrets if users place them there.

Mitigation: Keep secrets out of MEMORY.md, DREAMS.md, daily logs, and generated workspace notes; remove sensitive entries during review.

Risk: Optional cron and heartbeat automation can create recurring agent activity.

Mitigation: Enable scheduled jobs only after confirming the target channel, cadence, and command content match the intended operating model.

## Reference(s):

- [AI Persona OS ClawHub listing](https://clawhub.ai/jeffjhunter/skills/ai-persona-os)
- [AI Persona OS homepage](https://os.aipersonamethod.com)
- [Heartbeat Automation Guide](references/heartbeat-automation.md)
- [Never-Forget Protocol](references/never-forget-protocol.md)
- [Proactive Playbook](references/proactive-playbook.md)
- [Security Patterns](references/security-patterns.md)
- [SOUL.md Maker](references/soul-md-maker.md)
- [Security Note](SECURITY_NOTE.md)

## Skill Output:

**Output Type(s):** [Text, Markdown, Code, Shell commands, Configuration, Guidance]

**Output Format:** [Markdown guidance with inline shell commands and generated workspace files]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Produces agent-facing setup steps, workspace templates, optional configuration guidance, and local audit commands for OpenClaw environments.]

## Skill Version(s):

2.0.0 (source: frontmatter, changelog, server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
