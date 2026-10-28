# Contributing

Sunny Marker is a handwritten marker family licensed under the SIL Open Font
License 1.1. Contributions to the font, sources, documentation and build tools
are made under that license.

## Build and verify

Use Python 3.13 in a virtual environment. Install `requirements-qa.txt`, then
run `make build`, `make verify`, `make check`, and `make audit`.

The editable masters and designspaces are in `sources/`. `make build` compiles
them with fontmake. It does not require Potrace or any cached files.

Since 1.315, `sources/` holds refit outlines. `make outline-sources` makes them
from the archived 1.314 sources in `candidates/1.314/sources.zip`: it refits
every outline with fewer points and redraws the vertical caron, then writes
`candidates/1.315/sources.zip`; `sources/` is that archive, extracted. Edit the
UFOs in `sources/` directly for small corrections.

`make sources` runs the original parametric drawing generator (Potrace 1.16)
and writes the pre-refit outlines into `sources/`, replacing the 1.315 ones.
Run it only when changing the generator, and refit its output before building a
release.

Review actual font proofs at small and large sizes. Preserve glyph coverage,
OpenType features, kerning, and compatible point/contour order across masters.
Include the relevant QA report summary and a visual before/after with a PR.

Use a GitHub no-reply email for commits if you want to keep your email private.
Never commit credentials, local environment files, private audit reports, or
machine-specific absolute paths. `python scripts/check_secrets.py` scans the
working tree and all fetched Git history with Gitleaks.

## Attribution

Sam Dunn directs the design and owns the project. The original concept art was
created with ChatGPT. AI tools also assisted with font engineering and QA,
including writing the scripts that refit the 1.315 outlines.
`AUTHORS.txt` lists copyright holders and `CONTRIBUTORS.txt` lists people.

## Releases

Bump the version when changing fonts or metadata. Regenerate all formats and
their checksums together. Keep immutable published asset URLs immutable; release
a new filename when deploying an updated font. Publishing to a font service is
a separate step from merging source changes.
