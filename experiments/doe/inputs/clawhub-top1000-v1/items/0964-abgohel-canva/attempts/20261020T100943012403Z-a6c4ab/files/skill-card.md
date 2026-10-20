## Description:

Create, export, and manage Canva designs via the Connect API. Generate social posts, carousels, and graphics programmatically.

This skill is ready for commercial/non-commercial use.

## Publisher:

[abgohel](https://clawhub.ai/user/abgohel)

### License/Terms of Use:

MIT

## Use Case:

Developers, creators, and design teams use this skill to manage Canva designs through the Connect API, including listing designs, creating template-based assets, uploading files, and exporting finished graphics.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill uses broad Canva OAuth access for design, asset, and brand-template operations.

Mitigation: Authorize only the Canva workspace and scopes needed for the intended workflow, and limit use to designs and files explicitly selected by the user.

Risk: OAuth tokens are stored locally in ~/.canva/tokens.json, and the security evidence reports weak token handling.

Mitigation: Restrict token file permissions, rotate credentials if exposure is suspected, and prefer a managed secret store for business or private assets.

Risk: The security evidence flags an unpinned installer instruction.

Mitigation: Pin the ClawHub installer and skill version before installing in controlled environments.

## Reference(s):

- [ClawHub Skill Page](https://clawhub.ai/abgohel/skills/canva)
- [Canva Connect API Docs](https://www.canva.dev/docs/connect/)
- [Canva Connect OpenAPI Spec](https://www.canva.dev/sources/connect/api/latest/api.yml)
- [Canva Developers](https://www.canva.com/developers/)
- [Canva Connect API Starter Kit](https://github.com/canva-sdks/canva-connect-api-starter-kit)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Configuration, Guidance]

**Output Format:** [Markdown with inline shell commands and JSON examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May call Canva Connect API endpoints and read or write local Canva OAuth token files during use.]

## Skill Version(s):

1.0.0 (source: frontmatter, package.json, server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
