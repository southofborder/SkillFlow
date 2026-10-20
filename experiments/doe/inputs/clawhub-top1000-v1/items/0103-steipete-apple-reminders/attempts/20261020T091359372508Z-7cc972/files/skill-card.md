## Description:

Manage Apple Reminders via the `remindctl` CLI on macOS (list, add, edit, complete, delete), with support for lists, date filters, and JSON or plain output.

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Developers, operators, and Mac users can use this skill to have an agent inspect and manage Apple Reminders through the `remindctl` command-line tool. It is suited for listing reminders, creating or editing tasks, completing items, deleting reminders, and producing script-friendly reminder output on macOS.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill can guide an agent to change, complete, or delete Apple Reminders once macOS Reminders permission is granted.

Mitigation: Confirm the target reminder ID or list name before mutating reminders, and require explicit user confirmation before delete commands, especially commands using --force or --delete.

## Reference(s):

- [Apple Reminders ClawHub skill page](https://clawhub.ai/steipete/skills/apple-reminders)
- [remindctl project homepage](https://github.com/steipete/remindctl)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Configuration guidance]

**Output Format:** [Markdown with inline shell commands and command-output interpretation]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May reference remindctl JSON, TSV/plain, and quiet output modes when guiding automation.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
