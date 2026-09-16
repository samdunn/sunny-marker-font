"""Render Sunny Marker specimens from the shipped fonts (Pillow + fonttools)."""
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "web/specimens"
DEST.mkdir(exist_ok=True)
with ZipFile(ROOT / "web/downloads/SunnyMarker-1.310.zip") as archive:
    MARKER = archive.read("SunnyMarker[opsz,slnt,wdth,wght].ttf")
INK = "#242424"
PAPER = "#fbfaf7"
SUN = "#ffd44e"


def face(size, *, weight=400, width=100, slant=0, optical=18):
    data = MARKER
    font = ImageFont.truetype(BytesIO(data), size)
    axes = TTFont(BytesIO(data))["fvar"].axes
    values = {"wght": weight, "wdth": width, "slnt": slant, "opsz": optical}
    font.set_variation_by_axes([
        max(axis.minValue, min(axis.maxValue, values.get(axis.axisTag, axis.defaultValue)))
        for axis in axes
    ])
    return font


def text(draw, xy, value, size, *, fill=INK, max_width=None, **style):
    font = face(size, **style)
    while max_width and draw.textlength(value, font=font) > max_width:
        size -= 1
        font = face(size, **style)
    draw.text(xy, value, font=font, fill=fill, anchor="lt")


def save(canvas, name):
    canvas.save(DEST / name, optimize=True)


# A few small notes scattered across a quiet marker board.
canvas = Image.new("RGB", (1600, 1200), PAPER)

def note(xy, lines, angle, size=65):
    layer = Image.new("RGBA", (820, 260), (0, 0, 0, 0))
    pen = ImageDraw.Draw(layer)
    for index, line in enumerate(lines):
        text(pen, (20, 16 + index * 90), line, size, weight=400, optical=18, max_width=760)
    rotated = layer.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    canvas.paste(rotated, xy, rotated)

note((130, 175), ["COULD WE TRY", "THIS OVER HERE? ↘"], 5)
note((810, 505), ["YES, THIS ONE. ♡"], -4, size=67)
note((205, 825), ["A LITTLE MORE", "ROOM TO BREATHE. →"], 3, size=63)
save(canvas, "margin-notes.png")

# Compact, uppercase labeling: condensed letterforms, numbers, and punctuation.
canvas = Image.new("RGB", (1600, 1200), "#ffedaa")
draw = ImageDraw.Draw(canvas)
text(draw, (110, 100), "SMALL BATCH", 56, weight=500, width=80)
text(draw, (1240, 100), "NO. 027", 56, weight=500, width=80, max_width=250)
text(draw, (110, 334), "FRESH", 202, weight=650, width=75, optical=30)
text(draw, (110, 569), "PERSPECTIVE.", 190, weight=650, width=75, optical=30, max_width=1380)
draw.line([(112, 828), (1488, 828)], fill=INK, width=3)
text(draw, (110, 906), "GOOD IDEAS, IN SMALL SPACES.", 70, weight=450, width=80, max_width=1380)
text(draw, (110, 1060), "MADE WITH CARE.   /   HANDLE WITH CURIOSITY.", 48, weight=450, width=80)
save(canvas, "small-labels.png")

# Expanded display type, reversed out, with a mixed-case slanted annotation.
canvas = Image.new("RGB", (1600, 1200), INK)
draw = ImageDraw.Draw(canvas)
text(draw, (110, 100), "WIDE OPEN.", 55, width=125, fill=PAPER)
text(draw, (1320, 82), "✧", 151, fill=SUN)
text(draw, (110, 330), "MAKE SOME", 171, weight=650, width=125, optical=36, fill=PAPER, max_width=1380)
text(draw, (110, 538), "ROOM.", 225, weight=650, width=125, optical=36, fill=PAPER)
text(draw, (116, 873), "for the good stuff. →", 94, weight=400, width=100, slant=-6, fill=SUN, max_width=1380)
text(draw, (110, 1072), "A LITTLE MORE ROOM TO PLAY.", 49, width=110, fill=PAPER)
save(canvas, "wide-open.png")
# A concise, public-facing repository header; technical proof sheets stay in proofs/.
canvas = Image.new("RGB", (1600, 640), PAPER)
draw = ImageDraw.Draw(canvas)
text(draw, (105, 74), "HANDWRITTEN. VARIABLE. MADE FOR LITTLE NOTES.", 43, width=100)
text(draw, (98, 205), "SUNNY MARKER", 190, weight=600, width=95, optical=36, max_width=1400)
text(draw, (105, 510), "TINY NOTES.", 58, width=80)
text(draw, (591, 510), "BIG IDEAS.", 58, width=100)
text(draw, (1030, 510), "YOUR OWN WAY.", 56, width=115, slant=-3, max_width=470)
save(canvas, "github-header.png")
print("Rendered three 1600 × 1200 specimens and a 1600 × 640 GitHub header.")
