"""Compile committed UFO/designspace sources using the standard fontmake tool."""
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("SOURCE_DATE_EPOCH", "1788998400")
(ROOT / "build").mkdir(exist_ok=True)
subprocess.run([
        sys.executable, "-m", "fontmake",
        "-m", str(ROOT / "sources" / "SunnyMarker.designspace"),
        "-o", "variable", "--output-path",
        str(ROOT / "build" / "SunnyMarkerVariable.ttf"),
        "--no-production-names", "--keep-overlaps", "--no-autohint",
    ], cwd=ROOT, check=True, timeout=900)
