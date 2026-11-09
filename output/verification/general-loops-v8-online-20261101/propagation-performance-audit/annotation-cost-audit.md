# Selected-annotation cost audit (read only)

The current selected GA4 candidate is not asking the interpreter to explore arbitrary partial orders: all **372 modeled IR use fixed order**. It contains **375 atomic operations,18 case groups,66 distinct cases and127 case-tagged events**. There are16 explicit alternatives references (largest8) and23 merge operations (largest5 predecessors). The graph has194 blocks,285 edges and420 IR. These static counts do not establish the actual runtime candidate product.

The stronger explanation in the available live evidence is **repeated whole-annotation reconstruction while saving propagation**, not continued model reasoning. The root-owned nonblocking stack samples005/006 put the main thread under `save_propagation_run:110`, reached after `run_propagation:178` returned from `_calculate`. The observed nested path is `load_annotation → assemble_fragments → validate_fragment → project_sensitivity → expand_processing → build_demand_target_index → build_task_target_index → cfg_target_index/resolve_cfg_target`. Sampling establishes activity at those instants, not its fraction of total elapsed time.

## The exact repeated work in this candidate

The selected fragments have46 realizations,68 demand records,48 operation-demand records and57 sensitivity declarations. **13 sensitivity declarations refer to case-bearing IR**: ir_287 has8,ir_101 has2,ir_296 has2 andir_169 has1.

For every one of these13 declarations, `fragments.py:451–453` calls `project_sensitivity`. That function (`annotation_wire.py:743–756`) copies the **whole372-IR processing fragment**, clears sensitivity throughout it, adds the one declaration and expands/validates the entire processing object. It does not restrict the work to the affected IR.

One successful `assemble_fragments` has the following static expansion count:

| Caller | Whole-processing expansions |
|---|---:|
| Validate processing |1|
| Validate correspondence:base processing plus combined mapping wire |2|
| Validate sensitivity:base processing plus13 per-declaration projections |14|
| Final flat annotation expansion before compilation |1|
| Total |**18**|

Sixteen of these18 are processing-only expansions; the two others validate the larger combined wire. Each processing-only validation that passes evidence checks rebuilds the demand target index (`annotation_wire.py:701–702`).

The full annotation loader additionally replays the three saved fragment chains. Mapping and sensitivity each load/revalidate processing again through their dependency context, for **three processing-chain replays within five total step-chain replays**. Counting only accepted responses gives a conservative **37 whole-processing expansions per successful load_annotation**. The rejected first processing response is also rechecked; its cost and additional compiler checks are not included in that floor.

The normal `run_propagation` path contains two full annotation loads before `_calculate`, then three more during save and consistency checks (`runner.py:166–167,110,180,145`). Thus the eventual successful path has an accepted-response floor of **185 whole-processing expansions**. This is a static path count, not a claim that all185 had finished when sampled. The observed stack is in the first save-time load.

## Why each rebuilt index is expensive

The actual CFG contains **9,843 JSON positions**. `cfg_target_index` (`references.py:167–179`) traverses every position and calls `resolve_cfg_target`. Of those positions,**7,514 are anchored to an IR**. For each such target, `resolve_cfg_target:137–138` scans all420 instructions to find the one ID. This implies **3,155,880 IR-ID comparisons per CFG index build**, before type checking, copying values, source checks, pointer traversal and transfer-target indexing. The live samples show precisely this path inside repeated sensitivity projection.

This is program validation and indexing amplification. It is not a necessary cost of the model's seven semantic calls, and adding stronger reasoning effort would not fix it. No change is made during this running experiment.

## What the static candidate does and does not support

The interpreter has explicit bounded products for data candidates (`interpreter.py:232–250`) and conditional-build guards (`342–384`). It also enumerates admissible partial-order arrangements (`671–722`), but every selected spec is fixed, so the arbitrary-order factorial explanation does not fit this annotation. The largest specs are ir_169 andir_287 at29 atomic operations each, with7 cases each. Case alternatives should not be multiplied naively across the entire graph: they carry candidate/receiver associations, and actual candidate counts require runtime facts.

The UI marks the propagation stage before preparation verification and loading (`document_guided/runner.py:513–518`). The propagation directory is created only during the save path after solution and material validation (`propagation/runner.py:110–122`). Therefore `stage=propagation` or absence of a propagation directory alone cannot tell whether the solver is still running. Here the nonblocking stacks provide the stronger location evidence.

This audit does not report final propagation coverage or DOE, run a solver/compiler/replay, modify code, launch targets or interrupt the controller. It identifies the observed code path and quantifies its static repetition. A few stack samples do not measure a complete time profile or prove this is the only bottleneck.
