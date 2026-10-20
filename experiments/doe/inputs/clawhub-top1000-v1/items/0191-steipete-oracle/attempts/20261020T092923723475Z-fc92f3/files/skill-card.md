## Description:

Use the @steipete/oracle CLI to bundle a prompt plus the right files and get a second-model review (API or browser) for debugging, refactors, design checks, or cross-validation.

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Developers and engineers use Oracle to package a prompt with selected repository files and request an advisory second-model review for debugging, refactoring, design checks, or cross-validation.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Installing or running the external @steipete/oracle CLI without version pinning can create supply-chain exposure.

Mitigation: Pin @steipete/oracle to a reviewed exact version or install it through a locked project dependency before use.

Risk: Attached files and prompts may expose selected source code or sensitive data to external model providers.

Mitigation: Use dry-run and files-report first, attach only necessary files, and redact secrets before sending context.

Risk: API runs may incur usage costs, and browser or remote-host sessions may expose active authenticated sessions if misused.

Mitigation: Require explicit consent before API runs and handle browser sessions, remote-host tokens, and reattachment workflows carefully.

## Reference(s):

- [Oracle ClawHub skill page](https://clawhub.ai/steipete/skills/oracle)

## Skill Output:

**Output Type(s):** [guidance, shell commands, markdown]

**Output Format:** [Markdown with inline shell commands and review guidance]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May include advisory analysis from an external model and commands for dry runs, file reports, browser runs, API runs, rendering, and session reattachment.]

## Skill Version(s):

1.0.1 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
