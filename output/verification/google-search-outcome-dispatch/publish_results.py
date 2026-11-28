"""Publish the terminal run's selected graph, annotations, Task and recorded analyses."""
from argparse import ArgumentParser
from collections import Counter
from html import escape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import sys
from urllib.parse import quote
from xml.etree import ElementTree as ET


HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE.parent / "google-search-call-routing-20261125"))
import publish_run as previous

graphs, inventory = previous.graphs, previous.inventory
NS = "{" + graphs.NS + "}"
DETAIL = "annotated-cfg.svg"
OVERVIEW = "cfg-overview.svg"


class IRAnchors(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = Counter()

    def handle_starttag(self, tag, attrs):
        identifier = dict(attrs).get("id")
        if identifier and identifier.startswith("ir-"):
            self.ids[identifier] += 1


def file_link(directory, path, title):
    if directory.drive.lower() != path.drive.lower():
        return previous.link(path.as_uri(), title)
    return previous.link(quote(Path(os.path.relpath(path, directory)).as_posix(), safe="/"), title)


def accepted_graphs(run, directory, stages):
    """Show the exact committed CFG stages when final annotation selection failed."""
    saved = []
    for name, filename in (("graph", "initial.json"), ("revision-graph", "revision.json")):
        graph_file = run / "graph" / filename
        if not graph_file.is_file():
            continue
        artifact = previous.stage_artifact(run, stages, name)
        if artifact is None:
            continue
        cfg = inventory.load(graph_file)["cfg"]
        if cfg != artifact[2].get("cfg"):
            raise ValueError(f"{name} graph differs from the accepted stage value")
        rows = control_edges(cfg, None)
        table = ["<h2>Control edges</h2><table><tr><th>Edge</th><th>From</th><th>To</th><th>Condition</th></tr>"]
        for row in rows:
            table.append("<tr>" + "".join("<td>" + escape(v) + "</td>" for v in
                (row["id"], row["source_block_id"], row["target_block_id"],
                 row.get("disposition") or row["condition_text"] or "Unconditional")) + "</tr>")
        table.append("</table><h2>Instructions</h2>")
        ids = []
        for block, value in cfg["blocks"].items():
            table.append("<h3>" + escape(block + " · " + value["block_name"]) + "</h3>")
            for ir in value["instructions"]:
                ids.append(ir["id"])
                table.append(inventory.panel(ir["id"] + " · " + ir["opcode"], ir, identifier=inventory.anchor("ir", ir["id"])))
        page_file = f"cfg-structure-{name}.html"
        html = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Accepted CFG structure</title>'
                '<style>' + previous.STYLE + '</style></head><body><h1>Accepted CFG structure</h1>'
                + '<p>' + escape(run.name + " · " + name) + '</p><p>Final annotation selection unavailable.</p><nav>'
                + previous.link("index.html", "Audit results") + file_link(directory, graph_file, "Full CFG JSON")
                + "</nav>" + "".join(table) + "</body></html>")
        anchors = IRAnchors()
        anchors.feed(html)
        anchors.close()
        if anchors.ids != Counter(inventory.anchor("ir", ir) for ir in ids):
            raise ValueError("Accepted structure view omits instruction anchors")
        (directory / page_file).write_text(html, encoding="utf-8")
        saved.append({"stage": name, "html": page_file, "selection_committed": False,
                      "source": graph_file.relative_to(run).as_posix(), "sha256": graphs.digest(graph_file),
                      "block_count": len(cfg["blocks"]), "instruction_count": len(ids), "control_edge_count": len(rows),
                      "typed_dispatches": len({r["dispatch"] for r in rows if "dispatch" in r})})
    return saved


def control_edges(cfg, records):
    """Attach disposition only to a declared typed edge; retain its original display text."""
    rows = []
    for index, edge in enumerate(cfg["edges"], 1):
        terminal = cfg["blocks"][edge["source_block_id"]]["instructions"][-1]
        route = terminal["metadata"].get("outcome_dispatch")
        row = {"id": f"E{index:03}", **edge}
        if route is not None:
            target = edge["target_block_id"]
            roles = [role for role in ("return", "throw") if route["on_" + role] == target]
            if len(roles) != 1:
                raise ValueError(f"Ambiguous typed target for {terminal['id']} and {target}")
            actual = None if records is None or terminal["id"] not in records else [
                item for item in records[terminal["id"]].get("outcome_routes", []) if item["target"] == target]
            row.update(disposition=roles[0], producer=route["producer"], dispatch=terminal["id"], recorded_routes=actual)
            if actual:
                outcomes = records.get(route["producer"], {}).get("outcomes", [])
                cases = {(case["group"], case["case_id"]): case for case in outcomes}
                selected = [(case["group"], case["case_id"]) for case in actual]
                if len(set(selected)) != len(selected) or not set(selected) <= cases.keys():
                    raise ValueError(f"Recorded dispatch case differs from its actual producer at {terminal['id']}")
                row["recorded_producer_outcomes"] = [cases[key] for key in selected]
        rows.append(row)
    return rows


def label_edges(canvas, edges):
    controls = canvas.root.find("./*[@id='control-edges']")
    paths = {p.get("id"): p for p in controls.findall(NS + "path")}
    labels = {p.text: p for p in controls.findall(NS + "text")}
    ids = {row["id"] for row in edges}
    if set(paths) != ids or set(labels) != ids:
        raise ValueError("SVG edge inventory differs from the selected graph")
    for row in edges:
        if "disposition" not in row:
            continue
        role, identifier = row["disposition"], row["id"]
        label = labels[identifier]
        label.text = f"{identifier} · {role}"
        color = "#18634d" if role == "return" else "#9c391a"
        label.set("fill", color)
        label.set("font-weight", "700")
        # The stock renderer puts both outgoing labels at the same origin.
        if role == "throw":
            label.set("y", str(float(label.get("y")) + 17))
        path = paths[identifier]
        path.set("stroke", color)
        path.set("data-disposition", role)
        path.find(NS + "title").text = json.dumps(row, ensure_ascii=False)


def render_graphs(bundle, directory, edges, prepare_canvas=None, *, provenance_label="", link_inventory=False):
    detail, coverage, _, _ = graphs.render(bundle, provenance_label)
    overview, counts = graphs.render_overview(bundle, DETAIL, provenance_label)
    cfg = bundle["cfg"]
    ids = {ir["id"] for b in cfg["blocks"].values() for ir in b["instructions"]}
    if (len(ids) != coverage["instruction_count"] or len(ids) != counts["instructions"]
            or len(edges) != coverage["control_edge_count"] or len(edges) != counts["control_edges"]
            or coverage["result_use_count"] != counts["result_references"]):
        raise ValueError("Figure coverage differs from the selected CFG")
    detail_ids = {node.get("id") for node in detail.root.iter() if node.get("id")}
    if not all("instruction-" + ir in detail_ids and "view-" + ir in detail_ids for ir in ids):
        raise ValueError("Detailed SVG omits an instruction or its view")
    if link_inventory:
        for ir in ids:
            group = detail.root.find("./*[@id='instruction-" + ir + "']")
            title = group.find(NS + "text")
            group.remove(title)
            anchor = ET.SubElement(group, NS + "a", {"href": "annotations.html#" + inventory.anchor("ir", ir)})
            anchor.append(title)
    targets = {node.get("href", "") for node in overview.root.iter(NS + "a")}
    if (not all(DETAIL + "#view-" + ir in targets for ir in ids)
            or any(not href.startswith(DETAIL + "#") or href.partition("#")[2] not in detail_ids for href in targets)):
        raise ValueError("Overview has a missing or broken instruction link")
    for canvas, name in ((detail, DETAIL), (overview, OVERVIEW)):
        label_edges(canvas, edges)
        if prepare_canvas is not None:
            prepare_canvas(canvas, name)
        ET.ElementTree(canvas.root).write(directory / name, encoding="utf-8", xml_declaration=True)
    return coverage


def independent_task(run):
    owner = run / "task"
    if not (owner / "result.json").is_file():
        return None
    status = inventory.load(owner / "result.json")
    if status.get("status") != "complete":
        return None
    task = inventory.load(owner / "task.json")
    digest = graphs.canonical({k: v for k, v in task.items() if k != "task_sha256"})
    if digest != task["task_sha256"] or digest != status["task_ref"]["task_sha256"]:
        raise ValueError("Independent Task differs from its accepted reference")
    return task


def inherited_provenance(run):
    manifest = inventory.load(run / "manifest.json")
    ref = manifest.get("revalidated_upstream")
    if ref is None:
        return None
    receipt = inventory.load(graphs.reference(run, ref))
    origin = receipt["origin"]
    if (receipt["identity"] != "skillflow-revalidated-first-graph-v1"
            or receipt["validated_with"] != manifest["implementation"]["sha256"]
            or origin["graph_attempt"]["ordinal"] != 1):
        raise ValueError("Graph revalidation provenance differs from the child manifest")
    inherited = run / "inherited"
    original = origin["graph_attempt"]["artifacts"]["response.json"]
    for bound in (original, origin["original_task"], origin["original_flow"]):
        graphs.reference(inherited, bound)
    cfg = {"path": "graph/initial.json", "sha256": receipt["accepted_files"]["graph/initial.json"]}
    graphs.reference(run, cfg)
    return {"receipt": ref, "parent": Path(receipt["parent_directory"]).name,
            "graph_answer": {"path": "inherited/" + original["path"], "sha256": original["sha256"]},
            "task": {"path": "inherited/" + origin["original_task"]["path"], "sha256": origin["original_task"]["sha256"]},
            "flow": {"path": "inherited/" + origin["original_flow"]["path"], "sha256": origin["original_flow"]["sha256"]},
            "cfg": cfg, "original_graph_status": origin["original_graph_status"],
            "revalidated_graph_status": origin["current_graph_status"], "validated_with": receipt["validated_with"]}


def instruction_table(cfg, wire, directory, sections, *, compiled=None, records=None, coverage=None, selected):
    rows = {}
    for block, body in cfg["blocks"].items():
        for ir in body["instructions"]:
            key = ir["id"]
            rows[key] = {"block": block, "opcode": ir["opcode"], "wire_record": key in wire.get("ir_semantics", {}),
                         "compiled_record": None if compiled is None else key in compiled.get("ir_semantics", {}),
                         "forward_record": None if records is None else key in records,
                         "forward_coverage": (coverage or {}).get(key)}
    def state(value):
        return "Unavailable" if value is None else "Present" if value else "Missing"
    sections.append("<h2>Instruction coverage</h2><table><thead><tr><th>Instruction</th><th>Opcode</th><th>"
                    + ("Selected wire" if selected else "Accepted processing") + "</th><th>Compiled</th>"
                    "<th>Forward record</th><th>Forward coverage</th></tr></thead><tbody>")
    for key, row in rows.items():
        sections.append("<tr><td>" + previous.anchor(key) + "</td><td>" + escape(row["opcode"])
            + "</td><td>" + state(row["wire_record"]) + "</td><td>" + state(row["compiled_record"])
            + "</td><td>" + state(row["forward_record"]) + "</td><td>"
            + escape(row["forward_coverage"] or "Unavailable") + "</td></tr>")
    sections.append("</tbody></table>")
    previous.write_json(directory / "instruction-coverage.json", rows)
    return rows


def selected_report(run, directory, report, nav, sections):
    bundle = graphs.load_bundle(run)
    inv = inventory.load_inventory(run, run)
    task, cfg, wire = bundle["task"], bundle["cfg"], bundle["annotation"]
    if inv["artifacts"]["audit/wire-annotation.json"] != wire or inv["graph"] != cfg:
        raise ValueError("Inventory and graph renderers received different selected artifacts")
    compiled = inv["artifacts"]["audit/compiled-response.json"]
    fixed = report.get("inherited_provenance")
    if fixed is not None and any(inv["selection"][k] != fixed[k] for k in ("task", "cfg")):
        raise ValueError("Selected Task or CFG differs from the revalidated upstream receipt")
    records = inv["forward"].get("records.json")
    edges = control_edges(cfg, records)
    cover = inv["propagation"].get("coverage", {})
    instructions = {ir["id"]: ir for block in cfg["blocks"].values() for ir in block["instructions"]}
    selected_hash = inv["selection"]["cfg"]["sha256"]
    label = "Selected CFG SHA-256 " + selected_hash
    if fixed is not None:
        label += " · original graph response revalidated offline"
    def label_records(canvas, filename):
        for link in canvas.root.iter(NS + "a"):
            href = link.get("href", "")
            if filename == DETAIL:
                ir = href.partition("annotations.html#ir-")[2]
            else:
                ir = href.partition(DETAIL + "#view-")[2]
            if ir not in instructions:
                continue
            heading = link.find(NS + "text")
            heading.text += " · " + cover.get(ir, "forward unavailable")
    coverage = render_graphs(bundle, directory, edges, label_records, provenance_label=label, link_inventory=True)
    qa = previous.render_inventory(run, directory, label)
    anchors = IRAnchors()
    with (directory / "annotations.html").open(encoding="utf-8") as stream:
        while chunk := stream.read(1 << 17):
            anchors.feed(chunk)
    anchors.close()
    if anchors.ids != Counter(inventory.anchor("ir", ir) for ir in instructions) or qa["ir_rows"]["omitted"]:
        raise ValueError("Annotation HTML anchors differ from the selected instructions")
    previous.write_json(directory / "coverage.json", {"graph": coverage, "annotation_view": qa})
    previous.write_json(directory / "control-routes.json", {**previous.structural_routes(cfg), "edges": edges})
    previous.write_json(directory / "annotations.json", {
        "run": run.name, "selection": inv["selection"], "task": task, "wire_annotation": wire,
        "compiled_annotation": compiled, "instruction_ids": list(instructions),
        "forward_status": qa["forward_status"], "forward_coverage": inv["propagation"].get("coverage")})
    rows = previous.summarize_boundaries(inv)
    report.update(selection=inv["selection"], graph={k: coverage[k] for k in (
        "block_count", "instruction_count", "control_edge_count", "result_use_count", "modeled_ir_count", "unmodeled_ir_ids")},
        boundary_results=rows, typed_dispatches=len({r["dispatch"] for r in edges if "dispatch" in r}))
    doe = inv["backward"].get("doe-result.json")
    reviews = [review for row in rows for sink in row["doe"] for review in sink["comparisons"]]
    report["analysis"] = {"forward": qa["forward_status"],
        "forward_coverage": qa["forward_coverage"] if qa["forward_status"] is not None else None,
        "backward": inv["backward"].get("audit/demand-support.json", {}).get("status"), "doe": qa["doe_status"],
        "comparison_counts": None if doe is None else dict(Counter(r["conclusion"] for r in reviews))}
    nav.extend(previous.link(path, title) for path, title in (
        (OVERVIEW, "CFG overview"), (DETAIL, "Full annotated CFG"), ("annotations.html", "Per-instruction evidence"),
        ("annotations.json", "Complete annotations and Task JSON"), ("control-routes.json", "Control routes"),
        ("coverage.json", "Coverage audit"), ("instruction-coverage.json", "Per-instruction coverage JSON")))
    if doe is not None:
        nav.append(file_link(directory, run / "doe/doe-result.json", "DOE JSON"))
    sections.append(f'<p>{len(cfg["blocks"])} blocks · {len(instructions)} instructions · {len(edges)} control edges · '
        f'{coverage["modeled_ir_count"]} instructions with selected semantics · {report["typed_dispatches"]} typed outcome dispatches.</p>')
    sections.append("<p>" + " · ".join(escape(name.title() + " " + (report["analysis"][name] or "unavailable"))
                                        for name in ("forward", "backward", "doe")) + "</p>")
    typed = [r for r in edges if "disposition" in r]
    if typed:
        report["recorded_dispatches"] = (None if records is None else len({r["dispatch"] for r in typed if r["recorded_routes"]}))
        report["recorded_route_cases"] = (None if records is None else sum(len(r["recorded_routes"] or ()) for r in typed))
        sections.append("<h2>Operation outcomes</h2><table><thead><tr><th>Producer</th><th>Dispatch</th>"
                        "<th>Outcome</th><th>Destination</th><th>Recorded cases</th></tr></thead><tbody>")
        for row in typed:
            actual = row["recorded_routes"]
            cases = ("Dispatch record unavailable" if actual is None else
                     ", ".join(sorted({case["case_id"] for case in actual})) or "No case recorded on this edge")
            sections.append("<tr><td>" + previous.anchor(row["producer"]) + "</td><td>" + previous.anchor(row["dispatch"])
                + "</td><td>" + escape(row["disposition"]) + "</td><td>" + escape(row["target_block_id"])
                + "</td><td>" + escape(cases) + "</td></tr>")
        sections.append("</tbody></table>")
    sections.extend(previous.boundary_html(rows, doe is not None))
    instruction_table(cfg, wire, directory, sections, compiled=compiled, records=records,
                      coverage=cover, selected=True)
    return task


def unselected_inherited(run, directory, result, report, nav, sections):
    fixed = report["inherited_provenance"]
    cfg = inventory.load(graphs.reference(run, fixed["cfg"]))["cfg"]
    task = inventory.load(graphs.reference(run, fixed["task"]))
    wire = {"ir_semantics": {}, "processing_gaps": []}
    accepted = previous.stage_artifact(run, result["stages"], "processing")
    files = {"cfg": fixed["cfg"], "task": fixed["task"], "original_graph_answer": fixed["graph_answer"]}
    if accepted is not None:
        owner = run / "steps/processing"
        ref = inventory.load(owner / "manifest.json")["context"]["cfg_path"]
        if (owner / ref["path"]).resolve() != (run / fixed["cfg"]["path"]).resolve() or ref["sha256"] != fixed["cfg"]["sha256"]:
            raise ValueError("Accepted processing is bound to a different CFG")
        wire = accepted[2]
        files["processing"] = {"path": accepted[0].relative_to(run).as_posix(), "sha256": accepted[1]}
    bundle = {"run": run.name, "selection": None, "selection_committed": False,
              "view_kind": "revalidated_upstream_without_selected_annotation", "status": result,
              "cfg": cfg, "task": task, "annotation": wire, "files": files}
    edges = control_edges(cfg, None)
    coverage = render_graphs(bundle, directory, edges, link_inventory=True,
        provenance_label="Revalidated upstream CFG SHA-256 " + fixed["cfg"]["sha256"] + " · final selection unavailable")
    rows = instruction_table(cfg, wire, directory, sections, selected=False)
    fragments = []
    for name in ("processing", "sensitivity", "task-correspondence", "revision-processing",
                 "revision-sensitivity", "revision-task-correspondence"):
        artifact = previous.stage_artifact(run, result["stages"], name)
        if artifact is not None:
            fragments.append({"stage": name, "value_file": artifact[0].relative_to(run).as_posix(), "sha256": artifact[1]})
            nav.append(file_link(directory, artifact[0], name + " · independently accepted fragment"))
    html = ["<!doctype html><html lang='en'><head><meta charset='utf-8'><title>Unselected instruction evidence</title>"
            "<style>" + previous.STYLE + "</style></head><body><h1>Unselected instruction evidence</h1>"
            "<p>First graph response revalidated offline. Final annotations, forward analysis and DOE are unavailable.</p>"
            "<p>Revalidated CFG SHA-256 <code>" + fixed["cfg"]["sha256"] + "</code></p><nav>"
            + previous.link("index.html", "Run results") + previous.link(OVERVIEW, "CFG overview")
            + previous.link(DETAIL, "Full CFG") + "</nav>"]
    for body in cfg["blocks"].values():
        for ir in body["instructions"]:
            key = ir["id"]
            html.append('<section id="' + inventory.anchor("ir", key) + '"><h2>' + escape(key + " · " + ir["opcode"])
                + "</h2>" + inventory.panel("Complete revalidated IR", ir)
                + (inventory.panel("Accepted processing fragment", wire["ir_semantics"][key]) if rows[key]["wire_record"]
                   else "<p>Accepted processing record missing.</p>")
                + inventory.panel("Processing gaps", [g for g in wire.get("processing_gaps", []) if g["instruction_id"] == key])
                + "</section>")
    html.append("</body></html>")
    detail_html = "".join(html)
    anchors = IRAnchors()
    anchors.feed(detail_html)
    anchors.close()
    if anchors.ids != Counter(inventory.anchor("ir", ir) for ir in rows):
        raise ValueError("Unselected evidence view omits an instruction")
    (directory / "annotations.html").write_text(detail_html, encoding="utf-8")
    previous.write_json(directory / "coverage.json", {"graph": coverage, "selection": None})
    previous.write_json(directory / "control-routes.json", {**previous.structural_routes(cfg), "edges": edges})
    previous.write_json(directory / "annotations.json", {"selection": None, "independently_accepted": fragments,
        "task": task, "processing": wire if accepted is not None else None, "instruction_ids": list(rows)})
    report["accepted_graphs"] = [{"stage": "revalidated_upstream", "selection_committed": False, **fixed["cfg"],
        "block_count": len(cfg["blocks"]), "instruction_count": len(rows), "control_edge_count": len(edges),
        "typed_dispatches": len({r["dispatch"] for r in edges if "dispatch" in r})}]
    report["accepted_fragments"] = fragments
    nav.extend(previous.link(path, title) for path, title in ((OVERVIEW, "Revalidated CFG overview"),
        (DETAIL, "Revalidated CFG with available processing"), ("annotations.html", "Per-instruction evidence"),
        ("control-routes.json", "Control routes"), ("instruction-coverage.json", "Per-instruction coverage JSON")))
    return task


def publish(run, directory, boundary=None):
    run, directory = run.resolve(strict=True), directory.resolve()
    if directory.is_relative_to(run):
        raise ValueError("Use a report directory outside the recorded run")
    result = inventory.load(run / "result.json")
    if result.get("status") in {"running", "prepared"}:
        raise ValueError("Publication requires a terminal result")
    directory.mkdir(parents=True, exist_ok=True)
    if (directory / "results.json").is_file() and inventory.load(directory / "results.json").get("run") != run.name:
        raise ValueError("The report directory belongs to a different run")
    report = {"run": run.name, "run_directory": str(run), "status": result["status"], "stage": result.get("stage"),
              "stages": result.get("stages", {}), "limitations": result.get("limitations"), "reason": result.get("reason"),
              "selection": None, "graph": None, "analysis": None, "boundary_results": None}
    nav, sections = [], []
    fixed = inherited_provenance(run)
    if fixed is not None:
        report["inherited_provenance"] = fixed
        report["request_counts"] = result["counts"]
        nav.extend([file_link(directory, run / fixed["receipt"]["path"], "Upstream revalidation provenance"),
                    file_link(directory, run / fixed["graph_answer"]["path"], "Original graph answer")])
        sections.append("<h2>Graph provenance</h2><p>The Task, flow and first graph response come from "
            + escape(fixed["parent"]) + ". The first graph response was revalidated offline.</p>"
            + "<p>CFG file SHA-256 <code>" + fixed["cfg"]["sha256"] + "</code></p>")
    if (run / "selection.json").is_file():
        task = selected_report(run, directory, report, nav, sections)
    else:
        if result.get("selected_annotation") is not None:
            raise ValueError("Terminal result declares a selected annotation but selection.json is missing")
        sections.append("<p>No final Task, CFG and annotation bundle was selected. Forward, backward and DOE results are unavailable.</p>")
        if fixed is not None:
            task = unselected_inherited(run, directory, result, report, nav, sections)
        else:
            task = independent_task(run)
            report["accepted_graphs"] = accepted_graphs(run, directory, report["stages"])
            for row in report["accepted_graphs"]:
                nav.append(previous.link(row["html"], "Independently accepted CFG · " + row["stage"]))
                sections.append(f'<p>{escape(row["stage"])} · {row["instruction_count"]} instructions · '
                                f'{row["control_edge_count"]} control edges · final annotations unavailable.</p>')
    if task is not None:
        task_path = (run / report["selection"]["task"]["path"] if report["selection"] else
                     run / fixed["task"]["path"] if fixed else run / "task/task.json")
        report["task"] = {"kind": "selected" if report["selection"] else "independently accepted",
                          "sha256": task["task_sha256"], "requirement_count": len(task["requirements"]),
                          "path": task_path.relative_to(run).as_posix(), "purpose": task["purpose"]["text"]}
        nav.append(file_link(directory, task_path, "Complete Task"))
        sections.insert(0, "<h2>Task</h2><p>" + escape(task["purpose"]["text"]) + "</p>")
    else:
        report["task"] = None
    if boundary is None:
        boundary = next((p for p in (directory / "boundary-verification.json", directory.parent / "boundary-verification.json")
                         if p.is_file() and inventory.load(p).get("run") == run.name), None)
    if boundary is not None:
        boundary = boundary.resolve(strict=True)
        checked = inventory.load(boundary)
        if checked.get("run") != run.name or checked.get("selection") != report["selection"]:
            raise ValueError("Boundary verification belongs to a different run or selection")
        nav.append(file_link(directory, boundary, "Boundary verification"))
        report["boundary_verification"] = {"path": str(boundary), "sha256": graphs.digest(boundary)}
    if (run / "report.md").is_file():
        nav.append(file_link(directory, run / "report.md", "Original run report"))
    if fixed is not None:
        for folder, title in (("initial-assembled", "Provisional initial assembly"),
                              ("revalidated-results", "Separate offline readmission"),
                              ("revalidated-results/initial-control", "Earlier assembly control")):
            path = directory.parent / folder / "index.html"
            if path.is_file():
                nav.append(file_link(directory, path, title))
    for folder, title in (("online-draft", "Rejected original graph draft"), ("offline-demonstration", "Authored offline regression")):
        path = directory.parent / folder / "index.html"
        if path.is_file():
            nav.append(file_link(directory, path, title))
    nav.append(previous.link("results.json", "Run results JSON"))
    previous.write_json(directory / "results.json", report)
    status = escape(result["status"] + (" · " + result["stage"] if result.get("stage") else ""))
    markup = ['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" '
              'content="width=device-width, initial-scale=1"><title>google-search · Audit results</title><style>',
              previous.STYLE, "</style></head><body><header><h1>google-search</h1><p>", escape(run.name),
              "</p><p>Run status · ", status, "</p></header><nav>", *nav, "</nav>", *sections]
    if result.get("reason"):
        markup.append("<p>" + escape(result["reason"]) + "</p>")
    if report["limitations"]:
        markup.extend(["<h2>Recorded limitations</h2><ul>", *("<li>" + escape(v) + "</li>" for v in report["limitations"]), "</ul>"])
    (directory / "index.html").write_text("".join([*markup, "</body></html>"]), encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path)
    parser.add_argument("--out", type=Path, default=HERE / "online-results")
    parser.add_argument("--boundary", type=Path)
    args = parser.parse_args()
    path = args.run or Path(inventory.load(HERE / "dispatch.json")["run"])
    result = publish(path, args.out, args.boundary)
    print(json.dumps({"run": result["run"], "status": result["status"], "graph": result["graph"],
                      "index": str(args.out.resolve() / "index.html")}, ensure_ascii=False))
