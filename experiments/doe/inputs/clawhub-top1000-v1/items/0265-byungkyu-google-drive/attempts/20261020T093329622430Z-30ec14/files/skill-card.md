## Description:

Helps agents find, read, share, organize, upload, and download files and folders in a connected Google Drive account.

This skill is ready for commercial/non-commercial use.

## Publisher:

[byungkyu](https://clawhub.ai/user/byungkyu)

### License/Terms of Use:

MIT-0

## Use Case:

People and teams with a connected Google Drive account use this skill to find, read, download, upload, organize, and share their files and folders. It handles whole files rather than editing text within Docs, Sheets, or Slides.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Connecting the wrong account or granting broader Google Drive access than intended.

Mitigation: Obtain explicit approval for the connection, confirm the account, and select only the required OAuth scopes.

Risk: Sharing, replacing, moving, or deleting the wrong file or folder.

Mitigation: Prefer read-only operations and confirm the exact file IDs and proposed changes before each write.

Risk: Hosted functions, triggers, and destinations can perform continuing or high-impact actions.

Mitigation: Seek separate approval for each automation and remove functions, triggers, and destinations when no longer needed.

Risk: Using an API key instead of OAuth may expose a long-lived credential.

Mitigation: Prefer OAuth login; if an API key is necessary, keep it out of commands, logs, and stored files.

## Reference(s):

- [Google Drive skill release](https://clawhub.ai/byungkyu/skills/google-drive)
- [Maton homepage](https://maton.ai)
- [Google Drive API reference](https://developers.google.com/drive/api/reference/rest/v3)
- [Maton documentation](https://docs.maton.ai)
- [Time trigger reference](references/time/triggers.md)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Configuration guidance]

**Output Format:** [Markdown with file information, API examples, and shell commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [File content and metadata may contain personal information; access is limited to the connected account's permissions.]

## Skill Version(s):

1.2.11 (source: ClawHub release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
