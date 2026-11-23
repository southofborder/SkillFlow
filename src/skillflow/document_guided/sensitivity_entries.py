"""Source ingress coordinates for the guided sensitivity request.

Locations identify candidate accesses. A source citation establishes why a
particular read is an external input. Runtime Data/version identities are
resolved later, separately for every actual access.
"""
from copy import deepcopy
from collections import defaultdict
from typing import Literal

from pydantic import Field, ValidationError

from skillflow.common.recording import canonical_sha256
from skillflow.common.source_evidence import _json_object, extract_source_lines
from skillflow.common.validation import StructuralValidationError, schema_error, structural_error
from skillflow.propagation.contracts.references import cfg_instructions
from skillflow.propagation.contracts.sensitivity import SensitivityPath, SensitivityProperty
from skillflow.propagation.contracts.task import TaskEvidence
from skillflow.propagation.contracts.values import StrictSpec, Text


class EntryLabel(StrictSpec):
    entry_id: Text
    origin: Literal["skill_argument", "environment", "file", "tool_response"]
    applicability: Literal["source_field", "access"]
    access_ids: list[Text] = Field(default_factory=list)
    path: SensitivityPath = Field(default_factory=list)
    property: SensitivityProperty = "value"
    label: Text
    evidences: list[TaskEvidence] = Field(min_length=1)


class EntryGap(StrictSpec):
    instruction_id: Text
    missing_from: Literal["cfg", "processing"]
    missing_entry: Text
    reason: Text
    evidences: list[TaskEvidence] = Field(min_length=1)


class EntryLabels(StrictSpec):
    declarations: list[EntryLabel]
    entry_gaps: list[EntryGap] = Field(default_factory=list)


def _operations(segments, path=(), scope=(), case=()):
    for index, segment in enumerate(segments):
        prefix = (*path, index)
        if segment.get("kind") == "for_each":
            yield from _operations(segment["body"], (*prefix, "body"), prefix, case)
        elif segment.get("kind") == "cases":
            for ci, branch in enumerate(segment["cases"]):
                cp = (*prefix, "cases", ci)
                yield from _operations(branch.get("segments", []), (*cp, "segments"), scope, cp)
        else:
            for oi, operation in enumerate(segment.get("ops", [])):
                yield (*prefix, "ops", oi), scope, case, operation


def _straight_line_contexts(cfg):
    """Share a context only across proved unconditional straight-line edges."""
    incoming, outgoing = defaultdict(list), defaultdict(list)
    for edge in cfg.get("edges", []):
        incoming[edge["target_block_id"]].append(edge)
        outgoing[edge["source_block_id"]].append(edge)
    parent = {}
    for block in cfg["blocks"]:
        if block == cfg.get("entry_block_id") or len(incoming[block]) != 1:
            continue
        edge = incoming[block][0]
        predecessor = edge["source_block_id"]
        if len(outgoing[predecessor]) == 1 and edge.get("condition_text") is None:
            parent[block] = predecessor
    result = {}
    for block in cfg["blocks"]:
        current, visited = block, set()
        while current in parent and current not in visited and current not in result:
            visited.add(current)
            current = parent[current]
        if current in visited:
            # A closed cycle has no verified straight-line entrance.
            result.update({item: item for item in visited})
        else:
            root = result.get(current, current)
            result[block] = root
            result.update({item: root for item in visited})
    return result


def entry_catalogue(cfg, processing, *, owners=None):
    """Share a source classification for repeated accesses to one fixed root."""
    groups = {}
    definitions = processing.get("locations", {})
    anchors = defaultdict(list)
    for location in definitions.values():
        for ref in location.get("operand_refs", []):
            if ref["side"] == "input":
                anchors[ref["instruction_id"], ref["index"]].append(location)
    regions = _straight_line_contexts(cfg)
    blocks = {op["id"]: regions[block_id] for block_id, block in cfg["blocks"].items() for op in block["instructions"]}
    for ir, ins in sorted(cfg_instructions(cfg).items()):
        if ir not in processing.get("ir_semantics", {}) or owners is not None and ir not in owners:
            continue
        spec = processing["ir_semantics"][ir]

        def add(key, origins, source, site, location):
            identity = "entry_" + canonical_sha256(key)[:24]
            row = groups.setdefault(identity, {"source": source, "location": location, "origins": origins, "accesses": []})
            context = [blocks[ir]]
            if site.get("case_path") or site.get("scope_path"):
                context.extend([ir, site.get("scope_path", []), site.get("case_path", [])])
            access_id = "access_" + canonical_sha256([identity, ir, site])[:24]
            row["accesses"].append({"instruction_id": ir, "access_id": access_id,
                                    "source_entry_context": canonical_sha256(context), **site})

        for i, operand in enumerate(ins.get("inputs", [])):
            if operand["type"] == "context_key":
                name = operand["identifier"]
                for loc in anchors.get((ir, i), [{"kind": "runtime_context", "name": name}]):
                    kind = loc["kind"]
                    origins = {"runtime_context": ["skill_argument", "environment"], "storage": ["file"],
                               "user": ["skill_argument"]}.get(kind)
                    if origins:
                        key = ["context_key", kind, loc["name"]]
                        if loc.get("address_kind") == "unidentified":
                            key.extend([ir, i])
                        add(key, origins, name, {"value": {"kind": "input", "index": i}, "operand_index": i},
                            kind + ":" + loc["name"])
        for path, scope, case, op in _operations(spec.get("segments", []), ("segments",)):
            location = op.get("location")
            loc = definitions.get(location, {})
            kind = loc.get("kind")
            operation = op.get("op")
            if operation == "read" and kind in {"runtime_context", "storage"}:
                origins = ["environment", "skill_argument"] if kind == "runtime_context" else ["file"]
            elif operation in {"receive", "call"} and kind in {"remote", "tool"}:
                origins = ["tool_response"]
            elif operation == "receive" and kind == "user":
                origins = ["skill_argument"]
            else:
                continue
            site = {"operation_path": list(path), "value": {"kind": "local", "name": op["output"]}}
            if case:
                site["case_path"] = list(case)
            if scope:
                site["scope_path"] = list(scope)
            key = ["operation", ir, path]
            if operation == "read" and not loc.get("operand_refs") and loc.get("address_kind", "identified") == "identified":
                key = ["read", kind, location]
            add(key, origins, location, site, kind + ":" + loc["name"])
    return groups


def instructions():
    return ("Use entry_id from entry_catalogue. Classify only actual external inputs evidenced by the complete "
            "source: Skill arguments, environment values, file contents and tool responses. A read candidate "
            "can be internal state, a resource handle or a value written earlier: do not label it as a new "
            "external source. Set applicability=source_field only when your citation supports that the field at "
            "the source itself is sensitive regardless of callers, branches and accesses. For source_field, omit "
            "access_ids. If the evidence supports sensitivity only at particular accesses set applicability=access "
            "and supply exactly those distinct catalogue access_ids. Explain the choice in the evidence reason. Omit "
            "derived values, copied credentials, receives unrelated to a real reply, and numeric scores. "
            "If the source establishes an entry that processing omitted or merged with an incompatible "
            "value, submit an entry_gap with the affected CFG instruction, stage missing the relation, reason "
            "and precise physical source evidence; do not substitute a downstream local.")


def resolve_labels(raw, catalogue, instructions_by_id, files):
    """Expand source classifications into existing lexical records, never into new facts."""
    try:
        parsed = _json_object(raw)
    except (TypeError, ValueError) as exc:
        raise structural_error("json_format", "", str(exc)) from exc
    try:
        value = EntryLabels.model_validate(parsed)
    except ValidationError as exc:
        raise schema_error(exc, candidate=parsed, schema=EntryLabels.model_json_schema()) from exc
    expanded, diagnostics, seen = [], [], defaultdict(set)

    def error(code, path, reason):
        diagnostics.extend(structural_error(code, path, reason).diagnostics)

    def evidence(rows, prefix):
        for i, citation in enumerate(rows):
            try:
                extract_source_lines(files[citation.file], citation.start_line, citation.end_line)
            except (KeyError, ValueError):
                error("entry_evidence", f"{prefix}/evidences/{i}", "Use a physical span in the complete frozen source.")

    for i, label in enumerate(value.declarations):
        pointer = f"/declarations/{i}"
        evidence(label.evidences, pointer)
        entry = catalogue.get(label.entry_id)
        if entry is None:
            error("sensitivity_entry_id", pointer + "/entry_id", "Choose an entry_id in the signed ingress catalogue.")
            continue
        if label.origin not in entry["origins"]:
            error("sensitivity_entry_kind", pointer + "/origin", "The claimed origin does not match this entry's access kind.")
        wanted = set(label.access_ids)
        available = {s["access_id"] for s in entry["accesses"]}
        if ((label.applicability == "access") != bool(wanted) or not wanted <= available
                or len(wanted) != len(label.access_ids)):
            error("sensitivity_entry_applicability", pointer + "/access_ids",
                  "Source fields omit access_ids. Access-scoped labels require distinct access_ids belonging to this entry.")
            continue
        fields = label.model_dump(mode="json", exclude={"origin", "entry_id", "applicability", "access_ids"})
        key = canonical_sha256([label.entry_id, fields["path"], fields["property"], label.label])
        covered = wanted or available
        if seen[key] & covered:
            error("sensitivity_duplicate", pointer, "This entry, field, property and label already covers one or more of the same accesses.")
        seen[key].update(covered)
        for site in entry["accesses"]:
            if wanted and site["access_id"] not in wanted:
                continue
            lexical = {k: deepcopy(v) for k, v in site.items() if k not in {"operation_path", "operand_index", "access_id"}}
            expanded.append({**lexical, **deepcopy(fields), "source_entry_id": label.entry_id,
                             "source_entry_origin": label.origin,
                             "source_entry_location": entry["location"], "source_entry_applicability": label.applicability,
                             "source_access_id": site["access_id"]})
    gaps = [g.model_dump(mode="json") for g in value.entry_gaps]
    for i, gap in enumerate(value.entry_gaps):
        evidence(gap.evidences, f"/entry_gaps/{i}")
        if gap.instruction_id not in instructions_by_id:
            error("sensitivity_entry_gap_owner", f"/entry_gaps/{i}/instruction_id", "Use an existing CFG instruction.")
    if diagnostics:
        raise StructuralValidationError(diagnostics)
    return {"declarations": expanded, **({"entry_gaps": gaps} if gaps else {})}


def validate_resolved_sites(rows, catalogue):
    """A stored or merged declaration must still address the current CFG/processing site."""
    diagnostics = []
    sites = {site["access_id"]: (key, entry, site) for key, entry in catalogue.items()
             for site in entry["accesses"]}
    for i, record in enumerate(rows):
        if not isinstance(record, dict) or "source_entry_id" not in record:
            continue
        access = record.get("source_access_id")
        target = sites.get(access) if isinstance(access, str) else None
        if target:
            key, entry, site = target
            if (key == record["source_entry_id"] and entry["location"] == record.get("source_entry_location")
                    and record.get("source_entry_origin") in entry["origins"]
                    and all(record.get(k) == site.get(k) for k in ("instruction_id", "value", "source_entry_context"))
                    and (record.get("scope_path") or []) == (site.get("scope_path") or [])
                    and record.get("case_path") == site.get("case_path")):
                continue
        diagnostics.extend(structural_error("sensitivity_entry_binding", f"/declarations/{i}/source_access_id",
            "The stored ingress binding does not match the source entry, access position, context and value in the current catalogue.").diagnostics)
    return diagnostics


def prior_entry_labels(declarations):
    """Restore the signed model-facing classifications for a single revision slot."""
    labels = {}
    for row in declarations:
        if not row.get("source_entry_id"):
            continue
        label = {**{k: deepcopy(row[k]) for k in ("label", "path", "property", "evidences") if k in row},
                 "entry_id": row["source_entry_id"], "origin": row["source_entry_origin"],
                 "applicability": row["source_entry_applicability"]}
        key = canonical_sha256(label)
        record = labels.setdefault(key, label)
        if label["applicability"] == "access":
            record.setdefault("access_ids", []).append(row["source_access_id"])
    return list(labels.values())


def retain_valid_entries(raw, cfg, processing, files):
    """Retain validated rows with a known failure owner, never a raw downstream seed."""
    from skillflow.propagation.contracts.limitations import validation_gap
    try:
        candidate = _json_object(raw)
    except (TypeError, ValueError):
        return None, []
    if (set(candidate) - {"declarations", "entry_gaps"} or not isinstance(candidate.get("declarations"), list)
            or not isinstance(candidate.get("entry_gaps", []), list)):
        return None, []
    catalogue, owners = entry_catalogue(cfg, processing), cfg_instructions(cfg)
    valid = {"declarations": [], "entry_gaps": []}
    issues = {}
    for table in valid:
        for index, row in enumerate(candidate.get(table, [])):
            if not isinstance(row, dict):
                return None, []
            try:
                resolve_labels({"declarations": [], table: [row]}, catalogue, owners, files)
            except StructuralValidationError as exc:
                entry = catalogue.get(row.get("entry_id")) if isinstance(row.get("entry_id"), str) else None
                ids = ({s["instruction_id"] for s in entry["accesses"]} if entry else
                       {row["instruction_id"]} if isinstance(row.get("instruction_id"), str) and row["instruction_id"] in owners else set())
                if not ids:
                    return None, []
                for ir in ids:
                    issues.setdefault(ir, []).extend({**d, "path": d["path"].replace(
                        f"/{table}/0", f"/{table}/{index}", 1)} for d in exc.diagnostics)
            else:
                valid[table].append(row)
    try:
        resolved = resolve_labels(valid, catalogue, owners, files)
    except StructuralValidationError:
        return None, []
    return resolved, [validation_gap(ir, ds, unmodeled=False) for ir, ds in sorted(issues.items())]


def ingress_gap_rechecks(material):
    """Route a retained limitation to an existing producer target in this bundle."""
    from skillflow.common.source_evidence import json_pointer
    targets = {row["id"] for row in material["target_index"]}
    cfg_sites = {op["id"]: "cfg:" + json_pointer("blocks", bid, "instructions", i)
                 for bid, block in (material.get("cfg") or {}).get("blocks", {}).items()
                 for i, op in enumerate(block["instructions"])}
    result = []
    for gap in material.get("sensitivity_entry_gaps", []):
        ir = gap["instruction_id"]
        if gap["missing_from"] == "cfg":
            candidates = [cfg_sites.get(ir)]
            domain = {"domain": "cfg"}
        else:
            candidates = [prefix + json_pointer("ir_semantics", ir)
                          for prefix in ("annotation:", "fragment:processing:")]
            for i, item in enumerate(material.get("processing_gaps", [])):
                if item.get("instruction_id") == ir:
                    candidates.extend(prefix + json_pointer("processing_gaps", i)
                                      for prefix in ("annotation:", "fragment:processing:"))
            domain = {"domain": "annotation", "owner": "processing"}
        target = next((item for item in candidates if item in targets), None)
        if target:
            result.append({**domain, "target_ids": [target], "explanation":
                "An ingress classification remains unbound: " + gap["missing_entry"] + ". " + gap["reason"],
                "source_refs": [{k: e[k] for k in ("file", "start_line", "end_line")} for e in gap["evidences"]],
                "suggestion": "Verify the cited ingress relation at its producer and bind the actual access if supported."})
    return result
