"""Prepare a Google Fonts review package without submitting or publishing it."""
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile
from gfmetadata import FamilyProto, text_format
from PIL import Image, ImageDraw, ImageFont

from package_gf import VERSION

ROOT = Path(__file__).resolve().parents[1]
FAMILY = ROOT / "release/googlefonts/ofl/sunnymarker"
FAMILY.mkdir(parents=True, exist_ok=True)
for stale in FAMILY.glob("*.ttf"):
    stale.unlink()
for font in (ROOT / "fonts/variable").glob("*.ttf"):
    shutil.copyfile(font, FAMILY / font.name)
shutil.copyfile(ROOT / "OFL.txt", FAMILY / "OFL.txt")
subprocess.run([sys.executable, "-m", "gftools.scripts.add_font", "--github_url",
                "https://github.com/buildinternet/sunny-marker-font", str(FAMILY)],
               check=True, timeout=120)
metadata = FAMILY / "METADATA.pb"
family = text_format.Parse(metadata.read_text(), FamilyProto())
family.designer = "Sam Dunn"
family.category[:] = ["HANDWRITING"]
family.source.repository_url = "https://github.com/buildinternet/sunny-marker-font"
family.source.branch = "main"
metadata.write_text(text_format.MessageToString(family))
description = """<p>Sunny Marker is a flexible handwritten marker typeface for labels,
notes, headings, and playful interfaces. Its rounded strokes retain the uneven
rhythm of marker lettering across weight, width, slant, and optical size.</p>
<p>A small annotation can point to a detail, add a reminder, or bring a warmer
voice to a familiar interface. Sunny Marker supports those little moments as
well as larger headlines. Its single variable font moves from condensed to
expanded widths and from upright lettering to a gentle nine-degree slant.
Weight ranges from Light to Bold, while optical sizing opens spacing and
small counters for use at smaller sizes.</p>
<img src="sunny-marker-specimen.png" alt="Sunny Marker specimens at condensed,
normal and expanded widths, with a small handwritten annotation.">
<p>Designed by Sam Dunn, the family includes Latin accents, punctuation,
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
specimen = Image.new("RGB", (1600, 900), "#faf8f1")
draw = ImageDraw.Draw(specimen)
font_path = next((ROOT / "fonts/variable").glob("*.ttf"))
def face(size, weight=400, width=100, slant=0):
    font = ImageFont.truetype(str(font_path), size)
    font.set_variation_by_axes([weight, width, 36, slant])
    return font
ink = "#20231f"
draw.text((70, 38), "SUNNY MARKER", font=face(125, 600), fill=ink)
draw.text((74, 225), "Tiny notes. Big personality.", font=face(67), fill=ink)
draw.text((1020, 365), "a little sunshine ↙", font=face(40, slant=-5), fill="#566333")
draw.rounded_rectangle((70, 445, 1530, 830), radius=20, fill="#ffdf72")
for i, (width, label) in enumerate(((75, "Condensed"), (100, "Normal"), (125, "Expanded"))):
    y = 475 + i * 105
    draw.text((102, y + 12), label, font=ImageFont.load_default(size=24), fill=ink)
    draw.text((300, y), "Make room for good things.", font=face(64, width=width), fill=ink)
specimen.save(FAMILY / "article/sunny-marker-specimen.png", optimize=True)
archive = ROOT / "release" / f"sunny-marker-googlefonts-{VERSION}.zip"
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as output:
    for path in sorted(FAMILY.rglob("*")):
        if path.is_file():
            info = zipfile.ZipInfo(str(path.relative_to(FAMILY.parent.parent)), (2026, 9, 15, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            output.writestr(info, path.read_bytes())
print(archive.name)
