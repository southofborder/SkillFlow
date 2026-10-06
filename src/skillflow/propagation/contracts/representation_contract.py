"""One versioned account of where represented relations are carried."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json

VERSION = "skillflow-representation-contract-v3"

_RULES = (
    ("REP01", "CFG facts: the graph carries actual instructions, operand positions, unique result definitions, instruction order, control edges, textual conditions, declarations and metadata. Read these facts together with the transfer specification; the specification is not a second complete CFG. Names and declarations do not substitute for missing operations or explicit data relations."),
    ("REP02", "Ordinary return: a return terminator's CFG inputs identify the returned values. It has no public result outputs. Its transfer events and output_bindings may both be empty without losing that return identity. Inspect the actual CFG inputs before claiming forwarding is absent. Do not invent output index zero, user_output, network delivery, or a null-effect deliver to express an ordinary return. The caller's internal receiving state is not separately modeled. A wrong CFG return identity remains a real difference, but cannot be repaired by changing annotation to contradict the CFG."),
    ("REP03", "Transfer facts: acquisition scope, exact field/index selection, unchanged filter members, content changes, computed dependencies, explicit state writes and actual interaction arguments must be represented by supported typed transfer operations and value references. A result name in the CFG alone does not supply these relations. output_bindings bind exactly the existing public outputs, including unchanged values, without performing hidden transformations or context writes."),
    ("REP04", "Observation compilation: raw processing modes and references determine compiler-generated observations. Review the actual observed versions and their mapping to raw segments. Observations are contract-supported possible behavior, not measured execution. Do not demand an independently handwritten model_observe in raw effects, mechanically add llm or sink for every generated observation, or allow later cleanup to replace an earlier observed version."),
    ("REP05", "Effect boundaries: empty effects do not mean a no-op or identical entry and exit states. A known tool acquisition can use receive at a tool location without claiming networking; actual tool request arguments use a separate deliver at that tool boundary in a null-effect event when networking is not established. Request dependencies in receive are not that delivery. Resource locators are not automatically payloads. Ordinary return is not necessarily user-facing. Absence of a concrete network interface is not absence of a known acquisition or request delivery, and an unmodeled caller boundary is not an omitted supported effect."),
    ("REP06", "Permitted abstraction and limitations: possible dependency is not plaintext containment; candidate values are not a constructed object or simultaneous arguments. A source whole can exist without being observed. Open content, opaque computation, contract defaults and supported partial ordering are normal analysis inputs. Neither exact execution success nor a complete implementation must be invented to annotate them. Report material differences in scope, identity, dependencies, version or boundary, not wording alone. If a necessary distinction really cannot be represented, state a task failure rather than inventing unsupported operations."),
    ("REP07", "Sink ownership: location declarations carry access_scope and retention once, with their original location evidence table. The model does not output sink_boundaries, sink_type or exposure_level. The program derives the complete sink list from compiled deliver/write operations and location properties, keeping IR/event/operation positions and element scopes, but not another copy of symbolic or propagated inputs. Compiled observations are collected even without a sink role. Internal/task-limited relations remain in propagation while level 0 is excluded from the sink list. Boundary levels express access and retention, not data sensitivity or a DOE verdict. A review checks the model's property claims and their evidence; deterministic classification cannot prove those claims correct."),

    ("REP08", "Conditional construction: build members carry their field path, original value reference and optional Boolean when reference. Their values and control inputs have separate roles. A false condition omits a member, not a null value; abstract Boolean conditions retain candidate shapes with shared decisions for identical controls. Compiled observation guards use those same controls. Resolved records preserve member-to-input indexes and generated-observation control indexes without another copy of Data identities. Payload extraction excludes control slots. Data contents describe the constructed business fields while operation inputs may also preserve controls and their applicable dependence; influence is not plaintext membership."),
    ("REP09", "Shared request identity: deliver and its corresponding receive must use the same ordered request references at the same IR, scope and declared boundary. The program resolves unique associations and reuses actual delivered bindings for acquisition dependencies. Parameter shape does not assert a concrete JSON serialization. A possible external tool receiver is not proof of a network transport: remote and network effects require an evidenced communication mechanism. Sender/recipient names or an action verb are not that mechanism."),

)


def representation_contract() -> dict:
    return {"version": VERSION, "rules": [{"id": key, "text": value} for key, value in _RULES]}


def binding() -> dict[str, str]:
    serialized = json.dumps(representation_contract(), ensure_ascii=False, sort_keys=True,
                            separators=(",", ":"), allow_nan=False)
    return {"version": VERSION, "sha256": hashlib.sha256(serialized.encode("utf-8")).hexdigest()}


def validate(value) -> dict:
    if value != representation_contract():
        raise ValueError("Representation contract identity mismatch")
    return deepcopy(value)
