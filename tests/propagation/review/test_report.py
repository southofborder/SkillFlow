"""Presentation preserves findings and distinguishes failed review from no issue."""

from html import unescape
import re

from skillflow.propagation.review.report import display_model
from skillflow.propagation.review.report import render_html
from skillflow.propagation.review.report import render_markdown
from skillflow.propagation.review.report import write_reports


def materials(status="complete"):
    result = {
        "status": status, "summary": "issues_found" if status == "complete" else None,
        "reason": "只验证记录和定位；不证明推断成立。",
        "review": {"reviewed_ir_ids": ["ir_a", "ir_b"], "findings": [
            {"id": "F02", "target_ids": ["ann_0009"],
             "explanation": "先观察原数据，再删除字段。", "suggestion": "保留旧版本。",
             "evidences": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1, "reason": "Source support."}]},
            {"id": "F01", "target_ids": ["obs_0001"],
             "explanation": "接收边界的值绑定错误。", "suggestion": "保持实际边界身份。",
             "evidences": [{"rule_id": "EM01", "reason": "Contract support."}]},
        ]} if status == "complete" else None,
        "resolved_findings": [{"id": "F02", "targets": [
            {"id": "ann_0009", "pointer": "/ir_semantics/ir_a/events/0",
             "instruction_ids": ["ir_a"], "value": {"mode": "default"}}]}],
        "counts": {"logical_calls": 1, "http_attempts": 0, "http_attempts_observed": False},
        "response_chain": {"accepted_call": "calls/review/a001"},
        "accepted_call": "calls/review/a001",
    }
    from tests.propagation.annotation.helpers import material as base_material
    material = {**base_material(), "target_index": [], "observations": [{
        "id": "obs_0001", "instruction_id": "ir_a", "mode": "default",
        "values": [{"kind": "input", "index": 0}],
        "target": {"kind": "model_context", "name": "模型上下文"},
        "raw_target_id": "ann_0009", "processing_target_id": "ann_0008",
        "scope_target_ids": [],
    }]}
    return result, material


def test_markdown_and_html_preserve_findings_order_and_semantic_boundaries():
    model = display_model(*materials())
    markdown, html = render_markdown(model), render_html(model)
    for text in (markdown, html):
        assert text.index("F02") < text.index("F01")
        assert "保留旧版本" in text and "接收边界的值绑定错误" in text
        assert "no reported issue does not prove correct interpretation" in text
        assert "Material issues found" in text
    assert '"http_attempts_observed": false' in unescape(html)
    assert '"raw_target_id": "ann_0009"' in unescape(html)
    assert '"kind": "input"' in unescape(html)


def test_html_escapes_model_text_quotes_ids_and_resolved_original_values():
    result, material = materials()
    unsafe = '<script>alert("x")</script>'
    finding = result["review"]["findings"][0]
    finding.update(id="x' onclick='bad", explanation=unsafe, suggestion=unsafe)
    finding["evidences"][0]["reason"] = unsafe
    result["resolved_findings"][0]["targets"][0]["value"]["untrusted"] = unsafe
    html = render_html(display_model(result, material))
    assert unsafe not in html and "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "id='x&#x27; onclick=&#x27;bad'" in html
    assert "id='x' onclick='bad'" not in html


def test_failed_review_is_not_reported_as_no_findings_success():
    model = display_model(*materials("invalid_response"))
    markdown, html = render_markdown(model), render_html(model)
    assert "No valid finding list was produced" in markdown
    assert "Review failed" in html
    assert "Review incomplete" in markdown and "Review incomplete" in html
    assert "No material issue reported; " not in html


def test_complete_empty_findings_have_limited_claim():
    result, material = materials()
    result.update(summary="no_material_issue", resolved_findings=[])
    result["review"]["findings"] = []
    markdown = render_markdown(display_model(result, material))
    html = render_html(display_model(result, material))
    assert "No material issue reported" in markdown
    assert "this does not prove semantic correctness" in html


def test_report_local_audit_links_resolve_at_run_and_replay_locations(tmp_path):
    # Replay retains result.json locally but shares the frozen material and call
    # with its parent run. A link to replay/inputs is a broken audit reference.
    result, material = materials()
    (tmp_path / "inputs").mkdir()
    (tmp_path / "inputs/targets.json").write_text("[]", encoding="utf-8")
    (tmp_path / "inputs/observations.json").write_text("[]", encoding="utf-8")
    call = tmp_path / "calls/review/a001"
    call.mkdir(parents=True)
    (call / "call.json").write_text("{}", encoding="utf-8")
    (call / "response.json").write_text("{}", encoding="utf-8")
    (call / "validation.json").write_text("{}", encoding="utf-8")
    (call.parent / "chain.json").write_text("{}", encoding="utf-8")
    for directory in (tmp_path, tmp_path / "replay"):
        directory.mkdir(exist_ok=True)
        (directory / "result.json").write_text("{}", encoding="utf-8")
        write_reports(directory, result, material)
        html = (directory / "report.html").read_text(encoding="utf-8")
        links = re.findall(r"href=['\"]([^'\"]+)['\"]", html)
        assert len(links) >= 3
        for link in links:
            assert (directory / link).is_file(), f"Broken {directory.name} report link: {link}"
        markdown = (directory / "report.md").read_text(encoding="utf-8")
        for link in re.findall(r"\]\(([^)]+)\)", markdown):
            assert (directory / link).is_file(), f"Broken {directory.name} Markdown link: {link}"


def test_program_generated_semantic_correspondence_keeps_source_seed_and_gap():
    from skillflow.propagation.review.material import prepare_review_material
    from skillflow.propagation.review.services import validate_response
    from tests.propagation.review.test_core import fixture, empty_response
    prepared = prepare_review_material(*fixture())
    review = validate_response(empty_response(prepared), prepared).model_dump(mode="json")
    result = {"status": "complete", "summary": "no_material_issue", "reason": "工程记录", "review": review}
    model = display_model(result, prepared)
    assert model["crosswalk"][0]["requirement_id"] == prepared["task"]["requirements"][0]["id"]
    assert model["crosswalk"][0]["realization"]["status"] == "unmapped"
    assert model["crosswalk"][0]["declarations"] == []
    for rendered in (render_markdown(model), render_html(model)):
        assert "Per-requirement semantic correspondence" in rendered
        assert "unmapped" in rendered and "No executable declaration" in rendered
        assert "Expression status and review acceptance do not prove requirement satisfaction" in rendered
        assert "skill/SKILL" in rendered
