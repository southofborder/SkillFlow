## Description:

ElevenLabs text-to-speech with mac-style say UX.

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Developers and agents use Sag to generate ElevenLabs text-to-speech audio, preview voices, and produce local playback or MP3 voice replies from text.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill relies on an unpinned third-party Homebrew tap and sag CLI install.

Mitigation: Install only if you trust the sag Homebrew tap and are comfortable with the installed CLI.

Risk: The CLI requires an ElevenLabs API key and sends text for speech generation.

Mitigation: Use a revocable, limited API key where possible and avoid sending sensitive text unless you trust the CLI and ElevenLabs handling of that text.

## Reference(s):

- [Sag homepage](https://sag.sh)
- [Sag ClawHub skill page](https://clawhub.ai/steipete/skills/sag)
- [steipete ClawHub publisher profile](https://clawhub.ai/user/steipete)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Configuration guidance]

**Output Format:** [Markdown with inline bash code blocks and file-generation instructions]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May produce local MP3 audio files through the sag CLI when voice replies are requested.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
