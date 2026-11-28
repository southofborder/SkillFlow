"""Render the selected Google Search execution slice as editable vectors and a slide image."""

import json
from pathlib import Path

from matplotlib import rcParams
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch, Polygon


ROOT = Path(__file__).resolve().parent
rcParams.update({"svg.fonttype": "none", "pdf.fonttype": 42, "text.usetex": False})
W, H = 1600, 900
fig = Figure(figsize=(16, 9), dpi=100, facecolor="#f6f8fc")
FigureCanvasAgg(fig)
ax = fig.add_axes((0, 0, 1, 1))
ax.set(xlim=(0, W), ylim=(H, 0))
ax.set_axis_off()

INK = "#152547"
MUTED = "#435777"
CONTROL = "#526482"
DATA = "#00796f"
DEMAND = "#6744a1"
BINDING = "#335e9c"
WARN = "#9a4b18"
LINE = "#d5dfef"


def caption(x, y, value, size=15, *, color=INK, weight="normal", align="left", mono=False):
    return ax.text(x, y, value, fontsize=size, color=color, fontweight=weight,
                   ha=align, va="center", fontfamily="DejaVu Sans Mono" if mono else "DejaVu Sans",
                   linespacing=1.35, zorder=5)


def box(x, y, width, height, *, face="white", edge=LINE, radius=15, linewidth=1.1):
    ax.add_patch(FancyBboxPatch((x, y), width, height,
                 boxstyle=f"round,pad=0,rounding_size={radius}",
                 facecolor=face, edgecolor=edge, linewidth=linewidth, zorder=3))


def path(points, color, *, dashed=False, arrow=True, linewidth=2.2):
    xs, ys = zip(*points)
    ax.plot(xs, ys, color=color, linewidth=linewidth, linestyle=(0, (4, 3)) if dashed else "-",
            solid_capstyle="round", dash_capstyle="round", zorder=2)
    if arrow:
        x, y = points[-1]
        px, py = points[-2]
        length = ((x - px) ** 2 + (y - py) ** 2) ** 0.5
        vx, vy = (x - px) / length, (y - py) / length
        ax.add_patch(Polygon([(x, y), (x - vx * 13 - vy * 6, y - vy * 13 + vx * 6),
                             (x - vx * 13 + vy * 6, y - vy * 13 - vx * 6)],
                             closed=True, facecolor=color, edgecolor="none", zorder=4))


def node(x, y, width, height, details, *, accent=DATA, face="white"):
    box(x, y, width, height, face=face)
    caption(x + 21, y + 27, details["tag"], 11, color=accent, weight="bold")
    caption(x + 21, y + 59, details["title"], 20, weight="bold")
    for index, line in enumerate(details["lines"]):
        caption(x + 21, y + 91 + 25 * index, line, 13.2, color=MUTED)


def task(x, y, width, label, *, muted=False):
    face = "#eef2f6" if muted else "#e7effc"
    edge = "#d6e1f1" if muted else "#c9d9ee"
    box(x, y, width, 45, face=face, edge=edge, radius=9)
    caption(x + 13, y + 22, label, 11.4, color=MUTED if muted else BINDING, weight="bold")


facts = json.loads((ROOT / "figure-content.json").read_text(encoding="utf-8"))

caption(58, 58, "google-search", 36, weight="bold")
caption(60, 111, "Annotated CFG with Task Requirements", 21, color=MUTED)
caption(60, 158, facts["subtitle"], 13.5, color=MUTED)

for y, kind, color, dashed in [(64, "Control flow", CONTROL, False),
                                (96, "Forward data flow", DATA, False),
                                (128, "Backward demand", DEMAND, True),
                                (160, "Task binding", BINDING, True)]:
    path([(1212, y), (1272, y)], color, dashed=dashed)
    caption(1284, y, kind, 12.5, color=color)

# Data and demand cross the same pair of printed operation positions.
path([(393, 326), (554, 326)], DATA)
caption(474, 304, facts["forward_arrow"], 11.6, color=DATA, align="center")
if facts["backward_arrow"]:
    path([(554, 375), (393, 375)], DEMAND, dashed=True)
    caption(474, 399, facts["backward_arrow"], 11.6, color=DEMAND, align="center")
path([(992, 326), (1160, 326)], DATA)
caption(1076, 303, facts["response_arrow"], 11.5, color=DATA, align="center")

# Common control path branches below the response operation.
path([(1360, 425), (1360, 488)], CONTROL, arrow=False)
path([(1360, 488), (701, 488), (701, 560)], CONTROL)
path([(1360, 488), (1305, 488), (1305, 560)], CONTROL)
caption(682, 519, facts["success_edge"], 12.5, color=CONTROL, align="right")
caption(1421, 519, facts["error_edge"], 12.5, color=WARN, align="center")

node(58, 262, 335, 163, facts["source"])
node(554, 262, 438, 163, facts["request"])
node(1160, 262, 382, 163, facts["response"], accent=CONTROL)
node(480, 560, 443, 165, facts["success"], accent=CONTROL)
node(1036, 560, 506, 190, facts["error"], accent=WARN, face="#fff9f3")

task(58, 188, 335, facts["source_task"], muted=not facts["source_binds"])
task(554, 188, 438, facts["request_task"], muted=not facts["request_binds"])
if facts["source_binds"]:
    path([(226, 233), (226, 262)], BINDING, dashed=True, linewidth=1.6)
if facts["request_binds"]:
    path([(785, 233), (785, 262)], BINDING, dashed=True, linewidth=1.6)

box(58, 558, 355, 193, face="#eef1fa", edge="#d9e0f3")
caption(79, 588, "How to read the graph", 15.5, weight="bold")
for line_number, value in enumerate(facts["guide"]):
    caption(79, 627 + line_number * 28, value, 12.6, color=MUTED)

ax.plot([58, 1542], [797, 797], color=LINE, linewidth=1.1)
caption(59, 823, facts["status"], 13, color=INK, weight="bold")
caption(59, 858, facts["footnote"], 11.2, color=MUTED)

for suffix in ("svg", "png", "pdf"):
    fig.savefig(ROOT / f"google-search-annotated-cfg.{suffix}",
                format=suffix, dpi=160 if suffix == "png" else 100, facecolor=fig.get_facecolor())
