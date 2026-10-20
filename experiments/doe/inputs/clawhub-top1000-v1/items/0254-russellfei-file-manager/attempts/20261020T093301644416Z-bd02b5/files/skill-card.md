## Description:

File Manager helps agents organize local files, batch rename items, find duplicates, and synchronize directories using preview-first Python scripts.

This skill is ready for commercial/non-commercial use.

## Publisher:

[russellfei](https://clawhub.ai/user/russellfei)

### License/Terms of Use:

MIT-0

## Use Case:

External users and developers use this skill to inspect and execute local file-management workflows such as folder organization, duplicate-file cleanup, batch renaming, and one-way directory synchronization. It is most appropriate when the agent can preview filesystem changes before execution and the user can confirm the intended paths.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Bulk rename and sync operations can unexpectedly move, update, or delete files outside the intended scope.

Mitigation: Run scan-only or preview modes first, review all affected paths, and require explicit user confirmation before executing filesystem changes.

Risk: Unattended execution can apply destructive file operations without a final human path check.

Mitigation: Avoid --no-confirm and unattended cron usage for mutating commands, especially rename, sync, and delete workflows.

Risk: Directory sync with overlapping source and target paths can produce unintended copy, update, or deletion behavior.

Mitigation: Use clearly separated source and target directories and avoid sync runs where paths overlap.

Risk: Direct duplicate deletion can remove files the user intended to keep.

Mitigation: Prefer scan-only review or moving duplicates to a quarantine directory before permanent deletion.

## Reference(s):

- [File Management Best Practices](references/best_practices.md)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance]

**Output Format:** [Markdown with inline shell commands and file-operation guidance]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Outputs should preserve preview-first operation and call out when commands can rename, move, copy, or delete local files.]

## Skill Version(s):

1.2.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
