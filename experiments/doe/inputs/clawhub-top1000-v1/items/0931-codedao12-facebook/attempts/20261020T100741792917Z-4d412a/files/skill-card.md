## Description:

OpenClaw skill for Facebook Graph API workflows focused on Pages posting, comments, and Page management using direct HTTPS requests.

This skill is ready for commercial/non-commercial use.

## Publisher:

[codedao12](https://clawhub.ai/user/codedao12)

### License/Terms of Use:


## Use Case:

Developers and Page operators use this skill to plan direct Facebook Graph API workflows for publishing Page posts, moderating comments, handling permissions and tokens, and configuring Page webhooks.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Agents using the skill may operate live Facebook Pages, including public posting, editing, hiding, or deleting posts and comments.

Mitigation: Require explicit confirmation before publishing, editing, hiding, or deleting Page content or comments.

Risk: Facebook access tokens and app secrets could be exposed through unsafe request construction or logging.

Mitigation: Use Authorization headers instead of URL token parameters, never log tokens or app secrets, and store tokens securely.

Risk: Webhook handlers could accept spoofed events if signatures are not validated.

Mitigation: Validate X-Hub-Signature-256 with the app secret before processing webhook events.

## Reference(s):

- [Facebook Skill Page](https://clawhub.ai/codedao12/skills/facebook)
- [Graph API Overview](references/graph-api-overview.md)
- [Page Posting Guide](references/page-posting.md)
- [Comments and Moderation](references/comments-moderation.md)
- [Permissions and Tokens](references/permissions-and-tokens.md)
- [Webhooks (Pages)](references/webhooks.md)
- [HTTP Request Templates (Graph API)](references/http-request-templates.md)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance with HTTP request examples, checklists, and operational guardrails]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires Facebook App credentials, target Page IDs, token strategy, permissions, and review status supplied by the user.]

## Skill Version(s):

1.0.1 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
