## Description:

Manages QQ Zone photo albums, including QR-code login, album and photo listing, photo upload, photo and album download, and album creation.

This skill is ready for commercial/non-commercial use.

## Publisher:

[wscats](https://clawhub.ai/user/wscats)

### License/Terms of Use:

MIT-0

## Use Case:

Agents and end users use this skill to manage QQ Zone photo albums: sign in with a QQ session, list albums and photos, upload photos, download photos or albums, and create albums.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill requires QQ Zone session cookies that can grant account access.

Mitigation: Use a dedicated cookies file with restrictive permissions, keep it off shared systems, and remove it when the task is complete.

Risk: Download and upload actions read or write local photo files and can use user-provided URLs or paths.

Mitigation: Review file paths and download URLs before execution, and write downloads to an expected local output directory.

Risk: Newly created albums may have visibility settings that require user review.

Mitigation: Check QQ Zone album visibility after creation or upload workflows finish.

Risk: The skill uses QQ Zone interfaces that may change outside the skill publisher's control.

Mitigation: Validate the workflow with non-critical photos before relying on it for backup or migration.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/wscats/skills/qq-zone-photo)
- [QQ Zone](https://user.qzone.qq.com/)

## Skill Output:

**Output Type(s):** [Text, JSON, Shell commands, Files, Configuration]

**Output Format:** [Markdown guidance with inline shell commands; CLI actions return JSON status data and may write downloaded image files.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Most actions require a local QQ cookies JSON file; download actions write to a local output directory.]

## Skill Version(s):

1.0.3 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
