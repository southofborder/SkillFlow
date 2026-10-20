## Description:

Search Google Flights for prices, times, and airlines. No API key required.

This skill is ready for commercial/non-commercial use.

## Publisher:

[awlevin](https://clawhub.ai/user/awlevin)

### License/Terms of Use:

MIT

## Use Case:

External users and developers use this skill to look up one-way or round-trip Google Flights results from an agent workflow or command line, including prices, airlines, departure and arrival times, durations, stops, passenger counts, and seat class.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The README one-line installer retrieves and executes a remote shell script.

Mitigation: Review the install path first and prefer a pinned package-manager install such as uv, pipx, or pip in controlled environments.

Risk: The --upgrade path can update local packages without version pinning.

Mitigation: Avoid self-upgrade commands in managed environments unless the target version and change approval are explicit.

Risk: Flight search inputs such as airports, dates, passenger counts, and seat class may be sent to Google or the underlying scraper service.

Mitigation: Do not submit sensitive itinerary details unless that data sharing is acceptable for the user or organization.

## Reference(s):

- [ClawHub Skill Page](https://clawhub.ai/awlevin/skills/flight-search)
- [PyPI package](https://pypi.org/project/flight-search/)
- [fast-flights underlying library](https://github.com/AWeirdDev/flights)

## Skill Output:

**Output Type(s):** [Text, JSON]

**Output Format:** [Plain text flight listings or structured JSON search results]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Results may include route, departure date, return date, price status, airline, departure and arrival times, duration, stops, price, and best-flight marker.]

## Skill Version(s):

0.1.7 (source: pyproject.toml, CHANGELOG, server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
