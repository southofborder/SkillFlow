from copy import deepcopy
import json

import pytest

from skillflow.document_guided.batches import (
    batch_model, combine_annotation, combine_graph, validate_batch,
)
from skillflow.graph.extraction.candidate import IRAnalysisCandidate
from skillflow.propagation.contracts.profiles import RawAnnotationResponse


def graph_example():
    return {"entry_block_ref": "read", "constraints": ["Return the acquired value."],
            "declared_context_keys": ["input"], "diagnostics": [], "blocks": [
        {"block_ref": "read", "block_name": "Read", "data_source_kind": "context", "instructions": [
            {"instruction_ref": "acquire", "opcode": "read_context", "inputs": [{"type": "context_key", "identifier": "input"}],
             "outputs": [{"type": "result", "identifier": "acquired"}]},
            {"instruction_ref": "jump", "opcode": "dispatch"}]},
        {"block_ref": "finish", "block_name": "Return", "instructions": [
            {"instruction_ref": "done", "opcode": "return", "inputs": [{"type": "result", "identifier": "acquired"}]}]}],
            "edges": [{"source_block_ref": "read", "target_block_ref": "finish"}]}


def graph_batches():
    candidate = graph_example()
    header = {key: value for key, value in candidate.items() if key not in {"blocks", "edges"}}
    return header, [{"blocks": candidate["blocks"][:1], "edges": candidate["edges"]},
                    {"blocks": candidate["blocks"][1:], "edges": []}]


def test_graph_batches_preserve_explicit_cross_batch_values_and_compile():
    header, batches = graph_batches()
    before = deepcopy((header, batches))
    candidate, result = combine_graph(header, batches)
    assert result.ok, result.diagnostics
    assert len(candidate["edges"]) == 1
    assert len(result.cfg.blocks) == 2
    assert result.cfg.blocks["block_002"].instructions[0].inputs[0].identifier == "result_001"
    assert before == (header, batches)


def test_missing_edge_or_producer_is_not_repaired():
    header, batches = graph_batches()
    batches[1]["blocks"][0]["instructions"][0]["inputs"][0]["identifier"] = "not_produced"
    candidate, result = combine_graph(header, batches)
    assert not result.ok
    assert candidate["blocks"][1]["instructions"][0]["inputs"][0]["identifier"] == "not_produced"
    assert len(candidate["edges"]) == 1


def test_duplicate_graph_objects_and_batch_overreach_rejected():
    header, batches = graph_batches()
    with pytest.raises(ValueError, match="Duplicate"):
        combine_graph(header, [*batches, batches[0]])
    with pytest.raises(ValueError):
        validate_batch("graph", {**batches[0], "entry_block_ref": "read"})
    with pytest.raises(ValueError):
        validate_batch("locations", {"locations": {}, "location_evidences": {}, "demands": []})


def test_projection_fields_partition_actual_contracts():
    for base, kinds in [(IRAnalysisCandidate, ("graph", "graph_globals")),
                        (RawAnnotationResponse, ("locations", "ir", "globals"))]:
        names = [name for kind in kinds for name in batch_model(kind).model_fields]
        assert len(names) == len(set(names))
        assert set(names) == set(base.model_fields)


def annotation_batches():
    from skillflow.propagation.annotation.binding_examples import example_material, sink_demand_examples
    example = sink_demand_examples()[0]
    value = example["annotation"]
    locations = {key: value[key] for key in ("locations", "location_evidences")}
    irs = [{"ir_semantics": {ir: spec}} for ir, spec in value["ir_semantics"].items()]
    globals = {key: item for key, item in value.items() if key not in {*locations, "ir_semantics"}}
    return locations, irs, globals, example_material(example)


def test_annotation_batch_composition_uses_full_original_compiler():
    locations, irs, globals, material = annotation_batches()
    before = deepcopy((locations, irs, globals, material))
    raw, compiled, mapping = combine_annotation(locations, irs, globals, material=material)
    assert compiled["demands"] and mapping["events"]
    assert set(raw["ir_semantics"]) == set().union(*(row["ir_semantics"] for row in irs))
    assert before == (locations, irs, globals, material)
    with pytest.raises(ValueError, match="more than one"):
        combine_annotation(locations, [*irs, irs[0]], globals, material=material)
    with pytest.raises(ValueError):
        combine_annotation(locations, irs[1:], globals, material=material)
    wrong = deepcopy(globals)
    wrong["task_revision_id"] = "wrong-task"
    with pytest.raises(ValueError):
        combine_annotation(locations, irs, wrong, material=material)


def test_annotation_missing_payload_demands_are_not_invented():
    from skillflow.propagation.annotation.binding_examples import example_material, sink_demand_examples
    example = sink_demand_examples()[0]
    value = example["contrast"]
    locations = {key: value[key] for key in ("locations", "location_evidences")}
    irs = [{"ir_semantics": value["ir_semantics"]}]
    globals = {key: item for key, item in value.items() if key not in {*locations, "ir_semantics"}}
    raw, _, _ = combine_annotation(locations, irs, globals, material=example_material(example))
    assert raw["demands"] == value["demands"]
