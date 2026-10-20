## Description:

Extracts structured information from websites using direct page fetching for simple pages and browser automation for dynamic, paginated, or login-gated flows.

This skill is ready for commercial/non-commercial use.

## Publisher:

[zhangqixin9527](https://clawhub.ai/user/zhangqixin9527)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and agents use this skill to collect website listings, page fields, and structured summaries from public, dynamic, paginated, or authenticated web pages when the user has specified the target site and desired fields.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill can guide scraping of dynamic or login-gated pages and may save larger results in the workspace.

Mitigation: Use it only for sites and fields intentionally specified by the user, avoid secrets or unnecessary personal data, and review saved files when authenticated content is involved.

Risk: Blocked, incomplete, or missing site fields can lead to misleading extracted datasets.

Mitigation: Test one page first, do not invent missing fields, deduplicate results, and report access blocks or incomplete extraction clearly.

## Reference(s):

- [Web Scraping skill page](https://clawhub.ai/zhangqixin9527/skills/web-scraping)

## Skill Output:

**Output Type(s):** [Text, Markdown, JSON, Code, Shell commands, Configuration]

**Output Format:** [Markdown guidance, concise bullet summaries, JSON arrays, or CSV/TSV rows]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May save larger scraping results as workspace files when the task is more than a quick one-off.]

## Skill Version(s):

1.0.0 (source: release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
