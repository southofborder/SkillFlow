## Description:

Terminal Spotify playback/search via spogo (preferred) or spotify_player.

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

External users use this skill to have an agent provide terminal Spotify playback, search, device-selection, and configuration guidance through spogo or spotify_player.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Chrome Spotify cookie import can expose account credentials to a third-party CLI if the installed spogo binary is malicious or compromised.

Mitigation: Only run cookie import after verifying the installed spogo source and binary; prefer OAuth or device-login flows when available.

Risk: The skill relies on external CLIs installed through Homebrew, including a third-party tap for spogo.

Mitigation: Review the Homebrew formulas and pin or verify versions before use in managed environments.

## Reference(s):

- [Spotify](https://www.spotify.com)
- [ClawHub Skill Page](https://clawhub.ai/steipete/skills/spotify-player)
- [Publisher Profile](https://clawhub.ai/user/steipete)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Configuration, Guidance]

**Output Format:** [Markdown with inline shell commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May reference user-specific Spotify devices, browser-cookie import, and local spotify_player configuration paths.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
