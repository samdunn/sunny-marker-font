"""Remove local offset folds while preserving correspondence between masters."""

import numpy as np


def clean_polyline(poly):
    """Unfold small self-intersections without dropping or reordering vertices.

    Offset curves can fold where a tight concave corner closes. Redistribute
    the affected samples along the surviving flanks, as a proper stroke union
    would, rather than fitting a cubic through the fold. Large intersections
    are left for an explicit design repair.
    """
    p = poly.copy()
    n = len(p)
    for iteration in range(12):
        a = p
        r = np.roll(p, -1, axis=0) - p
        den = r[:, None, 0] * r[None, :, 1] - r[:, None, 1] * r[None, :, 0]
        q = p[None] - p[:, None]
        safe = np.where(abs(den) > 1e-9, den, 1)
        t = (q[:, :, 0] * r[None, :, 1] - q[:, :, 1] * r[None, :, 0]) / safe
        u = (q[:, :, 0] * r[:, None, 1] - q[:, :, 1] * r[:, None, 0]) / safe
        valid = (
            (abs(den) > 1e-9)
            & (t > 1e-6)
            & (t < 1 - 1e-6)
            & (u > 1e-6)
            & (u < 1 - 1e-6)
        )
        ii, jj = np.where(np.triu(valid, 2))
        repaired = False
        for i, j in zip(ii, jj):
            span = list(range(i + 1, j + 1))
            if len(span) > n / 2:
                i, j = j, i
                span = list(range(i + 1, n)) + list(range(0, j + 1))
            if not span or len(span) > n * 0.2:
                continue
            cross = p[i] + t[i, j] * r[i]
            if np.max(np.linalg.norm(p[span] - cross, axis=1)) > 18:
                continue
            # Put the apex at the closest original sample, and distribute the
            # remaining samples monotonically along each surviving flank.
            cut = int(np.argmin(np.linalg.norm(p[span] - cross, axis=1)))
            left, right = span[: cut + 1], span[cut + 1 :]
            pa, pb = p[i].copy(), p[(j + 1) % n].copy()
            for k, index in enumerate(left, 1):
                p[index] = pa + (cross - pa) * k / len(left)
            for k, index in enumerate(right, 1):
                p[index] = cross + (pb - cross) * k / (len(right) + 1)
            repaired = True
            break
        if not repaired:
            break
    return p


def round_cusps(poly, maximum_shift=8, threshold=145, iterations=12):
    """Soften sub-nib needles, leaving ordinary corners and ink texture alone."""
    p = poly.copy()
    for _ in range(iterations):
        incoming = p - np.roll(p, 1, axis=0)
        outgoing = np.roll(p, -1, axis=0) - p
        denominator = np.linalg.norm(incoming, axis=1) * np.linalg.norm(
            outgoing, axis=1
        )
        cosine = (incoming * outgoing).sum(axis=1) / np.maximum(denominator, 1e-9)
        needle = (cosine < np.cos(np.radians(threshold))) & (denominator > 1e-8)
        if not needle.any():
            break
        weight = 0.5 * needle + 0.12 * (np.roll(needle, 1) + np.roll(needle, -1))
        p += weight[:, None] * (
            (np.roll(p, 1, axis=0) + np.roll(p, -1, axis=0)) / 2 - p
        )
        delta = p - poly
        distance = np.linalg.norm(delta, axis=1)
        p = (
            poly
            + delta * np.minimum(1, maximum_shift / np.maximum(distance, 1e-9))[:, None]
        )
    return p
