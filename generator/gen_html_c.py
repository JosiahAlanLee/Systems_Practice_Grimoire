"""Stage C: every new leaf as an artboard, and the canvas index laid out in reading order."""
import json
import sys

sys.path.insert(0, "/home/claude/grim")
from artboard2 import page
import hands as Hd

O = "/home/claude/grim/out/"
PROJ = "/tmp/claude-0/-home-claude/f25d994f-f4dc-5e27-83bc-deb2f1661cca/scratchpad/canvas/project/"
B = {
    "title": "9f9267f32668f644e7e1bad16e22ed55", "index": "3bd355613d03d4d7a48f837fb8257559",
    "proem_1": "e7d5677092ba31b8c961d748be0bb626", "i_face": "6ab17bade0ae250e5150c7210ce8b0da",
    "s1_1": "67acb122058fca78cd3d5f27016da3bd", "s2_1": "fb37cc35e139e52c872a11b98ffdc9d3",
    "s3_1": "a2ac7667807572b3e87cd83d1e360966", "s4_1": "98f4dee2e4bdc62914192ccfc8d1c2b3",
    "s4_2": "28eb046e1001f5257921a9c5fe510acf", "v_face": "de5d498580b434743e227df953842aee",
    "s5_1": "71628f51e84935e820fbc41de3a3b4c9", "s6_1": "3171b2008299a42eb0ad94da3df1fb0d",
    "vii_face": "a4772141c2b64464dc74c5e895addfe0", "s7_1": "476a9eab3938149900d28438dc642866",
    "fm1": "e00febdb2bc933e0ebf1fe04b892dfc8", "fm2": "e9f5064bed0946f09d8910f1ff4cb8ae",
    "fm3": "12b84dc604c10748f4f9912a75736303", "fm4": "eda00bcc6706a32071b8bbafbce45712",
    "ix_face": "c465c2e3bd3edf19641a5db27322b075", "s9_1": "90ad2309d1c527f077ef47c05648eb2e",
    "x_face": "e2e21d804b250f42077c96f1a9b7b6eb", "s10_1": "10b78b938b924d074dd79696223843fa",
    "s11_1": "c587bea09fc62e0d86680706d67e2aed", "xii_face": "ae112d80d7f48e30ccdab1be16ac03bf",
    "s12_1": "c85351f246b86155d0bbddc0f319d21a", "debts_1": "690c431172fca2b25d9ac8e16d9913d0",
    "refs_1": "593fd445f8734570bab6dcc9bc223312", "refs_2": "f5d8670122d5a27d545ee8caf04d274d",
    "refs_3": "d3882fae2f196ba594ffdca47b8b9d60",
}
blob = lambda k: "/_blob/" + B[k]
P = {"red": Hd.RED, "ink": Hd.INK}
PAPER = "#ebe1c8"
CREAM = "#f6f1e3"
PICA = "IM FELL DW Pica"


def jload(p, key=None):
    j = json.load(open(p))
    return j[key] if key else j


SEC_NAMES = {"1": "Purpose, scope and starting points", "2": "The core practice", "3": "Four audits",
             "4": "Five distinctive claims", "5": "Power, care and representation",
             "6": "Irreversibility, habitats and artificial systems", "7": "Ten constraints",
             "9": "A test that found nothing distinctive", "10": "An analogy taken to its limit",
             "11": "Testing program", "12": "Open questions, left open"}
MARGINS = {"1", "2", "3", "4", "5", "6", "12"}

boards = {}   # file -> (html, w, h, title)


def add(fname, html, w, h, title):
    boards[fname] = (html, w, h, title)


def text_leaf(key, fname, title, alt):
    bx = jload(O + f"text/{key}.json")
    add(fname, page(title, bx, P, PAPER, Hd.INK, blob(key), alt, PICA), 1000, 1600, title)


add("Title.dc.html", page("Clavicula Matricis — title", jload(O + "title_boxes.json"), P, PAPER, Hd.INK, blob("title"),
                          "Title leaf: the name of the volume above an engraved roundel holding the open, branching "
                          "spiral.", "IM FELL English"), 1000, 1600, "Title")
add("Index.dc.html", page("Clavicula Matricis — index of the tables", jload(O + "index_boxes.json"), P, PAPER, Hd.INK,
                          blob("index"), "An engraved index of the thirteen tables and the bound-in tract, each with its "
                          "workshop.", "IM FELL English"), 1000, 1600, "Index of the tables")
text_leaf("proem_1", "Proem.dc.html", "Proem",
          "Text leaf: the opening paragraph of Revision 5 and what changed from Revision 4, with red rubrics.")
for num in ("1", "2", "3", "5", "6", "7", "9", "10", "11", "12"):
    extra = " Marks of Revision 3 stand in the margin, each with its meaning stated." if num in MARGINS else ""
    text_leaf(f"s{num}_1", f"Text-{num}.dc.html", f"§ {num} · {SEC_NAMES[num]}",
              f"Text leaf: Revision 5, section {num}, {SEC_NAMES[num].lower()}, in a letterpress face with red rubrics."
              + extra)
for part in ("1", "2"):
    text_leaf(f"s4_{part}", f"Text-4{'ab'[int(part) - 1]}.dc.html", f"§ 4 · Five distinctive claims ({part} of 2)",
              f"Text leaf: Revision 5, section 4, five distinctive claims, part {part} of 2, with red rubrics."
              + (" Marks of Revision 3 stand in the margin, each with its meaning stated." if part == "2" else ""))
text_leaf("debts_1", "Debts.dc.html", "Debts", "Text leaf: the debts, what was borrowed and from whom, in short form.")
for part in ("1", "2", "3"):
    text_leaf(f"refs_{part}", f"References-{part}.dc.html", f"References ({part} of 3)",
              f"Text leaf: the references, part {part} of 3, in a smaller letterpress face.")

PLATES = [
    ("I-face.dc.html", "i", "Tabula I — Of the One Question", PAPER, Hd.INK, "IM FELL English",
     "Engraved plate: a circle quartered by a cross, one emblem for each row of the scope table: a finished wheel over "
     "an empty dish; a single root with many fast arrows; dots with fading trails; an eye above a closed gate. Nine "
     "studs around it mark the starting points: four hollow, four filled, one balance."),
    ("V-face.dc.html", "v", "Tabula V — Of Visibility Read as Command", PAPER, Hd.INK, "EB Garamond",
     "A mounted cornmeal record: a network of equal nodes with no centre. One node is heavier where the hand paused. "
     "Typed tapes for the press, funders and investigators send red chalk lines to that node, and a red chalk circle "
     "appoints it."),
    ("VII-face.dc.html", "vii", "Tabula VII — Of the Ten Bindings", PAPER, Hd.INK, "IM FELL English",
     "Engraved plate: ten numbered seals bound by twisted cords to a ring around an empty seat. The tenth cord passes "
     "a gatekeeper and a second strand goes round it. Cords from the first and sixth seals are stitched over the "
     "plate's own frame. The ring is worn pale where its finest hatching was."),
    ("IX-face.dc.html", "ix", "Tabula IX — Of a Test That Found Nothing", CREAM, "#33261e", "IBM Plex Mono",
     "A plotter trial record: six postmortems in columns. Two readings plot the same figure for each case; a third "
     "row, for a generic checklist, is outlined in rust and left empty. Rows for retaliation, bottleneck ownership and "
     "gamed incentives hold only hollow circles. Below, a dotted plan of the next run: unseen cases, three arms, blind "
     "judges."),
    ("X-face.dc.html", "x", "Tabula X — Of an Analogy Taken to Its Limit", PAPER, Hd.INK, "EB Garamond",
     "A mounted cornmeal record: a dense vein network in a dusted refuge thins to fragments and then to solitary "
     "cells. Below, two clocks: a continuous slowing spiral that reaches every step, and a ring of brief bursts whose "
     "older marks fade away."),
    ("XII-face.dc.html", "xii", "Tabula XII — Of the Questions Left Open", CREAM, "#33261e", "IBM Plex Mono",
     "A plotter sheet of eight cells. Seven hold figures the pen left unfinished, one for each open question; the "
     "eighth is empty. One rust arc tries to close a regress and stops short."),
]
for fname, key, title, bg, ink, base, alt in PLATES:
    bx = jload(O + f"{key}_boxes.json", "face_boxes")
    pal = {"red": "#9e3b24" if bg == CREAM else Hd.RED, "ink": ink}
    add(fname, page(title, bx, pal, bg, ink, blob(f"{key}_face"), alt, base), 1000, 1600, title.split(" — ")[0] + " · face")

FM_ALT = [
    "Title page of a photocopied tract on grey stock, hinged in on a guard: a blackletter title, a large sigil in a "
    "ring, and a typewritten line beneath.",
    "Typewritten text under blackletter headings: its names, its office, its summoning, its notice, its departure "
    "and its critics.",
    "Twelve obligations run across the page. A black seal bearing the sigil and a litany of disasters covers their "
    "middle; most resume after it, and three end at the term the parties wrote.",
    "The sigil's working: the clause typed, its repeated letters struck, twelve letters left, the letters laid over "
    "one another and reduced to the figure. Below, a ruled form for objections, empty.",
]
FMP = {"red": "#151515", "ink": "#151515"}
for i in range(4):
    bx = jload(O + f"fm/fm{i + 1}.json")
    add(f"VisMaior-{i + 1}.dc.html", page(f"Vis Maior — page {i + 1}", bx, FMP, "#e9e7de", "#151515", blob(f"fm{i + 1}"),
                                           FM_ALT[i], "Special Elite", W=860, Hh=1360), 860, 1360,
        f"Vis Maior · {i + 1}")

for fname, (html, w, h, title) in boards.items():
    open(PROJ + fname, "w").write(html)
print(len(boards), "artboards written")

# ---------------------------------------------------------------- the canvas
ROWS = [
    ("Clavicula Matricis", [("Title.dc.html",), ("Index.dc.html",), ("Proem.dc.html",)]),
    ("I · Of the One Question", [("I-face.dc.html",), ("Text-1.dc.html",)]),
    ("II · Of the Two Clocks", [("II-face.dc.html",), ("II-verso.dc.html",), ("Text-2.dc.html",)]),
    ("III · Of the Speed of Correction", [("III-face.dc.html",), ("III-slip.dc.html",), ("Text-3.dc.html",)]),
    ("IV · Of the Second Copy", [("IV-face.dc.html",), ("IV-verso.dc.html",), ("Text-4a.dc.html",), ("Text-4b.dc.html",),
                                 ("Key-transcription.dc.html",)]),
    ("V · Of Visibility Read as Command", [("V-face.dc.html",), ("Text-5.dc.html",)]),
    ("VI · Of the Borrowed Face", [("VI-outside.dc.html",), ("VI-inside.dc.html",), ("Text-6.dc.html",)]),
    ("VII · Of the Ten Bindings", [("VII-face.dc.html",), ("Text-7.dc.html",)]),
    ("VIII · Of an Outage Delayed by Authority, with Vis Maior bound in",
     [("VIII-face.dc.html",), ("VIII-record.dc.html",), ("VisMaior-1.dc.html",), ("VisMaior-2.dc.html",),
      ("VisMaior-3.dc.html",), ("VisMaior-4.dc.html",)]),
    ("IX · Of a Test That Found Nothing", [("IX-face.dc.html",), ("Text-9.dc.html",), ("Slip-H.dc.html",)]),
    ("X · Of an Analogy Taken to Its Limit", [("X-face.dc.html",), ("Text-10.dc.html",)]),
    ("XI · Of the Closed Neck", [("XI-face.dc.html",), ("XI-verso.dc.html",), ("Text-11.dc.html",),
                                 ("XI-strip-front.dc.html", "XI-strip-back.dc.html")]),
    ("XII · Of the Questions Left Open", [("XII-face.dc.html",), ("Text-12.dc.html",)]),
    ("XIII · Of the Twelve Marks and the Mark", [("XIII-face.dc.html",), ("XIII-verso.dc.html",),
                                                 ("Key-legacy.dc.html", "Slip-I.dc.html")]),
    ("Debts and references", [("Debts.dc.html",), ("References-1.dc.html",), ("References-2.dc.html",),
                              ("References-3.dc.html",)]),
]
OLD_TITLES = {"II-face.dc.html": "II · face", "II-verso.dc.html": "II · verso", "III-face.dc.html": "III · face",
              "III-slip.dc.html": "III · facing slip", "IV-face.dc.html": "IV · face (the patch lifts)",
              "IV-verso.dc.html": "IV · verso", "Key-transcription.dc.html": "Proof sheet · transcription hand",
              "VI-outside.dc.html": "VI · outside of the fold", "VI-inside.dc.html": "VI · inside the fold (the tab lifts)",
              "VIII-face.dc.html": "VIII · face", "VIII-record.dc.html": "VIII · facing record",
              "Slip-H.dc.html": "Slip H · the quiet instrument", "XI-face.dc.html": "XI · face",
              "XI-verso.dc.html": "XI · verso", "XI-strip-front.dc.html": "XI · border strip",
              "XI-strip-back.dc.html": "XI · border strip, reverse", "XIII-face.dc.html": "XIII · face",
              "XIII-verso.dc.html": "XIII · verso", "Key-legacy.dc.html": "Proof slip · legacy hand",
              "Slip-I.dc.html": "Slip I · receipt for the revised seal"}
SIZES = {"Key-transcription.dc.html": (1000, 700), "VI-outside.dc.html": (1000, 1250),
         "VI-inside.dc.html": (2000, 1250), "Slip-H.dc.html": (1000, 560), "XI-strip-front.dc.html": (1000, 170),
         "XI-strip-back.dc.html": (1000, 170), "Key-legacy.dc.html": (1000, 440), "Slip-I.dc.html": (1000, 500)}
INTERACTIVE = {"IV-face.dc.html", "VI-inside.dc.html"}


def size_of(f):
    if f in boards:
        return boards[f][1], boards[f][2]
    return SIZES.get(f, (1000, 1600))


def title_of(f):
    if f in boards:
        t = boards[f][3]
        return {"Text-4a.dc.html": "§ 4 · Five distinctive claims, 1", "Text-4b.dc.html": "§ 4 · Five distinctive claims, 2"
                }.get(f, t)
    return OLD_TITLES[f]


def build_canvas(old):
    cv = dict(old)
    cv["pages"] = [{"id": "second", "name": "The volume"}, {"id": "first", "name": "First states"}]
    cv["launch"] = {"view": "canvas", "page": "second"}
    keep = {k: v for k, v in old["boards"].items() if v.get("page") == "first"}
    order = [k for k in old["order"] if k in keep]
    notes = {k: v for k, v in old["notes"].items() if v.get("page") == "first"}
    y = 0
    for ri, (label, cols) in enumerate(ROWS):
        x = 0
        row_h = 0
        for col in cols:
            cy = y
            cw = 0
            for f in col:
                w, h = size_of(f)
                b = {"x": x, "y": cy, "w": w, "h": h, "title": title_of(f), "page": "second"}
                if f in INTERACTIVE:
                    b["is_interactive"] = True
                keep[f] = b
                order.append(f)
                cy += h + 120
                cw = max(cw, w)
            row_h = max(row_h, cy - 120 - y)
            x += cw + 80
        notes[f"row{ri}"] = {"x": 0, "y": y - 300, "text": label, "kind": "title1", "maxW": max(1000, x - 80),
                             "page": "second"}
        y += row_h + 420
    cv["boards"] = keep
    cv["order"] = order
    cv["notes"] = notes
    return cv


if __name__ == "__main__":
    old = json.load(open(sys.argv[1]))
    cv = build_canvas(old)
    missing = [f for f in cv["boards"] if not __import__("os").path.exists(PROJ + f)]
    print("boards", len(cv["boards"]), "missing files", missing)
    json.dump(cv, open(PROJ + "canvas.json", "w"), ensure_ascii=False, separators=(",", ":"))
