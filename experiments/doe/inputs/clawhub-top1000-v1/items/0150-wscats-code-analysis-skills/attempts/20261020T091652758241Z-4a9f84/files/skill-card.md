## Description:

Code Analysis Skills generates descriptive Git-history reflection reports for self-review or consent-based team retrospectives from local repository commit data.

This skill is ready for commercial/non-commercial use.

## Publisher:

[wscats](https://clawhub.ai/user/wscats)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and engineering teams use this skill to summarize Git commit cadence, change patterns, style markers, and code-quality traces for personal reflection or fully consented retrospectives. It is not for performance reviews, ranking, compensation, discipline, surveillance, or other HR decisions.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill processes personal developer Git activity data, including timestamps, commit frequency, and change patterns.

Mitigation: Install and run it only for self-reflection or a team retrospective where every included contributor has clearly opted in, and treat generated reports as sensitive personal data.

Risk: Broad recursive scans can include repositories or contributors outside the intended consent scope.

Mitigation: Choose repository paths tightly and avoid broad scan-all runs on shared workspaces unless every included repository and contributor is in scope.

Risk: Report-rendering risks are noted for HTML and PDF outputs.

Mitigation: Prefer Markdown or JSON output until HTML escaping and PDF resource restrictions are fixed.

## Reference(s):

- [Metrics Guide](references/metrics-guide.md)

## Skill Output:

**Output Type(s):** [text, markdown, json, html, pdf, shell commands, guidance]

**Output Format:** [Markdown, JSON, HTML, or PDF reports, plus concise command and interpretation guidance.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires an explicit repository path and usage-policy acknowledgement; reports are scoped to the current local Git user by default or to explicitly consented authors for team retrospectives.]

## Skill Version(s):

1.1.1 (source: ClawHub release metadata; artifact pyproject.toml and skill.yaml list 1.1.0)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
