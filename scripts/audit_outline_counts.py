"""Count outline points and short or colinear segments, with no reporting cap.

Fontspector's outline checks stop listing findings after 100 per font and then
report PASS, so a busy font and a clean one can both pass. This counts every
finding, using the same rules:

- short segment: under 3 units or under 0.6% of its contour's length, after a
  line or as a curve (outline_short_segments);
- colinear: two consecutive lines turning less than 0.1 rad (outline_colinear_vectors).

TrueType curves are split at their implied on-curve points, as the checker
does, and each finding says whether it is a piece of one such curve.

Points are counted per character at each font's default location, with
components decomposed, over the characters every given font contains.
Segments are counted in static instances: every axis corner plus the default.

usage: audit_outline_counts.py --font LABEL FONT [--font LABEL FONT ...] [--out PATH]
Repeat a label to add its italic. The first font given for each label is used
for points; all of them for segments.
"""
import argparse
import collections
import itertools
import json
import math
import statistics
from pathlib import Path

from fontTools.pens.basePen import decomposeQuadraticSegment
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

CHARACTERS = {
    "upper": [chr(c) for c in range(0x41, 0x5B)],
    "lower": [chr(c) for c in range(0x61, 0x7B)],
    "digits": [chr(c) for c in range(0x30, 0x3A)],
    "punctuation": list("!\"#%&'()*,-./:;?@[\\]_{}¡§¶·¿‘’‚“”„•…‹›"),
    "symbols": list("$+<=>^`|~¢£¥©®°±×÷€™←↑→↓"),
    "accented": list(
        "ÀÁÂÃÄÅÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝàáâãäåçèéêëìíîïñòóôõöùúûüýÿ"
        "ĀāĂăĄąČčĎďĘęĚěŁłŃńŇňŘřŚśŠšŤťŮůŽžẞ"
    ),
    "marks": [chr(c) for c in (0x300, 0x301, 0x302, 0x303, 0x304, 0x306, 0x307,
                               0x308, 0x30A, 0x30B, 0x30C, 0x326, 0x327, 0x328)],
}
SHORT_ABSOLUTE, SHORT_RELATIVE, COLINEAR_RADIANS = 3.0, 0.006, 0.1


def recording(glyphset, name):
    pen = DecomposingRecordingPen(glyphset)
    glyphset[name].draw(pen)
    return pen.value


def points(glyphset, name):
    """Point count and on-curve hops shorter than 10 units."""
    count = tiny = 0
    last = None
    for op, args in recording(glyphset, name):
        if op == "moveTo":
            count += 1
            last = args[0]
        elif op in ("lineTo", "qCurveTo", "curveTo"):
            count += len(args)
            if args[-1] is None:
                continue
            if last is not None and math.dist(last, args[-1]) < 10:
                tiny += 1
            last = args[-1]
        else:
            last = None
    return count, tiny


def quad_length(p0, p1, p2, steps=24):
    pts = [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
            (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])
           for t in (i / steps for i in range(steps + 1))]
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


def segments(glyphset, name):
    """Contours as (kind, start, end, length, piece_of_curve) tuples."""
    contours, current, last, start = [], None, None, None
    for op, args in recording(glyphset, name):
        if op == "moveTo":
            current = []
            contours.append(current)
            last = start = args[0]
        elif op == "lineTo":
            current.append(("line", last, args[0], math.dist(last, args[0]), False))
            last = args[0]
        elif op == "qCurveTo":
            pts = list(args)
            if pts[-1] is None:
                pts = pts[:-1]
                implied = ((pts[-1][0] + pts[0][0]) / 2, (pts[-1][1] + pts[0][1]) / 2)
                last = start = implied
                pts.append(implied)
            pieces = decomposeQuadraticSegment(pts)
            for off, end in pieces:
                current.append(("curve", last, end, quad_length(last, off, end), len(pieces) > 1))
                last = end
        elif op in ("closePath", "endPath"):
            if current and math.dist(last, start) > 1e-9:
                current.append(("line", last, start, math.dist(last, start), False))
    return [c for c in contours if c]


def segment_findings(font):
    found = collections.Counter()
    glyphset = font.getGlyphSet()
    for name in font.getGlyphOrder():
        for contour in segments(glyphset, name):
            perimeter = sum(s[3] for s in contour)
            previous_line = contour[-1][0] == "line"
            for kind, _, _, length, piece in contour:
                short = length <= 1e-9 or (
                    (length < SHORT_ABSOLUTE or length < SHORT_RELATIVE * perimeter)
                    and (previous_line or kind == "curve"))
                if short:
                    found["short"] += 1
                    found["short_lines"] += kind == "line"
                    found["short_curve_pieces"] += piece
                    found["short_whole_curves"] += kind == "curve" and not piece
                    found["short_under_3_units"] += length < SHORT_ABSOLUTE
                previous_line = kind == "line"
            for a, b in zip(contour, contour[1:] + contour[:1]):
                if a[0] == b[0] == "line":
                    ta = math.atan2(a[2][1] - a[1][1], a[2][0] - a[1][0])
                    tb = math.atan2(b[2][1] - b[1][1], b[2][0] - b[1][0])
                    turn = abs((tb - ta + math.pi) % (2 * math.pi) - math.pi)
                    found["colinear"] += turn < COLINEAR_RADIANS
    return found


def instances(path):
    font = TTFont(path)
    axes = {a.axisTag: (a.minValue, a.defaultValue, a.maxValue) for a in font["fvar"].axes}
    tags = sorted(axes)
    corners = itertools.product(*[(axes[t][0], axes[t][2]) for t in tags])
    locations = [dict(zip(tags, c)) for c in corners] + [{t: axes[t][1] for t in tags}]
    for location in locations:
        yield instancer.instantiateVariableFont(TTFont(path), location, inplace=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font", nargs=2, action="append", required=True,
                        metavar=("LABEL", "FONT"))
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    groups = {}
    for label, path in args.font:
        groups.setdefault(label, []).append(Path(path))

    defaults = {label: TTFont(paths[0]) for label, paths in groups.items()}
    common = {
        category: [ch for ch in chars if all(ord(ch) in f.getBestCmap() for f in defaults.values())]
        for category, chars in CHARACTERS.items()
    }
    report = {"characters_compared": sum(map(len, common.values())), "fonts": {}}
    for label, paths in groups.items():
        font = defaults[label]
        cmap, glyphset = font.getBestCmap(), font.getGlyphSet()
        per_category, every, tiny = {}, [], 0
        for category, chars in common.items():
            counts = []
            for ch in chars:
                n, t = points(glyphset, cmap[ord(ch)])
                counts.append(n)
                tiny += t
            every += counts
            per_category[category] = {"median": statistics.median(counts), "max": max(counts)}
        found, styles = collections.Counter(), 0
        for path in paths:
            for instance in instances(path):
                found.update(segment_findings(instance))
                styles += 1
        report["fonts"][label] = {
            "files": [p.name for p in paths],
            "points_per_character": {
                "median": statistics.median(every),
                "mean": round(statistics.mean(every), 1),
                "max": max(every),
                "by_category": per_category,
            },
            "on_curve_hops_under_10_units": tiny,
            "static_instances": styles,
            "uncapped_findings": dict(sorted(found.items())),
        }
        print(label, json.dumps(report["fonts"][label]["points_per_character"]["median"]),
              tiny, styles, dict(found))
    if args.out:
        args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
