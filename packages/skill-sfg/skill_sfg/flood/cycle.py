"""Cycle label-closure fixpoint (port of graph-transfer-analyzer.js:729-871).

A real cycle body is a transform operator T; the closure is the fixpoint
L ∪ T(L) ∪ T²(L) ∪ … of T on the seed label. It serves two consumers: grading
the periodic-leak severity, and supplying the SPECIALIZING members that must
leave the cycle as their own flows.

``propagation_profile`` is INJECTED (a callable) rather than imported, to keep
the dependency DAG acyclic (cycle must not import analyzer). ``apply_filter`` is
likewise injected to avoid importing the full filter surface here.
"""

from .constants import GENERALIZING_DERIVED_CATEGORIES
from .filter import compact_label, dedupe_labels


# Port of closureLabelKey (graph-transfer-analyzer.js:731-737).
# Same uniqueness key as dedupeLabels: [label, origin_node, introduced_at].
def closure_label_key(label=None):
    label = label or {}
    return "|".join([
        label.get("label") or "",
        label.get("origin_node") or "",
        label.get("introduced_at") or label.get("origin_node") or "",
    ])


# Port of isSpecializingClosureMember (graph-transfer-analyzer.js:774-780).
# A member is specializing (must fork its own flow) iff it is NOT the seed AND
# it is either a pseudonymous class or a derived non-generalizing product.
def is_specializing_closure_member(member=None, seed_label=None):
    member = member or {}
    seed_label = seed_label or {}
    if not member:
        return False
    if closure_label_key(member) == closure_label_key(seed_label):
        return False
    if member.get("category") == "pseudonymous_data":
        return True
    if member.get("mode") == "derived" and member.get("category") not in GENERALIZING_DERIVED_CATEGORIES:
        return True
    return False


# Port of computeCycleClosure (graph-transfer-analyzer.js:810-871), reworked to a
# SINGLE algebraic pass ("封顶一圈"). Rather than chasing the fixpoint
# L ∪ T(L) ∪ T²(L) ∪ … — which does not reliably converge on large graphs and was
# the wall on the giant skills — we apply the cycle-body transform T to the SEED
# exactly ONCE. The out-of-cycle set is {seed} ∪ T(seed); products are NOT re-fed
# through T. There is no iteration ceiling to hit, so ``truncated`` is always
# False (analyzer never marks cyclic flows as "cycle_closure_not_converged").
#
# ``max_iterations`` is retained in the signature for call-site compatibility but
# is unused: one turn of the cycle is the model.
# apply_filter / propagation_profile injected (see module docstring).
def compute_cycle_closure(seed_label=None, feedback_cycle_paths=None,
                          profiles_by_node=None, nodes_by_id=None,
                          max_iterations=16, apply_filter=None, propagation_profile=None):
    feedback_cycle_paths = feedback_cycle_paths or []
    profiles_by_node = profiles_by_node or {}
    nodes_by_id = nodes_by_id or {}

    seed_compact = compact_label(seed_label)
    by_key = {}
    by_key[closure_label_key(seed_label)] = seed_compact

    # One turn of the cycle: transform the seed alone, once, along every feedback
    # cycle path. We feed ``seed_compact`` (not the accumulating set), so this is
    # exactly the original fixpoint's first iteration with no re-feed.
    for cycle_path in feedback_cycle_paths:
        for node_id in cycle_path:
            profile = profiles_by_node.get(node_id)
            if not profile:
                continue
            result = apply_filter(
                label_flow={
                    "label": seed_compact,
                    "trigger_context": [],
                    # Suppress this node's OWN source introduction: the closure is
                    # what the seed TRANSFORMS INTO, not every label the cycle
                    # nodes independently introduce.
                    "source_intro_applied_nodes": [node_id],
                    "flow_mode": "may_flow",
                },
                current_profile=propagation_profile(profile),
                edge={},
            )
            for branch in (result.get("branches") or []):
                # A source_introduction branch is the node introducing its own
                # label, not a transform of the seed — skip (defensive).
                if branch.get("flow_mode") == "source_introduction":
                    continue
                produced = compact_label(branch.get("label"))
                if not produced:
                    continue
                key = closure_label_key(produced)
                if key not in by_key:
                    by_key[key] = produced

    return {"labels": dedupe_labels(list(by_key.values())), "truncated": False}
