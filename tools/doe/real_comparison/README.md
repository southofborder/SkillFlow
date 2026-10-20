# Real Skill same-model comparison

This isolated driver implements the preregistered ClawHub comparison. It does
not install or execute downloaded Skills. It does not dispatch a model by itself,
and it never treats an assistant draft as a human confirmation.

The frozen question is whether SkillFlow has an actual advantage over direct
audit or one-prompt full-chain audit. All methods audit the Skill's declared
purpose. There is no independent user task. A declared purpose is not independently
verified user authorization, and an existing implementation is not proof that its
payload is necessary.

## Collection and source-only selection

Run commands from the repository root. The corpus default is
`experiments/doe/inputs/clawhub-top1000-v1`. Supply the exact run directory with
`--run-dir` for run-specific commands.

```powershell
python -m tools.doe.real_comparison acquire --workers 4
python -m tools.doe.real_comparison verify-corpus
python -m tools.doe.real_comparison screen
python -m tools.doe.real_comparison select
python -m tools.doe.real_comparison prepare --run-dir <run-directory>
```

The official downloads-ranked roster is sealed before package downloads. The
first 1,000 distinct owner-qualified identities remain the roster even when a
package is missing, blocked, or invalid. Pagination is a collection-window view,
not an atomic snapshot. Immutable attempts preserve HTTP responses, version
manifests, original archives and source hashes. An interrupted collector resumes
the same roster without substituting another version or rank.

The first collection disclosed one acquisition deviation: four hosted entries
without a frozen version pin received unversioned download requests before a
later check rejected the archives. None produced an accepted source view or
entered eligibility. The immutable attempt records and
`acquisition-protocol-deviations.json` retain this fact. Current acquisition code
rejects a missing hosted pin before requesting an archive; a regression verifies
zero download calls in that situation. Raw accounting success does not erase
this protocol deviation.

`selection.py` separates physical eligibility from source-reviewed feature
evidence. Regex nominations are reading aids, never accepted semantic labels.
Source review records quote physical file lines and classify local references.
Separate Skill/service dependencies may remain explicitly unknown. A broken
documentation path is not automatically missing source when the intended original
document is unambiguously retained elsewhere in the package; retain the actual
paths and uncertainty without inventing an executable alias. Missing indispensable
source content prevents formal selection.

The final eligible population must be accounted for before the seeded shuffle.
Exact and near source forks are grouped, including substantially shared file
trees with rewritten entry documents. Source clusters include publishers and
upstream repositories. The 24 selected cases and six reserves are frozen with
their original numbered bundles, raw source, tokenizer measurements and exclusion
evidence. No result-dependent selection or replacement is permitted.

## Human reference boundary

Prepared packets initially contain assistant source-fact drafts. Their explicit
`coverage_state` remains pending until the complete semantic reference has been
constructed from source. Empty draft receiver or DOE lists do not mean that no
receivers or DOE exist.

Complete every ledger, distinguishing declared purpose, required behavior,
implementation choices, necessary sensitive use, supported excess, uncertain
contracts, receiving points and preservation checks. A supported exposure has six
separate identity fields: source, sensitive scope, version, condition, recipient
and boundary event. Every interpretation and mandatory check needs exact evidence
objects with `path`, `start_line`, `end_line`, and an original-language `quote`.
Use `coverage_state: complete_for_human_verification` only when the ledger is
complete enough for the two independent human checks. This declaration is not a
software proof of semantic completeness.

Register two actual human reference verifiers and three separate timed reviewers
in `human-roster.json`, starting from the supplied template. Reviewer pseudonyms
are self-attested identity records, not personhood verification. Assistant agents
cannot register themselves as people or submit human confirmations.

Each of the two reference verifiers must personally inspect every selected and
reserve source/reference pair, before viewing target output. Import their own
records with:

```powershell
python -m tools.doe.real_comparison import-human --run-dir <run-directory> --submission <human-record.json>
python -m tools.doe.real_comparison freeze-references --run-dir <run-directory>
python -m tools.doe.real_comparison freeze-gate --run-dir <run-directory>
```

The reference confirmation binds the exact source and reference hashes and uses
the statement `I personally verified this source reference.` Two different
registered humans are required per case. Reference interpretation remains subject
to human error; later genuine corrigenda must preserve the original reference
and regrade all methods and repeats without generating new target answers.
After the complete target cohort has been closed by `freeze-outputs`, a correction
can create a new grading epoch using the exact same target answers:

```powershell
python -m tools.doe.real_comparison prepare-corrigendum --run-dir <run-directory> --case-id <case-id> --submission <proposed-reference.json> --reason "Source-grounded correction reason"
python -m tools.doe.real_comparison import-corrigendum --run-dir <run-directory> --corrigendum-id <returned-correction-id> --submission <first-human-confirmation.json>
python -m tools.doe.real_comparison import-corrigendum --run-dir <run-directory> --corrigendum-id <returned-correction-id> --submission <second-human-confirmation.json>
python -m tools.doe.real_comparison activate-corrigendum --run-dir <run-directory> --corrigendum-id <returned-correction-id>
python -m tools.doe.real_comparison prepare-scoring-packets --run-dir <run-directory>
```

The two confirmations must come from distinct registered reference verifiers and
bind the proposed reference and unchanged source hashes. Preparation keeps the
old references, scores and target artifacts byte-for-byte; activation seals a new
reference freeze inside an independent copied workspace. All 264 grading results
start pending, and no advantage conclusion is available until the new epoch has
complete adjudication. Grade templates bind `grading_epoch_id`; imports and
scoring resolve to the active epoch and reject prepared or superseded workspaces.
Further corrections start from the current reference version. Original target
generation stays closed throughout.

The original 72 timed first readings are shared across epochs, with submitted
records preserved unchanged; they are not repeated after a correction. Their
current quality judgments require new independent adjudication. Target response
IDs count once across the logical study, while incremental human confirmation,
regrading and adjudication work is reported separately. Copied confirmation and
timing records are deduplicated rather than counted as new work. Missing active
time remains unknown. Earlier frozen reference-construction documents remain
historical records; this maintained workflow adds the subsequent correction path.

## Target requests and known transport limitation

The required runtime is `gpt-6.1-sol / ultra / openai`, using fresh
`fork_turns="none"` children for every semantic request. Production core prompts
are left unchanged. API-only configuration is empty and explicitly nonbinding
for the injected mailbox. The experiment verifies actual child receipts instead.

The mailbox worker invokes the native graph pipeline from source, then independent
Task extraction, annotation, review and at most one controlled repair, propagation
and deterministic DOE. No historical graph or cross-repeat semantic cache is
reused, and no final model-written summary is added. Direct prompts are frozen
copies of the previous experiment's final templates, with common declared-purpose
input rendering. Self-review uses only the original task and exact first answer.

```powershell
python -m tools.doe.real_comparison worker --run-dir <run-directory> --workflow-id <planned-id> --source-path <frozen-source>
python -m tools.doe.real_comparison pending --run-dir <run-directory>
python -m tools.doe.real_comparison authorize --run-dir <run-directory> --request-id <request-id>
python -m tools.doe.real_comparison import-response --run-dir <run-directory> --request-id <request-id> --receipt-path <exact-child-rollout>
```

These commands do not implement the supervisor's actual collaboration call.
That interface accepts literal message arguments rather than a file argument.
Manual embedding caused one disclosed calibration source change; that failed
attempt was stopped and preserved, and its answer is not a conformant result.

The older PATH CLI (`0.121`) does not support the required `ultra` setting. A
separate application-bundled CLI (`0.163.0-alpha.10.2`) was subsequently tested in
one explicitly authorized feasibility request. Its exact stdin delivery matched
all **62,084 UTF-8 bytes** of the saved prompt. The receipt verified
`gpt-6.1-sol / ultra / openai`, **57,577 reported total tokens**, approximately
**626 seconds**, and no tool use. The visible response parsed as JSON; semantic
correctness was not evaluated. The
[feasibility record](../../../experiments/doe/runs/real-same-model-v1-20261020-090239Z/transport-inspection/feasibility-result.json)
retains the original failed collaboration attempt separately.

This establishes feasibility of one exact stdin request. It does not authorize
formal adoption of the CLI transport, satisfy the preregistered fresh-child
transport, or establish success of the three full native engineering
calibrations. Changing the formal transport requires an explicit protocol
amendment; formal generation remains gated by that decision, complete calibration
and actual human reference confirmation. No further target requests are
authorized by this feasibility result.

Requests are bounded by 64 actual children, eight million reported total tokens,
six hours per workflow, and 45 minutes per outstanding child. Complete delivery
over 300,000 reference tokens fails without clipping. Missing per-response usage
stays unknown and prevents another dispatch. A timeout requires supervisor child
termination; writing a local stop file alone does not terminate an agent.

Every success, failure, correction, interruption and actual retry remains in the
ledger. Receipts are imported using exact child and turn attribution. Token counts
are deduplicated by response ID; session totals, output character counts and
inferred currency prices are not substitutes. Hidden reasoning is not exported.
Encrypted receipt bodies cannot prove plaintext delivery equality. Protocol
isolation is not a hard filesystem sandbox.

## Closing generation, scoring and timed review

All 264 prespecified results, including failures and unavailable self-reviews,
must exist before reference-aware scoring starts. Close generation with:

```powershell
python -m tools.doe.real_comparison freeze-outputs --run-dir <run-directory>
python -m tools.doe.real_comparison prepare-scoring-packets --run-dir <run-directory>
python -m tools.doe.real_comparison prepare-timed-packets --run-dir <run-directory>
python -m tools.doe.real_comparison import-grade --run-dir <run-directory> --submission <human-score.json>
python -m tools.doe.real_comparison grade --run-dir <run-directory>
```

An output freeze disables later formal dispatch. Human scores bind candidate and
reference hashes and personally confirm `I personally checked this candidate
against the source reference.` Score every mandatory source check and merge
duplicate exposure descriptions. Format, field counts and length do not receive
credit. The primary endpoint is common to all methods; chain completeness is a
separate endpoint for SkillFlow and the full-chain prompt.

All errors and disputes, and a seeded 20 percent sample of initial passes,
require the other human's independent check. Unresolved disagreements are not
converted into definite errors or definite accuracy estimates. Failures remain in
the complete planned denominator. Statistics average the three repeats inside
each case and account for source clusters. The two primary comparisons use Holm
adjustment; practical accuracy requires at least a 10 percentage point difference
with supporting evidence, symmetrically for either method. Efficiency requires
supported quality noninferiority within five points and at least a 20 percent
resource or review-time reduction. No weighted overall winner is manufactured.

Timed review assigns three separate people 72 first-repeat main-method artifacts
in balanced rotation. Each person sees one method for a given case and eight
artifacts per method. The offline timer escapes all source and answer content,
pauses for breaks/hidden pages, and caps active work at 30 minutes. It exports
pending-quality human records; independent adjudication is still needed. Retain
timeouts, unresolved work and quick incorrect reviews; do not label them cheaper
successful review. Structure can reveal the method despite anonymized labels.

```powershell
python -m tools.doe.real_comparison import-timed --run-dir <run-directory> --submission <human-timed-record.json>
python -m tools.doe.real_comparison import-timed-adjudication --run-dir <run-directory> --submission <independent-human-quality-record.json>
```

## Offline replay and engineering evidence

```powershell
python -m tools.doe.real_comparison replay --run-dir <run-directory>
python -m tools.doe.real_comparison report --run-dir <run-directory>
python -m pytest tests/doe/test_real_comparison_*.py -q
```

Replay makes zero model calls. Byte integrity, protocol conformance, completeness
of accounting and semantic correctness are distinct claims. A preserved invalid
call can pass byte-integrity replay while the experiment protocol still fails.
When selection and schedule exist, replay also regenerates the score aggregation
from already imported human records, the observed cost ledger and the readable
report. It reports incomplete or unprepared human scoring explicitly and never
creates approvals or judgments. A failed protocol replay remains failed even
when these deterministic derived artifacts regenerate successfully. Invalid
score/cost evidence prevents report regeneration from stale derived artifacts.
Engineering tests never count as target semantic successes. Preparation, formal
target usage, human reference work, human scoring and practical review costs are
separate categories; any unobserved cost remains explicitly unknown.
