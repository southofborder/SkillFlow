## Description:

Use when you need to control Discord from Clawdbot via the discord tool: send messages, react, post or upload stickers, upload emojis, run polls, manage threads/pins/search, fetch permissions or member/role/channel info, or handle moderation actions in Discord DMs or channels.

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Developers and team operators use this skill to let an agent interact with Discord channels, DMs, messages, reactions, polls, threads, pins, search, role information, and moderation workflows through the configured Clawdbot.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill can perform real Discord actions, including deleting messages, changing roles, moderating users, and uploading local files.

Mitigation: Install it only for Discord bots with least-privilege permissions and require explicit confirmation before destructive, moderation, role-changing, or file-upload actions.

Risk: Untrusted Discord messages could try to authorize uploads from local file paths.

Mitigation: Do not allow Discord message content alone to approve local file uploads; require a trusted operator to confirm the exact file and destination.

## Reference(s):


## Skill Output:

**Output Type(s):** [API Calls, Configuration instructions, Guidance]

**Output Format:** [Markdown with JSON action examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May produce Discord actions that send, edit, delete, upload, moderate, or retrieve content depending on enabled action groups.]

## Skill Version(s):

1.0.1 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
