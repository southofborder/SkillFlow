## Description:

Transcribe audio via OpenAI Audio Transcriptions API (Whisper).

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Developers and other agent users use this skill to transcribe local audio files through OpenAI's audio transcription endpoint, optionally setting model, language, prompt, and JSON output options.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Selected audio files and optional prompt, language, and model fields are sent to OpenAI using the user's API key.

Mitigation: Use only recordings that the user's organization permits for external OpenAI processing, and avoid sensitive or regulated audio unless policy allows it.

## Reference(s):

- [OpenAI Speech to Text documentation](https://platform.openai.com/docs/guides/speech-to-text)
- [OpenAI audio transcriptions API endpoint](https://api.openai.com/v1/audio/transcriptions)

## Skill Output:

**Output Type(s):** [Text, JSON, Shell commands, Configuration]

**Output Format:** [Plain text transcript or JSON file, with the shell command printing the output path.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires curl and OPENAI_API_KEY; defaults to whisper-1 and writes <input>.txt or <input>.json unless an output path is supplied.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
