"""Field demands and declared content survive bounded per-member acquisition."""
from copy import deepcopy

import pytest
from pydantic import ValidationError

from skillflow.propagation.annotation.compiler import compile_response
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.material import prepare_material
from skillflow.propagation.loading import materials_from_result
from skillflow.propagation.solver import propagate
from skillflow.propagation.data import DataRegistry, LiteralContent
from skillflow.propagation.models import FlowLocation, FlowState
from skillflow.propagation.contracts.demand import RawDemandGoal, FieldExpression
from skillflow.propagation.contracts.demand_index import build_demand_target_index
from skillflow.doe.demand_engine import DemandEngine
from skillflow.doe.sensitivity_engine import SensitivityEngine
from skillflow.doe.sensitivity_material import prepare_sensitivity_review
from skillflow.doe.demand_material import prepare_demand_review
from tests.propagation.annotation.helpers import source_bundle
from tests.propagation.test_map_collection import map_fixture, EVIDENCE, local
from tests.doe.helpers import source_task
from tests.doe.components import mutable_components


def fixture(*, preserve="value", path=None, source_text=None, customize=None, collection_content=None):
    cfg, compiled_template = map_fixture()
    source_text = source_text or ("For each URL acquire a response and save and return a record. "
        "Preserve each record's URL. Response token fields are confidential.\n")
    source = source_bundle(source_text)
    citation = {"file": "skill/SKILL.md", "start_line": 1, "end_line": len(source_text.splitlines()),
                "reason": "The fixture explicitly declares a per-record requirement and sensitive field."}
    task = source_task(source, {"purpose": {"text": "Save URL records.", "evidences": [citation]},
        "requirements": [{"id": "R", "text": "Preserve every saved record URL.", "evidences": [citation]}], "issues": []})
    material = prepare_material(source, cfg, task_baseline=task)
    raw = deepcopy(compiled_template)
    raw.pop("sink_boundaries")
    raw.pop("task_ref")
    raw.update(outcome="completed", task_revision_id=task.task_sha256,
        realizations=[{"requirement_id": "R", "status": "expressed", "bindings": [], "gaps": []}],
        demands=[], expressions=[], location_evidences={key: [EVIDENCE] for key in raw["locations"]})
    def processing(events):
        return {"kind": "processing", "mode": "local", "returns": [],
                "events": events, "evidences": [EVIDENCE]}
    for spec in raw["ir_semantics"].values():
        spec.pop("precedence", None)
        for number, event in enumerate(spec["events"]):
            if event.get("kind") == "for_each":
                event["body"] = [processing(event["body"])]
                event["sensitivity"] = [{"value": local("response"), "path": ["token"],
                    "label": "credential", "evidences": [citation]}]
            else:
                spec["events"][number] = processing([event])
    write = raw["ir_semantics"]["ir_process"]["events"][1]["events"][0]["atomic_ops"][0]
    write["demands"] = [{"requirement_id": "R", "target": {"kind": "input", "index": 0},
        "preserve": preserve, "path": path if path is not None else [{"kind": "each"}, "url"],
        "reason": "Preserve the explicitly required saved record property."}]
    if customize is not None:
        customize(raw, citation)
    raw, compiled, mapping = compile_response(raw, material)
    registry = DataRegistry("doe-map-offline")
    urls = registry.register_source("urls", acquired_from="fixture", content=(
        LiteralContent(value=["url-a", "url-b"]) if collection_content is None else collection_content))
    initial = FlowState.from_mapping({FlowLocation(kind="runtime_context", name="collection"): frozenset([urls.id])})
    solved = propagate(cfg, to_payload(compiled), initial_registry=registry, initial_state=initial)
    assert solved.status == "complete", solved.diagnostics
    facts = mutable_components(materials_from_result(solved, material=material, raw_annotation=raw,
        compiled_annotation=compiled, mapping=mapping))
    annotation = facts.annotation
    targets = build_demand_target_index(cfg, raw)
    candidate = {"goals": compiled["demands"], "expressions": compiled["expressions"]}
    engine = DemandEngine(facts, task, annotation, candidate, targets)
    return facts, task, annotation, candidate, engine


def test_endpoint_each_field_demand_reaches_only_corresponding_yield_fields():
    facts, task, annotation, candidate, engine = fixture()
    result = engine.solve()
    body = [row for row in result["derivations"].values() if row["node"]["kind"] == "op_input"
            and engine.ops[row["node"]["operation_id"]]["spec"]["op"] == "build"]
    assert body and {row["node"]["slot"] for row in body} == {0}
    assert all(row["path"] == [] and row["property"] == "value" for row in body)
    assert not any(row["node"]["kind"] == "op_output" and
                   engine.ops[row["node"]["operation_id"]]["spec"]["op"] == "receive"
                   for row in result["derivations"].values())
    assert prepare_demand_review(facts, task, annotation, candidate).to_dict() == result


def test_cardinality_demand_uses_source_count_without_requiring_response_content():
    _, _, _, _, engine = fixture(preserve="cardinality", path=[])
    result = engine.solve()
    assert not any(row["node"]["kind"] == "op_input" and
                   engine.ops[row["node"]["operation_id"]]["scope"] is not None
                   for row in result["derivations"].values())
    assert any(row["node"]["kind"] == "ir_input" and row["node"]["instruction_id"] == "ir_process"
               and row["property"] == "cardinality" for row in result["derivations"].values())


def test_collected_sensitive_response_field_remains_visible_and_disjoint_from_url_demand():
    facts, task, annotation, candidate, _ = fixture()
    reviewed = prepare_sensitivity_review(facts, task, annotation, candidate).to_dict()
    save = next(sink for sink in reviewed["sinks"] if sink["boundary"]["sink_type"] == "storage_write")
    rows = save["data_reviews"]
    assert len(rows) == 2
    assert {row["conclusion"] for row in rows} == {"excess_supported"}
    assert {tuple(row["reduction"]["path"]) for row in rows} == {
        (0, "response", "token"), (1, "response", "token")}


def test_each_preserves_every_member_level_without_changing_expression_paths():
    goal = {"requirement_id": "R", "target": {"instruction_id": "ir", "path": []},
        "preserve": "value", "reason": "Explicit test requirement."}
    for path in (["nested", {"kind": "each"}], ["rows", {"kind": "each"}, "keys"],
                 ["nested", {"kind": "each"}, {"kind": "each"}],
                 [{"kind": "each"}, {"kind": "each"}]):
        assert RawDemandGoal.model_validate({**goal, "path": path}).model_dump(mode="json")["path"] == path
    with pytest.raises(ValidationError):
        FieldExpression.model_validate({"op": "field", "arg": {"op": "literal", "value": []},
                                        "path": [{"kind": "each"}]})


def test_ga4_status_source_normal_path_keeps_each_status_projection_and_saved_array():
    # Source excerpt is data only. This does not execute the Skill or model
    # catch-and-continue behavior beyond already supplied value candidates.
    source = """export async function checkIndexStatus(urls: string[]) {
  const results: Array<{ url: string; indexed: boolean; status: unknown }> = [];
  for (const url of urls) {
    try {
      const result = await inspectUrl(url, { save: false });
      results.push({
        url,
        indexed: result.indexStatus.verdict === 'PASS',
        status: result.indexStatus,
      });
    } catch (error) {
      results.push({ url, indexed: false, status: { error: String(error) } });
    }
  }
  saveResult(results, 'indexing', 'index_status_check');
  return results;
}
"""
    def normal_mapping(raw, citation):
        loop = raw["ir_semantics"]["ir_process"]["events"][0]
        loop["sensitivity"] = []
        operations = loop["body"][0]["events"][-1]["atomic_ops"]
        build = operations[-1]
        operations.insert(0, {"op": "select_part", "input": local("response"), "path": ["indexStatus"],
                              "output": "status", "evidences": [citation]})
        operations.insert(1, {"op": "compute", "inputs": [local("status")], "dependencies": ["derived"],
            "output": "indexed", "evidences": [citation], "expression": {"expression": {
                "op": "eq", "left": {"op": "field", "arg": {"op": "ref", "value": local("status")},
                "path": ["verdict"]}, "right": {"op": "literal", "value": "PASS"}}, "evidences": [citation]}})
        build["parts"] = [{"path": ["url"], "value": local("item")},
                          {"path": ["status"], "value": local("status")},
                          {"path": ["indexed"], "value": local("indexed")}]
    facts, task, annotation, candidate, engine = fixture(source_text=source, customize=normal_mapping)
    result = engine.solve()
    assert result["status"] == "complete"
    saved = next(sink for sink in result["sinks"] if sink["boundary"]["sink_type"] == "storage_write")
    batch = saved["actual_payload"][0]["inputs"][0][0]
    values = {value["id"]: value for value in facts.data}
    assert values[batch]["content"]["form"] == "mapped_collection"
    for member in values[batch]["content"]["members"]:
        record = values[member["values"][0]]
        parts = {tuple(part["path"]): part["data"] for part in record["content"]["parts"]}
        assert set(parts) == {("url",), ("status",), ("indexed",)}
        assert values[parts[("status",)]]["origin"]["path"] == ["indexStatus"]
    assert prepare_demand_review(facts, task, annotation, candidate).to_dict() == result


def test_alternative_member_content_does_not_cross_into_a_sibling_value():
    def alternatives(raw, citation):
        loop = raw["ir_semantics"]["ir_process"]["events"][0]
        operations = loop["body"][0]["events"][-1]["atomic_ops"]
        operations.append({"op": "build", "container": "object", "output": "alternate_record",
            "parts": [{"path": ["url"], "value": local("item")}, {"path": ["response"],
                "value": {"kind": "literal", "value": {"token": "unrelated-public-marker"}}}],
            "evidences": [citation]})
        loop["yield"] = {"kind": "alternatives", "items": [local("record"), local("alternate_record")]}
    _, _, _, _, engine = fixture(customize=alternatives)
    demand = engine.solve()
    tracker = SensitivityEngine(engine, demand, {"declared-response": {"instruction_id": "ir_process",
        "scope_path": ["events", 0], "declaration": {"value": local("response"), "path": ["token"],
            "property": "value", "label": "credential"}}})
    tracker.track()
    unrelated = {identity for identity, data in engine.index.data.items()
                 if data["content"] == {"form": "literal", "value": {"token": "unrelated-public-marker"}}}
    assert unrelated
    assert not any(row["data_id"] in unrelated for row in tracker.rows.values())
    from skillflow.doe.constraint_ranges import ContentRanges
    responses = {data for operation in engine.ops.values() if operation["spec"]["op"] == "receive"
                 for output in operation["record"]["outputs"] for data in output}
    ranges = ContentRanges(engine.index.data).track(responses, ["token"])
    assert not (unrelated & ranges.keys())


@pytest.mark.parametrize("zero_arguments", [False, True])
def test_explicit_repeated_call_pairs_survive_the_doe_fact_index(zero_arguments):
    def repeated_calls(raw, citation):
        events = raw["ir_semantics"]["ir_process"]["events"][0]["body"][0]["events"]
        for child in events[:2]:
            child["atomic_ops"][0]["request_id"] = "program-call-one"
            if zero_arguments:
                child["atomic_ops"][0]["inputs"] = []
                child["effect"] = None
                child["evidences"] = []
                raw["locations"]["service"]["kind"] = "tool"
        second = deepcopy(events[:2])
        for child in second:
            child["atomic_ops"][0]["request_id"] = "program-call-two"
        second[1]["atomic_ops"][0]["output"] = "second_response"
        events[2:2] = second
        events[-1]["atomic_ops"][-1]["parts"][1]["value"] = local("second_response")
    source_text = ("For each URL invoke a zero-argument tool response acquisition twice, then save and return a record containing that URL. "
                   "Response token fields are confidential.\n") if zero_arguments else None
    _, _, _, _, engine = fixture(customize=repeated_calls, source_text=source_text)
    pairs = [link for link in engine.index.links.values() if link["kind"] == "request_response"]
    assert len(pairs) == 4
    for pair in pairs:
        request, response = engine.ops[pair["source"]], engine.ops[pair["target"]]
        assert request["scope"] == response["scope"]
        assert request["spec"]["request_id"] == response["spec"]["request_id"]
        if zero_arguments:
            assert request["record"]["inputs"] == response["record"]["inputs"] == []


def test_ga4_batch_normal_completion_collects_child_notifications_for_default_save_and_return():
    # Frozen api/indexing.ts:57-79,89-105. This fixture covers the normal
    # metadata-present/default-save case, not fallback dates or fail-fast paths.
    source = """export async function requestIndexing(url: string, options: IndexingOptions = {}): Promise<UrlNotificationResult> {
  const { save = true } = options;

  const client = getIndexingClient();

  const response = await client.urlNotifications.publish({
    requestBody: {
      url,
      type: 'URL_UPDATED',
    },
  });

  const result: UrlNotificationResult = {
    url: response.data.urlNotificationMetadata?.url || url,
    type: 'URL_UPDATED',
    notifyTime: response.data.urlNotificationMetadata?.latestUpdate?.notifyTime || new Date().toISOString(),
  };

  if (save) {
    saveResult(result, 'indexing', 'request_indexing');
  }

  return result;
}

export async function requestIndexingBatch(urls: string[], options: IndexingOptions = {}): Promise<UrlNotificationResult[]> {
  const { save = true } = options;

  const results: UrlNotificationResult[] = [];

  // Process URLs sequentially to avoid rate limiting
  for (const url of urls) {
    const result = await requestIndexing(url, { save: false });
    results.push(result);
  }

  if (save) {
    saveResult(results, 'indexing', 'batch_indexing');
  }

  return results;
}
"""

    def notifications(raw, citation):
        loop = raw["ir_semantics"]["ir_process"]["events"][0]
        loop["sensitivity"] = []
        operations = loop["body"][0]["events"][-1]["atomic_ops"]
        build = operations[-1]
        operations[:0] = [
            {"op": "select_part", "input": local("response"),
             "path": ["data", "urlNotificationMetadata", "url"],
             "output": "notification_url", "evidences": [citation]},
            {"op": "select_part", "input": local("response"),
             "path": ["data", "urlNotificationMetadata", "latestUpdate", "notifyTime"],
             "output": "notification_time", "evidences": [citation]},
        ]
        build["parts"] = [
            {"path": ["url"], "value": local("notification_url")},
            {"path": ["type"], "value": {"kind": "literal", "value": "URL_UPDATED"}},
            {"path": ["notifyTime"], "value": local("notification_time")},
        ]
        realization = raw["realizations"][0]
        realization["status"] = "partial"
        realization["gaps"] = [{"reason": (
            "This offline fixture covers the metadata-present normal completion with default saving. "
            "Metadata fallbacks, save:false and first-failure termination conditions are not modeled; "
            "the collected value does not establish exception-path feasibility or final-save reachability."),
            "evidences": [citation]}]

    facts, _, _, _, engine = fixture(source_text=source, customize=notifications)
    result = engine.solve()
    assert result["status"] == "partial"
    assert any(row["code"] == "requirement_expression_gap" for row in result["diagnostics"])
    saved = next(sink for sink in result["sinks"] if sink["boundary"]["sink_type"] == "storage_write")
    batch = saved["actual_payload"][0]["inputs"][0][0]
    values = {value["id"]: value for value in facts.data}
    content = values[batch]["content"]
    assert content["form"] == "mapped_collection" and len(content["members"]) == 2
    instances = facts.records["ir_process"]["events"][0]["instances"]
    for member in content["members"]:
        assert len(member["values"]) == 1
        parts = {tuple(part["path"]): part["data"]
                 for part in values[member["values"][0]]["content"]["parts"]}
        assert set(parts) == {("url",), ("type",), ("notifyTime",)}
        instance = next(number for number, item in enumerate(instances)
                        if item["selector"] == member["selector"] and item["element"] == member["element"])
        acquisition = next(operation for operation in engine.ops.values()
                           if operation["spec"]["op"] == "receive" and operation["scope"] == (0, instance))
        acquired = acquisition["record"]["outputs"][0][0]
        assert values[parts[("url",)]]["origin"]["part_of"] == acquired
        assert values[parts[("notifyTime",)]]["origin"]["part_of"] == acquired
        assert values[parts[("type",)]]["content"]["value"] == "URL_UPDATED"
    public = next(binding for binding in facts.records["ir_process"]["exit_state"]["bindings"]
                  if binding["location"] == {"kind": "result", "name": "batch_result"})
    assert public["data_ids"] == [batch]


def test_ga4_catch_continue_yield_candidates_use_a_source_constructed_error_not_url_influence():
    # Frozen index.ts:324-345, client.ts:114-116 and settings.ts:62-64.
    # Only a known validation-error content candidate is tested. Neither the
    # throw/catch guard nor the mutually exclusive execution paths are solved.
    # Arbitrary SDK/network exceptions remain outside this fixture's coverage.
    source = r"""export async function checkIndexStatus(urls: string[]) {
  console.log(`\n🔎 Checking index status for ${urls.length} URL(s)...`);
  const results: Array<{ url: string; indexed: boolean; status: unknown }> = [];

  for (const url of urls) {
    try {
      console.log(`  → Inspecting: ${url}`);
      const result = await inspectUrl(url, { save: false });
      results.push({
        url,
        indexed: result.indexStatus.verdict === 'PASS',
        status: result.indexStatus,
      });
    } catch (error) {
      console.log(`  ✗ Failed: ${url}`);
      results.push({ url, indexed: false, status: { error: String(error) } });
    }
  }

  saveResult(results, 'indexing', 'index_status_check');
  console.log('✅ Index status check complete\n');
  return results;
}

  const validation = validateSettings();
  if (!validation.valid) {
    throw new Error(`Invalid credentials: ${validation.errors.join(', ')}`);
  }

  if (!settings.clientEmail) {
    errors.push('GA4_CLIENT_EMAIL is required');
  }
"""

    def candidates(raw, citation):
        spec = raw["ir_semantics"]["ir_process"]
        spec["order"] = "partial"
        loop = spec["events"][0]
        loop["sensitivity"] = []
        normal = loop["body"][0]["events"][-1]["atomic_ops"]
        build = normal[-1]
        normal[:0] = [
            {"op": "select_part", "input": local("response"), "path": ["indexStatus"],
             "output": "status", "evidences": [citation]},
            {"op": "compute", "inputs": [local("status")], "dependencies": ["derived"],
             "output": "indexed", "evidences": [citation], "expression": {"expression": {
                 "op": "eq", "left": {"op": "field", "arg": {"op": "ref", "value": local("status")},
                 "path": ["verdict"]}, "right": {"op": "literal", "value": "PASS"}}, "evidences": [citation]}},
        ]
        build["parts"] = [{"path": ["url"], "value": local("item")},
                          {"path": ["indexed"], "value": local("indexed")},
                          {"path": ["status"], "value": local("status")}]
        error_ops = [
            {"op": "compute", "inputs": [
                {"kind": "literal", "value": "Invalid credentials: "},
                {"kind": "literal", "value": "GA4_CLIENT_EMAIL is required"}],
             "dependencies": ["derived", "derived"], "output": "constructed_error", "evidences": [citation]},
            {"op": "compute", "inputs": [local("constructed_error")], "dependencies": ["derived"],
             "output": "error_text", "evidences": [citation]},
            {"op": "build", "container": "object", "output": "error_status", "parts": [
                {"path": ["error"], "value": local("error_text")}], "evidences": [citation]},
            {"op": "build", "container": "object", "output": "error_record", "parts": [
                {"path": ["url"], "value": local("item")},
                {"path": ["indexed"], "value": {"kind": "literal", "value": False}},
                {"path": ["status"], "value": local("error_status")}], "evidences": [citation]},
        ]
        loop["body"].append({"kind": "processing", "mode": "local", "returns": [],
            "events": [{"effect": "transform", "atomic_ops": error_ops, "evidences": [citation]}],
            "evidences": [citation]})
        loop["yield"] = {"kind": "alternatives", "items": [local("record"), local("error_record")]}
        raw["realizations"][0].update(status="partial", gaps=[{"reason": (
            "Only source-constructed credential-validation error content is retained as an alternative yield. "
            "The missing-email condition, throw/catch transfer, cache behavior, path exclusivity and arbitrary "
            "SDK/network exceptions are not modeled. This is not proof that both body paths execute, that "
            "a request occurs on validation failure, or that catch-and-continue semantics are complete."),
            "evidences": [citation]}])

    facts, _, _, _, engine = fixture(source_text=source, customize=candidates)
    result = engine.solve()
    assert result["status"] == "partial"
    assert any(row["code"] == "requirement_expression_gap" for row in result["diagnostics"])
    saved = next(sink for sink in result["sinks"] if sink["boundary"]["sink_type"] == "storage_write")
    batch = saved["actual_payload"][0]["inputs"][0][0]
    values = {value["id"]: value for value in facts.data}
    content = values[batch]["content"]
    assert content["form"] == "mapped_collection" and len(content["members"]) == 2
    assert all(len(member["values"]) == 2 for member in content["members"])
    for member in content["members"]:
        records = [values[identity] for identity in member["values"]]
        keyed = [{tuple(part["path"]): part["data"] for part in record["content"]["parts"]} for record in records]
        assert all(parts[("url",)] == member["element"] for parts in keyed)
        failure = next(parts for parts in keyed if values[parts[("indexed",)]]["content"] == {"form": "literal", "value": False})
        status = values[failure[("status",)]]["content"]
        error_text = values[status["parts"][0]["data"]]
        assert error_text["content"] == {"form": "opaque"}
        assert error_text["origin"]["acquired_from"] is None
        error_object = values[error_text["origin"]["inputs"][0]]
        assert error_object["origin"]["acquired_from"] is None
        inputs = [values[identity] for identity in error_object["origin"]["inputs"]]
        assert {item["content"]["value"] for item in inputs} == {
            "Invalid credentials: ", "GA4_CLIENT_EMAIL is required"}
        assert all(item["content"]["form"] == "literal" for item in inputs)
    public = next(binding for binding in facts.records["ir_process"]["exit_state"]["bindings"]
                  if binding["location"] == {"kind": "result", "name": "batch_result"})
    assert public["data_ids"] == [batch]
