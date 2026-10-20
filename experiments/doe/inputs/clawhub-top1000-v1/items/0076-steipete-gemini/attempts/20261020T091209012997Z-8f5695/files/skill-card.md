## Description:

Gemini CLI for one-shot Q&A, summaries, and generation.

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Developers and agents use this skill to invoke Gemini CLI in one-shot mode for questions, summaries, generation, JSON output, and extension management.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Prompt content may be processed by Google's Gemini service.

Mitigation: Avoid sending secrets or private data unless the user's Gemini account and data-handling settings are appropriate.

Risk: Homebrew installation of the Gemini CLI changes the local environment.

Mitigation: Review the Homebrew install path and package before installing gemini-cli.

Risk: The Gemini CLI --yolo option can reduce execution safety.

Mitigation: Follow the artifact guidance to avoid --yolo.

## Reference(s):

- [Gemini Developer Site](https://ai.google.dev/)
- [ClawHub Gemini Skill](https://clawhub.ai/steipete/skills/gemini)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance]

**Output Format:** [Markdown or plain text with inline Gemini CLI commands and optional JSON output examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires the gemini binary; Homebrew install metadata is available for gemini-cli.]

## Skill Version(s):

1.0.0 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
