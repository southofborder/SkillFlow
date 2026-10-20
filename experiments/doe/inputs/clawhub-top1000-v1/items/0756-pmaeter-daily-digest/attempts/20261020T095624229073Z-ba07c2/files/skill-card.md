## Description:

Generates a daily digest from stored memory files, summarizing decisions, lessons, actions, and questions into a dated journal entry.

This skill is ready for commercial/non-commercial use.

## Publisher:

[pmaeter](https://clawhub.ai/user/pmaeter)

### License/Terms of Use:


## Use Case:

Agents and operators use this skill to turn daily memory notes into a structured Markdown journal digest covering decisions, lessons, actions, and questions.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill reads dated memory notes that may contain sensitive personal or project information.

Mitigation: Install and run it only where reading those memory notes is acceptable, and review generated digest files before sharing them.

Risk: Scheduled use creates a new Markdown digest file each day it runs.

Mitigation: Confirm the journals/digest retention and access controls before enabling cron or another scheduler.

## Reference(s):

- [Daily Digest on ClawHub](https://clawhub.ai/pmaeter/skills/daily-digest)
- [README.md](README.md)
- [SKILL.md](SKILL.md)

## Skill Output:

**Output Type(s):** [markdown, files, shell commands, guidance]

**Output Format:** [Markdown file with structured sections]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Creates journals/digest/digest-YYYY-MM-DD.md when the script runs.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
