"""Record the sole running controller and current navigation; no model action."""
from pathlib import Path
import json

VERIFY = Path(__file__).resolve().parent
PROJECT = VERIFY.parents[2]
prepared = json.loads((VERIFY / "prepared-run.json").read_text(encoding="utf-8"))
run = Path(prepared["run_directory"])
controller = json.loads((run / "controller-started.json").read_text(encoding="utf-8"))
state = json.loads((VERIFY / "continuation-state.json").read_text(encoding="utf-8"))
state.update(status="running", controller=controller,
             instructions="One root-owned fresh GA4 is active. Freeze production, prompts, transport, controller and executables. Observe only. The controller owns its sole terminal zero-call replay. No duplicates, probes, additional cases, Skill execution or historical resume/replay.")
(VERIFY / "continuation-state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
prefix = ("Shared-v2 GA4 ACTIVE (2026-11-12): generic lossless review presentation passed 511/511 current scoped offline tests, zero skips/failures (not a whole-repository run). "
          f"Frozen implementation {prepared['implementation_sha256']}. Root dispatched exactly one new GA4: {run.relative_to(PROJECT).as_posix()}, "
          f"controller PID {controller['pid']}, at {controller['started_at']}. "
          "Read output/verification/online-ga4-review-shared-v2-20261112/continuation-state.json and dispatch-started.json before any action. "
          "Same complete 16-file source, gpt-6.1-sol/high/openai, seven normal requests, two workers and unchanged budgets; guided run v12/shared-v2. "
          "This sole controller owns its one terminal zero-call replay. Freeze accepted implementation/prompts/transport/controller/executables. "
          "Do not dispatch another run, execute Skills, resume/replay historical runs, add probes/small cases/resampling or import staged code. "
          "Offline evidence: output/verification/review-input-size-20261112/offline-acceptance.json; design docs/doe/review-input-size.zh.md. "
          "Earlier closed-run notes remain history.\n\n")
agents = PROJECT / "AGENTS.md"
existing = agents.read_text(encoding="utf-8")
if "Shared-v2 GA4 ACTIVE (2026-11-12):" not in existing:
    agents.write_text(prefix + existing, encoding="utf-8")
print(json.dumps({"status": state["status"], "controller": controller, "run_directory": str(run)}, indent=2))
