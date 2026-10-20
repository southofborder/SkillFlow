## Description:

Use when YouTube is or could be relevant: pasted video, channel, or playlist links; video IDs; @handles; creator lookups; video summaries; quotes; translations; topic research; tutorials; talks; lectures; expert discussions; product reviews; how-to guides; new product announcements; first looks; or cases where video content is fresher or richer than text search.

This skill is ready for commercial/non-commercial use.

## Publisher:

[therohitdas](https://clawhub.ai/user/therohitdas)

### License/Terms of Use:

MIT-0

## Use Case:

Developers, researchers, and general agent users use this skill to search YouTube, inspect channels and playlists, retrieve transcripts, and summarize or analyze video content through TranscriptAPI.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The setup flow asks the agent to create or verify a TranscriptAPI account and persist a TRANSCRIPT_API_KEY for future sessions.

Mitigation: Create the account yourself when possible and provide the API key through an approved secret mechanism rather than broad persistent shell configuration.

Risk: YouTube research queries or private links may be sent to TranscriptAPI when the skill is used.

Mitigation: Ask before sending sensitive research queries or private links to the service, and avoid using the skill for content that should not leave the user's approved environment.

## Reference(s):

- [TranscriptAPI homepage](https://transcriptapi.com)
- [TranscriptAPI OpenAPI specification](https://transcriptapi.com/openapi.json)
- [Authentication setup guide](references/auth-setup.md)
- [ClawHub skill page](https://clawhub.ai/therohitdas/skills/youtube-full)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance with curl examples and JSON or text API responses]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires TRANSCRIPT_API_KEY and internet access to transcriptapi.com; some endpoints consume TranscriptAPI credits.]

## Skill Version(s):

1.6.2 (source: frontmatter and release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
