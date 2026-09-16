#!/usr/bin/env python3
"""Build the entire release from the committed UFO/designspace sources."""
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('SOURCE_DATE_EPOCH', '1788998400')
for name in ('build_ufos.py', 'package_gf.py'):
    subprocess.run([sys.executable, '-u', str(ROOT / 'scripts' / name)],
                   cwd=ROOT, check=True, timeout=900)
