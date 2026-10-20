## Description:

Meta-agent skill for orchestrating complex tasks through autonomous sub-agents.

This skill is ready for commercial/non-commercial use.

## Publisher:

[aatmaan1](https://clawhub.ai/user/aatmaan1)

### License/Terms of Use:


## Use Case:

Developers and engineers use this skill to decompose complex work into coordinated sub-agent tasks, dispatch those agents, monitor file-based status, and consolidate their deliverables.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill coordinates autonomous sub-agents with broad authority to copy files, run commands, write outputs, and retain workspaces.

Mitigation: Use a dedicated workspace, limit input files to what each sub-agent needs, require approval before Bash or write-heavy subtasks, and decide in advance whether workspaces should be archived or deleted.

Risk: Sub-agent work can produce conflicting or incomplete deliverables during parallel execution.

Mitigation: Validate each outbox against its success criteria before consolidation and document unresolved conflicts in the final summary.

## Reference(s):

- [Agent Orchestrator skill page](https://clawhub.ai/aatmaan1/skills/agent-orchestrator)
- [File-Based Communication Protocol](references/communication-protocol.md)
- [Sub-Agent Templates](references/sub-agent-templates.md)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance]

**Output Format:** [Markdown instructions with code snippets, shell commands, generated skill definitions, task files, status JSON, and consolidation summaries.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Outputs are organized through sub-agent inbox, outbox, workspace, and status files.]

## Skill Version(s):

0.1.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
