## Description:

Automatically assess task complexity and adjust reasoning level.

This skill is ready for commercial/non-commercial use.

## Publisher:

[enzoricciulli](https://clawhub.ai/user/enzoricciulli)

### License/Terms of Use:


## Use Case:

External users and developers use this skill to have an agent classify incoming requests by complexity and adjust reasoning depth before responding.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill can silently change reasoning behavior across many user messages.

Mitigation: Install only when automatic reasoning changes are desired, and prefer explicit user opt-in for session-level behavior changes.

Risk: The skill can increase token usage by enabling extended reasoning for complex tasks.

Mitigation: Monitor usage after installation and disable the skill or reasoning mode for simple or cost-sensitive workflows.

Risk: The skill can append visual indicators to agent responses without asking.

Mitigation: Confirm the response-formatting behavior is acceptable for the target deployment before release.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/enzoricciulli/skills/adaptive-reasoning)

## Skill Output:

**Output Type(s):** [guidance, configuration]

**Output Format:** [Markdown instructions]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May affect response style by enabling reasoning behavior and appending visual indicators for complex requests.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
