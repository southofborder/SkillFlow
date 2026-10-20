## Description:

Improves Google rankings with search engine optimization (SEO): audits, keyword research, content optimization, technical fixes, schema, and links.

This skill is ready for commercial/non-commercial use.

## Publisher:

[ivangdavila](https://clawhub.ai/user/ivangdavila)

### License/Terms of Use:

MIT-0

## Use Case:

External site owners, marketers, content teams, and developers use this skill to audit organic search performance, diagnose ranking or indexing issues, plan SEO fixes, and draft or refresh search-targeted content.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill may persist business-sensitive SEO preferences, site profiles, audit history, keyword tracking, and drafts under ~/Clawic/data/seo/.

Mitigation: Review or delete ~/Clawic/data/seo/ if prior business context should not be reused, and avoid storing confidential strategy unless persistence is desired.

Risk: SEO recommendations or drafted content can be misleading if applied without validating the target site's current search data and constraints.

Mitigation: Review recommendations against Search Console data, the live SERP, and named URLs before publishing or shipping implementation changes.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/ivangdavila/skills/seo)
- [Clawic skill page](https://clawic.com/skills/seo)
- [Setup guide](setup.md)
- [Memory template](memory-template.md)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance with optional code, shell commands, configuration snippets, audit findings, content drafts, and implementation recommendations]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May persist disclosed SEO preferences, site profiles, audit history, keyword tracking, and drafts under ~/Clawic/data/seo/ when the agent is asked to retain that context.]

## Skill Version(s):

1.0.6 (source: frontmatter and server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
