#!/usr/bin/env python3
"""Functional checks of shipped fonts, independent of the outline generator."""
import hashlib
import io
import itertools
import json
from pathlib import Path
import zipfile

from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPointPen
from package_gf import VERSION
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from scipy.spatial import cKDTree
from outline_geometry import boundary, contours
import numpy as np
import uharfbuzz as hb

ROOT = Path(__file__).resolve().parents[1]
AXES = {'wght': (300, 400, 700), 'wdth': (75, 100, 125), 'opsz': (10, 14, 36), 'slnt': (-9, 0, 0)}
TEXT = 'Sunny day! Warm heads & cozy vibes 08'
GOOGLE_FONTS = {'SunnyMarker[opsz,wdth,wght].ttf', 'SunnyMarker-Italic[opsz,wdth,wght].ttf'}


def shaped(path, variations=None, text=TEXT, features=None):
    font = hb.Font(hb.Face(path.read_bytes()))
    if variations:
        font.set_variations(variations)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, features)
    assert all(g.codepoint for g in buf.glyph_infos), (path, text)
    return sum(p.x_advance for p in buf.glyph_positions), [g.codepoint for g in buf.glyph_infos]


def main():
    paths = sorted((ROOT / 'fonts').rglob('*'))
    fonts = [p for p in paths if p.suffix in ('.ttf', '.otf', '.woff2')]
    # Four-axis VF TTF + its WOFF2 + Google's upright/italic VFs + 30 x 3 statics.
    assert len(fonts) == 94, len(fonts)
    checks = 0
    for path in fonts:
        with TTFont(path) as f:
            assert abs(f['head'].fontRevision - float(VERSION)) < 1 / 65536
            assert f['OS/2'].fsType == 0
            assert f['name'].getDebugName(13).startswith('This Font Software')
            assert len(f.getGlyphOrder()) == 389
            assert f['hhea'].ascent == 960 and f['hhea'].descent == -340
            if 'fvar' in f and path.name in GOOGLE_FONTS:
                # The slant split is checked against the four-axis font by
                # verify_submission.py.
                assert {a.axisTag: (a.minValue, a.defaultValue, a.maxValue)
                        for a in f['fvar'].axes} == {k: v for k, v in AXES.items() if k != 'slnt'}
            elif 'fvar' in f:
                assert {a.axisTag: (a.minValue, a.defaultValue, a.maxValue)
                        for a in f['fvar'].axes} == AXES
                assert len(f['fvar'].instances) == 10
                static = instantiateVariableFont(f, {'wght': 300, 'wdth': 75, 'opsz': 10, 'slnt': 0})
                assert 'fvar' not in static
                assert static['OS/2'].sxHeight == 480
            else:
                assert f['OS/2'].usWidthClass in (3, 5, 7)
                for table in ('fvar', 'gvar', 'HVAR', 'MVAR'):
                    assert table not in f, (path, table)
            # WOFF2 must decompress successfully, with the same glyphs/tables.
            if path.suffix == '.woff2':
                f.flavor = None
                data = io.BytesIO()
                f.save(data)
                assert TTFont(io.BytesIO(data.getvalue())).getBestCmap() == f.getBestCmap()
        checks += 1
    measurements = []
    for path in [ROOT / 'fonts/variable/SunnyMarker[opsz,slnt,wdth,wght].ttf']:
        for weight, optical, slant in itertools.product((300, 350, 400, 550, 700), (10, 23, 36), (0, -2.25, -4.5, -6.75, -9)):
            widths = [shaped(path, {'wght': weight, 'wdth': width, 'opsz': optical, 'slnt': slant})[0]
                      for width in (75, 87.5, 100, 112.5, 125)]
            assert all(a < b for a, b in zip(widths, widths[1:])), widths
            measurements.append({'font': path.name, 'weight': weight, 'opsz': optical, 'slnt': slant,
                                 'advances_75_87_100_112_125': widths})
        for width in (75, 100, 125):
            assert shaped(path, {'wdth': width, 'opsz': 10})[0] > shaped(path, {'wdth': width, 'opsz': 36})[0]
        assert shaped(path, text='I')[1] != shaped(path, text='I', features={'ss01': True})[1]
        shaped(path, text='À bientôt Çiçek São Paulo Smörgås 0123456789 ← ↑ → ↓ ↖ ↗ ↘ ↙ ★ ✧ ♡ ☀ ✓ ✗')
        with TTFont(path) as f:
            for loc in itertools.product((300, 700), (75, 125), (10, 36), (0, -9)):
                instance = instantiateVariableFont(f, dict(zip(('wght', 'wdth', 'opsz', 'slnt'), loc)))
                for g in instance['glyf'].glyphs.values():
                    if g.numberOfContours > 0:
                        g.recalcBounds(instance['glyf'])
                        assert g.yMax <= 960 and g.yMin >= -340, (path, loc, g.yMin, g.yMax)
            for name in ('A', 'M', 'V', 'e', 'a', 'ccedilla', 'I.ss01'):
                assert f['gvar'].variations[name], name
        # Fixed-width exports must shape exactly like the corresponding VF instance.
        for italic in (False, True):
            for prefix, wdth in [('Condensed', 75), ('', 100), ('Extended', 125)]:
                for style, weight in [('Light', 300), ('Regular', 400), ('Medium', 500), ('SemiBold', 600), ('Bold', 700)]:
                    sub = ('Italic' if style == 'Regular' else style + 'Italic') if italic else style
                    static_path = ROOT / 'fonts/ttf' / f'SunnyMarker-{prefix}{sub}.ttf'
                    assert shaped(static_path)[0] == shaped(path, {'wght': weight, 'wdth': wdth, 'opsz': 36, 'slnt': -9 if italic else 0})[0]
                    if weight in (300, 400, 700):
                        # Regression: the Light cedilla used to split into flecks.
                        face = ImageFont.truetype(str(static_path), 240)
                        canvas = Image.new('L', (300, 400))
                        ImageDraw.Draw(canvas).text((90, 250), '\u00b8', font=face,
                                                   fill=255, anchor='ls')
                        _, components = ndimage.label(np.array(canvas) > 100)
                        assert components == 1, (static_path, 'cedilla components', components)
    verify_slant()
    manifest = json.loads((ROOT / 'fonts/manifest.json').read_text())
    for entry in manifest['files']:
        assert hashlib.sha256((ROOT / entry['path']).read_bytes()).hexdigest() == entry['sha256']
    with zipfile.ZipFile(ROOT / f'release/sunny-marker-web-{VERSION}.zip') as z:
        assert z.testzip() is None
        for path in (ROOT / 'web').rglob('*'):
            if path.is_file():
                assert z.read('sunny-marker-web/' + str(path.relative_to(ROOT / 'web'))) == path.read_bytes()
    report = {'passed': True, 'artifacts_checked': checks, 'sampled_variable_locations': 375,
              'width_measurements': measurements}
    (ROOT / 'documentation/verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'PASS: {checks} font artifacts; 375 variable locations; static/VF shaping parity; web ZIP + hashes.')


def verify_slant():
    """Prove all four axes coexist and intermediate slants retain the contours."""
    path = ROOT / 'fonts/variable/SunnyMarker[opsz,slnt,wdth,wght].ttf'
    font = TTFont(path)
    for slant in (0, -2.25, -4.5, -6.75, -9):
        face = instantiateVariableFont(font, dict(wght=400, wdth=100, opsz=14, slnt=slant))
        caret_angle = -np.degrees(np.arctan2(face['hhea'].caretSlopeRun, face['hhea'].caretSlopeRise))
        assert abs(caret_angle-slant) < .1, (slant, caret_angle)
    names = ('A', 'M', 'Y', 'e', 'copyright', 'registered', 'section', 'paragraph', 'trademark')
    def points(name, location):
        pen = RecordingPointPen()
        font.getGlyphSet(location=location)[name].drawPoints(pen)
        return np.array([args[0] for op, args, kwargs in pen.value if op == 'addPoint'])
    for weight, width, optical in itertools.product((300, 700), (75, 125), (10, 36)):
        location = {'wght': weight, 'wdth': width, 'opsz': optical}
        for name in names:
            upright = points(name, dict(location, slnt=0))
            slanted = points(name, dict(location, slnt=-9))
            assert upright.shape == slanted.shape
            assert np.ptp((slanted-upright)[:, 0]) > 30, (name, location)
            # Compare the ink after removing the nine-degree shear. Curve
            # handles may move more than the ink, unlike the old polyline nodes.
            # Allow 2u fitting per endpoint master + 2u optical relief + 1u
            # integer rounding. This stays below 0.14 pixels at 18px text size.
            upright_ink = boundary(font.getGlyphSet(location=dict(location, slnt=0)), name)
            slanted_ink = boundary(font.getGlyphSet(location=dict(location, slnt=-9)), name)
            slanted_ink[:, 0] -= np.tan(np.radians(9))*slanted_ink[:, 1]
            upright_ink[:, 0] -= upright_ink[:, 0].min()
            slanted_ink[:, 0] -= slanted_ink[:, 0].min()
            deviation = max(cKDTree(upright_ink).query(slanted_ink)[0].max(),
                            cKDTree(slanted_ink).query(upright_ink)[0].max())
            assert deviation <= 7, (name, location, deviation)
            for fraction in (.25, .5, .75):
                middle = points(name, dict(location, slnt=-9*fraction))
                expected = upright*(1-fraction) + slanted*fraction
                assert np.max(np.abs(middle-expected)) < 1.01, (name, location, fraction)
    print('PASS: continuous slant at width, weight and optical-size extremes.')


def verify_y_stems():
    """Measure shipped capital stems, independently of the source correction."""
    paths = sorted((ROOT / 'fonts/ttf').glob('*.ttf'))
    for path in paths:
        with TTFont(path) as f:
            for name in ('Y', 'Yacute', 'Ycircumflex', 'Ydieresis', 'Ygrave'):
                centers = []
                for y in (120, 260):
                    xs = []
                    for poly in contours(f.getGlyphSet(), name):
                        a, b = poly, np.roll(poly, -1, axis=0)
                        hit = (a[:, 1] > y) != (b[:, 1] > y)
                        aa, bb = a[hit], b[hit]
                        xs.extend(aa[:, 0] + (y-aa[:, 1]) *
                                  (bb[:, 0]-aa[:, 0]) / (bb[:, 1]-aa[:, 1]))
                    assert len(xs) == 2, (path, name, y, xs)
                    centers.append(float(np.mean(xs)))
                lean = (centers[1] - centers[0]) / 140
                # Remove italic shear and normalize for the width class.
                lean += np.tan(np.radians(f['post'].italicAngle))
                width = {3: 0.75, 5: 1, 7: 1.25}[f['OS/2'].usWidthClass]
                assert abs(lean / width) < 0.25, (path, name, lean / width)
    print(f'PASS: upright capital Y stems and accents in {len(paths)} static faces.')


def proof():
    (ROOT / 'proofs').mkdir(parents=True, exist_ok=True)
    img = Image.new('RGB', (1720, 1590), '#faf8f0')
    d = ImageDraw.Draw(img)
    label = ImageFont.load_default(size=19)
    title = ImageFont.load_default(size=30)
    d.text((40, 28), f'SUNNY MARKER / {VERSION} / VARIABLE WIDTH + SLANT', font=title, fill='#24251e')
    y = 88
    for italic in (False, True):
        path = ROOT / 'fonts/variable' / 'SunnyMarker[opsz,slnt,wdth,wght].ttf'
        for weight in (300, 400, 700):
            for wdth in (75, 100, 125):
                d.text((40, y), f'{"Italic" if italic else "Upright"} · {weight} · {wdth}%', font=label, fill='#8a4d29')
                f = ImageFont.truetype(str(path), 48)
                f.set_variation_by_axes([weight, wdth, 36, -9 if italic else 0])
                d.text((250, y - 13), TEXT + ' — Çç Şş', font=f, fill='#20221d')
                y += 70
            y += 8
    path = ROOT / 'fonts/variable/SunnyMarker[opsz,slnt,wdth,wght].ttf'
    f = ImageFont.truetype(str(path), 36)
    f.set_variation_by_axes([400, 100, 10, 0])
    d.text((40, y), 'À bientôt · São Paulo · Smörgås · 0123456789 · ← ↑ → ↓ ★ ♡ ☀ ✓ ✗', font=f, fill='#20221d')
    img.save(ROOT / 'proofs/variable-width-web.png')


if __name__ == '__main__':
    main()
    verify_y_stems()
    proof()
