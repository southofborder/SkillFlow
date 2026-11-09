"""Concrete GA4 v8 failures through the existing v9 compilation and backend.

No original answers are loaded, repaired, replayed or modified. These authored
boundary examples demonstrate representation capability, not online coverage.
"""
from copy import deepcopy
import json

import pytest

from skillflow.doe.demand_material import prepare_demand_review
from skillflow.doe.formal_runner import run_doe
from skillflow.doe.sensitivity_material import prepare_sensitivity_review
from skillflow.propagation.models import FlowLocation
from skillflow.propagation.contracts.task import Task
from skillflow.propagation.runner import save_propagation_run
from tests.propagation.component_helpers import accepted_annotation
from tests.document_guided.ga4_alignment_v9_cases import (
    EACH, bulk_fixture, cache_clock_fixture, comparison_save_fixture, environment_fixture, inspection_fixture,
    metadata_fixture, report_rows_fixture, solve,
)
from tests.document_guided.test_case_summaries import ga4_fixture


def operations(case, ir):
    return [op for event in case["solved"].records.get(ir).events for op in event.atomic_ops]


def data(case, identity):
    return case["solved"].registry.get(identity)


def one(ids):
    assert len(ids) == 1
    return next(iter(ids))


def demand_review(case):
    return prepare_demand_review(case["facts"], Task.model_validate(case["material"]["task"]),
        case["facts"].annotation, {"goals": case["compiled"]["demands"], "expressions": case["compiled"]["expressions"]}).to_dict()


def test_public_url_acquisition_normalization_and_real_save_binding():
    case = bulk_fixture(["same", "same", "/other"])
    records = case["solved"].records
    args = records.get("ir_args")
    loop = records.get("ir_normalize").events[0]
    assert {instance.selector for instance in loop.instances} == {0, 1, 2}
    assert len({instance.element for instance in loop.instances}) == 3
    assert loop.collections == args.exit_state.get(FlowLocation(kind="result", name="urls"))
    assert all(data(case, one(instance.yielded)).content.form == "opaque" for instance in loop.instances)
    assert all(event.effect != "model_observe" for instance in loop.instances for event in instance.body)
    report = operations(case, "ir_report")
    response = next(op.outputs[0] for op in report if op.op == "receive")
    sent = next(op.inputs for op in report if op.op == "deliver")
    assert response.isdisjoint(set().union(*sent))
    write, read = operations(case, "ir_save")
    assert write.inputs[0] == response == read.outputs[0]
    assert case["solved"].coverage["ir_return"] == "processed"


def test_empty_urls_return_before_client_api_or_save():
    case = bulk_fixture([])
    for ir in ("ir_filter", "ir_client", "ir_report", "ir_save"):
        assert case["solved"].coverage[ir] == "not_reached"
    assert case["solved"].coverage["ir_empty"] == "processed"
    assert not case["facts"].sinks


def test_filter_contains_actual_mapped_url_collection_and_precedes_client_read():
    case = bulk_fixture(["same", "same"])
    loop = case["solved"].records.get("ir_normalize").events[0]
    build = operations(case, "ir_filter")[0]
    assert build.inputs[1] == loop.outputs
    content = data(case, one(build.outputs[0])).content
    urls = next(part.data for part in content.parts if part.path == ["filter", "inListFilter", "values"])
    assert urls in loop.outputs
    ids = [ir["id"] for ir in case["material"]["cfg"]["blocks"]["nonempty"]["instructions"]]
    assert ids.index("ir_filter") < ids.index("ir_client") < ids.index("ir_report")


def test_inspection_request_nesting_response_projection_and_real_undefined():
    case = inspection_fixture()
    ops = operations(case, "ir_inspect")
    request = data(case, one(ops[0].outputs[0])).content
    assert {tuple(part.path) for part in request.parts} == {
        ("requestBody", "inspectionUrl"), ("requestBody", "siteUrl")}
    response = next(op for op in ops if op.op == "receive")
    projection = next(op for op in ops if op.op == "select_part")
    assert projection.inputs[0] == response.outputs[0]
    undefined = next(op for op in ops if op.op == "compute" and not op.inputs)
    assert data(case, one(undefined.outputs[0])).content.form == "opaque"
    assert data(case, one(undefined.outputs[0])).content.model_dump() != {"form": "literal", "value": None}
    actual_result = ops[-1].outputs[0]
    assert operations(case, "ir_save")[0].inputs[0] == actual_result
    assert actual_result != ops[0].outputs[0]


def test_dotenv_call_return_does_not_replace_environment_and_settings_read_post_versions():
    case = environment_fixture()
    record = case["solved"].records.get("ir_init")
    env = FlowLocation(kind="runtime_context", name="process.env")
    before, after = record.entry_state.get(env), record.exit_state.get(env)
    assert before < after
    all_ops = operations(case, "ir_init")
    returned = next(op.outputs[0] for op in all_ops if op.op == "receive")
    call_send = next(op for op in all_ops if op.op == "deliver")
    assert call_send.inputs == []
    assert returned.isdisjoint(after)
    settings_ops = operations(case, "ir_settings")
    assert settings_ops[0].outputs[0] == after
    selected = [op for op in settings_ops if op.op == "select_part"]
    assert len(selected) == 5 and all(op.inputs[0] == after for op in selected)
    # The results directory is computed from the independently acquired cwd.
    cwd = next(op.outputs[0] for op in settings_ops if op.op == "receive")
    assert any(op.op == "compute" and op.inputs[0] == cwd for op in settings_ops)


def test_indexing_cache_read_write_identity_and_clock_fallback_remain_distinct():
    case = cache_clock_fixture()
    record = case["solved"].records.get("ir_notify")
    ops = operations(case, "ir_notify")
    reads = [op for op in ops if op.op == "read" and op.endpoints[0].name == "indexing_cache"]
    write = next(op for op in ops if op.op == "write")
    assert write.endpoints[0].name == "indexing_cache"
    assert reads and all(op.outputs[0] == write.changes[0].before for op in reads)
    assert write.inputs[0].isdisjoint(write.changes[0].before)
    assert write.changes[0].after > write.changes[0].before
    assert all(change.location.name == "indexing_cache" for change in write.changes)
    clock = [op for op in ops if op.op == "receive" and op.endpoints[0].name == "Date clock"]
    assert len(clock) == 1 and clock[0].inputs == []
    remote = next(op for op in ops if op.op == "receive" and op.endpoints[0].name == "urlNotifications.publish")
    assert clock[0].outputs[0].isdisjoint(remote.outputs[0])
    assert any(event.case and event.case.name == "clock_fallback" for event in record.events)


@pytest.mark.parametrize("path,alternatives", [("batch", 1), ("reindex", 2), ("status", 2)])
def test_real_ga4_exception_sources_are_not_success_values_or_url_computations(path, alternatives):
    material, wire, _ = ga4_fixture(path)
    case = solve(material, wire)
    loop = case["solved"].records.get("ir_call").events[0]
    assert {instance.selector for instance in loop.instances} == {0, 1}
    # The serialized record set is canonicalized by identity, not array order.
    # The mapped source relationship retains the actual position separately.
    mapped = data(case, one(loop.outputs)).content
    assert {member.selector for member in mapped.members} == {0, 1}
    assert all(len(instance.yielded) == alternatives for instance in loop.instances)
    assert bool(loop.completion_groups) == (path == "batch")
    if path == "batch":
        reviewed = demand_review(case)
        assert reviewed["status"] == "complete"
        assert any(row["node"]["kind"] == "collection_output" and row["property"] == "value"
                   for row in reviewed["derivations"].values())
    for instance in loop.instances:
        errors = [op for event in instance.body if event.case.phase == "pre_request_error"
                  for op in event.atomic_ops if op.op == "receive"]
        replies = [op for event in instance.body if event.case.phase == "normal"
                   for op in event.atomic_ops if op.op == "receive"]
        assert errors and all(not op.inputs for op in errors)
        assert set().union(*(op.outputs[0] for op in errors)).isdisjoint(
            set().union(*(op.outputs[0] for op in replies)))
        assert all(data(case, one(op.outputs[0])).origin.acquired_from == "tool:Protected local call exception" for op in errors)


def test_report_row_value_demands_keep_both_each_levels_and_receiver_scope():
    case = report_rows_fixture()
    reviewed = demand_review(case)
    assert reviewed["status"] == "complete"
    assert not any(row["code"] in {"nested_member_demand", "path_widening"} for row in reviewed["diagnostics"])
    summary = next(row for row in reviewed["sinks"] if row["boundary"]["target"] == "summary")
    required = [reviewed["derivations"][key] for key in summary["demanded_information"]]
    assert {json.dumps(row["path"], sort_keys=True) for row in required} == {
        json.dumps(["rows", EACH, field, EACH, "value"], sort_keys=True) for field in ("dimensionValues", "metricValues")}
    saved = next(row for row in reviewed["sinks"] if row["boundary"]["target"] == "saved")
    assert any(reviewed["derivations"][key]["path"] == [] for key in saved["demanded_information"])


def test_comparison_save_binds_caller_responses_and_preserves_metadata_wrapper():
    case = comparison_save_fixture()
    comparison_ops = operations(case, "ir_compare")
    responses = [op.outputs[0] for op in comparison_ops if op.op == "receive"]
    assert len(responses) == 2 and responses[0].isdisjoint(responses[1])
    parts = data(case, one(comparison_ops[-1].outputs[0])).content.parts
    assert next(part.data for part in parts if part.path == ["period1", "data"]) in responses[0]
    assert next(part.data for part in parts if part.path == ["period2", "data"]) in responses[1]
    save_ops = operations(case, "ir_save")
    wrapper = next(op for op in save_ops if op.op == "build")
    write = next(op for op in save_ops if op.op == "write")
    assert write.inputs[0] == wrapper.outputs[0]
    content = data(case, one(wrapper.outputs[0])).content
    assert next(part.data for part in content.parts if part.path == ["data"]) in comparison_ops[-1].outputs[0]
    assert {tuple(part.path) for part in content.parts} == {
        ("metadata", "savedAt"), ("metadata", "propertyId"), ("metadata", "category"), ("metadata", "operation"), ("data",)}
    filepath = case["solved"].records.get("ir_save").exit_state.get(FlowLocation(kind="result", name="filepath"))
    assert filepath.isdisjoint(wrapper.outputs[0])


@pytest.mark.parametrize("whole", [False, True])
def test_discovery_field_requirements_remain_distinct_from_full_metadata(whole):
    case = metadata_fixture(whole=whole)
    reviewed = demand_review(case)
    sink = next(row for row in reviewed["sinks"] if row["boundary"]["target"] == "saved")
    paths = [reviewed["derivations"][key]["path"] for key in sink["demanded_information"]]
    assert bool([] in paths) is whole
    if not whole:
        assert {json.dumps(path, sort_keys=True) for path in paths} == {
            json.dumps(["dimensions", EACH, key], sort_keys=True) for key in ("apiName", "uiName", "description")}


@pytest.mark.parametrize("whole,conclusion", [(False, "excess_supported"), (True, "no_excess_established")])
def test_explicit_sensitive_variant_positive_and_required_whole_negative(whole, conclusion):
    case = metadata_fixture(whole=whole, sensitive_variant=True)
    reviewed = prepare_sensitivity_review(case["facts"], annotation=case["facts"].annotation).to_dict()
    sink = next(row for row in reviewed["sinks"] if row["boundary"]["target"] == "saved")
    assert sink["data_reviews"]
    assert {row["conclusion"] for row in sink["data_reviews"]} == {conclusion}


@pytest.mark.parametrize("fixture", [lambda: bulk_fixture(["a", "a"]), inspection_fixture,
    environment_fixture, cache_clock_fixture, report_rows_fixture, comparison_save_fixture, lambda: metadata_fixture(whole=True)])
def test_corrected_source_projection_commits_propagation_and_doe(tmp_path, monkeypatch, fixture):
    # New authored offline runs only. No historical solver or replay is invoked.
    import socket
    import skillflow.propagation.annotation.runner as annotation_runner
    import skillflow.propagation.runner as propagation_runner
    import skillflow.doe.formal_runner as doe_runner
    identity = propagation_runner.implementation_provenance()
    for module in (annotation_runner, propagation_runner, doe_runner):
        monkeypatch.setattr(module, "implementation_provenance", lambda: deepcopy(identity))
    monkeypatch.setattr(socket, "create_connection", lambda *_a, **_k: pytest.fail("Offline regression attempted a connection"))
    case = fixture()
    origin = accepted_annotation(tmp_path / "annotation", case["material"], case["raw"])
    saved = save_propagation_run(tmp_path / "propagation", annotation_run=origin, solved=case["solved"])
    assert saved.coverage == case["facts"].coverage
    result = run_doe(tmp_path / "propagation", run_dir=tmp_path / "doe")
    assert (tmp_path / "doe" / "doe-result.json").is_file()
    assert result["result"]
