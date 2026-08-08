"""StateNode + dedup key + judgment-summary helpers (M3 core, design B).

The StateNode replaces the JS ``labelFlow`` record. Under design B two things
change versus graph-transfer-analyzer.js:

  1. NO five spread-copied arrays. The wall was
     graph-transfer-analyzer.js:680-686 copying node_path / node_names /
     edge_path / route_history / filter_events per child (each O(depth)). The
     StateNode keeps only a SINGLE parent pointer plus O(#real-transforms)
     summary (transform_digest / word_set), so per-flow memory is O(1) in path
     length. DOE reconstructs node/edge paths from the parent chain, so nothing
     downstream reads the dropped arrays.

  2. The dedup key is JS-8 + ``origin_class`` (a 9-tuple, vs the JS 8-tuple at
     graph-transfer-analyzer.js:1294-1310) — a strict REFINEMENT of the JS key
     (origin_class = the origin node's {trust_boundary, data_surface} class,
     which is bounded). ``transform_sig`` was tried as a key component but
     REMOVED: it encodes the full ordered path prefix, so it grows without bound
     on cycles ("redact>redact>...") and turns the fixpoint flood into path
     enumeration (space explosion). Order does NOT propagate in the key; DOE
     rebuilds transform_seq at judgment time by walking the single parent chain
     (flow-path-utils.js rebuildFlowChain / evidence-pack.js transformsByNode),
     so "redact→send" and "send→redact" stay distinguishable downstream without
     a path-sensitive key here. transform_sig is still EMITTED on the flow_state
     as a boolean-ish digest field for DOE — it is just no longer a key.

Two accumulated substitutes for the cut arrays, both O(1):
  * ``filter_derived_seen`` — replaces ``isDerivedLabel``'s scan over the
    accumulated ``filter_events`` (graph-transfer-analyzer.js:1322-1329).
  * ``transform_digest`` — the ordered list of real transforms from origin
    onward; ``transform_sig`` is its ``'>'``-join, matching DOE transform_seq.
"""

import os

from ..security.data_labeler import short_hash
from .constants import reduction_antichain

# A/B seam for the reduction-antichain key component. Default ON (the component
# is part of the key). Set FCG_REDUCTION_KEY=0 to drop it — used ONLY to measure
# the real per-skill bucket multiplier the antichain adds (ON vs OFF on the same
# code path), mirroring the FCG_CYCLE_EXPAND A/B methodology. Not a product flag.
_REDUCTION_KEY_ON = os.environ.get("FCG_REDUCTION_KEY", "1") != "0"

# The 6 event types that mark a label as derived, from isDerivedLabel
# (graph-transfer-analyzer.js:1322-1329). 'semantic_extraction' never actually
# appears as an event type (the filter emits 'semantic_derivation'); kept for
# verbatim fidelity with the JS list.
_DERIVED_EVENT_TYPES = frozenset([
    "field_slice_keep",
    "semantic_derivation",
    "semantic_extraction",
    "aggregate",
    "summarization",
    "artifact_production",
])


class StateNode:
    """A deduped flood state. Attribute names mirror the JS labelFlow record at
    the data boundary; the O(depth) arrays are replaced by single-parent +
    O(constant) summary fields.
    """

    __slots__ = (
        # identity / label
        "label_flow_id", "flow_state_id", "current_node", "current_node_name",
        "label", "flow_mode", "phase", "storage_key", "confidence",
        # introduced_at (label-derived, carried for interning / origin)
        "introduced_at", "origin_node_name", "label_fingerprint",
        # single parent pointer (NOT a list) — DOE walks this chain
        "parent_state", "parent_label_flow_ids", "incoming_edge_id",
        # O(1) substitutes for the five cut arrays. NOTE: the acyclic guard
        # (JS path.includes) is answered by WALKING the parent_state chain, NOT by
        # a stored ancestor set — a per-flow set would be O(depth) and reintroduce
        # the O(N^2) wall on a long chain. depth_min stays (an int, O(1)).
        "depth_min", "filter_derived_seen",
        "transform_digest", "transform_sig", "word_set",
        "local_filter_event_ids",
        # origin (for dedup key + DOE origin_class)
        "origin_node", "origin_boundary",
        # trigger / source-intro bookkeeping (carried, not path arrays)
        "trigger_context", "source_intro_applied_nodes",
        # cycle bookkeeping (sets, not path arrays)
        "_cycle_nodes", "cycle_handling",
        # termination
        "terminated", "termination_reason", "truncated",
        # merge relationships (id lists, output-shape-bounded)
        "merge_group_ids", "parent_label_origin",
        # provenance id accumulation (label-derived; not path arrays)
        "origin_ids", "provenance_event_ids",
        # latest route event id for this hop (full event goes to the global list)
        "route_event_id",
    )

    def __init__(self, **kw):
        # identity / label
        self.label_flow_id = kw.get("label_flow_id", "")
        self.flow_state_id = kw.get("flow_state_id", "")
        self.current_node = kw.get("current_node", "")
        self.current_node_name = kw.get("current_node_name", "")
        self.label = kw.get("label")
        self.introduced_at = kw.get("introduced_at", "")
        self.origin_node_name = kw.get("origin_node_name", "")
        self.label_fingerprint = kw.get("label_fingerprint", "")
        self.flow_mode = kw.get("flow_mode", "may_flow")
        self.phase = kw.get("phase", "after_action")
        self.storage_key = kw.get("storage_key", "")
        self.confidence = kw.get("confidence", 0.3)
        # parent
        self.parent_state = kw.get("parent_state")
        self.parent_label_flow_ids = kw.get("parent_label_flow_ids", [])
        self.incoming_edge_id = kw.get("incoming_edge_id", "")
        # O(1) substitutes
        self.depth_min = kw.get("depth_min", 1)
        self.filter_derived_seen = kw.get("filter_derived_seen", False)
        self.transform_digest = kw.get("transform_digest", [])
        self.transform_sig = kw.get("transform_sig", "")
        self.word_set = kw.get("word_set", set())
        self.local_filter_event_ids = kw.get("local_filter_event_ids", [])
        # origin
        self.origin_node = kw.get("origin_node", "")
        self.origin_boundary = kw.get("origin_boundary")
        # trigger / source-intro
        self.trigger_context = kw.get("trigger_context", [])
        self.source_intro_applied_nodes = kw.get("source_intro_applied_nodes", [])
        # cycle
        self._cycle_nodes = kw.get("_cycle_nodes", frozenset())
        self.cycle_handling = kw.get("cycle_handling", "")
        # termination
        self.terminated = kw.get("terminated", False)
        self.termination_reason = kw.get("termination_reason", "")
        self.truncated = kw.get("truncated", False)
        # merge
        self.merge_group_ids = kw.get("merge_group_ids", [])
        self.parent_label_origin = kw.get("parent_label_origin", "")
        # provenance
        self.origin_ids = kw.get("origin_ids", [])
        self.provenance_event_ids = kw.get("provenance_event_ids", [])
        self.route_event_id = kw.get("route_event_id", "")


# Port of buildFlowStateKey (graph-transfer-analyzer.js:1294-1310) + design-B
# additions transform_sig (9th) + origin_node (10th). The first 8 components are
# byte-identical to the JS key.
def _origin_class_of(state):
    """origin equivalence class = trust_boundary/data_surface of the origin node —
    the SAME granularity DOE dedups on (originClass, doe-analyzer.js:491-498;
    test_flood_granularity_alignment.py:33-36). Two sources sharing a boundary
    collapse to one class, exactly as DOE would fold them into one judgment unit."""
    ob = getattr(state, "origin_boundary", None) or {}
    return f"{ob.get('trust_boundary') or 'unknown'}/{ob.get('data_surface') or 'unknown'}"


# Port of buildFlowStateKey (graph-transfer-analyzer.js:1294-1310) + design-B
# additions transform_sig (9th) + origin_CLASS (10th). The first 8 components are
# byte-identical to the JS key.
#
# The 10th component was ORIGINALLY origin_node (exact node id). That over-
# partitioned the flow-state index: two sources sharing a trust boundary reached a
# sink as DISTINCT states even though DOE folds them into ONE judgment unit
# (DOE keys on origin_class, never origin_node). On branchy graphs — 00001, 00004
# (self-improving family) — this defeated JS's O(V) convergence and drove the
# flood into path-enumeration (queue grew ~7x faster; 00001 never converged).
# Using origin_class here restores 1:1 alignment with the DOE unit AND the
# convergence the 8-tuple JS key had. The 4 granularity-alignment tests are the
# lock: same-class sources must collapse, different-class must stay distinct.
def build_flow_state_key(state):
    label = state.label or {}
    return "|".join([
        state.current_node or "",
        label.get("label") or "",
        label.get("category") or "",
        label.get("subtype") or "",
        label_availability(label, state),
        state.storage_key or "",
        state.flow_mode or "",
        state.phase or "after_action",
        # --- design-B additions ---
        # transform_sig deliberately REMOVED from the key: it encodes the full
        # ordered path prefix, so it grows without bound on cycles
        # (redact>redact>...) and turns the fixpoint flood into path enumeration
        # (space explosion — diagC isolated it as the sole unbounded driver).
        # The key is now JS-8 + origin_class, a strict refinement of the JS-8
        # tuple DOE consumed safely for years; cycles now fold at the dedup layer
        # (same node/label/availability/origin_class => merge => terminate). DOE
        # rebuilds transform_seq itself from the single parent chain, reading
        # FCG's transform_sig only as a boolean — see flood-transform-sig-dekey plan.
        _origin_class_of(state),
        # --- reduction antichain (order-free, bounded) ---
        # The set of maximal reductions applied before egress. Unlike transform_sig
        # this is a SET over a fixed 5-element universe (order collapses, cycles add
        # nothing once maximal), so it is BOUNDED by the poset's antichain count —
        # NOT by the path count. Adding it makes the key a strict refinement (A1
        # still holds); it separates a reducing path from a non-reducing one so
        # reduction_applied is homogeneous per bucket and the conservative-AND merge
        # no longer blurs "protected how" — DOE/LLM see the exact protection kind.
        reduction_profile_sig(state.transform_digest) if _REDUCTION_KEY_ON else "",
    ])


# Port of labelAvailability (graph-transfer-analyzer.js:1313-1318)
def label_availability(label=None, state=None):
    label = label or {}
    flow_mode = getattr(state, "flow_mode", None) if state is not None else None
    if flow_mode == "storage_read":
        return "stored"
    if flow_mode == "source_introduction":
        return "generated" if label.get("mode") == "derived" else "raw"
    if is_derived_label(label, state):
        return "transformed"
    return label.get("mode") or "raw"


# Port of isDerivedLabel (graph-transfer-analyzer.js:1320-1330).
# The JS scans the flow's accumulated ``filter_events`` for any of 6 derived
# types. We accumulate that as the O(1) boolean ``filter_derived_seen`` down the
# chain, so no array is needed.
def is_derived_label(label=None, state=None):
    label = label or {}
    if label.get("mode") == "derived":
        return True
    return bool(getattr(state, "filter_derived_seen", False))


class AncestorPath:
    """A ``__contains__`` view over a StateNode's ancestry that WALKS the single
    parent_state pointer instead of materializing a per-flow set.

    This is what keeps the flood O(N) rather than O(N^2) on a long chain: the
    acyclic guard (JS ``path.includes(target)``) is answered by walking parents,
    so no StateNode stores a depth-scaling set. The walk includes the flow's own
    current_node (matching JS, where node_path ends with the current node).
    """

    __slots__ = ("_flow",)

    def __init__(self, flow):
        self._flow = flow

    def __contains__(self, node_id):
        node = self._flow
        while node is not None:
            if node.current_node == node_id:
                return True
            node = node.parent_state
        return False


def ancestor_path(flow):
    return AncestorPath(flow)


def hop_marks_derived(filter_events):
    """Whether this hop's filter events include a derived-marking type (feeds the
    accumulated ``filter_derived_seen``). Mirrors the membership test in
    isDerivedLabel over just this hop's events."""
    return any(ev.get("type") in _DERIVED_EVENT_TYPES for ev in (filter_events or []))


# --- transform_digest / transform_sig (design B) -------------------------------
# Real transforms are appended in flood-advance order (== execution order,
# safety-critical). Each entry mirrors summarizeTransform (evidence-pack.js:209)
# minus DOE's presentation-only ``effect`` field.
from .constants import REAL_TRANSFORM_TYPES, REDUCTION_SET


def _label_text(label):
    """Port of labelText (evidence-pack.js:203-207)."""
    if label is None:
        return ""
    if isinstance(label, str):
        return label
    return label.get("label") or ".".join(
        p for p in [label.get("category"), label.get("subtype")] if p) or ""


def summarize_transform(ev=None):
    """Port of summarizeTransform (evidence-pack.js:209-218) WITHOUT ``effect``.
    Returns ``{type, from_label?, to_label?}`` — keys omitted (JS undefined→drop)
    when empty, and ``to_label`` omitted when equal to ``from_label``."""
    ev = ev or {}
    type_ = ev.get("type") or ""
    if not type_:
        return None
    from_ = _label_text(ev.get("from_label") or ev.get("dropped_label")
                        or ev.get("context_label") or ev.get("kept_label"))
    to_ = _label_text(ev.get("introduced_label") or ev.get("kept_label"))
    out = {"type": type_}
    if from_:
        out["from_label"] = from_
    if to_ and to_ != from_:
        out["to_label"] = to_
    return out


def digest_from_hop(filter_events):
    """The real-transform digest entries produced by this hop's filter events, in
    order. Only REAL_TRANSFORM_TYPES enter (source_introduction / unknown_may_flow
    / artifact_production excluded), matching evidence-pack.js's REAL set."""
    out = []
    for ev in (filter_events or []):
        if ev.get("type") not in REAL_TRANSFORM_TYPES:
            continue
        t = summarize_transform(ev)
        if t:
            out.append(t)
    return out


def transform_sig_of(transform_digest):
    """``'>'``-join of the digest types. Empty string for the KEY; callers emit
    ``sig or 'none'`` for the OUTPUT field to match DOE transform_seq's literal
    'none' (doe-analyzer.js:473)."""
    return ">".join(t["type"] for t in (transform_digest or []))


def reduction_applied_of(transform_digest):
    """True iff any digest entry is a reduction-kind transform (see REDUCTION_SET).
    Because the filter runs on the hop OUT of a node, a state's digest at
    sink-arrival holds only pre-egress transforms, so this is 'reduced before
    leaving'."""
    return bool(REDUCTION_SET & {t["type"] for t in (transform_digest or [])})


def reduction_profile_of(transform_digest):
    """The reduction ANTICHAIN of a digest: the maximal mutually-incomparable
    reduction types applied (see constants.reduction_antichain). Generalizes the
    reduction_applied bit — ``reduction_applied == bool(reduction_profile)`` —
    while telling DOE/LLM WHICH kinds of protection ran. Order-free and bounded
    by the poset (never the path count), so it is safe as a dedup-key component.
    Returns a sorted tuple; the '+'-join is the key/output surface form."""
    return reduction_antichain(t["type"] for t in (transform_digest or []))


def reduction_profile_sig(transform_digest):
    """``'+'``-join of the reduction antichain (sorted set semantics — order-free,
    unlike transform_sig's '>' sequence). Empty antichain -> '' for the KEY;
    callers emit ``sig or 'none'`` for the OUTPUT field."""
    return "+".join(reduction_profile_of(transform_digest))


# --- word_set (design B) -------------------------------------------------------
# task_need is a bag-of-words keyword-overlap signal on the DOE side; word_set is
# the FCG-side union of label surface tokens along the path. Exact token parity
# is NOT required (DOE derives task_need from rules/LLM, not from this bag), so a
# plain tokenizer + union suffices. Emitted sorted for determinism.
import re

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def seed_word_set(label):
    """Seed tokens from a label's text surface (field/label/subtype/evidence)."""
    label = label or {}
    text = " ".join(str(v) for v in [
        label.get("field_name"), label.get("field_path"),
        label.get("label"), label.get("subtype"),
        label.get("evidence_text"),
    ] if v)
    return set(_TOKEN_RE.findall(text.lower()))


def label_fingerprint(label):
    """Port of the label_fingerprint hash (graph-transfer-analyzer.js:1580).
    JS: ``label_${shortHash(`${label.label}:${label.origin_node}:${label.introduced_at}:${label.evidence_kind || ''}`)}``
    — colon-joined, 4 fields. ``None`` fields serialize as JS ``undefined`` would
    in a template literal ("undefined"); the compact_label upstream normalizes
    missing values so these are strings in practice."""
    label = label or {}
    parts = ":".join([
        _tmpl(label.get("label")),
        _tmpl(label.get("origin_node")),
        _tmpl(label.get("introduced_at")),
        label.get("evidence_kind") or "",
    ])
    return "label_" + short_hash(parts)


def _tmpl(value):
    """Mirror JS template-literal string coercion: ``${undefined}`` → 'undefined',
    ``${null}`` → 'null', else String(value)."""
    if value is None:
        return "undefined"
    return str(value)
