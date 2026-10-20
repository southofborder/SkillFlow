## Description:

Automate Windows GUI interactions (mouse, keyboard, windows) using PowerShell. Use when the user needs to simulate user input on the desktop, such as moving the cursor, clicking buttons, typing text in non-web apps, or managing window states.

This skill is ready for commercial/non-commercial use.

## Publisher:

[wwb-daniel](https://clawhub.ai/user/wwb-daniel)

### License/Terms of Use:


## Use Case:

Developers and operators use this skill to automate explicit, user-directed Windows desktop interactions such as moving the cursor, clicking controls, typing into non-web applications, and managing window focus.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill gives an agent broad raw mouse and keyboard control on a live Windows desktop, which can trigger unintended clicks, keystrokes, submissions, security dialogs, or destructive application actions.

Mitigation: Use it only for explicit user-directed GUI automation, verify the target window immediately before each action, avoid untrusted text in the typing helper, and require confirmation before clicks, special keys, form submissions, security dialogs, or destructive actions.

## Reference(s):


## Skill Output:

**Output Type(s):** [Text, Markdown, Code, Shell commands, Guidance]

**Output Format:** [Markdown with inline PowerShell commands and script usage guidance]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Produces guidance for using bundled PowerShell helpers; actions affect the active Windows desktop state.]

## Skill Version(s):

1.0.0 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
