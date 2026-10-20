## Description:

Capability Evolver analyzes AI agent runtime logs to detect error patterns, regressions, and inefficiencies, then generates structured improvement proposals.

This skill is ready for commercial/non-commercial use.

## Publisher:

[kennyzir](https://clawhub.ai/user/kennyzir)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and engineers use this skill to analyze structured agent runtime logs, assess system health, and generate prioritized reliability or improvement recommendations.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Runtime logs may contain sensitive fields or become too large for automated use.

Mitigation: Pass only needed log fields, keep inputs bounded, and add request-size or log-count caps in automated pipelines.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/kennyzir/skills/capability-evolver-pro)
- [ClawHub publisher profile](https://clawhub.ai/user/kennyzir)

## Skill Output:

**Output Type(s):** [text, guidance]

**Output Format:** [JSON-compatible structured results with text recommendations]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Analyze and evolve actions return bounded lists of detected patterns and recommendations; status returns supported actions, strategies, limits, and runtime metadata.]

## Skill Version(s):

1.0.2 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
