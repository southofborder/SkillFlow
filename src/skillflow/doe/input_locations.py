"""Deterministic use locations and semantic edit recipes, never a patch engine."""
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from typing import Literal
from pydantic import Field, JsonValue

from skillflow.common.recording import canonical_sha256
from skillflow.common.source_evidence import json_pointer, resolve_pointer, extract_source_lines
from skillflow.propagation.contracts.values import StrictSpec, Text, Index
from skillflow.propagation.contracts.joint import joint_source_files
from skillflow.propagation.contracts.demand_index import build_demand_target_index
from skillflow.propagation.contracts.demand import EachDemandStep
from skillflow.propagation.data.models import PathStep
from .input_contracts import overlaps, covers

Path = list[PathStep | EachDemandStep]


class EditSite(StrictSpec):
    pointer: Text
    role: Text


class SourceSpan(StrictSpec):
    file: Text
    start_line: Index
    end_line: Index
    evidence_origin: Literal["direct", "inherited"]


class AssessmentLocation(StrictSpec):
    cfg_pointer: Text
    raw_annotation_sites: list[EditSite]
    wire_annotation_sites: list[EditSite]
    metadata_binding_sites: list[EditSite]
    source_spans: list[SourceSpan]
    source_resolution: Literal["direct_span", "inherited_span", "annotation_only"]
    generated_origin: Literal["authored_use", "processing_observation", "acquisition_result"]
    scope: dict[str, JsonValue]
    downstream_use_sites: list[EditSite]
    reason: Text


class RetainedInformation(StrictSpec):
    property: Literal["value", "presence", "shape", "cardinality", "truth"]
    path: Path
    excluded_paths: list[Path]


class InputModification(StrictSpec):
    kind: Literal["remove_input", "exclude_field", "keep_ranges", "omit_result_range_at_use"]
    path: Path
    excluded_paths: list[Path]
    retained_information: list[RetainedInformation]
    reason: Text


class RetrievalProjection(StrictSpec):
    status: Literal["established", "unestablished"]
    capabilities: list[dict[str, JsonValue]]
    reason: Text


def use_suffix(operation, slot):
    """Return a real field pointer for a typed consumed slot, not /uses/N."""
    kind = operation["op"]
    if "inputs" in operation:
        if slot < len(operation["inputs"]):
            return ["inputs", slot]
        if slot == len(operation["inputs"]) and operation.get("when") is not None:
            return ["when"]
    if kind == "build":
        at = 0
        for index, part in enumerate(operation["parts"]):
            for field in (["when", "value"] if part.get("when") is not None else ["value"]):
                if at == slot:
                    return ["parts", index, field]
                at += 1
    elif kind == "update_fields":
        return ["input"] if slot == 0 else ["updates", slot - 1, "value"]
    elif kind == "merge":
        return ["incoming", slot, "value"]
    elif kind == "append":
        return ["input"] if slot == 0 else ["value"] if slot == 1 else None
    elif "input" in operation and slot == 0:
        return ["input"]
    return None


def record_use_suffix(operation, record, slot):
    """Recorded inactive members may omit value slots; preserve raw identity."""
    if operation["op"] == "build":
        for member, binding in enumerate(record["members"]):
            if binding["when_input_index"] == slot:
                return ["parts", member, "when"]
            if binding["value_input_index"] == slot:
                return ["parts", member, "value"]
        return None
    if operation.get("when") is not None and record.get("when_input_index") == slot:
        return ["when"]
    return use_suffix(operation, slot)


def assessed_modification(assessment, row):
    """Translate an established information change, never invent array edits."""
    if row["status"] != "deletable":
        return None, None
    location = assessment.get("location", {})
    if location.get("generated_origin") == "processing_observation" and all(
            site["role"] == "observed_processing_context" for site in location.get("raw_annotation_sites", [])):
        return None, "The generated observation has only a processing-context location; no specific source context-supply use is established for a concrete edit. The original observation remains recorded."
    path, excluded = row["path"], row["excluded_paths"]
    retained = {canonical_sha256({k:r[k] for k in ("property", "path", "excluded_paths")}):
                {k:deepcopy(r[k]) for k in ("property", "path", "excluded_paths")}
                for r in assessment["ranges"] if r["status"] in {"required", "unresolved"}}
    if path and not excluded and type(path[-1]) is not str:
        return None, "No member-removal or array-reindexing edit is established for this terminal index/member selector."
    if excluded and any(any(type(step) is int or isinstance(step, dict) for step in p) for p in excluded):
        if not any(r["property"] in {"shape", "cardinality"} and not r["path"] for r in retained.values()):
            return None, "The complement includes collection members but no supported structural retention recipe establishes index, order and cardinality preservation."
    if assessment["node_kind"] == "acquisition_output":
        return {"kind": "omit_result_range_at_use", "path": deepcopy(path), "excluded_paths": deepcopy(excluded),
            "retained_information": [retained[k] for k in sorted(retained)],
            "reason": "Omit the established unused acquired information at the listed downstream uses; retain the acquisition action and its original observation facts."}, None
    if excluded:
        return {"kind": "keep_ranges", "path": deepcopy(path), "excluded_paths": deepcopy(excluded),
            "retained_information": [retained[k] for k in sorted(retained)],
            "reason": "At this supplied use, preserve every listed value and structural information requirement while omitting the assessed complement. This is a semantic range recipe, not a value-only projection or executable patch."}, None
    if not path:
        return {"kind": "remove_input", "path": [], "excluded_paths": [], "retained_information": [],
            "reason": "Omit this entire value from the observed processing context at the listed supplier/result context sites; retain the acquisition and original observation fact."
                if location.get("generated_origin") == "processing_observation" else
                "Remove this entire supplied input use at the listed source/annotation sites; update its source-level argument relationship without erasing the original analysis fact."}, None
    return {"kind": "exclude_field", "path": deepcopy(path), "excluded_paths": [], "retained_information": [],
        "reason": "Omit this exact field at the assessed use, preserving its containing object/member identity and other required information."}, None


class InputLocationBuilder:
    def __init__(self, engine):
        self.engine = engine
        self.raw = engine.raw
        self.mapping = engine.annotation["mapping"]
        self.files = joint_source_files(engine.annotation["material"])
        self.targets = build_demand_target_index(engine.index.cfg, self.raw)
        self.operations = [x for x in self.targets.values() if x.get("domain") == "transfer" and x.get("kind") == "operation"]
        self.by_raw = {(x["instruction_id"], tuple(x["raw_path"])): x for x in self.operations}
        self.operations_by_ir = defaultdict(list)
        for operation in self.operations:
            self.operations_by_ir[operation["instruction_id"]].append(operation)
        self.uses = defaultdict(list)
        self.other_uses = defaultdict(list)
        for target in self.targets.values():
            if target.get("kind") == "input_use":
                self.uses[(target["instruction_id"], tuple(target["operation_raw_path"]))].append(target)
            elif target.get("kind") in {"output_binding", "segment_return", "collection"}:
                self.other_uses[target["instruction_id"]].append(target)
        self.cfg = {ir["id"]: json_pointer("blocks", bid, "instructions", i)
                    for bid, block in engine.index.cfg["blocks"].items() for i,ir in enumerate(block["instructions"])}
        self._locations = {}
        self._consumers = None

    def _site(self, target, slot, role="actual_input"):
        suffix = use_suffix(target["value"], slot)
        if suffix is None:
            raise ValueError("A consumed input has no actual editable source field")
        pointer = target["pointer"] + json_pointer(*suffix)
        resolve_pointer(self.raw, pointer)
        return {"pointer": pointer, "role": role}

    def _record_site(self, target, info, slot, role="actual_input"):
        suffix = record_use_suffix(target["value"], info["record"], slot)
        if suffix is None:
            raise ValueError("A recorded input has no source use at its recorded member/control position")
        pointer = target["pointer"] + json_pointer(*suffix)
        resolve_pointer(self.raw, pointer)
        return {"pointer": pointer, "role": role}

    def _wire(self, site):
        paths = self.mapping.get("wire_paths", {})
        ancestors = [p for p in paths if site["pointer"] == p or site["pointer"].startswith(p + "/")]
        if not ancestors:
            return None
        parent = max(ancestors, key=len)
        pointer = paths[parent] + site["pointer"][len(parent):]
        # Flat transforms preserve input field suffixes. A mapped container is
        # retained only if the selected wire object actually resolves it.
        wire = self.engine.annotation.get("wire_annotation")
        if wire is not None:
            try:
                resolve_pointer(wire, pointer)
            except (KeyError, IndexError, TypeError, ValueError):
                return {"pointer": paths[parent], "role": "mapped_operation_context"}
        return {"pointer": pointer, "role": site["role"]}

    def _sources(self, sites, ir):
        spans = {}
        for site in sites or [{"pointer": json_pointer("ir_semantics", ir)}]:
            parents = [x["pointer"] for x in self.operations_by_ir[ir] if site["pointer"] == x["pointer"] or site["pointer"].startswith(x["pointer"] + "/")]
            pointer = max(parents, key=len) if parents else site["pointer"]
            direct = bool(parents)
            while pointer:
                try:
                    value = resolve_pointer(self.raw, pointer)
                except (KeyError, IndexError, TypeError, ValueError):
                    value = None
                evidence = value.get("evidences", []) if isinstance(value, dict) else []
                for item in evidence:
                    if "file" not in item or item["file"] not in self.files:
                        continue
                    extract_source_lines(self.files[item["file"]], item["start_line"], item["end_line"])
                    span = {k:item[k] for k in ("file", "start_line", "end_line")}
                    span["evidence_origin"] = "direct" if direct else "inherited"
                    spans[canonical_sha256(span)] = span
                if evidence and any("file" in item for item in evidence):
                    break
                pointer = pointer.rsplit("/", 1)[0]
                direct = False
        return [spans[k] for k in sorted(spans)]

    def location(self, assessment):
        identity = assessment["id"]
        if identity in self._locations:
            return deepcopy(self._locations[identity])
        ir, operation, slot = assessment["instruction_id"], assessment["operation_id"], assessment["input_index"]
        cfg_pointer = self.cfg[ir]
        sites, downstream, scope = [], [], {}
        metadata_sites = []
        origin = "authored_use"
        if assessment["node_kind"] == "ir_input":
            cfg_pointer += json_pointer("inputs", slot)
            for name, declaration in self.raw["locations"].items():
                for index, reference in enumerate(declaration["operand_refs"]):
                    if reference == {"instruction_id": ir, "side": "input", "index": slot}:
                        metadata_sites.append({"pointer": json_pointer("locations", name, "operand_refs", index),
                            "role": "declared_location_operand_identity"})
            def uses_input(ref):
                return ref == {"kind": "input", "index": slot} or ref.get("kind") == "alternatives" and any(uses_input(r) for r in ref["items"])
            for target in self.operations_by_ir[ir]:
                if target["instruction_id"] == ir:
                    for use in self.uses[(ir, tuple(target["raw_path"]))]:
                        if uses_input(use["ref"]):
                            sites.append(self._site(target, use["slot"]))
            for target in self.other_uses[ir]:
                if uses_input(target["ref"]):
                    pointer = target["pointer"] + ("/value" if target["kind"] == "output_binding" else "")
                    resolve_pointer(self.raw, pointer)
                    sites.append({"pointer": pointer, "role": target["kind"]})
        else:
            info = self.engine.ops[operation]
            scope = {"position": deepcopy(info["position"]), "member_scope": None if info["scope"] is None else list(info["scope"])}
            if assessment["node_kind"] == "acquisition_output":
                origin = "acquisition_result"
                target = self.by_raw.get((ir, info["raw_op"]))
                if target:
                    sites.append({"pointer": target["pointer"] + "/output", "role": "acquired_result"})
                if self._consumers is None:
                    from .input_assessments import _reference_index, _consumer_index
                    nodes, refs, _, _ = _reference_index(self.engine)
                    self._consumers = (nodes, _consumer_index(self.engine, nodes, refs))
                nodes, consumers = self._consumers
                node_id = nodes[("op_output", ir, operation, slot)]
                for consumer, used_slot, _ in consumers(node_id)[0]:
                    use_info = self.engine.ops[consumer]
                    use_target = self.by_raw.get((use_info["position"]["instruction_id"], use_info["raw_op"]))
                    if use_target:
                        downstream.append(self._record_site(use_target, use_info, used_slot, "downstream_result_use"))
            elif info["raw_op"] is not None:
                target = self.by_raw[(ir, info["raw_op"])]
                sites.append(self._record_site(target, info, slot))
                ref = self.engine.slots(operation).get(slot, (None,))[0]
                if ref and ref["kind"] == "input":
                    cfg_pointer += json_pointer("inputs", ref["index"])
            else:
                origin = "processing_observation"
                ref = self.engine.slots(operation).get(slot, (None,))[0]
                for target in self.operations_by_ir[ir]:
                    if target["instruction_id"] != ir or tuple(target["segment_path"]) != info["segment"]:
                        continue
                    for use in self.uses[(ir, tuple(target["raw_path"]))]:
                        if use["ref"] == ref:
                            sites.append(self._site(target, use["slot"], "observed_context_supplier"))
                    if ref and ref["kind"] == "local" and target["value"].get("output") == ref["name"]:
                        sites.append({"pointer": target["pointer"] + "/output", "role": "observed_acquisition_or_result"})
                if not sites:
                    sites.append({"pointer": json_pointer("ir_semantics", ir, *info["segment"]), "role": "observed_processing_context"})
        sites = list({canonical_sha256(x):x for x in sites}.values())
        downstream = list({canonical_sha256(x):x for x in downstream}.values())
        spans = self._sources(sites, ir)
        value = {"cfg_pointer": cfg_pointer, "raw_annotation_sites": sites,
            "wire_annotation_sites": list({canonical_sha256(v):v for x in sites if (v := self._wire(x))}.values()),
            "metadata_binding_sites": metadata_sites,
            "source_spans": spans, "source_resolution": "direct_span" if any(x["evidence_origin"] == "direct" for x in spans) else "inherited_span" if spans else "annotation_only",
            "generated_origin": origin, "scope": scope, "downstream_use_sites": downstream,
            "reason": "Coordinates locate the selected actual use and genuine source evidence; no source columns, executable patch, or deletion of generated observations is inferred."
                if spans else "The selected material supplies no source span for this use; exact CFG/annotation coordinates remain available without a fabricated source location."}
        self._locations[identity] = value
        return deepcopy(value)

    def projection(self, assessment):
        if assessment["node_kind"] != "acquisition_output":
            return None
        response = assessment["operation_id"]
        rows = []
        receipt = self.engine.contracts.receipt
        if receipt is not None:
            from .input_contract_review import reviewed_acquisition_projections
            for link in self.engine.index.links.values():
                if link["kind"] != "request_response" or link["target"] != response:
                    continue
                request = self.engine.ops[link["source"]]; received = self.engine.ops[response]
                rows.extend(reviewed_acquisition_projections(receipt, request["position"]["instruction_id"], list(request["raw_op"]), received["position"]["instruction_id"], list(received["raw_op"])))
        supported = []
        accepted = False
        for relation in rows:
            accepted_relation = relation["decision"]["status"] == "accepted"
            accepted = accepted or accepted_relation
            capability = relation["capability"]
            returned = capability["returned_range"]
            # Exact-only: root capability grants no arbitrary descendant masks.
            exact = [r for r in assessment["ranges"] if r["status"] == "required" and r["property"] == returned["property"] and r["path"] == returned["path"] and not r["excluded_paths"]]
            uncertainty = any(r["status"] == "unresolved" and overlaps(r["path"], returned["path"]) for r in assessment["ranges"])
            target = self.by_raw[(relation["request"]["instruction_id"], tuple(relation["request"]["raw_path"]))]
            request_site = self._site(target, capability["selection_input_index"], "projection_parameter_operand")
            supported.append({**deepcopy(relation), "request_operand_location": request_site,
                "selection_parameter_path": deepcopy(capability["selection_parameter_path"]),
                "selected_supported_range": deepcopy(returned) if accepted_relation and exact and not uncertainty else None,
                "selection_reason": ("The exact reviewed returned range matches a completed required range." if exact and not uncertainty else "The reviewed capability is retained, but no exact completed result selection is established; no descendant or union projection is inferred.")
                    if accepted_relation else "This projection claim is not accepted: " + relation["decision"]["reason"]})
        return {"status": "established" if accepted else "unestablished", "capabilities": supported,
            "reason": "Reviewed capabilities describe only the exact listed request/response selection relations; no query, new argument value or combined mask is constructed."
                if accepted else "No accepted reviewed projection relation is supplied for this exact acquisition pair. Any rejected or unresolved authored claims retain their decisions below. This does not prove that the interface is incapable of projection."}

    def enrich(self, assessments):
        for assessment in assessments:
            assessment["location"] = self.location(assessment)
            assessment["retrieval_projection"] = self.projection(assessment)
            for row in assessment["ranges"]:
                row["modification"], row["modification_limit"] = assessed_modification(assessment, row)
        return assessments
