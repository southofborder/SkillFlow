## Description:

Create and manage Docker Desktop sandbox VMs for isolated agent execution, package exploration, network proxy control, and workspace-mounted command runs.

This skill is ready for commercial/non-commercial use.

## Publisher:

[gitgoodordietrying](https://clawhub.ai/user/gitgoodordietrying)

### License/Terms of Use:


## Use Case:

Developers and agent users use this skill to run agents, commands, and package exploration workflows inside Docker Desktop sandbox environments with workspace mounting and outbound network controls.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill may overstate sandbox safety for hostile or truly untrusted code.

Mitigation: Review the skill before installation for hostile-code workflows, verify Docker socket isolation, and treat sandboxing as one control rather than a complete trust boundary.

Risk: Mounted workspaces can be modified by code running inside the sandbox.

Mitigation: Use disposable checkouts, backups, or read-only copies when evaluating destructive or untrusted workloads.

Risk: Outbound network access can expose data or enable unwanted communication if proxy policy is too broad.

Mitigation: Use deny-by-default network rules and allow only the domains required for the task.

Risk: Resetting Docker sandbox state can remove sandbox data.

Mitigation: Avoid reset operations unless sandbox state loss is acceptable or the state has been saved elsewhere.

## Reference(s):

- [Docker Desktop Sandbox documentation](https://docs.docker.com/desktop/features/sandbox/)
- [ClawHub skill page](https://clawhub.ai/gitgoodordietrying/skills/docker-sandbox)

## Skill Output:

**Output Type(s):** [Guidance, Markdown, Shell commands, Configuration]

**Output Format:** [Markdown with bash, JavaScript, and configuration snippets]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Includes lifecycle commands, network proxy examples, workspace path mapping, environment notes, and troubleshooting guidance.]

## Skill Version(s):

1.0.0 (source: ClawHub release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
