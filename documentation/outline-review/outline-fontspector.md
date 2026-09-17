## FontSpector report

fontspector version: 1.7.4






## Check results




<details><summary>[2] build/outline-review/verify/fonts/ttf/SunnyMarker-BoldExpandedSlanted.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any jaggy segments? (outline_jaggy_segments)</summary>
    <div>


> This check heuristically detects outline segments which form a particularly small angle, indicative of an outline error. This may cause false positives in cases such as extreme ink traps, so should be regarded as advisory and backed up by manual inspection.




Original proposal: [https://github.com/fonttools/fontbakery/issues/3064]





- ⚠️ **WARN** The following glyphs have jaggy segments:

* B (U+0042): Line(Line { p0: (457.0, 408.0), p1: (465.0, 409.0) })/Line(Line { p0: (465.0, 409.0), p1: (456.0, 409.0) }) = 7.125016348901757 degrees
* z (U+007A): Quad(QuadBez { p0: (223.0, 136.5), p1: (222.0, 135.0), p2: (218.0, 134.0) })/Quad(QuadBez { p0: (218.0, 134.0), p1: (226.0, 134.0), p2: (230.0, 134.0) }) = 14.036243467926484 degrees
* arrowright (U+2192): Quad(QuadBez { p0: (460.5, 301.0), p1: (461.0, 302.0), p2: (468.0, 303.0) })/Quad(QuadBez { p0: (468.0, 303.0), p1: (462.0, 303.0), p2: (456.5, 303.0) }) = 8.130102354156005 degrees
* arrowupright (U+2197): Line(Line { p0: (388.0, 464.0), p1: (393.0, 465.0) })/Quad(QuadBez { p0: (393.0, 465.0), p1: (387.0, 465.0), p2: (379.5, 465.0) }) = 11.309932474020195 degrees
* arrowupleft (U+2196): Line(Line { p0: (222.0, 471.0), p1: (207.0, 471.0) })/Line(Line { p0: (207.0, 471.0), p1: (211.0, 470.0) }) = 14.036243467926484 degrees
* arrowdownright (U+2198): Line(Line { p0: (295.0, 227.0), p1: (310.0, 228.0) })/Line(Line { p0: (310.0, 228.0), p1: (307.0, 228.0) }) = 3.8140748342902824 degrees
* Eogonek (U+0118): Quad(QuadBez { p0: (492.5, -46.0), p1: (485.0, -51.0), p2: (480.0, -52.0) })/Line(Line { p0: (480.0, -52.0), p1: (499.0, -52.0) }) = 11.309932474020195 degrees
* zacute (U+017A): Quad(QuadBez { p0: (217.0, 136.5), p1: (216.0, 135.0), p2: (212.0, 134.0) })/Quad(QuadBez { p0: (212.0, 134.0), p1: (220.0, 134.0), p2: (224.0, 134.0) }) = 14.036243467926484 degrees
* zdotaccent (U+017C): Quad(QuadBez { p0: (218.0, 136.5), p1: (217.0, 135.0), p2: (213.0, 134.0) })/Quad(QuadBez { p0: (213.0, 134.0), p1: (221.0, 134.0), p2: (225.0, 134.0) }) = 14.036243467926484 degrees
* zcaron (U+017E): Quad(QuadBez { p0: (217.0, 136.5), p1: (216.0, 135.0), p2: (212.0, 134.0) })/Quad(QuadBez { p0: (212.0, 134.0), p1: (220.0, 134.0), p2: (224.0, 134.0) }) = 14.036243467926484 degrees
* guilsinglleft (U+2039): Line(Line { p0: (136.0, 260.0), p1: (128.0, 259.0) })/Line(Line { p0: (128.0, 259.0), p1: (136.0, 258.0) }) = 14.250032697803546 degrees
* guillemotleft (U+00AB): Line(Line { p0: (136.0, 260.0), p1: (128.0, 259.0) })/Line(Line { p0: (128.0, 259.0), p1: (136.0, 258.0) }) = 14.250032697803546 degrees
* guillemotleft (U+00AB): Line(Line { p0: (460.0, 260.0), p1: (452.0, 259.0) })/Line(Line { p0: (452.0, 259.0), p1: (460.0, 258.0) }) = 14.250032697803546 degrees [code: found-jaggy-segments]
  
  

</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Check there are no overlapping path segments (overlapping_path_segments)</summary>
    <div>


> Some rasterizers encounter difficulties when rendering glyphs with overlapping path segments.
> 
> A path segment is a section of a path defined by two on-curve points. When two segments share the same coordinates, they are considered overlapping.




Original proposal: [https://github.com/google/fonts/issues/7594#issuecomment-2401909084]





- ⚠️ **WARN** The following glyphs have overlapping path segments:

* M (U+004D): Quad(QuadBez { p0: (503.0, 372.0), p1: (503.0, 372.0), p2: (503.0, 372.0) }) has the same coordinates as a previous segment.
* w (U+0077): Quad(QuadBez { p0: (427.0, 223.5), p1: (427.0, 224.0), p2: (427.0, 223.0) }) has the same coordinates as a previous segment.
* wcircumflex (U+0175): Quad(QuadBez { p0: (413.0, 223.5), p1: (413.0, 224.0), p2: (413.0, 223.0) }) has the same coordinates as a previous segment.
* wgrave (U+1E81): Quad(QuadBez { p0: (412.0, 223.5), p1: (412.0, 224.0), p2: (412.0, 223.0) }) has the same coordinates as a previous segment.
* wacute (U+1E83): Quad(QuadBez { p0: (412.0, 223.5), p1: (412.0, 224.0), p2: (412.0, 223.0) }) has the same coordinates as a previous segment.
* wdieresis (U+1E85): Quad(QuadBez { p0: (417.0, 223.5), p1: (417.0, 224.0), p2: (417.0, 223.0) }) has the same coordinates as a previous segment.
* trademark (U+2122): Quad(QuadBez { p0: (453.0, 497.0), p1: (453.0, 497.0), p2: (453.0, 497.0) }) has the same coordinates as a previous segment. [code: overlapping-path-segments]
  
  

</div>
</details>


</div>
</details>


<details><summary>[2] build/outline-review/verify/fonts/ttf/SunnyMarker-LightCondensed.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Check the direction of the outermost contour in each glyph (outline_direction)</summary>
    <div>


> In TrueType fonts, the outermost contour of a glyph should be oriented clockwise, while the inner contours should be oriented counter-clockwise. Getting the path direction wrong can lead to rendering issues in some software.




Original proposal: [https://github.com/fonttools/fontbakery/issues/2056]





- ⚠️ **WARN** The following glyphs have a counter-clockwise outer contour:

* ordmasculine (U+00BA) has a counter-clockwise outer contour [code: ccw-outer-contour]
  
  

</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any semi-vertical or semi-horizontal lines? (outline_semi_vertical)</summary>
    <div>


> This check detects line segments which are nearly, but not quite, exactly horizontal or vertical. Sometimes such lines are created by design, but often they are indicative of a design error.
> 
> This check is disabled for italic styles, which often contain nearly-upright lines.




Original proposal: [https://github.com/fonttools/fontbakery/pull/3088]





- ⚠️ **WARN** The following glyphs have semi-vertical/semi-horizontal lines:

* paragraph (U+00B6): Line(Line { p0: (265.0, 514.0), p1: (264.0, 652.0) }) (angle: 90.42 degrees, expected: 90.00 degrees)
* emdash (U+2014): Line(Line { p0: (500.0, 253.0), p1: (307.0, 252.0) }) (angle: -179.70 degrees, expected: -180.00 degrees) [code: found-semi-vertical]
  
  

</div>
</details>


</div>
</details>


<details><summary>[1] build/outline-review/verify/fonts/ttf/SunnyMarker-Regular.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any semi-vertical or semi-horizontal lines? (outline_semi_vertical)</summary>
    <div>


> This check detects line segments which are nearly, but not quite, exactly horizontal or vertical. Sometimes such lines are created by design, but often they are indicative of a design error.
> 
> This check is disabled for italic styles, which often contain nearly-upright lines.




Original proposal: [https://github.com/fonttools/fontbakery/pull/3088]





- ⚠️ **WARN** The following glyphs have semi-vertical/semi-horizontal lines:

* Germandbls (U+1E9E): Line(Line { p0: (160.0, 477.0), p1: (159.0, -7.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (244.0, 199.0), p1: (245.0, 52.0) }) (angle: -89.61 degrees, expected: -90.00 degrees)
* endash (U+2013): Line(Line { p0: (387.0, 248.0), p1: (252.0, 247.0) }) (angle: -179.58 degrees, expected: -180.00 degrees)
* emdash (U+2014): Line(Line { p0: (625.0, 248.0), p1: (373.0, 247.0) }) (angle: -179.77 degrees, expected: -180.00 degrees)
* minus (U+2212): Line(Line { p0: (392.0, 248.0), p1: (270.0, 247.0) }) (angle: -179.53 degrees, expected: -180.00 degrees) [code: found-semi-vertical]
  
  

</div>
</details>


</div>
</details>






### Summary

| ⚠️ WARN | ✅ PASS | ⏩ SKIP | 
| ---|---|---|
| 5 | 19 | 8 | 
| 16% | 59% | 25% | 



