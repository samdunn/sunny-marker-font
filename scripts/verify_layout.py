"""Exercise actual HarfBuzz shaping, attachment and spacing across all axes."""

import argparse
import itertools
import json
import unicodedata
from pathlib import Path

from fontTools.ttLib import TTFont
import uharfbuzz as hb


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("font", type=Path)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    font = TTFont(args.font)
    order = font.getGlyphOrder()
    cmap = font.getBestCmap()
    hfont = hb.Font(hb.Face(args.font.read_bytes()))

    def shape(text, features=None):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(hfont, buf, features)
        return [
            (order[g.codepoint], p.x_advance, p.x_offset, p.y_offset)
            for g, p in zip(buf.glyph_infos, buf.glyph_positions)
        ]

    for tag in ("GDEF", "GPOS", "GSUB"):
        assert tag in font, tag
    assert all(c in cmap for c in [0x331, 0x2BC, 0x14B, 0x25CC, 0x2028, 0x2029])
    for code, name in cmap.items():
        if unicodedata.category(chr(code)).startswith("M"):
            assert font["hmtx"][name][0] == 0, name
            assert font["GDEF"].table.GlyphClassDef.classDefs[name] == 3, name
    accented = [chr(c) for c in cmap if unicodedata.normalize("NFD", chr(c)) != chr(c)]
    cases = [
        "j\u0300",
        "j\u0308",
        "j\u0303",
        "i\u030a",
        "į\u0301",
        "į\u0303",
        "A\u0331",
        "a\u0331",
        "q\u0301",
        "b\u0303",
        "Ą\u0301",
        "ę\u0303",
        "Ė\u0301",
        "Ū\u0303",
        "n\u0303\u0301",
        "i\u0307\u0301",
        "I\u0307\u0301",
        "ŋ Ŋ QʼEQCHIʼ Ľďľť",
    ]
    tested = 0
    for values in itertools.product(
        (300, 400, 550, 700), (75, 100, 125), (10, 14, 36), (0, -4.5, -9)
    ):
        location = dict(zip(("wght", "wdth", "opsz", "slnt"), values))
        hfont.set_variations(location)
        for ch in accented:
            assert shape(ch) == shape(unicodedata.normalize("NFD", ch)), (location, ch)
        for text in cases:
            shaped = shape(text)
            assert all(x[0] != ".notdef" for x in shaped), (location, text)
            if text.startswith(("j", "i", "į")):
                assert shaped[0][0] not in ("i", "j", "iogonek"), (
                    location,
                    text,
                    shaped,
                )
            for glyph, advance, x, y in shaped[1:]:
                if glyph.endswith(("comb", ".case", ".alt", ".turn")):
                    assert advance == 0, (location, text, shaped)
                    assert x != 0 or y != 0, (location, text, shaped)
        # Accents must not create tracking differences in otherwise equal text.
        assert sum(x[1] for x in shape("AVATAR")) == sum(x[1] for x in shape("ÁVÁTÁR"))
        tested += 1
    report = {
        "passed": True,
        "locations": tested,
        "canonical_pairs_per_location": len(accented),
        "attachment_strings_per_location": len(cases),
        "gdef_marks": True,
        "zero_width_marks": True,
        "accented_kerning_equivalent": True,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(report)


if __name__ == "__main__":
    main()
