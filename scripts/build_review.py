"""Build and verify the resubmission candidate without publishing anything."""

from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/outline-review"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    before = OUT / "before.ttf"
    if not before.exists():
        shutil.copyfile(
            ROOT / "fonts/variable/SunnyMarker[opsz,slnt,wdth,wght].ttf", before
        )
    candidate = OUT / "candidate/SunnyMarker[opsz,slnt,wdth,wght].ttf"
    steps = [
        ["test_outline_geometry.py"],
        ["build_ufos.py"],
        ["package_outline_review.py"],
        [
            "verify_outline_review.py",
            before,
            candidate,
            OUT / "geometry-check.json",
            "--source-masters",
            ROOT / "sources",
        ],
        ["verify_layout.py", candidate, OUT / "layout-check.json"],
        ["proof_outline_review.py", before, candidate, OUT / "proofs"],
        ["proof_resubmission.py", candidate, ROOT / "build/resubmission-review"],
        ["package_submission.py"],
        ["verify_submission.py"],
    ]
    for name, *arguments in steps:
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / name), *map(str, arguments)],
            cwd=ROOT,
            check=True,
            timeout=900,
        )


if __name__ == "__main__":
    main()
