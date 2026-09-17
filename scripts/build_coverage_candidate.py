"""Rebuild the 1.314 review snapshot without replacing stable release assets."""

import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

from fontTools import subset
from fontTools.ttLib import TTFont, newTable
from fontTools.varLib.instancer import instantiateVariableFont

import package_gf
from submission_font import prepare_submission_font

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "candidates/1.314"
OUT = ROOT / "build/coverage-candidate-1.314"
FILENAME = "SunnyMarker[opsz,slnt,wdth,wght].ttf"


def compress_variations(font):
    """Apply FontTools' standard IUP delta compression and rounding tolerance."""
    for name in font.getGlyphOrder():
        coordinates, controls = font["glyf"]._getCoordinatesAndControls(
            name, font["hmtx"].metrics
        )
        for variation in font["gvar"].variations.get(name, []):
            variation.optimize(
                coordinates,
                controls.endPts,
                isComposite=controls.numberOfContours < 0,
            )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources-only", action="store_true")
    args = parser.parse_args()
    os.environ.setdefault("SOURCE_DATE_EPOCH", "1788998400")
    OUT.mkdir(parents=True, exist_ok=True)
    archive = SNAPSHOT / "sources.zip"
    expected = (SNAPSHOT / "SHA256SUMS").read_text().splitlines()
    expected = dict(line.split("  ", 1)[::-1] for line in expected)
    if hashlib.sha256(archive.read_bytes()).hexdigest() != expected["sources.zip"]:
        raise ValueError("Source snapshot checksum mismatch")
    with zipfile.ZipFile(archive) as zipped:
        for entry in zipped.infolist():
            target = (OUT / entry.filename).resolve()
            if not target.is_relative_to(OUT.resolve() / "sources"):
                raise ValueError("Unexpected path in source snapshot")
        zipped.extractall(OUT)
    if args.sources_only:
        print(OUT / "sources")
        return
    raw = OUT / "SunnyMarkerVariable.ttf"
    subprocess.run(
        [sys.executable, "-m", "fontmake", "-m",
         str(OUT / "sources/SunnyMarker.designspace"), "-o", "variable",
         "--output-path", str(raw), "--no-production-names",
         "--keep-overlaps", "--no-autohint"],
        cwd=ROOT, check=True, timeout=900,
    )
    font = instantiateVariableFont(
        TTFont(raw, recalcTimestamp=False), {"opsz": (10, 14, 36)},
        inplace=True, optimize=False,
    )
    font["fvar"].instances = [
        i for i in font["fvar"].instances if i.coordinates["wdth"] == 100
    ]
    for instance in font["fvar"].instances:
        instance.coordinates["opsz"] = 14
    for name_id, value in (
        (1, "Sunny Marker"), (2, "Regular"), (4, "Sunny Marker Regular"),
        (6, "SunnyMarker-Regular"), (25, "SunnyMarker"),
    ):
        package_gf.set_name(font, value, name_id)
    for name_id in (16, 17):
        font["name"].removeNames(nameID=name_id)
    font["OS/2"].fsSelection = 0xC0
    font["head"].macStyle = 0
    font["post"].italicAngle = 0
    package_gf.VERSION = "1.314"
    package_gf.apply_metadata(font)
    font["meta"].data = {"dlng": "Latn, Goth", "slng": "Latn, Goth"}
    package_gf.build_stat(font)
    if "avar" not in font:
        font["avar"] = newTable("avar")
        font["avar"].segments = {
            a.axisTag: {-1.0: -1.0, 0.0: 0.0, 1.0: 1.0}
            for a in font["fvar"].axes
        }
    # FontTools removes empty records while instancing; its subsetter expects
    # every retained glyph to have a key, including constant composites.
    for name in font.getGlyphOrder():
        font["gvar"].variations.setdefault(name, [])
    options = subset.Options()
    options.name_IDs = ["*"]
    options.name_languages = ["*"]
    options.name_legacy = True
    options.layout_features = ["*"]
    options.notdef_outline = True
    options.recommended_glyphs = True
    options.glyph_names = True
    selection = subset.Subsetter(options=options)
    selection.populate(unicodes=set(font.getBestCmap()) - {0x1EBC, 0x1EBD})
    metadata = font["meta"]
    selection.subset(font)
    font["meta"] = metadata
    compress_variations(font)
    font.save(OUT / FILENAME)
    font.flavor = "woff2"
    font.save(OUT / "SunnyMarker-Variable.woff2")
    shutil.copytree(SNAPSHOT / "googlefonts", OUT / "googlefonts", dirs_exist_ok=True)
    for italic in (False, True):
        destination = OUT / "googlefonts/ofl/sunnymarker" / (
            "SunnyMarker" + ("-Italic" if italic else "") + "[opsz,wdth,wght].ttf"
        )
        prepare_submission_font(
            OUT / FILENAME, destination, italic=italic, version="1.314", optimize=False,
        )
        style = TTFont(destination, recalcTimestamp=False)
        compress_variations(style)
        style.save(destination)
    print(f"Built {len(font.getGlyphOrder())} glyphs / {len(font.getBestCmap())} characters")
    print(OUT)


if __name__ == "__main__":
    main()
