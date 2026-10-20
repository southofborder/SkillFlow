## Description:

Remote-control tmux sessions for interactive CLIs by sending keystrokes and scraping pane output.

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Developers and engineers use this skill to drive interactive command-line programs through tmux sessions, monitor pane output, and coordinate parallel coding-agent work when an interactive TTY is required.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill can drive interactive tmux sessions and send keystrokes to panes.

Mitigation: Use an isolated socket, verify the target session and pane before sending input, and avoid running it against sensitive or production shells.

Risk: Unattended coding-agent examples using high-authority modes can modify repositories or run commands without interactive review.

Mitigation: Use isolated worktrees or sandboxes and avoid `--yolo` or `--full-auto` unless the workspace and command scope are intentionally trusted.

Risk: `wait-for-text.sh` can print captured pane history to stderr on timeout, which may expose tokens, private source, or other sensitive terminal output.

Mitigation: Avoid polling panes that may contain secrets, limit captured history where practical, and review logs before sharing them.

## Reference(s):

- [ClawHub Skill Page](https://clawhub.ai/steipete/skills/tmux)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance with inline shell commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires tmux on PATH and is intended for macOS, Linux, or WSL environments.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
