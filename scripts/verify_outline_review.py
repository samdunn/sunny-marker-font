"""Independent geometry and shaping checks for an outline-review binary."""
import argparse
import itertools
import json
import hashlib
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
import uharfbuzz as hb
from scipy.spatial import cKDTree
from outline_geometry import boundary


def main():
    p = argparse.ArgumentParser()
    p.add_argument("before", type=Path)
    p.add_argument("after", type=Path)
    p.add_argument("report", type=Path)
    p.add_argument("--raw-masters", type=Path,
                   help="Compare dense ink-edge samples against generated masters")
    args = p.parse_args()
    font, before = TTFont(args.after), TTFont(args.before)
    order = font.getGlyphOrder()
    assert order == before.getGlyphOrder(), "Glyph order changed"
    assert font.getBestCmap() == before.getBestCmap(), "Character coverage changed"
    assert [(a.axisTag, a.minValue, a.maxValue) for a in font["fvar"].axes] == [
        (a.axisTag, a.minValue, a.maxValue) for a in before["fvar"].axes]
    points = lambda f: sum(len(f["glyf"][n].coordinates) for n in order
                           if f["glyf"][n].numberOfContours > 0)
    locations = list(itertools.product((300, 700), (75, 125), (10, 36), (0, -9)))
    locations += [(400, 100, 14, -4.5), (550, 87.5, 23, -2.25), (600, 112.5, 18, -6.75)]
    overflow = []
    for location in locations:
        gs = font.getGlyphSet(location=dict(zip(("wght", "wdth", "opsz", "slnt"), location)))
        for name in order:
            pen = BoundsPen(gs)
            gs[name].draw(pen)
            if pen.bounds and (pen.bounds[1] < -340 or pen.bounds[3] > 960):
                overflow.append({"location": location, "glyph": name, "bounds": pen.bounds})
    hfont = hb.Font(hb.Face(args.after.read_bytes()))
    text = "SUNNY MARKER À BIENTÔT Ąą Ęę Ľďľť © ® ™ § ¶ € £ ¥"
    shaped = 0
    for weight, optical, slant in itertools.product((300, 350, 400, 550, 700), (10, 23, 36), (0, -2.25, -4.5, -6.75, -9)):
        advances = []
        for width in (75, 87.5, 100, 112.5, 125):
            hfont.set_variations(dict(wght=weight, wdth=width, opsz=optical, slnt=slant))
            buffer = hb.Buffer()
            buffer.add_str(text)
            buffer.guess_segment_properties()
            hb.shape(hfont, buffer)
            assert all(g.codepoint for g in buffer.glyph_infos), "Missing glyph"
            advances.append(sum(p.x_advance for p in buffer.glyph_positions))
            shaped += 1
        assert all(a < b for a, b in zip(advances, advances[1:])), advances
    report = {"glyphs": len(order), "points_before": points(before), "points_after": points(font),
              "glyph_bound_locations": len(locations), "shaping_locations": shaped,
              "overflows": overflow, "passed": not overflow}
    report["sha256"] = {"before": hashlib.sha256(args.before.read_bytes()).hexdigest(),
                        "after": hashlib.sha256(args.after.read_bytes()).hexdigest()}
    if args.raw_masters:
        errors = []
        for name, location in [("Roman-Light-w75-o10", (300, 75, 10, 0)),
                               ("Italic-Bold-w125-o36", (700, 125, 36, -9)),
                               ("Roman-Regular-w100-o36", (400, 100, 36, 0))]:
            raw = TTFont(args.raw_masters / f"master-{name}.ttf")
            source = raw.getGlyphSet()
            fitted = font.getGlyphSet(location=dict(zip(("wght", "wdth", "opsz", "slnt"), location)))
            for glyph in order:
                if glyph == "space":
                    continue
                a, b = boundary(source, glyph), boundary(fitted, glyph)
                error = max(cKDTree(a).query(b)[0].max(), cKDTree(b).query(a)[0].max())
                errors.append({"master": name, "glyph": glyph, "error": float(error)})
        errors.sort(key=lambda item: item["error"], reverse=True)
        report["edge_comparisons"] = len(errors)
        report["largest_edge_deviations"] = errors[:8]
        # Includes source simplification, cubic fitting, quadratic conversion,
        # integer rounding and the independent one-unit sampling interval.
        report["passed"] = report["passed"] and errors[0]["error"] <= 5
    args.report.write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report, indent=2))
    assert report["passed"], "Ink bounds or dense edge comparison failed"


if __name__ == "__main__":
    main()
