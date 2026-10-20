## Description:

Helps agents inspect VMware infrastructure through read-only inventory, health checks, and VM, host, and datastore investigations.

This skill is ready for commercial/non-commercial use.

## Publisher:

[zw008](https://clawhub.ai/user/zw008)

### License/Terms of Use:

MIT-0

## Use Case:

Infrastructure operators and engineers use this skill to triage vCenter and ESXi health, inspect inventory, alarms, events, performance, and capacity, and investigate affected VMs, hosts, or datastores without modifying resources.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Monitoring access can expose sensitive VMware inventory and operational details.

Mitigation: Use a dedicated read-only VMware account and a secret manager rather than storing passwords in .env.

Risk: Optional webhooks and daemon notifications can send hostnames, IPs, usernames, alarms, and event text to external destinations.

Mitigation: Enable notifications only after reviewing the destination and approving disclosure of those operational details.

## Reference(s):

- [ClawHub skill release](https://clawhub.ai/zw008/skills/vmware-monitor)
- [Project homepage listed in skill metadata](https://github.com/vmware-skills/VMware-Monitor)
- [Setup guide](artifact/references/setup-guide.md)
- [CLI reference](artifact/references/cli-reference.md)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Configuration guidance]

**Output Format:** [Concise health summaries, investigation findings, and optional command examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Optional local HTML snapshots and user-enabled monitoring notifications.]

## Skill Version(s):

2.4.2 (source: ClawHub release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
