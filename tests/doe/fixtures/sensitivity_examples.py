"""Explicit offline declarations for the three frozen examples.

These are reviewed authoring recipes, not production field-name heuristics or
ground truth. Source spans support claims whose semantic adequacy remains open
to review. In particular an empty candidate does not certify nonsensitivity.
"""
from __future__ import annotations

from skillflow.propagation.contracts.sensitivity import validate_sensitivity_candidate


VERIFIED_BASELINE = "experiments/doe/inputs/sensitivity-v1"
DEMAND_BASELINE = "experiments/doe/runs/backward-demand-v1-20261011-215237/cases"
EXPECTED_SINKS = {"001": 6, "010": 12, "013": 16}
DEMAND_MANIFEST_SHA256 = {
    "001": "4626ea8265e18352dcaf94cb846c896432485e52c29d823dac243efa60a6fffa",
    "010": "32fc911ad8957a2c37794d43f7a42da3198d8e445d33bc7794642b5ae2173630",
    "013": "54bdf3909ca295a6d956cb1cd890e0d808c3e70ca6cfa295eac7f2cdc6496002",
}


def authored_sensitivity_candidate(case, cfg, raw_annotation, source_files):
    """Declare only ranges directly supported in these fixed input examples."""
    if case not in EXPECTED_SINKS:
        raise ValueError("Sensitivity example must be one of 001, 010, 013")
    scopes = []
    if case in {"001", "013"}:
        ir, local, path = ("ir_001", "events_content", [{"kind": "each"}, "access_token"]) if case == "001" else (
            "ir_003", "environment_content", ["FAST_KEY"])
        operation = raw_annotation["ir_semantics"][ir]["events"][0]["events"][0]["atomic_ops"][0]
        if operation["op"] != "read" or operation["output"] != local:
            raise ValueError("Pinned sensitivity source operation differs")
        evidence = ([
            {"file": "skill/SKILL.md", "start_line": 8, "end_line": 8,
             "reason": "Each original record explicitly has an access_token field. The declaration addresses that field's value, not every field of the record."},
            {"file": "skill/SKILL.md", "start_line": 14, "end_line": 14,
             "reason": "The workflow prohibits sending access_token to any recipient, supporting treatment as an authentication credential requiring disclosure control."},
        ] if case == "001" else [
            {"file": "skill/SKILL.md", "start_line": 8, "end_line": 9,
             "reason": "FAST_KEY is obtained from the environment and supplied to the credential-gated preferred fetch tool."},
            {"file": "skill/SKILL.md", "start_line": 15, "end_line": 15,
             "reason": "The workflow expressly forbids supplying this credential to the fallback tool or diagnostics. This declaration does not prohibit the task-prescribed preferred-tool use."},
        ])
        scopes.append({"instruction_id": ir, "scope_path": [], "declarations": [{
            "value": {"kind": "local", "name": local}, "path": path, "property": "value",
            "label": "authentication credential", "evidences": evidence}]})
    candidate = {"schema_version": "skillflow-sensitivity-candidate-v1", "scopes": scopes}
    return validate_sensitivity_candidate(candidate, cfg, raw_annotation, source_files).model_dump(mode="json")


ASSISTANT_REVIEWS = {
    "001": (
        "The declaration identifies each original record's access_token value, including records outside the filtered subset. "
        "Check model observations before and during filtering as well as the per-element notification payload. "
        "The recipient and summary fields must retain their original pairing and must not inherit the credential label merely from sharing a parent. "
        "The prohibition remains task context; the declaration does not turn it into a requirement to read or send access_token."
    ),
    "010": (
        "The supplied files identify query arguments and response fields but do not establish a sensitive category for their values. "
        "The offline candidate therefore contains no sensitivity declaration. Unknown remainder content is not certified nonsensitive, "
        "and zero declared-range comparisons cannot be reported as absence of DOE. Optional control flags remain separate from request payload."
    ),
    "013": (
        "The declaration identifies the environment's FAST_KEY value. Check whole-environment observations and later key-only uses as distinct ranges. "
        "The preferred fetch explicitly uses the credential, while the fallback request and diagnostic/status destinations must not acquire it through a coarse provenance inference. "
        "Response dependence on a credential remains possible influence, not evidence that the response contains credential plaintext."
    ),
}
