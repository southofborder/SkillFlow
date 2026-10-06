"""Explicit reconstruction of seven pinned candidates, never historical migration."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from skillflow.common.paths import project_root, resolve_material_path

from skillflow.common.recording import canonical_sha256
from skillflow.common.recording import read_json
from skillflow.common.recording import sha_file
from skillflow.propagation.material import prepare_material
from skillflow.propagation.annotation.services import compile_response


def verify_prechange(directory):
    directory = Path(directory)
    receipt = read_json(directory / "upstream-verification.json")
    unsigned = {key: value for key, value in receipt.items() if key != "sha256"}
    if receipt.get("identity") != "skillflow-prechange-verification-v1" or canonical_sha256(unsigned) != receipt.get("sha256"):
        raise ValueError("Pre-change validation receipt is invalid")
    for relative, digest in receipt["files"].items():
        path = (directory / relative).resolve()
        if not path.is_relative_to((directory / "upstream").resolve()) or sha_file(path) != digest:
            raise ValueError("Frozen historical material differs: " + relative)
    # The receipt records an old-contract validation. It is not a claim that the
    # current compiler can consume the old response without reconstruction.
    return receipt


def reconstruct(directory):
    directory = Path(directory)
    receipt = verify_prechange(directory)
    cases = read_json(directory / "upstream/candidates-v1.json")
    result = []
    for case in cases:
        verified = read_json(directory / "upstream" / (case["sample"] + "-verified.json"))
        old_material = verified["material"]
        material = prepare_material(old_material["source"], old_material["cfg"])
        raw = deepcopy(case["raw_annotation"])
        if raw.pop("unresolved") != []:
            raise ValueError("This explicit fixture reconstruction only supports the verified empty legacy field")
        changes = [{"pointer": "/unresolved", "before": [], "after": "removed"},
                   {"pointer": "/outcome", "before": "absent", "after": "completed"}]
        raw["outcome"] = "completed"
        for ir_id, spec in raw["transfer_specs"].items():
            if "order" in spec or "precedence" in spec:
                raise ValueError("Expected the exact historical raw specification")
            spec["order"] = "fixed"
            changes.append({"pointer": f"/transfer_specs/{ir_id}/order", "before": "absent", "after": "fixed"})
        old_rules = {rule["id"]: rule["text"] for rule in old_material["execution_model"]["rules"]}
        new_rules = {rule["id"]: rule["text"] for rule in material["execution_model"]["rules"]}

        def quotations(value, path=""):
            if isinstance(value, dict):
                if value.get("basis") == "execution_model":
                    rule, quote = value["ref_id"], value["quote"]
                    if quote not in old_rules[rule]:
                        raise ValueError("Old rule evidence was not authentic")
                    if quote not in new_rules[rule]:
                        value["quote"] = new_rules[rule]
                        changes.append({"pointer": path + "/quote", "before": quote, "after": value["quote"],
                                        "basis": "explicit_reconstruction", "rule": rule,
                                        "reason": "同一规则的默认来源/观察关系保留；新版以可计算顺序和任务失败取代泛化未决措辞。"})
                for key, item in value.items():
                    quotations(item, path + "/" + key.replace("~", "~0").replace("/", "~1"))
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    quotations(item, path + "/" + str(index))
        quotations(raw)
        normalized, compiled, mapping = compile_response(raw, material)
        if normalized != raw:
            raise ValueError("Reconstruction normalized an unrecorded candidate field")
        result.append({"case_id": case["case_id"], "sample": case["sample"], "material": material,
                       "raw_annotation": raw, "expectation": case["expectation"],
                       "source_metadata": verified["source_metadata"],
                       "provenance": {"kind": "explicit_reconstruction", "historical_raw_sha256": case["raw_sha256"],
                                      "historical_source_identity": verified["upstream_identity"],
                                      "prechange_receipt_sha256": receipt["sha256"],
                                      "candidate_sha256": canonical_sha256(raw),
                                      "compilation_sha256": canonical_sha256(mapping),
                                      "changes": changes,
                                      "notice": "人工实验结构重建，不是新版模型接受响应。"}})
    return result
