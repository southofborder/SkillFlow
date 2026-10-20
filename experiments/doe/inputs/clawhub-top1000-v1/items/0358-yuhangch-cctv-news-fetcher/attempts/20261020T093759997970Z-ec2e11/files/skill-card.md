## Description:

Fetch and parse news highlights from CCTV News Broadcast (Xinwen Lianbo) for a given date.

This skill is ready for commercial/non-commercial use.

## Publisher:

[yuhangch](https://clawhub.ai/user/yuhangch)

### License/Terms of Use:


## Use Case:

External users and agents use this skill to fetch CCTV News Broadcast highlights for a requested date, parse the crawler JSON, and summarize the results as domestic, international, or general news highlights.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The crawler follows links collected from remote CCTV pages and makes outbound requests from the local environment.

Mitigation: Review the skill before installation and prefer a version that allowlists CCTV hosts, rejects non-HTTPS or unexpected links, and adds request limits.

Risk: The crawler sends a hard-coded cookie and Host header with page requests.

Mitigation: Prefer a version that removes the hard-coded cookie and Host header before use in sensitive networks.

## Reference(s):

- [ClawHub Skill Page](https://clawhub.ai/yuhangch/skills/cctv-news-fetcher)
- [Publisher Profile](https://clawhub.ai/user/yuhangch)
- [CCTV Xinwen Lianbo archive endpoint](https://cctv.cntv.cn/lm/xinwenlianbo/${date}.shtml)
- [CCTV daily Xinwen Lianbo endpoint](https://tv.cctv.com/lm/xwlb/day/${date}.shtml)
- [Example Usage](examples/example.md)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, JSON, Guidance]

**Output Format:** [Markdown summary derived from JSON crawler output]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [The crawler prints dated news items with title and content fields before the agent summarizes them for the user.]

## Skill Version(s):

1.0.0 (source: server release metadata and package.json)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
