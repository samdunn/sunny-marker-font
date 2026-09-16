#!/usr/bin/env python3
"""Proof the default bare-stem I against the ss01 barred alternate."""
import os
import subprocess
import tempfile
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
OUT = os.path.join(ROOT, "proofs", "i-alternate.png")

# (font, text, ss01 on)
ROWS = [
    ("SunnyMarker-Light.otf", "NEW ITEM! MINIMAL", False),
    ("SunnyMarker-Regular.otf", "NEW ITEM! MINIMAL", False),
    ("SunnyMarker-Regular.otf", "NEW ITEM! MINIMAL", True),
    ("SunnyMarker-Bold.otf", "DESIGN IT III HI", False),
    ("SunnyMarker-Bold.otf", "DESIGN IT III HI", True),
    ("SunnyMarker-Italic.otf", "IÍÎÏĪĮİÞ IJ", False),
    ("SunnyMarker-Italic.otf", "IÍÎÏĪĮİÞ IJ", True),
]
SIZE = 72
LABEL_H = 20


def render(font, text, ss01, path):
    cmd = ["hb-view", os.path.join(BUILD, font), "--text-file=-",
           f"--font-size={SIZE}", "--margin=10", "-o", path, "-O", "png"]
    if ss01:
        cmd.append("--features=ss01")
    subprocess.run(cmd, input=text.encode("utf-8"), check=True, timeout=60)
    return Image.open(path).convert("RGB")


with tempfile.TemporaryDirectory() as tmp:
    tiles = [(render(f, t, s, os.path.join(tmp, f"{i}.png")),
              f"{f.split('-')[1][:-4]}  {'ss01 (barred)' if s else 'default (bare stem)'}")
             for i, (f, t, s) in enumerate(ROWS)]
    W = max(t.width for t, _ in tiles) + 40
    H = sum(t.height + LABEL_H for t, _ in tiles) + 40
    img = Image.new("RGB", (W, H), (252, 250, 245))
    d = ImageDraw.Draw(img)
    y = 20
    for tile, label in tiles:
        d.text((20, y), label, fill=(158, 152, 140))
        img.paste(tile, (20, y + LABEL_H))
        y += tile.height + LABEL_H
    img.save(OUT)
print("wrote", OUT)
