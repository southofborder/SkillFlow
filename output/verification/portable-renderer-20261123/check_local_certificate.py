"""Check the selected donor bytes with the locally built production renderer, offline."""
import json
from pathlib import Path
import sys

from skillflow.common.recording import implementation_provenance, sha_file
from skillflow.document_guided.accepted_upstream import describe_accepted_upstream
from skillflow.graph.audit.controlled import recertify_inherited
from skillflow.graph.ir.cfg import ControlFlowGraph
from skillflow.lean_renderer import renderer_path


def check():
    project = Path(__file__).resolve().parents[3]
    parent = project / "experiments/doe/runs/document-guided-ga4-lossless-delivery-high-20261122-211742"
    config = json.loads((parent / "manifest.json").read_bytes())["config"]
    bound = describe_accepted_upstream(parent, config=config)
    certificate_path = bound["certificate"]
    file_hash = bound["files"][certificate_path]
    raw = (parent / certificate_path).read_bytes()
    original = json.loads(raw)
    cfg = ControlFlowGraph.model_validate(json.loads((parent / bound["cfg_file"]).read_bytes())["cfg"])
    binary = renderer_path()
    local = recertify_inherited(raw, expected_sha256=file_hash, cfg=cfg, executable=binary)
    build_receipt = binary.parents[3] / "build.json"
    build = json.loads(build_receipt.read_bytes())
    if local["binary_sha256"] != build["binary_sha256"] or local["binary_sha256"] != sha_file(binary):
        raise ValueError("The local proof and checked build identify different executables")
    if (sha_file(parent / certificate_path) != file_hash or
            not all(local["checks"].values()) or len(cfg.blocks) != 215 or
            sum(len(block.instructions) for block in cfg.blocks.values()) != 489):
        raise ValueError("Unexpected input graph, certificate checks or donor document")
    return {"status": "passed", "implementation_sha256": implementation_provenance()["sha256"],
            "parent": parent.name, "certificate_file": certificate_path, "certificate_file_sha256": file_hash,
            "producer": {key: original["certificate"][key] for key in ("source_sha256", "binary_sha256")},
            "local_certificate": local, "local_renderer": str(binary), "local_build": build,
            "local_build_receipt_sha256": sha_file(build_receipt), "graph_ir_count": 489,
            "units": len(original["units"]), "links": len(original["derived_links"]),
            "python_executable": sys.executable, "python_sha256": sha_file(Path(sys.executable)),
            "historical_replays": 0, "model_calls": 0}


if __name__ == "__main__":
    print(json.dumps(check(), indent=2))
