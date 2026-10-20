## Description:

Fetch and read transcripts from YouTube videos. Use when you need to summarize a video, answer questions about its content, or extract information from it.

This skill is ready for commercial/non-commercial use.

## Publisher:

[michaelgathara](https://clawhub.ai/user/michaelgathara)

### License/Terms of Use:


## Use Case:

Developers and external users use this skill to retrieve YouTube transcripts so an agent can summarize videos, answer questions about video content, or extract specific information.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill invokes yt-dlp and can make outbound network requests to retrieve video subtitles.

Mitigation: Use explicit, trusted YouTube URLs and consider URL allowlisting in sensitive environments.

Risk: Transcript retrieval depends on a locally installed yt-dlp binary.

Mitigation: Install yt-dlp from a trusted source and pin or verify the installed version before use in controlled environments.

Risk: Videos without closed captions or auto-generated subtitles cannot produce transcript output.

Mitigation: Confirm that target videos have available subtitles before relying on the skill for summarization or question answering.

## Reference(s):

- [YouTube Watcher on ClawHub](https://clawhub.ai/michaelgathara/skills/youtube-watcher)
- [michaelgathara publisher profile](https://clawhub.ai/user/michaelgathara)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, guidance]

**Output Format:** [Plain text transcript output with Markdown guidance for summarization, question answering, or extraction workflows.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires yt-dlp on PATH and only returns transcript text when captions or auto-generated subtitles are available.]

## Skill Version(s):

1.0.0 (source: frontmatter and server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
