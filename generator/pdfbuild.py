"""Pieces for the e-reader PDF: local fonts, facsimile boards from the canvas, reset text leaves, Chromium."""
import json
import os
import re
import sys
from urllib.parse import quote

sys.path.insert(0, "/home/claude/grim")
from layout import html_box
import etext as L

SCR = "/tmp/claude-0/-home-claude/f25d994f-f4dc-5e27-83bc-deb2f1661cca/scratchpad/"
PROJ = SCR + "canvas/project/"
ASSETS = SCR + "canvas/assets/"
WORK = SCR + "pdf/"
FONTDIR = "/home/claude/fonts/"
ETEXT = "/home/claude/grim/out/etext/"
PW, PH = 1200, 1600
SCALE = 0.496                      # 6.2 in = 595.2 css px over 1200 units
PAGE_IN = (6.2, 8.2667)
PAL = {"red": L.RED, "ink": L.INK}

FACES = [
    ("IM Fell English", "normal", "400", "IMFeENrm28P.ttf"),
    ("IM Fell English", "italic", "400", "IMFeENit28P.ttf"),
    ("IM Fell English SC", "normal", "400", "IMFeENsc28P.ttf"),
    ("IM Fell DW Pica", "normal", "400", "IMFePIrm28P.ttf"),
    ("IM Fell DW Pica", "italic", "400", "IMFePIit28P.ttf"),
    ("IM Fell DW Pica SC", "normal", "400", "IMFePIsc28P.ttf"),
    ("EB Garamond", "normal", "400", "static/EBGaramond-Regular400.ttf"),
    ("EB Garamond", "italic", "400", "static/EBGaramond-Italic400.ttf"),
    ("Spectral", "normal", "400", "Spectral-Regular.ttf"),
    ("Spectral", "normal", "500", "Spectral-Medium.ttf"),
    ("Spectral", "italic", "400", "Spectral-Italic.ttf"),
    ("Spectral SC", "normal", "400", "SpectralSC-Regular.ttf"),
    ("Spectral SC", "normal", "500", "SpectralSC-Medium.ttf"),
    ("DM Serif Display", "normal", "400", "DMSerifDisplay-Regular.ttf"),
    ("DM Serif Display", "italic", "400", "DMSerifDisplay-Italic.ttf"),
    ("IBM Plex Mono", "normal", "400", "IBMPlexMono-Regular.ttf"),
    ("IBM Plex Mono", "normal", "500", "IBMPlexMono-Medium.ttf"),
    ("IBM Plex Mono", "italic", "400", "IBMPlexMono-Italic.ttf"),
    ("Sue Ellen Francisco", "normal", "400", "SueEllenFrancisco-Regular.ttf"),
    ("Zeyada", "normal", "400", "Zeyada.ttf"),
    ("Cutive Mono", "normal", "400", "CutiveMono-Regular.ttf"),
    ("Special Elite", "normal", "400", "SpecialElite-Regular.ttf"),
    ("UnifrakturMaguntia", "normal", "400", "UnifrakturMaguntia-Book.ttf"),
]


def furl(path):
    return "file://" + quote(path)


def font_css():
    return "\n".join(f"@font-face{{font-family:'{f}';font-style:{st};font-weight:{wt};"
                     f"src:url('{furl(FONTDIR + fn)}') format('truetype');}}" for f, st, wt, fn in FACES)


def page_css():
    """pages are printed at their design size, 1200 x 1600 css px, and scaled to 6.2 in afterwards: a transformed
    box taller than the page would be fragmented by its untransformed height"""
    return f"""
@page {{ size: {PW}px {PH}px; margin: 0 }}
html, body {{ margin: 0; padding: 0; background: #ffffff }}
.pg {{ position: relative; width: {PW}px; height: {PH}px; overflow: hidden; contain: strict; break-after: page; break-inside: avoid }}
.pg:last-child {{ break-after: auto }}
.cv {{ position: absolute; left: 0; top: 0; width: {PW}px; height: {PH}px; overflow: hidden }}
.cv a {{ display: block; position: absolute }}
p {{ margin: 0 }}
"""


# ------------------------------------------------------------------ blobs

def _pairs(src, var):
    body = src.split(var + " = {", 1)[1].split("}", 1)[0]
    return dict(re.findall(r'"(\w+)":\s*"([0-9a-f]{32})"', body))


def blob_map():
    m = {
        "e03d0f9a767c92384f70365cca97f837": "v2_viii_face.svg",
        "59539f70fc01137e0749d2aa94fdb7c5": "v2_viii_verso.svg",
        "2d3f508f24922aeeb7c8a5381d9e2079": "v2_iii_face.svg",
        "de284f098fa4523cb2c7066ecfedce03": "v2_iii_slip.svg",
        "c0a27142a86b4f6b811f3f94993cb098": "v2_xiii_face.svg",
        "9d7453f62877e44ff32b7c47acf0a9bd": "v2_xiii_verso.svg",
        "dd0e4902c40482cc9df1563b9986f7ce": "v2_keyslip.svg",
    }
    for k, v in _pairs(open("/home/claude/grim/gen_html_b.py").read(), "BLOB").items():
        m[v] = k + ".svg"
    for k, v in _pairs(open("/home/claude/grim/gen_html_c.py").read(), "B").items():
        m[v] = "v3_" + k + ".svg"
    for v in m.values():
        assert os.path.exists(ASSETS + v), v
    return m


BLOBS = blob_map()
RASTER = {}          # asset svg name -> local jpeg path (filled by rasterize())


# ------------------------------------------------------------------ boards

ROOT = re.compile(r'<div style="position: relative; width: (\d+)px; height: (\d+)px; overflow: hidden; '
                  r'background: ([^;]+); color: ([^;]+); font-family: ([^"]+)">')


def board(fname, state=None, extra=""):
    s = open(PROJ + fname).read()
    m = ROOT.search(s)
    W, Hh, bg, ink, ff = int(m[1]), int(m[2]), m[3], m[4], m[5]
    inner = s[m.end():s.rindex("</div>\n</x-dc>")]
    imgs = []

    def src(mm):
        name = BLOBS[mm[1]]
        imgs.append(name)
        return 'src="' + (furl(RASTER[name]) if name in RASTER else furl(ASSETS + name)) + '"'

    inner = re.sub(r'src="/_blob/([0-9a-f]{32})"', src, inner)
    if "<sc-if" in inner:
        def rep(mm):
            return mm[2] if mm[1] == (state or "closed") else ""
        inner = re.sub(r'<sc-if value="\{\{ (\w+) \}\}"[^>]*>(.*?)</sc-if>', rep, inner, flags=re.S)
        inner = re.sub(r' onClick="\{\{ \w+ \}\}"', "", inner).replace("cursor: pointer", "cursor: default")
    return dict(W=W, H=Hh, bg=bg, ink=ink, ff=ff, inner=inner + extra, imgs=imgs, name=fname)


def place(b, x, y, s, clip=None, shadow=False):
    """board b drawn at (x, y) on the 1200x1600 page at scale s; clip = (cx, cy, cw, ch) in board units"""
    cx, cy, cw, ch = clip or (0, 0, b["W"], b["H"])
    sh = " box-shadow: 0 2px 9px rgba(60,42,18,0.30);" if shadow else ""
    return (f'<div style="position: absolute; left: {x:g}px; top: {y:g}px; width: {cw}px; height: {ch}px; overflow: hidden; '
            f'transform-origin: 0 0; transform: scale({s:g});{sh}">'
            f'<div style="position: absolute; left: {-cx}px; top: {-cy}px; width: {b["W"]}px; height: {b["H"]}px; '
            f'overflow: hidden; background: {b["bg"]}; color: {b["ink"]}; font-family: {b["ff"]}">'
            f'{b["inner"]}</div></div>')


# ------------------------------------------------------------------ text leaves

def tagged(bx, html):
    return html.replace("<div style=", f'<div data-id="{bx["id"]}" style=', 1)


def etext_body(name, links=()):
    B = json.load(open(ETEXT + name + ".json"))
    out = [f'<img src="{furl(ETEXT + name + ".svg")}" alt="" style="position: absolute; left: 0; top: 0; '
           f'width: {PW}px; height: {PH}px">']
    for b in B:
        out.append(tagged(b, html_box(b, PAL, indent="")))
    for (x, y, w, h, href) in links:
        out.append(f'<a href="{href}" style="left: {x}px; top: {y}px; width: {w}px; height: {h}px"></a>')
    return "".join(out), B


def page_html(pid, bg, body):
    return f'<section class="pg" id="{pid}" style="background: {bg}"><div class="cv">{body}</div></section>'


def document(pages, title="Clavicula Matricis"):
    return ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><title>" + title + "</title><style>"
            + font_css() + page_css() + "</style></head><body>" + "\n".join(pages) + "</body></html>")


MEASURE_JS = """() => {
  const out = [];
  document.querySelectorAll('section.pg').forEach((sec, i) => {
    sec.querySelectorAll('[data-id]').forEach(el => {
      out.push({page: sec.id, i: i, id: el.dataset.id, top: el.offsetTop, h: el.offsetHeight, w: el.offsetWidth,
                sw: el.scrollWidth});
    });
  });
  return out;
}"""
