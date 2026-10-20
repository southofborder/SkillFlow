## Description:

高德地图综合服务，支持POI搜索、路径规划、旅游规划、周边搜索和热力图数据可视化

This skill is ready for commercial/non-commercial use.

## Publisher:

[lbs-amap](https://clawhub.ai/user/lbs-amap)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and external users use this skill to search Gaode/Amap POIs, find nearby places, plan routes or travel itineraries, and generate map or heatmap links from geospatial inputs.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Location searches, route coordinates, and supplied dataset URLs may be sent to Amap services.

Mitigation: Install only when this data sharing is acceptable, and avoid using private locations, private hosts, or token-bearing dataset URLs.

Risk: The skill can persist an Amap Web Service key in config.json.

Mitigation: Prefer AMAP_WEBSERVICE_KEY as an environment variable and avoid sharing local configuration files.

Risk: The Python helper communicates through a local Electron Unix socket.

Mitigation: Use it only with a trusted local desktop app and avoid running it on shared machines.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/lbs-amap/skills/amap-lbs-skill)
- [Gaode Web Service API overview](https://lbs.amap.com/api/webservice/summary)
- [Create a Gaode application and key](https://lbs.amap.com/api/webservice/create-project-and-key)
- [Gaode POI Search API documentation](https://lbs.amap.com/api/webservice/guide/api-advanced/newpoisearch)
- [Gaode Open Platform](https://lbs.amap.com/)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Configuration, API calls]

**Output Format:** [Markdown responses with map links, command examples, and JSON API results]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires AMAP_WEBSERVICE_KEY for API-backed POI search, routing, and travel planning.]

## Skill Version(s):

2.0.1 (source: frontmatter and server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
