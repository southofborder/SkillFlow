"""Versioned interpretation rules shared by semantic review and feedback.

This contract explains existing recorded IR facts. It adds neither execution
semantics to open operations nor a programmatic proof of model judgments.
"""

from __future__ import annotations

import hashlib
import json
from typing import Literal, get_args


CONTRACT_VERSION = "skill-ir-semantic-contract-v3"
AUDIT_SCHEMA_VERSION = 4
# Reading perspectives, not response categories or a semantic completeness test.
CHECKPOINTS = (
    {"id": "normative_scope", "label": "Requirement modality and scope"},
    {"id": "actions_objects", "label": "Actions and objects"},
    {"id": "data_bindings", "label": "Data sources and bindings"},
    {"id": "guards_exceptions", "label": "Conditions and exceptions"},
    {"id": "order_dependencies", "label": "Order and dependencies"},
    {"id": "counts_termination", "label": "Counts and termination"},
    {"id": "grounding_consistency", "label": "Reverse grounding and consistency"},
)
ConservativeRuleId = Literal["DEP-MERGE", "DEP-SOURCE"]
CONSERVATIVE_RULE_IDS = get_args(ConservativeRuleId)

# Provenance is a reference to the existing definition, not a claim that Lean
# proves the prose interpretation or that a model follows it correctly.
RULES = (
    {"id": "IR-SOURCE", "text":
     "Distinguish the source entry from the acquired value. A context_key naming a request or environment container can identify "
     "the source of a field returned by an acquisition; this representation alone asserts neither a whole-container read nor model visibility. "
     "Check the source entry, target field or getter, result identity, and subsequent argument binding together. Preserve explicit key-only "
     "getters, local processing, and isolation boundaries. Explicit whole-read-then-select actions must remain locatable with their actual "
     "intermediate result; do not demand extra source-level steps for an execution-model assumption when the source describes one acquisition. "
     "Content newly returned from a tool or external collection has an acquisition boundary distinct from its request dependencies; do not "
     "infer networking merely from that boundary or turn an explicitly pure computation into an acquisition. A missing explicit source cannot "
     "be excused by conservative dependency rules. Review only source and controlled facts, not unprovided security labels or propagation results.",
     "provenance": ["extraction/prompt.py:SOURCE ENTRY AND ACQUIRED VALUE", "ir/operand.py:OperandType"]},
    {"id": "IR-RESOURCE", "text":
     "external_resource identifies a file, tool, API, or service; it does not necessarily mean a remote or network resource. "
     "Local files may also use this type. A resource locator is not automatically a business argument. "
     "Check the actual type, location, and purpose; do not infer network transmission or extra arguments from the type name alone.",
     "provenance": ["ir/operand.py:OperandType", "extraction/prompt.py:For external acquisition"]},
    {"id": "IR-CONTROL", "text":
     "dispatch and return are fixed control terminators. dispatch ends the current block; outgoing edges connect successors, "
     "and inputs record values used to choose a branch. return ends the current path; inputs record returned values, "
     "and it may return no value. Neither produces result outputs. "
     "Do not classify these IR terms as additions or unknown merely because the source does not spell them out; "
     "still check the actual inputs, outgoing edges, conditions, and returned-value identities. "
     "return alone does not mean displaying or sending content to the user.",
     "provenance": ["ir/instruction.py:IRInstruction.validate_outputs", "extraction/prompt.py:USING RESULTS"]},
    {"id": "IR-IDENTITY", "text":
     "A result links to its unique definition by the actual identifier; semantic_name, block names, and similar wording cannot "
     "replace result identity. Initial-attempt, retry, and fallback results are not interchangeable. "
     "Check operand positions and instruction order as recorded; do not treat them as interchangeable sets.",
     "provenance": ["ir/operand.py:Operand", "extraction/prompt.py:USING RESULTS"]},
    {"id": "IR-PATH", "text":
     "Edges record connections and condition text; they do not prove that all paths are executable, conditions are always true, "
     "or loops terminate. Structural validation does not guarantee that all inputs are simultaneously available on every path. "
     "Do not infer a semantic error merely because a result is produced on only some paths; merge blocks may reference branch "
     "definitions, and loops may reference backedge definitions. Do not invent implicit phi, runtime value selection, or optional-argument mechanisms.",
     "provenance": ["ir/validation.py:module docstring", "extraction/prompt.py:USING RESULTS"]},
    {"id": "IR-DECLARATION", "text":
     "Graph-, block-, and instruction-level constraints are declarations at their respective scopes; they do not mean the corresponding "
     "operations have been recorded or that execution will succeed. Conflicts between declarations and operations may be reported. "
     "Block titles, names, and declarations cannot fill missing steps; source-explicit steps changing data content, destination, "
     "or execution conditions must each be locatable.",
     "provenance": ["extraction/prompt.py:CONSTRAINTS", "ir/instruction.py:IRInstruction.constraints"]},
    {"id": "IR-OPAQUE", "text":
     "Ordinary opcodes are open operation names. Check explicit wording and interfaces; do not guess unrecorded internal steps from names. "
     "Scripts retain black-box modeling: check explicit interfaces, inputs, outputs, and recorded external side effects. "
     "Preserving complete metadata or embedded source code does not mean internal behavior is explicitly modeled or execution succeeds.",
     "provenance": ["extraction/prompt.py:All opcodes are semantic strings", "ir/instruction.py:IRInstruction.metadata"]},
    {"id": "DEP-MERGE", "text":
     "Merge dependencies may be conservatively retained: when multiple existing result sources are candidates and the source text and "
     "recorded control relations support them, they may be recorded as a candidate dependency set. Cite at least two existing operand/definition "
     "fact IDs, explain their support, and state the lost path distinctions. This does not claim simultaneous argument use, exact value selection "
     "implemented in the graph, or transmission of every candidate. Do not classify a lack of more precise value selection alone as omitted, mistranslated, or unknown.",
     "provenance": ["extraction/prompt.py:Branch example: acquire only on one path, then reference both paths after the merge",
                    "ir/validation.py:module docstring"]},
    {"id": "DEP-SOURCE", "text":
     "Source dependencies may be conservatively retained: when multiple candidate sources already exist in the graph and the source text and "
     "current records support their possible dependencies, but finer distinctions cannot be made, retain that supported candidate set. "
     "Cite existing operand/definition facts individually and describe the lost source distinctions. Do not add sources or describe all candidates "
     "as actually read, simultaneous arguments, or necessarily transmitted.",
     "provenance": ["ir/operand.py:Operand", "extraction/prompt.py:USING RESULTS"]},
    {"id": "DEP-LIMIT", "text":
     "Conservative rules apply only to data-source and dependency precision. They cannot relax actions, execution paths, business arguments, "
     "return identity, counts, prohibitions, or scope; they cannot hide missing correct sources, explicitly wrong returned results, explicit extra "
     "arguments, or prohibited transfers. Containers, constraints, metadata, type fields, or semantic labels alone are not candidate-source evidence; "
     "do not use the source text to invent absent graph facts. Select complete operands or identifier facts; the definition and use of one result "
     "are not two independent candidate sources. Conservative acceptance must be explicit in this review; the program must not automatically "
     "change unknown to represented.",
     "provenance": ["semantic review scope:explicit requirements remain binding"]},
    {"id": "REVIEW-MODALITY", "text":
     "Distinguish requirements, permissions, prohibitions, examples, background, and their scopes. Checking existence to evaluate a condition "
     "does not automatically mean format/validity checking or normalization. 'An action is not required' does not automatically mean 'the action "
     "is prohibited'. Valid representation scaffolding is not automatically an added business step. Do not resolve source ambiguity or conflicts "
     "by model preference; a safety judgment cannot replace a fidelity review.",
     "provenance": ["extraction/prompt.py:NAMING OPERATIONS", "extraction/prompt.py:CONSTRAINTS"]},
    {"id": "REVIEW-UNIT", "text":
     "Organize findings by semantic relationships; related behavior, conditions, and results may be grouped without a fixed granularity or one-category "
     "classification. If any part of a combined requirement differs, describe that difference; do not mark the whole finding represented to hide "
     "a local error. Split findings when different conclusions need separate expression. An action's presence does not establish its objects, bindings, "
     "conditions, counts, order, or scope. Explain the source requirement, controlled record, differences, and evidence; check each conclusion against "
     "its evidence and the other findings. Neither overall similarity nor ID coverage replaces judgment.",
     "provenance": ["semantic review obligation policy"]},
)

_CONTRACT_RECORD = {
    "version": CONTRACT_VERSION,
    "checkpoints": CHECKPOINTS,
    "rules": RULES,
}
CONTRACT_SHA256 = hashlib.sha256(json.dumps(
    _CONTRACT_RECORD, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    allow_nan=False,
).encode("utf-8")).hexdigest()
CONTRACT_TEXT = "\n".join([
    f"IR interpretation and item-by-item review contract: {CONTRACT_VERSION}",
    "These rules explain existing records and review boundaries; they add no business requirements to the current Skill.",
    *(f"[{rule['id']}] {rule['text']}" for rule in RULES),
    "Seven reading checkpoints (no per-category form or finding classification is required):",
    *(f"{item['id']}: {item['label']}" for item in CHECKPOINTS),
])


def contract_binding() -> dict[str, str]:
    """A fresh identity record for a run manifest or checked review result."""
    return {"contract_version": CONTRACT_VERSION, "contract_sha256": CONTRACT_SHA256}
