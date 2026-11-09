"""Copy explicit batches of existing objects, then use the original compilers."""
from copy import deepcopy
from functools import lru_cache

from pydantic import ConfigDict, create_model

from skillflow.common.prompt_format import render_prompt_format
from skillflow.common.source_evidence import _json_object
from skillflow.graph.extraction.candidate import IRAnalysisCandidate
from skillflow.graph.extraction.compiler import compile_candidate
from skillflow.propagation.contracts.profiles import RawAnnotationResponse
from skillflow.propagation.annotation.services import compile_response


@lru_cache(maxsize=None)
def batch_model(kind):
    fields = {
        "graph": (IRAnalysisCandidate, ("blocks", "edges")),
        "graph_globals": (IRAnalysisCandidate, ("entry_block_ref", "constraints", "declared_context_keys", "diagnostics")),
        "locations": (RawAnnotationResponse, ("locations", "location_evidences")),
        "ir": (RawAnnotationResponse, ("ir_semantics",)),
        "globals": (RawAnnotationResponse, ("outcome", "task_revision_id", "realizations", "demands", "expressions", "processing_gaps")),
    }
    if kind not in fields:
        raise ValueError("Unknown batch kind")
    base, names = fields[kind]
    return create_model("Existing_" + kind, __config__=ConfigDict(**base.model_config),
                        **{name: (base.model_fields[name].annotation, deepcopy(base.model_fields[name]))
                           for name in names})


def batch_format(kind):
    return render_prompt_format(batch_model(kind).model_json_schema())


def validate_batch(kind, response):
    value = batch_model(kind).model_validate(_json_object(response)).model_dump(mode="json", exclude_unset=True)
    if kind == "locations" and set(value["locations"]) != set(value["location_evidences"]):
        raise ValueError("Location evidence coverage must match the submitted locations")
    return value


def combine_graph(globals, batches):
    candidate = validate_batch("graph_globals", globals)
    candidate.update(blocks=[], edges=[])
    for batch in batches:
        parsed = validate_batch("graph", batch)
        candidate["blocks"].extend(parsed.get("blocks", []))
        candidate["edges"].extend(parsed.get("edges", []))
    block_refs, instruction_refs, edges = set(), set(), set()
    for block in candidate["blocks"]:
        if block["block_ref"] in block_refs:
            raise ValueError("Duplicate explicitly submitted block reference")
        block_refs.add(block["block_ref"])
        for instruction in block["instructions"]:
            if instruction["instruction_ref"] in instruction_refs:
                raise ValueError("Duplicate explicitly submitted instruction reference")
            instruction_refs.add(instruction["instruction_ref"])
    for edge in candidate["edges"]:
        key = (edge["source_block_ref"], edge["target_block_ref"], edge.get("condition_text"))
        if key in edges:
            raise ValueError("Duplicate explicitly submitted control edge")
        edges.add(key)
    return candidate, compile_candidate(candidate)


def combine_annotation(locations, ir_batches, globals, *, material):
    candidate = validate_batch("locations", locations)
    candidate.update(validate_batch("globals", globals))
    candidate["ir_semantics"] = {}
    for batch in ir_batches:
        parsed = validate_batch("ir", batch)["ir_semantics"]
        if set(parsed) & set(candidate["ir_semantics"]):
            raise ValueError("An IR was submitted by more than one batch")
        candidate["ir_semantics"].update(parsed)
    # Original coverage, evidence, scope, Task, reference and compiler checks.
    return compile_response(candidate, material)
