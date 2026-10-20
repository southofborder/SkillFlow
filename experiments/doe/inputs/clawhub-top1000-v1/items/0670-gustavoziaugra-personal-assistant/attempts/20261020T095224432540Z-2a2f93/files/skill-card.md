## Description:

Personal daily briefing and productivity assistant. Generates morning briefings with priorities, habits, and self-care reminders. Use when starting your day, planning tasks, or maintaining daily routines and personal development. A minimalist personal productivity skill focused on you.

This skill is ready for commercial/non-commercial use.

## Publisher:

[gustavoziaugra](https://clawhub.ai/user/gustavoziaugra)

### License/Terms of Use:

MIT

## Use Case:

External users use this skill to generate local daily briefings that organize morning priorities, habit tracking, self-care reminders, and evening reflection for personal productivity and well-being.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Running the briefing script can create or overwrite a local JSON briefing file.

Mitigation: Choose the output path deliberately and avoid using a filename that contains data you need to preserve.

Risk: Scheduled runs or delivery integrations can expose personal reflections, priorities, or routines outside the local machine.

Mitigation: Review automation and delivery settings before enabling them, and avoid external delivery unless the destination is intended.

## Reference(s):

- [README](artifact/README.md)
- [ClawHub Skill Page](https://clawhub.ai/gustavoziaugra/skills/personal-assistant)

## Skill Output:

**Output Type(s):** [Text, JSON, Files, Shell commands, Guidance]

**Output Format:** [Markdown or plain text briefing with optional JSON file output]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Can create or overwrite a local briefing JSON file when output is requested.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
