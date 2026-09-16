# Glyph coverage and suggested additions

The atlas renders all 336 glyphs from the release, including unencoded alternates
and combining marks. The glyph names and Unicode values are in
`glyph-atlas/glyphs.json`.

## Already included

- Eight directional arrows: left, right, up, down and four diagonals.
- Filled star, outlined four-point sparkle, heart, sun, check and cross.
- Latin accents, common punctuation, currency and mathematical signs.
- Barred I alternate and Dutch j-acute composition.

## Recommended before the first public release

A small practical extension would make the font more useful for notes, room
labels and furniture measurements:

| Priority | Additions | Why |
| --- | --- | --- |
| 1 | Prime U+2032, double prime U+2033; ¼ ½ ¾ | Feet/inches, dimensions and common measurements. These should be real characters, not apostrophe/quote substitutes. |
| 1 | ↔ U+2194 and ↕ U+2195 | Dimension arrows and two-way relationships. |
| 1 | ☐ U+2610, ☑ U+2611, ☒ U+2612 | Complete the existing check/cross with a compact checklist set. |
| 2 | ↩ U+21A9 and ↪ U+21AA | Annotation and return arrows. |
| 2 | ⟲ U+27F2 and ⟳ U+27F3 | Rotation and circular movement in diagrams. |
| 2 | ☆ U+2606, ⚡ U+26A1 and ✨ U+2728 | Match the concept art's open star, lightning and sparkle cluster. |

The looping arrow and spiral in the concept art would be useful discretionary
alternates for an arrow and spiral mark; choose mappings and feature access
before drawing them. Do not map a picture to an unrelated Unicode character.

The chair, plant, box, bell and speech-bubble concept icons could form a companion
SVG set. That supports the original two-color treatment, accessible labels and
independent scaling. An optional monochrome font version can follow once the
symbol mapping and intended text fallback are clear.

These are recommendations, not implemented glyphs. The current atlas accurately
shows the characters that ship today. Every added glyph will need interpolation,
spacing, Unicode and small-size review across all supported axes.
