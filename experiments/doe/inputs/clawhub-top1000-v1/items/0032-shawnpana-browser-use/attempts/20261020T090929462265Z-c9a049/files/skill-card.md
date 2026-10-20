## Description:

Automates browser interactions for web testing, form filling, screenshots, and data extraction.

This skill is ready for commercial/non-commercial use.

## Publisher:

[shawnpana](https://clawhub.ai/user/shawnpana)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and agents use this skill to navigate websites, inspect page state, fill forms, capture screenshots, extract web data, and manage browser sessions through the browser-use CLI.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Agent-controlled browser sessions can access sensitive websites, authenticated accounts, cookies, and profile data.

Mitigation: Use real Chrome profiles, cookie import/export, profile synchronization, and raw CDP cookie or network commands only when the user explicitly intends that access.

Risk: Tunneling can make a local service reachable from the internet.

Mitigation: Start tunnels only for intended ports, avoid exposing sensitive local services, and stop tunnels after use.

Risk: Cloud browser use can depend on an API key and persistent cloud profile.

Mitigation: Confirm cloud-browser intent before connecting, protect BROWSER_USE_API_KEY, and close cloud sessions when finished.

## Reference(s):

- [Browser Use skill page](https://clawhub.ai/shawnpana/skills/browser-use)
- [browser-use CLI README](https://github.com/browser-use/browser-use/blob/main/browser_use/skill_cli/README.md)
- [Raw CDP & Python Session Reference](references/cdp-python.md)
- [Multiple Browser Sessions](references/multi-session.md)
- [Chrome DevTools Protocol docs](https://chromedevtools.github.io/devtools-protocol/)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance with inline shell commands and code snippets]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May direct agents to produce screenshots, extracted web data, browser state, cookies, or configuration values through browser-use commands.]

## Skill Version(s):

2.0.1 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
