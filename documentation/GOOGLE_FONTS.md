# Google Fonts onboarding candidate

Sunny Marker **1.311** is a review candidate derived from the **1.310** general
release. The website, npm package and regular desktop downloads remain 1.310.
This candidate has not been accepted into Google Fonts.

## Contents and reproducibility

- [Candidate ZIP](../release/sunny-marker-googlefonts-1.311.zip): the variable
  TTF, OFL, METADATA.pb, article and specimen in `ofl/sunnymarker/`.
- 336 glyphs; all 319 codepoints in GF Latin Core are present.
- Axes: `wght` 300–700, `wdth` 75–125, `opsz` 10–36 (default 14),
  `slnt` −9–0 degrees (default 0).
- Metadata changes: designer name and URL, unique PostScript names for all ten
  instances, SemiCondensed/SemiExpanded STAT labels, and a non-elidable optical
  size label. The internal version is incremented to 1.311.
- Binary comparison against 1.310 changes only `head`, `name`, `STAT` and `fvar`.
  Outlines, metrics, shaping/layout and axis ranges are unchanged.

Use the pinned Python environment described in the README:

```sh
./sources/build.sh
make submission
```

The first command builds the general release from editable UFO/designspace
sources using fontmake; the second creates the metadata-only review candidate.

## Current QA results

Fontspector **1.7.4**, unmodified `googlefonts` profile, was run on the complete
candidate package on 2026-09-16 with network access and no check exclusions:

| PASS | WARN | FAIL | SKIP | INFO | ERROR / FATAL |
| --- | --- | --- | --- | --- | --- |
| 148 | 22 | 7 | 42 | 9 | 0 / 0 |

See the [full report](fontspector-1.311.md) and
[machine-readable summary](googlefonts-candidate-summary.json).

```sh
fontspector -p googlefonts --timeout 20 --ghmarkdown qa/fontspector.md \
  'release/googlefonts/ofl/sunnymarker/SunnyMarker[opsz,slnt,wdth,wght].ttf' \
  release/googlefonts/ofl/sunnymarker/METADATA.pb \
  release/googlefonts/ofl/sunnymarker/OFL.txt \
  release/googlefonts/ofl/sunnymarker/article/*
```

### Remaining failures

All seven FAIL results come from `googlefonts/tofu`, code `bad-sample-text`.
The checker infers language support from base exemplars, then finds additional
characters in those languages' specimen strings that the font does not cover:

| Missing character | Affected language samples |
| --- | --- |
| U+0331 COMBINING MACRON BELOW | Amarakaeri; Otomi, Mezquital; Secoya |
| U+02BC MODIFIER LETTER APOSTROPHE | Qʼeqchiʼ; Yapese; Yucateco |
| U+014B LATIN SMALL LETTER ENG | Purepecha |

The checker suggests a sample-data inconsistency. That diagnosis has not been
independently confirmed. These are recorded for onboarding review; no test has
been disabled and these languages are not claimed as supported. We need to
resolve the sample data or add and proof the required glyphs before production
onboarding, unless Google grants an exception.

### Warnings to review

- A single `slnt` font is intentional. Google Workspace does not use this axis
  for its italic button; a separate italic companion may be needed for that
  distribution without removing the self-hosted font's continuous slant axis.
- Google Fonts subset routing and the `latin-ext` declaration need review so
  supported marks and symbols remain reachable through its API.
- Sam Dunn needs a Google Fonts designer profile and an approved photo.
- Other warnings cover the 3.72 MB variable TTF, vendor ID `NONE`, GDEF mark
  classes, WWS naming flag, soft-dot behavior, optional language/currency and
  separator coverage, `.notdef` sidebearings, mathematical widths, heart contour
  count, decomposed carons and overlapping-path heuristics. The full report
  lists the exact affected glyphs.

The earlier **FontBakery 1.1.0** run on the 1.310 release passed with no failures
or errors: 125 PASS / 9 WARN for the variable font and 413 PASS / 24 WARN for
representative statics. That does not replace current Fontspector results.
[Completed CI run](https://github.com/buildinternet/sunny-marker-font/actions/runs/35109462366).

## License, authorship and onboarding

The complete font family and editable sources use OFL 1.1 with no Reserved Font
Names. Sam Dunn confirmed ownership/right to release, no separate proprietary
edition, willingness to maintain the project during onboarding, and completion
of Google's CLA. The CLA signature is maintainer-reported.

The intended family menu name is **Sunny Marker**. Fontdata's name check found
no exact match on 2026-09-16. Sam Dunn directs the design; ChatGPT was used for
the original concept art, and AI tools assisted with font engineering and QA.
See [CONTRIBUTING.md](../CONTRIBUTING.md).

[Designer website](https://samdunn.org) ·
[Interactive specimen](https://sunnysdk.com/fonts/sunny-marker/) ·
[Google Fonts onboarding guide](https://googlefonts.github.io/gf-guide/onboarding.html)
