"""Persist explicit assistant source-screening decisions; no target outputs used."""
from pathlib import Path
import json
from tools.doe.real_comparison.selection import SCHEMA, validate_evidence

C = Path("experiments/doe/inputs/clawhub-top1000-v1")
S = json.loads((C / "selection/acq_screen_0301_0400_snapshot.json").read_text(encoding="utf-8"))
ROWS = {x["rank"]: x for x in S["entries"]}
DECISIONS = {}


def evidence(rank, path, first, last=None):
    last = first if last is None else last
    lines = (C / ROWS[rank]["source_dir"] / path).read_text(encoding="utf-8-sig").splitlines()
    return {"path": path, "start_line": first, "end_line": last, "quote": "\n".join(lines[first - 1:last])}


def feature(rank, name, path, first, last, reason):
    return {"feature": name, "reason": reason, "evidence": [evidence(rank, path, first, last)]}


def include(rank, features, closure, refs=None):
    row = ROWS[rank]
    DECISIONS[row["canonical_id"]] = {"source_tree_sha256": row["source_tree_sha256"], "reviewer_kind": "assistant_source_review", "reviewer_id": "acq_screen", "decision": "include", "reason": "At least two behavior-level source features and local source closure were reviewed without method outputs, DOE labels, scanner judgments, or reference answers. Assistant eligibility review does not establish human reference validity or safety.", "features": features, "source_closure": {"status": "complete_for_static_audit", "reason": closure, "local_reference_decisions": refs or []}}


def exclude(rank, reason, cites, refs=None):
    row = ROWS[rank]
    DECISIONS[row["canonical_id"]] = {"source_tree_sha256": row["source_tree_sha256"], "reviewer_kind": "assistant_source_review", "reviewer_id": "acq_screen", "decision": "exclude", "reason": reason, "features": [], "exclusion_evidence": cites, "source_closure": {"status": "incomplete", "reason": reason, "local_reference_decisions": refs or []}}


# These six source packages were individually checked: each retains the nine
# concrete trigger catalogues and uses the same declared device-login contract.
for rank, login_line in [(302, 54), (306, 55), (320, 55), (321, 55), (348, 52), (374, 52)]:
    include(rank, [feature(rank, "persistence_or_cross_session", "SKILL.md", login_line, login_line, "The documented OAuth login retains a profile and renewable access/refresh tokens in host configuration and credential storage; this is a declared mechanism, not a measured deployment guarantee."), feature(rank, "conditions_or_retries", "SKILL.md", login_line + 16, login_line + 17, "Unauthenticated state requires stopping and logging in again; API-key authentication receives different handling guidance.")], "The entry and all nine named platform trigger catalogues are retained. Maton CLI, app servers, account configuration and event data remain external interfaces or runtime inputs. Shared catalogue text does not make this app an event source or prove server-side controls.", [{"target": "references/{source}/triggers.md", "classification": "illustrative_or_optional", "reason": "The parameterized source name refers to the retained concrete catalogue files enumerated in this package, rather than an absent required implementation."}])

include(304, [feature(304, "conditions_or_retries", "mobile.md", 5, 11, "The supported responsive rendering mode changes layout rules at explicit viewport-width conditions."), feature(304, "versions_or_transformations", "mobile.md", 13, 21, "The responsive mode changes a data table's displayed representation into cards and converts multi-column forms into vertical layouts; this is presentation transformation, not a claim that content is removed.")], "All six named design references are retained. The project tree in stack.md is an illustrative generated application layout; external frontend packages and the eventual user application are not claimed bundled implementations.")
include(307, [feature(307, "element_or_recipient_pairing", "SKILL.md", 8, 10, "Each plan task is assigned to its own fresh implementation subagent, with the task-specific review sequence retained."), feature(307, "conditions_or_retries", "SKILL.md", 220, 224, "A review finding selects repair by the same implementer followed by repeated review until approval.")], "All three referenced implementer/reviewer prompt files are retained. The user's plan and repository are runtime inputs, and named companion superpowers skills are external workflow dependencies rather than missing files from this published prompt package.")
include(310, [feature(310, "conditions_or_retries", "scripts/screen-info.ps1.txt", 123, 129, "In screenshot mode an explicit target selects window lookup; a missing target window produces an error instead of a screenshot."), feature(310, "persistence_or_cross_session", "scripts/screen-info.ps1.txt", 142, 144, "The supported screenshot operation persists bitmap content as a PNG at the selected filesystem path.")], "All five scripts are retained under their original .ps1.txt publish names. SKILL.md explicitly documents the required local renaming, so the extension mismatch is not missing implementation. Windows APIs, running applications and clipboard/screen content remain external runtime state.")
include(311, [feature(311, "versions_or_transformations", "SKILL.md", 44, 51, "The rebase mode explicitly edits, combines, drops or preserves commit versions and messages."), feature(311, "conditions_or_retries", "SKILL.md", 145, 149, "The bisect workflow skips a revision when its build cannot compile.")], "This is a self-contained Git workflow reference. Repository histories and target branches are runtime inputs. The example test script is shown inline, not an absent bundled implementation.")
include(312, [feature(312, "versions_or_transformations", "scripts/yf.py", 40, 46, "The chart/report implementation derives moving-average differences, signal series and histogram values from close-price data."), feature(312, "conditions_or_retries", "scripts/yf.py", 125, 128, "An empty downloaded price history returns without constructing a chart.")], "The referenced yf.py implementation is retained. Yahoo Finance, yfinance and chart libraries are external interfaces; ticker histories and generated /tmp chart files are runtime data.")
include(313, [feature(313, "conditions_or_retries", "scripts/market_quote.py", 51, 59, "Cache use depends on file existence and the timestamp being within the configured TTL."), feature(313, "persistence_or_cross_session", "scripts/market_quote.py", 65, 68, "Fetched quote payloads receive a cache timestamp and are serialized into local cache files for later calls.")], "All three referenced market scripts, requirements and provider notes are retained. Watchlists/cache files are created at runtime; paid provider additions are optional and external provider behavior remains unknown.")
exclude(314, "The package claims its own Python core modules, and the bundled adapter imports core.skill_schema, core.storage and core.skill_engine, but no core directory or those implementations is present. The absent own core cannot be treated as merely an opaque external service.", [evidence(314, "mcporter_adapter.py", 12, 28), evidence(314, "SKILL.md", 31, 47)], [{"target": "<outside-package>", "classification": "illustrative_or_optional", "reason": "The outside-package MEMORY.md links are labeled research notes rather than required implementation source."}, {"target": "MCP_CONFIG.md", "classification": "missing_required_source", "reason": "The package architecture names this own MCP configuration document, which is absent along with its explicitly required Python core; missing own implementation is the decisive exclusion."}])
include(315, [feature(315, "conditions_or_retries", "SKILL.md", 70, 76, "Consent, rate-limit challenge or human-takeover conditions select a stop and user handoff in the supported device automation mode."), feature(315, "versions_or_transformations", "SKILL.md", 63, 67, "The device-signup mode decodes screenshot representations and uses extracted verification codes as later device input; these remain conditional operations, not universal media-generation behavior.")], "The Wonda CLI is explicitly an external npm/Homebrew dependency and its contract is documented inline. Device/media/social state is runtime data. The recapture path mentioned for maintaining X internals belongs to external CLI/companion tooling, not a claimed missing bundled script.")
include(317, [feature(317, "conditions_or_retries", "SKILL.md", 10, 16, "Missing user context triggers context-gathering questions before content production."), feature(317, "versions_or_transformations", "SKILL.md", 421, 428, "The declared batching mode turns reviewed content topics into platform-specific posts, threads, carousel/reel ideas and a publishing schedule.")], "The published skill is a self-contained strategy prompt. Source content, audience metrics and scheduling-platform access are runtime inputs or external interfaces; the source does not claim a bundled scheduler implementation.")
include(319, [feature(319, "persistence_or_cross_session", "SKILL.md", 106, 112, "Remember/forget operations classify content into persistent stores and retain an audit entry or soft archive."), feature(319, "conditions_or_retries", "SKILL.md", 119, 130, "Computed relevance ranges select searchable, deprioritized, explicit-search-only or archived memory behavior.")], "The initializer, memory templates and named architecture/routing/reflection documents are retained. MEMORY.md, episodes, graph entities and audit files are specified runtime-created workspace state; the memory provider is an external interface.")


def save(filename):
    for identity, decision in DECISIONS.items():
        row = next(row for row in ROWS.values() if row["canonical_id"] == identity)
        texts = {}
        for path in (C / row["source_dir"]).rglob("*"):
            if path.is_file():
                try:
                    texts[path.relative_to(C / row["source_dir"]).as_posix()] = path.read_text(encoding="utf-8-sig")
                except UnicodeDecodeError:
                    pass
        for item in decision["features"]:
            validate_evidence(texts, item["evidence"])
        if decision["decision"] == "exclude":
            validate_evidence(texts, decision["exclusion_evidence"])
        required = {item["target"] for item in row.get("unresolved_local_reference_nominations", [])}
        resolved = {item["target"] for item in decision["source_closure"]["local_reference_decisions"]}
        assert required <= resolved, (identity, required - resolved)
    output = C / "selection/review-batches" / filename
    raw = (json.dumps({"schema": SCHEMA, "decisions": DECISIONS}, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if output.exists():
        assert output.read_bytes() == raw, "Existing source-review batch differs."
    else:
        output.write_bytes(raw)
    print(len(DECISIONS), "source-only decisions validated and saved.")


if __name__ == "__main__":
    save("acq_screen_0301_0400_0001.json")
