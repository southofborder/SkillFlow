## Description:

Stop waiting for prompts. Keep working.

This skill is ready for commercial/non-commercial use.

## Publisher:

[ryancampbell](https://clawhub.ai/user/ryancampbell)

### License/Terms of Use:

MIT

## Use Case:

Developers and agent operators use this skill to configure task queues, proactive heartbeat routines, and scheduled work patterns that let agents continue useful work between human prompts.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Persistent unattended scheduled agent work can run without enough safeguards or cleanup guidance.

Mitigation: Enable scheduled runs only intentionally, document how to list and remove scheduled jobs, and set explicit timezone and active-hour limits.

Risk: Autonomous queue work may trigger external messages, agent spawning, destructive changes, or sensitive data access without sufficient human review.

Mitigation: Restrict allowed queued tasks and require confirmation for external communication, agent spawning, destructive operations, and sensitive data access.

## Reference(s):

- [Agent Autonomy Kit ClawHub Release](https://clawhub.ai/ryancampbell/skills/agent-autonomy-kit)
- [Proactive Heartbeat Template](templates/HEARTBEAT.md)
- [Task Queue Template](templates/QUEUE.md)
- [Agent Memory Kit](https://github.com/reflectt/agent-memory-kit)
- [Agent Team Kit](https://github.com/reflectt/agent-team-kit)

## Skill Output:

**Output Type(s):** [Markdown, Shell commands, Configuration, Guidance]

**Output Format:** [Markdown guidance with templates, inline shell commands, and JSON-like configuration examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Includes task queue and heartbeat templates for adapting an agent workspace.]

## Skill Version(s):

1.0.0 (source: frontmatter and server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
