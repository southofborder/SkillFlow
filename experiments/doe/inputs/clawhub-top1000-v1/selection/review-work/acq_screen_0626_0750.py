"""Explicit source reviews for the assigned 626-750 partition."""
import runpy
globals().update(runpy.run_path("experiments/doe/inputs/clawhub-top1000-v1/selection/review-work/acq_screen_0301_0400.py"))
DECISIONS.clear()
S = json.loads((C / "selection/acq_screen_0626_0750_snapshot.json").read_text(encoding="utf-8"))
ROWS.clear()
ROWS.update({row["rank"]: row for row in S["entries"]})

for rank, login_line in [(638, 52), (665, 54), (678, 52)]:
    include(rank, [feature(rank, "persistence_or_cross_session", "SKILL.md", login_line, login_line, "The documented OAuth login retains a profile and renewable tokens in host configuration/credential storage; this is a source declaration, not deployment verification."), feature(rank, "conditions_or_retries", "SKILL.md", login_line + 16, login_line + 17, "Unauthenticated state selects stopping and logging in again, while API-key mode receives different credential guidance.")], "All nine enumerated trigger-source catalogues and the app entry are retained. Maton and app servers are external interfaces, and credentials/configuration/events are runtime state. Shared trigger catalogues do not establish that this particular app is an event source.", [{"target": "references/{source}/triggers.md", "classification": "illustrative_or_optional", "reason": "The parameterized source name resolves to the retained concrete catalogue files explicitly enumerated by the entry."}])

for rank, token_line, pair_line in [(677, 86, 91), (689, 86, 91), (714, 71, 76), (716, 71, 76), (724, 85, 90)]:
    include(rank, [feature(rank, "persistence_or_cross_session", "SKILL.md", token_line, token_line, "The source explicitly declares hosted OAuth-token retention and injection into app requests; the hosting service's implementation remains an external contract."), feature(rank, "conditions_or_retries", "SKILL.md", pair_line - 1, pair_line + 1, "An unconfigured plugin/account selects the pairing/connection setup sequence instead of assuming a usable connection.")], "The published package is an instruction-only interface guide: ClawLink/plugin and app API implementations are explicitly external dependencies, not claimed missing bundled code. Its setup, tool contracts and execution workflow remain in the retained entry; logos/GIFs are illustrative assets and not source implementations.")


save("acq_screen_0626_0750_0001.json")
