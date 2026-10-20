# ClawHub same-model comparison: frozen first delivery

The source pool, cohort, prospective scoring rules and assistant reference review package are available. **Formal target requests: 0. Actual human source-reference confirmations: 0. No comparative semantic advantage is established.** This is the prespecified first delivery, not the completed 264-outcome experiment.

## Delivered evidence

| Item | Observed state | Evidence |
|---|---|---|
| Official downloads roster | 1,000 distinct owner-qualified Skills, six saved pages; roster frozen before package acquisition | [Source manifest](../../inputs/clawhub-top1000-v1/source-manifest.json), [raw roster](../../inputs/clawhub-top1000-v1/roster/entries.json) |
| Package acquisition | All 1,000 attempted; 993 complete and verified; seven retained failures | [Missing report](../../inputs/clawhub-top1000-v1/missing-report.md), [offline verification](acquisition-offline-first-delivery.json) |
| Selection | 589 physical nominations reviewed; 487 source-eligible; fixed seed 20261020 selected 24 plus six reserves | [Frozen selection audit](../../inputs/clawhub-top1000-v1/selection/frozen-v1/selection-audit.json), [case manifest](selection.json) |
| Source diversity | 24 distinct source clusters in the formal cohort; all 30 selected/reserve clusters distinct | [Sealed selection](../../inputs/clawhub-top1000-v1/selection/selection-freeze-v1.json) |
| Shared material | 30 complete numbered source packets; 220 retained readable files; no independent user task or synthetic fixture | [Source packages](cases/index.json), [material seal](materials-freeze.json) |
| Reference preparation | 30 assistant drafts; 284 receiving points, 98 material unknowns, 279 mandatory checks; exact source quotations and file inventories verified | [Human review package](human-reference-package.html), [instructions](human-reference-package.md), [draft seal](reference-draft-freeze-v1.json) |
| Human confirmation | Two actual people must independently verify all 30 references; all 60 confirmations pending | [Registration template](human-roster.template.json) |
| Common rules | Grading v2, exposure matching, primary adequacy, secondary chain/error/coverage measures, fixed self-review pairs, costs and correction epochs frozen prospectively | [Rubric](rubric.md), [evaluation supplement](evaluation-rules-supplement-v1.md), [rule/code seal](evaluation-rules-freeze.json) |
| Schedule and human allocation | 216 main workflows + 48 fixed reviews; 264 primary human assignments; 72 balanced first-read timed assignments | [Schedule](schedule.json), [scoring assignments](review/scoring-assignments.json), [timed assignments](review/assignments.json) |
| Engineering acceptance | 162 tests passed; zero failures, errors or skips; zero target model calls in tests | [Validation](engineering-validation-first-delivery.json), [JUnit](engineering-pytest-first-delivery.xml) |
| Offline replay | Source/rule/byte checks passed; scoring, costs and report regenerated with no model calls; original calibration protocol failure retained | [Replay](replay.json), [input integrity](input-integrity-first-delivery.json) |

The official [ClawHub API](https://github.com/openclaw/clawhub/blob/main/docs/api.md) supplies downloads ordering and cursor-based public Skills access. The sealed roster was captured from 09:03:58 to 09:05:03 UTC on 2026-10-20; it is an observation over that live window, not an atomic snapshot. No security-label filter, plugin list, lower-ranked substitute or newer-version fallback was used for accepted sources. The largest selected/reserve numbered bundle is 204,529 bytes and 60,886 fixed reference tokens, below both admission limits. The reference encoding is tiktoken 0.12.0 o200k_base, not an assertion about the model tokenizer.

## Source limitations and disclosed acquisition deviation

Four no-pin entries (ranks 24, 53, 74 and 899) received unversioned download requests before a later rejection. This violated the intended pre-download pin rule. Their archives were never accepted into common source views or eligibility. The collector now stops before requesting an unpinned archive. Original attempts, HTTP receipts and the earlier misleading rejection wording remain preserved in the [deviation record](../../inputs/clawhub-top1000-v1/acquisition-protocol-deviations.json). Hash verification does not make this collection deviation disappear.

The other three unavailable entries (ranks 387, 448 and 782) retain Windows path/file integrity failures. All seven ranked identities remain in the 1,000-entry manifest. Earlier failed archives were preserved when exact-version metadata-overlay recovery succeeded for 87 other entries; recovery records distinguish original archive hashes, official file hashes and derived common-source hashes. No downloaded Skill was installed or executed. All accepted sources in this collection were hosted packages; GitHub-descriptor acquisition was covered by engineering fixtures, not an observed GitHub item in this pool.

## Source-only reference scope

The 24 formal-case assistant drafts propose nine conditional excess units across six cases. The six reserves propose another five units across two cases. These are exploratory assistant interpretations, not human-confirmed gold, observed incidents, validated prevalence or target performance. Empty findings record source coverage and uncertainty; they do not establish safety. If the final human reference has few adjudicable positives, detection comparisons must be reported as limited evidence rather than changing the cohort or fabricating variants.

The drafts separate declared purpose, required behavior and implementation choice. Existing use does not establish necessity, and author declarations do not establish actual user authorization. Necessary actions can carry excess payload. Conditions, data versions, recipients, local processing, earlier observation and opaque dependencies remain explicit. The source-only coverage correction for real-001 added the documented cron credential-storage boundary while retaining uncertainty about unattended scheduling preservation; its earlier draft remains [preserved](reference-drafts/history/pre-coverage-audit/real-001.json). No method output drove the correction.

## One authorized CLI feasibility probe

Exactly one fresh application-CLI feasibility request was authorized and executed. Its actual receipt verified gpt-6.1-sol / ultra / openai, a fresh context, no tools/delegation, and exact equality of the 62,084-byte task stdin with the visible task message. One ordinary CLI environment-context message was present. The request reported 28,360 input tokens (12,544 cached), 29,217 output tokens and 57,577 total tokens; reasoning-output counters are a subset of output and are not added again. Response duration was 626.067 seconds. The visible answer parsed as JSON; semantic correctness was not evaluated. See the [complete feasibility evidence](transport-inspection/feasibility-result.json) and [visible answer](transport-inspection/proposed-cli-probe/visible-answer.txt).

The earlier collaboration calibration failed because manual message embedding changed a source fragment. It remains a rejected delivery violation with unknown per-response usage. The successful CLI probe neither replaces that attempt nor establishes completion of the three native engineering calibrations. Zero-model replay therefore intentionally retains failed overall protocol status while its byte checks and derived-artifact regeneration pass.

## Observed preparation and engineering costs

The attributed preparation window beginning 2026-10-20T09:02:00Z covers 12 registered preparation sessions and 1,405 deduplicated reported response IDs. Its subtotal is **257,852,528 reported total tokens**, including **251,376,512 cached input tokens** and 1,044,198 output tokens. These are summed per-response counters, including repeated cached contexts, not unique source volume or a session-cumulative estimate. This is research preparation, source screening, drafting and engineering work, separate from the three formal methods. The full historical preparation cost remains unknown; unregistered/unreceipted work and the supervisor's later/final responses are not inferred. [Window summary](preparation-window-summary.json), [per-response preparation ledger](preparation-cost.json).

Two engineering target requests are retained: the failed collaboration request with unknown usage, and the authorized CLI probe with 57,577 known tokens. Their combined total remains unknown. No monetary amount is estimated without billing evidence. Formal-method tokens, accuracy, stability and human review efficiency have not been measured. The [cost ledger](cost-ledger.json) keeps target response IDs, missing counters, original-plus-review views, preparation work and actual-human work separate.

## Remaining gates and scientific conclusion

Two actual source verifiers must inspect and confirm each exact final source/reference pair. Register them and three different timed participants; assistant flags or fictional fixture attestations cannot satisfy this requirement. Source disputes remain explicit. After final references are personally confirmed, their separate reference freeze can be built.

The frozen formal protocol still requires fresh collaboration children. Adopting the tested CLI for all semantic stages requires an explicit new protocol version and request adapter rather than pretending CLI requests are spawn_agent calls. The concrete [formal-adoption proposal](transport-inspection/formal-adoption-proposal.md) is prepared and remains proposed_not_adopted. Three full from-source native engineering calibrations must then pass under an approved path. No further CLI request or formal target call was made after the one-off authorization.

Current evidence establishes a collected real-source cohort, a reviewable prospective experiment, engineering preservation/accounting checks and one feasible literal transport. It establishes **no measured SkillFlow advantage**. Better trace structure is a testable hypothesis, not an accuracy result. If direct audit or the single-prompt chain competes with or exceeds SkillFlow, the final report must say so; if one independent review removes an apparent single-answer advantage, report it explicitly along with original-plus-review cost. None of the methods receives a presumed advantage.

## Frozen case inventory

| Case | Role | Official rank | Skill | Source cluster | Bundle bytes | Reference tokens | Draft excess units |
|---|---|---:|---|---|---:|---:|---:|
| [real-001](cases/real-001/source-bundle.txt) | formal | 587 | infra403/6551-twitter-to-binance-square | infra403/6551-daily-news | 43,487 | 11,529 | 0 |
| [real-002](cases/real-002/source-bundle.txt) | formal | 46 | lamelas/himalaya | lamelas/himalaya | 14,890 | 4,320 | 1 |
| [real-003](cases/real-003/source-bundle.txt) | formal | 233 | eddygk/skill-vetting | eddygk/skill-vetting | 34,895 | 9,284 | 0 |
| [real-004](cases/real-004/source-bundle.txt) | formal | 317 | carlosfmtz/social-content | carlosfmtz/social-content | 24,981 | 6,848 | 0 |
| [real-005](cases/real-005/source-bundle.txt) | formal | 343 | asif2bd/openclaw-token-optimizer | asif2bd/openclaw-token-optimizer | 70,092 | 17,366 | 0 |
| [real-006](cases/real-006/source-bundle.txt) | formal | 770 | drjmz/moltbook-registry | drjmz/moltbook-registry | 9,721 | 2,809 | 0 |
| [real-007](cases/real-007/source-bundle.txt) | formal | 372 | manifoldor/tushare | manifoldor/tushare | 40,263 | 12,646 | 1 |
| [real-008](cases/real-008/source-bundle.txt) | formal | 663 | zachgodsell93/meta-ads | zachgodsell93/meta-ads | 18,587 | 5,762 | 1 |
| [real-009](cases/real-009/source-bundle.txt) | formal | 224 | lunarcmd/moltbook-interact | lunarcmd/moltbook-interact | 19,333 | 5,871 | 0 |
| [real-010](cases/real-010/source-bundle.txt) | formal | 502 | 0731coderlee-sudo/wechat-publisher | 0731coderlee-sudo/wechat-publisher | 33,334 | 10,861 | 2 |
| [real-011](cases/real-011/source-bundle.txt) | formal | 853 | gxcun17/skywork-ppt | gxcun17/skywork-ppt | 107,047 | 28,787 | 2 |
| [real-012](cases/real-012/source-bundle.txt) | formal | 386 | broedkrummen/brave-api-search | broedkrummen/brave-api-search | 54,379 | 14,694 | 0 |
| [real-013](cases/real-013/source-bundle.txt) | formal | 368 | blueberrywoodsym/x-ai | blueberrywoodsym/x-ai | 23,000 | 6,672 | 0 |
| [real-014](cases/real-014/source-bundle.txt) | formal | 515 | spliff7777/windows-control | spliff7777/windows-control | 69,925 | 18,114 | 0 |
| [real-015](cases/real-015/source-bundle.txt) | formal | 661 | bluecraft-ai/cold-email | bluecraft-ai/cold-email | 30,305 | 8,140 | 0 |
| [real-016](cases/real-016/source-bundle.txt) | formal | 611 | byungkyu/google-ads-api | byungkyu/acuity-scheduling | 204,529 | 60,886 | 0 |
| [real-017](cases/real-017/source-bundle.txt) | formal | 109 | iswalle/getnote | iswalle/getnote | 68,449 | 19,269 | 2 |
| [real-018](cases/real-018/source-bundle.txt) | formal | 441 | victorcavero14/upload-post | victorcavero14/upload-post | 27,867 | 8,402 | 0 |
| [real-019](cases/real-019/source-bundle.txt) | formal | 964 | abgohel/canva | abgohel/canva | 17,797 | 5,525 | 0 |
| [real-020](cases/real-020/source-bundle.txt) | formal | 312 | kys42/stock-info-explorer | kys42/stock-info-explorer | 16,439 | 4,948 | 0 |
| [real-021](cases/real-021/source-bundle.txt) | formal | 152 | shreefentsar/remotion-video-toolkit | am-will/remotion | 101,346 | 29,974 | 0 |
| [real-022](cases/real-022/source-bundle.txt) | formal | 73 | steipete/model-usage | jx-76/jx76-gog | 15,433 | 4,012 | 0 |
| [real-023](cases/real-023/source-bundle.txt) | formal | 985 | franky0617/crypto-gold-monitor | franky0617/crypto-gold-monitor | 16,125 | 5,037 | 0 |
| [real-024](cases/real-024/source-bundle.txt) | formal | 240 | liam8/crypto-market-data | liam8/crypto-market-data | 21,451 | 6,269 | 0 |
| [real-025](cases/real-025/source-bundle.txt) | reserve | 473 | fly0pants/ecomseer | fly0pants/admapix | 65,651 | 21,082 | 1 |
| [real-026](cases/real-026/source-bundle.txt) | reserve | 480 | jacobzwj/bilibili-hot-monitor | jacobzwj/bilibili-hot-monitor | 103,652 | 30,902 | 4 |
| [real-027](cases/real-027/source-bundle.txt) | reserve | 359 | arnarsson/ssh-essentials | arnarsson/curl-http | 10,305 | 3,206 | 0 |
| [real-028](cases/real-028/source-bundle.txt) | reserve | 356 | jdrhyne/todo-tracker | jdrhyne/context-recovery | 24,197 | 7,300 | 0 |
| [real-029](cases/real-029/source-bundle.txt) | reserve | 419 | hw10181913/claude-code | hw10181913/claude-code | 38,060 | 10,392 | 0 |
| [real-030](cases/real-030/source-bundle.txt) | reserve | 504 | 0xs4m1337/demo-video | 0xs4m1337/demo-video | 14,236 | 4,167 | 0 |
