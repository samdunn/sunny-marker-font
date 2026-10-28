"""Check the built fonts and make the Google Fonts package, without publishing.

Run sources/build.sh first; this reads the fonts it writes to fonts/.
"""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
FONT = ROOT / "fonts/variable/SunnyMarker[opsz,slnt,wdth,wght].ttf"


def main():
    steps = [
        ["test_outline_geometry.py"],
        ["verify_layout.py", FONT, ROOT / "build/layout-check.json"],
        ["package_submission.py"],
        ["verify_submission.py"],
    ]
    (ROOT / "build").mkdir(exist_ok=True)
    for name, *arguments in steps:
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / name), *map(str, arguments)],
            cwd=ROOT,
            check=True,
            timeout=1800,
        )


if __name__ == "__main__":
    main()
