"""Assistant-authored demand candidates for pinned, offline examples.

This file is an authoring recipe for three frozen cases, not an extraction
heuristic, production semantics, independent review, or a ground-truth label.
"""
from __future__ import annotations

from copy import deepcopy
from skillflow.propagation.contracts.references import target_key

from skillflow.common.source_evidence import json_pointer
from skillflow.doe.demand_index import build_demand_target_index

from .task_examples import BASELINE, INPUT_SHA256


TASK_BASELINE = "experiments/doe/runs/task-evidence-v1-20261010-213606/cases"
EXPECTED_COUNTS = {"001": (7, 6), "010": (8, 12), "013": (9, 16)}


def authored_demand_candidate(case: str, cfg: dict, raw_annotation: dict, task: dict) -> dict:
    """Bind intentionally authored goals to exact current targets.

    The caller verifies frozen identities. Explicit case-specific positions here
    are experiment input, never rules inferred from opcodes or field names.
    """
    if case not in EXPECTED_COUNTS:
        raise ValueError("demand example must be one of 001, 010, 013")
    targets = build_demand_target_index(cfg, raw_annotation)
    requirements = {r["id"]: r for r in task["requirements"]}
    if len(requirements) != EXPECTED_COUNTS[case][0]:
        raise ValueError("pinned task requirement count differs")
    ir_pointers = {ir["id"]: json_pointer("blocks", block_id, "instructions", position)
                   for block_id, block in cfg["blocks"].items()
                   for position, ir in enumerate(block["instructions"])}
    goals, expressions = [], []

    def target(**attributes):
        matches = [key for key, value in targets.items()
                   if all(value.get(k) == v for k, v in attributes.items())]
        if len(matches) != 1:
            raise ValueError(f"pinned demand target is missing or ambiguous: {attributes}")
        return matches[0]

    def graph(ir_id, suffix=""):
        return target(pointer=ir_pointers[ir_id] + suffix)

    def operation(ir_id, path, op):
        value = target(instruction_id=ir_id, raw_path=raw_path(path), kind="operation")
        if targets[value]["value"]["op"] != op:
            raise ValueError("pinned operation type differs")
        return value

    def use(ir_id, path, slot):
        return target(instruction_id=ir_id, operation_raw_path=raw_path(path), kind="input_use", slot=slot)

    def raw_path(path):
        # These are the literal authoring positions above, not parsed data IDs.
        return [int(part) if part.isdigit() else part for part in path.lstrip("/").split("/")]

    def goal(requirement, target_id, property, reason, *, path=(), expected=None, expected_path=()):
        if requirement not in requirements:
            raise ValueError("pinned task requirement is missing")
        goals.append({"id": f"G{len(goals) + 1:03d}", "requirement_id": requirement,
                      "target": targets[target_id]["target"], "preserve": property, "path": list(path),
                      "expected": expected, "expected_path": list(expected_path), "reason": reason})

    def constraint(requirement, reason, property="constraint"):
        # Retained restrictions have no positive seed in v3. The corresponding
        # realization records the gap explicitly instead of claiming binding.
        pass

    def supplement(requirement, target_id, expression):
        expressions.append({"target": targets[target_id]["target"], "expression": expression,
                            "evidences": deepcopy(requirements[requirement]["evidences"])})

    def input_ref(index):
        return {"kind": "input", "index": index}

    def ref(index):
        return {"op": "ref", "value": input_ref(index)}

    def field(name):
        return {"op": "field", "arg": ref(0), "path": [name]}

    def literal(value):
        return {"op": "literal", "value": value}

    top = "/events/0/events/0/atomic_ops/0"
    if case == "001":
        constraint("R001", "Keep the stated file origin; this does not demand every file field at each receiver.")
        predicate = {"op": "and", "args": [
            {"op": "ne", "left": field("opted_out"), "right": literal(True)},
            {"op": "or", "args": [
                {"op": "eq", "left": field("urgent"), "right": literal(True)},
                {"op": "ge", "left": field("value"), "right": literal(100)}]}]}
        supplement("R002", operation("ir_003", top, "filter_items"), predicate)
        goal("R002", graph("ir_003", "/outputs/0"), "shape",
             "Preserve which members satisfy the subscription and urgency/value condition; member content is demanded separately.")
        constraint("R003", "Preserve once-per-selected-element scope and the exclusion of unselected members.")
        send = "/events/0/body/0/events/1/atomic_ops/0"
        goal("R003", operation("ir_005", send, "deliver"), "action",
             "Keep the required per-selected-record notification, without requiring all current payload fields.")
        for slot, name in enumerate(("recipient", "summary")):
            goal("R004", use("ir_005", send, slot), "value",
                 f"The argument must preserve this same element's {name} value, not the complete element.",
                 expected={"kind": "local", "name": "event_record"}, expected_path=[name])
        constraint("R005", "Retain the workflow-wide access_token prohibition without creating an input demand.", "prohibit")
        constraint("R006", "Preserve original-field retrieval rather than inventing summarization or conversion.")
        goal("R007", operation("ir_009", top, "write"), "action", "Keep the final count-file write.")
        goal("R007", use("ir_009", top, 0), "value", "Preserve the processed-count value passed to the file.", expected=input_ref(1))
        # No count supplement: the source says processed-record count, not a
        # guaranteed equality with selected collection size under call failures.
        constraint("R007", "Keep after-processing order. The current processed-count computation remains conservative; collection cardinality is not substituted.")
    elif case == "010":
        constraint("R001", "Keep the named request origin without turning the entire request into a required payload.")
        send = "/events/0/events/1/atomic_ops/0"
        goal("R002", operation("ir_007", send, "deliver"), "action", "Keep the one required search request.")
        goal("R002", use("ir_007", send, 0), "value", "The query member is the unchanged term value.",
             path=["query"], expected=input_ref(1))
        constraint("R002", "Preserve the existing single-call and original-query restriction.")
        for req, ir_id, name, input_index in (("R003", "ir_004", "from_date", 2), ("R004", "ir_005", "limit", 4)):
            goal(req, use("ir_007", send, 0), "value", f"When included, {name} is the original optional value.",
                 path=[name], expected=input_ref(input_index))
            goal(req, use("ir_007", send, 0), "presence", f"Preserve {name} inclusion versus omission; absence is not null substitution.", path=[name])
            supplement(req, operation(ir_id, "/events/0/events/0/atomic_ops/1", "compute"),
                       {"op": "present", "arg": field(name)})
        constraint("R005", "Keep the global delete prohibition without creating a required delete operation.", "prohibit")
        constraint("R006", "Keep the restriction against inferred fuzzy expansion, validation, and normalization.", "prohibit")
        goal("R007", operation("ir_010", top, "write"), "action", "Keep the explicitly required persistence of response.total.")
        goal("R007", use("ir_010", top, 0), "value", "Preserve only the specified saved total value.", expected=input_ref(1))
        goal("R008", graph("ir_012", "/inputs/0"), "value", "Ordinary return preserves this search response's items identity without a fabricated delivery event.")
    else:
        constraint("R001", "Keep distinct request and environment origins; do not demand whole-container exposure.")
        for req, ir_id in (("R002", "ir_007"), ("R003", "ir_011"), ("R005", "ir_015")):
            goal(req, operation(ir_id, top, "deliver"), "action", "Keep this task-prescribed call under its existing path conditions.")
            for slot, input_index in enumerate((1,) if ir_id == "ir_015" else (1, 2)):
                goal(req, use(ir_id, top, slot), "value", "Preserve this actual argument position and its specified original value.", expected=input_ref(input_index))
        for req in ("R002", "R003", "R004", "R005"):
            constraint(req, "Preserve credential/failure routing, bounded multiplicity, and parameter restrictions; the annotation's outcome computation remains conservative.")
        for req, returns in (("R006", ("ir_020", "ir_022", "ir_024")), ("R007", ("ir_026",))):
            for ir_id in returns:
                goal(req, graph(ir_id, "/inputs/0"), "value", "Preserve this terminal's distinct successful body or archive error; do not substitute another attempt's value.")
            constraint(req, "Keep the terminal stop/no-further-fetch requirement in addition to the returned value.")
        constraint("R008", "Keep the prohibited credential receivers as a restriction, not a positive credential payload demand.", "prohibit")
        for ir_id in ("ir_019", "ir_021", "ir_023", "ir_025"):
            goal("R009", operation(ir_id, top, "write"), "action", "Keep the required append on this terminal path.")
            goal("R009", use(ir_id, top, 0), "value", "Preserve this terminal's status value, not its full response or credential.", expected=input_ref(1))
        constraint("R009", "Preserve append-before-return on every terminal path; no new status format is inferred.")
    return {"goals": goals, "expressions": expressions}


ASSISTANT_REVIEWS = {
    "001": "The source predicate is made explicit as a supplement, and each notification argument is tied to the same selected element. The processed-count computation deliberately remains opaque: the source does not establish that successful processing count always equals selected collection size. Conservative demand from this computation may retain more record information than the precise notification and filter relations require. This is an analysis limitation, not evidence that every field is indispensable.",
    "010": "The request preserves query and optional values separately from their presence controls. Two evidenced presence expressions refine only the existing flag computations. Saved total and returned items retain their distinct response fields. The tool interface does not establish response equivalence under changed requests, so request retention can remain conservative. No request flag is made a tool-payload member.",
    "013": "The candidate retains credential routing, bounded retry/fallback, separate response identities, terminal state appends, and the named credential prohibition. Outcome classifiers remain opaque because the source does not specify a concrete response status interface. No success/error/status field schema is guessed from names. Environment demand can remain narrower than its observed whole, but response demands may be conservative; neither is a final sensitivity or DOE verdict.",
}
