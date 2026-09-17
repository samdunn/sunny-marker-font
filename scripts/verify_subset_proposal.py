"""Reproduce the Latin routing problem and test a proposed nam-files patch.

This does not modify Fontspector, Google metadata or any installed library.
It checks explicit subset codepoints, actual subset binaries, and shaping.
"""

import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import unicodedata

from fontTools import subset
from fontTools.ttLib import TTFont
import uharfbuzz as hb


def codepoints(text):
    return {int(m, 16) for m in re.findall(r"^0x([0-9A-Fa-f]+)\b", text, re.M)}


def shape(data, text):
    font = hb.Font(hb.Face(data))
    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    hb.shape(font, buffer)
    assert all(info.codepoint for info in buffer.glyph_infos), repr(text)
    return [
        (i.codepoint, p.x_advance, p.y_advance, p.x_offset, p.y_offset)
        for i, p in zip(buffer.glyph_infos, buffer.glyph_positions)
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("nam_files", type=Path)
    parser.add_argument("font", type=Path)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    report = {
        "font_sha256": hashlib.sha256(args.font.read_bytes()).hexdigest(),
        "upstream_base": subprocess.check_output(
            ["git", "-C", str(args.nam_files), "rev-parse", "HEAD"], text=True
        ).strip(),
        "official_fontspector_modified": False,
        "subsets": {},
    }
    for name, added, samples in [
        ("latin", {0x0331}, ["A\u0331", "a\u0331", "e\u0331\u0301", "i\u0331"]),
        ("latin-ext", {0x0331, 0x1EBC, 0x1EBD}, ["Ŋ\u0331", "Ẽ", "ẽ", "Ẽẽ"]),
    ]:
        path = f"Lib/gfsubsets/data/{name}_unique-glyphs.nam"
        before = codepoints(
            subprocess.check_output(
                ["git", "-C", str(args.nam_files), "show", "HEAD:" + path], text=True
            )
        )
        after = codepoints((args.nam_files / path).read_text())
        assert after - before == added and not before - after
        # Latin-ext files are generated with a basic Latin kernel by gfsubsets.
        if name == "latin-ext":
            after |= codepoints(
                (
                    args.nam_files / "Lib/gfsubsets/data/latin_unique-glyphs.nam"
                ).read_text()
            )
        font = TTFont(args.font)
        options = subset.Options()
        options.layout_features = ["*"]
        subsetter = subset.Subsetter(options=options)
        subsetter.populate(unicodes=after)
        subsetter.subset(font)
        stream = io.BytesIO()
        font.save(stream)
        data = stream.getvalue()
        assert added <= set(font.getBestCmap())
        for sample in samples:
            assert shape(data, unicodedata.normalize("NFC", sample)) == shape(
                data, unicodedata.normalize("NFD", sample)
            )
        report["subsets"][name] = dict(
            added=[f"U+{cp:04X}" for cp in sorted(added)],
            removed=[],
            bytes=len(data),
            samples=samples,
            canonical_shaping_passed=True,
        )
    vietnamese_path = "Lib/gfsubsets/data/vietnamese_unique-glyphs.nam"
    current = (args.nam_files / vietnamese_path).read_bytes()
    original = subprocess.check_output(
        ["git", "-C", str(args.nam_files), "show", "HEAD:" + vietnamese_path]
    )
    assert current == original
    report["vietnamese_unchanged"] = True
    report["passed"] = True
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
