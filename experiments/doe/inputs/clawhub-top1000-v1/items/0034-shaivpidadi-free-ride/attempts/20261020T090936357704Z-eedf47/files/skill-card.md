## Description:

Manages free AI models from OpenRouter for OpenClaw by ranking models, configuring fallbacks for rate-limit handling, and updating OpenClaw model configuration.

This skill is ready for commercial/non-commercial use.

## Publisher:

[shaivpidadi](https://clawhub.ai/user/shaivpidadi)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and OpenClaw users use this skill to configure free OpenRouter models as primary and fallback models, reducing API costs and keeping agent sessions running through rate limits.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill handles an OpenRouter API key and includes unsafe secret-check instructions.

Mitigation: Use a non-printing presence check for the key and avoid commands that print secrets to the terminal.

Risk: The skill changes OpenClaw model behavior by editing model and fallback configuration.

Mitigation: Review the target OpenClaw configuration before and after running the skill, and restart the gateway only after confirming the intended model changes.

Risk: The optional watcher can run continuously in the background and automatically rotate model configuration.

Mitigation: Run the watcher only when continuous health checks and automatic rotation are desired, preferably under an explicit process supervisor.

Risk: The documented installer uses an unpinned @latest package reference.

Mitigation: Prefer a pinned installer version for reproducible installation.

## Reference(s):

- [ClawHub Free Ride release page](https://clawhub.ai/shaivpidadi/skills/free-ride)
- [Publisher profile](https://clawhub.ai/user/shaivpidadi)
- [OpenRouter API keys](https://openrouter.ai/keys)
- [OpenRouter API reference](https://openrouter.ai/docs/api-reference/overview#headers)
- [OpenClaw](https://github.com/openclaw/openclaw)

## Skill Output:

**Output Type(s):** [text, shell commands, configuration, guidance]

**Output Format:** [Markdown with inline shell commands and configuration guidance]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May recommend commands that edit OpenClaw model configuration and use an OpenRouter API key.]

## Skill Version(s):

1.0.11 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
