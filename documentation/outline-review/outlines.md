## FontSpector report

fontspector version: 1.7.4






## Check results




<details><summary>[1] build/resubmission-review/final/instances/w400-d100-o36-s0.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any semi-vertical or semi-horizontal lines? (outline_semi_vertical)</summary>
    <div>


> This check detects line segments which are nearly, but not quite, exactly horizontal or vertical. Sometimes such lines are created by design, but often they are indicative of a design error.
> 
> This check is disabled for italic styles, which often contain nearly-upright lines.




Original proposal: [https://github.com/fonttools/fontbakery/pull/3088]





- ⚠️ **WARN** The following glyphs have semi-vertical/semi-horizontal lines:

* M (U+004D): Line(Line { p0: (531.0, 564.0), p1: (532.0, 315.0) }) (angle: -89.77 degrees, expected: -90.00 degrees)
* arrowup (U+2191): Line(Line { p0: (227.0, 371.0), p1: (226.0, 167.0) }) (angle: -90.28 degrees, expected: -90.00 degrees)
* Germandbls (U+1E9E): Line(Line { p0: (160.0, 472.0), p1: (159.0, -7.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (160.0, 60.0), p1: (161.0, 637.0) }) (angle: 89.90 degrees, expected: 90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (244.0, 578.0), p1: (245.0, 77.0) }) (angle: -89.89 degrees, expected: -90.00 degrees)
* trademark (U+2122): Line(Line { p0: (604.0, 643.0), p1: (605.0, 496.0) }) (angle: -89.61 degrees, expected: -90.00 degrees)
* emdash (U+2014): Line(Line { p0: (214.0, 314.0), p1: (365.0, 315.0) }) (angle: 0.38 degrees, expected: 0.00 degrees) [code: found-semi-vertical]
  
  

</div>
</details>


</div>
</details>


<details><summary>[2] build/resubmission-review/final/instances/w400-d75-o10-s0.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Check there are no overlapping path segments (overlapping_path_segments)</summary>
    <div>


> Some rasterizers encounter difficulties when rendering glyphs with overlapping path segments.
> 
> A path segment is a section of a path defined by two on-curve points. When two segments share the same coordinates, they are considered overlapping.




Original proposal: [https://github.com/google/fonts/issues/7594#issuecomment-2401909084]





- ⚠️ **WARN** The following glyphs have overlapping path segments:

* trademark (U+2122): Quad(QuadBez { p0: (430.0, 534.0), p1: (430.0, 534.0), p2: (430.0, 534.0) }) has the same coordinates as a previous segment. [code: overlapping-path-segments]
  
  

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

* M (U+004D): Line(Line { p0: (337.0, 149.0), p1: (338.0, 282.0) }) (angle: 89.57 degrees, expected: 90.00 degrees)
* arrowup (U+2191): Line(Line { p0: (206.0, 356.0), p1: (205.0, 162.0) }) (angle: -90.30 degrees, expected: -90.00 degrees)
* arrowdown (U+2193): Line(Line { p0: (199.0, 470.0), p1: (200.0, 326.0) }) (angle: -89.60 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (217.0, 579.0), p1: (218.0, 80.0) }) (angle: -89.89 degrees, expected: -90.00 degrees) [code: found-semi-vertical]
  
  

</div>
</details>


</div>
</details>


<details><summary>[1] build/resubmission-review/final/instances/w400-d125-o36-s0.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any semi-vertical or semi-horizontal lines? (outline_semi_vertical)</summary>
    <div>


> This check detects line segments which are nearly, but not quite, exactly horizontal or vertical. Sometimes such lines are created by design, but often they are indicative of a design error.
> 
> This check is disabled for italic styles, which often contain nearly-upright lines.




Original proposal: [https://github.com/fonttools/fontbakery/pull/3088]





- ⚠️ **WARN** The following glyphs have semi-vertical/semi-horizontal lines:

* M (U+004D): Line(Line { p0: (630.0, 565.0), p1: (631.0, 315.0) }) (angle: -89.77 degrees, expected: -90.00 degrees)
* Germandbls (U+1E9E): Line(Line { p0: (165.0, 516.0), p1: (164.0, -7.0) }) (angle: -90.11 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (220.0, 564.0), p1: (219.0, 382.0) }) (angle: -90.31 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (198.0, 60.0), p1: (199.0, 637.0) }) (angle: 89.90 degrees, expected: 90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (282.0, 578.0), p1: (283.0, 77.0) }) (angle: -89.89 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (398.0, 72.0), p1: (397.0, 639.0) }) (angle: 90.10 degrees, expected: 90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (482.0, 627.0), p1: (481.0, 138.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* trademark (U+2122): Line(Line { p0: (727.0, 640.0), p1: (728.0, 496.0) }) (angle: -89.60 degrees, expected: -90.00 degrees)
* emdash (U+2014): Line(Line { p0: (261.0, 314.0), p1: (446.0, 315.0) }) (angle: 0.31 degrees, expected: 0.00 degrees) [code: found-semi-vertical]
  
  

</div>
</details>


</div>
</details>


<details><summary>[1] build/resubmission-review/final/instances/w500-d100-o36-s0.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any semi-vertical or semi-horizontal lines? (outline_semi_vertical)</summary>
    <div>


> This check detects line segments which are nearly, but not quite, exactly horizontal or vertical. Sometimes such lines are created by design, but often they are indicative of a design error.
> 
> This check is disabled for italic styles, which often contain nearly-upright lines.




Original proposal: [https://github.com/fonttools/fontbakery/pull/3088]





- ⚠️ **WARN** The following glyphs have semi-vertical/semi-horizontal lines:

* arrowup (U+2191): Line(Line { p0: (235.0, 367.0), p1: (234.0, 163.0) }) (angle: -90.28 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (158.0, 64.0), p1: (159.0, 638.0) }) (angle: 89.90 degrees, expected: 90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (249.0, 574.0), p1: (250.0, 76.0) }) (angle: -89.88 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (407.0, 628.0), p1: (406.0, 142.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* emdash (U+2014): Line(Line { p0: (209.0, 318.0), p1: (359.0, 319.0) }) (angle: 0.38 degrees, expected: 0.00 degrees) [code: found-semi-vertical]
  
  

</div>
</details>


</div>
</details>


<details><summary>[1] build/resubmission-review/final/instances/w700-d125-o10-s0.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any semi-vertical or semi-horizontal lines? (outline_semi_vertical)</summary>
    <div>


> This check detects line segments which are nearly, but not quite, exactly horizontal or vertical. Sometimes such lines are created by design, but often they are indicative of a design error.
> 
> This check is disabled for italic styles, which often contain nearly-upright lines.




Original proposal: [https://github.com/fonttools/fontbakery/pull/3088]





- ⚠️ **WARN** The following glyphs have semi-vertical/semi-horizontal lines:

* Germandbls (U+1E9E): Line(Line { p0: (222.0, 509.0), p1: (221.0, 6.0) }) (angle: -90.11 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (229.0, 71.0), p1: (230.0, 640.0) }) (angle: 89.90 degrees, expected: 90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (331.0, 568.0), p1: (332.0, 74.0) }) (angle: -89.88 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (421.0, 69.0), p1: (420.0, 628.0) }) (angle: 90.10 degrees, expected: 90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (523.0, 629.0), p1: (522.0, 148.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* emdash (U+2014): Line(Line { p0: (290.0, 324.0), p1: (471.0, 325.0) }) (angle: 0.32 degrees, expected: 0.00 degrees) [code: found-semi-vertical]
  
  

</div>
</details>


</div>
</details>


<details><summary>[1] build/resubmission-review/final/instances/w700-d75-o10-s0.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any semi-vertical or semi-horizontal lines? (outline_semi_vertical)</summary>
    <div>


> This check detects line segments which are nearly, but not quite, exactly horizontal or vertical. Sometimes such lines are created by design, but often they are indicative of a design error.
> 
> This check is disabled for italic styles, which often contain nearly-upright lines.




Original proposal: [https://github.com/fonttools/fontbakery/pull/3088]





- ⚠️ **WARN** The following glyphs have semi-vertical/semi-horizontal lines:

* M (U+004D): Line(Line { p0: (323.0, 137.0), p1: (324.0, 264.0) }) (angle: 89.55 degrees, expected: 90.00 degrees)
* arrowup (U+2191): Line(Line { p0: (222.0, 358.0), p1: (221.0, 155.0) }) (angle: -90.28 degrees, expected: -90.00 degrees)
* arrowupleft (U+2196): Line(Line { p0: (47.0, 360.0), p1: (46.0, 476.0) }) (angle: 90.49 degrees, expected: 90.00 degrees)
* arrowdown (U+2193): Line(Line { p0: (217.0, 478.0), p1: (218.0, 330.0) }) (angle: -89.61 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (136.0, 71.0), p1: (137.0, 637.0) }) (angle: 89.90 degrees, expected: 90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (229.0, 568.0), p1: (230.0, 77.0) }) (angle: -89.88 degrees, expected: -90.00 degrees) [code: found-semi-vertical]
  
  

</div>
</details>


</div>
</details>


<details><summary>[1] build/resubmission-review/final/instances/w300-d125-o36-s0.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any semi-vertical or semi-horizontal lines? (outline_semi_vertical)</summary>
    <div>


> This check detects line segments which are nearly, but not quite, exactly horizontal or vertical. Sometimes such lines are created by design, but often they are indicative of a design error.
> 
> This check is disabled for italic styles, which often contain nearly-upright lines.




Original proposal: [https://github.com/fonttools/fontbakery/pull/3088]





- ⚠️ **WARN** The following glyphs have semi-vertical/semi-horizontal lines:

* Germandbls (U+1E9E): Line(Line { p0: (155.0, 519.0), p1: (154.0, -15.0) }) (angle: -90.11 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (211.0, 566.0), p1: (210.0, 391.0) }) (angle: -90.33 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (202.0, 53.0), p1: (203.0, 635.0) }) (angle: 89.90 degrees, expected: 90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (276.0, 584.0), p1: (277.0, 79.0) }) (angle: -89.89 degrees, expected: -90.00 degrees)
* emdash (U+2014): Line(Line { p0: (265.0, 308.0), p1: (453.0, 309.0) }) (angle: 0.30 degrees, expected: 0.00 degrees) [code: found-semi-vertical]
  
  

</div>
</details>


</div>
</details>


<details><summary>[1] build/resubmission-review/final/instances/w300-d75-o10-s0.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any semi-vertical or semi-horizontal lines? (outline_semi_vertical)</summary>
    <div>


> This check detects line segments which are nearly, but not quite, exactly horizontal or vertical. Sometimes such lines are created by design, but often they are indicative of a design error.
> 
> This check is disabled for italic styles, which often contain nearly-upright lines.




Original proposal: [https://github.com/fonttools/fontbakery/pull/3088]





- ⚠️ **WARN** The following glyphs have semi-vertical/semi-horizontal lines:

* M (U+004D): Line(Line { p0: (437.0, 558.0), p1: (438.0, 314.0) }) (angle: -89.77 degrees, expected: -90.00 degrees)
* arrowdown (U+2193): Line(Line { p0: (190.0, 462.0), p1: (191.0, 315.0) }) (angle: -89.61 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (265.0, 76.0), p1: (264.0, 646.0) }) (angle: 90.10 degrees, expected: 90.00 degrees)
* emdash (U+2014): Line(Line { p0: (187.0, 306.0), p1: (302.0, 307.0) }) (angle: 0.50 degrees, expected: 0.00 degrees) [code: found-semi-vertical]
  
  

</div>
</details>


</div>
</details>


<details><summary>[2] build/resubmission-review/final/instances/w700-d75-o36-s9.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any jaggy segments? (outline_jaggy_segments)</summary>
    <div>


> This check heuristically detects outline segments which form a particularly small angle, indicative of an outline error. This may cause false positives in cases such as extreme ink traps, so should be regarded as advisory and backed up by manual inspection.




Original proposal: [https://github.com/fonttools/fontbakery/issues/3064]





- ⚠️ **WARN** The following glyphs have jaggy segments:

* sparkle (U+2727): Quad(QuadBez { p0: (244.5, 490.0), p1: (244.0, 490.0), p2: (245.0, 496.0) })/Line(Line { p0: (245.0, 496.0), p1: (243.0, 489.0) }) = 6.483073692897206 degrees
* sparkle (U+2727): Quad(QuadBez { p0: (200.0, 219.0), p1: (200.0, 212.0), p2: (199.0, 204.0) })/Line(Line { p0: (199.0, 204.0), p1: (201.0, 210.0) }) = 11.309932474020227 degrees [code: found-jaggy-segments]
  
  

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

* Dcroat (U+0110): Quad(QuadBez { p0: (164.5, 156.5), p1: (164.0, 156.0), p2: (164.0, 157.0) }) has the same coordinates as a previous segment. [code: overlapping-path-segments]
  
  

</div>
</details>


</div>
</details>


<details><summary>[2] build/resubmission-review/final/instances/w400-d75-o36-s0.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Check there are no overlapping path segments (overlapping_path_segments)</summary>
    <div>


> Some rasterizers encounter difficulties when rendering glyphs with overlapping path segments.
> 
> A path segment is a section of a path defined by two on-curve points. When two segments share the same coordinates, they are considered overlapping.




Original proposal: [https://github.com/google/fonts/issues/7594#issuecomment-2401909084]





- ⚠️ **WARN** The following glyphs have overlapping path segments:

* trademark (U+2122): Quad(QuadBez { p0: (408.0, 534.0), p1: (408.0, 534.0), p2: (408.0, 534.0) }) has the same coordinates as a previous segment. [code: overlapping-path-segments]
  
  

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

* arrowup (U+2191): Line(Line { p0: (183.0, 356.0), p1: (182.0, 162.0) }) (angle: -90.30 degrees, expected: -90.00 degrees)
* arrowdown (U+2193): Line(Line { p0: (177.0, 470.0), p1: (178.0, 326.0) }) (angle: -89.60 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (194.0, 579.0), p1: (195.0, 80.0) }) (angle: -89.89 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (315.0, 625.0), p1: (314.0, 137.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* trademark (U+2122): Line(Line { p0: (472.0, 643.0), p1: (473.0, 496.0) }) (angle: -89.61 degrees, expected: -90.00 degrees)
* emdash (U+2014): Line(Line { p0: (159.0, 314.0), p1: (275.0, 315.0) }) (angle: 0.49 degrees, expected: 0.00 degrees) [code: found-semi-vertical]
  
  

</div>
</details>


</div>
</details>


<details><summary>[3] build/resubmission-review/final/instances/w700-d75-o36-s0.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any jaggy segments? (outline_jaggy_segments)</summary>
    <div>


> This check heuristically detects outline segments which form a particularly small angle, indicative of an outline error. This may cause false positives in cases such as extreme ink traps, so should be regarded as advisory and backed up by manual inspection.




Original proposal: [https://github.com/fonttools/fontbakery/issues/3064]





- ⚠️ **WARN** The following glyphs have jaggy segments:

* sparkle (U+2727): Quad(QuadBez { p0: (219.5, 220.0), p1: (221.0, 213.0), p2: (222.0, 204.0) })/Line(Line { p0: (222.0, 204.0), p1: (222.0, 210.0) }) = 6.340191745909966 degrees [code: found-jaggy-segments]
  
  

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

* ampersand (U+0026): Quad(QuadBez { p0: (231.0, 213.0), p1: (231.0, 213.0), p2: (231.0, 219.0) }) has the same coordinates as a previous segment. [code: overlapping-path-segments]
  
  

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

* M (U+004D): Line(Line { p0: (301.0, 137.0), p1: (302.0, 264.0) }) (angle: 89.55 degrees, expected: 90.00 degrees)
* arrowup (U+2191): Line(Line { p0: (200.0, 358.0), p1: (199.0, 155.0) }) (angle: -90.28 degrees, expected: -90.00 degrees)
* arrowdown (U+2193): Line(Line { p0: (194.0, 478.0), p1: (195.0, 330.0) }) (angle: -89.61 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (229.0, 72.0), p1: (228.0, 628.0) }) (angle: 90.10 degrees, expected: 90.00 degrees) [code: found-semi-vertical]
  
  

</div>
</details>


</div>
</details>


<details><summary>[1] build/resubmission-review/final/instances/w400-d125-o10-s9.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any jaggy segments? (outline_jaggy_segments)</summary>
    <div>


> This check heuristically detects outline segments which form a particularly small angle, indicative of an outline error. This may cause false positives in cases such as extreme ink traps, so should be regarded as advisory and backed up by manual inspection.




Original proposal: [https://github.com/fonttools/fontbakery/issues/3064]





- ⚠️ **WARN** The following glyphs have jaggy segments:

* star (U+2605): Quad(QuadBez { p0: (421.5, 621.5), p1: (430.0, 629.0), p2: (434.0, 638.0) })/Quad(QuadBez { p0: (434.0, 638.0), p1: (433.0, 634.0), p2: (441.5, 621.0) }) = 9.926245506651707 degrees [code: found-jaggy-segments]
  
  

</div>
</details>


</div>
</details>


<details><summary>[1] build/resubmission-review/final/instances/w400-d125-o10-s0.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any semi-vertical or semi-horizontal lines? (outline_semi_vertical)</summary>
    <div>


> This check detects line segments which are nearly, but not quite, exactly horizontal or vertical. Sometimes such lines are created by design, but often they are indicative of a design error.
> 
> This check is disabled for italic styles, which often contain nearly-upright lines.




Original proposal: [https://github.com/fonttools/fontbakery/pull/3088]





- ⚠️ **WARN** The following glyphs have semi-vertical/semi-horizontal lines:

* germandbls (U+00DF): Line(Line { p0: (193.0, 456.0), p1: (192.0, -7.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* Germandbls (U+1E9E): Line(Line { p0: (203.0, 516.0), p1: (202.0, -7.0) }) (angle: -90.11 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (319.0, 578.0), p1: (320.0, 77.0) }) (angle: -89.89 degrees, expected: -90.00 degrees) [code: found-semi-vertical]
  
  

</div>
</details>


</div>
</details>


<details><summary>[1] build/resubmission-review/final/instances/w300-d125-o10-s0.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any semi-vertical or semi-horizontal lines? (outline_semi_vertical)</summary>
    <div>


> This check detects line segments which are nearly, but not quite, exactly horizontal or vertical. Sometimes such lines are created by design, but often they are indicative of a design error.
> 
> This check is disabled for italic styles, which often contain nearly-upright lines.




Original proposal: [https://github.com/fonttools/fontbakery/pull/3088]





- ⚠️ **WARN** The following glyphs have semi-vertical/semi-horizontal lines:

* M (U+004D): Line(Line { p0: (667.0, 562.0), p1: (668.0, 314.0) }) (angle: -89.77 degrees, expected: -90.00 degrees)
* Germandbls (U+1E9E): Line(Line { p0: (193.0, 519.0), p1: (192.0, -15.0) }) (angle: -90.11 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (313.0, 584.0), p1: (314.0, 79.0) }) (angle: -89.89 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (444.0, 74.0), p1: (443.0, 646.0) }) (angle: 90.10 degrees, expected: 90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (518.0, 625.0), p1: (517.0, 132.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* trademark (U+2122): Line(Line { p0: (775.0, 643.0), p1: (776.0, 499.0) }) (angle: -89.60 degrees, expected: -90.00 degrees)
* emdash (U+2014): Line(Line { p0: (305.0, 306.0), p1: (492.0, 307.0) }) (angle: 0.31 degrees, expected: 0.00 degrees) [code: found-semi-vertical]
  
  

</div>
</details>


</div>
</details>


<details><summary>[2] build/resubmission-review/final/instances/w500-d75-o10-s0.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Check there are no overlapping path segments (overlapping_path_segments)</summary>
    <div>


> Some rasterizers encounter difficulties when rendering glyphs with overlapping path segments.
> 
> A path segment is a section of a path defined by two on-curve points. When two segments share the same coordinates, they are considered overlapping.




Original proposal: [https://github.com/google/fonts/issues/7594#issuecomment-2401909084]





- ⚠️ **WARN** The following glyphs have overlapping path segments:

* W (U+0057): Quad(QuadBez { p0: (359.0, 284.0), p1: (359.0, 282.0), p2: (359.0, 281.5) }) has the same coordinates as a previous segment.
* W (U+0057): Quad(QuadBez { p0: (359.0, 281.5), p1: (359.0, 281.0), p2: (359.0, 281.0) }) has the same coordinates as a previous segment.
* m (U+006D): Quad(QuadBez { p0: (166.0, 427.0), p1: (166.0, 427.0), p2: (166.0, 428.0) }) has the same coordinates as a previous segment.
* arrowdownleft (U+2199): Line(Line { p0: (119.0, 287.0), p1: (119.0, 288.0) }) has the same coordinates as a previous segment.
* Wcircumflex (U+0174): Quad(QuadBez { p0: (359.0, 284.0), p1: (359.0, 282.0), p2: (359.0, 281.5) }) has the same coordinates as a previous segment.
* Wcircumflex (U+0174): Quad(QuadBez { p0: (359.0, 281.5), p1: (359.0, 281.0), p2: (359.0, 281.0) }) has the same coordinates as a previous segment.
* Wgrave (U+1E80): Quad(QuadBez { p0: (359.0, 284.0), p1: (359.0, 282.0), p2: (359.0, 281.5) }) has the same coordinates as a previous segment.
* Wgrave (U+1E80): Quad(QuadBez { p0: (359.0, 281.5), p1: (359.0, 281.0), p2: (359.0, 281.0) }) has the same coordinates as a previous segment.
* Wacute (U+1E82): Quad(QuadBez { p0: (359.0, 284.0), p1: (359.0, 282.0), p2: (359.0, 281.5) }) has the same coordinates as a previous segment.
* Wacute (U+1E82): Quad(QuadBez { p0: (359.0, 281.5), p1: (359.0, 281.0), p2: (359.0, 281.0) }) has the same coordinates as a previous segment.
* Wdieresis (U+1E84): Quad(QuadBez { p0: (359.0, 284.0), p1: (359.0, 282.0), p2: (359.0, 281.5) }) has the same coordinates as a previous segment.
* Wdieresis (U+1E84): Quad(QuadBez { p0: (359.0, 281.5), p1: (359.0, 281.0), p2: (359.0, 281.0) }) has the same coordinates as a previous segment. [code: overlapping-path-segments]
  
  

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

* h (U+0068): Line(Line { p0: (342.0, 248.0), p1: (341.0, 132.0) }) (angle: -90.49 degrees, expected: -90.00 degrees)
* arrowup (U+2191): Line(Line { p0: (212.0, 341.0), p1: (211.0, 154.0) }) (angle: -90.31 degrees, expected: -90.00 degrees)
* arrowdown (U+2193): Line(Line { p0: (207.0, 480.0), p1: (208.0, 341.0) }) (angle: -89.59 degrees, expected: -90.00 degrees)
* Germandbls (U+1E9E): Line(Line { p0: (169.0, 431.0), p1: (168.0, -2.0) }) (angle: -90.13 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (191.0, 564.0), p1: (190.0, 378.0) }) (angle: -90.31 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (222.0, 574.0), p1: (223.0, 78.0) }) (angle: -89.88 degrees, expected: -90.00 degrees)
* hcaron (U+021F): Line(Line { p0: (342.0, 248.0), p1: (341.0, 132.0) }) (angle: -90.49 degrees, expected: -90.00 degrees) [code: found-semi-vertical]
  
  

</div>
</details>


</div>
</details>


<details><summary>[1] build/resubmission-review/final/instances/w300-d100-o36-s0.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any semi-vertical or semi-horizontal lines? (outline_semi_vertical)</summary>
    <div>


> This check detects line segments which are nearly, but not quite, exactly horizontal or vertical. Sometimes such lines are created by design, but often they are indicative of a design error.
> 
> This check is disabled for italic styles, which often contain nearly-upright lines.




Original proposal: [https://github.com/fonttools/fontbakery/pull/3088]





- ⚠️ **WARN** The following glyphs have semi-vertical/semi-horizontal lines:

* Germandbls (U+1E9E): Line(Line { p0: (149.0, 475.0), p1: (148.0, -15.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (188.0, 566.0), p1: (187.0, 390.0) }) (angle: -90.33 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (237.0, 584.0), p1: (238.0, 79.0) }) (angle: -89.89 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (327.0, 74.0), p1: (326.0, 646.0) }) (angle: 90.10 degrees, expected: 90.00 degrees)
* emdash (U+2014): Line(Line { p0: (217.0, 308.0), p1: (369.0, 309.0) }) (angle: 0.38 degrees, expected: 0.00 degrees) [code: found-semi-vertical]
  
  

</div>
</details>


</div>
</details>


<details><summary>[3] build/resubmission-review/final/instances/w500-d75-o36-s0.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any jaggy segments? (outline_jaggy_segments)</summary>
    <div>


> This check heuristically detects outline segments which form a particularly small angle, indicative of an outline error. This may cause false positives in cases such as extreme ink traps, so should be regarded as advisory and backed up by manual inspection.




Original proposal: [https://github.com/fonttools/fontbakery/issues/3064]





- ⚠️ **WARN** The following glyphs have jaggy segments:

* sparkle (U+2727): Quad(QuadBez { p0: (217.0, 215.5), p1: (219.0, 208.0), p2: (221.0, 199.0) })/Line(Line { p0: (221.0, 199.0), p1: (221.0, 205.0) }) = 12.528807709151492 degrees [code: found-jaggy-segments]
  
  

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

* W (U+0057): Quad(QuadBez { p0: (336.0, 282.0), p1: (336.0, 280.0), p2: (336.0, 279.5) }) has the same coordinates as a previous segment.
* W (U+0057): Quad(QuadBez { p0: (336.0, 279.5), p1: (336.0, 279.0), p2: (336.0, 279.0) }) has the same coordinates as a previous segment.
* four (U+0034): Quad(QuadBez { p0: (188.0, 430.0), p1: (188.0, 430.0), p2: (188.0, 430.0) }) has the same coordinates as a previous segment.
* arrowdownleft (U+2199): Line(Line { p0: (97.0, 287.0), p1: (97.0, 288.0) }) has the same coordinates as a previous segment.
* Wcircumflex (U+0174): Quad(QuadBez { p0: (336.0, 282.0), p1: (336.0, 280.0), p2: (336.0, 279.5) }) has the same coordinates as a previous segment.
* Wcircumflex (U+0174): Quad(QuadBez { p0: (336.0, 279.5), p1: (336.0, 279.0), p2: (336.0, 279.0) }) has the same coordinates as a previous segment.
* Wgrave (U+1E80): Quad(QuadBez { p0: (336.0, 282.0), p1: (336.0, 280.0), p2: (336.0, 279.5) }) has the same coordinates as a previous segment.
* Wgrave (U+1E80): Quad(QuadBez { p0: (336.0, 279.5), p1: (336.0, 279.0), p2: (336.0, 279.0) }) has the same coordinates as a previous segment.
* Wacute (U+1E82): Quad(QuadBez { p0: (336.0, 282.0), p1: (336.0, 280.0), p2: (336.0, 279.5) }) has the same coordinates as a previous segment.
* Wacute (U+1E82): Quad(QuadBez { p0: (336.0, 279.5), p1: (336.0, 279.0), p2: (336.0, 279.0) }) has the same coordinates as a previous segment.
* Wdieresis (U+1E84): Quad(QuadBez { p0: (336.0, 282.0), p1: (336.0, 280.0), p2: (336.0, 279.5) }) has the same coordinates as a previous segment.
* Wdieresis (U+1E84): Quad(QuadBez { p0: (336.0, 279.5), p1: (336.0, 279.0), p2: (336.0, 279.0) }) has the same coordinates as a previous segment. [code: overlapping-path-segments]
  
  

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

* M (U+004D): Line(Line { p0: (309.0, 150.0), p1: (310.0, 284.0) }) (angle: 89.57 degrees, expected: 90.00 degrees)
* arrowup (U+2191): Line(Line { p0: (190.0, 341.0), p1: (189.0, 154.0) }) (angle: -90.31 degrees, expected: -90.00 degrees)
* arrowdown (U+2193): Line(Line { p0: (184.0, 480.0), p1: (185.0, 341.0) }) (angle: -89.59 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (318.0, 626.0), p1: (317.0, 142.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* emdash (U+2014): Line(Line { p0: (156.0, 318.0), p1: (271.0, 319.0) }) (angle: 0.50 degrees, expected: 0.00 degrees) [code: found-semi-vertical]
  
  

</div>
</details>


</div>
</details>


<details><summary>[1] build/resubmission-review/final/instances/w700-d125-o36-s0.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any semi-vertical or semi-horizontal lines? (outline_semi_vertical)</summary>
    <div>


> This check detects line segments which are nearly, but not quite, exactly horizontal or vertical. Sometimes such lines are created by design, but often they are indicative of a design error.
> 
> This check is disabled for italic styles, which often contain nearly-upright lines.




Original proposal: [https://github.com/fonttools/fontbakery/pull/3088]





- ⚠️ **WARN** The following glyphs have semi-vertical/semi-horizontal lines:

* M (U+004D): Line(Line { p0: (631.0, 569.0), p1: (632.0, 316.0) }) (angle: -89.77 degrees, expected: -90.00 degrees)
* Germandbls (U+1E9E): Line(Line { p0: (185.0, 509.0), p1: (184.0, 6.0) }) (angle: -90.11 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (192.0, 71.0), p1: (193.0, 640.0) }) (angle: 89.90 degrees, expected: 90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (293.0, 568.0), p1: (294.0, 74.0) }) (angle: -89.88 degrees, expected: -90.00 degrees)
* trademark (U+2122): Line(Line { p0: (710.0, 636.0), p1: (711.0, 490.0) }) (angle: -89.61 degrees, expected: -90.00 degrees)
* emdash (U+2014): Line(Line { p0: (251.0, 325.0), p1: (432.0, 326.0) }) (angle: 0.32 degrees, expected: 0.00 degrees) [code: found-semi-vertical]
  
  

</div>
</details>


</div>
</details>


<details><summary>[1] build/resubmission-review/final/instances/w300-d100-o10-s0.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any semi-vertical or semi-horizontal lines? (outline_semi_vertical)</summary>
    <div>


> This check detects line segments which are nearly, but not quite, exactly horizontal or vertical. Sometimes such lines are created by design, but often they are indicative of a design error.
> 
> This check is disabled for italic styles, which often contain nearly-upright lines.




Original proposal: [https://github.com/fonttools/fontbakery/pull/3088]





- ⚠️ **WARN** The following glyphs have semi-vertical/semi-horizontal lines:

* Germandbls (U+1E9E): Line(Line { p0: (179.0, 475.0), p1: (178.0, -15.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (218.0, 566.0), p1: (217.0, 390.0) }) (angle: -90.33 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (267.0, 584.0), p1: (268.0, 79.0) }) (angle: -89.89 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (357.0, 74.0), p1: (356.0, 646.0) }) (angle: 90.10 degrees, expected: 90.00 degrees)
* emdash (U+2014): Line(Line { p0: (248.0, 306.0), p1: (399.0, 307.0) }) (angle: 0.38 degrees, expected: 0.00 degrees) [code: found-semi-vertical]
  
  

</div>
</details>


</div>
</details>


<details><summary>[1] build/resubmission-review/final/instances/w700-d100-o36-s9.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Check there are no overlapping path segments (overlapping_path_segments)</summary>
    <div>


> Some rasterizers encounter difficulties when rendering glyphs with overlapping path segments.
> 
> A path segment is a section of a path defined by two on-curve points. When two segments share the same coordinates, they are considered overlapping.




Original proposal: [https://github.com/google/fonts/issues/7594#issuecomment-2401909084]





- ⚠️ **WARN** The following glyphs have overlapping path segments:

* four (U+0034): Quad(QuadBez { p0: (282.0, 437.0), p1: (282.0, 437.0), p2: (282.0, 437.0) }) has the same coordinates as a previous segment. [code: overlapping-path-segments]
  
  

</div>
</details>


</div>
</details>


<details><summary>[1] build/resubmission-review/final/instances/w400-d75-o36-s9.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Check there are no overlapping path segments (overlapping_path_segments)</summary>
    <div>


> Some rasterizers encounter difficulties when rendering glyphs with overlapping path segments.
> 
> A path segment is a section of a path defined by two on-curve points. When two segments share the same coordinates, they are considered overlapping.




Original proposal: [https://github.com/google/fonts/issues/7594#issuecomment-2401909084]





- ⚠️ **WARN** The following glyphs have overlapping path segments:

* trademark (U+2122): Quad(QuadBez { p0: (404.0, 534.0), p1: (404.0, 534.0), p2: (404.0, 534.0) }) has the same coordinates as a previous segment. [code: overlapping-path-segments]
  
  

</div>
</details>


</div>
</details>


<details><summary>[2] build/resubmission-review/final/instances/w500-d75-o36-s9.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any jaggy segments? (outline_jaggy_segments)</summary>
    <div>


> This check heuristically detects outline segments which form a particularly small angle, indicative of an outline error. This may cause false positives in cases such as extreme ink traps, so should be regarded as advisory and backed up by manual inspection.




Original proposal: [https://github.com/fonttools/fontbakery/issues/3064]





- ⚠️ **WARN** The following glyphs have jaggy segments:

* sparkle (U+2727): Quad(QuadBez { p0: (197.0, 215.0), p1: (198.0, 208.0), p2: (198.0, 199.0) })/Line(Line { p0: (198.0, 199.0), p1: (199.0, 205.0) }) = 9.462322208025574 degrees
* ordfeminine (U+00AA): Quad(QuadBez { p0: (134.5, 415.0), p1: (135.0, 419.0), p2: (135.0, 420.0) })/Quad(QuadBez { p0: (135.0, 420.0), p1: (134.0, 416.0), p2: (133.5, 415.5) }) = 14.036243467926484 degrees [code: found-jaggy-segments]
  
  

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

* W (U+0057): Quad(QuadBez { p0: (339.0, 279.5), p1: (339.0, 279.0), p2: (339.0, 279.0) }) has the same coordinates as a previous segment.
* four (U+0034): Quad(QuadBez { p0: (219.0, 430.0), p1: (219.0, 430.0), p2: (219.0, 430.0) }) has the same coordinates as a previous segment.
* Wcircumflex (U+0174): Quad(QuadBez { p0: (339.0, 279.5), p1: (339.0, 279.0), p2: (339.0, 279.0) }) has the same coordinates as a previous segment.
* Wgrave (U+1E80): Quad(QuadBez { p0: (339.0, 279.5), p1: (339.0, 279.0), p2: (339.0, 279.0) }) has the same coordinates as a previous segment.
* Wacute (U+1E82): Quad(QuadBez { p0: (339.0, 279.5), p1: (339.0, 279.0), p2: (339.0, 279.0) }) has the same coordinates as a previous segment.
* Wdieresis (U+1E84): Quad(QuadBez { p0: (339.0, 279.5), p1: (339.0, 279.0), p2: (339.0, 279.0) }) has the same coordinates as a previous segment. [code: overlapping-path-segments]
  
  

</div>
</details>


</div>
</details>


<details><summary>[1] build/resubmission-review/final/instances/w700-d100-o10-s0.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any semi-vertical or semi-horizontal lines? (outline_semi_vertical)</summary>
    <div>


> This check detects line segments which are nearly, but not quite, exactly horizontal or vertical. Sometimes such lines are created by design, but often they are indicative of a design error.
> 
> This check is disabled for italic styles, which often contain nearly-upright lines.




Original proposal: [https://github.com/fonttools/fontbakery/pull/3088]





- ⚠️ **WARN** The following glyphs have semi-vertical/semi-horizontal lines:

* M (U+004D): Line(Line { p0: (566.0, 568.0), p1: (567.0, 316.0) }) (angle: -89.77 degrees, expected: -90.00 degrees)
* M (U+004D): Line(Line { p0: (428.0, 134.0), p1: (429.0, 262.0) }) (angle: 89.55 degrees, expected: 90.00 degrees)
* arrowdown (U+2193): Line(Line { p0: (268.0, 483.0), p1: (269.0, 342.0) }) (angle: -89.59 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (185.0, 71.0), p1: (186.0, 640.0) }) (angle: 89.90 degrees, expected: 90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (287.0, 568.0), p1: (288.0, 73.0) }) (angle: -89.88 degrees, expected: -90.00 degrees)
* emdash (U+2014): Line(Line { p0: (237.0, 324.0), p1: (384.0, 325.0) }) (angle: 0.39 degrees, expected: 0.00 degrees) [code: found-semi-vertical]
  
  

</div>
</details>


</div>
</details>


<details><summary>[2] build/resubmission-review/final/instances/w500-d75-o10-s9.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any jaggy segments? (outline_jaggy_segments)</summary>
    <div>


> This check heuristically detects outline segments which form a particularly small angle, indicative of an outline error. This may cause false positives in cases such as extreme ink traps, so should be regarded as advisory and backed up by manual inspection.




Original proposal: [https://github.com/fonttools/fontbakery/issues/3064]





- ⚠️ **WARN** The following glyphs have jaggy segments:

* g (U+0067): Line(Line { p0: (204.0, 43.0), p1: (204.0, 44.0) })/Line(Line { p0: (204.0, 44.0), p1: (203.0, 40.0) }) = 14.036243467926484 degrees
* gbreve (U+011F): Line(Line { p0: (204.0, 43.0), p1: (204.0, 44.0) })/Line(Line { p0: (204.0, 44.0), p1: (203.0, 40.0) }) = 14.036243467926484 degrees
* gdotaccent (U+0121): Line(Line { p0: (204.0, 43.0), p1: (204.0, 44.0) })/Line(Line { p0: (204.0, 44.0), p1: (203.0, 40.0) }) = 14.036243467926484 degrees
* gcommaaccent (U+0123): Line(Line { p0: (204.0, 43.0), p1: (204.0, 44.0) })/Line(Line { p0: (204.0, 44.0), p1: (203.0, 40.0) }) = 14.036243467926484 degrees
* trademark (U+2122): Quad(QuadBez { p0: (326.5, 526.0), p1: (330.0, 527.0), p2: (329.0, 528.0) })/Quad(QuadBez { p0: (329.0, 528.0), p1: (334.0, 525.0), p2: (335.0, 523.5) }) = 14.036243467926484 degrees
* gcaron (U+01E7): Line(Line { p0: (204.0, 43.0), p1: (204.0, 44.0) })/Line(Line { p0: (204.0, 44.0), p1: (203.0, 40.0) }) = 14.036243467926484 degrees [code: found-jaggy-segments]
  
  

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

* W (U+0057): Quad(QuadBez { p0: (362.0, 284.0), p1: (362.0, 282.0), p2: (362.0, 281.5) }) has the same coordinates as a previous segment.
* W (U+0057): Quad(QuadBez { p0: (362.0, 281.5), p1: (362.0, 281.0), p2: (362.0, 280.0) }) has the same coordinates as a previous segment.
* Wcircumflex (U+0174): Quad(QuadBez { p0: (362.0, 284.0), p1: (362.0, 282.0), p2: (362.0, 281.5) }) has the same coordinates as a previous segment.
* Wcircumflex (U+0174): Quad(QuadBez { p0: (362.0, 281.5), p1: (362.0, 281.0), p2: (362.0, 280.0) }) has the same coordinates as a previous segment.
* Wgrave (U+1E80): Quad(QuadBez { p0: (362.0, 284.0), p1: (362.0, 282.0), p2: (362.0, 281.5) }) has the same coordinates as a previous segment.
* Wgrave (U+1E80): Quad(QuadBez { p0: (362.0, 281.5), p1: (362.0, 281.0), p2: (362.0, 280.0) }) has the same coordinates as a previous segment.
* Wacute (U+1E82): Quad(QuadBez { p0: (362.0, 284.0), p1: (362.0, 282.0), p2: (362.0, 281.5) }) has the same coordinates as a previous segment.
* Wacute (U+1E82): Quad(QuadBez { p0: (362.0, 281.5), p1: (362.0, 281.0), p2: (362.0, 280.0) }) has the same coordinates as a previous segment.
* Wdieresis (U+1E84): Quad(QuadBez { p0: (362.0, 284.0), p1: (362.0, 282.0), p2: (362.0, 281.5) }) has the same coordinates as a previous segment.
* Wdieresis (U+1E84): Quad(QuadBez { p0: (362.0, 281.5), p1: (362.0, 281.0), p2: (362.0, 280.0) }) has the same coordinates as a previous segment. [code: overlapping-path-segments]
  
  

</div>
</details>


</div>
</details>


<details><summary>[1] build/resubmission-review/final/instances/w500-d125-o10-s0.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any semi-vertical or semi-horizontal lines? (outline_semi_vertical)</summary>
    <div>


> This check detects line segments which are nearly, but not quite, exactly horizontal or vertical. Sometimes such lines are created by design, but often they are indicative of a design error.
> 
> This check is disabled for italic styles, which often contain nearly-upright lines.




Original proposal: [https://github.com/fonttools/fontbakery/pull/3088]





- ⚠️ **WARN** The following glyphs have semi-vertical/semi-horizontal lines:

* M (U+004D): Line(Line { p0: (668.0, 566.0), p1: (669.0, 315.0) }) (angle: -89.77 degrees, expected: -90.00 degrees)
* Germandbls (U+1E9E): Line(Line { p0: (211.0, 513.0), p1: (210.0, -2.0) }) (angle: -90.11 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (233.0, 64.0), p1: (234.0, 638.0) }) (angle: 89.90 degrees, expected: 90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (324.0, 574.0), p1: (325.0, 76.0) }) (angle: -89.88 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (430.0, 71.0), p1: (429.0, 635.0) }) (angle: 90.10 degrees, expected: 90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (521.0, 628.0), p1: (520.0, 142.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* emdash (U+2014): Line(Line { p0: (296.0, 317.0), p1: (479.0, 318.0) }) (angle: 0.31 degrees, expected: 0.00 degrees) [code: found-semi-vertical]
  
  

</div>
</details>


</div>
</details>


<details><summary>[1] build/resubmission-review/final/instances/w700-d100-o36-s0.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any semi-vertical or semi-horizontal lines? (outline_semi_vertical)</summary>
    <div>


> This check detects line segments which are nearly, but not quite, exactly horizontal or vertical. Sometimes such lines are created by design, but often they are indicative of a design error.
> 
> This check is disabled for italic styles, which often contain nearly-upright lines.




Original proposal: [https://github.com/fonttools/fontbakery/pull/3088]





- ⚠️ **WARN** The following glyphs have semi-vertical/semi-horizontal lines:

* M (U+004D): Line(Line { p0: (536.0, 568.0), p1: (537.0, 316.0) }) (angle: -89.77 degrees, expected: -90.00 degrees)
* M (U+004D): Line(Line { p0: (398.0, 134.0), p1: (399.0, 262.0) }) (angle: 89.55 degrees, expected: 90.00 degrees)
* arrowdown (U+2193): Line(Line { p0: (238.0, 483.0), p1: (239.0, 342.0) }) (angle: -89.59 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (155.0, 71.0), p1: (156.0, 640.0) }) (angle: 89.90 degrees, expected: 90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (257.0, 568.0), p1: (258.0, 73.0) }) (angle: -89.88 degrees, expected: -90.00 degrees)
* emdash (U+2014): Line(Line { p0: (205.0, 325.0), p1: (353.0, 326.0) }) (angle: 0.39 degrees, expected: 0.00 degrees) [code: found-semi-vertical]
  
  

</div>
</details>


</div>
</details>


<details><summary>[1] build/resubmission-review/final/instances/w500-d100-o10-s0.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any semi-vertical or semi-horizontal lines? (outline_semi_vertical)</summary>
    <div>


> This check detects line segments which are nearly, but not quite, exactly horizontal or vertical. Sometimes such lines are created by design, but often they are indicative of a design error.
> 
> This check is disabled for italic styles, which often contain nearly-upright lines.




Original proposal: [https://github.com/fonttools/fontbakery/pull/3088]





- ⚠️ **WARN** The following glyphs have semi-vertical/semi-horizontal lines:

* arrowup (U+2191): Line(Line { p0: (265.0, 367.0), p1: (264.0, 163.0) }) (angle: -90.28 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (188.0, 64.0), p1: (189.0, 638.0) }) (angle: 89.90 degrees, expected: 90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (279.0, 574.0), p1: (280.0, 76.0) }) (angle: -89.88 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (437.0, 628.0), p1: (436.0, 142.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* emdash (U+2014): Line(Line { p0: (241.0, 317.0), p1: (390.0, 318.0) }) (angle: 0.38 degrees, expected: 0.00 degrees) [code: found-semi-vertical]
  
  

</div>
</details>


</div>
</details>


<details><summary>[1] build/resubmission-review/final/instances/w300-d75-o36-s0.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any semi-vertical or semi-horizontal lines? (outline_semi_vertical)</summary>
    <div>


> This check detects line segments which are nearly, but not quite, exactly horizontal or vertical. Sometimes such lines are created by design, but often they are indicative of a design error.
> 
> This check is disabled for italic styles, which often contain nearly-upright lines.




Original proposal: [https://github.com/fonttools/fontbakery/pull/3088]





- ⚠️ **WARN** The following glyphs have semi-vertical/semi-horizontal lines:

* arrowup (U+2191): Line(Line { p0: (174.0, 361.0), p1: (173.0, 167.0) }) (angle: -90.30 degrees, expected: -90.00 degrees)
* arrowdown (U+2193): Line(Line { p0: (167.0, 462.0), p1: (168.0, 315.0) }) (angle: -89.61 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (187.0, 585.0), p1: (188.0, 82.0) }) (angle: -89.89 degrees, expected: -90.00 degrees)
* trademark (U+2122): Line(Line { p0: (473.0, 645.0), p1: (474.0, 499.0) }) (angle: -89.61 degrees, expected: -90.00 degrees)
* emdash (U+2014): Line(Line { p0: (162.0, 308.0), p1: (278.0, 309.0) }) (angle: 0.49 degrees, expected: 0.00 degrees) [code: found-semi-vertical]
  
  

</div>
</details>


</div>
</details>


<details><summary>[1] build/resubmission-review/final/instances/w400-d100-o10-s0.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any semi-vertical or semi-horizontal lines? (outline_semi_vertical)</summary>
    <div>


> This check detects line segments which are nearly, but not quite, exactly horizontal or vertical. Sometimes such lines are created by design, but often they are indicative of a design error.
> 
> This check is disabled for italic styles, which often contain nearly-upright lines.




Original proposal: [https://github.com/fonttools/fontbakery/pull/3088]





- ⚠️ **WARN** The following glyphs have semi-vertical/semi-horizontal lines:

* M (U+004D): Line(Line { p0: (561.0, 564.0), p1: (562.0, 315.0) }) (angle: -89.77 degrees, expected: -90.00 degrees)
* arrowup (U+2191): Line(Line { p0: (257.0, 371.0), p1: (256.0, 167.0) }) (angle: -90.28 degrees, expected: -90.00 degrees)
* Germandbls (U+1E9E): Line(Line { p0: (190.0, 472.0), p1: (189.0, -7.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (190.0, 60.0), p1: (191.0, 637.0) }) (angle: 89.90 degrees, expected: 90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (274.0, 578.0), p1: (275.0, 77.0) }) (angle: -89.89 degrees, expected: -90.00 degrees)
* trademark (U+2122): Line(Line { p0: (634.0, 643.0), p1: (635.0, 496.0) }) (angle: -89.61 degrees, expected: -90.00 degrees)
* emdash (U+2014): Line(Line { p0: (246.0, 312.0), p1: (396.0, 313.0) }) (angle: 0.38 degrees, expected: 0.00 degrees) [code: found-semi-vertical]
  
  

</div>
</details>


</div>
</details>


<details><summary>[1] build/resubmission-review/final/instances/w500-d125-o36-s0.ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any semi-vertical or semi-horizontal lines? (outline_semi_vertical)</summary>
    <div>


> This check detects line segments which are nearly, but not quite, exactly horizontal or vertical. Sometimes such lines are created by design, but often they are indicative of a design error.
> 
> This check is disabled for italic styles, which often contain nearly-upright lines.




Original proposal: [https://github.com/fonttools/fontbakery/pull/3088]





- ⚠️ **WARN** The following glyphs have semi-vertical/semi-horizontal lines:

* germandbls (U+00DF): Line(Line { p0: (164.0, 438.0), p1: (163.0, -2.0) }) (angle: -90.13 degrees, expected: -90.00 degrees)
* Germandbls (U+1E9E): Line(Line { p0: (174.0, 513.0), p1: (173.0, -2.0) }) (angle: -90.11 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (227.0, 563.0), p1: (226.0, 379.0) }) (angle: -90.31 degrees, expected: -90.00 degrees)
* paragraph (U+00B6): Line(Line { p0: (286.0, 574.0), p1: (288.0, 76.0) }) (angle: -89.77 degrees, expected: -90.00 degrees)
* trademark (U+2122): Line(Line { p0: (720.0, 639.0), p1: (721.0, 493.0) }) (angle: -89.61 degrees, expected: -90.00 degrees)
* emdash (U+2014): Line(Line { p0: (256.0, 318.0), p1: (440.0, 319.0) }) (angle: 0.31 degrees, expected: 0.00 degrees) [code: found-semi-vertical]
  
  

</div>
</details>


</div>
</details>






### Summary

| ⚠️ WARN | ✅ PASS | ⏩ SKIP | 
| ---|---|---|
| 40 | 272 | 24 | 
| 12% | 81% | 7% | 



