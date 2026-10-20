## Description:

最稳定的抖音视频下载工具，用户提供抖音链接或modal_id即可自动解析并下载。

This skill is ready for commercial/non-commercial use.

## Publisher:

[valderwu3](https://clawhub.ai/user/valderwu3)

### License/Terms of Use:


## Use Case:

External users and developers use this skill to parse a Douyin link or modal_id, retrieve a TikHub-backed video URL, and optionally download the video file.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill sends Douyin modal_id values and the user's TikHub bearer token to api.tikhub.io.

Mitigation: Use it only for explicit Douyin download requests, store the TikHub token carefully, and restrict access to ~/.openclaw/config.json.

Risk: When download mode is used, video files may be written to the current working directory.

Mitigation: Run the skill from an intended output directory and review downloaded files before sharing or executing follow-up actions.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/valderwu3/skills/douyin-downloader)
- [TikHub token registration](https://user.tikhub.io/register?referral_code=JtYTGCqJ)
- [TikHub Douyin video API endpoint](https://api.tikhub.io/api/v1/douyin/web/fetch_one_video)

## Skill Output:

**Output Type(s):** [text, shell commands, configuration, code, files]

**Output Format:** [Markdown guidance with inline shell commands and optional downloaded MP4 files]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Outputs may include a parsed modal_id, a Douyin video URL, and an MP4 file written to the current directory when download mode is used.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
