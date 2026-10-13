"""The e-reader text pages: Revision 5 reset on a 3:4 page at reading size, same rubrics, tables and marginalia."""
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

W, H = 1200, 1600
PAPER = "#ebe1c8"
INK, RED, SEPIA = Hd.INK, Hd.RED, Hd.SEPIA
TX0, TW = 118, 764          # text column
MX, MW = 906, 234           # margin column (centre 1023)
TOP_FIRST, TOP = 330, 132
BOTTOM = 1478
SLACK = 1.005               # Chromium with the local font files measures within 0.3% of the PIL estimate
PICA, PICA_SC, ENG, ENG_SC = "IM FELL DW Pica", "IM FELL DW Pica SC", "IM FELL English", "IM FELL English SC"
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII"]

SECS = json.load(open("/home/claude/grim/src/rev5_sections.json"))
BYTITLE = {s["title"]: s for s in SECS}


BODY = dict(size=28, lh=39.5, gap=15)


def body_box(id, x, y, w, runs, size=None, lh=None, gap=None):
    return dict(id=id, x=x, y=y, w=w, size=size or BODY["size"], lh=lh or BODY["lh"], font=PICA, sc_font=PICA_SC,
                color=INK, para_gap=BODY["gap"] if gap is None else gap, runs=runs)


def smart_runs(runs):
    """straight quotes -> typographic, carrying the previous character across runs"""
    out, prev = [], " "
    for t, st in runs:
        buf = []
        for ch in t:
            if ch == "'":
                ch = "\u2019"
            elif ch == '"':
                ch = "\u201c" if (prev.isspace() or prev in "([{\u2014\u2013") else "\u201d"
            buf.append(ch)
            prev = ch
        out.append((("".join(buf)), st))
    return out


def map_runs(runs):
    out = []
    for t, s in smart_runs(runs):
        if "b" in s:
            out.append((t, "sc red"))
        elif "i" in s:
            out.append((t, "i"))
        else:
            out.append((t, ""))
    return out


def plain(runs):
    return "".join(t for t, s in smart_runs(runs))


def items_of(sec):
    """section blocks -> flow items"""
    items = []
    prev = None
    for b in sec["blocks"]:
        t = b["t"]
        if t == "embed":
            items.append(dict(kind="figure", h=232))
            continue
        if t == "table":
            items.append(dict(kind="table", rows=b["rows"]))
        elif t == "h3":
            txt = plain(b["runs"])
            num, _, rest = txt.partition(" ")
            if len(num) == 2 and num[0] == "D" and num[1].isdigit():
                items.append(dict(kind="p", runs=[(num + " ", "sc red"), (rest, "i")], extra=20, key=txt))
            else:
                items.append(dict(kind="p", runs=[(txt, "sc red")], extra=20, key=txt))
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
            bx = dict(id=f"t{ri}_{ci}", x=xs[ci] + 10, y=y + 10, w=xs[ci + 1] - xs[ci] - 20,
                      size=19 if hdr else 21, lh=24 if hdr else 27, font=PICA_SC if hdr else PICA, sc_font=PICA_SC,
                      color=RED if hdr else INK, para_gap=0, runs=[(plain(c), "")] if hdr else map_runs(c))
            if ci == 0 and not hdr:
                bx["runs"] = [(plain(c), "i")]
            hs.append(box_height(bx) * SLACK)
            cells.append(bx)
        rh = max(hs) + 20
        boxes.extend(cells)
        y += rh
        rules.append(("orn" if hdr else "hair", [(x0, y), (x0 + w, y)]))
    for xi in xs[1:-1]:
        rules.append(("hair", [(xi, y0 + 4), (xi, y - 4)]))
    rules[-1] = ("orn", rules[-1][1])
    return boxes, rules, y - y0


# ------------------------------------------------------------ pagination

def paginate(sec, first_top=TOP_FIRST, colfracs=None, table_x=(70, 1060)):
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
            y = cur_y + h * SLACK + 24
            cur = []

    ti = 0
    for it in items:
        if it["kind"] == "figure":
            close_flow()
            if y + it["h"] > BOTTOM:
                pages.append(page)
                page = dict(segs=[], top=TOP)
                y = TOP
            page["segs"].append(dict(kind="figure", y=y, h=it["h"]))
            y += it["h"] + 10
            cur_y = y
            continue
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
            y = y + 6 + th + 34
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
            return box_height(bx) + BODY["gap"] + seg["items"][k].get("extra", 0)
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
    for _ in range(120):
        d.circle("fox_fill", rng.uniform(0, W), rng.uniform(0, H), rng.uniform(0.6, 3.2) ** 1.4)
    h.stroke([(60, 78), (1140, 78)], "orn")
    h.stroke([(60, 83), (1140, 83)], "hair")
    if first:
        band_x(h, (480, 292), (720, 292), 10, 12, "hair", "ink")
        asterisk(h, 468, 292, 6, 8, weight="hair")
        asterisk(h, 732, 292, 6, 8, weight="hair")
    asterisk(h, 600, 1512, 6.5, 8, weight="hair", color="sep")


def gloss_box(id, x, y, i):
    name, meaning = MARKS[i]
    return dict(id=id, x=x, y=y, w=MW, size=16.5, lh=20.5, font=PICA, sc_font=PICA_SC, color=SEPIA, align="center",
                para_gap=0, runs=[(ROMAN[i] + " · ", "sc red"), (name.lower(), "sc"), ("", "br"), (meaning, "i")])


def build_section(title, num, short, margin=None, extra_boxes=None, colfracs=None, seed=0, table_x=(70, 990),
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
        B = [dict(id="rh_l", x=60, y=40, w=480, size=17, lh=22, font=ENG_SC, ls=0.2, color=INK,
                  runs=[("Clavicula Matricis", "")]),
             dict(id="rh_r", x=520, y=40, w=620, size=17, lh=22, font=ENG_SC, ls=0.16, align="right", color=RED,
                  runs=[((f"§ {num} · " if num else "") + short, "")])]
        if pi == 0:
            if num:
                B.append(dict(id="secno", x=400, y=146, w=400, size=22, lh=26, font=ENG_SC, ls=0.3, align="center",
                              color=RED, runs=[(f"§ {num}", "")]))
            B.append(dict(id="sectitle", x=70, y=180, w=1060, size=46, lh=54, font=ENG, align="center", color=INK,
                          runs=[(label or (sec["title"].split(" ", 1)[1] if num else sec["title"]), "")]))
        for si, sg in enumerate(pg["segs"]):
            if sg["kind"] == "flow":
                B.append(body_box(f"flow{si}", TX0, round(sg["y"], 1), TW, flow_runs(sg["items"])))
            elif sg["kind"] == "figure":
                sig_mark(h, TX0 + TW / 2, sg["y"] + 160, 84, "ink", "core")   # the branch rises ~1.7 sizes above the centre
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

        def size(what):
            """(block height, distance to the next block)"""
            if isinstance(what, int):
                return 150, 176
            hh = box_height(what(MX - 4, 0))
            return hh, hh + 34

        ys = []
        for k, (y, what) in enumerate(wants):
            if ys:
                y = max(y, ys[-1] + size(wants[k - 1][1])[1])
            ys.append(y)
        for k in reversed(range(len(wants))):
            lim = BOTTOM - size(wants[k][1])[0]
            if k + 1 < len(wants):
                lim = min(lim, ys[k + 1] - size(wants[k][1])[1])
            ys[k] = min(ys[k], lim)
        top = TOP_FIRST if pi == 0 else TOP
        for k, (y0, what) in enumerate(wants):
            y = ys[k]
            if y < top:
                print("  margin item does not fit on", title, pi + 1, what if isinstance(what, int) else "hand")
                continue
            if isinstance(what, int):
                draw_mark(what, h, MX + MW / 2, y + 44, 96)
                B.append(gloss_box(f"gl_{what}_{k}", MX, y + 104, what))
            else:
                B.append(what(MX - 4, y))
        if extra_boxes:
            B.extend(extra_boxes(pi, pg))
        foot = f"{num} · {pi + 1}" if num else f"{short.lower()} · {pi + 1}"
        B.append(dict(id="folio", x=500, y=1530, w=200, size=16, lh=20, font=ENG_SC, ls=0.2, align="center",
                      color=SEPIA, runs=[(foot, "")]))
        out.append((d.svg(), B))
    return out
