from skill_ir.analysis.availability import analyze_availability
import json

from skill_ir.extraction.pipeline import analyze_skill
from skill_ir.extraction.response_parser import parse_candidate_response
from skill_ir.extraction.candidate import IRAnalysisCandidate


def candidate_payload() -> dict:
    """A source, a block that touches nothing, and a block reading across both."""

    return {
        "entry_block_ref": "start",
        "declared_context_keys": ["user_input"],
        "blocks": [
            {
                "block_ref": "start",
                "block_name": "读入用户输入",
                "data_source_kind": "context",
                "instructions": [
                    {
                        "instruction_ref": "read_input",
                        "opcode": "read_context",
                        "inputs": [{"type": "context_key", "identifier": "user_input"}],
                        "outputs": [{"type": "result", "identifier": "input_value"}],
                    },
                    {"instruction_ref": "start_jump", "opcode": "dispatch"},
                ],
            },
            {
                "block_ref": "relay",
                "block_name": "记录进度",
                "instructions": [
                    {"instruction_ref": "relay_jump", "opcode": "dispatch"}
                ],
            },
            {
                "block_ref": "compute",
                "block_name": "提取城市并返回",
                "instructions": [
                    {
                        "instruction_ref": "extract",
                        "opcode": "extract_city",
                        "inputs": [{"type": "result", "identifier": "input_value"}],
                        "outputs": [{"type": "result", "identifier": "city"}],
                    },
                    {
                        "instruction_ref": "return",
                        "opcode": "return",
                        "inputs": [{"type": "result", "identifier": "city"}],
                    },
                ],
            },
        ],
        "edges": [
            {"source_block_ref": "start", "target_block_ref": "relay"},
            {"source_block_ref": "relay", "target_block_ref": "compute"},
        ],
        "diagnostics": [],
    }


def unreachable_definition_payload() -> dict:
    """Move the acquisition onto a sibling branch of the block that reads it.

    Nothing about the block that reads ``input_value`` changes; what changes is
    whether any path leads there from the instruction that produces it.
    """

    payload = candidate_payload()
    payload["entry_block_ref"] = "relay"
    payload["blocks"][0]["instructions"][1] = {
        "instruction_ref": "start_stop",
        "opcode": "return",
    }
    payload["blocks"][1]["instructions"] = [
        {
            "instruction_ref": "relay_jump",
            "opcode": "dispatch",
            "inputs": [{"type": "literal", "literal_value": True}],
        }
    ]
    payload["edges"] = [
        {
            "source_block_ref": "relay",
            "target_block_ref": "start",
            "condition_text": "读入",
        },
        {
            "source_block_ref": "relay",
            "target_block_ref": "compute",
            "condition_text": "直接处理",
        },
    ]
    return payload


class FakeClient:
    def __init__(self, responses: list[str]) -> None:
        self.responses = responses
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.responses.pop(0)


def make_skill(tmp_path):
    root = tmp_path / "skill"
    root.mkdir()
    (root / "SKILL.md").write_bytes(b"# Skill\nReturn the input.\n")
    return root


def test_parse_candidate_response_accepts_fenced_json() -> None:
    raw = "Here is the result:\n```json\n{" + '"entry_block_ref": "start"' + "}\n```"

    assert parse_candidate_response(raw) == {"entry_block_ref": "start"}


def test_analyze_skill_repairs_invalid_candidate_once(tmp_path) -> None:
    invalid = candidate_payload()
    invalid["blocks"][2]["instructions"][1]["inputs"][0]["identifier"] = "missing"
    valid = candidate_payload()
    client = FakeClient(
        [json.dumps(invalid, ensure_ascii=False), json.dumps(valid, ensure_ascii=False)]
    )

    result = analyze_skill(make_skill(tmp_path), client=client)

    assert result.status == "complete"
    assert result.requires_review is False
    assert result.attempts == 2
    assert result.cfg is not None
    assert result.cfg.blocks["block_003"].block_name == "提取城市并返回"
    assert "RESULT_NOT_DEFINED" in client.prompts[1]
    assert "missing" in client.prompts[1]


def test_analyze_skill_returns_degraded_after_repair_limit(tmp_path) -> None:
    client = FakeClient(["not JSON"] * 4)

    result = analyze_skill(make_skill(tmp_path), client=client)

    assert result.status == "degraded"
    assert result.requires_review is True
    assert result.cfg is None
    assert result.attempts == 4
    assert result.raw_candidate == {}
    assert result.raw_response == "not JSON"
    assert any("CANDIDATE_JSON_INVALID" in item for item in result.diagnostics)


def test_analyze_skill_compiles_fixed_candidate_without_network(tmp_path) -> None:
    candidate = IRAnalysisCandidate.model_validate(candidate_payload())

    result = analyze_skill(make_skill(tmp_path), candidate=candidate)

    assert result.status == "complete"
    assert result.attempts == 0
    assert result.cfg.blocks["block_003"].block_name == "提取城市并返回"
    assert result.cfg.blocks["block_001"].data_source_kind == "context"
    # The middle block declared nothing about the value that crosses it; the
    # propagation pass is where that fact comes from.
    analysis = analyze_availability(result.cfg)
    assert analysis.untouched_results["block_002"] == frozenset({"result_001"})
    assert analysis.entry_availability("block_003", "result_001") == "all_paths"


def test_analyze_skill_repairs_a_read_no_path_can_reach(tmp_path) -> None:
    client = FakeClient(
        [
            json.dumps(unreachable_definition_payload(), ensure_ascii=False),
            json.dumps(candidate_payload(), ensure_ascii=False),
        ]
    )

    result = analyze_skill(make_skill(tmp_path), client=client)

    assert result.status == "complete"
    assert result.requires_review is False
    assert result.attempts == 2
    assert result.cfg is not None
    repair_errors = client.prompts[1].split("Deterministic validation errors:", 1)[1]
    assert "RESULT_PATH_NOT_FOUND" in repair_errors
    assert "does not reach here along any path" in repair_errors
    # The repair prompt's only other content is the candidate the model wrote,
    # so the error has to be phrased in the names appearing there.
    assert "input_value" in repair_errors
    assert "提取城市并返回" in repair_errors
    assert "读入用户输入" in repair_errors


def test_analyze_skill_repairs_missing_source_despite_declared_initial_key(
    tmp_path,
) -> None:
    invalid = candidate_payload()
    invalid["entry_block_ref"] = "compute"
    invalid["blocks"] = invalid["blocks"][2:]
    invalid["edges"] = []
    client = FakeClient([json.dumps(invalid), json.dumps(candidate_payload())])

    result = analyze_skill(make_skill(tmp_path), client=client)

    assert result.status == "complete"
    assert result.attempts == 2
    assert result.cfg is not None
    assert result.cfg.blocks["block_001"].data_source_kind == "context"
    repair_errors = client.prompts[1].split("Deterministic validation errors:", 1)[1]
    assert "RESULT_NOT_DEFINED" in repair_errors
    assert "input_value" in repair_errors


def test_analyze_skill_degrades_after_repeated_unreachable_definition(tmp_path) -> None:
    invalid = unreachable_definition_payload()
    client = FakeClient([json.dumps(invalid, ensure_ascii=False)] * 3)

    result = analyze_skill(make_skill(tmp_path), client=client, max_repair_rounds=2)

    assert result.status == "degraded"
    assert result.requires_review is True
    assert result.cfg is None
    assert result.attempts == 3
    assert result.raw_candidate == invalid
    assert any(
        "RESULT_PATH_NOT_FOUND" in item and "input_value" in item
        for item in result.diagnostics
    )
    assert len(client.prompts) == 3
    assert all(
        "Deterministic validation errors:" in prompt for prompt in client.prompts[1:]
    )
