"""Scope missing-source comparison diagnostics to recorded acquisitions and their uses."""
from collections import defaultdict

from .access_sensitivity import AccessIndex
from .constraint_control import ConstraintLimit
from .constraint_ranges import ContentRanges
from .review_ranges import overlap_information


class IngressLimits:
    def __init__(self, engine):
        self.engine = engine
        self.cache = {}
        self.content = self.access = None
        self.sources = defaultdict(list)
        outputs = defaultdict(list)
        for node_id, node in engine.nodes.items():
            if node["kind"] == "ir_output":
                outputs[node["instruction_id"]].extend((node_id, data) for data in node["data_ids"])
            if node["kind"] != "op_output":
                continue
            info = engine.ops[node["operation_id"]]
            if info["spec"]["op"] in {"receive", "read"}:
                self.sources[node["instruction_id"]].extend((node_id, data) for data in node["data_ids"])
        for ir, bound in outputs.items():
            if not self.sources.get(ir):
                self.sources[ir] = bound

    def _uses(self, ir):
        if ir in self.cache:
            return self.cache[ir]
        starts = self.sources.get(ir)
        if not starts:
            self.cache[ir] = None
        else:
            if self.content is None:
                self.content = ContentRanges(self.engine.index.data)
                self.access = AccessIndex(self.engine)
            slots, edges, gaps = self.access.trace(starts, self.content.edges)
            try:
                fields = self.content.track({data for _, data in starts}, [], allowed_edges=edges)
            except ConstraintLimit:
                # Lexical version identity still bounds the affected uses.
                fields = None
            self.cache[ir] = slots, fields, gaps
        return self.cache[ir]

    def filter(self, limitations, diagnostics, operation, slot, data, signal, relevant):
        result = []
        for identity in limitations:
            diagnostic = diagnostics[identity]
            if diagnostic["code"] == "missing_sensitivity_ingress":
                uses = self._uses(diagnostic["instruction_id"])
                if uses is not None:
                    slots, fields, gaps = uses
                    if (operation, slot, data) not in slots and not any(ir in relevant for ir, _, _ in gaps):
                        continue
                    if ((operation, slot, data) in slots and fields is not None and data in fields and
                            not any(overlap_information({**item, "property": "value"}, signal) for item in fields[data])):
                        continue
            result.append(identity)
        return result
