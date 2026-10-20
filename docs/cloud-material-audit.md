# Cloud material audit

Date: 2026-10-20 (Asia/Shanghai). This audit inspected local files without
running a Skill or issuing a model request. It did not edit frozen inputs,
responses, protocols, or experiment results.

## Material closure to synchronize

The following roots contain the current comparison inputs, preparation,
calibration evidence, latest native analysis, and its direct baseline. Counts
below are a local snapshot taken after the stopped CLI calibration completed.
They exclude run locks, progress logs, and local Python caches, but include the
one bytecode file shipped inside an acquired source archive.

| Repository-relative root | Files | Bytes | Reason |
|---|---:|---:|---|
| `experiments/doe/inputs/clawhub-top1000-v1` | 29,680 | 513,180,100 | Frozen roster, acquisition attempts, archives, source views, and source-only selection evidence |
| `experiments/doe/inputs/direct-baseline-v1` | 51 | 77,299 | Prior-exposure package identities used by comparison selection; synthetic baseline inputs |
| `experiments/doe/inputs/direct-baseline-references-v1` | 4 | 233,672 | Preserved assistant-authored baseline references, not human ground truth |
| `experiments/doe/runs/real-same-model-v1-20261020-090239Z` | 1,412 | 38,609,235 | Current comparative protocol, 30 source packets, preparation, prospective long-source selection, and historical transport evidence |
| `experiments/doe/runs/real-same-model-v2-cli-20261020-1311Z` | 241 | 2,533,075 | Separate, permanently calibration-only CLI run and its retained stop |
| `experiments/doe/runs/constraints-pipeline-v1-20261020-162606` | 369 | 243,134,212 | Latest three-case research results, original calls, analysis, replay, and assistant assessment |
| `experiments/doe/runs/direct-baseline-v1-20261019-171200` | 1,796 | 15,785,463 | Frozen direct baseline and the exact prior prompt templates used by `real_comparison.inputs` |

The prospective selection and calibration were being completed in a separate
chat during this audit. These counts are not a final cohort seal or a substitute
for the committed material manifest. The staging/commit process must record
its own final file identities after checking for concurrent changes.

Existing tracked dependencies already cover:

- `experiments/corpus/semantics_review/inputs/upstream`: source packages for the
  three CLI calibrations.
- `experiments/propagation/runs/sink-tightening-v1-20261002-205045`: all 238
  frozen three-case source/CFG and historical fact files.
- `experiments/doe/inputs/sensitivity-v1`: all five fixture receipts.
- `experiments/doe/runs/backward-demand-v1-20261011-215237`: 62 tracked files;
  its four remaining local files are ignored run locks.
- `dataset/unzipped`: the already tracked prior-exposure packages.

The current comparison tests construct temporary synthetic inputs and fictional
receipts. They do not require the acquired corpus or real runs merely to execute.
The old Task Evidence directory appears in an imported fixture constant, but
current tests do not read that directory through the constant. It need not be
added for test execution. Other untracked historical runs remain local.

One frozen acquired artifact is normally ignored by Git:

```text
experiments/doe/inputs/clawhub-top1000-v1/items/0619-robbyczgw-cla-personas/attempts/20261020T095004255969Z-62b507/files/scripts/__pycache__/persona.cpython-312.pyc
```

It is a 12,932-byte member of the original downloaded package, explicitly bound
by `result.json` and `source-view.json`. It must be included explicitly when
preserving the corpus; it is not a cache produced by this project. Do not execute
it. Run `.runner.lock`, `dispatcher.lock`, local caches, and progress logs are
not portable active state.

## Offline verification

The following checks were run from the repository root with
`D:/anaconda3/python.exe -X utf8`. They only read materials:

```python
from pathlib import Path
from tools.doe.real_comparison.acquisition import verify_corpus
from tools.doe.real_comparison.selection import verify_reference_packets
from tools.doe.real_comparison.long_selection import validate_reviews

corpus = Path("experiments/doe/inputs/clawhub-top1000-v1")
run = Path("experiments/doe/runs/real-same-model-v1-20261020-090239Z")

corpus_result = verify_corpus(corpus)
packet_result = verify_reference_packets(corpus, run / "cases")
review_result = validate_reviews(
    run / "selection-inspection/long-v2", corpus, write=False
)
```

- Corpus: `verified`, 1,000 recorded attempts, 993 `complete_verified` packages,
  seven preserved integrity/format failures, zero verification errors, zero
  model calls. Verified accounting does not erase the disclosed acquisition
  deviation or make failed packages eligible.
- Source packets: all 30 verified, zero errors, zero model calls.
- Prospective long-source reviews: the first read-only attempt raised
  `KeyError('records')`. A later read, after separately produced selection files
  changed, returned `validated_available_reviews`: 141 candidates, 50 completed
  reviews, four review batches, zero errors, `final_seal: false`, and zero formal
  target calls. These are distinct observations, not a claim that the first
  attempt passed or that the prospective cohort is complete.

No audit operation rewrote a historical hash. Tests and identity checks for a
fresh cloud environment must use a new environment identity.

## Portability and stopped calibration

The long-selection `rules.json` binds four original absolute Windows paths.
The current loader resolves those paths directly. Their original bytes should
remain unchanged; copying the files to Linux does not make that old invocation
portable.

The v2 CLI calibration also binds an original Windows executable path and hash,
CLI version, runtime developer envelopes, and local receipt paths. It cannot be
resumed as an equivalent Linux execution. Its APIs permanently reject formal
dispatch, even if a gate file claims approval.

One CLI request completed during this audit from work already initiated in the
other chat. It was stopped at `2026-10-20T13:22:49Z` because:

```text
Runtime developer instructions differ from the pinned common CLI harness
```

Configuration, provider, and usage attribution were verified, but protocol
conformance failed. Recorded usage was 55,798 total tokens, and recorded response
duration was 609,995 ms. `dispatch-stop.json` forbids further dispatch or automatic
retry in this run. The dispatcher lock was removed by that running workflow;
this audit neither removed it nor launched the request. This calibration is not
a formal long experiment and is not evidence that cloud transport is ready.

## Bounded credential and path inspection

Recommended material roots contained no symlinks and no individual file above
50 MiB. The largest observed file was a roughly 26.3 MB transport record.

Filename inspection found no local login database, `auth.json`, credential
store, or private-key file in the runs. The two sensitive-looking source
filenames were an upstream `.env.example` with an empty API-key value and a
public signing key containing `BEGIN PUBLIC KEY`, not private-key material.

A bounded content scan checked private-key markers and common provider/GitHub
token patterns without printing matched values. Additional JSON/JSONL checks
looked for populated credential/authorization fields. No such matches appeared
in the current v1/v2 comparison runs, latest constraints run, or direct baseline
run. Corpus matches were in the acquired prompt-guard credential-redaction
tests and a GA4 documentation placeholder; they were reviewed as source test
and documentation material. Frozen source bytes were not sanitized or rewritten.

This inspection is not proof that arbitrary acquired source contains no secret.
It does establish that no local credential file was deliberately included and
that observed pattern matches were reviewed without exposing their values.
Personal billing artifacts under `output/pdf/` are unrelated and excluded.
