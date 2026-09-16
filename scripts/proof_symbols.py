"""Render the shipped symbols at reading and display sizes across the family."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from package_gf import VERSION

ROOT = Path(__file__).resolve().parents[1]
NAMES = ('CondensedLight', 'Regular', 'Bold', 'ExtendedBoldItalic')
TEXT = '@ § ¶ © ® ™'

def main():
    image = Image.new('RGB', (1680, 1120), '#faf8f1')
    draw = ImageDraw.Draw(image)
    label = ImageFont.load_default(size=22)
    title = ImageFont.load_default(size=36)
    draw.text((48, 30), f'SUNNY MARKER {VERSION} / SYMBOL BALANCE', font=title, fill='#20231f')
    for i, name in enumerate(NAMES):
        y = 110+i*245
        draw.text((48, y), name.replace('Italic', ' Italic'), font=label, fill='#65685f')
        path = ROOT/'fonts/ttf'/f'SunnyMarker-{name}.ttf'
        face = ImageFont.truetype(str(path), 160)
        draw.text((350, y-22), TEXT, font=face, fill='#20231f')
        for j, size in enumerate((16, 24, 36)):
            draw.text((350+j*370, y+148), f'{size} px', font=label, fill='#65685f')
            draw.text((430+j*370, y+140), TEXT, font=ImageFont.truetype(str(path), size), fill='#20231f')
    path = ROOT/'proofs/symbol-balance.png'
    image.save(path)
    print(path)

if __name__ == '__main__':
    main()
