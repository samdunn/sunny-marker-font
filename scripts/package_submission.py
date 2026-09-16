"""Prepare a Google Fonts review package without submitting or publishing it."""
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile
from gfmetadata import FamilyProto, text_format
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables

from package_gf import set_name

# Metadata-only onboarding candidate; the published web/npm release is 1.310.
VERSION = "1.311"


def prepare_submission_font(source, destination):
    font = TTFont(source, recalcTimestamp=False)
    for name_id, value in ((9, "Sam Dunn"), (12, "https://samdunn.org"),
                           (5, "Version " + VERSION),
                           (3, f"{VERSION};NONE;{font['name'].getDebugName(6)}")):
        set_name(font, value, name_id)
    font['head'].fontRevision = float(VERSION)
    for instance in font['fvar'].instances:
        style = font['name'].getDebugName(instance.subfamilyNameID)
        instance.postscriptNameID = font['name'].addName(
            'SunnyMarker-' + style.replace(' ', ''), platforms=((3, 1, 0x409),))
    stat = font['STAT'].table
    axes = {axis.AxisTag: index for index, axis in enumerate(stat.DesignAxisRecord.Axis)}
    for entry in stat.AxisValueArray.AxisValue:
        if entry.Format in (1, 2, 3) and entry.AxisIndex == axes['opsz']:
            entry.Flags &= ~2
    for value, label in ((87.5, 'SemiCondensed'), (112.5, 'SemiExpanded')):
        entry = otTables.AxisValue()
        entry.Format, entry.AxisIndex, entry.Flags = 1, axes['wdth'], 0
        entry.Value = value
        entry.ValueNameID = font['name'].addName(label, platforms=((3, 1, 0x409),))
        stat.AxisValueArray.AxisValue.append(entry)
    stat.AxisValueCount = len(stat.AxisValueArray.AxisValue)
    font.save(destination)

ROOT = Path(__file__).resolve().parents[1]
FAMILY = ROOT / "release/googlefonts/ofl/sunnymarker"
FAMILY.mkdir(parents=True, exist_ok=True)
for stale in FAMILY.glob("*.ttf"):
    stale.unlink()
for font in (ROOT / "fonts/variable").glob("*.ttf"):
    prepare_submission_font(font, FAMILY / font.name)
shutil.copyfile(ROOT / "OFL.txt", FAMILY / "OFL.txt")
subprocess.run([sys.executable, "-m", "gftools.scripts.add_font", "--github_url",
                "https://github.com/buildinternet/sunny-marker-font", str(FAMILY)],
               check=True, timeout=120)
metadata = FAMILY / "METADATA.pb"
family = text_format.Parse(metadata.read_text(), FamilyProto())
family.designer = "Sam Dunn"
family.category[:] = ["HANDWRITING"]
family.date_added = "2026-09-16"
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
shutil.copyfile(ROOT / "web/specimens/github-header.png",
                FAMILY / "article/sunny-marker-specimen.png")
archive = ROOT / "release" / f"sunny-marker-googlefonts-{VERSION}.zip"
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as output:
    for path in sorted(FAMILY.rglob("*")):
        if path.is_file():
            info = zipfile.ZipInfo(str(path.relative_to(FAMILY.parent.parent)), (2026, 9, 15, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            output.writestr(info, path.read_bytes())
print(archive.name)
