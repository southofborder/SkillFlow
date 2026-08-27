# Frozen JS parity oracles

These JSON files are the **frozen output of the original JS reference engine**
(`packages/skill-fcg-analyzer`), captured once — while that engine still existed
and the parity suite was green — by `tests/parity/_gen_golden.py`.

## Why they exist

The parity tests used to spawn `node` on each run to compare the Python port
against the live JS engine. When the JS analyzer was deleted (consolidation onto
the Python reference engine), that live oracle went away. Freezing its output
first keeps the regression pin **independent**: a test fails if the Python port
drifts from what JS actually produced, not from what Python produces today (which
would be vacuous).

All oracles were generated **rule-only** (`semanticLlm=false`, `disableLlm=true`)
— no LLM key was spent, and none is needed to reproduce.

## Files

| File | Shape | Source test |
|------|-------|-------------|
| `analyzer_core.json` | fixture-keyed snapshot (4) | `test_parity_analyzer_core.py` |
| `doc_flow.json` | fixture-keyed snapshot (8) | `test_parity_doc_flow.py` |
| `split_feedback.json` | fixture-keyed snapshot (2) | `test_parity_split_and_feedback.py` |
| `pipeline.json` | `skill|mode`-keyed snapshot (9 full + 2 quick) | `test_parity_pipeline.py` |
| `node_profiler.json` | single snapshot | `test_parity_node_profiler.py` |
| `frontmatter.json` | list (6) | `test_parity_frontmatter.py` |
| `shell.json` | list (28) | `test_parity_shell_classifier.py` |
| `tool_extractor.json` | list | `test_parity_tool_extractor.py` |
| `script_flow.json` | single snapshot | `test_parity_script_flow.py` |
| `flood_filter.json` | 3 hash strings | `test_parity_flood_filter.py` |

`flood_filter.json` is special: it is the **permanent witness** that Python's
JSON serialization + shortHash match Node's byte-for-byte (including non-ASCII
`café` / `中文`). The JS `data-labeler.js` that produced those hashes no longer
exists, so this golden is the only surviving reference for the FCG↔DOE join key.

## Regenerating

Do **not** regenerate against the Python engine — that defeats the purpose. These
files should only ever be re-derived from the original JS engine (recover it from
git history first). `_gen_golden.py` is kept for provenance/record only.
