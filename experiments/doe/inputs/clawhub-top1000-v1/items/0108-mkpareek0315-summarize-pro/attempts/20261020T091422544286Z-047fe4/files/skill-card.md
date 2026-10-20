## Description:

Summarize Pro helps an agent turn long content into concise summaries, TL;DRs, bullet points, action items, meeting notes, email digests, comparisons, and multi-language or custom-length summaries.

This skill is ready for commercial/non-commercial use.

## Publisher:

[mkpareek0315](https://clawhub.ai/user/mkpareek0315)

### License/Terms of Use:


## Use Case:

External users and employees use this skill to summarize articles, documents, meetings, emails, threads, books, PDFs, reports, and conversations into concise reader-facing outputs. It also supports saved summaries, summary history, usage stats, and custom summary templates stored locally.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Local history, stats, saved summaries, and templates may retain sensitive source content or derived summaries under ~/.openclaw/summarize-pro/.

Mitigation: Avoid using the skill for highly sensitive documents unless local retention is acceptable, and periodically manage or delete the stored files.

Risk: Summaries, action items, and comparisons may omit nuance or misstate source details if used without review.

Mitigation: Review generated outputs against the original material before using them for decisions, commitments, or external communication.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/mkpareek0315/skills/summarize-pro)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown and plain text with optional JSON-backed local state]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Can create and update local settings, history, saved summaries, and templates under ~/.openclaw/summarize-pro/.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
