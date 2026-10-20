"""Shared exclusive run ownership and accepted-call replay client."""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
import os
from pathlib import Path
import sys

from skillflow.common.llm.client import LlmClient


@contextmanager
def exclusive_run(directory: Path):
    """The OS releases this lock on process death; the lock file may remain."""
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / ".runner.lock").open("a+b") as handle:
        handle.seek(0, os.SEEK_END)
        if not handle.tell():
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        try:
            if sys.platform == "win32":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise ValueError("Another runner holds this run directory") from error
        try:
            yield
        finally:
            handle.seek(0)
            if sys.platform == "win32":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


class ReplayClient(LlmClient):
    def __init__(self, config, *, prior_calls, writer, on_record):
        super().__init__(config, record_calls=True, on_record=on_record)
        self.call_records = deepcopy(prior_calls)
        self._replay_length = len(prior_calls)
        self._replay_index = 0
        self._writer = writer

    def complete(self, prompt):
        if self._replay_index < self._replay_length:
            record = self.call_records[self._replay_index]
            if record["status"] != "complete" or record["prompt"] != self._writer.clean(prompt):
                raise ValueError("Recorded generation cannot be replayed with this prompt")
            self._replay_index += 1
            # Do not truncate the durable trace while replaying its early calls.
            return deepcopy(record["response"])
        return super().complete(prompt)


