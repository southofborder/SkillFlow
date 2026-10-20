## Description:

Integrates Tencent Cloud COS object storage, Cloud Infinite processing, MetaInsight retrieval, knowledge base workflows, and COS console guidance.

This skill is ready for commercial/non-commercial use.

## Publisher:

[shawnminh](https://clawhub.ai/user/shawnminh)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and operators use this skill to manage Tencent Cloud COS buckets and objects, run CI media and document processing, query MetaInsight datasets, create knowledge bases, and generate signed result previews.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill handles Tencent Cloud credentials that may authorize storage and CI processing operations.

Mitigation: Use short-lived STS credentials or a least-privilege Tencent sub-account, and avoid root account keys.

Risk: Persisting long-lived credentials locally can increase exposure if the workspace is shared or compromised.

Mitigation: Prefer ephemeral environment variables and avoid persisting credentials in .env or .env.enc unless local storage has been reviewed.

Risk: Authenticated requests can be sent to custom COS Domain, ServiceDomain, or Protocol values.

Mitigation: Only configure custom endpoints after verifying that they are trusted Tencent Cloud endpoints for the intended account and bucket.

Risk: Delete and service-disable operations can affect cloud data or CI service availability.

Mitigation: Keep KIKI=1 enabled when deletion or local credential management is not required, and review high-impact operations before execution.

## Reference(s):

- [COS Node.js SDK Operation Reference](references/api_reference.md)
- [Dataset Search](references/dataset-search.md)
- [Dataset Simple Query](references/dataset-simple-query.md)
- [Dataset Catalog](references/dataset-catalog.md)
- [Bucket Content Aggregation](references/bucket-content-aggregation.md)
- [Bucket Content Summary](references/bucket-content-summary.md)
- [CI Service Status](references/ci-service-status.md)
- [Search Results Preview](references/search-results-preview.md)
- [COS Console Feature Guides](references/console-feature-guides.md)
- [Tencent Cloud COS Pricing](https://cloud.tencent.com/document/product/436/16871)
- [Tencent Cloud CI Pricing](https://cloud.tencent.com/document/product/460/6970)
- [Tencent Cloud COS Node.js SDK](https://cloud.tencent.com/document/product/436/8629)
- [Tencent Cloud Cloud Infinite Documentation](https://cloud.tencent.com/document/product/460)
- [cos-nodejs-sdk-v5](https://github.com/tencentyun/cos-nodejs-sdk-v5)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance, JSON, HTML files]

**Output Format:** [Markdown guidance with shell commands, JSON command output, and optional HTML preview files]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires Tencent Cloud credentials plus Region and Bucket configuration; DatasetName and custom endpoint settings are optional.]

## Skill Version(s):

1.1.9 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
