"""Program-owned graph stages and their finite correction interface."""
from dataclasses import replace

from skillflow.common.source_evidence import _json_object
from skillflow.common.validation import StructuralValidationError, structural_error

FACTS = "graph_facts_v1"
UPDATES = "graph_updates_v1"
REPAIR_IDENTITY = "skillflow-graph-repair-input-v3"
PRIOR_REPAIR_IDENTITY = "skillflow-graph-repair-input-v2"
ARCHIVED_REPAIR_IDENTITY = "skillflow-graph-repair-input-v1"


def rejected_facts(evidence):
    material = evidence["material"]
    return material.get("candidate", material["response"])


def _repair_base(previous, files, accepted, archived, normalize_blocks):
    from .graph_facts import assemble_graph_facts, from_accepted_cfg
    if not accepted:
        try:
            facts = _json_object(previous)
        except (ValueError, TypeError):
            return None
        blocks = facts.get("blocks")
        if (not isinstance(blocks, list) or not any(isinstance(block, dict)
                and isinstance(block.get("ref"), str) and block["ref"].strip() for block in blocks)):
            return None
    try:
        options = {"files": files, "archived": archived, "normalize_blocks": normalize_blocks}
        return from_accepted_cfg(previous, **options) if accepted else assemble_graph_facts(facts, **options)
    except ValueError:
        return None


def _repair_material(base, previous, accepted, findings, files):
    from .graph_slots import plan_graph_repair
    identity = ARCHIVED_REPAIR_IDENTITY if base.archived else REPAIR_IDENTITY if base.normalize_blocks else PRIOR_REPAIR_IDENTITY
    return {"identity": identity, "previous": previous, "accepted": accepted,
            "findings": findings, "plan": plan_graph_repair(base, findings=findings, files=files)}


def repair_input(*, files, previous, findings, accepted, archived=False, normalize_blocks=True, failure_evidence=None):
    base = _repair_base(previous, files, accepted, archived, normalize_blocks)
    if base is None:
        return None
    if failure_evidence is not None and base.normalize_blocks:
        from .failed_stage_material import checked_structural_failure
        if (accepted or not checked_structural_failure(failure_evidence, stage="graph", files=files)
                or previous != rejected_facts(failure_evidence)):
            raise ValueError("Patch diagnostics must belong to this rejected source-bound graph")
        rejected = [row for row in failure_evidence["material"]["validation"]["diagnostics"]
                    if row["path"].startswith("/updates/")]
        base = replace(base, patch_diagnostics=rejected)
    return _repair_material(base, previous, accepted, findings, files)


def checked_repair(material, files, *, archived=False, normalize_blocks=True):
    if (not isinstance(material, dict) or set(material) != {"identity", "previous", "accepted", "findings", "plan"}
            or type(material["accepted"]) is not bool or not isinstance(material["plan"], dict)
            or not isinstance(material["plan"].get("base"), dict)):
        raise ValueError("Missing exact graph repair input")
    base = _repair_base(material["previous"], files, material["accepted"], archived, normalize_blocks)
    if base is not None and base.normalize_blocks and not material["accepted"]:
        # The stage reader checks this input against the terminal failure receipt.
        base = replace(base, patch_diagnostics=material["plan"]["base"].get("patch_diagnostics", []))
    if base is None or _repair_material(base, material["previous"], material["accepted"], material["findings"], files) != material:
        raise ValueError("Graph repair plan does not match its source and base")
    return base, material["plan"]


def repair_slots(plan):
    return plan["slots"]


def revision_paths(run):
    base = run / "graph/initial.json"
    if not base.is_file():
        base = run / "audit/failed-stages/graph.json"
    return base, run / "review/result.json", run / "graph/revision-input.json"


def load_revision_input(directory, path, files, dependencies, *, archived=False, normalize_blocks=True):
    from .online import read
    base_path, review_path, plan_path = revision_paths(directory.parent.parent)
    if path != plan_path or tuple(dependencies[-3:]) != (base_path, review_path, plan_path):
        raise ValueError("Graph revision is not bound to the accepted/rejected graph and its review")
    accepted = base_path.name == "initial.json"
    base = read(base_path)
    if not accepted:
        from .failed_stage_material import checked_structural_failure
        if not checked_structural_failure(base, stage="graph", files=files):
            raise ValueError("Graph revision base is not a source-bound rejected GraphFacts draft")
    review = read(review_path).get("review") or {}
    expected = repair_input(files=files, previous=base["cfg"] if accepted else rejected_facts(base),
                            accepted=accepted, archived=archived, normalize_blocks=normalize_blocks,
                            failure_evidence=None if accepted else base, findings=[row for row in review.get("findings", [])
                                                         if row["domain"] == "cfg"])
    if expected is None or read(path) != {"repair": expected}:
        raise ValueError("Graph revision input differs from its bound source, graph, or findings")
    return expected


def _accepted(assembly):
    if assembly.cfg is None:
        diagnostics = assembly.gaps
        if assembly.normalize_blocks:
            from .graph_slots import structural_slots
            _, gaps, _ = structural_slots(assembly)
            diagnostics = [*gaps, *assembly.patch_diagnostics]
        raise StructuralValidationError(diagnostics or [{
            "code": "graph_facts_incomplete", "path": "", "message": "Graph facts do not compile"}])
    return {"cfg": assembly.cfg, "assembly": assembly.to_receipt()}


def validate_graph(kind, value, context):
    from .graph_facts import assemble_graph_facts
    from .graph_slots import apply_graph_updates
    files = context["files"]
    archived = context.get("archived_graph", False)
    normalize_blocks = context.get("normalize_blocks", True)
    if kind == UPDATES:
        base, plan = checked_repair(context["graph_repair"], files, archived=archived, normalize_blocks=normalize_blocks)
    try:
        if kind == FACTS:
            strategy = context.get("graph_facts_strategy")
            assembly = strategy.merged_assembly(value) if strategy else None
            if assembly is None:
                assembly = assemble_graph_facts(value, files=files, archived=archived, normalize_blocks=normalize_blocks)
        else:
            assembly = apply_graph_updates(base, plan, value, files=files)
    except StructuralValidationError:
        raise
    except ValueError as error:
        raise structural_error("graph_facts" if kind == FACTS else "graph_updates", "", str(error)) from error
    return _accepted(assembly)


class GraphFactsCorrection:
    identity = "skillflow-graph-facts-correction-v4"

    def __init__(self, files, *, archived=False, normalize_blocks=True):
        self.files = files
        self.archived = archived
        self.normalize_blocks = normalize_blocks and not archived
        if not self.normalize_blocks and self.identity == "skillflow-graph-facts-correction-v4":
            self.identity = "skillflow-graph-facts-correction-v2" if archived else "skillflow-graph-facts-correction-v3"
        self._merged = None

    def merged_assembly(self, candidate):
        if self._merged is not None and self._merged.facts == candidate:
            return self._merged
        return None

    def _plan(self, candidate):
        return repair_input(files=self.files, previous=candidate, findings=[], accepted=False, archived=self.archived,
                            normalize_blocks=self.normalize_blocks)

    def can_correct(self, candidate, diagnostics):
        material = self._plan(candidate)
        return material is not None and bool(repair_slots(material["plan"]))

    def build_prompt(self, base_prompt, candidate, diagnostics):
        from .prompts import build_graph_updates_prompt
        return build_graph_updates_prompt(files=self.files, plan=self._plan(candidate)["plan"], archived_v17=self.archived,
                                          normalize_blocks=self.normalize_blocks)

    def merge(self, candidate, response):
        from .graph_slots import apply_graph_updates
        base, plan = checked_repair(self._plan(candidate), self.files, archived=self.archived, normalize_blocks=self.normalize_blocks)
        try:
            self._merged = apply_graph_updates(base, plan, _json_object(response), files=self.files)
            return self._merged.facts
        except StructuralValidationError:
            raise
        except ValueError as error:
            raise structural_error("graph_updates", "", str(error)) from error
