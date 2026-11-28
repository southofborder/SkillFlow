"""Render the meeting figure from the verified selected-basis readmission files."""
from collections import Counter
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import ImageFont


OUT = Path(__file__).resolve().parent / "revalidated-results"
NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
INK, MUTED = "#132b3b", "#415767"
TEAL, PURPLE, GOLD = "#0c695d", "#654397", "#92511a"


def load(name, expected=None):
    content = (OUT / name).read_bytes()
    if expected is not None and sha256(content).hexdigest() != expected:
        raise ValueError("Meeting figure input digest differs for " + name)
    return json.loads(content)


def evidence():
    receipt = load("receipt.json")
    assert receipt["basis"] == "terminal_selection" and receipt["readmission"]["instruction_id"] == "ir_045"
    names = ("boundary-comparisons", "forward-records", "forward-data", "forward", "backward", "doe")
    boundaries, records, versions, forward, backward, doe = [
        load(n + ".json", receipt["artifact_sha256"][n + ".json"]) for n in names]
    data = {d["id"]: d for d in versions}
    endpoint = "https://www.googleapis.com/customsearch/v1"
    sources = {"ir_049": ("ir_034", "runtime_context:current process environment binding GOOGLE_API_KEY"),
               "ir_076": ("ir_067", "runtime_context:google_search.api_key")}
    origin_ids = {}
    for ir, (entry, location) in sources.items():
        site = boundaries[ir]
        origin, = site["credential_origins"]
        key = origin["data_id"]
        assert data[key]["origin"]["acquired_from"] == location and site["acquisition_instruction"] == entry
        assert site["precise_R9_demands_at_credential_acquisition"] and not site["precise_R9_params_key_demands_at_GET"]
        goals = [g for g in backward["goals"] if g["requirement_id"] == "R9" and g["target"].get("instruction_id") == ir]
        assert any(g["preserve"] == "action" for g in goals)
        assert any(g["preserve"] == "value" and g["path"] == [] and g["target"]["slot"] == {"kind":"input","index":0} for g in goals)
        outcomes = {event["case"]["phase"]: event["case"]["disposition"] for event in records[ir]["events"] if event.get("case")}
        assert outcomes == {"normal":"return","pre_request_error":"throw","post_request_error":"throw"}
        sent = {event["case"]["phase"] for event in records[ir]["events"] if event.get("case")
                for op in event.get("atomic_ops", []) if op["op"] == "deliver" and {"kind":"remote","name":endpoint} in op["endpoints"]}
        assert sent == {"normal","post_request_error"}
        origin_ids[ir] = key
    assert len(set(origin_ids.values())) == 2
    assert not boundaries["ir_063"]["payload_operations"] and not boundaries["ir_063"]["comparisons"]
    assert "ir_063" not in records and forward["coverage"]["ir_063"] == "unmodeled" and forward["coverage"]["ir_065"] == "blocked"
    assert {"ir_063","ir_065"} <= {g["target"].get("instruction_id") for g in backward["goals"] if g["requirement_id"] == "R12"}
    assert (forward["status"], backward["status"], doe["status"]) == ("incomplete", "partial", "partial")
    return {"scope": receipt["description"], "basis": receipt["basis"], "selection": receipt["selection"],
            "inputs": {n + ".json": receipt["artifact_sha256"][n + ".json"] for n in names},
            "sources": origin_ids, "forward_coverage": dict(Counter(forward["coverage"].values())),
            "receiver": endpoint, "readmitted_row_sha256": receipt["readmission"]["row_sha256"]}


def element(parent, tag, **attrs):
    return ET.SubElement(parent, "{" + NS + "}" + tag, {k.replace("_", "-"): str(v) for k,v in attrs.items()})


def generate():
    proof = evidence()
    root = ET.Element("{" + NS + "}svg", {"width":"1600", "height":"900", "viewBox":"0 0 1600 900",
        "role":"img", "aria-labelledby":"figure-title figure-description", "font-family":"Segoe UI, Arial, sans-serif"})
    element(root, "title", id="figure-title").text = "Which API key reaches Google Search?"
    element(root, "desc", id="figure-description").text = ("Separate CLI and public HTTP requests transmit their own API key. "
        "R9 demands the operation and whole request. The CLI exception handler has no computed error output at ir_063.")
    element(root, "metadata", id="evidence").text = json.dumps(proof, ensure_ascii=False)
    defs = element(root, "defs")
    for key, color in (("forward", TEAL), ("backward", PURPLE), ("exception", GOLD)):
        marker = element(defs, "marker", id=key + "-arrow", markerWidth=9, markerHeight=9,
                         refX=8, refY=4, orient="auto", markerUnits="userSpaceOnUse")
        element(marker, "path", d="M0 0 L9 4 L0 8 Z", fill=color)
    element(root, "rect", width=1600, height=900, fill="#fbfcfa")
    checked = []
    def text(parent, x, y, value, *, size=20, color=INK, bold=False, within=(0,0,1600,900)):
        font = ImageFont.truetype(str(Path("C:/Windows/Fonts") / ("segoeuib.ttf" if bold else "segoeui.ttf")), size)
        left, top, right, bottom = font.getbbox(value, anchor="ls")
        bounds = x+left, y+top, x+right, y+bottom
        if bounds[0] < within[0] or bounds[1] < within[1] or bounds[2] > within[2] or bounds[3] > within[3]:
            raise ValueError(f"Text exceeds its figure region: {value!r} {bounds} outside {within}")
        checked.append(bounds)
        e = element(parent,"text",x=x,y=y,fill=color,font_size=size,font_weight=700 if bold else 400)
        e.text = value
        return e
    def arrow(d, key, dashed=False):
        a = element(root,"path",d=d,fill="none",stroke={"forward":TEAL,"backward":PURPLE,"exception":GOLD}[key],
            stroke_width=3.4,stroke_linejoin="round",stroke_linecap="round",marker_end="url(#"+key+"-arrow)")
        if dashed:
            a.set("stroke-dasharray","9 7")
    def box(x,y,w,h,ir,lines,*,fill="#ffffff",stroke="#c3d6d1",tone=TEAL):
        group = element(root,"a",href="annotations.html#ir-" + ir, aria_label="Open evidence for " + ir)
        element(group,"rect",x=x,y=y,width=w,height=h,rx=13,fill=fill,stroke=stroke,stroke_width=2)
        bound = (x+14,y+5,x+w-12,y+h-5)
        for dy, content, size, color, bold in lines:
            text(group,x+18,y+dy,content,size=size,color=color or tone,bold=bold,within=bound)
        return group
    def card(x,y,w,ir,tag,main,detail):
        return box(x,y,w,112,ir,[(26,tag,17,None,True),(65,main,24,INK,True),(94,detail,18,MUTED,False)])
    text(root,52,66,"Which API key reaches Google Search?",size=47,bold=True)
    text(root,54,106,"Offline revalidation of the final 84-instruction graph  ·  CLI argument transfer readmitted at ir_045",size=23,color=MUTED)
    arrow("M55 151 H111","forward")
    text(root,124,158,"Forward data",size=19,bold=True,color=TEAL)
    arrow("M458 151 H401","backward",True)
    text(root,475,158,"Backward Task demand",size=19,bold=True,color=PURPLE)
    arrow("M828 151 H885","exception")
    text(root,900,158,"CLI exception control",size=19,bold=True,color=GOLD)
    element(root,"path",d="M52 176 H1548",stroke="#cad4d5",stroke_width=1.5)
    px, mx, sx = 52, 413, 766
    for y in (197,385):
        arrow(f"M360 {y+55} H408","forward")
        arrow(f"M716 {y+55} H761","forward")
        arrow(f"M1040 {y+55} H1112","forward")
        arrow(f"M838 {y+114} V{y+138} H200 V{y+115}","backward",True)
    card(px,197,308,"ir_067","ir_067  ·  public entry","google_search.api_key","Data ID " + proof["sources"]["ir_076"][:13] + "…")
    card(mx,197,303,"ir_074","ir_074  ·  request assembly","Build public request","Own arguments → params")
    card(sx,197,274,"ir_076","ir_076  ·  HTTP call","Public GET","params.key carries this key")
    card(px,385,308,"ir_034","ir_034  ·  CLI entry","GOOGLE_API_KEY","Data ID " + proof["sources"]["ir_049"][:13] + "…")
    card(mx,385,303,"ir_045","ir_045 → ir_047  ·  CLI","Bind CLI arguments","Readmitted transfer → params")
    card(sx,385,274,"ir_049","ir_049  ·  HTTP call","CLI GET","params.key carries this key")
    text(root,231,362,"R9 reaches the public argument",size=18,color=PURPLE,bold=True)
    text(root,231,550,"R9 reaches the environment read",size=18,color=PURPLE,bold=True)
    receiver = element(root,"g")
    element(receiver,"rect",x=1118,y=197,width=430,height=300,rx=18,fill="#e8f4ee",stroke="#87b7a2",stroke_width=2)
    rb=(1135,202,1533,492)
    for y,val,size,col,bold in ((233,"Remote receiver",20,TEAL,True),(279,"Google Custom Search",30,INK,True),
        (320,"https://www.googleapis.com",23,INK,False),(349,"/customsearch/v1",23,INK,False),
        (393,"Query fields: q, key, cx, num",21,INK,True),(435,"Both GETs record delivery on normal",20,MUTED,False),
        (463,"return and post-send failure.",20,MUTED,False)):
        text(receiver,1140,y,val,size=size,color=col,bold=bold,within=rb)
    arrow("M964 500 V581 H607 V613","exception")
    text(root,998,559,"Throw before or after delivery",size=18,color=GOLD,bold=True)
    text(root,54,651,"CLI exception path",size=27,bold=True)
    text(root,54,687,"R12 calls for printing the error",size=20,color=MUTED)
    text(root,54,716,"and exiting with status 1.",size=20,color=MUTED)
    box(413,618,323,118,"ir_060",[(28,"ir_060 → ir_061  ·  processed",17,None,True),
        (67,"Match the exception",24,INK,True),(98,"except Exception",19,MUTED,False)],fill="#fffaf1",stroke="#d8b083",tone=GOLD)
    arrow("M739 678 H793","exception",True)
    box(798,618,388,118,"ir_063",[(28,"ir_063  ·  unmodeled",17,None,True),
        (67,"Format and print the error",24,INK,True),(98,"0 recorded stdout deliveries",20,GOLD,True)],
        fill="#fff3e3",stroke="#cc9a64",tone=GOLD)
    arrow("M1189 678 H1246","exception",True)
    box(1251,618,297,118,"ir_065",[(28,"ir_065  ·  blocked",17,None,True),
        (67,"Exit with status 1",23,INK,True),(98,"Source continuation",19,MUTED,False)],
        fill="#faf6ef",stroke="#d8c6aa",tone=GOLD)
    element(root,"rect",x=52,y=772,width=1496,height=99,rx=14,fill="#f0edf7")
    text(root,75,811,"R9 binds each GET action and its whole request.",size=24,color=PURPLE,bold=True)
    text(root,75,848,"Neither GET has a field-specific R9 demand for params.key.",size=21,color=INK)
    text(root,1020,812,"Forward incomplete",size=20,color=MUTED,bold=True,within=(1000,775,1530,854))
    text(root,1020,845,"Backward partial  ·  DOE partial",size=20,color=MUTED,within=(1000,775,1530,859))
    class Anchors(HTMLParser):
        def __init__(self):
            super().__init__()
            self.ids=set()
        def handle_starttag(self, tag, attrs):
            identifier=dict(attrs).get("id")
            if identifier:
                self.ids.add(identifier)
    anchors=Anchors()
    anchors.feed((OUT/"annotations.html").read_text(encoding="utf-8"))
    links=[a.get("href") for a in root.iter("{"+NS+"}a")]
    assert len(links)==9 and all(link.partition("#")[2] in anchors.ids for link in links)
    ET.ElementTree(root).write(OUT/"meeting-example.svg",encoding="utf-8",xml_declaration=True)
    return len(checked), len(links)


if __name__ == "__main__":
    print("Verified SVG labels and instruction links", *generate())
