"""Record this new authorized offline fix; no model or analysis execution."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import sys

VERIFY = Path(__file__).resolve().parent
PROJECT = VERIFY.parents[2]
sys.path.insert(0, str(PROJECT))
from skillflow.common.recording import implementation_provenance

def save(name, value):
    with (VERIFY / name).open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

previous = PROJECT / "experiments/doe/runs/document-guided-ga4-review-shared-v2-high-20261112-221242"
names = ("result.json", "controller-finished.json", "replay-check.json", "selection.json",
         "review/inputs.json", "review/prompt.txt", "review/result.json", "review/chain.json",
         "review/calls/review/a001/response.json", "review/calls/review/a001/validation.json",
         "review/calls/review/a002/response.json", "review/calls/review/a002/validation.json",
         "doe/audit/input-contract-review.json", "doe/doe-result.json")
save("baseline-provenance.json", implementation_provenance())
save("preserved-artifact-hashes.json", {name: hashlib.sha256((previous / name).read_bytes()).hexdigest()
    for name in names if (previous / name).is_file()})
state = {"status": "diagnosing", "created_at": datetime.now(timezone.utc).isoformat(),
    "authorization": "User requested diagnosing the three failed missing-field locators and whole-review invalidation, implementing a general fix without weakening validation; retain seven normal requests, two workers and existing budgets, then after offline acceptance root alone runs one fresh GA4.",
    "previous_closed_run": str(previous.relative_to(PROJECT)),
    "baseline_implementation_sha256": implementation_provenance()["sha256"],
    "model_starts": 0, "scope": "Offline diagnosis and general implementation, then one newly prepared GA4 and its sole controller-owned zero-call replay.",
    "constraints": ["Strict validation is retained; malformed facts are not accepted.",
                    "Preserve complete source, all obligations, exact identities and affected dependency scopes.",
                    "No historical replay/resume, Skill execution, probes, extra cases or staged-code import.",
                    "Freeze accepted implementation and existing budgets through the one fresh online run and replay."]}
save("continuation-state.json", state)
agents = PROJECT / "AGENTS.md"
agents.write_text("Current authorization (2026-11-13, source-review locality): the user requests a general fix for missing-field locator correction and local errors invalidating all contract review, without weakening validation. Keep seven normal semantic requests, two workers, Task v5 isolation and existing budgets. Diagnose and verify offline first; root alone may then prepare and start exactly ONE NEW GA4 gpt-6.1-sol/high/openai with the same complete source and its sole zero-call replay. Read output/verification/source-review-locality-20261113/continuation-state.json. Preserve prior closed runs and raw failures; no historical resume/replay, Skill execution, extra probes/cases/resampling or staged-worktree code. Freeze accepted implementation/prompts/transport/executables through the new run. This explicit authorization supersedes consumed earlier notes only for this fix and one fresh run.\n\n" + agents.read_text(encoding="utf-8"), encoding="utf-8")
print(json.dumps(state, indent=2))
