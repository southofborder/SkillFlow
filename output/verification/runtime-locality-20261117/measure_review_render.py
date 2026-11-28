"""Pure display measurement of preserved evidence; no candidate validation or run."""
from copy import deepcopy
import json
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from skillflow.common.recording import canonical_sha256, sha_file
from skillflow.document_guided.fragments import fragment_correction_strategy
from skillflow.document_guided.review_correction import ReviewCorrectionStrategy, _parts
from skillflow.document_guided.source_review import build_source_review_prompt
from skillflow.propagation.contracts.runtime_contract import runtime_contract
from tools.doe.document_guided_client import ENVELOPE, MAX_INPUT_CHARS

VERIFY = Path(__file__).resolve().parent
OLD = ROOT / "experiments/doe/runs/document-guided-ga4-processing-restart-high-20261117-172228/review"


def read(relative):
    return json.loads((OLD / relative).read_bytes().decode("utf-8"))


def main():
    names = ["inputs.json", "calls/review/a001/response.json", "calls/review/a001/validation.json", "calls/review/a001/prompt.txt"]
    pins = {name: sha_file(OLD / name) for name in names}
    material, raw, validation = read(names[0]), read(names[1]), read(names[2])
    original_prompt = (OLD / names[3]).read_bytes().decode("utf-8")
    results = []
    for label in ("preserved_material_new_correction_only", "synthetic_complete_current_runtime_substitution"):
        current = deepcopy(material)
        if label.startswith("synthetic"):
            current["runtime_contract"] = runtime_contract()
            base = build_source_review_prompt(current)
        else:
            base = original_prompt
        strategy = ReviewCorrectionStrategy(current, fragment_correction_strategy("review"))
        corrected = strategy.build_prompt(base, raw, validation["diagnostics"])
        prior, shown = _parts(base), _parts(corrected)
        assert prior and shown and strategy.scope["mode"] == "records"
        assert shown[2] == prior[2] == _parts(original_prompt)[2]
        context = shown[1].pop("correction")
        if isinstance(context["records"], list):
            assert dict(zip(context["record_ids"], context["records"])) == strategy.scope["records"]
        assert shown[1] == prior[1]
        original_payload = _parts(original_prompt)[1]
        if label.startswith("synthetic"):
            original_payload["runtime_contract"] = runtime_contract()
        assert shown[1] == original_payload
        inventory = shown[1]["input_contract_inventory"]
        assert len(inventory["obligations"]) == 684
        assert sum(len(row["scopes"]) for row in inventory["obligations"]) == 2540
        results.append({"case": label, "synthetic_only_substituted_key": "runtime_contract" if label.startswith("synthetic") else None,
            "material_sha256": canonical_sha256(current), "material_original_identity": current["identity"],
            "runtime_version": current["runtime_contract"]["version"],
            "base_characters": len(base), "correction_core_characters": len(corrected),
            "adapter_characters": len(ENVELOPE), "delivered_characters": len(ENVELOPE + corrected),
            "limit": MAX_INPUT_CHARS, "headroom": MAX_INPUT_CHARS - len(ENVELOPE + corrected),
            "delivery_sha256": canonical_sha256(ENVELOPE + corrected),
            "full_source_suffix_sha256": canonical_sha256(shown[2]),
            "source_files": len(current["files"]), "obligations": 684, "scopes": 2540,
            "selected_existing_records": len(strategy.scope["records"]),
            "missing_insertion_slots": len(strategy.scope["missing_obligation_ids"]),
            "complete_logical_input_equal": True, "original_source_suffix_equal": True,
            "correction_scope": strategy.scope["evidence"],
            "correction_context_sha256": canonical_sha256(context)})
    assert pins == {name: sha_file(OLD / name) for name in names}
    report = {"identity": "skillflow-pure-review-render-measurement-v1", "method": "Pure JSON loading and prompt display only; no source/candidate validator, compiler, backend, runner, replay, Skill or model call.",
        "historical_root": str(OLD), "historical_artifact_hashes": pins,
        "code_hashes": {str(path.relative_to(ROOT)): sha_file(path) for path in (
            ROOT / "src/skillflow/document_guided/review_correction.py", ROOT / "src/skillflow/document_guided/source_review.py",
            ROOT / "src/skillflow/propagation/contracts/runtime_contract.py", Path(__file__).resolve())},
        "cases": results, "limitation": "These concrete complete deliveries fit only if headroom is nonnegative; exact sharing cannot guarantee any arbitrary input fits. Existing whole delivery limit and bounded local retention remain necessary."}
    name = sys.argv[1] if len(sys.argv) == 2 else "review-render-measurement-01.json"
    if not re.fullmatch(r"review-render-measurement-[0-9]+\.json", name):
        raise ValueError("A fresh measurement receipt filename is required")
    destination = VERIFY / name
    if destination.exists():
        raise ValueError("Preserve the existing receipt; select a fresh destination before rerunning")
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps([{k: v for k, v in row.items() if k in {"case", "delivered_characters", "headroom", "selected_existing_records", "missing_insertion_slots", "runtime_version"}} for row in results]))


if __name__ == "__main__":
    main()
