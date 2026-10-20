## Description:

Career Planner China helps users explore China-focused education and career paths by collecting background details, estimating interests and work values, assessing AI impact, and producing personalized career planning reports.

This skill is ready for commercial/non-commercial use.

## Publisher:

[mnetfairy](https://clawhub.ai/user/mnetfairy)

### License/Terms of Use:

MIT-0

## Use Case:

External users, students, early-career workers, and career changers use this skill to discuss China-focused career options, compare education paths, understand AI-related job disruption, and receive practical next steps.

### Deployment Geography for Use:

China

## Known Risks and Mitigations:

Risk: The skill may collect sensitive personal career details such as education, interests, city, work goals, and career concerns.

Mitigation: Ask only for information needed for the current planning task, avoid unnecessary personal identifiers, and do not enable email sending, memory storage, tracking, or real-time search unless the user explicitly requests it.

Risk: Career, salary, AI-impact, and education-path recommendations can become outdated or may not fit a user's local circumstances.

Mitigation: Present recommendations as planning support rather than guarantees, and ask users to verify salary ranges, job demand, credentials, employers, and admissions requirements before acting.

Risk: Insurance-company recommendations and phone contacts could be mistaken for endorsed or authoritative advice.

Mitigation: Show only verified records with source URLs, keep contact details hidden until the user asks to see them, disclose that recommendations are informational, and advise independent verification before contacting a company.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/mnetfairy/skills/career-planner-china)
- [Skill definition and scope](artifact/SKILL.md)
- [Career assessment framework](artifact/references/assessment.md)
- [AI career impact reference](artifact/references/ai_career_impact.md)
- [Salary data reference](artifact/references/salary_data.md)
- [Salary database](artifact/references/salary_database.json)
- [Job demand trends](artifact/references/job_demand.md)
- [Industry trends](artifact/references/industry_trends.md)
- [Education paths](artifact/references/education_paths.md)
- [Insurance broker company data](artifact/references/insurance_broker_companies.json)
- [Optional integrations](artifact/references/integrations.md)

## Skill Output:

**Output Type(s):** [Guidance, Markdown, Text]

**Output Format:** [Conversational Markdown career planning report with structured recommendations and optional Markdown export]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Default behavior is offline and read-only; optional email sending, memory storage, follow-up tracking, and real-time search require explicit user request and host support.]

## Skill Version(s):

2.99.99 (source: server release metadata; artifact frontmatter reports 2.2.260)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
