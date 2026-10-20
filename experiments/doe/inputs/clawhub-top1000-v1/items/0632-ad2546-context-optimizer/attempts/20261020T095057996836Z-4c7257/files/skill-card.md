## Description:

Advanced context management with auto-compaction and dynamic context optimization for DeepSeek's 64k context window.

This skill is ready for commercial/non-commercial use.

## Publisher:

[ad2546](https://clawhub.ai/user/ad2546)

### License/Terms of Use:

MIT

## Use Case:

Developers and agent builders use this skill to keep long DeepSeek conversations within a 64k context window by compacting, filtering, and retrieving relevant conversation content.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The archive feature can retain pruned conversation content on disk and later reintroduce it into prompts.

Mitigation: Disable archive for sensitive work, choose a private archive path when enabled, and review retrieved snippets before using them.

Risk: Chat logging can expose optimization events or context-management details during sensitive sessions.

Mitigation: Set chat logging to none or disable logging when conversations may contain secrets or private data.

Risk: Uninstall commands can delete archive data from the configured path.

Mitigation: Verify archive and skill paths before running deletion commands.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/ad2546/skills/context-optimizer)
- [Project homepage](https://github.com/clawdbot/clawdbot)

## Skill Output:

**Output Type(s):** [Text, Markdown, Code, Shell commands, Configuration, Guidance]

**Output Format:** [Markdown guidance with JavaScript, YAML, and shell command snippets]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Can produce compacted message sets, archive snippets, status summaries, and configuration examples depending on the agent integration.]

## Skill Version(s):

1.0.0 (source: server release metadata and package.json)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
