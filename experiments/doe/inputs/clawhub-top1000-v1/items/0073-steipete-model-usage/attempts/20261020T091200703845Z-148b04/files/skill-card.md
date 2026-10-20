## Description:

Summarizes CodexBar local cost usage by model for Codex or Claude, including the current model or a full model breakdown.

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Developers and engineers use this skill to inspect local Codex or Claude model cost usage from CodexBar and produce current-model or all-model cost summaries for scripting or review.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill depends on the third-party CodexBar CLI and can inspect local Codex or Claude usage logs for cost summaries.

Mitigation: Install only in environments where CodexBar and the publisher are trusted, and confirm that local usage-log access is acceptable.

Risk: Per-model summaries are cost-only because CodexBar output does not split tokens by model.

Mitigation: Use the output for cost review rather than token-level attribution, and consult raw CodexBar data when token totals are needed.

## Reference(s):

- [CodexBar CLI quick ref](references/codexbar-cli.md)
- [ClawHub skill page](https://clawhub.ai/steipete/skills/model-usage)

## Skill Output:

**Output Type(s):** [text, json, shell commands, guidance]

**Output Format:** [Plain text or JSON, with Markdown guidance and shell command examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Cost-only per-model summaries; tokens are not split by model in CodexBar output.]

## Skill Version(s):

1.0.0 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
