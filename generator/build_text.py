"""Build every Revision 5 text leaf: proem, §1–§7, §9–§12, Debts, References."""
import json
import re
import sys

sys.path.insert(0, "/home/claude/grim")
import leaf
import hands as Hd
from preview import compose

OUT = "/home/claude/grim/out/text/"
PAL = {"red": leaf.RED, "ink": leaf.INK}
ZW = "​"


def hand(fn, id, text, size, w=168, **kw):
    return lambda x, y: fn(id, x, y, w, text, size=size, **kw)


# the proem: Rev 5's opening paragraph and "What changed from Revision 4"
front = leaf.BYTITLE["FRONT"]["blocks"]
changed = leaf.BYTITLE["What changed from Revision 4"]["blocks"]
leaf.BYTITLE["PROEM"] = {"title": "PROEM", "blocks": [front[2],
                         {"t": "h3x", "runs": [["What changed from Revision 4", "b"]]}] + changed}
_items = leaf.items_of


def items_of(sec):
    out = []
    for b in sec["blocks"]:
        if b["t"] == "h3x":
            out.append(dict(kind="p", runs=[("What changed from Revision 4", "sc red")], extra=16,
                            key="What changed"))
        else:
            out.extend(_items({"blocks": [b]}))
    return out


leaf.items_of = items_of


def url_soft(sec):
    """soft breaks inside URLs so long addresses wrap"""
    for b in sec["blocks"]:
        for i, (t, s) in enumerate(b.get("runs", [])):
            if "http" in t:
                b["runs"][i] = [re.sub(r"(https?://\S+)", lambda m: re.sub(r"([/.\-_])", r"\1" + ZW, m.group(1)), t), s]
    return sec


SPEC = [
    # key, section title, number, running-head short title, margin, colfracs, label
    ("proem", "PROEM", "", "Proem", [], None, "Revisable Systems Practice — Revision 5"),
    ("s1", "1 Purpose, scope and starting points", "1", "Purpose, scope and starting points",
     [("P4.", 9), ("P5.", 0)], [[0.3, 0.3, 0.4]], None),
    ("s2", "2 The core practice", "2", "The core practice",
     [("Regulation and revision.", 5), ("Regulation and revision.", 6), ("Add before you remove.", 7),
      ("Test the successor first.", 8), ("Reflexivity.", 10)], None, None),
    ("s3", "3 Four audits", "3", "Four audits",
     [("Captured options", 4), ("Does the centre expire?", hand(Hd.cust, "s01", "The gate does not know the road. "
                                                                 "It knows who may name the road.", 16)),
      ("Interests without votes.", 1), ("Before any audit", 3)], None, None),
    ("s4", "4 Five distinctive claims", "4", "Five distinctive claims",
     [("D3", hand(Hd.unh, "s04", "The witness who is punished teaches the instrument to report calm.", 22)),
      ("Measure. Code each", 5), ("Measure. Code each", 6)], None, None),
    ("s5", "5 Power, care and representation", "5", "Power, care and representation", [("Enforcement.", 3)], None,
     None),
    ("s6", "6 Irreversibility, habitats and artificial systems", "6", "Irreversibility, habitats and artificial systems",
     [("Habitats.", 2), ("Habitats.", 9), ("Artificial systems.", 1)], None, None),
    ("s7", "7 Ten constraints", "7", "Ten constraints", [], None, None),
    ("s9", "9 Worked example B: a test that found nothing distinctive", "9", "A test that found nothing distinctive",
     [], None, None),
    ("s10", "10 Worked example C: an analogy taken to its limit", "10", "An analogy taken to its limit", [], None,
     None),
    ("s11", "11 Testing program", "11", "Testing program",
     [("Tag provenance", hand(Hd.mhand, "s19", "Do not repair the witness to fit the instrument.", 22))],
     [[0.2, 0.24, 0.32, 0.24]], None),
    ("s12", "12 Open questions, left open", "12", "Open questions, left open",
     [("The refuge dependency.", 2), ("Single-owner infrastructure.", 4)], None, None),
    ("debts", "Debts", "", "Debts", [("Movement continuity", lambda x, y: dict(
        id="s17", x=x, y=y, w=168, size=15, lh=19, font=leaf.PICA, color=leaf.SEPIA, para_gap=0,
        runs=[("What remained legible was appointed oldest.", "i")]))], None, None),
]


def run(keys=None):
    import os
    os.makedirs(OUT, exist_ok=True)
    manifest = []
    for key, title, num, short, margin, colfracs, label in SPEC:
        if keys and key not in keys:
            continue
        leaves = leaf.build_section(title, num, short, margin=margin, colfracs=colfracs, label=label,
                                    seed=len(manifest) + 3)
        for i, (svg, B) in enumerate(leaves):
            name = f"{key}_{i + 1}"
            if key == "proem" and i == 0:
                B.append(dict(id="byline", x=300, y=186, w=400, size=15, lh=19, font=leaf.PICA, color=leaf.SEPIA,
                              align="center", runs=[("10 October 2026", "i")]))
            open(OUT + name + ".svg", "w").write(svg)
            json.dump(B, open(OUT + name + ".json", "w"), ensure_ascii=False)
            p = compose(svg, B, PAL, leaf.PAPER, 1000, 1600, "t_" + name)
            manifest.append((name, title, i + 1, len(leaves)))
    # references, smaller type, wider measure
    if not keys or "refs" in keys:
        leaf.BODY.update(size=15.5, lh=21, gap=6)
        leaf.TX0, leaf.TW = 112, 640
        sec = url_soft(leaf.BYTITLE["References"])
        leaves = leaf.build_section("References", "", "References", seed=77, margin=[
            ("Systematology: A revisable", hand(Hd.unh, "s14", "I kept the wrong copy because it was the one we used.",
                                               21))])
        for i, (svg, B) in enumerate(leaves):
            name = f"refs_{i + 1}"
            open(OUT + name + ".svg", "w").write(svg)
            json.dump(B, open(OUT + name + ".json", "w"), ensure_ascii=False)
            compose(svg, B, PAL, leaf.PAPER, 1000, 1600, "t_" + name)
            manifest.append((name, "References", i + 1, len(leaves)))
        leaf.BODY.update(size=19, lh=27.4, gap=11)
        leaf.TX0, leaf.TW = 128, 624
    json.dump(manifest, open(OUT + "manifest.json", "w"))
    for m in manifest:
        print(m)


if __name__ == "__main__":
    run(sys.argv[1:] or None)
