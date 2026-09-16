# Sunny Marker 1.310 quality verification

The family builds from 48 editable UFO masters in one four-axis designspace.
Weight, width, optical size and slant interpolate together in one variable font.
Ten named instances cover the five weights at upright and 9° slanted endpoints.
The optical axis defaults to 14; the 30 static styles remain at display size 36.

## Verified functional behavior

- All 92 font artifacts decode and pass the release checks.
- 375 sampled variable locations have monotonic width, plus all 30 static/VF
  shaping comparisons, axis limits, alternate features, clipping bounds, web ZIP
  contents and manifest hashes pass.
- Intermediate slants interpolate correctly at the width, weight and optical-size
  extremes. Cursor slopes follow the slant angle. Small-size counter relief can
  move outline points vertically by up to two units (0.2% em).
- Upright Y and all four accented Y forms pass the stem regression in every
  static style.
- Copyright and registered letters are larger relative to their rings; trademark
  is stronger, paragraph is cleaner, and section has an open central loop.
  `proofs/symbol-balance.png` shows these at 16, 24, 36 and 160 pixels in four styles.
- A common simplification mask across all 48 masters removes redundant polyline
  nodes while keeping a maximum one-unit error at every source master. See
  `source-simplification.json`. All 336 glyphs appear in the atlas and web gallery.

## Automated QA

The completed 1.310 run reports **zero FAIL and ERROR results**: 125 PASS /
9 WARN for the Google Fonts profile, and 413 PASS / 24 WARN for representative
statics. The interpolation check passes. See `quality-summary.json` for the
warning categories. These results are from FontBakery, not the newer
Fontspector checker.

`make check` runs the complete, unmodified FontBakery 1.1.0 Google Fonts profile
and representative static format checks. It enables network and interpolation
checks without suppressing check IDs. Raw reports go to ignored `qa/`; the CI
job reports completion. A timeout fails the run. Two worker processes and a
45-minute per-profile limit accommodate the four-axis interpolation analysis.

The source repository is now public. The separate **1.311 Google Fonts
onboarding candidate** corrects metadata without changing outlines, spacing,
layout or axis ranges. Fontspector 1.7.4 was run against the complete extracted
candidate, including metadata, license and article assets. It reports 148 PASS,
22 WARN, 7 FAIL, 42 SKIP and 9 INFO, with no ERROR or FATAL results. The seven
failures concern language sample strings that require three characters outside
the current coverage. See [`GOOGLE_FONTS.md`](GOOGLE_FONTS.md) for the exact
failures, remaining warnings and reproduction command. No check is suppressed.
This is an initial review candidate, not a production-ready Google Fonts package.

The font does not implement every optional orthography or a complete mathematical
symbol set. Review warnings for large variable-font size, decomposed carons,
hand-drawn mathematical widths, contour heuristics, optional dot handling and
Google Fonts subset routing. The font uses the unregistered vendor ID `NONE`.

The earlier spacing and raster regression reports describe the 1.301 → 1.302
cleanup specifically; their version fields prevent confusing those measurements
with the intentional symbol changes in 1.310.
