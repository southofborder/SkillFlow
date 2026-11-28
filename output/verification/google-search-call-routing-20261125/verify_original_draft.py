"""Compile an untouched copy of the rejected draft and inspect real source continuations."""
from hashlib import sha256
import json
from pathlib import Path

from check_entry_paths import describe
from skillflow.common.recording import implementation_provenance
from skillflow.document_guided.graph_facts import assemble_graph_facts, from_accepted_cfg


out = Path(__file__).resolve().parent
project = out.parents[2]
old = project / "experiments/doe/runs/document-guided-google-search-outcomes-high-20261125-190529"
record = old / "steps/graph/calls/a001/response.json"
data = record.read_bytes()
raw = json.loads(data)
if isinstance(raw, str):
    raw = json.loads(raw)
package = out / "source-package"
files = {"skill/" + p.relative_to(package).as_posix(): p.read_bytes().decode("utf-8")
         for p in package.rglob("*") if p.is_file()}
assembly = assemble_graph_facts(raw, files=files)
assert assembly.cfg is not None, assembly.gaps
cfg = assembly.cfg
check = describe(cfg)
operands = [v for block in cfg["blocks"].values() for ir in block["instructions"]
            for v in ir["inputs"] + ir["outputs"]]
check["checks"]["discarded_invented_caller_tag"] = all(
    v.get("semantic_name") != "helper.return_scope" for v in operands)
check["checks"]["accepted_cfg_roundtrip"] = from_accepted_cfg(cfg, files=files).cfg == cfg
check["checks"]["raw_record_unchanged"] = record.read_bytes() == data
check["all_checks_match"] = all(check["checks"].values())
check.update(origin="Offline regression only. Previous model answer recompiled from a read-only copy.",
             raw_sha256=sha256(data).hexdigest(), implementation=implementation_provenance()["sha256"])
(out / "offline-original-cfg.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
(out / "offline-route-acceptance.json").write_text(json.dumps(check, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(check["checks"]))
assert check["all_checks_match"]
