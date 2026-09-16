#!/usr/bin/env python3
"""Run the unmodified Google Fonts profile and static format checks.

No check exclusions or severity overrides. A timeout fails the command instead
of silently presenting an incomplete run as a pass. Network checks are enabled.
"""
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'qa'
OUT.mkdir(exist_ok=True)
GROUPS = {
    'googlefonts': ('check-googlefonts', sorted((ROOT / 'fonts/variable').glob('*.ttf'))),
    'static': ('check-universal', [ROOT / 'fonts/ttf' / name for name in (
        'SunnyMarker-CondensedLight.ttf', 'SunnyMarker-CondensedBoldItalic.ttf',
        'SunnyMarker-Regular.ttf', 'SunnyMarker-Italic.ttf',
        'SunnyMarker-ExtendedLight.ttf', 'SunnyMarker-ExtendedBoldItalic.ttf')]),
}
failed = False
summary = {}
for group, (profile, paths) in GROUPS.items():
    report = OUT / f'fontbakery-{group}.json'
    with (OUT / f'fontbakery-{group}.log').open('w') as log:
        try:
            result = subprocess.run([
                sys.executable, '-m', 'fontbakery', profile, '-n', '-J', '2', '--timeout', '15',
                '--json', str(report), *map(str, paths)],
                cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, timeout=2700)
            failed |= result.returncode != 0
            summary[group] = json.loads(report.read_text())['result'] if report.exists() else {'ERROR': 1}
        except subprocess.TimeoutExpired:
            failed = True
            summary[group] = {'ERROR': 'Timed out; the profile did not complete'}
    print(group, summary[group], flush=True)
(OUT / 'quality-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
sys.exit(1 if failed else 0)
