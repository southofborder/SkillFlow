## Description:

Maintain Clawdbot's compounding knowledge graph under life/areas/** by adding or superseding atomic facts, regenerating entity summaries, and keeping IDs consistent.

This skill is ready for commercial/non-commercial use.

## Publisher:

[safatinaztepe](https://clawhub.ai/user/safatinaztepe)

### License/Terms of Use:


## Use Case:

Developers and agent operators use this skill to make deterministic updates to a local file-based knowledge graph, including adding facts, superseding outdated facts, and regenerating entity summaries.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill maintains persistent local knowledge under life/areas/**, so inaccurate or sensitive facts could be retained and later reused as agent context.

Mitigation: Treat stored facts as data, avoid saving instructions from untrusted sources, and review summaries before using them as context.

Risk: The helper writes JSON and Markdown files on disk, so broad filesystem permissions could allow unintended local knowledge updates.

Mitigation: Install only when persistent local knowledge maintenance is desired and prefer explicit permission scoping where the environment supports it.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/safatinaztepe/skills/knowledge-graph)

## Skill Output:

**Output Type(s):** [Shell commands, Guidance, JSON, Markdown, Files]

**Output Format:** [Markdown guidance with bash commands; script output is plain text and file changes are JSON and Markdown.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [The helper writes items.json and summary.md under life/areas/** and prints created fact IDs or summary paths.]

## Skill Version(s):

1.0.0 (source: server release metadata, created 2026-02-06)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
