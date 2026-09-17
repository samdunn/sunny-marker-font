DRAFT ONLY — not submitted; maintainer requested no external contact.

**Archived proposal.** The [1.314 candidate](../../candidates/1.314/) instead
changes the font's repertoire. This draft is not part of that build or a request
to contact upstream maintainers.

# Keep macron below and E with tilde reachable in Latin subsets

Latin-script fonts can contain all required glyphs and still fail `googlefonts/tofu` after `latin` / `latin-ext` routing. In Sunny Marker's current review, nine failures refer to U+0331 COMBINING MACRON BELOW or U+1EBC / U+1EBD (Ẽ / ẽ), for Amarakaeri, Chickasaw, Guarani, Yanomamö, Mezquital Otomi, Secoya, Siona and Ticuna samples.

This proposal adds U+0331 to both Latin lists so it can accompany basic and extended Latin bases. It retains Ẽ / ẽ in `latin-ext` as well as their existing Vietnamese subset. No Vietnamese mapping is removed. The intentional shared Latin/Vietnamese letters are included in the overlap allowlist.

Validation: exact added-codepoint assertions; actual FontTools subset binaries; HarfBuzz shaping of A̱, a̱, é̱, i̱, Ŋ̱, Ẽ and ẽ; equivalent NFC/NFD glyph sequences and positions; unchanged Vietnamese definition. The installed Fontspector profile is unmodified and still reports the original routing failures. The upstream overlap test also has pre-existing failures; this proposal's focused regressions pass.

Related: https://github.com/googlefonts/nam-files/issues/6 and https://github.com/googlefonts/nam-files/issues/23. This is a minimal routing correction, independent of language-based subset inference in #29. Please advise if these shared characters should be assigned through another backend mechanism instead.
