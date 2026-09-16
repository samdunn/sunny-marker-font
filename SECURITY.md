# Security

This repository distributes font files and local build tools. It does not need
production credentials, cloud account access, or access to a user's documents.

Build in a virtual environment using the pinned dependencies. The build runs
fontmake and, only when regenerating design sources, Potrace. The master cache
is JSON rather than executable Python serialization. The preview server binds
to the loopback address. The specimen has no analytics or external scripts.

Run `make audit` for dependency and Python-code checks, and
`python scripts/check_secrets.py` for a redacted secret scan. These checks reduce
risk but do not establish that arbitrary third-party font files or pull requests
are safe to execute. Review build-script changes before running them.

Report a suspected vulnerability privately through GitHub's security advisory
reporting when enabled. Otherwise contact the maintainer through the public
GitHub profile linked in `AUTHORS.txt` to arrange a private report. Do not post
credentials or personal data in a public issue.
