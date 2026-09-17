# Sunny Marker specimens

Three reusable PNGs, each 1600 × 1200 pixels, rendered from Sunny Marker 1.313:

- `margin-notes.png`: three small, slightly rotated uppercase notes on an open background.
- `small-labels.png`: condensed lettering, numerals, and punctuation.
- `wide-open.png`: expanded display lettering and a slanted lowercase annotation.

The designs show type in context, vary scale and width, and pair with editable samples on the font page. Reference approaches: [Geist](https://vercel.com/font) and [CcTimeline](https://cctype.com/typefaces/cc-timeline). All specimen text and artwork here are original.

To regenerate from the bundled font release, install Pillow and fonttools (with Brotli support) in a Python environment, then run from the repository root:

```sh
python scripts/build_specimens.py
```

The script reads the Sunny Marker TTF inside the shipped desktop ZIP. It does not change the font binaries.
