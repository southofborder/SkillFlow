## Description:

Finance Radar provides Yahoo Finance-based stock and cryptocurrency analysis, portfolio and watchlist tracking, dividend summaries, stock scoring, trend and rumor scans, earnings reaction checks, batch CSV export, and SkillPay billing at 0.001 USDT per call.

This skill is ready for commercial/non-commercial use.

## Publisher:

[elevo11](https://clawhub.ai/user/elevo11)

### License/Terms of Use:


## Use Case:

External users and agents use Finance Radar to retrieve market analysis, portfolio and watchlist views, dividend summaries, stock scores, trend scans, rumor signals, and CSV batch exports for stock and cryptocurrency tickers.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Runtime dependency installation can fetch and execute unpinned package code.

Mitigation: Preinstall and pin yfinance in the execution environment before running the skill.

Risk: Billing operations can charge a SkillPay account and expose keys when credentials are passed on the command line.

Mitigation: Store SKILLPAY_API_KEY in an environment secret and require explicit user approval before every charge.

Risk: Portfolio, watchlist, and batch export commands can persist financial data or CSV files.

Mitigation: Require explicit user approval before portfolio or watchlist writes and before CSV export.

## Reference(s):

- [8-Dimension Stock Scoring Model](references/scoring-model.md)
- [Finance Radar ClawHub Page](https://clawhub.ai/elevo11/skills/finance-radar)

## Skill Output:

**Output Type(s):** [text, json, csv, shell commands, configuration]

**Output Format:** [Plain text or JSON CLI output, with optional CSV export for batch analysis.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires ticker inputs; billing operations require SKILLPAY_API_KEY.]

## Skill Version(s):

1.1.0 (source: server release metadata; changelog: Added batch analysis with CSV export)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
