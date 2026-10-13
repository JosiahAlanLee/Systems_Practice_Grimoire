"""VIS MAIOR — a tract on another stock, bound in after the eighth table: the demon none will summon and none will
criticize. Four pages of one folded sheet."""
import math
import random
import sys

sys.path.insert(0, "/home/claude/grim")
from core import Doc, arc_pts, bezier, catmull, resample
from marks import *

W, H = 860, 1360
STOCK = "#e9e7de"
TONER = "#151515"
GUARD = "#ddd2b6"
TYPE, BLACK = "Special Elite", "UnifrakturMaguntia"
STATEMENT = "NEITHER PARTY SHALL BE LIABLE"

# a plain stroke alphabet on a unit cell (x right, y down), enough for the statement
def _bowl(x0, y0, y1, w):
    return [(x0, y0)] + [(x0 + w + (y1 - y0) / 2 * math.cos(math.radians(a)) * 0.9,
                          (y0 + y1) / 2 + (y1 - y0) / 2 * math.sin(math.radians(a))) for a in range(-90, 91, 15)] + [(x0, y1)]


LETTERS = {
    "N": [[(0, 1), (0, 0), (0.7, 1), (0.7, 0)]],
    "E": [[(0.7, 0), (0, 0), (0, 1), (0.7, 1)], [(0, 0.5), (0.55, 0.5)]],
    "I": [[(0.35, 0), (0.35, 1)]],
    "T": [[(0, 0), (0.7, 0)], [(0.35, 0), (0.35, 1)]],
    "H": [[(0, 0), (0, 1)], [(0.7, 0), (0.7, 1)], [(0, 0.5), (0.7, 0.5)]],
    "R": [[(0, 1), (0, 0)], _bowl(0, 0, 0.5, 0.3), [(0.3, 0.5), (0.7, 1)]],
    "P": [[(0, 1), (0, 0)], _bowl(0, 0, 0.5, 0.3)],
    "A": [[(0, 1), (0.35, 0), (0.7, 1)], [(0.15, 0.6), (0.55, 0.6)]],
    "Y": [[(0, 0), (0.35, 0.5), (0.7, 0)], [(0.35, 0.5), (0.35, 1)]],
    "S": [bezier((0.66, 0.1), (0.5, -0.05), (0.02, 0.0), (0.12, 0.3), 10) +
          bezier((0.12, 0.3), (0.2, 0.5), (0.7, 0.5), (0.62, 0.78), 10)[1:] +
          bezier((0.62, 0.78), (0.55, 1.05), (0.12, 1.02), (0.04, 0.86), 10)[1:]],
    "L": [[(0, 0), (0, 1), (0.7, 1)]],
    "B": [[(0, 1), (0, 0)], _bowl(0, 0, 0.48, 0.28), _bowl(0, 0.48, 1, 0.36)],
}


def reduced(statement=STATEMENT):
    seen, out = set(), []
    for ch in statement:
        if ch.isalpha() and ch not in seen:
            seen.add(ch)
            out.append(ch)
    return out


def strike_runs(statement=STATEMENT):
    """the statement with every repeated letter struck"""
    seen, runs = set(), []
    for ch in statement:
        if ch == " ":
            runs.append((" ", ""))
        elif ch in seen:
            runs.append((ch, "x"))
        else:
            seen.add(ch)
            runs.append((ch, ""))
    merged = []
    for t, s in runs:
        if merged and merged[-1][1] == s:
            merged[-1] = (merged[-1][0] + t, s)
        else:
            merged.append((t, s))
    return merged


def monogram(h, cx, cy, s, weight="orn", color="ink"):
    """the twelve remaining letters laid over one another on a single cell"""
    for k, ch in enumerate(reduced()):
        for stroke in LETTERS[ch]:
            h.stroke([(cx + (x - 0.35) * s, cy + (y - 0.5) * s) for x, y in stroke], weight, color, amp=0.6)


def sigil(h, cx, cy, s, weight="core", color="ink", ring=True):
    """the reduced figure: shared stem, bars, the diagonal, one bowl, a leg, a fork above, a hook below"""
    P = lambda x, y: (cx + (x - 0.35) * s, cy + (y - 0.5) * s)
    h.stroke([P(0.35, -0.08), P(0.35, 1.0)], weight, color)                     # the shared stem
    h.stroke([P(0.02, 0.0), P(0.35, 0.0)], weight, color)                       # top bar, cut short
    h.stroke([P(0.05, 0.08), P(0.66, 0.94)], weight, color)                     # the diagonal
    h.stroke([P(0.35, 0.0)] + [P(0.35 + 0.3 * math.cos(math.radians(a)) + 0.0, 0.25 + 0.25 * math.sin(math.radians(a)))
                                 for a in range(-90, 91, 12)] + [P(0.35, 0.5)], weight, color)   # one bowl
    h.stroke([P(0.42, 0.5), P(0.74, 1.0)], weight, color)                       # the leg
    h.stroke([P(0.14, -0.3), P(0.35, -0.08), P(0.56, -0.3)], weight, color)     # the fork above
    h.stroke([P(0.35, 1.0), P(0.66, 1.0)], weight, color)                       # the foot
    h.stroke(bezier(P(0.35, 0.72), P(0.12, 0.66), P(0.0, 0.86), P(0.14, 0.98), 12), weight, color)  # the hook
    for p in (P(0.14, -0.3), P(0.56, -0.3), P(0.74, 1.0), P(0.02, 0.0), P(0.14, 0.98)):
        h.dot(p[0], p[1], s * 0.022, color)
    if ring:
        h.stroke(arc_pts(cx, cy + s * 0.12, s * 0.78, 0, 360, 160), "orn", color)


def styles():
    st = {}
    for c, col in (("ink", TONER), ("wh", "#efece4"), ("gd", "#8c7f62")):
        for k, wdt in (("core", 4.2), ("orn", 2.4), ("hair", 1.2), ("cip", 1.6)):
            st[f"{c}_{k}"] = {"fill": "none", "stroke": col, "stroke-width": str(wdt), "stroke-linecap": "round",
                              "stroke-linejoin": "round"}
        st[f"{c}_fill"] = {"fill": col, "stroke": "none"}
    for k, op in (("s1", 0.85), ("s2", 0.5), ("s3", 0.25)):
        st[f"tn_{k}"] = {"fill": TONER, "stroke": "none", "opacity": str(op)}
    for i in range(10):
        st[f"sh{i}_fill"] = {"fill": "#2a2a26", "stroke": "none", "opacity": f"{0.11 - i * 0.011:.3f}"}
    st["guard_fill"] = {"fill": GUARD, "stroke": "none"}
    st["guardsh_fill"] = {"fill": "#6d5f4b", "stroke": "none", "opacity": "0.18"}
    st["hole_fill"] = {"fill": "#4b4335", "stroke": "none", "opacity": "0.8"}
    st["thread_orn"] = {"fill": "none", "stroke": "#cfc6ae", "stroke-width": "2", "stroke-linecap": "round"}
    return st


def sheet(seed, gutter):
    """stock, copier shadow at the outer edge, toner flecks, the guard it is hinged on"""
    rng = random.Random(seed)
    st = styles()
    order = [f"sh{i}_fill" for i in range(10)] + ["tn_s3", "tn_s2", "tn_s1"] + \
            [k for k in st if k.startswith(("ink_", "wh_", "gd_"))] + ["guardsh_fill", "guard_fill", "hole_fill", "thread_orn"]
    d = Doc(W, H, st, order=order)
    outer = W if gutter == "left" else 0
    for i in range(10):
        wdt = 6 + i * 5
        x0 = outer - wdt if gutter == "left" else 0
        d.poly(f"sh{i}_fill", [(x0, 0), (x0 + wdt, 0), (x0 + wdt, H), (x0, H)], closed=True)
    for _ in range(520):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        d.circle(rng.choice(["tn_s3", "tn_s3", "tn_s2", "tn_s1"]), x, y, rng.uniform(0.35, 1.3))
    for _ in range(9):            # a few clustered drop-outs from a dirty platen
        cx, cy = rng.uniform(30, W - 30), rng.uniform(30, H - 30)
        for _ in range(rng.randint(6, 18)):
            d.circle("tn_s2", cx + rng.gauss(0, 6), cy + rng.gauss(0, 6), rng.uniform(0.4, 1.4))
    gx = 0 if gutter == "left" else W - 24
    d.poly("guardsh_fill", [(gx + (24 if gutter == "left" else -5), 0), (gx + (29 if gutter == "left" else 0), 0),
                            (gx + (29 if gutter == "left" else 0), H), (gx + (24 if gutter == "left" else -5), H)], closed=True)
    d.poly("guard_fill", [(gx, 0), (gx + 24, 0), (gx + 24, H), (gx, H)], closed=True)
    hx = gx + 12
    holes = [140 + k * 180 for k in range(7)]
    for y in holes:
        d.circle("hole_fill", hx, y, 1.9)
    for a, b in zip(holes[:-1], holes[1:]):
        d.poly("thread_orn", [(hx, a + 3), (hx + (3 if gutter == "left" else -3), (a + b) / 2), (hx, b - 3)])
    h = Hand(d, rng, "ink", amp=0.9)
    return d, h, rng


def folio(n, gutter):
    x = W - 120 if gutter == "left" else 60
    return dict(id="folio", x=W / 2 - 60, y=H - 70, w=120, size=16, lh=20, font=TYPE, align="center", color=TONER,
                runs=[(f"— {n} —", "")])


# ------------------------------------------------------------------ pages

def page1():
    d, h, rng = sheet(201, "left")
    h.stroke([(58, 44), (W - 34, 44), (W - 34, H - 44), (58, H - 44)], "core", closed=True)
    h.stroke([(68, 54), (W - 44, 54), (W - 44, H - 54), (68, H - 54)], "hair", closed=True)
    sigil(h, (W + 24) / 2, 700, 330)
    B = [dict(id="t", x=60, y=150, w=W - 36, size=104, lh=110, font=BLACK, align="center", color=TONER,
              runs=[("Vis Maior", "")]),
         dict(id="st", x=90, y=278, w=W - 156, size=22, lh=30, font=TYPE, align="center", color=TONER,
              runs=[("or, the Power which Excuseth", "")]),
         dict(id="dm", x=110, y=1090, w=W - 196, size=21, lh=32, font=TYPE, ls=0.06, align="center", color=TONER,
              runs=[("THE DEMON NONE WILL SUMMON", ""), ("", "br"), ("AND NONE WILL CRITICIZE", "")]),
         folio(1, "left")]
    return d.svg(), B


TEXT2 = [
    ("Of its Names", "It is called Force Majeure by the French, Höhere Gewalt by the Germans, Fuerza Mayor and Forza "
                     "Maggiore in the south, the Act of God by the English, and by the old jurists Vis Maior, the greater "
                     "force. It answers to all of these. It signs none of them."),
    ("Of its Office", "It excuseth performance. It suspendeth the hour. Under it no penalty accrueth and no credit is "
                      "owed. It hath dominion over flood, fire, storm and the shaking of the ground; over war, riot and "
                      "the closing of roads; over the strike, the embargo and the order of the magistrate; over the "
                      "failure of carriers, the failure of the mains, and the cutting of cable by persons unknown."),
    ("Of its Summoning", "It is not summoned. It is written in beforehand, in the smallest type, signed by both "
                         "parties and filed. Writing, signing, forgetting: that is the whole of the operation, and it is "
                         "performed in every office before every bargain. Thereafter it cometh of itself, when the loss "
                         "is no one's fault."),
    ("Of its Notice", "It hath no power until it is named. Name it in writing, promptly, to the other party. Set down "
                      "what it preventeth and for how long. Show that thou didst strive against it. Then it standeth "
                      "between thee and every claim."),
    ("Of its Departure", "It departeth when the circumstance endeth. If it tarry past the term the parties wrote, "
                         "either may end the bargain, and that ending is its only banishing."),
    ("Of its Critics", "It hath none. No party speaketh against it, for each would have it. In the hour of loss the "
                       "storm is cursed and the clause is kept, and the next bargain copieth it word for word."),
]


def page2():
    from layout import box_height
    d, h, rng = sheet(202, "right")
    B = []
    y = 70
    for k, (head, body) in enumerate(TEXT2):
        hb = dict(id=f"h{k}", x=60, y=y, w=W - 150, size=34, lh=38, font=BLACK, color=TONER, runs=[(head, "")])
        B.append(hb)
        y += 44
        bb = dict(id=f"b{k}", x=60, y=y, w=W - 150, size=17.5, lh=25, font=TYPE, color=TONER, runs=[(body, "")])
        B.append(bb)
        y += box_height(bb) * 1.08 + 26
    B.append(folio(2, "right"))
    return d.svg(), B, y


def page3():
    d, h, rng = sheet(203, "left")
    cx, cy, R = (W + 24) / 2 + 10, 640, 215
    xs, xe, xterm = 92, W - 70, W - 150
    ys = [330 + k * 52 for k in range(12)]
    ended = {2, 7, 10}
    for k, y in enumerate(ys):
        h.dot(xs, y, 5.5)
        # the bargain runs to the event, is held under it, and resumes or is ended at the term
        a = cx - math.sqrt(max(0.0, (R + 14) ** 2 - (y - cy) ** 2)) if abs(y - cy) < R + 14 else None
        b = cx + math.sqrt(max(0.0, (R + 14) ** 2 - (y - cy) ** 2)) if abs(y - cy) < R + 14 else None
        if a is None:
            h.stroke([(xs, y), (xterm if k in ended else xe, y)], "orn")
        else:
            h.stroke([(xs, y), (a - 10, y)], "orn")
            h.stroke([(a - 6, y - 7), (a - 6, y + 7)], "hair")
            h.stroke([(b + 6, y - 7), (b + 6, y + 7)], "hair")
            h.stroke([(b + 10, y), (xterm if k in ended else xe, y)], "orn")
        if k in ended:
            h.stroke([(xterm, y - 12), (xterm, y + 12)], "core")
        else:
            arrowhead(h, (xe, y), 0, 12, "ink", "orn")
    for yy in range(300, 950, 14):
        h.stroke([(xterm, yy), (xterm, yy + 7)], "hair")
    # the seal: black, with its figure in reverse
    disc = arc_pts(cx, cy, R, 0, 360, 200)
    h.doc.poly("ink_fill", disc, closed=True)
    sigil(Hand(d, rng, "ink", amp=0.6), cx, cy - 6, 150, "core", "wh", ring=False)
    h.stroke(arc_pts(cx, cy, R - 46, 0, 360, 180), "hair", "wh")
    h.stroke(arc_pts(cx, cy, R - 8, 0, 360, 180), "hair", "wh")
    words = ["FLOOD", "FIRE", "STORM", "EARTHQUAKE", "WAR", "RIOT", "STRIKE", "EMBARGO", "ORDER OF THE MAGISTRATE",
             "FAILURE OF CARRIERS", "CABLE CUT BY PERSONS UNKNOWN", "ACT OF GOD"]
    return d.svg(), dict(cx=cx, cy=cy, R=R, words=words, ys=ys, xterm=xterm)


def page3_boxes(meta):
    cx, cy, R = meta["cx"], meta["cy"], meta["R"]
    B = [dict(id="t", x=40, y=80, w=W - 80, size=64, lh=70, font=BLACK, align="center", color=TONER,
              runs=[("The Power", "")])]
    # the litany round the rim, word by word, in reverse
    words = meta["words"]
    total = sum(len(w) + 2 for w in words)
    a = -90.0
    rr = R - 27
    for i, w in enumerate(words):
        span = 360 * (len(w) + 2) / total
        mid = a + span / 2
        x, y = cx + rr * math.cos(math.radians(mid)), cy + rr * math.sin(math.radians(mid))
        bw = 2 * math.pi * rr * span / 360
        B.append(dict(id=f"w{i}", x=round(x - bw / 2, 1), y=round(y - 9, 1), w=round(bw, 1), h=18, size=12.5, lh=18,
                      font=TYPE, align="center", color="#efece4", ls=0.04, rot=round(mid + 90, 1), runs=[(w, "")]))
        a += span
    B.append(dict(id="term", x=meta["xterm"] - 70, y=258, w=140, size=13, lh=16, font=TYPE, align="center",
                  color=TONER, runs=[("the term the parties wrote", "")]))
    B.append(dict(id="bar", x=50, y=258, w=200, size=13, lh=16, font=TYPE, color=TONER, runs=[("the bargain", "")]))
    B.append(dict(id="cap", x=60, y=1010, w=W - 96, size=46, lh=54, font=BLACK, align="center", color=TONER,
                  runs=[("Under it no one was wrong.", "")]))
    B.append(folio(3, "left"))
    return B


def page4():
    d, h, rng = sheet(204, "right")
    # step marks down the page
    monogram(h, 250, 640, 190, "orn")
    h.stroke([(400, 640), (470, 640)], "hair")
    arrowhead(h, (470, 640), 0, 10, "ink", "hair")
    sigil(h, 640, 646, 180, "core")
    # the form for objections: ruled, and left as it was printed
    for k in range(6):
        y = 1010 + k * 44
        h.stroke([(60, y), (W - 90, y)], "hair", amp=0.3)
    return d.svg(), {}


def page4_boxes(meta):
    B = [dict(id="t", x=40, y=60, w=W - 110, size=56, lh=62, font=BLACK, align="center", color=TONER,
              runs=[("The Operation", "")]),
         dict(id="i1", x=60, y=160, w=W - 150, size=17.5, lh=25, font=TYPE, color=TONER,
              runs=[("Take the clause as it is written:", "")]),
         dict(id="s1", x=60, y=200, w=W - 150, size=24, lh=32, font=TYPE, ls=0.12, align="center", color=TONER,
              runs=[(STATEMENT, "")]),
         dict(id="i2", x=60, y=252, w=W - 150, size=17.5, lh=25, font=TYPE, color=TONER,
              runs=[("Strike every letter that has come before:", "")]),
         dict(id="s2", x=60, y=292, w=W - 150, size=24, lh=32, font=TYPE, ls=0.12, align="center", color=TONER,
              runs=strike_runs()),
         dict(id="i3", x=60, y=344, w=W - 150, size=17.5, lh=25, font=TYPE, color=TONER,
              runs=[("Twelve remain. Lay them one upon another, and keep what the figure needs:", "")]),
         dict(id="s3", x=60, y=404, w=W - 150, size=24, lh=32, font=TYPE, ls=0.5, align="center", color=TONER,
              runs=[(" ".join(reduced()), "")]),
         dict(id="i4", x=60, y=800, w=W - 150, size=17.5, lh=25, font=TYPE, color=TONER,
              runs=[("It needs no charging. The clause was signed, filed and forgotten, and that was the charge.", "")]),
         dict(id="obj", x=60, y=966, w=W - 150, size=17.5, lh=25, font=TYPE, ls=0.06, color=TONER,
              runs=[("OBJECTIONS TO THE POWER:", "")]),
         folio(4, "right")]
    return B
