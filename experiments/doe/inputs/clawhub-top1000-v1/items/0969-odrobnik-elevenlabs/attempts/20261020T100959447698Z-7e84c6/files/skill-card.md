## Description:

Text-to-speech, sound effects, music generation, voice management, and quota checks via the ElevenLabs API.

This skill is ready for commercial/non-commercial use.

## Publisher:

[odrobnik](https://clawhub.ai/user/odrobnik)

### License/Terms of Use:


## Use Case:

Developers and content creators use this skill to generate speech, dialogue, sound effects, and music through ElevenLabs, manage available voices, clone permitted voices from audio samples, and review quota or usage.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Text prompts, generation settings, account usage requests, and selected voice samples are sent to the ElevenLabs API.

Mitigation: Use only content acceptable for ElevenLabs processing and avoid sending confidential text or unapproved voice recordings.

Risk: Voice cloning can process sensitive voice recordings.

Mitigation: Use voice cloning only with recordings you own or have permission to use; keep samples in the guarded sample directory or another deliberate sample directory.

Risk: The ElevenLabs API key grants access to account operations used by the skill.

Mitigation: Protect ELEVENLABS_API_KEY, prefer environment-based configuration, and avoid storing the key in synced dotfiles or committed .env files.

## Reference(s):

- [ElevenLabs](https://elevenlabs.io)
- [ElevenLabs Music API compose documentation](https://elevenlabs.io/docs/api-reference/music/compose)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, files, guidance]

**Output Format:** [Markdown guidance with bash commands; script outputs include audio files, text tables, and optional JSON.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires ELEVENLABS_API_KEY, python3, requests, ffmpeg for conversion workflows, and afplay for optional macOS playback.]

## Skill Version(s):

1.3.4 (source: server release metadata and frontmatter)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
