## Description:

iMessage/SMS CLI for listing chats, history, watch, and sending.

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Developers and macOS power users use this skill to inspect Messages.app chats, retrieve message history and attachments, watch conversations, and send iMessage/SMS messages from a CLI workflow.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill installs an unpinned third-party CLI that can access sensitive Messages data.

Mitigation: Install only after reviewing and trusting the Homebrew tap and selected imsg version.

Risk: The skill may require terminal access to Messages data and permission to control Messages.app for sending.

Mitigation: Grant only the minimum macOS permissions needed, avoid broad Full Disk Access where possible, and remove permissions when no longer needed.

Risk: Message sending can affect real recipients through iMessage or SMS.

Mitigation: Keep manual confirmation of recipient, service, attachments, and message text before every send action.

## Reference(s):

- [imsg homepage](https://imsg.to)
- [ClawHub skill page](https://clawhub.ai/steipete/skills/imsg)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, guidance]

**Output Format:** [Markdown with inline shell commands and JSON-oriented command examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Command examples may request JSON output from the imsg CLI.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
