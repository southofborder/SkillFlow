## Description:

Query Google Places API (New) via the goplaces CLI for text search, place details, resolve, and reviews.

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Developers and agents use this skill to look up places through the Google Places API (New), including search, details, resolution, and reviews. It supports human-readable responses and JSON output for scripts.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill installs an unpinned third-party Homebrew package.

Mitigation: Confirm trust in the steipete/tap Homebrew source and the goplaces project before installation, and avoid elevated privileges.

Risk: Google Places API credentials may be over-scoped or overused.

Mitigation: Use a Google Places API key scoped and quota-limited for this use case.

## Reference(s):

- [ClawHub Skill Page](https://clawhub.ai/steipete/skills/goplaces)
- [goplaces GitHub Repository](https://github.com/steipete/goplaces)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, JSON]

**Output Format:** [Markdown guidance with inline shell commands and optional JSON-producing CLI usage]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires the goplaces binary and GOOGLE_PLACES_API_KEY; output may depend on Google Places API availability and quota.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
