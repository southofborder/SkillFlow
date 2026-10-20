## Description:

LinkedIn automation via browser relay or cookies for messaging, profile viewing, and network actions.

This skill is ready for commercial/non-commercial use.

## Publisher:

[biostartechnology](https://clawhub.ai/user/biostartechnology)

### License/Terms of Use:


## Use Case:

External users and agents use this skill to operate LinkedIn through browser automation for checking messages, viewing profiles, searching people, and sending messages or connection requests with user confirmation.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The session-cookie method can expose a reusable LinkedIn session credential if copied or stored insecurely.

Mitigation: Prefer the Chrome extension relay or an isolated browser profile; use the li_at cookie only with secure secret storage and a clear need.

Risk: Automated LinkedIn actions can send messages or connection requests too quickly or without intended approval.

Mitigation: Require explicit confirmation before sending messages or connection requests, and keep automation rate-limited.

## Reference(s):

- [ClawHub LinkedIn skill page](https://clawhub.ai/biostartechnology/skills/linkedin)
- [LinkedIn](https://linkedin.com)

## Skill Output:

**Output Type(s):** [Guidance, Configuration, Browser tool commands]

**Output Format:** [Markdown with browser tool command examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires an authenticated LinkedIn browser session or securely stored session cookie; sensitive actions require explicit user confirmation.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
