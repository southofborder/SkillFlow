## Description:

Work with Obsidian vaults as a knowledge base: search notes, read and create Markdown notes, edit note content, manage tags and wikilinks, and suggest folders.

This skill is ready for commercial/non-commercial use.

## Publisher:

[ruslanlanket](https://clawhub.ai/user/ruslanlanket)

### License/Terms of Use:


## Use Case:

Developers and knowledge workers use this skill to query, organize, and update an Obsidian Markdown vault through agent-guided search, note creation, tagging, wikilink inspection, and targeted note edits.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill can read and write persistent local Markdown files in an Obsidian vault, including replace, clear, and broad edit operations.

Mitigation: Restrict the configured vault path, keep backups, and require explicit confirmation before replace, clear, or broad edit commands.

Risk: File handling can escape the intended vault boundary according to the authoritative security summary.

Mitigation: Use a dedicated vault path, avoid untrusted note or folder names, and review resolved target paths before write operations.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/ruslanlanket/skills/obsidian-direct)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown responses with inline shell commands and JSON-capable CLI results]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May read, create, and modify Markdown files in a configured Obsidian vault.]

## Skill Version(s):

1.0.0 (source: evidence.release.version and artifact/_meta.json)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
