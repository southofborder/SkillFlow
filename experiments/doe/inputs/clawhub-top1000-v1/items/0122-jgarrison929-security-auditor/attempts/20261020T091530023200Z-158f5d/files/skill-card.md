## Description:

Use when reviewing code for security vulnerabilities, implementing authentication flows, auditing OWASP Top 10, configuring CORS/CSP headers, handling secrets, input validation, SQL injection prevention, XSS protection, or any security-related code review.

This skill is ready for commercial/non-commercial use.

## Publisher:

[jgarrison929](https://clawhub.ai/user/jgarrison929)

### License/Terms of Use:


## Use Case:

Developers and engineers use this skill to review application code and architecture for security vulnerabilities, OWASP Top 10 risks, authentication and authorization issues, unsafe input handling, secrets exposure, and dependency security concerns.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill may advise changes in sensitive areas such as authentication, secrets, middleware, database schema, security headers, and package files.

Mitigation: Require explicit human approval and review before applying changes to protected files or security-critical code paths.

Risk: The skill includes dependency audit and update commands, including unpinned npm tool execution suggestions.

Mitigation: Treat dependency commands as recommendations, prefer pinned or locally locked tooling, and review package changes before execution.

## Reference(s):


## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance]

**Output Format:** [Structured Markdown security audit findings with code examples and command suggestions]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Findings are organized by severity with file locations, fixes, and risk notes when source context supports them.]

## Skill Version(s):

1.0.0 (source: frontmatter and server-resolved release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
