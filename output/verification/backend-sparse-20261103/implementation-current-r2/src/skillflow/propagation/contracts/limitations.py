"""Source-declared processing limits and explicit program validation barriers.

These records neither supply missing values nor prove source completeness. Task
gaps remain a separate, globally conservative requirement mechanism.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Literal

from pydantic import Field, model_validator

from skillflow.common.recording import canonical_sha256
from skillflow.common.source_evidence import extract_source_lines
from skillflow.common.validation import structural_error
from skillflow.propagation.contracts.task import TaskEvidence
from skillflow.propagation.contracts.values import StrictSpec, Text, Index


class ValidationGapError(StrictSpec):
    code: Text
    path: str
    message: Text


class ProcessingGap(StrictSpec):
    instruction_id: Text
    reason: Text
    evidences: list[TaskEvidence] = Field(default_factory=list)
    outputs: list[Index] = Field(default_factory=list)
    locations: list[Text] = Field(default_factory=list)
    control: bool = False
    unmodeled: bool = False
    origin: Literal["source", "validation"] = "source"
    validation_errors: list[ValidationGapError] = Field(default_factory=list)

    @model_validator(mode="after")
    def supported_origin(self):
        if self.origin == "source" and (not self.evidences or self.validation_errors):
            raise ValueError("a source processing gap requires physical evidence and no validation-origin errors")
        if self.origin == "validation" and not self.validation_errors:
            raise ValueError("a validation processing gap requires program validation diagnostics")
        if len(set(self.outputs)) != len(self.outputs) or len(set(self.locations)) != len(self.locations):
            raise ValueError("processing gap footprints must not repeat references")
        return self


def validation_gap(instruction_id, diagnostics, *, unmodeled=True, reason=None):
    """Build a program-owned barrier without inventing source evidence."""
    errors = [{key: deepcopy(row[key]) for key in ("code", "path", "message")}
              for row in diagnostics]
    return ProcessingGap(instruction_id=instruction_id, origin="validation", unmodeled=unmodeled,
        reason=reason or ("The processing fragment for this instruction failed structural validation; its semantics were not replaced by empty operations."
                          if unmodeled else "A semantic fragment for this instruction failed structural validation; known processing facts remain available with incomplete coverage."),
        validation_errors=errors).model_dump(mode="json")


def gap_id(gap):
    value = ProcessingGap.model_validate(gap).model_dump(mode="json")
    return "processing_gap_" + canonical_sha256(value)[:20]


def unmodeled_ids(annotation):
    gaps = annotation.get("processing_gaps", []) if isinstance(annotation, dict) else annotation.processing_gaps
    return {gap["instruction_id"] if isinstance(gap, dict) else gap.instruction_id
            for gap in gaps if (gap.get("unmodeled", False) if isinstance(gap, dict) else gap.unmodeled)}


def validate_processing_gaps(cfg, gaps, locations, *, source_files=None):
    """Check actual references and optional frozen source spans, without Task."""
    instructions = {ir["id"]: ir for block in cfg["blocks"].values() for ir in block["instructions"]}
    parsed = [ProcessingGap.model_validate(value) for value in gaps]
    seen = set()
    for index, gap in enumerate(parsed):
        path = f"/processing_gaps/{index}"
        if gap.instruction_id not in instructions:
            raise structural_error("processing_gap_instruction", path + "/instruction_id", "Processing gap references an absent instruction.")
        if any(output >= len(instructions[gap.instruction_id]["outputs"]) for output in gap.outputs):
            raise structural_error("processing_gap_output", path + "/outputs", "Processing gap references an absent CFG output.")
        if not set(gap.locations) <= set(locations):
            raise structural_error("processing_gap_location", path + "/locations", "Processing gap references an absent declared location.")
        identity = gap_id(gap)
        if identity in seen:
            raise structural_error("processing_gap_duplicate", path, "Duplicate processing gap.")
        seen.add(identity)
        if source_files is not None:
            for position, evidence in enumerate(gap.evidences):
                if evidence.file not in source_files:
                    raise structural_error("evidence_file", path + f"/evidences/{position}", "Processing gap evidence is not in the frozen Skill.")
                try:
                    extract_source_lines(source_files[evidence.file], evidence.start_line, evidence.end_line)
                except ValueError as error:
                    raise structural_error("evidence_source_range", path + f"/evidences/{position}", str(error)) from error
    return parsed


def check_processing_coverage(cfg, annotation):
    """An explicit barrier is the only permitted replacement for an IR spec."""
    if hasattr(annotation, "model_dump"):
        annotation = annotation.model_dump(mode="json")
    expected = {ir["id"] for block in cfg["blocks"].values() for ir in block["instructions"]}
    actual = set(annotation["ir_semantics"])
    absent = unmodeled_ids(annotation)
    if actual & absent or actual | absent != expected:
        raise structural_error("instruction_coverage", "/ir_semantics",
            "Every actual IR requires exactly one modeled specification or explicit unmodeled processing coverage.",
            current={"modeled": sorted(actual), "unmodeled": sorted(absent)}, allowed=sorted(expected))


def diagnostic_applies(diagnostic, instructions, *, scoped_instructions=None):
    """Program scopes supplement existing global/IR-local diagnostic semantics."""
    affected = diagnostic.get("affected_instruction_ids")
    if affected is not None:
        # Forward closure already accounts for producers. Reapplying it to
        # every backward ancestor would contaminate independent sibling outputs.
        return bool(set(affected) & set(instructions if scoped_instructions is None else scoped_instructions))
    return diagnostic.get("instruction_id") is None or diagnostic["instruction_id"] in instructions


def instruction_successors(cfg):
    """IR successors including empty blocks, without interpreting conditions."""
    blocks = cfg["blocks"]
    outgoing = {block: set() for block in blocks}
    for edge in cfg["edges"]:
        outgoing[edge["source_block_id"]].add(edge["target_block_id"])

    def starts(block, seen):
        if block in seen:
            return set()
        values = blocks[block]["instructions"]
        if values:
            return {values[0]["id"]}
        return {item for target in outgoing[block] for item in starts(target, seen | {block})}

    result = {}
    for block, value in blocks.items():
        instructions = value["instructions"]
        for position, ir in enumerate(instructions):
            result[ir["id"]] = ({instructions[position + 1]["id"]} if position + 1 < len(instructions)
                                else {item for target in outgoing[block] for item in starts(target, set())})
    return result


def reachable_instructions(cfg, start):
    successors = instruction_successors(cfg)
    reached, pending = set(), [start]
    while pending:
        ir = pending.pop()
        if ir not in reached:
            reached.add(ir)
            pending.extend(successors.get(ir, ()))
    return reached


def processing_impacts(cfg, annotation):
    """Conservative output-use, named-location and explicit-control closure.

    Named-location readers in sibling branches remain affected: their state
    relation is not justified by the originating IR's CFG descendants alone.
    No values or aliases are supplied to propagation by this coverage closure.
    """
    if hasattr(annotation, "model_dump"):
        annotation = annotation.model_dump(mode="json")
    if not annotation.get("processing_gaps"):
        return {}
    instructions = {ir["id"]: ir for block in cfg["blocks"].values() for ir in block["instructions"]}
    specs = annotation["ir_semantics"]
    locations = annotation["locations"]
    readers, writes = {}, {ir: set() for ir in instructions}
    consumers = {}
    for ir, instruction in instructions.items():
        for value in instruction["inputs"]:
            if value["type"] == "result":
                consumers.setdefault(value["identifier"], set()).add(ir)

    def operations(events):
        for event in events:
            if event.get("kind") == "for_each":
                yield from operations(event["body"])
            elif event.get("kind") == "processing":
                yield from operations(event["events"])
            else:
                yield from event.get("atomic_ops", [])

    for ir, spec in specs.items():
        for operation in operations(spec["events"]):
            if operation["op"] in {"read", "receive", "deliver", "write"}:
                location = operation["location"] if operation["op"] in {"read", "receive"} else operation["target"]
                readers.setdefault(location, set()).add(ir)
                if operation["op"] == "write":
                    writes[ir].add(location)
    for location, declaration in locations.items():
        for reference in declaration["operand_refs"]:
            if reference["side"] == "input":
                readers.setdefault(location, set()).add(reference["instruction_id"])
        for ir, instruction in instructions.items():
            if declaration["kind"] == "runtime_context" and any(value["type"] == "context_key"
                    and value["identifier"] == declaration["name"] for value in instruction["inputs"]):
                readers.setdefault(location, set()).add(ir)
    # Runtime-context/property locations with the same actual name may alias.
    aliases = {name: {other for other, value in locations.items()
                      if value["kind"] == location["kind"] and (value["name"] == location["name"]
                          or value["name"].startswith("symbolic:") or location["name"].startswith("symbolic:"))}
               for name, location in locations.items()}
    result = {}
    for gap in annotation.get("processing_gaps", []):
        source = gap["instruction_id"]
        affected = {source}
        pending_values = [instructions[source]["outputs"][index]["identifier"] for index in gap.get("outputs", [])]
        pending_locations = list(gap.get("locations", []))
        if gap.get("control") or gap.get("unmodeled") or not (pending_values or pending_locations):
            affected.update(reachable_instructions(cfg, source))
        expanded, seen_values, seen_locations = set(), set(), set()
        while pending_values or pending_locations or affected - expanded:
            for ir in sorted(affected - expanded):
                expanded.add(ir)
                pending_locations.extend(writes[ir])
                # The originating IR's explicitly selected outputs remain sparse.
                if ir != source or gap.get("locations") or gap.get("control") or gap.get("unmodeled") or not gap.get("outputs"):
                    pending_values.extend(value["identifier"] for value in instructions[ir]["outputs"])
                if instructions[ir]["opcode"] == "dispatch":
                    affected.update(reachable_instructions(cfg, ir))
            while pending_values:
                value = pending_values.pop()
                if value not in seen_values:
                    seen_values.add(value)
                    affected.update(consumers.get(value, ()))
            while pending_locations:
                location = pending_locations.pop()
                if location not in seen_locations:
                    seen_locations.add(location)
                    for alias in aliases.get(location, {location}):
                        affected.update(readers.get(alias, ()))
        result[gap_id(gap)] = sorted(affected)
    return result
