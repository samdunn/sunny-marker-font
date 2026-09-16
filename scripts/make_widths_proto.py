#!/usr/bin/env python3
"""Width-axis prototype: Condensed (0.78x) and Extended (1.22x) at Regular
weight, with stroke-preserving anisotropic scaling and recomputed spacing.
"""
import build_font
import spacing

WIDTHS = [
    ("Condensed", 0.78, 3),   # usWidthClass 3
    ("Extended", 1.22, 7),    # usWidthClass 7
]

for style, ws, wclass in WIDTHS:
    contours, widths, xheight = build_font.build_glyphs(
        offset=0.0, style=style, width_scale=ws)
    polys = build_font.glyph_polys(contours)
    profiles = {}
    for name, ps in polys.items():
        l, r = spacing.glyph_profiles(ps)
        ys = [p[1] for pp in ps for p in pp]
        profiles[name] = (l, r, min(ys), max(ys))
    # narrower letters want proportionally narrower margins
    gap_w = spacing.GAP * (0.80 if ws < 1 else 1.12)
    sbs = spacing.compute_sidebearings(profiles, widths, xheight, gap=gap_w)
    kern = spacing.compute_kerning(profiles, widths, sbs,
                                   spacing.kern_candidates(), gap=gap_w)
    emit = sorted(set(p for p, v in kern.items()
                      if abs(v) >= spacing.KERN_THRESH)
                  | set(spacing.KERN_OVERRIDES))
    fea = spacing.kern_feature(kern, emit)
    out = build_font.assemble_font(contours, widths, xheight, sbs, fea,
                                   style=style, weight_class=400)
    # patch width class
    from fontTools.ttLib import TTFont
    f = TTFont(out)
    f["OS/2"].usWidthClass = wclass
    f.save(out)
    print("done", style)
