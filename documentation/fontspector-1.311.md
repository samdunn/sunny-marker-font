## FontSpector report

fontspector version: 1.7.4






## Check results




<details><summary>[15] release/googlefonts/ofl/sunnymarker/SunnyMarker[opsz,slnt,wdth,wght].ttf</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Check that OS/2 fsSelection WWS bit is set correctly. (opentype/fsselection_wws)</summary>
    <div>


> According to the OpenType specification, OS/2.fsSelection bit 8 (WWS) should be set if the font has name table strings consistent with a weight/width/slope family without requiring use of name IDs 21 and 22.
> 
> Conversely, if name IDs 21 and 22 are present (indicating the font names are not WWS-conformant), the WWS bit should not be set.




Original proposal: [https://github.com/fonttools/fontspector/issues/577]





- ⚠️ **WARN** OS/2 fsSelection WWS bit is not set, and the font does not have name IDs 21/22 (WWS Family/Subfamily). If the font's naming is WWS-conformant, the WWS bit should be set. [code: no-wws-without-wws-names]
  
  

</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Check mark characters are in GDEF mark glyph class. (opentype/GDEF_mark_chars)</summary>
    <div>


> Mark characters should be in the GDEF mark glyph class.




Original proposal: [https://github.com/fonttools/fontbakery/issues/2877]





- ⚠️ **WARN** The following mark characters should be in the GDEF mark glyph class:

* U+0300 (gravecomb)
* U+0301 (acutecomb)
* U+0302 (circumflexcomb)
* U+0303 (tildecomb)
* U+0304 (macroncomb)
* U+0306 (brevecomb)
* U+0307 (dotaccentcomb)
* U+0308 (dieresiscomb)
* U+030A (ringcomb)
... and 5 others [code: mark-chars]
  
  

</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Check accent of Lcaron, dcaron, lcaron, tcaron (alt_caron)</summary>
    <div>


> Lcaron, dcaron, lcaron, tcaron should NOT be composed with quoteright or quotesingle or comma or caron(comb). It should be composed with a distinctive glyph which doesn't look like an apostrophe.
> 
> Source: https://ilovetypography.com/2009/01/24/on-diacritics/ http://diacritics.typo.cz/index.php?id=5 https://www.typotheque.com/articles/lcaron




Original proposal: [https://github.com/fonttools/fontbakery/issues/3308]





- ⚠️ **WARN** Lcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]
  
  


- ⚠️ **WARN** dcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]
  
  


- ⚠️ **WARN** lcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]
  
  


- ⚠️ **WARN** tcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]
  
  

</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Check if each glyph has the recommended amount of contours. (contour_count)</summary>
    <div>


> Visually QAing thousands of glyphs by hand is tiring. Most glyphs can only be constructured in a handful of ways. This means a glyph's contour count will only differ slightly amongst different fonts, e.g a 'g' could either be 2 or 3 contours, depending on whether its double story or single story.
> 
> However, a quotedbl should have 2 contours, unless the font belongs to a display family.
> 
> This check currently does not cover variable fonts because there's plenty of alternative ways of constructing glyphs with multiple outlines for each feature in a VarFont. The expected contour count data for this check is currently optimized for the typical construction of glyphs in static fonts.




Original proposal: [https://github.com/fonttools/fontbakery/issues/4829]





- ⚠️ **WARN** This check inspects the glyph outlines and detects the total number of contours in each of them. The expected values are
     inferred from the typical amounts of contours observed in a
     large collection of reference font families. The divergences
     listed below may simply indicate a significantly different
     design on some of your glyphs. On the other hand, some of these
     may flag actual bugs in the font such as glyphs mapped to an
     incorrect codepoint. Please consider reviewing the design and
     codepoint assignment of these to make sure they are correct.


    The following glyphs do not have the recommended number of contours:
* heart (U+2764): found 2, expected one of: [1, 10, 24] [code: contour-count]
  
  

</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Ensure files are not too large. (file_size)</summary>
    <div>


> Serving extremely large font files causes usability issues. This check ensures that file sizes are reasonable.




Original proposal: [https://github.com/fonttools/fontbakery/issues/3320]





- ⚠️ **WARN** Font file is 3.72 MB; ideally it should be less than 1.05 MB [code: large-font]
  
  

</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Check math signs have the same width. (math_signs_width)</summary>
    <div>


> #,         It is a common practice to have math signs sharing the same width         (preferably the same width as tabular figures accross the entire font family).
> 
> This probably comes from the will to avoid additional tabular math signs knowing that their design can easily share the same width.




Original proposal: [https://github.com/fonttools/fontbakery/issues/3832]





- ⚠️ **WARN** The most common width is 432 among a set of 7  math glyphs.
The following math glyphs have a different width, though:
width=421: plus
width=370: less
width=369: greater
width=434: multiply
width=596: minus [code: width-outliers]
  
  

</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Ensure indic fonts have the Indian Rupee Sign glyph. (rupee)</summary>
    <div>


> Per Bureau of Indian Standards every font supporting one of the official Indian languages needs to include Unicode Character “₹” (U+20B9) Indian Rupee Sign.




Original proposal: [https://github.com/fonttools/fontbakery/issues/2967]





- ⚠️ **WARN** Font is missing the Indian Rupee Sign glyph. Please add a glyph for Indian Rupee Sign (₹) at codepoint U+20B9. [code: missing-rupee]
  
  

</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Ensure variable fonts have relatively consistent sidebearings. (suspicious_sidebearings)</summary>
    <div>


> Glyphs in variable fonts should vary across the designspace in a consistent way. If there are outliers the advance width, left or right sidebearings of glyphs at certain locations in the designspace, this may indicate design issue with the font.




Original proposal: [https://github.com/fonttools/fontspector/issues/557]





- ⚠️ **WARN** Glyph ".notdef" has suspiciously high variation (z-score 17.74) in right sidebearings at locations:
    wght=300.00, opsz=36.00
    opsz=36.00
    wght=499.99, opsz=36.00 [code: large-rsb-variation]
  
  

</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Shapes languages in all GF glyphsets. (googlefonts/glyphsets/shape_languages)</summary>
    <div>


> This check uses a heuristic to determine which GF glyphsets a font supports. Then it checks the font for correct shaping behaviour for all languages in those glyphsets.




Original proposal: [https://github.com/googlefonts/fontbakery/issues/4147]





- ⚠️ **WARN** Warning language shaping:

| Message                                                                     | Languages                    |
|-----------------------------------------------------------------------------|------------------------------|
| Auxiliary orthography codepoints:                                           | * fr_Latn (French)           |
|   The following auxiliary characters are missing from the font: Ǔ           |                              |
|   The following auxiliary characters are missing from the font: ſ           |                              |
|   The following auxiliary characters are missing from the font: ǔ           |                              |
| Auxiliary orthography codepoints:                                           | * de_Latn (German)           |
|   The following auxiliary characters are missing from the font: Ĕ           |                              |
|   The following auxiliary characters are missing from the font: Ĭ           |                              |
|   The following auxiliary characters are missing from the font: Ŏ           |                              |
|   The following auxiliary characters are missing from the font: Ō           |                              |
|   The following auxiliary characters are missing from the font: Ŭ           |                              |
|   The following auxiliary characters are missing from the font: ĕ           |                              |
|   The following auxiliary characters are missing from the font: ĭ           |                              |
|   The following auxiliary characters are missing from the font: ŏ           |                              |
|   The following auxiliary characters are missing from the font: ō           |                              |
|   The following auxiliary characters are missing from the font: ſ           |                              |
|   The following auxiliary characters are missing from the font: ŭ           |                              |
| Auxiliary orthography codepoints:                                           | * ca_Latn (Catalan)          |
|   The following auxiliary characters are missing from the font: Ĕ           |                              |
|   The following auxiliary characters are missing from the font: Ĭ           |                              |
|   The following auxiliary characters are missing from the font: Ŀ           |                              |
|   The following auxiliary characters are missing from the font: Ŏ           |                              |
|   The following auxiliary characters are missing from the font: Ō           |                              |
|   The following auxiliary characters are missing from the font: Ŭ           |                              |
|   The following auxiliary characters are missing from the font: ĕ           |                              |
|   The following auxiliary characters are missing from the font: ĭ           |                              |
|   The following auxiliary characters are missing from the font: ŀ           |                              |
|   The following auxiliary characters are missing from the font: ŏ           |                              |
|   The following auxiliary characters are missing from the font: ō           |                              |
|   The following auxiliary characters are missing from the font: ŭ           |                              |
| Auxiliary orthography codepoints:                                           | * lt_Latn (Lithuanian)       |
|   The following auxiliary characters are missing from the font: Ẽ           |                              |
|   The following auxiliary characters are missing from the font: Ĩ           |                              |
|   The following auxiliary characters are missing from the font: Ũ           |                              |
|   The following auxiliary characters are missing from the font: ẽ           |                              |
|   The following auxiliary characters are missing from the font: ĩ           |                              |
|   The following auxiliary characters are missing from the font: ũ           |                              |
|   Shaper didn't attach acutecomb to Aogonek when shaping the text 'Ą́'       |                              |
|   Shaper didn't attach tildecomb to Aogonek when shaping the text 'Ą̃'       |                              |
|   Shaper didn't attach acutecomb to Eogonek when shaping the text 'Ę́'       |                              |
|   Shaper didn't attach tildecomb to Eogonek when shaping the text 'Ę̃'       |                              |
|   Shaper didn't attach acutecomb to Edotaccent when shaping the text 'Ė́'    |                              |
|   Shaper didn't attach tildecomb to Edotaccent when shaping the text 'Ė̃'    |                              |
|   Shaper didn't attach acutecomb to Idotaccent when shaping the text 'İ́'    |                              |
|   Shaper didn't attach acutecomb to Idotaccent when shaping the text 'İ́'    |                              |
|   Shaper didn't attach gravecomb to Idotaccent when shaping the text 'İ̀'    |                              |
|   Shaper didn't attach gravecomb to Idotaccent when shaping the text 'İ̀'    |                              |
|   Shaper didn't attach tildecomb to Idotaccent when shaping the text 'İ̃'    |                              |
|   Shaper didn't attach tildecomb to Idotaccent when shaping the text 'İ̃'    |                              |
|   Shaper didn't attach acutecomb to Iogonek when shaping the text 'Į́'       |                              |
|   Shaper didn't attach dotaccentcomb to Iogonek when shaping the text 'Į̇́'   |                              |
|   Shaper didn't attach acutecomb to dotaccentcomb when shaping the text 'Į̇́' |                              |
|   Shaper didn't attach tildecomb to Iogonek when shaping the text 'Į̃'       |                              |
|   Shaper didn't attach dotaccentcomb to Iogonek when shaping the text 'Į̇̃'   |                              |
|   Shaper didn't attach tildecomb to dotaccentcomb when shaping the text 'Į̇̃' |                              |
|   Shaper didn't attach tildecomb to J when shaping the text 'J̃'             |                              |
|   Shaper didn't attach dotaccentcomb to J when shaping the text 'J̇̃'         |                              |
|   Shaper didn't attach tildecomb to dotaccentcomb when shaping the text 'J̇̃' |                              |
|   Shaper didn't attach tildecomb to L when shaping the text 'L̃'             |                              |
|   Shaper didn't attach tildecomb to M when shaping the text 'M̃'             |                              |
|   Shaper didn't attach tildecomb to R when shaping the text 'R̃'             |                              |
|   Shaper didn't attach acutecomb to Uogonek when shaping the text 'Ų́'       |                              |
|   Shaper didn't attach tildecomb to Uogonek when shaping the text 'Ų̃'       |                              |
|   Shaper didn't attach acutecomb to Umacron when shaping the text 'Ū́'       |                              |
|   Shaper didn't attach tildecomb to Umacron when shaping the text 'Ū̃'       |                              |
|   Shaper didn't attach acutecomb to aogonek when shaping the text 'ą́'       |                              |
|   Shaper didn't attach tildecomb to aogonek when shaping the text 'ą̃'       |                              |
|   Shaper didn't attach acutecomb to eogonek when shaping the text 'ę́'       |                              |
|   Shaper didn't attach tildecomb to eogonek when shaping the text 'ę̃'       |                              |
|   Shaper didn't attach acutecomb to edotaccent when shaping the text 'ė́'    |                              |
|   Shaper didn't attach tildecomb to edotaccent when shaping the text 'ė̃'    |                              |
|   Shaper didn't attach dotaccentcomb to i when shaping the text 'i̇́'         |                              |
|   Shaper didn't attach acutecomb to dotaccentcomb when shaping the text 'i̇́' |                              |
|   Shaper didn't attach dotaccentcomb to i when shaping the text 'i̇̀'         |                              |
|   Shaper didn't attach gravecomb to dotaccentcomb when shaping the text 'i̇̀' |                              |
|   Shaper didn't attach dotaccentcomb to i when shaping the text 'i̇̃'         |                              |
|   Shaper didn't attach tildecomb to dotaccentcomb when shaping the text 'i̇̃' |                              |
|   Shaper didn't attach acutecomb to iogonek when shaping the text 'į́'       |                              |
|   Shaper didn't attach dotaccentcomb to iogonek when shaping the text 'į̇́'   |                              |
|   Shaper didn't attach acutecomb to dotaccentcomb when shaping the text 'į̇́' |                              |
|   Shaper didn't attach tildecomb to iogonek when shaping the text 'į̃'       |                              |
|   Shaper didn't attach dotaccentcomb to iogonek when shaping the text 'į̇̃'   |                              |
|   Shaper didn't attach tildecomb to dotaccentcomb when shaping the text 'į̇̃' |                              |
|   Shaper didn't attach tildecomb to j when shaping the text 'j̃'             |                              |
|   Shaper didn't attach dotaccentcomb to j when shaping the text 'j̇̃'         |                              |
|   Shaper didn't attach tildecomb to dotaccentcomb when shaping the text 'j̇̃' |                              |
|   Shaper didn't attach tildecomb to l when shaping the text 'l̃'             |                              |
|   Shaper didn't attach tildecomb to m when shaping the text 'm̃'             |                              |
|   Shaper didn't attach tildecomb to r when shaping the text 'r̃'             |                              |
|   Shaper didn't attach acutecomb to uogonek when shaping the text 'ų́'       |                              |
|   Shaper didn't attach tildecomb to uogonek when shaping the text 'ų̃'       |                              |
|   Shaper didn't attach acutecomb to umacron when shaping the text 'ū́'       |                              |
|   Shaper didn't attach tildecomb to umacron when shaping the text 'ū̃'       |                              |
| Auxiliary orthography codepoints:                                           | * lv_Latn (Latvian)          |
|   The following auxiliary characters are missing from the font: Ō           |                              |
|   The following auxiliary characters are missing from the font: Ŗ           |                              |
|   The following auxiliary characters are missing from the font: ō           |                              |
|   The following auxiliary characters are missing from the font: ŗ           |                              |
| Auxiliary orthography codepoints:                                           | * en_Latn (English)          |
|   The following auxiliary characters are missing from the font: Ĕ           |                              |
|   The following auxiliary characters are missing from the font: Ĭ           |                              |
|   The following auxiliary characters are missing from the font: Ŏ           |                              |
|   The following auxiliary characters are missing from the font: Ō           |                              |
|   The following auxiliary characters are missing from the font: Ŭ           |                              |
|   The following auxiliary characters are missing from the font: ĕ           |                              |
|   The following auxiliary characters are missing from the font: ĭ           |                              |
|   The following auxiliary characters are missing from the font: ŏ           |                              |
|   The following auxiliary characters are missing from the font: ō           |                              |
|   The following auxiliary characters are missing from the font: ŭ           |                              |
|   The following auxiliary characters are missing from the font: ʻ           |                              |
| Auxiliary orthography codepoints:                                           | * ro_Latn (Romanian)         |
|   The following auxiliary characters are missing from the font: Ţ           |                              |
|   The following auxiliary characters are missing from the font: ţ           |                              |
| Auxiliary orthography codepoints:                                           | * nb_Latn (Norwegian Bokmål) |
|   The following auxiliary characters are missing from the font: Ǎ           |                              |
|   The following auxiliary characters are missing from the font: Ŋ           |                              |
|   The following auxiliary characters are missing from the font: Ŧ           |                              |
|   The following auxiliary characters are missing from the font: ǎ           |                              |
|   The following auxiliary characters are missing from the font: ŋ           |                              |
|   The following auxiliary characters are missing from the font: ŧ           |                              |
| Auxiliary orthography codepoints:                                           | * nl_Latn (Dutch)            |
|   The following auxiliary characters are missing from the font: Ĳ           |                              |
|   The following auxiliary characters are missing from the font: ĳ           |                              |
| Auxiliary orthography codepoints:                                           | * fi_Latn (Finnish)          |
|   The following auxiliary characters are missing from the font: Ǧ           |                              |
|   The following auxiliary characters are missing from the font: Ǥ           |                              |
|   The following auxiliary characters are missing from the font: Ȟ           |                              |
|   The following auxiliary characters are missing from the font: Ǩ           |                              |
|   The following auxiliary characters are missing from the font: Ŋ           |                              |
|   The following auxiliary characters are missing from the font: Ŝ           |                              |
|   The following auxiliary characters are missing from the font: Ţ           |                              |
|   The following auxiliary characters are missing from the font: Ŧ           |                              |
|   The following auxiliary characters are missing from the font: Ʒ           |                              |
|   The following auxiliary characters are missing from the font: Ǯ           |                              |
|   The following auxiliary characters are missing from the font: ǧ           |                              |
|   The following auxiliary characters are missing from the font: ǥ           |                              |
|   The following auxiliary characters are missing from the font: ȟ           |                              |
|   The following auxiliary characters are missing from the font: ǩ           |                              |
|   The following auxiliary characters are missing from the font: ŋ           |                              |
|   The following auxiliary characters are missing from the font: ŝ           |                              |
|   The following auxiliary characters are missing from the font: ţ           |                              |
|   The following auxiliary characters are missing from the font: ŧ           |                              |
|   The following auxiliary characters are missing from the font: ʒ           |                              |
|   The following auxiliary characters are missing from the font: ǯ           |                              |
| Auxiliary orthography codepoints:                                           | * cs_Latn (Czech)            |
|   The following auxiliary characters are missing from the font: Ĕ           | * cy_Latn (Welsh)            |
|   The following auxiliary characters are missing from the font: Ĭ           | * es_Latn (Spanish)          |
|   The following auxiliary characters are missing from the font: Ŏ           | * hu_Latn (Hungarian)        |
|   The following auxiliary characters are missing from the font: Ō           | * pt_Latn (Portuguese)       |
|   The following auxiliary characters are missing from the font: Ŭ           | * sk_Latn (Slovak)           |
|   The following auxiliary characters are missing from the font: ĕ           | * tr_Latn (Turkish)          |
|   The following auxiliary characters are missing from the font: ĭ           |                              |
|   The following auxiliary characters are missing from the font: ŏ           |                              |
|   The following auxiliary characters are missing from the font: ō           |                              |
|   The following auxiliary characters are missing from the font: ŭ           |                              |
| Auxiliary orthography codepoints:                                           | * da_Latn (Danish)           |
|   The following auxiliary characters are missing from the font: Ǿ           |                              |
|   The following auxiliary characters are missing from the font: ǿ           |                              | [code: warning-language-shaping]
  
  

</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Font has correct separator glyphs? (googlefonts/separator_glyphs)</summary>
    <div>


> U+2028 and U+2029 should be present; otherwise tofu is displayed. (whitespace_ink will check that they are empty)




Original proposal: [https://github.com/fonttools/fontspector/issues/93]





- ⚠️ **WARN** Missing separator glyph U+2028 [code: missing-separator-glyphs]
  
  


- ⚠️ **WARN** Missing separator glyph U+2029 [code: missing-separator-glyphs]
  
  

</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Ensure soft_dotted characters lose their dot when combined with marks that
replace the dot. (soft_dotted)</summary>
    <div>


> An accent placed on characters with a "soft dot", like i or j, causes the dot to disappear. An explicit dot above can be added where required. See "Diacritics on i and j" in Section 7.1, "Latin" in The Unicode Standard.
> 
> Characters with the Soft_Dotted property are listed in https://www.unicode.org/Public/UCD/latest/ucd/PropList.txt
> 
> See also: https://googlefonts.github.io/gf-guide/diacritics.html#soft-dotted-glyphs




Original proposal: [https://github.com/fonttools/fontbakery/issues/4059]





- ⚠️ **WARN** The dot of soft dotted characters used in orthographies _must_ disappear in the following strings:

* j̀
* j̈
* j̃
* j̄
* į̀
* į̂
* į́
* į̌
* į̃
... and 3 othersThe dot of soft dotted characters _should_ disappear in other cases, for example:

* j̆
* j̋
* ĵ
* j̇
* j̊
* ǰ
* į̆
* į̋
* į̈
... and 6 others [code: soft-dotted]
  
  

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

* acircumflex (U+00E2): Line(Line { p0: (253.0, 570.0), p1: (253.0, 570.0) }) has the same coordinates as a previous segment.
* acircumflex (U+00E2): Line(Line { p0: (253.0, 570.0), p1: (253.0, 570.0) }) has the same coordinates as a previous segment.
* acircumflex (U+00E2): Line(Line { p0: (253.0, 570.0), p1: (253.0, 570.0) }) has the same coordinates as a previous segment.
* acircumflex (U+00E2): Line(Line { p0: (253.0, 570.0), p1: (253.0, 570.0) }) has the same coordinates as a previous segment.
* ecircumflex (U+00EA): Line(Line { p0: (234.0, 616.0), p1: (234.0, 615.0) }) has the same coordinates as a previous segment.
* ecircumflex (U+00EA): Line(Line { p0: (233.0, 614.0), p1: (233.0, 614.0) }) has the same coordinates as a previous segment.
* icircumflex (U+00EE): Line(Line { p0: (175.0, 567.0), p1: (175.0, 567.0) }) has the same coordinates as a previous segment.
* icircumflex (U+00EE): Line(Line { p0: (175.0, 567.0), p1: (175.0, 567.0) }) has the same coordinates as a previous segment.
* ocircumflex (U+00F4): Line(Line { p0: (225.0, 618.0), p1: (226.0, 618.0) }) has the same coordinates as a previous segment.
... and 17 others [code: overlapping-path-segments]
  
  

</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Check variable font instances (googlefonts/fvar_instances)</summary>
    <div>


> Check a font's fvar instance coordinates comply with our guidelines: https://googlefonts.github.io/gf-guide/variable.html#fvar-instances
> 
> This check is skipped for fonts that have a Morph (MORF) axis since we allow users to define their own custom instances.




Original proposal: [https://github.com/fonttools/fontbakery/pull/3800]





- ⚠️ **WARN** fvar instance coordinates for non-wght axes are not the same as the fvar defaults. This may be intentional so please check with the font author:

| Name            | current                              | expected                            |
|-----------------|--------------------------------------|-------------------------------------|
| Light           | opsz=14, slnt=0, wdth=100, wght=300  | opsz=14, slnt=0, wdth=100, wght=300 |
| Light Italic    | opsz=14, slnt=-9, wdth=100, wght=300 | opsz=14, slnt=0, wdth=100, wght=300 |
| Regular         | opsz=14, slnt=0, wdth=100, wght=400  | opsz=14, slnt=0, wdth=100, wght=400 |
| Italic          | opsz=14, slnt=-9, wdth=100, wght=400 | opsz=14, slnt=0, wdth=100, wght=400 |
| Medium          | opsz=14, slnt=0, wdth=100, wght=500  | opsz=14, slnt=0, wdth=100, wght=500 |
| Medium Italic   | opsz=14, slnt=-9, wdth=100, wght=500 | opsz=14, slnt=0, wdth=100, wght=500 |
| SemiBold        | opsz=14, slnt=0, wdth=100, wght=600  | opsz=14, slnt=0, wdth=100, wght=600 |
| SemiBold Italic | opsz=14, slnt=-9, wdth=100, wght=600 | opsz=14, slnt=0, wdth=100, wght=600 |
| Bold            | opsz=14, slnt=0, wdth=100, wght=700  | opsz=14, slnt=0, wdth=100, wght=700 |
| Bold Italic     | opsz=14, slnt=-9, wdth=100, wght=700 | opsz=14, slnt=0, wdth=100, wght=700 |

 [code: suspicious-fvar-coords]
  
  

</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Variable fonts with slnt axis need a separate Italic file for Google Workspace compatibility. (googlefonts/varfont/slnt_needs_italic)</summary>
    <div>


> Google Workspace applications (Docs, Sheets, Slides) do not currently support the 'slnt' (Slant) axis for selecting italic styles. If a variable font family relies solely on a Slant axis for its italic styles, those styles will not be accessible in Workspace apps.
> 
> To ensure full compatibility, font families with a Slant axis should also provide a separate Italic file so that Workspace users can access italic styles through the standard Bold/Italic toggles.




Original proposal: [https://github.com/fonttools/fontspector/issues/647]





- ⚠️ **WARN** This variable font has a 'slnt' (Slant) axis but no 'ital' axis. Google Workspace apps (Docs, Sheets, Slides) do not support the Slant axis for selecting italic styles. Please ensure this font family also includes a separate Italic file so that italic styles are accessible in Workspace applications. [code: needs-italic]
  
  

</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Checking OS/2 achVendID. (googlefonts/vendor_id)</summary>
    <div>


> Microsoft keeps a list of font vendors and their respective contact info. This list is updated regularly and is indexed by a 4-char "Vendor ID" which is stored in the achVendID field of the OS/2 table.
> 
> Registering your ID is not mandatory, but it is a good practice since some applications may display the type designer / type foundry contact info on some dialog and also because that info will be visible on Microsoft's website:
> 
> https://docs.microsoft.com/en-us/typography/vendors/
> 
> This check verifies whether or not a given font's vendor ID is registered in that list or if it has some of the default values used by the most common font editors.
> 
> Each new FontBakery release includes a cached copy of that list of vendor IDs. If you registered recently, you're safe to ignore warnings emitted by this check, since your ID will soon be included in one of our upcoming releases.




Original proposal: [https://github.com/fonttools/fontbakery/issues/3943, https://github.com/fonttools/fontbakery/issues/4829]





- ⚠️ **WARN** OS/2 VendorID value 'NONE' is not yet recognized.
If you registered it recently, then it's safe to ignore this warning message. Otherwise, you should set it to your own unique 4 character code, and register it with Microsoft at https://www.microsoft.com/typography/links/vendorlist.aspx
 [code: unknown]
  
  

</div>
</details>


</div>
</details>


<details><summary>[3] release/googlefonts/ofl/sunnymarker</summary>
<div>


<details>
    <summary>🔥 <b>FAIL</b> Tofu should not be shown in sample texts. (googlefonts/tofu)</summary>
    <div>


> When the Google Fonts backend determines that a language is supported for a font, then the font should not show tofu for the sample texts for that language.




Original proposal: []





- 🔥 **FAIL** We detected support for the Amarakaeri language because the font contained all the base exemplars for the language, but the font is missing the following codepoints needed to render the specimen 16 sample text (This suggests there's something wrong with the sample text):

* ̱ (U+0331) [code: bad-sample-text]
  
  


- 🔥 **FAIL** We detected support for the Qʼeqchiʼ language because the font contained all the base exemplars for the language, but the font is missing the following codepoints needed to render the specimen 16 sample text (This suggests there's something wrong with the sample text):

* ʼ (U+02BC) [code: bad-sample-text]
  
  


- 🔥 **FAIL** We detected support for the Otomi, Mezquital language because the font contained all the base exemplars for the language, but the font is missing the following codepoints needed to render the specimen 16 sample text (This suggests there's something wrong with the sample text):

* ̱ (U+0331) [code: bad-sample-text]
  
  


- 🔥 **FAIL** We detected support for the Secoya language because the font contained all the base exemplars for the language, but the font is missing the following codepoints needed to render the specimen 16 sample text (This suggests there's something wrong with the sample text):

* ̱ (U+0331) [code: bad-sample-text]
  
  


- 🔥 **FAIL** We detected support for the Purepecha language because the font contained all the base exemplars for the language, but the font is missing the following codepoints needed to render the specimen 16 sample text (This suggests there's something wrong with the sample text):

* ŋ (U+014B) [code: bad-sample-text]
  
  


- 🔥 **FAIL** We detected support for the Yapese language because the font contained all the base exemplars for the language, but the font is missing the following codepoints needed to render the specimen 16 sample text (This suggests there's something wrong with the sample text):

* ʼ (U+02BC) [code: bad-sample-text]
  
  


- 🔥 **FAIL** We detected support for the Yucateco language because the font contained all the base exemplars for the language, but the font is missing the following codepoints needed to render the specimen 16 sample text (This suggests there's something wrong with the sample text):

* ʼ (U+02BC) [code: bad-sample-text]
  
  

</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> METADATA.pb subsets are correct? (googlefonts/metadata/subsets_correct)</summary>
    <div>


> The subsets fields in METADATA.pb must not contain any subsets for which the font has zero codepoints, and should contain all the subsets which the font does support. 'menu' and 'latin' should be declared for all fonts, there should be be at most one CJK subset declared, and the subsets must appear in alphabetical order.




Original proposal: [https://github.com/fonttools/fontbakery/issues/4829]





- ⚠️ **WARN** Please remove 'latin-ext' from METADATA.pb since less than 20% of its glyphs are supported by this font file. [code: unsupported-subset]
  
  

</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Check for codepoints not covered by METADATA subsets. (googlefonts/metadata/unreachable_subsetting)</summary>
    <div>


> This check ensures that all encoded glyphs in the font are covered by a subset declared in the METADATA.pb. Google Fonts splits the font into a set of subset fonts based on the contents of the `subsets` field and the subset definitions in the `glyphsets` repository.
> 
> Any encoded glyphs which are not by any of these subset definitions will not be served in the subsetted fonts, and so will be unreachable to the end user.




Original proposal: [https://github.com/fonttools/fontbakery/issues/4097 and https://github.com/fonttools/fontbakery/pull/4273]





- ⚠️ **WARN** release/googlefonts/ofl/sunnymarker/SunnyMarker[opsz,slnt,wdth,wght].ttf: The following codepoints supported by the font are not covered by any subsets defined in the font's metadata file, and will never be served. You can solve this by either manually adding additional subset declarations to METADATA.pb, or by editing the glyphset definitions.

* U+02D8 BREVE: try adding one of: canadian-aboriginal, yi
* U+02D9 DOT ABOVE: try adding one of: yi, canadian-aboriginal
* U+02DB OGONEK: try adding one of: canadian-aboriginal, yi
* U+0302 COMBINING CIRCUMFLEX ACCENT: try adding one of: coptic, math, cherokee, tifinagh
* U+0306 COMBINING BREVE: try adding one of: tifinagh, old-permic
* U+0307 COMBINING DOT ABOVE: try adding one of: canadian-aboriginal, todhri, malayalam, tai-le, coptic, old-permic, hebrew, tifinagh, syriac, math, duployan
* U+030A COMBINING RING ABOVE: try adding one of: duployan, syriac
* U+030B COMBINING DOUBLE ACUTE ACCENT: try adding one of: osage, cherokee
* U+030C COMBINING CARON: try adding one of: tai-le, cherokee
... and 16 others

Or you can add the above codepoints to one of the subsets supported by the font: latin, latin-ext, menu [code: unreachable-subsetting]
  
  

</div>
</details>


</div>
</details>


<details><summary>[1] release/googlefonts/ofl/sunnymarker/METADATA.pb</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> METADATA.pb: Designers are listed correctly on the Google Fonts catalog? (googlefonts/metadata/designer_profiles)</summary>
    <div>


> Google Fonts has a catalog of designers.
> 
> This check ensures that the online entries of the catalog can be found based on the designer names listed on the METADATA.pb file.
> 
> It also validates the URLs and file formats are all correctly set.




Original proposal: [https://github.com/fonttools/fontbakery/issues/3083]





- ⚠️ **WARN** It seems that samdunn is still not listed on the designers catalog. Please submit a photo and a link to a webpage where people can learn more about the work of this designer/typefoundry. [code: profile-not-found]
  
  

</div>
</details>


</div>
</details>






### Summary

| 🔥 FAIL | ⚠️ WARN | ℹ️ INFO | ✅ PASS | ⏩ SKIP | 
| ---|---|---|---|---|
| 7 | 22 | 9 | 148 | 42 | 
| 3% | 10% | 4% | 65% | 18% | 



