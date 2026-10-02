from skill_ir.analysis.availability import analyze_availability
import json
import re
import pytest
from skill_ir.inputs.skill_package import load_skill_package
from skill_ir.extraction.compiler import compile_candidate
from skill_ir.extraction.prompt import _EXAMPLES, _INSTRUCTIONS, build_whole_skill_prompt


@pytest.mark.parametrize("getter", [False, True])
def test_source_boundary_examples_preserve_entry_target_and_narrow_interface(getter) -> None:
    title, candidate = _EXAMPLES[5 if getter else 4]
    result = compile_candidate(candidate)
    assert result.ok, result.diagnostics
    assert len(result.cfg.blocks) == 1
    block = next(iter(result.cfg.blocks.values()))
    acquisition, returning = block.instructions
    assert returning.opcode == "return"
    assert returning.inputs[0].identifier == acquisition.outputs[0].identifier
    assert acquisition.outputs[0].semantic_name == "acquired_city"
    assert all(i.opcode not in {"model_observe", "select_part"} for i in block.instructions)
    if getter:
        assert acquisition.opcode == "request.get"
        assert acquisition.inputs[0].identifier == "request.get"
        assert acquisition.inputs[1].literal_value == "city"
        assert "local key-only interface" in acquisition.constraints[0]
        assert candidate["declared_context_keys"] == []
    else:
        assert acquisition.opcode == "read_city_from_request"
        assert acquisition.inputs[0].identifier == "request"
        assert candidate["declared_context_keys"] == ["request"]
        assert "no read mechanism or model visibility is specified" in title


def test_source_scope_prompt_preserves_target_without_inferring_execution_model() -> None:
    normalized = " ".join(_INSTRUCTIONS.split())
    for phrase in (
        "Preserve both where content is acquired and which value is obtained",
        "Do not replace the only reference to that source container with the desired field name",
        "context_key does not itself assert that the entire container was read or observed by a model",
        "preserve its actual interface and restriction instead of replacing it with a whole-container read",
        "retain those distinct actions and their intermediate result",
        "do not add source-level read/select/observe steps",
        "External acquisition does not imply network communication",
        "an explicitly pure function whose output is computed from existing inputs is an ordinary computation",
    ):
        assert phrase in normalized


def test_prompt_contains_complete_files_and_no_evidence_contract(tmp_path) -> None:
    root = tmp_path / "sample"
    root.mkdir()
    content = "第一行\n第二行\n"
    (root / "SKILL.md").write_bytes(content.encode("utf-8"))

    prompt = build_whole_skill_prompt(load_skill_package(root))

    assert '<skill-file path="SKILL.md" kind="markdown"' in prompt
    assert content in prompt
    assert "block_name" in prompt
    assert "black-box" in prompt
    assert "EvidenceRef" not in prompt
    assert "source_refs" not in prompt


@pytest.mark.parametrize("title, candidate", _EXAMPLES)
def test_prompt_examples_are_complete_compilable_candidates(
    tmp_path, title, candidate
) -> None:
    root = tmp_path / "example"
    root.mkdir()
    (root / "SKILL.md").write_text("# Example\n", encoding="utf-8")
    prompt = build_whole_skill_prompt(load_skill_package(root))
    assert title in prompt
    assert json.dumps(candidate, ensure_ascii=False, indent=2) in prompt

    result = compile_candidate(candidate)
    assert result.ok, result.diagnostics
    assert result.cfg.validate_integrity()
    for block in candidate["blocks"]:
        for retired in (
            "context_exports",
            "context_passthrough",
            "context_requires",
            "context_provides",
        ):
            assert retired not in block


@pytest.mark.parametrize("candidate", [item[1] for item in _EXAMPLES[:2]])
def test_relay_examples_keep_untouched_results_available(candidate) -> None:
    # Only these two examples include a block that does not touch an available
    # value; the order examples deliberately use their input in the next block.
    result = compile_candidate(candidate)
    assert result.ok, result.diagnostics
    analysis = analyze_availability(result.cfg)
    assert any(analysis.untouched_results.values())


def test_branch_example_references_values_only_one_path_produces() -> None:
    """The merge in the second example reads both branches' values on purpose."""

    _, candidate = _EXAMPLES[1]

    result = compile_candidate(candidate)

    assert result.ok, result.diagnostics
    analysis = analyze_availability(result.cfg)
    assert {use.semantic_name for use in analysis.path_dependent_reads} == {
        "slack_receipt",
        "skip_note",
    }
    assert analysis.unavailable_reads == ()


def test_prompt_requires_actual_sources_and_value_references(tmp_path) -> None:
    root = tmp_path / "sample"
    root.mkdir()
    (root / "SKILL.md").write_text("# Skill\n", encoding="utf-8")

    prompt = build_whole_skill_prompt(load_skill_package(root))

    normalized = " ".join(prompt.split())
    for required in [
        "Name the acquisition for what is actually read",
        "exactly one acquisition instruction",
        "result input naming it exactly",
        "unique across the WHOLE candidate",
        "neither reads nor produces a value does not mention it",
        "produce a NEW identifier",
        "whether a path connects each result producer to its reader",
        "a block inside a loop may reference a value that a later block on the backedge produces",
        "dispatch.inputs",
        "The declaration alone never makes a result available",
        "Only dispatch and return have fixed control-flow roles",
        "metadata.script_content",
        "do not copy example behaviors",
        "When calling a function or tool explicitly named in the source, preserve that name",
        "return may appear at the end of that block",
        "An independent branch may consist of return alone",
        "Return a source-specified literal or an existing result directly",
        "Preserve constraint wording from the source in constraints: list[str]",
        "Place Skill-wide constraints on IRAnalysisCandidate",
        "block-scoped constraints on CandidateBlock",
        "operation-scoped constraints on CandidateInstruction",
        "If scope is unclear, report that uncertainty in diagnostics rather than promoting it to a Skill-wide rule",
        "Actual data acquisition, processing, and transfer must still appear in operands and control flow",
        "A constraint alone does not introduce a conversion, validation, or other execution step",
    ]:
        assert required in normalized

    # The shared context namespace is gone from the contract, so it must not
    # survive in the wording either: a stale sentence would ask the model for a
    # field the compiler now rejects.
    for retired in [
        "context_exports",
        "context_passthrough",
        "context_requires",
        "context_provides",
        "local_dep",
    ]:
        assert retired not in prompt


def test_straight_line_example_ends_in_the_last_behavior_block() -> None:
    compiled = compile_candidate(_EXAMPLES[0][1])
    assert compiled.ok, compiled.diagnostics
    final_block = compiled.cfg.blocks["block_003"]
    assert [instruction.opcode for instruction in final_block.instructions] == [
        "log_progress",
        "return",
    ]
    assert final_block.instructions[-1].inputs[0].semantic_name == "normalized_message"
    assert not any(
        edge.source_block_id == final_block.block_id for edge in compiled.cfg.edges
    )
    assert len(compiled.cfg.blocks) == 3


@pytest.mark.parametrize("example_index, expected_order, send_value", [
    (2, ["locally_remove_field", "send_configuration", "return"], "filtered_config"),
    (3, ["send_configuration", "locally_remove_field", "return"], "original_config"),
])
def test_order_examples_compile_with_the_actual_sent_data_version(
    example_index, expected_order, send_value,
) -> None:
    compiled = compile_candidate(_EXAMPLES[example_index][1])
    assert compiled.ok, compiled.diagnostics
    source, processing = compiled.cfg.blocks.values()
    assert [instruction.opcode for instruction in processing.instructions] == expected_order
    original = source.instructions[0].outputs[0]
    removal = next(i for i in processing.instructions if i.opcode == "locally_remove_field")
    sending = next(i for i in processing.instructions if i.opcode == "send_configuration")
    filtered = removal.outputs[0]
    assert original.identifier != filtered.identifier
    assert removal.inputs[0].identifier == original.identifier
    assert removal.inputs[1].literal_value == "api_key"
    assert sending.inputs[1].semantic_name == send_value
    assert sending.inputs[1].identifier == (
        filtered.identifier if send_value == "filtered_config" else original.identifier)
    assert processing.instructions[-1].inputs[0].identifier == filtered.identifier
    assert len(compiled.cfg.edges) == 1


def test_english_granularity_instructions_preserve_source_and_code(tmp_path) -> None:
    root = tmp_path / "sample"
    root.mkdir()
    source = "# 中文原文\n先删除字段再发送。\n```python\nprint('不可翻译')\n```\n"
    (root / "SKILL.md").write_bytes(source.encode("utf-8"))
    prompt = build_whole_skill_prompt(load_skill_package(root))
    assert not re.search(r"[\u3400-\u9fff]", prompt.split("Complete Skill package:", 1)[0])
    assert source in prompt
    normalized = " ".join(_INSTRUCTIONS.split())
    for requirement in (
        "Each instruction represents one definite action",
        "order or an intermediate data version",
        "send must consume that result",
        "sending before removing the field must consume the original result",
        "do not split it mechanically by effect count",
        "Do not invent source-level operations for implicit model observation",
        "Treat code files and code blocks as black-box operations",
        "Write explanatory diagnostics in Chinese",
    ):
        assert requirement in normalized
