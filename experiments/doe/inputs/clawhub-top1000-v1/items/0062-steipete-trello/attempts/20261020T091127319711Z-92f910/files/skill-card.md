## Description:

Manage Trello boards, lists, and cards via the Trello REST API.

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Developers and operators use this skill to inspect Trello boards, lists, and cards, then create, move, comment on, or archive cards through Trello API commands.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The Trello token can provide broad access to the user's Trello account.

Mitigation: Use the least-privileged token available, run commands only on trusted machines, avoid logging full API URLs, and rotate the token if it may have appeared in logs or process monitoring.

## Reference(s):

- [Trello REST API documentation](https://developer.atlassian.com/cloud/trello/rest/)
- [Trello API key and token setup](https://trello.com/app-key)
- [ClawHub Trello skill page](https://clawhub.ai/steipete/skills/trello)

## Skill Output:

**Output Type(s):** [guidance, shell commands, configuration, JSON]

**Output Format:** [Markdown with inline bash commands and JSON-oriented jq examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Uses jq and the TRELLO_API_KEY and TRELLO_TOKEN environment variables.]

## Skill Version(s):

1.0.0 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
