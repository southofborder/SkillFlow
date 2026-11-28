"""Freeze or verify 100 static Skill packages from the sealed ClawHub cache."""

import argparse
from collections import Counter
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import zipfile


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CATALOG = REPO / "experiments/doe/inputs/clawhub-top1000-v1"
SOURCES = HERE / "clawhub-sources"
MANIFEST = HERE / "clawhub-complex.json"
CASE_COUNT = 100
MAX_SOURCE_BYTES = 500_000
CODE_SUFFIXES = frozenset(
    ".bash .bat .c .cc .cjs .clj .cpp .cs .dart .ex .exs .go .h .hpp .java "
    ".js .jsx .kt .kts .lua .mjs .php .pl .ps1 .py .r .rb .rs .scala .sh .sql "
    ".swift .ts .tsx .vue .zsh".split()
)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_bytes(path, expected_hash=None):
    data = path.read_bytes()
    if expected_hash is not None and sha256(data) != expected_hash:
        raise ValueError(f"SHA-256 mismatch: {path}")
    return data


def read_json(path, expected_hash=None):
    return json.loads(read_bytes(path, expected_hash))


def catalog_path(relative):
    name = PurePosixPath(relative)
    path = (CATALOG / name).resolve(strict=True)
    if name.as_posix() != relative or ".." in name.parts or not path.is_relative_to(CATALOG):
        raise ValueError(f"Unsafe catalog path: {relative}")
    return path


def artifact(path, digest=None):
    return {"path": path.relative_to(REPO).as_posix(), "sha256": digest or sha256(path.read_bytes())}


def inventory(rows):
    files = {row["path"]: (row["size"], row["sha256"]) for row in rows}
    if len(files) != len(rows):
        raise ValueError("Duplicate paths in upstream file inventory")
    return files


def candidate(entry, freeze, rejected):
    if entry["acquisition_status"] != "complete_verified":
        rejected["incomplete_acquisition"] += 1
        return None

    result_path = catalog_path(entry["result_path"])
    if freeze["files"][entry["result_path"]] != entry["result_sha256"]:
        raise ValueError(f"Acquisition result is absent from the corpus seal: {result_path}")
    result = read_json(result_path, entry["result_sha256"])
    if any(result[field] != entry[field] for field in (
        "identity", "rank", "version_pin", "source_kind", "archive_sha256",
        "source_view_path", "source_view_sha256",
    )) or result["status"] != "complete_verified" or result["file_integrity"] != "verified":
        raise ValueError(f"Acquisition identity mismatch: {result_path}")
    if result["source_kind"] != "hosted" or not result["version_pin"]:
        rejected["unsupported_source"] += 1
        return None

    view_path = catalog_path(result["source_view_path"])
    view = read_json(view_path, result["source_view_sha256"])
    if view["unresolved_provenance"] or any(
        row["provenance"] != "registry_generated"
        for row in view["files"] if not row["include_in_source"]
    ):
        rejected["unresolved_provenance"] += 1
        return None

    rows = sorted((row for row in view["files"] if row["include_in_source"]), key=lambda row: row["path"])
    original_files = inventory(rows)
    excluded = [row for row in view["files"] if not row["include_in_source"]]
    version_path = result_path.parent / "version.json"
    version = read_json(version_path)["version"]
    version_files = inventory(version["files"])
    for row in excluded:
        if row["path"] in version_files and version_files.pop(row["path"]) != (row["size"], row["sha256"]):
            raise ValueError(f"Registry metadata differs in the version inventory: {version_path}")
    if version["version"] != result["version_pin"] or original_files != version_files:
        raise ValueError(f"Author source differs from the pinned version inventory: {version_path}")
    if len(rows) != result["source_file_count"] or len(rows) != view["source_file_count"]:
        raise ValueError(f"Author source file count differs: {view_path}")
    if "SKILL.md" not in original_files:
        rejected["missing_root_skill_md"] += 1
        return None

    total_bytes = sum(row["size"] for row in rows)
    if total_bytes > MAX_SOURCE_BYTES:
        rejected["over_package_byte_limit"] += 1
        return None
    code_paths = {row["path"] for row in rows if PurePosixPath(row["path"]).suffix.lower() in CODE_SUFFIXES}
    if len(rows) < 3 or not code_paths:
        rejected["below_minimum_structure"] += 1
        return None

    bodies = {}
    code_lines = 0
    for row in rows:
        stored_path = catalog_path(row["stored_path"])
        if stored_path.relative_to(result_path.parent / "files").as_posix() != row["path"]:
            raise ValueError(f"Stored path differs from the version path: {stored_path}")
        body = read_bytes(stored_path, row["sha256"])
        if len(body) != row["size"]:
            raise ValueError(f"File size mismatch: {stored_path}")
        try:
            text = body.decode("utf-8-sig")
        except UnicodeDecodeError:
            rejected["non_utf8_source"] += 1
            return None
        if "\x00" in text:
            rejected["nul_in_source"] += 1
            return None
        if row["path"] in code_paths:
            code_lines += sum(bool(line.strip()) for line in text.splitlines())
        bodies[row["path"]] = body
    if code_lines == 0:
        rejected["no_nonblank_implementation"] += 1
        return None

    case_id = f"clawhub-{entry['rank']:04d}"
    files = [{key: row[key] for key in ("path", "size", "sha256")} for row in rows]
    byte_identity = [{"path": row["path"], "size": row["size"], "raw_sha256": row["sha256"]} for row in files]
    package_bytes_sha256 = sha256(json.dumps(
        byte_identity, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8"))
    return {
        "case_id": case_id,
        "identity": entry["identity"],
        "slug": entry["slug"],
        "owner_handle": entry["ownerHandle"],
        "version": entry["version_pin"],
        "roster_rank": entry["rank"],
        "source_directory": (SOURCES / case_id).relative_to(REPO).as_posix(),
        "package_bytes_sha256": package_bytes_sha256,
        "file_count": len(files),
        "total_bytes": total_bytes,
        "implementation_file_count": len(code_paths),
        "implementation_nonblank_lines": code_lines,
        "files": files,
        "acquisition": {
            "mode": "reused_verified_clawhub_download",
            "result": artifact(result_path, entry["result_sha256"]),
            "source_view": artifact(view_path, entry["source_view_sha256"]),
            "version_metadata": artifact(version_path),
            "archive": artifact(result_path.parent / "download.response", entry["archive_sha256"]),
            "registry_generated_files_excluded": [row["path"] for row in excluded],
        },
    }, bodies


def verify_archive(case, bodies):
    acquisition = case["acquisition"]
    archive_ref = acquisition["archive"]
    archive_path = REPO / archive_ref["path"]
    raw = read_bytes(archive_path, archive_ref["sha256"])
    result_ref = acquisition["result"]
    result = read_json(REPO / result_ref["path"], result_ref["sha256"])
    expected = dict(bodies)
    if result.get("recovery_kind") == "exact_version_registry_meta_overlay":
        prior = read_json(catalog_path(result["recovered_from_result_path"]), result["recovered_from_result_sha256"])
        original = read_bytes(archive_path.parent / "recovered-original-meta.response", result["recovered_source_sha256"])
        if (prior["download_sha256"] != archive_ref["sha256"] or result["recovery_file_http_status"] != 200
                or len(original) != result["recovered_source_size"] or original != expected["_meta.json"]):
            raise ValueError(f"Recovered author metadata differs: {archive_path}")
        expected["_meta.json"] = read_bytes(archive_path.parent / "archive-files" / "_meta.json")
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = [member.filename for member in archive.infolist() if not member.is_dir()]
        if len(names) != len(set(names)) or set(names) != set(expected).union(acquisition["registry_generated_files_excluded"]):
            raise ValueError(f"Archive member inventory differs: {archive_path}")
        for name, body in expected.items():
            if archive.read(name) != body:
                raise ValueError(f"Archive member bytes differ: {archive_path}: {name}")


def collect():
    freeze_path = CATALOG / "corpus-freeze-v1.json"
    freeze = read_json(freeze_path)
    manifest_path = CATALOG / "source-manifest.json"
    catalog = read_json(manifest_path, freeze["files"][manifest_path.name])
    if len(catalog["entries"]) != 1000 or len({row["identity"] for row in catalog["entries"]}) != 1000:
        raise ValueError("The frozen source catalog must contain 1,000 distinct roster entries")
    rejected = Counter()
    eligible = []
    seen_packages = set()
    for row in sorted(catalog["entries"], key=lambda row: row["rank"]):
        item = candidate(row, freeze, rejected)
        if item is None:
            continue
        case, _ = item
        if case["package_bytes_sha256"] in seen_packages:
            rejected["exact_duplicate_package"] += 1
            continue
        seen_packages.add(case["package_bytes_sha256"])
        eligible.append(item)

    if len(eligible) < CASE_COUNT:
        raise ValueError(f"Only {len(eligible)} of {CASE_COUNT} required eligible packages are available")
    selected = sorted(eligible, key=lambda item: (
        -item[0]["implementation_nonblank_lines"], -item[0]["implementation_file_count"],
        -item[0]["file_count"], item[0]["roster_rank"],
    ))[:CASE_COUNT]
    for case, bodies in selected:
        verify_archive(case, bodies)

    return ({
        "schema": "skillflow-clawhub-complex-cohort-v1",
        "status": "sources_verified",
        "source_catalog": {
            **artifact(manifest_path, freeze["files"][manifest_path.name]),
            "corpus_seal": artifact(freeze_path),
            "registry_documentation": "https://docs.openclaw.ai/clawhub/api",
        },
        "selection": {
            "scope": "Sealed ClawHub downloads-ranked roster; file-based complexity proxy.",
            "min_source_files": 3,
            "required_root_file": "SKILL.md",
            "max_total_source_bytes": MAX_SOURCE_BYTES,
            "source_encoding": "strict UTF-8 (BOM permitted); NUL rejected",
            "implementation_suffixes": sorted(CODE_SUFFIXES),
            "ranking": ["implementation_nonblank_lines_desc", "implementation_file_count_desc",
                        "file_count_desc", "roster_rank_asc"],
            "exact_duplicate_policy": "Retain the lowest roster rank before scoring.",
            "pool_count": len(catalog["entries"]),
            "eligible_count": len(eligible),
            "rejected_counts": dict(sorted(rejected.items())),
            "selected_count": len(selected),
        },
        "independent_tasks": None,
        "labels": None,
        "cases": [case for case, _ in selected],
    }, selected)


def write_verified(path, expected, *, verify):
    if verify or path.exists():
        if path.is_symlink() or read_bytes(path) != expected:
            raise ValueError(f"Existing artifact differs: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(expected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "verify"))
    verify = parser.parse_args().action == "verify"
    manifest, selected = collect()
    for case, bodies in selected:
        directory = REPO / case["source_directory"]
        for name, body in bodies.items():
            destination = directory / name
            if destination.resolve() != destination or not destination.is_relative_to(SOURCES):
                raise ValueError(f"Unsafe materialization destination: {destination}")
            write_verified(destination, body, verify=verify)
        actual = {path.relative_to(directory).as_posix() for path in directory.rglob("*") if path.is_file()}
        if actual != set(bodies):
            raise ValueError(f"Materialized file inventory differs: {directory}")
    if {path.name for path in SOURCES.iterdir()} != {case["case_id"] for case, _ in selected}:
        raise ValueError(f"Materialized package inventory differs: {SOURCES}")
    encoded_manifest = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    write_verified(MANIFEST, encoded_manifest, verify=verify)
    print(f"Verified {len(selected)} ClawHub packages and {sum(case['file_count'] for case, _ in selected)} source files.")


if __name__ == "__main__":
    main()
