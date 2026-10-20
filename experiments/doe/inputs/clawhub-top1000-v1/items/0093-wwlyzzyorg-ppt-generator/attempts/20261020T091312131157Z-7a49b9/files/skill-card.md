## Description:

将用户讲稿一键生成乔布斯风极简科技感竖屏HTML演示稿。当用户需要生成PPT、演示文稿、Slides、幻灯片，或要求科技风/极简风/乔布斯风格的演示时触发此技能。输出为单个可直接运行的HTML文件。

This skill is ready for commercial/non-commercial use.

## Publisher:

[wwlyzzyorg](https://clawhub.ai/user/wwlyzzyorg)

### License/Terms of Use:


## Use Case:

External users and presentation creators use this skill to turn Chinese speaker notes into a concise Jobs-style vertical technology presentation. The agent produces a refined Markdown script, slide structure outline, and a runnable single-file HTML slide deck.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Generated presentations load TailwindCSS and fonts from third-party CDNs, which may expose network metadata or fail when offline.

Mitigation: Review generated decks before sharing, and avoid opening highly sensitive presentations while online unless CDN fetching is acceptable.

## Reference(s):

- [Design Specification](references/design-spec.md)
- [Slide Types](references/slide-types.md)
- [ClawHub Skill Page](https://clawhub.ai/wwlyzzyorg/skills/ppt-generator)

## Skill Output:

**Output Type(s):** [Text, Markdown, Code, Files, Guidance]

**Output Format:** [Markdown with an HTML code block for a single runnable presentation file]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Generated HTML uses a 9:16 vertical layout with keyboard navigation, progress indicators, animation, and external CDN resources for TailwindCSS and fonts.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
