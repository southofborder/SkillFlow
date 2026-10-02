"""Local persistence retries never need or masquerade as a remote call."""

from __future__ import annotations

import errno
import hashlib
import os
from pathlib import Path

import pytest

import skill_ir.artifact_io as artifact_io
from skill_ir.artifact_io import ArtifactWriteError, atomic_write_text
from skill_ir.experiments.report import ArtifactWriter
from skill_ir.llm.config import LlmClientError


def windows_error(code):
    error = PermissionError(errno.EACCES, "synthetic local sharing error")
    error.winerror = code
    return error


def test_exact_utf8_text_replaces_old_file_and_leaves_no_temporary(tmp_path):
    target = tmp_path / "nested" / "report.md"
    value = '中文 "引文"\nsecond\r\n\\tail\x00'
    atomic_write_text(target, "old")
    atomic_write_text(target, value)
    assert target.read_bytes() == value.encode("utf-8")
    assert list(target.parent.glob(".*.tmp")) == []


@pytest.mark.parametrize("code", [5, 32, 33])
def test_temporary_sharing_failure_retries_same_closed_complete_file(tmp_path, monkeypatch, code):
    target = tmp_path / "state.json"
    target.write_bytes(b"old")
    payload = "完整新快照\n"
    original_replace = artifact_io.os.replace
    attempts, sleeps = [], []

    def replace(source, destination):
        attempts.append((source, destination, source.read_bytes()))
        # Re-opening in exclusive append mode verifies the writer is closed on
        # Windows before the replacement retry starts.
        with source.open("ab"):
            pass
        if len(attempts) <= 2:
            assert target.read_bytes() == b"old"
            raise windows_error(code)
        original_replace(source, destination)

    monkeypatch.setattr(artifact_io.os, "replace", replace)
    monkeypatch.setattr(artifact_io, "sleep", sleeps.append)
    atomic_write_text(target, payload)
    assert len(attempts) == 3
    assert len({attempt[0] for attempt in attempts}) == 1
    assert all(attempt[2] == payload.encode("utf-8") for attempt in attempts)
    assert sleeps == [0.05, 0.1]
    assert target.read_bytes() == payload.encode("utf-8")
    assert not attempts[0][0].exists()


def test_persistent_sharing_failure_retains_redacted_complete_snapshot(tmp_path, monkeypatch):
    target = tmp_path / "response.json"
    target.write_bytes(b"previous accepted record")
    original_error = windows_error(32)
    attempts, delays = [], []

    def fail_replace(source, destination):
        attempts.append(source)
        raise original_error

    monkeypatch.setattr(artifact_io.os, "replace", fail_replace)
    monkeypatch.setattr(artifact_io, "sleep", delays.append)
    with pytest.raises(ArtifactWriteError) as raised:
        ArtifactWriter(("private-test-key",)).text(target, 'accepted: private-test-key\n中文')
    error = raised.value
    assert not isinstance(error, (OSError, LlmClientError))
    assert error.__cause__ is original_error
    assert error.stage == "replace" and error.path == target
    assert error.attempts == 7
    assert len(set(attempts)) == 1 and len(attempts) == 7
    assert len(delays) == 6 and sum(delays) < 3
    assert error.snapshot_complete is True
    assert error.temporary_path == attempts[0]
    expected = 'accepted: [REDACTED]\n中文'.encode("utf-8")
    assert error.temporary_path.read_bytes() == expected
    assert error.snapshot_sha256 == hashlib.sha256(expected).hexdigest()
    assert error.cleanup_error is None
    assert error.cause_type == "PermissionError" and error.winerror == 32 and error.errno == errno.EACCES
    assert "winerror=32" in str(error) and "PermissionError" in str(error)
    assert "private-test-key" not in str(error)
    assert "replace" in str(error) and str(error.temporary_path) in str(error)
    assert error.snapshot_sha256 in str(error)
    assert target.read_bytes() == b"previous accepted record"


@pytest.mark.parametrize("error", [
    PermissionError(errno.EACCES, "no Windows sharing classification"),
    OSError(errno.ENOSPC, "disk full"), windows_error(2), RuntimeError("replace callback bug"),
])
def test_unrelated_replace_errors_are_not_retried(tmp_path, monkeypatch, error):
    target = tmp_path / "record.txt"
    target.write_text("old", encoding="utf-8")
    calls = []

    def fail_replace(*args):
        calls.append(args)
        raise error

    monkeypatch.setattr(artifact_io.os, "replace", fail_replace)
    monkeypatch.setattr(artifact_io, "sleep", lambda _: pytest.fail("unrelated error was retried"))
    with pytest.raises(ArtifactWriteError) as raised:
        atomic_write_text(target, "new")
    assert len(calls) == 1 and raised.value.attempts == 1
    assert raised.value.__cause__ is error
    assert raised.value.snapshot_complete
    assert raised.value.temporary_path.read_text(encoding="utf-8") == "new"
    assert target.read_text(encoding="utf-8") == "old"


def test_mkdir_failure_has_no_certified_snapshot_and_preserves_cause(tmp_path, monkeypatch):
    target = tmp_path / "missing" / "record.txt"
    original_error = PermissionError("mkdir blocked")

    def fail_mkdir(*args, **kwargs):
        raise original_error

    monkeypatch.setattr(Path, "mkdir", fail_mkdir)
    with pytest.raises(ArtifactWriteError) as raised:
        atomic_write_text(target, "data")
    assert raised.value.stage == "mkdir"
    assert raised.value.__cause__ is original_error
    assert raised.value.temporary_path is None
    assert raised.value.snapshot_complete is False
    assert raised.value.snapshot_sha256 is None
    assert raised.value.attempts == 0


@pytest.mark.parametrize("cleanup_fails", [False, True])
@pytest.mark.parametrize("short_write", [False, True])
def test_partial_write_never_claims_complete_snapshot_or_loses_original_error(
    tmp_path, monkeypatch, cleanup_fails, short_write,
):
    target = tmp_path / "record.txt"
    target.write_bytes(b"old")
    original_open, original_unlink = Path.open, Path.unlink
    original_error = OSError(errno.ENOSPC, "write failed halfway")
    cleanup_error = PermissionError("cleanup blocked")

    class BrokenStream:
        def __init__(self, path):
            self.stream = original_open(path, "xb")

        def __enter__(self):
            return self

        def write(self, payload):
            self.stream.write(payload[:3])
            if short_write:
                return 3
            raise original_error

        def __exit__(self, *args):
            self.stream.close()

    def open_file(path, mode="r", *args, **kwargs):
        if mode == "xb" and path.suffix == ".tmp":
            return BrokenStream(path)
        return original_open(path, mode, *args, **kwargs)

    def unlink_file(path, *args, **kwargs):
        if path.suffix == ".tmp" and cleanup_fails:
            raise cleanup_error
        return original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", open_file)
    monkeypatch.setattr(Path, "unlink", unlink_file)
    monkeypatch.setattr(artifact_io.os, "replace", lambda *args: pytest.fail("partial file was replaced"))
    with pytest.raises(ArtifactWriteError) as raised:
        atomic_write_text(target, "complete new record")
    error = raised.value
    assert error.stage == "write"
    assert error.snapshot_complete is False and error.snapshot_sha256 is None
    assert error.attempts == 0
    if short_write:
        assert "Incomplete temporary artifact write" in str(error.__cause__)
    else:
        assert error.__cause__ is original_error
        assert error.cause_type == "OSError" and error.errno == errno.ENOSPC
    assert error.cleanup_error is (cleanup_error if cleanup_fails else None)
    assert error.temporary_path.exists() is cleanup_fails
    if cleanup_fails:
        assert error.temporary_path.read_bytes() == b"com"
        assert "no certified complete snapshot" in str(error)
    assert target.read_bytes() == b"old"


@pytest.mark.parametrize("interrupt", [KeyboardInterrupt, SystemExit])
def test_interrupt_during_replace_remains_interrupt_and_does_not_delete_snapshot(tmp_path, monkeypatch, interrupt):
    target = tmp_path / "record.txt"
    target.write_bytes(b"old")
    attempts = []

    def interrupted_replace(source, destination):
        attempts.append(source)
        raise interrupt()

    monkeypatch.setattr(artifact_io.os, "replace", interrupted_replace)
    with pytest.raises(interrupt):
        atomic_write_text(target, "new")
    assert len(attempts) == 1 and attempts[0].read_bytes() == b"new"
    assert target.read_bytes() == b"old"


def test_callback_error_can_keep_original_cause_without_inventing_a_path():
    cause = OSError("callback storage failed")
    error = ArtifactWriteError(None, "callback", cause)
    assert error.path is None and error.__cause__ is cause
    assert error.cause_type == "OSError"
    assert "target path not supplied" in str(error)


@pytest.mark.skipif(os.name != "nt", reason="requires native Windows sharing semantics")
def test_real_windows_sharing_handle_released_before_retry(tmp_path, monkeypatch):
    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                    wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    kernel32.CreateFileW.restype = wintypes.HANDLE
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    target = tmp_path / "native-sharing.txt"
    target.write_bytes(b"old")
    handle = kernel32.CreateFileW(str(target), 0x80000000, 0, None, 3, 0x80, None)
    assert handle != ctypes.c_void_p(-1).value, ctypes.get_last_error()
    attempts, delays = [], []
    original_replace = artifact_io.os.replace

    def replace(source, destination):
        attempts.append(source)
        original_replace(source, destination)

    def release(delay):
        nonlocal handle
        delays.append(delay)
        assert handle is not None
        assert kernel32.CloseHandle(handle)
        handle = None

    monkeypatch.setattr(artifact_io.os, "replace", replace)
    monkeypatch.setattr(artifact_io, "sleep", release)
    try:
        atomic_write_text(target, "new after handle release")
    finally:
        if handle is not None:
            kernel32.CloseHandle(handle)
    assert delays == [0.05]
    assert len(attempts) == 2 and attempts[0] == attempts[1]
    assert not attempts[0].exists()
    assert target.read_bytes() == b"new after handle release"
