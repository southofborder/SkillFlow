## Description:

Provides filesystem command guidance for directory listing, file and content search, batch file processing, and directory analysis.

This skill is ready for commercial/non-commercial use.

## Publisher:

[amaofx](https://clawhub.ai/user/amaofx)

### License/Terms of Use:


## Use Case:

Developers and technical users use this skill as a filesystem command reference for listing directories, searching files and content, analyzing size and structure, and planning batch file operations.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Batch delete, move, rename, and in-place replacement examples can modify or remove many files if run without review.

Mitigation: Ask the agent to preview affected files before mutation, use dry-run or listing commands where available, and back up important files before bulk operations.

Risk: The skill is a Chinese-language command reference, which may be unsuitable for users expecting English operational guidance.

Mitigation: Install it only when Chinese-language filesystem guidance is desired or ask the agent to translate and explain commands before use.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/amaofx/skills/filesystem)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, guidance]

**Output Format:** [Markdown with inline shell command examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Chinese-language filesystem command reference with safety reminders for bulk mutation commands.]

## Skill Version(s):

1.0.0 (source: ClawHub release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
