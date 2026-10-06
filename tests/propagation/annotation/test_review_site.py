"""Offline review payload, SVG identity mapping and script-free source display."""

from skillflow.common.paths import project_root, resolve_material_path

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET

import pytest
from skillflow.common.recording import canonical_sha256


SCRIPT = project_root() / "tools/propagation/annotation/build_review_site.py"
spec = importlib.util.spec_from_file_location("skillflow_review_site", SCRIPT)
site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)


def case(identifier="001"):
    return {
        "case_id": identifier, "sample_id": "N01", "basename": identifier + "-样例", "skill_name": "样例",
        "feedback_status": "audit_passed", "feedback_reason": "模型判定保留，不是证明", "selected_revision": 0,
        "annotation_status": "complete", "annotation_reason": "记录完整", "graph_sha256": "frozen-graph",
        "cfg": {"entry_block_id": "b<&>\"", "blocks": {"b<&>\"": {"block_id": "b<&>\"", "block_name": "中文块",
            "instructions": [{"id": "ir<&>\"", "opcode": "return", "inputs": [], "outputs": [],
                              "metadata": {"script": "</script><script>alert('never')</script>"}}]}}, "edges": []},
        "source": {"files": [{"path": "SKILL.md", "content": "中文全文\n</script><img src=x onerror=alert(1)>\n"}],
                   "units": [{"id": "src_1", "file": "SKILL.md", "start_line": 1, "end_line": 3}]},
        "profiles": {"ir<&>\"": {"operator": ["tool"], "roles": ["source", "sink"],
            "effects": ["fs_read", "model_observe"], "evidences": [{"field": "effects", "value": "fs_read", "effect_index": 0,
            "basis": "source", "ref_id": "src_1", "quote": "中文全文", "reason": "原文依据"}]}},
        "locations": {}, "transfer_specs": {}, "sink_boundaries": [],
        "audit": {"findings": [{"id": "combined", "kind": "semantic", "status": "represented", "conservative": None}]},
        "png_file": "ir-IPP/001-样例.png", "svg_file": "render/001-样例.svg",
        "suggestions_file": "suggestions/001-样例.md",
    }


def svg():
    root = ET.Element("svg", {"xmlns": site.SVG_NS, "width": "400", "height": "240", "viewBox": "0 0 400 240"})
    block = ET.SubElement(root, "g", {"data-block-id": 'b<&>"'})
    ET.SubElement(block, "rect", {"x": "10", "y": "10", "width": "380", "height": "200"})
    operation = ET.SubElement(block, "g", {"data-ir-id": 'ir<&>"', "data-block-id": 'b<&>"'})
    ET.SubElement(operation, "text", {"x": "30", "y": "80"}).text = "中文 return <&>"
    return ET.tostring(root, encoding="unicode")


def export(tmp_path, cases=None):
    material = {"schema_version": 5, "identity": "skill-ir-full-pipeline-delivery-v5", "profile_schema_version": "security-profile-v10", "run_id": "offline-fixture", "cases": cases if cases is not None else [case()]}
    path = tmp_path / "review-data.json"
    path.write_text(json.dumps(material, ensure_ascii=False), encoding="utf-8")
    (tmp_path / "render").mkdir(exist_ok=True)
    (tmp_path / "render/001-样例.svg").write_text(svg(), encoding="utf-8")
    return path


def embedded_data(html):
    raw = re.search(r'<script id="review-data" type="application/json">(.*?)</script>', html, re.S).group(1)
    return json.loads(raw)


def test_page_embeds_complete_source_profiles_and_states_without_fetch(tmp_path):
    source = case()
    data = export(tmp_path, [source])
    output = site.build_review_site(data, tmp_path / "review/index.html")
    html = output.read_text(encoding="utf-8")
    result = embedded_data(html)["cases"][0]
    assert result["source"] == source["source"]
    assert result["cfg"] == source["cfg"] and result["profiles"] == source["profiles"]
    assert "unresolved" not in result
    assert result["feedback_status"] == "audit_passed" and result["annotation_status"] == "complete"
    assert "fetch(" not in html and "XMLHttpRequest" not in html and "innerHTML" not in html
    assert "</script><img" not in html and "</script><script>alert" not in html
    assert "connect-src 'none'" in html
    assert "助手复核（独立于模型判断）" in html
    assert "未填写 conservative 的保留项不自动等于精确保留" in html
    assert "model_observe" in html and "模型观察" in html


@pytest.mark.parametrize("field,value", [("schema_version", 1), ("profile_schema_version", "security-profile-v1"),
                                        ("profile_schema_version", "security-profile-v2"),
                                        ("profile_schema_version", "security-profile-v4"),
                                        ("identity", "skill-ir-full-pipeline-delivery-v1")])
def test_review_refuses_old_profile_exports(tmp_path, field, value):
    data = export(tmp_path)
    payload = json.loads(data.read_text(encoding="utf-8"))
    payload[field] = value
    data.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported review export version"):
        site.build_review_site(data, tmp_path / "review/index.html")


def audit_case(tmp_path):
    item = case()
    item["locations"] = {"model": {"kind": "model_context", "name": "agent", "operand_refs": [], "access_scope": "recipient", "retention": None}}
    table = {"model": [{"basis": "source", "ref_id": "src_1", "quote": "中文全文", "reason": "定位边界依据"}]}
    audit = tmp_path / "audit/001/location-evidences.json"
    audit.parent.mkdir(parents=True)
    audit.write_text(json.dumps(table, ensure_ascii=False), encoding="utf-8")
    item["annotation_audit"] = {"file": "audit/001/location-evidences.json", "sha256": canonical_sha256(table)}
    return item, table, audit


def test_review_embeds_separate_audit_without_changing_business_locations(tmp_path):
    item, table, _ = audit_case(tmp_path)
    data = export(tmp_path, [item])
    html = site.build_review_site(data, tmp_path / "review/index.html").read_text(encoding="utf-8")
    rendered = embedded_data(html)["cases"][0]
    assert rendered["locations"] == item["locations"]
    assert set(rendered["locations"]["model"]) == {"kind", "name", "operand_refs", "access_scope", "retention"}
    assert rendered["annotation_audit"]["evidences"] == table
    assert "evidences" not in json.loads(data.read_text(encoding="utf-8"))["cases"][0]["annotation_audit"]
    assert "位置证据审计（独立保存）" in html


def test_review_rejects_tampered_location_audit(tmp_path):
    item, table, path = audit_case(tmp_path)
    table["model"][0]["quote"] = "changed"
    path.write_text(json.dumps(table), encoding="utf-8")
    with pytest.raises(ValueError, match="audit digest mismatch"):
        site.build_review_site(export(tmp_path, [item]), tmp_path / "review/index.html")


@pytest.mark.parametrize("field,value", [("key", "agent"), ("anchors", []), ("evidences", [])])
def test_review_rejects_old_embedded_location_contract(tmp_path, field, value):
    item, _, _ = audit_case(tmp_path)
    item["locations"]["model"][field] = value
    with pytest.raises(ValueError):
        site.build_review_site(export(tmp_path, [item]), tmp_path / "review/index.html")


def test_review_rejects_old_evidence_location_even_with_current_header(tmp_path):
    item = case()
    evidence = next(iter(item["profiles"].values()))["evidences"][0]
    evidence["location"] = evidence.pop("ref_id")
    with pytest.raises(ValueError):
        site.build_review_site(export(tmp_path, [item]), tmp_path / "review/index.html")


@pytest.mark.parametrize("location", ["profile", "evidence", "unresolved"])
def test_review_v5_header_does_not_accept_old_actor_records(tmp_path, location):
    item = case()
    profile = next(iter(item["profiles"].values()))
    if location == "profile":
        profile["actor"] = profile.pop("operator")
    elif location == "evidence":
        profile["evidences"][0].update(field="actor", value="tool", effect_index=None)
    else:
        item["unresolved"] = [{"instruction_id": 'ir<&>"', "field": "actor", "reason": "legacy"}]
    with pytest.raises(ValueError):
        site.build_review_site(export(tmp_path, [item]), tmp_path / "review/index.html")


def test_review_template_explains_empty_effects_and_operator(tmp_path):
    item = case()
    profile = next(iter(item["profiles"].values()))
    profile["effects"] = []
    profile["evidences"][0].update(value=None, effect_index=None, reason="没有适用效果；不表示没有数据绑定")
    html = site.build_review_site(export(tmp_path, [item]), tmp_path / "review/index.html").read_text(encoding="utf-8")
    assert "执行主体（operator）" in html
    assert "不等于空操作，也不表示入口与出口状态相同" in html
    assert next(iter(embedded_data(html)["cases"][0]["profiles"].values()))["effects"] == []


def test_execution_origin_is_visible_and_not_a_new_semantic_status(tmp_path):
    executable = shutil.which("node")
    if executable is None:
        pytest.skip("Node unavailable for isolated offline function verification")
    reused, rerun = case(), case("008")
    reused["execution_origin"] = {"kind": "reused", "parent_run_id": "parent-run", "source_run_id": "parent-run",
                                  "provenance_sha256": "a" * 64}
    rerun["execution_origin"] = {**reused["execution_origin"], "kind": "rerun", "source_run_id": "offline-fixture"}
    page = site.build_review_site(export(tmp_path, [reused, rerun]), tmp_path / "review/index.html").read_text(encoding="utf-8")
    data = embedded_data(page)["cases"]
    assert [item["execution_origin"] for item in data] == [reused["execution_origin"], rerun["execution_origin"]]
    assert all(item["feedback_status"] == "audit_passed" and item["annotation_status"] == "complete" for item in data)
    function = page.split("function originBadge(", 1)[1].split("\nfunction jsonBlock(", 1)[0]
    code = 'const node=(tag,cls,text)=>({tag,cls,text});\nfunction originBadge(' + function
    code += '\nconst cases=' + json.dumps(data, ensure_ascii=False) + ''';
if(originBadge(cases[0]).text!=="复用父记录"||originBadge(cases[1]).text!=="本次重新执行")throw Error("origin badges");
if(!originSummary(cases[0]).includes("本次未重新调用模型")||!originSummary(cases[0]).includes("父运行 parent-run"))throw Error("reuse provenance");
if(!originSummary(cases[1]).includes("实际执行运行 offline-fixture"))throw Error("fresh provenance");
if(originBadge({})!==null||originSummary({})!=="")throw Error("ordinary run changed");
'''
    script = tmp_path / "origin-functions.js"
    script.write_text(code, encoding="utf-8")
    result = subprocess.run([executable, str(script)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert 'badge(c.annotation_status),originBadge(c)' in page
    assert 'badge(c.annotation_status,"标注："),originBadge(c)' in page
    assert 'node("div","metadata",originSummary(c))' in page


@pytest.mark.parametrize("change", ["wrong_source", "unknown_kind", "unsealed"])
def test_review_rejects_unbound_execution_origin(tmp_path, change):
    item = case()
    origin = {"kind": "reused", "parent_run_id": "parent-run", "source_run_id": "parent-run", "provenance_sha256": "a" * 64}
    if change == "wrong_source":
        origin["source_run_id"] = "another-run"
    elif change == "unknown_kind":
        origin["kind"] = "assumed-success"
    else:
        origin.pop("provenance_sha256")
    item["execution_origin"] = origin
    with pytest.raises(ValueError, match="execution origin"):
        site.build_review_site(export(tmp_path, [item]), tmp_path / "review/index.html")


def test_actual_graph_identifiers_survive_xml_escaping(tmp_path):
    output = site.build_review_site(export(tmp_path), tmp_path / "review/index.html")
    cleaned = embedded_data(output.read_text(encoding="utf-8"))["cases"][0]["svg"]
    root = ET.fromstring(cleaned)
    assert [node.get("data-ir-id") for node in root.iter() if node.get("data-ir-id")] == ['ir<&>"']
    assert [node.get("data-block-id") for node in root.iter() if node.get("data-block-id")] == ['b<&>"', 'b<&>"']
    assert "中文 return <&>" in "".join(root.itertext())


def test_svg_removes_executable_external_and_foreign_content():
    unsafe = '''<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)">
      <script>alert(1)</script><foreignObject><div>unsafe HTML</div></foreignObject>
      <style>body{background:url(https://outside)}</style>
      <a href="javascript:alert(1)"><text>link</text></a>
      <text onclick="alert(1)" style="background:url(https://outside)" fill="url(https://outside)">safe text</text>
      <path marker-end="url(#arrow)" d="M 0 0 L 1 1"/>
    </svg>'''
    cleaned = site.sanitize_svg(unsafe)
    assert "safe text" in cleaned and "url(#arrow)" in cleaned
    for forbidden in ["script", "foreignObject", "style=", "onload", "onclick", "https://outside", "javascript:"]:
        assert forbidden not in cleaned


@pytest.mark.parametrize("changed", ["unknown_ir", "missing_ir", "wrong_block"])
def test_svg_must_bind_all_clickable_operations_to_actual_cfg(changed):
    value = svg()
    if changed == "unknown_ir":
        value = value.replace("data-ir-id=", "data-other-id=", 1).replace("<text", '<text data-ir-id="invented"', 1)
    elif changed == "missing_ir":
        value = value.replace("data-ir-id=", "data-other-id=", 1)
    else:
        value = value.replace("data-block-id=", "data-other-block=", 1).replace("<text", '<text data-block-id="unknown"', 1)
    with pytest.raises(ValueError, match="unknown|lacks clickable"):
        site.sanitize_svg(value, case()["cfg"])


def test_no_cfg_case_remains_failure_without_fallback(tmp_path):
    failed = {**case(), "cfg": None, "audit": None, "svg_file": None, "profiles": {},
              "feedback_status": "extraction_error", "annotation_status": "not_run"}
    path = site.build_review_site(export(tmp_path, [failed]), tmp_path / "review/index.html")
    result = embedded_data(path.read_text(encoding="utf-8"))["cases"][0]
    assert result["cfg"] is result["audit"] is result["svg"] is None
    assert result["profiles"] == {} and result["annotation_status"] == "not_run"


def test_thirty_case_order_and_independent_state_selection(tmp_path):
    cases = []
    for number in reversed(range(1, 31)):
        item = case(f"{number:03}")
        item["feedback_status"] = ["audit_passed", "semantic_failure", "audit_error"][number % 3]
        item["annotation_status"] = ["complete", "semantic_failure", "not_run"][number % 3]
        cases.append(item)
    path = site.build_review_site(export(tmp_path, cases), tmp_path / "review/index.html")
    result = embedded_data(path.read_text(encoding="utf-8"))["cases"]
    assert [c["case_id"] for c in result] == [f"{i:03}" for i in range(1, 31)]
    assert {c["feedback_status"] for c in result} == {"audit_passed", "semantic_failure", "audit_error"}
    assert {c["annotation_status"] for c in result} == {"complete", "semantic_failure", "not_run"}


@pytest.mark.parametrize("field,value", [("svg_file", "../outside.svg"), ("png_file", "https://example.invalid/x"),
                                          ("suggestions_file", "javascript:alert(1)")])
def test_external_or_escaping_artifact_paths_are_rejected(tmp_path, field, value):
    changed = {**case(), field: value}
    with pytest.raises(ValueError, match="escapes|relative"):
        site.build_review_site(export(tmp_path, [changed]), tmp_path / "review/index.html")


def test_duplicate_case_id_is_not_silently_overwritten(tmp_path):
    with pytest.raises(ValueError, match="unique"):
        site.build_review_site(export(tmp_path, [case(), deepcopy(case())]), tmp_path / "review/index.html")


def test_inline_script_has_valid_javascript_syntax(tmp_path):
    executable = shutil.which("node")
    if executable is None:
        pytest.skip("Node unavailable for offline syntax verification")
    text = site.TEMPLATE.read_text(encoding="utf-8")
    code = re.search(r"<script>\s*(.*?)</script>", text, re.S).group(1)
    path = tmp_path / "review.js"
    path.write_text(code, encoding="utf-8")
    checked = subprocess.run([executable, "--check", str(path)], capture_output=True, text=True)
    assert checked.returncode == 0, checked.stderr


def test_long_execution_diagnostic_is_folded_without_changing_data(tmp_path):
    executable = shutil.which("node")
    if executable is None:
        pytest.skip("Node unavailable for isolated offline function verification")
    item = case()
    item["feedback_status"] = "audit_error"
    item["feedback_reason"] = "159 validation errors for AuditResult\n" + "<script>inert()</script>错误诊断\n" * 4000
    item["feedback_reason_summary"] = "核对响应无效：159 项字段类型错误。"
    output = site.build_review_site(export(tmp_path, [item]), tmp_path / "review/index.html")
    page = output.read_text(encoding="utf-8")
    value = embedded_data(page)["cases"][0]
    assert value["feedback_reason"] == item["feedback_reason"]
    assert value["feedback_reason_summary"] == item["feedback_reason_summary"]
    function = page.split("function runReason(", 1)[1].split("\nfunction button(", 1)[0]
    code = '''
const node=(tag,cls,text)=>({tag,text:text||"",children:[],append(...items){this.children.push(...items)}});
const notice=text=>node("div","",text);const statusClass=()=>"error";
''' + "function runReason(" + function + "\nconst c=" + json.dumps(value, ensure_ascii=False) + ''';
const rendered=runReason(c,"feedback","语义核对");
if(rendered.children[0].text.length>500||!rendered.children[0].text.includes(c.feedback_reason_summary))throw Error("summary");
const details=rendered.children[1];
if(details.tag!=="details"||details.open||details.children[1].tag!=="pre"||details.children[1].text!==c.feedback_reason)throw Error("full diagnostic");
delete c.feedback_reason_summary;
const fallback=runReason(c,"feedback","语义核对");
if(fallback.children[0].text.length>500||fallback.children[1].children[1].text!==c.feedback_reason)throw Error("fallback");
const short=runReason({annotation_reason:"标注记录完整",annotation_status:"complete"},"annotation","安全标注");
if(short.children.length!==1||short.children[0].text!=="安全标注：标注记录完整")throw Error("short reason");
'''
    script = tmp_path / "diagnostic-function.js"
    script.write_text(code, encoding="utf-8")
    result = subprocess.run([executable, str(script)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_execution_only_review_is_not_a_historical_or_current_graph_review(tmp_path):
    executable = shutil.which("node")
    if executable is None:
        pytest.skip("Node unavailable for isolated offline function verification")
    template = site.TEMPLATE.read_text(encoding="utf-8")
    function = template.split("function appendAssistantReview(", 1)[1].split("\nfunction appendEvidenceLocation(", 1)[0]
    code = '''
const node=(tag,cls,text)=>({text:text||"",children:[],append(...items){this.children.push(...items)}});
const notice=text=>node("div","",text);
const collect=n=>[n.text,...n.children.map(collect)].join("\\n");
''' + "function appendAssistantReview(" + function + '''
const review={reviewer:"assistant",status:"execution_only",human_confirmed:false,reviews:[{revision:null,graph_sha256:null,
scope:"execution_only",matches_selected_graph:false,assessment:"执行失败复核",observations:["无图不能判断业务语义"]}]};
const absent=node();appendAssistantReview(absent,{cfg:null,assistant_review:review});
const text=collect(absent);
if(!text.includes("仅执行记录复核，无可用图")||!text.includes("不能构成图语义复核通过"))throw Error(text);
if(!text.includes("执行失败复核")||!text.includes("无图不能判断业务语义")||text.includes("本例尚未完成助手复核"))throw Error(text);
if(text.includes("第 null 轮")||text.includes("历史轮次")||text.includes("图摘要"))throw Error(text);
const existing=node();appendAssistantReview(existing,{cfg:{},assistant_review:review});
if(!collect(existing).includes("当前选定图尚未完成助手复核"))throw Error(collect(existing));
'''
    script = tmp_path / "review-function.js"
    script.write_text(code, encoding="utf-8")
    result = subprocess.run([executable, str(script)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_local_browser_interaction_keeps_source_inert_and_statuses_separate(tmp_path):
    runtime = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node"
    modules, executable = runtime / "node_modules", runtime / "bin/node.exe"
    browser = Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")
    if not (executable.is_file() and browser.is_file() and (modules / "playwright/package.json").is_file()):
        pytest.skip("Optional local Edge and Playwright are unavailable")
    first, location_table, _ = audit_case(tmp_path)
    first["transfer_specs"] = {'ir<&>"': {"order": "partial", "precedence": [], "events": [{"effect_index": 0, "atomic_ops": [
        {"op": "deliver", "inputs": [{"kind": "literal", "value": "fixture"}],
         "target": "model", "evidences": location_table["model"]}]}], "output_bindings": []}}
    profile = first["profiles"]['ir<&>"']
    profile["effects"] = ["model_observe", "transform", "model_observe", "context_write"]
    profile["evidences"][0].update(value="model_observe", effect_index=0)
    for index, value in enumerate(profile["effects"][1:], 1):
        profile["evidences"].append({**profile["evidences"][0], "value": value,
                                    "effect_index": index, "basis": "cfg", "ref_id": "g_fixture"})
    first["assistant_review"] = {"reviewer": "assistant", "human_confirmed": False, "status": "reviewed",
        "reviews": [{"revision": 0, "graph_sha256": "frozen-graph", "matches_selected_graph": True,
                     "assessment": "独立助手复核合成记录", "observations": []},
                    {"revision": 1, "graph_sha256": "another-graph", "matches_selected_graph": False,
                     "assessment": "其他图的复核不能当成当前结论", "observations": []}]}
    failed = {**case("002"), "cfg": None, "svg_file": None, "profiles": {}, "audit": None,
              "feedback_status": "extraction_error", "annotation_status": "not_run"}
    unknown = {**case("003"), "feedback_status": "semantic_failure", "annotation_status": "semantic_failure"}
    page_path = site.build_review_site(export(tmp_path, [first, failed, unknown]), tmp_path / "review/index.html")
    script = tmp_path / "browser-check.mjs"
    script.write_text(r'''
import {createRequire} from 'node:module';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const require=createRequire(path.join(process.argv[2],'placeholder.cjs'));
const {chromium}=require('playwright');
const browser=await chromium.launch({headless:true,executablePath:process.argv[3],args:['--disable-gpu']});
try {
 const page=await browser.newPage({viewport:{width:1560,height:980}});
 const errors=[],external=[],dialogs=[];
 page.on('pageerror',e=>errors.push(String(e)));
 page.on('dialog',async d=>{dialogs.push(d.message());await d.dismiss()});
 await page.route('**/*',r=>{if(!r.request().url().startsWith('file:')){external.push(r.request().url());return r.abort()}return r.continue()});
 await page.goto(pathToFileURL(process.argv[4]).href);
 await page.waitForSelector('svg [data-ir-id]');
 if(await page.locator('.case').count()!==3)throw Error('case inventory');
 await page.locator('.case').filter({hasText:'002'}).click();
 if(!await page.locator('#graph-empty').isVisible())throw Error('missing graph failure card');
 await page.selectOption('#feedback-filter','semantic_failure');
 if(await page.locator('.case').count()!==1)throw Error('feedback filter');
 await page.selectOption('#feedback-filter','all');
 await page.selectOption('#annotation-filter','complete');
 if(await page.locator('.case').count()!==1)throw Error('annotation filter');
 await page.locator('.case').click();
 await page.locator('svg [data-ir-id]').click();
 if(!await page.locator('#detail-panel').innerText().then(t=>t.includes('ir<&>"')&&t.includes('model_observe · 模型观察')&&t.includes('原文依据')))throw Error('actual ID and evidence');
 if(!await page.locator('#detail-panel').innerText().then(t=>t.includes('1. model_observe')&&t.includes('2. transform')&&t.includes('3. model_observe')&&t.includes('步骤 3（索引 2）')&&t.includes('部分顺序')))throw Error('ordered effects occurrence evidence');
 if(!await page.locator('#detail-panel').innerText().then(t=>t.includes('执行主体（operator）')&&t.includes('4. context_write · 上下文写入')&&t.includes('步骤 4（索引 3）')))throw Error('v3 operator and context write');
 if(!await page.locator('#detail-panel').innerText().then(t=>t.includes('model · model_context · agent')&&t.includes('operand_refs')))throw Error('v5 business location');
 const locationAudit=page.locator('details.location-audit');
 if(await locationAudit.count()!==1||await locationAudit.getAttribute('open')!==null)throw Error('audit initially folded');
 await locationAudit.locator('summary').click();
 if(!await locationAudit.innerText().then(t=>t.includes('位置证据审计（独立保存）')&&t.includes('src_1')&&t.includes('定位边界依据')))throw Error('separate location audit');
 const before=await page.locator('#zoom-value').innerText();await page.click('#zoom-in');
 if(await page.locator('#zoom-value').innerText()===before)throw Error('zoom');
 const box=await page.locator('#viewport').boundingBox();
 const old=await page.locator('#graph-stage').getAttribute('style');
 await page.mouse.move(box.x+12,box.y+12);await page.mouse.down();await page.mouse.move(box.x+95,box.y+55);await page.mouse.up();
 if(await page.locator('#graph-stage').getAttribute('style')===old)throw Error('pan');
 await page.getByRole('button',{name:'定位完整源文',exact:true}).first().click();
 if(await page.locator('.source-line').count()!==3)throw Error('full source');
 if(await page.locator('#detail-panel img').count())throw Error('injected HTML');
 if(!await page.locator('#detail-panel').innerText().then(t=>t.includes('</script><img src=x onerror=alert(1)>')))throw Error('literal source content');
 await page.getByRole('tab',{name:'语义核对'}).click();
 await page.getByLabel('显示全部核对项（含保留与背景）').check();
 if(await page.locator('.finding').count()!==1)throw Error('audit findings');
 if(!await page.locator('#detail-panel').innerText().then(t=>t.includes('独立助手复核合成记录')&&t.includes('未填写 conservative')&&t.includes('历史轮次，不能替代当前图复核')))throw Error('separate assistant judgment');
 if(errors.length||external.length||dialogs.length)throw Error(JSON.stringify({errors,external,dialogs}));
 console.log('offline browser checks passed');
} finally {await browser.close()}
''', encoding="utf-8")
    checked = subprocess.run([str(executable), str(script), str(modules), str(browser), str(page_path)],
                             capture_output=True, text=True, timeout=60)
    assert checked.returncode == 0, checked.stderr
    assert "offline browser checks passed" in checked.stdout
