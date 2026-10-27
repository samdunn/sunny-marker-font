"""Draw the vertical caron (ď ľ ť Ľ) as a marker stroke in every master.

Through 1.314 `caroncomb.alt` was one fixed wedge, about 19 units thick in
every weight, while every other mark is a 57-89 unit marker stroke. Here each
master's mark is made from that master's own acute, at 85% of the weight of
its apostrophe: the top cap slides down the stroke until the mark is 160
units tall, then the stroke stands upright with a slight lean (plus the
italic slant). That is 30 units taller than the old wedge, so the heavier
stroke still reads as a tick rather than a dot. The mark keeps the acute's
point structure, so the masters stay compatible, and its `_side` anchor, so
mark positioning is unchanged.

The mark keeps the old wedge's left edge, so its gap to the stem does not
shrink. Where the heavier mark then reaches past the advance, the four
accented letters get just enough extra advance for a small right sidebearing.

usage: redraw_vertical_caron.py SOURCES [--report PATH]
"""
import argparse
import json
import math
from pathlib import Path

import numpy as np
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.perimeterPen import PerimeterPen
from ufoLib2 import Font

REFERENCE = "master-Roman-Regular-w100-o36.ufo"
LEAN_DEGREES = 10  # the old wedge's lean, top to the right
SLANT_DEGREES = 9
BOTTOM, HEIGHT = -14.0, 160.0  # the old wedge ran from 6 to 135.8
WEIGHT = 0.85  # stroke weight relative to the apostrophe
COMPOSITES = ("Lcaron", "dcaron", "lcaron", "tcaron")
RIGHT_SIDEBEARING = 12.0  # minimum room after the mark, font units


def stroke_width(font, name):
    """Mean thickness of a one-stroke glyph: twice its area over its perimeter."""
    area, perimeter = AreaPen(font), PerimeterPen(font)
    font[name].draw(area)
    font[name].draw(perimeter)
    return 2 * abs(area.value) / perimeter.value


def points(contour):
    return np.array([(p.x, p.y) for p in contour.points], float)


def owners(contour):
    """Index of the on-curve point each point moves with."""
    pts = contour.points
    n = len(pts)
    own = []
    for i, p in enumerate(pts):
        if p.segmentType is not None:
            own.append(i)
        elif pts[(i - 1) % n].segmentType is not None:
            own.append((i - 1) % n)  # first handle: belongs to the start
        else:
            own.append((i + 1) % n)  # second handle: belongs to the end
    return own


def axis(xy):
    centred = xy - xy.mean(0)
    _, _, vt = np.linalg.svd(centred, full_matrices=False)
    u = vt[0]
    return u if u[1] > 0 else -u


def outline_bounds(xy, types):
    """Exact bounds of a closed cubic contour given as UFO points."""
    n = len(xy)
    on = [i for i in range(n) if types[i] is not None]
    pen = BoundsPen(None)
    start = on[-1]
    pen.moveTo(tuple(xy[start]))
    i = (start + 1) % n
    buffer = []
    for _ in range(n):
        if types[i] is None:
            buffer.append(tuple(xy[i]))
        else:
            if buffer:
                pen.curveTo(*buffer, tuple(xy[i]))
            else:
                pen.lineTo(tuple(xy[i]))
            buffer = []
        i = (i + 1) % n
    pen.closePath()
    return pen.bounds


def build(acute_xy, types, top, lean, bottom=BOTTOM, height=HEIGHT):
    """Shorten, stand up and place one master's acute as the vertical caron."""
    u = axis(acute_xy)
    target = np.array([math.sin(math.radians(lean)), math.cos(math.radians(lean))])
    angle = math.atan2(target[1], target[0]) - math.atan2(u[1], u[0])
    rot = np.array([[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]])

    def shape(shift):
        xy = acute_xy.copy()
        xy[top] -= shift * u
        xy = (xy - xy.mean(0)) @ rot.T
        return xy

    lo, hi = 0.0, 400.0
    for _ in range(60):
        mid = (lo + hi) / 2
        b = outline_bounds(shape(mid), types)
        if b[3] - b[1] > height:
            lo = mid
        else:
            hi = mid
    xy = shape(hi)
    b = outline_bounds(xy, types)
    return xy - np.array([b[0], b[1] - bottom])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--bottom", type=float, default=BOTTOM)
    parser.add_argument("--height", type=float, default=HEIGHT)
    parser.add_argument("--weight", type=float, default=WEIGHT)
    args = parser.parse_args()
    paths = sorted(args.sources.glob("master-*.ufo"))
    fonts = {p.name: Font.open(p) for p in paths}

    ref = fonts[REFERENCE]["acutecomb"].contours[0]
    ref_xy = points(ref)
    own = owners(ref)
    u = axis(ref_xy)
    centre = ref_xy.mean(0)
    on_top = {i for i, p in enumerate(ref.points) if p.segmentType and (ref_xy[i] - centre) @ u > 0}
    top = np.array([i for i in range(len(own)) if own[i] in on_top])
    types = [p.segmentType for p in ref.points]

    report = {}
    for name, font in fonts.items():
        acute = font["acutecomb"].contours[0]
        assert [p.segmentType for p in acute.points] == types, name
        mark = font["caroncomb.alt"]
        old = mark.contours[0]
        old_left = outline_bounds(points(old), [p.segmentType for p in old.points])[0]
        lean = LEAN_DEGREES + (SLANT_DEGREES if "Italic" in name else 0)
        scale = args.weight * stroke_width(font, "quoteright") / stroke_width(font, "acutecomb")
        xy = build(points(acute) * scale, types, top, lean, args.bottom, args.height)
        xy[:, 0] += old_left
        mark.clearContours()
        pen = mark.getPointPen()
        pen.beginPath()
        for (x, y), t in zip(xy, types):
            pen.addPoint((round(float(x), 3), round(float(y), 3)), segmentType=t)
        pen.endPath()
        right = outline_bounds(xy, types)[2]
        entry = {"right_edge": round(float(right), 1), "scale": round(scale, 3)}
        side = next(a for a in mark.anchors if a.name == "_side")
        for comp_name in COMPOSITES:
            glyph = font[comp_name]
            comp = next(c for c in glyph.components if c.baseGlyph == "caroncomb.alt")
            needed = comp.transformation[4] + right + RIGHT_SIDEBEARING
            old_width = glyph.width
            if needed > glyph.width:
                glyph.width = math.ceil(needed)
            entry[comp_name] = {"width": [old_width, glyph.width]}
        report[name] = entry
        font.save(paths[[p.name for p in paths].index(name)], overwrite=True)
        assert (side.x, side.y) == (0, 125), (name, side.x, side.y)
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + "\n")
    widened = sorted({c for e in report.values() for c in COMPOSITES if e[c]["width"][0] != e[c]["width"][1]})
    print(f"Redrew caroncomb.alt in {len(fonts)} masters; wider advance: {widened or 'none'}")


if __name__ == "__main__":
    main()
