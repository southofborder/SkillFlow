## Description:

AI audio generation and text-to-speech powered by CellCog for voiceovers, narration, voice cloning, avatar voices, sound effects, music, podcasts, and dialogue.

This skill is ready for commercial/non-commercial use.

## Publisher:

[cellcog](https://clawhub.ai/user/cellcog)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and content creators use this skill to ask an agent to generate speech, voiceovers, cloned/avatar voices, sound effects, and music through CellCog-backed audio providers.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Voice cloning or avatar voice generation could be used without proper consent.

Mitigation: Use cloned/avatar voices only with explicit permission from the voice owner and without impersonation or deception.

Risk: Mutable dependency installation can weaken supply-chain control.

Mitigation: Install CellCog in an isolated environment and prefer pinned versions or verified sources where possible.

Risk: The skill requires an API key and may access files needed for audio workflows.

Mitigation: Expose only CELLCOG_API_KEY and the files required for the specific task.

## Reference(s):

- [ClawHub Skill Page](https://clawhub.ai/cellcog/skills/audio-generation-cellcog)
- [CellCog](https://cellcog.ai)
- [Publisher Profile](https://clawhub.ai/user/cellcog)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance]

**Output Format:** [Markdown instructions with Python examples and shell setup commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Generated audio is produced through CellCog-backed providers; use of cloned/avatar voices requires explicit permission from the voice owner.]

## Skill Version(s):

1.0.17 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
