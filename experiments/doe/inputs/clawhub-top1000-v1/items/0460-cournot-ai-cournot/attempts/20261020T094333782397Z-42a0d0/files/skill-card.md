## Description:

Query Cournot for an event probability and supporting evidence when the user explicitly asks to use Cournot.

This skill is ready for commercial/non-commercial use.

## Publisher:

[cournot-ai](https://clawhub.ai/user/cournot-ai)

### License/Terms of Use:

MIT-0

## Use Case:

External users and agent operators use Cournot to query a crypto event claim and receive a structured probability assessment with supporting evidence. The skill also guides payment confirmation when the free account allowance is exhausted.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Event queries are sent to the external Cournot API.

Mitigation: Use the skill only for explicit Cournot requests and avoid including unrelated sensitive context in the event claim.

Risk: The optional paid wallet flow can transfer real assets and the scanner flagged an unpinned remote wallet setup path.

Mitigation: Do not run wallet setup or payment commands without separate explicit confirmation; prefer a pinned, reviewed wallet install source before using real funds.

## Reference(s):

- [Cournot ClawHub listing](https://clawhub.ai/cournot-ai/skills/cournot)
- [Cournot homepage](https://skill.cournot.ai/)
- [Query flow](references/query-flow.md)
- [Payment flow](references/payment.md)
- [Response formatting](references/response-format.md)
- [Binance Agentic Wallet](https://github.com/binance/binance-skills-hub/tree/main/skills/binance-web3/binance-agentic-wallet)
- [x402 Foundation Buyer Quickstart](https://docs.x402.org/getting-started/quickstart-for-buyers)
- [viem Local Accounts](https://viem.sh/docs/accounts/local)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Configuration guidance]

**Output Format:** [Markdown responses with structured tables and inline shell commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Probability requests use the Cournot external API; paid requests require explicit confirmation before any wallet command is invoked.]

## Skill Version(s):

1.0.0 (source: ClawHub release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
