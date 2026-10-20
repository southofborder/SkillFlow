## Description:

Builds or modernizes DCC-MCP adapters and standalone studio MCP services.

This skill is ready for commercial/non-commercial use.

## Publisher:

[loonghao](https://clawhub.ai/user/loonghao)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and studio engineers use this skill to create or update integrations for digital content creation applications and private studio services, with guidance on runtime wiring, validation, and release.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Generated service, gateway, UI-control, install, memory, or feedback changes could alter local systems or workflows.

Mitigation: Review proposed changes before running them and validate the requested behavior in the intended environment.

Risk: Service integration could expose credentials or private endpoints.

Mitigation: Keep credentials in the project owner's secret store or environment and require operator controls before exposing an intranet service.

## Reference(s):

- [Skill homepage (declared)](https://github.com/dcc-mcp/dcc-mcp-agent-plugins/blob/main/plugins/dcc-mcp/skills/dcc-mcp-creator/SKILL.md)
- [Adapter and service workflow](references/ADAPTER_WORKFLOW.md)
- [Internal standalone service workflow](references/INTERNAL_SERVICE_WORKFLOW.md)
- [Runtime integration](references/RUNTIME_INTEGRATION.md)
- [Testing and release](references/TESTING_AND_RELEASE.md)

## Skill Output:

**Output Type(s):** [Code, Configuration instructions, Shell commands, Guidance]

**Output Format:** [Source files and Markdown guidance with code and command examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May modify files in the user's project; live-host validation is separate from source checks.]

## Skill Version(s):

0.19.113 (source: SKILL.md metadata and ClawHub release)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
