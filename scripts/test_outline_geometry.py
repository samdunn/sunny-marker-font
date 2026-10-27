"""Regression tests for source geometry, independent of font packaging.

Set SUNNY_MARKER_SOURCES to run the source checks on another folder of
masters, such as a candidate's extracted sources.zip.
"""

import os
import unittest
from pathlib import Path

import numpy as np

from fit_sources import fit_contour
from glyph_extensions import _bbox, _match_winding, _signed_area_contour, joined_stroke
from clean_polylines import round_cusps
from regularize_sources import redistribute


SOURCES = Path(
    os.environ.get("SUNNY_MARKER_SOURCES", Path(__file__).resolve().parents[1] / "sources")
)


class GeometryTests(unittest.TestCase):
    def test_intermediate_letter_joins_do_not_reverse_direction(self):
        import itertools
        from pathlib import Path
        from fontTools.designspaceLib import DesignSpaceDocument
        from fontTools.varLib.models import VariationModel, normalizeLocation
        from ufoLib2 import Font
        from round_source_joins import segment_curves

        doc = DesignSpaceDocument.fromfile(
            SOURCES / "SunnyMarker.designspace"
        )
        axes = {a.name: (a.minimum, a.default, a.maximum) for a in doc.axes}
        model = VariationModel(
            [normalizeLocation(source.location, axes) for source in doc.sources]
        )
        fonts = [Font.open(source.path) for source in doc.sources]
        for name in ("u", "w", "k"):
            masters = [segment_curves(font[name].contours[0])[0] for font in fonts]
            for values in itertools.product(
                (350, 550, 600), (87.5, 112.5), (14, 23), (0, -4.5, -9)
            ):
                curves = model.interpolateFromMasters(
                    normalizeLocation(dict(zip(axes, values)), axes), masters
                )
                incoming = np.roll(curves[:, 3] - curves[:, 2], 1, axis=0)
                outgoing = curves[:, 1] - curves[:, 0]
                cosine = (incoming * outgoing).sum(axis=1) / (
                    np.linalg.norm(incoming, axis=1) * np.linalg.norm(outgoing, axis=1)
                )
                angle = np.degrees(np.arccos(np.clip(cosine, -1, 1)))
                self.assertLess(float(angle.max()), 90, (name, values))

    def test_w_has_no_unintended_holes_across_source_masters(self):
        from outline_geometry import assert_w_structure
        from pathlib import Path
        from ufoLib2 import Font

        masters = sorted(SOURCES.glob("master-*.ufo"))
        self.assertEqual(len(masters), 48)
        for master in masters:
            font = Font.open(master)
            assert_w_structure(font)

    def test_mark_center_does_not_jump_with_stroke_sampling_density(self):
        from prepare_layout import top_center

        left = np.column_stack([np.linspace(0, 20, 100), np.full(100, 500)])
        right = np.column_stack([np.linspace(300, 320, 100), np.full(100, 500)])
        bottom = np.array([[0.0, 0], [320, 0]])
        self.assertEqual(
            top_center(np.concatenate([left, right[::10], right[-1:], bottom]), 0), 160
        )
        self.assertEqual(
            top_center(np.concatenate([left[::10], left[-1:], right, bottom]), 0), 160
        )

    def test_recentered_components_serialize_as_valid_ufo_numbers(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from ufoLib2 import Font
        from ufoLib2.objects import Anchor, Component
        from polish_sources import stabilize_top_anchors

        font = Font()
        base = font.newGlyph("w")
        pen = base.getPen()
        pen.moveTo((0, 0))
        pen.lineTo((300.0006, 0))
        pen.lineTo((300.0006, 500))
        pen.lineTo((0, 500))
        pen.closePath()
        base.anchors.append(Anchor(280, 534, name="top"))
        mark = font.newGlyph("acutecomb")
        mark.anchors.append(Anchor(0, 0, name="_top"))
        accented = font.newGlyph("wacute")
        accented.components.extend(
            [Component("w"), Component("acutecomb", (1, 0, 0, 1, 280, 534))]
        )
        accented.anchors.append(Anchor(280, 700, name="top"))
        stabilize_top_anchors(font, np.float64(0))
        self.assertEqual(accented.components[1].transformation.dx, 150)
        self.assertTrue(
            all(value == 0 for value in stabilize_top_anchors(font, 0).values())
        )
        self.assertEqual(accented.components[1].transformation.dx, 150)
        with TemporaryDirectory() as directory:
            path = Path(directory) / "test.ufo"
            font.save(path)
            reopened = Font.open(path)
            self.assertEqual(reopened["wacute"].components[1].transformation.dx, 150)

    def test_short_span_merge_preserves_curve_and_rejects_corner(self):
        from polish_sources import merge, evalcurve
        from round_source_joins import split
        from scipy.spatial import cKDTree

        curve = np.array([[0.0, 0], [20, 80], [80, 80], [100, 0]])
        a, b = split(curve, 0.025)
        merged, error = merge(a[None], b[None], tolerance=2)
        self.assertIsNotNone(merged)
        samples = np.linspace(0, 1, 2001)[None]
        original = evalcurve(curve[None], samples)[0]
        result = evalcurve(merged, samples)[0]
        self.assertLess(
            max(
                cKDTree(original).query(result)[0].max(),
                cKDTree(result).query(original)[0].max(),
            ),
            2.1,
        )
        np.testing.assert_allclose(merged[0, [0, 3]], curve[[0, 3]])
        a = np.array([[0.0, 0], [30, 0], [60, 0], [90, 0]])
        b = np.array([[90.0, 0], [90, 30], [90, 60], [90, 90]])
        self.assertIsNone(merge(a[None], b[None], tolerance=2)[0])

    def test_line_alignment_keeps_connected_runs_and_italic_shear(self):
        from polish_sources import snap_lines

        vertices = np.array([[0.0, 0], [1, 50], [2, 100], [80, 100], [80, 0]])
        curves = np.array(
            [
                a + np.linspace(0, 1, 4)[:, None] * (b - a)
                for a, b in zip(vertices, np.roll(vertices, -1, axis=0))
            ]
        )
        masters = np.stack([curves, curves.copy()])
        shear = np.tan(np.radians(9))
        masters[1, :, :, 0] += shear * masters[1, :, :, 1]
        result, count = snap_lines(masters, ["line"] * 5, np.array([0, shear]))
        self.assertGreater(count, 0)
        np.testing.assert_allclose(
            result[:, :, 3], np.roll(result[:, :, 0], -1, axis=1)
        )
        unsheared = result[1].copy()
        unsheared[:, :, 0] -= shear * unsheared[:, :, 1]
        np.testing.assert_allclose(unsheared, result[0], atol=1e-10)
        np.testing.assert_allclose(result[0, :2, [0, 3], 0], 1)
        self.assertLessEqual(np.linalg.norm(result - masters, axis=-1).max(), 1.1)

    def test_counter_opening_repairs_reversed_flanks_without_open_seam(self):
        from polish_sources import open_caps

        arc = np.array([[10.0, 20], [10, 5], [-10, 5], [-10, 20]])
        return_arc = np.array([[-10.0, 20], [-10, 45], [10, 45], [10, 20]])
        master = np.stack([arc, return_arc])
        collapsed = master.copy()
        collapsed[:, :, 0] *= -0.1
        result, count = open_caps(
            np.stack([master, collapsed]), ["curve"] * 2, np.zeros(2), 0
        )
        self.assertGreater(count, 0)
        self.assertGreaterEqual(result[1, 0, 0, 0] - result[1, 0, 3, 0], 6)
        np.testing.assert_allclose(
            result[:, :, 3], np.roll(result[:, :, 0], -1, axis=1)
        )
        np.testing.assert_allclose(result[0], master)

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
