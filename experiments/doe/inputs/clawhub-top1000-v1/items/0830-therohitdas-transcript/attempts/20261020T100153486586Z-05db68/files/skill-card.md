## Description:

Fetches spoken content from YouTube videos through TranscriptAPI for transcripts, summaries, quotes, translations, fact checking, and other video-grounded research.

This skill is ready for commercial/non-commercial use.

## Publisher:

[therohitdas](https://clawhub.ai/user/therohitdas)

### License/Terms of Use:

MIT-0

## Use Case:

External users, developers, and research assistants use this skill to retrieve YouTube transcripts, timestamps, and video metadata from TranscriptAPI for summarization, quoting, translation, fact checking, and video-based research.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The setup flow can give the agent broad, persistent control over the TranscriptAPI key and account signup.

Mitigation: Create the account yourself when practical, store the key in a dedicated secret manager, and avoid pasting or persisting the key broadly across sessions.

Risk: Transcript requests send video identifiers and account-related data to TranscriptAPI.

Mitigation: Use the skill only for videos and account data you are comfortable sharing with TranscriptAPI.

## Reference(s):

- [TranscriptAPI](https://transcriptapi.com)
- [TranscriptAPI Auth Setup](references/auth-setup.md)
- [ClawHub Transcript Skill](https://clawhub.ai/therohitdas/skills/transcript)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Configuration, Guidance]

**Output Format:** [Markdown with inline shell commands, API request examples, and transcript text or JSON returned from TranscriptAPI]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires TRANSCRIPT_API_KEY and internet access to transcriptapi.com; transcript requests default to text output with timestamps and metadata unless the user asks otherwise.]

## Skill Version(s):

1.5.1 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
