## Description:

Work with Obsidian vaults (plain Markdown notes) and automate via obsidian-cli.

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Developers, knowledge workers, and agents use this skill to locate Obsidian vaults, search notes, create notes, and safely move, rename, or delete Markdown notes through obsidian-cli.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill depends on a third-party Homebrew tap and obsidian-cli binary that can access local Obsidian vault files.

Mitigation: Install only after trust-checking the yakitrak/yakitrak tap and obsidian-cli tool.

Risk: Move and delete operations can modify synced or work vault content.

Mitigation: Review proposed move, rename, and delete commands before execution.

## Reference(s):

- [Obsidian Help](https://help.obsidian.md)

## Skill Output:

**Output Type(s):** [Guidance, Shell commands, Configuration]

**Output Format:** [Markdown with inline shell commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires Obsidian desktop configuration and the obsidian-cli binary.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
