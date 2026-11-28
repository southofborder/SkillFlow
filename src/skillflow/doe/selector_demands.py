"""Bind control information to an evidenced test of a specific immutable operand."""
from __future__ import annotations

from skillflow.common.recording import canonical_sha256


ROOT_RULES = {"typed_case_selector", "typed_control_operand", "declared_unavailable_selector", "outcome_dispatch_selector"}
COPY_RULES = {"actual_operand", "cfg_result_use", "incoming_value", "public_result",
              "protected_outcome_value",
              "public_return_boundary", "processing_boundary", "selected_path", "remaining_content",
              "unchanged_content", "updated_value", "constructed_member", "same_element",
              "context_reaching_write", "saved_read", "map_yield", "expression_reference",
              "declared_unavailable_operand"}


def reference(ir, operand, guard):
    selector = {key: guard[key] for key in ("path", "tests", "outcome")}
    return "selector_" + canonical_sha256([ir, operand, selector])


def control_property(guard):
    tested = guard["tests"][:guard["outcome"] + 1]
    return "presence" if all(test["kind"] == "missing" for test in tested) else "truth"


def shifts_tested_index(removed, tested):
    """Deleting an earlier array element may readdress this tested subject."""
    if not removed or len(removed) > len(tested):
        return False
    offset = len(removed) - 1
    return (type(removed[offset]) is int and type(tested[offset]) is int
            and removed[offset] < tested[offset] and removed[:offset] == tested[:offset])


def sources(engine):
    """Index compiled declarations and actual origins, including cases without a produced event."""
    result = {}

    def add(ir, operand, guard, nodes, evidences):
        key = reference(ir, operand, guard)
        entry = result.setdefault(key, {"guard": guard, "nodes": set(), "evidences": [],
                                       "instruction_id": ir})
        entry["nodes"].update(n for n in nodes if n)
        for item in evidences:
            if item not in entry["evidences"]:
                entry["evidences"].append(item)

    for ir, semantics in engine.compiled["ir_semantics"].items():
        for outer in semantics["events"]:
            for event in outer.get("body", [outer]):
                case = event.get("case") or {}
                guard = case.get("guard")
                if guard:
                    slot = guard["input_index"]
                    add(ir, {"kind": "input", "index": slot}, guard,
                        [engine.node_at("ir_input", ir, slot=slot)], case["guard_evidences"])
                for op in event.get("atomic_ops", []):
                    if op["op"] == "branch" and op.get("selector") and op["input"]["kind"] == "input":
                        slot = op["input"]["index"]
                        add(ir, op["input"], op["selector"],
                            [engine.node_at("ir_input", ir, slot=slot)], op["evidences"])
    for info in engine.ops.values():
        op = info["spec"]
        if op["op"] == "branch" and op.get("selector"):
            ir = info["position"]["instruction_id"]
            add(ir, op["input"], op["selector"], [engine.node_at("op_input", ir, info["key"], 0)], op["evidences"])
    return result


def validate_bindings(derivations, engine):
    """An ordinary truth demand cannot gain a selector by changing its saved label."""
    bound = {key: row for key, row in derivations.items() if row.get("selector_ref")}
    if not bound:
        return
    from .material import _id
    node_ids = {canonical_sha256(node): key for key, node in engine.nodes.items()}
    ready, children = set(), {}
    for key, row in bound.items():
        entry = engine.selector_sources.get(row["selector_ref"])
        if entry is None or row["property"] != control_property(entry["guard"]):
            raise ValueError("Demand selector reference differs from its compiled control test")
        meta = row["node"]
        node = node_ids.get(canonical_sha256(meta))
        wanted = {field: row[field] for field in ("property", "path", "each", "excluded_paths", "selector_ref")}
        if "outcome_data_ids" in row:
            wanted["outcome_data_ids"] = row["outcome_data_ids"]
        if node is None or key != _id("demand_", [node, wanted, row["requirement_id"], row["seed_goal_id"],
                                                   row["conservative"], row.get("information_bound", False)]):
            raise ValueError("Demand selector derivation identity differs from its subject or information range")
        if (ROOT_RULES.intersection(row["rules"]) and row["path"] == entry["guard"]["path"]
                and any(engine.nodes[node] == meta for node in entry["nodes"])):
            ready.add(key)
        if COPY_RULES.intersection(row["rules"]):
            for parent in row["parents"]:
                origin = bound.get(parent)
                if origin and origin["selector_ref"] == row["selector_ref"] and origin["seed_goal_id"] == row["seed_goal_id"]:
                    children.setdefault(parent, []).append(key)
    reached = set()
    while ready:
        key = ready.pop()
        if key not in reached:
            reached.add(key)
            ready.update(children.get(key, ()))
    if reached != bound.keys():
        raise ValueError("Demand selector proof has no matching compiled operand and exact transfer ancestry")


def reason(entry):
    guard = entry["guard"]
    tests = [test["kind"] + ("=" + repr(test["value"]) if test["kind"] == "equals" else "")
             for test in guard["tests"]]
    source = entry["evidences"][0]
    return (f"Retain the first-match decision {guard['outcome']} in {tests} on {guard['path']} "
            f"at {entry['instruction_id']} ({source['file']}, lines {source['start_line']}-{source['end_line']}).")
