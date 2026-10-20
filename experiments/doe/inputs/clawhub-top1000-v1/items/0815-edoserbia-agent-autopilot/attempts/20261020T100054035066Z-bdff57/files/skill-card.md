## Description:

Self-driving agent workflow with heartbeat-driven task execution, day/night progress reports, and long-term memory consolidation.

This skill is ready for commercial/non-commercial use.

## Publisher:

[edoserbia](https://clawhub.ai/user/edoserbia)

### License/Terms of Use:


## Use Case:

Developers and agent operators use this skill to configure an autonomous agent workflow that tracks tasks, advances work on heartbeat intervals, reports progress, and maintains long-term project memory.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill configures an autonomous heartbeat loop that can continue creating and executing tasks without a natural stop condition.

Mitigation: Use it only in an isolated workspace with limited tool permissions, and require explicit approval for new tasks, external APIs, commits, network access, and destructive or account-impacting actions.

Risk: The workflow includes persistent memory rewriting, which can preserve incorrect decisions or remove useful context.

Mitigation: Keep version history for memory files, review MEMORY.md changes before accepting them, and require approval for any memory rewrite.

Risk: The initialization script creates workspace directories, copies todo-management from local or global locations, and writes report-state.json.

Mitigation: Inspect the target workspace path before running the script, run it in a non-production workspace first, and verify the copied todo-management skill before enabling automation.

Risk: The example workflow mentions quantitative trading use cases, which could be misapplied to real financial activity.

Mitigation: Do not connect production credentials, trading accounts, or financial APIs until human approval gates and environment-specific controls are in place.

## Reference(s):

- [Example setup guide](references/example-setup.md)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance with bash commands and JSON configuration snippets]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Produces heartbeat, reporting, memory, and workspace initialization guidance for an agent configured with todo-management.]

## Skill Version(s):

1.4.1 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
