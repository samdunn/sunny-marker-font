# Contributing

Sunny Marker is a handwritten marker family licensed under the SIL Open Font
License 1.1. Contributions to the font, sources, documentation and build tools
are made under that license.

## Build and verify

Use Python 3.13 in a virtual environment. Install `requirements-qa.txt`, then
run `make build`, `make verify`, `make check`, and `make audit`.

The editable masters and designspaces are in `sources/`. `make build` compiles
them with fontmake. It does not require Potrace or any cached files.

For changes to the parametric drawing generator, install Potrace 1.16 and run
`make sources` before rebuilding. This regenerates the UFOs from the committed
reference art and Python design code and replaces direct UFO edits. Keep the
generator and committed UFOs in sync when changing generated shapes.

Review actual font proofs at small and large sizes. Preserve glyph coverage,
OpenType features, kerning, and compatible point/contour order across masters.
Include the relevant QA report summary and a visual before/after with a PR.

Use a GitHub no-reply email for commits if you want to keep your email private.
Never commit credentials, local environment files, private audit reports, or
machine-specific absolute paths. `python scripts/check_secrets.py` scans the
working tree and all fetched Git history with Gitleaks.

## Attribution

Sam Dunn directs the design and owns the project. The original concept art was
created with ChatGPT; AI tools also assisted with font engineering and QA.
`AUTHORS.txt` lists copyright holders and `CONTRIBUTORS.txt` lists people.

## Releases

Bump the version when changing fonts or metadata. Regenerate all formats and
their checksums together. Keep immutable published asset URLs immutable; release
a new filename when deploying an updated font. Publishing to a font service is
a separate step from merging source changes.
