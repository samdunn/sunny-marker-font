"""Read actual curve geometry for QA (never treat handles as ink vertices)."""

import numpy as np
from fontTools.pens.basePen import BasePen


class FlattenPen(BasePen):
    def __init__(self, glyph_set):
        super().__init__(glyph_set)
        self.contours = []
        self.current = []

    def _moveTo(self, point):
        self.current = [np.array(point, float)]

    def _lineTo(self, point):
        self.current.append(np.array(point, float))

    def _qCurveToOne(self, control, end):
        a, b, c = self.current[-1], np.array(control), np.array(end)
        length = np.linalg.norm(b - a) + np.linalg.norm(c - b)
        t = np.linspace(0, 1, max(3, int(np.ceil(length))) + 1)[1:, None]
        self.current.extend((1 - t) ** 2 * a + 2 * (1 - t) * t * b + t * t * c)

    def _curveToOne(self, control1, control2, end):
        a, b, c, d = (
            self.current[-1],
            np.array(control1),
            np.array(control2),
            np.array(end),
        )
        length = np.linalg.norm(b - a) + np.linalg.norm(c - b) + np.linalg.norm(d - c)
        t = np.linspace(0, 1, max(3, int(np.ceil(length))) + 1)[1:, None]
        self.current.extend(
            (1 - t) ** 3 * a
            + 3 * (1 - t) ** 2 * t * b
            + 3 * (1 - t) * t * t * c
            + t**3 * d
        )

    def _closePath(self):
        self.contours.append(np.array(self.current))
        self.current = []


def contours(glyph_set, name):
    pen = FlattenPen(glyph_set)
    glyph_set[name].draw(pen)
    return pen.contours


def boundary(glyph_set, name):
    """Sample ink edges at no more than one-unit spacing, including lines."""
    result = []
    for poly in contours(glyph_set, name):
        edges = np.roll(poly, -1, axis=0) - poly
        steps = np.maximum(1, np.ceil(np.linalg.norm(edges, axis=1)).astype(int))
        indexes = np.repeat(np.arange(len(poly)), steps)
        offsets = np.repeat(np.r_[0, steps.cumsum()[:-1]], steps)
        t = (np.arange(steps.sum()) - offsets) / steps[indexes]
        result.append(poly[indexes] + edges[indexes] * t[:, None])
    return np.concatenate(result) if result else np.empty((0, 2))


def assert_w_structure(glyph_set):
    """A W must retain both tall strokes and have no enclosed counter."""
    import pathops

    path = pathops.Path()
    glyph_set["W"].draw(path.getPen())
    clean = pathops.simplify(path)
    assert len(list(clean.contours)) == 1, "W has an unintended counter or piece"
    polys = contours(glyph_set, "W")
    ymax = max(p[:, 1].max() for p in polys)
    ymin = min(p[:, 1].min() for p in polys)
    level = ymin + (ymax - ymin) * 0.85
    crossings = sum(
        int(np.count_nonzero((p[:, 1] > level) != (np.roll(p[:, 1], -1) > level)))
        for p in polys
    )
    assert crossings == 4, "W must have two intact upper strokes"
