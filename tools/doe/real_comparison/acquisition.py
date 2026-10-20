"""Read-only, pinned ClawHub acquisition with an immutable observed roster.

Downloaded material is untrusted data. This module never installs or executes it.
The public registry can change while a cursor is traversed; first-seen order is
recorded explicitly rather than claiming an atomic popularity snapshot.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import threading
import time
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlparse
from urllib.request import Request, urlopen
import uuid
import zipfile


SCHEMA = "skillflow.clawhub-acquisition.v1"
DEFAULT_BASE_URL = "https://clawhub.ai"
MAX_ARCHIVE_BYTES = 256 * 1024 * 1024
MAX_EXPANDED_BYTES = 512 * 1024 * 1024
MAX_FILE_BYTES = 128 * 1024 * 1024
MAX_FILES = 20000


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _immutable(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != value:
            raise ValueError(f"Immutable artifact differs: {path}")
        return
    with path.open("xb") as handle:
        handle.write(value)


def _write(path: Path, value: object) -> None:
    """Replace derived progress only; frozen evidence uses _immutable."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    temp.write_bytes(_json_bytes(value))
    os.replace(temp, path)


@dataclass(frozen=True)
class HTTPResponse:
    status: int
    headers: dict[str, str]
    body: bytes
    url: str = ""


def _transport(url: str) -> HTTPResponse:
    request = Request(url, headers={"User-Agent": "SkillFlow-research-corpus/1.0 (public read-only acquisition)", "Accept": "application/json, application/zip;q=0.9, */*;q=0.5"})
    try:
        response = urlopen(request, timeout=60)
    except HTTPError as error:
        response = error
    with response:
        body = response.read(MAX_ARCHIVE_BYTES + 1)
        if len(body) > MAX_ARCHIVE_BYTES:
            raise ValueError("HTTP response exceeds the acquisition byte limit.")
        return HTTPResponse(response.status, {k.lower(): v for k, v in response.headers.items()}, body, response.geturl())


class HTTPClient:
    """One shared request clock; every retry preserves its response and delay."""
    def __init__(self, transport: Callable[[str], HTTPResponse] | None = None, *, requests_per_second: float = 5, retries: int = 3, sleep: Callable[[float], None] = time.sleep, max_retry_wait: float = 300):
        if not 0 < requests_per_second <= 5:
            raise ValueError("Request rate must be greater than zero and at most five per second.")
        self.transport = transport or _transport
        self.interval = 1 / requests_per_second
        self.retries = retries
        self.sleep = sleep
        self.max_retry_wait = max_retry_wait
        self._next = 0.0
        self._lock = threading.Lock()

    def get(self, url: str, evidence_dir: Path, name: str) -> HTTPResponse:
        waited = 0.0
        for attempt in range(self.retries + 1):
            with self._lock:
                delay = max(0, self._next - time.monotonic())
                if delay:
                    self.sleep(delay)
                self._next = time.monotonic() + self.interval
            started = _now()
            try:
                response = self.transport(url)
                headers = {k.lower(): v for k, v in response.headers.items()}
                response = HTTPResponse(response.status, headers, response.body, response.url or url)
                error = None
            except (URLError, TimeoutError, OSError) as exception:
                response = HTTPResponse(0, {}, b"", url)
                error = f"{type(exception).__name__}: {exception}"
            stem = f"{name}-{attempt + 1:02d}"
            _immutable(evidence_dir / (stem + ".body"), response.body)
            record = {"url": url, "final_url": response.url, "started_at": started, "ended_at": _now(), "status": response.status, "headers": response.headers, "body_sha256": _hash(response.body), "body_size": len(response.body), "error": error}
            retry = response.status in (0, 429, 500, 502, 503, 504) and attempt < self.retries
            retry_delay = self._retry_delay(response.headers, attempt) if retry else 0
            if retry and waited + retry_delay > self.max_retry_wait:
                record["retry_stopped"] = "Required server delay exceeds the bounded retry wait; no early retry was issued."
                retry = False
            record["retry_delay_seconds"] = retry_delay if retry else None
            _immutable(evidence_dir / (stem + ".json"), _json_bytes(record))
            if not retry:
                return response
            waited += retry_delay
            self.sleep(retry_delay)
        raise AssertionError("Unreachable retry state.")

    @staticmethod
    def _retry_delay(headers: dict[str, str], attempt: int) -> float:
        value = headers.get("retry-after")
        if value:
            try:
                return max(0, float(value)) + 0.05
            except ValueError:
                try:
                    return max(0, parsedate_to_datetime(value).timestamp() - time.time()) + 0.05
                except (ValueError, TypeError):
                    pass
        if headers.get("ratelimit-reset"):
            try:
                return max(0, float(headers["ratelimit-reset"])) + 0.05
            except ValueError:
                pass
        if headers.get("x-ratelimit-reset"):
            try:
                return max(0, float(headers["x-ratelimit-reset"]) - time.time()) + 0.05
            except ValueError:
                pass
        return 2 ** attempt + 0.05


def _url(base: str, route: str, **query) -> str:
    values = {k: v for k, v in query.items() if v is not None}
    return base.rstrip("/") + route + ("?" + urlencode(values) if values else "")


def _identity(item: dict) -> str:
    owner, slug = item.get("ownerHandle"), item.get("slug")
    if not isinstance(owner, str) or not owner or not isinstance(slug, str) or not slug or "/" in owner or "/" in slug:
        raise ValueError("Roster item lacks an unambiguous ownerHandle/slug identity.")
    return owner + "/" + slug


def collect_roster(root: str | Path, target_count: int = 1000, base_url: str = DEFAULT_BASE_URL, *, client: HTTPClient | None = None, page_size: int = 200) -> dict:
    """Seal the first target_count distinct observed Skill identities, before downloads."""
    root = Path(root)
    roster = root / "roster"
    if (roster / "manifest.json").exists():
        manifest = _read(roster / "manifest.json")
        if manifest["target_count"] != target_count or manifest["base_url"] != base_url.rstrip("/"):
            raise ValueError("Requested roster parameters differ from the frozen roster.")
        errors = _verify_roster(root)
        if errors:
            raise ValueError("Frozen roster verification failed: " + "; ".join(errors))
        return manifest
    if target_count < 1 or not 1 <= page_size <= 200:
        raise ValueError("Roster count and page size are invalid.")
    client = client or HTTPClient()
    start_path = roster / "start.json"
    if start_path.exists():
        start = _read(start_path)
        if start["target_count"] != target_count or start["base_url"] != base_url.rstrip("/"):
            raise ValueError("Resume parameters differ from the original roster traversal.")
    else:
        start = {"schema": SCHEMA, "started_at": _now(), "target_count": target_count, "base_url": base_url.rstrip("/"), "sort": "downloads", "safety_filter": None, "rank_semantics": "First-seen distinct identities in a public downloads cursor traversal; not an atomic snapshot."}
        _immutable(start_path, _json_bytes(start))
    entries, seen, pages, duplicates = [], set(), [], []
    cursor, observed_position, cursor_seen = None, 0, set()
    page_no = 0
    while len(entries) < target_count:
        page_no += 1
        page_path = roster / "pages" / f"{page_no:04d}.json"
        record_path = roster / "pages" / f"{page_no:04d}.record.json"
        if page_path.exists():
            if not record_path.exists():
                raise ValueError("A roster page has no matching immutable request record.")
            record = _read(record_path)
            if record["cursor_in"] != cursor:
                raise ValueError("Stored roster cursor chain differs.")
            raw = page_path.read_bytes()
        else:
            url = _url(base_url, "/api/v1/skills", sort="downloads", limit=min(page_size, target_count - len(entries)), cursor=cursor)
            response = client.get(url, roster / "requests", f"page-{page_no:04d}-{uuid.uuid4().hex[:8]}")
            if response.status != 200:
                _write(roster / "progress.json", {"status": "incomplete", "error": f"Roster request returned HTTP {response.status}.", "collected": len(entries), "page": page_no, "cursor": cursor})
                return _read(roster / "progress.json")
            raw = response.body
            parsed = json.loads(raw)
            record = {"page": page_no, "url": url, "cursor_in": cursor, "cursor_out": parsed.get("nextCursor"), "received_at": _now(), "body_sha256": _hash(raw), "body_size": len(raw)}
            _immutable(record_path, _json_bytes(record))
            _immutable(page_path, raw)
        if _hash(raw) != record["body_sha256"]:
            raise ValueError("Stored roster page hash differs.")
        page = json.loads(raw)
        if not isinstance(page.get("items"), list):
            raise ValueError("Roster API response has no items array.")
        for index, item in enumerate(page["items"]):
            observed_position += 1
            identity = _identity(item)
            if identity in seen:
                duplicates.append({"identity": identity, "observed_page": page_no, "observed_item_index": index, "observed_position": observed_position})
                continue
            seen.add(identity)
            if len(entries) < target_count:
                entry = {"rank": len(entries) + 1, "identity": identity, "ownerHandle": item["ownerHandle"], "slug": item["slug"], "version_pin": (item.get("latestVersion") or {}).get("version"), "downloads": (item.get("stats") or {}).get("downloads"), "observed_page": page_no, "observed_item_index": index, "observed_position": observed_position, "raw_record": item}
                entries.append(entry)
        pages.append({"path": page_path.relative_to(root).as_posix(), "record_path": record_path.relative_to(root).as_posix(), "sha256": _hash(raw), "record_sha256": _hash(record_path.read_bytes())})
        _write(roster / "progress.json", {"status": "collecting", "collected": len(entries), "pages": page_no, "duplicates": len(duplicates), "cursor": page.get("nextCursor")})
        if len(entries) >= target_count:
            break
        next_cursor = page.get("nextCursor")
        if not next_cursor or next_cursor in cursor_seen:
            _write(roster / "progress.json", {"status": "incomplete", "collected": len(entries), "error": "Cursor traversal exhausted or repeated before the requested distinct roster was obtained."})
            return _read(roster / "progress.json")
        cursor_seen.add(next_cursor)
        cursor = next_cursor
    entries_bytes = _json_bytes(entries)
    duplicates_bytes = _json_bytes(duplicates)
    _immutable(roster / "entries.json", entries_bytes)
    _immutable(roster / "duplicates.json", duplicates_bytes)
    manifest = {**start, "status": "roster_complete", "ended_at": _now(), "entry_count": len(entries), "observed_positions": observed_position, "duplicate_observation_count": len(duplicates), "entries_sha256": _hash(entries_bytes), "duplicates_sha256": _hash(duplicates_bytes), "pages": pages}
    _immutable(roster / "manifest.json", _json_bytes(manifest))
    _write(roster / "progress.json", {"status": "roster_complete", "collected": len(entries), "pages": page_no, "duplicates": len(duplicates)})
    return manifest


def _verify_roster(root: Path) -> list[str]:
    errors = []
    roster = root / "roster"
    if not (roster / "manifest.json").exists():
        return ["The complete roster has not been sealed."]
    manifest = _read(roster / "manifest.json")
    for name, field in (("entries.json", "entries_sha256"), ("duplicates.json", "duplicates_sha256")):
        if not (roster / name).exists() or _hash((roster / name).read_bytes()) != manifest[field]:
            errors.append(f"Roster artifact hash differs: {name}")
    entries = _read(roster / "entries.json")
    if len(entries) != manifest["target_count"] or len({x["identity"] for x in entries}) != len(entries):
        errors.append("Roster count or identity uniqueness differs.")
    for page in manifest["pages"]:
        for path_field, hash_field in (("path", "sha256"), ("record_path", "record_sha256")):
            path = root / page[path_field]
            if not path.exists() or _hash(path.read_bytes()) != page[hash_field]:
                errors.append(f"Roster page evidence differs: {page[path_field]}")
    return errors


def _safe_path(value: str) -> str:
    if not isinstance(value, str) or not value or any(char in value for char in ('\\', '\x00', ':', '*', '?', '"', '<', '>', '|')):
        raise ValueError("Archive path is unsafe.")
    path = PurePosixPath(value)
    if path.is_absolute() or any(x in ("", ".", "..") for x in value.split("/")):
        raise ValueError("Archive path escapes or aliases the extraction root.")
    reserved = {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)), *(f"lpt{i}" for i in range(1, 10))}
    if any(x.rstrip(" .") != x or x.split(".")[0].lower() in reserved for x in path.parts):
        raise ValueError("Archive path is not safely representable on Windows.")
    return path.as_posix()


def _zip_files(blob: bytes, *, github_path: str | None = None) -> dict[str, bytes]:
    """Validate all entries before returning selected bytes; never follows symlinks."""
    result, seen, total = {}, set(), 0
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        if len(archive.infolist()) > MAX_FILES:
            raise ValueError("Archive exceeds the file count limit.")
        names = []
        for info in archive.infolist():
            raw = info.filename[:-1] if info.is_dir() else info.filename
            name = _safe_path(raw)
            folded = name.casefold()
            if folded in seen:
                raise ValueError("Archive contains duplicate or case-colliding paths.")
            seen.add(folded)
            if stat.S_ISLNK(info.external_attr >> 16) or info.flag_bits & 1:
                raise ValueError("Archive contains a symbolic link or encrypted entry.")
            total += info.file_size
            if info.file_size > MAX_FILE_BYTES or total > MAX_EXPANDED_BYTES:
                raise ValueError("Archive exceeds extraction byte limits.")
            names.append((info, name))
        prefix = None
        if github_path is not None:
            roots = {name.split("/")[0] for _, name in names}
            if len(roots) != 1:
                raise ValueError("GitHub archive does not have one repository root.")
            folder = "" if github_path in ("", ".") else _safe_path(github_path.strip("/"))
            prefix = next(iter(roots)) + "/" + (folder + "/" if folder else "")
        for info, name in names:
            if info.is_dir():
                continue
            if prefix is not None:
                if not name.startswith(prefix):
                    continue
                name = name[len(prefix):]
                if not name:
                    continue
            body = archive.read(info)
            if len(body) != info.file_size:
                raise ValueError("Archive file length differs from its directory entry.")
            result[name] = body
    if not result:
        raise ValueError("Archive contains no files at the selected source path.")
    return result


def github_content_hash(files: dict[str, bytes], *, root_folder: bool = False) -> str:
    """ClawHub folder digest; archive SHA-256 is a separate quantity.

    GitHub folder hash ordering is supplied by JS String.localeCompare in the
    registry. ASCII paths with ordinary punctuation are compared using the
    registry-compatible ICU collator when available; otherwise a mismatch is
    retained rather than accepting an unverified digest.
    """
    names = [name for name in files if not root_folder or "/" not in name]
    # This fixed script only sorts JSON strings. It never loads source code.
    node = shutil.which("node")
    if node:
        ordered = subprocess.run([node, "-e", "const fs=require('fs'); const a=JSON.parse(fs.readFileSync(0,'utf8')); a.sort((a,b)=>a.localeCompare(b)); process.stdout.write(JSON.stringify(a));"], input=json.dumps(names, ensure_ascii=False).encode("utf-8"), capture_output=True, timeout=30, check=True)
        names = json.loads(ordered.stdout)
    else:
        # A mismatch remains an acquisition failure; it is never waived.
        names.sort()
    lines = [f"{name}\0{len(files[name])}\0{_hash(files[name])}" for name in names]
    return _hash("\n".join(lines).encode("utf-8"))


def _slug_component(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", value)[:80]


def _item_dir(root: Path, entry: dict) -> Path:
    return root / "items" / f"{entry['rank']:04d}-{_slug_component(entry['ownerHandle'])}-{_slug_component(entry['slug'])}"


def _error_status(code: int) -> str:
    return "blocked_public_access" if code in (401, 403, 423) else "unavailable_pinned_source" if code in (404, 409, 410) else "http_failure"


def _source_view(root: Path, attempt: Path, files: dict[str, bytes], kind: str, verification: dict | None, *, recovered_source_paths: set[str] | None = None) -> dict:
    card = (verification or {}).get("card") or {}
    source_list = ((verification or {}).get("artifact") or {}).get("files")
    authoritative = {x["path"]: x for x in source_list or []}
    rows, unresolved = [], []
    for name, body in sorted(files.items()):
        provenance, include, reason = "source", True, "Preserved original source bytes."
        if name == "_meta.json" and name in (recovered_source_paths or set()):
            reason = "Exact-version stored source bytes recovered through the public file endpoint and verified against the original version manifest; the registry archive overlay is preserved separately."
        elif name == "_meta.json" and kind == "hosted":
            provenance, include, reason = "registry_generated", False, "ClawHub adds archive installation metadata; retained outside the analysis source view."
        elif name.casefold() == "skill-card.md" and kind == "hosted":
            if card.get("available") and card.get("sha256") == _hash(body) and card.get("size") == len(body):
                provenance, include, reason = "registry_generated", False, "Official version verification identifies this exact generated skill card."
            elif source_list is not None and name in authoritative and authoritative[name].get("sha256") == _hash(body):
                reason = "Official version verification includes this exact author-source file."
            else:
                provenance, include, reason = "unresolved_skill_card", False, "Generated versus author source provenance could not be established; candidate selection must resolve or exclude it."
                unresolved.append(name)
        rows.append({"path": name, "stored_path": (attempt / "files" / name).relative_to(root).as_posix(), "size": len(body), "sha256": _hash(body), "provenance": provenance, "include_in_source": include, "reason": reason})
    return {"schema": SCHEMA, "files": rows, "unresolved_provenance": unresolved, "source_file_count": sum(x["include_in_source"] for x in rows)}


def _acquire_one(root: Path, entry: dict, base_url: str, client: HTTPClient, *, retry_failed: bool) -> dict:
    item_dir = _item_dir(root, entry)
    attempts = item_dir / "attempts"
    previous = sorted(attempts.glob("*/result.json")) if attempts.exists() else []
    if previous:
        last = _read(previous[-1])
        if last["status"] == "complete_verified" or not retry_failed:
            return {"identity": entry["identity"], "rank": entry["rank"], "status": last["status"], "result_path": previous[-1].relative_to(root).as_posix(), "result_sha256": _hash(previous[-1].read_bytes()), "resumed": True}
    attempt = attempts / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "-" + uuid.uuid4().hex[:6])
    attempt.mkdir(parents=True)
    result = {"schema": SCHEMA, "identity": entry["identity"], "rank": entry["rank"], "version_pin": entry["version_pin"], "started_at": _now(), "status": "started", "entry_sha256": _hash(_json_bytes(entry)), "errors": []}
    _immutable(attempt / "entry.json", _json_bytes(entry))
    query = {"ownerHandle": entry["ownerHandle"]}
    path = "/api/v1/skills/" + quote(entry["slug"], safe="")
    try:
        # This endpoint only describes an installation; it does not install it.
        metadata_response = client.get(_url(base_url, path + "/install", **query), attempt / "requests", "source-resolution")
        _immutable(attempt / "metadata.json", metadata_response.body)
        if metadata_response.status != 200:
            result["status"] = _error_status(metadata_response.status)
            result["errors"].append(f"Public source resolution returned HTTP {metadata_response.status}.")
            return _finish(root, attempt, result)
        metadata = json.loads(metadata_response.body)
        install_kind = metadata.get("installKind") or (metadata.get("artifact") or {}).get("kind") or (metadata.get("install") or {}).get("kind")
        github = install_kind == "github" or metadata.get("sourceRef") == "public-github" or (metadata.get("source") or {}).get("sourceRef") == "public-github"
        result["source_resolution"] = metadata
        version_data, verification = None, None
        if not github and entry["version_pin"] is None:
            result["source_kind"] = "hosted"
            result["status"] = "unavailable_pinned_source"
            result["errors"].append("The frozen roster has no hosted version pin; no unversioned download request is permitted.")
            return _finish(root, attempt, result)
        if not github and entry["version_pin"] is not None:
            version_response = client.get(_url(base_url, path + "/versions/" + quote(entry["version_pin"], safe=""), **query), attempt / "requests", "version")
            _immutable(attempt / "version.json", version_response.body)
            if version_response.status != 200:
                result["status"] = _error_status(version_response.status)
                result["errors"].append(f"Frozen version metadata returned HTTP {version_response.status}; no latest-version fallback was attempted.")
                return _finish(root, attempt, result)
            version_data = json.loads(version_response.body).get("version")
            if not version_data or version_data.get("version") != entry["version_pin"]:
                raise ValueError("Version metadata does not match the frozen version pin.")
        response = client.get(_url(base_url, "/api/v1/download", slug=entry["slug"], ownerHandle=entry["ownerHandle"], version=None if github else entry["version_pin"]), attempt / "requests", "download")
        _immutable(attempt / "download.response", response.body)
        result["download_status"] = response.status
        result["download_sha256"] = _hash(response.body)
        if response.status != 200:
            result["status"] = _error_status(response.status)
            result["errors"].append(f"Pinned public download returned HTTP {response.status}.")
            return _finish(root, attempt, result)
        if response.body.lstrip().startswith(b"{"):
            descriptor = json.loads(response.body)
            _immutable(attempt / "descriptor.json", _json_bytes(descriptor))
            if descriptor.get("sourceRef") != "public-github":
                raise ValueError("Download JSON is not a supported public-github handoff descriptor.")
            repo, commit, folder, content_hash = (descriptor.get(k) for k in ("repo", "commit", "path", "contentHash"))
            if not isinstance(repo, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo) or not isinstance(commit, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", commit) or not isinstance(folder, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", str(content_hash)):
                raise ValueError("GitHub handoff is not pinned to a valid repository, exact commit, path, and content hash.")
            expected_url = f"https://api.github.com/repos/{repo}/zipball/{commit}"
            if descriptor.get("archiveUrl") != expected_url:
                raise ValueError("GitHub archive URL does not match the official pinned repository and commit.")
            resolved_github = metadata.get("github")
            if resolved_github and any(resolved_github.get(key) != descriptor.get(key) for key in ("repo", "commit", "path", "contentHash")):
                raise ValueError("GitHub download descriptor changed after public source resolution; no replacement commit was accepted.")
            result.update(source_kind="github", repo=repo, commit=commit, source_path=folder, content_hash=content_hash)
            archive_response = client.get(expected_url, attempt / "requests", "github-archive")
            _immutable(attempt / "github-source.zip", archive_response.body)
            if archive_response.status != 200:
                result["status"] = _error_status(archive_response.status)
                result["errors"].append(f"Pinned GitHub archive returned HTTP {archive_response.status}.")
                return _finish(root, attempt, result)
            files = _zip_files(archive_response.body, github_path=folder)
            computed = github_content_hash(files, root_folder=folder in ("", "."))
            result.update(archive_sha256=_hash(archive_response.body), computed_content_hash=computed)
            if computed.lower() != content_hash.lower():
                raise ValueError("GitHub source-folder content hash differs from the official descriptor; archive hash is not substituted.")
        else:
            result["source_kind"] = "hosted"
            result["archive_sha256"] = _hash(response.body)
            if entry["version_pin"] is None or version_data is None:
                raise ValueError("Hosted archive has no verified version pin; refusing an implicit latest download.")
            files = _zip_files(response.body)
            expected = {item["path"]: item for item in version_data["files"]}
            if set(files) - {"_meta.json"} != set(expected) - {"_meta.json"}:
                raise ValueError("Hosted archive file set differs from frozen version metadata.")
            for name, item in expected.items():
                if name not in files or len(files[name]) != item["size"] or _hash(files[name]) != item["sha256"]:
                    raise ValueError(f"Hosted file size or SHA-256 differs: {name}")
            verify_response = client.get(_url(base_url, path + "/verify", version=entry["version_pin"], **query), attempt / "requests", "provenance")
            _immutable(attempt / "verification.json", verify_response.body)
            if verify_response.status == 200:
                candidate = json.loads(verify_response.body)
                if candidate.get("version") == entry["version_pin"] and candidate.get("publisherHandle") == entry["ownerHandle"]:
                    verification = candidate
            result["provenance_response_status"] = verify_response.status
        for name, body in files.items():
            _immutable(attempt / "files" / name, body)
        view = _source_view(root, attempt, files, result["source_kind"], verification)
        _immutable(attempt / "source-view.json", _json_bytes(view))
        result.update(status="complete_verified", file_integrity="verified", source_view_path=(attempt / "source-view.json").relative_to(root).as_posix(), source_view_sha256=_hash(_json_bytes(view)), file_count=len(files), source_file_count=view["source_file_count"], unresolved_provenance=view["unresolved_provenance"])
    except (ValueError, KeyError, TypeError, zipfile.BadZipFile, json.JSONDecodeError, OSError, subprocess.SubprocessError) as error:
        result["status"] = "integrity_or_format_failure"
        result["errors"].append(f"{type(error).__name__}: {error}")
    return _finish(root, attempt, result)


def _finish(root: Path, attempt: Path, result: dict) -> dict:
    result["ended_at"] = _now()
    result["artifacts"] = [{"path": path.relative_to(root).as_posix(), "size": path.stat().st_size, "sha256": _hash(path.read_bytes())} for path in sorted(attempt.rglob("*")) if path.is_file() and path.name != "result.json"]
    _immutable(attempt / "result.json", _json_bytes(result))
    return {"identity": result["identity"], "rank": result["rank"], "status": result["status"], "result_path": (attempt / "result.json").relative_to(root).as_posix(), "result_sha256": _hash((attempt / "result.json").read_bytes()), "resumed": False}


def _collection_session(root: Path, operation: str, *, workers: int, retry_failed: bool = False, limit: int | None = None) -> tuple[Path, dict]:
    """Append invocation provenance without replacing previous session records."""
    session = root / "collection-sessions" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "-" + uuid.uuid4().hex[:6])
    index_path = root / "acquisition-index.json"
    previous = _read(index_path) if index_path.exists() else {}
    starts = []
    for row in previous.get("items", []):
        result_path = root / row["result_path"]
        if result_path.exists():
            value = _read(result_path).get("started_at")
            if value:
                starts.append(value)
    record = {"schema": SCHEMA, "operation": operation, "started_at": _now(), "workers": workers, "retry_failed": retry_failed, "limit": limit, "index_before_sha256": _hash(index_path.read_bytes()) if index_path.exists() else None, "index_before_started_at": previous.get("started_at"), "earliest_preserved_attempt_started_at": min(starts) if starts else None, "historical_session_limit": "Collection invocations predating this session log may only be timed from their retained attempt and roster records."}
    _immutable(session / "start.json", _json_bytes(record))
    return session, record


def _finish_collection_session(root: Path, session: Path, summary: dict) -> None:
    index = root / "acquisition-index.json"
    _immutable(session / "completion.json", _json_bytes({"schema": SCHEMA, "ended_at": _now(), "index_after_sha256": _hash(index.read_bytes()) if index.exists() else None, "attempted_count": summary.get("attempted_count"), "status_counts": summary.get("status_counts"), "verification_status": summary.get("status"), "verification_error_count": len(summary.get("errors", []))}))


def acquire_corpus(root: str | Path, workers: int = 4, *, base_url: str | None = None, client: HTTPClient | None = None, retry_failed: bool = False, limit: int | None = None) -> dict:
    """Retrieve only the sealed roster. Failed identities never receive substitutes."""
    root = Path(root)
    errors = _verify_roster(root)
    if errors:
        raise ValueError("Artifacts cannot be retrieved before a complete verified roster is sealed: " + "; ".join(errors))
    if not 1 <= workers <= 4:
        raise ValueError("Acquisition concurrency must be between one and four.")
    roster = _read(root / "roster" / "manifest.json")
    if base_url is not None and base_url.rstrip("/") != roster["base_url"]:
        raise ValueError("Artifact base URL differs from the frozen roster source.")
    base_url = roster["base_url"]
    entries = _read(root / "roster" / "entries.json")
    selected = entries if limit is None else entries[:limit]
    client = client or HTTPClient()
    results = {}
    old_index = root / "acquisition-index.json"
    previous_index = {}
    if old_index.exists():
        previous_index = _read(old_index)
        results = {x["identity"]: x for x in previous_index["items"]}
    session, session_record = _collection_session(root, "acquire_corpus", workers=workers, retry_failed=retry_failed, limit=limit)
    started = previous_index.get("started_at") or session_record["started_at"]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_acquire_one, root, entry, base_url, client, retry_failed=retry_failed): entry for entry in selected}
        for future in as_completed(futures):
            item = future.result()
            results[item["identity"]] = item
            ordered = [results[x["identity"]] for x in entries if x["identity"] in results]
            _write(old_index, {"schema": SCHEMA, "roster_sha256": _hash((root / "roster" / "manifest.json").read_bytes()), "started_at": started, "active_collection_session": (session / "start.json").relative_to(root).as_posix(), "updated_at": _now(), "planned_count": len(entries), "attempted_count": len(ordered), "items": ordered})
    summary = verify_corpus(root)
    _finish_collection_session(root, session, summary)
    return summary


def _prove_registry_meta_overlay(root: Path, entry: dict, row: dict) -> dict | None:
    """Offline eligibility proof; rejected cases trigger no alternate HTTP request."""
    result_path = root / row["result_path"]
    if row.get("result_sha256") and _hash(result_path.read_bytes()) != row["result_sha256"]:
        return None
    result = _read(result_path)
    if result.get("status") != "integrity_or_format_failure" or result.get("source_kind") != "hosted" or result.get("download_status") != 200 or result.get("version_pin") != entry["version_pin"] or result.get("entry_sha256") != _hash(_json_bytes(entry)):
        return None
    attempt = result_path.parent
    for artifact in result.get("artifacts", []):
        stored = root / artifact["path"]
        if not stored.exists() or stored.stat().st_size != artifact["size"] or _hash(stored.read_bytes()) != artifact["sha256"]:
            return None
    try:
        version = _read(attempt / "version.json")["version"]
        if not entry["version_pin"] or version["version"] != entry["version_pin"]:
            return None
        raw_zip = (attempt / "download.response").read_bytes()
        if _hash(raw_zip) != result.get("download_sha256") or _hash(raw_zip) != result.get("archive_sha256"):
            return None
        files = _zip_files(raw_zip)
        expected = {item["path"]: item for item in version["files"]}
        if len(expected) != len(version["files"]) or set(files) != set(expected) or "_meta.json" not in expected:
            return None
        mismatches = [name for name, item in expected.items() if len(files[name]) != item["size"] or _hash(files[name]) != item["sha256"]]
        if mismatches != ["_meta.json"]:
            return None
        overlay = json.loads(files["_meta.json"])
        if set(overlay) != {"ownerId", "slug", "version", "publishedAt"} or overlay["slug"] != entry["slug"] or overlay["version"] != entry["version_pin"] or not isinstance(overlay["ownerId"], str) or not overlay["ownerId"] or not isinstance(overlay["publishedAt"], (int, float)):
            return None
        return {"prior_result": result, "prior_result_path": row["result_path"], "prior_result_sha256": _hash(result_path.read_bytes()), "version": version, "files": files, "raw_zip": raw_zip, "registry_overlay": overlay, "mismatches": mismatches}
    except (KeyError, TypeError, ValueError, OSError, zipfile.BadZipFile):
        return None


def _recover_registry_meta_one(root: Path, entry: dict, proof: dict, base_url: str, client: HTTPClient) -> dict:
    attempt = _item_dir(root, entry) / "attempts" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "-meta-recovery-" + uuid.uuid4().hex[:6])
    attempt.mkdir(parents=True)
    previous = proof["prior_result"]
    result = {"schema": SCHEMA, "identity": entry["identity"], "rank": entry["rank"], "version_pin": entry["version_pin"], "started_at": _now(), "status": "started", "source_kind": "hosted", "entry_sha256": _hash(_json_bytes(entry)), "download_status": 200, "download_sha256": previous["download_sha256"], "archive_sha256": previous["archive_sha256"], "source_resolution": previous.get("source_resolution"), "recovery_kind": "exact_version_registry_meta_overlay", "recovered_from_result_path": proof["prior_result_path"], "recovered_from_result_sha256": proof["prior_result_sha256"], "errors": []}
    _immutable(attempt / "entry.json", _json_bytes(entry))
    _immutable(attempt / "download.response", proof["raw_zip"])
    prior_attempt = (root / proof["prior_result_path"]).parent
    _immutable(attempt / "version.json", (prior_attempt / "version.json").read_bytes())
    _immutable(attempt / "archive-files" / "_meta.json", proof["files"]["_meta.json"])
    _immutable(attempt / "recovery-proof.json", _json_bytes({"schema": SCHEMA, "prior_result_path": proof["prior_result_path"], "prior_result_sha256": proof["prior_result_sha256"], "public_archive_http_status": 200, "mismatching_paths": proof["mismatches"], "all_other_manifest_files_verified": True, "registry_overlay": proof["registry_overlay"], "registry_overlay_sha256": _hash(proof["files"]["_meta.json"]), "registry_implementation_reference": "https://github.com/openclaw/clawhub/blob/main/convex/downloads.ts", "scope": "Recover the one overwritten stored source file only; no blocked archive, alternative version, new rank, or unverified replacement is permitted."}))
    try:
        path = "/api/v1/skills/" + quote(entry["slug"], safe="")
        response = client.get(_url(base_url, path + "/file", path="_meta.json", version=entry["version_pin"], ownerHandle=entry["ownerHandle"]), attempt / "requests", "recover-original-meta")
        _immutable(attempt / "recovered-original-meta.response", response.body)
        result["recovery_file_http_status"] = response.status
        if response.status != 200:
            result["status"] = _error_status(response.status)
            result["errors"].append(f"Exact-version public source-file recovery returned HTTP {response.status}; no alternate endpoint or version was attempted.")
            return _finish(root, attempt, result)
        expected = next(item for item in proof["version"]["files"] if item["path"] == "_meta.json")
        if len(response.body) != expected["size"] or _hash(response.body) != expected["sha256"]:
            raise ValueError("Recovered original _meta.json does not match the frozen exact-version source size and SHA-256.")
        files = {**proof["files"], "_meta.json": response.body}
        verification = None
        if any(name.casefold() == "skill-card.md" for name in files):
            verified = client.get(_url(base_url, path + "/verify", version=entry["version_pin"], ownerHandle=entry["ownerHandle"]), attempt / "requests", "recovered-source-provenance")
            _immutable(attempt / "verification.json", verified.body)
            result["provenance_response_status"] = verified.status
            if verified.status == 200:
                candidate = json.loads(verified.body)
                if candidate.get("version") == entry["version_pin"] and candidate.get("publisherHandle") == entry["ownerHandle"]:
                    verification = candidate
        for name, blob in files.items():
            _immutable(attempt / "files" / name, blob)
        view = _source_view(root, attempt, files, "hosted", verification, recovered_source_paths={"_meta.json"})
        _immutable(attempt / "source-view.json", _json_bytes(view))
        result.update(status="complete_verified", file_integrity="verified", source_view_path=(attempt / "source-view.json").relative_to(root).as_posix(), source_view_sha256=_hash(_json_bytes(view)), file_count=len(files), source_file_count=view["source_file_count"], unresolved_provenance=view["unresolved_provenance"], recovered_source_sha256=expected["sha256"], recovered_source_size=expected["size"])
    except (ValueError, KeyError, TypeError, OSError) as error:
        result["status"] = "integrity_or_format_failure"
        result["errors"].append(f"{type(error).__name__}: {error}")
    return _finish(root, attempt, result)


def recover_registry_meta_overlays(root: str | Path, workers: int = 4, *, client: HTTPClient | None = None, limit: int | None = None) -> dict:
    """Opt-in recovery after the original complete roster has been attempted.

    The caller must wait until its acquisition process has stopped. Every
    eligibility check is offline, and blocked ZIPs are never recovered through
    file endpoints. Existing failed attempts remain immutable.
    """
    root = Path(root)
    errors = _verify_roster(root)
    if errors:
        raise ValueError("Registry overlay recovery requires a verified frozen roster: " + "; ".join(errors))
    if not 1 <= workers <= 4:
        raise ValueError("Recovery concurrency must be between one and four.")
    entries = _read(root / "roster" / "entries.json")
    index_path = root / "acquisition-index.json"
    index = _read(index_path)
    indexed = {row["identity"]: row for row in index["items"]}
    if set(indexed) != {entry["identity"] for entry in entries}:
        raise ValueError("Registry overlay recovery cannot begin before every frozen roster identity has an acquisition result.")
    eligible = []
    for entry in entries:
        proof = _prove_registry_meta_overlay(root, entry, indexed[entry["identity"]])
        if proof is not None:
            eligible.append((entry, proof))
    selected = eligible if limit is None else eligible[:limit]
    session, record = _collection_session(root, "recover_registry_meta_overlays", workers=workers, limit=limit)
    _immutable(session / "eligibility.json", _json_bytes({"eligible_count": len(eligible), "selected_count": len(selected), "skipped_count": len(entries) - len(eligible), "selected": [{"identity": entry["identity"], "rank": entry["rank"], "prior_result_path": proof["prior_result_path"], "prior_result_sha256": proof["prior_result_sha256"]} for entry, proof in selected]}))
    client = client or HTTPClient()
    base_url = _read(root / "roster" / "manifest.json")["base_url"]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(_recover_registry_meta_one, root, entry, proof, base_url, client) for entry, proof in selected]
        for future in as_completed(futures):
            row = future.result()
            indexed[row["identity"]] = row
            updated = {**index, "started_at": index.get("started_at") or record["started_at"], "updated_at": _now(), "active_collection_session": (session / "start.json").relative_to(root).as_posix(), "items": [indexed[entry["identity"]] for entry in entries]}
            _write(index_path, updated)
    summary = verify_corpus(root)
    summary["recovery"] = {"eligible_count": len(eligible), "attempted_count": len(selected), "skipped_count": len(entries) - len(eligible), "session_path": session.relative_to(root).as_posix()}
    _finish_collection_session(root, session, summary)
    return summary


def verify_corpus(root: str | Path) -> dict:
    """Offline validation; no network, skill execution, or model calls."""
    root = Path(root)
    errors = _verify_roster(root)
    rows, counts, missing = [], {}, []
    if not errors:
        entries = _read(root / "roster" / "entries.json")
        index = _read(root / "acquisition-index.json") if (root / "acquisition-index.json").exists() else {"items": []}
        indexed = {row["identity"]: row for row in index["items"]}
        for entry in entries:
            row = indexed.get(entry["identity"])
            if row is None:
                missing.append(entry["identity"])
                continue
            result_path = root / row["result_path"]
            if row.get("result_sha256") and _hash(result_path.read_bytes()) != row["result_sha256"]:
                errors.append(f"Acquisition result hash differs: {entry['identity']}")
            result = _read(result_path)
            if result.get("recovery_kind") == "exact_version_registry_meta_overlay":
                prior_path = root / result["recovered_from_result_path"]
                if not prior_path.exists() or _hash(prior_path.read_bytes()) != result["recovered_from_result_sha256"]:
                    errors.append(f"Original failed recovery evidence differs: {entry['identity']}")
            for artifact in result.get("artifacts", []):
                stored = root / artifact["path"]
                if not stored.exists() or stored.stat().st_size != artifact["size"] or _hash(stored.read_bytes()) != artifact["sha256"]:
                    errors.append(f"Acquisition evidence differs: {artifact['path']}")
            counts[result["status"]] = counts.get(result["status"], 0) + 1
            if result["identity"] != entry["identity"] or result["entry_sha256"] != _hash(_json_bytes(entry)):
                errors.append(f"Acquired entry identity differs: {entry['identity']}")
            if result["status"] == "complete_verified":
                view_path = root / result["source_view_path"]
                if not view_path.exists() or _hash(view_path.read_bytes()) != result["source_view_sha256"]:
                    errors.append(f"Source-view hash differs: {entry['identity']}")
                    continue
                view = _read(view_path)
                for file in view["files"]:
                    stored = root / file["stored_path"]
                    if not stored.exists() or stored.stat().st_size != file["size"] or _hash(stored.read_bytes()) != file["sha256"]:
                        errors.append(f"Preserved source bytes differ: {entry['identity']}/{file['path']}")
                archive_path = result_path.parent / ("github-source.zip" if result["source_kind"] == "github" else "download.response")
                if not archive_path.exists() or _hash(archive_path.read_bytes()) != result["archive_sha256"]:
                    errors.append(f"Archive SHA-256 differs: {entry['identity']}")
            rows.append({"identity": entry["identity"], "rank": entry["rank"], "status": result["status"], "errors": result.get("errors", []), "unresolved_provenance": result.get("unresolved_provenance", [])})
    return {"schema": SCHEMA, "verified_at": _now(), "status": "verified" if not errors else "verification_failed", "roster_count": len(rows) + len(missing), "attempted_count": len(rows), "not_attempted_count": len(missing), "not_attempted": missing, "status_counts": counts, "errors": errors, "items": rows, "model_calls": 0, "skill_installations": 0, "skill_executions": 0}
