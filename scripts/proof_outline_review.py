"""Before/after outline and reading proofs made from the actual font binaries."""

import argparse
import io
import json
import math
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPointPen
from PIL import Image, ImageDraw, ImageFont

from glyph_atlas import label_font
from shaped_proof import draw_shaped

LOCATION = dict(wght=400, wdth=100, opsz=36, slnt=0)
BG, INK, MUTED = "#faf8f1", "#252525", "#77746d"


def face(path, size, location=LOCATION):
    result = ImageFont.truetype(str(path), size)
    font = TTFont(path)
    if "fvar" in font:
        result.set_variation_by_axes([location[a.axisTag] for a in font["fvar"].axes])
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--before-label", default="published 1.310")
    parser.add_argument("--after-label", default="working candidate")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    paths = [args.before, args.after]
    image = Image.new("RGB", (1600, 1420), BG)
    draw = ImageDraw.Draw(image)
    draw.text((55, 36), "SUNNY MARKER / OUTLINE REVIEW", font=label_font(30), fill=INK)
    draw.text(
        (55, 83),
        f"Actual font renders. Left: {args.before_label}. Right: {args.after_label}.",
        font=label_font(21),
        fill=MUTED,
    )
    rows = [
        ("Basic letters", "SUNNY MARKER", 76),
        ("Accents above", "ÁÀÂÃÄÅ ĆČ ĚĢ", 67),
        ("Lowercase accents", "áàâãäå ćč ěğ", 67),
        ("Connected and side marks", "Ąą Ęę Įį Ųų Ľďľť", 61),
        ("Symbols and sharp S", "© ® ™ § ¶ € £ ¥ ß ẞ", 68),
        ("Small text / 24 px", "A LITTLE MORE ROOM TO BREATHE.", 24),
        ("Small text / 18 px", "DON’T FORGET THE PLANTS!  À BIENTÔT.", 18),
    ]
    for row, (label, text, size) in enumerate(rows):
        y = 156 + row * 173
        draw.text((55, y), label, font=label_font(18), fill=MUTED)
        for col, path in enumerate(paths):
            draw_shaped(
                draw, (55 + col * 780, y + 112), text, path, size, LOCATION, INK
            )
    image.save(args.output / "before-after.png")

    # PUA mappings exist only in these in-memory proof fonts.
    names = ["O", "S", "acutecomb", "ogonekcomb", "Euro", "copyright"]
    fonts = [TTFont(path) for path in paths]
    proof_binaries = []
    for font in fonts:
        for table in font["cmap"].tables:
            if table.isUnicode():
                table.cmap = {0xE000 + i: name for i, name in enumerate(names)}
        binary = io.BytesIO()
        font.save(binary)
        proof_binaries.append(binary.getvalue())
    image = Image.new("RGB", (1800, 1220), BG)
    draw = ImageDraw.Draw(image)
    draw.text(
        (45, 25),
        f"OUTLINE POINTS / {args.before_label.upper()} → {args.after_label.upper()}",
        font=label_font(29),
        fill=INK,
    )
    statistics = {}
    for column, name in enumerate(names):
        for row, path in enumerate(paths):
            font = fonts[row]
            gs = font.getGlyphSet(location=LOCATION if "fvar" in font else None)
            pen = RecordingPointPen()
            gs[name].drawPoints(pen)
            points = [(a[0], a[1]) for op, a, kw in pen.value if op == "addPoint"]
            statistics.setdefault(name, {})["before" if row == 0 else "after"] = len(
                points
            )
            xs, ys = zip(*(p for p, _ in points))
            scale = min(240 / (max(xs) - min(xs)), 340 / (max(ys) - min(ys)))
            size = int(scale * 1000)
            scale = size / 1000
            x = 35 + column * 295 - min(xs) * scale
            baseline = 460 + row * 570 + min(ys) * scale
            f = ImageFont.truetype(io.BytesIO(proof_binaries[row]), size)
            if "fvar" in font:
                f.set_variation_by_axes(
                    [LOCATION[a.axisTag] for a in font["fvar"].axes]
                )
            draw.text(
                (x, baseline), chr(0xE000 + column), font=f, fill="#dedbd2", anchor="ls"
            )
            for (px, py), kind in points:
                xx, yy = x + px * scale, baseline - py * scale
                radius = 2 if kind else 1.5
                draw.ellipse(
                    (xx - radius, yy - radius, xx + radius, yy + radius),
                    fill="#2b65b8" if kind else "#d09a39",
                )
            label_x = 35 + column * 295
            draw.text((label_x, 505 + row * 570), name, font=label_font(21), fill=INK)
            draw.text(
                (label_x, 537 + row * 570),
                f"{len(points)} points",
                font=label_font(18),
                fill=MUTED,
            )
    image.save(args.output / "outline-points.png")
    (args.output / "point-counts.json").write_text(
        json.dumps(statistics, indent=2) + "\n"
    )
    # Complete inventory at a consistent em size, including standalone marks.
    atlas_font = TTFont(args.after)
    names = sorted(
        atlas_font.getGlyphOrder(),
        key=lambda name: name in {".notdef", "space", "nbspace"},
    )
    for table in atlas_font["cmap"].tables:
        if table.isUnicode():
            table.cmap = {0xE000 + i: name for i, name in enumerate(names)}
    binary = io.BytesIO()
    atlas_font.save(binary)
    af = ImageFont.truetype(io.BytesIO(binary.getvalue()), 128)
    if "fvar" in atlas_font:
        af.set_variation_by_axes([LOCATION[a.axisTag] for a in atlas_font["fvar"].axes])
    for page in range(math.ceil(len(names) / 84)):
        image = Image.new("RGB", (2240, 1550), BG)
        draw = ImageDraw.Draw(image)
        draw.text(
            (40, 28),
            f"SUNNY MARKER / CANDIDATE GLYPHS / {page+1}",
            font=label_font(30),
            fill=INK,
        )
        draw.text(
            (40, 77),
            "Regular · normal width · upright · 36pt optical size · actual outlines",
            font=label_font(20),
            fill=MUTED,
        )
        for cell, index in enumerate(
            range(page * 84, min((page + 1) * 84, len(names)))
        ):
            x, y = 40 + (cell % 12) * 180, 128 + (cell // 12) * 195
            char = chr(0xE000 + index)
            blank = {
                "lineSeparator": "line break",
                "paragraphSeparator": "paragraph break",
                "space": "space",
                "nbspace": "no-break space",
            }.get(names[index])
            if blank:
                draw.text((x + 15, y + 105), blank, font=label_font(15), fill=MUTED)
            else:
                bounds = af.getbbox(char, anchor="ls")
                draw.text(
                    (x + 80 - (bounds[0] + bounds[2]) / 2, y + 126),
                    char,
                    font=af,
                    fill=INK,
                    anchor="ls",
                )
            draw.text((x + 5, y + 166), names[index], font=label_font(14), fill=MUTED)
        image.save(args.output / f"glyphs-{page+1:02}.png")
    print(json.dumps(statistics, indent=2))


if __name__ == "__main__":
    main()
