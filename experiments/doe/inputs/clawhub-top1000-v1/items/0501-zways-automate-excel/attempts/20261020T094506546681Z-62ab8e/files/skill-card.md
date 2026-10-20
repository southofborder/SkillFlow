## Description:

Automates reading, writing, merging, transforming, and validating Excel (.xlsx/.xls) files for spreadsheet, Excel data, CSV-to-Excel conversion, batch processing, and report generation workflows.

This skill is ready for commercial/non-commercial use.

## Publisher:

[zways](https://clawhub.ai/user/zways)

### License/Terms of Use:


## Use Case:

Developers, analysts, and operations teams use this skill to automate Excel and CSV batch processing, including merging sheets, converting formats, filtering, deduplicating, aggregating, validating, formatting, and generating reports.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill can overwrite workbooks when commands are run without a distinct output path.

Mitigation: Use explicit output paths, keep backups before formatting or renaming workbooks, and review command arguments before execution.

Risk: Generated Excel files can carry unsafe formula-like values from untrusted CSV, Excel, or template data.

Mitigation: Review untrusted inputs before conversion or template fill, escape formula-like values where needed, and avoid opening generated files from untrusted sources.

Risk: Dependency versions are specified as minimums, which may vary across environments.

Mitigation: Pin and review dependencies before using the skill in sensitive or controlled environments.

## Reference(s):

- [Automate Excel ClawHub listing](https://clawhub.ai/zways/skills/automate-excel)
- [API and parameter reference](artifact/reference.md)
- [Usage examples](artifact/examples.md)

## Skill Output:

**Output Type(s):** [Text, Markdown, Code, Shell commands, Files, Configuration]

**Output Format:** [Markdown guidance with Python and shell command snippets; scripts produce Excel, CSV, and validation output files.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [The bundled scripts operate on local spreadsheet files and may write or overwrite output workbooks depending on the selected command and output path.]

## Skill Version(s):

0.1.3 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
