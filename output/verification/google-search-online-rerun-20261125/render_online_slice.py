"""Draw a compact talk slide from the checked request slice."""

import json
from pathlib import Path

from matplotlib import rcParams
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parent
facts = json.loads((ROOT / "slide-facts.json").read_text(encoding="utf-8"))
rcParams["svg.fonttype"] = "none"
fig = Figure(figsize=(16, 9), dpi=100, facecolor="#f6f8fc")
FigureCanvasAgg(fig)
ax = fig.add_axes((0, 0, 1, 1))
ax.set(xlim=(0, 1600), ylim=(900, 0))
ax.set_axis_off()

INK, MUTED = "#152547", "#405574"
TEAL, PURPLE, BLUE = "#00796f", "#6744a1", "#335e9c"
GREY = "#687888"


def text(x, y, value, size=15, color=INK, bold=False, ha="left", va="center"):
    ax.text(x, y, value, fontsize=size, color=color, fontweight="bold" if bold else "normal",
            family="DejaVu Sans", ha=ha, va=va, zorder=5, linespacing=1.45)


def rounded(x, y, width, height, face="white", edge="#d6e0ee"):
    ax.add_patch(FancyBboxPatch((x,y), width,height, boxstyle="round,pad=0,rounding_size=14",
                                facecolor=face, edgecolor=edge, linewidth=1.2, zorder=2))


def arrow(a, b, color, dashed=False):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=19, color=color,
                                linewidth=2.4, linestyle=(0,(4,3)) if dashed else "-",
                                shrinkA=0, shrinkB=0, zorder=4))


def node(x, y, width, value):
    rounded(x, y, width, 185)
    text(x+23, y+30, value[0], 11.3, TEAL, True)
    text(x+23, y+68, value[1], 20, INK, True)
    for index, row in enumerate(value[2]):
        text(x+23, y+105+27*index, row, 13.4, MUTED)


text(58, 59, "google-search", 36, INK, True)
text(60, 115, "Annotated CFG with Task Requirements", 21, MUTED)
text(60, 170, facts["scope"], 13.2, MUTED)

for y, color, label, dashed in [(63, BLUE, "Task binding", True),
                                (99, TEAL, "Forward data flow", False),
                                (135, PURPLE, "Backward demand", True)]:
    arrow((1215,y),(1270,y),color,dashed)
    text(1285,y,label,13,color)

rounded(1118, 205, 423, 82, "#e9f0fc", "#d2dff4")
text(1139, 230, facts["task"][0], 11.5, BLUE, True)
text(1139, 259, facts["task"][1], 13.0, INK, True)
arrow((1329,287),(1329,332),BLUE,True)

node(58, 332, 345, facts["nodes"][0])
node(549, 332, 422, facts["nodes"][1])
node(1118, 332, 423, facts["nodes"][2])

for (left, right), forward, reverse in zip(((403,549),(971,1118)), facts["forward"], facts["reverse"], strict=True):
    mid = (left+right)/2
    arrow((left,392),(right,392),TEAL)
    text(mid,368,forward,10.2,TEAL,ha="center")
    arrow((right,469),(left,469),PURPLE if facts["reverse_established"] else GREY,True)
    text(mid,491,reverse,10.2,PURPLE if facts["reverse_established"] else GREY,ha="center")

rounded(58, 595, 1483, 157, "#edf2fa", "#d8e2f2")
for x, width, row in zip((81, 575, 1084),(490,500,403),facts["reading"],strict=True):
    text(x,628,row[0],13.8,INK,True)
    text(x,661,row[1],12.0,MUTED,va="top")

ax.plot([58,1542],[793,793],color="#d5dfef",linewidth=1.2)
text(58,823,facts["status"],13,INK,True)
text(58,859,facts["footnote"],11.2,MUTED)

for kind in ("svg","png"):
    fig.savefig(ROOT/f"google-search-online-annotated-cfg.{kind}",format=kind,
                dpi=160 if kind=="png" else 100,facecolor=fig.get_facecolor())
