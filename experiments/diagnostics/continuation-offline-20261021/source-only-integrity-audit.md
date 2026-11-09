# Offline source-only integrity and connector audit

Audit time: 2026-10-21T03:37:36.677768+00:00. Git: `2e28bcce25a24f39c54d6c06f215ff3df93b6305`.

The preserved byte seals pass, but the actual historical 24 selected cases and six reserves do not all validate under the current selector. No existing proposal, review, validation pointer, source, preparation, or seal was rewritten.

Current source validation: `needs_review_correction`; 65 reviews checked; 1 errors overall. Among the fixed 30 historical choices, 29 validate and 1 fail. 2 stored connectors in 1 historical choices lack current target support.

The 20-file source cohort seal check passes: `True`. The 770-file preparation freeze check passes: `True`. Read-only `verify_preparation` returns `passed` for 30 packets; that verifier does not rerun the stronger selector.

The source cohort's selector digest is `d1c11da87538642f5aed98ec1d01328d2891d1efa7311a4c0eef1242c1473a25`; the current file is `80f43141c3956aa3247425928052fc23d5095d1948b632108ceec3387e391299`. The digests differ. The historical record remains historical and is not resealed.

Verified historical source measurements: 24 selected plus six reserves; 22 selected source clusters. For the selected 24, reference tokens range 21,361–62,869, median 38,273, total 977,753. Across all 30, median is 37,184.5 and total is 1,182,402. Recorded formal requests and human approvals remain zero, no corresponding execution/approval files were found, and dispatch remains disabled.

These are source-only engineering checks. Exact quotes, hashes, mechanical counts and packet identity do not establish semantic completeness, DOE labels, independent human gold, a successful comparison, or permission to execute.

| Case | Role | Queue | Canonical source | Reference tokens | Current eligibility | Unsupported connectors |
|---|---|---:|---|---:|---|---:|
| real-001 | selected | 1 | jeffaf/bluesky | 21,361 | pass | 0 |
| real-002 | selected | 3 | adamkristopher/ga4-analytics | 62,869 | pass | 0 |
| real-003 | selected | 4 | simmer/polymarket-fast-loop | 28,935 | pass | 0 |
| real-004 | selected | 7 | ivangdavila/docker | 37,221 | pass | 0 |
| real-005 | selected | 9 | matagul/desktop-control | 24,326 | pass | 0 |
| real-006 | selected | 12 | enderfga/openclaw-claude-code | 24,376 | pass | 0 |
| real-007 | selected | 13 | guccidgi/notebooklm-skill | 37,148 | pass | 0 |
| real-008 | selected | 14 | ivangdavila/writing | 37,962 | pass | 0 |
| real-009 | selected | 17 | wemeeting/tencent-meeting-skill | 47,031 | pass | 0 |
| real-010 | selected | 20 | ivangdavila/markdown | 50,675 | pass | 0 |
| real-011 | selected | 22 | sdk-team/alibabacloud-migration-mas-cloud-migration-survey | 34,939 | pass | 0 |
| real-012 | selected | 23 | callmedas69/credential-manager | 21,881 | pass | 0 |
| real-013 | selected | 24 | icemilo414/cognitive-memory | 54,233 | pass | 0 |
| real-014 | selected | 25 | wscats/resume-assistant | 38,584 | pass | 0 |
| real-015 | selected | 26 | dannyshmueli/chart-image | 60,281 | pass | 0 |
| real-016 | selected | 27 | theplasmak/faster-whisper | 57,781 | pass | 0 |
| real-017 | selected | 32 | autogame-17/feishu-evolver-wrapper | 55,212 | pass | 0 |
| real-018 | selected | 35 | qlifebot-coder/ralph-loops | 54,649 | pass | 0 |
| real-019 | selected | 37 | anotb/homeassistant-skill | 27,088 | pass | 0 |
| real-020 | selected | 39 | nevo-david/postiz | 46,362 | pass | 0 |
| real-021 | selected | 41 | atlaspa/openclaw-memory | 50,771 | pass | 0 |
| real-022 | selected | 42 | pskoett/self-improving-agent | 39,543 | fail | 2 |
| real-023 | selected | 43 | robbyczgw-cla/elevenlabs-voices | 32,655 | pass | 0 |
| real-024 | selected | 45 | shashwatgtm/social-media-management | 31,870 | pass | 0 |
| real-025 | reserve | 46 | wscats/juejin-skills | 28,120 | pass | 0 |
| real-026 | reserve | 49 | ad2546/context-optimizer | 33,578 | pass | 0 |
| real-027 | reserve | 50 | eversonl/garmin-health-analysis | 35,613 | pass | 0 |
| real-028 | reserve | 51 | yoder-bawt/yoder-skill-auditor | 34,780 | pass | 0 |
| real-029 | reserve | 52 | zhzai30/clawquest-agent-mine-openclaw | 38,242 | pass | 0 |
| real-030 | reserve | 53 | xrowgmbh/xrowgmbh-gitlab-agent | 34,316 | pass | 0 |

## real-022: pskoett/self-improving-agent (queue 42)

Current error: ValueError: A named text asset lacks explicit operative input/output-template content evidence

Frozen review: `reviews/queue-031-045.json`. Frozen source root: `items/0001-pskoett-self-improving-agent/attempts/20261020T090639376240Z-7eb42d/files`.

Operative-line proof supplied: False; the mechanical proof count is 0, with no line-threshold proof. Claimed operative files: 8.

The current validator first stops before checking edges because these operative members are `text_asset` files and the frozen basis supplies no `operative_content_evidence` for them: `assets/LEARNINGS.md`, `assets/ERRORS.md`, `assets/FEATURE_REQUESTS.md`, `assets/SKILL-TEMPLATE.md`. The stored local-reference quotations are not substituted for that separate content-evidence field.

The connector checks below were then run independently against the unchanged stored edge evidence.

Unsupported connector 6: `SKILL.md` → `hooks/openclaw/HOOK.md`.

The stored source quote is byte/line grounded, but the current connector guard does not establish this exact target. A directory-copy instruction does not establish an operative file reference merely because a target exists in that directory.

Original physical evidence: `SKILL.md:131-132`; quote verified against retained source.

```text
cp -r ~/.openclaw/skills/self-improving-agent/hooks/openclaw ~/.openclaw/hooks/self-improvement
openclaw hooks enable self-improvement
```

Unsupported connector 7: `SKILL.md` → `hooks/openclaw/handler.ts`.

The stored source quote is byte/line grounded, but the current connector guard does not establish this exact target. A directory-copy instruction does not establish an operative file reference merely because a target exists in that directory.

Original physical evidence: `SKILL.md:131-132`; quote verified against retained source.

```text
cp -r ~/.openclaw/skills/self-improving-agent/hooks/openclaw ~/.openclaw/hooks/self-improvement
openclaw hooks enable self-improvement
```

Claimed operative files unreachable using the stored supported edges: `hooks/openclaw/HOOK.md`.

## Reproduction and boundaries

Run from the repository root using the installed offline dependencies:

```powershell
python -B experiments/diagnostics/continuation-offline-20261021/source_only_integrity_audit.py
```

The script denies socket connections, uses `validate_reviews(..., write=False)` and write-free `verify_preparation(...)`, and compares all existing files in both protected trees before and after. It calls no selector-writing path and reads no method output. The preparation helper inspects pending semantic-reference status fields only; this audit does not inspect or generate semantic labels.

Protected files compared: 806; changes: 0. Network connection attempts: 0; model/CLI target requests: zero.

Synthetic selector regressions are separate from the real-cohort audit. Reproduction: `python -B -m pytest tests/doe/test_real_comparison_long_selection.py -q -p no:cacheprovider --basetemp=experiments/diagnostics/continuation-offline-20261021/source-selector-pytest-temp --junitxml=experiments/diagnostics/continuation-offline-20261021/source-selector-tests.xml`. The recorded run passed 45 tests; passing synthetic regressions does not change the actual cohort's failed current gate.

Future handling requires an explicit protocol decision. Options are to supersede affected source-only evidence against the same frozen sources and create a separate fully revalidated seal, preserve this as historical preparation while prospectively choosing another selection procedure, or locate the exact historical selector bytes and explicitly choose that implementation. No option is implemented or authorized by this audit.
