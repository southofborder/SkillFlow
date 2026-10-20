## Description:

Inspect Google Ads accounts and campaigns, run GAQL reports, and coordinate campaign or audience changes with confirmation via the Google Ads API.

This skill is ready for commercial/non-commercial use.

## Publisher:

[hith3sh](https://clawhub.ai/user/hith3sh)

### License/Terms of Use:

MIT-0

## Use Case:

External users and developers use this skill to inspect Google Ads customers and campaigns, run GAQL performance reports, and prepare campaign, ad group, or audience changes through ClawLink with explicit confirmation for writes.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill asks users to install and allowlist an unpinned third-party ClawLink plugin that mediates Google Ads access.

Mitigation: Install only when the user trusts ClawLink and the ClawHub package source, and verify the provider through the linked ClawLink materials before connecting accounts.

Risk: Connected Google Ads accounts may have production spend or customer-list access.

Mitigation: Connect only the Google Ads accounts needed for the task and review permissions before using the skill in production environments.

Risk: Write actions can create or update campaigns, ad groups, audiences, or customer lists.

Mitigation: Require a clear preview and explicit user confirmation before every write or destructive action.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/hith3sh/skills/google-ads-campaigns)
- [Google Ads API documentation](https://developers.google.com/google-ads/api/docs/start)
- [Google Ads API reference](https://developers.google.com/google-ads/api/reference/rpc)
- [GAQL query documentation](https://developers.google.com/google-ads/api/docs/query/overview)
- [ClawLink](https://claw-link.dev/?utm_source=clawhub&utm_medium=referral&utm_content=google-ads-campaigns)
- [ClawLink Docs](https://docs.claw-link.dev/openclaw)
- [ClawLink Verification](https://claw-link.dev/verify)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance with inline shell commands and JSON tool-call parameters]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires a connected Google Ads account through ClawLink; write actions require preview and explicit user confirmation.]

## Skill Version(s):

1.0.5 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
