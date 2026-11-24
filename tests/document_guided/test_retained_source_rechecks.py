from copy import deepcopy

import pytest

from skillflow.common.recording import canonical_sha256
from skillflow.document_guided.fragment_revision import processing_scope
from skillflow.document_guided.revision_rechecks import (
    checked_retention_targets, pending_retention_findings, retained_source_rechecks,
)


def test_kept_contract_is_rechecked_against_its_own_output_and_consumers():
    def ir(name, inputs, outputs):
        def port(key):
            return {"type": "result", "identifier": key}
        return {"id": name, "inputs": [port(k) for k in inputs], "outputs": [port(k) for k in outputs],
                "opcode": "value", "constraints": [], "metadata": {}}
    cfg = {"blocks": {"b": {"instructions": [ir("caller", [], ["options"]), ir("body", ["options"], [])],
                             "data_source_kind": None}}, "edges": []}
    proc = {"ir_semantics": {"caller": {"output_bindings": []}, "body": {"output_bindings": []}}}
    pieces = {"processing": {"value": proc}, "graph": {"value": cfg}, "annotation": {}}
    refs = [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1}]
    target = "annotation:/ir_semantics/caller"
    finding = {"id": "F002", "domain": "annotation", "owner": "processing", "target_ids": [target],
               "input_contract_obligation_id": "paired-request", "source_refs": refs,
               "explanation": "The invoked result is discarded.", "suggestion": "Recheck the returned value."}
    material = {"files": {"skill/SKILL.md": "Return the computed report."},
                "target_index": [{"id": target}], "annotation": proc}
    scope = processing_scope(cfg, cfg, [finding], proc)
    assert scope["slots"]["caller"]["source_rechecks"][0]["obligation_id"] == "paired-request"
    assert list(scope["read_only"]["result_consumers"]["caller"]) == ["body"]
    retained = retained_source_rechecks({"findings": [finding]}, pieces, pieces)
    material["revision_rechecks"] = checked_retention_targets(retained, material)
    other = {"status": "accepted", "obligation_id": "different-argument", "evidences": refs}
    assert len(pending_retention_findings(material, [other], [])) == 1
    assert not pending_retention_findings(material, [{**other, "obligation_id": "paired-request"}], [])
    bad = deepcopy(retained)
    bad[0]["targets"][target] = canonical_sha256("stale")
    with pytest.raises(ValueError, match="differs"):
        checked_retention_targets(bad, material)
    changed = deepcopy(pieces)
    changed["processing"]["value"]["ir_semantics"]["caller"]["output_bindings"] = ["changed"]
    assert retained_source_rechecks({"findings": [finding]}, pieces, changed) == []
