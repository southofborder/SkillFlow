"""Atomic local text artifacts, without treating persistence as transport.

A complete temporary snapshot survives a failed replacement. Retrying a Windows
sharing/access failure reuses that closed file; it never regenerates the content
or calls a model. Callers must redact content before handing it to this module.
"""

from __future__ import annotations

import hashlib
import os
from collections.abc import Iterable
from pathlib import Path
from time import sleep
from uuid import uuid4


_REPLACE_DELAYS = (0.05, 0.1, 0.2, 0.4, 0.8, 1.0)
_RETRYABLE_WINERRORS = frozenset({5, 32, 33})


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class ArtifactWriteError(RuntimeError):
    """Local persistence failed; the original exception is retained as cause.

    ``snapshot_sha256`` describes only a fully written, closed temporary file.
    A failed or partially written snapshot never carries that certificate.
    """

    def __init__(
        self, path: Path | None, stage: str, cause: Exception | None = None, *, temporary_path: Path | None = None,
        snapshot_complete: bool = False, snapshot_sha256: str | None = None,
        attempts: int = 0, cleanup_error: Exception | None = None,
    ) -> None:
        self.path = path
        self.stage = stage
        self.temporary_path = temporary_path
        self.snapshot_complete = snapshot_complete
        self.snapshot_sha256 = snapshot_sha256
        self.attempts = attempts
        self.cleanup_error = cleanup_error
        self.cause_type = type(cause).__name__ if cause is not None else None
        self.errno = getattr(cause, "errno", None)
        self.winerror = getattr(cause, "winerror", None)
        if cause is not None:
            self.__cause__ = cause
        snapshot = (f"complete snapshot retained at {temporary_path}; SHA-256 {snapshot_sha256}"
                    if snapshot_complete else "no certified complete snapshot")
        cleanup = (f"; partial-file cleanup also failed ({type(cleanup_error).__name__})"
                   if cleanup_error is not None else "")
        diagnosis = (f"; cause={self.cause_type}, errno={self.errno}, winerror={self.winerror}"
                     if cause is not None else "")
        target = str(path) if path is not None else "target path not supplied"
        super().__init__(f"Artifact write failed at {stage}: {target}; {snapshot}; "
                         f"replacement attempts={attempts}{diagnosis}{cleanup}")


def atomic_write_text(path: Path, value: str) -> None:
    """Commit exact UTF-8 text, preserving the old destination on failure.

    Retry only Windows access/sharing/lock violations while replacing a closed
    complete file. The six bounded delays total 2.55 seconds. No write, mkdir or
    unrelated replacement failure is retried. Interrupts remain interrupts.
    """
    atomic_write_chunks(path, (value,))


def atomic_write_chunks(path: Path, chunks: Iterable[str], *, match_existing: bool = False) -> None:
    """Stream exact UTF-8 chunks into one closed snapshot before publication."""
    path = Path(path).absolute()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as error:
        raise ArtifactWriteError(path, "mkdir", error) from error

    temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    try:
        digest = hashlib.sha256()
        with temporary.open("xb") as stream:
            for chunk in chunks:
                payload = chunk.encode("utf-8")
                if stream.write(payload) != len(payload):
                    raise OSError("Incomplete temporary artifact write")
                digest.update(payload)
        # The context manager must close successfully before this is complete.
    except Exception as error:
        cleanup_error = None
        try:
            temporary.unlink(missing_ok=True)
        except Exception as cleanup_failure:
            cleanup_error = cleanup_failure
        raise ArtifactWriteError(
            path, "write", error, temporary_path=temporary, cleanup_error=cleanup_error,
        ) from error

    snapshot_sha256 = digest.hexdigest()
    if match_existing and path.exists():
        same = file_sha256(path) == snapshot_sha256
        temporary.unlink()
        if not same:
            raise ValueError("Interrupted formal DOE artifact differs: " + path.name)
        return
    for attempt in range(len(_REPLACE_DELAYS) + 1):
        try:
            os.replace(temporary, path)
            return
        except Exception as error:
            if (isinstance(error, OSError)
                    and getattr(error, "winerror", None) in _RETRYABLE_WINERRORS
                    and attempt < len(_REPLACE_DELAYS)):
                sleep(_REPLACE_DELAYS[attempt])
                continue
            # Do not delete the complete snapshot: it may contain the only
            # durable copy of an already accepted remote response.
            raise ArtifactWriteError(
                path, "replace", error, temporary_path=temporary,
                snapshot_complete=True, snapshot_sha256=snapshot_sha256,
                attempts=attempt + 1,
            ) from error
