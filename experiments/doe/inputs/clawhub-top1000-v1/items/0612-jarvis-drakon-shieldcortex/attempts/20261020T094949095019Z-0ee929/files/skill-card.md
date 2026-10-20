## Description:

Memory and defence for AI agents: semantic recall, knowledge graph and decay, plus a memory firewall that scans and enforces against prompt injection, credential leaks and poisoning.

This skill is ready for commercial/non-commercial use.

## Publisher:

[jarvis-drakon](https://clawhub.ai/user/jarvis-drakon)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and agent operators use ShieldCortex to maintain local semantic memory and a knowledge graph, recall context across sessions, and scan agent instructions and saved content for security threats.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The bundled OpenClaw approval gate may ignore approval settings and allow flagged memory-saving actions to proceed.

Mitigation: Do not rely on this gate until its configuration handling and enforcement are fixed; use reviewed, pinned local dependencies and review flagged actions.

Risk: OpenClaw startup self-heal may remove legacy hook directories or copy hook files without prompting.

Mitigation: Back up existing hook directories or set SHIELDCORTEX_SKIP_SELF_HEAL=1 before startup.

Risk: Full cloud memory sync can upload saved memory content.

Mitigation: Review auto-memory settings and the sync mode before enabling cloud sync; leave sync off when content should remain local.

## Reference(s):

- [ShieldCortex documentation](https://shieldcortex.ai/docs)
- [ShieldCortex npm package](https://www.npmjs.com/package/shieldcortex)
- [ShieldCortex changelog](https://shieldcortex.ai/changelog)
- [ShieldCortex release on ClawHub](https://clawhub.ai/jarvis-drakon/skills/shieldcortex)
- [Project repository listed in skill metadata](https://github.com/Drakon-Systems-Ltd/ShieldCortex)

## Skill Output:

**Output Type(s):** [Text, Guidance, Configuration]

**Output Format:** [Text and structured memory or security results, with Markdown guidance and JSON configuration examples.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Memory features and enforcement depend on the installed integration and its configuration.]

## Skill Version(s):

5.10.6 (source: frontmatter; server release 5.10.6)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
