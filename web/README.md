# Sunny Marker for the web — 1.310

This folder is a standalone marketing page and type tester. Copy it to a static
host or a directory on Sunny's website, such as `/fonts/sunny-marker/`. All assets
use relative URLs, with no server, analytics, third-party scripts, or CDN needed.
Serve this folder from your host to publish the page.

Keep `sunny-marker.css` next to `webfonts/` and retain `OFL.txt`.

```html
<link rel="stylesheet" href="/fonts/sunny-marker/sunny-marker.css">
```

```css
.handwritten {
  font-family: "Sunny Marker", sans-serif;
  font-weight: 400;           /* 300–700 */
  font-stretch: 100%;         /* 75% condensed → 125% expanded */
  font-style: oblique 4.5deg;  /* 0–9 degrees; normal is upright */
  font-optical-sizing: auto;  /* opsz 10–36, follows text size */
  font-synthesis: none;
}
```

One variable WOFF2 file contains all four axes. `font-style: italic` selects the
slanted endpoint; an explicit `oblique` angle selects an intermediate lean.
This is a continuous slant of the same letterforms. For direct OpenType control,
`font-variation-settings: "slnt" -4.5` produces a 4.5° right lean: the OpenType
sign is the reverse of CSS's angle. Keep normal CSS properties for weight and
width. For a deliberate optical size, add `"opsz" 14` and set
`font-optical-sizing: none`. The barred capital I uses
`font-feature-settings: "ss01" 1`.

Automatic optical sizing raises the lowercase body and opens counters and
spacing at smaller sizes. The tester shows “Auto” without assuming a pixel-to-point
conversion. The default Note preset starts at 24 pixels with an all-caps display. All caps / Normal changes presentation without rewriting the typed text. It preserves your text while changing presets or individual axes.

## Included pages and downloads

- `index.html`: one scrolling page with the type tester, presets, copyable CSS,
  download, and a searchable gallery of all 336 glyphs on the same page.
- `glyph-atlas/`: PNG sheets and the accessible, machine-readable glyph inventory.
- `downloads/SunnyMarker-1.310.zip`: variable TTF, WOFF2 and OFL license.
- `sunny-marker-static.css`: optional 30-style fallback family, `Sunny Marker Static`.

Static faces use optical size 36 and select the nearest available width/weight.
They are useful when one fixed style is enough; continuous controls use the
variable font. Static Italic files retain their existing names for compatibility.

## Serving

Serve WOFF2 as `font/woff2` and CSS as `text/css`. For a separate font origin, allow
the site's origin with `Access-Control-Allow-Origin`. Use a versioned directory
when setting long-lived immutable cache headers. Change it when updating fonts.

For local preview, run `python3 -m http.server 8766 --bind 127.0.0.1` in this folder
and open <http://127.0.0.1:8766>. Use a local server for clipboard-copy support.
The page can also be opened as a local file; if clipboard access is unavailable,
select and copy the displayed CSS manually.

The source repository is currently private. Publish the reviewed fresh source
snapshot before adding a public source link to the marketing page. This page
makes no claim of Google Fonts acceptance or hosting.

References: [OpenType slant axis](https://learn.microsoft.com/en-us/typography/opentype/spec/dvaraxistag_slnt),
[CSS font style ranges](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@font-face/font-style),
[automatic optical sizing](https://www.w3.org/TR/css-fonts-4/#font-optical-sizing-def).
