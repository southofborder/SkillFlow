"""Publish separate, evidence-bound views of the authored regression and original online draft."""
from collections import Counter, defaultdict
from html import escape
import json
from pathlib import Path

from publish_results import (DETAIL, HERE, NS, OVERVIEW, IRAnchors, control_edges, file_link, graphs,
                             inventory, previous, publish, render_graphs)


HISTORICAL = HERE.parents[2] / "experiments/doe/runs/document-guided-google-search-call-routing-high-20261125-194132"
OFFLINE = "Authored offline regression"
DRAFT = "Original online graph draft · rejected"


def page(path, title, intro, nav, sections):
    markup = ['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" '
              'content="width=device-width, initial-scale=1"><title>', escape(title), "</title><style>",
              previous.STYLE, "</style></head><body><header><h1>", escape(title), "</h1><p>", escape(intro),
              "</p></header><nav>", *nav, "</nav>", *sections, "</body></html>"]
    path.write_text("".join(markup), encoding="utf-8")


def offline_report():
    directory = HERE / "offline-demonstration"
    directory.mkdir(exist_ok=True)
    artifacts = {key: HERE / ("offline-" + name + ".json") for key, name in (
        ("cfg", "graph"), ("wire", "authored-wire"), ("forward", "forward"), ("backward", "demands"),
        ("doe", "doe"), ("acceptance", "acceptance"))}
    artifacts["task"] = HISTORICAL / "task/task.json"
    saved = {key: inventory.load(path) for key, path in artifacts.items()}
    cfg, wire, forward, backward, doe, accepted, task = (saved[k] for k in artifacts)
    if (task["task_sha256"] != graphs.canonical({k: v for k, v in task.items() if k != "task_sha256"})
            or task["task_sha256"] != accepted["task_sha256"] or task["source_sha256"] != accepted["source_sha256"]):
        raise ValueError("Offline Task does not match regression evidence")
    instructions = {ir["id"]: ir for b in cfg["blocks"].values() for ir in b["instructions"]}
    if set(instructions) != set(wire["ir_semantics"]) or set(instructions) != set(forward["coverage"]):
        raise ValueError("Offline graph, semantics and forward coverage refer to different instructions")
    intro = ("This source-grounded regression uses authored annotations and synthetic inputs. "
             "The 20:53 online run selected no CFG or annotation. Its original draft is reported separately.")
    facts = {k: {"path": str(p), "sha256": graphs.digest(p)} for k, p in artifacts.items()}
    bundle = {"run": OFFLINE, "view_kind": "authored_offline_regression", "selection_committed": False, "selection": None,
              "status": {"status": "authored offline regression", "forward": forward["status"], "backward": backward["status"],
                         "doe": doe["status"]}, "cfg": cfg, "task": task, "annotation": wire, "files": facts}
    goals = defaultdict(list)
    for goal in backward["goals"]:
        if ir := goal["target"].get("instruction_id"):
            goals[ir].append(goal)
    labels = {
        "Diagnostic original CFG and accepted fragments - assembly did not commit": OFFLINE + " · complete annotated CFG",
        "Diagnostic uncommitted CFG overview": OFFLINE + " · CFG overview",
        "SkillFlow | DIAGNOSTIC: assembly did not commit": OFFLINE + " · complete annotated CFG",
        "SkillFlow | DIAGNOSTIC - assembly did not commit": OFFLINE + " · CFG overview",
        "ACCEPTED PROCESSING FRAGMENT": "AUTHORED WIRE SEMANTICS",
        "Accepted processing globals - NOT assembled annotation": "Complete authored annotation globals",
        "Selection and provenance": "Offline provenance",
        "Terminal diagnostic display of the accepted original CFG and processing fragments. No assembled annotation or selection committed. Missing records remain explicit.": intro,
        "Complete original CFG overview with accepted processing fragments only. Assembly did not commit. Links open the explicit diagnostic detail, not selected final annotations.": intro,
        "Accepted original CFG and processing fragments only; no committed annotation, Task bindings or merged sensitivity.": intro,
        "Original accepted fragments only; missing annotations are marked. Click an instruction for full detail.": intro,
    }

    def prepare_canvas(canvas, filename):
        for element in canvas.root.iter():
            if element.text in labels:
                element.text = labels[element.text]
        if filename == OVERVIEW:
            for a in canvas.root.iter(NS + "a"):
                ir = a.get("href", "").partition("#view-")[2]
                if ir not in instructions:
                    continue
                task_ids = sorted({g["requirement_id"] for g in goals[ir]})
                for t in a.iter(NS + "text"):
                    if t.text and "Task: unassembled" in t.text:
                        t.text = t.text.replace("Task: unassembled", "Task: " + (", ".join(task_ids) or "no direct goal"))

    edges = control_edges(cfg, forward["records"])
    coverage = render_graphs(bundle, directory, edges, prepare_canvas)
    previous.write_json(directory / "coverage.json", {"scope": OFFLINE, "graph": coverage,
        "forward": forward["status"], "coverage": dict(Counter(forward["coverage"].values())),
        "backward": backward["status"], "doe": doe["status"], "source_files": facts})
    previous.write_json(directory / "control-routes.json", {"scope": OFFLINE, "edges": edges})
    nav = [previous.link(OVERVIEW, "CFG overview"), previous.link(DETAIL, "Complete annotated CFG"),
           previous.link("annotations.html", "All instruction annotations"), previous.link("doe.html", "DOE boundary results"),
           previous.link("control-routes.json", "Control routes"), file_link(directory, artifacts["wire"], "Annotations JSON"),
           file_link(directory, artifacts["task"], "Complete historical Task"), previous.link("coverage.json", "Coverage and provenance"),
           previous.link("../online-results/index.html", "Actual online result")]
    sinks = defaultdict(list)
    for sink in doe["sinks"]:
        sinks[sink["boundary"]["instruction_id"]].append(sink)
    instruction_rows = ["<h2>Task</h2><p>" + escape(task["purpose"]["text"]) + "</p>",
                        inventory.panel("Complete Task requirements and evidence", task["requirements"])]
    audits = []
    for block_id, block in cfg["blocks"].items():
        instruction_rows.append("<h2>" + escape(block_id + " · " + block["block_name"]) + "</h2>")
        for ir in block["instructions"]:
            key = ir["id"]
            instruction_rows.append(f'<section id="{inventory.anchor("ir", key)}"><h3>' + escape(key + " · " + ir["opcode"])
                + '</h3><p>Forward coverage · ' + escape(forward["coverage"][key]) + ' · '
                + previous.link(DETAIL + "#view-" + key, "View in CFG") + '</p>'
                + inventory.panel("Full instruction and source", ir)
                + inventory.panel("Complete authored wire annotation", wire["ir_semantics"][key])
                + inventory.panel("Recorded forward transfer", forward["records"].get(key))
                + inventory.panel("Backward Task goals", goals[key])
                + inventory.panel("DOE boundary records", sinks[key]) + "</section>")
    for row in doe["sinks"]:
        b = row["boundary"]
        ir = b["instruction_id"]
        audits.append("<section><h2>" + previous.link("annotations.html#" + inventory.anchor("ir", ir), ir) + " · "
                      + escape(b["target"]) + "</h2><p>" + escape(b["sink_type"]) + " · recorded comparisons "
                      + str(len(row["data_reviews"])) + "</p>")
        for review in row["data_reviews"]:
            derivation = doe["derivations"]["sensitivity"][review["derivation_id"]]
            audits.append("<p><strong>" + escape(derivation["label"]) + "</strong> · input "
                + str(review["input_index"]) + " · " + escape(previous.field_path(derivation["path"]))
                + " · " + escape(review["conclusion"]) + "</p><p>" + escape(review["reason"]) + "</p>"
                + inventory.panel("Sensitivity evidence", derivation))
        audits.append(inventory.panel("Complete boundary and comparison records", row) + "</section>")
    page(directory / "annotations.html", OFFLINE + " · instruction annotations", intro, nav, instruction_rows)
    parser = IRAnchors()
    parser.feed((directory / "annotations.html").read_text(encoding="utf-8"))
    parser.close()
    if parser.ids != Counter(inventory.anchor("ir", ir) for ir in instructions):
        raise ValueError("Offline HTML omits an instruction")
    page(directory / "doe.html", OFFLINE + " · DOE", intro, [*nav, file_link(directory, artifacts["doe"], "Full DOE JSON"),
         file_link(directory, artifacts["backward"], "Full backward demands")], audits)
    summary = [f'<p>{coverage["block_count"]} blocks · {len(instructions)} annotated instructions · {len(edges)} control edges · '
               f'{accepted["protected_pairs"]} protected producer/dispatch pairs.</p>',
               "<p>Forward " + escape(forward["status"]) + " · backward " + escape(backward["status"]) + " · DOE "
               + escape(doe["status"]) + " · " + str(accepted["comparison_count"]) + " comparisons.</p>",
               "<h2>Task</h2><p>" + escape(task["purpose"]["text"]) + "</p><h2>Regression assumptions</h2><ul>",
               *("<li>" + escape(t) + "</li>" for t in accepted["assumptions"]), "</ul>"]
    page(directory / "index.html", OFFLINE + " · google-search", intro, nav, summary)
    return coverage


def online_draft(run):
    directory = HERE / "online-draft"
    directory.mkdir(exist_ok=True)
    call = run / "steps/graph/calls/a001"
    response = inventory.load(call / "response.json")
    validation = inventory.load(call / "validation.json")
    if validation["status"] != "structural_invalid" or validation["response_sha256"] != graphs.canonical(response):
        raise ValueError("Original draft differs from its recorded rejection")
    raw = json.loads(response) if isinstance(response, str) else response
    blocks = raw["blocks"]
    count = sum(1 + len(b["operations"]) for b in blocks)
    previous.write_json(directory / "graph-facts.json", raw)
    nav = [previous.link("graph-facts.json", "Full decoded model response"), file_link(directory, call / "validation.json", "Original rejection"),
           previous.link("../online-results/index.html", "Terminal online result"), previous.link("../offline-demonstration/index.html", "Authored offline regression")]
    sections = [inventory.panel("Recorded structural diagnostics", validation["diagnostics"])]
    verified = HERE / "recompiled-online-graph-verification.json"
    if verified.is_file():
        proof = inventory.load(verified)
        cfg_path = HERE / "recompiled-online-cfg.json"
        cfg = inventory.load(cfg_path)
        task_path = run / "task/task.json"
        edges = control_edges(cfg, None)
        ids = {ir["id"] for b in cfg["blocks"].values() for ir in b["instructions"]}
        transfers = {**proof["source_derived_handler_annotations"], **proof["source_derived_argument_annotations"]}
        if (Path(proof["source"]).resolve() != (call / "response.json").resolve()
                or proof["response_file_sha256"] != graphs.digest(call / "response.json")
                or proof["roundtrip_equal"] is not True or proof["fresh_model_calls"] != 0 or not set(transfers) <= ids
                or (len(cfg["blocks"]), len(ids), len(edges)) != (proof["blocks"], proof["IR"], proof["edges"])):
            raise ValueError("Offline recompilation evidence differs from the first online response or rendered graph")
        bundle = {"run": run.name, "view_kind": "online_response_recompiled_offline", "selection_committed": False,
                  "selection": None, "cfg": cfg, "task": inventory.load(task_path), "annotation": {"ir_semantics": transfers},
                  "status": {"status": "original online rejection; offline structural recompilation completed"},
                  "files": {p.name: {"path": str(p), "sha256": graphs.digest(p)} for p in (verified, cfg_path, task_path, call / "response.json")}}
        title = "Original online graph · recompiled offline"
        summary = (f'The corrected frontend compiled the unedited first model response into {len(ids)} instructions. '
                   f'{len(transfers)} source-derived transfers cover exception handling and optional argument binding. '
                   'The original online run selected no annotation.')
        def label(canvas, filename):
            for el in canvas.root.iter():
                text = el.text or ""
                if text.startswith("SkillFlow | DIAGNOSTIC"):
                    el.text = title + (" · overview" if filename == OVERVIEW else " · complete structure")
                elif text.startswith(("Terminal diagnostic display", "Complete original CFG overview", "Accepted original CFG", "Original accepted fragments only;")):
                    el.text = summary
                elif text in {"Diagnostic original CFG and accepted fragments - assembly did not commit",
                              "Diagnostic uncommitted CFG overview"}:
                    el.text = title
                elif text == "ACCEPTED PROCESSING FRAGMENT":
                    el.text = "OFFLINE SOURCE-DERIVED TRANSFER"
                elif text == "Accepted processing globals - NOT assembled annotation":
                    el.text = "Offline source-derived transfers"
                elif text == "Selection and provenance":
                    el.text = "Source and recompile provenance"
        coverage = render_graphs(bundle, directory, edges, label)
        previous.write_json(directory / "coverage.json", coverage)
        previous.write_json(directory / "control-routes.json", {"scope": title, "edges": edges})
        nav[:0] = [previous.link(OVERVIEW, "Recompiled CFG overview"), previous.link(DETAIL, "Full structural CFG"),
                   file_link(directory, cfg_path, "Recompiled CFG JSON"), file_link(directory, verified, "Recompile verification")]
        sections[:0] = ["<h2>Offline structural recompilation</h2><p>", escape(summary), "</p>",
                        inventory.panel("Source-derived handler and argument transfer records", transfers)]
    edge_count = 0
    for block in blocks:
        ref, exit = block["ref"], block["exit"]
        target = lambda name: previous.link("#" + inventory.anchor("block", name), name)
        if exit["kind"] == "outcome_dispatch":
            routes = ["Return → " + target(exit["on_return"]), "Throw → " + target(exit["on_throw"])]
        elif exit["kind"] == "branch":
            routes = [escape(a["condition"] or "Guarded arm") + " → " + target(a["target"]) for a in exit["arms"]]
        elif exit["kind"] == "jump":
            routes = [target(exit["target"])]
        else:
            routes = []
        edge_count += len(routes)
        sections.append(f'<section id="{inventory.anchor("block", ref)}"><h2>' + escape(ref) + "</h2><p>"
                        + (" · ".join(routes) if routes else "Terminal return") + "</p>")
        for op in block["operations"]:
            sections.append(inventory.panel(op["ref"] + " · " + op["opcode"], op,
                                             identifier=inventory.anchor("ir", ref + "/operations/" + op["ref"])))
        sections.append(inventory.panel("Exit · " + exit["kind"], exit, identifier=inventory.anchor("ir", ref + "/exit")) + "</section>")
    intro = (f"The first automatic GraphFacts response proposed {len(blocks)} blocks, {count} operations and exits, "
             f"and {edge_count} control edges. The online validator rejected it. The identifiers in this view are authored local references.")
    page(directory / "index.html", DRAFT, intro, nav, sections)
    return {"blocks": len(blocks), "operations_and_exits": count, "control_edges": edge_count}


if __name__ == "__main__":
    run = Path(inventory.load(HERE / "dispatch.json")["run"]).resolve(strict=True)
    offline = offline_report()
    draft = online_draft(run)
    publish(run, HERE / "online-results")
    print(json.dumps({"offline_instructions": offline["instruction_count"], "offline_edges": offline["control_edge_count"],
                      "original_rejected_draft": draft, "online_status": inventory.load(run / "result.json")["status"]}))
