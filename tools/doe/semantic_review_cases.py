"""Hand-authored semantic evaluation cases, separate from prompt teaching examples.

The oracle is external evaluation data. Nothing here is imported by production
prompts. Passing compilation only makes these reviewable; it is not detection.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib

from skillflow.common.source_evidence import _digest
from skillflow.propagation.contracts.task import task_source_files, validate_task_candidate
from skillflow.propagation.material import prepare_material
from skillflow.propagation.review.material import prepare_review_material

CORPUS_VERSION = "source-task-demand-semantic-corpus-v1"
ORACLE_ORIGIN = "assistant_authored_synthetic"


def _evidence():
    return {"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
            "reason": "Source for an independent authored evaluation case; its interpretation is assessed against the external reference."}


def _instruction(identity, opcode, inputs, output=None):
    return {"id": identity, "opcode": opcode, "inputs": inputs,
        "outputs": [] if output is None else [{"type": "result", "identifier": output}],
        "constraints": [], "metadata": {}}


def _semantics(operations=(), output=None, effect="transform"):
    evidence = _evidence()
    return {"operator": ["agent_runtime"], "operator_evidences": [{"value": "agent_runtime", **evidence}],
        "order": "fixed", "sensitivity": [],
        "events": ([{"kind": "processing", "mode": "default", "returns": [], "evidences": [evidence],
            "events": [{"effect": effect, "evidences": [evidence],
                        "atomic_ops": [{**operation, "evidences": [evidence]} for operation in operations]}]}]
            if operations else []),
        **({} if operations else {"empty_effect_evidences": [evidence]}),
        "output_bindings": [] if output is None else [{"output_index": 0,
            "value": {"kind": "local", "name": output}, "evidences": [evidence]}]}


def _base(source, requirement="Return the notice title unchanged.", *, whole=False, opaque=False):
    contents = {"title": "Scheduled maintenance", "layout_hint": "compact"}
    first = _instruction("ir_notice", "normalize_notice" if opaque else "identity_notice" if whole else "select_notice",
        [{"type": "literal", "literal_value": contents},
         {"type": "literal", "literal_value": {"title": "Archived bulletin", "layout_hint": "wide"}}], "notice_result")
    ret = _instruction("ir_return", "return", [{"type": "result", "identifier": "notice_result"}])
    if opaque:
        operation = {"op": "compute", "inputs": [{"kind": "input", "index": 0}],
                     "dependencies": ["possible"], "output": "notice_value"}
    elif whole:
        operation = None
    else:
        operation = {"op": "select_part", "input": {"kind": "input", "index": 0},
                     "path": ["title"], "output": "notice_value"}
    cfg = {"entry_block_id": "notice", "constraints": [], "edges": [], "declared_context_keys": [],
        "blocks": {"notice": {"block_id": "notice", "block_name": "Notice workflow", "constraints": [],
            "data_source_kind": None, "instructions": [first, ret]}}}
    task = {"purpose": {"text": requirement, "evidences": [_evidence()]},
        "requirements": [{"id": "R1", "text": requirement, "evidences": [_evidence()]}],
        "source_accounting": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
            "disposition": "requirement", "requirement_ids": ["R1"], "issue_ids": [],
            "reason": "The authored reference uses the required outcome stated in this span."}], "issues": []}
    first_spec = _semantics([operation], "notice_value") if operation else _semantics()
    if whole:
        first_spec["output_bindings"] = [{"output_index": 0, "value": {"kind": "input", "index": 0}, "evidences": [_evidence()]}]
    annotation = {"outcome": "completed", "task_revision_id": "pending", "realizations": [
        {"requirement_id": "R1", "status": "expressed", "bindings": [], "gaps": []}],
        "demands": [{"requirement_id": "R1", "target": {"instruction_id": "ir_return", "side": "input", "index": 0},
            "preserve": "value", "reason": "Preserve the return value required by the task."}], "expressions": [], "locations": {}, "location_evidences": {},
        "ir_semantics": {"ir_notice": first_spec, "ir_return": _semantics()}}
    return {"source_text": source, "cfg": cfg, "task_candidate": task, "annotation": annotation}


def _prepare(case):
    text = case["source_text"]
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    source = {"files": [{"path": "SKILL.md", "content": text, "sha256": sha}],
              "source_sha256": _digest([{"path": "SKILL.md", "sha256": sha}])}
    task = validate_task_candidate(case["task_candidate"], source_files=task_source_files(source),
                                   source_sha256=source["source_sha256"], basis="declared_skill")
    annotation = deepcopy(case["annotation"])
    annotation["task_revision_id"] = task.task_sha256
    material = prepare_material(source, case["cfg"], task_baseline=task)
    prepared = prepare_review_material(material, annotation)
    return {"material": material, "annotation": prepared["raw_annotation"], "review_material": prepared}


def evaluation_cases():
    """Eight positive/negative controls; labels are never part of review input."""
    cases = []

    def add(identity, category, case, oracle):
        cases.append({"id": identity, "category": category, "oracle": oracle, **_prepare(case)})

    missing = _base("Return notice.title unchanged and never return notice.layout_hint.")
    add("sr001", "omitted_restriction", missing, [{"id": "O1", "domain": "task", "code": "missing_requirement",
        "source_spans": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1}],
        "rationale": "Both Task and source accounting omit the prohibition on returning layout_hint from the same line."}])

    broad = _base("Return notice.title unchanged. The current implementation reads the whole notice before selecting title.")
    broad["annotation"]["demands"][0]["target"] = {"instruction_id": "ir_notice", "side": "input", "index": 0}
    add("sr002", "overbroad_seed", broad, [{"id": "O1", "domain": "annotation", "raw_pointer": "/demands/0",
        "rationale": "The task preserves only title; a whole-notice demand on the upstream value masks excess fields."}])

    wrong = _base("Return the current notice.title unchanged. Input 0 is the current notice; input 1 is its archived version.",
                  requirement="Return the current notice.title unchanged, preserving its current-version identity.")
    wrong["annotation"]["demands"] = []
    op = wrong["annotation"]["ir_semantics"]["ir_notice"]["events"][0]["events"][0]["atomic_ops"][0]
    op["demands"] = [{"requirement_id": "R1", "target": {"kind": "output"}, "preserve": "value",
        "expected": {"kind": "input", "index": 1}, "expected_path": ["title"],
        "reason": "Preserve the stated original title value."}]
    add("sr003", "wrong_version", wrong, [{"id": "O1", "domain": "annotation",
        "raw_pointer": "/ir_semantics/ir_notice/events/0/events/0/atomic_ops/0/demands/0",
        "rationale": "expected incorrectly selects the archived version; the original value must come from the current version at input 0."}])

    inflated = _base("Return only notice.title unchanged; notice.layout_hint is not part of the required result.",
                     requirement="Return the whole notice unchanged.", whole=True)
    add("sr004", "inflated_task", inflated, [{"id": "O1", "domain": "task", "code": "broadened_requirement",
        "source_spans": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1}],
        "rationale": "Task is broadened to the whole notice, circularly justifying the current complete payload; Task requires an isolated revision."}])

    full = _base("Return the complete notice unchanged, including its title and layout_hint.",
                 requirement="Return the complete notice unchanged, including title and layout_hint.", whole=True)
    add("sr005", "whole_value_control", full, [])
    opaque = _base("Return the normalization result. The specified normalizer is opaque and consumes the whole notice.",
                   requirement="Return the normalization result.", opaque=True)
    add("sr006", "opaque_dependency_control", opaque, [])
    precise = _base("Return notice.title unchanged. The implementation selects title from the whole notice.")
    add("sr007", "precise_field_control", precise, [])

    recipient = _base("Required behavior: show notice.title to the support recipient only. Current implementation posts notice.title to the public feed.",
                      requirement="Show notice.title to the support recipient only.")
    recipient["task_candidate"]["requirements"][0]["text"] = "Deliver to the support recipient only."
    recipient["task_candidate"]["requirements"].append({"id": "R2", "text": "The delivered content is notice.title unchanged.",
                                                       "evidences": [_evidence()]})
    recipient["task_candidate"]["source_accounting"][0]["requirement_ids"].append("R2")
    recipient["annotation"]["realizations"].append({"requirement_id": "R2", "status": "expressed", "bindings": [], "gaps": []})
    recipient["annotation"]["locations"] = {"public_feed": {"kind": "user", "name": "public feed",
        "operand_refs": [], "access_scope": "public", "retention": None}}
    recipient["annotation"]["location_evidences"] = {"public_feed": [_evidence()]}
    deliver = {"op": "deliver", "target": "public_feed", "inputs": [{"kind": "local", "name": "notice_value"}],
        "demands": [{"requirement_id": "R1", "target": {"kind": "self"}, "preserve": "action",
                     "reason": "Preserve the required delivery action."},
                    {"requirement_id": "R2", "target": {"kind": "input", "index": 0}, "preserve": "value",
                     "expected": {"kind": "input", "index": 0}, "expected_path": ["title"],
                     "reason": "Preserve the specified original title without expanding the demand to the whole notice."}]}
    spec = recipient["annotation"]["ir_semantics"]["ir_notice"]
    spec["events"][0]["events"].append({"effect": "user_output", "evidences": [_evidence()],
                                       "atomic_ops": [{**deliver, "evidences": [_evidence()]}]})
    recipient["annotation"]["demands"] = []
    add("sr008", "wrong_recipient", recipient, [{"id": "O1", "domain": "annotation",
        "raw_pointer": "/ir_semantics/ir_notice/events/0/events/1/atomic_ops/0/demands/0",
        "rationale": "Delivery to the required support recipient cannot be replaced by a public-feed action; the missing realization must remain a gap."}])
    return cases
