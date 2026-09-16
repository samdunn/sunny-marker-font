# Sunny Marker

A flexible handwritten marker family for labels, notes, headings, and playful
interfaces. Continuous weight, width, slant and optical size keep the same warm,
irregular character across compact labels and large display type.

![Sunny Marker — handwritten, variable, made for little notes](web/specimens/github-header.png)

[Try the font](https://sunnysdk.com/fonts/sunny-marker/) · [View specimens](https://sunnysdk.com/fonts/sunny-marker/#specimens) · [Browse all 336 glyphs](https://sunnysdk.com/fonts/sunny-marker/#glyphs)

## Use the fonts

```sh
npm install @sunnyai/sunny-marker
```

```js
import "@sunnyai/sunny-marker/css";
```

Install inside your project. For Next.js, use the optional
[`@sunnyai/sunny-marker/next` loader](packages/sunny-marker/README.md).

### Downloads and formats

Version **1.310** includes a four-axis OpenType variable font and 30 matching static styles.

| Download | What it contains |
| --- | --- |
| [Variable desktop (.ttf)](web/downloads/SunnyMarker-1.310.zip) | One OpenType font with TrueType outlines; adjustable weight, width, slant, and optical size. The ZIP also includes its WOFF2 and license. |
| [Static desktop (.otf)](web/downloads/SunnyMarker-Static-OTF-1.310.zip) | 30 fixed OpenType styles with CFF outlines, plus the license. |
| [Web package](release/sunny-marker-web-1.310.zip) | WOFF2 files, CSS, and a standalone type tester. |

**TTF is OpenType too.** The file extension describes the outline format; it does
not determine whether a font is variable or supports OpenType features. Our
variable font uses TrueType outlines. The `.otf` exports are fixed styles, useful
for applications that do not expose variable controls. See the
[OpenType specification](https://learn.microsoft.com/en-us/typography/opentype/spec/otff#filenames).

For a plain HTML page, copy [`web/`](web/) into your public assets:

```html
<link rel="stylesheet" href="/fonts/sunny-marker/sunny-marker.css">
```

```css
.marker {
  font-family: "Sunny Marker", cursive;
  font-weight: 400;
  font-stretch: 100%;
  font-style: oblique 0deg;   /* 0–9° right lean */
  font-optical-sizing: auto;
  font-synthesis: none;
}
```

| Axis | Minimum | Default | Maximum |
| --- | --- | --- | --- |
| Weight `wght` | 300 Light | 400 Regular | 700 Bold |
| Width `wdth` | 75 Condensed | 100 Normal | 125 Expanded |
| Optical size `opsz` | 10 | 14 | 36 |
| Slant `slnt` | -9° right lean | 0° upright | 0° |

The variable font has ten named instances: five weights at upright and slanted endpoints. Width and slant remain continuously
adjustable. Static styles use display optical size 36. At smaller optical sizes,
lowercase letters grow taller and spacing opens. Slant moves continuously from upright to a 9° right lean in the same file.

The family contains **336 glyphs**, including Latin accents, punctuation,
currencies, eight directional arrows, a sun, star, sparkle, heart, check and cross.
Capital Y has an upright lower stem. Capital I has a bare stem by default;
`ss01` or `salt` selects its barred alternate. Dutch j-acute uses `ccmp`.

See [`documentation/glyph-atlas/`](documentation/glyph-atlas/) for the complete
glyph inventory and rendered plates, and [`web/README.md`](web/README.md) for
integration details. `make preview` opens a local specimen server on port 8766.

## Install in a project

See [`packages/sunny-marker/README.md`](packages/sunny-marker/README.md) for npm,
CSS and Next.js imports. `make npm` (Node.js 24 required) builds and checks the
allowlisted installable archive in `web/downloads/`. It includes one variable
WOFF2, CSS, an optional Next.js loader, setup documentation and the OFL.

## Build from editable sources

Python 3.13 is the tested environment. Use a virtual environment:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip==26.2.1
python -m pip install -r requirements-qa.txt
make build
make verify
make check
make audit
```

`make build` compiles committed UFO/designspace sources with fontmake, then
packages matching desktop/web fonts, metadata, checksums and a deterministic ZIP.
`make check` runs the unmodified Google Fonts FontBakery profile, including its
network and interpolation checks. Timeouts are errors, not passing results.

The original drawing pipeline remains available: install Potrace 1.16 and run
`make sources` to regenerate the UFOs from the reference artwork and Python
geometry code. This replaces direct UFO edits. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

`SOURCE_DATE_EPOCH` defaults to the project's fixed release epoch. Pinned build
tools and source files support repeatable builds. Generated intermediates,
private configuration and raw audit logs are ignored by Git.

## Google Fonts review

Submitted for initial review in [google/fonts#10972](https://github.com/google/fonts/issues/10972).

The [1.311 onboarding candidate](release/sunny-marker-googlefonts-1.311.zip)
adds Google Fonts metadata to the 1.310 variable font. It has identical outlines,
spacing, layout tables and axis ranges. The website and npm package remain on
the general release, **1.310**.

Run `make submission` after building to reproduce the candidate. Google's
current Fontspector checks identified remaining language-sample failures and
warnings that need onboarding review; this is not an accepted Google Fonts
release. See [the candidate report](documentation/GOOGLE_FONTS.md).

## Project files

- `sources/`: editable UFO masters and designspaces.
- `scripts/`: source generation, fontmake build, packaging and verification.
- `fonts/`: released fonts plus a SHA-256 manifest.
- `web/`: standalone marketing page, type tester, glyph gallery and downloads.
- `references/` and `glyphs/manifest.json`: original drawing inputs.
- `documentation/`: quality results, glyph atlas and release guidance.

## License and credits

Copyright 2026 The Sunny Marker Project Authors. All font styles, sources and build
materials use the **SIL Open Font License 1.1**, with no Reserved Font Names.
See [`OFL.txt`](OFL.txt), [`AUTHORS.txt`](AUTHORS.txt), and
[`CONTRIBUTORS.txt`](CONTRIBUTORS.txt). Documents made with the font do not need
to use the OFL.

Designed and maintained by Sam Dunn, with AI-assisted concept development and
font engineering. See the contribution guide for provenance and attribution.

Sunny brand artwork in `web/branding/` is separate from the font software.
See its `NOTICE.txt`; it is excluded from the npm package.
