"""Put points on curve extremes and drop points the drawing does not need.

All masters change together, so every glyph keeps one shared point structure.

1. Split curves at their horizontal and vertical extremes. Each master gets a
   node at its own extreme; the italic masters use slanted extremes. An
   extreme within MIN_PIECE units of an existing smooth node replaces that
   node, so no tiny segment appears.
2. Merge neighbouring segments when one cubic that keeps both end tangents
   stays within TOLERANCE units of the original drawing in every master.
   Every merge is measured against the original outline, so repeated merges
   cannot add up. Nodes on extremes and at corners stay. Two lines that run
   on nearly straight become one line, stood exactly upright or level when
   it would otherwise sit a fraction of a degree off; when one line would
   stray too far in some master, they become one gentle curve. No merged
   segment turns more than 115 degrees (a quarter arc plus slant) or gains
   an extreme of its own.
3. Split again at any extreme the merge exposed in another master.

A glyph keeps only step 1 if its refit outline moves more than
TOLERANCE + 1.5 units from the original at any master or at the midpoint
between two neighbouring masters. Anchors, components and metrics are not
touched. The report lists every glyph's point counts and largest movement.
"""

import argparse
import itertools
import json
import re
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree
from ufoLib2 import Font

from polish_sources import write_contour
from round_source_joins import segment_curves

REFERENCE = "master-Roman-Regular-w100-o36.ufo"
SLANT = float(np.tan(np.radians(9)))
EXTREME_MIN = 1.0
CORNER_DEGREES = 15
AXIS_DEGREES = 2
MAX_TURN_DEGREES = 115
SAMPLES = 24
MIN_PIECE = 8.0
NEAR_AXIS_DEGREES = 0.6
COLINEAR_DEGREES = 8.0  # fontspector flags joins under 0.1 rad (5.73°); rounding short lines can shift a join ~1.5°
JOIN_BEND_DEGREES = 20  # bend a join may have in the reference and still merge


def bezier(c, t):
    t = np.asarray(t, dtype=float)[..., None]
    return (
        (1 - t) ** 3 * c[0]
        + 3 * (1 - t) ** 2 * t * c[1]
        + 3 * (1 - t) * t * t * c[2]
        + t**3 * c[3]
    )


def deslant(c, slant):
    out = np.array(c, dtype=float, copy=True)
    out[..., 0] -= slant * out[..., 1]
    return out


def extreme_ts(c, axis, lo=0.02, hi=0.98):
    p0, p1, p2, p3 = c[:, axis]
    a = -p0 + 3 * p1 - 3 * p2 + p3
    b = 2 * (p0 - 2 * p1 + p2)
    k = p1 - p0
    if abs(a) < 1e-9:
        roots = [-k / b] if abs(b) > 1e-9 else []
    else:
        disc = b * b - 4 * a * k
        if disc < 0:
            return []
        s = np.sqrt(disc)
        roots = [(-b - s) / (2 * a), (-b + s) / (2 * a)]
    return sorted(float(r) for r in roots if lo < r < hi)


def bulging_extremes(c):
    """Interior extremes that stand clear of both segment ends."""
    found = []
    for axis in (0, 1):
        for t in extreme_ts(c, axis):
            v = bezier(c, t)[axis]
            if min(abs(v - c[0, axis]), abs(v - c[3, axis])) > EXTREME_MIN:
                found.append((t, axis))
    found.sort()
    kept = []
    for t, axis in found:
        if not kept or t - kept[-1][0] > 0.02:
            kept.append((t, axis))
    return kept


def split_at(c, ts):
    """Split one cubic (4, 2) at increasing parameters."""
    pieces, rest, done = [], np.array(c, dtype=float), 0.0
    for t in ts:
        u = (t - done) / (1 - done)
        p01 = rest[0] + (rest[1] - rest[0]) * u
        p12 = rest[1] + (rest[2] - rest[1]) * u
        p23 = rest[2] + (rest[3] - rest[2]) * u
        p012 = p01 + (p12 - p01) * u
        p123 = p12 + (p23 - p12) * u
        mid = p012 + (p123 - p012) * u
        pieces.append(np.array([rest[0], p01, p012, mid]))
        rest = np.array([mid, p123, p23, rest[3]])
        done = t
    pieces.append(rest)
    return pieces


def align_handles(left, right, axis, slant):
    """Make both handles at a split extreme exactly level or upright."""
    node = left[3]
    for handle in (left[2], right[1]):
        if axis == 1:
            handle[1] = node[1]
        else:
            handle[0] = node[0] + slant * (handle[1] - node[1])


def master_ts(curve, slant, targets):
    """Each reference extreme's parameter in one master, and whether it is that
    master's own extreme (True) or the reference parameter reused (False)."""
    local = deslant(curve, slant)
    ts, own = [], []
    for t_ref, axis in targets:
        roots = [r for r in extreme_ts(local, axis, 0.005, 0.995) if abs(r - t_ref) < 0.25]
        if roots:
            ts.append(min(roots, key=lambda r: abs(r - t_ref)))
            own.append(True)
        else:
            ts.append(t_ref)
            own.append(False)
    if any(b <= a + 1e-3 for a, b in zip(ts, ts[1:])):
        return [t for t, _ in targets], [False] * len(targets)
    return ts, own


def split_any(curves, s, targets, slants):
    """Split one segment in every master at its extremes, short pieces allowed."""
    result = []
    for m in range(len(curves)):
        ts, own = master_ts(curves[m, s], slants[m], targets)
        pieces = split_at(curves[m, s], ts)
        for k, ((_, axis), mine) in enumerate(zip(targets, own)):
            if mine:
                align_handles(pieces[k], pieces[k + 1], axis, slants[m])
        result.append(pieces)
    return [np.array([result[m][k] for m in range(len(curves))]) for k in range(len(targets) + 1)]


def absorb(long_side, short_side, before, tolerance, slants, ref):
    """Fit `before` + short piece (or short piece + `before`) as one curve.

    Moving the shared node onto the extreme this way avoids a tiny segment.
    The fit is measured against the outline the two pieces describe.
    """
    if before is None:
        return None
    first, second = (before, short_side) if long_side == "after" else (short_side, before)
    samples = np.concatenate([segment_samples(first), segment_samples(second)[:, 1:]], axis=1)
    t0, _ = tangents(first)
    _, t1 = tangents(second)
    merged, error = fit_span(samples, unit(t0), unit(t1), tolerance)
    if merged is None:
        return None
    start_t, end_t = tangents(merged)
    direction = merged[:, 3] - merged[:, 0]
    if (angle(start_t, end_t) > MAX_TURN_DEGREES).any():
        return None
    if ((start_t * direction).sum(-1) <= 0).any() or ((end_t * direction).sum(-1) <= 0).any():
        return None
    if bulging_extremes(deslant(merged[ref], slants[ref])):
        return None
    return merged


def split_extremes(curves, kinds, protected, slants, ref, snap_tolerance=0.0):
    """Give every curve a node at each extreme, shared by all masters.

    An extreme within MIN_PIECE units of an existing smooth node takes that
    node's place: the neighbouring segment is refit to end on the extreme
    (within snap_tolerance of the outline). Otherwise it is left alone.
    """
    segs = [np.array(curves[:, i]) for i in range(curves.shape[1])]
    kinds, protected = list(kinds), list(protected)
    added = 0
    i = 0
    while i < len(segs):
        n = len(segs)
        if kinds[i] != "curve":
            i += 1
            continue
        targets = bulging_extremes(deslant(segs[i][ref], slants[ref]))
        if not targets:
            i += 1
            continue
        stack = np.stack(segs, axis=1)
        pieces = split_any(stack, i, targets, slants)
        lengths = [np.linalg.norm(pc[:, 3] - pc[:, 0], axis=-1).min() for pc in pieces]
        if min(lengths) >= MIN_PIECE:
            segs[i:i + 1] = pieces
            kinds[i:i + 1] = ["curve"] * len(pieces)
            protected[i:i + 1] = [protected[i]] + [True] * len(targets)
            added += len(targets)
            i += len(pieces)
            continue
        if len(targets) == 1 and snap_tolerance > 0:
            prev, nxt = (i - 1) % n, (i + 1) % n
            if lengths[0] < MIN_PIECE and lengths[1] >= MIN_PIECE and not protected[i] \
                    and kinds[prev] == "curve":
                merged = absorb("after", pieces[0], segs[prev], snap_tolerance, slants, ref)
                if merged is not None:
                    segs[prev] = merged
                    segs[i] = pieces[1]
                    protected[i] = True
                    added += 1
                    i += 1
                    continue
            if lengths[1] < MIN_PIECE and lengths[0] >= MIN_PIECE and not protected[nxt] \
                    and kinds[nxt] == "curve" and nxt != i:
                merged = absorb("before", pieces[1], segs[nxt], snap_tolerance, slants, ref)
                if merged is not None:
                    segs[i] = pieces[0]
                    segs[nxt] = merged
                    protected[nxt] = True
                    added += 1
                    i += 1
                    continue
        i += 1
    return np.stack(segs, axis=1), kinds, protected, added


def angle(u, v):
    nu = np.linalg.norm(u, axis=-1)
    nv = np.linalg.norm(v, axis=-1)
    cosine = (u * v).sum(axis=-1) / np.maximum(nu * nv, 1e-12)
    return np.degrees(np.arccos(np.clip(cosine, -1, 1)))


def tangents(curve):
    """Start and end tangent of each master's segment, skipping zero handles."""
    start = curve[:, 1] - curve[:, 0]
    weak = np.linalg.norm(start, axis=-1) < 1e-6
    start[weak] = (curve[:, 2] - curve[:, 0])[weak]
    end = curve[:, 3] - curve[:, 2]
    weak = np.linalg.norm(end, axis=-1) < 1e-6
    end[weak] = (curve[:, 3] - curve[:, 1])[weak]
    return start, end


def node_protection(curves, kinds, slants, ref):
    """Keep corners in any master and nodes already sitting on an extreme."""
    segments = curves.shape[1]
    keep = []
    for j in range(segments):
        _, incoming = tangents(curves[:, (j - 1) % segments])
        outgoing, _ = tangents(curves[:, j])
        corner = bool((angle(incoming, outgoing) > CORNER_DEGREES).any())
        d_in = deslant(incoming[ref], slants[ref])
        d_out = deslant(outgoing[ref], slants[ref])
        on_axis = False
        for axis in (0, 1):
            tilt = [
                np.degrees(np.arctan2(abs(d[axis]), abs(d[1 - axis]) + 1e-12))
                for d in (d_in, d_out)
            ]
            if max(tilt) < AXIS_DEGREES:
                on_axis = True
        between_lines = kinds[(j - 1) % segments] == "line" and kinds[j] == "line"
        if between_lines:
            # A join that is straight in the reference but kinked in another
            # master is marker jitter: the line merge's own tolerance decides.
            corner = bool(angle(incoming[ref], outgoing[ref]) > COLINEAR_DEGREES)
        keep.append(corner or (on_axis and not between_lines))
    return keep


def unit(v):
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-9)


def segment_samples(curve):
    """Dense samples of one segment in every master, both ends included."""
    t = np.linspace(0, 1, SAMPLES + 1)[None, :, None]
    c = curve[:, None]
    return (
        (1 - t) ** 3 * c[:, :, 0]
        + 3 * (1 - t) ** 2 * t * c[:, :, 1]
        + 3 * (1 - t) * t * t * c[:, :, 2]
        + t**3 * c[:, :, 3]
    )


def fit_span(p, t0, t1, tolerance, ends=None):
    """One cubic per master through p's ends, keeping both end tangents.

    p holds the original outline's samples, shape (master, sample, xy). The
    fit refines the sample parameters by Newton steps, as polish_sources does.
    `ends` pins the cubic to nodes that have moved since sampling (a line
    stood upright by snap_axis), so a refit can't pull them back.
    """
    arcs = np.linalg.norm(np.diff(p, axis=1), axis=2)
    length = arcs.sum(axis=1)
    u = np.c_[np.zeros(len(p)), arcs.cumsum(axis=1)] / np.maximum(length[:, None], 1e-9)
    start, end = (p[:, 0], p[:, -1]) if ends is None else ends
    error = np.inf
    for _ in range(12):
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
            np.where(abs(det) > 1e-10, (x0 * c11 - x1 * c01) / safe, length / 3), 0.01, length
        )
        beta = np.clip(
            np.where(abs(det) > 1e-10, (x1 * c00 - x0 * c01) / safe, length / 3), 0.01, length
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


def axis_plan(start, end, slants):
    """Which axis a merged line should be stood on, and the nudge it costs.

    A line just off the axis in one upright master is stood on it in every
    upright master; otherwise the masters in between would interpolate
    through near-axis angles. The nudge counts against the merge tolerance,
    so a line clearly angled in some master stays split. Returns None when
    the line can't be stood up at all.
    """
    d = np.abs(end - start)
    upright = np.abs(slants) < 1e-9
    for axis in (0, 1):
        other = 1 - axis
        off = np.degrees(np.arctan2(d[:, axis], np.maximum(d[:, other], 1e-12)))
        near = upright & (off < NEAR_AXIS_DEGREES)
        slightly_off = near & (off > 1e-6)
        if not slightly_off.any():
            continue
        if (off[upright] > 45).any():
            return None
        return axis, np.where(upright, d[:, axis] / 2, 0.0)
    return None, np.zeros(len(start))


def on_axis(curves, kinds, k, slants, axis):
    """Is segment k a line standing exactly on `axis` in every upright master?"""
    if kinds[k] != "line":
        return False
    upright = np.abs(slants) < 1e-9
    return bool((np.abs(curves[upright, k, 0, axis] - curves[upright, k, 3, axis]) < 1e-6).all())


def snap_axis(curves, kinds, a, slants, axis):
    """Stand line `a` exactly upright (axis 0) or level (axis 1) in every
    upright master, carrying the neighbours' end nodes and adjacent handles so
    their tangents keep their direction.

    An end shared with a neighbour line already on the same axis stays put,
    so standing this line up can't tilt that one. With both ends free, each
    moves half the offset, to a whole unit the compile won't round apart."""
    n = len(kinds)
    if n < 3 or axis is None:
        return
    prev, nxt = (a - 1) % n, (a + 1) % n
    start_fixed = on_axis(curves, kinds, prev, slants, axis)
    end_fixed = on_axis(curves, kinds, nxt, slants, axis)
    for m in range(len(curves)):
        if abs(slants[m]) > 1e-9:
            continue
        start, end = curves[m, a, 0], curves[m, a, 3]
        if start_fixed and end_fixed:
            if abs(start[axis] - end[axis]) > 1e-6:
                continue
            mid = start[axis]
        elif start_fixed:
            mid = start[axis]
        elif end_fixed:
            mid = end[axis]
        else:
            mid = round((start[axis] + end[axis]) / 2)
        ds, de = mid - start[axis], mid - end[axis]
        curves[m, prev, 3, axis] += ds
        curves[m, prev, 2, axis] += ds
        curves[m, nxt, 0, axis] += de
        curves[m, nxt, 1, axis] += de
        curves[m, a, 0, axis] = mid
        curves[m, a, 3, axis] = mid
    for k in (prev, a, nxt):
        if kinds[k] == "line":
            c0, c3 = curves[:, k, 0], curves[:, k, 3]
            curves[:, k, 1] = c0 + (c3 - c0) / 3
            curves[:, k, 2] = c0 + 2 * (c3 - c0) / 3


def try_merge(a, b, kind_a, kind_b, samples, tolerance, slants, ref):
    """Merge two neighbours, measuring against the original outline samples."""
    start, end = a[:, 0], b[:, 3]
    direction = end - start
    if np.linalg.norm(direction, axis=-1).min() < 1e-6:
        return None
    if kind_a == "line" and kind_b == "line":
        offset = samples - start[:, None]
        cross = np.abs(direction[:, None, 0] * offset[..., 1] - direction[:, None, 1] * offset[..., 0])
        error = float((cross / np.linalg.norm(direction, axis=-1)[:, None]).max())
        # A line left just off vertical or horizontal gets stood up straight
        # afterwards (snap_axis); count that nudge against the tolerance too.
        plan = axis_plan(start, end, slants)
        if plan is not None:
            axis, nudge = plan
            error += float(nudge.max())
            if error <= tolerance:
                line = start[:, None] + np.linspace(0, 1, 4)[None, :, None] * direction[:, None]
                return line, ("line", axis), error
        # Too bent for one line in some master: one gentle curve keeps the
        # hand-drawn bend without a node in the middle.
    t0, _ = tangents(a)
    _, t1 = tangents(b)
    merged, error = fit_span(samples, unit(t0), unit(t1), tolerance, ends=(start, end))
    if merged is None:
        return None
    start_t, end_t = tangents(merged)
    if (angle(start_t, end_t) > MAX_TURN_DEGREES).any():
        return None
    if ((start_t * direction).sum(-1) <= 0).any() or ((end_t * direction).sum(-1) <= 0).any():
        return None
    if bulging_extremes(deslant(merged[ref], slants[ref])):
        return None
    return merged, "curve", float(error)


def straight_join(curves, kinds, a, b, ref):
    """A join between two lines that runs straight on in some master (the
    colinear pairs fontspector flags) and bends at most JOIN_BEND_DEGREES in the
    reference. Earlier merges can straighten a join that was protected as a
    corner, so this is judged on the current outline."""
    if kinds[a] != "line" or kinds[b] != "line":
        return False
    turn = angle(curves[:, a, 3] - curves[:, a, 0], curves[:, b, 3] - curves[:, b, 0])
    return bool(turn.min() < COLINEAR_DEGREES and turn[ref] <= JOIN_BEND_DEGREES)


def merge_pass(curves, kinds, protected, tolerance, slants, ref):
    curves = np.array(curves)
    kinds, protected = list(kinds), list(protected)
    originals = [segment_samples(curves[:, i]) for i in range(len(kinds))]
    cache, removed, worst = {}, 0, 0.0
    while len(kinds) > 3:
        best = None
        for j in range(len(kinds)):
            a, b = (j - 1) % len(kinds), j
            if protected[j] and not straight_join(curves, kinds, a, b, ref):
                continue
            key = (
                curves[:, a].tobytes(), curves[:, b].tobytes(), kinds[a], kinds[b],
                originals[a].shape[1], originals[b].shape[1],
            )
            if key not in cache:
                joined = np.concatenate([originals[a], originals[b][:, 1:]], axis=1)
                cache[key] = try_merge(
                    curves[:, a], curves[:, b], kinds[a], kinds[b], joined, tolerance, slants, ref
                )
            result = cache[key]
            if result is not None and (best is None or result[2] < best[1][2]):
                best = (j, result)
        if best is None:
            break
        j, (merged, kind, error) = best
        axis = None
        if isinstance(kind, tuple):
            kind, axis = kind
        a = (j - 1) % len(kinds)
        originals[a] = np.concatenate([originals[a], originals[j][:, 1:]], axis=1)
        curves[:, a] = merged
        kinds[a] = kind
        curves = np.delete(curves, j, axis=1)
        kinds.pop(j)
        protected.pop(j)
        originals.pop(j)
        if kind == "line":
            snap_axis(curves, kinds, a - 1 if j < a else a, slants, axis)
        removed += 1
        worst = max(worst, error)
    return curves, kinds, protected, removed, worst


def sample(curves, per_segment):
    t = np.linspace(0, 1, per_segment, endpoint=False)
    m, s = curves.shape[:2]
    out = np.empty((m, s * per_segment, 2))
    for i in range(s):
        c = curves[:, i]
        tt = t[None, :, None]
        out[:, i * per_segment:(i + 1) * per_segment] = (
            (1 - tt) ** 3 * c[:, None, 0]
            + 3 * (1 - tt) ** 2 * tt * c[:, None, 1]
            + 3 * (1 - tt) * tt * tt * c[:, None, 2]
            + tt**3 * c[:, None, 3]
        )
    return out


def neighbour_pairs(paths):
    """Master pairs that differ along exactly one axis by one step."""
    order = {"Light": 0, "Regular": 1, "Medium": 2, "Bold": 3}
    keys = []
    for p in paths:
        slant, weight, width, opsz = re.match(
            r"master-(Roman|Italic)-(\w+)-w(\d+)-o(\d+)\.ufo", p.name
        ).groups()
        keys.append((slant == "Italic", order[weight], [75, 100, 125].index(int(width)), int(opsz)))
    pairs = []
    for i, j in itertools.combinations(range(len(keys)), 2):
        diff = [x != y for x, y in zip(keys[i], keys[j])]
        if sum(diff) != 1:
            continue
        axis = diff.index(True)
        if axis in (1, 2) and abs(keys[i][axis] - keys[j][axis]) != 1:
            continue
        pairs.append((i, j))
    return pairs


def movement(before, after, pairs):
    """Largest distance from the old outline to the new one, all locations."""
    old = sample(before, 12)
    new = sample(after, 160)
    locations = [(i,) for i in range(len(before))] + pairs
    worst = 0.0
    for loc in locations:
        o = old[list(loc)].mean(axis=0)
        n = new[list(loc)].mean(axis=0)
        distance, _ = cKDTree(n).query(o)
        worst = max(worst, float(distance.max()))
    return worst


def point_count(curves, kinds):
    return sum(1 if k == "line" else 3 for k in kinds)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", type=Path)
    parser.add_argument("--tolerance", type=float, default=5.0)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    paths = sorted(args.sources.glob("master-*.ufo"))
    fonts = [Font.open(p) for p in paths]
    ref = next(i for i, p in enumerate(paths) if p.name == REFERENCE)
    slants = np.array([SLANT if "Italic" in p.name else 0.0 for p in paths])
    pairs = neighbour_pairs(paths)

    report, totals = {}, {"before": 0, "after": 0, "extremes_added": 0, "fallbacks": []}
    for name in fonts[0].keys():
        if not fonts[0][name].contours:
            continue
        glyph = {"before": 0, "after": 0, "extremes_added": 0, "merged": 0, "fit_error": 0.0}
        results, worst_move = [], 0.0
        for ci in range(len(fonts[0][name].contours)):
            source = [segment_curves(f[name].contours[ci]) for f in fonts]
            assert all(k == source[0][1] for _, k in source), (name, ci)
            curves = np.array([c for c, _ in source])
            kinds = list(source[0][1])
            glyph["before"] += point_count(curves, kinds)
            protected = node_protection(curves, kinds, slants, ref)
            split, split_kinds, split_protected, added = split_extremes(
                curves, kinds, protected, slants, ref, snap_tolerance=args.tolerance
            )
            merged, merged_kinds, merged_protected, removed, error = merge_pass(
                split, split_kinds, split_protected, args.tolerance, slants, ref
            )
            final, final_kinds, _, added_again = split_extremes(
                merged, merged_kinds, merged_protected, slants, ref, snap_tolerance=1.0
            )
            worst_move = max(worst_move, movement(curves, final, pairs))
            results.append((ci, split, split_kinds, final, final_kinds))
            glyph["extremes_added"] += added + added_again
            glyph["merged"] += removed
            glyph["fit_error"] = max(glyph["fit_error"], error)
        fallback = worst_move > args.tolerance + 1.5
        for ci, split, split_kinds, final, final_kinds in results:
            curves, kinds = (split, split_kinds) if fallback else (final, final_kinds)
            glyph["after"] += point_count(curves, kinds)
            if not args.dry_run:
                for font, c in zip(fonts, curves):
                    write_contour(font[name].contours[ci], c, kinds)
        glyph["largest_movement"] = round(worst_move, 2)
        glyph["fit_error"] = round(glyph["fit_error"], 2)
        glyph["fallback_extremes_only"] = fallback
        if fallback:
            totals["fallbacks"].append(name)
        report[name] = glyph
        totals["before"] += glyph["before"]
        totals["after"] += glyph["after"]
        totals["extremes_added"] += glyph["extremes_added"]

    if not args.dry_run:
        # Anchors, components and metrics stay as they were: the outlines
        # move at most the tolerance, so marks keep their 1.314 positions.
        for font, path in zip(fonts, paths):
            font.save(path, overwrite=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps({"tolerance_units": args.tolerance, "totals": totals, "glyphs": report}, indent=2) + "\n"
    )
    print(
        f"Reference-master points {totals['before']} -> {totals['after']}; "
        f"{totals['extremes_added']} extreme nodes added; "
        f"{len(totals['fallbacks'])} glyphs kept extremes only: {totals['fallbacks'][:20]}"
    )


if __name__ == "__main__":
    main()
