## Description:

命理大师 is an all-in-one Chinese astrology and divination skill for BaZi, Zi Wei Dou Shu, Qi Men Dun Jia, Yijing divination, tarot, astrology, numerology, feng shui, naming, dressing guidance, relationship timing, local profiles, optional daily fortune pushes, and browser-based Liuyao readings.

This skill is ready for commercial/non-commercial use.

## Publisher:

[wscats](https://clawhub.ai/user/wscats)

### License/Terms of Use:

MIT-0

## Use Case:

External users and agents use this skill to produce cultural, reflective fortune and divination readings, local chart calculations, daily fortune summaries, relationship or timing guidance, and optional profile-based reports. It is positioned as reference material only and should not replace medical, legal, financial, psychological, naming, marriage, or other professional advice.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The security verdict is suspicious because input-handling bugs could expose or modify local JSON files or a browser-entered API key.

Mitigation: Review before installing on shared or multi-user machines, use non-sensitive test data where possible, and wait for fixes to userId path validation, owner-only profile permissions, and unsafe innerHTML rendering before treating the skill as low risk.

Risk: The skill can store birth, family, relationship, interaction, and push-log data in local plaintext files.

Mitigation: Only store profile data when needed, avoid entering sensitive real-world details unless local plaintext storage is acceptable, and use the documented profile commands to review, edit, or delete stored data.

Risk: The optional browser Liuyao feature can send a question and hexagram to a user-configured LLM endpoint with a browser-entered API key.

Mitigation: Keep the browser LLM feature disabled unless needed, use HTTPS endpoints, and use a separate limited API key rather than a primary or shared key.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/wscats/skills/university-applications)
- [README](README.md)
- [Safety and ethics](references/safety-and-ethics.md)
- [Intake and routing](references/intake-and-routing.md)
- [Output templates](references/output-templates.md)
- [BaZi framework](references/bazi-framework.md)
- [Zi Wei framework](references/ziwei-framework.md)
- [Qi Men framework](references/qimen-framework.md)
- [Yijing divination framework](references/yijing-divination-framework.md)
- [Tarot framework](references/tarot-framework.md)
- [Astrology framework](references/astrology-framework.md)
- [Numerology framework](references/numerology-framework.md)
- [Feng shui and timing framework](references/fengshui-and-timing-framework.md)
- [Relationship and timing](references/relationship-and-timing.md)
- [Naming framework](references/naming-framework.md)
- [Dressing framework](references/dressing-framework.md)
- [Palmistry framework](references/palmistry-framework.md)
- [Physiognomy framework](references/physiognomy-framework.md)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance]

**Output Format:** [Markdown and text responses with optional shell commands, local JSON profile data, and HTML report or browser interface outputs]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Outputs are cultural and symbolic guidance; local scripts may read or write local profile, preference, and push-log JSON files when users opt in.]

## Skill Version(s):

1.2.10 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
