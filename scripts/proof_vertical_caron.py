"""Before/after proof of the vertical caron (ď ľ ť Ľ) across weight and slant.

usage: proof_vertical_caron.py BEFORE AFTER OUTPUT.png [--before-label] [--after-label]
Both fonts must be four-axis (opsz, slnt, wdth, wght) variable fonts.
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw

from glyph_atlas import label_font
from shaped_proof import draw_shaped

BG, INK, MUTED = "#faf8f1", "#252525", "#77746d"
TEXT = "Ľ ď ľ ť  Ľubo ďalej ľahko ťava"
ROWS = [
    ("Light", dict(wght=300, wdth=100, opsz=36, slnt=0)),
    ("Regular", dict(wght=400, wdth=100, opsz=36, slnt=0)),
    ("Bold", dict(wght=700, wdth=100, opsz=36, slnt=0)),
    ("Bold condensed", dict(wght=700, wdth=75, opsz=10, slnt=0)),
    ("Italic", dict(wght=400, wdth=100, opsz=36, slnt=-9)),
]
SIZE = 58


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--before-label", default="1.314")
    parser.add_argument("--after-label", default="1.315")
    args = parser.parse_args()
    image = Image.new("RGB", (1600, 170 + len(ROWS) * 150), BG)
    draw = ImageDraw.Draw(image)
    draw.text((55, 36), "SUNNY MARKER / VERTICAL CARON", font=label_font(30), fill=INK)
    draw.text(
        (55, 83),
        f"Actual font renders. Left: {args.before_label}. Right: {args.after_label}.",
        font=label_font(21),
        fill=MUTED,
    )
    for row, (label, location) in enumerate(ROWS):
        y = 150 + row * 150
        draw.text((55, y), label, font=label_font(18), fill=MUTED)
        for col, path in enumerate((args.before, args.after)):
            draw_shaped(draw, (55 + col * 780, y + 95), TEXT, path, SIZE, location, INK)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output)
    print(args.output)


if __name__ == "__main__":
    main()
