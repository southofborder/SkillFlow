"""Task evidence remains bound to the same source and sealed Task version."""
from copy import deepcopy

import pytest

from skillflow.doe.demand_material import prepare_demand_review
from skillflow.propagation.annotation.compiler import compile_response
from skillflow.propagation.material import prepare_material
from skillflow.propagation.contracts.task import Task, task_source_files
from tests.doe.test_demand_engine import fixture, inp, candidate


def _fixture():
    return fixture([{"op": "select_part", "input": inp(), "path": ["body"], "output": "body"}])


def test_joint_source_cannot_rebind_a_valid_doe_file_to_other_text():
    facts, task, annotation, targets = _fixture()
    changed = deepcopy(annotation)
    changed["material"]["source"]["files"][0]["content"] += "\nDifferent source.\n"
    with pytest.raises(ValueError, match="source differs from frozen facts"):
        prepare_demand_review(facts, task, changed, candidate(targets))


def test_task_version_is_bound_to_the_same_material_and_external_inputs_are_rejected():
    from skillflow.propagation.solver import propagate
    from skillflow.propagation.annotation.services import to_payload
    from skillflow.propagation.loading import materials_from_result
    facts, task, annotation, targets = _fixture()
    from tests.doe.helpers import source_task
    from skillflow.propagation.contracts.task import CandidateTask
    changed = {key: deepcopy(task.model_dump(mode="json")[key]) for key in CandidateTask.model_fields}
    changed["purpose"]["text"] += " Preserve the original body value."
    new_task = source_task(annotation["material"]["source"], changed)
    material = prepare_material(annotation["material"]["source"], facts.cfg, task_baseline=new_task)
    raw = deepcopy(annotation["raw_annotation"])
    raw["task_revision_id"] = new_task.task_sha256
    checked, compiled, mapping = compile_response(raw, material)
    new_facts = materials_from_result(propagate(material["cfg"],to_payload(compiled)),material=material,
        raw_annotation=checked,compiled_annotation=compiled,mapping=mapping)
    prepare_demand_review(new_facts,new_task,new_facts.annotation,candidate(targets))
    with pytest.raises(ValueError,match="differs"):
        prepare_demand_review(facts,new_task,new_facts.annotation,candidate(targets))
    for retired in ("user_request", "policies"):
        with pytest.raises(TypeError):
            prepare_material(material["source"], facts.cfg, **{retired: "Not a supported input"})
