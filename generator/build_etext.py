"""Build the e-reader text pages for every section of Revision 5."""
import json
import os
import re
import sys

sys.path.insert(0, "/home/claude/grim")
import etext as L
import hands as Hd
from preview import compose

OUT = "/home/claude/grim/out/etext/"
PAL = {"red": L.RED, "ink": L.INK}
ZW = "​"


def hand(fn, id, text, size, w=232, **kw):
    return lambda x, y: fn(id, x, y, w, text, size=size, **kw)


front = L.BYTITLE["FRONT"]["blocks"]
changed = L.BYTITLE["What changed from Revision 4"]["blocks"]
L.BYTITLE["PROEM"] = {"title": "PROEM", "blocks": [front[2], {"t": "h3x"}] + changed}
_items = L.items_of


def items_of(sec):
    out = []
    for b in sec["blocks"]:
        if b["t"] == "h3x":
            out.append(dict(kind="p", runs=[("What changed from Revision 4", "sc red")], extra=22, key="What changed"))
        else:
            out.extend(_items({"blocks": [b]}))
    return out


L.items_of = items_of


def url_soft(sec):
    for b in sec["blocks"]:
        for i, (t, s) in enumerate(b.get("runs", [])):
            if "http" in t:
                b["runs"][i] = [re.sub(r"(https?://\S+)", lambda m: re.sub(r"([/.\-_])", r"\1" + ZW, m.group(1)), t), s]
    return sec


SPEC = [
    ("proem", "PROEM", "", "Proem", [], None, "Revisable Systems Practice — Revision 5"),
    ("s1", "1 Purpose, scope and starting points", "1", "Purpose, scope and starting points",
     [("P4.", 9), ("P5.", 0)], [[0.28, 0.3, 0.42]], None),
    ("s2", "2 The core practice", "2", "The core practice",
     [("Regulation and revision.", 5), ("Regulation and revision.", 6), ("Add before you remove.", 7),
      ("Test the successor first.", 8), ("Reflexivity.", 10)], None, None),
    ("s3", "3 Four audits", "3", "Four audits",
     [("Captured options", 4), ("Does the centre expire?", hand(Hd.cust, "s01", "The gate does not know the road. "
                                                                 "It knows who may name the road.", 21)),
      ("Interests without votes.", 1), ("Before any audit", 3)], None, None),
    ("s4", "4 Five distinctive claims", "4", "Five distinctive claims",
     [("D3", hand(Hd.unh, "s04", "The witness who is punished teaches the instrument to report calm.", 29)),
      ("Measure. Code each", 5), ("Measure. Code each", 6)], None, None),
    ("s5", "5 Power, care and representation", "5", "Power, care and representation", [("Enforcement.", 3)], None,
     None),
    ("s6", "6 Irreversibility, habitats and artificial systems", "6", "Irreversibility, habitats and artificial systems",
     [("Habitats.", 2), ("Habitats.", 9), ("Artificial systems.", 1)], None, None),
    ("s7", "7 Ten constraints", "7", "Ten constraints", [], None, None),
    ("s8", "8 Worked example A: an outage delayed by authority", "8", "An outage delayed by authority",
     [("Audits.", 3), ("Proposal.", 7)], None, None),
    ("s9", "9 Worked example B: a test that found nothing distinctive", "9", "A test that found nothing distinctive",
     [], None, None),
    ("s10", "10 Worked example C: an analogy taken to its limit", "10", "An analogy taken to its limit", [], None, None),
    ("s11", "11 Testing program", "11", "Testing program",
     [("Tag provenance", hand(Hd.mhand, "s19", "Do not repair the witness to fit the instrument.", 29))],
     [[0.19, 0.24, 0.31, 0.26]], None),
    ("s12", "12 Open questions, left open", "12", "Open questions, left open",
     [("The refuge dependency.", 2), ("Single-owner infrastructure.", 4)], None, None),
    ("s13", "13 The mark and an orientation", "13", "The mark and an orientation", [], None, None),
    ("debts", "Debts", "", "Debts", [("Movement continuity", lambda x, y: dict(
        id="s17", x=x, y=y, w=232, size=20, lh=25, font=L.PICA, color=L.SEPIA, para_gap=0,
        runs=[("What remained legible was appointed oldest.", "i")]))], None, None),
]


def run():
    os.makedirs(OUT, exist_ok=True)
    manifest = []
    for k, (key, title, num, short, margin, colfracs, label) in enumerate(SPEC):
        pages = L.build_section(title, num, short, margin=margin, colfracs=colfracs, label=label, seed=k + 31)
        for i, (svg, B) in enumerate(pages):
            name = f"{key}_{i + 1}"
            if key == "proem" and i == 0:
                B.append(dict(id="byline", x=400, y=244, w=400, size=20, lh=24, font=L.PICA, color=L.SEPIA,
                              align="center", runs=[("10 October 2026", "i")]))
            open(OUT + name + ".svg", "w").write(svg)
            json.dump(B, open(OUT + name + ".json", "w"), ensure_ascii=False)
            compose(svg, B, PAL, L.PAPER, L.W, L.H, "e_" + name)
            manifest.append(dict(name=name, key=key, num=num, short=short, page=i + 1, of=len(pages)))
    L.BODY.update(size=22, lh=30, gap=6)
    L.TX0, L.TW = 96, 816
    L.MX, L.MW = 942, 200
    url_soft(L.BYTITLE["References"])
    pages = L.build_section("References", "", "References", seed=77, margin=[
        ("Systematology: A revisable", hand(Hd.unh, "s14", "I kept the wrong copy because it was the one we used.", 27,
                                           w=200))])
    for i, (svg, B) in enumerate(pages):
        name = f"refs_{i + 1}"
        open(OUT + name + ".svg", "w").write(svg)
        json.dump(B, open(OUT + name + ".json", "w"), ensure_ascii=False)
        compose(svg, B, PAL, L.PAPER, L.W, L.H, "e_" + name)
        manifest.append(dict(name=name, key="refs", num="", short="References", page=i + 1, of=len(pages)))
    json.dump(manifest, open(OUT + "manifest.json", "w"))
    for m in manifest:
        print(m["name"], m["page"], "/", m["of"])


if __name__ == "__main__":
    run()
