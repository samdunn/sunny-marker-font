#!/usr/bin/env python3
"""Package the four-axis family, matching static instances, and web assets.

All published formats come from the same VF outlines and spacing. Historical
per-weight raster traces remain in build/ as design references only.
"""
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import zipfile

from fontTools.fontBuilder import FontBuilder
from fontTools.otlLib.builder import buildStatTable
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables.ttProgram import Program
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'build'
FDIR = ROOT / 'fonts'
VERSION = '1.313'
os.environ.setdefault('SOURCE_DATE_EPOCH', '1788998400')
COPYRIGHT = ('Copyright 2026 The Sunny Marker Project Authors '
             '(https://github.com/buildinternet/sunny-marker-font)')
OFL_URL = 'https://openfontlicense.org'
OFL_NOTICE = ('This Font Software is licensed under the SIL Open Font License, '
              'Version 1.1. This license is available with a FAQ at: ' + OFL_URL)
WEIGHTS = [('Light', 300), ('Regular', 400), ('Medium', 500),
           ('SemiBold', 600), ('Bold', 700)]
WIDTHS = [('Condensed', 75, 3), ('', 100, 5), ('Extended', 125, 7)]


def set_name(font, string, nid):
    font['name'].removeNames(nameID=nid)
    for pid, eid, lid in ((3, 1, 0x409),):
        font['name'].setName(string, nid, pid, eid, lid)


def apply_metadata(font):
    os2 = font['OS/2']
    os2.version = max(os2.version, 4)
    os2.fsType = 0
    os2.achVendID = 'NONE'
    os2.fsSelection |= 0x80
    os2.ulCodePageRange1 = 1
    os2.ulCodePageRange2 = 0
    # Shared metrics cover all masters and keep width/style switches stable.
    font['hhea'].ascent = os2.sTypoAscender = 960
    font['hhea'].descent = os2.sTypoDescender = -340
    font['hhea'].lineGap = os2.sTypoLineGap = 0
    os2.usWinAscent, os2.usWinDescent = 960, 340
    font['head'].fontRevision = float(VERSION)
    for nid, value in ((0, COPYRIGHT), (5, 'Version ' + VERSION),
                       (13, OFL_NOTICE), (14, OFL_URL)):
        set_name(font, value, nid)
    set_name(font, f"{VERSION};NONE;{font['name'].getDebugName(6)}", 3)
    meta = newTable('meta')
    meta.data = {'dlng': 'Latn', 'slng': 'Latn'}
    font['meta'] = meta
    font['name'].names = [record for record in font['name'].names if record.platformID != 1]
    if 'glyf' in font:
        gasp = newTable('gasp')
        gasp.version, gasp.gaspRange = 1, {0xFFFF: 15}
        font['gasp'] = gasp
        prep = newTable('prep')
        prep.program = Program()
        prep.program.fromBytecode(b'\xb8\x01\xff\x85\xb0\x04\x8d')
        font['prep'] = prep


def build_stat(font):
    buildStatTable(font, [
        {'tag': 'opsz', 'name': 'Optical size', 'ordering': 0,
         'values': [{'value': 14, 'name': '14pt', 'flags': 2}]},
        {'tag': 'wdth', 'name': 'Width', 'ordering': 1,
         'values': [{'value': 75, 'name': 'Condensed'},
                    {'value': 100, 'name': 'Normal', 'flags': 2},
                    {'value': 125, 'name': 'Expanded'}]},
        {'tag': 'wght', 'name': 'Weight', 'ordering': 2,
         'values': [dict(value=w, name=s, **({'flags': 2, 'linkedValue': 700}
                                           if w == 400 else {})) for s, w in WEIGHTS]},
        {'tag': 'slnt', 'name': 'Slant', 'ordering': 3,
         'values': [{'value': 0, 'name': 'Default', 'flags': 2}]},
    ], macNames=False)


def build_static_stat(font):
    """Describe the actual static face, including its italic style link."""
    weight = font['OS/2'].usWeightClass
    width_class = font['OS/2'].usWidthClass
    width, width_name = {3: (75, 'Condensed'), 5: (100, 'Normal'), 7: (125, 'Expanded')}[width_class]
    italic = bool(font['OS/2'].fsSelection & 1)
    weight_name = dict((value, name) for name, value in WEIGHTS)[weight]
    buildStatTable(font, [
        {'tag': 'opsz', 'name': 'Optical size', 'values': [{'value': 36, 'name': '36pt', 'flags': 2}]},
        {'tag': 'wdth', 'name': 'Width', 'values': [{'value': width, 'name': width_name, 'flags': 2 if width == 100 else 0}]},
        {'tag': 'wght', 'name': 'Weight', 'values': [{'value': weight, 'name': weight_name, 'flags': 2 if weight == 400 else 0}]},
        {'tag': 'ital', 'name': 'Italic', 'values': [{'value': int(italic), 'name': 'Italic' if italic else 'Roman', 'flags': 0 if italic else 2, **({} if italic else {'linkedValue': 1})}]},
    ], macNames=False)


def save_woff2(font, path):
    font.flavor = 'woff2'
    font.save(path)
    font.flavor = None


def save_otf(font, path):
    """CFF courtesy export of the *same* outlines, no independent tracing."""
    glyph_set = font.getGlyphSet()
    charstrings = {}
    for name in font.getGlyphOrder():
        pen = T2CharStringPen(font['hmtx'][name][0], glyph_set)
        glyph_set[name].draw(pen)
        charstrings[name] = pen.getCharString()
    for tag in ('glyf', 'loca', 'gasp', 'prep', 'fpgm', 'cvt ', 'maxp'):
        if tag in font:
            del font[tag]
    font.sfntVersion = 'OTTO'
    font['post'].formatType = 3.0
    fb = FontBuilder(font=font, isTTF=False)
    fb.setupCFF(font['name'].getDebugName(6), {
        'FullName': font['name'].getDebugName(4), 'FamilyName': 'Sunny Marker',
        'Weight': font['name'].getDebugName(17) or font['name'].getDebugName(2),
        'version': VERSION, 'Notice': COPYRIGHT, 'ItalicAngle': font['post'].italicAngle,
    }, charstrings, {})
    fb.setupMaxp()
    fb.save(path)


def package_family():
    vf = TTFont(BUILD / 'SunnyMarkerVariable.ttf')
    # Rebase the optical default without changing the 10-36 design range.
    vf = instantiateVariableFont(vf, {'opsz': (10, 14, 36)}, inplace=True)
    vf['fvar'].instances = [i for i in vf['fvar'].instances if i.coordinates['wdth'] == 100]
    for instance in vf['fvar'].instances:
        instance.coordinates['opsz'] = 14
    if 'avar' not in vf:
        avar = newTable('avar')
        avar.segments = {a.axisTag: {-1.0: -1.0, 0.0: 0.0, 1.0: 1.0} for a in vf['fvar'].axes}
        vf['avar'] = avar
    sub = 'Regular'
    for nid, value in ((1, 'Sunny Marker'), (2, sub), (4, f'Sunny Marker {sub}'),
                       (6, f'SunnyMarker-{sub}'),
                       (25, 'SunnyMarker')):
        set_name(vf, value, nid)
    for nid in (16, 17):
        vf['name'].removeNames(nameID=nid)
    vf['OS/2'].fsSelection = 0xC0
    vf['head'].macStyle = 0
    vf['post'].italicAngle = 0
    apply_metadata(vf)
    build_stat(vf)
    stem = 'SunnyMarker[opsz,slnt,wdth,wght]'
    vf.save(FDIR / 'variable' / (stem + '.ttf'))
    save_woff2(vf, FDIR / 'webfonts' / 'SunnyMarker-Variable.woff2')
    for italic in (False, True):
        # Pin the shared dimensions once per style before making 15 exports.
        style_vf = instantiateVariableFont(vf, {'opsz': 36, 'slnt': -9 if italic else 0}, optimize=False)
        for width_name, wdth, width_class in WIDTHS:
            for style, wght in WEIGHTS:
                font = instantiateVariableFont(style_vf, {'wght': wght, 'wdth': wdth})
                if 'STAT' in font:
                    del font['STAT']
                font['name'].removeNames(nameID=25)
                weight_style = ('Italic' if style == 'Regular' else style + ' Italic') if italic else style
                full = ' '.join(filter(None, (width_name, weight_style)))
                base_family = ' '.join(filter(None, ('Sunny Marker', width_name)))
                ribbi = style in ('Regular', 'Bold')
                legacy_family = base_family if ribbi else f'{base_family} {style}'
                legacy_style = weight_style if ribbi else ('Italic' if italic else 'Regular')
                for nid, value in ((1, legacy_family), (2, legacy_style),
                                   (4, 'Sunny Marker ' + full),
                                   (6, 'SunnyMarker-' + full.replace(' ', '')),
                                   (16, 'Sunny Marker'), (17, full)):
                    set_name(font, value, nid)
                font['OS/2'].usWeightClass = wght
                font['OS/2'].usWidthClass = width_class
                bold = wght == 700
                font['OS/2'].fsSelection = 0x80 | (1 if italic else 0) | (0x20 if bold else 0)
                if not italic and not bold:
                    font['OS/2'].fsSelection |= 0x40
                font['head'].macStyle = (1 if bold else 0) | (2 if italic else 0)
                font['post'].italicAngle = -9 if italic else 0
                font['hhea'].caretSlopeRise = 1000 if italic else 1
                font['hhea'].caretSlopeRun = 158 if italic else 0
                apply_metadata(font)
                build_static_stat(font)
                basename = 'SunnyMarker-' + full.replace(' ', '')
                font.save(FDIR / 'ttf' / (basename + '.ttf'))
                save_woff2(font, FDIR / 'webfonts' / (basename + '.woff2'))
                save_otf(font, FDIR / 'otf' / (basename + '.otf'))
    print('Packaged', sub, flush=True)


def package_web():
    web = ROOT / 'web'
    web.mkdir(exist_ok=True)
    index = web / 'index.html'
    if index.exists():
        index.write_text(re.sub(r'SunnyMarker-(Static-OTF-)?\d+\.\d+\.zip',
            lambda m: 'SunnyMarker-' + (m.group(1) or '') + VERSION + '.zip', index.read_text()))
    css = [f'''/* Sunny Marker {VERSION} — SIL OFL 1.1. Keep beside webfonts/. */
@font-face {{
  font-family: "Sunny Marker";
  src: url("./webfonts/SunnyMarker-Variable.woff2") format("woff2");
  font-weight: 300 700;
  font-stretch: 75% 125%;
  font-style: oblique 0deg 9deg;
  font-display: swap;
}}''']
    static_css = ['/* Optional static fallback: use family "Sunny Marker Static". */']
    for italic in (False, True):
        style = 'italic' if italic else 'normal'
        for width_name, wdth, _ in WIDTHS:
            for name, weight in WEIGHTS:
                weight_style = ('Italic' if name == 'Regular' else name + ' Italic') if italic else name
                full = ' '.join(filter(None, (width_name, weight_style))).replace(' ', '')
                static_css.append(f'''@font-face {{
  font-family: "Sunny Marker Static";
  src: url("./webfonts/SunnyMarker-{full}.woff2") format("woff2");
  font-weight: {weight};
  font-stretch: {wdth}%;
  font-style: {style};
  font-display: swap;
}}''')
    (web / 'sunny-marker.css').write_text('\n\n'.join(css) + '\n')
    (web / 'sunny-marker-static.css').write_text('\n\n'.join(static_css) + '\n')
    # The web folder is a standalone, copyable deployment unit.
    for stale in (web / 'webfonts').glob('SunnyMarker*.woff2'):
        stale.unlink()
    shutil.copytree(FDIR / 'webfonts', web / 'webfonts', dirs_exist_ok=True)
    shutil.copy2(ROOT / 'OFL.txt', web / 'OFL.txt')
    downloads = web / 'downloads'
    downloads.mkdir(exist_ok=True)
    for stale in downloads.glob('SunnyMarker-*.zip'):
        stale.unlink()
    with zipfile.ZipFile(downloads / f'SunnyMarker-{VERSION}.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        paths = [*sorted((FDIR / 'variable').glob('*.ttf')),
                 FDIR / 'webfonts/SunnyMarker-Variable.woff2', ROOT / 'OFL.txt']
        for path in paths:
            info = zipfile.ZipInfo(path.name, (2026, 9, 15, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    with zipfile.ZipFile(downloads / f'SunnyMarker-Static-OTF-{VERSION}.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in [*sorted((FDIR / 'otf').glob('*.otf')), ROOT / 'OFL.txt']:
            info = zipfile.ZipInfo(path.name, (2026, 9, 15, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    files = sorted(p for p in FDIR.rglob('*') if p.suffix in ('.ttf', '.otf', '.woff2'))
    manifest = {'version': VERSION,
                'axes': {'wght': [300, 400, 700], 'wdth': [75, 100, 125], 'opsz': [10, 14, 36], 'slnt': [-9, 0, 0]},
                'files': [{'path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size,
                           'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
    (ROOT / 'fonts' / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    release = ROOT / 'release'
    release.mkdir(exist_ok=True)
    with zipfile.ZipFile(release / f'sunny-marker-web-{VERSION}.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for path in sorted(p for p in web.rglob('*') if p.is_file()):
            entry = zipfile.ZipInfo('sunny-marker-web/' + str(path.relative_to(web)),
                                    date_time=(2026, 9, 10, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            z.writestr(entry, path.read_bytes())
    print(f'Packaged web/ and release/sunny-marker-web-{VERSION}.zip')


def main():
    for directory, pattern in [('variable', '*.ttf'), ('ttf', '*.ttf'),
                               ('otf', '*.otf'), ('webfonts', '*.woff2')]:
        out = FDIR / directory
        out.mkdir(parents=True, exist_ok=True)
        # Replace only this project's generated font artifacts, never sources.
        for path in out.glob('SunnyMarker' + pattern):
            path.unlink()
    manifest = FDIR / 'manifest.json'
    if manifest.exists():
        manifest.unlink()
    package_family()
    from glyph_atlas import main as glyph_atlas
    glyph_atlas()
    package_web()


if __name__ == '__main__':
    main()
