## Description:

Search the web using Google Custom Search Engine (PSE). Use this when you need live information, documentation, or to research topics and the built-in web_search is unavailable.

This skill is ready for commercial/non-commercial use.

## Publisher:

[mxfeinberg](https://clawhub.ai/user/mxfeinberg)

### License/Terms of Use:


## Use Case:

Developers and OpenClaw agents use this skill to run live web searches through Google's Custom Search API when built-in web search is unavailable.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Failed API calls may expose the Google API key or search details through exception text in logs or agent output.

Mitigation: Use a restricted Google API key, avoid sensitive searches, and sanitize error handling before broad deployment.

## Reference(s):

- [Google Programmable Search Engine setup](https://cse.google.com/cse/all)
- [Google Custom Search API endpoint](https://www.googleapis.com/customsearch/v1)
- [ClawHub skill page](https://clawhub.ai/mxfeinberg/skills/google-search)

## Skill Output:

**Output Type(s):** [JSON, Shell commands, Configuration guidance]

**Output Format:** [JSON search results with text status and error messages]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires GOOGLE_API_KEY and GOOGLE_CSE_ID environment variables; returns five results by default unless a result count is supplied.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
