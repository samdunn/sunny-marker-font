#!/usr/bin/env python3
"""Generate Sunny Marker masters: wght, wdth, opsz and continuous slnt.

Outlines per weight come from normal-displacement of the Regular polylines
(identical point structures -> exact gvar interpolation), with counters
closing at 55% of the outer growth to match the statics. `displace()` keeps
concave corners intact through that offset -- without it the interior joins
dissolve as weight rises (see its comment, and scripts/audit_joins.py).

At opsz 10 (text sizes), counters and narrow mouths open, sidebearings
open up ~30 units/side, and kerning relaxes to 55%. At opsz 36 (display),
spacing is tighter and the original contour detail stays intact.

The upright and 9-degree slanted sources form one designspace. Spacing and
kerning are recomputed after slanting and interpolate with the outlines.
"""
import os
from master_data import load_master_data
import numpy as np
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.designspaceLib import (DesignSpaceDocument, AxisDescriptor,
                                      SourceDescriptor, InstanceDescriptor)
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

import build_font
import spacing
from ufo_sources import export_master, export_designspace
from glyph_extensions import ZERO_ADVANCE, UNENCODED, CCMP_FEA, ALT_FEA
from build_font import CMAP, UPM, CAP

# Stable font timestamps; callers can override for a future release.
os.environ.setdefault("SOURCE_DATE_EPOCH", "1788998400")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
VF_DIR = os.path.join(BUILD, "vf-masters")
SAMPLE = 6.0
TEXT_SB_EXTRA = 30      # opsz 10: extra units per side
TEXT_KERN_SCALE = 0.55  # opsz 10: kerning relaxes
ITALIC_ANGLE = build_font.ITALIC_ANGLE
TAN = float(np.tan(np.radians(ITALIC_ANGLE)))

data = load_master_data(os.path.join(BUILD, "masters.json"))
masters = data["masters"]
emit_pairs = data["emit_pairs"]

WEIGHTS = [("Light", 300), ("Regular", 400), ("Medium", 500),
           ("Bold", 700)]
WIDTHS = [("Condensed", 75, 3), ("Normal", 100, 5), ("Extended", 125, 7)]
# The reference Regular is the drawing source, not the released Regular weight.
# Keep the usable range near that drawing: full erosion loses the irregular
# nib, and full dilation fills counters. Public weight labels stay 300–700.
STROKE_MULTIPLIERS = {"Light": 0.76, "Regular": 0.88,
                      "Medium": 0.97, "Bold": 1.11}
OFFSETS = {s: (mult - 1) * data["stroke"] / 2
           for s, mult in STROKE_MULTIPLIERS.items()}
REG = masters["Regular"]
XHEIGHT = REG["xheight"]
TEXT_XHEIGHT = 480

flatten_contour = build_font._flatten
resample = build_font._resample
normals = build_font._normals
smooth = build_font._smooth


def signed_area(poly):
    x, y = poly[:, 0], poly[:, 1]
    return 0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


# ---- corner-preserving offset -------------------------------------------
# The statics are traced per weight, and raster dilation by a round nib is a
# true Minkowski sum, so their concave corners stay sharp. The VF cannot do
# that: dilation changes topology (Bold seals E/F/G/H/T slots into closed
# counters -- 88 glyphs change contour count), and gvar needs one topology
# across masters. So the VF displaces the Regular polyline instead.
#
# Plain per-vertex displacement gets concave corners wrong twice over:
#   1. normals() is a central difference, so at a sharp vertex it returns the
#      angle bisector. Moving it by `delta` leaves it short of where the two
#      offset flanks actually cross -- short by 1/cos(turn/2), ~3.9x at V's
#      150 degree notch. The flanks close in while the tip stays put.
#   2. The flank vertices within delta/tan(alpha) of the tip offset straight
#      across the bisector (9-15 vertices/side at V's notch), so the true
#      offset self-intersects there and a real offset clips that loop away.
# _smooth() used to paper over both by averaging the mess into a blob, which
# is why VF notches dissolved as weight rose (V: -155 static vs -10 VF).
#
# Mitering alone just turns the mush into a spike -- the crossing loop is
# still there. So we find where the offset flanks actually cross and clip the
# loop, which is what a real offset does. The crossing is found by testing
# segments rather than from the analytic miter (delta/cos(turn/2)): that
# formula assumes straight flanks, and on a curved notch like M's the tip it
# predicts does not line up with the true crossing, leaving a needle.
#
# The clipped vertices are then spread along the two surviving flanks rather
# than piled onto the crossing point. Piling them up looks right but is
# fatal: TTGlyphPen drops duplicate points, the masters stop being
# interpolation-compatible, and varLib silently skips the glyph -- which then
# renders as Regular at every weight.
CORNER_VERTEX_DEG = 20.0   # a corner turns this much at ONE vertex; a round
                           # marker cap spreads 180 deg over ~33 vertices at
                           # ~5 deg each, so curves never qualify
CORNER_TOTAL_DEG = 30.0    # total turn across a corner's vertices
CORNER_MAX_SPAN = 4        # vertices per corner after 6u resampling (1-2)
MIN_HALF_ANGLE = 3.0       # deg; bounds the search on near-180 deg slits
WINDOW_CAP = 40            # vertices searched either side of a corner


def _turns(poly):
    """Signed exterior turn at each vertex, radians."""
    e_prev = poly - np.roll(poly, 1, axis=0)
    e_next = np.roll(poly, -1, axis=0) - poly
    cross = e_prev[:, 0] * e_next[:, 1] - e_prev[:, 1] * e_next[:, 0]
    return np.arctan2(cross, (e_prev * e_next).sum(axis=1))


def _ring_arc(poly):
    """(arc position of each vertex, perimeter)."""
    e = np.linalg.norm(np.roll(poly, -1, axis=0) - poly, axis=1)
    return np.concatenate([[0.0], np.cumsum(e)[:-1]]), float(e.sum())


def corner_clusters(poly):
    """-> [(indices, total_turn_rad)] for sharp vertices only."""
    phi = _turns(poly)
    n = len(poly)
    vmin = np.radians(CORNER_VERTEX_DEG)
    seen = np.zeros(n, bool)
    out = []
    for i in range(n):
        if seen[i] or abs(phi[i]) < vmin:
            continue
        s = np.sign(phi[i])
        idx = [i]
        seen[i] = True
        for step in (1, -1):
            j = (i + step) % n
            while (not seen[j] and np.sign(phi[j]) == s
                   and abs(phi[j]) >= vmin and len(idx) < CORNER_MAX_SPAN):
                seen[j] = True
                idx.append(j) if step == 1 else idx.insert(0, j)
                j = (j + step) % n
        total = float(np.sum(phi[idx]))
        if abs(total) >= np.radians(CORNER_TOTAL_DEG):
            out.append((idx, total))
    return out


def _cross(a1, a2, b1, b2):
    """Proper intersection of segments a1a2 and b1b2, else None."""
    r = a2 - a1
    s = b2 - b1
    den = r[0] * s[1] - r[1] * s[0]
    if abs(den) < 1e-12:
        return None
    q = b1 - a1
    t = (q[0] * s[1] - q[1] * s[0]) / den
    u = (q[0] * r[1] - q[1] * r[0]) / den
    if 1e-9 < t < 1 - 1e-9 and 1e-9 < u < 1 - 1e-9:
        return a1 + t * r
    return None


def displace(poly, delta):
    """Offset `poly` by `delta` along its normals, keeping concave corners.

    Returns (moved, pinned); `pinned` marks vertices that must not be
    smoothed afterwards -- the rebuilt corner and its clipped flanks.
    """
    nrm = normals(poly)
    moved = poly + delta * nrm
    n = len(poly)
    pinned = np.zeros(n, bool)
    if delta == 0 or n < 12:
        return moved, pinned

    arc, per = _ring_arc(poly)
    spacing = per / n

    def idx_dist(i, j):
        d = abs(i - j)
        return min(d, n - d)

    clusters = corner_clusters(poly)
    centres = [idx[len(idx) // 2] for idx, _ in clusters]
    for (idx, total), c in zip(clusters, centres):
        # A vertex on the OUTSIDE of the offset is an arc; plain displacement
        # already lands on it (this is why round caps came through fine).
        if delta * total >= 0:
            continue
        # Search far enough to reach the crossing: it sits about
        # delta/tan(alpha) along each flank. Stop half-way to the neighbouring
        # corner so two corners' loops can never be merged into one.
        alpha = max((np.pi - abs(total)) / 2.0, np.radians(MIN_HALF_ANGLE))
        want = int(abs(delta) / np.tan(alpha) / max(spacing, 1e-6)) + 3
        lim = n // 3
        for o in centres:
            if o != c:
                lim = min(lim, max(2, idx_dist(c, o) // 2))
        W = int(min(want, lim, WINDOW_CAP))
        if W < 2:
            continue

        # Widest crossing of a left-flank segment with a right-flank one.
        best = None
        for i in range(1, W):
            ii = (c - i) % n
            for j in range(1, W):
                jj = (c + j) % n
                X = _cross(moved[ii], moved[(ii + 1) % n],
                           moved[jj], moved[(jj + 1) % n])
                if X is not None and (best is None or i + j > best[0]):
                    best = (i + j, ii, jj, X)
        if best is None:
            continue                    # no loop: plain offset is already right
        _, ii, jj, X = best

        span = []
        k = (ii + 1) % n
        while k != (jj + 1) % n:
            span.append(k)
            k = (k + 1) % n
        if not span or c not in span or len(span) > 0.4 * n:
            continue
        cut = span.index(c)
        left, right = span[:cut + 1], span[cut + 1:]
        # Spread the clipped vertices along the two flanks that survive, so
        # they sit on the real clipped outline and stay distinct.
        a = moved[ii].copy()
        b = moved[(jj + 1) % n].copy()
        for t, k in enumerate(left, start=1):
            moved[k] = a + (X - a) * (t / len(left))
        for t, k in enumerate(right, start=1):
            moved[k] = X + (b - X) * (t / (len(right) + 1))
        pinned[span] = True
    return moved, pinned


SMOOTH_RAMP = 4        # vertices over which smoothing fades back in


def smooth_pinned(poly, pinned, passes=2, lam=0.35):
    """_smooth, but the rebuilt corners hold still -- otherwise the Laplacian
    rounds off the very corner the clip just reconstructed.

    The weight ramps back to full over SMOOTH_RAMP vertices rather than
    switching hard: a hard edge between held and smoothed vertices leaves a
    shallow kink right beside every corner, which reads as a jaggy segment.
    """
    w = np.ones(len(poly))
    w[pinned] = 0.0
    for _ in range(SMOOTH_RAMP):
        w = np.minimum(w, np.minimum(np.roll(w, 1), np.roll(w, -1)) + 1.0 / SMOOTH_RAMP)
    p = poly.copy()
    for _ in range(passes):
        avg = (np.roll(p, -1, axis=0) + np.roll(p, 1, axis=0)) / 2
        p = p + (lam * w)[:, None] * (avg - p)
    return p


# sign calibration on 'O' outer contour
o_polys = [resample(flatten_contour(c), SAMPLE) for c in REG["contours"]["O"]]
outer = max(o_polys, key=lambda p: np.ptp(p[:, 0]))
grown = outer + 10 * normals(outer)
SIGN = 1.0 if np.ptp(grown[:, 0]) > np.ptp(outer[:, 0]) else -1.0

base_polys = {gname: [resample(flatten_contour(c), SAMPLE) for c in contours]
              for gname, contours in REG["contours"].items()}

os.makedirs(VF_DIR, exist_ok=True)
glyph_order = ([".notdef", "space"] + [n for n in CMAP if n != "space"]
               + UNENCODED)
cmap = {}
for name, codes in CMAP.items():
    for code in codes:
        cmap[code] = name

kern_pairs_all = spacing.kern_candidates()


def build_master(style, wght, opsz, moved_map, widths, sbs, kern, path,
                 italic=False, wdth=100, width_class=5):
    glyphs = {}
    metrics = {}
    for gname in glyph_order:
        # Never drop a closing point in only some masters.
        pen = TTGlyphPen(None, outputImpliedClosingLine=True)
        if gname in moved_map:
            lsb, rsb = sbs.get(gname, (spacing.GAP, spacing.GAP))
            for moved in moved_map[gname]:
                pen.moveTo((moved[0][0] + lsb, moved[0][1]))
                for pt in moved[1:]:
                    pen.lineTo((pt[0] + lsb, pt[1]))
                pen.closePath()
            adv = int(round(widths[gname] + lsb + rsb))
            if gname in ZERO_ADVANCE:
                adv = 0
        elif gname == "space":
            adv = round((270 + (TEXT_SB_EXTRA if opsz == 10 else 0)) * wdth / 100)
        else:
            pen.moveTo((80, 0))
            pen.lineTo((80, CAP))
            pen.lineTo((420, CAP))
            pen.lineTo((420, 0))
            pen.closePath()
            adv = 500
        glyphs[gname] = pen.glyph()
        metrics[gname] = (adv, 0)

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    glyf = fb.font["glyf"]
    for gname in glyph_order:
        g = glyf[gname]
        lsb = g.xMin if hasattr(g, "xMin") and g.numberOfContours else 0
        metrics[gname] = (metrics[gname][0], lsb)
    fb.setupHorizontalMetrics(metrics)
    ymin = min((glyf[g].yMin for g in glyph_order
                if glyf[g].numberOfContours), default=-250)
    ymax = max((glyf[g].yMax for g in glyph_order
                if glyf[g].numberOfContours), default=860)
    fb.setupHorizontalHeader(ascent=900, descent=-250, lineGap=60)
    fb.setupOS2(sTypoAscender=900, sTypoDescender=-250, sTypoLineGap=60,
                usWinAscent=max(900, ymax + 40), usWinDescent=abs(min(-250, ymin)),
                sCapHeight=CAP,
                sxHeight=round(TEXT_XHEIGHT if opsz == 10 else XHEIGHT),
                achVendID="SUNY", fsSelection=(0x01 if italic else 0x40),
                usWeightClass=wght, usWidthClass=width_class)
    sname = f"{style} Italic" if italic else style
    fb.setupNameTable({
        "familyName": "Sunny Marker Variable",
        "styleName": sname,
        "psName": f"SunnyMarkerVariable-{sname.replace(' ', '')}-w{wdth}-o{opsz}",
        "version": "Version 1.301",
    })
    fb.setupPost(italicAngle=-ITALIC_ANGLE if italic else 0)
    if italic:
        fb.font["head"].macStyle |= 0x2
        fb.font["hhea"].caretSlopeRise = 1000
        fb.font["hhea"].caretSlopeRun = int(round(1000 * TAN))
    fea = spacing.kern_feature(kern, emit_pairs)
    fea = fea.replace("feature kern {",
                      CCMP_FEA + "\n" + ALT_FEA + "\nfeature kern {")
    addOpenTypeFeaturesFromString(fb.font, fea)
    fb.save(path)
    export_master(fb.font, fea, os.path.join(ROOT, "sources", os.path.basename(path)))


def width_transform(poly, scale, stroke, outer=True):
    """Change width with horizontal stroke compensation, before italic shear.

    Condensed lightens the nib by 9% to keep counters open, following the
    static width prototype. Extended restores vertical strokes to their
    normal width. Applying only the x component of a corner-preserving
    offset retains the original vertical metrics and compatible topology.
    Small components cap compensation to avoid erasing accents/dots.
    """
    if scale == 1:
        return poly.copy()
    local_stroke = min(stroke, np.ptp(poly[:, 0]), np.ptp(poly[:, 1]))
    target = 0.91 if scale < 1 else 1.0
    delta = local_stroke * (target / scale - 1) / 2
    if delta > 0 and not outer:
        delta *= 0.55
    offset, _ = displace(poly, SIGN * delta)
    result = poly.copy()
    result[:, 0] = offset[:, 0] * scale
    return result


def text_outlines(moved_map):
    """Open counters and narrow mouths at small optical sizes.

    This leaves the hand-drawn contour landmarks in place, with exactly the
    same point structure. Counter relief is independent of weight: tiny
    counters should not fill in just because a label is bold.
    """
    result = {}
    lowercase = {name for name, codes in CMAP.items()
                 if any(chr(code).islower() for code in codes)} | {"jacute"}
    for name, polys in moved_map.items():
        big = max(polys, key=lambda p: abs(signed_area(p)))
        outer_sign = np.sign(signed_area(big))
        # Ascender accents follow the ascender, not the x-height. Translating
        # every detached mark by the x-height increase pushed lacute above
        # the line metrics and moved side carons away from d/l/t.
        bodies = [p for p in polys if p[:, 1].min() <= XHEIGHT + 12]
        body_top = max((p[:, 1].max() for p in bodies), default=XHEIGHT)
        if body_top <= XHEIGHT:
            mark_lift = TEXT_XHEIGHT - XHEIGHT
        elif body_top < CAP:
            mark_lift = (TEXT_XHEIGHT + (body_top-XHEIGHT)
                         * (CAP-TEXT_XHEIGHT)/(CAP-XHEIGHT) - body_top)
        else:
            mark_lift = 0
        opened = []
        for poly in polys:
            is_counter = np.sign(signed_area(poly)) != outer_sign
            # e/c/s and their accented forms have open rather than closed
            # counters. A small inset gives their mouths breathing room.
            mouth = name[0] in 'ecs' and not name.endswith('comb')
            delta = -4.0 if is_counter else -1.5 if mouth else 0.0
            moved, pinned = displace(poly, SIGN * delta)
            moved = smooth_pinned(moved, pinned, passes=1) if delta else moved
            if name in lowercase:
                moved = moved.copy()
                ys = moved[:, 1]
                if poly[:, 1].min() > XHEIGHT + 12:
                    # Detached dots and accents travel with the taller body;
                    # preserve their thickness instead of stretching them.
                    moved[:, 1] += mark_lift
                else:
                    # A larger lowercase body helps at 16–24 px. Keep the
                    # baseline, descenders and ascender/cap height anchored.
                    body = (ys > 0) & (ys <= XHEIGHT)
                    ascender = ys > XHEIGHT
                    moved[body, 1] = ys[body] * TEXT_XHEIGHT / XHEIGHT
                    moved[ascender, 1] = (TEXT_XHEIGHT + (ys[ascender] - XHEIGHT)
                                          * (CAP - TEXT_XHEIGHT) / (CAP - XHEIGHT))
            opened.append(moved)
        result[name] = opened
    return result


def run(italic):
    tag = "Italic" if italic else "Roman"
    master_paths = []
    for width_name, wdth, width_class in WIDTHS:
        scale = wdth / 100
        for style, wght in WEIGHTS:
            d = OFFSETS[style]
            s_comp = CAP / (CAP + 2 * d)
            moved_map = {}
            widths = {}
            for gname, polys in base_polys.items():
                big = max(polys, key=lambda p: abs(signed_area(p)))
                outer_sign = np.sign(signed_area(big))
                moved_polys = []
                for poly in polys:
                    is_outer = np.sign(signed_area(poly)) == outer_sign
                    # Preserve narrow stems, dots, accents, and interior
                    # strokes instead of applying a whole-letter nib offset.
                    local_nib = min(1.0, np.ptp(poly[:, 0]) / 124,
                                    np.ptp(poly[:, 1]) / 124)
                    factor = local_nib if is_outer else (0.40 if d < 0 else 0.20)
                    if gname in {"Ccedilla", "ccedilla", "Scedilla", "scedilla",
                                 "cedilla.spacing", "cedillacomb"} and poly[:, 1].max() < 60:
                        # The cedilla nib is smaller than a letter's nib; applying
                        # the full letter offset erases the Light hook.
                        factor *= 0.35 if gname[0].isupper() else 0.47
                    moved, pinned = displace(poly, SIGN * d * factor)
                    moved = smooth_pinned(moved, pinned) if d != 0 else moved
                    moved = moved.copy()
                    moved[:, 0] = (moved[:, 0] + d) * s_comp
                    moved[:, 1] = (moved[:, 1] + d) * s_comp
                    moved = width_transform(moved, scale, (124 + 2 * d) * s_comp,
                                            np.sign(signed_area(poly)) == outer_sign)
                    if italic:
                        moved[:, 0] += moved[:, 1] * TAN
                    moved_polys.append(moved)
                minx = min(p[:, 0].min() for p in moved_polys)
                moved_polys = [p - [minx, 0] for p in moved_polys]
                moved_map[gname] = moved_polys
                widths[gname] = float(max(p[:, 0].max() for p in moved_polys))

            profiles = {}
            for gname, ps in moved_map.items():
                l, r = spacing.glyph_profiles(ps)
                ys = np.concatenate([p[:, 1] for p in ps])
                profiles[gname] = (l, r, float(ys.min()), float(ys.max()))
            gap_w = (spacing.GAP - 0.25 * d) * (0.80 if wdth < 100 else
                                                       1.12 if wdth > 100 else 1)
            sbs = spacing.compute_sidebearings(profiles, widths, XHEIGHT,
                                               gap=gap_w)
            fscale = ((124 + 2 * d) / 124) ** 0.5
            kern = spacing.compute_kerning(profiles, widths, sbs, kern_pairs_all,
                                           gap=gap_w, floor_scale=fscale)

            # display master (opsz 36): tight, matches statics
            p40 = os.path.join(VF_DIR, f"master-{tag}-{style}-w{wdth}-o36.ttf")
            build_master(style, wght, 36, moved_map, widths, sbs, kern, p40,
                         italic=italic, wdth=wdth, width_class=width_class)
            # text master: open counters/mouths as well as spacing and kerning.
            sbs10 = {n: (l + TEXT_SB_EXTRA * scale, r + TEXT_SB_EXTRA * scale)
                     for n, (l, r) in sbs.items()}
            kern10 = {p: int(round(v * TEXT_KERN_SCALE)) for p, v in kern.items()}
            p10 = os.path.join(VF_DIR, f"master-{tag}-{style}-w{wdth}-o10.ttf")
            build_master(style, wght, 10, text_outlines(moved_map), widths, sbs10, kern10, p10,
                         italic=italic, wdth=wdth, width_class=width_class)
            master_paths.append((style, wght, wdth, p40, p10))
            print("masters", tag, width_name, style, wght, flush=True)
    doc = DesignSpaceDocument()
    ax_w = AxisDescriptor()
    ax_w.minimum, ax_w.default, ax_w.maximum = 300, 400, 700
    ax_w.name, ax_w.tag = "Weight", "wght"
    doc.addAxis(ax_w)
    ax_d = AxisDescriptor()
    ax_d.minimum, ax_d.default, ax_d.maximum = 75, 100, 125
    ax_d.name, ax_d.tag = "Width", "wdth"
    doc.addAxis(ax_d)
    ax_o = AxisDescriptor()
    ax_o.minimum, ax_o.default, ax_o.maximum = 10, 36, 36
    ax_o.name, ax_o.tag = "Optical size", "opsz"
    doc.addAxis(ax_o)
    for style, wght, wdth, p40, p10 in master_paths:
        for opsz, path in ((36, p40), (10, p10)):
            src = SourceDescriptor()
            src.path = path
            src.location = {"Weight": wght, "Width": wdth, "Optical size": opsz}
            src.familyName = "Sunny Marker Variable"
            src.styleName = f"{tag} {style} w{wdth} o{opsz}"
            doc.addSource(src)
    # GF requires named instances at every 100-unit weight in range
    for width_name, wdth, _ in WIDTHS:
        for style, wght in [("Light", 300), ("Regular", 400), ("Medium", 500),
                            ("SemiBold", 600), ("Bold", 700)]:
            inst = InstanceDescriptor()
            inst.location = {"Weight": wght, "Width": wdth, "Optical size": 36}
            inst.familyName = "Sunny Marker Variable"
            if italic:
                inst.styleName = ("Italic" if style == "Regular"
                                  else f"{style} Italic")
            else:
                inst.styleName = style
            if wdth != 100:
                inst.styleName = f"{width_name} {inst.styleName}"
            doc.addInstance(inst)
    ds_path = os.path.join(VF_DIR, f"SunnyMarker-{tag}.designspace")
    doc.write(ds_path)
    export_designspace(doc, os.path.join(ROOT, "sources", f"SunnyMarker-{tag}.designspace"))

    # Fail early instead of allowing varLib to silently skip incompatible glyphs.
    from fontTools.ttLib import TTFont
    topology = None
    for source in doc.sources:
        with TTFont(source.path) as master:
            current = {g: tuple(master["glyf"][g].endPtsOfContours)
                       for g in glyph_order if master["glyf"][g].numberOfContours}
        if topology is None:
            topology = current
        if current != topology:
            raise ValueError(f"Incompatible master topology: {source.path}")
    return doc


def combine_sources():
    """One compatible designspace interpolates continuously through slant."""
    from pathlib import Path
    sources = Path(ROOT) / "sources"
    roman = DesignSpaceDocument.fromfile(sources / "SunnyMarker-Roman.designspace")
    italic = DesignSpaceDocument.fromfile(sources / "SunnyMarker-Italic.designspace")
    slant = AxisDescriptor()
    slant.name, slant.tag = "Slant", "slnt"
    slant.minimum, slant.default, slant.maximum = -ITALIC_ANGLE, 0, 0
    roman.addAxis(slant)
    for source in roman.sources:
        source.location["Slant"] = 0
    for source in italic.sources:
        source.location["Slant"] = -ITALIC_ANGLE
        roman.addSource(source)
    for instance in roman.instances:
        instance.location["Slant"] = 0
    for instance in italic.instances:
        instance.location["Slant"] = -ITALIC_ANGLE
        roman.addInstance(instance)
    roman.write(sources / "SunnyMarker.designspace")
    for style in ("Roman", "Italic"):
        (sources / f"SunnyMarker-{style}.designspace").unlink()


if __name__ == "__main__":
    run(italic=False)
    run(italic=True)
    combine_sources()
