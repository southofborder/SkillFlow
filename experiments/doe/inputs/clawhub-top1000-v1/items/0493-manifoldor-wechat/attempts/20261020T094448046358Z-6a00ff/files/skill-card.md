## Description:

Install OpenClaw's official WeChat plugin and complete account pairing via QR code scan.

This skill is ready for commercial/non-commercial use.

## Publisher:

[manifoldor](https://clawhub.ai/user/manifoldor)

### License/Terms of Use:

MIT-0

## Use Case:

OpenClaw users use this skill to install the official WeChat plugin, display a QR-code pairing page, and save the paired WeChat account configuration without manual command-line steps.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill downloads and executes an npm installer during setup.

Mitigation: Pin the installer version and require explicit approval before installation.

Risk: The skill writes WeChat bot credentials and uses browser-visible status data and /tmp files.

Mitigation: Keep tokens out of browser-visible status data and avoid storing credentials in /tmp.

Risk: The skill starts a local HTTP server for the pairing flow.

Mitigation: Bind the server to loopback and keep routes narrowly scoped.

Risk: The skill changes OpenClaw configuration and restarts the gateway.

Mitigation: Review the proposed configuration changes before execution and validate remote identifiers.

Risk: The skill constructs shell commands for local administration.

Mitigation: Avoid shell-string command construction where argument arrays or safer APIs are available.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/manifoldor/skills/wechat)
- [Publisher profile](https://clawhub.ai/user/manifoldor)
- [WeChat iLink API base](https://ilinkai.weixin.qq.com)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Configuration, Guidance]

**Output Format:** [Markdown guidance with generated local HTML status page and shell command execution]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Generates QR-code and status files under /tmp, writes OpenClaw WeChat account configuration, and updates OpenClaw channel settings.]

## Skill Version(s):

2.1.0 (source: server release evidence and frontmatter)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
