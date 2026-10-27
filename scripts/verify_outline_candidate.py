"""Independent checks for the 1.315 outline candidate against archived 1.314.

1.315 keeps 1.314's drawings with fewer points and a node at every extreme,
leaves out the Gothic alphabet, and redraws one mark: the vertical caron of
ď ľ ť Ľ, now a marker stroke that follows the weight axis. This checks that:

- the repertoire is 1.314's minus Gothic;
- shaping (advances and mark offsets) is identical for every other retained
  character and for the combining macron, overline and macron below;
- every other outline stays close to 1.314's at 108 axis settings, with each
  contour keeping its direction;
- in ď ľ ť Ľ the mark never touches the letter or crosses the advance, the
  advance is never narrower than 1.314's, and the mark gets heavier with weight;
- the outlines use far fewer points.

usage: verify_outline_candidate.py [FONT]
With no FONT, it checks the archived candidate and its checksums.
"""
from pathlib import Path
import hashlib
import itertools
import json
import sys

import numpy as np
import uharfbuzz as hb
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/outline-verification"
FILENAME = "SunnyMarker[opsz,slnt,wdth,wght].ttf"
GOTHIC = set(range(0x10330, 0x1034B))
CARON = {0x13D, 0x10F, 0x13E, 0x165}  # Ľ ď ľ ť, redrawn on purpose
MIN_GAP = 3.0  # least room between the vertical caron and its letter
# Largest distance a 1.315 outline may sit from 1.314's, in font units
# (UPM 1000). The refit tolerance is 6 at the masters; interpolation and
# rounding to whole units add a little.
LIMIT = 8.0
STEP = 4.0  # outline sampling interval, font units


def check_snapshot(snapshot):
    for line in (snapshot / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split("  ", 1)
        assert hashlib.sha256((snapshot / name).read_bytes()).hexdigest() == digest, name


def shape(font, order, text, loc):
    font.set_variations(loc)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf)
    return [
        (order[i.codepoint], p.x_advance, p.y_advance, p.x_offset, p.y_offset)
        for i, p in zip(buf.glyph_infos, buf.glyph_positions)
    ]


def contours(glyphset, name):
    """Each contour as a dense closed polyline, plus its signed area."""
    pen = DecomposingRecordingPen(glyphset)
    glyphset[name].draw(pen)
    out, current, start = [], None, None

    def quad(p0, p1, p2):
        n = max(2, int(np.hypot(*np.subtract(p2, p0)) / STEP) + 2)
        t = np.linspace(0, 1, n)[1:, None]
        return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * np.array(p1) + t * t * np.array(p2)

    for op, args in pen.value:
        if op == "moveTo":
            start = np.array(args[0], float)
            current = [start[None]]
            out.append(current)
        elif op == "lineTo":
            last = current[-1][-1]
            end = np.array(args[0], float)
            n = max(2, int(np.hypot(*(end - last)) / STEP) + 2)
            current.append(last + np.linspace(0, 1, n)[1:, None] * (end - last))
        elif op == "qCurveTo":
            pts = [np.array(p, float) for p in args if p is not None]
            if args[-1] is None:  # all off-curve contour
                start = (pts[-1] + pts[0]) / 2
                current = [start[None]]
                out.append(current)
                pts.append(start)
            last = current[-1][-1]
            offs, end = pts[:-1], pts[-1]
            for k, off in enumerate(offs):
                nxt = end if k == len(offs) - 1 else (off + offs[k + 1]) / 2
                current.append(quad(last, off, nxt))
                last = nxt
        elif op in ("closePath", "endPath"):
            last = current[-1][-1]
            n = max(2, int(np.hypot(*(start - last)) / STEP) + 2)
            current.append(last + np.linspace(0, 1, n)[1:, None] * (start - last))
    polys = [np.concatenate(c) for c in out]
    areas = [0.5 * float(np.sum(p[:-1, 0] * p[1:, 1] - p[1:, 0] * p[:-1, 1])) for p in polys]
    return polys, areas


def inside(poly, pts):
    """Even-odd point-in-polygon test for many points."""
    x, y = pts[:, :1], pts[:, 1:]
    x1, y1 = poly[None, :, 0], poly[None, :, 1]
    x2, y2 = np.roll(poly[:, 0], -1)[None], np.roll(poly[:, 1], -1)[None]
    dy = np.where(y2 == y1, 1e-12, y2 - y1)
    crossing = ((y1 > y) != (y2 > y)) & (x < (x2 - x1) * (y - y1) / dy + x1)
    return crossing.sum(axis=1) % 2 == 1


def point_count(font, name):
    glyph = font["glyf"][name]
    return 0 if glyph.isComposite() else glyph.numberOfContours and len(glyph.coordinates)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if len(sys.argv) > 1:
        candidate = Path(sys.argv[1])
    else:
        check_snapshot(ROOT / "candidates/1.315")
        candidate = ROOT / "candidates/1.315" / FILENAME
    check_snapshot(ROOT / "candidates/1.314")
    archived = ROOT / "candidates/1.314" / FILENAME

    new, old = TTFont(candidate), TTFont(archived)
    new_cmap, old_cmap = new.getBestCmap(), old.getBestCmap()
    chars, kept = set(new_cmap), set(old_cmap) - GOTHIC
    assert chars == kept, sorted(chars ^ kept)
    assert {0x305, 0x331} <= chars
    assert len(chars) == 374 and len(new.getGlyphOrder()) == 389

    # Shaping: advances and mark offsets must not change.
    a = hb.Font(hb.Face(archived.read_bytes()))
    b = hb.Font(hb.Face(candidate.read_bytes()))
    locations = list(itertools.product((300, 400, 550, 700), (75, 100, 125), (10, 23, 36), (0, -4.5, -9)))
    shaping_checks = mark_checks = caron_checks = 0
    for values in locations:
        loc = dict(zip(("wght", "wdth", "opsz", "slnt"), values))
        for cp in sorted(kept - CARON):
            assert shape(a, old.getGlyphOrder(), chr(cp), loc) == shape(b, new.getGlyphOrder(), chr(cp), loc), (cp, loc)
            shaping_checks += 1
        for cp in sorted(CARON):
            before = shape(a, old.getGlyphOrder(), chr(cp), loc)
            after = shape(b, new.getGlyphOrder(), chr(cp), loc)
            assert [g[0] for g in before] == [g[0] for g in after], (cp, loc)
            assert after[0][1] >= before[0][1], (cp, loc, before, after)
            caron_checks += 1
        for cp in map(ord, "AEIOUaeiou"):
            for mark in (0x304, 0x305, 0x331):
                text = chr(cp) + chr(mark)
                assert shape(a, old.getGlyphOrder(), text, loc) == shape(b, new.getGlyphOrder(), text, loc), (text, loc)
                mark_checks += 1

    # Outlines: distance from 1.314 and contour direction at every location.
    glyphs = sorted({new_cmap[cp] for cp in kept - CARON} | {"tildecomb", "macronbelowcomb"} & set(new.getGlyphOrder()))
    worst, worst_at, distances, outline_checks = 0.0, None, [], 0
    for values in locations:
        loc = dict(zip(("wght", "wdth", "opsz", "slnt"), values))
        gs_new, gs_old = new.getGlyphSet(location=loc), old.getGlyphSet(location=loc)
        for name in glyphs:
            pn, an = contours(gs_new, name)
            po, ao = contours(gs_old, name)
            assert len(pn) == len(po), (name, loc)
            if not pn:
                continue
            # Contours are matched by order; each keeps its winding.
            for i, (x, y) in enumerate(zip(an, ao)):
                assert np.sign(x) == np.sign(y), (name, loc, i, x, y)
            new_pts, old_pts = np.concatenate(pn), np.concatenate(po)
            d = max(
                cKDTree(old_pts).query(new_pts)[0].max(),
                cKDTree(new_pts).query(old_pts)[0].max(),
            )
            distances.append(d)
            outline_checks += 1
            if d > worst:
                worst, worst_at = d, (name, loc)
    assert worst <= LIMIT, (worst, worst_at)

    # The vertical caron: clear of its letter and inside the advance everywhere.
    smallest_gap, thickness = np.inf, {}
    for values in locations:
        loc = dict(zip(("wght", "wdth", "opsz", "slnt"), values))
        gs = new.getGlyphSet(location=loc)
        for cp in sorted(CARON):
            name = new_cmap[cp]
            polys, areas = contours(gs, name)
            letter, mark = polys[:-1], polys[-1]
            letter_pts = np.concatenate(letter)
            gap = float(cKDTree(letter_pts).query(mark)[0].min())
            assert gap >= MIN_GAP, (name, loc, gap)
            assert not any(inside(poly, mark).any() for poly in letter), (name, loc)
            assert mark[:, 0].max() <= gs[name].width, (name, loc)
            smallest_gap = min(smallest_gap, gap)
            perimeter = float(np.linalg.norm(np.diff(mark, axis=0), axis=1).sum())
            thickness.setdefault(values[1:], {})[values[0]] = 2 * abs(areas[-1]) / perimeter
    for by_weight in thickness.values():
        weights = sorted(by_weight)
        assert all(by_weight[x] < by_weight[y] for x, y in zip(weights, weights[1:])), by_weight

    # Points per encoded glyph in the default (opsz 14) outlines.
    names = sorted({new_cmap[cp] for cp in kept})
    before = [point_count(old, n) for n in names]
    after = [point_count(new, n) for n in names]
    drawn = [(x, y) for x, y in zip(before, after) if x]
    report = {
        "font": candidate.name,
        "sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(),
        "glyphs": len(new.getGlyphOrder()),
        "codepoints": len(chars),
        "removed_codepoints": f"U+10330-U+1034A ({len(GOTHIC)} Gothic letters)",
        "axis_locations": len(locations),
        "retained_shaping_checks": shaping_checks,
        "mark_checks": mark_checks,
        "vertical_caron": {
            "redrawn_characters": "U+013D U+010F U+013E U+0165 (Ľ ď ľ ť)",
            "advance_checks": caron_checks,
            "smallest_gap_to_letter_units": round(smallest_gap, 1),
            "mark_thickness_units": {
                "wght_300": round(float(np.mean([v[300] for v in thickness.values()])), 1),
                "wght_700": round(float(np.mean([v[700] for v in thickness.values()])), 1),
            },
        },
        "outline_checks": outline_checks,
        "largest_outline_distance_units": round(worst, 2),
        "largest_outline_distance_at": {"glyph": worst_at[0], **worst_at[1]},
        "p99_outline_distance_units": round(float(np.percentile(distances, 99)), 2),
        "median_outline_distance_units": round(float(np.median(distances)), 2),
        "points_in_default_outlines": {
            "1.314": int(sum(x for x, _ in drawn)),
            "1.315": int(sum(y for _, y in drawn)),
            "median_per_glyph_1.314": float(np.median([x for x, _ in drawn])),
            "median_per_glyph_1.315": float(np.median([y for _, y in drawn])),
        },
    }
    (OUT / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
