# Cloud preparation verification

This record describes preparation on `codex/cloud-setup`. It is not a research
evaluation, a cloud authentication receipt, or authorization to start a model
experiment.

## Submission boundary

Include current SkillFlow source, tests, tools, maintained documentation, and
the complete material closure needed for the current comparison. Keep already
tracked historical materials and `.gitattributes` (`* -text`) unchanged.
Do not rewrite Git history, introduce bulk LFS conversion, or upload local
credentials. Unrelated bill-template changes remain outside this commit.

The current source work is carried forward as it stood before cloud preparation;
cloud tools are separate from the production pipeline. This task does not
change research prompts, analysis rules, experimental selection, or scoring.

Frozen content can retain original absolute Windows paths. Byte integrity does
not mean a historical producer can run on another platform. The stopped CLI
calibration, its old producer identity, and long-selection path assumptions are
documented in the [handoff](cloud-research-handoff.md).

## Checks

| Check | Status |
|---|---|
| Dedicated preparation branch | Created from `f8d20063d697ad186b0b530d56d60f3a104000f8` |
| Portable setup and guarded CLI / offline graph smoke | Implemented; local check passed |
| Cloud tools, installed CLI, transport guards, recovery and selection regressions | 120 passed, 1 skipped in 53.43 seconds |
| Full current regression suite | Started, then stopped during the slow full-pipeline load/replay group; not counted as passing |
| Current material closure and byte inventory | 33,985 files / 963,396,696 bytes verified; exact paths and SHA-256 retained in `experiments/configs/cloud-materials-v1.json` |
| Credential / unrelated-file review | Bounded source and material scans completed; final index scope checked separately |
| New handoff/navigation links | 21 local targets exist; unrelated historical links were not included in this check |
| Setup script syntax and line endings | Bash syntax check passed; cloud scripts use LF without a UTF-8 BOM |
| Clean checkout from submitted Git revision | GitHub clone at `43dc849` completed; editable install, import isolation, CLI help and offline compile/render passed |
| Material verification in the deeper Windows checkout path | Two-pass audit passed: 33,468 files verified by the original command, then all 517 ordinary-path lookup failures rechecked with the same validators and an extended-length root; 33,985 files / 963,396,696 bytes total, zero remaining failures or skipped entries |
| Focused regressions from the GitHub checkout | 120 passed, 1 skipped in 52.63 seconds; tracked checkout remained clean |
| Actual Codex Cloud environment publication | Blocked: repository selection recovered after a page refresh, but environment initialization failed, including one explicit initialization retry |
| Actual cloud CLI authentication / model / receipts | Not tested; no experiment calls authorized |
| Second-computer continuation | Requires the user to open the same published cloud task |

Local smoke used Python from the current development environment. The PATH CLI
reported `0.121.0`, not the adapter's pinned `0.163.0-alpha.10.2`; no authentication
or inference command was executed. This mismatch is recorded, not bypassed.

The fresh Windows GitHub clone initially stopped at a long path inside a
frozen upstream package's vendored environment. Enabling `core.longpaths` in
that verification clone allowed checkout completion. No frozen path was
renamed, shortened or omitted, and no global Git setting was changed. A new
Windows verification clone should supply `git -c core.longpaths=true clone ...`
at creation time.

Git long-path support and Python path lookup are separate. The first complete
manifest command in the deeper verification directory returned failure for
517 paths beyond the ordinary Windows path limit. It verified the other
33,468 files (959,199,647 bytes) and reported no content mismatches. That failure
record is retained; the default command is not claimed to have passed.

Exactly those 517 entries were then rechecked using the unchanged `_load`,
`_checked`, and `_digest` helpers with the Windows extended-length root. Every
entry passed the same path-containment, link, regular-file, byte-count and
SHA-256 checks. The recheck took 9.70 seconds and accounted for the remaining
4,197,049 bytes. Combined coverage is 33,985 files / 963,396,696 bytes, with no
skipped entries, remaining missing files or mismatches. The sealed manifest
SHA-256 is
`0bcace1948c8d814652aae334270779fa1a92232a4486894ffcd3147d08ce15f`.
The common project-root resolver was also verified to preserve the explicit
extended-length root. No validator, source, manifest or frozen byte was
changed to obtain this result.

Clean-checkout verification uses a new virtual environment with
`--system-site-packages`: the package is installed from the GitHub checkout,
while dependency packages are inherited from the installed development
environment. The resolved `skillflow` import was checked against the clone's
`src/skillflow` directory. This establishes checkout/package isolation, not a
fresh Linux dependency-resolution result. The cloud setup script will still
install project-declared dependencies in its actual environment.

The clean-checkout regression ran the same focused command shown below, using
the new virtual environment from the clone directory. Its count is a repeated
verification of the same group, not an additional set of unique tests.

The submission is a point-in-time development snapshot. Concurrent prospective
selection work remains unsealed; later edits are not silently overwritten or
declared part of the verified snapshot. The committed manifest, not a live
working-tree directory count, determines the included material identity.

The first submitted revision is
[`43dc8494921290878eac5a6b472bbfbe0a27f36d`](https://github.com/southofborder/SkillFlow/commit/43dc8494921290878eac5a6b472bbfbe0a27f36d).
`git ls-remote` confirmed that exact revision at
`refs/heads/codex/cloud-setup`. Repository visibility and permissions were not
changed; the preparation branch has not been merged into `main`.

In the signed-in Cloud creation UI, the initial GitHub connection-list error
cleared after refreshing the page. The selected repository was
`southofborder/SkillFlow`. Starting setup then reported that the setup chat
could not start, and its environment panel reported that SkillFlow environment
creation had failed. One explicit initialization retry produced the same
failure. This is a separate failure from the earlier repository-list error.
The UI did not expose a cause. No usable cloud checkout, setup command execution,
publication, or **Only me** access setting has been confirmed. Do not describe
the local clean-checkout checks as cloud execution.

Once initialization becomes available, continue the existing setup attempt if
possible, select `codex/cloud-setup` before installation, run the setup command
below, and confirm the environment is named `SkillFlow` with access **Only me**
before publication. Do not start a research task or calibration to test the
environment. Publication, a real cloud checkout, and continuation from a second
computer remain separate unchecked items.

The exact focused regression command was:

```text
python -B -X utf8 -m pytest tests/cloud tests/test_installed_cli.py tests/doe/test_real_comparison_cli_adapter.py tests/doe/test_real_comparison_cli_amendment.py tests/doe/test_real_comparison_execution.py tests/doe/test_real_comparison_long_selection.py -q -p no:cacheprovider
```

The skip requires real Windows symlink creation privileges; a separate mocked
link-rejection test passed. Injected transports and fabricated test receipts
do not count as live calibration. The initial 12-test smoke and later cloud-only
checks overlap this group and are not added to its count.

A separate scan of 536 maintained source, test, tool and documentation files
found no matches for the selected credential-token/private-key patterns.
The [material audit](cloud-material-audit.md) records corpus and run checks,
reviewed synthetic-pattern matches, acquisition failures and current selection
status. These are bounded inspections, not a universal no-secret guarantee.

Setup:

```bash
bash tools/cloud/setup.sh
```

Offline regressions:

```text
python -B -X utf8 -m pytest tests -q -p no:cacheprovider
```

If formal verification is needed, install exactly `formal/lean-toolchain` and
run `lake build` and `lake env lean ProofAudit.lean` inside `formal/`. Python
installation does not imply that these Lean checks ran.
