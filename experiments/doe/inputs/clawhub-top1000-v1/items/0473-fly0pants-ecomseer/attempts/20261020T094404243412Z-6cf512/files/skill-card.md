## Description:

EcomSeer helps agents search TikTok Shop products, rankings, influencers, shops, videos, ads, and deeper EcomSeer research reports through natural-language requests.

This skill is ready for commercial/non-commercial use.

## Publisher:

[fly0pants](https://clawhub.ai/user/fly0pants)

### License/Terms of Use:

MIT-0

## Use Case:

External e-commerce operators, sellers, and analysts use this skill through an agent to query TikTok Shop market data, compare products, shops, influencers, videos, and ads, and request deeper EcomSeer research reports.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill can store pasted EcomSeer API keys for later API use.

Mitigation: Use a dedicated, revocable EcomSeer API key with the least access available and avoid pasting secrets into chat where possible.

Risk: Deep Research can send the user's query, context, and API key to EcomSeer server-side infrastructure and create a shareable hosted report link.

Mitigation: Use Deep Research only for data acceptable to send to EcomSeer infrastructure, and review hosted report links before sharing them.

Risk: The release documentation uses an unpinned npx install command.

Mitigation: Review the installer source and release version before installing or deploying the skill.

## Reference(s):

- [EcomSeer Website](https://www.ecomseer.com)
- [ClawHub Skill Page](https://clawhub.ai/fly0pants/skills/ecomseer)
- [Goods API Reference](references/api-goods.md)
- [Product Detail API Reference](references/api-product-detail.md)
- [Influencer API Reference](references/api-influencer.md)
- [Video API Reference](references/api-video.md)
- [Shop API Reference](references/api-shop.md)
- [Ad and Creative API Reference](references/api-ad.md)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown responses with tables, summaries, shell commands, and links to hosted HTML reports for deeper research.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Responses mirror the user's language; complex research may use EcomSeer server-side analysis and return a shareable hosted report link.]

## Skill Version(s):

1.0.1 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
