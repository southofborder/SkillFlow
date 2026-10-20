## Description:

Writes, fixes, and converts Markdown that renders consistently across GitHub, MDX, Pandoc, documentation sites, chat platforms, and other common Markdown targets.

This skill is ready for commercial/non-commercial use.

## Publisher:

[ivangdavila](https://clawhub.ai/user/ivangdavila)

### License/Terms of Use:

MIT-0

## Use Case:

Developers, technical writers, and agents use this skill to create, repair, convert, lint, and safely render Markdown for specific target parsers and publishing surfaces.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill stores and reuses local Markdown, project, and contact notes across sessions.

Mitigation: Install it only when persistent local recall is desired, and ask the agent to show proposed memory writes before saving notes.

Risk: Private repositories, client documentation, or sensitive contacts may be reflected in local memory if the agent is allowed to persist them.

Mitigation: Review the skill before installation in sensitive workspaces and avoid persisting client or private details unless they are intended for local recall.

Risk: Untrusted Markdown can carry unsafe HTML, link schemes, tracking images, deceptive characters, or secret-bearing snippets.

Mitigation: Sanitize rendered HTML, apply URL-scheme allowlists, avoid rendering untrusted MDX, and strip live credentials to pointers before writing any durable note.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/ivangdavila/skills/markdown)
- [Skill homepage](https://clawic.com/skills/markdown)
- [Markdown skill definition](artifact/SKILL.md)
- [Security guidance](artifact/security.md)
- [Memory template](artifact/memory-template.md)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance]

**Output Format:** [Markdown, code blocks, configuration snippets, shell commands, and concise guidance]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Outputs are target-renderer aware and may include exact byte-level edits, lint or conversion commands, and safety notes for untrusted Markdown.]

## Skill Version(s):

1.0.3 (source: frontmatter and server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
