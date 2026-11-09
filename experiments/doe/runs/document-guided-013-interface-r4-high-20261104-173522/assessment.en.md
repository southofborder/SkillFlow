All 31 generated IR propagated, including four append-before-return terminal classes; DOE still has no actionable conclusion.

The unused-write-output blocker is removed in actual new generation. Request/response versions, credential recipients and terminal values remain inspectable, with 11 satisfied static restrictions. All 15 sensitive comparisons remain explicitly unresolved; the remaining presence warning does not establish a real credential-gate violation.

This is the one authorized fresh interface-r4 run, with newly generated Task, flow, CFG and semantic fragments. No historical answers were imported. All observations below use the closed saved result and the controller-owned sole replay; this report did not run another analysis, replay, model, or Skill.

| Completion evidence | Actual result |
| --- | --- |
| Generated IR | 31/31 processed; 0 cutoff, 0 blocked, 0 not reached |
| Source-boundary audit | Three distinct request/receive pairs and four terminal append/return classes computed across eight syntactic CFG paths;24/24 declared sink positions appear in DOE. Presence/failure/status interfaces remain limited. |
| DOE | partial; 24 sink positions; 15 sensitive comparisons; {'no_excess_established': 15} |
| Review | graph=audit_passed; annotation=incomplete |
| Replay | matched; 23.772 s; 0 new native starts |

Generated-IR coverage and source-site representation are distinct denominators. A processed instruction may retain opaque behavior, candidate ambiguity or a source relationship gap. A `no_excess_established` result with unresolved limitations is not a safety verdict.

Source-supported findings and remaining limits:

- All 31 selected IR are processed without cutoff or propagation diagnostic. Four appends have no public CFG outputs, no processing output bindings and no recorded operation outputs. Each executes explicit append before its own terminal return.
- The first fast and retry requests use the same original source_id and FAST_KEY versions but distinct program-generated request IDs and completion Data IDs. Archive receives only original source_id, with a third independent completion. No key or preferred-tool error is added to archive arguments.
- First success ir_017 returns its own body; retry success ir_022 returns its own body; archive success ir_027 returns its own body; archive failure ir_031 returns that archive outcome interpreted as error on its predecessor. Success/error representation remains abstract because the tool failure envelope is unspecified.
- Each branch appends its own computed status to local:status.txt, deriving after-state from prior file plus the status. The four alternative appends are not four sequential writes in one execution. Exact status text, delimiter, initial file bytes and disk success are unknown.
- Absent key routes to archive; first success terminates; transient first failure permits one retry; non-transient failure or failed retry routes to archive; archive success and failure both terminate. Eight syntactic paths aggregate into four terminal classes, without proving concrete feasibility.
- One FAST_KEY declaration resolves. The 15 DOE comparisons include permitted fast-tool deliveries, possible model observations and possible influence on status writes. Archive has no declared key comparison; possible dependency does not imply key plaintext in a response or status.
- Nine requirements are expressed, four partial and one retained-only, with 41 traced goals. All 24 sinks inherit eight global blockers; 13 source-backed processing gaps have unmodeled=false. Diagnostic-output prohibition R13 has no specified receiver or serialization; it is not silently equated with status.txt or a model observation.
- Eleven forward constraints are satisfied in the declared static model, including append-before-return and archive-key prohibition. R3 only_if remains potential_violation despite an explicitly declared presence gate; its qualification does not prove source or runtime violation.

The four interface changes in this generated run:

- The 013 unnecessary-write-output fix is directly exercised: all four status appends compute as storage side effects, with no fake whole-file value, extra read or fabricated compute. Allfour returns formerly vulnerable to blockage now have records.
- The actual R3 condition copies the displayed normalized ir_004 operation/self present expression and is structurally accepted. This exercises the expression-reference fix. Constraint satisfaction remains separate.
- The only structural correction fixes R12 source scope using an invalid non-for_each target; it is not an R3 expression-reference failure. No semantic repair occurred.
- The review has findings=[] but diagnostic_only=true, and annotation_review is incomplete. Ownership repair dispatch is therefore not exercised by this case; no claim of review acceptance removes its known gaps.

The remaining blockers are classified by layer:

- Source/modeling precision: absent-binding interface, tool failure envelope, transient classifier, status content and append-failure behavior are unspecified or opaque.
- Task-correspondence/policy: the diagnostic recipient prohibition and partial status/control requirements become global blockers, keeping all 15 DOE comparisons unresolved.
- Constraint analysis: presence-gate R3 returns a qualified potential_violation; the exact expression is valid and source gate represented, so this is not the old reference-interface error.
- Interface/propagation/publication: all selected writes and returns compute and save; no storage-output cutoff remains. Semantic/DOE status remains partial.

Independent source evidence:

- [assessment.en.md](D:/projects/SkillFlow/output/verification/online-interface-r4-20261104/013-source-audit/assessment.en.md)
- [evidence.json](D:/projects/SkillFlow/output/verification/online-interface-r4-20261104/013-source-audit/evidence.json)

These are finite assistant source-audit criteria, not human gold. Supported/contradicted/unresolved relationship labels are not a general accuracy rate, precision, recall, proof of no DOE, or a comparison with direct GPT.

| Request category | Actual starts | Input tokens | Cached input (subset) | Output tokens | Public total |
| --- | ---: | ---: | ---: | ---: | ---: |
| normal_generation | 7 | 169,283 | 86,016 | 26,372 | 195,655 |
| structural_correction | 1 | 28,483 | 12,288 | 324 | 28,807 |
| Total | 8 | 197,766 | 98,304 | 26,696 | 224,462 |

There were 0 outer transport retries, 0 unknown public final-turn usage requests, and 2 public CLI reconnect/wait notices. Internal HTTP attempt counts and any unreported internal-attempt usage are unknown; the notices are not counted as extra model finals. Cached input is already part of input. No currency or hidden-reasoning estimate is made. Raw stdout final turns, final-answer association, process markers, usage sidecars and aggregate counters reconcile in the independent receipt audit.

| Model stage, including its correction if any | Starts | Request elapsed sum (s) | Public total tokens |
| --- | ---: | ---: | ---: |
| flow | 1 | 70.396 | 16,294 |
| graph | 1 | 147.026 | 23,883 |
| processing | 1 | 249.970 | 38,932 |
| review | 1 | 85.661 | 37,844 |
| sensitivity | 1 | 86.920 | 25,266 |
| task | 1 | 86.777 | 18,112 |
| task-correspondence | 2 | 244.357 | 64,131 |

Request elapsed sums include saved request intervals and can overlap across the two workers. They are not the analysis wall clock.

| Local component | Measured seconds |
| --- | ---: |
| propagation_compute | 0.291 |
| propagation_save | 1.871 |
| propagation_total | 2.723 |
| doe_load | 1.306 |
| doe_compute | 2.897 |
| doe_total | 5.767 |
| DOE post-compute publication | 1.446 |
| Main analysis wall | 821.299 |
| Sole replay wall | 23.772 |
| Controller wall, analysis through replay closure | 846.204 |

Component intervals are nested and must not be added to form another total. Propagation total includes its compute/save intervals; DOE total includes load/compute/publication. Unmeasured divisions remain unmeasured.

Backend-r3 processed 19/27 IR, with 4 unmodeled write cutoffs and 4 blocked returns; it used 9 calls, 255,328 public tokens and 816.010 seconds. This run processes 31/31 IR, including all four append/return classes, using 8 calls, 224,462 tokens and 821.299 seconds. The improved completed scope is real; the similar wall time and different generated graph are not a general speedup claim. Both DOE results remain partial.

Saved artifacts: [run-summary.json](D:/projects/SkillFlow/experiments/doe/runs/document-guided-013-interface-r4-high-20261104-173522/run-summary.json), [mechanical-evidence.json](D:/projects/SkillFlow/experiments/doe/runs/document-guided-013-interface-r4-high-20261104-173522/mechanical-evidence.json), [metrics.json](D:/projects/SkillFlow/experiments/doe/runs/document-guided-013-interface-r4-high-20261104-173522/metrics.json), [component-timing.json](D:/projects/SkillFlow/experiments/doe/runs/document-guided-013-interface-r4-high-20261104-173522/component-timing.json), [propagation/manifest.json](D:/projects/SkillFlow/experiments/doe/runs/document-guided-013-interface-r4-high-20261104-173522/propagation/manifest.json), [doe/doe-result.json](D:/projects/SkillFlow/experiments/doe/runs/document-guided-013-interface-r4-high-20261104-173522/doe/doe-result.json), [replay-check.json](D:/projects/SkillFlow/experiments/doe/runs/document-guided-013-interface-r4-high-20261104-173522/replay-check.json).

The archived and current pinned implementation files matched during receipt audit. Source hashes are checked separately by the source audit. Old failures, raw answers and paused v9 processes are preserved. No additional target sampling was added.
