"""Acquisition tests use synthetic HTTP data and never execute downloaded code."""
import hashlib
import io
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import zipfile

import pytest

from tools.doe.real_comparison import acquisition as acq


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def response(value, status=200, headers=None):
    body = value if isinstance(value, bytes) else json.dumps(value, ensure_ascii=False).encode()
    return acq.HTTPResponse(status, headers or {}, body)


def item(owner="author", slug="sample", version="1.0.0"):
    return {"ownerHandle": owner, "slug": slug, "latestVersion": {"version": version} if version else None, "stats": {"downloads": 20}}


def zipped(files):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        for name, blob in files.items():
            archive.writestr(name, blob)
    return stream.getvalue()


def client(transport):
    return acq.HTTPClient(transport, sleep=lambda _: None)


def seal(tmp_path, items=None):
    items = items or [item()]
    return acq.collect_roster(tmp_path, len(items), client=client(lambda _: response({"items": items, "nextCursor": None})))


def hosted_transport(files=None, *, wrong_hash=False, blocked=False):
    files = files or {"SKILL.md": "Read 用户资料 and return the requested summary.\n".encode(), "skill-card.md": b"Generated registry analysis."}
    calls = []

    def fetch(url):
        calls.append(url)
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        assert query["ownerHandle"] == ["author"]
        if parsed.path.endswith("/install"):
            return response({"ok": True, "slug": "sample", "installKind": "archive", "archive": {"version": "2.0.0"}})
        if "/versions/" in parsed.path:
            assert parsed.path.endswith("/1.0.0")
            if blocked:
                return response(b"Version no longer available", status=410)
            return response({"version": {"version": "1.0.0", "files": [{"path": name, "size": len(blob), "sha256": "0" * 64 if wrong_hash else digest(blob)} for name, blob in files.items()]}})
        if parsed.path.endswith("/download"):
            assert query["version"] == ["1.0.0"]
            return response(zipped({**files, "_meta.json": b'{"slug":"sample","version":"1.0.0"}'}))
        if parsed.path.endswith("/verify"):
            return response({"version": "1.0.0", "publisherHandle": "author", "card": {"available": True, "sha256": digest(files["skill-card.md"]), "size": len(files["skill-card.md"])}, "artifact": {"files": [{"path": "SKILL.md", "sha256": digest(files["SKILL.md"])}]}})
        raise AssertionError(url)

    return fetch, calls


def test_roster_first_seen_order_owner_identity_and_duplicate_traversal(tmp_path):
    pages = [{"items": [item("a", "same"), item("b", "same")], "nextCursor": "cursor1"}, {"items": [item("b", "same"), item("c", "third")], "nextCursor": "cursor2"}]
    calls = []

    def fetch(url):
        calls.append(url)
        return response(pages[len(calls) - 1])

    result = acq.collect_roster(tmp_path, 3, client=client(fetch), page_size=2)
    entries = json.loads((tmp_path / "roster/entries.json").read_text())
    assert [x["identity"] for x in entries] == ["a/same", "b/same", "c/third"]
    assert result["duplicate_observation_count"] == 1
    assert result["observed_positions"] == 4
    assert entries[-1]["observed_position"] == 4
    assert all("sort=downloads" in url and "nonSuspicious" not in url for url in calls)
    assert acq.collect_roster(tmp_path, 3, client=client(lambda _: pytest.fail("Frozen roster fetched again"))) == result


def test_roster_is_required_before_any_artifact_download(tmp_path):
    with pytest.raises(ValueError, match="before a complete verified roster"):
        acq.acquire_corpus(tmp_path, client=client(lambda _: pytest.fail("Unsealed artifact retrieval")))


def test_roster_mutation_is_rejected(tmp_path):
    seal(tmp_path)
    (tmp_path / "roster/entries.json").write_text("[]")
    with pytest.raises(ValueError, match="verification"):
        acq.collect_roster(tmp_path, 1)


def test_hosted_preserves_original_language_and_generated_metadata_separation(tmp_path):
    seal(tmp_path)
    fetch, calls = hosted_transport()
    result = acq.acquire_corpus(tmp_path, workers=1, client=client(fetch))
    assert result["status_counts"] == {"complete_verified": 1}
    index = json.loads((tmp_path / "acquisition-index.json").read_text())
    output = json.loads((tmp_path / index["items"][0]["result_path"]).read_text())
    view = json.loads((tmp_path / output["source_view_path"]).read_text())
    assert [x["path"] for x in view["files"] if x["include_in_source"]] == ["SKILL.md"]
    skill = next(x for x in view["files"] if x["path"] == "SKILL.md")
    assert "用户资料" in (tmp_path / skill["stored_path"]).read_text(encoding="utf-8")
    assert {x["path"] for x in view["files"] if x["provenance"] == "registry_generated"} == {"_meta.json", "skill-card.md"}
    assert output["version_pin"] == "1.0.0"
    assert "2.0.0" not in " ".join(calls)


def test_resume_never_replaces_a_successful_archive_and_detects_tampering(tmp_path):
    seal(tmp_path)
    fetch, _ = hosted_transport()
    acq.acquire_corpus(tmp_path, workers=1, client=client(fetch))
    result = acq.acquire_corpus(tmp_path, workers=1, client=client(lambda _: pytest.fail("Successful entry downloaded again")))
    assert result["status"] == "verified"
    source = next(tmp_path.glob("items/*/attempts/*/files/SKILL.md"))
    source.write_bytes(b"changed")
    assert acq.verify_corpus(tmp_path)["status"] == "verification_failed"


def test_pinned_version_failure_does_not_fallback_or_replace_identity(tmp_path):
    seal(tmp_path)
    fetch, calls = hosted_transport(blocked=True)
    result = acq.acquire_corpus(tmp_path, workers=1, client=client(fetch))
    assert result["status_counts"] == {"unavailable_pinned_source": 1}
    assert not any("/download?" in url for url in calls)
    assert result["roster_count"] == 1


def test_hash_mismatch_is_retained_as_failure(tmp_path):
    seal(tmp_path)
    fetch, _ = hosted_transport(wrong_hash=True)
    result = acq.acquire_corpus(tmp_path, workers=1, client=client(fetch))
    assert result["status_counts"] == {"integrity_or_format_failure": 1}
    assert next(tmp_path.glob("items/*/attempts/*/download.response")).exists()
    assert not list(tmp_path.glob("items/*/attempts/*/source-view.json"))


@pytest.mark.parametrize("name", ["../escape", "/absolute", "folder\\evil", "file:stream", "CON.txt", "x/../evil", "bad. ", "question?"])
def test_unsafe_archive_paths_are_rejected_before_extraction(name):
    with pytest.raises(ValueError, match="Archive path"):
        acq._safe_path(name)
    # Python's Windows ZIP writer normalizes backslashes itself.
    if "\\" not in name:
        with pytest.raises(ValueError, match="Archive path"):
            acq._zip_files(zipped({name: b"untrusted"}))


def test_archive_case_collisions_and_links_are_rejected():
    with pytest.raises(ValueError, match="case-colliding"):
        acq._zip_files(zipped({"SKILL.md": b"a", "skill.md": b"b"}))
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        info = zipfile.ZipInfo("link")
        info.create_system = 3
        info.external_attr = 0o120777 << 16
        archive.writestr(info, "../../outside")
    with pytest.raises(ValueError, match="symbolic link"):
        acq._zip_files(stream.getvalue())


def test_github_descriptor_and_content_hash_are_distinct_from_zip_hash(tmp_path):
    seal(tmp_path, [item(version=None)])
    files = {"SKILL.md": b"# Real source", "scripts/run.py": b"print('never executed')"}
    commit = "a" * 40
    descriptor = {"sourceRef": "public-github", "repo": "owner/repo", "path": "skills/sample", "commit": commit, "contentHash": acq.github_content_hash(files), "archiveUrl": f"https://api.github.com/repos/owner/repo/zipball/{commit}"}
    archive = zipped({"repo-abcdef/skills/sample/" + name: blob for name, blob in files.items()})

    def fetch(url):
        if "/install?" in url:
            return response({"ok": True, "installKind": "github", "github": {key: descriptor[key] for key in ("repo", "path", "commit", "contentHash")}})
        if "/download?" in url:
            assert "version=" not in url
            return response(descriptor)
        assert url == descriptor["archiveUrl"]
        return response(archive)

    result = acq.acquire_corpus(tmp_path, workers=1, client=client(fetch))
    assert result["status_counts"] == {"complete_verified": 1}
    output = json.loads(next(tmp_path.glob("items/*/attempts/*/result.json")).read_text())
    assert output["content_hash"] == descriptor["contentHash"]
    assert output["archive_sha256"] == digest(archive)
    assert output["archive_sha256"] != output["content_hash"]
    assert output["computed_content_hash"] == output["content_hash"]


def test_http_retry_after_is_honored_and_all_receipts_are_preserved(tmp_path):
    calls, delays = [], []

    def fetch(url):
        calls.append(url)
        return response(b"rate limited", status=429, headers={"Retry-After": "7"}) if len(calls) == 1 else response({"ok": True})

    http = acq.HTTPClient(fetch, sleep=delays.append)
    assert http.get("https://example.test", tmp_path, "query").status == 200
    assert any(delay >= 7 for delay in delays)
    assert len(list(tmp_path.glob("*.body"))) == 2
    calls.clear()
    bounded = acq.HTTPClient(lambda _: response(b"wait", status=429, headers={"Retry-After": "1000"}), sleep=lambda _: pytest.fail("Server retry delay must not be shortened"))
    assert bounded.get("https://example.test", tmp_path, "bounded").status == 429


def test_source_card_without_provenance_is_not_silently_author_source(tmp_path):
    files = {"SKILL.md": b"source", "skill-card.md": b"unknown origin"}
    view = acq._source_view(tmp_path, tmp_path / "attempt", files, "hosted", None)
    assert view["unresolved_provenance"] == ["skill-card.md"]
    assert not next(x for x in view["files"] if x["path"] == "skill-card.md")["include_in_source"]


def test_missing_hosted_pin_stops_before_any_unversioned_archive_request(tmp_path):
    seal(tmp_path, [item(version=None)])
    calls = []

    def fetch(url):
        calls.append(url)
        assert urlparse(url).path.endswith("/install"), "No latest archive or version lookup is permitted"
        return response({"ok": True, "installKind": "archive", "archive": {"version": "newest"}})

    result = acq.acquire_corpus(tmp_path, workers=1, client=client(fetch))
    assert len(calls) == 1
    assert result["status_counts"] == {"unavailable_pinned_source": 1}
    assert not list(tmp_path.glob("items/*/attempts/*/download.response"))


def prepare_meta_overlay_failure(tmp_path, *, other_mismatch=False, overlay_version="1.0.0", blocked=False):
    seal(tmp_path)
    original_meta = b'{"source_setting":"preserve this original source"}\n'
    files = {"SKILL.md": b"# Source\nRead the stored source setting.\n", "_meta.json": original_meta}
    overlay = json.dumps({"ownerId": "public-owner-id", "slug": "sample", "version": overlay_version, "publishedAt": 12345}).encode()

    def fetch(url):
        parsed = urlparse(url)
        if parsed.path.endswith("/install"):
            return response({"ok": True, "slug": "sample", "installKind": "archive", "archive": {"version": "1.0.0"}})
        if "/versions/" in parsed.path:
            return response({"version": {"version": "1.0.0", "files": [{"path": name, "size": len(blob), "sha256": digest(blob)} for name, blob in files.items()]}})
        if parsed.path.endswith("/download"):
            if blocked:
                return response(b"Public download blocked", status=403)
            return response(zipped({**files, "_meta.json": overlay, **({"SKILL.md": b"Unexpected changed source"} if other_mismatch else {})}))
        raise AssertionError(url)

    acq.acquire_corpus(tmp_path, workers=1, client=client(fetch))
    index = json.loads((tmp_path / "acquisition-index.json").read_text())
    prior = tmp_path / index["items"][0]["result_path"]
    return original_meta, prior


def test_meta_overlay_recovery_preserves_failure_zip_and_original_source_hash(tmp_path):
    original_meta, prior = prepare_meta_overlay_failure(tmp_path)
    prior_bytes = prior.read_bytes()
    archive_bytes = (prior.parent / "download.response").read_bytes()
    calls = []

    def fetch(url):
        calls.append(url)
        parsed = urlparse(url)
        assert parsed.path.endswith("/file")
        assert parse_qs(parsed.query) == {"ownerHandle": ["author"], "version": ["1.0.0"], "path": ["_meta.json"]}
        return response(original_meta)

    summary = acq.recover_registry_meta_overlays(tmp_path, workers=1, client=client(fetch))
    assert summary["status"] == "verified"
    assert summary["status_counts"] == {"complete_verified": 1}
    assert len(calls) == 1
    assert prior.read_bytes() == prior_bytes
    index = json.loads((tmp_path / "acquisition-index.json").read_text())
    result_path = tmp_path / index["items"][0]["result_path"]
    result = json.loads(result_path.read_text())
    assert result["recovery_kind"] == "exact_version_registry_meta_overlay"
    assert result["recovered_from_result_path"] == prior.relative_to(tmp_path).as_posix()
    assert (result_path.parent / "download.response").read_bytes() == archive_bytes
    assert (result_path.parent / "files/_meta.json").read_bytes() == original_meta
    assert (result_path.parent / "archive-files/_meta.json").read_bytes() != original_meta
    view = json.loads((tmp_path / result["source_view_path"]).read_text())
    meta = next(x for x in view["files"] if x["path"] == "_meta.json")
    assert meta["include_in_source"] and meta["provenance"] == "source"
    assert meta["sha256"] == digest(original_meta)
    repeated = acq.recover_registry_meta_overlays(tmp_path, workers=1, client=client(lambda _: pytest.fail("Successful recovery fetched again")))
    assert repeated["recovery"]["attempted_count"] == 0


@pytest.mark.parametrize("options", [{"blocked": True}, {"other_mismatch": True}, {"overlay_version": "2.0.0"}])
def test_meta_recovery_does_not_bypass_blocks_or_accept_other_mismatches(tmp_path, options):
    _, prior = prepare_meta_overlay_failure(tmp_path, **options)
    before = prior.read_bytes()
    summary = acq.recover_registry_meta_overlays(tmp_path, workers=1, client=client(lambda _: pytest.fail("Ineligible recovery issued a network request")))
    assert summary["recovery"]["attempted_count"] == 0
    assert prior.read_bytes() == before


def test_meta_recovery_rejects_wrong_exact_version_file_bytes(tmp_path):
    _, prior = prepare_meta_overlay_failure(tmp_path)
    before = prior.read_bytes()
    summary = acq.recover_registry_meta_overlays(tmp_path, workers=1, client=client(lambda _: response(b"Wrong stored source")))
    assert summary["status_counts"] == {"integrity_or_format_failure": 1}
    assert prior.read_bytes() == before
    newest = sorted(tmp_path.glob("items/*/attempts/*/result.json"))[-1]
    assert "does not match" in json.loads(newest.read_text())["errors"][0]


def test_recovery_replay_checks_original_failed_attempt_identity(tmp_path):
    original_meta, prior = prepare_meta_overlay_failure(tmp_path)
    acq.recover_registry_meta_overlays(tmp_path, workers=1, client=client(lambda _: response(original_meta)))
    prior.write_bytes(prior.read_bytes() + b" ")
    summary = acq.verify_corpus(tmp_path)
    assert summary["status"] == "verification_failed"
    assert any("Original failed recovery evidence" in message for message in summary["errors"])


def test_meta_recovery_waits_for_all_roster_acquisitions(tmp_path):
    seal(tmp_path, [item(), item("other", "second")])
    fetch, _ = hosted_transport()
    acq.acquire_corpus(tmp_path, workers=1, limit=1, client=client(fetch))
    with pytest.raises(ValueError, match="before every frozen roster"):
        acq.recover_registry_meta_overlays(tmp_path, workers=1, client=client(lambda _: pytest.fail("Incomplete corpus recovery")))


def test_collection_resume_keeps_started_at_and_appends_immutable_sessions(tmp_path):
    seal(tmp_path)
    fetch, _ = hosted_transport()
    acq.acquire_corpus(tmp_path, workers=1, client=client(fetch))
    first_index = json.loads((tmp_path / "acquisition-index.json").read_text())
    evidence = {path: path.read_bytes() for path in (tmp_path / "collection-sessions").rglob("*.json")}
    acq.acquire_corpus(tmp_path, workers=1, client=client(lambda _: pytest.fail("Resume reissued network requests")))
    resumed_index = json.loads((tmp_path / "acquisition-index.json").read_text())
    assert resumed_index["started_at"] == first_index["started_at"]
    assert resumed_index["active_collection_session"] != first_index["active_collection_session"]
    assert len(list((tmp_path / "collection-sessions").glob("*/start.json"))) == 2
    assert len(list((tmp_path / "collection-sessions").glob("*/completion.json"))) == 2
    assert all(path.read_bytes() == blob for path, blob in evidence.items())
