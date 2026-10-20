## Description:

Multi-source deep research agent. Searches the web, synthesizes findings, and delivers cited reports. No API keys required.

This skill is ready for commercial/non-commercial use.

## Publisher:

[parags](https://clawhub.ai/user/parags)

### License/Terms of Use:

MIT

## Use Case:

Developers, researchers, analysts, and external users use this skill to plan multi-query web research, read key sources, synthesize findings, and produce cited reports for a topic or decision.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The documented URL-fetching command can allow a malicious URL to execute local shell commands.

Mitigation: Validate URLs before fetching and invoke curl without shell interpolation; avoid fetching arbitrary or untrusted URLs.

Risk: Browsing, report saving, and sub-agent behavior are not tightly scoped.

Mitigation: Use the skill in an isolated workspace, keep research non-sensitive, and review file paths and sub-agent instructions before execution.

Risk: Research output can include outdated, unsupported, or misleading claims.

Mitigation: Require citations for claims, cross-check important findings across sources, and flag gaps or low-confidence findings in the report.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/parags/skills/deep-research-pro)
- [Project homepage declared by skill metadata](https://github.com/paragshah/deep-research-pro)
- [OpenClaw](https://github.com/openclaw/openclaw)
- [uv](https://github.com/astral-sh/uv)
- [Author profile from README](https://moltbook.com/u/AstralSage)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown report with citations, optional JSON output, and inline shell commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Reports may be delivered in chat or saved to local Markdown or JSON files.]

## Skill Version(s):

1.0.2 (source: server release metadata; artifact frontmatter and package.json report 1.0.0)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
