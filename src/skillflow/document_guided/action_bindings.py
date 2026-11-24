"""Bind source actions to exact submitted processing coordinates."""
from collections import Counter
from typing import Annotated

from pydantic import Field, ValidationError

from skillflow.common.source_evidence import json_pointer, validate_source_ref
from skillflow.common.validation import StructuralValidationError, structural_error
from skillflow.propagation.contracts.references import cfg_instructions
from skillflow.propagation.contracts.task import task_source_files
from skillflow.propagation.contracts.values import Text
from .graph_facts import SourceAction

ActionBindings = dict[Text, list[list[Text | Annotated[int, Field(strict=True, ge=0)]]]]


def action_coordinates(record):
    """Iteration order is execution order within each feasible case and loop body."""
    def walk(segments, prefix, choices):
        for i, segment in enumerate(segments):
            path = (*prefix, i)
            for j, _ in enumerate(segment.get("ops", [])):
                yield (*path, "ops", j), choices
            for j, case in enumerate(segment.get("cases", [])):
                branch = {**choices, path: j}
                guard = "guard" if case.get("guard") is not None else "condition"
                yield (*path, "cases", j, guard), branch
                yield from walk(case.get("segments", []), (*path, "cases", j, "segments"), branch)
                if "yield" in case:
                    yield (*path, "cases", j, "yield"), branch
                if case.get("disposition") == "throw":
                    yield (*path, "cases", j, "disposition"), branch
            if "body" in segment:
                yield (*path, "collection"), choices
                yield from walk(segment["body"], (*path, "body"), choices)
                if "yield" in segment:
                    yield (*path, "yield"), choices
            for j, _ in enumerate(segment.get("returns", [])):
                yield (*path, "returns", j), choices
    yield from walk(record.get("segments", []), ("segments",), {})
    for i, _ in enumerate(record.get("output_bindings", [])):
        yield ("output_bindings", i), {}


BOUNDARY_ROLES = {"call", "receive", "deliver", "read", "write", "loop", "branch"}


def _at(root, path):
    for token in path:
        root = root[token]
    return root


def verified_split_calls(ir, raw_spec, wire_paths, record):
    """Project only actual backend request/response pairs to their flat operations."""
    from skillflow.propagation.contracts.specs import RawIRSemantics, _raw_event_paths, flatten_raw_spec
    from skillflow.propagation.contracts.uses import request_pairs
    from skillflow.common.recording import canonical_sha256

    typed = RawIRSemantics.model_validate(raw_spec)
    flattened = flatten_raw_spec(typed)
    lowered = _raw_event_paths(typed)
    prefix = json_pointer("ir_semantics", ir)
    def position(key):
        outer, body, op = key
        event = json_pointer("events", outer) if body is None else json_pointer("events", outer, "body", body)
        pointer = wire_paths.get(prefix + lowered[event] + json_pointer("atomic_ops", op))
        if pointer is None or not pointer.startswith(prefix + "/"):
            return None
        return tuple(int(part) if part.isdigit() else part for part in pointer[len(prefix) + 1:].split("/"))

    pairs = {}
    for response, request in request_pairs(flattened).items():
        send, receive = position(request), position(response)
        if send is None or receive is None or send == receive:
            continue  # A canonical "call" maps both lowered coordinates to itself.
        # The flat wire preserves a case/member occurrence more precisely than
        # the backend pairing key. An endpoint in another alternative cannot
        # witness this syntactic action.
        def occurrence(path):
            return tuple(path[:i + (2 if part == "cases" else 1)]
                         for i, part in enumerate(path) if part in {"cases", "body"})
        if occurrence(send) != occurrence(receive):
            continue
        request_op, response_op = _at(record, send), _at(record, receive)
        if (request_op.get("op") == "deliver" and response_op.get("op") == "receive"
                and request_op.get("input_contract") is not None
                and canonical_sha256(request_op["input_contract"]) == canonical_sha256(response_op.get("input_contract"))):
            pairs[receive] = send
    return pairs


def _role_errors(record, instruction, processing, ref, role, paths, split_calls=None, *, context_acquisition=False):
    """Prove presence on normal alternatives without enumerating path products.

    Each case group is a disjunction. An unconditional operation, or one
    group whose applicable alternatives all contain the operation, suffices.
    Different loop bodies are separate member domains.
    """
    selected = {tuple(path) for path in paths}
    locations = processing.get("locations", {})
    interface_roles = {"call", "receive", "deliver"}
    def witness(path, phase="normal"):
        if path not in selected:
            return False
        if path == ("terminator",):
            return role == "branch" and instruction["opcode"] == "dispatch"
        if path[-1] == "collection":
            return role == "loop"
        if path[-1] in {"guard", "condition"}:
            return role == "branch"
        if context_acquisition and role == "receive" and path[0] == "output_bindings":
            return _at(record, path)["value"].get("kind") == "input"
        if len(path) < 2 or path[-2] != "ops":
            return False
        op = _at(record, path)
        kind = op["op"]
        location = op.get("location", op.get("target"))
        boundary = locations.get(location, {}).get("kind") if isinstance(location, str) else None
        if role in {"read", "write"}:
            return kind == role and boundary in {"runtime_context", "storage"}
        if role == "branch":
            return kind == "branch"
        if role == "loop":
            return False
        if role == "call":
            paired = kind == "receive" and split_calls is not None and split_calls.get(path) in selected
            return boundary in {"tool", "remote"} and (kind == "call" or paired or phase == "post_request_error" and kind == "deliver")
        if role == "receive":
            if context_acquisition:
                from .entry_transfers import _read_index
                if _read_index(op, instruction, locations) is not None:
                    return True
                if kind == "select_part" and op["input"]["kind"] == "input":
                    return True
            return kind in {"call", "receive"} and boundary in {"user", "tool", "remote"}
        return kind in {"call", "deliver"} and boundary in {"tool", "remote", "user", "model_context"}

    def reached(segments, base, phase="normal"):
        for i, seg in enumerate(segments):
            seg_path = (*base, i)
            if any(witness((*seg_path, "ops", j), phase) for j in range(len(seg.get("ops", [])))):
                return True
            if "cases" in seg:
                valid_cases = []
                for j, case in enumerate(seg["cases"]):
                    phase_here = case["phase"]
                    if role in interface_roles and phase_here == "pre_request_error":
                        continue
                    if role == "receive" and phase_here == "post_request_error" and case["disposition"] == "throw":
                        continue
                    case_path = (*seg_path, "cases", j)
                    guard = "guard" if case.get("guard") is not None else "condition"
                    valid_cases.append(witness((*case_path, guard)) or
                                       reached(case.get("segments", []), (*case_path, "segments"), phase_here))
                if valid_cases and all(valid_cases):
                    return True
            if seg.get("kind") == "for_each" and witness((*seg_path, "collection")):
                return True
        return False

    if (witness(("terminator",)) or reached(record.get("segments", []), ("segments",))
            or any(witness(p) for p in selected if p[:1] == ("output_bindings",))):
        return []
    # Iteration-local semantics must hold inside every body representing this
    # action. A known operation in another collection cannot satisfy its peer.
    bodies = {path[:path.index("body") + 1] for path in selected if "body" in path}
    outside = [path for path in selected if path[:1] == ("segments",) and "body" not in path
               and len(path) > 1 and path[-2] == "ops"]
    if bodies and not outside:
        missing = [path for path in sorted(bodies) if not reached(_at(record, path), path)]
        if not missing:
            return []
        scope = ", ".join(json_pointer(*p) for p in missing)
    else:
        scope = "the instruction's applicable control paths"
    return [f"Source action {ref!r} requires a real {role} at {scope}. A placeholder, output forwarding, "
            "or an operation in another alternative cannot establish this boundary. "
            "Use its actual declared location and interface inputs where required."]


def recover_linear_bindings(record, instruction, processing):
    """Return a unique source/role/order alignment, or explain what is missing.

    Only straight-line producers and their direct returned locals qualify.
    Repeated action kinds are legal. Dynamic programming counts up to two
    alignments without enumerating every way to divide the operation stream.
    """
    from .annotation_wire import nearest_source_evidence
    from .graph_facts import source_action_role

    actions = instruction.get("metadata", {}).get("source_actions") or record.get("source_actions", [])
    names = [a["ref"] for a in actions]
    positions = list(action_coordinates(record))
    def abstain(reason):
        return None, (f"Source actions {names}: {reason}. Original physical operations and their evidence remain "
                      "at the same /ir_semantics instruction in the immutable submitted processing candidate.")
    if len(names) < 2 or record.get("order") == "partial":
        return abstain("a unique fixed action order is unavailable")
    producers, forwarding, candidates, op_paths = {}, [], [], []
    for path, _ in positions:
        if path[0] == "output_bindings" or path[-2] == "returns":
            val = _at(record, path)
            val = val.get("value") if path[0] == "output_bindings" else val
            if not isinstance(val, dict) or val.get("kind") != "local":
                return abstain(f"output {json_pointer(*path)} does not identify one local producer")
            forwarding.append((path, val["name"]))
            continue
        if len(path) != 4 or path[2] != "ops":
            return abstain(f"the branch/member occurrence at {json_pointer(*path)} needs an explicit source binding")
        op = _at(record, path)
        kind = op["op"]
        if kind == "placeholder":
            roles = {"value"} if op["kind"] == "value" else {"other"}
        elif kind == "call":
            roles = {"call", "receive", "deliver"}
        else:
            roles = {kind if kind in BOUNDARY_ROLES else "value"}
        ev, _ = nearest_source_evidence(record, path)
        matches = []
        for i, action in enumerate(actions):
            if source_action_role(action) not in roles:
                continue
            span = action["source"]
            if any(ref["file"] == span["file"] and ref["start_line"] <= span["end_line"]
                   and ref["end_line"] >= span["start_line"] for ref in ev):
                matches.append(i)
        if not matches:
            return abstain(f"no source- and role-matched action exists at {json_pointer(*path)}")
        candidates.append(matches)
        op_paths.append(path)
        output = op.get("output")
        if output:
            if output in producers:
                return abstain(f"more than one operation produces local {output!r}")
            producers[output] = len(op_paths) - 1
    if instruction["opcode"] in {"dispatch", "return"}:
        return abstain("the CFG terminator needs an explicit action owner")
    if not candidates or any(local not in producers for _, local in forwarding):
        return abstain("an output lacks its unique source-backed producer")
    counts, parents = {-1: 1}, []
    for matches in candidates:
        next_counts, links = {}, {}
        for i in matches:
            choices = [prev for prev in (i-1, i) if prev in counts]
            n = sum(counts[prev] for prev in choices)
            if n:
                next_counts[i] = min(n, 2)
                if n == 1:
                    links[i] = choices[0]
        parents.append(links)
        counts = next_counts
    owner = len(names) - 1
    if counts.get(owner) != 1:
        choices = {json_pointer(*p): [names[i] for i in rows] for p, rows in zip(op_paths, candidates, strict=True)}
        return abstain(f"there is no unique monotone complete match for {choices}")
    assigned = []
    for links in reversed(parents):
        assigned.append(owner)
        owner = links[owner]
    assigned.reverse()
    grouping = {name: [] for name in names}
    for path, i in zip(op_paths, assigned, strict=True):
        grouping[names[i]].append(list(path))
    for path, local in forwarding:
        grouping[names[assigned[producers[local]]]].append(list(path))
    return grouping, None


def checked_action_bindings(processing, material, *, raw_specs=None, wire_paths=None):
    instructions, result, errors = cfg_instructions(material["cfg"]), {}, []
    from .entry_transfers import acquisition_ports, entry_binding_errors, location_errors
    entries = acquisition_ports(material)
    errors.extend(location_errors(entries, processing.get("locations", {})))
    context_acquisitions = {b["instructions"][0]["id"] for b in material["cfg"]["blocks"].values()
                            if b.get("data_source_kind") == "context" and b.get("instructions")}
    files = None
    for ir, record in processing.get("ir_semantics", {}).items():
        if ir not in instructions:
            continue
        cfg = instructions[ir]
        if ir in entries:
            errors.extend(entry_binding_errors(cfg, entries[ir][1], record, processing.get("locations", {})))
        declared = cfg.get("metadata", {}).get("source_actions", [])
        supplied = record.get("source_actions", [])
        prefix = json_pointer("ir_semantics", ir)
        def error(code, field, message, **context):
            errors.extend(structural_error(code, prefix + "/" + field, message, **context).diagnostics)
        def role_error(field, message, bound):
            ops = [json_pointer(*p) for p in bound if len(p) >= 2 and p[-2] == "ops"
                   and _at(record, p).get("op") == "placeholder"]
            error("source_action_role", field, message, placeholder_operations=ops)
        if declared and supplied:
            error("source_action_inventory", "source_actions", "This IR already has a CFG-owned source action inventory.")
            continue
        actions = declared or supplied
        from .graph_facts import source_action_role
        pairs = None
        def role_diagnostics(name, role, bound):
            nonlocal pairs
            if role == "call" and raw_specs is not None and pairs is None and any(
                    len(p) >= 2 and p[-2] == "ops" and _at(record, p).get("op") == "receive" for p in bound):
                try:
                    pairs = verified_split_calls(ir, raw_specs[ir], wire_paths, record)
                except (ValidationError, StructuralValidationError):
                    # The ordinary backend validator still reports the original
                    # malformed or ambiguous request. It cannot witness a call.
                    pairs = {}
            return _role_errors(record, cfg, processing, name, role, bound, pairs,
                                context_acquisition=ir in context_acquisitions)
        if not actions:
            role = source_action_role({"kind": cfg["opcode"]})
            if role in BOUNDARY_ROLES:
                coords = [path for path, _ in action_coordinates(record)]
                if cfg["opcode"] == "dispatch":
                    coords.append(("terminator",))
                for message in role_diagnostics(ir, role, coords):
                    role_error("action_bindings" if supplied else "segments", message, coords)
            if record.get("action_bindings") is not None:
                error("source_action_inventory", "source_actions", "Bindings need existing CFG actions or a source-located legacy inventory.")
            continue
        if files is None:
            files = task_source_files(material["source"])
        try:
            parsed = [SourceAction.model_validate(row) for row in actions]
            for row in parsed:
                validate_source_ref(row.source.model_dump(), files)
        except (TypeError, ValueError, ValidationError) as exc:
            error("source_action_inventory", "source_actions", "Invalid source-action row or physical span: " + str(exc))
            continue
        refs = [row.ref for row in parsed]
        if len(refs) != len(set(refs)):
            error("source_action_inventory", "source_actions", "Each source-action ref must be unique inside this IR.")
            continue
        coords = list(action_coordinates(record))
        # An empty CFG terminator still selects its real successor or returns.
        if cfg["opcode"] in {"dispatch", "return"}:
            coords.append((("terminator",), {}))
        paths = [p for p, _ in coords]
        binding = record.get("action_bindings")
        if binding is None and len(refs) == 1 and paths:
            binding = {refs[0]: [list(p) for p in paths]}
        if not isinstance(binding, dict) or set(binding) != set(refs):
            error("source_action_binding", "action_bindings",
                  f"Account for these source actions exactly once: {refs}. Bind their actual operations and output coordinates.")
            continue
        owners = {}
        counts = Counter()
        for ref in refs:
            if not binding[ref]:
                error("source_action_binding", "action_bindings", f"Action {ref} requires its executable operation, output or terminator.")
            for path in binding[ref]:
                pos = tuple(path)
                counts[pos] += 1
                owners[pos] = ref
        if set(paths) != set(owners) or any(count != 1 for count in counts.values()):
            error("source_action_binding", "action_bindings",
                  "Bind every actual operation, selected case test/throw, loop collection, return, yield, output binding and terminator to exactly one action. "
                  f"Missing {sorted(map(str, set(paths) - set(owners)))}. Invalid or repeated "
                  f"{sorted(map(str, {p for p,c in counts.items() if p not in paths or c != 1}))}.")
            continue
        roles = set()
        for index, row in enumerate(parsed):
            try:
                role = source_action_role(row.model_dump(mode="json", exclude_none=True))
            except ValueError as exc:
                error("source_action_inventory", f"source_actions/{index}/role", str(exc))
                continue
            roles.add(role)
            if supplied and role is None:
                error("source_action_inventory", f"source_actions/{index}/role",
                      "Use an explicit source role when supplying a new action with a free-text kind.")
            if role in BOUNDARY_ROLES:
                for message in role_diagnostics(row.ref, role, binding[row.ref]):
                    role_error("action_bindings", message, binding[row.ref])
        primary = source_action_role({"kind": cfg["opcode"]})
        if primary in BOUNDARY_ROLES and primary not in roles:
            error("source_action_inventory", "source_actions", "The action inventory omits the CFG instruction's declared " + primary + " role.")
        # Output bindings describe forwarding after execution, not another chronological action.
        ranks = {ref:i for i,ref in enumerate(refs)}
        sequence = [(ranks[owners[p]], choices) for p, choices in coords if p[0] != "output_bindings"]
        if len(refs) > 1 and (record.get("order") == "partial" or any(
                a > b and all(k not in y or y[k] == v for k,v in x.items())
                for i,(a,x) in enumerate(sequence) for b,y in sequence[i+1:])):
            error("source_action_order", "action_bindings", "Operations on the same executable path must follow the source-action order.")
            continue
        result[ir] = {"actions": actions, "bindings": binding}
    if errors:
        raise StructuralValidationError(errors)
    return result
