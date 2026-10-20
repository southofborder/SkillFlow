## Description:

ByteRover helps agents use the brv CLI to query, search, curate, review, and version-control project memory stored in .brv/context-tree and connected memory providers.

This skill is ready for commercial/non-commercial use.

## Publisher:

[byteroverinc](https://clawhub.ai/user/byteroverinc)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and agents use this skill to retrieve and maintain project memory, including patterns, decisions, architecture rules, local context-tree files, provider setup, history, and optional remote sync workflows.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Project context may be sent to a configured LLM provider during query and curate operations.

Mitigation: Review context before invoking LLM-backed commands, prefer local brv search when synthesis is not needed, and avoid including secrets or sensitive source files.

Risk: The skill can write persistent project memory and change local context history.

Mitigation: Require user approval before curation, review pending operations with brv review, and keep memory changes version controlled.

Risk: Remote sync sends memory to ByteRover cloud and requires authentication.

Mitigation: Use local version control by default and run cloud sync only after confirming the target remote and authentication posture.

Risk: Global CLI installation can execute third-party package code.

Mitigation: Pin or independently verify the byterover-cli package before global installation.

## Reference(s):

- [ClawHub Skill Page](https://clawhub.ai/byteroverinc/skills/byterover)

## Skill Output:

**Output Type(s):** [guidance, shell commands, configuration, markdown, text]

**Output Format:** [Markdown instructions with inline shell command examples and occasional JSON output examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May instruct agents to read, write, review, or sync persistent project memory through the brv CLI.]

## Skill Version(s):

3.3.0 (source: server-resolved release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
