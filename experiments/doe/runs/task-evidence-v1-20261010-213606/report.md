# Task Evidence v1: offline baseline

Source spans and target references are validated; semantic support and completeness are not proven.

All candidates and review opinions were authored by the assistant. No remote model was called, no Skill was executed, and no demand, sensitivity, or DOE verdict was computed.

| Case | Reference validation | Requirements | Replay | Materials |
|---|---|---:|---|---|
| 001 | reference_validated | 7 | matched | [Review](cases/001/report.html), [Task](cases/001/task.json), [Assistant opinion](assistant-reviews/001.md), [Frozen facts](../../../propagation/runs/sink-tightening-v1-20261002-205045/cases/001/propagation/doe-input.json) |
| 010 | reference_validated | 8 | matched | [Review](cases/010/report.html), [Task](cases/010/task.json), [Assistant opinion](assistant-reviews/010.md), [Frozen facts](../../../propagation/runs/sink-tightening-v1-20261002-205045/cases/010/propagation/doe-input.json) |
| 013 | reference_validated | 9 | matched | [Review](cases/013/report.html), [Task](cases/013/task.json), [Assistant opinion](assistant-reviews/013.md), [Frozen facts](../../../propagation/runs/sink-tightening-v1-20261002-205045/cases/013/propagation/doe-input.json) |

Start with each requirement, inspect the supporting source, then inspect its CFG target. Uncited source lines are navigation aids, not detected omissions. A correct reference can support an incorrect interpretation.
