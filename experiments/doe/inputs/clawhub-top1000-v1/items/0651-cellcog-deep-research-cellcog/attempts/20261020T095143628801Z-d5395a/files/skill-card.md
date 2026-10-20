## Description:

AI deep research powered by CellCog for market research, competitive analysis, investment research, academic research, due diligence, literature reviews, financial analysis, crypto research, news intelligence, and multi-source synthesis.

This skill is ready for commercial/non-commercial use.

## Publisher:

[cellcog](https://clawhub.ai/user/cellcog)

### License/Terms of Use:

MIT-0

## Use Case:

Developers, analysts, researchers, and external users use this skill to request CellCog-powered deep research, including market research, competitive analysis, investment analysis, academic literature review, due diligence, and citation-backed synthesis when requested.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Prompts, uploaded context, and generated research requests may be shared with the third-party CellCog service.

Mitigation: Use only if CellCog is trusted for the intended data; avoid secrets, regulated data, or sensitive business information unless approved.

Risk: The skill depends on the external cellcog package and CELLCOG_API_KEY setup, creating normal install and supply-chain exposure.

Mitigation: Prefer pinned package versions, reviewed release sources, and standard credential handling for CELLCOG_API_KEY.

Risk: Citations are not automatic, so research output may omit source links unless requested.

Mitigation: Ask for citations explicitly and review cited sources before relying on outputs for high-stakes decisions.

## Reference(s):

- [ClawHub Skill Page](https://clawhub.ai/cellcog/skills/deep-research-cellcog)
- [CellCog Homepage](https://cellcog.ai)
- [DeepResearch Bench Leaderboard](https://huggingface.co/spaces/muset-ai/DeepResearch-Bench-Leaderboard)

## Skill Output:

**Output Type(s):** [Text, Markdown, Code, Configuration, Guidance, Files]

**Output Format:** [Plain response, Markdown, PDF report, or interactive HTML report depending on the prompt]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Can include charts, tables, timelines, market maps, and source citations when explicitly requested]

## Skill Version(s):

1.0.20 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
