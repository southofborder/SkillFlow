## Description:

Monitor blogs and RSS/Atom feeds for updates using the blogwatcher CLI.

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Developers and external users use this skill to install and operate the blogwatcher CLI for tracking blogs and RSS/Atom feeds, scanning for new articles, and managing read state.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Installing the CLI from a mutable Go module version can fetch code that has not been reviewed for this release.

Mitigation: Pin blogwatcher to a specific reviewed version before installation.

Risk: The installed CLI may inherit unnecessary secrets or sensitive filesystem access from the agent environment.

Mitigation: Install and run the CLI in an environment that exposes only the required files, feed URLs, and environment variables.

## Reference(s):

- [Blogwatcher ClawHub page](https://clawhub.ai/steipete/skills/blogwatcher)
- [Blogwatcher homepage](https://github.com/Hyaxia/blogwatcher)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Guidance]

**Output Format:** [Markdown with inline shell commands and CLI examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires the blogwatcher CLI to be installed and available on PATH.]

## Skill Version(s):

1.0.0 (source: ClawHub release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
