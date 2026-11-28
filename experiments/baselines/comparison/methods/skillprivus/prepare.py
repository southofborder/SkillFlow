"""Prepare and validate one paper-based SkillPrivus audit without model access."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import tempfile


HERE = Path(__file__).resolve().parent
COMPARISON = HERE.parents[1]
REPO = COMPARISON.parents[2]
PAPER = "arXiv:2611.26747v1"
VARIANT = "skillprivus-paper-based-v1"
STAGES = ("screening", "extraction", "judgment", "harm")
OPERATIONS = {"Read", "Infer", "Save", "Send", "Delete"}
DEPARTURES = {"recipient", "info_type", "subject", "access", "derivation"}
CI_REQUIRED = ("subject", "sender", "recipient", "info_type", "transmission_principle", "domain", "expected_norm")
HARMS = {
    "Surveillance", "Interrogation", "Aggregation", "Identification", "Secondary Use",
    "Exclusion", "Breach of Confidentiality", "Disclosure", "Exposure", "Increased Accessibility",
    "Appropriation", "Distortion", "Inference",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value, *, compact=False) -> bytes:
    if compact:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode()


def unique_keys(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"Duplicate JSON key: {key}")
        value[key] = item
    return value


def parse(data: bytes):
    return json.loads(data, object_pairs_hook=unique_keys)


def safe_id(value: str) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,80}", value) is None:
        raise ValueError(f"Invalid run or case ID: {value!r}")
    return value


def regular_path(path: Path) -> None:
    info = path.lstat()
    reparse = getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    if stat.S_ISLNK(info.st_mode) or reparse:
        raise ValueError(f"Links and reparse points are outside the source view: {path}")


def relative_path(value: str) -> Path:
    path = PurePosixPath(value)
    if path.is_absolute() or path.as_posix() != value or not path.parts or ".." in path.parts or "\\" in value or ":" in value:
        raise ValueError(f"Invalid repository-relative path: {value!r}")
    return Path(*path.parts)


def freeze_json(path: Path, value) -> str:
    data = json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".pending-", delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(data)
    try:
        os.link(temporary, path)
    except FileExistsError:
        regular_path(path)
        if path.read_bytes() != data:
            raise ValueError(f"Refusing to replace an existing artifact: {path}")
    finally:
        temporary.unlink()
    return digest(data)


def source_files(case: dict) -> list[dict]:
    source = REPO / relative_path(case["source_directory"])
    if not source.resolve(strict=True).is_relative_to(REPO):
        raise ValueError(f"Source directory escapes the repository: {source}")
    regular_path(source)
    entries = case["files"]
    expected = {entry["path"]: entry for entry in entries}
    for path in expected:
        relative_path(path)
    if len(expected) != len(entries) or len(entries) != case["file_count"]:
        raise ValueError(f"Inconsistent source file count for case {case['case_id']}")

    actual = {}
    for directory, folders, files in os.walk(source):
        for member in folders + files:
            regular_path(Path(directory) / member)
        for member in files:
            path = Path(directory) / member
            if not path.is_file():
                raise ValueError(f"Expected a regular source file: {path}")
            actual[path.relative_to(source).as_posix()] = path
    if actual.keys() != expected.keys():
        raise ValueError(f"Source file inventory differs for case {case['case_id']}")

    package = []
    identity = []
    for name, path in sorted(actual.items()):
        data = path.read_bytes()
        file_hash = digest(data)
        if file_hash != expected[name]["sha256"] or len(data) != expected[name]["size"]:
            raise ValueError(f"Source hash or size differs: {path}")
        text = data.decode("utf-8")
        if "\0" in text:
            raise ValueError(f"NUL found in source text: {path}")
        package.append({"path": name, "sha256": file_hash, "text": text})
        identity.append({"path": name, "size": len(data), "raw_sha256": file_hash})
    if digest(json_bytes(identity, compact=True)) != case["package_bytes_sha256"]:
        raise ValueError(f"Package SHA-256 differs for case {case['case_id']}")
    if sum(entry["size"] for entry in identity) != case["total_bytes"]:
        raise ValueError(f"Package byte count differs for case {case['case_id']}")
    return package


def request(case_dir: Path, stage: str, inputs: dict) -> str:
    templates = case_dir.parents[1] / "prompt-templates"
    if not templates.is_dir():
        templates = HERE / "prompts"
    return freeze_json(case_dir / "requests" / f"{stage}.json", {
        "stage": stage,
        "instructions": (templates / f"{stage}.txt").read_text(encoding="utf-8"),
        "input": inputs,
    })


def prepare(run_dir: Path, cohort: Path, case_ids: list[str], *, execution: dict | None = None) -> int:
    raw = cohort.read_bytes()
    cases = parse(raw)["cases"]
    by_id = {safe_id(case["case_id"]): case for case in cases}
    if len(by_id) != len(cases):
        raise ValueError("Duplicate cohort case ID")
    selected = list(dict.fromkeys(case_ids)) if case_ids else list(by_id)
    for case_id in selected:
        if case_id not in by_id:
            raise ValueError(f"Unknown cohort case ID: {case_id}")
    manifest = {
        "variant": VARIANT,
        "paper": PAPER,
        "paper_backend": "gpt-oss-120b",
        "status": "offline_preparation",
        "cohort_path": cohort.resolve().relative_to(REPO).as_posix(),
        "cohort_sha256": digest(raw),
    }
    if execution is not None:
        manifest.update(execution)
    freeze_json(run_dir / "manifest.json", manifest)
    for case_id in selected:
        case = by_id[case_id]
        package = source_files(case)
        case_dir = run_dir / "cases" / case_id
        screening_hash = request(case_dir, "screening", {"skill": case["slug"], "files": package})
        (case_dir / "raw").mkdir(exist_ok=True)
        freeze_json(case_dir / "manifest.json", {
            "case_id": case_id,
            "skill": case["slug"],
            "version": case["version"],
            "source_directory": case["source_directory"],
            "file_count": case["file_count"],
            "package_bytes_sha256": case["package_bytes_sha256"],
            "screening_request_sha256": screening_hash,
        })
    return len(selected)


def assert_text(value, field, *, nullable=False):
    if value is None and nullable:
        return
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Expected nonempty text for {field}")


def check_evidence(evidence, sources: dict[str, list[str]], *, required=False) -> None:
    if not isinstance(evidence, list) or (required and not evidence):
        raise ValueError("Missing source evidence ranges")
    for entry in evidence:
        path = entry["path"]
        start, end = entry["start_line"], entry["end_line"]
        lines = sources.get(path, [])
        if type(start) is not int or type(end) is not int or not 1 <= start <= end <= len(lines):
            raise ValueError(f"Invalid evidence range: {path}:{start}-{end}")
        if entry["quote"] != "\n".join(lines[start - 1:end]):
            raise ValueError(f"Evidence differs from source: {path}:{start}-{end}")


def indexed_rows(rows, expected: set[str] | None = None) -> dict:
    if not isinstance(rows, list):
        raise ValueError("Expected an array of moves")
    found = {}
    for row in rows:
        move_id = row["move_id"]
        assert_text(move_id, "move_id")
        if move_id in found or (expected is not None and move_id not in expected):
            raise ValueError(f"Duplicate or unknown move ID: {move_id}")
        found[move_id] = row
    return found


def normalize(stage: str, answer, inputs: dict, sources: dict[str, list[str]]):
    if stage == "screening":
        if answer["status"] not in {"included", "excluded", "unresolved"}:
            raise ValueError("Unknown screening status")
        assert_text(answer["reason"], "screening reason")
        check_evidence(answer["evidence"], sources, required=answer["status"] == "included")
        return answer
    if stage == "extraction":
        if answer["status"] not in {"complete", "incomplete"}:
            raise ValueError("Unknown extraction status")
        assert_text(answer["reason"], "extraction reason")
        assert_text(answer["claim"], "claim", nullable=True)
        check_evidence(answer["claim_evidence"], sources, required=answer["claim"] is not None)
        for row in indexed_rows(answer["moves"]).values():
            if row["operation"] not in OPERATIONS:
                raise ValueError(f"Unknown operation: {row['operation']}")
            assert_text(row["data"], "move data")
            for field in ("source", "recipient", "condition"):
                assert_text(row[field], field, nullable=True)
            check_evidence(row["evidence"], sources, required=True)
        return answer

    expected = indexed_rows(inputs["moves"])
    found = indexed_rows(answer, set(expected))
    records = []
    for move_id in expected:
        row = found.get(move_id)
        if row is None:
            if stage == "judgment":
                records.append({"move_id": move_id, "verdict": "Incomplete", "departed_param": None,
                                "ci": None, "reason": "Judgment omitted in the submitted answer."})
            else:
                records.append({"move_id": move_id, "harm_type": None,
                                "reason": "Harm typing omitted in the submitted answer."})
            continue
        assert_text(row["reason"], "reason")
        if stage == "judgment":
            verdict = row["verdict"]
            if verdict not in {"Violation", "Ok", "Incomplete"}:
                raise ValueError(f"Unknown verdict: {verdict}")
            if verdict == "Violation" and row["departed_param"] not in DEPARTURES:
                raise ValueError(f"Missing or invalid departure for move {move_id}")
            ci = row["ci"]
            if not isinstance(ci, dict):
                raise ValueError(f"Expected CI object for move {move_id}")
            if any(field not in ci or not isinstance(ci[field], str) or not ci[field].strip() for field in CI_REQUIRED):
                row = {**row, "verdict": "Incomplete", "departed_param": None,
                       "coverage_reason": "Required CI field or expected norm is missing."}
        elif row["harm_type"] is not None and row["harm_type"] not in HARMS:
            raise ValueError(f"Unknown harm type: {row['harm_type']}")
        records.append(row)
    return records


def stage_record(case_dir: Path, stage: str):
    path = case_dir / "records" / f"{stage}.json"
    if path.is_file():
        record = parse(path.read_bytes())
        request_data = (case_dir / "requests" / f"{stage}.json").read_bytes()
        answer_data = (case_dir / "raw" / f"{stage}.json").read_bytes()
        if record["request_sha256"] != digest(request_data) or record["answer_sha256"] != digest(answer_data):
            raise ValueError(f"Request or answer changed for stage {stage}")
        return record["result"]
    return None


def finish(case_dir: Path, case: dict, screen: dict, result_file: str, variant: str) -> None:
    extraction = stage_record(case_dir, "extraction")
    judgments = stage_record(case_dir, "judgment")
    harms = stage_record(case_dir, "harm")
    moves = indexed_rows(extraction["moves"]) if extraction else {}
    by_harm = indexed_rows(harms) if harms else {}
    violations = None if judgments is None else [row for row in judgments if row["verdict"] == "Violation"]
    if screen["status"] != "included":
        status = "completed" if screen["status"] == "excluded" else "partial"
        native_status = "screened_out" if status == "completed" else "screening_unresolved"
    else:
        partial = (extraction["status"] == "incomplete" or
                   any(row["verdict"] == "Incomplete" for row in judgments or []) or
                   any(row["harm_type"] is None for row in harms or []))
        status = "partial" if partial else "completed"
        native_status = "incomplete" if partial else "analyzed"
    if extraction and extraction["status"] == "complete" and not moves:
        violations = []
    if extraction is not None:
        freeze_json(case_dir / "privacy-card.json", {
            "case_id": case["case_id"],
            "skill": case["skill"],
            "declared_claim": extraction["claim"],
            "claim_evidence": extraction["claim_evidence"],
            "observed_moves": list(moves.values()),
            "potential_violations": None if violations is None else [
                {"move": moves[row["move_id"]], "judgment": row, "harm": by_harm.get(row["move_id"])}
                for row in violations
            ],
        })
    freeze_json(case_dir / result_file, {
        "case_id": case["case_id"],
        "variant": variant,
        "package_bytes_sha256": case["package_bytes_sha256"],
        "status": status,
        "native_status": native_status,
        "screening": screen["status"],
        "move_count": None if extraction is None else len(moves),
        "violation_count": None if violations is None else len(violations),
        "incomplete_judgments": None if judgments is None else sum(row["verdict"] == "Incomplete" for row in judgments),
        "privacy_card": None if extraction is None else "privacy-card.json",
    })


def advance(run_dir: Path, case_id: str, stage: str, *, result_file: str = "result.json") -> str:
    case_dir = run_dir / "cases" / safe_id(case_id)
    case = parse((case_dir / "manifest.json").read_bytes())
    screen_data = (case_dir / "requests" / "screening.json").read_bytes()
    if digest(screen_data) != case["screening_request_sha256"]:
        raise ValueError("Prepared screening request differs from its manifest")
    screen_input = parse(screen_data)["input"]
    sources = {file["path"]: re.split(r"\r\n|\n|\r", file["text"]) for file in screen_input["files"]}
    for lines in sources.values():
        if lines[-1] == "":
            lines.pop()
    request_data = (case_dir / "requests" / f"{stage}.json").read_bytes()
    answer_data = (case_dir / "raw" / f"{stage}.json").read_bytes()
    result = normalize(stage, parse(answer_data), parse(request_data)["input"], sources)
    freeze_json(case_dir / "records" / f"{stage}.json", {
        "request_sha256": digest(request_data), "answer_sha256": digest(answer_data), "result": result,
    })
    screen = stage_record(case_dir, "screening")
    if stage == "screening" and screen["status"] == "included":
        request(case_dir, "extraction", screen_input)
        return "extraction"
    if stage == "extraction" and result["moves"]:
        request(case_dir, "judgment", {
            "skill": case["skill"], "claim": result["claim"],
            "claim_evidence": result["claim_evidence"], "moves": result["moves"],
        })
        return "judgment"
    if stage == "judgment":
        violations = [row for row in result if row["verdict"] == "Violation"]
        if violations:
            moves = indexed_rows(stage_record(case_dir, "extraction")["moves"])
            request(case_dir, "harm", {"moves": [
                {"move_id": row["move_id"], "move": moves[row["move_id"]], "judgment": row}
                for row in violations
            ]})
            return "harm"
    variant = parse((run_dir / "manifest.json").read_bytes())["variant"]
    finish(case_dir, case, screen, result_file, variant)
    return "finished"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prep = commands.add_parser("prepare", help="verify the frozen cohort and write screening packets")
    prep.add_argument("--run-id", required=True)
    prep.add_argument("--cohort", type=Path, default=COMPARISON / "inputs" / "clawhub-complex.json")
    prep.add_argument("--case-id", action="append", default=[])
    step = commands.add_parser("advance", help="validate a saved answer and construct the next packet")
    step.add_argument("--run-id", required=True)
    step.add_argument("--case-id", required=True)
    step.add_argument("--stage", choices=STAGES, required=True)
    args = parser.parse_args()
    run_dir = COMPARISON / "runs" / "skillprivus" / safe_id(args.run_id)
    if not run_dir.resolve().is_relative_to(COMPARISON):
        raise ValueError("Run path escapes comparison directory")
    if args.command == "prepare":
        print(f"Prepared {prepare(run_dir, args.cohort, args.case_id)} SkillPrivus screening packets.")
    else:
        print(f"Case {args.case_id}: {advance(run_dir, args.case_id, args.stage)}")


if __name__ == "__main__":
    main()
