## Description:

Helps agents use a connected Google account to search, manage, and organize contacts and contact groups through Maton.

This skill is ready for commercial/non-commercial use.

## Publisher:

[byungkyu](https://clawhub.ai/user/byungkyu)

### License/Terms of Use:

MIT-0

## Use Case:

People and teams with an authorized Google account use this skill to find, create, update, or delete contacts and manage contact groups. With separate approval, they can set up Maton automations that act on the connected account.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Contact changes or deletion can affect the wrong person or account.

Mitigation: Use the narrowest account and scopes, verify the contact and account, and obtain explicit approval before each write or deletion.

Risk: Approved automations can persist and forward event data to external destinations.

Mitigation: Require separate approval for automations and destinations, and disclose what data will be forwarded before enabling them.

## Reference(s):

- [Google Contacts skill on ClawHub](https://clawhub.ai/byungkyu/skills/google-contacts)
- [Maton homepage](https://maton.ai)
- [Google People API documentation](https://developers.google.com/people/api/rest)
- [Maton CLI manual](https://cli.maton.ai/manual)
- [Scheduled trigger reference](artifact/references/time/triggers.md)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Configuration guidance]

**Output Format:** [Markdown with contact summaries and optional command examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May include personal contact data; disclose only fields needed for the request.]

## Skill Version(s):

1.2.6 (source: server-resolved ClawHub release)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
