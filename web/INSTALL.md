# Sunny Marker

A handwritten variable font for little notes, labels, headings and playful interfaces.
One self-hosted WOFF2 contains all four axes and 336 glyphs. Font version 1.310;
package version 1.310.0. Free for personal and commercial use under the SIL OFL 1.1.

## Install in your project

Run this from the app or package folder where you want to use the font:

```sh
npm install @sunnyai/sunny-marker
```

Install locally as a project dependency. A global install (`npm install -g`)
will not make the package available to your app’s imports or register a desktop font.
In a pnpm workspace, add it to the app that consumes it.

Also works with `pnpm add @sunnyai/sunny-marker`, `yarn add @sunnyai/sunny-marker` and
`bun add @sunnyai/sunny-marker`. The same package is available as a versioned tarball
from the [Sunny website](https://sunnysdk.com/fonts/sunny-marker/downloads/sunnyai-sunny-marker-1.310.0.tgz).

## Any CSS bundler (Vite, React, Vue, Svelte, Astro)

Import once in your app's entry point or global stylesheet:

```js
import "@sunnyai/sunny-marker/css";
```

```html
<span class="sunny-marker note">A LITTLE NOTE GOES A LONG WAY.</span>
```

```css
.note {
  font-size: 18px;
  font-weight: 500;
  font-stretch: 85%;
  font-style: oblique 0deg;
}
```

You can also apply `font-family: "Sunny Marker", cursive` directly. The stylesheet
defines the font and one optional utility class; it does not change global type.
Keep `font-optical-sizing: auto` and `font-synthesis: none` on your own classes.

## Next.js

Use the optional `next/font/local` entry point instead of the CSS import:

```jsx
import { SunnyMarker } from "@sunnyai/sunny-marker/next";
import "./globals.css";

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={SunnyMarker.variable}>
      <body>{children}</body>
    </html>
  );
}
```

```css
.note {
  font-family: var(--font-sunny-marker), cursive;
  font-optical-sizing: auto;
  font-synthesis: none;
  font-size: 18px;
  font-weight: 500;
  font-stretch: 85%;
  font-style: oblique 0deg;
}
```

`SunnyMarker.className` is also available. Next.js is an optional peer dependency;
CSS users do not install it. Preloading is off because annotations usually do not
need a page-wide font preload. The host app serves the font; no external font
request or runtime library is required.

## Desktop apps (Font Book, design tools and documents)

[Download the desktop font ZIP](https://sunnysdk.com/fonts/sunny-marker/downloads/SunnyMarker-1.310.zip),
extract it, and install `SunnyMarker[opsz,slnt,wdth,wght].ttf`. On macOS, open the
TTF in Font Book and choose Install. No WOFF2 conversion is needed.

The npm package supplies WOFF2 for browsers; the ZIP includes the TTF for desktop
apps. Both contain the same four-axis font. Available axis controls depend on
the app. The single variable font covers upright through slanted styles.

## Variable controls

| Control      | CSS                         | Range           |
| ------------ | --------------------------- | --------------- |
| Weight       | `font-weight`               | 300–700         |
| Width        | `font-stretch`              | 75%–125%        |
| Slant        | `font-style: oblique 6deg`  | 0–9° right lean |
| Optical size | `font-optical-sizing: auto` | 10–36           |

For direct axis control, use `font-variation-settings: "wght" 500, "wdth" 85,
"slnt" -6, "opsz" 18`. Positive CSS oblique angles correspond to negative `slnt`
values. The font has slanted letterforms; it does not contain a separate cursive
italic design. Case is controlled by your text or CSS `text-transform`.

The raw font is exported at `@sunnyai/sunny-marker/files/SunnyMarker-Variable.woff2`.
The package contains no install scripts, telemetry, runtime dependencies, source
history or Sunny brand artwork. Keep `OFL.txt` with redistributed font files.

[Try the font and browse every glyph](https://sunnysdk.com/fonts/sunny-marker/).

## Desktop formats: both are OpenType

- [Variable desktop (.ttf)](downloads/SunnyMarker-1.310.zip): one OpenType font with TrueType outlines and all four adjustable axes.
- [Static desktop (.otf)](downloads/SunnyMarker-Static-OTF-1.310.zip): 30 fixed styles with CFF outlines, useful when an application does not expose variable controls.
- WOFF2 is the compressed browser format. Installing the npm package does not install a desktop font.

The `.ttf` extension does not mean the variable font lacks OpenType features.
The [OpenType specification](https://learn.microsoft.com/en-us/typography/opentype/spec/otff#filenames) supports both `.ttf` and `.otf`.
