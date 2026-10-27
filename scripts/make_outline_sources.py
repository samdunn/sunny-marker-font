"""Make the 1.315 sources from the archived 1.314 sources.

1. Extract and checksum candidates/1.314/sources.zip.
2. Point the font info's URLs at github.com/samdunn/sunny-marker-font.
3. Refit the outlines (refine_outlines.py, 6-unit tolerance).
4. Redraw the vertical caron as a marker stroke (redraw_vertical_caron.py).
5. Write candidates/1.315/sources.zip and its checksum line.

Every step is deterministic, so running this again reproduces sources.zip
byte for byte. Reports go to build/outline-refit/.
"""
import hashlib
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "build/outline-refit"
SOURCES = WORK / "sources"
ARCHIVE = ROOT / "candidates/1.315/sources.zip"
SUMS = ROOT / "candidates/1.315/SHA256SUMS"
OLD_URL = "github.com/buildinternet/sunny-marker-font"
NEW_URL = "github.com/samdunn/sunny-marker-font"
TOLERANCE = "6"


def run(*args):
    subprocess.run([sys.executable, *args], cwd=ROOT / "scripts", check=True)


def main():
    run("build_coverage_candidate.py", "--version", "1.314", "--sources-only")
    if SOURCES.exists():
        shutil.rmtree(SOURCES)
    WORK.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT / "build/coverage-candidate-1.314/sources", SOURCES)
    for info in SOURCES.glob("*.ufo/fontinfo.plist"):
        info.write_text(info.read_text().replace(OLD_URL, NEW_URL))

    run("refine_outlines.py", str(SOURCES), "--tolerance", TOLERANCE,
        "--report", str(WORK / "refine-outlines.json"))
    run("redraw_vertical_caron.py", str(SOURCES), "--report", str(WORK / "vertical-caron.json"))

    files = sorted(p for p in SOURCES.rglob("*") if p.is_file() and p.name != ".DS_Store")
    with zipfile.ZipFile(ARCHIVE, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zipped:
        for path in files:
            info = zipfile.ZipInfo(str(path.relative_to(WORK)), date_time=(2026, 10, 27, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zipped.writestr(info, path.read_bytes())
    digest = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
    lines = [l for l in SUMS.read_text().splitlines() if not l.endswith("  sources.zip")] if SUMS.exists() else []
    SUMS.write_text("\n".join(sorted(lines + [f"{digest}  sources.zip"], key=lambda l: l.split("  ", 1)[1])) + "\n")
    print(f"{ARCHIVE.relative_to(ROOT)}  {digest}")


if __name__ == "__main__":
    main()
