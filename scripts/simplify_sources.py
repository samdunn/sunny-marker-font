"""Remove redundant polyline nodes with one shared mask across every master.

Each omitted source point remains within one font unit of its replacement
segment in every master. Extrema, contour starts and contour counts stay fixed.
The common mask preserves interpolation compatibility throughout the axes.
"""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from defusedxml.ElementTree import parse

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
TOLERANCE = 1.0


def shared_mask(points):
    """points has shape (master, point, xy)."""
    count = points.shape[1]
    keep = {0, count}
    for axis in (0, 1):
        keep.update(np.argmin(points[:, :, axis], axis=1).tolist())
        keep.update(np.argmax(points[:, :, axis], axis=1).tolist())
    closed = np.concatenate((points, points[:, :1]), axis=1)
    anchors = sorted(keep)
    stack = list(zip(anchors, anchors[1:]))
    while stack:
        start, end = stack.pop()
        if end - start < 2:
            continue
        a = closed[:, start:start + 1]
        vector = closed[:, end:end + 1] - a
        offset = closed[:, start + 1:end] - a
        denom = (vector * vector).sum(axis=2, keepdims=True)
        t = np.clip((offset * vector).sum(axis=2, keepdims=True) /
                    np.maximum(denom, 1e-12), 0, 1)
        distance = np.linalg.norm(offset - t * vector, axis=2)
        per_point = distance.max(axis=0)
        index = int(np.argmax(per_point))
        if per_point[index] > TOLERANCE:
            split = start + 1 + index
            keep.add(split)
            stack.extend(((start, split), (split, end)))
    return sorted(keep - {count})


def simplify_group(masters):
    import plistlib
    if not masters:
        raise RuntimeError("Generate the UFO masters first")
    contents = [plistlib.loads((p / "glyphs/contents.plist").read_bytes()) for p in masters]
    before = after = 0
    for name in contents[0]:
        paths = [p / "glyphs" / c[name] for p, c in zip(masters, contents)]
        trees = [parse(p) for p in paths]
        contours = [t.findall("./outline/contour") for t in trees]
        if len({len(c) for c in contours}) != 1:
            raise ValueError(f"Incompatible contours: {name}")
        for ci in range(len(contours[0])):
            nodes = [c[ci].findall("point") for c in contours]
            if len({len(n) for n in nodes}) != 1:
                raise ValueError(f"Incompatible points: {name}")
            if any(p.get("type") != "line" for ns in nodes for p in ns):
                raise ValueError(f"Expected polylines: {name}")
            points = np.array([[(float(p.get("x")), float(p.get("y"))) for p in ns]
                               for ns in nodes])
            mask = set(shared_mask(points))
            before += len(nodes[0])
            after += len(mask)
            for master, ns in enumerate(nodes):
                for index, p in enumerate(ns):
                    if index not in mask:
                        contours[master][ci].remove(p)
        for tree, path in zip(trees, paths):
            ET.indent(tree, space="  ")
            tree.write(path, encoding="UTF-8", xml_declaration=True)
    report = {"masters": len(masters), "points_before": before,
              "points_after": after, "maximum_master_error_units": TOLERANCE,
              "units_per_em": 1000}
    return report


def main():
    reports = {"family": simplify_group(sorted((ROOT / "sources").glob("master-*.ufo")))}
    (ROOT / "documentation/source-simplification.json").write_text(json.dumps(reports, indent=2) + "\n")
    print(reports)


if __name__ == "__main__":
    main()
