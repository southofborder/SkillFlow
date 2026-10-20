## Description:

Continuous self-improvement through structured reflection and memory.

This skill is ready for commercial/non-commercial use.

## Publisher:

[hopyky](https://clawhub.ai/user/hopyky)

### License/Terms of Use:

MIT

## Use Case:

Developers and agent operators use this skill to give an OpenClaw agent a recurring self-review loop that checks whether reflection is due, reads recent lessons, and records misses and fixes in local memory.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Recurring reflection workflows may persist sensitive prompts, credentials, customer data, or incident details in local memory.

Mitigation: Configure the memory path deliberately, inspect it regularly, and instruct agents not to log secrets or sensitive operational details.

Risk: Installation from a mutable external checkout can change the executable after review.

Mitigation: Install only from a pinned, reviewed commit or release and review the executable before deployment.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/hopyky/skills/self-reflection)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [CLI status text, Markdown memory entries, and JSON configuration]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires jq and date; writes reflection memory and timer state to configured local paths.]

## Skill Version(s):

1.1.1 (source: SKILL.md frontmatter, server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
