"""Render the evidence-bound offline readmission alongside its actual online comparator."""
from collections import Counter
from html import escape
from pathlib import Path

from publish_results import (DETAIL, HERE, NS, OVERVIEW, IRAnchors, control_edges, file_link, graphs,
                             inventory, previous, render_graphs)
from publish_initial import source_section


def publish(run, out):
    run, out = run.resolve(), out.resolve()
    receipt = inventory.load(out / "receipt.json")
    selection = inventory.load(run / "selection.json")
    if receipt["run"] != run.name or selection != receipt["selection"]:
        raise ValueError("Offline revalidation refers to a different official selection")
    for name, digest in receipt["inputs"].items():
        graphs.reference(run, {"path": name, "sha256": digest})
    for name, digest in receipt["artifact_sha256"].items():
        graphs.reference(out, {"path": name, "sha256": digest})
    def read(name):
        return inventory.load(out / name, receipt["artifact_sha256"][name])
    task = inventory.load(graphs.reference(run, selection["task"]))
    cfg = inventory.load(graphs.reference(run, selection["cfg"]))["cfg"]
    basis = receipt["basis_annotation"]
    owner = graphs.reference(run, basis).parent
    initial_control = receipt["basis"] == "initial_control"
    if initial_control:
        if owner != run / "annotation" or out != HERE / "revalidated-results/initial-control":
            raise ValueError("The original assembly control belongs in the separate initial-control view")
    elif receipt["basis"] != "terminal_selection" or basis != selection["annotation"]:
        raise ValueError("The terminal selection does not bind this readmission's basis")
    manifest = inventory.load(owner / "manifest.json")
    initial = inventory.load(owner / "audit/wire-annotation.json", manifest["artifacts"]["audit/wire-annotation.json"])
    wire, raw, compiled, mapping = (read("derived-" + name + ".json") for name in ("wire", "raw", "compiled", "mapping"))
    forward, records = read("forward.json"), read("forward-records.json")
    backward, doe = read("backward.json"), read("doe.json")
    admission = receipt["readmission"]
    recovered = admission["instruction_id"]
    if task["task_sha256"] != receipt["task_sha256"] or task["source_sha256"] != receipt["source_sha256"]:
        raise ValueError("Derived Task or source differs from the selected originals")
    original_specs, derived_specs = initial["ir_semantics"], wire["ir_semantics"]
    if original_specs.keys() | {recovered} != derived_specs.keys() or recovered in original_specs:
        raise ValueError("Derived annotation does not add exactly the readmitted instruction")
    if any(spec != derived_specs[ir] for ir, spec in original_specs.items()):
        raise ValueError("Derived processing changed a modeled instruction in its bound assembly")
    supplied = inventory.load(run / admission["source_candidate"], receipt["inputs"][admission["source_candidate"]])
    archived = inventory.resolve_pointer(supplied, admission["pointer"])
    if graphs.canonical(archived) != admission["row_sha256"]:
        raise ValueError("Archived model row differs from the readmission receipt")
    instructions = {ir["id"]: ir for block in cfg["blocks"].values() for ir in block["instructions"]}
    keys = set(instructions)
    cover = forward["coverage"]
    if keys != cover.keys() or records.keys() - keys:
        raise ValueError("Derived forward coverage or record refers to the wrong graph")
    title = ("Earlier automatic assembly · offline control" if initial_control
             else "Offline revalidation with one readmitted model row")
    note = (f"{recovered} uses the archived processing response identified by the receipt. "
            "The graph and Task come from the official online selection. The figures show the separately recomputed "
            "results. This derived annotation has no new source review.")
    if initial_control:
        note += " This control uses the earlier automatic assembly before revision."
    bundle = {"view_kind": "derived_offline_readmission", "selection": None, "selection_committed": False,
              "online_selection": selection, "basis_annotation": basis, "readmission": admission, "run": run.name, "cfg": cfg, "task": task,
              "annotation": wire, "status": {"status": "separate offline revalidation", "forward": forward["status"],
              "backward": backward["status"], "doe": doe["status"]}, "files": {"receipt": {"path": "receipt.json",
              "sha256": graphs.digest(out / "receipt.json")}, **receipt["artifact_sha256"]}}
    goals = backward.get("goals", [])
    def label(canvas, filename):
        for item in canvas.root.iter():
            txt = item.text or ""
            if txt.startswith("SkillFlow | DIAGNOSTIC") or txt in {
                "Diagnostic original CFG and accepted fragments - assembly did not commit", "Diagnostic uncommitted CFG overview"}:
                item.text = title + (" · overview" if filename == OVERVIEW else " · full annotated CFG")
            elif txt.startswith(("Terminal diagnostic display", "Complete original CFG overview",
                                  "Accepted original CFG", "Original accepted fragments only;")):
                item.text = note
            elif txt == "ACCEPTED PROCESSING FRAGMENT":
                item.text = "OFFLINE REVALIDATED WIRE SEMANTICS"
            elif txt == "Accepted processing globals - NOT assembled annotation":
                item.text = "Revalidated annotation globals"
            elif txt == "Selection and provenance":
                item.text = "Offline readmission provenance"
            elif txt == "GAP: no executable annotation selected":
                item.text = "GAP · no executable annotation in this revalidation"
        for a in canvas.root.iter(NS + "a"):
            ir = a.get("href", "").partition("#view-" if filename == OVERVIEW else "#ir-")[2]
            if ir not in keys:
                continue
            heading = a.find(NS + "text")
            heading.text += " · " + cover[ir] + (" · readmitted" if ir == recovered else "")
            for line in a.iter(NS + "text"):
                if line.text and "Task: unassembled" in line.text:
                    ids = {g["requirement_id"] for g in goals if g["target"].get("instruction_id") == ir}
                    line.text = line.text.replace("Task: unassembled", "Task: " + (", ".join(sorted(ids)) or "no direct goal"))
    edges = control_edges(cfg, records)
    coverage = render_graphs(bundle, out, edges, label, link_inventory=True,
        provenance_label="Official selected CFG SHA-256 " + selection["cfg"]["sha256"] + " · separate offline readmission")
    sinks = read("forward-sinks.json")
    joins, global_rows, counts = {}, {}, {}
    for name, rows in {
        "Compiled event mapping": mapping.get("events", []), "Realizations": compiled["realizations"],
        "Demand goals": compiled["demands"], "Input contracts": compiled.get("input_contracts", []),
        "Reported processing gaps": compiled.get("processing_gaps", []),
        "Declared boundaries": compiled.get("sink_boundaries", []), "Recorded boundaries": sinks,
        "Forward diagnostics": forward["diagnostics"], "Backward goals": goals,
        "Backward input assessments": backward["input_assessments"], "Backward input findings": backward["input_findings"],
        "Backward demands": [{"id": k, **v} for k, v in backward["derivations"].items()],
        "Backward sink demands": backward["sinks"], "DOE sink comparisons": doe["sinks"],
        "DOE diagnostics": doe.get("diagnostics", [])}.items():
        joins[name], global_rows[name] = inventory.group_rows(rows, keys, counts, name)
    nav = [previous.link("index.html", "Offline readmission summary"), previous.link(OVERVIEW, "CFG overview"),
           previous.link(DETAIL, "Full annotated CFG"), previous.link("annotations.html", "Per-instruction evidence"),
           previous.link("derived-wire.json", "Complete revalidated wire"), previous.link("forward-data.json", "Forward data versions"),
           previous.link("backward.json", "Backward demands"), previous.link("revalidated-control-routes.json", "Observed control routes"),
           previous.link("doe.json", "Recomputed DOE"), previous.link("boundary-comparisons.json", "Boundary comparisons"),
           previous.link("receipt.json", "Readmission receipt"), previous.link("source-review-provenance.json", "Review provenance"),
           previous.link("render-verification.json", "Render verification"),
           file_link(out, HERE / "supplement-results/index.html", "Official online result")]
    if initial_control:
        nav.append(file_link(out, HERE / "revalidated-results/index.html", "Offline readmission of the final selection"))
    elif (out / "initial-control/receipt.json").exists():
        nav.append(previous.link("initial-control/index.html", "Earlier automatic assembly control"))
    if not initial_control and (out / "meeting-example.svg").is_file():
        nav.insert(0, previous.link("meeting-example.svg", "Meeting figure · API key paths"))
    header = ("<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
              "<title>" + title + "</title><style>" + previous.STYLE + "</style></head><body><h1>" + title
              + "</h1><p>" + escape(note) + "</p><nav>" + "".join(nav) + "</nav>")
    sources, missing = inventory.read_sources(run), set()
    sections = [header, "<h2>Task</h2><p>" + escape(task["purpose"]["text"]) + "</p>", inventory.panel("Complete Task", task)]
    for key, ir in instructions.items():
        sections.append('<section id="' + inventory.anchor("ir", key) + '"><h2>' + escape(key + " · " + ir["opcode"])
            + "</h2><p>Forward " + escape(cover[key]) + " · " + ("Forward record present" if key in records else "Forward record missing")
            + " · " + ("Wire semantics present" if key in derived_specs else "Wire semantics missing") + "</p>"
            + previous.link(DETAIL + "#view-" + key, "Show in CFG"))
        if key == recovered:
            sections.extend([inventory.panel("Single deterministic readmission", admission), inventory.panel("Archived model row", archived),
                             file_link(out, run / admission["source_candidate"], "Original recorded model candidate")])
        for name, value in {"Exact instruction": ir, "Revalidated wire annotation": derived_specs.get(key),
            "Normalized annotation": raw["ir_semantics"].get(key), "Compiled annotation": compiled["ir_semantics"].get(key),
            "Source action bindings": mapping.get("source_action_bindings", {}).get(key),
            "Forward operation and data records": records.get(key), **{k: v[key] for k, v in joins.items()}}.items():
            sections.append(inventory.panel(name, value))
        sections.append(inventory.excerpt_rows([ir, derived_specs.get(key)], sources, missing) + "</section>")
    sections.extend(["<h2>Additional evidence</h2>", inventory.panel("Global records", {k: v for k, v in global_rows.items() if v}),
                     source_section(sources), "</body></html>"])
    page = "".join(sections)
    markers = IRAnchors()
    markers.feed(page)
    markers.close()
    if markers.ids != Counter(inventory.anchor("ir", ir) for ir in keys):
        raise ValueError("Offline readmission HTML omits instructions")
    (out / "annotations.html").write_text(page, encoding="utf-8")
    previous.write_json(out / "revalidated-control-routes.json", {"scope": title, "edges": edges})
    verification = {"scope": title, "graph": coverage, "readmitted_instruction": recovered, "official_selection": selection,
        "instruction_anchors": len(markers.ids), "record_count": len(records), "actual_route_case_count": sum(
            len(edge.get("recorded_routes") or []) for edge in edges), "forward_coverage": dict(Counter(cover.values())),
        "row_joins": counts, "source_references_without_excerpt": sorted(missing)}
    previous.write_json(out / "render-verification.json", verification)
    summary = (f"{len(keys)} instructions, {coverage['modeled_ir_count']} with wire semantics, {len(records)} with forward records. "
               f"Forward {forward['status']}, backward {backward['status']}, DOE {doe['status']}.")
    (out / "index.html").write_text(header + "<p>" + escape(summary) + "</p><p>" + previous.anchor(recovered)
        + " · Archived model row SHA-256 <code>" + admission["row_sha256"] + "</code></p><p>Original validator diagnostic "
        + "<code>" + escape(admission["archived_diagnostic_code"]) + "</code></p><p>Official selected CFG SHA-256 "
        + "<code>" + selection["cfg"]["sha256"] + "</code></p></body></html>", encoding="utf-8")
    return summary


if __name__ == "__main__":
    run = Path(inventory.load(HERE / "downstream-dispatch.json")["run"])
    for out in (HERE / "revalidated-results", HERE / "revalidated-results/initial-control"):
        if (out / "receipt.json").is_file():
            print(publish(run, out))
