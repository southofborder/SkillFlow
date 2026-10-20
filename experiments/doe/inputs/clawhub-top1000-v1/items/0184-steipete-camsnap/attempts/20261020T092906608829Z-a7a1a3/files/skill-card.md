## Description:

Capture frames or clips from RTSP/ONVIF cameras.

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Developers and operators use this skill to generate camsnap commands and configuration guidance for discovering cameras, capturing snapshots or clips, monitoring motion events, and running diagnostics.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Installing camsnap uses a third-party Homebrew tap.

Mitigation: Install only if you trust steipete/tap/camsnap and review the package before deployment.

Risk: Camera credentials may be exposed when passwords are typed directly into command examples.

Mitigation: Prefer an interactive prompt, protected configuration, or a least-privileged camera account when the tool supports it.

Risk: The skill can guide access to camera streams.

Mitigation: Use only with authorized cameras and confirm camera privacy and security requirements before capture or motion monitoring.

## Reference(s):

- [Camsnap homepage](https://camsnap.ai)
- [ClawHub Camsnap skill page](https://clawhub.ai/steipete/skills/camsnap)
- [ClawHub publisher profile for steipete](https://clawhub.ai/user/steipete)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown with inline shell commands and configuration paths]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Produces camsnap command guidance; depends on camsnap, ffmpeg, and configured camera access.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
