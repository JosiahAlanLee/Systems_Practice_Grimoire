"""Stage B artboards: II, IV, VI, XI, the border strip, the transcription proof sheet, slips H and I."""
import json
import sys

sys.path.insert(0, "/home/claude/grim")
from artboard2 import page
import hands as Hd

O = "/home/claude/grim/out/"
P = {"red": Hd.RED, "ink": Hd.INK}
BLOB = {
    "ii_face": "37fdcbcc211f39de64df9363526b82db", "ii_verso": "ca4803e874593929c25313e3fb5f8ba4",
    "iv_face": "42923db40698df6ba908f470763f276c", "iv_verso": "e8a3b26dc1c8041134127a7d1b428a26",
    "vi_inside": "ada5472885774016e9e2ec56d20dc43e", "vi_outside": "73e5e11056587a4a8ed980bd35e2eddd",
    "xi_face": "1d80e0b907826161354c6b6c3d42e6ce", "xi_verso": "60ccdc979396bc9e43c47cccd9e3acec",
    "xi_strip_front": "eb55a1ed07ebee3089a8ebea4cbe0b90", "xi_strip_back": "87d3ec8c9736f8c737273a7a8bb18ba6",
    "keyproof": "d1d8b0137e3edfaae18ef6e9b2ba08c0", "slip_h": "d9c520a70e66e2e7bc2ef762f9e017e8",
    "slip_i": "063776061e25ad602f4ba19ab14d1582",
}
b = lambda k: "/_blob/" + BLOB[k]

ii = json.load(open(O + "ii_boxes.json"))
ivb = json.load(open(O + "iv_boxes.json"))
vib = json.load(open(O + "vi_boxes.json"))
xib = json.load(open(O + "xi_boxes.json"))
slb = json.load(open(O + "slips_boxes.json"))

import iv, vi, xi, slips

pages = {
    "II-face": page("Tabula II — Of the Two Clocks", ii["face_boxes"], P, "#ebe1c8", Hd.INK, b("ii_face"),
                    "Engraved plate: a large clock face cut into the plate, its recognition-to-dispatch interval hatched, "
                    "beside a smaller clock drawn on a pasted sheet with its dispatch-to-restoration interval hatched. Three "
                    "witness lines run under both; the shared dispatch tick is half engraved and half drawn; a fine "
                    "access-request line crosses from the pasted clock into the engraved one. Typed tapes name "
                    "recognition, dispatch and restoration.", "IM FELL English"),
    "II-verso": page("Verso of Tabula II", ii["verso_boxes"], P, "#ebe1c8", Hd.INK, b("ii_verso"),
                     "Verso with a ruler on which the dispatch is entered twice in red.", "IM FELL English"),
    "IV-face": page("Tabula IV — Of the Second Copy", ivb["face_boxes"], P, iv.PAPER, Hd.INK, b("iv_face"),
                    "A mounted record of two long cornmeal deposits on a dark ground, joined by a dotted copying path with "
                    "an arrow. Both deposits lack the same segment; a paper patch covers the first gap, the second is "
                    "exposed, and red chalk brackets mark both. A sharp test stroke sits at the lower edge. Below the "
                    "mount, a caption strip in the transcription hand.", "EB Garamond",
                    extra=iv.patch_html({"patch": ivb["patch"]}), script=iv.SCRIPT, fonts_extra=("Zeyada",)),
    "IV-verso": page("Verso of Tabula IV", ivb["verso_boxes"], P, iv.PAPER, Hd.INK, b("iv_verso"),
                     "Verso of the mounted record.", "EB Garamond"),
    "VI-outside": page("Tabula VI — Of the Borrowed Face (outside of the fold)", vib["outside_boxes"], P, vi.PAPER,
                       vi.PENS["dk"], b("vi_outside"),
                       "The folded flap of a plotter foldout: three attempted profiles show faintly through the paper "
                       "in reverse.", "IBM Plex Mono", W=vi.WO, Hh=vi.HO),
    "VI-inside": page("Tabula VI — inside the fold", vib["inside_boxes"], P, vi.PAPER, vi.PENS["dk"], b("vi_inside"),
                      "A plotter foldout: three successive attempts at a supplied profile, each with the target "
                      "registered over it as a dotted olive line. The third meets the cheek and overshoots the jaw, "
                      "measured by rust-red ticks. To the right a movable registration tab carries the small target "
                      "contour; a thread runs from its eyelet to a pasted, unsigned instruction; a folded procedural scrap "
                      "lies below.", "IBM Plex Mono", W=vi.W2, Hh=vi.H2, extra=vi.tab_html(), script=vi.SCRIPT),
    "XI-face": page("Tabula XI — Of the Closed Neck", xib["face_boxes"], P, xi.PAPER, Hd.INK, b("xi_face"),
                    "Engraved plate: two routes descend from separate origins and meet above a large pinched gate whose "
                    "neck has been closed with a later cut. A rust-red plotter line leaves the meeting point, passes "
                    "round the gate and arrives at a second, smaller gate below, through which the engraved spine also "
                    "runs. An inset cartouche holds a short instruction; three tracing fields at the foot record two "
                    "trials and leave the third blank.", "IM FELL English"),
    "XI-verso": page("Verso of Tabula XI", xib["verso_boxes"], P, xi.PAPER, Hd.INK, b("xi_verso"),
                     "Verso with a strip from another copy laid in at the top, holding the instruction intact.",
                     "IM FELL English"),
    "XI-strip-front": page("Tabula XI — border strip", xib["strip_front"], P, xi.STRIP_PAPER, Hd.INK, b("xi_strip_front"),
                           "A border strip, its stitching holes along the top edge, carrying twelve groups of letters "
                           "and periods between two rules.", "IM FELL DW Pica", W=xi.STRIP_W, Hh=xi.STRIP_H),
    "XI-strip-back": page("Tabula XI — border strip, reverse", xib["strip_back"], P, xi.STRIP_PAPER, Hd.INK,
                          b("xi_strip_back"),
                          "The back of the border strip: twelve column numerals, each with a short downstroke beneath, "
                          "and two letters stacked under the first.", "IM FELL DW Pica", W=xi.STRIP_W, Hh=xi.STRIP_H),
    "Key-transcription": page("Proof sheet — the transcription hand", slb["key_boxes"], P, slips.SLIP_BG, Hd.INK,
                              b("keyproof"),
                              "The twelve marks, each with one, two or three tally strokes above its letter; invalid "
                              "combinations dashed; an example sentence in the hand between two rules.", "EB Garamond",
                              W=slips.KW, Hh=slips.KH),
    "Slip-H": page("Slip H — a rule for the quiet instrument", slb["h_boxes"], P, slips.H_MOUNT, Hd.INK, b("slip_h"),
                   "A torn scrap of gridded technical paper with a ruled trial form at its foot: three headed columns and "
                   "a fourth left without a head.", "IM FELL DW Pica", W=slips.HW, Hh=slips.HH),
    "Slip-I": page("Slip I — from a receipt for the revised seal", slb["i_boxes"], P, slips.H_MOUNT, Hd.INK, b("slip_i"),
                   "A receipt leaf torn from its counterfoil: a stamped seal holding an open spiral; beside it a cleaner "
                   "patch of paper with two pin holes where a separate slip was once attached.", "IM FELL DW Pica",
                   W=slips.IW, Hh=slips.IH),
}
for k, v in pages.items():
    open(O + k + ".dc.html", "w").write(v)
    print(k, len(v))
