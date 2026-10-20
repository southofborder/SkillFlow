## Description:

Generate and edit diagrams with the mcp-diagram-generator MCP server. Use this skill for new diagrams, existing .drawio/.mmd/.excalidraw edits, network topology, architecture, flowchart, swimlane, sequence, class, ER, and Excalidraw whiteboard work. Always use this skill when the user asks to draw, generate, revise, or export any diagram.

This skill is ready for commercial/non-commercial use.

## Publisher:

[matthewyin](https://clawhub.ai/user/matthewyin)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and engineers use this skill to create or revise Draw.io, Mermaid, and Excalidraw diagrams for documentation, architecture, network topology, process, UML, data model, and whiteboard workflows.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The recommended setup runs an external MCP server through an unpinned npm package.

Mitigation: Pin and review the mcp-diagram-generator npm package version before use, and run the server in a restricted environment.

Risk: The skill can write diagram files to custom paths and may create output directories plus .diagram-config.json.

Mitigation: Check requested output paths before generation and limit write access to approved workspace locations.

## Reference(s):

- [Format Selection Guide](references/format-selection-guide.md)
- [Interactive Intake Guide](references/interaction-intake-guide.md)
- [JSON Schema Guide](references/json-schema-guide.md)
- [Layout And Quality Guide](references/layout-quality-guide.md)
- [Network Topology Examples](references/network-topology-examples.md)
- [Architecture Diagram Playbook](references/playbook-architecture.md)
- [Excalidraw Playbook](references/playbook-excalidraw.md)
- [Flowchart Playbook](references/playbook-flowchart.md)
- [Network Topology Playbook](references/playbook-network-topology.md)
- [Swimlane Playbook](references/playbook-swimlane.md)
- [UML And Data Model Playbook](references/playbook-uml.md)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance, files]

**Output Format:** [Markdown guidance plus generated .drawio, .mmd, or .excalidraw diagram files]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May initialize .diagram-config.json and create diagram output directories; custom output paths should be reviewed before generation.]

## Skill Version(s):

1.1.7 (source: ClawHub release metadata; package.json reports 1.2.1)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
