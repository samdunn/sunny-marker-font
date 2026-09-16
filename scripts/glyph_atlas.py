"""Render every actual glyph, including unencoded alternates and combining marks.

A temporary in-memory cmap maps one private-use code point to each glyph ID.
It is used only for the proof; no private-use encoding is added to release fonts.
"""
import io
import json
import math
from html import escape
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "documentation/glyph-atlas"
BG, INK, MUTED, YELLOW = "#F8F6EF", "#151820", "#73716B", "#FFD256"


def label_font(size):
    for path in ("/System/Library/Fonts/Supplemental/Arial.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def web_gallery(font, inventory, reverse):
    """Use the webfont for text; draw unmapped/zero-width glyphs explicitly."""
    cards = []
    glyph_set = font.getGlyphSet()
    for entry in sorted(inventory, key=lambda item: item['name'] in {'.notdef', 'space', 'nbspace'}):
        name = entry['name']
        codes = reverse.get(name, [])
        label = ', '.join(entry['unicode']) or ('missing glyph' if name == '.notdef' else 'alternate')
        char = chr(codes[0]) if codes else ''
        if name in {'space', 'nbspace'}:
            visual = '<span class="empty-glyph">space</span>'
        elif codes and entry['advance']:
            visual = f'<span class="marker">{escape(char)}</span>'
        else:
            glyph = font['glyf'][name]
            pen = SVGPathPen(glyph_set)
            glyph_set[name].draw(pen)
            em = font['head'].unitsPerEm
            box = f'{(glyph.xMin+glyph.xMax-em)/2:g} {(-glyph.yMax-glyph.yMin-em)/2:g} {em} {em}'
            visual = f'<svg viewBox="{box}" aria-hidden="true"><path transform="scale(1,-1)" d="{pen.getCommands()}"/></svg>'
        search = escape(f'{name} {label} {char}'.lower(), quote=True)
        cards.append(f'<li class="glyph-card" data-search="{search}" aria-label="{escape(name)}: {escape(label)}"><div class="glyph-drawing" aria-hidden="true">{visual}</div><span class="glyph-name" title="{escape(name)}">{escape(name)}</span><span class="glyph-code">{escape(label)}</span></li>')
    page = ROOT / 'web/index.html'
    source = page.read_text()
    start, end = '<!-- GLYPH CARDS START -->', '<!-- GLYPH CARDS END -->'
    if start in source and end in source:
        before, tail = source.split(start, 1)
        _, after = tail.split(end, 1)
        page.write_text(before + start + '\n' + '\n'.join(cards) + '\n' + end + after)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    path = ROOT / "fonts/ttf/SunnyMarker-Regular.ttf"
    font = TTFont(path)
    order = font.getGlyphOrder()
    reverse = {}
    for cp, name in font.getBestCmap().items():
        reverse.setdefault(name, []).append(cp)
    # Preserve the real order/outline IDs but make every glyph drawable by Pillow.
    for table in font["cmap"].tables:
        if table.isUnicode():
            table.cmap = {0xE000 + index: name for index, name in enumerate(order)}
    data = io.BytesIO()
    font.save(data)
    binary = data.getvalue()
    inventory = [{"index": i, "name": name,
                  "unicode": [f"U+{cp:04X}" for cp in reverse.get(name, [])],
                  "advance": font["hmtx"][name][0]}
                 for i, name in enumerate(order)]
    (OUT / "glyphs.json").write_text(json.dumps(inventory, indent=2) + "\n")
    web_gallery(font, inventory, reverse)

    def sheet(indices, columns, cell_width, cell_height, heading, filename):
        margin, top = 72, 265
        rows = math.ceil(len(indices) / columns)
        width, height = columns * cell_width + 2 * margin, rows * cell_height + top + 95
        image = Image.new("RGB", (width, height), BG)
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((margin, 46, margin + 308, 92), radius=9, fill=YELLOW)
        from package_gf import VERSION
        draw.text((margin + 17, 53), f"SUNNY MARKER / {VERSION}", font=label_font(23), fill=INK)
        draw.text((margin, 112), heading, font=label_font(52), fill=INK)
        draw.text((margin, 183), f"{len(order)} glyphs · Regular · Actual release outlines · SIL Open Font License 1.1",
                  font=label_font(23), fill=MUTED)
        draw.line((margin, 230, width - margin, 230), fill="#D8D5CB", width=2)
        for position, index in enumerate(indices):
            entry = inventory[index]
            x = margin + (position % columns) * cell_width
            y = top + (position // columns) * cell_height
            draw.rounded_rectangle((x + 3, y + 3, x + cell_width - 9, y + cell_height - 10),
                                   radius=10, fill="#FFFFFF")
            char = chr(0xE000 + index)
            face = ImageFont.truetype(io.BytesIO(binary), int(cell_height * .57))
            bounds = face.getbbox(char)
            if bounds[2] - bounds[0] > cell_width - 25:
                face = ImageFont.truetype(io.BytesIO(binary), int(face.size * (cell_width - 25) /
                                                                             (bounds[2] - bounds[0])))
                bounds = face.getbbox(char)
            glyph_x = x + (cell_width - (bounds[2] - bounds[0])) / 2 - bounds[0] - 3
            glyph_y = y + 13 + (cell_height * .62 - (bounds[3] - bounds[1])) / 2 - bounds[1]
            draw.text((glyph_x, glyph_y), char, font=face, fill=INK)
            if bounds[2] == bounds[0]:
                draw.text((x + 12, y + 38), "[empty]", font=label_font(16), fill=MUTED)
            draw.text((x + 12, y + cell_height - 57), entry["name"], font=label_font(13), fill=INK)
            label = ", ".join(entry["unicode"]) or ("missing-glyph symbol" if entry["name"] == ".notdef" else "unencoded alternate")
            draw.text((x + 12, y + cell_height - 36), label, font=label_font(11), fill=MUTED)
        draw.text((margin, height - 57), "Drawn from the font, not the concept sheet. Combining marks are shown alone.",
                  font=label_font(20), fill=MUTED)
        image.save(OUT / filename, optimize=True)

    sheet(list(range(len(order))), 16, 150, 158, "Every glyph. Every little detail.", "all-glyphs.png")
    for page in range(math.ceil(len(order) / 84)):
        start = page * 84
        indices = list(range(start, min(start + 84, len(order))))
        sheet(indices, 12, 180, 180, f"Glyph atlas / {page + 1:02d}", f"glyphs-{page + 1:02d}.png")
    print(f"Rendered {len(order)} glyphs in an overview and four detailed plates")
    import shutil
    shutil.copytree(OUT, ROOT / "web/glyph-atlas", dirs_exist_ok=True)


if __name__ == "__main__":
    main()
