## Description:

Automatically fetches YouTube video transcripts, detects YouTube URLs, generates structured summaries with metadata and key insights, and sends full transcripts to messaging platforms.

This skill is ready for commercial/non-commercial use.

## Publisher:

[abe238](https://clawhub.ai/user/abe238)

### License/Terms of Use:

MIT

## Use Case:

External users and developers use this skill to summarize YouTube videos from URLs or video IDs, fetch available transcript text, and optionally deliver transcript files through Telegram.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Unpinned third-party Node dependency installation can execute changing code during setup.

Mitigation: Review and pin dependency revisions before installation, and run npm install/build steps in a controlled environment.

Risk: Full transcripts may be stored locally or sent to Telegram, which can expose private video content or send files to the wrong destination.

Mitigation: Use non-sensitive videos, confirm Telegram chat targets before delivery, and apply transcript retention or deletion controls.

Risk: YouTube URLs and video IDs are untrusted input.

Mitigation: Validate video IDs with a strict allowlist before transcript fetching or shell command construction.

## Reference(s):

- [README](artifact/README.md)
- [Sample Output](artifact/examples/sample-output.md)
- [MCP YouTube Transcript dependency](https://github.com/kimtaeyoon83/mcp-server-youtube-transcript)
- [ClawHub skill page](https://clawhub.ai/abe238/skills/youtube-summarizer)

## Skill Output:

**Output Type(s):** [Markdown, Text, Files, Shell commands, Guidance]

**Output Format:** [Markdown summary plus optional transcript text file and installation or troubleshooting commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May save full transcripts locally and send transcript files to Telegram when used in a Telegram context.]

## Skill Version(s):

1.0.0 (source: SKILL.md frontmatter, package.json, ClawHub release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
