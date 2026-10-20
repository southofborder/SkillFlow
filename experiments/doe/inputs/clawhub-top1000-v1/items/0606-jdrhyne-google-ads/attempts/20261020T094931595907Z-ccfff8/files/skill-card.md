## Description:

Query, audit, and optimize Google Ads campaigns through an attached browser or the Google Ads API, defaulting to read-only reporting and requiring reviewed approval for account changes.

This skill is ready for commercial/non-commercial use.

## Publisher:

[jdrhyne](https://clawhub.ai/user/jdrhyne)

### License/Terms of Use:

MIT-0

## Use Case:

External users and developers use this skill to inspect Google Ads accounts, produce campaign and conversion-health analyses, generate recommendations, and perform tightly scoped account changes only after a reviewed approval flow.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Account changes can affect campaign delivery, spend, targeting, conversion setup, labels, or other business-impacting settings.

Mitigation: Require a bounded preview with account identity, entity IDs, before and after values, timing, validation method, rollback notes, and explicit action-time approval before execution.

Risk: Google Ads credentials, OAuth tokens, customer IDs, reports, and account data may be sensitive.

Mitigation: Use protected local configuration or secret storage, never ask for or display credential values, retrieve only requested fields, and avoid exporting or sharing reports without separate approval.

Risk: Incomplete context, conversion lag, attribution settings, UI drift, or ambiguous account identity can lead to misleading recommendations or unsafe actions.

Mitigation: Confirm account and manager context, reporting dates, timezone, business objective, primary conversion actions, accessible controls, and data completeness before drawing conclusions or proposing changes.

## Reference(s):

- [Google Ads API Documentation](https://developers.google.com/google-ads/api/docs/start)
- [Google Ads API Release Notes](https://developers.google.com/google-ads/api/docs/release-notes)
- [Google Ads API Upgrade Guide](https://developers.google.com/google-ads/api/docs/upgrade)
- [Google Ads API Client Libraries](https://developers.google.com/google-ads/api/docs/client-libs)
- [Google Ads API Limits and Quotas](https://developers.google.com/google-ads/api/docs/best-practices/quotas)
- [Google Ads Skill on ClawHub](https://clawhub.ai/jdrhyne/skills/google-ads)
- [Publisher Profile](https://clawhub.ai/user/jdrhyne)
- [API Setup Reference](references/api-setup.md)
- [Browser Workflows Reference](references/browser-workflows.md)
- [Mutation Workflow Reference](references/mutation-workflow.md)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance with inline code and shell command examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Outputs are scoped to the confirmed Google Ads account, customer context, date range, and approved change preview.]

## Skill Version(s):

1.2.0 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
