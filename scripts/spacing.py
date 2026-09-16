#!/usr/bin/env python3
"""Optical spacing + kerning for Sunny Marker.

Sidebearings: simplified HT-Letterspacer. For each glyph, sample the left and
right ink profiles over a reference zone and set the margin so the average
optical gap (capped at DEPTH so open shapes like L/T don't overreact) hits a
constant target. Flat stems get the full margin; recessed or diagonal sides
pull in automatically.

Kerning: for every candidate pair, measure the actual ink gap profile
(margins included) over the rows where both glyphs have ink, and kern so the
weighted mean gap hits the target while the closest approach never drops
below MIN_CLEAR.
"""
import numpy as np

UPPER = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
LOWER = set("abcdefghijklmnopqrstuvwxyz")
# cap-height alternates reached through GSUB: spaced and kerned as caps, so
# switching a feature on never falls back to default spacing
ALT_CAPS = {"I.ss01"}
DIGITS = {"zero", "one", "two", "three", "four", "five", "six", "seven",
          "eight", "nine"}

# tuning
GAP = 51          # target one-side optical margin (stem-stem pair gap = 2*GAP)
DEPTH = 80        # profile depth cap for sidebearing averaging
DAMP = 0.55       # fraction of mean depth pulled back in (full=overtight)
SB_MIN, SB_MAX = 0, 130
KERN_TARGET = 2 * GAP   # desired mean pair gap
MIN_CLEAR = 50          # minimum ink clearance after kerning
# deep negative room for overhang pairs (T/F/P/Y + lowercase); actual
# collision safety comes from the adaptive clearance floor, not this clamp
KERN_MIN, KERN_MAX = -230, 40
KERN_THRESH = 10

YGRID = np.arange(-260, 760, 5.0)

KERN_PUNCT = ["period", "comma", "quotesingle", "quotedbl", "quoteleft",
              "quoteright", "quotedblleft", "quotedblright", "hyphen",
              "exclam", "question", "colon", "semicolon", "slash"]


def glyph_profiles(polys):
    """left[], right[] x-values per YGRID row (nan where no ink)."""
    left = np.full(len(YGRID), np.nan)
    right = np.full(len(YGRID), np.nan)
    for poly in polys:
        p = np.asarray(poly)
        a = p
        b = np.roll(p, -1, axis=0)
        for i, y in enumerate(YGRID):
            hit = (a[:, 1] - y) * (b[:, 1] - y) <= 0
            hit &= np.abs(a[:, 1] - b[:, 1]) > 1e-9
            if not hit.any():
                continue
            aa, bb = a[hit], b[hit]
            t = (y - aa[:, 1]) / (bb[:, 1] - aa[:, 1])
            xs = aa[:, 0] + t * (bb[:, 0] - aa[:, 0])
            lo, hi = xs.min(), xs.max()
            left[i] = lo if np.isnan(left[i]) else min(left[i], lo)
            right[i] = hi if np.isnan(right[i]) else max(right[i], hi)
    return left, right


def zone_for(name, ink_lo, ink_hi, xheight, cap):
    if name in UPPER or name in ALT_CAPS or name in DIGITS:
        return 10, cap - 10
    if name in LOWER:
        return 10, xheight - 5
    # punctuation/symbols: their own vertical extent, clipped
    return max(ink_lo + 4, -220), min(ink_hi - 4, 720)


# hand-tuned craft layer, applied after the automatic pass (units, additive)
SB_OVERRIDES = {}          # name: (dlsb, drsb)
KERN_OVERRIDES = {}        # (L, R): delta
# cap + J (all-caps acronyms): J's empty upper left leaves a crater that the
# mean metric can't close within the clamp — pull these in further
KERN_OVERRIDES.update({(c, "J"): -55 for c in "ABCDEFGHIKLMNOPRSTUVWXYZ"})
# j's left sidebearing includes its descender hook, leaving excess air
# after a word space (flagged by review on the Light styles)
KERN_OVERRIDES[("space", "j")] = -35


def compute_sidebearings(profiles, widths, xheight, cap=700, gap=GAP):
    """profiles: {name: (left, right, ink_lo, ink_hi)}. -> {name: (lsb, rsb)}

    gap: weight-scaled target margin (bolder styles run tighter)."""
    sbs = {}
    for name, (left, right, ink_lo, ink_hi) in profiles.items():
        w = widths[name]
        zlo, zhi = zone_for(name, ink_lo, ink_hi, xheight, cap)
        rows = (YGRID >= zlo) & (YGRID <= zhi)
        if not rows.any():
            sbs[name] = (int(gap), int(gap))
            continue
        dl = left[rows].copy()
        dr = w - right[rows]
        dl[np.isnan(dl)] = DEPTH  # empty row = fully recessed (capped)
        dr[np.isnan(dr)] = DEPTH
        lsb = gap - DAMP * min(float(np.mean(np.minimum(dl, DEPTH))), DEPTH)
        rsb = gap - DAMP * min(float(np.mean(np.minimum(dr, DEPTH))), DEPTH)
        odl, odr = SB_OVERRIDES.get(name, (0, 0))
        sbs[name] = (int(np.clip(round(lsb + odl), SB_MIN, SB_MAX)),
                     int(np.clip(round(rsb + odr), SB_MIN, SB_MAX)))
    return sbs


def kern_candidates():
    names = (sorted(UPPER) + sorted(ALT_CAPS) + sorted(LOWER)
             + sorted(DIGITS) + KERN_PUNCT)
    return [(l, r) for l in names for r in names]


# all-caps settings (buttons, labels) read best with extra air — calibrated
# against the reference sheet's usage examples
CAPS_EXTRA = 48
CAPS_CLASS = UPPER | ALT_CAPS | DIGITS | {"exclam", "question"}


def compute_kerning(profiles, widths, sbs, pairs, gap=GAP, floor_scale=1.0):
    """-> {(L,R): kern} for all candidate pairs (unfiltered values).

    floor_scale: clearance floors scale with stroke weight — heavier
    strokes need more absolute whitespace to read as separate."""
    base_target = 2 * gap
    caps_extra = CAPS_EXTRA * gap / GAP
    kern = {}
    for (L, R) in pairs:
        if L not in profiles or R not in profiles:
            continue
        lL, rL, loL, hiL = profiles[L]
        lR, rR, loR, hiR = profiles[R]
        rows = ~np.isnan(rL) & ~np.isnan(lR)
        rows &= (YGRID >= -220) & (YGRID <= 720)
        if rows.sum() < 3:
            continue
        target = base_target
        if L in CAPS_CLASS and R in CAPS_CLASS:
            target += caps_extra
        gap = ((widths[L] - rL[rows]) + sbs[L][1]
               + sbs[R][0] + lR[rows])
        k = target - float(np.mean(gap))
        min_gap = float(np.min(gap))
        # adaptive clearance floor: a short near-miss (the tip of r's arm,
        # a diagonal corner) may pass much closer than a long parallel edge
        near_span = float(((gap - min_gap) < 12).sum()) * 5.0  # units tall
        if near_span <= 25:
            floor = 28 * floor_scale
        elif near_span <= 60:
            floor = 40 * floor_scale
        else:
            floor = MIN_CLEAR * floor_scale
        if min_gap + k < floor:
            k = floor - min_gap
        k = float(np.clip(k, KERN_MIN, KERN_MAX))
        kern[(L, R)] = int(round(k))
    for p, dv in KERN_OVERRIDES.items():
        kern[p] = int(np.clip(kern.get(p, 0) + dv, KERN_MIN - 60, KERN_MAX + 60))
    return kern


def kern_feature(kern, emit_pairs):
    """Build a fea string for the given pair list (values from kern dict)."""
    lines = ["languagesystem DFLT dflt;", "languagesystem latn dflt;",
             "feature kern {"]
    for (L, R) in emit_pairs:
        v = kern.get((L, R), 0)
        lines.append(f"    pos \\{L} \\{R} {v};")
    lines.append("} kern;")
    return "\n".join(lines)
