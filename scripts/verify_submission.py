"""Verify Google's style split, archive, designer profile and actual shaping."""

import hashlib
import itertools
import json
from pathlib import Path
import zipfile
from functools import lru_cache

from fontTools.ttLib import TTFont
from PIL import Image
from gfmetadata import FamilyProto, DesignerInfoProto, text_format
import uharfbuzz as hb

ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=3)
def load_font(path):
    font = TTFont(path)
    order = font.getGlyphOrder()
    face = hb.Font(hb.Face(path.read_bytes()))
    return order, face


def shape(path, location, text):
    order, face = load_font(path)
    face.set_variations(location)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(face, buf)
    return [
        (order[g.codepoint], p.x_advance, p.x_offset, p.y_offset)
        for g, p in zip(buf.glyph_infos, buf.glyph_positions)
    ]


def main():
    root = ROOT / "release/googlefonts"
    family_dir = root / "ofl/sunnymarker"
    metadata = text_format.Parse(
        (family_dir / "METADATA.pb").read_text(), FamilyProto()
    )
    assert metadata.name == "Sunny Marker" and metadata.designer == "Sam Dunn"
    assert {f.style for f in metadata.fonts} == {"normal", "italic"}
    source = (
        ROOT / "build/outline-review/candidate/SunnyMarker[opsz,slnt,wdth,wght].ttf"
    )
    checks = 0
    samples = [
        "ÁVÁTÁR À bientôt Ąą Ęę Ľďľť",
        "i\u0307\u0301 į\u0301 j\u0308 a\u0331",
        "Ōō Ŋŋ © ® ™ 1+1=2",
    ]
    for entry in metadata.fonts:
        path = family_dir / entry.filename
        italic = entry.style == "italic"
        font = TTFont(path)
        assert {a.axisTag for a in font["fvar"].axes} == {"wght", "wdth", "opsz"}
        assert bool(font["OS/2"].fsSelection & 1) == italic
        assert font["post"].italicAngle == (-9 if italic else 0)
        assert path.stat().st_size < 1050000
        for weight, width, optical in itertools.product(
            (300, 400, 700), (75, 100, 125), (10, 14, 36)
        ):
            location = dict(wght=weight, wdth=width, opsz=optical)
            for text in samples:
                a = shape(source, dict(location, slnt=-9 if italic else 0), text)
                b = shape(path, location, text)
                assert [g[0] for g in a] == [g[0] for g in b], (
                    entry.filename,
                    location,
                    text,
                )
                assert all(
                    abs(x - y) <= 2
                    for ga, gb in zip(a, b)
                    for x, y in zip(ga[1:], gb[1:])
                ), (entry.filename, location, text)
                checks += 1
    designer = root / "catalog/designers/samdunn"
    info = text_format.Parse((designer / "info.pb").read_text(), DesignerInfoProto())
    assert info.designer == metadata.designer
    portrait = Image.open(designer / info.avatar.file_name)
    assert portrait.size == (300, 300) and not portrait.info
    assert 200 < len((designer / "bio.html").read_text()) < 1000
    assert "https://samdunn.org" in (designer / "bio.html").read_text()
    with zipfile.ZipFile(
        ROOT / "release/sunny-marker-googlefonts-1.312.zip"
    ) as archive:
        assert archive.testzip() is None
        expected = {str(p.relative_to(root)): p for p in root.rglob("*") if p.is_file()}
        assert set(archive.namelist()) == set(expected)
        assert all(archive.read(n) == p.read_bytes() for n, p in expected.items())
    report = {
        "passed": True,
        "style_split_shaping_comparisons": checks,
        "designer_profile": "Sam Dunn; approved 300px portrait; metadata-free PNG",
        "files": {
            str(p.relative_to(root)): {
                "bytes": p.stat().st_size,
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            }
            for p in sorted(root.rglob("*"))
            if p.is_file()
        },
    }
    (ROOT / "build/outline-review/submission-check.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    print(
        "PASS:", checks, "style-split comparisons, package integrity, designer profile"
    )


if __name__ == "__main__":
    main()
