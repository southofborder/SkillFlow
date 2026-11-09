# Sensitivity v1: offline baseline

This offline experiment compares explicitly declared sensitive ranges with task-preserving demands. It does not establish exhaustive sensitivity coverage, runtime disclosure, or global minimality.

Three independently frozen cases; zero API calls. Original annotation responses remain historical materials. Current-format inputs are explicitly reconstructed offline candidates, with their provenance and differences retained.

| Case | Status | Declared ranges | Sinks | Supported excess | Possible excess | No excess established | Replay | Materials |
|---|---|---:|---:|---:|---:|---:|---|---|
| 001 | complete | 1 | 6 | 1 | 0 | 4 | matched | [Review](cases/001/report.html), [Result](cases/001/sensitivity-review.json), [Candidate](candidates/001.json), [New demand](demand/001/report.html), [Reconstruction](reconstructed/001.json), [Assistant opinion](assistant-reviews/001.md) |
| 010 | complete | 0 | 12 | 0 | 0 | 0 | matched | [Review](cases/010/report.html), [Result](cases/010/sensitivity-review.json), [Candidate](candidates/010.json), [New demand](demand/010/report.html), [Reconstruction](reconstructed/010.json), [Assistant opinion](assistant-reviews/010.md) |
| 013 | complete | 1 | 16 | 0 | 0 | 4 | matched | [Review](cases/013/report.html), [Result](cases/013/sensitivity-review.json), [Candidate](candidates/013.json), [New demand](demand/013/report.html), [Reconstruction](reconstructed/013.json), [Assistant opinion](assistant-reviews/013.md) |

Counts are declared-range comparisons, not unique leaks or observed executions. In particular case 010's empty declarations do not establish that its unknown content is nonsensitive.
