## Description:

Resume Assistant helps job seekers polish, tailor, score, and export resumes and CVs with checklist reviews, ATS-aware guidance, and multi-format templates.

This skill is ready for commercial/non-commercial use.

## Publisher:

[wscats](https://clawhub.ai/user/wscats)

### License/Terms of Use:

MIT-0

## Use Case:

Job seekers, career coaches, and developers using compatible agents can use this skill to review resumes, improve wording, customize resumes for job descriptions, evaluate quality with a score, and export resumes in common submission formats.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Resume content can include sensitive personal information that may be processed by the user's selected agent or LLM provider.

Mitigation: Redact unnecessary personal details before use and prefer explicit /resume commands when working with sensitive documents.

Risk: Export workflows can create files or HTML where unsafe user fields or links would be harmful if handled without care.

Mitigation: Confirm before exporting files, escape user-provided fields in HTML, and block unsafe link schemes.

Risk: Resume improvement prompts could accidentally overstate a user's experience if edits are not grounded in the source resume.

Mitigation: Keep edits truthful, do not invent achievements or skills, and ask for missing background when needed.

## Reference(s):

- [Resume Assistant on ClawHub](https://clawhub.ai/wscats/skills/resume-assistant)
- [Artifact README](artifact/README.md)
- [Skill specification](artifact/SKILL.md)
- [Usage examples](artifact/examples/usage.md)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance]

**Output Format:** [Markdown responses, resume documents, HTML or LaTeX exports, Pandoc-ready Markdown, conversion commands, and structured scoring reports.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Supports English and Chinese resumes, slash commands, natural-language routing, four template styles, and export targets for Word, Markdown, HTML, LaTeX, and PDF.]

## Skill Version(s):

1.0.6 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
