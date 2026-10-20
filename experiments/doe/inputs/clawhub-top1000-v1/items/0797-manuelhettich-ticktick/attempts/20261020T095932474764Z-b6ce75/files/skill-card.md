## Description:

Manage TickTick tasks and projects from the command line with OAuth2 auth, batch operations, and rate limit handling.

This skill is ready for commercial/non-commercial use.

## Publisher:

[manuelhettich](https://clawhub.ai/user/manuelhettich)

### License/Terms of Use:


## Use Case:

Agents and developers use this skill to authenticate with TickTick, list, create, update, complete, and abandon tasks, and manage TickTick projects from command-line workflows.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill stores TickTick OAuth client secrets and tokens in a local configuration file.

Mitigation: Protect ~/.clawdbot/credentials/ticktick-cli/config.json and avoid pasting real client secrets into shared terminals, transcripts, or automation logs.

Risk: Task mutation commands can complete or abandon the wrong task if an ambiguous name or incorrect ID is used.

Mitigation: Use --json list output to confirm project and task IDs, and verify task status before complete, abandon, or batch-abandon operations.

Risk: Bulk operations can hit TickTick API rate limits.

Mitigation: Prefer targeted project filters and stagger large batches when operating near documented TickTick rate limits.

## Reference(s):

- [TickTick Developer Center](https://developer.ticktick.com/manage)
- [TickTick Open API v1](https://developer.ticktick.com/api)
- [TickTick Batch Task API](https://api.ticktick.com/open/v1/batch/task)

## Skill Output:

**Output Type(s):** [Shell commands, Configuration instructions, Guidance]

**Output Format:** [Markdown guidance with bash commands and optional JSON command output]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Supports machine-readable command output through the --json flag.]

## Skill Version(s):

1.0.0 (source: ClawHub release evidence; package.json reports 0.1.0)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
