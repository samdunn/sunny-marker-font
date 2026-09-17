"""Prepare a Google Fonts review package without submitting or publishing it."""

from pathlib import Path
import shutil
import subprocess
import sys
import zipfile
from gfmetadata import FamilyProto, text_format
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.otlLib.builder import buildStatTable

from package_gf import set_name
from PIL import Image, ImageDraw
from shaped_proof import draw_shaped

# Review exports from the current source build; published web/npm stays separate.
VERSION = "1.313"


def prepare_submission_font(source, destination, italic=False):
    font = TTFont(source, recalcTimestamp=False)
    font = instantiateVariableFont(font, {"slnt": -9 if italic else 0}, inplace=True)
    style = "Italic" if italic else "Regular"
    for nid, value in (
        (1, "Sunny Marker"),
        (2, style),
        (4, "Sunny Marker " + style),
        (6, "SunnyMarker-" + style),
        (25, "SunnyMarkerItalic" if italic else "SunnyMarker"),
    ):
        set_name(font, value, nid)
    font["OS/2"].fsSelection = 0x180 | (1 if italic else 0x40)
    font["head"].macStyle = 2 if italic else 0
    font["post"].italicAngle = -9 if italic else 0
    font["hhea"].caretSlopeRise = 1000 if italic else 1
    font["hhea"].caretSlopeRun = 158 if italic else 0
    for name_id, value in (
        (9, "Sam Dunn"),
        (12, "https://samdunn.org"),
        (5, "Version " + VERSION),
        (3, f"{VERSION};NONE;{font['name'].getDebugName(6)}"),
    ):
        set_name(font, value, name_id)
    font["head"].fontRevision = float(VERSION)
    for instance in font["fvar"].instances:
        style = font["name"].getDebugName(instance.subfamilyNameID)
        instance.postscriptNameID = font["name"].addName(
            "SunnyMarker-" + style.replace(" ", ""), platforms=((3, 1, 0x409),)
        )
    buildStatTable(
        font,
        [
            {
                "tag": "opsz",
                "name": "Optical size",
                "values": [{"value": 14, "name": "14pt"}],
            },
            {
                "tag": "wdth",
                "name": "Width",
                "values": [
                    {"value": v, "name": n, **({"flags": 2} if v == 100 else {})}
                    for v, n in [
                        (75, "Condensed"),
                        (87.5, "SemiCondensed"),
                        (100, "Normal"),
                        (112.5, "SemiExpanded"),
                        (125, "Expanded"),
                    ]
                ],
            },
            {
                "tag": "wght",
                "name": "Weight",
                "values": [
                    {
                        "value": v,
                        "name": n,
                        **({"flags": 2, "linkedValue": 700} if v == 400 else {}),
                    }
                    for v, n in [
                        (300, "Light"),
                        (400, "Regular"),
                        (500, "Medium"),
                        (600, "SemiBold"),
                        (700, "Bold"),
                    ]
                ],
            },
            {
                "tag": "ital",
                "name": "Italic",
                "values": [
                    {
                        "value": 1 if italic else 0,
                        "name": "Italic" if italic else "Roman",
                        **({} if italic else {"flags": 2, "linkedValue": 1}),
                    }
                ],
            },
        ],
        macNames=False,
    )
    font.save(destination)


def specimen(source, destination):
    """A specimen rendered with the candidate itself, including its layout."""
    image = Image.new("RGB", (1600, 900), "#faf8f1")
    draw = ImageDraw.Draw(image)
    ink = "#242424"
    loc = dict(wght=400, wdth=100, opsz=36, slnt=0)
    draw_shaped(
        draw, (75, 100), "SUNNY MARKER / HANDWRITTEN & VARIABLE", source, 32, loc, ink
    )
    draw_shaped(draw, (75, 305), "A LITTLE MORE", source, 145, dict(loc, wdth=110), ink)
    draw_shaped(
        draw, (75, 480), "ROOM FOR IDEAS.", source, 145, dict(loc, wdth=90), ink
    )
    draw.rounded_rectangle((75, 565, 1525, 810), radius=20, fill="#ffe889")
    draw_shaped(
        draw,
        (115, 637),
        "COULD WE TRY THIS OVER HERE? →",
        source,
        33,
        dict(loc, wght=400, wdth=85, opsz=14),
        ink,
    )
    draw_shaped(
        draw,
        (810, 675),
        "YES, THIS ONE. ♡",
        source,
        38,
        dict(loc, wght=500, wdth=100, slnt=-5, opsz=14),
        ink,
    )
    draw_shaped(
        draw,
        (240, 755),
        "TINY NOTES. BIG IDEAS. YOUR OWN WAY.",
        source,
        27,
        dict(loc, wght=400, wdth=115, opsz=14),
        ink,
    )
    image.save(destination, optimize=True)


ROOT = Path(__file__).resolve().parents[1]
FAMILY = ROOT / "release/googlefonts/ofl/sunnymarker"
FAMILY.mkdir(parents=True, exist_ok=True)
for stale in FAMILY.glob("*.ttf"):
    stale.unlink()
source = ROOT / "build/outline-review/candidate/SunnyMarker[opsz,slnt,wdth,wght].ttf"
if not source.exists():
    raise FileNotFoundError(
        "Build the current review font with make review before packaging"
    )
for italic in (False, True):
    stem = "SunnyMarker" + ("-Italic" if italic else "") + "[opsz,wdth,wght].ttf"
    prepare_submission_font(source, FAMILY / stem, italic=italic)
shutil.copyfile(ROOT / "OFL.txt", FAMILY / "OFL.txt")
subprocess.run(
    [
        sys.executable,
        "-m",
        "gftools.scripts.add_font",
        "--github_url",
        "https://github.com/buildinternet/sunny-marker-font",
        str(FAMILY),
    ],
    check=True,
    timeout=120,
)
metadata = FAMILY / "METADATA.pb"
family = text_format.Parse(metadata.read_text(), FamilyProto())
family.designer = "Sam Dunn"
family.category[:] = ["HANDWRITING"]
family.date_added = "2026-09-17"
family.source.repository_url = "https://github.com/buildinternet/sunny-marker-font"
family.source.branch = "codex/resubmission-polish"
metadata.write_text(text_format.MessageToString(family))
description = """<p>Sunny Marker is a flexible handwritten marker typeface for labels,
notes, headings, and playful interfaces. Its rounded strokes retain the uneven
rhythm of marker lettering across weight, width, slant, and optical size.</p>
<p>A small annotation can point to a detail, add a reminder, or bring a warmer
voice to a familiar interface. Sunny Marker supports those little moments as
well as larger headlines. The family moves from condensed to expanded widths,
with upright lettering and a gentle nine-degree italic.
Weight ranges from Light to Bold, while optical sizing opens spacing and
small counters for use at smaller sizes.</p>
<img src="sunny-marker-specimen.png" alt="Sunny Marker: handwritten, variable,
made for little notes. Tiny notes, big ideas, your own way.">
<p>Designed by <a href="https://samdunn.org">Sam Dunn</a>, the family includes Latin accents, punctuation,
currencies, directional arrows, and a small collection of playful symbols.
The project provides editable UFO sources and a reproducible build pipeline
under the SIL Open Font License. Development includes AI-assisted concept
work and font engineering.</p>
<p>To contribute, see <a href="https://github.com/buildinternet/sunny-marker-font">the
Sunny Marker project on GitHub</a>.</p>
"""
(FAMILY / "DESCRIPTION.en_us.html").unlink(missing_ok=True)
(FAMILY / "article").mkdir(exist_ok=True)
(FAMILY / "article/ARTICLE.en_us.html").write_text(description)
specimen(source, FAMILY / "article/sunny-marker-specimen.png")
(FAMILY / "article/LICENSE.txt").unlink(missing_ok=True)
(FAMILY / "article/image-license.txt").write_text(
    "Sunny Marker specimen artwork © 2026 Sam Dunn.\n"
    "Licensed under Creative Commons Attribution-ShareAlike 4.0 International.\n"
    "https://creativecommons.org/licenses/by-sa/4.0/\n"
    "The font itself is licensed under SIL OFL 1.1; see ../OFL.txt.\n"
)
submission_root = FAMILY.parent.parent
shutil.copytree(
    ROOT / "sources/googlefonts/catalog",
    submission_root / "catalog",
    dirs_exist_ok=True,
)
archive = ROOT / "release" / f"sunny-marker-googlefonts-{VERSION}.zip"
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as output:
    for path in sorted(submission_root.rglob("*")):
        if path.is_file():
            info = zipfile.ZipInfo(
                str(path.relative_to(FAMILY.parent.parent)), (2026, 9, 15, 0, 0, 0)
            )
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            output.writestr(info, path.read_bytes())
print(archive.name)
