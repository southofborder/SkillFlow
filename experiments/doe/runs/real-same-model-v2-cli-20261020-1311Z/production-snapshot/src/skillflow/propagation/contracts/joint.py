"""Normalize one joint semantic response into task and demand contracts.

Only pre-existing CFG targets are supplied to the model. Response-local goals
and expressions are resolved at their enclosing operation after strict parsing.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pydantic import ValidationError

from skillflow.common.source_evidence import extract_source_lines
from skillflow.common.recording import canonical_sha256
from skillflow.common.source_evidence import json_pointer, resolve_pointer
from skillflow.common.validation import StructuralValidationError, structural_error, validation_at, schema_error
from skillflow.propagation.contracts.task import (
    Task, task_source_files, checked_task, task_reference,
)
from skillflow.propagation.contracts.realizations import validate_realizations
from skillflow.propagation.contracts.demand import CandidateDemand, validate_demand_candidate
from skillflow.propagation.contracts.demand_index import build_demand_target_index, target_id_for, operation_target
from skillflow.propagation.contracts.references import target_key
from skillflow.propagation.contracts.sensitivity import (
    extract_sensitivity_candidate, validate_sensitivity_candidate,
)
from skillflow.propagation.contracts.constraints import validate_constraints


def joint_source_files(material):
    return task_source_files(material["source"], user_request=material["user_request"])


def _task(material):
    return checked_task(material["task"], source_files=joint_source_files(material),
                        source_sha256=material["source"]["source_sha256"])


def _raw_diagnostic(diagnostic, raw, goal_paths, expression_paths):
    """Project a normalized validator location without changing its audit."""
    row = deepcopy(diagnostic)
    parts = row["path"].split("/")
    if len(parts) >= 3 and parts[1] in {"goals", "expressions"} and parts[2].isdigit():
        paths = goal_paths if parts[1] == "goals" else expression_paths
        row["path"] = paths[int(parts[2])] + ("/" + "/".join(parts[3:]) if parts[3:] else "")
    elif row["path"] == "/goals":
        row["path"] = "/demands"
    context = row.get("context", {})
    if "present" in context:
        for key in ("current", "current_type", "current_length", "current_keys"):
            context.pop(key, None)
        if context["present"]:
            current = resolve_pointer(raw, row["path"])
            if len(json.dumps(current, ensure_ascii=False, allow_nan=False)) <= 800:
                context["current"] = deepcopy(current)
            else:
                context["current_type"] = type(current).__name__
                if isinstance(current, (dict, list, str)):
                    context["current_length"] = len(current)
                if isinstance(current, dict):
                    context["current_keys"] = list(current)
    return row


def normalize_joint_semantics(raw, material):
    """Normalize Task, demands and expressions without a second model call."""
    if hasattr(raw, "model_dump"):
        raw = raw.model_dump(mode="json")
    task = _task(material)
    if raw["task_revision_id"] != task.task_sha256:
        raise structural_error("task_revision", "/task_revision_id", "The annotation must use the exact supplied Task revision.")
    targets = build_demand_target_index(material["cfg"], raw)
    goals = [{**deepcopy(goal), "id": "goal_" + canonical_sha256([task.task_sha256, "demands", index])[:20]}
             for index, goal in enumerate(raw["demands"])]
    expressions = deepcopy(raw["expressions"])
    goal_paths = [f"/demands/{index}" for index in range(len(goals))]
    expression_paths = [f"/expressions/{index}" for index in range(len(expressions))]
    reference_errors, invalid_seed_requirements = [], set()
    for item, item_path in [*zip(goals, goal_paths), *zip(expressions, expression_paths)]:
        if target_key(item["target"]) not in targets or targets[target_key(item["target"])]["domain"] != "cfg":
            if "requirement_id" in item:
                invalid_seed_requirements.add(item["requirement_id"])
            reference_errors.extend(structural_error("target_domain", item_path + "/target",
                                   "top-level targets must resolve directly to the pre-existing CFG",
                                   current=item["target"]).diagnostics)

    for target_id, target in targets.items():
        if target.get("domain") != "transfer" or target["kind"] != "operation":
            continue
        operation = target["value"]
        ir_id, path = target["instruction_id"], target["raw_path"]
        coordinate_hint = (
            'Syntax fragments: operation.demands[].target={"kind":"input","index":0} '
            'selects the first parameter use of that atomic operation; a ValueRef '
            '{"kind":"input","index":0} selects the first actual input of the enclosing IR. '
            'The equal numbers do not imply equal values. Use this operation\'s allowed_input_indexes. '
            'target={"kind":"self"} with preserve="action" concerns the operation itself, not its payload.')
        for goal_index, goal in enumerate(operation.get("demands", [])):
            goal_path = json_pointer("ir_semantics", ir_id, *path, "demands", goal_index)
            choice = goal["target"]
            position = path
            if choice["kind"] == "input":
                position = [*path, "uses", choice["index"]]
            elif choice["kind"] == "output":
                position = [*path, "output"]
            identity = target_id_for(ir_id, position)
            if identity not in targets:
                invalid_seed_requirements.add(goal["requirement_id"])
                slots = sorted(item["slot"] for item in targets.values()
                    if item.get("kind") == "input_use" and item.get("instruction_id") == ir_id
                    and item.get("operation_raw_path") == path)
                reference_errors.extend(structural_error("operation_goal_slot", goal_path + "/target",
                                       "operation task goal references an absent input or output",
                                       current=choice, allowed_input_indexes=slots,
                                       has_output="output" in operation,
                                       **({"format_example": coordinate_hint} if not any(
                                           row["code"] in {"operation_goal_slot", "operation_goal_value"}
                                           for row in reference_errors) else {})).diagnostics)
                continue
            if choice["kind"] == "self" and goal["preserve"] != "action" and "output" not in operation:
                invalid_seed_requirements.add(goal["requirement_id"])
                reference_errors.extend(structural_error("operation_goal_value", goal_path + "/target",
                                       "a value goal requires a real operation output or input",
                                       current=choice, preserve=goal["preserve"],
                                       allowed="self for action; input(index) for an actual parameter value",
                                       **({"format_example": coordinate_hint} if not any(
                                           row["code"] in {"operation_goal_slot", "operation_goal_value"}
                                           for row in reference_errors) else {})).diagnostics)
                continue
            goals.append({key: value for key, value in goal.items() if key != "target"} | {
                "target": operation_target(ir_id, position),
                "id": "goal_" + canonical_sha256([task.task_sha256, "ir_semantics", ir_id, *path, "demands", goal_index])[:20],
            })
            goal_paths.append(goal_path)
        if operation.get("expression") is not None:
            expressions.append({"target": operation_target(ir_id, path), **operation["expression"]})
            expression_paths.append(json_pointer("ir_semantics", ir_id, *path, "expression"))

    # Invalid target identities do not justify cascading capability or seed
    # errors. Other targets, source spans and realization rows remain checkable.
    usable_goals = [(goal, path) for goal, path in zip(goals, goal_paths)
                    if target_key(goal["target"]) in targets]
    usable_expressions = [(expression, path) for expression, path in zip(expressions, expression_paths)
                          if target_key(expression["target"]) in targets]
    goals, goal_paths = [item[0] for item in usable_goals], [item[1] for item in usable_goals]
    expressions, expression_paths = ([item[0] for item in usable_expressions],
                                      [item[1] for item in usable_expressions])
    normalized_candidate = {"goals": goals, "expressions": expressions}
    try:
        candidate = CandidateDemand.model_validate(normalized_candidate)
    except ValidationError as error:
        # Duplicate supplements and other normalized grammar constraints are
        # prerequisites; do not misclassify them as implementation failures.
        normalized_error = schema_error(error, candidate=normalized_candidate,
                                        schema=CandidateDemand.model_json_schema())
        raise StructuralValidationError([
            _raw_diagnostic(row, raw, goal_paths, expression_paths)
            for row in normalized_error.diagnostics]) from error
    diagnostics = reference_errors
    try:
        validate_demand_candidate(candidate, task,
            joint_source_files(material), targets)
    except StructuralValidationError as error:
        for diagnostic in error.diagnostics:
            path = diagnostic["path"].split("/")
            if len(path) >= 3 and path[1] in {"goals", "expressions"} and path[2].isdigit():
                paths = goal_paths if path[1] == "goals" else expression_paths
                mapped = paths[int(path[2])] + ("/" + "/".join(path[3:]) if path[3:] else "")
                if path[1] == "goals":
                    invalid_seed_requirements.add(goals[int(path[2])]["requirement_id"])
            else:
                mapped = diagnostic["path"].replace("/goals", "/demands", 1).replace("/expressions", "/expressions", 1)
            diagnostics.append({**diagnostic, "path": mapped})
    try:
        validate_sensitivity_candidate(extract_sensitivity_candidate(raw), material["cfg"], raw,
                                       joint_source_files(material))
    except StructuralValidationError as error:
        diagnostics.extend(error.diagnostics)
    try:
        realizations = validate_realizations(raw["realizations"], task=task, cfg=material["cfg"],
            source_files=joint_source_files(material), goals=candidate.goals,
            invalid_seed_requirements=invalid_seed_requirements)
    except StructuralValidationError as error:
        diagnostics.extend(error.diagnostics)
    else:
        from skillflow.propagation.contracts.realizations import TaskRealization
        try:
            validate_constraints([TaskRealization.model_validate(row) for row in realizations],
                cfg=material["cfg"], raw=raw, targets=targets,
                expressions=candidate.expressions, locations=raw["locations"])
        except StructuralValidationError as error:
            diagnostics.extend(error.diagnostics)
    if diagnostics:
        raise StructuralValidationError(diagnostics)
    return {"task_ref": task_reference(task), "realizations": realizations,
            "demands": [v.model_dump(mode="json") for v in candidate.goals],
            "expressions": [v.model_dump(mode="json") for v in candidate.expressions]}


def validate_compiled_joint_semantics(compiled, material):
    """Check stored normalized structure; recompilation verifies raw provenance."""
    task = _task(material)
    if compiled["task_ref"] != task_reference(task):
        raise ValueError("compiled task reference differs from the frozen Task revision")
    demand = CandidateDemand.model_validate({"goals": compiled["demands"], "expressions": compiled["expressions"]})
    known = {item.id for item in task.requirements}
    if any(goal.requirement_id not in known for goal in demand.goals):
        raise ValueError("compiled task goal references an absent requirement")
    files = joint_source_files(material)
    for supplement in demand.expressions:
        for evidence in supplement.evidences:
            if evidence.file not in files:
                raise ValueError("demand expression evidence must cite task or Skill source")
            extract_source_lines(files[evidence.file], evidence.start_line, evidence.end_line)
    validate_sensitivity_candidate(extract_sensitivity_candidate(compiled), material["cfg"], compiled,
                                   joint_source_files(material))
    realizations = validate_realizations(compiled["realizations"], task=task, cfg=material["cfg"],
                                         source_files=files, goals=demand.goals)
    return {"task_ref": task_reference(task), "realizations": realizations,
            "demands": [v.model_dump(mode="json") for v in demand.goals],
            "expressions": [v.model_dump(mode="json") for v in demand.expressions]}


def goal_mapping(raw, normalized):
    """Program-owned raw coordinates; models never predict compiled goal IDs."""
    paths = [json_pointer("demands", i) for i in range(len(raw["demands"]))]
    # Normalization enumerates raw operations in this exact indexed order.
    # Reuse the declarations' canonical target coordinate to recover its wrapper.
    for goal in normalized["demands"][len(paths):]:
        target = goal["target"]
        base = target["operation_path"]
        operation = raw["ir_semantics"][target["instruction_id"]]
        for part in base:
            operation = operation[part]
        matches = [index for index in range(len(operation["demands"]))
                   if "goal_" + canonical_sha256([normalized["task_ref"]["task_sha256"], "ir_semantics",
                       target["instruction_id"], *base, "demands", index])[:20] == goal["id"]]
        if len(matches) != 1:
            raise ValueError("Compiled goal has no unique original declaration")
        paths.append(json_pointer("ir_semantics", target["instruction_id"], *base, "demands", matches[0]))
    return [{"raw_pointer": pointer, "goal_id": goal["id"], "requirement_id": goal["requirement_id"],
             "target": deepcopy(goal["target"])} for pointer, goal in zip(paths, normalized["demands"])]
