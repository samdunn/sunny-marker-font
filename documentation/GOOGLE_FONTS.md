# Google Fonts resubmission candidate — 1.313

**Historical 1.313 results.** The newer [1.314 candidate](../candidates/1.314/)
resolves these checker failures through font-side repertoire changes and has
zero recorded failures/errors. It does not depend on an upstream patch. Its
report covers the separate browser-delivery limitation and remaining warnings.

The initial [Sunny Marker proposal](https://github.com/google/fonts/issues/10972)
was closed for outline quality: symbols, accents and excessive points. The
[1.313 outline review](OUTLINE_REVIEW.md) documents revised drawings, construction,
shaping and visual proofs. This package is prepared locally for renewed design review;
it is **not an accepted Google Fonts release or a fully passing onboarding
package**. Remaining Google subset-routing failures need an upstream routing
change or an approved onboarding approach. No contact with Google or submission has been made
for this revision. The same outlines are packaged for the general 1.313 release.

## Package

[Download the complete 1.313 candidate](../release/sunny-marker-googlefonts-1.313.zip).

- **391 glyphs**, including all 319 GF Latin Core codepoints.
- Separate upright and italic variable TTFs under `ofl/sunnymarker/`, with
  `wght` 300–700, `wdth` 75–125 and `opsz` 10–36 (default 14).
  The self-hosted font keeps its continuous fourth `slnt` axis, −9–0°.
  Google recommends separate styles for applications with an italic button.
- Upright **920,248 bytes**; italic **938,472 bytes**.
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
| 281 | 12 | **9** | 69 | 16 | 0 / 0 |

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

Independent geometry, layout, package and 92-format checks pass. All **84**
evaluated outline locations have **zero warnings, failures or errors**. These
outline results do not replace the full Google Fonts profile above.

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
A [minimal three-character routing patch](subset-proposal/README.md) is prepared
and tested **locally only**. It adds U+0331 to Latin and Latin Extended, retains
Ẽ/ẽ in Latin Extended, and leaves Vietnamese unchanged. Actual subset binaries
pass HarfBuzz mark-shaping and canonical-equivalence tests. This does not alter
Fontspector or Google's service; the official nine failures remain. The maintainer
requested no contact, so the draft has not been submitted.
The candidate does not declare unrelated script subsets, delete working characters,
or suppress these failures to obtain a passing report.

## Remaining warnings

- Subset coverage and routing: `latin-ext` is sparse, and some combining marks,
  arrows and doodles are outside the current declared web subsets.
- Optional language additions (Ŧ/ŧ, Ǿ/ǿ, Ĳ/ĳ, ſ, Ŀ/ŀ, Ǥ/ǥ, Ʒ/ʒ, Ǯ/ǯ).
  These auxiliary characters are not missing Latin Core requirements. They remain
  a possible future coverage expansion, not newly claimed support.
- Missing ₹: the [official rupee check](https://github.com/fonttools/fontspector/blob/main/profile-universal/src/checks/rupee.rs)
  warns for any non-Indic font without it. This is not evidence of broken existing
  characters. Adding it would be a separate drawing and proofing task.
- Vendor ID `NONE` is not registered; no fabricated vendor identifier is used.
- Only `space` retains the statistical sidebearing warning. Its advance changes
  deliberately with the width axis. The earlier accented-letter warnings were
  resolved by stable accent centering.
- Sam Dunn's designer profile is prepared but not yet in Google's catalog.

Earlier file-size, mark-class, soft-dot, naming, mathematical-width,
unreachable-glyph, contour-direction and local outline findings have been addressed.
The remaining warnings are disclosed, not suppressed. [Google's QA guidance](https://googlefonts.github.io/gf-guide/qa.html) treats
warnings as review items; neither an automated pass nor this report guarantees
design acceptance. Exact warnings and affected glyphs remain in the complete reports.

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
[Sunny Marker specimen](https://sunnysdk.com/fonts/sunny-marker/) ·
[Google Fonts designer profile guidance](https://googlefonts.github.io/gf-guide/profile.html) ·
[Variable-family guidance](https://googlefonts.github.io/gf-guide/variable.html)
