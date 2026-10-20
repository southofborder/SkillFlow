## Description:

Use Exa Search API to search the web and return structured results with titles, URLs, snippets, and optional page text.

This skill is ready for commercial/non-commercial use.

## Publisher:

[xinhai-ai](https://clawhub.ai/user/xinhai-ai)

### License/Terms of Use:


## Use Case:

Developers and agents use this skill when they specifically need Exa-backed web search, including structured results and optional page text retrieval. It can also guide configuration of the required Exa API key.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Search queries, filters, and optional content requests are sent to Exa.

Mitigation: Use this skill only when Exa-backed search is intended and avoid submitting sensitive queries unless that use is approved.

Risk: The skill requires an Exa API key.

Mitigation: Store EXA_API_KEY in a controlled environment and avoid broadly exposing it.

## Reference(s):

- [Exa Documentation](https://exa.ai/docs)
- [ClawHub Skill Page](https://clawhub.ai/xinhai-ai/skills/exa-search)

## Skill Output:

**Output Type(s):** [text, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance with shell command examples; search execution returns JSON from Exa.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires node and EXA_API_KEY; result count is constrained to 1 through 25.]

## Skill Version(s):

1.0.0 (source: release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
