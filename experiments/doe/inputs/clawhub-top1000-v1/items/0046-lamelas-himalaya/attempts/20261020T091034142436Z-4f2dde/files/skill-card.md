## Description:

Himalaya helps agents guide terminal-based email management with the Himalaya CLI, including listing, reading, composing, replying, forwarding, searching, organizing messages, multi-account setup, and MML composition.

This skill is ready for commercial/non-commercial use.

## Publisher:

[lamelas](https://clawhub.ai/user/lamelas)

### License/Terms of Use:


## Use Case:

External users and developers use this skill to operate and troubleshoot Himalaya email workflows from the terminal, including account configuration, message handling, attachment management, and rich message composition.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Email credentials could be exposed if plaintext password examples are copied into shared, backed-up, or source-controlled configuration files.

Mitigation: Use pass, a system keyring, or another secure command-based secret source for Himalaya password fields.

## Reference(s):

- [Himalaya Project Homepage](https://github.com/pimalaya/himalaya)
- [Himalaya Configuration Reference](references/configuration.md)
- [Message Composition with MML](references/message-composition.md)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Configuration, Guidance]

**Output Format:** [Markdown with inline shell commands and TOML configuration examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May include account-specific command examples, email configuration snippets, and operational guidance for Himalaya CLI workflows.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
