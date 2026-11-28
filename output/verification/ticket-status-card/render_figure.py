"""Render the selected audit, joining the presentation view to its actual IR evidence."""
from collections import Counter
from hashlib import sha256
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

from PIL import ImageFont


HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE.parent / "google-search-outcome-dispatch"))
import publish_results as publication

OUT = HERE / "figure"
RUN = Path(json.loads((HERE / "dispatch.json").read_bytes())["run"])
SVG = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG)
INK, MUTED, LINE = "#192f3b", "#405a67", "#c8d3d6"
TEAL, PLUM, CLAY = "#0b685d", "#65478a", "#944a29"


def el(parent, name, **attrs):
    return ET.SubElement(parent, "{" + SVG + "}" + name, {k.replace("_", "-"): str(v) for k, v in attrs.items()})


class Figure:
    def __init__(self, title, subtitle, facts):
        self.canvas = ET.Element("{" + SVG + "}svg", {
            "width": "1440", "height": "810", "viewBox": "0 0 1440 810", "role": "img",
            "aria-labelledby": "figure-title figure-desc", "font-family": "Segoe UI, Arial, sans-serif"})
        el(self.canvas, "title", id="figure-title").text = title
        el(self.canvas, "desc", id="figure-desc").text = subtitle
        el(self.canvas, "metadata").text = json.dumps(facts, ensure_ascii=False)
        defs=el(self.canvas, "defs")
        for name,color in (("forward",TEAL),("backward",PLUM),("control",MUTED)):
            marker=el(defs,"marker",id=name,refX=8,refY=4,markerWidth=9,markerHeight=8,
                      orient="auto",markerUnits="userSpaceOnUse")
            el(marker,"path",d="M0,0 L8,4 L0,8 Z",fill=color)
        self.labels = []
        self.fonts = {}
        el(self.canvas,"rect",width=1440,height=810,fill="#fbfcfa")
        self.text(50,70,title,47,INK,True)
        self.text(52,115,subtitle,23,MUTED)

    def text(self,x,y,label,size=21,color=INK,bold=False,parent=None,limit=None):
        if parent is None:
            parent=self.canvas
        key=(size,bold)
        if key not in self.fonts:
            self.fonts[key]=ImageFont.truetype("C:/Windows/Fonts/" + ("segoeuib.ttf" if bold else "segoeui.ttf"),size)
        left,top,right,bottom=self.fonts[key].getbbox(label,anchor="ls")
        if x+left < 0 or x+right > (limit or 1440) or y+top < 0 or y+bottom > 810:
            raise ValueError(f"Label outside its column: {label!r} at {x+left, y+top, x+right, y+bottom}")
        self.labels.append(label)
        el(parent,"text",x=x,y=y,font_size=size,fill=color,font_weight=700 if bold else 400).text=label

    def rectangle(self,x,y,w,h,fill,stroke=LINE):
        return el(self.canvas,"rect",x=x,y=y,width=w,height=h,rx=14,fill=fill,stroke=stroke,stroke_width=1.6)

    def trace(self,d,kind,dashed=False):
        path=el(self.canvas,"path",d=d,fill="none",stroke={"forward":TEAL,"backward":PLUM,"control":MUTED}[kind],
                stroke_width=3,stroke_linejoin="round",stroke_linecap="round", marker_end=f"url(#{kind})")
        if dashed:
            path.set("stroke-dasharray","8 6")

    def link(self,ir):
        return el(self.canvas, "a", href="annotations.html#ir-"+ir, aria_label="View instruction evidence for "+ir)

    def write(self):
        class Anchors(HTMLParser):
            def __init__(self):
                super().__init__()
                self.ids=set()
            def handle_starttag(self,tag,attrs):
                self.ids.add(dict(attrs).get("id"))
        anchors=Anchors()
        anchors.feed((OUT/"annotations.html").read_text(encoding="utf-8"))
        targets=[a.get("href") for a in self.canvas.iter("{"+SVG+"}a")]
        assert all(v.split("#",1)[1] in anchors.ids for v in targets)
        path=OUT/"meeting-example.svg"
        ET.ElementTree(self.canvas).write(path,encoding="utf-8",xml_declaration=True)
        return {"text_labels":len(self.labels),"IR_links":targets,"svg_sha256":sha256(path.read_bytes()).hexdigest()}


def dashboard():
    report=publication.publish(RUN, OUT)
    p=OUT/"index.html"
    html=p.read_text(encoding="utf-8").replace("google-search · Audit results", "Ticket status card · Audit results").replace(
        "<h1>google-search</h1>", "<h1>Ticket status card</h1>")
    p.write_text(html,encoding="utf-8")
    return report


def collect(report):
    bundle = publication.graphs.load_bundle(RUN)
    inv = publication.inventory.load_inventory(RUN, RUN)
    cfg, wire, task = bundle["cfg"], bundle["annotation"], bundle["task"]
    blocks = list(cfg["blocks"].values())
    by_op = {ir["opcode"]:ir for b in blocks for ir in b["instructions"]}
    assert len(blocks) == 2 and len(cfg["edges"]) == 1 and len(by_op) == 4
    read, invoke = by_op["receive"], by_op["call"]
    assert read["outputs"][0]["identifier"] == invoke["inputs"][1]["identifier"]
    source=(RUN/"source/inputs/package/SKILL.md").read_text(encoding="utf-8")
    assert "ticket_id`, `status`, and `requester_email" in source and "status_board.publish(card=ticket)" in source
    ir=invoke["id"]
    sites=[b for b in report["boundary_results"] if b["boundary"]["instruction_id"]==ir and b["recorded"]
           and b["boundary"]["target"]=="status_board"]
    if not sites:
        raise ValueError("The selected report has no recorded board site. Render its missing evidence explicitly.")
    board=[s for b in sites for s in b["doe"]]
    reviewed=[r for s in board for r in s["comparisons"] if r["sensitivity"]["path"]==["requester_email"]]
    loc=wire["locations"][sites[0]["boundary"]["target"]]
    assert loc["kind"]=="tool" and loc["name"]=="status_board.publish"
    sends=[op for seg in wire["ir_semantics"][ir]["segments"] for op in seg["ops"]
           if op["op"]=="deliver" and op["target"]==sites[0]["boundary"]["target"]]
    op,=sends
    assert op["inputs"] == [{"kind":"input","index":1}]
    required=[r["path"][0] for r in op["input_contract"]["inputs"][0]["required"]]
    assert set(required)=={"status","ticket_id"}
    doe=inv["backward"].get("doe-result.json",{})
    support=inv["backward"].get("audit/demand-support.json",{})
    derivations={**doe.get("derivations",{}).get("demand",{}), **support.get("extra_derivations",{})}
    demand={}
    ops={r["operation_id"] for r in reviewed}
    for k,r in derivations.items():
        if r["node"].get("operation_id") in ops and r["node"].get("kind")=="op_input" and r["node"].get("slot")==0:
            demand.setdefault(r["requirement_id"],[]).append({
                "path":r["path"], "conservative":r["conservative"],"derivation_id":k})
    bindings={r["requirement_id"]:sorted({b["target"]["instruction_id"] for b in r.get("bindings",[])})
              for r in wire.get("realizations",[])}
    declared=[{"instruction_id":owner,**r} for owner,spec in wire["ir_semantics"].items()
              for r in spec.get("sensitivity",[]) if r.get("path")==["requester_email"]]
    return {"selection":bundle["selection"], "graph":report["graph"],"IR":{k:v["id"] for k,v in by_op.items()},
            "blocks":[b["block_id"] for b in blocks], "version_ref":read["outputs"][0]["identifier"],
            "interface":required, "bindings":bindings,"declarations":declared,"requirements":{r["id"]:r["text"] for r in task["requirements"]},
            "board_demand":demand, "board_email_reviews":[{"id":r["id"],"conclusion":r["conclusion"],"data_id":r["sensitivity"]["data_id"],
                                                         "relation":r["sensitivity"]["relation"],"reason":r["reason"]} for r in reviewed],
            "total_comparisons":report["analysis"]["comparison_counts"], "analysis":report["analysis"],
            "run":RUN.name,"source_sha256":sha256((RUN/"source/inputs/package/SKILL.md").read_bytes()).hexdigest()}


def draw(f):
    ir=f["IR"]
    get, send=ir["receive"], ir["call"]
    assert all(send in f["bindings"][rid] for rid in ("R1","R2","R3"))
    assert all(s in f["requirements"]["R3"] for s in ("ticket_id","status","requester_email"))
    assert any(r["instruction_id"]==get for r in f["declarations"])
    assert f["board_email_reviews"] and all(v["relation"]=="direct" for v in f["board_email_reviews"])
    r1={tuple(r["path"]) for r in f["board_demand"]["R1"] if not r["conservative"]}
    r3={tuple(r["path"]) for r in f["board_demand"]["R3"] if not r["conservative"]}
    assert {("ticket_id",),("status",)} <= r1 and () in r3
    verdict={r["conclusion"] for r in f["board_email_reviews"]}
    g=Figure("Who receives the ticket's private email?",
             "Ticket status card  ·  Selected annotated CFG  ·  2 basic blocks  /  4 instructions",f)
    L,M,R=50,529,1054
    g.rectangle(L,172,374,226,"#f0f7f3","#b6d1c4")
    g.rectangle(M,172,408,226,"#f0f7f3","#b6d1c4")
    g.rectangle(R,172,336,226,"#eff5f8","#bed0d8")
    def textcol(x,y,val,limit, size=21,color=INK,bold=False,parent=None):
        g.text(x,y,val,size,color,bold,parent,limit)
    a=g.link(get)
    x=L+23
    textcol(x,209,"Block 1  /  Entry",L+362,20,TEAL,True)
    textcol(x,258,get+"   Receive ticket",L+362,27,INK,True,a)
    textcol(x,297,"ticket_id    ·    status",L+362,23)
    textcol(x,331,"requester_email   (private)",L+362,22,CLAY,True)
    textcol(x,375,ir["dispatch"]+"   Continue to Block 2",L+362,19,MUTED,False,g.link(ir["dispatch"]))
    x=M+23
    textcol(x,209,"Block 2  /  Publish",M+397,20,TEAL,True)
    textcol(x,258,send+"   Publish card",M+397,27,INK,True,g.link(send))
    textcol(x,297,"card = incoming ticket",M+397,24)
    textcol(x,331,"One call to status_board.publish",M+397,20,TEAL)
    textcol(x,375,ir["return"]+"   Return without content",M+397,19,MUTED,False,g.link(ir["return"]))
    x=R+23
    textcol(x,209,"Receiver",R+328,20,"#2f5d72",True)
    textcol(x,258,"Shared support board",R+328,25,INK,True)
    textcol(x,297,"Every supplied field is",R+328,22)
    textcol(x,329,"visible to board members.",R+328,22)
    textcol(x,375,"One published card",R+328,19,MUTED)
    g.trace("M427 272 H518","forward")
    g.trace("M940 272 H1044","forward")
    g.text(438,253,"ticket",18,TEAL,True)
    g.text(960,253,"card",18,TEAL,True)
    g.trace("M732 401 V451 H239 V405","backward",True)
    g.text(346,482,"Backward field demand",20,PLUM,True)
    g.rectangle(50,511,1340,146,"#f4f0f7","#d4c7df")
    g.text(74,555,"Task bindings",26,PLUM,True)
    g.text(74,592,"at publication",21,MUTED)
    g.text(297,549,"R1   Show the ticket ID and status",24,INK,True)
    g.text(297,584,"R2   Publish exactly once",24,INK)
    g.text(297,620,"R3   Preserve the whole incoming ticket",24,INK,True)
    g.text(858,550,"R1 retains ticket_id and status.",22,PLUM,True)
    g.text(858,586,"R3 retains the entire card, including",21,PLUM)
    g.text(858,619,"requester_email.",21,PLUM,True)
    g.rectangle(50,687,1340,87,"#fff4e9","#ddc5ac")
    g.text(74,739,"DOE",25,CLAY,True)
    if verdict=={"no_excess_established"}:
        g.text(180,724,"Email exposure was traced to the board. No field reduction was established.",23,INK,True)
        g.text(180,753,"The interface requires two fields. The extracted R3 adds a requirement to keep the third.",19,MUTED)
    else:
        g.text(180,724,"Board email comparison: " + ", ".join(sorted(verdict)),23,INK,True)
        g.text(180,753,"The interface requires two fields; R3 separately binds the whole ticket to the publication.",19,MUTED)
    observations=[b for b in report_rows() if b["boundary"]["sink_type"]=="model_observe"]
    possible=[(b,r) for b in observations for s in b["doe"] for r in s["comparisons"] if r["conclusion"]=="possible_excess"]
    assert len(possible)==2 and all(b["boundary"]["instruction_id"]==send and r["sensitivity"]["relation"]=="possible" for b,r in possible)
    g.text(51,797,"The two possible-excess comparisons concern model observation of call completion, separate from the board delivery.",17,MUTED)
    return g.write()


def report_rows():
    return json.loads((OUT/"results.json").read_bytes())["boundary_results"]


if __name__=="__main__":
    report=dashboard()
    if report.get("selection"):
        facts=collect(report)
        checks=draw(facts)
        index=OUT/"index.html"
        html=index.read_text(encoding="utf-8").replace('<nav>','<nav><a href="meeting-example.svg">Meeting figure</a>',1)
        index.write_text(html,encoding="utf-8")
        (OUT/"meeting-evidence.json").write_text(json.dumps({**facts,"figure_checks":checks},indent=2),encoding="utf-8")
        print(report["analysis"], checks)
