## Description:

Generate spectrograms and feature-panel visualizations from audio with the songsee CLI.

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Developers, audio engineers, and analysts use this skill to ask an agent for songsee CLI commands that turn audio files into spectrograms, feature panels, and time-sliced visualizations.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill depends on a third-party Homebrew formula and CLI.

Mitigation: Install only after reviewing and accepting the third-party package source and formula.

Risk: Audio input and output paths are provided by the user and may expose unintended files if chosen carelessly.

Mitigation: Run songsee only on audio files and output paths that the user intentionally selects.

## Reference(s):

- [Songsee ClawHub Skill Page](https://clawhub.ai/steipete/skills/songsee)
- [Songsee Project Homepage](https://github.com/steipete/songsee)

## Skill Output:

**Output Type(s):** [Guidance, Shell commands, Files]

**Output Format:** [Markdown with inline shell commands; songsee produces image files such as PNG or JPG]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires the songsee CLI; ffmpeg is used for some non-WAV/MP3 formats when available.]

## Skill Version(s):

1.0.0 (source: ClawHub release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
