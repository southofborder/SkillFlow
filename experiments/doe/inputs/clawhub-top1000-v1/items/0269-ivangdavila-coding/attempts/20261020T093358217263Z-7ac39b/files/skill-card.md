## Description:

Coding style memory that adapts to your preferences, conventions, and patterns for consistent coding.

This skill is ready for commercial/non-commercial use.

## Publisher:

[ivangdavila](https://clawhub.ai/user/ivangdavila)

### License/Terms of Use:


## Use Case:

Developers use this skill to let an agent remember explicitly confirmed coding preferences, organize them in local memory files, and apply them consistently to future coding work.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill maintains persistent local coding-preference memory.

Mitigation: Store only preferences the user explicitly confirms, avoid sensitive data, and let users inspect or delete entries on request.

Risk: Security evidence says criteria.md incorrectly directs agents to update the skill instructions themselves.

Mitigation: Treat criteria.md as needing correction or review before use; preference updates should target ~/coding/memory.md, not SKILL.md.

Risk: Unconfirmed or inferred preferences can cause unwanted coding behavior.

Mitigation: Require explicit confirmation before saving any preference and do not infer preferences from project files, silence, or observation.

## Reference(s):

- [Coding skill page](https://clawhub.ai/ivangdavila/skills/coding)
- [Publisher profile](https://clawhub.ai/user/ivangdavila)
- [Coding homepage](https://clawic.com/skills/coding)
- [criteria.md](artifact/criteria.md)
- [dimensions.md](artifact/dimensions.md)
- [memory-template.md](artifact/memory-template.md)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Guidance]

**Output Format:** [Markdown with concise text and inline shell commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May create or update local preference files under ~/coding/ after explicit user confirmation.]

## Skill Version(s):

1.0.3 (source: frontmatter and server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
