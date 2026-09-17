# Local subset-routing proposal

**Prepared and tested locally. Not submitted. The maintainer requested no contact with Google or other maintainers.**

The font contains the characters behind all nine `googlefonts/tofu` failures. Google's current Latin routing lists omit U+0331 (combining macron below) and route U+1EBC / U+1EBD (Ẽ / ẽ) only through Vietnamese.

The [proposed patch](latin-routing.patch) adds U+0331 to `latin` and `latin-ext`, and shares Ẽ / ẽ with `latin-ext` while retaining their Vietnamese mappings. It targets `googlefonts/nam-files` commit `1d38a7d77ce11452ccbfe8fa9a0cb728ee6d7cd3`.

[Verification](verification.json) checks the exact additions, actual subset binaries, mark shaping and identical NFC/NFD glyph positions. Vietnamese is unchanged. Two focused upstream regression tests pass. The repository's general overlap test has pre-existing failures; no all-tests-passing claim is made. Regenerating with a newer Unicode database also introduces unrelated codepoints; those unrelated additions were kept out of this minimal patch.

This demonstrates a possible fix. It does **not** change Google's live service or Fontspector's bundled subset tables. The unmodified official profile remains authoritative and continues to report nine failures until the upstream routing is corrected or Google approves another approach. Adding unrelated script subsets to Sunny Marker's metadata would not be an honest solution.

To reproduce against a local nam-files checkout with the patch applied:

```sh
python scripts/verify_subset_proposal.py /path/to/nam-files \
  'build/outline-review/candidate/SunnyMarker[opsz,slnt,wdth,wght].ttf' \
  build/subset-proposal.json
```

The [draft message](UPSTREAM_PR.md) is saved only for future use if the maintainer authorizes contact.
