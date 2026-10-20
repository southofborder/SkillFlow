## Description:

Connects to a user's GetNote/Dedao account through the official CLI to save, find, read, and organize notes and knowledge-base content.

This skill is ready for commercial/non-commercial use.

## Publisher:

[iswalle](https://clawhub.ai/user/iswalle)

### License/Terms of Use:

MIT-0

## Use Case:

GetNote/Dedao users can authorize their account and ask an agent to save and retrieve notes, search recordings and books, manage tags and knowledge bases, and diagnose their connection.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Account authorization and note access may expose private content or locally stored credentials.

Mitigation: Authorize only the intended account in the browser; avoid displaying credentials or private note contents in shared conversations.

Risk: Deletion, bulk tag replacement, and public sharing may irreversibly change or expose notes.

Mitigation: Confirm the target and impact before destructive or public operations, then verify the resulting state.

Risk: Setup and CLI updates can install or synchronize companion skills.

Mitigation: Review setup and update prompts and use the platform-managed installation or update flow.

Risk: Uploads and other note writes can change the authorized account's remote data.

Mitigation: Confirm the destination and scope before uploading or writing; check the final response before reporting success.

## Reference(s):

- [GetNote skill on ClawHub](https://clawhub.ai/iswalle/skills/getnote)
- [Official GetNote CLI package](https://www.npmjs.com/package/@getnote/cli)
- [Connection and authorization](references/auth.md)
- [Notes and recordings](references/note.md)
- [Search](references/search.md)
- [Knowledge bases and uploads](references/kb.md)
- [Tags](references/tag.md)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Guidance]

**Output Format:** [Markdown with note links and optional CLI commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May include note titles, IDs, summaries, links, and confirmed operation status; does not expose full credentials.]

## Skill Version(s):

2.3.1 (source: skill frontmatter and server release)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
