## Description:

Remembers, recalls, and organizes durable facts in a categorized markdown store at ~/Clawic/data/memory/, parallel to built-in agent memory.

This skill is ready for commercial/non-commercial use.

## Publisher:

[ivangdavila](https://clawhub.ai/user/ivangdavila)

### License/Terms of Use:

MIT-0

## Use Case:

External users and developers use this skill to give an agent durable local memory for facts, decisions, people, projects, and longer histories that should remain searchable across sessions.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The memory store is plaintext on the user's machine and can expose sensitive facts to local users, backups, synced folders, or other processes.

Mitigation: Install only when local durable memory is desired; keep the store on appropriate private or encrypted storage and review what gets stored.

Risk: Passwords, API keys, tokens, and similar secrets would be unsafe if written into the memory store.

Mitigation: Do not store secrets; store only a pointer to the user's vault or other secret manager location.

Risk: Cloud sync, git history, and backups can retain facts after deletion from the active markdown files.

Mitigation: Use private sync or version-control locations carefully and warn users that deletion from the store may not remove retained historical copies.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/ivangdavila/skills/memory)
- [Clawic Memory skill page](https://clawic.com/skills/memory)
- [Server-resolved provenance](unavailable)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Configuration, Guidance]

**Output Format:** [Markdown guidance with inline shell commands and local file paths]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Produces agent instructions for creating, updating, searching, maintaining, and deleting local markdown memory files.]

## Skill Version(s):

1.0.7 (source: server evidence and frontmatter)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
