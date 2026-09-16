#!/usr/bin/env sh
# Build all release formats from the committed UFO/designspace sources.
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
exec "${PYTHON:-python3}" scripts/build.py
