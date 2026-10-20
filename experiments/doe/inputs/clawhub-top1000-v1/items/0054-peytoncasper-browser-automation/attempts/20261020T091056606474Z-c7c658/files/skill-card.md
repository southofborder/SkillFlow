## Description:

Automate web browser interactions using natural language via CLI commands for browsing websites, navigating pages, extracting data, taking screenshots, filling forms, clicking buttons, and interacting with web applications.

This skill is ready for commercial/non-commercial use.

## Publisher:

[peytoncasper](https://clawhub.ai/user/peytoncasper)

### License/Terms of Use:


## Use Case:

Developers and external agents use this skill to navigate websites, perform natural-language page actions, extract structured data, capture screenshots, and manage browser sessions through CLI commands.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Automated browsing can expose visited sites, page contents, screenshots, downloads, or form entries to the configured browser environment and AI provider.

Mitigation: Use only approved sites and data, prefer local-only operation for sensitive work, avoid entering real passwords through natural-language commands, and inspect generated files after use.

Risk: Browser sessions can persist because the skill uses a reusable Chrome profile.

Mitigation: Clear or isolate the browser profile for sensitive sessions and close the browser after each workflow.

Risk: Remote browser mode can be selected automatically when Browserbase credentials are configured.

Mitigation: Check the configured environment before use and remove remote browser credentials when local-only operation is required.

## Reference(s):

- [Browser Automation ClawHub Skill Page](https://clawhub.ai/peytoncasper/skills/browser-automation)
- [Browser Automation CLI Reference](artifact/REFERENCE.md)
- [Browser Automation Examples](artifact/EXAMPLES.md)

## Skill Output:

**Output Type(s):** [Shell commands, JSON, Files, Guidance]

**Output Format:** [Markdown guidance with inline shell commands; CLI commands return JSON and screenshot or download file paths.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May save screenshots under ./agent/browser_screenshots/ and downloads under ./agent/downloads/; browser profiles may persist sessions.]

## Skill Version(s):

1.0.1 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
