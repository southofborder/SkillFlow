## Description:

Use when completing tasks, implementing major features, or before merging to verify work meets requirements.

This skill is ready for commercial/non-commercial use.

## Publisher:

[zlc000190](https://clawhub.ai/user/zlc000190)

### License/Terms of Use:


## Use Case:

Developers and engineering teams use this skill to request structured code reviews after implementation work, before merges, or when they need an independent check of requirements, code quality, testing, and production readiness.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The workflow can expose git diffs and implementation details to a review subagent.

Mitigation: Use it only with repositories and requirements that are appropriate for the review agent context, and choose the base and head SHAs deliberately.

Risk: The skill may prompt more frequent reviews than a team wants by default.

Mitigation: Tune or override the workflow's review cadence for the team's development process.

## Reference(s):

- [Code Review Agent Template](artifact/code-reviewer.md)
- [ClawHub Skill Page](https://clawhub.ai/zlc000190/skills/requesting-code-review)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, guidance]

**Output Format:** [Markdown guidance with inline bash commands and structured review sections.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Includes placeholders for implementation summary, requirements or plan, base and head git SHAs, and description.]

## Skill Version(s):

0.1.0 (source: release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
