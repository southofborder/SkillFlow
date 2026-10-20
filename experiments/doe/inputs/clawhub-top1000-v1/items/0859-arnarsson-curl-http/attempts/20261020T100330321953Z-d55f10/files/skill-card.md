## Description:

Essential curl commands for HTTP requests, API testing, and file transfers.

This skill is ready for commercial/non-commercial use.

## Publisher:

[arnarsson](https://clawhub.ai/user/arnarsson)

### License/Terms of Use:


## Use Case:

Developers and engineers use this skill as a curl reference for HTTP requests, API testing, file transfers, authentication, debugging, and scripting patterns.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Examples that include passwords, API keys, bearer tokens, cookies, verbose output, or trace files can expose secrets if copied directly.

Mitigation: Replace placeholders with protected local configuration, prefer authorization headers over URL query keys, and redact logs, traces, and shell history before sharing.

Risk: The TLS bypass example using curl -k disables certificate verification.

Mitigation: Use curl -k only in controlled testing with known endpoints, and keep certificate verification enabled for production or sensitive traffic.

Risk: Upload, download, cookie, and proxy examples can transfer or route sensitive data when adapted to real services.

Mitigation: Verify destination URLs, proxy settings, file paths, and cookie files before execution, and avoid sending sensitive files or credentials to untrusted endpoints.

## Reference(s):

- [Curl homepage](https://curl.se/)
- [Curl documentation](https://curl.se/docs/)
- [MDN HTTP request methods](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods)
- [ClawHub skill page](https://clawhub.ai/arnarsson/skills/curl-http)
- [Publisher profile](https://clawhub.ai/user/arnarsson)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, guidance]

**Output Format:** [Markdown with inline bash code blocks]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires the curl binary for examples that are executed by a user or agent.]

## Skill Version(s):

1.0.0 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
