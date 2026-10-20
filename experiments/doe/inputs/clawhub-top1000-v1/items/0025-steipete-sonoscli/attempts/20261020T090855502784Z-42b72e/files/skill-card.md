## Description:

Control Sonos speakers (discover/status/play/volume/group).

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

External users and developers use this skill to operate Sonos speakers on a local network, including discovery, playback control, volume changes, grouping, favorites, queue management, and optional Spotify search.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The required Sonos CLI is installed from a third-party Go module using @latest, so the installed upstream code may change over time.

Mitigation: Install only when the upstream project is trusted, review the module before deployment, and pin or mirror a vetted version for controlled environments.

Risk: Optional Spotify search may require Spotify credentials in the environment.

Mitigation: Provide only the required Spotify credentials, avoid exposing unrelated secrets, and use least-privilege credential handling where available.

## Reference(s):

- [Sonos CLI homepage](https://sonoscli.sh)
- [sonoscli Go module](https://pkg.go.dev/github.com/steipete/sonoscli/cmd/sonos)

## Skill Output:

**Output Type(s):** [text, shell commands, configuration, guidance]

**Output Format:** [Markdown with inline shell commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May include Sonos CLI commands, local-network troubleshooting guidance, and optional Spotify credential setup.]

## Skill Version(s):

1.0.0 (source: ClawHub release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
