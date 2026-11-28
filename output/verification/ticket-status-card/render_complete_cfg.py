"""Draw the four selected instructions and their task bindings as a single vector page."""
import json
import math
import argparse
from hashlib import sha256
from pathlib import Path
from xml.etree import ElementTree as ET

from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


HERE = Path(__file__).resolve().parent
OUT = HERE / "figure"
RUN = Path(json.loads((HERE / "dispatch.json").read_bytes())["run"])
STEM = "annotated-cfg-with-task-requirements"
W, H = 1760, 990
INK, MUTED, NAVY = "#152D3D", "#415A69", "#244D67"
GREEN, PURPLE, AMBER = "#116559", "#694782", "#974721"
WHITE, BORDER, RULE = "#FFFFFF", "#BCCBD2", "#D8E2E6"


def read(name):
    return json.loads((RUN / name).read_bytes())


def verify():
    selection = read("selection.json")
    for ref in selection.values():
        assert sha256((RUN / ref["path"]).read_bytes()).hexdigest() == ref["sha256"]
    cfg = read(selection["cfg"]["path"])["cfg"]
    wire = read("annotation/audit/wire-annotation.json")
    observed = read("propagation/records.json")
    assert [(b["block_name"], [(v["id"], v["opcode"]) for v in b["instructions"]])
            for b in cfg["blocks"].values()] == [
        ("entry", [("ir_001", "receive"), ("ir_002", "dispatch")]),
        ("publish", [("ir_003", "call"), ("ir_004", "return")])]
    assert cfg["edges"] == [{"source_block_id": "block_001", "target_block_id": "block_002", "condition_text": None}]
    recv = cfg["blocks"]["block_001"]["instructions"][0]
    call = cfg["blocks"]["block_002"]["instructions"][0]
    assert recv["outputs"][0]["identifier"] == call["inputs"][1]["identifier"] == "result_001"
    assert recv["inputs"][0]["identifier"] == "ticket" and call["inputs"][0]["identifier"] == "status_board.publish"
    assert not call["outputs"]
    assert {r["requirement_id"]: [b["target"] for b in r["bindings"]] for r in wire["realizations"]} == {
        "R1": [{"instruction_id": "ir_003", "side": "input", "index": 1}],
        "R2": [{"instruction_id": "ir_003", "path": []}],
        "R3": [{"instruction_id": "ir_001", "side": "output", "index": 0},
               {"instruction_id": "ir_003", "side": "input", "index": 1}]}
    for ir, expected in (("ir_001", ["read", "deliver"]), ("ir_003", ["deliver", "receive", "deliver"])):
        assert [op["op"] for ev in observed[ir]["events"] for op in ev["atomic_ops"]] == expected
    sites = read("doe/doe-result.json")["sinks"]
    totals = {(s["boundary"]["instruction_id"],s["boundary"]["event_index"]):
              [d["conclusion"] for d in s["data_reviews"]] for s in sites}
    assert totals == {("ir_001", 1): ["no_excess_established"]*2, ("ir_003", 0): ["no_excess_established"]*2,
                      ("ir_003", 2): ["possible_excess"]*2}
    return selection


class Page:
    def __init__(self, selection, *, stem=STEM, description=None):
        self.stem = stem
        self.root = ET.Element("svg", xmlns="http://www.w3.org/2000/svg", width=str(W), height=str(H),
                               viewBox=f"0 0 {W} {H}", role="img")
        ET.SubElement(self.root, "title").text = "Ticket status card — Annotated CFG with Task Requirements"
        ET.SubElement(self.root, "desc").text = description or (
            "Four IR instructions in two basic blocks, one unconditional control edge and one shared ticket value. "
            "R3 binds the unfiltered record at receipt and publication. Default model observations are shown separately.")
        ET.SubElement(self.root, "metadata").text = json.dumps(selection)
        for name, file in (("Normal","segoeui.ttf"),("Strong","segoeuib.ttf"),("Code","consola.ttf")):
            pdfmetrics.registerFont(TTFont(name, str(Path("C:/Windows/Fonts") / file)))
        self.pdf = canvas.Canvas(str(OUT / (stem+".pdf")), pagesize=(W*.6, H*.6), pageCompression=1)
        self.pdf.setTitle("Ticket status card — Annotated CFG with Task Requirements")
        self.pdf.scale(.6,.6)
        self.pdf.setLineJoin(1)
        self.pdf.setLineCap(1)

    def rect(self,x,y,w,h,fill,stroke=None,r=0):
        ET.SubElement(self.root,"rect",x=str(x),y=str(y),width=str(w),height=str(h),rx=str(r),
                      fill=fill,stroke=stroke or "none", **{"stroke-width":"1.5"})
        p=self.pdf
        p.setFillColor(HexColor(fill))
        p.setLineWidth(1.5)
        if stroke: p.setStrokeColor(HexColor(stroke))
        p.roundRect(x,H-y-h,w,h,r,stroke=int(bool(stroke)),fill=1)

    def text(self,x,y,label,size=22,color=INK,font="Normal",limit=W-50):
        width=pdfmetrics.stringWidth(label,font,size)
        assert x+width <= limit+1, (label,x+width,limit)
        self.pdf.setFillColor(HexColor(color))
        self.pdf.setFont(font,size)
        self.pdf.drawString(x,H-y,label)
        ET.SubElement(self.root,"text",x=str(x),y=str(y),fill=color,**{
            "font-family":"Consolas, monospace" if font=="Code" else "Segoe UI, Arial, sans-serif",
            "font-weight":"700" if font=="Strong" else "400","font-size":str(size)}).text=label
        return width

    def line(self,pts,color=RULE,weight=1.4,arrow=False,dashed=False):
        op={"fill":"none","stroke":color,"stroke-width":str(weight),"stroke-linecap":"round","stroke-linejoin":"round"}
        if dashed: op["stroke-dasharray"]="7 6"
        ET.SubElement(self.root,"polyline",points=" ".join(f"{x},{y}" for x,y in pts),**op)
        p=self.pdf
        p.setStrokeColor(HexColor(color)); p.setLineWidth(weight); p.setDash([7,6] if dashed else [])
        path=p.beginPath(); path.moveTo(pts[0][0],H-pts[0][1])
        for x,y in pts[1:]: path.lineTo(x,H-y)
        p.drawPath(path); p.setDash([])
        if arrow:
            (x1,y1),(x2,y2)=pts[-2:]
            angle=math.atan2(y2-y1,x2-x1); co,si=math.cos(angle),math.sin(angle)
            vertices=[(x2,y2),(x2-10*co+5*si,y2-10*si-5*co),(x2-10*co-5*si,y2-10*si+5*co)]
            ET.SubElement(self.root,"polygon",points=" ".join(f"{x:.2f},{y:.2f}" for x,y in vertices),fill=color)
            p.setFillColor(HexColor(color)); path=p.beginPath(); path.moveTo(x2,H-y2)
            for x,y in vertices[1:]: path.lineTo(x,H-y)
            path.close(); p.drawPath(path,stroke=0,fill=1)

    def badge(self,x,y,name):
        self.rect(x,y,42,25,"#F0EAF5",r=5)
        self.text(x+9,y+18,name,16,PURPLE,"Strong")

    def ir(self,x,y,name,opcode,ids=()):
        self.text(x,y,name,21,NAVY,"Code")
        self.text(x+113,y,opcode,26,INK,"Strong")
        for i,req in enumerate(ids): self.badge(883-46*len(ids)+46*i,y-21,req)

    def save(self):
        ET.ElementTree(self.root).write(OUT / (self.stem+".svg"),encoding="utf-8",xml_declaration=True)
        self.pdf.showPage(); self.pdf.save()


def draw(r12_doe=None):
    selection=verify()
    comparison = r12_doe is not None
    if comparison:
        doe=json.loads(r12_doe.read_bytes())
        board,=[s for s in doe["sinks"] if s["boundary"]["target"]=="status_board"]
        reviews=board["data_reviews"]
        assert set(board["related_requirements"])=={"R1","R2"}
        assert all(r["operation_id"]=="op_ir_003:e0:a0" for r in reviews)
        sensitivity=doe["derivations"]["sensitivity"]
        assert len(reviews)==2 and all(sensitivity[r["derivation_id"]]["path"]==["requester_email"]
                                       and sensitivity[r["derivation_id"]]["relation"]=="direct" for r in reviews)
        verdict,={r["conclusion"] for r in reviews}
        edit_supported=all(isinstance(r.get("reduction"),dict)
                           and r["reduction"]["kind"]=="exclude_field"
                           and r["reduction"]["path"]==["requester_email"] for r in reviews)
        assert (verdict=="excess_supported")==edit_supported
        page=Page({"basis":"Controlled task variant retaining R1 and R2", "parent_selection":selection,
                   "doe_sha256":sha256(r12_doe.read_bytes()).hexdigest()},
                  stem="ticket-status-card-r1-r2",description="Offline analysis of the same ticket workflow under two requirements. "
                  "The board receives the original ticket. Displaying ID and status and publishing once require only two fields.")
        page.pdf.setTitle("Ticket status card — R1 and R2 only")
    else:
        page=Page(selection)
    rect,text,line=page.rect,page.text,page.line
    rect(0,0,W,H,"#F7F9F9")
    text(56,73,"Ticket status card",50,INK,"Strong")
    text(58,109,"Annotated CFG  /  R1 and R2 only  /  Offline comparison" if comparison else
         "Annotated CFG with Task Requirements",26,MUTED)
    for x,color,caption,dashed in [(998,NAVY,"Control flow",False),(1224,GREEN,"Data flow",False),(1433,PURPLE,"Backward demand",True)]:
        line([(x,83),(x+40,83)],color,3,True,dashed)
        text(x+53,90,caption,20,color,"Strong")

    # Each block encloses its own terminator. Both data lanes connect the two nonterminal IR.
    rect(56,143,852,255,WHITE,BORDER,12)
    rect(75,157,120,30,"#E7EFF4",r=5)
    text(85,179,"block_001",19,NAVY,"Code")
    text(208,180,"Entry",26,NAVY,"Strong")
    line([(77,194),(885,194)])
    page.ir(82,224,"ir_001","receive",() if comparison else ("R3",))
    text(82,257,"in[0] = context.ticket",21,INK,"Code")
    text(440,257,"out[0] = result_001",21,INK,"Code")
    text(82,288,"e0   Read ticket into incoming_ticket and bind it to out[0].",22)
    text(82,318,"e1   Model observes the acquired ticket under the default contract.",22)
    text(82,345,"Sensitive at input and at read",19,AMBER,"Strong")
    text(371,345,"requester_email  /  private_contact_address",19,AMBER,"Code")
    line([(77,357),(885,357)])
    page.ir(82,385,"ir_002","dispatch")
    text(350,384,"Unconditional jump to block_002.",21,MUTED)

    line([(138,398),(138,461)],NAVY,3,True)
    text(162,439,"block_001 → block_002",21,NAVY,"Code")
    rect(56,465,852,319,WHITE,BORDER,12)
    rect(75,478,120,30,"#E7EFF4",r=5)
    text(85,500,"block_002",19,NAVY,"Code")
    text(208,501,"Publish",26,NAVY,"Strong")
    line([(77,515),(885,515)])
    page.ir(82,545,"ir_003","call",("R1","R2") if comparison else ("R1","R2","R3"))
    text(82,578,"in[0] = status_board.publish",20,INK,"Code")
    text(440,578,"in[1] = result_001",20,INK,"Code")
    text(82,609,"e0   Deliver card = result_001 to the shared board.",22)
    text(82,640,"e1   Receive publish_completion for this same invocation.",22)
    text(82,671,"e2   Model observes the opaque completion under the default contract.",22)
    text(82,710,"The tool declares no return content. The call defines no IR output.",21,MUTED)
    line([(77,734),(885,734)])
    page.ir(82,766,"ir_004","return")
    text(350,765,"End the Skill with no return value.",21,MUTED)

    line([(908,257),(945,257),(945,572),(910,572)],GREEN,3,True)
    line([(908,607),(985,607),(985,225),(910,225)],PURPLE,3,True,True)

    rect(1036,143,668,641,WHITE,BORDER,12)
    text(1060,186,"Task Requirements and IR bindings",29,INK,"Strong")
    line([(1060,206),(1680,206)])
    page.badge(1062,225,"R1")
    text(1119,246,"Show the ticket ID and status to board members.",23,INK,"Strong",1686)
    text(1062,288,"Bind",19,PURPLE,"Strong")
    text(1162,288,"ir_003.in[1]",21,INK,"Code")
    text(1062,323,"Seed",19,PURPLE,"Strong")
    text(1162,323,"deliver.arg[0].ticket_id",21,INK,"Code")
    text(1162,350,"deliver.arg[0].status",21,INK,"Code")
    line([(1060,376),(1680,376)])
    page.badge(1062,395,"R2")
    text(1119,416,"Publish the card exactly once.",23,INK,"Strong")
    text(1062,458,"Bind",19,PURPLE,"Strong")
    text(1162,458,"ir_003",21,INK,"Code")
    text(1062,493,"Seed",19,PURPLE,"Strong")
    text(1162,493,"Preserve the deliver action.",22)
    text(1062,528,"Limit",19,PURPLE,"Strong")
    text(1162,528,"At most one delivery attempt per task.",22)
    line([(1060,552),(1680,552)])
    if comparison:
        text(1062,592,"Fields at the publish operation",25,NAVY,"Strong")
        text(1062,637,"Interface requires",20,GREEN,"Strong")
        text(1265,637,"ticket_id, status",22,INK,"Code")
        text(1062,680,"Also delivered",20,AMBER,"Strong")
        text(1265,680,"requester_email",22,AMBER,"Code")
        text(1062,733,"The board shows every supplied field to its members.",22,MUTED)
    else:
        page.badge(1062,571,"R3")
        text(1119,592,"Use the entire incoming ticket as the card.",23,INK,"Strong",1686)
        text(1062,634,"Bind",19,PURPLE,"Strong")
        text(1162,634,"ir_001.out[0] and ir_003.in[1]",21,INK,"Code")
        text(1062,669,"Seed",19,PURPLE,"Strong")
        text(1162,669,"deliver.arg[0] at path []",21,INK,"Code")
        text(1162,701,"The empty path retains the whole value,",22)
        text(1162,730,"including requester_email.",22)

    rect(56,805,1648,138,"#EDF5F2","#B5CCC4",12)
    text(82,840,"At the board boundary",25,GREEN,"Strong")
    text(82,877,"Delivered",20,GREEN,"Strong")
    text(211,877,"ticket_id, status, requester_email",21,INK,"Code")
    text(82,914,"Required",20,GREEN,"Strong")
    text(211,914,"ticket_id, status" if comparison else
         "R1 and R2 retain the ID and status. R3 retains the entire card.",21,font="Code" if comparison else "Normal")
    line([(931,826),(931,924)],"#B5CCC4")
    text(962,842,"DOE on requester_email",24,GREEN,"Strong")
    text(962,878,verdict if comparison else "no_excess_established",24,AMBER if comparison else INK,"Code")
    if comparison:
        text(962,912,("Omit requester_email from the card at ir_003." if edit_supported else
             "The two requirements cover the ticket ID and status."),22)
    else:
        text(962,912,"The selected R3 preserves the email at publication.",22)
    text(57,974,"e0–e2 are local event indices within an instruction. At ir_003, IR input 1 supplies delivery argument 0.",19,MUTED)
    page.save()


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--r12-doe",type=Path)
    draw(parser.parse_args().r12_doe)
