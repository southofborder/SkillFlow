## Description:

A comprehensive Bilibili toolkit that integrates hot trending monitoring, video downloading, video watching/playback, subtitle downloading, and video publishing capabilities into a single skill.

This skill is ready for commercial/non-commercial use.

## Publisher:

[wscats](https://clawhub.ai/user/wscats)

### License/Terms of Use:

MIT-0

## Use Case:

External users and developers use this skill to monitor Bilibili trends, inspect and download videos or subtitles, retrieve playback data, and publish or edit Bilibili videos when they provide session cookies.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill can use full Bilibili session cookies, and server security evidence warns those cookies may be attached to broader network requests than the documentation promises.

Mitigation: Use the skill without credentials when possible; provide cookies only for publishing or high-quality downloads and prefer a throwaway Bilibili account.

Risk: Credential persistence can leave session cookies on disk when BILIBILI_PERSIST or equivalent persistence is enabled.

Mitigation: Avoid BILIBILI_PERSIST unless persistence is required, and clear persisted credentials after use.

Risk: The security verdict is suspicious, so network behavior deserves review before deployment.

Mitigation: Run the skill in an isolated environment and review outbound traffic during evaluation.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/wscats/skills/bilibili-all-in-one)
- [ClawHub publisher profile](https://clawhub.ai/user/wscats)
- [Project homepage from ClawHub metadata](https://github.com/wscats/bilibili-all-in-one)

## Skill Output:

**Output Type(s):** [Text, Markdown, Code, Shell commands, Configuration, Guidance, Files]

**Output Format:** [Markdown, JSON-like API results, shell command snippets, configuration guidance, and local media or subtitle files.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May require Bilibili session cookies for publishing and high-quality downloads; downloaded media and subtitles are written to local output directories.]

## Skill Version(s):

1.0.24 (source: server release evidence and artifact/skill.json)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
