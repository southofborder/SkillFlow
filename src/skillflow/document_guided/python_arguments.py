"""Immutable scalar defaults that can be established from a Python signature."""
import ast
from functools import lru_cache
from math import isfinite


@lru_cache(maxsize=64)
def _defaults(text):
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return {}
    defaults = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        args = node.args
        positional = [*args.posonlyargs, *args.args]
        pairs = [*zip(reversed(positional), reversed(args.defaults)),
                 *zip(args.kwonlyargs, args.kw_defaults)]
        for arg, expr in pairs:
            if expr is None:
                continue
            try:
                value = ast.literal_eval(expr)
            except (TypeError, ValueError):
                continue
            if (value is None or type(value) in (str, bool, int)
                    or type(value) is float and isfinite(value)):
                defaults[node.lineno, arg.arg] = value
    return defaults


def argument_defaults(ports, files):
    rows = []
    for port in ports:
        span = port["source"]
        if not port["optional"] or not span["file"].endswith(".py"):
            continue
        defaults = _defaults(files[span["file"]])
        key = span["start_line"], port["parameter"]
        if key in defaults:
            rows.append({"input_index": port["input_index"], "output_index": port["output_index"],
                         "value": defaults[key]})
    return rows


SUPPLIED = "argument supplied"
OMITTED = "argument omitted"


def explicit_argument_ports(facts, files, slots):
    """Prove one declared optional input, its immutable snapshot and both source-backed arms."""
    from .entry_occurrences import _same_signature, _tail, callable_signature_ports
    from .source_calls import _edges, source_span
    from skillflow.common.recording import canonical_sha256
    blocks = {b["ref"]: b for b in facts["blocks"]}
    for bi, guarded in enumerate(facts["blocks"]):
        end = guarded["exit"]
        if end.get("metadata", {}).get("predicate") not in {"argument_supplied", "python_argument_supplied"}:
            continue
        span = source_span(end)
        site = _same_signature([span], files) if span else None
        if not span or not span["file"].endswith(".py"):
            continue
        if not site:
            yield bi, "A Python supplied/omitted branch must cite the physical parameter signature."
            continue
        parents = [b for b in blocks.values() if guarded["ref"] in _edges(b)]
        entry = guarded if guarded["source_kind"] == "context" else parents[0] if len(parents) == 1 and not guarded["operations"] else None
        if (not entry or entry["source_kind"] != "context" or len(entry["operations"]) != 1
                or end["kind"] != "branch" or len(end["conditions"]) != 1 or len(end["arms"]) != 2):
            yield bi, "An argument-presence branch needs one immutable snapshot from its signature acquisition."
            continue
        receive = entry["operations"][0]
        outputs = receive["outputs"]
        value = end["conditions"][0].get("result")
        input_names = [_tail(v.get("context_key", "")) for v in receive["inputs"]]
        index = outputs.index(value) if value in outputs else -1
        known = callable_signature_ports(receive, files)
        indexed = {p["input_index"]: p["output_index"] for p in known}
        if (source_span(receive) != span or not (0 <= index < len(site.parameters))
                or len(outputs) != len(site.parameters) or input_names != [p for p, optional in site.parameters]
                or not site.parameters[index][1] or any(indexed.get(i) != i for i in range(len(outputs)) if i != index)
                or index in indexed and indexed[index] != index):
            yield bi, "The supplied-or-omitted operand must be the unique optional parameter snapshot of this invocation."
            continue
        name = input_names[index]
        defaults = _defaults(files[site.file])
        arms = [blocks.get(a["target"]) for a in end["arms"]]
        if (site.first, name) not in defaults or not all(arm and len(arm["operations"]) == 1
                and arm["exit"]["kind"] == "jump" and len(arm["operations"][0]["outputs"]) == 1
                and source_span(arm["operations"][0]) == span
                and (arm["operations"][0].get("role") or arm["operations"][0]["opcode"]) == "value"
                and not arm["operations"][0].get("source_actions") for arm in arms):
            yield bi, "The supplied and omitted arms must bind the original value and its source-literal default."
            continue
        lhs, rhs = (arm["operations"][0] for arm in arms)
        if (any({b["ref"] for b in blocks.values() if arm["ref"] in _edges(b)} != {guarded["ref"]} for arm in arms)
                or lhs["inputs"] != [{"result": value}] or arms[0]["exit"]["target"] != arms[1]["exit"]["target"]
                or canonical_sha256(rhs["inputs"]) != canonical_sha256([{"literal": defaults[site.first, name]}])):
            yield bi, "The supplied arm must forward the snapshot; only the omitted arm may choose the declared default."
            continue
        slots[entry["ref"]] = {"input_index": index, "output_index": index, "parameter": name}
        end["metadata"]["predicate"] = "python_argument_supplied"
        end["arms"][0]["condition"], end["arms"][1]["condition"] = SUPPLIED, OMITTED


def argument_transfers(cfg):
    records = {}
    for key, block in cfg["blocks"].items():
        if not block["instructions"]:
            continue
        end = block["instructions"][-1]
        if end.get("metadata", {}).get("predicate") != "python_argument_supplied":
            continue
        targets = {edge["condition_text"]: edge["target_block_id"] for edge in cfg["edges"]
                   if edge["source_block_id"] == key}
        evidence = [{**end["metadata"]["source_span"], "reason": "Python applies the signature default only on omission."}]
        branch = {"op": "branch", "input": {"kind": "input", "index": 0}, "predicate": "selector",
                  "selector": {"path": [], "tests": [{"kind": "missing"}], "outcome": 1},
                  "true_target": targets[SUPPLIED], "false_target": targets[OMITTED], "evidences": evidence}
        records[end["id"]] = {"segments": [{"mode": "local", "ops": [branch], "returns": []}], "evidences": evidence}
        for target in targets.values():
            ir = cfg["blocks"][target]["instructions"][0]
            records[ir["id"]] = {"output_bindings": [{"output_index": 0, "value": {"kind": "input", "index": 0}}],
                                 "evidences": evidence}
    return records
