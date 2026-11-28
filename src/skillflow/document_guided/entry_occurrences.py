"""Match context operands to physical invocation sites in the frozen source."""
from __future__ import annotations

import ast
from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
import re

from skillflow.common.recording import canonical_sha256


ENTRY_OCCURRENCE_RULES = (
    "Acquire values supplied by the same physical invocation or read together. Cite its signature or "
    "actual read site. Keep different public invocation signatures, module evaluation and direct execution "
    "on their own activation paths, including before a common helper. A selector is not a bundle of values "
    "from all routes. On each route bind actual arguments to that invocation's own results; preserve "
    "omission and source-backed forwarding of the same argument to multiple internal calls. A single "
    "source object may supply several fields. Use existing operands, result references, actions and edges."
)


@dataclass(frozen=True)
class Signature:
    file: str
    first: int
    last: int
    name: str
    parameters: tuple[tuple[str, bool], ...]
    variadic: bool = False
    body_end: int | None = None

    @property
    def source(self):
        return {"file": self.file, "start_line": self.first, "end_line": self.last}

    @property
    def owner(self):
        return f"{self.file}:{self.first}:{self.name}"


_JS_DECLARATION = re.compile(
    r"^[ \t]*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+"
    r"(?P<name>[A-Za-z_$][\w$]*)\s*\((?P<params>[^()]*)\)", re.MULTILINE)
_JS_NONCODE = re.compile(r'''//[^\n]*|/\*[\s\S]*?\*/|'(?:\\.|[^'\\\n])*'|"(?:\\.|[^"\\\n])*"|`(?:\\.|[^`\\])*`''')
_JS_PARAMETER = re.compile(r"\s*([A-Za-z_$][\w$]*)\s*(\?)?\s*(?::[^=]+)?(?:=(.+))?\s*\Z", re.DOTALL)
_EXTENSIONS = (".js", ".ts", ".jsx", ".tsx", ".mjs", ".mts", ".cjs", ".cts")


def _masked_js(match):
    blank = re.sub(r"[^\n]", " ", match.group())
    return blank if match.group().startswith("/") else "0" + blank[1:]


def _parameter_parts(raw):
    closes = {"{": "}", "[": "]", "<": ">"}
    pending, parts, start = [], [], 0
    for i, char in enumerate(raw):
        if char in closes:
            pending.append(closes[char])
        elif char in "}]>":
            if not pending or pending.pop() != char:
                return None
        elif char == "," and not pending:
            parts.append(raw[start:i])
            start = i + 1
    return None if pending else [part for part in [*parts, raw[start:]] if part.strip()]


def _body_end(masked, offset):
    # Accept an ordinary body or a simple TS named/generic return type.
    # Ambiguous regex/division or inline return-type syntax needs source review.
    start = re.match(r"\s*(?::\s*[\w$., |&\[\]<>]+\s*)?\{", masked[offset:])
    if not start:
        return None
    depth = 1
    for token in re.finditer(r"[{}/]", masked[offset + start.end():]):
        if token[0] == "/":
            return None
        depth += 1 if token[0] == "{" else -1
        if depth == 0:
            end = offset + start.end() + token.start()
            return masked.count("\n", 0, end) + 1
    return None


@lru_cache(maxsize=64)
def _signatures(file, text):
    # Recognize only declarations with unambiguous parameter boundaries. The
    # general source-action and control checks below also work for prose inputs.
    if file.endswith(".py"):
        try:
            tree = ast.parse(text)
        except (SyntaxError, ValueError):
            return ()
        rows = []
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            args = node.args
            positional = [*args.posonlyargs, *args.args]
            params = [(arg.arg, i >= len(positional) - len(args.defaults)) for i, arg in enumerate(positional)]
            params += [(arg.arg, default is not None) for arg, default in zip(args.kwonlyargs, args.kw_defaults)]
            last = max([node.lineno, *(arg.end_lineno for arg in [*positional, *args.kwonlyargs])])
            rows.append(Signature(file, node.lineno, last, node.name, tuple(params),
                                  bool(args.vararg or args.kwarg), node.end_lineno))
        return tuple(rows)
    if not file.endswith(_EXTENSIONS):
        return ()
    # Preserve character offsets and newlines while ignoring declarations in
    # comments and literals. Nested/destructured parameters require review.
    masked = _JS_NONCODE.sub(_masked_js, text)
    rows = []
    for match in _JS_DECLARATION.finditer(masked):
        raw = masked[match.start("params"):match.end("params")].strip()
        parts = _parameter_parts(raw)
        if parts is None:
            continue
        parsed = [_JS_PARAMETER.fullmatch(part) for part in parts]
        if any(part is None for part in parsed):
            continue
        params = tuple((part[1], bool(part[2] or "=" in part[0])) for part in parsed)
        rows.append(Signature(file, masked.count("\n", 0, match.start()) + 1,
                              masked.count("\n", 0, match.end()) + 1, match["name"], params,
                              body_end=_body_end(masked, match.end())))
    return tuple(rows)


def _source_span(span, files):
    return (isinstance(span, dict) and isinstance(span.get("file"), str) and span["file"] in files
            and type(span.get("start_line")) == type(span.get("end_line")) == int
            and 0 < span["start_line"] <= span["end_line"])


def _sites(span, files):
    if not _source_span(span, files):
        return ()
    first, last = span["start_line"], span["end_line"]
    return tuple(s for s in _signatures(span["file"], files[span["file"]]) if first <= s.first <= last)


def _body_owner(span, files):
    if not _source_span(span, files):
        return None
    enclosing = [s for s in _signatures(span["file"], files[span["file"]]) if s.body_end is not None
                 and s.first <= span["start_line"] <= span["end_line"] <= s.body_end]
    if not enclosing:
        return None
    innermost = max(enclosing, key=lambda s: s.first)
    return innermost if sum(s.first == innermost.first for s in enclosing) == 1 else None


def _tail(name):
    return re.split(r"[.:/]", name)[-1]


def declaration_only(span, files):
    sites = _sites(span, files)
    if len(sites) != 1 or span["start_line"] != sites[0].first or span["end_line"] > sites[0].last:
        return False
    lines = files[span["file"]].splitlines()
    return lines[span["end_line"] - 1].strip().endswith(("{", ":"))


def _read_actions(instruction):
    metadata = instruction.get("metadata", {})
    authored = instruction.get("source_actions")
    if authored:
        return authored
    inherited = metadata.get("source_actions")
    if (instruction.get("source") is None and isinstance(inherited, list) and inherited
            and all(isinstance(a, dict) and isinstance(a.get("kind"), str) and
                    isinstance(a.get("source"), dict) and
                    set(("file", "start_line", "end_line")) <= a["source"].keys() for a in inherited)):
        return inherited
    return [
        {"kind": instruction["opcode"], "role": instruction.get("role"),
         "source": instruction.get("source") or metadata.get("source_span")}]


def _same_signature(spans, files):
    if not spans or any(not _source_span(s, files) for s in spans):
        return None
    file = spans[0]["file"]
    if any(s["file"] != file for s in spans):
        return None
    return next((s for s in _signatures(file, files[file])
                 if all(s.first <= a["start_line"] <= a["end_line"] <= s.last for a in spans)), None)


def callable_signature_ports(instruction, files):
    """Return proven direct formal-to-result bindings; accept raw and canonical IR."""
    actions = _read_actions(instruction)
    if not all((a.get("role") or a["kind"]) == "receive" for a in actions):
        return []
    spans = [a.get("source") for a in actions]
    site = _same_signature(spans, files)
    if not site and len(actions) == 1 and (sites := _sites(spans[0], files)):
        if len(sites) == 1 and sites[0].first == spans[0]["start_line"]:
            site = sites[0]
    if not site:
        return []
    inputs, outputs = instruction.get("inputs", []), instruction.get("outputs", [])
    keys = [op.get("context_key") or (op.get("identifier") if op.get("type") == "context_key" else None)
            for op in inputs]
    if not keys or not all(keys):
        return []
    labels = [op if isinstance(op, str) else op.get("semantic_name") or op["identifier"] for op in outputs]
    bindings = []
    for param, optional in site.parameters:
        matches = [i for i, name in enumerate(keys) if _tail(name) == param]
        if len(matches) != 1:
            continue
        found = [i for i, name in enumerate(labels) if _tail(name) == param]
        snapshot = instruction.get("metadata", {}).get("python_argument_snapshot")
        if (isinstance(snapshot, dict) and snapshot.get("parameter") == param and optional
                and snapshot.get("input_index") == matches[0] and type(snapshot.get("output_index")) is int
                and 0 <= snapshot["output_index"] < len(labels)):
            found = [snapshot["output_index"]]
        if not found and len(keys) == len(labels) == len(site.parameters) == 1:
            found = [0]
        if len(found) == 1:
            port = {"input_index": matches[0], "output_index": found[0], "parameter": param,
                    "optional": optional, "owner": site.owner, "source": site.source}
            if len(actions) > 1:
                source_lines = files[site.file].splitlines()
                anchors = [a["ref"] for a in actions if a.get("ref") and param in _tokens(
                    "\n".join(source_lines[a["source"]["start_line"] - 1:a["source"]["end_line"]]))]
                if len(anchors) == 1:
                    port["action_ref"] = anchors[0]
            bindings.append(port)
    return bindings


def _uses(block):
    values = [v for op in block["operations"] for v in op["inputs"]]
    exit = block["exit"]
    values.extend(exit.get("conditions", exit.get("values", exit.get("inputs", []))))
    return {v["result"] for v in values if "result" in v}


def _tokens(text):
    return set(re.findall(r"(?<![\w$])[A-Za-z_$][\w$]*", text))


def signature_obligations(blocks, bi, oi, scope, sites, files):
    """Bind only formals evidenced in this occurrence or used by its sourced consumer."""
    op = blocks[bi]["operations"][oi]
    keys = [v["context_key"] for v in op["inputs"] if "context_key" in v]
    labels = {_tail(k) for k in keys}
    result_formals = {v: _tail(v) for v in op["outputs"] if _tail(v) in labels}
    for port in callable_signature_ports(op, files):
        result_formals[op["outputs"][port["output_index"]]] = port["parameter"]
    evidence = defaultdict(set)
    for i in scope:
        for other in blocks[i]["operations"]:
            actual = {result_formals[v["result"]] for v in other["inputs"] if v.get("result") in result_formals}
            if not actual:
                continue
            for action in _read_actions(other):
                span = action.get("source")
                for owner in {*_sites(span, files), _body_owner(span, files)} - {None}:
                    evidence[owner].update(actual)
    rows = []
    for site in sites:
        named = {_tail(k) for k in keys if site.name in re.split(r"[.:/]", k)[:-1]}
        if any(s.get("source") == site.source for s in _read_actions(op)):
            named.update(labels)
        used = evidence[site] | named
        rows.append(site.source | {"name": site.name, "parameters": [p for p, _ in site.parameters if p in used]})
    return rows


def occurrence_conflicts(facts, files):
    """Return separate activation evidence and the consumers of the suspect results."""
    blocks = facts["blocks"]
    used = [_uses(block) for block in blocks]
    # A branch name alone is not a source owner. Resolve it against a real
    # declaration and an actual result used to select the branch.
    signatures = [s for file, text in files.items() for s in _signatures(file, text)]
    by_name = defaultdict(list)
    for site in signatures:
        by_name[site.name].append(site)
    for bi, block in enumerate(blocks):
        if block["source_kind"] != "context":
            continue
        for oi, op in enumerate(block["operations"]):
            keys = [v["context_key"] for v in op["inputs"] if "context_key" in v]
            if not keys:
                continue
            actions = _read_actions(op)
            reads = [a for a in actions if (a.get("role") or a["kind"]) in {"receive", "read"}]
            spans = [a["source"] for a in reads if _source_span(a.get("source"), files)]
            if not spans:
                continue
            observed = set(op["outputs"])
            consumers = {i for i, values in enumerate(used) if observed & values}
            branches = {i for i in consumers if blocks[i]["exit"]["kind"] == "branch" and
                        any(v.get("result") in observed for v in blocks[i]["exit"]["conditions"])}
            names = {name for i in branches for arm in blocks[i]["exit"]["arms"]
                     for name in _tokens(arm.get("condition") or "")}
            direct = {s for span in spans for s in _sites(span, files)}
            consumers_sites = {s for i in consumers for action in blocks[i]["operations"]
                               if any(v.get("result") in observed for v in action["inputs"])
                               for s in _sites(action.get("source") or action.get("metadata", {}).get("source_span"), files)}
            branch_sites = {s for i in branches for s in _sites(
                blocks[i]["exit"].get("source") or blocks[i]["exit"].get("metadata", {}).get("source_span"), files)}
            selected = {by_name[n][0] for n in names if len(by_name[n]) == 1} & (direct | consumers_sites | branch_sites)
            matched = {s for s in selected if any(p == _tail(key) for p, _ in s.parameters for key in keys)}
            # Even disconnected exported functions can be named independently
            # in the claimed operands. Require corroboration at both the actual
            # declaration and the input's formal; no spelling-only partition.
            named = {s for s in direct for key in keys if s.name in re.split(r"[.:/]", key)[:-1]
                     and any(p == _tail(key) for p, _ in s.parameters)}
            matched |= named
            # If the anchor is a single, exact callable signature, each claimed
            # direct argument must be possible at that site. Several projections
            # of ONE supplied object have only one raw input. Reusing the same
            # actual key in two slots still constitutes just one raw input.
            exact = len(direct) == 1 and len(spans) == 1 and spans[0]["start_line"] == next(iter(direct)).first
            excess_formals = (exact and not next(iter(direct)).variadic
                              and len(set(keys)) > len(next(iter(direct)).parameters)
                              and (reads[0].get("role") or reads[0]["kind"]) == "receive")
            if excess_formals:
                matched |= direct
            distinct_spans = {(span["file"], span["start_line"], span["end_line"]) for span in spans}
            multiple_reads = len(distinct_spans) > 1 and not _same_signature(spans, files) and not any(
                a != b and a[0] == b[0] and a[1] <= b[2] and b[1] <= a[2]
                for a in distinct_spans for b in distinct_spans)
            if not (multiple_reads or excess_formals or len(keys) > 1 and len(direct) > 1 and len(matched) > 1):
                continue
            if excess_formals:
                site = next(iter(direct))
                message = (f"The cited signature {site.owner} declares {len(site.parameters)} formal arguments. "
                           f"The acquisition claims {len(set(keys))} distinct direct input keys.")
            elif multiple_reads:
                message = "The acquisition combines separately sourced reads at different physical locations."
            else:
                message = "The acquisition pools arguments belonging to separately selected source invocations."
            yield (bi, oi, sorted(consumers | {bi}), sorted(matched, key=lambda s: (s.file, s.first)), spans,
                   message + " Bind arguments and results where each call or read occurs.")
    yield from _crossed_invocations(blocks, used, files, signatures)


def _crossed_invocations(blocks, used, files, signatures):
    """Check a raw formal whose direct consumer cites another public callable's body."""
    acquisitions = {}
    for bi, block in enumerate(blocks):
        if block["source_kind"] != "context":
            continue
        for oi, op in enumerate(block["operations"]):
            for port in callable_signature_ports(op, files):
                result = op["outputs"][port["output_index"]]
                acquisitions[result] = bi, oi, port["owner"]
    owners = {owner for _, _, owner in acquisitions.values()}
    if len(owners) < 2:
        return
    declarations = {s.owner: s for s in signatures if s.owner in owners}
    for ci, block in enumerate(blocks):
        for cj, op in enumerate(block["operations"]):
            direct = {v["result"] for v in op["inputs"] if v.get("result") in acquisitions}
            if not direct:
                continue
            actions = _read_actions(op)
            # A distinct, sourced caller-side invocation can forward its
            # formal to a callee. A callee declaration alone cannot do so.
            if len(actions) != 1 or (actions[0].get("role") or actions[0]["kind"]) != "call":
                continue
            span = actions[0].get("source")
            target = _body_owner(span, files)
            if not target or target.owner not in owners:
                continue
            for version in sorted(direct):
                bi, oi, owner = acquisitions[version]
                if owner == target.owner:
                    continue
                peers = {v for v, (_, _, s) in acquisitions.items() if s in {owner, target.owner}}
                scope = {i for i, uses in enumerate(used) if uses & peers}
                scope.update(acquisitions[v][0] for v in peers)
                message = (f"Result {version!r} belongs to {owner}, but its direct call at "
                           f"/blocks/{ci}/operations/{cj} cites {target.owner}. Restore the source-backed "
                           "activation and argument version, or show the actual forwarding call at its caller.")
                yield bi, oi, sorted(scope), [declarations[owner], target], [span], message


def qualify_occurrence_keys(candidate, files, inherited_refs, *, bind_defaults=True, snapshots=None):
    """Distinct physical callers cannot alias through an accidentally reused raw key."""
    owners = defaultdict(set)
    sites = []
    for block in candidate["blocks"]:
        if block["data_source_kind"] != "context":
            continue
        ir = block["instructions"][0]
        prior = inherited_refs.get(ir["instruction_ref"])
        if prior:
            for current, old in zip(ir["outputs"], prior["outputs"]):
                if current["identifier"] == old["identifier"] and old.get("semantic_name"):
                    current["semantic_name"] = old["semantic_name"]
        ir["metadata"].pop("optional_context_inputs", None)
        if snapshots and block["block_ref"] in snapshots:
            ir["metadata"]["python_argument_snapshot"] = snapshots[block["block_ref"]]
        ports = callable_signature_ports(ir, files)
        optional = sorted(p["input_index"] for p in ports if p["optional"])
        if optional:
            ir["metadata"]["optional_context_inputs"] = optional
        if bind_defaults and not prior:
            from .python_arguments import argument_defaults
            snapshot = ir["metadata"].get("python_argument_snapshot", {})
            defaults = argument_defaults([p for p in ports if p["output_index"] != snapshot.get("output_index")], files)
            if defaults:
                ir["metadata"]["python_argument_defaults"] = defaults
        for port in ports:
            operand = ir["inputs"][port["input_index"]]
            owners[operand["identifier"]].add(port["owner"])
            sites.append((operand, port))
    taken = set(candidate["declared_context_keys"])
    replacements = {}
    for operand, port in sites:
        key = operand["identifier"]
        if len(owners[key]) > 1:
            pair = key, port["owner"]
            if pair not in replacements:
                stem = "entry." + canonical_sha256(pair)[:16] + "."
                name = stem + key
                while name in taken:
                    name = stem + name
                replacements[pair] = name
                taken.add(name)
            operand.setdefault("semantic_name", key)
            operand["identifier"] = replacements[pair]
    if replacements:
        still_used = {v["identifier"] for b in candidate["blocks"] for ir in b["instructions"]
                      for v in ir["inputs"] if v["type"] == "context_key"}
        replaced = {key for key, _ in replacements}
        candidate["declared_context_keys"] = [
            key for key in candidate["declared_context_keys"] if key not in replaced or key in still_used
        ] + list(replacements.values())
