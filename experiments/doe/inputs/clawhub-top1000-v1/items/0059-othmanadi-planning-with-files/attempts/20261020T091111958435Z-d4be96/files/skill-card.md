## Description:

Helps agents manage multi-step work with persistent project planning files and optional lifecycle context hooks.

This skill is ready for commercial/non-commercial use.

## Publisher:

[othmanadi](https://clawhub.ai/user/othmanadi)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and other agent users use this skill to track plans, findings, and progress across multi-step tasks and resume work with project context.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Planning files may expose secrets when their contents are added to agent context.

Mitigation: Do not put secrets in task_plan.md or progress.md.

Risk: Optional session replay can surface prior same-project transcript excerpts.

Mitigation: Use --replay only when surfacing those excerpts is acceptable.

Risk: Gated mode can block an agent from stopping.

Mitigation: Enable gated mode only when stop-blocking behavior is desired.

## Reference(s):

- [Skill documentation](reference.md)
- [Planning examples](examples.md)
- [ClawHub skill page](https://clawhub.ai/othmanadi/skills/planning-with-files)

## Skill Output:

**Output Type(s):** [Markdown, Text, Shell commands]

**Output Format:** [Markdown planning files and text guidance]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [None]

## Skill Version(s):

3.24.0 (source: ClawHub release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
