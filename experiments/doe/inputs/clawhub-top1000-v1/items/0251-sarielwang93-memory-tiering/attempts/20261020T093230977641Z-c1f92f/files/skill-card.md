## Description:

Automated multi-tiered memory management (HOT, WARM, COLD). Use this skill to organize, prune, and archive context during memory operations or compactions.

This skill is ready for commercial/non-commercial use.

## Publisher:

[sarielwang93](https://clawhub.ai/user/sarielwang93)

### License/Terms of Use:


## Use Case:

Developers and agent operators use this skill to organize working memory into HOT, WARM, and COLD tiers, prune completed context, and summarize archived information during manual memory maintenance or post-compaction workflows.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill can read and rewrite broad memory files, daily logs, and possible credentials during memory reorganization.

Mitigation: Use explicit user review, backups or version history, mandatory secret redaction, and clear limits on the memory files and date ranges processed.

Risk: Important audit history or private context may be lost or over-summarized during pruning and archival.

Mitigation: Review proposed tier changes before applying them and verify that critical information remains recoverable after reorganization.

## Reference(s):


## Skill Output:

**Output Type(s):** [Guidance, Markdown, Files]

**Output Format:** [Markdown memory updates and concise status text]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May read and rewrite memory tier files and recent daily logs when invoked.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
