## Description:

OpenClaw Command Center provides a local dashboard for monitoring agent sessions, model usage, costs, scheduled jobs, and system health.

This skill is ready for commercial/non-commercial use.

## Publisher:

[jontsai](https://clawhub.ai/user/jontsai)

### License/Terms of Use:

MIT

## Use Case:

OpenClaw operators and developers use the dashboard to monitor agents, review usage and costs, inspect system health, and manage scheduled jobs in their workspace.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Dashboard data and job controls may be exposed by default or proxy authentication settings.

Mitigation: Bind explicitly to loopback or a trusted interface; use token authentication for non-local access.

Risk: Header-based Tailscale or Cloudflare authentication may be bypassed if the origin is reachable outside a trusted proxy.

Mitigation: Use these modes only when the origin is isolated behind a correctly configured trusted proxy.

## Reference(s):

- [ClawHub skill listing](https://clawhub.ai/jontsai/skills/command-center)
- [Architecture overview](artifact/docs/architecture/OVERVIEW.md)
- [Work graph contract](artifact/docs/work-graph.md)

## Skill Output:

**Output Type(s):** [Guidance, Shell commands]

**Output Format:** [Markdown with inline shell commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Runs a local web dashboard for monitoring and job management.]

## Skill Version(s):

1.5.0 (source: skill frontmatter and server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
