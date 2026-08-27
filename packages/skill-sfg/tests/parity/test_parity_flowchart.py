"""Cross-engine parity: REAL JS generateFlowchartArtifacts vs the Python port.

The flowchart artifacts (.flow.mmd + .flow.md) are a pure-visualization layer with
no downstream verdict consumer, so this pins the port structurally rather than on a
real 1 MB artifact: a compact synthetic fcg.json (_flowchart_inputs.json) that
exercises every report section, every mermaid arrow/class branch, and the
escaping edge cases. The JS output is frozen to golden/flowchart.json (see
golden/README.md); this test asserts the Python port reproduces it byte-for-byte.

The single intentional nondeterminism is the `- Generated At: **<ISO ts>**` line
(wall clock); it is masked on both sides before comparison. Mermaid is compared
exactly.
"""

import json
import os
import re

_HERE = os.path.dirname(__file__)
_INPUTS = os.path.join(_HERE, "_flowchart_inputs.json")
# Frozen JS oracle (see golden/README.md).
with open(os.path.join(_HERE, "golden", "flowchart.json"), encoding="utf-8") as _fh:
    _GOLDEN = json.load(_fh)

from skill_sfg.output.flowchart_generator import generate_flowchart_artifacts

_TS_LINE = re.compile(r"^- Generated At: \*\*.*\*\*$", re.MULTILINE)


def _mask_ts(md: str) -> str:
    return _TS_LINE.sub("- Generated At: **<MASKED>**", md)


def test_js_python_flowchart_parity():
    with open(_INPUTS, "r", encoding="utf-8") as handle:
        fcg_json = json.load(handle)

    py = generate_flowchart_artifacts(fcg_json)

    assert py["mermaid"] == _GOLDEN["mermaid"], "mermaid diverged"
    assert _mask_ts(py["markdown"]) == _mask_ts(_GOLDEN["markdown"]), "markdown diverged"
