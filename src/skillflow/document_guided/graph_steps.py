"""Program-owned graph stages and their finite correction interface."""
from skillflow.common.source_evidence import _json_object
from skillflow.common.validation import StructuralValidationError, structural_error

FACTS = "graph_facts_v1"
UPDATES = "graph_updates_v1"
REPAIR_IDENTITY = "skillflow-graph-repair-input-v1"


def rejected_facts(evidence):
    material = evidence["material"]
    return material.get("candidate", material["response"])


def repair_input(*, files, previous, findings, accepted):
    from .graph_facts import assemble_graph_facts, from_accepted_cfg
    from .graph_slots import plan_graph_repair
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
        base = (from_accepted_cfg(previous, files=files) if accepted else
                assemble_graph_facts(facts, files=files))
    except ValueError:
        return None
    return {"identity": REPAIR_IDENTITY, "previous": previous, "accepted": accepted,
            "findings": findings, "plan": plan_graph_repair(base, findings=findings, files=files)}


def checked_repair(material, files):
    from .graph_facts import assemble_graph_facts, from_accepted_cfg
    if not isinstance(material, dict) or set(material) != {"identity", "previous", "accepted", "findings", "plan"} or type(material["accepted"]) is not bool:
        raise ValueError("Missing exact graph repair input")
    expected = repair_input(files=files, previous=material["previous"],
                            findings=material["findings"], accepted=material["accepted"])
    if expected != material:
        raise ValueError("Graph repair plan does not match its source and base")
    base = (from_accepted_cfg(material["previous"], files=files) if material["accepted"] else
            assemble_graph_facts(_json_object(material["previous"]), files=files))
    return base, material["plan"]


def repair_slots(plan):
    return plan["slots"]


def revision_paths(run):
    base = run / "graph/initial.json"
    if not base.is_file():
        base = run / "audit/failed-stages/graph.json"
    return base, run / "review/result.json", run / "graph/revision-input.json"


def load_revision_input(directory, path, files, dependencies):
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
                            accepted=accepted, findings=[row for row in review.get("findings", [])
                                                         if row["domain"] == "cfg"])
    if expected is None or read(path) != {"repair": expected}:
        raise ValueError("Graph revision input differs from its bound source, graph, or findings")
    return expected


def _accepted(assembly):
    if assembly.cfg is None:
        raise StructuralValidationError(assembly.gaps or [{
            "code": "graph_facts_incomplete", "path": "", "message": "Graph facts do not compile"}])
    return {"cfg": assembly.cfg, "assembly": assembly.to_receipt()}


def validate_graph(kind, value, context):
    from .graph_facts import assemble_graph_facts
    from .graph_slots import apply_graph_updates
    files = context["files"]
    if kind == UPDATES:
        base, plan = checked_repair(context["graph_repair"], files)
    try:
        if kind == FACTS:
            strategy = context.get("graph_facts_strategy")
            assembly = strategy.merged_assembly(value) if strategy else None
            if assembly is None:
                assembly = assemble_graph_facts(value, files=files)
        else:
            assembly = apply_graph_updates(base, plan, value, files=files)
    except StructuralValidationError:
        raise
    except ValueError as error:
        raise structural_error("graph_facts" if kind == FACTS else "graph_updates", "", str(error)) from error
    return _accepted(assembly)


class GraphFactsCorrection:
    identity = "skillflow-graph-facts-correction-v1"

    def __init__(self, files):
        self.files = files
        self._merged = None

    def merged_assembly(self, candidate):
        if self._merged is not None and self._merged.facts == candidate:
            return self._merged
        return None

    def _plan(self, candidate):
        return repair_input(files=self.files, previous=candidate, findings=[], accepted=False)

    def can_correct(self, candidate, diagnostics):
        material = self._plan(candidate)
        return material is not None and bool(repair_slots(material["plan"]))

    def build_prompt(self, base_prompt, candidate, diagnostics):
        from .prompts import build_graph_updates_prompt
        return build_graph_updates_prompt(files=self.files, plan=self._plan(candidate)["plan"])

    def merge(self, candidate, response):
        from .graph_slots import apply_graph_updates
        base, plan = checked_repair(self._plan(candidate), self.files)
        try:
            self._merged = apply_graph_updates(base, plan, _json_object(response), files=self.files)
            return self._merged.facts
        except StructuralValidationError:
            raise
        except ValueError as error:
            raise structural_error("graph_updates", "", str(error)) from error
