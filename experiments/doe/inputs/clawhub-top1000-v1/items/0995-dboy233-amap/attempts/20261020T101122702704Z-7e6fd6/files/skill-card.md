## Description:

Amap helps agents use the Gaode Map Web Service API for place search, weather queries, route planning, geocoding, reverse geocoding, and administrative district lookup.

This skill is ready for commercial/non-commercial use.

## Publisher:

[dboy233](https://clawhub.ai/user/dboy233)

### License/Terms of Use:


## Use Case:

External users and developers use this skill to answer location-oriented requests through Amap, including weather, point-of-interest search, driving directions, address geocoding, coordinate reverse geocoding, and adcode lookup.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: User-provided locations may be inserted directly into curl command strings, creating command-injection risk.

Mitigation: Review commands before execution, use only trusted location inputs, URL-encode parameters, and pass curl arguments without shell interpolation.

Risk: Location, home, work, or travel addresses can be sensitive personal data.

Mitigation: Avoid submitting sensitive addresses unless necessary and minimize location detail in requests.

## Reference(s):

- [Amap Open Platform](https://lbs.amap.com/)
- [ClawHub skill page](https://clawhub.ai/dboy233/skills/amap)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, API Calls, Configuration instructions]

**Output Format:** [Markdown with inline bash code blocks and curl command examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires curl and an AMAP_KEY environment variable for Amap Web Service API calls.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
