"""Read-only size accounting and reversible presentation experiments.

This does not import an analysis runner, invoke a model, replay a run, or edit
historical inputs. Only receipts in this script's directory are written.
"""
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
PROJECT = BASE.parents[3]
RUN = PROJECT / "experiments/doe/runs/document-guided-ga4-input-necessity-corrected-r2-high-20261112-183209"


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write(name, value):
    (BASE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def field_sizes(value):
    # The exact contribution includes quoted key, colon and comma. The final
    # brace adjustment makes the sum exactly equal to the whole object size.
    entries = [{"key": key, "value_chars": len(compact(item)),
        "key_separator_chars": len(compact(key)) + 2,
        "chars_with_key_separator": len(compact(key)) + 2 + len(compact(item))}
        for key, item in value.items()]
    return {"total_chars": len(compact(value)), "fields": entries,
        "outer_object_adjustment": 1 if value else 2}


def record_table(rows):
    """Retain every exact key-set, absent/null distinction and record order."""
    shapes = []
    indexes = {}
    encoded = []
    for row in rows:
        shape = tuple(row)
        if shape not in indexes:
            indexes[shape] = len(shapes)
            shapes.append(list(shape))
        encoded.append([indexes[shape], *row.values()])
    return {"columns": shapes, "rows": encoded}


def expand_record_table(table):
    return [dict(zip(table["columns"][row[0]], row[1:])) for row in table["rows"]]


def inventory_tables(inventory):
    result = deepcopy(inventory)
    rows = []
    for obligation in result["obligations"]:
        obligation["scopes"] = record_table(obligation["scopes"])
        rows.append(obligation)
    result["obligations"] = record_table(rows)
    return result


def expand_inventory_tables(inventory):
    result = deepcopy(inventory)
    result["obligations"] = expand_record_table(result["obligations"])
    for obligation in result["obligations"]:
        obligation["scopes"] = expand_record_table(obligation["scopes"])
    return result


def global_scope_inventory(inventory):
    """Share scope column shapes across the inventory; keep rows in obligations."""
    result = deepcopy(inventory)
    shapes, indexes = [], {}
    for obligation in result["obligations"]:
        rows = []
        for scope in obligation["scopes"]:
            shape = tuple(scope)
            if shape not in indexes:
                indexes[shape] = len(shapes)
                shapes.append(list(shape))
            rows.append([indexes[shape], *scope.values()])
        obligation["scopes"] = rows
    result["scope_columns"] = shapes
    result["obligations"] = record_table(result["obligations"])
    return result


def expand_global_scope_inventory(inventory):
    result = deepcopy(inventory)
    shapes = result.pop("scope_columns")
    result["obligations"] = expand_record_table(result["obligations"])
    for obligation in result["obligations"]:
        obligation["scopes"] = [dict(zip(shapes[row[0]], row[1:])) for row in obligation["scopes"]]
    return result


def exact_subtree_dictionary(value, minimum=60):
    """Experimental general DAG encoding; exact JSON values, no schema inference.

    All containers are wrapped as typed arrays, so arbitrary user/source literal
    keys cannot collide with a reference marker. This is a size experiment only,
    not a recommended model-facing format.
    """
    counts = Counter()
    originals = {}
    def visit(item):
        if isinstance(item, (dict, list)):
            key = compact(item)
            counts[key] += 1
            originals[key] = item
            for child in item.values() if isinstance(item, dict) else item:
                visit(child)
    visit(value)
    selected = {key for key, count in counts.items() if count > 1 and len(key) >= minimum}
    ids = {key: index for index, key in enumerate(sorted(selected, key=lambda s: (len(s), s)))}
    def encode(item, define=None):
        if isinstance(item, (dict, list)):
            key = compact(item)
            if key in ids and key != define:
                return ["ref", ids[key]]
            if isinstance(item, dict):
                return ["object", [[key, encode(child)] for key, child in item.items()]]
            return ["array", [encode(child) for child in item]]
        return ["atom", item]
    definitions = [encode(originals[key], define=key) for key in ids]
    encoded = {"definitions": definitions, "root": encode(value)}
    def decode(item):
        tag, body = item
        if tag == "ref": return decode(definitions[body])
        if tag == "object": return {key: decode(child) for key, child in body}
        if tag == "array": return [decode(child) for child in body]
        if tag == "atom": return body
        raise ValueError(tag)
    assert decode(encoded["root"]) == value
    return encoded


def walk_values(value, pointer=""):
    yield pointer, value
    if isinstance(value, dict):
        for key, item in value.items():
            yield from walk_values(item, pointer + "/" + key.replace("~", "~0").replace("/", "~1"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk_values(item, pointer + "/" + str(index))


def main():
    review_path = RUN / "review/prompt.txt"
    delivery_path = next((RUN / "transport/review").glob("*/prompt.txt"))
    prompt = review_path.read_text(encoding="utf-8")
    delivery = delivery_path.read_text(encoding="utf-8")
    assert len(delivery) == 1079505
    assert delivery.endswith(prompt)
    prefix, rest = prompt.split("\nINPUT_JSON\n", 1)
    payload_text, source = rest.split("\nCOMPLETE SOURCE\n", 1)
    instructions, response = prefix.split("\nRESPONSE FORMAT\n", 1)
    payload = json.loads(payload_text)
    assert compact(payload) == payload_text
    assert len(delivery) == len(delivery) - len(prompt) + len(instructions) + len(response) + len(payload_text) + len(source) + 46
    inventory = payload["input_contract_inventory"]
    material = json.loads((RUN / "review/inputs.json").read_text(encoding="utf-8"))
    contributions = {key: field_sizes(payload[key]) for key in ("annotation", "cfg", "input_contract_inventory", "runtime_contract", "task")}
    duplicates = defaultdict(list)
    for pointer, value in walk_values(payload):
        if isinstance(value, (dict, list)):
            key = compact(value)
            if len(key) >= 50:
                duplicates[key].append(pointer)
    duplicate_rows = sorted([{"chars": len(value), "occurrences": len(paths),
        "gross_repetition_chars": len(value) * (len(paths) - 1), "example": value[:200], "paths": paths}
        for value, paths in duplicates.items() if len(paths) > 1],
        key=lambda row: row["gross_repetition_chars"], reverse=True)
    variants = []
    for name, encode, decode in [("per_obligation_scope_tables", inventory_tables, expand_inventory_tables),
                                 ("shared_scope_columns", global_scope_inventory, expand_global_scope_inventory)]:
        encoded = encode(inventory)
        assert decode(encoded) == inventory
        transformed = deepcopy(payload)
        transformed["input_contract_inventory"] = encoded
        candidate_chars = len(delivery) - len(payload_text) + len(compact(transformed))
        variants.append({"name": name, "inventory_chars": len(compact(encoded)),
            "full_delivery_chars_before_format_instructions": candidate_chars,
            "saved_chars": len(delivery) - candidate_chars,
            "headroom_before_format_instructions": 1048576 - candidate_chars,
            "decoded_inventory_equal": True, "all_obligation_ids_equal": True,
            "all_scope_ids_equal": True, "source_section_sha256": sha(source),
            "source_section_unchanged": True})
        write(name + ".json", encoded)
    # Attribute strings/keys and literal duplicate appearances without adding
    # overlapping potential savings into an invalid total.
    strings = Counter()
    keys = Counter()
    string_sizes = Counter()
    for pointer, value in walk_values(payload):
        if isinstance(value, str):
            strings[value] += 1
            string_sizes[pointer.split("/")[1]] += len(compact(value))
        elif isinstance(value, dict):
            keys.update(value.keys())
    scope_fields = defaultdict(int)
    scopes = [scope for row in inventory["obligations"] for scope in row["scopes"]]
    for row in scopes:
        for key, value in row.items(): scope_fields[key] += len(compact(value))
    result = {"status": "measured_from_frozen_request", "historical_run": str(RUN),
        "delivery_chars": len(delivery), "review_prompt_chars": len(prompt), "limit": 1048576,
        "excess": len(delivery) - 1048576, "delivery_sha256": sha(delivery), "prompt_sha256": sha(prompt),
        "sections": {"transport_envelope": len(delivery) - len(prompt), "instructions": len(instructions),
            "response_format": len(response), "input_json": len(payload_text), "complete_source": len(source),
            "section_delimiters": 46},
        "payload": field_sizes(payload), "components": contributions,
        "local_audit_material_chars": len((RUN / "review/inputs.json").read_text(encoding="utf-8")),
        "local_metadata_not_all_delivered": True,
        "actual_fragment_count": len(payload["fragments"]), "actual_observation_count": len(payload["observations"]),
        "source_files": len(material["files"]), "raw_source_codepoints": sum(len(s) for s in material["files"].values()),
        "source_section_sha256": sha(source), "obligations": len(inventory["obligations"]),
        "scopes": len(scopes), "scope_kind_counts": dict(Counter(row["kind"] for row in scopes)),
        "scope_field_value_chars": dict(scope_fields), "exact_duplicate_subtrees_top": duplicate_rows[:30],
        "duplicate_potential_savings_are_overlapping": True,
        "string_value_chars_by_payload_component": dict(string_sizes),
        "key_occurrences": keys.most_common(25),
        "repeated_strings_top": sorted([{"value": s, "count": n, "gross_repetition_chars": len(compact(s)) * (n-1)}
            for s,n in strings.items() if n>1 and len(s)>15], key=lambda row:row["gross_repetition_chars"],reverse=True)[:25],
        "reversible_inventory_variants": variants,
        "limitations": ["Candidate delivery sizes exclude the new format explanation and protocol identity length changes.",
            "No model quality or acceptance is established by JSON roundtrip equality.",
            "No source, contract, scope or supplied literal value was truncated or omitted.",
            "These are isolated formatting measurements, not a historical analysis replay."]}
    write("request-size-breakdown.json", result)
    print(json.dumps({key: result[key] for key in ("delivery_chars", "sections", "obligations", "scopes", "reversible_inventory_variants")}, indent=2))


if __name__ == "__main__":
    main()
