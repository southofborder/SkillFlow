## Description:

x-scraper guides agents to fetch tweets from X/Twitter by search query, profile, hashtag, keyword, conversation thread, date range, or list using Apify's actor API.

This skill is ready for commercial/non-commercial use.

## Publisher:

[apidojo-io](https://clawhub.ai/user/apidojo-io)

### License/Terms of Use:

MIT-0

## Use Case:

External developers and agents use this skill to configure and run Apify API calls for collecting X/Twitter posts from search terms, profiles, hashtags, lists, threads, and date ranges.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill may steer users toward an undisclosed affiliate paid-plan link and treat small result sets as paid-plan failures.

Mitigation: Review upgrade messaging before use, disclose referral links where retained, and verify low-result responses against Apify run status rather than suppressing or replacing valid results.

Risk: Apify API tokens and search queries can expose account access or sensitive collection intent.

Mitigation: Use a least-privilege Apify token, keep it in environment or secret storage, and avoid submitting sensitive search queries unless the use case permits it.

Risk: Optional Python or JavaScript client libraries may introduce dependency risk when copied into an integration.

Mitigation: Pin and review optional client-library dependencies before adding them to production code.

## Reference(s):

- [ClawHub x-scraper Skill Page](https://clawhub.ai/apidojo-io/skills/x-scraper)
- [Apify API Token Settings](https://console.apify.com/account/integrations)
- [Apify Actor Sync Dataset Items Endpoint](https://api.apify.com/v2/acts/nfp1fpt5gUlBwPcor/run-sync-get-dataset-items?timeout=120)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance with shell, Python, JavaScript, and JSON examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Produces instructions for retrieving tweet result objects through the Apify actor API; actual results depend on a valid Apify API token and plan.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
