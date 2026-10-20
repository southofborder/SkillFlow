"""Deterministic, read-only sink relations over verified propagation components.

Content relations stay in Data, and use links describe static possibilities.
Neither relation establishes sensitivity, necessity, or measured execution.
"""
from __future__ import annotations

from collections import defaultdict, deque
from copy import deepcopy
import json
from pathlib import Path

from skillflow.common.recording import canonical_sha256
from skillflow.common.source_evidence import _json_object
from skillflow.propagation.conditions import payload_inputs
from skillflow.propagation.contracts.runtime_contract import (
    runtime_contract_binding, validate_runtime_contract,
)
from skillflow.propagation.data import validate_data_records, validate_element_membership
from skillflow.propagation.loading import PropagationMaterials
from skillflow.common.source_evidence import _checked_source

from .models import DoeMaterial


def _id(prefix, value):
    if prefix == "op_":
        suffix = f":e{value['event_index']}"
        if value["instance_index"] is not None:
            suffix += f":i{value['instance_index']}:b{value['body_event_index']}"
        return prefix + value["instruction_id"] + suffix + f":a{value['op_index']}"
    if prefix == "scope_":
        return f"scope_{value[0]}:e{value[1]}:i{value[2]}"
    # Compact new references, while original Data IDs are never shortened.
    # Insertion checks below reject a collision instead of overwriting a fact.
    return prefix + canonical_sha256(value)[:20]


def _ids(slots):
    return {value for slot in slots for value in slot}


def _data_refs(data):
    content, origin = data["content"], data["origin"]
    refs = set(origin.get("inputs", []))
    refs.update(item["data"] for item in origin.get("dependencies", []))
    if origin.get("part_of"):
        refs.add(origin["part_of"])
    if content.get("base"):
        refs.add(content["base"])
    refs.update(item["data"] for item in content.get("parts", []))
    refs.update(item["data"] for item in content.get("updates", []))
    return refs


def _operation_data(operation):
    record = operation["record"]
    refs = _ids([*record["inputs"], *record["outputs"]])
    for change in record["changes"]:
        refs.update(change["before"])
        refs.update(change["after"])
    return refs


def _location(location):
    return location["kind"], location["name"]


def _template(position):
    return (position["event_index"], position["body_event_index"], position["op_index"])


def _order_key(position):
    return (position["event_index"], -1 if position["body_event_index"] is None else position["body_event_index"], position["op_index"])


class _Index:
    def __init__(self, raw):
        self.raw, self.cfg = raw, raw.cfg
        self.data = {item["id"]: deepcopy(item) for item in raw.data}
        self.instructions, self.ir_block, self.ir_offset = {}, {}, {}
        self.operations, self.ir_operations, self.scopes = {}, defaultdict(list), {}
        self.location_ids = {_location(value): key for key, value in raw.locations.items()}
        self.successors, self.predecessors = defaultdict(set), defaultdict(set)
        for edge in self.cfg["edges"]:
            source, target = edge["source_block_id"], edge["target_block_id"]
            self.successors[source].add(target)
            self.predecessors[target].add(source)
        self.reachable = {}
        for block in self.cfg["blocks"]:
            self.reachable[block] = self._closure({block}, self.successors)
        for block_id, block in self.cfg["blocks"].items():
            for offset, ir in enumerate(block["instructions"]):
                ir_id = ir["id"]
                self.instructions[ir_id] = deepcopy(ir)
                self.ir_block[ir_id], self.ir_offset[ir_id] = block_id, offset
        self.precedence = {}
        for ir_id, record in raw.records.items():
            relation = defaultdict(set)
            for item in record["precedence"]:
                relation[_template(item["before"])].add(_template(item["after"]))
            for event_index, event in enumerate(record["events"]):
                children = [(body_index, child) for instance in event.get("instances", [])
                            for body_index, child in enumerate(instance["body"])] if event.get("kind") == "for_each" else [(None, event)]
                for body_index, child in children:
                    for op_index in range(1, len(child["atomic_ops"])):
                        relation[(event_index, body_index, op_index - 1)].add((event_index, body_index, op_index))
            self.precedence[ir_id] = {key: self._closure(value, relation) for key, value in relation.items()}
            for event_index, event in enumerate(record["events"]):
                if event.get("kind") == "for_each":
                    for instance_index, instance in enumerate(event["instances"]):
                        scope = {"instruction_id": ir_id, "event_index": event_index,
                                 "instance_index": instance_index, "collection": instance["collection"], "element": instance["element"]}
                        self.scopes[_id("scope_", [ir_id, event_index, instance_index])] = scope
                        for body_index, child in enumerate(instance["body"]):
                            self._add_operations(ir_id, event_index, child, body_index, instance_index)
                else:
                    self._add_operations(ir_id, event_index, event)
        self.producers, self.consumers = defaultdict(set), defaultdict(set)
        for op_id, operation in self.operations.items():
            for data_id in _ids(operation["record"]["outputs"]):
                self.producers[data_id].add(op_id)
            for data_id in _ids(operation["record"]["inputs"]):
                self.consumers[data_id].add(op_id)
        self.links = {}
        self._value_links()
        self._memory_links()
        self.outgoing, self.incoming = defaultdict(set), defaultdict(set)
        for key, link in self.links.items():
            self.outgoing[link["source"]].add(key)
            self.incoming[link["target"]].add(key)

    @staticmethod
    def _closure(seeds, edges):
        found, queue = set(seeds), list(seeds)
        while queue:
            for target in edges.get(queue.pop(), ()):
                if target not in found:
                    found.add(target)
                    queue.append(target)
        return found

    def _add_operations(self, ir_id, event_index, event, body_index=None, instance_index=None):
        for op_index, record in enumerate(event["atomic_ops"]):
            position = {"instruction_id": ir_id, "event_index": event_index, "op_index": op_index,
                        "body_event_index": body_index, "instance_index": instance_index}
            key = _id("op_", position)
            self.operations[key] = {"position": position, "effect": event["effect"], "record": deepcopy(record)}
            self.ir_operations[ir_id].append(key)

    def ir_may_before(self, source, target):
        a, b = self.ir_block[source], self.ir_block[target]
        if a == b:
            if self.ir_offset[source] < self.ir_offset[target]:
                return True
            # A control backedge may connect a later definition to a later iteration.
            return any(a in self.reachable[next_block] for next_block in self.successors[a])
        return b in self.reachable[a]

    def may_before(self, source, target):
        if source == target:
            return False
        a, b = self.operations[source]["position"], self.operations[target]["position"]
        if a["instruction_id"] != b["instruction_id"]:
            return self.ir_may_before(a["instruction_id"], b["instruction_id"])
        if (a["instance_index"] is not None and b["instance_index"] is not None
                and a["event_index"] == b["event_index"] and a["instance_index"] != b["instance_index"]):
            return False
        if self.raw.records[a["instruction_id"]]["order"] == "fixed":
            return _order_key(a) < _order_key(b)
        # In a partial order, permit a candidate only when the reverse is not required.
        return _template(a) not in self.precedence[a["instruction_id"]].get(_template(b), set())

    def add_link(self, kind, source, target, data_ids, result=None):
        link = {"kind": kind, "source": source, "target": target, "data_ids": sorted(data_ids), "result": result}
        key = _id("link_", link)
        if key in self.links and self.links[key] != link:
            raise ValueError("usage reference digest collision")
        self.links[key] = link

    def _result_values(self, ir_id, side, name):
        record = self.raw.records.get(ir_id)
        if record is None:
            return set()
        return {data_id for binding in record[side + "_state"]["bindings"]
                if binding["location"] == {"kind": "result", "name": name}
                for data_id in binding["data_ids"]}

    def _value_links(self):
        for data_id, producers in self.producers.items():
            for producer in producers:
                for consumer in self.consumers[data_id]:
                    # Cross-IR uses belong to exact public-result or reaching-
                    # memory links, not another all-pairs copy of those facts.
                    if (self.operations[producer]["position"]["instruction_id"] == self.operations[consumer]["position"]["instruction_id"]
                            and self.may_before(producer, consumer)):
                        # Merge candidate intersections at one operation pair below.
                        actual = _ids(self.operations[producer]["record"]["outputs"]) & _ids(self.operations[consumer]["record"]["inputs"])
                        self.add_link("produces_consumes", producer, consumer, actual)
        definitions = {out["identifier"]: ir_id for ir_id, ir in self.instructions.items() for out in ir["outputs"]}
        for ir_id, ir in self.instructions.items():
            for operand in ir["inputs"]:
                if operand["type"] != "result":
                    continue
                result = operand["identifier"]
                definition = definitions[result]
                if self.ir_may_before(definition, ir_id):
                    ids = self._result_values(definition, "exit", result) & self._result_values(ir_id, "entry", result)
                    self.add_link("result_use", definition, ir_id, ids, result)
            for operand in ir["outputs"]:
                ids = self._result_values(ir_id, "exit", operand["identifier"])
                for op_id in self.ir_operations[ir_id]:
                    produced = _ids(self.operations[op_id]["record"]["outputs"]) & ids
                    if produced:
                        self.add_link("result_binding", op_id, ir_id, produced, operand["identifier"])
        for observer, operation in self.operations.items():
            if operation["effect"] != "model_observe" or operation["record"]["op"] != "deliver":
                continue
            observed = _ids(payload_inputs(operation["record"]))
            for data_id in observed:
                for consumer in self.consumers[data_id]:
                    if (operation["position"]["instruction_id"] == self.operations[consumer]["position"]["instruction_id"]
                            and self.may_before(observer, consumer)):
                        used = observed & _ids(self.operations[consumer]["record"]["inputs"])
                        self.add_link("observed_use", observer, consumer, used)
        # Recover only an unambiguous, identical request binding at one existing scope.
        receipts = [key for key, value in self.operations.items() if value["record"]["op"] == "receive"]
        matches = {}
        for receipt in receipts:
            operation = self.operations[receipt]
            pos, record = operation["position"], operation["record"]
            choices = []
            for delivery in self.ir_operations[pos["instruction_id"]]:
                prior = self.operations[delivery]
                if (prior["record"]["op"] == "deliver" and prior["effect"] != "model_observe"
                        and prior["position"]["instance_index"] == pos["instance_index"]
                        and prior["record"]["endpoints"] == record["endpoints"]
                        and payload_inputs(prior["record"]) == record["inputs"] and self.may_before(delivery, receipt)):
                    choices.append(delivery)
            if len(choices) == 1:
                matches[receipt] = choices[0]
        counts = defaultdict(int)
        for delivery in matches.values():
            counts[delivery] += 1
        for receipt, delivery in matches.items():
            if counts[delivery] == 1:
                self.add_link("request_response", delivery, receipt, _ids(self.operations[receipt]["record"]["inputs"]))

    def _memory_links(self):
        """Finite reaching-write identities, separate from coincident Data values."""
        # Also expose the same entry reaching definitions to offline demand
        # clients that consume an explicit context operand without a read op.
        # This does not add links or change sink slicing semantics.
        self.entry_writes = {}
        out, reached = {}, set()
        roots = {self.cfg["entry_block_id"]}
        queue, queued = deque(sorted(roots)), set(roots)
        links = set()

        def merge(states):
            result = {}
            for state in states:
                for location, definitions in state.items():
                    result.setdefault(location, set()).update(definitions)
            return result

        def writes(op_id, state, *, weak=False):
            for change in self.operations[op_id]["record"]["changes"]:
                location = _location(change["location"])
                if not weak and change["update"] == "delete":
                    state.pop(location, None)
                elif change["after"]:
                    if weak or change["update"] == "weak":
                        state.setdefault(location, set()).add(op_id)
                    else:
                        state[location] = {op_id}

        def reads(op_id, state):
            op = self.operations[op_id]["record"]
            if op["op"] != "read":
                return
            values = _ids(op["outputs"])
            for endpoint in op["endpoints"]:
                location = _location(endpoint)
                for definition in state.get(location, set()):
                    stored = {data_id for change in self.operations[definition]["record"]["changes"]
                              if _location(change["location"]) == location for data_id in change["after"]}
                    common = stored & values
                    if common:
                        links.add((definition, op_id, tuple(sorted(common))))

        while queue:
            block_id = queue.popleft()
            queued.remove(block_id)
            state = merge(out[p] for p in self.predecessors[block_id] if p in out)
            for ir in self.cfg["blocks"][block_id]["instructions"]:
                ir_id = ir["id"]
                self.entry_writes[ir_id] = merge([state])
                if ir_id not in self.raw.records:
                    continue
                operations = self.ir_operations[ir_id]
                if self.raw.records[ir_id]["order"] == "partial":
                    base = merge([state])

                    def visible_at(read_id=None):
                        candidates = [key for key in operations if read_id is None or self.may_before(key, read_id)]
                        barriers = defaultdict(set)
                        for key in candidates:
                            guaranteed = read_id is None or _template(self.operations[read_id]["position"]) in self.precedence[ir_id].get(_template(self.operations[key]["position"]), set())
                            if guaranteed:
                                for change in self.operations[key]["record"]["changes"]:
                                    if change["update"] in {"strong", "delete"}:
                                        barriers[_location(change["location"])].add(key)
                        visible = {loc: set(defs) for loc, defs in base.items() if not barriers[loc]}
                        for key in candidates:
                            for change in self.operations[key]["record"]["changes"]:
                                loc = _location(change["location"])
                                if not change["after"]:
                                    continue
                                overwritten = any(other != key and _template(self.operations[other]["position"]) in self.precedence[ir_id].get(_template(self.operations[key]["position"]), set()) for other in barriers[loc])
                                if not overwritten:
                                    visible.setdefault(loc, set()).add(key)
                        return visible

                    for op_id in operations:
                        reads(op_id, visible_at(op_id))
                    state = visible_at()
                else:
                    for op_id in operations:
                        reads(op_id, state)
                        writes(op_id, state)
            changed = block_id not in reached or state != out.get(block_id)
            out[block_id], reached = state, reached | {block_id}
            if changed:
                for next_block in sorted(self.successors[block_id]):
                    if next_block not in queued:
                        queue.append(next_block)
                        queued.add(next_block)
        for source, target, data_ids in sorted(links):
            self.add_link("saved_read", source, target, data_ids)

    def data_closure(self, seeds):
        return self._closure(set(seeds), {key: _data_refs(value) for key, value in self.data.items()})

    def sink_operations(self, boundary):
        found = []
        for key in self.ir_operations[boundary["instruction_id"]]:
            op = self.operations[key]
            position = op["position"]
            if (position["event_index"] == boundary["event_index"] and position["op_index"] == boundary["op_index"]
                    and position["body_event_index"] == boundary["body_event_index"]):
                # False conditional member instances stay out of this sink's payload.
                if op["record"].get("when_input_index") is not None and not payload_inputs(op["record"]):
                    continue
                found.append(key)
        return found

    def slice(self, boundary):
        anchors = self.sink_operations(boundary)
        root_data = set().union(*(_ids(payload_inputs(self.operations[key]["record"])) for key in anchors))
        backward_data = self.data_closure(root_data)
        backward_ops, queue = set(anchors), list(anchors)
        for data_id in backward_data:
            for producer in self.producers[data_id]:
                if any(self.may_before(producer, anchor) for anchor in anchors):
                    backward_ops.add(producer)
                    queue.append(producer)
        while queue:
            target = queue.pop()
            for link_id in self.incoming[target]:
                link = self.links[link_id]
                if link["kind"] not in {"produces_consumes", "saved_read"}:
                    continue
                source = link["source"]
                if source not in backward_ops:
                    backward_ops.add(source)
                    queue.append(source)
        for key in backward_ops:
            backward_data.update(self.data_closure(_operation_data(self.operations[key])))

        anchor_ir = boundary["instruction_id"]
        usage_nodes, usage_links = {anchor_ir, *anchors}, set()
        # Current action's concrete ordered steps are its immediate use context.
        usage_nodes.update(self.ir_operations[anchor_ir])
        queue = list(usage_nodes)
        while queue:
            node = queue.pop()
            for link_id in self.outgoing[node]:
                link = self.links[link_id]
                if node in self.operations:
                    op = self.operations[node]
                    if op["record"]["op"] == "deliver" and op["effect"] != "model_observe" and link["kind"] != "request_response":
                        continue
                usage_links.add(link_id)
                target = link["target"]
                if target not in usage_nodes:
                    usage_nodes.add(target)
                    queue.append(target)
                if target in self.instructions:
                    for op_id in self.ir_operations[target]:
                        if op_id not in usage_nodes:
                            usage_nodes.add(op_id)
                            queue.append(op_id)
        usage_ops = usage_nodes & self.operations.keys()
        usage_irs = (usage_nodes & self.instructions.keys()) | {self.operations[key]["position"]["instruction_id"] for key in usage_ops}
        selected_irs = usage_irs | {self.operations[key]["position"]["instruction_id"] for key in backward_ops}
        relevant_blocks = {self.ir_block[key] for key in selected_irs}
        context_blocks = self._closure(relevant_blocks, self.predecessors)
        scope_ids = [key for key, value in self.scopes.items() if value["instruction_id"] in selected_irs
                     and any(op["position"]["instruction_id"] == value["instruction_id"]
                             and op["position"]["event_index"] == value["event_index"]
                             and op["position"]["instance_index"] == value["instance_index"]
                             for op_id, op in self.operations.items() if op_id in backward_ops | usage_ops)]
        diagnostics = [deepcopy(item) for item in self.raw.diagnostics
                       if item.get("instruction_id") in selected_irs
                       or any(block in context_blocks for block in item.get("blocks", []))
                       or "instruction_id" not in item and "blocks" not in item]
        return {"sink": {"id": _id("sink_", boundary), "boundary": deepcopy(boundary), "operations": anchors},
                "backward_slice": {"data": sorted(backward_data), "operations": self.sort_ops(backward_ops)},
                "usage_context": {"instructions": sorted(usage_irs), "operations": self.sort_ops(usage_ops), "links": sorted(usage_links)},
                "context": {"blocks": sorted(context_blocks), "edge_indices": [], "scope_ids": sorted(scope_ids),
                            "diagnostics": diagnostics,
                            "partial_ir_ids": sorted(key for key in selected_irs if self.raw.records.get(key, {}).get("order") == "partial")}}

    def sort_ops(self, keys):
        return sorted(keys, key=lambda key: (self.operations[key]["position"]["instruction_id"],
                      _order_key(self.operations[key]["position"]),
                      -1 if self.operations[key]["position"]["instance_index"] is None else self.operations[key]["position"]["instance_index"]))


def _read_materials(value):
    if not isinstance(value, PropagationMaterials):
        raise TypeError("Use verified propagation materials; standalone DOE input files are not supported")
    return value


def prepare_doe_material(facts) -> DoeMaterial:
    """Build factual material without executing Skills, calling models, or adding Data."""
    raw = _read_materials(facts)
    user_request = raw.material["user_request"]
    index = _Index(raw)
    slices = [index.slice(boundary) for boundary in raw.sinks]
    selected_blocks = set().union(*(set(item["context"]["blocks"]) for item in slices)) if slices else {index.cfg["entry_block_id"]}
    selected_irs = {ir["id"] for block in selected_blocks for ir in index.cfg["blocks"][block]["instructions"]}
    # Definition closure keeps identifiers in selected IRs meaningful without the full CFG.
    definitions = {operand["identifier"]: ir_id for ir_id, ir in index.instructions.items() for operand in ir["outputs"]}
    def definition_closure():
        queue = list(selected_irs)
        while queue:
            for operand in index.instructions[queue.pop()]["inputs"]:
                if operand["type"] == "result" and definitions[operand["identifier"]] not in selected_irs:
                    definition = definitions[operand["identifier"]]
                    block = index.ir_block[definition]
                    selected_blocks.add(block)
                    for ir in index.cfg["blocks"][block]["instructions"]:
                        if ir["id"] not in selected_irs:
                            selected_irs.add(ir["id"])
                            queue.append(ir["id"])
    definition_closure()
    op_ids = set().union(*(set(item["backward_slice"]["operations"]) | set(item["usage_context"]["operations"]) for item in slices)) if slices else set()
    link_ids = set().union(*(set(item["usage_context"]["links"]) for item in slices)) if slices else set()
    # A link is a shared fact and cannot dangle after projection.
    for key in link_ids:
        for node in (index.links[key]["source"], index.links[key]["target"]):
            if node in index.operations:
                op_ids.add(node)
    data_ids = set().union(*(set(item["backward_slice"]["data"]) for item in slices)) if slices else set()
    for key in op_ids:
        data_ids.update(_operation_data(index.operations[key]))
    scope_ids = set().union(*(set(item["context"]["scope_ids"]) for item in slices)) if slices else set()
    for key in scope_ids:
        data_ids.update((index.scopes[key]["collection"], index.scopes[key]["element"]))
    for key in link_ids:
        data_ids.update(index.links[key]["data_ids"])
    data_ids = index.data_closure(data_ids)
    if not data_ids <= index.data.keys():
        raise ValueError("Sink relation references missing Data")
    location_ids = {boundary["target"] for boundary in raw.sinks}
    for key in op_ids:
        for location in index.operations[key]["record"]["endpoints"]:
            location_ids.add(index.location_ids[_location(location)])
        for change in index.operations[key]["record"]["changes"]:
            location_ids.add(index.location_ids[_location(change["location"])])
    for location_id in location_ids:
        for ref in raw.locations[location_id]["operand_refs"]:
            block = index.ir_block[ref["instruction_id"]]
            selected_blocks.add(block)
            selected_irs.update(ir["id"] for ir in index.cfg["blocks"][block]["instructions"])
    definition_closure()
    edges = [deepcopy(edge) for edge in index.cfg["edges"] if edge["source_block_id"] in selected_blocks and edge["target_block_id"] in selected_blocks]
    for item in slices:
        blocks = set(item["context"]["blocks"])
        item["context"]["edge_indices"] = [i for i, edge in enumerate(edges) if edge["source_block_id"] in blocks and edge["target_block_id"] in blocks]
    blocks = {key: {"block_id": key, "block_name": value["block_name"],
              "instruction_ids": [ir["id"] for ir in value["instructions"]],
              "constraints": value.get("constraints", []), "data_source_kind": value.get("data_source_kind")}
              for key, value in index.cfg["blocks"].items() if key in selected_blocks}
    contract = raw.runtime_contract
    material = {"schema_version": "skillflow-doe-material-v2", "task": {"basis": "declared_skill" if user_request is None else "user_request", "text": user_request},
                "source": deepcopy(raw.source), "runtime_contract": {**contract, "sha256": runtime_contract_binding(contract)["sha256"]},
                "shared_info": {"entry_block_id": index.cfg["entry_block_id"], "instructions": {key: index.instructions[key] for key in sorted(selected_irs)},
                 "blocks": blocks, "edges": edges, "constraints": index.cfg.get("constraints", []), "declared_context_keys": index.cfg.get("declared_context_keys", []),
                 "data": {key: index.data[key] for key in sorted(data_ids)}, "operations": {key: index.operations[key] for key in index.sort_ops(op_ids)},
                 "locations": {key: raw.locations[key] for key in sorted(location_ids)}, "actions": {key: raw.actions[key] for key in sorted(selected_irs)},
                 "orders": {key: {field: raw.records[key][field] for field in ("order", "precedence")} for key in sorted(selected_irs) if key in raw.records},
                 "scopes": {key: index.scopes[key] for key in sorted(scope_ids)}, "links": {key: index.links[key] for key in sorted(link_ids)}}, "sinks": slices}
    return validate_doe_material(material)


def validate_doe_material(raw, *, facts=None) -> DoeMaterial:
    """Validate projected identities/references, optionally against their frozen facts."""
    if isinstance(raw, DoeMaterial):
        raw = raw.model_dump(mode="json")
    # JSON enum strings are the graph's wire form. JSON mode retains strict
    # integer/Boolean checks without requiring Python Enum objects from callers.
    parsed = DoeMaterial.model_validate_json(json.dumps(_json_object(raw), ensure_ascii=False, allow_nan=False))
    value = parsed.model_dump(mode="json")
    shared, contract = value["shared_info"], value["runtime_contract"]
    _checked_source(value["source"])
    if set(contract) != {"version", "rules", "sha256"}:
        raise ValueError("runtime contract must bind its complete rule text")
    checked_contract = validate_runtime_contract({key: contract[key] for key in ("version", "rules")})
    if contract["sha256"] != runtime_contract_binding(checked_contract)["sha256"]:
        raise ValueError("runtime contract digest mismatch")
    task = value["task"]
    if (task["basis"] == "declared_skill" and task["text"] is not None
            or task["basis"] == "user_request" and (task["text"] is None or not task["text"].strip())):
        raise ValueError("task basis and original text disagree")
    validate_data_records(list(shared["data"].values()))
    instructions, operations, data = shared["instructions"], shared["operations"], shared["data"]
    if set(shared["actions"]) != set(instructions) or not set(shared["orders"]) <= instructions.keys():
        raise ValueError("action coverage or order references disagree with selected IRs")
    if any(key != item["id"] for key, item in instructions.items()) or any(key != item["id"] for key, item in data.items()):
        raise ValueError("shared object identity mismatch")
    if shared["entry_block_id"] not in shared["blocks"]:
        raise ValueError("entry block is missing")
    for key, block in shared["blocks"].items():
        if key != block["block_id"] or not set(block["instruction_ids"]) <= instructions.keys():
            raise ValueError("block has invalid instruction references")
    membership = [ir_id for block in shared["blocks"].values() for ir_id in block["instruction_ids"]]
    if len(membership) != len(set(membership)) or set(membership) != set(instructions):
        raise ValueError("each selected instruction must belong to exactly one block")
    for edge in shared["edges"]:
        if not {edge["source_block_id"], edge["target_block_id"]} <= shared["blocks"].keys():
            raise ValueError("control edge references missing blocks")
    for location in shared["locations"].values():
        for ref in location["operand_refs"]:
            if ref["instruction_id"] not in instructions or ref["index"] >= len(instructions[ref["instruction_id"]][ref["side"] + "s"]):
                raise ValueError("location operand reference is outside the selected instructions")
    for key, operation in operations.items():
        if key != _id("op_", operation["position"]) or operation["position"]["instruction_id"] not in instructions:
            raise ValueError("operation identity or IR reference mismatch")
        if not _operation_data(operation) <= data.keys():
            raise ValueError("operation has dangling Data references")
        pos = operation["position"]
        if (pos["body_event_index"] is None) != (pos["instance_index"] is None):
            raise ValueError("element operation requires body and instance coordinates")
        if pos["instance_index"] is not None:
            scope = _id("scope_", [pos["instruction_id"], pos["event_index"], pos["instance_index"]])
            if scope not in shared["scopes"]:
                raise ValueError("operation scope is missing")
    for key, scope in shared["scopes"].items():
        if (key != _id("scope_", [scope["instruction_id"], scope["event_index"], scope["instance_index"]])
                or scope["instruction_id"] not in instructions or not {scope["collection"], scope["element"]} <= data.keys()):
            raise ValueError("invalid element scope")
        validate_element_membership(list(data.values()), scope["collection"], scope["element"])
    for key, link in shared["links"].items():
        if (key != _id("link_", link) or not {link["source"], link["target"]} <= operations.keys() | instructions.keys()
                or not set(link["data_ids"]) <= data.keys()):
            raise ValueError("invalid usage link")
        if link["kind"] == "result_use":
            if link["source"] not in instructions or link["target"] not in instructions:
                raise ValueError("result use must connect actual instructions")
            if (link["result"] not in {op["identifier"] for op in instructions[link["source"]]["outputs"]}
                    or link["result"] not in {op.get("identifier") for op in instructions[link["target"]]["inputs"] if op["type"] == "result"}):
                raise ValueError("result use refers to a nonexistent definition or use")
        elif link["kind"] == "result_binding":
            if (link["source"] not in operations or link["target"] not in instructions
                    or operations[link["source"]]["position"]["instruction_id"] != link["target"]
                    or link["result"] not in {op["identifier"] for op in instructions[link["target"]]["outputs"]}):
                raise ValueError("result binding refers to a nonexistent public output")
        elif link["source"] not in operations or link["target"] not in operations:
            raise ValueError("operation use must connect actual operations")
    seen, selected_ops = set(), set()
    for item in value["sinks"]:
        sink, boundary = item["sink"], item["sink"]["boundary"]
        if sink["id"] in seen or sink["id"] != _id("sink_", boundary):
            raise ValueError("duplicate or invalid sink identity")
        seen.add(sink["id"])
        if boundary["target"] not in shared["locations"]:
            raise ValueError("sink target is missing")
        for key in sink["operations"]:
            if key not in operations:
                raise ValueError("sink operation is missing")
            pos = operations[key]["position"]
            if any(pos[field] != boundary[field] for field in ("instruction_id", "event_index", "op_index", "body_event_index")):
                raise ValueError("sink operation coordinate mismatch")
            op = operations[key]
            record = op["record"]
            from skillflow.propagation.contracts.boundaries import classify_sink
            target = shared["locations"][boundary["target"]]
            if len(record["endpoints"]) != 1 or _location(record["endpoints"][0]) != _location(target):
                raise ValueError("sink target differs from its recorded endpoint")
            selected = classify_sink(record["op"], op["effect"], target,
                                     write_mode="replace" if record["inputs"] else "delete")
            if selected != (boundary["sink_type"], boundary["exposure_level"]):
                raise ValueError("sink classification differs from its actual operation")
            selected_ops.add(key)
        for section in (item["backward_slice"], item["usage_context"]):
            if not set(section["operations"]) <= operations.keys():
                raise ValueError("slice operation reference is missing")
        if (not set(item["backward_slice"]["data"]) <= data.keys()
                or not set(item["usage_context"]["instructions"]) <= instructions.keys()
                or not set(item["usage_context"]["links"]) <= shared["links"].keys()
                or not set(item["context"]["blocks"]) <= shared["blocks"].keys()
                or not set(item["context"]["scope_ids"]) <= shared["scopes"].keys()
                or not set(item["context"]["partial_ir_ids"]) <= shared["orders"].keys()
                or any(type(i) is not int or i < 0 or i >= len(shared["edges"]) for i in item["context"]["edge_indices"])):
            raise ValueError("slice has a dangling shared reference")
    # Detect dropped sinks even when loading the material on its own.
    from skillflow.propagation.contracts.boundaries import classify_sink
    identities = {_location(location): key for key, location in shared["locations"].items()}
    for key, operation in operations.items():
        record = operation["record"]
        if record["op"] not in {"deliver", "write"}:
            continue
        if record.get("when_input_index") is not None and not payload_inputs(record):
            continue
        endpoint = identities.get(_location(record["endpoints"][0])) if record["endpoints"] else None
        if endpoint is None:
            raise ValueError("interaction has no declared endpoint")
        classification = classify_sink(record["op"], operation["effect"], shared["locations"][endpoint],
                                       write_mode="replace" if record["inputs"] else "delete")
        if classification is not None and key not in selected_ops:
            raise ValueError("material omits a recorded sink")
    if facts is not None:
        source = _read_materials(facts)
        expected = prepare_doe_material(source)
        if expected.model_dump(mode="json") != value:
            raise ValueError("DOE material differs from the frozen propagation facts")
    return parsed

