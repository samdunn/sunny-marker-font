"""Regression tests for source geometry, independent of font packaging."""
import unittest

import numpy as np

from fit_sources import fit_contour
from glyph_extensions import _bbox, _match_winding, _signed_area_contour, joined_stroke


class GeometryTests(unittest.TestCase):
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
        t = np.linspace(0, 2*np.pi, 160, endpoint=False)
        circle = np.column_stack([100*np.cos(t), 100*np.sin(t)])
        masters = np.stack([circle, circle * [1.25, 0.8]])
        _, segments, error = fit_contour(masters)
        self.assertLess(sum(3 if s[2] == "curve" else 1 for s in segments), 40)
        self.assertLessEqual(error, 2)
        square = np.array([[0, 0], [100, 0], [100, 100], [0, 100]], float)
        _, segments, error = fit_contour(np.stack([square, square*2]))
        self.assertEqual([s[2] for s in segments], ["line"]*4)
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
        t = np.linspace(0, 2*np.pi, 12, endpoint=False)
        poly = np.column_stack([200*np.cos(t), 200*np.sin(t)])
        dense = np.concatenate([a+(b-a)*np.linspace(0, 1, 250)[:, None]
                                for a, b in zip(poly, np.roll(poly, -1, axis=0))])
        points, segments, _ = fit_contour(poly[None])
        for start, end, kind, controls in segments:
            a = points[0, start]
            u = np.linspace(0, 1, 250)[:, None]
            if kind == "line":
                curve = a+(controls[0]-a)*u
            else:
                b, c, d = controls[0]
                curve = (1-u)**3*a+3*(1-u)**2*u*b+3*(1-u)*u*u*c+u**3*d
            self.assertLessEqual(cKDTree(dense).query(curve)[0].max(), 2.1)


if __name__ == "__main__":
    unittest.main()
