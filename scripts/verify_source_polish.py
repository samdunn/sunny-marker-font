"""Measure the full ink-edge change between two sets of compatible UFOs.

This is independent of the fitting algorithm: both directions of the boundary
are sampled at one-unit spacing. Include the resulting sampling uncertainty
when interpreting distances. Deliberate counter repairs have a separate bound.
"""

import argparse
import json
from pathlib import Path

from scipy.spatial import cKDTree
from ufoLib2 import Font
import pathops

from outline_geometry import boundary


def filled_boundary(font, name):
    path = pathops.Path()
    font[name].draw(path.getPen())
    clean = pathops.simplify(path)
    significant = sum(abs(contour.area) > 0.5 for contour in clean.contours)
    principal = pathops.Path()
    for contour in clean.contours:
        # Sub-four-square-unit fragments are independently counted above.
        # A disappearing microscopic hole otherwise reports a large distance
        # to the nearest outer edge even though the changed ink area is tiny.
        if abs(contour.area) > 4:
            principal.addPath(contour)
    return boundary({name: principal}, name), significant


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    results = []
    for path in sorted(args.before.glob("master-*.ufo")):
        before, after = Font.open(path), Font.open(args.after / path.name)
        assert set(before.keys()) == set(after.keys()), "Glyph coverage changed"
        for name in before.keys():
            if not before[name].contours:
                continue
            (a, old_contours), (b, new_contours) = filled_boundary(
                before, name
            ), filled_boundary(after, name)
            deviation = float(
                max(cKDTree(a).query(b)[0].max(), cKDTree(b).query(a)[0].max())
            )
            limit = 40 if name == "W" else 12
            results.append(
                dict(
                    master=path.stem,
                    glyph=name,
                    deviation=deviation,
                    limit=limit,
                    filled_contours_before=old_contours,
                    filled_contours_after=new_contours,
                    passed=deviation <= limit and new_contours <= old_contours,
                )
            )
        print(path.stem, flush=True)
    results.sort(key=lambda item: item["deviation"], reverse=True)
    report = dict(
        comparisons=len(results),
        passed=all(r["passed"] for r in results),
        sampling_interval_units=1,
        ignored_boundary_fragment_area_units_squared=4,
        counted_topology_fragment_area_units_squared=0.5,
        largest_deviations=results[:30],
        failures=[r for r in results if not r["passed"]],
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "largest_deviations"}))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
