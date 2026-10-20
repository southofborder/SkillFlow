## Description:

Control Philips Hue lights/scenes via the OpenHue CLI.

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

External users and developers use this skill to let an agent inspect and control Philips Hue lights, rooms, and scenes through a configured Hue Bridge using the OpenHue CLI.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Agent-issued OpenHue commands can turn lights on or off, change brightness or color, and activate scenes.

Mitigation: Review proposed commands before execution and use precise room, light, scene names, or IDs.

Risk: Setup may authorize access to a Hue Bridge in the user's environment.

Mitigation: Authorize only the intended Hue Bridge and confirm discovered bridge details before allowing ongoing control.

## Reference(s):

- [OpenHue CLI documentation](https://www.openhue.io/cli)
- [ClawHub Openhue skill page](https://clawhub.ai/steipete/skills/openhue)
- [ClawHub publisher profile for steipete](https://clawhub.ai/user/steipete)

## Skill Output:

**Output Type(s):** [Shell commands, Configuration instructions, Guidance]

**Output Format:** [Markdown with inline shell commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires the openhue CLI and Hue Bridge authorization during setup.]

## Skill Version(s):

1.0.0 (source: server-resolved release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
