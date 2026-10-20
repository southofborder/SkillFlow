## Description:

Essential Git commands and workflows for version control, branching, and collaboration.

This skill is ready for commercial/non-commercial use.

## Publisher:

[arnarsson](https://clawhub.ai/user/arnarsson)

### License/Terms of Use:


## Use Case:

Developers and engineers use this skill for concise Git command guidance across repository setup, everyday version-control workflows, branching, remotes, history inspection, undo operations, stashing, rebasing, tagging, submodules, and cleanup.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Commands in the undo, clean, delete, and force-push sections can discard local work or rewrite remote history.

Mitigation: Review git status, inspect affected branches or files, and confirm the intended destructive effect before allowing an agent to run those commands.

## Reference(s):

- [Git Homepage](https://git-scm.com/)
- [Official Git Documentation](https://git-scm.com/doc)
- [Pro Git Book](https://git-scm.com/book)
- [A Visual Git Reference](https://marklodato.github.io/visual-git-guide/)
- [ClawHub Skill Page](https://clawhub.ai/arnarsson/skills/git-essentials)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Configuration, Guidance]

**Output Format:** [Markdown with inline bash and ini code blocks]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires the git binary for command execution examples; the skill itself is a command reference.]

## Skill Version(s):

1.0.0 (source: release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
