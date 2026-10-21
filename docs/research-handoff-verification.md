# Research handoff submission verification

Date: 2026-10-21. Scope: the two tracked research changes requested by the user,
their focused corrections, documentation and a Git fast-forward. No research
experiment, model request, calibration resume or corpus acquisition was run.

## Reviewed files and corrections

- `tools/doe/real_comparison/long_selection.py`
- `tests/doe/test_real_comparison_long_selection.py`

The pending changes improve physical evidence coordinates, distinguish operative
files from supporting connectors, and accept the explicit source-closure status
used by the preparation workflow. Review found and corrected the following issues
before submission:

| Issue | Final behavior |
|---|---|
| An npm script name could connect an unrelated manifest | Implicit `npm run` evidence must name an exact nonempty script in the source file's colocated `package.json`. |
| A command regex accepted negated text, `cd ... && ...`, or a truncated dotted script name | Only a complete isolated command line with the exact script name establishes this implicit connector. Unsupported composition needs explicit evidence. |
| Recursive-copy suffix matching could connect unrelated absolute/home directories to local members | Removed that added inference. A directory suffix does not prove an individual file's identity. |
| An asset usage keyword could credit a negated or illustrative reference | Restored explicit operative-content evidence; keywords do not supply it. |

Added tests cover root and nested colocated manifests, unrelated targets, malformed
script dictionaries/values, command fragments, directory-copy references, negative
asset prose, canonical portable paths and Boolean line-number rejection. Supporting
connectors can establish reachability without earning operative-file count credit.

These are source-selection evidence checks, not changes to the research threshold,
Task semantics, prompts, propagation, DOE, or evaluation rules. Some frozen older
selection proofs used directory-copy quotations. They were not resealed or
retrospectively declared valid under the tightened implementation.

## Offline regression

Execution host: the existing Windows checkout, using `D:/anaconda3/python.exe`.
The final related suite passed **286 tests**, with **one skip**, in **228.58 seconds**.
The skipped test requires host permission to create a symlink; a separate mocked
link-detection test passed. There were no test failures or errors.

Exact PowerShell command:

```powershell
$handoffTests = @(git ls-files -- 'tests/doe/test_real_comparison*.py')
& 'D:/anaconda3/python.exe' -B -X utf8 -m pytest @handoffTests tests/cloud tests/test_installed_cli.py -q -p no:cacheprovider --junitxml=tmp/cloud-setup/research-handoff-regression-20261021.xml
```

The selection includes tracked comparison tests and explicitly named cloud/CLI
tests. It excludes the newer unreviewed, untracked CLI-v3 tests. Transports are
injected or mocked; no production experiment dispatcher was invoked. This is a
related regression suite, not a claim that the complete repository test suite or
a real Linux Cloud installation passed.

The [verification receipt](verification/research-handoff-20261021.json) retains
the resolved module list, per-module counts, skip, input file hashes and the raw
local JUnit receipt hash. The raw JUnit file remains in the ignored local `tmp/`
directory; the receipt is a derived summary, not a second experiment result.

The earlier 17-test baseline and 41-test intermediate run are development checks.
They overlap the final suite and are not added to its count. The final suite
includes the later exact-command regression.

## Submission and preservation checks

- Base preparation branch: `codex/cloud-setup` at
  `73704423a734584f237b096799e47043f406ecbb`.
- Main before integration: `f8d20063d697ad186b0b530d56d60f3a104000f8`.
- Reviewed selection-code commit: `85d85283` (`Tighten long-skill selection evidence checks`).
- The reviewed changes and new handoff are committed explicitly. No broad
  `git add .`, history rewrite, forced remote update or old-run migration is used.
- `.gitattributes` remains unchanged, including frozen-byte protection.
- Modified billing files are excluded. Their current local hashes are checked
  before and after integration; previously tracked billing history is preserved.
- Newer local-only code and preparation are indexed in
  [the inventory](research-local-only-inventory.json), not submitted as if reviewed.
- New handoff links and inventory hashes are checked. The complete historical
  report link graph is not rewritten or asserted portable.
- The staged submission is checked for private-key markers and common credential
  patterns without printing possible values. This is a scoped check, not a claim
  that all historical repository content was independently audited today.
- `git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol diff --check`
  is part of the final gate. The explicit CRLF setting recognizes preserved
  Windows line endings without rewriting documentation or frozen files.
  Git history records the exact
  code/documentation commits; the final user response records the confirmed
  remote `main` revision rather than a self-referential hash in this document.

The handoff is an English reconstruction of decisions and repository evidence,
not a verbatim conversation export. It explicitly distinguishes committed facts,
local-only records, semantic limitations and authorizations that remain absent.
