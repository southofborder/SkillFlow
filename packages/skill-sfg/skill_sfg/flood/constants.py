"""Flood-engine constants — ported verbatim from the JS flood + DOE authorities.

Sources:
  * graph-transfer-analyzer.js:28-60  — DEFAULT_LIMITS / LIMIT_ENV_KEYS / NO_LIMIT
  * graph-transfer-analyzer.js:649    — SEMANTIC_FLOW_MODES
  * graph-transfer-analyzer.js:773    — GENERALIZING_DERIVED_CATEGORIES
  * flow-instance-router.js:108,133   — CONTROL_FLOW_PLACEHOLDER_PARAMS, NEGATIVE_CONDITION_REGEX
  * evidence-pack.js:243-246          — REAL_TRANSFORM_TYPES (FCG-side authority for digest)

REAL_TRANSFORM_TYPES lives in the DOE package in JS, but the flood side is now the
authority: it precomputes transform_digest, so this set MUST match evidence-pack.js
exactly or the M4 verdict-equivalence parity fails. The REDUCTION_SET / DERIVATION
split (which of the real transforms count as a reduction for reduction_applied) is a
new M3 concept documented in the plan.
"""

import re

# --- graph-transfer-analyzer.js:28-60 ------------------------------------------
# Local flooding is deterministic and guaranteed to converge; the size gates are
# optional result-size ceilings, NOT safety timeouts. NO_LIMIT == JS
# Number.MAX_SAFE_INTEGER; the slice()/counter checks never fire on a real graph.
NO_LIMIT = 9007199254740991  # Number.MAX_SAFE_INTEGER

DEFAULT_LIMITS = {
    "maxLabelFlows": NO_LIMIT,
    "maxInstances": NO_LIMIT,
    "maxEvents": NO_LIMIT,
    "maxDepth": 1000,
    "maxBranchesPerNode": NO_LIMIT,
    "maxMergeParents": 8,
    "maxRelatedFlows": 128,
    "maxMergeGroupsPerFlow": 64,
    "maxClosureIterations": 16,
}

LIMIT_ENV_KEYS = {
    "maxLabelFlows": "SFG_SECURITY_MAX_LABEL_FLOWS",
    "maxInstances": "SFG_SECURITY_MAX_INSTANCES",
    "maxEvents": "SFG_SECURITY_MAX_EVENTS",
    "maxDepth": "SFG_SECURITY_MAX_DEPTH",
    "maxBranchesPerNode": "SFG_SECURITY_MAX_BRANCHES_PER_NODE",
    "maxMergeParents": "SFG_SECURITY_MAX_MERGE_PARENTS",
    "maxRelatedFlows": "SFG_SECURITY_MAX_RELATED_FLOWS",
    "maxMergeGroupsPerFlow": "SFG_SECURITY_MAX_MERGE_GROUPS_PER_FLOW",
    "maxClosureIterations": "SFG_SECURITY_MAX_CLOSURE_ITERATIONS",
}

# --- graph-transfer-analyzer.js:649 --------------------------------------------
# Semantic-kind flow modes describe the NODE's transform of the data (introduce/
# derive/read-storage); they must survive route downgrade.
SEMANTIC_FLOW_MODES = frozenset(["source_introduction", "derived_flow", "storage_read"])

# --- graph-transfer-analyzer.js:773 --------------------------------------------
# Generalizing derived categories: a summarize/aggregate product is BROADER than
# its input (a subset of the seed's information), so the seed's own out-flow
# already carries it → never injected as a specializing closure member.
GENERALIZING_DERIVED_CATEGORIES = frozenset(["aggregate_data"])

# --- flow-instance-router.js:108 -----------------------------------------------
# control_flow placeholder params: a pure-ordering edge's data_flow is a
# placeholder (state>state / context>context / empty). Only a data-carrying
# control_flow edge lets a label definitely flow across.
CONTROL_FLOW_PLACEHOLDER_PARAMS = frozenset(["", "state", "context"])

# --- flow-instance-router.js:133 -----------------------------------------------
# Negative-condition precision gate. re.I mirrors the JS /.../i flag. The word
# boundaries \b behave identically for these ASCII alternatives.
NEGATIVE_CONDITION_REGEX = re.compile(
    r"\b(?:unless|only if|except|without|do(?:es)? not|don't|doesn't|never|"
    r"no longer|must not|cannot|can't|if not|provided that|as long as)\b",
    re.IGNORECASE,
)

# --- evidence-pack.js:243-246 (FCG-side authority) -----------------------------
# The transform event types that genuinely change data (introduction / pure
# pass-through excluded). Only these enter transform_digest / transform_sig.
REAL_TRANSFORM_TYPES = frozenset([
    "redact_drop", "field_slice_drop", "field_slice_keep",
    "summarization", "aggregate", "pseudonymize", "semantic_derivation",
])

# --- M3 new: reduction vs derivation split (see plan) --------------------------
# reduction_applied = any reduction-kind transform occurred before egress.
# Reductions strictly reduce/protect (drop, slice, summarize, aggregate).
# Derivations (pseudonymize / semantic_derivation) rename/specialize; they do NOT
# reduce, so they are excluded from reduction_applied.
REDUCTION_SET = frozenset([
    "redact_drop", "field_slice_drop", "field_slice_keep",
    "summarization", "aggregate",
])


# --- reduction poset (antichain-valued reduction fact) -------------------------
# reduction_applied started as a single BIT ("did any reduction run before
# egress"). It is generalized here to an ANTICHAIN over the reduction types — the
# set of *maximal, mutually-incomparable* reductions a flow applied. This lets the
# DOE/LLM judge WHAT KIND of protection ran (not just whether any did), and it
# dissolves the conservative-AND merge blur: once the antichain is a dedup-key
# component, only paths that protected the data the SAME way merge into a bucket,
# so reduction_applied is homogeneous per bucket (no AND folding needed).
#
# WHY THIS DOES NOT RE-EXPLODE (the transform_sig lesson): transform_sig was an
# ORDERED PATH PREFIX — unbounded on cycles ("redact>redact>...") — which turned
# the fixpoint flood into path enumeration. The antichain is a SET over a FIXED
# 5-element universe: order collapses ({redact,summarize} == {summarize,redact}),
# the powerset is capped at 2^5, and along any path it grows MONOTONICALLY toward
# a maximal element and then stops (a cycle re-applying the same reduction adds
# nothing). Bounded by the poset's antichain count — a graph-INDEPENDENT constant
# — not by the number of paths.
#
# POSET EDGES: currently EMPTY — all 5 reduction types are mutually incomparable
# (a FLAT antichain). A type-level strength order is unsafe: whether
# field_slice_keep protects more than redact_drop, or summarization more than
# aggregate, depends on the INSTANCE (what was kept/dropped, the aggregation k),
# which the type alone does not carry. We only assert comparability that is
# instance-independent — none qualifies yet. reduction_dominates() is the single
# seam to add an edge later (e.g. 'aggregate': {'summarization'}) without touching
# any caller. Key: stronger -> the set of reductions it strictly dominates/absorbs.
_REDUCTION_DOMINATES = {
    # 'aggregate': frozenset(['summarization']),  # candidate edge — deliberately OFF
}


def reduction_dominates(stronger, weaker):
    """True iff ``stronger`` is a strictly-stronger reduction than ``weaker`` under
    the poset, so ``weaker`` is absorbed out of any antichain that also contains
    ``stronger``. Flat poset => always False (no configured edges)."""
    return weaker in _REDUCTION_DOMINATES.get(stronger, frozenset())


def reduction_antichain(types):
    """Collapse an iterable of transform types to the antichain of reductions it
    contains: keep only reduction-kind types, then drop any element dominated by
    another present element. Flat poset => the reduction set unchanged. Returns a
    sorted tuple (deterministic, hashable) suitable for a dedup-key component."""
    present = {t for t in types if t in REDUCTION_SET}
    maximal = {t for t in present
               if not any(reduction_dominates(o, t) for o in present if o != t)}
    return tuple(sorted(maximal))
