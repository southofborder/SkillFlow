"""Keep persistence failures from hiding an earlier error or permitting resend."""
from __future__ import annotations

from typing import Callable


def error_fields(error: BaseException) -> dict:
    """These fields are redacted by the artifact writer before persistence."""
    fields = {"error": str(error), "error_type": type(error).__name__}
    if getattr(error, "recording_failed", False):
        fields["recording_failed"] = True
        fields["recording_errors"] = list(getattr(error, "recording_errors", []))
    return fields


def finalize_record(
    write: Callable[[], None], primary_error: BaseException | None,
    record: dict | None = None,
) -> None:
    """A failed final write fails success, but never replaces an active error.

    If persistence also fails during an error, retain the first exception and
    attach the secondary failure. Both retry layers must treat the attached
    marker as non-retryable. Interrupts during a write still propagate normally.
    """
    try:
        write()
    except Exception as secondary:
        if record is not None:
            record["recording_failed"] = True
        if primary_error is None:
            secondary.recording_failed = True
            if record is not None:
                record.setdefault("recording_errors", []).append({
                    "error": str(secondary), "error_type": type(secondary).__name__,
                })
            raise
        primary_error.recording_failed = True
        errors = list(getattr(primary_error, "recording_errors", []))
        errors.append({"error": str(secondary), "error_type": type(secondary).__name__})
        primary_error.recording_errors = errors
        if record is not None:
            record["recording_errors"] = list(errors)
        # LlmClientError may describe a retryable network failure. A failed
        # record of that failure makes another remote request unsafe.
        if hasattr(primary_error, "transient"):
            primary_error.transient = False
        add_note = getattr(primary_error, "add_note", None)
        if add_note is not None:
            add_note(f"Additionally failed to persist a record: {type(secondary).__name__}: {secondary}")
