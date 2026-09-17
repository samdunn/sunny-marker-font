"""Review FontBakery's A/AE kink warning against actual variable locations.

The warning averages two diagonal corners of the weight/width designspace.
The actual font also has intermediate weight and width masters, so its path
between those corners is not that two-corner average. Keep the warning in the
official report and independently measure the actual flagged join along the path.
"""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from fontTools.ttLib import TTFont
from fontTools.varLib.interpolatable import Glyph


def join_points(font, name, location):
    glyph = Glyph(name, font.getGlyphSet(location=location))
    points = glyph.points[0][84:87]
    assert [p[1] for p in points] == [False, True, False], "Flagged join moved"
    return np.array([p[0] for p in points])


def bend(points):
    incoming, outgoing = np.diff(points, axis=0)
    cross = abs(incoming[0] * outgoing[1] - incoming[1] * outgoing[0])
    return dict(
        deviation_units=float(cross / np.linalg.norm(incoming + outgoing)),
        angle_degrees=float(np.degrees(np.arctan2(cross, incoming @ outgoing))),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("font", type=Path)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    font = TTFont(args.font)
    paths = []
    for name in ("A", "AE"):
        for optical in (10, 14):
            first = dict(wght=700, wdth=75, opsz=optical, slnt=-9)
            last = dict(wght=300, wdth=125, opsz=optical, slnt=-9)
            hypothetical = bend(
                (join_points(font, name, first) + join_points(font, name, last)) / 2
            )
            actual = []
            for t in np.linspace(0, 1, 101):
                location = dict(
                    wght=float(700 - 400 * t),
                    wdth=float(75 + 50 * t),
                    opsz=optical,
                    slnt=-9,
                )
                actual.append(
                    dict(location=location, **bend(join_points(font, name, location)))
                )
            worst = max(actual, key=lambda row: row["deviation_units"])
            assert worst["deviation_units"] < 2, (name, worst)
            paths.append(
                dict(
                    glyph=name,
                    optical_size=optical,
                    samples=101,
                    hypothetical_corner_average=hypothetical,
                    actual_maximum=worst,
                )
            )
    report = dict(
        passed=True,
        font_sha256=hashlib.sha256(args.font.read_bytes()).hexdigest(),
        glyph_location_checks=404,
        unique_locations=202,
        fonttools_default_deviation_threshold_units=2,
        official_warning_suppressed=False,
        scope="Only the reported A/AE contour 0 point 85 joins; sampled actual diagonal paths, not all possible coordinates.",
        paths=paths,
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print("PASS: 404 A/AE glyph-location checks remain below the two-unit kink threshold")


if __name__ == "__main__":
    main()
