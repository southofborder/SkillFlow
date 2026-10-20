## Description:

Foodora-only CLI for checking past orders and active order status (Deliveroo WIP).

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

External users and developers use this skill to operate the ordercli CLI for Foodora order history, active order status, and explicit reorder workflows. Deliveroo support is described as work in progress.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill asks users to install a mutable external ordercli binary.

Mitigation: Prefer a pinned and verified ordercli version before using the skill.

Risk: Browser login and session import can expose food delivery account sessions or cookies.

Mitigation: Use a dedicated browser profile when browser login is necessary and avoid importing from a main Chrome profile.

Risk: Reorder commands can change a cart when confirmed.

Mitigation: Use preview mode first and run confirm commands only when cart changes are intended.

## Reference(s):

- [Ordercli homepage](https://ordercli.sh)
- [Foodora Austria](https://www.foodora.at/)
- [ClawHub skill page](https://clawhub.ai/steipete/skills/ordercli)
- [Publisher profile](https://clawhub.ai/user/steipete)

## Skill Output:

**Output Type(s):** [Shell commands, Configuration instructions, Guidance]

**Output Format:** [Markdown with inline shell commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Includes commands for order lookup, active order tracking, session import, and reorder confirmation.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
