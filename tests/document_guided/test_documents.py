from copy import deepcopy

import pytest

from skillflow.document_guided import build_document_prompt, source_packet
from skillflow.document_guided.prompts import build_batch_prompt
from skillflow.document_guided.source import copy_script_content
from skillflow.document_guided.source import select_document_source, prompt_cfg
from skillflow.document_guided.prompts import build_graph_prompt, build_annotation_prompt


def test_exact_source_ranges_merge_overlap_preserve_unicode_and_line_endings():
    files = {"skill/SKILL.md": "Start\r\n\r\n原文\r\nEnd", "code.py": "value = 1\n"}
    spans = [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 2},
             {"file": "skill/SKILL.md", "start_line": 2, "end_line": 3}]
    packet = source_packet(files, spans)
    assert packet["ranges"] == [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 3,
                                  "text": "Start\r\n\r\n原文\r\n"}]
    assert packet["unreferenced_ranges"] == [
        {"file": "skill/SKILL.md", "start_line": 4, "end_line": 4},
        {"file": "code.py", "start_line": 1, "end_line": 1}]
    assert len(source_packet(files)["ranges"]) == 2
    assert source_packet(files, [*spans, {"file": "code.py", "start_line": 1, "end_line": 1}])["ranges"][-1]["text"] == files["code.py"]


@pytest.mark.parametrize("span", [
    {"file": "missing", "start_line": 1, "end_line": 1},
    {"file": "s", "start_line": True, "end_line": 1},
    {"file": "s", "start_line": 0, "end_line": 1},
    {"file": "s", "start_line": 1, "end_line": 2},
])
def test_missing_or_invalid_source_never_guessed(span):
    with pytest.raises(ValueError):
        source_packet({"s": "one"}, [span])


def test_plain_work_documents_use_short_template_and_task_isolation():
    files = {"s": "Do not disclose the private field.\nReturn the public result.\n"}
    prompt = build_document_prompt("flow", files=files)
    headings = ["STEP RESPONSIBILITY", "PREVIOUS WORK", "GLOBAL REQUIREMENTS AND LIMITATIONS",
                "RELATED SOURCE", "OUTPUT REQUIREMENTS"]
    assert [prompt.index(name) for name in headings] == sorted(prompt.index(name) for name in headings)
    assert "JSON Schema" not in prompt and "SourceAccounting" not in prompt
    for step, kwargs in [
        ("processing", {"runtime_contract": {"rules": []}}),
        ("task-correspondence", {"task": {"requirements": ["Do not disclose"]}, "documents": {"processing": "Read the whole value."}}),
        ("sensitivity", {"documents": {"processing": "Read the whole value."}}),
    ]:
        text = build_document_prompt(step, files=files, cfg={"fixture": "full CFG"},
                                     global_requirements="Do not disclose the private field; return the public result. No unresolved source conflict in this fixture.", **kwargs)
        assert all(text.count(name) == 1 for name in headings)
    with pytest.raises(ValueError, match="does not accept"):
        build_document_prompt("task-correspondence", files=files, cfg={}, task={},
                              global_requirements="Return the public result.",
                              documents={"processing": "p", "sensitivity": "secret judgment"})
    with pytest.raises(ValueError, match="complete readable source"):
        build_document_prompt("flow", files=files, spans=[])
    with pytest.raises(ValueError, match="explicit global obligations"):
        build_document_prompt("sensitivity", files=files, cfg={}, documents={"processing": "p"})


def test_batch_format_is_current_projection_not_full_annotation():
    prompt = build_batch_prompt("locations", files={"s": "Save result."}, spans=None,
                               documents={"processing": "Save the result locally."},
                               accepted_objects={}, global_requirements="Preserve the result.")
    assert '"locations"' in prompt and '"location_evidences"' in prompt
    assert '"realizations"' not in prompt
    assert '"ir_semantics"' not in prompt
    assert prompt.count("Format notation:") == 1


def test_script_copy_uses_exact_selected_range_not_extension_or_similarity():
    candidate = {"blocks": [{"instructions": [{"instruction_ref": "run", "metadata": {}}]}]}
    before = deepcopy(candidate)
    files = {"extensionless": "#!/bin/sh\r\nprintf '原文'\r\n"}
    span = {"file": "extensionless", "start_line": 1, "end_line": 2}
    copied = copy_script_content(candidate, "run", span, files=files)
    assert copied["blocks"][0]["instructions"][0]["metadata"]["script_content"] == files["extensionless"]
    assert candidate == before
    with pytest.raises(ValueError, match="exact existing"):
        copy_script_content(candidate, "similar_run", span, files=files)
    with pytest.raises(ValueError, match="differs"):
        copy_script_content(copied, "run", {**span, "end_line": 1}, files=files)


def test_document_refs_select_exact_ranges_and_keep_global_source():
    files = {"skill/SKILL.md": "Global prohibition.\r\nGlobal ambiguity.\r\n",
             "skill/a.py": "first\nsecond\nthird\n",
             "skill/b.py": "not selected\n"}
    packet = select_document_source(files, {"flow": "Actual call: `skill/a.py:2-2`."})
    assert [(row["file"], row["start_line"], row["end_line"]) for row in packet["ranges"]] == [
        ("skill/SKILL.md", 1, 2), ("skill/a.py", 2, 2)]
    assert packet["ranges"][0]["text"] == files["skill/SKILL.md"]
    assert len(packet["files"]) == 3
    assert packet["unreferenced_ranges"]


def test_document_navigation_fallback_is_visible_and_unknown_files_never_guessed():
    files = {"skill/SKILL.md": "Global.\n", "skill/a.py": "one\ntwo\n"}
    for text in ("See `skill/a.py`.", "See `skill/a.py:200-201`." ):
        packet = select_document_source(files, {"flow": text})
        assert packet["ranges"][-1]["text"] == files["skill/a.py"]
        assert "absent or unusable" in packet["selection_notes"][0]
    packet = select_document_source(files, {"flow": "The task/task correspondence has no source ranges yet."})
    assert not packet["unreferenced_ranges"]
    assert "complete readable source" in packet["selection_notes"][0]
    with pytest.raises(ValueError, match="unknown frozen file"):
        select_document_source(files, {"flow": "See skill/similar_a.py:1-2."})


def test_relationship_step_updates_same_flow_without_final_formats():
    files = {"skill/SKILL.md": "Keep two calls separate.\n"}
    text = build_document_prompt("relationships", files=files,
        documents={"flow": "There are two calls. skill/SKILL.md:1-1"},
        global_requirements="Preserve global restrictions and unresolved questions.")
    assert "complete revised flow document" in text
    assert "Format notation:" not in text
    assert "do not" in text.lower()
    with pytest.raises(ValueError, match="source and the flow document only"):
        build_document_prompt("relationships", files=files, cfg={},
            documents={"flow": "f"}, global_requirements="Preserve restrictions.")


def test_prompt_cfg_only_omits_identical_code_actually_sent_and_never_changes_input():
    files = {"skill/a.py": "x = 1\n", "skill/b.py": "y = 2\n"}
    cfg = {"blocks": [{"instructions": [
        {"metadata": {"script_content": files["skill/a.py"], "other": "retained"}},
        {"metadata": {"script_content": files["skill/b.py"]}},
        {"metadata": {"script_content": "x=1\n"}},
    ]}]}
    before = deepcopy(cfg)
    packet = source_packet(files, [{"file": "skill/a.py", "start_line": 1, "end_line": 1}])
    displayed = prompt_cfg(cfg, packet=packet)["blocks"][0]["instructions"]
    assert displayed[0]["metadata"] == {"other": "retained"}
    assert displayed[1]["metadata"]["script_content"] == "y = 2\n"
    assert displayed[2]["metadata"]["script_content"] == "x=1\n"
    assert prompt_cfg(cfg) == cfg == before


def test_final_fill_prompts_have_one_full_format_and_inherited_whole_work():
    from tests.document_guided.test_batches import annotation_batches
    from skillflow.graph.extraction.candidate import IRAnalysisCandidate
    from skillflow.graph.extraction.compiler import compile_candidate
    from skillflow.graph.extraction.prompt import _EXAMPLES
    from skillflow.propagation.annotation.services import compile_response
    from skillflow.document_guided.batches import combine_annotation
    from skillflow.document_guided.cfg_wire import CFGWire, normalize_cfg_wire
    from skillflow.document_guided.annotation_wire import compile_flat_response
    from tests.document_guided.test_parallel_runner import _flat
    files = {"skill/SKILL.md": "Read the value and return it."}
    graph_prompt = build_graph_prompt(files=files, documents={"flow": "One complete flow. skill/SKILL.md:1-1"},
        global_requirements="Keep source-supported branches and open issues.")
    assert graph_prompt.count("Format notation:") == 1
    assert "CFGWire" in graph_prompt and "cannot_assess" in graph_prompt
    assert "One complete flow. skill/SKILL.md:1-1" in graph_prompt
    assert "Read the value and return it." in graph_prompt
    assert "_source_span={file,start_line,end_line}" in graph_prompt
    candidate = IRAnalysisCandidate.model_validate(_EXAMPLES[0][1])
    assert compile_candidate(candidate).ok
    wire_candidate = {"entry_block_ref": "main", "blocks": [{"block_ref": "main", "instructions": [
        {"opcode": "return", "inputs": [{"type": "literal", "literal_value": "original"}]}]}]}
    assert CFGWire.model_validate(wire_candidate)
    assert compile_candidate(normalize_cfg_wire(wire_candidate)).ok
    locations, irs, globals_, material = annotation_batches()
    documents = {"processing": "Actual processing only.",
        "task-correspondence": "Preserve the supported endpoint content.",
        "sensitivity": "Do not invent sensitive information."}
    before = deepcopy(material)
    annotation_prompt = build_annotation_prompt(material, documents=documents,
        global_requirements="Retain every Task requirement and unresolved restriction.")
    assert annotation_prompt.count("Format notation:") == 1
    assert "FlatAnnotationResponse" in annotation_prompt and "FailureResponse" in annotation_prompt
    assert "FlatCall" in annotation_prompt and "FlatForEach" in annotation_prompt
    assert "SEALED_TASK" in annotation_prompt and "RUNTIME_CONTRACT" in annotation_prompt
    assert annotation_prompt.count("DOCUMENT processing") == 1
    assert annotation_prompt.count("DOCUMENT task-correspondence") == 1
    assert annotation_prompt.count("DOCUMENT sensitivity") == 1
    assert material == before
    raw, compiled, _ = combine_annotation(locations, irs, globals_, material=material)
    assert compile_response(raw, material)[1] == compiled
    wire, backend_raw, flat_compiled, _ = compile_flat_response(_flat(raw), material)
    assert "task_revision_id" not in wire
    assert backend_raw["task_revision_id"] == material["task"]["task_sha256"]
    assert set(flat_compiled["ir_semantics"]) == set(compiled["ir_semantics"])
    with pytest.raises(ValueError, match="exactly these working documents"):
        build_annotation_prompt(material, documents={**documents, "flow": "unrelated copy"},
            global_requirements="Keep restrictions.")
