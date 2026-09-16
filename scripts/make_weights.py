#!/usr/bin/env python3
"""Build all Sunny Marker statics: 5 weights x upright/italic, with optical
sidebearings and geometry-derived GPOS kerning per style.

The kern pair *emission list* is fixed from Regular upright (pairs whose
Regular value exceeds the threshold), so every static and every VF master
shares an identical GPOS structure - required for varLib merging.
"""
import os
from master_data import save_master_data
import numpy as np
from PIL import Image
from scipy import ndimage

import build_font
import spacing

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# measure regular stroke width in font units (see README)
import json
man = json.load(open(build_font.MANIFEST))
sheet = Image.open(build_font.SHEET).convert("L")
strokes = []
for row in man["rows"]:
    for g in row["glyphs"]:
        if g["name"] in ("l.lc", "I", "exclam"):
            crop = np.asarray(sheet.crop((g["x0"], g["y0"], g["x1"], g["y1"])))
            d = ndimage.distance_transform_edt(crop < 128)
            strokes.append(2 * d.max())
rows = man["rows"]


def med(row, names, key):
    return float(np.median([g[key] for g in row["glyphs"] if g["name"] in names]))


cap_px = ((med(rows[0], set("ABCDEFGHIJKLMN"), "y1")
           - med(rows[0], set("ABCDEFGHIJKLMN"), "y0"))
          + (med(rows[1], set("OPRSTUVWXYZ"), "y1")
             - med(rows[1], set("OPRSTUVWXYZ"), "y0"))) / 2
S = float(np.median(strokes)) * build_font.CAP / cap_px
print(f"stroke {S:.0f} units")

# Heavy (900, 1.45x) removed for now — never looked right even with
# counter/aperture protection; the family tops out at Bold until a
# proper black master is drawn
WEIGHTS = [
    ("Light", 300, 0.70),
    ("Regular", 400, 1.00),
    ("Medium", 500, 1.15),
    ("Bold", 700, 1.30),
]

# ---- pass 1: trace all weights ----
traced = {}
for style, wclass, mult in WEIGHTS:
    offset = (mult - 1.0) * S / 2.0
    contours, widths, xheight = build_font.build_glyphs(offset=offset,
                                                        style=style)
    traced[style] = {"offset": offset, "weight_class": wclass,
                     "contours": contours, "widths": widths,
                     "xheight": xheight}

# ---- pass 2: spacing/kerning; emission list from Regular upright ----
pairs = spacing.kern_candidates()
emit_pairs = None
master_data = {}

for italic in (False, True):
    for style, wclass, mult in WEIGHTS:
        t = traced[style]
        contours, widths = t["contours"], t["widths"]
        if italic:
            contours, widths = build_font.shear_glyphs(contours, widths)
        polys = build_font.glyph_polys(contours)
        profiles = {}
        for name, ps in polys.items():
            l, r = spacing.glyph_profiles(ps)
            ys = [p[1] for pp in ps for p in pp]
            profiles[name] = (l, r, min(ys), max(ys))
        # bolder styles run tighter: scale the target margin with the offset
        gap_w = spacing.GAP - 0.25 * t["offset"]
        sbs = spacing.compute_sidebearings(profiles, widths, t["xheight"],
                                           gap=gap_w)
        fscale = ((124 + 2 * t["offset"]) / 124) ** 0.5
        kern = spacing.compute_kerning(profiles, widths, sbs, pairs,
                                       gap=gap_w, floor_scale=fscale)
        key = ("Italic-" if italic else "") + style
        master_data[key] = {"offset": t["offset"], "weight_class": wclass,
                            "contours": contours, "widths": widths,
                            "sbs": sbs, "kern": kern,
                            "xheight": t["xheight"]}

# emission list from Regular upright values + all craft overrides
reg_kern = master_data["Regular"]["kern"]
emit_pairs = sorted(set(p for p, v in reg_kern.items()
                        if abs(v) >= spacing.KERN_THRESH)
                    | set(spacing.KERN_OVERRIDES))
print(f"kern pairs emitted: {len(emit_pairs)}")

for italic in (False, True):
    for style, wclass, mult in WEIGHTS:
        key = ("Italic-" if italic else "") + style
        m = master_data[key]
        fea = spacing.kern_feature(m["kern"], emit_pairs)
        build_font.assemble_font(m["contours"], m["widths"], m["xheight"],
                                 m["sbs"], fea, style=style,
                                 weight_class=wclass, italic=italic)

save_master_data(os.path.join(ROOT, "build", "masters.json"),
                 {"masters": master_data, "emit_pairs": emit_pairs, "stroke": S})
print("saved master data for VF step")
