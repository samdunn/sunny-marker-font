"""Fit compatible cubic curves to the generated polyline masters.

Every master shares segment boundaries and point types. A segment is accepted
only when its fit meets the tolerance in every master, not just Regular.
Endpoints at extrema and sharp corners of the reference drawing are retained;
smooth joins use the same tangent on both sides. This is a source-generation
step, not a filter to run on hand-edited cubic UFOs.
"""
import json
from pathlib import Path
import plistlib
import xml.etree.ElementTree as ET

from defusedxml.ElementTree import parse
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CURVE_TOLERANCE = 2.0
LINE_TOLERANCE = 0.6


def unit(v):
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-9)


def fit_contour(points, reference=0):
    """Return shared (start, end, kind, controls) segments and fit error.

    Coordinates have shape (masters, points, xy). Error is measured at all
    input vertices against an iteratively reparameterized curve. The independent
    QA also checks the rasterized result and intermediate axis locations.
    """
    # A duplicated closing point is not another segment. Use one shared mask.
    distinct = np.any(np.linalg.norm(points - np.roll(points, 1, axis=1), axis=2)
                      > 1e-8, axis=0)
    points = points[:, distinct]
    count = points.shape[1]
    if count < 3:
        raise ValueError("Degenerate contour")
    incoming = unit(points - np.roll(points, 1, axis=1))
    outgoing = unit(np.roll(points, -1, axis=1) - points)
    turn = np.arccos(np.clip((incoming * outgoing).sum(axis=2), -1, 1))
    sharp = set(np.flatnonzero(turn[reference] > np.radians(42)))
    anchors = {0, count, *sharp}
    for axis in (0, 1):
        anchors.add(int(np.argmin(points[reference, :, axis])))
        anchors.add(int(np.argmax(points[reference, :, axis])))
    tangents = unit(incoming + outgoing)
    closed = np.concatenate([points, points[:, :1]], axis=1)
    result = []
    worst = 0.0

    def fit(start, end):
        nonlocal worst
        p = closed[:, start:end + 1]
        a, b = p[:, 0], p[:, -1]
        chord = b - a
        if end - start == 1:
            result.append((start, end, "line", b))
            return
        offset = p - a[:, None]
        projection = np.clip((offset * chord[:, None]).sum(axis=2)
                             / np.maximum((chord * chord).sum(axis=1)[:, None], 1e-9), 0, 1)
        distance = np.linalg.norm(offset - projection[..., None] * chord[:, None], axis=2)
        # Keep a genuine straight segment instead of a nearly flat curve.
        if distance.max() <= LINE_TOLERANCE:
            worst = max(worst, float(distance.max()))
            result.append((start, end, "line", b))
            return
        arc = np.linalg.norm(np.diff(p, axis=1), axis=2)
        length = arc.sum(axis=1)
        u = np.concatenate([np.zeros((len(p), 1)), np.cumsum(arc, axis=1)], axis=1)
        u /= np.maximum(length[:, None], 1e-9)
        t0 = outgoing[:, start] if start in sharp else tangents[:, start]
        last = end % count
        t1 = incoming[:, last] if last in sharp else tangents[:, last]
        for iteration in range(6):
            v = 1-u
            b1, b2 = 3*v*v*u, 3*v*u*u
            # Solve handle lengths with fixed endpoint tangents.
            h0, h1 = b1[..., None]*t0[:, None], -b2[..., None]*t1[:, None]
            base = (v**3+b1)[..., None]*a[:, None] + (u**3+b2)[..., None]*b[:, None]
            target = p-base
            c00, c01 = (h0*h0).sum(axis=(1, 2)), (h0*h1).sum(axis=(1, 2))
            c11 = (h1*h1).sum(axis=(1, 2))
            x0, x1 = (h0*target).sum(axis=(1, 2)), (h1*target).sum(axis=(1, 2))
            det = c00*c11-c01*c01
            valid = np.abs(det) > 1e-10
            safe = np.where(valid, det, 1)
            alpha = np.clip(np.where(valid, (x0*c11-x1*c01)/safe, length/3), .01, length)
            beta = np.clip(np.where(valid, (x1*c00-x0*c01)/safe, length/3), .01, length)
            c1, c2 = a+alpha[:, None]*t0, b-beta[:, None]*t1
            q = base+h0*alpha[:, None, None]+h1*beta[:, None, None]
            per_vertex = np.linalg.norm(q-p, axis=2).max(axis=0)
            error = float(per_vertex.max())
            if error <= CURVE_TOLERANCE:
                # Vertex-only fits can bow between sparse points on a straight
                # flank. Check the curve back against every source segment too.
                sample_count = max(17, int(np.ceil(length.max()/4))+1)
                sample = np.linspace(0, 1, sample_count)[None, :, None]
                curve = ((1-sample)**3*a[:, None]
                         + 3*(1-sample)**2*sample*c1[:, None]
                         + 3*(1-sample)*sample**2*c2[:, None]
                         + sample**3*b[:, None])
                edges = np.diff(p, axis=1)
                offset = curve[:, :, None]-p[:, None, :-1]
                projection = np.clip((offset*edges[:, None]).sum(axis=3)
                                     / np.maximum((edges*edges).sum(axis=2)[:, None], 1e-9), 0, 1)
                deviation = np.linalg.norm(offset-projection[..., None]*edges[:, None], axis=3)
                edge_error = float(deviation.min(axis=2).max())
                if edge_error <= CURVE_TOLERANCE:
                    result.append((start, end, "curve", np.stack([c1, c2, b], axis=1)))
                    worst = max(worst, error, edge_error)
                    return
                # Reparameterizing cannot fix a curve that bows off the path;
                # split it at an original point instead.
                break
            # Closest-point refinement avoids extra nodes caused solely by
            # different traversal speeds along the polyline and the cubic.
            d1 = (3*(v*v)[..., None]*(c1-a)[:, None]
                  + 6*(v*u)[..., None]*(c2-c1)[:, None]
                  + 3*(u*u)[..., None]*(b-c2)[:, None])
            d2 = (6*v[..., None]*(c2-2*c1+a)[:, None]
                  + 6*u[..., None]*(b-2*c2+c1)[:, None])
            denominator = (d1*d1+(q-p)*d2).sum(axis=2)
            step = ((q-p)*d1).sum(axis=2)/np.maximum(denominator, 1e-9)
            refined = np.clip(u-step, 0, 1)
            refined[:, 0], refined[:, -1] = 0, 1
            # Keep correspondence ordered, including in extreme masters.
            ordered = np.all(np.diff(refined, axis=1) >= 0, axis=1)
            u = np.where(ordered[:, None], refined, u)
        split = start + 1 + int(np.argmax(per_vertex[1:-1]))
        fit(start, split)
        fit(split, end)

    ordered = sorted(anchors)
    for a, b in zip(ordered, ordered[1:]):
        fit(a, b)
    return points, result, worst


def main():
    masters = sorted((ROOT / "sources").glob("master-*.ufo"))
    reference = next(i for i, m in enumerate(masters)
                     if m.name == "master-Roman-Regular-w100-o36.ufo")
    contents = [plistlib.loads((m / "glyphs/contents.plist").read_bytes()) for m in masters]
    before = after = curves = 0
    maximum = 0.0
    glyph_report = {}
    for name in contents[0]:
        paths = [m / "glyphs" / c[name] for m, c in zip(masters, contents)]
        trees = [parse(p) for p in paths]
        outlines = [t.findall("./outline/contour") for t in trees]
        if len({len(o) for o in outlines}) != 1:
            raise ValueError(f"Incompatible contours: {name}")
        nb = na = 0
        for ci in range(len(outlines[0])):
            nodes = [o[ci].findall("point") for o in outlines]
            if len({len(n) for n in nodes}) != 1:
                raise ValueError(f"Incompatible points: {name}")
            if any(p.get("type") != "line" for ns in nodes for p in ns):
                raise ValueError(f"Expected generated polylines: {name}; regenerate sources first")
            coords = np.array([[(float(p.get("x")), float(p.get("y"))) for p in ns] for ns in nodes])
            points, segments, error = fit_contour(coords, reference)
            maximum = max(maximum, error)
            nb += len(nodes[0])
            na += sum(3 if s[2] == "curve" else 1 for s in segments)
            curves += sum(s[2] == "curve" for s in segments)
            for mi, outline in enumerate(outlines):
                contour = outline[ci]
                contour.clear()
                # UFO point types describe the incoming segment. Rotate the
                # final endpoint to the start, followed by each segment's handles.
                first = points[mi, 0]
                ET.SubElement(contour, "point", x=str(first[0]), y=str(first[1]), type=segments[-1][2])
                for si, (_, _, kind, values) in enumerate(segments):
                    values = values[mi:mi+1] if kind == "line" else values[mi]
                    for pi, value in enumerate(values):
                        is_end = pi == len(values)-1
                        if si == len(segments)-1 and is_end:
                            continue
                        attrs = {"x": f"{value[0]:.4f}", "y": f"{value[1]:.4f}"}
                        if is_end:
                            attrs["type"] = kind
                        ET.SubElement(contour, "point", **attrs)
        before += nb
        after += na
        glyph_report[name] = {"before": nb, "after": na}
        for tree, path in zip(trees, paths):
            ET.indent(tree, space="  ")
            tree.write(path, encoding="UTF-8", xml_declaration=True)
    report = {"masters": len(masters), "points_before": before, "points_after": after,
              "cubic_segments": curves, "maximum_sample_fit_error_units": maximum,
              "curve_tolerance_units": CURVE_TOLERANCE, "glyphs": glyph_report}
    (ROOT / "documentation/curve-fitting.json").write_text(json.dumps(report, indent=2) + "\n")
    print({k: v for k, v in report.items() if k != "glyphs"}, flush=True)


if __name__ == "__main__":
    main()
