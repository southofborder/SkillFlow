## Description:

Helps agents discover and install relevant skills from the open agent skills ecosystem when users ask for specialized functionality.

This skill is ready for commercial/non-commercial use.

## Publisher:

[breckengan](https://clawhub.ai/user/breckengan)

### License/Terms of Use:


## Use Case:

Developers and agent users use this skill to search for installable skills, compare relevant options, and receive install commands when they need specialized workflows or tools.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill encourages global installation and skipped-confirmation install commands for third-party skills.

Mitigation: Review each skill source before installing it, avoid global installation unless user-level availability is intended, and do not skip confirmation prompts for untrusted or newly discovered packages.

Risk: The security verdict is suspicious because broad activation and unattended installation can expose users to untrusted packages.

Mitigation: Read the skill carefully before use and prefer reviewed, trusted packages for normal workflows.

## Reference(s):

- [Find Skill on ClawHub](https://clawhub.ai/breckengan/skills/find-skill)
- [Skills directory](https://skills.sh/)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, guidance]

**Output Format:** [Markdown with inline shell commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May include skill recommendations, installation commands, and links to skill listings.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
