"""Publish the selected automatic run and its DOE evidence. Reads saved artifacts only."""
from argparse import ArgumentParser
from collections import Counter
from html import escape
import json
import os
from pathlib import Path
import sys
from urllib.parse import quote
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "google-search-full-20261125"))
import render_annotation_inventory as inventory
import render_full_cfg as graphs


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def link(url, label):
    return f'<a href="{escape(url, quote=True)}">{escape(label)}</a>'


def file_link(directory, path, label):
    relative = Path(os.path.relpath(path, directory)).as_posix()
    return link(quote(relative, safe="/"), label)


def render_figures(bundle, out, fixture_label):
    detail, coverage, _, _ = graphs.render(bundle, fixture_label)
    detail_name = "annotated-cfg.svg"
    overview, counts = graphs.render_overview(bundle, detail_name, fixture_label)
    ET.ElementTree(detail.root).write(out / detail_name, encoding="utf-8", xml_declaration=True)
    ET.ElementTree(overview.root).write(out / "cfg-overview.svg", encoding="utf-8", xml_declaration=True)
    ids = {node.get("id") for node in detail.root.iter() if node.get("id")}
    expected = {ins["id"] for block in bundle["cfg"]["blocks"].values() for ins in block["instructions"]}
    assert len(expected) == coverage["instruction_count"] == counts["instructions"]
    assert all("instruction-" + ir in ids and "view-" + ir in ids for ir in expected)
    assert coverage["control_edge_count"] == counts["control_edges"]
    assert coverage["result_use_count"] == counts["result_references"]
    for node in overview.root.iter("{%s}a" % graphs.NS):
        dest = node.attrib["href"]
        if not dest.startswith(detail_name + "#") or dest.partition("#")[2] not in ids:
            raise ValueError(f"Broken CFG overview link {dest!r}")
    return coverage


def render_inventory(run, out, fixture_label):
    with (out / "annotations.html").open("w", encoding="utf-8") as stream:
        for section in inventory.render(run, run):
            if isinstance(section, dict):
                return section
            if section.startswith("<header>"):
                heading = '<header><div>'
                section = section.replace(heading, heading + "<p>" + escape(fixture_label) + "</p>", 1) if fixture_label else section
            stream.write(section)
    raise ValueError("The annotation inventory did not produce a coverage audit")


def anchor(ir):
    return link("annotations.html#" + inventory.anchor("ir", ir), ir)


def summarize_boundaries(inv):
    compiled = inv["artifacts"]["audit/compiled-response.json"]
    declared = compiled.get("sink_boundaries", [])
    observed = inv["forward"].get("sinks.json", [])
    result = inv["backward"].get("doe-result.json")
    sinks = result["sinks"] if result is not None else []
    derivations = result["derivations"]["sensitivity"] if result is not None else {}

    def coord(boundary):
        return json.dumps(boundary, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    def fresh(boundary):
        return {"boundary": boundary, "declared": False, "recorded": False, "doe": []}

    rows = {}
    for collection, name in ((declared, "declared"), (observed, "recorded")):
        for boundary in collection:
            rows.setdefault(coord(boundary), fresh(boundary))[name] = True
    for sink in sinks:
        boundary = sink["boundary"]
        row = rows.setdefault(coord(boundary), fresh(boundary))
        reviews = []
        for review in sink["data_reviews"]:
            signal = derivations[review["derivation_id"]]
            reviews.append({**review, "sensitivity": signal})
        row["doe"].append({"id": sink["id"], "actual_payload": sink["actual_payload"],
                            "related_requirements": sink["related_requirements"], "comparisons": reviews,
                            "limitations": sink["limitations"]})
    return sorted(rows.values(), key=lambda r: coord(r["boundary"]))


def structural_routes(cfg):
    targets = {edge["target_block_id"] for edge in cfg["edges"]}
    source_blocks = {edge["source_block_id"] for edge in cfg["edges"]}
    return {
        "entries": [b for b in cfg["blocks"] if b == cfg["entry_block_id"] or b not in targets],
        "exits": [b for b in cfg["blocks"] if b not in source_blocks],
        "blocks": {b: {"name": block["block_name"], "instructions": [ir["id"] for ir in block["instructions"]]}
                   for b, block in cfg["blocks"].items()},
        "edges": cfg["edges"],
    }


def stage_artifact(run, stages, name):
    """Read a committed stage value, including a stage-local partial acceptance."""
    status = stages.get(name, {}).get("status")
    if status not in {"complete", "partial"}:
        return None
    owner = run / "steps" / name
    receipt = inventory.load(owner / "result.json")
    if receipt.get("status", "complete") not in {"complete", "partial"} or not receipt.get("value_file"):
        return None
    value_path = (owner / receipt["value_file"]).resolve()
    if value_path.parent != owner:
        raise ValueError(f"Stage value is outside {name}")
    chain = inventory.load(owner / "calls/chain.json")
    if graphs.canonical(chain) != receipt["response_chain_sha256"] or chain.get("accepted_call") != receipt.get("accepted_call"):
        raise ValueError(f"Acceptance chain differs for {name}")
    if receipt.get("status", "complete") == "complete" and not receipt.get("accepted_call"):
        return None
    return value_path, receipt["value_sha256"], inventory.load(value_path, receipt["value_sha256"])


def structure_only(run, directory, stages, fixture_label):
    """Publish each independently accepted CFG; final annotation status stays unavailable."""
    saved = []
    for stage, filename in (("graph", "initial.json"), ("revision-graph", "revision.json")):
        graph_path = run / "graph" / filename
        if not graph_path.is_file():
            continue
        accepted = stage_artifact(run, stages, stage)
        if accepted is None:
            continue
        cfg = inventory.load(graph_path)["cfg"]
        if accepted[2].get("cfg") != cfg:
            raise ValueError(f"The saved {stage} CFG differs from its accepted stage value")
        sources = inventory.read_sources(run)
        graph_digest = graphs.digest(graph_path)
        fragments = []
        for name in ("processing", "task-correspondence", "sensitivity",
                     "revision-processing", "revision-task-correspondence", "revision-sensitivity"):
            artifact = stage_artifact(run, stages, name)
            if artifact is None:
                continue
            owner = run / "steps" / name
            ref = inventory.load(owner / "manifest.json")["context"]["cfg_path"]
            if (owner / ref["path"]).resolve() == graph_path and ref["sha256"] == graph_digest:
                fragments.append({"stage": name, "status": stages[name]["status"], "path": artifact[0].relative_to(run).as_posix(),
                                  "sha256": artifact[1]})
        shape = structural_routes(cfg)
        paths = {item["id"]: item for block in cfg["blocks"].values() for item in block["instructions"]}
        def block_anchor(block_id):
            return link("#" + inventory.anchor("block", block_id), block_id)
        page = [f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Accepted CFG · {escape(stage)}</title>',
                '<meta name="viewport" content="width=device-width,initial-scale=1"><style>' + STYLE + '</style></head><body>']
        if fixture_label:
            page += ['<p class="fixture">', escape(fixture_label), '</p>']
        page += ["<header><h1>Accepted CFG structure</h1><p>", escape(run.name), "</p><p>Stage · ", escape(stage),
                 " · ", str(len(shape["blocks"])), " blocks · ", str(len(paths)), " IR instructions · ",
                 str(len(shape["edges"])), " control edges</p></header><nav>", link("index.html", "Audit summary"),
                 file_link(directory, graph_path, "Original CFG JSON"), "</nav>",
                 "<p>Final annotations, task bindings, forward records and DOE comparisons are unavailable for this bundle.</p>",
                 "<h2>Upstream records for this graph</h2><ul>"]
        for fragment in fragments:
            page += ["<li>", file_link(directory, run / fragment["path"], fragment["stage"]), " · ",
                     escape(fragment["status"]), "</li>"]
        if not fragments:
            page.append("<li>No accepted annotation fragments.</li>")
        page += ["</ul><h2>Control flow</h2><p>Entry blocks · ", ", ".join(block_anchor(b) for b in shape["entries"]),
                 "</p><p>Exit blocks · ", ", ".join(block_anchor(b) for b in shape["exits"]), "</p>",
                 "<div class=\"scroll\"><table><thead><tr><th>From</th><th>To</th><th>Condition</th></tr></thead><tbody>"]
        for edge in cfg["edges"]:
            page += ["<tr><td>", block_anchor(edge["source_block_id"]), "</td><td>", block_anchor(edge["target_block_id"]),
                     "</td><td>", escape(edge.get("condition_text") or "Unconditional"), "</td></tr>"]
        page.append("</tbody></table></div><h2>Instructions</h2>")
        definitions = {out["identifier"]: row["id"] for row in paths.values() for out in row["outputs"] if out["type"] == "result"}
        for b, block in cfg["blocks"].items():
            page += [f'<h3 id="{inventory.anchor("block", b)}">', escape(b + " · " + block["block_name"]), "</h3>"]
            for ir in block["instructions"]:
                identifier = ir["id"]
                page += [f'<section id="{inventory.anchor("ir", identifier)}"><h4>', escape(identifier + " · " + ir["opcode"]),
                         "</h4><p>Final annotation · unavailable</p><details><summary>Operands, dependencies and source</summary>",
                         "<p>Inputs</p><ul>", inventory.format_operands(ir["inputs"], definitions), "</ul><p>Outputs</p><ul>",
                         inventory.format_operands(ir["outputs"], {}), "</ul>", inventory.excerpt_rows(ir, sources, set()),
                         inventory.panel("Complete instruction", ir), "</details></section>"]
        page.append("<h2>Frozen source files</h2>")
        for filename_key, lines in sources.items():
            path = run / "source/inputs/package" / filename_key.removeprefix("skill/")
            page += ["<details><summary>", escape(filename_key), "</summary>", file_link(directory, path, "Open source file"), "<pre>"]
            for line_no, line in enumerate(lines, 1):
                line_id = inventory.anchor("line", f"{filename_key}:{line_no}")
                page.append(f'<span id="{line_id}">{line_no:>3}  {escape(line)}</span>\n')
            page.append("</pre></details>")
        page.append("</body></html>")
        html_path = directory / f"cfg-structure-{stage}.html"
        html_path.write_text("".join(page), encoding="utf-8")
        saved.append({"stage": stage, "view_kind": "structure_only", "selection_committed": False,
                      "status": "accepted_cfg_without_selected_annotation", "html": html_path.name,
                      "source": graph_path.relative_to(run).as_posix(), "sha256": graph_digest,
                      "block_count": len(cfg["blocks"]), "instruction_count": len(paths), "control_edge_count": len(cfg["edges"]),
                      "ir_annotation_status": dict.fromkeys(paths, "unavailable"), "upstream_fragments": fragments})
    return saved


STYLE = """
:root{color:#203544;background:#f6f8fa;font:16px/1.55 system-ui,sans-serif}
body{max-width:74rem;margin:0 auto;padding:2.2rem 3vw 5rem}h1,h2{letter-spacing:-.025em;line-height:1.18}
h1{font-size:2.1rem;margin:0}h2{margin:2.2rem 0 .8rem}a{color:#075b75;text-underline-offset:.15em}
header{border-bottom:2px solid #365b64;padding-bottom:1rem}header p{margin:.45rem 0;color:#495e6c}
nav{display:flex;gap:.65rem;flex-wrap:wrap;margin:1.2rem 0}nav a{padding:.45rem .8rem;background:white;border:1px solid #a9bcc1;
border-radius:5px;text-decoration:none}nav a:first-child{background:#165960;color:white;border-color:#165960}
table{width:100%;border-collapse:collapse;background:white;font-size:.94rem}
th,td{padding:.6rem .75rem;text-align:left;border-bottom:1px solid #dbe3e7;vertical-align:top}th{background:#e7eff1}
code{font-size:.9em;overflow-wrap:anywhere}details{margin:.35rem 0}summary{cursor:pointer;color:#245569}
.scroll{overflow:auto}.muted{color:#536876}.fixture{font-weight:600;color:#9a3412}li{margin:.4rem 0}
"""


def field_path(value):
    return "$" + "".join("." + key if isinstance(key, str) and key.isidentifier() else
                         "[" + json.dumps(key, ensure_ascii=False) + "]" for key in value)


def boundary_html(rows, available):
    yield "<h2>Data boundaries</h2>"
    if not rows:
        yield "<p>No boundary records are available in the selected artifacts.</p>"
        return
    yield '<div class="scroll"><table><thead><tr><th>Instruction / operation</th><th>Recipient or location</th><th>Exposure</th><th>DOE comparison</th></tr></thead><tbody>'
    for row in rows:
        b = row["boundary"]
        coord = [b["event_index"], *([b["body_event_index"]] if b.get("body_event_index") is not None else []), b["op_index"]]
        yield "<tr><td>" + anchor(b["instruction_id"]) + "<br><small>" + escape(" / ".join(map(str, coord))) + "</small></td>"
        yield "<td>" + escape(b["target"]) + "<br><small>" + escape(b["sink_type"]) + "</small></td>"
        reach = "Forward boundary record" if row["recorded"] else ("Declared boundary only" if row["declared"] else "DOE boundary record")
        yield "<td>" + reach + "</td><td>"
        if not row["doe"]:
            yield "No DOE record" if available else "DOE unavailable"
        for sink in row["doe"]:
            reviews = sink["comparisons"]
            counts = Counter(item["conclusion"] for item in reviews)
            yield escape(", ".join(f"{n} {k}" for k, n in sorted(counts.items())) or "No sensitive range compared")
            if reviews:
                yield "<details><summary>Sensitive fields and versions</summary><ul>"
                for item in reviews:
                    v = item["sensitivity"]
                    reqs = ", ".join(sink["related_requirements"]) or "None"
                    reduction = json.dumps(item["reduction"], ensure_ascii=False) if item["reduction"] is not None else "None"
                    yield ("<li><b>" + escape(v["label"]) + "</b> · <code>" + escape(field_path(v["path"])) +
                           "</code> · " + escape(v["relation"]) + "<br>Input " + str(item["input_index"]) +
                           " · " + link("annotations.html#" + inventory.anchor("data", v["data_id"]), v["data_id"][:19] + "…") +
                           "<br>" + escape(item["reason"]) + "<br>Boundary task references · " + escape(reqs) +
                           "<br>Reduction · " + escape(reduction) + "</li>")
                yield "</ul></details>"
        yield "</td></tr>"
    yield "</tbody></table></div>"


def publish(run, directory, fixture_label):
    if directory.is_relative_to(run) or not directory.is_relative_to(HERE):
        raise ValueError("Write to a report folder below this verification directory, outside the recorded run.")
    result = inventory.load(run / "result.json")
    selected = (run / "selection.json").is_file()
    directory.mkdir(parents=True, exist_ok=True)
    report = {"run": run.name, "run_directory": str(run), "fixture_label": fixture_label or None,
              "status": result["status"], "stage": result.get("stage"), "stages": result.get("stages"),
              "reason": result.get("reason"), "limitations": result.get("limitations"),
              "selection": None, "graph": None, "analysis": None, "boundary_results": None}
    header = [file_link(directory, run / "report.md", "Automatic run report")] if (run / "report.md").is_file() else []
    body = []
    if selected:
        inv = inventory.load_inventory(run, run)
        report["selection"] = inv["selection"]
        bundle = graphs.load_bundle(run)
        coverage = render_figures(bundle, directory, fixture_label)
        qa = render_inventory(run, directory, fixture_label)
        assert qa["instructions"] == coverage["instruction_count"] and qa["ir_rows"]["omitted"] == 0
        write_json(directory / "coverage.json", {"graph": coverage, "annotation_view": qa})
        report["graph"] = {k: coverage[k] for k in ("block_count", "instruction_count", "control_edge_count",
                                                    "result_use_count", "modeled_ir_count", "unmodeled_ir_ids")}
        rows = summarize_boundaries(inv)
        report["boundary_results"] = rows
        doe = inv["backward"].get("doe-result.json")
        reviews = [item for row in rows for sink in row["doe"] for item in sink["comparisons"]]
        reductions = [item["id"] for item in reviews if item["reduction"] is not None]
        report["analysis"] = {"forward": qa["forward_status"], "forward_coverage": qa["forward_coverage"],
                              "backward": inv["backward"].get("audit/demand-support.json", {}).get("status"),
                              "doe": qa["doe_status"],
                              "comparison_counts": dict(Counter(x["conclusion"] for x in reviews)) if doe is not None else None,
                              "comparisons_with_reduction": reductions if doe is not None else None}
        write_json(directory / "control-routes.json", structural_routes(inv["graph"]))
        header = [link("cfg-overview.svg", "CFG overview"), link("annotated-cfg.svg", "Full editable CFG"),
                  link("annotations.html", "Search all annotations"), *header]
        if doe is not None:
            header += [file_link(directory, run / "doe/doe-result.json", "Full DOE JSON")]
        header += [link("control-routes.json", "Control edges"), link("results.json", "Boundary evidence JSON")]
        body += [f'<p>{qa["blocks"]} blocks · {qa["instructions"]} IR instructions · {qa["cfg_edges"]} control edges · '
                 f'{coverage["modeled_ir_count"]} instructions with selected semantics.</p>',
                 "<p>Forward · " + escape(qa["forward_status"] or "unavailable") + " &nbsp; Backward · " +
                 escape(report["analysis"]["backward"] or "unavailable") + " &nbsp; DOE · " +
                 escape(qa["doe_status"] or "unavailable") + "</p>", *boundary_html(rows, doe is not None)]
    else:
        header.append(link("results.json", "Run status JSON"))
        body.append("<p>The run did not select a complete Task, CFG and annotation bundle.</p>")
        accepted = structure_only(run, directory, result.get("stages", {}), fixture_label)
        if accepted:
            report["accepted_graphs"] = accepted
            report["graph"] = {"view_kind": "structure_only", "selection_committed": False,
                               "stages": [row["stage"] for row in accepted]}
        for row in accepted:
            header.append(link(row["html"], "Accepted CFG structure · " + row["stage"]))
            body += [f'<p>{escape(row["stage"])} · {row["block_count"]} blocks · {row["instruction_count"]} IR instructions · '
                     f'{row["control_edge_count"]} control edges. Final annotations unavailable.</p>']
        body.append("<p>Automatic DOE results are unavailable.</p>")
    write_json(directory / "results.json", report)
    markup = ['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
              "<title>google-search · SkillFlow audit</title><style>", STYLE, "</style></head><body><header>"]
    if fixture_label:
        markup += ['<p class="fixture">', escape(fixture_label), "</p>"]
    markup += ["<h1>google-search</h1><p>", escape(run.name), "</p><p>Automatic audit · ", escape(result["status"]),
               "</p></header><nav>", *header, "</nav>", *body, "</body></html>"]
    (directory / "index.html").write_text("".join(markup), encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--fixture-label", default="")
    args = parser.parse_args()
    saved = publish(args.run.resolve(strict=True), args.out.resolve(), args.fixture_label)
    print(json.dumps({"run": saved["run"], "status": saved["status"], "graph": saved["graph"],
                      "analysis": saved["analysis"], "output": str(args.out)}, ensure_ascii=False))
