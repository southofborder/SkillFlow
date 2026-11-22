"""Compile source-located facts into a canonical CFG, retaining incomplete drafts separately."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from dataclasses import dataclass, field
import json
import re
from typing import Annotated, Any, Literal

from pydantic import Field, ValidationError

from skillflow.common.recording import canonical_sha256
from skillflow.common.source_evidence import (
    SourceRef, StrictRecord, Text, extract_source_lines, json_pointer, validate_source_ref,
)
from skillflow.graph.extraction.candidate import IRAnalysisCandidate
from skillflow.graph.extraction.compiler import allocate_candidate_ids, compile_candidate
from skillflow.graph.ir.cfg import ControlFlowGraph

IDENTITY = "skillflow-graph-facts-v1"


class ResultValue(StrictRecord):
    result: Text


class ContextValue(StrictRecord):
    context_key: Text


class ResourceValue(StrictRecord):
    external_resource: Text


class LiteralValue(StrictRecord):
    literal: Any


Value = ResultValue | ContextValue | ResourceValue | LiteralValue


class Action(StrictRecord):
    ref: Text
    opcode: Text
    inputs: list[Value]
    outputs: list[Text]
    source: SourceRef | None
    constraints: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Exit(StrictRecord):
    source: SourceRef | None
    constraints: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Jump(Exit):
    kind: Literal["jump"]
    target: Text


class Arm(StrictRecord):
    target: Text
    condition: Text | None


class Branch(Exit):
    kind: Literal["branch"]
    conditions: list[Value] = Field(min_length=1)
    arms: list[Arm] = Field(min_length=1)


class Return(Exit):
    kind: Literal["return"]
    values: list[Value]


ExitFact = Annotated[Jump | Branch | Return, Field(discriminator="kind")]


class Block(StrictRecord):
    ref: Text
    source_kind: Literal["normal", "context", "external"]
    operations: list[Action]
    exit: ExitFact
    name: Text | None = None
    constraints: list[str] = Field(default_factory=list)


class Facts(StrictRecord):
    entry: Text
    blocks: list[Block] = Field(min_length=1)
    constraints: list[str] = Field(default_factory=list)


GRAPH_FACTS_SCHEMA = Facts.model_json_schema()
# The nullable variant is reserved for importing old accepted records internally.
for _name in ("Action", "Jump", "Branch", "Return"):
    GRAPH_FACTS_SCHEMA["$defs"][_name]["properties"]["source"] = {"$ref": "#/$defs/SourceRef"}
_arm_condition = GRAPH_FACTS_SCHEMA["$defs"]["Arm"]["properties"]["condition"]
GRAPH_FACTS_SCHEMA["$defs"]["Arm"]["properties"]["condition"] = _arm_condition["anyOf"][0]
GRAPH_FACTS_SCHEMA["$defs"]["Branch"]["properties"]["arms"]["maxItems"] = 2


@dataclass(frozen=True)
class GraphAssembly:
    facts: dict
    candidate: dict | None
    cfg: dict | None
    slots: dict
    gaps: list
    id_map: dict
    source_sha256: str
    origin: str = "model_facts"
    legacy_cfg: dict | None = None
    patch_diagnostics: list = field(default_factory=list)

    def to_receipt(self):
        return {"identity": IDENTITY, "origin": self.origin, "source_sha256": self.source_sha256,
            "facts_sha256": canonical_sha256(self.facts),
            "candidate_sha256": _digest(self.candidate), "cfg_sha256": _digest(self.cfg),
            "legacy_cfg_sha256": _digest(self.legacy_cfg), "facts": deepcopy(self.facts),
            "id_map": deepcopy(self.id_map), "slots": deepcopy(self.slots), "gaps": deepcopy(self.gaps),
            "patch_diagnostics": deepcopy(self.patch_diagnostics)}


def _digest(value):
    return None if value is None else canonical_sha256(value)


def _name(value):
    return isinstance(value, str) and value.strip() and value == value.strip()


def source_digest(files):
    if not isinstance(files, dict) or not files or any(
            not _name(key) or not isinstance(value, str) for key, value in files.items()):
        raise ValueError("Expected a complete frozen source file table")
    return canonical_sha256(files)


def instruction_ref(block, operation=None):
    return (json_pointer("blocks", block, "exit") if operation is None
            else json_pointer("blocks", block, "operations", operation))


def _raw_at(value, path):
    for part in path:
        if isinstance(value, dict) and part in value:
            value = value[part]
        elif isinstance(value, list) and type(part) is int and 0 <= part < len(value):
            value = value[part]
        else:
            return False, None
    return True, value


def field_slot(facts, path):
    """Return a narrow edit permission with an unambiguous logical owner."""
    if not path:
        return None
    if path == ("entry",):
        owner = ["entry"]
    elif len(path) >= 3 and path[0] == "blocks" and type(path[1]) is int:
        blocks = facts.get("blocks")
        present, block = _raw_at(facts, path[:2])
        ref = block.get("ref") if present and isinstance(block, dict) else None
        if not _name(ref) or path[2] == "ref" or sum(
                isinstance(row, dict) and row.get("ref") == ref for row in blocks) != 1:
            return None
        owner = ["block", ref, *path[2:]]
        if path[2] == "operations" and len(path) >= 4:
            present, op = _raw_at(facts, path[:4])
            op_ref = op.get("ref") if present and isinstance(op, dict) else None
            if (not _name(op_ref) or (len(path) >= 5 and path[4] == "ref")
                    or sum(isinstance(row, dict) and row.get("ref") == op_ref
                           for row in block["operations"]) != 1):
                return None
            owner = ["action", ref, op_ref, *path[4:]]
    else:
        return None
    present, prior = _raw_at(facts, path)
    return {"slot_id": "cfg_slot_" + canonical_sha256(owner)[:24], "kind": "field",
        "path": list(path), "target": json_pointer(*owner),
        "present": present, **({"old_value": deepcopy(prior)} if present else {})}


def _validation_path(raw, loc):
    """Remove Pydantic union implementation names from a response locator."""
    result, value = [], raw
    for part in loc:
        if isinstance(value, dict) and (part == value.get("kind") or part in {
                "ResultValue", "ResourceValue", "ContextValue", "LiteralValue"}):
            continue
        if isinstance(value, dict) and part in value:
            value = value[part]
        elif isinstance(value, list) and type(part) is int and 0 <= part < len(value):
            value = value[part]
        else:
            result.append(part)
            break
        result.append(part)
    return tuple(result)


def _add_gap(facts, slots, gaps, code, path, message, *, editable=True):
    slot = field_slot(facts, path) if editable else None
    if slot is not None:
        slots[slot["slot_id"]] = slot
    row = {"code": code, "path": json_pointer(*path), "message": message}
    if slot is not None:
        row["slot_id"] = slot["slot_id"]
    if row not in gaps:
        gaps.append(row)


def _validate_facts(raw, slots, gaps):
    try:
        return Facts.model_validate(raw)
    except ValidationError as error:
        # A union error at an operand is repaired by replacing the single operand,
        # not by editing a field that exists only in another union alternative.
        for row in error.errors():
            loc = tuple(row["loc"])
            if any(part in {"ResultValue", "ResourceValue", "ContextValue", "LiteralValue"}
                   for part in loc if isinstance(part, str)):
                prefix = next(i for i, part in enumerate(loc) if part in {
                    "ResultValue", "ResourceValue", "ContextValue", "LiteralValue"})
                path = _validation_path(raw, loc[:prefix])
                _add_gap(raw, slots, gaps, "invalid_operand", path,
                         "Supply exactly one typed operand value with its actual identity or literal.")
                continue
            path = _validation_path(raw, loc)
            _add_gap(raw, slots, gaps, row["type"], path, row["msg"],
                     editable=row["type"] != "extra_forbidden")
        return None


def _operand(value):
    selector, content = next(iter(value.model_dump(mode="json").items()))
    return ({"type": "literal", "literal_value": content} if selector == "literal"
            else {"type": selector, "identifier": content})


def _lower(facts, raw, *, files, slots, gaps, legacy_cfg):
    blocks, edges, contexts = [], [], []
    previous = {(block["block_id"], insn["id"]): insn for block in (legacy_cfg or {}).get("blocks", {}).values()
                for insn in block["instructions"]}
    known_blocks = Counter(block.ref for block in facts.blocks)
    known_outputs = Counter(value for block in facts.blocks
                            for action in block.operations for value in action.outputs)
    legacy_edges = {}
    for edge in (legacy_cfg or {}).get("edges", []):
        legacy_edges.setdefault(edge["source_block_id"], []).append((edge["target_block_id"], edge["condition_text"]))
    locators, inherited_refs = {}, {}
    if facts.entry not in known_blocks:
        _add_gap(raw, slots, gaps, "entry_not_found", ("entry",),
                 "The entry must refer to a declared block.")

    def add_edge(ref, target, condition, path):
        edges.append({"source_block_ref": ref, "target_block_ref": target, "condition_text": condition})
        if target not in known_blocks:
            _add_gap(raw, slots, gaps, "target_not_found", path, "This target does not identify a declared block.")

    def instruction(ref, opcode, values, outputs, fact, path, prior_id):
        metadata = deepcopy(fact.metadata)
        legacy = previous.get((facts.blocks[path[1]].ref, prior_id))
        if fact.source is None:
            if legacy is None:
                _add_gap(raw, slots, gaps, "source_required", (*path, "source"),
                         "An authored action or exit needs its exact frozen source location.")
            elif metadata != legacy["metadata"]:
                _add_gap(raw, slots, gaps, "source_required", (*path, "source"),
                         "Changed source metadata needs a new frozen source location.")
        else:
            try:
                span = validate_source_ref(fact.source.model_dump(), files)
            except ValueError as error:
                _add_gap(raw, slots, gaps, "source_span", (*path, "source"), str(error))
            else:
                generated = {"script_content", "_source_span", "source_span"}
                if legacy is not None and metadata == legacy["metadata"]:
                    metadata = {name: content for name, content in metadata.items() if name not in generated}
                elif generated & metadata.keys():
                    _add_gap(raw, slots, gaps, "generated_metadata", (*path, "metadata"),
                             "Source span and exact script text are generated by the program.")
                metadata["source_span"] = span.model_dump()
                metadata["script_content"] = extract_source_lines(files[span.file], span.start_line, span.end_line)
        inputs = [_operand(value) for value in values]
        input_field = "conditions" if isinstance(fact, Branch) else "values" if isinstance(fact, Return) else "inputs"
        for index, operand in enumerate(inputs):
            kind = operand["type"]
            if kind == "result" and operand["identifier"] not in known_outputs:
                _add_gap(raw, slots, gaps, "result_not_found", (*path, input_field, index),
                         "This input must name its declared result producer.")
            if kind == "context_key" and operand["identifier"] not in contexts:
                contexts.append(operand["identifier"])
        output_operands = [{"type": "result", "identifier": value} for value in outputs]
        if legacy is not None:
            inherited_refs[ref] = legacy
        return {"instruction_ref": ref, "opcode": opcode, "inputs": inputs,
            "outputs": output_operands, "constraints": fact.constraints, "metadata": metadata}

    for bi, block in enumerate(facts.blocks):
        path = ("blocks", bi)
        if not _name(block.ref) or known_blocks[block.ref] != 1:
            _add_gap(raw, slots, gaps, "ambiguous_block", (*path, "ref"),
                     "Block references must be unique and nonempty without surrounding space.", editable=False)
        refs = Counter(op.ref for op in block.operations)
        operations = []
        local_definitions = {output: index for index, op in enumerate(block.operations) for output in op.outputs
                             if known_outputs[output] == 1}
        for oi, op in enumerate(block.operations):
            op_path = (*path, "operations", oi)
            ref = instruction_ref(block.ref, op.ref)
            if not _name(op.ref) or refs[op.ref] != 1:
                _add_gap(raw, slots, gaps, "ambiguous_action", (*op_path, "ref"),
                         "Action references must be unique within the block.", editable=False)
            if op.opcode.strip() in {"dispatch", "return"}:
                _add_gap(raw, slots, gaps, "generated_exit", (*op_path, "opcode"),
                         "Describe exits only in the exit fact. The program emits its terminator.")
            for index, output in enumerate(op.outputs):
                if not _name(output) or known_outputs[output] != 1:
                    _add_gap(raw, slots, gaps, "ambiguous_result", (*op_path, "outputs", index),
                             "Each result reference must have one producer and no surrounding space.", editable=False)
            for index, value in enumerate(op.inputs):
                if isinstance(value, ResultValue) and local_definitions.get(value.result, -1) >= oi:
                    _add_gap(raw, slots, gaps, "result_read_before_definition", (*op_path, "inputs", index),
                             "This input refers to an action result at or after its own use in the same block.")
                if isinstance(value, ContextValue) and not (block.source_kind == "context" and oi == 0):
                    _add_gap(raw, slots, gaps, "context_acquisition_only", (*op_path, "inputs", index),
                             "A raw context key belongs to its context acquisition, not an ordinary use.")
            operations.append(instruction(ref, op.opcode, op.inputs, op.outputs, op, op_path, op.ref))
            locators[(bi, oi)] = op_path
        exit, exit_path = block.exit, (*path, "exit")
        if isinstance(exit, Jump):
            add_edge(block.ref, exit.target, None, (*exit_path, "target"))
        elif isinstance(exit, Branch):
            actual_arms = [(arm.target, arm.condition) for arm in exit.arms]
            if actual_arms != legacy_edges.get(block.ref):
                if len(exit.arms) > 2:
                    _add_gap(raw, slots, gaps, "binary_dispatch", (*exit_path, "arms"),
                             "The authored branch must name at most two outgoing arms.")
                for ai, arm in enumerate(exit.arms):
                    if arm.condition is None:
                        _add_gap(raw, slots, gaps, "guarded_arm", (*exit_path, "arms", ai, "condition"),
                                 "Supply the actual condition for this guarded arm.")
            for ai, arm in enumerate(exit.arms):
                add_edge(block.ref, arm.target, arm.condition, (*exit_path, "arms", ai, "target"))
        values = exit.values if isinstance(exit, Return) else exit.conditions if isinstance(exit, Branch) else []
        for vi, value in enumerate(values):
            if isinstance(value, ContextValue):
                _add_gap(raw, slots, gaps, "context_acquisition_only",
                         (*exit_path, "values" if isinstance(exit, Return) else "conditions", vi),
                         "The exit must refer to the acquired result, not a raw context key.")
        legacy_block = (legacy_cfg or {}).get("blocks", {}).get(block.ref, {})
        legacy_ops = legacy_block.get("instructions", [])
        legacy_exit = legacy_ops[-1]["id"] if legacy_ops else None
        operations.append(instruction(instruction_ref(block.ref), "return" if isinstance(exit, Return) else "dispatch",
            values, [], exit, exit_path, legacy_exit))
        locators[(bi, len(operations) - 1)] = exit_path
        kind = None if block.source_kind == "normal" else block.source_kind
        if kind is not None:
            if len(block.operations) != 1:
                _add_gap(raw, slots, gaps, "acquisition_shape", (*path, "operations"),
                         "A source block needs exactly one acquisition before its exit.")
            elif not block.operations[0].outputs:
                _add_gap(raw, slots, gaps, "acquisition_output", (*path, "operations", 0, "outputs"),
                         "This source acquisition needs a result output.")
        if kind == "context" and len(block.operations) == 1 and (not block.operations[0].inputs
                or any(not isinstance(value, ContextValue) for value in block.operations[0].inputs)):
            _add_gap(raw, slots, gaps, "context_acquisition_inputs", (*path, "operations", 0, "inputs"),
                     "Context acquisition needs its actual context keys.")
        if kind == "external" and (not operations[0]["inputs"] or not any(
                item["type"] in {"result", "external_resource"} for item in operations[0]["inputs"])):
            _add_gap(raw, slots, gaps, "external_acquisition_inputs",
                     (*path, "operations", 0, "inputs") if len(operations) > 1 else (*path, "operations"),
                     "External acquisition needs an actual resource or prior result input.")
        blocks.append({"block_ref": block.ref, "block_name": block.name or block.ref,
            "data_source_kind": kind, "instructions": operations, "constraints": block.constraints})

    if legacy_cfg is not None:
        contexts = list(dict.fromkeys([*legacy_cfg["declared_context_keys"], *contexts]))
        order = {(edge["source_block_id"], edge["target_block_id"], edge["condition_text"]): i
                 for i, edge in enumerate(legacy_cfg["edges"])}
        edges.sort(key=lambda row: order.get((row["source_block_ref"], row["target_block_ref"],
                                              row["condition_text"]), len(order)))
    return {"entry_block_ref": facts.entry, "blocks": blocks, "edges": edges,
            "constraints": facts.constraints, "declared_context_keys": contexts}, locators, inherited_refs


def _compile_gap_path(row, locators):
    parts = tuple(int(value) if value.isdecimal() else value for value in re.findall(r"[^.\[\]]+", row.path))
    if parts and parts[0] == "blocks" and len(parts) >= 4 and parts[2] == "instructions":
        path = locators.get((parts[1], parts[3]))
        if path is not None:
            suffix = parts[4:]
            if suffix and suffix[0] == "inputs" and path[-1] == "exit":
                # The precise selector depends on whether the exit is guarded or returns.
                return path
            return (*path, *suffix)
    if parts == ("entry_block_ref",):
        return ("entry",)
    return None


def _restore_legacy_labels(cfg, inherited_refs):
    if not inherited_refs:
        return
    for block in cfg["blocks"].values():
        for op in block["instructions"]:
            legacy = inherited_refs.get(op["draft_instruction_id"])
            if legacy is None:
                continue
            op["draft_instruction_id"] = legacy["draft_instruction_id"]
            for side in ("inputs", "outputs"):
                for item, old in zip(op[side], legacy[side]):
                    if (item["type"], item.get("identifier")) != (old["type"], old.get("identifier")):
                        continue
                    if old.get("semantic_name") is None:
                        item.pop("semantic_name", None)
                    else:
                        item["semantic_name"] = old["semantic_name"]


def assemble_graph_facts(value, *, files, canonical_ids=None, legacy_cfg=None):
    """Lower complete facts and revalidate the entire CFG without synthesizing semantics."""
    sha = source_digest(files)
    if not isinstance(value, dict):
        raise ValueError("Graph facts require a JSON object")
    canonical_sha256(value)
    raw, slots, gaps = deepcopy(value), {}, []
    origin = "accepted_cfg" if legacy_cfg is not None else "model_facts"
    prior = deepcopy(canonical_ids or {})
    facts = _validate_facts(raw, slots, gaps)
    if facts is None:
        return GraphAssembly(raw, None, None, slots, gaps, prior, sha, origin, legacy_cfg)
    candidate, locators, inherited_refs = _lower(facts, raw, files=files, slots=slots, gaps=gaps, legacy_cfg=legacy_cfg)
    if gaps:
        return GraphAssembly(raw, None, None, slots, gaps, prior, sha, origin, legacy_cfg)
    try:
        parsed = IRAnalysisCandidate.model_validate(candidate)
    except ValidationError as error:
        for row in error.errors():
            path = tuple(row["loc"])
            if len(path) >= 4 and path[0] == "blocks" and path[2] == "instructions":
                locator = locators.get((path[1], path[3]))
                if locator is not None:
                    _add_gap(raw, slots, gaps, row["type"], locator, row["msg"])
                    continue
            _add_gap(raw, slots, gaps, row["type"], (), row["msg"], editable=False)
        return GraphAssembly(raw, None, None, slots, gaps, prior, sha, origin, legacy_cfg)
    ids = allocate_candidate_ids(parsed, canonical_ids)
    compiled = compile_candidate(parsed, canonical_ids=ids)
    for row in compiled.diagnostics:
        path = _compile_gap_path(row, locators)
        _add_gap(raw, slots, gaps, row.code, path or (), row.message, editable=path is not None)
        if path is None:
            gaps[-1]["compiler_path"] = row.path
    cfg = None
    if compiled.ok and not gaps:
        cfg = json.loads(compiled.cfg.to_json())
        _restore_legacy_labels(cfg, inherited_refs)
        ControlFlowGraph.model_validate(cfg).validate_integrity()
    return GraphAssembly(raw, candidate, cfg, slots, gaps, ids, sha, origin, legacy_cfg)


def _fact_input(operand):
    return ({"literal": deepcopy(operand["literal_value"])} if operand["type"] == "literal"
            else {operand["type"]: operand["identifier"]})


def from_accepted_cfg(cfg, *, files):
    """Bind old canonical material without representing it as new model-authored facts."""
    verified = ControlFlowGraph.model_validate(cfg)
    verified.validate_integrity()
    canonical = json.loads(verified.to_json())
    if canonical != cfg:
        raise ValueError("Only an exact, already-canonical CFG can supply an accepted repair base")
    cfg = canonical
    facts = {"entry": cfg["entry_block_id"], "constraints": cfg["constraints"], "blocks": []}
    ids = {"blocks": {}, "instructions": {}, "results": {}}
    outgoing = {}
    for edge in cfg["edges"]:
        outgoing.setdefault(edge["source_block_id"], []).append(edge)
    for ref, block in cfg["blocks"].items():
        ids["blocks"][ref] = ref
        draft = {"ref": ref, "source_kind": block["data_source_kind"] or "normal",
                 "name": block["block_name"], "constraints": block["constraints"], "operations": []}
        for row in block["instructions"][:-1]:
            action = {"ref": row["id"], "opcode": row["opcode"], "source": None,
                "inputs": [_fact_input(value) for value in row["inputs"]],
                "outputs": [value["identifier"] for value in row["outputs"]],
                "constraints": row["constraints"], "metadata": row["metadata"]}
            draft["operations"].append(action)
            ids["instructions"][instruction_ref(ref, row["id"])] = row["id"]
            ids["results"].update((value, value) for value in action["outputs"])
        if not block["instructions"]:
            raise ValueError("No repairable semantic exit is available for an empty accepted block")
        terminal = block["instructions"][-1]
        ids["instructions"][instruction_ref(ref)] = terminal["id"]
        exit = {"source": None, "constraints": terminal["constraints"], "metadata": terminal["metadata"]}
        edges = outgoing.get(ref, [])
        inputs = [_fact_input(value) for value in terminal["inputs"]]
        if terminal["opcode"] == "return":
            exit.update(kind="return", values=inputs)
        elif len(edges) == 1 and edges[0]["condition_text"] is None and not inputs:
            exit.update(kind="jump", target=edges[0]["target_block_id"])
        else:
            exit.update(kind="branch", conditions=inputs,
                arms=[{"target": row["target_block_id"], "condition": row["condition_text"]} for row in edges])
        draft["exit"] = exit
        facts["blocks"].append(draft)
    assembly = assemble_graph_facts(facts, files=files, canonical_ids=ids, legacy_cfg=cfg)
    if assembly.cfg != cfg:
        raise ValueError("Cannot reconstruct the accepted CFG exactly from editable facts")
    return assembly
