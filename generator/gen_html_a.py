import json, sys
sys.path.insert(0, '/home/claude/grim')
from artboard2 import page
import hands as Hd
O = '/home/claude/grim/out/'
v8 = json.load(open(O+'v2_viii_boxes.json')); v3 = json.load(open(O+'v2_iii_boxes.json')); v13 = json.load(open(O+'v2_xiii_boxes.json'))
P8 = {'red': Hd.RED, 'ink': Hd.INK}
import v2_iii, v2_xiii
P3 = {'red': v2_iii.PENS['rr'], 'ink': v2_iii.PENS['dk']}
P13 = {'red': v2_xiii.OCHRE, 'ink': v2_xiii.MEAL}
pages = {
 'VIII-face': page('Tabula VIII — Of an Outage Delayed by Authority (second pass)', v8['face_boxes'], P8, '#ebe1c8', Hd.INK,
   '/_blob/e03d0f9a767c92384f70365cca97f837',
   'Engraved plate within its plate mark: an escalation route runs down from the NOC through a required gate and a horned executive triangle, waits on a ladder, then reaches technical dispatch, the field crew and the fiber break. A vermilion added route leaves just below the NOC and arrives at dispatch. Rulers mark two timestamp intervals; typed labels name the NOC and technical dispatch.', 'IM FELL DW Pica'),
 'VIII-record': page('Facing record to Tabula VIII', v8['verso_boxes'], P8, '#ebe1c8', Hd.INK, '/_blob/59539f70fc01137e0749d2aa94fdb7c5',
   'Facing record with a small red route beside the deposition and a key of the marks used on the plate.', 'IM FELL DW Pica'),
 'III-face': page('Tabula III — Of the Speed of Correction (second pass)', v3['face_boxes'], P3, v2_iii.PAPER, v2_iii.PENS['dk'],
   '/_blob/2d3f508f24922aeeb7c8a5381d9e2079',
   'A plotter drawing on cream stock: a horned figure with raised arms and a spiral on its torso stands in a square of sixteen triangular cells, lightly and evenly hatched. One diagonal was plotted against the wrong origin and re-plotted in rust red; two registration witnesses record the error. The two cells of unknowns carry hollow circles. A legacy-hand inscription runs round the frame; a pen-test strip sits at the foot.', 'Spectral'),
 'III-slip': page('Facing slip to Tabula III', v3['slip_boxes'], P3, v2_iii.PAPER, v2_iii.PENS['dk'], '/_blob/de284f098fa4523cb2c7066ecfedce03',
   'Facing slip ruled for text, with registration witnesses at two corners.', 'Spectral'),
 'XIII-face': page('Tabula XIII — Of the Twelve Marks and the Mark (second pass)', v13['face_boxes'], P13, v2_xiii.PAPER, v2_xiii.MEAL,
   '/_blob/c0a27142a86b4f6b811f3f94993cb098',
   'A mounted record of a cornmeal deposit on dark earth, held by paper corners: twelve medallions, one per sketching mark, some with thin or partial outer deposits and one border visibly refilled; below, a great seal holding the open, branching spiral in red ochre.', 'EB Garamond'),
 'XIII-verso': page('Verso of Tabula XIII', v13['verso_boxes'], P8, '#ebe1c8', Hd.INK, '/_blob/9d7453f62877e44ff32b7c47acf0a9bd',
   'Verso with the open spiral beside its paragraph and mark XII beside an objection.', 'EB Garamond'),
 'Key-legacy': page('Proof slip — the legacy hand', v13['key_boxes'], P8, '#ebe1c8', Hd.INK, '/_blob/dd0e4902c40482cc9df1563b9986f7ce',
   'The twenty-six glyphs of the legacy hand, each above its letter.', 'EB Garamond', W=1000, Hh=440),
}
for k, v in pages.items():
    open(O + k + '.dc.html', 'w').write(v)
    print(k, len(v))
