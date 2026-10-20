## Description:

Manage Apple Notes via the `memo` CLI on macOS, including creating, viewing, editing, deleting, searching, moving, and exporting notes.

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Developers and end users on macOS use this skill to manage Apple Notes through the `memo` CLI from an agent workflow, including note creation, lookup, editing, deletion, folder moves, and export.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill depends on an unpinned third-party `memo` CLI installation.

Mitigation: Review and trust the `memo` source before installing; in managed environments, pin and verify the CLI version before use.

Risk: Apple Notes Automation access can expose or modify sensitive note contents.

Mitigation: Grant Automation permission only when needed, limit use to trusted workspaces, and avoid processing notes that contain secrets or regulated data.

Risk: Delete and edit operations can change or remove user notes.

Mitigation: Require explicit user confirmation for destructive or modifying actions and clearly identify the selected note before running the command.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/steipete/skills/apple-notes)
- [memo CLI homepage](https://github.com/antoniorodr/memo)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Configuration, Guidance]

**Output Format:** [Markdown with inline shell commands and concise CLI-result summaries]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires macOS, Apple Notes.app access, and the `memo` binary.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
