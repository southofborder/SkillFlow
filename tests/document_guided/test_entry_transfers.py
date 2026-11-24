"""Check actual invocation versions, conservative local recovery and optional argument presence."""
from copy import deepcopy
from hashlib import sha256

import pytest

from skillflow.common.source_evidence import _digest
from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.fragments import assemble_fragments, salvage_fragment, validate_fragment
from skillflow.propagation.annotation.binding_examples import instruction, result
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.data import DataRegistry, LiteralContent
from skillflow.propagation.models import FlowLocation, FlowState
from skillflow.propagation.selectors import selector_outcomes
from skillflow.propagation.solver import propagate
from tests.propagation.annotation.helpers import prepared_material


def fixture(*, extra=False):
    content = "export function example(first: string, second?: string) { return second; }\n"
    file = {"path": "entry.ts", "content": content, "sha256": sha256(content.encode()).hexdigest()}
    source = {"files": [file], "source_sha256": _digest([{k: file[k] for k in ("path", "sha256")}])}
    span = {"file": "skill/entry.ts", "start_line": 1, "end_line": 1}
    evidence = [{**span, "reason": "The public function receives these separate arguments."}]
    args = ["first", "second"]
    ir = instruction("ir_entry", "receive", [{"type": "context_key", "identifier": k} for k in args])
    ir["outputs"] = [{**result("out_" + k), "semantic_name": k} for k in [*args, *(["extra"] if extra else [])]]
    ir["metadata"] = {"source_actions": [{"ref": "args", "kind": "receive", "source": span}],
                      "optional_context_inputs": [1]}
    exit_ir = instruction("ir_end", "return", [result("out_second")])
    graph = {"entry_block_id": "entry", "declared_context_keys": args, "constraints": [], "edges": [],
             "blocks": {"entry": {"block_id": "entry", "block_name": "example", "data_source_kind": "context",
                        "constraints": [], "instructions": [ir, exit_ir]}}}
    gap = {"instruction_id": "ir_entry", "unmodeled": True, "outputs": list(range(len(ir["outputs"]))),
           "reason": "The candidate cannot associate every declared output with an invocation argument.",
           "evidences": evidence}
    p = {"ir_semantics": {"ir_end": {"evidences": evidence}}, "processing_gaps": [gap]}
    return prepared_material(source, graph), p


def test_proved_ports_and_local_unknown_output_share_the_same_entry():
    m, raw = fixture(extra=True)
    original = deepcopy(raw)
    p = validate_fragment("processing", raw, m)
    assert raw == original
    rec = p["ir_semantics"]["ir_entry"]
    assert [b["value"] for b in rec["output_bindings"][:2]] == [{"kind": "input", "index": i} for i in [0, 1]]
    assert [op["op"] for op in rec["segments"][0]["ops"]] == ["placeholder"]
    assert p["processing_gaps"][0]["outputs"] == [2]
    assert p["processing_gaps"][0]["unmodeled"] is False
    assert validate_fragment("processing", p, m) == p


def test_conflicting_binding_needs_correction_then_preserves_other_operations():
    m, raw = fixture()
    gap = raw["processing_gaps"][0]
    p = validate_fragment("processing", raw, m)
    record = p["ir_semantics"]["ir_entry"]
    record["output_bindings"][0]["value"]["index"] = 1
    op = {"op": "placeholder", "kind": "effect", "inputs": [], "reason": "The caller's instrumentation is opaque.",
          "evidences": gap["evidences"]}
    record["segments"] = [{"mode": "local", "ops": [op], "returns": []}]
    p["processing_gaps"] = [gap]
    with pytest.raises(StructuralValidationError) as exc:
        validate_fragment("processing", p, m)
    assert any(row["code"] == "entry_output_binding" for row in exc.value.diagnostics)
    saved, gaps = salvage_fragment("processing", p, m)
    assert not gaps
    saved_record = saved["ir_semantics"]["ir_entry"]
    assert saved_record["segments"][0]["ops"] == [op]
    assert saved_record["output_bindings"][0]["value"] == {"kind": "input", "index": 0}
    assert not saved["processing_gaps"]


def test_gap_from_another_lifecycle_never_controls_the_entry():
    from skillflow.propagation.contracts.limitations import gap_id, processing_impacts
    m, raw = fixture()
    m["source"]["files"][0]["content"] += "initialize_cache();\n"
    raw["processing_gaps"][0].update(control=True, evidences=[{"file": "skill/entry.ts",
        "start_line": 2, "end_line": 2, "reason": "Module startup may initialize a shared cache."}])
    with pytest.raises(StructuralValidationError) as exc:
        validate_fragment("processing", raw, m)
    assert any(r["code"] == "entry_gap_scope" for r in exc.value.diagnostics)
    saved, gaps = salvage_fragment("processing", raw, m)
    assert "ir_entry" in saved["ir_semantics"]
    assert not saved["processing_gaps"] and len(gaps) == 1 and not gaps[0]["unmodeled"]
    assert "skill/entry.ts:2-2" in gaps[0]["validation_errors"][0]["message"]
    annotation = {"ir_semantics": {}, "locations": {}, "processing_gaps": gaps}
    assert processing_impacts(m["cfg"], annotation)[gap_id(gaps[0])] == ["ir_entry"]


def test_salvage_removes_only_the_rejected_packet_and_unused_projections():
    m, raw = fixture()
    p = validate_fragment("processing", raw, m)
    rec = p["ir_semantics"]["ir_entry"]
    rec["segments"] = [{"mode": "local", "returns": [], "ops": [
        {"op": "read", "location": "fictitious", "output": "all_args"},
        {"op": "select_part", "input": {"kind": "local", "name": "all_args"}, "path": ["x"], "output": "x"},
        {"op": "placeholder", "kind": "effect", "inputs": [], "reason": "The caller runs an uninspected logger.",
         "evidences": rec["evidences"]}]}]
    rec["output_bindings"][0]["value"] = {"kind": "local", "name": "x"}
    p["locations"] = {"fictitious": {"kind": "runtime_context", "name": "all.arguments", "evidences": rec["evidences"]}}
    p["processing_gaps"] = raw["processing_gaps"]
    saved, gaps = salvage_fragment("processing", p, m)
    assert not gaps
    kept = saved["ir_semantics"]["ir_entry"]
    assert kept["segments"][0]["ops"] == rec["segments"][0]["ops"][2:]
    assert kept["output_bindings"][0]["value"] == {"kind": "input", "index": 0}


def test_finite_and_shared_corrections_cannot_discard_supported_sibling_effects():
    from skillflow.document_guided.fragments import fragment_correction_strategy
    from skillflow.document_guided.fragment_revision import merge_processing_revision, processing_scope
    m, raw = fixture()
    p = validate_fragment("processing", raw, m)
    ir = "ir_entry"
    spec = p["ir_semantics"][ir]
    effect = {"op": "placeholder", "kind": "effect", "inputs": [], "reason": "The caller runs an unspecified observer.",
              "evidences": spec["evidences"]}
    spec["segments"] = [{"mode": "local", "returns": [], "ops": [effect]}]
    original = deepcopy(p)
    p["processing_gaps"] = raw["processing_gaps"]
    spec["output_bindings"][0]["value"]["index"] = 1
    with pytest.raises(StructuralValidationError) as exc:
        validate_fragment("processing", p, m)
    strategy = fragment_correction_strategy("processing")
    strategy.build_prompt("Inputs", p, exc.value.diagnostics)
    proposed = strategy.merge(p, {"coverage_slots": [{"instruction_id": ir, "keep": "unmodeled"}]})
    saved, gaps = salvage_fragment("processing", proposed, m)
    assert not gaps and saved["ir_semantics"][ir]["segments"] == original["ir_semantics"][ir]["segments"]
    scope = processing_scope(m["cfg"], m["cfg"], [{"target_ids": ["annotation:/ir_semantics/" + ir]}], original)
    patch = {"coverage_slots": [{"instruction_id": ir, "unmodeled_gaps": raw["processing_gaps"]}]}
    merged = merge_processing_revision(original, scope, patch)
    assert validate_fragment("processing", merged, m)["ir_semantics"][ir] == original["ir_semantics"][ir]


def test_rejects_wrong_source_evidence_and_cross_argument_location():
    m, raw = fixture()
    raw["processing_gaps"][0]["evidences"][0]["end_line"] = 88
    with pytest.raises(StructuralValidationError):
        validate_fragment("processing", raw, m)
    m, raw = fixture()
    p = validate_fragment("processing", raw, m)
    p["locations"] = {"bundle": {"kind": "runtime_context", "name": "bundle",
        "operand_refs": [{"instruction_id": "ir_entry", "side": "input", "index": i} for i in [0, 1]],
        "evidences": raw["processing_gaps"][0]["evidences"]}}
    with pytest.raises(StructuralValidationError) as exc:
        validate_fragment("processing", p, m)
    assert any(r["code"] == "entry_location_alias" for r in exc.value.diagnostics)


@pytest.mark.parametrize("include_placeholder", [True, False])
def test_single_read_in_prose_preserves_packet_and_localizes_only_callback(include_placeholder):
    # No supported programming-language signature. These are the actual
    # submitted read and selected field, with independent physical citations.
    text = "Read packet.json once.\nReturn the packet's title.\nA plugin estimates the rank from the packet.\n"
    file = {"path": "SKILL.md", "content": text, "sha256": sha256(text.encode()).hexdigest()}
    source = {"files": [file], "source_sha256": _digest([{k: file[k] for k in ("path", "sha256")}])}
    def span(line):
        return {"file": "skill/SKILL.md", "start_line": line, "end_line": line}
    actions = [{"ref": ref, "kind": role, "source": span(i + 1)}
               for i, (ref, role) in enumerate([("packet", "read"), ("title", "value"), ("rank", "other")])]
    ir = instruction("ir_read_packet", "read", [{"type": "external_resource", "identifier": "packet.json"}])
    ir.update(outputs=[result("title"), result("rank")], metadata={"source_actions": actions})
    cfg = {"entry_block_id": "entry", "constraints": [], "edges": [], "declared_context_keys": [], "blocks": {
        "entry": {"block_id": "entry", "block_name": "packet", "constraints": [], "data_source_kind": "external",
                  "instructions": [ir, instruction("ir_end", "return", [result("title")])]}}}
    material = prepared_material(source, cfg)
    evidence = lambda i: [{**span(i), "reason": "This line specifies this packet operation."}]
    local = lambda key: {"kind": "local", "name": key}
    ops = [{"op": "read", "location": "file", "output": "raw", "evidences": evidence(1)},
           {"op": "select_part", "input": local("raw"), "path": ["title"], "output": "title", "evidences": evidence(2)}]
    binds = [{"output_index": 0, "value": local("title")}]
    paths = {"packet": [["segments", 0, "ops", 0]], "title": [["segments", 0, "ops", 1], ["output_bindings", 0]]}
    gap = {"instruction_id": "ir_read_packet", "unmodeled": True, "outputs": [1], "evidences": evidence(3),
           "reason": "The plugin determines the rank from the packet; its ranking rule is unavailable."}
    if include_placeholder:
        paths["rank"] = [["segments", 0, "ops", 2], ["output_bindings", 1]]
        ops.append({"op": "placeholder", "kind": "value", "inputs": [local("raw")], "output": "rank",
                    "reason": gap["reason"], "evidences": evidence(3)})
        binds.append({"output_index": 1, "value": local("rank")})
    raw = {"ir_semantics": {"ir_read_packet": {"segments": [{"mode": "local", "ops": ops, "returns": []}],
        "evidences": evidence(1), "action_bindings": paths, "output_bindings": binds}, "ir_end": {"evidences": evidence(2)}},
        "locations": {"file": {"kind": "storage", "name": "packet.json", "evidences": evidence(1)}}, "processing_gaps": [gap]}
    p = validate_fragment("processing", raw, material)
    rec = p["ir_semantics"]["ir_read_packet"]
    assert rec["segments"][0]["ops"][:2] == ops[:2]
    assert len(rec["output_bindings"]) == 2 and rec["output_bindings"][0] == binds[0]
    assert p["processing_gaps"] == [{**gap, "unmodeled": False}]
    assert validate_fragment("processing", p, material) == p


@pytest.mark.parametrize("value, expected", [("OMITTED", {0}), (None, {1}), ("", {2}), ("UNKNOWN", {1, 2, 3}),
                                              ("UNSPECIFIED_INVOCATION", {0, 1, 2, 3})])
def test_optional_snapshot_distinguishes_omitted_null_empty_and_unknown(value, expected):
    m, raw = fixture()
    p = validate_fragment("processing", raw, m)
    correspondence = {"realizations": [{"requirement_id": "R001"}], "demands": [{"requirement_id": "R001",
        "target": {"instruction_id": "ir_end", "side": "input", "index": 0}, "preserve": "value",
        "reason": "Return the optional argument's actual version."}]}
    _, _, compiled, _ = assemble_fragments(p, correspondence, {"declarations": []}, m)
    registry = DataRegistry("invocation")
    first = registry.register_source("first", acquired_from="runtime_context:first")
    source = FlowLocation(kind="runtime_context", name="second")
    state = {FlowLocation(kind="runtime_context", name="first"): frozenset([first.id])}
    if value != "OMITTED":
        data = registry.register_source("second", acquired_from="runtime_context:second",
            content=None if value == "UNKNOWN" else LiteralContent(value=value))
        state[source] = frozenset([data.id])
    facts = (propagate(m["cfg"], to_payload(compiled)) if value == "UNSPECIFIED_INVOCATION" else
             propagate(m["cfg"], to_payload(compiled), initial_state=FlowState.from_mapping(state), initial_registry=registry))
    assert facts.coverage == {"ir_entry": "processed", "ir_end": "processed"}
    observed = facts.records.get("ir_entry")
    entry = {b.location: b.data_ids for b in observed.entry_state.bindings}
    if value == "OMITTED":
        assert source not in entry
        assert not any(item["data"]["origin"].get("acquired_from") == "runtime_context:second"
                       for item in facts.registry.to_dict()["records"])
    if value == "UNSPECIFIED_INVOCATION":
        assert len(entry[source]) == 1  # The omission alternative is not an input read.
    outputs = next(b.data_ids for b in observed.exit_state.bindings if b.location.name == "out_second")
    selector = {"path": [], "tests": [{"kind": "missing"}, {"kind": "null"}, {"kind": "equals", "value": ""}]}
    assert set.union(*(selector_outcomes(facts.registry, data_id, selector) for data_id in outputs)) == expected
