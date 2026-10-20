## Description:

Helps agents publish files and websites to live URLs, manage site access, and store or share files in private Drives.

This skill is ready for commercial/non-commercial use.

## Publisher:

[adamludwin](https://clawhub.ai/user/adamludwin)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and other agents use this skill to publish sites and files, control who can view them, and manage private Drive storage or shared team sites.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Publishing selected local files can expose sensitive content or make a site publicly accessible.

Mitigation: Confirm the exact files, destination, and visibility with the user before publishing.

Risk: Drive operations and sharing tokens can expose, change, or delete private files.

Mitigation: Confirm the affected Drive paths and token permissions; use a narrow path prefix and short expiry when sharing.

Risk: A stored API key grants persistent access to the user's here.now account.

Mitigation: Get consent before saving credentials and keep the credentials file private.

## Reference(s):

- [ClawHub skill release](https://clawhub.ai/adamludwin/skills/here-now)
- [here.now documentation](https://here.now/docs)
- [here.now API reference](https://here.now/openapi.json)

## Skill Output:

**Output Type(s):** [Guidance, Shell commands, URLs]

**Output Format:** [Markdown with commands and published URLs]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Publishing may return a live site URL, access details, warnings, or a claim link for an expiring anonymous site.]

## Skill Version(s):

1.33.0 (source: server-resolved release)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
