# ClawHub package availability and integrity record

The sealed roster contains **1000** owner-qualified Skills. Counts: `{"complete_verified": 993, "integrity_or_format_failure": 7}`.

The public list was captured over the saved roster interval, before package downloads. It is not an instantaneous atomic ranking. All 1,000 ranked identities remain in the source manifest; no lower-ranked substitute or newer version is selected for a missing item.

Archives and binaries are retained without installation or execution. Availability and integrity failures are not DOE judgments or model failures. Prior failed attempts remain preserved when a documented exact-version recovery succeeds.

| Rank | Canonical identity | Version | Current acquisition status | Evidence |
|---:|---|---|---|---|
| 24 | autogame-17/evolver | None | integrity_or_format_failure | [Result](items/0024-autogame-17-evolver/attempts/20261020T090853936224Z-f4e147/result.json) |
| 53 | emilioacc/atxp | None | integrity_or_format_failure | [Result](items/0053-emilioacc-atxp/attempts/20261020T091055847063Z-92857a/result.json) |
| 74 | autogame-17/capability-evolver | None | integrity_or_format_failure | [Result](items/0074-autogame-17-capability-evolver/attempts/20261020T091201105653Z-f14afc/result.json) |
| 387 | g0atfac3/g0atbot-tiktok-carousel | 1.0.0 | integrity_or_format_failure | [Result](items/0387-g0atfac3-g0atbot-tiktok-carousel/attempts/20261020T101959940465Z-meta-recovery-76cbca/result.json) |
| 448 | autogame-17/feishu-doc | 1.2.7 | integrity_or_format_failure | [Result](items/0448-autogame-17-feishu-doc/attempts/20261020T102007558582Z-meta-recovery-c3948b/result.json) |
| 782 | mileszhang001-boom/agent-tool-scout | 0.1.0 | integrity_or_format_failure | [Result](items/0782-mileszhang001-boom-agent-tool-scout/attempts/20261020T095800102654Z-3c90f1/result.json) |
| 899 | koatora20/guard-scanner | None | integrity_or_format_failure | [Result](items/0899-koatora20-guard-scanner/attempts/20261020T100612656622Z-f57403/result.json) |

## Disclosed acquisition deviation

Four hosted entries with no frozen version pin received an unversioned download request before a later check rejected the archive. They have no accepted source view and do not enter eligibility or selection. The collector now rejects missing pins before issuing download requests. Original attempts and the earlier misleading rejection wording remain preserved in the [deviation record](acquisition-protocol-deviations.json). No lower rank or newer source was accepted.
