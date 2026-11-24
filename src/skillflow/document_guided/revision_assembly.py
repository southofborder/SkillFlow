"""Assemble current scoped fragment revisions, then validate the full merged material."""
from collections import defaultdict
from copy import deepcopy

from skillflow.common.recording import canonical_sha256
from skillflow.common.revision_slots import decode_revision_slots
from skillflow.common.source_evidence import json_pointer
from skillflow.common.validation import StructuralValidationError, structural_error
from skillflow.propagation.contracts.limitations import validation_gap

from .fragment_revision import merge_correspondence_revision, merge_processing_revision, merge_sensitivity_revision
from .fragment_wire import expand_revision_rows
from .processing_correction import remove_coverage_claims


def _diagnostic_owners(row, field, names, candidate=None):
    path = row["path"].split("/")[1:]
    context = row.get("context", {})
    found = {context.get("instruction_id"), context.get("requirement_id")}
    found.discard(None)
    if len(path) < 2:
        return found
    table, token = path[:2]
    if table == field and token.isdigit() and int(token) < len(names):
        found.add(names[int(token)])
    if table == "ir_semantics":
        found.add(token.replace("~1", "/").replace("~0", "~"))
    if candidate is not None and token.isdigit() and table in {
            "processing_gaps", "declarations", "entry_gaps", "realizations", "demands", "operation_demands", "expressions"}:
        rows = candidate.get(table, [])
        if int(token) < len(rows) and isinstance(rows[int(token)], dict):
            item = rows[int(token)]
            if table == "operation_demands":
                for goal in item.get("demands", []):
                    if isinstance(goal, dict) and isinstance(goal.get("requirement_id"), str):
                        found.add(goal["requirement_id"])
            for ref in (item, item.get("target", {})):
                if isinstance(ref, dict):
                    found.update(ref[k] for k in ("instruction_id", "requirement_id") if isinstance(ref.get(k), str))
    return found


def _scope_for(scope, rows):
    plan = {key: value for key, value in scope.items() if key != "scope_sha256"}
    plan["slots"] = {key: scope["slots"][key] for key in rows}
    return {**plan, "scope_sha256": canonical_sha256(plan)}


def _conflicting_declarations(rows):
    owners = defaultdict(set)
    for ir, row in rows.items():
        locations, expressions = row.get("new_locations"), row.get("new_expressions")
        if isinstance(locations, dict):
            for name in locations:
                owners[("location", name)].add(ir)
        if isinstance(expressions, list):
            for exp in expressions:
                if isinstance(exp, dict) and isinstance(exp.get("target"), dict):
                    owners[("expression", canonical_sha256(exp["target"]))].add(ir)
    return [(kind, key, irs) for (kind, key), irs in owners.items() if len(irs) > 1]


def assemble_revision(kind, raw, context, material):
    """Retain only scoped errors with identifiable owners; the ordinary compiler decides validity."""
    from .fragments import validate_fragment
    revision_key = {"processing": "processing_revision", "sensitivity": "sensitivity_revision",
                    "task-correspondence": "correspondence_revision"}[kind]
    scope, previous = (context[revision_key][k] for k in ("scope", "previous"))
    if (canonical_sha256(previous) != scope["candidate_sha256"] or canonical_sha256({
            k: v for k, v in scope.items() if k != "scope_sha256"}) != scope["scope_sha256"]):
        raise ValueError("Revision scope does not match its bound prior material.")
    processing = kind == "processing"
    sensitivity = kind == "sensitivity"
    field = "coverage_slots" if processing else "slots"
    owner = "requirement_id" if kind == "task-correspondence" else "instruction_id"
    decoded = decode_revision_slots(raw, field=field, owner=owner, authorized=scope["slots"],
        shared=expand_revision_rows if processing else False)
    live = dict(decoded.rows)
    diagnostics = list(decoded.diagnostics)
    failed = {name: [] for name in scope["slots"].keys() - live.keys()}
    for diagnostic in diagnostics:
        for name in _diagnostic_owners(diagnostic, field, []) & failed.keys():
            failed[name].append(diagnostic)
    submitted = decoded.submitted
    if processing:
        for typ, key, owners in _conflicting_declarations(live):
            for name in sorted(owners):
                diagnostic = {"code": "revision_declaration_conflict", "path": json_pointer(field, name),
                              "message": f"The proposed {typ} {key} has multiple declaring slots.",
                              "context": {owner: name}}
                diagnostics.append(diagnostic)
                failed.setdefault(name, []).append(diagnostic)
                live.pop(name, None)
    discarded_prior = set()
    upstream = list(context.get("validation_gaps", []))
    while True:
        names = list(live)
        candidate = None
        local_scope = _scope_for(scope, live)
        # Reuse the original slot merger with a strict subset of the already authorized
        # owners. The original prior candidate and signed field grants are never changed.
        merged = {field: list(live.values())}
        gaps = list(upstream) if processing else []
        carried = set()
        try:
            if processing:
                candidate = merge_processing_revision(previous, local_scope, merged, files=context.get("files"))
            elif sensitivity:
                candidate = merge_sensitivity_revision(previous, local_scope, merged, files=context.get("files"))
            else:
                candidate = merge_correspondence_revision(previous, local_scope, merged)
            for name, problems in sorted(failed.items()):
                slot = scope["slots"][name]
                errors = problems or [{"code": "revision_slot_missing", "path": json_pointer(field, name),
                                        "message": "This authorized owner has no valid revised value."}]
                if processing:
                    if slot["allow_keep"] and name not in discarded_prior:
                        carried.add(name)
                    else:
                        remove_coverage_claims(candidate, {name})
                        gaps.append(validation_gap(name, errors))
                elif sensitivity:
                    if name not in discarded_prior:
                        carried.add(name)
                    else:
                        candidate["declarations"] = [d for d in candidate.get("declarations", [])
                                                     if d["instruction_id"] != name]
                    gaps.append(validation_gap(name, errors, unmodeled=False))
                elif slot["allow_keep"] and name not in discarded_prior:
                    carried.add(name)
                else:
                    # Only the affected task requirement loses its unsupported goals.
                    candidate["realizations"] = [r for r in candidate["realizations"] if r["requirement_id"] != name]
                    candidate["realizations"].append({"requirement_id": name, "gaps": [{
                        "reason": errors[0]["message"], "evidences": deepcopy(slot["requirement"]["evidences"])}]})
                    if "demands" in candidate:
                        candidate["demands"] = [g for g in candidate["demands"] if g["requirement_id"] != name]
                    for group in candidate.get("operation_demands", []):
                        group["demands"] = [g for g in group["demands"] if g["requirement_id"] != name]
                    if "operation_demands" in candidate:
                        candidate["operation_demands"] = [g for g in candidate["operation_demands"] if g["demands"]]
            value = validate_fragment(kind, candidate, material, processing=context.get("processing"),
                validation_gaps=gaps if processing else upstream)
        except StructuralValidationError as error:
            rejected = defaultdict(list)
            for diagnostic in error.diagnostics:
                owners = _diagnostic_owners(diagnostic, field, names, candidate)
                if candidate is not None and diagnostic["path"].startswith("/locations/"):
                    key = diagnostic["path"].split("/")[2].replace("~1", "/").replace("~0", "~")
                    owners.update(n for n, row in live.items() if isinstance(row.get("new_locations"), dict)
                                  and key in row["new_locations"])
                for name in owners & (live.keys() | carried):
                    rejected[name].append(diagnostic)
            if not rejected:
                raise
            for name, problems in rejected.items():
                if name not in live:
                    discarded_prior.add(name)
                live.pop(name, None)
                labeled = [{**d, "context": {**d.get("context", {}), owner: name}} for d in problems]
                failed.setdefault(name, []).extend(labeled)
                diagnostics.extend(labeled)
            continue
        receipt = {"assembled_sha256": canonical_sha256(value), "validation_gaps_sha256": canonical_sha256(gaps),
                 "scope_sha256": scope["scope_sha256"], "raw_sha256": canonical_sha256(raw),
            "submitted": sorted(submitted), "accepted": sorted(live), "retained_prior": sorted(carried),
            "quarantined": sorted(failed.keys() - carried), "diagnostics": diagnostics, "repairs": decoded.repairs}
        return value, gaps, receipt


def full_revision(kind, raw, context, material):
    """Read a complete replacement against its current owners when no finite prior is reusable."""
    from skillflow.common.revision_slots import read_revision_object
    from skillflow.propagation.contracts.references import cfg_instructions
    from .fragments import validate_fragment, salvage_fragment
    from .sensitivity_entries import entry_catalogue, resolve_labels, retain_valid_entries
    from .fragment_wire import expand_processing_response, PROCESSING_WIRE_IDENTITY
    obj = read_revision_object(raw)
    value, diagnostics = obj.value, list(obj.diagnostics)
    if kind == "processing" and "format" in value:
        try:
            value = expand_processing_response(value)
        except (TypeError, ValueError):
            if (set(value) != {"format", "payload", "shared_values"} or value["format"] != PROCESSING_WIRE_IDENTITY
                    or not isinstance(value["payload"], dict) or not isinstance(value["shared_values"], dict)):
                raise structural_error("revision_envelope", "", "Expected the complete processing envelope.")
            flattened, coordinates = {}, {}
            assembled = {}
            for table, elements in value["payload"].items():
                if table in {"ir_semantics", "locations"} and isinstance(elements, dict):
                    entries = elements.items()
                    assembled[table] = {}
                elif table in {"expressions", "processing_gaps"} and isinstance(elements, list):
                    entries = enumerate(elements)
                    assembled[table] = []
                else:
                    raise structural_error("revision_envelope", json_pointer("payload", table),
                                           "Cannot independently identify this complete revision collection.")
                for index, item in entries:
                    number = len(coordinates)
                    coordinates[number] = (table, index)
                    flattened[number] = item
            included, errors = expand_revision_rows(flattened, value["shared_values"], owner="instruction_id", field="records")
            for diagnostic in errors:
                if diagnostic["path"].startswith("/records/"):
                    table, index = coordinates[int(diagnostic["path"].split("/")[2])]
                    diagnostic = {**diagnostic, "path": json_pointer(table, index)}
                diagnostics.append(diagnostic)
            for number, item in included.items():
                table, index = coordinates[number]
                if isinstance(assembled[table], dict):
                    assembled[table][index] = item
                else:
                    assembled[table].append(item)
            value = assembled
    if value.get("outcome") == "cannot_assess":
        return None
    instructions = cfg_instructions(material["cfg"])
    new_gaps, reqs = [], set()
    catalogue = entry_catalogue(material["cfg"], context["processing"]) if kind == "sensitivity" else {}
    for diagnostic in diagnostics:
        path = diagnostic["path"].removeprefix("/payload/").strip("/").split("/")
        table = path[0]
        c = diagnostic.get("context", {})
        if table == "shared_values":
            continue  # Dependent records carry their own errors.
        if kind == "processing" and table == "locations":
            continue  # The full compiler resolves each actual address user below.
        ir = (path[1].replace("~1", "/").replace("~0", "~") if table == "ir_semantics" and len(path) > 1
              else c.get("instruction_id"))
        if kind == "sensitivity":
            entry = catalogue.get(c.get("entry_id"), {})
            ids = {a["instruction_id"] for a in entry.get("accesses", [])} or ({ir} if ir in instructions else set())
            if not ids:
                raise StructuralValidationError([diagnostic])
            new_gaps.extend(validation_gap(i, [diagnostic], unmodeled=False) for i in sorted(ids))
        elif kind == "processing":
            if ir not in instructions:
                raise StructuralValidationError([diagnostic])
            remove_coverage_claims(value, {ir})
            new_gaps.append(validation_gap(ir, [diagnostic]))
        elif c.get("requirement_id") in {r["id"] for r in material["task"]["requirements"]}:
            reqs.add(c["requirement_id"])
        else:
            raise StructuralValidationError([diagnostic])
    if reqs:
        for table in ("realizations", "demands"):
            if table in value:
                value[table] = [row for row in value[table] if row.get("requirement_id") not in reqs]
        if "operation_demands" in value:
            for row in value["operation_demands"]:
                row["demands"] = [g for g in row["demands"] if g.get("requirement_id") not in reqs]
            value["operation_demands"] = [row for row in value["operation_demands"] if row["demands"]]
    upstream = list(context.get("validation_gaps", []))
    if kind == "sensitivity":
        try:
            value = resolve_labels(value, catalogue, instructions, context["files"])
        except StructuralValidationError as error:
            resolved, limits = retain_valid_entries(value, material["cfg"], context["processing"], context["files"])
            if resolved is None:
                raise
            diagnostics.extend(error.diagnostics)
            new_gaps.extend(limits)
            value = resolved
    try:
        valid = validate_fragment(kind, value, material, processing=context.get("processing"), validation_gaps=upstream + new_gaps)
    except StructuralValidationError as error:
        diagnostics.extend(error.diagnostics)
        valid, limits = salvage_fragment(kind, value, material, processing=context.get("processing"), validation_gaps=upstream + new_gaps)
        if valid is None:
            raise
        new_gaps.extend(limits)
    receipt = {
        "mode": "complete_replacement",
        "raw_sha256": canonical_sha256(raw),
        "assembled_sha256": canonical_sha256(valid),
        "validation_gaps_sha256": canonical_sha256(new_gaps),
        "repairs": obj.repairs,
        "diagnostics": diagnostics,
    }
    return valid, new_gaps, receipt
