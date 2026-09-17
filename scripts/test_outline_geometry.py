"""Regression tests for source geometry, independent of font packaging."""

import unittest

import numpy as np

from fit_sources import fit_contour
from glyph_extensions import _bbox, _match_winding, _signed_area_contour, joined_stroke
from clean_polylines import round_cusps
from regularize_sources import redistribute


class GeometryTests(unittest.TestCase):
    def test_final_fillet_preserves_compatible_segments(self):
        from round_source_joins import fillet_contours

        poly = np.array(
            [[0.0, 0], [50, 0], [51, 30], [52, 0], [100, 0], [100, 100], [0, 100]]
        )
        curves = np.array(
            [
                a + np.linspace(0, 1, 4)[:, None] * (b - a)
                for a, b in zip(poly, np.roll(poly, -1, axis=0))
            ]
        )
        result, targets = fillet_contours(np.stack([curves, curves * [1.25, 1]]))
        self.assertEqual(result.shape, (2, 8, 4, 2))
        self.assertEqual(np.flatnonzero(targets).tolist(), [2])
        np.testing.assert_allclose(
            result[:, :, 3], np.roll(result[:, :, 0], -1, axis=1)
        )
        # The rounded apex stays within the original needle's convex hull.
        self.assertLessEqual(result[:, :, :, 1].max(), 100)
        self.assertGreaterEqual(result[:, :, :, 1].min(), 0)

    def test_resampling_keeps_master_correspondence_and_extrema(self):
        square = np.array(
            [[0, 0], [1, 0], [80, 0], [100, 0], [100, 100], [0, 100]], float
        )
        masters = np.stack([square, square * [1.25, 0.8]])
        result = redistribute(masters, 0)
        self.assertEqual(result.shape[0], 2)
        np.testing.assert_allclose(result[1], result[0] * [1.25, 0.8])
        np.testing.assert_allclose(result.min(axis=1), masters.min(axis=1))
        np.testing.assert_allclose(result.max(axis=1), masters.max(axis=1))
        self.assertTrue(np.all(np.linalg.norm(np.diff(result, axis=1), axis=2) > 0))

    def test_cusp_rounding_is_bounded_and_leaves_ordinary_corners(self):
        square = np.array([[0, 0], [100, 0], [100, 100], [0, 100]], float)
        np.testing.assert_array_equal(round_cusps(square), square)
        needle = np.array(
            [[0, 0], [50, 0], [51, 30], [52, 0], [100, 0], [100, 100], [0, 100]], float
        )
        rounded = round_cusps(needle, maximum_shift=12, threshold=115, iterations=64)
        self.assertEqual(rounded.shape, needle.shape)
        self.assertLessEqual(np.linalg.norm(rounded - needle, axis=1).max(), 12.00001)
        self.assertLess(rounded[2, 1], needle[2, 1])

    def test_ring_counter_stays_inside_every_master(self):
        from ufoLib2 import Font
        from prepare_layout import draw_ring
        from fontTools.pens.areaPen import AreaPen

        for weight in (300, 400, 500, 700):
            for width in (0.75, 1, 1.25):
                for shear in (0, np.tan(np.radians(9))):
                    font = Font()
                    font.info.openTypeOS2WeightClass = weight
                    glyph = font.newGlyph("ringcomb")
                    pen = glyph.getPen()
                    pen.moveTo((-76, 0))
                    pen.lineTo((76, 0))
                    pen.lineTo((76, 152))
                    pen.lineTo((-76, 152))
                    pen.closePath()
                    draw_ring(font, "ringcomb", shear, width, 0)
                    outer, inner = glyph.contours
                    a, b = outer.getBounds(), inner.getBounds()
                    self.assertTrue(
                        a[0] < b[0] < b[2] < a[2] and a[1] < b[1] < b[3] < a[3]
                    )
                    for contour, sign in ((outer, 1), (inner, -1)):
                        area = AreaPen(None)
                        contour.draw(area)
                        self.assertGreater(area.value * sign, 0)

    def test_ink_bounds_exclude_control_handles(self):
        arch = [[("move", (0, 0)), ("curve", (0, 100), (100, 100), (100, 0))]]
        self.assertEqual(_bbox(arch), (0, 0, 100, 75))

    def test_reversing_winding_preserves_curves_and_ink(self):
        arch = [[("move", (0, 0)), ("curve", (0, 100), (100, 100), (100, 0))]]
        triangle = [[("move", (0, 0)), ("line", (100, 0)), ("line", (50, 100))]]
        reversed_arch = _match_winding(arch, triangle)
        self.assertEqual(_bbox(reversed_arch), _bbox(arch))
        self.assertEqual(sum(s[0] == "curve" for s in reversed_arch[0]), 1)
        self.assertGreater(_signed_area_contour(reversed_arch[0]), 0)
        # Reversing twice recovers the exact original curve, not its handle polygon.
        self.assertEqual(_match_winding(reversed_arch, arch), arch)

    def test_shared_fit_preserves_corners_and_reduces_round_contours(self):
        t = np.linspace(0, 2 * np.pi, 160, endpoint=False)
        circle = np.column_stack([100 * np.cos(t), 100 * np.sin(t)])
        masters = np.stack([circle, circle * [1.25, 0.8]])
        _, segments, error = fit_contour(masters)
        self.assertLess(sum(3 if s[2] == "curve" else 1 for s in segments), 40)
        self.assertLessEqual(error, 2)
        square = np.array([[0, 0], [100, 0], [100, 100], [0, 100]], float)
        _, segments, error = fit_contour(np.stack([square, square * 2]))
        self.assertEqual([s[2] for s in segments], ["line"] * 4)
        self.assertEqual(error, 0)

    def test_caron_has_one_clean_joined_outline(self):
        import pathops
        from build_font import _flatten

        contours = joined_stroke([(-105, 130), (0, 0), (105, 130)], 90)
        self.assertEqual(len(contours), 1)
        # Boolean normalization must not discover small extra loops at the join.
        path = pathops.Path()
        poly = _flatten(contours[0], steps=24)
        path.moveTo(*poly[0])
        for point in poly[1:]:
            path.lineTo(*point)
        path.close()
        normalized = pathops.simplify(path)
        self.assertEqual(sum(v == pathops.PathVerb.MOVE for v, p in normalized), 1)

    def test_curve_cannot_bow_between_sparse_source_vertices(self):
        from scipy.spatial import cKDTree

        t = np.linspace(0, 2 * np.pi, 12, endpoint=False)
        poly = np.column_stack([200 * np.cos(t), 200 * np.sin(t)])
        dense = np.concatenate(
            [
                a + (b - a) * np.linspace(0, 1, 250)[:, None]
                for a, b in zip(poly, np.roll(poly, -1, axis=0))
            ]
        )
        points, segments, _ = fit_contour(poly[None])
        for start, end, kind, controls in segments:
            a = points[0, start]
            u = np.linspace(0, 1, 250)[:, None]
            if kind == "line":
                curve = a + (controls[0] - a) * u
            else:
                b, c, d = controls[0]
                curve = (
                    (1 - u) ** 3 * a
                    + 3 * (1 - u) ** 2 * u * b
                    + 3 * (1 - u) * u * u * c
                    + u**3 * d
                )
            self.assertLessEqual(cKDTree(dense).query(curve)[0].max(), 2.1)


if __name__ == "__main__":
    unittest.main()
