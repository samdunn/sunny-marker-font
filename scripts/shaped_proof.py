"""Render HarfBuzz-shaped text even on Pillow builds without libraqm."""

from functools import lru_cache
import io
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import ImageFont
import uharfbuzz as hb


@lru_cache(maxsize=128)
def load(path, stamp, size, coordinates):
    data = Path(path).read_bytes()
    font = TTFont(io.BytesIO(data))
    mapping = {0xE000 + i: name for i, name in enumerate(font.getGlyphOrder())}
    for table in font["cmap"].tables:
        if table.isUnicode():
            table.cmap = mapping.copy()
    output = io.BytesIO()
    font.save(output)
    face = ImageFont.truetype(
        io.BytesIO(output.getvalue()), size, layout_engine=ImageFont.Layout.BASIC
    )
    location = dict(coordinates)
    if "fvar" in font:
        face.set_variation_by_axes(
            [location.get(a.axisTag, a.defaultValue) for a in font["fvar"].axes]
        )
    shaper = hb.Font(hb.Face(data))
    shaper.set_variations(location)
    return face, shaper, font["head"].unitsPerEm


def draw_shaped(draw, position, text, path, size, location, fill):
    path = Path(path)
    face, shaper, upm = load(
        str(path), path.stat().st_mtime_ns, size, tuple(sorted(location.items()))
    )
    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    hb.shape(shaper, buffer)
    x, y = position
    factor = size / upm
    for glyph, p in zip(buffer.glyph_infos, buffer.glyph_positions):
        draw.text(
            (x + p.x_offset * factor, y - p.y_offset * factor),
            chr(0xE000 + glyph.codepoint),
            font=face,
            fill=fill,
            anchor="ls",
        )
        x += p.x_advance * factor
        y -= p.y_advance * factor
    return x - position[0]
