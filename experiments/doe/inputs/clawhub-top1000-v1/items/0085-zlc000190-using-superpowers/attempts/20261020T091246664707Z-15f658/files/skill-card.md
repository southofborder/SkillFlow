## Description:

Establishes a skill-loading workflow for agents at the start of conversations, requiring relevant skills to be invoked before responses or clarifying questions.

This skill is ready for commercial/non-commercial use.

## Publisher:

[zlc000190](https://clawhub.ai/user/zlc000190)

### License/Terms of Use:


## Use Case:

Developers and agent operators use this skill to make an agent check for relevant skills before responding or taking action. It is primarily a process-control reminder for skill discovery and invocation.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill broadly forces agent behavior and downstream skill loading across nearly every conversation.

Mitigation: Review before installing and preserve normal instruction priority, safety checks, and user confirmation for sensitive actions.

Risk: The skill can pressure an agent to load and follow other skills too early.

Mitigation: Treat it as a discipline reminder and confirm that any downstream skill is relevant and appropriate before relying on it.

## Reference(s):

- [ClawHub Skill Page](https://clawhub.ai/zlc000190/skills/using-superpowers)
- [Publisher Profile](https://clawhub.ai/user/zlc000190)

## Skill Output:

**Output Type(s):** [Guidance, Markdown]

**Output Format:** [Markdown instructions and workflow guidance]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Directs agent decision flow and may affect when other skills are loaded.]

## Skill Version(s):

0.1.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
