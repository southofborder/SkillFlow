## Description:

Fetch GitHub issues, spawn sub-agents to implement fixes and open PRs, then monitor and address PR review comments.

This skill is ready for commercial/non-commercial use.

## Publisher:

[jackhua6](https://clawhub.ai/user/jackhua6)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and repository maintainers use this skill to fetch GitHub issues, coordinate sub-agents that implement fixes, open pull requests, and monitor review comments.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: GitHub tokens may be exposed through command output, transcripts, credential helpers, or token-bearing remotes.

Mitigation: Use a narrowly scoped token, avoid sharing run logs that may contain token material, inspect repository and global Git credential settings after use, and rotate the token if exposure is possible.

Risk: The skill can make unattended repository changes, global Git changes, and pull requests when flags such as --yes or --cron are used.

Mitigation: Run it only on repositories where automated modification is acceptable, prefer interactive confirmation, and use unattended or notification flags only with an external approval process.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/jackhua6/skills/gh-issues)
- [Publisher profile](https://clawhub.ai/user/jackhua6)
- [GitHub Issues API endpoint pattern](https://api.github.com/repos/{SOURCE_REPO}/issues?per_page={limit}&state={state}&{query_params})
- [GitHub Pull Requests API endpoint pattern](https://api.github.com/repos/{SOURCE_REPO}/pulls)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance]

**Output Format:** [Markdown with inline shell commands, API request examples, status tables, and pull request summaries]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Can initiate repository changes and pull requests through delegated agents when the user confirms or unattended flags are used.]

## Skill Version(s):

1.0.0 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
