"""Evidence-bound revision of processing records against stable CFG identities."""
from collections import defaultdict
from copy import deepcopy

from pydantic import ValidationError

from skillflow.common.recording import canonical_sha256
from skillflow.common.source_evidence import _json_object, json_pointer, resolve_pointer
from skillflow.common.validation import StructuralValidationError, schema_error, structural_error
from skillflow.propagation.contracts.references import cfg_instructions, resolve_cfg_target

from .processing_correction import gap_positions, merge_slots


IDENTITY = "skillflow-processing-revision-scope-v1"
SENSITIVITY_IDENTITY = "skillflow-sensitivity-revision-scope-v1"
CORRESPONDENCE_IDENTITY = "skillflow-correspondence-revision-scope-v1"


def _block_members(cfg):
    return {ir["id"]: block_id for block_id, block in cfg["blocks"].items()
            for ir in block["instructions"]}


def _neighborhoods(cfg):
    incoming, outgoing = defaultdict(list), defaultdict(list)
    for edge in cfg["edges"]:
        incoming[edge["target_block_id"]].append(edge)
        outgoing[edge["source_block_id"]].append(edge)
    return {block_id: (incoming[block_id], outgoing[block_id], block["data_source_kind"],
                       block.get("constraints", [])) for block_id, block in cfg["blocks"].items()}


def _data_consumers(*graphs):
    consumers = defaultdict(set)
    for graph in graphs:
        instructions = cfg_instructions(graph)
        producer = {operand["identifier"]: ir for ir, row in instructions.items()
                    for operand in row["outputs"] if operand["type"] == "result"}
        for consumer, row in instructions.items():
            for operand in row["inputs"]:
                if operand["type"] == "result" and operand["identifier"] in producer:
                    consumers[producer[operand["identifier"]]].add(consumer)
    return consumers


def _downstream(edges, seeds):
    reached, pending = set(seeds), list(seeds)
    while pending:
        following = set(edges.get(pending.pop(), ())) - reached
        reached.update(following)
        pending.extend(following)
    return reached


def _changed_instructions(old_cfg, new_cfg):
    old, new = cfg_instructions(old_cfg), cfg_instructions(new_cfg)
    old_members, new_members = _block_members(old_cfg), _block_members(new_cfg)
    old_edges, new_edges = _neighborhoods(old_cfg), _neighborhoods(new_cfg)
    changed = {ir for ir in old.keys() | new.keys() if old.get(ir) != new.get(ir)
               or old_members.get(ir) != new_members.get(ir)}
    changed.update(ir for ir, block in new_members.items() if old_edges.get(block) != new_edges[block])
    for block in old_cfg["blocks"].keys() & new_cfg["blocks"].keys():
        before = [item["id"] for item in old_cfg["blocks"][block]["instructions"] if new_members.get(item["id"]) == block]
        after = [item["id"] for item in new_cfg["blocks"][block]["instructions"] if old_members.get(item["id"]) == block]
        if before != after:
            changed.update(left for left, right in zip(before, after) if left != right)
    return changed


def _anchored_owner(target, fragment):
    for prefix in ("annotation:", "fragment:processing:"):
        if target.startswith(prefix):
            pointer = target[len(prefix):]
            break
    else:
        return None
    tokens = pointer.split("/")
    if len(tokens) < 3 or tokens[1] not in {"ir_semantics", "processing_gaps"}:
        return None
    owner = "/".join(tokens[:3])
    try:
        record = resolve_pointer(fragment, owner)
    except ValueError:
        return None
    if tokens[1] == "processing_gaps":
        return record["instruction_id"]
    return tokens[2].replace("~1", "/").replace("~0", "~")


def _same_target(cfg_before, cfg_after, target):
    try:
        before = resolve_cfg_target(target, cfg_before)
        after = resolve_cfg_target(target, cfg_after)
    except (ValidationError, ValueError):
        return False
    return before["kind"] == after["kind"] and before["value"] == after["value"]


def _cfg_evidence(value):
    if isinstance(value, dict):
        if value.get("kind") == "literal" or value.get("op") == "literal":
            return
        for key, child in value.items():
            if key == "evidences":
                yield from (row["target"] for row in child if isinstance(row, dict) and "target" in row)
            else:
                yield from _cfg_evidence(child)
    elif isinstance(value, list):
        for child in value:
            yield from _cfg_evidence(child)


def processing_scope(old_cfg, new_cfg, findings, prior_processing, validation_gaps=()):
    """Compute edit permissions using executable references and checked finding anchors.

    Shared locations and standalone expression declarations are held immutable.
    A revision cannot reuse a changed address or expression relationship by
    pretending it was an IR-local edit. The caller retains its earlier bundle
    if no coherent new processing material can be proved.
    """
    old, new = cfg_instructions(old_cfg), cfg_instructions(new_cfg)
    changed = _changed_instructions(old_cfg, new_cfg)
    records, gaps = prior_processing["ir_semantics"], prior_processing.get("processing_gaps", [])
    for location in prior_processing.get("locations", {}).values():
        if any(not _same_target(old_cfg, new_cfg, target) for target in [*location.get("operand_refs", []), *_cfg_evidence(location)]):
            return None
    for expression in prior_processing.get("expressions", []):
        if (expression["target"].get("instruction_id") in changed
                or any(not _same_target(old_cfg, new_cfg, target) for target in [expression["target"], *_cfg_evidence(expression)])):
            return None
    changed.update(ir for ir, record in records.items()
                   if any(not _same_target(old_cfg, new_cfg, target) for target in _cfg_evidence(record)))
    affected = _downstream(_data_consumers(old_cfg, new_cfg), changed)
    located, source_rechecks, unresolved = defaultdict(list), defaultdict(list), []
    for finding in findings:
        if finding.get("domain", "annotation") != "annotation" or finding.get("owner", "processing") != "processing":
            continue
        for target in finding["target_ids"]:
            owner = _anchored_owner(target, prior_processing)
            if owner in new:
                located[owner].append(target)
                source_rechecks[owner].append({"target_id": target, "source_refs": deepcopy(finding.get("source_refs", []))})
            else:
                unresolved.append(target)
    previous_gaps = gap_positions(prior_processing)
    slots = {}
    for ir in sorted((affected | located.keys()) & new.keys()):
        slots[ir] = {"instruction": deepcopy(new[ir]), "changed_cfg": ir in changed,
            "finding_targets": sorted(set(located[ir])), "modeled": deepcopy(records.get(ir)),
            "source_rechecks": source_rechecks[ir], "allow_keep": ir not in changed and ir in old,
            "unmodeled_gaps": {json_pointer("processing_gaps", index): deepcopy(gaps[index])
                               for index in previous_gaps[ir]}}
    plan = {"identity": IDENTITY, "candidate_sha256": canonical_sha256(prior_processing),
        "old_cfg_sha256": canonical_sha256(old_cfg), "new_cfg_sha256": canonical_sha256(new_cfg),
        "findings_sha256": canonical_sha256(findings), "slots": slots,
        "removed_instruction_ids": sorted(old.keys() - new.keys()),
        "retained_validation_gaps": [deepcopy(gap) for gap in validation_gaps
            if gap["instruction_id"] in new and gap["instruction_id"] not in slots],
        "unresolved_targets": sorted(set(unresolved))}
    return {**plan, "scope_sha256": canonical_sha256(plan)}


def merge_processing_revision(previous, scope, response):
    """Merge exact processing IR updates for a checked semantic revision plan."""
    from .annotation_wire import FlatProcessingGap
    from .fragment_wire import expand_processing_response

    body = {key: value for key, value in scope.items() if key != "scope_sha256"}
    if (scope.get("identity") != IDENTITY or scope.get("scope_sha256") != canonical_sha256(body)
            or scope.get("candidate_sha256") != canonical_sha256(previous)):
        raise ValueError("Processing revision scope does not bind the exact prior fragment")
    try:
        response = expand_processing_response(response)
    except (TypeError, ValueError) as error:
        raise structural_error("processing_revision_json", "", str(error)) from error
    if set(response) != {"coverage_slots"} or not isinstance(response["coverage_slots"], list):
        raise structural_error("processing_revision_envelope", "", "Return the authorized coverage_slots array only.")

    def validate_gap(value, pointer):
        try:
            FlatProcessingGap.model_validate(value)
        except ValidationError as error:
            raise schema_error(error, pointer, candidate=value, schema=FlatProcessingGap.model_json_schema()) from error

    for index, row in enumerate(response["coverage_slots"]):
        if isinstance(row, dict) and "keep" in row and isinstance(row.get("instruction_id"), str):
            slot = scope["slots"].get(row["instruction_id"])
            if slot is not None and not slot["allow_keep"]:
                raise structural_error("processing_revision_keep", json_pointer("coverage_slots", index, "keep"),
                    "A changed CFG slot needs an explicit processing record or source-backed unmodeled gap.")
    merged = merge_slots(previous, response, {"candidate_sha256": scope["candidate_sha256"],
        "records": {}, "coverage_slots": scope["slots"], "field_slots": {}}, validate_gap=validate_gap)
    seen = {row["instruction_id"] for row in response["coverage_slots"]}
    missing = scope["slots"].keys() - seen
    if missing:
        raise StructuralValidationError([{"code": "processing_revision_missing", "path": json_pointer("ir_semantics", ir),
            "message": "The revision did not fill this requested processing slot.",
            "context": {"instruction_id": ir}} for ir in sorted(missing)])
    retired = set(scope["removed_instruction_ids"])
    for ir in retired:
        merged["ir_semantics"].pop(ir, None)
    if "processing_gaps" in merged:
        merged["processing_gaps"] = [gap for gap in merged["processing_gaps"] if gap["instruction_id"] not in retired]
    return merged


def _operations(value):
    """Read only the flat operation trees of one already validated IR."""
    if isinstance(value, list):
        for item in value:
            yield from _operations(item)
    elif isinstance(value, dict):
        if "op" in value:
            yield value
            return
        for name in ("segments", "body", "ops", "cases"):
            if name in value:
                yield from _operations(value[name])


def _location_uses(processing, cfg):
    """Return the actual modeled location dependencies and state read/write roles."""
    locations = processing.get("locations", {})
    uses, reads, writes = defaultdict(set), defaultdict(list), defaultdict(list)
    for ir, spec in processing["ir_semantics"].items():
        for op in _operations(spec):
            ref = op.get("location", op.get("target"))
            if not isinstance(ref, str) or ref not in locations:
                continue
            uses[ir].add(ref)
            if op["op"] == "read":
                reads[ir].append(locations[ref])
            if op["op"] == "write":
                writes[ir].append(locations[ref])
    for ir, instruction in cfg_instructions(cfg).items():
        reads[ir].extend({"kind": "runtime_context", "name": op["identifier"], "address_kind": "identified"}
                         for op in instruction["inputs"] if op["type"] == "context_key")
    return uses, reads, writes


def _sensitivity_owner(target, prior):
    if target.startswith("fragment:sensitivity:/declarations/"):
        pointer = target.removeprefix("fragment:sensitivity:")
        try:
            return resolve_pointer(prior, "/".join(pointer.split("/")[:3]))["instruction_id"]
        except (KeyError, TypeError, ValueError):
            return None
    if target.startswith("annotation:/ir_semantics/"):
        tokens = target.split("/")
        if "sensitivity" in tokens[3:]:
            return tokens[2].replace("~1", "/").replace("~0", "~")
    return None


def sensitivity_scope(old_cfg, new_cfg, old_processing, new_processing, findings, prior_sensitivity):
    """Authorize only changed lexical/data dependencies and directly reviewed declarations."""
    from skillflow.propagation.contracts.limitations import instruction_successors
    from skillflow.propagation.contracts.locations import locations_may_alias

    old_specs, new_specs = old_processing["ir_semantics"], new_processing["ir_semantics"]
    old_locations, new_locations = old_processing.get("locations", {}), new_processing.get("locations", {})
    changed_locations = {name for name in old_locations.keys() | new_locations.keys()
                         if old_locations.get(name) != new_locations.get(name)}
    changed = _changed_instructions(old_cfg, new_cfg)
    changed.update(ir for ir in old_specs.keys() | new_specs.keys() if old_specs.get(ir) != new_specs.get(ir))
    edges = _data_consumers(old_cfg, new_cfg)
    for processing, cfg in ((old_processing, old_cfg), (new_processing, new_cfg)):
        uses, reads, writes = _location_uses(processing, cfg)
        changed.update(ir for ir, names in uses.items() if names & changed_locations)
        successors = instruction_successors(cfg)
        for writer, targets in writes.items():
            for reader in _downstream(successors, successors[writer]):
                if any(locations_may_alias(target, source) for target in targets for source in reads[reader]):
                    edges[writer].add(reader)
    affected = _downstream(edges, changed)
    source_rechecks, unresolved, declarations = defaultdict(list), [], defaultdict(list)
    for record in prior_sensitivity.get("declarations", []):
        declarations[record["instruction_id"]].append(record)
    for finding in findings:
        if finding.get("domain", "annotation") != "annotation" or finding.get("owner") != "sensitivity":
            continue
        for target in finding["target_ids"]:
            owner = _sensitivity_owner(target, prior_sensitivity)
            if owner in new_specs:
                source_rechecks[owner].append({"target_id": target, "source_refs": deepcopy(finding.get("source_refs", []))})
            else:
                unresolved.append(target)
    new = cfg_instructions(new_cfg)
    slots = {ir: {"instruction": deepcopy(new[ir]), "processing": deepcopy(new_specs[ir]),
                  "declarations": deepcopy(declarations[ir]), "source_rechecks": source_rechecks[ir]}
             for ir in sorted((affected | source_rechecks.keys()) & new_specs.keys())}
    plan = {"identity": SENSITIVITY_IDENTITY, "candidate_sha256": canonical_sha256(prior_sensitivity),
        "old_cfg_sha256": canonical_sha256(old_cfg), "new_cfg_sha256": canonical_sha256(new_cfg),
        "old_processing_sha256": canonical_sha256(old_processing), "new_processing_sha256": canonical_sha256(new_processing),
        "findings_sha256": canonical_sha256(findings), "slots": slots,
        "removed_instruction_ids": sorted(declarations.keys() - new_specs.keys()),
        "unresolved_targets": sorted(set(unresolved))}
    return {**plan, "scope_sha256": canonical_sha256(plan)}


def merge_sensitivity_revision(previous, scope, response):
    """Replace only authorized declaration groups and preserve every other row."""
    from .fragments import ScopedSensitivity

    body = {key: value for key, value in scope.items() if key != "scope_sha256"}
    if (scope.get("identity") != SENSITIVITY_IDENTITY or scope.get("scope_sha256") != canonical_sha256(body)
            or scope.get("candidate_sha256") != canonical_sha256(previous)):
        raise ValueError("Sensitivity revision scope does not bind the exact prior fragment")
    try:
        response = _json_object(response)
    except (TypeError, ValueError) as error:
        raise structural_error("sensitivity_revision_json", "", str(error)) from error
    if set(response) != {"slots"} or not isinstance(response["slots"], list):
        raise structural_error("sensitivity_revision_envelope", "", "Return the authorized slots array only.")
    slots, updates = scope["slots"], {}
    for index, row in enumerate(response["slots"]):
        path = json_pointer("slots", index)
        if not isinstance(row, dict) or set(row) != {"instruction_id", "declarations"} or not isinstance(row["declarations"], list):
            raise structural_error("sensitivity_revision_shape", path, "Each slot requires instruction_id and a declarations array.")
        ir = row["instruction_id"]
        if not isinstance(ir, str) or ir not in slots or ir in updates:
            raise structural_error("sensitivity_revision_identity", path + "/instruction_id", "Use each authorized instruction_id at most once.")
        for decl_index, declaration in enumerate(row["declarations"]):
            pointer = path + f"/declarations/{decl_index}"
            try:
                parsed = ScopedSensitivity.model_validate(declaration)
            except ValidationError as error:
                raise schema_error(error, pointer, candidate=declaration,
                    schema=ScopedSensitivity.model_json_schema()) from error
            if parsed.instruction_id != ir:
                raise structural_error("sensitivity_revision_owner", pointer + "/instruction_id", "The declaration must belong to this exact slot.")
        updates[ir] = row["declarations"]
    missing = slots.keys() - updates.keys()
    if missing:
        raise StructuralValidationError([{"code": "sensitivity_revision_missing", "path": "/slots",
            "message": "The revision omitted a requested sensitivity slot.", "context": {"instruction_id": ir}}
            for ir in sorted(missing)])
    result, declarations, retired = deepcopy(previous), [], set(scope["removed_instruction_ids"])
    for row in result.get("declarations", []):
        owner = row["instruction_id"]
        if owner in slots:
            declarations.extend(deepcopy(updates.pop(owner, [])))
        elif owner not in retired:
            declarations.append(row)
    for ir in sorted(updates):
        declarations.extend(deepcopy(updates[ir]))
    if declarations or "declarations" in result:
        result["declarations"] = declarations
    return result


def _correspondence_groups(fragment):
    groups = {row["requirement_id"]: {"realization": row, "demands": [], "operation_demands": []}
              for row in fragment["realizations"]}
    for row in fragment.get("demands", []):
        groups[row["requirement_id"]]["demands"].append(row)
    for row in fragment.get("operation_demands", []):
        per_requirement = defaultdict(list)
        for goal in row["demands"]:
            per_requirement[goal["requirement_id"]].append(goal)
        for requirement, goals in per_requirement.items():
            groups[requirement]["operation_demands"].append({**row, "demands": goals})
    return groups


def _correspondence_owners(target, fragment):
    for prefix in ("annotation:", "fragment:task-correspondence:"):
        if target.startswith(prefix):
            pointer = target[len(prefix):]
            break
    else:
        return set()
    tokens = pointer.split("/")
    if len(tokens) < 3:
        return set()
    try:
        if tokens[1] in {"realizations", "demands"}:
            return {resolve_pointer(fragment, "/".join(tokens[:3]))["requirement_id"]}
        if tokens[1] == "operation_demands":
            row = resolve_pointer(fragment, "/".join(tokens[:3]))
            if len(tokens) >= 5 and tokens[3] == "demands":
                return {resolve_pointer(row, "/" + "/".join(tokens[3:5]))["requirement_id"]}
            return {goal["requirement_id"] for goal in row["demands"]}
        if tokens[1] == "ir_semantics":
            for row in fragment.get("operation_demands", []):
                prefix = json_pointer("ir_semantics", row["instruction_id"], *row["operation_path"], "demands")
                if pointer == prefix:
                    return {goal["requirement_id"] for goal in row["demands"]}
                if pointer.startswith(prefix + "/"):
                    index = pointer[len(prefix) + 1:].split("/", 1)[0]
                    return {resolve_pointer(row, "/demands/" + index)["requirement_id"]}
    except (KeyError, ValueError, TypeError):
        return set()
    return set()


def correspondence_scope(old_cfg, new_cfg, old_processing, new_processing, old_task, new_task, findings,
                         prior_correspondence, *, old_validation_gaps=(), new_validation_gaps=()):
    """Reuse checked requirement records only within an identical operation universe."""
    if (old_cfg != new_cfg or old_processing != new_processing
            or list(old_validation_gaps) != list(new_validation_gaps)):
        return None
    relevant_task_fields = {"task_sha256", "requirements", "issues"}
    if ({key: value for key, value in old_task.items() if key not in relevant_task_fields}
            != {key: value for key, value in new_task.items() if key not in relevant_task_fields}):
        return None
    old = {row["id"]: row for row in old_task["requirements"]}
    new = {row["id"]: row for row in new_task["requirements"]}
    changed = {req for req in old.keys() | new.keys() if old.get(req) != new.get(req)}
    before_issues = {row["id"]: row for row in old_task["issues"]}
    after_issues = {row["id"]: row for row in new_task["issues"]}
    for issue_id in before_issues.keys() | after_issues.keys():
        before, after = before_issues.get(issue_id), after_issues.get(issue_id)
        if before == after:
            continue
        issues = [row for row in (before, after) if row is not None]
        if any(not row["requirement_ids"] for row in issues):
            return None
        changed.update(req for row in issues for req in row["requirement_ids"])

    located = defaultdict(list)
    for finding in findings:
        if finding.get("domain", "annotation") != "annotation" or finding.get("owner") != "task-correspondence":
            continue
        for target in finding["target_ids"]:
            owners = _correspondence_owners(target, prior_correspondence)
            if not owners or not owners <= old.keys():
                return None
            for owner in owners:
                located[owner].append({"target_id": target, "source_refs": deepcopy(finding.get("source_refs", []))})
    previous = _correspondence_groups(prior_correspondence)
    slots = {req: {"requirement": deepcopy(new[req]), "previous": deepcopy(previous.get(req)),
                   "source_rechecks": located[req], "allow_keep": req not in changed and req in previous}
             for req in sorted((changed | located.keys()) & new.keys())}
    plan = {"identity": CORRESPONDENCE_IDENTITY, "candidate_sha256": canonical_sha256(prior_correspondence),
        "cfg_sha256": canonical_sha256(new_cfg), "processing_sha256": canonical_sha256(new_processing),
        "validation_gaps_sha256": canonical_sha256(list(new_validation_gaps)),
        "old_task_sha256": canonical_sha256(old_task), "new_task_sha256": canonical_sha256(new_task),
        "findings_sha256": canonical_sha256(findings), "slots": slots,
        "removed_requirement_ids": sorted(old.keys() - new.keys())}
    return {**plan, "scope_sha256": canonical_sha256(plan)}


def merge_correspondence_revision(previous, scope, response):
    """Merge whole requirement records without changing another requirement's goals."""
    from .fragments import CorrespondenceFragment

    body = {key: value for key, value in scope.items() if key != "scope_sha256"}
    if (scope.get("identity") != CORRESPONDENCE_IDENTITY or scope.get("scope_sha256") != canonical_sha256(body)
            or scope.get("candidate_sha256") != canonical_sha256(previous)):
        raise ValueError("Task correspondence revision scope does not bind the exact prior fragment")
    try:
        response = _json_object(response)
    except (TypeError, ValueError) as error:
        raise structural_error("correspondence_revision_json", "", str(error)) from error
    if set(response) != {"slots"} or not isinstance(response["slots"], list):
        raise structural_error("correspondence_revision_envelope", "", "Return the authorized slots array only.")
    slots, replacements, supplied = scope["slots"], {}, set()
    for index, row in enumerate(response["slots"]):
        path = json_pointer("slots", index)
        if not isinstance(row, dict) or not isinstance(row.get("requirement_id"), str):
            raise structural_error("correspondence_revision_shape", path, "Each slot requires its explicit requirement_id.")
        req = row["requirement_id"]
        if req not in slots or req in supplied:
            raise structural_error("correspondence_revision_identity", path + "/requirement_id",
                "Use each authorized requirement_id at most once.")
        supplied.add(req)
        if set(row) == {"requirement_id", "keep"} and row["keep"] is True and slots[req]["allow_keep"]:
            continue
        if set(row) != {"requirement_id", "realization", "demands", "operation_demands"}:
            raise structural_error("correspondence_revision_shape", path,
                "Supply a complete realization and both demand arrays, or explicitly keep an unchanged allowed requirement.")
        patch = {"realizations": [row["realization"]], "demands": row["demands"], "operation_demands": row["operation_demands"]}
        try:
            parsed = CorrespondenceFragment.model_validate(patch)
        except ValidationError as error:
            raise schema_error(error, path, candidate=patch, schema=CorrespondenceFragment.model_json_schema()) from error
        goals = [*parsed.demands, *(goal for group in parsed.operation_demands for goal in group.demands)]
        if parsed.realizations[0].requirement_id != req or any(goal.requirement_id != req for goal in goals):
            raise structural_error("correspondence_revision_owner", path,
                "The realization and every submitted goal must belong to this exact requirement slot.")
        replacements[req] = patch
    missing = slots.keys() - supplied
    if missing:
        raise StructuralValidationError([{"code": "correspondence_revision_missing", "path": "/slots",
            "message": "The revision omitted a requested requirement slot.", "context": {"requirement_id": req}}
            for req in sorted(missing)])
    invalidated = set(scope["removed_requirement_ids"]) | replacements.keys()
    result = deepcopy(previous)
    result["realizations"] = [deepcopy(replacements[row["requirement_id"]]["realizations"][0])
        if row["requirement_id"] in replacements else row for row in result["realizations"]
        if row["requirement_id"] not in scope["removed_requirement_ids"]]
    present = {row["requirement_id"] for row in result["realizations"]}
    result["realizations"].extend(deepcopy(replacements[req]["realizations"][0]) for req in sorted(replacements.keys() - present))
    demands = [row for row in result.get("demands", []) if row["requirement_id"] not in invalidated]
    operations = {}
    for operation in result.get("operation_demands", []):
        key = operation["instruction_id"], tuple(operation["operation_path"])
        retained = [goal for goal in operation["demands"] if goal["requirement_id"] not in invalidated]
        if retained:
            operations[key] = {**operation, "demands": retained}
    for patch in replacements.values():
        demands.extend(deepcopy(patch["demands"]))
        seen = set()
        for operation in patch["operation_demands"]:
            key = operation["instruction_id"], tuple(operation["operation_path"])
            if key in seen:
                raise structural_error("correspondence_revision_operation", "/slots",
                    "Use one operation demand record per exact operation within a requirement slot.")
            seen.add(key)
            group = operations.setdefault(key, {**operation, "demands": []})
            group["demands"].extend(deepcopy(operation["demands"]))
    if demands or "demands" in result:
        result["demands"] = demands
    if operations or "operation_demands" in result:
        result["operation_demands"] = list(operations.values())
    return result
