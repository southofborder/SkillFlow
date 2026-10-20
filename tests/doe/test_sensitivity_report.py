"""Sensitivity presentation preserves declaration limits and shared references."""
from copy import deepcopy

from skillflow.doe.sensitivity_report import build_view, render_html, render_markdown
from skillflow.doe.sensitivity_material import SensitivityReview as _StoredReview


def fixture():
    declaration = {"value": {"kind": "local", "name": "original"}, "path": ["secret"],
        "property": "value", "label": "credential <script>", "evidences": [
            {"file": "skill/SKILL.md", "start_line": 2, "end_line": 2, "reason": "The file declares a credential."}]}
    index = {"declarations": {"S1": {"instruction_id": "ir_1", "scope_path": [],
        "declaration_index": 0, "declaration": declaration}}}
    item = {"id": "review-A", "operation_id": "op-A", "input_index": 1,
        "derivation_id": "SD1", "conclusion": "possible_excess", "reason": "A possible relation does not prove plaintext.",
        "demand_refs": ["DD1"], "constraint_refs": [], "reduction": None}
    signal = {"data_id": "D-A", "label": "credential <script>", "property": "value", "path": ["secret"],
        "excluded_paths": [], "relation": "possible", "declaration_id": "S1", "parents": [], "rules": ["explicit_declaration"]}
    result = {"schema_version": "skillflow-sensitivity-review-v4", "status": "complete", "sinks": [
        {"id": "sink-A", "boundary": {"target": "<img>"}, "actual_payload": [["D-A"], ["D-A"]],
         "related_requirements": ["R1"], "data_reviews": [item], "limitations": []},
        {"id": "sink-B", "boundary": {}, "actual_payload": [], "related_requirements": [],
         "data_reviews": [], "limitations": []}],
        "derivations": {"sensitivity": {"SD1": signal}, "demand": {"DD1": {}}},
        "constraints": {"checks": {}, "preservation": {}, "influence": {}},
        "diagnostics": [], "coverage": {"sensitivity_basis": "declared_ranges_only"}}
    metadata = {"candidate_origin": "assistant_authored_offline", "source_files": {
        "skill/SKILL.md": "Header\r\nKeep credential private.\r\n"}, "task": {"requirements": [{"id": "R1", "text": "Return the original value."}]}}
    return _StoredReview(result, index), metadata


def test_shared_report_views_preserve_order_evidence_and_limits():
    review, metadata = fixture()
    before = deepcopy(review.to_dict())
    view = build_view(review, metadata=metadata)
    assert [sink["id"] for sink in view["sinks"]] == ["sink-A", "sink-B"]
    assert view["sinks"][0]["value"]["actual_payload"] == [["D-A"], ["D-A"]]
    assert view["declarations"][0]["evidences"][0]["quote"] == "Keep credential private.\r\n"
    html, md = render_html(review, metadata=metadata), render_markdown(review, metadata=metadata)
    for output in (html, md):
        assert output.index(view["sinks"][0]["anchor"]) < output.index(view["sinks"][1]["anchor"])
        assert "Sensitivity coverage is limited to explicit declarations" in output
        assert "not a non-sensitive or no-DOE certificate" in output
        assert "Possible excess" in output
        assert "<script>" not in output and "<img>" not in output
        assert "&lt;script&gt;" in output
    assert review.to_dict() == before


def test_empty_candidate_does_not_claim_nonsensitivity():
    review, metadata = fixture()
    result = review.to_dict()
    for sink in result["sinks"]:
        sink["data_reviews"] = []
    result["derivations"]["sensitivity"] = {}
    empty = _StoredReview(result, {"declarations": {}})
    for output in (render_html(empty, metadata=metadata), render_markdown(empty, metadata=metadata)):
        assert "No explicit sensitivity declarations" in output
        assert "not assigned invented sensitive fields or labels" in output
        assert "Undeclared content is not proven non-sensitive" in output


def test_all_shared_derivation_links_have_targets():
    review, metadata = fixture()
    html = render_html(review, metadata=metadata)
    view = build_view(review, metadata=metadata)
    row = view["sinks"][0]["rows"][0]
    for anchor in [row["declaration_anchor"], row["derivation_anchor"], row["demands"][0]["anchor"]]:
        assert f'href="#{anchor}"' in html
        assert f'id="{anchor}"' in html
