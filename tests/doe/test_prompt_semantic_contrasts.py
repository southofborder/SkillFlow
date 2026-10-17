"""Reference contrasts inspect analysis consequences, not model accuracy."""
from copy import deepcopy

from skillflow.doe.demand_engine import DemandEngine
from skillflow.doe.demand_index import build_demand_target_index
from skillflow.doe.sensitivity_material import joint_demands
from skillflow.propagation.annotation.binding_examples import example_material
from skillflow.propagation.annotation.compiler import compile_response
from skillflow.propagation.annotation.prompt_examples import prompt_examples
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.contracts.task import Task
from skillflow.propagation.loading import materials_from_result
from skillflow.propagation.solver import propagate


def solve(index, field):
    fixture = prompt_examples()[index]
    return solve_fixture(fixture, field)


def solve_fixture(fixture, field):
    material = example_material(fixture)
    raw, compiled, mapping = compile_response(fixture[field], material)
    propagated = propagate(material["cfg"], to_payload(compiled))
    assert propagated.status == "complete", propagated.diagnostics
    facts = materials_from_result(propagated, material=material, raw_annotation=raw,
                                  compiled_annotation=compiled, mapping=mapping)
    engine = DemandEngine(facts, Task.model_validate(material["task"]), facts.annotation,
        joint_demands(facts.annotation), build_demand_target_index(facts.cfg, raw))
    solved = engine.solve()
    assert solved == DemandEngine(facts, Task.model_validate(material["task"]), facts.annotation,
        joint_demands(facts.annotation), build_demand_target_index(facts.cfg, raw)).solve(queue_order="lifo")
    return engine, solved


def rows(engine, solved, opcode, *, node_kind="op_input"):
    return [row for row in solved["derivations"].values()
            if row["node"]["kind"] == node_kind
            and engine.ops[row["node"]["operation_id"]]["spec"]["op"] == opcode]


def test_filter_shape_and_predicate_are_not_complete_members_or_collection_truth():
    good_engine, good = solve(0, "annotation")
    bad_engine, bad = solve(0, "contrast")
    good_rows = rows(good_engine, good, "filter_items", node_kind="op_output")
    bad_rows = rows(bad_engine, bad, "filter_items", node_kind="op_output")
    assert {row["property"] for row in good_rows} <= {"shape", "cardinality"}
    assert {"value", "truth"} <= {row["property"] for row in bad_rows}
    predicate_rows = rows(good_engine, good, "filter_items")
    assert any("ready" in row["path"] for row in predicate_rows)


def test_second_submission_does_not_inherit_first_submission_demands():
    good_engine, good = solve(1, "annotation")
    bad_engine, bad = solve(1, "contrast")
    good_rows = rows(good_engine, good, "deliver")
    bad_rows = rows(bad_engine, bad, "deliver")
    assert len({row["node"]["operation_id"] for row in good_rows}) == 2
    assert len({row["node"]["operation_id"] for row in bad_rows}) == 1
    assert {row["node"]["slot"] for row in good_rows} == {0, 1}


def test_open_encoding_alone_adds_no_gap_while_current_append_content_is_preserved():
    good_engine, good = solve(2, "annotation")
    bad_engine, bad = solve(2, "contrast")
    assert rows(good_engine, good, "write")
    assert not rows(bad_engine, bad, "write")
    assert good["status"] == bad["status"] == "complete"
    assert any(row["conservative"] for row in good["derivations"].values())
    assert prompt_examples()[2]["annotation"]["realizations"][0]["gaps"] == []


def test_explicit_unrepresented_format_requirement_retains_gap_without_losing_append_content():
    fixture = deepcopy(prompt_examples()[2])
    fixture["source"] += " The stored record must conform to the vendor's Z-format."
    fixture["task_candidate"]["purpose"]["text"] = fixture["source"]
    fixture["task_candidate"]["requirements"][0]["text"] = fixture["source"]
    task_revision = example_material(fixture)["task"]["task_sha256"]
    for field in ("annotation", "contrast"):
        candidate = fixture[field]
        candidate["task_revision_id"] = task_revision
        candidate["realizations"][0].update(status="partial", gaps=[{
            "reason": "The required vendor encoding has not been represented by the abstract append relation.",
            "evidences": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
                "reason": "The source explicitly requires vendor Z-format rather than leaving encoding open."}],
        }])
    good_engine, good = solve_fixture(fixture, "annotation")
    bad_engine, bad = solve_fixture(fixture, "contrast")
    assert rows(good_engine, good, "write") and not rows(bad_engine, bad, "write")
    assert good["status"] == bad["status"] == "partial"
    assert any(row["conservative"] for row in good["derivations"].values())


def test_filter_self_truth_is_the_same_collection_output_error_not_a_predicate_reference():
    fixture = deepcopy(prompt_examples()[0])
    demands = fixture["contrast"]["ir_semantics"]["ir_slot_filter"]["events"][0]["events"][0]["atomic_ops"][0]["demands"]
    demands[1]["target"] = {"kind": "self"}
    engine, solved = solve_fixture(fixture, "contrast")
    assert any(row["property"] == "truth" and row["path"] == []
               for row in rows(engine, solved, "filter_items", node_kind="op_output"))
