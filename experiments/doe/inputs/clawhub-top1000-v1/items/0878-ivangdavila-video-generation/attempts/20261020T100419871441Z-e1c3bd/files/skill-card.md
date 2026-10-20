## Description:

Create AI videos with Sora 2, Veo 3, Seedance, Runway, and modern APIs using reliable prompt and rendering workflows.

This skill is ready for commercial/non-commercial use.

## Publisher:

[ivangdavila](https://clawhub.ai/user/ivangdavila)

### License/Terms of Use:


## Use Case:

Developers, creators, and production teams use this skill to choose video-generation providers, write shot-focused prompts, and build reliable asynchronous rendering workflows across hosted and local model options.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Prompts, rendering parameters, and any selected reference media may be sent to third-party video providers.

Mitigation: Use only providers trusted for the content being generated and avoid submitting sensitive media unless provider terms and project requirements allow it.

Risk: Provider preferences, shot recipes, costs, and optional run history may be retained locally under ~/video-generation/.

Mitigation: Review memory.md and history.md periodically and remove entries that should not be retained.

Risk: Generated video URLs from provider APIs may expire before downstream export or review.

Mitigation: Download completed outputs promptly and preserve job metadata needed for audits or reruns.

## Reference(s):

- [ClawHub Skill Page](https://clawhub.ai/ivangdavila/skills/video-generation)
- [Skill Homepage](https://clawic.com/skills/video-generation)
- [AI Video Generation Skill Definition](artifact/SKILL.md)
- [Setup - AI Video Generation](artifact/setup.md)
- [API Patterns - AI Video Generation](artifact/api-patterns.md)
- [Model Snapshot](artifact/benchmarks.md)
- [OpenAI Sora 2](artifact/openai-sora.md)
- [Google Veo 3.x](artifact/google-veo.md)
- [Runway Gen-4 API](artifact/runway.md)
- [Open-Source Local Video Models](artifact/open-source-video.md)

## Skill Output:

**Output Type(s):** [guidance, markdown, code, shell commands, configuration]

**Output Format:** [Markdown guidance with inline code and shell command examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May include provider routing advice, prompt structures, API workflow patterns, and local preference-memory setup guidance.]

## Skill Version(s):

1.0.1 (source: frontmatter, server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
