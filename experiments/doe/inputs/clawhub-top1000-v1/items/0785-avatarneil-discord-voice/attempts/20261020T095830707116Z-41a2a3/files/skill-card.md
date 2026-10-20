## Description:

Real-time voice conversations in Discord voice channels with Claude AI.

This skill is ready for commercial/non-commercial use.

## Publisher:

[avatarneil](https://clawhub.ai/user/avatarneil)

### License/Terms of Use:

MIT

## Use Case:

Developers and server operators use this skill to let an OpenClaw or Clawdbot agent join Discord voice channels, transcribe speech, route requests to the agent, and speak responses back through configurable STT and TTS providers.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Anyone in a joined Discord voice channel may be able to drive the connected agent and affect shared context.

Mitigation: Install only in trusted servers or channels, configure allowedUsers explicitly, and run voice-originated requests with a restricted agent/tool profile.

Risk: Voice input may be recorded, logged, transcribed, sent to providers, and used as agent input.

Mitigation: Tell participants how speech is handled and prefer local or TLS-protected STT/TTS paths when handling sensitive conversations.

Risk: Remote Wyoming STT over TCP can expose transcription traffic if deployed without transport protection.

Mitigation: Avoid remote Wyoming TCP unless it is secured by a trusted tunnel or equivalent protected network path.

Risk: Node dependencies and native voice components increase supply-chain and runtime review needs.

Mitigation: Audit and update the npm lockfile before production use and preinstall system dependencies through normal administrator-controlled channels.

## Reference(s):

- [Discord Voice ClawHub Page](https://clawhub.ai/avatarneil/skills/discord-voice)
- [README](artifact/README.md)
- [Security Model](artifact/SECURITY.md)
- [OpenClaw Plugin Metadata](artifact/openclaw.plugin.json)

## Skill Output:

**Output Type(s):** [Text, Audio, Shell commands, Configuration, Guidance]

**Output Format:** [Markdown guidance with inline JSON and shell command examples; spoken audio in Discord at runtime]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Uses Discord voice permissions, configured STT/TTS providers, optional provider API keys, ffmpeg, and native voice dependencies.]

## Skill Version(s):

0.1.6 (source: server release metadata; artifact package.json is 0.1.5 and artifact CHANGELOG is 0.1.0)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
