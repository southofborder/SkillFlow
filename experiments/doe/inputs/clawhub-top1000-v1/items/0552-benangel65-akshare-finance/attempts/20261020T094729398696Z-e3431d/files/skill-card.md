## Description:

Akshare Finance helps agents use AKShare to retrieve public financial market, macroeconomic, and cryptocurrency data for analysis workflows.

This skill is ready for commercial/non-commercial use.

## Publisher:

[benangel65](https://clawhub.ai/user/benangel65)

### License/Terms of Use:


## Use Case:

Developers, analysts, and finance-focused agent users use this skill to fetch public market data, macroeconomic indicators, market overviews, and portfolio monitoring examples through AKShare. Outputs should be treated as data assistance for analysis, not investment advice.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Financial-data outputs may be delayed, incomplete, or unsuitable as the sole basis for trading or investment decisions.

Mitigation: Treat outputs as market-data assistance, verify important results against authoritative sources, and avoid presenting the skill as investment advice.

Risk: The skill depends on AKShare, pandas, and external financial-data services, which can affect reproducibility and availability.

Mitigation: Install in a virtual environment, pin dependency versions for higher-assurance use, and handle upstream service errors or schema changes.

Risk: Localization and market coverage caveats may affect users outside the data sources and markets exposed by AKShare.

Mitigation: Confirm that requested indicators, symbols, and market conventions are supported before relying on the output in a workflow.

## Reference(s):

- [AKShare Documentation](https://akshare.akfamily.xyz/)
- [AKShare GitHub Repository](https://github.com/akfamily/akshare)
- [Skill Reference README](references/README.md)
- [ClawHub Skill Page](https://clawhub.ai/benangel65/skills/akshare-finance)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance with Python and shell snippets; helper scripts emit JSON.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [AKShare calls generally return pandas DataFrames; included helper scripts serialize selected stock, macroeconomic, and cryptocurrency results as JSON.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
