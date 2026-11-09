"""Short isolated prompts; understanding does not receive final JSON schemas."""
from skillflow.common.prompt_format import compact_json, render_prompt_format
from skillflow.propagation.contracts.abstraction import BOUNDARY_GRANULARITY, NECESSITY_EXAMPLE
from skillflow.task.prompts import PRE_SUBMIT_CHECK
from .source import render_source, source_packet, select_document_source, select_fragment_source, prompt_cfg
from .interface_examples import phase_examples

_STEPS = {
    "flow": (set(), "Describe actual entry points, behavior, conditions, cross-file producers and consumers, actual parameters, distinct returned versions, order, shared state, and unresolved relationships in one short document. Preserve independent capabilities and selected import sources. Connect analysis, saved results, reading and summarization only where source supports them; missing file association remains an explicit gap."),
    "relationships": ({"flow"}, "Complete the same whole-Skill flow document with actual producers, consumed parameters, distinct return versions, branch inputs, order and shared-state relationships. Preserve independent capabilities and unresolved source conflicts. Do not divide the Skill into separate graph jobs or ask the program to infer connections."),
    "processing": ({"flow"}, "Describe actual acquisition and processing ranges, observation, delivery, storage, and distinct data versions. Include source-supported per-element acquisition and yield/collection output, normal completion versus caught errors, and actual representational obstacles. A saved-result continuation does not establish file provenance. Reading a whole value does not make every field a task requirement."),
    "task-correspondence": ({"processing"}, "Relate every fixed Task requirement to actual results, receiving input slots, saved payloads, behavior, supported constraints, and remaining gaps. Do not rewrite Task or infer demands from the entire current payload."),
    "sensitivity": ({"processing"}, "Identify sensitive information ranges, their actual source versions and supporting context. Do not change processing or task demands; missing declarations do not establish non-sensitivity."),
}
_OUTPUT = """Return a short English Markdown working document, not a JSON business object.
Record only checkable conclusions, exact file/line references (skill/path.ext:12-18), relationships
needed by the next step, and unresolved questions. Do not provide a chain of
thought, copy code bodies, or produce another Task summary. Working documents
do not replace source evidence. If material is insufficient, explicitly request
exact frozen file names or inclusive line ranges. Do not guess dependencies.
For a necessary unrepresentable relationship, return only a failure JSON:
{"outcome":"cannot_assess","failure":{"reason":"specific obstacle",
"evidences":[{"file":"exact frozen file","start_line":1,"end_line":1,
"reason":"why this actual span requires that relationship"}]}}.
Use real spans; ordinary uncertainty remains a short document limitation."""

_OWNER_CHECKS = {
    "flow": "Recheck entry points, independent capabilities, conditions, recipients, state changes and producer/consumer links. Keep unsupported connections as explicit gaps.",
    "cfg": "Recheck actual entry/exit, explicit connections and operands, unique producers, returned versions and source-supported branch inputs. Keep acquisition, initialization and later uses distinct where the source distinguishes them.",
    "processing": "Recheck current-IR coverage, actual request/response and member pairing, state effects, output bindings and local returns. Use the same action boundaries as the CFG; keep precise local gaps instead of fake operations or missing effects.",
    "task-correspondence": "Recheck each supplied Task requirement against actual operations and values, including conditions and receiver pairing. Separate action necessity from payload necessity; preserve genuine whole-value requirements and specific unexpressed requirements.",
    "sensitivity": "Recheck sensitive sources, ranges, versions and existing member/case references. Distinguish plaintext inclusion from possible or derived influence; use source evidence without inferring Task necessity.",
}


def _pre_submit(output, owner, enabled):
    if type(enabled) is not bool:
        raise ValueError("self_check must be Boolean")
    if not enabled:
        return output
    return output + "\n\nPRE-SUBMIT CHECK\n" + PRE_SUBMIT_CHECK + "\n" + _OWNER_CHECKS[owner]


def _render(role, previous, global_requirements, packet, output):
    return "\n\n".join(("STEP RESPONSIBILITY\n" + role,
                         "PREVIOUS WORK\n" + previous,
                         "GLOBAL REQUIREMENTS AND LIMITATIONS\n" + global_requirements,
                         "RELATED SOURCE\n" + render_source(packet),
                         "OUTPUT REQUIREMENTS\n" + output))


def build_document_prompt(step, *, files, spans=None, documents=None, cfg=None,
                          task=None, runtime_contract=None, global_requirements=""):
    if step not in _STEPS:
        raise ValueError("Unknown working-document step")
    if type(global_requirements) is not str or (step != "flow" and not global_requirements.strip()):
        raise ValueError("Later requests require explicit global obligations and unresolved issues")
    documents = documents or {}
    allowed, role = _STEPS[step]
    if set(documents) - allowed:
        raise ValueError(f"{step} does not accept documents: {sorted(set(documents) - allowed)}")
    if step == "relationships" and "flow" not in documents:
        raise ValueError("Relationship completion requires the existing flow document")
    if step in {"task-correspondence", "sensitivity"} and "processing" not in documents:
        raise ValueError(f"{step} requires the processing document")
    if any(type(value) is not str or not value.strip() for value in documents.values()):
        raise ValueError("Working documents must be nonempty Markdown text")
    packet = source_packet(files, spans) if step == "flow" else select_document_source(files, documents, spans=spans)
    if step == "flow":
        if any(value is not None for value in (cfg, task, runtime_contract)):
            raise ValueError("Flow understanding receives source and navigation only")
        if packet["unreferenced_ranges"]:
            raise ValueError("Initial flow understanding requires the complete readable source")
    elif step == "relationships":
        if any(value is not None for value in (cfg, task, runtime_contract)):
            raise ValueError("Relationship completion receives source and the flow document only")
    elif cfg is None:
        raise ValueError(f"{step} requires the complete CFG")
    if (task is not None) != (step == "task-correspondence"):
        raise ValueError("Only task-correspondence receives the sealed Task, and it is required")
    if (runtime_contract is not None) != (step == "processing"):
        raise ValueError("Only processing receives the runtime contract, and it is required")
    previous = [f"DOCUMENT {name}\n{text}" for name, text in documents.items()]
    for name, value in (("CFG", cfg), ("SEALED_TASK", task), ("RUNTIME_CONTRACT", runtime_contract)):
        if value is not None:
            previous.append(name + "\n" + compact_json(prompt_cfg(value, packet=packet) if name == "CFG" else value))
    if cfg is not None:
        previous.append("CFG display omits metadata.script_content only where the identical code is already supplied below as related source. Other embedded code remains. This does not narrow any operation or change the saved graph.")
    output = _OUTPUT
    if step == "relationships":
        output += "\nReturn the complete revised flow document, including earlier conclusions and unresolved questions; not an incremental supplement."
    return _render(role, "\n\n".join(previous) or "None.",
                   global_requirements or "Preserve global requirements, prohibitions and unresolved source conflicts; never infer their absence from a local excerpt.", packet, output)


def _working_documents(documents, required):
    if set(documents) != set(required):
        raise ValueError("Expected exactly these working documents: " + ", ".join(required))
    if any(type(text) is not str or not text.strip() for text in documents.values()):
        raise ValueError("Working documents must be nonempty Markdown text")
    return "\n\n".join("DOCUMENT " + name + "\n" + documents[name] for name in required)


_GRAPH_FILLING = """Fill one complete existing CFG candidate from the completed flow document and its source.
Use the document as a fallible working result, not an authority above the source.
Keep source-supported entry points, independent components, conditions, explicit
cross-file producer/consumer relationships and unresolved conflicts. Do not add
edges from proximity or names. The program numbers and validates explicit model
objects; it does not infer control or data connections.

Each instruction is one definite source action. Source-specified changes and
transfers with different versions stay distinct. Keep pure local calculations
opaque, but expose conditions that change acquisition, delivery, saved content,
returned versions or state. Retain callable interfaces and source-backed call
summaries; do not construct an internal call stack or expand every code line.
Acquisition is a source block (context/external) with exactly one acquisition
instruction followed by dispatch/return. Context acquisition consumes declared
context_key entries. Resource identifiers are not the acquired values. Ordinary
computation uses data_source_kind=null. Every produced result identifier is unique
throughout the candidate; later consumers use that actual identifier, including
across branches and loops. Do not invent relay acquisitions or a second producer.
Preserve repeated calls and returns as different versions.

A block with outgoing edges ends in dispatch; a terminal block ends in return.
Both have no outputs. dispatch consumes the values used to choose its edges;
return consumes its actual result. Edge condition_text is not a data dependency.
Place source constraints at their real graph/block/instruction scope. A stated
restriction is not an implemented guard, deletion or extra operation. Faithfully
retained source ambiguity does not require choosing a winning interpretation.

For code, put the exact frozen source selection in the existing metadata field
as _source_span={file,start_line,end_line}; the program copies that exact original
text into metadata.script_content and removes this technical selection. Never
invent a range or duplicate the code in the response. Other metadata is preserved.
Check all explicit connections, operands, unique references and actual entry
before returning one complete JSON object. No fragment, patch or additional keys.
Use cannot_assess only when no usable whole candidate can represent a necessary
relationship; cite frozen source. Open details or preserved ambiguity alone are
not a failure. Explanations use English; source quotations retain their language.
"""


def build_graph_prompt(*, files, documents, spans=None, global_requirements, feedback=None):
    """One whole candidate, without business grouping or fragment assembly."""
    from pydantic import TypeAdapter
    from .cfg_wire import CFGWire
    from skillflow.task.services import _FailureResponse
    if type(global_requirements) is not str or not global_requirements.strip():
        raise ValueError("Graph filling requires explicit global obligations and unresolved issues")
    previous = _working_documents(documents, ("flow",))
    if feedback is not None:
        previous += "\n\nCURRENT REVIEW FEEDBACK\n" + compact_json(feedback)
    output = _GRAPH_FILLING + "\n" + BOUNDARY_GRANULARITY + "\nEXISTING RESPONSE FORMAT\n" + render_prompt_format(
        TypeAdapter(CFGWire | _FailureResponse).json_schema())
    output += ("\nThe program generates instruction references, readable canonical names and the context-key inventory. "
               "Do not supply instruction_ref, semantic_name or declared_context_keys. Empty/default fields may be omitted. "
               "Keep distinct acquisition, version, recipient, condition and visibility changes. "
               "A declaration, repeated explanation or example is not automatically another executed action. "
               "Do not expand an import-source by export by example Cartesian product; preserve actual alternatives. "
               "The program never infers file ownership from names, adjacent actions or a shared label.")
    return _render("Fill the one complete CFG for the same Skill; do not re-plan it as subgraphs.",
        previous, global_requirements, select_document_source(files, documents, spans=spans), output)


def build_flow_prompt(*, files, global_requirements, self_check=False):
    """The new entry retains a short flow, without a whole-run failure branch."""
    output = ("Return a short English Markdown flow document with exact frozen file/line references. "
              "Preserve actual entry points, versions, recipients, conditions, effects and unresolved relationships. "
              "State source-local gaps in the document; submit supported facts rather than refusing the whole Skill. "
              "Do not copy code, invent dependency links or give hidden reasoning.\n" + BOUNDARY_GRANULARITY)
    return _render(_STEPS["flow"][1], "None.", global_requirements, source_packet(files), _pre_submit(output, "flow", self_check))


def build_fragment_prompt(step, *, files, documents, cfg, global_requirements,
                          task=None, runtime_contract=None, repair_context=None, self_check=False):
    """One semantic owner submits records; Python performs annotation assembly."""
    from .fragments import fragment_adapter, fragment_contract_rules
    if step not in {"processing", "task-correspondence", "sensitivity"}:
        raise ValueError("Unknown semantic fragment")
    expected = {"flow"} if step == "processing" else {"processing"}
    if set(documents) != expected or ((task is not None) != (step == "task-correspondence")):
        raise ValueError("Fragment dependency isolation differs")
    if (runtime_contract is not None) != (step == "processing"):
        raise ValueError("Only processing receives the runtime contract")
    texts = {key: value if isinstance(value, str) else compact_json(value)
             for key, value in documents.items()}
    typed_context = {"processing": documents.get("processing"), **({"task": task} if task is not None else {})}
    packet = (select_fragment_source(files, typed_context) if step != "processing"
              else select_document_source(files, texts))
    previous = ["DOCUMENT " + key + "\n" + value for key, value in texts.items()]
    previous.append("CFG\n" + compact_json(prompt_cfg(cfg, packet=packet)))
    if task is not None:
        previous.append("SEALED_TASK\n" + compact_json(task))
    if runtime_contract is not None:
        previous.append("RUNTIME_CONTRACT\n" + compact_json(runtime_contract))
    if repair_context is not None:
        previous.append("Return one COMPLETE replacement fragment for the CURRENT CFG and Task version. "
            "Review targets identify where to recheck, not the permitted output subset. Preserve every still-supported record. "
            "The old fragment is reference material, not an implicit merge or a source of current coordinates. "
            "Only an explicitly requested structural correction uses the replacements envelope.\nSOURCE REVIEW REPAIR\n" + compact_json(repair_context))
    common = ("Return only the requested compact JSON semantic fragment. There is no whole-analysis failure outcome. "
        "Submit supported declarations and specific source-located unresolved relationships. "
        "The program assembles annotation; never repeat another owner's fields, Task text, code, internal IDs or pass ledgers. "
        "Use existing CFG IDs and explicit processing coordinates; do not match calls by adjacency or arguments. "
        "Interpretations and reasons use English; source and quotes retain their original language. "
        "Source evidence is a citation, not proof of semantic completeness.\n" + BOUNDARY_GRANULARITY)
    necessity = NECESSITY_EXAMPLE if step == "task-correspondence" else ""
    coverage = ""
    if step == "processing":
        ids = [ir["id"] for block in cfg["blocks"].values() for ir in block["instructions"]]
        coverage = ("COMPLETE PROCESSING COVERAGE\nEvery CURRENT CFG instruction, including dispatch and return, needs exactly one "
            "ir_semantics record or an explicit source-backed unmodeled processing gap. A control terminator is not omitted "
            "merely because it has no output. Precision-only gaps do not replace its record. Do not return only edited records.\n"
            "REQUIRED_IR_IDS\n" + compact_json(ids) + "\n")
    output = (common + necessity + coverage + "FRAGMENT FORMAT\n" + render_prompt_format(fragment_adapter(step).json_schema())
              + "\n" + fragment_contract_rules(step) + "\n" + phase_examples(step))
    return _render(_STEPS[step][1], "\n\n".join(previous), global_requirements, packet, _pre_submit(output, step, self_check))


def build_compact_graph_prompt(**kwargs):
    """Reuse the graph semantics, exposing only the new non-refusal schema."""
    from .cfg_wire import CFGWire, cfg_contract_rules
    files, documents = kwargs["files"], kwargs["documents"]
    packet = select_document_source(files, documents, spans=kwargs.get("spans"))
    previous = _working_documents(documents, ("flow",))
    if kwargs.get("feedback") is not None:
        feedback = dict(kwargs["feedback"])
        if "cfg" in feedback:
            feedback["cfg"] = prompt_cfg(feedback["cfg"], packet=packet)
        previous += "\n\nCURRENT REVIEW FEEDBACK\n" + compact_json(feedback)
    rules = ("Fill one complete CFG from source. The flow document is fallible working material. "
             "Retain supported relationships and source-located diagnostics for open details; do not return a whole-analysis refusal. "
             "Interpretations use English; source quotations retain their language.\n")
    output = (rules + "\n" + BOUNDARY_GRANULARITY + "\nCFG WIRE FORMAT\n" + render_prompt_format(CFGWire.model_json_schema())
              + "\n" + cfg_contract_rules() + "\n" + phase_examples("cfg"))
    return _render("Fill the complete CFG from source; preserve real versions and receiving boundaries.",
        previous, kwargs["global_requirements"], packet, _pre_submit(output, "cfg", kwargs.get("self_check", False)))


def build_annotation_prompt(material, *, documents, spans=None, global_requirements,
                            repair_context=None):
    """One full annotation; previous documents split judgment, not business data."""
    from pydantic import TypeAdapter
    from skillflow.propagation.material import checked_material
    from skillflow.propagation.contracts.joint import joint_source_files
    from .annotation_wire import RESPONSE_ADAPTER
    if type(global_requirements) is not str or not global_requirements.strip():
        raise ValueError("Annotation filling requires explicit global obligations and unresolved issues")
    material = checked_material(material)
    packet = select_document_source(joint_source_files(material), documents, spans=spans)
    previous = _working_documents(documents, ("processing", "task-correspondence", "sensitivity"))
    previous += "\n\nCFG\n" + compact_json(prompt_cfg(material["cfg"], packet=packet))
    previous += "\n\nSEALED_TASK\n" + compact_json(material["task"])
    previous += "\n\nRUNTIME_CONTRACT\n" + compact_json(material["runtime_contract"])
    previous += ("\nCFG display omits metadata.script_content only where identical code is supplied below as related source; other embedded code remains. "
                 "The complete saved CFG and actual acquisition scopes remain unchanged.")
    if repair_context is not None:
        previous += ("\n\nANNOTATION REPAIR\nThe prior findings and targets belong to their recorded old objects. "
            "Use the current Task and CFG, recheck source, and never transplant old IDs into changed objects. "
            "Return one complete replacement; preserve supported relationships and sensitivity.\n" + compact_json(repair_context))
    output = ("Return one complete flat annotation JSON object. Working documents are fallible conclusions; "
        "check source, retain unresolved issues, and keep source-supported versions, conditions and receiver pairing.\n"
        + render_prompt_format(RESPONSE_ADAPTER.json_schema()) + "\n\n"
        "IR records contain segments with ops. Evidence inherits from the nearest applicable parent; override a changed claim. "
        "Locations carry their own evidences; boundary defaults follow the supplied contract. The program binds Task revision, "
        "derives realization status and expands effects; do not copy hashes or operator/empty-effect proofs.\n"
        "Task demands preserve only grounded requirements. Required action does not require every carried field. "
        "Attach required delivery/save content to the actual operation input, separately from action. "
        "Targets input(index), output and self mean actual parameter use, produced value and action; self is action only. "
        "Do not infer a whole-value demand from acquisition or current payload. Preserve explicit whole-value returns "
        "where source actually requires them, separately for each receiving boundary.\n"
        "call represents one known request and response at tool/remote. Its input demands address request parameters, "
        "output demands address the response, self addresses request initiation. Constraint phase request (default) "
        "or response selects that actual event. Independent or asynchronous interactions keep separate operations.\n"
        "for_each is a single element scope: read/receive/call are allowed; nested loops and arbitrary shared writes are not. "
        "A bounded cases summary uses fixed IR order and may explicitly replace a task-local runtime_context binding with may=true; "
        "this is a state possibility summary, not per-member state execution. "
        "Specify yield and output together to collect one possible result per source occurrence. Body locals do not escape otherwise. "
        "Repeated equal elements remain distinct invocations. Unknown collection is not a one-element list. "
        "Source-backed success/error alternatives occupy one member; do not invent exceptions or catch-and-continue behavior.\n"
        "mode local requires explicit returns, including []. yield and output_bindings never create model observation. "
        "A source-supported local segment with ops=[] and nonempty returns may route an existing final value to the model. "
        "Possible/derived influence does not establish original plaintext inclusion. Unknown response contents do not justify invented fields. "
        "Keep known API acquisition even without SDK internals. Pure compute does not acquire a response. "
        "compute dependencies default to possible; its optional effect is transform (default) or null for an effect-free possible relation.\n"
        "Only source-supported constraints and expressions are allowed; unsupported restrictions remain gaps. "
        "Use cannot_assess only for a necessary relationship that cannot be represented, not ordinary opacity or retained ambiguity. "
        "English explanations; original quotations keep their language.")
    return _render("Independently fill actual processing, fixed-Task demands and sensitivity using the supplied conclusions and source.", previous, global_requirements,
        packet, output)


def build_batch_prompt(kind, *, files, spans, documents, accepted_objects, global_requirements):
    from .batches import batch_format
    if type(global_requirements) is not str or not global_requirements.strip():
        raise ValueError("Batch requests require explicit global obligations and unresolved issues")
    allowed = ({"flow"} if kind.startswith("graph") else
               {"processing", "task-correspondence", "sensitivity"})
    if set(documents) - allowed:
        raise ValueError("A batch received an unrelated working document")
    role = ("Fill the requested existing graph objects and explicit references. Do not infer or delegate missing connections to the program."
            if kind.startswith("graph") else
            "Fill only the requested existing annotation fields. Use actual IR operands and operation input slots; expected relationships do not change actual processing. Preserve source versions and global restrictions.")
    previous = "\n\n".join(f"DOCUMENT {name}\n{text}" for name, text in documents.items())
    previous += "\n\nACCEPTED OBJECTS (read only)\n" + compact_json(accepted_objects)
    output = ("Return one complete JSON object for this batch, with no unknown fields. "
              "Do not rewrite accepted objects outside this batch. Keep explicit references. "
              "Request exact frozen source ranges when material is missing. Final composition "
              "undergoes the original full validation and compilation.\n" + batch_format(kind))
    return _render(role, previous, global_requirements, source_packet(files, spans), output)
