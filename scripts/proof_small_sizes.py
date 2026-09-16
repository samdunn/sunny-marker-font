#!/usr/bin/env python3
"""Proof the actual shipped VF at small sizes; optional before/after comparison."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
AFTER = ROOT / 'fonts/variable/SunnyMarker[opsz,slnt,wdth,wght].ttf'
BEFORE = Path('/private/tmp/sunny-marker-before/upright.ttf')


def main():
    img = Image.new('RGB', (1440, 1240), '#faf8f0')
    draw = ImageDraw.Draw(img)
    label = ImageFont.load_default(size=17)
    title = ImageFont.load_default(size=25)
    draw.text((36, 25), 'SUNNY MARKER / SMALL-SIZE & WEIGHT REFINEMENT', font=title, fill='#25251f')
    columns = [('Previous weight range', BEFORE), ('Refined weight range', AFTER)] if BEFORE.exists() else [('Refined weight range', AFTER)]
    for ci, (heading, path) in enumerate(columns):
        x = 36 + ci * 700
        draw.text((x, 85), heading, font=title, fill='#935134')
        y = 138
        for weight in (300, 400, 700):
            draw.text((x, y), f'Weight {weight} · 48 px · normal width', font=label, fill='#66675e')
            face = ImageFont.truetype(str(path), 48)
            face.set_variation_by_axes([weight, 100, 36] + ([0] if path == AFTER else []))
            draw.text((x, y + 22), 'Hello, sunshine! Aaeg', font=face, fill='#22231d')
            y += 118
        for size in (16, 20, 24, 32):
            draw.text((x, y), f'Regular · {size} px · opsz {min(36, size)}', font=label, fill='#66675e')
            face = ImageFont.truetype(str(path), size)
            face.set_variation_by_axes([400, 100, min(36, max(10, size))] + ([0] if path == AFTER else []))
            draw.text((x, y + 30), 'Room ready. Warm white · $299 · Add to room', font=face, fill='#22231d')
            y += 94
        draw.text((x, y), 'Condensed Bold · 20 px · opsz 20', font=label, fill='#66675e')
        face = ImageFont.truetype(str(path), 20)
        face.set_variation_by_axes([700, 75, 20] + ([0] if path == AFTER else []))
        draw.text((x, y + 30), 'MAKE ROOM. A B D O P R 8 9 · café · sunshine', font=face, fill='#22231d')
        y += 90
        draw.text((x, y), 'Light · 24 px · opsz 24', font=label, fill='#66675e')
        face = ImageFont.truetype(str(path), 24)
        face.set_variation_by_axes([300, 100, 24] + ([0] if path == AFTER else []))
        draw.text((x, y + 30), 'Little details. Ilij! À bientôt · Çç Şş', font=face, fill='#22231d')
    out = ROOT / 'proofs/small-size-refinement.png'
    img.save(out)
    print(out)


if __name__ == '__main__':
    main()
