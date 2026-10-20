## Description:

Use the ClawdHub CLI to search, install, update, and publish agent skills from clawdhub.com.

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Developers and agents use this skill to manage ClawdHub skills through the ClawdHub CLI, including searching, installing, updating, listing, authenticating, and publishing skill folders.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Broad install and forced update commands can change installed agent skills unexpectedly.

Mitigation: Review commands before running them, prefer pinned CLI and skill versions, inspect changes before using forced updates, and keep a rollback path.

Risk: Publish commands can upload local files from a skill directory.

Mitigation: Publish only directories that have been checked for secrets, private files, and unintended content.

Risk: Registry overrides can direct operations to an untrusted service.

Mitigation: Confirm the registry is trusted before using CLAWDHUB_REGISTRY or the --registry option.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/steipete/skills/clawdhub)
- [ClawdHub registry](https://clawdhub.com)

## Skill Output:

**Output Type(s):** [shell commands, configuration, guidance]

**Output Format:** [Markdown with inline bash code blocks]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Includes CLI install, authentication, search, install, update, list, and publish command examples.]

## Skill Version(s):

1.0.0 (source: server-resolved release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
