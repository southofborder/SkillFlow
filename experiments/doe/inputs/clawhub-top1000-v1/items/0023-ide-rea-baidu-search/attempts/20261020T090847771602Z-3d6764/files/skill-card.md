## Description:

Search the web using Baidu AI Search Engine (BDSE). Use for live information, documentation, or research topics.

This skill is ready for commercial/non-commercial use.

## Publisher:

[ide-rea](https://clawhub.ai/user/ide-rea)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and agents use this skill to run live Baidu web searches for current information, documentation lookup, and research topics from an OpenClaw environment.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Search queries are sent to Baidu and may include sensitive information if users place secrets or private data in prompts.

Mitigation: Avoid placing credentials, personal data, or confidential business information in search queries.

Risk: An environment-controlled proxy path can redirect search queries and a session identifier outside the stated Baidu endpoint.

Mitigation: Review or remove the DUMATE_SCHEDULER_URL proxy behavior unless the scheduler environment is trusted and controlled.

Risk: The skill requires a Baidu API key stored in local OpenClaw configuration.

Mitigation: Restrict permissions on the OpenClaw configuration file and rotate the key if exposure is suspected.

## Reference(s):

- [Baidu API Key Setup Guide](references/apikey-fetch.md)
- [Baidu AI Search API key console](https://console.bce.baidu.com/ai-search/qianfan/ais/console/apiKey)
- [Baidu AI Search API endpoint](https://qianfan.baidubce.com/v2/ai_search/web_search)

## Skill Output:

**Output Type(s):** [Text, JSON, Shell commands, Configuration guidance]

**Output Format:** [JSON search result array printed to stdout, with setup guidance in Markdown.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires python3 and BAIDU_API_KEY; accepts query, count, and freshness parameters.]

## Skill Version(s):

1.1.4 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
