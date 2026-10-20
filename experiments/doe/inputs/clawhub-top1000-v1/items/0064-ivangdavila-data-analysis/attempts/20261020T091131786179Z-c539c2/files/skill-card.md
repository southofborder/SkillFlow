## Description:

Data analysis and visualization for querying databases, generating reports, automating spreadsheets, and turning raw data into clear, actionable insights.

This skill is ready for commercial/non-commercial use.

## Publisher:

[ivangdavila](https://clawhub.ai/user/ivangdavila)

### License/Terms of Use:

MIT-0

## Use Case:

Employees, external users, developers, and analysts use this skill to turn SQL, spreadsheets, notebooks, dashboards, exports, and ad hoc tables into decision-ready analysis, visualizations, reports, metric definitions, experiment readouts, cohort or funnel analysis, anomaly reviews, and recommendations.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Analysis may involve sensitive datasets, credentials, or business metrics supplied by the user.

Mitigation: Keep sensitive data local unless the user explicitly authorizes sharing, avoid exposing credentials, and summarize only the data needed for the analysis decision.

Risk: Weak sample sizes, ambiguous metric definitions, confounding, or data quality issues can produce misleading conclusions.

Mitigation: Define metric contracts before calculation, quantify uncertainty, segment likely confounders, and downgrade or block conclusions when the data cannot support the claim.

## Reference(s):

- [ClawHub Skill Page](https://clawhub.ai/ivangdavila/skills/data-analysis)
- [Skill Homepage](https://clawic.com/skills/data-analysis)
- [Metric Contracts](artifact/metric-contracts.md)
- [Chart Selection](artifact/chart-selection.md)
- [Decision Briefs](artifact/decision-briefs.md)
- [Analytical Pitfalls](artifact/pitfalls.md)
- [Analysis Techniques](artifact/techniques.md)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance]

**Output Format:** [Markdown or plain text, with code, SQL, formulas, tables, chart guidance, or shell commands when appropriate for the analysis task]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Outputs should lead with the insight, quantify uncertainty, state limitations, and recommend next steps.]

## Skill Version(s):

1.0.2 (source: frontmatter and server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
