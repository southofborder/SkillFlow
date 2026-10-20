## Description:

Persistent TODO scratch pad for tracking tasks across sessions. Use when the user asks to add, list, complete, remove, or summarize tasks in a portable workspace Markdown file. Uses stable task IDs and exact matching; heartbeat reporting is opt-in and count-only.

This skill is ready for commercial/non-commercial use.

## Publisher:

[jdrhyne](https://clawhub.ai/user/jdrhyne)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and agent users use this skill to maintain a portable Markdown TODO list across sessions, including adding, listing, completing, removing, and summarizing tasks with stable task IDs.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill can create and modify the configured TODO file and adjacent backup, lock, and counter files.

Mitigation: Use the default workspace TODO.md or set TODO_FILE deliberately so it does not target an unrelated file.

Risk: Task removal is destructive once the confirmation command is approved.

Mitigation: Preview the exact task ID and text first, then remove one stable ID at a time only after explicit approval.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/jdrhyne/skills/todo-tracker)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Configuration]

**Output Format:** [Markdown task file updates and plain text command output]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Writes to a configurable local TODO file with adjacent backup, lock, and monotonic ID counter files; heartbeat output is opt-in and count-only.]

## Skill Version(s):

1.1.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
