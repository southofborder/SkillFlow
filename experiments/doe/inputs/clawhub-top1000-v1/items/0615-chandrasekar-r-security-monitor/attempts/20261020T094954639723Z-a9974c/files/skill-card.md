## Description:

Real-time security monitoring for Clawdbot. Detects intrusions, unusual API calls, credential usage patterns, and alerts on breaches.

This skill is ready for commercial/non-commercial use.

## Publisher:

[chandrasekar-r](https://clawhub.ai/user/chandrasekar-r)

### License/Terms of Use:


## Use Case:

Developers and operators use this skill to run continuous security monitoring for a Clawdbot deployment, including alerts for failed logins, unexpected ports, process spikes, watched file changes, credential presence, and Docker health issues.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The monitor reads root-scoped credential files and records security-sensitive activity in logs and state files.

Mitigation: Run it only under a tightly scoped account, avoid granting unrelated credential-file access, and protect generated logs and state as sensitive security data.

Risk: The documented --threats option does not limit checks.

Mitigation: Do not rely on --threats for scoping; review behavior before installing and restrict runtime permissions externally.

Risk: Daemon mode can run too aggressively because interval parsing is broken.

Mitigation: Avoid daemon mode until interval parsing and resource controls are fixed.

## Reference(s):

- [ClawHub Security Monitor release page](https://clawhub.ai/chandrasekar-r/skills/security-monitor)
- [ClawHub publisher profile](https://clawhub.ai/user/chandrasekar-r)

## Skill Output:

**Output Type(s):** [text, shell commands, configuration, JSON logs]

**Output Format:** [Markdown instructions with bash commands; runtime console text and newline-delimited JSON alert logs]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Writes alert logs and monitor state under /root/clawd/clawdbot-security; Telegram alerts are configurable for high-severity events.]

## Skill Version(s):

1.0.0 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
