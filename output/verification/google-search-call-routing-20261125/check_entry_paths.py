"""Inspect the two real source entries in a saved google-search CFG; zero model calls."""
import argparse
import json
from collections import defaultdict, deque
from pathlib import Path


def read(path):
    return json.loads(path.read_bytes())


def find_path(edges, starts, ends, omit=()):
    queue = deque((block, [block]) for block in sorted(starts))
    seen = set(omit)
    while queue:
        block, path = queue.popleft()
        if block in seen:
            continue
        if block in ends:
            return path
        seen.add(block)
        queue.extend((dest, [*path, dest]) for dest in edges[block] if dest not in seen)
    return []


def source_lines(ir):
    meta = ir.get("metadata", {})
    spans = [a.get("source") for a in meta.get("source_actions", [])] or [meta.get("source_span")]
    return {(s["start_line"], s["end_line"]) for s in spans if s and s["file"].endswith("/scripts/search.py")}


def describe(cfg):
    blocks = cfg["blocks"]
    edges = defaultdict(list)
    for edge in cfg["edges"]:
        edges[edge["source_block_id"]].append(edge["target_block_id"])
    entries = {"CLI": set(), "public": set()}
    stages = {name: set() for name in ("request", "status", "decode", "success_output", "error_output")}
    terminals = {}
    for block, contents in blocks.items():
        for ir in contents["instructions"]:
            lines = source_lines(ir)
            if ir["opcode"] == "return":
                terminals[block] = {"ir": ir["id"], "lines": sorted(lines),
                                    "inputs": ir["inputs"]}
            if ir["opcode"] in {"dispatch", "return"}:
                continue
            if any(v["type"] == "context_key" for v in ir["inputs"]):
                if (6, 6) in lines and (len(ir["outputs"]) >= 2 or any(
                    param in str(v.get("identifier", "")).lower()
                    for v in ir["inputs"] for param in ("query", "api_key", "cse_id", "num_results"))):
                    entries["public"].add(block)
            actions = ir.get("metadata", {}).get("source_actions", [])
            reads_cli_input = any((a.get("role") or a.get("kind")) in {"read", "receive"} for a in actions)
            if (reads_cli_input or ir["opcode"] in {"read", "receive"}) and any(
                    19 <= start <= end <= 28 for start, end in lines):
                entries["CLI"].add(block)
            for line, stage in ((14, "request"), (15, "status"), (16, "decode"),
                                (36, "success_output"), (38, "error_output")):
                if (line, line) in lines:
                    stages[stage].add(block)
    # For stdout, prefer the concrete delivery over expressions at the same source line.
    for line, stage in ((36, "success_output"), (38, "error_output")):
        deliveries = {block for block in stages[stage] for ir in blocks[block]["instructions"]
                      for act in ir.get("metadata", {}).get("source_actions", [])
                      if act.get("source", {}).get("start_line") == line
                      and (act.get("role") or act.get("kind")) == "deliver"}
        if deliveries:
            stages[stage] = deliveries
    reachable = {name: {stage: {block for block in sites if find_path(edges, starts, {block})}
                        for stage, sites in stages.items()} for name, starts in entries.items()}
    cli = reachable["CLI"]
    public = reachable["public"]
    # Public return and exception terminals are observable through the existing CFG edges.
    # The individual return/throw value identities are supplied in the terminal records.
    public_terms = {block for block in terminals if find_path(edges, entries["public"], {block})}
    paths = {
        "cli_decode_to_success_output": find_path(edges, cli["decode"], cli["success_output"]),
        "cli_request_exception_to_error_output_before_status": find_path(
            edges, cli["request"], cli["error_output"], cli["status"] | cli["decode"]),
        "public_decode_to_function_exit": find_path(edges, public["decode"], public_terms),
        "public_request_exception_to_function_exit_before_status": find_path(
            edges, public["request"], public_terms, public["status"] | public["decode"]),
    }
    checks = {
        "both_argument_contexts_present": all(entries.values()),
        "both_request_occurrences_present": bool(cli["request"] and public["request"]),
        "request_blocks_separated": bool(cli["request"] and public["request"])
                                    and cli["request"].isdisjoint(public["request"]),
        "public_cannot_reach_cli_output": bool(entries["public"] and stages["error_output"] and stages["success_output"])
                                         and not (public["error_output"] or public["success_output"]),
        "cli_cannot_exit_via_public_function_terminals": bool(entries["CLI"] and public_terms)
            and not find_path(edges, entries["CLI"], public_terms),
        **{key: bool(value) for key, value in paths.items()},
    }
    return {"scope": "Source-located graph reachability. Paths are possible static routes; "
                     "sensitive contents and DOE are read from downstream records separately.",
            "entries": {k: sorted(v) for k, v in entries.items()},
            "reachable_sites": {n: {k: sorted(v) for k, v in sites.items()} for n, sites in reachable.items()},
            "paths": paths, "public_terminals": {b: terminals[b] for b in sorted(public_terms)},
            "checks": checks, "all_checks_match": all(checks.values())}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cfg", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    obj = read(args.cfg)
    report = describe(obj.get("cfg", obj))
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["checks"]))
