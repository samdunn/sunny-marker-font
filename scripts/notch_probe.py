#!/usr/bin/env python3
"""Locate and measure the sharpness of concave notches in a shipped font.

Works off the rendered outline (CFF or TT) so it measures what actually
ships. The notch tip is the most concave point by windowed turn; its
sharpness is the total turn concentrated within +-HALF_W units of arc --
a knife-sharp notch turns ~150 deg, a rounded one much less.
"""
import numpy as np
from fontTools.pens.basePen import BasePen

WIN = 8.0      # units either side for the turn window


class Flat(BasePen):
    def __init__(self, gs):
        super().__init__(gs)
        self.polys = []
        self.cur = []

    def _moveTo(self, p):
        self.cur = [p]

    def _lineTo(self, p):
        self.cur.append(p)

    def _curveToOne(self, p1, p2, p3):
        p0 = np.array(self.cur[-1], float)
        for i in range(1, 25):
            t = i / 24
            self.cur.append(tuple((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * np.array(p1)
                                  + 3 * (1 - t) * t ** 2 * np.array(p2) + t ** 3 * np.array(p3)))

    def _qCurveToOne(self, p1, p2):
        p0 = np.array(self.cur[-1], float)
        for i in range(1, 17):
            t = i / 16
            self.cur.append(tuple((1 - t) ** 2 * p0 + 2 * (1 - t) * t * np.array(p1)
                                  + t ** 2 * np.array(p2)))

    def _closePath(self):
        if self.cur:
            self.polys.append(self.cur)
            self.cur = []

    def _endPath(self):
        self._closePath()


def polys_of(font, g):
    gs = font.getGlyphSet()
    p = Flat(gs)
    gs[g].draw(p)
    p._closePath()
    return [np.array(x, float) for x in p.polys if len(x) > 8]


def resample(poly, step=1.0):
    d = np.linalg.norm(np.diff(poly, axis=0, append=poly[:1]), axis=1)
    cum = np.concatenate([[0], np.cumsum(d)])
    L = cum[-1]
    n = max(16, int(L / step))
    t = np.linspace(0, L, n, endpoint=False)
    out = np.empty((n, 2))
    j = 0
    for i, tt in enumerate(t):
        while j < len(d) - 1 and cum[j + 1] < tt:
            j += 1
        a = (tt - cum[j]) / max(d[j], 1e-9)
        out[i] = poly[j] * (1 - a) + poly[(j + 1) % len(poly)] * a
    return out


def signed_area(p):
    x, y = p[:, 0], p[:, 1]
    return 0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


def turns(poly, ink, win=WIN):
    p = resample(poly, 1.0)
    k = max(1, int(round(win)))
    prv = np.roll(p, k, axis=0)
    nxt = np.roll(p, -k, axis=0)
    t1, t2 = p - prv, nxt - p
    cross = t1[:, 0] * t2[:, 1] - t1[:, 1] * t2[:, 0]
    dot = (t1 * t2).sum(axis=1)
    return p, np.degrees(np.arctan2(cross, dot)) * ink


def notch(font, g):
    """-> (tip_xy, turn_deg) of the sharpest concave notch."""
    ps = polys_of(font, g)
    outer = max(ps, key=lambda p: abs(signed_area(p)))
    ink = 1.0 if signed_area(outer) > 0 else -1.0
    best = None
    for poly in ps:
        p, tn = turns(poly, ink)
        i = int(np.argmin(tn))
        if best is None or tn[i] < best[1]:
            best = ((float(p[i][0]), float(p[i][1])), float(tn[i]))
    return best
