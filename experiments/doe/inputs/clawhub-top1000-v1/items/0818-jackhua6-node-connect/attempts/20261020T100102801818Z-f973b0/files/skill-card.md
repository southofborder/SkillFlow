## Description:

Diagnose OpenClaw node connection and pairing failures for Android, iOS, and macOS companion apps. Use when QR/setup code/manual connect fails, local Wi-Fi works but VPS/tailnet does not, or errors mention pairing required, unauthorized, bootstrap token invalid or expired, gateway.bind, gateway.remote.url, Tailscale, or plugins.entries.device-pair.config.publicUrl.

This skill is ready for commercial/non-commercial use.

## Publisher:

[jackhua6](https://clawhub.ai/user/jackhua6)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and operators use this skill to diagnose OpenClaw node-to-gateway routes, QR/setup code failures, manual connection issues, and pairing/authentication errors across Android, iOS, and macOS companion apps.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill recommends approving the latest pending device pairing, which could approve an unintended device when requests are ambiguous or multiple devices are pending.

Mitigation: Compare the pending request with the intended device using a stable request ID, displayed code, fingerprint, or similar identifier, and reject unknown or ambiguous requests before approving.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/jackhua6/skills/node-connect)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Configuration guidance]

**Output Format:** [Markdown with inline shell commands and concise diagnostic guidance]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May ask clarifying questions when route, setup method, or app error text is ambiguous.]

## Skill Version(s):

1.0.0 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
