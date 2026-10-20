## Description:

ElevenLabs TTS helps agents generate expressive text-to-speech voice messages with ElevenLabs audio tags, multilingual voice synthesis, and WhatsApp-oriented delivery guidance.

This skill is ready for commercial/non-commercial use.

## Publisher:

[shaharsha](https://clawhub.ai/user/shaharsha)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and agents use this skill to configure ElevenLabs TTS, compose expressive voice prompts with audio tags, and prepare generated speech for WhatsApp voice-message workflows.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The documented WhatsApp workflow can pick and send the wrong temporary audio file.

Mitigation: Use the exact output path from the current TTS call or a private per-run directory, and avoid scanning shared temporary paths.

Risk: Text sent to ElevenLabs and WhatsApp recipients is external disclosure.

Mitigation: Do not submit sensitive or confidential text unless disclosure is approved, and verify the intended WhatsApp recipient before sending.

## Reference(s):

- [Audio Tags Reference](references/audio-tags.md)
- [ClawHub skill page](https://clawhub.ai/shaharsha/skills/elevenlabs-tts)
- [ClawHub source listing](https://clawhub.com/skills/elevenlabs-tts)
- [ElevenLabs](https://elevenlabs.io)
- [ElevenLabs voice library](https://elevenlabs.io/voice-library)
- [ElevenLabs voices API](https://api.elevenlabs.io/v1/voices)

## Skill Output:

**Output Type(s):** [Guidance, Shell commands, Configuration, API Calls, Files]

**Output Format:** [Markdown guidance with JSON configuration examples, inline tool calls, and bash commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May produce or route audio files through ElevenLabs TTS and WhatsApp workflows when the required API key and ffmpeg are available.]

## Skill Version(s):

2.4.0 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
