## Description:

Parse, search, and analyze application logs across formats. Use when debugging from log files, setting up structured logging, analyzing error patterns, correlating events across services, parsing stack traces, or monitoring log output in real time.

This skill is ready for commercial/non-commercial use.

## Publisher:

[gitgoodordietrying](https://clawhub.ai/user/gitgoodordietrying)

### License/Terms of Use:


## Use Case:

Developers and engineers use this skill to inspect application logs, find error patterns, parse stack traces, analyze structured JSON logs, monitor log output, and correlate events across services.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Logs can contain personal data, secrets, credentials, and other sensitive operational details.

Mitigation: Use the skill only on logs you are authorized to inspect, avoid printing or sharing sensitive fields, and redact personal data and secrets before exporting results.

Risk: Structured logging examples may introduce dependency risk if adapted without version control.

Mitigation: Pin dependency versions when adapting the Node.js, Python, or Go structured logging examples in real projects.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/gitgoodordietrying/skills/log-analyzer)
- [ClawHub publisher profile](https://clawhub.ai/user/gitgoodordietrying)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance with inline shell commands and code examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May include log search commands, parsing snippets, structured logging examples, monitoring pipelines, and error summary approaches.]

## Skill Version(s):

1.0.0 (source: server-resolved release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
