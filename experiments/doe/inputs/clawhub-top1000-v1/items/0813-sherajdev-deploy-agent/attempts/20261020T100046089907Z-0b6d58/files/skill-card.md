## Description:

Multi-step deployment agent for full-stack apps. Build -> Test -> GitHub -> Cloudflare Pages with human approval at each step.

This skill is ready for commercial/non-commercial use.

## Publisher:

[sherajdev](https://clawhub.ai/user/sherajdev)

### License/Terms of Use:


## Use Case:

Developers and engineers use this skill to guide full-stack application deployment through local build and test steps, GitHub repository preparation, and Cloudflare Pages deployment. It also provides Next.js and Cloudflare D1 configuration checks and remediation guidance.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The security verdict is suspicious because approval and deployment claims do not match the included script behavior.

Mitigation: Review each deployment step manually and do not treat the skill's approval prompts or reported deployment status as authoritative.

Risk: The skill stores local deployment state and evidence notes that state handling can affect files outside its intended state folder.

Mitigation: Use simple deployment names and inspect local state paths before running commands that create, update, or remove deployment state.

Risk: The skill shows Cloudflare token configuration and relies on GitHub and Cloudflare CLIs for deployment-related actions.

Mitigation: Use least-privilege Cloudflare and GitHub credentials, avoid broad long-lived tokens, and verify CLI authentication before use.

Risk: The deployment guide recommends dependency changes that may affect build reproducibility.

Mitigation: Prefer pinned dependencies, lockfile-based installs, and reviewed package updates before deployment.

## Reference(s):

- [Cloudflare Pages Next.js Framework Guide](https://developers.cloudflare.com/pages/framework-guides/nextjs/)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance with inline shell commands and configuration snippets]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Outputs include deployment state summaries, prerequisite checks, command suggestions, and Cloudflare Pages and D1 configuration guidance.]

## Skill Version(s):

1.1.0 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
