"""Neutral original-content ranges; no sensitivity classification or Data mutation."""
from __future__ import annotations

from collections import defaultdict, deque
from copy import deepcopy

from skillflow.common.recording import canonical_sha256
from skillflow.doe.sensitivity_engine import covers, prefix, cut, embed, range_presence, mapped_selector
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
        self.family_sources = defaultdict(set)
        self.path_budget = 2
        def attach(identity, content, origin, family=False):
            form = content["form"]
            if origin.get("part_of"):
                self.edges[origin["part_of"]].append((identity, "project", origin["path"]))
                self.edges[identity].append((origin["part_of"], "embed", origin["path"]))
            if form == "known_parts":
                for part in content["parts"]:
                    self.edges[part["data"]].append((identity, "embed", part["path"]))
                    self.edges[identity].append((part["data"], "family_project" if family else "project", part["path"]))
                    self.path_budget += len(part["path"])
                    if family:
                        self.family_sources[identity].add(part["data"])
            elif form == "mapped_collection":
                for member in content["members"]:
                    for value in member["values"]:
                        selector = mapped_selector(data, content, member)
                        self.edges[value].append((identity, "embed", [selector]))
                        self.edges[identity].append((value, "family_project" if family else "map_project", [selector]))
                        if family:
                            self.family_sources[identity].add(value)
                self.path_budget += 1
            elif form == "selection":
                self.edges[content["base"]].append((identity, "project", content["path"]))
                self.edges[identity].append((content["base"], "family_embed" if family else "embed", content["path"]))
                self.path_budget += len(content["path"])
                if family:
                    self.family_sources[identity].add(content["base"])
            elif form == "accumulated_collection":
                from .constraint_control import collection_size
                size = collection_size(data, content["base"])
                self.edges[content["base"]].append((identity, "identity", None))
                if content["mode"] == "item":
                    self.edges[content["added"]].append((identity, "embed", [size if size is not None else {"kind": "each"}]))
                else:
                    self.edges[content["added"]].append((identity, "accumulated_items", size))
                self.path_budget += 1
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
        for identity, value in data.items():
            content, origin = value["content"], value["origin"]
            if content["form"] == "loop_summary":
                for variant in content["variants"]:
                    attach(identity, variant["content"], variant, True)
            else:
                attach(identity, content, origin)

    def track(self, sources, path):
        found, queue = defaultdict(dict), deque()
        parents, roots = defaultdict(set), set()
        def emit(identity, signal, parent=None):
            if len(signal["path"]) > self.path_budget + len(path):
                signal = {"path": [], "excluded_paths": [], "relation": "possible"}
            marker = canonical_sha256(signal)
            node = identity, marker
            changed = parent is not None and parent != node and parent not in parents[node]
            if parent is not None and parent != node:
                parents[node].add(parent)
            if marker not in found[identity]:
                found[identity][marker] = signal
                queue.append((identity, signal))
                if sum(map(len, found.values())) > self.max_states:
                    raise ConstraintLimit("Original-content range analysis exceeded its finite resource limit.")
            elif changed and self.data[identity]["content"]["form"] in {"mapped_collection", "loop_summary"}:
                queue.append((identity, signal))
            return node
        def supported(mapped, target, node, seen):
            if node in seen:
                return False
            seen = {*seen, node}
            if node in roots:
                return True
            values = self.family_sources[mapped] if self.data[mapped]["content"]["form"] == "loop_summary" else {
                value for member in self.data[mapped]["content"]["members"] for value in member["values"]}
            for parent in parents[node]:
                if node[0] == mapped and parent[0] in values:
                    if parent[0] == target:
                        return True
                elif supported(mapped, target, parent, seen):
                    return True
            return False
        for identity in sources:
            if range_presence(self.data, identity, path) not in {"absent", "empty", "invalid"}:
                roots.add(emit(identity, {"path": deepcopy(path), "excluded_paths": [], "relation": "direct"}))
        while queue:
            identity, signal = queue.popleft()
            node = identity, canonical_sha256(signal)
            for target, kind, parameter in self.edges[identity]:
                if kind in {"map_project", "family_project", "family_embed"}:
                    if not supported(identity, target, node, set()):
                        continue
                    result = embed(signal, parameter) if kind == "family_embed" else project(signal, parameter)
                elif kind == "identity":
                    result = deepcopy(signal)
                elif kind == "accumulated_items":
                    result = deepcopy(signal)
                    if result["path"] and type(result["path"][0]) is int:
                        result["path"][0] = result["path"][0] + parameter if parameter is not None else {"kind": "each"}
                    result["excluded_paths"] = [[p[0] + parameter, *p[1:]] if p and type(p[0]) is int
                        and parameter is not None else p for p in result["excluded_paths"]
                        if not (p and type(p[0]) is int and parameter is None)]
                elif kind == "project":
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
                    emit(target, result, node)
        return {identity: list(rows.values()) for identity, rows in found.items()}
