## Description:

Guides an agent through using Apify-powered TikTok scraping actors to fetch videos, profiles, hashtags, music, comments, and location-based posts.

This skill is ready for commercial/non-commercial use.

## Publisher:

[apidojo-io](https://clawhub.ai/user/apidojo-io)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and external users use this skill to prepare API calls and code snippets for collecting TikTok posts, creator profiles, hashtag or music results, comments, and location-linked posts through Apify actors. It is suited to user-directed data extraction workflows that require structured JSON results.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill can enable broad collection of TikTok profiles, comments, and location-linked posts without built-in privacy or acceptable-use guardrails.

Mitigation: Use it only for narrow, lawful, user-directed scraping; minimize personal data collection and confirm TikTok, Apify, and applicable privacy-law requirements before bulk jobs.

Risk: The skill depends on a paid Apify plan and may return demo or limited results without the required account status.

Mitigation: Confirm the Apify plan and API token before running jobs, and stop if returned data indicates demo mode, limited results, or a free-plan restriction.

## Reference(s):

- [Server-resolved GitHub provenance](https://github.com/apidojo-io/social-media-skills/tree/main/skills/tiktok-scraper)
- [ClawHub skill page](https://clawhub.ai/apidojo-io/skills/tiktok-scraper)
- [Apify account setup](https://console.apify.com/account/integrations)
- [Apify pricing](https://apify.com/pricing?fpr=yhdrb)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance]

**Output Format:** [Markdown with bash, JSON, Python, and JavaScript examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [The skill helps produce Apify API requests and client-library examples that return structured JSON post or comment objects.]

## Skill Version(s):

0.1.0 (source: release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
