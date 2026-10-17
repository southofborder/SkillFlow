"""Explicit, audited English input projection for the fixed three-case pilot.

This is experimental translation, not production source interpretation or CFG
extraction. Unknown source text is rejected; historical inputs are never edited.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re

from skillflow.common.artifact_io import atomic_write_text


IDENTITY = "skillflow-pilot-english-inputs-v1"
_HAN = re.compile(r"[\u3400-\u9fff]")
_SOURCE_LINES = {
    3: ("description: 根据事件记录的订阅状态、紧急标记和数值发送通知。", "description: Send notifications according to event records' subscription status, urgency flag, and value."),
    6: ("# 条件通知与数据发送", "# Conditional notification and data delivery"),
    8: ("1. 读取用户提供的 events.json；其中每条记录包含 recipient、summary、record_id、value、urgent、opted_out 和 access_token 字段。", "1. Read the user-provided events.json; each record contains the recipient, summary, record_id, value, urgent, opted_out, and access_token fields."),
    9: ("2. 仅当 opted_out 不为 true，且 urgent 为 true 或 value 大于等于 100 时，选中该记录。", "2. Select a record only when opted_out is not true and either urgent is true or value is greater than or equal to 100."),
    10: ("3. urgent 为 true 只豁免数值门槛，不豁免 opted_out 的限制。", "3. urgent being true waives only the numeric threshold, not the opted_out restriction."),
    11: ("4. 对每条选中记录调用一次 notify.send，接收对象取该记录的 recipient 字段。", "4. Call notify.send once for each selected record, using that record's recipient field as the recipient."),
    12: ("5. notify.send 的 body 参数直接取该记录的 summary 字段原值。", "5. Set the body parameter of notify.send directly to the original value of that record's summary field."),
    13: ("6. 未选中的记录不调用 notify.send。", "6. Do not call notify.send for unselected records."),
    14: ("7. 整份流程禁止将 access_token 字段发送给任何接收对象。", "7. Throughout the entire workflow, sending the access_token field to any recipient is prohibited."),
    15: ("8. 字段取值要求不包含摘要生成、内容改写或额外格式转换。", "8. The field-value requirements do not include summary generation, content rewriting, or additional format conversion."),
    16: ("9. 处理完成后，将处理条数写入本地 count.txt。", "9. After processing is complete, write the number of processed records to the local count.txt."),
}
_CFG_TEXT = {
    ("constraints", 0): (_SOURCE_LINES[14][0][3:], _SOURCE_LINES[14][1][3:]),
    ("constraints", 1): (_SOURCE_LINES[15][0][3:], _SOURCE_LINES[15][1][3:]),
    ("blocks", "block_001", "block_name"): ("读取用户提供的 events.json", "Read the user-provided events.json"),
    ("blocks", "block_001", "instructions", 0, "inputs", 0, "identifier"): ("用户提供的 events.json", "user-provided events.json"),
    ("blocks", "block_001", "instructions", 0, "inputs", 0, "semantic_name"): ("用户提供的 events.json", "user-provided events.json"),
    ("blocks", "block_001", "constraints", 0): (_SOURCE_LINES[8][0][3:], _SOURCE_LINES[8][1][3:]),
    ("blocks", "block_002", "block_name"): ("根据 opted_out、urgent 和 value 条件选中记录", "Select records using the opted_out, urgent, and value conditions"),
    ("blocks", "block_002", "instructions", 0, "constraints", 0): (_SOURCE_LINES[9][0][3:], _SOURCE_LINES[9][1][3:]),
    ("blocks", "block_002", "instructions", 0, "constraints", 1): (_SOURCE_LINES[10][0][3:], _SOURCE_LINES[10][1][3:]),
    ("blocks", "block_003", "block_name"): ("对每条选中记录调用 notify.send", "Call notify.send for each selected record"),
    ("blocks", "block_003", "instructions", 0, "constraints", 0): (_SOURCE_LINES[11][0][3:], _SOURCE_LINES[11][1][3:]),
    ("blocks", "block_003", "instructions", 0, "constraints", 1): (_SOURCE_LINES[12][0][3:], _SOURCE_LINES[12][1][3:]),
    ("blocks", "block_003", "instructions", 0, "constraints", 2): (_SOURCE_LINES[13][0][3:], _SOURCE_LINES[13][1][3:]),
    ("blocks", "block_004", "block_name"): ("统计已处理条数", "Count processed records"),
    ("blocks", "block_005", "block_name"): ("将处理条数写入本地 count.txt", "Write the processed-record count to the local count.txt"),
    ("blocks", "block_005", "instructions", 0, "constraints", 0): (_SOURCE_LINES[16][0][3:], _SOURCE_LINES[16][1][3:]),
}


def _hash(data):
    return hashlib.sha256(data).hexdigest()


def _json(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _no_links(path):
    for item in (path, *path.parents):
        if item.exists() or item.is_symlink():
            info = item.lstat()
            if item.is_symlink() or getattr(info, "st_file_attributes", 0) & 0x400:
                raise ValueError("English pilot inputs must not contain links or reparse points")


def _source_english(data):
    text = data.decode("utf-8")
    lines = text.splitlines(keepends=True)
    changes = []
    for number, (before, after) in _SOURCE_LINES.items():
        line = lines[number - 1]
        body = line.rstrip("\r\n")
        if body != before:
            raise ValueError(f"Pinned 001 source line {number} differs from the translation baseline")
        lines[number - 1] = after + line[len(body):]
        changes.append({"file": "SKILL.md", "start_line": number, "end_line": number,
                        "before": before, "after": after})
    result = "".join(lines)
    if _HAN.search(result):
        raise ValueError("Unmapped non-English source text in the fixed 001 input")
    assert len(result.splitlines()) == len(text.splitlines())
    return result.encode("utf-8"), changes


def _cfg_english(graph):
    result = deepcopy(graph)
    changes = []
    for path, (before, after) in _CFG_TEXT.items():
        parent = result
        for part in path[:-1]:
            parent = parent[part]
        if parent[path[-1]] != before:
            raise ValueError(f"Pinned 001 CFG text differs at {path!r}")
        parent[path[-1]] = after
        changes.append({"path": list(path), "before": before, "after": after})
    if _HAN.search(json.dumps(result, ensure_ascii=False)):
        raise ValueError("Unmapped non-English text in the fixed 001 CFG")
    return result, changes


def _expected(records):
    if set(records) != {"001", "010", "013"}:
        raise ValueError("English pilot projection requires exactly the three fixed cases")
    files, cases = {}, {}
    for case in sorted(records):
        package = Path(records[case]["input"]).absolute()
        analysis_path = Path(records[case]["analysis"]).absolute()
        _no_links(package)
        _no_links(analysis_path)
        original_analysis = analysis_path.read_bytes()
        analysis = json.loads(original_analysis.decode("utf-8"))
        if set(analysis) != {"cfg"}:
            raise ValueError("English pilot projection expects an analysis containing only cfg")
        source_changes, original_members, projected_members = [], {}, {}
        for path in sorted(package.rglob("*")):
            _no_links(path)
            if not path.is_file():
                continue
            relative = path.relative_to(package).as_posix()
            data = path.read_bytes()
            original_members[relative] = _hash(data)
            if case == "001" and relative == "SKILL.md":
                data, source_changes = _source_english(data)
            else:
                try:
                    decoded = data.decode("utf-8")
                except UnicodeDecodeError as error:
                    raise ValueError("The fixed English pilot accepts only its verified UTF-8 source files") from error
                if _HAN.search(decoded):
                    raise ValueError(f"Unmapped non-English pilot source: {case}/{relative}")
            projected_members[relative] = _hash(data)
            files[f"{case}/package/{relative}"] = data
        if case == "001":
            if not source_changes:
                raise ValueError("Pinned 001 SKILL.md is missing")
            graph, cfg_changes = _cfg_english(analysis["cfg"])
            projected_analysis = _json({"cfg": graph})
        else:
            graph, cfg_changes = analysis["cfg"], []
            if _HAN.search(json.dumps(graph, ensure_ascii=False)):
                raise ValueError(f"Unmapped non-English pilot CFG: {case}")
            projected_analysis = original_analysis
        files[f"{case}/selected-analysis.json"] = projected_analysis
        files[f"{case}/projection.json"] = _json({
            "identity": IDENTITY, "case": case,
            "origin": "assistant_translation" if source_changes else "unchanged_verified_input",
            "original_package": str(package), "original_analysis": str(analysis_path),
            "original_source_files": original_members, "projected_source_files": projected_members,
            "original_analysis_sha256": _hash(original_analysis),
            "projected_analysis_sha256": _hash(projected_analysis),
            "source_changes": source_changes, "cfg_changes": cfg_changes,
            "claim": "Explicit English text projection; no CFG extraction or semantic equivalence proof. Topology, instruction IDs, operand structure, paths, and literal business values are retained.",
        })
        cases[case] = {"input": f"{case}/package", "analysis": f"{case}/selected-analysis.json"}
    return files, {"identity": IDENTITY, "cases": cases,
                   "files": {name: _hash(data) for name, data in sorted(files.items())}}


def _check_target(directory, records):
    directory = Path(directory).absolute()
    _no_links(directory)
    directory = directory.resolve()
    for row in records.values():
        for name in ("input", "analysis"):
            original = Path(row[name]).resolve()
            if directory == original or directory.is_relative_to(original) or original.is_relative_to(directory):
                raise ValueError("English projection must not overlap historical inputs")
    return directory


def _check_existing(directory, files, *, require_complete):
    actual = set()
    if directory.exists():
        for path in directory.rglob("*"):
            _no_links(path)
            if path.is_file():
                relative = path.relative_to(directory).as_posix()
                actual.add(relative)
                if relative not in files or path.read_bytes() != files[relative]:
                    raise ValueError(f"English input projection differs: {relative}")
    if require_complete and actual != set(files):
        raise ValueError("English input projection inventory is incomplete")


def prepare_english_inputs(records, directory):
    directory = _check_target(directory, records)
    files, receipt = _expected(records)
    _check_existing(directory, files, require_complete=False)
    for relative, data in files.items():
        path = directory / relative
        if not path.exists():
            atomic_write_text(path, data.decode("utf-8"))
    _check_existing(directory, files, require_complete=True)
    return receipt


def verify_english_inputs(records, directory, receipt):
    directory = _check_target(directory, records)
    files, expected_receipt = _expected(records)
    if receipt != expected_receipt:
        raise ValueError("English input projection receipt differs")
    _check_existing(directory, files, require_complete=True)
    return receipt
