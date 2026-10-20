## Description:

Edit PDFs with natural-language instructions using the nano-pdf CLI.

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Developers and document authors use this skill to apply natural-language edits to a specific page in a PDF through the nano-pdf CLI.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill depends on the external nano-pdf Python package as resolved by uv, and the package is not pinned by the skill metadata.

Mitigation: Use a pinned or sandboxed install when processing sensitive documents or when reproducibility is required.

Risk: PDF edits may target the wrong page when nano-pdf page numbering differs by version or configuration.

Mitigation: Sanity-check the output PDF and retry with the alternate page-number base if the edit appears off by one.

Risk: Generated PDFs may contain incorrect or unintended changes.

Mitigation: Review generated PDFs before distributing them.

## Reference(s):

- [nano-pdf PyPI project](https://pypi.org/project/nano-pdf/)
- [ClawHub skill page](https://clawhub.ai/steipete/skills/nano-pdf)

## Skill Output:

**Output Type(s):** [Shell commands, Guidance]

**Output Format:** [Markdown with inline bash code blocks]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May include reminders to verify page numbering and review generated PDFs before distribution.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
