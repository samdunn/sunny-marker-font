#!/usr/bin/env python3
"""Render proof PNGs using the built OTF."""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, "build", "SunnyMarker-Regular.otf")
PROOFS = os.path.join(ROOT, "proofs")

LINES = [
    ("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 64),
    ("abcdefghijklmnopqrstuvwxyz", 64),
    ("0123456789", 64),
    ("!?.,:;\"'()[]{}/\\-_+=@#$%&*<>", 64),
    ("→ ↗ ↑ ↖ ← ↘ ↓ ↙ ★ ✧ ♡ ☀ ✓ ✗", 64),
    ("“Don’t forget to add a little sunshine.”", 56),
    ("ROOM READY! POP! YOU GOT THIS!", 56),
    ("New item: small table lamp ✓ warm light ✓ cozy vibes", 44),
    ("The quick brown fox jumps over the lazy dog.", 44),
]

pad = 48
line_gap = 30
imgs = []
widths = []
total_h = pad
for text, size in LINES:
    f = ImageFont.truetype(FONT, size)
    bbox = f.getbbox(text)
    widths.append(bbox[2] + 2 * pad)
    total_h += (bbox[3] - min(bbox[1], 0)) + line_gap

W = max(widths)
H = total_h + pad
img = Image.new("RGB", (W, H), (252, 250, 245))
d = ImageDraw.Draw(img)
y = pad
for text, size in LINES:
    f = ImageFont.truetype(FONT, size)
    bbox = f.getbbox(text)
    d.text((pad, y - min(bbox[1], 0)), text, font=f, fill=(20, 20, 20))
    y += (bbox[3] - min(bbox[1], 0)) + line_gap
out = os.path.join(PROOFS, "specimen-v1.png")
img.save(out)
print("wrote", out, img.size)
