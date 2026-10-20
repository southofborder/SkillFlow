## Description:

Manage Things 3 via the `things` CLI on macOS (add/update projects+todos via URL scheme; read/search/list from the local Things database).

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

External users and developers use this skill to manage Things 3 tasks on macOS through the `things` CLI, including creating, updating, listing, and searching tasks, projects, areas, and tags.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Broad macOS Full Disk Access can expose more local data than the skill needs for Things database reads.

Mitigation: Prefer THINGSDB or --db to point at the specific Things database, and revoke Full Disk Access after use if it is granted.

Risk: Putting real auth tokens directly in commands can expose them through shell history, logs, or process inspection.

Mitigation: Use THINGS_AUTH_TOKEN or another controlled secret source, avoid pasting tokens into command lines, and rotate any token that may have been exposed.

Risk: Installing the CLI with @latest can pull unreviewed future changes.

Mitigation: Pin things3-cli to a reviewed version before installing or deploying the skill.

## Reference(s):

- [ClawHub skill page: Things Mac](https://clawhub.ai/steipete/skills/things-mac)
- [things3-cli GitHub repository](https://github.com/ossianhempel/things3-cli)
- [things3-cli Go install module](https://github.com/ossianhempel/things3-cli/tree/main/cmd/things)

## Skill Output:

**Output Type(s):** [Shell commands, Configuration instructions, Guidance]

**Output Format:** [Markdown with inline bash code blocks]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [macOS-only guidance for using the `things` CLI with Things 3.]

## Skill Version(s):

1.0.0 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
