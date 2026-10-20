## Description:

Track water and sleep with JSON file storage.

This skill is ready for commercial/non-commercial use.

## Publisher:

[stellarhold170nt](https://clawhub.ai/user/stellarhold170nt)

### License/Terms of Use:


## Use Case:

External users and personal assistant agents use this skill to record water intake, sleep and wake events, and simple daily statistics in a local JSON file.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The water amount placeholder can lead to unintended local code execution if non-numeric input is inserted into the Node.js snippet.

Mitigation: Validate cup counts as numeric values before execution and pass them as separate arguments rather than interpolating raw user input.

Risk: The skill stores a local health log in the skill directory.

Mitigation: Install and use the skill only where local storage of water and sleep records is acceptable.

Risk: Update and delete snippets modify the latest water record without a confirmation step.

Mitigation: Require confirmation before running update or delete actions.

## Reference(s):


## Skill Output:

**Output Type(s):** [Shell commands, Code, Configuration]

**Output Format:** [Markdown with inline bash and JSON code blocks]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Produces local Node.js snippets that read and write a health-data.json file under the configured base directory.]

## Skill Version(s):

1.0.2 (source: frontmatter and server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
