"""Rebuild a review candidate snapshot without replacing stable release assets.

1.314 is the archived coverage candidate. 1.315 builds from the refit outline
sources (`scripts/refine_outlines.py`) and leaves out the Gothic alphabet.
"""

import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

import package_gf

ROOT = Path(__file__).resolve().parents[1]
FILENAME = "SunnyMarker[opsz,slnt,wdth,wght].ttf"
GOTHIC = package_gf.GOTHIC
CANDIDATES = {
    "1.314": {
        "out": "build/coverage-candidate-1.314",
        "omit": {0x1EBC, 0x1EBD},
        "languages": "Latn, Goth",
    },
    "1.315": {
        "out": "build/outline-candidate-1.315",
        "omit": {0x1EBC, 0x1EBD} | GOTHIC,
        "languages": "Latn",
    },
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources-only", action="store_true")
    parser.add_argument("--version", choices=sorted(CANDIDATES), default="1.314")
    args = parser.parse_args()
    config = CANDIDATES[args.version]
    SNAPSHOT = ROOT / "candidates" / args.version
    OUT = ROOT / config["out"]
    os.environ.setdefault("SOURCE_DATE_EPOCH", "1788998400")
    OUT.mkdir(parents=True, exist_ok=True)
    archive = SNAPSHOT / "sources.zip"
    expected = (SNAPSHOT / "SHA256SUMS").read_text().splitlines()
    expected = dict(line.split("  ", 1)[::-1] for line in expected)
    if hashlib.sha256(archive.read_bytes()).hexdigest() != expected["sources.zip"]:
        raise ValueError("Source snapshot checksum mismatch")
    with zipfile.ZipFile(archive) as zipped:
        for entry in zipped.infolist():
            target = (OUT / entry.filename).resolve()
            if not target.is_relative_to(OUT.resolve() / "sources"):
                raise ValueError("Unexpected path in source snapshot")
        zipped.extractall(OUT)
    if args.sources_only:
        print(OUT / "sources")
        return
    raw = OUT / "SunnyMarkerVariable.ttf"
    subprocess.run(
        [sys.executable, "-m", "fontmake", "-m",
         str(OUT / "sources/SunnyMarker.designspace"), "-o", "variable",
         "--output-path", str(raw), "--no-production-names",
         "--keep-overlaps", "--no-autohint"],
        cwd=ROOT, check=True, timeout=900,
    )
    package_gf.VERSION = args.version
    font = package_gf.finish_variable(raw, config["omit"], config["languages"])
    font.save(OUT / FILENAME)
    font.flavor = "woff2"
    font.save(OUT / "SunnyMarker-Variable.woff2")
    shutil.copytree(SNAPSHOT / "googlefonts", OUT / "googlefonts", dirs_exist_ok=True)
    package_gf.package_google_fonts(OUT / FILENAME, OUT / "googlefonts/ofl/sunnymarker")
    print(f"Built {len(font.getGlyphOrder())} glyphs / {len(font.getBestCmap())} characters")
    print(OUT)


if __name__ == "__main__":
    main()
