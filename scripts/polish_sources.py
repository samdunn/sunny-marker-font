"""Polish cubic masters after layout construction, preserving shared topology.

Short spans are merged only when a tangent-constrained fit stays within two
units at the sampled parameters in every master. Counter openings and near-axis
line alignment are separate, deliberate drawing repairs; their changes are
reported independently and checked against dense before/after ink boundaries.
"""

import argparse
import json
from pathlib import Path
import numpy as np
from ufoLib2 import Font
from round_source_joins import fillet_contours, segment_curves


def unit(a):
    return a / np.maximum(np.linalg.norm(a, axis=-1, keepdims=True), 1e-9)


def evalcurve(c, t):
    t = np.asarray(t)[..., None]
    return (
        (1 - t) ** 3 * c[:, None, 0]
        + 3 * (1 - t) ** 2 * t * c[:, None, 1]
        + 3 * (1 - t) * t * t * c[:, None, 2]
        + t**3 * c[:, None, 3]
    )


def merge(a, b, tolerance=1):
    """Fit two adjoining cubics together in every master, or reject the merge."""
    t = np.linspace(0, 1, 25)[None, :]
    p = np.concatenate([evalcurve(a, t), evalcurve(b, t)[:, 1:]], axis=1)
    arcs = np.linalg.norm(np.diff(p, axis=1), axis=2)
    length = arcs.sum(axis=1)
    u = np.c_[np.zeros(len(p)), arcs.cumsum(axis=1)] / np.maximum(length[:, None], 1e-9)
    start, end = p[:, 0], p[:, -1]
    t0 = unit(a[:, 1] - a[:, 0])
    t1 = unit(b[:, 3] - b[:, 2])
    for _ in range(8):
        v = 1 - u
        h0 = (3 * v * v * u)[..., None] * t0[:, None]
        h1 = -(3 * v * u * u)[..., None] * t1[:, None]
        base = (v**3 + 3 * v * v * u)[..., None] * start[:, None] + (
            u**3 + 3 * v * u * u
        )[..., None] * end[:, None]
        target = p - base
        c00 = (h0 * h0).sum((1, 2))
        c01 = (h0 * h1).sum((1, 2))
        c11 = (h1 * h1).sum((1, 2))
        x0 = (h0 * target).sum((1, 2))
        x1 = (h1 * target).sum((1, 2))
        det = c00 * c11 - c01 * c01
        safe = np.where(abs(det) > 1e-10, det, 1)
        alpha = np.clip(
            np.where(abs(det) > 1e-10, (x0 * c11 - x1 * c01) / safe, length / 3),
            0.01,
            length,
        )
        beta = np.clip(
            np.where(abs(det) > 1e-10, (x1 * c00 - x0 * c01) / safe, length / 3),
            0.01,
            length,
        )
        c1 = start + alpha[:, None] * t0
        c2 = end - beta[:, None] * t1
        q = base + h0 * alpha[:, None, None] + h1 * beta[:, None, None]
        error = float(np.linalg.norm(q - p, axis=2).max())
        if error <= tolerance:
            return np.stack([start, c1, c2, end], axis=1), error
        d1 = (
            3 * (v * v)[..., None] * (c1 - start)[:, None]
            + 6 * (v * u)[..., None] * (c2 - c1)[:, None]
            + 3 * (u * u)[..., None] * (end - c2)[:, None]
        )
        d2 = (
            6 * v[..., None] * (c2 - 2 * c1 + start)[:, None]
            + 6 * u[..., None] * (end - 2 * c2 + c1)[:, None]
        )
        den = (d1 * d1 + (q - p) * d2).sum(axis=2)
        step = ((q - p) * d1).sum(axis=2) / np.maximum(den, 1e-9)
        refined = np.clip(u - step, 0, 1)
        refined[:, 0] = 0
        refined[:, -1] = 1
        ordered = np.all(np.diff(refined, axis=1) >= 0, axis=1)
        u = np.where(ordered[:, None], refined, u)
    return None, error


def write_contour(contour, curves, kinds):
    from ufoLib2.objects import Point

    contour.points.clear()
    contour.points.append(
        Point(float(curves[0, 0, 0]), float(curves[0, 0, 1]), type=kinds[-1])
    )
    for i, (curve, kind) in enumerate(zip(curves, kinds)):
        if kind == "curve":
            for x, y in curve[1:3]:
                contour.points.append(Point(float(x), float(y)))
        if i < len(curves) - 1:
            contour.points.append(
                Point(float(curve[3, 0]), float(curve[3, 1]), type=kind)
            )


def polish(curves, kinds):
    removed = 0
    changed = True
    worst = 0
    while changed and len(kinds) > 3:
        changed = False
        lengths = np.linalg.norm(np.diff(curves, axis=2), axis=3).sum(axis=2)
        for j in np.argsort(lengths.min(axis=0)):
            if lengths[:, j].min() > 10:
                break
            for a, b in [
                (int(j), int((j + 1) % len(kinds))),
                (int((j - 1) % len(kinds)), int(j)),
            ]:
                merged, error = merge(curves[:, a], curves[:, b], tolerance=2)
                if merged is not None:
                    curves[:, a] = merged
                    curves = np.delete(curves, b, axis=1)
                    kinds[a] = "curve"
                    kinds.pop(b)
                    removed += 1
                    changed = True
                    worst = max(worst, error)
                    break
            if changed:
                break
    return curves, kinds, removed, worst


def snap_lines(curves, kinds, slants, tolerance=6):
    c = curves.copy()
    c[:, :, :, 0] -= slants[:, None, None] * c[:, :, :, 1]
    count = 0
    n = len(kinds)
    # Each master's rounding differs, but moving endpoints keeps topology intact.
    # Align complete connected runs so one correction cannot tilt its neighbor.
    for master in c:
        for axis in (0, 1):
            parent = list(range(n))

            def root(i):
                while parent[i] != i:
                    i = parent[i]
                return i

            for j, kind in enumerate(kinds):
                if kind != "line":
                    continue
                delta = master[j, 3] - master[j, 0]
                if abs(delta[axis]) <= tolerance and abs(delta[1 - axis]) >= 40:
                    parent[root((j + 1) % n)] = root(j)
            groups = {}
            for j in range(n):
                groups.setdefault(root(j), []).append(j)
            for members in groups.values():
                if len(members) < 2:
                    continue
                center = master[members, 0, axis].mean()
                for j in members:
                    delta = center - master[j, 0, axis]
                    master[j, :2, axis] += delta
                    master[(j - 1) % n, 2:, axis] += delta
                count += len(members) - 1
    c[:, :, :, 0] += slants[:, None, None] * c[:, :, :, 1]
    return c, count


def soften_variable_joins(curves, kinds, name):
    """Keep opposing tangents from forming needles between weight masters.

    The u/w/k joins look round at the masters but their handles cross while
    interpolating. Trim both flanks and add a shared six-unit rounding arc.
    A lower master angle threshold captures these intermediate-only cusps.
    """
    if name not in ("u", "w", "k"):
        return curves, kinds, 0
    rounded, targets = fillet_contours(curves, distance=6, angle_limit=100)
    if rounded is None:
        return curves, kinds, 0
    updated = []
    for i, kind in enumerate(kinds):
        updated.append(kind)
        if targets[(i + 1) % len(kinds)]:
            updated.append("curve")
    return rounded, updated, int(targets.sum())


def open_caps(curves, kinds, slants, reference):
    """Keep a counter's bottom arc open when the heavy narrow master pinches.

    The ampersand has narrow internal notches inherited from the drawing.
    Maintain a six-unit opening at the same shared arc, including when an offset
    would reverse the two flanks. This is an intentional local drawing repair.
    """
    c = curves.copy()
    c[:, :, :, 0] -= slants[:, None, None] * c[:, :, :, 1]
    changes = 0
    n = len(kinds)
    for span in (1, 2):
        for j in range(n):
            indices = [(j + k) % n for k in range(span)]
            if any(kinds[k] != "curve" for k in indices):
                continue
            start, end = c[:, j, 0], c[:, indices[-1], 3]
            direction = unit((end - start)[reference])
            if np.linalg.norm(direction) < 0.5:
                continue
            width = (end - start) @ direction
            if width.min() >= 6 or width[reference] < 6:
                continue
            normal = np.array([-direction[1], direction[0]])
            controls = c[:, indices].reshape(len(c), -1, 2)
            depth = abs((controls - (start + end)[:, None] / 2) @ normal).max(axis=1)
            affected = (width < 6) & (depth > 2) & (depth < 25) & (width > -28)
            for mi in np.flatnonzero(affected):
                # Interpolate a correction along the arc, avoiding a singular scale when
                # the two flanks coincide or reverse in the offset geometry.
                correction = (6 - width[mi]) / 2
                for k, index in enumerate(indices):
                    for point in range(4):
                        t = (k + point / 3) / span
                        c[mi, index, point] += direction * correction * (2 * t - 1)
                c[mi, (j - 1) % n, 2:] -= direction * correction
                c[mi, (indices[-1] + 1) % n, :2] += direction * correction
                changes += 1
    c[:, :, :, 0] += slants[:, None, None] * c[:, :, :, 1]
    return c, changes


def normalize_w(curves, reference, narrow_masters):
    """Rebuild W's filled boundary without the offset loops inside its strokes.

    Heavy condensed strokes cross near the two joins. Widening those internal
    loops would create holes. Boolean-normalize the filled shape instead, then
    fit all masters with common landmarks on the unchanged long flanks.
    """
    import pathops
    from scipy.spatial import cKDTree
    from outline_geometry import FlattenPen
    from fit_sources import fit_contour
    from clean_polylines import round_cusps

    polygons = []
    for master, narrow in zip(curves, narrow_masters):
        path = pathops.Path()
        path.moveTo(*master[0, 0])
        for curve in master:
            path.cubicTo(*curve[1:].reshape(-1))
        path.close()
        clean = pathops.simplify(path)
        # Close sub-four-unit slits left where thick strokes nearly touch.
        # Expand then contract by two units, leaving the external silhouette
        # intact while removing fragile hairline notches inside the join.
        if narrow:
            edge = pathops.Path(clean)
            edge.stroke(4, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
            edge.convertConicsToQuads(0.05)
            expanded = pathops.op(clean, edge, pathops.PathOp.UNION)
            edge = pathops.Path(expanded)
            edge.stroke(4, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
            edge.convertConicsToQuads(0.05)
            closed = pathops.op(expanded, edge, pathops.PathOp.DIFFERENCE)
            # Boolean stroke operations can be unstable at coincident edges.
            # A slit correction must not remove a stroke or change bulk ink.
            assert abs(closed.area - clean.area) < abs(clean.area) * 0.01
            clean = closed
        pen = FlattenPen(None)
        clean.draw(pen)
        assert len(pen.contours) == 1, "W must have one filled contour"
        polygon = pen.contours[0]
        area = lambda p: np.sum(
            p[:, 0] * np.roll(p[:, 1], -1) - p[:, 1] * np.roll(p[:, 0], -1)
        )
        if area(polygon) * area(master[:, 0]) < 0:
            polygon = polygon[::-1]
        polygons.append(polygon)
    lengths = np.linalg.norm(np.diff(curves, axis=2), axis=3).sum(axis=2)
    landmarks = [
        i
        for i in range(curves.shape[1])
        if np.min(lengths[:, i]) > 40
        and np.min(lengths[:, (i - 1) % curves.shape[1]]) > 15
    ]
    indexes, keep = [], np.ones(len(landmarks), bool)
    for polygon, master in zip(polygons, curves):
        distance, nearest = cKDTree(polygon).query(master[landmarks, 0])
        keep &= distance < 2
        indexes.append(nearest)
    indexes = np.array(indexes)[:, keep]
    assert indexes.shape[1] >= 8
    for polygon, selected in zip(polygons, indexes):
        assert len(set(selected)) == len(selected), "W landmarks must remain distinct"
        assert sum(
            (b - a) % len(polygon) for a, b in zip(selected, np.roll(selected, -1))
        ) == len(polygon), "Landmarks must traverse W exactly once"
    parts = []
    for column in range(indexes.shape[1]):
        arcs = []
        for polygon, selected in zip(polygons, indexes):
            a, b = selected[column], selected[(column + 1) % len(selected)]
            arc = (
                polygon[a : b + 1]
                if b > a
                else np.concatenate([polygon[a:], polygon[: b + 1]])
            )
            dist = np.r_[0, np.cumsum(np.linalg.norm(np.diff(arc, axis=0), axis=1))]
            arcs.append((arc, dist))
        steps = max(3, int(np.ceil(max(dist[-1] for arc, dist in arcs) / 3)))
        parts.append(
            np.array(
                [
                    np.column_stack(
                        [
                            np.interp(
                                np.linspace(0, dist[-1], steps, endpoint=False),
                                dist,
                                arc[:, axis],
                            )
                            for axis in (0, 1)
                        ]
                    )
                    for arc, dist in arcs
                ]
            )
        )
    samples = np.concatenate(parts, axis=1)
    samples = np.array(
        [round_cusps(p, maximum_shift=4, threshold=115, iterations=32) for p in samples]
    )
    points, segments, error = fit_contour(samples, reference)
    result, kinds = [], []
    for start, end, kind, controls in segments:
        a = points[:, start]
        if kind == "line":
            segment = (
                a[:, None]
                + np.linspace(0, 1, 4)[None, :, None] * (controls - a)[:, None]
            )
        else:
            segment = np.concatenate([a[:, None], controls], axis=1)
        result.append(segment)
        kinds.append(kind)
    return np.stack(result, axis=1), kinds, error


def stabilize_top_anchors(font, shear):
    """Recenter top marks after polishing, including precomposed components."""
    from outline_geometry import FlattenPen
    from prepare_layout import top_center
    from fontTools.misc.transform import Transform

    old = {g.name: {a.name: (a.x, a.y) for a in g.anchors} for g in font}
    shifts = {}

    def update(name):
        if name in shifts:
            return shifts[name]
        glyph = font[name]
        top = next((a for a in glyph.anchors if a.name == "top"), None)
        if top is None or "_top" in old[name]:
            shifts[name] = 0
            return 0
        if glyph.contours:
            pen = FlattenPen(font)
            glyph.draw(pen)
            center = top_center(np.concatenate(pen.contours), shear)
            target = round(float(center + shear * top.y), 3)
            shift = float(target - top.x)
        elif glyph.components:
            shift = update(glyph.components[0].baseGlyph)
            for component in glyph.components[1:]:
                if "_top" in old[component.baseGlyph]:
                    a, b, c, d, x, y = component.transformation
                    component.transformation = Transform(
                        *(float(v) for v in (a, b, c, d, round(x + shift, 3), y))
                    )
        else:
            shift = 0
        top.x = round(float(top.x + shift), 3)
        shifts[name] = shift
        return shift

    for name in font.keys():
        update(name)
    return shifts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sources", type=Path, default=Path(__file__).resolve().parents[1] / "sources"
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("build/resubmission-polish/source-polish.json"),
    )
    args = parser.parse_args()
    paths = sorted(args.sources.glob("master-*.ufo"))
    fonts = [Font.open(p) for p in paths]
    reference = next(
        i for i, p in enumerate(paths) if p.name == "master-Roman-Regular-w100-o36.ufo"
    )
    slants = np.array(
        [np.tan(np.radians(9)) if "Italic" in p.name else 0 for p in paths]
    )
    report = {}
    total = 0
    for name in fonts[0].keys():
        removed = snapped = opened = rounded_joins = normalized = 0
        normalized_error = 0
        worst = 0
        for ci in range(len(fonts[0][name].contours)):
            source = [segment_curves(f[name].contours[ci]) for f in fonts]
            assert all(k == source[0][1] for c, k in source)
            curves, kinds, n, e = polish(
                np.array([c for c, k in source]), list(source[0][1])
            )
            cap_count = join_count = 0
            if name == "W":
                curves, kinds, normalized_error = normalize_w(
                    curves, reference, ["-w75-" in p.name for p in paths]
                )
                normalized = len(curves)
            if name == "ampersand":
                curves, cap_count = open_caps(curves, kinds, slants, reference)
            if name in ("ordfeminine", "star", "sparkle"):
                rounded, targets = fillet_contours(
                    curves,
                    distance=4,
                    angle_limit=120 if name == "ordfeminine" else 145,
                )
                if rounded is not None:
                    updated = []
                    for i, k in enumerate(kinds):
                        updated.append(k)
                        if targets[(i + 1) % len(kinds)]:
                            updated.append("curve")
                    curves, kinds = rounded, updated
                    join_count = int(targets.sum())
            curves, kinds, intermediate_joins = soften_variable_joins(
                curves, kinds, name
            )
            join_count += intermediate_joins
            curves, count = snap_lines(
                curves, kinds, slants, tolerance=12 if name == "w" else 6
            )
            removed += n
            snapped += count
            opened += cap_count
            rounded_joins += join_count
            worst = max(worst, e)
            if n or count or cap_count or join_count or normalized:
                for f, cs in zip(fonts, curves):
                    write_contour(f[name].contours[ci], cs, kinds)
        if removed or snapped or opened or rounded_joins or normalized:
            report[name] = {
                "merged_segments": removed,
                "aligned_lines": snapped,
                "opened_master_counters": opened,
                "rounded_shared_joins": rounded_joins,
                "boolean_normalized_masters": normalized,
                "maximum_normalized_fit_error": normalized_error,
                "maximum_pair_fit_error": worst,
            }
            total += removed
    for font, path, shear in zip(fonts, paths, slants):
        stabilize_top_anchors(font, shear)
        font.save(path, overwrite=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print("Merged", total, "shared segments;", len(report), "glyphs polished")


if __name__ == "__main__":
    main()
