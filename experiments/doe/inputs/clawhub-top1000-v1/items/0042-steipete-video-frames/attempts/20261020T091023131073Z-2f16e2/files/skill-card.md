## Description:

Extract frames or short clips from videos using ffmpeg.

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Developers and engineers use this skill to extract a representative frame, timestamped frame, or quick thumbnail from local video files with FFmpeg.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: FFmpeg processes local video files and can be exposed to malformed or untrusted media input.

Mitigation: Install only if comfortable running FFmpeg locally, keep FFmpeg updated, and run it on files from trusted sources where possible.

Risk: The frame index argument is not validated as a non-negative integer before it is placed into the FFmpeg filter expression.

Mitigation: Prefer --time or pass simple numeric --index values, and do not pass --index from untrusted or automatically generated input.

## Reference(s):

- [FFmpeg](https://ffmpeg.org)
- [ClawHub Skill Page](https://clawhub.ai/steipete/skills/video-frames)
- [Publisher Profile](https://clawhub.ai/user/steipete)

## Skill Output:

**Output Type(s):** [text, shell commands, guidance]

**Output Format:** [Markdown with inline bash commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [The skill produces guidance for invoking a local shell script that writes image files from video input.]

## Skill Version(s):

1.0.0 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
