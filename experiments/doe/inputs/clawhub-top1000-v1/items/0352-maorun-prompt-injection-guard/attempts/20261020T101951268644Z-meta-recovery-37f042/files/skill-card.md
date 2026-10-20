## Description:

Prompt injection defense. Detect and block malicious prompts, protect system instructions, sanitize user input.

This skill is ready for commercial/non-commercial use.

## Publisher:

[maorun](https://clawhub.ai/user/maorun)

### License/Terms of Use:


## Use Case:

Agents and developers use this skill to identify prompt injection attempts, separate untrusted input from instructions, and prevent disclosure of secrets or system prompts during assistant workflows.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The broad auto-trigger may activate during ordinary security discussions or when other skills mention prompt injection or attacks.

Mitigation: Review trigger behavior before deployment and test common workflows where security research, prompts, or attack terminology appear.

Risk: The skill is defensive guidance rather than executable enforcement, so protection depends on the host agent applying the guidance consistently.

Mitigation: Pair deployment with review of agent instruction hierarchy, tool authorization boundaries, and output filtering behavior.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/maorun/skills/prompt-injection-guard)

## Skill Output:

**Output Type(s):** [Text, Markdown, Guidance]

**Output Format:** [Markdown guidance with warning, confirmation, and blocking responses]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [No executable code; auto-triggered on broad prompt-injection and attack keywords.]

## Skill Version(s):

1.0.0 (source: server release metadata and artifact/_meta.json)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
