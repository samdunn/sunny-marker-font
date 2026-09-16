#!/usr/bin/env python3
"""Vectorize extracted glyphs with potrace and build SunnyMarker-Regular.otf.

Pipeline per glyph: crop from grayscale sheet -> 6x lanczos upscale ->
threshold -> potrace (smooth cubic beziers) -> parse SVG path -> scale into
font units on a per-row baseline -> CFF charstring. Metrics are derived from
the sheet itself (cap height normalized to 700/1000 UPM).
"""
import json
import os
import re
import subprocess
import shutil
import numpy as np
from PIL import Image
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHEET = os.path.join(ROOT, "references", "glyph-grid.png")
MANIFEST = os.path.join(ROOT, "glyphs", "manifest.json")
SVG_DIR = os.path.join(ROOT, "glyphs", "svg")
BUILD = os.path.join(ROOT, "build")

UPM = 1000
CAP = 700          # target cap height in font units
SB = 52            # side bearing
SCALE_UP = 6       # raster upscale before tracing

DESCENDERS = set("gjpqy")
XHEIGHT_CHARS = set("acemnorsuvwxz")

MEASURED_STROKE = 124.0  # family marker stroke width in font units
# glyphs drawn short in the sheet -> raise to CAP height AND normalize their
# stroke to the family width (source strokes measured via EDT, font units)
CAP_FIX = {"exclam": 113.0, "question": 97.0}

# glyph name -> unicode(s)
CMAP = {}
for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    CMAP[c] = [ord(c)]
for c in "abcdefghijklmnopqrstuvwxyz":
    CMAP[c] = [ord(c)]
for i, n in enumerate(["zero", "one", "two", "three", "four", "five", "six",
                       "seven", "eight", "nine"]):
    CMAP[n] = [ord("0") + i]
CMAP.update({
    "exclam": [0x21], "question": [0x3F], "period": [0x2E], "comma": [0x2C],
    "semicolon": [0x3B], "quotedbl": [0x22], "parenleft": [0x28],
    "parenright": [0x29], "bracketleft": [0x5B], "bracketright": [0x5D],
    "braceleft": [0x7B], "slash": [0x2F], "backslash": [0x5C],
    "hyphen": [0x2D, 0x2010], "underscore": [0x5F], "plus": [0x2B],
    "equal": [0x3D], "at": [0x40], "numbersign": [0x23], "dollar": [0x24],
    "percent": [0x25], "ampersand": [0x26], "asterisk": [0x2A],
    "less": [0x3C], "greater": [0x3E],
    # extras
    "arrowright": [0x2192], "arrowupright": [0x2197], "arrowup": [0x2191],
    "arrowupleft": [0x2196], "arrowleft": [0x2190],
    "arrowdownright": [0x2198], "arrowdown": [0x2193],
    "arrowdownleft": [0x2199], "star": [0x2605], "sparkle": [0x2727],
    "heart": [0x2661, 0x2764], "sun": [0x2600], "check": [0x2713],
    "cross": [0x2717],
    # derived
    "colon": [0x3A], "braceright": [0x7D], "quotesingle": [0x27],
    "quoteleft": [0x2018], "quoteright": [0x2019],
    "quotedblleft": [0x201C], "quotedblright": [0x201D],
    "space": [0x20, 0x00A0],
})
from glyph_extensions import (EXT_CMAP, ZERO_ADVANCE, UNENCODED,
                              CCMP_FEA, ALT_FEA, bare_stem, unbarred_j, upright_y_stem)  # noqa: E402
CMAP.update(EXT_CMAP)

DIGIT_NAMES = ["zero", "one", "two", "three", "four", "five", "six", "seven",
               "eight", "nine"]


def manifest_glyph_font_name(name):
    """manifest file name -> font glyph name"""
    if name.endswith(".lc"):
        return name[:-3]
    if name.startswith("digit"):
        return DIGIT_NAMES[int(name[5:])]
    return name


# ---------------- potrace SVG parsing ----------------

NUM_RE = re.compile(r"-?\d+\.?\d*(?:e-?\d+)?")


def parse_potrace_svg(svg_text):
    """Return list of contours; each contour is a list of segments.

    Segment: ("line", (x, y)) or ("curve", (x1, y1), (x2, y2), (x3, y3)).
    Contour implicitly starts at start point stored as first element
    ("move", (x, y)). Coordinates already have the group transform applied.
    """
    m = re.search(r'transform="translate\(([-\d.]+),([-\d.]+)\)\s*'
                  r'scale\(([-\d.]+),([-\d.]+)\)"', svg_text)
    tx, ty, sx, sy = (float(g) for g in m.groups())

    def T(x, y):
        return (tx + sx * x, ty + sy * y)

    contours = []
    for pm in re.finditer(r'<path d="([^"]+)"', svg_text):
        d = pm.group(1)
        tokens = re.findall(r"[MmCcLlZz]|" + NUM_RE.pattern, d)
        i = 0
        cmd = None
        cur = (0.0, 0.0)
        contour = None
        while i < len(tokens):
            t = tokens[i]
            if t in "MmCcLlZz":
                cmd = t
                i += 1
                if cmd in "Zz":
                    if contour:
                        contours.append(contour)
                        contour = None
                continue
            if cmd in "Mm":
                x, y = float(tokens[i]), float(tokens[i + 1])
                i += 2
                if cmd == "m":
                    x, y = cur[0] + x, cur[1] + y
                cur = (x, y)
                if contour:
                    contours.append(contour)
                contour = [("move", T(*cur))]
                # subsequent implicit pairs are lineto
                cmd = "L" if cmd == "M" else "l"
            elif cmd in "Ll":
                x, y = float(tokens[i]), float(tokens[i + 1])
                i += 2
                if cmd == "l":
                    x, y = cur[0] + x, cur[1] + y
                cur = (x, y)
                contour.append(("line", T(*cur)))
            elif cmd in "Cc":
                v = [float(tokens[i + k]) for k in range(6)]
                i += 6
                if cmd == "c":
                    v = [v[0] + cur[0], v[1] + cur[1], v[2] + cur[0],
                         v[3] + cur[1], v[4] + cur[0], v[5] + cur[1]]
                contour.append(("curve", T(v[0], v[1]), T(v[2], v[3]),
                                T(v[4], v[5])))
                cur = (v[4], v[5])
            else:
                raise ValueError("unexpected token " + t)
        if contour:
            contours.append(contour)
    return contours


def disk(r):
    n = int(np.ceil(r))
    y, x = np.ogrid[-n:n + 1, -n:n + 1]
    return (x * x + y * y) <= r * r


COUNTER_FACTOR = 0.55    # counters close at only 55% of the outer growth
APERTURE_FACTOR = 0.40   # open apertures (mouth of e/s/a) narrow at 40%
APERTURE_DETECT_PX = 26  # concavities narrower than ~2x this are apertures
MIN_HOLE_RADIUS_PX = 17  # counters never erode below this inscribed radius
MIN_PART_SEP_PX = 5.0    # half-gap kept between glyph parts (upscaled px)


def embolden(mask, r_px):
    """Weight-aware dilation:
    - outer boundary grows by r_px
    - counters (holes) shrink at COUNTER_FACTOR, never below a minimum
      inscribed radius (the eye of e, bowls of a/8 stay open)
    - open apertures (mouth of e, slots of s) narrow at APERTURE_FACTOR
      instead of sealing shut
    - separate parts (dot of !, i, %, sun rays) never fuse: each grows
      inside its own Voronoi territory with a margin at the boundary
    """
    from scipy import ndimage
    P = APERTURE_DETECT_PX + 2
    mask = np.pad(mask, P)

    # aperture channels: narrow concavities of the original shape
    closed = ndimage.binary_closing(mask, structure=disk(APERTURE_DETECT_PX))
    aperture = closed & ~mask
    r_ap = APERTURE_FACTOR * r_px
    keep_open = (ndimage.binary_erosion(aperture, structure=disk(r_ap))
                 if r_ap >= 0.5 else aperture)

    def grow_part(part):
        filled = ndimage.binary_fill_holes(part)
        grown = ndimage.binary_dilation(filled, structure=disk(r_px))
        holes, nh = ndimage.label(filled & ~part)
        for h in range(1, nh + 1):
            hole = holes == h
            edt = ndimage.distance_transform_edt(hole)
            allowed = max(float(edt.max()) - MIN_HOLE_RADIUS_PX, 0.0)
            r_h = min(COUNTER_FACTOR * r_px, allowed)
            kept = (hole & (edt > r_h)) if r_h >= 0.5 else hole
            grown &= ~kept
        return grown

    lab, n = ndimage.label(mask)
    if n <= 1:
        out = grow_part(mask)
    else:
        territory = np.argmin(
            np.stack([ndimage.distance_transform_edt(lab != i)
                      for i in range(1, n + 1)]), axis=0)
        out = np.zeros_like(mask)
        for i in range(1, n + 1):
            own = territory == (i - 1)
            interior = ndimage.distance_transform_edt(own) > MIN_PART_SEP_PX
            out |= grow_part(lab == i) & own & interior
    out &= ~keep_open
    return out[P:-P, P:-P]


def trace_glyph(sheet_gray, g, tag, r_px=0.0, svg_dir=None, width_scale=1.0):
    """Crop glyph from sheet, upscale, optionally dilate/erode by r_px
    (round kernel = marker nib), potrace. Returns contours in
    upscaled-pixel coordinates (y down, origin at crop top-left).

    width_scale: anisotropic condensed/extended. The bitmap is x-scaled,
    then vertical strokes are restored with a horizontal-only kernel so
    the marker nib stays round (x-scaling alone thins/fattens verticals
    while leaving horizontals untouched)."""
    from scipy import ndimage
    svg_dir = svg_dir or SVG_DIR
    m = 3 + int(np.ceil(max(r_px, 0) / SCALE_UP)) + 1
    x0, x1, y0, y1 = g["x0"] - m, g["x1"] + m, g["y0"] - m, g["y1"] + m
    crop = sheet_gray.crop((x0, y0, x1, y1))
    big = crop.resize((int(round(crop.width * SCALE_UP * width_scale)),
                       crop.height * SCALE_UP), Image.LANCZOS)
    bw = big.point(lambda p: 0 if p < 140 else 255).convert("1")
    if abs(width_scale - 1.0) > 0.01:
        U2PX = SCALE_UP / 9.655  # font units -> upscaled px
        mask = np.asarray(bw) == 0
        if width_scale < 1.0:
            # Condensed runs optically darker at equal stroke (counters
            # shrink, ink doesn't), so target a ~9% lighter uniform stroke:
            # horizontal dilate restores verticals ABOVE target, then a
            # small round erosion evens all orientations, re-opens
            # counters/apertures, and smooths the anisotropic artifacts.
            e_u = MEASURED_STROKE * 0.045          # per-side lighten
            target_v = MEASURED_STROKE * 0.91      # final uniform stroke
            d_hu = (target_v - MEASURED_STROKE * width_scale + 2 * e_u) / 2
            d_hx = int(round(max(d_hu, 0) * U2PX))
            if d_hx >= 1:
                mask = ndimage.binary_dilation(
                    mask, structure=np.ones((1, 2 * d_hx + 1), bool))
            e_px = e_u * U2PX
            if e_px >= 0.5:
                mask = ndimage.binary_erosion(mask, structure=disk(e_px))
        else:
            # Extended: thin the widened verticals back to the family stroke
            r_hx = int(round(MEASURED_STROKE * (width_scale - 1) / 2 * U2PX))
            if r_hx >= 1:
                mask = ndimage.binary_erosion(
                    mask, structure=np.ones((1, 2 * r_hx + 1), bool))
        bw = Image.fromarray(
            np.where(mask, 0, 255).astype(np.uint8)).convert("1")
    if abs(r_px) >= 0.5:
        mask = np.asarray(bw) == 0  # ink
        if r_px > 0:
            mask = embolden(mask, r_px)
        else:
            mask = ndimage.binary_erosion(mask, structure=disk(-r_px))
        bw = Image.fromarray(np.where(mask, 0, 255).astype(np.uint8)).convert("1")
    pbm = os.path.join(svg_dir, tag + ".pbm")
    svg = os.path.join(svg_dir, tag + ".svg")
    bw.save(pbm)
    potrace = shutil.which("potrace")
    if potrace is None:
        raise RuntimeError("Install Potrace before regenerating raster sources")
    subprocess.run([potrace, pbm, "-s", "-o", svg, "--turdsize", "20",
                    "--alphamax", "1.0", "--opttolerance", "0.3"],
                   check=True, timeout=30)
    os.remove(pbm)
    with open(svg) as f:
        contours = parse_potrace_svg(f.read())
    return contours, (x0, y0)


# ---------------- polyline helpers (cap-height correction) ----------------

def _flatten(contour, steps=24):
    pts = [contour[0][1]]
    for seg in contour[1:]:
        if seg[0] == "line":
            pts.append(seg[1])
        else:
            p0 = np.array(pts[-1], float)
            p1, p2, p3 = (np.array(p, float) for p in seg[1:])
            for i in range(1, steps + 1):
                t = i / steps
                q = ((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1
                     + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3)
                pts.append(tuple(q))
    if np.allclose(pts[0], pts[-1]):
        pts = pts[:-1]
    return np.array(pts)


def _resample(poly, spacing=5.0):
    d = np.linalg.norm(np.diff(np.vstack([poly, poly[:1]]), axis=0), axis=1)
    per = d.sum()
    n = max(16, int(round(per / spacing)))
    cum = np.concatenate([[0], np.cumsum(d)])
    targets = np.linspace(0, per, n, endpoint=False)
    closed = np.vstack([poly, poly[:1]])
    out = np.empty((n, 2))
    j = 0
    for i, t in enumerate(targets):
        while cum[j + 1] < t:
            j += 1
        seg_len = cum[j + 1] - cum[j]
        a = 0.0 if seg_len == 0 else (t - cum[j]) / seg_len
        out[i] = closed[j] * (1 - a) + closed[j + 1] * a
    return out


def _normals(poly):
    t = np.roll(poly, -1, axis=0) - np.roll(poly, 1, axis=0)
    ln = np.linalg.norm(t, axis=1, keepdims=True)
    ln[ln == 0] = 1
    t = t / ln
    return np.stack([t[:, 1], -t[:, 0]], axis=1)


def _smooth(poly, passes=2, lam=0.35):
    p = poly.copy()
    for _ in range(passes):
        p = p + lam * ((np.roll(p, -1, axis=0) + np.roll(p, 1, axis=0)) / 2 - p)
    return p


def cap_align(contours, src_stroke, target_stroke):
    """Scale a short glyph so its height reaches CAP and its stroke lands on
    the family width: f*top - 2d = CAP and f*src - 2d = target give
    f = (CAP - target)/(top - src), d = (f*src - target)/2 (erode if d>0,
    dilate if d<0). Keeps dots round and on the baseline.
    Returns (line-segment contours, ink width)."""
    ys = [p[1] for c in contours for seg in c for p in seg[1:]]
    top = max(ys)
    f = (CAP - target_stroke) / (top - src_stroke)
    if not 1.02 < f < 2.0:
        return None
    d = (f * src_stroke - target_stroke) / 2
    polys = [_resample(_flatten(c)) for c in contours]
    polys = [p * f for p in polys]
    # sign calibration: displacing outward must grow the largest contour
    big = max(polys, key=lambda p: np.ptp(p[:, 0]))
    sign = 1.0 if np.ptp((big + 10 * _normals(big))[:, 0]) > np.ptp(big[:, 0]) else -1.0
    moved = [_smooth(p - sign * d * _normals(p)) for p in polys]
    minx = min(p[:, 0].min() for p in moved)
    miny = min(p[:, 1].min() for p in moved)
    out = []
    width = max(p[:, 0].max() for p in moved) - minx
    for p in moved:
        p = p - [minx, miny]
        segs = [("move", tuple(p[0]))]
        segs += [("line", tuple(pt)) for pt in p[1:]]
        out.append(segs)
    return out, float(width)


# ---------------- outline simplification (smoothing-spline refit) --------

SIMPLIFY_TOL = 2.4      # units of wobble to smooth away
CORNER_ANGLE = 38.0     # degrees; sharper turns are preserved as corners
CORNER_WIN = 7.0        # tangent window (units) for corner detection
MAX_DEV = 8.0           # refit rejected if it strays further than this


def _turn_angles(poly, win):
    d = np.linalg.norm(np.diff(poly, axis=0, append=poly[:1]), axis=1)
    step = max(1, int(round(win / max(d.mean(), 1e-6))))
    prv = np.roll(poly, step, axis=0)
    nxt = np.roll(poly, -step, axis=0)
    t1 = poly - prv
    t2 = nxt - poly
    ang = np.degrees(np.abs(np.arctan2(
        t1[:, 0] * t2[:, 1] - t1[:, 1] * t2[:, 0],
        (t1 * t2).sum(axis=1))))
    return ang, step


def _corner_indices(poly):
    """Split points: sharp corners (small window) plus tight rounded
    apexes (larger window) — both make the arcs between them gentle
    enough for stable spline fitting."""
    n = len(poly)
    per = float(np.linalg.norm(
        np.diff(poly, axis=0, append=poly[:1]), axis=1).sum())
    apex_win = min(85.0, per / 12.0)
    idx = []
    for win, thresh in ((CORNER_WIN, CORNER_ANGLE), (apex_win, 65.0)):
        ang, step = _turn_angles(poly, win)
        for i in np.argsort(-ang):
            if ang[i] < thresh:
                break
            if all(min(abs(i - j), n - abs(i - j)) > 2 * step for j in idx):
                idx.append(int(i))
    return sorted(idx)


def _ppoly_to_beziers(ppx, ppy):
    """Piecewise cubics (shared breakpoints) -> list of Bezier segments."""
    segs = []
    n = min(len(ppx.x) - 1, ppx.c.shape[1], ppy.c.shape[1])
    for i in range(n):
        h = ppx.x[i + 1] - ppx.x[i]
        if h <= 1e-9:
            continue
        out = []
        for pp in (ppx, ppy):
            c3, c2, c1, c0 = pp.c[:, i]
            out.append((c0,
                        c0 + c1 * h / 3,
                        c0 + 2 * c1 * h / 3 + c2 * h * h / 3,
                        c0 + c1 * h + c2 * h * h + c3 * h ** 3))
        (x0, x1, x2, x3), (y0, y1, y2, y3) = out
        segs.append(((x0, y0), (x1, y1), (x2, y2), (x3, y3)))
    return segs


def _fit_open(pts, knot_spacing):
    """Least-squares cubic B-spline through an open arc, x and y fitted on
    a SHARED evenly spaced knot vector (independent knot selection would
    misalign the piecewise intervals)."""
    from scipy import interpolate
    arclen = np.concatenate([[0], np.cumsum(
        np.linalg.norm(np.diff(pts, axis=0), axis=1))])
    L = arclen[-1]
    if L < 1e-6 or len(pts) < 8:
        return None
    t = arclen / L
    t, keep = np.unique(t, return_index=True)
    pts = pts[keep]
    if len(pts) < 8:
        return None
    n_int = max(0, int(round(L / knot_spacing)) - 1)
    n_int = min(n_int, max(0, len(pts) // 4 - 4))
    interior = np.linspace(0, 1, n_int + 2)[1:-1]
    try:
        tckx = interpolate.splrep(t, pts[:, 0], k=3, task=-1, t=interior)
        tcky = interpolate.splrep(t, pts[:, 1], k=3, task=-1, t=interior)
    except Exception:
        return None
    ppx = interpolate.PPoly.from_spline(tckx)
    ppy = interpolate.PPoly.from_spline(tcky)
    segs = _ppoly_to_beziers(ppx, ppy)
    if not segs:
        return None
    # snap endpoints exactly onto the polyline ends (corner points),
    # dragging the adjacent control point by the same small delta
    p0, p1, p2, p3 = segs[0]
    d0 = pts[0] - np.array(p0)
    segs[0] = (tuple(pts[0]), tuple(np.array(p1) + d0), p2, p3)
    p0, p1, p2, p3 = segs[-1]
    d1 = pts[-1] - np.array(p3)
    segs[-1] = (p0, p1, tuple(np.array(p2) + d1), tuple(pts[-1]))
    return segs


def _fit_closed(pts, knot_spacing):
    """Closed contour with no corners: seam it at the flattest point and
    fit as a pinned open arc (PPoly.from_spline mishandles periodic
    splines, so periodic fitting is avoided entirely)."""
    ang, _ = _turn_angles(pts, 15.0)
    i0 = int(np.argmin(ang))
    rotated = np.roll(pts, -i0, axis=0)
    return _fit_open(np.vstack([rotated, rotated[:1]]), knot_spacing)


def _max_deviation(segs, poly):
    pts = []
    for p0, p1, p2, p3 in segs:
        for tt in np.linspace(0, 1, 8):
            q = ((1 - tt) ** 3 * np.array(p0) + 3 * (1 - tt) ** 2 * tt * np.array(p1)
                 + 3 * (1 - tt) * tt ** 2 * np.array(p2) + tt ** 3 * np.array(p3))
            pts.append(q)
    pts = np.array(pts)
    d2 = ((pts[:, None, :] - poly[None, :, :]) ** 2).sum(axis=2)
    return float(np.sqrt(d2.min(axis=1).max()))


def simplify_contours(contours, tol=SIMPLIFY_TOL):
    """Refit traced contours with smoothing splines: keeps the hand-drawn
    bounce, drops pixel-level wobble, cuts point count ~4x. Sharp corners
    (star points, arrowheads, junctions) are detected and preserved."""
    out = []
    for contour in contours:
        poly = _resample(_flatten(contour, steps=10), spacing=2.0)
        if len(poly) < 10:
            out.append(contour)
            continue
        corners = _corner_indices(poly)
        segs = None
        for spacing_try in (110.0, 60.0, 30.0):
            if corners:
                segs = []
                loops = corners + [corners[0] + len(poly)]
                ext = np.vstack([poly, poly])
                ok = True
                for a, b in zip(loops[:-1], loops[1:]):
                    arc = _fit_open(ext[a:b + 1], spacing_try)
                    if arc is None:
                        ok = False
                        break
                    segs.extend(arc)
                if not ok:
                    segs = None
            else:
                segs = _fit_closed(poly, spacing_try)
            if segs and _max_deviation(segs, poly) <= MAX_DEV:
                break
            segs = None
        if not segs:
            out.append(contour)
            continue
        new = [("move", segs[0][0])]
        for p0, p1, p2, p3 in segs:
            new.append(("curve", p1, p2, p3))
        out.append(new)
    return out


# ---------------- font unit conversion ----------------

def contours_to_units(contours, crop_origin, baseline_px, scale):
    """Convert traced contours (upscaled px, y down) into font units
    (y up, baseline at 0). x is left-aligned to ink; returns (contours, w)."""
    xs = []
    for c in contours:
        for seg in c:
            for pt in seg[1:]:
                xs.append(pt[0])
    xmin = min(xs)
    xmax = max(xs)

    def U(pt):
        x = (pt[0] - xmin) / SCALE_UP * scale
        y_sheet = crop_origin[1] + pt[1] / SCALE_UP
        y = (baseline_px - y_sheet) * scale
        return (x, y)

    out = []
    for c in contours:
        out.append([(seg[0], *[U(p) for p in seg[1:]]) for seg in c])
    width = (xmax - xmin) / SCALE_UP * scale
    return out, width


def draw_contours(pen_target, contours, dx=0.0, dy=0.0, mirror_x=None,
                  rot180_about=None):
    for c in contours:
        pts_transformed = []
        for seg in c:
            newpts = []
            for (x, y) in seg[1:]:
                if mirror_x is not None:
                    x = 2 * mirror_x - x
                if rot180_about is not None:
                    x = 2 * rot180_about[0] - x
                    y = 2 * rot180_about[1] - y
                newpts.append((x + dx, y + dy))
            pts_transformed.append((seg[0], newpts))
        # mirroring flips winding; T2 charstrings don't care (CFF uses
        # non-zero but potrace emits proper nesting; flip keeps nesting)
        pen_target.moveTo(pts_transformed[0][1][0])
        for kind, pts in pts_transformed[1:]:
            if kind == "line":
                pen_target.lineTo(pts[0])
            else:
                pen_target.curveTo(*pts)
        pen_target.closePath()


def build_glyphs(offset=0.0, style="Regular", width_scale=1.0):
    """Trace all glyphs at the given outline offset. Returns
    (glyph_contours, glyph_width, xheight).

    offset: outline offset in font units per side (+bolder / -lighter).
    Vertical compensation: after dilation the ink bbox grows by `offset` in
    every direction, so y' = (y + offset) * s with s = CAP/(CAP + 2*offset)
    puts baseline-sitters back on 0 and cap tops back at CAP. Anything
    centered at CAP/2 (arrows/doodles) is a fixed point of this map.
    """
    svg_dir = os.path.join(SVG_DIR, style)
    os.makedirs(svg_dir, exist_ok=True)
    os.makedirs(BUILD, exist_ok=True)
    sheet = Image.open(SHEET).convert("L")
    man = json.load(open(MANIFEST))
    rows = man["rows"]

    # ---- per-row baselines (sheet px, y down) ----
    def bottoms(row, names):
        sel = [g["y1"] for g in row["glyphs"]
               if manifest_glyph_font_name(g["name"]) in names]
        return float(np.median(sel))

    def tops(row, names):
        sel = [g["y0"] for g in row["glyphs"]
               if manifest_glyph_font_name(g["name"]) in names]
        return float(np.median(sel))

    base = {}
    base[0] = bottoms(rows[0], set("ABCDEFGHIJKLMN"))
    base[1] = bottoms(rows[1], set("OPRSTUVWXYZ"))  # Q tail may descend
    base[2] = bottoms(rows[2], set("abcdehiklmn"))
    base[3] = bottoms(rows[3], set("orstuvwxz"))
    base[4] = bottoms(rows[4], set(DIGIT_NAMES))
    base[5] = bottoms(rows[5], {"exclam", "period", "question"})
    base[6] = bottoms(rows[6], {"numbersign", "percent", "ampersand"})
    base[7] = None  # extras: vertically centered instead

    cap_px = base[0] - tops(rows[0], set("ABCDEFGHIJKLMN"))
    cap_px2 = base[1] - tops(rows[1], set("OPRSTUVWXYZ"))
    cap_px = (cap_px + cap_px2) / 2
    scale = CAP / cap_px
    xh_px = base[2] - tops(rows[2], XHEIGHT_CHARS & set("acemn"))
    xheight = xh_px * scale
    print(f"cap {cap_px:.1f}px -> scale {scale:.3f}; x-height {xheight:.0f}u")

    glyph_contours = {}   # font glyph name -> contours in font units
    glyph_width = {}      # ink width in units

    r_px = offset / scale * SCALE_UP  # offset in upscaled bitmap pixels
    s_comp = CAP / (CAP + 2 * offset)
    print(f"style {style}: offset {offset:+.1f}u -> r {r_px:+.1f}px, "
          f"comp scale {s_comp:.4f}")

    def compensate(contours, width):
        out = [[(seg[0], *[((x * s_comp), (y + offset) * s_comp)
                           for (x, y) in seg[1:]]) for seg in c]
               for c in contours]
        return out, width * s_comp

    for ri, row in enumerate(rows):
        for g in row["glyphs"]:
            fname = manifest_glyph_font_name(g["name"])
            if fname == "semicolon.alt":
                continue
            contours, origin = trace_glyph(sheet, g, g["name"], r_px=r_px,
                                           svg_dir=svg_dir,
                                           width_scale=width_scale)
            if ri == 7:
                # extras: center glyph vertically at 350 units
                ymid_px = (g["y0"] + g["y1"]) / 2
                baseline_px = ymid_px + 350 / scale
            else:
                baseline_px = base[ri]
            cont_u, w = contours_to_units(contours, origin, baseline_px, scale)
            cont_u, w = compensate(cont_u, w)
            if fname in CAP_FIX:
                src_w = (CAP_FIX[fname] + 2 * offset) * s_comp
                target_w = (MEASURED_STROKE + 2 * offset) * s_comp
                fixed = cap_align(cont_u, src_w, target_w)
                if fixed:
                    cont_u, w = fixed
            cont_u = simplify_contours(cont_u)
            glyph_contours[fname] = cont_u
            glyph_width[fname] = w

    # ---- derived glyphs ----
    # The sheet draws I with top/bottom bars. Default to a bare marker stem
    # (fitted from that drawing's own stem) and keep the barred original as
    # the ss01/salt alternate. Runs before the extensions so the accented
    # I's, Idotaccent and Thorn all build on the bare stem.
    glyph_contours["I.ss01"] = glyph_contours["I"]
    glyph_width["I.ss01"] = glyph_width["I"]
    stem = bare_stem([_flatten(c) for c in glyph_contours["I"]],
                     [_flatten(c) for c in glyph_contours["H"]],
                     simplify_contours, _flatten)
    sx0 = min(p[0] for c in stem for s in c for p in s[1:])
    sx1 = max(p[0] for c in stem for s in c for p in s[1:])
    glyph_contours["I"] = [[(s[0], *[(x - sx0, y) for (x, y) in s[1:]])
                            for s in c] for c in stem]
    glyph_width["I"] = sx1 - sx0

    # Keep J's original hooked bottom and hand lean, without the top bar.
    # Apply before extensions so the capital J-acute inherits the same form.
    j = unbarred_j([_flatten(c) for c in glyph_contours["J"]], CAP,
                   simplify_contours)
    jx0 = min(p[0] for c in j for s in c for p in s[1:])
    jx1 = max(p[0] for c in j for s in c for p in s[1:])
    glyph_contours["J"] = [[(s[0], *[(x-jx0, y) for x, y in s[1:]])
                            for s in c] for c in j]
    glyph_width["J"] = jx1-jx0

    # A capital Y needs its own stem, rather than a lowercase-style tail.
    # Compose accents from the corrected outline below.
    glyph_contours["Y"] = upright_y_stem(glyph_contours["Y"], CAP)

    def bbox(contours):
        xs, ys = [], []
        for c in contours:
            for seg in c:
                for (x, y) in seg[1:]:
                    xs.append(x)
                    ys.append(y)
        return min(xs), min(ys), max(xs), max(ys)

    def translated(contours, dx, dy):
        return [[(seg[0], *[(x + dx, y + dy) for (x, y) in seg[1:]])
                 for seg in c] for c in contours]

    # colon = two periods stacked
    p = glyph_contours["period"]
    _, py0, _, py1 = bbox(p)
    lift = xheight - (py1 - py0)
    glyph_contours["colon"] = p + translated(p, 0, lift)
    glyph_width["colon"] = glyph_width["period"]

    # braceright = mirrored braceleft
    bl = glyph_contours["braceleft"]
    bx0, _, bx1, _ = bbox(bl)
    mid = (bx0 + bx1) / 2
    mirrored = []
    for c in bl:
        segs = [(seg[0], *[(2 * mid - x, y) for (x, y) in seg[1:]])
                for seg in c]
        mirrored.append(segs)
    glyph_contours["braceright"] = mirrored
    glyph_width["braceright"] = glyph_width["braceleft"]

    # curly quotes from comma raised to cap zone; quotesingle uses the same
    # raised-comma shape (weight-proof: quotedbl's ticks fuse when dilated)
    cm = glyph_contours["comma"]
    cx0, cy0, cx1, cy1 = bbox(cm)
    ch = cy1 - cy0
    raise_dy = CAP - cy1  # top of raised comma at cap height
    qr = translated(cm, 0, raise_dy)
    glyph_contours["quoteright"] = qr
    glyph_width["quoteright"] = cx1 - cx0
    glyph_contours["quotesingle"] = qr
    glyph_width["quotesingle"] = cx1 - cx0
    # quoteleft = comma rotated 180
    cmid = ((cx0 + cx1) / 2, (cy0 + cy1) / 2)
    rot = []
    for c in cm:
        segs = [(seg[0], *[(2 * cmid[0] - x, 2 * cmid[1] - y)
                           for (x, y) in seg[1:]]) for seg in c]
        rot.append(segs)
    glyph_contours["quoteleft"] = translated(rot, 0, raise_dy)
    glyph_width["quoteleft"] = cx1 - cx0
    gap = 55
    glyph_contours["quotedblright"] = qr + translated(qr, (cx1 - cx0) + gap, 0)
    glyph_width["quotedblright"] = (cx1 - cx0) * 2 + gap
    ql = glyph_contours["quoteleft"]
    glyph_contours["quotedblleft"] = ql + translated(ql, (cx1 - cx0) + gap, 0)
    glyph_width["quotedblleft"] = (cx1 - cx0) * 2 + gap

    # GF Latin Core extension: marks, symbols, composites (per weight)
    import glyph_extensions
    glyph_extensions.add_extensions(glyph_contours, glyph_width, offset,
                                    s_comp, xheight, simplify_contours)

    return glyph_contours, glyph_width, xheight


ITALIC_ANGLE = 9.0  # degrees


def shear_glyphs(glyph_contours, glyph_width, angle=ITALIC_ANGLE):
    """Oblique: shear about the baseline, re-anchor x to ink min."""
    t = np.tan(np.radians(angle))
    out_c, out_w = {}, {}
    for name, contours in glyph_contours.items():
        sheared = [[(seg[0], *[(x + y * t, y) for (x, y) in seg[1:]])
                    for seg in c] for c in contours]
        xs = [p[0] for c in sheared for seg in c for p in seg[1:]]
        x0, x1 = min(xs), max(xs)
        out_c[name] = [[(seg[0], *[(x - x0, y) for (x, y) in seg[1:]])
                        for seg in c] for c in sheared]
        out_w[name] = x1 - x0
    return out_c, out_w


def glyph_polys(glyph_contours):
    """Flatten contours to polygons for the spacing engine."""
    return {name: [_flatten(c) for c in contours]
            for name, contours in glyph_contours.items()}


def assemble_font(glyph_contours, glyph_width, xheight, sbs, fea,
                  style="Regular", weight_class=400, italic=False):
    """Compile a static CFF OTF with per-glyph sidebearings and GPOS kern."""
    from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

    full_style = (style + " Italic" if italic else style).replace(
        "Regular Italic", "Italic")
    glyph_order = ([".notdef", "space"] + [n for n in CMAP if n != "space"]
                   + UNENCODED)
    fb = FontBuilder(UPM, isTTF=False)
    fb.setupGlyphOrder(glyph_order)
    cmap = {}
    for name, codes in CMAP.items():
        for code in codes:
            cmap[code] = name
    fb.setupCharacterMap(cmap)

    charstrings = {}
    metrics = {}
    for name in glyph_order:
        pen = T2CharStringPen(0, None)
        if name in glyph_contours:
            lsb, rsb = sbs.get(name, (SB, SB))
            draw_contours(pen, glyph_contours[name], dx=lsb)
            adv = int(round(glyph_width[name] + lsb + rsb))
            if name in ZERO_ADVANCE:
                adv = 0
        elif name == "space":
            adv = 270
        else:  # .notdef simple box
            pen.moveTo((80, 0))
            pen.lineTo((80, CAP))
            pen.lineTo((420, CAP))
            pen.lineTo((420, 0))
            pen.closePath()
            adv = 500
        charstrings[name] = pen.getCharString()
        metrics[name] = (adv, 0)

    ps_name = f"SunnyMarker-{full_style.replace(' ', '')}"
    fb.setupCFF(ps_name,
                {"FullName": f"Sunny Marker {full_style}",
                 "FamilyName": "Sunny Marker",
                 "Weight": style},
                charstrings, {})
    # fix lsb in hmtx from actual bounds
    glyf_bounds = {}
    cff = fb.font["CFF "].cff[0]
    for name in glyph_order:
        cs = cff.CharStrings[name]
        b = cs.calcBounds(cff.CharStrings)
        glyf_bounds[name] = b
        lsb = int(b[0]) if b else 0
        metrics[name] = (metrics[name][0], lsb)
    fb.setupHorizontalMetrics(metrics)

    all_b = [b for b in glyf_bounds.values() if b]
    ymin = int(min(b[1] for b in all_b))
    ymax = int(max(b[3] for b in all_b))
    print("font bbox y:", ymin, ymax)

    ascent, descent = 900, -250  # ascent clears accented caps
    fb.setupHorizontalHeader(ascent=ascent, descent=descent, lineGap=60)
    is_bold = style == "Bold"
    fsSel = (0x20 if is_bold else 0x40) | (0x01 if italic else 0)
    if italic and not is_bold:
        fsSel &= ~0x40  # italic bit replaces regular bit
    fb.setupOS2(sTypoAscender=ascent, sTypoDescender=descent,
                sTypoLineGap=60, usWinAscent=max(ascent, ymax),
                usWinDescent=abs(min(descent, ymin)),
                sxHeight=int(xheight), sCapHeight=CAP,
                achVendID="SUNY",
                fsSelection=fsSel,
                usWeightClass=weight_class, usWidthClass=5)
    # legacy 4-style model: Regular/Bold(+Italic) live in "Sunny Marker";
    # other weights get their own legacy family + typographic names 16/17
    if style in ("Regular", "Bold"):
        legacy_family = "Sunny Marker"
        legacy_style = full_style
    else:
        legacy_family = f"Sunny Marker {style}"
        legacy_style = "Italic" if italic else "Regular"
    fb.setupNameTable({
        "familyName": legacy_family,
        "styleName": legacy_style,
        "uniqueFontIdentifier": f"{ps_name}:2026",
        "fullName": f"Sunny Marker {full_style}",
        "psName": ps_name,
        "version": "Version 1.100",
        "copyright": "Sunny Marker - traced from hand-drawn reference",
    })
    if style not in ("Regular", "Bold"):
        name = fb.font["name"]
        for pid, eid, lid in ((3, 1, 0x409), (1, 0, 0)):
            name.setName("Sunny Marker", 16, pid, eid, lid)
            name.setName(full_style, 17, pid, eid, lid)
    fb.font["head"].macStyle = (1 if is_bold else 0) | (2 if italic else 0)
    fb.setupPost(italicAngle=-ITALIC_ANGLE if italic else 0)
    if fea:
        fea = fea.replace("feature kern {",
                          CCMP_FEA + "\n" + ALT_FEA + "\nfeature kern {")
        addOpenTypeFeaturesFromString(fb.font, fea)
    out = os.path.join(BUILD, f"{ps_name}.otf")
    fb.save(out)
    print("wrote", out)
    return out
