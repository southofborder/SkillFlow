## Description:

Start every day focused. Get a morning briefing with overdue tasks, today's priorities, calendar overview, and context from recent meetings. Works with ai-meeting-notes to-do list. No setup. Just say 'briefing'.

This skill is ready for commercial/non-commercial use.

## Publisher:

[jeffjhunter](https://clawhub.ai/user/jeffjhunter)

### License/Terms of Use:


## Use Case:

External users use this skill to ask an agent for a concise daily or weekly briefing from available to-do, meeting-note, calendar, and memory context. It helps surface overdue items, today's priorities, schedule context, and one focus recommendation.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Briefings may expose sensitive information from to-do lists, recent meeting notes, calendar entries, and memory or profile files.

Mitigation: Install only when this data access is acceptable, keep sensitive details out of memory/profile files, and disable those sources when the agent supports it.

Risk: Broad trigger phrases may cause the skill to gather context when the user did not intend a full briefing.

Mitigation: Prefer explicit invocations such as 'daily briefing' and review the produced briefing before acting on it.

## Reference(s):

- [AI Daily Briefing ClawHub listing](https://clawhub.ai/jeffjhunter/skills/ai-daily-briefing)
- [Quick Start](examples/quick-start.md)
- [Example Output: Daily Briefing](examples/output-example.md)
- [Briefing Preferences](assets/PREFERENCES-template.md)
- [Creator homepage](https://jeffjhunter.com)

## Skill Output:

**Output Type(s):** [Text, Markdown, Guidance]

**Output Format:** [Markdown briefing with structured sections]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May include overdue items, priorities, calendar entries, recent-meeting context, weekly previews, or setup guidance depending on available user context.]

## Skill Version(s):

1.0.0 (source: frontmatter and server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
