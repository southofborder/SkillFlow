"""A valid standalone fact file still must match its selected transfer spec."""
from copy import deepcopy
import runpy

import pytest

from skillflow.common.paths import project_root
from skillflow.doe.demand_material import prepare_demand_review, validate_record_spec_structure
from skillflow.propagation.loading import materials_from_result
from tests.doe.components import mutable_components
from tests.doe.test_demand_engine import fixture, inp, local, candidate


def values():
    return fixture([
        {"op": "compute", "inputs": [inp()], "dependencies": ["possible"], "output": "first"},
    ], mode="local")


@pytest.mark.parametrize("change,message", [
    ("drop_operation", "operation coverage"),
    ("drop_event", "event coverage"),
    ("effect", "record effect"),
    ("kind", "operation kind"),
    ("order", "order or precedence"),
])
def test_non_sink_structure_tampering_is_rejected_after_standalone_fact_validation(change, message):
    facts, task, annotation, targets = values()
    altered = deepcopy(facts)
    record = altered.records["ir_filter"]
    transform = next(event for event in record["events"] if event.get("effect") == "transform")
    if change == "drop_operation":
        transform["atomic_ops"].pop(0)
    elif change == "drop_event":
        record["events"].remove(transform)
    elif change == "effect":
        transform["effect"] = None
    elif change == "kind":
        transform["atomic_ops"][0]["op"] = "select_part"
    else:
        record["order"] = "partial"
    # A handoff alone does not encode its selected transfer specification.
    # Removing the last operation is already rejected by the handoff loader;
    # the direct check additionally locks the pairing invariant itself.
    with pytest.raises(ValueError, match=message):
        validate_record_spec_structure(altered, annotation["compiled_annotation"])
    if change != "drop_operation":
        with pytest.raises(ValueError, match=message):
            prepare_demand_review(altered, task, annotation, candidate(targets))
    else:
        with pytest.raises(ValueError):
            prepare_demand_review(altered, task, annotation, candidate(targets))


def test_foreach_instance_body_must_keep_every_compiled_event_and_operation():
    material, metadata, compilation, payload, solved = runpy.run_path(
        str(project_root() / "examples/propagation/processing_demo.py"))["example"]()
    facts = mutable_components(materials_from_result(solved,material=material,raw_annotation=compilation[0],
        compiled_annotation=compilation[1],mapping=compilation[2],source_metadata=metadata))
    validate_record_spec_structure(facts, compilation[1])
    dropped = deepcopy(facts)
    scope = dropped.records["ir_send"]["events"][0]
    scope["instances"][0]["body"].pop(0)
    with pytest.raises(ValueError, match="foreach body coverage"):
        validate_record_spec_structure(dropped, compilation[1])
    dropped = deepcopy(facts)
    body = dropped.records["ir_send"]["events"][0]["instances"][0]["body"]
    event = next(item for item in body if item["effect"] == "transform")
    event["atomic_ops"].pop(0)
    with pytest.raises(ValueError, match="operation coverage"):
        validate_record_spec_structure(dropped, compilation[1])


def test_explicit_precedence_cannot_be_detached_from_a_matching_partial_spec():
    facts, _, annotation, _ = values()
    compiled = deepcopy(annotation["compiled_annotation"])
    compiled["ir_semantics"]["ir_filter"]["precedence"] = [{
        "before": {"event_index": 0, "op_index": 0, "body_event_index": None},
        "after": {"event_index": 1, "op_index": 0, "body_event_index": None}}]
    with pytest.raises(ValueError, match="order or precedence"):
        validate_record_spec_structure(facts, compiled)
