"""Offline revision bookkeeping; no stage selection or model transport setup."""
from copy import deepcopy
from pathlib import Path
import re

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.recording import (
    RecordingClient, SavedResponseClient, canonical_sha256, implementation_provenance,
    injected_factory, read_json,
)
from skillflow.common.runs import exclusive_run
from .batches import validate_batch

IDENTITY = "skillflow-document-offline-v1"


def _name(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", value):
        raise ValueError("An audit name must be a simple local identifier")


def _bound(path, expected, writer):
    if path.exists():
        if read_json(path) != expected:
            raise ValueError("Frozen request or batch bindings differ")
    else:
        writer.json(path, expected)


def _request_identity(prompt, bindings):
    return {"identity": IDENTITY, "prompt_sha256": canonical_sha256(prompt),
            "bindings": deepcopy(bindings), "implementation": implementation_provenance()}


def record_injected_request(directory, prompt, bindings, *, client):
    """The caller explicitly supplies an offline client; saved calls never resend."""
    directory, writer = Path(directory), ArtifactWriter(())
    with exclusive_run(directory):
        _bound(directory / "request.json", _request_identity(prompt, bindings), writer)
        saved = directory / "call"
        if (saved / "call.json").exists():
            return SavedResponseClient(saved, writer).complete(prompt)
        if any(saved.glob("*")):
            raise ValueError("Incomplete call preparation; no automatic resend")
        return RecordingClient(saved, injected_factory(client), writer).complete(prompt)


def replay_request(directory, prompt, bindings):
    directory = Path(directory)
    if read_json(directory / "request.json") != _request_identity(prompt, bindings):
        raise ValueError("Replay request, upstream materials, or implementation changed")
    return SavedResponseClient(directory / "call", ArtifactWriter(())).complete(prompt)


class BatchJournal:
    """Select immutable revisions atomically; dependencies are audit-only bindings.

    The caller supplies behavioral batches and dependencies explicitly. This
    class does not infer links, create demands, or schedule semantic repairs.
    """
    def __init__(self, directory, bindings):
        self.directory, self.writer = Path(directory), ArtifactWriter(())
        self.binding = {"identity": IDENTITY, "bindings": deepcopy(bindings)}
        with exclusive_run(self.directory):
            _bound(self.directory / "bindings.json", self.binding, self.writer)
            if not (self.directory / "selection.json").exists():
                self.writer.json(self.directory / "selection.json", {})

    def _load(self):
        if read_json(self.directory / "bindings.json") != self.binding:
            raise ValueError("Frozen batch bindings differ")
        selection = read_json(self.directory / "selection.json")
        if not isinstance(selection, dict):
            raise ValueError("Invalid batch selection")
        loaded = {}
        for name, digest in selection.items():
            _name(name)
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise ValueError("Invalid batch revision address")
            row = read_json(self.directory / "revisions" / (digest + ".json"))
            if canonical_sha256(row) != digest or row["name"] != name:
                raise ValueError("Batch revision identity mismatch")
            if row.get("bindings_sha256") != canonical_sha256(self.binding):
                raise ValueError("Batch revision belongs to different frozen inputs")
            if validate_batch(row["kind"], row["response"]) != row["value"]:
                raise ValueError("Batch normalization differs from its response")
            loaded[name] = row
        return selection, loaded

    def accept(self, name, kind, response, *, depends_on=None):
        _name(name)
        normalized = validate_batch(kind, response)
        with exclusive_run(self.directory):
            selection, loaded = self._load()
            dependencies = dict(depends_on or {})
            if name in dependencies or any(selection.get(key) != digest for key, digest in dependencies.items()):
                raise ValueError("Batch dependency is missing, stale, or self-referential")
            if name in loaded and loaded[name]["kind"] != kind:
                raise ValueError("A replacement cannot change batch kind")
            row = {"name": name, "kind": kind, "response": deepcopy(response),
                   "value": normalized, "depends_on": dependencies,
                   "bindings_sha256": canonical_sha256(self.binding)}
            digest = canonical_sha256(row)
            _bound(self.directory / "revisions" / (digest + ".json"), row, self.writer)
            selection[name] = digest
            self.writer.json(self.directory / "selection.json", selection)
            return digest

    def current(self):
        selection, loaded = self._load()
        for row in loaded.values():
            if any(selection.get(key) != digest for key, digest in row["depends_on"].items()):
                raise ValueError("A downstream batch uses a replaced upstream revision")
        return {name: deepcopy(row["value"]) for name, row in loaded.items()}

    def revisions(self):
        return dict(self._load()[0])
