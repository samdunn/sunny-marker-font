"""Render the accent-placement and small-outline corrections against 1.312."""

import argparse
from pathlib import Path
import zipfile

from PIL import Image, ImageDraw

from glyph_atlas import label_font
from shaped_proof import draw_shaped


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    args.output.mkdir(parents=True, exist_ok=True)
    before = root / "build/resubmission-polish/before-1.312.ttf"
    with zipfile.ZipFile(
        root / "release/sunny-marker-googlefonts-1.312.zip"
    ) as archive:
        before.write_bytes(
            archive.read("ofl/sunnymarker/SunnyMarker[opsz,wdth,wght].ttf")
        )
    image = Image.new("RGB", (1800, 1450), "#faf8f1")
    draw = ImageDraw.Draw(image)
    ink, muted = "#20221d", "#686763"
    draw.text(
        (55, 35), "SUNNY MARKER / ACCENTS ACROSS WEIGHT", font=label_font(30), fill=ink
    )
    for column, (path, title) in enumerate(
        [(before, "1.312 — BEFORE"), (args.candidate, "1.313 — CORRECTED")]
    ):
        x = 55 + column * 900
        draw.text((x, 100), title, font=label_font(23), fill=muted)
        for row, weight in enumerate((300, 400, 500, 600, 700)):
            y = 170 + row * 225
            draw.text(
                (x, y),
                f"WEIGHT {weight} · WIDTH 100% · OPTICAL 36",
                font=label_font(19),
                fill=muted,
            )
            loc = dict(wght=weight, wdth=100, opsz=36, slnt=0)
            draw_shaped(draw, (x, y + 100), "Ŵ ŵ Ẅ ẅ Ž ž Ř ř", path, 80, loc, ink)
            draw_shaped(
                draw, (x, y + 160), "A LITTLE MORE ROOM. Ŵŵ Žž Řř", path, 24, loc, ink
            )
    image.save(args.output / "accent-weight-comparison.png")
    image = Image.new("RGB", (1800, 1180), "#faf8f1")
    draw = ImageDraw.Draw(image)
    draw.text(
        (55, 35), "SUNNY MARKER / SMALL OUTLINE REPAIRS", font=label_font(30), fill=ink
    )
    for column, (path, title) in enumerate(
        [(before, "1.312 — BEFORE"), (args.candidate, "1.313 — CORRECTED")]
    ):
        x = 55 + column * 900
        draw.text((x, 100), title, font=label_font(23), fill=muted)
        for row, weight in enumerate((400, 500, 700)):
            y = 170 + row * 320
            draw.text(
                (x, y),
                f"WEIGHT {weight} · WIDTH 75% · OPTICAL 36",
                font=label_font(19),
                fill=muted,
            )
            loc = dict(wght=weight, wdth=75, opsz=36, slnt=0)
            draw_shaped(draw, (x, y + 200), "W & ª ★ ✧", path, 180, loc, ink)
            draw_shaped(
                draw,
                (x, y + 250),
                "NEW & SUNNY. ★ A LITTLE NOTE. ✧",
                path,
                24,
                loc,
                ink,
            )
    image.save(args.output / "outline-repairs-comparison.png")
    image = Image.new("RGB", (1800, 1000), "#faf8f1")
    draw = ImageDraw.Draw(image)
    draw.text(
        (55, 35), "SUNNY MARKER / BETWEEN THE MASTERS", font=label_font(30), fill=ink
    )
    for column, (path, title) in enumerate(
        [(before, "1.312 — BEFORE"), (args.candidate, "1.313 — CORRECTED")]
    ):
        x = 55 + column * 900
        draw.text((x, 100), title, font=label_font(23), fill=muted)
        for row, weight in enumerate((550, 600)):
            y = 170 + row * 370
            draw.text(
                (x, y),
                f"WEIGHT {weight} · WIDTH 87.5% · OPTICAL 23",
                font=label_font(19),
                fill=muted,
            )
            loc = dict(wght=weight, wdth=87.5, opsz=23, slnt=0)
            draw_shaped(draw, (x, y + 230), "u w k", path, 240, loc, ink)
            draw_shaped(
                draw, (x, y + 300), "a quick sunny week. ŵ ū ǩ", path, 32, loc, ink
            )
    image.save(args.output / "intermediate-joins-comparison.png")


if __name__ == "__main__":
    main()
