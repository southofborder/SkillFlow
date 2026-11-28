"""Read-only old-request regression of the new renderer, never a run replay."""
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
from time import perf_counter

PROJECT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT))
from skillflow.common.prompt_format import compact_json
from skillflow.common.recording import implementation_provenance
from skillflow.document_guided.source_review import build_source_review_prompt, SHARED_VIEW
from skillflow.document_guided.review_display import expand_review_payload
from tools.doe.document_guided_client import ENVELOPE, MAX_INPUT_CHARS

BASE = Path(__file__).resolve().parent
RUN = PROJECT / "experiments/doe/runs/document-guided-ga4-input-necessity-corrected-r2-high-20261112-183209"


def sha(value):
    return hashlib.sha256(value).hexdigest()


def parsed(prompt):
    return json.loads(prompt.split("\nINPUT_JSON\n", 1)[1].split("\nCOMPLETE SOURCE\n", 1)[0])


def main():
    baseline = json.loads((BASE / "preserved-r2-artifact-hashes.json").read_text(encoding="utf-8"))
    before = {name: sha((RUN / name).read_bytes()) for name in baseline["files"]}
    assert before == baseline["files"]
    material = json.loads((RUN / "review/inputs.json").read_bytes())
    old_prompt = (RUN / "review/prompt.txt").read_bytes().decode("utf-8")
    assert build_source_review_prompt(material) == old_prompt
    original_material = deepcopy(material)
    revised = deepcopy(material)
    revised["prompt_view"] = SHARED_VIEW
    started = perf_counter()
    prompt = build_source_review_prompt(revised)
    render_seconds = perf_counter() - started
    assert material == original_material
    display = parsed(prompt)
    expanded = expand_review_payload(display)
    logical = parsed(old_prompt)
    assert compact_json(expanded) == compact_json(logical)
    old_source = old_prompt.split("\nCOMPLETE SOURCE\n", 1)[1]
    new_source = prompt.split("\nCOMPLETE SOURCE\n", 1)[1]
    assert new_source.encode("utf-8") == old_source.encode("utf-8")
    obligations = logical["input_contract_inventory"]["obligations"]
    scopes = [scope for row in obligations for scope in row["scopes"]]
    source_files = {name: sha(content.encode("utf-8")) for name, content in material["files"].items()}
    old_delivery, delivery = ENVELOPE + old_prompt, ENVELOPE + prompt
    assert len(old_delivery) == 1079505 and len(delivery) < MAX_INPUT_CHARS
    assert len(delivery) < 0.85 * len(old_delivery)
    after = {name: sha((RUN / name).read_bytes()) for name in baseline["files"]}
    assert before == after
    result = {"status": "passed", "historical_analysis_or_replay_executed": False,
        "new_model_calls": 0, "old_prompt_byte_identical": True,
        "new_view": SHARED_VIEW, "display_format": display["format"],
        "original_delivery_codepoints": len(old_delivery), "new_delivery_codepoints": len(delivery),
        "saved_codepoints": len(old_delivery) - len(delivery), "remaining_headroom": MAX_INPUT_CHARS - len(delivery),
        "transport_limit_unchanged": MAX_INPUT_CHARS, "render_seconds": render_seconds,
        "exact_serialized_payload_roundtrip": True, "source_section_byte_identical": True,
        "source_section_sha256": sha(new_source.encode("utf-8")), "source_file_sha256": source_files,
        "all_logical_documents_retained": list(logical), "obligation_count": len(obligations),
        "scope_count": len(scopes), "obligation_kinds": dict(Counter(row["kind"] for row in obligations)),
        "every_obligation_scope_identity_order_and_descriptor_retained": True,
        "shared_definitions": len(display["shared_values"]), "record_column_sets": len(display["record_columns"]),
        "original_artifact_hashes_unchanged": after, "implementation_sha256": implementation_provenance()["sha256"],
        "new_delivery_sha256": sha(delivery.encode("utf-8")),
        "note": "Only deterministic prompt rendering/expansion was performed against a read-only saved request. No model answer, propagation, DOE or historical replay was requested."}
    (BASE / "new-review-prompt.txt").write_bytes(prompt.encode("utf-8"))
    (BASE / "new-review-delivery.txt").write_bytes(delivery.encode("utf-8"))
    (BASE / "integrated-delivery-measurement.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("status", "original_delivery_codepoints",
        "new_delivery_codepoints", "saved_codepoints", "remaining_headroom", "obligation_count", "scope_count",
        "exact_serialized_payload_roundtrip", "source_section_byte_identical")}, indent=2))


if __name__ == "__main__":
    main()
