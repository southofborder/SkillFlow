## Description:

Guides agents using Canonry MCP tools or the cnry CLI to inspect AI visibility evidence, diagnose changes, plan measurement, review integrations, and report results.

This skill is ready for commercial/non-commercial use.

## Publisher:

[arberx](https://clawhub.ai/user/arberx)

### License/Terms of Use:

MIT-0

## Use Case:

Marketing teams, site operators, and their agents use Canonry to review stored visibility evidence, investigate changes, plan approved measurements, inspect integrations, and prepare scoped reports.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Connected credentials and local configuration may expose sensitive access.

Mitigation: Keep config and token files private; never paste secrets into chat or reports.

Risk: Live reads, probes, and measurement runs may consume provider quota or create saved evidence.

Mitigation: Prefer stored-only or read-only access and obtain approval for the exact target and bounded live work.

Risk: Writes to ads, schedules, webhooks, routing, or WordPress can change external systems or incur costs.

Mitigation: Require explicit approval for each proposed change and verify the result before retrying an uncertain action.

Risk: Stale, partial, or incomparable evidence can lead to misleading conclusions.

Mitigation: Preserve dates, scope, sample sizes, and missing-data caveats when comparing results.

## Reference(s):

- [Canonry CLI Reference](references/canonry-cli.md)
- [AEO Analysis](references/aeo-analysis.md)
- [Indexing Workflows](references/indexing.md)
- [Server-Side Traffic](references/server-side-traffic.md)
- [Google Business Profile Integration](references/google-business-profile.md)
- [Google Ads and Google Tag Manager](references/google-marketing.md)
- [WordPress Integration](references/wordpress-integration.md)

## Skill Output:

**Output Type(s):** [Analysis, Guidance, Shell commands, Configuration instructions]

**Output Format:** [Markdown with inline commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Distinguishes stored evidence from live actions and states missing data, dates, and sample sizes.]

## Skill Version(s):

7.46.0+9ce35e0 (source: ClawHub release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
