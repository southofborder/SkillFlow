"""Passive lossless-pair inventory of one rejected saved response, never a repair.

This reads the current run only. Objects remain ordered pairs throughout response
forensics. No pair table is merged, accepted, expanded, or written into the run.
"""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

from skillflow.document_guided.fragment_wire import output_wire_instructions

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RUN = ROOT / "experiments/doe/runs/document-guided-ga4-processing-shared-high-20261116-225414"


class ObjectPairs(list):
    pass


def compact_pairs(value):
    if isinstance(value, ObjectPairs):
        return "{" + ",".join(json.dumps(key, ensure_ascii=False) + ":" + compact_pairs(child)
                              for key, child in value) + "}"
    if isinstance(value, list):
        return "[" + ",".join(compact_pairs(child) for child in value) + "]"
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def unique_fields(value):
    """Forensic access to one already proven unique object; never merge tables."""
    assert isinstance(value, ObjectPairs)
    assert len({key for key, _ in value}) == len(value)
    return {key: child for key, child in value}


def inventory(value):
    duplicates, refs = [], Counter()
    def walk(item, pointer):
        if isinstance(item, ObjectPairs):
            duplicates.extend({"path": pointer, "key": key, "count": count}
                              for key, count in Counter(key for key, _ in item).items() if count > 1)
            if len(item) == 1 and item[0][0] == "$ref":
                refs[str(item[0][1])] += 1
            for occurrence, (key, child) in enumerate(item):
                walk(child, pointer + "/" + key.replace("~", "~0").replace("/", "~1") + "#" + str(occurrence))
        elif isinstance(item, list):
            for index, child in enumerate(item):
                walk(child, pointer + "/" + str(index))
    walk(value, "")
    return duplicates, refs


def main():
    calls = RUN / "steps/processing/calls"
    response_file = calls / "a001/response.json"
    saved_bytes = response_file.read_bytes()
    raw = json.loads(saved_bytes.decode("utf-8"))
    root = json.loads(raw, object_pairs_hook=ObjectPairs)
    tables = [value for key, value in root if key == "shared_values"]
    assert len(tables) == 2
    first, second = [unique_fields(table) for table in tables]
    overlap = set(first) & set(second)
    same = sorted(key for key in overlap if compact_pairs(first[key]) == compact_pairs(second[key]))
    unequal = sorted(overlap - set(same))
    duplicates, references = inventory(root)
    payload = next(value for key, value in root if key == "payload")
    _, payload_refs = inventory(payload)
    all_names = set(first) | set(second)
    prompt1 = (calls / "a001/prompt.txt").read_bytes().decode("utf-8")
    prompt2 = (calls / "a002/prompt.txt").read_bytes().decode("utf-8")
    marker = "\nCURRENT_CANDIDATE_AND_DIAGNOSTICS\n"
    context_at = prompt2.rfind(marker) + len(marker)
    context = json.loads(prompt2[context_at:])
    guidance = output_wire_instructions()
    extra_instructions = prompt2[len(prompt1):context_at - len(marker)]
    table_rows = []
    for index, table in enumerate(tables, 1):
        names = [key for key, _ in table]
        table_rows.append({"occurrence": index, "entries": len(table),
            "duplicate_names": {key: count for key, count in Counter(names).items() if count > 1},
            "vN_names": [key for key in names if re.fullmatch(r"v(?:0|[1-9][0-9]*)", key)],
            "invalid_vN_name_count": sum(re.fullmatch(r"v(?:0|[1-9][0-9]*)", key) is None for key in names),
            "forensic_pair_preserving_compact_chars": len(compact_pairs(table)),
            "value_pair_fingerprints": {key: hashlib.sha256(compact_pairs(value).encode()).hexdigest()
                                        for key, value in table}})
    result = {"observed_at": datetime.now(timezone.utc).isoformat(),
        "run": RUN.relative_to(ROOT).as_posix(),
        "method": "Saved bytes, lossless object-pairs JSON forensics, and pure output instruction string only. No response expansion, stage validation, backend, model call, or replay.",
        "limits": "Pair-preserving compact lengths retain duplicate members and are forensic text measures, not accepted canonical or expanded JSON sizes. Unequal definitions are exact-value differences, not proven semantic contradictions.",
        "response": {"raw_chars": len(raw), "raw_utf8_bytes": len(raw.encode()),
            "saved_file_bytes": len(saved_bytes), "saved_file_sha256": hashlib.sha256(saved_bytes).hexdigest(),
            "declared_format": next(value for key, value in root if key == "format"),
            "root_member_order": [key for key, _ in root],
            "duplicate_members": duplicates,
            "forensic_pair_preserving_compact_chars": len(compact_pairs(root)),
            "accepted_compact_chars": None, "accepted_expanded_chars": None,
            "root_member_value_chars": [{"key": key, "forensic_pair_preserving_compact_chars": len(compact_pairs(value))}
                                         for key, value in root],
            "tables": table_rows,
            "overlap": {"count": len(overlap), "identical_count": len(same), "unequal_count": len(unequal),
                "identical_keys": same, "unequal_keys": unequal,
                "only_first": sorted(set(first) - set(second)), "only_second": sorted(set(second) - set(first))},
            "reference_object_count": sum(references.values()), "distinct_reference_names": len(references),
            "payload_reference_object_count": sum(payload_refs.values()),
            "payload_reference_names_absent_from_first": sorted(set(payload_refs) - set(first)),
            "payload_reference_names_absent_from_second": sorted(set(payload_refs) - set(second)),
            "all_reference_names_absent_from_both": sorted(set(references) - all_names)},
        "correction": {"initial_prompt_chars": len(prompt1), "correction_prompt_chars": len(prompt2),
            "extra_chars": len(prompt2) - len(prompt1), "initial_prompt_exact_prefix": prompt2.startswith(prompt1),
            "complete_raw_candidate_exact_match": context["candidate"] == raw,
            "candidate_json_string_chars": len(json.dumps(context["candidate"], ensure_ascii=False, separators=(",", ":"))),
            "context_chars": len(prompt2[context_at:]), "context_keys": list(context),
            "diagnostics": context["diagnostics"], "format_examples": context["format_examples"],
            "extra_instructions": extra_instructions,
            "initial_wire_guidance_exact_occurrences": prompt1.count(guidance),
            "correction_wire_guidance_exact_occurrences": prompt2.count(guidance),
            "explicit_vN_grammar_in_output_guidance": "vN" in guidance,
            "explicit_duplicate_key_rule_in_output_guidance": any(word in guidance.lower() for word in ("duplicate", "unique")),
            "joint_processing_correction": "JOINT PROCESSING CORRECTION MATERIAL" in prompt2,
            "output_wire_guidance": guidance},
        "saved_validation": json.loads((calls / "a001/validation.json").read_bytes().decode())}
    target = OUT / "processing-initial-rejected-pair-forensics.json"
    if target.exists():
        raise RuntimeError("Forensic report already exists; preserve it and use a new filename.")
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": target.relative_to(ROOT).as_posix(),
                      "response": {key: result['response'][key] for key in ('raw_chars','root_member_order','reference_object_count','distinct_reference_names','payload_reference_names_absent_from_first','payload_reference_names_absent_from_second','all_reference_names_absent_from_both')},
                      "correction": {key: result['correction'][key] for key in ('initial_prompt_chars','correction_prompt_chars','extra_chars','initial_prompt_exact_prefix','complete_raw_candidate_exact_match','candidate_json_string_chars','context_chars','explicit_vN_grammar_in_output_guidance','explicit_duplicate_key_rule_in_output_guidance')}}))


if __name__ == "__main__":
    main()
