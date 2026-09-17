# Outline quality review

Status: development work following the initial Google Fonts rejection.
The published website, npm package and downloads remain 1.310. No revised
candidate has been sent to the reviewer yet.

The [review](https://github.com/google/fonts/issues/10972#issuecomment-5714431859)
cited symbols, accents and excessive outline points. Automated packaging and
interpolation checks do not replace a review of the drawings.

## Construction changes

- Generated polylines are now fitted with cubic curves before fontmake compiles
  them to compatible TrueType curves. A common segmentation is validated against
  all 48 masters, with a two-unit sampled fit tolerance (1000 units per em),
  including a reverse check along the curves between original vertices.
  Sharp reference corners and reference extrema remain endpoints. This retains
  the irregular marker shape while removing many unnecessary vertices.
- Reversing a symbol's winding now reverses the curves correctly. The previous
  code treated control handles as outline vertices, which could introduce
  artificial angular edges in overlaid shapes.
- Accent and symbol placement uses the actual curved ink bounds, rather than
  the bounding box of the control handles. Top accents share an ink-based gap.
- Circumflex and caron joins use a clean rounded stroke instead of intersecting
  sampled offsets. Ogoneks use a curved hook. Uppercase Lcaron uses its proper
  side mark, alongside dcaron, lcaron and tcaron.
- Generated marker strokes use actual rounded joins and normalized contours.
  The lower- and uppercase sharp S are redrawn with continuous curves and open
  lower terminals; the previous angular skeletons produced pinholes at joins.
- At small optical sizes, detached marks follow their base's actual height
  change. Marks over ascenders no longer receive the full x-height translation.

## Reproduce the review

Install the pinned environment from the README, including Potrace 1.16 for source
regeneration. The committed release binaries provide the comparison baseline.

```sh
mkdir -p build/outline-review
cp 'fonts/variable/SunnyMarker[opsz,slnt,wdth,wght].ttf' build/outline-review/before.ttf
make sources
python scripts/test_outline_geometry.py
python scripts/build_ufos.py
python scripts/package_outline_review.py
python scripts/verify_outline_review.py \
  build/outline-review/before.ttf \
  'build/outline-review/candidate/SunnyMarker[opsz,slnt,wdth,wght].ttf' \
  build/outline-review/geometry-check.json --raw-masters build/vf-masters
python scripts/proof_outline_review.py \
  build/outline-review/before.ttf \
  'build/outline-review/candidate/SunnyMarker[opsz,slnt,wdth,wght].ttf' \
  build/outline-review/proofs
```

`package_outline_review.py` writes a development font under `build/` only. It
does not replace shipped fonts, downloads, npm contents or website assets.

## Proofs and measured results

![Before and after](outline-review/before-after.png)

![Outline point comparison](outline-review/outline-points.png)

Full glyph plates: [1](outline-review/glyphs-01.png),
[2](outline-review/glyphs-02.png), [3](outline-review/glyphs-03.png),
[4](outline-review/glyphs-04.png). These show the actual candidate outlines.

- Compiled outline points: **63,565 → 34,350**, a 46% reduction.
- 336 glyphs and the same character coverage and four axis ranges.
- 375 shaping locations passed; 51 complete-glyph bounds locations (all 48
  source-master positions plus three intermediate positions) had no clipping. Continuous slant and capital-Y regression checks passed, with three
  representative static faces checked for the Y regression.
- Five source-geometry regression tests passed.
- 1,005 independently sampled glyph/master comparisons found a maximum edge
  deviation of **2.88 font units** from the newly generated raw design masters
  after simplification, fitting, compilation and rounding. This measures the
  approximation stage, not the intentional changes from the old drawings.
- Targeted Fontspector 1.7.4 outline/interpolation checks on the variable font
  and three static instances: **19 PASS, 5 WARN, 8 SKIP, 0 FAIL/ERROR**. The
  variable font itself had no warnings in these selected checks. This is not
  a run of the complete Google Fonts onboarding profile.
- Bandit and the pinned Gitleaks scan found no reported issues in the tested
  source tree; Gitleaks also checked the local public-repository history.

See [geometry measurements](outline-review/geometry-check.json),
[Fontspector detail](outline-review/outline-fontspector.md), and
[source curve-fitting measurements](curve-fitting.json).

## Remaining acceptance work

This is a construction improvement, not a claim of Google Fonts readiness.
The five static-sample warnings cover narrow Light contour direction and
near-horizontal segments; near-horizontal segments in Regular; and jagged or
overlapping segments in expanded slanted Bold. These need glyph-by-glyph review,
especially B/z, arrow joins, and M/w at that extreme. No checks were disabled to
make those findings disappear. The full report lists the affected glyphs.
The remaining work includes visual review of the complete symbol and accent
set across axes, review of node placement and joins, consistent accented-letter
spacing, and resolution of the previously documented combining-mark and
language-coverage findings. Those findings remain in
[the onboarding report](GOOGLE_FONTS.md).

References: [Google Fonts outline quality](https://googlefonts.github.io/gf-guide/outlines),
[diacritic requirements](https://googlefonts.github.io/gf-guide/diacritics.html),
and [Glyphs: drawing good paths](https://glyphsapp.com/learn/drawing-good-paths).
