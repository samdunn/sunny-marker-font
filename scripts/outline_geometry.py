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
        length = np.linalg.norm(b-a)+np.linalg.norm(c-b)
        t = np.linspace(0, 1, max(3, int(np.ceil(length)))+1)[1:, None]
        self.current.extend((1-t)**2*a+2*(1-t)*t*b+t*t*c)

    def _curveToOne(self, control1, control2, end):
        a, b, c, d = self.current[-1], np.array(control1), np.array(control2), np.array(end)
        length = np.linalg.norm(b-a)+np.linalg.norm(c-b)+np.linalg.norm(d-c)
        t = np.linspace(0, 1, max(3, int(np.ceil(length)))+1)[1:, None]
        self.current.extend((1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d)

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
        for a, b in zip(poly, np.roll(poly, -1, axis=0)):
            steps = max(1, int(np.ceil(np.linalg.norm(b-a))))
            t = np.arange(steps)[:, None]/steps
            result.extend(a+(b-a)*t)
    return np.array(result)
