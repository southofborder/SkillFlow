## Description:

Fetches Chinese stock and futures market data via the Tushare API, including stock quotes, futures data, company fundamentals, and macroeconomic indicators, with a required TUSHARE_TOKEN.

This skill is ready for commercial/non-commercial use.

## Publisher:

[manifoldor](https://clawhub.ai/user/manifoldor)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and market-data analysts use this skill to configure and run a Python CLI that retrieves Chinese A-share, futures, company fundamental, and macroeconomic data from Tushare.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The script and installed Python dependencies need access to the Tushare API token.

Mitigation: Install in an isolated virtual environment, pin dependency versions, and keep TUSHARE_TOKEN scoped to the shell or environment that runs the skill.

Risk: The release uses an unpinned Python dependency installation for tushare and pandas.

Mitigation: Review dependency provenance and install reviewed, pinned versions before using the skill in controlled environments.

Risk: Some Tushare interfaces may require account points or paid permissions, which can lead to missing or incomplete data.

Mitigation: Confirm Tushare account entitlements and API coverage before relying on returned market data.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/manifoldor/skills/tushare)
- [Tushare official site](https://tushare.pro)
- [Tushare token registration](https://tushare.pro/weborder/#/login?reg=503098)
- [Tushare stock API documentation](https://tushare.pro/document/2?doc_id=14)
- [Tushare futures API documentation](https://tushare.pro/document/2?doc_id=134)
- [Stock API reference](references/stock_api.md)
- [Futures API reference](references/futures_api.md)

## Skill Output:

**Output Type(s):** [text, JSON, shell commands, configuration guidance]

**Output Format:** [Markdown guidance with bash commands and CLI text or JSON output]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires TUSHARE_TOKEN and the Python packages tushare and pandas.]

## Skill Version(s):

1.0.9 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
