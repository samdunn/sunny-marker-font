"""Redistribute compatible samples along corresponding contour arcs.

Offsetting dense source vertices compresses samples at a concave join. Keeping
that density in a variable font produces segments that collapse when rounded.
Use the drawing's extrema/corners as shared landmarks, and distribute samples
by each master's actual arc length between those landmarks.
"""

import plistlib
from pathlib import Path
import xml.etree.ElementTree as ET
from defusedxml.ElementTree import parse
import numpy as np
from clean_polylines import round_cusps

ROOT = Path(__file__).resolve().parents[1]


def redistribute(points, reference):
    ref = points[reference]
    before = ref - np.roll(ref, 1, axis=0)
    after = np.roll(ref, -1, axis=0) - ref
    cos = (before * after).sum(axis=1) / np.maximum(
        np.linalg.norm(before, axis=1) * np.linalg.norm(after, axis=1), 1e-9
    )
    count = len(ref)
    anchors = {0, count, *np.flatnonzero(cos < np.cos(np.radians(42))).tolist()}
    for axis in (0, 1):
        anchors.update([int(np.argmin(ref[:, axis])), int(np.argmax(ref[:, axis]))])
    closed = np.concatenate([points, points[:, :1]], axis=1)
    parts = []
    for start, end in zip(sorted(anchors), sorted(anchors)[1:]):
        p = closed[:, start : end + 1]
        lengths = np.linalg.norm(np.diff(p, axis=1), axis=2)
        arc = np.concatenate(
            [np.zeros((len(p), 1)), np.cumsum(lengths, axis=1)], axis=1
        )
        steps = max(2, int(np.ceil(arc[:, -1].max() / 5)))
        samples = []
        for master, dist in zip(p, arc):
            t = np.linspace(0, dist[-1], steps, endpoint=False)
            samples.append(
                np.column_stack(
                    [np.interp(t, dist, master[:, axis]) for axis in (0, 1)]
                )
            )
        parts.append(np.array(samples))
    return np.concatenate(parts, axis=1)


def main():
    masters = sorted((ROOT / "sources").glob("master-*.ufo"))
    reference = next(
        i
        for i, m in enumerate(masters)
        if m.name == "master-Roman-Regular-w100-o36.ufo"
    )
    contents = [
        plistlib.loads((m / "glyphs/contents.plist").read_bytes()) for m in masters
    ]
    for name in contents[0]:
        paths = [m / "glyphs" / c[name] for m, c in zip(masters, contents)]
        trees = [parse(p) for p in paths]
        contours = [t.findall("./outline/contour") for t in trees]
        for ci in range(len(contours[0])):
            nodes = [c[ci].findall("point") for c in contours]
            coords = np.array(
                [[(float(p.get("x")), float(p.get("y"))) for p in ns] for ns in nodes]
            )
            sampled = redistribute(coords, reference)
            if name not in ("star", "sparkle"):
                sampled = np.array(
                    [
                        round_cusps(p, maximum_shift=12, threshold=115, iterations=64)
                        for p in sampled
                    ]
                )
            for mi, cs in enumerate(contours):
                contour = cs[ci]
                contour.clear()
                for x, y in sampled[mi]:
                    ET.SubElement(
                        contour, "point", x=f"{x:.5f}", y=f"{y:.5f}", type="line"
                    )
        for tree, path in zip(trees, paths):
            ET.indent(tree, space="  ")
            tree.write(path, encoding="UTF-8", xml_declaration=True)
    print("Redistributed contour arcs across", len(masters), "masters")


if __name__ == "__main__":
    main()
