"""The e-reader edition: one 6.2 x 8.27 in PDF, facsimile leaves and reset text in reading order."""
import json
import os
import random
import re
import sys

sys.path.insert(0, "/home/claude/grim")
import pdfbuild as P
from pdfbuild import board, place, page_html, etext_body, PW, PH
import etext as L
from core import Doc
from marks import Hand
from front import INDEX

OUT_PDF = P.WORK + "Clavicula_Matricis_ereader.pdf"
RAW_PDF = P.WORK + "raw.pdf"
PAPER = L.PAPER
SC, ENG, PICA = "'IM Fell English SC', serif", "'IM Fell English', serif", "'IM Fell DW Pica', serif"
RASTER_BOARDS = {"iv_face.svg": "#ebe1c8", "v3_v_face.svg": "#ebe1c8", "v3_x_face.svg": "#ebe1c8",
                 "v2_xiii_face.svg": "#e9dfc6"}
RASTER_SCALE = 1.5

MANIFEST = json.load(open(P.ETEXT + "manifest.json"))
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII"]


# ------------------------------------------------------------------ furniture for the added leaves

def furniture_svg(name, seed):
    rng = random.Random(seed)
    st = L.styles()
    d = Doc(PW, PH, st, order=["fox_fill"] + [k for k in st if k != "fox_fill"])
    h = Hand(d, rng, "ink", amp=0.35)
    L.furniture(h, d, rng, False)
    path = P.WORK + name + ".svg"
    open(path, "w").write(d.svg())
    return path


def text_div(x, y, w, size, lh, font, color, html, align="left", ls=None, style=""):
    l = f" letter-spacing: {ls}em;" if ls else ""
    return (f'<div style="position: absolute; left: {x}px; top: {y}px; width: {w}px; font-family: {font}; '
            f'font-size: {size}px; line-height: {lh}px; color: {color}; text-align: {align};{l} {style}">{html}</div>')


def heads(right):
    return (text_div(60, 40, 480, 17, 22, SC, L.INK, "Clavicula Matricis", ls=0.2)
            + text_div(520, 40, 620, 17, 22, SC, L.RED, right, align="right", ls=0.16))


def caption(y, html, sub=None, w=1000):
    out = text_div((PW - w) / 2, y, w, 18, 24, SC, L.SEPIA, html, align="center", ls=0.16)
    if sub:
        out += text_div((PW - w) / 2, y + 28, w, 19, 25, PICA, L.SEPIA, f"<i>{sub}</i>", align="center")
    return out


# ------------------------------------------------------------------ page kinds

def leaf(pid, fname, state=None, extra=""):
    """a 1000 x 1600 board centred on the 1200 x 1600 page, its paper carried into the margins"""
    b = board(fname, state, extra)
    s = min(PW / b["W"], PH / b["H"])
    x, y = (PW - b["W"] * s) / 2, (PH - b["H"] * s) / 2
    return page_html(pid, b["bg"], place(b, x, y, s))


def bound_in(pid, fname):
    """a sheet of another stock, tipped in on the volume's paper"""
    b = board(fname)
    s = 1.1
    w, hh = b["W"] * s, b["H"] * s
    return page_html(pid, PAPER, place(b, (PW - w) / 2, (PH - hh) / 2, s, shadow=True))


def loose(pid, rh, items, seed):
    """slips laid on a volume leaf: items = [(fname, y, caption, sub)]"""
    body = f'<img src="{P.furl(furniture_svg(pid, seed))}" alt="" style="position: absolute; left: 0; top: 0; width: {PW}px; height: {PH}px">'
    body += heads(rh)
    for fname, y, cap, sub in items:
        b = board(fname)
        s = 1.1
        body += place(b, (PW - b["W"] * s) / 2, y, s, shadow=True)
        if cap:
            body += caption(y + b["H"] * s + 22, cap, sub)
    return page_html(pid, PAPER, body)


def text_leaf(pid, name):
    body, _ = etext_body(name)
    return page_html(pid, PAPER, body)


def vi_pages():
    pages = []
    # the fold opened, reduced
    b = board("VI-inside.dc.html", "closed")
    s = 0.56
    w, hh = b["W"] * s, b["H"] * s
    body = f'<img src="{P.furl(furniture_svg("vi-whole", 61))}" alt="" style="position: absolute; left: 0; top: 0; width: {PW}px; height: {PH}px">'
    body += heads("Tabula VI · the fold opened")
    y0 = 300
    body += place(b, (PW - w) / 2, y0, s, shadow=True)
    body += caption(y0 + hh + 40, "Inside the fold, reduced",
                    "The sittings follow at full size, then the tab, first in place and then lifted.")
    pages.append(page_html("tab-VI-whole", PAPER, body))
    # two crops by content rather than at the crease, so nothing written across the fold is cut:
    # the three sittings with their notes, then the tab, the pasted instruction and the scrap
    crops = (("tab-VI-sittings", "closed", (0, 0, 1300, 1250)), ("tab-VI-tab", "closed", (1300, 0, 700, 1250)),
             ("tab-VI-lifted", "lifted", (1300, 0, 700, 1250)))
    for pid, state, clip in crops:
        b = board("VI-inside.dc.html", state)
        s = min(PW / clip[2], 1.2)
        w, hh = clip[2] * s, clip[3] * s
        pages.append(page_html(pid, b["bg"], place(b, (PW - w) / 2, (PH - hh) / 2, s, clip=clip)))
    return pages


def index_links():
    out = []
    for k, (num, title, shop, sec) in enumerate(INDEX):
        y = 300 + k * 62
        href = f"#tab-{num}" if num else "#vis-maior"
        out.append(f'<a href="{href}" aria-label="{title}" style="position: absolute; display: block; left: 120px; '
                   f'top: {y - 6}px; width: 650px; height: 54px"></a>')
        if sec:
            out.append(f'<a href="#sec-{sec.split()[-1]}" aria-label="{sec}" style="position: absolute; display: block; '
                       f'left: 790px; top: {y - 6}px; width: 100px; height: 54px"></a>')
    return "".join(out)


def etexts(key, first_id):
    out = []
    for m in MANIFEST:
        if m["key"] == key:
            out.append(text_leaf(first_id if m["page"] == 1 else f"{first_id}-{m['page']}", m["name"]))
    return out


# ------------------------------------------------------------------ the volume

def volume():
    """returns (pages html list, outline spec)"""
    pages, toc = [], []

    def add(items, label=None, level=0):
        if label:
            toc.append((label, len(pages), level))
        pages.extend(items if isinstance(items, list) else [items])

    add(leaf("title", "Title.dc.html"), "Title")
    add(leaf("index", "Index.dc.html", extra=index_links()), "Index of the Tables")
    add(etexts("proem", "proem"), "Proem")
    titles = {num: t for num, t, _, _ in INDEX if num}
    secs = {m["key"]: m["short"] for m in MANIFEST}

    def table(n, faces, loose_pages=()):
        r = ROMAN[n - 1]
        toc.append((f"{r} · {titles[r]}", len(pages), 0))
        for pid, fname, label, state in faces:
            add(leaf(pid, fname, state), label, 1)
        add(etexts(f"s{n}", f"sec-{n}"), f"§ {n} · {secs[f's{n}']}", 1)
        for lp, label in loose_pages:
            add(lp, label, 1)

    table(1, [("tab-I", "I-face.dc.html", "Tabula I", None)])
    table(2, [("tab-II", "II-face.dc.html", "Tabula II", None), ("tab-II-verso", "II-verso.dc.html", "Verso", None)])
    table(3, [("tab-III", "III-face.dc.html", "Tabula III", None),
              ("tab-III-slip", "III-slip.dc.html", "Facing slip", None)])
    table(4, [("tab-IV", "IV-face.dc.html", "Tabula IV, the patch in place", "closed"),
              ("tab-IV-lifted", "IV-face.dc.html", "Tabula IV, the patch lifted", "lifted"),
              ("tab-IV-verso", "IV-verso.dc.html", "Verso", None)],
          [(loose("loose-iv", "Loose · Tabula IV",
                  [("Key-transcription.dc.html", 415, None, None)], 41),
            "Proof sheet · the transcription hand")])
    table(5, [("tab-V", "V-face.dc.html", "Tabula V", None)])
    # VI: outside, then the fold
    toc.append((f"VI · {titles['VI']}", len(pages), 0))
    add(leaf("tab-VI", "VI-outside.dc.html"), "Tabula VI, outside of the fold", 1)
    vp = vi_pages()
    add(vp[0], "Inside the fold, reduced", 1)
    add(vp[1], "The three sittings", 1)
    add(vp[2], "The registration tab in place", 1)
    add(vp[3], "The registration tab lifted", 1)
    add(etexts("s6", "sec-6"), f"§ 6 · {secs['s6']}", 1)
    table(7, [("tab-VII", "VII-face.dc.html", "Tabula VII", None)])
    table(8, [("tab-VIII", "VIII-face.dc.html", "Tabula VIII", None),
              ("tab-VIII-record", "VIII-record.dc.html", "Facing record", None)])
    toc.append(("Vis Maior, or the Power which Excuseth", len(pages), 0))
    for i in range(4):
        add(bound_in("vis-maior" if i == 0 else f"vis-maior-{i + 1}", f"VisMaior-{i + 1}.dc.html"),
            ["Of its Names … Of its Critics", "The Power", "The Operation"][i - 1] if i else None, 1)
    table(9, [("tab-IX", "IX-face.dc.html", "Tabula IX", None)],
          [(loose("loose-ix", "Loose · Tabula IX", [("Slip-H.dc.html", 440, "Slip H · the quiet instrument", None)], 42),
            "Slip H · the quiet instrument")])
    table(10, [("tab-X", "X-face.dc.html", "Tabula X", None)])
    table(11, [("tab-XI", "XI-face.dc.html", "Tabula XI", None), ("tab-XI-verso", "XI-verso.dc.html", "Verso", None)],
          [(loose("loose-xi", "Loose · Tabula XI",
                  [("XI-strip-front.dc.html", 470, "Border strip · front", None),
                   ("XI-strip-back.dc.html", 860, "Border strip · reverse", None)], 43),
            "Border strip, front and reverse")])
    table(12, [("tab-XII", "XII-face.dc.html", "Tabula XII", None)])
    table(13, [("tab-XIII", "XIII-face.dc.html", "Tabula XIII", None),
               ("tab-XIII-verso", "XIII-verso.dc.html", "Verso", None)],
          [(loose("loose-xiii", "Loose · Tabula XIII",
                  [("Key-legacy.dc.html", 230, None, None),
                   ("Slip-I.dc.html", 804, "Slip I · from a receipt for the revised seal", None)], 44),
            "Proof slip and slip I")])
    add(etexts("debts", "debts"), "Debts")
    add(etexts("refs", "refs"), "References")
    return pages, toc


# ------------------------------------------------------------------ raster plates

def rasterize(pw):
    br = pw.chromium.launch()
    ctx = br.new_context(viewport={"width": 1000, "height": 1600}, device_scale_factor=RASTER_SCALE)
    pg = ctx.new_page()
    for name, bg in RASTER_BOARDS.items():
        out = P.WORK + name.replace(".svg", ".jpg")
        if not os.path.exists(out):
            html = (f'<html><body style="margin:0;background:{bg}"><img src="{P.furl(P.ASSETS + name)}" '
                    f'style="display:block;width:1000px;height:1600px"></body></html>')
            open(P.WORK + "r.html", "w").write(html)
            pg.goto("file://" + P.WORK + "r.html")
            pg.wait_for_load_state("load")
            pg.screenshot(path=out, type="jpeg", quality=86)
        P.RASTER[name] = out
    br.close()


def finish(toc):
    """scale to 6.2 x 8.27 in, point the named destinations at whole pages, add the outline and metadata"""
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import ArrayObject, NameObject
    w = PdfWriter(clone_from=PdfReader(RAW_PDF))
    for page in w.pages:
        page.scale_by(P.SCALE)
        mb = page.mediabox
        for box in ("cropbox", "trimbox", "bleedbox", "artbox"):    # defaults would be scaled a second time
            setattr(page, box, mb)
        page.compress_content_streams()
    dests = w._root_object.get("/Dests")
    if dests is not None:
        dests = dests.get_object()
        for k in list(dests.keys()):
            arr = dests[k].get_object() if hasattr(dests[k], "get_object") else dests[k]
            dests[NameObject(k)] = ArrayObject([arr[0], NameObject("/Fit")])
    parents = {}
    for label, idx, level in toc:
        item = w.add_outline_item(label, idx, parent=parents.get(level - 1) if level else None)
        parents[level] = item
    w.add_metadata({"/Title": "Clavicula Matricis",
                    "/Subject": "Revisable Systems Practice, Revision 5, set out in thirteen tables, "
                                "with its text, its debts and a bound-in tract. E-reader edition, 3:4.",
                    "/Keywords": "Clavicula Matricis; Revisable Systems Practice; Revision 5; grimoire",
                    "/Creator": "Chromium; pypdf"})
    w.page_layout = "/SinglePage"
    with open(P.WORK + "scaled.pdf", "wb") as f:
        w.write(f)
    import subprocess
    subprocess.run(["qpdf", "--compress-streams=y", "--recompress-flate", "--object-streams=generate",
                    P.WORK + "scaled.pdf", OUT_PDF], check=True)


def main():
    from playwright.sync_api import sync_playwright
    os.makedirs(P.WORK, exist_ok=True)
    with sync_playwright() as pw:
        rasterize(pw)
        pages, toc = volume()
        doc = P.document(pages)
        open(P.WORK + "book.html", "w").write(doc)
        br = pw.chromium.launch()
        pg = br.new_page()
        pg.goto("file://" + P.WORK + "book.html")
        pg.wait_for_load_state("load")
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(800)
        meas = pg.evaluate(P.MEASURE_JS)
        ids = pg.evaluate("() => Array.from(document.querySelectorAll('section.pg')).map(s => s.id)")
        pg.pdf(path=RAW_PDF, prefer_css_page_size=True, print_background=True)
        br.close()
    json.dump(dict(toc=toc, ids=ids, meas=meas), open(P.WORK + "build.json", "w"))
    print("pages", len(pages), "sections", len(ids))
    finish(toc)


if __name__ == "__main__":
    main()
