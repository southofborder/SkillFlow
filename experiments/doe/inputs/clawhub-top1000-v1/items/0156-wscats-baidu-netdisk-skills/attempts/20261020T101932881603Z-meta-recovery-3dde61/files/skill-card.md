## Description:

Baidu Netdisk file management via CLI for upload, download, transfer, sharing, search, move, copy, rename, folder creation, deletion, and agent memory backup or restore.

This skill is ready for commercial/non-commercial use.

## Publisher:

[wscats](https://clawhub.ai/user/wscats)

### License/Terms of Use:

MIT-0

## Use Case:

External users and developers use this skill to manage files in Baidu Netdisk through the bdpan CLI, including file operations, public sharing, and transfer workflows. Users in supported Claw environments can also back up or restore selected agent memory files.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill can access and modify Baidu Netdisk files and selected local agent-memory files.

Mitigation: Install and use it only after confirming that this access is acceptable, and review planned file operations before execution.

Risk: Install, self-update, restore, and uninstall flows can make high-impact changes.

Mitigation: Review installer and update behavior carefully, avoid --yes or --force for install, update, restore, or uninstall, and verify custom configuration paths before use.

Risk: Public sharing can expose files to anyone with the link and extraction code.

Mitigation: Confirm public shares before creation, verify the selected files, and prefer time-limited shares unless a permanent link is required.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/wscats/skills/baidu-netdisk-skills)
- [Metadata repository link](https://github.com/wscats/baidu-netdisk-skills)
- [Authentication Guide](artifact/reference/authentication.md)
- [bdpan CLI Command Reference](artifact/reference/bdpan-commands.md)
- [Usage Examples](artifact/reference/examples.md)
- [Troubleshooting Guide](artifact/reference/troubleshooting.md)
- [Development Notes](artifact/reference/notes.md)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown responses with inline shell commands and optional JSON CLI output]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May include user confirmations, risk warnings, progress reports, and Baidu Netdisk or local memory file paths.]

## Skill Version(s):

1.1.5 (source: server release evidence and artifact metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
