## Description:

Audit, clean, and optimize Clawdbot's vector memory (LanceDB). Use when memory is bloated with junk, token usage is high from irrelevant auto-recalls, or setting up memory maintenance automation.

This skill is ready for commercial/non-commercial use.

## Publisher:

[dylanbaker24](https://clawhub.ai/user/dylanbaker24)

### License/Terms of Use:


## Use Case:

Developers and operators use this skill to inspect, prune, reseed, and configure Clawdbot vector memory so recalled memories stay relevant and token usage stays controlled.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Unguarded deletion of the LanceDB memory directory can permanently remove vector memories.

Mitigation: Verify backups and decide which facts to reseed before running wipe commands.

Risk: A persistent monthly maintenance job can repeat destructive memory deletion unexpectedly.

Mitigation: Add scheduled maintenance only when intentional, and keep a clear removal path for the cron job.

Risk: Following memory-maintenance guidance without review can remove useful context or preserve the wrong facts.

Mitigation: Review audit results and reseed only concise, valuable memories that match the documented storage guidelines.

## Reference(s):

- [ClawHub Skill Page](https://clawhub.ai/dylanbaker24/skills/memory-hygiene)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown with inline shell commands and JSON configuration snippets]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [None]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
