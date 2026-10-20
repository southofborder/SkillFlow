## Description:

Query and trade on Polymarket prediction markets: check odds, trending markets, search events, view order books, place trades, and manage positions.

This skill is ready for commercial/non-commercial use.

## Publisher:

[mvanhorn](https://clawhub.ai/user/mvanhorn)

### License/Terms of Use:

MIT

## Use Case:

External users and developers use this skill to browse Polymarket prediction markets, inspect odds and order books, and manage wallet-backed trades through an agent.

### Deployment Geography for Use:

Global, with the artifact noting availability to US developers.

## Known Risks and Mitigations:

Risk: The skill can guide an agent to perform real-money Polymarket activity through wallet-backed CLI commands.

Mitigation: Use read-only features when possible, keep any wallet limited to funds the user is prepared to risk, and execute trading or cancellation commands only after explicit confirmation.

Risk: The setup instructions include a remote curl-to-sh installer before enabling CLI-backed trading features.

Mitigation: Do not run the installer as written; use a pinned and verified release or manually review the installer before execution.

Risk: Wallet setup stores private key material in a local Polymarket configuration file.

Mitigation: Protect the local configuration file and avoid using wallets that hold more funds than needed for the intended activity.

## Reference(s):

- [Polymarket](https://polymarket.com)
- [Polymarket CLI](https://github.com/Polymarket/polymarket-cli)
- [Polymarket Gamma API](https://gamma-api.polymarket.com)
- [ClawHub Skill Page](https://clawhub.ai/mvanhorn/skills/polymarket)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown and terminal-oriented text with inline shell commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Read-only market queries can run without a wallet; order books, trading, orders, and positions depend on the external Polymarket CLI, wallet configuration, and explicit confirmation for execution.]

## Skill Version(s):

1.2.1 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
