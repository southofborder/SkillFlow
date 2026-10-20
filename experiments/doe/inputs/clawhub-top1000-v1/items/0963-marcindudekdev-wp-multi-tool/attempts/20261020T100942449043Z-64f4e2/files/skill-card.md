## Description:

Guides WordPress site health audits and performance troubleshooting with WP-CLI diagnostics and, with approval, database cleanup and configuration changes.

This skill is ready for commercial/non-commercial use.

## Publisher:

[marcindudekdev](https://clawhub.ai/user/marcindudekdev)

### License/Terms of Use:

MIT-0

## Use Case:

WordPress site operators and developers use this skill to assess site health, investigate slow queries and database bloat, and review proposed performance fixes. Basic diagnostics work without the paid plugin; plugin-specific monitoring requires it.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Cleanup commands can permanently delete WordPress data.

Mitigation: Require explicit approval for each write operation and take a database backup before cleanup.

Risk: Database optimization and configuration changes can disrupt a live site.

Mitigation: Review the proposed commands and site impact before approving table optimization or wp-config.php edits.

Risk: Activating the plugin changes site behavior but is not included among the declared write operations.

Mitigation: Require explicit user approval before running plugin activation commands.

## Reference(s):

- [WP Multitool skill on ClawHub](https://clawhub.ai/marcindudekdev/skills/wp-multi-tool)
- [WP Multitool website and documentation](https://wpmultitool.com)

## Skill Output:

**Output Type(s):** [Analysis, Shell commands, Configuration guidance]

**Output Format:** [Markdown with WP-CLI commands and site health findings]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Plugin commands may return JSON; proposed write operations require user confirmation.]

## Skill Version(s):

1.9.14 (source: ClawHub release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
