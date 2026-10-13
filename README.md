# Clavicula Matricis

*or, the Little Key of the Matrix*

Revisable Systems Practice, Revision 5 (10 October 2026), set out in thirteen tables by three workshops (the retained impression, the deposited arrangement and the repeated instruction), with the leaves of its text, its debts, and a tract of another stock, *Vis Maior*, bound in after the eighth table.

It is an art object. The text is real and the diagrams are meant to work as process diagrams. The glyphs, the hands and the tract are invented.

## Contents

- `pdf/Clavicula_Matricis_ereader.pdf`: the e-reader edition. 64 pages at 3:4 (6.2 × 8.27 in), with linked index and bookmarks.
- `canvas/project/`: the artboards as published on the design canvas, one `.dc.html` per leaf, plus `canvas.json` for reading order.
- `canvas/assets/`: the drawn layer of each leaf as SVG. Text is set over it in HTML.
- `generator/`: the Python that draws everything.
- `generator/src/`: the Revision 5 source text as JSON blocks.
- `generator/out/`: generated SVGs and text-box JSON.
- `fonts/`: the typefaces (OFL / Apache). `fonts/static/` holds a weight-400 instance of EB Garamond so PDFs embed TrueType, not Type 3.
- [`plotter/`](plotter/README.md): a two-pen, stroke-only edition of *Of the Closed Neck*, with A4 black/red SVG passes, a registration/test sheet and a portable exporter. Digitally checked; awaiting an iDraw trial.

## Generator map

| Module | What it does |
|---|---|
| `core.py`, `marks.py` | SVG document, hand-drawn stroke model, the twelve sketching marks and ornaments |
| `layout.py`, `ptext.py`, `preview.py` | text boxes: measuring and wrapping with PIL, HTML output, raster previews |
| `hands.py`, `tx.py`, `cipher.py` | the recurring hands, the transcription hand, the ciphers |
| `eng.py`, `meal.py` | engraving and cornmeal workshop furniture |
| `plate_*.py`, `ii.py`, `iv.py`, `vi.py`, `xi.py`, `v2_*.py` | the thirteen tables, their versos and facing leaves |
| `slips.py` | proof sheets and slips H and I |
| `fm.py` | *Vis Maior* |
| `front.py` | title leaf and index |
| `leaf.py`, `build_text.py` | text leaves for the canvas (1000 × 1600) |
| `etext.py`, `build_etext.py` | text reset for the e-reader page (1200 × 1600) |
| `artboard2.py`, `gen_html_*.py`, `build_v2.py` | canvas artboards |
| `pdfbuild.py`, `make_pdf.py` | the PDF: Chromium print with local fonts, then pypdf scale, outline and links |

## Building

Paths are still hard-coded to the original workspace (`/home/claude/grim`, `/home/claude/fonts`, and a scratchpad directory). Adjust them before running. Requirements: Python 3, Pillow, cairosvg, shapely, fontTools, pypdf, Playwright with Chromium, and qpdf.

Rough order: the plate modules and `build_v2.py`, then `build_text.py`, then `gen_html_*.py` (canvas), then `build_etext.py`, then `make_pdf.py`.

No one needs permission to stop using it.
