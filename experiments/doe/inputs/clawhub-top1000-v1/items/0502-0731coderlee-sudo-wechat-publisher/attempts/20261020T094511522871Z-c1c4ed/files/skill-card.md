## Description:

Publishes Markdown articles to a WeChat Official Account draft box through wenyan-cli, with support for themes, code highlighting, and image uploads.

This skill is ready for commercial/non-commercial use.

## Publisher:

[0731coderlee-sudo](https://clawhub.ai/user/0731coderlee-sudo)

### License/Terms of Use:

MIT

## Use Case:

Content creators and developers use this skill to prepare Markdown articles with required frontmatter, choose wenyan themes, and publish drafts to a WeChat Official Account for review before release.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill handles WeChat AppID and AppSecret values and artifact scripts read them from TOOLS.md into shell environment variables.

Mitigation: Use a secret manager or tightly scoped environment injection, do not store AppSecret in shared docs, repositories, backups, or shell startup files, and rotate any secret that was stored there.

Risk: The publishing script can modify the user's system by installing @wenyan-md/cli globally when the command is missing.

Mitigation: Install a reviewed and pinned wenyan-cli version yourself before using the skill, and review shell scripts before execution.

Risk: Article text and images are sent to WeChat services during publishing.

Mitigation: Review all Markdown content, frontmatter, cover images, and embedded images before publishing drafts.

## Reference(s):

- [Wechat Publisher on ClawHub](https://clawhub.ai/0731coderlee-sudo/skills/wechat-publisher)
- [themes.md](references/themes.md)
- [troubleshooting.md](references/troubleshooting.md)
- [wenyan-cli](https://github.com/caol64/wenyan-cli)
- [wenyan upload configuration](https://yuzhi.tech/docs/wenyan/upload)
- [WeChat Official Account API documentation](https://developers.weixin.qq.com/doc/offiaccount/)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance with inline shell commands and configuration examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May publish drafts and upload article images to WeChat services when the generated commands are executed.]

## Skill Version(s):

0.1.0 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
