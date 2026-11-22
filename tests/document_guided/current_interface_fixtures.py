"""Authored current-contract copies of the fixed 010/013 regression material.

The saved source, operands, expressions and old answers are never changed.
Unspecified outcome encodings remain concrete processing/interface gaps.
"""
from copy import deepcopy


def current_contract_copy(processing, case):
    result = deepcopy(processing)
    for ir, spec in result["ir_semantics"].items():
        for segment in spec.get("segments", []):
            for operation in segment.get("ops", []):
                if operation["op"] == "call":
                    if case == "010":
                        assert ir == "ir_016" and operation["location"] == "search_tool" and len(operation["inputs"]) == 1
                        cited = [{"file": "skill/references/workflow.md", "start_line": 7, "end_line": 13,
                                  "reason": "The source defines query and the two optional unchanged call arguments."}]
                        requirements = [[{"property": "value", "path": ["query"]},
                            {"property": "value", "path": ["from_date"], "if_present": True},
                            {"property": "value", "path": ["limit"], "if_present": True}]]
                    else:
                        assert case == "013" and ir in {"ir_005", "ir_008", "ir_010"}
                        expected_count = 1 if operation["location"] == "archive_tool" else 2
                        assert operation["location"] in {"archive_tool", "fast_tool"} and len(operation["inputs"]) == expected_count
                        cited = [{"file": "skill/SKILL.md", "start_line": 9, "end_line": 12,
                                  "reason": "Fast fetch requires source_id and FAST_KEY; archive fetch takes source_id alone."}]
                        requirements = [[{"property": "value", "path": []}] for _ in operation["inputs"]]
                    operation["input_contract"] = {"inputs": [
                        {"input_index": index, "required": required, "remainder": "independent",
                         "reason": "The cited interface requires exactly the declared argument information."}
                        for index, required in enumerate(requirements)],
                        "reason": "The source explicitly specifies the actual tool arguments and optionality.", "evidences": cited}
                elif operation["op"] == "compute" and not operation.get("expression"):
                    assert case == "013" and ir in {"ir_006", "ir_007", "ir_009", "ir_011", "ir_013", "ir_017", "ir_021", "ir_025"}
                    if ir in {"ir_013", "ir_017", "ir_021", "ir_025"}:
                        missing = "The representation of the final status and its mapping from this actual fetch outcome."
                        resolution = "Specify the final-status encoding and which outcome fields determine it."
                    elif ir == "ir_007":
                        missing = "The error discriminator or interface field used to classify this first failure as transient."
                        resolution = "Specify the transient-error criterion and its exact field on the first fetch outcome."
                    else:
                        missing = "The success/failure discriminator and its field on this actual fetch outcome."
                        resolution = "Specify the fetch outcome's success discriminator and exact representation."
                    cited = deepcopy(spec["evidences"])
                    barrier = {"code": "missing_interface", "reason": missing,
                               "missing": missing, "resolution": resolution, "evidences": cited}
                    inputs = [{"input_index": index, "required": [], "remainder": "unresolved",
                               "reason": missing, "gap": deepcopy(barrier)} for index in range(len(operation["inputs"]))]
                    properties = ["value", "truth"] if ir in {"ir_006", "ir_007", "ir_009", "ir_011"} else ["value"]
                    operation["demand_transfer"] = {"rules": [{"output": {"property": property, "path": []},
                        "inputs": deepcopy(inputs), "reason": "The source states the qualitative duty but leaves its outcome encoding unspecified.",
                        "evidences": deepcopy(cited)} for property in properties]}
    return result
