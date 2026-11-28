"""Publish the committed initial assembly as a provisional read-only view."""
from collections import Counter, defaultdict
from html import escape
from pathlib import Path
import json

from publish_results import (DETAIL, HERE, NS, OVERVIEW, IRAnchors, control_edges, file_link, graphs,
                             inherited_provenance, inventory, previous, render_graphs)


def source_section(sources):
    parts = ["<section><h2>Frozen source files</h2>"]
    for name, lines in sources.items():
        parts.append("<details><summary>" + escape(name) + "</summary><pre>")
        for number, line in enumerate(lines, 1):
            parts.append('<span id="' + inventory.anchor("line", f"{name}:{number}") + '">'
                + escape(f"{number:3}  {line}") + "</span>\n")
        parts.append("</pre></details>")
    return "".join([*parts, "</section>"])


def publish_initial(run, out):
    run, out = run.resolve(), out.resolve()
    if out.is_relative_to(run):
        raise ValueError("Initial assembly reporting requires an external directory")
    result = inventory.load(run / "result.json")
    if result["stages"].get("assembly", {}).get("status") not in {"complete", "partial"}:
        raise ValueError("Initial assembly has no accepted stage result")
    fixed = inherited_provenance(run)
    owner = run / "annotation"
    manifest = inventory.load(owner / "manifest.json")
    if (manifest["candidate_origin"] != "program_assembled_fragments"
            or graphs.canonical({k: v for k, v in manifest.items() if k != "manifest_sha256"}) != manifest["manifest_sha256"]):
        raise ValueError("Initial assembly manifest does not verify")
    refs = inventory.load(owner / "inputs/references.json", manifest["files"]["inputs/references.json"])
    cfg_path = graphs.reference(run, fixed["cfg"])
    if (owner / refs["cfg"]["path"]).resolve() != cfg_path or refs["cfg"]["sha256"] != fixed["cfg"]["sha256"]:
        raise ValueError("Initial assembly does not bind the revalidated CFG")
    inventory.confirm_input(owner, manifest["task_run_ref"], (run / fixed["task"]["path"]).parent)
    inventory.confirm_input(owner, refs["source_owner"], run / "source")
    for name in ("processing", "task-correspondence", "sensitivity"):
        inventory.confirm_input(owner, refs["fragment_steps"][name], run / "steps" / name)
    audits = {key: inventory.load(owner / key, digest) for key, digest in manifest["artifacts"].items()}
    cfg, task = inventory.load(cfg_path)["cfg"], inventory.load(graphs.reference(run, fixed["task"]))
    wire, raw, compiled, mapping = (audits["audit/" + name + ".json"] for name in (
        "wire-annotation", "raw-annotation", "compiled-response", "compilation-map"))
    files = {**{k: fixed[k] for k in ("cfg", "task", "flow", "graph_answer")}, "assembly_manifest": {
        "path": "annotation/manifest.json", "sha256": graphs.digest(owner / "manifest.json")},
        **{k: {"path": "annotation/" + k, "sha256": d} for k, d in manifest["artifacts"].items()}}
    bundle = {"run": run.name, "view_kind": "initial_automatic_assembly", "selection": None, "selection_committed": False,
              "cfg": cfg, "task": task, "annotation": wire, "status": {"status": "provisional initial assembly"},
              "files": files}
    instructions = {ir["id"]: ir for b in cfg["blocks"].values() for ir in b["instructions"]}
    keys = set(instructions)
    demands, realizations = defaultdict(list), defaultdict(list)
    for table, grouped in ((wire["demands"], demands), (wire["realizations"], realizations)):
        for entry in table:
            for ir in inventory.ids_in(entry, keys):
                grouped[ir].append(entry)
    title = "Provisional initial assembly"
    note = ("Automatically assembled processing, Task correspondence and sensitivity. "
            "The final selection, propagation and DOE are outside this snapshot.")
    def label(canvas, filename):
        for element in canvas.root.iter():
            text = element.text or ""
            if text.startswith("SkillFlow | DIAGNOSTIC") or text in {
                "Diagnostic original CFG and accepted fragments - assembly did not commit", "Diagnostic uncommitted CFG overview"}:
                element.text = title + (" · CFG overview" if filename == OVERVIEW else " · full annotated CFG")
            elif text.startswith(("Terminal diagnostic display", "Complete original CFG overview",
                                  "Accepted original CFG", "Original accepted fragments only;")):
                element.text = note
            elif text == "ACCEPTED PROCESSING FRAGMENT":
                element.text = "ASSEMBLED WIRE SEMANTICS"
            elif text == "Accepted processing globals - NOT assembled annotation":
                element.text = "Initial assembled annotation globals"
            elif text == "Selection and provenance":
                element.text = "Initial assembly provenance"
            elif text.startswith("GAP: no executable annotation selected"):
                element.text = "GAP · initial assembled annotation missing"
        if filename == OVERVIEW:
            for a in canvas.root.iter(NS + "a"):
                ir = a.get("href", "").partition("#view-")[2]
                if ir in instructions:
                    ids = sorted({d["requirement_id"] for d in demands[ir] + realizations[ir]})
                    for t in a.iter(NS + "text"):
                        if t.text and "Task: unassembled" in t.text:
                            t.text = t.text.replace("Task: unassembled", "Task: " + (", ".join(ids) or "no direct binding"))
    out.mkdir(parents=True, exist_ok=True)
    edges = control_edges(cfg, None)
    coverage = render_graphs(bundle, out, edges, label, provenance_label="Initial CFG SHA-256 " + fixed["cfg"]["sha256"],
                             link_inventory=True)
    rows = []
    sources = inventory.read_sources(run)
    missing = set()
    for key, ir in instructions.items():
        spec = wire["ir_semantics"].get(key)
        rows.append('<section id="' + inventory.anchor("ir", key) + '"><h2>' + escape(key + " · " + ir["opcode"])
            + '</h2><p>' + ("Assembled processing present." if spec else "Missing executable processing annotation.")
            + "</p>" + previous.link(DETAIL + "#view-" + key, "View on CFG")
            + inventory.panel("Exact instruction", ir) + inventory.panel("Assembled wire semantics", spec)
            + inventory.panel("Normalized annotation", raw["ir_semantics"].get(key))
            + inventory.panel("Compiled annotation", compiled["ir_semantics"].get(key))
            + inventory.panel("Source action bindings", mapping.get("source_action_bindings", {}).get(key))
            + inventory.panel("Task demands and realizations", demands[key] + realizations[key])
            + inventory.panel("Processing gaps", [g for g in wire["processing_gaps"] if g["instruction_id"] == key])
            + inventory.excerpt_rows([ir, spec, demands[key], realizations[key]], sources, missing) + "</section>")
    nav = [previous.link("index.html", "Summary"), previous.link(OVERVIEW, "CFG overview"),
           previous.link(DETAIL, "Full annotated CFG"), previous.link("annotations.html", "Per-instruction annotations"),
           previous.link("annotations.json", "Full assembled annotations and Task JSON"),
           previous.link("coverage.json", "Coverage and digests"), file_link(out, owner / "manifest.json", "Assembly manifest")]
    header = ("<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
              "<title>" + title + "</title><style>" + previous.STYLE + "</style></head><body><h1>" + title
              + "</h1><p>" + note + "</p><nav>" + "".join(nav) + "</nav>")
    page = header + "".join(rows) + source_section(sources) + "</body></html>"
    anchors = IRAnchors()
    anchors.feed(page)
    anchors.close()
    if anchors.ids != Counter(inventory.anchor("ir", k) for k in keys):
        raise ValueError("Initial assembly inventory omits instructions")
    (out / "annotations.html").write_text(page, encoding="utf-8")
    absent = coverage["unmodeled_ir_ids"]
    summary = (f"{len(cfg['blocks'])} blocks, {len(keys)} instructions, {len(edges)} control edges. "
               f"{coverage['modeled_ir_count']} instructions have assembled wire semantics. Missing processing at "
               + (", ".join(absent) or "none") + ".")
    previous.write_json(out / "annotations.json", {"view": title, "selection": None, "task": task, "wire_annotation": wire,
        "compiled_annotation": compiled, "files": files, "origin": fixed})
    previous.write_json(out / "coverage.json", {"scope": title, "selection": None, "graph": coverage,
        "annotation_html_anchors": len(anchors.ids), "processing_gaps": wire["processing_gaps"],
        "source_references_without_excerpt": sorted(missing)})
    previous.write_json(out / "control-routes.json", {"scope": title, "edges": edges})
    (out / "index.html").write_text(header + "<p>" + escape(summary) + "</p><h2>Task</h2><p>" + escape(task["purpose"]["text"])
        + "</p><p>Initial CFG SHA-256 <code>" + fixed["cfg"]["sha256"] + "</code></p><p>Initial assembly manifest file SHA-256 "
        + "<code>" + files["assembly_manifest"]["sha256"] + "</code></p></body></html>", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(publish_initial(Path(inventory.load(HERE / "downstream-dispatch.json")["run"]), HERE / "initial-assembled"))
