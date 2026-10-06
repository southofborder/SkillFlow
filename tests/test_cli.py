import json

from skillflow.cli import main


def test_cli_offline_candidate_writes_complete_result(tmp_path) -> None:
    skill_root = tmp_path / "skill"
    skill_root.mkdir()
    (skill_root / "SKILL.md").write_bytes(b"# Demo\nReturn input.\n")
    candidate_path = tmp_path / "candidate.json"
    candidate_path.write_text(
        json.dumps(
            {
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
                                "inputs": [
                                    {"type": "context_key", "identifier": "user_input"}
                                ],
                                "outputs": [
                                    {"type": "result", "identifier": "input_value"}
                                ],
                            },
                            {"instruction_ref": "jump", "opcode": "dispatch"},
                        ],
                    },
                    {
                        "block_ref": "answer",
                        "block_name": "返回用户输入",
                        "instructions": [
                            {
                                "instruction_ref": "return_input",
                                "opcode": "return",
                                "inputs": [
                                    {"type": "result", "identifier": "input_value"}
                                ],
                            }
                        ],
                    },
                ],
                "edges": [{"source_block_ref": "start", "target_block_ref": "answer"}],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    output_path = tmp_path / "result.json"

    exit_code = main(
        [
            "analyze",
            "--input",
            str(skill_root),
            "--candidate",
            str(candidate_path),
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == 0
    result = json.loads(output_path.read_text(encoding="utf-8"))
    assert result["status"] == "complete"
    assert result["cfg"]["blocks"]["block_002"]["block_name"] == "返回用户输入"
    source = result["cfg"]["blocks"]["block_001"]
    assert source["data_source_kind"] == "context"
    acquisition = source["instructions"][0]
    # The canonical identifier is written out, and the extractor's own wording is kept
    # beside it so the value can still be read back as a sentence.
    assert acquisition["outputs"][0] == {
        "type": "result",
        "identifier": "result_001",
        "semantic_name": "input_value",
    }
    assert (
        result["cfg"]["blocks"]["block_002"]["instructions"][0]["inputs"][0][
            "identifier"
        ]
        == "result_001"
    )
    for retired in (
        "context_exports",
        "context_passthrough",
        "context_requires",
        "context_provides",
    ):
        assert retired not in source
    assert "literal_value" not in acquisition["inputs"][0]
    assert result["prompt"]
