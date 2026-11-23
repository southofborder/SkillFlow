"""Recorded lexical use chains for access-specific sensitivity declarations.

Data can be shared by unrelated reads. A verified Data edge establishes what
was carried, while a lexical occurrence establishes which access supplied it.
"""
from collections import defaultdict, deque

from skillflow.common.recording import canonical_sha256


class AccessIndex:
    def __init__(self, engine):
        self.engine = engine
        self.consumers = defaultdict(list)
        self.copies = defaultdict(list)
        self.scoped_values = defaultdict(list)
        self.linked_outputs = defaultdict(list)
        self.node = {(n["kind"], n["instruction_id"], n["operation_id"], n["slot"]): k
                     for k, n in engine.nodes.items()}
        for key, info in engine.ops.items():
            ir = info["position"]["instruction_id"]
            for slot, (ref, _) in engine.slots(key).items():
                for node in self._resolve(ref, ir, info["scope"]):
                    self.consumers[node].append((key, slot))
        for ir, spec in engine.compiled["ir_semantics"].items():
            for binding in spec["output_bindings"]:
                dest = self.node.get(("ir_output", ir, None, binding["output_index"]))
                for node in self._resolve(binding["value"], ir):
                    self.copies[node].append(dest)
            for ei, event in enumerate(spec["events"]):
                if event.get("kind") == "for_each":
                    actual = engine.index.records.get(ir, {}).get("events", [])
                    if ei >= len(actual):
                        continue
                    for j, member in enumerate(actual[ei]["instances"]):
                        scope = (ei, j)
                        element = engine.elements.get((ir, scope, event["item"]))
                        for node in self._resolve(event["collection"], ir):
                            self.scoped_values[node].append((member["collection"], element, {member["element"]}, ir))
                        output = engine.locals.get((ir, None, event.get("output")))
                        if output:
                            for node in self._resolve(event["yield"], ir, scope):
                                for data in member["yielded"]:
                                    self.scoped_values[node].append((data, output, set(engine.nodes[output]["data_ids"]), ir))
        for link in engine.index.links.values():
            if link["kind"] in {"saved_read", "request_response"}:
                key = link["target"]
                ir = engine.ops[key]["position"]["instruction_id"]
                dest = self.node.get(("op_output", ir, key, 0))
                if dest:
                    self.linked_outputs[link["source"]].append((dest, set(link["data_ids"]), link["kind"]))
        for ir, instruction in engine.index.instructions.items():
            for slot, operand in enumerate(instruction["inputs"]):
                if operand["type"] == "result":
                    owner, output = engine.definitions[operand["identifier"]]
                    self.copies[self.node["ir_output", owner, None, output]].append(self.node["ir_input", ir, None, slot])
                elif operand["type"] == "context_key":
                    for location in engine._operand_locations.get((ir, "input", slot), []):
                        for write in engine.index.entry_writes.get(ir, {}).get(location, []):
                            self.linked_outputs[write].append((self.node["ir_input", ir, None, slot],
                                engine.index.written_values(write, location), "saved_read"))

    def _resolve(self, ref, ir, scope=None):
        if ref["kind"] == "input":
            return [self.node["ir_input", ir, None, ref["index"]]]
        if ref["kind"] == "alternatives":
            return {node for child in ref["items"] for node in self._resolve(child, ir, scope)}
        if ref["kind"] == "literal":
            return []
        return self.engine.resolve(ref, ir, scope)

    def trace(self, starts, edges):
        """Follow recorded value/occurrence pairs, keeping unbound transfers local."""
        allowed_slots, allowed_edges, gaps, seen = set(), set(), set(), set()
        queue = deque(starts)

        def transfer(source, target, dest, matched):
            if source == target:
                queue.append((dest, target))
            for _, relation, parameter in matched:
                allowed_edges.add((source, target, relation, canonical_sha256(parameter)))
                queue.append((dest, target))

        while queue:
            node, data = queue.popleft()
            if (node, data) in seen:
                continue
            seen.add((node, data))
            for dest in self.copies[node]:
                if dest and data in self.engine.nodes[dest]["data_ids"]:
                    queue.append((dest, data))
            for source, dest, values, ir in self.scoped_values[node]:
                if data != source or not dest:
                    continue
                for target in values:
                    matched = [e for e in edges[data] if e[0] == target]
                    if not matched and target != data:
                        gaps.add((ir, None, "recorded member or yielded value and its collection range"))
                    transfer(data, target, dest, matched)
            for key, slot in self.consumers[node]:
                info = self.engine.ops[key]
                record, spec, ir = info["record"], info["spec"], info["position"]["instruction_id"]
                if data not in record["inputs"][slot]:
                    continue
                allowed_slots.add((key, slot, data))
                for dest, linked, kind in self.linked_outputs[key]:
                    for target in self.engine.nodes[dest]["data_ids"]:
                        if kind == "saved_read" and target not in linked:
                            continue
                        if kind == "request_response" and data not in linked:
                            continue
                        matched = [e for e in edges[data] if e[0] == target]
                        if not matched and data != target and kind == "saved_read":
                            gaps.add((ir, key, "recorded write input and reached storage version"))
                        transfer(data, target, dest, matched)
                for output, values in enumerate(record["outputs"]):
                    dest = self.node["op_output", ir, key, output]
                    for value in values:
                        if record.get("alternatives") and not any(
                                data in alt["inputs"][slot] and value in alt["outputs"][output]
                                for alt in record["alternatives"]):
                            continue
                        if value == data:
                            queue.append((dest, value))
                            continue
                        # Which same-Data input supplied a constructed field is
                        # known exactly from the operation's recorded member.
                        matches = [(target, relation, parameter) for target, relation, parameter in edges[data]
                                   if target == value]
                        repeated = any(i != slot and data in xs for i, xs in enumerate(record["inputs"]))
                        if repeated and spec["op"] == "build":
                            fields = [("embed", m["path"]) for m in record["members"] if m["value_input_index"] == slot]
                            fields.extend(("conditional_membership", m["path"]) for m in record["members"]
                                          if m["when_input_index"] == slot)
                            matches = [(t, r, p) for t, r, p in matches if (r, p) in fields]
                        elif repeated and matches:
                            gaps.add((ir, key, "individual repeated input and output range"))
                            continue
                        transfer(data, value, dest, matches)
        return allowed_slots, allowed_edges, gaps
