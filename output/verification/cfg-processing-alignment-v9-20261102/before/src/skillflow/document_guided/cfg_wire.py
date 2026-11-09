"""Small model-facing CFG input; canonical graph semantics stay in the compiler."""
from copy import deepcopy
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from skillflow.graph.extraction.candidate import CandidateEdge, IRAnalysisCandidate
from skillflow.common.validation import StructuralValidationError, structural_error, schema_error
from skillflow.propagation.contracts.values import Text

CFG_RULES = {
    "operand_variant": "A literal is {type:literal,literal_value:<actual JSON>}. Other operand types supply a nonempty identifier and omit literal_value, even null. Public outputs are result operands. Instruction IDs, semantic_name and the context-key inventory are generated; omit them.",
    "external_acquisition_inputs": "An external acquisition explicitly consumes the real external_resource or previously produced result source. Resource identity is not its acquired contents or an invented positional argument.",
    "dispatch_inputs": "A branching or guarded dispatch names the actual condition operands. Edge text does not substitute for these inputs. Return and dispatch terminate their block and have no public outputs.",
    "cfg_connections": "Entry and every edge endpoint refer to existing blocks. Result names have one producer. Ordinary inputs consume defined versions; forward/backedge uses require a real graph path and cannot be read before definition inside the same block. Preserve independent capabilities and genuine returns/throws.",
    "acquisition_shape": "A context/external acquisition block has exactly one acquisition instruction followed by dispatch/return; context acquisition consumes its context_key entries. Ordinary computation uses data_source_kind=null. Do not create relay acquisitions or duplicate producers. Outgoing blocks end in dispatch and terminal blocks in return; preserve repeated source calls as different versions.",
    "source_scope": "Retain real entry points, independent components and cross-file links, not proximity/name-based edges. Each instruction is a meaningful action, version or boundary; declarations, examples and repeated explanations do not automatically become executable nodes. Put source restrictions at their real graph/block/instruction scope; they are not implemented guards or extra operations.",
    "source_span": "For code, metadata._source_span={file,start_line,end_line} selects exact inclusive frozen source lines. The program copies the original text into script_content; do not duplicate code or invent ranges. Other meaningful metadata is retained.",
    "loop_relations": "A real loop may retain its header, body, backedges and exits. Preserve the collection/member and initial/updated values needed for processing; do not invent a numeric cursor solely as CFG bookkeeping. Program loop regions and iteration identities are not model fields. Conditional merge membership must be expressible from actual predecessors, not only a prose phi description.",
}


def cfg_contract_rules():
    return "APPLICATION RULES (not response fields)\n" + "\n".join(
        f"- {name}: {text}" for name, text in CFG_RULES.items())


class Wire(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class LiteralOperand(Wire):
    type: Literal["literal"]
    literal_value: Any = Field(description="The actual JSON value, including explicit null when that is the source value.")


class ResultOperand(Wire):
    type: Literal["result"]
    identifier: Text


class ContextOperand(Wire):
    type: Literal["context_key"]
    identifier: Text


class ResourceOperand(Wire):
    type: Literal["external_resource"]
    identifier: Text


WireOperand = Annotated[LiteralOperand | ResultOperand | ContextOperand | ResourceOperand, Field(discriminator="type")]


class WireInstruction(Wire):
    opcode: str
    inputs: list[WireOperand] = Field(default_factory=list)
    outputs: list[ResultOperand] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class WireBlock(Wire):
    block_ref: str
    block_name: str | None = None
    data_source_kind: str | None = None
    instructions: list[WireInstruction] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)


class CFGWire(Wire):
    entry_block_ref: str
    blocks: list[WireBlock]
    edges: list[CandidateEdge] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    diagnostics: list[str] = Field(default_factory=list)


def normalize_cfg_wire(value):
    """Generate bookkeeping only, never connections, source kinds or producers."""
    diagnostics = []
    blocks = value.get("blocks", []) if isinstance(value, dict) else []
    edges = value.get("edges", []) if isinstance(value, dict) else []
    if isinstance(blocks, list):
        for index, block in enumerate(blocks):
            if not isinstance(block, dict) or not isinstance(block.get("instructions"), list) or not block["instructions"]:
                continue
            instructions = block["instructions"]
            acquisition, terminal = instructions[0], instructions[-1]
            if isinstance(acquisition, dict) and block.get("data_source_kind") == "external":
                inputs = acquisition.get("inputs", [])
                if isinstance(inputs, list) and not any(isinstance(item, dict) and item.get("type") in {"external_resource", "result"} for item in inputs):
                    diagnostics.extend(structural_error("external_acquisition_inputs", f"/blocks/{index}/instructions/0/inputs",
                        "external acquisition requires an explicit external_resource or previously produced result input; resource identity is not acquired content or a positional call argument").diagnostics)
            outgoing = [edge for edge in edges if isinstance(edge, dict) and edge.get("source_block_ref") == block.get("block_ref")] if isinstance(edges, list) else []
            if (isinstance(terminal, dict) and terminal.get("opcode") == "dispatch" and
                    (len(outgoing) > 1 or any(edge.get("condition_text") for edge in outgoing)) and not terminal.get("inputs")):
                diagnostics.extend(structural_error("dispatch_inputs", f"/blocks/{index}/instructions/{len(instructions)-1}/inputs",
                    "guarded or branching dispatch requires explicit condition dependencies; edge text does not declare data inputs").diagnostics)
    try:
        parsed = CFGWire.model_validate(value)
    except ValidationError as error:
        if not diagnostics:
            raise
        diagnostics.extend(schema_error(error, candidate=value, schema=CFGWire.model_json_schema()).diagnostics)
        raise StructuralValidationError(diagnostics) from error
    if diagnostics:
        raise StructuralValidationError(diagnostics)
    raw = parsed.model_dump(mode="json", exclude_unset=True)
    contexts, serial = [], 0
    for block in raw["blocks"]:
        if "block_name" not in block:
            block["block_name"] = block["block_ref"]
        for instruction in block.get("instructions", []):
            serial += 1
            instruction["instruction_ref"] = f"instruction_{serial:04d}"
            for operand in instruction.get("inputs", []):
                if operand["type"] == "context_key" and operand.get("identifier") not in contexts:
                    contexts.append(operand.get("identifier"))
    raw["declared_context_keys"] = contexts
    # Preserve omission versus explicit null. The canonical validators reject
    # malformed literals, source blocks and invalid source/consumer relations.
    return IRAnalysisCandidate.model_validate(deepcopy(raw)).model_dump(mode="json", exclude_unset=True)
