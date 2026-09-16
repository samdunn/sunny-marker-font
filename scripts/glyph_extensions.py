#!/usr/bin/env python3
"""GF Latin Core extension: accent marks, symbols, and composed glyphs.

Marks and new symbols are generated as parametric marker strokes: a
skeleton polyline gets seeded hand-wobble, is buffered to a round-capped
outline at the family stroke width (scaled per weight), then smoothed by
the same spline refit as traced glyphs. Accented letters are composed from
the per-weight base outlines with anchors measured from the ink.
Overlays (Ø, €, Ł, ¥…) rely on nonzero winding, so overlapping contours
render as a union without rasterizing.
"""
import numpy as np

CAPU = 700.0
MARK_GAP = 34.0        # gap between base top and mark bottom
MARK_STROKE_F = 0.86   # marks drawn slightly lighter than the base stroke

# ---------------------------------------------------------------- helpers

def _open_resample(pts, spacing=4.0):
    pts = np.asarray(pts, float)
    d = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    L = d.sum()
    n = max(6, int(round(L / spacing)))
    cum = np.concatenate([[0], np.cumsum(d)])
    t = np.linspace(0, L, n + 1)
    out = np.empty((n + 1, 2))
    j = 0
    for i, tt in enumerate(t):
        while j < len(d) - 1 and cum[j + 1] < tt:
            j += 1
        seg = max(cum[j + 1] - cum[j], 1e-9)
        a = (tt - cum[j]) / seg
        out[i] = pts[j] * (1 - a) + pts[j + 1] * a
    return out


def _normals_open(p):
    t = np.gradient(p, axis=0)
    ln = np.linalg.norm(t, axis=1, keepdims=True)
    ln[ln == 0] = 1
    t = t / ln
    return np.stack([t[:, 1], -t[:, 0]], axis=1)


def stroke_contour(skel, w, seed=0, wobble=2.5):
    """Round-capped marker stroke along a skeleton -> closed polygon
    contour in segment format."""
    p = _open_resample(skel, 4.0)
    if wobble > 0:
        rng = np.random.default_rng(seed)
        arclen = np.concatenate([[0], np.cumsum(
            np.linalg.norm(np.diff(p, axis=0), axis=1))])
        wl = rng.uniform(75, 115)
        ph = rng.uniform(0, 2 * np.pi)
        n0 = _normals_open(p)
        p = p + n0 * (wobble * np.sin(2 * np.pi * arclen / wl + ph))[:, None]
    n = _normals_open(p)
    r = w / 2.0
    right = p + n * r
    left = p - n * r

    def cap(center, a0, a1, steps=10):
        aa = np.linspace(a0, a1, steps)
        return np.stack([center[0] + r * np.cos(aa),
                         center[1] + r * np.sin(aa)], axis=1)

    def ang(v):
        return np.arctan2(v[1], v[0])

    end_n = n[-1]
    start_n = n[0]
    poly = np.vstack([
        right,
        cap(p[-1], ang(end_n), ang(end_n) + np.pi),
        left[::-1],
        cap(p[0], ang(-start_n), ang(-start_n) + np.pi),
    ])
    segs = [("move", tuple(poly[0]))]
    segs += [("line", tuple(q)) for q in poly[1:]]
    return segs


def circle_contour(cx, cy, r, steps=48, ccw=False):
    aa = np.linspace(0, 2 * np.pi, steps, endpoint=False)
    if ccw:
        aa = aa[::-1]
    pts = np.stack([cx + r * np.cos(aa), cy + r * np.sin(aa)], axis=1)
    segs = [("move", tuple(pts[0]))]
    segs += [("line", tuple(q)) for q in pts[1:]]
    return segs


def bare_stem(polys, ref_polys, simplify, flatten, seed=41, wobble=2.0):
    """Bare marker stem taken from a barred letter (the sheet's I).

    Scans the ink for the rows where only the stem is present, fits its
    centre line, then re-strokes that line at the measured stem width. The
    source is already dilated for the weight, so the result inherits the
    weight without extra parameters.

    polys/ref_polys: flattened ink of the source (barred I) and of the
    reference flat-cap stem (H). The stem takes H's vertical span, not the
    source's: the source's bars are drawn past cap height, and a bare stem
    that overshot with them would sit taller than every other flat cap —
    and would push the accents on Í/Ì past the family's usWinAscent.
    """
    ys = np.concatenate([p[:, 1] for p in polys])
    y0, y1 = float(ys.min()), float(ys.max())
    rows = np.linspace(y0, y1, 240)[1:-1]
    width = np.full(len(rows), np.nan)
    center = np.full(len(rows), np.nan)
    for poly in polys:
        a, b = poly, np.roll(poly, -1, axis=0)
        for i, y in enumerate(rows):
            hit = ((a[:, 1] - y) * (b[:, 1] - y) <= 0) & (
                np.abs(a[:, 1] - b[:, 1]) > 1e-9)
            if not hit.any():
                continue
            aa, bb = a[hit], b[hit]
            t = (y - aa[:, 1]) / (bb[:, 1] - aa[:, 1])
            xs = aa[:, 0] + t * (bb[:, 0] - aa[:, 0])
            lo, hi = float(xs.min()), float(xs.max())
            if np.isnan(width[i]):
                width[i], center[i] = hi - lo, (lo + hi) / 2
            else:  # more than one contour on this row: take the full span
                width[i] = max(width[i], hi - lo)
    ok = ~np.isnan(width)
    # reference width from the middle third (stem only on a barred I); the
    # global min would land on the tapered tip of a bar instead
    n = len(rows)
    narrow = ok & (width <= 1.35 * float(np.nanmedian(width[n // 3:2 * n // 3])))
    # longest contiguous run of stem-only rows
    best = run = None
    for i, flag in enumerate(narrow):
        if flag:
            run = (i, i) if run is None else (run[0], i)
            if best is None or run[1] - run[0] > best[1] - best[0]:
                best = run
        else:
            run = None
    lo, hi = best
    a_, b_ = np.polyfit(rows[lo:hi + 1], center[lo:hi + 1], 1)
    w = float(np.median(width[lo:hi + 1]))
    r = w / 2.0
    # inset the skeleton by the cap radius so the round ends land on y0/y1
    skel = [(a_ * (y0 + r) + b_, y0 + r), (a_ * (y1 - r) + b_, y1 - r)]
    stem = simplify([stroke_contour(skel, w, seed=seed, wobble=wobble)])
    # squash onto H's span, measured on flattened ink (the spline refit's
    # control points bulge well past the round caps, so _bbox would lie)
    ry = np.concatenate([p[:, 1] for p in ref_polys])
    sy = np.concatenate([p[:, 1] for p in (flatten(c) for c in stem)])
    fy = float(np.ptp(ry)) / float(np.ptp(sy))
    sy0, ry0 = float(sy.min()), float(ry.min())
    return [[(s[0], *[(x, (y - sy0) * fy + ry0) for (x, y) in s[1:]])
             for s in c] for c in stem]


def unbarred_j(polys, cap_top, simplify):
    """Keep the drawn J hook; replace only its barred top with a round nib.

    Measure the existing upper stem, clip below the crossbar, and extend its
    two flanks to a rounded cap at the capital height. No new hook is drawn.
    """
    if len(polys) != 1:
        raise ValueError("Expected the traced capital J to have one contour")
    poly = np.asarray(polys[0], float)
    cut = cap_top * 0.74

    def crossings(y):
        a, b = poly, np.roll(poly, -1, axis=0)
        hit = (a[:, 1] > y) != (b[:, 1] > y)
        a, b = a[hit], b[hit]
        xs = np.sort(a[:, 0] + (y - a[:, 1]) * (b[:, 0] - a[:, 0])
                     / (b[:, 1] - a[:, 1]))
        if len(xs) != 2:
            raise ValueError(f"Expected two J stem edges at {y}, found {len(xs)}")
        return xs

    rows = np.linspace(cap_top * 0.58, cut, 30)
    spans = np.array([crossings(y) for y in rows])
    left_slope = np.polyfit(rows, spans[:, 0], 1)[0]
    right_slope = np.polyfit(rows, spans[:, 1], 1)[0]
    center_fit = np.polyfit(rows, spans.mean(axis=1), 1)
    left, right = crossings(cut)
    radius = (right - left) / 2
    cap_y = cap_top - radius
    cap_x = float(np.polyval(center_fit, cap_y))

    def flank(x, top_x, slope):
        a = np.array([x, cut])
        d = np.array([top_x, cap_y])
        dy = (cap_y - cut) / 3
        b, c = a + [slope * dy, dy], d - [0, dy]
        t = np.linspace(0, 1, 20)[:, None]
        return (1-t)**3*a + 3*(1-t)**2*t*b + 3*(1-t)*t**2*c + t**3*d

    theta = np.linspace(np.pi, 0, 33)
    arc = np.column_stack([cap_x + radius * np.cos(theta),
                           cap_y + radius * np.sin(theta)])
    top = np.vstack([flank(left, cap_x-radius, left_slope), arc[1:],
                     flank(right, cap_x+radius, right_slope)[-2::-1]])

    # Clip to the lower half-plane. The one new horizontal edge marks where
    # the measured extension belongs; preserve the original contour winding.
    clipped = []
    for a, b in zip(poly, np.roll(poly, -1, axis=0)):
        if (a[1] <= cut) != (b[1] <= cut):
            clipped.append(a + (cut-a[1]) / (b[1]-a[1]) * (b-a))
        if b[1] <= cut:
            clipped.append(b)
    result = []
    inserted = 0
    for a, b in zip(clipped, clipped[1:] + clipped[:1]):
        result.append(a)
        if abs(a[1]-cut) < 1e-6 and abs(b[1]-cut) < 1e-6:
            extension = top if a[0] < b[0] else top[::-1]
            result.extend(extension[1:-1])
            inserted += 1
    if inserted != 1:
        raise ValueError(f"Expected one clipped J crossbar edge, found {inserted}")
    return simplify([[('move', tuple(result[0]))]
                     + [('line', tuple(p)) for p in result[1:]]])


def upright_y_stem(contours, cap_top):
    """Bring the capital Y's diagonal tail toward a gently upright stem.

    Retain the traced fork and nib: translate points horizontally only below
    the join, easing the correction in with zero slope at its upper boundary.
    Applied before accent composition, this also corrects every capital Y
    accent without touching the lowercase y or its descender.
    """
    join = cap_top * 0.60
    ease = cap_top * 0.115

    def point(x, y):
        below = max(0.0, join - y)
        shift = 0.32 * (below - ease * (1 - np.exp(-below / ease)))
        return x + shift, y

    return [[(seg[0], *(point(x, y) for x, y in seg[1:]))
             for seg in contour] for contour in contours]


def _bbox(contours):
    xs = [p[0] for c in contours for s in c for p in s[1:]]
    ys = [p[1] for c in contours for s in c for p in s[1:]]
    return min(xs), min(ys), max(xs), max(ys)


def _tr(contours, dx, dy):
    return [[(s[0], *[(x + dx, y + dy) for (x, y) in s[1:]]) for s in c]
            for c in contours]


def _scale(contours, fx, fy=None, cx=0.0, cy=0.0):
    fy = fx if fy is None else fy
    return [[(s[0], *[((x - cx) * fx + cx, (y - cy) * fy + cy)
                      for (x, y) in s[1:]]) for s in c] for c in contours]


def _rot180(contours, cx, cy):
    return [[(s[0], *[(2 * cx - x, 2 * cy - y) for (x, y) in s[1:]])
             for s in c] for c in contours]


def _signed_area_contour(c):
    pts = [p for s in c for p in s[1:]]
    x = np.array([p[0] for p in pts])
    y = np.array([p[1] for p in pts])
    return 0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


def _match_winding(overlay, reference):
    """Flip the overlay as a whole so its OUTER contour's winding matches
    the reference outer contour (nonzero fill then unions instead of
    punching holes). Flipping per-contour would also flip the overlay's
    own counters (the eye of e in ae/oe), filling them solid — the
    overlay's internal hole structure must be preserved."""
    ref_sign = np.sign(_signed_area_contour(
        max(reference, key=lambda c: abs(_signed_area_contour(c)))))
    ov_sign = np.sign(_signed_area_contour(
        max(overlay, key=lambda c: abs(_signed_area_contour(c)))))
    if ov_sign == ref_sign:
        return list(overlay)
    out = []
    for c in overlay:
        pts = [c[0][1]] + [p for s in c[1:] for p in s[1:]]
        pts = pts[::-1]
        out.append([("move", pts[0])] + [("line", p) for p in pts[1:]])
    return out


# ---------------------------------------------------------------- marks

def build_marks(stroke_w, seed_base=7):
    """Mark contours, each centered at x=0. Above-marks sit with bottom at
    y=0; below-marks hang with top at y=0. Sized for lowercase."""
    s = stroke_w * 0.78
    M = {}
    M["grave"] = [stroke_contour([(-52, 160), (48, 10)], s, seed=seed_base + 1,
                                 wobble=1.0)]
    M["acute"] = [stroke_contour([(52, 160), (-48, 10)], s, seed=seed_base + 2,
                                 wobble=1.0)]
    M["circumflex"] = [stroke_contour([(-105, 0), (0, 130), (105, 0)], s * 0.94,
                                      seed=seed_base + 3, wobble=1.0)]
    M["caron"] = [stroke_contour([(-105, 130), (0, 0), (105, 130)], s * 0.94,
                                 seed=seed_base + 4, wobble=1.0)]
    tx = np.linspace(-118, 118, 40)
    ty = 40 * np.sin(np.linspace(0, 2 * np.pi, 40))
    M["tilde"] = [stroke_contour(np.stack([tx, ty + 48], axis=1), s * 0.88,
                                 seed=seed_base + 5, wobble=0)]
    M["macron"] = [stroke_contour([(-112, 42), (112, 48)], s * 0.88,
                                  seed=seed_base + 6, wobble=1.0)]
    ba = np.linspace(np.pi * 1.12, np.pi * 1.88, 24)
    M["breve"] = [stroke_contour(
        np.stack([98 * np.cos(ba), 132 + 92 * np.sin(ba)], axis=1), s * 0.88,
        seed=seed_base + 7, wobble=0)]
    M["dotaccent"] = [circle_contour(0, 62, s * 0.62)]
    M["dieresis"] = [circle_contour(-95, 60, s * 0.58),
                     circle_contour(95, 60, s * 0.58)]
    # ring hole must survive every weight: floor the inner radius so the
    # annulus never seals (76 - 0.72*s closed to ~6u at Regular and up)
    M["ring"] = [circle_contour(0, 78, 76),
                 circle_contour(0, 78, max(76 - s * 0.52, 32), ccw=True)]
    M["hungarumlaut"] = [stroke_contour([(-20, 158), (-85, 10)], s * 0.9,
                                        seed=seed_base + 8, wobble=1.0),
                         stroke_contour([(112, 158), (47, 10)], s * 0.9,
                                        seed=seed_base + 9, wobble=1.0)]
    # below marks (top at 0)
    # A continuous hook, not the old three tight polygonal elbows. Offsetting
    # those elbows at Light folded the inner edge into disconnected flecks.
    t = np.linspace(0, 1, 24)[:, None]
    def cubic(a, b, c, d):
        return ((1-t)**3 * np.array(a) + 3*(1-t)**2*t * np.array(b)
                + 3*(1-t)*t**2 * np.array(c) + t**3 * np.array(d))
    hook = np.vstack([cubic((6, -5), (5, -35), (-18, -48), (-10, -65))[:-1],
                      cubic((-10, -65), (90, -66), (58, -177), (-30, -148))])
    M["cedilla"] = [stroke_contour(hook, s * 0.60,
                                   seed=seed_base + 10, wobble=0)]
    M["ogonek"] = [stroke_contour([(8, -2), (-44, -58), (-22, -130), (50, -116)],
                                  s * 0.78, seed=seed_base + 11, wobble=0)]
    return M


# ------------------------------------------------------------ composites

# name -> (base, mark, position)  position: "top" | "below" | "belowright"
LATIN = {}
for b, marks in {
    "A": [("grave", "Agrave"), ("acute", "Aacute"), ("circumflex", "Acircumflex"),
          ("tilde", "Atilde"), ("dieresis", "Adieresis"), ("ring", "Aring"),
          ("macron", "Amacron"), ("breve", "Abreve"), ("ogonek", "Aogonek")],
    "C": [("acute", "Cacute"), ("dotaccent", "Cdotaccent"), ("caron", "Ccaron")],
    "D": [("caron", "Dcaron")],
    "E": [("grave", "Egrave"), ("acute", "Eacute"), ("circumflex", "Ecircumflex"),
          ("dieresis", "Edieresis"), ("macron", "Emacron"),
          ("dotaccent", "Edotaccent"), ("ogonek", "Eogonek"), ("caron", "Ecaron")],
    "G": [("breve", "Gbreve"), ("dotaccent", "Gdotaccent")],
    "I": [("grave", "Igrave"), ("acute", "Iacute"), ("circumflex", "Icircumflex"),
          ("dieresis", "Idieresis"), ("macron", "Imacron"),
          ("ogonek", "Iogonek"), ("dotaccent", "Idotaccent")],
    "K": [],
    "L": [("acute", "Lacute"), ("caron", "Lcaron")],
    "N": [("tilde", "Ntilde"), ("acute", "Nacute"), ("caron", "Ncaron")],
    "O": [("grave", "Ograve"), ("acute", "Oacute"), ("circumflex", "Ocircumflex"),
          ("tilde", "Otilde"), ("dieresis", "Odieresis"),
          ("macron", "Omacron"), ("hungarumlaut", "Ohungarumlaut")],
    "R": [("acute", "Racute"), ("caron", "Rcaron")],
    "S": [("acute", "Sacute"), ("caron", "Scaron"), ("cedilla", "Scedilla")],
    "T": [("caron", "Tcaron")],
    "U": [("grave", "Ugrave"), ("acute", "Uacute"), ("circumflex", "Ucircumflex"),
          ("dieresis", "Udieresis"), ("macron", "Umacron"), ("ring", "Uring"),
          ("hungarumlaut", "Uhungarumlaut"), ("ogonek", "Uogonek")],
    "W": [("circumflex", "Wcircumflex"), ("grave", "Wgrave"),
          ("acute", "Wacute"), ("dieresis", "Wdieresis")],
    "Y": [("acute", "Yacute"), ("circumflex", "Ycircumflex"),
          ("dieresis", "Ydieresis"), ("grave", "Ygrave")],
    "Z": [("acute", "Zacute"), ("dotaccent", "Zdotaccent"), ("caron", "Zcaron")],
}.items():
    for mk, name in marks:
        LATIN[name] = (b, mk, "below" if mk in ("cedilla", "ogonek") else "top")

for b, marks in {
    "a": [("grave", "agrave"), ("acute", "aacute"), ("circumflex", "acircumflex"),
          ("tilde", "atilde"), ("dieresis", "adieresis"), ("ring", "aring"),
          ("macron", "amacron"), ("breve", "abreve"), ("ogonek", "aogonek")],
    "c": [("acute", "cacute"), ("dotaccent", "cdotaccent"), ("caron", "ccaron")],
    "e": [("grave", "egrave"), ("acute", "eacute"), ("circumflex", "ecircumflex"),
          ("dieresis", "edieresis"), ("macron", "emacron"),
          ("dotaccent", "edotaccent"), ("ogonek", "eogonek"), ("caron", "ecaron")],
    "g": [("breve", "gbreve"), ("dotaccent", "gdotaccent")],
    "l": [("acute", "lacute")],
    "n": [("tilde", "ntilde"), ("acute", "nacute"), ("caron", "ncaron")],
    "o": [("grave", "ograve"), ("acute", "oacute"), ("circumflex", "ocircumflex"),
          ("tilde", "otilde"), ("dieresis", "odieresis"),
          ("macron", "omacron"), ("hungarumlaut", "ohungarumlaut")],
    "r": [("acute", "racute"), ("caron", "rcaron")],
    "s": [("acute", "sacute"), ("caron", "scaron"), ("cedilla", "scedilla")],
    "u": [("grave", "ugrave"), ("acute", "uacute"), ("circumflex", "ucircumflex"),
          ("dieresis", "udieresis"), ("macron", "umacron"), ("ring", "uring"),
          ("hungarumlaut", "uhungarumlaut"), ("ogonek", "uogonek")],
    "w": [("circumflex", "wcircumflex"), ("grave", "wgrave"),
          ("acute", "wacute"), ("dieresis", "wdieresis")],
    "y": [("acute", "yacute"), ("circumflex", "ycircumflex"),
          ("dieresis", "ydieresis"), ("grave", "ygrave")],
    "z": [("acute", "zacute"), ("dotaccent", "zdotaccent"), ("caron", "zcaron")],
    "C_c": [],
}.items():
    if b == "C_c":
        continue
    for mk, name in marks:
        LATIN[name] = (b, mk, "below" if mk in ("cedilla", "ogonek") else "top")

LATIN.update({
    "Ccedilla": ("C", "cedilla", "below"), "ccedilla": ("c", "cedilla", "below"),
    "ldot": None,  # unused
    "dotlessi_grave": None,
})
del LATIN["ldot"], LATIN["dotlessi_grave"]

# dotless-based
DOTLESS = {
    "igrave": ("dotlessi", "grave"), "iacute": ("dotlessi", "acute"),
    "icircumflex": ("dotlessi", "circumflex"), "idieresis": ("dotlessi", "dieresis"),
    "imacron": ("dotlessi", "macron"), "iogonek": ("i", "ogonek"),
}

# comma-accent glyphs (uppercase: comma below; ģ gets turned comma above)
COMMA_ACCENT = {
    "Gcommaaccent": ("G", "below"), "gcommaaccent": ("g", "aboveturned"),
    "Kcommaaccent": ("K", "below"), "kcommaaccent": ("k", "below"),
    "Lcommaaccent": ("L", "below"), "lcommaaccent": ("l", "below"),
    "Ncommaaccent": ("N", "below"), "ncommaaccent": ("n", "below"),
    "Scommaaccent": ("S", "below"), "scommaaccent": ("s", "below"),
    "Tcommaaccent": ("T", "below"), "tcommaaccent": ("t", "below"),
}

# caron-as-apostrophe forms
CARON_ALT = {"dcaron": "d", "lcaron": "l", "tcaron": "t"}

EXT_CMAP = {
    # accented Latin-1 + Extended (unicodes resolved by AGL-style table)
    "Agrave": [0xC0], "Aacute": [0xC1], "Acircumflex": [0xC2],
    "Atilde": [0xC3], "Adieresis": [0xC4], "Aring": [0xC5],
    "Ccedilla": [0xC7], "Egrave": [0xC8], "Eacute": [0xC9],
    "Ecircumflex": [0xCA], "Edieresis": [0xCB], "Igrave": [0xCC],
    "Iacute": [0xCD], "Icircumflex": [0xCE], "Idieresis": [0xCF],
    "Ntilde": [0xD1], "Ograve": [0xD2], "Oacute": [0xD3],
    "Ocircumflex": [0xD4], "Otilde": [0xD5], "Odieresis": [0xD6],
    "Ugrave": [0xD9], "Uacute": [0xDA], "Ucircumflex": [0xDB],
    "Udieresis": [0xDC], "Yacute": [0xDD],
    "agrave": [0xE0], "aacute": [0xE1], "acircumflex": [0xE2],
    "atilde": [0xE3], "adieresis": [0xE4], "aring": [0xE5],
    "ccedilla": [0xE7], "egrave": [0xE8], "eacute": [0xE9],
    "ecircumflex": [0xEA], "edieresis": [0xEB], "igrave": [0xEC],
    "iacute": [0xED], "icircumflex": [0xEE], "idieresis": [0xEF],
    "ntilde": [0xF1], "ograve": [0xF2], "oacute": [0xF3],
    "ocircumflex": [0xF4], "otilde": [0xF5], "odieresis": [0xF6],
    "ugrave": [0xF9], "uacute": [0xFA], "ucircumflex": [0xFB],
    "udieresis": [0xFC], "yacute": [0xFD], "ydieresis": [0xFF],
    "Amacron": [0x100], "amacron": [0x101], "Abreve": [0x102],
    "abreve": [0x103], "Aogonek": [0x104], "aogonek": [0x105],
    "Cacute": [0x106], "cacute": [0x107], "Cdotaccent": [0x10A],
    "cdotaccent": [0x10B], "Ccaron": [0x10C], "ccaron": [0x10D],
    "Dcaron": [0x10E], "dcaron": [0x10F],
    "Emacron": [0x112], "emacron": [0x113], "Edotaccent": [0x116],
    "edotaccent": [0x117], "Eogonek": [0x118], "eogonek": [0x119],
    "Ecaron": [0x11A], "ecaron": [0x11B], "Gbreve": [0x11E],
    "gbreve": [0x11F], "Gdotaccent": [0x120], "gdotaccent": [0x121],
    "Gcommaaccent": [0x122], "gcommaaccent": [0x123],
    "Imacron": [0x12A], "imacron": [0x12B], "Iogonek": [0x12E],
    "iogonek": [0x12F], "Idotaccent": [0x130], "dotlessi": [0x131],
    "Kcommaaccent": [0x136], "kcommaaccent": [0x137],
    "Lacute": [0x139], "lacute": [0x13A], "Lcommaaccent": [0x13B],
    "lcommaaccent": [0x13C], "Lcaron": [0x13D], "lcaron": [0x13E],
    "Lslash": [0x141], "lslash": [0x142], "Nacute": [0x143],
    "nacute": [0x144], "Ncommaaccent": [0x145], "ncommaaccent": [0x146],
    "Ncaron": [0x147], "ncaron": [0x148],
    "Ohungarumlaut": [0x150], "ohungarumlaut": [0x151],
    "OE": [0x152], "oe": [0x153], "Racute": [0x154], "racute": [0x155],
    "Rcaron": [0x158], "rcaron": [0x159], "Sacute": [0x15A],
    "sacute": [0x15B], "Scedilla": [0x15E], "scedilla": [0x15F],
    "Scaron": [0x160], "scaron": [0x161], "Tcaron": [0x164],
    "tcaron": [0x165], "Umacron": [0x16A], "umacron": [0x16B],
    "Uring": [0x16E], "uring": [0x16F], "Uhungarumlaut": [0x170],
    "uhungarumlaut": [0x171], "Uogonek": [0x172], "uogonek": [0x173],
    "Wcircumflex": [0x174], "wcircumflex": [0x175], "Ycircumflex": [0x176],
    "ycircumflex": [0x177], "Ydieresis": [0x178], "Zacute": [0x179],
    "zacute": [0x17A], "Zdotaccent": [0x17B], "zdotaccent": [0x17C],
    "Zcaron": [0x17D], "zcaron": [0x17E],
    "Scommaaccent": [0x218], "scommaaccent": [0x219],
    "Tcommaaccent": [0x21A], "tcommaaccent": [0x21B],
    "dotlessj": [0x237],
    "Wgrave": [0x1E80], "wgrave": [0x1E81], "Wacute": [0x1E82],
    "wacute": [0x1E83], "Wdieresis": [0x1E84], "wdieresis": [0x1E85],
    "Ygrave": [0x1EF2], "ygrave": [0x1EF3],
    "germandbls": [0xDF], "Germandbls": [0x1E9E],
    "AE": [0xC6], "ae": [0xE6], "Oslash": [0xD8], "oslash": [0xF8],
    "Thorn": [0xDE], "thorn": [0xFE], "Eth": [0xD0], "eth": [0xF0],
    "Dcroat": [0x110], "dcroat": [0x111], "Hbar": [0x126], "hbar": [0x127],
    # symbols
    "exclamdown": [0xA1], "questiondown": [0xBF], "cent": [0xA2],
    "sterling": [0xA3], "yen": [0xA5], "Euro": [0x20AC],
    "section": [0xA7], "paragraph": [0xB6], "copyright": [0xA9],
    "registered": [0xAE], "trademark": [0x2122], "degree": [0xB0],
    "periodcentered": [0xB7], "bullet": [0x2022], "ellipsis": [0x2026],
    "endash": [0x2013], "emdash": [0x2014], "quotesinglbase": [0x201A],
    "quotedblbase": [0x201E], "guilsinglleft": [0x2039],
    "guilsinglright": [0x203A], "guillemotleft": [0xAB],
    "guillemotright": [0xBB], "multiply": [0xD7], "divide": [0xF7],
    "minus": [0x2212], "ordfeminine": [0xAA], "ordmasculine": [0xBA],
    "asciicircum": [0x5E], "asciitilde": [0x7E], "bar": [0x7C],
    "grave.spacing": [0x60], "macron.spacing": [0xAF],
    "acute.spacing": [0xB4], "dieresis.spacing": [0xA8],
    "cedilla.spacing": [0xB8],
    "circumflex.spacing": [0x2C6], "caron.spacing": [0x2C7],
    "breve.spacing": [0x2D8], "dotaccent.spacing": [0x2D9],
    "ring.spacing": [0x2DA], "ogonek.spacing": [0x2DB],
    "tilde.spacing": [0x2DC], "hungarumlaut.spacing": [0x2DD],
    # combining marks
    "gravecomb": [0x300], "acutecomb": [0x301], "circumflexcomb": [0x302],
    "tildecomb": [0x303], "macroncomb": [0x304], "brevecomb": [0x306],
    "dotaccentcomb": [0x307], "dieresiscomb": [0x308], "ringcomb": [0x30A],
    "hungarumlautcomb": [0x30B], "caroncomb": [0x30C],
    "commaaccentcomb": [0x326], "cedillacomb": [0x327], "ogonekcomb": [0x328],
}

ZERO_ADVANCE = {n for n in EXT_CMAP if n.endswith("comb")}
UNENCODED = ["jacute", "Jacute", "I.ss01"]
CCMP_FEA = ("feature ccmp { sub \\j \\acutecomb by \\jacute; "
            "sub \\J \\acutecomb by \\Jacute; } ccmp;")
# default I is a bare stem; the sheet's barred drawing is the alternate
ALT_FEA = ("feature salt { sub \\I by \\I.ss01; } salt;\n"
           "feature ss01 { featureNames { name \"Barred capital I\"; }; "
           "sub \\I by \\I.ss01; } ss01;\n"
           "feature aalt { feature salt; } aalt;")


def _top_anchor(contours, frac=0.20):
    x0, y0, x1, y1 = _bbox(contours)
    band = y1 - (y1 - y0) * frac
    xs = [p[0] for c in contours for s in c for p in s[1:] if p[1] >= band]
    return (float(np.mean(xs)) if xs else (x0 + x1) / 2, y1)


def _bottom_anchor(contours, frac=0.20, right=False):
    x0, y0, x1, y1 = _bbox(contours)
    band = y0 + (y1 - y0) * frac
    xs = [p[0] for c in contours for s in c for p in s[1:] if p[1] <= band]
    if not xs:
        xs = [(x0 + x1) / 2]
    if right:
        return (float(np.percentile(xs, 88)), y0)
    return (float(np.mean(xs)), y0)


def add_extensions(gc, gw, offset, s_comp, xheight, simplify):
    """Extend glyph_contours (gc) / glyph_width (gw) in place.
    offset/s_comp: weight parameters. simplify: build_font.simplify_contours."""
    stroke_w = (124.0 + 2 * offset) * s_comp
    marks = build_marks(stroke_w)
    marks = {k: simplify(v) for k, v in marks.items()}
    capу = CAPU

    def add(name, contours, width=None):
        x0, _, x1, _ = _bbox(contours)
        gc[name] = _tr(contours, -x0, 0)
        gw[name] = (x1 - x0) if width is None else width

    # dotless bases: strip the contour whose bbox sits fully above x-height
    for src, dst in (("i", "dotlessi"), ("j", "dotlessj")):
        body = [c for c in gc[src] if _bbox([c])[1] < xheight * 0.8]
        add(dst, body)

    def compose(name, base, mark, pos):
        bc = gc[base]
        mc = marks[mark]
        is_cap = base[0].isupper()
        mscale = 0.75 if is_cap else 1.0
        gap = 26.0 if is_cap else MARK_GAP
        mc = _scale(mc, mscale)
        if pos == "top":
            ax, ay = _top_anchor(bc)
            # never below the body top (i-dot removed cases use dotless)
            ay = max(ay, xheight if not is_cap else capу)
            placed = _tr(mc, ax, ay + gap)
        elif pos == "below":
            right = mark == "ogonek"
            ax, ay = _bottom_anchor(bc, right=right)
            placed = _tr(mc, ax, ay + 4)
        else:
            raise ValueError(pos)
        x0b, _, x1b, _ = _bbox(bc)
        merged = bc + placed
        x0m, _, x1m, _ = _bbox(merged)
        gc[name] = _tr(merged, -x0m, 0)
        gw[name] = x1m - x0m

    for name, spec in LATIN.items():
        base, mark, pos = spec
        if base in ("i", "j") and pos == "top":
            base = "dotless" + base
        compose(name, base, mark, pos)
    for name, (base, mark) in DOTLESS.items():
        compose(name, base, mark, "below" if mark == "ogonek" else "top")
    # Idotaccent = I + dot
    compose("Idotaccent", "I", "dotaccent", "top")
    # Dutch j-acute (unencoded, reached via ccmp)
    compose("jacute", "dotlessj", "acute", "top")
    compose("Jacute", "J", "acute", "top")

    # comma accents from the comma glyph
    comma = _scale(gc["comma"], 0.82)
    cx0, cy0, cx1, cy1 = _bbox(comma)
    for name, (base, pos) in COMMA_ACCENT.items():
        bc = gc[base]
        if pos == "below":
            ax, ay = _bottom_anchor(bc)
            placed = _tr(comma, ax - (cx0 + cx1) / 2, ay - 30 - cy1)
        else:  # gcommaaccent: turned comma above
            tc = _rot180(comma, (cx0 + cx1) / 2, (cy0 + cy1) / 2)
            ax, ay = _top_anchor(bc)
            placed = _tr(tc, ax - (cx0 + cx1) / 2, ay + MARK_GAP - cy0)
        merged = bc + placed
        x0m, _, x1m, _ = _bbox(merged)
        gc[name] = _tr(merged, -x0m, 0)
        gw[name] = x1m - x0m

    # caron-as-apostrophe (ď ľ ť)
    q = _scale(gc["quoteright"], 0.9)
    qx0, qy0, qx1, qy1 = _bbox(q)
    for name, base in CARON_ALT.items():
        bc = gc[base]
        _, _, bx1, by1 = _bbox(bc)
        placed = _tr(q, bx1 + 30 - qx0, by1 - qy1)
        merged = bc + placed
        x0m, _, x1m, _ = _bbox(merged)
        gc[name] = _tr(merged, -x0m, 0)
        gw[name] = x1m - x0m

    # ---------------- overlays & special letterforms ----------------
    def overlay(name, base, extra):
        bc = gc[base]
        ov = _match_winding(extra, bc)
        merged = bc + ov
        x0m, _, x1m, _ = _bbox(merged)
        gc[name] = _tr(merged, -x0m, 0)
        gw[name] = x1m - x0m

    sw = stroke_w
    # Ø ø: slash through O/o
    for name, base in (("Oslash", "O"), ("oslash", "o")):
        x0b, y0b, x1b, y1b = _bbox(gc[base])
        m = 40 if base == "O" else 30
        overlay(name, base, [stroke_contour(
            [(x1b - m - 20, y1b + 55), (x0b + m + 20, y0b - 55)], sw * 0.8,
            seed=31)])
    # Ł ł: bar through stem
    for name, base in (("Lslash", "L"), ("lslash", "l")):
        x0b, y0b, x1b, y1b = _bbox(gc[base])
        cy = (y1b - y0b) * 0.42 + y0b
        overlay(name, base, [stroke_contour(
            [(x0b - 34, cy - 40), (x0b + 130, cy + 45)], sw * 0.72, seed=32)])
    # Đ đ Ħ ħ: crossbars
    x0b, y0b, x1b, y1b = _bbox(gc["D"])
    overlay("Dcroat", "D", [stroke_contour(
        [(x0b - 40, 320), (x0b + 150, 320)], sw * 0.72, seed=33)])
    x0b, y0b, x1b, y1b = _bbox(gc["d"])
    overlay("dcroat", "d", [stroke_contour(
        [(x1b - 150, 540), (x1b + 60, 540)], sw * 0.7, seed=34)])
    x0b, y0b, x1b, y1b = _bbox(gc["H"])
    overlay("Hbar", "H", [stroke_contour(
        [(x0b - 36, 560), (x1b + 36, 560)], sw * 0.7, seed=35)])
    x0b, y0b, x1b, y1b = _bbox(gc["h"])
    overlay("hbar", "h", [stroke_contour(
        [(x0b - 40, 520), (x0b + 160, 520)], sw * 0.7, seed=36)])

    # AE / ae / OE / oe by overlap composition
    def sidebyside(name, left, right, overlap, lscale=1.0):
        lc = _scale(gc[left], lscale) if lscale != 1.0 else gc[left]
        lx0, _, lx1, _ = _bbox(lc)
        rc = gc[right]
        rx0, _, rx1, _ = _bbox(rc)
        placed = _tr(rc, lx1 - overlap - rx0, 0)
        merged = lc + _match_winding(placed, lc)
        x0m, _, x1m, _ = _bbox(merged)
        gc[name] = _tr(merged, -x0m, 0)
        gw[name] = x1m - x0m

    sidebyside("AE", "A", "E", 150)
    sidebyside("ae", "a", "e", 120)
    sidebyside("OE", "O", "E", 130)
    sidebyside("oe", "o", "e", 100)

    # Thorn/thorn/Eth/eth/germandbls from stroke skeletons + bases
    x0b, y0b, x1b, y1b = _bbox(gc["I"])
    stem_w = x1b - x0b
    # Thorn: I stem + bowl mid
    bowl = np.stack([np.cos(np.linspace(-np.pi / 2, np.pi / 2, 22)) * 190,
                     np.sin(np.linspace(-np.pi / 2, np.pi / 2, 22)) * 150 + 350],
                    axis=1)
    bowl[:, 0] += x0b + stem_w / 2
    overlay("Thorn", "I", [stroke_contour(bowl, sw * 0.92, seed=37, wobble=1.5)])
    # thorn: l + bowl low
    x0b, y0b, x1b, y1b = _bbox(gc["l"])
    bowl2 = np.stack([np.cos(np.linspace(-np.pi / 2, np.pi / 2, 22)) * 165,
                      np.sin(np.linspace(-np.pi / 2, np.pi / 2, 22)) * 130 + 205],
                     axis=1)
    bowl2[:, 0] += x0b + (x1b - x0b) / 2
    merged = gc["l"] + _match_winding(
        [stroke_contour(bowl2, sw * 0.92, seed=38, wobble=1.5)], gc["l"])
    # extend stem below baseline for thorn descender
    stem = stroke_contour([(x0b + (x1b - x0b) / 2, 120),
                           (x0b + (x1b - x0b) / 2, -210)], sw * 0.95,
                          seed=39, wobble=1.0)
    merged += _match_winding([stem], gc["l"])
    x0m, _, x1m, _ = _bbox(merged)
    gc["thorn"] = _tr(merged, -x0m, 0)
    gw["thorn"] = x1m - x0m
    # Eth/eth
    x0b, y0b, x1b, y1b = _bbox(gc["D"])
    overlay("Eth", "D", [stroke_contour(
        [(x0b - 40, 330), (x0b + 155, 330)], sw * 0.72, seed=40)])
    ox0, oy0, ox1, oy1 = _bbox(gc["o"])
    tail = stroke_contour([(ox1 - 55, oy1 - 40), (ox1 + 15, 560), (ox1 - 130, 640)],
                          sw * 0.85, seed=41, wobble=1.2)
    merged = gc["o"] + _match_winding([tail], gc["o"])
    x0m, _, x1m, _ = _bbox(merged)
    gc["eth"] = _tr(merged, -x0m, 0)
    gw["eth"] = x1m - x0m
    # germandbls: stem + double bump
    sk = [(0, 0), (0, 480), (30, 620), (150, 660), (255, 580), (235, 470),
          (150, 420), (255, 350), (275, 200), (185, 105), (95, 130)]
    gc_b = [stroke_contour(sk, sw * 0.94, seed=42, wobble=1.4)]
    add("germandbls", simplify(gc_b))
    skC = [(0, 0), (0, 500), (35, 655), (170, 700), (290, 610), (268, 480),
           (175, 425), (285, 345), (305, 175), (200, 70), (100, 95)]
    add("Germandbls", simplify([stroke_contour(skC, sw, seed=43, wobble=1.4)]))

    # ---------------- symbols ----------------
    # ¡ ¿: rotate, top at x-height, descends below baseline
    for src, dst in (("exclam", "exclamdown"), ("question", "questiondown")):
        c = gc[src]
        x0b, y0b, x1b, y1b = _bbox(c)
        rc = _rot180(c, (x0b + x1b) / 2, (y0b + y1b) / 2)
        rc = _tr(rc, 0, xheight - y1b)  # top at x-height
        add(dst, rc)
    # dashes & math
    hy = gc["hyphen"]
    hx0, hy0, hx1, hy1 = _bbox(hy)
    hw = hx1 - hx0
    add("endash", _scale(hy, 1.45, 1.0, cx=(hx0 + hx1) / 2))
    add("emdash", _scale(hy, 2.4, 1.0, cx=(hx0 + hx1) / 2))
    add("minus", _scale(hy, 1.5, 1.0, cx=(hx0 + hx1) / 2))
    cyh = (hy0 + hy1) / 2
    add("divide", _scale(hy, 1.15, 1.0, cx=(hx0 + hx1) / 2)
        + [circle_contour((hx0 + hx1) / 2, cyh + 145, stroke_w * 0.62)]
        + [circle_contour((hx0 + hx1) / 2, cyh - 145, stroke_w * 0.62)])
    cr = gc["cross"]
    cx0b, cy0b, cx1b, cy1b = _bbox(cr)
    add("multiply", _tr(_scale(cr, 0.82, cx=(cx0b + cx1b) / 2,
                               cy=(cy0b + cy1b) / 2), 0,
                        cyh - (cy0b + cy1b) / 2 * 0.82 - (1 - 0.82) * 0))
    # period-derived
    pd = gc["period"]
    px0, py0, px1, py1 = _bbox(pd)
    pw = px1 - px0
    add("periodcentered", _tr(pd, 0, 250 - py0))
    add("bullet", _tr(_scale(pd, 1.6, cx=px0, cy=py0), 0, 210 - py0))
    ell = pd + _tr(pd, pw + 105, 0) + _tr(pd, 2 * (pw + 105), 0)
    add("ellipsis", ell)
    # low quotes
    cm = gc["comma"]
    cx0b, cy0b, cx1b, cy1b = _bbox(cm)
    add("quotesinglbase", cm)
    add("quotedblbase", cm + _tr(cm, (cx1b - cx0b) + 55, 0))
    # guillemets
    ls = gc["less"]
    lx0, ly0, lx1, ly1 = _bbox(ls)
    g1 = _scale(ls, 0.78, cx=lx0, cy=(ly0 + ly1) / 2)
    g1x0, _, g1x1, _ = _bbox(g1)
    add("guilsinglleft", g1)
    add("guillemotleft", g1 + _tr(g1, (g1x1 - g1x0) + 45, 0))
    gr = gc["greater"]
    gx0, gy0, gx1, gy1 = _bbox(gr)
    g2 = _scale(gr, 0.78, cx=gx0, cy=(gy0 + gy1) / 2)
    g2x0, _, g2x1, _ = _bbox(g2)
    add("guilsinglright", g2)
    add("guillemotright", g2 + _tr(g2, (g2x1 - g2x0) + 45, 0))
    # degree / ordinals
    add("degree", _tr(marks["ring"], 0, 545))
    aa = _scale(gc["a"], 0.58)
    ax0, ay0, ax1, ay1 = _bbox(aa)
    add("ordfeminine", _tr(aa, 0, 380 - ay0))
    oo = _scale(gc["o"], 0.58)
    ox0b, oy0b, _, _ = _bbox(oo)
    add("ordmasculine", _tr(oo, 0, 380 - oy0b))
    # currency
    Cc = gc["C"]
    Cx0, Cy0, Cx1, Cy1 = _bbox(Cc)
    bars = [stroke_contour([(Cx0 - 60, 380), (Cx0 + 260, 395)], sw * 0.62, seed=50),
            stroke_contour([(Cx0 - 60, 260), (Cx0 + 240, 272)], sw * 0.62, seed=51)]
    merged = Cc + _match_winding(bars, Cc)
    x0m, _, x1m, _ = _bbox(merged)
    gc["Euro"] = _tr(merged, -x0m, 0)
    gw["Euro"] = x1m - x0m
    cc = gc["c"]
    ccx0, ccy0, ccx1, ccy1 = _bbox(cc)
    cbar = [stroke_contour([((ccx0 + ccx1) / 2, ccy1 + 70),
                            ((ccx0 + ccx1) / 2, ccy0 - 70)], sw * 0.6, seed=52)]
    merged = cc + _match_winding(cbar, cc)
    x0m, _, x1m, _ = _bbox(merged)
    gc["cent"] = _tr(merged, -x0m, 0)
    gw["cent"] = x1m - x0m
    Yc = gc["Y"]
    Yx0, Yy0, Yx1, Yy1 = _bbox(Yc)
    ybars = [stroke_contour([(Yx0 + 30, 330), (Yx1 - 30, 330)], sw * 0.6, seed=53),
             stroke_contour([(Yx0 + 30, 215), (Yx1 - 30, 215)], sw * 0.6, seed=54)]
    merged = Yc + _match_winding(ybars, Yc)
    x0m, _, x1m, _ = _bbox(merged)
    gc["yen"] = _tr(merged, -x0m, 0)
    gw["yen"] = x1m - x0m
    # £: skeleton
    pound = [stroke_contour([(255, 585), (200, 665), (95, 668), (40, 580),
                             (52, 430), (58, 250), (25, 60)], sw * 0.95,
                            seed=55, wobble=1.2),
             stroke_contour([(-45, 335), (215, 348)], sw * 0.72, seed=56),
             stroke_contour([(-10, 12), (305, 4)], sw * 0.92, seed=57)]
    add("sterling", simplify(pound))
    # §: two interlocking curves leave a real open counter in the middle.
    def cubic_points(a, b, c, d):
        t = np.linspace(0, 1, 32)[:, None]
        return ((1-t)**3 * np.array(a) + 3*(1-t)**2*t * np.array(b)
                + 3*(1-t)*t*t * np.array(c) + t**3 * np.array(d))

    upper = np.vstack([
        cubic_points((282, 621), (228, 697), (74, 680), (78, 577)),
        cubic_points((78, 577), (82, 489), (275, 463), (279, 365))[1:],
        cubic_points((279, 365), (282, 271), (149, 240), (76, 326))[1:],
    ])
    merged = simplify([stroke_contour(upper, sw * 0.72, seed=68, wobble=1.2),
                       stroke_contour(np.array([350, 700]) - upper,
                                      sw * 0.72, seed=69, wobble=1.2)])
    _, low, _, high = _bbox(merged)
    add("section", _scale(_tr(merged, 0, -low), 1, 700 / (high - low)))
    # ¶: a compact filled bowl and two equally weighted round-ended stems.
    # Keep the top bar within the stems instead of forming a heavy overhang.
    theta = np.linspace(np.pi / 2, 3 * np.pi / 2, 36)
    bowlp = np.column_stack([14 + 190 * np.cos(theta),
                            508 + 148 * np.sin(theta)])
    bowl = [("move", tuple(bowlp[0]))] + [("line", tuple(p)) for p in bowlp[1:]]
    par = [bowl,
           stroke_contour([(12, 652), (12, 45)], sw * 0.75, seed=59, wobble=1.2),
           stroke_contour([(168, 652), (168, 45)], sw * 0.75, seed=60, wobble=1.2),
           stroke_contour([(12, 652), (168, 652)], sw * 0.75, seed=61, wobble=1.0)]
    add("paragraph", simplify(par))
    # © ®: hand-drawn ring (annulus, low-frequency wobble) at the
    # reference's proportions, with ring and interior letter sharing a nib.
    def _wobbly_circle(cx, cy, r, seed, amp, ccw=False):
        aa = np.linspace(0, 2 * np.pi, 72, endpoint=False)
        rng = np.random.default_rng(seed)
        ph1, ph2 = rng.uniform(0, 2 * np.pi, 2)
        rr = r + amp * np.sin(2 * aa + ph1) + amp * 0.6 * np.sin(5 * aa + ph2)
        if ccw:
            aa, rr = aa[::-1], rr[::-1]
        pts = np.stack([cx + rr * np.cos(aa), cy + rr * np.sin(aa)], axis=1)
        return [("move", tuple(pts[0]))] + [("line", tuple(q))
                                            for q in pts[1:]]

    ring_t = sw * 0.55
    rc = 350.0
    for letter, gname, seed, lscale in (("C", "copyright", 71, 0.56),
                                        ("R", "registered", 73, 0.54)):
        ring = [_wobbly_circle(rc, rc, rc, seed, amp=7.0),
                _wobbly_circle(rc, rc, rc - ring_t, seed + 1, amp=5.0,
                               ccw=True)]
        inner = _scale(gc[letter], lscale)
        ix0, iy0, ix1, iy1 = _bbox(inner)
        placed = _tr(inner, rc - (ix0 + ix1) / 2, rc - (iy0 + iy1) / 2)
        add(gname, simplify(ring) + placed)
    Tm = _scale(gc["T"], 0.57)
    Mm = _scale(gc["M"], 0.57)
    tx0, ty0, tx1, ty1 = _bbox(Tm)
    mx0, my0, mx1, my1 = _bbox(Mm)
    tm = _tr(Tm, 0, 700 - ty1) + _tr(Mm, tx1 - tx0 + 40 - mx0, 700 - my1)
    add("trademark", tm)
    # ^ ~ | ` and spacing marks
    add("asciicircum", _tr(_scale(marks["circumflex"], 1.15), 0, 380))
    add("asciitilde", _tr(_scale(marks["tilde"], 1.25), 0, 230))
    add("bar", [stroke_contour([(0, 730), (4, -150)], sw * 0.9, seed=62,
                               wobble=1.5)])
    add("grave.spacing", _tr(marks["grave"], 0, 520))
    add("acute.spacing", _tr(marks["acute"], 0, 520))
    add("macron.spacing", _tr(marks["macron"], 0, 540))
    add("dieresis.spacing", _tr(marks["dieresis"], 0, 540))
    add("cedilla.spacing", _tr(marks["cedilla"], 0, 0))
    add("circumflex.spacing", _tr(marks["circumflex"], 0, 520))
    add("caron.spacing", _tr(marks["caron"], 0, 520))
    add("breve.spacing", _tr(marks["breve"], 0, 520))
    add("dotaccent.spacing", _tr(marks["dotaccent"], 0, 540))
    add("ring.spacing", _tr(marks["ring"], 0, 520))
    add("ogonek.spacing", _tr(marks["ogonek"], 0, 0))
    add("tilde.spacing", _tr(marks["tilde"], 0, 540))
    add("hungarumlaut.spacing", _tr(marks["hungarumlaut"], 0, 520))
    # combining marks: centered on previous glyph (negative offset)
    for mk, comb in (("grave", "gravecomb"), ("acute", "acutecomb"),
                     ("circumflex", "circumflexcomb"), ("tilde", "tildecomb"),
                     ("macron", "macroncomb"), ("breve", "brevecomb"),
                     ("dotaccent", "dotaccentcomb"), ("dieresis", "dieresiscomb"),
                     ("ring", "ringcomb"), ("hungarumlaut", "hungarumlautcomb"),
                     ("caron", "caroncomb")):
        mc = _tr(marks[mk], -190, xheight + MARK_GAP)
        gc[comb] = mc
        gw[comb] = 0.0
    gc["commaaccentcomb"] = _tr(comma, -190 - (cx0 + cx1) / 2, -30 - cy1)
    gw["commaaccentcomb"] = 0.0
    gc["cedillacomb"] = _tr(marks["cedilla"], -190, 0)
    gw["cedillacomb"] = 0.0
    gc["ogonekcomb"] = _tr(marks["ogonek"], -190, 0)
    gw["ogonekcomb"] = 0.0
