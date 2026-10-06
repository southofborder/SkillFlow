"""Offline fixtures, recorded CFGs, seeded graphs and metamorphic test cases."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
import hashlib
import itertools
import json
from pathlib import Path
import random
from typing import Any, Iterable

from skillflow.common.paths import project_root, resolve_material_path
REPOSITORY_ROOT = project_root()


@dataclass
class Case:
    name: str
    family: str
    cfg: dict[str, Any]
    expected: bool | None = None
    expected_domain: str = "core"
    provenance: dict[str, Any] = field(default_factory=dict)


def result(name: str) -> dict[str, Any]:
    return {"type": "result", "identifier": name}


def literal(value: Any = True) -> dict[str, Any]:
    return {"type": "literal", "literal_value": value}


def ins(name: str, opcode: str = "operation", inputs: list | None = None,
        outputs: list | None = None) -> dict[str, Any]:
    return {"id": f"ir_{name}", "opcode": opcode, "inputs": inputs or [], "outputs": outputs or []}


def block(name: str, instructions: list, source: str | None = None) -> dict[str, Any]:
    return {"block_id": name, "block_name": name, "instructions": instructions, "data_source_kind": source}


def edge(source: str, target: str, condition: str | None = None) -> dict[str, Any]:
    return {"source_block_id": source, "target_block_id": target, "condition_text": condition}


def graph(blocks: list[dict], edges: list[dict] | None = None, contexts: list[str] | None = None) -> dict[str, Any]:
    return {"entry_block_id": blocks[0]["block_id"], "blocks": {b["block_id"]: b for b in blocks},
            "edges": edges or [], "declared_context_keys": contexts or []}


def fixtures() -> list[Case]:
    values: list[Case] = []

    def add(name: str, cfg: dict, expected: bool = True, domain: str = "core") -> dict:
        values.append(Case(name, "rule-fixture", deepcopy(cfg), expected, domain))
        return cfg

    def changed(name: str, cfg: dict, mutate: Any, expected: bool = False,
                domain: str = "core") -> dict:
        copied = deepcopy(cfg)
        mutate(copied)
        return add(name, copied, expected, domain)

    simple = add("single-return", graph([block("A", [ins("ret", "return")])]))
    empty = deepcopy(simple)
    empty["blocks"] = {}
    add("empty-graph", empty, False)
    changed("entry-missing", simple, lambda g: g.update(entry_block_id="absent"))
    changed("block-key-mismatch", simple, lambda g: g["blocks"]["A"].update(block_id="different"))
    changed("empty-block", simple, lambda g: g["blocks"]["A"].update(instructions=[]))
    changed("terminator-missing", simple, lambda g: g["blocks"]["A"]["instructions"][0].update(opcode="compute"))
    changed("dispatch-no-target", simple, lambda g: g["blocks"]["A"]["instructions"][0].update(opcode="dispatch"))
    changed("return-outgoing", simple, lambda g: g["edges"].append(edge("A", "A")))
    changed("undefined-result", simple, lambda g: g["blocks"]["A"]["instructions"][0].update(inputs=[result("missing")]))
    changed("terminator-output", simple, lambda g: g["blocks"]["A"]["instructions"][0].update(outputs=[result("r")]))
    local = add("local-result-order", graph([block("A", [ins("make", outputs=[result("r")]), ins("use", inputs=[result("r")]), ins("ret", "return")])]))
    changed("local-read-before", local, lambda g: g["blocks"]["A"]["instructions"].__setitem__(slice(0, 2), list(reversed(g["blocks"]["A"]["instructions"][:2]))))
    changed("local-same-instruction-read", local, lambda g: g["blocks"]["A"]["instructions"][0].update(inputs=[result("r")]))
    changed("instruction-id-local-duplicate", local, lambda g: g["blocks"]["A"]["instructions"][1].update(id="ir_make"))
    changed("result-local-duplicate", local, lambda g: g["blocks"]["A"]["instructions"][1].update(outputs=[result("r")]))
    changed("result-output-duplicate", local, lambda g: g["blocks"]["A"]["instructions"][0]["outputs"].append(result("r")))
    changed("output-not-result", local, lambda g: g["blocks"]["A"]["instructions"][0].update(outputs=[literal()]))
    changed("early-terminator", local, lambda g: g["blocks"]["A"]["instructions"][1].update(opcode="return"))
    pair = add("cross-block-result", graph([block("A", [ins("make", outputs=[result("r")]), ins("dispatch", "dispatch")]), block("B", [ins("ret", "return", [result("r")])])], [edge("A", "B")]))
    changed("edge-duplicate", pair, lambda g: g["edges"].append(deepcopy(g["edges"][0])))
    changed("edge-target-undefined", pair, lambda g: g["edges"][0].update(target_block_id="undefined"))
    changed("edge-source-undefined", pair, lambda g: g["edges"][0].update(source_block_id="undefined"))
    changed("guard-needs-input", pair, lambda g: g["edges"][0].update(condition_text="yes"))
    changed("instruction-id-global-duplicate", pair, lambda g: g["blocks"]["B"]["instructions"][0].update(id="ir_make"))
    guarded = changed("guard-with-input", pair, lambda g: (g["edges"][0].update(condition_text="yes"), g["blocks"]["A"]["instructions"][-1].update(inputs=[literal()])), True)
    changed("parallel-distinct-guards", guarded, lambda g: g["edges"].append(edge("A", "B", "no")), True)
    changed("guard-whitespace-null", pair, lambda g: g["edges"][0].update(condition_text=" \t\n"), True)
    changed("guard-whitespace-duplicate", guarded, lambda g: g["edges"].append(edge("A", "B", " yes ")))
    roots = add("independent-roots", graph([block("A", [ins("ret_a", "return")]), block("B", [ins("ret_b", "return")])]))
    disconnected = deepcopy(roots)
    disconnected["blocks"]["A"]["instructions"].insert(0, ins("produce", outputs=[result("r")]))
    disconnected["blocks"]["B"]["instructions"][0]["inputs"] = [result("r")]
    add("disconnected-result-path", disconnected, False)
    cycle = graph([block("A", [ins("ret", "return")]), block("B", [ins("loop", "dispatch")])], [edge("B", "B")])
    add("unreachable-cycle", cycle, False)
    cycle["entry_block_id"] = "B"
    add("entry-cycle-and-root", cycle)
    merge = graph([block("A", [ins("choose", "dispatch", [literal()])]), block("B", [ins("make", outputs=[result("r")]), ins("go_b", "dispatch")]), block("C", [ins("go_c", "dispatch")]), block("D", [ins("ret", "return", [result("r")])])], [edge("A", "B", "yes"), edge("A", "C", "no"), edge("B", "D"), edge("C", "D")])
    add("may-reach-is-not-dominance", merge)
    changed("sibling-read-no-path", merge, lambda g: g["blocks"]["C"]["instructions"][0].update(inputs=[result("r")]))
    changed("branch-no-dependencies", merge, lambda g: g["blocks"]["A"]["instructions"][0].update(inputs=[]))
    changed("global-result-duplicate", merge, lambda g: g["blocks"]["C"]["instructions"].insert(0, ins("make_c", outputs=[result("r")])))
    context = add("context-source", graph([block("A", [ins("read", inputs=[{"type": "context_key", "identifier": "request"}], outputs=[result("r")]), ins("ret", "return", [result("r")])], "context")], contexts=["request"]))
    changed("context-not-declared", context, lambda g: g.update(declared_context_keys=[]))
    changed("source-shape", context, lambda g: g["blocks"]["A"]["instructions"].insert(1, ins("extra")))
    changed("source-no-output", context, lambda g: g["blocks"]["A"]["instructions"][0].update(outputs=[]))
    changed("context-empty-input", context, lambda g: g["blocks"]["A"]["instructions"][0].update(inputs=[]))
    changed("context-mixed-input", context, lambda g: g["blocks"]["A"]["instructions"][0]["inputs"].append(literal()))
    changed("context-outside-source", context, lambda g: g["blocks"]["A"].update(data_source_kind=None))
    changed("context-outside-acquisition", context, lambda g: g["blocks"]["A"]["instructions"][1]["inputs"].append({"type": "context_key", "identifier": "request"}))
    external = add("external-source", graph([block("A", [ins("read", inputs=[{"type": "external_resource", "identifier": "resource"}], outputs=[result("r")]), ins("ret", "return")], "external")]))
    add("external-source-from-prior-result", graph([block("A", [ins("make", outputs=[result("address")]), ins("go", "dispatch")]), block("B", [ins("fetch", inputs=[result("address")], outputs=[result("response")]), ins("ret", "return", [result("response")])], "external")], [edge("A", "B")]))
    add("loop-path-is-not-first-iteration-availability", graph([block("A", [ins("read", inputs=[result("later")]), ins("go_a", "dispatch")]), block("B", [ins("later", outputs=[result("later")]), ins("go_b", "dispatch")])], [edge("A", "B"), edge("B", "A")]))
    changed("repeated-context-read", context, lambda g: g["blocks"]["A"]["instructions"][0]["inputs"].append({"type": "context_key", "identifier": "request"}), True)
    changed("external-source-no-resource", external, lambda g: g["blocks"]["A"]["instructions"][0].update(inputs=[literal()]))
    changed("external-source-reserved-opcode", external, lambda g: g["blocks"]["A"]["instructions"][0].update(opcode="return"))
    changed("explicit-nonliteral-null", local, lambda g: g["blocks"]["A"]["instructions"][0]["outputs"][0].update(literal_value=None), domain="schema")
    changed("unknown-field", simple, lambda g: g.update(unknown=True), domain="schema")
    changed("invalid-instruction-id", simple, lambda g: g["blocks"]["A"]["instructions"][0].update(id="not-prefixed"), domain="schema")
    changed("invalid-source-kind", simple, lambda g: g["blocks"]["A"].update(data_source_kind="network"), domain="schema")
    changed("missing-result-identifier", local, lambda g: g["blocks"]["A"]["instructions"][0]["outputs"][0].pop("identifier"), domain="schema")
    changed("literal-semantic-name", simple, lambda g: g["blocks"]["A"]["instructions"][0].update(inputs=[{"type": "literal", "semantic_name": "forbidden"}]), domain="schema")
    changed("duplicate-context-declaration", context, lambda g: g["declared_context_keys"].append(" request "), domain="schema")
    return values


def recorded_cases(manifest: Path) -> list[Case]:
    """The renderer manifest selects records; only hashed analysis CFGs are inputs.

    The manifest's cfg is a display model_dump containing null placeholders and
    MUST NOT replace the saved analysis cfg or be silently cleaned and accepted.
    """
    manifest = manifest.resolve()
    source = json.loads(manifest.read_text(encoding="utf-8"))
    path_base = source.get("path_base")
    if path_base not in (None, "repository"):
        raise ValueError(f"unknown manifest path_base: {path_base!r}")
    samples = source["samples"]
    if len(samples) != 30 or [s["index"] for s in samples] != list(range(1, 31)):
        raise ValueError("review manifest must contain exactly ordered samples 001..030")
    cases = []
    for sample in samples:
        expected_rep = 3 if sample["index"] == 15 else 1
        if sample["repetition"] != expected_rep or (sample["index"] == 15 and sample["sample_id"] != "F03"):
            raise ValueError("review selection requires 015 F03 repetition 3 and all others repetition 1")
        path = Path(sample["analysis_path"])
        if path_base == "repository":
            if path.is_absolute():
                raise ValueError("repository manifest analysis_path must be relative")
            candidate = (REPOSITORY_ROOT / path).resolve()
            if not candidate.is_relative_to(REPOSITORY_ROOT.resolve()):
                raise ValueError("repository manifest analysis_path must stay inside repository")
            path = candidate if candidate.exists() else resolve_material_path(path, base=REPOSITORY_ROOT)
        raw = path.read_bytes()
        actual_hash = hashlib.sha256(raw).hexdigest()
        if actual_hash != sample["analysis_sha256"]:
            raise ValueError(f"analysis hash mismatch: {path}")
        analysis = json.loads(raw)
        cfg = analysis["cfg"]
        cases.append(Case(f"review-{sample['index']:03d}-{sample['sample_id']}", "review-original", cfg, True,
                          provenance={"manifest_path": str(manifest), "manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
                                      "manifest_path_base": path_base, "manifest_analysis_path": sample["analysis_path"],
                                      "analysis_path": str(path), "analysis_sha256": actual_hash,
                                      "sample_id": sample["sample_id"], "index": sample["index"], "repetition": sample["repetition"]}))
    return cases


def topology_cases(max_blocks: int = 3) -> Iterable[Case]:
    """Exhaust all directed edge subsets, including self-loops, up to the bound.

    Each topology appears plain and with result r defined in block 0 and read
    in the last block. This probes reachability and root treatment, not merely
    arbitrarily invalid terminators: terminators agree with outgoing edges.
    """
    for n in range(1, max_blocks + 1):
        slots = list(itertools.product(range(n), repeat=2))
        for mask in range(1 << len(slots)):
            edges = [edge(f"b{i}", f"b{j}") for k, (i, j) in enumerate(slots) if mask & (1 << k)]
            for read in (False, True):
                blocks = []
                for i in range(n):
                    outgoing = [e for e in edges if e["source_block_id"] == f"b{i}"]
                    items = []
                    if read and i == 0:
                        items.append(ins("make", outputs=[result("r")]))
                    inputs = [result("r")] if read and i == n - 1 else ([literal()] if len(outgoing) > 1 else [])
                    items.append(ins(f"end_{i}", "dispatch" if outgoing else "return", inputs))
                    blocks.append(block(f"b{i}", items))
                yield Case(f"topology-{n}-{mask}-{int(read)}", "topology-enumeration", graph(blocks, edges))


def random_cases(seed: int = 20260913, count: int = 160) -> Iterable[Case]:
    rng = random.Random(seed)
    for index in range(count):
        n = rng.randint(1, 8)
        edges = [edge(f"b{i}", f"b{j}", rng.choice([None, "yes", "no"])) for i in range(n) for j in range(n) if rng.random() < .22]
        blocks = []
        for i in range(n):
            outgoing = [e for e in edges if e["source_block_id"] == f"b{i}"]
            inputs = [result(f"r{rng.randrange(n + 1)}")] if rng.random() < .35 else []
            items = [ins(f"make_{i}", inputs=inputs, outputs=[result(f"r{i}")]), ins(f"end_{i}", "dispatch" if outgoing else "return", [literal()] if len(outgoing) > 1 or any(e["condition_text"] for e in outgoing) else [])]
            blocks.append(block(f"b{i}", items))
        yield Case(f"seed-{seed}-{index:04d}", "seeded-generation", graph(blocks, edges), provenance={"seed": seed, "index": index})


def renamed(cfg: dict) -> dict:
    copied = deepcopy(cfg)
    names: dict[str, dict[str, str]] = {k: {} for k in ("block", "instruction", "result", "context")}

    def rename(kind: str, value: str) -> str:
        value = value.strip() if kind != "block-key" else value
        mapping = names[kind]
        if value not in mapping:
            mapping[value] = f"{'ir' if kind == 'instruction' else kind}_renamed_{len(mapping)}"
        return mapping[value]

    copied["entry_block_id"] = rename("block", copied["entry_block_id"])
    rebuilt = {}
    for key, b in copied["blocks"].items():
        new_key = rename("block", key)
        b["block_id"] = rename("block", b["block_id"])
        for instruction in b["instructions"]:
            instruction["id"] = rename("instruction", instruction["id"])
            for operand in instruction.get("inputs", []) + instruction.get("outputs", []):
                if operand["type"] in ("result", "context_key"):
                    kind = "result" if operand["type"] == "result" else "context"
                    operand["identifier"] = rename(kind, operand["identifier"])
        rebuilt[new_key] = b
    copied["blocks"] = rebuilt
    for e in copied.get("edges", []):
        for key in ("source_block_id", "target_block_id"):
            e[key] = rename("block", e[key])
    copied["declared_context_keys"] = [rename("context", k) for k in copied.get("declared_context_keys", [])]
    return copied


def metamorphic_cases(base: list[Case]) -> Iterable[Case]:
    for case in base:
        if case.expected_domain != "core":
            continue
        yield Case(case.name + "-rename", "legal-renaming", renamed(case.cfg), case.expected, provenance={"parent": case.name})
        reverse = deepcopy(case.cfg)
        reverse["blocks"] = dict(reversed(list(reverse["blocks"].items())))
        reverse["edges"] = list(reversed(reverse.get("edges", [])))
        yield Case(case.name + "-storage-reverse", "storage-order", reverse, case.expected, provenance={"parent": case.name})


def mutation_cases(base: list[Case]) -> Iterable[Case]:
    for case in base:
        if case.expected is not True:
            continue
        operations: list[tuple[str, Any]] = [
            ("entry", lambda g: g.update(entry_block_id="__missing_entry__")),
            ("undefined-read", lambda g: next(iter(g["blocks"].values()))["instructions"][-1].setdefault("inputs", []).append(result("__missing_result__"))),
            ("remove-instruction", lambda g: next(iter(g["blocks"].values()))["instructions"].pop()),
        ]
        if case.cfg.get("edges"):
            operations.extend([
                ("duplicate-edge", lambda g: g["edges"].append(deepcopy(g["edges"][0]))),
                ("remove-edge", lambda g: g["edges"].pop(0)),
                ("dangling-target", lambda g: g["edges"][0].update(target_block_id="__missing_target__")),
                ("change-condition", lambda g: g["edges"][0].update(condition_text="mutated condition")),
            ])
        for label, operation in operations:
            copied = deepcopy(case.cfg)
            operation(copied)
            yield Case(case.name + "-mutation-" + label, "single-mutation", copied, provenance={"parent": case.name, "mutation": label})
