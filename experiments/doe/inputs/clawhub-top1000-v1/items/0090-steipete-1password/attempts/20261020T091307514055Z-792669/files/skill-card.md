## Description:

Set up and use 1Password CLI (op). Use when installing the CLI, enabling desktop app integration, signing in (single or multi-account), or reading/injecting/running secrets via op.

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Developers and operators use this skill to install and authenticate the 1Password CLI, then read, inject, or run commands with secrets while preserving the CLI session state.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Secret values can be exposed in terminal output, logs, chat, or captured terminal panes.

Mitigation: Do not print secrets, keep masking enabled, and avoid disabling masking unless explicitly authorized for a controlled workflow.

Risk: Decrypted passwords, private keys, or configuration values can persist in local project files.

Mitigation: Prefer `op run` or `op inject` workflows that avoid persistent plaintext output; when files are required, use restrictive permissions, cleanup, and credential rotation plans.

Risk: 1Password CLI authentication can fail or prompt repeatedly when commands are run outside the maintained terminal session.

Mitigation: Run sign-in and secret-access commands inside a fresh dedicated tmux session and verify access with `op whoami` before reading secrets.

## Reference(s):

- [1Password CLI get-started](https://developer.1password.com/docs/cli/get-started/)
- [get-started.md](references/get-started.md)
- [cli-examples.md](references/cli-examples.md)
- [ClawHub skill page](https://clawhub.ai/steipete/skills/1password)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown with inline shell commands and configuration guidance]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires the 1Password CLI binary `op`; brew install metadata is available for macOS users.]

## Skill Version(s):

1.0.1 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
