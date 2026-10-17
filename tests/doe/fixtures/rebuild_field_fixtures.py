"""Explicit offline field-tightening fixtures, never a production compatibility reader.

These functions construct new candidates from previously verified receipts. They
never overwrite a source receipt or claim that the reconstructed candidate was
accepted from a model. Source/effect claims are retained while redundant wire
wrappers and program-owned identities are rebuilt.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from skillflow.common.recording import canonical_sha256

from skillflow.common.source_evidence import json_pointer
from skillflow.propagation.contracts.references import cfg_target_from_path
from skillflow.common.source_evidence import resolve_pointer


def rebuild_raw_annotation(old_raw, old_material, *, task=None):
    """Translate the explicitly selected legacy fixture, not arbitrary loader input."""
    if not isinstance(old_raw.get("profiles"), dict) or not isinstance(old_raw.get("transfer_specs"), dict):
        raise ValueError("Field reconstruction requires an explicit legacy candidate")
    if set(old_raw["profiles"]) != set(old_raw["transfer_specs"]):
        raise ValueError("Legacy profile/spec coverage differs")
    units = {row["id"]: row for row in old_material["source_index"]}
    graph_refs = {row["id"]: row["pointer"] for row in old_material["graph_index"]}
    def direct(pointer):
        cur = old_material["cfg"]; parts=[]
        for token in pointer.lstrip("/").split("/") if pointer else []:
            token=token.replace("~1", "/").replace("~0", "~")
            key=int(token) if isinstance(cur,list) else token
            parts.append(key);cur=cur[key]
        return cfg_target_from_path(old_material["cfg"],parts)


    def evidence(value):
        if "file" in value:
            return deepcopy(value)
        basis = value["basis"]
        if basis == "source":
            unit = units[value["ref_id"]]
            return {"file": "skill/" + unit["file"], "start_line": unit["start_line"],
                    "end_line": unit["end_line"], "reason": value["reason"]}
        if basis not in {"cfg", "execution_model"}:
            raise ValueError("Unsupported fixture evidence domain")
        return {**({"target": direct(graph_refs[value["ref_id"]])} if basis == "cfg" else {"rule_id": value["ref_id"]}), "reason": value["reason"]}

    def convert(value):
        if isinstance(value, list):
            return [convert(item) for item in value]
        if not isinstance(value, dict):
            return deepcopy(value)
        result = {}
        for key, item in value.items():
            if key == "evidences":
                result[key] = [evidence(item) for item in item]
            elif key == "task_goals":
                result["demands"] = [{("preserve" if k == "property" else k): convert(v) for k, v in goal.items() if k != "id"} for goal in item]
            else:
                result[key] = convert(item)
        return result

    output = {key: convert(value) for key, value in old_raw.items()
              if key not in {"profiles", "transfer_specs", "task", "demand", "sink_boundaries", "location_evidences"}}
    output.setdefault("demands", [])
    output["demands"] = [row for row in output["demands"] if row["preserve"] not in {"constraint", "prohibit"}]

    output.setdefault("expressions", [])
    output["location_evidences"] = {key: [evidence(item) for item in value]
                                      for key, value in old_raw["location_evidences"].items()}
    output["ir_semantics"] = {}
    for ir, old_spec in old_raw["transfer_specs"].items():
        profile = old_raw["profiles"][ir]
        spec = convert(old_spec)
        spec.pop("precedence", None)
        spec["operator"] = deepcopy(profile["operator"])
        spec["operator_evidences"] = [{"value": row["value"], **evidence(row)}
                                      for row in profile["evidences"] if row["field"] == "operator"]
        def events(items):
            for item in items:
                if item.get("kind") == "for_each":
                    events(item["body"])
                elif item.get("kind") == "processing":
                    events(item["events"])
                else:
                    index = item.pop("effect_index")
                    item["effect"] = None if index is None else profile["effects"][index]
                    item["evidences"] = [] if index is None else [evidence(row)
                        for row in profile["evidences"] if row["field"] == "effects" and row["effect_index"] == index]
        events(spec["events"])
        if not profile["effects"]:
            spec["empty_effect_evidences"] = [evidence(row) for row in profile["evidences"]
                                             if row["field"] == "effects" and row["value"] is None]
        spec.setdefault("sensitivity", [])
        for item in spec["events"]:
            if item.get("kind") == "for_each":
                item.setdefault("sensitivity", [])
        output["ir_semantics"][ir] = spec
    return output


def previous_target_id(target):
    """Find the exact legacy address identity; never use name similarity."""
    if target["domain"] == "cfg":
        return "target_" + hashlib.sha256(target["pointer"].encode()).hexdigest()[:20]
    pointer = json_pointer("transfer_specs", target["instruction_id"], *target["raw_path"])
    return "demand_target_" + hashlib.sha256(pointer.encode()).hexdigest()[:20]



def _scope_identity(value):
    if isinstance(value, dict):
        return {key: _scope_identity(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_scope_identity(item) for item in value]
    if isinstance(value, str) and value.startswith("transfer:["):
        parts = json.loads(value[len("transfer:"):])
        if not parts or not isinstance(parts[0], str) or len(parts[0]) != 64:
            raise ValueError("Unexpected recorded symbolic-scope identity")
        return "transfer:" + json.dumps(["<frozen-rule-identity>", *parts[1:]], ensure_ascii=False, separators=(",", ":"))
    return value


def data_addresses(facts):
    """Build acyclic provenance addresses for explicit cross-version fixtures.

    Description edges may point back to a parent; origin inputs/part_of do not.
    No field is sorted here to conceal an operation or parameter order change.
    Collisions are rejected instead of silently merging equal-looking objects.
    """
    data = {row["id"]: row for row in facts["data"]}
    result, active = {}, set()
    def address(identity):
        if identity in result:
            return result[identity]
        if identity in active or identity not in data:
            raise ValueError("Cannot establish an acyclic fixture Data correspondence")
        active.add(identity)
        row, origin = data[identity], data[identity]["origin"]
        if origin["part_of"] is not None:
            key = ["part", address(origin["part_of"]), _scope_identity(origin["path"])]
        else:
            content = row["content"]
            form = content["form"]
            if form == "known_parts" and not content["parts_complete"]:
                shape = {"form": "opaque"}
            elif form == "known_parts":
                shape = {"form": form, "paths": [part["path"] for part in content["parts"]]}
            else:
                shape = {key: value for key, value in content.items() if key not in {"base", "updates"}}
                if "updates" in content:
                    shape["updates"] = [part["path"] for part in content["updates"]]
            key = ["value", origin["at"], origin["acquired_from"],
                   [address(item) for item in origin["inputs"]], _scope_identity(shape)]
        active.remove(identity)
        result[identity] = "fixture_data_" + canonical_sha256(key)
        return result[identity]
    for identity in data:
        address(identity)
    if len(set(result.values())) != len(result):
        raise ValueError("Ambiguous fixture Data correspondence; identities must not be merged")
    return result


def canonical_facts(facts):
    """Normalize generated identities only; preserve business operation order."""
    addresses = data_addresses(facts)
    def normalize(value, path=()):
        if isinstance(value, str):
            return addresses.get(value, _scope_identity(value))
        if isinstance(value, list):
            values = [normalize(item, (*path, index)) for index, item in enumerate(value)]
            if value and all(isinstance(item, str) and item in addresses for item in value):
                # Provenance inputs encode actual parameter order. Other arrays
                # made solely of Data IDs are candidate sets in this wire type.
                return values if path[-2:] == ("origin", "inputs") else sorted(values)
            return values
        if isinstance(value, dict):
            return {key: normalize(item, (*path, key)) for key, item in value.items()}
        return value
    value = normalize(facts)
    value.pop("schema_version")
    value.pop("execution_model")
    value["actions"] = {ir: {"operator": row["operator"]} for ir, row in value["actions"].items()}
    value["data"] = {row["id"]: row for row in value["data"]}
    return value, addresses


def compare_forward_facts(before, after):
    left, old_addresses = canonical_facts(before)
    right, new_addresses = canonical_facts(after)
    if left != right:
        changed = [key for key in left.keys() | right.keys() if left.get(key) != right.get(key)]
        raise ValueError("Field reconstruction changed forward relationships: " + ", ".join(sorted(changed)))
    inverse = {address: identity for identity, address in new_addresses.items()}
    return {identity: inverse[address] for identity, address in old_addresses.items()}


def canonical_demand(result, facts=None, target_map=None):
    """Compare demand relationships across generated-ID changes, not just counts."""
    addresses = data_addresses(facts) if facts is not None else {}
    targets = target_map or {}
    def normalize(value, path=()):
        if isinstance(value, str):
            return targets.get(value, addresses.get(value, _scope_identity(value)))
        if isinstance(value, list):
            items = [normalize(item, (*path, index)) for index, item in enumerate(value)]
            if path and path[-1] == "data_ids":
                return sorted(items)
            if value and all(isinstance(item, str) and item in addresses for item in value):
                return sorted(items)
            return items
        if isinstance(value, dict):
            return {key: normalize(item, (*path, key)) for key, item in value.items()}
        return value
    value = normalize(result)
    value.pop("schema_version")
    value["goals"] = sorted([{key: item for key, item in goal.items() if key != "id"}
                             for goal in value["goals"]], key=canonical_sha256)
    derivations = value["derivations"]
    identities = {identity: "fixture_demand_" + canonical_sha256({key: item for key, item in row.items()
                  if key not in {"id", "parents", "rules"}}) for identity, row in derivations.items()}
    if len(set(identities.values())) != len(identities):
        raise ValueError("Ambiguous demand correspondence cannot conceal merged uses")
    value["derivations"] = {identities[identity]: {**{key: item for key, item in row.items()
                            if key not in {"id", "parents"}}, "parents": sorted(identities[p] for p in row["parents"])}
                            for identity, row in derivations.items()}
    for sink in value["sinks"]:
        for name in ("demanded_information", "conservative_retention"):
            sink[name] = sorted(identities[identity] for identity in sink[name])
    return value

def canonical_sensitivity(result, facts):
    """Normalize compact and legacy result coordinates for an offline comparison.

    Only deterministic IDs and the deliberately removed duplicate row fields are
    projected. Every signal, demand, parent, range, conclusion and limitation is
    retained; duplicate fields in legacy rows must agree with their owners.
    """
    addresses = data_addresses(facts)
    def normalize(value):
        if isinstance(value, str):
            return addresses.get(value, _scope_identity(value))
        if isinstance(value, list):
            values = [normalize(item) for item in value]
            return sorted(values) if value and all(isinstance(v, str) and v in addresses for v in value) else values
        if isinstance(value, dict):
            return {key: normalize(item) for key, item in value.items()}
        return value
    value = normalize(result)
    value.pop("schema_version")
    groups = value["derivations"]
    maps = {}
    for group, rows in groups.items():
        excluded = {"id", "parents", "rules"}
        maps[group] = {key: "fixture_" + group + "_" + canonical_sha256({
            field: item for field, item in row.items() if field not in excluded}) for key, row in rows.items()}
        if len(set(maps[group].values())) != len(rows):
            raise ValueError("Ambiguous sensitivity comparison derivation")
        groups[group] = {maps[group][key]: {
            **{field: item for field, item in row.items() if field not in {"id", "parents"}},
            "parents": sorted(maps[group][parent] for parent in row["parents"])} for key, row in rows.items()}
    duplicates = ("data_id", "label", "property", "path", "excluded_paths", "relation", "declaration_id")
    for sink in value["sinks"]:
        for row in sink["data_reviews"]:
            signal_id = maps["sensitivity"][row["derivation_id"]]
            signal = groups["sensitivity"][signal_id]
            for field in duplicates:
                if field in row and row.pop(field) != signal[field]:
                    raise ValueError("Legacy review disagrees with its authoritative derivation")
            if "limitations" in row and row.pop("limitations") != sink["limitations"]:
                raise ValueError("Legacy review disagrees with its authoritative sink limitations")
            row["derivation_id"] = signal_id
            row["demand_refs"] = sorted(maps["demand"][key] for key in row["demand_refs"])
            row["id"] = "fixture_review_" + canonical_sha256([sink["id"],row["operation_id"],row["input_index"],signal_id])
        sink["data_reviews"].sort(key=lambda row: row["id"])
    return value
