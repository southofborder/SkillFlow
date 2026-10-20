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
| Clean checkout from submitted Git revision | Pending |
| Actual Codex Cloud environment publication | Blocked: signed-in creation dialog cannot load the GitHub connection, including one explicit retry |
| Actual cloud CLI authentication / model / receipts | Not tested; no experiment calls authorized |
| Second-computer continuation | Requires the user to open the same published cloud task |

Local smoke used Python from the current development environment. The PATH CLI
reported `0.121.0`, not the adapter's pinned `0.163.0-alpha.10.2`; no authentication
or inference command was executed. This mismatch is recorded, not bypassed.

The submission is a point-in-time development snapshot. Concurrent prospective
selection work remains unsealed; later edits are not silently overwritten or
declared part of the verified snapshot. The committed manifest, not a live
working-tree directory count, determines the included material identity.

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
