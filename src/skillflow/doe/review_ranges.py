"""Resolve review claims against selected operation occurrences and finite information scopes."""
from copy import deepcopy
from collections import defaultdict
from typing import Literal

from pydantic import model_validator

from skillflow.common.recording import canonical_sha256
from skillflow.common.source_evidence import json_pointer
from skillflow.propagation.contracts.input_requirements import InformationRequirement
from skillflow.propagation.contracts.values import Index, StrictSpec, Text
from .input_contracts import covers, overlaps
from .source_input_findings import _validate_pair, source_operation_targets


class FindingRange(StrictSpec):
    operation: Text
    role: Literal["argument", "response", "receiver"]
    information: InformationRequirement
    input_index: Index | None = None

    @model_validator(mode="after")
    def coordinates(self):
        if (self.role == "argument") != (self.input_index is not None):
            raise ValueError("Only an argument range must identify its actual input index.")
        return self


def _within(left, right):
    return left == right or left.startswith(right + "/") or right.startswith(left + "/")


def overlap_information(a, b):
    if not overlaps(a["path"], b["path"]):
        return False
    if any(covers(path, b["path"]) for path in a.get("excluded_paths", [])) or any(
            covers(path, a["path"]) for path in b.get("excluded_paths", [])):
        return False
    for parent, child in ((a, b), (b, a)):
        depth = len(child["path"]) - len(parent["path"])
        if parent["property"] == "presence" and depth > 0:
            return False
        if parent["property"] in {"shape", "cardinality"} and depth > 1:
            return False
    return a["property"] == "value" or b["property"] == "value" or a["property"] == b["property"]


class FindingRanges:
    """Use repair pointers for routing; resolve precise claims using actual operands."""

    def __init__(self, inventory, targets, cfg, raw, mapping):
        self.targets = targets
        self.layouts = {row["obligation_id"]: row for row in inventory["contracts"]}
        self.obligations = {row["id"]: row for row in inventory["obligations"]}
        self.operations = source_operation_targets(cfg=cfg, raw_annotation=raw, mapping=mapping) if cfg and raw else {}
        pairs = defaultdict(dict)
        for entries in self.operations.values():
            for entry in entries:
                op = entry["value"]
                if op["op"] in {"deliver", "receive"} and op.get("request_id"):
                    key = (entry["instruction_id"], tuple(entry.get("scope_path") or []), op["request_id"])
                    pairs[key][entry["pointer"]] = entry
        self.paired = {}
        for candidates in pairs.values():
            entries = list(candidates.values())
            if len(entries) == 2:
                self.paired.update({e["pointer"]: entries for e in entries})
        self.cfg_sites = {ir["id"]: "cfg:" + json_pointer("blocks", bid, "instructions", number)
                          for bid, block in (cfg or {}).get("blocks", {}).items()
                          for number, ir in enumerate(block["instructions"])}
        # A repair pointer can already name a required field of a tool interface.
        # Its operand and information property come from the compiled declaration.
        self.interface_fields = defaultdict(list)
        for key, obligation in self.obligations.items():
            if obligation.get("kind") != "tool":
                continue
            ref = {k: obligation[k] for k in ("instruction_id", "raw_path")}
            bases = {p for p in targets[key] if not p.startswith("cfg:")}
            bases.add("annotation:" + obligation["raw_pointer"].rsplit("/", 1)[0])
            for i, item in enumerate(self.layouts[key].get("inputs", [])):
                for j, row in enumerate(item["required"]):
                    information = {k: row["information"][k] for k in ("property", "path")}
                    subject = {"role": "argument", "input_index": item["input_index"], "information": information}
                    for base in bases:
                        self.interface_fields[f"{base}/input_contract/inputs/{i}/required/{j}"].append((ref, subject))

    def resolve(self, finding):
        if not finding.get("affected_ranges"):
            targets = finding.get("target_ids", [])
            if (finding.get("domain") == "annotation" and finding.get("source_refs") and targets
                    and all(t in self.interface_fields for t in targets)):
                return [r for t in targets for r in self.interface_fields[t]]
            return []
        result = []
        for row in finding.get("affected_ranges", []):
            subject = FindingRange.model_validate(row).model_dump(mode="json", exclude_none=True)
            entries = self.operations.get(subject["operation"], [])
            if not entries:
                raise ValueError("An affected range must locate an actual selected operation.")
            _validate_pair(entries)
            role = subject["role"]
            if not all(any(_within(target, subject["operation"]) or _within(target, self.cfg_sites[e["instruction_id"]])
                           for target in finding["target_ids"]) for e in entries):
                raise ValueError("Affected operation is outside this finding's repair targets.")
            if len(entries) == 1:
                entries = self.paired.get(entries[0]["pointer"], entries)
                _validate_pair(entries)
            for entry in entries:
                ref = {key: deepcopy(entry[key]) for key in ("instruction_id", "raw_path")}
                spec = entry["value"]
                if role == "argument":
                    if not 0 <= subject["input_index"] < len(spec.get("inputs", [])):
                        raise ValueError("Affected argument is outside the operation's input slots.")
                elif role == "receiver":
                    if spec["op"] not in {"receive", "deliver"}:
                        raise ValueError("Affected receiver must locate an actual request or response boundary.")
                elif spec["op"] == "deliver" and len(entries) == 2:
                    continue
                elif spec.get("output") is None:
                    raise ValueError("Affected response must locate an operation with a result.")
                result.append((ref, {k: deepcopy(v) for k, v in subject.items() if k != "operation"}))
        return result

    def barriers(self, findings):
        rows = {}
        for finding in findings:
            for ref, subject in self.resolve(finding):
                body = {"record_path": finding.get("id") or finding["target_ids"][0],
                        "code": "review_information_range", "domain": "operation", "operation_refs": [ref],
                        "range": subject, "reason": finding["explanation"], "resolution": finding["suggestion"],
                        "source_refs": deepcopy(finding["source_refs"])}
                identity = "review_barrier_" + canonical_sha256(body)[:20]
                rows[identity] = {"id": identity, **body}
        return [rows[k] for k in sorted(rows)]

    def source_consistency(self, normalized, findings, *, mapping, cfg):
        from .source_input_findings import check_source_input_finding_consistency
        check_source_input_finding_consistency(normalized, [f for f in findings if not (
            self.resolve(f) or f.get("sensitivity_entry_gap_id"))], mapping=mapping, cfg=cfg)
        for finding in findings:
            for ref, affected in self.resolve(finding):
                for source in normalized:
                    for usage in source["operation_refs"]:
                        if ref != {k: usage[k] for k in ref}:
                            continue
                        actual = source["actual"]
                        if affected["role"] == "argument":
                            conflict = (actual["kind"] == "input_range" and actual["input_index"] == affected["input_index"]
                                        and overlap_information({"path": actual["path"], "property": "value"}, affected["information"]))
                        elif affected["role"] == "response":
                            conflict = any(i["kind"] == "output" and overlap_information(i, affected["information"])
                                           for i in usage["impacts"])
                        else:
                            conflict = True
                        if conflict:
                            raise ValueError("Source-input finding conflicts with the reviewed operation range at "
                                             + str(ref) + ": " + str(affected))

    def conflicts(self, check, finding):
        if finding.get("input_projection_scope_ids") or finding.get("input_contract_obligation_id") or (finding.get("sensitivity_entry_gap_id") and not finding.get("affected_ranges")):
            return []
        if finding.get("domain") not in {"cfg", "annotation"}:
            return []
        obligation = self.obligations[check["obligation_id"]]
        scopes = self.layouts[obligation["id"]]["scopes"]
        accepted = {key for row in check["scope_checks"] if row["status"] == "accepted" for key in row["scope_ids"]}
        if check["status"] != "accepted":
            scopes = [s for s in scopes if s["id"] in accepted]
        matching = self.resolve(finding)
        if matching:
            return [s["id"] for s in scopes if any(ref["instruction_id"] == obligation["instruction_id"]
                    and ref["raw_path"] == obligation["raw_path"] and self._intersects(s, subject, self.layouts[obligation["id"]]["scopes"])
                    for ref, subject in matching)]
        return [s["id"] for s in scopes if any(_within(site, target) for site in self.targets[obligation["id"]]
                                                 for target in finding.get("target_ids", []))]

    @staticmethod
    def _intersects(scope, subject, scopes):
        role, info = subject["role"], subject["information"]
        if role == "receiver":
            # The receiver's identity is independent of the payload contract.
            return False
        if role == "response":
            return "output" in scope and overlap_information(info, scope["output"])
        if scope.get("input_index") != subject["input_index"]:
            return False
        if "information" in scope:
            return overlap_information(info, scope["information"])
        if scope["kind"] == "remainder":
            excluded = [s["information"]["path"] for s in scopes if "information" in s
                        and s.get("input_index") == scope["input_index"] and s.get("output") == scope.get("output")
                        and s["information"]["property"] == "value"]
            return not any(covers(path, info["path"]) for path in excluded)
        return False


class AssessmentRangeLimits:
    """Use the exact assessed payload slot and version for each DOE comparison."""
    def __init__(self, demand):
        self.rows = defaultdict(list)
        local = {d["id"] for d in demand.get("diagnostics", []) if d["code"] == "input_contract_review_validation"}
        if local:
            for item in demand["input_assessments"]:
                if item["node_kind"] == "op_input":
                    for row in item["ranges"]:
                        refs = local.intersection(row["diagnostic_refs"])
                        if refs and row["status"] == "unresolved":
                            self.rows[item["operation_id"]].append((item["input_index"], set(item["data_ids"]), row, refs))

    def for_boundary(self, payloads):
        return {ref for p in payloads for _, _, _, refs in self.rows.get(p["operation_id"], ()) for ref in refs}

    def for_signal(self, operation, slot, data, signal):
        from .sensitivity_engine import demand_overlap
        return {ref for index, versions, row, refs in self.rows.get(operation, ()) if slot == index and data in versions
                and demand_overlap(signal, {**row, "each": False, "conservative": False}) != "none" for ref in refs}
