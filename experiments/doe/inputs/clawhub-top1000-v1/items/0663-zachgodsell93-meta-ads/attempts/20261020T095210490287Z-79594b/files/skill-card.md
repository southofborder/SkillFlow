## Description:

Manage Meta Ads campaigns, ad sets, ads, creatives, and performance metrics through documented Meta Graph API requests.

This skill is ready for commercial/non-commercial use.

## Publisher:

[zachgodsell93](https://clawhub.ai/user/zachgodsell93)

### License/Terms of Use:


## Use Case:

Developers, marketers, and operators use this skill to prepare Meta Ads API requests for reading performance data and managing campaigns, ad sets, ads, and creatives. Because it covers write and delete operations, users should review generated actions before applying them to live ad accounts.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Broad, long-lived Meta ad-management credentials can expose live ad accounts to unauthorized or excessive changes.

Mitigation: Use narrowly scoped credentials, store tokens in a secret manager, avoid query-string tokens, and separate read-only reporting credentials from management credentials.

Risk: Write and delete operations can activate, change budgets for, or remove live ad assets.

Mitigation: Require explicit human approval before activating campaigns, changing budgets, or deleting campaigns, ad sets, ads, or creatives.

## Reference(s):

- [ClawHub Meta Ads skill page](https://clawhub.ai/zachgodsell93/skills/meta-ads)
- [Meta Graph API v25.0 endpoint](https://graph.facebook.com/v25.0/)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown with curl examples, JSON payloads, and configuration guidance]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires Meta access tokens and an ad account ID supplied by the user.]

## Skill Version(s):

1.0.0 (source: server release metadata and artifact frontmatter)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
