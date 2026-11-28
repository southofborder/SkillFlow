"""One abstract runtime contract shared by annotation and static propagation.

The contract bounds possible executions; it does not describe a measured trace
or select a concrete agent runtime. Rules and the closed operation inventory
describe the typed implementation; source review checks their application.
Source extraction and source/CFG review do not inherit its defaults.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from typing import Any
from .abstraction import BOUNDARY_GRANULARITY


CONTRACT_VERSION = "skillflow-abstract-runtime-v16"
LEGACY_CONTRACT_VERSION = "skillflow-abstract-runtime-v12"
_SELECTOR_CONTRACT = "skillflow-abstract-runtime-v13"
_PLACEHOLDER_CONTRACT = "skillflow-abstract-runtime-v14"
_OUTCOME_CONTRACT = "skillflow-abstract-runtime-v15"
_ARCHIVED = (LEGACY_CONTRACT_VERSION, _SELECTOR_CONTRACT, _PLACEHOLDER_CONTRACT, _OUTCOME_CONTRACT)

# Stable evidence IDs. A revised meaning or text requires a new contract version.
_RULES = (
    ("EM01", "Source scope default: a natural-language request for a field from a container does not establish a key-only read mechanism. Preserve the related source whole as a possible acquisition scope unless an explicit interface or mechanism restricts the read or returned content. Merely needing one field, using a local tool, or naming a getter in an opcode is not such evidence. Keep source identity, local read scope, returned content, and the selected target value separate. Express the requested field selection without replacing the source whole by an independent field source. The whole may remain unexpanded; do not invent other fields, sensitivity labels, file paths, or access to unrelated runtime state. This is a conservative analysis default, not proof that an actual execution reads the whole, and not an extra source-level CFG action."),
    ("EM02", "Tool-return default: content returned by an agent tool is retained as possibly entering the next model request unless an explicit content-routing or isolation mechanism restricts it. Apply this default to the returned version, not to everything the tool internally read. A local process can scan a whole file and return only a selected line; the scan alone does not expose the whole file to the model. Explicit local-only processing, result-only return, model-invisible storage, and credential injection or handles constrain this default. Such exceptions require supported source, code, or interface evidence, not executor labels or wishful implementation choices. This is a may-analysis assumption, not a measured event or a fact about every agent."),
    ("EM03", "Model visibility boundary: content placed in a model request constitutes model_observe of that content, not proof that the model understands, remembers, or later discloses it. Local reading and LLM scheduling alone do not establish that boundary. For content acquired for the agent's natural-language processing with no explicit isolation or restricted routing, retain possible model observation of the acquired version. Cite this rule for the default and source/CFG evidence for the acquisition to which it applies. An agent_runtime or tool label, a local-sounding opcode, or a desired field is not evidence of model invisibility. Defaults apply normally when execution details are absent. A necessary relationship not supported by the available material remains an explicit local limitation; unknown concrete values alone do not disable supported static analysis."),
    ("EM04", "Data versions and explicit mechanisms: distinguish model processing from local processing. A model selecting or transforming content observes its input version; explicitly local processing whose result alone is returned exposes that result instead, without inventing observation of all internal inputs. An evidenced key-only interface limits the acquired or returned value, while model visibility is assessed separately. A supported model-invisible credential proxy or isolated handle is not secret plaintext. Subsequent filtering cannot revoke an earlier observation. Selection, masking, encryption, and summarization use transform when supported, but do not prove sensitivity removal. Distinct observation stages require distinct phase evidence; do not invent their count or impose protection-first ordering."),
    ("EM05", "Declarations and defaults: a prohibition or instruction to use only a specified field does not itself implement filtering, masking, isolation, or a key-only interface. Preserve explicit restrictions without inventing protective actions to satisfy them. Contract defaults may supply possible analysis events for an existing action; they cannot create an unrelated acquisition or source-level business action. Clearly identify default-based inferences as possible under this contract, never as explicit source requirements, observed runtime events, or verified security guarantees."),
    ("EM06", "Independent interaction boundaries: tool names and LLM participation do not prove network communication; sending verbs, recipient identifiers, and executor labels are not communication-mechanism evidence. Choose remote/net_send/net_receive only when the source, code, or interface establishes network transport; otherwise retain a known tool at tool/recipient/null under EM12; ordinary return does not prove user-facing output. Model observation, network delivery, and user output are separate boundaries. Preserving possible observation of a container does not broaden later API arguments: delivery must retain actual selected values, input order, result identities, and explicit prohibitions. Lack of a concrete getter or execution framework alone does not disable the declared defaults. Preserve calculable partial order; report a semantic failure only when a necessary relation cannot be represented or assessed."),
    ("EM07", "Runtime-context writes: context_write requires evidence of creating, updating, or deleting runtime context content or bindings that later actions can read, including shared session state and environment variables. Merely producing an IR result is not a context write. File writes and model observation do not automatically imply context_write; each effect requires its own evidence. Saving unchanged content does not imply transform. Deleting a binding does not imply reading, transforming, or observing its former content. This classification rule does not establish an otherwise unrecorded write."),
    ("EM08", "Address and value identity: preserve relevant input scope unless an explicit selection, deletion, replacement, or isolation supports reduction. Unknown computations retain possible input dependencies without claiming that all input plaintext survives. Location address_kind defaults to identified: its name is a stable source identity even if content is unknown. Known caller slots, caught exception payloads, request outcomes and member-local values must not become wildcard addresses. Reuse their real input/local/call result; an independently acquired exception source has its own evidenced identity and occurrence. Only an actually unidentified address sets address_kind=unidentified, with a specific address_reason and physical source evidence. It may alias identified or unidentified addresses of the same kind and permits only weak updates. The spelling symbolic: has no alias semantics; legacy prefixed names without explicit address_kind are rejected. Unknown payload, unavailable concrete value, or missing execution is not evidence of address uncertainty. Partial effect order retains supported original and later candidates. Source wholes may exist without observation; registration alone creates no delivery. Declare symbolic operations, never propagated Data IDs or DOE judgments."),
    ("EM09", "Acquisition and computation differ: returned tool or collection content has an acquisition boundary not exhausted by query inputs. Preserve that boundary, actual request inputs, and possible dependencies. Established remote receipt uses receive at a remote location with net_receive; known tool acquisition without established networking uses receive at a tool location in a null-effect event. An explicitly pure calculation remains compute; an opaque computation preserves possible dependencies without inventing a new external source. Unknown networking does not erase known acquisition. Assess the returned content's possible model routing with EM02 and EM03 rather than inferring visibility from the tool name."),
    ("EM10", "Deterministic processing compilation: model mode declares model processing. When participating operators are explicitly supplied, they must include llm; omitted or null operator is unknown, not a confirmed absence. Executor labels do not independently establish visibility. Before model processing, observe its actually referenced external input versions; intermediate values computed within that same segment are not fresh external inputs; acquired read/receive outputs become observable after acquisition. Default mode retains possible observation of read/receive outputs and non-isolated transformation inputs; it does not observe receive request parameters merely because a response is acquired. Local mode requires explicit source or code/interface evidence and an explicit returns list; internal reads are not model observations, while declared returned values cross to the model after the local segment. Empty local returns means no content returned to the model by that segment. Deduplicate unchanged external symbolic references within one processing segment by value reference and its consumption condition. A conditional observation never subsumes a later unconditional consumption. Conditions needed for model processing are themselves observed when applicable; a definitely omitted build member consumes no member value. Preserve earlier whole-value observation even when a later request member is omitted. Preserve different segments and returned/acquired versions, without treating every intermediate computation as another model call. Generated model-observation effects do not automatically add llm to operator; retain the independently evidenced executors. The compiler creates these observations from typed modes and references, not opcode or evidence keywords. A model may still misclassify a mode; compilation proves structural implications of the supplied mode, not its truth. IR order is fixed or partial. For partial order, preserve required definition/use and declared within-segment ordering; the compiler records observation-before-model-processing, acquisition-before-observation, and local-processing-before-return-observation constraints. Independent segments may interleave between primitive operations. Partial order is a computable may relation, not a semantic failure."),
    ("EM11", "Element scope and filtering: filter_items preserves selected input elements unchanged under its recorded predicate; the static analysis does not execute a natural-language predicate. for_each introduces one shared element binding per possible element so selections and delivery parameters retain that element's identity. It is an analysis scope, not an invented CFG loop or one measured call. Each body may read or receive a fresh value with member-specific identity. Body locals remain scoped; only an explicit paired yield/output exports the yielded member values as a collection retaining source collection identity, element selectors, order and same-element relationships. An empty collection yields an empty collection. Unknown membership remains symbolic. The compact for_each body retains its lexical contract; explicit CFG loops may nest and are summarized by EM17. Yielding is not a shared-state mutation; arbitrary per-member shared-state execution is not introduced. A supported call summary retains case-specific acquisition, normal or thrown outcomes and explicit may state effects without per-member state execution. Empty input performs no member effects. Uncaught failure permits a complete collection and following save only on the normal-completion path; caught member failures contribute their source-supported error records instead. Selecting an explicit field with select_part preserves that exact part, while compute only records dependence and never proves a field was forwarded unchanged. A field named summary is not itself a summarization operation."),
    ("EM12", "Boundary properties and defaults: access_scope is task, recipient, shared, or public; retention is task, persistent, or null when a receiving boundary's retention is not modeled. Storage and runtime-context locations require non-null retention. A task-internal tool requires supported local execution and task-internal receiving scope; explicitly nonlocal tools use recipient. Unspecified tool deployment conservatively retains an external recipient possibility, without inventing net_send or asserting measured remote execution. Runtime context defaults to task access and task retention; explicit cross-task memory or cross-subject sharing changes the respective property. Files default to task access and persistent retention; task-limited retention requires an explicit temporary-use and cleanup mechanism, not a temp-sounding name. Model, remote, and user boundaries default to recipient access, with null retention unless explicit retention is supported. A locally hosted model remains a content-processing recipient. Public access and sharing require source, code, interface, or supported contract evidence. Null retention does not establish no saving, logging, or future reuse; do not invent unmentioned backend persistence. These properties characterize static boundaries, not sensitivity, necessity, risk, or execution success."),
    ("EM13", "Delivery and sink classification: distinguish actual request delivery, acquired tool response, and compiler-generated model observation of the relevant versions. A tool receive's request dependencies do not replace a deliver operation for an evidenced tool request. Known networking uses its existing net_send delivery; do not duplicate that same delivery as an external_tool sink. A tool delivery with no established network effect is a null-effect deliver to a tool location, including an explicit empty argument list for a known zero-argument request. Pure task-internal delivery remains a propagation relation but is not a DOE sink. Collect content delivery, write and model-observation operations, not executor labels. Deletion or unbinding delivers no old content; append exposes this step's appended input, not automatically all previous stored content. Compute boundary exposure_level deterministically: task-internal/task-limited is 0, task-internal persistent is 1, recipient or shared is 2, public is 3; retain the highest applicable level. Levels describe boundary access and retention only. Only levels 1-3 enter the sink list. Preserve different stages, versions and element scopes. Ordinary return still identifies values in CFG inputs and does not invent a caller location or delivery."),

    ("EM14", "Optional request members: construct known object fields from their actual value references, preserving original field identity. build members may have a Boolean when reference: true includes the original value, false omits the member without consuming its value, and an abstract Boolean retains both possibilities. Identical condition references share one decision within a construction, so jointly controlled fields are not independently mixed. Conditions are control inputs, not request contents; do not add existence flags as payload merely because they govern optional parameters. Reject explicit non-Boolean controls instead of truthiness coercion. A possible true branch still requires a member value. Conditions do not narrow previously acquired or observed wholes, and are not a Data/path-condition system. Compiler-generated conditional observations use the same member condition, observing the condition separately when required and observing the member only when it may be consumed. This is symbolic parameter construction, not a claim about wire serialization."),
    ("EM15", "Request delivery and acquisition: define one request value from actual parameter values and reference it consistently in deliver.inputs and the corresponding receive.inputs. At one IR and element scope, request/response association requires the same boundary and exactly the same ordered symbolic request references. A model-declared call is expanded into an explicitly paired delivery and receive; the program assigns their pair identity from the call coordinate, including repeated identical parameters. One delivery matches at most one response; separately declared ambiguous matches are an explicit binding failure, not a closest-position, name-similarity, or FIFO guess. Acquisition reuses the matched delivery's actual input bindings, including literal identities and data versions, and follows its delivery. Known zero-argument calls and acquisition with no request remain possible under their existing rules. Response inputs describe request influence, not response contents and not a replacement for request delivery."),


    ("EM16", BOUNDARY_GRANULARITY),
    ("EM17", "Finite loop summaries: preserve explicit CFG loops and derive scopes from control flow, not names. Processing supplies predecessor/value merges, collection-member relations and typed Boolean edge choices. A merge selects the corresponding incoming predecessor, including the entry seed before a backedge value exists; it is not an unconditional independent union. A member retains its source occurrence, including duplicate values and nested scopes. A typed empty/member guard can exclude an empty body; prose does not prove feasibility or termination. Summarize repeated definitions and collection contributions in a finite relation rather than allocating an unbounded input-ID chain. Preserve initial content, alternative per-occurrence yields, receiver/payload pairing, request/response identity and acquired-source provenance. Unknown repetition remains unknown, not a singleton execution. Exact singleton state updates may overwrite; aliased summary locations use possible updates. Prior boundary observations survive later overwrites. Loops do not prove precise cache counts or that an existing handle uses new credentials. Unexpanded recursive content remains an explicit precision limitation, not an empty value or evidence of necessity. Unsupported scope blocks its dependent continuation while independent branches may continue. Nested each paths follow actual member scopes; cardinality does not demand every member's contents. Summary computation is static may analysis, never Skill execution."),
    ("EM18", "Ordinary save/write default: when a source requires saving or writing a value but does not specify an update mode, the compact model interface may omit mode and the program expands it to replace. Explicit append, deletion or other supported source update semantics take priority. This is a public runtime abstraction, not an assertion that the source explicitly specifies overwrite. Keep the actual saved value and receiving location; unknown serialization alone does not erase this relation or stop following computation. A separately required format, ordering or representation property that is not expressed remains a specific limitation."),
)

# This is a compact audit inventory of the existing schemas, not an evaluator.
# Tests compare its closed vocabulary with AtomicOp/RawAtomicOp/FlatAtomicOp.
# Common obligations apply to every row; a row may specify a narrower domain.
_OPERATION_CONTRACT = {
    "columns": ["name", "level", "inputs", "outputs", "identity", "information", "effects"],
    "common": {
        "evidence": "Every declared operation cites source/CFG evidence or an applicable runtime rule. Unidentified addresses require physical source evidence and address_reason. Semantic input contracts require output sufficiency and input necessity evidence; actual use alone is insufficient.",
        "failure": "Unsupported concrete data/domain relations retain the original error and operation/IR/input scope; no fabricated value or silently dropped candidate. Dependent continuations remain unresolved. Unknown implementation/integrity faults and resource limits remain distinct from supported local data failures. Unfinished work is not proof of path infeasibility.",
        "schema": "Typed schemas remain authoritative for fields, arity, references, ordering and bounds. Known constructors/selectors/updates use deterministic operations, not opaque compute. Unsupported source behavior has an evidenced scoped processing gap; this finite vocabulary does not enumerate arbitrary Skill behavior.",
    },
    "expression_operators": {
        "ref": "Existing declared value/version; no acquisition or new operand.",
        "literal": "Exact JSON value, including distinct null/object/list forms.",
        "field": "Exact source field/index selection and required structure.",
        "present": "Presence, not payload value or generic truthiness.",
        "count": "Collection cardinality, not every member payload.",
        "not": "Boolean negation with the original predicate dependency.",
        "eq": "Typed equality of the two declared expressions.",
        "ne": "Typed inequality of the two declared expressions.",
        "lt": "Typed ordered comparison of declared expressions.",
        "le": "Typed ordered comparison of declared expressions.",
        "gt": "Typed ordered comparison of declared expressions.",
        "ge": "Typed ordered comparison of declared expressions.",
        "and": "Declared Boolean conjunction; preserve relevant controls.",
        "or": "Declared Boolean disjunction; preserve relevant controls.",
    },
    "rows": [
        ["read", "atomic", "declared state location", "current value candidates", "address alias policy; preserve versions", "value/shape of actual read", "context_read or fs_read"],
        ["receive", "atomic", "ordered request values + source", "fresh acquired value", "call/occurrence/source and request pairing", "response independent of request plaintext", "net_receive or tool/null"],
        ["deliver", "atomic", "ordered actual payload + target", "none", "recipient and payload occurrence paired", "action and actual observed value", "net_send/model_observe/user_output or tool/null"],
        ["write", "atomic", "target; zero/delete or one value", "state change, no value result", "identified definite replace/delete; otherwise weak", "value/action; append retains prior content", "context_write or fs_write"],
        ["select_part", "atomic", "value + field/index path", "existing selected part", "retain exact source/selector", "value/shape/presence of selected scope", "transform; missing part stays diagnostic"],
        ["exclude_parts", "atomic", "value + disjoint paths", "whole except paths", "retain base and exclusions", "remaining fields, not a sensitivity claim", "transform"],
        ["update_fields", "atomic", "base + nonoverlapping field values", "updated value", "retain unaffected parts and new versions", "selected replacements and residual structure", "transform"],
        ["build", "atomic", "field/index members; optional Boolean gates", "object or list", "retain actual member identities and gates", "value/shape/presence; contiguous list indexes", "transform; no implicit unknown fields"],
        ["compute", "atomic", "ordered declared values", "derived opaque value", "dependencies are influence, not passthrough", "exact expression or reviewed output-range rules", "transform or possible-dependency/null"],
        ["filter_items", "atomic", "collection + predicate", "subset view", "retain original member identity", "membership/control/cardinality separate from payload", "transform; prose predicate not executed"],
        ["merge", "atomic", "one value per actual predecessor", "selected incoming value", "predecessor correlated; not independent union", "preserve selected value and predecessor control", "transform or null"],
        ["member", "atomic", "collection", "scoped member", "original occurrence incl. duplicates", "member payload and membership", "transform or null; objects are not arrays"],
        ["branch", "atomic", "Boolean or typed collection predicate", "successor alternatives", "same predicate occurrence and targets", "truth/membership/cardinality, not all plaintext", "control; preserve unsupported candidate diagnostic"],
        ["append", "atomic", "collection + item or collection", "accumulated collection", "ordered occurrences and prior base", "payload/cardinality; item versus items", "transform or null"],
        ["call", "wire", "source + ordered request values", "response", "exact deliver/receive pair; no argument-based merging", "interface inputs and separate acquisition", "lowers to deliver + receive"],
        ["processing", "structure", "declared local/model/default operations", "locals + explicit local returns", "IR entry versions and lexical scope", "visibility derives from mode and actual reads", "ordered effects; local returns only"],
        ["for_each", "structure", "collection + lexical body", "optional paired yield/output collection", "member/source/occurrence pairing incl. duplicates", "membership/cardinality separate from member values", "empty body has no effects; bounded member scope"],
        ["cases", "structure", "actual call outcome alternatives", "yield on every returning case", "same protected invocation and member", "normal/error outcome plus actual prerequisites", "no network in pre_request_error; no invented catch"],
    ],
}


def runtime_contract(*, version=CONTRACT_VERSION) -> dict[str, Any]:
    """Return current rules or the pinned previous rule text for inspection."""
    if version not in (CONTRACT_VERSION, *_ARCHIVED):
        raise ValueError("Unsupported abstract runtime contract version")
    inventory = deepcopy(_OPERATION_CONTRACT)
    if version != LEGACY_CONTRACT_VERSION:
        inventory["common"]["selectors"] = (
            "A source-backed case guard tests an immutable entry operand and field path using an ordered finite "
            "partition. First matching test wins; the remaining domain is the final outcome. Known fields, scalar "
            "tags, absence, and nonempty strings have typed semantics. For unknown content preserve compatible "
            "choices. On the same immutable version and field, keep outcomes whose predicate decisions can "
            "hold together, including tests with different order or overlapping domains. Independent versions stay separate. "
            "Keep normal/exception routes, effect occurrences, and decision controls with their source evidence. "
            "An explicit branch can use the same typed selector on its actual operand; case names and prose "
            "cannot prove route compatibility.")
    if version in (_PLACEHOLDER_CONTRACT, _OUTCOME_CONTRACT, CONTRACT_VERSION):
        inventory["rows"].append(["placeholder", "atomic", "possible inputs", "value or effect",
            "site, versions, member", "possible influence", "optional weak write; no implied observation or delivery"])
    rules = dict(_RULES)
    if version in (_OUTCOME_CONTRACT, CONTRACT_VERSION):
        rules["EM11"] = (rules["EM11"].split("Selecting an explicit field with select_part")[0]
            + "A typed compute expression may project the exact value of an input field, test presence, "
              "or derive a scalar. A compute without an exact expression conveys input influence. "
              "A protected operation may bind its CFG completion flag and separate return or exception slots. "
              "The selected outcome carries its own state and only its available slots. The exception "
              "refers to this invocation. Its message contents require separate evidence.")
        rows = {row[0]: row for row in inventory["rows"]}
        rows["compute"][3:5] = ["exact projection, typed scalar, or opaque value",
                                 "same expression and input versions in both analysis directions"]
        rows["cases"][3] = "local returned yield or CFG completion with case-specific return/exception"
    if version == CONTRACT_VERSION:
        inventory["common"]["selectors"] = (
            "A source-backed guard tests a field of an immutable entry operand. The first matching test wins; "
            "the last outcome covers the remainder. Known fields, scalar tags, absence and nonempty strings "
            "have typed semantics. Unknown values retain compatible choices. For the same version and field, "
            "combine only compatible decisions, including tests with different order or overlapping domains. "
            "Independent versions stay separate. Retain route, effects, controls and source evidence. "
            "Branches can share a typed selector on the same operand; names and prose do not establish compatibility.")
    return {"version": version,
            "rules": [{"id": rule_id, "text": text} for rule_id, text in rules.items()],
            "operation_contract": inventory}


def _sha256(value: Any) -> str:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_runtime_contract(model: Any, *, read_only=False) -> dict[str, Any]:
    """Reject old, altered, or expanded rules; never silently substitute them."""
    version = model["version"] if read_only and isinstance(model, dict) and model.get("version") in _ARCHIVED else CONTRACT_VERSION
    expected = runtime_contract(version=version)
    if (type(model) is not dict or set(model) != {"version", "rules", "operation_contract"}
            or type(model.get("version")) is not str
            or model["version"] != version
            or type(model.get("rules")) is not list
            or any(type(rule) is not dict or set(rule) != {"id", "text"}
                   or type(rule["id"]) is not str or type(rule["text"]) is not str
                   for rule in model["rules"])
            or model != expected):
        raise ValueError("Abstract runtime contract identity mismatch: unsupported version or altered rules")
    return deepcopy(model)


def runtime_contract_binding(model: Any, *, read_only=False) -> dict[str, str]:
    """Bind the complete validated rule text using the recording digest format."""
    checked = validate_runtime_contract(model, read_only=read_only)
    return {"version": checked["version"], "sha256": _sha256(checked)}


def validate_runtime_contract_binding(binding: Any, *, read_only=False) -> dict[str, str]:
    """Validate the exact two-field identity of the supported contract."""
    version = binding["version"] if read_only and isinstance(binding, dict) and binding.get("version") in _ARCHIVED else CONTRACT_VERSION
    expected = runtime_contract_binding(runtime_contract(version=version), read_only=read_only)
    if (type(binding) is not dict or set(binding) != {"version", "sha256"}
            or any(type(binding[key]) is not str for key in binding)
            or binding != expected):
        raise ValueError("Abstract runtime contract binding mismatch: unsupported version or digest")
    return deepcopy(binding)
