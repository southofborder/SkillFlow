## Description:

Tasker docstore task management via tool-dispatch for task lists, due today or overdue views, week planning, add/move/complete flows, and explicit /task commands.

This skill is ready for commercial/non-commercial use.

## Publisher:

[amirbrooks](https://clawhub.ai/user/amirbrooks)

### License/Terms of Use:


## Use Case:

Developers and users who manage task docstores use this skill to turn natural-language task requests and explicit /task commands into tasker_cmd actions for listing, planning, adding, moving, and completing tasks.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill dispatches task-management commands to a separate tasker_cmd plugin and tasker CLI that can change a user's task docstore.

Mitigation: Install only when the plugin and CLI are trusted and allowlisted, and review commands that create, move, complete, or otherwise change tasks.

Risk: Ambiguous task selectors could lead to changes being applied to the wrong task.

Mitigation: Resolve partial selectors before acting, proceed by ID only when there is exactly one match, and keep machine IDs out of human-facing output.

## Reference(s):

- [ClawHub Skill Page](https://clawhub.ai/amirbrooks/skills/task)
- [CLAWDBOT Integration Guide](docs/CLAWDBOT_INTEGRATION.md)

## Skill Output:

**Output Type(s):** [text, shell commands, configuration, guidance]

**Output Format:** [Markdown or plain text with tasker CLI arguments and human-readable task views]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Prefers human-readable Telegram or WhatsApp-compatible formatting and avoids exposing machine IDs in user-facing output.]

## Skill Version(s):

0.1.0 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
