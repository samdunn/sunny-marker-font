# Public-release audit

Audit date: 2026-09-16. This records the reviewed source snapshot for the public
Sunny Marker 1.310 repository. It is not a Google Fonts submission or acceptance.

## Completed

- Compared the exported source snapshot with the latest private source revision:
  all 16,766 tracked files matched before the presentation and packaging updates.
- Gitleaks 8.30.1 scanned the source and nested release archives with redacted
  output; no secret-token matches were found.
- Reviewed source text, font name tables, archive members, image metadata and
  file names for private paths, email addresses, credentials and unsafe archive
  paths. Personal/work email addresses and local machine paths are excluded.
- The pinned build/QA environment passes dependency resolution and pip-audit
  with no known vulnerabilities. Bandit found no medium/high-severity issues.
- Functional verification passed for all 92 font artifacts, 375 variable
  locations, static/variable shaping parity, upright capital Y stems, web ZIP
  contents and font hashes. Font outlines are unchanged from version 1.310.
- The 30 static CFF OpenType styles now have a separate desktop download.
  The four-axis variable TTF is also OpenType, using TrueType outlines.
- Python tooling uses JSON instead of executable pickle loading, defusedxml
  for XML parsing, and bounded subprocesses. The Gitleaks download is pinned
  by checksum.
- CI uses immutable action revisions, read-only repository permissions and no
  persisted checkout credential. Font builds and checks need no cloud secrets.
  Ignore rules cover credentials, local settings, caches and audit reports.

## Public snapshot

This repository starts with fresh Git history. The earlier development history,
including its personal/work commit email addresses and private review metadata,
is preserved separately in a private archive. It is not part of this snapshot.
The intentional author credit and public GitHub contact remain in AUTHORS.txt
and CONTRIBUTORS.txt. New commits use a GitHub noreply identity.

Detailed audit reports stay outside the source tree. Release archives contain
project files only; no Git database, local configuration or private audit output
is distributed.

## Google Fonts publication steps

The maintainer confirmed ownership/right to release the original drawings and
all styles under OFL 1.1. The repository includes editable UFO sources, a standard
fontmake build, license and contributor files, a specimen and a full glyph atlas.
`make submission` generates a candidate Google Fonts package with metadata.

The public source links now resolve. Sam Dunn confirmed signing Google's CLA
on 2026-09-16 and confirmed there is no separate proprietary edition and that
he will maintain the project during onboarding. The signature was reported by
the copyright holder; it has not been independently verified here.

The 1.311 candidate adds metadata required by the current Fontspector checker.
Its seven remaining language-sample failures and warnings are disclosed in
[`GOOGLE_FONTS.md`](GOOGLE_FONTS.md). Google Fonts still needs to review the
design, resolve technical onboarding items and add a designer profile. An
approved designer photo has not yet been supplied. An initial proposal does
not mean acceptance into the collection.

Automated scans establish what was checked at this revision. They cannot prove
absence of every possible secret, vulnerability or legal issue in future changes.
