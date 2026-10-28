"""Prepare a Google Fonts package from the built fonts, without submitting it.

The upright and italic fonts are copied unchanged from fonts/variable, where
sources/build.sh writes them. METADATA.pb lists the repository files that
Google's packager copies, and the About article is kept in documentation/article.
"""

from pathlib import Path
import shutil
import subprocess
import sys
import zipfile
from gfmetadata import FamilyProto, text_format

from PIL import Image, ImageDraw
from shaped_proof import draw_shaped
from package_gf import VERSION

REPOSITORY = "https://github.com/samdunn/sunny-marker-font"
STYLES = ("SunnyMarker[opsz,wdth,wght].ttf", "SunnyMarker-Italic[opsz,wdth,wght].ttf")
ARTICLE = ("ARTICLE.en_us.html", "sunny-marker-specimen.png", "image-license.txt")


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
VARIABLE = ROOT / "fonts/variable"
source = VARIABLE / "SunnyMarker[opsz,slnt,wdth,wght].ttf"
if not all((VARIABLE / name).exists() for name in (source.name, *STYLES)):
    raise FileNotFoundError("Build the fonts with sources/build.sh before packaging")
for name in STYLES:
    shutil.copyfile(VARIABLE / name, FAMILY / name)
shutil.copyfile(ROOT / "OFL.txt", FAMILY / "OFL.txt")
(FAMILY / "METADATA.pb").unlink(missing_ok=True)
subprocess.run(
    [
        sys.executable,
        "-m",
        "gftools.scripts.add_font",
        "--github_url",
        REPOSITORY,
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
family.source.repository_url = REPOSITORY
family.source.branch = "main"
del family.source.files[:]
for source_file, dest_file in (
    ("OFL.txt", "OFL.txt"),
    *((f"fonts/variable/{name}", name) for name in STYLES),
    *((f"documentation/article/{name}", f"article/{name}") for name in ARTICLE),
):
    entry = family.source.files.add()
    entry.source_file, entry.dest_file = source_file, dest_file
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
<p>To contribute, see <a href="https://github.com/samdunn/sunny-marker-font">the
Sunny Marker project on GitHub</a>.</p>
"""
(FAMILY / "DESCRIPTION.en_us.html").unlink(missing_ok=True)
article = ROOT / "documentation/article"
article.mkdir(parents=True, exist_ok=True)
(article / "ARTICLE.en_us.html").write_text(description)
specimen(source, article / "sunny-marker-specimen.png")
(article / "image-license.txt").write_text(
    "Sunny Marker specimen artwork © 2026 Sam Dunn.\n"
    "Licensed under Creative Commons Attribution-ShareAlike 4.0 International.\n"
    "https://creativecommons.org/licenses/by-sa/4.0/\n"
    "The font itself is licensed under SIL OFL 1.1; see ../OFL.txt.\n"
)
shutil.rmtree(FAMILY / "article", ignore_errors=True)
(FAMILY / "article").mkdir()
for name in ARTICLE:
    shutil.copyfile(article / name, FAMILY / "article" / name)
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
