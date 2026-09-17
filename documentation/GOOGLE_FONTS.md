# Google Fonts resubmission candidate — 1.312

The initial [Sunny Marker proposal](https://github.com/google/fonts/issues/10972)
was closed for outline quality: symbols, accents and excessive points. The
[1.312 outline review](OUTLINE_REVIEW.md) documents revised drawings, construction,
shaping and visual proofs. This package is prepared for renewed design review;
it is **not an accepted Google Fonts release or a fully passing onboarding
package**. Remaining Google subset-routing failures need resolution with the
onboarding team. Published website, npm and desktop assets remain 1.310.

## Package

[Download the complete 1.312 candidate](../release/sunny-marker-googlefonts-1.312.zip).

- **391 glyphs**, including all 319 GF Latin Core codepoints.
- Separate upright and italic variable TTFs under `ofl/sunnymarker/`, with
  `wght` 300–700, `wdth` 75–125 and `opsz` 10–36 (default 14).
  The self-hosted font keeps its continuous fourth `slnt` axis, −9–0°.
  Google recommends separate styles for applications with an italic button.
- Upright **943,568 bytes**; italic **960,108 bytes**.
- OFL, METADATA.pb, article, a new specimen rendered from this candidate, and
  the specimen's CC BY-SA 4.0 image license.
- Sam Dunn's designer profile under `catalog/designers/samdunn/`, including the
  user-approved **300 × 300** portrait, stripped of embedded metadata, and a
  linked biography. The files are prepared; Google's catalog entry has not been
  registered. The portrait is separate from the font's OFL license.

Run `make review` with the README's pinned dependencies to reproduce the candidate
and verification. `make submission` only repackages an already built review font.
See [package hashes and checks](outline-review/submission-check.json).

## Current QA

**Fontspector 1.7.4**, unmodified `googlefonts` profile, 2026-09-17, with network
access and no exclusions or severity overrides:

| PASS | WARN | FAIL | SKIP | INFO | ERROR / FATAL |
| --- | --- | --- | --- | --- | --- |
| 297 | 17 | **9** | 93 | 18 | 0 / 0 |

[Full report](outline-review/googlefonts.md) ·
[Machine-readable results](outline-review/googlefonts.json)

```sh
fontspector -p googlefonts --timeout 20 \
  --json build/googlefonts.json --ghmarkdown build/googlefonts.md \
  release/googlefonts/ofl/sunnymarker/*.ttf \
  release/googlefonts/ofl/sunnymarker/METADATA.pb \
  release/googlefonts/ofl/sunnymarker/OFL.txt \
  release/googlefonts/ofl/sunnymarker/article/*
```

Independent geometry, layout, package and 92-format checks pass; all 48 outline
locations have **zero FAIL/ERROR**, with 40 disclosed warnings. FontBakery 1.1.0
also reports zero FAIL/ERROR for the general variable and static exports. Those
results do not replace the current full Fontspector profile.

## Remaining Google Fonts failures

All nine failures are `googlefonts/tofu`, code **`missing-subsetted`**. The font
contains and shapes the affected characters. Google's current `latin`/`latin-ext`
subset definitions do not route them to its web API output:

| Character | Affected sample texts |
| --- | --- |
| U+0331 COMBINING MACRON BELOW | Amarakaeri, Chickasaw, Otomi (Mezquital), Secoya, Siona, Ticuna |
| U+1EBC Ẽ / U+1EBD ẽ | Guarani, Yanomamö, Ticuna |

This was checked against Fontspector's `google-fonts-subsets 0.202602.1` and
`googlefonts/nam-files` main at `1d38a7d77ce11452ccbfe8fa9a0cb728ee6d7cd3`.
It differs from earlier 1.311 failures: those were missing font glyphs, which
have now been added and proofed.

Related upstream discussions already cover [missing combining marks](https://github.com/googlefonts/nam-files/issues/6),
[combining-mark distribution](https://github.com/googlefonts/nam-files/issues/23),
and [deriving subsets from language support](https://github.com/googlefonts/nam-files/pull/29).
The onboarding team needs to advise on subset generation or an approved exception.
The candidate does not declare unrelated script subsets, delete working characters,
or suppress these failures to obtain a passing report.

## Remaining warnings

- Subset coverage and routing: `latin-ext` is sparse, and some combining marks,
  arrows and doodles are outside the current declared web subsets.
- Optional language additions (such as Ŧ/ŧ, Ĳ/ĳ and Ʒ/ʒ), and a rupee inferred
  from Romanized Indic coverage. These are not missing Latin Core characters.
- Vendor ID `NONE` is not registered; no fabricated vendor identifier is used.
- A few sidebearings change non-monotonically between variable masters.
- Sam Dunn's designer profile is prepared but not yet in Google's catalog.

Earlier file-size, mark-class, soft-dot, naming, mathematical-width,
unreachable-glyph and contour-direction findings have been addressed. Exact
warnings and affected glyphs remain in the complete reports.

## Authorship and onboarding

Sam Dunn confirmed ownership and the right to release the entire family and
editable sources under OFL 1.1, no Reserved Font Names, no separate proprietary
edition, willingness to maintain the project, and completion of Google's CLA.
The CLA signature is maintainer-reported. The approved portrait is included with
permission for the designer profile; it is not font-source artwork.

Sam Dunn directs the design. ChatGPT was used for the original concept art, and
AI tools assisted with font engineering and QA. See [CONTRIBUTING.md](../CONTRIBUTING.md).
The historical [1.311 archive](../release/sunny-marker-googlefonts-1.311.zip) and
[report](fontspector-1.311.md) remain available for comparison, not current results.

[Designer website](https://samdunn.org) ·
[Published 1.310 specimen](https://sunnysdk.com/fonts/sunny-marker/) ·
[Google Fonts designer profile guidance](https://googlefonts.github.io/gf-guide/profile.html) ·
[Variable-family guidance](https://googlefonts.github.io/gf-guide/variable.html)
