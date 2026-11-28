"""Pure presentation comparison; no historic validators or run execution."""
import hashlib
import json
from pathlib import Path

from skillflow.common.prompt_format import compact_json
from skillflow.document_guided.processing_display import (
    _parts, compact_processing_correction, expand_processing_material,
    pack_processing_material, render_processing_material,
)

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RUN = ROOT / "experiments/doe/runs/document-guided-ga4-source-review-locality-high-20261113-203902"
bound = {}


def read(path):
    raw = path.read_bytes()
    bound[path.relative_to(ROOT).as_posix()] = hashlib.sha256(raw).hexdigest()
    return raw.decode("utf-8")


def value_after(prompt, heading):
    return json.JSONDecoder().raw_decode(prompt.split(heading + "\n", 1)[1])[0]


flow = read(RUN / "steps/flow/document.md")
rows, bases = [], {}
for stage in ("processing", "revision-processing"):
    old = read(RUN / "steps" / stage / "calls/a001/prompt.txt")
    assert flow in old
    logical = {"documents": {"flow": flow}, "cfg": value_after(old, "CFG"),
               "runtime_contract": value_after(old, "RUNTIME_CONTRACT")}
    notice = ""
    if stage == "revision-processing":
        logical["repair_context"] = value_after(old, "SOURCE REVIEW REPAIR")
        # Keep the old repair instructions verbatim, even for this size-only comparison.
        start = old.index("Return one COMPLETE replacement fragment")
        notice = old[start:old.index("SOURCE REVIEW REPAIR\n", start)]
    packed = pack_processing_material(logical)
    assert compact_json(expand_processing_material(packed)) == compact_json(logical)
    prefix = old[:old.index("PREVIOUS WORK\n") + len("PREVIOUS WORK\n")]
    suffix = old[old.index("\n\nGLOBAL REQUIREMENTS AND LIMITATIONS\n"):]
    new = prefix + notice + render_processing_material(logical) + suffix
    assert _parts(new)[2] == suffix
    bases[stage] = new
    rows.append({"stage": stage, "original_prompt_codepoints": len(old),
                 "presentation_only_prompt_codepoints": len(new), "saved_codepoints": len(old) - len(new),
                 "saved_percent": 100 * (1 - len(new) / len(old)),
                 "full_source_output_suffix_unchanged": True,
                 "logical_payload_sha256": packed["logical_sha256"],
                 "exact_expansion_checked": True,
                 "instructions_unchanged_notice": "This isolates input display savings: old output instructions/schema are retained. It is not the final new request prompt."})

correction = read(RUN / "steps/processing/calls/a002/prompt.txt")
base = read(RUN / "steps/processing/calls/a001/prompt.txt")
context = value_after(correction, "CURRENT_CANDIDATE_AND_DIAGNOSTICS")
fallback = bases["processing"] + correction[len(base):]
joint = compact_processing_correction(bases["processing"], fallback, context)
assert _parts(joint)[1]["correction"] == context
assert _parts(joint)[2] == _parts(bases["processing"])[2]
rows.append({"stage": "processing-correction", "original_prompt_codepoints": len(correction),
             "presentation_only_prompt_codepoints": len(joint), "saved_codepoints": len(correction) - len(joint),
             "saved_percent": 100 * (1 - len(joint) / len(correction)),
             "full_source_output_suffix_unchanged": True,
             "complete_correction_context_preserved": True})

for path in (ROOT / "src/skillflow/document_guided/processing_display.py",
             ROOT / "src/skillflow/document_guided/review_display.py"):
    read(path)
result = {"version": "skillflow-processing-display-size-audit-v1",
          "scope": "Pure display transformation of saved input values. No old run, replay, validator, backend or model execution.",
          "metric": "Unicode codepoints; neither token nor wall-time savings are inferred.",
          "rows": rows, "artifact_sha256": bound}
(OUT / "processing-display-size-audit.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(rows, indent=2))
