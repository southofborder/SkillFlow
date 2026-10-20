## Description:

Use the Bluesky CLI for timeline, search, notifications, posts, replies, threads, images, likes, reposts, follows, blocks, and mutes.

This skill is ready for commercial/non-commercial use.

## Publisher:

[jeffaf](https://clawhub.ai/user/jeffaf)

### License/Terms of Use:

MIT-0

## Use Case:

External users and developers use this skill to operate a Bluesky account from an agent-assisted CLI workflow, including reading feeds and notifications, drafting posts, creating threads, and managing follows, blocks, mutes, likes, and reposts.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The CLI can post publicly and change Bluesky account state through follows, blocks, mutes, reposts, deletes, and related actions.

Mitigation: Use --dry-run for public post, reply, quote, and thread drafts; verify exact account or post targets before mutations; use --yes only after the user confirms the intended action.

Risk: Bluesky app passwords and session tokens grant access to operate the user's account.

Mitigation: Use the hidden login prompt, keep app passwords out of chat and shell history, store only the session token, and rely on owner-only config-file permissions.

Risk: The wrapper can install the atproto Python dependency into a local virtual environment.

Mitigation: Review or pin dependencies when stronger supply-chain control is required.

## Reference(s):

- [ClawHub Bluesky skill page](https://clawhub.ai/jeffaf/skills/bluesky)
- [Bluesky](https://bsky.app)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance with inline shell commands and optional JSON output from read commands.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Read commands can return JSON with --json; account-changing commands should be reviewed and may require explicit confirmation.]

## Skill Version(s):

1.6.3 (source: server evidence, frontmatter, changelog)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
