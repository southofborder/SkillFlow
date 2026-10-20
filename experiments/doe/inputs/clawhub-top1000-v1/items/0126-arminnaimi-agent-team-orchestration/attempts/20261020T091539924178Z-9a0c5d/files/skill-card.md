## Description:

Orchestrate multi-agent teams with defined roles, task lifecycles, handoff protocols, and review workflows.

This skill is ready for commercial/non-commercial use.

## Publisher:

[arminnaimi](https://clawhub.ai/user/arminnaimi)

### License/Terms of Use:


## Use Case:

Developers and operators use this skill to coordinate sustained multi-agent workflows with clear roles, task states, handoff protocols, shared artifact paths, and review gates.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Scheduled ops examples or agent-spawning workflows can modify shared task records or run without intended oversight if schedules, permissions, artifact paths, and approval points are left implicit.

Mitigation: Before use, set explicit schedules, permissions, artifact paths, and human approval points for spawning agents or modifying shared task records.

## Reference(s):

- [ClawHub Skill Page](https://clawhub.ai/arminnaimi/skills/agent-team-orchestration)
- [Team Setup](references/team-setup.md)
- [Task Lifecycle](references/task-lifecycle.md)
- [Communication](references/communication.md)
- [Patterns](references/patterns.md)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance with inline command and path examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Produces operational playbooks, role definitions, handoff templates, task lifecycle guidance, and review workflow guidance.]

## Skill Version(s):

1.0.0 (source: server-resolved release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
