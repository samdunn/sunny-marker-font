"""Replace sub-nib needles with compatible, bounded curve fillets.

Polygon reduction can turn a tiny rounded join back into two nearly parallel
segments. Round those joins in the final cubic sources, after fitting, so the
correction survives simplification. Every master receives the same segments.
"""

from pathlib import Path

import numpy as np
from ufoLib2 import Font

ROOT = Path(__file__).resolve().parents[1]


def split(curve, t):
    a = curve[:-1] * (1 - t) + curve[1:] * t
    b = a[:-1] * (1 - t) + a[1:] * t
    c = b[0] * (1 - t) + b[1] * t
    return np.array([curve[0], a[0], b[0], c]), np.array([c, b[1], a[2], curve[3]])


def trim(curve, start, end):
    _, right = split(curve, start)
    left, _ = split(right, (end - start) / (1 - start))
    return left


def segment_curves(contour):
    points = contour.points
    endpoints = [i for i, p in enumerate(points) if p.type in ("line", "curve")]
    curves, kinds = [], []
    for a, b in zip(endpoints, endpoints[1:] + endpoints[:1]):
        indexes = (
            list(range(a, b + 1))
            if b > a
            else list(range(a, len(points))) + list(range(b + 1))
        )
        coords = np.array([(points[i].x, points[i].y) for i in indexes])
        kind = points[b].type
        if kind == "line":
            coords = coords[0] + np.linspace(0, 1, 4)[:, None] * (
                coords[-1] - coords[0]
            )
        assert coords.shape == (4, 2)
        curves.append(coords)
        kinds.append(kind)
    return np.array(curves), kinds


def fillet_contours(curves, distance=10):
    """curves: (masters, segments, four control points, xy)."""
    incoming = np.roll(curves[:, :, 3] - curves[:, :, 2], 1, axis=1)
    outgoing = curves[:, :, 1] - curves[:, :, 0]
    length = np.linalg.norm(incoming, axis=2) * np.linalg.norm(outgoing, axis=2)
    cosine = (incoming * outgoing).sum(axis=2) / np.maximum(length, 1e-12)
    targets = np.any((cosine < np.cos(np.radians(145))) & (length > 1e-8), axis=0)
    if not targets.any():
        return None, targets
    results = []
    for master in curves:
        trimmed = []
        for i, curve in enumerate(master):
            t = np.linspace(0, 1, 65)[:, None]
            samples = (
                (1 - t) ** 3 * curve[0]
                + 3 * (1 - t) ** 2 * t * curve[1]
                + 3 * (1 - t) * t * t * curve[2]
                + t**3 * curve[3]
            )
            arc = np.r_[0, np.cumsum(np.linalg.norm(np.diff(samples, axis=0), axis=1))]
            cut = min(distance, arc[-1] * 0.25)
            start = float(np.interp(cut, arc, t[:, 0])) if targets[i] else 0
            end = (
                float(np.interp(arc[-1] - cut, arc, t[:, 0]))
                if targets[(i + 1) % len(master)]
                else 1
            )
            trimmed.append(trim(curve, start, end))
        result = []
        for i, curve in enumerate(trimmed):
            result.append(curve)
            if targets[(i + 1) % len(master)]:
                a, b = curve[3], trimmed[(i + 1) % len(master)][0]
                corner = master[i, 3]
                result.append(
                    np.array([a, a + 2 * (corner - a) / 3, b + 2 * (corner - b) / 3, b])
                )
        results.append(result)
    return np.array(results), targets


def main():
    paths = sorted((ROOT / "sources").glob("master-*.ufo"))
    fonts = [Font.open(p) for p in paths]
    joins = 0
    for name in fonts[0].keys():
        if name in ("star", "sparkle"):
            continue  # Deliberately pointed doodles.
        for ci in range(len(fonts[0][name].contours)):
            source = [segment_curves(font[name].contours[ci]) for font in fonts]
            assert all(k == source[0][1] for c, k in source)
            rounded, targets = fillet_contours(np.array([c for c, k in source]))
            if rounded is None:
                continue
            kinds = []
            for i, kind in enumerate(source[0][1]):
                kinds.append(kind)
                if targets[(i + 1) % len(targets)]:
                    kinds.append("curve")
            for font, curves in zip(fonts, rounded):
                contour = font[name].contours[ci]
                contour.points.clear()
                # A contour point's type identifies its incoming segment.
                from ufoLib2.objects import Point

                contour.points.append(
                    Point(
                        float(curves[0, 0, 0]), float(curves[0, 0, 1]), type=kinds[-1]
                    )
                )
                for i, (curve, kind) in enumerate(zip(curves, kinds)):
                    if kind == "curve":
                        for x, y in curve[1:3]:
                            contour.points.append(Point(float(x), float(y)))
                    if i < len(curves) - 1:
                        contour.points.append(
                            Point(float(curve[3, 0]), float(curve[3, 1]), type=kind)
                        )
            joins += int(targets.sum())
    for font, path in zip(fonts, paths):
        font.save(path, overwrite=True)
    print("Rounded", joins, "shared joins across", len(fonts), "masters")


if __name__ == "__main__":
    main()
