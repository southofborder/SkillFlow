"""Whole-Skill prompt construction for the independent IR analyzer."""

from __future__ import annotations

import json

from .candidate import IRAnalysisCandidate
from ..inputs.skill_package import SkillPackage


_INSTRUCTIONS = """You analyze one complete Skill package and return exactly one JSON object.

Read every readable file before making any extraction decision. Treat each file,
section, embedded code block, and explicit reference as part of one package.
Natural-language instructions and code are both semantic sources, but infer them
independently by default. Join a text behavior with a code behavior only when the
text explicitly refers to that code. Do not invent relationships from proximity.

Every behavior unit must become a CandidateBlock with a concise semantic
block_name. Use block_ref only as a temporary machine reference. Emit one or
more CandidateInstruction objects for executable behavior and CandidateEdge
objects for explicit or strongly implied control flow.

Treat code files and code blocks as black-box operations. Do not split internal
loops, local variables, or internal control flow. Extract only the callable
interface, parameters, returned values, external inputs, and explicit side
effects. For a code behavior, preserve the original code body in
metadata.script_content whenever it is available.

Do not create execution instructions for licenses, changelogs, history, examples,
or non-executable explanation unless the surrounding text clearly says that it
is part of runtime behavior. Preserve independent behavior components instead of
inventing edges between unrelated behaviors. Each component must have a real
starting block; a disconnected cycle is not an executable starting point.

Represent two different actions explicitly: acquiring data and computing results.
Every result operand an instruction consumes must refer to an output of some
instruction; literal constants and resource identifiers are different operand types. A value being mentioned in prose somewhere in the package never
makes it available; only an instruction that produces it does.

ACQUIRING DATA: Every actual read of runtime context, file/configuration contents,
or returned data from an external API/tool/service is a real source CandidateBlock.
Set data_source_kind to "context" or "external". A source block contains exactly one
acquisition instruction followed by a dispatch or return terminator. One read may
produce multiple outputs. Preserve conditional reads on their own paths; do not
hoist every source to the entry block.

For runtime context, use data_source_kind="context". The acquisition inputs
must be non-empty context_key operands identifying keys in declared_context_keys.
Only this acquisition may consume context_key operands. The declaration alone
never makes a result available: the acquisition produces the named results used
by later instructions. Name the acquisition for what is actually read, for example
read_user_message or read_city_from_request. Use read_context only when the source
does not give a more specific action. The data_source_kind and operand structure
determine the source category, not the opcode spelling.

For external acquisition, use data_source_kind="external" and a descriptive
opcode such as read_file, http_get, or a named tool call. Include an
external_resource identifier or a result, such as a dynamic file path, in its
inputs. A resource identifies a file, API, tool, or service; it is not the data
returned from it. A pure side effect without returned data can be an ordinary
block. Keep literal constants in Operand.literal_value; do not create source
blocks just to introduce literals or service handles.

All opcodes are semantic strings under the same contract. There is no separate
list of built-in business operations. Do not infer effects or audit findings
from opcode spelling. Only dispatch and return have fixed control-flow roles as
specified below. Preserve original code in metadata.script_content.

NAMING OPERATIONS: Choose an action-and-object name that says what this instruction
does, using details supported by the source: read_city_from_request,
trim_message_whitespace, or send_slack_notification. A reader should understand
the action from the opcode together with its operands, without relying only on
the block name. When calling a function or tool explicitly named in the source,
preserve that name, for example normalize_city or check_urgency. Do not invent
processing steps, destinations, or effects to make a name more specific. Use the
same opcode for the same behavior on different paths; a branch alone does not
require a different operation name. These names are examples, not a vocabulary
restriction or a list of operations with special validation rules.

COMPUTING RESULTS: Set data_source_kind to null for ordinary behavior and computed
transformations. Every instruction output is a result whose identifier you choose,
and that identifier must be unique across the WHOLE candidate: never give the same identifier
to two produced values, even in different blocks. Choose a meaningful result identifier based on what it
holds, for example "extracted_city" or "weather_report".

USING RESULTS: To consume a value, write a result input naming it exactly
as the producing instruction named it in its outputs, whichever block that
instruction lives in. Do not re-acquire or relay a value on the way: a block that
neither reads nor produces a value does not mention it, and later readers refer directly to the original result identifier. The compiler
checks that a control-flow path connects the producer to the reader. To change a value, consume it and
produce a NEW identifier for the result, so the original identifier keeps its original
meaning everywhere it appears.

Say what the package says and let the analysis work out whether a path connects each result producer to its reader. A block after a merge may reference a value that only one branch
produces, and a block inside a loop may reference a value that a later block on
the backedge produces. Neither is an error to avoid: do not add a second producer
to make such a read look safe, and do not drop the read.

Use dispatch as the final instruction of a block that has outgoing edges. Use
return as the final instruction of a block that ends execution. Put every value
used to choose a branch in dispatch.inputs, including computed predicates. Edge
condition_text text is only a readable description; it never declares data dependencies.
Both dispatch and return must have empty outputs; return consumes its result
through inputs. A block must not have instructions after its terminator.

ENDING BLOCKS: When a behavior finishes the path, return may appear at the end of
that block. An independent branch may consist of return alone. Return a
source-specified literal or an existing result directly; do not introduce
preparation, assignment, or wrapping operations just to pass it to return.
Preserve actual branch/merge boundaries and independent behavior components.

Return only JSON matching the schema below; do not wrap it in Markdown fences
and do not add commentary.
"""


# Complete candidate examples are kept as data so tests can compile the exact
# JSON shown to the model, including the result-operand contract.
_EXAMPLES = [
    (
        "Straight-line example: read, trim, then log progress and return in the same block",
        {
            "entry_block_ref": "read_input",
            "declared_context_keys": ["user_input"],
            "blocks": [
                {
                    "block_ref": "read_input",
                    "block_name": "Read the user's input message",
                    "data_source_kind": "context",
                    "instructions": [
                        {
                            "instruction_ref": "read",
                            "opcode": "read_user_message",
                            "inputs": [
                                {"type": "context_key", "identifier": "user_input"}
                            ],
                            "outputs": [
                                {"type": "result", "identifier": "raw_message"}
                            ],
                        },
                        {"instruction_ref": "go_normalize", "opcode": "dispatch"},
                    ],
                },
                {
                    "block_ref": "normalize",
                    "block_name": "Remove leading and trailing whitespace from the message",
                    "data_source_kind": None,
                    "instructions": [
                        {
                            "instruction_ref": "normalize_message",
                            "opcode": "trim_message_whitespace",
                            "inputs": [{"type": "result", "identifier": "raw_message"}],
                            "outputs": [
                                {"type": "result", "identifier": "normalized_message"}
                            ],
                        },
                        {"instruction_ref": "go_record", "opcode": "dispatch"},
                    ],
                },
                {
                    "block_ref": "record",
                    "block_name": "Record progress and return the normalized message",
                    "data_source_kind": None,
                    "instructions": [
                        {
                            "instruction_ref": "record_progress",
                            "opcode": "log_progress",
                            "inputs": [{"type": "literal", "literal_value": "ready"}],
                        },
                        {
                            "instruction_ref": "return_message",
                            "opcode": "return",
                            "inputs": [
                                {"type": "result", "identifier": "normalized_message"}
                            ],
                        },
                    ],
                },
            ],
            "edges": [
                {"source_block_ref": "read_input", "target_block_ref": "normalize"},
                {"source_block_ref": "normalize", "target_block_ref": "record"},
            ],
            "diagnostics": [],
        },
    ),
    (
        "Branch example: acquire only on one path, then reference both paths after the merge",
        {
            "entry_block_ref": "read_input",
            "declared_context_keys": ["user_input"],
            "blocks": [
                {
                    "block_ref": "read_input",
                    "block_name": "Read the alert message",
                    "data_source_kind": "context",
                    "instructions": [
                        {
                            "instruction_ref": "read",
                            "opcode": "read_alert_message",
                            "inputs": [
                                {"type": "context_key", "identifier": "user_input"}
                            ],
                            "outputs": [
                                {"type": "result", "identifier": "raw_message"}
                            ],
                        },
                        {"instruction_ref": "go_decide", "opcode": "dispatch"},
                    ],
                },
                {
                    "block_ref": "decide",
                    "block_name": "Check urgency",
                    "data_source_kind": None,
                    "instructions": [
                        {
                            "instruction_ref": "check_urgency",
                            "opcode": "check_message_urgency",
                            "inputs": [{"type": "result", "identifier": "raw_message"}],
                            "outputs": [{"type": "result", "identifier": "urgent"}],
                        },
                        {
                            "instruction_ref": "choose_path",
                            "opcode": "dispatch",
                            "inputs": [{"type": "result", "identifier": "urgent"}],
                        },
                    ],
                },
                {
                    "block_ref": "send_alert",
                    "block_name": "Send the alert and read the Slack receipt",
                    "data_source_kind": "external",
                    "instructions": [
                        {
                            "instruction_ref": "send_slack",
                            "opcode": "post_slack_alert",
                            "inputs": [
                                {"type": "external_resource", "identifier": "slack"},
                                {"type": "result", "identifier": "raw_message"},
                            ],
                            "outputs": [
                                {"type": "result", "identifier": "slack_receipt"}
                            ],
                        },
                        {
                            "instruction_ref": "go_reply_from_alert",
                            "opcode": "dispatch",
                        },
                    ],
                },
                {
                    "block_ref": "skip_alert",
                    "block_name": "Prepare the non-urgent note",
                    "data_source_kind": None,
                    "instructions": [
                        {
                            "instruction_ref": "make_skip_note",
                            "opcode": "prepare_no_alert_note",
                            "inputs": [
                                {"type": "literal", "literal_value": "No alert needed"}
                            ],
                            "outputs": [{"type": "result", "identifier": "skip_note"}],
                        },
                        {"instruction_ref": "go_reply_from_skip", "opcode": "dispatch"},
                    ],
                },
                {
                    "block_ref": "reply",
                    "block_name": "Report the outcome of whichever path ran",
                    "data_source_kind": None,
                    "instructions": [
                        {
                            "instruction_ref": "format_reply",
                            "opcode": "format_alert_outcome",
                            "inputs": [
                                {"type": "result", "identifier": "raw_message"},
                                {"type": "result", "identifier": "slack_receipt"},
                                {"type": "result", "identifier": "skip_note"},
                            ],
                            "outputs": [
                                {"type": "result", "identifier": "outcome_text"}
                            ],
                        },
                        {
                            "instruction_ref": "return_outcome",
                            "opcode": "return",
                            "inputs": [
                                {"type": "result", "identifier": "outcome_text"}
                            ],
                        },
                    ],
                },
            ],
            "edges": [
                {"source_block_ref": "read_input", "target_block_ref": "decide"},
                {
                    "source_block_ref": "decide",
                    "target_block_ref": "send_alert",
                    "condition_text": "urgent",
                },
                {
                    "source_block_ref": "decide",
                    "target_block_ref": "skip_alert",
                    "condition_text": "not urgent",
                },
                {"source_block_ref": "send_alert", "target_block_ref": "reply"},
                {"source_block_ref": "skip_alert", "target_block_ref": "reply"},
            ],
            "diagnostics": [],
        },
    ),
]


def build_whole_skill_prompt(package: SkillPackage) -> str:
    """Build a complete prompt without truncating readable package content."""

    sections = [
        _INSTRUCTIONS,
        "Candidate JSON Schema:",
        json.dumps(
            IRAnalysisCandidate.model_json_schema(), ensure_ascii=False, indent=2
        ),
    ]
    for title, candidate in _EXAMPLES:
        sections.extend(
            [title + ":", json.dumps(candidate, ensure_ascii=False, indent=2)]
        )
    sections.extend(
        [
            "The examples illustrate the contract only. Extract the actual package below; "
            "do not copy example behaviors that are absent from it.",
            "Complete Skill package:",
        ]
    )

    for file in package.files:
        header = (
            f'<skill-file path="{file.path}" kind="{file.kind}" size="{file.size}">'
        )
        sections.append(header)
        if file.content is None:
            sections.append("[binary content omitted]")
        else:
            sections.append(file.content)
        sections.append("</skill-file>")

    return "\n\n".join(sections)
