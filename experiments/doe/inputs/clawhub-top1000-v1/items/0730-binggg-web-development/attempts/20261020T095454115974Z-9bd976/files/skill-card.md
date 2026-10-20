## Description:

Helps developers implement, debug, build, deploy, and validate React, Vue, and Vite frontends, including CloudBase Web integration when needed.

This skill is ready for commercial/non-commercial use.

## Publisher:

[binggg](https://clawhub.ai/user/binggg)

### License/Terms of Use:

MIT

## Use Case:

Developers use this skill to implement and troubleshoot existing or new Web frontends, validate browser flows, and integrate CloudBase Web SDK or static hosting when appropriate.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The protected-route and auth-guard examples may treat an unverified token as an authenticated user.

Mitigation: Review and correct authentication examples before use; verify token signature, issuer, audience, expiry, environment, and session or revocation state with a trusted backend or supported CloudBase validation flow before granting access.

Risk: An implicit CloudBase region may point the application at the wrong deployment region.

Mitigation: Configure the CloudBase region explicitly for the intended deployment.

## Reference(s):

- [ClawHub skill release](https://clawhub.ai/binggg/skills/web-development)
- [Framework guidance](artifact/frameworks.md)
- [Browser validation guidance](artifact/browser-testing.md)
- [CloudBase integration documentation](https://docs.cloudbase.net/integration/introduce.md)

## Skill Output:

**Output Type(s):** [Code, Shell commands, Configuration, Guidance]

**Output Format:** [Text or Markdown with code and configuration snippets]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May include build, browser-validation, and deployment steps.]

## Skill Version(s):

1.27.84 (source: ClawHub release metadata; artifact frontmatter lists 2.36.0)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
