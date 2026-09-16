#!/usr/bin/env python3
"""Audit interior joins (inner corners) across the family.

Two questions:

1. Are the junctions decisive? At each concave junction the outline has to
   turn ~50-160 degrees. That turn is delivered either by a KINK (a tangent
   break the spline refit preserved -- crisp) or smeared into a FILLET
   (soft). The kink fraction is the answer. Concavity alone is not a
   junction: the counter of `o` is concave the whole way round, and the
   inside of `(` is one long concave curve. A junction concentrates its turn
   into a short arc, so runs longer than ARC_MAX are reported as design
   curves and left alone.

2. Does the VF hold the corners its own statics have? The statics are traced
   per weight (raster dilation = a true Minkowski sum, which keeps concave
   corners sharp). The VF instead displaces the Regular polyline along vertex
   normals and smooths it, which rounds those corners away as weight rises.
   Run with --vf to compare the shipped VF against the shipped statics.

Usage:
    python3 audit_joins.py            # junction audit, Regular masters
    python3 audit_joins.py --vf       # static vs VF notch sharpness
"""
import os
from master_data import load_master_data
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")

KINK_DEG = 18.0     # tangent break counted as a corner
JOIN_TURN = 45.0    # total concave turn that makes a run a junction
ARC_MAX = 60.0      # longer concave runs are design curves, not corners
SOFT_R = 15.0       # fillet radius at/above this reads as soft
DS = 0.75


def _segs(contour):
    pts = [np.array(contour[0][1], float)]
    out = []
    for s in contour[1:]:
        p0 = pts[-1]
        if s[0] == "line":
            p3 = np.array(s[1], float)
            out.append((p0, p0 + (p3 - p0) / 3, p0 + 2 * (p3 - p0) / 3, p3))
        else:
            p1, p2, p3 = (np.array(p, float) for p in s[1:])
            out.append((p0, p1, p2, p3))
        pts.append(out[-1][3])
    if not np.allclose(pts[-1], pts[0]):
        p0, p3 = pts[-1], pts[0]
        out.append((p0, p0 + (p3 - p0) / 3, p0 + 2 * (p3 - p0) / 3, p3))
    return out


def _d1(s, t):
    p0, p1, p2, p3 = s
    return (3 * (1 - t) ** 2 * (p1 - p0) + 6 * (1 - t) * t * (p2 - p1)
            + 3 * t ** 2 * (p3 - p2))


def _d2(s, t):
    p0, p1, p2, p3 = s
    return 6 * (1 - t) * (p2 - 2 * p1 + p0) + 6 * t * (p3 - 2 * p2 + p1)


def _at(s, t):
    p0, p1, p2, p3 = s
    return ((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1
            + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3)


def _curv(s, t):
    v, a = _d1(s, t), _d2(s, t)
    sp = float(np.hypot(v[0], v[1]))
    if sp < 1e-9:
        return 0.0
    return float((v[0] * a[1] - v[1] * a[0]) / sp ** 3)


def _area(segs, n=24):
    p = np.array([_at(s, t) for s in segs for t in np.linspace(0, 1, n, endpoint=False)])
    x, y = p[:, 0], p[:, 1]
    return 0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


def junctions(contours):
    """-> list of dicts; ink is on the left once the outer winding is
    normalised, so turn < 0 is concave (an inner join)."""
    allseg = [_segs(c) for c in contours]
    areas = [_area(s) for s in allseg]
    oi = int(np.argmax(np.abs(areas)))
    ink = 1.0 if areas[oi] > 0 else -1.0
    out = []
    for ci, segs in enumerate(allseg):
        turn, R, pos, kink = [], [], [], []
        for i, s in enumerate(segs):
            a, b = _d1(segs[i - 1], 1.0), _d1(s, 0.0)
            ang = 0.0
            if np.hypot(*a) > 1e-9 and np.hypot(*b) > 1e-9:
                ang = np.degrees(np.arctan2(a[0] * b[1] - a[1] * b[0], a @ b)) * ink
            L = sum(float(np.hypot(*(_at(s, t + .02) - _at(s, t))))
                    for t in np.linspace(0, .98, 50))
            n = max(2, int(round(L / DS)))
            for j, t in enumerate(np.linspace(0, 1, n, endpoint=False)):
                k = _curv(s, t) * ink
                turn.append(np.degrees(k * (L / n)))
                R.append(1.0 / abs(k) if abs(k) > 1e-9 else 9e9)
                pos.append(_at(s, t))
                kink.append(ang if j == 0 else 0.0)
        turn = np.array(turn); R = np.array(R)
        kink = np.array(kink); pos = np.array(pos)
        tot = turn + kink
        n = len(tot)
        seen = np.zeros(n, bool)
        for st in range(n):
            if seen[st] or tot[st] >= 0:
                continue
            idx = [st]; seen[st] = True
            for step in (1, -1):
                j = (st + step) % n
                while tot[j] < 0 and not seen[j]:
                    seen[j] = True
                    idx.append(j) if step == 1 else idx.insert(0, j)
                    j = (j + step) % n
            T = float(np.sum(tot[idx]))
            if abs(T) < JOIN_TURN:
                continue
            K = float(np.sum(kink[idx]))
            c = idx[int(np.argmin(kink[idx]) if abs(K) > abs(T) * 0.5
                        else np.argmin(R[idx]))]
            out.append({"outer": ci == oi, "turn": T, "kink_frac": abs(K) / abs(T),
                        "R": float(np.min(R[idx])), "arc": len(idx) * DS,
                        "pos": (float(pos[c][0]), float(pos[c][1]))})
    return out


def report_static():
    gc = load_master_data(os.path.join(BUILD, "masters.json"))
    gc = gc["masters"]["Regular"]["contours"]
    rows = [(g, r) for g, c in gc.items() for r in junctions(c) if r["outer"]]
    corners = [(g, r) for g, r in rows if r["arc"] <= ARC_MAX]
    curves = len(rows) - len(corners)
    kf = np.array([r["kink_frac"] for _, r in corners])
    print(f"glyphs {len(gc)}: {len(corners)} interior junctions "
          f"({curves} concave design curves ignored)")
    print(f"kink fraction: median {np.median(kf):.2f} -- "
          f"{(kf > 0.5).mean()*100:.0f}% of junctions are delivered by a sharp kink")
    soft = [(g, r) for g, r in corners if r["kink_frac"] <= 0.5 and r["R"] >= SOFT_R]
    print(f"soft junctions (kink_frac<=0.5, R>={SOFT_R}u, stroke=124u): {len(soft)}")
    for g, r in sorted(soft, key=lambda x: -x[1]["R"]):
        print(f"   {g:12s} turn {r['turn']:6.0f}  R {r['R']:5.1f}u  "
              f"at ({r['pos'][0]:.0f},{r['pos'][1]:.0f})")


def report_vf():
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from notch_probe import notch
    vfp = os.path.join(ROOT, "fonts", "variable", "SunnyMarker[opsz,wght].ttf")
    pairs = [("Light", 300), ("Regular", 400), ("Medium", 500), ("Bold", 700)]
    print("Sharpest interior notch, turn over a +-8u window "
          "(more negative = sharper)\n")
    print(f"{'glyph':6s}" + "".join(f"{s:>11s}{'':>10s}" for s, _ in pairs))
    print(f"{'':6s}" + "".join(f"{'static':>11s}{'VF':>10s}" for _ in pairs))
    for g in ("V", "W", "M", "N", "K", "Y", "X", "A", "v", "w", "x", "y"):
        row = f"{g:6s}"
        for style, wght in pairs:
            st = TTFont(os.path.join(BUILD, f"SunnyMarker-{style}.otf"))
            vf = instancer.instantiateVariableFont(TTFont(vfp),
                                                   {"wght": wght, "opsz": 36})
            row += f"{notch(st, g)[1]:11.0f}{notch(vf, g)[1]:10.0f}"
        print(row)


if __name__ == "__main__":
    report_vf() if "--vf" in sys.argv else report_static()
