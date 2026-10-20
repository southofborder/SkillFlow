## Description:

Persistent local transcript-first memory for OpenClaw via a Node adapter and FastAPI engine.

This skill is ready for commercial/non-commercial use.

## Publisher:

[bluepointdigital](https://clawhub.ai/user/bluepointdigital)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and agent operators use Smart Memory to give local OpenClaw-style agents durable, transcript-backed recall for prior decisions, preferences, project state, and pending insights.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The local service stores transcripts and derived memories that may contain sensitive conversation history.

Mitigation: Run it only in a trusted local environment, keep storage access restricted, and review retention or cleanup practices before using it with sensitive data.

Risk: The memory service can affect future prompts through retrieved memories and injected context.

Mitigation: Treat stored and retrieved memories as untrusted context, inspect evidence when continuity matters, and avoid relying on memory that cannot be verified.

Risk: The FastAPI backend exposes transcript and memory inspection endpoints.

Mitigation: Keep the service bound to 127.0.0.1 and add authentication before any remote, shared, or network-exposed use.

Risk: Installer and configuration steps can change local tool routing and memory behavior.

Mitigation: Review installation commands before execution and confirm the rollback path before disabling built-in memory tools.

## Reference(s):

- [Smart Memory on ClawHub](https://clawhub.ai/bluepointdigital/skills/smart-memory)
- [Smart Memory README](artifact/README.md)
- [Smart Memory OpenClaw Skill](artifact/skills/smart-memory-openclaw/README.md)
- [Agent Integration Guide](artifact/INTEGRATION.md)
- [Memory Structure](artifact/MEMORY_STRUCTURE.md)
- [Hot Memory and Working Context](artifact/HOT_MEMORY_EXTENSION.md)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance with API examples and shell commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires a local FastAPI backend on 127.0.0.1:8000 and stores transcript-backed memory locally.]

## Skill Version(s):

3.1.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
