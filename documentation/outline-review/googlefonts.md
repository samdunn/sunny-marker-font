## FontSpector report

fontspector version: 1.7.4






## Check results




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


<details><summary>[4] release/googlefonts/ofl/sunnymarker/SunnyMarker-Italic[opsz,wdth,wght].ttf</summary>
<div>


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





- ⚠️ **WARN** Glyph "space" has suspiciously high variation (z-score 10.82) in right sidebearings at locations:
    wdth=125.00
    wght=499.99, wdth=125.00, opsz=10.00
    wght=499.99, wdth=125.00
    wght=700.00, wdth=125.00, opsz=10.00
    wght=700.00, wdth=125.00 [code: large-rsb-variation]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Shapes languages in all GF glyphsets. (googlefonts/glyphsets/shape_languages)</summary>
    <div>


> This check uses a heuristic to determine which GF glyphsets a font supports. Then it checks the font for correct shaping behaviour for all languages in those glyphsets.




Original proposal: [https://github.com/googlefonts/fontbakery/issues/4147]





- ⚠️ **WARN** Warning language shaping:

| Message                                                           | Languages                    |
|-------------------------------------------------------------------|------------------------------|
| Auxiliary orthography codepoints:                                 | * ca_Latn (Catalan)          |
|   The following auxiliary characters are missing from the font: Ŀ |                              |
|   The following auxiliary characters are missing from the font: ŀ |                              |
| Auxiliary orthography codepoints:                                 | * de_Latn (German)           |
|   The following auxiliary characters are missing from the font: ſ | * fr_Latn (French)           |
| Auxiliary orthography codepoints:                                 | * da_Latn (Danish)           |
|   The following auxiliary characters are missing from the font: Ǿ |                              |
|   The following auxiliary characters are missing from the font: ǿ |                              |
| Auxiliary orthography codepoints:                                 | * fi_Latn (Finnish)          |
|   The following auxiliary characters are missing from the font: Ǥ |                              |
|   The following auxiliary characters are missing from the font: Ŧ |                              |
|   The following auxiliary characters are missing from the font: Ʒ |                              |
|   The following auxiliary characters are missing from the font: Ǯ |                              |
|   The following auxiliary characters are missing from the font: ǥ |                              |
|   The following auxiliary characters are missing from the font: ŧ |                              |
|   The following auxiliary characters are missing from the font: ʒ |                              |
|   The following auxiliary characters are missing from the font: ǯ |                              |
| Auxiliary orthography codepoints:                                 | * nb_Latn (Norwegian Bokmål) |
|   The following auxiliary characters are missing from the font: Ŧ |                              |
|   The following auxiliary characters are missing from the font: ŧ |                              |
| Auxiliary orthography codepoints:                                 | * nl_Latn (Dutch)            |
|   The following auxiliary characters are missing from the font: Ĳ |                              |
|   The following auxiliary characters are missing from the font: ĳ |                              | [code: warning-language-shaping]



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


<details><summary>[4] release/googlefonts/ofl/sunnymarker/SunnyMarker[opsz,wdth,wght].ttf</summary>
<div>


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





- ⚠️ **WARN** Glyph "space" has suspiciously high variation (z-score 11.70) in right sidebearings at locations:
    wght=300.00, wdth=75.00
    wght=300.00, wdth=125.00
    wdth=75.00, opsz=10.00
    wdth=75.00
    wdth=125.00, opsz=10.00
    wdth=125.00
    wght=499.99, wdth=75.00, opsz=10.00
    wght=499.99, wdth=75.00
    wght=499.99, wdth=125.00, opsz=10.00
    wght=499.99, wdth=125.00
    wght=700.00, wdth=125.00, opsz=10.00
    wght=700.00, wdth=125.00 [code: large-rsb-variation]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Shapes languages in all GF glyphsets. (googlefonts/glyphsets/shape_languages)</summary>
    <div>


> This check uses a heuristic to determine which GF glyphsets a font supports. Then it checks the font for correct shaping behaviour for all languages in those glyphsets.




Original proposal: [https://github.com/googlefonts/fontbakery/issues/4147]





- ⚠️ **WARN** Warning language shaping:

| Message                                                           | Languages                    |
|-------------------------------------------------------------------|------------------------------|
| Auxiliary orthography codepoints:                                 | * da_Latn (Danish)           |
|   The following auxiliary characters are missing from the font: Ǿ |                              |
|   The following auxiliary characters are missing from the font: ǿ |                              |
| Auxiliary orthography codepoints:                                 | * nb_Latn (Norwegian Bokmål) |
|   The following auxiliary characters are missing from the font: Ŧ |                              |
|   The following auxiliary characters are missing from the font: ŧ |                              |
| Auxiliary orthography codepoints:                                 | * de_Latn (German)           |
|   The following auxiliary characters are missing from the font: ſ | * fr_Latn (French)           |
| Auxiliary orthography codepoints:                                 | * fi_Latn (Finnish)          |
|   The following auxiliary characters are missing from the font: Ǥ |                              |
|   The following auxiliary characters are missing from the font: Ŧ |                              |
|   The following auxiliary characters are missing from the font: Ʒ |                              |
|   The following auxiliary characters are missing from the font: Ǯ |                              |
|   The following auxiliary characters are missing from the font: ǥ |                              |
|   The following auxiliary characters are missing from the font: ŧ |                              |
|   The following auxiliary characters are missing from the font: ʒ |                              |
|   The following auxiliary characters are missing from the font: ǯ |                              |
| Auxiliary orthography codepoints:                                 | * ca_Latn (Catalan)          |
|   The following auxiliary characters are missing from the font: Ŀ |                              |
|   The following auxiliary characters are missing from the font: ŀ |                              |
| Auxiliary orthography codepoints:                                 | * nl_Latn (Dutch)            |
|   The following auxiliary characters are missing from the font: Ĳ |                              |
|   The following auxiliary characters are missing from the font: ĳ |                              | [code: warning-language-shaping]



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





- 🔥 **FAIL** The font has the following codepoints needed to render the specimen 16 sample text for language Amarakaeri, but although the font contained all the base exemplars for the language, tofu will still be produced because the codepoints do not appear in any of the subsets latin-ext, latin:

* ̱ (U+0331) [code: missing-subsetted]




- 🔥 **FAIL** The font has the following codepoints needed to render the poster md sample text for language Chickasaw, but although the font contained all the base exemplars for the language, tofu will still be produced because the codepoints do not appear in any of the subsets latin-ext, latin:

* ̱ (U+0331) [code: missing-subsetted]




- 🔥 **FAIL** The font has the following codepoints needed to render the specimen 16 sample text for language Guarani, but although the font contained all the codepoints for the sample text, tofu will still be produced because the codepoints do not appear in any of the subsets latin-ext, latin:

* ẽ (U+1EBD) [code: missing-subsetted]




- 🔥 **FAIL** The font has the following codepoints needed to render the specimen 16 sample text for language Yanomamö, but although the font contained all the codepoints for the sample text, tofu will still be produced because the codepoints do not appear in any of the subsets latin-ext, latin:

* ẽ (U+1EBD) [code: missing-subsetted]




- 🔥 **FAIL** The font has the following codepoints needed to render the specimen 16 sample text for language Otomi, Mezquital, but although the font contained all the base exemplars for the language, tofu will still be produced because the codepoints do not appear in any of the subsets latin-ext, latin:

* ̱ (U+0331) [code: missing-subsetted]




- 🔥 **FAIL** The font has the following codepoints needed to render the specimen 16 sample text for language Secoya, but although the font contained all the base exemplars for the language, tofu will still be produced because the codepoints do not appear in any of the subsets latin-ext, latin:

* ̱ (U+0331) [code: missing-subsetted]




- 🔥 **FAIL** The font has the following codepoints needed to render the poster lg sample text for language Siona, but although the font contained all the codepoints for the sample text, tofu will still be produced because the codepoints do not appear in any of the subsets latin-ext, latin:

* ̱ (U+0331) [code: missing-subsetted]




- 🔥 **FAIL** The font has the following codepoints needed to render the masthead partial sample text for language Ticuna, but although the font contained all the codepoints for the sample text, tofu will still be produced because the codepoints do not appear in any of the subsets latin-ext, latin:

* Ẽ (U+1EBC)
* ẽ (U+1EBD) [code: missing-subsetted]




- 🔥 **FAIL** The font has the following codepoints needed to render the specimen 16 sample text for language Ticuna, but although the font contained all the codepoints for the sample text, tofu will still be produced because the codepoints do not appear in any of the subsets latin-ext, latin:

* ̱ (U+0331) [code: missing-subsetted]



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





- ⚠️ **WARN** release/googlefonts/ofl/sunnymarker/SunnyMarker-Italic[opsz,wdth,wght].ttf: The following codepoints supported by the font are not covered by any subsets defined in the font's metadata file, and will never be served. You can solve this by either manually adding additional subset declarations to METADATA.pb, or by editing the glyphset definitions.

* U+02D8 BREVE: try adding one of: canadian-aboriginal, yi
* U+02D9 DOT ABOVE: try adding one of: yi, canadian-aboriginal
* U+02DB OGONEK: try adding one of: yi, canadian-aboriginal
* U+0302 COMBINING CIRCUMFLEX ACCENT: try adding one of: tifinagh, math, coptic, cherokee
* U+0306 COMBINING BREVE: try adding one of: tifinagh, old-permic
* U+0307 COMBINING DOT ABOVE: try adding one of: math, duployan, coptic, syriac, tifinagh, todhri, malayalam, hebrew, old-permic, canadian-aboriginal, tai-le
* U+030A COMBINING RING ABOVE: try adding one of: duployan, syriac
* U+030B COMBINING DOUBLE ACUTE ACCENT: try adding one of: cherokee, osage
* U+030C COMBINING CARON: try adding one of: tai-le, cherokee
... and 20 others

Or you can add the above codepoints to one of the subsets supported by the font: latin, latin-ext, menu [code: unreachable-subsetting]




- ⚠️ **WARN** release/googlefonts/ofl/sunnymarker/SunnyMarker[opsz,wdth,wght].ttf: The following codepoints supported by the font are not covered by any subsets defined in the font's metadata file, and will never be served. You can solve this by either manually adding additional subset declarations to METADATA.pb, or by editing the glyphset definitions.

* U+02D8 BREVE: try adding one of: canadian-aboriginal, yi
* U+02D9 DOT ABOVE: try adding one of: yi, canadian-aboriginal
* U+02DB OGONEK: try adding one of: yi, canadian-aboriginal
* U+0302 COMBINING CIRCUMFLEX ACCENT: try adding one of: tifinagh, math, coptic, cherokee
* U+0306 COMBINING BREVE: try adding one of: tifinagh, old-permic
* U+0307 COMBINING DOT ABOVE: try adding one of: math, duployan, coptic, syriac, tifinagh, todhri, malayalam, hebrew, old-permic, canadian-aboriginal, tai-le
* U+030A COMBINING RING ABOVE: try adding one of: duployan, syriac
* U+030B COMBINING DOUBLE ACUTE ACCENT: try adding one of: cherokee, osage
* U+030C COMBINING CARON: try adding one of: tai-le, cherokee
... and 20 others

Or you can add the above codepoints to one of the subsets supported by the font: latin, latin-ext, menu [code: unreachable-subsetting]



</div>
</details>


</div>
</details>






### Summary

| 🔥 FAIL | ⚠️ WARN | ℹ️ INFO | ✅ PASS | ⏩ SKIP |
| ---|---|---|---|---|
| 9 | 12 | 16 | 281 | 69 |
| 2% | 3% | 4% | 73% | 18% |



