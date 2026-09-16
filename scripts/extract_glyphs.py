#!/usr/bin/env python3
"""Extract individual glyph images from the Sunny Marker glyph grid sheet.

Segments the sheet into rows by horizontal ink projection, then splits each
row into glyphs by connected components merged across small horizontal gaps.
Validates each row against the expected character sequence and writes
per-glyph PNGs plus a manifest with pixel geometry for the font build step.
"""
import json
import os
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHEET = os.path.join(ROOT, "references", "glyph-grid.png")
OUT_PNG = os.path.join(ROOT, "glyphs", "png")
MANIFEST = os.path.join(ROOT, "glyphs", "manifest.json")

# Expected glyph rows, top to bottom (label rows are auto-skipped by height).
ROWS = [
    list("ABCDEFGHIJKLMN"),
    list("OPQRSTUVWXYZ"),
    list("abcdefghijklmn"),
    list("opqrstuvwxyz"),
    list("0123456789"),
    ["exclam", "question", "period", "comma", "semicolon", "semicolon.alt",
     "quotedbl", "parenleft", "parenright", "bracketleft", "bracketright",
     "braceleft", "slash", "backslash"],
    ["hyphen", "underscore", "plus", "equal", "at", "numbersign", "dollar",
     "percent", "ampersand", "asterisk", "less", "greater"],
    ["arrowright", "arrowupright", "arrowup", "arrowupleft", "arrowleft",
     "arrowdownright", "arrowdown", "arrowdownleft", "star", "sparkle",
     "heart", "sun", "check", "cross"],
]

NAME_FOR_CHAR = {}  # filled below for A-Z a-z 0-9
for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    NAME_FOR_CHAR[c] = c
for c in "abcdefghijklmnopqrstuvwxyz":
    NAME_FOR_CHAR[c] = c + ".lc"  # avoid case-insensitive filename clashes
for c in "0123456789":
    NAME_FOR_CHAR[c] = "digit" + c


def main():
    im = Image.open(SHEET).convert("L")
    a = np.asarray(im)
    ink = a < 128  # black glyphs on white

    # --- find rows by horizontal projection ---
    rowsum = ink.sum(axis=1)
    has_ink = rowsum > 2
    bands = []
    y = 0
    H = len(has_ink)
    while y < H:
        if has_ink[y]:
            y0 = y
            while y < H and (has_ink[y] or (y + 4 < H and has_ink[y:y + 4].any())):
                y += 1
            bands.append((y0, y))
        else:
            y += 1
    # classify: label bands are short, glyph bands tall
    heights = [b[1] - b[0] for b in bands]
    print("bands:", [(b[0], b[1], b[1] - b[0]) for b in bands])
    glyph_bands = [b for b in bands if (b[1] - b[0]) > 35]
    print(f"{len(glyph_bands)} glyph bands (expected {len(ROWS)})")
    assert len(glyph_bands) == len(ROWS), "row segmentation mismatch"

    os.makedirs(OUT_PNG, exist_ok=True)
    manifest = {"sheet": "references/glyph-grid.png", "rows": []}

    for ri, ((y0, y1), expected) in enumerate(zip(glyph_bands, ROWS)):
        band = ink[y0:y1]
        lab, n = ndimage.label(band)
        objs = ndimage.find_objects(lab)
        comps = []
        for i, sl in enumerate(objs):
            if sl is None:
                continue
            ys, xs = sl
            area = (lab[sl] == (i + 1)).sum()
            if area < 12:  # noise specks
                continue
            comps.append([xs.start, xs.stop, ys.start, ys.stop, i + 1])
        comps.sort(key=lambda c: c[0])

        # merge components separated by small horizontal gap (multi-part glyphs)
        merged = []
        GAP = 18
        for c in comps:
            if merged and c[0] - merged[-1][1] < GAP:
                m = merged[-1]
                m[1] = max(m[1], c[1])
                m[2] = min(m[2], c[2])
                m[3] = max(m[3], c[3])
                m[4].append(c[4])
            else:
                merged.append([c[0], c[1], c[2], c[3], [c[4]]])

        print(f"row {ri}: {len(merged)} glyphs (expected {len(expected)})")
        if len(merged) != len(expected):
            for m in merged:
                print("   x", m[0], "-", m[1], "w", m[1] - m[0])
            raise SystemExit(f"row {ri} glyph count mismatch")

        row_entry = {"band": [int(y0), int(y1)], "glyphs": []}
        for gi, (m, name) in enumerate(zip(merged, expected)):
            x0, x1, gy0, gy1, labels = m
            mask = np.isin(lab[gy0:gy1, x0:x1], labels)
            gname = NAME_FOR_CHAR.get(name, name)
            # save padded binary png (black ink on white)
            pad = 4
            out = np.full((mask.shape[0] + 2 * pad, mask.shape[1] + 2 * pad), 255, np.uint8)
            out[pad:-pad, pad:-pad] = np.where(mask, 0, 255)
            Image.fromarray(out).save(os.path.join(OUT_PNG, gname + ".png"))
            row_entry["glyphs"].append({
                "name": gname,
                "x0": int(x0), "x1": int(x1),
                "y0": int(y0 + gy0), "y1": int(y0 + gy1),
                "pad": pad,
            })
        manifest["rows"].append(row_entry)

    with open(MANIFEST, "w") as f:
        json.dump(manifest, f, indent=1)
    print("wrote", MANIFEST)


if __name__ == "__main__":
    main()
