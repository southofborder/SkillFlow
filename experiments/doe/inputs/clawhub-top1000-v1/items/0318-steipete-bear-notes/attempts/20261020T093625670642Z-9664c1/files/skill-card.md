## Description:

Create, search, and manage Bear notes via grizzly CLI.

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Developers and Bear users on macOS use this skill to have an agent provide commands and configuration guidance for creating, reading, searching, appending to, and tagging Bear notes through the grizzly CLI.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Bear token handling can expose note access if ~/.config/grizzly/token is readable, shared, or broadly backed up.

Mitigation: Treat the Bear token as sensitive, restrict local file access, and avoid sharing or broad backups of the token file.

Risk: The install metadata uses an unpinned third-party grizzly CLI module, so future installs may retrieve changed code.

Mitigation: Review or pin the grizzly CLI version before deployment instead of relying on @latest.

## Reference(s):

- [Bear](https://bear.app)
- [Grizzly CLI Go module](https://pkg.go.dev/github.com/tylerwince/grizzly/cmd/grizzly)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Configuration, Guidance]

**Output Format:** [Markdown with shell command examples and configuration snippets]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires macOS, the Bear app, and the grizzly CLI; some operations require a Bear app token.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
