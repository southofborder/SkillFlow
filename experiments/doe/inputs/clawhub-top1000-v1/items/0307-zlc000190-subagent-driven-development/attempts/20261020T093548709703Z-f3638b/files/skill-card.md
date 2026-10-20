## Description:

Use when executing implementation plans with independent tasks in the current session

This skill is ready for commercial/non-commercial use.

## Publisher:

[zlc000190](https://clawhub.ai/user/zlc000190)

### License/Terms of Use:


## Use Case:

Developers and engineering agents use this skill to execute an existing implementation plan through task-specific subagents, with spec compliance and code quality review gates after each task.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The workflow can lead an agent to carry out file changes, tests, reviews, and commits in a repository.

Mitigation: Start from an isolated worktree or non-main branch and make commit permission explicit before invoking the workflow.

Risk: A task-specific subagent may misread requirements or overbuild if task context is incomplete.

Mitigation: Provide the full task text and scene-setting context, then require spec compliance and code quality review loops before marking the task complete.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/zlc000190/skills/subagent-driven-development)
- [Implementer subagent prompt template](artifact/implementer-prompt.md)
- [Spec compliance reviewer prompt template](artifact/spec-reviewer-prompt.md)
- [Code quality reviewer prompt template](artifact/code-quality-reviewer-prompt.md)

## Skill Output:

**Output Type(s):** [Guidance, Markdown, Code, Shell commands]

**Output Format:** [Markdown workflow guidance and prompt templates]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May lead an agent to modify files, run tests, and create commits when that workflow is explicitly allowed.]

## Skill Version(s):

0.1.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
