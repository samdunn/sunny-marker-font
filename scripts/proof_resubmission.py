"""Readable specimens and outline-only QA instances across the designspace."""

import argparse
import itertools
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw

from glyph_atlas import label_font
from proof_outline_review import face, BG, INK, MUTED
from shaped_proof import draw_shaped


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("font", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    f = TTFont(args.font)
    out = args.output / "instances"
    out.mkdir(exist_ok=True)
    order = f.getGlyphOrder()
    for w, d, o, s in itertools.product(
        (300, 400, 500, 700), (75, 100, 125), (10, 36), (0, -9)
    ):
        gs = f.getGlyphSet(location=dict(wght=w, wdth=d, opsz=o, slnt=s))
        glyphs = {}
        metrics = {}
        for name in order:
            pen = TTGlyphPen(gs)
            gs[name].draw(pen)
            glyphs[name] = pen.glyph()
            metrics[name] = (round(gs[name].width), 0)
        fb = FontBuilder(1000, isTTF=True)
        fb.setupGlyphOrder(order)
        fb.setupCharacterMap(f.getBestCmap())
        fb.setupGlyf(glyphs)
        for name, glyph in glyphs.items():
            glyph.recalcBounds(fb.font["glyf"])
            metrics[name] = (metrics[name][0], getattr(glyph, "xMin", 0))
        fb.setupHorizontalMetrics(metrics)
        fb.setupHorizontalHeader(ascent=960, descent=-340)
        fb.setupOS2(
            usWeightClass=w,
            usWidthClass={75: 3, 100: 5, 125: 7}[d],
            fsSelection=1 if s else 64,
            sTypoAscender=960,
            sTypoDescender=-340,
            usWinAscent=960,
            usWinDescent=340,
        )
        fb.setupNameTable(
            {
                "familyName": "Sunny Marker QA",
                "styleName": "Italic" if s else "Regular",
                "psName": f"SunnyMarkerQA-w{w}-d{d}-o{o}-s{abs(s)}",
            }
        )
        fb.setupPost(italicAngle=s)
        fb.font["head"].macStyle = 2 if s else 0
        fb.save(out / f"w{w}-d{d}-o{o}-s{abs(s)}.ttf")
    for o in (10, 36):
        img = Image.new("RGB", (2200, 2400), BG)
        draw = ImageDraw.Draw(img)
        draw.text(
            (55, 30),
            f"SUNNY MARKER / VARIABLE EXTREMES / OPTICAL {o}",
            font=label_font(30),
            fill=INK,
        )
        rows = list(itertools.product((300, 400, 700), (75, 100, 125), (0, -9)))
        for index, (w, d, s) in enumerate(rows):
            col, row = index % 2, index // 2
            x, y = 55 + col * 1100, 120 + row * 250
            loc = dict(wght=w, wdth=d, opsz=o, slnt=s)
            draw.text(
                (x, y),
                f"WEIGHT {w} / WIDTH {d}% / SLANT {s}",
                font=label_font(19),
                fill=MUTED,
            )
            ft = face(args.font, 50, loc)
            for offset, text in enumerate(
                [
                    "SUNNY MARKER — B M W @ © ® § ¶",
                    "ÀÁÂÃÄÅ Ąą Ęę Ľďľť ßẞ Ŋŋ",
                    "tiny notes, big ideas. 0123456789",
                ]
            ):
                draw_shaped(
                    draw, (x, y + 70 + offset * 65), text, args.font, 50, loc, INK
                )
        img.save(args.output / f"extremes-opsz{o}.png")
    img = Image.new("RGB", (1800, 1500), BG)
    draw = ImageDraw.Draw(img)
    draw.text(
        (55, 30),
        "SUNNY MARKER / LANGUAGES & COMBINING MARKS",
        font=label_font(29),
        fill=INK,
    )
    rows = [
        ("French / Portuguese", "À BIENTÔT. SÃO PAULO. CŒUR. ÇA VA ?"),
        ("Polish", "ZAŻÓŁĆ GĘŚLĄ JAŹŃ. PÓJDŹŻE, KIŃ TĘ CHMURNOŚĆ."),
        ("Czech / Slovak", "PŘÍLIŠ ŽLUŤOUČKÝ KŮŇ. ĽÚBIŤ ĎALEJ. ľ ď ť"),
        ("German / Latvian", "GRÜẞE. STRAẞE. ĢIMENE. ĶIRSIS. ĻOTI."),
        ("Lithuanian accents", "Ą́ Ą̃ Ė́ Ū̃ į́ į̃ ė́ ū̃ i̇́ j̃"),
        ("Added sample coverage", "QʼEQCHIʼ · A̱ a̱ E̱ e̱ · Ŋ ŋ"),
        ("Combining / stacked marks", "á̱ ẽ̱ q́ b̃ ñ́ i̊ j̀ j̈ į́"),
        (
            "Small annotations / 18px",
            "A LITTLE MORE ROOM TO BREATHE. DON’T FORGET THE PLANTS!",
        ),
    ]
    for i, (label, text) in enumerate(rows):
        y = 120 + i * 165
        draw.text((55, y), label, font=label_font(21), fill=MUTED)
        draw_shaped(
            draw,
            (55, y + 105),
            text,
            args.font,
            18 if i == 7 else 62,
            dict(wght=400, wdth=100, opsz=36, slnt=0),
            INK,
        )
    img.save(args.output / "language-proof.png")
    print(args.output)


if __name__ == "__main__":
    main()
