## Description:

Use when you have a spec or requirements for a multi-step task, before touching code.

This skill is ready for commercial/non-commercial use.

## Publisher:

[zlc000190](https://clawhub.ai/user/zlc000190)

### License/Terms of Use:


## Use Case:

Developers and engineering teams use this skill to turn specifications or requirements into detailed implementation plans before making code changes. It emphasizes file-level tasks, tests, documentation checks, validation commands, and execution handoff choices.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Generated implementation plans may contain incorrect assumptions, weak tests, or unsuitable task sequencing.

Mitigation: Review each plan before execution, especially file paths, test coverage, commands, and handoff choices.

Risk: The skill may guide agents to create plan files and propose later code changes or commits.

Mitigation: Require human approval before using generated plans to modify code, run commands, or create commits.

## Reference(s):

- [Writing Plans ClawHub skill page](https://clawhub.ai/zlc000190/skills/writing-plans)

## Skill Output:

**Output Type(s):** [markdown, guidance, shell commands]

**Output Format:** [Markdown plan with task sections, code blocks, and command examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May direct agents to write plan files under docs/plans and offer follow-on execution workflows.]

## Skill Version(s):

0.1.0 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
