"""Text leaves: the Revision 5 text set verbatim, with rubrics, tables and marginal marks whose meanings are stated."""
import json
import math
import random
import sys

sys.path.insert(0, "/home/claude/grim")
from core import Doc
from marks import *
import hands as Hd
from layout import box_height, layout_lines
from page2 import MARKS, draw_mark

W, H = 1000, 1600
PAPER = "#ebe1c8"
INK, RED, SEPIA = Hd.INK, Hd.RED, Hd.SEPIA
TX0, TW = 128, 624          # text column
MX, MW = 790, 160           # margin column (centre 870)
TOP_FIRST, TOP = 252, 104
BOTTOM = 1492
SLACK = 1.06
PICA, PICA_SC, ENG, ENG_SC = "IM FELL DW Pica", "IM FELL DW Pica SC", "IM FELL English", "IM FELL English SC"
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII"]

SECS = json.load(open("/home/claude/grim/src/rev5_sections.json"))
BYTITLE = {s["title"]: s for s in SECS}


BODY = dict(size=19, lh=27.4, gap=11)


def body_box(id, x, y, w, runs, size=None, lh=None, gap=None):
    return dict(id=id, x=x, y=y, w=w, size=size or BODY["size"], lh=lh or BODY["lh"], font=PICA, sc_font=PICA_SC,
                color=INK, para_gap=BODY["gap"] if gap is None else gap, runs=runs)


def map_runs(runs):
    out = []
    for t, s in runs:
        if "b" in s:
            out.append((t, "sc red"))
        elif "i" in s:
            out.append((t, "i"))
        else:
            out.append((t, ""))
    return out


def plain(runs):
    return "".join(t for t, s in runs)


def items_of(sec):
    """section blocks -> flow items"""
    items = []
    prev = None
    for b in sec["blocks"]:
        t = b["t"]
        if t == "embed":
            continue
        if t == "table":
            items.append(dict(kind="table", rows=b["rows"]))
        elif t == "h3":
            txt = plain(b["runs"])
            num, _, rest = txt.partition(" ")
            if len(num) == 2 and num[0] == "D" and num[1].isdigit():
                items.append(dict(kind="p", runs=[(num + " ", "sc red"), (rest, "i")], extra=14, key=txt))
            else:
                items.append(dict(kind="p", runs=[(txt, "sc red")], extra=14, key=txt))
        elif t == "p":
            items.append(dict(kind="p", runs=map_runs(b["runs"]), extra=0, key=plain(b["runs"])))
        elif t in ("li", "oli"):
            if t == "oli":
                mark = [(f"{b['n']}. ", "red")]
            elif b.get("depth", 0):
                mark = [("– ", "red")]
            else:
                mark = [("¶ ", "red")]
            items.append(dict(kind="p", runs=mark + map_runs(b["runs"]), extra=0, key=plain(b["runs"])))
        prev = t
    return items


def flow_runs(ps):
    runs = []
    for k, p in enumerate(ps):
        if k:
            runs.append(("", "br" + (f" +{p['extra']:g}" if p.get("extra") else "")))
        runs.extend(p["runs"])
    return runs


# ------------------------------------------------------------------ tables

def table_layout(rows, x0, w, y0, colfrac):
    """returns (boxes, rules, height). colfrac: list of fractions summing to 1"""
    xs = [x0]
    for f in colfrac:
        xs.append(xs[-1] + w * f)
    boxes, rules = [], []
    y = y0
    rules.append(("orn", [(x0, y), (x0 + w, y)]))
    for ri, r in enumerate(rows):
        hdr = ri == 0
        hs = []
        cells = []
        for ci, c in enumerate(r["cells"]):
            bx = dict(id=f"t{ri}_{ci}", x=xs[ci] + 8, y=y + 8, w=xs[ci + 1] - xs[ci] - 16,
                      size=13.5 if hdr else 15, lh=18 if hdr else 20, font=PICA_SC if hdr else PICA, sc_font=PICA_SC,
                      color=RED if hdr else INK, para_gap=0, runs=[(plain(c), "")] if hdr else map_runs(c))
            if ci == 0 and not hdr:
                bx["runs"] = [(plain(c), "i")]
            hs.append(box_height(bx) * SLACK)
            cells.append(bx)
        rh = max(hs) + 16
        boxes.extend(cells)
        y += rh
        rules.append(("orn" if hdr else "hair", [(x0, y), (x0 + w, y)]))
    for xi in xs[1:-1]:
        rules.append(("hair", [(xi, y0 + 4), (xi, y - 4)]))
    rules[-1] = ("orn", rules[-1][1])
    return boxes, rules, y - y0


# ------------------------------------------------------------ pagination

def paginate(sec, first_top=TOP_FIRST, colfracs=None, table_x=(100, 800)):
    items = items_of(sec)
    pages = []
    page = dict(segs=[], top=first_top)
    y = first_top
    cur = []
    cur_y = y

    def close_flow():
        nonlocal cur, y, cur_y
        if cur:
            bx = body_box("f", TX0, cur_y, TW, flow_runs(cur))
            h = box_height(bx)
            page["segs"].append(dict(kind="flow", items=cur, y=cur_y, h=h))
            y = cur_y + h * SLACK + 18
            cur = []

    ti = 0
    for it in items:
        if it["kind"] == "table":
            close_flow()
            fr = (colfracs or [])[ti] if colfracs and ti < len(colfracs) else None
            ti += 1
            tb, tr, th = table_layout(it["rows"], table_x[0], table_x[1], 0, fr)
            if y + th > BOTTOM:
                pages.append(page)
                page = dict(segs=[], top=TOP)
                y = TOP
            page["segs"].append(dict(kind="table", rows=it["rows"], y=y + 6, h=th, frac=fr))
            y = y + 6 + th + 26
            cur_y = y
            continue
        trial = cur + [it]
        if not cur:
            cur_y = y
        bx = body_box("f", TX0, cur_y, TW, flow_runs(trial))
        h = box_height(bx)
        if cur_y + h * SLACK > BOTTOM:
            carry = []
            while cur and plain(cur[-1]["runs"]).rstrip().endswith(":") and len(cur) > 1:
                carry.insert(0, cur.pop())
            close_flow()
            pages.append(page)
            page = dict(segs=[], top=TOP)
            y = TOP
            cur_y = y
            cur = [dict(c) for c in carry] + [it]
            cur[0] = dict(cur[0], extra=0)
        else:
            cur = trial
    close_flow()
    pages.append(page)
    return pages


def para_offset(seg, key):
    """estimated y offset of the paragraph whose key starts with `key` inside a flow segment"""
    for k, p in enumerate(seg["items"]):
        if p.get("key", "").startswith(key):
            if k == 0:
                return 0
            bx = body_box("f", 0, 0, TW, flow_runs(seg["items"][:k]))
            return box_height(bx) + 11 + seg["items"][k].get("extra", 0)
    return None


# ------------------------------------------------------------ drawing

def styles():
    st = {}
    for c, col in (("ink", INK), ("red", RED), ("sep", SEPIA), ("pm", "#d6c9aa")):
        for k, wdt in (("core", 2.6), ("orn", 1.45), ("hair", 0.85), ("cip", 1.3)):
            st[f"{c}_{k}"] = {"fill": "none", "stroke": col, "stroke-width": str(wdt), "stroke-linecap": "round",
                              "stroke-linejoin": "round"}
        st[f"{c}_fill"] = {"fill": col, "stroke": "none"}
    st["fox_fill"] = {"fill": "#b89a6a", "stroke": "none", "opacity": "0.15"}
    return st


def furniture(h, d, rng, first):
    for _ in range(110):
        d.circle("fox_fill", rng.uniform(0, W), rng.uniform(0, H), rng.uniform(0.6, 3.0) ** 1.4)
    h.stroke([(56, 58), (944, 58)], "orn")
    h.stroke([(56, 62), (944, 62)], "hair")
    if first:
        band_x(h, (400, 222), (600, 222), 8, 10, "hair", "ink")
        asterisk(h, 390, 222, 5, 8, weight="hair")
        asterisk(h, 610, 222, 5, 8, weight="hair")
    asterisk(h, 500, 1530, 5.5, 8, weight="hair", color="sep")


def gloss_box(id, x, y, i):
    name, meaning = MARKS[i]
    return dict(id=id, x=x, y=y, w=MW, size=12.5, lh=15.5, font=PICA, sc_font=PICA_SC, color=SEPIA, align="center",
                para_gap=0, runs=[(ROMAN[i] + " · ", "sc red"), (name.lower(), "sc"), ("", "br"), (meaning, "i")])


def build_section(title, num, short, margin=None, extra_boxes=None, colfracs=None, seed=0, table_x=(100, 800),
                  label=None):
    """returns list of (svg, boxes) per leaf. margin: list of (key, mark_index or ('hand', boxfn))"""
    sec = BYTITLE[title]
    pages = paginate(sec, colfracs=colfracs, table_x=table_x)
    out = []
    for pi, pg in enumerate(pages):
        rng = random.Random(seed * 100 + pi)
        st = styles()
        d = Doc(W, H, st, order=["fox_fill"] + [k for k in st if k != "fox_fill"])
        h = Hand(d, rng, "ink", amp=0.35)
        furniture(h, d, rng, pi == 0)
        B = [dict(id="rh_l", x=56, y=28, w=420, size=13, lh=17, font=ENG_SC, ls=0.22, color=INK,
                  runs=[("Clavicula Matricis", "")]),
             dict(id="rh_r", x=476, y=28, w=468, size=13, lh=17, font=ENG_SC, ls=0.22, align="right", color=RED,
                  runs=[((f"§ {num} · " if num else "") + short, "")])]
        if pi == 0:
            if num:
                B.append(dict(id="secno", x=300, y=112, w=400, size=16, lh=20, font=ENG_SC, ls=0.3, align="center",
                              color=RED, runs=[(f"§ {num}", "")]))
            B.append(dict(id="sectitle", x=80, y=138, w=840, size=34, lh=40, font=ENG, align="center", color=INK,
                          runs=[(label or (sec["title"].split(" ", 1)[1] if num else sec["title"]), "")]))
        for si, sg in enumerate(pg["segs"]):
            if sg["kind"] == "flow":
                B.append(body_box(f"flow{si}", TX0, round(sg["y"], 1), TW, flow_runs(sg["items"])))
            else:
                tb, tr, th = table_layout(sg["rows"], table_x[0], table_x[1], sg["y"], sg["frac"])
                for b in tb:
                    b["id"] = f"s{si}_{b['id']}"
                B.extend(tb)
                for wt, pts in tr:
                    h.stroke(pts, wt, "ink", amp=0.05)
        # marginalia
        wants = []
        for key, what in (margin or []):
            for sg in pg["segs"]:
                if sg["kind"] != "flow":
                    continue
                off = para_offset(sg, key)
                if off is not None:
                    wants.append((sg["y"] + off + 8, what))
        wants.sort(key=lambda t: t[0])
        placed_y = []
        for y, what in wants:
            if placed_y and y < placed_y[-1] + (150 if isinstance(what, int) else 130):
                y = placed_y[-1] + (150 if isinstance(what, int) else 130)
            if y > BOTTOM - 120:
                continue
            placed_y.append(y)
            if True:
                if isinstance(what, int):
                    draw_mark(what, h, MX + MW / 2, y + 34, 74)
                    B.append(gloss_box(f"gl_{what}_{len(placed_y)}", MX, y + 80, what))
                else:
                    bx = what(MX - 4, y)
                    B.append(bx)
        if extra_boxes:
            B.extend(extra_boxes(pi, pg))
        foot = f"{num} · {pi + 1}" if num else f"{short.lower()} · {pi + 1}"
        B.append(dict(id="folio", x=420, y=1548, w=160, size=12, lh=16, font=ENG_SC, ls=0.2, align="center",
                      color=SEPIA, runs=[(foot, "")]))
        out.append((d.svg(), B))
    return out
