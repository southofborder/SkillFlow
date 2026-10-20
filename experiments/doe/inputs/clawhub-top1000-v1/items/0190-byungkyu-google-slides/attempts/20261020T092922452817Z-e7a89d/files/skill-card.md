## Description:

Helps agents create and edit Google Slides presentations through a connected account, with optional user-approved automations.

This skill is ready for commercial/non-commercial use.

## Publisher:

[byungkyu](https://clawhub.ai/user/byungkyu)

### License/Terms of Use:

MIT-0

## Use Case:

People and teams use this skill to read, create, and update presentations, slides, and formatting in an authorized Google Slides account. They can also set up approved scheduled or event-driven actions.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Connecting an account grants access to the selected Google Slides data.

Mitigation: Confirm account authorization with the user and select the narrowest available Google scopes.

Risk: Writes and automations can change slides or run later without a person present.

Mitigation: Review the exact target and payload, and obtain explicit approval before writes or automations.

Risk: Raw API keys can expose long-lived credentials.

Mitigation: Prefer the OAuth-enabled CLI; use raw API keys only when the CLI cannot be used.

## Reference(s):

- [Google Slides skill release](https://clawhub.ai/byungkyu/skills/google-slides)
- [Google Slides API reference](https://developers.google.com/slides/api/reference/rest)
- [Maton documentation](https://docs.maton.ai)
- [Maton CLI manual](https://cli.maton.ai/manual)

## Skill Output:

**Output Type(s):** [Guidance, Shell commands, Code, Configuration instructions]

**Output Format:** [Markdown with commands and examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Actions and responses depend on the authorized account and user-approved requests.]

## Skill Version(s):

1.2.5 (source: ClawHub release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
