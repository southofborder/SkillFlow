## Description:

Full Windows desktop control. Mouse, keyboard, screenshots - interact with any Windows application like a human.

This skill is ready for commercial/non-commercial use.

## Publisher:

[spliff7777](https://clawhub.ai/user/spliff7777)

### License/Terms of Use:

MIT

## Use Case:

Developers and agents use this skill to inspect, control, and verify Windows desktop applications through mouse, keyboard, window, dialog, screenshot, UI element, and webpage automation.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill can perform broad desktop actions including clicks, keystrokes, window control, and dialog handling.

Mitigation: Use it only in an intended controlled session and require explicit human confirmation before clicks, hotkeys, closing windows, saving, accepting, deleting, or dismissing dialogs.

Risk: Screen, window, UI element, and webpage reading can expose visible sensitive information.

Mitigation: Avoid sensitive applications and visible secrets while the skill is active.

Risk: Automation may target the wrong window, element, or dialog when multiple applications are open.

Mitigation: Prefer listing or reading windows and UI elements before acting, then verify the result after each state-changing action.

## Reference(s):

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)

## Skill Output:

**Output Type(s):** [Shell commands, Text, JSON, Images, Guidance]

**Output Format:** [Markdown guidance with Python command examples; script outputs include plain text, JSON, and base64 PNG screenshots]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Some commands directly manipulate the Windows desktop and may change application state.]

## Skill Version(s):

1.0.0 (source: package.json, server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
