"""Neutral original-content ranges; no sensitivity classification or Data mutation."""
from __future__ import annotations

from collections import defaultdict, deque
from copy import deepcopy

from skillflow.common.recording import canonical_sha256
from skillflow.doe.sensitivity_engine import covers, prefix, cut, embed, range_presence
from skillflow.propagation.data import is_definitely_empty_collection
from .constraint_control import ConstraintLimit


def project(signal, path):
    if any(covers(excluded, path) for excluded in signal["excluded_paths"]):
        return None
    if prefix(path, signal["path"]):
        result = {**deepcopy(signal), "path": signal["path"][len(path):]}
    elif prefix(signal["path"], path):
        # Unlike sensitivity classification, an explicit ban on original whole
        # content also covers an explicitly selected proper part of that content.
        result = {**deepcopy(signal), "path": []}
    else:
        return None
    result["excluded_paths"] = [p[len(path):] for p in signal["excluded_paths"] if prefix(path, p)]
    return result


class ContentRanges:
    def __init__(self, data, *, max_states=20000):
        self.data, self.max_states = data, max_states
        self.edges = defaultdict(list)
        for identity, value in data.items():
            content, origin = value["content"], value["origin"]
            form = content["form"]
            if origin.get("part_of"):
                self.edges[origin["part_of"]].append((identity, "project", origin["path"]))
                self.edges[identity].append((origin["part_of"], "embed", origin["path"]))
            if form == "known_parts":
                for part in content["parts"]:
                    self.edges[part["data"]].append((identity, "embed", part["path"]))
                    self.edges[identity].append((part["data"], "project", part["path"]))
            elif form == "whole_except":
                self.edges[content["base"]].append((identity, "cut", content["excluded_parts"]))
            elif form == "field_updates":
                self.edges[content["base"]].append((identity, "cut", [part["path"] for part in content["updates"]]))
                for part in content["updates"]:
                    self.edges[part["data"]].append((identity, "embed", part["path"]))
            elif form == "subset_view":
                if not is_definitely_empty_collection(data, identity):
                    self.edges[content["base"]].append((identity, "subset", None))
            # An opaque result can have descriptive known parts. Those parts do
            # not erase its separately declared possible/derived dependencies.
            if form == "opaque" or form == "known_parts" and not content["parts_complete"]:
                dependencies = {row["data"] for row in origin.get("dependencies", [])}
                dependencies.update(origin.get("inputs", []))
                for source in dependencies:
                    self.edges[source].append((identity, "possible", None))

    def track(self, sources, path):
        found, queue = defaultdict(dict), deque()
        def emit(identity, signal):
            marker = canonical_sha256(signal)
            if marker not in found[identity]:
                found[identity][marker] = signal
                queue.append((identity, signal))
                if sum(map(len, found.values())) > self.max_states:
                    raise ConstraintLimit("Original-content range analysis exceeded its finite resource limit.")
        for identity in sources:
            if range_presence(self.data, identity, path) not in {"absent", "empty", "invalid"}:
                emit(identity, {"path": deepcopy(path), "excluded_paths": [], "relation": "direct"})
        while queue:
            identity, signal = queue.popleft()
            for target, kind, parameter in self.edges[identity]:
                if kind == "project":
                    result = project(signal, parameter)
                elif kind == "embed":
                    result = embed(signal, parameter)
                elif kind == "cut":
                    result = cut(signal, parameter)
                elif kind == "subset":
                    result = {**deepcopy(signal), "relation": "possible"}
                    if result["path"] and type(result["path"][0]) is int:
                        result["path"][0] = {"kind": "each"}
                    result["excluded_paths"] = [p for p in result["excluded_paths"] if not p or type(p[0]) is not int]
                else:
                    result = {"path": [], "excluded_paths": [], "relation": "possible"}
                if result is not None:
                    emit(target, result)
        return {identity: list(rows.values()) for identity, rows in found.items()}
