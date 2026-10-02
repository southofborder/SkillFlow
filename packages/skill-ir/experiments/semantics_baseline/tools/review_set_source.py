"""Read verified baseline sources and create deterministic, input-only Skill ZIPs.

Selection is structural: the first complete repetition wins, without consulting
external fact annotations or review verdicts. No Skill code or model is executed.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import zipfile

_PACKAGE = Path(__file__).resolve().parents[3]
if str(_PACKAGE / "src") not in sys.path:
    sys.path.insert(0, str(_PACKAGE / "src"))

from skill_ir.artifacts.analysis_json import load_analysis_cfg
from skill_ir.inputs.skill_package import load_skill_package

_SPEC = importlib.util.spec_from_file_location(
    "review_set_result_integrity", Path(__file__).with_name("result_integrity.py")
)
integrity = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(integrity)

SAMPLE_IDS = tuple(f"{group}{number:02}" for group in "NQFDR" for number in range(1, 7))
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
_BASE_RELATIVE = Path("packages/skill-ir/experiments/semantics_baseline")


def _read(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def _digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _safe_path(root: Path, relative: str) -> Path:
    if not isinstance(relative, str):
        raise ValueError("Expected a relative source path")
    parts = PurePosixPath(relative).parts
    if (not parts or relative != "/".join(parts) or ".." in parts
            or "\\" in relative or ":" in relative or "\x00" in relative
            or PurePosixPath(relative).is_absolute()):
        raise ValueError(f"Unsafe source path: {relative!r}")
    path = root.joinpath(*parts)
    if path.is_symlink() or path.resolve() != path.absolute():
        raise ValueError(f"Linked or escaping source path: {relative!r}")
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Source path escapes its root: {relative!r}")
    return path


def _frozen_catalog(base: Path) -> tuple[dict, list[dict]]:
    """Verify the input catalog lock without reading annotation bodies."""
    manifest = _read(base / "freeze_manifest.json")
    if manifest.get("schema_version") != 1:
        raise ValueError("Unsupported freeze manifest schema")
    files = manifest.get("files", {})
    if integrity.freeze.inventory_digest(files) != manifest.get("content_sha256"):
        raise ValueError("Frozen manifest aggregate digest mismatch")
    catalog_path = base / "frozen/corpus/corpus.json"
    raw = catalog_path.read_bytes()
    if files.get("corpus/corpus.json") != {"sha256": _digest(raw), "bytes": len(raw)}:
        raise ValueError("Frozen corpus catalog changed")
    samples = _read(catalog_path).get("samples", [])
    if [sample.get("id") for sample in samples] != list(SAMPLE_IDS):
        raise ValueError("Expected fixed 30-sample N/Q/F/D/R corpus order")
    paths = [sample.get("package_path") for sample in samples]
    if len(set(paths)) != len(SAMPLE_IDS):
        raise ValueError("Frozen Skill package paths must be unique")
    for sample in samples:
        relative = sample["package_path"]
        parts = PurePosixPath(relative).parts
        if len(parts) != 3 or parts[0] != "inputs" or parts[1] not in {"controlled", "upstream"}:
            raise ValueError("Only individual frozen Skill inputs may be exported")
        _safe_path(base / "frozen/corpus", relative)
    return manifest, samples


def _package_files(base: Path, package: Path, manifest: dict) -> dict[str, bytes]:
    root = base / "frozen/corpus"
    relative = package.relative_to(root).as_posix()
    package = _safe_path(root, relative)
    if not package.is_dir():
        raise ValueError(f"Missing frozen Skill package: {package}")
    prefix = "corpus/" + relative + "/"
    expected = {name[len(prefix):]: value for name, value in manifest["files"].items()
                if name.startswith(prefix)}
    actual = {}
    for path in sorted(package.rglob("*")):
        name = path.relative_to(package).as_posix()
        _safe_path(package, name)
        if path.is_file():
            actual[name] = path.read_bytes()
        elif not path.is_dir():
            raise ValueError(f"Unsupported Skill input member: {name}")
    inventory = {name: {"sha256": _digest(raw), "bytes": len(raw)} for name, raw in actual.items()}
    if inventory != expected or "SKILL.md" not in actual:
        raise ValueError(f"Frozen Skill package bytes or inventory changed: {package.name}")
    return actual


def _skill_name(raw: bytes) -> str:
    """Read the simple scalar name used by the pinned corpus, stripping YAML quotes."""
    lines = raw.decode("utf-8-sig").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("SKILL.md requires YAML frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise ValueError("Unclosed SKILL.md frontmatter") from error
    values = [line[len("name:"):].strip() for line in lines[1:end] if line.startswith("name:")]
    if len(values) != 1:
        raise ValueError("SKILL.md requires exactly one frontmatter name")
    value = values[0]
    if value.startswith('"'):
        try:
            value = json.loads(value)
        except json.JSONDecodeError as error:
            raise ValueError("Invalid quoted Skill name") from error
    elif value.startswith("'"):
        if not value.endswith("'") or len(value) < 2:
            raise ValueError("Invalid quoted Skill name")
        value = value[1:-1].replace("''", "'")
    if not isinstance(value, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
        raise ValueError("Skill name must be a portable lowercase filename component")
    return value


def build_export_plan(repo_root: Path, run_dir: Path) -> list[dict]:
    """Choose each sample's earliest complete repetition, rejecting stale evidence.

    A corrupted earliest complete result is an error, never permission to silently
    substitute a later result. Failed/degraded/uncertain trials are not candidates.
    """
    base = Path(repo_root).expanduser().resolve() / _BASE_RELATIVE
    run = Path(run_dir).expanduser().resolve()
    manifest, samples = _frozen_catalog(base)
    experiment = _read(run / "experiment.json")
    report = _read(run / "report.json")
    variant = integrity.select_result_variant(experiment)
    provenance = experiment.get("provenance", {})
    if (provenance.get("freeze_manifest_sha256") != integrity.sha(base / "freeze_manifest.json")
            or provenance.get("contract") != "constraints-v2"):
        raise ValueError("Run is not bound to this frozen constraints-v2 corpus")
    if experiment.get("repetitions") != 3:
        raise ValueError("Export requires the recorded three-repetition experiment")
    if (report.get("mode") != "online" or report.get("name") != experiment.get("name")
            or not isinstance(report.get("run_id"), str) or not report["run_id"]):
        raise ValueError("Report and experiment identity disagree")
    cases = experiment.get("cases", [])
    identities = {case["id"]: case for case in cases}
    dataset = _read(run / "dataset.json").get("cases", [])
    if (len(cases) != 30 or set(identities) != set(SAMPLE_IDS)
            or len(dataset) != 30 or {case["id"] for case in dataset} != set(SAMPLE_IDS)):
        raise ValueError("Run must retain all 30 frozen input identities")
    for case in dataset:
        if any(case.get(key) != value for key, value in identities[case["id"]].items()):
            raise ValueError("Dataset and experiment input identity disagree")
    trials = report.get("trials", [])
    expected_trials = {(sid, variant, rep) for sid in SAMPLE_IDS for rep in (1, 2, 3)}
    if (len(trials) != 90 or {(t.get("case"), t.get("variant"), t.get("repetition"))
                              for t in trials} != expected_trials):
        raise ValueError("Report must retain exactly the 30 by 3 trial plan")
    plan = []
    for index, sample in enumerate(samples, 1):
        sid = sample["id"]
        package = _safe_path(base / "frozen/corpus", sample["package_path"])
        files = _package_files(base, package, manifest)
        identity = identities[sid]
        loaded = load_skill_package(package)
        canonical = json.dumps(loaded.model_dump(mode="json"), ensure_ascii=False,
                               sort_keys=True, separators=(",", ":")).encode("utf-8")
        if (identity.get("split") != sample["split"]
                or identity.get("extraction_input_sha256") != _digest(canonical)):
            raise ValueError(f"Run input identity differs from frozen package: {sid}")
        candidates = sorted((t for t in trials if t["case"] == sid and t["status"] == "complete"),
                            key=lambda t: t["repetition"])
        if not candidates:
            raise ValueError(f"No complete repetition available: {sid}")
        selected = candidates[0]
        path = _safe_path(run, selected["artifacts"])
        record = _read(path / "record.json")
        integrity.verify_trial_record(record, selected, path, identity)
        analysis_path = path / "analysis.json"
        analysis = _read(analysis_path)
        if analysis.get("status") != "complete":
            raise ValueError(f"Selected analysis is not complete: {sid}")
        cfg = load_analysis_cfg(analysis_path)
        if (record.get("split") != sample["split"]
                or record.get("blocks") != len(cfg.blocks) or record.get("edges") != len(cfg.edges)
                or any(record.get(key) != analysis.get(key) for key in ("status", "attempts", "diagnostics"))):
            raise ValueError(f"Analysis and record summary disagree: {sid}")
        name = _skill_name(files["SKILL.md"])
        plan.append({"index": index, "sample_id": sid, "skill_name": name,
                     "basename": f"{index:03d}-{name}", "repetition": selected["repetition"],
                     "package_path": str(package.resolve()), "analysis_path": str(analysis_path.resolve()),
                     "analysis_sha256": record["artifact_sha256"]["analysis.json"],
                     "cfg": cfg.model_dump(mode="json"), "run_id": report["run_id"]})
    return plan


def _item_files(item: dict) -> tuple[Path, dict[str, bytes]]:
    package = Path(item["package_path"])
    if not package.is_absolute() or len(package.parents) < 5:
        raise ValueError("Export item requires an absolute frozen package path")
    base = package.parents[4]
    manifest, samples = _frozen_catalog(base)
    matches = [sample for sample in samples if sample["id"] == item["sample_id"]]
    if len(matches) != 1 or package != base / "frozen/corpus" / matches[0]["package_path"]:
        raise ValueError("Export item does not identify its frozen Skill input")
    files = _package_files(base, package, manifest)
    index = SAMPLE_IDS.index(item["sample_id"]) + 1
    name = _skill_name(files["SKILL.md"])
    if (item["index"] != index or item["skill_name"] != name
            or item["basename"] != f"{index:03d}-{name}"):
        raise ValueError("Export item name or numbering differs from its frozen Skill")
    return base, files


def write_skill_zip(item: dict, destination: Path) -> None:
    """Create a new deterministic ZIP with original bytes and SKILL.md at root."""
    base, files = _item_files(item)
    destination = Path(destination).expanduser().resolve()
    if destination.is_relative_to(base / "frozen"):
        raise ValueError("Cannot write an export into the frozen tree")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "x", compression=zipfile.ZIP_STORED) as archive:
        for name, raw in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=ZIP_TIMESTAMP)
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.compress_type = zipfile.ZIP_STORED
            archive.writestr(info, raw)


def verify_skill_zip(item: dict, destination: Path) -> dict:
    """Require the exact frozen member paths and bytes, without extracting files."""
    _, files = _item_files(item)
    destination = Path(destination)
    with zipfile.ZipFile(destination) as archive:
        members = archive.infolist()
        if [member.filename for member in members] != sorted(files):
            raise ValueError("ZIP inventory differs from the frozen Skill input")
        for member in members:
            if (member.is_dir() or stat.S_ISLNK(member.external_attr >> 16)
                    or member.date_time != ZIP_TIMESTAMP or member.compress_type != zipfile.ZIP_STORED
                    or member.extra or member.comment):
                raise ValueError(f"Unexpected ZIP member metadata: {member.filename}")
            if archive.read(member) != files[member.filename]:
                raise ValueError(f"ZIP member bytes differ from frozen source: {member.filename}")
        if archive.comment:
            raise ValueError("Unexpected ZIP archive comment")
    return {"sample_id": item["sample_id"], "basename": item["basename"],
            "zip_sha256": integrity.sha(destination), "file_count": len(files),
            "files": {name: {"sha256": _digest(raw), "bytes": len(raw)} for name, raw in sorted(files.items())}}
